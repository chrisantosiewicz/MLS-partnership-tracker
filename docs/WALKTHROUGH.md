# Walkthrough: how the pipeline works

Claude built the first version of everything here on Oct 26, 2026, at Chris's
request, so the project would be in place while he was at work. This document
is the teaching plan for going through it together afterward. **Chris should
be able to explain every line before any of it goes on a resume.**

Work through it in this order. Each section names the skill it practices, the
files, the ideas to understand, and questions to answer out loud or in
writing. Answers go in `PROGRESS_LOG.md`.

---

## 0. The big picture (15 min)

```
data/*.csv (hand-maintained)  ─┐
Wikimedia Pageviews API ──► python/wiki_pageviews.py ──► data/raw/pageviews.parquet ─┤
ASA API ──────────────────► python/asa_matches.py ───► data/raw/matches.parquet ───┤
                                                                                   ▼
                                 python/build.py: sql/schema.sql → sql/load.sql → sql/models/*.sql
                                                                                   ▼
                                                       tests/*.sql (must return 0 rows)
                                                                                   ▼
                                                    site/index.qmd → GitHub Pages
```

GitHub Actions (`.github/workflows/daily.yml`) runs that whole chain once a
day and commits the new raw data.

**Layers.** Raw files (exactly what the APIs returned, kept so we never have to
re-download history) → typed tables (`dim_`, `stg_`, `fact_`) → models that
answer questions (`partnership_history`, `mart_*`). Each layer only reads the
one before it.

**Questions**
1. Why keep raw API data in the repo instead of re-downloading it every day?
2. Why is `tracker.duckdb` in `.gitignore` while `data/raw/*.parquet` is committed?

---

## 1. Schema design (skill 1: SQL, schema design) · `sql/schema.sql`

Ideas to understand:
- **Grain.** Every table's comment says what one row is. Most SQL bugs are a
  grain mistake (joining two tables at different grains and duplicating rows).
- **Dimensions vs facts.** `dim_club` describes things; `fact_pageviews_daily`
  records measurements. Facts are big and narrow; dimensions are small and wide.
- **Natural vs surrogate keys.** `club_id` (`CHI`) and `brand_id` (`carvana`)
  are readable codes we control. Not using the full name as the key means a
  rename doesn't break joins.
- **Why primary keys on dims but no foreign keys.** A duplicate club id should
  stop everything. A deal pointing at a missing brand should show up in a
  readable test report, not crash the load.
- **Design decisions already made** (were the Week 1 design questions):
  grain of a deal row; category belongs to the brand; `kit_scope` for
  home/away splits; `reported_value_*` columns that can't be filled without a
  source; `end_season` blank = active.

**Questions**
1. What is the grain of `stg_partnerships`? What happens to the table when
   Carvana renews with the Fire? When the Fire switch to a new kit sponsor?
2. Why is `category_id` on `dim_brand` and not on the deal? Give a case where
   that would be wrong.
3. Why does `fact_pageviews_daily` have no primary key?

---

## 2. Loading (skill 1) · `sql/load.sql`

- `all_varchar = true` + explicit `CAST`s: we decide the types, not DuckDB's guesser.
- `NULLIF(TRIM(x), '')` turns empty CSV cells into real NULLs.
- `dim_match` uses **LEFT JOIN** to `dim_club` twice (home and away) so an
  unknown team name becomes a NULL that a test catches, instead of the match
  silently disappearing (which an INNER JOIN would do).

**Questions**
1. What would go wrong if `dim_match` used INNER JOINs?
2. Why join `dim_club` twice with two aliases?

---

## 3. Type 2 history and as-of joins (skill 1) · `sql/models/10_partnership_history.sql`

- Turns seasons into `valid_from` / `valid_to` dates. Open-ended deals get
  `9999-12-31`, so `BETWEEN` works without NULL checks.
- **As-of join:** `WHERE DATE '2025-06-01' BETWEEN valid_from AND valid_to`.
  Try `sql/examples/as_of_kit_partner.sql`.
- `start_season_basis = 'first_observed'`: v0 rows only prove the 2026 season,
  so asking about 2025 returns "unknown", never a wrong answer.

**Exercise:** write the as-of query for "who was on each club's sleeve on
2026-05-01?" yourself, without looking at the example.

**Questions**
1. Why is `valid_to` inclusive here, and what changes if it were exclusive?
2. What's the difference between this and just storing a `current_sponsor` column on `dim_club`?

---

## 4. Window functions with frames (skill 1) · `sql/models/20_attention_daily.sql`

The core analytic model. Read the CTEs top to bottom:
1. `entities`: clubs and brands stacked with `UNION ALL` into one list.
2. `article_span`: first and last day of data per article.
3. `spine`: one row per entity per day (`GENERATE_SERIES` + `UNNEST`).
4. `filled`: LEFT JOIN the real views onto the spine; missing day = 0.
5. `with_baseline`: `AVG(views) OVER (... ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING)`.

Ideas to understand:
- **Why a date spine.** `ROWS BETWEEN 28 PRECEDING` counts rows, not days. If
  the API skipped a day, 28 rows would cover 29 days. The spine makes rows = days.
- **Why exclude the current day.** A match-day spike would otherwise raise its
  own baseline and understate its lift.
- **Why `baseline_days = 28`.** The first 28 days of an article don't have a
  full baseline, so they get NULL instead of a misleading average.
- Named `WINDOW w AS (...)` avoids repeating the frame.

**Questions**
1. What's the difference between `ROWS BETWEEN` and `RANGE BETWEEN`? When would RANGE be enough?
2. Is filling missing days with 0 always right? When could it be wrong?
3. Explain `lift_vs_baseline = views / baseline_avg - 1` in plain English.

---

## 5. Match-day lift (skills 1 and 5) · `sql/models/30_match_day_lift.sql`

- `UNION ALL` "unpivots" a match into two rows (home club, away club).
- Match day uses the **UTC** kickoff date because Wikimedia days are UTC. A
  7:30pm Pacific kickoff is 02:30 UTC the next day.

**Questions**
1. Why can't we just join `dim_match` to pageviews on `home_club_id`?
2. A partnerships VP asks "so our sponsor gets 40% more exposure on match days?"
   What do you say?

---

## 6. CTE-heavy reporting (skills 1 and 5) · `sql/models/40_category_landscape.sql`

- `SUM(deals) OVER (PARTITION BY asset_id)` gives each category's share of an
  asset without a second GROUP BY.
- `PERCENT_RANK()` ranks clubs by their current sponsors' combined brand attention.
- `COUNT(*)` vs `COUNT(br.brand_id)` after a LEFT JOIN: total sponsors vs
  sponsors that have pageview data.
- Home/away splits count as two deals (Dallas has two front-of-kit health
  partners). That's a choice; say it in the methods note if it matters.

**Questions**
1. Why `SELECT DISTINCT club_id, brand_id` in `club_sponsors`? What breaks without it?
2. Not built yet: "deals by market size". What data would you need, and where would you source it?

---

## 7. Tests as queries (skill 1) · `tests/*.sql`

- Each test returns the **rows that break a rule**. Zero rows = pass.
- `test_` fails the build; `warn_` only prints (used for the Wikipedia title
  check so one renamed article doesn't take the whole site down).
- The overlap test is the classic interval check: two ranges overlap when
  `a.start <= b.end AND b.start <= a.end`. `a.partnership_id < b.partnership_id`
  avoids comparing a row with itself or each pair twice.

**Exercise:** write one new test yourself: "no brand appears in `brands.csv`
without any deal in `partnerships.csv`". Decide whether it's a `test_` or `warn_`.

**Questions**
1. Why test with queries instead of database constraints?
2. Why is the overlap test written with `kit_scope = ... OR 'all' IN (...)`?

---

## 8. Python ingestion (skills 2 and 3) · `python/wiki_pageviews.py`, `python/asa_matches.py`, `python/config.py`

- **Incremental:** `last_loaded_day()` → `next_start()`: only ask for days after the last one we have.
- **Idempotent:** `merge_and_save()` dedupes with `QUALIFY ROW_NUMBER() ... = 1`
  (latest fetch wins). Running twice changes nothing; `tests/python/test_wiki_pageviews.py` proves it.
- **Retries:** `make_session()` retries 429 and 5xx with exponential backoff and honours `Retry-After`.
- **Atomic write:** write a temp file, then rename, so a crash never leaves half a file.
- **Polite to the API:** descriptive User-Agent, one request at a time (Wikimedia's policy).
- ASA matches are a **full refresh** (small table, schedules change), which is idempotent by construction.
- `REQUIRED_FIELDS`: fail loudly if ASA renames a field.

**Questions**
1. "Incremental" and "idempotent": define each and show the line of code that delivers it.
2. Why does pageviews ingestion stop at yesterday?
3. Why does a 404 log a warning instead of crashing?
4. Run `pytest -q tests/python` and explain what `test_merge_is_idempotent` proves.

---

## 9. GitHub Actions (skill 2) · `.github/workflows/daily.yml`, `ci.yml`

- `schedule` (cron, UTC), `workflow_dispatch` (manual button), `push` (on code changes).
- Steps run in order; a failed step stops the job. Tests run **before** the
  data commit and deploy, so bad data never reaches the site.
- `permissions:` grant only what's needed (commit, publish pages).
- `ci.yml` runs the Python unit tests on every pull request.

**Questions**
1. If the overlap test fails at 09:17 tomorrow, what does the site show, and what happens to that day's pageviews?
2. Read a failed run's log and find the failing step (we'll do this live on the first failure).

---

## 10. The page (skill 6) · `site/index.qmd`, `site/charts.py`

- Chart titles **state the finding**, computed from the data.
- Methods and limitations: pageviews = attention, not value; UTC match days;
  season-based dates; reported values only with sources.

**Questions**
1. Rewrite the landscape chart's title for a partnerships VP in under 12 words.
2. What's the single biggest limitation a hiring manager will poke at?

---

## Interview defense (skill 7), end of walkthrough
1. "Walk me through how a new day of data gets onto the page."
2. "How do you know your sponsor data is right?"
3. "What does a 300% match-day lift actually mean for a sponsor?"
