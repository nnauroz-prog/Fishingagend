"""Berichts-Agent — fasst Simulationen via LLM und Tool-Use zusammen.

Der Agent bekommt ein Werkzeug-Set zur Hand und entscheidet selbst,
welche Aggregate er fuer den Bericht abruft. Das spiegelt das
"reichhaltige Toolset" aus MiroFish wider.
"""

from __future__ import annotations

from collections import Counter

from app.dienste.llm_dienst import LLMSchnittstelle, hole_llm_dienst
from app.modelle.simulation import Simulation

_SYSTEM_BERICHT = """Du bist ein Analyst fuer Multi-Agenten-Simulationen.
Du erhaelst eine Simulation und einen Werkzeugkasten, mit dem du
Statistiken, einzelne Agenten-Verlaeufe und Welt-Vergleiche abfragst.

Nutze die Werkzeuge gezielt — nicht jedes auf gut Glueck. Schreibe am
Ende einen praegnanten Markdown-Bericht in deutscher Sprache:

# Zusammenfassung (3-4 Saetze)
## Beobachtungen je Welt
## Schluesselereignisse
## Einschaetzung & Empfehlung

Antworte ausschliesslich auf Deutsch."""


_SYSTEM_CHAT = """Du bist Analyst-Assistent fuer Multi-Agenten-Simulationen.
Du beantwortest Nachfragen zu einer abgeschlossenen Simulation, kannst
ueber den Werkzeugkasten zusaetzliche Aggregate ziehen.
Antworte knapp und auf Deutsch."""


WERKZEUGE = [
    {
        "name": "statistik",
        "description": "Liefert Aggregat-Zahlen: Anzahl Schritte je Welt, beteiligte Agenten.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "agent_aktionen",
        "description": "Alle Aktionen eines Agenten ueber alle Schritte hinweg.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Anzeigename des Agenten"}},
            "required": ["name"],
        },
    },
    {
        "name": "vergleiche_welten",
        "description": "Listet die ersten Schritte auf, in denen Kontroll- und Variantenwelt voneinander abweichen.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "suche_im_verlauf",
        "description": "Sucht alle Ereignisse, die einen bestimmten Begriff enthalten.",
        "input_schema": {
            "type": "object",
            "properties": {"begriff": {"type": "string"}},
            "required": ["begriff"],
        },
    },
    {
        "name": "zeitraum",
        "description": "Listet alle Ereignisse zwischen Schritt-Nr. start und ende (inkl.).",
        "input_schema": {
            "type": "object",
            "properties": {
                "start": {"type": "integer"},
                "ende": {"type": "integer"},
            },
            "required": ["start", "ende"],
        },
    },
]


def _werkzeug_handler(sim: Simulation):
    async def aufrufen(name: str, eingabe: dict) -> str:
        if name == "statistik":
            zaehler = Counter(s.welt for s in sim.verlauf)
            akteure: Counter[str] = Counter()
            for s in sim.verlauf:
                for e in s.ereignisse:
                    if ":" in e:
                        akteure[e.split(":", 1)[0].strip()] += 1
            return (
                f"Schritte je Welt: {dict(zaehler)}. "
                f"Top-Akteure: {dict(akteure.most_common(5))}. "
                f"Gesamt-Eintraege: {sum(zaehler.values())}."
            )
        if name == "agent_aktionen":
            ziel = (eingabe.get("name") or "").strip().lower()
            zeilen: list[str] = []
            for s in sim.verlauf:
                for e in s.ereignisse:
                    if e.lower().startswith(ziel + ":"):
                        zeilen.append(f"[{s.welt}#{s.nummer}] {e}")
            return "\n".join(zeilen[:30]) or f"Keine Aktionen fuer '{ziel}' gefunden."
        if name == "vergleiche_welten":
            paare: dict[int, dict[str, list[str]]] = {}
            for s in sim.verlauf:
                paare.setdefault(s.nummer, {}).setdefault(s.welt, []).extend(s.ereignisse)
            unterschiede: list[str] = []
            for nr, p in sorted(paare.items()):
                k, v = p.get("kontrolle", []), p.get("variante", [])
                if k != v:
                    unterschiede.append(f"#{nr}: Kontrolle={k} | Variante={v}")
                if len(unterschiede) >= 10:
                    break
            return "\n".join(unterschiede) or "Keine Abweichungen erkannt."
        if name == "suche_im_verlauf":
            q = (eingabe.get("begriff") or "").lower()
            treffer = [
                f"[{s.welt}#{s.nummer}] {e}"
                for s in sim.verlauf
                for e in s.ereignisse
                if q in e.lower()
            ]
            return "\n".join(treffer[:30]) or f"Keine Treffer fuer '{q}'."
        if name == "zeitraum":
            start, ende = int(eingabe.get("start", 0)), int(eingabe.get("ende", 0))
            zeilen = [
                f"[{s.welt}#{s.nummer}] {e}"
                for s in sim.verlauf
                if start <= s.nummer <= ende
                for e in s.ereignisse
            ]
            return "\n".join(zeilen[:50]) or "Keine Eintraege im Zeitraum."
        return f"Unbekanntes Werkzeug: {name}"

    return aufrufen


class BerichtDienst:
    def __init__(self, llm: LLMSchnittstelle | None = None) -> None:
        self._fixierter_llm = llm

    @property
    def _llm(self) -> LLMSchnittstelle:
        return self._fixierter_llm or hole_llm_dienst()

    async def erstelle_bericht(self, simulation: Simulation) -> str:
        anweisung = (
            f"Erstelle einen Bericht fuer Simulation '{simulation.name}'.\n"
            f"Status: {simulation.status.value} · Schritte: {simulation.schritte} · "
            f"Agenten: {len(simulation.agent_ids)} · Dual: {simulation.dual_modus}\n"
            f"Variable: {simulation.variable or '—'}\n"
            "Nutze die Werkzeuge gezielt, um Belege zu sammeln."
        )
        ergebnis = await self._llm.mit_werkzeugen(
            system_prompt=_SYSTEM_BERICHT,
            verlauf=[{"role": "user", "content": anweisung}],
            werkzeuge=WERKZEUGE,
            werkzeug_aufruf=_werkzeug_handler(simulation),
        )
        return ergebnis.text

    async def chatte(
        self,
        simulation: Simulation,
        verlauf: list[dict[str, str]],
        nachricht: str,
    ) -> str:
        anweisung = (
            f"Simulation: {simulation.name}. "
            f"Frage des Nutzers: {nachricht}"
        )
        kombiniert = list(verlauf) + [{"role": "user", "content": anweisung}]
        ergebnis = await self._llm.mit_werkzeugen(
            system_prompt=_SYSTEM_CHAT,
            verlauf=kombiniert,
            werkzeuge=WERKZEUGE,
            werkzeug_aufruf=_werkzeug_handler(simulation),
            max_runden=4,
        )
        return ergebnis.text
