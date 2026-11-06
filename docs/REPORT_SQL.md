# SQL for the expanded report (Chris writes these)

The page and chart code for five new report sections is already in
`site/index.qmd` and `site/charts.py`. The charts read four tables that don't
exist yet. Write each one as a new file in `sql/models/`, then run
`python python/build.py` and `python site/charts.py` to see your output in
`site/_preview/`.

Each spec gives the grain, the exact columns the chart reads, and a toy
example of the main technique on made-up data, not on our tables. Work
through them in order: each one is a little harder than the one before.

| # | File | Table | Technique | Skill |
|---|------|-------|-----------|-------|
| 1 | `50_sponsor_directory.sql` | `mart_sponsor_directory` | Pivot with conditional aggregation, LEFT JOIN from a dimension | 1. SQL |
| 2 | `60_club_match_lift.sql` | `mart_club_match_lift` | `MEDIAN` + `FILTER` | 1. SQL |
| 3 | `70_lift_by_result.sql` | `mart_lift_by_result` | `CASE` from two perspectives | 1. SQL |
| 4 | `80_attention_by_season.sql` | `mart_attention_by_season` | Like-for-like date windows, `LAG` | 1. SQL |

Write a header comment for each file the way the existing models do: what the
table answers, its grain, and any rule a reader would question.

---

## 1. `mart_sponsor_directory`

**Answers:** who is on each club's kit right now?
**Grain:** one row per club. **All 30 clubs**, including clubs with no
recorded deal.

| Column | Meaning |
|--------|---------|
| `club_id`, `short_name`, `conference` | From `dim_club` |
| `front_of_kit_brand` | Current front-of-kit brand name(s); NULL if none recorded |
| `front_of_kit_category` | That brand's category name |
| `sleeve_brand`, `sleeve_category` | Same for the sleeve |
| `source_url` | One source for the club's row (NULL if no deals) |
| `date_checked` | Latest `date_checked` across the club's current deals |

**Watch out:** some clubs have two front-of-kit rows (`kit_scope` primary and
secondary: Dallas, Philadelphia) or two sleeve rows (Minnesota, Seattle).
Your table must still have one row per club. Show both brands in one cell,
e.g. `Children's Health / UT Southwestern`.

**Toy example: pivot with `FILTER`.** Rows become columns by aggregating
once per target column, each with its own filter:

```sql
WITH pets(owner, kind, name) AS (
    VALUES ('ana', 'cat', 'Miso'), ('ana', 'dog', 'Rex'),
           ('ben', 'dog', 'Fido'), ('ben', 'dog', 'Spot')
)
SELECT owner,
       STRING_AGG(name, ' / ') FILTER (WHERE kind = 'cat') AS cats,
       STRING_AGG(name, ' / ') FILTER (WHERE kind = 'dog') AS dogs
FROM pets
GROUP BY owner;
-- ana | Miso | Rex
-- ben | NULL | Fido / Spot
```

**Questions:** Why must the query start `FROM dim_club` and LEFT JOIN the
deals, rather than start from the deals? Where would you filter `is_current`:
in the WHERE clause or in a CTE before the join, and why does it matter?

**Suggested test:** `tests/test_sponsor_directory_one_row_per_club.sql`
returns any `club_id` that appears more than once, or any club in `dim_club`
that is missing.

---

## 2. `mart_club_match_lift`

**Answers:** which clubs' Wikipedia pages get the biggest bump on match day,
home and away?
**Grain:** one row per club per season.

| Column | Meaning |
|--------|---------|
| `club_id`, `season` | |
| `matches` | Matches with a lift value |
| `median_lift` | Median `lift_vs_baseline` across those matches |
| `median_lift_home`, `median_lift_away` | Same, home matches only / away only |

Read from `mart_match_day_lift`. Leave out rows where `lift_vs_baseline` is
NULL (there was no full 28-day baseline yet).

**Toy example: several aggregates with different filters in one pass.**

```sql
WITH scores(player, venue, pts) AS (
    VALUES ('ana', 'home', 10), ('ana', 'home', 30), ('ana', 'away', 5),
           ('ben', 'away', 8), ('ben', 'away', 12)
)
SELECT player,
       MEDIAN(pts)                              AS median_all,
       MEDIAN(pts) FILTER (WHERE venue = 'home') AS median_home
FROM scores
GROUP BY player;
-- ana | 10.0 | 20.0
-- ben | 10.0 | NULL
```

**Questions:** Why median and not average for lift? (Look at Inter Miami's
2023 days in `mart_attention_daily`.) Why does the chart default to the latest
season instead of pooling all four?

---

## 3. `mart_lift_by_result`

**Answers:** does a win draw more attention than a loss?
**Grain:** one row per result (`'win'`, `'draw'`, `'loss'`) per venue
(`'home'`, `'away'`): six rows.

| Column | Meaning |
|--------|---------|
| `result` | `'win'`, `'draw'` or `'loss'`, **from the club's point of view** |
| `venue` | `'home'` or `'away'` |
| `matches` | Club-matches in the group |
| `median_lift` | Median `lift_vs_baseline` |

`mart_match_day_lift` has one row per club per match, but no scores. The
scores are on `dim_match`. The trap: `home_score > away_score` is a win for
the home row and a loss for the away row of the same match.

**Toy example: CASE that depends on whose row it is.**

```sql
WITH games(game, side, my_goals_if_home, my_goals_if_away) AS (
    VALUES (1, 'home', 2, 1), (1, 'away', 2, 1)
)
SELECT game, side,
       CASE WHEN side = 'home' THEN my_goals_if_home ELSE my_goals_if_away END AS goals_for,
       CASE WHEN side = 'home' THEN my_goals_if_away ELSE my_goals_if_home END AS goals_against
FROM games;
-- 1 | home | 2 | 1   (a win)
-- 1 | away | 1 | 2   (a loss)
```

Once you have `goals_for` and `goals_against`, the result is one more CASE.

**Questions:** The page says this shows correlation, not cause. Why? (Hint:
what does a UTC pageview day include before kickoff?) A quick sanity check:
across all rows, should `win` and `loss` have the same count? Why?

**Suggested test:** wins = losses for each season, since every decided match
gives one of each.

---

## 4. `mart_attention_by_season`

**Answers:** which clubs are gaining public attention compared with last year?
**Grain:** one row per club per year.

| Column | Meaning |
|--------|---------|
| `club_id`, `season` | `season` = calendar year of `view_date` |
| `avg_daily_views` | Average daily views **from Jan 1 to the same day of year as the latest data** |
| `prev_avg_daily_views` | The same club's value for the year before |
| `change_vs_prev` | `avg_daily_views / prev_avg_daily_views - 1` |

Read club rows from `mart_attention_daily`.

**The design decision:** 2026 only runs to the latest day of data. Comparing
10 months of 2026 with all 12 of 2025 would be biased, because playoffs and
the off-season fall in the missing months. So every year uses the same
calendar window. `DAYOFYEAR()` is one way to do that. Leap years shift it by
a day; say in a comment whether that matters.

**Toy example: `LAG` for "the previous row's value".**

```sql
WITH sales(store, yr, total) AS (
    VALUES ('a', 2024, 100), ('a', 2025, 150), ('b', 2025, 80)
)
SELECT store, yr, total,
       LAG(total) OVER (PARTITION BY store ORDER BY yr) AS prev_total
FROM sales;
-- a | 2024 | 100 | NULL
-- a | 2025 | 150 | 100
-- b | 2025 |  80 | NULL
```

**Questions:** What happens without `PARTITION BY`? San Diego FC first played
in 2025: what does its 2025 row show, and is its 2026 change a fair comparison?

---

## When you're done

1. `python python/build.py` passes, including any tests you added.
2. `python site/charts.py` writes five charts to `site/_preview/`. Open them
   and check that the titles' numbers match a query you run by hand.
3. Push to the PR branch. Claude reviews the SQL and asks you to explain a few
   choices, and the answers go in `PROGRESS_LOG.md`.
