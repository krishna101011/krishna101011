"""Renders a small "title bar" chip SVG: one accent dot and a label, placed
above the REPL block / langstats chart / snake animation for a shared
visual identity instead of three ad hoc captions.

GitHub's markdown sanitizer strips <style> tags and most inline style=""
attributes from rendered READMEs, same as it strips <script> — so, like
pysnake/langstats, this uses direct presentation attributes (fill, stroke)
only. No CSS.
"""
from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

HEIGHT = 30
DOT_RADIUS = 5
DOT_MARGIN = 14
TEXT_START_OFFSET = DOT_MARGIN + DOT_RADIUS * 2 + 8
CHAR_WIDTH_ESTIMATE = 7.3  # monospace at font-size 12
RIGHT_PADDING = 16
MIN_WIDTH = 180

BLUE = "#306998"
YELLOW = "#FFD43B"
DARK_TEXT = "#c9d1d9"
LIGHT_TEXT = "#24292f"
DARK_BODY = "#161b22"
LIGHT_BODY = "#f6f8fa"


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_chip(label: str, theme: str) -> str:
    if theme not in ("dark", "light"):
        raise ValueError(f"theme must be 'dark' or 'light', got {theme!r}")
    if not label:
        raise ValueError("render_chip() needs a non-empty label")

    text_color = DARK_TEXT if theme == "dark" else LIGHT_TEXT
    body_color = DARK_BODY if theme == "dark" else LIGHT_BODY

    width = max(MIN_WIDTH, TEXT_START_OFFSET + int(len(label) * CHAR_WIDTH_ESTIMATE) + RIGHT_PADDING)
    dot_cx = DOT_MARGIN + DOT_RADIUS
    dot_cy = HEIGHT // 2
    label_safe = _escape(label)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" '
        f'viewBox="0 0 {width} {HEIGHT}" role="img" aria-label="{label_safe}">'
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{HEIGHT - 1}" rx="6" '
        f'fill="{body_color}" stroke="{BLUE}" stroke-width="1"/>'
        f'<circle cx="{dot_cx}" cy="{dot_cy}" r="{DOT_RADIUS}" fill="{YELLOW}"/>'
        f'<text x="{TEXT_START_OFFSET}" y="{dot_cy + 4}" font-size="12" '
        f'font-family="monospace, monospace" fill="{text_color}">{label_safe}</text>'
        "</svg>"
    )


def write_chip(name: str, label: str) -> None:
    """Writes assets/chip-{name}-{dark,light}.svg."""
    ASSETS_DIR.mkdir(exist_ok=True)
    for theme in ("dark", "light"):
        svg = render_chip(label, theme)
        (ASSETS_DIR / f"chip-{name}-{theme}.svg").write_text(svg, encoding="utf-8")


CHIPS = {
    "repl": "krishna.py — python3",
    "langstats": "language_breakdown()",
    "snake": "snake.render()",
}


def main() -> None:
    for name, label in CHIPS.items():
        write_chip(name, label)
    print(f"Wrote {len(CHIPS) * 2} chip SVGs to {ASSETS_DIR}")


if __name__ == "__main__":
    main()
