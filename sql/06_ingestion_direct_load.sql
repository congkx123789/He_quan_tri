-- 06_ingestion_direct_load.sql
-- High-Performance Enterprise Ingestion into Oracle 23ai
-- Uses Direct Path Loading (/*+ APPEND */) for 80GB+ scalability

SET SERVEROUTPUT ON;

-- 1. Load Products and Specs (Relational & JSON)
-- We combine category-specific external tables into the main PRODUCTS table
PRINT '📦 Loading Products and Specs into Oracle...';

INSERT /*+ APPEND */ INTO PRODUCTS (name, category, price)
SELECT name, category, price FROM EXT_PRODUCTS_ELECTRONICS
UNION ALL
SELECT name, category, price FROM EXT_PRODUCTS_HOME
UNION ALL
SELECT name, category, price FROM EXT_PRODUCTS_TOOLS;

-- Map ASIN to the generated Product IDs for the Specs table
INSERT /*+ APPEND */ INTO PRODUCT_SPECS (product_id, specs_json)
SELECT p.product_id, e.specs_json
FROM PRODUCTS p
JOIN (
    SELECT asin, name, specs_json FROM EXT_PRODUCTS_ELECTRONICS
    UNION ALL
    SELECT asin, name, specs_json FROM EXT_PRODUCTS_HOME
    UNION ALL
    SELECT asin, name, specs_json FROM EXT_PRODUCTS_TOOLS
) e ON p.name = e.name;

-- 2. Load Reviews (Unstructured)
-- Massive direct load from the combined external reviews table
PRINT '💬 Loading Customer Reviews (Textual)...';

INSERT /*+ APPEND */ INTO CUSTOMER_REVIEWS (customer_name, review_text, review_rating)
SELECT customer_name, review_text, rating FROM EXT_REVIEWS_COMBINED;

COMMIT;

PRINT '🎉 Enterprise Ingestion Complete for 80GB Dataset.';
