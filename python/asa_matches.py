"""Download MLS match schedules and results from American Soccer Analysis.

Usage (from the repo root):
    python python/asa_matches.py

Writes data/raw/matches.parquet with every MLS match from config.START_DATE's
season to the current season.

Incremental by season: the first run fetches every season; later runs only
re-fetch the current season (where schedules and scores change) and keep the
older seasons already saved. Rerunning is idempotent.

If ASA is slow or down, we retry a few times. If it still fails and we already
have a matches file, we keep yesterday's file and warn instead of failing the
whole daily build: one day of stale match data is better than no page.

Source: American Soccer Analysis API via the itscalledsoccer package.
https://www.americansocceranalysis.com/ — please credit ASA when using this data.
"""

import time
from datetime import datetime, timezone

import duckdb
import pandas as pd
from itscalledsoccer.client import AmericanSoccerAnalysis

import config

# Fields we need from ASA's games endpoint. If ASA renames one, we stop with a
# clear message instead of loading a half-empty table.
ATTEMPTS = 3
WAIT_SECONDS = 30  # between attempts: 30s, then 60s

REQUIRED_FIELDS = [
    "game_id", "date_time_utc", "home_team_id", "away_team_id",
    "home_score", "away_score", "season_name", "status",
]


def fetch_games(asa: AmericanSoccerAnalysis, seasons: list[str]) -> list[dict]:
    """All MLS games for the given seasons, as a list of dicts."""
    games = asa.get_games(leagues="mls", season_name=seasons)
    return games.to_dicts()


def fetch_team_names(asa: AmericanSoccerAnalysis) -> dict[str, str]:
    """ASA team_id -> team_name for MLS."""
    teams = asa.get_teams(leagues="mls")
    return {t["team_id"]: t["team_name"] for t in teams.to_dicts()}


def to_rows(games: list[dict], team_names: dict[str, str]) -> pd.DataFrame:
    """Keep the fields we use and swap team ids for names."""
    if games:
        missing = [f for f in REQUIRED_FIELDS if f not in games[0]]
        if missing:
            raise KeyError(f"ASA games response is missing fields: {missing}. "
                           f"Fields returned: {sorted(games[0])}")

    rows = pd.DataFrame(
        {
            "game_id": [g["game_id"] for g in games],
            # ASA sends e.g. '2025-03-01 19:30:00 UTC'; store as a UTC timestamp.
            "kickoff_utc": [
                pd.to_datetime(str(g["date_time_utc"]).replace(" UTC", ""), utc=True).tz_localize(None)
                for g in games
            ],
            "season": [int(g["season_name"]) for g in games],
            "home_team_name": [team_names.get(g["home_team_id"]) for g in games],
            "away_team_name": [team_names.get(g["away_team_id"]) for g in games],
            "home_score": [g["home_score"] for g in games],
            "away_score": [g["away_score"] for g in games],
            "status": [g["status"] for g in games],
        }
    )
    # Scores are empty for matches not played yet; keep them as nullable ints.
    for col in ["home_score", "away_score"]:
        rows[col] = rows[col].astype("Int64")
    return rows


def saved_seasons() -> set[int]:
    """Seasons already in matches.parquet (empty set if the file is missing)."""
    if not config.MATCHES_FILE.exists():
        return set()
    con = duckdb.connect()
    rows = con.execute(
        "SELECT DISTINCT season FROM read_parquet(?)", [str(config.MATCHES_FILE)]
    ).fetchall()
    con.close()
    return {season for (season,) in rows}


def seasons_to_fetch(this_year: int, already_saved: set[int]) -> list[int]:
    """Every season on the first run; afterwards only the current one."""
    all_seasons = list(range(config.START_DATE.year, this_year + 1))
    missing = [s for s in all_seasons if s not in already_saved]
    return sorted(set(missing) | {this_year})


def keep_other_seasons(new_rows: pd.DataFrame, fetched: list[int]) -> pd.DataFrame:
    """Add back saved rows for the seasons we didn't re-fetch."""
    if not config.MATCHES_FILE.exists():
        return new_rows
    con = duckdb.connect()
    old = con.execute(
        "SELECT * FROM read_parquet(?) WHERE NOT list_contains(?, season)",
        [str(config.MATCHES_FILE), fetched],
    ).fetchdf()
    con.close()
    for col in ["home_score", "away_score"]:
        old[col] = old[col].astype("Int64")
    return pd.concat([old, new_rows], ignore_index=True)


def fetch_with_retries(seasons: list[int]) -> pd.DataFrame:
    """Fetch and convert, retrying on timeouts and connection errors."""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            asa = AmericanSoccerAnalysis(request_timeout=90)
            return to_rows(fetch_games(asa, [str(s) for s in seasons]), fetch_team_names(asa))
        except Exception as err:  # the ASA client raises several error types
            if attempt == ATTEMPTS:
                raise
            wait = WAIT_SECONDS * attempt
            print(f"WARN   ASA attempt {attempt} failed ({type(err).__name__}); retrying in {wait}s")
            time.sleep(wait)


def save(rows: pd.DataFrame) -> None:
    """Overwrite matches.parquet with the column types in config.MATCHES_COLUMNS."""
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"CREATE TABLE matches ({config.MATCHES_COLUMNS})")
    con.register("rows_df", rows)
    con.execute("INSERT INTO matches SELECT * FROM rows_df ORDER BY kickoff_utc")
    tmp = config.MATCHES_FILE.with_suffix(".tmp.parquet")
    con.execute(f"COPY matches TO '{tmp.as_posix()}' (FORMAT parquet)")
    tmp.replace(config.MATCHES_FILE)
    con.close()


def main() -> None:
    this_year = datetime.now(timezone.utc).year
    already_saved = saved_seasons()
    seasons = seasons_to_fetch(this_year, already_saved)

    try:
        fetched = fetch_with_retries(seasons)
    except Exception as err:
        if already_saved:
            print(f"WARN   ASA unavailable ({type(err).__name__}); keeping saved matches")
            return
        raise  # no saved file to fall back on

    rows = keep_other_seasons(fetched, seasons)
    save(rows)

    unmapped = rows.loc[rows["home_team_name"].isna() | rows["away_team_name"].isna()]
    print(f"done   fetched seasons {seasons}; {len(rows)} matches saved"
          f"; {len(unmapped)} with an unknown team id")


if __name__ == "__main__":
    main()
