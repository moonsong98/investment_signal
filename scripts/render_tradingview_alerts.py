from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "data/tradingview/recommended_alerts.json"
SECRET_PLACEHOLDER = "YOUR_SECRET_FROM_ENV"


def load_catalog(path: Path | str = DEFAULT_CATALOG) -> list[dict[str, Any]]:
    catalog = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(catalog, list):
        raise ValueError("TradingView alert catalog must be a JSON list")
    return catalog


def render_alert_message(alert: dict[str, Any], secret_placeholder: str = SECRET_PLACEHOLDER) -> str:
    required = {"symbol", "asset_type", "timeframe", "alert_type", "message"}
    missing = sorted(required - alert.keys())
    if missing:
        raise ValueError(f"missing alert fields: {', '.join(missing)}")

    payload = {
        "secret": secret_placeholder,
        "source": "tradingview",
        "symbol": str(alert["symbol"]).upper(),
        "asset_type": alert["asset_type"],
        "timeframe": alert["timeframe"],
        "alert_type": alert["alert_type"],
        "event_at": "{{time}}",
        "price": "__TRADINGVIEW_CLOSE__",
        "message": alert["message"],
    }
    rendered = json.dumps(payload, indent=2)
    return rendered.replace('"__TRADINGVIEW_CLOSE__"', "{{close}}")


def filter_catalog(
    catalog: list[dict[str, Any]],
    alert_id: str | None = None,
    symbol: str | None = None,
) -> list[dict[str, Any]]:
    filtered = catalog
    if alert_id is not None:
        filtered = [alert for alert in filtered if alert.get("id") == alert_id]
    if symbol is not None:
        normalized = symbol.strip().upper()
        filtered = [
            alert
            for alert in filtered
            if str(alert.get("symbol", "")).strip().upper() == normalized
        ]
    return filtered


def render_catalog(
    catalog: list[dict[str, Any]],
    alert_id: str | None = None,
    symbol: str | None = None,
) -> str:
    alerts = filter_catalog(catalog, alert_id=alert_id, symbol=symbol)
    blocks = []
    for alert in alerts:
        title = str(alert.get("id", "unnamed_alert"))
        blocks.append(f"# {title}\n{render_alert_message(alert)}")
    return "\n\n".join(blocks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render copy-safe TradingView webhook alert messages.",
    )
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG),
        help="Alert catalog JSON path.",
    )
    parser.add_argument(
        "--id",
        dest="alert_id",
        help="Render only one alert by catalog id.",
    )
    parser.add_argument(
        "--symbol",
        help="Render only alerts for one canonical symbol.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog = load_catalog(args.catalog)
    rendered = render_catalog(catalog, alert_id=args.alert_id, symbol=args.symbol)
    if not rendered:
        print("No matching TradingView alerts found.", file=sys.stderr)
        return 1
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
