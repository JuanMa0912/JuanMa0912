"""The two data-driven panels: a neofetch-style info card and a language bar."""

from __future__ import annotations

import json
from pathlib import Path

from svgkit import (BASE_CSS, BLUE, GREEN, GREY, LINE, ORANGE, PANEL, PINK,
                    PURPLE, esc, style, svg_open, write)

ROOT = Path(__file__).resolve().parent.parent

# Linguist colours, with the near-black ones lifted so they survive dark mode.
LANG_COLOURS = {
    "TypeScript": "#3aa0f5", "JavaScript": "#e3c22c", "Python": "#4b8bbe",
    "Jupyter Notebook": "#f0652f", "Shell": "#89e051", "PowerShell": "#4b7bbd",
    "PLpgSQL": "#5b93c9", "HTML": "#e34c26", "CSS": "#a37acc", "Java": "#c07a35",
    "C++": "#f34b7d", "C": "#8f9cad", "Go": "#00add8", "Rust": "#e0a06a",
    "Dockerfile": "#5aa9d6", "Makefile": "#7ec699", "SQL": "#e38c00",
}
FALLBACK = [GREEN, BLUE, PURPLE, ORANGE, PINK]


def colour_for(name: str, index: int) -> str:
    return LANG_COLOURS.get(name, FALLBACK[index % len(FALLBACK)])


# --------------------------------------------------------------------------- #

def info_card() -> str:
    contrib = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    langs = json.loads((ROOT / "data" / "languages.json").read_text(encoding="utf-8"))
    stats = contrib["stats"]
    top = langs["languages"][0]["name"] if langs["languages"] else "-"

    rows = [
        ("host", "server232 · WSL2 Ubuntu 24.04 · Windows 11"),
        ("shell", "bash · pwsh · ssh -o BatchMode=yes"),
        ("role", "Electronic Engineer · M.Sc. cand. AI & Data Science"),
        ("focus", "AgentOps → LLMOps → MLOps"),
        ("doing", "agents that operate pipelines without breaking them"),
        ("lang", f"{top} · Python · TypeScript · SQL"),
        ("repos", f'{langs["repos"]} public · {langs["stars"]} star' + ("s" if langs["stars"] != 1 else "")),
        ("uptime", f'{stats["total"]} contributions · {stats["active_days"]} active days'),
        ("policy", "read-only by default · approval-gated writes"),
        ("locale", "Cali, Colombia · UTC-5"),
    ]

    width, top_pad, line_h = 520, 46, 21
    height = top_pad + len(rows) * line_h + 52
    key_w = max(len(k) for k, _ in rows)

    out = [svg_open(width, height, "profile info card")]
    out.append(style(BASE_CSS + f"""
.row {{ opacity: 0; animation: fade-up .5s ease-out forwards; }}
.k {{ fill: {GREEN}; font-size: 12px; font-weight: 600; }}
.v {{ fill: {GREY}; font-size: 12px; }}
.host {{ fill: {BLUE}; font-size: 13px; font-weight: 700; }}
.at {{ fill: {GREY}; }}
.sw {{ opacity: 0; animation: pop .4s ease-out forwards; transform-box: fill-box; transform-origin: center; }}
"""))
    out.append(f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" fill="{PANEL}" stroke="{LINE}"/>\n')

    out.append(f'<text class="row host" x="20" y="27" style="animation-delay:.05s">juanma<tspan class="at">@</tspan>github<tspan class="at" dx="8">~</tspan></text>\n')
    out.append(f'<line x1="20" y1="35" x2="{width - 20}" y2="35" stroke="{LINE}"/>\n')

    for i, (key, value) in enumerate(rows):
        y = top_pad + i * line_h
        pad = " " * (key_w - len(key))
        out.append(
            f'<text class="row" x="20" y="{y}" style="animation-delay:{.15 + i * .07:.2f}s">'
            f'<tspan class="k">{esc(key)}</tspan><tspan class="v">{pad}  {esc(value)}</tspan></text>\n'
        )

    # neofetch's signature colour strip
    swatch_y = top_pad + len(rows) * line_h + 8
    palette = [GREEN, BLUE, PURPLE, ORANGE, PINK, "#39d353", "#4493f8", GREY]
    for i, colour in enumerate(palette):
        out.append(
            f'<rect class="sw" x="{20 + i * 26}" y="{swatch_y}" width="20" height="12" rx="3" fill="{colour}" '
            f'style="animation-delay:{.9 + i * .06:.2f}s"/>\n'
        )
    out.append(
        f'<text class="row v" x="{width - 20}" y="{swatch_y + 11}" text-anchor="end" font-size="10" '
        f'style="animation-delay:1.4s">generated {esc(contrib["generated"])}</text>\n'
    )
    out.append("</svg>\n")
    return "".join(out)


# --------------------------------------------------------------------------- #

def lang_bars(top_n: int = 6) -> str:
    data = json.loads((ROOT / "data" / "languages.json").read_text(encoding="utf-8"))
    langs = [l for l in data["languages"] if l["share"] >= 0.005][:top_n]
    rest = 1.0 - sum(l["share"] for l in langs)
    if rest > 0.005:
        langs.append({"name": "Other", "share": rest, "repos": 0})

    width, bar_w, bar_h = 520, 480, 14
    bar_x, bar_y = 20, 56
    cols, col_w, row_h = 2, 240, 22
    rows = (len(langs) + cols - 1) // cols
    height = bar_y + bar_h + 22 + rows * row_h + 20

    out = [svg_open(width, height, "languages by repository")]
    out.append(style(BASE_CSS + f"""
.t {{ fill: {BLUE}; font-size: 13px; font-weight: 700; opacity: 0; animation: fade-in .5s ease-out forwards; }}
.sub {{ fill: {GREY}; font-size: 10px; opacity: 0; animation: fade-in .5s ease-out .2s forwards; }}
.leg {{ opacity: 0; animation: fade-up .45s ease-out forwards; }}
.n {{ fill: {GREY}; font-size: 11.5px; }}
.p {{ font-size: 11.5px; font-weight: 600; }}
#wipe rect {{ animation: wipe 1.4s cubic-bezier(.22,1,.36,1) .25s backwards; }}
@keyframes wipe {{ from {{ width: 0; }} to {{ width: {bar_w}px; }} }}
"""))
    out.append(f'<clipPath id="wipe"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="7"/></clipPath>\n')

    out.append(f'<text class="t" x="20" y="26">languages</text>\n')
    out.append(
        f'<text class="sub" x="20" y="42">weighted per repository — each repo counts once, '
        f'split by its own byte mix ({data["repos_with_code"]} repos)</text>\n'
    )

    out.append(f'<g clip-path="url(#wipe)">\n')
    cursor = float(bar_x)
    for i, lang in enumerate(langs):
        seg = lang["share"] * bar_w
        colour = GREY if lang["name"] == "Other" else colour_for(lang["name"], i)
        out.append(
            f'<rect x="{cursor:.1f}" y="{bar_y}" width="{max(seg, 1.5):.1f}" height="{bar_h}" fill="{colour}">'
            f'<title>{esc(lang["name"])} — {lang["share"] * 100:.1f}%</title></rect>\n'
        )
        cursor += seg
    out.append("</g>\n")

    for i, lang in enumerate(langs):
        col, row = i % cols, i // cols
        x = 20 + col * col_w
        y = bar_y + bar_h + 34 + row * row_h
        colour = GREY if lang["name"] == "Other" else colour_for(lang["name"], i)
        repos = f' · {lang["repos"]} repos' if lang.get("repos") else ""
        out.append(
            f'<g class="leg" style="animation-delay:{.7 + i * .08:.2f}s">'
            f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{colour}"/>'
            f'<text x="{x + 17}" y="{y}"><tspan class="n">{esc(lang["name"])}</tspan>'
            f'<tspan class="p" dx="6" fill="{colour}">{lang["share"] * 100:.1f}%</tspan>'
            f'<tspan class="n" dx="4" font-size="10">{esc(repos)}</tspan></text></g>\n'
        )

    out.append("</svg>\n")
    return "".join(out)


if __name__ == "__main__":
    write(str(ROOT / "assets" / "info-card.svg"), info_card())
    write(str(ROOT / "assets" / "lang-bars.svg"), lang_bars())
