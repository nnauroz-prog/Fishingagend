"""GraphRAG — Aufbau eines Wissensgraphen aus unstrukturiertem Text (Stub)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Entitaet:
    name: str
    typ: str
    beschreibung: str = ""


@dataclass
class Beziehung:
    von: str
    nach: str
    art: str
    gewicht: float = 1.0


@dataclass
class WissensGraph:
    entitaeten: list[Entitaet] = field(default_factory=list)
    beziehungen: list[Beziehung] = field(default_factory=list)


class GraphRAGDienst:
    """Extrahiert Entitäten und Beziehungen aus Texten und baut einen Graphen."""

    async def extrahiere(self, texte: list[str]) -> WissensGraph:
        """Vorerst Platzhalter — produziert leeren Graphen.

        In der Voll-Implementierung wird hier ein LLM-Pipeline-Aufruf
        ausgeführt: Chunking → NER → Relations-Extraktion → Deduplikation.
        """
        return WissensGraph()

    async def abfrage(self, _graph: WissensGraph, _frage: str) -> str:
        """Beantwortet eine natürliche-Sprache-Frage gegen den Graphen."""
        return "Noch nicht implementiert."
