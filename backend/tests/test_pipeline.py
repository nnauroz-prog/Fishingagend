"""Tests für die 5-Phasen-Pipeline (Aus-Graph, Memory-Injection, Bericht-Chat)."""

from __future__ import annotations

import json


async def test_aus_graph_legt_personen_als_agenten_an(client, llm_mock) -> None:
    # Phase 1: Graph mit zwei Personen befüllen
    llm_mock._antworten = [  # noqa: SLF001
        json.dumps(
            {
                "entitaeten": [
                    {"name": "Mara", "typ": "Person", "beschreibung": "Forscherin"},
                    {"name": "Jonas", "typ": "Person", "beschreibung": "Aktivist"},
                    {"name": "Berlin", "typ": "Ort", "beschreibung": ""},
                ],
                "beziehungen": [],
            }
        )
    ]
    await client.post("/api/graphrag/extrahieren", json={"texte": ["Mara und Jonas in Berlin."]})

    # Phase 2: Personas via LLM aus dem Graph ziehen — Mock liefert nur einen Default,
    # also haben beide den Mock-Persona-Namen, aber es entstehen zwei Agenten.
    r = await client.post("/api/agenten/aus-graph", json={"max_personen": 5})
    assert r.status_code == 200
    angelegt = r.json()
    # Zwei Person-Entitaeten -> zwei Agenten
    assert len(angelegt) == 2
    # Sie sind persistiert
    liste = await client.get("/api/agenten")
    assert len(liste.json()) >= 2


async def test_memory_injection_persistiert_episode(client) -> None:
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
    aid = a.json()["id"]

    r = await client.post(
        f"/api/agenten/{aid}/gedaechtnis",
        json={"inhalt": "Hat 2025 ein Buch veröffentlicht."},
    )
    assert r.status_code == 201

    g = await client.get(f"/api/agenten/{aid}/gedaechtnis")
    assert g.status_code == 200
    assert any("Buch" in e for e in g.json())


async def test_temporale_memory_updates_landen_im_gedaechtnis(client, llm_mock) -> None:
    """Aktionen aus der Sim landen automatisch im Agent-Gedaechtnis."""
    erstellt = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "Sim-Tester",
                "hintergrund": "",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {},
                "sprachstil": "neutral",
            }
        },
    )
    aid = erstellt.json()["id"]
    s = await client.post(
        "/api/simulation",
        json={
            "name": "Memory-Test",
            "agent_ids": [aid],
            "schritte": 2,
            "variable": {},
            "dual_modus": False,
        },
    )
    sid = s.json()["id"]
    await client.post(f"/api/simulation/{sid}/starte?sofort=true")

    g = await client.get(f"/api/agenten/{aid}/gedaechtnis")
    assert g.status_code == 200
    eintraege = g.json()
    # 2 Schritte * 1 Welt = 2 Eintraege erwartet
    assert any("Sim-Tester" in e and "Schritt" in e for e in eintraege)


async def test_bericht_chat_nutzt_simulation(client, llm_mock) -> None:
    a = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "X",
                "hintergrund": "",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {},
                "sprachstil": "neutral",
            }
        },
    )
    s = await client.post(
        "/api/simulation",
        json={
            "name": "Chat-Bericht",
            "agent_ids": [a.json()["id"]],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
        },
    )
    sid = s.json()["id"]
    await client.post(f"/api/simulation/{sid}/starte?sofort=true")

    r = await client.post(
        f"/api/berichte/{sid}/chat",
        json={"nachricht": "Wer war am aktivsten?"},
    )
    assert r.status_code == 200
    assert "antwort" in r.json()
    assert isinstance(r.json()["antwort"], str)
