from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import promote_research_draft  # noqa: E402


class PromoteResearchDraftTests(unittest.TestCase):
    def test_promotes_reviewed_copy_without_removing_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_dir = root / "content/research/drafts"
            output_dir = root / "content/research"
            draft_dir.mkdir(parents=True)
            draft = draft_dir / "2026-05-06-btc-event.md"
            draft.write_text(
                "# Draft\n\nStatus: draft\nHuman Review: required\n",
                encoding="utf-8",
            )

            with patch.object(promote_research_draft, "ROOT", root):
                with patch.object(promote_research_draft, "DEFAULT_DRAFT_DIR", draft_dir):
                    target = promote_research_draft.promote_draft(
                        draft,
                        output_dir=output_dir,
                    )

            self.assertTrue(draft.exists())
            self.assertTrue(target.exists())
            text = target.read_text(encoding="utf-8")
            self.assertIn("Status: reviewed", text)
            self.assertIn("Human Review: completed", text)

    def test_rejects_paths_outside_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_dir = root / "content/research/drafts"
            outside = root / "content/research/private.md"
            draft_dir.mkdir(parents=True)
            outside.parent.mkdir(parents=True, exist_ok=True)
            outside.write_text("# Private\n", encoding="utf-8")

            with patch.object(promote_research_draft, "ROOT", root):
                with patch.object(promote_research_draft, "DEFAULT_DRAFT_DIR", draft_dir):
                    with self.assertRaises(ValueError):
                        promote_research_draft.promote_draft(outside)

    def test_rejects_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_dir = root / "content/research/drafts"
            output_dir = root / "content/research"
            draft_dir.mkdir(parents=True)
            draft = draft_dir / "2026-05-06-btc-event.md"
            draft.write_text("# Draft\n", encoding="utf-8")
            target = output_dir / draft.name
            target.write_text("# Existing\n", encoding="utf-8")

            with patch.object(promote_research_draft, "ROOT", root):
                with patch.object(promote_research_draft, "DEFAULT_DRAFT_DIR", draft_dir):
                    with self.assertRaises(FileExistsError):
                        promote_research_draft.promote_draft(draft, output_dir=output_dir)


if __name__ == "__main__":
    unittest.main()
