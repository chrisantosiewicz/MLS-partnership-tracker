-- Required fields: a deal needs a start, and a reported value needs its own
-- source (reported values are always "reported by X", never our estimate).
SELECT club_id, brand_id, asset_id, start_season,
       reported_value_usd_per_year, reported_value_source_url
FROM stg_partnerships
WHERE (start_season IS NULL AND start_date IS NULL)
   OR (reported_value_usd_per_year IS NOT NULL AND reported_value_source_url IS NULL)
   OR (reported_value_note IS NOT NULL AND reported_value_source_url IS NULL);
