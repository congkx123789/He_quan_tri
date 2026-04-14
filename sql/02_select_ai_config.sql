-- 02_select_ai_config.sql
-- Configure Oracle 23ai "Select AI" to use GPU-accelerated Ollama
-- Using Llama 3 for chat/reasoning and BGE-M3 for embeddings

SET SERVEROUTPUT ON;

PROMPT '🤖 Configuring Oracle 23ai AI Engine...';

-- 1. Create Credential for Ollama (Ollama doesn't require auth by default, but Oracle needs a profile)
BEGIN
    DBMS_CLOUD.CREATE_CREDENTIAL(
        credential_name => 'OLLAMA_CRED',
        username        => 'ollama',
        password        => 'ollama'
    );
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -27486 OR SQLCODE = -955 THEN NULL;-- Already exists
        ELSE RAISE;
        END IF;
END;
/

-- 2. Configure AI Model Profile for BGE-M3 (Embeddings)
BEGIN
    DBMS_CLOUD_AI.DROP_PROFILE(profile_name => 'OLLAMA_EMBED', silent => TRUE);
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'OLLAMA_EMBED',
        attributes   => '{
            "provider": "ollama",
            "credential_name": "OLLAMA_CRED",
            "base_url": "http://ollama:11434/api",
            "model": "bge-m3",
            "task": "embedding"
        }'
    );
END;
/

-- 3. Configure AI Model Profile for Llama 3 (Chat/Natural Language to SQL)
BEGIN
    DBMS_CLOUD_AI.DROP_PROFILE(profile_name => 'OLLAMA_CHAT', silent => TRUE);
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'OLLAMA_CHAT',
        attributes   => '{
            "provider": "ollama",
            "credential_name": "OLLAMA_CRED",
            "base_url": "http://ollama:11434/api",
            "model": "llama3",
            "task": "chat"
        }'
    );
END;
/

PROMPT '✅ AI Profile "OLLAMA_CHAT" and "OLLAMA_EMBED" Ready.';
