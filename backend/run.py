"""Einstiegspunkt zum Starten des Fishingagend-Backends."""

from __future__ import annotations

import uvicorn

from app.config import einstellungen


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=einstellungen.backend_host,
        port=einstellungen.backend_port,
        reload=einstellungen.entwicklung,
        log_level=einstellungen.log_level.lower(),
    )


if __name__ == "__main__":
    main()
