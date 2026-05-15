"""Pytest-Konfiguration und gemeinsame Fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.datenbank import initialisiere_datenbank, setze_datenbank_url
from app.dienste.llm_dienst import MockLLMDienst, setze_llm_dienst
from app.dienste.simulation_dienst import setze_simulation_dienst
from app.main import app


@pytest.fixture
async def isolierte_datenbank(tmp_path: Path):
    db_pfad = tmp_path / "test.db"
    setze_datenbank_url(f"sqlite+aiosqlite:///{db_pfad}")
    await initialisiere_datenbank()
    yield
    setze_datenbank_url("sqlite+aiosqlite:///./data/fishingagend.db")


@pytest.fixture
def llm_mock():
    mock = MockLLMDienst(
        antworten=[
            "Mock-Antwort 1.",
            "Mock-Antwort 2.",
            "Mock-Antwort 3.",
            "Mock-Antwort 4.",
            "Mock-Antwort 5.",
        ]
    )
    setze_llm_dienst(mock)
    setze_simulation_dienst(None)
    yield mock
    setze_llm_dienst(None)
    setze_simulation_dienst(None)


@pytest.fixture
async def client(isolierte_datenbank, llm_mock):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
