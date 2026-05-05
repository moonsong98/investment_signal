"""Local LLM usage ledger for budget control."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class UsageRecord:
    recorded_at: str
    event_id: str
    provider: str
    model: str
    dry_run: bool
    estimated_input_tokens: int
    estimated_output_tokens: int


@dataclass(frozen=True)
class UsageLimits:
    daily_limit: int
    monthly_limit: int


@dataclass(frozen=True)
class UsageSummary:
    daily_count: int
    monthly_count: int
    daily_limit: int
    monthly_limit: int

    @property
    def within_limits(self) -> bool:
        return self.daily_count < self.daily_limit and self.monthly_count < self.monthly_limit


class UsageLedger:
    def __init__(self, usage_dir: Path | str) -> None:
        self.usage_dir = Path(usage_dir)

    def record(self, record: UsageRecord) -> Path:
        self.usage_dir.mkdir(parents=True, exist_ok=True)
        path = self.usage_dir / f"{record.recorded_at[:10]}.jsonl"
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(asdict(record), sort_keys=True) + "\n")
        return path

    def count_for_prefix(self, prefix: str) -> int:
        count = 0
        if not self.usage_dir.exists():
            return count
        for path in self.usage_dir.glob("*.jsonl"):
            if not path.name.startswith(prefix):
                continue
            count += sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        return count

    def summarize(self, limits: UsageLimits, now: datetime | None = None) -> UsageSummary:
        active_now = now or datetime.now(UTC)
        day_prefix = active_now.date().isoformat()
        month_prefix = day_prefix[:7]
        return UsageSummary(
            daily_count=self.count_for_prefix(day_prefix),
            monthly_count=self.count_for_prefix(month_prefix),
            daily_limit=limits.daily_limit,
            monthly_limit=limits.monthly_limit,
        )


def new_usage_record(
    event_id: str,
    provider: str = "deterministic",
    model: str = "level-3-template-v1",
    dry_run: bool = True,
    estimated_input_tokens: int = 0,
    estimated_output_tokens: int = 0,
    now: datetime | None = None,
) -> UsageRecord:
    active_now = now or datetime.now(UTC)
    return UsageRecord(
        recorded_at=active_now.isoformat(),
        event_id=event_id,
        provider=provider,
        model=model,
        dry_run=dry_run,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=estimated_output_tokens,
    )
