-- Rule: a whitespace row never names a category the club already holds.
SELECT w.club_id, w.category_id
FROM mart_category_whitespace AS w
JOIN mart_club_category_map AS m USING (club_id, category_id);
