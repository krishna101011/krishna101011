from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USERNAME = "krishna101011"
API_BASE = "https://api.github.com"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
HISTORY_FILE = DATA_DIR / "github-history.json"

USER_AGENT = "krishna101011-control-room/1.0"


def github_get(path: str, page: int | None = None):
    """Request data from GitHub's public API."""
    url = f"{API_BASE}{path}"

    if page is not None:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}page={page}&per_page=100"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    }

    request = Request(url, headers=headers)

    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except HTTPError as error:
            if error.code == 403:
                print(
                    "GitHub rate limit or access restriction encountered."
                )

            if error.code >= 500 and attempt < 2:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                f"GitHub API error {error.code}: {error.reason}"
            ) from error

        except URLError as error:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                f"Network error while contacting GitHub: {error.reason}"
            ) from error

    raise RuntimeError("GitHub request failed after retries.")


def get_all_repositories() -> list[dict]:
    """Collect all public repositories owned by the account."""
    repositories = []

    for page in range(1, 20):
        result = github_get(
            f"/users/{USERNAME}/repos?type=owner&sort=updated",
            page=page,
        )

        if not isinstance(result, list) or not result:
            break

        repositories.extend(result)

        if len(result) < 100:
            break

    # Never store private repositories.
    return [
        repo
        for repo in repositories
        if not repo.get("private", False)
    ]


def get_recent_events() -> list[dict]:
    """Collect the user's recent public GitHub events."""
    events = []

    for page in range(1, 4):
        result = github_get(
            f"/users/{USERNAME}/events/public",
            page=page,
        )

        if not isinstance(result, list) or not result:
            break

        events.extend(result)

        if len(result) < 100:
            break

    return events


def summarize_events(events: list[dict]) -> dict:
    """Turn raw GitHub events into simple activity numbers."""
    today = datetime.now(timezone.utc).date()

    commits = 0
    pushes = 0
    pull_requests = 0
    issues = 0
    recent_events = 0

    for event in events:
        created_at = event.get("created_at")

        if not created_at:
            continue

        try:
            event_date = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            ).date()
        except ValueError:
            continue

        if event_date != today:
            continue

        recent_events += 1

        event_type = event.get("type")

        if event_type == "PushEvent":
            pushes += 1

            commits += len(
                event.get("payload", {}).get("commits", [])
            )

        elif event_type == "PullRequestEvent":
            pull_requests += 1

        elif event_type == "IssuesEvent":
            issues += 1

    # This is OUR derived metric.
    # It is NOT an official GitHub score.
    raw_score = (
        commits
        + (pull_requests * 3)
        + (issues * 2)
        + pushes
    )

    activity_index = min(100, raw_score)

    return {
        "commits": commits,
        "pushes": pushes,
        "pull_requests": pull_requests,
        "issues": issues,
        "recent_events": recent_events,
        "activity_index": activity_index,
    }


def build_repository_records(
    repositories: list[dict],
) -> list[dict]:
    """Keep only the public repository information we need."""
    records = []

    for repo in repositories:
        records.append(
            {
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "stars": repo.get(
                    "stargazers_count",
                    0,
                ),
                "forks": repo.get(
                    "forks_count",
                    0,
                ),
                "open_issues": repo.get(
                    "open_issues_count",
                    0,
                ),
                "watchers": repo.get(
                    "watchers_count",
                    0,
                ),
                "archived": repo.get(
                    "archived",
                    False,
                ),
                "default_branch": repo.get(
                    "default_branch"
                ),
            }
        )

    return records


def load_history() -> dict:
    """Load old snapshots without destroying history."""
    if not HISTORY_FILE.exists():
        return {"snapshots": []}

    try:
        with HISTORY_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except json.JSONDecodeError:
        print(
            "Warning: history file was invalid."
        )
        return {"snapshots": []}


def save_history(history: dict) -> None:
    """Safely write the historical dataset."""
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = HISTORY_FILE.with_suffix(
        ".tmp"
    )

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            history,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_file.replace(
        HISTORY_FILE
    )


def upsert_snapshot(
    history: dict,
    snapshot: dict,
) -> None:
    """Add today's snapshot without creating duplicates."""
    snapshots = history.setdefault(
        "snapshots",
        [],
    )

    snapshots[:] = [
        item
        for item in snapshots
        if item.get("date") != snapshot["date"]
    ]

    snapshots.append(snapshot)

    snapshots.sort(
        key=lambda item: item.get(
            "date",
            "",
        )
    )


def main() -> int:
    print(
        f"Collecting public GitHub data for "
        f"@{USERNAME}..."
    )

    repositories = get_all_repositories()
    events = get_recent_events()

    repository_records = build_repository_records(
        repositories
    )

    activity = summarize_events(events)

    now = datetime.now(timezone.utc)

    snapshot = {
        "date": now.date().isoformat(),
        "collected_at": now.isoformat(),
        "account": USERNAME,
        "repository_count": len(
            repository_records
        ),
        "active_repository_count": sum(
            1
            for repo in repository_records
            if not repo["archived"]
            and repo["pushed_at"]
        ),
        "stars": sum(
            repo["stars"]
            for repo in repository_records
        ),
        "forks": sum(
            repo["forks"]
            for repo in repository_records
        ),
        "repositories": repository_records,
        "activity": activity,
    }

    history = load_history()

    upsert_snapshot(
        history,
        snapshot,
    )

    save_history(history)

    print()
    print("================================")
    print(" CONTROL ROOM DATA COLLECTION")
    print("================================")
    print(
        f"Repositories : "
        f"{snapshot['repository_count']}"
    )
    print(
        f"Active repos : "
        f"{snapshot['active_repository_count']}"
    )
    print(
        f"Stars        : "
        f"{snapshot['stars']}"
    )
    print(
        f"Forks        : "
        f"{snapshot['forks']}"
    )
    print(
        f"Commits      : "
        f"{activity['commits']}"
    )
    print(
        f"Pull requests: "
        f"{activity['pull_requests']}"
    )
    print(
        f"Issues       : "
        f"{activity['issues']}"
    )
    print(
        f"Activity index: "
        f"{activity['activity_index']}/100"
    )
    print()
    print(
        f"History saved to:"
        f"\n{HISTORY_FILE}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
