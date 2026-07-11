# core/llm.py
from openai import AsyncOpenAI
from core.config import settings

client = AsyncOpenAI(
    base_url=settings.OPENAI_API_BASE_URL,
    api_key=settings.OPENAI_API_KEY,
    default_headers={"ngrok-skip-browser-warning": "true"}
)