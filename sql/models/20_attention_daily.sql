-- mart_attention_daily: daily Wikipedia pageviews for every club and brand,
-- with a 28-day trailing baseline.
--
-- Grain: one row per entity (club or brand) per UTC day.
--
-- Why a date spine: the Pageviews API can skip days with no views. A window
-- of "28 PRECEDING ROWS" over gappy data would cover more than 28 days, so we
-- first build one row per day per entity and fill missing days with 0.
--
-- Baseline = average of the 28 days BEFORE the current day (the current day is
-- excluded so a spike doesn't inflate its own baseline). It stays NULL until
-- there are 28 prior days.

CREATE TABLE mart_attention_daily AS
WITH entities AS (           -- one row per thing we track, with its article
    SELECT 'club' AS entity_type, club_id AS entity_id, wikipedia_article AS article
    FROM dim_club
    UNION ALL
    SELECT 'brand', brand_id, wikipedia_article
    FROM dim_brand
    WHERE wikipedia_article IS NOT NULL
),
article_span AS (            -- first and last day we have data for each article
    SELECT article, MIN(view_date) AS first_day, MAX(view_date) AS last_day
    FROM fact_pageviews_daily
    GROUP BY article
),
spine AS (                   -- every day in each article's span
    SELECT e.entity_type, e.entity_id, e.article,
           CAST(UNNEST(GENERATE_SERIES(s.first_day, s.last_day, INTERVAL 1 DAY)) AS DATE) AS view_date
    FROM entities AS e
    JOIN article_span AS s USING (article)
),
filled AS (                  -- attach views; missing day = 0 views
    SELECT sp.entity_type, sp.entity_id, sp.article, sp.view_date,
           COALESCE(f.views, 0) AS views
    FROM spine AS sp
    LEFT JOIN fact_pageviews_daily AS f
           ON f.article = sp.article AND f.view_date = sp.view_date
),
with_baseline AS (
    SELECT *,
           AVG(views) OVER w   AS baseline_avg,
           COUNT(*)   OVER w   AS baseline_days
    FROM filled
    WINDOW w AS (PARTITION BY entity_type, entity_id
                 ORDER BY view_date
                 ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING)
)
SELECT
    entity_type, entity_id, article, view_date, views,
    CASE WHEN baseline_days = 28 THEN baseline_avg END            AS baseline_28d,
    CASE WHEN baseline_days = 28 AND baseline_avg > 0
         THEN views / baseline_avg - 1 END                         AS lift_vs_baseline
FROM with_baseline;
