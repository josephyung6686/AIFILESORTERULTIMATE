"""A rejected fact may not be handed to P11 as a matching fact.

`placement/vocabulary.py` already publishes the decision, and publishes it as a
decision rather than an omission:

    #: `rejected` is deliberately absent from `EVIDENCE_TYPES` and named here so
    #: the exclusion is a published decision rather than an omission
    DROPPED_RELIABILITY_STATE: str = "rejected"
    assert DROPPED_RELIABILITY_STATE in RELIABILITY_STATES
    assert DROPPED_RELIABILITY_STATE not in EVIDENCE_TYPES

The SPEC says why: "§3.13's `rejected` is DROPPED: a rejected fact cannot support
a placement, so a record resting on one would be a contradiction rather than a
low-confidence decision -- the correct expression is `outcome = abstain`."

`MatchingFact.reliability` checked nothing. It required the field to be non-empty
and took whatever arrived, so the two asserts above described a rule with no
reachable enforcement anywhere in P11 -- and a caller that read a retracted fact
out of the store and passed it in got a placement built on a claim the person had
already said was wrong, silently, with `exact fact match` printed beside it.

This is the guard that makes that a refusal instead. It is not the whole of the
defect: a caller that mislabels a rejected row as `direct` before handing it over
is telling P11 something untrue, and no check on this side can see through that.
What it does mean is that the mistake can no longer be made quietly.
"""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.records import MatchingFact
from placement.vocabulary import (
    DROPPED_RELIABILITY_STATE, EVIDENCE_TYPES, OutOfVocabulary,
)


def test_a_rejected_fact_is_refused_as_a_matching_fact():
    """The guard. `rejected` is the one reliability state P11 will not match on."""
    with pytest.raises(OutOfVocabulary) as raised:
        MatchingFact(file_fact_id="ff-1", field="subject", value="PHYS1401",
                     reliability=DROPPED_RELIABILITY_STATE,
                     evidence_ref="obs-1")

    assert "reliability" in str(raised.value)


def test_every_other_reliability_state_still_matches():
    """The twin, over the whole published set and not one hand-picked member.

    A guard written as "refuse anything that is not `direct`" would pass the test
    above and quietly stop P11 placing on a `validated`, `user_confirmed` or
    `context-supported` fact -- which is most of what it is for. Six values, all
    of them accepted.
    """
    for state in EVIDENCE_TYPES:
        fact = MatchingFact(file_fact_id="ff-1", field="subject",
                            value="PHYS1401", reliability=state,
                            evidence_ref="obs-1")
        assert fact.reliability == state


def test_the_dropped_state_is_still_a_real_reliability_state():
    """And the exclusion stays a decision rather than a typo.

    `rejected` has to be a state P6 really writes for dropping it to mean
    anything; if the spelling drifted, this vocabulary would be excluding a value
    nothing ever produces while the real one sailed through.
    """
    from evidence_shape.vocabulary import RELIABILITY_STATES

    assert DROPPED_RELIABILITY_STATE in RELIABILITY_STATES
    assert DROPPED_RELIABILITY_STATE not in EVIDENCE_TYPES
    assert v.DIRECT in EVIDENCE_TYPES
