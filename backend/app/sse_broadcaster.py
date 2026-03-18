"""
Simple SSE (Server-Sent Events) broadcaster.
Any backend code that changes the schema calls `notify_schema_changed()`,
which pushes an event to every connected SSE client.
"""
import asyncio
from typing import Set

# One asyncio.Queue per connected client
_subscribers: Set[asyncio.Queue] = set()


def subscribe() -> asyncio.Queue:
    """Register a new SSE client and return its dedicated queue."""
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.add(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    """Remove a client queue when the connection closes."""
    _subscribers.discard(q)


def notify_schema_changed() -> None:
    """
    Called from synchronous route handlers (e.g. query_routes.py).
    Puts a schema_changed event into every active subscriber queue.
    """
    for q in list(_subscribers):
        try:
            q.put_nowait("schema_changed")
        except asyncio.QueueFull:
            pass  # drop if the client is slow
