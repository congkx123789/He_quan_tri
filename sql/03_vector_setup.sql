-- 03_vector_setup.sql
-- Oracle AI Vector Search Configuration

-- 1. Create a Vector Index (In-Memory or Disk-based)
-- For high performance on 50GB data, HNSW is recommended.
CREATE VECTOR INDEX idx_customer_reviews_vec 
ON CUSTOMER_REVIEWS(review_vector) 
ORGANIZATION INMEMORY NEIGHBOR GRAPH
DISTANCE METRIC COSINE;

-- 2. Procedure to generate embeddings via Ollama (Local)
-- This logic usually sits in Python or a PL/SQL wrapper calling DBMS_VECTOR_CHAIN
-- Example semantic search query:
/*
SELECT r.customer_name, r.review_text
FROM CUSTOMER_REVIEWS r
WHERE product_id = :pid
ORDER BY VECTOR_DISTANCE(r.review_vector, :query_vector, COSINE)
FETCH FIRST 5 ROWS ONLY;
*/
