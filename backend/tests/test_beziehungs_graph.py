"""Test fuer den Beziehungs-Graph-Endpunkt."""

from __future__ import annotations


async def test_leerer_graph_wenn_keine_beziehungen(client) -> None:
    r = await client.get("/api/agenten/beziehungs-graph")
    assert r.status_code == 200
    daten = r.json()
    assert daten == {"knoten": [], "kanten": []}


async def test_graph_enthaelt_agenten_und_externe_kanten(client) -> None:
    a = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "Anna",
                "hintergrund": "",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {
                    "Bert": "freundlich",
                    "Externer Mensch": "kennt sie aus dem Studium",
                },
                "sprachstil": "neutral",
            }
        },
    )
    assert a.status_code == 201
    await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "Bert",
                "hintergrund": "",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {},
                "sprachstil": "neutral",
            }
        },
    )

    r = await client.get("/api/agenten/beziehungs-graph")
    daten = r.json()
    namen = {k["id"]: k["typ"] for k in daten["knoten"]}
    assert namen.get("Anna") == "agent"
    assert namen.get("Bert") == "agent"
    assert namen.get("Externer Mensch") == "extern"
    assert any(
        k["von"] == "Anna" and k["nach"] == "Bert" and k["beschreibung"] == "freundlich"
        for k in daten["kanten"]
    )
