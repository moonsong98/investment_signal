# Codex Preflight Checklist

Before implementing a new milestone, Codex must confirm:

- Target milestone and acceptance criteria
- Whether the change can expose secrets or account data
- Whether the change could trigger live trading behavior
- Expected local test command
- Required environment variables
- Public versus private output boundary
- Whether external APIs should be mocked
- Whether LLM calls are allowed for the change

Before implementing any future live trading feature, Codex must also confirm:

- Broker or exchange provider
- Market and asset class
- Paper trading versus live trading
- Order types allowed
- Risk limits
- Timezone and trading session rules
- Audit log format
- Manual approval and emergency stop requirements
