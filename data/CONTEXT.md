# data: research and the hand-maintained dataset

One job: add or correct sourced sponsorship rows. Chris does the research.

## Inputs
- `README.md`: the data dictionary and sourcing rules. Read this first.
- `TO_VERIFY.md`: the research queue.
- The CSV you're editing (`partnerships.csv`, `brands.csv`, ...).

Do NOT load: `raw/*.parquet` (pipeline output, large, never hand-edited),
`../sql/`, `../site/`.

## Process
1. Pick an item from `TO_VERIFY.md` or a new source.
2. Edit the CSV row following the sourcing rules: `source_url`,
   `source_type` and `date_checked` on every row. Values only if reported.
3. Run `python python/build.py` from the repo root. Every `test_` must pass.
4. Add a line to `../CHANGELOG.md`. Update or remove the `TO_VERIFY.md` item.

## Outputs
- Edited CSVs, `CHANGELOG.md` line, updated `TO_VERIFY.md`, in one PR.

## Human check
Chris opens each new `source_url` and confirms it says what the row says.
