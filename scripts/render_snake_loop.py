"""Renders assets/snake-loop-{dark,light}.svg: a small state diagram of the
three moods build_frames() actually assigns (EATING, IDLE, FED) and the real
conditions that move between them.

Every edge label is derived from scripts/pysnake/engine.py's own constants
at generation time, not retyped — if IDLE_GAP_THRESHOLD_DAYS or
FED_PERCENTILE ever change, this diagram changes with them (or
tests/test_snake_loop.py fails loud; see there).

Pure SVG via direct attributes — no <style>, no <script> — same constraint
GitHub's markdown sanitizer imposes on every other asset here.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.pysnake.engine import FED_PERCENTILE, IDLE_GAP_THRESHOLD_DAYS  # noqa: E402

ASSETS_DIR = REPO_ROOT / "assets"

BLUE = "#306998"
YELLOW = "#FFD43B"
DARK_TEXT = "#c9d1d9"
LIGHT_TEXT = "#24292f"

WIDTH = 620
HEIGHT = 340

EATING = (310, 95, 150, 46)  # cx, cy, w, h — see _box()
IDLE = (120, 275, 150, 46)
FED = (500, 275, 150, 46)


def gap_days_label() -> str:
    return f"gap &gt; {IDLE_GAP_THRESHOLD_DAYS} days"


def fed_label() -> str:
    top_pct = round((1 - FED_PERCENTILE) * 100)
    return f"top {top_pct}% day"


def _box(cx: int, cy: int, w: int, h: int, label: str, color: str, text_color: str) -> str:
    x, y = cx - w // 2, cy - h // 2
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
        f'fill="none" stroke="{color}" stroke-width="1.5"/>'
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="13" '
        f'font-family="monospace, monospace" font-weight="bold" fill="{text_color}">{label}</text>'
    )


def _label(x: int, y: int, text: str, text_color: str) -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="10" '
        f'font-family="monospace, monospace" fill="{text_color}">{text}</text>'
    )


def _curve(x1: int, y1: int, x2: int, y2: int, bend: int, color: str, marker: str) -> str:
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    length = (dx**2 + dy**2) ** 0.5 or 1
    # perpendicular offset, so forward/return edges between the same two
    # nodes arc apart instead of drawing on top of each other
    ox, oy = -dy / length * bend, dx / length * bend
    cx, cy = mx + ox, my + oy
    return (
        f'<path d="M{x1},{y1} Q{cx:.1f},{cy:.1f} {x2},{y2}" fill="none" '
        f'stroke="{color}" stroke-width="1.5" marker-end="url(#{marker})"/>'
    ), (cx, cy)


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

    eating_cx, eating_cy, eating_w, eating_h = EATING
    idle_cx, idle_cy, idle_w, idle_h = IDLE
    fed_cx, fed_cy, fed_w, fed_h = FED

    boxes = (
        _box(eating_cx, eating_cy, eating_w, eating_h, "EATING", BLUE, text_color)
        + _box(idle_cx, idle_cy, idle_w, idle_h, "IDLE", BLUE, text_color)
        + _box(fed_cx, fed_cy, fed_w, fed_h, "FED", YELLOW, text_color)
    )

    # self-loop on EATING: a small arc leaving and re-entering the top edge
    loop_left_x, loop_right_x = eating_cx - 22, eating_cx + 22
    loop_top_y = eating_cy - eating_h // 2
    self_loop = (
        f'<path d="M{loop_left_x},{loop_top_y} '
        f'C{loop_left_x - 10},{loop_top_y - 34} {loop_right_x + 10},{loop_top_y - 34} {loop_right_x},{loop_top_y}" '
        f'fill="none" stroke="{BLUE}" stroke-width="1.5" marker-end="url(#arrow-blue)"/>'
    )
    self_loop_label = _label(eating_cx, loop_top_y - 30, "normal day", text_color)

    edges = []
    labels = []

    # EATING -> IDLE
    path, (cx, cy) = _curve(
        eating_cx - 60, eating_cy + eating_h // 2, idle_cx + 20, idle_cy - idle_h // 2, bend=-45,
        color=BLUE, marker="arrow-blue",
    )
    edges.append(path)
    labels.append(_label(int(cx) - 18, int(cy) - 4, gap_days_label(), text_color))

    # IDLE -> EATING (return)
    path, (cx, cy) = _curve(
        idle_cx + 55, idle_cy - idle_h // 2, eating_cx - 20, eating_cy + eating_h // 2, bend=45,
        color=BLUE, marker="arrow-blue",
    )
    edges.append(path)
    labels.append(_label(int(cx) - 50, int(cy) + 10, "next contribution", text_color))

    # EATING -> FED
    path, (cx, cy) = _curve(
        eating_cx + 60, eating_cy + eating_h // 2, fed_cx - 20, fed_cy - fed_h // 2, bend=45,
        color=YELLOW, marker="arrow-yellow",
    )
    edges.append(path)
    labels.append(_label(int(cx) + 12, int(cy) - 4, fed_label(), text_color))

    # FED -> EATING (return)
    path, (cx, cy) = _curve(
        fed_cx - 55, fed_cy - fed_h // 2, eating_cx + 20, eating_cy + eating_h // 2, bend=-45,
        color=YELLOW, marker="arrow-yellow",
    )
    edges.append(path)
    labels.append(_label(int(cx) + 45, int(cy) + 10, "next tick", text_color))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        'aria-label="State diagram: EATING loops on normal days, moves to IDLE when the gap since '
        f'the last contribution exceeds {IDLE_GAP_THRESHOLD_DAYS} days, moves to FED on a '
        f'{fed_label()}, and both IDLE and FED return to EATING.">'
        + defs
        + boxes
        + self_loop
        + self_loop_label
        + "".join(edges)
        + "".join(labels)
        + "</svg>"
    )


def main() -> None:
    ASSETS_DIR.mkdir(exist_ok=True)
    for theme in ("dark", "light"):
        svg = render_svg(theme)
        (ASSETS_DIR / f"snake-loop-{theme}.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote assets/snake-loop-dark.svg / assets/snake-loop-light.svg "
          f"(gap>{IDLE_GAP_THRESHOLD_DAYS}d, {fed_label()})")


if __name__ == "__main__":
    main()
