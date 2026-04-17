import oracledb
import os
import torch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Cấu hình DB (Sử dụng đúng tài khoản người dùng, không dùng SYS)
user = "select_ai"
password = "oracle123"
dsn = "localhost:1521/FREEPDB1"

# Load Model BGE-M3 (Matching your orchestrator)
model_name = "BAAI/bge-m3"
print(f"🧠 Loading {model_name} from local cache...")

# Using the same optimization as your orchestrator
try:
    model = SentenceTransformer(
        model_name, 
        device="cuda",
        model_kwargs={"torch_dtype": torch.bfloat16}
    )
    print("✅ BGE-M3 Ready (BF16).")
except Exception as e:
    print(f"⚠️ Fallback to FP16: {e}")
    model = SentenceTransformer(model_name, device="cuda")

def perform_search(query_str):
    print(f"\n🔎 Querying: '{query_str}'")
    import json
    # 1. Generate Embedding
    embedding_list = model.encode(query_str, normalize_embeddings=True).tolist()
    # 2. Convert to JSON string for Oracle
    vector_json = json.dumps(embedding_list)
    
    conn = oracledb.connect(user=user, password=password, dsn=dsn)
    cursor = conn.cursor()
    
    # SQL Order by Vector Distance (Using JSON string to avoid ORA-01484)
    sql = """
    SELECT REVIEW_TEXT, RATING
    FROM CUSTOMER_REVIEWS
    ORDER BY VECTOR_DISTANCE(VECTOR_CONTENT, VECTOR(:v), COSINE)
    FETCH FIRST 5 ROWS ONLY
    """
    
    cursor.execute(sql, v=vector_json)
    rows = cursor.fetchall()
    
    if not rows:
        print("❌ No matches found!")
    else:
        for i, row in enumerate(rows, 1):
            text = str(row[0]).replace('\n', ' ')
            print(f"{i}. [Rating {row[1]}] {text[:150]}...")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_queries = [
        "best sound quality headphones for work",
        "durable kitchen equipment for home cooking",
        "poor quality product and bad customer service"
    ]
    for q in test_queries:
        perform_search(q)
        print("-" * 60)
