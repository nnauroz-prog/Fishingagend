"""Test des Demo-Daten-Saats."""

from __future__ import annotations

from app.config import einstellungen
from app.dienste.agent_dienst import hole_agent_dienst
from app.dienste.demo_dienst import saee_demo_daten


async def test_demo_legt_beispiele_an_wenn_db_leer(isolierte_datenbank, llm_mock) -> None:
    einstellungen.demo_daten_einspielen = True
    try:
        anzahl = await saee_demo_daten()
    finally:
        einstellungen.demo_daten_einspielen = False
    assert anzahl >= 5
    agenten = await hole_agent_dienst().liste()
    namen = {a.persona.name for a in agenten}
    assert "Lisa Weber" in namen
    assert "Markus König" in namen


async def test_demo_idempotent(isolierte_datenbank, llm_mock) -> None:
    await saee_demo_daten()
    zweite = await saee_demo_daten()
    assert zweite == 0
