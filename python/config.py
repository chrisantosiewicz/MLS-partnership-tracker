"""Shared settings: file paths, the backfill start date, and the HTTP User-Agent."""

from datetime import date
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PAGEVIEWS_FILE = RAW_DIR / "pageviews.parquet"
MATCHES_FILE = RAW_DIR / "matches.parquet"

# Backfill pageviews and matches from this date.
START_DATE = date(2023, 1, 1)

# Wikimedia requires a User-Agent that says who we are and how to reach us.
# Format they ask for: <client>/<version> (<contact>) <library>/<version>
USER_AGENT = (
    "MLSPartnershipTracker/0.1 "
    "(https://github.com/chrisantosiewicz/MLS-partnership-tracker) "
    "python-requests"
)

# Column layouts of the raw files. Writing an empty file with these columns
# lets the SQL build run before the first ingestion.
PAGEVIEWS_COLUMNS = "article VARCHAR, view_date DATE, views BIGINT, fetched_at TIMESTAMP"
MATCHES_COLUMNS = (
    "game_id VARCHAR, kickoff_utc TIMESTAMP, season INTEGER, "
    "home_team_name VARCHAR, away_team_name VARCHAR, "
    "home_score INTEGER, away_score INTEGER, status VARCHAR"
)


def ensure_raw_files() -> None:
    """Create empty raw Parquet files if they don't exist yet."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for path, columns in [(PAGEVIEWS_FILE, PAGEVIEWS_COLUMNS), (MATCHES_FILE, MATCHES_COLUMNS)]:
        if not path.exists():
            con = duckdb.connect()
            con.execute(f"CREATE TABLE empty ({columns})")
            con.execute(f"COPY empty TO '{path.as_posix()}' (FORMAT parquet)")
            con.close()
