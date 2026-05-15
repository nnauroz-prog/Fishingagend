"""Tests für die Stimmungs-Analyse."""

from __future__ import annotations

from app.dienste.stimmung_dienst import schritt_stimmung, stimmungs_verlauf
from app.modelle.simulation import Simulation, SimulationSchritt, SimulationStatus


def test_positive_woerter_geben_positiven_score() -> None:
    score = schritt_stimmung(["Anna: Ich freue mich, das ist wunderbar"])
    assert score > 0


def test_negative_woerter_geben_negativen_score() -> None:
    score = schritt_stimmung(["Bert: Das ist ein Problem, ich habe Angst und Wut"])
    assert score < 0


def test_neutrale_ohne_treffer() -> None:
    assert schritt_stimmung(["Bert: heute regnet es"]) == 0.0


def test_stimmungs_verlauf_gruppiert_je_welt() -> None:
    sim = Simulation(
        name="X",
        agent_ids=["a"],
        schritte=2,
        status=SimulationStatus.ABGESCHLOSSEN,
        verlauf=[
            SimulationSchritt(nummer=1, welt="kontrolle", ereignisse=["Anna: gut"]),
            SimulationSchritt(nummer=1, welt="variante", ereignisse=["Anna: schlecht"]),
            SimulationSchritt(nummer=2, welt="kontrolle", ereignisse=["Anna: super klasse"]),
            SimulationSchritt(nummer=2, welt="variante", ereignisse=["Anna: Konflikt"]),
        ],
    )
    v = stimmungs_verlauf(sim)
    assert v["kontrolle"][0]["score"] > 0
    assert v["variante"][0]["score"] < 0
    assert v["kontrolle"][1]["schritt"] == 2


async def test_stimmungs_endpunkt(client) -> None:
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
            "name": "Test",
            "agent_ids": [a.json()["id"]],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
        },
    )
    sid = s.json()["id"]
    await client.post(f"/api/simulation/{sid}/starte?sofort=true")
    r = await client.get(f"/api/simulation/{sid}/stimmung")
    assert r.status_code == 200
    assert "kontrolle" in r.json()
