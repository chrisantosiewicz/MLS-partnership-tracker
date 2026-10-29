-- valid_to must be on or after valid_from.
SELECT partnership_id, club_id, brand_id, asset_id, valid_from, valid_to
FROM partnership_history
WHERE valid_to < valid_from;
