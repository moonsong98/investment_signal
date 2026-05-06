from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
SCRIPTS_DIR = ROOT / "scripts"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from investment.models import AssetType, Severity  # noqa: E402
from investment.rules import classify_alert_type  # noqa: E402
from investment.watchlist import find_watchlist_item, load_watchlist  # noqa: E402
from render_tradingview_alerts import DEFAULT_CATALOG, load_catalog, render_alert_message  # noqa: E402


def validate_catalog(catalog_path: Path = DEFAULT_CATALOG) -> list[str]:
    errors: list[str] = []
    catalog = load_catalog(catalog_path)
    watchlist = load_watchlist(ROOT / "data/watchlists/watchlist.example.json")
    ids: set[str] = set()

    for index, alert in enumerate(catalog):
        prefix = str(alert.get("id") or f"alert[{index}]")
        alert_id = str(alert.get("id", "")).strip()
        if not alert_id:
            errors.append(f"{prefix}: missing id")
        elif alert_id in ids:
            errors.append(f"{prefix}: duplicate id")
        ids.add(alert_id)

        symbol = str(alert.get("symbol", "")).strip().upper()
        if not find_watchlist_item(symbol, watchlist):
            errors.append(f"{prefix}: symbol is not in watchlist: {symbol}")

        try:
            AssetType(str(alert.get("asset_type", "")))
        except ValueError:
            errors.append(f"{prefix}: unsupported asset_type: {alert.get('asset_type')}")

        severity = classify_alert_type(str(alert.get("alert_type", "")))
        if severity is Severity.LEVEL_1:
            errors.append(f"{prefix}: recommended alert must not classify as level_1")

        try:
            rendered = render_alert_message(alert)
        except ValueError as exc:
            errors.append(f"{prefix}: {exc}")
        else:
            if "YOUR_SECRET_FROM_ENV" not in rendered:
                errors.append(f"{prefix}: rendered message is missing secret placeholder")
            if "{{close}}" not in rendered:
                errors.append(f"{prefix}: rendered message is missing TradingView close placeholder")

    return errors


def main() -> int:
    errors = validate_catalog()
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("TradingView catalog OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
