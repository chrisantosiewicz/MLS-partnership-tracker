-- Every match team must map to one of our clubs (via asa_team_name).
-- Matches before 2023 are ignored: they can include defunct clubs.
SELECT match_id, match_date_utc, home_club_id, away_club_id
FROM dim_match
WHERE season >= 2023
  AND (home_club_id IS NULL OR away_club_id IS NULL);
