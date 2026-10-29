# Week 1 plan: Oct 26 to Nov 1, 2026

> **Superseded on Oct 26:** Chris asked Claude to build the foundation now and teach it afterward. See `PROGRESS_LOG.md` for the current to-do list and `docs/WALKTHROUGH.md` for the teaching plan. The design questions below are now answered in `data/README.md` and `docs/WALKTHROUGH.md` section 1.

**Goal for the week:** `data/partnerships.csv` (v0, about 90 sourced rows) loads into DuckDB through your `sql/schema.sql`, and your data-quality tests return zero rows.

**Budget:** 9 hours (range 8 to 10). $0 spend.

| # | Task | Hours | Skill it practices | Done when |
|---|------|-------|--------------------|-----------|
| 1 | CTE practice: SQLBolt or Mode's SQL tutorial (CTE / subquery sections), then about 10 timed LeetCode database problems, solving each with at least one CTE | 3.0 | 1. SQL beyond coursework | You've logged each problem, its time, and one line on why you split it into the CTEs you did |
| 2 | Create the repo `mls-partnership-tracker` (`python/`, `sql/`, `tests/`, `data/`, `site/`, README stub, `.gitignore`, MIT or CC license choice), and connect it here | 0.5 | 2. Data pipelines | Repo is on GitHub and I can see it |
| 3 | Agree the column contract and allowed values for the CSV (category list, asset list, how to record "not reported") before collecting anything | 0.5 | 5. Partnership analysis thinking | A short `data/README.md` data dictionary you wrote |
| 4 | Write `sql/schema.sql`: `dim_club`, `dim_brand`, `dim_category`, and a staging table for the CSV. Stub `dim_match`, `fact_pageviews_daily`, `partnership_history` (filled in Week 2) | 1.5 | 1. Schema design | `duckdb tracker.duckdb < sql/schema.sql` runs clean twice in a row |
| 5 | Build dataset v0: for all 30 clubs, front-of-kit, sleeve and stadium naming partner, each from a primary source (club or brand press release first, then credible press) | 3.0 | 4. Research and sourcing | About 90 rows, every row has `source_url` and `date_checked` |
| 6 | Write the first tests in `tests/` as queries that must return zero rows (see list below), load the CSV, run them | 0.5 | 1. Writing tests as queries | All tests return 0 rows |

### Order I suggest
Tasks 2 and 3 first (Sunday or Monday, 1 hour), then 1 (spread over 2 or 3 sittings), then 4, then 5 and 6 together. Doing 4 before 5 means the schema forces you to decide things like "what is a category" before you have 90 rows to fix.

### Design questions to answer before you write `schema.sql`
Bring me your answers. These are the ones a reviewer would ask about.
1. **Grain.** What does one row of `partnerships.csv` mean? (One brand on one asset for one club over one span of seasons? What happens when a deal is renewed?)
2. **Keys.** Natural key or surrogate key for `dim_club` and `dim_brand`? What do you do when "Audi" and "Audi of America" both show up?
3. **Brand vs. Wikipedia article.** A brand might have no article, or share one with its parent company. Where does `wiki_article` live, and is it nullable?
4. **Category.** Is it a property of the brand (Audi is "Automotive") or of the deal? Can one brand sit in two categories?
5. **Reported value.** How will you store "not publicly reported" vs. "reported as $X per year" vs. "reported as $X over N years"?
6. **Open-ended deals.** How does `end_season` look for a current deal with no announced end?

### Tests to write this week (each must return zero rows)
- Every row has a non-empty `source_url` and `date_checked`.
- `category` is in the allowed list (`dim_category`).
- `asset` is in the allowed list.
- `end_season` is null or on/after `start_season`.
- No club has two front-of-kit partners whose season ranges overlap. *(This one needs a self-join or a window function. Good CTE practice.)*
- Every club in the CSV exists in `dim_club`, and all 30 clubs appear at least once.

## A small worked CTE example (not from this project)
Same idea you'll use later, on a toy table `games(team, game_date, goals)`:

```sql
-- Which teams scored above their own season average in their last game?
WITH team_avg AS (            -- step 1: one row per team
    SELECT team, AVG(goals) AS avg_goals
    FROM games
    GROUP BY team
),
last_game AS (                -- step 2: one row per team, latest game only
    SELECT team, goals,
           ROW_NUMBER() OVER (PARTITION BY team ORDER BY game_date DESC) AS rn
    FROM games
)
SELECT l.team, l.goals, a.avg_goals
FROM last_game l
JOIN team_avg a USING (team)  -- both CTEs are one row per team, so no fan-out
WHERE l.rn = 1
  AND l.goals > a.avg_goals;
```

What to notice: each CTE has one job and a name that says it, you can `SELECT * FROM team_avg` on its own to debug it, and the comment on the join states the grain so a reviewer knows it can't duplicate rows. That is the habit I'll review for.

## Sourcing rules for v0 (until we write them up properly)
- Primary source first: the club's or brand's own announcement. Press (The Athletic, SportsBusiness Journal, local papers) when no primary exists. No fan wikis as the only source.
- `date_checked` is the date you opened the source, in `YYYY-MM-DD`.
- If you can't verify a row, leave it out and note it in the progress log. A blank is better than a guess.
- Reported values only with a source that states them, labelled "reported".

## End of week
Send me: the repo link, `schema.sql`, the CSV, the test output, and your CTE practice log. I'll review the SQL, then ask you 2 or 3 interview questions on schema design.
