"""Turn the GitHub avatar into one-colour ASCII art that prints row by row.

Run once (or whenever the avatar changes) -- the output is static, so the daily
workflow does not rebuild it and does not need Pillow:

    uv run --with pillow python tools/render_avatar.py
"""

from __future__ import annotations

import io
import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from svgkit import BASE_CSS, GREEN, GREY, style, svg_open, write

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("PROFILE_USER", "JuanMa0912")

COLS = 72
ASPECT = 0.55          # monospace cells are far taller than they are wide
RAMP = " .`:-~=+*coaO#8%@"
FONT_SIZE = 8.6
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE * 1.0


def fetch_avatar() -> Image.Image:
    url = f"https://github.com/{USER}.png?size=480"
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-builder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    img = Image.open(io.BytesIO(raw))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        flat = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(flat, img)
    return img.convert("L")


def to_ascii(img: Image.Image) -> list[str]:
    rows = max(1, round(COLS * (img.height / img.width) * ASPECT))
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.25)
    img = img.resize((COLS, rows), Image.LANCZOS)
    px = img.load()

    # Decide polarity from the border: if the avatar sits on a light background,
    # the background must map to blanks or the portrait drowns in glyphs.
    border = [px[x, 0] for x in range(COLS)] + [px[x, rows - 1] for x in range(COLS)]
    border += [px[0, y] for y in range(rows)] + [px[COLS - 1, y] for y in range(rows)]
    invert = sum(border) / len(border) > 128

    last = len(RAMP) - 1
    lines = []
    for y in range(rows):
        chars = []
        for x in range(COLS):
            value = px[x, y]
            if invert:
                value = 255 - value
            chars.append(RAMP[min(last, value * len(RAMP) // 256)])
        lines.append("".join(chars).rstrip())
    return lines


def build(lines: list[str]) -> str:
    width = round(COLS * CHAR_W) + 4
    height = round(len(lines) * LINE_H) + 26

    out = [svg_open(width, height, f"ASCII portrait of {USER}")]
    out.append(style(BASE_CSS + f"""
.px {{ font-size: {FONT_SIZE}px; fill: {GREEN}; white-space: pre; letter-spacing: 0; }}
.sig {{ font-size: 9px; fill: {GREY}; opacity: 0; animation: fade-in .6s ease-out {len(lines) * .035 + .5:.2f}s forwards; }}
@keyframes print {{ from {{ width: 0; }} to {{ width: {width}px; }} }}
clipPath rect {{ animation: print .55s steps({COLS // 2}) backwards; }}
"""))

    for i, line in enumerate(lines):
        y = 10 + i * LINE_H
        out.append(
            f'<clipPath id="r{i}" style="animation-delay:{i * 0.035:.2f}s">'
            f'<rect x="0" y="{y - FONT_SIZE:.1f}" width="{width}" height="{LINE_H + 1:.1f}"/></clipPath>\n'
            f'<text class="px" x="2" y="{y:.1f}" xml:space="preserve" clip-path="url(#r{i})">'
            f'{line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</text>\n'
        )

    out.append(
        f'<text class="sig" x="2" y="{height - 8}">'
        f'./render_avatar.py --cols {COLS} --ramp density</text>\n'
    )
    out.append("</svg>\n")
    return "".join(out)


if __name__ == "__main__":
    lines = to_ascii(fetch_avatar())
    print("\n".join(lines))
    write(str(ROOT / "assets" / "avatar-ascii.svg"), build(lines))
