from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tail_events  # noqa: E402


def event_payload(symbol: str, received_at: str) -> dict:
    return {
        "received_at": received_at,
        "event_at": "2026-05-06T00:00:00+00:00",
        "symbol": symbol,
        "severity": "level_2",
        "alert_type": "breakout_20d_high",
        "notification": {"reason": "dry_run"},
        "payload": {
            "message": f"{symbol} breakout",
            "secret": "[REDACTED]",
        },
    }


class TailEventsTests(unittest.TestCase):
    def test_tail_events_returns_recent_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            event_dir.joinpath("2026-05-06.jsonl").write_text(
                json.dumps(event_payload("BTC", "2026-05-06T00:00:00+00:00"))
                + "\n"
                + json.dumps(event_payload("ETH", "2026-05-06T00:01:00+00:00"))
                + "\n",
                encoding="utf-8",
            )

            lines = tail_events.tail_events(event_dir, limit=1)

            self.assertEqual(len(lines), 1)
            self.assertIn("symbol=ETH", lines[0])
            self.assertIn("notification=dry_run", lines[0])
            self.assertNotIn("secret", lines[0].lower())
            self.assertNotIn("[REDACTED]", lines[0])

    def test_missing_event_dir_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            lines = tail_events.tail_events(Path(temp_dir) / "missing", limit=10)

            self.assertEqual(lines, [])


if __name__ == "__main__":
    unittest.main()
