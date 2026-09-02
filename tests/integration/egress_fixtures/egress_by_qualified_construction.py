# tests/integration/egress_fixtures/egress_by_qualified_construction.py
"""Rule E with a dot in front of it: the seal read the call target as a bare name.

`from privacy.items import SelfDescription` was caught and `items.SelfDescription(...)`
was not, which is the same construction with a different import line -- and the
import line is the half a module chooses freely.
"""
from __future__ import annotations

from privacy import items


def describe() -> object:
    return items.SelfDescription("role:me")
