"""53-week contribution heatmap that fills in on a diagonal wave."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from svgkit import BASE_CSS, GREEN, GREY, LEVELS, esc, style, svg_open, write

ROOT = Path(__file__).resolve().parent.parent
CELL, GAP = 11, 3
PITCH = CELL + GAP
PAD_L, PAD_T = 30, 22
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def build() -> str:
    payload = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    days, stats = payload["days"], payload["stats"]

    first = date.fromisoformat(stats["first_day"])
    last = date.fromisoformat(stats["last_day"])
    # GitHub's grid columns are Sunday-first weeks; back up to that Sunday.
    origin = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = (last - origin).days // 7 + 1

    width = PAD_L + weeks * PITCH + 4
    height = PAD_T + 7 * PITCH + 26

    out = [svg_open(width, height, f"{stats['total']} contributions in the last year")]
    out.append(style(BASE_CSS + f"""
.cell {{ opacity: 0; animation: pop .45s cubic-bezier(.34,1.4,.64,1) forwards; transform-box: fill-box; transform-origin: center; }}
.lbl {{ fill: {GREY}; font-size: 9px; opacity: 0; animation: fade-in .6s ease-out forwards; }}
.cap {{ fill: {GREY}; font-size: 10px; opacity: 0; animation: fade-in .6s ease-out 1.9s forwards; }}
.hot {{ fill: {GREEN}; }}
"""))

    # month ruler
    seen = set()
    for week in range(weeks):
        day = origin + timedelta(days=week * 7)
        key = (day.year, day.month)
        if day.day <= 7 and key not in seen and week < weeks - 1:
            seen.add(key)
            x = PAD_L + week * PITCH
            out.append(f'<text class="lbl" x="{x}" y="{PAD_T - 8}" style="animation-delay:{week * .012:.2f}s">{MONTHS[day.month - 1]}</text>\n')

    for row, label in DAY_LABELS.items():
        y = PAD_T + row * PITCH + CELL - 1
        out.append(f'<text class="lbl" x="0" y="{y}" style="animation-delay:.2s">{label}</text>\n')

    # the grid itself, revealed on a diagonal
    for week in range(weeks):
        for row in range(7):
            day = origin + timedelta(days=week * 7 + row)
            if day < first or day > last:
                continue
            info = days.get(day.isoformat())
            if info is None:
                continue
            level, count = info["level"], info["count"]
            x = PAD_L + week * PITCH
            y = PAD_T + row * PITCH
            delay = week * 0.013 + row * 0.028
            plural = "contribution" if count == 1 else "contributions"
            out.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{LEVELS[level]}" style="animation-delay:{delay:.2f}s">'
                f'<title>{count} {plural} on {esc(day.isoformat())}</title></rect>\n'
            )

    # footer: totals on the left, level legend on the right
    base_y = PAD_T + 7 * PITCH + 15
    busiest = stats["busiest_day"]
    out.append(
        f'<text class="cap" x="0" y="{base_y}">'
        f'<tspan class="hot">{stats["total"]}</tspan> contributions'
        f'<tspan dx="6">·</tspan><tspan dx="6" class="hot">{stats["active_days"]}</tspan> active days'
        f'<tspan dx="6">·</tspan><tspan dx="6">longest streak </tspan><tspan class="hot">{stats["longest_streak"]}</tspan>'
        f'<tspan dx="6">·</tspan><tspan dx="6">peak </tspan><tspan class="hot">{busiest["count"]}</tspan>'
        f'<tspan dx="4">on {esc(busiest["date"])}</tspan></text>\n'
    )

    legend_x = width - 150
    out.append(f'<text class="cap" x="{legend_x}" y="{base_y}">Less</text>\n')
    for i, colour in enumerate(LEVELS):
        out.append(
            f'<rect class="cell" x="{legend_x + 30 + i * PITCH}" y="{base_y - 9}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{colour}" style="animation-delay:{1.9 + i * .07:.2f}s"/>\n'
        )
    out.append(f'<text class="cap" x="{legend_x + 30 + 5 * PITCH + 4}" y="{base_y}">More</text>\n')

    out.append("</svg>\n")
    return "".join(out)


if __name__ == "__main__":
    write(str(ROOT / "assets" / "contrib-heatmap.svg"), build())
