"""Persona-Generierung — erzeugt aus Saat-Daten eine glaubwürdige Persona via LLM."""

from __future__ import annotations

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
        self._llm = llm or hole_llm_dienst()

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
