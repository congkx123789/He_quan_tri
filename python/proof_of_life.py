import oracledb
import csv
import os
import sys

# Database configuration
DB_USER = os.getenv("DB_USER", "system")
DB_PASS = os.getenv("DB_PASS", "oracle")
DB_DSN = "localhost:1521/freepdb1"

BATCH_SIZE = 1000 # Small batch for absolute visibility
TARGET_ROWS = 5000 # Just enough to PROVE life

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def run_proof_of_life():
    print("🚀 Proof of Life Starting...")
    conn = get_connection()
    cursor = conn.cursor()
    
    file_path = 'data/ingest/processed_metadata_electronics.csv'
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        return

    print(f"📦 Loading {TARGET_ROWS} rows from {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = []
        count = 0
        
        for row in reader:
            # name, category, price
            batch.append((row['name'][:4000], row['category'][:1000], float(row['price'] or 0)))
            count += 1
            
            if len(batch) >= BATCH_SIZE:
                cursor.executemany("INSERT INTO PRODUCTS (name, category, price) VALUES (:1, :2, :3)", batch)
                conn.commit()
                print(f"✅ Committed {count} rows...")
                batch = []
            
            if count >= TARGET_ROWS:
                break
        
        if batch:
            cursor.executemany("INSERT INTO PRODUCTS (name, category, price) VALUES (:1, :2, :3)", batch)
            conn.commit()

    print("\n🧐 Verification Query...")
    cursor.execute("SELECT product_id, category, substr(name, 1, 50) FROM PRODUCTS WHERE ROWNUM <= 5")
    for row in cursor.fetchall():
        print(f"FOUND: ID={row[0]} | CAT={row[1]} | NAME={row[2]}...")
    
    print("\n✨ PROOF OF LIFE COMPLETE. DATABASE IS ACTIVE.")
    conn.close()

if __name__ == "__main__":
    run_proof_of_life()
