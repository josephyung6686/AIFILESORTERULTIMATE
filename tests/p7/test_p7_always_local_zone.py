# tests/p7/test_p7_always_local_zone.py
"""CR-01: an excerpt that addresses a `path` or `filename` zone is always-local.

`00` §8.4's always-local list opens with the word "Paths". `extractors/filesystem.py`
writes one observation per scanned file whose `zone` is `"path"` and whose `raw_value`
is the parent directory of the file -- `/Users/<name>/Documents/Legal/Divorce`. That
observation carries no `text_span`, because the run's one text unit is the filename.

Before this file, an `Excerpt` naming that observation was RELEASED whole. Three
correct-looking comments left a hole between them:

  * `resolve.materialise` returns `raw_value` entire with `unit_length=None` for a
    span-less observation, and its docstring is right -- §2.3's spreadsheet cell and
    §2.8's EXIF field have no unit for a span to cover.
  * `items.is_whole_document` returns False when `unit_length is None`, and ITS
    docstring is right -- reading the absent length as zero would make every cell a
    whole document.
  * `check_item` never read `zone` at all, and nothing else does either. So the
    always-local kind that §8.4 names FIRST had no check anywhere on the ordinary
    release path.

The refusal is in `_precheck_items`, not the postcheck, and the zone comes from the
LOCATOR (`resolve.current_location`, which selects no content). That placement is the
point: `release.DECISION_ORDER` says nothing materialises until every check that could
deny has run, and a path refused after materialisation is a path the gate read first.
It also keeps `denial.DECIDABLE_FROM_REQUEST`'s claim about `always_local_item` true.

The two controls below are the reason this is a zone check and not a flip of
`is_whole_document`: a span-less `metadata`-zone field and a span-less `title`-zone
field are BOUNDED VALUES, not documents, and both must still be released.
"""
from __future__ import annotations

import hashlib
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.vocabulary import ZONES
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)
from extractors.schema import create_extraction_schema
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.gate import Gate
from privacy.items import (
    CandidateLabel, EvidenceReference, Excerpt, RedactedIdentifier,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target
from privacy.resolve import UnresolvableSpan
from privacy.schema import create_privacy_schema
from privacy.vocabulary import ALWAYS_LOCAL, ALWAYS_LOCAL_ZONES

OBSERVED_AT = "2026-09-02T09:00:00Z"
PLAN_VERSION = "plan-zone-1"
COMPONENT = "0.1.0"
CLOUD = ModelTarget(locality="cloud", model_id="a-model", provider="Acme")
#: P7's own ceiling echo. A number only a test may choose.
MAX_DOSSIER_TOKENS = 4000

#: The directory the reviewer's probe carried onto the wire, in the shape
#: `extractors/filesystem.py` writes it: the parent folder of a scanned file.
PRIVATE_DIRECTORY = "/Users/joseph/Documents/Legal/Divorce"
#: What a span-less non-path observation looks like: §2.8's EXIF-style metadata field
#: and a document title. Bounded values, and they must keep being released.
A_TITLE = "Spring Term Syllabus"


@pytest.fixture()
def zone_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_privacy_schema(conn)
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


def _span_less_observation(conn, file_id: str, content_hash: str, *,
                           zone: str, raw_value: str) -> str:
    """One observation with NO text span, exactly as `filesystem.py:83-89` writes it.

    `record_text_unit` is deliberately not called: the whole point of this shape is
    that there is no unit for a span to cover, which is what made `unit_length` None
    and `is_whole_document` False.
    """
    digest = hashlib.sha256(f"{content_hash}:{zone}".encode()).hexdigest()
    run_id = new_id()
    container = (Segment(kind="field", label=zone),)
    location = Location(zone=zone, container_path=container, text_span=None)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name="filesystem", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1,
    ))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name="filesystem",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=raw_value, location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id=run_id,
        context_before=None, context_after=None, context_truncated=False,
    ))
    return observation_key(
        content_hash=digest, extractor_name="filesystem",
        locator=serialize_locator(location), raw_value=raw_value,
    )


def _store_policy(conn) -> Policy:
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(("area-1", "cloud_model"),),
        redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION,
        set_at=OBSERVED_AT,
    )
    version = set_policy(
        conn, draft, component_version=COMPONENT, user_id="joseph",
        reason="always-local zone test",
    )
    return replace(draft, policy_version=version)


def _classify(conn, file_id: str, content_hash: str, *, key: str) -> None:
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class="public_low",
        protected=False, basis="detector", evidence_refs=(key,),
        reliability_state="direct", observed_at=OBSERVED_AT,
    ))


def _gate(conn) -> Gate:
    return Gate(
        conn,
        store=ClassificationStore(conn),
        plan_version=PLAN_VERSION,
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: (),
        component_version=COMPONENT,
        now=lambda: OBSERVED_AT,
        user_id="joseph",
    )


def _request(*, items, file_id: str) -> ModelCallRequest:
    return ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=CLOUD, requested_items=tuple(items),
        prompt_template_id="template.under-ratification",
        prompt_fingerprint="fingerprint-zone-1",
        max_dossier_tokens=MAX_DOSSIER_TOKENS,
    )


def _seed(conn, *, zone: str, raw_value: str) -> tuple[str, str]:
    content_hash = f"hash-{zone}"
    file_id = _file(conn, f"{zone}-fixture.pdf", content_hash)
    key = _span_less_observation(
        conn, file_id, content_hash, zone=zone, raw_value=raw_value)
    _classify(conn, file_id, content_hash, key=key)
    _store_policy(conn)
    return file_id, key


# ================================================================================
# The vocabulary: a mapping onto the existing nine, never a tenth member
# ================================================================================

def test_the_zone_set_maps_onto_always_local_and_adds_no_member():
    """`80` §2's "NO TENTH MEMBER IS ADDED" is unaffected: `ALWAYS_LOCAL` stays at
    nine, and `ALWAYS_LOCAL_ZONES` names the two document zones through which the
    first of those nine, and §7.7's flagged sixth releasable kind, have a route out.
    """
    assert len(ALWAYS_LOCAL) == 9
    assert ALWAYS_LOCAL[0] == "paths"
    assert ALWAYS_LOCAL_ZONES == frozenset({"path", "filename"})
    assert not ALWAYS_LOCAL_ZONES & set(ALWAYS_LOCAL)


# ================================================================================
# The defect: the ordinary release path, on the zone §8.4 names first
# ================================================================================

def test_a_span_less_path_zone_excerpt_is_denied_and_the_path_never_appears(zone_conn):
    """CR-01, reproduced and closed.

    SABOTAGE: delete the `zone in ALWAYS_LOCAL_ZONES` branch from
    `privacy/items.check_item` and this test goes red on `isinstance(decision,
    Denied)` -- the run in which `/Users/joseph/Documents/Legal/Divorce` is the
    `value` of a `released_evidence` entry in the bytes a cloud model is shown.
    """
    file_id, key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    decision = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="path"),),
        file_id=file_id))

    assert isinstance(decision, Denied), (
        f"a path-zone excerpt was {type(decision).__name__}; §8.4's always-local "
        f"list opens with the word 'Paths'")
    assert decision.reason == "always_local_item"
    assert PRIVATE_DIRECTORY not in decision.explanation, (
        "the refusal must not quote the value it refused to release")


def test_the_denial_names_the_zone_and_the_section_that_forbids_it(zone_conn):
    file_id, key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    decision = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="path"),),
        file_id=file_id))
    assert "path" in decision.explanation
    assert "8.4" in decision.explanation
    assert decision.remedy_options, "§8.6: a denial is never a dead end"


def test_a_redacted_identifier_is_not_a_way_round_the_zone(zone_conn):
    """The sensitive-key refusal names `RedactedIdentifier` as the legitimate second
    route for the same key. A zone has no such route: redacting a directory leaves a
    directory, and §8.4 puts the whole kind local rather than a value inside it.
    """
    file_id, key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    decision = _gate(zone_conn).release(_request(
        items=(RedactedIdentifier(
            observation_key=key, span=None, identifier_class="path"),),
        file_id=file_id))
    assert isinstance(decision, Denied)
    assert decision.reason == "always_local_item"


def test_a_span_less_filename_zone_excerpt_is_denied_too(zone_conn):
    """`filesystem.py:144`'s `unrouted_result` writes exactly this shape.

    Released as an `Excerpt` it would publish a whole filename while bypassing BOTH
    of the checks the design put on filenames: `Filename`'s `allow_unratified` opt-in
    and §7.3's protected-records ban, neither of which `check_item` applies to an
    excerpt. The reviewer inferred this case from the path case; it is run here.
    """
    file_id, key = _seed(zone_conn, zone="filename", raw_value="Divorce Petition.pdf")
    decision = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="filename"),),
        file_id=file_id))
    assert isinstance(decision, Denied)
    assert decision.reason == "always_local_item"


def test_nothing_was_materialised_before_the_refusal(zone_conn):
    """The refusal is a LOCATOR fact, so it lands in `_precheck_items`.

    `resolve.current_location` selects `observation_id, observation_key, file_id,
    location, superseded_by` and no content column; `materialise` is what reads
    `raw_value`. Proving the order matters because `DECISION_ORDER` is explicit that
    a gate which resolved first would hold the text in memory before deciding it was
    allowed to -- and a path is the one value where holding it IS the harm.

    SABOTAGE: move the branch from `_precheck_items` into `_postcheck_items` and this
    test goes red while the four above stay green.
    """
    file_id, key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    read: list[str] = []
    gate = _gate(zone_conn)

    from privacy import gate as gate_module

    original = gate_module.materialise

    def watched(conn, item):
        read.append(item.observation_key)
        return original(conn, item)

    gate_module.materialise = watched
    try:
        decision = gate.release(_request(
            items=(Excerpt(observation_key=key, span=None, reason="path"),),
            file_id=file_id))
    finally:
        gate_module.materialise = original

    assert isinstance(decision, Denied)
    assert read == [], (
        "the gate resolved the path's raw_value before refusing to release it")


def test_a_reference_to_a_path_observation_is_refused_too(zone_conn):
    """BROADER THAN THE FINDING, and recorded at the branch in `check_item`.

    `Gate._precheck_items` reads the zone for every item carrying an
    `observation_key`, so an `EvidenceReference` -- which §4 calls "an id only, no
    content" -- is refused as well. It blocks no demonstrated leak: the id leaves
    keyed. It is kept because "an excerpt may not address a path, a reference may"
    is a rule needing its own justification and §8.4's sentence gives none. The rule
    is about the ZONE, so it holds whoever asks.

    SABOTAGE: scope `_located_zone` to `TEXT_BEARING` and this goes red alone.
    """
    file_id, key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    decision = _gate(zone_conn).release(_request(
        items=(EvidenceReference(observation_key=key),), file_id=file_id))
    assert isinstance(decision, Denied)
    assert decision.reason == "always_local_item"


def test_a_reference_to_an_ordinary_zone_is_untouched(zone_conn):
    """The refusal is about the zone and not about the kind. Without this the test
    above is also satisfied by a gate that refuses every reference."""
    file_id, key = _seed(zone_conn, zone="body", raw_value="a bounded value")
    decision = _gate(zone_conn).release(_request(
        items=(EvidenceReference(observation_key=key),), file_id=file_id))
    assert isinstance(decision, Released)


def test_a_candidate_label_addresses_no_observation_and_is_unaffected(zone_conn):
    """§4 already draws this line: a label "carries no observation and no value, so
    a label reading 'GPS' releases the word and nothing else." It has no
    `observation_key`, so `_located_zone` returns None and the branch never runs."""
    file_id, _key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    decision = _gate(zone_conn).release(_request(
        items=(CandidateLabel(label="Legal"),), file_id=file_id))
    assert isinstance(decision, Released)


# ================================================================================
# What an absent zone means, run rather than reasoned about
# ================================================================================

def test_a_key_that_does_not_resolve_releases_nothing(zone_conn):
    """`_located_zone` returns `None` for a key it cannot resolve, and `None` skips
    the zone refusal. That is safe, and this is the test that says so with a run
    instead of an argument.

    The refusal is DEFERRED, never waived: the same key is unreadable to
    `resolve.materialise`, which raises at step 3 before any value exists. So the
    item cannot be released, and `None` never becomes "not always-local".

    It stays an exception rather than becoming `Denied always_local_item` because
    `test_p7_release.test_a_resolve_failure_propagates_and_is_not_a_denial` rules on
    it: a key the evidence does not carry is a contract violation by the CALLER, and
    answering a typo with a privacy verdict would be the wrong kind of true.
    """
    file_id, _key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    with pytest.raises(UnresolvableSpan):
        _gate(zone_conn).release(_request(
            items=(Excerpt(observation_key="sha256:no-such-key", span=None,
                           reason="path"),),
            file_id=file_id))


def test_every_stored_zone_is_one_of_p4s_fifteen(zone_conn):
    """Why there is no third case for `_located_zone` to be unsure about.

    `Location.__post_init__` runs `check(self.zone, ZONES)`, so "a locator with no
    zone" is not a state this product can store. The always-local set is a subset of
    what a locator can carry, which is what makes a zone check total.
    """
    with pytest.raises(Exception):
        Location(zone="", container_path=(), text_span=None)
    with pytest.raises(Exception):
        Location(zone="not-a-zone", container_path=(), text_span=None)
    assert ALWAYS_LOCAL_ZONES <= set(ZONES)


# ================================================================================
# The controls. A span-less value is not automatically a whole document.
# ================================================================================

@pytest.mark.parametrize("zone", ["metadata", "title"])
def test_a_span_less_bounded_field_is_still_released(zone_conn, zone):
    """This is why `is_whole_document` was NOT flipped to True on a missing length.

    §2.3's spreadsheet cell and §2.8's EXIF field are both span-less, and both are
    bounded values rather than documents. `test_live_path.py` asserts the span-less
    `title:field=Title` observation is Released and that assertion is correct.

    SABOTAGE: add `"title"` to `ALWAYS_LOCAL_ZONES`, or return True from
    `is_whole_document` when `unit_length is None`, and this goes red.
    """
    file_id, key = _seed(zone_conn, zone=zone, raw_value=A_TITLE)
    decision = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason=zone),),
        file_id=file_id))
    assert isinstance(decision, Released), (
        f"a span-less {zone} field is a bounded value, not a document")
    assert decision.materialised_items[0].value == A_TITLE
    assert decision.materialised_items[0].unit_length is None
