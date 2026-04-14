-- 04_external_tables.sql
-- High-Performance External Table Definitions for 83GB Amazon Dataset
-- Final Robust Version: Handling massive multi-line JSON blocks and all categories

SET SERVEROUTPUT ON;

PROMPT '🔍 Re-Configuring Ultra-Robust External Tables for ALL categories...';

CREATE OR REPLACE DIRECTORY DATA_IN_DIR AS '/opt/oracle/data_in/ingest';

BEGIN
    FOR t IN (SELECT table_name FROM user_tables WHERE table_name LIKE 'EXT_%') LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name;
    END LOOP;
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- 1. Metadata Table (Shared for all categories via multiple locations)
CREATE TABLE EXT_PRODUCTS_META (
    asin VARCHAR2(50),
    name VARCHAR2(4000),
    category VARCHAR2(1000),
    brand VARCHAR2(255),
    price VARCHAR2(50),
    specs_json CLOB
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY DATA_IN_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY NEWLINE
        SKIP 1
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            asin CHAR(50),
            name CHAR(4000),
            category CHAR(1000),
            brand CHAR(255),
            price CHAR(50),
            specs_json CHAR(20000000) -- Critical Fix: Allow 20MB strings
        )
    )
    LOCATION (
        'processed_metadata_electronics.csv',
        'processed_metadata_home_and_kitchen.csv',
        'processed_metadata_tools.csv'
    )
) REJECT LIMIT UNLIMITED;

-- 2. Reviews Table (Shared for all categories)
CREATE TABLE EXT_REVIEWS (
    asin VARCHAR2(50),
    customer_name VARCHAR2(255),
    review_rating CHAR(5),
    review_text CLOB,
    created_at VARCHAR2(50)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY DATA_IN_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY NEWLINE
        SKIP 1
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            asin CHAR(50),
            customer_name CHAR(255),
            review_rating CHAR(5),
            review_text CHAR(20000000), -- Critical Fix: Allow 20MB strings
            created_at CHAR(50)
        )
    )
    LOCATION (
        'processed_reviews_electronics.csv',
        'processed_reviews_home_and_kitchen.csv',
        'processed_reviews_tools.csv'
    )
) REJECT LIMIT UNLIMITED;

PROMPT '✅ External Tables are now ROBUST (All categories & 20MB capacity).';
