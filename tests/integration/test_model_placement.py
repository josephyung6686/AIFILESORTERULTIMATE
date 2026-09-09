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

# ALIASED: this module already binds `FILE` to a file-id fixture at line 51,
# and P11's subject kind is a different thing wearing the same word.
from placement.vocabulary import FILE as SUBJECT_FILE
from placement.vocabulary import GROUP as SUBJECT_GROUP

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
from privacy.vocabulary import (
    ALWAYS_LOCAL_ZONES, ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET, CLOUD_LOCALITY,
    RELEASED_TO_EVERY_TARGET,
)

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
        gate=object(), model_client=object(), prompt=None, residual_prompt=None,
        model_target=TARGET,
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
    """`model_path_available()` reads seven of the nine as a SET, and this respects it.

    Its own docstring says what a half-injection costs: the missing piece is
    discovered "after a dossier has been assembled". So a deployment with no
    prompt supplies no gate, no client and no dependencies either -- the file
    abstains with a reason, which is what it does today, and nothing is built.

    `residual_prompt` is the ninth and joins the same all-or-nothing set: it is
    site D's OWN text, and until it existed `_judge_with_model` sent site C's for
    both -- a residual answer naming one of §7.7's eight actions, judged against a
    schema with no `action` key in it.

    `model_target` is the tenth (`104` R-118): §8.4's gate reads the target's
    locality BEFORE a dossier exists, and a target handed over without the rest
    would be the half-injection this set exists to refuse.

    `usage_recorder` is the eleventh (`104` R-145): `104` R-14's mailbox, which
    site C's `run_call` never received, so its responses wrote no usage row.

    `route_for` is the twelfth (`104` §17.13 ruling 3): the target is chosen per
    FILE now -- cloud where the cloud gate permits the file, local where it does
    not -- and a route handed over without the rest would be the same
    half-injection. It is `None` in a deployment whose destination is the single
    pair, which is why it is the SET that is asserted and not its emptiness.
    """
    injections = model_path_injections(db, _authorities(), plan_version=PLAN)

    assert set(injections) == {
        "gate", "model_client", "prompt", "residual_prompt", "call_dependencies",
        "model_call_request", "chosen_node_of", "residual_action_of",
        "sensitivity_policy", "model_target", "route_for", "usage_recorder",
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


def test_the_always_local_zones_are_offered_exactly_as_the_partition_says(db):
    """The whole point of asking this question at Site C rather than inheriting it.

    Placement is about where a file belongs, so the observations that most
    obviously bear on it are the ones naming where it already IS -- and `path`
    and `filename` are the zones §8.4's always-local members 1 and 6 have a route
    out through. The filesystem extractor writes one observation per file whose
    raw value is the parent directory.

    **`104` §17.13 (9 Sep 2026) SPLIT THE ANSWER, so this test asserts the split.**
    It read: no always-local zone is ever offered to a placement model. The owner
    ruled `path` and `ocr` shown to either model within the ceiling -- on the measured
    corpus the folder path was where 20 of 43 labelled coursework files kept their
    course code, at the one site that is ABOUT where a file belongs -- and left
    `filename` behind, because §7.7's name has its own door in `items.Filename` under
    `allow_unratified`, where §7.3's protected-records ban also applies.

    **Iterated over the vocabulary rather than over a list written here**, and
    `d005418` is why: `ocr` was added to `ALWAYS_LOCAL_ZONES` on 2026-09-04 as member
    3 (text Apple Vision read off a scanned identity card), and the comment beside the
    set says the mapping from the nine kinds of DATA to the fifteen zones is made BY
    HAND, one member at a time. A test naming its own zones would have gone on passing
    while the placement path offered OCR text, which is the shape of the defect that
    commit fixed. Since §17.13 that iteration has to walk BOTH halves, so the two
    published sets are read and their union is asserted to be the whole -- which is
    how member 4 still reaches this test on the day someone maps it, whichever side of
    the ruling it is put on.
    """
    always_local = {
        zone: _observation(db, key=f"k-{zone}", zone=zone,
                           value=f"a value read from the {zone} zone",
                           span=None, unit_text=None)
        for zone in sorted(ALWAYS_LOCAL_ZONES)
    }
    assert always_local, "ALWAYS_LOCAL_ZONES is empty; this test proves nothing"
    assert (RELEASED_TO_EVERY_TARGET | ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET
            == ALWAYS_LOCAL_ZONES), (
        "a fourth always-local zone was added without a §17.13 decision, and this "
        "test would then be silent about it")
    heading = _observation(
        db, key="k-head", zone="heading", value="PHYS1401",
        span=TextSpan(start=0, end=8),
        unit_text="PHYS1401 Lecture 8 — Rotational dynamics")

    offered = releasable_excerpts(
        db, evidence_refs=(*always_local.values(), heading), locality=CLOUD_LOCALITY)

    keys = {item.observation_key for item in offered}
    assert keys == {heading} | {always_local[zone]
                                for zone in RELEASED_TO_EVERY_TARGET}
    for zone in ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET:
        assert always_local[zone] not in keys, zone


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

    offered = releasable_excerpts(db, evidence_refs=(heading,), locality=CLOUD_LOCALITY)

    assert len(offered) == 1
    assert offered[0].span == TextSpan(start=17, end=25)


def test_an_observation_covering_its_whole_unit_is_offered_and_the_ceiling_refuses(
        db):
    """§8.4's own sentence, and `104` §17.13 moved which word carries it.

    It read: "should not send full documents where a short heading or OCR excerpt is
    enough", refused HERE rather than at the door, because the gate refuses AFTER the
    text has been materialised and the release minted -- so leaving it to the door
    means paying to build a document in order to say no to it.

    §17.13 ruled a whole text unit shown to either model WITHIN THE CEILING, so
    covering a unit is no longer what makes a reading a document. Being longer than
    P1's stored ceiling is, and `releasable_excerpts` reads no ceiling: it is the
    zone-and-signal door, and the length is spent by the fill and refused by
    `items.check_item`.

    So the test follows its sentence to where the sentence now lives. The same
    Excerpt this door hands back is refused by `check_item` under a ceiling one
    character short of the unit and admitted under one that fits, both read off the
    document rather than typed beside it.

    THE UNIT KEEPS ITS LINE BREAKS AND THE REASON HAS EXPIRED. `104` R-152 gave them:
    the unit was `"the whole thing"`, fifteen characters on one line, and a unit
    holding no line break became a LINE and was released. Every unit is released now
    and the distinction decides nothing here.
    """
    from privacy.items import WholeDocumentRequested, check_item

    document = "the whole thing\nand a second line of it\nand a third"
    whole = _observation(
        db, key="k-all", zone="body", value=document,
        span=TextSpan(start=0, end=len(document)), unit_text=document)

    excerpt, = releasable_excerpts(db, evidence_refs=(whole,),
                                   locality=CLOUD_LOCALITY)
    assert excerpt.observation_key == whole

    def at_ceiling(ceiling):
        return check_item(
            excerpt, unit_length=len(document), zone="body", protected=False,
            sensitive_keys=frozenset(), allow_unratified=True,
            suspension_permits_self_description=False, locality=CLOUD_LOCALITY,
            ceiling=ceiling)

    with pytest.raises(WholeDocumentRequested) as caught:
        at_ceiling(len(document) - 1)
    assert "full documents" in str(caught.value)
    assert at_ceiling(len(document)) is None


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

    assert releasable_excerpts(db, evidence_refs=(old,), locality=CLOUD_LOCALITY) == ()
    assert [item.observation_key
            for item in releasable_excerpts(db, evidence_refs=(new,), locality=CLOUD_LOCALITY)] == [new]


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

    offered = releasable_excerpts(db, evidence_refs=(flagged, ordinary), locality=CLOUD_LOCALITY)

    assert [item.observation_key for item in offered] == [ordinary]


# --- `104` R-58: the file address has three parts ----------------------------

def test_a_file_address_comes_back_as_the_file_id_and_not_the_id_plus_its_hash():
    """`placement.store.subject_ref_of` writes `file:<file_id>:<content_hash>`.

    `_file_id_of` partitioned on the first colon and returned everything after
    it, so every file address came back as `<file_id>:<content_hash>` -- a string
    that matches no row in `files`. Dead while nothing called it and wrong the
    moment site C is wired, which is the wave that wires it.
    """
    from model_placement import _file_id_of
    from placement.store import subject_ref_of

    class _Subject:
        kind = SUBJECT_FILE
        file_id = "9ee1dc75-2f17-40e0-8869-34d3c1a49ac5"
        content_hash = "a" * 64
        group_id = None

    address = subject_ref_of(_Subject())

    assert address.count(":") == 2, address
    assert _file_id_of(address) == _Subject.file_id


def test_a_file_id_that_contains_a_colon_survives_the_trim():
    """The old docstring's reason for refusing a right-hand split, kept and
    answered rather than dropped: P11 promises nothing about a file id's shape,
    so an id containing a colon must survive. The content hash cannot contain one
    -- it is sha256 hex -- so the LAST colon is the boundary between id and hash
    however many the id has."""
    from model_placement import _file_id_of

    assert _file_id_of(f"{SUBJECT_FILE}:has:colons:in:id:{'b' * 64}") == "has:colons:in:id"


def test_a_group_address_is_untouched_because_it_carries_no_hash():
    """`subject_ref_of` writes two parts for a group and three for a file, and
    the same function reads both. Trimming a hash off a group address would take
    the group id with it."""
    from model_placement import _file_id_of

    assert _file_id_of(f"{SUBJECT_GROUP}:group-1") == "group-1"


def test_a_malformed_address_is_returned_whole_rather_than_repaired():
    """A caller looking up half an address gets no row; inventing the missing
    half would get it the WRONG row. `84` §1's absent-means-refuse, at the one
    place where a plausible repair is available and is worse than none."""
    from model_placement import _file_id_of

    assert _file_id_of(f"{SUBJECT_FILE}:no-hash-here") == "no-hash-here"
    assert _file_id_of("no-colons-at-all") == "no-colons-at-all"


# --- `104` R-15, CLOSED: the value is grounded, the destination is looked up ----
#
# This was a strict xfail against the defect: `_invented_dimension` compared a
# level's VALUE against `dossier.allowed_vocabulary`, which P11 fills with the
# legal NODE IDS, so a real institution was "invented". The xfail's own reason
# named the fix -- "check the value against the evidence it cites, and the
# node-id set stays the check for `destination` alone" -- and that is what
# landed, so both halves are asserted green here instead.


def _grounded_in(*values: str):
    """A site-C dossier whose file states `values`, built from P8's own record."""
    from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
    from llm_harness.vocabulary import C_PLACEMENT

    return Dossier(
        dossier_id="ds-r15", call_site=C_PLACEMENT, subject_ref="file:f1:h1",
        eligibility_reason="several_legal_nodes_plausible", plan_version="plan-1",
        policy_version="policy-1",
        allowed_vocabulary=("node_f1d70c8a_1", "node_f1d70c8a_2"),
        evidence_items=(EvidenceItem(
            evidence_ref="obs-1", kind="excerpt", location="body",
            excerpt_span=(0, 8), reliability_state="direct",
            basis="direct-anchor"),),
        conflicts=(),
        released_evidence=tuple(
            ReleasedEvidence(observation_key="obs-1", address="body:1",
                             value=value, zone="body")
            for value in values),
        max_dossier_tokens=4000, reduction_rung="none", release_id="rel-1")


def test_a_real_institution_the_file_states_is_not_an_invented_one():
    """The correct answer site C will actually give: a real institution, in the
    file's own released text."""
    from llm_harness.placement_validation import _invented_dimension

    payload = {"per_dimension_support": [
        {"dimension": "institution", "value": "Columbia University",
         "support": "direct"}]}

    assert _invented_dimension(
        payload, _grounded_in("Submitted to Columbia University")) is None


def test_an_institution_the_file_never_states_is_still_invented():
    """The control: grounding is a check and not a rubber stamp."""
    from llm_harness.placement_validation import _invented_dimension
    from llm_harness.vocabulary import INVENTED_INSTITUTION

    payload = {"per_dimension_support": [
        {"dimension": "institution", "value": "Columbia University",
         "support": "direct"}]}

    assert _invented_dimension(
        payload, _grounded_in("a page about nothing in particular")
    ) == INVENTED_INSTITUTION


def test_a_node_id_is_no_longer_what_a_value_is_measured_against():
    """The defect itself, asserted gone. A legal node id in a VALUE slot says
    nothing about what the file states, and used to be the only thing that
    passed."""
    from llm_harness.placement_validation import _invented_dimension
    from llm_harness.vocabulary import INVENTED_INSTITUTION

    payload = {"per_dimension_support": [
        {"dimension": "institution", "value": "node_f1d70c8a_1",
         "support": "direct"}]}

    assert _invented_dimension(
        payload, _grounded_in("Submitted to Columbia University")
    ) == INVENTED_INSTITUTION


def test_the_same_check_is_right_about_a_destination_and_that_half_stays():
    """The half of R-15 that was NOT broken. A destination outside the frozen
    tree IS invented and the node-id set is exactly the right vocabulary for
    that question -- which is the question the check was written for before it
    was pointed at values too. The two questions are now asked in two places:
    the destination against `allowed_vocabulary` and the tree, in
    `_placement_site`; the values against the evidence, here. So a bogus
    destination is not this function's finding, and its own reason code is what
    reports it (pinned end to end in `tests/p8/test_p8_placement_validation.py::
    test_r15_a_destination_outside_the_frozen_tree_is_still_rejected`)."""
    from llm_harness.placement_validation import _invented_dimension

    payload = {"destination": "node-hallucinated",
               "per_dimension_support": [
                   {"dimension": "institution", "value": "Columbia University",
                    "support": "direct"}]}

    assert _invented_dimension(
        payload, _grounded_in("Submitted to Columbia University")) is None


# --- `104` R-149: the request that cannot be formed --------------------------


def _placement_prompt():
    """Site C's real `PromptDefinition`. The builder binds the request to the
    prompt's own fingerprint, so a stand-in stops it before the item set is ever
    the question -- and the item set is the question here."""
    from llm_harness.records import PromptDefinition
    from llm_harness.vocabulary import C_PLACEMENT

    return PromptDefinition(
        template_id="template.placement", template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}', call_site=C_PLACEMENT,
        call_site_version="1", shaping_policy_bytes=b'{"policy":"authored"}')


def _placement_builder(db):
    """The live builder, wired the way `cli.placement_inputs` wires it."""
    return model_path_injections(
        db, _authorities(prompt=_placement_prompt()),
        plan_version=PLAN)["model_call_request"]


def _item(ref: str, *, location: str, span):
    from llm_harness.records import EvidenceItem

    return EvidenceItem(evidence_ref=ref, kind="fact", location=location,
                        excerpt_span=span, reliability_state="direct",
                        basis="direct-anchor")


def test_a_file_whose_only_cited_reading_is_its_filename_forms_no_request(db):
    """`104` R-149's state, through the live seam and with nothing stubbed.

    The two exclusions meet here. `releasable_excerpts` drops an always-local
    reading -- that is the test above, and it is the one that matters most at
    this site -- and `ModelCallRequest.__post_init__` then refuses what is left:
    *"a request with no items has nothing to release"*. So a file whose whole
    citation set is its own name reaches P11's builder and no request comes back.

    Measured on the six-file stub corpus of
    `tests/integration/test_local_model_fact_pass.py` before `104` R-148:
    one file, one fact, a filename-only citation. `placement.pipeline` used to
    catch this raise into the deterministic fallback and record it in neither
    ledger; `tests/p11/test_p11_pipeline.py` pins the abstention it writes now.

    R-148 does not close the state. It offers a factless file its own releasable
    readings, and a file with NO body reading at all -- every reading it has in
    an always-local zone, which is what this fixture builds -- still arrives
    with nothing to send.
    """
    from privacy.release import MalformedRequest

    name = _observation(db, key="k-name", zone="filename",
                        value="Columbia Essay.txt", span=None, unit_text=None)
    assert releasable_excerpts(db, evidence_refs=(name,), locality=CLOUD_LOCALITY) == ()

    build = _placement_builder(db)
    with pytest.raises(MalformedRequest):
        build(subject_ref=f"{SUBJECT_FILE}:{FILE}:{HASH}",
              evidence_items=(_item(name, location="filename", span=None),),
              max_dossier_tokens=4000)


def test_the_same_file_with_one_body_reading_does_form_a_request(db):
    """The twin that says the refusal is about the item set and not the file.

    One releasable reading beside the filename is a request, and it carries the
    reading and not the name -- so the abstention above is what an EMPTY offer
    means, never a file P11 declined to ask about.
    """
    name = _observation(db, key="k-name-2", zone="filename",
                        value="Columbia Essay.txt", span=None, unit_text=None)
    body = _observation(db, key="k-body", zone="heading", value="PHYS1401",
                        span=TextSpan(start=0, end=8),
                        unit_text="PHYS1401 Lecture 8 — Rotational dynamics")

    request = _placement_builder(db)(
        subject_ref=f"{SUBJECT_FILE}:{FILE}:{HASH}",
        evidence_items=(_item(name, location="filename", span=None),
                        _item(body, location="heading", span=(0, 8))),
        max_dossier_tokens=4000)

    assert [item.observation_key for item in request.requested_items] == [body]
