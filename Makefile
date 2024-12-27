# Makefile

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make run-dev     - Run the app in development mode"
	@echo "  make run-prod    - Run the app in production mode"

# Variables
FLASK_ENV = development
PORT = 8000

# Development environment
run-dev:
	flask run --debug --port $(PORT)

# Production environment
run-prod:
	flask run --port $(PORT)
