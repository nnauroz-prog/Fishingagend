"""Plattform-Simulation — verwaltet Posts, Reaktionen und Folgen-Beziehungen."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass

from sqlalchemy import select

from app.datenbank import (
    PlattformBeitragZeile,
    PlattformFolgtZeile,
    PlattformReaktionZeile,
    session_factory,
)
from app.dienste.llm_dienst import LLMSchnittstelle, hole_llm_dienst
from app.modelle.agent import Agent
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)


_SYSTEM = """Du verkörperst {name} in einer Multi-Agenten-Plattform-Simulation.
Beruf: {beruf}. Sprachstil: {sprachstil}.
Hintergrund: {hintergrund}
Werte: {werte}.

Im aktuellen Schritt wählst du genau EINE Aktion. Antworte als JSON:

{{
  "aktion": "posten" | "reagieren" | "folgen" | "nichts",
  "inhalt": "kurzer Post-Text (nur bei posten)",
  "beitrag_id": 0,                  // ID des Beitrags (nur bei reagieren)
  "reaktion": "like" | "antwort" | "repost",  // nur bei reagieren
  "antwort": "Kommentar (nur bei reagieren+antwort)",
  "ziel": "Name eines anderen Agenten (nur bei folgen)"
}}

Antworte ausschließlich auf Deutsch. Bleibe in deiner Rolle."""


@dataclass
class FeedEintrag:
    art: str  # post, like, antwort, repost, folgt
    autor: str
    inhalt: str
    welt: str
    schritt_nr: int
    beitrag_id: int | None = None
    ziel: str | None = None


class PlattformDienst:
    def __init__(self, llm: LLMSchnittstelle | None = None) -> None:
        self._fixierter_llm = llm

    @property
    def _llm(self) -> LLMSchnittstelle:
        return self._fixierter_llm or hole_llm_dienst()

    async def naechste_aktion(
        self,
        sim_id: str,
        welt: str,
        schritt_nr: int,
        agent: Agent,
        kontext_beitraege: list[PlattformBeitragZeile],
        andere_namen: list[str],
        variablen_text: str,
    ) -> str:
        """Lässt einen Agenten eine Plattform-Aktion wählen und persistiert sie."""
        beitrags_text = "\n".join(
            f"- #{b.id} von {b.autor}: {b.inhalt}" for b in kontext_beitraege[-8:]
        ) or "(noch keine Beiträge)"

        sys_prompt = _SYSTEM.format(
            name=agent.persona.name,
            beruf=agent.persona.beruf or "unbekannt",
            sprachstil=agent.persona.sprachstil,
            hintergrund=agent.persona.hintergrund or "—",
            werte=", ".join(agent.persona.werte) or "—",
        )
        anweisung = (
            f"Welt: {welt}, Schritt {schritt_nr}.\n"
            f"{variablen_text}"
            f"Aktuelle Beiträge:\n{beitrags_text}\n\n"
            f"Andere Agenten: {', '.join(andere_namen) or '—'}\n\n"
            "Wähle deine nächste Aktion."
        )

        try:
            roh = await self._llm.antworte_json(sys_prompt, anweisung, max_token=400)
        except Exception:
            # Fallback: zufällige Aktion, damit die Sim weiterläuft
            roh = self._zufalls_aktion(kontext_beitraege, andere_namen)

        return await self._persistiere(sim_id, welt, schritt_nr, agent, roh, kontext_beitraege)

    def _zufalls_aktion(
        self,
        beitraege: list[PlattformBeitragZeile],
        namen: list[str],
    ) -> dict:
        if beitraege and random.random() < 0.4:
            return {
                "aktion": "reagieren",
                "beitrag_id": random.choice(beitraege).id,
                "reaktion": "like",
            }
        if namen and random.random() < 0.2:
            return {"aktion": "folgen", "ziel": random.choice(namen)}
        return {"aktion": "posten", "inhalt": "Kein Kommentar."}

    async def _persistiere(
        self,
        sim_id: str,
        welt: str,
        schritt_nr: int,
        agent: Agent,
        roh: dict,
        beitraege: list[PlattformBeitragZeile],
    ) -> str:
        aktion = str(roh.get("aktion", "nichts")).lower()
        async with session_factory()() as session:
            if aktion == "posten":
                inhalt = str(roh.get("inhalt") or "").strip()[:600] or "(leerer Post)"
                eintrag = PlattformBeitragZeile(
                    simulation_id=sim_id,
                    welt=welt,
                    schritt_nr=schritt_nr,
                    autor=agent.persona.name,
                    inhalt=inhalt,
                )
                session.add(eintrag)
                await session.commit()
                return f"{agent.persona.name} postet: „{inhalt}“"

            if aktion == "reagieren":
                bid = int(roh.get("beitrag_id") or 0)
                gueltig = next((b for b in beitraege if b.id == bid), None)
                if gueltig is None and beitraege:
                    gueltig = beitraege[-1]
                if gueltig is None:
                    return f"{agent.persona.name} liest, sieht aber nichts."
                typ = str(roh.get("reaktion", "like")).lower()
                if typ not in {"like", "antwort", "repost"}:
                    typ = "like"
                inhalt = str(roh.get("antwort") or "")[:400] if typ == "antwort" else None
                session.add(
                    PlattformReaktionZeile(
                        simulation_id=sim_id,
                        welt=welt,
                        schritt_nr=schritt_nr,
                        beitrag_id=gueltig.id,
                        autor=agent.persona.name,
                        typ=typ,
                        inhalt=inhalt,
                    )
                )
                await session.commit()
                if typ == "antwort":
                    return f"{agent.persona.name} antwortet auf #{gueltig.id}: „{inhalt}“"
                return f"{agent.persona.name} {typ}t Beitrag #{gueltig.id} von {gueltig.autor}"

            if aktion == "folgen":
                ziel = str(roh.get("ziel") or "").strip()
                if not ziel or ziel == agent.persona.name:
                    return f"{agent.persona.name} überlegt, wem er folgen soll."
                session.add(
                    PlattformFolgtZeile(
                        simulation_id=sim_id,
                        welt=welt,
                        folger=agent.persona.name,
                        gefolgter=ziel,
                        schritt_nr=schritt_nr,
                    )
                )
                await session.commit()
                return f"{agent.persona.name} folgt nun {ziel}"

            return f"{agent.persona.name} bleibt heute still."

    async def feed(self, sim_id: str, welt: str | None = None) -> list[dict]:
        """Komplettes Feed: Posts samt Reaktionen, optional auf eine Welt gefiltert."""
        async with session_factory()() as session:
            stmt = select(PlattformBeitragZeile).where(
                PlattformBeitragZeile.simulation_id == sim_id
            )
            if welt:
                stmt = stmt.where(PlattformBeitragZeile.welt == welt)
            stmt = stmt.order_by(PlattformBeitragZeile.id)
            beitraege = (await session.execute(stmt)).scalars().all()

            if not beitraege:
                return []

            ids = [b.id for b in beitraege]
            r_stmt = select(PlattformReaktionZeile).where(
                PlattformReaktionZeile.beitrag_id.in_(ids)
            )
            reaktionen = (await session.execute(r_stmt)).scalars().all()
            r_index: dict[int, list[dict]] = {}
            for r in reaktionen:
                r_index.setdefault(r.beitrag_id, []).append(
                    {"typ": r.typ, "autor": r.autor, "inhalt": r.inhalt, "schritt_nr": r.schritt_nr}
                )

            return [
                {
                    "id": b.id,
                    "welt": b.welt,
                    "autor": b.autor,
                    "schritt_nr": b.schritt_nr,
                    "inhalt": b.inhalt,
                    "reaktionen": r_index.get(b.id, []),
                }
                for b in beitraege
            ]

    async def folgen(self, sim_id: str, welt: str | None = None) -> list[dict]:
        async with session_factory()() as session:
            stmt = select(PlattformFolgtZeile).where(
                PlattformFolgtZeile.simulation_id == sim_id
            )
            if welt:
                stmt = stmt.where(PlattformFolgtZeile.welt == welt)
            zeilen = (await session.execute(stmt)).scalars().all()
            return [
                {"folger": z.folger, "gefolgter": z.gefolgter, "schritt_nr": z.schritt_nr, "welt": z.welt}
                for z in zeilen
            ]


_dienst: PlattformDienst | None = None


def hole_plattform_dienst() -> PlattformDienst:
    global _dienst
    if _dienst is None:
        _dienst = PlattformDienst()
    return _dienst


def setze_plattform_dienst(d: PlattformDienst | None) -> None:
    global _dienst
    _dienst = d


# JSON ist hier nicht direkt verwendet, aber Code unten könnte ihn brauchen.
_ = json
