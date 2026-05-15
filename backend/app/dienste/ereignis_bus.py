"""Ereignis-Bus — leichter Pub/Sub fuer Simulations-Live-Updates."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any


class EreignisBus:
    """Pro-Topic asyncio.Queue je Subscriber.

    Nicht persistiert — pro Prozess. Reicht fuer Single-Node, mehrere
    parallele WebSocket-Clients pro Simulation.
    """

    def __init__(self) -> None:
        self._abos: dict[str, set[asyncio.Queue[dict[str, Any]]]] = defaultdict(set)

    async def veroeffentliche(self, topic: str, ereignis: dict[str, Any]) -> None:
        for queue in list(self._abos.get(topic, ())):
            try:
                queue.put_nowait(ereignis)
            except asyncio.QueueFull:
                # Bei voller Queue: aelteste verwerfen, neue rein.
                _ = queue.get_nowait()
                queue.put_nowait(ereignis)

    @asynccontextmanager
    async def abonniere(self, topic: str) -> AsyncIterator[asyncio.Queue[dict[str, Any]]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=100)
        self._abos[topic].add(queue)
        try:
            yield queue
        finally:
            self._abos[topic].discard(queue)
            if not self._abos[topic]:
                self._abos.pop(topic, None)


_bus = EreignisBus()


def hole_ereignis_bus() -> EreignisBus:
    return _bus
