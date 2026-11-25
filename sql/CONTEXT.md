# sql: the warehouse build

One job: turn `data/` into tables and models in `tracker.duckdb`. Chris writes
the SQL; Claude explains and reviews.

## Inputs
- `schema.sql` (tables), `load.sql` (reads `data/`), then `models/*.sql` in
  file-name order (`10_`, `20_`, ...). Each model's header states its grain.
- Only the model you're working on, plus the models it reads from.
- `examples/`: hand-run queries, not part of the build.

Do NOT load: `../data/raw/*.parquet`, `../site/`, other models' internals
unless you join to them.

## Process
1. State the grain (one row = ?) in the file's header comment first.
2. Write the model; a new file takes the next free number in `models/`.
3. Run `python python/build.py` from the repo root. It rebuilds from scratch
   and runs every test.

## Outputs
- A `models/NN_name.sql` file and, usually, a test in `../tests/` for it.

## Human check
Chris explains the grain and one join out loud, and checks a few rows by hand
in DuckDB (`duckdb tracker.duckdb`).
