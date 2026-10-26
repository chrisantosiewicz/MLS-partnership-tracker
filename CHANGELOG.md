# Changelog

Dataset and pipeline changes, newest first. Dataset versions are git tags
(`v0.1`, `v0.2`, ...).

## Unreleased (v0.1 candidate)

### Dataset
- First 57 rows of `partnerships.csv`: front-of-kit partners for 29 clubs and
  sleeve partners for 24 clubs, 2026 season. Sourced from two independent 2026
  roundups (Blinkfire Analytics, forsoccer.com) that agree, plus the FC Dallas
  primary-kit release. All rows `start_season_basis = first_observed`.
- Left out until verified: Real Salt Lake (sources disagree on front vs sleeve
  between Intermountain Health and Select Health), Portland's away-kit front,
  sleeve partners for FC Dallas, Houston, New England, Orlando and San Jose,
  and all stadium naming rights.
- `brands.csv`: 54 brands with categories. 16 have no Wikipedia title yet
  (6 have no article; 10 need the exact title confirmed). Puyallup Tribe's
  title also needs checking.
- Added category `professional_services` (Guidehouse, BLG).

### Pipeline
- Schema, loads, `partnership_history` (type 2), attention baseline,
  match-day lift, category landscape, 13 data tests and 1 warning test.
- Wikipedia pageviews ingestion (backfill from 2023-01-01, then incremental).
- ASA match ingestion (2023 to current season).
- Quarto page with two charts; GitHub Actions daily build and PR checks.
