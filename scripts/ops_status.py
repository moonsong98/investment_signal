from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class EventSummary:
    total_events: int
    latest_symbol: str | None
    latest_severity: str | None
    latest_event_at: str | None


def count_jsonl_records(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def load_event_summary(event_dir: Path) -> EventSummary:
    events = []
    if event_dir.exists():
        for path in sorted(event_dir.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(json.loads(line))

    if not events:
        return EventSummary(
            total_events=0,
            latest_symbol=None,
            latest_severity=None,
            latest_event_at=None,
        )

    latest = sorted(events, key=lambda event: event.get("received_at", ""))[-1]
    return EventSummary(
        total_events=len(events),
        latest_symbol=latest.get("symbol"),
        latest_severity=latest.get("severity"),
        latest_event_at=latest.get("event_at"),
    )


def count_files(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def check_health(url: str) -> str:
    try:
        with request.urlopen(url, timeout=3) as response:
            if response.status == 200:
                return "ok"
            return f"status_{response.status}"
    except error.URLError:
        return "unreachable"


def docker_compose_status() -> str:
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--status", "running", "--services"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unavailable"
    if result.returncode != 0:
        return "unavailable"
    services = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return ",".join(services) if services else "none"


def build_status(health_url: str) -> dict[str, str | int | None]:
    event_summary = load_event_summary(ROOT / "data/events")
    return {
        "health": check_health(health_url),
        "docker_services": docker_compose_status(),
        "event_count": event_summary.total_events,
        "latest_symbol": event_summary.latest_symbol,
        "latest_severity": event_summary.latest_severity,
        "latest_event_at": event_summary.latest_event_at,
        "draft_count": count_files(ROOT / "content/research/drafts", "*.md"),
        "llm_usage_records": sum(
            count_jsonl_records(path)
            for path in (ROOT / "data/llm/usage").glob("*.jsonl")
        )
        if (ROOT / "data/llm/usage").exists()
        else 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print secret-safe local operations status.")
    parser.add_argument(
        "--health-url",
        default="http://127.0.0.1:8000/health",
        help="Health endpoint to check.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status = build_status(args.health_url)
    for key, value in status.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
