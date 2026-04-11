#!/bin/bash

# scripts/data_entrypoint.sh
# Entrypoint for the Data Engine Container

set -e

echo "🔌 [Data Engine] Booting up..."

# Check for .env variables (passed as env vars in docker-compose)
if [ -z "$HF_TOKEN" ]; then
    echo "❌ ERROR: HF_TOKEN is missing. Please provide it in your .env file."
    exit 1
fi

echo "📥 [Data Engine] Initiating Acquisition Path..."
python3 python/enterprise_download_80gb.py

echo "🧹 [Data Engine] Organizing Hierarchy..."
python3 python/organize_data.py

echo "🛠️  [Data Engine] Running Safe-Mode Engineering..."
python3 python/process_for_external.py

echo "🎉 [Data Engine] Foundation 83.6GB Ready in /app/data"
