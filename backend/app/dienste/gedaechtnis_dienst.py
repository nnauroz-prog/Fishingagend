"""Langzeit-Gedächtnis pro Agent — In-Memory-Stub."""

from __future__ import annotations

from collections import defaultdict


class GedaechtnisDienst:
    """Speichert vergangene Episoden und erlaubt einfache Abfragen."""

    def __init__(self) -> None:
        self._episoden: dict[str, list[str]] = defaultdict(list)

    def merke(self, agent_id: str, episode: str) -> None:
        self._episoden[agent_id].append(episode)

    def hole_kontext(self, agent_id: str, max_eintraege: int = 10) -> list[str]:
        return self._episoden[agent_id][-max_eintraege:]

    def loesche(self, agent_id: str) -> None:
        self._episoden.pop(agent_id, None)


_dienst = GedaechtnisDienst()


def hole_gedaechtnis_dienst() -> GedaechtnisDienst:
    return _dienst
