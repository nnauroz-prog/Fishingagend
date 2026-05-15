"""Tests für Vorlagen und Backup/Restore."""

from __future__ import annotations


async def test_vorlagen_liste(client) -> None:
    r = await client.get("/api/vorlagen")
    assert r.status_code == 200
    daten = r.json()
    assert len(daten) >= 5
    schluessel = {v["schluessel"] for v in daten}
    assert "klima_kommune" in schluessel
    assert "krankenhaus_krise" in schluessel


async def test_vorlage_anwenden_legt_agenten_und_sim_an(client) -> None:
    vorher = (await client.get("/api/agenten")).json()
    r = await client.post(
        "/api/vorlagen/klima_kommune/anwenden",
        json={"sofort_starten": False},
    )
    assert r.status_code == 200
    sim = r.json()
    assert sim["name"] == "Klimakrise in der Kommune"
    assert len(sim["agent_ids"]) == 4
    nachher = (await client.get("/api/agenten")).json()
    assert len(nachher) >= len(vorher) + 4


async def test_unbekannte_vorlage_404(client) -> None:
    r = await client.post(
        "/api/vorlagen/gibt-es-nicht/anwenden",
        json={"sofort_starten": False},
    )
    assert r.status_code == 404


async def test_backup_export_und_import_anhaengen(client) -> None:
    # Etwas Inhalt erzeugen
    await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "Sicherung",
                "hintergrund": "",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {},
                "sprachstil": "neutral",
            }
        },
    )

    export = (await client.get("/api/backup/export")).json()
    assert export["version"] == 1
    assert any(
        "Sicherung" in a["persona_json"] for a in export["agenten"]
    )

    # Import im Modus "anhaengen" — kein Konflikt erwartet, weil IDs gleich
    r = await client.post("/api/backup/import?modus=anhaengen", json=export)
    assert r.status_code == 200
    # Mit anhaengen werden vorhandene IDs uebersprungen
    assert r.json()["agenten"] == 0


async def test_backup_import_invalid_modus(client) -> None:
    r = await client.post("/api/backup/import?modus=blubb", json={})
    assert r.status_code == 422
