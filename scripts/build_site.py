from __future__ import annotations

import json
import struct
import sys
import zlib
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
CONTENT_DIR = ROOT / "content"
DATA_DIR = ROOT / "data"
SRC_DIR = ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from investment.rules import classify_alert_type  # noqa: E402


CONTENT_SECTIONS = {
    "journal": "Trading Journal",
    "research": "Research Notes",
    "macro": "Macro Notes",
    "strategy": "Strategy Notes",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    html: list[str] = []
    in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if in_list:
                html.append("</ul>")
                in_list = False
            continue

        if line.startswith("# "):
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(f"<h1>{escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(f"<h2>{escape(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{escape(line[2:])}</li>")
        else:
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(f"<p>{escape(line)}</p>")

    if in_list:
        html.append("</ul>")

    return "\n".join(html)


def page_shell(title: str, body: str) -> str:
    nav = "".join(
        f'<a href="{section}.html">{label}</a>'
        for section, label in CONTENT_SECTIONS.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <header>
    <a class="brand" href="index.html">Investment Research Lab</a>
    <nav>{nav}<a href="events.html">Events</a></nav>
  </header>
  <main>
    {body}
  </main>
</body>
</html>
"""


def list_markdown_files(section: str) -> list[Path]:
    path = CONTENT_DIR / section
    return sorted(file for file in path.glob("*.md") if file.is_file())


def build_index() -> None:
    cards = "".join(
        f"""
        <article class="card">
          <h2>{escape(label)}</h2>
          <p>Open the latest {escape(label.lower())}.</p>
          <a href="{section}.html">View</a>
        </article>
        """
        for section, label in CONTENT_SECTIONS.items()
    )
    body = f"""
    <section class="hero">
      <div>
        <h1>Personal Investment Research Lab</h1>
        <p>Static research workspace for journals, strategy notes, macro notes,
        company research, and redacted alert logs.</p>
      </div>
      <img src="assets/market-overview.png" alt="Sample market overview line chart">
    </section>
    <section class="grid">{cards}
      <article class="card">
        <h2>Event Logs</h2>
        <p>Review sample TradingView alerts and severity classification.</p>
        <a href="events.html">View</a>
      </article>
    </section>
    """
    write_text(SITE_DIR / "index.html", page_shell("Investment Research Lab", body))


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int]]) -> None:
    raw_rows = []
    for y in range(height):
        start = y * width
        row = pixels[start : start + width]
        raw_rows.append(b"\x00" + b"".join(bytes(pixel) for pixel in row))

    data = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            png_chunk(b"IDAT", zlib.compress(b"".join(raw_rows))),
            png_chunk(b"IEND", b""),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def build_market_overview_image() -> None:
    width = 960
    height = 360
    bg = (247, 248, 245)
    grid = (217, 221, 212)
    ink = (31, 41, 51)
    green = (31, 118, 100)
    amber = (154, 91, 0)
    red = (154, 41, 48)
    pixels = [bg for _ in range(width * height)]

    def set_pixel(x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            pixels[y * width + x] = color

    def draw_line(points: list[tuple[int, int]], color: tuple[int, int, int]) -> None:
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            dx = abs(x2 - x1)
            dy = -abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx + dy
            x, y = x1, y1
            while True:
                for ox in (-1, 0, 1):
                    for oy in (-1, 0, 1):
                        set_pixel(x + ox, y + oy, color)
                if x == x2 and y == y2:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x += sx
                if e2 <= dx:
                    err += dx
                    y += sy

    for x in range(64, width - 48):
        set_pixel(x, height - 64, ink)
    for y in range(48, height - 64):
        set_pixel(64, y, ink)
    for y in range(72, height - 64, 48):
        for x in range(65, width - 48):
            set_pixel(x, y, grid)

    base_points = [(80, 250), (180, 232), (280, 238), (380, 198), (480, 178), (580, 154), (680, 166), (780, 128), (900, 112)]
    macro_points = [(80, 198), (180, 206), (280, 190), (380, 202), (480, 186), (580, 192), (680, 176), (780, 184), (900, 168)]
    risk_points = [(80, 276), (180, 262), (280, 284), (380, 252), (480, 272), (580, 246), (680, 258), (780, 224), (900, 232)]
    draw_line(base_points, green)
    draw_line(macro_points, amber)
    draw_line(risk_points, red)

    write_png(SITE_DIR / "assets/market-overview.png", width, height, pixels)


def build_section(section: str, title: str) -> None:
    files = list_markdown_files(section)
    if not files:
        body = f"<h1>{escape(title)}</h1><p>No notes yet.</p>"
    else:
        articles = "\n".join(
            f'<article class="note">{markdown_to_html(read_text(file))}</article>'
            for file in files
        )
        body = f"<h1>{escape(title)}</h1>{articles}"
    write_text(SITE_DIR / f"{section}.html", page_shell(title, body))


def load_sample_alerts() -> list[dict[str, Any]]:
    alerts = []
    for path in sorted((DATA_DIR / "samples").glob("tradingview_alert_*.json")):
        payload = json.loads(read_text(path))
        severity = classify_alert_type(str(payload["alert_type"]))
        alerts.append(
            {
                "file": path.name,
                "symbol": payload["symbol"],
                "alert_type": payload["alert_type"],
                "timeframe": payload["timeframe"],
                "event_at": payload["event_at"],
                "severity": severity.value,
                "message": payload["message"],
            }
        )
    return alerts


def build_events() -> None:
    rows = []
    for alert in load_sample_alerts():
        rows.append(
            "<tr>"
            f"<td>{escape(alert['event_at'])}</td>"
            f"<td>{escape(alert['symbol'])}</td>"
            f"<td>{escape(alert['alert_type'])}</td>"
            f"<td>{escape(alert['timeframe'])}</td>"
            f"<td><span class=\"severity {escape(alert['severity'])}\">{escape(alert['severity'])}</span></td>"
            f"<td>{escape(alert['message'])}</td>"
            "</tr>"
        )

    body = f"""
    <h1>Sample Alert Events</h1>
    <p>These events are generated from local sample payloads. Secrets and raw
    payloads are not published to the static site.</p>
    <table>
      <thead>
        <tr><th>Event Time</th><th>Symbol</th><th>Alert</th><th>Timeframe</th><th>Severity</th><th>Message</th></tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """
    write_text(SITE_DIR / "events.html", page_shell("Sample Alert Events", body))
    write_text(SITE_DIR / "events.json", json.dumps(load_sample_alerts(), indent=2))


def build_styles() -> None:
    css = """
:root {
  color-scheme: light;
  --bg: #f7f8f5;
  --surface: #ffffff;
  --ink: #1f2933;
  --muted: #5c6670;
  --line: #d9ddd4;
  --accent: #1f7664;
  --warn: #9a5b00;
  --danger: #9a2930;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.6;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 18px 32px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
}

a {
  color: var(--accent);
  text-decoration: none;
}

.brand {
  color: var(--ink);
  font-weight: 700;
}

nav {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

main {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 36px 0 64px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 460px);
  gap: 28px;
  align-items: center;
  padding: 32px 0;
  border-bottom: 1px solid var(--line);
}

.hero h1 {
  margin: 0 0 12px;
  font-size: 36px;
}

.hero p,
p {
  color: var(--muted);
}

.hero img {
  display: block;
  width: 100%;
  height: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.card,
.note {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
}

.note {
  margin: 16px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: var(--surface);
  border: 1px solid var(--line);
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}

th {
  font-size: 13px;
  color: var(--muted);
}

.severity {
  display: inline-block;
  min-width: 72px;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 700;
  text-align: center;
}

.level_1 {
  background: #e8ece6;
  color: #405047;
}

.level_2 {
  background: #fff1d6;
  color: var(--warn);
}

.level_3 {
  background: #ffe1e4;
  color: var(--danger);
}

@media (max-width: 720px) {
  header {
    align-items: flex-start;
    flex-direction: column;
    padding: 16px;
  }

  .hero h1 {
    font-size: 28px;
  }

  .hero {
    grid-template-columns: 1fr;
  }

  table {
    display: block;
    overflow-x: auto;
  }
}
"""
    write_text(SITE_DIR / "assets/styles.css", css.strip() + "\n")


def build_site() -> None:
    build_market_overview_image()
    build_styles()
    build_index()
    for section, title in CONTENT_SECTIONS.items():
        build_section(section, title)
    build_events()


if __name__ == "__main__":
    build_site()
    print(f"Built static site at {SITE_DIR}")
