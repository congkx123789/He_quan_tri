import oracledb
import os
import requests
import json
import sys

# Database configuration
DB_USER = os.getenv("DB_USER", "system")
DB_PASS = os.getenv("DB_PASS", "oracle")
DB_DSN = "localhost:1521/freepdb1"

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "bge-m3:latest"

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def get_query_embedding(text):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": text},
            timeout=10
        )
        response.raise_for_status()
        # Convert to string for TO_VECTOR compatibility
        return str(response.json()["embedding"])
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return None

def semantic_search(query_text, top_k=5):
    print(f"🔍 Searching for: \"{query_text}\"...")
    
    query_vector_str = get_query_embedding(query_text)
    if not query_vector_str:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # Use VECTOR_DISTANCE with TO_VECTOR for ORA-01484 compatibility
    sql = """
        SELECT review_text, review_rating, 
               VECTOR_DISTANCE(review_vector, TO_VECTOR(:1), COSINE) as distance
        FROM CUSTOMER_REVIEWS
        WHERE review_vector IS NOT NULL
        ORDER BY distance
        FETCH FIRST :2 ROWS ONLY
    """
    
    cursor.execute(sql, [query_vector_str, top_k])
    
    print(f"\n✨ Top {top_k} Most Relevant Reviews:\n" + "="*50)
    for i, (text, rating, dist) in enumerate(cursor.fetchall(), 1):
        print(f"[{i}] Score: {1-dist:.4f} | Rating: {rating}⭐")
        print(f"Text: {str(text)[:200]}...")
        print("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python semantic_search.py 'your query'")
    else:
        query = " ".join(sys.argv[1:])
        semantic_search(query)
