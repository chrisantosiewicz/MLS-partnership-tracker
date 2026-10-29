"""Unit tests for wiki_pageviews.py. No network: API responses are faked."""

from datetime import date

import duckdb
import pytest

import config
import wiki_pageviews as wp


def test_build_url_encodes_title():
    url = wp.build_url("CF Montréal", date(2025, 1, 1), date(2025, 1, 31))
    assert "/CF_Montr%C3%A9al/daily/20250101/20250131" in url


def test_build_url_encodes_slash_and_parentheses():
    url = wp.build_url("AC/DC (band)", date(2025, 1, 1), date(2025, 1, 2))
    assert "/AC%2FDC_%28band%29/" in url


def test_parse_items():
    payload = {"items": [
        {"article": "Toronto_FC", "timestamp": "2025060100", "views": 812},
        {"article": "Toronto_FC", "timestamp": "2025060200", "views": 790},
    ]}
    rows = wp.parse_items("Toronto FC", payload)
    assert rows == [
        {"article": "Toronto FC", "view_date": date(2025, 6, 1), "views": 812},
        {"article": "Toronto FC", "view_date": date(2025, 6, 2), "views": 790},
    ]


def test_next_start_backfills_new_article():
    assert wp.next_start("New Article", {}) == config.START_DATE


def test_next_start_continues_after_last_day():
    assert wp.next_start("Toronto FC", {"Toronto FC": date(2025, 6, 2)}) == date(2025, 6, 3)


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, response):
        self.response = response

    def get(self, url, timeout):
        return self.response


def test_fetch_article_404_returns_no_rows():
    rows = wp.fetch_article(FakeSession(FakeResponse(404)), "Not A Real Title",
                            date(2025, 1, 1), date(2025, 1, 2))
    assert rows == []


@pytest.fixture
def temp_pageviews(tmp_path, monkeypatch):
    """Point config at an empty pageviews file in a temp folder."""
    monkeypatch.setattr(config, "RAW_DIR", tmp_path)
    monkeypatch.setattr(config, "PAGEVIEWS_FILE", tmp_path / "pageviews.parquet")
    monkeypatch.setattr(config, "MATCHES_FILE", tmp_path / "matches.parquet")
    config.ensure_raw_files()
    return tmp_path / "pageviews.parquet"


def test_merge_is_idempotent(temp_pageviews):
    rows = [
        {"article": "Toronto FC", "view_date": date(2025, 6, 1), "views": 812},
        {"article": "Toronto FC", "view_date": date(2025, 6, 2), "views": 790},
    ]
    con = duckdb.connect()
    assert wp.merge_and_save(con, rows) == 2
    # Loading the same days again must not add rows.
    assert wp.merge_and_save(con, rows) == 2
    # And loading nothing new keeps what we have.
    assert wp.merge_and_save(con, []) == 2


def test_merge_keeps_latest_fetch(temp_pageviews):
    con = duckdb.connect()
    wp.merge_and_save(con, [{"article": "A", "view_date": date(2025, 6, 1), "views": 10}])
    wp.merge_and_save(con, [{"article": "A", "view_date": date(2025, 6, 1), "views": 12}])
    views = con.execute(f"SELECT views FROM read_parquet('{temp_pageviews}')").fetchall()
    assert views == [(12,)]
