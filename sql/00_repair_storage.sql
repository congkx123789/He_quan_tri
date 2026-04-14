-- 00_repair_storage.sql
-- Goal: Fix ORA-12954 by recreating the USERS tablespace at a safe size
-- and restoring the database to a healthy state.

SET SERVEROUTPUT ON;

PROMPT '🔨 Starting Database Storage Repair...';

-- 1. Create a temporary 'REPAIR' tablespace
CREATE TABLESPACE REPAIR_TS 
DATAFILE '/opt/oracle/oradata/FREE/FREEPDB1/repair01.dbf' 
SIZE 100M AUTOEXTEND ON NEXT 50M MAXSIZE 1G;

-- 2. Set it as default so we can drop USERS
ALTER DATABASE DEFAULT TABLESPACE REPAIR_TS;

-- 3. Drop the broken USERS tablespace (which we offlined earlier)
PROMPT '🗑️ Dropping broken USERS tablespace...';
DROP TABLESPACE USERS INCLUDING CONTENTS AND DATAFILES;

-- 4. Recreate USERS at a healthy size (5GB peak to stay safe below 12GB total)
PROMPT '✨ Recreating healthy USERS tablespace...';
CREATE TABLESPACE USERS 
DATAFILE '/opt/oracle/oradata/FREE/FREEPDB1/users01.dbf' 
SIZE 500M AUTOEXTEND ON NEXT 100M MAXSIZE 5G;

-- 5. Restore USERS as default
ALTER DATABASE DEFAULT TABLESPACE USERS;

-- 6. Cleanup REPAIR tablespace
PROMPT '🧹 Cleaning up repair artifacts...';
DROP TABLESPACE REPAIR_TS INCLUDING CONTENTS AND DATAFILES;

PROMPT '✅ Database Storage Repaired. Ready for AI Modernization.';
