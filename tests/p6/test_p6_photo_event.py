# tests/p6/test_p6_photo_event.py
"""G7 — Done-means 26 and 27. §4.2's deterministic event, §2.6's hierarchy, A07."""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import SIGNAL_TIERS

from facts import photo_event
from facts.facets import fill_or_abstain
from facts.file_facts import facts_for_file
from facts.photo_event import (
    EVENT_FIELD, EVENT_INPUTS, EVENT_STATE, MEDIA_TYPES, MEDIA_TYPE_FIELD,
    PHOTO_BANDS, SCREENSHOT_BAND, PhotoEventClustering, media_type, photo_events,
)
from facts.states import DIRECT, POSSIBLE, VALIDATED, is_stronger
from facts.unresolved import (
    BELOW_MARGIN, BELOW_SCORE_THRESHOLD, NO_CANDIDATE_EVIDENCE, unresolved_for_file,
)

CLOCK = "2026-08-19T12:00:00+00:00"

#: P5 spells the tag names; P6 injects them. The test is the only place they meet.
LABELS = {
    "camera": frozenset({"Make", "Model"}),
    "capture_time": frozenset({"DateTimeOriginal"}),
    "location": frozenset({"GPSLatitude", "GPSLongitude"}),
}

#: Every number below is the TEST's. §4.2 names the inputs and states no thresholds.
WEIGHTS = {SIGNAL_TIERS[0]: 8.0, SIGNAL_TIERS[1]: 4.0, SIGNAL_TIERS[2]: 7.5}


def _identifiers(module) -> set[str]:
    """Every name and attribute this module's CODE mentions.

    An AST walk, not a source-text search: a text search matches comments and
    docstrings, and a guard that does that has broken three tasks on this project
    already (P5 PLAN, Task 20). §2.6 rules OCR text density out by name, so the
    assertion is that nothing here can reach a text unit at all.
    """
    tree = ast.parse(inspect.getsource(module))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(alias.name for alias in node.names)
            names.add(getattr(node, "module", "") or "")
    return names


def _record(conn, tmp_path, *, name, body):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Photos", mime_type="image/jpeg",
        detected_format="jpeg", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label, signal_tier,
             extractor="image.metadata", zone="metadata", source_type="image",
             analysis_tier="native"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct",
        run_id=run_id, signal_tier=signal_tier)
    record_observation(conn, observation)
    return observation.observation_key


def _photo(conn, tmp_path, *, name, body, camera="Canon EOS R5",
           stamp="2026:07:04 11:02:13", gps="40.7128", tier_three=None):
    """One image with §4.2's three inputs, each at the band §2.6 gives it."""
    file_id, content_hash = _record(conn, tmp_path, name=name, body=body)
    _observe(conn, run_id=f"{name}-cam", file_id=file_id, content_hash=content_hash,
             raw=camera, label="Make", signal_tier=SIGNAL_TIERS[0])
    _observe(conn, run_id=f"{name}-time", file_id=file_id, content_hash=content_hash,
             raw=stamp, label="DateTimeOriginal", signal_tier=SIGNAL_TIERS[1])
    _observe(conn, run_id=f"{name}-gps", file_id=file_id, content_hash=content_hash,
             raw=gps, label="GPSLatitude", signal_tier=SIGNAL_TIERS[1])
    if tier_three is not None:
        _observe(conn, run_id=f"{name}-shot", file_id=file_id,
                 content_hash=content_hash, raw=tier_three, label="PixelWidth",
                 signal_tier=SIGNAL_TIERS[2])
    return file_id, content_hash


def _same_camera_and_day(left, right) -> bool:
    """The injected contextual check. §4.2 names the inputs and states no window."""
    return (left["camera"] == right["camera"]
            and bool(left["capture_time"]) and bool(right["capture_time"])
            and left["capture_time"][0][:10] == right["capture_time"][0][:10])


CLUSTERING = PhotoEventClustering(labels=LABELS, same_event=_same_camera_and_day,
                                  minimum_members=2)


def _event_rows(conn, file_id, content_hash):
    return [r for r in facts_for_file(conn, file_id, content_hash)
            if r["field_key"] == EVENT_FIELD]


@pytest.fixture()
def one_event(p6_conn, tmp_path):
    left = _photo(p6_conn, tmp_path, name="IMG_0101.jpg", body=b"pixels-one")
    right = _photo(p6_conn, tmp_path, name="IMG_0102.jpg", body=b"pixels-two",
                   stamp="2026:07:04 11:04:52", gps="40.7130")
    return left, right


def test_a_camera_time_and_gps_cluster_is_a_validated_event(one_event, p6_conn):
    # Done-means 26, and §4.2's "a deterministic event created from camera, time,
    # and GPS metadata".
    (left, left_hash), (right, right_hash) = one_event
    written = photo_events(p6_conn, file_ids=(left, right), clustering=CLUSTERING)
    assert set(written) == {left, right}
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        rows = _event_rows(p6_conn, file_id, digest)
        assert len(rows) == 1
        assert rows[0]["reliability_state"] == EVENT_STATE
        assert json.loads(rows[0]["evidence_refs"])       # M14: cited, and non-empty
        assert all(ref.startswith("sha256:")
                   for ref in json.loads(rows[0]["evidence_refs"]))


def test_the_event_state_is_never_direct_and_never_possible():
    # Not `direct`: no explicit slot states an event. Not `possible`: P9 requires a
    # seed fact to be Direct or Validated, so a `possible` event is unusable as one.
    assert EVENT_STATE == VALIDATED
    assert is_stronger(DIRECT, EVENT_STATE)
    assert is_stronger(EVENT_STATE, POSSIBLE)


def test_an_image_with_no_exif_produces_no_event_and_no_row(p6_conn, tmp_path):
    # Done-means 26. §2.6: absence is never evidence, and P5 writes no absence
    # observation for this module to read. Nothing was proposed, so nothing refused.
    left, left_hash = _record(p6_conn, tmp_path, name="stripped.jpg", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="stripped2.jpg", body=b"two")
    assert photo_events(p6_conn, file_ids=(left, right),
                        clustering=CLUSTERING) == {}
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        assert facts_for_file(p6_conn, file_id, digest) == []
        assert unresolved_for_file(p6_conn, file_id, digest) == []


def test_a_tier_three_signal_never_contributes_to_an_event(p6_conn, tmp_path):
    # §2.6 puts exact display resolutions, PNG format and software metadata in the
    # screenshot-hypothesis band. §4.2's event is built from the other two bands.
    left, left_hash = _record(p6_conn, tmp_path, name="a.png", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="b.png", body=b"two")
    for file_id, digest, run in ((left, left_hash, "l"), (right, right_hash, "r")):
        # A tier-3 reading that carries a CAMERA label: the label is not what is
        # read, the tier is (M2).
        _observe(p6_conn, run_id=f"{run}-shot", file_id=file_id,
                 content_hash=digest, raw="Canon EOS R5", label="Make",
                 signal_tier=SIGNAL_TIERS[2])
    assert photo_events(p6_conn, file_ids=(left, right),
                        clustering=CLUSTERING) == {}
    assert _event_rows(p6_conn, left, left_hash) == []


def test_a_tier_is_read_from_the_observation_and_never_re_derived(p6_conn, tmp_path):
    # M2, stated in the skeleton's Global Constraints: `signal_tier` "comes from P4's
    # observation and is never recomputed from `extractor_name` or a field label".
    # These two rows carry the image extractor's name AND a camera label AND no tier.
    left, left_hash = _record(p6_conn, tmp_path, name="untiered1.jpg", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="untiered2.jpg", body=b"two")
    for file_id, digest, run in ((left, left_hash, "l"), (right, right_hash, "r")):
        _observe(p6_conn, run_id=f"{run}-cam", file_id=file_id, content_hash=digest,
                 raw="Canon EOS R5", label="Make", signal_tier=None)
        _observe(p6_conn, run_id=f"{run}-time", file_id=file_id, content_hash=digest,
                 raw="2026:07:04 11:02:13", label="DateTimeOriginal",
                 signal_tier=None)
    assert photo_events(p6_conn, file_ids=(left, right),
                        clustering=CLUSTERING) == {}
    assert media_type(p6_conn, file_id=left, content_hash=left_hash,
                      tier_weight=WEIGHTS, minimum_score=1.0,
                      minimum_margin=1.0) is None
    rows = unresolved_for_file(p6_conn, left, left_hash,
                               field_key=MEDIA_TYPE_FIELD)
    assert [r["reason"] for r in rows] == [NO_CANDIDATE_EVIDENCE]


def test_a_cluster_below_the_injected_minimum_is_not_an_event(p6_conn, tmp_path):
    # §4.2 uses the event as a GROUP seed; how many photographs make one is deferred
    # with the time window and the GPS radius, so it is injected.
    only, only_hash = _photo(p6_conn, tmp_path, name="alone.jpg", body=b"one")
    assert photo_events(p6_conn, file_ids=(only,), clustering=CLUSTERING) == {}
    assert _event_rows(p6_conn, only, only_hash) == []
    assert unresolved_for_file(p6_conn, only, only_hash) == []


def test_tier_one_and_tier_three_in_conflict_fill_no_media_type(p6_conn, tmp_path):
    # Done-means 27, and §2.6's "conflicting signals should lead to abstention rather
    # than an invented classification" — reached by the ordinary §3.7 margin, with
    # weights the TEST injects, and not by a mechanism this module owns.
    file_id, content_hash = _record(p6_conn, tmp_path, name="conflict.png",
                                    body=b"pixels")
    _observe(p6_conn, run_id="c-cam", file_id=file_id, content_hash=content_hash,
             raw="Canon EOS R5", label="Make", signal_tier=SIGNAL_TIERS[0])
    _observe(p6_conn, run_id="c-shot", file_id=file_id, content_hash=content_hash,
             raw="2560x1440", label="PixelWidth", signal_tier=SIGNAL_TIERS[2])
    assert media_type(p6_conn, file_id=file_id, content_hash=content_hash,
                      tier_weight=WEIGHTS, minimum_score=1.0,
                      minimum_margin=2.0) is None
    rows = unresolved_for_file(p6_conn, file_id, content_hash,
                               field_key=MEDIA_TYPE_FIELD)
    assert [r["reason"] for r in rows] == [BELOW_MARGIN]


def test_stripped_exif_never_becomes_a_screenshot(p6_conn, tmp_path):
    # A07, verbatim from tests/eval/fixtures/adversarial/A07.json: outcome
    # `abstained`, forbidden value {"field": "media_type", "value": "screenshot"}.
    # §2.6: "must not mistake the absence of EXIF for proof that an image is a
    # screenshot." The margin is injected at zero, so the arithmetic alone would
    # have produced the forbidden value.
    file_id, content_hash = _record(p6_conn, tmp_path, name="whatsapp.jpg",
                                    body=b"a real photograph, stripped")
    _observe(p6_conn, run_id="a-shot", file_id=file_id, content_hash=content_hash,
             raw="1170x2532", label="PixelWidth", signal_tier=SIGNAL_TIERS[2])
    _observe(p6_conn, run_id="a-fmt", file_id=file_id, content_hash=content_hash,
             raw="PNG", label="Format", signal_tier=SIGNAL_TIERS[2])
    assert media_type(p6_conn, file_id=file_id, content_hash=content_hash,
                      tier_weight=WEIGHTS, minimum_score=0.0,
                      minimum_margin=0.0) is None
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash,
                               field_key=MEDIA_TYPE_FIELD)
    assert [r["reason"] for r in rows] == [BELOW_MARGIN]
    # The refusal cites what it looked at; a refusal with no record is not inspectable.
    assert len(json.loads(rows[0]["evidence_refs"])) == 2


def test_a_missing_signal_contributes_nothing_to_either_candidate(p6_conn, tmp_path):
    # Done-means 27. Provable precisely because P5 writes no absence observation:
    # the file with one reading and the file with three reach the same conclusion,
    # and the two the first one lacks moved neither candidate.
    lean, lean_hash = _record(p6_conn, tmp_path, name="lean.jpg", body=b"one")
    _observe(p6_conn, run_id="lean-cam", file_id=lean, content_hash=lean_hash,
             raw="Canon EOS R5", label="Make", signal_tier=SIGNAL_TIERS[0])
    full, full_hash = _photo(p6_conn, tmp_path, name="full.jpg", body=b"two")
    for file_id, digest in ((lean, lean_hash), (full, full_hash)):
        assert media_type(p6_conn, file_id=file_id, content_hash=digest,
                          tier_weight=WEIGHTS, minimum_score=1.0,
                          minimum_margin=1.0) is not None
        row = [r for r in facts_for_file(p6_conn, file_id, digest)
               if r["field_key"] == MEDIA_TYPE_FIELD][0]
        assert row["canonical_value"] == MEDIA_TYPES[0]
        assert unresolved_for_file(p6_conn, file_id, digest,
                                   field_key=MEDIA_TYPE_FIELD) == []


def test_ocr_text_density_is_never_a_screenshot_signal(p6_conn, tmp_path):
    # §2.6: "OCR text density is also not a reliable screenshot detector because
    # receipts, document scans, whiteboards, and photographs of pages can all contain
    # dense text." Structural first: nothing here can reach a text unit at all.
    mentioned = _identifiers(photo_event)
    assert not [name for name in mentioned
                if "text" in name.lower() or "unit" in name.lower()]
    assert "evidence_shape.store" not in mentioned
    # And behaviourally: a page photographed at close range, dense with text.
    file_id, content_hash = _record(p6_conn, tmp_path, name="whiteboard.jpg",
                                    body=b"pixels")
    _observe(p6_conn, run_id="w-cam", file_id=file_id, content_hash=content_hash,
             raw="Canon EOS R5", label="Make", signal_tier=SIGNAL_TIERS[0])
    _observe(p6_conn, run_id="w-ocr", file_id=file_id, content_hash=content_hash,
             raw="lecture notes " * 400, label="ocr_text", signal_tier=None,
             extractor="ocr.vision", zone="ocr", source_type="ocr",
             analysis_tier="ocr")
    assert media_type(p6_conn, file_id=file_id, content_hash=content_hash,
                      tier_weight=WEIGHTS, minimum_score=1.0,
                      minimum_margin=1.0) is not None
    row = [r for r in facts_for_file(p6_conn, file_id, content_hash)
           if r["field_key"] == MEDIA_TYPE_FIELD][0]
    assert row["canonical_value"] == MEDIA_TYPES[0]


def test_the_clustering_and_the_weights_are_injected_with_no_defaults():
    # §4.2 names the inputs and states no time window, no GPS radius and no
    # camera-identity test; §3.7's weights are Deferred. None is here.
    fields = dataclasses.fields(PhotoEventClustering)
    assert [f.name for f in fields] == ["labels", "same_event", "minimum_members"]
    for field in fields:
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING
    signature = inspect.signature(media_type)
    for name in ("tier_weight", "minimum_score", "minimum_margin"):
        parameter = signature.parameters[name]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is inspect.Parameter.empty
    clustering = inspect.signature(photo_events).parameters["clustering"]
    assert clustering.default is inspect.Parameter.empty
    # Task 25's technique: runtime introspection of the namespace, not a text search.
    numbers = {name: value for name, value in vars(photo_event).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {}
    # The bands are P4's published order, read — not P6's copy of it.
    assert PHOTO_BANDS == SIGNAL_TIERS[:-1]
    assert SCREENSHOT_BAND == SIGNAL_TIERS[-1:]
    assert EVENT_INPUTS == ("camera", "capture_time", "location")
    assert set(LABELS) == set(EVENT_INPUTS)


def test_the_result_does_not_depend_on_the_order_the_file_ids_arrive_in(
        one_event, p6_conn):
    # P4's reads are in insertion order and P6 must not inherit it (Global
    # Constraints). Two orders, one outcome, compared as sets of stored rows.
    (left, left_hash), (right, right_hash) = one_event
    forward = photo_events(p6_conn, file_ids=(left, right), clustering=CLUSTERING)
    reverse = photo_events(p6_conn, file_ids=(right, left), clustering=CLUSTERING)
    assert set(forward) == set(reverse) == {left, right}

    def shape(written):
        return sorted(
            (r["file_id"], r["reliability_state"], r["canonical_value"],
             r["evidence_refs"])
            for file_id, digest in ((left, left_hash), (right, right_hash))
            for r in _event_rows(p6_conn, file_id, digest)
            if r["fact_id"] in set(written.values()))

    assert shape(forward) == shape(reverse)


def test_the_fact_and_the_abstention_of_one_pass_share_one_cache_key(
        p6_conn, tmp_path):
    # Preamble §3.2's deciding argument, and the reason this module does NOT key on
    # "the observations the fact cites": "The fact and the abstention produced by one
    # pass share one key … an abstention with no citations has no cited observations
    # to compute a key from. One key per pass answers both."
    #
    # _ASSEMBLY-RULINGS.md §9.2 names this task's own document (`16-19:76-77`) as one
    # of the three carrying the LOSING rule; the preamble carries the winner and is
    # later, so the deviation is deliberate and is pinned here.
    #
    # Every file below carries an observation the event does NOT cite, written by a
    # SECOND extractor. That is what makes the two rules give different answers: keyed
    # on the cited observations the pairs are one, keyed on the file version they are
    # two, and `facts.facets.fill_or_abstain` already keys on the file version.
    left, left_hash = _photo(p6_conn, tmp_path, name="IMG_0201.jpg", body=b"one")
    right, right_hash = _photo(p6_conn, tmp_path, name="IMG_0202.jpg", body=b"two",
                               stamp="2026:07:04 11:07:41", gps="40.7131")
    for name, file_id, digest in (("l", left, left_hash), ("r", right, right_hash)):
        _observe(p6_conn, run_id=f"{name}-dim", file_id=file_id,
                 content_hash=digest, raw="2560x1440", label="PixelWidth",
                 signal_tier=SIGNAL_TIERS[2], extractor="image.dimensions")

    # Half one: the fact this module writes and the refusal `fill_or_abstain` writes
    # for the same file version are one §3.4 slot.
    photo_events(p6_conn, file_ids=(left, right), clustering=CLUSTERING)
    event_row = _event_rows(p6_conn, left, left_hash)[0]
    assert len(json.loads(event_row["evidence_refs"])) == 3     # the tier-3 is not one
    assert media_type(p6_conn, file_id=left, content_hash=left_hash,
                      tier_weight=WEIGHTS, minimum_score=1_000_000.0,
                      minimum_margin=0.0) is None
    refused = unresolved_for_file(p6_conn, left, left_hash,
                                  field_key=MEDIA_TYPE_FIELD)
    assert [r["reason"] for r in refused] == [BELOW_SCORE_THRESHOLD]
    assert event_row["cache_key"] == refused[0]["cache_key"]

    # Half two: the §2.6 refusal this module writes BEFORE any ranking lands in the
    # same slot `fill_or_abstain` would have used. A07's file — one tier-3 reading it
    # cites and one untiered reading, by two extractors — then facets' own writer.
    a07, a07_hash = _record(p6_conn, tmp_path, name="stripped.jpg", body=b"stripped")
    _observe(p6_conn, run_id="a-shot", file_id=a07, content_hash=a07_hash,
             raw="1170x2532", label="PixelWidth", signal_tier=SIGNAL_TIERS[2],
             extractor="image.dimensions")
    _observe(p6_conn, run_id="a-fmt", file_id=a07, content_hash=a07_hash,
             raw="JPEG", label="Format", signal_tier=None)
    assert media_type(p6_conn, file_id=a07, content_hash=a07_hash,
                      tier_weight=WEIGHTS, minimum_score=0.0,
                      minimum_margin=0.0) is None
    assert fill_or_abstain(p6_conn, file_id=a07, content_hash=a07_hash,
                           field_key=MEDIA_TYPE_FIELD, candidates=(),
                           minimum_score=0.0, minimum_margin=0.0) is None
    keys = {r["reason"]: r["cache_key"]
            for r in unresolved_for_file(p6_conn, a07, a07_hash,
                                         field_key=MEDIA_TYPE_FIELD)}
    assert set(keys) == {BELOW_MARGIN, NO_CANDIDATE_EVIDENCE}
    assert keys[BELOW_MARGIN] == keys[NO_CANDIDATE_EVIDENCE]
