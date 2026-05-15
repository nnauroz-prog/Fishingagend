"""Authentifizierungs-Endpunkte und Dependency."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.config import einstellungen
from app.dienste.auth_dienst import (
    entschluessele_token,
    erstelle_token,
    hole_per_email,
    hole_per_id,
    lege_nutzer_an,
    pruefe_passwort,
)

router = APIRouter()


class Registrierung(BaseModel):
    email: EmailStr
    passwort: str = Field(min_length=8, max_length=200)
    anzeige_name: str = Field(min_length=1, max_length=120)


class Anmeldung(BaseModel):
    email: EmailStr
    passwort: str


class NutzerAusgabe(BaseModel):
    id: str
    email: str
    anzeige_name: str
    rolle: str


class TokenAusgabe(BaseModel):
    token: str
    token_typ: str = "Bearer"
    nutzer: NutzerAusgabe


@router.post("/registriere", response_model=NutzerAusgabe, status_code=status.HTTP_201_CREATED)
async def registriere(anfrage: Registrierung) -> NutzerAusgabe:
    try:
        n = await lege_nutzer_an(anfrage.email, anfrage.passwort, anfrage.anzeige_name)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return NutzerAusgabe(id=n.id, email=n.email, anzeige_name=n.anzeige_name, rolle=n.rolle)


@router.post("/anmelde", response_model=TokenAusgabe)
async def anmelde(anfrage: Anmeldung) -> TokenAusgabe:
    n = await hole_per_email(anfrage.email)
    if n is None or not n.aktiv or not pruefe_passwort(anfrage.passwort, n.passwort_hash):
        raise HTTPException(status_code=401, detail="Ungültige Zugangsdaten")
    return TokenAusgabe(
        token=erstelle_token(n.id, n.rolle),
        nutzer=NutzerAusgabe(id=n.id, email=n.email, anzeige_name=n.anzeige_name, rolle=n.rolle),
    )


async def aktueller_nutzer(
    authorization: str | None = Header(default=None),
) -> NutzerAusgabe | None:
    """Liest optional einen User aus dem JWT. Wenn AUTH_AKTIV=false ist,
    wird kein Token verlangt und None zurueckgegeben."""
    if not authorization or not authorization.lower().startswith("bearer "):
        if einstellungen.auth_aktiv:
            raise HTTPException(status_code=401, detail="Token fehlt")
        return None
    token = authorization.split(None, 1)[1]
    daten = entschluessele_token(token)
    if not daten:
        raise HTTPException(status_code=401, detail="Token ungültig")
    n = await hole_per_id(daten.get("sub", ""))
    if n is None or not n.aktiv:
        raise HTTPException(status_code=401, detail="Nutzer nicht aktiv")
    return NutzerAusgabe(id=n.id, email=n.email, anzeige_name=n.anzeige_name, rolle=n.rolle)


def erforderlich(nutzer: NutzerAusgabe | None = Depends(aktueller_nutzer)) -> NutzerAusgabe:
    """Macht aus dem optionalen User einen erforderlichen."""
    if nutzer is None:
        if einstellungen.auth_aktiv:
            raise HTTPException(status_code=401, detail="Anmeldung erforderlich")
        # Wenn Auth aus ist, simulieren wir einen anonymen Service-User.
        return NutzerAusgabe(
            id="anonym", email="anonym@local", anzeige_name="Anonym", rolle="nutzer"
        )
    return nutzer


@router.get("/ich", response_model=NutzerAusgabe)
async def ich(nutzer: NutzerAusgabe = Depends(erforderlich)) -> NutzerAusgabe:
    return nutzer
