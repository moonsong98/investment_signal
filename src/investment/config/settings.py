"""Environment-backed settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


LOCAL_APP_ENVS = {"local", "test", "dev", "development"}
PLACEHOLDER_WEBHOOK_SECRETS = {"replace-with-local-secret", "YOUR_SECRET_FROM_ENV"}


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
    watchlist_path: Path
    enable_research_notes: bool
    research_note_dir: Path
    llm_dry_run: bool
    llm_usage_dir: Path
    llm_daily_limit: int
    llm_monthly_limit: int

    def __post_init__(self) -> None:
        app_env = self.app_env.strip().lower()
        secret = self.tradingview_webhook_secret.strip()
        if not secret:
            raise ValueError("TRADINGVIEW_WEBHOOK_SECRET must not be empty")
        if app_env not in LOCAL_APP_ENVS and secret in PLACEHOLDER_WEBHOOK_SECRETS:
            raise ValueError(
                "TRADINGVIEW_WEBHOOK_SECRET must be changed outside local/test environments"
            )

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
            watchlist_path=Path(os.getenv("WATCHLIST_PATH", "data/watchlists/watchlist.example.json")),
            enable_research_notes=env_bool("ENABLE_RESEARCH_NOTES", True),
            research_note_dir=Path(os.getenv("RESEARCH_NOTE_DIR", "content/research/drafts")),
            llm_dry_run=env_bool("LLM_DRY_RUN", True),
            llm_usage_dir=Path(os.getenv("LLM_USAGE_DIR", "data/llm/usage")),
            llm_daily_limit=int(os.getenv("LLM_DAILY_LIMIT", "5")),
            llm_monthly_limit=int(os.getenv("LLM_MONTHLY_LIMIT", "50")),
        )
