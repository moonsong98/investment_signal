from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "http://127.0.0.1:8000/webhooks/tradingview"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_payload(path: Path, secret: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["secret"] = secret
    return payload


def post_payload(url: str, payload: dict[str, Any]) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10) as response:
            return response.status, response.read().decode("utf-8")
    except error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")
    except error.URLError as exc:
        return 0, f"request failed: {exc.reason}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a sample TradingView alert without printing secrets.",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="Webhook URL. Defaults to local FastAPI webhook.",
    )
    parser.add_argument(
        "--payload",
        default=str(ROOT / "data/samples/tradingview_alert_level2.json"),
        help="Sample payload JSON path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(ROOT / ".env")
    secret = os.getenv("TRADINGVIEW_WEBHOOK_SECRET")
    if not secret:
        print("TRADINGVIEW_WEBHOOK_SECRET is not set in the environment or .env", file=sys.stderr)
        return 2

    payload = load_payload(Path(args.payload), secret)
    status_code, response_body = post_payload(args.url, payload)
    print(f"status={status_code}")
    print(response_body)
    return 0 if 200 <= status_code < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
