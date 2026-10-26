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

**Chris's to-do (in order):**
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
