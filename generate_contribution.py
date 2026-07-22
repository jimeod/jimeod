"""
generate_contribution.py

Generates `github-contribution-animation.svg`: a 53x7 GitHub-style contribution
calendar with a diagonal "slant reveal" animation (bottom-left -> top-right),
a bright glint/specular flash on each square as it lands, and an outer glow
filter on high-intensity (level 3+) squares.

Pure SMIL — no CSS transitions, no JS. Fully self-contained, renders anywhere
SVG + SMIL is supported (GitHub's README renderer included).

Run:  python3 generate_contribution.py
"""

import random
from config import (
    CONTRIBUTION_SVG, BG_DARK, BG_PANEL, BORDER_GLASS, LEVELS, GLINT_COLOR,
    NEON_CYAN, NEON_PURPLE, FONT_MONO,
)

random.seed(7)  # deterministic demo data — swap get_levels() for real data if you like

COLS, ROWS = 53, 7
CELL, GAP = 11, 3
PITCH = CELL + GAP

MARGIN_LEFT = 34
MARGIN_TOP = 46
MARGIN_RIGHT = 24
MARGIN_BOTTOM = 22

GRID_W = COLS * PITCH - GAP
GRID_H = ROWS * PITCH - GAP
WIDTH = MARGIN_LEFT + GRID_W + MARGIN_RIGHT
HEIGHT = MARGIN_TOP + GRID_H + MARGIN_BOTTOM

STEP = 0.045      # seconds of delay between successive diagonals
REVEAL_DUR = 0.55  # seconds each square takes to flash + settle
HOLD = 3.0         # pause (seconds) once fully revealed, before looping

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def get_levels():
    """
    Returns a COLS x ROWS grid of contribution intensity levels (0-4).

    If `contrib_data.json` exists next to this script (produced by scraping
    https://github.com/users/<username>/contributions — see fetch_real_data()
    below, or the GitHub GraphQL API), that real data is used. Otherwise
    falls back to plausible-looking demo data so the script still runs
    standalone for anyone trying it out.
    """
    import json
    import os

    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contrib_data.json")
    if os.path.exists(json_path):
        with open(json_path) as f:
            raw = json.load(f)
        grid = [[0] * ROWS for _ in range(COLS)]
        for key, level in raw.items():
            week, day = (int(x) for x in key.split(","))
            if 0 <= week < COLS and 0 <= day < ROWS:
                grid[week][day] = level
        return grid

    weights = [40, 24, 18, 12, 6]  # skew toward fewer/low contributions, like real data
    grid = []
    for _c in range(COLS):
        col = [random.choices(range(5), weights=weights, k=1)[0] for _r in range(ROWS)]
        grid.append(col)
    return grid


def build_svg():
    levels = get_levels()
    max_diag = (COLS - 1) + (ROWS - 1)
    total_cycle = max_diag * STEP + REVEAL_DUR + HOLD

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="{FONT_MONO}">'
    )

    # ---- defs: glow filters + gradients ----
    parts.append('<defs>')
    parts.append(
        '<filter id="squareGlow" x="-150%" y="-150%" width="400%" height="400%">'
        '<feGaussianBlur stdDeviation="2.1" result="blur"/>'
        '<feMerge>'
        '<feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/>'
        '</feMerge></filter>'
    )
    parts.append(
        '<filter id="panelGlow" x="-30%" y="-30%" width="160%" height="160%">'
        '<feGaussianBlur stdDeviation="10" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    parts.append(
        f'<linearGradient id="titleGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{NEON_CYAN}"/>'
        f'<stop offset="100%" stop-color="{NEON_PURPLE}"/>'
        f'</linearGradient>'
    )
    parts.append(
        f'<radialGradient id="bgGlow" cx="50%" cy="0%" r="90%">'
        f'<stop offset="0%" stop-color="{NEON_CYAN}" stop-opacity="0.10"/>'
        f'<stop offset="100%" stop-color="{NEON_CYAN}" stop-opacity="0"/>'
        f'</radialGradient>'
    )
    parts.append('</defs>')

    # ---- background panel (glassmorphism) ----
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="{BG_DARK}"/>')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#bgGlow)"/>')
    parts.append(
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="13" '
        f'fill="none" stroke="{BORDER_GLASS}" stroke-width="1.2"/>'
    )

    # ---- title ----
    parts.append(
        f'<text x="{MARGIN_LEFT}" y="24" font-size="13.5" font-weight="700" '
        f'letter-spacing="1.5" fill="url(#titleGrad)">CONTRIBUTION MATRIX</text>'
    )
    parts.append(
        f'<circle cx="{WIDTH - 20}" cy="20" r="4" fill="{NEON_CYAN}">'
        f'<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/>'
        f'</circle>'
    )

    # ---- invisible master clock driving the infinite loop ----
    parts.append(
        f'<rect id="masterClock" x="0" y="0" width="0" height="0" opacity="0">'
        f'<animate attributeName="opacity" values="0;0" dur="{total_cycle:.3f}s" '
        f'repeatCount="indefinite"/></rect>'
    )

    # ---- day-of-week labels ----
    for row, label in DAY_LABELS.items():
        y = MARGIN_TOP + row * PITCH + CELL - 2
        parts.append(
            f'<text x="{MARGIN_LEFT - 8}" y="{y}" font-size="9" fill="#5c6570" '
            f'text-anchor="end">{label}</text>'
        )

    # ---- month labels (approximate, every ~4.35 weeks) ----
    for m in range(12):
        col = round(m * (COLS / 12))
        x = MARGIN_LEFT + col * PITCH
        parts.append(
            f'<text x="{x}" y="{MARGIN_TOP - 10}" font-size="9" fill="#5c6570">{MONTHS[m]}</text>'
        )

    # ---- the grid itself ----
    for c in range(COLS):
        for r in range(ROWS):
            level = levels[c][r]
            color = LEVELS[level]
            x = MARGIN_LEFT + c * PITCH
            y = MARGIN_TOP + r * PITCH
            diag = c + (ROWS - 1 - r)          # bottom-left -> top-right sweep
            delay = diag * STEP

            filter_attr = ' filter="url(#squareGlow)"' if level >= 3 else ''
            cx, cy = x + CELL / 2, y + CELL / 2

            # Pop-in scale uses an explicit translate/scale/translate trio
            # (avoids relying on transform-origin, which some SVG sanitizers drop).
            scale_anim = (
                f'<animateTransform attributeName="transform" type="scale" '
                f'begin="masterClock.begin+{delay:.3f}s" dur="{REVEAL_DUR}s" '
                f'values="0.4;1.12;1" keyTimes="0;0.3;1" fill="freeze"/>'
            )

            rect = (
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{LEVELS[0]}" opacity="0">'
                f'<animate attributeName="opacity" begin="masterClock.begin+{delay:.3f}s" '
                f'dur="{REVEAL_DUR}s" values="0;1;1" keyTimes="0;0.18;1" fill="freeze"/>'
                f'<animate attributeName="fill" begin="masterClock.begin+{delay:.3f}s" '
                f'dur="{REVEAL_DUR}s" '
                f'values="{GLINT_COLOR};{GLINT_COLOR};{color}" '
                f'keyTimes="0;0.22;1" fill="freeze"/>'
                f'</rect>'
            )

            parts.append(f'<g{filter_attr}>')
            parts.append(f'<g transform="translate({cx},{cy})">')
            parts.append(f'<g>{scale_anim}')
            parts.append(f'<g transform="translate({-cx},{-cy})">')
            parts.append(rect)
            parts.append('</g></g></g></g>')

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    with open(CONTRIBUTION_SVG, "w") as f:
        f.write(svg)
    print(f"Wrote {CONTRIBUTION_SVG} ({len(svg)} bytes)")
