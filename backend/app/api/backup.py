"""Backup/Restore-Endpunkte."""

from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException, Query

from app.dienste.backup_dienst import exportiere, importiere

router = APIRouter()


@router.get("/export")
async def export_alles() -> dict:
    """Vollstaendiger DB-Dump als JSON."""
    return await exportiere()


@router.post("/import")
async def import_alles(
    daten: dict = Body(...),
    modus: str = Query(default="anhaengen", pattern="^(anhaengen|ersetzen)$"),
) -> dict[str, int]:
    """Importiert ein Backup. Modus: anhaengen (default) oder ersetzen."""
    try:
        return await importiere(daten, modus=modus)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
