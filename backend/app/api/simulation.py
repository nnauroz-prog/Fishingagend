"""Simulations-Endpunkte."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.dienste.simulation_dienst import SimulationDienst, hole_simulation_dienst
from app.modelle.simulation import Simulation, SimulationErstellen

router = APIRouter()


@router.get("", response_model=list[Simulation])
async def liste(dienst: SimulationDienst = Depends(hole_simulation_dienst)) -> list[Simulation]:
    return await dienst.liste()


@router.post("", response_model=Simulation, status_code=status.HTTP_201_CREATED)
async def plane(
    eingabe: SimulationErstellen,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> Simulation:
    return await dienst.plane(eingabe)


@router.get("/{sim_id}", response_model=Simulation)
async def hole(
    sim_id: str,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> Simulation:
    sim = await dienst.hole(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    return sim


@router.post("/{sim_id}/starte", response_model=Simulation)
async def starte(
    sim_id: str,
    hintergrund: BackgroundTasks,
    sofort: bool = False,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> Simulation:
    """Startet eine Simulation.

    `sofort=true`: läuft synchron — gut für kleine Tests.
    Sonst: läuft im Hintergrund, der Endpunkt antwortet sofort.
    """
    sim = await dienst.hole(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    if sofort:
        sim = await dienst.starte(sim_id)
        if sim is None:
            raise HTTPException(status_code=404, detail="Simulation verschwunden")
        return sim
    hintergrund.add_task(dienst.starte, sim_id)
    return sim
