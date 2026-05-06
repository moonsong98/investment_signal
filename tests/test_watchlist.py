from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.watchlist import find_watchlist_item, load_watchlist


class WatchlistTests(unittest.TestCase):
    def test_load_and_find_crypto_items(self) -> None:
        watchlist = load_watchlist(ROOT / "data/watchlists/watchlist.example.json")

        btc = find_watchlist_item("btc", watchlist)
        eth = find_watchlist_item("ETH", watchlist)

        self.assertIsNotNone(btc)
        self.assertIsNotNone(eth)
        self.assertEqual(btc["name"], "Bitcoin")
        self.assertEqual(eth["asset_type"], "crypto")

    def test_find_watchlist_item_matches_aliases(self) -> None:
        watchlist = load_watchlist(ROOT / "data/watchlists/watchlist.example.json")

        btc = find_watchlist_item("BINANCE:BTCUSDT", watchlist)
        sol = find_watchlist_item("solusdt", watchlist)

        self.assertIsNotNone(btc)
        self.assertIsNotNone(sol)
        self.assertEqual(btc["symbol"], "BTC")
        self.assertEqual(sol["symbol"], "SOL")

    def test_missing_watchlist_returns_empty_list(self) -> None:
        watchlist = load_watchlist(ROOT / "data/watchlists/missing.json")

        self.assertEqual(watchlist, [])


if __name__ == "__main__":
    unittest.main()
