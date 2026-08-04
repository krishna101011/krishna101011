"""
Pulls the most recent public push event for GH_USERNAME and rewrites the
"currently building" block in README.md between two marker lines.

Runs unattended inside GitHub Actions — see .github/workflows/update-readme.yml
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone

import requests

USERNAME = os.environ.get("GH_USERNAME")
TOKEN = os.environ.get("GITHUB_TOKEN")

README_PATH = "README.md"
START_MARKER = "# CURRENT:START"
END_MARKER = "# CURRENT:END"


def fetch_latest_push() -> dict | None:
    """Return the most recent PushEvent outside the profile repo, or None."""
    url = f"https://api.github.com/users/{USERNAME}/events/public"
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    profile_repo = f"{USERNAME}/{USERNAME}"

    for event in resp.json():
        if event["type"] != "PushEvent":
            continue
        if event["repo"]["name"] == profile_repo:
            continue
        commits = event.get("payload", {}).get("commits", [])
        if not commits:
            continue
        return {
            "repo": event["repo"]["name"].split("/")[-1],
            "message": commits[-1]["message"].splitlines()[0],
            "created_at": event["created_at"],
        }
    return None


def relative_time(iso_ts: str) -> str:
    then = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    hours = int((datetime.now(timezone.utc) - then).total_seconds() // 3600)
    if hours < 1:
        return "just now"
    if hours < 24:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"


def build_line(event: dict | None) -> str:
    if event is None:
        return "$ status: heads down, nothing pushed publicly this week"
    msg = event["message"][:72]
    return f'$ status: {event["repo"]} — "{msg}" ({relative_time(event["created_at"])})'


def update_readme(line: str) -> bool:
    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
    )
    replacement = f"{START_MARKER}\n{line}\n{END_MARKER}"

    if not pattern.search(content):
        print(f"Markers not found in {README_PATH}", file=sys.stderr)
        return False

    new_content = pattern.sub(replacement, content)
    if new_content == content:
        return False

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main() -> None:
    if not USERNAME:
        print("GH_USERNAME not set", file=sys.stderr)
        sys.exit(1)

    event = fetch_latest_push()
    line = build_line(event)
    changed = update_readme(line)
    print("README updated." if changed else "No change needed.")


if __name__ == "__main__":
    main()
