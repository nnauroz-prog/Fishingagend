"""Health-Check, Versions- und Statistik-Endpunkte."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app import __version__
from app.datenbank import (
    AgentZeile,
    BeziehungZeile,
    EntitaetZeile,
    SimulationZeile,
    session_factory,
)

router = APIRouter()


@router.get("/zustand")
async def zustand() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@router.get("/statistiken")
async def statistiken() -> dict[str, int | dict[str, int]]:
    """Aggregierte Zaehler fuer das Dashboard."""
    async with session_factory()() as session:
        agenten = (await session.scalar(select(func.count(AgentZeile.id)))) or 0
        sims = (await session.scalar(select(func.count(SimulationZeile.id)))) or 0
        ents = (await session.scalar(select(func.count(EntitaetZeile.id)))) or 0
        bzs = (await session.scalar(select(func.count(BeziehungZeile.id)))) or 0

        nach_status: dict[str, int] = {}
        rows = await session.execute(
            select(SimulationZeile.status, func.count(SimulationZeile.id)).group_by(
                SimulationZeile.status
            )
        )
        for status, anzahl in rows.all():
            nach_status[status] = anzahl

    return {
        "agenten": agenten,
        "simulationen": sims,
        "entitaeten": ents,
        "beziehungen": bzs,
        "simulationen_nach_status": nach_status,
    }
