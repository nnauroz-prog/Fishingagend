"""FastAPI-Hauptanwendung."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agenten, berichte, chat, graphrag, simulation, zustand
from app.config import einstellungen
from app.datenbank import initialisiere_datenbank
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)


@asynccontextmanager
async def lebenszyklus(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("starte_anwendung", modell=einstellungen.anthropic_modell)
    await initialisiere_datenbank()
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
app.include_router(agenten.router, prefix="/api/agenten", tags=["Agenten"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(berichte.router, prefix="/api/berichte", tags=["Berichte"])
app.include_router(graphrag.router, prefix="/api/graphrag", tags=["GraphRAG"])


@app.get("/")
async def wurzel() -> dict[str, str]:
    return {
        "name": "Fishingagend",
        "version": "0.1.0",
        "dokumentation": "/docs",
    }
