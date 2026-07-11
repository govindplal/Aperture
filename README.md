# Aperture

Aperture is the foundational backend for an agentic AI system. Currently in its initial build phase, this repository houses a high-performance, asynchronous FastAPI web server designed to handle real-time streaming LLM responses and robust tool-calling capabilities.

This backend is built to bypass heavy abstractions (like LangChain) in favor of native SDKs, strong data contracts, and raw speed.

## 🚀 Current Features (Build 01 & Build 02)

* **Asynchronous Streaming Engine:** Utilizes FastAPI's `StreamingResponse` to pipe LLM text deltas to the client character-by-character via Server-Sent Events (SSE).
* **Manual Tool Dispatch System:** Features a custom, asynchronous tool registry that parses LLM intentions, validates JSON arguments, and executes native Python functions (like fetching webpage content via `httpx`).
* **Defensive JSON Parsing:** Built-in "traps" to catch and parse rogue JSON outputs from open-source models that struggle with native tool-calling APIs, preventing crashes and ensuring execution.
* **Modular Architecture:** Utilizes FastAPI `APIRouter` to cleanly separate agent endpoints from the main application, utilizing a Singleton pattern for the OpenAI client to maximize performance.
* **Strong Data Contracts:** Pydantic `BaseModel` classes validate all incoming request payloads, ensuring the LLM API only receives perfectly shaped message arrays.
* **Fail-Fast Environment Config:** Managed via `pydantic-settings`. The server intercepts missing environment variables at boot time to prevent silent runtime crashes.
* **OpenAI-Compatible Architecture:** Built with the `openai` Python SDK, seamlessly supporting local models (like Qwen via Ollama) and production APIs (like Kimi/Moonshot) with zero code changes.
* **Structured Request Logging:** Implements custom `loguru` middleware to track request methods, paths, status codes, and execution times down to the millisecond.

## 📁 Repository Structure

The project has been modularized to support independent tools and routers.

```text
aperture/
├── core/
│   ├── config.py        # Pydantic environment validation
│   └── llm.py           # OpenAI client Singleton initialization
├── models/
│   └── chat.py          # Request/Response schemas
├── routers/             
│   └── agent.py         # Agent execution and tool-routing endpoints
├── tools/
│   ├── __init__.py      
│   ├── functions.py     # Executable Python functions (e.g., httpx web scraper)
│   ├── registry.py      # Async tool dispatcher
│   └── schemas.py       # JSON schemas representing the tool menu to the LLM
├── .env                 # Secrets and routing config (git-ignored)
├── .env.example         # Template for environment variables
├── .gitignore           # Ignored files and directories
├── .python-version      # Defined python version for uv
├── main.py              # Application entry point and streaming logic
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

3. **Install dependencies and start the server:**
   ```bash
   uv run uvicorn main:app --reload
   ```

## 🧪 Testing the Agent

You can test the newly constructed tool-calling router using `curl`.

**Test 1: Normal Chat (No Tools)**
This tests the LLM's standard response capabilities and system prompt adherence.
```bash
curl -X POST "http://localhost:8000/agent/run" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"What is the core difference between synchronous and asynchronous code execution?\"}"
```

**Test 2: Tool Execution (Web Fetching)**
This tests the agent's ability to intercept a URL, correctly format a tool call, and trigger the backend web scraping function.
```bash
curl -X POST "http://localhost:8000/agent/run" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"Can you read the content at [https://example.com](https://example.com) ?\"}"
```

## 🗺️ Roadmap
- [x] **Build 01:** FastAPI Foundation & Streaming Loop
- [x] **Build 02:** Manual Tool Dispatch System
- [ ] **Build 03:** Two-Tool Agent Loop
- [ ] **Build 04:** DOM-to-Markdown Extraction (Playwright)
