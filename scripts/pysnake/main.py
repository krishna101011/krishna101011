"""CLI entrypoint: fetch -> engine -> render -> write dist/*.svg.

Runs identically locally and in CI - no environment-specific behavior,
username is a plain argument:

    python -m scripts.pysnake.main <github-username>
"""
from __future__ import annotations

import sys
from pathlib import Path

from .engine import build_frames
from .fetch_contributions import ContributionFetchError, fetch_calendar
from .render import render_svg

DIST_DIR = Path(__file__).resolve().parent.parent.parent / "dist"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python -m scripts.pysnake.main <github-username>", file=sys.stderr)
        return 2

    username = argv[0]

    try:
        days = fetch_calendar(username)
    except ContributionFetchError as exc:
        # Non-zero exit -> red CI. A quiet fallback here would mean a
        # stale snake sits in the README forever with nobody noticing.
        print(f"pysnake: {exc}", file=sys.stderr)
        return 1

    frames = build_frames(days)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    dark_path = DIST_DIR / "pysnake-dark.svg"
    light_path = DIST_DIR / "pysnake-light.svg"
    dark_path.write_text(render_svg(days, frames, theme="dark"), encoding="utf-8", newline="\n")
    light_path.write_text(render_svg(days, frames, theme="light"), encoding="utf-8", newline="\n")

    total_contributions = sum(d["count"] for d in days)
    print(
        f"pysnake: {len(days)} days ({total_contributions} contributions) -> "
        f"{len(frames)} frames -> {dark_path.name}, {light_path.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
