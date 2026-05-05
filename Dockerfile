FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --extra api --no-dev

EXPOSE 8000

CMD ["uv", "run", "--frozen", "--extra", "api", "uvicorn", "investment.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
