# Aperture

Aperture is the foundational backend for an agentic AI system. Currently in its initial build phase, this repository houses a high-performance, asynchronous FastAPI web server designed to handle real-time streaming LLM responses and robust tool-calling capabilities.

This backend is built to bypass heavy abstractions (like LangChain) in favor of native SDKs, strong data contracts, and raw speed.

## 🚀 Features

* **Asynchronous Streaming Engine:** Utilizes FastAPI's `StreamingResponse` to pipe LLM text deltas to the client character-by-character via Server-Sent Events (SSE).
* **Agentic Re-feeding Loop:** Implements a closed-loop execution pattern. The backend captures tool execution output, appends the event history, and transparently re-routes data back to the LLM to synthesize natural-language conclusions.
* **Multi-Tool Dispatch Registry:** Features a custom, asynchronous tool registry that parses LLM intentions, dynamically matches requests to active functions, validates JSON arguments, and runs tool code seamlessly.
* **Headless DOM-to-Markdown Extraction:** Integrates automated browser instances to load JavaScript-rendered components, bypass basic bot blocks via custom headers, and process heavy raw DOM footprints into clean, context-efficient Markdown text.
* **Defensive JSON Parsing:** Built-in "traps" to catch and parse rogue JSON outputs from open-source models that struggle with native tool-calling APIs, preventing application crashes.
* **Modular Architecture:** Utilizes FastAPI `APIRouter` to cleanly isolate agent endpoints from core configuration, utilizing a Singleton pattern for the OpenAI client lifecycle.
* **Strong Data Contracts:** Pydantic `BaseModel` classes validate all incoming request payloads, ensuring the LLM API only receives perfectly shaped message arrays.
* **Fail-Fast Environment Config:** Managed via `pydantic-settings`. The server intercepts missing environment variables at boot time to prevent silent runtime crashes.
* **OpenAI-Compatible Architecture:** Built with the `openai` Python SDK, seamlessly supporting local models (like Qwen via Ollama) and production APIs with zero code changes.
* **Structured Request Logging:** Implements custom `loguru` middleware to track request methods, paths, status codes, and execution times down to the millisecond.

## 📁 Repository Structure

The project is modularized to support independent tools, data schemas, and routers.

```text
aperture/
├── core/
│   ├── config.py        # Pydantic environment validation
│   └── llm.py           # OpenAI client Singleton initialization
├── models/
│   └── chat.py          # Request/Response schemas
├── routers/             
│   └── agent.py         # Agent execution, loop control, and tool-routing endpoints
├── tools/
│   ├── __init__.py      
│   ├── functions.py     # Executable Python functions (Playwright extraction, string math)
│   ├── registry.py      # Async tool dispatcher map
│   └── schemas.py       # JSON schemas representing the tool menu to the LLM
├── .env                 # Secrets and routing config (git-ignored)
├── .env.example         # Template for environment variables
├── .gitignore           # Ignored files and directories
├── .python-version      # Defined python version for uv
├── main.py              # Application entry point, Windows event loop fixes, and streaming logic
├── pyproject.toml       # Project metadata
└── uv.lock              # Dependency lockfile
```

## 🛠️ Local Setup

This project uses `uv` for lightning-fast dependency management.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/Aperture.git](https://github.com/yourusername/Aperture.git)
   cd Aperture
   ```

2. **Set up the environment:**
   Create a `.env` file in the root directory:
   ```env
   # Example configuration for a local Ollama tunnel
   OPENAI_API_BASE_URL=[https://your-ngrok-url.ngrok-free.app/v1](https://your-ngrok-url.ngrok-free.app/v1)
   OPENAI_API_KEY=not_needed_for_local
   LLM_MODEL_NAME=qwen2.5-coder:7b
   ```

3. **Install dependencies and binary runtimes:**
   ```bash
   uv add playwright html2text
   uv run playwright install chromium
   ```

4. **Start the server:**
   ```bash
   uv run uvicorn main:app --reload
   ```

## 🧪 Testing the Agent

You can test the multi-tool re-feeding capabilities using `curl`.

**Test 1: Core Knowledge Conversing (No Tools)**
```bash
curl -X POST "http://localhost:8000/agent/run" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"What is the core difference between synchronous and asynchronous code execution?\"}"
```

**Test 2: Internal Python Function Execution (String Length Tool)**
```bash
curl -X POST "http://localhost:8000/agent/run" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"Can you calculate the length of this string for me: 'The quick brown fox jumps over the lazy dog'?\"}"
```

**Test 3: Headless Browser Scrape & Re-feed (DOM to Markdown Tool)**
```bash
curl -X POST "http://localhost:8000/agent/run" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"Can you summarize the first few paragraphs of [https://en.wikipedia.org/wiki/FastAPI](https://en.wikipedia.org/wiki/FastAPI) ?\"}"
```

## 🗺️ Roadmap
- [x] **Build 01:** FastAPI Foundation & Streaming Loop
- [x] **Build 02:** Manual Tool Dispatch System
- [x] **Build 03:** Two-Tool Agent Loop
- [x] **Build 04:** DOM-to-Markdown Extraction (Playwright)
```
