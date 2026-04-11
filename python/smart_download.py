import os
import requests
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv

# Enable high-speed hf_transfer
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

# Load environment variables
load_dotenv()

TOKEN = os.getenv('HF_TOKEN')
REPO_ID = "McAuley-Lab/Amazon-Reviews-2023"

# Enterprise Acquisition Config (Scale to 40-60GB total)
METADATA_SHARDS = [
    # Electronics (Full 10 Shards)
    *[f"raw_meta_Electronics/full-{str(i).zfill(5)}-of-00010.parquet" for i in range(10)],
    # Toys & Games (5 Shards)
    *[f"raw_meta_Toys_and_Games/full-{str(i).zfill(5)}-of-00005.parquet" for i in range(5)],
]

REVIEW_FILE = "raw/review_categories/Electronics.jsonl"
REVIEW_LIMIT = 1000000 # 1 Million reviews (~10-20GB depending on length)

def download_shards():
    print(f"🚀 [1/2] Initiating Enterprise Metadata Acquisition (15 Shards)...")
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    for shard in METADATA_SHARDS:
        print(f"📥 Acquiring shard: {shard}...")
        try:
            hf_hub_download(
                repo_id=REPO_ID,
                filename=shard,
                repo_type="dataset",
                token=TOKEN,
                local_dir=data_dir,
                local_dir_use_symlinks=False
            )
        except Exception as e:
            print(f"⚠️ Failed shard {shard}: {e}")

def stream_review_enterprise():
    print(f"🚀 [2/2] Streaming Enterprise Review Segment ({REVIEW_LIMIT} rows)...")
    data_dir = os.path.join(os.getcwd(), 'data')
    target_file = os.path.join(data_dir, "reviews_enterprise.jsonl")
    
    url = f"https://huggingface.co/datasets/{REPO_ID}/resolve/main/{REVIEW_FILE}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        count = 0
        with open(target_file, 'wb') as f:
            for line in response.iter_lines():
                if count >= REVIEW_LIMIT:
                    break
                f.write(line + b"\n")
                count += 1
                if count % 50000 == 0:
                    print(f"📈 [Review Stream] Captured {count} records...")
        
        print(f"✅ Enterprise Review segment saved to: {target_file}")
    except Exception as e:
        print(f"❌ Failed to stream enterprise reviews: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("⚠️ HF_TOKEN not found in .env.")
    else:
        # Check if already partially downloaded to avoid redownloading shard 0
        download_shards()
        stream_review_enterprise()
