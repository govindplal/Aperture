# Aperture

Aperture is the foundational backend for an agentic AI system. Currently in its initial build phase, this repository houses a high-performance, asynchronous FastAPI web server designed to handle real-time streaming LLM responses.

This backend is built to bypass heavy abstractions (like LangChain) in favor of native SDKs, strong data contracts, and raw speed.

## 🚀 Current Features (Build 01)

* **Asynchronous Streaming Engine:** Utilizes FastAPI's `StreamingResponse` to pipe LLM text deltas to the client character-by-character via Server-Sent Events (SSE).
* **Strong Data Contracts:** Pydantic `BaseModel` classes validate all incoming request payloads, ensuring the LLM API only receives perfectly shaped message arrays.
* **Fail-Fast Environment Config:** Managed via `pydantic-settings`. The server intercepts missing environment variables at boot time to prevent silent runtime crashes.
* **OpenAI-Compatible Architecture:** Built with the `openai` Python SDK, seamlessly supporting local models (like Qwen via Ollama) and production APIs (like Kimi/Moonshot) with zero code changes.
* **Structured Request Logging:** Implements custom `loguru` middleware to track request methods, paths, status codes, and execution times down to the millisecond.

## 📁 Repository Structure

```text
aperture/
├── core/
│   └── config.py        # Pydantic environment validation
├── models/
│   └── chat.py          # Request/Response schemas
├── routers/             # API route controllers (Upcoming)
├── .env                 # Secrets and routing config (git-ignored)
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

## 🧪 Testing the Stream

You can test the real-time streaming endpoint using `curl`. The `--no-buffer` flag ensures you see the characters arrive live:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d "{\"messages\": [{\"role\": \"user\", \"content\": \"Write a short poem about coding.\"}]}" \
     --no-buffer
```

## 🗺️ Roadmap
- [x] **Build 01:** FastAPI Foundation & Streaming Loop
- [ ] **Build 02:** Manual Tool Dispatch System
- [ ] **Build 03:** Two-Tool Agent Loop
- [ ] **Build 04:** DOM-to-Markdown Extraction (Playwright)
