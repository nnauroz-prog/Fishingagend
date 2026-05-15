"""Strukturiertes Logging via structlog."""

from __future__ import annotations

import logging

import structlog

from app.config import einstellungen

_initialisiert = False


def _initialisiere() -> None:
    global _initialisiert
    if _initialisiert:
        return

    logging.basicConfig(level=einstellungen.log_level, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if einstellungen.entwicklung else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, einstellungen.log_level)),
        cache_logger_on_first_use=True,
    )
    _initialisiert = True


def erstelle_logger(name: str) -> structlog.stdlib.BoundLogger:
    _initialisiere()
    return structlog.get_logger(name)
