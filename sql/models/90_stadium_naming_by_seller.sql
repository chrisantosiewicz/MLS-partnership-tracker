-- mart_stadium_naming_by_seller: do naming rights sold by the club go to
-- different categories than naming rights sold by an outside venue owner
-- (an NFL or university stadium)?
--
-- Grain: one row per seller ('club', 'stadium_owner') per sponsor category,
-- current stadium naming deals only.
-- sold_by lives on the source rows (stg_partnerships), not on
-- partnership_history, so it's joined back on the deal's natural key.
-- Small numbers: only a handful of clubs play in outside-owned venues, so
-- this describes the current set; it doesn't support a general claim.

CREATE TABLE mart_stadium_naming_by_seller AS
WITH stadium_deals AS (
    SELECT sp.sold_by, b.brand_name, b.category_id, ph.club_id
    FROM partnership_history AS ph
    JOIN (SELECT DISTINCT club_id, brand_id, asset_id, kit_scope, sold_by
          FROM stg_partnerships) AS sp
      USING (club_id, brand_id, asset_id, kit_scope)
    JOIN dim_brand AS b USING (brand_id)
    WHERE ph.is_current
      AND ph.asset_id = 'stadium_naming'
)
SELECT
    d.sold_by,
    d.category_id,
    cat.category_name,
    COUNT(*)                                                     AS deals,
    COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY d.sold_by)       AS share_of_seller,
    STRING_AGG(d.brand_name || ' (' || c.short_name || ')', ', '
               ORDER BY d.brand_name)                            AS deals_list
FROM stadium_deals AS d
JOIN dim_category AS cat USING (category_id)
JOIN dim_club     AS c   USING (club_id)
GROUP BY d.sold_by, d.category_id, cat.category_name;
