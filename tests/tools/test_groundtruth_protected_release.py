"""Where a protected file's dossier WENT, read out of a run's own database.

`104` §18.7 (9 Sep 2026, confirmed twice) moved the protected question. It used to
be "was this file opened", and the answer was measurable from `text_units` alone.
The owner ruled that protected material IS opened on this machine and shown to the
LOCAL model, never to the cloud, and stays marked and counted -- so the question
became "did any of it leave the device", and that is not a property of the file.
It is a property of the RELEASE the gate minted for the call.

So this module is the seam test for the join, and it is a test rather than a
paragraph because every part of it is a table a person could get wrong by one
column: which release paid for which dossier, which dossier is about which file,
and which of `LOCALITIES` the ledger stored beside it.

Synthetic on purpose, like every other module in this directory: five invented
files, hand-built rows, no product process and nothing outside the repository.
`tests/tools/test_groundtruth_end_to_end.py` is where the harness meets the real
product; what breaks silently here is a SELECT, and a SELECT is provable in
milliseconds against a database this file wrote itself.
"""


from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the path.
# Done HERE rather than in a `conftest.py`, for the reason the sibling test modules
# spell out at length: with no `__init__.py` in the tests tree, a `conftest.py` in
# this directory would take the bare name `conftest` away from `tests/p5/conftest.py`,
# whose tests import from it by that name at call time.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import hashlib
import json
import sqlite3

import pytest

from database_agent.db import create_schema
from evidence_shape.canonical import canonical_json
from evidence_shape.schema import create_evidence_schema
from extractors.router import ROUTING_DDL
from facts.schema import create_facts_schema
from llm_harness.schema import create_llm_schema
from placement.schema import create_placement_schema
from privacy.release import ModelTarget
from privacy.schema import create_privacy_schema
from privacy.vocabulary import CLOUD_LOCALITY, LOCALITIES
from questions.schema import create_questions_schema
from scan_agent.exclusion import EXCLUSION_DDL
from tree_design.schema import create_tree_schema

from tools.groundtruth.labels import load_labels
from tools.groundtruth.measure import (
    RELEASE_BEARING_TABLES,
    UNREADABLE_TARGET,
    observe_run,
)
from tools.groundtruth import measure
from tools.groundtruth.report import scorecard
from tools.groundtruth.score import (
    BREACH_RELEASED,
    protected_verdict,
    score_situation,
)

SITUATION = "academic.coursework"
CLOCK = "2026-09-07T00:00:00Z"
PLAN = "plan-1"

#: Five protected files, one per rule the reader has to get right.
#:
#: Every one of them is marked, extracted, holds text units and was never filed.
#: The ONLY thing that differs between them is the release their call was made
#: under -- which is the whole claim `104` §18.7 makes: reading a protected file
#: here is the product working, and the destination is the entire verdict.
LOCAL = "Medical/vaccination record.txt"        # asked, local target: no breach
CLOUD = "Medical/insurance claim.txt"           # asked, cloud target: BREACH
SEEDED = "Medical/blood panel.txt"              # answer handed over by a prior run
FAILED = "Medical/referral letter.txt"          # cloud call that failed after transport
GARBLED = "Medical/pharmacy receipt.txt"        # a ledger row this cannot parse

IDS = {LOCAL: "f-local", CLOUD: "f-cloud", SEEDED: "f-seeded",
       FAILED: "f-failed", GARBLED: "f-garbled"}

LABELS = {"files": [
    {"path": path, "group": "fixture", "situation": SITUATION,
     "destination": None, "protected": True}
    for path in IDS
]}

#: The two targets, built through the product's own class rather than typed out as
#: JSON. `binding._target_form` is `canonical_json(target.to_mapping())`, and going
#: through `ModelTarget` means a change to the stored shape turns this test RED
#: instead of turning the reader in `measure.py` silent -- which is the failure mode
#: a hand-written fixture string has and cannot report.
LOCAL_TARGET = ModelTarget(locality="local", model_id="qwen3:8b",
                           provider="ollama", context_tokens=8192)
CLOUD_TARGET = ModelTarget(locality=CLOUD_LOCALITY, model_id="deepseek-chat",
                           provider="deepseek")


def _hash(file_id: str) -> str:
    return hashlib.sha256(file_id.encode()).hexdigest()


def _subject(file_id: str) -> str:
    return f"file:{file_id}:{_hash(file_id)}"


def _corpus(root: Path) -> Path:
    for relative in IDS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return root


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    for create in (create_schema, create_evidence_schema, create_facts_schema,
                   create_privacy_schema, create_placement_schema,
                   create_tree_schema, create_questions_schema, create_llm_schema):
        create(conn)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(ROUTING_DDL)
    return conn


def _file_row(conn, file_id: str, corpus: Path, relative: str) -> None:
    conn.execute(
        "INSERT INTO files (file_id, current_path, filename, normalized_filename, "
        "extension, directory_position, volume_id, content_hash, hash_algorithm, "
        "observed_size, observed_timestamps, mime_type, detected_format, scan_state, "
        "extraction_status_by_tier, sensitivity_state) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sha256', 0, '{}', 'text/plain', 'text', "
        "'included', '{}', 'unknown')",
        (file_id, str(corpus / relative), Path(relative).name,
         Path(relative).name.casefold(), Path(relative).suffix, "0",
         "vol-1", _hash(file_id)))
    # Marked and counted -- §18.7 kept that half of the rule intact.
    conn.execute(
        "INSERT INTO classifications (fact_id, file_id, content_hash, handling_class, "
        "protected, basis, evidence_refs, reliability_state, observed_at) "
        "VALUES (?, ?, ?, 'sensitive_personal', 1, 'rule', '[]', 'corroborated', ?)",
        (f"c-{file_id}", file_id, _hash(file_id), CLOCK))
    # And opened on this machine, which is what the ruling permits: an extraction
    # run past `filesystem.record` is what `Observation.opened` reads.
    conn.execute(
        "INSERT INTO extraction_runs (run_id, file_id, content_hash, extractor_name, "
        "extractor_version, source_type, analysis_tier, config, config_fingerprint, "
        "completeness, observation_count, started_at, finished_at) "
        "VALUES (?, ?, ?, 'pdf.text', '1', 'file', 'tier_1', '{}', 'cfg-1', "
        "'complete', 1, ?, ?)",
        (f"x-{file_id}", file_id, _hash(file_id), CLOCK, CLOCK))
    # Abstained, so nothing here is a `filed` breach and the released column is
    # the only thing the verdict can be reacting to.
    conn.execute(
        "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
        "origin_stage, outcome, node_id, created_at, payload) "
        "VALUES (?, ?, ?, 'placement', 'abstain', NULL, ?, ?)",
        (f"d-{file_id}", _subject(file_id), PLAN, CLOCK,
         json.dumps({"ask": None, "review_policy": "auto_eligible"})))


def _dossier(conn, dossier_id: str, file_id: str) -> None:
    conn.execute(
        "INSERT INTO llm_dossier (dossier_id, call_site, subject_ref, "
        "eligibility_reason, plan_version, policy_version, reduction_rung, payload, "
        "observed_at) VALUES (?, 'C_placement', ?, 'bounded_ambiguity', ?, 'pol-1', "
        "'unreduced', '{}', ?)",
        (dossier_id, _subject(file_id), PLAN, CLOCK))


def _ledger(conn, release_id: str, stored_target: str) -> None:
    conn.execute(
        "INSERT INTO release_ledger (release_id, model_target, prompt_fingerprint, "
        "policy_version, content_digest, audit_id, minted_at, spent_at) "
        "VALUES (?, ?, 'fp-1', 'pol-1', 'digest-1', 1, ?, ?)",
        (release_id, stored_target, CLOCK, CLOCK))


def _response(conn, dossier_id: str, release_id: str, model_id: str) -> None:
    conn.execute(
        "INSERT INTO llm_response (response_id, dossier_id, response_bytes, model_id, "
        "prompt_fingerprint, release_audit_id, release_id, observed_at) "
        "VALUES (?, ?, ?, ?, 'fp-1', 1, ?, ?)",
        (f"r-{dossier_id}", dossier_id, b"{}", model_id, release_id, CLOCK))


def _usage(conn, dossier_id: str, release_id: str, model_id: str) -> None:
    conn.execute(
        "INSERT INTO llm_call_usage (usage_id, dossier_id, release_id, model_id, "
        "prompt_tokens, completion_tokens, prompt_cache_hit_tokens, "
        "prompt_cache_miss_tokens, response_format, reserved_cost, observed_at) "
        "VALUES (?, ?, ?, ?, 10, 10, 0, 10, 'json', '1', ?)",
        (f"u-{dossier_id}", dossier_id, release_id, model_id, CLOCK))


def _call_failure(conn, dossier_id: str, release_id: str) -> None:
    conn.execute(
        "INSERT INTO llm_call_failure (failure_id, dossier_id, failure_class, "
        "explanation, release_id, observed_at) "
        "VALUES (?, ?, 'transport_timeout', 'the provider never answered', ?, ?)",
        (f"z-{dossier_id}", dossier_id, release_id, CLOCK))


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One database, five protected files, and one destination each."""
    base = tmp_path_factory.mktemp("protected_release")
    corpus = _corpus(base / "corpus")
    out = base / "out"
    out.mkdir()
    database = out / f"{SITUATION.replace('.', '_')}.sqlite"
    conn = _connect(database)

    for relative, file_id in IDS.items():
        _file_row(conn, file_id, corpus, relative)

    stored_local = canonical_json(LOCAL_TARGET.to_mapping())
    stored_cloud = canonical_json(CLOUD_TARGET.to_mapping())

    # 1. Asked, and the answer came from the model on this machine.
    _dossier(conn, "dos-local", "f-local")
    _ledger(conn, "rel-local", stored_local)
    _response(conn, "dos-local", "rel-local", "qwen3:8b")
    _usage(conn, "dos-local", "rel-local", "qwen3:8b")

    # 2. Asked, and the bytes left the device. The one breach on this corpus.
    _dossier(conn, "dos-cloud", "f-cloud")
    _ledger(conn, "rel-cloud", stored_cloud)
    _response(conn, "dos-cloud", "rel-cloud", "deepseek-chat")
    _usage(conn, "dos-cloud", "rel-cloud", "deepseek-chat")

    # 3. A dossier and a response HANDED to this run by `--reuse-answers-from`.
    #    `tools.groundtruth.reuse` copies both tables forward and deliberately
    #    does not copy the ledger, so this `release_id` dangles on purpose.
    _dossier(conn, "dos-seeded", "f-seeded")
    _response(conn, "dos-seeded", "rel-from-a-prior-run", "deepseek-chat")

    # 4. A cloud call that failed AFTER the transport had it. The release was
    #    spent and the bytes went; only the answer is missing.
    _dossier(conn, "dos-failed", "f-failed")
    _ledger(conn, "rel-failed", stored_cloud)
    _call_failure(conn, "dos-failed", "rel-failed")

    # 5. A ledger row whose target this reader cannot parse. It is a release that
    #    HAPPENED, to a destination nobody can name.
    _dossier(conn, "dos-garbled", "f-garbled")
    _ledger(conn, "rel-garbled", "not json at all")
    _usage(conn, "dos-garbled", "rel-garbled", "who-knows")

    conn.commit()
    conn.close()

    labels_path = base / "labels.json"
    labels_path.write_text(json.dumps(LABELS), encoding="utf-8")
    labels = load_labels(labels_path, known_situations=frozenset({SITUATION}))
    run = observe_run(database, corpus, situation=SITUATION, label="Medical",
                      promised_levels=())
    return {"database": database, "corpus": corpus, "labels": labels, "run": run}


# --- the reading itself -----------------------------------------------------

def test_the_locality_comes_off_the_ledger_and_never_off_the_model_name(built):
    """SABOTAGE: decide locality by comparing `llm_call_usage.model_id` against
    the run's `GRAPH_AGENT_LOCAL_MODEL`.

    Both calls below are `C_placement` calls on a protected file with a response
    and a usage row; the model ids are the only thing a name comparison can see,
    and they are configuration -- the owner pulls a different local model and the
    scoreboard reports eight breaches, or a hosted provider serves one called
    `qwen3:8b` and it reports none. `privacy.binding` wrote the whole
    `ModelTarget` beside the release, so the run has already said which it was.
    """
    files = built["run"].files
    assert files[LOCAL].cloud_releases == ()
    assert files[LOCAL].released_to_cloud is False
    assert files[CLOUD].cloud_releases == ("deepseek/deepseek-chat",)
    assert files[CLOUD].released_to_cloud is True
    # Both were read on this machine. That is the ruling working, not a breach,
    # and it is why `opened` cannot be the column the verdict reads.
    assert files[LOCAL].opened and files[CLOUD].opened


def test_a_release_this_run_never_minted_is_not_this_run_s_release(built):
    """SABOTAGE: count a dangling `release_id` as a cloud destination.

    `tools.groundtruth.reuse` copies `llm_dossier` and `llm_response` forward
    under `--reuse-answers-from` and refuses to copy `release_ledger` -- "a
    single-use capability that paid for a call in another run has not paid for
    anything in this one". So on every seeded database the release columns dangle
    BY DESIGN, and a reader that treated an unmatched id as cloud would report a
    breach for each answer a prior run bought, local answers included, with the
    count growing as reuse improved.
    """
    assert built["run"].files[SEEDED].cloud_releases == ()
    assert built["run"].files[SEEDED].released_to_cloud is False


def test_a_cloud_call_that_failed_still_sent_the_bytes(built):
    """SABOTAGE: read only `llm_response` and `llm_call_usage`.

    `transport.issue` spends the release inside its transaction, "before the
    spend, before the socket", and calls `model_client.invoke` only after that;
    both `record_call_failure` arms are past the invoke. So a row here is a call
    whose payload had already gone to the client and whose answer was unusable --
    and excluding this table would let a provider's timeout launder a release
    nobody can recall. Even without that ordering the verdict stands: the gate
    minted a CLOUD release for a protected file, so the door had already opened
    cloud-ward on it, which is the thing §18.7 forbids.
    """
    assert "llm_call_failure" in RELEASE_BEARING_TABLES
    assert built["run"].files[FAILED].cloud_releases == ("deepseek/deepseek-chat",)


def test_a_target_this_cannot_read_is_named_and_never_dropped(built):
    """SABOTAGE: `except ValueError: continue`, dropping the row.

    A `release_ledger` row was written by the gate, so one this cannot parse is a
    release that HAPPENED to a destination nobody can name -- and unknown is not
    "local". Dropping it is the direction that flatters the product on the
    strength of a column this reader failed to read, which is the one failure
    this package exists to refuse.
    """
    assert built["run"].files[GARBLED].cloud_releases == (UNREADABLE_TARGET,)


# --- the verdict ------------------------------------------------------------

def test_the_verdict_fails_exactly_the_files_whose_bytes_left(built):
    """The whole point, stated as the scorecard states it.

    SABOTAGE: keep the old `if observation.opened` arm. All five files here were
    opened, marked, counted and never filed, and four of them are the ruling
    working; the old scorer failed all five and printed the r19 line -- `PROTECTED
    FAIL -- 8 of 8 protected files ... opened` -- over a run that had held.
    """
    breaches = protected_verdict(built["labels"], built["run"].files)
    # In path order, which is the verdict's own order: the scorecard prints these
    # to a person, and a list that reordered itself between runs would read as a
    # different set of problems every time.
    assert [(b.path, b.kind) for b in breaches] == [
        (CLOUD, BREACH_RELEASED),
        (GARBLED, BREACH_RELEASED),
        (FAILED, BREACH_RELEASED),
    ]
    # The two that held are absent from the verdict entirely, which is the only
    # way a person can tell a run that behaved from one that was not measured.
    assert not any(b.path in {LOCAL, SEEDED} for b in breaches)


def test_the_breach_names_the_target_so_a_person_can_act_on_it(built):
    breaches = protected_verdict(built["labels"], built["run"].files)
    detail = next(b.detail for b in breaches if b.path == CLOUD)
    assert "deepseek/deepseek-chat" in detail


def test_the_scorecard_prints_the_released_count_under_its_own_word(built):
    """The block a person reads first, on a run that failed.

    SABOTAGE: leave the card's second line reading `opened`. The word is the
    whole message -- `not marked` is the half that improves as extraction
    improves, and `released` is the half no later version of this product can
    undo -- and a card that names a kind the verdict no longer mints prints `0`
    beside it forever while three real breaches go unlabelled.
    """
    breaches = protected_verdict(built["labels"], built["run"].files)
    card = scorecard([built["run"]], [score_situation(built["run"], built["labels"])],
                     built["labels"], breaches, [],
                     corpus_files=len(IDS), seconds=1.0)
    assert f"PROTECTED   FAIL -- 3 of {len(IDS)} protected files" in card
    assert f"3  {BREACH_RELEASED}" in card
    assert "opened" not in card
    assert "CANNOT be undone" in card


# --- the spelling this instrument keeps for itself --------------------------

def test_the_cloud_locality_is_pinned_against_the_product_s_own_vocabulary():
    """`measure.py` spells `"cloud"` rather than importing it, because it has to
    read a database an older build wrote and importing the product's vocabulary
    would make the instrument agree with the product by construction.

    SABOTAGE: rename `privacy.vocabulary.CLOUD_LOCALITY` and leave this reader
    alone. A copied spelling that nothing ties back is a comparison that silently
    stops matching, and the scoreboard would print PASS forever. This is the tie:
    the divergence is a red test here, exactly as `test_groundtruth_held_proposals`
    pins the deciders against `placement.vocabulary`.
    """
    assert measure.CLOUD_LOCALITY == CLOUD_LOCALITY
    assert measure.CLOUD_LOCALITY in LOCALITIES
