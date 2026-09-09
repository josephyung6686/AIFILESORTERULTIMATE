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

**SUPERSESSION, 9 Sep 2026, `104` §17.13 (the owner's ruling, applied on the owner's
word "for now its ok let it through").** The title line above is the rule this file
was written for and is kept as its history. The rule now is that `path` and `ocr` are
released to EVERY target within the dossier ceiling and `filename` alone is refused to
every target -- `vocabulary.RELEASED_TO_EVERY_TARGET` against
`ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET`. What CR-01 built is untouched: the zone is
still read off the LOCATOR in `_precheck_items` before anything is materialised, and a
zone in the refused set is still answered there. What changed is the MEMBERSHIP of
that set, from three zones to one. Every test the ruling moved carries its own dated
paragraph saying what it asserted before and why it asserts the opposite now; none of
them was deleted, and the tests below that were re-addressed from `path` to `filename`
assert exactly what they always did, at the zone where there is still a refusal to
assert it about.
"""
from __future__ import annotations

import hashlib
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.vocabulary import ZONES
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from extractors.filesystem import METADATA_SLOTS
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
from privacy.resolve import UnresolvableSpan, materialise
from privacy.schema import create_privacy_schema
from privacy.vocabulary import (
    ALWAYS_LOCAL, ALWAYS_LOCAL_ZONES, ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET,
    RELEASED_TO_EVERY_TARGET,
)

OBSERVED_AT = "2026-09-02T09:00:00Z"
PLAN_VERSION = "plan-zone-1"
COMPONENT = "0.1.0"
CLOUD = ModelTarget(locality="cloud", model_id="a-model", provider="Acme")
#: `104` R-159's other destination. Every test in this file predates the ruling and
#: is about `CLOUD`; the pairs at the bottom are what the ruling changed, and they
#: are written as PAIRS -- the same fixture, the same request, one field different --
#: because "the rule now depends on the target" is a claim about a difference and a
#: test of the local half alone would not make it.
LOCAL = ModelTarget(locality="local", model_id="a-model", provider="ollama")
#: P7's own ceiling echo. A number only a test may choose.
MAX_DOSSIER_TOKENS = 4000
#: P1's stored ceiling, which is the one `Gate._stored_ceiling` reads and the only
#: one `check_item`'s whole-document arm may be asked about (`104` §17.13, M9: the
#: request's `max_dossier_tokens` is "the caller's echo of it").
CEILING_KEY = "model.max_dossier_tokens_per_call"


class _Item:
    """A key and a span, which is all `resolve.materialise` reads off an item."""

    def __init__(self, observation_key: str, span) -> None:
        self.observation_key = observation_key
        self.span = span

#: The directory the reviewer's probe carried onto the wire, in the shape
#: `extractors/filesystem.py` writes it: the parent folder of a scanned file.
CARD_NUMBER = "K123456(7)"
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


def _request(*, items, file_id: str,
             model_target: ModelTarget = CLOUD) -> ModelCallRequest:
    return ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=model_target, requested_items=tuple(items),
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
    assert ALWAYS_LOCAL_ZONES >= frozenset({"path", "filename"})
    assert not ALWAYS_LOCAL_ZONES & set(ALWAYS_LOCAL)


# ================================================================================
# The defect: the ordinary release path, on the zone §8.4 names first
# ================================================================================

def test_a_span_less_path_zone_excerpt_now_puts_the_directory_on_the_cloud_wire(
        zone_conn):
    """CR-01's own reproduction, re-argued to the opposite answer by `104` §17.13.

    **THIS TEST ASSERTED `Denied` UNTIL 9 Sep 2026**, and the sentence it asserted it
    with is the one worth reading first: the sabotage it named was "the run in which
    `/Users/joseph/Documents/Legal/Divorce` is the `value` of a `released_evidence`
    entry in the bytes a cloud model is shown". That run is now the ruling. Asked
    §17.6's question with the code's answer in front of them -- the cloud is shown
    zero characters, and half the corpus is refused to it -- the owner extended item
    14 to the cloud target: a cloud model may be shown a whole text unit, the person's
    folder path and OCR text, within the same ceiling, for every file the cloud gate
    permits.

    So what is asserted here is the released VALUE and not the verdict, deliberately.
    The directory CR-01 kept off the wire is named in this test, on a CLOUD target, so
    that this file cannot be read as having applied the ruling without showing what
    the ruling releases. Which FILE may cross is decided elsewhere and per file
    (`cli.target_for` over `cli.model_route_permitted`, `104` R-170): a protected file
    and an unclassified file never reach this door with a cloud target.

    The mechanism CR-01 built is untouched and is still driven, one zone along.
    `test_a_span_less_filename_zone_excerpt_is_denied_too` runs this exact shape
    through the same locator pass and is still `Denied`, because `filename` is the one
    member of `ALWAYS_LOCAL_ZONES` the ruling does not release.
    """
    file_id, key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    decision = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="path"),),
        file_id=file_id))

    assert isinstance(decision, Released), (
        f"a path-zone excerpt bound for a cloud model was "
        f"{type(decision).__name__}; `104` §17.13 releases the person's folder path "
        f"to every target within the ceiling")
    assert [one.value for one in decision.materialised_items] == [PRIVATE_DIRECTORY], (
        "the cloud model is shown the folder itself, which is what the ruling is")


def test_the_denial_names_the_zone_and_the_section_that_forbids_it(zone_conn):
    """RE-ADDRESSED from `path` to `filename` by `104` §17.13, and the claim is
    unchanged by the move: a person reading the refusal is told WHICH zone was
    refused, WHICH section refuses it, and where to go instead.

    The zone the assertion names had to move because the path zone no longer produces
    a denial to read. Nothing about what is asserted moved with it -- `check_item`'s
    message names the zone, `deny_always_local_item` quotes §8.4's nine-name sentence
    whole, and §8.6 requires the remedy.
    """
    file_id, key = _seed(zone_conn, zone="filename",
                         raw_value="Divorce Petition.pdf")
    decision = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="filename"),),
        file_id=file_id))
    assert "filename" in decision.explanation
    assert "8.4" in decision.explanation
    assert decision.remedy_options, "§8.6: a denial is never a dead end"


def test_a_redacted_identifier_is_not_a_way_round_the_zone(zone_conn):
    """The sensitive-key refusal names `RedactedIdentifier` as the legitimate second
    route for the same key. A zone has no such route: §8.4 puts the whole kind local
    rather than a value inside it, and the refusal is on the ADDRESS, so a second item
    kind pointed at the same address is answered the same way.

    RE-ADDRESSED from `path` to `filename` by `104` §17.13, and the claim is stronger
    at the zone it moved to than at the one it left. `filename` has no redacted second
    route BY CONSTRUCTION rather than by argument: §7.7's name has exactly one door,
    `items.Filename`, where `allow_unratified` and §7.3's protected-records ban both
    apply, and a filename arriving as a redacted identifier would go round both while
    releasing nothing the `Filename` door does not already release.
    """
    file_id, key = _seed(zone_conn, zone="filename",
                         raw_value="Divorce Petition.pdf")
    decision = _gate(zone_conn).release(_request(
        items=(RedactedIdentifier(
            observation_key=key, span=None, identifier_class="filename"),),
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
    allowed to -- and a name a person gave a file is a value where holding it IS the
    harm, which is why `filename` keeps its own door.

    RE-ADDRESSED from `path` to `filename` by `104` §17.13. What is asserted is the
    ORDER and not the zone: the refusal must arrive before the value exists. The path
    zone no longer produces a refusal for the order to be asserted about, so the
    assertion moved to the zone that still does. The property is the same property.

    The stub takes `**kwargs` for a reason worth stating rather than working around.
    `Gate._materialise` passes `within_file_ids`, and a two-argument stub would raise
    `TypeError` on any path that actually reached materialisation -- which would fail
    this test for the wrong reason and hide the real one. It must fail on `read == []`
    with the sentence below it, or not at all.

    SABOTAGE: move the branch from `_precheck_items` into `_postcheck_items` and this
    test goes red while the ones above stay green.
    """
    file_id, key = _seed(zone_conn, zone="filename",
                         raw_value="Divorce Petition.pdf")
    read: list[str] = []
    gate = _gate(zone_conn)

    from privacy import gate as gate_module

    original = gate_module.materialise

    def watched(conn, item, **kwargs):
        read.append(item.observation_key)
        return original(conn, item, **kwargs)

    gate_module.materialise = watched
    try:
        decision = gate.release(_request(
            items=(Excerpt(observation_key=key, span=None, reason="filename"),),
            file_id=file_id))
    finally:
        gate_module.materialise = original

    assert isinstance(decision, Denied)
    assert read == [], (
        "the gate resolved the filename's raw_value before refusing to release it")


def test_a_reference_to_a_refused_zones_observation_is_refused_too(zone_conn):
    """BROADER THAN THE FINDING, and recorded at the branch in `check_item`.

    `Gate._precheck_items` reads the zone for every item carrying an
    `observation_key`, so an `EvidenceReference` -- which §4 calls "an id only, no
    content" -- is refused as well. It blocks no demonstrated leak: the id leaves
    keyed. It is kept because "an excerpt may not address this zone, a reference may"
    is a rule needing its own justification and §8.4's sentence gives none. The rule
    is about the ZONE, so it holds whoever asks.

    RE-ADDRESSED from `path` to `filename` by `104` §17.13, which moved the zone and
    left the claim alone. The claim was never about paths: it is that the refusal
    keys off the zone and not off the item kind, and `filename` is the zone that
    still refuses. Its control below ("a reference to an ordinary zone is
    untouched") is what stops this being satisfied by a gate that refuses every
    reference.

    SABOTAGE: scope `_located_zone` to `TEXT_BEARING` and this goes red alone.
    """
    file_id, key = _seed(zone_conn, zone="filename",
                         raw_value="Divorce Petition.pdf")
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
# CR-05: the same value under a second address, in a zone that is not its own
# ================================================================================
#
# The zone rule is enforced ON THE ZONE, so it is only as good as the honesty of the
# address. `extractors/filesystem.py` used to write the filename TWICE in one run --
# once truthfully at `zone="filename"`, and once through `METADATA_SLOTS` as
# `metadata:field=normalized_filename`. The gate refused the first and released the
# second in full, for the same file, in the same run.
#
# The fix is at the SOURCE and not here: the slot is gone, because a value in the
# wrong zone is a defect in the address rather than a gap in the rule. Answering it
# with a list of forbidden field names would have made `items.py` own the "gazetteer
# ... keyword list" its module docstring forbids, and would have left the next
# mis-zoned value uncaught. These tests hold the invariant the cut restores.


def _labelled_observation(conn, file_id: str, content_hash: str, *,
                          zone: str, label: str, raw_value: str,
                          extractor: str) -> str:
    """One span-less observation at `zone:field=label`, the CR-05 shape."""
    digest = hashlib.sha256(f"{content_hash}:{zone}:{label}".encode()).hexdigest()
    run_id = new_id()
    location = Location(zone=zone,
                        container_path=(Segment(kind="field", label=label),),
                        text_span=None)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type="image", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1,
    ))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name=extractor,
        extractor_version="1.0.0", source_type="image", raw_value=raw_value,
        location=location, occurrence_count=1, observed_at=OBSERVED_AT,
        reliability="direct", run_id=run_id,
        context_before=None, context_after=None, context_truncated=False,
    ))
    return observation_key(
        content_hash=digest, extractor_name=extractor,
        locator=serialize_locator(location), raw_value=raw_value)


def test_the_filesystem_extractor_gives_the_filename_exactly_one_home(zone_conn):
    """CR-05, closed at the source. The reproduction was a released filename.

    `METADATA_SLOTS` is read here rather than respelled, so restoring the slot fails
    this test rather than quietly restoring the release.

    SABOTAGE: put `"normalized_filename"` back in `METADATA_SLOTS` and this goes red.
    """
    assert "normalized_filename" not in METADATA_SLOTS, (
        "the filename has a home at `zone=\"filename\"`; a second one in a "
        "releasable zone is what CR-05 released in full")
    assert set(METADATA_SLOTS) == {"extension", "mime_type"}, (
        "both identify a FORMAT and neither identifies a person; a slot naming "
        "anything a person wrote or chose does not belong in a releasable zone")


def test_a_filename_under_a_metadata_address_would_have_been_released(zone_conn):
    """What the cut prevents, stated as the mechanism rather than as a worry.

    This is the reviewer's CR-05 probe: the identical `raw_value` is refused from the
    `filename` address and released from a `metadata` one. It documents that the gate
    decides on the ZONE and cannot see that two addresses carry one value -- which is
    why the fix had to be at the extractor.
    """
    file_id, filename_key = _seed(
        zone_conn, zone="filename", raw_value="Divorce settlement final.pdf")
    metadata_key = _labelled_observation(
        zone_conn, file_id, "hash-cr05", zone="metadata",
        label="normalized_filename", raw_value="Divorce settlement final.pdf",
        extractor="filesystem")

    refused = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=filename_key, span=None, reason="filename"),),
        file_id=file_id))
    assert isinstance(refused, Denied) and refused.reason == "always_local_item"

    released = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=metadata_key, span=None, reason="metadata"),),
        file_id=file_id))
    assert isinstance(released, Released), (
        "if this is ever Denied the gate grew a rule that does not key off the zone; "
        "read it before deleting this test")
    assert released.materialised_items[0].value == "Divorce settlement final.pdf"


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


# ================================================================================
# The third zone, and the member nobody mapped
# ================================================================================

def test_an_ocr_zone_excerpt_now_puts_the_recognised_text_on_the_cloud_wire(
        zone_conn):
    """Member THREE, re-argued to the opposite answer by `104` §17.13.

    **THIS TEST ASSERTED `Denied` FROM 4 Sep TO 9 Sep 2026.** What it was written for
    is still true and is why it exists: `ocr_output` is member three of §8.4's nine,
    the mapping from the nine kinds of DATA onto the fifteen document ZONES is made by
    hand one member at a time, and this member's mapping was missed for three days
    while `extractors/ocr.py` wrote every recognised region into `zone="ocr"`. The
    mapping is not undone -- `ocr` is still in `ALWAYS_LOCAL_ZONES` and
    `ALWAYS_LOCAL` still stands at nine. What the ruling changed is what that
    membership DOES: the two mapped zones §8.4's paths sentence actually names, `path`
    and `ocr`, are released to every target within the ceiling.

    **THE RESIDUAL IS THIS FIXTURE AND THE OWNER RULED KNOWING IT.** `104` R-161 is
    open: P5 emits a sensitivity signal by FIELD POSITION for a format's own
    person-valued slots, and an OCR reading has no field to be signalled by, so
    `sensitive_keys` is empty for a scanned page. The card number Apple Vision read
    off an identity document is therefore an ordinary releasable excerpt again, and
    §17.13 item 4 records it as accepted knowingly: "names and addresses inside body
    text are not detected ... and reach the provider for unprotected files". The
    value is asserted here rather than the verdict so that this file states the price
    of the ruling in the ruling's own terms.

    What still holds the line is the FILE gate and not this door: `cli.target_for`
    over `cli.model_route_permitted` (`104` R-170) sends a protected file and an
    unclassified file to the local model, and `105` §13.3's always-local privacy
    CLASS refuses a cloud target for a file classified into it.
    """
    file_id, key = _seed(zone_conn, zone="ocr", raw_value=CARD_NUMBER)
    decision = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="ocr"),),
        file_id=file_id))

    assert isinstance(decision, Released), (
        f"an `ocr`-zone excerpt bound for a cloud model was "
        f"{type(decision).__name__}; `104` §17.13 releases OCR text to every target "
        f"within the ceiling")
    assert [one.value for one in decision.materialised_items] == [CARD_NUMBER]


def test_the_zone_set_now_maps_three_members_and_still_adds_no_tenth():
    """The guard on the set itself, updated with the member it was missing."""
    assert len(ALWAYS_LOCAL) == 9
    assert "ocr_output" in ALWAYS_LOCAL
    assert ALWAYS_LOCAL_ZONES == frozenset({"path", "filename", "ocr"})
    assert not ALWAYS_LOCAL_ZONES & set(ALWAYS_LOCAL)


def test_the_real_ocr_extractors_whole_passage_is_released_and_nothing_bounds_it_here(
        zone_conn):
    """The one above seeds a synthetic row. THIS ONE runs the real extractor.

    `extractors/ocr.py` gained a whole-passage observation on 2026-09-04, because
    everything Apple Vision read off a screenshot was reaching `text_units` and
    nothing else: eleven image files on the owner's disk carried 14 to 27 recognised
    units each and emitted zero evidence, and the recogniser scans evidence only.

    That row is a WHOLE PAGE OF RECOGNISED TEXT, which is a far larger thing to leak
    than the card number the test above refuses -- a scanned identity document
    arrives here entire. The emitter addresses it `zone="ocr"` for exactly that
    reason, and this test is the proof that the choice is load-bearing rather than
    cosmetic: it drives the REAL gate over the REAL emitted observation.

    **RE-ARGUED 9 Sep 2026 BY `104` §17.13, AND THE ANSWER IS NOW `Released`.** The
    paragraphs above are why this test drives the real extractor and they are
    unchanged; what changed is the verdict, for the same reason as the two tests
    above it. The old sabotage -- change `zone="ocr"` to `zone="body"` in
    `extractors/ocr.py` -- no longer changes any answer, because neither zone is
    refused now, and saying so is more useful than keeping a sabotage that cannot
    fire.

    **WHAT BOUNDS THIS ROW IS NOT `check_item`, AND THAT IS THE FINDING THIS TEST NOW
    CARRIES.** §17.13's whole-document arm refuses a whole unit LONGER THAN the stored
    ceiling, and "whole" is answered by coverage of a text unit. `extractors/ocr.py`
    emits this whole-passage observation with NO `text_units` row at its own container
    path -- the same shape `104` §5 SF-1 found in `extractors/docx.py` -- so
    `resolve.materialise` reports `unit_length=None`, `is_whole_document` is False,
    and the arm cannot fire at any ceiling. The assertion below is run with a ceiling
    one character SHORTER than the passage and the passage is still released, which is
    that fact stated as a run rather than as a worry.

    The bound that does apply is one step out, in the two places that count characters
    rather than coverage: `model_facts.within_dossier_budget` skips a reading that
    does not fit the caller's remainder, so the stage never offers this row inside a
    full dossier, and the gate's own `dossier_over_budget` refuses a dossier over the
    stored ceiling when `measure_tokens` is wired -- which `_gate` in this file
    deliberately does not wire, so that a zone question is answered by the zone rules
    alone.
    """
    from evidence_shape.store import RunWriter
    from extractors.ocr import OcrOutput, OcrRegion, extract_ocr
    from extractors.safety import SafetyPolicy

    content_hash = "bcbb377bc839704c4e4ccf7781cce3dcc88cc8a288c9eebbffa245a3476c56e9"
    file_id = _file(zone_conn, "scanned-hkid.png", content_hash)
    scanned = ("HONG KONG PERMANENT IDENTITY CARD\n"
               f"CHAN TAI MAN\n{CARD_NUMBER}")

    result = extract_ocr(
        file_row={"file_id": file_id, "content_hash": content_hash,
                  "filename": "scanned-hkid.png"},
        path=Path("/corpus/scanned-hkid.png"),
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        ocr_engine=lambda target, *, config: OcrOutput(
            provider="apple-vision", provider_version="19.1",
            regions=tuple(
                OcrRegion(page=None, region=index, text=line, confidence=0.9)
                for index, line in enumerate(scanned.split("\n"), 1)),
            pages_processed=1, pages_total=1),
        config={"languages": ["en-US"]},
        find_structured_strings=lambda text: (),
        now=OBSERVED_AT, context_window=20)
    RunWriter(zone_conn, author="P5").write(result)

    stored = [dict(row) for row in zone_conn.execute(
        "SELECT observation_key, raw_value, location FROM evidence "
        "WHERE file_id = ? AND superseded_by IS NULL", (file_id,))]
    whole = [row for row in stored if scanned in row["raw_value"]]
    assert whole, (
        "the real extractor emitted no whole-passage row, so this test is guarding "
        f"nothing; stored {[r['raw_value'][:40] for r in stored]}")

    _classify(zone_conn, file_id, content_hash, key=whole[0]["observation_key"])
    _store_policy(zone_conn)
    # One character SHORTER than the passage, which is the ceiling that WOULD refuse
    # a whole unit under §17.13. It refuses nothing here, because the emitted row has
    # no text unit at its path for the coverage test to answer about.
    set_ceiling(zone_conn, CEILING_KEY, len(scanned) - 1)
    resolved = materialise(
        zone_conn, _Item(whole[0]["observation_key"], None))
    assert resolved.unit_length is None, (
        "`extractors/ocr.py` grew a `text_units` row at the whole passage's own "
        "container path, so the whole-document arm CAN fire for it now and the "
        "paragraph above this test is out of date -- read it before changing this")

    decision = _gate(zone_conn).release(_request(
        items=(Excerpt(observation_key=whole[0]["observation_key"], span=None,
                       reason="the recognised text of a scanned card"),),
        file_id=file_id))

    assert isinstance(decision, Released), (
        f"a whole page of OCR text was {type(decision).__name__}; `104` §17.13 "
        f"releases OCR text to every target within the ceiling")
    assert [one.value for one in decision.materialised_items] == [scanned], (
        "the whole recognised page is what reaches the model, card number and name "
        "together, which is what §17.13 item 4 accepts knowingly")


# ================================================================================
# `104` R-159, then `104` §17.13: whose target the always-local ZONE rule was about,
# and then that the answer stopped depending on the target at all
# ================================================================================
#
# THE R-159 PARAGRAPH, KEPT AS HISTORY. `00`:186 puts paths, complete extracted text
# and OCR output under "should remain local" and says the engine sends selected
# excerpts "when a cloud model is used"; until 8 Sep 2026 the code applied that
# sentence to every destination, and the gate's OTHER always-local rule -- `105`
# §13.3's privacy CLASS, `gate.py` ~347 -- was already cloud-only, so one door
# answered "always local" two ways about one request. The owner ruled §15.4 item 14
# the first way: a local model may be shown the person's folder path and OCR text
# within the dossier ceiling. The two tests below were written as PAIRS for that
# ruling -- the same fixture, the same request, one field different -- because "the
# rule now depends on the target" is a claim about a difference.
#
# **`104` §17.13, 9 Sep 2026: THE PAIR COLLAPSED, AND THAT IS WHAT THESE TESTS NOW
# ASSERT.** The owner extended item 14 to the cloud target -- "a cloud model may be
# shown a whole text unit, the person's folder path and OCR text within the same
# ceiling, for every file the cloud gate permits" -- so `path` and `ocr` no longer
# divide by destination and `check_item` has no arm that branches on `locality`. The
# tests keep their two-target shape rather than dropping to one, because a difference
# that has gone is a claim worth running: a build that quietly restored the cloud
# refusal would go red here and nowhere else in this section.
#
# What the destination still decides is which FILE reaches this door at all
# (`cli.target_for` over `cli.model_route_permitted`, `104` R-170) and §13.3's
# privacy CLASS in `gate.py` ~347. Neither is a zone rule, and neither is here.

def test_a_path_zone_excerpt_is_released_to_every_target(zone_conn):
    """THE PAIR THAT COLLAPSED. Same fixture, same item, one field -- same answer.

    **This test asserted `Denied` for `CLOUD` and `Released` for `LOCAL` on 8 Sep
    2026, which was `104` R-159.** The measurement that made R-159 is still the
    reason the zone is released at all: 20 of r15's 43 labelled coursework files
    carried their course code ONLY here, in the folder the person filed the file in,
    and until 8 Sep no model was shown it. `104` §17.13 then asked the same question
    about the cloud with the same measurement in front of it -- half the corpus
    refused, the cloud shown zero characters -- and the owner extended item 14 to the
    cloud target.

    Both halves are asserted rather than one, and the loop is over both targets, for
    the reason the pair was written in the first place: the claim is about a
    DIFFERENCE, and "there is no longer a difference" is a claim of the same kind. A
    build that restored the cloud refusal -- by putting `locality` back into
    `check_item`'s zone arm, which is the obvious way to read `00`:186's "when a
    cloud model is used" -- goes red here.
    """
    file_id, key = _seed(zone_conn, zone="path", raw_value=PRIVATE_DIRECTORY)
    item = Excerpt(observation_key=key, span=None, reason="path")

    for target in (CLOUD, LOCAL):
        released = _gate(zone_conn).release(_request(
            items=(item,), file_id=file_id, model_target=target))
        assert isinstance(released, Released), (
            f"a path-zone excerpt bound for a {target.locality} model was "
            f"{type(released).__name__}; `104` §17.13 releases it to either")
        assert ([one.value for one in released.materialised_items]
                == [PRIVATE_DIRECTORY]), (
            f"the {target.locality} model is shown the folder itself, which is what "
            f"the ruling is")


def test_an_ocr_zone_excerpt_is_released_to_every_target(zone_conn):
    """The same collapsed pair on member three, and the residual moved with it.

    **This asserted `Denied` for `CLOUD` and `Released` for `LOCAL` on 8 Sep 2026.**
    29 OCR runs on r15 were shown to nobody, which is what R-159 was ruled on. The
    sentence that ended the R-159 version of this docstring was "nothing here leaves
    the device", and under `104` §17.13 that sentence is no longer true of this test:
    with R-161 open, `sensitive_keys` is empty for a scanned page, so the recognised
    text of an unclassified scanned document -- the card number in this very fixture
    -- now goes to the provider. §17.13 item 4 records that as accepted knowingly.

    `105` §13.3's always-local privacy CLASS still refuses a cloud target, and
    `cli.model_route_permitted` still routes a protected or unclassified file to the
    local model. Those are decisions about the FILE, taken before this door; this
    door asks about the zone, and the zone answers the same for either target.
    """
    file_id, key = _seed(zone_conn, zone="ocr", raw_value=CARD_NUMBER)
    item = Excerpt(observation_key=key, span=None, reason="ocr")

    for target in (CLOUD, LOCAL):
        released = _gate(zone_conn).release(_request(
            items=(item,), file_id=file_id, model_target=target))
        assert isinstance(released, Released), (
            f"an ocr-zone excerpt bound for a {target.locality} model was "
            f"{type(released).__name__}; `104` §17.13 releases it to either")
        assert [one.value for one in released.materialised_items] == [CARD_NUMBER]


def test_a_filename_zone_excerpt_is_refused_to_a_local_target_too(zone_conn):
    """The member the ruling does NOT release, and the one place this build reads
    `104` R-159's brief against its letter.

    `filename`'s membership in `ALWAYS_LOCAL_ZONES` was never §8.4's paths sentence.
    It is §7.7's flagged SIXTH releasable kind wearing a zone, put there by CR-01 so
    that an `Excerpt` cannot address a filename and bypass `allow_unratified` and
    §7.3's protected-records ban -- "refused HERE and released THERE". A local target
    that admitted this excerpt would falsify three docstrings that carry no locality
    (`gate`'s module text on `_located_zone`, `release.NAME_BEARING`,
    `model_facts.build_fact_request`) and would release nothing new: the name already
    arrives through `items.Filename`, the door built for it.

    The ruling's own words name two zones, "the person's folder path and OCR text",
    and `vocabulary.RELEASED_TO_EVERY_TARGET` is that phrase transcribed.

    **UNMOVED BY `104` §17.13, 9 Sep 2026, and this is the test that says so.** The
    ruling that extended item 14 to the cloud target extended it to the two zones the
    sentence names and to no third one, so this test is the only one in the section
    whose two-target loop still returns two refusals. Everything above it changed
    answer; this did not, because the reason it refuses was never about a
    destination.
    """
    file_id, key = _seed(zone_conn, zone="filename", raw_value="passport.pdf")
    item = Excerpt(observation_key=key, span=None, reason="the name")

    for target in (CLOUD, LOCAL):
        decision = _gate(zone_conn).release(_request(
            items=(item,), file_id=file_id, model_target=target))
        assert isinstance(decision, Denied), (
            f"a filename-zone excerpt bound for a {target.locality} model was "
            f"{type(decision).__name__}; §7.7's kind has its own door")
        assert decision.reason == "always_local_item"


def test_the_ruling_partitions_the_three_zones_and_a_fourth_would_fail_at_import():
    """The set guard, one turn stronger than the one above it.

    `ALWAYS_LOCAL_ZONES` is a HAND-MADE mapping -- its own comment says "THE OTHER
    SIX HAVE NOT BEEN AUDITED" -- so a fourth zone will be added one day by someone
    reading §8.4 and not this ruling. `privacy.vocabulary` raises `ImportError` when
    the two halves stop partitioning the whole, which puts that person in front of
    the locality question instead of defaulting their zone to the local model.
    """
    assert RELEASED_TO_EVERY_TARGET == frozenset({"path", "ocr"})
    assert ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET == frozenset({"filename"})
    assert (RELEASED_TO_EVERY_TARGET | ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET
            == ALWAYS_LOCAL_ZONES)
    assert not (RELEASED_TO_EVERY_TARGET & ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET)
