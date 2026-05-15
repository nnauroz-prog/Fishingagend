"""Simulations-Endpunkte."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket, status
from pydantic import BaseModel, Field

from app.dienste.agent_dienst import hole_agent_dienst
from app.dienste.ereignis_bus import hole_ereignis_bus
from app.dienste.llm_dienst import hole_llm_dienst
from app.dienste.plattform_dienst import PlattformDienst, hole_plattform_dienst
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


class BatchAnfrage(BaseModel):
    """Eine Vorlage + mehrere Variablen-Wert-Kombinationen.

    Erzeugt n Simulationen mit identischer Vorlage, aber unterschiedlicher
    `variable`. Praktisch fuer Sensitivitaets-Analysen.
    """

    vorlage: SimulationErstellen
    variablen_serie: list[dict] = Field(min_length=1, max_length=20)
    sofort_starten: bool = False


@router.post("/batch", response_model=list[Simulation])
async def batch(
    anfrage: BatchAnfrage,
    hintergrund: BackgroundTasks,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> list[Simulation]:
    """Legt fuer jede Variable in `variablen_serie` eine Sim an."""
    angelegt: list[Simulation] = []
    for i, variable in enumerate(anfrage.variablen_serie):
        eingabe = anfrage.vorlage.model_copy(
            update={
                "name": f"{anfrage.vorlage.name} #{i + 1}",
                "variable": variable,
            }
        )
        sim = await dienst.plane(eingabe)
        angelegt.append(sim)
        if anfrage.sofort_starten:
            hintergrund.add_task(dienst.starte, sim.id)
    return angelegt



class AusTextAnfrage(BaseModel):
    beschreibung: str = Field(min_length=10, max_length=2000)


_ANALYSE_SYSTEM = """Du parsest eine natuerlichsprachige Sim-Anforderung.
Waehle aus den verfuegbaren Agenten passende Teilnehmer und schlage eine
Konfiguration vor. Antworte als JSON:

{
  "name": "Kurzer aussagekraeftiger Titel",
  "beschreibung": "1-2 Saetze",
  "schritte": 3-30,
  "variable": {"feld": "wert"},
  "dual_modus": true,
  "plattform_modus": false,
  "agent_namen": ["Name 1", "Name 2"]
}

Waehle nur Namen aus der gegebenen Liste."""


@router.post("/aus-text", response_model=SimulationErstellen)
async def aus_text(anfrage: AusTextAnfrage) -> SimulationErstellen:
    """Schlaegt aus einer freien Beschreibung eine Sim-Konfiguration vor."""
    agenten = await hole_agent_dienst().liste()
    namen_index = {a.persona.name: a.id for a in agenten}
    katalog = "\n".join(
        f"- {a.persona.name} ({a.persona.beruf or '—'})" for a in agenten[:30]
    ) or "(keine Agenten — bitte zuerst welche anlegen)"

    anweisung = (
        f"Verfuegbare Agenten:\n{katalog}\n\nAnforderung:\n{anfrage.beschreibung}"
    )
    roh = await hole_llm_dienst().antworte_json(_ANALYSE_SYSTEM, anweisung)

    namen = [n for n in roh.get("agent_namen", []) if n in namen_index]
    if not namen:
        namen = list(namen_index.keys())[:5]
    ids = [namen_index[n] for n in namen]
    if not ids:
        raise HTTPException(
            status_code=400,
            detail="Keine Agenten verfuegbar — bitte zuerst Agenten anlegen.",
        )

    return SimulationErstellen(
        name=str(roh.get("name") or "Auto-Simulation")[:200],
        beschreibung=str(roh.get("beschreibung") or anfrage.beschreibung)[:500],
        agent_ids=ids,
        schritte=int(roh.get("schritte") or 5),
        variable=dict(roh.get("variable") or {}),
        dual_modus=bool(roh.get("dual_modus", True)),
        plattform_modus=bool(roh.get("plattform_modus", False)),
    )


@router.get("/{sim_id}", response_model=Simulation)
async def hole(
    sim_id: str,
    dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> Simulation:
    sim = await dienst.hole(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    return sim


@router.get("/{sim_id}/feed")
async def feed(
    sim_id: str,
    welt: str | None = None,
    plattform: PlattformDienst = Depends(hole_plattform_dienst),
) -> list[dict]:
    """Plattform-Feed (Posts + Reaktionen) einer Simulation."""
    return await plattform.feed(sim_id, welt=welt)


@router.get("/{sim_id}/folgen")
async def folgen(
    sim_id: str,
    welt: str | None = None,
    plattform: PlattformDienst = Depends(hole_plattform_dienst),
) -> list[dict]:
    """Folge-Beziehungen, die in der Simulation entstanden sind."""
    return await plattform.folgen(sim_id, welt=welt)


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
