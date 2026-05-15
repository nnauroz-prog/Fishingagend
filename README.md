# Fishingagend

> KI-Vorhersage-Engine auf Basis einer Multi-Agenten-Architektur — eine deutschsprachige, modernisierte Neufassung von [MiroFish](https://github.com/666ghj/MiroFish).

Fishingagend extrahiert Saat-Informationen aus der realen Welt und konstruiert eine digitale Parallelwelt mit hunderten von intelligenten Agenten. Jeder Agent besitzt eine eigenständige Persönlichkeit, ein Langzeitgedächtnis und entwickelt sich in einer sozialen Simulation weiter. Über das Einspeisen von Variablen lassen sich zukünftige Verläufe ableiten.

## Architektur

| Schicht       | Stack                                                            |
|---------------|------------------------------------------------------------------|
| Backend       | Python 3.11+, FastAPI, Pydantic v2, `uv`                         |
| Frontend      | Vue 3, Vite, TypeScript, Tailwind CSS, Pinia, Vue Router, Vue I18n |
| LLM           | Anthropic Claude (`claude-opus-4-7`) via offizielles SDK         |
| Persistenz    | SQLite (Standard), tauschbar gegen PostgreSQL                    |
| Container     | Docker, Docker Compose                                           |
| CI            | GitHub Actions (Ruff, pytest, Vitest, Build)                     |

## Schnellstart

### Voraussetzungen

- Python 3.11 oder 3.12
- Node.js 18 oder neuer
- Ein Anthropic-API-Key (`ANTHROPIC_API_KEY`)

### Mit Docker Compose

```bash
cp .env.example .env
# ANTHROPIC_API_KEY in .env eintragen
docker compose up --build
```

Frontend: <http://localhost:5173>, Backend: <http://localhost:8000/docs>

### Lokal

```bash
# Backend
cd backend
uv sync           # oder: pip install -e .
uv run python run.py

# Frontend (in zweitem Terminal)
cd frontend
npm install
npm run dev
```

## Projektstruktur

```
.
├── backend/              FastAPI-Anwendung mit Multi-Agenten-Logik
│   ├── app/
│   │   ├── api/          REST-Endpunkte
│   │   ├── modelle/      Pydantic-Modelle (Agenten, Personas, Simulation)
│   │   ├── dienste/      Geschäftslogik (LLM, GraphRAG, Gedächtnis)
│   │   └── werkzeuge/    Hilfsfunktionen
│   └── tests/            pytest-Suite
├── frontend/             Vue-3-Single-Page-Anwendung
│   └── src/
│       ├── api/          HTTP-Clients
│       ├── components/   wiederverwendbare Komponenten
│       ├── views/        Seiten (Startseite, Agenten, Chat, Simulation, Berichte)
│       ├── store/        Pinia-Stores
│       ├── router/       Vue Router
│       └── i18n/         Übersetzungen (de, en)
├── locales/              gemeinsame Übersetzungen
├── docker-compose.yml
└── .github/workflows/    CI-Pipeline
```

## Module

### GraphRAG-Aufbau und Entitäts-Extraktion
Texte werden in Chunks zerlegt; pro Chunk fragt das LLM nach Entitäten (Person, Organisation, Ort, Konzept, Ereignis) und Beziehungen, die anschließend dedupliziert in einem Wissensgraphen landen. Siehe `backend/app/dienste/graphrag_dienst.py`.

### Persona-Generierung
Aus Saat-Stichworten wird via LLM eine vollständige Persona erzeugt — Name, Alter, Beruf, Hintergrund, Werte, Charakterzüge, Sprachstil. Robustes JSON-Parsing, das auch Markdown-Fences toleriert. Siehe `backend/app/dienste/persona_dienst.py`.

### Dual-Welt-Simulation
Zwei Welten laufen parallel: in der Kontroll-Welt agieren die Agenten ohne externe Variable, in der Varianten-Welt mit. Pro Schritt entscheidet jeder Agent (LLM-Aufruf) seine nächste Aktion auf Basis des bisherigen Verlaufs. Läuft im Hintergrund — der `POST /api/simulation/{id}/starte`-Endpunkt antwortet sofort, das Frontend pollt den Status. Mit `?sofort=true` läuft sie synchron. Siehe `backend/app/dienste/simulation_dienst.py`.

### Berichts-Agent
Aggregiert Schritte, schickt sie als Anweisung an das LLM und erhält einen Markdown-Bericht mit Zusammenfassung, Beobachtungen je Welt, Schlüsselereignissen und Empfehlung. Siehe `backend/app/dienste/bericht_dienst.py`.

### Chat
Direktes Gespräch mit einem simulierten Agenten — inklusive Kontext aus dessen Langzeit-Gedächtnis (in der DB persistiert). Persona-Block ist via Prompt-Caching markiert. Siehe `backend/app/api/chat.py`.

### Persistenz
SQLAlchemy mit Async-SQLite; Tabellen werden beim Start automatisch erstellt. PostgreSQL: einfach `DATENBANK_URL` umstellen.

### Mock-LLM für Entwicklung & Tests
Ohne `ANTHROPIC_API_KEY` startet die App mit einem deterministischen Mock-LLM. Die Tests injizieren ihren eigenen Mock und prüfen sowohl die Ausgabe als auch den exakt gesendeten Prompt — also auch ohne API-Key komplett deckungsgleich.

## Entwicklung

```bash
# Backend-Tests + Lint
cd backend && uv run pytest && uv run ruff check .

# Frontend-Tests + Typcheck + Lint
cd frontend && npm test && npm run typecheck && npm run lint
```

## Verbesserungen gegenüber dem Original

- Vue 3 (Composition API) + Vite + TypeScript statt Vue 2 / Webpack / JS
- FastAPI statt monolithischer Flask-Struktur
- Anthropic-SDK direkt integriert, OpenAI-Kompatibilität bleibt optional
- Tailwind-basiertes UI mit Dark Mode
- Vollständige deutsche Lokalisierung
- Tests + CI ab Tag 1
- Sauber getrennte Schichten (`api/` ↔ `dienste/` ↔ `modelle/`)

## Lizenz

AGPL-3.0 — wie das ursprüngliche Projekt.
