"""Rebuild every data-driven SVG in the profile. Standard library only.

    python tools/build.py

The ASCII portrait is deliberately not rebuilt here: it needs Pillow and only
changes when the avatar does. See tools/render_avatar.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fetch_data
import render_cards
import render_diagrams
import render_heatmap
from svgkit import write

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def main() -> None:
    fetch_data.main()
    ASSETS.mkdir(exist_ok=True)
    print("rendering ...")
    write(str(ASSETS / "contrib-heatmap.svg"), render_heatmap.build())
    write(str(ASSETS / "info-card.svg"), render_cards.info_card())
    write(str(ASSETS / "lang-bars.svg"), render_cards.lang_bars())
    write(str(ASSETS / "header.svg"), render_diagrams.header())
    write(str(ASSETS / "agent-loop.svg"), render_diagrams.agent_loop())
    write(str(ASSETS / "lifecycle.svg"), render_diagrams.lifecycle())
    print("done")


if __name__ == "__main__":
    main()
