"""Download MLS match schedules and results from American Soccer Analysis.

Usage (from the repo root):
    python python/asa_matches.py

Writes data/raw/matches.parquet with every MLS match from config.START_DATE's
season to the current season. The file is rebuilt in full each run (it's
small, and schedules change), so rerunning is idempotent.

Source: American Soccer Analysis API via the itscalledsoccer package.
https://www.americansocceranalysis.com/ — please credit ASA when using this data.
"""

from datetime import datetime, timezone

import duckdb
import pandas as pd
from itscalledsoccer.client import AmericanSoccerAnalysis

import config

# Fields we need from ASA's games endpoint. If ASA renames one, we stop with a
# clear message instead of loading a half-empty table.
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
    seasons = [str(y) for y in range(config.START_DATE.year, this_year + 1)]

    asa = AmericanSoccerAnalysis()
    rows = to_rows(fetch_games(asa, seasons), fetch_team_names(asa))
    save(rows)

    unmapped = rows.loc[rows["home_team_name"].isna() | rows["away_team_name"].isna()]
    print(f"done   {len(rows)} matches for seasons {seasons[0]}-{seasons[-1]}"
          f"; {len(unmapped)} with an unknown team id")


if __name__ == "__main__":
    main()
