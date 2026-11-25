-- mart_lift_by_result: does a win draw more attention than a loss?
--
-- Grain: one row per result ('win', 'draw', 'loss') per venue ('home',
-- 'away'): six rows, pooled across clubs and seasons.
-- The result is from the club's point of view: the same 2-1 score is a win
-- for the home row and a loss for the away row. Correlation, not cause: a
-- UTC pageview day includes the hours before kickoff.

CREATE TABLE mart_lift_by_result AS
WITH scored AS (
    SELECT l.venue, l.lift_vs_baseline,
           CASE WHEN l.venue = 'home' THEN m.home_score ELSE m.away_score END AS goals_for,
           CASE WHEN l.venue = 'home' THEN m.away_score ELSE m.home_score END AS goals_against
    FROM mart_match_day_lift AS l
    JOIN dim_match AS m USING (match_id)
    WHERE l.lift_vs_baseline IS NOT NULL
)
SELECT
    CASE WHEN goals_for > goals_against THEN 'win'
         WHEN goals_for < goals_against THEN 'loss'
         ELSE 'draw' END                  AS result,
    venue,
    COUNT(*)                              AS matches,
    MEDIAN(lift_vs_baseline)              AS median_lift
FROM scored
WHERE goals_for IS NOT NULL AND goals_against IS NOT NULL
GROUP BY ALL;
