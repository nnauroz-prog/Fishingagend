"""Alembic-Umgebung — bezieht Metadaten aus app.datenbank."""

from __future__ import annotations

import re
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.config import einstellungen
from app.datenbank import Basis

config = context.config

# Datenbank-URL aus den Anwendungseinstellungen ziehen — synchroner Treiber
# fuer Alembic (sqlite statt sqlite+aiosqlite).
url = re.sub(r"\+aiosqlite", "", einstellungen.datenbank_url)
url = re.sub(r"\+asyncpg", "", url)
config.set_main_option("sqlalchemy.url", url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

ziel_metadaten = Basis.metadata


def offline_lauf() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=ziel_metadaten,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def online_lauf() -> None:
    motor = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with motor.connect() as verbindung:
        context.configure(connection=verbindung, target_metadata=ziel_metadaten)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    offline_lauf()
else:
    online_lauf()
