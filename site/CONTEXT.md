# site: the published page

One job: render the Quarto page from `tracker.duckdb` and publish it to
GitHub Pages (done by `.github/workflows/daily.yml`).

## Inputs
- `index.qmd` (Overview), `sponsors.qmd`, `brands.qmd`, `clubs.qmd`,
  `attention.qmd`, `methods.qmd`: page
  text and the queries each runs. `FEATURED_CLUB` in `attention.qmd` sets the
  club the attention chart opens on.
- `charts.py`: every chart returns a `Chart` (figure, finding title,
  subtitle, note, data table); `card()` turns it into the page's HTML card.
  Also the `query()` helper, KPI tiles and the sponsor directory.
- `styles/`: `brand.scss` (layout and components) and `light.scss` (color
  tokens). Light theme only (Chris, Nov 25: dark mode not worth the upkeep).
- `assets/theme.js`: wires the club picker and the directory filter.
- `_quarto.yml`: pages, navbar, themes, and the pinned Plotly.js script.
- A built `tracker.duckdb` (run `python python/build.py` first).

Do NOT load: `_site/` (generated), `../data/raw/`.

## Process
Run `quarto render site` from the repo root and open `site/_site/index.html`.
`python site/charts.py` writes each chart on its own to `site/_preview/`.
Plotly.js is loaded from jsDelivr at the version in `_quarto.yml`; keep it
equal to `plotly.offline.get_plotlyjs_version()` when upgrading `plotly`.

## Human check
Chris reads every chart title and caption and confirms it says "attention",
never "value", and that each number matches a query he can rerun.
