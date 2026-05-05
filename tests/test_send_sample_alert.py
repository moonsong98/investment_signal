from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import error


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import send_sample_alert  # noqa: E402


class SendSampleAlertTests(unittest.TestCase):
    def test_load_dotenv_does_not_override_existing_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("TRADINGVIEW_WEBHOOK_SECRET=file-secret\n", encoding="utf-8")

            with patch.dict(os.environ, {"TRADINGVIEW_WEBHOOK_SECRET": "existing-secret"}):
                send_sample_alert.load_dotenv(env_path)

                self.assertEqual(os.environ["TRADINGVIEW_WEBHOOK_SECRET"], "existing-secret")

    def test_load_payload_injects_secret_without_printing(self) -> None:
        payload = send_sample_alert.load_payload(
            ROOT / "data/samples/tradingview_alert_level2.json",
            "runtime-secret",
        )

        self.assertEqual(payload["secret"], "runtime-secret")

    def test_main_does_not_print_secret(self) -> None:
        response = {"ok": True, "notification": {"reason": "dry_run"}}
        with patch.dict(os.environ, {"TRADINGVIEW_WEBHOOK_SECRET": "runtime-secret"}):
            with patch.object(send_sample_alert, "post_payload", return_value=(200, json.dumps(response))):
                with patch.object(sys, "argv", ["send_sample_alert.py"]):
                    with patch("builtins.print") as print_mock:
                        exit_code = send_sample_alert.main()

        printed = "\n".join(str(call.args[0]) for call in print_mock.call_args_list)
        self.assertEqual(exit_code, 0)
        self.assertNotIn("runtime-secret", printed)
        self.assertIn("status=200", printed)

    def test_connection_error_is_reported_without_secret(self) -> None:
        payload = {"secret": "runtime-secret", "symbol": "SPY"}
        with patch("urllib.request.urlopen", side_effect=error.URLError("connection refused")):
            status_code, response_body = send_sample_alert.post_payload(
                "http://127.0.0.1:9/webhooks/tradingview",
                payload,
            )

        self.assertEqual(status_code, 0)
        self.assertNotIn("runtime-secret", response_body)


if __name__ == "__main__":
    unittest.main()
