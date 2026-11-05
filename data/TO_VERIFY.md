# To verify

The research queue. When sources disagree, the row stays out of the CSVs and
goes here (sourcing rule 2 in `README.md`). Remove an item once it's settled
and the CSV change is in `../CHANGELOG.md`.

## Missing rows
- Stadium naming rights, two clubs left (checked 2026-11-05; 26 recorded,
  and Chicago, NYCFC and Vancouver play in unsponsored stadiums):
  - Sporting KC: Children's Mercy Park's naming deal ended after 2025
    (https://www.kctv5.com/2025/12/12/sporting-kc-ends-partnership-with-childrens-mercy-begins-new-deal-with-saint-lukes/).
    What is the stadium called in 2026, and does anyone hold the rights?
  - CF Montréal: Stade Saputo carries the name of Saputo Inc., the owner
    family's company. Find a source saying whether it's a paid naming deal.
- Chicago Fire's planned stadium is McDonald's Park (opening 2028). Add it
  when the club moves.

## Sources disagree or unclear
- Portland away-kit front (Tillamook?).
- Magellan Corporation: which company, which category.

## Brands
- Confirm Wikipedia titles for brands marked "Article title not yet confirmed"
  in `brands.csv`, plus every title the daily run's `warn_` test lists.
- Puyallup Tribe: check the Wikipedia title.
- Intermountain Health (may still be "Intermountain Healthcare") and Select
  Health: confirm titles. Apollo (Apollo.io): confirm title.
- New stadium brands: confirm the titles the next daily run's `warn_` test
  lists (pageviews for them start on that run).

## Upgrades
- San Jose history: Habbas Law held the right sleeve from May 2025
  (https://www.sjearthquakes.com/news/san-jose-earthquakes-and-habbas-law-announce-official-sleeve-partnership)
  until Apollo took it in July 2026. Needs a source for when Habbas Law's
  patch ended.
- Change some `first_observed` rows to `announced`, with real start seasons
  (needed for as-of history before 2026).
