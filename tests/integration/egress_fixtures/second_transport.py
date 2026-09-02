# tests/integration/egress_fixtures/second_transport.py
"""A second module that declares itself the transport, and is a good one.

It would pass `privacy.transport_guard.assert_single_egress` on its own -- one entry
point, taking a `Released` -- which is exactly why counting the declarers is a
different question from checking them. Two doors, both locked, both doors.
"""
from __future__ import annotations

from collections.abc import Callable

from privacy.release import Released

IS_MODEL_TRANSPORT: bool = True


def issue(released: Released, *, sink: Callable[[bytes], bytes]) -> bytes:
    return sink(b"")
