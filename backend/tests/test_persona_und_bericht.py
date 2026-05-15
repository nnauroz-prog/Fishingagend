"""Tests für PersonaDienst, BerichtDienst und GraphRAGDienst (mit Mock-LLM)."""

from __future__ import annotations

import json

import pytest

from app.dienste.bericht_dienst import BerichtDienst
from app.dienste.graphrag_dienst import GraphRAGDienst
from app.dienste.llm_dienst import MockLLMDienst
from app.dienste.persona_dienst import PersonaDienst
from app.modelle.simulation import Simulation, SimulationSchritt, SimulationStatus


async def test_persona_dienst_parst_llm_json() -> None:
    mock = MockLLMDienst(
        antworten=[
            json.dumps(
                {
                    "name": "Lara Kessler",
                    "alter": 41,
                    "beruf": "Architektin",
                    "hintergrund": "Studium in Zürich, eigene Firma seit 2018.",
                    "werte": ["Nachhaltigkeit", "Klarheit"],
                    "charakterzuege": ["pragmatisch"],
                    "sprachstil": "knapp",
                }
            )
        ]
    )
    persona = await PersonaDienst(llm=mock).generiere({"thema": "Stadtplanung"})
    assert persona.name == "Lara Kessler"
    assert persona.alter == 41
    assert "Nachhaltigkeit" in persona.werte


async def test_persona_dienst_toleriert_markdown_fences() -> None:
    mock = MockLLMDienst(
        antworten=['```json\n{"name": "Tim", "werte": [], "charakterzuege": []}\n```']
    )
    persona = await PersonaDienst(llm=mock).generiere({})
    assert persona.name == "Tim"


async def test_bericht_dienst_baut_anweisung_und_ruft_llm_auf() -> None:
    mock = MockLLMDienst(antworten=["# Zusammenfassung\nAlles lief gut."])
    sim = Simulation(
        name="Demo",
        agent_ids=["a"],
        schritte=1,
        status=SimulationStatus.ABGESCHLOSSEN,
        verlauf=[
            SimulationSchritt(nummer=1, welt="kontrolle", ereignisse=["Anna: läuft."])
        ],
    )
    text = await BerichtDienst(llm=mock).erstelle_bericht(sim)
    assert text.startswith("# Zusammenfassung")
    # System-Prompt fest, Anweisung enthält die Sim-Daten
    system, verlauf = mock.aufrufe[0]
    assert "Multi-Agenten-Simulationen" in system
    nutzer = verlauf[-1]["content"]
    assert "Demo" in nutzer and "kontrolle" in nutzer


async def test_graphrag_extrahiert_und_dedupliziert(isolierte_datenbank) -> None:
    antwort = json.dumps(
        {
            "entitaeten": [
                {"name": "Alice", "typ": "Person", "beschreibung": "Forscherin"},
                {"name": "ETH", "typ": "Organisation", "beschreibung": ""},
            ],
            "beziehungen": [
                {"von": "Alice", "nach": "ETH", "art": "arbeitet_bei", "gewicht": 0.9}
            ],
        }
    )
    mock = MockLLMDienst(antworten=[antwort, antwort])  # zweimal denselben Inhalt
    dienst = GraphRAGDienst(llm=mock)
    graph = await dienst.extrahiere(
        ["Alice forscht an der ETH.", "Alice arbeitet an der ETH."]
    )
    # Deduplizierung: trotz zweier Texte nur 2 Entitäten und 1 Beziehung
    assert len(graph.entitaeten) == 2
    assert len(graph.beziehungen) == 1
    # Der Graph wurde persistiert und laesst sich erneut laden
    erneut = await dienst.lade()
    assert len(erneut.entitaeten) == 2


@pytest.mark.parametrize(
    "eingabe,erwartet",
    [
        ("```json\n{\"a\": 1}\n```", {"a": 1}),
        ("Vorrede {\"b\": 2} Nachrede", {"b": 2}),
    ],
)
async def test_llm_json_parsing_robust(eingabe: str, erwartet: dict) -> None:
    mock = MockLLMDienst(antworten=[eingabe])
    daten = await mock.antworte_json("sys", "frag")
    assert daten == erwartet
