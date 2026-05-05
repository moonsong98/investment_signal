# Roadmap

## v0: Principles And Project Foundation

- Document investment principles, risk principles, agent role, watchlist policy, alert severity policy, security policy, cost policy, and testing policy.
- Create folder structure for docs, content, sample data, Python modules, and tests.
- Define initial data models and sample payloads.

Acceptance criteria:
- A new contributor can understand the mission and safety constraints from docs.
- v0-v3 live trading prohibition is explicit.
- Local tests pass with `uv run python -m unittest discover -s tests`.

## v1: GitHub Pages Research Lab

- Build a static site for journals, strategy notes, research notes, macro notes, and sample alert logs.
- Use sample data only.
- Do not connect external APIs.

Acceptance criteria:
- Static content can be previewed locally and published to GitHub Pages.
- Sample alert logs and research notes are visible without secrets.
- The site builds with `uv run python scripts/build_site.py`.

## v2: TradingView Alert To Telegram

- Receive TradingView webhook payloads.
- Validate shared secret and JSON schema.
- Classify severity.
- Send Level 2 and Level 3 Telegram notifications.

Acceptance criteria:
- Valid sample payloads produce expected notification decisions.
- Invalid secrets and malformed payloads fail safely.
- No LLM, broker API, or live trading exists.

## v3: Event Logger And LLM Analysis

- Store structured events.
- Run LLM analysis for Level 3 events only.
- Generate Markdown research note drafts.
- Publish safe data for GitHub Pages.

Acceptance criteria:
- Level 3 sample event creates a research note draft.
- Level 1 and Level 2 events do not call LLM.
- Sensitive fields are redacted before publication.
- Initial implementation may use deterministic note templates before real LLM API calls.

## v4: Paper Trading Experiment

- Add virtual account, paper positions, paper trades, risk limits, and performance reports.
- Use paper capital only.
- Do not place live broker orders.

Acceptance criteria:
- Paper trades are reproducible from sample events.
- Risk limits block invalid entries.
- No live order path exists.

## v5: Limited Small Live Trading

- Do not implement now.
- Prepare a separate approval plan after v0-v4 are stable.

Acceptance criteria:
- Requires explicit human approval, kill switch, broker selection, and risk policy review.
