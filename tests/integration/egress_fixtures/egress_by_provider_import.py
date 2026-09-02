# tests/integration/egress_fixtures/egress_by_provider_import.py
"""The fifth, and the one with no exotic syntax in it at all.

Rule C exempts `readers/model_*` because that is where a socket may legitimately
live. Nothing asked who may IMPORT one. A part that calls a provider's send
function directly declares no flag, reaches for no `.invoke`, and names no network
module -- `_imported` returns `readers.model_deepseek`, which matched no rule.

This is CR-02's shape written in four lines: bytes on the wire that the gate never
released, through a door that is locked only against the callers who go the long
way round.
"""
from __future__ import annotations

from readers.model_deepseek import deepseek_invoke


def ask(sentence: str) -> bytes:
    return deepseek_invoke(sentence.encode("utf-8"))
