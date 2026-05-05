"""Generate human-review research note drafts from Level 3 events."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NOTE_HEADER = "Generated Research Note Draft"


@dataclass(frozen=True)
class GeneratedNote:
    event_id: str
    path: Path
    title: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "event"


def iter_event_logs(event_dir: Path | str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for path in sorted(Path(event_dir).glob("*.jsonl")):
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if raw_line.strip():
                events.append(json.loads(raw_line))
    return events


def is_level_3_event(event: dict[str, Any]) -> bool:
    return event.get("severity") == "level_3"


def note_filename(event: dict[str, Any]) -> str:
    event_at = str(event.get("event_at", "unknown-date"))[:10]
    symbol = slugify(str(event.get("symbol", "unknown")))
    alert_type = slugify(str(event.get("alert_type", "event")))
    event_id = slugify(str(event.get("event_id", "")))[:8]
    suffix = f"-{event_id}" if event_id else ""
    return f"{event_at}-{symbol}-{alert_type}{suffix}.md"


def render_note(event: dict[str, Any]) -> str:
    payload = event.get("payload") or {}
    symbol = str(event.get("symbol", "UNKNOWN"))
    alert_type = str(event.get("alert_type", "unknown_event"))
    severity = str(event.get("severity", "unknown"))
    event_at = str(event.get("event_at", ""))
    received_at = str(event.get("received_at", ""))
    asset_type = str(event.get("asset_type", ""))
    timeframe = str(event.get("timeframe", ""))
    message = str(payload.get("message", ""))
    price = payload.get("price")

    price_line = f"\n- Price: {price}" if price is not None else ""
    return f"""# {NOTE_HEADER}: {symbol} {alert_type}

Status: draft
Human Review: required
LLM Used: false

## Event Summary

- Symbol: {symbol}
- Asset Type: {asset_type}
- Alert Type: {alert_type}
- Severity: {severity}
- Timeframe: {timeframe}
- Event Time: {event_at}
- Received Time: {received_at}{price_line}
- Message: {message}

## Initial Interpretation

This Level 3 event may indicate a material change in market behavior, thesis
quality, or risk conditions. Treat this note as a research prompt, not as a
trading decision.

## Risk Review

- Confirm whether the signal is driven by price action, fundamentals, macro
  conditions, or news.
- Check whether the event changes the long-term investment thesis.
- Check whether the event is isolated or confirmed by related assets and volume.
- Do not place live orders from this note.

## Follow-Up Questions

- What changed versus the prior thesis?
- Is this signal temporary noise or a thesis-relevant event?
- What external sources should be checked before making any decision?
- Should this item remain on the watchlist, be escalated for deeper research, or
  be ignored after review?
"""


def generate_research_note_for_event(
    event: dict[str, Any],
    output_dir: Path | str,
) -> GeneratedNote | None:
    if not is_level_3_event(event):
        return None

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    note_path = output_path / note_filename(event)
    note_path.write_text(render_note(event), encoding="utf-8")
    return GeneratedNote(
        event_id=str(event.get("event_id", "")),
        path=note_path,
        title=f"{event.get('symbol', 'UNKNOWN')} {event.get('alert_type', 'event')}",
    )


def generate_research_notes(
    event_dir: Path | str,
    output_dir: Path | str,
) -> list[GeneratedNote]:
    notes: list[GeneratedNote] = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for event in iter_event_logs(event_dir):
        note = generate_research_note_for_event(event, output_path)
        if note is not None:
            notes.append(note)
    return notes
