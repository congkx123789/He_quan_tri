import oracledb
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USER = os.getenv('DB_USER', 'DEMO_USER')
PASSWORD = os.getenv('DB_PASS', 'DemoPass123!')
DSN = f"localhost:{os.getenv('ORACLE_PORT', '1521')}/FREEPDB1"

def get_connection():
    try:
        conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def ingest_products(conn):
    print("📦 Ingesting Products...")
    df = pd.read_csv('data/products.csv')
    cursor = conn.cursor()
    data = [tuple(x) for x in df.values]
    cursor.executemany("INSERT INTO PRODUCTS (product_id, name, category, price, old_price, stock_quantity) VALUES (:1, :2, :3, :4, :5, :6)", data)
    conn.commit()
    print(f"✅ Ingested {len(df)} products.")

def ingest_specs(conn):
    print("📜 Ingesting JSON Specs...")
    df = pd.read_csv('data/specs.csv')
    cursor = conn.cursor()
    data = [tuple(x) for x in df.values]
    cursor.executemany("INSERT INTO PRODUCT_SPECS (product_id, specs_json) VALUES (:1, :2)", data)
    conn.commit()
    print(f"✅ Ingested {len(df)} specs.")

def ingest_reviews(conn):
    print("💬 Ingesting Reviews...")
    df = pd.read_csv('data/reviews.csv')
    cursor = conn.cursor()
    # Note: Vector embedding generation would happen here via Ollama API
    # For now, we ingest the text.
    data = [(r['product_id'], r['customer_name'], r['review_text'], r['rating']) for _, r in df.iterrows()]
    cursor.executemany("INSERT INTO CUSTOMER_REVIEWS (product_id, customer_name, review_text, review_rating) VALUES (:1, :2, :3, :4)", data)
    conn.commit()
    print(f"✅ Ingested {len(df)} reviews.")

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        ingest_products(conn)
        ingest_specs(conn)
        ingest_reviews(conn)
        conn.close()
        print("🎉 Ingestion complete!")
