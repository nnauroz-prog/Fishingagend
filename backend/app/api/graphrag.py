"""GraphRAG-Endpunkte — Aufbau, Abfrage und Anzeige des Wissensgraphen."""

from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.dienste.graphrag_dienst import GraphRAGDienst

router = APIRouter()


class ExtraktionsAnfrage(BaseModel):
    texte: list[str] = Field(min_length=1)


class AbfrageAnfrage(BaseModel):
    frage: str = Field(min_length=1)


class EntitaetAusgabe(BaseModel):
    name: str
    typ: str
    beschreibung: str = ""


class BeziehungAusgabe(BaseModel):
    von: str
    nach: str
    art: str
    gewicht: float = 1.0


class GraphAusgabe(BaseModel):
    entitaeten: list[EntitaetAusgabe]
    beziehungen: list[BeziehungAusgabe]


_dienst = GraphRAGDienst()


@router.post("/extrahieren", response_model=GraphAusgabe)
async def extrahiere(anfrage: ExtraktionsAnfrage) -> GraphAusgabe:
    graph = await _dienst.extrahiere(anfrage.texte)
    return GraphAusgabe(
        entitaeten=[EntitaetAusgabe(**e.__dict__) for e in graph.entitaeten],
        beziehungen=[BeziehungAusgabe(**b.__dict__) for b in graph.beziehungen],
    )


@router.get("/graph", response_model=GraphAusgabe)
async def lade_graph() -> GraphAusgabe:
    graph = await _dienst.lade()
    return GraphAusgabe(
        entitaeten=[EntitaetAusgabe(**e.__dict__) for e in graph.entitaeten],
        beziehungen=[BeziehungAusgabe(**b.__dict__) for b in graph.beziehungen],
    )


@router.delete("/graph", status_code=status.HTTP_204_NO_CONTENT)
async def loesche_graph() -> None:
    await _dienst.loesche_alles()


@router.post("/abfrage")
async def abfrage(anfrage: AbfrageAnfrage) -> dict[str, str]:
    return {"antwort": await _dienst.abfrage(anfrage.frage)}
