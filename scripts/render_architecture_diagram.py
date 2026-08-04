"""Generates assets/architecture-{dark,light}.svg — a static system diagram
of this repo's own pipeline. Not wired into any workflow: unlike dist/, the
thing it depicts (the pipeline's shape) doesn't change on a schedule, only
when the architecture itself does. Run manually after changing a cadence,
adding a workflow, or renaming a script:

    python scripts/render_architecture_diagram.py
"""
from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

BLUE = "#306998"
YELLOW = "#FFD43B"
DARK_TEXT = "#c9d1d9"
LIGHT_TEXT = "#24292f"

WIDTH = 640
HEIGHT = 360


def _box(x: int, y: int, w: int, h: int, lines: list[str], text_color: str) -> str:
    text_x = x + w // 2
    first_y = y + h // 2 - (len(lines) - 1) * 7 + 4
    texts = "".join(
        f'<text x="{text_x}" y="{first_y + i * 15}" text-anchor="middle" '
        f'font-size="{12 if i == 0 else 11}" font-family="monospace, monospace" '
        f'font-weight="{"bold" if i == 0 else "normal"}" fill="{text_color}">{line}</text>'
        for i, line in enumerate(lines)
    )
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
        f'fill="none" stroke="{BLUE}" stroke-width="1.5"/>{texts}'
    )


def _arrow(x1: int, y1: int, x2: int, y2: int, color: str, marker: str, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="4 3"' if dashed else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="1.5"{dash} marker-end="url(#{marker})"/>'
    )


def _label(x: int, y: int, text: str, color: str) -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="10" '
        f'font-family="monospace, monospace" fill="{color}">{text}</text>'
    )


def render_svg(theme: str) -> str:
    if theme not in ("dark", "light"):
        raise ValueError(f"theme must be 'dark' or 'light', got {theme!r}")
    text_color = DARK_TEXT if theme == "dark" else LIGHT_TEXT

    defs = (
        "<defs>"
        f'<marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
        f'<marker id="arrow-yellow" viewBox="0 0 10 10" refX="8" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{YELLOW}"/></marker>'
        "</defs>"
    )

    source = _box(170, 20, 300, 50, ["GitHub contribution calendar", "(public page, no auth)"], text_color)

    pysnake = _box(
        60, 110, 280, 70,
        ["pysnake.yml — every 12h", "fetch → engine → render"],
        text_color,
    )
    update_readme = _box(
        300, 200, 280, 70,
        ["update-readme.yml — every 6h", "update_readme → langstats → repl"],
        text_color,
    )

    commit = _box(170, 290, 300, 50, ["commit to main", "(github-actions[bot])"], text_color)

    arrows = [
        _arrow(320, 70, 320, 108, BLUE, "arrow-blue"),  # source -> pysnake
        _arrow(200, 180, 200, 288, BLUE, "arrow-blue"),  # pysnake -> commit
        _arrow(440, 270, 380, 288, BLUE, "arrow-blue"),  # update-readme -> commit
        _arrow(300, 165, 340, 198, YELLOW, "arrow-yellow", dashed=True),  # pysnake -> update-readme
    ]
    workflow_run_label = _label(365, 190, "workflow_run: completed", YELLOW if theme == "dark" else "#8a6d00")

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        'aria-label="Architecture diagram: the GitHub contribution calendar feeds pysnake.yml '
        '(fetch, engine, render, every 12 hours), which commits to main and, on completion, '
        'triggers update-readme.yml (every 6 hours otherwise) via a workflow_run event; '
        'both workflows commit to main.">'
        + defs
        + source
        + pysnake
        + update_readme
        + commit
        + "".join(arrows)
        + workflow_run_label
        + "</svg>"
    )


def main() -> None:
    ASSETS_DIR.mkdir(exist_ok=True)
    for theme in ("dark", "light"):
        svg = render_svg(theme)
        (ASSETS_DIR / f"architecture-{theme}.svg").write_text(svg, encoding="utf-8")
    print("Wrote assets/architecture-dark.svg / assets/architecture-light.svg")


if __name__ == "__main__":
    main()
