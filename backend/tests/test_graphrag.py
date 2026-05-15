"""Tests fuer die GraphRAG-Endpunkte mit Persistenz."""

from __future__ import annotations

import json


async def test_graphrag_extrahieren_und_laden(client, llm_mock) -> None:
    llm_mock._antworten = [  # noqa: SLF001
        json.dumps(
            {
                "entitaeten": [
                    {"name": "Anna", "typ": "Person", "beschreibung": "Forscherin"},
                    {"name": "ETH", "typ": "Organisation", "beschreibung": ""},
                ],
                "beziehungen": [
                    {"von": "Anna", "nach": "ETH", "art": "arbeitet_bei", "gewicht": 0.9}
                ],
            }
        )
    ]

    r = await client.post("/api/graphrag/extrahieren", json={"texte": ["Anna ist an der ETH."]})
    assert r.status_code == 200
    daten = r.json()
    assert len(daten["entitaeten"]) == 2
    assert len(daten["beziehungen"]) == 1

    # Persistiert: GET /graph liefert dasselbe
    g = await client.get("/api/graphrag/graph")
    assert g.status_code == 200
    assert len(g.json()["entitaeten"]) == 2


async def test_graphrag_loeschen_leert_die_db(client, llm_mock) -> None:
    llm_mock._antworten = [  # noqa: SLF001
        json.dumps({"entitaeten": [{"name": "X", "typ": "Konzept"}], "beziehungen": []})
    ]
    await client.post("/api/graphrag/extrahieren", json={"texte": ["X"]})
    r = await client.delete("/api/graphrag/graph")
    assert r.status_code == 204
    g = await client.get("/api/graphrag/graph")
    assert g.json()["entitaeten"] == []


async def test_graphrag_abfrage_bei_leerem_graph(client, llm_mock) -> None:
    r = await client.post("/api/graphrag/abfrage", json={"frage": "Wer arbeitet wo?"})
    assert r.status_code == 200
    assert "leer" in r.json()["antwort"].lower()
