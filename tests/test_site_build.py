from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


class SiteBuildTests(unittest.TestCase):
    def test_build_site_outputs_expected_pages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            site_dir = Path(temp_dir)
            with patch.object(build_site, "SITE_DIR", site_dir):
                build_site.build_site()

            expected = {
                "index.html",
                "journal.html",
                "research.html",
                "macro.html",
                "strategy.html",
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
            site_dir = Path(temp_dir)
            with patch.object(build_site, "SITE_DIR", site_dir):
                build_site.build_site()

            events = json.loads((site_dir / "events.json").read_text())
            serialized = json.dumps(events)

            self.assertNotIn("secret", serialized)
            self.assertNotIn("replace-with-local-secret", serialized)
            self.assertEqual(
                [event["severity"] for event in events],
                ["level_1", "level_2", "level_3"],
            )


if __name__ == "__main__":
    unittest.main()
