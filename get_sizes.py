from huggingface_hub import HfApi
api = HfApi()
info = api.dataset_info('McAuley-Lab/Amazon-Reviews-2023')
cats = ['Electronics', 'Home_and_Kitchen', 'Tools_and_Home_Improvement', 'Toys_and_Games']
total = 0
for f in info.siblings:
    path = f.rfilename
    if any(cat in path for cat in cats) and ('jsonl' in path or 'parquet' in path):
        # Sizes are not in siblings usually, checking dataset_info.siblings directly might be None
        # We might need to use HfFileSystem to get sizes
        pass

from huggingface_hub import HfFileSystem
fs = HfFileSystem()
total = 0
files = fs.glob("datasets/McAuley-Lab/Amazon-Reviews-2023/raw/**/*")
files += fs.glob("datasets/McAuley-Lab/Amazon-Reviews-2023/raw_meta_*/**/*")

for file in files:
    if any(cat in file for cat in cats):
        size = fs.du(file)
        if size > 0:
            print(f"{file}: {size / 1024**2:.2f} MB")
            total += size

print(f"\n--- TOTAL: {total / 1024**3:.2f} GB ---")
