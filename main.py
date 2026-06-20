import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

from models.chat import ChatRequest
from core.config import settings

app = FastAPI()

@app.get("/")
async def root():
    return {"success": "200"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def stream_chat(payload: ChatRequest):

    client = AsyncOpenAI(
        base_url= settings.OPENAI_API_BASE_URL,
        api_key= settings.OPENAI_API_KEY,
        default_headers={"ngrok-skip-browser-warning": "true"}
    )

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