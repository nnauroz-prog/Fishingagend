"""Test fuer Batch-Sim-Endpunkt."""

from __future__ import annotations


async def test_batch_legt_n_simulationen_an(client) -> None:
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
        "/api/simulation/batch",
        json={
            "vorlage": {
                "name": "Sensitivitaet",
                "agent_ids": [aid],
                "schritte": 1,
                "variable": {},
                "dual_modus": False,
            },
            "variablen_serie": [
                {"temp": 1.0},
                {"temp": 1.5},
                {"temp": 2.0},
            ],
            "sofort_starten": False,
        },
    )
    assert r.status_code == 200
    daten = r.json()
    assert len(daten) == 3
    assert daten[0]["name"].endswith("#1")
    assert daten[2]["name"].endswith("#3")
    assert daten[0]["variable"] == {"temp": 1.0}
    assert daten[2]["variable"] == {"temp": 2.0}
    assert all(s["status"] == "geplant" for s in daten)


async def test_batch_lehnt_leere_serie_ab(client) -> None:
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
    r = await client.post(
        "/api/simulation/batch",
        json={
            "vorlage": {
                "name": "Leer",
                "agent_ids": [a.json()["id"]],
                "schritte": 1,
                "variable": {},
                "dual_modus": False,
            },
            "variablen_serie": [],
        },
    )
    assert r.status_code == 422
