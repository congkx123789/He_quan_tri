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
