import os
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv

# Enable high-speed transfer if installed
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

# Load environment variables
load_dotenv()

TOKEN = os.getenv('HF_TOKEN')
REPO_ID = "McAuley-Lab/Amazon-Reviews-2023"

# Target Categories for ~80GB Goal
CATEGORIES = [
    {"name": "Electronics", "shards": 10},
    {"name": "Home_and_Kitchen", "review_only": True}, # Home & Kitchen doesn't have parquet shards in this repo
    {"name": "Tools_and_Home_Improvement", "review_only": True}
]

DATA_DIR = os.path.join(os.getcwd(), 'data')

def download_enterprise_80gb(sample_mode=False):
    mode_str = "[SAMPLE MODE]" if sample_mode else "[FULL ENTERPRISE]"
    print(f"🚀 {mode_str} Initiating Data Acquisition...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Download Electronics Shards (Parquet)
    # Full: 10 shards, Sample: 1 shard
    shard_count = 1 if sample_mode else 10
    for i in range(shard_count):
        shard = f"raw_meta_Electronics/full-{str(i).zfill(5)}-of-00010.parquet"
        print(f"📥 Metadata Shard: {shard}")
        hf_hub_download(repo_id=REPO_ID, filename=shard, repo_type="dataset", token=TOKEN, local_dir=DATA_DIR)

    # 2. Download Full Reviews (JSONL)
    # Full: All categories, Sample: Just one category (Electronics)
    targets = [
        "raw/review_categories/Electronics.jsonl"
    ] if sample_mode else [
        "raw/meta_categories/meta_Home_and_Kitchen.jsonl",
        "raw/meta_categories/meta_Tools_and_Home_Improvement.jsonl",
        "raw/review_categories/Electronics.jsonl",
        "raw/review_categories/Home_and_Kitchen.jsonl",
        "raw/review_categories/Tools_and_Home_Improvement.jsonl"
    ]
    
    for target in targets:
        print(f"📥 Review File: {target}...")
        try:
            hf_hub_download(
                repo_id=REPO_ID, 
                filename=target, 
                repo_type="dataset", 
                token=TOKEN, 
                local_dir=DATA_DIR,
                local_dir_use_symlinks=False
            )
        except Exception as e:
            print(f"⚠️ Failed to pull {target}: {e}")

if __name__ == "__main__":
    import sys
    is_sample = "--sample" in sys.argv
    if not TOKEN:
        print("⚠️ HF_TOKEN not found in .env.")
    else:
        download_enterprise_80gb(sample_mode=is_sample)
