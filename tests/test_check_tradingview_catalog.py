from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_tradingview_catalog  # noqa: E402


class CheckTradingViewCatalogTests(unittest.TestCase):
    def test_default_catalog_is_valid(self) -> None:
        errors = check_tradingview_catalog.validate_catalog()

        self.assertEqual(errors, [])

    def test_invalid_catalog_reports_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "catalog.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "id": "bad_alert",
                            "symbol": "UNKNOWN",
                            "asset_type": "bad_type",
                            "timeframe": "{{interval}}",
                            "alert_type": "rsi_overheated",
                            "message": "Bad alert"
                        }
                    ]
                ),
                encoding="utf-8",
            )

            errors = check_tradingview_catalog.validate_catalog(path)

            self.assertTrue(any("symbol is not in watchlist" in error for error in errors))
            self.assertTrue(any("unsupported asset_type" in error for error in errors))
            self.assertTrue(any("must not classify as level_1" in error for error in errors))
