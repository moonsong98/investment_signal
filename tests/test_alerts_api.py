from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.alerts import AlertValidationError, validate_tradingview_payload
from investment.config import Settings
from investment.logging import JsonlEventLogger, redact_payload
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
        self.assertEqual(len(alert.dedupe_key), 64)

    def test_crypto_sample_payloads_are_valid_level_2_events(self) -> None:
        for sample_name, expected_symbol in [
            ("tradingview_alert_btc_breakout.json", "BTC"),
            ("tradingview_alert_eth_breakout.json", "ETH"),
            ("tradingview_alert_sol_breakout.json", "SOL"),
        ]:
            with self.subTest(sample_name=sample_name):
                payload = self.load_payload(sample_name)

                alert = validate_tradingview_payload(
                    payload,
                    expected_secret="replace-with-local-secret",
                )

                self.assertEqual(alert.symbol, expected_symbol)
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

    def test_exchange_prefixed_symbol_is_allowed(self) -> None:
        payload = self.load_payload("tradingview_alert_btc_breakout.json")
        payload["symbol"] = "BINANCE:BTCUSDT"

        alert = validate_tradingview_payload(
            payload,
            expected_secret="replace-with-local-secret",
        )

        self.assertEqual(alert.symbol, "BINANCE:BTCUSDT")

    def test_unsupported_symbol_characters_are_rejected(self) -> None:
        payload = self.load_payload("tradingview_alert_level2.json")
        payload["symbol"] = "SPY<script>"

        with self.assertRaises(AlertValidationError):
            validate_tradingview_payload(
                payload,
                expected_secret="replace-with-local-secret",
            )

    def test_unsupported_alert_type_characters_are_rejected(self) -> None:
        payload = self.load_payload("tradingview_alert_level2.json")
        payload["alert_type"] = "breakout-20d-high"

        with self.assertRaises(AlertValidationError):
            validate_tradingview_payload(
                payload,
                expected_secret="replace-with-local-secret",
            )

    def test_overlong_message_is_rejected(self) -> None:
        payload = self.load_payload("tradingview_alert_level2.json")
        payload["message"] = "x" * 501

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


class EventLoggerTests(unittest.TestCase):
    def test_redact_payload_masks_sensitive_values(self) -> None:
        payload = {
            "secret": "real-secret",
            "symbol": "SPY",
            "nested": {"token": "real-token", "message": "ok"},
        }

        redacted = redact_payload(payload)

        self.assertEqual(redacted["secret"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["token"], "[REDACTED]")
        self.assertEqual(redacted["symbol"], "SPY")

    def test_jsonl_logger_writes_redacted_alert(self) -> None:
        payload = json.loads((ROOT / "data/samples/tradingview_alert_level2.json").read_text())
        alert = validate_tradingview_payload(
            payload,
            expected_secret="replace-with-local-secret",
        )
        notification = TelegramNotifier(bot_token=None, chat_id=None, dry_run=True).send_alert(
            alert
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            event = JsonlEventLogger(Path(temp_dir)).log_alert(
                alert=alert,
                raw_payload=payload,
                notification=notification,
            )
            log_files = list(Path(temp_dir).glob("*.jsonl"))

            self.assertEqual(len(log_files), 1)
            serialized = log_files[0].read_text()
            self.assertIn(event.event_id, serialized)
            self.assertIn(alert.dedupe_key, serialized)
            self.assertIn("[REDACTED]", serialized)
            self.assertNotIn("replace-with-local-secret", serialized)


class FastApiTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("fastapi is not installed; run with uv run --extra api")

        from investment.api import create_app

        self.temp_dir = tempfile.TemporaryDirectory()
        self.note_dir = Path(self.temp_dir.name) / "research"
        settings = Settings(
            app_env="test",
            tradingview_webhook_secret="replace-with-local-secret",
            telegram_bot_token=None,
            telegram_chat_id=None,
            telegram_dry_run=True,
            event_log_dir=Path(self.temp_dir.name),
            watchlist_path=ROOT / "data/watchlists/watchlist.example.json",
            enable_research_notes=True,
            research_note_dir=self.note_dir,
            llm_dry_run=True,
            llm_usage_dir=Path(self.temp_dir.name) / "llm",
            llm_daily_limit=5,
            llm_monthly_limit=50,
        )
        self.client = TestClient(create_app(settings))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

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
        self.assertEqual(body["duplicate"], False)
        self.assertIn("event_id", body)
        self.assertEqual(body["notification"]["reason"], "dry_run")
        self.assertEqual(body["research_note"]["created"], False)
        self.assertEqual(len(list(Path(self.temp_dir.name).glob("*.jsonl"))), 1)

    def test_webhook_skips_duplicate_payload(self) -> None:
        payload = json.loads((ROOT / "data/samples/tradingview_alert_level2.json").read_text())

        first = self.client.post("/webhooks/tradingview", json=payload)
        second = self.client.post("/webhooks/tradingview", json=payload)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        body = second.json()
        self.assertEqual(body["duplicate"], True)
        self.assertEqual(body["notification"]["reason"], "duplicate")
        self.assertEqual(len(list(Path(self.temp_dir.name).glob("*.jsonl"))), 1)

    def test_webhook_generates_research_note_for_level_3(self) -> None:
        payload = json.loads((ROOT / "data/samples/tradingview_alert_level3.json").read_text())

        response = self.client.post("/webhooks/tradingview", json=payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["severity"], "level_3")
        self.assertEqual(body["research_note"]["created"], True)
        self.assertEqual(body["llm_usage"]["within_limits"], True)
        notes = list(self.note_dir.glob("*.md"))
        self.assertEqual(len(notes), 1)
        note_text = notes[0].read_text(encoding="utf-8")
        self.assertIn("Generated Research Note Draft", note_text)
        self.assertIn("No matching watchlist item was found", note_text)
        self.assertNotIn("replace-with-local-secret", note_text)
        self.assertNotIn("[REDACTED]", note_text)
        usage_logs = list((Path(self.temp_dir.name) / "llm").glob("*.jsonl"))
        self.assertEqual(len(usage_logs), 1)

    def test_webhook_rejects_invalid_secret(self) -> None:
        payload = json.loads(
            (ROOT / "data/samples/tradingview_alert_invalid_secret.json").read_text()
        )

        response = self.client.post("/webhooks/tradingview", json=payload)

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
