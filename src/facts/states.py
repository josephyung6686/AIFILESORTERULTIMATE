# src/facts/states.py
"""§3.13's six reliability states — P4's tuple, re-exported, never re-spelled.

Preamble rule 2: "There is one `file_facts` table and one set of six reliability
states." §3.5 settles why: "A file fact is not inherently rule-based or LLM-based. It
is the common format into which both systems write their conclusions." The producer
is a column, not a schema.

`STATES` IS `evidence_shape.vocabulary.RELIABILITY_STATES` — the same object, not a
copy, so the two cannot drift. Beside it, **one named constant per state**, spelled
here and nowhere else: every other module imports `DIRECT`, `POSSIBLE`, `VALIDATED`,
`LLM_SUPPORTED`, `USER_CONFIRMED` or `REJECTED`, never a bare literal and never an
index into `STATES`. The §3.13 prose spellings ("LLM-supported", "user
confirmed") are English; a value outside the six is a load error, not a spelling to
normalize.

**Extractors write two of the six; P6 owns all six.** P4 conformance rule 3 (P4 D11)
rejects the other four on an *observation*; `file_facts` accepts all six on a *fact*.
That boundary is asserted from both sides in `tests/p6/test_p6_states.py`.

**`rejected` has no strength.** §3.13: "A rejected fact is a proposal that the user
or validator marked as incorrect." It is an exclusion, not the bottom of a ladder: a
rejected fact that merely ranked below `possible` would be resurfaced by any
comparison that picks the strongest candidate, which is the failure §8.7 names —
"Otherwise the system will repeatedly resurface the same attractive but incorrect
grouping." Asking for its strength raises.
"""
from __future__ import annotations

from evidence_shape.vocabulary import (
    RELIABILITY_STATES as STATES,
    NotInVocabulary,
    check,
)

#: §3.13's six states, one named constant each. This module is the ONE place a state
#: name is spelled; every other module imports the constant. Never a bare literal (a
#: second home for a published vocabulary) and never an index into `STATES` (which is
#: single-homed and unreadable, and silently couples the consumer to the tuple's
#: ORDER -- reorder it and meanings change with no test failing). The repo's own
#: precedent: P5 publishes POTENTIALLY_SENSITIVE, P1 publishes SUPERSEDED_CONTENT.
#: `test_the_six_named_constants_are_exactly_the_six_states` pins each to `STATES`.
USER_CONFIRMED: str = "user_confirmed"
DIRECT: str = "direct"
VALIDATED: str = "validated"
LLM_SUPPORTED: str = "llm_supported"
POSSIBLE: str = "possible"
REJECTED: str = "rejected"

#: §3.13's five ranked states, weakest first, so `strength` is an index and the order
#: is readable in one line. §3.13's own sentence order is strongest-first; the ladder
#: is written the other way round only so that a larger number means a stronger fact.
STRENGTH_ORDER: tuple[str, ...] = (
    POSSIBLE,
    LLM_SUPPORTED,
    VALIDATED,
    DIRECT,
    USER_CONFIRMED,
)

#: The sixth state, named as excluded rather than left out silently.
EXCLUDED_STATE = REJECTED


def strength(state: str) -> int:
    """Where `state` sits on §3.13's ladder. Larger is stronger.

    Raises `NotInVocabulary` for `rejected` (an exclusion, not a rank) and for any
    string that is not one of the six.
    """
    check(state, STATES, name="reliability_state")
    if state == EXCLUDED_STATE:
        raise NotInVocabulary(
            f"{EXCLUDED_STATE!r} is §3.13's exclusion, not a rank: 'a proposal that "
            f"the user or validator marked as incorrect'. Compare membership, never "
            f"strength — a rejected fact that merely ranked below 'possible' would be "
            f"resurfaced by any comparison that picks the strongest candidate (§8.7)."
        )
    return STRENGTH_ORDER.index(state)


def is_stronger(a: str, b: str) -> bool:
    """Strictly stronger on §3.13's ladder. Both arguments must be ranked states."""
    return strength(a) > strength(b)


#: §3.6'S TWO EXCLUSIONS, AND THE FLOOR UNDER EVERY FOLDER PROPOSAL. DERIVED, NEVER
#: SPELLED: the ladder above is weakest first, `rejected` is absent from it by
#: construction (it is `EXCLUDED_STATE`, an exclusion rather than a rank), and
#: dropping the first member drops `possible` -- so one slice removes both states
#: §3.6 keeps out of a proposal and no state name is written down a second time.
#:
#: **HERE SINCE `104` §18.2 GAP 1, AND IT MOVED RATHER THAN BEING COPIED.** It was
#: defined in `facts.read_surface`, which imports `facts.supersede`; gap 1 makes
#: `supersede.preferred_of_slot` read this same line -- a `possible` clue is not one
#: of OQ6's several ANSWERS -- and `supersede` importing it back off `read_surface`
#: is an import cycle that fails at load. The constant is a projection of
#: `STRENGTH_ORDER`, `STRENGTH_ORDER` lives here, so this is where the projection
#: belongs. `read_surface` re-exports it under the same name, so every existing
#: `from facts.read_surface import PROPOSAL_ELIGIBLE_STATES` still resolves and there
#: is still exactly ONE home for the tuple rather than two that may drift.
#:
#: The plan's Task 24 body says `STRENGTH_ORDER[:-1]` and calls the last member the
#: weakest. That is the opposite of the shipped ladder and would have excluded
#: `user_confirmed` -- a user's own answer -- from every folder proposal while still
#: excluding nothing weak. Shipped code outranks the task body; see the conflict report.
PROPOSAL_ELIGIBLE_STATES: tuple[str, ...] = STRENGTH_ORDER[1:]
