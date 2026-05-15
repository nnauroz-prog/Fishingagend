"""Stimmungs-Analyse — sehr leichtgewichtig per Wörterbuch.

Ein Schritt erhält einen Sentiment-Score zwischen -1 (negativ) und +1 (positiv).
Ohne LLM-Aufruf, also instant und deterministisch.
"""

from __future__ import annotations

from app.modelle.simulation import Simulation

_POSITIV = {
    "gut", "freut", "freue", "freuen", "froh", "glücklich", "wunderbar", "toll",
    "super", "klasse", "danke", "vertrauen", "hoffnung", "erfolg", "gewonnen",
    "gewinn", "liebe", "schoen", "schön", "hilft", "geholfen", "lobe", "stolz",
    "zustimmung", "ja", "einverstanden", "klar",
}
_NEGATIV = {
    "schlecht", "schlimm", "wütend", "wut", "angst", "fürchte", "fuerchte",
    "kritik", "verärgert", "sorge", "sorgen", "problem", "probleme", "konflikt",
    "ablehnung", "nein", "niemals", "tot", "krise", "krisen", "verloren",
    "verlust", "trauer", "feind", "hass", "schreit", "warnt", "verbietet",
    "scheiter", "scheitert",
}


def schritt_stimmung(ereignisse: list[str]) -> float:
    """Score zwischen -1 und +1 für eine Liste von Ereignissen."""
    if not ereignisse:
        return 0.0
    pos = neg = 0
    for e in ereignisse:
        worte = e.lower().split()
        for w in worte:
            w = w.strip(".,!?;:\"'„“()")
            if w in _POSITIV:
                pos += 1
            if w in _NEGATIV:
                neg += 1
    gesamt = pos + neg
    if not gesamt:
        return 0.0
    return (pos - neg) / gesamt


def stimmungs_verlauf(sim: Simulation) -> dict:
    """Pro Schritt × Welt einen Score. Liefert sortierte Listen je Welt."""
    welten: dict[str, dict[int, float]] = {}
    for s in sim.verlauf:
        welten.setdefault(s.welt, {})[s.nummer] = schritt_stimmung(s.ereignisse)

    ergebnis: dict[str, list[dict]] = {}
    for welt, scores in welten.items():
        ergebnis[welt] = [
            {"schritt": n, "score": round(scores[n], 3)}
            for n in sorted(scores)
        ]
    return ergebnis
