"""Renders dist/langstats-dark.svg and dist/langstats-light.svg: a small
horizontal bar chart of language bytes across my public repos. Data comes
from krishna.language_breakdown() — the same real GitHub-API call the
REPL transcript shows, not a second guess at it. No third-party badge
service.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import krishna  # noqa: E402

DIST_DIR = REPO_ROOT / "dist"

BAR_HEIGHT = 18
BAR_GAP = 10
BAR_MAX_WIDTH = 220
LABEL_WIDTH = 110
MARGIN = 10

PYTHON_BLUE = "#306998"
PYTHON_YELLOW = "#FFD43B"
LIGHT_TEXT = "#24292f"
DARK_TEXT = "#c9d1d9"
LIGHT_TRACK = "#ebedf0"
DARK_TRACK = "#21262d"


def render_svg(breakdown: dict[str, float], theme: str) -> str:
    if theme not in ("dark", "light"):
        raise ValueError(f"theme must be 'dark' or 'light', got {theme!r}")
    if not breakdown:
        raise ValueError("render_svg() needs at least one language")

    text_color = DARK_TEXT if theme == "dark" else LIGHT_TEXT
    track_color = DARK_TRACK if theme == "dark" else LIGHT_TRACK

    languages = list(breakdown.items())  # already sorted largest-first by krishna.language_breakdown()
    width = MARGIN * 2 + LABEL_WIDTH + BAR_MAX_WIDTH + 50
    height = MARGIN * 2 + len(languages) * (BAR_HEIGHT + BAR_GAP) - BAR_GAP

    bars = []
    for i, (language, pct) in enumerate(languages):
        y = MARGIN + i * (BAR_HEIGHT + BAR_GAP)
        bar_width = max(2, round(BAR_MAX_WIDTH * pct / 100))
        fill = PYTHON_YELLOW if i == 0 else PYTHON_BLUE
        text_y = y + BAR_HEIGHT * 0.72
        bars.append(
            f'<text x="{MARGIN}" y="{text_y:.1f}" font-size="12" '
            f'font-family="monospace, monospace" fill="{text_color}">{language}</text>'
            f'<rect x="{MARGIN + LABEL_WIDTH}" y="{y}" width="{BAR_MAX_WIDTH}" height="{BAR_HEIGHT}" '
            f'rx="3" fill="{track_color}"/>'
            f'<rect x="{MARGIN + LABEL_WIDTH}" y="{y}" width="{bar_width}" height="{BAR_HEIGHT}" '
            f'rx="3" fill="{fill}"/>'
            f'<text x="{MARGIN + LABEL_WIDTH + BAR_MAX_WIDTH + 8}" y="{text_y:.1f}" '
            f'font-size="12" font-family="monospace, monospace" fill="{text_color}">{pct:g}%</text>'
        )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'role="img" aria-label="A horizontal bar chart of language bytes across my public repositories.">'
        + "".join(bars)
        + "</svg>"
    )


def main() -> int:
    breakdown = krishna.language_breakdown()
    if not breakdown:
        print("No language data returned from the GitHub API — nothing to render.", file=sys.stderr)
        return 1

    DIST_DIR.mkdir(exist_ok=True)
    for theme in ("dark", "light"):
        svg = render_svg(breakdown, theme)
        (DIST_DIR / f"langstats-{theme}.svg").write_text(svg, encoding="utf-8")

    print(f"Wrote langstats-dark.svg / langstats-light.svg for {len(breakdown)} language(s): {breakdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
