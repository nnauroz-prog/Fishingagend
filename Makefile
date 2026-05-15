.PHONY: install backend-install frontend-install dev backend-dev frontend-dev \
        test backend-test frontend-test lint backend-lint frontend-lint \
        build prod migrate db-upgrade db-revision clean

install: backend-install frontend-install

backend-install:
	cd backend && pip install -r requirements.txt && pip install -e ".[dev]"

frontend-install:
	cd frontend && npm install --no-audit --no-fund

# --- Entwicklung ---
dev:
	@echo "Starte backend (uvicorn) und frontend (vite) parallel ..."
	@trap 'kill 0' INT; \
	  (cd backend && python run.py) & \
	  (cd frontend && npm run dev) & \
	  wait

backend-dev:
	cd backend && python run.py

frontend-dev:
	cd frontend && npm run dev

# --- Tests ---
test: backend-test frontend-test

backend-test:
	cd backend && python -m pytest

frontend-test:
	cd frontend && npm test

# --- Lint ---
lint: backend-lint frontend-lint

backend-lint:
	cd backend && ruff check .

frontend-lint:
	cd frontend && npm run typecheck

# --- Build ---
build:
	cd frontend && npm run build

# --- Datenbank ---
db-upgrade:
	cd backend && alembic upgrade head

db-revision:
	cd backend && alembic revision --autogenerate -m "$(NAME)"

migrate: db-upgrade

# --- Production ---
prod:
	docker compose -f docker-compose.prod.yml up --build -d

# --- Aufräumen ---
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/data/*.db backend/data/*.sqlite
	rm -rf frontend/dist frontend/.vite
