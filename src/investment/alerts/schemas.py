"""TradingView alert payload validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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

    symbol = str(payload["symbol"]).strip().upper()
    timeframe = str(payload["timeframe"]).strip()
    alert_type = str(payload["alert_type"]).strip().lower()
    message = str(payload["message"]).strip()
    if not symbol:
        raise AlertValidationError("symbol must not be empty")
    if not timeframe:
        raise AlertValidationError("timeframe must not be empty")
    if not alert_type:
        raise AlertValidationError("alert_type must not be empty")
    if not message:
        raise AlertValidationError("message must not be empty")

    price = payload.get("price")
    if price is not None:
        try:
            price = float(price)
        except (TypeError, ValueError) as exc:
            raise AlertValidationError("price must be numeric when provided") from exc

    return TradingViewAlert(
        source=source,
        symbol=symbol,
        asset_type=asset_type,
        timeframe=timeframe,
        alert_type=alert_type,
        event_at=parse_event_time(payload["event_at"]),
        message=message,
        price=price,
        severity=classify_alert_type(alert_type),
    )
