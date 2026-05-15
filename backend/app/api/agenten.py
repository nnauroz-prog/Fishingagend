"""Endpunkte zur Verwaltung von Agenten."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.dienste.agent_dienst import AgentDienst, hole_agent_dienst
from app.dienste.persona_dienst import PersonaDienst
from app.modelle.agent import Agent, AgentErstellen
from app.modelle.persona import Persona

router = APIRouter()


class PersonaAusSaat(BaseModel):
    saat: dict[str, str] = Field(default_factory=dict)


@router.get("", response_model=list[Agent])
async def liste_agenten(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    dienst: AgentDienst = Depends(hole_agent_dienst),
) -> list[Agent]:
    alle = await dienst.liste()
    return alle[offset : offset + limit]


@router.post("", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def erstelle_agent(
    eingabe: AgentErstellen,
    dienst: AgentDienst = Depends(hole_agent_dienst),
) -> Agent:
    return await dienst.erstelle(eingabe)


@router.post("/aus-saat", response_model=Persona)
async def persona_aus_saat(eingabe: PersonaAusSaat) -> Persona:
    """Erzeugt eine Persona via LLM — Frontend kann sie dann posten."""
    return await PersonaDienst().generiere(eingabe.saat)


class AusGraphAnfrage(BaseModel):
    max_personen: int = Field(default=8, ge=1, le=30)
    sofort_anlegen: bool = Field(
        default=True,
        description="True: erzeugte Personas direkt als Agenten persistieren",
    )


@router.post("/aus-graph", response_model=list[Agent])
async def aus_graph(
    eingabe: AusGraphAnfrage,
    dienst: AgentDienst = Depends(hole_agent_dienst),
) -> list[Agent]:
    """Phase 2 der Pipeline: erzeugt Personas aus dem aktuellen Wissensgraphen
    (Personen-Entitäten) und legt sie optional direkt als Agenten an."""
    personas = await PersonaDienst().generiere_aus_graph(eingabe.max_personen)
    if not eingabe.sofort_anlegen:
        return [Agent(persona=p) for p in personas]
    angelegte: list[Agent] = []
    for p in personas:
        angelegte.append(await dienst.erstelle(AgentErstellen(persona=p)))
    return angelegte


class GedaechtnisEintrag(BaseModel):
    inhalt: str = Field(min_length=1, max_length=4000)


@router.post("/{agent_id}/gedaechtnis", status_code=status.HTTP_201_CREATED)
async def merke(
    agent_id: str,
    eintrag: GedaechtnisEintrag,
    agenten: AgentDienst = Depends(hole_agent_dienst),
) -> dict[str, str]:
    """Memory-Injection: schreibt eine Episode ins Langzeit-Gedächtnis eines Agenten."""
    if not await agenten.hole(agent_id):
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    from app.dienste.gedaechtnis_dienst import hole_gedaechtnis_dienst

    await hole_gedaechtnis_dienst().merke(agent_id, eintrag.inhalt)
    return {"status": "ok"}


@router.get("/{agent_id}/gedaechtnis", response_model=list[str])
async def lese_gedaechtnis(
    agent_id: str,
    grenze: int = 50,
    agenten: AgentDienst = Depends(hole_agent_dienst),
) -> list[str]:
    if not await agenten.hole(agent_id):
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    from app.dienste.gedaechtnis_dienst import hole_gedaechtnis_dienst

    return await hole_gedaechtnis_dienst().hole_kontext(agent_id, grenze)


@router.get("/{agent_id}", response_model=Agent)
async def hole_agent(agent_id: str, dienst: AgentDienst = Depends(hole_agent_dienst)) -> Agent:
    agent = await dienst.hole(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    return agent


@router.put("/{agent_id}", response_model=Agent)
async def aktualisiere_agent(
    agent_id: str,
    persona: Persona,
    dienst: AgentDienst = Depends(hole_agent_dienst),
) -> Agent:
    agent = await dienst.aktualisiere_persona(agent_id, persona)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def loesche_agent(agent_id: str, dienst: AgentDienst = Depends(hole_agent_dienst)) -> None:
    if not await dienst.loesche(agent_id):
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
