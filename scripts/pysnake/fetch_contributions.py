"""Fetches the public GitHub contribution calendar for a user - no auth, no
GraphQL, no personal access token. Just the same public page GitHub renders
at https://github.com/users/<name>/contributions.

That endpoint has changed markup before (SVG rects, then an accessible
<table> of <td> cells). As of this writing it's the latter: each day is a

    <td class="ContributionCalendar-day" data-date="YYYY-MM-DD"
        data-level="0-4" id="contribution-day-component-<row>-<col>">

with the *exact* contribution count living in a sibling element instead of
on the cell itself:

    <tool-tip for="contribution-day-component-<row>-<col>">
        3 contributions on August 4th.
    </tool-tip>
    <tool-tip for="...">No contributions on August 3rd.</tool-tip>

`data-level` is only a 0-4 bucket (GitHub's own heatmap quantization) - not
useful for "top 10% of contribution counts", so this parses the tooltip
text for the real integer instead, joining the two elements on their
id/for pair rather than trying to recover a date from the tooltip's
year-less "August 4th" text.

If GitHub changes this markup again, this fails loudly (see
ContributionFetchError below) instead of quietly returning nothing.
"""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from html.parser import HTMLParser

CONTRIBUTIONS_URL = "https://github.com/users/{username}/contributions"
REQUEST_TIMEOUT_SECONDS = 15

_NO_CONTRIBUTIONS_RE = re.compile(r"^No contributions on")
_COUNT_RE = re.compile(r"^(\d+)\s+contributions?\s+on")


class ContributionFetchError(RuntimeError):
    """Raised whenever the calendar can't be fetched or parsed - callers
    should let this propagate (non-zero exit), never swallow it into an
    empty result."""


class _ContributionCalendarParser(HTMLParser):
    """Two-pass-in-one-pass: collects {cell_id: iso_date} from the <td>
    cells and {cell_id: count} from the <tool-tip> elements that reference
    them by id/for, then fetch_calendar() joins the two."""

    def __init__(self) -> None:
        super().__init__()
        self.dates_by_id: dict[str, str] = {}
        self.counts_by_id: dict[str, int] = {}
        self._tooltip_for: str | None = None
        self._tooltip_text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "td" and "ContributionCalendar-day" in (attrs_dict.get("class") or ""):
            cell_id = attrs_dict.get("id")
            date = attrs_dict.get("data-date")
            if cell_id and date:
                self.dates_by_id[cell_id] = date
        elif tag == "tool-tip":
            self._tooltip_for = attrs_dict.get("for")
            self._tooltip_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._tooltip_for is not None:
            self._tooltip_text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip" and self._tooltip_for is not None:
            text = "".join(self._tooltip_text_parts).strip()
            count = _parse_tooltip_count(text)
            if count is not None:
                self.counts_by_id[self._tooltip_for] = count
            self._tooltip_for = None
            self._tooltip_text_parts = []


def _parse_tooltip_count(text: str) -> int | None:
    if _NO_CONTRIBUTIONS_RE.match(text):
        return 0
    match = _COUNT_RE.match(text)
    return int(match.group(1)) if match else None


def fetch_calendar(username: str) -> list[dict]:
    """Return one entry per day, chronological order:
    {"date": "YYYY-MM-DD", "count": int}.

    Raises ContributionFetchError if the page can't be fetched, or if its
    markup doesn't yield any usable data - never returns an empty list
    silently.
    """
    url = CONTRIBUTIONS_URL.format(username=username)
    request = urllib.request.Request(
        url,
        headers={
            # A plain script UA gets blocked more often than a browser-ish
            # one; this is a public page, not an API call needing a key.
            "User-Agent": (
                "Mozilla/5.0 (compatible; pysnake/1.0; "
                f"+https://github.com/{username}/{username})"
            )
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            html_bytes = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ContributionFetchError(f"could not fetch {url}: {exc}") from exc

    html_text = html_bytes.decode("utf-8", errors="replace")

    parser = _ContributionCalendarParser()
    parser.feed(html_text)

    if not parser.dates_by_id:
        raise ContributionFetchError(
            "found no '.ContributionCalendar-day' cells in the fetched page - "
            "GitHub's markup for /users/<name>/contributions may have changed "
            f"(fetched {len(html_text)} bytes from {url})"
        )

    if not parser.counts_by_id:
        raise ContributionFetchError(
            "found calendar cells but no parseable <tool-tip> contribution "
            "counts - the tooltip text format may have changed"
        )

    days = [
        {"date": date, "count": parser.counts_by_id.get(cell_id, 0)}
        for cell_id, date in parser.dates_by_id.items()
    ]
    days.sort(key=lambda d: d["date"])
    return days


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("usage: python -m scripts.pysnake.fetch_contributions <github-username>", file=sys.stderr)
        raise SystemExit(2)

    try:
        result = fetch_calendar(sys.argv[1])
    except ContributionFetchError as exc:
        print(f"fetch_contributions: {exc}", file=sys.stderr)
        raise SystemExit(1)

    print(json.dumps(result, indent=2))
