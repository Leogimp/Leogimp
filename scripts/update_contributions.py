import json
import urllib.request
from datetime import date, datetime

CELL = 11
STEP = 13.5
LEFT = 30
TOP = 20
RX = 2

DARK = {
    "c0": "#1b2129", "c1": "#4d4d4d", "c2": "#8c8c8c", "c3": "#c9c9c9", "c4": "#ffffff",
    "m": "#ffffff", "text": "#8b949e",
}
LIGHT = {
    "c0": "#e5e7eb", "c1": "#b3b3b3", "c2": "#808080", "c3": "#3f3f3f", "c4": "#000000",
    "m": "#000000", "text": "#6b7280",
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch_days(username: str):
    url = f"https://github-contributions-api.jogruber.de/v4/{username}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.load(resp)
    days = sorted(data["contributions"], key=lambda d: d["date"])[-365:]
    return [(datetime.strptime(d["date"], "%Y-%m-%d").date(), int(d["level"])) for d in days]


def build_svg(days):
    first = days[0][0]
    pad = (first.weekday() + 1) % 7  # Sunday = 0, like GitHub
    cols = -(-(pad + len(days)) // 7)
    width = LEFT + cols * STEP + 4
    height = TOP + 7 * STEP + 4

    rects, labels, month_x = [], [], {}
    for i, (d, level) in enumerate(days):
        col, row = (pad + i) // 7, (pad + i) % 7
        if row == 0 and d.strftime("%Y%m") not in month_x:
            month_x[d.strftime("%Y%m")] = LEFT + col * STEP
        x = round(LEFT + col * STEP, 1)
        y = round(TOP + row * STEP, 1)
        rects.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RX}" class="c{level}"/>')

    prev_x = -999
    for key in sorted(month_x):
        x, m = month_x[key], int(key[4:6])
        if x - prev_x >= 36:
            labels.append(f'<text x="{x}" y="13" class="m">{MONTHS[m - 1]}</text>')
            prev_x = x
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        labels.append(f'<text x="0" y="{round(TOP + row * STEP + 9, 1)}" class="w">{name}</text>')

    def css(c):
        return (f"text{{font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-size:9px;fill:{c['text']}}}\n"
                f".m{{fill:{c['m']};font-size:9.5px}}\n"
                + " ".join(f".{k}{{fill:{v}}}" for k, v in c.items() if k.startswith("c")))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
        "<style>\n"
        f"{css(DARK)}\n"
        "@media (prefers-color-scheme:light){\n"
        f"{css(LIGHT)}\n"
        "}\n"
        "</style>\n"
        + "\n".join(labels) + "\n" + "\n".join(rects) + "\n</svg>"
    )


def main():
    days = fetch_days("Leogimp")
    svg = build_svg(days)
    with open("contributions.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"contributions.svg written ({len(svg)} bytes, {len(days)} days)")


if __name__ == "__main__":
    main()
