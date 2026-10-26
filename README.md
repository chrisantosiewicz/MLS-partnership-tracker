# MLS Partnership Tracker

A sourced, versioned dataset of MLS club sponsorships, plus a daily pipeline
that tracks public attention (Wikipedia pageviews) for each club and sponsor
brand. It powers the sponsorship page of Chris Antosiewicz's portfolio site.

> **Status:** foundations in progress. Dataset v0 covers 2026 front-of-kit
> (29 clubs) and sleeve (24 clubs) partners. Stadium naming rights are next.

## How it works

```
data/*.csv (hand-maintained) ───────────────────────────────┐
Wikimedia Pageviews API → python/wiki_pageviews.py → data/raw/pageviews.parquet ─┤
American Soccer Analysis → python/asa_matches.py → data/raw/matches.parquet ─────┤
                                                                                 ▼
        python/build.py: sql/schema.sql → sql/load.sql → sql/models/*.sql → tests/*.sql
                                                                                 ▼
                                                      site/ (Quarto) → GitHub Pages
```

GitHub Actions runs the whole chain daily (`.github/workflows/daily.yml`). If
any data test fails, nothing is published and the previous page stays up.

| Folder | What's in it |
|--------|--------------|
| `data/` | Hand-maintained CSVs and the [data dictionary](data/README.md); `raw/` holds API data |
| `sql/` | `schema.sql`, `load.sql`, and `models/` (history, attention baseline, match-day lift, category landscape) |
| `tests/` | Data tests: queries that must return zero rows. `tests/python/` has unit tests |
| `python/` | Ingestion scripts and the build runner |
| `site/` | Quarto page and chart code |
| `docs/` | [Walkthrough](docs/WALKTHROUGH.md) and weekly plans |

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python python/wiki_pageviews.py    # fetch pageviews (first run backfills from 2023)
python python/asa_matches.py       # fetch MLS matches
python python/build.py             # build tracker.duckdb and run every data test
pytest -q tests/python             # unit tests for the ingestion code
quarto render site                 # build the page into site/_site/
```

## Sources and credits

- **Sponsorship rows:** each row cites its source in `source_url`, with the
  date it was checked.
- **Pageviews:** [Wikimedia Analytics API](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/),
  released under CC0. Requests send a descriptive User-Agent and run one at a
  time, per Wikimedia's access policy. Pageviews are a proxy for public
  attention, not sponsor value.
- **Matches:** [American Soccer Analysis](https://www.americansocceranalysis.com/)
  via the `itscalledsoccer` package. Thanks to ASA for a free, public API.

## License

Code: [MIT](LICENSE). Dataset files in `data/`: [CC BY 4.0](data/LICENSE.md).

## Project tracking

- [`CHANGELOG.md`](CHANGELOG.md): dataset and pipeline changes
- [`PROGRESS_LOG.md`](PROGRESS_LOG.md): weekly plan, what got done, decisions
- [`Skill Tracker.md`](Skill%20Tracker.md): skills practiced, with evidence
