# tests/p15/egress_fixtures/clean.py
"""What the guard must NOT flag, so it is a distinction rather than a blanket ban.

It takes a `str`, it says "invoke" in its prose, and it names `ModelClient` in a
comment -- all three of which a text scan reads as an egress. `proposal.py` is the
real module this stands for: it says `invoke` and `llm_harness` in prose, and it is
the module whose whole point is that it holds no transport.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable

# A `ModelClient` is what a caller might invoke to build one of these. Not here.
Proposer = Callable[[str, frozenset[str]], Iterable[str]]


def propose_from(self_description: str, offered: frozenset[str], *,
                 propose: Proposer) -> Iterable[str]:
    return propose(self_description, offered)
