-- 03_vector_setup.sql
-- High-Performance Semantic Search Indexing for 145M Records
-- Optimized for Oracle 23ai native Vector Store

SET SERVEROUTPUT ON;

PROMPT '📦 Initializing Vector Indexing (HNSW Mode)...';

-- Enable HNSW (Hierarchical Navigable Small World) Indexing
-- This provides sub-second search throughput on massive datasets
BEGIN
    -- Drop existing index if it exists
    EXECUTE IMMEDIATE 'DROP INDEX idx_review_vector_hnsw';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -955 OR SQLCODE = -1418 THEN NULL; 
        ELSE RAISE;
        END IF;
END;
/

-- Create the HNSW index
-- Accuracy is balanced with search speed for enterprise RAG
CREATE VECTOR INDEX idx_review_vector_hnsw 
ON CUSTOMER_REVIEWS (review_vector)
ORGANIZATION INMEMORY NEIGHBOR GRAPH
DISTANCE COSINE
WITH TARGET ACCURACY 90
TABLESPACE USERS;

PROMPT '✅ HNSW Vector Index Created Successfully.';
