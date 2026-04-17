import oracledb
import os
import time
import sys
import torch
from sentence_transformers import SentenceTransformer

# Docker/Environment configuration
DB_USER = os.getenv("DB_USER", "select_ai")
DB_PASS = os.getenv("DB_PASS", "oracle123")
DB_DSN  = os.getenv("DB_DSN", "localhost:1521/freepdb1")
MODEL_NAME = "BAAI/bge-m3"

# Memory Optimization for Blackwell 16GB
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def check_db_space(conn):
    """Monitor user data size to prevent ORA-12954"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(bytes)/1024/1024 FROM user_segments")
        res = cursor.fetchone()[0]
        return res if res else 0
    except:
        return 0 # Fallback if query fails

def process_vectors():
    print(f"🧠 AI Orchestrator v45 (Consistent Rhythm Mode)")
    print(f"📡 Connecting to {DB_DSN} as {DB_USER}")
    
    if not torch.cuda.is_available(): sys.exit(1)
        
    print(f"🎮 GPU Detected: {torch.cuda.get_device_name(0)}")
    
    try:
        model = SentenceTransformer(
            MODEL_NAME, 
            device="cuda",
            model_kwargs={
                "torch_dtype": torch.bfloat16,
                "attn_implementation": "flash_attention_2"
            }
        )
        print("✅ Model Ready with BF16 + FA2.")
    except Exception as e:
        print(f"⚠️ Optimization Fallback: {e}")
        model = SentenceTransformer(MODEL_NAME, device="cuda", model_kwargs={"torch_dtype": torch.float16})

    total_done = 0
    # DEEP UNIFORMITY PARAMETERS (Blackwell Optimized - Safe Mode)
    BUFFER_SIZE = 25000         # Large buffer for maximum uniformity
    INTERNAL_BATCH_SIZE = 64    # Reduced batch for safer VRAM usage
    SAFETY_LIMIT_MB = 11000     # Leave 1GB spare (Limit is 12GB)

    while True:
        try:
            conn   = get_connection()
            
            # Check Safety Limit
            current_size = check_db_space(conn)
            if current_size > SAFETY_LIMIT_MB:
                print(f"🚨 SAFETY STOP: Database size ({current_size:.1f}MB) reached limit!")
                conn.close()
                break

            cursor = conn.cursor()

            # Step 1: Fetch Large Buffer (Using Uppercase for Oracle standard)
            print(f"🎬 Filling Sort Buffer ({BUFFER_SIZE} items)...", flush=True)
            cursor.execute("""
                SELECT REVIEW_ID, REVIEW_TEXT
                FROM   CUSTOMER_REVIEWS
                WHERE  VECTOR_CONTENT IS NULL
                AND    dbms_lob.getlength(REVIEW_TEXT) > 10
                AND    ROWNUM <= :1
            """, [BUFFER_SIZE])
            
            rows = cursor.fetchall()
            if not rows:
                print("💤 No more data. Waiting (10s)...", flush=True)
                conn.close()
                time.sleep(10)
                continue

            # Step 2: Local Sort by Length
            sorted_rows = sorted(rows, key=lambda x: len(str(x[1])))
            
            print(f"🎼 Buffer Full. Processing in uniform batches...", flush=True)
            
            # Step 3: Process the sorted buffer
            for i in range(0, len(sorted_rows), INTERNAL_BATCH_SIZE):
                chunk = sorted_rows[i : i + INTERNAL_BATCH_SIZE]
                rids  = [r[0] for r in chunk]
                texts = [str(r[1]) for r in chunk]
                
                start_batch = time.time()
                embeddings = model.encode(texts, batch_size=INTERNAL_BATCH_SIZE, convert_to_numpy=True)
                duration = time.time() - start_batch
                
                update_data = []
                for rid, emb in zip(rids, embeddings):
                    update_data.append([str(emb.tolist()), rid])

                # Use explicit Uppercase for columns to avoid any ORA-00904
                cursor.executemany(
                    "UPDATE CUSTOMER_REVIEWS SET VECTOR_CONTENT = TO_VECTOR(:1) WHERE REVIEW_ID = :2",
                    update_data
                )
                conn.commit()
                
                total_done += len(chunk)
                rate = len(chunk) / duration if duration > 0 else 0
                print(f"⚡ Rhythm: {total_done:,} docs | rate: {rate:.1f} rev/sec | sz: {len(texts[0])}-{len(texts[-1])}")

            conn.close()

        except Exception as e:
            print(f"❌ Error: {e}")
            torch.cuda.empty_cache()
            time.sleep(5)

if __name__ == "__main__":
    process_vectors()
