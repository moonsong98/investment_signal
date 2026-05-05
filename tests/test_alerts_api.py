from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.alerts import AlertValidationError, validate_tradingview_payload
from investment.config import Settings
from investment.models import Severity
from investment.notifications import TelegramNotifier, should_notify


class AlertValidationTests(unittest.TestCase):
    def load_payload(self, name: str) -> dict:
        return json.loads((ROOT / f"data/samples/{name}").read_text())

    def test_valid_level_2_payload(self) -> None:
        payload = self.load_payload("tradingview_alert_level2.json")

        alert = validate_tradingview_payload(
            payload,
            expected_secret="replace-with-local-secret",
        )

        self.assertEqual(alert.symbol, "SPY")
        self.assertEqual(alert.severity, Severity.LEVEL_2)

    def test_invalid_secret_rejected(self) -> None:
        payload = self.load_payload("tradingview_alert_invalid_secret.json")

        with self.assertRaises(AlertValidationError):
            validate_tradingview_payload(
                payload,
                expected_secret="replace-with-local-secret",
            )

    def test_missing_required_field_rejected(self) -> None:
        payload = self.load_payload("tradingview_alert_level2.json")
        del payload["symbol"]

        with self.assertRaises(AlertValidationError):
            validate_tradingview_payload(
                payload,
                expected_secret="replace-with-local-secret",
            )


class NotificationTests(unittest.TestCase):
    def test_level_1_does_not_notify(self) -> None:
        self.assertFalse(should_notify(Severity.LEVEL_1))

    def test_level_2_dry_run_notification(self) -> None:
        payload = json.loads((ROOT / "data/samples/tradingview_alert_level2.json").read_text())
        alert = validate_tradingview_payload(
            payload,
            expected_secret="replace-with-local-secret",
        )
        notifier = TelegramNotifier(bot_token=None, chat_id=None, dry_run=True)

        result = notifier.send_alert(alert)

        self.assertFalse(result.sent)
        self.assertTrue(result.dry_run)
        self.assertEqual(result.reason, "dry_run")
        self.assertIn("Human review required", result.message)


class FastApiTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("fastapi is not installed; run with uv run --extra api")

        from investment.api import create_app

        settings = Settings(
            app_env="test",
            tradingview_webhook_secret="replace-with-local-secret",
            telegram_bot_token=None,
            telegram_chat_id=None,
            telegram_dry_run=True,
        )
        self.client = TestClient(create_app(settings))

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_webhook_accepts_valid_payload(self) -> None:
        payload = json.loads((ROOT / "data/samples/tradingview_alert_level2.json").read_text())

        response = self.client.post("/webhooks/tradingview", json=payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["severity"], "level_2")
        self.assertEqual(body["notification"]["reason"], "dry_run")

    def test_webhook_rejects_invalid_secret(self) -> None:
        payload = json.loads(
            (ROOT / "data/samples/tradingview_alert_invalid_secret.json").read_text()
        )

        response = self.client.post("/webhooks/tradingview", json=payload)

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
