"""Runs krishna.py for real and writes the captured output into README.md
as a Python REPL transcript, between two HTML comment markers — same
technique update_readme.py uses for the currently-building line, just
scoped to the whole identity block.

Also owns cache-busting for every generated-SVG <picture> embed in that
block: each image URL gets a `?v={sha}` query string set to the short SHA
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
START_MARKER = "<!-- REPL:START -->"
END_MARKER = "<!-- REPL:END -->"

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

# Dry, not padded — see scripts/langstats.py.
LANGSTATS_CAPTION = "one public repo, one language — the bar-chart equivalent of a strong opinion."

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


def build_transcript() -> str:
    lines = [
        ">>> import krishna",
        _repl_line("whoami()", krishna.whoami()),
        _repl_line("currently_building()", krishna.currently_building()),
        _repl_line("skills", krishna.skills),
        _repl_line("projects", krishna.projects),
        _repl_line("language_breakdown()", krishna.language_breakdown()),
        _repl_line("snake.render()", krishna.snake.render()),
    ]

    langstats_picture = LANGSTATS_PICTURE_TEMPLATE.format(
        raw=RAW_BASE,
        dark_sha=_last_changed_sha("dist/langstats-dark.svg"),
        light_sha=_last_changed_sha("dist/langstats-light.svg"),
    )

    snake_picture = SNAKE_PICTURE_TEMPLATE.format(
        raw=RAW_BASE,
        dark_sha=_last_changed_sha("dist/pysnake-dark.svg"),
        light_sha=_last_changed_sha("dist/pysnake-light.svg"),
    )

    return (
        f"{_chip('repl')}\n\n"
        f"```pycon\n{chr(10).join(lines)}\n```\n\n"
        f'<div align="center">\n\n'
        f"{_chip('langstats')}\n\n"
        f"{langstats_picture}\n\n"
        f"<sub>{LANGSTATS_CAPTION}</sub>\n\n"
        "</div>\n\n"
        f'<div align="center">\n\n'
        f"{_chip('snake')}\n\n"
        f"{snake_picture}\n\n"
        f"<sub>{SNAKE_CAPTION}</sub>\n\n"
        "</div>"
    )


def _replace_between_markers(content: str, block: str) -> tuple[str, bool]:
    """Pure string transform, no filesystem — the part that actually needs
    testing for "replaces exactly once, never duplicates"."""
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    if not pattern.search(content):
        raise ValueError(f"markers {START_MARKER!r}/{END_MARKER!r} not found")

    replacement = f"{START_MARKER}\n{block}\n{END_MARKER}"
    new_content = pattern.sub(replacement, content)
    return new_content, new_content != content


def update_readme() -> bool:
    content = README_PATH.read_text(encoding="utf-8")
    try:
        new_content, changed = _replace_between_markers(content, build_transcript())
    except ValueError as exc:
        print(f"{exc} in {README_PATH}", file=sys.stderr)
        sys.exit(1)

    if changed:
        README_PATH.write_text(new_content, encoding="utf-8")
    return changed


def main() -> None:
    changed = update_readme()
    print("README REPL block updated." if changed else "No change needed.")


if __name__ == "__main__":
    main()
