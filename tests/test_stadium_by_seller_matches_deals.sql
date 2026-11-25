-- Rule: mart_stadium_naming_by_seller counts every current stadium naming
-- deal exactly once (no deal lost or doubled by the sold_by join).
SELECT
    (SELECT SUM(deals) FROM mart_stadium_naming_by_seller)                       AS in_mart,
    (SELECT COUNT(*) FROM partnership_history
     WHERE is_current AND asset_id = 'stadium_naming')                           AS in_history
WHERE (SELECT SUM(deals) FROM mart_stadium_naming_by_seller)
   <> (SELECT COUNT(*) FROM partnership_history
       WHERE is_current AND asset_id = 'stadium_naming');
