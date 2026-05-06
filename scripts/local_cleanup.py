from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CleanupTarget:
    path: Path
    kind: str


def collect_targets(root: Path = ROOT) -> list[CleanupTarget]:
    targets: list[CleanupTarget] = []

    for pattern in [
        "data/events/*.jsonl",
        "data/llm/usage/*.jsonl",
        "content/research/drafts/*.md",
        "scripts/**/__pycache__",
        "src/**/__pycache__",
        "tests/**/__pycache__",
    ]:
        for path in root.glob(pattern):
            if path.exists():
                targets.append(
                    CleanupTarget(
                        path=path,
                        kind="dir" if path.is_dir() else "file",
                    )
                )

    return sorted(targets, key=lambda target: str(target.path))


def remove_target(target: CleanupTarget) -> None:
    if target.path.is_dir():
        shutil.rmtree(target.path)
    else:
        target.path.unlink()


def format_target(root: Path, target: CleanupTarget) -> str:
    try:
        relative = target.path.relative_to(root)
    except ValueError:
        relative = target.path
    return f"{target.kind} {relative}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List or remove ignored local runtime outputs.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually remove listed files. Without this flag the command is dry-run only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = collect_targets(ROOT)
    action = "remove" if args.apply else "would_remove"

    for target in targets:
        print(f"{action}={format_target(ROOT, target)}")
        if args.apply:
            remove_target(target)

    print(f"count={len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
