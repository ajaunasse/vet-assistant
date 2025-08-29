# NeuroVet Makefile - Docker Commands
# Usage: make <command>

.PHONY: help build up down restart logs clean dev stop backend frontend db shell test migrate-auto migrate-up migrate-down migrate-history migrate-current

# Default target
help: ## Show this help message
	@echo "NeuroVet Docker Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Main Commands
build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

dev: ## Start all services in development mode with logs
	docker-compose up

down: ## Stop and remove all containers
	docker-compose down

restart: ## Restart all services
	docker-compose restart

stop: ## Stop all services (without removing)
	docker-compose stop

# Service-specific commands
backend: ## Start only backend service
	docker-compose up -d db backend

frontend: ## Start only frontend service
	docker-compose up -d frontend

db: ## Start only database service
	docker-compose up -d db

# Utility commands  
logs: ## Show logs for all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-db: ## Show database logs
	docker-compose logs -f db

shell: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-db: ## Open MySQL shell
	docker-compose exec db mysql -u neurovet -p neurovet_db

# Development commands
install: ## Install backend dependencies
	docker-compose exec backend uv sync

# Database commands
db-init: ## Initialize database (create tables)
	docker-compose exec backend uv run python scripts/init_db.py init

db-check: ## Check database status and tables
	docker-compose exec backend uv run python scripts/init_db.py check

db-reset: ## Reset database (drop and recreate tables)
	docker-compose exec db mysql -u root -proot_password -e "DROP DATABASE IF EXISTS neurovet_db; CREATE DATABASE neurovet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
	docker-compose exec db mysql -u root -proot_password -e "GRANT ALL PRIVILEGES ON neurovet_db.* TO 'neurovet'@'%';"
	make db-init

db-setup: ## Complete database setup (start db, wait, init tables)
	@echo "🚀 Starting database setup..."
	docker-compose up -d db
	@echo "⏳ Waiting for database to be ready..."
	@until docker-compose exec db mysqladmin ping -h localhost -u root -proot_password --silent; do \
		echo "Waiting for database..."; \
		sleep 2; \
	done
	@echo "✅ Database is ready!"
	make db-init
	@echo "🎉 Database setup complete!"

db-migrate: ## Run database migrations (create tables)
	make db-init

# Alembic migration commands
migrate-auto: ## Generate new migration from model changes
	@echo "🔄 Generating migration from model changes..."
	@read -p "Enter migration description: " desc; \
	docker-compose exec backend uv run alembic revision --autogenerate -m "$$desc"

migrate-up: ## Apply pending migrations
	@echo "⬆️  Applying pending migrations..."
	docker-compose exec backend uv run alembic upgrade head

migrate-down: ## Rollback last migration  
	@echo "⬇️  Rolling back last migration..."
	docker-compose exec backend uv run alembic downgrade -1

migrate-history: ## Show migration history
	@echo "📜 Migration history:"
	docker-compose exec backend uv run alembic history --verbose

migrate-current: ## Show current migration
	@echo "📍 Current migration:"
	docker-compose exec backend uv run alembic current

db-seed: ## Seed database with sample data (if needed)
	@echo "🌱 No seed data defined yet"

db-backup: ## Backup database
	@echo "💾 Creating database backup..."
	docker-compose exec db mysqldump -u neurovet -pneurovet_pass neurovet_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created!"

db-status: ## Show database connection status
	@echo "📊 Checking database status..."
	@docker-compose exec db mysqladmin ping -h localhost -u root -proot_password > /dev/null 2>&1 && echo "✅ Database: Connected" || echo "❌ Database: Disconnected"

test: ## Run backend tests
	docker-compose exec backend uv run pytest

lint: ## Run backend linting
	docker-compose exec backend uv run ruff check .

format: ## Format backend code
	docker-compose exec backend uv run ruff format .

# Cleanup commands
clean: ## Remove all containers, volumes, and images
	docker-compose down -v --remove-orphans
	docker system prune -af

clean-volumes: ## Remove only volumes (keeps images)
	docker-compose down -v

rebuild: ## Clean build and restart
	make clean
	make build
	make up

# Health check
health: ## Check service health
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend: OK" || echo "❌ Backend: DOWN"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend: OK" || echo "❌ Frontend: DOWN"  
	@curl -s http://localhost:3000/api/v1/health > /dev/null && echo "✅ Frontend → Backend: OK" || echo "❌ Frontend → Backend: DOWN"
	@docker-compose exec db mysqladmin ping -h localhost -u root -proot_password > /dev/null 2>&1 && echo "✅ Database: OK" || echo "❌ Database: DOWN"