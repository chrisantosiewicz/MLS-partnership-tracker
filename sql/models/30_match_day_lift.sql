-- mart_match_day_lift: how much more attention a club's Wikipedia article
-- gets on a match day than its usual (28-day baseline) level.
--
-- Grain: one row per club per match (each match appears twice: home and away).
-- Only completed matches are included.
--
-- Which pageview day is "the match day"? Pageviews are counted per UTC day.
-- A 7:30 pm ET kickoff is 23:30 UTC, so almost the whole match and the
-- evening after it fall on the NEXT UTC day. Using the UTC date of kickoff
-- (the v0.1 rule) missed the attention for about a third of club-matches.
-- attention_date_utc = UTC date two hours after kickoff (roughly full time):
-- an afternoon kickoff stays on its own day, an evening one in the Americas
-- moves to the UTC day that holds the match and its aftermath.

CREATE TABLE mart_match_day_lift AS
WITH club_matches AS (       -- unpivot home/away into one row per club
    SELECT match_id, match_date_utc,
           CAST(kickoff_utc + INTERVAL 2 HOUR AS DATE) AS attention_date_utc, season,
           home_club_id AS club_id, away_club_id AS opponent_club_id, 'home' AS venue
    FROM dim_match
    WHERE status = 'FullTime'
    UNION ALL
    SELECT match_id, match_date_utc,
           CAST(kickoff_utc + INTERVAL 2 HOUR AS DATE), season,
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
    cm.attention_date_utc,
    a.views,
    a.baseline_28d,
    a.lift_vs_baseline
FROM club_matches AS cm
JOIN mart_attention_daily AS a
  ON a.entity_type = 'club'
 AND a.entity_id   = cm.club_id
 AND a.view_date   = cm.attention_date_utc;
