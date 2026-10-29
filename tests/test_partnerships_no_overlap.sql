-- An exclusive asset (front of kit, sleeve, stadium name) can only have one
-- brand at a time per club and kit. Two deals clash when they are on the same
-- kit (or either covers 'all' kits) and each starts before the other ends.
-- a.partnership_id < b.partnership_id compares each pair once and never a
-- deal with itself.
WITH exclusive_deals AS (
    SELECT ph.*
    FROM partnership_history AS ph
    JOIN dim_asset AS a USING (asset_id)
    WHERE a.exclusive_per_club
)
SELECT a.club_id, a.asset_id,
       a.brand_id AS brand_1, a.kit_scope AS kit_1, a.valid_from AS from_1, a.valid_to AS to_1,
       b.brand_id AS brand_2, b.kit_scope AS kit_2, b.valid_from AS from_2, b.valid_to AS to_2
FROM exclusive_deals AS a
JOIN exclusive_deals AS b
  ON a.club_id  = b.club_id
 AND a.asset_id = b.asset_id
 AND a.partnership_id < b.partnership_id
 AND (a.kit_scope = b.kit_scope OR 'all' IN (a.kit_scope, b.kit_scope))
 AND a.valid_from <= b.valid_to
 AND b.valid_from <= a.valid_to;
