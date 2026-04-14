#!/bin/bash

# Enterprise AI Platform - Unified Startup Script (Bigdata Architecture Sync)
echo "🚀 Starting Enterprise AI Platform on Blackwell GPU..."

# 1. Start Infrastructure (Oracle & Ollama)
echo "📂 Starting Infrastructure in Docker..."
docker compose up -d

# 2. Wait for Oracle to be Healthy
echo "⌛ Waiting for Oracle 26ai to be healthy..."
until [ "$(docker inspect -f {{.State.Health.Status}} oracle-26ai)" == "healthy" ]; do
    echo -n "."
    sleep 3
done
echo "✅ Oracle is ready!"

# 3. Launch AI Engine Locally (Total Performance Mode)
echo "🤖 Starting AI Orchestrator on Host (with Blackwell GPU access)..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    
    # Mirror Bigdata: Inject production environment variables
    # Using the verified application user to avoid admin connection errors
    export DB_USER=select_ai
    export DB_PASS=oracle123
    export DB_DSN=localhost:1521/FREEPDB1
    export OLLAMA_HOST=http://localhost:11435
    
    python3 python/ai_orchestrator.py
else
    echo "❌ Virtual environment .venv not found. Run setup first."
    exit 1
fi
