# TradingView Setup

This guide configures TradingView to send alerts into the local FastAPI webhook.
The webhook only logs, classifies, notifies, and creates research drafts. It does
not place orders.

## Prerequisites

1. Start the local webhook service:

```bash
docker compose up -d --build
```

2. Confirm the local service is healthy:

```bash
uv run python scripts/ops_status.py
```

3. Expose the local service with an HTTPS tunnel:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Use the HTTPS URL printed by cloudflared as the TradingView webhook base URL.
Temporary `trycloudflare.com` URLs change when the tunnel restarts.

## TradingView Alert Form

In TradingView, open a chart and create an alert.

- Condition: choose the indicator or built-in condition you want to monitor
- Webhook URL: `https://your-tunnel.trycloudflare.com/webhooks/tradingview`
- Message: paste one JSON message from `docs/tradingview-alert-templates.md`
- Expiration: choose a short test window first, then extend after validation
- Notify on app/email: optional; Telegram will be handled by this service

Do not paste the real webhook secret into screenshots, docs, GitHub issues, or
commits.

## Recommended First Alerts

Start with a small set of high-signal alerts:

- `BTC` daily 20-day high breakout
- `BTC` daily 200-day moving average breakdown
- `ETH` daily 20-day high breakout
- `SOL` daily 20-day high breakout
- `SPY` daily major drawdown or 200-day moving average breakdown
- `DXY` daily FX spike or macro regime signal

For crypto alerts, prefer setting `symbol` explicitly to `BTC`, `ETH`, or `SOL`.
The watchlist also includes common aliases such as `BTCUSDT` and
`BINANCE:BTCUSDT`, so research-note context can still be matched when an alert
uses a TradingView exchange ticker.

## Pine Script Starter

Use this optional Pine Script when you want consistent alert conditions across
charts. Add it to the chart, then create one TradingView alert per condition.

```pine
//@version=5
indicator("Investment Research Alerts", overlay=true)

lookbackHigh = input.int(20, "Breakout Lookback", minval=2)
volumeLength = input.int(20, "Volume SMA Length", minval=2)
volumeMultiplier = input.float(2.0, "Volume Spike Multiplier", minval=1.0)
rsiLength = input.int(14, "RSI Length", minval=2)
rsiHigh = input.float(70.0, "RSI High", minval=50.0, maxval=100.0)

sma200 = ta.sma(close, 200)
highestPrior = ta.highest(high[1], lookbackHigh)
volumeSma = ta.sma(volume, volumeLength)
rsi = ta.rsi(close, rsiLength)

breakout20dHigh = close > highestPrior
breakdown200dMa = ta.crossunder(close, sma200)
volumeSpike = volume > volumeSma * volumeMultiplier
rsiOverheated = rsi > rsiHigh

plot(sma200, "200 SMA", color=color.orange)

alertcondition(breakout20dHigh, "20D High Breakout", "breakout_20d_high")
alertcondition(breakdown200dMa, "200D MA Breakdown", "breakdown_200d_ma")
alertcondition(volumeSpike, "Volume Spike", "volume_spike")
alertcondition(rsiOverheated, "RSI Overheated", "rsi_overheated")
```

The Pine alert message is only the condition label. In the TradingView alert
form, paste the full JSON body from `docs/tradingview-alert-templates.md`.

## Local Verification

After creating a TradingView alert, trigger one safe test with a sample payload:

```bash
uv run python scripts/send_sample_alert.py \
  --url https://your-tunnel.trycloudflare.com/webhooks/tradingview \
  --payload data/samples/tradingview_alert_btc_breakout.json
```

Then check local status:

```bash
uv run python scripts/ops_status.py
```

Expected result:

- `health=ok`
- `event_count` increases by one for a new event
- `latest_symbol` matches the tested symbol
- Level 2 and Level 3 events send Telegram when `TELEGRAM_DRY_RUN=false`

If `event_count` does not change, check the FastAPI container logs:

```bash
docker compose logs webhook-api
```
