.PHONY: help install install-dev test test-cov lint format clean build run

# Default target
help:
	@echo "PromptyDumpty - Universal Package Manager for AI Agent Artifacts"
	@echo ""
	@echo "Available targets:"
	@echo "  make install      - Install package in production mode"
	@echo "  make install-dev  - Install package in development mode with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run linters (ruff and black check)"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Remove build artifacts and cache"
	@echo "  make build        - Build distribution packages"
	@echo "  make run          - Run dumpty CLI (use ARGS='your arguments')"
	@echo ""
	@echo "Examples:"
	@echo "  make run ARGS='--version'"
	@echo "  make run ARGS='init --agent copilot'"
	@echo "  make run ARGS='list'"

# Install package in production mode
install:
	pip install .

# Install package in development mode with dev dependencies
install-dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=dumpty --cov-report=term-missing --cov-report=html

# Run linters
lint:
	@echo "Running ruff..."
	ruff check dumpty/ tests/
	@echo "Checking code formatting with black..."
	black --check dumpty/ tests/

# Format code
format:
	black dumpty/ tests/

# Clean build artifacts and cache
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Build distribution packages
build: clean
	python -m build

# Run dumpty CLI
# Usage: make run ARGS='--version'
# Usage: make run ARGS='init --agent copilot'
run:
	dumpty $(ARGS)
