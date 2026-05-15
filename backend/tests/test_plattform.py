"""Tests für die Plattform-Simulation (Posts/Reaktionen/Folgen)."""

from __future__ import annotations

import json


async def _agent(client, name: str) -> str:
    r = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": name,
                "hintergrund": "Test",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {},
                "sprachstil": "neutral",
            }
        },
    )
    return r.json()["id"]


async def test_plattform_simulation_erzeugt_posts(client, llm_mock) -> None:
    # Mock: jeder Aufruf liefert eine Posten-Aktion
    llm_mock._antworten = [  # noqa: SLF001
        json.dumps({"aktion": "posten", "inhalt": f"Mein Beitrag {i}"}) for i in range(50)
    ]
    a1 = await _agent(client, "Anna")
    a2 = await _agent(client, "Bert")

    s = await client.post(
        "/api/simulation",
        json={
            "name": "Plattform-Test",
            "agent_ids": [a1, a2],
            "schritte": 2,
            "variable": {},
            "dual_modus": False,
            "plattform_modus": True,
        },
    )
    sid = s.json()["id"]
    f = await client.post(f"/api/simulation/{sid}/starte?sofort=true")
    assert f.status_code == 200
    assert f.json()["status"] == "abgeschlossen"

    feed = (await client.get(f"/api/simulation/{sid}/feed")).json()
    # 2 Schritte * 2 Agenten = 4 Posts (alle posten)
    assert len(feed) == 4
    assert all(eintrag["welt"] == "kontrolle" for eintrag in feed)
    assert {e["autor"] for e in feed} == {"Anna", "Bert"}


async def test_plattform_simulation_reaktionen(client, llm_mock) -> None:
    # Erst einen Post, dann lauter Reaktionen
    llm_mock._antworten = [  # noqa: SLF001
        json.dumps({"aktion": "posten", "inhalt": "Hallo Welt"}),
        json.dumps({"aktion": "reagieren", "beitrag_id": 999, "reaktion": "like"}),
        json.dumps({"aktion": "reagieren", "beitrag_id": 999, "reaktion": "antwort", "antwort": "Stimmt!"}),
        json.dumps({"aktion": "folgen", "ziel": "Anna"}),
    ]
    a1 = await _agent(client, "Anna")
    a2 = await _agent(client, "Bert")
    a3 = await _agent(client, "Cleo")
    a4 = await _agent(client, "Dirk")

    s = await client.post(
        "/api/simulation",
        json={
            "name": "Reaktionen",
            "agent_ids": [a1, a2, a3, a4],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
            "plattform_modus": True,
        },
    )
    sid = s.json()["id"]
    await client.post(f"/api/simulation/{sid}/starte?sofort=true")

    feed = (await client.get(f"/api/simulation/{sid}/feed")).json()
    # Mindestens ein Post mit Reaktionen
    posts = [e for e in feed if e["reaktionen"]]
    assert posts, "Erwartet mindestens einen Post mit Reaktionen"

    folgt = (await client.get(f"/api/simulation/{sid}/folgen")).json()
    assert any(f["gefolgter"] == "Anna" for f in folgt)
