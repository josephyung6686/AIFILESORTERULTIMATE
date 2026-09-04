"""The model path of P11, wired as far as it can honestly go.

`85` §5 again, at Sites C and D: `placement_inputs` in `src/cli.py` passes
`gate=None, model_client=None, prompt=None, call_dependencies=None`, so
`PipelineInputs.model_path_available()` has been `False` on every run this product
has ever made and §6.12 step 7 has never once executed. `model_facts.py` did the
same job for Site A and is the shape this follows.

**What these tests do NOT assert is that a call is made.** No prompt is ratified
for `C_placement` or `D_residual` -- `planning/82-FACT-PROMPT-DRAFT.md` §0 records
the owner's ratification for `A_fact` and for nothing else -- and an agent may not
author prompt text. So the module is built to the prompt and stops there, and the
first test pins the honest state that leaves: with no prompt, every injection is
absent together and the pipeline abstains exactly as it does today.

The second group is the one that matters most. Placement is ABOUT paths, and paths
are `ALWAYS_LOCAL`. What a placement call may release is therefore not obvious, and
these tests pin it rather than leaving it to be discovered at a provider.
"""
from __future__ import annotations

import zlib
from decimal import Decimal

import pytest

from database_agent.db import create_schema
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from extractors.schema import create_extraction_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit
from llm_harness.budgets import ScanBudget
from llm_harness.records import EvidenceItem
from privacy.release import ModelTarget
from privacy.vocabulary import ALWAYS_LOCAL_ZONES

from model_placement import (
    PLACEMENT_STAGE,
    PlacementCallAuthorities,
    model_path_injections,
    releasable_excerpts,
)

T0 = "2026-09-04T00:00:00Z"
PLAN = "version-1"
FILE = "file-1"
#: P1's shape, checked by `Observation.__post_init__` -- 64 lowercase hex.
HASH = "a" * 64
RUN = "run-1"
TARGET = ModelTarget(locality="cloud", model_id="deepseek-chat",
                     provider="deepseek")


@pytest.fixture()
def db(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    # P5's tables, because `releasable_excerpts` reads P5's per-value sensitivity
    # signal. A read against an absent table proves nothing about the read.
    create_extraction_schema(conn)
    record_run(conn, ExtractionRun(
        run_id=RUN, file_id=FILE, content_hash=HASH, extractor_name="fixture",
        extractor_version="1", source_type="text_document",
        analysis_tier="native", config={}, completeness="complete",
        started_at=T0))
    return conn


def _authorities(**overrides) -> PlacementCallAuthorities:
    values = dict(
        gate=object(), model_client=object(), prompt=None, model_target=TARGET,
        evidence_resolver=lambda key: "text", contradicts=lambda *a, **k: False,
        scan_budget=ScanBudget(scan_id="scan-1", corpus_file_count=1,
                               max_calls_per_1000_files=1,
                               max_estimated_cost=Decimal("1"),
                               min_calls_per_scan=0),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        policy_version="policy-1", wire_handle_key=b"k" * 32,
        sensitivity_policy=lambda *a, **k: True,
        chosen_node_of=lambda verdict: verdict.claim_ref,
        residual_action_of=None)
    values.update(overrides)
    return PlacementCallAuthorities(**values)


# --- the honest absent state ------------------------------------------------


def test_with_no_ratified_prompt_every_injection_is_absent_together(db):
    """`model_path_available()` reads all seven as a SET, and this respects that.

    Its own docstring says what a half-injection costs: the missing piece is
    discovered "after a dossier has been assembled". So a deployment with no
    prompt supplies no gate, no client and no dependencies either -- the file
    abstains with a reason, which is what it does today, and nothing is built.
    """
    injections = model_path_injections(db, _authorities(), plan_version=PLAN)

    assert set(injections) == {
        "gate", "model_client", "prompt", "call_dependencies",
        "model_call_request", "chosen_node_of", "residual_action_of",
        "sensitivity_policy",
    }
    assert all(injections[name] is None for name in injections)


def test_with_a_prompt_every_injection_the_step_needs_is_present(db):
    """The other side of the same set: one prompt away from a live model path."""
    injections = model_path_injections(
        db, _authorities(prompt=object()), plan_version=PLAN)

    required = ("gate", "model_client", "prompt", "call_dependencies",
                "model_call_request", "chosen_node_of", "sensitivity_policy")
    assert all(injections[name] is not None for name in required)


# --- what a placement call may release --------------------------------------


def _observation(db, *, key: str, zone: str, value: str,
                 span: TextSpan | None, unit_text: str | None) -> str:
    """One observation, and the text unit its span points into when it has one.

    Returns the `observation_key` P4 minted, which is what a placement call
    addresses; the `key` argument only names the container path so two
    observations in one test do not share a unit.
    """
    # A distinct page per observation, so two of them in one test never share a
    # text unit -- `unit_length_for_observation` keys on the container path.
    # `crc32` and not `hash`: `hash` is salted per interpreter, and a fixture
    # whose addresses move between runs is a fixture that can fail on Tuesdays.
    path = (Segment(kind="page", index=1 + zlib.crc32(key.encode()) % 900),)
    if unit_text is not None:
        record_text_unit(db, TextUnit(
            run_id=RUN, container_path=path, text=unit_text))
    observation = Observation(
        file_id=FILE, content_hash=HASH, extractor_name="fixture",
        extractor_version="1", source_type="text_document", raw_value=value,
        location=Location(zone=zone, container_path=path, text_span=span),
        occurrence_count=1, observed_at=T0, reliability="direct", run_id=RUN)
    record_observation(db, observation)
    return observation.observation_key


def test_no_always_local_zone_is_ever_offered_to_a_placement_model(db):
    """The whole point of asking this question at Site C rather than inheriting it.

    Placement is about where a file belongs, so the observations that most
    obviously bear on it are the ones naming where it already IS -- and `path`
    and `filename` are the zones §8.4's always-local members 1 and 6 have a route
    out through. The filesystem extractor writes one observation per file whose
    raw value is the parent directory. Offering it here would send the owner's
    folder structure to a provider under the name "evidence".

    **Iterated over `ALWAYS_LOCAL_ZONES` rather than over a list written here**,
    and `d005418` is why: `ocr` was added to that set on 2026-09-04 as member 3
    (text Apple Vision read off a scanned identity card), and the comment beside
    the set says the mapping from the nine kinds of DATA to the fifteen zones is
    made BY HAND, one member at a time. A test naming its own zones would have
    gone on passing while the placement path offered OCR text, which is exactly
    the shape of the defect that commit fixes. This one covers member 4 on the
    day someone maps it, without being edited.
    """
    always_local = {
        zone: _observation(db, key=f"k-{zone}", zone=zone,
                           value=f"a value read from the {zone} zone",
                           span=None, unit_text=None)
        for zone in sorted(ALWAYS_LOCAL_ZONES)
    }
    assert always_local, "ALWAYS_LOCAL_ZONES is empty; this test proves nothing"
    heading = _observation(
        db, key="k-head", zone="heading", value="PHYS1401",
        span=TextSpan(start=0, end=8),
        unit_text="PHYS1401 Lecture 8 — Rotational dynamics")

    offered = releasable_excerpts(
        db, evidence_refs=(*always_local.values(), heading))

    assert [item.observation_key for item in offered] == [heading]


def test_the_span_offered_is_the_observations_own_and_never_a_synthesised_one(db):
    """The defect this function exists to stop, and it is live in `cli.evidence_for`.

    `cli.evidence_for` builds every `EvidenceItem` with
    `excerpt_span=(0, len(canonical_value))` -- a span over the VALUE, laid against
    a text unit it did not come from. P7 resolves a span by taking that substring
    of the UNIT, so a 8-character value would release the first 8 characters of the
    document, whatever they are. `model_facts.build_fact_request` writes the same
    rule down for Site A: the span is the observation's OWN, never a synthesised
    `(0, len(value))`.
    """
    heading = _observation(
        db, key="k-head", zone="heading", value="PHYS1401",
        span=TextSpan(start=17, end=25),
        unit_text="Lecture 8 for the PHYS1401 course, week three")

    offered = releasable_excerpts(db, evidence_refs=(heading,))

    assert len(offered) == 1
    assert offered[0].span == TextSpan(start=17, end=25)


def test_an_observation_covering_its_whole_unit_is_refused_before_the_spend(db):
    """§8.4's own sentence, applied where it costs nothing to apply it.

    "should not send full documents where a short heading or OCR excerpt is
    enough". The gate refuses this too, with `whole_document_requested` -- but it
    refuses AFTER the text has been materialised and after the release was minted,
    so leaving it to the door means paying to build a document in order to say no
    to it.
    """
    whole = _observation(
        db, key="k-all", zone="body", value="the whole thing",
        span=TextSpan(start=0, end=15), unit_text="the whole thing")

    assert releasable_excerpts(db, evidence_refs=(whole,)) == ()


def test_a_placement_request_names_the_placement_stage_and_this_file_only(db):
    """§8.4's audit record says which stage asked and about what. Both are pinned.

    `Target.file_ids` is this one file: a placement call is about one subject, and
    a target naming more would authorise a release about files the judge was not
    asked about.
    """
    heading = _observation(
        db, key="k-head", zone="heading", value="PHYS1401",
        span=TextSpan(start=0, end=8), unit_text="PHYS1401 Lecture 8")
    build = model_path_injections(
        db, _authorities(prompt=_prompt()), plan_version=PLAN)["model_call_request"]

    request = build(
        subject_ref=f"file:{FILE}",
        evidence_items=(EvidenceItem(
            evidence_ref=heading, kind="fact", location="heading",
            excerpt_span=(0, 8), reliability_state="direct",
            basis="direct-anchor"),),
        max_dossier_tokens=1024)

    assert request.stage == PLACEMENT_STAGE
    assert request.target.file_ids == (FILE,)
    assert request.target.group_id is None
    assert [item.observation_key
            for item in request.requested_items] == [heading]


def _prompt():
    """A prompt-shaped stand-in. NOT prompt text, and never sent anywhere.

    `PromptDefinition` is what the composition root builds from ratified bytes.
    These tests need an object that is not `None`; they assert nothing about what
    it says, because there is nothing ratified for it to say.
    """
    from llm_harness.fingerprint import prompt_fingerprint
    from llm_harness.records import PromptDefinition

    definition = PromptDefinition(
        template_id="fixture.not-ratified", template_bytes=b"fixture",
        response_schema_bytes=b"{}", call_site="C_placement",
        call_site_version="1", shaping_policy_bytes=b"{}")
    prompt_fingerprint(definition)
    return definition


def test_a_superseded_reading_is_never_offered_to_a_placement_model(db):
    """A later extraction retracted this reading, and a retracted value is not evidence.

    `observations_by_key` returns EVERY row for a key on purpose -- §8.5's
    cross-version diff needs both -- and `Observation` carries no supersede state
    of its own, so nothing about the record itself says it was retracted. A caller
    that took the newest row by insertion order would offer the superseded one
    whenever the replacement was written first. `cli._stored_value_of` filters
    `superseded_by IS NULL` at the resolving end of the same seam; this is the
    releasing end.
    """
    from evidence_shape.store import supersede_observation

    old = _observation(db, key="k-old", zone="heading", value="PHYS1401",
                       span=TextSpan(start=0, end=8),
                       unit_text="PHYS1401 Lecture 8")
    old_id = db.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?",
        (old,)).fetchone()["observation_id"]
    new = _observation(db, key="k-new", zone="heading", value="PHYS1402",
                       span=TextSpan(start=0, end=8),
                       unit_text="PHYS1402 Lecture 9")
    new_id = db.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?",
        (new,)).fetchone()["observation_id"]
    supersede_observation(db, old_observation_id=old_id,
                          new_observation_id=new_id,
                          reason="a later extraction read the course code again")

    assert releasable_excerpts(db, evidence_refs=(old,)) == ()
    assert [item.observation_key
            for item in releasable_excerpts(db, evidence_refs=(new,))] == [new]


def test_a_value_p5_signalled_sensitive_is_never_offered_to_a_placement_model(db):
    """P5's per-value signal, which is the only one in the product, read at site C.

    `privacy.items.sensitive_observation_keys` is "the only per-value sensitivity
    signal in the product" by its own docstring, and P7 owns no detector of its
    own. `model_facts.releasable_observations` reads it at site A and refuses the
    WHOLE request over one signalled observation. Site C had no such check until
    this test: a card number P5 flagged inside an otherwise ordinary body zone
    would have gone into a placement dossier, because the zone rule cannot see it
    and the whole-unit rule cannot see it either.

    The gate refuses it too, with `ProtectedItemRequested`. Reading it here means
    the request is never BUILT — the same argument the zone exclusions rest on.
    """
    from extractors.long_tail import (
        POTENTIALLY_SENSITIVE, SensitivitySignal, record_sensitivity_signals,
    )

    flagged = _observation(db, key="k-card", zone="body", value="4111 1111 1111 1111",
                           span=TextSpan(start=6, end=25),
                           unit_text="Card: 4111 1111 1111 1111, expires soon")
    ordinary = _observation(db, key="k-head", zone="heading", value="PHYS1401",
                            span=TextSpan(start=0, end=8),
                            unit_text="PHYS1401 Lecture 8")
    keys = [row["observation_key"] for row in db.execute(
        "SELECT observation_key FROM evidence ORDER BY rowid")]
    record_sensitivity_signals(
        db, run_id=RUN,
        signals=(SensitivitySignal(observation_index=keys.index(flagged),
                                   signal=POTENTIALLY_SENSITIVE,
                                   basis="fixture: a card number"),),
        observation_keys=keys, now=T0)

    offered = releasable_excerpts(db, evidence_refs=(flagged, ordinary))

    assert [item.observation_key for item in offered] == [ordinary]
