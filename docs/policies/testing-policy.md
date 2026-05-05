# Testing Policy

All milestones must be locally testable.

Default command:

```bash
uv run python -m unittest discover -s tests
```

Static site build command:

```bash
uv run python scripts/build_site.py
```

Test priorities:
- Alert schema parsing
- Severity classification
- Secret validation
- Redaction
- Markdown note generation
- Static site generation from sample data
- Paper trading risk limits when v4 starts

External APIs, Telegram, and LLMs should use mocks in local tests by default.
