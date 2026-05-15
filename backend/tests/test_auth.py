"""Auth-Tests — Register, Login, JWT, Protected-Endpunkt."""

from __future__ import annotations


async def test_registrieren_und_anmelden(client) -> None:
    r = await client.post(
        "/api/auth/registriere",
        json={"email": "max@example.de", "passwort": "passwort123", "anzeige_name": "Max"},
    )
    assert r.status_code == 201
    n = r.json()
    assert n["email"] == "max@example.de"
    assert n["rolle"] == "nutzer"

    a = await client.post(
        "/api/auth/anmelde",
        json={"email": "max@example.de", "passwort": "passwort123"},
    )
    assert a.status_code == 200
    daten = a.json()
    assert daten["token"]
    assert daten["nutzer"]["anzeige_name"] == "Max"

    ich = await client.get("/api/auth/ich", headers={"Authorization": f"Bearer {daten['token']}"})
    assert ich.status_code == 200
    assert ich.json()["email"] == "max@example.de"


async def test_doppelte_email_409(client) -> None:
    await client.post(
        "/api/auth/registriere",
        json={"email": "x@y.de", "passwort": "passwort123", "anzeige_name": "X"},
    )
    r2 = await client.post(
        "/api/auth/registriere",
        json={"email": "x@y.de", "passwort": "passwort123", "anzeige_name": "Y"},
    )
    assert r2.status_code == 409


async def test_falsches_passwort_401(client) -> None:
    await client.post(
        "/api/auth/registriere",
        json={"email": "y@y.de", "passwort": "passwort123", "anzeige_name": "Y"},
    )
    r = await client.post(
        "/api/auth/anmelde",
        json={"email": "y@y.de", "passwort": "falsch1234"},
    )
    assert r.status_code == 401


async def test_ich_ohne_token_wenn_auth_aus(client) -> None:
    # AUTH_AKTIV ist default False — /ich liefert ohne Token einen Anonym-User
    r = await client.get("/api/auth/ich")
    assert r.status_code == 200
    assert r.json()["email"] == "anonym@local"


async def test_token_pflicht_wenn_auth_aktiv(client) -> None:
    from app.config import einstellungen

    einstellungen.auth_aktiv = True
    try:
        r = await client.get("/api/auth/ich")
        assert r.status_code == 401
    finally:
        einstellungen.auth_aktiv = False
