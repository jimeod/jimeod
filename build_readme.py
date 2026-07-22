"""
build_readme.py

Builds the GitHub profile README:
  1. Regenerates SVG assets:
       - terminal-card.svg
       - info-card.svg
       - github-contribution-animation.svg

  2. Writes README.md with:
       - GitHub avatar
       - terminal card
       - info card
       - contribution animation

Run:
    python3 build_readme.py
"""

import subprocess
import sys
import os

from config import (
    USERNAME,
    README_PATH,
    TERMINAL_SVG,
    INFOCARD_SVG,
    CONTRIBUTION_SVG,
)


START_MARKER = "<!-- PROFILE-SVG:START -->"
END_MARKER = "<!-- PROFILE-SVG:END -->"


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def regenerate_svgs():
    """
    Runs all SVG generators.
    """

    scripts = (
        "generate_contribution.py",
        "generate_terminal.py",
        "generate_infocard.py",
    )

    for script in scripts:
        path = os.path.join(SCRIPT_DIR, script)

        print(f"--- running {script} ---")

        subprocess.run(
            [sys.executable, path],
            check=True,
            cwd=SCRIPT_DIR,
        )


def _rel(path: str) -> str:
    """
    Cleans relative paths.
    """

    return path[2:] if path.startswith("./") else path


def render_block() -> str:
    """
    Creates the generated README section.
    """

    terminal_rel = _rel(TERMINAL_SVG)
    infocard_rel = _rel(INFOCARD_SVG)
    contribution_rel = _rel(CONTRIBUTION_SVG)

    return f"""{START_MARKER}

<p align="center">
  <img 
    <img src="https://github.com/jimeod.png?size=200">
    width="180"
    alt="{USERNAME} avatar"
  />
</p>

<h2 align="center">
  Hi, I'm {USERNAME} 👋
</h2>

<p align="center">
  Software Engineering Student · Machine Learning · Robotics
</p>

<br/>

<table>
  <tr>
    <td valign="top">
      <img 
        src="{terminal_rel}" 
        alt="Animated ASCII terminal portrait"
      />
    </td>

    <td valign="top">
      <img 
        src="{infocard_rel}" 
        alt="Neofetch-style info card"
      />
    </td>
  </tr>
</table>

<br/>

<p align="center">
  <img 
    src="{contribution_rel}"
    alt="Animated contribution graph"
  />
</p>

{END_MARKER}
"""


def write_readme():
    """
    Updates README while preserving manual content.
    """

    block = render_block()

    try:
        with open(README_PATH, "r", encoding="utf-8") as file:
            existing = file.read()

    except FileNotFoundError:
        existing = f"# Hi, I'm {USERNAME} 👋\n"


    if START_MARKER in existing and END_MARKER in existing:

        before = existing.split(START_MARKER)[0]
        after = existing.split(END_MARKER)[1]

        new_content = (
            before
            + block
            + after
        )

    else:

        new_content = (
            existing.rstrip()
            + "\n\n"
            + block
            + "\n"
        )


    with open(
        README_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(new_content)


    print(f"README generated: {README_PATH}")


if __name__ == "__main__":

    regenerate_svgs()
    write_readme()