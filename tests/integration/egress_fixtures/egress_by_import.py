# tests/p15/egress_fixtures/egress_by_import.py
"""A questions module that took a model client. The obvious shape of the mistake."""
from __future__ import annotations

from collections.abc import Iterable

from llm_harness.transport import ModelClient


def propose_from(self_description: str, offered: frozenset[str], *,
                 client: ModelClient) -> Iterable[str]:
    return ()
