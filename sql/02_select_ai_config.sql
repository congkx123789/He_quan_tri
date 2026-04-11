-- 02_select_ai_config.sql
-- Connecting Oracle 23ai to Local Ollama-Llama 3
-- This enables Natural Language to SQL transformation for 80GB+ Analysis

BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'OLLAMA_LLAMA3',
    attributes   => '{"provider": "ollama", 
                      "host": "http://host.docker.internal:11434", 
                      "model": "llama3", 
                      "embedding_model": "bge-m3"}',
    description  => 'Primary AI Profile for Local Enterprise Amazon Reviews Analysis'
  );
END;
/

-- Enable AI for specific schemas/tables
BEGIN
  DBMS_CLOUD_AI.SET_PROFILE('OLLAMA_LLAMA3');
END;
/

-- Sample AI Usage:
-- SELECT AI 'Tìm cho tôi 3 cái tai nghe bền nhất dưới 2 triệu' FROM DUAL;
