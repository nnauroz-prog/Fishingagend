"""Tests für die Agenten-Endpunkte."""

from __future__ import annotations


async def test_erstelle_und_lese_agent(client) -> None:
    eingabe = {
        "persona": {
            "name": "Anna Schmidt",
            "beruf": "Forscherin",
            "hintergrund": "Promotion in Soziologie",
            "werte": ["Neugier", "Ehrlichkeit"],
            "charakterzuege": ["analytisch"],
            "sprachstil": "fachlich",
        }
    }
    erstellt = await client.post("/api/agenten", json=eingabe)
    assert erstellt.status_code == 201
    agent = erstellt.json()
    assert agent["persona"]["name"] == "Anna Schmidt"

    geholt = await client.get(f"/api/agenten/{agent['id']}")
    assert geholt.status_code == 200
    assert geholt.json()["id"] == agent["id"]


async def test_unbekannter_agent_liefert_404(client) -> None:
    antwort = await client.get("/api/agenten/gibt-es-nicht")
    assert antwort.status_code == 404
