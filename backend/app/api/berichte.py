"""Berichts-Endpunkte — Markdown-Bericht und Chat mit dem Berichts-Agent."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dienste.bericht_dienst import BerichtDienst
from app.dienste.simulation_dienst import SimulationDienst, hole_simulation_dienst
from app.modelle.chat import Nachricht

router = APIRouter()


def hole_bericht_dienst() -> BerichtDienst:
    return BerichtDienst()


@router.get("/{sim_id}")
async def bericht(
    sim_id: str,
    sim_dienst: SimulationDienst = Depends(hole_simulation_dienst),
    bericht_dienst: BerichtDienst = Depends(hole_bericht_dienst),
) -> dict[str, str]:
    sim = await sim_dienst.hole(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    inhalt = await bericht_dienst.erstelle_bericht(sim)
    return {"simulation_id": sim_id, "markdown": inhalt}


class BerichtChatAnfrage(BaseModel):
    nachricht: str = Field(min_length=1, max_length=4000)
    verlauf: list[Nachricht] = Field(default_factory=list)


@router.post("/{sim_id}/chat")
async def bericht_chat(
    sim_id: str,
    anfrage: BerichtChatAnfrage,
    sim_dienst: SimulationDienst = Depends(hole_simulation_dienst),
    bericht_dienst: BerichtDienst = Depends(hole_bericht_dienst),
) -> dict[str, str]:
    """Chatte mit dem Berichts-Agent ueber eine Simulation — er nutzt
    Werkzeuge, um konkrete Aggregate aus dem Verlauf zu ziehen."""
    sim = await sim_dienst.hole(sim_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation nicht gefunden")
    verlauf = [
        {"role": "user" if n.rolle == "nutzer" else "assistant", "content": n.inhalt}
        for n in anfrage.verlauf
    ]
    antwort = await bericht_dienst.chatte(sim, verlauf, anfrage.nachricht)
    return {"antwort": antwort}
