# 🤖 Local Enterprise AI: 83GB Amazon Reviews Analysis
[![Database: Oracle 23ai](https://img.shields.io/badge/Database-Oracle_23ai-red)](#)
[![AI Shell: Ollama-Llama3](https://img.shields.io/badge/AI-Ollama--Llama3-blue)](#)
[![Data Volume: 83GB](https://img.shields.io/badge/Data-83GB--Amazon--2023-green)](#)
[![Hardware: Enterprise Workstation](https://img.shields.io/badge/Hardware-Enterprise--Grade-orange)](#)

A high-performance, private AI system built on **Oracle Database 23ai Free Edition** and **Ollama**, designed to perform high-velocity data engineering, semantic vector analysis, and natural language querying over a massive **83.6GB Amazon Reviews 2023** dataset.

![Project Banner](assets/banner.png)

## 🌟 Executive Summary
This project demonstrates a production-grade **Local Enterprise AI** architecture. It bridges the gap between massive, unstructured data (80GB+ JSONL/Parquet) and actionable business intelligence using a "Thinking" Vector Database. The entire stack runs locally on a personal machine, ensuring 100% data privacy and zero API costs.

---

## 🚀 Key Technological Pillars

### 1. High-Velocity Data Engineering (The "Enterprise Engine")
- **Scale**: Successfully processed over **67,000,000 customer reviews** and millions of product specs.
- **Safe-Mode Architecture**: Optimized for high-volume environments using a **Streaming Processor** that maintains a memory footprint of **< 1GB** even when handling 30GB+ individual files.
- **In-Stream Cleaning**: Automatic price normalization, high-performance deduplication (via hashing), and HTML scrubbing during the ingestion path.

### 2. The Hybrid Thinking Database (Oracle 23ai)
- **Multi-Model Native Support**: Managing Relational (Sales), Document (JSON Specs), and Unstructured (Vector Reviews) data in one ACID-compliant engine.
- **Direct Path Loading**: Leverages Oracle's `/*+ APPEND */` logic and External Tables to achieve "bare-metal" throughput during ingestion from CSV to Vector tables.
- **Semantic Vector Search**: Native HNSW indexing for instant sentiment and topic discovery across millions of records.

### 3. Generative AI Orientation (Select AI & PL/SQL Engine)
- **Select AI Integration**: Bridges Oracle's internal query engine to a local **Ollama** instance serving **Llama 3 (8B)**.
- **CORE_AI_PKG**: Professional PL/SQL engine for centralized semantic search and AI reasoning.
- **JSON Relational Duality**: Exposes relational data as structure-perfect JSON documents for modern web apps.

### 4. Graph & Deep Learning Integration
- **Native Property Graph**: Links products and reviews for graph-based pattern discovery.
- **Cancer Survival Mamba**: (Incubating) A secondary project focused on deep learning for TCGA cancer survival prediction.

## ☁️ Run on Google Colab (Cloud Acceleration)
If you want to use Colab's GPU for LLM acceleration or remote data engineering:
1. **Upload**: Upload this repository to your **Google Drive** (e.g., `/MyDrive/He_quan_tri`).
2. **Launch**: Open **`Local_Enterprise_AI_Colab.ipynb`** in Google Colab.
3. **Connect**: Mount Drive and run the cells to utilize T4/A100 GPUs for Llama 3 processing.
4. **Ingest**: Processed data can be synced back to your local Oracle machine via `python/colab_bridge.py`.

---

## 🏗️ Architecture & Data Flow
```mermaid
graph TD
    A[Amazon 2023 Raw Data - 83GB] --> B[Data Acquisition Engine]
    B -->|Verified Parquet/JSONL| C[Custom Hierarchy Organization]
    C -->|Cleaned Streaming CSV| D[Oracle External Tables]
    D -->|Direct Path Load| E[Oracle 23ai Vector Tables]
    E -->|Vector Search| F[Semantic Analysis]
    E -->|Select AI| G[Ollama / Llama 3]
    G -->|SQL Translation| H[Admin Dashboard / APEX]
```

---

## 📂 Project Organization
- `/python`: The Engineering Core (Downloader, Organizer, Safe-Mode Processor).
- `/sql`: The AI/DB Core (Schema, Vector Setup, Select AI Configuration, Ingestion).
- `/data`: Organized dataset hierarchy (Excluded from Git, documented via `data/README.md`).
- `/scripts`: Container orchestration and entrypoints.

---

## 📍 Multi-Mode Deployment (Portability)

### Mode A: Python Virtual Environment (Lightweight)
Perfect for local development. Handles data acquisition and organization via a local venv.
```bash
make setup-venv
```

### Mode B: Total Isolation (Docker Mode)
The entire "Enterprise Engine" is containerized. Requires only Docker to be installed on the host.
```bash
make setup-docker
```

---

## 💻 New Machine Setup (3-Step Deploy)

To run this entire stack on a new machine with full AI modernization enabled:

### 1. Requirements
- **Docker** & **Docker Compose**
- **NVIDIA Drivers** (Optional for GPU acceleration)
- **Python 3.10+**

### 2. Deployment
Clone the repository and run the automated deployment script:
```bash
git clone git@github.com:congkx123789/He_quan_tri.git
cd He_quan_tri
chmod +x deploy_new_machine.sh
./deploy_new_machine.sh
```

### 3. Verification
Once complete, you can test the AI search via SQL:
```sql
-- Query the JSON Duality View
SELECT data FROM PRODUCT_DETAILS_DV FETCH FIRST 1 ROWS ONLY;
```

---

## 🚨 Public Machine Security Guide (Zero-Trace)

If you are running this project on a machine that is **not yours** or is **public**, follow these steps to ensure total privacy:

### 1. Silent Deployment
When running `./deploy_new_machine.sh`, your Hugging Face Token and Database Password will be **hidden from the screen** during input. 

### 2. Ephemeral Session
While working, your credentials are stored only in `.env` (which is git-ignored).

### 3. Total Cleanup (Wipe Everything)
Before leaving the machine, run:
```bash
make purge
```
**This will:**
- Stop all AI services.
- **Delete the Database Vectors** (Docker volumes).
- **Delete your Tokens** (`.env`).
- **Clear Terminal History** (preventing anyone from seeing your previous commands).

For a faster cleanup that only removes keys but keeps the data:
```bash
make logout
```

---

## ⚙️ Hardware Specifications (Reference)
This system is optimized for high-end local workstations:
- **Processor**: High-performance Multicore CPU.
- **GPU**: NVIDIA GPU with 8GB+ VRAM (Recommended for LLM acceleration).
- **Memory**: 32GB+ RAM (Supported via Safe-Mode Streaming).
- **Storage**: ~250GB Free SSD space target.

---

## 📎 License & Security
- **Security**: All API Keys/Tokens are managed via `.env` (excluded from Git).
- **Privacy**: No data leaves the local network. All LLM processing is handled by Ollama.

*Crafted with 🤖 for Enterprise-grade AI Demonstrations.*
