"""Tests fuer Einstellungs-Endpunkt und Anforderungs-Parsing."""

from __future__ import annotations

import json


async def test_einstellungen_zeigt_konfig_ohne_secrets(client) -> None:
    r = await client.get("/api/einstellungen")
    assert r.status_code == 200
    daten = r.json()
    assert daten["llm"]["provider"] in {"anthropic", "openai"}
    # Keys werden nur als Boolean exponiert
    assert isinstance(daten["llm"]["anthropic_api_key_gesetzt"], bool)
    assert isinstance(daten["llm"]["openai_api_key_gesetzt"], bool)
    assert daten["datenbank_dialekt"] == "sqlite"


async def test_aus_text_schlaegt_konfiguration_vor(client, llm_mock) -> None:
    # 2 Agenten anlegen, deren Namen das LLM zurueckgeben kann
    for name in ["Anna", "Bert"]:
        await client.post(
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

    llm_mock._antworten = [  # noqa: SLF001
        json.dumps(
            {
                "name": "Klima-Lauf",
                "beschreibung": "Diskussion zur Klima-Wende",
                "schritte": 4,
                "variable": {"co2_ziel": "minus 50%"},
                "dual_modus": True,
                "plattform_modus": True,
                "agent_namen": ["Anna", "Bert"],
            }
        )
    ]

    r = await client.post(
        "/api/simulation/aus-text",
        json={"beschreibung": "Ich will eine Diskussion zur CO2-Reduktion sehen."},
    )
    assert r.status_code == 200
    daten = r.json()
    assert daten["name"] == "Klima-Lauf"
    assert daten["schritte"] == 4
    assert daten["plattform_modus"] is True
    assert len(daten["agent_ids"]) == 2


async def test_aus_text_ohne_agenten_400(client, llm_mock) -> None:
    llm_mock._antworten = [json.dumps({"agent_namen": []})]
    r = await client.post(
        "/api/simulation/aus-text",
        json={"beschreibung": "Egal, geht eh schief"},
    )
    assert r.status_code == 400
