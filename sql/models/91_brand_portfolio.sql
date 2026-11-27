-- mart_brand_portfolio: every current sponsor brand, its MLS footprint and
-- how much public attention its Wikipedia page gets.
--
-- Grain: one row per brand with at least one current deal.
-- Attention = average daily pageviews over the last 28 days of data (NULL
-- when the brand has no confirmed English Wikipedia article). It is a measure
-- of the brand's public attention overall, not of what it gets from MLS.

CREATE TABLE mart_brand_portfolio AS
WITH current_deals AS (
    SELECT ph.brand_id, ph.club_id, ph.asset_id, a.asset_name, c.short_name
    FROM partnership_history AS ph
    JOIN dim_asset AS a USING (asset_id)
    JOIN dim_club  AS c USING (club_id)
    WHERE ph.is_current
),
brand_recent AS (
    SELECT entity_id AS brand_id, AVG(views) AS avg_daily_views_28d
    FROM mart_attention_daily
    WHERE entity_type = 'brand'
      AND view_date > (SELECT MAX(view_date) FROM mart_attention_daily) - INTERVAL 28 DAY
    GROUP BY entity_id
)
SELECT
    b.brand_id,
    b.brand_name,
    b.parent_company,
    cat.category_name,
    COUNT(DISTINCT d.club_id)                                         AS clubs,
    COUNT(*)                                                          AS deals,
    STRING_AGG(DISTINCT d.short_name, ', ' ORDER BY d.short_name)     AS club_list,
    STRING_AGG(DISTINCT d.asset_name, ', ' ORDER BY d.asset_name)     AS asset_list,
    br.avg_daily_views_28d
FROM current_deals AS d
JOIN dim_brand    AS b   USING (brand_id)
JOIN dim_category AS cat USING (category_id)
LEFT JOIN brand_recent AS br USING (brand_id)
GROUP BY b.brand_id, b.brand_name, b.parent_company, cat.category_name, br.avg_daily_views_28d;
