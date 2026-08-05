"""Guards against the snake-loop diagram drifting out of sync with the real
thresholds in engine.py — same "fail loud instead of silently wrong"
pattern as the langstats caption guard and fetch_contributions.py's
markup-drift check."""
from scripts.pysnake import engine
from scripts.render_snake_loop import fed_label, gap_days_label, render_svg


def test_gap_days_label_reflects_engines_actual_threshold():
    # ground truth re-imported fresh from engine.py, not copied — if
    # IDLE_GAP_THRESHOLD_DAYS ever changes, this recomputes the expected
    # text instead of comparing against a stale hardcoded number.
    assert str(engine.IDLE_GAP_THRESHOLD_DAYS) in gap_days_label()


def test_fed_label_reflects_engines_actual_percentile():
    expected_top_pct = round((1 - engine.FED_PERCENTILE) * 100)
    assert f"top {expected_top_pct}%" in fed_label()


def test_rendered_svgs_actually_embed_the_derived_labels():
    # the labels aren't just computed correctly in isolation — the SVG the
    # README embeds has to actually contain them.
    for theme in ("dark", "light"):
        svg = render_svg(theme)
        assert gap_days_label() in svg
        assert fed_label() in svg


def test_rendered_svgs_have_no_script_or_style_tags():
    for theme in ("dark", "light"):
        svg = render_svg(theme)
        assert "<script" not in svg
        assert "<style" not in svg
