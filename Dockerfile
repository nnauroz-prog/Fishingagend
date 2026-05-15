# --- Stufe 1: Frontend-Build ---
FROM node:20-alpine AS frontend-bauer
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
# Leere Basis-URL -> Frontend nutzt relative /api/-Pfade, also denselben Host.
ENV VITE_API_BASIS=""
RUN npm run build

# --- Stufe 2: Backend + ausgelieferte statische Dateien ---
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STATISCH_PFAD=/app/statisch

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY backend/ ./
COPY --from=frontend-bauer /app/dist ./statisch

RUN mkdir -p /app/data

ENV BACKEND_HOST=0.0.0.0 \
    CORS_URSPRUENGE="*" \
    ENTWICKLUNG=false \
    DEMO_DATEN_EINSPIELEN=true

EXPOSE 8000

# Render setzt $PORT — wir respektieren das, Default 8000.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
