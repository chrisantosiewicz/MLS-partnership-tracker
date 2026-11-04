# site: the published page

One job: render the Quarto page from `tracker.duckdb` and publish it to
GitHub Pages (done by `.github/workflows/daily.yml`).

## Inputs
- `index.qmd`: page text and the queries it runs. `FEATURED_CLUB` sets the
  attention chart's club.
- `charts.py`: chart code and the `query()` helper.
- `_quarto.yml`: site settings and navbar.
- A built `tracker.duckdb` (run `python python/build.py` first).

Do NOT load: `_site/` (generated), `../data/raw/`.

## Process
Run `quarto render site` from the repo root and open `site/_site/index.html`.

## Human check
Chris reads every chart title and caption and confirms it says "attention",
never "value", and that each number matches a query he can rerun.
