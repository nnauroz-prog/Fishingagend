"""Tests fuer die Pagination auf Listen-Endpunkten."""

from __future__ import annotations


async def _agent(client, name: str) -> None:
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
    assert r.status_code == 201


async def test_agenten_pagination(client) -> None:
    for i in range(7):
        await _agent(client, f"Agent {i}")

    seite1 = await client.get("/api/agenten?limit=3&offset=0")
    seite2 = await client.get("/api/agenten?limit=3&offset=3")
    seite3 = await client.get("/api/agenten?limit=3&offset=6")
    assert len(seite1.json()) == 3
    assert len(seite2.json()) == 3
    assert len(seite3.json()) == 1


async def test_pagination_lehnt_negative_werte_ab(client) -> None:
    r = await client.get("/api/agenten?limit=0")
    assert r.status_code == 422
    r = await client.get("/api/agenten?offset=-1")
    assert r.status_code == 422
