# Progress log

One entry per week. Newest at the top. This file plus `Skill Tracker.md` and `CHANGELOG.md` are the project's memory between sessions, so keep them up to date.

## Week 1: Oct 26 to Nov 1, 2026 (Foundations)

**Change of plan (Oct 26):** Chris asked Claude to build the whole foundation now and teach it afterward ("walk through the stuff with me and educate in hindsight"). The original plan is kept in [`docs/week1-plan.md`](docs/week1-plan.md). The teaching plan is [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md).

**Done (built by Claude, Oct 26):**
- Repo created (Chris). Scaffold, licenses, data dictionary.
- SQL: schema, loads, `partnership_history`, attention baseline, match-day lift, category landscape, 13 tests + 1 warning.
- Python: pageviews ingestion (incremental, idempotent, retries), ASA match ingestion, 11 unit tests.
- GitHub Actions daily build + PR checks; Quarto page with two charts.
- Dataset v0: 57 rows (2026 front of kit for 29 clubs, sleeve for 24), 54 brands.
- Not yet run against the live APIs: the build machine couldn't reach Wikimedia or ASA. The first GitHub Actions run is the first live test.

**Status (Oct 30):**
- Page is live: https://chrisantosiewicz.github.io/MLS-partnership-tracker/
- Daily build failures on Oct 29 (manual rerun and the scheduled run) were the ASA API timing out after 30s. Fixed by PR #2 (retries, current season only, keeps saved matches if ASA is down); the build right after the merge passed and published.
- GitHub fired the 09:17 UTC schedule about 7 hours late on its first day. Normal for GitHub; nothing to fix.
- First findings: health care holds 8 of 31 front-of-kit deals; median match-day lift in club pageviews is about +24% across clubs, about +56% for St. Louis City over the last year.

**Next steps:** see "Plan to Nov 15" below.

**Original to-do (Oct 26; items 1 to 3 done):**
1. Review and merge PR #1.
2. Turn on Pages: repo Settings → Pages → Source: **GitHub Actions**.
3. Actions tab → "Daily build" → **Run workflow**. The first run backfills about 3 years of pageviews and takes a few minutes. Share the log if it fails.
4. Work through `docs/WALKTHROUGH.md` with Claude (about 4 to 5 hours across the week). Answer the questions below.
5. Research (about 3 hours), following the sourcing rules in `data/README.md`:
   - Stadium naming rights for all 30 clubs (none recorded yet).
   - To verify: Real Salt Lake front and sleeve (sources disagree: Intermountain Health vs Select Health); Portland away-kit front (Tillamook?); sleeve partners for Dallas, Houston, New England, Orlando, San Jose; Magellan Corporation (which company, which category).
   - Confirm Wikipedia titles for the brands marked "Article title not yet confirmed" in `brands.csv`, plus every title the daily run's `warn_` test lists.
   - Upgrade a few `first_observed` rows to `announced` with real start seasons (needed for as-of history before 2026).
6. Pick the club for the attention chart (default: St. Louis City SC, `FEATURED_CLUB` in `site/index.qmd`).

**Plan to Nov 15** (about 9 hours a week)

Rest of Week 1 (Oct 30 to Nov 1, ~4h)
1. Walkthrough sections 0 to 4 with Claude: big picture, schema, loads, type 2 history, the attention window function (~2.5h). Answer the questions in writing below.
2. CTE practice: SQLBolt or Mode, then 5 timed LeetCode database problems (~1.5h).

Week 2 (Nov 2 to 8, ~9h)
3. Walkthrough sections 5 to 10: match-day lift, landscape, tests, Python, Actions, page (~2.5h).
4. Write your first piece yourself: one new data test (walkthrough section 7 exercise) and the sleeve as-of query (section 3), reviewed by Claude (~1h).
5. Research (~3.5h): stadium naming rights for all 30 clubs; the "to verify" list above; real start seasons for front-of-kit deals.
6. Pick the featured club for the attention chart. Tag `v0.1` and write its CHANGELOG entry (~0.5h).
7. Confirm two scheduled daily runs in a row passed (Nov 15 goal).

Week 3 (Nov 9 to 15, ~9h)
8. Website kit: 120-word summary, architecture diagram, ERD, methods and limitations paragraph, links, "what's next" roadmap. Add the sponsorship tab to the Quarto site.
9. Interview defense: 3 hiring-manager questions, answered in writing. Then draft resume bullets and a LinkedIn post from what's actually built and what you can explain.
10. Maintenance (Claude): move GitHub Actions to Node 24 versions before the Node 20 deprecation bites.

**CTE practice log** (still worth doing; the walkthrough leans on CTEs):
| Problem | Time | Why these CTEs |
|---------|------|----------------|
| | | |

**Decisions made:**
- Licenses: MIT for code, CC BY 4.0 for `data/`.
- Changes go in through pull requests that Chris reviews.
- Deal grain: club × brand × asset × kit × continuous span. Category belongs to the brand.
- Home/away splits recorded with `kit_scope`; the league-wide Apple TV left-sleeve patch is not recorded (it's a league asset, not a club sale).
- v0 rows use `start_season_basis = first_observed` (2026) until real start seasons are sourced.
- A bad Wikipedia title only warns; every other data test fails the daily build.
- Match day = UTC date of kickoff, to match Wikimedia's UTC days.

**Interview questions and feedback:**
-

**Hours actually spent:**
