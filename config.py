"""
config.py
Shared configuration + color palette for the GitHub profile SVG generator suite.
Edit USERNAME (and anything else you like) — all other scripts import from here.
"""

# ── Identity ──────────────────────────────────────────────────────────────
USERNAME = "jimeod"
DISPLAY_NAME = "Jimena Ortega Dominguez"

# ── Output paths ──────────────────────────────────────────────────────────
OUT_DIR = "."
CONTRIBUTION_SVG = f"{OUT_DIR}/github-contribution-animation.svg"
TERMINAL_SVG = f"{OUT_DIR}/terminal-card.svg"
INFOCARD_SVG = f"{OUT_DIR}/info-card.svg"
README_PATH = f"{OUT_DIR}/README.md"

# ── Palette: deep dark / cyberpunk-developer neon ──────────────────────────
BG_DARK = "#0d1117"          # page / GitHub-dark background
BG_PANEL = "#12161c"         # glass panel base
BG_PANEL_2 = "#161b22"       # secondary panel tone
BORDER_GLASS = "#30363d"
BORDER_GLOW = "#39ffe3"

NEON_CYAN = "#39ffe3"
NEON_GREEN = "#39d353"
NEON_ORANGE = "#ffab40"
NEON_PURPLE = "#b56bff"
NEON_WHITE = "#f2f6fc"

TEXT_MUTED = "#8b949e"
TEXT_DIM = "#5c6570"

# Contribution-square intensity ramp (GitHub-style, tuned toward neon green)
LEVELS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#127a3b",
    3: "#1fbb5c",
    4: "#39ff8f",
}
GLINT_COLOR = "#f5fff9"  # white-green specular flash color

FONT_MONO = "'SF Mono','Fira Code','JetBrains Mono',ui-monospace,Consolas,monospace"
