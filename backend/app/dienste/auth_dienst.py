"""Authentifizierung — bcrypt-Hashing, JWT-Signatur, User-Verwaltung."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from passlib.context import CryptContext
from sqlalchemy import select

from app.config import einstellungen
from app.datenbank import NutzerZeile, session_factory
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)

_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
JWT_ALGO = "HS256"


def hashe_passwort(passwort: str) -> str:
    return _pwd.hash(passwort)


def pruefe_passwort(klar: str, hash_wert: str) -> bool:
    try:
        return _pwd.verify(klar, hash_wert)
    except Exception:
        return False


def erstelle_token(nutzer_id: str, rolle: str, gueltigkeit_minuten: int | None = None) -> str:
    minuten = gueltigkeit_minuten or einstellungen.jwt_gueltigkeit_minuten
    laeuft_aus = datetime.utcnow() + timedelta(minutes=minuten)
    nutzlast: dict[str, Any] = {"sub": nutzer_id, "rolle": rolle, "exp": laeuft_aus}
    return jwt.encode(nutzlast, einstellungen.jwt_geheimnis, algorithm=JWT_ALGO)


def entschluessele_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, einstellungen.jwt_geheimnis, algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        return None


async def lege_nutzer_an(
    email: str,
    passwort: str,
    anzeige_name: str,
    rolle: str = "nutzer",
) -> NutzerZeile:
    async with session_factory()() as session:
        vorhanden = (
            await session.execute(select(NutzerZeile).where(NutzerZeile.email == email))
        ).scalar_one_or_none()
        if vorhanden:
            raise ValueError("E-Mail bereits vergeben")
        zeile = NutzerZeile(
            id=str(uuid4()),
            email=email.lower(),
            passwort_hash=hashe_passwort(passwort),
            anzeige_name=anzeige_name,
            rolle=rolle,
        )
        session.add(zeile)
        await session.commit()
        await session.refresh(zeile)
    return zeile


async def hole_per_email(email: str) -> NutzerZeile | None:
    async with session_factory()() as session:
        return (
            await session.execute(select(NutzerZeile).where(NutzerZeile.email == email.lower()))
        ).scalar_one_or_none()


async def hole_per_id(nutzer_id: str) -> NutzerZeile | None:
    async with session_factory()() as session:
        return await session.get(NutzerZeile, nutzer_id)


async def sorge_fuer_admin() -> None:
    """Legt einen Admin-User an, falls die Tabelle leer ist — beim ersten Start."""
    async with session_factory()() as session:
        vorhanden = (await session.execute(select(NutzerZeile))).first()
    if vorhanden:
        return
    try:
        await lege_nutzer_an(
            email=einstellungen.admin_email,
            passwort=einstellungen.admin_passwort,
            anzeige_name="Administrator",
            rolle="admin",
        )
        logger.info("admin_angelegt", email=einstellungen.admin_email)
    except Exception:
        logger.warning("admin_anlage_fehlgeschlagen")
