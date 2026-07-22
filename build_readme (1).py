"""
build_readme.py

Orchestrates the whole profile-README build:
  1. Regenerates all three SVGs (contribution graph, terminal card, info card).
  2. Writes README.md with:
       - terminal-card.svg and info-card.svg side-by-side in an HTML <table>
       - github-contribution-animation.svg centered underneath

Run:  python3 build_readme.py
This is the only script you need to run day-to-day; it calls the other three.
"""

import subprocess
import sys
import os

from config import (
    USERNAME, README_PATH, TERMINAL_SVG, INFOCARD_SVG, CONTRIBUTION_SVG,
)

# Markers so re-running this script updates the generated block in place
# without clobbering any hand-written content above/below it.
START_MARKER = "<!-- PROFILE-SVG:START -->"
END_MARKER = "<!-- PROFILE-SVG:END -->"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def regenerate_svgs():
    for script in ("generate_contribution.py", "generate_terminal.py", "generate_infocard.py"):
        path = os.path.join(SCRIPT_DIR, script)
        print(f"--- running {script} ---")
        subprocess.run([sys.executable, path], check=True, cwd=SCRIPT_DIR)


def _rel(path: str) -> str:
    # Strip a leading "./" so links look clean in the rendered README
    return path[2:] if path.startswith("./") else path


def render_block() -> str:
    terminal_rel = _rel(TERMINAL_SVG)
    infocard_rel = _rel(INFOCARD_SVG)
    contribution_rel = _rel(CONTRIBUTION_SVG)

    return f"""{START_MARKER}
<table>
  <tr>
    <td valign="top">
      <img src="{terminal_rel}" alt="Animated ASCII terminal portrait" />
    </td>
    <td valign="top">
      <img src="{infocard_rel}" alt="Neofetch-style info card" />
    </td>
  </tr>
</table>

<p align="center">
  <img src="{contribution_rel}" alt="Animated contribution graph" />
</p>
{END_MARKER}"""


def write_readme():
    block = render_block()

    try:
        with open(README_PATH, "r") as f:
            existing = f.read()
    except FileNotFoundError:
        existing = f"# Hi, I'm {USERNAME} 👋\n\n"

    if START_MARKER in existing and END_MARKER in existing:
        pre = existing.split(START_MARKER)[0]
        post = existing.split(END_MARKER)[1]
        new_content = pre + block + post
    else:
        sep = "\n\n" if not existing.endswith("\n\n") else ""
        new_content = existing + sep + block + "\n"

    with open(README_PATH, "w") as f:
        f.write(new_content)
    print(f"Wrote {README_PATH}")


if __name__ == "__main__":
    regenerate_svgs()
    write_readme()
