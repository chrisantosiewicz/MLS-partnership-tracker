"""Unit tests for asa_matches.py. No network: ASA responses are faked."""

import pandas as pd
import pytest

import asa_matches as asa

TEAMS = {"t1": "Chicago Fire FC", "t2": "St. Louis City SC"}


def game(**overrides):
    base = {
        "game_id": "g1", "date_time_utc": "2025-03-01 19:30:00 UTC",
        "home_team_id": "t1", "away_team_id": "t2",
        "home_score": 2, "away_score": 1, "season_name": "2025", "status": "FullTime",
    }
    return {**base, **overrides}


def test_to_rows_maps_names_and_parses_time():
    rows = asa.to_rows([game()], TEAMS)
    row = rows.iloc[0]
    assert row["home_team_name"] == "Chicago Fire FC"
    assert row["away_team_name"] == "St. Louis City SC"
    assert row["kickoff_utc"] == pd.Timestamp("2025-03-01 19:30:00")
    assert row["season"] == 2025


def test_to_rows_keeps_unplayed_scores_empty():
    rows = asa.to_rows([game(home_score=None, away_score=None, status="PreMatch")], TEAMS)
    assert pd.isna(rows.iloc[0]["home_score"])


def test_to_rows_fails_loudly_on_missing_field():
    bad = game()
    del bad["status"]
    with pytest.raises(KeyError, match="status"):
        asa.to_rows([bad], TEAMS)


def test_first_run_fetches_every_season():
    assert asa.seasons_to_fetch(2026, set()) == [2023, 2024, 2025, 2026]


def test_later_runs_fetch_only_current_season():
    assert asa.seasons_to_fetch(2026, {2023, 2024, 2025, 2026}) == [2026]


def test_new_year_fetches_new_season():
    assert asa.seasons_to_fetch(2027, {2023, 2024, 2025, 2026}) == [2027]


def test_keep_other_seasons_replaces_only_fetched(tmp_path, monkeypatch):
    import config
    monkeypatch.setattr(config, "RAW_DIR", tmp_path)
    monkeypatch.setattr(config, "MATCHES_FILE", tmp_path / "matches.parquet")
    old = asa.to_rows([game(game_id="old25", season_name="2025"),
                       game(game_id="old26", season_name="2026", status="PreMatch")], TEAMS)
    asa.save(old)
    new = asa.to_rows([game(game_id="old26", season_name="2026", status="FullTime")], TEAMS)
    merged = asa.keep_other_seasons(new, [2026])
    assert sorted(merged["game_id"]) == ["old25", "old26"]
    assert merged.loc[merged["game_id"] == "old26", "status"].item() == "FullTime"
    asa.save(merged)  # merged frame must still match the file's column types
