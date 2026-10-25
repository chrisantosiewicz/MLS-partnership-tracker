# Data dictionary

## `clubs.csv` (reference data, one row per MLS club, 30 rows)

| Column | Meaning |
|--------|---------|
| `club_id` | Short code used as the key (e.g. `CHI`). Project convention, not an official MLS code |
| `club_name` | Full club name |
| `short_name` | Name for chart labels |
| `city`, `state_province`, `country` | Where the club plays its home matches |
| `conference` | Eastern or Western (2026 season) |
| `wikipedia_article` | English Wikipedia article title, as used by the Pageviews API. **Not yet checked against Wikipedia**; Week 2 ingestion must confirm each title resolves without a redirect |

## `partnerships.csv` (one row per ... *Chris to define the grain*)

The header is a starting draft taken from the project brief. Change it once
you've answered the design questions in `docs/week1-plan.md`.

| Column | Meaning |
|--------|---------|
| `club` | |
| `brand` | |
| `category` | Must be one of the allowed categories below |
| `asset` | Must be one of the allowed assets below |
| `start_season` | |
| `end_season` | |
| `reported_value` | |
| `reported_value_source_url` | |
| `source_url` | |
| `date_checked` | `YYYY-MM-DD` |

### Allowed assets
*Chris to define.* v0.1 scope: front of kit, sleeve, stadium naming.

### Allowed categories
*Chris to define.*
