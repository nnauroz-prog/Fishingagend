"""GraphRAG-Endpunkte — Aufbau & Abfrage des Wissensgraphen."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.dienste.graphrag_dienst import GraphRAGDienst

router = APIRouter()


class ExtraktionsAnfrage(BaseModel):
    texte: list[str] = Field(min_length=1)


class AbfrageAnfrage(BaseModel):
    frage: str


_dienst = GraphRAGDienst()


@router.post("/extrahieren")
async def extrahiere(anfrage: ExtraktionsAnfrage) -> dict[str, int]:
    graph = await _dienst.extrahiere(anfrage.texte)
    return {
        "entitaeten": len(graph.entitaeten),
        "beziehungen": len(graph.beziehungen),
    }


@router.post("/abfrage")
async def abfrage(_anfrage: AbfrageAnfrage) -> dict[str, str]:
    # Stub: später mit echtem Graphen
    return {"antwort": "Noch nicht implementiert."}
