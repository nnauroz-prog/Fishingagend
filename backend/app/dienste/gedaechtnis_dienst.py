"""Langzeit-Gedächtnis pro Agent — persistiert in der Datenbank."""

from __future__ import annotations

from sqlalchemy import desc, select

from app.datenbank import GedaechtnisZeile, session_factory


class GedaechtnisDienst:
    async def merke(self, agent_id: str, episode: str) -> None:
        async with session_factory()() as session:
            session.add(GedaechtnisZeile(agent_id=agent_id, inhalt=episode))
            await session.commit()

    async def hole_kontext(self, agent_id: str, max_eintraege: int = 10) -> list[str]:
        async with session_factory()() as session:
            stmt = (
                select(GedaechtnisZeile)
                .where(GedaechtnisZeile.agent_id == agent_id)
                .order_by(desc(GedaechtnisZeile.id))
                .limit(max_eintraege)
            )
            zeilen = (await session.execute(stmt)).scalars().all()
            return [z.inhalt for z in reversed(zeilen)]

    async def loesche(self, agent_id: str) -> None:
        async with session_factory()() as session:
            zeilen = (
                await session.execute(
                    select(GedaechtnisZeile).where(GedaechtnisZeile.agent_id == agent_id)
                )
            ).scalars().all()
            for z in zeilen:
                await session.delete(z)
            await session.commit()


_dienst = GedaechtnisDienst()


def hole_gedaechtnis_dienst() -> GedaechtnisDienst:
    return _dienst
