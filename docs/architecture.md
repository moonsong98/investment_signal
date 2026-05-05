# Architecture

```text
TradingView Alert
-> Webhook Receiver
-> Event Validator
-> Rule Engine
-> Telegram Notifier
-> Event Logger
-> LLM Analysis Agent
-> Markdown Note Generator
-> GitHub Pages Dashboard
```

## Runtime Choices

- Local development: Python 3.14 and uv
- Static site: GitHub Pages
- Webhook receiver: Cloudflare Workers or similar low-cost serverless backend
- Notification: Telegram Bot
- LLM analysis: important Level 3 events only

## Boundaries

- GitHub Pages is static and cannot receive TradingView webhooks directly.
- Webhook processing belongs in a serverless backend.
- Public pages must not expose account data, real position sizes, tokens, or secrets.
- Broker API integration is explicitly out of scope until a later approved milestone.
