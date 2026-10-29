-- At most one row per article per day.
SELECT article, view_date, COUNT(*) AS copies
FROM fact_pageviews_daily
GROUP BY article, view_date
HAVING COUNT(*) > 1;
