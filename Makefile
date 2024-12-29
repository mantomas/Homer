# Makefile

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make run-dev     - Run the app in development mode"
	@echo "  make run-prod    - Run the app in production mode"

# Variables
PORT = 8000

# Development environment
run-dev:
	.venv/bin/flask run --debug --port $(PORT)

# Production environment
run-prod:
	.venv/bin/gunicorn -b localhost:$(PORT) -w 2 garden:app
