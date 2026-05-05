# investment

Personal investment research and alert agent.

This project is not a live automated trading bot. Its first job is to help a
human investor study markets, monitor important signals, log events, and draft
research notes without exposing secrets or personal account data.

## Codex Setup

Codex should use [`AGENTS.md`](AGENTS.md) as the main repository instruction file.
It defines project context, coding rules, trading safety defaults, and the expected direction for future modules.

## Initial Scope

- Investment principles and risk policy documentation
- Watchlist and alert severity policies
- TradingView alert schema and sample payloads
- Telegram notification policy
- LLM usage policy for important events only
- GitHub Pages-ready research and journal content structure

## Local Configuration

Create a local `.env` file from `.env.example` when environment variables are needed.
Do not commit real credentials, broker account IDs, API tokens, webhook secrets, or personal financial data.

## Run

```bash
uv run python main.py
```

## Build Site

```bash
uv run python scripts/build_site.py
```

## Run Webhook API

```bash
uv run --extra api uvicorn investment.api.app:app --reload --host 127.0.0.1 --port 8000
```

Send a safe local sample alert:

```bash
uv run python scripts/send_sample_alert.py
```

Generate Level 3 research note drafts:

```bash
uv run python scripts/generate_research_notes.py
```

## Test

```bash
uv run python -m unittest discover -s tests
```

## Roadmap

See [`docs/roadmap.md`](docs/roadmap.md).
