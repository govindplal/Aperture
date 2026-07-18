import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel

from tools.registry import dispatch_tool
from tools.schemas import AGENT_TOOLS

from core.config import settings
from core.llm import client

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.db import Session, Message, ToolCall

router = APIRouter(prefix="/agent", tags=["Agent Operations"])

class AgentRequest(BaseModel):
    prompt: str

@router.post("/run")
async def run_agent(request: AgentRequest, db:AsyncSession = Depends(get_db)):

    db_session = Session(task=request.prompt)
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session) # This pulls the auto-generated ID back from Postgres

    # 2. Log the initial user message
    db_msg = Message(
        session_id=db_session.id,
        role="user",
        content=request.prompt
    )
    db.add(db_msg)
    await db.commit()

    logger.info(f"Received task: {request.prompt}")

    async def agent_stream_generator():

        messages = [
            {"role": "system", "content": "You are a helpful assistant. ONLY use tools if explicitly required by the user's prompt. Otherwise, answer from your own knowledge."},
            {"role": "user", "content": request.prompt}
        ]

        response = await client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=messages,
            tools=AGENT_TOOLS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # FLOW BRANCH A: Standard API tool call
        if response_message.tool_calls:
            logger.info("Tool call detected. Executing and re-feeding...")

            messages.append(response_message)
            execution_results = []
            
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                
                try:
                    parsed_arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    parsed_arguments = {}
                
                tool_output = await dispatch_tool(tool_name, parsed_arguments)

                db_tool_call = ToolCall(
                    session_id=db_session.id,
                    tool_name=tool_name,
                    tool_input=parsed_arguments,
                    tool_result={"output": tool_output},
                )
                db.add(db_tool_call)
                await db.commit()

                db_tool_msg = Message(
                    session_id=db_session.id,
                    role="system", # Or 'tool', depending on how you format it for the LLM
                    content=f"Tool {tool_name} returned: {tool_output}"
                )
                db.add(db_tool_msg)
                await db.commit()

                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": str(tool_output)
                })


                final_response = await client.chat.completions.create(
                    model=settings.LLM_MODEL_NAME,
                    messages=messages,
                    stream=True
                )

                final_accumulated_text = ""
                async for chunk in final_response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        final_accumulated_text += content
                        yield content

                db_assistant_msg = Message(
                    session_id=db_session.id,
                    role="assistant",
                    content=final_accumulated_text
                )
                db.add(db_assistant_msg)
            
                db_session.status = "complete"
                await db.commit()
                return
            
        # FLOW BRANCH B: Handling text or rogue JSON
        else:
            text_content = response_message.content if response_message.content else ""
            
            # THE TRAP: Check if the text is actually a JSON tool call
            try:
                possible_tool_call = json.loads(text_content)
                
                # Check if it matches the exact structure the model hallucinated
                if isinstance(possible_tool_call, dict) and "name" in possible_tool_call and "arguments" in possible_tool_call:
                    tool_name = possible_tool_call["name"]
                    tool_args = possible_tool_call["arguments"]
                    
                    logger.info(f"Caught rogue JSON tool call: {tool_name}")
                    result = await dispatch_tool(tool_name, tool_args)

                    db_tool_call = ToolCall(session_id=db_session.id, tool_name=tool_name, tool_input=tool_args, tool_result={"output": result})
                    db.add(db_tool_call)
                    
                    db_tool_msg = Message(session_id=db_session.id, role="system", content=f"Tool {tool_name} returned: {result}")
                    db.add(db_tool_msg)
                    await db.commit()

                    messages.append({"role": "assistant", "content": text_content})
                    messages.append({"role": "user", "content": f"The tool '{tool_name}' executed successfully and returned this data: {result}. Please provide the final response to the user."})
                    
                    # Second LLM Call
                    final_response = await client.chat.completions.create(
                        model=settings.LLM_MODEL_NAME,
                        messages=messages,
                        stream=True
                    )

                    final_accumulated_text = ""
                    async for chunk in final_response:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            final_accumulated_text += content
                            yield content
                            
                    # Save DB
                    db_assistant_msg = Message(session_id=db_session.id, role="assistant", content=final_accumulated_text)
                    db.add(db_assistant_msg)
                    db_session.status = "complete"
                    await db.commit()
                    return
                
            except json.JSONDecodeError:
                pass

            logger.info("LLM completed request with standard text.")

        yield text_content
            
        # Save DB
        db_assistant_msg = Message(session_id=db_session.id, role="assistant", content=text_content)
        db.add(db_assistant_msg)
        db_session.status = "complete"
        await db.commit()

        return

    return StreamingResponse(agent_stream_generator(), media_type="text/plain")
