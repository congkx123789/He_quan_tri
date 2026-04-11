#!/bin/bash

# setup_enterprise_ai.sh
# Master Orchestrator for Local Enterprise AI (80GB+ System)

set -e # Exit on error

echo "🚀 Starting Master Setup for Local Enterprise AI..."

# 1. Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Creating from template..."
    cp .env.example .env
    echo "‼️  Please edit the .env file and add your HF_TOKEN before running again."
    exit 1
fi

# 2. Virtual Environment Setup
if [ ! -d "venv" ]; then
    echo "📦 Creating Python Virtual Environment..."
    python3 -m venv venv
fi

echo "🐍 Activating Environment & Installing Dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Data Infrastructure
echo "📁 Initializing Data Directory Structure..."
mkdir -p data/electronics data/home_and_kitchen data/tools data/ingest

echo "📥 Starting Data Acquisition (83.6GB Target)..."
# Using the optimized enterprise downloader
python3 python/enterprise_download_80gb.py

echo "🧹 Organizing Dataset into Professional Hierarchy..."
python3 python/organize_data.py

echo "🛠️  Running Safe-Mode Data Engineering (CSV Processing)..."
python3 python/process_for_external.py

# 4. Starting Infrastructure
echo "🐳 Starting Docker Microservices (Oracle, Ollama, APEX)..."
docker-compose up -d

echo "🎉 Setup Complete! You can now analyze your 80GB dataset."
echo "💡 To begin SQL ingestion, run: sqlplus system/OracleAdmin123! @sql/06_ingestion_direct_load.sql"
