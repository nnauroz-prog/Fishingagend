"""Persona-Modell — beschreibt die Persönlichkeit eines Agenten."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Persona(BaseModel):
    """Charakter eines simulierten Agenten."""

    name: str = Field(description="Anzeigename")
    alter: int | None = Field(default=None, ge=0, le=150)
    beruf: str | None = None
    hintergrund: str = Field(default="", description="Lebenslauf, Erfahrungen")
    werte: list[str] = Field(default_factory=list, description="Wichtige Werte und Überzeugungen")
    charakterzuege: list[str] = Field(default_factory=list, description="Z. B. extrovertiert, vorsichtig")
    beziehungen: dict[str, str] = Field(
        default_factory=dict,
        description="Abbildung Agent-ID → Beschreibung der Beziehung",
    )
    sprachstil: str = Field(default="neutral", description="Z. B. förmlich, salopp, fachlich")
