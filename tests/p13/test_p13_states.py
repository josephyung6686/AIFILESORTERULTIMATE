"""`66` §4: five states, five sentences, and never one vague message.

    "Find must name the state that actually applies. [...] These states should
    never share one vague message such as 'could not find.'"

`74` §6 B3's named test is `test_the_five_absence_states_have_five_distinct_messages`
and its negative twin is `test_two_states_sharing_a_message_fails`. The twin is a
twin in the house sense: it goes red against a `states.py` whose sentence table
gives two states the same words, which is exactly the collapse `66` §4 forbids
and the one a copy-edit pass would introduce by accident.
"""
from __future__ import annotations

import pytest

from review_surface.states import (
    ABSENCE_NO_STRONG_MATCH,
    ABSENCE_PROTECTED,
    ABSENCE_SENTENCES,
    ABSENCE_STATES,
    ABSENCE_STILL_INDEXING,
    ABSENCE_UNREADABLE,
    ABSENCE_UNSUPPORTED,
    AbsenceNotice,
    StatesCollapsed,
    absence_notices,
    one_message_for,
)
from review_surface.vocabulary import OutOfVocabulary


def test_the_five_absence_states_have_five_distinct_messages():
    """`74` §6 B3's named test. Five states in, five different sentences out."""
    assert ABSENCE_STATES == (
        "protected", "unreadable", "unsupported_format", "still_indexing",
        "no_strong_match")
    sentences = [ABSENCE_SENTENCES[state] for state in ABSENCE_STATES]
    assert len(set(sentences)) == len(ABSENCE_STATES)
    for sentence in sentences:
        assert sentence
        assert "could not find" not in sentence.lower(), (
            "`66` §4 names this as the vague message the five states exist to "
            "replace")
    # And each says what `66` §4 says that state MEANS. The wording is deferred
    # design; the DISTINCTION is contractual, so each is pinned to its own idea.
    assert "privacy policy" in ABSENCE_SENTENCES[ABSENCE_PROTECTED]
    assert "read" in ABSENCE_SENTENCES[ABSENCE_UNREADABLE]
    assert "extractor" in ABSENCE_SENTENCES[ABSENCE_UNSUPPORTED]
    assert "indexing" in ABSENCE_SENTENCES[ABSENCE_STILL_INDEXING]
    assert "match" in ABSENCE_SENTENCES[ABSENCE_NO_STRONG_MATCH]


def test_two_states_sharing_a_message_fails():
    """`74` §6 B3's negative twin, run against the live table AND a sabotage one.

    The check is a function so that it can be pointed at a table that is not the
    package's. Asserting only against the real table would pass identically if
    `ABSENCE_STATES` were empty, and would not show that the check can fail.
    """
    def collapsed(sentences):
        """Every message two or more states share."""
        seen: dict[str, list[str]] = {}
        for state in ABSENCE_STATES:
            seen.setdefault(sentences[state], []).append(state)
        return [states for states in seen.values() if len(states) > 1]

    assert collapsed(ABSENCE_SENTENCES) == []
    # Sabotage: 'unreadable' and 'unsupported_format' are given one message, the
    # single most plausible merge -- both read as "we could not use this file".
    sabotaged = dict(ABSENCE_SENTENCES)
    sabotaged[ABSENCE_UNSUPPORTED] = sabotaged[ABSENCE_UNREADABLE]
    assert collapsed(sabotaged) == [[ABSENCE_UNREADABLE, ABSENCE_UNSUPPORTED]]
    # And the vague message itself, given to all five, is caught as one group.
    assert collapsed({state: "Could not find." for state in ABSENCE_STATES}) == [
        list(ABSENCE_STATES)]


def test_asking_for_one_message_over_two_states_raises_with_both_named():
    with pytest.raises(StatesCollapsed) as caught:
        one_message_for([ABSENCE_PROTECTED, ABSENCE_UNREADABLE])
    assert "protected" in str(caught.value)
    assert "unreadable" in str(caught.value)


def test_asking_for_one_message_over_one_state_still_raises():
    """The function exists only to be the place the collapse is refused."""
    with pytest.raises(StatesCollapsed):
        one_message_for([ABSENCE_PROTECTED])


def test_notices_are_produced_per_state_and_a_zero_count_is_omitted():
    notices = absence_notices(
        {ABSENCE_PROTECTED: 14, ABSENCE_UNREADABLE: 0,
         ABSENCE_STILL_INDEXING: 89},
        explanation_refs={ABSENCE_PROTECTED: "help/protected",
                          ABSENCE_STILL_INDEXING: "help/indexing"})
    assert [n.state for n in notices] == [ABSENCE_PROTECTED,
                                          ABSENCE_STILL_INDEXING]
    assert [n.count for n in notices] == [14, 89]


def test_every_notice_carries_a_reachable_explanation():
    """`66` §4 requires a reachable explanation of what the state means and why.

    `67` §1 makes this the standing constraint for the protected state in
    particular: marked and counted, never opened, and never silently omitted.
    """
    with pytest.raises(ValueError):
        AbsenceNotice(state=ABSENCE_PROTECTED, count=1, explanation_ref="")


def test_a_notice_with_a_zero_count_cannot_be_constructed():
    """A state with nothing in it is not a state to report; it is silence, and
    `66` §4's point is that silence is what must not happen for a NON-zero one."""
    with pytest.raises(ValueError):
        AbsenceNotice(state=ABSENCE_PROTECTED, count=0,
                      explanation_ref="help/protected")


def test_an_unknown_state_is_refused():
    with pytest.raises(OutOfVocabulary):
        AbsenceNotice(state="could_not_find", count=1, explanation_ref="help")
