# 🏛️ System Architecture: Local Enterprise AI

This document details the flow of data and intelligence within the system.

## 🔄 Interaction Flow

1.  **User Input (UI)**: The user interacts with an Oracle APEX dashboard or a search interface.
2.  **Select AI (SQL Layer)**: Oracle 23ai receives a Natural Language query. It looks up the Metadata (Table names, column comments).
3.  **Local API Call**: Oracle uses `DBMS_CLOUD_AI` to send a REST request to `http://host.docker.internal:11434`.
4.  **Local LLM (Ollama)**: Running on the **GPU accelerator**, Ollama processes the prompt and returns valid SQL code.
5.  **Execution**: Oracle executes the generated SQL against the locally stored datasets (up to 50GB).
6.  **Results**: Data is returned to the UI as structured tables, JSON objects, or Semantic search matches.

## 💾 Hybrid Data Storage

| Data Type | Table | Purpose |
| :--- | :--- | :--- |
| **Relational** | `PRODUCTS`, `SALES` | Exact calculations, inventory tracking, financial reporting. |
| **Document** | `PRODUCT_SPECS` | Flexibility for varying hardware specs (RAM, CPU, Sizes). |
| **Vector** | `CUSTOMER_REVIEWS` | Semantic search (e.g., "Find durable products"). |

## 🛡️ Security & Privacy
- **No Internet Required**: Once Docker images and models are pulled, the entire system can run air-gapped.
- **VPC Simulation**: Docker bridge network ensures isolated communication between the DB and the host.
