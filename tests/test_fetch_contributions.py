"""fetch_contributions.py depends on specific attribute names in GitHub's
public contribution-calendar HTML. These tests mock the network call so
they run offline, and check that markup drift is caught with a clear
message rather than silently parsed into nothing."""
import pytest

from scripts.pysnake import fetch_contributions

WELL_FORMED_HTML = """
<table>
  <td class="ContributionCalendar-day" data-date="2025-01-01" data-level="1"
      id="contribution-day-component-0-0"></td>
  <td class="ContributionCalendar-day" data-date="2025-01-02" data-level="0"
      id="contribution-day-component-0-1"></td>
</table>
<tool-tip for="contribution-day-component-0-0">3 contributions on January 1st.</tool-tip>
<tool-tip for="contribution-day-component-0-1">No contributions on January 2nd.</tool-tip>
"""

# The class name survived, but the date attribute was renamed — exactly the
# kind of partial drift that used to produce a misleading "found no cells"
# error even though cells actually were found.
MARKUP_WITH_RENAMED_DATE_ATTRIBUTE = """
<table>
  <td class="ContributionCalendar-day" data-day="2025-01-01" data-level="1"
      id="contribution-day-component-0-0"></td>
</table>
"""


class _FakeResponse:
    def __init__(self, data: bytes):
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self) -> bytes:
        return self._data


def _mock_urlopen(monkeypatch, html: str) -> None:
    def fake_urlopen(request, timeout=None):
        return _FakeResponse(html.encode("utf-8"))

    monkeypatch.setattr(fetch_contributions.urllib.request, "urlopen", fake_urlopen)


def test_well_formed_markup_parses_successfully(monkeypatch):
    _mock_urlopen(monkeypatch, WELL_FORMED_HTML)
    days = fetch_contributions.fetch_calendar("someuser")
    assert days == [
        {"date": "2025-01-01", "count": 3},
        {"date": "2025-01-02", "count": 0},
    ]


def test_renamed_date_attribute_raises_a_clear_markup_drift_error(monkeypatch):
    _mock_urlopen(monkeypatch, MARKUP_WITH_RENAMED_DATE_ATTRIBUTE)
    with pytest.raises(
        fetch_contributions.ContributionFetchError,
        match="GitHub's calendar markup changed",
    ):
        fetch_contributions.fetch_calendar("someuser")
