"""Tests the marker-replacement string transform in isolation from the
live krishna.py calls it's normally fed by."""
import pytest

from scripts.render_repl_block import (
    REPL_END_MARKER,
    REPL_START_MARKER,
    SNAKE_END_MARKER,
    SNAKE_START_MARKER,
    _langstats_caption,
    _replace_between_markers,
)

START = REPL_START_MARKER
END = REPL_END_MARKER


def test_replace_between_markers_inserts_new_content():
    content = f"before\n{START}\nold stuff\n{END}\nafter"
    new_content, changed = _replace_between_markers(content, START, END, "new block")
    assert changed is True
    assert new_content == f"before\n{START}\nnew block\n{END}\nafter"
    assert new_content.count(START) == 1
    assert new_content.count(END) == 1


def test_replace_between_markers_is_a_noop_when_content_is_already_current():
    content = f"before\n{START}\nsame block\n{END}\nafter"
    new_content, changed = _replace_between_markers(content, START, END, "same block")
    assert changed is False
    assert new_content == content


def test_replace_between_markers_does_not_duplicate_on_repeated_calls():
    content = f"before\n{START}\nold\n{END}\nafter"
    once, changed_once = _replace_between_markers(content, START, END, "block A")
    twice, changed_twice = _replace_between_markers(once, START, END, "block A")

    assert changed_once is True
    assert changed_twice is False
    assert twice == once
    assert twice.count(START) == 1
    assert twice.count(END) == 1


def test_replace_between_markers_raises_when_markers_missing():
    with pytest.raises(ValueError):
        _replace_between_markers("no markers in this content at all", START, END, "block")


def _dual_region_update(content, snake_block, repl_block):
    """Mirrors update_readme()'s loop: one region at a time, over the
    same content string, so a bug that lets one region's substitution
    bleed into the other would show up here too."""
    content, snake_changed = _replace_between_markers(content, SNAKE_START_MARKER, SNAKE_END_MARKER, snake_block)
    content, repl_changed = _replace_between_markers(content, REPL_START_MARKER, REPL_END_MARKER, repl_block)
    return content, snake_changed, repl_changed


def test_two_marker_regions_update_independently_without_bleeding():
    content = (
        f"header\n\n{SNAKE_START_MARKER}\nold snake\n{SNAKE_END_MARKER}\n\n"
        f"middle\n\n{REPL_START_MARKER}\nold repl\n{REPL_END_MARKER}\n\nfooter"
    )

    new_content, snake_changed, repl_changed = _dual_region_update(content, "new snake", "new repl")

    assert snake_changed is True
    assert repl_changed is True
    assert new_content == (
        f"header\n\n{SNAKE_START_MARKER}\nnew snake\n{SNAKE_END_MARKER}\n\n"
        f"middle\n\n{REPL_START_MARKER}\nnew repl\n{REPL_END_MARKER}\n\nfooter"
    )
    # each region's content is only its own — no cross-contamination
    assert "old repl" not in new_content
    assert "old snake" not in new_content
    assert "new repl" not in new_content[: new_content.index(SNAKE_END_MARKER)]
    assert "new snake" not in new_content[new_content.index(REPL_START_MARKER) :]


def test_two_marker_regions_stay_stable_across_repeated_runs():
    content = (
        f"header\n\n{SNAKE_START_MARKER}\nold snake\n{SNAKE_END_MARKER}\n\n"
        f"middle\n\n{REPL_START_MARKER}\nold repl\n{REPL_END_MARKER}\n\nfooter"
    )

    once, _, _ = _dual_region_update(content, "snake block", "repl block")
    twice, snake_changed_again, repl_changed_again = _dual_region_update(once, "snake block", "repl block")

    assert snake_changed_again is False
    assert repl_changed_again is False
    assert twice == once
    assert twice.count(SNAKE_START_MARKER) == 1
    assert twice.count(SNAKE_END_MARKER) == 1
    assert twice.count(REPL_START_MARKER) == 1
    assert twice.count(REPL_END_MARKER) == 1


def test_updating_one_region_leaves_the_other_untouched():
    content = (
        f"header\n\n{SNAKE_START_MARKER}\nsnake v1\n{SNAKE_END_MARKER}\n\n"
        f"middle\n\n{REPL_START_MARKER}\nrepl v1\n{REPL_END_MARKER}\n\nfooter"
    )

    # only the snake region changes this round — repl content is re-fed
    # the exact same block, same as update_readme() does when only one
    # region's live data actually changed.
    new_content, snake_changed, repl_changed = _dual_region_update(content, "snake v2", "repl v1")

    assert snake_changed is True
    assert repl_changed is False
    assert f"{REPL_START_MARKER}\nrepl v1\n{REPL_END_MARKER}" in new_content
    assert f"{SNAKE_START_MARKER}\nsnake v2\n{SNAKE_END_MARKER}" in new_content


def test_langstats_caption_keeps_the_specific_wording_for_the_one_one_case():
    assert _langstats_caption(1, 1) == (
        "one public repo, one language — the bar-chart equivalent of a strong opinion."
    )


@pytest.mark.parametrize(
    ("repo_count", "language_count", "expected"),
    [
        (1, 3, "1 public repo, 3 languages — draw your own conclusions."),
        (5, 1, "5 public repos, 1 language — draw your own conclusions."),
        (4, 7, "4 public repos, 7 languages — draw your own conclusions."),
    ],
)
def test_langstats_caption_pluralizes_correctly_for_other_counts(repo_count, language_count, expected):
    assert _langstats_caption(repo_count, language_count) == expected
