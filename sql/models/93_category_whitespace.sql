-- mart_category_whitespace: categories that several MLS clubs sell their
-- major assets to, but a given club doesn't (in the tracked assets).
--
-- Grain: one row per club x category, for categories bought at 3 or more
-- other clubs and absent from this club's current tracked deals.
-- lookalike_brands lists who buys that category elsewhere: a starting point
-- for prospecting research, not a claim that the club lacks a partner in the
-- category (it may sell one other inventory this dataset doesn't track).

CREATE TABLE mart_category_whitespace AS
WITH category_reach AS (     -- one row per category
    SELECT category_id, category_name,
           COUNT(DISTINCT club_id)  AS clubs_buying
    FROM mart_club_category_map
    GROUP BY category_id, category_name
),
lookalikes AS (              -- one row per category x brand, with its clubs
    SELECT b.category_id, b.brand_name,
           STRING_AGG(DISTINCT c.short_name, ', ' ORDER BY c.short_name) AS at_clubs,
           COUNT(DISTINCT ph.club_id)                                    AS n_clubs
    FROM partnership_history AS ph
    JOIN dim_brand AS b USING (brand_id)
    JOIN dim_club  AS c USING (club_id)
    WHERE ph.is_current
    GROUP BY b.category_id, b.brand_name
)
SELECT
    c.club_id,
    r.category_id,
    r.category_name,
    r.clubs_buying,
    (SELECT STRING_AGG(l.brand_name || ' (' || l.at_clubs || ')', '; '
                       ORDER BY l.n_clubs DESC, l.brand_name)
     FROM lookalikes AS l WHERE l.category_id = r.category_id)  AS lookalike_brands
FROM dim_club AS c
CROSS JOIN category_reach AS r
WHERE r.clubs_buying >= 3
  AND NOT EXISTS (
      SELECT 1 FROM mart_club_category_map AS m
      WHERE m.club_id = c.club_id AND m.category_id = r.category_id
  );
