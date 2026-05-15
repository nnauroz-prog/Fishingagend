#!/usr/bin/env bash
# Einmalige Einrichtung — wird nach dem ersten Build des Codespace ausgefuehrt.
set -e

echo "→ Backend-Abhängigkeiten installieren ..."
pip install --user --upgrade pip
pip install --user -r backend/requirements.txt

echo "→ Frontend-Abhängigkeiten installieren ..."
cd frontend && npm install --no-audit --no-fund && cd ..

echo "→ Datenbank-Schema migrieren ..."
mkdir -p backend/data
cd backend && alembic upgrade head && cd ..

# Standard-.env nur anlegen, wenn keine vorhanden — dann lauft die App mit Mock-LLM.
if [ ! -f .env ]; then
  cp .env.example .env
  echo "→ .env aus .env.example angelegt (kein API-Key, Mock-LLM aktiv)"
fi

echo "✓ Setup fertig. Beim nächsten 'postStartCommand' fährt alles automatisch hoch."
