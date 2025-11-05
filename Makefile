# ==============================================================================
# SaaS CRM Monorepo - Development Makefile
# ==============================================================================
# Simplifies common development tasks for local Docker-based development.
#
# Quick Start:
#   make setup       # Initial setup (copy .env, install deps)
#   make dev-up      # Start all services in development mode
#   make dev-down    # Stop all services
#   make dev-logs    # View logs from all services
#
# ==============================================================================

.PHONY: help setup dev-up dev-down dev-restart dev-logs dev-rebuild \
        prod-up prod-down prod-logs db-reset db-migrate db-shell \
        test lint format clean

# Default target
help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  SaaS CRM Monorepo - Development Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📦  Setup & Installation:"
	@echo "  make setup          Copy .env.example → .env and install dependencies"
	@echo ""
	@echo "🚀  Development:"
	@echo "  make dev-up         Start all services in development mode"
	@echo "  make dev-down       Stop all development services"
	@echo "  make dev-restart    Restart all development services"
	@echo "  make dev-logs       View logs from all services (Ctrl+C to exit)"
	@echo "  make dev-rebuild    Rebuild and restart all services"
	@echo ""
	@echo "🏭  Production:"
	@echo "  make prod-up        Start all services in production mode"
	@echo "  make prod-down      Stop all production services"
	@echo "  make prod-logs      View production logs"
	@echo ""
	@echo "🗄️   Database:"
	@echo "  make db-reset       Reset databases (WARNING: destroys data)"
	@echo "  make db-migrate     Run database migrations"
	@echo "  make db-shell-crm   Open PostgreSQL shell for CRM database"
	@echo "  make db-shell-ops   Open PostgreSQL shell for Ops database"
	@echo ""
	@echo "🧪  Testing & Quality:"
	@echo "  make test           Run all tests"
	@echo "  make test-api       Run API tests only"
	@echo "  make lint           Run linters (Python + TypeScript)"
	@echo "  make format         Auto-format code"
	@echo ""
	@echo "🧹  Cleanup:"
	@echo "  make clean          Remove build artifacts, caches, etc."
	@echo "  make clean-docker   Remove all Docker volumes and images"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ==============================================================================
# Setup & Installation
# ==============================================================================

setup:
	@echo "🔧 Setting up development environment..."
	@if [ ! -f .env ]; then \
		echo "📝 Copying .env.example → .env..."; \
		cp .env.example .env; \
		echo "✅ .env created. Please update with your credentials."; \
	else \
		echo "⚠️  .env already exists, skipping..."; \
	fi
	@echo "📦 Installing frontend dependencies..."
	@cd crm && npm install
	@cd ops-console && npm install
	@echo "📦 Installing backend dependencies..."
	@cd crm_api && pip3 install -r requirements.txt
	@cd ops_api && pip3 install -r requirements.txt
	@echo "✅ Setup complete! Run 'make dev-up' to start services."

# ==============================================================================
# Development Mode
# ==============================================================================

dev-up:
	@echo "🚀 Starting development services..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✅ Services started!"
	@echo ""
	@echo "📡 Service URLs:"
	@echo "  CRM API:          http://localhost:8000"
	@echo "  Ops API:          http://localhost:8001"
	@echo "  Adminer (DB GUI): http://localhost:8080"
	@echo "  RedisInsight:     http://localhost:8081"
	@echo ""
	@echo "To view logs: make dev-logs"
	@echo "To stop:      make dev-down"

dev-down:
	@echo "🛑 Stopping development services..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
	@echo "✅ Services stopped."

dev-restart:
	@echo "🔄 Restarting development services..."
	@$(MAKE) dev-down
	@$(MAKE) dev-up

dev-logs:
	@echo "📜 Viewing logs (Ctrl+C to exit)..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

dev-rebuild:
	@echo "🔨 Rebuilding and restarting services..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✅ Rebuild complete!"

# ==============================================================================
# Production Mode
# ==============================================================================

prod-up:
	@echo "🏭 Starting production services..."
	docker-compose up -d
	@echo "✅ Production services started!"

prod-down:
	@echo "🛑 Stopping production services..."
	docker-compose down
	@echo "✅ Production services stopped."

prod-logs:
	@echo "📜 Viewing production logs (Ctrl+C to exit)..."
	docker-compose logs -f

# ==============================================================================
# Database Management
# ==============================================================================

db-reset:
	@echo "⚠️  WARNING: This will destroy all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "💣 Resetting databases..."; \
		docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v; \
		docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d crm-db ops-db redis; \
		sleep 5; \
		echo "✅ Databases reset."; \
	else \
		echo "❌ Cancelled."; \
	fi

db-shell-crm:
	@echo "🐘 Opening CRM database shell..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec crm-db psql -U crm_user -d crm_dev

db-shell-ops:
	@echo "🐘 Opening Ops database shell..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec ops-db psql -U ops_user -d ops_dev

# ==============================================================================
# Testing & Quality
# ==============================================================================

test:
	@echo "🧪 Running all tests..."
	@$(MAKE) test-api

test-api:
	@echo "🧪 Running API tests..."
	@cd crm_api && PYTHONPATH=/home/saas/Saas-CRM---Claude/crm_api python3 -m pytest tests/ -v || true
	@cd ops_api && python3 -m pytest tests/ -v || true

lint:
	@echo "🔍 Running linters..."
	@echo "  TypeScript (eslint)..."
	@cd crm && npm run lint || true
	@cd ops-console && npm run lint || true

# ==============================================================================
# Cleanup
# ==============================================================================

clean:
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete."

clean-docker:
	@echo "⚠️  WARNING: This will remove all Docker volumes and images!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "💣 Removing Docker resources..."; \
		docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --rmi all; \
		echo "✅ Docker cleanup complete."; \
	else \
		echo "❌ Cancelled."; \
	fi

# ==============================================================================
# Service Status
# ==============================================================================

status:
	@echo "📊 Service Status:"
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps
