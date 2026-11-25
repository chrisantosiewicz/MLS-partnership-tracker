-- mart_sponsor_match_day_attention: does a sponsor brand's Wikipedia page get
-- more attention on its club's match days than on comparable non-match days?
--
-- Grain: one row per club x sponsor brand (assets pooled), for brands with a
-- Wikipedia article, over the span the brand sponsored the club.
--
-- The trap this model avoids: most MLS matches fall on a UTC Sunday (Saturday
-- evening in the US), and company pages get ~15% fewer views at weekends. A
-- naive "match day vs baseline" comparison makes every sponsor look ignored on
-- match day. So each match day is compared with the brand's own non-match days
-- on the SAME weekday during the deal:
--   excess = match-day lift - median lift on non-match days, same weekday.
-- days_above_norm feeds a sign test in site/charts.py (under no effect, about
-- half of match days land above the weekday norm).
--
-- Deal span comes from partnership_history (as-of join on valid_from and
-- valid_to), so a brand only counts on match days while it held the asset.
-- Public attention only: this says nothing about sponsorship value.

CREATE TABLE mart_sponsor_match_day_attention AS
WITH last_day AS (
    SELECT MAX(view_date) AS d FROM mart_attention_daily
),
deals AS (                   -- one row per club x brand, assets pooled
    SELECT ph.club_id, ph.brand_id,
           STRING_AGG(DISTINCT a.asset_name, ', ')   AS assets,
           MIN(ph.valid_from)                        AS deal_from,
           LEAST(MAX(ph.valid_to), MAX(ld.d))        AS deal_to
    FROM partnership_history AS ph
    JOIN dim_brand AS b USING (brand_id)
    JOIN dim_asset AS a USING (asset_id)
    CROSS JOIN last_day AS ld
    WHERE b.wikipedia_article IS NOT NULL
    GROUP BY ph.club_id, ph.brand_id
),
match_days AS (
    SELECT DISTINCT club_id, attention_date_utc FROM mart_match_day_lift
),
brand_days AS (              -- one row per deal x day the brand has a lift value
    SELECT d.club_id, d.brand_id, a.view_date, a.views, a.lift_vs_baseline,
           DAYOFWEEK(a.view_date)            AS weekday,
           m.attention_date_utc IS NOT NULL  AS is_match_day
    FROM deals AS d
    JOIN mart_attention_daily AS a
      ON a.entity_type = 'brand'
     AND a.entity_id   = d.brand_id
     AND a.view_date BETWEEN d.deal_from AND d.deal_to
    LEFT JOIN match_days AS m
      ON m.club_id = d.club_id AND m.attention_date_utc = a.view_date
    WHERE a.lift_vs_baseline IS NOT NULL
),
weekday_norm AS (            -- brand's typical lift on non-match days, per weekday
    SELECT club_id, brand_id, weekday, MEDIAN(lift_vs_baseline) AS norm_lift
    FROM brand_days
    WHERE NOT is_match_day
    GROUP BY ALL
),
excess AS (
    SELECT bd.club_id, bd.brand_id, bd.lift_vs_baseline - wn.norm_lift AS excess_lift
    FROM brand_days AS bd
    JOIN weekday_norm AS wn USING (club_id, brand_id, weekday)
    WHERE bd.is_match_day
)
SELECT
    d.club_id,
    d.brand_id,
    d.assets,
    d.deal_from,
    d.deal_to,
    (SELECT AVG(views) FROM brand_days AS bd
     WHERE bd.club_id = d.club_id AND bd.brand_id = d.brand_id)    AS avg_daily_views,
    COUNT(e.excess_lift)                                          AS match_days,
    MEDIAN(e.excess_lift)                                         AS median_excess_lift,
    COUNT(*) FILTER (WHERE e.excess_lift > 0)                     AS days_above_norm
FROM deals AS d
JOIN excess AS e USING (club_id, brand_id)
GROUP BY d.club_id, d.brand_id, d.assets, d.deal_from, d.deal_to;
