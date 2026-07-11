import asyncio
import time

from fastapi import FastAPI, Request
from routers import agent
from fastapi.responses import StreamingResponse

from models.chat import ChatRequest
from core.config import settings
from core.llm import client

from loguru import logger


app = FastAPI()

app.include_router(agent.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter()
    process_time_ms = (end_time - start_time) * 1000

    logger.info(
        f"{request.method} {request.url.path} -"
        f"Status: {response.status_code} -"
        f"Completed in {process_time_ms:.2f}ms"
    )

    return response

@app.get("/")
async def root():
    return {"success": "200"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def stream_chat(payload: ChatRequest):


    async def openai_generator():

        stream = await client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=[{"role": m.role, "content": m.content} for m in payload.messages],
            stream=True,
        )
        async for chunk in stream:  
            if chunk.choices and chunk.choices[0].delta.content is not None:
                text_chunk = chunk.choices[0].delta.content
                yield text_chunk

    return StreamingResponse(openai_generator(), media_type="text/event-stream")