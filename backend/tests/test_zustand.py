"""Test des Zustand-Endpunkts."""

from __future__ import annotations


async def test_zustand_liefert_ok(client) -> None:
    antwort = await client.get("/api/zustand")
    assert antwort.status_code == 200
    daten = antwort.json()
    assert daten["status"] == "ok"
    assert "version" in daten
