"""Renders a frame sequence (see engine.py) plus the underlying contribution
heatmap as a self-contained SVG, animated purely with SMIL (<animate>) -
GitHub's markdown sanitizer strips <script> tags from embedded content, so
there is no other option for an animated SVG here anyway.

Two variants share the same animation and only swap the heatmap/background
contrast (light vs dark) - the snake itself stays Python blue/yellow in
both, so it reads the same regardless of which GitHub theme is viewing it.
"""
from __future__ import annotations

from datetime import date as Date

from .engine import Frame, grid_position, sunday_on_or_before

CELL_SIZE = 10
CELL_GAP = 3
PITCH = CELL_SIZE + CELL_GAP
MARGIN = 6
FRAME_DURATION_SECONDS = 0.35

SNAKE_BLUE = "#306998"
SNAKE_YELLOW = "#FFD43B"

# GitHub's own light/dark heatmap palettes, levels 0 (empty) through 4.
LIGHT_LEVELS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
DARK_LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
LIGHT_ZZZ_COLOR = "#57606a"
DARK_ZZZ_COLOR = "#8b949e"


def _levels_by_date(days: list[dict]) -> dict[str, int]:
    """Bucket each day's count into a 0-4 heatmap level using this user's
    own quartiles, since we don't have GitHub's internal thresholds - this
    is purely a rendering concern, unrelated to engine.py's exact-count
    "fed" logic."""
    counts = sorted(d["count"] for d in days if d["count"] > 0)
    if not counts:
        return {d["date"]: 0 for d in days}

    q1 = counts[int(len(counts) * 0.25)]
    q2 = counts[int(len(counts) * 0.5)]
    q3 = counts[int(len(counts) * 0.75)]

    levels: dict[str, int] = {}
    for d in days:
        count = d["count"]
        if count == 0:
            level = 0
        elif count <= q1:
            level = 1
        elif count <= q2:
            level = 2
        elif count <= q3:
            level = 3
        else:
            level = 4
        levels[d["date"]] = level
    return levels


def _key_times(n: int) -> list[float]:
    if n <= 1:
        return [0.0]
    return [i / (n - 1) for i in range(n)]


def _animate(attr: str, values: list[str], key_times: list[float], dur: str) -> str:
    return (
        f'<animate attributeName="{attr}" '
        f'values="{";".join(values)}" '
        f'keyTimes="{";".join(f"{t:.5f}" for t in key_times)}" '
        f'dur="{dur}" calcMode="discrete" repeatCount="indefinite"/>'
    )


def render_svg(days: list[dict], frames: list[Frame], theme: str) -> str:
    if theme not in ("dark", "light"):
        raise ValueError(f"theme must be 'dark' or 'light', got {theme!r}")
    if not days:
        raise ValueError("render_svg() needs at least one day of calendar data")
    if not frames:
        raise ValueError("render_svg() needs at least one frame")

    levels = DARK_LEVELS if theme == "dark" else LIGHT_LEVELS
    zzz_color = DARK_ZZZ_COLOR if theme == "dark" else LIGHT_ZZZ_COLOR

    anchor = sunday_on_or_before(Date.fromisoformat(days[0]["date"]))
    positions = {d["date"]: grid_position(Date.fromisoformat(d["date"]), anchor) for d in days}
    max_col = max(col for col, _row in positions.values())

    width = MARGIN * 2 + (max_col + 1) * PITCH
    height = MARGIN * 2 + 7 * PITCH

    day_levels = _levels_by_date(days)
    cells = []
    for d in days:
        col, row = positions[d["date"]]
        x = MARGIN + col * PITCH
        y = MARGIN + row * PITCH
        level = day_levels[d["date"]]
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" fill="{levels[level]}"/>')

    key_times = _key_times(len(frames))
    total_duration = max(len(frames) - 1, 1) * FRAME_DURATION_SECONDS
    dur = f"{total_duration:.2f}s"

    def px(coord: tuple[int, int]) -> tuple[int, int]:
        col, row = coord
        return MARGIN + col * PITCH, MARGIN + row * PITCH

    segments = []
    for segment_index in range(6):  # engine.MAX_SNAKE_LENGTH, kept in sync manually - see engine.py
        pixel_positions = []
        for frame in frames:
            body = frame.coords
            coord = body[segment_index] if segment_index < len(body) else body[-1]
            pixel_positions.append(px(coord))

        xs = [str(x) for x, _y in pixel_positions]
        ys = [str(y) for _x, y in pixel_positions]

        fill_animation = ""
        if segment_index == 0:
            fills = [SNAKE_YELLOW if frame.mood == "fed" else SNAKE_BLUE for frame in frames]
            fill_animation = _animate("fill", fills, key_times, dur)

        segments.append(
            f'<rect x="{pixel_positions[0][0]}" y="{pixel_positions[0][1]}" '
            f'width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" fill="{SNAKE_BLUE}">'
            f"{_animate('x', xs, key_times, dur)}"
            f"{_animate('y', ys, key_times, dur)}"
            f"{fill_animation}"
            f"</rect>"
        )

    head_pixels = [px(frame.coords[0]) for frame in frames]
    zzz_xs = [str(x + CELL_SIZE + 2) for x, _y in head_pixels]
    zzz_ys = [str(y - 3) for _x, y in head_pixels]
    zzz_opacity = ["1" if frame.mood == "idle" else "0" for frame in frames]
    zzz = (
        f'<text font-size="8" font-family="monospace, monospace" fill="{zzz_color}" '
        f'x="{head_pixels[0][0] + CELL_SIZE + 2}" y="{head_pixels[0][1] - 3}" opacity="0">'
        f"{_animate('x', zzz_xs, key_times, dur)}"
        f"{_animate('y', zzz_ys, key_times, dur)}"
        f"{_animate('opacity', zzz_opacity, key_times, dur)}"
        "z z z</text>"
    )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'role="img" aria-label="An animated snake, colored like Python\'s logo, '
        'crawling across my GitHub contribution graph and eating the days I actually committed code.">'
        "<title>PySnake - a hand-built contribution snake, not a third-party action</title>"
        + "".join(cells)
        + zzz
        + "".join(segments)
        + "</svg>"
    )
