"""Endpunkte zur Verwaltung von Agenten."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.dienste.agent_dienst import AgentDienst, hole_agent_dienst
from app.dienste.persona_dienst import PersonaDienst
from app.modelle.agent import Agent, AgentErstellen
from app.modelle.persona import Persona

router = APIRouter()


class PersonaAusSaat(BaseModel):
    saat: dict[str, str] = Field(default_factory=dict)


@router.get("", response_model=list[Agent])
async def liste_agenten(dienst: AgentDienst = Depends(hole_agent_dienst)) -> list[Agent]:
    return await dienst.liste()


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


@router.get("/{agent_id}", response_model=Agent)
async def hole_agent(agent_id: str, dienst: AgentDienst = Depends(hole_agent_dienst)) -> Agent:
    agent = await dienst.hole(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def loesche_agent(agent_id: str, dienst: AgentDienst = Depends(hole_agent_dienst)) -> None:
    if not await dienst.loesche(agent_id):
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
