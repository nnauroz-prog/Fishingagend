"""Berichts-Agent — fasst Simulationsdaten zusammen."""

from __future__ import annotations

from app.modelle.simulation import Simulation


class BerichtDienst:
    """Erzeugt einen lesbaren Bericht aus einem Simulationslauf."""

    async def erstelle_bericht(self, simulation: Simulation) -> str:
        """Stub: produziert eine Markdown-Zusammenfassung ohne LLM."""
        zeilen: list[str] = [
            f"# Bericht: {simulation.name}",
            "",
            f"- Status: **{simulation.status.value}**",
            f"- Agenten: {len(simulation.agent_ids)}",
            f"- Schritte: {simulation.schritte}",
            f"- Dual-Modus: {'ja' if simulation.dual_modus else 'nein'}",
            "",
            "## Verlauf",
        ]
        for schritt in simulation.verlauf[:50]:
            zeilen.append(f"- Schritt {schritt.nummer} ({schritt.welt}): {', '.join(schritt.ereignisse)}")
        if len(simulation.verlauf) > 50:
            zeilen.append(f"- ... und {len(simulation.verlauf) - 50} weitere Schritte")
        return "\n".join(zeilen)
