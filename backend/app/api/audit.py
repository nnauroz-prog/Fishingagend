"""Audit-Log-Endpunkt."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.dienste.audit_dienst import lese

router = APIRouter()


@router.get("")
async def liste(
    limit: int = Query(default=100, ge=1, le=500),
    ressource: str | None = None,
) -> list[dict]:
    """Letzte Audit-Eintraege, optional auf eine Ressource gefiltert."""
    return await lese(limit=limit, ressource=ressource)
