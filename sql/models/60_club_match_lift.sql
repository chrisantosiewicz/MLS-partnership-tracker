-- mart_club_match_lift: which clubs' Wikipedia pages get the biggest bump on
-- match day, home and away?
--
-- Grain: one row per club per season.
-- Median, not average: one viral day (Inter Miami, 2023) would dominate a
-- mean. Rows with a NULL lift (no full 28-day baseline yet) are left out.

CREATE TABLE mart_club_match_lift AS
SELECT
    club_id,
    season,
    COUNT(*)                                                 AS matches,
    MEDIAN(lift_vs_baseline)                                 AS median_lift,
    MEDIAN(lift_vs_baseline) FILTER (WHERE venue = 'home')   AS median_lift_home,
    MEDIAN(lift_vs_baseline) FILTER (WHERE venue = 'away')   AS median_lift_away
FROM mart_match_day_lift
WHERE lift_vs_baseline IS NOT NULL
GROUP BY club_id, season;
