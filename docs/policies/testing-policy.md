# Testing Policy

All milestones must be locally testable.

Default command:

```bash
uv run python -m unittest discover -s tests
```

Test priorities:
- Alert schema parsing
- Severity classification
- Secret validation
- Redaction
- Markdown note generation
- Paper trading risk limits when v4 starts

External APIs, Telegram, and LLMs should use mocks in local tests by default.
