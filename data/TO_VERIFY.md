# To verify

The research queue. When sources disagree, the row stays out of the CSVs and
goes here (sourcing rule 2 in `README.md`). Remove an item once it's settled
and the CSV change is in `../CHANGELOG.md`.

## Missing rows
- Stadium naming rights for all 30 clubs (none recorded yet).

## Sources disagree or unclear
- Portland away-kit front (Tillamook?).
- Magellan Corporation: which company, which category.

## Brands
- Confirm Wikipedia titles for brands marked "Article title not yet confirmed"
  in `brands.csv`, plus every title the daily run's `warn_` test lists.
- Puyallup Tribe: check the Wikipedia title.
- Intermountain Health (may still be "Intermountain Healthcare") and Select
  Health: confirm titles. Apollo (Apollo.io): confirm title.

## Upgrades
- San Jose history: Habbas Law held the right sleeve from May 2025
  (https://www.sjearthquakes.com/news/san-jose-earthquakes-and-habbas-law-announce-official-sleeve-partnership)
  until Apollo took it in July 2026. Needs a source for when Habbas Law's
  patch ended.
- Change some `first_observed` rows to `announced`, with real start seasons
  (needed for as-of history before 2026).
