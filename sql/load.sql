-- load.sql: fill the tables from the files in data/.
--
-- CSVs are read as text (all_varchar) and cast here, so the types are decided
-- in one readable place instead of by DuckDB's type sniffing. TRIM + NULLIF
-- turns empty cells into real NULLs.

INSERT INTO dim_club
SELECT club_id, club_name, short_name, city, state_province, country,
       conference, wikipedia_article, asa_team_name
FROM read_csv('data/clubs.csv', header = true, all_varchar = true);

INSERT INTO dim_category
SELECT category_id, category_name, description
FROM read_csv('data/categories.csv', header = true, all_varchar = true);

INSERT INTO dim_asset
SELECT asset_id, asset_name, CAST(exclusive_per_club AS BOOLEAN), description
FROM read_csv('data/assets.csv', header = true, all_varchar = true);

INSERT INTO dim_brand
SELECT TRIM(brand_id),
       TRIM(brand_name),
       NULLIF(TRIM(parent_company), ''),
       NULLIF(TRIM(category_id), ''),
       NULLIF(TRIM(wikipedia_article), ''),
       NULLIF(TRIM(no_article_reason), ''),
       NULLIF(TRIM(notes), '')
FROM read_csv('data/brands.csv', header = true, all_varchar = true);

INSERT INTO stg_partnerships
SELECT TRIM(club_id),
       TRIM(brand_id),
       TRIM(asset_id),
       COALESCE(NULLIF(TRIM(kit_scope), ''), 'all'),
       CAST(NULLIF(TRIM(start_season), '') AS INTEGER),
       NULLIF(TRIM(start_season_basis), ''),
       CAST(NULLIF(TRIM(end_season), '') AS INTEGER),
       CAST(NULLIF(TRIM(start_date), '') AS DATE),
       CAST(NULLIF(TRIM(end_date), '') AS DATE),
       CAST(NULLIF(TRIM(reported_value_usd_per_year), '') AS DECIMAL(14, 2)),
       NULLIF(TRIM(reported_value_note), ''),
       NULLIF(TRIM(reported_value_source_url), ''),
       NULLIF(TRIM(source_type), ''),
       NULLIF(TRIM(source_url), ''),
       CAST(NULLIF(TRIM(date_checked), '') AS DATE),
       NULLIF(TRIM(notes), '')
FROM read_csv('data/partnerships.csv', header = true, all_varchar = true);

-- Raw files written by the Python ingestion scripts.
INSERT INTO fact_pageviews_daily
SELECT article, view_date, views
FROM read_parquet('data/raw/pageviews.parquet');

-- Map ASA team names to our club ids. A LEFT JOIN keeps the match even when a
-- name doesn't map, so tests/test_matches_map_to_clubs.sql can report it.
INSERT INTO dim_match
SELECT m.game_id,
       m.kickoff_utc,
       CAST(m.kickoff_utc AS DATE),
       m.season,
       home.club_id,
       away.club_id,
       m.home_score,
       m.away_score,
       m.status
FROM read_parquet('data/raw/matches.parquet') AS m
LEFT JOIN dim_club AS home ON home.asa_team_name = m.home_team_name
LEFT JOIN dim_club AS away ON away.asa_team_name = m.away_team_name;
