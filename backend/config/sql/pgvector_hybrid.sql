WITH vector_scores AS (
    SELECT id, content, metadata,
           1 - (embedding <=> :embedding) as vector_score
    FROM {table_name}
    ORDER BY embedding <=> :embedding
    LIMIT :k * 2
),
keyword_scores AS (
    SELECT id,
           ts_rank(to_tsvector('english', content), plainto_tsquery('english', :query)) as keyword_score
    FROM {table_name}
    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query)
)
SELECT v.content, v.metadata,
       (:alpha * v.vector_score + (1 - :alpha) * COALESCE(k.keyword_score, 0)) as combined_score
FROM vector_scores v
LEFT JOIN keyword_scores k ON v.id = k.id
ORDER BY combined_score DESC
LIMIT :k