"""
generate_terminal.py

Generates `terminal-card.svg`: a macOS-style terminal window containing a
dense ASCII-art rendering of the user's GitHub avatar. The art is revealed
row-by-row, top-to-bottom, with a white "cursor" block sweeping left-to-right
across each row as it prints. Finishes with a typewriter `$ whoami` line.

Pure SMIL — no CSS transitions, no JS.

Run:  python3 generate_terminal.py
"""

import io
import requests
from PIL import Image

from config import (
    TERMINAL_SVG, USERNAME, DISPLAY_NAME, BG_DARK, BG_PANEL, BORDER_GLASS,
    NEON_CYAN, NEON_GREEN, NEON_ORANGE, NEON_PURPLE, NEON_WHITE, TEXT_MUTED,
    FONT_MONO,
)

# ---- ASCII-art tuning ------------------------------------------------------
ASCII_COLS = 64          # characters per row
ASCII_ROWS = 32          # number of rows
# Dense-to-sparse ramp; index 0 = darkest pixel -> index -1 = brightest.
RAMP = "@%#*+=-:. "[::-1]

CHAR_W = 6.15            # px per character cell (monospace-tuned)
CHAR_H = 12.0

ROW_STAGGER = 0.10       # seconds between each row starting to type
TYPE_DUR = 0.40          # seconds for a single row to type across
HOLD = 3.2               # pause after full reveal before the loop resets

WIDTH = 660
TITLEBAR_H = 34
PADDING = 18


def fetch_avatar(username: str) -> Image.Image:
    """
    Downloads the user's GitHub avatar. Falls back to a generated placeholder
    (a simple radial gradient bust) if the network is unavailable, so the
    script still produces valid output offline.
    """
    url = f"https://github.com/{username}.png?size=200"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content)).convert("L")
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] could not fetch avatar for '{username}' ({exc}); using placeholder")
        return _placeholder_image()


def _placeholder_image(size: int = 200) -> Image.Image:
    img = Image.new("L", (size, size), color=20)
    px = img.load()
    cx, cy = size / 2, size / 2
    for yy in range(size):
        for xx in range(size):
            d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
            px[xx, yy] = max(0, 235 - int(d * 1.3))
    return img


def image_to_ascii(img: Image.Image, cols: int, rows: int) -> list[str]:
    """Converts a grayscale image into `rows` strings of `cols` ASCII chars."""
    img = img.resize((cols, rows))
    pixels = img.tobytes()  # mode "L" -> one byte (0-255) per pixel
    ramp_len = len(RAMP)
    lines = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0-255
            idx = min(ramp_len - 1, brightness * ramp_len // 256)
            row_chars.append(RAMP[idx])
        lines.append("".join(row_chars))
    return lines


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(username: str, display_name: str) -> str:
    img = fetch_avatar(username)
    lines = image_to_ascii(img, ASCII_COLS, ASCII_ROWS)

    art_w = ASCII_COLS * CHAR_W
    art_h = ASCII_ROWS * CHAR_H
    height = TITLEBAR_H + PADDING + art_h + PADDING + 34  # + footer typewriter row

    total_cycle = (ASCII_ROWS - 1) * ROW_STAGGER + TYPE_DUR + HOLD

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" '
        f'viewBox="0 0 {WIDTH} {height:.0f}" font-family="{FONT_MONO}">'
    )

    # ---- defs ----
    parts.append('<defs>')
    parts.append(
        '<filter id="termGlow" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="6" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    parts.append(
        f'<linearGradient id="asciiGrad" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{NEON_CYAN}"/>'
        f'<stop offset="100%" stop-color="{NEON_GREEN}"/>'
        f'</linearGradient>'
    )
    parts.append(
        f'<clipPath id="cardClip"><rect x="0" y="0" width="{WIDTH}" height="{height:.0f}" rx="14"/></clipPath>'
    )
    parts.append('</defs>')

    parts.append(f'<g clip-path="url(#cardClip)">')

    # ---- background ----
    parts.append(f'<rect width="{WIDTH}" height="{height:.0f}" fill="{BG_DARK}"/>')
    parts.append(
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2:.0f}" rx="13" '
        f'fill="none" stroke="{BORDER_GLASS}" stroke-width="1.2"/>'
    )

    # ---- title bar (macOS traffic lights) ----
    parts.append(f'<rect x="0" y="0" width="{WIDTH}" height="{TITLEBAR_H}" fill="{BG_PANEL}"/>')
    parts.append(
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{WIDTH}" y2="{TITLEBAR_H}" '
        f'stroke="{BORDER_GLASS}" stroke-width="1"/>'
    )
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{22 + i * 18}" cy="{TITLEBAR_H / 2}" r="6" fill="{color}"/>')
    parts.append(
        f'<text x="{WIDTH / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle" '
        f'font-size="12" fill="{TEXT_MUTED}">{esc(username)}@github — ascii-portrait — 80x{ASCII_ROWS}</text>'
    )

    # ---- master clock (drives infinite loop) ----
    parts.append(
        f'<rect opacity="0" width="0" height="0">'
        f'<animate id="masterClock" attributeName="opacity" values="0;0" '
        f'dur="{total_cycle:.3f}s" repeatCount="indefinite"/></rect>'
    )

    # ---- ASCII art rows ----
    art_x = (WIDTH - art_w) / 2
    art_y = TITLEBAR_H + PADDING

    for r, line in enumerate(lines):
        y = art_y + r * CHAR_H + CHAR_H * 0.8
        begin = r * ROW_STAGGER
        row_w = len(line) * CHAR_W

        # Clip rect reveals the row left-to-right (typewriter sweep)
        clip_id = f"rowClip{r}"
        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'<rect x="{art_x:.2f}" y="{art_y + r * CHAR_H:.2f}" height="{CHAR_H:.2f}" width="0">'
            f'<animate attributeName="width" begin="masterClock.begin+{begin:.3f}s" '
            f'dur="{TYPE_DUR}s" values="0;{row_w:.2f}" fill="freeze"/>'
            f'</rect>'
        )
        parts.append('</clipPath>')

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            f'<text x="{art_x:.2f}" y="{y:.2f}" font-size="{CHAR_H - 1:.1f}" '
            f'fill="url(#asciiGrad)" xml:space="preserve">{esc(line)}</text>'
        )
        parts.append('</g>')

        # sweeping cursor block, tracks the leading edge of the clip rect
        parts.append(
            f'<rect y="{art_y + r * CHAR_H:.2f}" width="{CHAR_W:.2f}" height="{CHAR_H:.2f}" '
            f'fill="{NEON_WHITE}" opacity="0">'
            f'<animate attributeName="x" begin="masterClock.begin+{begin:.3f}s" '
            f'dur="{TYPE_DUR}s" values="{art_x:.2f};{art_x + row_w:.2f}" fill="freeze"/>'
            f'<animate attributeName="opacity" begin="masterClock.begin+{begin:.3f}s" '
            f'dur="{TYPE_DUR}s" values="0.85;0.85;0" keyTimes="0;0.9;1" fill="freeze"/>'
            f'</rect>'
        )

    # ---- footer typewriter: `$ whoami` -> name ----
    footer_text = f"$ whoami"
    reply_text = display_name
    footer_y = art_y + art_h + 22
    footer_begin = (ASCII_ROWS - 1) * ROW_STAGGER + TYPE_DUR + 0.3

    prompt_full = f"{footer_text}"
    prompt_w = len(prompt_full) * CHAR_W
    parts.append(f'<clipPath id="footerClip1">')
    parts.append(
        f'<rect x="{art_x:.2f}" y="{footer_y - CHAR_H:.2f}" height="{CHAR_H + 4:.2f}" width="0">'
        f'<animate attributeName="width" begin="masterClock.begin+{footer_begin:.3f}s" '
        f'dur="0.5s" calcMode="discrete" '
        f'values="0;{prompt_w:.2f}" fill="freeze"/>'
        f'</rect>'
    )
    parts.append('</clipPath>')
    parts.append(f'<g clip-path="url(#footerClip1)">')
    parts.append(
        f'<text x="{art_x:.2f}" y="{footer_y:.2f}" font-size="13" '
        f'fill="{NEON_ORANGE}" xml:space="preserve">{esc(prompt_full)}</text>'
    )
    parts.append('</g>')

    reply_begin = footer_begin + 0.7
    reply_full = reply_text
    reply_w = len(reply_full) * CHAR_W
    reply_x = art_x + prompt_w + CHAR_W
    parts.append(f'<clipPath id="footerClip2">')
    parts.append(
        f'<rect x="{reply_x:.2f}" y="{footer_y - CHAR_H:.2f}" height="{CHAR_H + 4:.2f}" width="0">'
        f'<animate attributeName="width" begin="masterClock.begin+{reply_begin:.3f}s" '
        f'dur="0.6s" calcMode="discrete" '
        f'values="0;{reply_w:.2f}" fill="freeze"/>'
        f'</rect>'
    )
    parts.append('</clipPath>')
    parts.append(f'<g clip-path="url(#footerClip2)">')
    parts.append(
        f'<text x="{reply_x:.2f}" y="{footer_y:.2f}" font-size="13" font-weight="700" '
        f'fill="{NEON_PURPLE}" xml:space="preserve">{esc(reply_full)}</text>'
    )
    parts.append('</g>')

    # blinking cursor after the typed reply
    cursor_x = reply_x + reply_w + 2
    parts.append(
        f'<rect x="{cursor_x:.2f}" y="{footer_y - CHAR_H + 2:.2f}" width="{CHAR_W - 1:.2f}" '
        f'height="{CHAR_H:.2f}" fill="{NEON_WHITE}" opacity="0">'
        f'<animate attributeName="opacity" begin="masterClock.begin+{reply_begin + 0.6:.3f}s" '
        f'dur="1s" values="0;1;1;0;0" keyTimes="0;0.05;0.5;0.55;1" repeatCount="indefinite"/>'
        f'</rect>'
    )

    parts.append('</g>')  # close cardClip group
    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg(USERNAME, DISPLAY_NAME)
    with open(TERMINAL_SVG, "w") as f:
        f.write(svg)
    print(f"Wrote {TERMINAL_SVG} ({len(svg)} bytes)")
