"""Chat-Endpunkt — Gespräch mit einem simulierten Agenten."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.dienste.agent_dienst import AgentDienst, hole_agent_dienst
from app.dienste.gedaechtnis_dienst import GedaechtnisDienst, hole_gedaechtnis_dienst
from app.dienste.llm_dienst import LLMSchnittstelle, hole_llm_dienst
from app.modelle.chat import ChatAnfrage, ChatAntwort, Nachricht
from app.modelle.persona import Persona

router = APIRouter()


def _system_prompt(persona: Persona, gedaechtnis: list[str]) -> str:
    zeilen = [
        f"Du verkörperst {persona.name}.",
        f"Beruf: {persona.beruf or 'unbekannt'}.",
        f"Hintergrund: {persona.hintergrund or 'keiner angegeben'}.",
        f"Werte: {', '.join(persona.werte) or 'keine'}.",
        f"Charakterzüge: {', '.join(persona.charakterzuege) or 'keine'}.",
        f"Sprachstil: {persona.sprachstil}.",
        "Antworte ausschließlich auf Deutsch und bleibe konsequent in dieser Rolle.",
    ]
    if gedaechtnis:
        zeilen.append("\nLangzeit-Gedächtnis:")
        zeilen.extend(f"- {eintrag}" for eintrag in gedaechtnis)
    return "\n".join(zeilen)


@router.post("", response_model=ChatAntwort)
async def chatte(
    anfrage: ChatAnfrage,
    agenten: AgentDienst = Depends(hole_agent_dienst),
    gedaechtnis: GedaechtnisDienst = Depends(hole_gedaechtnis_dienst),
    llm: LLMSchnittstelle = Depends(hole_llm_dienst),
) -> ChatAntwort:
    agent = await agenten.hole(anfrage.agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")

    verlauf = [
        {"role": "user" if n.rolle == "nutzer" else "assistant", "content": n.inhalt}
        for n in anfrage.verlauf
    ]
    verlauf.append({"role": "user", "content": anfrage.nachricht})

    kontext = await gedaechtnis.hole_kontext(agent.id)
    system = _system_prompt(agent.persona, kontext)
    antwort = await llm.antworte(system_prompt=system, verlauf=verlauf)

    await gedaechtnis.merke(agent.id, f"Nutzer: {anfrage.nachricht}")
    await gedaechtnis.merke(agent.id, f"Ich: {antwort.text}")

    nachricht = Nachricht(rolle="agent", inhalt=antwort.text)
    return ChatAntwort(
        agent_id=agent.id,
        antwort=antwort.text,
        nachricht=nachricht,
        eingangs_token=antwort.eingangs_token,
        ausgangs_token=antwort.ausgangs_token,
    )


@router.post("/strom")
async def chatte_strom(
    anfrage: ChatAnfrage,
    agenten: AgentDienst = Depends(hole_agent_dienst),
    gedaechtnis: GedaechtnisDienst = Depends(hole_gedaechtnis_dienst),
    llm: LLMSchnittstelle = Depends(hole_llm_dienst),
) -> StreamingResponse:
    """Streamt die Antwort als Server-Sent Events."""
    agent = await agenten.hole(anfrage.agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")

    verlauf = [
        {"role": "user" if n.rolle == "nutzer" else "assistant", "content": n.inhalt}
        for n in anfrage.verlauf
    ]
    verlauf.append({"role": "user", "content": anfrage.nachricht})
    kontext = await gedaechtnis.hole_kontext(agent.id)
    system = _system_prompt(agent.persona, kontext)

    async def ereignisse() -> AsyncIterator[bytes]:
        gesammelt: list[str] = []
        try:
            async for delta in llm.stroeme(system_prompt=system, verlauf=verlauf):
                gesammelt.append(delta)
                yield _sse("delta", {"text": delta})
            text = "".join(gesammelt)
            await gedaechtnis.merke(agent.id, f"Nutzer: {anfrage.nachricht}")
            await gedaechtnis.merke(agent.id, f"Ich: {text}")
            yield _sse("fertig", {"text": text})
        except Exception as exc:
            yield _sse("fehler", {"meldung": str(exc)})

    return StreamingResponse(ereignisse(), media_type="text/event-stream")


def _sse(typ: str, daten: dict) -> bytes:
    return f"event: {typ}\ndata: {json.dumps(daten, ensure_ascii=False)}\n\n".encode()
