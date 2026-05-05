from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRAFT_DIR = ROOT / "content/research/drafts"
DEFAULT_RESEARCH_DIR = ROOT / "content/research"


def require_relative_to(path: Path, parent: Path) -> None:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise ValueError(f"{path} must be inside {parent}") from exc


def promote_draft(
    draft_path: Path,
    output_dir: Path = DEFAULT_RESEARCH_DIR,
    remove_draft: bool = False,
) -> Path:
    draft = draft_path.expanduser()
    if not draft.is_absolute():
        draft = ROOT / draft
    require_relative_to(draft, DEFAULT_DRAFT_DIR)
    if not draft.exists():
        raise FileNotFoundError(f"draft not found: {draft}")
    if draft.suffix != ".md":
        raise ValueError("draft must be a Markdown file")

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / draft.name
    if target.exists():
        raise FileExistsError(f"target already exists: {target}")

    text = draft.read_text(encoding="utf-8")
    if "Human Review: required" in text:
        text = text.replace("Human Review: required", "Human Review: completed")
    if "Status: draft" in text:
        text = text.replace("Status: draft", "Status: reviewed")

    target.write_text(text, encoding="utf-8")
    if remove_draft:
        draft.unlink()
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a reviewed generated draft into public research content.",
    )
    parser.add_argument("draft", help="Path to a draft under content/research/drafts")
    parser.add_argument(
        "--remove-draft",
        action="store_true",
        help="Remove the ignored draft after promotion.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        target = promote_draft(Path(args.draft), remove_draft=args.remove_draft)
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
