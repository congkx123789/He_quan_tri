# Local Enterprise AI - Professional Makefile

.PHONY: setup-venv setup-docker clean-data push-config

# Mode A: Local Virtual Environment
setup-venv:
	@echo "🚀 Launching Mode A: Python Virtual Environment..."
	chmod +x setup_enterprise_ai.sh
	./setup_enterprise_ai.sh

# Mode B: Full Dockerization
setup-docker:
	@echo "🐳 Launching Mode B: Total Isolation (Docker)..."
	docker-compose --profile setup-mode up --build data-engine
	docker-compose up -d oracle ollama

# Mode C: Portable Deployment (New Machine)
deploy:
	@echo "🌐 Launching Mode C: Portable Deployment..."
	chmod +x deploy_new_machine.sh
	./deploy_new_machine.sh

# Utility: Clean Temporary Files
clean:
	@echo "🧹 Cleaning temporary lock files and caches..."
	rm -rf data/.cache
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Utility: Summary of Data
status:
	@du -sh data/*
	@docker ps

# Git Utility: Push all changes
push:
	@echo "📤 Pushing code to GitHub..."
	git add .
	git commit -m "update: deployment scripts and AI modernization fixes"
	git push origin main

# Cloud Sync: Oracle Snapshots via Hugging Face
snapshot-push:
	@echo "📸 Creating and pushing AI Snapshot to Hugging Face..."
	chmod +x scripts/snapshot_db.sh
	./scripts/snapshot_db.sh
	. && python3 python/hf_snapshot_sync.py push

snapshot-pull:
	@echo "📥 Pulling AI Snapshot from Hugging Face..."
	. && python3 python/hf_snapshot_sync.py pull

# Security Utility: Zero-Trace Cleanup (For Public Machines)
logout:
	@echo "🔒 Logging out: Removing .env and stopping containers..."
	docker compose stop
	rm -f .env
	@echo "✅ Credentials removed."

purge:
	@echo "🚨 PURGING PROJECT: Removing ALL traces (Data, Vectors, Keys)..."
	docker compose down -v
	rm -rf sql/dumps/*.dmp
	rm -rf sql/dumps/*.log
	rm -f .env
	rm -rf .venv
	rm -rf __pycache__
	@echo "🧹 Clearing Bash history for safety..."
	history -c && history -w
	@echo "✅ PURGE COMPLETE. This machine is now clean."
