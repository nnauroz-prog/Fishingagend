"""Tests für den Berichts-Endpunkt."""

from __future__ import annotations


async def test_bericht_unbekannte_simulation_404(client) -> None:
    antwort = await client.get("/api/berichte/gibts-nicht")
    assert antwort.status_code == 404


async def test_bericht_liefert_markdown_fuer_abgeschlossene_simulation(client) -> None:
    # Agent
    a = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "Anna",
                "hintergrund": "",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {},
                "sprachstil": "neutral",
            }
        },
    )
    agent_id = a.json()["id"]

    # Simulation planen + sofort starten
    s = await client.post(
        "/api/simulation",
        json={
            "name": "Mini",
            "agent_ids": [agent_id],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
        },
    )
    sim_id = s.json()["id"]
    await client.post(f"/api/simulation/{sim_id}/starte?sofort=true")

    # Bericht
    b = await client.get(f"/api/berichte/{sim_id}")
    assert b.status_code == 200
    daten = b.json()
    assert daten["simulation_id"] == sim_id
    assert isinstance(daten["markdown"], str)
    assert len(daten["markdown"]) > 0
