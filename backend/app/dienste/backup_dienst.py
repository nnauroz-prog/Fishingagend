"""Backup/Restore — exportiert die komplette Datenbank als JSON-Blob.

Bewusst pragmatisch: keine Migration-Versionen-Pruefung beim Import.
Wer Backups einspielt, sorgt selber dafuer, dass das Schema passt.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.datenbank import (
    AgentZeile,
    AuditZeile,
    BeziehungZeile,
    EntitaetZeile,
    GedaechtnisZeile,
    NutzerZeile,
    PlattformBeitragZeile,
    PlattformFolgtZeile,
    PlattformReaktionZeile,
    SimulationSchrittZeile,
    SimulationZeile,
    session_factory,
)


def _datum(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


async def exportiere() -> dict[str, Any]:
    """Liefert ein vollstaendiges DB-Abbild als serialisierbares dict."""
    async with session_factory()() as session:
        agenten = (await session.execute(select(AgentZeile))).scalars().all()
        gedaechtnis = (await session.execute(select(GedaechtnisZeile))).scalars().all()
        sims = (await session.execute(select(SimulationZeile))).scalars().all()
        schritte = (await session.execute(select(SimulationSchrittZeile))).scalars().all()
        ents = (await session.execute(select(EntitaetZeile))).scalars().all()
        bzs = (await session.execute(select(BeziehungZeile))).scalars().all()
        beitraege = (await session.execute(select(PlattformBeitragZeile))).scalars().all()
        reaktionen = (await session.execute(select(PlattformReaktionZeile))).scalars().all()
        folgt = (await session.execute(select(PlattformFolgtZeile))).scalars().all()
        audit = (await session.execute(select(AuditZeile))).scalars().all()
        nutzer = (await session.execute(select(NutzerZeile))).scalars().all()

    return {
        "version": 1,
        "exportiert_am": datetime.utcnow().isoformat(),
        "agenten": [
            {
                "id": a.id,
                "persona_json": a.persona_json,
                "notizen": a.notizen,
                "erstellt_am": _datum(a.erstellt_am),
                "aktualisiert_am": _datum(a.aktualisiert_am),
            }
            for a in agenten
        ],
        "gedaechtnis": [
            {"agent_id": g.agent_id, "inhalt": g.inhalt, "erstellt_am": _datum(g.erstellt_am)}
            for g in gedaechtnis
        ],
        "simulationen": [
            {
                "id": s.id,
                "name": s.name,
                "beschreibung": s.beschreibung,
                "agent_ids_json": s.agent_ids_json,
                "schritte": s.schritte,
                "variable_json": s.variable_json,
                "dual_modus": s.dual_modus,
                "plattform_modus": s.plattform_modus,
                "status": s.status,
                "erstellt_am": _datum(s.erstellt_am),
            }
            for s in sims
        ],
        "simulations_schritte": [
            {
                "simulation_id": s.simulation_id,
                "nummer": s.nummer,
                "welt": s.welt,
                "ereignisse_json": s.ereignisse_json,
                "agent_zustaende_json": s.agent_zustaende_json,
            }
            for s in schritte
        ],
        "entitaeten": [
            {"name": e.name, "typ": e.typ, "beschreibung": e.beschreibung}
            for e in ents
        ],
        "beziehungen": [
            {"von": b.von, "nach": b.nach, "art": b.art, "gewicht": b.gewicht}
            for b in bzs
        ],
        "plattform_beitraege": [
            {
                "id": b.id,
                "simulation_id": b.simulation_id,
                "welt": b.welt,
                "schritt_nr": b.schritt_nr,
                "autor": b.autor,
                "inhalt": b.inhalt,
            }
            for b in beitraege
        ],
        "plattform_reaktionen": [
            {
                "simulation_id": r.simulation_id,
                "welt": r.welt,
                "schritt_nr": r.schritt_nr,
                "beitrag_id": r.beitrag_id,
                "autor": r.autor,
                "typ": r.typ,
                "inhalt": r.inhalt,
            }
            for r in reaktionen
        ],
        "plattform_folgt": [
            {
                "simulation_id": f.simulation_id,
                "welt": f.welt,
                "folger": f.folger,
                "gefolgter": f.gefolgter,
                "schritt_nr": f.schritt_nr,
            }
            for f in folgt
        ],
        "audit_log": [
            {
                "zeitstempel": _datum(a.zeitstempel),
                "aktion": a.aktion,
                "ressource": a.ressource,
                "ressource_id": a.ressource_id,
                "details": a.details,
            }
            for a in audit
        ],
        "nutzer": [
            {
                "id": n.id,
                "email": n.email,
                "passwort_hash": n.passwort_hash,
                "anzeige_name": n.anzeige_name,
                "rolle": n.rolle,
                "aktiv": n.aktiv,
                "erstellt_am": _datum(n.erstellt_am),
            }
            for n in nutzer
        ],
    }


async def importiere(daten: dict[str, Any], modus: str = "anhaengen") -> dict[str, int]:
    """Importiert ein Backup. Modus:
      - "anhaengen": vorhandene Zeilen bleiben; doppelte werden uebersprungen.
      - "ersetzen":  alle Tabellen werden zuvor geleert.
    Gibt Zaehler je Tabelle zurueck.
    """
    if modus not in {"anhaengen", "ersetzen"}:
        raise ValueError("modus muss 'anhaengen' oder 'ersetzen' sein")

    zaehler = {k: 0 for k in [
        "agenten", "gedaechtnis", "simulationen", "simulations_schritte",
        "entitaeten", "beziehungen", "plattform_beitraege",
        "plattform_reaktionen", "plattform_folgt", "audit_log", "nutzer",
    ]}

    async with session_factory()() as session:
        if modus == "ersetzen":
            for typ in (
                AuditZeile, PlattformFolgtZeile, PlattformReaktionZeile,
                PlattformBeitragZeile, BeziehungZeile, EntitaetZeile,
                SimulationSchrittZeile, SimulationZeile,
                GedaechtnisZeile, AgentZeile, NutzerZeile,
            ):
                for z in (await session.execute(select(typ))).scalars().all():
                    await session.delete(z)
            await session.commit()

        bestand_agenten = {
            a.id for a in (await session.execute(select(AgentZeile))).scalars().all()
        }
        bestand_sims = {
            s.id for s in (await session.execute(select(SimulationZeile))).scalars().all()
        }
        bestand_emails = {
            n.email for n in (await session.execute(select(NutzerZeile))).scalars().all()
        }

        for a in daten.get("agenten", []):
            if a["id"] in bestand_agenten:
                continue
            session.add(AgentZeile(
                id=a["id"], persona_json=a["persona_json"], notizen=a.get("notizen"),
                erstellt_am=datetime.fromisoformat(a["erstellt_am"]) if a.get("erstellt_am") else datetime.utcnow(),
                aktualisiert_am=datetime.fromisoformat(a["aktualisiert_am"]) if a.get("aktualisiert_am") else datetime.utcnow(),
            ))
            zaehler["agenten"] += 1

        for g in daten.get("gedaechtnis", []):
            session.add(GedaechtnisZeile(agent_id=g["agent_id"], inhalt=g["inhalt"]))
            zaehler["gedaechtnis"] += 1

        for s in daten.get("simulationen", []):
            if s["id"] in bestand_sims:
                continue
            session.add(SimulationZeile(
                id=s["id"], name=s["name"], beschreibung=s.get("beschreibung", ""),
                agent_ids_json=s["agent_ids_json"], schritte=s["schritte"],
                variable_json=s.get("variable_json") or {},
                dual_modus=bool(s.get("dual_modus", True)),
                plattform_modus=bool(s.get("plattform_modus", False)),
                status=s.get("status", "geplant"),
            ))
            zaehler["simulationen"] += 1

        for sch in daten.get("simulations_schritte", []):
            session.add(SimulationSchrittZeile(
                simulation_id=sch["simulation_id"], nummer=sch["nummer"],
                welt=sch["welt"], ereignisse_json=sch.get("ereignisse_json", "[]"),
                agent_zustaende_json=sch.get("agent_zustaende_json", "{}"),
            ))
            zaehler["simulations_schritte"] += 1

        for e in daten.get("entitaeten", []):
            session.add(EntitaetZeile(
                name=e["name"], typ=e["typ"], beschreibung=e.get("beschreibung", "")
            ))
            zaehler["entitaeten"] += 1

        for b in daten.get("beziehungen", []):
            session.add(BeziehungZeile(
                von=b["von"], nach=b["nach"], art=b["art"],
                gewicht=float(b.get("gewicht", 1.0)),
            ))
            zaehler["beziehungen"] += 1

        for b in daten.get("plattform_beitraege", []):
            session.add(PlattformBeitragZeile(
                simulation_id=b["simulation_id"], welt=b["welt"],
                schritt_nr=b["schritt_nr"], autor=b["autor"], inhalt=b["inhalt"],
            ))
            zaehler["plattform_beitraege"] += 1

        for r in daten.get("plattform_reaktionen", []):
            session.add(PlattformReaktionZeile(
                simulation_id=r["simulation_id"], welt=r["welt"],
                schritt_nr=r["schritt_nr"], beitrag_id=r["beitrag_id"],
                autor=r["autor"], typ=r["typ"], inhalt=r.get("inhalt"),
            ))
            zaehler["plattform_reaktionen"] += 1

        for f in daten.get("plattform_folgt", []):
            session.add(PlattformFolgtZeile(
                simulation_id=f["simulation_id"], welt=f["welt"],
                folger=f["folger"], gefolgter=f["gefolgter"],
                schritt_nr=f["schritt_nr"],
            ))
            zaehler["plattform_folgt"] += 1

        for a in daten.get("audit_log", []):
            session.add(AuditZeile(
                aktion=a["aktion"], ressource=a["ressource"],
                ressource_id=a.get("ressource_id"), details=a.get("details"),
            ))
            zaehler["audit_log"] += 1

        for n in daten.get("nutzer", []):
            if n["email"] in bestand_emails:
                continue
            session.add(NutzerZeile(
                id=n["id"], email=n["email"], passwort_hash=n["passwort_hash"],
                anzeige_name=n["anzeige_name"], rolle=n.get("rolle", "nutzer"),
                aktiv=bool(n.get("aktiv", True)),
            ))
            zaehler["nutzer"] += 1

        await session.commit()

    return zaehler


def serialisiere(daten: dict[str, Any]) -> str:
    return json.dumps(daten, ensure_ascii=False, indent=2)
