# docs: coaching and project state

One job: keep track of where Chris is, what he's learning, and what was decided.
Nothing here is read by the pipeline.

| File | What it holds |
|------|---------------|
| `PROGRESS_LOG.md` | Current week's plan and status, newest week on top |
| `SKILL_TRACKER.md` | Skill ratings with evidence, updated weekly |
| `DECISIONS.md` | Standing decisions. One line each, with the date |
| `WALKTHROUGH.md` | Teaching plan for the Claude-built foundation |
| `REPORT_SQL.md` | Specs for the report-expansion models (arrives with PR #4) |
| `_archive/` | Superseded plans and finished weeks of the log |

## Start of a session

1. Read the top (current week) of `PROGRESS_LOG.md` and `SKILL_TRACKER.md`.
   Skim `../CHANGELOG.md` for what changed since last time.
2. Ask Chris what he finished. Plan 8 to 10 hours for the week.
3. Go to the folder for the task (routing table in `../CLAUDE.md`).

Do NOT load: `_archive/`, `WALKTHROUGH.md` unless doing the walkthrough,
`../data/raw/`.

## End of the week

1. Update this week's entry in `PROGRESS_LOG.md`: done, hours, answers.
2. Update `SKILL_TRACKER.md`. Ratings move only on evidence Chris can explain.
3. Add any new standing decision to `DECISIONS.md`.
4. Move the finished week's entry to `_archive/log-week-N.md` and link it
   from the log, so the log stays short.

## Human check

Chris reads the week's log entry and confirms the hours and ratings are his.
