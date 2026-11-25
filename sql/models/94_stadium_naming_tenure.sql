-- mart_stadium_naming_tenure: how long each current stadium name has been in
-- place.
--
-- Grain: one row per current stadium naming deal.
-- seasons_named counts seasons from the deal's first season to the latest
-- season of pageview data, inclusive. Only rows whose start season is
-- 'announced' (a sourced first season) have a real tenure; 'first_observed'
-- rows are kept with tenure_known = false so the page can say so.

CREATE TABLE mart_stadium_naming_tenure AS
WITH this_season AS (
    SELECT YEAR(MAX(view_date)) AS season FROM mart_attention_daily
)
SELECT
    ph.club_id,
    c.short_name,
    b.brand_name,
    cat.category_name,
    sp.start_season,
    sp.start_season_basis,
    sp.start_season_basis = 'announced'               AS tenure_known,
    ts.season - sp.start_season + 1                   AS seasons_named,
    sp.sold_by,
    sp.source_url
FROM partnership_history AS ph
JOIN stg_partnerships AS sp
  USING (club_id, brand_id, asset_id, kit_scope)
JOIN dim_club     AS c   USING (club_id)
JOIN dim_brand    AS b   USING (brand_id)
JOIN dim_category AS cat USING (category_id)
CROSS JOIN this_season AS ts
WHERE ph.is_current
  AND ph.asset_id = 'stadium_naming';
