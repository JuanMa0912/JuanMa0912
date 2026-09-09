"""Shared helpers for the profile SVGs.

Palette rule: every colour here must stay legible on BOTH the GitHub light
(#ffffff) and dark (#0d1117) canvas. GitHub embeds these files as <img>, so a
`prefers-color-scheme` query inside the SVG follows the *OS* theme, not the
GitHub theme -- they disagree often enough that theme-swapped text is a real
invisibility risk. Mid-greys and accents only; never near-black or near-white.
"""

from __future__ import annotations

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# Both-theme-safe palette.
GREEN = "#3fb950"
GREEN_DIM = "#238636"
BLUE = "#4493f8"
PURPLE = "#a371f7"
ORANGE = "#db6d28"
PINK = "#db61a2"
GREY = "#7d8590"        # secondary text  (~4.2:1 on white, ~4.4:1 on #0d1117)
GREY_DIM = "#6e7681"
LINE = "#6e768155"      # borders, semi-transparent so it reads on both
PANEL = "#6e768114"     # panel fill, subtle on both

# GitHub contribution levels 0..4, tuned to read on both canvases.
LEVELS = ["#6e768133", "#0e4429", "#006d32", "#26a641", "#39d353"]

ESCAPES = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;"}


def esc(text: str) -> str:
    return "".join(ESCAPES.get(ch, ch) for ch in str(text))


def svg_open(width: int, height: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}" '
        f'font-family="{FONT}">\n<title>{esc(title)}</title>\n'
    )


def style(css: str) -> str:
    return f"<style>\n{css.strip()}\n</style>\n"


BASE_CSS = f"""
text {{ font-family: {FONT}; }}
@keyframes fade-up {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes fade-in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes pop {{ 0% {{ opacity: 0; transform: scale(.4); }} 70% {{ transform: scale(1.12); }} 100% {{ opacity: 1; transform: scale(1); }} }}
@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; opacity: 1 !important; transform: none !important; }}
}}
"""


def write(path: str, body: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print(f"  wrote {path}")
