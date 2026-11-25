# python: ingestion and the build runner

One job: fetch API data into `data/raw/` and run the SQL build.

| File | Does |
|------|------|
| `config.py` | Paths, backfill start date, User-Agent, raw file columns |
| `wiki_pageviews.py` | Wikimedia pageviews → `data/raw/pageviews.parquet` (incremental) |
| `asa_matches.py` | American Soccer Analysis matches → `data/raw/matches.parquet` |
| `build.py` | Rebuilds `tracker.duckdb` and runs every data test |

Do NOT load: `data/raw/*.parquet`, `site/`. Unit tests are in
`../tests/python/`.

## Process
Run from the repo root: `python python/<script>.py`, then
`pytest -q tests/python`. Respect each API's terms: one request at a time to
Wikimedia, with the descriptive User-Agent.

## Human check
Chris reads the GitHub Actions log of the next daily run and confirms the
fetch step reported new rows.
