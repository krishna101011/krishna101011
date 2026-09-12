from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "github-history.json"
README_FILE = ROOT / "README.md"

START_MARKER = "<!-- METRICS:START -->"
END_MARKER = "<!-- METRICS:END -->"


def main() -> None:
    with DATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        history = json.load(file)

    snapshots = history.get(
        "snapshots",
        [],
    )

    if not snapshots:
        raise RuntimeError(
            "No historical snapshot exists."
        )

    latest = snapshots[-1]

    activity = latest.get(
        "activity",
        {},
    )

    repository_count = latest.get(
        "repository_count",
        0,
    )

    active_repository_count = latest.get(
        "active_repository_count",
        0,
    )

    stars = latest.get(
        "stars",
        0,
    )

    forks = latest.get(
        "forks",
        0,
    )

    commits = activity.get(
        "commits",
        0,
    )

    pull_requests = activity.get(
        "pull_requests",
        0,
    )

    issues = activity.get(
        "issues",
        0,
    )

    activity_index = activity.get(
        "activity_index",
        0,
    )

    recent_activity = (
        f"{commits} commits · "
        f"{pull_requests} PRs · "
        f"{issues} issues"
    )

    replacement = f"""<!-- METRICS:START -->
| METRIC | VALUE |
|---|---:|
| REPOSITORIES | {repository_count} |
| ACTIVE REPOSITORIES | {active_repository_count} |
| STARS | {stars} |
| FORKS | {forks} |
| RECENT ACTIVITY | {recent_activity} |
| ACTIVITY INDEX | {activity_index}/100 |
<!-- METRICS:END -->"""

    content = README_FILE.read_text(
        encoding="utf-8"
    )

    start = content.find(
        START_MARKER
    )

    end = content.find(
        END_MARKER
    )

    if start == -1 or end == -1:
        raise RuntimeError(
            "README metric markers "
            "were not found."
        )

    end += len(END_MARKER)

    new_content = (
        content[:start]
        + replacement
        + content[end:]
    )

    README_FILE.write_text(
        new_content,
        encoding="utf-8",
    )

    print(
        "README metrics updated."
    )


if __name__ == "__main__":
    main()