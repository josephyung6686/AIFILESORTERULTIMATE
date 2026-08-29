# tests/p6/test_p6_states.py
"""§3.13's six reliability states, spelled once — by P4, and re-exported here."""
import importlib
import pkgutil

import dataclasses

import pytest

from evidence_shape.conformance import validate_observation
from evidence_shape.fixtures import by_number
from evidence_shape.vocabulary import (
    EXTRACTOR_RELIABILITY_STATES, RELIABILITY_STATES, NotInVocabulary,
)

from facts.states import (
    DIRECT, EXCLUDED_STATE, LLM_SUPPORTED, POSSIBLE, REJECTED, STATES,
    STRENGTH_ORDER, USER_CONFIRMED, VALIDATED, is_stronger, strength,
)


def test_states_is_p4s_tuple_and_not_a_copy_of_it():
    # Preamble rule 2: "The six literals are P4's, already published, and P6
    # re-spells none of them." Identity, not equality: a copy would drift.
    assert STATES is RELIABILITY_STATES
    assert STATES == ("user_confirmed", "direct", "validated", "llm_supported",
                      "possible", "rejected")


def test_the_six_named_constants_are_exactly_the_six_states():
    # Preamble §3.1: the six are published BOTH ways -- `STATES` for iteration and
    # membership, one named constant for naming one state. Every other module
    # imports the constant: never a bare literal (a second home), never an index
    # (single-homed, unreadable, and coupled to the tuple's ORDER). This test is
    # what makes the literal safe to spell in `states.py` and nowhere else -- a typo
    # in one constant fails here rather than becoming a second vocabulary.
    named = (USER_CONFIRMED, DIRECT, VALIDATED, LLM_SUPPORTED, POSSIBLE, REJECTED)
    assert named == STATES
    assert len(set(named)) == 6
    for one in named:
        assert one in STATES


def test_the_3_13_prose_spellings_are_prose_and_are_not_members():
    # §3.13 writes "LLM-supported" and "user confirmed"; §3.5 writes "LLM-supported"
    # too. Those are English, not values. A value outside the six is a load error,
    # never a spelling to normalize.
    for prose in ("LLM-supported", "User-confirmed", "user confirmed", "Direct"):
        assert prose not in STATES


def test_no_module_in_facts_publishes_a_second_copy_of_the_six():
    # Preamble rule 2: "P6 publishes no second copy and no alias table." A producer
    # naming the one or two states it may write is not a copy; a module-level
    # collection whose members ARE the six is.
    import facts
    offenders = []
    for info in pkgutil.iter_modules(facts.__path__):
        module = importlib.import_module(f"facts.{info.name}")
        if module.__name__ == "facts.states":
            continue
        for name, value in vars(module).items():
            if not isinstance(value, (tuple, list, set, frozenset)):
                continue
            if all(isinstance(m, str) for m in value) and set(value) == set(STATES):
                offenders.append(f"{module.__name__}.{name}")
    assert offenders == []


def test_the_strength_order_is_3_13s_and_has_five_members():
    assert STRENGTH_ORDER == ("possible", "llm_supported", "validated", "direct",
                              "user_confirmed")
    assert strength("user_confirmed") > strength("direct") > strength("validated") \
        > strength("llm_supported") > strength("possible")
    assert set(STRENGTH_ORDER) < set(STATES)


def test_rejected_has_no_strength_because_3_13_makes_it_an_exclusion():
    # "A rejected fact is a proposal that the user or validator marked as incorrect."
    # A rejected fact that merely ranked below `possible` would be resurfaced by any
    # comparison that picks the strongest — §8.7's own failure mode.
    assert EXCLUDED_STATE == "rejected"
    assert EXCLUDED_STATE in STATES
    assert EXCLUDED_STATE not in STRENGTH_ORDER
    with pytest.raises(NotInVocabulary):
        strength("rejected")
    with pytest.raises(NotInVocabulary):
        is_stronger("direct", "rejected")


def test_a_string_that_is_not_a_state_at_all_raises_rather_than_scoring_zero():
    with pytest.raises(NotInVocabulary):
        strength("probable")
    with pytest.raises(NotInVocabulary):
        strength("")


def test_is_stronger_is_strict_and_total_over_the_five():
    assert is_stronger("direct", "possible")
    assert not is_stronger("possible", "direct")
    assert not is_stronger("direct", "direct")


def test_extractors_write_two_of_the_six_and_p6_owns_all_six(p6_conn):
    # Takes `p6_conn` so Task 1's step 4 proves the fixture builds — P1's schema plus
    # P4's three tables — before Task 2 extends it with P6's own.
    #
    # P4 conformance rule 3 / P4 D11: an *observation* may carry only `direct` or
    # `possible`. A *fact* may carry any of the six. The same tuple, two admissible
    # subsets, asserted from both sides — not a comment in a docstring.
    assert EXTRACTOR_RELIABILITY_STATES == ("direct", "possible")
    assert set(EXTRACTOR_RELIABILITY_STATES) < set(STATES)

    observation = by_number(1).observations[0]
    assert observation.reliability == "possible"
    assert validate_observation(observation) == observation

    # Verified live 2026-08-22: P4 raises NotInVocabulary here, not NonConforming.
    with pytest.raises(NotInVocabulary):
        validate_observation(dataclasses.replace(observation, reliability="validated"))

    # And the same word is a rank P6 can ask for.
    assert strength("validated") > strength("llm_supported")
