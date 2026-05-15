"""Tests für die Simulations-Endpunkte."""

from __future__ import annotations


async def test_plane_und_starte_simulation(client) -> None:
    sim_eingabe = {
        "name": "Klima-Szenario A",
        "beschreibung": "Test-Lauf",
        "agent_ids": ["a-1", "a-2"],
        "schritte": 3,
        "variable": {"temperatur_anstieg": 1.5},
        "dual_modus": True,
    }
    geplant = await client.post("/api/simulation", json=sim_eingabe)
    assert geplant.status_code == 201
    sim = geplant.json()
    assert sim["status"] == "geplant"

    gestartet = await client.post(f"/api/simulation/{sim['id']}/starte")
    assert gestartet.status_code == 200
    fertig = gestartet.json()
    assert fertig["status"] == "abgeschlossen"
    # 3 Schritte × 2 Welten = 6 Einträge
    assert len(fertig["verlauf"]) == 6
