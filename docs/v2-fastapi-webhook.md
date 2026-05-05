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
curl -X POST http://127.0.0.1:8000/webhooks/tradingview \
  -H "Content-Type: application/json" \
  --data @data/samples/tradingview_alert_level2.json
```

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

## Expected Behavior

- Level 1: accepted, no Telegram notification
- Level 2: accepted, Telegram notification when configured
- Level 3: accepted, Telegram notification when configured; later LLM analysis target
- Invalid secret: rejected
- Malformed payload: rejected
