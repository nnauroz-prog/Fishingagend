"""GraphRAG — Aufbau eines Wissensgraphen aus Texten via LLM-Extraktion."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.dienste.llm_dienst import LLMSchnittstelle, hole_llm_dienst

_SYSTEM_EXTRAKTION = """Du extrahierst Entitäten und Beziehungen aus Texten
für einen Wissensgraphen. Erkenne Personen, Organisationen, Orte, Konzepte
und ihre Beziehungen.

Antwortformat (JSON-Objekt):
{
  "entitaeten": [
    {"name": "...", "typ": "Person|Organisation|Ort|Konzept|Ereignis", "beschreibung": "kurz"}
  ],
  "beziehungen": [
    {"von": "Entität A", "nach": "Entität B", "art": "z. B. arbeitet_bei", "gewicht": 0.0-1.0}
  ]
}

Sei sparsam: nur Entitäten, die wirklich genannt werden. Doppelte Namen einmal."""

_SYSTEM_ABFRAGE = """Du beantwortest Fragen anhand eines Wissensgraphen.
Halte dich strikt an die übergebenen Knoten und Kanten — wenn die Information
fehlt, sage das ehrlich. Antworte auf Deutsch."""


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

    def fuege_hinzu(self, anderer: WissensGraph) -> None:
        bekannt = {(e.name, e.typ) for e in self.entitaeten}
        for e in anderer.entitaeten:
            if (e.name, e.typ) not in bekannt:
                self.entitaeten.append(e)
                bekannt.add((e.name, e.typ))
        kanten = {(b.von, b.nach, b.art) for b in self.beziehungen}
        for b in anderer.beziehungen:
            if (b.von, b.nach, b.art) not in kanten:
                self.beziehungen.append(b)
                kanten.add((b.von, b.nach, b.art))

    def als_text(self) -> str:
        zeilen = ["Entitäten:"]
        for e in self.entitaeten[:80]:
            zeilen.append(f"- {e.name} ({e.typ}): {e.beschreibung}")
        zeilen.append("\nBeziehungen:")
        for b in self.beziehungen[:120]:
            zeilen.append(f"- {b.von} --[{b.art}]--> {b.nach}")
        return "\n".join(zeilen)


def _zerlege(text: str, groesse: int = 1500) -> list[str]:
    """Einfaches Chunking auf Satzgrenze — vermeidet hartes Abschneiden."""
    text = text.strip()
    if len(text) <= groesse:
        return [text]
    teile: list[str] = []
    rest = text
    while len(rest) > groesse:
        schnitt = rest.rfind(". ", 0, groesse)
        if schnitt < groesse // 2:
            schnitt = groesse
        teile.append(rest[:schnitt].strip())
        rest = rest[schnitt:].strip()
    if rest:
        teile.append(rest)
    return teile


class GraphRAGDienst:
    def __init__(self, llm: LLMSchnittstelle | None = None) -> None:
        self._llm = llm or hole_llm_dienst()

    async def extrahiere(self, texte: list[str]) -> WissensGraph:
        graph = WissensGraph()
        for text in texte:
            for chunk in _zerlege(text):
                roh = await self._llm.antworte_json(
                    system_prompt=_SYSTEM_EXTRAKTION,
                    anweisung=f"Text:\n{chunk}",
                    max_token=2048,
                )
                teil = WissensGraph(
                    entitaeten=[Entitaet(**e) for e in roh.get("entitaeten", [])],
                    beziehungen=[Beziehung(**b) for b in roh.get("beziehungen", [])],
                )
                graph.fuege_hinzu(teil)
        return graph

    async def abfrage(self, graph: WissensGraph, frage: str) -> str:
        anweisung = f"Wissensgraph:\n{graph.als_text()}\n\nFrage: {frage}"
        antwort = await self._llm.antworte(
            system_prompt=_SYSTEM_ABFRAGE,
            verlauf=[{"role": "user", "content": anweisung}],
            max_token=1024,
            temperatur=0.3,
        )
        return antwort.text
