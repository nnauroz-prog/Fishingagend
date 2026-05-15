#!/usr/bin/env bash
# Startet Backend und Frontend im Hintergrund — wird bei jedem Codespace-Start
# ausgefuehrt. Die Logs landen in /tmp, damit man bei Bedarf reinschauen kann.
set -e

# Saubere Vorgaenger killen (falls Codespace neu gestartet wurde)
pkill -f "python run.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

cd "$(dirname "$0")/.."

echo "→ Backend startet auf :8000 ..."
(cd backend && nohup python run.py > /tmp/fishingagend-backend.log 2>&1 &)

echo "→ Frontend startet auf :5173 ..."
(cd frontend && nohup npm run dev -- --host 0.0.0.0 > /tmp/fishingagend-frontend.log 2>&1 &)

# Kurz warten, damit beide Prozesse Zeit haben Sockets zu binden,
# bevor Codespaces das Port-Forwarding einrichtet.
sleep 3
echo "✓ Beide Dienste laufen. Frontend öffnet automatisch im Browser."
