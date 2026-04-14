-- 06_ingestion_direct_load.sql
-- Ultra-Fast Native Ingestion for 80GB Dataset
-- Optimized for 32GB RAM & Parallel Processing

SET SERVEROUTPUT ON;
SET FEEDBACK ON;
SET TIMING ON;

PROMPT '🚀 Starting Native SQL Ingestion (Turbo Mode)...';

-- 1. Load Products Metadata
-- Using APPEND hint for high-speed direct path loading
PROMPT '📦 Ingesting Products (Full Scale)...';
INSERT /*+ APPEND NOLOGGING PARALLEL(8) */ INTO PRODUCTS (name, category, price, asin)
SELECT name, category, TO_NUMBER(price, '999999.99'), asin
FROM EXT_PRODUCTS_META;
COMMIT;

-- 2. Load Reviews
PROMPT '📦 Ingesting Customer Reviews (First 100k)...';
INSERT /*+ APPEND NOLOGGING */ INTO CUSTOMER_REVIEWS (product_id, customer_name, review_text, review_rating)
SELECT p.product_id, e.customer_name, e.review_text, e.review_rating
FROM EXT_REVIEWS e
JOIN PRODUCTS p ON e.asin = p.asin
WHERE ROWNUM <= 100000;
COMMIT;

PROMPT '✅ Proof of Life Batch Complete.';

-- Show results
SET HEAD ON;
SELECT count(*) AS PRODUCTS_LANDED FROM PRODUCTS;
SELECT count(*) AS REVIEWS_LANDED FROM CUSTOMER_REVIEWS;

SELECT product_id, category, substr(name, 1, 50) as name 
FROM PRODUCTS 
WHERE ROWNUM <= 5;
