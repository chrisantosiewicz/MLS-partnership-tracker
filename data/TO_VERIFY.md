# To verify

The research queue. When sources disagree, the row stays out of the CSVs and
goes here (sourcing rule 2 in `README.md`). Remove an item once it's settled
and the CSV change is in `../CHANGELOG.md`.

## Missing rows
- Stadium naming rights for all 30 clubs (none recorded yet).
- Sleeve partners for Houston, New England, Orlando and San Jose. Checked
  2026-11-05: no club, kit or press page found names a 2026 sleeve partner for
  Houston, New England or Orlando (they may have none). San Jose: Habbas Law
  took the right sleeve in May 2025
  (https://www.sjearthquakes.com/news/san-jose-earthquakes-and-habbas-law-announce-official-sleeve-partnership);
  needs a 2026 source before it goes in.

## Sources disagree or unclear
- Portland away-kit front (Tillamook?).
- Magellan Corporation: which company, which category.

## Brands
- Confirm Wikipedia titles for brands marked "Article title not yet confirmed"
  in `brands.csv`, plus every title the daily run's `warn_` test lists.
- Puyallup Tribe: check the Wikipedia title.
- Intermountain Health (may still be "Intermountain Healthcare") and Select
  Health: confirm titles.

## Upgrades
- Change some `first_observed` rows to `announced`, with real start seasons
  (needed for as-of history before 2026).
