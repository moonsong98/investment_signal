"""Watchlist loading and lookup helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_watchlist(path: Path | str) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return json.loads(source.read_text(encoding="utf-8"))


def find_watchlist_item(
    symbol: str,
    watchlist: list[dict[str, Any]],
) -> dict[str, Any] | None:
    normalized = symbol.strip().upper()
    for item in watchlist:
        if str(item.get("symbol", "")).strip().upper() == normalized:
            return item
        aliases = {str(alias).strip().upper() for alias in item.get("aliases", [])}
        if normalized in aliases:
            return item
    return None
