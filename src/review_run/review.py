"""§6.11's placement review, as the lines a person reads.

    "The user should see these distinctions in the review interface, because a
    direct placement and a context-supported placement should not demand the
    same level of trust."

`review_surface.items` builds that as a CONTROL rather than as a label:
`affordance_for` gives a context-supported match a different acceptance
affordance from an exact fact match, because "two cards that read differently and
accept identically demand identical trust". It had no caller. What `src/cli.py`
prints for a placement is a destination and a sentence, the same shape for every
confidence class, so the distinction the design states as contractual reached
nobody.

**Names are asked for, never taken.** `name_for` answers `None` when a subject's
name is not for this screen, and the renderer counts that subject instead. P13's
rule is that it has no code path which receives protected content and then hides
it -- it has code paths that decline to ask -- and a renderer that took every
filename and filtered afterwards would be the forbidden path with a filter bolted
on. Which subjects those are is the composition root's decision, and it is
already made there by `--show-protected`.

**A chain is rendered with a separator no filesystem uses.** `labels` composes a
TUPLE and never a string, because a joined string is a path in every way that
matters. Here it must become one line, so the tuple is passed back through
`refuse_path_separator` first -- the guard fires rather than being trusted -- and
joined with an arrow, which no reader and no `os.path` will take for a path.

**Every refusal passes through**, and one of them cannot be reached from a real
record. `items.UnrenderableDecision` guards a `place` outcome with no
destination, and `PlacementDecision.__post_init__` refuses to CONSTRUCT one --
"`destination` is present exactly when outcome is `place`". So the guard is a
guard against a hand-built record and against a future in which P11 relaxes that
invariant, and no test here fakes a decision P11 forbids in order to reach it.
It is reported as a finding rather than exercised through a lie.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence

from placement.records import PlacementDecision

from review_surface.citations import UNRESOLVABLE
from review_surface.items import (
    CitationResolver,
    PlacementReviewItem,
    placement_review_item,
)
from review_surface.labels import refuse_path_separator

__all__ = ["placement_lines"]

#: Not a path separator on any platform this ships to, which is the whole reason
#: it is this character and not "/". `refuse_path_separator` has already
#: guaranteed no label carries one of its own.
_CHAIN_JOIN = " > "


def _card(item: PlacementReviewItem, name: str) -> tuple[str, ...]:
    """One subject's block. Every line is read off the item; none is computed."""
    chain = refuse_path_separator(item.destination_label_chain)
    # Read off `ResolvedCitation.state`, which is `citations`' own answer, and
    # never off the record's text. This counted a `str()` prefix once and was
    # right only about the test's stand-in resolver: the real
    # `resolve_matching_facts` returns a dataclass whose `str()` begins
    # "ResolvedCitation(", so every citation in production would have counted as
    # resolved and Done-means 3's whole point -- that a broken citation is
    # visible AS missing -- would have been silently off.
    unresolved = sum(1 for _, resolution in item.cited_facts
                     if getattr(resolution, "state", None) == UNRESOLVABLE)
    return (
        f"  {name}",
        f"    {item.render_state}, by {item.confidence_class} "
        f"-- {item.acceptance_affordance}",
        (f"    into: {_CHAIN_JOIN.join(chain)}" if chain
         else "    into: nothing is proposed"),
        f"    because: {item.explanation}",
        f"    evidence: {len(item.cited_facts)} cited, {unresolved} of them "
        "unresolved",
    )


def placement_lines(conn: sqlite3.Connection,
                    decisions: Sequence[PlacementDecision], *,
                    name_for: Callable[[PlacementDecision], str | None],
                    resolve_citations: CitationResolver) -> tuple[str, ...]:
    """§6.11's cards, ready to print, with the unnamed subjects counted.

    `name_for` is handed the DECISION and not `item.subject_ref`, which is the
    decision id. A subject is a file or a group of files, the composition root
    already knows how to name one, and P13's own record deliberately carries no
    filename -- so the naming stays where the naming policy is.

    `name_for` and `resolve_citations` are both required. A default name would
    put a filename on a screen the composition root had not agreed to name it
    on, and a default resolver would be P13 guessing what a citation says --
    which `placement_review_item` already refuses for the same reason.
    """
    cards: list[str] = []
    unnamed = 0
    for decision in decisions:
        item = placement_review_item(conn, decision,
                                     resolve_citations=resolve_citations)
        name = name_for(decision)
        if name is None:
            unnamed += 1
            continue
        cards.extend(_card(item, name))

    aggregate = ()
    if unnamed:
        aggregate = (
            f"  {unnamed} file{'' if unnamed == 1 else 's'} "
            f"{'is' if unnamed == 1 else 'are'} not named on this screen. "
            f"{'Its' if unnamed == 1 else 'Their'} placement"
            f"{'' if unnamed == 1 else 's'} "
            f"{'is' if unnamed == 1 else 'are'} still counted and "
            f"{'it is' if unnamed == 1 else 'they are'} still yours to review.",
        )
    return ("", "How each placement was reached, and how much it asks of you:",
            *cards, *aggregate)
