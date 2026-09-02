# tests/p7/test_p7_cloud_egress_content.py
"""What may leave the device once a real cloud client is wired, and what may not.

Every test above this one in `tests/p7/` was written while nothing in `src/` could
send anything anywhere. `readers/model_anthropic.py` changes that, and these are
the properties that were free before and are load-bearing now.

The client under test is the REAL one. `anthropic_invoke` is called, the returned
`invoke` is the real closure, and only `send` -- the two statements that import
the SDK and open a socket -- is replaced by a recorder. So "the transport was
never reached" here means the real client's real `invoke` was never called, not
that a stand-in was not called.

Three properties, each with the sabotage that proves it is a check and not a
coincidence recorded in the docstring beside it:

  1. An always-local kind cannot be NAMED in a request (`privacy.items`).
  2. A protected file never reaches the transport (`privacy.gate`).
  3. A mode that forbids a cloud target denies before anything is materialised.

And the fourth, which is a ruling rather than a mechanism: `80` §2 rules that a
person's typed self-description is a `user_edits` item, always local, and that
consent does not unlock it. The evidence here is structural -- there is no import
path from the egress chain to the module that holds one.
"""
from __future__ import annotations

import ast
import hashlib
import pathlib
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)
from extractors.schema import create_extraction_schema
from llm_harness.transport import ModelClient
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.records import PromptDefinition
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import A_FACT
from readers.model_anthropic import PROVIDER, anthropic_invoke
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.gate import Gate
from privacy.items import (
    AlwaysLocalRequested, CandidateLabel, EvidenceReference, Excerpt, Filename,
    MetadataField, RedactedIdentifier,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target
from privacy.schema import create_privacy_schema
from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS

OBSERVED_AT = "2026-08-31T09:00:00Z"
PLAN_VERSION = "plan-egress-1"
COMPONENT = "0.1.0"
TEXT = "The spring term syllabus for BUSIB 4300 was issued to the applicant."
SPAN = TextSpan(start=29, end=39)
#: A real target for the real client. `provider` must be `PROVIDER` and
#: `locality` must be cloud, or `anthropic_invoke` refuses to build at all --
#: which is `tests/readers/test_model_anthropic.py`'s subject, not this file's.
CLOUD = ModelTarget(locality="cloud", model_id="a-model", provider=PROVIDER)
#: P7's own ceiling echo. Injected everywhere; a number only a test may choose.
MAX_DOSSIER_TOKENS = 4000
#: The deployment's ceiling, injected. A test's own number.
MAX_RESPONSE_TOKENS = 1024


class _Answer:
    """One text block, shaped like the SDK response `_send` returns."""

    stop_reason = "end_turn"
    stop_details = None

    class _Text:
        type = "text"
        text = '{"claims": []}'

    content = (_Text(),)


class _Socket:
    """Stands in for the two statements that import the SDK and open a socket.

    Everything between `transport.issue` and this list -- `transport`'s own
    recompute, the real `invoke`, the real decode, the real target check -- is the
    product's own code running unmodified.
    """

    def __init__(self) -> None:
        self.sent: list[str] = []

    def __call__(self, *, api_key, model_id, max_tokens, prompt):
        self.sent.append(prompt)
        return _Answer()


def _real_client(socket: "_Socket") -> ModelClient:
    """The REAL deployment client, with only the socket replaced."""
    return ModelClient(model_target=CLOUD, invoke=anthropic_invoke(
        api_key="a-test-key", model_target=CLOUD,
        max_response_tokens=MAX_RESPONSE_TOKENS, send=socket))


# ================================================================================
# 1. An always-local kind cannot be named in a request
# ================================================================================

def test_none_of_the_nine_can_be_named_as_a_releasable_field():
    """SABOTAGE PROVEN: deleting the `_refuse_always_local_name` call from
    `MetadataField.__post_init__` turns every assertion below red."""
    for name in ALWAYS_LOCAL:
        with pytest.raises(AlwaysLocalRequested, match=name):
            MetadataField(name=name)


def test_the_nine_are_refused_however_they_are_spelled():
    """§8.4's own sentence writes them as English. `_normalise` is Task 2's
    transformation and the refusal has to survive it, or "GPS" and "User edits"
    walk through the door "gps" and "user_edits" are refused at."""
    for spelling in ("GPS", "  gps  ", "User edits", "COMPLETE EXTRACTED TEXT",
                     "Raw sensitive values", "File hashes"):
        with pytest.raises(AlwaysLocalRequested):
            MetadataField(name=spelling)


def test_no_releasable_kind_is_one_of_the_nine():
    """The two closed vocabularies do not overlap, checked rather than assumed.

    If a tenth always-local member were ever added with a name matching a
    releasable kind, the request would be constructible and the gate would be the
    only thing between it and the provider."""
    assert set(ITEM_KINDS) & set(ALWAYS_LOCAL) == set()


def test_a_file_id_that_is_a_path_is_refused():
    """§8.4's first always-local word is "Paths"."""
    with pytest.raises(AlwaysLocalRequested, match="path separator"):
        Filename(file_id="/Users/someone/Documents/passport.pdf")
    with pytest.raises(AlwaysLocalRequested, match="path separator"):
        Filename(file_id="corpus\\passport.pdf")


def test_the_complete_list_of_what_a_request_may_carry():
    """The whole releasable surface, enumerated in one assertion.

    This is the list a reader should be able to check the report against: six
    kinds, and the FIELDS of each. Nothing here is a value; every one is a
    reference the gate resolves locally, and `resolve.py` is the only module that
    turns one into a string.
    """
    import dataclasses

    surface = {
        cls.__name__: tuple(f.name for f in dataclasses.fields(cls))
        for cls in (Excerpt, RedactedIdentifier, CandidateLabel, MetadataField,
                    EvidenceReference, Filename)
    }
    assert surface == {
        "Excerpt": ("observation_key", "span", "reason"),
        "RedactedIdentifier": ("observation_key", "span", "identifier_class"),
        "CandidateLabel": ("label",),
        "MetadataField": ("name",),
        "EvidenceReference": ("observation_key",),
        "Filename": ("file_id",),
    }


# ================================================================================
# 2 and 3. The gate, with the real client on the far side of it
# ================================================================================

@pytest.fixture()
def egress_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_privacy_schema(conn)
    create_llm_schema(conn)
    return conn


def _file(conn, name: str, content_hash: str) -> str:
    corpus = Path(tempfile.mkdtemp()) / "corpus"
    corpus.mkdir()
    path = corpus / name
    path.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=4096,
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
        content_hash=content_hash,
    )


def _evidence(conn, file_id: str, content_hash: str) -> str:
    digest = hashlib.sha256(content_hash.encode()).hexdigest()
    run_id = new_id()
    page = (Segment(kind="page", index=1),)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1,
    ))
    record_text_unit(conn, TextUnit(run_id=run_id, container_path=page, text=TEXT))
    location = Location(zone="body", container_path=page, text_span=SPAN)
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name="fixture.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=TEXT[SPAN.start:SPAN.end], location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id=run_id,
        context_before=TEXT[:SPAN.start], context_after=TEXT[SPAN.end:],
        context_truncated=False,
    ))
    return observation_key(
        content_hash=digest, extractor_name="fixture.text",
        locator=serialize_locator(location), raw_value=TEXT[SPAN.start:SPAN.end],
    )


def _store_policy(conn, mode: str) -> Policy:
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode,
        consent_grants=(), redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION,
        set_at=OBSERVED_AT,
    )
    version = set_policy(
        conn, draft, component_version=COMPONENT, user_id="joseph",
        reason="egress content test",
    )
    return replace(draft, policy_version=version)


def _classify(conn, file_id: str, content_hash: str, *, key: str,
              protected: bool) -> None:
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="sensitive_personal" if protected else "public_low",
        protected=protected, basis="detector", evidence_refs=(key,),
        reliability_state="direct", observed_at=OBSERVED_AT,
    ))


def _gate(conn) -> Gate:
    return Gate(
        conn,
        store=ClassificationStore(conn),
        plan_version=PLAN_VERSION,
        classifier=lambda value, *, context_before=None, context_after=None:
            "fixture-identifier-class",
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: (),
        component_version=COMPONENT,
        now=lambda: OBSERVED_AT,
        user_id="joseph",
    )


def _prompt() -> PromptDefinition:
    """Injected and absent of authored text. `76`: `template_bytes` is fingerprinted
    into every audit record, fact row and cache key, so the real one is the owner's
    to ratify and a test's placeholder must not read like a candidate."""
    return PromptDefinition(
        template_id="template.under-ratification",
        template_bytes=b"<no prompt has been ratified; this is a test placeholder>",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"injected"}',
    )


def _request(*, key: str, file_id: str, fingerprint: str) -> ModelCallRequest:
    return ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=CLOUD,
        requested_items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        prompt_template_id="template.under-ratification",
        prompt_fingerprint=fingerprint,
        max_dossier_tokens=MAX_DOSSIER_TOKENS,
    )


def _seed(conn, *, name: str, content_hash: str, protected: bool) -> tuple[str, str]:
    file_id = _file(conn, name, content_hash)
    key = _evidence(conn, file_id, content_hash)
    _classify(conn, file_id, content_hash, key=key, protected=protected)
    return file_id, key


def _issued_events(conn) -> list:
    return list(conn.execute(
        "SELECT event_type FROM events WHERE event_type = 'model_call_issued'"))


def test_a_protected_file_never_reaches_the_real_client(egress_conn):
    """SABOTAGE PROVEN: with `builders["protected_cloud_target"]` removed from
    `privacy/gate.py`, the gate returns `Released` and this test goes red on the
    `isinstance(decision, Denied)` line -- which is exactly the run in which a
    protected file's released excerpt would have gone to a provider.

    The client is built but never handed a release, so `sender.sent` is the
    measurement: it is what the network saw.
    """
    socket = _Socket()
    client = _real_client(socket)
    file_id, key = _seed(
        egress_conn, name="passport.pdf", content_hash="hash-passport",
        protected=True)
    _store_policy(egress_conn, "cloud_assisted")
    prompt = _prompt()

    decision = _gate(egress_conn).release(_request(
        key=key, file_id=file_id, fingerprint=prompt_fingerprint(prompt)))

    assert isinstance(decision, Denied)
    assert decision.reason == "protected_cloud_target"
    assert socket.sent == []
    assert _issued_events(egress_conn) == []
    assert client.model_target is CLOUD          # built, and never spent


def test_a_denial_is_never_a_dead_end(egress_conn):
    """§8.6: the person is told what was deferred and why, and given something to
    do about it. A refusal with no remedy is `Denied.__post_init__`'s own error."""
    file_id, key = _seed(
        egress_conn, name="passport.pdf", content_hash="hash-passport",
        protected=True)
    _store_policy(egress_conn, "cloud_assisted")
    decision = _gate(egress_conn).release(_request(
        key=key, file_id=file_id, fingerprint=prompt_fingerprint(_prompt())))
    assert decision.remedy_options
    assert decision.explanation.strip()


@pytest.mark.parametrize("mode", ["offline", "local_model"])
def test_a_local_first_mode_denies_a_cloud_target(egress_conn, mode):
    """SABOTAGE PROVEN: replacing `mode_forbids(...)` with `False` in
    `privacy/gate.py` makes both parameterisations return `Released`.

    §8.4's `offline` is "No content leaves the device". A wired cloud client does
    not change that sentence, and this is the test that says the sentence is a
    mechanism.
    """
    socket = _Socket()
    _real_client(socket)
    file_id, key = _seed(
        egress_conn, name="notes.pdf", content_hash=f"hash-{mode}", protected=False)
    _store_policy(egress_conn, mode)

    decision = _gate(egress_conn).release(_request(
        key=key, file_id=file_id, fingerprint=prompt_fingerprint(_prompt())))

    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"
    assert socket.sent == []
    assert _issued_events(egress_conn) == []


@pytest.mark.parametrize("mode", ["hybrid", "cloud_assisted"])
def test_the_two_modes_that_permit_a_cloud_target_do(egress_conn, mode):
    """The positive half. Without it the four tests above are satisfied by a gate
    that denies everything, and "nothing left the device" would be true of a
    product that does nothing."""
    file_id, key = _seed(
        egress_conn, name="notes.pdf", content_hash=f"hash-ok-{mode}",
        protected=False)
    _store_policy(egress_conn, mode)
    decision = _gate(egress_conn).release(_request(
        key=key, file_id=file_id, fingerprint=prompt_fingerprint(_prompt())))
    assert isinstance(decision, Released)
    assert decision.model_target == CLOUD


def test_the_released_item_carries_only_the_requested_span(egress_conn):
    """The complete answer to "what can leave the device", measured on the one
    run where something can. Every other character of the text unit is absent."""
    file_id, key = _seed(
        egress_conn, name="notes.pdf", content_hash="hash-span", protected=False)
    _store_policy(egress_conn, "hybrid")
    decision = _gate(egress_conn).release(_request(
        key=key, file_id=file_id, fingerprint=prompt_fingerprint(_prompt())))
    assert isinstance(decision, Released)
    released = "".join(item.value for item in decision.materialised_items)
    assert "applicant" not in released
    assert "spring term" not in released


# ================================================================================
# 4. A self-description cannot reach a provider (`80` §2)
# ================================================================================

def test_a_typed_self_description_is_a_user_edit_and_user_edits_are_always_local():
    """`80` §2, as a mechanism rather than a paragraph.

    The ruling adds no tenth member -- it says the existing `user_edits` covers a
    typed self-description -- so what a test can check is that `user_edits` is
    still one of the nine and still unnameable."""
    assert "user_edits" in ALWAYS_LOCAL
    with pytest.raises(AlwaysLocalRequested):
        MetadataField(name="user_edits")
    with pytest.raises(AlwaysLocalRequested):
        MetadataField(name="user edits")


def test_the_ruling_is_recorded_where_the_member_lives():
    """A closed vocabulary carries its own approval at the member (brief §11 and
    the rule the lead restated: no member is added or reinterpreted without owner
    approval recorded there). If the ruling is ever deleted from
    `privacy/vocabulary.py`, this is what notices."""
    source = pathlib.Path("src/privacy/vocabulary.py").read_text()
    assert "RULING 2026-08-31" in source
    assert "Consent does not unlock it" in source


def test_no_import_path_runs_from_the_egress_chain_to_a_self_description():
    """The structural half, and the one that would catch a future mistake.

    `src/questions/` is where a person's typed answers live. If any module in the
    egress chain -- the transport, the harness, the real client, the gate, the
    release types -- ever imports it transitively, a self-description acquires a
    route to a provider. Today there is no such edge, and this is the test that
    fails on the day one is added.
    """
    src = pathlib.Path("src")
    graph: dict[str, set[str]] = {}
    for path in src.rglob("*.py"):
        dotted = ".".join(path.relative_to(src).with_suffix("").parts)
        dotted = dotted.removesuffix(".__init__")
        edges: set[str] = set()
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                edges.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                edges.add(node.module)
        graph[dotted] = edges

    def reachable(start: str) -> set[str]:
        seen: set[str] = set()
        pending = [start]
        while pending:
            for edge in graph.get(pending.pop(), ()):
                if edge in graph and edge not in seen:
                    seen.add(edge)
                    pending.append(edge)
        return seen

    chain = ("llm_harness.transport", "llm_harness.harness",
             "readers.model_anthropic", "privacy.gate", "privacy.release")
    offending = {
        root: sorted(m for m in reachable(root) if m.startswith("questions."))
        for root in chain
    }
    assert offending == {root: [] for root in chain}, offending


def test_no_module_in_src_invokes_a_model_client_except_the_transport():
    """The budget, the release ledger and the audit record all rest on this.

    `privacy.transport_guard.assert_single_call_site` proves it WITHIN
    `llm_harness/transport.py`, and `tests/p8/test_p8_transport.py` proves it
    across `src/llm_harness/`. Neither looks at the composition root, which is
    where a second caller would actually be written -- somebody reaching past the
    harness to "just check the model is up" spends no release, reserves no budget
    call and writes no audit record, and every byte of the dossier still leaves.
    """
    offending: dict[str, list[int]] = {}
    for path in pathlib.Path("src").rglob("*.py"):
        if path.name == "transport.py":
            continue
        lines = [
            node.lineno
            for node in ast.walk(ast.parse(path.read_text()))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "invoke"
        ]
        if lines:
            offending[str(path)] = lines
    assert offending == {}, offending
