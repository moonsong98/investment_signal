"""TradingView alert payload validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import re
from typing import Any

from investment.models import AssetType, EventSource, Severity
from investment.rules import classify_alert_type


REQUIRED_FIELDS = {
    "secret",
    "source",
    "symbol",
    "asset_type",
    "timeframe",
    "alert_type",
    "event_at",
    "message",
}

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9:._/-]{1,32}$")
TIMEFRAME_PATTERN = re.compile(r"^[A-Za-z0-9]{1,16}$")
ALERT_TYPE_PATTERN = re.compile(r"^[a-z0-9_]{1,64}$")
MAX_MESSAGE_LENGTH = 500


class AlertValidationError(ValueError):
    """Raised when an alert payload is malformed or unauthorized."""


@dataclass(frozen=True)
class TradingViewAlert:
    source: EventSource
    symbol: str
    asset_type: AssetType
    timeframe: str
    alert_type: str
    event_at: datetime
    message: str
    price: float | None
    severity: Severity
    dedupe_key: str


def build_dedupe_key(
    source: EventSource,
    symbol: str,
    timeframe: str,
    alert_type: str,
    event_at: datetime,
) -> str:
    raw = "|".join(
        [
            source.value,
            symbol.upper(),
            timeframe,
            alert_type.lower(),
            event_at.isoformat(),
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def parse_event_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise AlertValidationError("event_at must be an ISO timestamp string")
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise AlertValidationError("event_at must be a valid ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise AlertValidationError("event_at must include a timezone")
    return parsed


def validate_symbol(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise AlertValidationError("symbol must not be empty")
    if not SYMBOL_PATTERN.fullmatch(normalized):
        raise AlertValidationError("symbol contains unsupported characters or is too long")
    return normalized


def validate_timeframe(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise AlertValidationError("timeframe must not be empty")
    if not TIMEFRAME_PATTERN.fullmatch(normalized):
        raise AlertValidationError("timeframe contains unsupported characters or is too long")
    return normalized


def validate_alert_type(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        raise AlertValidationError("alert_type must not be empty")
    if not ALERT_TYPE_PATTERN.fullmatch(normalized):
        raise AlertValidationError("alert_type contains unsupported characters or is too long")
    return normalized


def validate_message(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise AlertValidationError("message must not be empty")
    if len(normalized) > MAX_MESSAGE_LENGTH:
        raise AlertValidationError("message is too long")
    return normalized


def validate_tradingview_payload(
    payload: dict[str, Any],
    expected_secret: str,
) -> TradingViewAlert:
    missing = sorted(REQUIRED_FIELDS - payload.keys())
    if missing:
        raise AlertValidationError(f"missing required fields: {', '.join(missing)}")

    if payload["secret"] != expected_secret:
        raise AlertValidationError("invalid webhook secret")

    try:
        source = EventSource(payload["source"])
    except ValueError as exc:
        raise AlertValidationError("source must be tradingview") from exc
    if source is not EventSource.TRADINGVIEW:
        raise AlertValidationError("source must be tradingview")

    try:
        asset_type = AssetType(payload["asset_type"])
    except ValueError as exc:
        raise AlertValidationError("asset_type is not supported") from exc

    symbol = validate_symbol(str(payload["symbol"]))
    timeframe = validate_timeframe(str(payload["timeframe"]))
    alert_type = validate_alert_type(str(payload["alert_type"]))
    message = validate_message(str(payload["message"]))

    price = payload.get("price")
    if price is not None:
        try:
            price = float(price)
        except (TypeError, ValueError) as exc:
            raise AlertValidationError("price must be numeric when provided") from exc

    event_at = parse_event_time(payload["event_at"])
    return TradingViewAlert(
        source=source,
        symbol=symbol,
        asset_type=asset_type,
        timeframe=timeframe,
        alert_type=alert_type,
        event_at=event_at,
        message=message,
        price=price,
        severity=classify_alert_type(alert_type),
        dedupe_key=build_dedupe_key(source, symbol, timeframe, alert_type, event_at),
    )
