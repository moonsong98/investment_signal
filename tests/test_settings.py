from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.config import Settings  # noqa: E402


def make_settings(app_env: str, secret: str) -> Settings:
    return Settings(
        app_env=app_env,
        tradingview_webhook_secret=secret,
        telegram_bot_token=None,
        telegram_chat_id=None,
        telegram_dry_run=True,
        event_log_dir=Path("data/events"),
        watchlist_path=Path("data/watchlists/watchlist.example.json"),
        enable_research_notes=True,
        research_note_dir=Path("content/research/drafts"),
        llm_dry_run=True,
        llm_usage_dir=Path("data/llm/usage"),
        llm_daily_limit=5,
        llm_monthly_limit=50,
    )


class SettingsTests(unittest.TestCase):
    def test_local_allows_placeholder_secret(self) -> None:
        settings = make_settings("local", "replace-with-local-secret")

        self.assertEqual(settings.tradingview_webhook_secret, "replace-with-local-secret")

    def test_test_env_allows_placeholder_secret(self) -> None:
        settings = make_settings("test", "replace-with-local-secret")

        self.assertEqual(settings.app_env, "test")

    def test_production_rejects_placeholder_secret(self) -> None:
        with self.assertRaises(ValueError):
            make_settings("production", "replace-with-local-secret")

    def test_production_accepts_real_secret(self) -> None:
        settings = make_settings("production", "production-secret-value")

        self.assertEqual(settings.tradingview_webhook_secret, "production-secret-value")

    def test_empty_secret_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_settings("local", "")


if __name__ == "__main__":
    unittest.main()
