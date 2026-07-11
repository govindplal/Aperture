
import httpx
from loguru import logger


async def get_webpage_content(url: str) -> str:
    logger.info(f"Tool executed: Fetching content from {url}")

    try:

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise an error for bad responses ()

            return response.text

    except Exception as e:
        logger.error(f"Failed to fetch {url}: {str(e)}")
        return f"Error fetching webpage: {str(e)}"