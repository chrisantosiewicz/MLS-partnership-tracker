-- Every deal must point at a club, brand and asset that exist.
SELECT p.club_id, p.brand_id, p.asset_id,
       c.club_id IS NULL  AS unknown_club,
       b.brand_id IS NULL AS unknown_brand,
       a.asset_id IS NULL AS unknown_asset
FROM stg_partnerships AS p
LEFT JOIN dim_club  AS c ON c.club_id  = p.club_id
LEFT JOIN dim_brand AS b ON b.brand_id = p.brand_id
LEFT JOIN dim_asset AS a ON a.asset_id = p.asset_id
WHERE c.club_id IS NULL OR b.brand_id IS NULL OR a.asset_id IS NULL;
