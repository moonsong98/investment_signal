# Operations Runbook

This runbook is for local operation of the TradingView webhook and research
assistant.

## Daily Status

Run:

```bash
uv run python scripts/ops_status.py
```

The command is secret-safe. It reports:
- local health endpoint status
- running Docker Compose services
- total event count
- latest event symbol and severity
- generated draft count
- LLM usage ledger record count

Print recent local event summaries:

```bash
uv run python scripts/tail_events.py --limit 5
```

The command reads ignored local JSONL logs and prints only selected redacted
fields. It does not print webhook secrets, dedupe keys, or raw payloads.

## Local Server

Start or rebuild:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

## Public Tunnel

Run cloudflared after the local server is healthy:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

## Safe Alert Test

```bash
uv run python scripts/send_sample_alert.py \
  --url https://your-tunnel.trycloudflare.com/webhooks/tradingview
```

## Publish Dashboard

Before publishing generated site output:

```bash
uv run python scripts/build_site.py
uv run python scripts/check_public_output.py
```

Only commit public output after confirming it does not include smoke-test events,
private notes, account data, or secrets.

## Local Cleanup

List ignored runtime outputs without deleting them:

```bash
uv run python scripts/local_cleanup.py
```

Remove the listed local outputs only when you intentionally want a clean local
workspace:

```bash
uv run python scripts/local_cleanup.py --apply
```

This removes ignored event logs, LLM usage ledgers, generated draft notes, and
Python cache directories. It does not remove `.env`.
