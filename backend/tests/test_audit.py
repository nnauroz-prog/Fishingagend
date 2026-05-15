"""Audit-Log-Tests."""

from __future__ import annotations


async def test_audit_loggt_agent_erstellung(client) -> None:
    a = await client.post(
        "/api/agenten",
        json={
            "persona": {
                "name": "Audi",
                "hintergrund": "",
                "werte": [],
                "charakterzuege": [],
                "beziehungen": {},
                "sprachstil": "neutral",
            }
        },
    )
    aid = a.json()["id"]

    log = (await client.get("/api/audit?ressource=agent")).json()
    assert any(
        e["aktion"] == "agent_erstellt" and e["ressource_id"] == aid
        for e in log
    )


async def test_audit_loggt_simulation_status(client) -> None:
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
            "name": "Audit-Sim",
            "agent_ids": [a.json()["id"]],
            "schritte": 1,
            "variable": {},
            "dual_modus": False,
        },
    )
    sid = s.json()["id"]
    await client.post(f"/api/simulation/{sid}/starte?sofort=true")

    log = (await client.get("/api/audit?ressource=simulation")).json()
    aktionen = {e["aktion"] for e in log if e["ressource_id"] == sid}
    assert "sim_geplant" in aktionen
    assert "sim_laeuft" in aktionen
    assert "sim_abgeschlossen" in aktionen


async def test_audit_limit(client) -> None:
    r = await client.get("/api/audit?limit=5")
    assert r.status_code == 200
    assert len(r.json()) <= 5
