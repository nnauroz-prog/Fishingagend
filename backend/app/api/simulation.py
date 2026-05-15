"""Simulations-Endpunkte."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.dienste.simulation_dienst import SimulationDienst, hole_simulation_dienst
from app.modelle.simulation import Simulation, SimulationErstellen

router = APIRouter()


@router.get("", response_model=list[Simulation])
async def liste(dienst: SimulationDienst = Depends(hole_simulation_dienst)) -> list[Simulation]:
    return dienst.liste()


@router.post("", response_model=Simulation, status_code=status.HTTP_201_CREATED)
async def plane(
    eingabe: SimulationErstellen,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> Simulation:
    return dienst.plane(eingabe)


@router.get("/{sim_id}", response_model=Simulation)
async def hole(sim_id: str, dienst: SimulationDienst = Depends(hole_simulation_dienst)) -> Simulation:
    sim = dienst.hole(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    return sim


@router.post("/{sim_id}/starte", response_model=Simulation)
async def starte(
    sim_id: str,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> Simulation:
    sim = await dienst.starte(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    return sim
