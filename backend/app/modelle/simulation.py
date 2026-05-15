"""Simulations-Modelle."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

WeltTyp = Literal["kontrolle", "variante"]


class SimulationStatus(str, Enum):
    GEPLANT = "geplant"
    LAEUFT = "laeuft"
    ABGESCHLOSSEN = "abgeschlossen"
    FEHLGESCHLAGEN = "fehlgeschlagen"


class SimulationErstellen(BaseModel):
    """Eingabe zum Anlegen einer neuen Simulation."""

    name: str = Field(min_length=1, max_length=200)
    beschreibung: str = ""
    agent_ids: list[str] = Field(min_length=1)
    schritte: int = Field(default=20, ge=1, le=1000)
    variable: dict[str, Any] = Field(
        default_factory=dict,
        description="Eingespeiste Variable, die die Welt beeinflusst",
    )
    dual_modus: bool = Field(
        default=True,
        description="Zwei parallele Welten — eine Kontroll-, eine Variantenwelt",
    )


class SimulationSchritt(BaseModel):
    nummer: int
    welt: WeltTyp = "kontrolle"
    ereignisse: list[str] = Field(default_factory=list)
    agent_zustaende: dict[str, str] = Field(default_factory=dict)


class Simulation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    beschreibung: str = ""
    agent_ids: list[str]
    schritte: int
    variable: dict[str, Any] = Field(default_factory=dict)
    dual_modus: bool = True
    status: SimulationStatus = SimulationStatus.GEPLANT
    erstellt_am: datetime = Field(default_factory=datetime.utcnow)
    verlauf: list[SimulationSchritt] = Field(default_factory=list)
