# Decisions

Standing decisions, one line each. Add new ones at the bottom with a date.
When a decision changes, edit the line and note the old version.

- Licenses: MIT for code, CC BY 4.0 for `data/`. (Oct 26)
- Changes go in through pull requests that Chris reviews. (Oct 26)
- Deal grain: club × brand × asset × kit × continuous span. Category belongs to the brand. (Oct 26)
- Home/away splits recorded with `kit_scope`; the league-wide Apple TV left-sleeve patch is not recorded (it's a league asset, not a club sale). (Oct 26)
- v0 rows use `start_season_basis = first_observed` (2026) until real start seasons are sourced. (Oct 26)
- A bad Wikipedia title only warns; every other data test fails the daily build. (Oct 26)
- Match day for attention = UTC date two hours after kickoff (`attention_date_utc`), to match Wikimedia's UTC days. Was: UTC date of kickoff (Oct 26), which put most of a 7:30 pm ET match on the wrong day; median lift was understated (+24% vs +38%). (Nov 25)
- Repo layout follows ICM (github.com/RinDig/icm-architect, MIT): `CLAUDE.md` routes, each folder has a `CONTEXT.md`, the repo is the only home for project files. (Nov 4)
- Site is light theme only; dark mode was built and removed as not worth the upkeep. (Nov 25)
- Whitespace ("open categories") is a research list from the three tracked assets only. The site never says a club lacks a partner in a category. (Nov 25)
