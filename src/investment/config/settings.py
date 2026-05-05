"""Environment-backed settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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
    event_log_dir: Path
    enable_research_notes: bool
    research_note_dir: Path

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
            event_log_dir=Path(os.getenv("EVENT_LOG_DIR", "data/events")),
            enable_research_notes=env_bool("ENABLE_RESEARCH_NOTES", True),
            research_note_dir=Path(os.getenv("RESEARCH_NOTE_DIR", "content/research")),
        )
