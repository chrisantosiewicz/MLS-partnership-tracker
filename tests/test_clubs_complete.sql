-- MLS has 30 clubs in 2026. Returns one row if the count is wrong.
SELECT COUNT(*) AS clubs
FROM dim_club
HAVING COUNT(*) <> 30;
