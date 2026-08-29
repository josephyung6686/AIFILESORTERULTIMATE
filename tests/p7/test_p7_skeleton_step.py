# tests/p7/test_p7_skeleton_step.py
"""Done-means 13, and 11 §9's second fixture path.

02-segmentation-map.md's walking skeleton is "One file, one deterministic path, every
seam touched. No LLM, no cloud, no embeddings -- which also means no privacy gate is
exercised, because nothing leaves the machine."

Done-means 13 turns that into an obligation: the skeleton "must nonetheless assert:
the classification exists for the scanned file; the gate is installed on the only
egress path; `release` was called zero times; the audit log is empty; and a deliberate
attempted call under `offline` returns `Denied` with reason `mode_forbids_target`.
That is the seam test -- that the door exists and is shut."

Read the last two tests in this file before reading the rest of it. The detector is
unwritten (D2), so the classification path one asserts is written HERE, by the test,
standing in for a detector that does not exist. On a real corpus every file resolves
to `Denied(unclassified)`. This step proves the door, not the classification.

Four things the PLAN's draft of this file asserted are false against the SHIPPED code,
and each is corrected here rather than worked around silently:

1. `Gate.__init__` takes TWELVE keyword-only parameters, not two. The plan's
   `Gate(conn, component_version=..., scope_for=...)` cannot be constructed. §3.3 gave
   Task 20 the job of pinning that signature, and it pinned it as
   `privacy.fixtures.gate_arguments`, which is IMPORTED here rather than re-derived --
   a second private copy of the twelve is the defect class this project has paid for
   most.
2. `policy._persist` REFUSES a caller-supplied `policy_version`
   (`CallerSuppliedPolicyVersion`), so the plan's `offline_policy()` with
   `policy_version="policy-skeleton"` raises before it can be stored. The published
   fixtures' own offline policy is used instead -- it already carries W1's floor and
   every redaction facet at its more redacting value.
3. `transcription_authorized_for` is `(conn, scope, *, plan_version)` and returns a
   `TranscriptionAuthorization`, not `(scope)`.
4. `record_consent_choice` requires `policy=` and `scope=`; §8.4's grant cannot be
   written without the area it is scoped to (Open question 3).

And one that is a RULE rather than a signature: §3.9, "the `protected` flag decides,
never the class". `Gate.release`'s consent branch reads `record.protected`, so the
plan's `classify(..., handling_class="sensitive_personal", protected=False)` releases
instead of asking. Fixture 10 -- the published one -- carries `protected=True`, and
that is what this file uses.
"""
from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import pathlib
from typing import Callable

import pytest

from database_agent.files_table import get_file

from eval_harness.bundle import bundle_files
from eval_harness.store import create_eval_schema

from evidence_shape.fixtures import FIXTURES as P4_FIXTURES
from evidence_shape.store import (
    RunWriter, record_observation, record_run, record_text_unit,
)

from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.structured_text import TextDocument

from orchestrator import TARGETED_OCR_UNAVAILABLE, Wave2, run_wave2

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

from privacy.audit import audit_records_for
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.consent import NeedsConsent, pending_consent, record_consent_choice
from privacy.denial import mode_forbids
from privacy.fixtures import (
    CLOUD_MODEL, FIXTURE_CLOCK, GateFixture, SKELETON_FIXTURE, by_number,
    gate_arguments,
)
from privacy.gate import Gate
from privacy.learning_seam import assign
from privacy.policy import current_policy, set_policy, transcription_authorized_for
from privacy.release import Denied, Released, Target
from privacy.transport_guard import (
    assert_single_call_site, assert_single_egress)
from privacy.vocabulary import CONSENT_OPTIONS, USER, USER_CONFIRMED

COMPONENT = "0.1.0"
NEVER: Callable[[], bool] = lambda: False
SKELETON_CLOCK = "2026-08-22T10:00:00+00:00"
SRC_ROOT = pathlib.Path(importlib.import_module("privacy").__file__).parent.parent

#: The fixture whose policy is §8.4's fully offline mode. Imported rather than
#: re-authored: `by_number(8).policy` IS W1's floor with every redaction facet at its
#: more redacting value, and `_policy` leaves `policy_version` unset because the gate
#: owns the version (§6) and `_persist` refuses a caller who supplies one.
OFFLINE_FIXTURE = 8

#: The published `Released` fixture, whose request is the one used to show that a file
#: with NO classification denies. Its policy grants a cloud model for its own area, so
#: the only thing left to deny it is the missing class.
UNCLASSIFIED_PROBE_FIXTURE = 9


@pytest.fixture()
def skeleton_db(p7_conn):
    """P1 + P3 + P4 + P5 + P7 from `p7_conn`, plus the two schemas Wave 2 also needs.

    `tests/wave2/`'s own harness records why every part's tables are created rather
    than most of them: "§0's 'each part owns its own tables' cuts both ways, and a
    harness that creates four parts' tables out of five is testing a database the
    product never runs on." `p7_conn` already runs four of the five creators; the scan
    and extraction schemas are re-run harmlessly and the eval schema is the one this
    file adds, because P2's bundle is where Wave 2 ends.
    """
    create_scan_schema(p7_conn)
    create_extraction_schema(p7_conn)
    create_eval_schema(p7_conn)
    return p7_conn


@pytest.fixture()
def corpus(tmp_path: pathlib.Path) -> pathlib.Path:
    """02-segmentation-map.md's input: "one PDF whose title carries a course code"."""
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "syllabus.pdf").write_bytes(b"%PDF-1.4 BUSIB 4300")
    return root


def mime_for(path: pathlib.Path) -> str | None:
    return {".pdf": "application/pdf"}.get(path.suffix)


def skeleton_readers() -> Readers:
    """Deterministic readers. No LLM, no network, no OCR provider."""
    page = "BUSIB 4300 Course Information"
    return Readers(
        read_pdf=lambda p: PdfDocument(
            metadata={"Title": "BUSIB 4300 Syllabus"}, iso_dates={},
            pages=(PdfPage(number=1, text=page,
                           regions=(Region(zone="heading", start=0, end=29,
                                           ordinal=1, label="Course Information"),)),)),
        read_docx=lambda p: DocxDocument(core_properties={}),
        read_text_document=lambda p: TextDocument(text=page),
        read_long_tail=lambda p, transcribe=False: LongTailFile(),
        read_manifest=lambda p: ArchiveManifest(archive_type="zip"),
        read_image=lambda p: ImageRecord(image_format="PNG", dimensions="2880x1800",
                                         width=2880, height=1800),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None)


def walk(conn, corpus_root, *, authorized=None) -> Wave2:
    """One deterministic pass. Note what is NOT passed: there is no gate parameter."""
    selection = record_selection(conn, sources=[corpus_root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_wave2(
        conn, selection, source=FilesystemCorpusSource(), mime_type_for=mime_for,
        scan_state="scanned", budget_exhausted=NEVER,
        detect_format=lambda p: p.suffix.lstrip(".") or None,
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=skeleton_readers(), sink=RunWriter(conn, author="P5"),
        now=lambda: SKELETON_CLOCK, context_window=40,
        no_usable_facts=TARGETED_OCR_UNAVAILABLE,
        transcription_authorized=authorized or NEVER,
        corpus_form="snapshot", policy_settings={},
        file_entry_body=lambda row: {"payload_ref": f"blobs/{row['content_hash']}"})


def only_file(conn) -> str:
    rows = conn.execute("SELECT file_id FROM files").fetchall()
    assert len(rows) == 1
    return rows[0]["file_id"]


def classify(conn, file_id, handling_class="personal_non_sensitive", *,
             protected=False) -> ClassificationRecord:
    """THE DETECTOR THAT DOES NOT EXIST, written by the test and saying so.

    D2 put the rule set behind an injection and no task in any plan produces one.
    SPEC *Deferred*: "The design states *what* is protected and never *how it is
    recognised*. The detector rule set, its signals, and its thresholds are
    hand-authored. P7 publishes the vocabulary the detectors write into."

    Until one is supplied, this is what a classification's arrival looks like: a
    caller writing through P7's writer. Nothing here is a detection rule; it is the
    act of recording a decision some other component made. `protected` is a PARAMETER
    and is never derived from `handling_class` -- §3.9, and C5 is open.
    """
    record = ClassificationRecord(
        file_id=file_id, content_hash=get_file(conn, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis=USER,
        evidence_refs=(), reliability_state=USER_CONFIRMED,
        observed_at=SKELETON_CLOCK)
    written = assign(conn, record, store=ClassificationStore(conn),
                     component_version=COMPONENT)
    assert written is not None, "§8.7 suppressed the stand-in write"
    return record


def bind(fixture: GateFixture, file_id: str) -> GateFixture:
    """The published fixture, retargeted at the file the SKELETON actually scanned.

    Only `target` moves. Everything else -- policy, items, template, area -- is the
    published fixture's, because a fixture edited to fit a test is no longer the
    fixture SPEC §11 published.
    """
    return dataclasses.replace(
        fixture,
        request=dataclasses.replace(
            fixture.request,
            target=Target(file_ids=(file_id,),
                          group_id=fixture.request.target.group_id)))


def install(conn, fixture: GateFixture, file_id: str):
    """Store the fixture's policy and build the real gate over the scanned file.

    `gate_arguments` is Task 20's pin of `Gate.__init__`'s twelve keywords (§3.3), and
    it is imported rather than reproduced. A private copy here would be a seventh home
    for a rule another module owns.
    """
    bound = bind(fixture, file_id)
    # Fixture 10's request names P4 fixture 3's durable observation key. Consent now
    # records the exact canonical locator from the live Location, so the walking
    # skeleton must persist that referenced metadata just as the fixture replay does.
    if fixture.p4_fixture is not None:
        source = next(item for item in P4_FIXTURES
                      if item.number == fixture.p4_fixture)
        requested_keys = {
            item.observation_key for item in bound.request.requested_items
            if hasattr(item, "observation_key")
        }
        missing = requested_keys and not conn.execute(
            "SELECT 1 FROM evidence WHERE observation_key IN ({}) LIMIT 1".format(
                ",".join("?" for _ in requested_keys)), tuple(requested_keys),
        ).fetchone()
        if missing:
            record_run(conn, dataclasses.replace(source.run, file_id=file_id))
            for unit in source.text_units:
                record_text_unit(conn, unit)
            for observation in source.observations:
                record_observation(
                    conn, dataclasses.replace(observation, file_id=file_id),
                )
    set_policy(conn, bound.policy, component_version=COMPONENT, user_id="joseph",
               reason="the published fixture's policy, under the walking skeleton")
    gate = Gate(conn, **gate_arguments(bound, store=ClassificationStore(conn)))
    return gate, bound.request


def p7_events(conn) -> int:
    return conn.execute(
        "SELECT count(*) c FROM events WHERE subsystem = 'P7'").fetchone()["c"]


def src_modules():
    """Every module under `src/`, by dotted name, with its file.

    Three modules in `src/readers/` bind optional third-party OCR and PDF backends
    (`Quartz`, `pdfminer`) that this environment does not install, so importing the
    tree blindly -- as the plan's draft did -- raises `ModuleNotFoundError` and the
    guard never runs. They are yielded with `module = None` and the caller falls back
    to the file, which is how a transport hiding behind an uninstalled dependency is
    still caught.
    """
    for path in sorted(SRC_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts or ".egg-info" in str(path):
            continue
        dotted = str(path.relative_to(SRC_ROOT).with_suffix("")).replace("/", ".")
        dotted = dotted[:-9] if dotted.endswith(".__init__") else dotted
        try:
            yield dotted, path, importlib.import_module(dotted)
        except ModuleNotFoundError:
            yield dotted, path, None


def _declares_transport(path: pathlib.Path) -> bool:
    """`IS_MODEL_TRANSPORT = True` at module level, read as syntax and not as text.

    An AST read rather than a substring scan: the flag appears in a comment and in a
    docstring in `privacy/transport_guard.py`, and a text search would find both.
    """
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in tree.body:
        targets = (node.targets if isinstance(node, ast.Assign)
                   else [node.target] if isinstance(node, ast.AnnAssign) else [])
        for target in targets:
            if isinstance(target, ast.Name) and target.id == "IS_MODEL_TRANSPORT":
                value = node.value
                if isinstance(value, ast.Constant) and value.value is True:
                    return True
    return False


# ===========================================================================
# Path one -- the deterministic skeleton. The door exists and is shut.
# ===========================================================================

def test_the_wave_2_caller_has_nowhere_to_put_a_gate():
    # "`release` was called zero times" as a STRUCTURAL fact rather than a counted one:
    # seventeen parameters and not one of them is a gate, a classification, a detector
    # or a P7 policy. A caller that cannot hold a gate cannot have called one.
    #
    # SEVENTEEN, read live. The preamble's §4 says seventeen and Task 22's own prose
    # says eighteen; the preamble wins and the substrate agrees with it.
    parameters = inspect.signature(run_wave2).parameters
    assert len(parameters) == 17
    for forbidden in ("gate", "release", "classifier", "detector", "handling_class",
                      "privacy_policy", "classification"):
        assert forbidden not in parameters, forbidden


def test_the_policy_parameter_is_p5s_safety_policy_and_not_p7s():
    # Two different words one parameter apart. `SafetyPolicy` has two fields and
    # deliberately no third; P7's `Policy` has seven. Conflating them is how a future
    # author "wires the gate in" and silently disables the container rule instead.
    from privacy.policy import Policy
    assert {f.name for f in dataclasses.fields(SafetyPolicy)} == {
        "is_protected_container", "is_dataless"}
    assert "operation_mode" in {f.name for f in dataclasses.fields(Policy)}
    assert "operation_mode" not in {f.name for f in dataclasses.fields(SafetyPolicy)}
    # NOT `signature(...).annotation is not Policy`, which was true in every possible
    # world: `run_wave2`'s `policy` parameter carries no annotation at all, and
    # `src/orchestrator.py` has `from __future__ import annotations`, so even an
    # explicit `policy: Policy` would arrive as the STRING 'Policy' and never as the
    # class. The guard could not have failed. Read the source instead.
    import ast
    import pathlib
    orchestrator = pathlib.Path(inspect.getfile(run_wave2))
    tree = ast.parse(orchestrator.read_text())

    # 1. the orchestrator must not import P7's Policy at all
    imported = {
        f"{node.module}.{alias.name}"
        for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module
        for alias in node.names
    }
    assert "privacy.policy.Policy" not in imported, imported

    # 2. and if `policy` ever gains an annotation, it must not name P7's Policy
    function = next(node for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef) and node.name == "run_wave2")
    annotations = {
        argument.arg: (ast.unparse(argument.annotation)
                       if argument.annotation is not None else None)
        for argument in function.args.args + function.args.kwonlyargs
    }
    assert "policy" in annotations, annotations
    assert annotations["policy"] in (None, "SafetyPolicy"), annotations["policy"]


def test_the_deterministic_path_runs_end_to_end(skeleton_db, corpus):
    result = walk(skeleton_db, corpus)
    assert isinstance(result, Wave2)
    assert skeleton_db.execute(
        "SELECT count(*) c FROM extraction_runs").fetchone()["c"] > 0


def test_the_audit_log_is_empty_after_the_deterministic_path(skeleton_db, corpus):
    # Done-means 13's fourth clause. Not "P7 wrote few events" -- none, because
    # nothing asked the gate anything.
    walk(skeleton_db, corpus)
    assert p7_events(skeleton_db) == 0
    assert audit_records_for(skeleton_db, file_id=only_file(skeleton_db)) == []


def test_the_classification_exists_for_the_scanned_file(skeleton_db, corpus):
    # Done-means 13's first clause. Written by `classify`, which stands in for the
    # detector and says so; see its docstring.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    record = classify(skeleton_db, file_id)
    store = ClassificationStore(skeleton_db)
    assert store.current(file_id, record.content_hash) == record
    assert get_file(skeleton_db, file_id)["sensitivity_state"] is not None


def test_the_gate_is_installed_on_the_only_egress_path(skeleton_db, corpus):
    """Done-means 13's second clause, now that there is a transport to assert it of.

    This test used to assert `transports == []` -- "there is no transport, so the
    property holds over an empty set" -- and then loop over that empty list calling
    `assert_single_egress`. P8 shipped `llm_harness/transport.py` and the assertion
    stayed true anyway, because the module never set `IS_MODEL_TRANSPORT`: the scan
    kept returning `[]`, the emptiness assertion kept passing, and the loop under it
    -- the only line that ever runs the guard on real code -- iterated nothing. The
    day P8 landed, this test went from vacuous-by-design to vacuous-by-accident, and
    nothing said so.

    Both halves are now positive assertions. The scan must find EXACTLY the one
    transport, and the guard must reach a verdict on it. `tests/p7/
    test_p7_real_transport_egress.py` holds the detail; this holds the count, because
    a SECOND module declaring itself the transport is the failure this file is
    positioned to see and that one is not.
    """
    walk(skeleton_db, corpus)
    declared = [path for _dotted, path, _module in src_modules()
                if _declares_transport(path)]
    assert [path.name for path in declared] == ["transport.py"], declared
    transports = [dotted for dotted, _path, module in src_modules()
                  if module is not None
                  and getattr(module, "IS_MODEL_TRANSPORT", False)]
    assert transports == ["llm_harness.transport"], transports
    for dotted in transports:
        module = importlib.import_module(dotted)
        assert assert_single_egress(module) is None
        assert assert_single_call_site(module) is None


def test_release_was_called_zero_times(skeleton_db, corpus):
    # Done-means 13's third clause, counted as well as proven structurally. A gate is
    # constructed, handed to nobody, and asked nothing -- which is exactly the
    # skeleton's shape: the door is installed and never opened.
    calls: list[object] = []

    class RecordingGate(Gate):
        def release(self, request):
            calls.append(request)
            return super().release(request)

    RecordingGate(skeleton_db, **gate_arguments(
        by_number(OFFLINE_FIXTURE), store=ClassificationStore(skeleton_db)))
    walk(skeleton_db, corpus)
    assert calls == []


def test_a_deliberate_call_under_offline_is_denied_mode_forbids_target(
        skeleton_db, corpus):
    # Done-means 13's fifth clause, and the whole point: the door is SHUT, not absent.
    # §8.4's fully offline mode: "No content leaves the device; only local rules and
    # local models may run."
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    gate, request = install(skeleton_db, by_number(OFFLINE_FIXTURE), file_id)
    decision = gate.release(request)
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"
    assert decision.explanation
    assert decision.remedy_options


def test_the_deliberate_call_is_audited_even_though_it_was_denied(
        skeleton_db, corpus):
    # §8.4: "Every model call should be recorded in a consent-aware audit record", and
    # §8.2 covers "Every significant event affecting a file". The empty log above is
    # empty because nothing asked, not because denials go unrecorded.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    gate, request = install(skeleton_db, by_number(OFFLINE_FIXTURE), file_id)
    before = p7_events(skeleton_db)
    gate.release(request)
    assert p7_events(skeleton_db) > before
    records = audit_records_for(skeleton_db, file_id=file_id)
    assert [r.outcome for r in records] == ["denied"]


def test_the_transcription_back_edge_is_p7s_and_is_not_the_gate(skeleton_db, corpus):
    # M10's back-edge: P5's call site is `transcription_authorized()`, a zero-argument
    # predicate at `src/extractors/long_tail.py`. P7 fills it. This is an
    # authorization consulted before a LOCAL extractor runs -- no content leaves, and
    # it is NOT §8.4's door. A reader who saw P7 in the Wave-2 call could otherwise
    # conclude the skeleton exercises the gate.
    offline = by_number(OFFLINE_FIXTURE)
    set_policy(skeleton_db, offline.policy, component_version=COMPONENT,
               user_id="joseph", reason="the user switched the corpus to offline mode")
    authorized = transcription_authorized_for(
        skeleton_db, "Academics", plan_version=offline.policy.plan_version)
    assert inspect.signature(authorized).parameters == {}
    assert authorized() is False
    walk(skeleton_db, corpus, authorized=authorized)
    assert p7_events(skeleton_db) == 1        # the `policy_set` above, and nothing more


def test_the_transcription_predicate_is_not_a_release_and_writes_no_audit(
        skeleton_db, corpus):
    # The other half of the sentence above, asserted rather than asserted-about: a
    # granted transcription authorization still produces no audit record, because
    # nothing left the machine. `local_model` is one of §8.4's four options and is not
    # `no_model_use`, which is the whole of §2.9's reading Task 5 reported.
    offline = by_number(OFFLINE_FIXTURE)
    granted = dataclasses.replace(
        offline.policy, consent_grants=(("Academics", "local_model"),))
    set_policy(skeleton_db, granted, component_version=COMPONENT, user_id="joseph",
               reason="the user authorized a local model for Academics")
    authorized = transcription_authorized_for(
        skeleton_db, "Academics", plan_version=granted.plan_version)
    assert authorized() is True
    walk(skeleton_db, corpus, authorized=authorized)
    assert audit_records_for(skeleton_db, file_id=only_file(skeleton_db)) == []


# ===========================================================================
# The bundle -- where this task INVERTS the plan skeleton
# ===========================================================================

def test_the_bundle_handling_class_is_still_none_after_a_classification(
        skeleton_db, corpus):
    # The plan skeleton expects this to be non-null "closing the loop
    # src/orchestrator.py:259 left open". It is NOT, and both reasons are quotable.
    #
    # 1. P7 Open question 8 is open: "Whether a bundle intended to leave the user's
    #    machine may carry audit records -- which name excerpts -- is unstated."
    #    A P7 that wrote into `bundle_file_entry` would answer it in code.
    # 2. The value is the Wave-2 caller's and the caller's own comment says why it is
    #    None: "The honest value is None because the class is unknown, not because
    #    another column happened to be empty."
    result = walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    entries = bundle_files(skeleton_db, result.bundle_id)
    assert entries
    for entry in entries:
        assert entry["handling_class"] is None


def test_a_second_pass_after_classification_still_carries_none(skeleton_db, corpus):
    # The classification is written BEFORE this pass, so "the bundle was built too
    # early" is not the explanation. The caller passes a literal `None` and P7 has no
    # seam into it -- which is the honest posture while no detector exists.
    walk(skeleton_db, corpus)
    classify(skeleton_db, only_file(skeleton_db))
    second = walk(skeleton_db, corpus)
    entries = bundle_files(skeleton_db, second.bundle_id)
    assert entries
    for entry in entries:
        assert entry["handling_class"] is None


def test_src_privacy_writes_into_no_bundle_table(skeleton_db, corpus):
    # OQ8 held structurally, not by restraint: P7 imports no P2 writer at all.
    privacy_dir = SRC_ROOT / "privacy"
    for path in sorted(privacy_dir.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("eval_harness"), path.name
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("eval_harness"), path.name


# ===========================================================================
# Path two -- 11 §9's second fixture path, the B2 contract test
# ===========================================================================

def test_the_skeleton_fixture_is_named_as_data():
    # So P8 and P13 can find 11 §9's second path without reading this plan.
    assert SKELETON_FIXTURE == 10
    assert isinstance(by_number(SKELETON_FIXTURE).decision, NeedsConsent)
    assert by_number(SKELETON_FIXTURE).decision.options == CONSENT_OPTIONS


def test_a_dossier_requiring_sensitive_text_returns_needs_consent(
        skeleton_db, corpus):
    # 11 §9, clauses one and two: "a dossier that requires sensitive text /
    # Gate.release returns NeedsConsent". §8.4: "If a model needs text containing
    # sensitive content, the user should see that requirement and choose."
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id,
             handling_class=fixture.classification.handling_class,
             protected=fixture.classification.protected)
    gate, request = install(skeleton_db, fixture, file_id)
    decision = gate.release(request)
    assert isinstance(decision, NeedsConsent)
    assert decision.options == CONSENT_OPTIONS
    assert decision.consent_request_id
    assert decision.requirement.file_ids == (file_id,)


def test_the_protected_flag_and_not_the_class_opens_the_consent_branch(
        skeleton_db, corpus):
    # §3.9, and the plan draft's one substantive error: it asked for this branch with
    # `protected=False`. The class is identical here and the flag is not, and the flag
    # is what decides.
    #
    # What the unprotected run does instead is itself the proof: it walks PAST the
    # consent question and releases the fixture's now-persisted P4 reference. An
    # author who "simplified" the branch to read `handling_class` would get a
    # `NeedsConsent` here and fail.
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id,
             handling_class=fixture.classification.handling_class, protected=False)
    gate, request = install(skeleton_db, fixture, file_id)
    assert isinstance(gate.release(request), Released)
    assert [r.outcome for r in audit_records_for(
        skeleton_db, file_id=file_id
    )] == ["released"]


def test_path_one_can_never_produce_this_branch(skeleton_db, corpus):
    # Why 11 §9 exists: "It is the minimum that makes the one privacy-failure seam
    # exercisable without waiting for full depth." Path one's deliberate call is
    # fixture 8's -- a CLOUD target under `offline` -- and the mode denies it before
    # the consent question can be reached, so the first path cannot exercise B2.
    #
    # THE PLAN'S REASON FOR THIS IS WRONG AND THE SHIPPED CODE SAYS SO. Task 22's
    # draft ran fixture 10's request unchanged under `offline` and expected
    # `mode_forbids_target`. `denial.mode_forbids` returns True only for a CLOUD
    # locality -- "A LOCAL model is permitted under both" -- and fixture 10's target is
    # LOCAL by construction, so that call returns `NeedsConsent` and the draft's
    # assertion is false. `offline` is not a blanket "nothing gets far enough"; it is
    # a refusal of the target's locality. So the locality is varied here and the mode
    # is held fixed, which is the claim that actually holds.
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id,
             handling_class=fixture.classification.handling_class,
             protected=fixture.classification.protected)
    to_the_cloud = dataclasses.replace(
        fixture, policy=by_number(OFFLINE_FIXTURE).policy,
        request=dataclasses.replace(fixture.request, model_target=CLOUD_MODEL))
    gate, request = install(skeleton_db, to_the_cloud, file_id)
    decision = gate.release(request)
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"


def test_offline_refuses_the_target_and_not_the_call(skeleton_db, corpus):
    # The correction above, stated as its own assertion so it cannot be read as an
    # accident of the test above. §8.4's fully offline mode is "No content leaves the
    # device; only local rules and local models may run" -- a LOCAL target under
    # `offline` is permitted, and a P7 that denied it would be denying a local model
    # the design offers as one of §8.4's four consent options.
    assert mode_forbids("offline", "cloud") is True
    assert mode_forbids("offline", "local") is False
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id,
             handling_class=fixture.classification.handling_class,
             protected=fixture.classification.protected)
    offline = dataclasses.replace(fixture, policy=by_number(OFFLINE_FIXTURE).policy)
    gate, request = install(skeleton_db, offline, file_id)
    assert isinstance(gate.release(request), NeedsConsent)


def test_no_model_release_exists_until_a_choice_is_recorded(skeleton_db, corpus):
    # Done-means 7's own falsifiable form, and it needs the id Task 14 added.
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id,
             handling_class=fixture.classification.handling_class,
             protected=fixture.classification.protected)
    gate, request = install(skeleton_db, fixture, file_id)
    decision = gate.release(request)
    records = audit_records_for(skeleton_db,
                                consent_request_id=decision.consent_request_id)
    assert [r.outcome for r in records] == ["consent_requested"]
    assert pending_consent(skeleton_db, decision.consent_request_id) is not None


def test_choosing_no_model_use_records_the_choice_and_releases_nothing(
        skeleton_db, corpus):
    # 11 §9's third clause is P13's gesture; P7's half is that the recorded choice
    # closes the request and produces no `model_release`. P13's SPEC: "P13 records the
    # collection, not the grant."
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id,
             handling_class=fixture.classification.handling_class,
             protected=fixture.classification.protected)
    gate, request = install(skeleton_db, fixture, file_id)
    decision = gate.release(request)
    record_consent_choice(
        skeleton_db, decision.consent_request_id, "no_model_use",
        policy=current_policy(skeleton_db,
                              plan_version=fixture.policy.plan_version),
        scope=fixture.area, user_id="joseph", component_version=COMPONENT,
        observed_at=FIXTURE_CLOCK)
    outcomes = [r.outcome for r in audit_records_for(
        skeleton_db, consent_request_id=decision.consent_request_id)]
    assert "released" not in outcomes
    assert pending_consent(skeleton_db, decision.consent_request_id) is None
    assert current_policy(
        skeleton_db, plan_version=fixture.policy.plan_version).consent_grants == ()


def test_no_model_use_is_one_of_the_four_and_is_not_a_denial_reason():
    # The typed half of "does not become abstain": `no_model_use` is a CONSENT OPTION.
    # It is not in `DENIAL_REASONS`, so a caller cannot map the branch onto a denial by
    # respelling, and `NeedsConsent` carries no `reason` field to hold one.
    from privacy.vocabulary import DENIAL_REASONS
    assert "no_model_use" in CONSENT_OPTIONS
    assert "no_model_use" not in DENIAL_REASONS
    fields = {f.name for f in dataclasses.fields(NeedsConsent)}
    assert fields == {"consent_request_id", "requirement", "options"}


def test_clause_four_is_p8s_and_clause_three_is_p13s():
    # 11 §9: "choosing no_model_use does not become abstain inside P8." INSIDE P8 --
    # so the assertion belongs to P8's suite, as its Done-means 13, and to P13's as its
    # Done-means 16. P7's obligation is to make the absorption UNREPRESENTABLE, which
    # the test above does at the type level; policing it is not P7's and cannot be.
    #
    # P8 may be present, but P7 does not execute its harness. Review surface remains
    # a later dependency and is still intentionally absent.
    for absent in ("review_surface",):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(absent)
    assert by_number(SKELETON_FIXTURE).downstream_obligation == (
        "so P8 can prove it returns the branch to its caller intact")


# ===========================================================================
# The honesty clause -- read this one first
# ===========================================================================

def test_with_no_detector_every_real_file_resolves_to_denied_unclassified(
        skeleton_db, corpus):
    # The claim the plan skeleton makes in prose, asserted: "Until it is supplied, a
    # P7 running against a real corpus classifies nothing and every real file resolves
    # to `Denied(unclassified)` -- a correct, locked door with nobody holding a key."
    #
    # Nothing is classified here because nothing in the product classifies. Path one's
    # `classify()` is the test standing in for a detector; remove it and this is what
    # the walking skeleton actually produces.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    assert get_file(skeleton_db, file_id)["sensitivity_state"] is None
    assert ClassificationStore(skeleton_db).history(file_id) == []
    gate, request = install(
        skeleton_db, by_number(UNCLASSIFIED_PROBE_FIXTURE), file_id)
    decision = gate.release(request)
    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"
    assert not isinstance(decision, Released)


def test_this_step_proves_the_door_and_not_the_classification():
    # Said once, in a test, so it survives the plan being archived. "P7 is done" and
    # "the product classifies files" are different claims and only the first is
    # deliverable from these twenty-two tasks.
    detector_producers = []
    for name in ("privacy.classification", "privacy.classification_store",
                 "privacy.learning_seam", "privacy.gate"):
        module = importlib.import_module(name)
        detector_producers += [
            attribute for attribute in vars(module)
            if attribute.lower().startswith("detect")
            or attribute.upper().startswith("RULE")]
    assert detector_producers == []
