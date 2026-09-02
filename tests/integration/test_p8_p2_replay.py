"""P8→P2 replay: stored response bytes re-validate without a model call."""
from __future__ import annotations

import pytest

from llm_harness.records import EvidenceItem
from llm_harness.schema import create_llm_schema
from llm_harness.stage_output import (
    emit_stage_output,
    record_p8_version_tuple,
    replay_recorded_response,
)
from llm_harness.store import record_dossier, record_response
from llm_harness.transport import ModelClient
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    DIRECT_ANCHOR,
    REJECT,
)
from p8.conftest import (
    FIXED_CLOCK,
    RELEASED_MATERIAL,
    make_dossier,
    make_fact_bundle,
    make_released_evidence,
    make_verdict,
    record_subject,
)
from privacy.release import ModelTarget

from database_agent.db import create_schema
from eval_harness.run import VERSION_TUPLE_FIELDS, get_version_tuple, start_run
from eval_harness.stage_output import stage_outputs
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

DIRECT_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[{"evidence_ref":"obs-key-1","cited_span":"Columbia University",'
    b'"why_it_supports":"names the school"}]}]}'
)
def _direct_bytes(key: str) -> bytes:
    """A stored response citing a real P4 observation key (M14: `sha256:` prefixed)."""
    return DIRECT_BYTES.replace(b"obs-key-1", key.encode("ascii"))


UNKNOWN_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school"},'
    b'"unknown":{"insufficiency_statement":"no labeled school"}}]}'
)

PROMPT_FP = "fp-p8-replay"
MODEL_ID = "fixture-model"


def _axes():
    return dict(
        extractor_versions={},
        graph_algorithm_version=None,
        prompt_fingerprint=PROMPT_FP,
        model_identifier=MODEL_ID,
        template_library_version=None,
        placement_scorer_version=None,
        analysis_tiers_enabled=["llm"],
    )


def _resolver(released: str | None, key: str = "obs-key-1"):
    def resolve(observation_key: str) -> str | None:
        if observation_key == key:
            return released
        return None
    return resolve


def _never_contradicts(*_a, **_k):
    return False


class _Trap:
    def __init__(self):
        self.calls = []

    def __call__(self, payload: bytes) -> bytes:
        self.calls.append(payload)
        raise AssertionError("replay must not invoke ModelClient")


@pytest.fixture()
def replay_conn(conn):
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_llm_schema(conn)
    create_eval_schema(conn)
    create_fields(conn)
    return conn


@pytest.fixture()
def subject(replay_conn, tmp_path):
    return record_subject(replay_conn, tmp_path)


def _dossier(key: str = "obs-key-1", *, subject_ref: str = "file-1"):
    """A reference AND what P7 released under it.

    An `evidence_items` entry is the reference the model is allowed to cite; the
    text it may quote is `released_evidence`. A dossier with the first and not
    the second showed the model a handle and no material, so every citation to it
    is ungrounded -- which is what Site A now says.
    """
    return make_dossier(
        subject_ref=subject_ref,
        evidence_items=(
            EvidenceItem(
                evidence_ref=key,
                kind="excerpt",
                location="body",
                excerpt_span=(0, len(RELEASED_MATERIAL)),
                reliability_state="direct",
                basis=DIRECT_ANCHOR,
            ),
        ),
        released_evidence=(
            make_released_evidence(
                observation_key=key,
                address=f"0:{len(RELEASED_MATERIAL)}",
                value=RELEASED_MATERIAL,
            ),
        ),
    )


def test_fixture_records_version_tuple_then_starts_run_then_emits(replay_conn):
    ref = record_p8_version_tuple(replay_conn, **_axes())
    run_id = start_run(
        replay_conn, bundle_id="bundle-replay", run_kind="replay",
        version_tuple_ref=ref, budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    output_id = emit_stage_output(
        replay_conn, run_id=run_id, subject_ref="file-1",
        result=make_verdict(), inputs=("obs-key-1",), version_tuple_ref=ref,
    )
    row = stage_outputs(replay_conn, run_id, stage_id="llm_interpretation")[0]
    assert row["stage_output_id"] == output_id
    assert row["outcome"] == "produced"
    assert row["budget_state"] == "within_ceiling"
    stored = get_version_tuple(replay_conn, ref)
    assert tuple(stored) == VERSION_TUPLE_FIELDS or set(stored) == set(VERSION_TUPLE_FIELDS)
    assert stored["prompt_fingerprint"] == PROMPT_FP
    assert stored["model_identifier"] == MODEL_ID
    assert "validator_version" not in stored
    assert "policy_version" not in stored


def test_replay_revalidates_stored_bytes_without_a_model_call(replay_conn, subject):
    key = subject[2]
    bundle = make_fact_bundle(replay_conn, subject)
    trap = _Trap()
    client = ModelClient(
        model_target=ModelTarget(locality="local", model_id=MODEL_ID, provider="fixture"),
        invoke=trap,
    )
    dossier = _dossier(key, subject_ref=subject[0])
    record_dossier(replay_conn, dossier, observed_at=FIXED_CLOCK)
    record_response(
        replay_conn, dossier_id=dossier.dossier_id, response_bytes=_direct_bytes(key),
        model_id=MODEL_ID, prompt_fingerprint=PROMPT_FP, release_audit_id=17,
        release_id="release-fixture", observed_at=FIXED_CLOCK,
    )
    ref = record_p8_version_tuple(replay_conn, **_axes())
    run_id = start_run(
        replay_conn, bundle_id="bundle-replay", run_kind="replay",
        version_tuple_ref=ref, budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    verdicts, report = replay_recorded_response(
        replay_conn, dossier,
        evidence_resolver=_resolver(RELEASED_MATERIAL, key),
        site_dependencies=bundle,
        contradicts=_never_contradicts,
        dossier_builder="fixture",
        policy_version="policy-1", handle_key=FIXTURE_HANDLE_KEY,
    )
    assert trap.calls == []
    assert client.invoke is trap
    assert len(verdicts) == 1
    assert verdicts[0].outcome == ACCEPT_DIRECT
    assert report.claims_accepted_direct == 1
    emit_stage_output(
        replay_conn, run_id=run_id, subject_ref=dossier.subject_ref,
        result=verdicts[0], inputs=("obs-key-1",), version_tuple_ref=ref,
    )
    row = stage_outputs(replay_conn, run_id, stage_id="llm_interpretation")[0]
    assert row["outcome"] == "produced"
    assert trap.calls == []


def test_replay_does_not_trust_cached_validation(replay_conn, subject):
    key = subject[2]
    bundle = make_fact_bundle(replay_conn, subject)
    trap = _Trap()
    ModelClient(
        model_target=ModelTarget(locality="local", model_id=MODEL_ID, provider="fixture"),
        invoke=trap,
    )
    dossier = _dossier(key, subject_ref=subject[0])
    record_dossier(replay_conn, dossier, observed_at=FIXED_CLOCK)
    record_response(
        replay_conn, dossier_id=dossier.dossier_id, response_bytes=_direct_bytes(key),
        model_id=MODEL_ID, prompt_fingerprint=PROMPT_FP, release_audit_id=17,
        release_id="release-fixture", observed_at=FIXED_CLOCK,
    )
    first, _ = replay_recorded_response(
        replay_conn, dossier,
        evidence_resolver=_resolver(RELEASED_MATERIAL, key),
        site_dependencies=bundle,
        contradicts=_never_contradicts,
        dossier_builder="fixture",
        policy_version="policy-1", handle_key=FIXTURE_HANDLE_KEY,
    )
    assert first[0].outcome == ACCEPT_DIRECT
    stored_outcome = replay_conn.execute(
        "SELECT outcome FROM llm_verdict WHERE dossier_id = ?",
        (dossier.dossier_id,),
    ).fetchone()
    assert stored_outcome is None
    # Same dossier, same stored bytes, same P6 authority -- only the store has
    # moved: the observation the response cites no longer resolves. A replay that
    # trusted its earlier verdict would still say `accept_direct`.
    second, report = replay_recorded_response(
        replay_conn, dossier,
        evidence_resolver=_resolver(None, key),
        site_dependencies=bundle,
        contradicts=_never_contradicts,
        dossier_builder="fixture",
        policy_version="policy-1", handle_key=FIXTURE_HANDLE_KEY,
    )
    assert trap.calls == []
    assert second[0].outcome == REJECT
    assert second[0].reasons == (CITATION_NOT_FOUND,)
    assert report.claims_rejected == 1
    assert first[0].outcome != second[0].outcome


def test_site_a_replay_appends_no_second_p6_consequence(replay_conn, subject):
    """The one boundary replay must not cross.

    `facts.unresolved.write_unresolved` is "Always an INSERT, never an update and
    never de-duplicated". Site A's `apply_verdict` is the only place P8 writes
    into another part's store, and replay drove it unconditionally: re-validating
    one stored abstention left P6 saying the model had declined twice.
    """
    from facts.unresolved import unresolved_for_file

    file_id, content_hash, key = subject
    bundle = make_fact_bundle(replay_conn, subject)
    dossier = _dossier(key, subject_ref=file_id)
    record_dossier(replay_conn, dossier, observed_at=FIXED_CLOCK)
    record_response(
        replay_conn, dossier_id=dossier.dossier_id,
        response_bytes=UNKNOWN_BYTES,
        model_id=MODEL_ID, prompt_fingerprint=PROMPT_FP, release_audit_id=17,
        observed_at=FIXED_CLOCK,
        release_id="release-fixture",
    )

    def replay():
        return replay_recorded_response(
            replay_conn, dossier,
            evidence_resolver=_resolver(RELEASED_MATERIAL, key),
            site_dependencies=bundle,
            contradicts=_never_contradicts,
            dossier_builder="fixture",
            policy_version="policy-1", handle_key=FIXTURE_HANDLE_KEY,
        )

    first, _ = replay()
    second, _ = replay()
    third, _ = replay()
    assert [v.outcome for v in first] == [ABSTAIN]
    assert [v.outcome for v in second] == [ABSTAIN]
    assert first[0].verdict_id == third[0].verdict_id
    assert [row["reason"] for row in unresolved_for_file(
        replay_conn, file_id, content_hash)] == []


def test_replay_reads_the_latest_response_under_a_fixed_clock(
    replay_conn, subject, monkeypatch,
):
    """`response_id` is a uuid4. Ordering by it under an injected fixed clock --
    which is how every test and every replay run is driven -- made "the latest
    response" a coin toss, so a replay could re-validate an older response than
    the caller meant.

    The ids here descend as the rows are inserted, so the two orderings disagree
    every time rather than half the time.
    """
    from llm_harness import store

    file_id, _content_hash, key = subject
    bundle = make_fact_bundle(replay_conn, subject)
    dossier = _dossier(key, subject_ref=file_id)
    record_dossier(replay_conn, dossier, observed_at=FIXED_CLOCK)

    descending = iter(["response-9", "response-1"])
    monkeypatch.setattr(store, "_new_id", lambda: next(descending))
    for response_bytes in (UNKNOWN_BYTES, _direct_bytes(key)):
        record_response(
            replay_conn, dossier_id=dossier.dossier_id,
            response_bytes=response_bytes, model_id=MODEL_ID,
            prompt_fingerprint=PROMPT_FP, release_audit_id=17,
            release_id="release-fixture", observed_at=FIXED_CLOCK,
        )
    assert [row["response_id"] for row in replay_conn.execute(
        "SELECT response_id FROM llm_response ORDER BY rowid"
    )] == ["response-9", "response-1"]

    verdicts, _report = replay_recorded_response(
        replay_conn, dossier,
        evidence_resolver=_resolver(RELEASED_MATERIAL, key),
        site_dependencies=bundle,
        contradicts=_never_contradicts,
        dossier_builder="fixture",
        policy_version="policy-1", handle_key=FIXTURE_HANDLE_KEY,
    )
    assert [v.outcome for v in verdicts] == [ACCEPT_DIRECT]
