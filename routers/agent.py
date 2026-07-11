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

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL_NAME,
        messages=[
            # THE FIX: Tell the model exactly how to behave
            {"role": "system", "content": "You are a helpful assistant. ONLY use the get_webpage_content tool if the user explicitly provides a URL in their prompt. Otherwise, answer from your own knowledge."},
            {"role": "user", "content": request.prompt}
        ],
        tools=AGENT_TOOLS,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # FLOW BRANCH A: The API correctly parsed the tool call
    if response_message.tool_calls:
        logger.info("Tool call detected via standard API structure.")
        execution_results = []
        
        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            
            try:
                parsed_arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                parsed_arguments = {}
            
            tool_output = await dispatch_tool(tool_name, parsed_arguments)
            
            execution_results.append({
                "tool_called": tool_name,
                "arguments": parsed_arguments,
                "result": tool_output
            })
            
        return {"status": "tools_executed", "data": execution_results}
        
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
                
                return {
                    "status": "tools_executed_from_text", 
                    "tool_called": tool_name,
                    "data": result
                }
        except json.JSONDecodeError:
            # It's not JSON, just normal text. Let it pass through.
            pass

        logger.info("LLM completed request with standard text.")
        return {
            "status": "text_response",
            "content": text_content
        }