# Security Policy

- Store secrets in environment variables, GitHub Secrets, or Cloudflare Secrets.
- Never commit Telegram tokens, webhook secrets, API keys, account IDs, or broker credentials.
- Never publish account balances, real position sizes, or personal financial data to GitHub Pages.
- Validate webhook shared secrets before processing payloads.
- Redact sensitive fields before logging or publishing.
- Keep `.env.example` updated with names only, not real values.
- Keep `.dockerignore` aligned with `.gitignore` so local secrets and account
  exports are not sent in Docker build contexts.
- Run `uv run python scripts/check_public_output.py` before publishing or
  committing generated public site output.
