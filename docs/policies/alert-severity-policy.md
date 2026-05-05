# Alert Severity Policy

## Level 1: Log Only

Examples:
- Minor RSI overbought or oversold signal
- Small price move
- General watchlist update

Processing:
- Save structured event log
- No Telegram notification
- No LLM analysis

## Level 2: Telegram Notification

Examples:
- 20-day high breakout
- 200-day moving average breakdown
- Volume spike
- Major index drawdown
- FX spike
- Earnings date reminder
- Major filing detected

Processing:
- Send short Telegram notification
- Save structured event log
- Optionally show on dashboard

## Level 3: LLM Analysis

Examples:
- Chart signal and fundamental change happen together
- Earnings shock
- Major guidance change
- Possible long-term thesis damage
- Important news for a watched company
- Sharp selloff plus support breakdown
- Major macro regime shift

Processing:
- Send detailed Telegram notification
- Run LLM analysis
- Draft Markdown research note
- Save dashboard-ready output
