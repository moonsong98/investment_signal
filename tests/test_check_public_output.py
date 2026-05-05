from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_public_output  # noqa: E402


class CheckPublicOutputTests(unittest.TestCase):
    def test_detects_secret_like_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "site"
            path.mkdir()
            (path / "events.json").write_text(
                '{"secret": "replace-with-local-secret"}',
                encoding="utf-8",
            )

            findings = check_public_output.scan_public_output([path])

            self.assertGreaterEqual(len(findings), 1)
            self.assertEqual(findings[0].pattern_name, "placeholder_secret")

    def test_ignores_drafts_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "content/research"
            draft_dir = path / "drafts"
            draft_dir.mkdir(parents=True)
            (draft_dir / "draft.md").write_text("[REDACTED]", encoding="utf-8")

            findings = check_public_output.scan_public_output([path])

            self.assertEqual(findings, [])

    def test_allows_normal_public_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "site"
            path.mkdir()
            (path / "index.html").write_text("<h1>Research Lab</h1>", encoding="utf-8")

            findings = check_public_output.scan_public_output([path])

            self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
