# tests: data tests and unit tests

One job: catch bad data before it's published.

## Inputs
- `*.sql`: each file is a query that returns the rows breaking one rule.
  `test_*.sql` must return zero rows or the daily build fails. `warn_*.sql`
  rows are printed but don't fail the build (known gaps).
- `python/`: pytest unit tests for the ingestion scripts (no network).
- The table the rule is about (`../sql/schema.sql` or the model file).

Do NOT load: `../data/raw/`, `../site/`.

## Process
1. Write the rule as a one-line comment at the top of the file.
2. Name it `test_<table>_<rule>.sql` (or `warn_` for a gap we track).
3. Run `python python/build.py` for data tests and `pytest -q tests/python`
   for unit tests.

## Outputs
- One new `.sql` file per rule. `build.py` picks it up automatically.

## Human check
Chris breaks a CSV row on purpose and confirms the new test catches it, then
reverts the row.
