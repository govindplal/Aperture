
get_webpage_content_tool = {
    "type": "function",
    "function": {
        "name": "get_webpage_content",
        "description": "Fetches the raw text content from a given webpage URL. Use this to read articles, documentation, or scrape text from a specific site.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full, valid URL of the webpage to fetch (e.g., https://news.ycombinator.com)."
                }
            },
            "required": ["url"]
        }
    }
}

AGENT_TOOLS = [get_webpage_content_tool]