"""Einstellungs-Endpunkt — zeigt aktuelle (nicht-geheime) Konfiguration."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import einstellungen

router = APIRouter()


@router.get("")
async def lies() -> dict:
    """Gibt die aktive Konfiguration zurueck — Secrets nur als Boolean-Flags."""
    return {
        "llm": {
            "provider": einstellungen.llm_provider,
            "anthropic_modell": einstellungen.anthropic_modell,
            "anthropic_api_key_gesetzt": bool(einstellungen.anthropic_api_key),
            "openai_modell": einstellungen.openai_modell,
            "openai_basis_url": einstellungen.openai_basis_url or None,
            "openai_api_key_gesetzt": bool(einstellungen.openai_api_key),
        },
        "simulation": {
            "max_agenten": einstellungen.max_agenten,
            "simulations_schritte": einstellungen.simulations_schritte,
            "demo_daten_einspielen": einstellungen.demo_daten_einspielen,
        },
        "datenbank_dialekt": einstellungen.datenbank_url.split("+")[0].split(":")[0],
    }
