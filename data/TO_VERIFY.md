# To verify

The research queue. When sources disagree, the row stays out of the CSVs and
goes here (sourcing rule 2 in `README.md`). Remove an item once it's settled
and the CSV change is in `../CHANGELOG.md`.

## Missing rows
- Chicago Fire's planned stadium is McDonald's Park (opening 2028). Add it
  when the club moves.

## Sources disagree or unclear
- Portland away-kit front (Tillamook?). Nov 25: Bank of America replaced
  Tillamook on the front from 2026 and Tillamook moved to the sleeve (already
  in the CSV; headline of the release as carried by Barchart: "BofA Becomes
  Front of Jersey Partner, Tillamook to Remain on Kit With Sleeve Patch",
  https://www.barchart.com/story/news/36532149/portland-timbers-enter-multi-year-community-impact-partnership-with-bank-of-america).
  Still unconfirmed: whether Bank of America is on the secondary
  kit too, so the BofA row stays `kit_scope = primary`. A Barchart copy of the
  BofA release returned no text; find the club's own release.
- Magellan Corporation: which company, which category.

## Brands
- Confirm Wikipedia titles for brands marked "Article title not yet confirmed"
  in `brands.csv`, plus every title the daily run's `warn_` test lists.
- Puyallup Tribe: check the Wikipedia title.
- Intermountain Health (may still be "Intermountain Healthcare") and Select
  Health: confirm titles. Apollo (Apollo.io): confirm title.
- New stadium brands: confirm the titles the next daily run's `warn_` test
  lists (pageviews for them start on that run).

## Checked Nov 25 (no CSV change)
- Sporting KC stadium: KC Soccer Journal (Dec 14, 2025) says the new 2026 name
  "is not yet known". English Wikipedia now titles the article "Sporting Park",
  which suggests an unsponsored name. No row until a naming partner is
  announced.

## Upgrades
- San Jose history: Habbas Law held the sleeve from Saturday, May 3 (2025
  season), on both kits
  (https://www.sjearthquakes.com/news/san-jose-earthquakes-and-habbas-law-announce-official-sleeve-partnership).
  Apollo's release (debut ahead of July 25, 2026) doesn't mention Habbas Law.
  Still needed: a source saying whether Habbas Law's patch carried into 2026
  before Apollo. Without it the row would need a guessed end date, so it stays
  out (checked Nov 25).
- Change some `first_observed` rows to `announced`, with real start seasons
  (needed for as-of history before 2026).
