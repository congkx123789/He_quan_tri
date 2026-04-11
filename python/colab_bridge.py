import os
import shutil

def colab_sync_report():
    print("🌉 [Colab Bridge] Examining Google Drive sync status...")
    drive_path = "/content/drive/MyDrive/He_quan_tri"
    if not os.path.exists(drive_path):
        print("❌ Error: Google Drive path not found. Ensure Drive is mounted.")
        return
    
    # Check data volume on Drive
    data_dir = os.path.join(drive_path, 'data')
    if os.path.exists(data_dir):
        size_bytes = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                         for dirpath, dirnames, filenames in os.walk(data_dir) 
                         for filename in filenames)
        print(f"📁 Current Managed Data on Drive: {size_bytes/1024**3:.2f} GB")
    else:
        print("📂 Data directory not yet initialized on Drive.")

def prepare_remote_ingest():
    print("📡 [Colab Bridge] Preparing data for remote Oracle Ingestion...")
    # Logic to zip processed CSVs for easy download from Colab to Local
    source = "data/ingest"
    if os.path.exists(source):
        shutil.make_archive("colab_ingest_payload", 'zip', source)
        print("📦 Paylod created: colab_ingest_payload.zip. Download this to your local Oracle machine.")

if __name__ == "__main__":
    colab_sync_report()
