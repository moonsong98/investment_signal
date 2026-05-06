from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ops_status  # noqa: E402


class OpsStatusTests(unittest.TestCase):
    def test_load_event_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            event_dir.joinpath("2026-05-06.jsonl").write_text(
                json.dumps(
                    {
                        "received_at": "2026-05-06T00:00:00+00:00",
                        "event_at": "2026-05-05T13:30:00+00:00",
                        "symbol": "BTC",
                        "severity": "level_3",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            summary = ops_status.load_event_summary(event_dir)

            self.assertEqual(summary.total_events, 1)
            self.assertEqual(summary.latest_symbol, "BTC")
            self.assertEqual(summary.latest_severity, "level_3")

    def test_empty_event_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            summary = ops_status.load_event_summary(Path(temp_dir))

            self.assertEqual(summary.total_events, 0)
            self.assertIsNone(summary.latest_symbol)

    def test_count_jsonl_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "usage.jsonl"
            path.write_text("{}\n\n{}\n", encoding="utf-8")

            self.assertEqual(ops_status.count_jsonl_records(path), 2)


if __name__ == "__main__":
    unittest.main()
