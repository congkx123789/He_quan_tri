#!/bin/bash
echo "🛑 PROMPT: Killing old pipeline processes..."
pkill -f "python3 python/enterprise_loader.py" || true
pkill -f "python3 python/ai_orchestrator.py" || true
docker exec -i oracle-23ai pkill -f sqlplus || true

echo "🧹 PROMPT: Cleaning Oracle sessions..."
docker exec -i oracle-23ai sqlplus -S / as sysdba <<EOS
ALTER SESSION SET CONTAINER = FREEPDB1;
BEGIN
  FOR r IN (select sid,serial# from v\$session where username = 'SYSTEM') LOOP
    EXECUTE IMMEDIATE 'alter system kill session ''' || r.sid || ',' || r.serial# || ''' IMMEDIATE';
  END LOOP;
END;
/
EOS

echo "🚀 PROMPT: Starting Turbo Ingestion (32GB Mode)..."
(./venv_ingest/bin/python3 python/enterprise_loader.py > ingest.log 2>&1) &

echo "🧠 PROMPT: Starting GPU AI Orchestrator (BGE-M3)..."
(./venv_ingest/bin/python3 python/ai_orchestrator.py > ai_orchestrator.log 2>&1) &

echo "✅ PROMPT: Pipeline rebooted. CHECK logs with: tail -f ingest.log"
