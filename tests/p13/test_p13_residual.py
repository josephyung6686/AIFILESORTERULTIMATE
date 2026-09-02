"""§7.5's residual screen and §7.6's ordering. `74` §6 B4 and B5.

    "The residual process should begin with a visible residual surfacing screen,
    not an automatic cleanup operation."
    "The system should divide these files into understandable review sets using
    reliable characteristics, rather than presenting a single intimidating pile."

B4's named test is `test_every_residual_set_presents_all_seven_attributes` with
twin `test_a_set_missing_an_attribute_is_a_failure_not_a_blank`. B5's is
`test_no_per_file_view_is_constructible_before_a_set_decision_is_recorded` with
twin `test_a_per_file_view_built_from_an_absent_decision_is_refused`.

SPEC Open question 2 is OPEN -- whether §7.5's eight-way partition is canonical or
illustrative. §7.5's eight lines are prefaced "It may show" and P11 defers the
partition, so NOTHING here asserts a number of sets or names one after the
design's eight.
"""
from __future__ import annotations

import dataclasses

import pytest

from placement.residual import (
    LEAVE_IN_PLACE,
    REVIEW_WITH_MODEL,
    SEND_TO_APPROVED_NODE,
    SET_CHOICES,
    ResidualSet,
    ResidualSetDecision,
    SetDecisionRequired,
    record_set_decision,
)

from review_surface.residual import (
    SEVEN_ATTRIBUTES,
    WEAK_NEIGHBOURS,
    IncompleteResidualCard,
    residual_card,
    residual_file_view,
    residual_screen,
)

T0 = "2026-08-29T00:00:00Z"


def _set(**overrides) -> ResidualSet:
    count = overrides.pop("file_count", 58)
    values = dict(
        set_id="set-1", plan_version="plan-1",
        label="screenshots with no accepted project or event",
        file_count=count,
        representative_examples=("f-1", "f-2", "f-3"),
        file_type_distribution=(("png", 51), ("jpg", 7)),
        age_range=("2024-03", "2026-08"),
        evidence_availability="OCR text available for 44 of 58",
        sensitivity_status="none flagged", protected=False,
        weak_graph_neighbours=("g-reference-clips",),
        reason_not_placed=("no fact reached a legal destination and no accepted "
                           "group claimed them"),
        member_file_ids=tuple(f"f-{n}" for n in range(count)))
    values.update(overrides)
    return ResidualSet(**values)


# --------------------------------------------------------------------------
# B4 -- the seven attributes.
# --------------------------------------------------------------------------

def test_every_residual_set_presents_all_seven_attributes(p13_conn):
    """`74` §6 B4's named test, and Done-means 5.

    §7.5: each set "should display representative examples, file-type
    distribution, age range, available OCR or text evidence, sensitivity status,
    any weak graph neighbors, and the reason the system could not safely place
    the files through the normal pipeline."
    """
    assert SEVEN_ATTRIBUTES == (
        "representative_examples", "file_type_distribution", "age_range",
        "evidence_availability", "sensitivity_status", "weak_graph_neighbours",
        "reason_not_placed")
    assert len(SEVEN_ATTRIBUTES) == 7
    card = residual_card(_set())
    for name in SEVEN_ATTRIBUTES:
        assert card.attribute(name) not in (None, "", (), {}), (
            f"{name} is one of §7.5's seven; a card is not shorter without it")


def test_a_set_missing_an_attribute_is_a_failure_not_a_blank(p13_conn):
    """`74` §6 B4's negative twin, once per attribute.

    A card that silently drops an attribute looks complete while hiding the very
    thing the user needs in order to decide, which is the difference between a
    screen that helps and one that only appears to.
    """
    blanks = {"representative_examples": (), "weak_graph_neighbours": (),
              "file_type_distribution": (), "age_range": (),
              "evidence_availability": "", "sensitivity_status": "",
              "reason_not_placed": "x"}
    assert set(blanks) == set(SEVEN_ATTRIBUTES)
    for name in SEVEN_ATTRIBUTES:
        if name == "reason_not_placed":
            # P11's own record already refuses an empty reason, so the blank
            # cannot even be constructed. The rule is enforced upstream and the
            # card does not get to be the second home for it.
            with pytest.raises(ValueError):
                _set(reason_not_placed="")
            continue
        if name == WEAK_NEIGHBOURS:
            # The one of the seven §7.5 qualifies. See the test below: an empty
            # tuple here is the set's ANSWER, so it is checked there rather than
            # among the blanks, and this loop still covers the other five.
            continue
        with pytest.raises(IncompleteResidualCard) as caught:
            residual_card(_set(**{name: blanks[name]}))
        assert name in str(caught.value)
        assert caught.value.missing == [name]


def test_a_set_with_no_weak_neighbours_answers_with_none_rather_than_a_sentinel(
        p13_conn):
    """§7.5 qualifies exactly one of the seven, and the word is "ANY".

        "...sensitivity status, ANY weak graph neighbors, and the reason the
        system could not safely place the files..."

    Every other attribute is named flat. So a set with no weak graph neighbours
    has a true answer -- there are none -- and `()` is that answer rather than a
    producer who did not fill the field in. Treating the two alike is what this
    test's predecessor documented as design: it asserted a card built with
    `weak_graph_neighbours=("none",)`, which is a producer inventing a sentinel
    to get past the check, and a card that would then display a weak neighbour
    named "none" to a person.

    The twin is the second half. `age_range` carries no such qualifier, so an
    empty one is still a rendering failure, and a fix that simply stopped
    checking emptiness would pass the first assertion here and fail the second.
    """
    card = residual_card(_set(weak_graph_neighbours=()))
    assert card.weak_graph_neighbours == ()

    with pytest.raises(IncompleteResidualCard):
        residual_card(_set(age_range=()))


def test_the_refusal_names_which_attributes_are_missing_as_data(p13_conn):
    """So a composition root can print the gap instead of printing a traceback.

    `84` §6: what the screen tells a person has to be true, and a person whose
    build cannot answer two of §7.5's seven is owed those two by name rather than
    a stack trace or a screen that never renders. The names are on the exception
    as a list, not only inside its message, because a caller cannot act on prose.
    """
    with pytest.raises(IncompleteResidualCard) as caught:
        residual_card(_set(age_range=(), file_type_distribution=()))
    assert caught.value.missing == ["file_type_distribution", "age_range"]


def test_the_summary_line_and_the_cards_cannot_disagree(p13_conn):
    """§7.5's own sentence, and its number summed from the cards themselves.

    A summary saying 146 above cards totalling 131 is the two-denominator bug
    D11 was ruled on, so the total is derived and never passed in.
    """
    screen = residual_screen(
        (_set(file_count=58, set_id="set-1"),
         _set(file_count=88, set_id="set-2", label="standalone PDFs and forms")),
        plan_version="plan-1")
    assert screen.total_unplaced == 146
    assert "146" in screen.summary_line
    assert sum(card.file_count for card in screen.cards) == screen.total_unplaced


def test_the_screen_assumes_no_number_of_sets_and_no_set_names(p13_conn):
    """SPEC Open question 2 is OPEN: §7.5's eight lines are prefaced "It may show"."""
    assert residual_screen((), plan_version="plan-1").cards == ()
    assert len(residual_screen(
        tuple(_set(set_id=f"set-{n}") for n in range(3)),
        plan_version="plan-1").cards) == 3


def test_every_card_offers_p11_s_four_set_choices_and_no_others(p13_conn):
    """§7.6's four choices, imported from P11 rather than respelled."""
    assert residual_card(_set()).choices == SET_CHOICES
    assert len(SET_CHOICES) == 4


def test_the_protected_flag_rides_along_and_is_not_one_of_the_seven(p13_conn):
    """`67` §1: marked and counted, never silently omitted -- and never one of
    the seven, because Done-means 5 says seven."""
    card = residual_card(_set(protected=True))
    assert card.protected is True
    assert "protected" not in SEVEN_ATTRIBUTES


def test_a_card_carries_no_member_file_id_list(p13_conn):
    """Done-means 15's precondition: a set must not be expandable into a file
    list by the card alone. `member_file_ids` stays on P11's record."""
    names = {f.name for f in dataclasses.fields(residual_card(_set()))}
    assert "member_file_ids" not in names


# --------------------------------------------------------------------------
# B5 -- §7.6's ordering. The set decision comes first, or there is no view.
# --------------------------------------------------------------------------

class _Spy:
    """Counts every time anything asks for per-file recommendations."""

    def __init__(self, items=()):
        self.calls = 0
        self.items = tuple(items)

    def __call__(self, set_id):
        self.calls += 1
        return self.items


def _decide(conn, choice, *, set_id="set-1", node_id=None):
    record_set_decision(
        conn,
        ResidualSetDecision(set_id=set_id, plan_version="plan-1",
                            choice=choice, node_id=node_id, decided_at=T0),
        component_version="p13-1", observed_at=T0, user_id="jy")


def test_no_per_file_view_is_constructible_before_a_set_decision_is_recorded(
        p13_conn):
    """`74` §6 B5's named test, and Done-means 6's first clause.

    A caller-side `if` is a rule one caller can forget; a constructor that cannot
    produce the object is a rule nobody can forget.
    """
    spy = _Spy(("rec-1",))
    with pytest.raises(SetDecisionRequired) as caught:
        residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                           recommendations_for=spy)
    assert "set-1" in str(caught.value)
    assert spy.calls == 0, (
        "recommendations were fetched for a set with no decision")


def test_a_per_file_view_built_from_an_absent_decision_is_refused(p13_conn):
    """`74` §6 B5's negative twin. Three absences, none of which yields a view.

    Each is a different way the decision can be missing -- never taken, taken for
    a different set, taken against a different plan version -- and in all three
    the spy must stay at zero, because §7.6's cost promise is about the CALL not
    being made rather than about the result being discarded afterwards.
    """
    _decide(p13_conn, REVIEW_WITH_MODEL, set_id="set-1")
    for plan_version, set_id in (("plan-1", "set-never-decided"),
                                 ("plan-2", "set-1"),
                                 ("plan-2", "set-never-decided")):
        spy = _Spy(("rec-1",))
        with pytest.raises(SetDecisionRequired):
            residual_file_view(p13_conn, plan_version=plan_version,
                               set_id=set_id, recommendations_for=spy)
        assert spy.calls == 0, (
            f"{plan_version}/{set_id} produced a recommendation request")


def test_a_leave_in_place_set_produces_zero_recommendations_and_zero_calls(
        p13_conn):
    """Done-means 6, second clause: it must cost zero model calls."""
    _decide(p13_conn, LEAVE_IN_PLACE)
    spy = _Spy(("rec-1", "rec-2"))
    view = residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                              recommendations_for=spy)
    assert view.recommendations == ()
    assert view.model_calls_permitted is False
    assert spy.calls == 0


def test_a_review_with_model_set_reaches_its_recommendations(p13_conn):
    _decide(p13_conn, REVIEW_WITH_MODEL)
    spy = _Spy(("rec-1", "rec-2"))
    view = residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                              recommendations_for=spy)
    assert view.recommendations == ("rec-1", "rec-2")
    assert view.model_calls_permitted is True
    assert spy.calls == 1


def test_a_send_to_approved_node_set_needs_no_model_and_asks_for_none(p13_conn):
    _decide(p13_conn, SEND_TO_APPROVED_NODE, node_id="n-residual")
    spy = _Spy(("rec-1",))
    view = residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                              recommendations_for=spy)
    assert view.model_calls_permitted is False
    assert view.recommendations == ()
    assert spy.calls == 0


def test_the_view_carries_the_decision_it_was_gated_on(p13_conn):
    _decide(p13_conn, REVIEW_WITH_MODEL)
    view = residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                              recommendations_for=_Spy())
    assert view.set_decision.choice == REVIEW_WITH_MODEL
    assert view.set_decision.set_id == "set-1"
