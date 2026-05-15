"""Simulations-Engine — startet Dual-Welt-Simulationen (Stub)."""

from __future__ import annotations

from app.modelle.simulation import (
    Simulation,
    SimulationErstellen,
    SimulationSchritt,
    SimulationStatus,
)


class SimulationDienst:
    def __init__(self) -> None:
        self._lauf: dict[str, Simulation] = {}

    def liste(self) -> list[Simulation]:
        return list(self._lauf.values())

    def hole(self, sim_id: str) -> Simulation | None:
        return self._lauf.get(sim_id)

    def plane(self, eingabe: SimulationErstellen) -> Simulation:
        sim = Simulation(
            name=eingabe.name,
            beschreibung=eingabe.beschreibung,
            agent_ids=eingabe.agent_ids,
            schritte=eingabe.schritte,
            variable=eingabe.variable,
            dual_modus=eingabe.dual_modus,
        )
        self._lauf[sim.id] = sim
        return sim

    async def starte(self, sim_id: str) -> Simulation | None:
        """Stub: legt deterministische Beispielschritte ohne LLM-Aufruf an."""
        sim = self._lauf.get(sim_id)
        if sim is None:
            return None
        sim.status = SimulationStatus.LAEUFT
        for nummer in range(1, sim.schritte + 1):
            sim.verlauf.append(
                SimulationSchritt(
                    nummer=nummer,
                    welt="kontrolle",
                    ereignisse=[f"Schritt {nummer} (Kontroll-Welt)"],
                )
            )
            if sim.dual_modus:
                sim.verlauf.append(
                    SimulationSchritt(
                        nummer=nummer,
                        welt="variante",
                        ereignisse=[f"Schritt {nummer} (Varianten-Welt)"],
                    )
                )
        sim.status = SimulationStatus.ABGESCHLOSSEN
        return sim


_dienst = SimulationDienst()


def hole_simulation_dienst() -> SimulationDienst:
    return _dienst
