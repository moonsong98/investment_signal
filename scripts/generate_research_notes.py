from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.research import generate_research_notes  # noqa: E402


def main() -> int:
    notes = generate_research_notes(
        event_dir=ROOT / "data/events",
        output_dir=ROOT / "content/research/drafts",
    )
    print(f"generated_notes={len(notes)}")
    for note in notes:
        print(note.path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
