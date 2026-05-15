# Fishingagend

> KI-Vorhersage-Engine auf Basis einer Multi-Agenten-Architektur — eine deutschsprachige, modernisierte Neufassung von [MiroFish](https://github.com/666ghj/MiroFish).

Fishingagend extrahiert Saat-Informationen aus der realen Welt und konstruiert eine digitale Parallelwelt mit hunderten von intelligenten Agenten. Jeder Agent besitzt eine eigenständige Persönlichkeit, ein Langzeitgedächtnis und entwickelt sich in einer sozialen Simulation weiter. Über das Einspeisen von Variablen lassen sich zukünftige Verläufe ableiten.

![Backend tests](https://img.shields.io/badge/backend%20tests-17%2F17%20%E2%9C%93-success)
![Frontend tests](https://img.shields.io/badge/frontend%20tests-12%2F12%20%E2%9C%93-success)

## Architektur

| Schicht       | Stack                                                              |
|---------------|--------------------------------------------------------------------|
| Backend       | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2 (Async), Alembic, `uv` |
| Frontend      | Vue 3, Vite, TypeScript, Tailwind CSS + Typography, Pinia, Vue Router, Vue I18n, marked |
| LLM           | Anthropic Claude (`claude-opus-4-7`) — mit Prompt-Caching und Streaming |
| Persistenz    | SQLite (Standard), tauschbar gegen PostgreSQL via `DATENBANK_URL`  |
| Container     | Docker, Docker Compose (Dev + Prod mit Nginx)                      |
| CI            | GitHub Actions (Ruff, pytest, Vitest, Build)                       |

## Schnellstart

### Voraussetzungen

- Python 3.11 oder 3.12
- Node.js 18 oder neuer
- Optional: Anthropic-API-Key (`ANTHROPIC_API_KEY`) — ohne Key startet ein Mock-LLM, alle Pfade bleiben funktionsfähig.

### Mit Docker Compose (Entwicklung)

```bash
cp .env.example .env       # ANTHROPIC_API_KEY eintragen, optional
docker compose up --build
```

- Frontend: <http://localhost:5173>
- Backend + OpenAPI-Doku: <http://localhost:8000/docs>

### Mit Docker Compose (Produktion)

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Frontend wird als statisches Bündel von Nginx ausgeliefert (Port 80, mit SPA-Fallback, Asset-Caching, Sicherheitsheadern).

### Lokal — mit Makefile

```bash
make install      # Backend + Frontend Abhängigkeiten
make migrate      # Alembic-Migration ausführen
make dev          # backend (8000) + frontend (5173) parallel
make test         # alle Tests
make lint         # Ruff + Vue-TSC
make build        # Frontend-Production-Build
```

### Lokal — ohne Makefile

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
python run.py

# Frontend (zweites Terminal)
cd frontend
npm install
npm run dev
```

## Projektstruktur

```
.
├── backend/
│   ├── alembic/             Migrationen (Initial-Schema vorhanden)
│   ├── app/
│   │   ├── api/             REST-Endpunkte (agenten, chat, simulation, berichte, graphrag, zustand)
│   │   ├── modelle/         Pydantic-Modelle
│   │   ├── dienste/         Geschäftslogik (LLM, Persona, GraphRAG, Simulation, Bericht, Gedächtnis)
│   │   ├── werkzeuge/       Hilfsfunktionen (logger)
│   │   ├── datenbank.py     SQLAlchemy-Setup
│   │   ├── config.py        Pydantic-Settings
│   │   └── main.py          FastAPI-Anwendung
│   ├── scripts/             Beispiel-Skripte
│   ├── tests/               pytest-Suite (17 Tests)
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/             axios-Clients + SSE-Stream
│   │   ├── components/      AgentKarte, ChatNachricht, SimulationsAnzeige, ToastSchicht, Navigationsleiste
│   │   ├── views/           Startseite, Agenten, AgentDetail, Chat, Simulation, SimulationDetail, GraphRAG, Berichte, NichtGefunden
│   │   ├── store/           Pinia-Stores (agenten, simulation, toasts)
│   │   ├── router/
│   │   ├── i18n/            Lokalisierung (de, en)
│   │   └── werkzeuge/       (markdown)
│   ├── tests/               Vitest-Suite (12 Tests)
│   ├── Dockerfile           (Dev — Vite-Server)
│   ├── Dockerfile.prod      (Prod — Multi-Stage + Nginx)
│   └── nginx.conf
├── locales/                 Backend-Lokalisierungen
├── docker-compose.yml       Entwicklung
├── docker-compose.prod.yml  Produktion (Nginx + restart-Politik)
├── Makefile
└── .github/workflows/ci.yml CI-Pipeline
```

## Module

### GraphRAG-Aufbau und Entitäts-Extraktion
Texte werden in Chunks zerlegt; pro Chunk extrahiert das LLM Entitäten (Person, Organisation, Ort, Konzept, Ereignis) und Beziehungen, die anschließend dedupliziert in einem Wissensgraphen landen. Befragbar via natürlicher Sprache. UI: `/graphrag`.

### Persona-Generierung
Aus Saat-Stichworten erzeugt das LLM eine vollständige Persona — Name, Alter, Beruf, Hintergrund, Werte, Charakterzüge, Sprachstil. Robustes JSON-Parsing toleriert Markdown-Fences. Im Mock-Modus wird ein Default zurückgegeben.

### Dual-Welt-Simulation
Zwei Welten laufen parallel: Kontroll-Welt ohne externe Variable, Varianten-Welt mit. Pro Schritt entscheidet jeder Agent (LLM-Aufruf) seine nächste Aktion auf Basis des bisherigen Verlaufs. Läuft im Hintergrund (`POST /api/simulation/{id}/starte` antwortet sofort, das Frontend pollt alle 2 s den Status auf der Detail-Seite). Mit `?sofort=true` läuft sie synchron.

### Berichts-Agent
Aggregiert Schritte, schickt sie als Anweisung an das LLM und erhält einen Markdown-Bericht mit Zusammenfassung, Beobachtungen je Welt, Schlüsselereignissen und Empfehlung. Frontend rendert das Markdown via `marked` mit Tailwind-Typography.

### Chat (mit Streaming)
Direktes Gespräch mit einem simulierten Agenten — Antwort kommt zeichenweise via Server-Sent Events. Persona-Block ist Prompt-gecached; Langzeit-Gedächtnis steht in der DB und wird in den System-Prompt eingespeist.

### Persistenz
SQLAlchemy mit Async-SQLite; PostgreSQL via `DATENBANK_URL` umstellbar. Schema-Verwaltung über Alembic — `alembic upgrade head` oder `make migrate`.

### Mock-LLM für Entwicklung & Tests
Ohne `ANTHROPIC_API_KEY` startet die App mit einem deterministischen Mock-LLM. Tests injizieren ihren eigenen Mock und prüfen sowohl die Ausgabe als auch den exakt gesendeten Prompt — die App ist damit ohne API-Key komplett benutzbar.

## API-Übersicht

| Methode | Pfad                              | Beschreibung                                |
|---------|-----------------------------------|---------------------------------------------|
| GET     | `/api/zustand`                    | Health-Check                                |
| GET     | `/api/agenten`                    | Liste aller Agenten                         |
| POST    | `/api/agenten`                    | Agent anlegen                               |
| GET     | `/api/agenten/{id}`               | Agent abrufen                               |
| DELETE  | `/api/agenten/{id}`               | Agent löschen                               |
| POST    | `/api/agenten/aus-saat`           | Persona-Vorschlag via LLM                   |
| POST    | `/api/chat`                       | Chat (Antwort als JSON)                     |
| POST    | `/api/chat/strom`                 | Chat (SSE-Streaming)                        |
| GET     | `/api/simulation`                 | Simulationen auflisten                      |
| POST    | `/api/simulation`                 | Simulation planen                           |
| GET     | `/api/simulation/{id}`            | Simulation samt Verlauf                     |
| POST    | `/api/simulation/{id}/starte`     | Starten (Hintergrund; `?sofort=true` synchron) |
| GET     | `/api/berichte/{id}`              | Markdown-Bericht                            |
| POST    | `/api/graphrag/extrahieren`       | Entitäten + Beziehungen extrahieren         |
| POST    | `/api/graphrag/abfrage`           | Wissensgraph befragen                       |

Vollständige OpenAPI-Doku unter `/docs`.

## Lizenz

AGPL-3.0 — wie das ursprüngliche Projekt.
