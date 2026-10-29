-- Example as-of join: which brand was on each club's front of kit on a date?
-- Not part of the build; run it by hand in DuckDB:
--   duckdb tracker.duckdb < sql/examples/as_of_kit_partner.sql

SELECT c.club_name, b.brand_name, ph.valid_from, ph.valid_to
FROM dim_club AS c
LEFT JOIN partnership_history AS ph
       ON ph.club_id  = c.club_id
      AND ph.asset_id = 'front_of_kit'
      AND DATE '2025-06-01' BETWEEN ph.valid_from AND ph.valid_to
LEFT JOIN dim_brand AS b USING (brand_id)
ORDER BY c.club_name;
