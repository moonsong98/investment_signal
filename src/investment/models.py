"""Core data models for the investment research agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class AssetType(StrEnum):
    STOCK = "stock"
    ETF = "etf"
    INDEX = "index"
    FX = "fx"
    COMMODITY = "commodity"
    CRYPTO = "crypto"
    MACRO = "macro"


class EventSource(StrEnum):
    TRADINGVIEW = "tradingview"
    MANUAL = "manual"
    MACRO = "macro"
    FILING = "filing"
    NEWS = "news"


class Severity(StrEnum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"


class JournalDecision(StrEnum):
    WATCH = "watch"
    BUY_CANDIDATE = "buy_candidate"
    SELL_CANDIDATE = "sell_candidate"
    HOLD_REVIEW = "hold_review"
    AVOID = "avoid"


class PaperTradeStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class WatchlistItem:
    symbol: str
    name: str
    asset_type: AssetType
    market: str
    currency: str
    thesis: str
    risk_notes: str
    tags: list[str] = field(default_factory=list)
    priority: int = 3
    active: bool = True


@dataclass(frozen=True)
class AlertEvent:
    event_id: str
    source: EventSource
    received_at: datetime
    event_at: datetime
    symbol: str
    asset_type: AssetType
    timeframe: str
    alert_type: str
    raw_payload: dict[str, Any]
    normalized_payload: dict[str, Any]
    severity: Severity
    rule_matches: list[str]
    dedupe_key: str


@dataclass(frozen=True)
class ResearchNote:
    note_id: str
    created_at: datetime
    title: str
    note_type: str
    symbols: list[str]
    source_event_ids: list[str]
    summary: str
    key_points: list[str]
    risks: list[str]
    open_questions: list[str]
    llm_used: bool
    human_review_status: str = "draft"


@dataclass(frozen=True)
class TradingJournalEntry:
    entry_id: str
    created_at: datetime
    symbols: list[str]
    thesis: str
    decision: JournalDecision
    evidence: list[str]
    risk_review: str
    follow_up_date: str | None
    human_notes: str


@dataclass(frozen=True)
class PaperTrade:
    trade_id: str
    strategy_id: str
    symbol: str
    side: str
    quantity: float
    entry_time: datetime
    entry_price: float
    exit_time: datetime | None
    exit_price: float | None
    status: PaperTradeStatus
    stop_loss: float | None
    take_profit: float | None
    max_loss_limit: float
    reason: str
    linked_event_ids: list[str] = field(default_factory=list)
