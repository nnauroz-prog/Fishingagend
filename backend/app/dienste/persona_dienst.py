"""Persona-Generierung — erzeugt aus Saat-Daten eine glaubwürdige Persona via LLM."""

from __future__ import annotations

import asyncio

from app.dienste.graphrag_dienst import GraphRAGDienst
from app.dienste.llm_dienst import LLMSchnittstelle, hole_llm_dienst
from app.modelle.persona import Persona

_SYSTEM = """Du bist Persona-Designer für eine Multi-Agenten-Simulation.
Aus den übergebenen Saat-Daten erzeugst du eine plausible, dreidimensionale
Person. Die Person muss konsistent und realistisch sein — keine Karikatur.

Antwortformat (JSON-Objekt):
{
  "name": "Vorname Nachname",
  "alter": 18-90,
  "beruf": "klare Berufsbezeichnung",
  "hintergrund": "2-3 Sätze Lebenslauf, prägende Erfahrungen",
  "werte": ["Wert 1", "Wert 2", "Wert 3"],
  "charakterzuege": ["Zug 1", "Zug 2", "Zug 3"],
  "sprachstil": "z. B. fachlich, salopp, formell, knapp"
}
Antworte ausschließlich auf Deutsch."""


class PersonaDienst:
    def __init__(self, llm: LLMSchnittstelle | None = None) -> None:
        self._fixierter_llm = llm

    @property
    def _llm(self) -> LLMSchnittstelle:
        return self._fixierter_llm or hole_llm_dienst()

    async def generiere(self, saat: dict[str, str]) -> Persona:
        anweisung = "Saat-Daten:\n" + "\n".join(f"- {k}: {v}" for k, v in saat.items())
        roh = await self._llm.antworte_json(_SYSTEM, anweisung)
        return Persona(
            name=str(roh.get("name", saat.get("name", "Unbenannt"))),
            alter=roh.get("alter"),
            beruf=roh.get("beruf"),
            hintergrund=str(roh.get("hintergrund", "")),
            werte=list(roh.get("werte", [])),
            charakterzuege=list(roh.get("charakterzuege", [])),
            sprachstil=str(roh.get("sprachstil", "neutral")),
        )

    async def generiere_aus_graph(self, max_personen: int = 8) -> list[Persona]:
        """Liest Personen-Entitäten aus dem aktuellen Wissensgraphen und
        erzeugt aus jeder eine plausible Persona — parallel."""
        graph = await GraphRAGDienst().lade()
        personen = [e for e in graph.entitaeten if e.typ.lower() == "person"]
        personen = personen[:max_personen]
        if not personen:
            return []

        async def _eine(name: str, beschreibung: str) -> Persona:
            saat = {"name": name, "kontext": beschreibung or "(keine Beschreibung)"}
            return await self.generiere(saat)

        return await asyncio.gather(*(_eine(p.name, p.beschreibung) for p in personen))
