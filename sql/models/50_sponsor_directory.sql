-- mart_sponsor_directory: who holds each club's major assets right now?
--
-- Grain: one row per club, all 30 clubs, including clubs with no recorded
-- deal (FROM dim_club, LEFT JOIN the deals, so a club never drops out).
--
-- Rows become columns with conditional aggregation (one STRING_AGG per
-- asset, each with its own FILTER). Some clubs have two rows for one asset
-- (kit_scope primary/secondary: Dallas, Philadelphia; two sleeves:
-- Minnesota, Seattle), so brands are joined with ' / ' to keep one row per
-- club. is_current is filtered in the CTE, before the join: filtering it in
-- WHERE after a LEFT JOIN would drop the clubs with no deals.

CREATE TABLE mart_sponsor_directory AS
WITH current_deals AS (
    SELECT ph.club_id, ph.asset_id, ph.kit_scope, ph.source_url, ph.date_checked,
           b.brand_name, cat.category_name, sp.sold_by
    FROM partnership_history AS ph
    JOIN dim_brand    AS b   USING (brand_id)
    JOIN dim_category AS cat USING (category_id)
    LEFT JOIN (SELECT DISTINCT club_id, brand_id, asset_id, kit_scope, sold_by
               FROM stg_partnerships) AS sp
           USING (club_id, brand_id, asset_id, kit_scope)
    WHERE ph.is_current
)
SELECT
    c.club_id,
    c.short_name,
    c.conference,
    STRING_AGG(d.brand_name, ' / ' ORDER BY d.kit_scope, d.brand_name)
        FILTER (WHERE d.asset_id = 'front_of_kit')                     AS front_of_kit_brand,
    STRING_AGG(DISTINCT d.category_name, ' / ')
        FILTER (WHERE d.asset_id = 'front_of_kit')                     AS front_of_kit_category,
    STRING_AGG(d.brand_name, ' / ' ORDER BY d.kit_scope, d.brand_name)
        FILTER (WHERE d.asset_id = 'sleeve')                           AS sleeve_brand,
    STRING_AGG(DISTINCT d.category_name, ' / ')
        FILTER (WHERE d.asset_id = 'sleeve')                           AS sleeve_category,
    STRING_AGG(d.brand_name, ' / ')
        FILTER (WHERE d.asset_id = 'stadium_naming')                   AS stadium_brand,
    STRING_AGG(DISTINCT d.category_name, ' / ')
        FILTER (WHERE d.asset_id = 'stadium_naming')                   AS stadium_category,
    MAX(d.sold_by) FILTER (WHERE d.asset_id = 'stadium_naming')        AS stadium_sold_by,
    -- One source link per asset cell (the first by kit_scope when there are two).
    ARG_MIN(d.source_url, d.kit_scope) FILTER (WHERE d.asset_id = 'front_of_kit')   AS front_of_kit_source,
    ARG_MIN(d.source_url, d.kit_scope) FILTER (WHERE d.asset_id = 'sleeve')         AS sleeve_source,
    ARG_MIN(d.source_url, d.kit_scope) FILTER (WHERE d.asset_id = 'stadium_naming') AS stadium_source,
    -- One source per club: the front-of-kit row's if there is one.
    ARG_MIN(d.source_url, CASE d.asset_id WHEN 'front_of_kit' THEN 1
                                         WHEN 'sleeve' THEN 2 ELSE 3 END) AS source_url,
    MAX(d.date_checked)                                                AS date_checked
FROM dim_club AS c
LEFT JOIN current_deals AS d USING (club_id)
GROUP BY c.club_id, c.short_name, c.conference;
