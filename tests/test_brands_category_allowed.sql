-- Every brand needs a category from the allowed list in data/categories.csv.
SELECT b.brand_id, b.category_id
FROM dim_brand AS b
LEFT JOIN dim_category AS c USING (category_id)
WHERE c.category_id IS NULL;
