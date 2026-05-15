"""SQLAlchemy-Async-Setup und Tabellen-Definition."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.config import einstellungen


class Basis(DeclarativeBase):
    pass


class AgentZeile(Basis):
    __tablename__ = "agenten"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    persona_json: Mapped[str] = mapped_column(Text)
    notizen: Mapped[str | None] = mapped_column(Text, nullable=True)
    erstellt_am: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    aktualisiert_am: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class GedaechtnisZeile(Basis):
    __tablename__ = "gedaechtnis"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agenten.id", ondelete="CASCADE"))
    inhalt: Mapped[str] = mapped_column(Text)
    erstellt_am: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SimulationZeile(Basis):
    __tablename__ = "simulationen"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    beschreibung: Mapped[str] = mapped_column(Text, default="")
    agent_ids_json: Mapped[str] = mapped_column(Text)
    schritte: Mapped[int] = mapped_column()
    variable_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    dual_modus: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String(20), default="geplant")
    erstellt_am: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    schritt_zeilen: Mapped[list[SimulationSchrittZeile]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
        order_by="SimulationSchrittZeile.id",
    )


class SimulationSchrittZeile(Basis):
    __tablename__ = "simulations_schritte"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("simulationen.id", ondelete="CASCADE")
    )
    nummer: Mapped[int]
    welt: Mapped[str] = mapped_column(String(20))
    ereignisse_json: Mapped[str] = mapped_column(Text, default="[]")
    agent_zustaende_json: Mapped[str] = mapped_column(Text, default="{}")

    simulation: Mapped[SimulationZeile] = relationship(back_populates="schritt_zeilen")


class EntitaetZeile(Basis):
    __tablename__ = "entitaeten"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    typ: Mapped[str] = mapped_column(String(40))
    beschreibung: Mapped[str] = mapped_column(Text, default="")


class BeziehungZeile(Basis):
    __tablename__ = "beziehungen"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    von: Mapped[str] = mapped_column(String(200), index=True)
    nach: Mapped[str] = mapped_column(String(200), index=True)
    art: Mapped[str] = mapped_column(String(80))
    gewicht: Mapped[float] = mapped_column(default=1.0)


def _kodiere(wert: Any) -> str:
    return json.dumps(wert, ensure_ascii=False)


def _dekodiere(wert: str | None, fallback: Any) -> Any:
    if not wert:
        return fallback
    return json.loads(wert)


_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _erstelle_engine_falls_noetig() -> async_sessionmaker[AsyncSession]:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_async_engine(einstellungen.datenbank_url, echo=False, future=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _session_factory


def setze_datenbank_url(url: str) -> None:
    """Für Tests — setzt eine alternative DB und verwirft die alte Engine."""
    global _engine, _session_factory
    einstellungen.datenbank_url = url
    _engine = None
    _session_factory = None


async def initialisiere_datenbank() -> None:
    """Erzeugt fehlende Tabellen — ersetzt Alembic im Skelett."""
    _erstelle_engine_falls_noetig()
    assert _engine is not None
    async with _engine.begin() as verbindung:
        await verbindung.run_sync(Basis.metadata.create_all)


async def hole_session() -> AsyncIterator[AsyncSession]:
    factory = _erstelle_engine_falls_noetig()
    async with factory() as session:
        yield session


def session_factory() -> async_sessionmaker[AsyncSession]:
    return _erstelle_engine_falls_noetig()


# Helfer für die Service-Schicht — bewusst hier, damit nur eine Stelle
# die JSON-Kodierung kennt.
def kodiere_json(wert: Any) -> str:
    return _kodiere(wert)


def dekodiere_json(wert: str | None, fallback: Any) -> Any:
    return _dekodiere(wert, fallback)
