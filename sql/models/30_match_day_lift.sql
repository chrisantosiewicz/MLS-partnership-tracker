-- mart_match_day_lift: how much more attention a club's Wikipedia article
-- gets on a match day than its usual (28-day baseline) level.
--
-- Grain: one row per club per match (each match appears twice: home and away).
-- Match day = the UTC date of kickoff, the same clock the Pageviews API uses.
-- Only completed matches are included.

CREATE TABLE mart_match_day_lift AS
WITH club_matches AS (       -- unpivot home/away into one row per club
    SELECT match_id, match_date_utc, season,
           home_club_id AS club_id, away_club_id AS opponent_club_id, 'home' AS venue
    FROM dim_match
    WHERE status = 'FullTime'
    UNION ALL
    SELECT match_id, match_date_utc, season,
           away_club_id, home_club_id, 'away'
    FROM dim_match
    WHERE status = 'FullTime'
)
SELECT
    cm.match_id,
    cm.club_id,
    cm.opponent_club_id,
    cm.venue,
    cm.season,
    cm.match_date_utc,
    a.views,
    a.baseline_28d,
    a.lift_vs_baseline
FROM club_matches AS cm
JOIN mart_attention_daily AS a
  ON a.entity_type = 'club'
 AND a.entity_id   = cm.club_id
 AND a.view_date   = cm.match_date_utc;
