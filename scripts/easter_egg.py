"""
You weren't supposed to find this file.
Since you did, you've earned the right to run it:

    python scripts/easter_egg.py
"""

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


def main() -> None:
    print(BANNER)
    print(random.choice(FORTUNES))
    print("\nYou found the easter egg. Star the repo, or don't — I'm a README, not a cop.")


if __name__ == "__main__":
    main()
