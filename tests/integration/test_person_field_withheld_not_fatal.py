# tests/integration/test_person_field_withheld_not_fatal.py
"""`104` R-161's SECOND half, end to end: a signalled field costs the file that
field, and not its call.

THE TRAP THIS FILE EXISTS TO HOLD SHUT (`104` §17.6, written before the build):

    The signal feeds `sensitive_observation_keys`, one of the four exclusions in
    `model_facts.may_be_released`, and every one of those refuses the WHOLE
    request rather than the item. `Author` was released 139 times, `Creator` 50 and
    `last_modified_by` 85 over 617 dossiers, so the naive implementation costs 139
    files their entire model call and re-starves site A in one commit, while
    looking like a privacy improvement.

Two corrections the build measured, both stated here because a later reader will
otherwise re-derive them:

  1. **The refusal is `AlwaysLocalRequested` -> `Denied(always_local_item)`, not
     `ProtectedItemRequested`.** `items.check_item` raises the first for an
     `Excerpt` over a signalled key under §8.4's `raw_sensitive_values`;
     `ProtectedItemRequested` is §7.3's, about an unratified item kind on a
     PROTECTED file, and is a different refusal reached a different way. The cost
     is the same -- the whole request -- so the trap is real; only its name was
     wrong.
  2. **The withhold already existed at the two builders that were wired**, and
     that is why the ruling costs no file its call. `may_be_released` drops a
     signalled key from the OFFER (site A) and `model_placement.releasable_excerpts`
     does the same at site C, both of them "one of the gate's own refusals applied a
     step early so the call is never BUILT rather than built and denied". So the
     tests below PIN behaviour that holds rather than announce behaviour that is
     new -- and the one builder where it did NOT hold is site B, which
     `tests/p9/test_p9_person_field_excerpt.py` covers.

Measured against `~/.graph-agent/lead/gt-w1bn/academic_coursework.sqlite` (199
files, read-only copy, 8 Sep 2026): 76 person-valued readings across 60 files are
now signalled, 76 readings are withheld from the offer, and the number of files
whose offer empties -- `fact_call_stage`'s `if not offered: return ()`, which is
what "loses its call" actually means -- is **0 before and 0 after**, at both
localities.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

import cli
from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter, observation_keys_for_run
from extractors.long_tail import record_sensitivity_signals
from extractors.pdf import PdfDocument, PdfPage, extract_pdf, person_field_signals
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from model_facts import ordered_releasable_observations, releasable_observations
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.gate import Gate
from privacy.items import Excerpt, sensitive_observation_keys
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target

OBSERVED_AT = "2026-09-08T09:00:00Z"
PLAN_VERSION = "plan-person-field"
COMPONENT = "0.1.0"
LOCAL = ModelTarget(locality="local", model_id="a-model", provider="Ollama")
CLOUD = ModelTarget(locality="cloud", model_id="a-model", provider="Acme")
MAX_DOSSIER_TOKENS = 4000
CONTENT_HASH = "c977b477a6329f00518d55e10bb5c469fc6b24e8528f3fc1a9bbbbe94a6feada"

AUTHOR = "Daniel Lacker"
#: What every one of the 25 `/Author` PDFs on the owner's corpus also carries: a
#: title, a producer string, and a page of its own prose. The point of the fixture
#: is that the Author is NOT the only thing the file can say.
A_LECTURE = PdfDocument(
    metadata={"Author": AUTHOR, "Title": "Lecture 3: Martingales",
              "Producer": "Acrobat Distiller", "Creator": "Microsoft Word"},
    pages=(PdfPage(number=1, text="PHYS1401. Martingales and stopping times."),),
)


@pytest.fixture()
def person_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    from privacy.schema import create_privacy_schema
    create_privacy_schema(conn)
    return conn


def _scanned_lecture(conn) -> tuple[str, dict[str, str]]:
    """P1's row, P5's run, P4's rows and P5's signals -- the live sequence, with
    nothing stubbed between the extractor and the database."""
    corpus = Path(tempfile.mkdtemp()) / "corpus"
    corpus.mkdir()
    document = corpus / "Lecture 3.pdf"
    document.write_bytes(b"%PDF-1.7\n")
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=4096,
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
        content_hash=CONTENT_HASH)

    produced = extract_pdf(
        file_row={"file_id": file_id, "content_hash": CONTENT_HASH,
                  "filename": document.name},
        path=document,
        policy=SafetyPolicy(is_protected_container=lambda p: False,
                            is_dataless=lambda p: False),
        read_pdf=lambda target: A_LECTURE,
        find_structured_strings=lambda text: (),
        now=OBSERVED_AT, context_window=20)

    run_id = RunWriter(conn, author="extractors").write(produced)
    keys = observation_keys_for_run(conn, run_id)
    record_sensitivity_signals(
        conn, run_id=run_id, signals=person_field_signals(produced),
        observation_keys=keys, now=OBSERVED_AT)

    by_value = {row["raw_value"]: keys[index]
                for index, row in enumerate(produced.observations)}

    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=CONTENT_HASH, handling_class="public_low",
        protected=False, basis="detector", evidence_refs=(keys[0],),
        reliability_state="direct", observed_at=OBSERVED_AT))
    set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(("area-1", "cloud_model"),),
        redaction_settings=dict(MORE_REDACTING), automatic_move_permissions={},
        plan_version=PLAN_VERSION, set_at=OBSERVED_AT),
        component_version=COMPONENT, user_id="joseph",
        reason="person field withheld, not fatal")
    return file_id, by_value


def _gate(conn) -> Gate:
    return Gate(
        conn, store=ClassificationStore(conn), plan_version=PLAN_VERSION,
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: (),
        component_version=COMPONENT, now=lambda: OBSERVED_AT, user_id="joseph")


def _ask(conn, file_id: str, keys, *, target=CLOUD):
    return _gate(conn).release(ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=target,
        requested_items=tuple(
            Excerpt(observation_key=key, span=None, reason="the file's own reading")
            for key in keys),
        prompt_template_id="template.under-ratification",
        prompt_fingerprint="fingerprint-person-1",
        max_dossier_tokens=MAX_DOSSIER_TOKENS))


# --- the signal reaches the door -------------------------------------------------

def test_the_author_reaches_the_database_as_a_signal(person_conn):
    """r15's `extraction_sensitivity_signal` table was EMPTY over 199 files
    (`104` R-161). A signal the orchestrator does not write is a signal P7 has
    nothing to redact against, so the chain is asserted and not the emitter."""
    file_id, by_value = _scanned_lecture(person_conn)
    assert sensitive_observation_keys(person_conn, file_id) == frozenset(
        {by_value[AUTHOR]})


@pytest.mark.parametrize("target", [LOCAL, CLOUD])
def test_asked_for_alone_the_author_is_refused_at_the_door(person_conn, target):
    """§8.4's `raw_sensitive_values`, and it is NOT divided by the target: a
    recognised human identifier is not a fact about where the value is going."""
    file_id, by_value = _scanned_lecture(person_conn)
    decision = _ask(person_conn, file_id, [by_value[AUTHOR]], target=target)
    assert isinstance(decision, Denied)
    assert decision.reason == "always_local_item"
    assert AUTHOR not in decision.explanation


# --- and the file keeps its call -------------------------------------------------

@pytest.mark.parametrize("locality", ["local", "cloud"])
def test_the_offer_drops_the_author_and_keeps_everything_else(person_conn, locality):
    """The withhold, at the builder. `may_be_released` asks the door's own question
    a step early, so the call is never BUILT with the Author in it."""
    file_id, by_value = _scanned_lecture(person_conn)
    # `limit` became required on this function in `104` R-164, after this test was
    # written: the deployment's own cap, so what is asserted is the offer a real
    # call would build rather than an unbounded one no caller ever asks for.
    offered = ordered_releasable_observations(
        person_conn, file_id=file_id, content_hash=CONTENT_HASH, locality=locality,
        limit=cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS)
    values = {observation.raw_value for observation in offered}
    assert AUTHOR not in values
    assert "Lecture 3: Martingales" in values
    assert "Acrobat Distiller" in values


@pytest.mark.parametrize("locality,target", [("local", LOCAL), ("cloud", CLOUD)])
def test_a_file_carrying_a_signalled_field_still_gets_its_call(
        person_conn, locality, target):
    """THE PIN THE RULING ASKED FOR. `104` §17.6: "make a signalled observation be
    withheld from the offer instead of fatal to the request."

    Every item the builder offers goes through the door in ONE request, so a
    request that carries a refused item costs the file everything else in it. The
    assertion is `Released`, and it is over the offer the builder actually makes.
    """
    file_id, _by_value = _scanned_lecture(person_conn)
    offered = releasable_observations(
        person_conn, file_id=file_id, content_hash=CONTENT_HASH, limit=12,
        locality=locality, ceiling=MAX_DOSSIER_TOKENS)
    assert offered, (
        "the file's offer emptied, which is `fact_call_stage`'s `if not offered: "
        "return ()` -- the file loses its whole call and this ruling re-starves "
        "site A")
    decision = _ask(person_conn, file_id,
                    [item.observation_key for item in offered], target=target)
    assert isinstance(decision, Released), getattr(decision, "explanation", decision)
    released = {item.value for item in decision.materialised_items}
    assert AUTHOR not in released
    assert "Lecture 3: Martingales" in released


def test_the_whole_offer_would_die_if_the_author_were_left_in(person_conn):
    """The counterfactual, asserted rather than described, because it is the whole
    reason the withhold is at the builder and not at the door.

    Without this the tests above are also satisfied by a door that refuses the item
    and releases the rest -- which is not what the door does.
    """
    file_id, by_value = _scanned_lecture(person_conn)
    offered = releasable_observations(
        person_conn, file_id=file_id, content_hash=CONTENT_HASH, limit=12,
        locality="cloud", ceiling=MAX_DOSSIER_TOKENS)
    keys = [item.observation_key for item in offered] + [by_value[AUTHOR]]
    decision = _ask(person_conn, file_id, keys)
    assert isinstance(decision, Denied)
    assert decision.reason == "always_local_item"
