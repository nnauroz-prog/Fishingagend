"""Simulations-Engine — Dual-Welt-Simulation mit echten LLM-Aufrufen."""

from __future__ import annotations

import asyncio
import json
from uuid import uuid4

from sqlalchemy import select

from app.datenbank import (
    AgentZeile,
    PlattformBeitragZeile,
    SimulationSchrittZeile,
    SimulationZeile,
    dekodiere_json,
    kodiere_json,
    session_factory,
)
from app.dienste.ereignis_bus import hole_ereignis_bus
from app.dienste.gedaechtnis_dienst import hole_gedaechtnis_dienst
from app.dienste.lern_dienst import hole_lern_dienst
from app.dienste.llm_dienst import LLMSchnittstelle, hole_llm_dienst
from app.dienste.plattform_dienst import hole_plattform_dienst
from app.modelle.agent import Agent
from app.modelle.persona import Persona
from app.modelle.simulation import (
    Simulation,
    SimulationErstellen,
    SimulationSchritt,
    SimulationStatus,
)
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)

_SYSTEM_AGENT = """Du verkörperst {name}.
Beruf: {beruf}. Sprachstil: {sprachstil}.
Hintergrund: {hintergrund}
Werte: {werte}. Charakterzüge: {charakterzuege}.

Du nimmst an einer mehrstufigen sozialen Simulation teil.
In jedem Schritt erhältst du den aktuellen Welt-Zustand und entscheidest,
welche Aktion du als nächstes vornimmst — kurz, in einer Zeile, in der
ersten Person Gegenwart.

Antworte ausschließlich auf Deutsch."""


class SimulationDienst:
    def __init__(self, llm: LLMSchnittstelle | None = None) -> None:
        self._llm = llm or hole_llm_dienst()

    # -------- Lese-Operationen --------
    async def liste(self) -> list[Simulation]:
        async with session_factory()() as session:
            zeilen = (await session.execute(select(SimulationZeile))).scalars().all()
            return [await self._zu_modell(session, z) for z in zeilen]

    async def hole(self, sim_id: str) -> Simulation | None:
        async with session_factory()() as session:
            zeile = await session.get(SimulationZeile, sim_id)
            return await self._zu_modell(session, zeile) if zeile else None

    # -------- Schreib-Operationen --------
    async def plane(self, eingabe: SimulationErstellen) -> Simulation:
        async with session_factory()() as session:
            zeile = SimulationZeile(
                id=str(uuid4()),
                name=eingabe.name,
                beschreibung=eingabe.beschreibung,
                agent_ids_json=kodiere_json(eingabe.agent_ids),
                schritte=eingabe.schritte,
                variable_json=eingabe.variable,
                dual_modus=eingabe.dual_modus,
                plattform_modus=eingabe.plattform_modus,
            )
            session.add(zeile)
            await session.commit()
            await session.refresh(zeile)
            return await self._zu_modell(session, zeile)

    async def starte(self, sim_id: str) -> Simulation | None:
        sim = await self.hole(sim_id)
        if sim is None:
            return None

        await self._setze_status(sim_id, SimulationStatus.LAEUFT)
        try:
            agenten = await self._lade_agenten(sim.agent_ids)
            welten = ["kontrolle"] + (["variante"] if sim.dual_modus else [])
            beschreibungen: dict[str, list[str]] = {welt: [] for welt in welten}

            for nummer in range(1, sim.schritte + 1):
                aufgaben = [
                    self._schritt_in_welt(
                        sim_id=sim_id,
                        nummer=nummer,
                        welt=welt,
                        agenten=agenten,
                        variable=sim.variable if welt == "variante" else {},
                        bisher=beschreibungen[welt],
                        plattform_modus=sim.plattform_modus,
                    )
                    for welt in welten
                ]
                ergebnisse = await asyncio.gather(*aufgaben)
                for welt, schritt in zip(welten, ergebnisse, strict=False):
                    beschreibungen[welt].extend(schritt.ereignisse)

            await self._setze_status(sim_id, SimulationStatus.ABGESCHLOSSEN)
        except Exception:
            logger.exception("simulation_fehlgeschlagen", sim_id=sim_id)
            await self._setze_status(sim_id, SimulationStatus.FEHLGESCHLAGEN)
            raise

        # Lern-Phase nach Abschluss: Reflexionen, Beziehungen, Konsolidierung
        fertige = await self.hole(sim_id)
        if fertige and fertige.status == SimulationStatus.ABGESCHLOSSEN:
            try:
                ergebnis = await hole_lern_dienst().lerne_aus_sim(fertige)
                await hole_ereignis_bus().veroeffentliche(
                    f"sim:{sim_id}", {"typ": "lernen", **ergebnis}
                )
            except Exception:
                logger.exception("lernen_fehlgeschlagen", sim_id=sim_id)

        return fertige

    # -------- Hilfen --------
    async def _setze_status(self, sim_id: str, status: SimulationStatus) -> None:
        async with session_factory()() as session:
            zeile = await session.get(SimulationZeile, sim_id)
            if zeile:
                zeile.status = status.value
                await session.commit()
        await hole_ereignis_bus().veroeffentliche(
            f"sim:{sim_id}", {"typ": "status", "status": status.value}
        )

    async def _lade_agenten(self, ids: list[str]) -> list[Agent]:
        async with session_factory()() as session:
            zeilen = (
                await session.execute(select(AgentZeile).where(AgentZeile.id.in_(ids)))
            ).scalars().all()
            return [
                Agent(
                    id=z.id,
                    persona=Persona(**json.loads(z.persona_json)),
                    notizen=z.notizen,
                    erstellt_am=z.erstellt_am,
                    aktualisiert_am=z.aktualisiert_am,
                )
                for z in zeilen
            ]

    async def _schritt_in_welt(
        self,
        sim_id: str,
        nummer: int,
        welt: str,
        agenten: list[Agent],
        variable: dict[str, object],
        bisher: list[str],
        plattform_modus: bool = False,
    ) -> SimulationSchritt:
        kontext = "\n".join(f"- {e}" for e in bisher[-10:]) or "(noch keine Ereignisse)"
        variablen_block = (
            f"Eingespeiste Variable: {json.dumps(variable, ensure_ascii=False)}\n"
            if variable
            else ""
        )

        gedaechtnis = hole_gedaechtnis_dienst()
        name_zu_id = {a.persona.name: a.id for a in agenten}

        if plattform_modus:
            ergebnisse = await self._plattform_schritt(
                sim_id, welt, nummer, agenten, variablen_block
            )
        else:
            async def _einzelaktion(agent: Agent) -> str:
                sys_prompt = _SYSTEM_AGENT.format(
                    name=agent.persona.name,
                    beruf=agent.persona.beruf or "unbekannt",
                    sprachstil=agent.persona.sprachstil,
                    hintergrund=agent.persona.hintergrund,
                    werte=", ".join(agent.persona.werte) or "—",
                    charakterzuege=", ".join(agent.persona.charakterzuege) or "—",
                )
                anweisung = (
                    f"Schritt {nummer}, Welt: {welt}.\n"
                    f"{variablen_block}"
                    f"Bisherige Ereignisse:\n{kontext}\n\n"
                    "Beschreibe deine nächste Handlung in EINEM Satz."
                )
                antwort = await self._llm.antworte(
                    system_prompt=sys_prompt,
                    verlauf=[{"role": "user", "content": anweisung}],
                    max_token=120,
                    temperatur=0.8,
                )
                return f"{agent.persona.name}: {antwort.text.strip()}"

            ergebnisse = await asyncio.gather(*(_einzelaktion(a) for a in agenten))

        # Temporale Memory-Updates: jede Aktion landet im Langzeit-Gedaechtnis
        # des handelnden Agenten — so weiss er beim spaeteren Chat noch, was
        # er in welcher Welt getan hat.
        for eintrag in ergebnisse:
            if ":" in eintrag:
                name = eintrag.split(":", 1)[0].strip()
                aid = name_zu_id.get(name)
                if aid:
                    await gedaechtnis.merke(
                        aid,
                        f"[Sim {sim_id[:6]}/{welt}/Schritt {nummer}] {eintrag}",
                    )

        schritt = SimulationSchritt(nummer=nummer, welt=welt, ereignisse=ergebnisse)  # type: ignore[arg-type]

        async with session_factory()() as session:
            session.add(
                SimulationSchrittZeile(
                    simulation_id=sim_id,
                    nummer=nummer,
                    welt=welt,
                    ereignisse_json=kodiere_json(ergebnisse),
                    agent_zustaende_json=kodiere_json({}),
                )
            )
            await session.commit()

        await hole_ereignis_bus().veroeffentliche(
            f"sim:{sim_id}",
            {
                "typ": "schritt",
                "nummer": nummer,
                "welt": welt,
                "ereignisse": ergebnisse,
            },
        )
        return schritt

    async def _plattform_schritt(
        self,
        sim_id: str,
        welt: str,
        nummer: int,
        agenten: list[Agent],
        variablen_block: str,
    ) -> list[str]:
        """Plattform-Schritt: jeder Agent waehlt Posten/Reagieren/Folgen.

        Sequentiell, damit spaetere Agenten die frischen Posts frueherer Agenten
        sehen — das spiegelt eine echte Plattform realistischer wider.
        """
        plattform = hole_plattform_dienst()
        namen_alle = [a.persona.name for a in agenten]
        ergebnisse: list[str] = []

        for agent in agenten:
            async with session_factory()() as session:
                stmt = (
                    select(PlattformBeitragZeile)
                    .where(
                        PlattformBeitragZeile.simulation_id == sim_id,
                        PlattformBeitragZeile.welt == welt,
                    )
                    .order_by(PlattformBeitragZeile.id.desc())
                    .limit(20)
                )
                beitraege = list(reversed((await session.execute(stmt)).scalars().all()))

            andere = [n for n in namen_alle if n != agent.persona.name]
            ergebnisse.append(
                await plattform.naechste_aktion(
                    sim_id=sim_id,
                    welt=welt,
                    schritt_nr=nummer,
                    agent=agent,
                    kontext_beitraege=beitraege,
                    andere_namen=andere,
                    variablen_text=variablen_block,
                )
            )

        return ergebnisse

    async def _zu_modell(self, session, zeile: SimulationZeile) -> Simulation:
        await session.refresh(zeile, attribute_names=["schritt_zeilen"])
        verlauf = [
            SimulationSchritt(
                nummer=s.nummer,
                welt=s.welt,  # type: ignore[arg-type]
                ereignisse=dekodiere_json(s.ereignisse_json, []),
                agent_zustaende=dekodiere_json(s.agent_zustaende_json, {}),
            )
            for s in zeile.schritt_zeilen
        ]
        return Simulation(
            id=zeile.id,
            name=zeile.name,
            beschreibung=zeile.beschreibung,
            agent_ids=dekodiere_json(zeile.agent_ids_json, []),
            schritte=zeile.schritte,
            variable=zeile.variable_json or {},
            dual_modus=zeile.dual_modus,
            plattform_modus=zeile.plattform_modus,
            status=SimulationStatus(zeile.status),
            erstellt_am=zeile.erstellt_am,
            verlauf=verlauf,
        )


_dienst: SimulationDienst | None = None


def hole_simulation_dienst() -> SimulationDienst:
    global _dienst
    if _dienst is None:
        _dienst = SimulationDienst()
    return _dienst


def setze_simulation_dienst(dienst: SimulationDienst | None) -> None:
    global _dienst
    _dienst = dienst
