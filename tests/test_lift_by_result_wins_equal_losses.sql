-- Rule: every decided match gives one win and one loss. Among matches where
-- both clubs have a lift value, wins in mart_lift_by_result's logic must
-- equal losses.
WITH pairs AS (
    SELECT match_id
    FROM mart_match_day_lift
    WHERE lift_vs_baseline IS NOT NULL
    GROUP BY match_id
    HAVING COUNT(*) = 2
),
results AS (
    SELECT CASE WHEN m.home_score = m.away_score THEN 'draw'
                WHEN (l.venue = 'home') = (m.home_score > m.away_score) THEN 'win'
                ELSE 'loss' END AS result
    FROM mart_match_day_lift AS l
    JOIN pairs USING (match_id)
    JOIN dim_match AS m USING (match_id)
)
SELECT COUNT(*) FILTER (WHERE result = 'win')  AS wins,
       COUNT(*) FILTER (WHERE result = 'loss') AS losses
FROM results
HAVING COUNT(*) FILTER (WHERE result = 'win') <> COUNT(*) FILTER (WHERE result = 'loss');
