-- Every deal must cite a source and the date it was checked.
SELECT club_id, brand_id, asset_id, start_season
FROM stg_partnerships
WHERE source_url IS NULL
   OR source_url NOT LIKE 'http%'
   OR date_checked IS NULL;
