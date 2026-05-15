"""Berichts-Endpunkte."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dienste.bericht_dienst import BerichtDienst
from app.dienste.simulation_dienst import SimulationDienst, hole_simulation_dienst

router = APIRouter()


def hole_bericht_dienst() -> BerichtDienst:
    return BerichtDienst()


@router.get("/{sim_id}")
async def bericht(
    sim_id: str,
    sim_dienst: SimulationDienst = Depends(hole_simulation_dienst),
    bericht_dienst: BerichtDienst = Depends(hole_bericht_dienst),
) -> dict[str, str]:
    sim = await sim_dienst.hole(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    inhalt = await bericht_dienst.erstelle_bericht(sim)
    return {"simulation_id": sim_id, "markdown": inhalt}
