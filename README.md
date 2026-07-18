# Aperture

Aperture is the foundational backend for an agentic AI system. Currently at **Checkpoint 06 of 15** in its build phase, this repository houses a high-performance, asynchronous FastAPI web server designed to handle real-time streaming LLM responses and robust tool-calling capabilities.

This backend is built to bypass heavy abstractions (like LangChain) in favor of native SDKs, strong data contracts, and raw speed.

## 🚀 Features

* **Asynchronous Streaming Engine:** Utilizes FastAPI's `StreamingResponse` to pipe LLM text deltas to the client character-by-character via Server-Sent Events (SSE).
* **Agentic Re-feeding Loop:** Implements a closed-loop execution pattern. The backend captures tool execution output, appends the event history, and transparently re-routes data back to the LLM to synthesize natural-language conclusions.
* **Persistent Agent Memory:** Utilizes `SQLAlchemy` (with the `asyncpg` driver) to automatically log every `Session`, `Message`, and `ToolCall` into PostgreSQL, providing a complete, queryable audit trail of the agent's actions.
* **Automated Schema Migrations:** Fully integrated `Alembic` environment configured for asynchronous execution to manage database evolution without breaking the containerized stack.
* **Generator Stream Architecture:** Combines HTTP chunk yielding with background database transactions, ensuring the user gets real-time streaming responses while silently logging the final accumulated text to the database.
* **Multi-Tool Dispatch Registry:** Features a custom, asynchronous tool registry that parses LLM intentions, dynamically matches requests to active functions, validates JSON arguments, and runs tool code seamlessly.
* **Headless DOM-to-Markdown Extraction:** Integrates automated browser instances to load JavaScript-rendered components, bypass basic bot blocks via custom headers, and process heavy raw DOM footprints into clean, context-efficient Markdown text.
* **Defensive JSON Parsing:** Built-in "traps" to catch and parse rogue JSON outputs from open-source models that struggle with native tool-calling APIs, preventing application crashes.
* **Containerized Infrastructure:** A unified `docker-compose` stack running a hot-reloading Linux API container, PostgreSQL 16, and Redis 7 on an isolated internal network.
* **Modular Architecture:** Utilizes FastAPI `APIRouter` to cleanly isolate agent endpoints from core configuration.
* **Strong Data Contracts:** Pydantic `BaseModel` classes validate all incoming request payloads, ensuring the LLM API only receives perfectly shaped message arrays.
* **Fail-Fast Environment Config:** Managed via `pydantic-settings`. The server intercepts missing environment variables at boot time to prevent silent runtime crashes.
* **OpenAI-Compatible Architecture:** Built with the `openai` Python SDK, seamlessly supporting local models (like Qwen via Ollama) and production APIs with zero code changes.

## 📁 Repository Structure

The project is modularized to support independent tools, data schemas, and routers.

```text
aperture/
├── core/
│   ├── config.py        # Pydantic environment validation
│   ├── database.py      # Async Postgres engine and dependency injection
│   └── llm.py           # OpenAI client Singleton initialization
├── migrations/          # Alembic asynchronous migration scripts and environment
├── models/
│   ├── chat.py          # Pydantic Request/Response schemas
│   └── db.py            # SQLAlchemy DeclarativeBase ORM models
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
├── alembic.ini          # Alembic configuration for migrations
├── docker-compose.yml   # Infrastructure orchestration (API, Postgres, Redis)
├── Dockerfile           # Python 3.12 Linux environment with embedded Playwright binaries
├── main.py              # Application entry point, Windows event loop fixes, and streaming logic
├── pyproject.toml       # Project metadata
└── uv.lock              # Dependency lockfile
```

## 🛠️ Setup & Execution

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/Aperture.git](https://github.com/yourusername/Aperture.git)
cd Aperture
```

### 2. Set up the environment
Create a `.env` file in the root directory by copying the example:
```bash
cp .env.example .env
```
Ensure your database credentials and LLM endpoints are configured:
```env
# Example configuration for a local Ollama tunnel
OPENAI_API_BASE_URL=[https://your-ngrok-url.ngrok-free.app/v1](https://your-ngrok-url.ngrok-free.app/v1)
OPENAI_API_KEY=not_needed_for_local
LLM_MODEL_NAME=qwen2.5-coder:7b

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=aperture
```

### 3. Boot the Infrastructure (Recommended)
Aperture is designed to run inside Docker to ensure environment parity. This spins up the API, PostgreSQL, and Redis together.
```bash
docker compose up --build
```
*Note: The local directory is mounted as a volume. Editing code in your IDE will instantly hot-reload the containerized API.*

### Alternative: Local Host Execution
If you prefer running without Docker, use `uv` for dependency management:
```bash
uv add playwright html2text sqlalchemy alembic asyncpg
uv run playwright install chromium
uv run uvicorn main:app --reload
```

## 🧪 Testing the Agent

You can test the multi-tool re-feeding capabilities using `curl`. Because the database is now integrated, every execution generates a persistent audit trail.

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
- [x] **01** FastAPI Application Foundation
- [x] **02** Manual Tool Dispatch System
- [x] **03** Two-Tool Agent Loop
- [x] **04** `dom_to_markdown` via Playwright
- [x] **05** Docker Compose Stack (Postgres + Redis)
- [x] **06** Postgres Models + Alembic Migrations
- [ ] **07** Full ReAct Agent Loop
- [ ] **08** pgvector Semantic Memory
- [ ] **09** Workflow Graph + Deterministic Replay
- [ ] **10** Redis Task Queue + SSE
- [ ] **11** Next.js Agent UI
- [ ] **12** Memory Explorer + Replay UI
- [ ] **13** Agent Control Interface
- [ ] **14** Tests + CI with GitHub Actions
- [ ] **15** Cloudflare Worker Deployment
