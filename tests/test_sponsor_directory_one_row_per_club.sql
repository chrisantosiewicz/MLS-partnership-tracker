-- Rule: mart_sponsor_directory has exactly one row for every club in dim_club.
SELECT club_id, 'duplicate' AS problem
FROM mart_sponsor_directory GROUP BY club_id HAVING COUNT(*) > 1
UNION ALL
SELECT c.club_id, 'missing'
FROM dim_club AS c
LEFT JOIN mart_sponsor_directory AS d USING (club_id)
WHERE d.club_id IS NULL;
