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
    echo "🔒 Initializing Security Configuration..."
    echo -n "🔑 Enter Hugging Face Token (input will be hidden): "
    read -s HF_TOKEN
    echo -e "\n🔑 Enter Oracle Database Password (input will be hidden): "
    read -s DB_PASS
    echo -e "\n"

    # Create .env safely
    cat <<EOF > .env
HF_TOKEN=$HF_TOKEN
ORACLE_PWD=$DB_PASS
ORACLE_PORT=1521
OLLAMA_PORT=11435
DB_USER=SYS
DB_PASS=$DB_PASS
OLLAMA_ENDPOINT=http://ollama-26ai:11434
EOF
    echo "✅ .env created safely."
    unset HF_TOKEN
    unset DB_PASS
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

# 5. Data & Vector Restoration (Optional Cloud Sync)
echo "------------------------------------------------"
echo "☁️  Do you want to restore AI Vectors from Hugging Face? (y/n)"
read -r sync_choice
if [ "$sync_choice" == "y" ]; then
    echo "📥 Pulling Snapshot from Cloud..."
    source .venv/bin/activate && python3 python/hf_snapshot_sync.py pull
    
    echo "🔄 Importing Snapshot into Oracle (impdp)..."
    docker exec -i oracle-26ai bash -c "export ORACLE_HOME=/opt/oracle/product/23ai/dbhome_1; export PATH=\$PATH:\$ORACLE_HOME/bin; impdp sys/OracleAdmin123@FREEPDB1 as sysdba directory=CLOUD_SYNC_DIR dumpfile=enterprise_snapshot.dmp logfile=import.log transform=disable_archive_logging:y"
    echo "✅ AI Vectors restored from Cloud."
else
    echo "⏭️  Skipping Cloud Sync. Running standard SQL provisioning..."
    # Step A: Infrastructure & Repair
    docker exec -i oracle-26ai sqlplus -s sys/OracleAdmin123@FREEPDB1 as sysdba < sql/00_repair_storage.sql
    docker exec -i oracle-26ai sqlplus -s sys/OracleAdmin123@FREEPDB1 as sysdba < sql/01_schema.sql
    docker exec -i oracle-26ai sqlplus -s sys/OracleAdmin123@FREEPDB1 as sysdba < sql/02_select_ai_config.sql
    docker exec -i oracle-26ai sqlplus -s sys/OracleAdmin123@FREEPDB1 as sysdba < sql/07_12_modernization_setup.sql
fi

echo "✅ Deployment sequence finalized."

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
