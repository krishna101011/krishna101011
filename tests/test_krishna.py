"""Structural tests only — language_breakdown() and currently_building()
hit live data (a real GitHub API call, a real file on disk), so these check
shape, not exact values.
"""
import pytest

import krishna


def test_whoami_returns_a_non_empty_string():
    result = krishna.whoami()
    assert isinstance(result, str)
    assert result


def test_currently_building_returns_a_non_empty_string():
    result = krishna.currently_building()
    assert isinstance(result, str)
    assert result


def test_skills_is_a_dict_of_non_empty_strings():
    assert isinstance(krishna.skills, dict)
    assert krishna.skills
    for key, value in krishna.skills.items():
        assert isinstance(key, str) and key
        assert isinstance(value, str) and value


def test_projects_is_a_list():
    assert isinstance(krishna.projects, list)


def test_language_breakdown_returns_percentages_summing_near_100():
    result = krishna.language_breakdown()
    assert isinstance(result, dict)
    if not result:
        pytest.skip("GitHub API returned no language data for any public repo")

    total = 0.0
    for language, pct in result.items():
        assert isinstance(language, str) and language
        assert isinstance(pct, float)
        assert 0.0 <= pct <= 100.0
        total += pct
    assert 95.0 <= total <= 100.5  # per-language rounding can drift it slightly off 100


def test_snake_render_returns_a_non_empty_string():
    result = krishna.snake.render()
    assert isinstance(result, str)
    assert result


def test_repo_count_returns_a_positive_int():
    result = krishna.repo_count()
    assert isinstance(result, int)
    assert result >= 1  # this profile repo is always at least one of them
