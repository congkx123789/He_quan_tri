import oracledb
import csv
import os
import sys
import time
import json
from multiprocessing import Process

csv.field_size_limit(10 * 1024 * 1024)

DB_USER = os.getenv("DB_USER", "select_ai")
DB_PASS = os.getenv("DB_PASS", "oracle123")
DB_DSN = "localhost:1521/freepdb1"
CHECKPOINT_DIR = "checkpoints"
BATCH_SIZE = 5000

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def save_checkpoint(category, type, count):
    cp_file = os.path.join(CHECKPOINT_DIR, f"{category}_{type}.json")
    with open(cp_file, 'w') as f:
        json.dump({'count': count}, f)

def get_checkpoint(category, type):
    cp_file = os.path.join(CHECKPOINT_DIR, f"{category}_{type}.json")
    if os.path.exists(cp_file):
        with open(cp_file, 'r') as f:
            return json.load(f).get('count', 0)
    return 0

def load_products_worker(category):
    conn = get_connection()
    cursor = conn.cursor()
    file_path = f'data/ingest/processed_metadata_{category}.csv'
    if not os.path.exists(file_path):
        conn.close()
        return

    processed_count = get_checkpoint(category, 'prod')
    print(f"🚀 [Prod-{category}] Resuming from {processed_count:,}...", flush=True)

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for _ in range(processed_count):
            next(reader, None)

        batch = []
        count = processed_count
        for row in reader:
            if count >= 500000:
                print(f"🛑 [Prod-{category}] Reached 500K limit. Stopping.", flush=True)
                break
            # Mapping CSV 'name' to SQL 'title' and handling missing image_url
            batch.append((row['asin'], row['name'], row.get('main_image_url', '')))
            count += 1
            if len(batch) >= BATCH_SIZE:
                try:
                    cursor.executemany("INSERT INTO PRODUCTS (asin, title, image_url) VALUES (:1, :2, :3)", batch)
                    conn.commit()
                    save_checkpoint(category, 'prod', count)
                except Exception as e:
                    print(f"❌ [Prod-{category}] INSERT ERROR: {e}", flush=True)
                    conn.rollback() 
                batch = []
                if count % 50000 == 0:
                    print(f"📦 [Prod-{category}] Progress: {count:,} items", flush=True)
        if batch:
            try:
                cursor.executemany("INSERT INTO PRODUCTS (asin, title, image_url) VALUES (:1, :2, :3)", batch)
                conn.commit()
                save_checkpoint(category, 'prod', count)
            except Exception as e:
                print(f"❌ [Prod-{category}] FINAL INSERT ERROR: {e}", flush=True)
    conn.close()

def load_reviews_worker(category):
    conn = get_connection()
    cursor = conn.cursor()
    file_path = f"data/ingest/processed_reviews_{category}.csv"
    if not os.path.exists(file_path):
        conn.close()
        return

    processed_count = get_checkpoint(category, 'rev')
    print(f"🔥 [Review-{category}] Resuming from {processed_count:,} (Direct Mode)...", flush=True)
    
    start_time = time.time()
    total_written = processed_count
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for _ in range(processed_count):
            next(reader, None)

        batch = []
        for row in reader:
            if total_written >= 500000:
                print(f"🛑 [Review-{category}] Reached 500K limit. Stopping.", flush=True)
                break
            
            try:
                asin = row.get("asin")
                cursor.execute("SELECT product_id FROM PRODUCTS WHERE asin = :1", [asin])
                res = cursor.fetchone()
                if not res: continue

                pid = res[0]
                batch.append((row.get("review_text"), row.get("rating"), pid))
                if len(batch) >= 1000:
                    cursor.executemany("INSERT INTO CUSTOMER_REVIEWS (REVIEW_TEXT, REVIEW_RATING, PRODUCT_ID) VALUES (:1, :2, :3)", batch)
                    conn.commit()
                    total_written += len(batch)
                    save_checkpoint(category, 'rev', total_written)
                    batch = []
                    if total_written % 10000 == 0:
                        rate = (total_written - processed_count) / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
                        print(f"⚡ [Review-{category}] Flowing: {total_written:,} (Rate: {rate:.0f}/s)", flush=True)
            except Exception as e:
                print(f"❌ [Review-{category}] ROW ERROR: {e}", flush=True)
                continue
            
    if batch:
        try:
            cursor.executemany("INSERT INTO CUSTOMER_REVIEWS (REVIEW_TEXT, REVIEW_RATING, PRODUCT_ID) VALUES (:1, :2, :3)", batch)
            conn.commit()
            save_checkpoint(category, 'rev', total_written)
        except Exception as e:
            print(f"❌ [Review-{category}] FINAL BATCH ERROR: {e}", flush=True)
    conn.close()

if __name__ == "__main__":
    categories = ["electronics", "home_and_kitchen", "tools"]
    print("\n💎 UNIFIED RESILIENT ENGINE v46 ACTIVATED", flush=True)
    
    # PHASE 1: Products
    print("🛰️ Phase 1: Ingesting Products...", flush=True)
    prod_procs = []
    for cat in categories:
        p = Process(target=load_products_worker, args=(cat,))
        p.start()
        prod_procs.append(p)
    for p in prod_procs:
        p.join()
        
    # PHASE 2: Reviews
    print("🛰️ Phase 2: Ingesting Reviews...", flush=True)
    rev_procs = []
    for cat in categories:
        p = Process(target=load_reviews_worker, args=(cat,))
        p.start()
        rev_procs.append(p)
    for p in rev_procs:
        p.join()
    
    print("✅ Full 1.5M Sample Ingestion Move Complete.", flush=True)
