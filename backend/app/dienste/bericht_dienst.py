"""Berichts-Agent — fasst Simulationsdaten via LLM zusammen."""

from __future__ import annotations

from collections import Counter

from app.dienste.llm_dienst import LLMSchnittstelle, hole_llm_dienst
from app.modelle.simulation import Simulation

_SYSTEM = """Du bist Analyst für Multi-Agenten-Simulationen.
Schreibe einen prägnanten Bericht in deutscher Sprache als Markdown.
Struktur:

# Zusammenfassung (3-4 Sätze)
## Beobachtungen je Welt
## Schlüsselereignisse
## Einschätzung & Empfehlung

Bleibe sachlich. Wenn die Variantenwelt fehlt, lasse den Vergleich aus."""


class BerichtDienst:
    def __init__(self, llm: LLMSchnittstelle | None = None) -> None:
        self._llm = llm or hole_llm_dienst()

    async def erstelle_bericht(self, simulation: Simulation) -> str:
        zaehler = Counter(s.welt for s in simulation.verlauf)
        anweisung = self._baue_anweisung(simulation, zaehler)
        antwort = await self._llm.antworte(
            system_prompt=_SYSTEM,
            verlauf=[{"role": "user", "content": anweisung}],
            max_token=2048,
            temperatur=0.4,
        )
        return antwort.text

    def _baue_anweisung(self, sim: Simulation, zaehler: Counter[str]) -> str:
        zeilen = [
            f"Simulation: {sim.name}",
            f"Beschreibung: {sim.beschreibung or '—'}",
            f"Status: {sim.status.value}",
            f"Schritte: {sim.schritte} | Agenten: {len(sim.agent_ids)} | Dual: {sim.dual_modus}",
            f"Variable: {sim.variable or '—'}",
            "",
            f"Ereignisse pro Welt: {dict(zaehler)}",
            "",
            "Verlauf (gekürzt auf maximal 60 Einträge):",
        ]
        for schritt in sim.verlauf[:60]:
            for ereignis in schritt.ereignisse[:3]:
                zeilen.append(f"- [{schritt.welt} #{schritt.nummer}] {ereignis}")
        if len(sim.verlauf) > 60:
            zeilen.append(f"... und {len(sim.verlauf) - 60} weitere Schritte ausgelassen.")
        return "\n".join(zeilen)
