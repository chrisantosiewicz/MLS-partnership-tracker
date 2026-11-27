# Changelog

Dataset and pipeline changes, newest first. Dataset versions are git tags
(`v0.1`, `v0.2`, ...).

## Unreleased

### Market intelligence (Nov 25, PR after #8)
- **Brands page**: a searchable directory of all 77 current sponsor brands
  with owner, category, clubs, assets and Wikipedia attention, plus a
  multi-club filter (`mart_brand_portfolio`).
- **Clubs page**: a profile per club with its three partners (each linked to
  its source), match-day and year-over-year attention ranks, its best sponsor
  match-day result, and open categories to research with lookalike brands
  from other clubs (`mart_category_whitespace`). Profiles are linkable by
  hash, e.g. `clubs.html#SEA`.
- **Sponsors page**: a club-by-category market map (`mart_club_category_map`)
  and a stadium-naming tenure chart (`mart_stadium_naming_tenure`).
- Two new tests: portfolio and market map each count every current deal once;
  whitespace never names a category the club already holds.
- Dark mode removed (Chris: not worth the upkeep).

### Site
- Redesigned as a four-page site (Overview, Sponsors, Attention, Methods):
  hero and headline-number tiles, finding cards linking to each chart, chart
  cards whose titles state the finding, a "View data" table under every
  chart, a searchable and filterable sponsor directory with a source link on
  every deal and a club picker on the attention chart. Mobile layout checked
  at 390px. (A dark mode shipped in PR #8 and was removed on Nov 25 at Chris's
  request: not worth the upkeep.)
- Charts use a palette checked for color-vision deficiency.

### Analysis
- Who sells the stadium name: `mart_stadium_naming_by_seller` compares
  categories of club-sold and venue-sold (NFL or university stadium) naming
  rights. Test: every current stadium deal counted once.
- Do sponsors get noticed on match day: `mart_sponsor_match_day_attention`
  compares a sponsor brand's Wikipedia views on its club's match days with its
  own non-match days on the same weekday, during the deal only. The page runs a
  sign test per brand with a Benjamini-Hochberg adjustment. A naive comparison
  is confounded: 75% of matches fall on a UTC weekend, when company pages get
  about 16% fewer views.

### Research
- `TO_VERIFY.md`: Portland (BofA front, Tillamook to sleeve), Sporting KC
  stadium (no naming partner found) and San Jose sleeve history updated with
  what the sources do and don't say. No CSV rows changed: none of the open
  items has a source strong enough yet.

### Fix
- Match-day attention now uses the UTC day that holds the match
  (`attention_date_utc`, UTC date two hours after kickoff) instead of the UTC
  date of kickoff. A 7:30 pm ET kickoff is 23:30 UTC, so 37% of club-matches
  were measured on the day before the match was played. Median match-day lift
  across clubs rises from +24% to +38%, and no club's 2026 median is negative
  any more (Orlando City was -11%). Decision updated in `docs/DECISIONS.md`.

### Report
- Five new page sections: sponsor directory (front of kit, sleeve and
  stadium, with a coverage line), match-day lift for every club (home vs
  away), lift by result, and change in attention vs last year.
- Four new models: `mart_sponsor_directory`, `mart_club_match_lift`,
  `mart_lift_by_result`, `mart_attention_by_season` (specs in
  `docs/REPORT_SQL.md`). Written by Claude on Nov 25 at Chris's request, to
  be walked through afterward.
- Two new tests: one directory row per club; wins equal losses.
- Intro says stadium naming rights are tracked again (25 clubs since Nov 5).

### Docs
- README opens with a headline finding from `mart_category_share`, and the
  ASCII pipeline sketch is now a Mermaid architecture diagram.
- New `docs/DATA_MODEL.md`: ERD of the warehouse tables, the marts and how
  they join.

## v0.1 (2026-11-13)

Tag `v0.1` points at the merge of PR #6.

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
