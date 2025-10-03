.PHONY: help setup dev build up down logs clean test migrate

help:
	@echo "StudyMaster - Available Commands"
	@echo "=================================="
	@echo "setup      - Initial project setup"
	@echo "dev        - Start development environment"
	@echo "build      - Build all containers"
	@echo "up         - Start all services"
	@echo "down       - Stop all services"
	@echo "logs       - View logs"
	@echo "clean      - Clean containers and volumes"
	@echo "test       - Run tests"
	@echo "migrate    - Run database migrations"
	@echo "lint       - Run linters"

setup:
	@echo "Setting up StudyMaster..."
	cp .env.example .env
	@echo "Please edit .env with your configuration"
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
	@echo "Setup complete! Run 'make dev' to start"

dev:
	docker-compose up -d postgres redis minio
	@echo "Waiting for services to be ready..."
	sleep 5
	cd backend && . venv/bin/activate && alembic upgrade head
	@echo "Starting backend..."
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm run dev

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Backend: http://localhost:8000, Frontend: http://localhost:3000"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist

test:
	cd backend && . venv/bin/activate && pytest -v
	cd frontend && npm run test

migrate:
	cd backend && . venv/bin/activate && alembic upgrade head

lint:
	cd backend && . venv/bin/activate && ruff check . && mypy .
	cd frontend && npm run lint
