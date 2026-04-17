import os
import sys
import argparse
from huggingface_hub import HfApi, create_repo, hf_hub_download
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('HF_TOKEN')
DUMP_FILE = "sql/dumps/enterprise_snapshot.dmp"
REPO_NAME = "oracle-ai-vector-snapshot"

def sync_to_hf(repo_id, private=True):
    api = HfApi(token=TOKEN)
    user = api.whoami().get('name')
    full_repo_id = f"{user}/{repo_id}"
    
    print(f"🚀 Preparing to push snapshot to Hugging Face: {full_repo_id}")
    
    try:
        create_repo(repo_id=full_repo_id, token=TOKEN, private=private, repo_type="dataset", exist_ok=True)
    except Exception as e:
        print(f"⚠️ Repo exists or creation failed: {e}")

    if not os.path.exists(DUMP_FILE):
        print(f"❌ Error: Snapshot file {DUMP_FILE} not found. Run scripts/snapshot_db.sh first.")
        return

    print(f"📤 Uploading 12GB Snapshot (using LFS)...")
    api.upload_file(
        path_or_fileobj=DUMP_FILE,
        path_in_repo="enterprise_snapshot.dmp",
        repo_id=full_repo_id,
        repo_type="dataset",
        run_as_future=False
    )
    print(f"✅ Upload complete: https://huggingface.co/datasets/{full_repo_id}")

def pull_from_hf(repo_id):
    print(f"📥 Downloading latest snapshot from: {repo_id}")
    os.makedirs(os.path.dirname(DUMP_FILE), exist_ok=True)
    
    hf_hub_download(
        repo_id=repo_id,
        filename="enterprise_snapshot.dmp",
        repo_type="dataset",
        local_dir="sql/dumps",
        token=TOKEN
    )
    print(f"✅ Download complete: {DUMP_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Oracle AI Snapshot with Hugging Face")
    parser.add_argument("action", choices=["push", "pull"])
    parser.add_argument("--repo", default=REPO_NAME, help="Hugging Face repo name")
    parser.add_argument("--public", action="store_false", dest="private", help="Make repo public")
    
    args = parser.parse_args()
    
    if not TOKEN:
        print("❌ Error: HF_TOKEN not found in .env. Please provide a token with 'Write' access.")
        sys.exit(1)
        
    if args.action == "push":
        sync_to_hf(args.repo, private=args.private)
    elif args.action == "pull":
        # For pull, we might need the full user/repo string
        repo = args.repo if "/" in args.repo else f"auto" # handle auto-discovery logic if needed
        pull_from_hf(args.repo)
