#!/bin/bash
# deploy_new_machine.sh
# Automated Deployment Script for Enterprise AI Platform
# Optimized for Oracle 23ai Free (12GB Limit)

set -e

echo "🚀 Starting Enterprise AI Portable Deployment..."

# 1. Environment Verification
echo "🔍 Checking Prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found. Please install Docker first."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 not found. Please install Python 3.10+."; exit 1; }

# 2. Config Initialization
if [ ! -f .env ]; then
    echo "📄 Creating .env from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env created. (Note: HF_TOKEN might be required for full data re-download)."
    else
        echo "ORACLE_PWD=OracleAdmin123" > .env
        echo "ORACLE_PORT=1521" >> .env
        echo "OLLAMA_PORT=11435" >> .env
        echo "DB_USER=SYS" >> .env
        echo "DB_PASS=OracleAdmin123" >> .env
    fi
fi

# 3. Infrastructure Startup
echo "🐳 Starting Containers (Oracle & Ollama)..."
docker compose up -d

# 4. Database Readiness
echo "⌛ Waiting for Oracle Database to be Healthy (this may take 2-3 minutes)..."
until [ "$(docker inspect -f {{.State.Health.Status}} oracle-26ai)" == "healthy" ]; do
    echo -n "."
    sleep 5
done
echo -e "\n✅ Oracle is ready!"

# 5. SQL Provisioning (The Modernization Sequence)
echo "📦 Running SQL Provisioning Sequence..."

RUN_SQL() {
    echo "⚡ Executing: $1"
    docker exec -i oracle-26ai sqlplus -s sys/OracleAdmin123@FREEPDB1 as sysdba < "$1"
}

# Step A: Infrastructure & Repair (Ensure USERS_V2 exists and DB is optimized)
RUN_SQL sql/00_repair_storage.sql

# Step B: Schema & Config
RUN_SQL sql/01_schema.sql
RUN_SQL sql/02_select_ai_config.sql

# Step C: Phase 2 Modernization (Items 7-12)
RUN_SQL sql/07_12_modernization_setup.sql

# 6. Python Environment
if [ ! -d ".venv" ]; then
    echo "🐍 Setting up Python Virtual Environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install oracledb sentence-transformers torch python-dotenv
echo "✅ Python dependencies installed."

echo "🎉 DEPLOYMENT COMPLETE!"
echo "------------------------------------------------"
echo "You can now run the AI Orchestrator:"
echo "source .venv/bin/activate && python3 python/ai_orchestrator.py"
echo "------------------------------------------------"
