# Data dictionary

Hand-maintained files live here. Files in `raw/` are written by the Python
ingestion scripts; don't edit them by hand.

## `partnerships.csv`: the core dataset

**Grain:** one row = one brand holding one asset, on one kit, at one club, for
one continuous span of seasons. A renewal with the same brand extends
`end_season` on the same row. A new brand on the same asset is a new row.

| Column | Meaning |
|--------|---------|
| `club_id` | Club code from `clubs.csv` |
| `brand_id` | Brand code from `brands.csv` |
| `asset_id` | `front_of_kit`, `sleeve` or `stadium_naming` (see `assets.csv`) |
| `kit_scope` | `all` (every kit), `primary` or `secondary`. Used when a club has different partners on home and away kits |
| `start_season` | First season of the deal |
| `start_season_basis` | `announced` = the deal's real first season, from a source. `first_observed` = the first season we have a source for; the deal may be older |
| `end_season` | Last season the brand holds the asset. Blank = active, no announced end |
| `start_date`, `end_date` | Optional exact dates, when known. Override the season-based dates |
| `reported_value_usd_per_year` | Only if a published source reports it. Blank = not publicly reported |
| `reported_value_note` | How it was reported, e.g. "reported $75M over 8 years" |
| `reported_value_source_url` | Required whenever a value or note is filled |
| `source_type` | `primary` (club or brand announcement), `press` (news coverage) or `roundup` (a list covering many clubs) |
| `source_url` | Where the row was verified |
| `date_checked` | `YYYY-MM-DD`, the day the source was read |
| `notes` | Anything a reviewer should know: conflicts between sources, second sources |

### Sourcing rules
1. Primary source first (club or brand announcement). Then credible press. A
   roundup is acceptable when two independent roundups agree; note the second
   one in `notes`.
2. When sources disagree, leave the row out and list it in `PROGRESS_LOG.md`
   under "to verify". A blank is better than a guess.
3. Upgrading a `roundup` row to a `primary` source, or `first_observed` to
   `announced`, is a normal edit: update the row and `date_checked`, and add a
   line to `CHANGELOG.md`.

## `brands.csv`

| Column | Meaning |
|--------|---------|
| `brand_id` | Short code used as the key |
| `brand_name` | Name as it appears on the kit or stadium |
| `parent_company` | Owner, when different from the brand |
| `category_id` | From `categories.csv`. A category belongs to the brand, not the deal |
| `wikipedia_article` | Exact English Wikipedia title used for pageviews. Blank only if `no_article_reason` is filled |
| `no_article_reason` | Why there's no article ("No English Wikipedia article found", "Article title not yet confirmed") |
| `notes` | Free text |

## `clubs.csv`

| Column | Meaning |
|--------|---------|
| `club_id` | Short code used as the key (e.g. `CHI`). Project convention, not an official MLS code |
| `club_name`, `short_name` | Full name, and name for chart labels |
| `city`, `state_province`, `country` | Where the club plays home matches |
| `conference` | Eastern or Western (2026) |
| `wikipedia_article` | English Wikipedia title for pageviews |
| `asa_team_name` | Team name in the American Soccer Analysis API (checked against its teams endpoint on 2026-10-26) |

## `categories.csv` and `assets.csv`

The allowed lists. Add a category only when no existing one fits, and note
why in `CHANGELOG.md`.

## `raw/` (written by the pipeline)

| File | Written by | Grain |
|------|-----------|-------|
| `pageviews.parquet` | `python/wiki_pageviews.py` | article x UTC day |
| `matches.parquet` | `python/asa_matches.py` | MLS match |
