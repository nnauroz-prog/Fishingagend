"""Anwendungs-Konfiguration, geladen aus Umgebungsvariablen."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Einstellungen(BaseSettings):
    """Zentrale Einstellungen — werden aus `.env` und Prozess-Umgebung gelesen."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM — Provider-Auswahl
    llm_provider: str = Field(
        default="anthropic",
        description="anthropic | openai (auch Qwen, lokale OpenAI-kompatible Endpunkte)",
    )

    # Anthropic
    anthropic_api_key: str = Field(default="", description="API-Schlüssel für Anthropic")
    anthropic_modell: str = Field(default="claude-opus-4-7")

    # OpenAI-kompatibel (OpenAI, Alibaba Qwen via Bailian, Ollama, etc.)
    openai_api_key: str = Field(default="")
    openai_basis_url: str = Field(
        default="",
        description="z. B. https://dashscope.aliyuncs.com/compatible-mode/v1 für Qwen",
    )
    openai_modell: str = Field(default="qwen-plus")

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    entwicklung: bool = True
    log_level: str = "INFO"
    cors_urspruenge: str = "http://localhost:5173"

    # Datenbank
    datenbank_url: str = "sqlite+aiosqlite:///./data/fishingagend.db"

    # Simulation
    max_agenten: int = 200
    simulations_schritte: int = 50

    # Demo
    demo_daten_einspielen: bool = True

    @property
    def cors_liste(self) -> list[str]:
        return [u.strip() for u in self.cors_urspruenge.split(",") if u.strip()]


@lru_cache
def lade_einstellungen() -> Einstellungen:
    return Einstellungen()


einstellungen = lade_einstellungen()
