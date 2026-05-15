"""Tests fuer den Lern-Dienst (Reflexionen, Beziehungen, Konsolidierung,
Praeferenzen)."""

from __future__ import annotations

import json


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


async def test_reflexion_landet_im_gedaechtnis_nach_sim(client, llm_mock) -> None:
    # Nach Sim ruft der LernDienst pro Agent: Reflexion, Beziehungen, Konsolidierung
    # Mock-Antworten so setzen, dass Reflexion nicht-leer ist:
    llm_mock._antworten = ["Habe heute viel zugehoert."] * 100  # noqa: SLF001
    a = await _agent(client, "Anna")
    s = await client.post(
        "/api/simulation",
        json={
            "name": "Lern-Test",
            "agent_ids": [a],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
        },
    )
    sid = s.json()["id"]
    await client.post(f"/api/simulation/{sid}/starte?sofort=true")

    r = await client.get(f"/api/agenten/{a}/reflexionen")
    assert r.status_code == 200
    refs = r.json()
    assert any("[Reflexion" in r for r in refs), f"Erwartet Reflexionen, hatte: {refs}"


async def test_beziehungen_werden_aus_sim_gelernt(client, llm_mock) -> None:
    # Mock-Antworten: zuerst Sim-Aktionen, dann fuer Lern-Phase
    # Reflexion (text), Beziehungs-JSON
    llm_mock._antworten = [  # noqa: SLF001
        "Begruesst Bert.",          # Sim-Aktion Anna
        "Begruesst Anna.",          # Sim-Aktion Bert
        "Reflexion text",           # Anna Reflexion
        json.dumps({"beziehungen": {"Bert": "freundlich, sympathisch"}}),
        "Reflexion text",           # Bert Reflexion
        json.dumps({"beziehungen": {"Anna": "vertrauensvoll"}}),
    ]
    a1 = await _agent(client, "Anna")
    a2 = await _agent(client, "Bert")
    s = await client.post(
        "/api/simulation",
        json={
            "name": "Beziehungs-Test",
            "agent_ids": [a1, a2],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
        },
    )
    await client.post(f"/api/simulation/{s.json()['id']}/starte?sofort=true")

    a1_neu = (await client.get(f"/api/agenten/{a1}")).json()
    a2_neu = (await client.get(f"/api/agenten/{a2}")).json()
    assert "Bert" in a1_neu["persona"]["beziehungen"]
    assert "Anna" in a2_neu["persona"]["beziehungen"]
    assert "freundlich" in a1_neu["persona"]["beziehungen"]["Bert"]


async def test_praeferenzen_zaehlt_haeufige_begriffe(client) -> None:
    a = await _agent(client, "Lara")
    # Manuell Memory befuellen
    for inhalt in [
        "Treffen mit Markus zur Klima-Konferenz.",
        "Markus hat einen Vorschlag zur CO2-Reduktion gemacht.",
        "Konferenz war erfolgreich, Klima-Aktion startet bald.",
    ]:
        await client.post(f"/api/agenten/{a}/gedaechtnis", json={"inhalt": inhalt})

    r = await client.get(f"/api/agenten/{a}/praeferenzen")
    assert r.status_code == 200
    daten = r.json()
    # "Markus" als Person, "klima" oder "konferenz" als Begriff
    namen = {p["name"] for p in daten["personen"]}
    assert "Markus" in namen
    assert daten["episoden"] == 3


async def test_konsolidierung_wird_bei_vielen_episoden_ausgefuehrt(client, llm_mock) -> None:
    # Erst Memory aufblasen, dann eine Sim — Konsolidierung sollte greifen
    llm_mock._antworten = [  # noqa: SLF001
        "Aktion",  # Sim-Aktion
        "Reflexion",  # Reflexion
        json.dumps({"beziehungen": {}}),  # Beziehungen (leer)
        "Zusammenfassung der aelteren Erinnerungen.",  # Konsolidierung
    ]
    a = await _agent(client, "Klaus")
    # 60 Memory-Einträge anlegen
    for i in range(60):
        await client.post(f"/api/agenten/{a}/gedaechtnis", json={"inhalt": f"Eintrag {i}"})

    vorher = await client.get(f"/api/agenten/{a}/gedaechtnis?grenze=10000")
    assert len(vorher.json()) == 60

    # Eine Sim laufen lassen → Lern-Phase greift
    s = await client.post(
        "/api/simulation",
        json={
            "name": "Konsolidierung",
            "agent_ids": [a],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
        },
    )
    await client.post(f"/api/simulation/{s.json()['id']}/starte?sofort=true")

    nachher = await client.get(f"/api/agenten/{a}/gedaechtnis?grenze=10000")
    eintraege = nachher.json()
    # 60 -> 25 behalten + 1 Zusammenfassung + 1 Sim-Aktion + 1 Reflexion = 28
    assert len(eintraege) < 60
    assert any(e.startswith("[Zusammenfassung]") for e in eintraege)
