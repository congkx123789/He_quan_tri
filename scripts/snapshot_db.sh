#!/bin/bash
# scripts/snapshot_db.sh
# Export theized Oracle state (max 12GB) for Cloud Sync

set -e

DUMP_DIR="./sql/dumps"
mkdir -p "$DUMP_DIR"
chmod 777 "$DUMP_DIR"

echo "📸 Initiating Oracle DB Snapshot..."

# 1. Ensure the PDB is identified and the directory is mapped inside Oracle
# We use the SYS user to create/verify the directory object
docker exec -i oracle-26ai sqlplus -s sys/OracleAdmin123@FREEPDB1 as sysdba <<EOF
SET FEEDBACK OFF
CREATE OR REPLACE DIRECTORY CLOUD_SYNC_DIR AS '/opt/oracle/admin/FREE/dpdump';
GRANT READ, WRITE ON DIRECTORY CLOUD_SYNC_DIR TO PUBLIC;
EXIT;
EOF

# 2. Run Data Pump Export (expdp)
# We export the whole schema containing our Vectors, Graphs, and Duality Views
echo "📦 Exporting vectors and schema (expdp)..."
docker exec -i oracle-26ai bash -c "export ORACLE_HOME=/opt/oracle/product/26ai/dbhomeFree; export PATH=\$ORACLE_HOME/bin:\$PATH; export LD_LIBRARY_PATH=\$ORACLE_HOME/lib; expdp \\\"sys/OracleAdmin123@FREEPDB1 as sysdba\\\" directory=CLOUD_SYNC_DIR dumpfile=enterprise_snapshot.dmp logfile=export.log reuse_dumpfiles=y schemas=SELECT_AI"

echo "✅ Snapshot created: $DUMP_DIR/enterprise_snapshot.dmp"
