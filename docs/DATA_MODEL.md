# Data model

Every table lives in one DuckDB file, `tracker.duckdb`, rebuilt from scratch
by `python/build.py` on each run. Column lists below match
[`sql/schema.sql`](../sql/schema.sql) and [`sql/models/`](../sql/models/).

## Layers

| Prefix | Built by | Grain |
|--------|----------|-------|
| `dim_` | `schema.sql` + `load.sql` | One row per thing: club, brand, category, asset, match |
| `stg_` | `schema.sql` + `load.sql` | The hand-maintained CSV as typed rows, before business rules |
| `fact_` | `schema.sql` + `load.sql` | One row per measurement: article per UTC day |
| `partnership_history` | `models/10_partnership_history.sql` | One row per deal, with `valid_from` / `valid_to` dates (type 2 SCD) |
| `mart_` | `models/20` to `models/40` | Tables the page reads |

## Entity relationship diagram

Primary keys on the `dim_` tables are enforced. Foreign keys are **not declared**: each line below
is checked by a data test in [`tests/`](../tests/) instead, so a bad row
shows up in the test report rather than crashing the load.

```mermaid
erDiagram
    dim_club ||--o{ stg_partnerships : "club_id"
    dim_brand ||--o{ stg_partnerships : "brand_id"
    dim_asset ||--o{ stg_partnerships : "asset_id"
    dim_category ||--o{ dim_brand : "category_id"
    stg_partnerships ||--|| partnership_history : "becomes, one row per deal"
    dim_club ||--o{ dim_match : "home_club_id, away_club_id"
    dim_club ||--o{ fact_pageviews_daily : "wikipedia_article = article"
    dim_brand |o--o{ fact_pageviews_daily : "wikipedia_article = article"

    dim_club {
        varchar club_id PK "project code, e.g. CHI"
        varchar club_name
        varchar short_name
        varchar city
        varchar state_province
        varchar country
        varchar conference
        varchar wikipedia_article "title used by the Pageviews API"
        varchar asa_team_name "name used by American Soccer Analysis"
    }

    dim_brand {
        varchar brand_id PK "slug, e.g. carvana"
        varchar brand_name
        varchar parent_company
        varchar category_id FK
        varchar wikipedia_article "null only when no_article_reason says why"
        varchar no_article_reason
        varchar notes
    }

    dim_category {
        varchar category_id PK
        varchar category_name
        varchar description
    }

    dim_asset {
        varchar asset_id PK "front_of_kit, sleeve, stadium_naming"
        varchar asset_name
        boolean exclusive_per_club "one brand at a time"
        varchar description
    }

    stg_partnerships {
        varchar club_id FK
        varchar brand_id FK
        varchar asset_id FK
        varchar kit_scope "all, primary or secondary"
        integer start_season
        varchar start_season_basis "announced or first_observed"
        integer end_season "null = no announced end"
        date start_date
        date end_date
        decimal reported_value_usd_per_year "null = not publicly reported"
        varchar reported_value_note
        varchar reported_value_source_url
        varchar source_type "primary, press or roundup"
        varchar source_url
        date date_checked
        varchar notes
        varchar sold_by "club or stadium_owner"
    }

    partnership_history {
        bigint partnership_id PK "row number, regenerated each build"
        varchar club_id FK
        varchar brand_id FK
        varchar asset_id FK
        varchar kit_scope
        varchar start_season_basis
        date valid_from
        date valid_to "inclusive; 9999-12-31 = open"
        decimal reported_value_usd_per_year
        varchar reported_value_note
        varchar reported_value_source_url
        varchar source_type
        varchar source_url
        date date_checked
        boolean is_current
    }

    dim_match {
        varchar match_id PK
        timestamp kickoff_utc
        date match_date_utc "same clock as pageviews"
        integer season
        varchar home_club_id FK
        varchar away_club_id FK
        integer home_score
        integer away_score
        varchar status
    }

    fact_pageviews_daily {
        varchar article "no PK; duplicates caught by a test"
        date view_date
        bigint views
    }
```

## Marts

The marts are derived tables the page reads. They're kept out of the diagram
above so it stays readable.

```mermaid
flowchart LR
    ph[partnership_history]
    fp[fact_pageviews_daily]
    dc[dim_club]
    db[dim_brand]
    dm[dim_match]
    da[dim_asset]
    dcat[dim_category]

    mad["mart_attention_daily<br/>entity x UTC day, 28-day baseline"]
    mml["mart_match_day_lift<br/>club x match"]
    mcs["mart_category_share<br/>asset x category"]
    mcsa["mart_club_sponsor_attention<br/>one row per club"]

    fp --> mad
    dc --> mad
    db --> mad
    mad --> mml
    dm --> mml
    ph --> mcs
    db --> mcs
    da --> mcs
    dcat --> mcs
    ph --> mcsa
    mad --> mcsa
```

| Mart | Grain | Answers |
|------|-------|---------|
| `mart_attention_daily` | One row per club or brand per UTC day | Daily pageviews against the trailing 28-day baseline |
| `mart_match_day_lift` | One row per club per match | How far a club's pageviews rise on match day |
| `mart_category_share` | One row per asset per category | Which categories buy each asset, among current deals |
| `mart_club_sponsor_attention` | One row per club | Attention its current sponsor brands get, last 28 days |

Pageviews are a proxy for public attention, never sponsor value.

## Notes on the joins

- **Pageviews join on article title**, not an id: `dim_club.wikipedia_article`
  and `dim_brand.wikipedia_article` match `fact_pageviews_daily.article`.
  `mart_attention_daily` stacks clubs and brands into one table with
  `entity_type` and `entity_id`.
- **As-of questions** use `partnership_history`:
  `WHERE DATE '2025-06-01' BETWEEN valid_from AND valid_to`. See
  [`sql/examples/as_of_kit_partner.sql`](../sql/examples/as_of_kit_partner.sql).
- **`sold_by`** stays in `stg_partnerships` and isn't carried into
  `partnership_history` yet.
