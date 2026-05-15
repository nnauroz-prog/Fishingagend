"""Verwaltung der Agenten — In-Memory-Stub für das Skelett."""

from __future__ import annotations

from app.modelle.agent import Agent, AgentErstellen


class AgentDienst:
    """Vorerst In-Memory; später durch SQLAlchemy-Repository ersetzbar."""

    def __init__(self) -> None:
        self._speicher: dict[str, Agent] = {}

    def liste(self) -> list[Agent]:
        return list(self._speicher.values())

    def hole(self, agent_id: str) -> Agent | None:
        return self._speicher.get(agent_id)

    def erstelle(self, eingabe: AgentErstellen) -> Agent:
        agent = Agent(persona=eingabe.persona, notizen=eingabe.notizen)
        self._speicher[agent.id] = agent
        return agent

    def loesche(self, agent_id: str) -> bool:
        return self._speicher.pop(agent_id, None) is not None


_dienst = AgentDienst()


def hole_agent_dienst() -> AgentDienst:
    return _dienst
