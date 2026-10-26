-- schema.sql: every table in the warehouse, created empty.
--
-- Layers
--   dim_*   one row per thing (club, brand, category, asset, match)
--   stg_*   the hand-maintained CSV as typed rows, before any business rules
--   fact_*  one row per measurement (article x day)
--   partnership_history and the marts are built later by sql/models/.
--
-- Keys: primary keys are enforced so a duplicate id stops the build with a
-- clear error. Foreign keys are NOT declared; referential checks live in
-- tests/ instead, so a bad row shows up in the test report rather than
-- crashing the load.

CREATE TABLE dim_club (
    club_id            VARCHAR PRIMARY KEY,   -- project code, e.g. 'CHI'
    club_name          VARCHAR NOT NULL,
    short_name         VARCHAR NOT NULL,
    city               VARCHAR NOT NULL,
    state_province     VARCHAR NOT NULL,
    country            VARCHAR NOT NULL,
    conference         VARCHAR NOT NULL,
    wikipedia_article  VARCHAR NOT NULL,      -- title as used by the Pageviews API
    asa_team_name      VARCHAR NOT NULL       -- name used by American Soccer Analysis
);

CREATE TABLE dim_category (
    category_id    VARCHAR PRIMARY KEY,
    category_name  VARCHAR NOT NULL,
    description    VARCHAR
);

CREATE TABLE dim_asset (
    asset_id            VARCHAR PRIMARY KEY,
    asset_name          VARCHAR NOT NULL,
    exclusive_per_club  BOOLEAN NOT NULL,     -- true = only one brand at a time
    description         VARCHAR
);

CREATE TABLE dim_brand (
    brand_id           VARCHAR PRIMARY KEY,   -- slug, e.g. 'carvana'
    brand_name         VARCHAR NOT NULL,
    parent_company     VARCHAR,
    category_id        VARCHAR,               -- checked against dim_category in tests
    wikipedia_article  VARCHAR,               -- null only when no_article_reason says why
    no_article_reason  VARCHAR,
    notes              VARCHAR
);

-- One row = one brand holding one asset (on one kit) at one club for one
-- continuous span. A renewal with the same brand extends end_season on the
-- same row. A new brand on the same asset is a new row.
CREATE TABLE stg_partnerships (
    club_id                      VARCHAR,
    brand_id                     VARCHAR,
    asset_id                     VARCHAR,
    kit_scope                    VARCHAR,     -- 'all', 'primary' or 'secondary' kit
    start_season                 INTEGER,
    start_season_basis           VARCHAR,     -- 'announced' or 'first_observed'
    end_season                   INTEGER,     -- null = still active / no announced end
    start_date                   DATE,        -- optional, when the exact date is known
    end_date                     DATE,
    reported_value_usd_per_year  DECIMAL(14, 2),  -- null = not publicly reported
    reported_value_note          VARCHAR,     -- e.g. 'reported $50M over 10 years'
    reported_value_source_url    VARCHAR,
    source_type                  VARCHAR,     -- 'primary', 'press' or 'roundup'
    source_url                   VARCHAR,
    date_checked                 DATE,
    notes                        VARCHAR
);

-- One row per MLS match from American Soccer Analysis.
CREATE TABLE dim_match (
    match_id        VARCHAR PRIMARY KEY,
    kickoff_utc     TIMESTAMP,
    match_date_utc  DATE,        -- UTC calendar date, same clock as pageviews
    season          INTEGER,
    home_club_id    VARCHAR,     -- null if the ASA team name isn't in dim_club
    away_club_id    VARCHAR,
    home_score      INTEGER,
    away_score      INTEGER,
    status          VARCHAR
);

-- One row per Wikipedia article per UTC day.
CREATE TABLE fact_pageviews_daily (
    article    VARCHAR NOT NULL,
    view_date  DATE NOT NULL,
    views      BIGINT NOT NULL
    -- No primary key on purpose: tests/test_pageviews_no_duplicates.sql
    -- reports duplicate article-days instead of the load crashing.
);
