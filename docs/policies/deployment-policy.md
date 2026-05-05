# Deployment Policy

## GitHub Pages

Use GitHub Pages for static public content only:
- Investment journal
- Strategy notes
- Research note drafts
- Redacted event logs

## Webhook Backend

Use Cloudflare Workers or a similar serverless backend for TradingView webhooks.
GitHub Pages must not be used as a webhook receiver.

## Secrets

Use GitHub Secrets or Cloudflare Secrets for deployment secrets.
Do not place secrets in static site output.
