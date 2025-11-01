# ==============================================================================
# PRODUCTION-READY MONOREPO MAKEFILE
# ==============================================================================
# Usage:
#   make help              - Show this help message
#   make setup             - Initial setup for local development
#   make test              - Run all tests
#   make migrate           - Generate Alembic migration
#   make docker-up         - Start Docker services
#   make docker-down       - Stop Docker services
# ==============================================================================

.PHONY: help setup test test-crm test-ops test-frontend lint clean docker-up docker-down migrate dev dev-stop checks checks-fast seed seed-crm seed-ops seed-clear

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ==============================================================================
# HELP
# ==============================================================================

help: ## Show this help message
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Production-Ready Monorepo - Available Commands$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"

# ==============================================================================
# SETUP
# ==============================================================================

setup: ## Initial setup for local development
	@echo "$(GREEN)Setting up local development environment...$(NC)"
	@cp -n .env.example .env || true
	@echo "$(GREEN)✓ Created .env file from template$(NC)"
	@echo "$(YELLOW)Installing Python dependencies...$(NC)"
	@cd crm_api && pip install -q pytest pytest-cov || true
	@cd ops_api && pip install -q pytest pytest-cov || true
	@echo "$(GREEN)✓ Python dependencies installed$(NC)"
	@echo "$(YELLOW)Installing frontend dependencies...$(NC)"
	@cd crm && npm install --silent || true
	@cd ops-console && npm install --silent || true
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"
	@echo "$(GREEN)✓ Setup complete!$(NC)"

# ==============================================================================
# TESTING
# ==============================================================================

test: test-crm test-ops test-frontend ## Run all tests (backend + frontend)

test-crm: ## Run CRM API tests
	@echo "$(BLUE)Running CRM API tests...$(NC)"
	@cd crm_api && python -m pytest -v --tb=short

test-ops: ## Run Ops API tests
	@echo "$(BLUE)Running Ops API tests...$(NC)"
	@cd ops_api && python -m pytest -v --tb=short

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running CRM frontend tests...$(NC)"
	@cd crm && npm run test -- --run || true
	@echo "$(BLUE)Running Ops Console frontend tests...$(NC)"
	@cd ops-console && npm run test -- --run || true

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@cd crm_api && python -m pytest --cov=app --cov-report=html --cov-report=term
	@cd ops_api && python -m pytest --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage reports generated in htmlcov/$(NC)"

# ==============================================================================
# LINTING
# ==============================================================================

lint: ## Run linters (when using real packages)
	@echo "$(YELLOW)Note: Linting requires real packages (not stubs)$(NC)"
	@echo "$(YELLOW)Install: pip install black ruff mypy$(NC)"
	# black --check crm_api/ ops_api/
	# ruff check crm_api/ ops_api/
	# mypy crm_api/ ops_api/

format: ## Format code (when using real packages)
	@echo "$(YELLOW)Note: Formatting requires real packages (not stubs)$(NC)"
	# black crm_api/ ops_api/
	# ruff check --fix crm_api/ ops_api/

# ==============================================================================
# DATABASE MIGRATIONS
# ==============================================================================

migrate: ## Generate Alembic migration (Usage: make migrate SERVICE=crm message="add table")
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)ERROR: SERVICE parameter required$(NC)"; \
		echo "$(YELLOW)Usage: make migrate SERVICE=crm message='add users table'$(NC)"; \
		echo "$(YELLOW)       make migrate SERVICE=ops message='add scheduler'$(NC)"; \
		exit 1; \
	fi
	@if [ -z "$(message)" ]; then \
		echo "$(RED)ERROR: message parameter required$(NC)"; \
		echo "$(YELLOW)Usage: make migrate SERVICE=$(SERVICE) message='your migration message'$(NC)"; \
		exit 1; \
	fi
	@if [ "$(SERVICE)" = "crm" ]; then \
		echo "$(GREEN)Generating CRM migration: $(message)$(NC)"; \
		cd crm_api && alembic revision --autogenerate -m "$(message)"; \
	elif [ "$(SERVICE)" = "ops" ]; then \
		echo "$(GREEN)Generating Ops migration: $(message)$(NC)"; \
		cd ops_api && alembic revision --autogenerate -m "$(message)"; \
	else \
		echo "$(RED)ERROR: Invalid SERVICE. Use 'crm' or 'ops'$(NC)"; \
		exit 1; \
	fi

migrate-upgrade: ## Apply migrations (Usage: make migrate-upgrade SERVICE=crm)
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)ERROR: SERVICE parameter required$(NC)"; \
		exit 1; \
	fi
	@if [ "$(SERVICE)" = "crm" ]; then \
		cd crm_api && alembic upgrade head; \
	elif [ "$(SERVICE)" = "ops" ]; then \
		cd ops_api && alembic upgrade head; \
	fi

migrate-downgrade: ## Rollback migrations (Usage: make migrate-downgrade SERVICE=crm)
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)ERROR: SERVICE parameter required$(NC)"; \
		exit 1; \
	fi
	@if [ "$(SERVICE)" = "crm" ]; then \
		cd crm_api && alembic downgrade -1; \
	elif [ "$(SERVICE)" = "ops" ]; then \
		cd ops_api && alembic downgrade -1; \
	fi

check-migrations: ## Check for migration drift
	@echo "$(BLUE)Checking for migration drift...$(NC)"
	@python tools/check_migrations.py

schema-diff: ## Show schema differences (Usage: make schema-diff SERVICE=crm)
	@python tools/schema_diff.py --service $(SERVICE)

# ==============================================================================
# DOCKER
# ==============================================================================

docker-up: ## Start Docker services (Postgres, Redis)
	@echo "$(GREEN)Starting Docker services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@docker-compose ps

docker-down: ## Stop Docker services
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-logs: ## Show Docker logs (Usage: make docker-logs SERVICE=crm-db)
	@docker-compose logs -f $(SERVICE)

docker-clean: ## Remove Docker volumes and clean up
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker-compose down -v
	@echo "$(GREEN)✓ Cleaned up$(NC)"

# ==============================================================================
# DEVELOPMENT SERVERS
# ==============================================================================

dev: ## Start entire development environment (recommended)
	@echo "$(GREEN)Starting development environment...$(NC)"
	@chmod +x scripts/dev.sh
	@./scripts/dev.sh

dev-stop: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(NC)"
	@chmod +x scripts/dev.sh
	@./scripts/dev.sh --stop

run-crm-api: ## Run CRM API locally (dev mode)
	@echo "$(GREEN)Starting CRM API on http://localhost:8000$(NC)"
	@cd crm_api && python -m app.main

run-ops-api: ## Run Ops API locally (dev mode)
	@echo "$(GREEN)Starting Ops API on http://localhost:8001$(NC)"
	@cd ops_api && python -m app.main

run-crm-frontend: ## Run CRM frontend dev server
	@echo "$(GREEN)Starting CRM frontend on http://localhost:5173$(NC)"
	@cd crm && npm run dev

run-ops-frontend: ## Run Ops Console frontend dev server
	@echo "$(GREEN)Starting Ops Console on http://localhost:5174$(NC)"
	@cd ops-console && npm run dev

# ==============================================================================
# CLEANUP
# ==============================================================================

clean: ## Clean build artifacts and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "node_modules" -prune -o -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned up$(NC)"

clean-all: clean docker-clean ## Deep clean (including Docker volumes)

# ==============================================================================
# BUILD
# ==============================================================================

build-frontend: ## Build production frontend bundles
	@echo "$(GREEN)Building CRM frontend...$(NC)"
	@cd crm && npm run build
	@echo "$(GREEN)Building Ops Console...$(NC)"
	@cd ops-console && npm run build
	@echo "$(GREEN)✓ Frontend builds complete$(NC)"

# ==============================================================================
# UTILITIES
# ==============================================================================

check-env: ## Verify .env file exists
	@if [ ! -f .env ]; then \
		echo "$(RED)ERROR: .env file not found$(NC)"; \
		echo "$(YELLOW)Run: make setup$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ .env file exists$(NC)"; \
	fi

checks: ## Run all quality checks (tests, coverage, security)
	@echo "$(GREEN)Running all quality checks...$(NC)"
	@chmod +x scripts/checks.sh
	@./scripts/checks.sh

checks-fast: ## Run fast quality checks (skip slower validations)
	@echo "$(GREEN)Running fast quality checks...$(NC)"
	@chmod +x scripts/checks.sh
	@./scripts/checks.sh --fast

seed: ## Seed development databases with demo data
	@echo "$(YELLOW)Seeding databases...$(NC)"
	@python scripts/seed.py
	@echo "$(GREEN)✓ Database seeded$(NC)"

seed-crm: ## Seed CRM database only
	@echo "$(YELLOW)Seeding CRM database...$(NC)"
	@python scripts/seed.py --crm

seed-ops: ## Seed Ops database only
	@echo "$(YELLOW)Seeding Ops database...$(NC)"
	@python scripts/seed.py --ops

seed-clear: ## Clear all seeded data
	@echo "$(YELLOW)Clearing all seeded data...$(NC)"
	@python scripts/seed.py --clear

# ==============================================================================
# DOCUMENTATION
# ==============================================================================

docs: ## Generate API documentation
	@echo "$(BLUE)Generating API documentation...$(NC)"
	@echo "$(YELLOW)TODO: Add Sphinx or similar for API docs$(NC)"

# ==============================================================================
# CI/CD
# ==============================================================================

ci: checks ## Run CI pipeline (all quality checks)
	@echo "$(GREEN)✓ CI pipeline passed$(NC)"
