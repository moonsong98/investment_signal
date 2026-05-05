# Cost Control Policy

Free or low-cost tools are preferred:
- GitHub repository for code and versioned docs
- GitHub Pages for static research pages
- Cloudflare Workers or similar serverless backend for webhooks
- Telegram Bot for alerts
- Public APIs where feasible

LLM usage must be limited:
- Do not send every event to LLMs.
- Run rule-based severity classification first.
- Send only Level 3 events to LLMs.
- Track request counts and prompt sizes.
