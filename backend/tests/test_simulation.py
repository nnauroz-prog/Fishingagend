"""Tests für die Simulations-Endpunkte."""

from __future__ import annotations


async def _erzeuge_agent(client, name: str) -> str:
    antwort = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": name,
                "beruf": "Tester",
                "hintergrund": "Erzeugt für die Test-Suite.",
                "werte": ["Klarheit"],
                "charakterzuege": ["analytisch"],
                "sprachstil": "knapp",
                "beziehungen": {},
            }
        },
    )
    assert antwort.status_code == 201
    return antwort.json()["id"]


async def test_plane_simulation(client) -> None:
    a1 = await _erzeuge_agent(client, "Anna")
    a2 = await _erzeuge_agent(client, "Bert")
    geplant = await client.post(
        "/api/simulation",
        json={
            "name": "Klima-Szenario A",
            "beschreibung": "Test-Lauf",
            "agent_ids": [a1, a2],
            "schritte": 2,
            "variable": {"temperatur_anstieg": 1.5},
            "dual_modus": True,
        },
    )
    assert geplant.status_code == 201
    sim = geplant.json()
    assert sim["status"] == "geplant"
    assert sim["agent_ids"] == [a1, a2]


async def test_starte_simulation_synchron(client, llm_mock) -> None:
    a1 = await _erzeuge_agent(client, "Anna")
    plan = await client.post(
        "/api/simulation",
        json={
            "name": "Mini",
            "agent_ids": [a1],
            "schritte": 2,
            "variable": {"x": 1},
            "dual_modus": True,
        },
    )
    sim_id = plan.json()["id"]

    fertig = await client.post(f"/api/simulation/{sim_id}/starte?sofort=true")
    assert fertig.status_code == 200
    daten = fertig.json()
    assert daten["status"] == "abgeschlossen"
    # 2 Schritte × 2 Welten = 4 Schritt-Einträge
    assert len(daten["verlauf"]) == 4
    assert any("Mock-Antwort" in e for s in daten["verlauf"] for e in s["ereignisse"])
    # Pro Schritt × Welt × Agent = 1 LLM-Aufruf, also 2*2*1 = 4
    assert len(llm_mock.aufrufe) >= 4
