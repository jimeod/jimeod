"""
generate_infocard.py

Generates `info-card.svg`: a small neofetch-style panel meant to sit beside
the ASCII portrait terminal. Each line slides up + fades in with a staggered
0.06s delay per row, mimicking a terminal printing neofetch output.

Pure SMIL — no CSS transitions, no JS.

Run:  python3 generate_infocard.py
"""

from config import (
    INFOCARD_SVG, USERNAME, BG_DARK, BG_PANEL, BORDER_GLASS,
    NEON_CYAN, NEON_GREEN, NEON_ORANGE, NEON_PURPLE, NEON_WHITE,
    TEXT_MUTED, FONT_MONO,
)

WIDTH = 420
PADDING_X = 22
PADDING_TOP = 26
PADDING_BOTTOM = 20
LINE_H = 22

STAGGER = 0.06     # seconds between each row's stagger start
RISE_DUR = 0.42    # seconds for a row's slide+fade to complete
RISE_PX = 10        # px a row rises while fading in
HOLD = 3.0

# ---- content: (kind, text, color) ----
# kind "header" draws a bold section title with a rule under it.
# kind "row"    draws "label: value" with label/value colored separately.
CONTENT = [
    ("title", f"{USERNAME}@github", NEON_CYAN),
    ("rule", "", BORDER_GLASS),
    ("header", "About", NEON_ORANGE),
    ("row", ("Role", "Software Engineering student"), (TEXT_MUTED, NEON_WHITE)),
    ("row", ("Focus", "ML · Computer Vision · Robotics"), (TEXT_MUTED, NEON_WHITE)),
    ("row", ("LinkedIn", "jimena-ortega-dominguez"), (TEXT_MUTED, NEON_WHITE)),
    ("header", "Building", NEON_GREEN),
    ("row", ("Robot", "Self-balancing bot (ESP32 + IMU)"), (TEXT_MUTED, NEON_CYAN)),
    ("row", ("Vision", "Traffic sign recognition"), (TEXT_MUTED, NEON_CYAN)),
    ("row", ("Learning", "Sensor fusion · PID · YOLO"), (TEXT_MUTED, NEON_CYAN)),
    ("header", "Stack", NEON_PURPLE),
    ("row", ("Languages", "Python · C++ · C# · TypeScript"), (TEXT_MUTED, NEON_PURPLE)),
    ("row", ("ML / CV", "PyTorch · TensorFlow · scikit-learn"), (TEXT_MUTED, NEON_PURPLE)),
    ("row", ("Tools", "Git · Docker · Arduino · GCP"), (TEXT_MUTED, NEON_PURPLE)),
    ("header", "Highlights", NEON_ORANGE),
    ("row", ("Activity", "64 contributions this year"), (TEXT_MUTED, NEON_WHITE)),
    ("row", ("Pinned", "Self-Balancing-Robot · BatteryMe-app"), (TEXT_MUTED, NEON_WHITE)),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg():
    n_lines = len(CONTENT)
    height = PADDING_TOP + n_lines * LINE_H + PADDING_BOTTOM
    total_cycle = (n_lines - 1) * STAGGER + RISE_DUR + HOLD

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="{FONT_MONO}">'
    )

    parts.append('<defs>')
    parts.append(
        '<filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    parts.append('</defs>')

    # background glass panel
    parts.append(f'<rect width="{WIDTH}" height="{height}" rx="14" fill="{BG_DARK}"/>')
    parts.append(
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="13" '
        f'fill="none" stroke="{BORDER_GLASS}" stroke-width="1.2"/>'
    )

    # master clock for infinite loop
    parts.append(
        f'<rect opacity="0" width="0" height="0">'
        f'<animate id="masterClock" attributeName="opacity" values="0;0" '
        f'dur="{total_cycle:.3f}s" repeatCount="indefinite"/></rect>'
    )

    y = PADDING_TOP
    for i, item in enumerate(CONTENT):
        kind = item[0]
        begin = i * STAGGER
        row_y = y + i * LINE_H

        # Each row is wrapped in a translate that animates from +RISE_PX -> 0
        # combined with an opacity fade — the staggered terminal-print effect.
        parts.append(f'<g opacity="0">')
        parts.append(
            f'<animate attributeName="opacity" begin="masterClock.begin+{begin:.3f}s" '
            f'dur="{RISE_DUR}s" values="0;1" fill="freeze"/>'
        )
        parts.append(f'<animateTransform attributeName="transform" type="translate" '
                      f'begin="masterClock.begin+{begin:.3f}s" dur="{RISE_DUR}s" '
                      f'values="0,{RISE_PX};0,0" fill="freeze"/>')

        if kind == "title":
            _, text, color = item
            parts.append(
                f'<text x="{PADDING_X}" y="{row_y}" font-size="14.5" font-weight="700" '
                f'fill="{color}" filter="url(#softGlow)">{esc(text)}</text>'
            )
        elif kind == "rule":
            parts.append(
                f'<line x1="{PADDING_X}" y1="{row_y - 6}" x2="{WIDTH - PADDING_X}" '
                f'y2="{row_y - 6}" stroke="{BORDER_GLASS}" stroke-width="1"/>'
            )
        elif kind == "header":
            _, text, color = item
            parts.append(
                f'<text x="{PADDING_X}" y="{row_y}" font-size="12.5" font-weight="700" '
                f'letter-spacing="1.2" fill="{color}">{esc(text.upper())}</text>'
            )
        elif kind == "row":
            _, (label, value), (label_color, value_color) = item
            parts.append(
                f'<text x="{PADDING_X}" y="{row_y}" font-size="12.5" '
                f'fill="{label_color}">{esc(label)}: '
                f'<tspan fill="{value_color}">{esc(value)}</tspan></text>'
            )
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    with open(INFOCARD_SVG, "w") as f:
        f.write(svg)
    print(f"Wrote {INFOCARD_SVG} ({len(svg)} bytes)")
