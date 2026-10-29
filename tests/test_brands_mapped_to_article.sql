-- Every brand is either mapped to a Wikipedia article or says why it isn't.
SELECT brand_id, brand_name
FROM dim_brand
WHERE wikipedia_article IS NULL
  AND no_article_reason IS NULL;
