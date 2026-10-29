"""Download daily Wikipedia pageviews for every club and brand article.

Usage (from the repo root):
    python python/wiki_pageviews.py

How it works:
  - The article list comes from data/clubs.csv and data/brands.csv.
  - Results are kept in data/raw/pageviews.parquet (one row per article per day).
  - Incremental: for each article we only ask for days after the last day we
    already have. A new article is backfilled from config.START_DATE.
  - Idempotent: running it twice in a row adds nothing the second time, and
    if a day is somehow fetched twice, the merge keeps one row per article-day.

Source: Wikimedia Analytics API (pageviews), data released under CC0.
https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/
"""

import csv
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote

import duckdb
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

API_URL = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
    "en.wikipedia/all-access/user/{title}/daily/{start}/{end}"
)
# "user" = people only; this filters out known bots and crawlers.

PAUSE_SECONDS = 0.2  # be polite: one request at a time, small gap between them


def load_articles() -> list[str]:
    """Return every distinct Wikipedia article named in clubs.csv and brands.csv."""
    articles = set()
    for filename in ["clubs.csv", "brands.csv"]:
        with open(config.DATA_DIR / filename, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                title = (row.get("wikipedia_article") or "").strip()
                if title:
                    articles.add(title)
    return sorted(articles)


def make_session() -> requests.Session:
    """HTTP session with our User-Agent and automatic retries.

    Retries up to 5 times on rate limiting (429) and server errors (5xx),
    waiting 1s, 2s, 4s, ... between tries and honouring Retry-After.
    """
    session = requests.Session()
    session.headers["User-Agent"] = config.USER_AGENT
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        respect_retry_after_header=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def build_url(article: str, start: date, end: date) -> str:
    """API URL for one article. Spaces become underscores; other characters
    (é, /, parentheses) are percent-encoded."""
    title = quote(article.replace(" ", "_"), safe="")
    return API_URL.format(title=title, start=start.strftime("%Y%m%d"), end=end.strftime("%Y%m%d"))


def parse_items(article: str, payload: dict) -> list[dict]:
    """Turn the API's JSON into rows. timestamp looks like '2025060100'."""
    return [
        {
            "article": article,
            "view_date": datetime.strptime(item["timestamp"][:8], "%Y%m%d").date(),
            "views": int(item["views"]),
        }
        for item in payload.get("items", [])
    ]


def fetch_article(session: requests.Session, article: str, start: date, end: date) -> list[dict]:
    """Daily views for one article between start and end (inclusive).

    A 404 means Wikimedia has no data for that title in the range, usually a
    wrong or renamed article title. We warn and return no rows rather than
    stopping the whole run; tests/test_pageviews_every_article_loaded.sql
    will then flag the article.
    """
    response = session.get(build_url(article, start, end), timeout=30)
    if response.status_code == 404:
        print(f"WARN   no data for '{article}' ({start} to {end})")
        return []
    response.raise_for_status()
    return parse_items(article, response.json())


def last_loaded_day(con: duckdb.DuckDBPyConnection) -> dict[str, date]:
    """Latest view_date we already have for each article."""
    rows = con.execute(
        "SELECT article, MAX(view_date) FROM read_parquet(?) GROUP BY article",
        [str(config.PAGEVIEWS_FILE)],
    ).fetchall()
    return {article: last_day for article, last_day in rows}


def next_start(article: str, last_days: dict[str, date]) -> date:
    """First day to request: the day after our last row, or the backfill start."""
    if article in last_days:
        return last_days[article] + timedelta(days=1)
    return config.START_DATE


def merge_and_save(con: duckdb.DuckDBPyConnection, new_rows: list[dict]) -> int:
    """Combine existing and new rows, keep one row per article-day (the most
    recently fetched), and rewrite the Parquet file. Returns total row count."""
    fetched_at = datetime.now(timezone.utc).replace(tzinfo=None)
    new = pd.DataFrame(new_rows, columns=["article", "view_date", "views"])
    new["fetched_at"] = fetched_at
    con.register("new_rows", new)

    con.execute(
        f"""
        CREATE OR REPLACE TABLE merged AS
        WITH combined AS (
            SELECT article, view_date, views, fetched_at
            FROM read_parquet('{config.PAGEVIEWS_FILE.as_posix()}')
            UNION ALL
            SELECT article, CAST(view_date AS DATE), CAST(views AS BIGINT),
                   CAST(fetched_at AS TIMESTAMP)
            FROM new_rows
        )
        SELECT article, view_date, views, fetched_at
        FROM combined
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY article, view_date ORDER BY fetched_at DESC
        ) = 1
        ORDER BY article, view_date
        """
    )
    # Write to a temp file first, then swap, so a crash never leaves a half file.
    tmp = config.PAGEVIEWS_FILE.with_suffix(".tmp.parquet")
    con.execute(f"COPY merged TO '{tmp.as_posix()}' (FORMAT parquet)")
    tmp.replace(config.PAGEVIEWS_FILE)
    return con.execute("SELECT COUNT(*) FROM merged").fetchall()[0][0]


def main() -> None:
    config.ensure_raw_files()
    con = duckdb.connect()
    last_days = last_loaded_day(con)

    # Pageviews for a day are published the following day, so stop at yesterday (UTC).
    end = datetime.now(timezone.utc).date() - timedelta(days=1)

    session = make_session()
    new_rows: list[dict] = []
    for article in load_articles():
        start = next_start(article, last_days)
        if start > end:
            continue  # already up to date
        rows = fetch_article(session, article, start, end)
        print(f"fetch  {article}: {len(rows)} day(s) from {start}")
        new_rows.extend(rows)
        time.sleep(PAUSE_SECONDS)

    total = merge_and_save(con, new_rows)
    print(f"done   {len(new_rows)} new row(s); {total} rows in {config.PAGEVIEWS_FILE.name}")


if __name__ == "__main__":
    main()
