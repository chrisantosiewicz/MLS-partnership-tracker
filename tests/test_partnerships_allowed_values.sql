-- Coded columns must use their allowed values (see data/README.md).
SELECT club_id, brand_id, asset_id, kit_scope, start_season_basis, source_type
FROM stg_partnerships
WHERE kit_scope NOT IN ('all', 'primary', 'secondary')
   OR start_season_basis IS NULL
   OR start_season_basis NOT IN ('announced', 'first_observed')
   OR source_type IS NULL
   OR source_type NOT IN ('primary', 'press', 'roundup');
