"""§7.7's eight, §7.9's loop, and the ninth that does not exist."""
from __future__ import annotations

import pathlib

import pytest

from llm_harness.fixtures import FIXTURE_HANDLE_KEY, SITE_D_REASON_PAIRS
from llm_harness.placement_validation import (
    ResidualDependencies, validate_residual_response,
)
from llm_harness.vocabulary import (
    ABSTAIN as P8_ABSTAIN, ACCEPT_DIRECT, CHOOSE_BROAD_PARENT,
    CHOOSE_RESIDUAL_DESTINATION,
    INVENTED_FOLDER, LEAVE_IN_CURRENT_LOCATION,
    LEAVE_IN_PLACE as P8_LEAVE_IN_PLACE_DISPOSITION,
    MARK_PROTECTED_OR_UNSUPPORTED,
    MARK_REVIEW_LATER as P8_MARK_REVIEW_LATER, REJECT, RESIDUAL_ACTIONS,
    RESIDUAL_DESTINATION, RETURN_ACCEPTED_PACKET, RETURN_CONFIRMED_GROUP,
    RETURN_TO_PLACEMENT as P8_RETURN_DISPOSITION,
    STRONGER_RELATIONSHIP_OVERLOOKED,
)

from placement import vocabulary as v
from placement.records import ResidualContext, ReturnTarget
from placement.residual import (
    ACTION_OUTCOME, ReturnCycleExhausted, ReturnCycleLimitRequired,
    check_return_cycle, link_return, outcome_for_action,
)
from placement.store import record_decision
from p11.conftest import FIXED_CLOCK
from p11.test_p11_records import _decision


def _residual_deps(pair):
    absent = frozenset(pair.frozen_absent_nodes)
    return ResidualDependencies(
        node_exists=lambda node_id, _plan: node_id not in absent,
        # The pair's OWN sensitivity answer, not a blanket `True`: a permissive
        # stub would pass the SENSITIVITY_RESTRICTION_IGNORED pair and the fixture
        # set would stop being six distinct cases.
        sensitivity_policy=lambda *_a, **_k: pair.sensitivity_ok,
        approved_target_ids=pair.approved_target_ids)


def _verdict_for(expected_reason):
    pair = next(p for p in SITE_D_REASON_PAIRS
                if p.expected_reasons == (expected_reason,))
    verdicts, _ = validate_residual_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False, dependencies=_residual_deps(pair),
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p11-test", release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY)
    return verdicts[0]


def _verdict_for_action(action, *, target=None):
    """P8's verdict on a well-cited D response carrying one of the eight actions.

    Built from the direct-accept outcome pair rather than a reason pair, because
    the question here is what an ACCEPTED answer is recorded as.
    """
    import dataclasses
    import json

    from llm_harness.fixtures import SITE_D_OUTCOME_PAIRS

    pair = next(p for p in SITE_D_OUTCOME_PAIRS if p.name == "direct_accept")
    parsed = json.loads(pair.response_bytes)
    parsed["claims"][0]["payload"].update(action=action, target=target)
    pair = dataclasses.replace(pair, response_bytes=json.dumps(parsed).encode())
    verdicts, _ = validate_residual_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False, dependencies=_residual_deps(pair),
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p11-test", release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY)
    return verdicts[0]


# --- eight actions, one shape ------------------------------------------------------

def test_the_map_is_total_over_p8s_controlled_set_and_has_no_ninth():
    assert set(ACTION_OUTCOME) == set(RESIDUAL_ACTIONS)
    assert len(ACTION_OUTCOME) == len(RESIDUAL_ACTIONS) == 8
    assert set(ACTION_OUTCOME.values()) <= set(v.OUTCOMES)


def _load_a_fresh_copy_of_residual():
    """Execute `src/placement/residual.py` again under its own module name.

    A fresh execution is what runs the module-level assertions. Reloading
    `placement.residual` in place would leave a half-initialised module in
    `sys.modules` when the assertion fires; this loads an independent copy and
    leaves the live one untouched.
    """
    import importlib.util
    import sys
    from pathlib import Path

    path = Path(__file__).resolve().parents[2] / "src" / "placement" / "residual.py"
    spec = importlib.util.spec_from_file_location("_residual_probe", path)
    module = importlib.util.module_from_spec(spec)
    # `@dataclass` resolves annotations through `sys.modules[cls.__module__]`, so
    # the copy has to be registered while it executes -- and unregistered after,
    # so nothing else can import it by accident.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        del sys.modules[spec.name]
    return module


def test_a_ninth_p8_action_is_a_load_error_and_not_a_runtime_surprise(monkeypatch):
    # SPEC:95: "There is no ninth action on the residual path." The map is keyed
    # on P8's controlled set, so the day P8 adds one, importing this module has
    # to fail -- a contract revision, announced at load, rather than a KeyError
    # in front of a user halfway through a corpus.
    assert _load_a_fresh_copy_of_residual().ACTION_OUTCOME  # the negative twin
    import llm_harness.vocabulary as p8

    monkeypatch.setattr(p8, "RESIDUAL_ACTIONS",
                        RESIDUAL_ACTIONS + ("delete_it_quietly",))
    with pytest.raises(AssertionError):
        _load_a_fresh_copy_of_residual()


def test_the_map_cannot_grow_a_ninth_at_runtime():
    with pytest.raises(TypeError):
        ACTION_OUTCOME["organise_it_nicely"] = v.PLACE


def test_ask_user_is_never_a_residual_outcome():
    # SPEC:437-445: `ask_user` is §6.9's multi-home question and the residual path
    # is closed to the eight §7.7 actions, none of which asks.
    assert v.ASK_USER not in ACTION_OUTCOME.values()


def test_each_of_the_eight_maps_to_its_specd_outcome_and_qualifier():
    cases = (
        (RETURN_CONFIRMED_GROUP, "g-columbia", v.RETURN_TO_PLACEMENT,
         v.CONFIRMED_DOMAIN_GROUP),
        (RETURN_ACCEPTED_PACKET, "pk-1", v.RETURN_TO_PLACEMENT,
         v.ACCEPTED_GRAPH_OR_PURPOSE_PACKET),
        (CHOOSE_RESIDUAL_DESTINATION, "n-review-later", v.PLACE, "n-review-later"),
        (CHOOSE_BROAD_PARENT, "n-academics", v.PLACE, "n-academics"),
        (P8_MARK_REVIEW_LATER, None, v.MARK_REVIEW_LATER, None),
        (LEAVE_IN_CURRENT_LOCATION, None, v.LEAVE_IN_PLACE, None),
        (MARK_PROTECTED_OR_UNSUPPORTED, v.PROTECTED, v.MARK_STATE, v.PROTECTED),
        (P8_ABSTAIN, None, v.ABSTAIN, v.NO_SUPPORTED_DESTINATION),
    )
    assert len(cases) == len(RESIDUAL_ACTIONS)
    for action, target, expected_outcome, expected_payload in cases:
        outcome, payload = outcome_for_action(action, target=target)
        assert outcome == expected_outcome, action
        assert payload == expected_payload, action


def test_two_pairs_of_actions_differ_only_by_a_qualifier():
    # SPEC:386-399: this is why eight actions need no field the §6 path lacks.
    assert (ACTION_OUTCOME[RETURN_CONFIRMED_GROUP]
            == ACTION_OUTCOME[RETURN_ACCEPTED_PACKET] == v.RETURN_TO_PLACEMENT)
    assert (ACTION_OUTCOME[CHOOSE_RESIDUAL_DESTINATION]
            == ACTION_OUTCOME[CHOOSE_BROAD_PARENT] == v.PLACE)
    # And they are still two actions, not one: the qualifier differs.
    assert (outcome_for_action(RETURN_CONFIRMED_GROUP, target="g-1")[1]
            != outcome_for_action(RETURN_ACCEPTED_PACKET, target="pk-1")[1])


def test_a_place_with_no_node_is_refused_rather_than_returned():
    # `PlacementDecision` requires `destination` present exactly on `place`, so
    # `(place, None)` is a record no one can build -- and the failure would land
    # a whole stage away from the action that caused it.
    for action in (CHOOSE_RESIDUAL_DESTINATION, CHOOSE_BROAD_PARENT):
        with pytest.raises(ValueError):
            outcome_for_action(action, target=None)


def test_a_return_names_what_it_returns_to():
    # `ReturnTarget` requires a non-empty id. An action that says "send this back
    # to the confirmed group" without naming the group is unbuildable.
    for action in (RETURN_CONFIRMED_GROUP, RETURN_ACCEPTED_PACKET):
        with pytest.raises(ValueError):
            outcome_for_action(action, target=None)


def test_the_mark_takes_one_of_two_states_and_no_third():
    """RE-ARGUED for `104` R-104; the assertions are unchanged and the reason is
    not the one they were written under.

    They were written as P11 refusing to invent a third category, which is the
    right argument for a P11 CALLER that made a word up. It is not the argument
    for the word that actually arrives: `_residual_action_of` (`cli.py`:1710)
    reads site D's raw payload, so an accepted `mark_protected_or_unsupported`
    carries whatever string the MODEL wrote in `target` into this function.

    P8 is where a model's word belongs refused, and P8 cannot refuse it yet --
    the two states are this package's and no P8 module may import `placement`
    (`tests/p8/test_p8_architecture.py`'s `NEIGHBOUR_PRODUCERS`). So this raise
    is currently the run-ender `104` R-104 names, and softening it here would be
    worse than the defect: P11 "re-implements no check of P8's"
    (`placement/__init__`), and answering an abstention for a word P8 ACCEPTED
    would write the record `pipeline`:4235 reserves for an answer the validator
    threw away -- the file's record would say the model abstained when it said
    "mark protected".

    What SHOULD happen instead is pinned as a strict xfail at
    `tests/llm_harness/test_d2_contract_gaps.py::
    test_g8_a_mark_whose_state_is_neither_word_is_refused_by_p8`. The day the two
    words have a P8 home, that turns green, a stray word never reaches here, and
    these assertions go back to meaning what they say on the tin.
    """
    outcome, payload = outcome_for_action(MARK_PROTECTED_OR_UNSUPPORTED,
                                          target=v.UNSUPPORTED)
    assert (outcome, payload) == (v.MARK_STATE, v.UNSUPPORTED)
    for bad in (None, "archived", v.PLACE):
        with pytest.raises(ValueError):
            outcome_for_action(MARK_PROTECTED_OR_UNSUPPORTED, target=bad)


def test_the_two_marked_states_are_the_two_words_the_d_template_offers():
    """DESIGN: P11's `MARKED_STATES` and the words site D's ratified text tells
    the model to use are one vocabulary, not two that happen to agree.

    MEASUREMENT: both wired D templates state the pair in prose -- `"target" is
    the word "protected" or the word "unsupported"` -- and every word of
    `MARKED_STATES` appears in that sentence. `104` R-104 leaves P8 unable to
    check the pair (it may not import this package); this holds the two records
    equal so the P8 home that closes it cannot be given a different pair.
    """
    library = pathlib.Path(__file__).resolve().parents[2] / "src/llm_harness/library"
    for name in ("d_residual_template.ladder.txt",
                 "d_residual_template.shelves.txt"):
        text = (library / name).read_text()
        sentence = next(line for line in text.splitlines()
                        if line.startswith('"mark_protected_or_unsupported"'))
        for state in v.MARKED_STATES:
            assert f'the word "{state}"' in sentence, (name, state)
        assert len(v.MARKED_STATES) == sentence.count("the word ")


def test_the_three_targetless_actions_refuse_a_target():
    # Silently dropping it would let a caller believe it named a destination for
    # `leave_in_current_location` and see the file stay where it was.
    for action in (P8_MARK_REVIEW_LATER, LEAVE_IN_CURRENT_LOCATION, P8_ABSTAIN):
        assert outcome_for_action(action, target=None)
        with pytest.raises(ValueError):
            outcome_for_action(action, target="n-somewhere")


def test_an_action_outside_the_controlled_set_is_p8s_refusal_not_p11s():
    verdict = _verdict_for("ACTION_NOT_IN_CONTROLLED_SET")
    assert verdict.outcome == REJECT
    with pytest.raises(KeyError):
        outcome_for_action("organise_it_nicely", target=None)


def test_the_gate_b12_screenshot_cannot_produce_a_travel_folder():
    # §7.8's worked example, and P8 already enforces it: any target with a "/"
    # is INVENTED_FOLDER. P11 writes no second version of this check.
    verdict = _verdict_for(INVENTED_FOLDER)
    assert verdict.outcome == REJECT
    assert INVENTED_FOLDER in verdict.reasons


def test_a_stronger_relationship_hands_the_file_back_to_placement():
    # §7.9's trigger is P8's; P11 reads the disposition and emits the outcome.
    verdict = _verdict_for(STRONGER_RELATIONSHIP_OVERLOOKED)
    assert verdict.disposition == P8_RETURN_DISPOSITION
    assert ACTION_OUTCOME[RETURN_CONFIRMED_GROUP] == v.RETURN_TO_PLACEMENT


def test_p11_writes_none_of_site_ds_reason_codes():
    # Resolution O7: P8 owns the checks, P11 owns the authorities. A P11 literal
    # of a Site D code would be a second opinion with no way to be reconciled.
    import ast
    from pathlib import Path

    codes = {"ACTION_NOT_IN_CONTROLLED_SET", "DESTINATION_NOT_IN_FROZEN_TREE",
             "EVIDENCE_NOT_IN_FILE_RECORD", "SENSITIVITY_RESTRICTION_IGNORED",
             "STRONGER_RELATIONSHIP_OVERLOOKED", INVENTED_FOLDER}
    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    for path in sorted(root.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and node.value in codes:
                raise AssertionError(f"{path.name}:{node.lineno} spells {node.value}")


# --- §7.9's loop --------------------------------------------------------------------

def _returning(decision_id="r1", plan_version="plan-1", **overrides):
    values = dict(
        decision_id=decision_id, plan_version=plan_version,
        origin_stage=v.RESIDUAL, outcome=v.RETURN_TO_PLACEMENT, destination=None,
        return_target=ReturnTarget(kind=v.CONFIRMED_DOMAIN_GROUP,
                                   id="g-columbia"),
        residual=ResidualContext(set_id="s1", set_decision=v.REVIEW_WITH_MODEL,
                                 lifecycle_policy_ref=None))
    values.update(overrides)
    return _decision(**values)


def test_the_return_link_persists_both_records(p11_conn):
    # Done-means 13: the residual finding is never discarded because placement
    # later succeeded, and the second record points at the first.
    residual = _returning()
    placement = _decision(decision_id="p1", plan_version="plan-2",
                          returned_from="r1")
    record_decision(p11_conn, residual, component_version="P11-test",
                    observed_at=FIXED_CLOCK)
    record_decision(p11_conn, placement, component_version="P11-test",
                    observed_at=FIXED_CLOCK)
    link_return(p11_conn, residual_decision=residual,
                placement_decision=placement, component_version="P11-test",
                observed_at=FIXED_CLOCK)
    rows = p11_conn.execute(
        "SELECT record_id, returned_from FROM placement_decisions "
        "ORDER BY record_id").fetchall()
    assert [r["record_id"] for r in rows] == ["p1", "r1"]
    assert rows[0]["returned_from"] == "r1"
    event = p11_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.RETURN_ISSUED,)).fetchone()
    assert "r1" in event["explanation"] and "p1" in event["explanation"]


def test_a_placement_that_names_no_residual_decision_is_not_a_return(p11_conn):
    with pytest.raises(ValueError):
        link_return(p11_conn, residual_decision=_returning(),
                    placement_decision=_decision(decision_id="p1",
                                                 plan_version="plan-2"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)


def test_only_a_return_decision_can_issue_a_return(p11_conn):
    # A `leave_in_place` residual finding linked as a return would log a §7.9
    # traversal that never happened, and §8.8's diff would walk a loop with no
    # first half.
    not_a_return = _returning(
        decision_id="r1", outcome=v.LEAVE_IN_PLACE, return_target=None)
    with pytest.raises(ValueError):
        link_return(p11_conn, residual_decision=not_a_return,
                    placement_decision=_decision(decision_id="p1",
                                                 plan_version="plan-2",
                                                 returned_from="r1"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)


def test_a_return_links_one_subject_to_itself_and_not_to_another(p11_conn):
    from placement.records import Subject

    other = _decision(decision_id="p1", plan_version="plan-2", returned_from="r1",
                      subject=Subject(kind=v.FILE, file_id="f2", content_hash="h2",
                                      group_id=None, member_file_ids=()))
    with pytest.raises(ValueError) as raised:
        link_return(p11_conn, residual_decision=_returning(),
                    placement_decision=other, component_version="P11-test",
                    observed_at=FIXED_CLOCK)
    assert "f2" in str(raised.value) or "f1" in str(raised.value)


def test_the_cycle_limit_is_injected_and_absent_means_refuse(p11_conn):
    with pytest.raises(ReturnCycleLimitRequired):
        check_return_cycle(p11_conn, subject_ref="file:f1:h1",
                           max_return_cycles=None)


def test_exceeding_the_injected_cycle_limit_raises_rather_than_looping(p11_conn):
    # Two returns in two plan versions: the one-current-row index is per plan
    # version, so this is a genuine cycle rather than an illegal second live row.
    for index in (1, 2):
        record_decision(
            p11_conn, _returning(decision_id=f"r{index}",
                                 plan_version=f"plan-{index}"),
            component_version="P11-test", observed_at=FIXED_CLOCK)
    assert check_return_cycle(p11_conn, subject_ref="file:f1:h1",
                              max_return_cycles=2) == 2
    with pytest.raises(ReturnCycleExhausted) as raised:
        check_return_cycle(p11_conn, subject_ref="file:f1:h1",
                           max_return_cycles=1)
    assert "file:f1:h1" in str(raised.value)


def test_the_count_is_per_subject_and_per_outcome(p11_conn):
    # The negative twins for the two WHERE clauses. Drop `subject_ref` and every
    # file in the corpus shares one budget; drop `outcome` and an ordinary
    # placement counts as a trip round §7.9's loop.
    record_decision(p11_conn, _returning(), component_version="P11-test",
                    observed_at=FIXED_CLOCK)
    record_decision(p11_conn, _decision(decision_id="p1", plan_version="plan-2"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)
    assert check_return_cycle(p11_conn, subject_ref="file:f1:h1",
                              max_return_cycles=5) == 1
    assert check_return_cycle(p11_conn, subject_ref="file:f9:h9",
                              max_return_cycles=0) == 0


def test_a_superseded_return_is_a_corrected_record_and_not_a_second_cycle(p11_conn):
    # One traversal whose record was revised is still one traversal. Counting the
    # superseded row would exhaust an injected bound the file never reached, and
    # the partial unique index already allows exactly one live return per version
    # -- so counting live rows is what makes the number mean "trips round the
    # loop" instead of "times somebody edited the record".
    record_decision(p11_conn, _returning(decision_id="r1"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)
    record_decision(
        p11_conn, _returning(decision_id="r1b", supersedes="r1"),
        component_version="P11-test", observed_at=FIXED_CLOCK,
        supersede_reason="the return target was corrected")
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM placement_decisions").fetchone()["c"] == 2
    assert check_return_cycle(p11_conn, subject_ref="file:f1:h1",
                              max_return_cycles=1) == 1


def test_the_residual_action_path_is_reachable_from_somewhere_in_placement():
    """The three §7.7/§7.9 entry points exist and nothing in `src/placement/`
    calls them.

    `outcome_for_action` turns a validated P8 action into a decision, `link_return`
    logs §7.9's loop and `check_return_cycle` bounds it. Their owed consumer is the
    residual pass, which is not built. Until it is, the eight actions map onto
    outcomes that nothing constructs -- the exact shape of the four concepts this
    codebase shipped fully-tested and connected to nothing.

    The gap is CLOSED: `placement/pipeline.py` calls all three --
    `outcome_for_action` from `run_residual_file`, and `check_return_cycle` and
    `link_return` from §7.9's loop back into §6. The `xfail(strict=True)` marker
    that reported the gap is gone, removed by the XPASS it was written to
    produce.
    """
    from p11.test_p11_residual_sets import _placement_sources_calling

    for entry_point in ("outcome_for_action", "link_return", "check_return_cycle"):
        assert _placement_sources_calling(entry_point) - {"residual.py"}, entry_point


# --- `104` R-104: the two halves of one choice, and they disagreed ----------------


def test_p8_and_p11_record_the_same_thing_when_the_model_says_leave_it_here():
    """The ladder above has always mapped `leave_in_current_location` onto
    `leave_in_place`; P8's own record of the same answer said
    `residual_destination`.

    P11 reads the ACTION through the injected `residual_action_of` and never the
    disposition, so the two never had to agree for the file to end up in the right
    place -- which is why this went unnoticed. What disagreed is what a person and
    a replay READ: `llm_verdict` said the model had chosen a residual destination
    and `placement_decisions` said the file stayed put.

    The two constants are one string, and `placement/vocabulary.py:171-176` says so
    in the codebase's own words -- "P8 -- whose value P11's `LEAVE_IN_PLACE`
    OUTCOME is". Asserted on each side's own name so a future split of the two
    spellings breaks here rather than passing silently.
    """
    verdict = _verdict_for_action(LEAVE_IN_CURRENT_LOCATION)

    assert verdict.outcome == ACCEPT_DIRECT
    assert verdict.disposition == P8_LEAVE_IN_PLACE_DISPOSITION
    assert verdict.disposition != RESIDUAL_DESTINATION
    assert ACTION_OUTCOME[LEAVE_IN_CURRENT_LOCATION] == v.LEAVE_IN_PLACE
    assert outcome_for_action(LEAVE_IN_CURRENT_LOCATION,
                              target=None) == (v.LEAVE_IN_PLACE, None)
    assert verdict.disposition == ACTION_OUTCOME[LEAVE_IN_CURRENT_LOCATION]


def test_only_a_choice_of_destination_is_recorded_as_a_destination():
    """The two actions that DO name a home keep `residual_destination`; the fix
    above narrows that disposition to them rather than replacing it."""
    for action, target in ((CHOOSE_RESIDUAL_DESTINATION, "node-legal"),
                           (CHOOSE_BROAD_PARENT, "node-parent")):
        verdict = _verdict_for_action(action, target=target)
        assert verdict.disposition == RESIDUAL_DESTINATION, action
        assert ACTION_OUTCOME[action] == v.PLACE, action
