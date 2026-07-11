import json

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from tools.registry import dispatch_tool
from tools.schemas import AGENT_TOOLS

from core.config import settings
from core.llm import client

router = APIRouter(prefix="/agent", tags=["Agent Operations"])

class AgentRequest(BaseModel):
    prompt: str

@router.post("/run")
async def run_agent(request: AgentRequest):
    logger.info(f"Received task: {request.prompt}")

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

            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": str(tool_output)
            })


            final_response = await client.chat.completions.create(
                model=settings.LLM_MODEL_NAME,
                messages=messages
            )

            return {
                "status": "agent_loop_completed",
                "content": final_response.choices[0].message.content
            }
        
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
                
                messages.append({"role": "assistant", "content": text_content})
                messages.append({"role": "user", "content": f"The tool '{tool_name}' executed successfully and returned this data: {result}. Please provide the final response to the user."})
                
                # Second LLM Call
                final_response = await client.chat.completions.create(
                    model=settings.LLM_MODEL_NAME,
                    messages=messages
                )
                
                return {
                    "status": "agent_loop_completed_from_text", 
                    "content": final_response.choices[0].message.content
                }
        except json.JSONDecodeError:
            # It's not JSON, just normal text. Let it pass through.
            pass

        logger.info("LLM completed request with standard text.")
        return {
            "status": "text_response",
            "content": text_content
        }