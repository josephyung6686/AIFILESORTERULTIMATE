"""Optional cheap hint — never a hard lane router (architecture §4.1)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelHint:
    tier: str  # fast | frontier | local
    preload_group: str | None
    reason: str


_ORGANIZE_WORDS = (
    "organize", "sort", "move", "rename", "apply", "tree", "group",
    "place", "folder structure",
)
_FIND_WORDS = (
    "where", "find", "search", "locate", "which file", "look for",
)


def hint_for_question(question: str) -> ModelHint:
    """Suggest tier/preload. Agent may ignore; never blocks tools."""
    q = (question or "").strip().lower()
    if any(w in q for w in _ORGANIZE_WORDS):
        return ModelHint(
            tier="frontier",
            preload_group="organize_propose",
            reason="organize language — hint frontier + propose group",
        )
    if any(w in q for w in _FIND_WORDS):
        return ModelHint(
            tier="fast",
            preload_group=None,
            reason="find language — cheap model enough",
        )
    return ModelHint(tier="fast", preload_group=None, reason="default fast")
