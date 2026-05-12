# Smart Wish Tracker - Development Makefile

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
VENV_DIR := .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_PYTHON) -m pip

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "Smart Wish Tracker - Available Make Targets:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Environment Setup
.PHONY: venv
venv: ## Create virtual environment
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "Installing development dependencies..."
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PIP) install --upgrade pip setuptools wheel; \
		$(VENV_PIP) install -r requirements.txt; \
	else \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi

.PHONY: setup
setup: venv install-dev setup-pre-commit ## Complete development environment setup
	@echo "Development environment setup complete!"
	@echo "To activate the virtual environment, run: source $(VENV_DIR)/bin/activate"

# Pre-commit Hooks
.PHONY: setup-pre-commit
setup-pre-commit: ## Install and setup pre-commit hooks
	@echo "Setting up pre-commit hooks..."
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) -m pre_commit install; \
		$(VENV_PYTHON) -m pre_commit install --hook-type commit-msg; \
		echo "Pre-commit hooks installed successfully!"; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

.PHONY: pre-commit-run
pre-commit-run: ## Run pre-commit hooks on all files
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) -m pre_commit run --all-files; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

.PHONY: pre-commit-update
pre-commit-update: ## Update pre-commit hooks to latest versions
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) -m pre_commit autoupdate; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Linting and Formatting
.PHONY: lint
lint: ## Run all linting checks
	@echo "Running linting checks..."
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) -m flake8 . || true; \
		$(VENV_PYTHON) -m mypy . || true; \
		$(VENV_PYTHON) -m bandit -r . -f json -o bandit-report.json || true; \
		$(VENV_PYTHON) -m pydocstyle . || true; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

.PHONY: format
format: ## Format code with black and isort
	@echo "Formatting code..."
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables *.py; \
		$(VENV_PYTHON) -m isort .; \
		$(VENV_PYTHON) -m black .; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

.PHONY: format-check
format-check: ## Check if code is properly formatted
	@echo "Checking code formatting..."
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) -m black --check .; \
		$(VENV_PYTHON) -m isort --check-only .; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Testing
.PHONY: test
test: ## Run tests
	@echo "Running tests..."
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) test_hierarchy.py; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@echo "Running tests with verbose output..."
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) -v test_hierarchy.py; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Application
.PHONY: run
run: ## Run the Flask application
	@echo "Starting Flask application..."
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) app.py; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

.PHONY: run-dev
run-dev: ## Run the Flask application in development mode
	@echo "Starting Flask application in development mode..."
	@if [ -d "$(VENV_DIR)" ]; then \
		FLASK_ENV=development $(VENV_PYTHON) app.py; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Cleanup
.PHONY: clean
clean: ## Clean up temporary files and caches
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -f bandit-report.json
	rm -f test_hierarchy.db
	@echo "Cleanup complete!"

.PHONY: clean-venv
clean-venv: clean ## Remove virtual environment and clean up
	@echo "Removing virtual environment..."
	rm -rf $(VENV_DIR)
	@echo "Virtual environment removed!"

# Git hooks
.PHONY: install-hooks
install-hooks: setup-pre-commit ## Alias for setup-pre-commit

.PHONY: check-all
check-all: format-check lint test ## Run all checks (format, lint, test)

# Development workflow
.PHONY: dev-install
dev-install: setup ## Complete development setup (alias for setup)

.PHONY: ci
ci: format-check lint test ## Run CI pipeline checks