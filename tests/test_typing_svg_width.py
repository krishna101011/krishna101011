"""Guards against the header typing-SVG clipping its own text again.

readme-typing-svg centers every line (text-anchor='middle') inside a fixed
canvas (`width=`). If a line is wider than that canvas, it clips evenly off
both ends — silently, since it's just an <img> in markdown; nothing else
would ever notice. This estimates each line's rendered width from a
char-width measured directly against the live service (see the constant
below) and fails loudly if any line would come within margin of overflowing,
the same "fail loud instead of silently wrong" pattern fetch_contributions.py
uses for markup drift.
"""
import re
from pathlib import Path
from urllib.parse import unquote_plus

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"

# Measured directly: fetched the real readme-typing-svg output at a wide
# canvas (so nothing clipped), froze the SMIL animation on each line, and
# read the actual SVG text bbox width via getBBox() in a real browser.
# "import this" -> 132px/11 chars, "import antigravity" -> 216px/18 chars,
# the "git commit" line -> 456px/38 chars: all exactly 12.0px/char. This is
# only valid for this exact font+size; the test below checks that combo
# hasn't silently changed underneath this calibration.
CALIBRATED_FONT = "Fira Code"
CALIBRATED_SIZE = "20"
CHAR_WIDTH_PX = 12.0

# Real margin, not a hairline — leaves room for minor cross-renderer font
# metric variance instead of a number that only just barely fits today.
MARGIN_PX = 40


def _extract_typing_svg_url() -> str:
    readme = README_PATH.read_text(encoding="utf-8")
    match = re.search(r"https://readme-typing-svg\.demolab\.com\?[^\)]+", readme)
    assert match, "no readme-typing-svg URL found in README.md"
    return match.group(0)


def _query_params(url: str) -> dict[str, str]:
    query = url.split("?", 1)[1]
    params: dict[str, str] = {}
    for pair in query.split("&"):
        key, _, value = pair.partition("=")
        params[key] = value
    return params


def _decoded_lines(params: dict[str, str]) -> list[str]:
    raw_lines = params["lines"].split(";")
    # SVG text content collapses runs of whitespace to one space and trims
    # the ends (XML whitespace handling) — matching that here keeps the
    # width estimate honest instead of over-counting collapsed spaces.
    return [re.sub(r"\s+", " ", unquote_plus(line)).strip() for line in raw_lines]


def test_calibration_still_matches_the_configured_font_and_size():
    params = _query_params(_extract_typing_svg_url())
    font = unquote_plus(params["font"])
    size = params["size"]
    assert (font, size) == (CALIBRATED_FONT, CALIBRATED_SIZE), (
        f"typing-SVG now uses font={font!r} size={size!r}, but CHAR_WIDTH_PX "
        f"was measured for {CALIBRATED_FONT!r} size={CALIBRATED_SIZE!r} — "
        "re-measure and update CHAR_WIDTH_PX before trusting this guard again"
    )


def test_every_typing_svg_line_fits_within_the_configured_width_with_margin():
    url = _extract_typing_svg_url()
    params = _query_params(url)
    configured_width = int(params["width"])
    lines = _decoded_lines(params)
    assert lines, "no lines= found in the typing-SVG URL"

    failures = []
    for line in lines:
        estimated_width = len(line) * CHAR_WIDTH_PX
        budget = configured_width - MARGIN_PX
        if estimated_width > budget:
            failures.append(
                f"  {line!r}: ~{estimated_width:.0f}px needed (+{MARGIN_PX}px margin), "
                f"only {configured_width}px configured"
            )

    if failures:
        pytest.fail(
            "typing-SVG line(s) would clip against width="
            f"{configured_width} in README.md:\n" + "\n".join(failures) +
            "\nWiden `width=` in the typing-SVG URL, or shorten the line."
        )
