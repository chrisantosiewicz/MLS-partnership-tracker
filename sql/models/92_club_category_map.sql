-- mart_club_category_map: which sponsor categories each club has sold, and
-- through which assets. The "market map" of current deals.
--
-- Grain: one row per club x category with at least one current deal.
-- Only the three tracked assets (front of kit, sleeve, stadium name) count;
-- a club may hold other deals in a category that this dataset doesn't track.

CREATE TABLE mart_club_category_map AS
SELECT
    ph.club_id,
    b.category_id,
    cat.category_name,
    COUNT(*)                                                   AS deals,
    STRING_AGG(b.brand_name || ' (' || LOWER(REPLACE(a.asset_name, ' partner', '')) || ')',
               ', ' ORDER BY a.asset_id)                       AS deal_list
FROM partnership_history AS ph
JOIN dim_brand    AS b   USING (brand_id)
JOIN dim_category AS cat USING (category_id)
JOIN dim_asset    AS a   USING (asset_id)
WHERE ph.is_current
GROUP BY ph.club_id, b.category_id, cat.category_name;
