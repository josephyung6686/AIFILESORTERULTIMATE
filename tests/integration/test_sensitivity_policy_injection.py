# tests/integration/test_sensitivity_policy_injection.py
"""R-55 — the `sensitivity_policy` dependency nothing supplied.

`SENSITIVITY_RESTRICTION_IGNORED` and `SENSITIVITY_POLICY_VIOLATION` are two of
P8's fifteen placement checks and both rest on one injected predicate. Until this
work `src/cli.py` passed `None` for it and every test in the tree stubbed it
`True` or read a fixture's own `sensitivity_ok` flag, so no test anywhere asked
P7 the question. The measured consequence is in the D2 bakeoff: both local D
texts filed the redacted statement into Receipts and P8 accepted it.

**The policy is an adapter, not a rule.** §8.4's automatic-move predicate already
exists and is published: `privacy.moves.may_move_automatically` reads the same two
P7 facts the gate reads -- the live classification record and, for a protected
one, the user policy that permits its move -- refuses by default and writes
nothing. Everything here wires that answer to Sites C and D. If a test in this
file ever needs a new branch of judgement, the branch belongs in P7.

**Three things this file pins that are easy to get wrong.**

  * The subject address. `placement.store.subject_ref_of` spells a file as
    `file:<id>:<hash>`; P8's own fixtures use the shorthand `file-1`. The adapter
    parses the real one and refuses anything else, so the tests below build the
    real one rather than asserting against the shorthand.
  * A response that moves nothing cannot violate a move restriction.
    `leave_in_current_location` and `mark_review_later` carry no target and are
    permitted for a protected file -- refusing them would push a protected file
    OUT of the one disposition that leaves it alone.
  * An unclassified file is refused, not permitted. That is P7's branch order and
    its docstring says why. On a corpus nothing has classified it means every
    file, which is a real coverage cost and is asserted here by name rather than
    left for someone to discover.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from cli import sensitivity_policy_for

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from llm_harness.fixtures import (
    FIXTURE_HANDLE_KEY, PLAN_V1, SITE_C_REASON_PAIRS, SITE_D_REASON_PAIRS,
)
from llm_harness.placement_validation import (
    PlacementDependencies, ResidualDependencies,
    validate_placement_response, validate_residual_response,
)
from llm_harness.vocabulary import (
    LEAVE_IN_CURRENT_LOCATION, MARK_REVIEW_LATER,
    SENSITIVITY_POLICY_VIOLATION, SENSITIVITY_RESTRICTION_IGNORED,
)

from placement.records import Subject
from placement.store import subject_ref_of
from placement.vocabulary import FILE, GROUP

from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.schema import create_privacy_schema
from privacy.vocabulary import USER, USER_CONFIRMED

CLOCK = "2026-09-06T12:00:00+00:00"
COMPONENT = "0.1.0"
#: `llm_harness.fixtures` builds both site dossiers under this plan version and
#: the adapter reads the version off the dossier, so the policy row below is
#: written against the fixtures' own constant rather than a copy of it.
PLAN = PLAN_V1


# --- the substrate: one real P1 file and P7's own tables ---------------------------

@pytest.fixture()
def db(conn):
    """P1's tables plus P7's. Nothing else: the adapter reads `files`,
    `classifications` and `policies` and touches no other part's store."""
    create_schema(conn)
    create_privacy_schema(conn)
    return conn


@pytest.fixture()
def file_id(db, tmp_path):
    """A real `record_file` row, because the classification is keyed on
    `(file_id, content_hash)` and `record_file` is what computes the hash."""
    folder = tmp_path / "corpus"
    folder.mkdir(exist_ok=True)
    document = folder / "redacted-statement.pdf"
    document.write_bytes(b"%PDF-1.4 account ending 4242")
    return record_file(
        db, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(folder), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def subject_ref(db, file_id) -> str:
    """P11's own address for this file version, built by P11's own function."""
    return subject_ref_of(Subject(
        kind=FILE, file_id=file_id, content_hash=get_file(db, file_id)["content_hash"],
        group_id=None, member_file_ids=()))


def classify(db, file_id, *, protected: bool, handling_class: str) -> None:
    """P7's own store. `basis=USER` because no detector fired -- Task 3 refuses a
    detector record with no `evidence_refs`, and inventing one would be a fixture
    claiming a capability D2 says this product does not have."""
    ClassificationStore(db).write(ClassificationRecord(
        file_id=file_id, content_hash=get_file(db, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis=USER,
        evidence_refs=(), reliability_state=USER_CONFIRMED, observed_at=CLOCK))


def permit_the_move(db, file_id) -> None:
    """The user policy §8.4 requires before protected material may move."""
    set_policy(db, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="offline",
        consent_grants=(),
        redaction_settings={"names": "redacted", "previews": "redacted",
                            "thumbnails": "redacted", "ocr_text": "redacted",
                            "location_data": "redacted"},
        automatic_move_permissions={file_id: True}, plan_version=PLAN,
        set_at=CLOCK), component_version=COMPONENT, user_id="joseph",
        reason="the person permitted this one file to move")


# --- the two dossiers, addressed to the real file ---------------------------------

def _pair_named(pairs, reason):
    return next(p for p in pairs if p.expected_reasons == (reason,))


def _residual_case(subject_ref):
    """P8's own D13 pair, re-addressed to a file that exists.

    `_same_file_evidence` refuses a residual response whose evidence sits outside
    the dossier's subject, so the excerpt's `location` moves with the subject.
    Everything else -- the response bytes, the approved set, the vocabulary -- is
    the recorded fixture untouched.
    """
    pair = _pair_named(SITE_D_REASON_PAIRS, SENSITIVITY_RESTRICTION_IGNORED)
    item = dataclasses.replace(pair.dossier.evidence_items[0], location=subject_ref)
    return pair, dataclasses.replace(
        pair.dossier, subject_ref=subject_ref, evidence_items=(item,))


def _placement_case(subject_ref):
    pair = _pair_named(SITE_C_REASON_PAIRS, SENSITIVITY_POLICY_VIOLATION)
    return pair, dataclasses.replace(pair.dossier, subject_ref=subject_ref)


def _residual_reasons(db, pair, dossier):
    absent = frozenset(pair.frozen_absent_nodes)
    verdicts, _ = validate_residual_response(
        dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False,
        dependencies=ResidualDependencies(
            node_exists=lambda node_id, _plan: node_id not in absent,
            sensitivity_policy=sensitivity_policy_for(db),
            approved_target_ids=pair.approved_target_ids),
        model_id="r55-model", prompt_fingerprint="fp-canonical",
        dossier_builder="r55-test", release_audit_id=17,
        handle_key=FIXTURE_HANDLE_KEY)
    return verdicts[0]


def _placement_reasons(db, pair, dossier):
    absent = frozenset(pair.frozen_absent_nodes)
    verdicts, _ = validate_placement_response(
        dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False,
        dependencies=PlacementDependencies(
            node_exists=lambda node_id, _plan: node_id not in absent,
            support_threshold=0.0, margin_predicate=lambda *_a, **_k: True,
            sensitivity_policy=sensitivity_policy_for(db)),
        model_id="r55-model", prompt_fingerprint="fp-canonical",
        dossier_builder="r55-test", release_audit_id=17,
        handle_key=FIXTURE_HANDLE_KEY)
    return verdicts[0]


# --- the two tests the item names ------------------------------------------------

def test_a_protected_file_into_an_approved_residual_target_is_refused_by_name(
        db, file_id, subject_ref):
    # D13 through the product's own validator, with P7 answering instead of a stub.
    classify(db, file_id, protected=True, handling_class="sensitive_personal")
    pair, dossier = _residual_case(subject_ref)
    verdict = _residual_reasons(db, pair, dossier)
    assert SENSITIVITY_RESTRICTION_IGNORED in verdict.reasons
    assert verdict.disposition == pair.expected_disposition


def test_an_ordinary_file_into_the_same_approved_target_is_not_refused(
        db, file_id, subject_ref):
    # The control. Without it the test above would pass against an adapter that
    # refuses everything, which is the other way to make a corpus place nothing.
    classify(db, file_id, protected=False, handling_class="personal_non_sensitive")
    pair, dossier = _residual_case(subject_ref)
    assert SENSITIVITY_RESTRICTION_IGNORED not in _residual_reasons(
        db, pair, dossier).reasons


def test_the_same_protected_file_is_refused_at_the_placement_site_too(
        db, file_id, subject_ref):
    # One adapter, two flags: §6.12 step 7 spells Site C's refusal differently.
    classify(db, file_id, protected=True, handling_class="sensitive_personal")
    pair, dossier = _placement_case(subject_ref)
    assert SENSITIVITY_POLICY_VIOLATION in _placement_reasons(db, pair, dossier).reasons


def test_a_placement_of_an_ordinary_file_is_not_refused_on_sensitivity(
        db, file_id, subject_ref):
    classify(db, file_id, protected=False, handling_class="personal_non_sensitive")
    pair, dossier = _placement_case(subject_ref)
    assert SENSITIVITY_POLICY_VIOLATION not in _placement_reasons(
        db, pair, dossier).reasons


# --- the branches P7 owns, read back through the adapter --------------------------

def test_a_user_policy_permitting_this_files_move_lifts_the_refusal(
        db, file_id, subject_ref):
    # §8.4: protected material may not move "without a user policy that explicitly
    # permits it" -- which means WITH one it may. A policy that could not lift the
    # refusal would make the permission the person granted unreadable.
    classify(db, file_id, protected=True, handling_class="sensitive_personal")
    permit_the_move(db, file_id)
    pair, dossier = _residual_case(subject_ref)
    assert SENSITIVITY_RESTRICTION_IGNORED not in _residual_reasons(
        db, pair, dossier).reasons


def test_an_unclassified_file_is_refused_and_that_is_the_coverage_cost(
        db, file_id, subject_ref):
    """No classification record at all -- the state of most of a real corpus.

    P7 answers `unreadable_unclassified` and refuses, and its own docstring says
    why the branch order is not interchangeable: answering `not_protected` for a
    corpus nothing has classified is §8.6's forbidden move reached sideways. So
    this is the honest answer and it is also expensive. The number is already
    measured and written down -- `src/cli.py`'s `model_route_permitted` records it
    from the 2026-09-05 run over the owner's ground-truth corpus: 95 of 199 files
    carry no classification record. Every one of them is refused here.
    """
    pair, dossier = _residual_case(subject_ref)
    assert SENSITIVITY_RESTRICTION_IGNORED in _residual_reasons(
        db, pair, dossier).reasons


# --- what the adapter refuses to answer about ------------------------------------

def test_a_group_subject_is_refused_rather_than_guessed(db):
    policy = sensitivity_policy_for(db)
    dossier = _pair_named(SITE_D_REASON_PAIRS, SENSITIVITY_RESTRICTION_IGNORED).dossier
    group = dataclasses.replace(dossier, subject_ref=f"{GROUP}:g-1")
    assert policy(group, {"action": "choose_residual_destination",
                          "target": "node-legal"}) is False


def test_a_subject_naming_a_file_that_is_not_in_the_database_is_refused(db):
    policy = sensitivity_policy_for(db)
    dossier = _pair_named(SITE_D_REASON_PAIRS, SENSITIVITY_RESTRICTION_IGNORED).dossier
    absent = dataclasses.replace(dossier, subject_ref=f"{FILE}:no-such-file:deadbeef")
    assert policy(absent, {"action": "choose_residual_destination",
                           "target": "node-legal"}) is False


def test_the_shorthand_subject_ref_the_fixtures_use_is_not_read_as_a_file_id(db):
    # `file-1` is P8 fixture shorthand, not `subject_ref_of`'s output. Reading it
    # as a file id would make the adapter answer about a file nobody addressed.
    policy = sensitivity_policy_for(db)
    dossier = _pair_named(SITE_D_REASON_PAIRS, SENSITIVITY_RESTRICTION_IGNORED).dossier
    assert policy(dossier, {"action": "choose_residual_destination",
                            "target": "node-legal"}) is False


@pytest.mark.parametrize("action", [LEAVE_IN_CURRENT_LOCATION, MARK_REVIEW_LATER])
def test_a_response_that_moves_nothing_is_permitted_for_a_protected_file(
        db, file_id, subject_ref, action):
    # The disposition that leaves a protected file alone is the SAFE one. Refusing
    # it would be the policy pushing protected material out of its own shelter.
    classify(db, file_id, protected=True, handling_class="sensitive_personal")
    policy = sensitivity_policy_for(db)
    _pair, dossier = _residual_case(subject_ref)
    assert policy(dossier, {"action": action, "target": None}) is True


def test_a_protected_file_is_still_refused_when_the_response_names_a_target(
        db, file_id, subject_ref):
    classify(db, file_id, protected=True, handling_class="sensitive_personal")
    policy = sensitivity_policy_for(db)
    _pair, dossier = _residual_case(subject_ref)
    assert policy(dossier, {"action": "choose_residual_destination",
                            "target": "node-legal"}) is False


# --- the injection itself ---------------------------------------------------------

def test_the_composition_root_no_longer_passes_none_for_the_policy():
    """`src/cli.py` built `PipelineInputs` with `sensitivity_policy=None` on every
    run this product has ever made. The eight model-path fields are withheld
    together on purpose and seven of them still are; this one is not a model-path
    injection in the same sense -- `model_path_available` reads it, but P8 uses it
    to REFUSE, and a refusal that needs no prompt should not wait for one.
    """
    import inspect

    import cli

    source = inspect.getsource(cli)
    assert "sensitivity_policy=None" not in source
    assert "sensitivity_policy=sensitivity_policy_for(conn)" in source
