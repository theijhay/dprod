.PHONY: help setup dev test lint clean build

help: ## Show this help message
	@echo "Dprod Development Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Set up development environment
	@echo "Setting up Dprod development environment..."
	@./scripts/setup-dev.sh

dev: ## Start development environment
	@echo "Starting Dprod development environment..."
	@docker-compose up --build

dev-api: ## Start API server only
	@echo "Starting API server..."
	@poetry run uvicorn services.api.core.main:app --reload --host 0.0.0.0 --port 8000

dev-cli: ## Start CLI development
	@echo "Starting CLI development..."
	@cd tools/cli && npm run dev

dev-frontend: ## Start frontend development
	@echo "Starting frontend development..."
	@cd tools/frontend && npm run dev

test: ## Run all tests
	@echo "Running tests..."
	@pytest

test-api: ## Run API tests
	@echo "Running API tests..."
	@cd services/api && pytest

test-cli: ## Run CLI tests
	@echo "Running CLI tests..."
	@cd tools/cli && npm test

lint: ## Run linting
	@echo "Running linting..."
	@black .
	@isort .
	@flake8 .

clean: ## Clean up development environment
	@echo "Cleaning up..."
	@docker-compose down -v
	@docker system prune -f

build: ## Build all packages
	@echo "Building all packages..."
	@cd services/api && poetry run python -m build
	@cd tools/cli && npm run build
	@cd tools/frontend && npm run build

install: ## Install all dependencies
	@echo "Installing dependencies..."
	@poetry install
	@cd tools/cli && npm install
	@cd tools/frontend && npm install
