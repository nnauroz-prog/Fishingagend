"""FastAPI-Hauptanwendung."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    agenten,
    audit,
    auth,
    backup,
    berichte,
    chat,
    graphrag,
    simulation,
    vorlagen,
    zustand,
)
from app.api import einstellungen as einstellungen_api
from app.config import einstellungen
from app.datenbank import initialisiere_datenbank
from app.dienste.auth_dienst import sorge_fuer_admin
from app.dienste.demo_dienst import saee_demo_daten
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)


@asynccontextmanager
async def lebenszyklus(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("starte_anwendung", modell=einstellungen.anthropic_modell)
    await initialisiere_datenbank()
    if einstellungen.demo_daten_einspielen:
        anzahl = await saee_demo_daten()
        if anzahl:
            logger.info("demo_daten_aktiv", neue_agenten=anzahl)
    await sorge_fuer_admin()
    yield
    logger.info("beende_anwendung")


app = FastAPI(
    title="Fishingagend API",
    description="Multi-Agenten-KI-Vorhersage-Engine",
    version="0.1.0",
    lifespan=lebenszyklus,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=einstellungen.cors_liste,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zustand.router, prefix="/api", tags=["Zustand"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(agenten.router, prefix="/api/agenten", tags=["Agenten"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(berichte.router, prefix="/api/berichte", tags=["Berichte"])
app.include_router(graphrag.router, prefix="/api/graphrag", tags=["GraphRAG"])
app.include_router(einstellungen_api.router, prefix="/api/einstellungen", tags=["Einstellungen"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(vorlagen.router, prefix="/api/vorlagen", tags=["Vorlagen"])
app.include_router(backup.router, prefix="/api/backup", tags=["Backup"])


# --- Statisches Frontend ausliefern (wenn vorhanden) ---
# Im Production-Container packen wir das Frontend-Bundle nach /app/statisch und
# servieren es von derselben Origin. Asset-Pfade werden direkt gemountet, die
# Wurzel und SPA-Routen liefern index.html.
_statisch = Path(os.getenv("STATISCH_PFAD", "")).resolve() if os.getenv("STATISCH_PFAD") else None

if _statisch and _statisch.exists():
    _assets = _statisch / "assets"
    if _assets.exists():
        app.mount("/assets", StaticFiles(directory=_assets), name="assets")

    for datei in ("favicon.svg", "favicon.ico"):
        _pfad = _statisch / datei
        if _pfad.exists():
            app.add_api_route(
                f"/{datei}",
                lambda p=_pfad: FileResponse(p),  # type: ignore[misc]
                include_in_schema=False,
            )

    @app.get("/", include_in_schema=False)
    async def wurzel() -> FileResponse:
        return FileResponse(_statisch / "index.html")

    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):
        antwort = await call_next(request)
        if antwort.status_code != 404:
            return antwort
        pfad = request.url.path
        if pfad.startswith(("/api/", "/docs", "/openapi.json", "/redoc", "/assets/")):
            return antwort
        return FileResponse(_statisch / "index.html")

else:

    @app.get("/")
    async def wurzel_json() -> dict[str, str]:
        return {
            "name": "Fishingagend",
            "version": "0.1.0",
            "dokumentation": "/docs",
        }


@app.exception_handler(404)
async def _nicht_gefunden(request: Request, _exc) -> JSONResponse:
    return JSONResponse({"detail": "Nicht gefunden", "pfad": request.url.path}, status_code=404)
