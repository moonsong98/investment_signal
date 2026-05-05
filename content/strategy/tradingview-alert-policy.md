# TradingView Alert Policy

Status: draft

## Hypothesis

TradingView alerts should reduce monitoring burden by surfacing only meaningful
technical events.

## Signals

- 20-day high breakout
- 200-day moving average breakdown
- Volume spike
- Support or resistance break

## Risk Controls

- Level 1 alerts are log-only.
- Level 2 alerts send Telegram notifications.
- Level 3 alerts can trigger LLM research drafts.
- No alert places live orders.

