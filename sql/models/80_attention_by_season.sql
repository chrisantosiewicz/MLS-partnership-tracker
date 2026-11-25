-- mart_attention_by_season: which clubs are gaining public attention
-- compared with last year?
--
-- Grain: one row per club per calendar year.
-- Like-for-like window: every year runs from Jan 1 to the same day of year as
-- the latest data, so a partial current year isn't compared with a full one.
-- DAYOFYEAR shifts by one day after Feb 28 in a leap year (2024); one day in
-- ~300 moves an average by well under 1%, so it's accepted.
-- A club's first year has no previous year (NULL change), e.g. San Diego 2025.

CREATE TABLE mart_attention_by_season AS
WITH cutoff AS (
    SELECT DAYOFYEAR(MAX(view_date)) AS last_doy FROM mart_attention_daily
),
yearly AS (
    SELECT a.entity_id AS club_id,
           YEAR(a.view_date) AS season,
           AVG(a.views) AS avg_daily_views,
           COUNT(*) AS days
    FROM mart_attention_daily AS a, cutoff
    WHERE a.entity_type = 'club'
      AND DAYOFYEAR(a.view_date) <= cutoff.last_doy
    GROUP BY ALL
)
SELECT
    club_id,
    season,
    avg_daily_views,
    days,
    LAG(avg_daily_views) OVER w                      AS prev_avg_daily_views,
    avg_daily_views / LAG(avg_daily_views) OVER w - 1 AS change_vs_prev
FROM yearly
WINDOW w AS (PARTITION BY club_id ORDER BY season);
