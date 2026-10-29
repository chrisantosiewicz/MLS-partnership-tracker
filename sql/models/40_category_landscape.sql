-- Category landscape: which categories MLS clubs sell their major assets to,
-- and how much public attention each club's current sponsor brands get.
-- Both use deals current as of today (partnership_history.is_current).

-- 1. Category share by asset.
-- Grain: one row per asset x category.
CREATE TABLE mart_category_share AS
WITH current_deals AS (
    SELECT ph.asset_id, b.category_id
    FROM partnership_history AS ph
    JOIN dim_brand AS b USING (brand_id)
    WHERE ph.is_current
),
counts AS (
    SELECT asset_id, category_id, COUNT(*) AS deals
    FROM current_deals
    GROUP BY asset_id, category_id
)
SELECT
    c.asset_id,
    a.asset_name,
    c.category_id,
    cat.category_name,
    c.deals,
    c.deals / SUM(c.deals) OVER (PARTITION BY c.asset_id)  AS share_of_asset
FROM counts AS c
JOIN dim_asset    AS a   USING (asset_id)
JOIN dim_category AS cat USING (category_id);

-- 2. Clubs ranked by the attention their current sponsor brands get.
-- Grain: one row per club.
-- Attention = each current sponsor brand's average daily pageviews over the
-- last 28 days of data, summed across the club's sponsors. A brand that
-- sponsors two clubs counts fully for each (it's the brand's attention, not a
-- split of it). PERCENT_RANK: 1.0 = most attention, 0.0 = least.
CREATE TABLE mart_club_sponsor_attention AS
WITH latest AS (
    SELECT MAX(view_date) AS last_day FROM mart_attention_daily
),
brand_recent AS (            -- one row per brand
    SELECT a.entity_id AS brand_id, AVG(a.views) AS avg_daily_views_28d
    FROM mart_attention_daily AS a, latest
    WHERE a.entity_type = 'brand'
      AND a.view_date > latest.last_day - INTERVAL 28 DAY
    GROUP BY a.entity_id
),
club_sponsors AS (           -- one row per club x distinct current sponsor brand
    SELECT DISTINCT club_id, brand_id
    FROM partnership_history
    WHERE is_current
),
club_totals AS (             -- one row per club
    SELECT cs.club_id,
           COUNT(*)                                  AS current_sponsor_brands,
           COUNT(br.brand_id)                        AS brands_with_pageviews,
           COALESCE(SUM(br.avg_daily_views_28d), 0)  AS sponsor_avg_daily_views_28d
    FROM club_sponsors AS cs
    LEFT JOIN brand_recent AS br USING (brand_id)
    GROUP BY cs.club_id
)
SELECT
    ct.*,
    PERCENT_RANK() OVER (ORDER BY ct.sponsor_avg_daily_views_28d) AS attention_percent_rank
FROM club_totals AS ct;
