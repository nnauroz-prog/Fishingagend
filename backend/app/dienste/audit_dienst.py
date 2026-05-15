"""Audit-Log — schreibt schreibende Aktionen mit Zeitstempel in die DB."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import desc, select

from app.datenbank import AuditZeile, session_factory
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)


async def schreibe(
    aktion: str,
    ressource: str,
    ressource_id: str | None = None,
    details: dict | None = None,
) -> None:
    """Legt einen Audit-Eintrag an. Failt nicht laut — Audit darf die App
    nicht killen, wenn die Spalte z. B. zu klein ist."""
    try:
        async with session_factory()() as session:
            session.add(
                AuditZeile(
                    aktion=aktion,
                    ressource=ressource,
                    ressource_id=ressource_id,
                    details=json.dumps(details, ensure_ascii=False) if details else None,
                )
            )
            await session.commit()
    except Exception:
        logger.warning("audit_schreiben_fehlgeschlagen", aktion=aktion, ressource=ressource)


async def lese(limit: int = 100, ressource: str | None = None) -> list[dict[str, Any]]:
    async with session_factory()() as session:
        stmt = select(AuditZeile).order_by(desc(AuditZeile.id)).limit(limit)
        if ressource:
            stmt = stmt.where(AuditZeile.ressource == ressource)
        zeilen = (await session.execute(stmt)).scalars().all()
    return [
        {
            "id": z.id,
            "zeitstempel": z.zeitstempel.isoformat(),
            "aktion": z.aktion,
            "ressource": z.ressource,
            "ressource_id": z.ressource_id,
            "details": json.loads(z.details) if z.details else None,
        }
        for z in zeilen
    ]
