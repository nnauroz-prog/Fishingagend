"""Test des SSE-Chat-Endpunkts."""

from __future__ import annotations


async def _erstelle_agent(client) -> str:
    antwort = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "Anna",
                "hintergrund": "Test",
                "werte": [],
                "charakterzuege": [],
                "sprachstil": "neutral",
                "beziehungen": {},
            }
        },
    )
    assert antwort.status_code == 201
    return antwort.json()["id"]


async def test_chat_strom_emittiert_delta_und_fertig(client) -> None:
    agent_id = await _erstelle_agent(client)
    async with client.stream(
        "POST",
        "/api/chat/strom",
        json={"agent_id": agent_id, "nachricht": "Hi"},
    ) as antwort:
        assert antwort.status_code == 200
        assert antwort.headers["content-type"].startswith("text/event-stream")
        text = ""
        async for chunk in antwort.aiter_text():
            text += chunk
    assert "event: delta" in text
    assert "event: fertig" in text
    assert "Mock-Antwort" in text


async def test_chat_strom_unbekannter_agent_404(client) -> None:
    antwort = await client.post(
        "/api/chat/strom",
        json={"agent_id": "gibts-nicht", "nachricht": "Hi"},
    )
    assert antwort.status_code == 404
