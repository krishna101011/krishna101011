"""Runs krishna.py for real and writes the captured output into README.md
between two independent pairs of HTML comment markers — same technique
update_readme.py uses for the currently-building line, just scoped to two
regions instead of one:

  <!-- SNAKE:START/END --> — the pysnake chip + picture + caption, in hero
  position right under the header banner.
  <!-- REPL:START/END --> — the identity REPL transcript + the language
  chart. The snake picture itself does NOT also appear here — it's already
  shown once, up top; the REPL block still prints krishna.snake.render()'s
  real return value as text, since that's honest output from a real call,
  just not a second copy of the image.

Both regions are read, substituted, and written in one pass in
update_readme() — a single read, two substitutions in memory, one write —
so a run can't leave the file with only one region updated.

Also owns cache-busting for every generated-SVG <picture> embed in these
blocks: each image URL gets a `?v={sha}` query string set to the short SHA
of the commit that last actually changed that specific file (via `git log`),
so GitHub's CDN can't keep serving a stale image after the file changes.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import krishna  # noqa: E402

README_PATH = REPO_ROOT / "README.md"
SNAKE_START_MARKER = "<!-- SNAKE:START -->"
SNAKE_END_MARKER = "<!-- SNAKE:END -->"
REPL_START_MARKER = "<!-- REPL:START -->"
REPL_END_MARKER = "<!-- REPL:END -->"

RAW_BASE = "https://raw.githubusercontent.com/krishna101011/krishna101011/main"

# Chip labels — see scripts/render_chip.py for the CHIPS this must match.
CHIP_LABELS = {
    "repl": "krishna.py — python3",
    "langstats": "language_breakdown()",
    "snake": "snake.render()",
}

CHIP_TEMPLATE = """<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{raw}/assets/chip-{name}-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="{raw}/assets/chip-{name}-light.svg" />
  <img alt="{label}" src="{raw}/assets/chip-{name}-light.svg"/>
</picture>"""

# Non-negotiable: this is the one sentence that substantiates the whole
# custom-engine effort over a third-party action. Don't paraphrase it.
SNAKE_CAPTION = (
    "generated twice a day by <code>scripts/pysnake/</code> — a snake engine "
    "I wrote myself, not a third-party action"
)

SNAKE_PICTURE_TEMPLATE = """<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{raw}/dist/pysnake-dark.svg?v={dark_sha}" />
  <source media="(prefers-color-scheme: light)" srcset="{raw}/dist/pysnake-light.svg?v={light_sha}" />
  <img alt="a Python-colored snake eating my contribution graph, one green square at a time" src="{raw}/dist/pysnake-light.svg?v={light_sha}" width="100%"/>
</picture>"""

LANGSTATS_PICTURE_TEMPLATE = """<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{raw}/dist/langstats-dark.svg?v={dark_sha}" />
  <source media="(prefers-color-scheme: light)" srcset="{raw}/dist/langstats-light.svg?v={light_sha}" />
  <img alt="a horizontal bar chart of language bytes across my public repositories" src="{raw}/dist/langstats-light.svg?v={light_sha}" width="400"/>
</picture>"""


def _chip(name: str) -> str:
    return CHIP_TEMPLATE.format(raw=RAW_BASE, name=name, label=CHIP_LABELS[name])


def _last_changed_sha(relative_path: str) -> str:
    """The short SHA of the most recent commit that touched relative_path,
    so the cache-bust query string only changes when the file's content
    actually did. Falls back to the current HEAD if the file was only just
    created and hasn't been committed yet (e.g. a first local run)."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%h", "--", relative_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    sha = result.stdout.strip()
    if sha:
        return sha

    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return head.stdout.strip() or "local"


def _repl_line(expr: str, value: object) -> str:
    return f">>> krishna.{expr}\n{value!r}"


def _langstats_caption(repo_count: int, language_count: int) -> str:
    """Templated off the real counts so this never goes stale the way a
    hardcoded "one public repo, one language" would the moment either
    number changes — see krishna.repo_count() / krishna.language_breakdown()."""
    if repo_count == 1 and language_count == 1:
        return "one public repo, one language — the bar-chart equivalent of a strong opinion."

    repo_word = "repo" if repo_count == 1 else "repos"
    language_word = "language" if language_count == 1 else "languages"
    return f"{repo_count} public {repo_word}, {language_count} {language_word} — draw your own conclusions."


def build_transcript() -> str:
    breakdown = krishna.language_breakdown()

    lines = [
        ">>> import krishna",
        _repl_line("whoami()", krishna.whoami()),
        _repl_line("currently_building()", krishna.currently_building()),
        _repl_line("skills", krishna.skills),
        _repl_line("projects", krishna.projects),
        _repl_line("language_breakdown()", breakdown),
        _repl_line("snake.render()", krishna.snake.render()),
    ]

    langstats_caption = _langstats_caption(krishna.repo_count(), len(breakdown))

    langstats_picture = LANGSTATS_PICTURE_TEMPLATE.format(
        raw=RAW_BASE,
        dark_sha=_last_changed_sha("dist/langstats-dark.svg"),
        light_sha=_last_changed_sha("dist/langstats-light.svg"),
    )

    return (
        f"{_chip('repl')}\n\n"
        f"```pycon\n{chr(10).join(lines)}\n```\n\n"
        f'<div align="center">\n\n'
        f"{_chip('langstats')}\n\n"
        f"{langstats_picture}\n\n"
        f"<sub>{langstats_caption}</sub>\n\n"
        "</div>"
    )


def build_snake_block() -> str:
    """The pysnake chip + picture + caption — hero position, right under
    the header banner. Shown exactly once on the page; the REPL transcript
    below still prints krishna.snake.render()'s real text return value,
    just not this image a second time."""
    snake_picture = SNAKE_PICTURE_TEMPLATE.format(
        raw=RAW_BASE,
        dark_sha=_last_changed_sha("dist/pysnake-dark.svg"),
        light_sha=_last_changed_sha("dist/pysnake-light.svg"),
    )

    return (
        f"{_chip('snake')}\n\n"
        f"{snake_picture}\n\n"
        f"<sub>{SNAKE_CAPTION}</sub>"
    )


def _replace_between_markers(content: str, start_marker: str, end_marker: str, block: str) -> tuple[str, bool]:
    """Pure string transform, no filesystem — the part that actually needs
    testing for "replaces exactly once, never duplicates," independently
    per marker pair so one region's write can't bleed into another's."""
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if not pattern.search(content):
        raise ValueError(f"markers {start_marker!r}/{end_marker!r} not found")

    replacement = f"{start_marker}\n{block}\n{end_marker}"
    new_content = pattern.sub(replacement, content)
    return new_content, new_content != content


def update_readme() -> bool:
    """One read, two substitutions in memory, one write — so a run can
    never leave the file with only the snake block or only the REPL block
    updated."""
    content = README_PATH.read_text(encoding="utf-8")
    changed_any = False

    for start_marker, end_marker, block in (
        (SNAKE_START_MARKER, SNAKE_END_MARKER, build_snake_block()),
        (REPL_START_MARKER, REPL_END_MARKER, build_transcript()),
    ):
        try:
            content, changed = _replace_between_markers(content, start_marker, end_marker, block)
        except ValueError as exc:
            print(f"{exc} in {README_PATH}", file=sys.stderr)
            sys.exit(1)
        changed_any = changed_any or changed

    if changed_any:
        README_PATH.write_text(content, encoding="utf-8")
    return changed_any


def main() -> None:
    changed = update_readme()
    print("README REPL block updated." if changed else "No change needed.")


if __name__ == "__main__":
    main()
