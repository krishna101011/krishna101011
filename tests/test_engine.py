"""Tests the snake-frame logic in isolation from rendering — synthetic day
lists in, mood tags out.
"""
from datetime import date, timedelta

from scripts.pysnake.engine import IDLE_GAP_THRESHOLD_DAYS, build_frames


def _days(entries):
    return [{"date": d, "count": c} for d, c in entries]


def test_gap_past_the_threshold_produces_an_idle_frame():
    start = date(2025, 1, 1)
    next_day = start + timedelta(days=IDLE_GAP_THRESHOLD_DAYS + 2)
    days = _days([(start.isoformat(), 1), (next_day.isoformat(), 1)])
    frames = build_frames(days)
    assert any(frame.mood == "idle" for frame in frames)


def test_gap_under_the_threshold_produces_no_idle_frame():
    start = date(2025, 1, 1)
    next_day = start + timedelta(days=IDLE_GAP_THRESHOLD_DAYS - 2)
    days = _days([(start.isoformat(), 1), (next_day.isoformat(), 1)])
    frames = build_frames(days)
    assert not any(frame.mood == "idle" for frame in frames)


def test_top_decile_contribution_day_produces_a_fed_frame():
    # Nine quiet days plus one big one — the 90th-percentile threshold lands
    # exactly on the standout day, so only it should be tagged "fed".
    counts = [1] * 9 + [10]
    entries = [(f"2025-01-{i + 1:02d}", c) for i, c in enumerate(counts)]
    frames = build_frames(_days(entries))
    assert any(frame.mood == "fed" for frame in frames)


def test_single_contribution_day_produces_valid_frames():
    frames = build_frames(_days([("2025-01-01", 1)]))
    assert frames
    assert all(frame.mood in ("eating", "idle", "fed") for frame in frames)
