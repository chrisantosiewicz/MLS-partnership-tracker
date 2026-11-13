# Changelog

Dataset and pipeline changes, newest first. Dataset versions are git tags
(`v0.1`, `v0.2`, ...).

## Unreleased (v0.1 candidate)

### Dataset
- Stadium naming rights for 25 clubs (Nov 5). Each row cites a club, brand or
  press announcement. No row for Chicago, NYCFC and Vancouver (unsponsored
  names), Sporting KC (Children's Mercy deal ended after 2025; the club is
  seeking a new partner) or CF Montréal (Stade Saputo is named for the owner's
  company, not a paid deal). 20 new brands.
- New column `sold_by` in `partnerships.csv`: `club`, or `stadium_owner` for
  external venues (Atlanta, Charlotte, New England and Seattle's NFL
  stadiums, and San Diego State's Snapdragon Stadium). Added to the
  allowed-values test.
- Real Salt Lake added (Nov 5): Select Health on the front of the kit and
  Intermountain Health on the sleeve, from the 2024 Intermountain and RSL
  announcements (`start_season_basis = announced`, 2024). Select Health is
  Intermountain's health plan, which is why the roundups disagreed. New brands
  `intermountain_health` (health_care) and `select_health` (insurance).
- FC Dallas has no club sleeve partner in 2026: its 2026 kit release names only
  the league-wide Apple TV patch, which the dataset doesn't record. Houston,
  New England and Orlando are the same (checked by Chris, Nov 5).
- San Jose sleeve: Apollo (right sleeve) from July 25, 2026, per the club's
  announcement. New brand `apollo` (technology).
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
- GitHub Actions moved to their Node 24 versions (checkout v5, setup-python
  v6, upload-pages-artifact v5, deploy-pages v5) ahead of the Node 20
  deprecation (Nov 5).
- Schema, loads, `partnership_history` (type 2), attention baseline,
  match-day lift, category landscape, 13 data tests and 1 warning test.
- Wikipedia pageviews ingestion (backfill from 2023-01-01, then incremental).
- ASA match ingestion (2023 to current season).
- Quarto page with two charts; GitHub Actions daily build and PR checks.
