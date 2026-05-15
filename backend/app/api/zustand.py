"""Health-Check und Versions-Endpunkt."""

from __future__ import annotations

from fastapi import APIRouter

from app import __version__

router = APIRouter()


@router.get("/zustand")
async def zustand() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
