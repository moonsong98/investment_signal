from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import local_cleanup  # noqa: E402


class LocalCleanupTests(unittest.TestCase):
    def test_collect_targets_finds_ignored_runtime_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_file = root / "data/events/2026-05-06.jsonl"
            usage_file = root / "data/llm/usage/2026-05.jsonl"
            draft_file = root / "content/research/drafts/draft.md"
            cache_dir = root / "src/investment/__pycache__"
            for path in [event_file, usage_file, draft_file]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test\n", encoding="utf-8")
            cache_dir.mkdir(parents=True)

            targets = local_cleanup.collect_targets(root)
            rendered = [local_cleanup.format_target(root, target) for target in targets]

            self.assertIn("file data/events/2026-05-06.jsonl", rendered)
            self.assertIn("file data/llm/usage/2026-05.jsonl", rendered)
            self.assertIn("file content/research/drafts/draft.md", rendered)
            self.assertIn("dir src/investment/__pycache__", rendered)

    def test_remove_target_deletes_file_and_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            file_path = root / "data/events/2026-05-06.jsonl"
            dir_path = root / "tests/__pycache__"
            file_path.parent.mkdir(parents=True)
            file_path.write_text("test\n", encoding="utf-8")
            dir_path.mkdir(parents=True)

            local_cleanup.remove_target(local_cleanup.CleanupTarget(file_path, "file"))
            local_cleanup.remove_target(local_cleanup.CleanupTarget(dir_path, "dir"))

            self.assertFalse(file_path.exists())
            self.assertFalse(dir_path.exists())


if __name__ == "__main__":
    unittest.main()
