# AGENTS.md

This file defines how Codex should work in this repository.

## Project Context

This repository is for personal investment research, alerting, and future paper
trading experiments. It is not a live automated trading bot.

Primary domains:
- Macro indicators, market regimes, and cross-asset analysis
- Public company analysis, financial statements, filings, and valuation
- TradingView-based signal research and alert workflows
- Python services and scripts for research, data collection, backtesting, and automation
- FastAPI or serverless services for APIs, dashboards, and webhooks

## Default Language

- Communicate with the user in Korean unless they ask otherwise.
- Keep code, identifiers, comments, commit messages, and documentation in English unless Korean is clearly more appropriate.

## Engineering Principles

- Prefer small, testable modules over large scripts.
- Keep trading logic, data access, broker/exchange integration, and API presentation separated.
- Treat financial data as unreliable until validated for source, timestamp, currency, timezone, and adjustment policy.
- Do not hard-code credentials, tokens, account IDs, webhook secrets, or API keys.
- Do not place live trading behavior behind ambiguous defaults.
- Prefer explicit configuration over hidden environment assumptions.

## Financial And Trading Safety

- Never present analysis as financial advice.
- Do not implement live trading in v0 through v3.
- Do not implement broker API integration unless the user explicitly starts a later milestone for it.
- For any future automated trading, default to dry-run or paper trading unless the user explicitly asks for live trading behavior.
- Any future live order placement, broker/exchange write action, or position-changing operation must require explicit user confirmation.
- Log or return enough context to audit a trading decision: input data timestamp, signal, position state, risk limits, and intended action.
- Include risk controls when implementing automation: max position size, max daily loss or stop condition, duplicate-order protection, and market-hours handling when relevant.
- Be careful with timezones. Prefer timezone-aware datetimes and document whether timestamps are UTC, exchange-local time, or Asia/Seoul.

## Python Standards

- Target the Python version declared in `pyproject.toml`.
- Use `uv` for running Python commands, dependency management, and virtual environment workflows.
- Use type hints for new public functions and for trading/data models.
- Prefer `pathlib.Path`, `datetime` timezone-aware objects, and structured logging.
- Prefer dataclasses or Pydantic models for structured domain data.
- Keep external API clients thin and isolate provider-specific details.
- Add tests for parsing, calculations, trading rules, and API endpoints when behavior is non-trivial.

## FastAPI Standards

- Keep route handlers thin.
- Put business logic in service modules.
- Use Pydantic models for request and response schemas.
- Validate webhook payloads and secrets before processing.
- Return explicit error responses instead of broad exception swallowing.

## TradingView Standards

- Treat TradingView alerts as untrusted external input.
- Validate alert schema, symbol, timeframe, strategy name, timestamp, and secret before acting.
- Make duplicate alert handling idempotent when it can trigger orders or state changes.
- Keep Pine Script assumptions documented near the consuming Python code.

## Data And Research Standards

- Record source, retrieval time, and key assumptions for datasets used in analysis.
- Avoid mixing adjusted and unadjusted prices without clear naming.
- Avoid mixing fiscal and calendar periods without explicit conversion.
- Prefer reproducible notebooks/scripts over one-off manual calculations.
- Cache external data where practical, but make cache invalidation explicit.

## Secrets And Local Files

- Store secrets only in local environment variables or ignored `.env` files.
- Keep `.env.example` updated with required variable names and safe placeholder values.
- Do not commit raw broker exports, account statements, proprietary datasets, or personal financial information.

## Common Commands

Use these commands when available:

```bash
uv run python main.py
uv run python scripts/build_site.py
uv run python scripts/send_sample_alert.py
uv run python scripts/generate_research_notes.py
uv run --extra api uvicorn investment.api.app:app --reload --host 127.0.0.1 --port 8000
uv run python -m unittest discover -s tests
```

When dependencies, tests, linting, or formatting tools are added, update this section.

## Change Workflow

- Inspect the existing code before editing.
- Keep edits scoped to the user request.
- Do not rewrite unrelated files.
- Preserve user changes in a dirty worktree.
- Before changing behavior, identify the expected input/output and likely failure modes.
- After edits, run the most relevant available verification command.

## Suggested Project Layout

Use this as the default direction when the project grows:

```text
src/investment/
  alerts/         # Alert schemas and normalization
  config/         # Settings and environment loading
  llm/            # LLM prompts and analysis adapters
  logging/        # Event log writers and redaction
  notifications/  # Telegram and other notifiers
  pages/          # GitHub Pages data/note generation
  paper/          # Paper trading only; no live broker orders
  research/       # Macro/company analysis workflows
  rules/          # Severity classification and filtering
  tradingview/    # TradingView webhook parsing and validation
docs/
content/
data/
tests/
```

## Before Implementing Live Trading

Codex must confirm these details with the user:
- Broker or exchange provider
- Market and asset class
- Paper trading versus live trading
- Order types allowed
- Risk limits
- Timezone and trading session rules
- Required audit log format
