"""Static-content SVGs: the typing header and the two animated diagrams.

These carry no fetched data, so the daily workflow does not need to rerun them
-- but they live here so the whole profile is reproducible from one command.
"""

from __future__ import annotations

from pathlib import Path

from svgkit import (BASE_CSS, BLUE, GREEN, GREY, LINE, ORANGE, PANEL, PURPLE,
                    esc, style, svg_open, write)

ROOT = Path(__file__).resolve().parent.parent
CHAR = 0.6  # monospace advance width as a fraction of the font size


def typed(uid: str, text: str, x: float, y: float, size: float, fill: str,
          delay: float, speed: float = 0.055) -> tuple[str, str]:
    """A line that types itself out. Returns (css, markup).

    The reveal is a clipPath whose width steps once per character, so the text
    stays real text rather than becoming path data.
    """
    span = len(text) * size * CHAR
    dur = len(text) * speed
    css = (
        f"#clip-{uid} rect {{ animation: type-{uid} {dur:.2f}s steps({len(text)}) {delay:.2f}s backwards; }}\n"
        f"@keyframes type-{uid} {{ from {{ width: 0; }} to {{ width: {span:.1f}px; }} }}\n"
        f"#cur-{uid} {{ animation: type-{uid} {dur:.2f}s steps({len(text)}) {delay:.2f}s backwards,"
        f" blink 1.05s steps(1) {delay:.2f}s infinite; }}\n"
    )
    markup = (
        f'<clipPath id="clip-{uid}"><rect x="{x}" y="{y - size}" width="{span:.1f}" height="{size * 1.45:.1f}"/></clipPath>\n'
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" clip-path="url(#clip-{uid})">{esc(text)}</text>\n'
        f'<rect id="cur-{uid}" x="{x}" y="{y - size * .82:.1f}" width="{size * CHAR:.1f}" height="{size * .95:.1f}" '
        f'fill="{fill}" opacity=".85"/>\n'
    )
    return css, markup


def header() -> str:
    width, height = 900, 220
    prompt = "juanma@github:~$ "
    prompt_w = len(prompt) * 15 * CHAR

    lines = [
        ("a", "whoami --agentic", 20 + prompt_w, 40, 15, GREY, 0.3),
        ("b", "Juan Manuel Velasquez Terreros", 20, 92, 27, BLUE, 1.5),
    ]
    css_parts, body = [], []
    for uid, text, x, y, size, fill, delay in lines:
        css, markup = typed(uid, text, x, y, size, fill, delay)
        css_parts.append(css)
        body.append(markup)

    out = [svg_open(width, height, "Juan Manuel Velasquez Terreros")]
    out.append(style(BASE_CSS + f"""
@keyframes blink {{ 0%, 50% {{ opacity: .85; }} 51%, 100% {{ opacity: 0; }} }}
@keyframes sweep {{ from {{ stroke-dashoffset: 900; }} to {{ stroke-dashoffset: 0; }} }}
.late {{ opacity: 0; animation: fade-up .7s ease-out forwards; }}
.rule {{ stroke: {GREEN}; stroke-width: 1.5; stroke-dasharray: 900; animation: sweep 1.1s ease-out 3.4s backwards; }}
""" + "".join(css_parts)))

    out.append(f'<text x="20" y="40" font-size="15" fill="{GREEN}" font-weight="600">{esc(prompt)}</text>\n')
    out.extend(body)

    out.append(
        f'<text class="late" x="20" y="125" font-size="13.5" fill="{GREY}" style="animation-delay:3.5s">'
        f'Electronic Engineer &#183; M.Sc. candidate in Artificial Intelligence &amp; Data Science '
        f'&#8212; Universidad Autonoma de Occidente, Colombia</text>\n'
    )
    out.append(f'<line class="rule" x1="20" y1="146" x2="{width - 20}" y2="146"/>\n')
    out.append(
        f'<text class="late" x="20" y="176" font-size="14" fill="{GREY}" style="animation-delay:4.1s">'
        f'<tspan fill="{GREEN}" font-weight="600">$</tspan> I build agents that <tspan fill="{BLUE}">observe</tspan>, '
        f'<tspan fill="{BLUE}">diagnose</tspan> and <tspan fill="{BLUE}">safely operate</tspan> production data '
        f'pipelines &#8212;</text>\n'
    )
    out.append(
        f'<text class="late" x="34" y="199" font-size="14" fill="{GREY}" style="animation-delay:4.4s">'
        f'with the guardrails production actually requires. '
        f'<tspan fill="{PURPLE}" font-weight="600">MLOps &#8594; LLMOps &#8594; AgentOps</tspan>, end to end.</text>\n'
    )
    out.append("</svg>\n")
    return "".join(out)


# --------------------------------------------------------------------------- #

def node(x, y, w, h, label, sub, colour, delay, rx=10):
    text = (
        f'<text x="{x + w / 2}" y="{y + (24 if sub else h / 2 + 4)}" text-anchor="middle" font-size="13" '
        f'font-weight="700" fill="{colour}">{esc(label)}</text>'
    )
    if sub:
        text += (
            f'<text x="{x + w / 2}" y="{y + 41}" text-anchor="middle" font-size="10.5" '
            f'fill="{GREY}">{esc(sub)}</text>'
        )
    return (
        f'<g class="node" style="animation-delay:{delay:.2f}s">'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{PANEL}" stroke="{colour}" stroke-width="1.4"/>'
        f'{text}</g>\n'
    )


def agent_loop() -> str:
    width, height = 900, 300
    # The path the pulse travels: the read-only happy path, then home again.
    flow = ("M 100 96 V 70 H 200 M 340 70 H 370 M 510 70 H 544 M 676 70 H 720 "
            "M 795 96 V 176 M 795 228 V 250 H 100 V 96")

    out = [svg_open(width, height, "observe, diagnose, report, approve, execute, verify")]
    out.append(style(BASE_CSS + f"""
.node {{ opacity: 0; animation: fade-up .55s ease-out forwards; }}
.edge {{ stroke: {GREY}; stroke-width: 1.5; fill: none; opacity: 0; animation: fade-in .6s ease-out forwards; }}
.tag {{ fill: {GREY}; font-size: 10px; opacity: 0; animation: fade-in .6s ease-out 2s forwards; }}
"""))
    out.append(
        f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{GREY}"/></marker>'
        f'<path id="flow" d="{flow}" fill="none" stroke="none"/></defs>\n'
    )

    edges = [
        ("M 172 70 H 194", 0.5),
        ("M 342 70 H 364", 0.7),
        ("M 512 70 H 538", 0.9),
        ("M 678 70 H 714", 1.1),
        ("M 795 98 V 170", 1.3),
        ("M 610 118 V 176", 1.5),
        ("M 690 202 H 714", 1.7),
        ("M 795 230 V 250 H 100 V 98", 1.9),
    ]
    for path, delay in edges:
        out.append(f'<path class="edge" d="{path}" marker-end="url(#ar)" style="animation-delay:{delay:.2f}s"/>\n')

    out.append(node(32, 44, 140, 54, "OBSERVE", "logs / timers / tables", BLUE, 0.10))
    out.append(node(202, 44, 140, 54, "DIAGNOSE", "severity model", BLUE, 0.25))
    out.append(node(372, 44, 140, 54, "REPORT", "evidence + next step", BLUE, 0.40))
    out.append(node(720, 44, 150, 54, "EXECUTE", "allowlisted only", GREEN, 0.85))
    out.append(node(720, 176, 150, 54, "VERIFY", "then audit trail", GREEN, 1.00))
    out.append(node(500, 176, 190, 54, "HUMAN APPROVAL", "exact command + time window", ORANGE, 1.15))

    out.append(
        f'<g class="node" style="animation-delay:.55s">'
        f'<path d="M 610 22 L 678 70 L 610 118 L 542 70 Z" fill="{PANEL}" stroke="{PURPLE}" stroke-width="1.4"/>'
        f'<text x="610" y="66" text-anchor="middle" font-size="12" font-weight="700" fill="{PURPLE}">risk</text>'
        f'<text x="610" y="82" text-anchor="middle" font-size="12" font-weight="700" fill="{PURPLE}">class?</text></g>\n'
    )

    out.append(f'<text class="tag" x="686" y="60">read-only</text>\n')
    out.append(f'<text class="tag" x="618" y="152">write / privileged</text>\n')
    out.append(
        f'<text class="tag" x="410" y="245" text-anchor="middle">'
        f'every action leaves an audit trail &#183; nothing destructive runs unapproved</text>\n'
    )

    out.append(
        f'<circle r="4.5" fill="{GREEN}">'
        f'<animateMotion dur="7s" repeatCount="indefinite"><mpath href="#flow"/></animateMotion>'
        f'<animate attributeName="opacity" values="0;.95;.95;0" keyTimes="0;.06;.94;1" dur="7s" '
        f'repeatCount="indefinite"/></circle>\n'
    )
    out.append("</svg>\n")
    return "".join(out)


# --------------------------------------------------------------------------- #

def lifecycle() -> str:
    width, height = 900, 160
    stages = [
        ("MLOps", "ingest / index", "train / serve", BLUE),
        ("LLMOps", "prompts / RAG", "evals / observability", PURPLE),
        ("AgentOps", "autonomy / guardrails", "approvals / audit", GREEN),
    ]
    box_w, gap = 250, 75
    start = (width - (3 * box_w + 2 * gap)) / 2

    out = [svg_open(width, height, "MLOps to LLMOps to AgentOps")]
    out.append(style(BASE_CSS + f"""
.stage {{ opacity: 0; animation: fade-up .6s ease-out forwards; }}
.arrow {{ stroke: {GREY}; stroke-width: 2; fill: none; stroke-dasharray: 60;
          animation: draw .7s ease-out backwards; }}
@keyframes draw {{ from {{ stroke-dashoffset: 60; }} to {{ stroke-dashoffset: 0; }} }}
"""))
    out.append(
        f'<defs><marker id="a2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{GREY}"/></marker></defs>\n'
    )

    for i, (name, l1, l2, colour) in enumerate(stages):
        x = start + i * (box_w + gap)
        out.append(
            f'<g class="stage" style="animation-delay:{i * .35:.2f}s">'
            f'<rect x="{x}" y="30" width="{box_w}" height="92" rx="12" fill="{PANEL}" stroke="{colour}" stroke-width="1.4"/>'
            f'<text x="{x + box_w / 2}" y="62" text-anchor="middle" font-size="16" font-weight="700" fill="{colour}">{name}</text>'
            f'<text x="{x + box_w / 2}" y="84" text-anchor="middle" font-size="11" fill="{GREY}">{esc(l1)}</text>'
            f'<text x="{x + box_w / 2}" y="101" text-anchor="middle" font-size="11" fill="{GREY}">{esc(l2)}</text></g>\n'
        )
        if i < 2:
            ax = x + box_w + 12
            out.append(
                f'<path class="arrow" d="M {ax} 76 H {ax + gap - 26}" marker-end="url(#a2)" '
                f'style="animation-delay:{i * .35 + .35:.2f}s"/>\n'
            )
    out.append("</svg>\n")
    return "".join(out)


if __name__ == "__main__":
    write(str(ROOT / "assets" / "header.svg"), header())
    write(str(ROOT / "assets" / "agent-loop.svg"), agent_loop())
    write(str(ROOT / "assets" / "lifecycle.svg"), lifecycle())
