-- Rule: mart_brand_portfolio and mart_club_category_map each account for
-- every current deal exactly once.
SELECT 'brand_portfolio' AS mart, (SELECT SUM(deals) FROM mart_brand_portfolio) AS deals
WHERE (SELECT SUM(deals) FROM mart_brand_portfolio)
   <> (SELECT COUNT(*) FROM partnership_history WHERE is_current)
UNION ALL
SELECT 'club_category_map', (SELECT SUM(deals) FROM mart_club_category_map)
WHERE (SELECT SUM(deals) FROM mart_club_category_map)
   <> (SELECT COUNT(*) FROM partnership_history WHERE is_current);
