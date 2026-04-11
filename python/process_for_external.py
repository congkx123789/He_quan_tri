import json
import csv
import os
import pandas as pd
import re
import gc

def scrub_text(text):
    if not text: return ""
    # Strip HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Simplify whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_price(price):
    try:
        if isinstance(price, (int, float)): return float(price)
        # Handle string prices like "$23.99"
        p = re.sub(r'[^\d.]', '', str(price))
        return float(p) if p else 0.0
    except Exception:
        return 0.0

def process_metadata_parquet(input_dir, output_path):
    print(f"🛠️ [Safe-Mode] Engineering Metadata shards from {input_dir} (100% Streaming)...")
    try:
        shards = sorted([os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.parquet')])
        first_shard = True
        for shard in shards:
            print(f"📖 Cleaning shard: {os.path.basename(shard)}...")
            df = pd.read_parquet(shard)
            
            df = df.rename(columns={'parent_asin': 'asin', 'title': 'name', 'main_category': 'category'})
            sql_cols = ['asin', 'name', 'brand', 'category', 'price']
            for col in sql_cols:
                if col not in df.columns: df[col] = ''
            
            # Clean Specs in place
            def bundle_specs(row):
                specs = {k: v for k, v in row.items() if k not in sql_cols}
                return json.dumps(specs, default=str)
            
            df['price'] = df['price'].apply(normalize_price)
            df['name'] = df['name'].apply(scrub_text)
            df['specs_json'] = df.apply(bundle_specs, axis=1)
            
            df[sql_cols + ['specs_json']].to_csv(output_path, mode='a' if not first_shard else 'w', 
                                                index=False, quoting=csv.QUOTE_ALL, 
                                                header=first_shard)
            first_shard = False
            del df
            gc.collect() 
        print(f"✅ Metadata cleaned and exported to {output_path}")
    except Exception as e: print(f"❌ Engineering failed: {e}")

def process_metadata_jsonl(input_path, output_path):
    print(f"🛠️ [Safe-Mode] Engineering Metadata JSONL: {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.writer(fout, quoting=csv.QUOTE_ALL)
        writer.writerow(['asin', 'name', 'brand', 'category', 'price', 'specs_json'])
        for line in fin:
            try:
                data = json.loads(line)
                asin = data.get('parent_asin', '') or data.get('asin', '')
                name = scrub_text(data.get('title', ''))
                brand = data.get('brand', '')
                category = data.get('main_category', '')
                price = normalize_price(data.get('price', 0))
                specs = {k: v for k, v in data.items() if k not in ['title', 'main_category', 'price', 'asin', 'parent_asin']}
                writer.writerow([asin, name, brand, category, price, json.dumps(specs, default=str)])
            except Exception: continue
    print(f"✅ Metadata cleaned to {output_path}")

def process_reviews_enterprise(input_path, output_path):
    print(f"🛠️ [Safe-Mode] Engineering Reviews (Deduplicating & Scrubbing): {input_path}...")
    seen_reviews = set() # Store hashes for dedup (RAM usage check)
    
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.writer(fout, quoting=csv.QUOTE_ALL)
        writer.writerow(['asin', 'customer_name', 'rating', 'review_text'])
        
        count = 0
        written = 0
        for line in fin:
            try:
                data = json.loads(line)
                asin = data.get('parent_asin', '') or data.get('asin', '')
                user = data.get('user_id', 'Anonymous')
                text = scrub_text(data.get('text', ''))
                
                # Deduplication Check
                rev_hash = hash((asin, user, text[:100]))
                if rev_hash in seen_reviews:
                    continue
                
                # Add to set (Control size to avoid RAM issues)
                if len(seen_reviews) < 1000000: # Max 1M hashes
                    seen_reviews.add(rev_hash)
                
                rating = data.get('rating', 0)
                writer.writerow([asin, user, rating, text])
                written += 1
                count += 1
                if count % 100000 == 0: 
                    print(f"📈 Analyzed {count} reviews... (Kept {written})")
                    gc.collect()
            except Exception: continue
    print(f"✅ Engineering complete. Reviews cleaned to {output_path}")

if __name__ == "__main__":
    data_dir = os.path.join(os.getcwd(), 'data')
    ingest_dir = os.path.join(data_dir, 'ingest')
    os.makedirs(ingest_dir, exist_ok=True)
    
    categories = ["electronics", "home_and_kitchen", "tools"]
    for cat in categories:
        cat_dir = os.path.join(data_dir, cat)
        if not os.path.exists(cat_dir): continue
        
        print(f"\n🚀 Launching Enterprise Engine for: {cat}")
        
        meta_parq_dir = os.path.join(cat_dir, 'metadata')
        meta_jsonl = os.path.join(cat_dir, 'metadata.jsonl')
        meta_out = os.path.join(ingest_dir, f'processed_metadata_{cat}.csv')
        
        if os.path.exists(meta_parq_dir) and any(f.endswith('.parquet') for f in os.listdir(meta_parq_dir)):
            process_metadata_parquet(meta_parq_dir, meta_out)
        elif os.path.exists(meta_jsonl):
            process_metadata_jsonl(meta_jsonl, meta_out)
            
        rev_in = os.path.join(cat_dir, 'reviews.jsonl')
        rev_out = os.path.join(ingest_dir, f'processed_reviews_{cat}.csv')
        if os.path.exists(rev_in):
            process_reviews_enterprise(rev_in, rev_out)
