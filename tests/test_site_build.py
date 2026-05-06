from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


def copy_public_test_data(temp_dir: Path) -> Path:
    data_dir = temp_dir / "data"
    shutil.copytree(ROOT / "data/samples", data_dir / "samples")
    shutil.copytree(ROOT / "data/watchlists", data_dir / "watchlists")
    (data_dir / "events").mkdir()
    return data_dir


class SiteBuildTests(unittest.TestCase):
    def test_build_site_outputs_expected_pages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site_dir = root / "site"
            data_dir = copy_public_test_data(root)
            with patch.object(build_site, "SITE_DIR", site_dir):
                with patch.object(build_site, "DATA_DIR", data_dir):
                    build_site.build_site()

            expected = {
                "index.html",
                "journal.html",
                "research.html",
                "macro.html",
                "strategy.html",
                "watchlist.html",
                "watchlist.json",
                "events.html",
                "events.json",
                "assets/market-overview.png",
                "assets/styles.css",
            }
            generated = {
                str(path.relative_to(site_dir))
                for path in site_dir.rglob("*")
                if path.is_file()
            }

            self.assertTrue(expected.issubset(generated))

    def test_events_json_excludes_webhook_secret(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site_dir = root / "site"
            data_dir = copy_public_test_data(root)
            with patch.object(build_site, "SITE_DIR", site_dir):
                with patch.object(build_site, "DATA_DIR", data_dir):
                    build_site.build_site()

            events = json.loads((site_dir / "events.json").read_text())
            serialized = json.dumps(events)

            self.assertNotIn("secret", serialized)
            self.assertNotIn("replace-with-local-secret", serialized)
            severities = {event["severity"] for event in events}
            symbols = {event["symbol"] for event in events}

            self.assertTrue({"level_1", "level_2", "level_3"}.issubset(severities))
            self.assertTrue({"BTC", "ETH", "SOL"}.issubset(symbols))

    def test_events_json_uses_redacted_event_logs_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            site_dir = Path(temp_dir) / "site"
            data_dir = Path(temp_dir) / "data"
            event_dir = data_dir / "events"
            event_dir.mkdir(parents=True)
            event_dir.joinpath("2026-05-06.jsonl").write_text(
                json.dumps(
                    {
                        "event_id": "event-1",
                        "received_at": "2026-05-06T00:00:00+00:00",
                        "event_at": "2026-05-05T13:30:00+00:00",
                        "source": "tradingview",
                        "symbol": "BTC",
                        "asset_type": "crypto",
                        "timeframe": "1D",
                        "alert_type": "breakout_20d_high",
                        "severity": "level_2",
                        "notification": {
                            "sent": False,
                            "dry_run": True,
                            "reason": "dry_run",
                        },
                        "payload": {
                            "message": "BTC breakout",
                            "secret": "[REDACTED]",
                            "raw": "should-not-publish",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with patch.object(build_site, "SITE_DIR", site_dir):
                with patch.object(build_site, "DATA_DIR", data_dir):
                    build_site.build_events()

            events = json.loads((site_dir / "events.json").read_text())
            serialized = json.dumps(events)

            self.assertEqual(events[0]["symbol"], "BTC")
            self.assertEqual(events[0]["notification_reason"], "dry_run")
            self.assertNotIn("event_id", events[0])
            self.assertNotIn("notification_sent", events[0])
            self.assertNotIn("secret", serialized)
            self.assertNotIn("raw", serialized)
            self.assertNotIn("should-not-publish", serialized)

    def test_watchlist_json_includes_crypto_monitoring_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site_dir = root / "site"
            data_dir = copy_public_test_data(root)
            with patch.object(build_site, "SITE_DIR", site_dir):
                with patch.object(build_site, "DATA_DIR", data_dir):
                    build_site.build_site()

            watchlist = json.loads((site_dir / "watchlist.json").read_text())
            symbols = {item["symbol"] for item in watchlist}

            self.assertTrue({"BTC", "ETH", "SOL"}.issubset(symbols))
            self.assertNotIn("thesis", watchlist[0])
            self.assertNotIn("risk_notes", watchlist[0])


if __name__ == "__main__":
    unittest.main()
