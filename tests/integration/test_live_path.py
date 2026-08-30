# tests/integration/test_live_path.py
"""One run of the real product, from a directory on disk to a P9 membership.

Nothing here is a double for a seam. Every authority supplied is one a deployment
is *required* to supply -- P7 ships no detector, P5 ships no format readers and no
§2.2 pattern catalogue, P6's direct slots have no default, P9's limits and
knowledge have none -- and every seam between them is live: the real `scan`, the
real extractors driven by the real pdfminer adapter over a real PDF, the real
`FactResolver`, the real `Gate`, the real `run_call`, the real transport, the real
site dispatcher, the real `p8_seam`, the real `group_subject`, the real
`replay_bundle`.

This exists because 3,621 tests pass and the product has never run end to end.
Every seam below is currently proved against a hand-built substitute, and a test
that constructs the record a seam was supposed to produce cannot fail when the
producer is wrong.

Two injected callables are NOT authorities, and both are named where they are used:

* `ModelClient.invoke` -- a network call is not a test, so it returns recorded
  bytes shaped to the dossier it was actually handed. `transport.ModelClient` takes
  `invoke` as a constructor argument; that is the documented deployment seam.
* `_WiredRunCall` -- it *calls* the real `run_call` and returns its real result
  unchanged, keeping a reference to the request and the verdict so a test can read
  them. It substitutes nothing. The five keyword arguments it binds are the ones
  `src/grouping/pipeline.py:341` does not supply, which is defect 3, and
  `test_p9_calls_run_call_with_its_real_signature` is the test that says so.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from database_agent.identity import hash_file
from eval_harness.assertions import assert_run, assertions
from eval_harness.bundle import bundle_files, expectations
from eval_harness.replay import StageResult, replay_bundle
from eval_harness.run import VERSION_TUPLE_FIELDS
from eval_harness.stage_output import stage_outputs
from extractors.stage_output import extraction_stage_output
from evidence_shape.location import TextSpan
from evidence_shape.store import observations_for_file
from extractors.reading import StructuredString
from extractors.safety import SafetyPolicy
from facts.direct import DirectSlot, DirectSlots, direct_facts
from facts.discount import MetadataScreen
from facts.file_facts import facts_for_file
from facts.resolver import FactResolver
from facts.usable import record_pass
from grouping.config import GroupingLimits
from grouping.embeddings import EmbeddingsOff
from grouping.pipeline import (
    GroupingKnowledge,
    ModelCallAuthorities,
    group_subject,
)
from grouping.retrieval import EmbeddingIdentity, RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.store import memberships_for_group
from llm_harness.budgets import ScanBudget, create_budget_schema
from llm_harness.harness import CallDependencies, run_call
from llm_harness.records import P8Verdict, PromptDefinition
from llm_harness.schema import create_llm_schema
from llm_harness.sites import SiteDependencies
from llm_harness.stage_output import emit_stage_output
from llm_harness.transport import ModelClient
from llm_harness.vocabulary import ACCEPT_DIRECT, B_GROUP, REJECT
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.gate import Gate
from privacy.items import Excerpt
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import ModelCallRequest, ModelTarget, Released, Target
from privacy.transport_guard import assert_single_egress
from production import P1P7Authorities, bootstrap_p1_p7, run_production_p1_p7
from readers.deployment import macos_readers
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.selection import record_selection

_HERE = Path(__file__).resolve()


def _load_pdf_builder():
    """`tests/readers/pdf_bytes.py` is a rootless module: pytest only puts its
    directory on `sys.path` when it collects something from `tests/readers/`, which
    is after this file. Load it by path so the corpus builder is the real one."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "live_path_pdf_bytes", _HERE.parents[1] / "readers" / "pdf_bytes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_pdf


build_pdf = _load_pdf_builder()

CLOCK = "2026-08-27T12:00:00+00:00"
PLAN_VERSION = "plan-live-1"
COMPONENT = "0.1.0"
#: The course code `build_pdf` writes into every title and into the body sentence.
#: The walking skeleton's specified input is "one PDF whose title carries a course
#: code" (`planning/02-segmentation-map.md`).
COURSE = "BUSIB 4300"
#: The body sentence `build_pdf` writes. The released span is COURSE inside it, so
#: every other character of this string is text the gate must not release.
BODY = "This syllabus covers the spring term for BUSIB 4300."
BUNDLE_MARKER = "BUNDLE-INTERIOR-MUST-NOT-BE-READ"

CLOUD = ModelTarget(locality="cloud", model_id="big-model", provider="a-provider")
EMBEDDING = EmbeddingIdentity(
    scope="corpus", model_id="big-model", model_version="1")

#: The ten §1.2 fields in P3 SPEC R2's order, under P1's column names.
SECTION_1_2_FIELDS = (
    "current_path", "filename", "normalized_filename", "extension", "mime_type",
    "observed_size", "observed_timestamps", "directory_position", "content_hash",
    "scan_state",
)


# --- the corpus ------------------------------------------------------------------

def _corpus(tmp_path: Path) -> Path:
    """Two real PDFs on one subject, and one protected container."""
    root = tmp_path / "corpus"
    root.mkdir()
    build_pdf(root / "Syllabus.pdf", title=f"{COURSE} Syllabus", pages=1)
    build_pdf(root / "Lecture 08.pdf", title=f"{COURSE} Lecture 08", pages=1)
    (root / "Numbers.app" / "Contents").mkdir(parents=True)
    (root / "Numbers.app" / "Contents" / "sheet.numbers").write_text(BUNDLE_MARKER)
    return root


# --- the authorities a deployment must supply ------------------------------------

def _find_structured_strings(text: str) -> tuple[StructuredString, ...]:
    """§2.2's patterns. P5 ships none -- they sit in its SPEC's Deferred table."""
    return tuple(
        StructuredString(kind="identifier", start=match.start(), end=match.end())
        for match in re.finditer(re.escape(COURSE), text))


#: P6's §3.5 slot set. `DirectSlots` has no default, so the slot is the caller's.
#: The slot named is the §2.2 identifier reading inside the page-one heading
#: region, whose observation carries a real `text_span` starting at 0. The
#: `/Title` metadata slot -- §3.5's own "a document title" example -- carries
#: `text_span = None`, and `test_p9_asks_p7_for_the_span_the_observation_carries`
#: is the test that says why no group anchored on it can ever be released.
_HEADING_LOCATOR = "heading:page=1/heading=1#0-10"
_TITLE_LOCATOR = "title:field=Title"
_SLOTS = DirectSlots(slots=(
    DirectSlot(
        slot_id="pdf.heading.identifier", field_key="subject",
        names=lambda locator: locator == _HEADING_LOCATOR,
        canonical=lambda raw: " ".join(raw.split()[:2])),
))


#: §2.2/§2.3's suppression catalogue. Injected with no default, like the slots.
_SCREEN = MetadataScreen(tool_producer_strings=(), metadata_property_names=())


def _direct_stage(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
    return direct_facts(
        conn, file_id=file_id, content_hash=content_hash, slots=_SLOTS,
        screen=_SCREEN)


def _resolver(*, tiers: frozenset[str], cache_key: str) -> FactResolver:
    return FactResolver(
        stages={"direct": _direct_stage, "rule": None, "llm": None},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda file_id: False,
        record_pass=lambda conn, file_id, content_hash: record_pass(
            conn, file_id=file_id, content_hash=content_hash,
            analysis_tiers=tiers),
        cache_key_for=lambda file_id, content_hash: f"{cache_key}:{content_hash}",
        screen_metadata=lambda conn, file_id, content_hash: ())


def _classify(conn, file_id: str, content_hash: str) -> ClassificationRecord | None:
    """P7's candidate producer. The detector does not exist, so it is the caller's
    and `P1P7Authorities` refuses to run without one."""
    row = conn.execute(
        "SELECT observation_key FROM evidence WHERE file_id = ? "
        "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()
    if row is None:
        return None
    return ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="personal_non_sensitive", protected=False, basis="detector",
        evidence_refs=(row["observation_key"],), reliability_state="direct",
        observed_at=CLOCK)


def _authorities(bundle_expectations=()) -> P1P7Authorities:
    return P1P7Authorities(
        bundle_expectations=bundle_expectations,
        native_resolver=_resolver(
            tiers=frozenset(("filesystem", "native")), cache_key="native-v1"),
        ocr_resolver=_resolver(
            tiers=frozenset(("filesystem", "native", "ocr")), cache_key="ocr-v1"),
        # The subject fact is usable, so targeted OCR is never needed and Apple
        # Vision is never reached. `usable_threshold` has no default either.
        usable_threshold=lambda facts, unresolved: True,
        classify=_classify,
        source=FilesystemCorpusSource(),
        mime_type_for=lambda path: (
            "application/pdf" if Path(path).suffix == ".pdf" else None),
        scan_state="scanned",
        scan_budget_exhausted=lambda: False,
        detect_format=lambda path: (
            "pdf" if Path(path).suffix == ".pdf" else None),
        # The line no live test has ever run: the REAL protected-container
        # predicate, through the real pipeline. `test_production_p1_p7.py` passes
        # `lambda path: False` here.
        policy=SafetyPolicy(
            is_protected_container=is_protected_container,
            is_dataless=lambda path: False),
        readers=macos_readers(find_structured_strings=_find_structured_strings),
        now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        p7_component_version=COMPONENT)


# --- P7's own injected authorities ------------------------------------------------

def _identifier_class(value, *, context_before=None, context_after=None):
    """A course code is an identifier. P7 ships no detector; this is the caller's."""
    return "course-code" if COURSE in value else None


def _redact(value: str, *, identifier_class: str) -> str:
    return "[redacted]"


def _policy(conn) -> Policy:
    import dataclasses

    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(), redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION, set_at=CLOCK)
    version = set_policy(
        conn, draft, component_version=COMPONENT, user_id="joseph",
        reason="live path")
    return dataclasses.replace(draft, policy_version=version)


def _gate(conn, *, file_ids: tuple[str, ...]) -> Gate:
    return Gate(
        conn, store=ClassificationStore(conn), plan_version=PLAN_VERSION,
        classifier=_identifier_class, transform=_redact,
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: file_ids,
        component_version=COMPONENT, now=lambda: CLOCK, user_id="joseph")


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="template.grouping", template_bytes=b"TEMPLATE\n",
        response_schema_bytes=b'{"type":"object"}', call_site=B_GROUP,
        call_site_version="1", shaping_policy_bytes=b'{"policy":"authored"}')


class Recorder:
    """A `ModelClient.invoke` that answers the dossier it was actually handed.

    `transport.issue` calls it with the exact model-visible bytes and the reply is
    built by reading those bytes, so the citations are the release's own. `claims`
    decides how many claims come back, which is what makes P8's claim-selection
    rule observable at all.
    """

    def __init__(self, *, claims: str = "one_good") -> None:
        self.calls: list[bytes] = []
        self.claims = claims

    @staticmethod
    def dossier_of(model_visible: bytes) -> dict:
        """`records.assemble` is `template_bytes + canonical_dossier_bytes`."""
        return json.loads(model_visible.split(b"\n", 1)[1])

    def __call__(self, model_visible_bytes: bytes) -> bytes:
        self.calls.append(model_visible_bytes)
        body = self.dossier_of(model_visible_bytes)
        members = [item["evidence_ref"] for item in body["evidence_items"]
                   if item["kind"] == "member"]
        released = body["released_evidence"][0]
        good = {
            "claim_ref": "coherence",
            "payload": {"coherent": True, "members": members},
            "citations": [{
                "evidence_ref": released["observation_key"],
                "cited_span": released["value"],
                "why_it_supports": "states the group's basis",
            }],
        }
        bad = {
            "claim_ref": "invented",
            "payload": {"coherent": True,
                        "members": ["a-file-nobody-retrieved"]},
            "citations": [{
                "evidence_ref": released["observation_key"],
                "cited_span": "a span the release does not contain",
                "why_it_supports": "invented",
            }],
        }
        claims = {"one_good": [good], "bad_then_good": [bad, good]}[self.claims]
        return json.dumps({"claims": claims},
                          separators=(",", ":")).encode("utf-8")


# --- the run ----------------------------------------------------------------------

@dataclass
class LiveRun:
    conn: object
    corpus: Path
    run: object
    policy: Policy
    file_ids: tuple[str, ...]
    anchor_file_id: str
    anchor_content_hash: str


@pytest.fixture()
def live(conn, tmp_path) -> LiveRun:
    """P1 -> P3 -> P4/P5 -> P6 -> P7, live, over a real corpus on disk."""
    bootstrap_p1_p7(conn)
    create_grouping_schema(conn)
    create_llm_schema(conn)
    create_budget_schema(conn)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)

    corpus = _corpus(tmp_path)
    selection_id = record_selection(
        conn, sources=[corpus], candidate_roots=[], cross_folder_moves=False,
        selected_by=None)
    # §8.5's reference corpus is hand work (P2 SPEC, Deferred: "the corpus
    # selection, the labelling, and the per-subject expected values are hand
    # work"). The label is authored HERE, before the bundle exists, because a
    # bundle is immutable once created (P2 SPEC §3, "Replay bundle") and carries
    # `bundle_expectation[]` among its contents. The subject is the content hash --
    # §8.5's five shared-evidence dimensions are keyed to it -- computed with P1's
    # own published `hash_file` rather than a second spelling of R1.
    anchor_hash = hash_file(corpus / "Syllabus.pdf", materialized=True)
    run = run_production_p1_p7(conn, selection_id, authorities=_authorities(
        bundle_expectations=({"dimension": "extraction",
                              "subject_ref": anchor_hash,
                              "expected_value": {"observation_count": 1,
                                                 "coverage": {"units": "pages",
                                                              "processed": 1,
                                                              "total": 1}},
                              "expected_outcome_kind": "produced",
                              "source": "hand-labelled"},)))

    rows = conn.execute(
        "SELECT file_id, current_path, content_hash FROM files "
        "ORDER BY current_path").fetchall()
    anchor = [row for row in rows
              if row["current_path"].endswith("Syllabus.pdf")][0]
    return LiveRun(
        conn=conn, corpus=corpus, run=run, policy=_policy(conn),
        file_ids=tuple(row["file_id"] for row in rows),
        anchor_file_id=anchor["file_id"],
        anchor_content_hash=anchor["content_hash"])


def _knowledge(live: LiveRun, *, embedding_identity) -> GroupingKnowledge:
    store = ClassificationStore(live.conn)
    return GroupingKnowledge(
        retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={}, similarity=None,
            similarity_threshold=None, embedding_identity=embedding_identity,
            domain=None),
        active_schema_for=lambda conn, file_id, content_hash: ("subject",),
        signal_evaluator_for=lambda domain: True,
        classification_store=store.current,
        # A non-empty conflict set fires SR4 in `graph.evaluate_stop_rules`, which
        # returns before the dossier exists, so a real conflict can never reach the
        # request. See the report: this is why D1.6 is not a test here.
        conflicts_for=lambda files: (),
        duplicate_or_version=None)


def _limits() -> GroupingLimits:
    return GroupingLimits(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)


def _text_for(live: LiveRun, observation_key: str) -> str | None:
    row = live.conn.execute(
        "SELECT raw_value FROM evidence WHERE observation_key = ? "
        "AND superseded_by IS NULL", (observation_key,)).fetchone()
    return None if row is None else row["raw_value"]


def _call_dependencies(live: LiveRun) -> CallDependencies:
    return CallDependencies(
        proposal_class="grouping.coherence",
        basis_key=json.dumps({"field_key": "subject", "value": COURSE}),
        learning_scope="group", learning_subject_id=live.anchor_file_id,
        evidence_resolver=lambda observation_key: _text_for(live, observation_key),
        # Site B needs no site bundle: `sites.dispatch` routes B_group straight to
        # `validate_group_response`, which takes none.
        site_dependencies=SiteDependencies(
            fact=None, placement=None, residual=None, template=None),
        contradicts=lambda *args, **kwargs: False,
        unreduced_fits=True, summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        scan_budget=ScanBudget(
            scan_id=live.run.scan_run_id, corpus_file_count=1000,
            max_calls_per_1000_files=5, max_estimated_cost=Decimal("10"),
            min_calls_per_scan=0),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        allowed_vocabulary=("coherent",),
        policy_version=live.policy.policy_version)


#: P9's request USED to need repairing before P7 would accept it. Both fields are
#: fixed, so nothing is repaired any more and every test below sends the request
#: P9 actually builds.
#:
#: `prompt_fingerprint`: P9 passed `dossier.dossier_fingerprint` where the
#: fingerprint of the `PromptDefinition` the transport sends belongs.
#: `grouping.p8_seam.prompt_fingerprint_for` now derives it from the prompt.
#: `model_target`: P9 passed `knowledge.retrieval.embedding_identity`, the local
#: vector model, where P7's `ModelTarget` belongs. It now comes from
#: `ModelCallAuthorities`.
#:
#: The shim is DELETED rather than left as a no-op: a repair that rewrites a field
#: with the value already there masks any regression in the code that produces it.


def _model_authorities(live: LiveRun, recorder: Recorder) -> ModelCallAuthorities:
    """`run_call`'s five arguments, as a deployment hands them to P9.

    Every one is the real object -- P7's own `Gate` over the live connection, a
    real `ModelClient` over the byte recorder, the authored `PromptDefinition`,
    P8's own `CallDependencies`, and a frozen clock. Nothing here is a stub. A
    stand-in would put this file back among the tests that hid the defect it
    exists to catch: a `gate=None` bundle, for instance, makes `run_call` return
    `ValidationUnavailable(missing=("gate",))` before it reaches the seam, and
    every assertion downstream then passes for the wrong reason.

    These five used to be built inside `_WiredRunCall`, because `pipeline.py`
    called `p8_run_call(conn, request)` and omitted them. P9 now carries a
    `ModelCallAuthorities` and forwards them under `run_call`'s own keyword names,
    so the test hands them to P9 and P9 does the forwarding -- which is the
    production path, rather than a way around it.
    """
    return ModelCallAuthorities(
        gate=_gate(live.conn, file_ids=live.file_ids),
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=_prompt(),
        validation_dependencies=_call_dependencies(live),
        observed_at=lambda: CLOCK,
        # The SAME target the client is pointed at. P7 gates the request against
        # this and P8 sends to that; two values here would let the gate decide
        # about one destination while the bytes went to another.
        model_target=CLOUD)


class _WiredRunCall:
    """The real `run_call`, over the request P9 actually built.

    It substitutes nothing and repairs nothing. It forwards the five keyword
    arguments P9 supplies, passes P9's request through untouched, calls `run_call`,
    and returns its result unchanged. It keeps the request and the result so a test
    can read what P9 handed P8 and what P8 handed back.

    It used to do two more things, and both are gone because the defects they stood
    in for are fixed: it built `run_call`'s five arguments itself (P9 now carries
    them in `ModelCallAuthorities`), and it rewrote `model_target` and
    `prompt_fingerprint` on the way past (P9 now produces both correctly).
    """

    def __init__(self, recorder: Recorder) -> None:
        self.recorder = recorder
        self.request = None
        self.result = None

    def __call__(self, conn, request, **authorities):
        self.request = request
        # `**authorities` is P9's bundle, arriving under `run_call`'s own keyword
        # names. Forwarded verbatim: this wrapper no longer knows what is in it.
        self.result = run_call(conn, request, **authorities)
        return self.result


def _group(live: LiveRun, p8_run_call, *, recorder: Recorder):
    """One `group_subject` over the live corpus, with P9's own honest knowledge
    and the real authorities a deployment hands it."""
    return group_subject(
        live.conn, file_id=live.anchor_file_id,
        content_hash=live.anchor_content_hash, plan_version_id=PLAN_VERSION,
        limits=_limits(),
        knowledge=_knowledge(live, embedding_identity=EMBEDDING),
        user_seed_for=lambda file_id, content_hash: None,
        p8_run_call=p8_run_call,
        p8_authorities=_model_authorities(live, recorder),
        embeddings=EmbeddingsOff(), created_at=CLOCK)


def _every_text_value(conn) -> list[str]:
    """Every TEXT cell in every table. Defect 1's harm is a row in the append-only
    `events` log, and a test that reads only `files` would miss it."""
    found: list[str] = []
    tables = [row["name"] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' "
        "AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        for row in conn.execute(f'SELECT * FROM "{table}"'):
            found.extend(v for v in tuple(row) if isinstance(v, str))
    return found


# --- seam 1: P3 -> P1 --------------------------------------------------------------

def test_p3_writes_the_ten_section_1_2_fields_and_authors_its_own_events(live):
    """P1 stores; P3 authors (§8.2, M8). A `discovery` event whose `subsystem` is
    P1 would make §8.2's reconstruction requirement unmeetable."""
    rows = live.conn.execute(
        "SELECT * FROM files ORDER BY current_path").fetchall()
    assert len(rows) == 2, [row["current_path"] for row in rows]
    for row in rows:
        for field in SECTION_1_2_FIELDS:
            assert row[field] not in (None, ""), (field, row["current_path"])

    authored = live.conn.execute(
        "SELECT DISTINCT event_type, subsystem FROM events "
        "WHERE event_type IN ('discovery', 'stat observation', 'hashing') "
        "ORDER BY event_type").fetchall()
    assert [row["event_type"] for row in authored] == [
        "discovery", "hashing", "stat observation"]
    assert {row["subsystem"] for row in authored} == {"P3"}


def test_nothing_inside_a_protected_container_reaches_the_database(live):
    """§4b: the container is recorded, its interior is not -- not its paths and not
    a byte of its content."""
    bundle = str(live.corpus / "Numbers.app")
    interior = str(live.corpus / "Numbers.app" / "Contents")

    verdicts = live.conn.execute(
        "SELECT * FROM exclusion_verdicts WHERE rule = 'protected container'"
    ).fetchall()
    assert [row["path"] for row in verdicts] == [bundle]
    assert verdicts[0]["label"] == "untouched_protected"

    values = _every_text_value(live.conn)
    assert not [v for v in values if interior in v], "an interior path was recorded"
    assert not [v for v in values if BUNDLE_MARKER in v], "interior CONTENT recorded"


def test_the_session_watch_reads_nothing_inside_a_protected_container(live):
    """The scan and the watch are two readers of one corpus, and only the scan has
    ever been tested against §4b (`src/scan_agent/watch.py` names neither
    protection nor exclusion)."""
    from scan_agent.watch import SessionWatch

    interior = live.corpus / "Numbers.app" / "Contents" / "sheet.numbers"
    watch = SessionWatch(live.conn)
    try:
        watch.open([live.corpus])
        interior.write_text(BUNDLE_MARKER + " changed")
        watch.poll()
        watch.notify(interior)
    finally:
        watch.close()

    rows = live.conn.execute(
        "SELECT old_path, new_path FROM events "
        "WHERE event_type = 'external modification detection'").fetchall()
    offenders = [dict(row) for row in rows
                 if "Numbers.app" in ((row["old_path"] or "")
                                      + (row["new_path"] or ""))]
    assert offenders == [], offenders


# --- seam 2: P4/P5 -> P6 -----------------------------------------------------------

def test_a_real_observation_becomes_a_fact_carrying_its_evidence_link(live):
    """One PDF, read by the real adapter, emitted in P4's frozen shape, resolved by
    the real `FactResolver` to a fact that cites the observation it rests on."""
    facts = [row for row in facts_for_file(
        live.conn, live.anchor_file_id, live.anchor_content_hash)
        if row["field_key"] == "subject"]
    assert len(facts) == 1, [dict(row) for row in facts]
    fact = facts[0]
    assert fact["reliability_state"] == "direct"
    assert fact["origin"] == "deterministic_extractor"

    refs = json.loads(fact["evidence_refs"])
    assert refs, "a fact with no evidence link is not a fact P6 may publish"
    keys = {one.observation_key
            for one in observations_for_file(live.conn, live.anchor_file_id)}
    assert set(refs) <= keys, (refs, sorted(keys))

    value = live.conn.execute(
        'SELECT canonical_value FROM "values" WHERE value_id = ?',
        (fact["value_id"],)).fetchone()
    assert value["canonical_value"] == COURSE


# --- seam 3: P6 -> P7 --------------------------------------------------------------

def _body_observation(live: LiveRun):
    """The one observation whose span sits inside a larger text unit."""
    rows = live.conn.execute(
        "SELECT observation_key, location FROM evidence "
        "WHERE file_id = ? AND raw_value = ? AND superseded_by IS NULL",
        (live.anchor_file_id, COURSE)).fetchall()
    body = [one for one in rows
            if json.loads(one["location"])["zone"] == "body"]
    assert body, "the real PDF produced no body-zone observation to release"
    location = json.loads(body[0]["location"])
    return body[0]["observation_key"], TextSpan(
        start=location["text_span"]["start"], end=location["text_span"]["end"])


def _release_one(live: LiveRun, key: str, span: TextSpan | None) -> object:
    request = ModelCallRequest(
        stage="grouping", target=Target(file_ids=(live.anchor_file_id,)),
        model_target=CLOUD,
        requested_items=(Excerpt(
            observation_key=key, span=span, reason="states the group's basis"),),
        prompt_template_id="template.grouping",
        prompt_fingerprint="sha256:fp-live", max_dossier_tokens=4000)
    return _gate(live.conn, file_ids=live.file_ids).release(request)


def test_the_gate_releases_no_text_outside_the_requested_span(live):
    """§8.4 puts "complete extracted text" in the always-local set and P7's SPEC:248
    has a release carry post-redaction values only. The observation this excerpt
    comes from carries 40 characters of raw context on either side of the span."""
    key, span = _body_observation(live)
    decision = _release_one(live, key, span)
    assert isinstance(decision, Released), decision
    item = decision.materialised_items[0]
    assert item.value == "[redacted]", item.value

    leaked = [name for name in ("context_before", "context_after",
                                "context_truncated")
              if hasattr(item, name)]
    assert leaked == [], (
        f"a released item carries {leaked}; §8.4 puts the raw text on either side "
        "of the span in the always-local set")

    body = json.dumps(
        {name: getattr(item, name) for name in
         ("observation_key", "span", "value", "zone", "unit_length")})
    for fragment in (BODY[:BODY.index(COURSE)],
                     BODY[BODY.index(COURSE) + len(COURSE):]):
        if fragment.strip():
            assert fragment.strip() not in body, fragment


def test_p9_asks_p7_for_the_span_the_observation_carries(live):
    """`p8_seam.build_dossier_request` built `TextSpan(0, len(excerpt.text))` for
    every requested item instead of reading the observation's own span.
    `privacy.resolve.materialise` refuses a span that disagrees with the record
    (`src/privacy/gate.py:460`), so any anchor whose observation does not carry
    exactly `(0, len)` -- every metadata observation, whose `text_span` is `None`,
    and every body excerpt, whose span does not start at 0 -- could never be
    released. §3.5's own first example, a document title, is one of them.

    The body used to build `TextSpan(0, len(raw_value))` here too and assert that
    P7 accepted it -- reproducing the defect in the test instead of exercising P9,
    while asserting on the line above that the very same observation carries no
    span. It now reads what P9 ACTUALLY asks for, which is what the name says.
    """
    row = live.conn.execute(
        "SELECT observation_key, raw_value, location FROM evidence "
        "WHERE file_id = ? AND superseded_by IS NULL",
        (live.anchor_file_id,)).fetchall()
    title = [one for one in row
             if json.loads(one["location"])["locator"] == _TITLE_LOCATOR]
    assert title, "the real PDF produced no title observation"
    assert json.loads(title[0]["location"])["text_span"] is None

    # What P9 asks for, per observation, over the live corpus.
    recorder = Recorder()
    wired = _WiredRunCall(recorder)
    _group(live, wired, recorder=recorder)
    live_span = {
        one["observation_key"]: json.loads(one["location"])["text_span"]
        for one in row
    }
    asked = wired.request.model_call_request.requested_items
    assert asked, "P9's request carried no items"
    for item in asked:
        recorded = live_span[item.observation_key]
        # P4 serialises the span as an object, not a pair.
        expected = (None if recorded is None
                    else TextSpan(recorded["start"], recorded["end"]))
        assert item.span == expected, (item.observation_key, item.span, expected)

    # And the unbounded reference P9 now sends is one P7 accepts.
    decision = _release_one(live, title[0]["observation_key"], None)
    assert isinstance(decision, Released), decision


def test_the_model_is_shown_the_released_span_and_no_other_text_of_its_unit(live):
    """The canonical model-visible bytes are the only artefact that answers "what
    did the model see". Nothing from the body sentence but the released value may
    appear in them."""
    recorder = Recorder()
    wired = _WiredRunCall(recorder)
    _group(live, wired, recorder=recorder)
    assert recorder.calls, wired.result

    seen = recorder.calls[0]
    for fragment in (BODY[:BODY.index(COURSE)],
                     BODY[BODY.index(COURSE) + len(COURSE):]):
        if fragment.strip():
            assert fragment.strip().encode("utf-8") not in seen, (
                f"the model was shown context outside the release: "
                f"{fragment.strip()!r}")


# --- seam 4: P7 -> P8 --------------------------------------------------------------

def test_run_call_returns_a_real_verdict_over_a_real_release(live):
    """`run_call` is the only public evaluation callable. Everything between the
    request and the verdict -- gate, dossier, transport, dispatcher -- is P8's."""
    recorder = Recorder()
    wired = _WiredRunCall(recorder)
    result = _group(live, wired, recorder=recorder)

    assert result.not_implemented_reason is None, result.not_implemented_reason
    assert isinstance(wired.result, P8Verdict), wired.result
    assert wired.result.outcome == ACCEPT_DIRECT, wired.result.reasons
    assert len(recorder.calls) == 1
    assert live.conn.execute(
        "SELECT count(*) AS c FROM release_ledger").fetchone()["c"] == 1


def test_the_real_transport_satisfies_the_single_egress_guard():
    """`privacy.transport_guard.assert_single_egress` over the real transport
    module. The guard has only ever run against modules with no live client."""
    import llm_harness.transport as transport

    assert assert_single_egress(transport) is None


# --- seam 5: P8 -> P9 --------------------------------------------------------------

def test_the_verdict_becomes_a_membership_through_p8_seam(live):
    """P9 maps P8's verdict. Nothing here constructs a `Membership`."""
    recorder = Recorder()
    result = _group(live, _WiredRunCall(recorder), recorder=recorder)
    assert result.model_result is not None, result.not_implemented_reason
    assert result.model_result.membership_ids, result.model_result
    stored = memberships_for_group(live.conn, result.group.group_id)
    assert {item.membership_id for item in stored} >= set(
        result.model_result.membership_ids)


def test_p9_calls_run_call_with_its_real_signature(live):
    """`src/grouping/pipeline.py:341` calls `p8_run_call(conn, request)`. The live
    `run_call` requires five more keyword-only arguments -- `gate`, `model_client`,
    `prompt`, `validation_dependencies`, `observed_at` -- so the first real call
    raises `TypeError` before any verdict can exist."""
    result = _group(live, run_call, recorder=Recorder())
    assert result.model_result is not None, result.not_implemented_reason


def test_p9_hands_p7_a_model_target(live):
    """`pipeline.py` passed `knowledge.retrieval.embedding_identity` as
    `build_dossier_request(model_target=...)`, which becomes
    `ModelCallRequest.model_target`. `EmbeddingIdentity` is `(scope, model_id,
    model_version)` and names the local vector model retrieval channel 6 uses; the
    gate reads `.locality` off this field at `src/privacy/gate.py:133` to decide
    whether bytes may leave the machine, and an embedding identity has none.

    The target now comes from `ModelCallAuthorities`. The assertion reads the
    request P9 built rather than only checking that nothing raised: `run_call` has
    several ways to return without a real target ever being examined, and each of
    them would satisfy a bare `model_result is not None`."""
    from privacy.release import ModelTarget

    recorder = Recorder()
    wired = _WiredRunCall(recorder)
    result = _group(live, wired, recorder=recorder)

    target = wired.request.model_call_request.model_target
    assert isinstance(target, ModelTarget), target
    assert target == CLOUD, target
    assert result.model_result is not None, result.not_implemented_reason


def test_p9_binds_the_release_to_the_fingerprint_of_the_prompt_p8_sends(live):
    """§6 binds a release to `(model_target, prompt_fingerprint, policy_version)`
    and `transport.issue` recomputes the fingerprint from the `PromptDefinition`
    it is sending, so a request bound to anything else has its release refused by
    `consume_release` (`src/privacy/binding.py:157`) AFTER P7 has spent it.

    `pipeline.py` bound it to `dossier.dossier_fingerprint`, which is the dossier's
    content address and never that. P9 does see the prompt -- its caller hands one
    over in `ModelCallAuthorities` -- so it can and now does derive the value, via
    `grouping.p8_seam.prompt_fingerprint_for`.

    The assertion reads the fingerprint off the request P9 built, not just that the
    call survived: a release refused for some other reason would leave a bare
    `model_result is not None` looking exactly the same."""
    from llm_harness.fingerprint import prompt_fingerprint

    recorder = Recorder()
    wired = _WiredRunCall(recorder)
    result = _group(live, wired, recorder=recorder)

    assert wired.request.model_call_request.prompt_fingerprint == (
        prompt_fingerprint(_prompt()))
    assert result.model_result is not None, result.not_implemented_reason


def test_a_rejected_first_claim_is_not_overruled_by_a_clean_second(live):
    """`src/llm_harness/harness.py:348` returns `verdicts[-1]` -- the last claim by
    position. `run_call`'s own shard selection at `:472` chooses by severity, and
    `src/grouping/vocabulary.py:45` says one verdict per call, "one per shard, one
    per claim". Only the shard half shipped."""
    recorder = Recorder(claims="bad_then_good")
    wired = _WiredRunCall(recorder)
    result = _group(live, wired, recorder=recorder)

    outcomes = [row["outcome"] for row in live.conn.execute(
        "SELECT outcome FROM llm_verdict ORDER BY rowid")]
    assert REJECT in outcomes, outcomes
    assert wired.result.outcome == REJECT, (
        f"P8 returned {wired.result.outcome!r} for a response whose first claim "
        f"was rejected; the returned verdicts were {outcomes}")
    assert result.model_result.membership_ids == (), result.model_result


# --- seam 6: -> P2 -----------------------------------------------------------------

def _version_axes() -> dict:
    axes = {name: None for name in VERSION_TUPLE_FIELDS}
    axes["extractor_versions"] = {}
    axes["prompt_fingerprint"] = "sha256:fp-live"
    axes["model_identifier"] = CLOUD.model_id
    axes["analysis_tiers_enabled"] = ["llm"]
    return axes


def test_p2_replays_the_bundle_the_run_produced_and_measures_the_stage_that_ran(
        live):
    """P2 replays the bundle P1--P7 actually assembled, and P8's own P2 emitter
    reports the verdict. `src/llm_harness/stage_output.py:122-132` passes no
    `dimension_values` to `record_stage_output`, so the stage that ran leaves no
    measurement and `assertions.verdict_for` scores its dimension `not_run`."""
    recorder = Recorder()
    wired = _WiredRunCall(recorder)
    result = _group(live, wired, recorder=recorder)
    assert isinstance(wired.result, P8Verdict), wired.result

    bundle_id = live.run.bundle_id
    assert bundle_files(live.conn, bundle_id), "the run assembled an empty bundle"

    def llm_stage(ctx):
        ref = ctx.conn.execute(
            "SELECT version_tuple_ref FROM run_manifest WHERE run_id = ?",
            (ctx.run_id,)).fetchone()["version_tuple_ref"]
        emit_stage_output(
            ctx.conn, run_id=ctx.run_id, subject_ref=result.group.group_id,
            result=wired.result, inputs=(), version_tuple_ref=ref)
        return []

    run_id = replay_bundle(
        live.conn, bundle_id, version_tuple=_version_axes(), budget_ceilings={},
        run_settings={"model_enabled": True, "embeddings_enabled": False},
        adapters={"llm_interpretation": llm_stage})

    emitted = stage_outputs(live.conn, run_id, stage_id="llm_interpretation")
    assert [row["outcome"] for row in emitted if
            row["subject_ref"] == result.group.group_id] == ["produced"], emitted

    measured = live.conn.execute(
        "SELECT dimension, subject_ref, outcome FROM stage_dimension_value "
        "WHERE run_id = ?", (run_id,)).fetchall()
    assert [row["dimension"] for row in measured] == ["llm_grounding"], (
        "the llm_interpretation stage ran and produced a verdict, and P2 holds no "
        f"measurement for it: {[dict(row) for row in measured]}")


def test_p2_can_carry_an_expectation_for_the_bundle_the_run_produced(live):
    """§8.5's per-stage assertions, reachable from a real run.

    P2 SPEC §3: "A bundle is immutable once CREATED", and `bundle_expectation[]` is
    one of the bundle's contents -- so the labels are supplied TO the assembly, not
    attached to the artefact afterwards. `_assemble_bundle` used to seal before any
    caller could hand one over, which made P2 SPEC Done-means 1 -- a bundle built
    "with every field in §8.5's contents list present" -- unsatisfiable by the only
    code that builds a real bundle, and `assert_run` over one could write nothing.

    The label here was authored in the `live` fixture BEFORE the scan ran. That
    ordering is the point: an expectation attachable after the run is ground truth
    fitted to the results it exists to judge.
    """
    carried = expectations(live.conn, live.run.bundle_id, dimension="extraction")
    assert [row["subject_ref"] for row in carried] == [live.anchor_content_hash]
    assert carried[0]["source"] == "hand-labelled"

    def extraction_from_the_bundle(ctx):
        """P5's real envelope, over the extraction runs the bundle captured.

        ONE EXTRACTOR PER REPLAY, and not by preference. P2 SPEC's dimension table
        gives dimension 1 the subject `(content hash, extractor id)` -- a PAIR --
        but `extractors.stage_output` keys its `DimensionValue` on the content hash
        alone, so this corpus's `pdf.text` and `filesystem.record` runs over one file
        version collide on `stage_dimension_value`'s
        (run_id, dimension, subject_ref) key. Measuring one extractor is one slice of
        the pair and is the only shape available until that key is the pair.

        P4's row is read from the retained `row` column, which is P4's row exactly as
        P4 published it -- the promoted columns are the subset P2 queries and carry
        no `analysis_tier`. `coverage` arrives as stored JSON text.
        """
        def p4_row(stored: str) -> dict:
            row = json.loads(stored)
            return {**row, "coverage": json.loads(row["coverage"])}

        return [StageResult(**{k: v for k, v in extraction_stage_output(
                    run=p4_row(row["row"])).items() if k != "stage_id"})
                for row in ctx.conn.execute(
                    "SELECT row FROM bundle_extraction_run "
                    "WHERE bundle_id = ? AND extractor_name = ?",
                    (ctx.bundle_id, "pdf.text"))]

    run_id = replay_bundle(
        live.conn, live.run.bundle_id, version_tuple=_version_axes(),
        budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        adapters={"extraction": extraction_from_the_bundle})

    assert assert_run(live.conn, run_id) == 1, (
        "§8.5's per-stage assertions are unreachable from a real run")
    row = assertions(live.conn, run_id, dimension="extraction")[0]
    assert row["verdict"] != "not_run", (
        "the extraction stage ran over the bundle's own captured runs; `not_run` "
        "is §8.5's word for the stage that did not")
    # A real value comparison happened. Which way it went is the label's business --
    # P2 states no tolerance (SPEC Open question 2) and this test invents none.
    assert row["verdict"] in ("match", "divergent"), row["verdict"]
    assert json.loads(row["observed"])["coverage"] == {
        "units": "pages", "processed": 1, "total": 1}


# --- the whole path ----------------------------------------------------------------

def test_one_walk_goes_from_a_directory_on_disk_to_a_p9_membership(live):
    recorder = Recorder()
    wired = _WiredRunCall(recorder)
    result = _group(live, wired, recorder=recorder)

    assert live.conn.execute(
        "SELECT count(*) AS c FROM files").fetchone()["c"] == 2
    assert live.conn.execute(
        "SELECT count(*) AS c FROM evidence").fetchone()["c"] > 0
    assert live.conn.execute(
        "SELECT count(*) AS c FROM file_facts").fetchone()["c"] == 2
    assert live.conn.execute(
        "SELECT count(*) AS c FROM release_ledger").fetchone()["c"] == 1
    assert len(recorder.calls) == 1
    assert isinstance(wired.result, P8Verdict), wired.result
    assert result.model_result is not None, result.not_implemented_reason
    assert result.model_result.membership_ids
    assert memberships_for_group(live.conn, result.group.group_id)
    assert live.conn.execute(
        "SELECT count(*) AS c FROM exclusion_verdicts "
        "WHERE label = 'untouched_protected'").fetchone()["c"] == 1
