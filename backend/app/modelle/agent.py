"""Agenten-Modelle."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from app.modelle.persona import Persona


class AgentErstellen(BaseModel):
    """Eingabe zum Anlegen eines neuen Agenten."""

    persona: Persona
    notizen: str | None = None


class Agent(BaseModel):
    """Vollständiger Agent inkl. Metadaten."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    persona: Persona
    notizen: str | None = None
    erstellt_am: datetime = Field(default_factory=datetime.utcnow)
    aktualisiert_am: datetime = Field(default_factory=datetime.utcnow)
    gedaechtnis_id: str | None = Field(
        default=None,
        description="Verweis auf den externen Gedächtnis-Speicher",
    )
