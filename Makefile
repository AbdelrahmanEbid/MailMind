# MailMind - Makefile for development tasks
# Based on LangGraph template patterns

.PHONY: help install install-dev clean lint format typecheck test test-unit test-integration test-coverage dev docs build

# Default target
help:
	@echo "MailMind Development Commands"
	@echo "============================"
	@echo ""
	@echo "Setup:"
	@echo "  install         Install production dependencies"
	@echo "  install-dev     Install development dependencies"
	@echo "  clean          Clean build artifacts and cache"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code with black and isort"
	@echo "  typecheck      Run type checking with mypy"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo ""
	@echo "Development:"
	@echo "  dev            Start development server"
	@echo "  docs           Build documentation"
	@echo "  build          Build package"
	@echo ""

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install "langgraph-cli[inmem]"

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Code quality
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/
	isort src/ tests/

typecheck:
	mypy src/mailmind/

# Testing
test:
	pytest

test-unit:
	pytest tests/unit_tests/ -m "not integration"

test-integration:
	pytest tests/integration_tests/ -m integration

test-coverage:
	pytest --cov=src/mailmind --cov-report=html --cov-report=term-missing

test-performance:
	pytest tests/ -m performance

# Development
dev:
	langgraph dev

dev-uv:
	uvx --from "langgraph-cli[inmem]" --with-editable . langgraph dev

# Documentation
docs:
	mkdocs build

docs-serve:
	mkdocs serve

# Build
build:
	python -m build

# Docker targets (if using Docker)
# Database migrations (if using database)
# Monitoring and profiling
# Security
# Release targets
# Environment setup
# LangGraph specific
# Monitoring
# Backup and restore (if using database)
# Performance benchmarking
