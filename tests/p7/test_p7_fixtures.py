# tests/p7/test_p7_fixtures.py
"""Done-means 11's first clause, and its second clause named as P8's rather than faked.

SPEC §11: "Request -> decision pairs, one per `Denied.reason`, plus: a clean
`Released` with redaction applied; a `NeedsConsent` returning all four options; a
protected file under each of the four modes; an `unreadable_unclassified` file; a
`Protected Records` residual request. Each fixture carries the audit record the gate
would have appended."

The second sentence is what makes this worth doing and what makes it hard. A fixture
carrying a HAND-WRITTEN audit record is a second implementation of the gate, and it
drifts from the first invisibly because both sides belong to P7. So every fixture here
is replayed through the real gate against a real database and compared field for
field, and only the identity fields a replay cannot preserve are excused -- by name,
in a frozen set, so the excuse list cannot grow quietly.
"""
from __future__ import annotations

import dataclasses
import importlib
import inspect

import pytest

from database_agent.budget import set_ceiling
from database_agent.files_table import record_file, set_extraction_status

from evidence_shape.fixtures import FIXTURES as P4_FIXTURES
from evidence_shape.store import (
    observation_keys_for_run, record_observation, record_run, record_text_unit,
)

from extractors.long_tail import (
    POTENTIALLY_SENSITIVE, SensitivitySignal, record_sensitivity_signals,
)

from privacy.audit import AUDIT_FIELDS, audit_record
from privacy.classification import ClassificationRecord, UNREADABLE_UNCLASSIFIED
from privacy.classification_store import ClassificationStore, GateOutcomeNotAFileFact
from privacy.fixtures import (
    EXTRA_OBSERVATIONS, FIXTURE_AREA, FIXTURE_BYTES, FIXTURE_CLOCK,
    FIXTURE_COMPONENT_VERSION, FIXTURE_COVERAGE, FIXTURE_RETRACTION_LIMIT,
    FIXTURE_USER_ID, FIXTURES, GATE_ARGUMENTS, GateFixture, MINTED_DECISION_FIELDS,
    MODE_SWEEP, SPEC_11_ITEMS, UNEXTRACTED_CONTENT_HASH, WHOLE_UNIT_OBSERVATION,
    WHOLE_UNIT_P4_FIXTURE, UnknownFixture, by_number, gate_arguments,
)
from privacy.gate import Gate
from privacy.items import Filename
from privacy.policy import current_policy, set_policy
from privacy.release import Denied, Released, Target
from privacy.revocation import revoke
from privacy.vocabulary import (
    CONSENT_OPTIONS, DENIAL_REASONS, HANDLING_CLASSES, OPERATION_MODES,
)
from privacy.consent import NeedsConsent

CEILING_KEY = "model.max_dossier_tokens_per_call"

#: The fields a replay cannot preserve, each because something downstream MINTS it.
#:
#: `file_id` / `file_ids` -- `record_file` mints P1's opaque id.
#: `policy_version` / `authorizing_policy` -- `policy._persist` mints
#: `policy-{uuid4}` and REFUSES a caller-supplied version
#: (`CallerSuppliedPolicyVersion`), so a fixture that stated one could not be seeded
#: at all. This is the plan's draft corrected against the shipped module.
#:
#: Everything else -- content hash, observation key, locator, span, mode, outcome,
#: sensitivity, redaction flag, timestamps -- is content-addressed or caller-supplied
#: and survives, so it is compared.
SUBSTITUTED_FIELDS = frozenset(
    {"file_id", "file_ids", "policy_version", "authorizing_policy"})

#: Minted by the gate at call time, so a fixture can carry an example and never the
#: value. `audit_id` is P1's `lastrowid`.
#:
#: `release_id` is NOT here, and D14 is why: `_release_record` sets it to `None`
#: unconditionally, because §6 appends the audit BEFORE the release exists and `events`
#: is append-only, so the row can never be back-filled. It is a compared field whose
#: value is `None` on every record including a release, and the join runs
#: ledger -> events. Excusing it is what let an earlier draft publish a release_id the
#: gate cannot produce.
MINTED_FIELDS = frozenset({"audit_id"})


def p4(number: int):
    found = [f for f in P4_FIXTURES if f.number == number]
    assert found, f"P4 fixture {number} does not exist"
    return found[0]


def seed(conn, fixture: GateFixture, tmp_path) -> str:
    """A real `files` row, a real P4 substrate, a real policy, a real classification.

    Nothing here is synthesized past P1's own writer. `record_file` takes an explicit
    `content_hash` with `materialized=False`, which is what lets the row carry P4's
    fixture hash -- and therefore what makes the seeded `observation_key` identical to
    the published one. Without that, every excerpt in every fixture would address an
    observation the replay had not written.
    """
    source = p4(fixture.p4_fixture) if fixture.p4_fixture is not None else None
    content_hash = (source.run.content_hash if source is not None
                    else UNEXTRACTED_CONTENT_HASH)
    corpus = tmp_path / f"corpus-{fixture.number}"
    corpus.mkdir(parents=True, exist_ok=True)
    document = corpus / "fixture-document.pdf"
    document.write_bytes(FIXTURE_BYTES)
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size, observed_timestamps='{"mtime": 1.0}',
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=False,
        content_hash=content_hash)

    if source is not None:
        run = dataclasses.replace(source.run, file_id=file_id)
        record_run(conn, run)
        for unit in source.text_units:
            record_text_unit(conn, unit)
        for observation in source.observations:
            record_observation(conn, dataclasses.replace(observation, file_id=file_id))
        # The one gap in P4's published set: no fixture addresses its own text unit in
        # full, and `whole_document_requested` cannot be reached without one.
        for observation in EXTRA_OBSERVATIONS.get(fixture.number, ()):
            record_observation(conn, dataclasses.replace(observation, file_id=file_id))
        # P4's own run completeness, through P1's own writer. This is what separates
        # fixture 15 ("something looked and could not read it") from fixture 2
        # ("nothing has looked"), because D2 forbids the store from holding the class.
        set_extraction_status(
            conn, file_id, status_by_tier={run.analysis_tier: run.completeness},
            author=run.extractor_name, component_version=run.extractor_version)
        if fixture.sensitive_keys:
            # P5's per-value signal, written through P5's own writer. Without this the
            # set `sensitive_observation_keys` composes is EMPTY for every file, and
            # `always_local_item` is unreachable no matter what fixture 7 requests --
            # the failure that made the old zone-based fixture pass by releasing.
            keys = observation_keys_for_run(conn, run.run_id)
            record_sensitivity_signals(
                conn, run_id=run.run_id,
                signals=tuple(
                    SensitivitySignal(observation_index=keys.index(key),
                                      signal=POTENTIALLY_SENSITIVE,
                                      basis="the published fixture's P5 signal")
                    for key in fixture.sensitive_keys),
                observation_keys=keys, now=FIXTURE_CLOCK)

    # M9 calls `request.max_dossier_tokens` "the caller's echo of it", so the fixture's
    # echo is what the configured ceiling must be. The gate reads P1's stored value and
    # never the request's -- `over_dossier_ceiling` is explicit about it -- so without
    # this the ceiling is unset, an unset ceiling cannot deny, and fixture 6 releases.
    set_ceiling(conn, CEILING_KEY, fixture.request.max_dossier_tokens)

    set_policy(conn, fixture.policy, component_version=FIXTURE_COMPONENT_VERSION,
               user_id=FIXTURE_USER_ID, reason="the published fixture's policy")
    if fixture.revoked:
        # `policy.revoke_consent` appends NO event; `revocation.revoke` is what writes
        # the `consent_revoked` row that `policy_revoked_for` reads back. Seeding
        # through the former alone leaves the denial unreachable, which is the shape
        # of failure this whole file exists to catch.
        revoke(conn, current_policy(conn, plan_version=fixture.policy.plan_version),
               fixture.area, user_id=FIXTURE_USER_ID,
               component_version=FIXTURE_COMPONENT_VERSION, observed_at=FIXTURE_CLOCK,
               retraction_limit=FIXTURE_RETRACTION_LIMIT,
               files_in_scope=lambda _scope: (file_id,))
    if fixture.classification is not None:
        ClassificationStore(conn).write(
            dataclasses.replace(fixture.classification, file_id=file_id,
                                content_hash=content_hash))
    return file_id


def prepare(conn, fixture: GateFixture, tmp_path):
    """Seed, rebind the request to the minted file id, and build the real gate.

    The gate is built from `gate_arguments`, which fills all TWELVE keywords
    `Gate.__init__` takes. Two of them are optional in the signature and mandatory
    here: with `template_for` unset fixture 4 releases, and with `measure_tokens`
    unset fixture 6 releases -- in both cases because the branch is unreachable, not
    because the rule is wrong.
    """
    file_id = seed(conn, fixture, tmp_path)
    request = dataclasses.replace(
        fixture.request,
        target=Target(file_ids=(file_id,), group_id=fixture.request.target.group_id),
        requested_items=tuple(
            dataclasses.replace(item, file_id=file_id) if isinstance(item, Filename)
            else item for item in fixture.request.requested_items))
    bound = dataclasses.replace(fixture, request=request)
    gate = Gate(conn, **gate_arguments(bound, store=ClassificationStore(conn)))
    return gate, request, file_id


def replay(conn, fixture: GateFixture, tmp_path):
    gate, request, file_id = prepare(conn, fixture, tmp_path)
    return gate.release(request), file_id


def _audit_id_of(conn, decision) -> int:
    """The audit id the gate returned, whichever branch it returned it on."""
    if isinstance(decision, Released):
        return int(decision.audit_id)
    row = conn.execute(
        "SELECT event_id FROM events WHERE subsystem = 'P7' "
        "ORDER BY event_id DESC LIMIT 1").fetchone()
    return int(row["event_id"])


# --- SPEC §11's list, item for item -----------------------------------------

def test_the_coverage_map_names_every_spec_11_item_and_nothing_else():
    # The test that fails if a list member has no fixture, which is the only thing
    # standing between "eighteen fixtures" and "the ones the SPEC asked for".
    assert set(FIXTURE_COVERAGE) == set(DENIAL_REASONS) | set(SPEC_11_ITEMS)
    for item, numbers in FIXTURE_COVERAGE.items():
        assert numbers, item
        for number in numbers:
            assert by_number(number)


def test_the_five_plus_items_carry_the_specs_own_words():
    # A paraphrase here is a failing test and not an editorial choice: SPEC_11_ITEMS is
    # the checklist, and a checklist rewritten in the author's words no longer checks
    # the document it came from.
    assert SPEC_11_ITEMS == (
        "a clean `Released` with redaction applied",
        "a `NeedsConsent` returning all four options",
        "a protected file under each of the four modes",
        "an `unreadable_unclassified` file",
        "a `Protected Records` residual request",
    )


def test_there_is_one_fixture_per_denial_reason():
    for reason in DENIAL_REASONS:
        reached = [f for f in FIXTURES
                   if isinstance(f.decision, Denied) and f.decision.reason == reason]
        assert reached, reason


def test_the_denial_reasons_are_all_eight_and_no_ninth():
    reasons = {f.decision.reason for f in FIXTURES if isinstance(f.decision, Denied)}
    assert reasons == set(DENIAL_REASONS)
    assert len(DENIAL_REASONS) == 8


def test_fixture_numbers_are_dense_unique_and_eighteen():
    # Sixteen are SPEC §11's. Seventeen and eighteen are Open question 5's two
    # branches, which §11 does not ask for and which are the only place in the part
    # where both readings of OQ5 exist as data.
    numbers = [f.number for f in FIXTURES]
    assert numbers == list(range(1, 19))
    assert len(FIXTURES) == 18


def test_by_number_raises_on_a_number_nobody_published():
    assert by_number(1).number == 1
    with pytest.raises(UnknownFixture):
        by_number(99)


def test_the_gate_fixture_publishes_fourteen_named_fields():
    # Six are the plan skeleton's. Eight are added by this task and every one of them
    # is either a held-open question the fixture answers AS DATA (`area`,
    # `unclassified_permits_local`, `residual_template`) or a replay precondition
    # without which "each fixture carries the audit record the gate would have
    # appended" is unfalsifiable (`classification`, `p4_fixture`, `revoked`,
    # `sensitive_keys`). `downstream_obligation` carries SPEC §11's own sentences to P8.
    assert [f.name for f in dataclasses.fields(GateFixture)] == [
        "number", "spec_case", "policy", "classification", "area", "request",
        "decision", "audit_record", "p4_fixture", "downstream_obligation", "revoked",
        "sensitive_keys", "unclassified_permits_local", "residual_template"]


# --- the pin on `Gate.__init__`, which this task owns ------------------------

def test_gate_arguments_are_the_twelve_keywords_the_gate_actually_takes():
    # Task 11 said Task 20 pinned this and Task 20 said it reported a pin on Task 11,
    # so the signature had no owner and an equality test against a hard-coded pair
    # passed while ten keywords went unfilled. Asserted as an EQUALITY against the
    # live signature so the pin cannot drift from Task 11 in either direction.
    parameters = inspect.signature(Gate.__init__).parameters
    keywords = [name for name, p in parameters.items()
                if p.kind is inspect.Parameter.KEYWORD_ONLY]
    assert tuple(keywords) == GATE_ARGUMENTS
    assert len(GATE_ARGUMENTS) == 12
    assert list(parameters)[:2] == ["self", "conn"]


def test_the_ten_required_keywords_have_no_default_and_the_two_optional_ones_do():
    parameters = inspect.signature(Gate.__init__).parameters
    required = [name for name in GATE_ARGUMENTS
                if parameters[name].default is inspect.Parameter.empty]
    assert required == list(GATE_ARGUMENTS[:10])
    assert GATE_ARGUMENTS[10:] == ("measure_tokens", "template_for")
    for optional in GATE_ARGUMENTS[10:]:
        assert parameters[optional].default is None


def test_gate_arguments_fills_every_one_of_the_twelve_for_every_fixture():
    # The `None` defaults are the trap: `template_for=None` makes
    # `protected_records_template` unreachable on an excerpt and `measure_tokens=None`
    # makes `dossier_over_budget` unreachable, so two of the eighteen fixtures would
    # replay to the wrong branch with nothing raised anywhere.
    store = object()
    for fixture in FIXTURES:
        filled = gate_arguments(fixture, store=store)
        assert tuple(filled) == GATE_ARGUMENTS, fixture.number
        assert all(value is not None for value in filled.values()), fixture.number


def test_the_two_optional_keywords_are_supplied_where_a_denial_needs_them():
    # 4 and 16 reach `protected_records_template` through `template_for`; 6 reaches
    # `dossier_over_budget` only through `measure_tokens`.
    from privacy.denial import PROTECTED_RECORDS_TEMPLATE
    for number in (4, 16):
        fixture = by_number(number)
        assert fixture.residual_template == PROTECTED_RECORDS_TEMPLATE
        template_for = gate_arguments(fixture, store=object())["template_for"]
        assert template_for("any-file-id") == PROTECTED_RECORDS_TEMPLATE
        assert fixture.decision.reason == "protected_records_template"
    assert by_number(6).decision.reason == "dossier_over_budget"
    assert callable(gate_arguments(by_number(6), store=object())["measure_tokens"])


def test_without_template_for_the_content_half_releases(p7_conn, tmp_path):
    # The claim above, run rather than asserted: fixture 4's denial exists ONLY
    # because `template_for` was supplied. With the signature's `None` default the
    # branch at the top of the gate is unreachable and a protected-records excerpt
    # sails through as an ordinary protected-cloud question.
    fixture = by_number(4)
    file_id = seed(p7_conn, fixture, tmp_path)
    request = dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,)))
    keywords = gate_arguments(dataclasses.replace(fixture, request=request),
                              store=ClassificationStore(p7_conn))
    keywords["template_for"] = lambda _file_id: None
    decision = Gate(p7_conn, **keywords).release(request)
    # It does not merely deny for a weaker reason -- it RELEASES a protected file's
    # excerpt to a cloud model, because its area carries an explicit grant. That is
    # how much of §7.3 rides on the optional keyword being supplied.
    assert isinstance(decision, Released)


def test_without_measure_tokens_the_budget_denial_cannot_fire(p7_conn, tmp_path):
    # The same claim for fixture 6: an unmeasured dossier cannot exceed a ceiling.
    fixture = by_number(6)
    file_id = seed(p7_conn, fixture, tmp_path)
    request = dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,)))
    keywords = gate_arguments(dataclasses.replace(fixture, request=request),
                              store=ClassificationStore(p7_conn))
    keywords["measure_tokens"] = None
    decision = Gate(p7_conn, **keywords).release(request)
    assert isinstance(decision, Released)


def test_exactly_one_fixture_revokes_a_grant_before_the_call():
    # §8.4: the user may "revoke a policy for future runs". `policy_revoked` means a
    # grant EXISTED and was withdrawn; a fixture with no grant to begin with would be
    # testing "never permitted", which is a different denial.
    revoking = {f.number for f in FIXTURES if f.revoked}
    assert revoking == {3}
    fixture = by_number(3)
    assert fixture.decision.reason == "policy_revoked"
    assert fixture.area in dict(fixture.policy.consent_grants)


def test_the_corpus_area_is_carried_as_data_and_never_inferred():
    # Open question 3 stays open: P7 defines no area, so every fixture that needs one
    # states it and the gate takes a resolver with no default.
    scoped = {f.number: f.area for f in FIXTURES if f.area is not None}
    assert scoped
    assert all(isinstance(area, str) and area for area in scoped.values())
    for fixture in FIXTURES:
        for scope, _option in fixture.policy.consent_grants:
            assert isinstance(scope, str)


def test_no_fixture_invents_a_vocabulary_value():
    for fixture in FIXTURES:
        assert fixture.policy.operation_mode in OPERATION_MODES
        if fixture.classification is not None:
            assert fixture.classification.handling_class in HANDLING_CLASSES
        if isinstance(fixture.decision, Denied):
            assert fixture.decision.reason in DENIAL_REASONS
        if isinstance(fixture.decision, NeedsConsent):
            assert set(fixture.decision.options) == set(CONSENT_OPTIONS)


def test_every_fixture_policy_leaves_the_version_for_the_gate_to_mint():
    # `policy._persist` raises `CallerSuppliedPolicyVersion` on anything else, so a
    # fixture that stated a version could not be seeded at all. This is why
    # `policy_version` and `authorizing_policy` are substituted rather than compared.
    from privacy.policy import UNSET_POLICY_VERSION
    for fixture in FIXTURES:
        assert fixture.policy.policy_version == UNSET_POLICY_VERSION, fixture.number
        assert fixture.audit_record.policy_version == UNSET_POLICY_VERSION
        assert fixture.audit_record.authorizing_policy == UNSET_POLICY_VERSION


# --- the two pairs that look like duplicates and are not ---------------------

def test_the_store_refuses_to_hold_the_unreadable_class_as_a_file_fact(p7_conn):
    # D2, shipped: `unreadable_unclassified` "is a gate outcome, not a file fact".
    # This is why fixture 15 carries NO ClassificationRecord -- the plan's draft gave
    # it one with that class, which the store rejects. The distinction between "nothing
    # has looked" and "something looked and could not read it" therefore lives in the
    # EXTRACTION, which is the only place D2 leaves for it.
    with pytest.raises(GateOutcomeNotAFileFact):
        ClassificationStore(p7_conn).write(ClassificationRecord(
            file_id="f", content_hash="a" * 64,
            handling_class=UNREADABLE_UNCLASSIFIED, protected=False,
            basis="detector", evidence_refs=(p4(3).observations[0].observation_key,),
            reliability_state="direct", observed_at=FIXTURE_CLOCK))


def test_the_unclassified_fixture_has_no_extraction_and_the_unreadable_one_does():
    nothing_looked = by_number(2)
    looked_and_failed = by_number(15)
    assert nothing_looked.classification is None
    assert looked_and_failed.classification is None
    assert nothing_looked.p4_fixture is None
    assert looked_and_failed.p4_fixture == 18
    assert nothing_looked.decision.reason == looked_and_failed.decision.reason == (
        "unclassified")


def test_the_two_unclassified_fixtures_get_different_explanations_from_the_gate(
        p7_conn, tmp_path):
    # The distinction, run rather than described. §8.6 requires the product to show
    # "what has been deferred, and why", and "nobody looked" and "the extractor could
    # not read it" are two different whys with two different remedies.
    nothing_looked, _ = replay(p7_conn, by_number(2), tmp_path)
    looked_and_failed, _ = replay(p7_conn, by_number(15), tmp_path)
    assert nothing_looked.reason == looked_and_failed.reason == "unclassified"
    assert nothing_looked.explanation != looked_and_failed.explanation
    # The gate reads `files.extraction_status_by_tier`, which `record_file` starts at
    # `{}` and P4 fixture 18's run fills with its own `unreadable` completeness.
    assert '{"native": "unreadable"}' in looked_and_failed.explanation
    assert "'{}'" in nothing_looked.explanation
    assert '"unreadable"' not in nothing_looked.explanation


def test_the_unreadable_fixture_stands_on_p4s_own_unreadable_run():
    # §2.9's indexed-but-unreadable, which P4 fixture 18 carries as
    # `completeness = "unreadable"`. P7 invents no extraction outcome of its own.
    assert by_number(15).p4_fixture == 18
    assert p4(18).run.completeness == "unreadable"


def test_both_halves_of_7_3_are_covered_separately():
    # §7.3: Protected Records "must not cause filenames or content to be exposed in
    # model prompts". Two nouns, two fixtures.
    from privacy.items import Excerpt
    content_half = by_number(4)
    filename_half = by_number(16)
    assert all(isinstance(item, Excerpt)
               for item in content_half.request.requested_items)
    assert all(isinstance(item, Filename)
               for item in filename_half.request.requested_items)
    assert content_half.decision.reason == "protected_records_template"
    assert filename_half.decision.reason == "protected_records_template"


def test_the_protected_cloud_rule_does_not_depend_on_the_item_kind():
    # §8.4 names no item kind: "Protected material should not be included in
    # cloud-model prompts by default." Fixture 1 asks for an excerpt, fixture 13 for a
    # metadata field, and both are denied for the same reason under the same mode.
    from privacy.items import Excerpt, MetadataField
    assert by_number(1).policy.operation_mode == by_number(13).policy.operation_mode
    assert isinstance(by_number(1).request.requested_items[0], Excerpt)
    assert isinstance(by_number(13).request.requested_items[0], MetadataField)
    assert by_number(1).decision.reason == "protected_cloud_target"
    assert by_number(13).decision.reason == "protected_cloud_target"


# --- always-local, which is P5's signal and not a zone -----------------------

def test_the_always_local_fixture_stands_on_a_key_p5_signalled():
    # The only `AlwaysLocalRequested` the gate can raise on a CONSTRUCTIBLE item is
    # `item.observation_key in sensitive_keys`; the nine always-local NAMES are
    # unconstructible in Task 7's `__post_init__`, so a request holding one cannot be
    # a fixture. An earlier draft used an `Excerpt` "in the ocr zone", which
    # `check_item` never branches on -- so the fixture RESOLVED AND RELEASED, silently.
    from privacy.items import Excerpt
    fixture = by_number(7)
    assert fixture.decision.reason == "always_local_item"
    assert fixture.sensitive_keys, "with no signalled key the denial is unreachable"
    requested = {item.observation_key for item in fixture.request.requested_items
                 if isinstance(item, Excerpt)}
    assert set(fixture.sensitive_keys) <= requested
    assert all(key in {o.observation_key for o in p4(fixture.p4_fixture).observations}
               for key in fixture.sensitive_keys)


def test_no_fixture_relies_on_a_text_unit_zone_because_p4_publishes_none():
    # Why the zone reading was wrong, asserted rather than remembered: P4's text unit
    # for the OCR fixture carries no zone at all. The string `ocr` lives only in the
    # observation's locator, and `check_item` reads neither.
    unit = p4(8).text_units[0]
    assert getattr(unit, "zone", None) is None
    assert "ocr" in p4(8).observations[0].locator


def test_the_p5_signal_is_what_the_gate_reads(p7_conn, tmp_path):
    # The composition, end to end: P4's runs for the file -> P5's signals for the run
    # -> the keys the gate refuses. Seeded through P5's own writer, so a change to
    # either side fails here rather than turning a denial into a release.
    from privacy.items import sensitive_observation_keys
    fixture = by_number(7)
    file_id = seed(p7_conn, fixture, tmp_path)
    assert sensitive_observation_keys(p7_conn, file_id) == frozenset(
        fixture.sensitive_keys)


def test_without_the_p5_signal_the_always_local_fixture_releases(p7_conn, tmp_path):
    # The silent failure the fixture was rewritten to avoid, reproduced on purpose:
    # strip the signal and the same request resolves and is RELEASED. A fixture for
    # `always_local_item` that never reaches the denial proves the opposite of its name.
    fixture = dataclasses.replace(by_number(7), sensitive_keys=())
    decision, _ = replay(p7_conn, fixture, tmp_path)
    assert isinstance(decision, Released)


# --- the mode sweep ---------------------------------------------------------

def test_a_protected_file_appears_under_each_of_the_four_modes():
    assert set(MODE_SWEEP) == set(OPERATION_MODES)
    for mode, number in MODE_SWEEP.items():
        fixture = by_number(number)
        assert fixture.policy.operation_mode == mode
        assert fixture.classification is not None
        assert fixture.classification.protected is True


def test_mode_is_evaluated_before_protection_so_the_reason_is_the_general_one():
    # The precedence this task pins for Task 13. Under `offline` and `local_model` a
    # cloud target is unreachable for ANY file, so naming the passport as the cause
    # would be a false explanation -- and §8.6 requires the UI to show "what has been
    # deferred, and why". Under `hybrid` and `cloud_assisted` the target IS reachable
    # and the protection is the real cause.
    assert by_number(MODE_SWEEP["offline"]).decision.reason == "mode_forbids_target"
    assert by_number(MODE_SWEEP["local_model"]).decision.reason == "mode_forbids_target"
    assert by_number(MODE_SWEEP["hybrid"]).decision.reason == "protected_cloud_target"
    assert by_number(
        MODE_SWEEP["cloud_assisted"]).decision.reason == "protected_cloud_target"


def test_the_precedence_pin_matches_the_published_order():
    # The same rule read off Task 13's data rather than off the fixtures, so the two
    # cannot drift: `mode_forbids_target` precedes `protected_cloud_target`.
    from privacy.denial import DENIAL_ORDER
    assert DENIAL_ORDER.index("mode_forbids_target") < DENIAL_ORDER.index(
        "protected_cloud_target")


def test_the_mode_only_denial_uses_a_non_protected_file():
    # Fixture 8 isolates the mode axis: a `public_low`, unprotected file still cannot
    # reach a cloud target under `offline`. Without this, `mode_forbids_target` would
    # only ever be observed on protected files and the two rules would be untestable
    # apart.
    fixture = by_number(8)
    assert fixture.classification.handling_class == "public_low"
    assert fixture.classification.protected is False
    assert fixture.policy.operation_mode == "offline"
    assert fixture.decision.reason == "mode_forbids_target"


# --- the whole-document gap in P4's fixture set ------------------------------

def test_no_p4_fixture_addresses_its_own_text_unit_in_full():
    # Why `EXTRA_OBSERVATIONS` exists, asserted rather than remembered.
    # `resolve.materialise` refuses a request span that disagrees with the record, and
    # `is_whole_document` needs `span.end >= unit_length`, so a denial for
    # `whole_document_requested` needs an observation that covers its whole unit. P4
    # publishes none. The day P4 publishes one, this test fails and the extra
    # observation should be deleted in favour of it.
    for fixture in P4_FIXTURES:
        units = {tuple(unit.container_path): unit for unit in fixture.text_units}
        for observation in fixture.observations:
            span = observation.location.text_span
            unit = units.get(tuple(observation.location.container_path))
            if span is None or unit is None:
                continue
            assert not (span.start <= 0 and span.end >= unit.length), (
                fixture.number, observation.locator)


def test_the_extra_observation_is_p4s_own_material_and_there_is_one():
    # It borrows P4 fixture 11's run, content hash, extractor and text unit, and the
    # key is computed by P4's own `observation_key`. Nothing about the bytes is P7's.
    assert set(EXTRA_OBSERVATIONS) == {5}
    source = p4(WHOLE_UNIT_P4_FIXTURE)
    assert WHOLE_UNIT_OBSERVATION.run_id == source.run.run_id
    assert WHOLE_UNIT_OBSERVATION.content_hash == source.run.content_hash
    assert WHOLE_UNIT_OBSERVATION.extractor_name == source.run.extractor_name
    assert WHOLE_UNIT_OBSERVATION.raw_value == source.text_units[0].text
    assert WHOLE_UNIT_OBSERVATION.location.text_span.end == source.text_units[0].length
    assert WHOLE_UNIT_OBSERVATION.observation_key.startswith("sha256:")


# --- Open question 5, held open as two fixtures ------------------------------

def test_the_oq5_pair_differs_in_exactly_one_parameter():
    # "Does `unreadable_unclassified` permit a LOCAL model call?" is unanswered, and
    # `unclassified_denies` takes `local_calls_on_unclassified` with no default for
    # that reason. A pair whose halves differed in anything but the parameter would
    # not isolate the parameter, so everything else is asserted identical.
    one, two = by_number(17), by_number(18)
    assert one.unclassified_permits_local is False
    assert two.unclassified_permits_local is True
    assert one.policy == two.policy
    assert one.classification is None and two.classification is None
    assert one.request == two.request
    assert one.p4_fixture == two.p4_fixture
    assert one.request.model_target.locality == "local"


def test_the_oq5_pair_holds_both_readings_and_names_no_winner():
    assert isinstance(by_number(17).decision, Denied)
    assert by_number(17).decision.reason == "unclassified"
    assert isinstance(by_number(18).decision, Released)


def test_the_gate_parameter_behind_oq5_has_no_default():
    # The moment someone gives it one, P7 has answered a question the SPEC holds open,
    # and this pair stops meaning anything.
    parameters = inspect.signature(Gate.__init__).parameters
    assert parameters["unclassified_permits_local"].default is (
        inspect.Parameter.empty)
    from privacy.denial import unclassified_denies
    assert inspect.signature(
        unclassified_denies).parameters["local_calls_on_unclassified"].default is (
        inspect.Parameter.empty)


# --- the two non-denial branches --------------------------------------------

def test_the_released_fixture_applied_redaction_and_carries_a_manifest():
    # §11: "a clean `Released` with redaction applied".
    fixture = by_number(9)
    assert isinstance(fixture.decision, Released)
    assert fixture.audit_record.redaction_applied is True
    assert fixture.decision.redaction_manifest.entries
    assert all(entry.identifier_class
               for entry in fixture.decision.redaction_manifest.entries)
    assert fixture.decision.redaction_manifest.any_redacted is True


def test_no_released_fixture_echoes_the_local_text_back():
    # §8.4 puts "complete extracted text" in the always-local set, and the transform
    # is what stops a materialised value being the stored one. `apply_redaction`
    # raises `RedactionIneffective` when a transform returns its input, so a released
    # item carrying the local string could not have been produced at all.
    for number in (9, 18):
        released = by_number(number).decision
        for item in released.materialised_items:
            assert item.value != p4(3).observations[0].raw_value


def test_the_needs_consent_fixture_offers_all_four_options_in_the_specs_order():
    # §8.4: the user should "choose whether to allow a local model, a cloud model, a
    # redacted prompt, or no model use". Four, and a surface that offers three has
    # made the decision for them.
    fixture = by_number(10)
    assert isinstance(fixture.decision, NeedsConsent)
    assert fixture.decision.options == CONSENT_OPTIONS
    assert len(CONSENT_OPTIONS) == 4


def test_the_consent_branch_needs_a_protected_file_and_an_ungranted_scope():
    # The gate's branch is `text_items and protected_ids and scope not in granted`.
    # An earlier draft set `protected=False` AND carried a grant for the fixture's own
    # area, so BOTH conjuncts failed and the fixture released.
    fixture = by_number(10)
    assert fixture.classification.protected is True
    assert fixture.area is not None
    assert fixture.area not in dict(fixture.policy.consent_grants)


def test_the_consent_branch_is_unreachable_with_a_cloud_target():
    # Not a fixture detail -- a property of the two rules read together. Under
    # `cloud_assisted`, `protected_cloud_denies` returns False only when the scope IS
    # granted, and the consent branch requires that it is NOT. So a protected file
    # with a cloud target denies before it can ask, and the fixture that asks must use
    # a local target. §8.4 describes exactly that case, and the first of the four
    # options it offers is a LOCAL model.
    from privacy.denial import protected_cloud_denies
    fixture = by_number(10)
    assert fixture.request.model_target.locality == "local"
    assert protected_cloud_denies(
        protected=True, locality="local", operation_mode="cloud_assisted",
        scope=fixture.area, granted_scopes=()) is False
    assert protected_cloud_denies(
        protected=True, locality="cloud", operation_mode="cloud_assisted",
        scope=fixture.area, granted_scopes=()) is True


def test_the_needs_consent_fixture_has_no_reason_field_to_be_read_as_a_denial():
    # B2: `NeedsConsent` "is never an outcome the caller may absorb". P7's obligation
    # is to make the absorption unrepresentable, and the type-level form of that is
    # the absence of a `reason` field a caller could map onto a denial.
    names = {f.name for f in dataclasses.fields(by_number(10).decision)}
    assert "reason" not in names
    assert names == {"consent_request_id", "requirement", "options"}


# --- the P8 obligations, carried as data rather than as a comment ------------

def test_exactly_two_fixtures_carry_an_obligation_on_p8():
    carriers = {f.number for f in FIXTURES if f.downstream_obligation is not None}
    assert carriers == {6, 10}


def test_the_budget_fixture_says_a_p8_test_that_reaches_it_is_a_p8_failure():
    # SPEC §11, verbatim: a M9 backstop, not a gate result.
    obligation = by_number(6).downstream_obligation
    assert obligation == (
        "so P8 can prove its ladder ran first -- a P8 test that reaches this denial "
        "through the normal path is a P8 failure, not a gate result")
    assert by_number(6).decision.reason == "dossier_over_budget"


def test_the_consent_fixture_says_p8_must_return_the_branch_intact():
    assert by_number(10).downstream_obligation == (
        "so P8 can prove it returns the branch to its caller intact")


def test_done_means_11s_second_clause_is_p8s_test_run_and_not_assertable_here():
    # "and P8's harness passes its own tests against those fixtures with P7
    # unimplemented." P8 does not exist. This test exists so the limitation lives in
    # the suite rather than in a report nobody rereads.
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("llm_harness")
    assert all(f.decision is not None for f in FIXTURES), (
        "the P7 half -- published, replayable request/decision pairs -- is what this "
        "part can deliver; the P8 half is P8's test run")


# --- requests carry references, never content --------------------------------

def test_no_request_carries_materialised_content():
    # SPEC §6: requests "carry references, never materialised content". Asserted over
    # the item records rather than by eye, because a sixth item kind added later would
    # otherwise slip through.
    for fixture in FIXTURES:
        for item in fixture.request.requested_items:
            for field in dataclasses.fields(item):
                value = getattr(item, field.name)
                if isinstance(value, str):
                    assert "\n" not in value, (fixture.number, field.name)
                    assert len(value) < 200, (fixture.number, field.name)


def test_a_metadata_field_names_a_field_and_does_not_carry_its_value():
    from privacy.items import MetadataField
    names = {f.name for f in dataclasses.fields(MetadataField)}
    assert names == {"name"}


def test_excerpts_included_holds_key_and_span_pairs_and_not_the_text():
    # SPEC §7: "excerpts_included stores (observation_key, span) pairs plus the
    # redaction_manifest, not a second copy of the text".
    unit_text = p4(3).text_units[0].text
    seen = 0
    for fixture in FIXTURES:
        for key, span in fixture.audit_record.excerpts_included:
            seen += 1
            assert key.startswith("sha256:")
            assert "#" in span and "-" in span
            assert unit_text not in key and unit_text not in span
    assert seen, "no fixture carries an excerpt pair, so this test proved nothing"


# --- the fixtures stand on P4's fixtures, not on a private substrate ---------

def test_every_excerpt_addresses_an_observation_the_replay_writes():
    # The reason `p4_fixture` names a NUMBER and does not copy the observation:
    # `observation_key` is derived from (content_hash, extractor_name, locator,
    # raw_value), so a P4 fixture that moves moves P7's key with it. A copied key
    # would rot silently and the replay would address nothing.
    from privacy.items import Excerpt, RedactedIdentifier
    for fixture in FIXTURES:
        addressed = [item for item in fixture.request.requested_items
                     if isinstance(item, (Excerpt, RedactedIdentifier))]
        if not addressed:
            continue
        assert fixture.p4_fixture is not None, fixture.number
        published = {o.observation_key for o in p4(fixture.p4_fixture).observations}
        published |= {o.observation_key
                      for o in EXTRA_OBSERVATIONS.get(fixture.number, ())}
        for item in addressed:
            assert item.observation_key in published, (fixture.number, item)


# --- the replay: the fixture and the gate are one implementation -------------

@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_replaying_a_fixture_through_the_real_gate_reproduces_the_decision(
        p7_conn, tmp_path, number):
    fixture = by_number(number)
    decision, _ = replay(p7_conn, fixture, tmp_path)
    assert type(decision) is type(fixture.decision), fixture.spec_case
    if isinstance(fixture.decision, Denied):
        assert decision.reason == fixture.decision.reason, fixture.spec_case
        assert decision.explanation
        assert decision.remedy_options
    if isinstance(fixture.decision, NeedsConsent):
        assert decision.options == fixture.decision.options
        assert decision.requirement.handling_class == (
            fixture.decision.requirement.handling_class)
        assert decision.requirement.items == fixture.decision.requirement.items
    if isinstance(fixture.decision, Released):
        assert decision.model_target == fixture.decision.model_target
        assert decision.materialised_items == fixture.decision.materialised_items
        assert decision.redaction_manifest == fixture.decision.redaction_manifest


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_replaying_a_fixture_reproduces_its_audit_record_field_for_field(
        p7_conn, tmp_path, number):
    # SPEC §11: "Each fixture carries the audit record the gate would have appended."
    # `would have appended` is a claim about the implementation, so it is checked
    # against the implementation and not against a second hand-written copy of it.
    fixture = by_number(number)
    decision, _ = replay(p7_conn, fixture, tmp_path)
    appended = audit_record(p7_conn, _audit_id_of(p7_conn, decision))
    for field in AUDIT_FIELDS:
        if field in MINTED_FIELDS or field in SUBSTITUTED_FIELDS:
            continue
        assert getattr(appended, field) == getattr(fixture.audit_record, field), (
            fixture.number, field)


def test_the_excused_field_list_is_small_and_named():
    # An ignore-list is the standard way a golden-record test stops testing anything.
    # Five names, each with a reason, and the set is asserted rather than extended.
    # `release_id` came OUT of it under D14: it is not minted, it is `None`.
    assert SUBSTITUTED_FIELDS == {
        "file_id", "file_ids", "policy_version", "authorizing_policy"}
    assert MINTED_FIELDS == {"audit_id"}
    assert "release_id" not in MINTED_FIELDS | SUBSTITUTED_FIELDS
    assert len(SUBSTITUTED_FIELDS | MINTED_FIELDS) < len(AUDIT_FIELDS) / 2


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_the_substituted_fields_are_the_only_ones_a_replay_changes(
        p7_conn, tmp_path, number):
    # The excuse list, checked from the other side: every excused field really does
    # differ from the fixture's stated value, so none of them is being excused for
    # nothing. A field that stopped being minted would fail here and be compared again.
    fixture = by_number(number)
    decision, file_id = replay(p7_conn, fixture, tmp_path)
    appended = audit_record(p7_conn, _audit_id_of(p7_conn, decision))
    assert appended.file_id == file_id
    assert appended.file_ids == (file_id,)
    assert appended.policy_version.startswith("policy-")
    assert appended.policy_version != fixture.audit_record.policy_version
    assert appended.authorizing_policy == appended.policy_version
    assert appended.audit_id is not None


# --- D14: the audit record's `release_id` is None, and the join runs one way --

@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_the_audit_records_release_id_is_none_on_every_branch(
        p7_conn, tmp_path, number):
    # D14. §6 puts the audit append strictly BEFORE the release exists, `mint_release`
    # takes the `audit_id`, and `events` is append-only so the row cannot be
    # back-filled. `_release_record` therefore sets `release_id=None` unconditionally
    # -- including on a release. An earlier draft published a `release_id` on the
    # fixture's audit record and excused the field from comparison, which is how a
    # value the gate cannot produce survived review.
    decision, _ = replay(p7_conn, by_number(number), tmp_path)
    appended = audit_record(p7_conn, _audit_id_of(p7_conn, decision))
    assert appended.release_id is None
    assert by_number(number).audit_record.release_id is None


def test_the_released_decision_carries_a_release_id_the_record_does_not():
    # The decision's id is real; the record's is not. Both are true at once and the
    # two are joined ledger -> events, which is the direction Task 12 gave the ledger
    # an `audit_id` column for.
    for number in (9, 18):
        released = by_number(number)
        assert isinstance(released.decision, Released)
        assert released.decision.release_id
        assert released.audit_record.release_id is None
    assert MINTED_DECISION_FIELDS == {
        "release_id", "audit_id", "policy_version", "consent_request_id"}


def test_the_join_runs_ledger_to_events_and_not_the_other_way(p7_conn, tmp_path):
    # SPEC §7 lists `release_id` on the audit record and §6 makes it impossible to be
    # there. §7 is amended; §6's ordering guarantee -- "the audit is written before
    # anything is released" -- is the property the whole trail rests on and is
    # untouched. The reachable direction is asserted rather than described.
    decision, _ = replay(p7_conn, by_number(9), tmp_path)
    assert isinstance(decision, Released)
    row = p7_conn.execute(
        "SELECT audit_id FROM release_ledger WHERE release_id = ?",
        (decision.release_id,)).fetchone()
    assert row is not None and row["audit_id"] == decision.audit_id
    assert audit_record(p7_conn, row["audit_id"]).release_id is None


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_every_replay_leaves_exactly_one_audit_event(p7_conn, tmp_path, number):
    # §8.4: "Every model call should be recorded in a consent-aware audit record."
    # Every call, including the denied ones and the local ones -- §8.4 names no
    # exemption, and §8.2 covers "Every significant event affecting a file". Counted
    # around the gate call alone, so the seeding's own events cannot pad it.
    gate, request, _ = prepare(p7_conn, by_number(number), tmp_path)
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    gate.release(request)
    after = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after == before + 1
