"""An actually-importable stand-in for a bio. Every function here does real
work — nothing is copied prose. `python krishna.py` runs a live demo of
each one; scripts/render_repl_block.py imports this module for real and
captures the return values verbatim into the README's REPL transcript.
"""
from __future__ import annotations

import os
from pathlib import Path

import requests

USERNAME = "krishna101011"
GITHUB_API = "https://api.github.com"

_ROOT = Path(__file__).resolve().parent
_CURRENTLY_BUILDING_PATH = _ROOT / "currently_building.txt"


def whoami() -> str:
    return "student · builds things that teach other people to code"


def currently_building() -> str:
    """Reads the status line scripts/update_readme.py refreshes every 6
    hours from my latest public push."""
    try:
        return _CURRENTLY_BUILDING_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "heads down, nothing pushed publicly this week"


skills: dict[str, str] = {
    "Python": "primary language — this file included",
    "React": "frontend for the apps this profile links to",
    "FastAPI": "backend framework of choice",
    "GitHub Actions": "the thing that keeps this README from going stale",
    "Anthropic API": "used it to build an essay-feedback tool",
}

projects: list = []  # public repos are still in the oven — this one doesn't count


class Snake:
    """A handle onto the already-generated PySnake SVGs (see
    scripts/pysnake/). render() doesn't re-run the scrape+render pipeline
    here — that needs a live fetch of GitHub's contribution calendar, which
    belongs in the pysnake workflow, not in a README demo — it reports on
    what's actually sitting in dist/ right now."""

    def render(self) -> str:
        paths = sorted((_ROOT / "dist").glob("pysnake-*.svg"))
        if not paths:
            return "no pysnake SVGs on disk yet — run scripts/pysnake/main.py"
        rendered = ", ".join(f"{p.name} ({p.stat().st_size}B)" for p in paths)
        return f"already rendered: {rendered}"


snake = Snake()


def _github_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def repo_count() -> int:
    """How many public repos GET /users/{username}/repos returns right now
    — same source language_breakdown() sums bytes over, kept as its own
    cheap call (no per-repo languages_url fetches) so callers who only need
    the count don't pay for the rest."""
    headers = _github_headers()
    resp = requests.get(
        f"{GITHUB_API}/users/{USERNAME}/repos",
        headers=headers,
        params={"per_page": 100, "type": "owner"},
        timeout=10,
    )
    resp.raise_for_status()
    return len(resp.json())


def language_breakdown() -> dict[str, float]:
    """Sums `language` bytes (via each repo's languages_url) across every
    public repo and returns each language's share as a percentage, sorted
    largest first. No padding for variety — if one language dominates, the
    numbers say so."""
    headers = _github_headers()
    resp = requests.get(
        f"{GITHUB_API}/users/{USERNAME}/repos",
        headers=headers,
        params={"per_page": 100, "type": "owner"},
        timeout=10,
    )
    resp.raise_for_status()
    repos = resp.json()

    totals: dict[str, int] = {}
    for repo in repos:
        lang_resp = requests.get(repo["languages_url"], headers=headers, timeout=10)
        lang_resp.raise_for_status()
        for language, byte_count in lang_resp.json().items():
            totals[language] = totals.get(language, 0) + byte_count

    grand_total = sum(totals.values())
    if grand_total == 0:
        return {}

    return {
        language: round(byte_count / grand_total * 100, 1)
        for language, byte_count in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    }


def _demo() -> None:
    for expr, value in (
        ("whoami()", whoami()),
        ("currently_building()", currently_building()),
        ("skills", skills),
        ("projects", projects),
        ("repo_count()", repo_count()),
        ("language_breakdown()", language_breakdown()),
        ("snake.render()", snake.render()),
    ):
        print(f">>> krishna.{expr}")
        print(repr(value))
        print()


if __name__ == "__main__":
    _demo()
