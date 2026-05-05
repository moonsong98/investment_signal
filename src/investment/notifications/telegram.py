"""Telegram notification client."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import request

from investment.alerts import TradingViewAlert
from investment.models import Severity


@dataclass(frozen=True)
class NotificationResult:
    sent: bool
    dry_run: bool
    reason: str
    message: str


def should_notify(severity: Severity) -> bool:
    return severity in {Severity.LEVEL_2, Severity.LEVEL_3}


def format_telegram_message(alert: TradingViewAlert) -> str:
    prefix = "Research alert" if alert.severity is Severity.LEVEL_2 else "Important research alert"
    price_line = f"\nPrice: {alert.price:g}" if alert.price is not None else ""
    return (
        f"{prefix}\n"
        f"Severity: {alert.severity.value}\n"
        f"Symbol: {alert.symbol}\n"
        f"Asset: {alert.asset_type.value}\n"
        f"Timeframe: {alert.timeframe}\n"
        f"Alert: {alert.alert_type}\n"
        f"Event time: {alert.event_at.isoformat()}"
        f"{price_line}\n"
        f"Message: {alert.message}\n\n"
        "Human review required. This is not financial advice."
    )


class TelegramNotifier:
    def __init__(self, bot_token: str | None, chat_id: str | None, dry_run: bool) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.dry_run = dry_run

    def send_alert(self, alert: TradingViewAlert) -> NotificationResult:
        if not should_notify(alert.severity):
            return NotificationResult(
                sent=False,
                dry_run=self.dry_run,
                reason="severity_is_log_only",
                message="",
            )

        message = format_telegram_message(alert)
        if self.dry_run:
            return NotificationResult(
                sent=False,
                dry_run=True,
                reason="dry_run",
                message=message,
            )
        if not self.bot_token or not self.chat_id:
            return NotificationResult(
                sent=False,
                dry_run=False,
                reason="missing_telegram_config",
                message=message,
            )

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        body = json.dumps({"chat_id": self.chat_id, "text": message}).encode("utf-8")
        req = request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=10) as response:
            response.read()

        return NotificationResult(
            sent=True,
            dry_run=False,
            reason="sent",
            message=message,
        )
