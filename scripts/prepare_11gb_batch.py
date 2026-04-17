import pandas as pd
import oracledb
import os
import uuid
import numpy as np

# Database configuration
DB_USER = os.getenv("DB_USER", "select_ai")
DB_PASS = os.getenv("DB_PASS", "oracle123")
DB_DSN  = os.getenv("DB_DSN", "localhost:1521/freepdb1")

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def load_balanced_data():
    categories = ['electronics', 'home_and_kitchen', 'tools']
    target_rows_per_cat = 500000 
    
    conn = get_connection()
    
    print("🚀 Starting Balanced Data Ingestion (1.5M Records Target)...")
    
    for cat in categories:
        prod_file = f"data/ingest/processed_metadata_{cat}.csv"
        rev_file  = f"data/ingest/processed_reviews_{cat}.csv"
        
        if os.path.exists(prod_file) and os.path.exists(rev_file):
            print(f"📦 Loading {cat}...")
            
            # 1. Load Products
            df_prod = pd.read_csv(prod_file, nrows=target_rows_per_cat)
            
            # AGGRESSIVE CLEANING (Safe for 1000-byte limit)
            df_prod = df_prod.fillna('None')
            df_prod = df_prod.astype(str)
            
            df_prod['asin'] = df_prod['asin'].str.slice(0, 50)
            df_prod['name'] = df_prod['name'].str.slice(0, 800) # 800 chars safety for 1000 bytes
            df_prod['category'] = df_prod['category'].str.slice(0, 100)
            df_prod['price_val'] = pd.to_numeric(df_prod['price'], errors='coerce').fillna(0.0)
            
            prod_data = df_prod[['asin', 'name', 'category', 'price_val', 'specs_json']].values.tolist()
            
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT /*+ APPEND */ INTO SELECT_AI.PRODUCTS (product_id, name, category, price, specs_json)
                VALUES (:1, :2, :3, :4, :5)
            """, prod_data)
            conn.commit()
            print(f"   ✅ {len(prod_data)} Products loaded.")
            
            # 2. Load Reviews
            df_rev = pd.read_csv(rev_file, nrows=target_rows_per_cat)
            
            # AGGRESSIVE CLEANING
            df_rev = df_rev.fillna('None')
            df_rev = df_rev.astype(str)
            
            df_rev['asin'] = df_rev['asin'].str.slice(0, 50)
            df_rev['rating_val'] = pd.to_numeric(df_rev['rating'], errors='coerce').fillna(5.0)
            df_rev['review_id'] = [str(uuid.uuid4()) for _ in range(len(df_rev))]
            
            rev_data = df_rev[['review_id', 'asin', 'rating_val', 'review_text']].values.tolist()
            
            cursor.executemany("""
                INSERT /*+ APPEND */ INTO SELECT_AI.CUSTOMER_REVIEWS (review_id, product_id, rating, review_text)
                VALUES (:1, :2, :3, :4)
            """, rev_data)
            conn.commit()
            print(f"   ✅ {len(rev_data)} Reviews loaded.")
            cursor.close()
            
    conn.close()
    print("✨ Balanced Data Load Complete.")

if __name__ == "__main__":
    load_balanced_data()
