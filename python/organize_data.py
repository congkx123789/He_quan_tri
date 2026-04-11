import os
import shutil

def organize_dataset():
    print("🧹 Starting Enterprise Data Reorganization...")
    data_dir = os.path.join(os.getcwd(), 'data')
    
    # Target Structure Mapping
    categories = {
        "electronics": {
            "meta_dir": "raw_meta_Electronics",
            "rev_file": "raw/review_categories/Electronics.jsonl"
        },
        "home_and_kitchen": {
            "meta_file": "raw/meta_categories/meta_Home_and_Kitchen.jsonl",
            "rev_file": "raw/review_categories/Home_and_Kitchen.jsonl"
        },
        "tools": {
            "meta_file": "raw/meta_categories/meta_Tools_and_Home_Improvement.jsonl",
            "rev_file": "raw/review_categories/Tools_and_Home_Improvement.jsonl"
        }
    }
    
    os.makedirs(os.path.join(data_dir, 'ingest'), exist_ok=True)
    
    for cat, paths in categories.items():
        cat_dir = os.path.join(data_dir, cat)
        meta_target = os.path.join(cat_dir, 'metadata')
        os.makedirs(meta_target, exist_ok=True)
        
        # 1. Handle Metadata
        if "meta_dir" in paths:
            # Move shard folder
            source = os.path.join(data_dir, paths["meta_dir"])
            if os.path.exists(source):
                print(f"📦 Moving {cat} shards...")
                for f in os.listdir(source):
                    shutil.move(os.path.join(source, f), os.path.join(meta_target, f))
                os.rmdir(source)
        elif "meta_file" in paths:
            # Move single file
            source = os.path.join(data_dir, paths["meta_file"])
            if os.path.exists(source):
                print(f"📄 Moving {cat} metadata...")
                shutil.move(source, os.path.join(cat_dir, "metadata.jsonl"))
        
        # 2. Handle Reviews
        source_rev = os.path.join(data_dir, paths["rev_file"])
        if os.path.exists(source_rev):
            print(f"💬 Moving {cat} reviews...")
            shutil.move(source_rev, os.path.join(cat_dir, "reviews.jsonl"))

    print("🎉 Reorganization complete. Folders are now clean and professional.")

if __name__ == "__main__":
    organize_dataset()
