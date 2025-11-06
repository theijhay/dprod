.PHONY: help dev dev-all dev-api dev-cli dev-frontend test clean docker-up docker-down

help: ## Show this help message
	@echo "Dprod - Zero-configuration Deployment Platform"
	@echo ""
	@echo "Quick Start:"
	@echo "  make dev          - Start API + CLI (detector & orchestrator run inside API)"
	@echo "  npm run dev       - Same as 'make dev'"
	@echo ""
	@echo "Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start all services (API includes detector & orchestrator)
	npm run dev

dev-all: ## Start all services including frontend
	npm run dev:all

dev-api: ## Start API server (includes detector & orchestrator)
	npm run dev:api

dev-cli: ## Link CLI globally for development
	npm run dev:cli

dev-frontend: ## Start frontend development server
	npm run dev:frontend

docker-up: ## Start all services with Docker Compose
	npm run docker:up

docker-down: ## Stop Docker Compose services
	npm run docker:down

migrate: ## Run database migrations
	npm run db:migrate

migrate-create: ## Create new migration (usage: make migrate-create MSG="message")
	npm run db:migrate:create "$(MSG)"

test: ## Run all tests
	npm run test

test-api: ## Run API tests only
	npm run test:api

test-detector: ## Run detector tests only
	npm run test:detector

test-orchestrator: ## Run orchestrator tests only
	npm run test:orchestrator

test-cli: ## Run CLI tests only
	npm run test:cli

lint: ## Run code linting
	npm run lint

lint-fix: ## Auto-fix linting issues
	npm run lint:fix

clean: ## Clean up everything (Docker, cache, etc.)
	npm run clean

install: ## Install all dependencies
	@echo "Installing Python dependencies..."
	@poetry install
	@echo "Installing Node.js dependencies..."
	@npm install
