import oracledb
import os
import torch
from sentence_transformers import SentenceTransformer

# Connection configuration
DB_USER = "select_ai"
DB_PASS = "oracle123"
DB_DSN  = "localhost:1521/freepdb1"
MODEL_NAME = "BAAI/bge-m3"

def search():
    print(f"🔎 --- NÂNG CẤP: TÌM KIẾM SẢN PHẨM ---")
    query = "excellent build quality and very durable tools"
    print(f"❓ Câu hỏi: '{query}'")
    
    # Vector hóa câu hỏi (BF16)
    model = SentenceTransformer(MODEL_NAME, device="cuda", model_kwargs={"torch_dtype": torch.bfloat16})
    query_vector = model.encode(query).tolist()
    
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cursor = conn.cursor()
    
    # Kết nối (JOIN) bảng Reviews và Products để lấy Tên sản phẩm
    cursor.execute("""
        SELECT p.TITLE, r.REVIEW_TEXT, r.REVIEW_RATING
        FROM   CUSTOMER_REVIEWS r
        JOIN   PRODUCTS p ON r.PRODUCT_ID = p.PRODUCT_ID
        WHERE  r.VECTOR_CONTENT IS NOT NULL
        ORDER BY VECTOR_DISTANCE(r.VECTOR_CONTENT, TO_VECTOR(:1), COSINE)
        FETCH FIRST 5 ROWS ONLY
    """, [str(query_vector)])
    
    results = cursor.fetchall()
    print(f"\n✅ Top 5 Sản phẩm khớp nhất tìm thấy:\n" + "="*70)
    for i, res in enumerate(results):
        title = str(res[0])
        review = str(res[1])[:150] + "..." if len(str(res[1])) > 150 else str(res[1])
        print(f"{i+1}. 📦 SẢN PHẨM: {title}")
        print(f"   💬 NHẬN XÉT: {review}")
        print(f"   ⭐ ĐÁNH GIÁ: {res[2]}/5\n")
    
    conn.close()

if __name__ == "__main__":
    search()
