from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.llm import AnalysisPolicy, analyze_event, is_analysis_eligible


class LlmAnalysisTests(unittest.TestCase):
    def test_level_3_event_is_eligible(self) -> None:
        event = {"severity": "level_3"}

        self.assertTrue(is_analysis_eligible(event, AnalysisPolicy()))

    def test_level_2_event_is_not_eligible(self) -> None:
        event = {"severity": "level_2"}

        self.assertFalse(is_analysis_eligible(event, AnalysisPolicy()))
        analysis = analyze_event(event)
        self.assertFalse(analysis.eligible)
        self.assertEqual(analysis.skipped_reason, "severity_below_level_3")

    def test_analysis_is_disabled_by_policy(self) -> None:
        event = {"severity": "level_3"}

        analysis = analyze_event(event, AnalysisPolicy(enabled=False))

        self.assertFalse(analysis.eligible)
        self.assertEqual(analysis.skipped_reason, "analysis_disabled")

    def test_level_3_analysis_never_makes_trade_decision(self) -> None:
        event = {
            "severity": "level_3",
            "symbol": "BTC",
            "asset_type": "crypto",
            "alert_type": "support_breakdown",
            "timeframe": "1D",
            "payload": {"message": "Support breakdown"},
        }

        analysis = analyze_event(event)

        self.assertTrue(analysis.eligible)
        self.assertFalse(analysis.llm_used)
        self.assertIn("not as a trade decision", analysis.summary)


if __name__ == "__main__":
    unittest.main()
