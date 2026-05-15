"""Tests für den Chat-Endpunkt."""

from __future__ import annotations


async def test_chat_mit_unbekanntem_agent_gibt_404(client) -> None:
    antwort = await client.post(
        "/api/chat",
        json={"agent_id": "gibt-es-nicht", "nachricht": "Hallo"},
    )
    assert antwort.status_code == 404


async def test_chat_liefert_mock_antwort_und_speichert_gedaechtnis(client, llm_mock) -> None:
    erstellt = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "Klara",
                "beruf": "Juristin",
                "hintergrund": "Vertretung im Verwaltungsrecht.",
                "werte": ["Genauigkeit"],
                "charakterzuege": ["sachlich"],
                "sprachstil": "fachlich",
                "beziehungen": {},
            }
        },
    )
    agent_id = erstellt.json()["id"]

    antwort = await client.post(
        "/api/chat",
        json={"agent_id": agent_id, "nachricht": "Wie geht's?"},
    )
    assert antwort.status_code == 200
    daten = antwort.json()
    assert daten["antwort"] == "Mock-Antwort 1."
    assert daten["nachricht"]["rolle"] == "agent"

    # Persona-Block muss im Mock-Aufruf enthalten sein
    system = llm_mock.aufrufe[-1][0]
    assert "Klara" in system
    assert "Juristin" in system
