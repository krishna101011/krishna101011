"""Turns a list of {"date", "count"} days into a sequence of animation
frames - actual snake-game logic (a deque body that grows, shrinks, and
moves one grid cell at a time), not a data-to-gif pass.

Coordinate system matches GitHub's own contribution calendar: columns are
weeks, rows are days-of-week with Sunday=0..Saturday=6, both derived
straight from the ISO date so this module never needs to know anything
about GitHub's HTML (that's fetch_contributions.py's job).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date as Date
from datetime import timedelta

MAX_SNAKE_LENGTH = 6

# How many empty days in a row before the snake stops gliding and takes a
# nap instead. Below this, a gap is just "a quiet weekend" and the normal
# glide covers it fine.
IDLE_GAP_THRESHOLD_DAYS = 10
IDLE_FRAME_COUNT = 3

# Days at or above this percentile of this user's own non-zero contribution
# counts get a "fed" pulse instead of a plain "eating" frame.
FED_PERCENTILE = 0.90

Coord = tuple[int, int]  # (week_column, weekday_row)


@dataclass
class Frame:
    coords: list[Coord]  # head-first
    mood: str  # "eating" | "idle" | "fed"


def grid_position(day: Date, anchor_sunday: Date) -> Coord:
    """Public: render.py needs the same week/day grid math to place the
    heatmap cells behind the snake."""
    row = (day.weekday() + 1) % 7  # Python: Monday=0..Sunday=6 -> Sunday=0..Saturday=6
    col = (day - anchor_sunday).days // 7
    return col, row


def sunday_on_or_before(day: Date) -> Date:
    """Public for the same reason as grid_position() above."""
    return day - timedelta(days=(day.weekday() + 1) % 7)


def _percentile(sorted_ascending: list[int], pct: float) -> int:
    if not sorted_ascending:
        return 0
    index = min(len(sorted_ascending) - 1, int(len(sorted_ascending) * pct))
    return sorted_ascending[index]


def _orthogonal_path(start: Coord, target: Coord) -> list[Coord]:
    """Down the column to the right row, then across to the next active
    column - never a diagonal, never a teleport. Returns the intermediate
    steps plus the final target; excludes `start` itself."""
    col, row = start
    target_col, target_row = target
    path: list[Coord] = []

    row_step = 1 if target_row > row else -1
    while row != target_row:
        row += row_step
        path.append((col, row))

    col_step = 1 if target_col > col else -1
    while col != target_col:
        col += col_step
        path.append((col, row))

    if not path:
        path.append((col, row))
    return path


def _advance(body: deque[Coord], new_head: Coord, grow: bool) -> None:
    body.appendleft(new_head)
    if not grow or len(body) > MAX_SNAKE_LENGTH:
        body.pop()


def build_frames(days: list[dict]) -> list[Frame]:
    if not days:
        raise ValueError("build_frames() needs at least one day of calendar data")

    parsed = [(Date.fromisoformat(d["date"]), d["count"]) for d in days]
    anchor = sunday_on_or_before(parsed[0][0])

    contributed_counts = sorted(count for _, count in parsed if count > 0)
    fed_threshold = _percentile(contributed_counts, FED_PERCENTILE) if contributed_counts else None

    contribution_days = [(day, count) for day, count in parsed if count > 0]

    frames: list[Frame] = []
    body: deque[Coord] = deque()

    if not contribution_days:
        # Nothing to eat all year - the snake just sits and naps. Still a
        # valid (if bleak) animation rather than an empty file.
        body.append(grid_position(parsed[0][0], anchor))
        for _ in range(IDLE_FRAME_COUNT):
            frames.append(Frame(list(body), "idle"))
        return frames

    first_target = grid_position(contribution_days[0][0], anchor)
    body.append((first_target[0] - 1, first_target[1]))  # start just off-grid, same row

    previous_day: Date | None = None
    for day, count in contribution_days:
        target = grid_position(day, anchor)

        if previous_day is not None:
            gap_days = (day - previous_day).days - 1
            if gap_days > IDLE_GAP_THRESHOLD_DAYS:
                # the snake naps here so it doesn't have to watch three
                # weeks of me not committing.
                for _ in range(IDLE_FRAME_COUNT):
                    frames.append(Frame(list(body), "idle"))

        path = _orthogonal_path(body[0], target)
        for i, step in enumerate(path):
            arriving = i == len(path) - 1
            _advance(body, step, grow=arriving)
            if arriving:
                fed = fed_threshold is not None and count >= fed_threshold
                mood = "fed" if fed else "eating"
                frames.append(Frame(list(body), mood))
                if fed:
                    frames.append(Frame(list(body), "fed"))  # hold the pulse one extra beat
            else:
                frames.append(Frame(list(body), "eating"))

        previous_day = day

    return frames
