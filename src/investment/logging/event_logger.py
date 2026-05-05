"""Structured event logging with secret redaction."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from investment.alerts import TradingViewAlert
from investment.notifications import NotificationResult


SENSITIVE_KEYS = {
    "secret",
    "token",
    "api_key",
    "apikey",
    "password",
    "authorization",
    "credential",
    "credentials",
}


@dataclass(frozen=True)
class LoggedEvent:
    event_id: str
    received_at: str
    source: str
    symbol: str
    asset_type: str
    timeframe: str
    alert_type: str
    event_at: str
    severity: str
    notification: dict[str, Any]
    payload: dict[str, Any]


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if key.lower() in SENSITIVE_KEYS:
            redacted[key] = "[REDACTED]"
        elif isinstance(value, dict):
            redacted[key] = redact_payload(value)
        else:
            redacted[key] = value
    return redacted


class JsonlEventLogger:
    def __init__(self, log_dir: Path | str) -> None:
        self.log_dir = Path(log_dir)

    def log_alert(
        self,
        alert: TradingViewAlert,
        raw_payload: dict[str, Any],
        notification: NotificationResult,
    ) -> LoggedEvent:
        received_at = datetime.now(UTC)
        event = LoggedEvent(
            event_id=str(uuid4()),
            received_at=received_at.isoformat(),
            source=alert.source.value,
            symbol=alert.symbol,
            asset_type=alert.asset_type.value,
            timeframe=alert.timeframe,
            alert_type=alert.alert_type,
            event_at=alert.event_at.isoformat(),
            severity=alert.severity.value,
            notification={
                "sent": notification.sent,
                "dry_run": notification.dry_run,
                "reason": notification.reason,
            },
            payload=redact_payload(raw_payload),
        )
        self.write(event)
        return event

    def write(self, event: LoggedEvent) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self.log_dir / f"{event.received_at[:10]}.jsonl"
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(asdict(event), sort_keys=True) + "\n")
