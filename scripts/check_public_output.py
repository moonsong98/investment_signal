from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHS = [
    ROOT / "site",
    ROOT / "content/journal",
    ROOT / "content/macro",
    ROOT / "content/research",
    ROOT / "content/strategy",
]
IGNORED_DIR_NAMES = {"drafts", "private", "__pycache__"}
SECRET_PATTERNS = {
    "placeholder_secret": re.compile(r"replace-with-local-secret", re.IGNORECASE),
    "api_key": re.compile(r"\b(api[_-]?key|secret[_-]?key|access[_-]?token)\b", re.IGNORECASE),
    "account_id": re.compile(r"\b(account[_-]?id|broker[_-]?account)\b", re.IGNORECASE),
    "redacted_marker": re.compile(r"\[REDACTED\]"),
    "raw_payload": re.compile(r"\b(raw_payload|authorization|password)\b", re.IGNORECASE),
}


@dataclass(frozen=True)
class Finding:
    path: Path
    pattern_name: str


def iter_public_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
            continue
        for file in path.rglob("*"):
            if not file.is_file():
                continue
            if any(part in IGNORED_DIR_NAMES for part in file.relative_to(path).parts):
                continue
            files.append(file)
    return sorted(files)


def scan_file(path: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    findings = []
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            findings.append(Finding(path=path, pattern_name=name))
    return findings


def scan_public_output(paths: list[Path] | None = None) -> list[Finding]:
    active_paths = paths or DEFAULT_PATHS
    findings: list[Finding] = []
    for file in iter_public_files(active_paths):
        findings.extend(scan_file(file))
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan public output for sensitive patterns.")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional paths to scan. Defaults to public site and content directories.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [Path(path) for path in args.paths] if args.paths else None
    findings = scan_public_output(paths)
    for finding in findings:
        print(f"{finding.path}: {finding.pattern_name}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
