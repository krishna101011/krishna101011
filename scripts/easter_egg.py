"""
You weren't supposed to find this file.
Since you did, you've earned the right to run it:

    python scripts/easter_egg.py

Also doubles as the pysnake workflow's "post-render check" step - see
.github/workflows/pysnake.yml. Under GitHub Actions it skips the banner
and fortune (nobody wants ASCII art in a CI log) and prints one dry line
instead, for whoever actually reads Actions logs before judging a profile.
"""

import os
import random

FORTUNES = [
    "A mutable default argument once ruined someone's Tuesday. Never yours, I hope.",
    "Dr. Pythonicus says: 'is' checks identity, '==' checks vibes. Know the difference.",
    "You have been debugging for 45 minutes. It is a typo. It is always a typo.",
    "This repo contains more comments about coffee than coffee breaks actually taken.",
]

BANNER = r"""
   ___         ___      _   _                _
  |   \ _ _   | _ \_  _| |_| |_  ___ _ _ _  _(_)__ _  _ ___
  | |) | '_|  |  _/ || |  _| ' \/ _ \ ' \ || | / _| || (_-<
  |___/|_|    |_|  \_, |\__|_||_\___/_||_\_,_|_\__|\_,_/__/
                    |__/
"""

# DRAFT - pick one, see the 3 options in the PR/chat. This is option 3,
# wired in so the workflow has something real to run while you decide.
CI_LOG_LINE = "Still here. The snake is real, the gaps in my commit history are real, and so is this log line."


def main() -> None:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(CI_LOG_LINE)
        return

    print(BANNER)
    print(random.choice(FORTUNES))
    print("\nYou found the easter egg. Star the repo, or don't — I'm a README, not a cop.")


if __name__ == "__main__":
    main()
