#!/bin/bash
# auto_restore.sh
# One-Touch Restore script for Local Enterprise AI (290k Snapshot)

set -e

echo "🚀 Starting One-Touch AI Restore..."

# 1. Environment Check
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Copy .env.example and add your HF_TOKEN."
    exit 1
fi

# 2. Setup Virtual Environment for HF Pull
echo "🐍 Setting up temporary Python environment..."
python3 -m venv .restore_venv
.restore_venv/bin/pip install huggingface_hub python-dotenv

# 3. Pull Snapshot from Hugging Face
echo "📥 Downloading 1.6GB Snapshot from Hugging Face..."
.restore_venv/bin/python3 python/hf_snapshot_sync.py pull

# 4. Start Infrastructure
echo "🐳 Starting Oracle 26ai Container..."
docker-compose up -d oracle-26ai

echo "⌛ Waiting for Oracle to be ready (approx 1 min)..."
until docker exec oracle-26ai healthcheck.sh 2>/dev/null; do
    echo -n "."
    sleep 5
done
echo "✅ Oracle is healthy!"

# 5. Restore Database
echo "📦 Restoring 290,000 records & Vector Index (impdp)..."
docker exec -i oracle-26ai impdp sys/OracleAdmin123@FREEPDB1 as sysdba \
    directory=CLOUD_SYNC_DIR \
    dumpfile=enterprise_snapshot.dmp \
    logfile=import.log \
    schemas=SELECT_AI \
    table_exists_action=REPLACE \
    reuse_datafiles=y

echo "✨ RESTORE COMPLETE! 290,000 records are now live and indexed."
echo "💡 You can now run semantic searches in Oracle AI."
