import oracledb
import os
import time
import sys

# Database configuration
DB_USER = os.getenv("DB_USER", "system")
DB_PASS = os.getenv("DB_PASS", "oracle")
DB_DSN = "localhost:1521/freepdb1"

def get_stats():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                (SELECT count(*) FROM PRODUCTS) as p_count,
                (SELECT count(*) FROM CUSTOMER_REVIEWS) as r_count,
                (SELECT count(*) FROM CUSTOMER_REVIEWS WHERE review_vector IS NOT NULL) as v_count
            FROM dual
        """)
        return cursor.fetchone()
    except:
        return (0, 0, 0)

def dashboard():
    print("\n" + "="*40)
    print(" 🚀 ENTERPRISE AI PIPELINE MONITOR ")
    print("="*40)
    while True:
        p, r, v = get_stats()
        sys.stdout.write(f"\r📦 Sản phẩm: {p:,} | 💬 Đánh giá: {r:,} | 🧠 Đã AI hóa: {v:,}  ")
        sys.stdout.flush()
        time.sleep(2)

if __name__ == "__main__":
    dashboard()
