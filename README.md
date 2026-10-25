# MLS Partnership Tracker

A sourced, versioned dataset of MLS club sponsorships, plus a daily pipeline
that tracks public attention (Wikipedia pageviews) for each club and sponsor
brand. It powers the sponsorship page of Chris Antosiewicz's portfolio site.

> **Status:** Week 1 of 3 (foundations). The dataset and schema are under
> construction. Nothing here is final yet.

## Layout

| Folder | What's in it |
|--------|--------------|
| `data/` | Hand-maintained CSVs (`partnerships.csv`, `clubs.csv`) and the data dictionary |
| `sql/` | `schema.sql` (tables), `load.sql` (loads the CSVs), later the models |
| `tests/` | Data-quality tests. Each is a query that must return zero rows |
| `python/` | Ingestion scripts and the test runner |
| `site/` | Quarto page (Week 3) |
| `docs/` | Weekly plans |

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python python/run_tests.py       # rebuilds tracker.duckdb and runs every test
```

The runner exits with an error if any test returns rows.

## Sources

- Sponsorship rows: each row cites its own source in `source_url`.
- Wikimedia Pageviews API (from Week 2), used as a proxy for public attention,
  not sponsor value.
- American Soccer Analysis (from Week 2), for MLS schedules and results.

## License

Code: [MIT](LICENSE). Dataset files in `data/`: [CC BY 4.0](data/LICENSE.md).

## Project tracking

- [`PROGRESS_LOG.md`](PROGRESS_LOG.md): weekly plan, what got done, decisions
- [`Skill Tracker.md`](Skill%20Tracker.md): skills practiced, with evidence
