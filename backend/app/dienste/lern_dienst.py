"""Lern-Dienst — macht aus Erinnerung echtes Lernen.

Vier Mechanismen, die nach jeder abgeschlossenen Simulation greifen:
1. **Beziehungen lernen** — Persona.beziehungen wird aufgrund der Sim-Aktionen
   aktualisiert (z. B. {"Markus König": "vertrauensvoll, stimmt oft zu"}).
2. **Memory-Konsolidierung** — bei >50 Episoden wird die aelteste Haelfte vom
   LLM zu einer einzigen Zusammenfassung verdichtet (Praefix [Zusammenfassung]).
3. **Reflexionen** — Agent schreibt nach der Sim eine kurze Reflexion in sein
   Gedaechtnis (Praefix [Reflexion]).
4. **Praeferenzen-Tracking** — kein LLM-Aufruf, nur Aggregation: welche
   Begriffe und Namen tauchen am haeufigsten im Memory auf.
"""

from __future__ import annotations

import json
import re
from collections import Counter

from app.config import einstellungen
from app.dienste.agent_dienst import hole_agent_dienst
from app.dienste.gedaechtnis_dienst import hole_gedaechtnis_dienst
from app.dienste.llm_dienst import LLMSchnittstelle, hole_llm_dienst
from app.modelle.agent import Agent
from app.modelle.persona import Persona
from app.modelle.simulation import Simulation
from app.werkzeuge.logger import erstelle_logger

logger = erstelle_logger(__name__)

KONSOLIDIERUNGS_SCHWELLE = 50
KONSOLIDIERUNGS_HALBWERT = 25  # halbiere die aeltesten N Eintraege

_REFLEXION_SYSTEM = """Du bist {name} und reflektierst die soeben abgeschlossene
Simulation in EINEM Satz aus der ersten Person. Was hast du gelernt? Wer ist
dir wichtig geworden? Antworte auf Deutsch, knapp, in der Ich-Form."""

_BEZIEHUNGS_SYSTEM = """Du bist Beziehungs-Analyst. Aus den Sim-Aktionen eines
Agenten leitest du ab, wie er nun zu anderen genannten Personen steht.

Antwortformat (JSON):
{
  "beziehungen": {
    "Name 1": "kurze Beschreibung der Beziehung (max. 80 Zeichen)",
    "Name 2": "..."
  }
}

Nimm nur Personen, die wirklich vorkommen. Kein Erfinden. Bestehende
Beziehungen darfst du verfeinern."""

_KONSOLIDIERUNGS_SYSTEM = """Du verdichtest aelte Erinnerungen eines Agenten zu
einer einzigen, kurzen Zusammenfassung (max. 4 Saetze). Behalte Personen,
Ereignisse, Gefuehle. Antwort auf Deutsch."""

_DRIFT_SYSTEM = """Du bist Charakter-Coach. Aus den Sim-Aktionen eines Agenten
schlaegst du DEZENTE Anpassungen seiner Werte und Charakterzuege vor —
hoechstens je einen Eintrag hinzufuegen ODER einen entfernen, niemals
einen kompletten Umbau. Antwort als JSON:

{
  "werte_hinzu": ["neuer Wert"],
  "werte_weg": ["alter Wert"],
  "charakterzuege_hinzu": ["neuer Zug"],
  "charakterzuege_weg": ["alter Zug"]
}

Leere Listen sind ok. Kein Erfinden ausserhalb der Sim."""


class LernDienst:
    def __init__(self, llm: LLMSchnittstelle | None = None) -> None:
        self._fixierter_llm = llm

    @property
    def _llm(self) -> LLMSchnittstelle:
        return self._fixierter_llm or hole_llm_dienst()

    # ---------- Hauptaufruf ----------
    async def lerne_aus_sim(self, sim: Simulation) -> dict[str, int]:
        """Wird nach jeder abgeschlossenen Sim ausgefuehrt.
        Gibt Aggregat-Zaehler zurueck: aktualisierte Beziehungen,
        konsolidierte Memories, geschriebene Reflexionen."""
        agent_dienst = hole_agent_dienst()
        agenten = await agent_dienst.liste()
        # Nur Agenten, die in dieser Sim teilgenommen haben
        teilnehmer = [a for a in agenten if a.id in sim.agent_ids]

        zaehler = {"beziehungen": 0, "konsolidierungen": 0, "reflexionen": 0, "drift": 0}

        for agent in teilnehmer:
            try:
                if await self._schreibe_reflexion(agent, sim):
                    zaehler["reflexionen"] += 1
            except Exception:
                logger.warning("reflexion_fehlgeschlagen", agent_id=agent.id)

            try:
                if await self._aktualisiere_beziehungen(agent, sim):
                    zaehler["beziehungen"] += 1
            except Exception:
                logger.warning("beziehungen_fehlgeschlagen", agent_id=agent.id)

            try:
                if await self._konsolidiere_falls_noetig(agent.id):
                    zaehler["konsolidierungen"] += 1
            except Exception:
                logger.warning("konsolidierung_fehlgeschlagen", agent_id=agent.id)

            if einstellungen.werte_drift_aktiv:
                try:
                    if await self._werte_drift(agent, sim):
                        zaehler["drift"] += 1
                except Exception:
                    logger.warning("drift_fehlgeschlagen", agent_id=agent.id)

        logger.info("lernen_abgeschlossen", **zaehler)
        return zaehler

    async def _werte_drift(self, agent: Agent, sim: Simulation) -> bool:
        """Dezente Anpassung der Werte/Charakterzuege — opt-in via env."""
        eigene = [
            e for s in sim.verlauf for e in s.ereignisse
            if e.lower().startswith(agent.persona.name.lower() + ":")
        ][:20]
        if not eigene:
            return False

        anweisung = (
            f"Agent: {agent.persona.name}\n"
            f"Aktuelle Werte: {agent.persona.werte}\n"
            f"Aktuelle Charakterzuege: {agent.persona.charakterzuege}\n"
            f"Sim-Aktionen:\n" + "\n".join(f"- {a}" for a in eigene)
        )
        roh = await self._llm.antworte_json(_DRIFT_SYSTEM, anweisung, max_token=400)
        hinzu_w = [str(x).strip() for x in roh.get("werte_hinzu", []) if x][:1]
        weg_w = [str(x).strip() for x in roh.get("werte_weg", []) if x][:1]
        hinzu_c = [str(x).strip() for x in roh.get("charakterzuege_hinzu", []) if x][:1]
        weg_c = [str(x).strip() for x in roh.get("charakterzuege_weg", []) if x][:1]

        if not (hinzu_w or weg_w or hinzu_c or weg_c):
            return False

        neue_werte = [w for w in agent.persona.werte if w not in weg_w] + [
            w for w in hinzu_w if w not in agent.persona.werte
        ]
        neue_zuege = [c for c in agent.persona.charakterzuege if c not in weg_c] + [
            c for c in hinzu_c if c not in agent.persona.charakterzuege
        ]
        if (
            neue_werte == agent.persona.werte
            and neue_zuege == agent.persona.charakterzuege
        ):
            return False

        neue_persona = Persona(
            **{
                **agent.persona.model_dump(),
                "werte": neue_werte,
                "charakterzuege": neue_zuege,
            }
        )
        await hole_agent_dienst().aktualisiere_persona(agent.id, neue_persona)
        return True

    # ---------- Reflexion ----------
    async def _schreibe_reflexion(self, agent: Agent, sim: Simulation) -> bool:
        eigene_aktionen = [
            e for s in sim.verlauf for e in s.ereignisse
            if e.lower().startswith(agent.persona.name.lower() + ":")
            or agent.persona.name in e
        ][:20]
        if not eigene_aktionen:
            return False

        anweisung = (
            f"Simulation: {sim.name}.\n"
            f"Deine Aktionen:\n" + "\n".join(f"- {a}" for a in eigene_aktionen)
        )
        antwort = await self._llm.antworte(
            system_prompt=_REFLEXION_SYSTEM.format(name=agent.persona.name),
            verlauf=[{"role": "user", "content": anweisung}],
            max_token=120,
            temperatur=0.6,
        )
        text = antwort.text.strip()
        if not text:
            return False
        await hole_gedaechtnis_dienst().merke(
            agent.id, f"[Reflexion zu Sim {sim.id[:6]}] {text}"
        )
        return True

    # ---------- Beziehungen ----------
    async def _aktualisiere_beziehungen(self, agent: Agent, sim: Simulation) -> bool:
        relevante = [
            e for s in sim.verlauf for e in s.ereignisse
            if agent.persona.name in e
        ]
        if not relevante:
            return False

        teilnehmer_namen = sorted({
            e.split(":", 1)[0].strip()
            for s in sim.verlauf
            for e in s.ereignisse
            if ":" in e and e.split(":", 1)[0].strip() != agent.persona.name
        })
        if not teilnehmer_namen:
            return False

        bestand = json.dumps(agent.persona.beziehungen, ensure_ascii=False)
        anweisung = (
            f"Du bist {agent.persona.name}. "
            f"Bestehende Beziehungen: {bestand}.\n"
            f"Andere in der Sim: {', '.join(teilnehmer_namen)}.\n"
            f"Auszug aus dem Verlauf:\n" + "\n".join(f"- {e}" for e in relevante[:30])
        )
        roh = await self._llm.antworte_json(_BEZIEHUNGS_SYSTEM, anweisung, max_token=600)
        neue_beziehungen = roh.get("beziehungen") or {}
        if not isinstance(neue_beziehungen, dict) or not neue_beziehungen:
            return False

        # Mergen — neue ueberschreiben alte fuer denselben Schluessel
        kombiniert = dict(agent.persona.beziehungen)
        kombiniert.update({str(k): str(v)[:120] for k, v in neue_beziehungen.items()})

        if kombiniert == agent.persona.beziehungen:
            return False

        neue_persona = Persona(
            **{**agent.persona.model_dump(), "beziehungen": kombiniert}
        )
        await hole_agent_dienst().aktualisiere_persona(agent.id, neue_persona)
        return True

    # ---------- Konsolidierung ----------
    async def _konsolidiere_falls_noetig(self, agent_id: str) -> bool:
        gd = hole_gedaechtnis_dienst()
        alle = await gd.hole_kontext(agent_id, max_eintraege=10000)
        if len(alle) < KONSOLIDIERUNGS_SCHWELLE:
            return False

        zu_verdichten = alle[:KONSOLIDIERUNGS_HALBWERT]
        anweisung = "Aelteste Episoden:\n" + "\n".join(f"- {e}" for e in zu_verdichten)
        antwort = await self._llm.antworte(
            system_prompt=_KONSOLIDIERUNGS_SYSTEM,
            verlauf=[{"role": "user", "content": anweisung}],
            max_token=400,
            temperatur=0.3,
        )
        zusammenfassung = antwort.text.strip()
        if not zusammenfassung:
            return False

        # Aelteste loeschen, Zusammenfassung als neuen Eintrag schreiben.
        # Strategie: alles loeschen, behaltene neu schreiben.
        await gd.loesche(agent_id)
        await gd.merke(agent_id, f"[Zusammenfassung] {zusammenfassung}")
        for e in alle[KONSOLIDIERUNGS_HALBWERT:]:
            await gd.merke(agent_id, e)
        return True


# ---------- Praeferenzen-Tracking (kein LLM) ----------
_STOPP_WOERTER = {
    "und", "oder", "aber", "der", "die", "das", "ich", "du", "er", "sie", "es",
    "wir", "ihr", "ein", "eine", "einen", "im", "in", "auf", "mit", "von", "zu",
    "fuer", "für", "ist", "sind", "war", "waren", "habe", "hat", "haben", "wird",
    "werden", "auch", "nur", "noch", "schon", "sehr", "gut", "mal", "mehr",
    "sim", "schritt", "kontrolle", "variante", "reflexion", "zusammenfassung",
}


async def berechne_praeferenzen(agent_id: str) -> dict:
    """Aggregat ueber das Memory: Top-Begriffe und Top-Personen.
    Keine LLM-Aufrufe — pure Counter."""
    eintraege = await hole_gedaechtnis_dienst().hole_kontext(agent_id, max_eintraege=10000)
    text = " ".join(eintraege)

    # Personen: Wörter mit Großbuchstaben am Anfang, mind. 3 Zeichen
    namen = Counter(
        wort
        for wort in re.findall(r"\b[A-ZÄÖÜ][a-zA-ZäöüÄÖÜß]{2,}\b", text)
        if wort.lower() not in _STOPP_WOERTER
    )

    # Begriffe: alle Wörter, lowercased, ohne Stoppwörter, mind. 4 Zeichen
    begriffe = Counter(
        wort.lower()
        for wort in re.findall(r"\b[a-zA-ZäöüÄÖÜß]{4,}\b", text)
        if wort.lower() not in _STOPP_WOERTER and not wort[0].isupper()
    )

    return {
        "personen": [{"name": n, "anzahl": k} for n, k in namen.most_common(10)],
        "begriffe": [{"wort": w, "anzahl": k} for w, k in begriffe.most_common(20)],
        "episoden": len(eintraege),
    }


_dienst: LernDienst | None = None


def hole_lern_dienst() -> LernDienst:
    global _dienst
    if _dienst is None:
        _dienst = LernDienst()
    return _dienst


def setze_lern_dienst(d: LernDienst | None) -> None:
    global _dienst
    _dienst = d
