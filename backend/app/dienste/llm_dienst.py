"""LLM-Adapter — kapselt Anthropic-Aufrufe inklusive Prompt-Caching."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Protocol

from anthropic import AsyncAnthropic

from app.config import einstellungen
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)


@dataclass
class LLMAntwort:
    text: str
    eingangs_token: int = 0
    ausgangs_token: int = 0


@dataclass
class WerkzeugAufruf:
    """Ein Werkzeug-Aufruf, den das Modell ausführen lassen will."""

    name: str
    eingabe: dict[str, Any]
    aufruf_id: str = ""


@dataclass
class WerkzeugErgebnis:
    """Endergebnis einer Tool-Use-Schleife."""

    text: str
    aufrufe: list[WerkzeugAufruf]
    eingangs_token: int = 0
    ausgangs_token: int = 0


class LLMSchnittstelle(Protocol):
    """Damit Tests einen Mock einsetzen können."""

    async def antworte(
        self,
        system_prompt: str,
        verlauf: list[dict[str, str]],
        max_token: int = ...,
        temperatur: float = ...,
    ) -> LLMAntwort: ...

    def stroeme(
        self,
        system_prompt: str,
        verlauf: list[dict[str, str]],
        max_token: int = ...,
        temperatur: float = ...,
    ) -> AsyncIterator[str]: ...

    async def mit_werkzeugen(
        self,
        system_prompt: str,
        verlauf: list[dict[str, Any]],
        werkzeuge: list[dict[str, Any]],
        max_runden: int = ...,
        werkzeug_aufruf: Any = ...,
    ) -> WerkzeugErgebnis: ...


class LLMDienst:
    """Dünner Wrapper um das Anthropic-SDK."""

    def __init__(self, api_key: str | None = None, modell: str | None = None) -> None:
        self._modell = modell or einstellungen.anthropic_modell
        self._client = AsyncAnthropic(api_key=api_key or einstellungen.anthropic_api_key)

    async def antworte(
        self,
        system_prompt: str,
        verlauf: list[dict[str, str]],
        max_token: int = 1024,
        temperatur: float = 0.7,
    ) -> LLMAntwort:
        """Sendet einen Chat-Aufruf.

        Der system_prompt wird mit Prompt-Caching markiert: wiederholte
        Aufrufe mit identischem Persona-Block sind deutlich günstiger.
        """
        logger.debug("llm_aufruf", modell=self._modell, nachrichten=len(verlauf))
        antwort = await self._client.messages.create(
            model=self._modell,
            max_tokens=max_token,
            temperature=temperatur,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=verlauf,  # type: ignore[arg-type]
        )
        text = "".join(blok.text for blok in antwort.content if blok.type == "text")
        return LLMAntwort(
            text=text,
            eingangs_token=antwort.usage.input_tokens,
            ausgangs_token=antwort.usage.output_tokens,
        )

    async def antworte_json(
        self,
        system_prompt: str,
        anweisung: str,
        max_token: int = 2048,
        temperatur: float = 0.3,
    ) -> dict[str, Any]:
        """Fordert eine JSON-Antwort an und parst sie robust.

        Falls das Modell den JSON-Block in Markdown-Fences einbettet, wird
        das innere Objekt extrahiert.
        """
        verlauf = [{"role": "user", "content": anweisung}]
        roh = await self.antworte(
            system_prompt=system_prompt + "\n\nAntworte ausschließlich mit gültigem JSON.",
            verlauf=verlauf,
            max_token=max_token,
            temperatur=temperatur,
        )
        return _parse_json(roh.text)

    async def stroeme(
        self,
        system_prompt: str,
        verlauf: list[dict[str, str]],
        max_token: int = 1024,
        temperatur: float = 0.7,
    ) -> AsyncIterator[str]:
        """Streamt Text-Deltas vom LLM."""
        async with self._client.messages.stream(
            model=self._modell,
            max_tokens=max_token,
            temperature=temperatur,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=verlauf,  # type: ignore[arg-type]
        ) as strom:
            async for text in strom.text_stream:
                yield text

    async def mit_werkzeugen(
        self,
        system_prompt: str,
        verlauf: list[dict[str, Any]],
        werkzeuge: list[dict[str, Any]],
        max_runden: int = 6,
        werkzeug_aufruf: Any = None,
    ) -> WerkzeugErgebnis:
        """Tool-Use-Schleife: LLM darf Werkzeuge aufrufen, bis es einen Text liefert.

        ``werkzeug_aufruf`` ist eine async Funktion ``(name, eingabe) -> str``,
        die das jeweilige Werkzeug ausfuehrt.
        """
        nachrichten = list(verlauf)
        gesamt_eingang = 0
        gesamt_ausgang = 0
        protokoll: list[WerkzeugAufruf] = []
        for _ in range(max_runden):
            antwort = await self._client.messages.create(
                model=self._modell,
                max_tokens=2048,
                system=system_prompt,
                tools=werkzeuge,  # type: ignore[arg-type]
                messages=nachrichten,  # type: ignore[arg-type]
            )
            gesamt_eingang += antwort.usage.input_tokens
            gesamt_ausgang += antwort.usage.output_tokens
            tool_uses = [b for b in antwort.content if b.type == "tool_use"]
            if not tool_uses:
                text = "".join(b.text for b in antwort.content if b.type == "text")
                return WerkzeugErgebnis(
                    text=text,
                    aufrufe=protokoll,
                    eingangs_token=gesamt_eingang,
                    ausgangs_token=gesamt_ausgang,
                )

            nachrichten.append({"role": "assistant", "content": antwort.content})
            ergebnisse: list[dict[str, Any]] = []
            for tu in tool_uses:
                aufruf = WerkzeugAufruf(name=tu.name, eingabe=dict(tu.input), aufruf_id=tu.id)
                protokoll.append(aufruf)
                ausgabe = (
                    await werkzeug_aufruf(aufruf.name, aufruf.eingabe)
                    if werkzeug_aufruf
                    else "Kein Werkzeug-Handler registriert."
                )
                ergebnisse.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": ausgabe,
                    }
                )
            nachrichten.append({"role": "user", "content": ergebnisse})

        return WerkzeugErgebnis(
            text="(Maximale Werkzeug-Runden erreicht ohne Antwort.)",
            aufrufe=protokoll,
            eingangs_token=gesamt_eingang,
            ausgangs_token=gesamt_ausgang,
        )


class MockLLMDienst:
    """Liefert deterministische Antworten — für Tests ohne API-Key."""

    def __init__(self, antworten: list[str] | None = None) -> None:
        self._antworten = list(antworten or ["Mock-Antwort."])
        self._index = 0
        self.aufrufe: list[tuple[str, list[dict[str, str]]]] = []

    async def antworte(
        self,
        system_prompt: str,
        verlauf: list[dict[str, str]],
        max_token: int = 1024,
        temperatur: float = 0.7,
    ) -> LLMAntwort:
        self.aufrufe.append((system_prompt, list(verlauf)))
        text = self._antworten[self._index % len(self._antworten)]
        self._index += 1
        return LLMAntwort(text=text, eingangs_token=10, ausgangs_token=20)

    async def antworte_json(
        self,
        system_prompt: str,
        anweisung: str,
        max_token: int = 2048,
        temperatur: float = 0.3,
    ) -> dict[str, Any]:
        antwort = await self.antworte(system_prompt, [{"role": "user", "content": anweisung}])
        try:
            return _parse_json(antwort.text)
        except (json.JSONDecodeError, ValueError):
            # Sinnvoller Default fuer den Mock-Modus ohne API-Key, sodass
            # Persona-/GraphRAG-Pfade auch lokal lauffaehig sind.
            return {"name": "Mock-Persona", "entitaeten": [], "beziehungen": []}

    async def stroeme(
        self,
        system_prompt: str,
        verlauf: list[dict[str, str]],
        max_token: int = 1024,
        temperatur: float = 0.7,
    ) -> AsyncIterator[str]:
        """Streamt die Mock-Antwort wortweise — nützlich für Frontend-Tests."""
        antwort = await self.antworte(system_prompt, verlauf, max_token, temperatur)
        for wort in antwort.text.split(" "):
            await asyncio.sleep(0)
            yield wort + " "

    async def mit_werkzeugen(
        self,
        system_prompt: str,
        verlauf: list[dict[str, Any]],
        werkzeuge: list[dict[str, Any]],
        max_runden: int = 6,
        werkzeug_aufruf: Any = None,
    ) -> WerkzeugErgebnis:
        """Mock: ruft (falls vorhanden) jedes Werkzeug genau einmal mit leerer
        Eingabe auf, dann gibt es eine deterministische Textantwort zurueck."""
        protokoll: list[WerkzeugAufruf] = []
        for w in werkzeuge[:max_runden]:
            aufruf = WerkzeugAufruf(name=w["name"], eingabe={}, aufruf_id=f"mock-{w['name']}")
            protokoll.append(aufruf)
            if werkzeug_aufruf:
                await werkzeug_aufruf(aufruf.name, aufruf.eingabe)
        antwort = await self.antworte(system_prompt, verlauf)
        return WerkzeugErgebnis(
            text=antwort.text,
            aufrufe=protokoll,
            eingangs_token=antwort.eingangs_token,
            ausgangs_token=antwort.ausgangs_token,
        )


def _parse_json(text: str) -> dict[str, Any]:
    """Versucht, ein JSON-Objekt aus einem Text zu extrahieren."""
    text = text.strip()
    if text.startswith("```"):
        # ```json ... ``` oder ``` ... ```
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        ergebnis = json.loads(text)
    except json.JSONDecodeError:
        # Letzter Rettungsversuch: erstes geschweiftes Paar ausschneiden
        suche = re.search(r"\{.*\}", text, re.DOTALL)
        if not suche:
            raise
        ergebnis = json.loads(suche.group(0))
    if not isinstance(ergebnis, dict):
        raise ValueError("LLM-Antwort war kein JSON-Objekt")
    return ergebnis


_dienst: LLMSchnittstelle | None = None


def hole_llm_dienst() -> LLMSchnittstelle:
    """Gibt den aktuellen LLM-Dienst zurück.

    Ohne API-Key wird ein Mock genutzt — so läuft die Anwendung lokal
    ohne Anthropic-Konto und Tests sind deterministisch.
    """
    global _dienst
    if _dienst is None:
        if einstellungen.anthropic_api_key:
            _dienst = LLMDienst()
        else:
            logger.warning("kein_api_key", hinweis="Mock-LLM aktiv")
            _dienst = MockLLMDienst()
    return _dienst


def setze_llm_dienst(dienst: LLMSchnittstelle | None) -> None:
    """Für Tests: erlaubt das Einsetzen oder Zurücksetzen des Dienstes."""
    global _dienst
    _dienst = dienst
