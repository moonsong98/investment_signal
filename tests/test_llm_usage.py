from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.llm import UsageLedger, UsageLimits, new_usage_record


class LlmUsageTests(unittest.TestCase):
    def test_usage_ledger_records_and_summarizes_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = UsageLedger(Path(temp_dir))
            now = datetime(2026, 5, 6, tzinfo=UTC)
            ledger.record(new_usage_record("event-1", now=now))
            ledger.record(new_usage_record("event-2", now=now))

            summary = ledger.summarize(
                UsageLimits(daily_limit=5, monthly_limit=10),
                now=now,
            )

            self.assertEqual(summary.daily_count, 2)
            self.assertEqual(summary.monthly_count, 2)
            self.assertTrue(summary.within_limits)

    def test_usage_summary_detects_limit_exhaustion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = UsageLedger(Path(temp_dir))
            now = datetime(2026, 5, 6, tzinfo=UTC)
            ledger.record(new_usage_record("event-1", now=now))

            summary = ledger.summarize(
                UsageLimits(daily_limit=1, monthly_limit=10),
                now=now,
            )

            self.assertFalse(summary.within_limits)


if __name__ == "__main__":
    unittest.main()
