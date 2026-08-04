"""Tests the marker-replacement string transform in isolation from the
live krishna.py calls it's normally fed by."""
import pytest

from scripts.render_repl_block import END_MARKER, START_MARKER, _replace_between_markers


def test_replace_between_markers_inserts_new_content():
    content = f"before\n{START_MARKER}\nold stuff\n{END_MARKER}\nafter"
    new_content, changed = _replace_between_markers(content, "new block")
    assert changed is True
    assert new_content == f"before\n{START_MARKER}\nnew block\n{END_MARKER}\nafter"
    assert new_content.count(START_MARKER) == 1
    assert new_content.count(END_MARKER) == 1


def test_replace_between_markers_is_a_noop_when_content_is_already_current():
    content = f"before\n{START_MARKER}\nsame block\n{END_MARKER}\nafter"
    new_content, changed = _replace_between_markers(content, "same block")
    assert changed is False
    assert new_content == content


def test_replace_between_markers_does_not_duplicate_on_repeated_calls():
    content = f"before\n{START_MARKER}\nold\n{END_MARKER}\nafter"
    once, changed_once = _replace_between_markers(content, "block A")
    twice, changed_twice = _replace_between_markers(once, "block A")

    assert changed_once is True
    assert changed_twice is False
    assert twice == once
    assert twice.count(START_MARKER) == 1
    assert twice.count(END_MARKER) == 1


def test_replace_between_markers_raises_when_markers_missing():
    with pytest.raises(ValueError):
        _replace_between_markers("no markers in this content at all", "block")
