from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import render_tradingview_alerts  # noqa: E402


class RenderTradingViewAlertsTests(unittest.TestCase):
    def test_default_catalog_renders_copyable_alert_messages(self) -> None:
        catalog = render_tradingview_alerts.load_catalog()

        rendered = render_tradingview_alerts.render_catalog(catalog, symbol="BTC")

        self.assertIn("# btc_breakout_20d_high_1d", rendered)
        self.assertIn('"symbol": "BTC"', rendered)
        self.assertIn('"secret": "YOUR_SECRET_FROM_ENV"', rendered)
        self.assertIn('"event_at": "{{time}}"', rendered)
        self.assertIn('"price": {{close}}', rendered)

    def test_catalog_filter_matches_alert_id(self) -> None:
        catalog = render_tradingview_alerts.load_catalog()

        filtered = render_tradingview_alerts.filter_catalog(
            catalog,
            alert_id="eth_breakout_20d_high_1d",
        )

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["symbol"], "ETH")

    def test_render_message_rejects_missing_required_fields(self) -> None:
        with self.assertRaises(ValueError):
            render_tradingview_alerts.render_alert_message({"symbol": "BTC"})

    def test_load_catalog_rejects_non_list_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "catalog.json"
            path.write_text(json.dumps({"id": "bad"}), encoding="utf-8")

            with self.assertRaises(ValueError):
                render_tradingview_alerts.load_catalog(path)


if __name__ == "__main__":
    unittest.main()
