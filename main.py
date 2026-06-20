import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from models.chat import ChatRequest

app = FastAPI()

@app.get("/")
async def root():
    return {"success": "200"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def stream_chat(payload: ChatRequest):
    async def mock_generator():
        chunks = ["Hello", " world", "!"]
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.5)

    return StreamingResponse(mock_generator(), media_type="text/event-stream")