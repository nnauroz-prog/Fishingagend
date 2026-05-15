"""Sim-Vorlagen-Endpunkte."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dienste.agent_dienst import AgentDienst, hole_agent_dienst
from app.dienste.simulation_dienst import SimulationDienst, hole_simulation_dienst
from app.dienste.vorlagen_dienst import hole_vorlage, liste_vorlagen
from app.modelle.agent import AgentErstellen
from app.modelle.simulation import Simulation, SimulationErstellen

router = APIRouter()


@router.get("")
async def liste() -> list[dict]:
    return liste_vorlagen()


class VorlageStartAnfrage(BaseModel):
    name: str | None = None
    sofort_starten: bool = False


@router.post("/{schluessel}/anwenden", response_model=Simulation)
async def anwenden(
    schluessel: str,
    anfrage: VorlageStartAnfrage,
    agent_dienst: AgentDienst = Depends(hole_agent_dienst),
    sim_dienst: SimulationDienst = Depends(hole_simulation_dienst),
) -> Simulation:
    """Legt die Personas der Vorlage als Agenten an (falls noch nicht da)
    und erzeugt daraus eine geplante Simulation."""
    vorlage = hole_vorlage(schluessel)
    if vorlage is None:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")

    # Bestehende Agenten holen, um Doppelte zu vermeiden
    vorhandene = await agent_dienst.liste()
    namen_zu_id = {a.persona.name: a.id for a in vorhandene}

    agent_ids: list[str] = []
    for persona in vorlage.personas:
        if persona.name in namen_zu_id:
            agent_ids.append(namen_zu_id[persona.name])
        else:
            neu = await agent_dienst.erstelle(AgentErstellen(persona=persona))
            agent_ids.append(neu.id)

    sim = await sim_dienst.plane(
        SimulationErstellen(
            name=anfrage.name or vorlage.titel,
            beschreibung=vorlage.beschreibung,
            agent_ids=agent_ids,
            schritte=vorlage.schritte,
            variable=vorlage.variable,
            dual_modus=vorlage.dual_modus,
            plattform_modus=vorlage.plattform_modus,
        )
    )

    if anfrage.sofort_starten:
        gestartet = await sim_dienst.starte(sim.id)
        if gestartet:
            return gestartet
    return sim
