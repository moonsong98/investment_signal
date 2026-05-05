from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.models import AssetType, Severity, WatchlistItem
from investment.rules import classify_alert_type


class ModelTests(unittest.TestCase):
    def test_watchlist_sample_matches_model(self) -> None:
        payload = json.loads((ROOT / "data/watchlists/watchlist.example.json").read_text())

        items = [
            WatchlistItem(
                symbol=item["symbol"],
                name=item["name"],
                asset_type=AssetType(item["asset_type"]),
                market=item["market"],
                currency=item["currency"],
                thesis=item["thesis"],
                risk_notes=item["risk_notes"],
                tags=item["tags"],
                priority=item["priority"],
                active=item["active"],
            )
            for item in payload
        ]

        self.assertGreaterEqual(len(items), 1)
        self.assertTrue(all(item.active for item in items))
        self.assertEqual(
            {"BTC", "ETH", "SOL"}.intersection({item.symbol for item in items}),
            {"BTC", "ETH", "SOL"},
        )


class SeverityRuleTests(unittest.TestCase):
    def test_level_1_default(self) -> None:
        self.assertEqual(classify_alert_type("rsi_overbought"), Severity.LEVEL_1)

    def test_level_2_alert(self) -> None:
        self.assertEqual(classify_alert_type("breakout_20d_high"), Severity.LEVEL_2)

    def test_level_3_alert(self) -> None:
        self.assertEqual(
            classify_alert_type("earnings_shock_support_breakdown"),
            Severity.LEVEL_3,
        )


if __name__ == "__main__":
    unittest.main()
