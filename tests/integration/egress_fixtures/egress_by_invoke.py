# tests/p15/egress_fixtures/egress_by_invoke.py
"""The same door with the sign taken down: no import, no annotation, one call.

This is the shape a scan for `ModelClient` misses, and it is the likelier one --
duck typing is how a second egress arrives without anybody deciding to add one.
"""
from __future__ import annotations

from collections.abc import Iterable


def propose_from(self_description: str, offered: frozenset[str], *,
                 client) -> Iterable[str]:
    reply = client.invoke(self_description.encode("utf-8"))
    return reply.decode("utf-8").split(",")
