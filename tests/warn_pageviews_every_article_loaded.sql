-- Every club and brand article should have pageview data. A miss usually
-- means a wrong or renamed Wikipedia title in clubs.csv or brands.csv.
-- warn_ prefix: reported in the log, but does not fail the daily build.
WITH articles AS (
    SELECT wikipedia_article AS article FROM dim_club
    UNION
    SELECT wikipedia_article FROM dim_brand WHERE wikipedia_article IS NOT NULL
)
SELECT a.article
FROM articles AS a
WHERE NOT EXISTS (
    SELECT 1 FROM fact_pageviews_daily AS f WHERE f.article = a.article
);
