import os
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('HF_TOKEN')
REPO_ID = "McAuley-Lab/Amazon-Reviews-2023"

# Essential files identified
FILES_TO_DOWNLOAD = [
    "raw/review_categories/Electronics.jsonl",
    "raw/meta_categories/meta_Electronics.jsonl"
]

def download_amazon_data():
    print(f"🚀 Starting Amazon Reviews 2023 Download...")
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    for file_path in FILES_TO_DOWNLOAD:
        print(f"📥 Downloading {file_path} from {REPO_ID}...")
        try:
            local_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=file_path,
                repo_type="dataset",
                token=TOKEN,
                local_dir=data_dir,
                local_dir_use_symlinks=False
            )
            print(f"✅ Saved to: {local_path}")
        except Exception as e:
            print(f"❌ Failed to download {file_path}: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("⚠️ HF_TOKEN not found in .env. Please check your configuration.")
    else:
        download_amazon_data()
