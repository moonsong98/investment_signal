# TradingView Alert Templates

Use these JSON bodies in TradingView alerts. Replace `YOUR_SECRET_FROM_ENV` with
the value stored in local `.env` or your deployment secret store. Do not commit
real secrets.

Webhook URL:

```text
https://your-public-url/webhooks/tradingview
```

## Crypto Breakout

Use for BTC, ETH, and SOL alerts. Set `symbol` manually to the canonical
watchlist symbol instead of using `{{ticker}}`.

```json
{
  "secret": "YOUR_SECRET_FROM_ENV",
  "source": "tradingview",
  "symbol": "BTC",
  "asset_type": "crypto",
  "timeframe": "{{interval}}",
  "alert_type": "breakout_20d_high",
  "event_at": "{{time}}",
  "price": {{close}},
  "message": "{{exchange}}:{{ticker}} 20-day high breakout"
}
```

## Crypto Breakdown

```json
{
  "secret": "YOUR_SECRET_FROM_ENV",
  "source": "tradingview",
  "symbol": "BTC",
  "asset_type": "crypto",
  "timeframe": "{{interval}}",
  "alert_type": "support_breakdown",
  "event_at": "{{time}}",
  "price": {{close}},
  "message": "{{exchange}}:{{ticker}} support breakdown"
}
```

## Stock Breakout

```json
{
  "secret": "YOUR_SECRET_FROM_ENV",
  "source": "tradingview",
  "symbol": "{{ticker}}",
  "asset_type": "stock",
  "timeframe": "{{interval}}",
  "alert_type": "breakout_20d_high",
  "event_at": "{{time}}",
  "price": {{close}},
  "message": "{{exchange}}:{{ticker}} 20-day high breakout"
}
```

## 200-Day Moving Average Breakdown

```json
{
  "secret": "YOUR_SECRET_FROM_ENV",
  "source": "tradingview",
  "symbol": "SPY",
  "asset_type": "etf",
  "timeframe": "{{interval}}",
  "alert_type": "breakdown_200d_ma",
  "event_at": "{{time}}",
  "price": {{close}},
  "message": "{{exchange}}:{{ticker}} broke below the 200-day moving average"
}
```

## Index Drawdown

```json
{
  "secret": "YOUR_SECRET_FROM_ENV",
  "source": "tradingview",
  "symbol": "{{ticker}}",
  "asset_type": "index",
  "timeframe": "{{interval}}",
  "alert_type": "major_index_drawdown",
  "event_at": "{{time}}",
  "price": {{close}},
  "message": "{{exchange}}:{{ticker}} major drawdown"
}
```

## Local Safe Test

This script reads `.env`, injects the webhook secret into a sample payload, and
does not print the secret:

```bash
uv run python scripts/send_sample_alert.py
```

To test a Cloudflare Tunnel URL:

```bash
uv run python scripts/send_sample_alert.py \
  --url https://your-tunnel.trycloudflare.com/webhooks/tradingview
```
