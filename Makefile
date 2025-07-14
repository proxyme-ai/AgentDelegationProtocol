# Agent Delegation Protocol - Development Makefile

.PHONY: help install test lint format clean dev build docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run all tests"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code"
	@echo "  clean       - Clean build artifacts"
	@echo "  dev         - Start development servers"
	@echo "  build       - Build frontend"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-run  - Run with Docker Compose"

# Install dependencies
install:
	pip install -r requirements.txt
	cd frontend && npm install

# Run all tests
test:
	pytest -v --cov=. --cov-report=html
	cd frontend && npm test
	cd frontend && npm run test:e2e

# Run linting
lint:
	black --check .
	flake8 .
	bandit -r . -f json -o bandit-report.json
	cd frontend && npm run lint

# Format code
format:
	black .
	cd frontend && npm run format

# Clean build artifacts
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf bandit-report.json
	rm -rf *.log
	cd frontend && rm -rf node_modules/.cache
	cd frontend && rm -rf dist/

# Start development servers
dev:
	./run_local.sh

# Build frontend
build:
	cd frontend && npm run build

# Build Docker images
docker-build:
	docker build -t agent-delegation-protocol .
	cd frontend && docker build -t agent-delegation-frontend .

# Run with Docker Compose
docker-run:
	docker-compose up --build

# Security check
security:
	safety check
	bandit -r . -f json -o bandit-report.json

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install black flake8 mypy bandit safety pytest-cov
	cd frontend && npm install

# Run quick tests (unit tests only)
test-quick:
	pytest tests/ -v --ignore=tests/test_performance.py

# Run performance tests
test-performance:
	pytest tests/test_performance.py -v -s

# Generate documentation
docs:
	@echo "Generating documentation..."
	@echo "API documentation available in README.md"
	@echo "Security documentation in SECURITY.md"
	@echo "Contributing guidelines in CONTRIBUTING.md"