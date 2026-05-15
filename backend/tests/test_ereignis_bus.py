"""Test fuer den Pub/Sub-Ereignis-Bus."""

from __future__ import annotations

import asyncio

from app.dienste.ereignis_bus import EreignisBus


async def test_abonnent_empfaengt_veroeffentlichte_ereignisse() -> None:
    bus = EreignisBus()
    async with bus.abonniere("topic-1") as queue:
        await bus.veroeffentliche("topic-1", {"a": 1})
        await bus.veroeffentliche("topic-1", {"a": 2})
        e1 = await asyncio.wait_for(queue.get(), timeout=1)
        e2 = await asyncio.wait_for(queue.get(), timeout=1)
    assert e1 == {"a": 1}
    assert e2 == {"a": 2}


async def test_andere_topics_werden_nicht_zugestellt() -> None:
    bus = EreignisBus()
    async with bus.abonniere("a") as queue:
        await bus.veroeffentliche("b", {"x": 1})
        await asyncio.sleep(0)
        assert queue.empty()


async def test_abo_wird_nach_verlassen_aufgeraeumt() -> None:
    bus = EreignisBus()
    async with bus.abonniere("t") as _q:
        assert "t" in bus._abos  # noqa: SLF001
    assert "t" not in bus._abos  # noqa: SLF001
