
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
    },
}

calculate_string_length = {
        "type": "function",
        "function": {
            "name": "calculate_string_length",
            "description": "Calculates the total number of characters in a provided string text block.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text string to measure."}
                },
                "required": ["text"]
            }
        }
}

AGENT_TOOLS = [get_webpage_content_tool, calculate_string_length]