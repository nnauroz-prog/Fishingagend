"""Endpunkte zur Verwaltung von Agenten."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.dienste.agent_dienst import AgentDienst, hole_agent_dienst
from app.modelle.agent import Agent, AgentErstellen

router = APIRouter()


@router.get("", response_model=list[Agent])
async def liste_agenten(dienst: AgentDienst = Depends(hole_agent_dienst)) -> list[Agent]:
    return dienst.liste()


@router.post("", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def erstelle_agent(
    eingabe: AgentErstellen,
    dienst: AgentDienst = Depends(hole_agent_dienst),
) -> Agent:
    return dienst.erstelle(eingabe)


@router.get("/{agent_id}", response_model=Agent)
async def hole_agent(agent_id: str, dienst: AgentDienst = Depends(hole_agent_dienst)) -> Agent:
    agent = dienst.hole(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def loesche_agent(agent_id: str, dienst: AgentDienst = Depends(hole_agent_dienst)) -> None:
    if not dienst.loesche(agent_id):
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
