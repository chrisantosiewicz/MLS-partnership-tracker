-- A source can't have been checked on a date that hasn't happened yet.
SELECT club_id, brand_id, asset_id, date_checked
FROM stg_partnerships
WHERE date_checked > CURRENT_DATE;
