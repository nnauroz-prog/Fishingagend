"""Simulations-Endpunkte."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket, status

from app.dienste.ereignis_bus import hole_ereignis_bus
from app.dienste.simulation_dienst import SimulationDienst, hole_simulation_dienst
from app.modelle.simulation import Simulation, SimulationErstellen

router = APIRouter()


@router.get("", response_model=list[Simulation])
async def liste(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> list[Simulation]:
    alle = await dienst.liste()
    return alle[offset : offset + limit]


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


@router.get("/{sim_id}/export")
async def exportiere(
    sim_id: str,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> dict:
    """Liefert Simulation samt Verlauf als JSON — perfekt zum Archivieren."""
    sim = await dienst.hole(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    return sim.model_dump(mode="json")


@router.post("/{sim_id}/starte", response_model=Simulation)
async def starte(
    sim_id: str,
    hintergrund: BackgroundTasks,
    sofort: bool = False,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> Simulation:
    """Startet eine Simulation.

    `sofort=true`: laeuft synchron — gut fuer kleine Tests.
    Sonst: laeuft im Hintergrund, der Endpunkt antwortet sofort.
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


@router.websocket("/{sim_id}/strom")
async def stroeme(websocket: WebSocket, sim_id: str) -> None:
    """Pusht Schritt- und Status-Ereignisse einer Simulation live."""
    await websocket.accept()
    bus = hole_ereignis_bus()
    async with bus.abonniere(f"sim:{sim_id}") as queue:
        try:
            while True:
                try:
                    ereignis = await asyncio.wait_for(queue.get(), timeout=30)
                    await websocket.send_text(json.dumps(ereignis, ensure_ascii=False))
                except TimeoutError:
                    # Heartbeat fuer Proxies (Nginx schliesst leere Connections)
                    await websocket.send_text(json.dumps({"typ": "ping"}))
        except Exception:
            await websocket.close()
