"""FastAPI webhook application."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, status

from investment.alerts import AlertValidationError, validate_tradingview_payload
from investment.config import Settings
from investment.logging import JsonlEventLogger
from investment.notifications import TelegramNotifier


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings.from_env()
    app = FastAPI(title="Investment Alert Webhook", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "app_env": app_settings.app_env}

    @app.post("/webhooks/tradingview")
    def tradingview_webhook(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            alert = validate_tradingview_payload(
                payload,
                expected_secret=app_settings.tradingview_webhook_secret,
            )
        except AlertValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        notifier = TelegramNotifier(
            bot_token=app_settings.telegram_bot_token,
            chat_id=app_settings.telegram_chat_id,
            dry_run=app_settings.telegram_dry_run,
        )
        notification = notifier.send_alert(alert)
        logged_event = JsonlEventLogger(app_settings.event_log_dir).log_alert(
            alert=alert,
            raw_payload=payload,
            notification=notification,
        )

        return {
            "ok": True,
            "event_id": logged_event.event_id,
            "symbol": alert.symbol,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value,
            "notification": {
                "sent": notification.sent,
                "dry_run": notification.dry_run,
                "reason": notification.reason,
            },
        }

    return app


app = create_app()
