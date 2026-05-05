"""Severity rules for alert events.

The first production versions should stay rule-based. LLM analysis is allowed
only after an event reaches Level 3.
"""

from __future__ import annotations

from investment.models import Severity


LEVEL_3_ALERT_TYPES = {
    "earnings_shock",
    "guidance_cut",
    "guidance_raise_major",
    "thesis_damage",
    "macro_regime_shift",
    "earnings_shock_support_breakdown",
    "fundamental_change_chart_breakdown",
}

LEVEL_2_ALERT_TYPES = {
    "breakout_20d_high",
    "breakdown_200d_ma",
    "volume_spike",
    "major_index_drawdown",
    "fx_spike",
    "earnings_date",
    "major_filing",
    "support_breakdown",
    "resistance_breakout",
}


def classify_alert_type(alert_type: str) -> Severity:
    """Classify a normalized alert type into a notification severity."""

    normalized = alert_type.strip().lower()
    if normalized in LEVEL_3_ALERT_TYPES:
        return Severity.LEVEL_3
    if normalized in LEVEL_2_ALERT_TYPES:
        return Severity.LEVEL_2
    return Severity.LEVEL_1
