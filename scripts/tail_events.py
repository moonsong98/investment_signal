from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENT_DIR = ROOT / "data/events"


def load_events(event_dir: Path | str = DEFAULT_EVENT_DIR) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for path in sorted(Path(event_dir).glob("*.jsonl")):
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            events.append(json.loads(raw_line))
    return sorted(events, key=lambda event: str(event.get("received_at", "")))


def format_event(event: dict[str, Any]) -> str:
    notification = event.get("notification") or {}
    payload = event.get("payload") or {}
    parts = [
        f"received_at={event.get('received_at', '')}",
        f"event_at={event.get('event_at', '')}",
        f"symbol={event.get('symbol', '')}",
        f"severity={event.get('severity', '')}",
        f"alert_type={event.get('alert_type', '')}",
        f"notification={notification.get('reason', '')}",
    ]
    message = str(payload.get("message", "")).strip()
    if message:
        parts.append(f"message={message}")
    return " ".join(parts)


def tail_events(event_dir: Path | str = DEFAULT_EVENT_DIR, limit: int = 10) -> list[str]:
    events = load_events(event_dir)
    return [format_event(event) for event in events[-limit:]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a secret-safe summary of recent local event logs.",
    )
    parser.add_argument(
        "--event-dir",
        default=str(DEFAULT_EVENT_DIR),
        help="Directory containing local JSONL event logs.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of recent events to print.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for line in tail_events(Path(args.event_dir), max(args.limit, 0)):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
