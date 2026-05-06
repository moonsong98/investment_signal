# v2 FastAPI Webhook

This milestone receives TradingView alerts, validates the shared secret and
payload shape, classifies severity, and sends Telegram notifications for Level 2
and Level 3 events.

Live trading and broker API integration remain out of scope.

## Local Setup

Create `.env` from `.env.example` and set local values:

```bash
TRADINGVIEW_WEBHOOK_SECRET=replace-with-local-secret
TELEGRAM_DRY_RUN=true
```

The placeholder webhook secret is allowed only for `APP_ENV=local`, `test`,
`dev`, or `development`. Any non-local deployment must use a real secret value.

Run the API:

```bash
uv run --extra api uvicorn investment.api.app:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Send a sample TradingView alert:

```bash
uv run python scripts/send_sample_alert.py
```

The script reads `.env`, injects `TRADINGVIEW_WEBHOOK_SECRET` into the sample
payload, and does not print the secret.

## Docker

```bash
docker compose up --build
```

## Telegram

By default, `TELEGRAM_DRY_RUN=true` prevents real Telegram delivery. To send
real messages, set:

```bash
TELEGRAM_DRY_RUN=false
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Do not commit real values.

Avoid running `docker compose config` after real secrets are placed in `.env`.
It expands environment values and can print tokens or webhook secrets to the
terminal.

## Expected Behavior

- Level 1: accepted, no Telegram notification
- Level 2: accepted, Telegram notification when configured
- Level 3: accepted, Telegram notification when configured; later LLM analysis target
- Invalid secret: rejected
- Malformed payload: rejected
- Unsupported symbol, timeframe, alert type, or overlong message: rejected before logging

## TradingView Templates

See [`tradingview-alert-templates.md`](tradingview-alert-templates.md).

For the end-to-end TradingView alert setup checklist, see
[`tradingview-setup.md`](tradingview-setup.md).
