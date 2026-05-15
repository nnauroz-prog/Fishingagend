"""Chat-Modelle."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Rolle = Literal["nutzer", "agent", "system"]


class Nachricht(BaseModel):
    rolle: Rolle
    inhalt: str
    zeitstempel: datetime = Field(default_factory=datetime.utcnow)


class ChatAnfrage(BaseModel):
    agent_id: str
    nachricht: str = Field(min_length=1, max_length=8000)
    verlauf: list[Nachricht] = Field(default_factory=list)


class ChatAntwort(BaseModel):
    agent_id: str
    antwort: str
    nachricht: Nachricht
    eingangs_token: int = 0
    ausgangs_token: int = 0
