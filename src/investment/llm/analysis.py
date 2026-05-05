"""LLM analysis policy and deterministic fallback analyzer.

This module intentionally does not call an external LLM API yet. It defines the
gate and output shape that real LLM calls must follow later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AnalysisPolicy:
    enabled: bool = True
    dry_run: bool = True
    max_events_per_run: int = 5


@dataclass(frozen=True)
class EventAnalysis:
    eligible: bool
    llm_used: bool
    summary: str
    risk_points: list[str]
    follow_up_questions: list[str]
    skipped_reason: str | None = None


def is_analysis_eligible(event: dict[str, Any], policy: AnalysisPolicy) -> bool:
    return policy.enabled and event.get("severity") == "level_3"


def analyze_event(event: dict[str, Any], policy: AnalysisPolicy | None = None) -> EventAnalysis:
    active_policy = policy or AnalysisPolicy()
    if not active_policy.enabled:
        return EventAnalysis(
            eligible=False,
            llm_used=False,
            summary="Analysis is disabled by policy.",
            risk_points=[],
            follow_up_questions=[],
            skipped_reason="analysis_disabled",
        )
    if event.get("severity") != "level_3":
        return EventAnalysis(
            eligible=False,
            llm_used=False,
            summary="Event severity is below the analysis threshold.",
            risk_points=[],
            follow_up_questions=[],
            skipped_reason="severity_below_level_3",
        )

    symbol = str(event.get("symbol", "UNKNOWN"))
    alert_type = str(event.get("alert_type", "unknown_event"))
    asset_type = str(event.get("asset_type", "unknown_asset"))
    timeframe = str(event.get("timeframe", "unknown_timeframe"))
    payload = event.get("payload") or {}
    message = str(payload.get("message", "No message provided."))

    return EventAnalysis(
        eligible=True,
        llm_used=False,
        summary=(
            f"{symbol} produced a Level 3 {alert_type} alert on {timeframe}. "
            f"Treat it as a research escalation for {asset_type}, not as a trade decision. "
            f"Event message: {message}"
        ),
        risk_points=[
            "Confirm whether the signal is supported by independent market, news, or fundamental evidence.",
            "Check whether the event changes the long-term thesis or only reflects short-term volatility.",
            "Review related assets and liquidity conditions before changing any plan.",
        ],
        follow_up_questions=[
            "What evidence would confirm or invalidate the current thesis?",
            "Is this event isolated, or does it align with broader market signals?",
            "What should be reviewed before any human investment decision?",
        ],
    )
