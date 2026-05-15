"""Verwaltung der Agenten — persistiert via SQLAlchemy."""

from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.datenbank import AgentZeile, session_factory
from app.modelle.agent import Agent, AgentErstellen
from app.modelle.persona import Persona


def _zu_agent(zeile: AgentZeile) -> Agent:
    return Agent(
        id=zeile.id,
        persona=Persona(**json.loads(zeile.persona_json)),
        notizen=zeile.notizen,
        erstellt_am=zeile.erstellt_am,
        aktualisiert_am=zeile.aktualisiert_am,
    )


class AgentDienst:
    async def liste(self) -> list[Agent]:
        async with session_factory()() as session:
            ergebnis = await session.execute(select(AgentZeile))
            return [_zu_agent(z) for z in ergebnis.scalars().all()]

    async def hole(self, agent_id: str) -> Agent | None:
        async with session_factory()() as session:
            zeile = await session.get(AgentZeile, agent_id)
            return _zu_agent(zeile) if zeile else None

    async def erstelle(self, eingabe: AgentErstellen) -> Agent:
        async with session_factory()() as session:
            zeile = AgentZeile(
                id=str(uuid4()),
                persona_json=eingabe.persona.model_dump_json(),
                notizen=eingabe.notizen,
            )
            session.add(zeile)
            await session.commit()
            await session.refresh(zeile)
            return _zu_agent(zeile)

    async def aktualisiere_persona(self, agent_id: str, persona: Persona) -> Agent | None:
        async with session_factory()() as session:
            zeile = await session.get(AgentZeile, agent_id)
            if zeile is None:
                return None
            zeile.persona_json = persona.model_dump_json()
            await session.commit()
            await session.refresh(zeile)
            return _zu_agent(zeile)

    async def loesche(self, agent_id: str) -> bool:
        async with session_factory()() as session:
            zeile = await session.get(AgentZeile, agent_id)
            if zeile is None:
                return False
            await session.delete(zeile)
            await session.commit()
            return True


# Pro Prozess eine Instanz; sie ist zustandslos.
_dienst = AgentDienst()


def hole_agent_dienst() -> AgentDienst:
    return _dienst


# Hilfsfunktion für andere Dienste
async def lade_agent_via_session(session: AsyncSession, agent_id: str) -> Agent | None:
    zeile = await session.get(AgentZeile, agent_id)
    return _zu_agent(zeile) if zeile else None
