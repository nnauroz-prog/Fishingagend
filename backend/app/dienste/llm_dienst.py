"""LLM-Adapter — kapselt Anthropic-Aufrufe inklusive Prompt-Caching."""

from __future__ import annotations

from dataclasses import dataclass

from anthropic import AsyncAnthropic

from app.config import einstellungen
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)


@dataclass
class LLMAntwort:
    text: str
    eingangs_token: int
    ausgangs_token: int


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
        """Sendet einen Chat-Aufruf und gibt die Antwort zurück.

        Der system_prompt wird mit Prompt-Caching markiert, sodass wiederholte
        Aufrufe mit identischem Persona-Block deutlich günstiger sind.
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


_dienst: LLMDienst | None = None


def hole_llm_dienst() -> LLMDienst:
    global _dienst
    if _dienst is None:
        _dienst = LLMDienst()
    return _dienst
