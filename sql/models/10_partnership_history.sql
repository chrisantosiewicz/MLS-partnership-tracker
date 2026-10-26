-- partnership_history: who held which asset at which club, and when.
--
-- Grain: one row per deal (club x brand x asset x kit x continuous span).
-- valid_from / valid_to turn seasons into dates so we can do as-of joins:
--   "which brand was on the Fire's kit on 2025-06-01?"
--   -> WHERE DATE '2025-06-01' BETWEEN valid_from AND valid_to
-- This is the type 2 slowly changing dimension pattern: when the holder of an
-- asset changes we don't overwrite the old row, we close it (valid_to) and add
-- a new one, so history is kept.
--
-- Season -> date rules (a simplification, listed under limitations):
--   valid_from = start_date if known, else Jan 1 of start_season
--   valid_to   = end_date if known, else Dec 31 of end_season,
--                else 9999-12-31 for a deal with no announced end
-- valid_to is inclusive.
--
-- start_season_basis = 'first_observed' means valid_from is the first season
-- we have a source for, not necessarily when the deal began. As-of questions
-- before that date return no sponsor (unknown), never a wrong one.

CREATE TABLE partnership_history AS
WITH deals AS (
    SELECT
        p.club_id,
        p.brand_id,
        p.asset_id,
        p.kit_scope,
        p.start_season_basis,
        COALESCE(p.start_date, MAKE_DATE(p.start_season, 1, 1))  AS valid_from,
        COALESCE(p.end_date,
                 MAKE_DATE(p.end_season, 12, 31),
                 DATE '9999-12-31')                             AS valid_to,
        p.reported_value_usd_per_year,
        p.reported_value_note,
        p.reported_value_source_url,
        p.source_type,
        p.source_url,
        p.date_checked
    FROM stg_partnerships AS p
)
SELECT
    ROW_NUMBER() OVER (ORDER BY club_id, asset_id, valid_from)  AS partnership_id,
    d.*,
    CURRENT_DATE BETWEEN d.valid_from AND d.valid_to             AS is_current
FROM deals AS d;
