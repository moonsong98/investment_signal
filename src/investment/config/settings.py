"""Environment-backed settings."""

from __future__ import annotations

import os
from dataclasses import dataclass


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str
    tradingview_webhook_secret: str
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    telegram_dry_run: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "local"),
            tradingview_webhook_secret=os.getenv(
                "TRADINGVIEW_WEBHOOK_SECRET",
                "replace-with-local-secret",
            ),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN") or None,
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID") or None,
            telegram_dry_run=env_bool("TELEGRAM_DRY_RUN", True),
        )
