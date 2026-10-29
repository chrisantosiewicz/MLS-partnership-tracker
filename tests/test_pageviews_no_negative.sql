-- Pageview counts can't be negative.
SELECT article, view_date, views
FROM fact_pageviews_daily
WHERE views < 0;
