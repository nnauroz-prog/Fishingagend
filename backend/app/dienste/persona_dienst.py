"""Persona-Generierung aus dem Knowledge-Graph (Stub)."""

from __future__ import annotations

from app.dienste.llm_dienst import hole_llm_dienst
from app.modelle.persona import Persona


class PersonaDienst:
    """Erzeugt aus Saat-Daten und Graph-Knoten eine plausible Persona."""

    async def generiere(self, saat: dict[str, str]) -> Persona:
        """Stub-Implementierung — der LLM-Aufruf ist vorbereitet, aber deaktiviert.

        Sobald ein API-Key gesetzt ist, kann der untenstehende Block aktiviert
        werden, um echte Personas zu erzeugen.
        """
        # llm = hole_llm_dienst()
        # antwort = await llm.antworte(
        #     system_prompt="Du bist ein Persona-Designer ...",
        #     verlauf=[{"role": "user", "content": json.dumps(saat)}],
        # )
        _ = hole_llm_dienst  # nur, damit der Import nicht ungenutzt ist
        return Persona(
            name=saat.get("name", "Unbenannt"),
            beruf=saat.get("beruf"),
            hintergrund=saat.get("hintergrund", ""),
            werte=saat.get("werte", "").split(",") if saat.get("werte") else [],
            charakterzuege=[],
            sprachstil="neutral",
        )
