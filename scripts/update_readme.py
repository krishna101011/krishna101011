"""
Pulls the most recent public push event for GH_USERNAME and writes the
"currently building" status line to currently_building.txt, which
krishna.py's currently_building() reads.

Runs unattended inside GitHub Actions — see .github/workflows/update-readme.yml
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

USERNAME = os.environ.get("GH_USERNAME")
TOKEN = os.environ.get("GITHUB_TOKEN")

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "currently_building.txt"


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
        return "heads down, nothing pushed publicly this week"
    msg = event["message"][:72]
    return f'{event["repo"]} — "{msg}" ({relative_time(event["created_at"])})'


def update_currently_building_file(line: str) -> bool:
    previous = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else None
    if previous == line:
        return False

    OUTPUT_PATH.write_text(line, encoding="utf-8")
    return True


def main() -> None:
    if not USERNAME:
        print("GH_USERNAME not set", file=sys.stderr)
        sys.exit(1)

    event = fetch_latest_push()
    line = build_line(event)
    changed = update_currently_building_file(line)
    print("currently_building.txt updated." if changed else "No change needed.")


if __name__ == "__main__":
    main()
