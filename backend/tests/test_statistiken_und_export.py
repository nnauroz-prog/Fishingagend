"""Tests fuer Statistik- und Export-Endpunkte."""

from __future__ import annotations


async def _agent(client, name: str) -> str:
    r = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": name,
                "hintergrund": "",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {},
                "sprachstil": "neutral",
            }
        },
    )
    return r.json()["id"]


async def test_statistiken_zaehlt_korrekt(client) -> None:
    leer = (await client.get("/api/statistiken")).json()
    assert leer["agenten"] == 0
    assert leer["simulationen"] == 0

    a = await _agent(client, "X")
    await client.post(
        "/api/simulation",
        json={
            "name": "S",
            "agent_ids": [a],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
        },
    )
    voll = (await client.get("/api/statistiken")).json()
    assert voll["agenten"] == 1
    assert voll["simulationen"] == 1
    assert voll["simulationen_nach_status"] == {"geplant": 1}


async def test_agent_aktualisieren(client) -> None:
    a = await _agent(client, "Original")
    neu = {
        "name": "Geaendert",
        "alter": 50,
        "beruf": "Neu",
        "hintergrund": "Anderer Hintergrund",
        "werte": ["A"],
        "charakterzuege": ["B"],
        "beziehungen": {},
        "sprachstil": "knapp",
    }
    r = await client.put(f"/api/agenten/{a}", json=neu)
    assert r.status_code == 200
    daten = r.json()
    assert daten["persona"]["name"] == "Geaendert"
    assert daten["persona"]["beruf"] == "Neu"


async def test_simulation_export(client) -> None:
    a = await _agent(client, "X")
    s = await client.post(
        "/api/simulation",
        json={
            "name": "Export-Test",
            "agent_ids": [a],
            "schritte": 1,
            "variable": {"k": "v"},
            "dual_modus": False,
        },
    )
    sid = s.json()["id"]
    await client.post(f"/api/simulation/{sid}/starte?sofort=true")
    r = await client.get(f"/api/simulation/{sid}/export")
    assert r.status_code == 200
    daten = r.json()
    assert daten["id"] == sid
    assert daten["name"] == "Export-Test"
    assert "verlauf" in daten
