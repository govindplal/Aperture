FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv pip install --system -r pyproject.toml

RUN uv run playwright install --with-deps chromium

COPY . .

EXPOSE 8000