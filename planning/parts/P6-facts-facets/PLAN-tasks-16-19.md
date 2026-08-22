# P6 — Facts and facets — PLAN, Tasks 16–19

> This is the detail pass for the last task of **Wave C (16)** and the first three seams of
> **Wave D (17–19)**. **Read `PLAN-tasks-14-15.md` first** — it carries the "What already exists"
> import list, the one cache-key rule these producers share, and the two tasks (14, 15) that sit
> beside Task 16 in Wave C. The rules, the verified seams and the file layout are in
> `PLAN-SKELETON.md`; the `Interfaces:` block on each task below is the same contract, honoured name
> for name, with any addition to a `Produces:` line called out where it is made.
>
> Tasks 1–15 and 20–27 are written by other authors against the same skeleton.

---

## What these four tasks add to the import list

Beyond the surface `PLAN-tasks-14-15.md` enumerates, Tasks 16–19 import these and nothing else:

```text
facts.facets        Candidate(value, score, evidence_refs)
                    fill_or_abstain(conn, *, file_id, content_hash, field_key, candidates,
                                    minimum_score, minimum_margin) -> str | None
facts.domains       active_field_allowlist(conn, *, file_id, content_hash,
                                           activation_signals) -> tuple[str, ...]
facts.states        is_stronger(a: str, b: str) -> bool
facts.file_facts    FILE_FACTS_COLUMNS: tuple[str, ...]
                    FORBIDDEN_COLUMN_SUBSTRINGS: tuple[str, ...]
facts.unresolved    UNRESOLVED_REASONS: tuple[str, ...]
database_agent.supersede   mark_superseded(conn, table, *, old_id, new_id, reason) -> None
                           chain(conn, table, record_id) -> list[sqlite3.Row]
                           supersede_ddl(table) -> str
extractors.failure         ContractViolation                     — Task 19 only, and see its note
extractors.ocr_policy      text_layer_state                      — Task 19's danger test only
extractors.sink            ExtractionResult                      — Task 19's danger test only
evidence_shape.vocabulary  SIGNAL_TIERS, ANALYSIS_TIERS, RELIABILITY_STATES, check
```

**Verified live, 2026-08-22, by execution rather than from a document.**

- `mark_superseded(conn, table, *, old_id, new_id, reason) -> None` writes **three** columns across
  **two** rows: the old row gets `superseded_by` and `supersede_reason`, the new row gets
  `supersedes`. It raises `KeyError` on an unknown `old_id`, `ValueError` when `old_id` is already
  superseded (*"the first supersede_reason is never overwritten (§8.2)"*), `ValueError` on an empty
  reason, and `ValueError` when the link would cycle. **It does not touch `preferred` and knows
  nothing about it** — that column is Task 18's whole job.
- `chain(conn, table, record_id)` walks **forward only**: with `a → b → c` recorded, `chain(a)`
  returns `[a, b, c]` and `chain(c)` returns `[c]`. So a history read must start at the oldest row,
  not at the newest, and Task 18's `fact_history` finds the tail before it walks.
- `supersede_ddl("file_facts")` returns exactly
  `"supersedes TEXT, superseded_by TEXT, supersede_reason TEXT"`.
- `Observation.__post_init__` **does not** enforce P4 conformance rule 11 — an `Observation` with
  `signal_tier=1` and `source_type="text_document"` constructs without complaint;
  `conformance.validate_observation` is where rule 11 lives. Task 16's M2 test relies on this being
  true, and on nothing else about it.
- `SIGNAL_TIERS == (1, 2, 3)` and its members are **integers**. §2.6's three bands arrive in that
  order, which is what lets Task 16 read the screenshot band as `SIGNAL_TIERS[-1:]` rather than
  spelling a `3`.
- `ExtractionResult(run, observations=(), text_units=())` — `run` is a `Mapping`, and
  `ExtractionResult(run={}, text_units=({"text": "a real text layer"},))` constructs.
  `ocr_policy._has_text`
  reads `unit["text"].strip()` and nothing else, so a one-key text unit is a complete fixture for
  Task 19's danger test.
- `extractors.failure.ContractViolation` inherits `Exception` directly, and
  `orchestrator._extract_one` re-raises it by name rather than converting it into a `failed` run.
  Executed end to end: a `ContractViolation` subclass raised from inside a `no_usable_facts`
  callable propagates out of `ocr_policy.text_layer_state` untouched.
- `database_agent.events.RESERVED_EVENT_TYPES` contains `"fact creation"` and `"fact rejection"`,
  both spelled with a space. It contains **no** supersession event and no abstention event, which is
  why Task 18 appends none.

---

## The one cache-key rule these tasks share

Identical to the rule stated once in `PLAN-tasks-14-15.md`, restated here because Task 16 is a
separate module and cannot import another task's private helper without breaking its contract:

- **`extractor_version`** is `canonical_json` of the sorted distinct `[extractor_name,
  extractor_version]` pairs of the observations the fact cites.
- **`analysis_tier`** is the **last** tier present in `ANALYSIS_TIERS` order — `filesystem` <
  `native` < `ocr` < `llm`.
- **`model_identifier` and `prompt_fingerprint` are `None`** on every deterministic fact. Task 17 is
  the one exception in this file: an LLM-supported fact carries P8's real values and lands at
  `analysis_tier = "llm"`, which is `ANALYSIS_TIERS[-1]` and is why the two never share a slot.

The reconciliation belongs in `facts.cache`, which Task 6 owns. It is written out per producer with
this note above it. See *Contract notes* at the end.

---

### Wave C — the last of the three fact families P6 was handed

### Task 16: Photo events, and §2.6's media-type conflict (G7, M2)

**Files:**
- Create: `src/facts/photo_event.py`
- Test: `tests/p6/test_p6_photo_event.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `cite`, `analysis_tier_for_observation`;
  `facts.facets` — `Candidate`, `fill_or_abstain`; `facts.file_facts` — `write_fact`,
  `FACT_ORIGINS`; `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`; `facts.values` —
  `ensure_value`, `VALUE_ORIGINS`; `facts.cache.fact_cache_key`;
  `database_agent.files_table.get_file`; `evidence_shape.canonical` — `canonical_json`, `sha256_of`;
  `evidence_shape.vocabulary` — `SIGNAL_TIERS`, `ANALYSIS_TIERS`, `check`.
- Produces (`photo_event.py`): `EVENT_FIELD: str`, `MEDIA_TYPE_FIELD: str`, `EVENT_STATE: str`,
  `EVENT_INPUTS: tuple[str, str, str]`, `MEDIA_TYPES: tuple[str, str]`,
  `PHOTO_BANDS: tuple[int, ...]`, `SCREENSHOT_BAND: tuple[int, ...]`,
  `PhotoEventClustering(labels, same_event, minimum_members)` — injected, no defaults;
  `photo_events(conn, *, file_ids, clustering) -> Mapping[str, str]`;
  `media_type(conn, *, file_id, content_hash, tier_weight, minimum_score, minimum_margin) -> str | None`.

> **Addition to the skeleton's `Produces:` line, declared.** The skeleton names three: `photo_events`,
> `media_type`, `PhotoEventClustering`. The six constants above are added because §2.6's two
> hypotheses, §4.2's three inputs and the two field keys are each a spelling that would otherwise
> live twice — once in the module and once in the test — and P6's standing rule is that a closed
> vocabulary has one home. Nothing named by the skeleton is renamed or re-typed.

**Done-means:** 26, 27. **Adversarial case:** A07.

**§4.2, quoted, because it is the only sentence in the design that states this fact exists:**

> For a photo group, it might be a deterministic event created from camera, time, and GPS metadata.

**§2.6, quoted in full for the hierarchy, because every clause of it decides something below:**

> The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.

**§2.6 again, the sentence that makes the tier-3-only case a refusal rather than a conclusion:**

> However, the system must not mistake the absence of EXIF for proof that an image is a screenshot. Messaging platforms and downloaded web images often strip metadata from real photographs. OCR text density is also not a reliable screenshot detector because receipts, document scans, whiteboards, and photographs of pages can all contain dense text.

**The tier is read, never re-derived (M2).** `Observation.signal_tier` carries §2.6's hierarchy
because P4 put it there for exactly this consumer, and the skeleton's Global Constraints are
explicit: *"`signal_tier` comes from P4's observation and is never recomputed from `extractor_name`
or a field label — that would encode §2.6 in a second place (M2)."* So this module branches on the
integer and on nothing else. An observation P5 left untiered contributes to nothing, and the test
below drives that case with an observation carrying a camera label, the image extractor's name, and
`signal_tier = None`: it produces no event and no vote.

**The bands are read off P4's published order, not re-spelled.** `SIGNAL_TIERS == (1, 2, 3)` and
§2.6's three bands arrive in that order, so `SCREENSHOT_BAND = SIGNAL_TIERS[-1:]` and
`PHOTO_BANDS = SIGNAL_TIERS[:-1]`. That is a reading of a published tuple — the same technique the
cache-key rule applies to `ANALYSIS_TIERS` — and it is not decoration: `extractors/ocr_policy.py`
already reads the same split as `USABLE_METADATA_TIERS = frozenset({1, 2})`, so a literal `3` here
would be P6's copy of a boundary that exists in two places already. Both constants are **tuples**,
because Task 25 introspects every module namespace for a bare `int` or `float` and a band index is
not a threshold but is indistinguishable from one at run time.

**P5 spells the EXIF tag names and P6 holds no copy.** The skeleton's P5 table is explicit that a
camera / capture-time / GPS observation's container-path label is *"the reader-supplied tag name,
which P5 deliberately never spells"*. So the labels arrive inside `PhotoEventClustering.labels`,
keyed by `EVENT_INPUTS`, with no default — the same shape Task 14 uses for the perceptual-hash
label, and the same reason.

**The event is `validated`, and both boundaries are load-bearing.** Not `direct`: no explicit slot
states an event, and §3.13 reserves `direct` for a value read out of a reliable slot. Not
`possible`: P9 requires a seed fact to be Direct or Validated, so a `possible` event is a seed P9 can
never use and G7 would deliver nothing. `validated` is §3.13's own definition — a deterministic rule
that passes a contextual check — and the contextual check is the injected `same_event` predicate
agreeing that two files' camera, capture-time and GPS readings describe one occasion.

**A photograph with no EXIF gets no event and no `unresolved` row.** Same reading Tasks 14 and 15
apply: the SPEC's `unresolved` schema records *"the field that was attempted"*, and a file that
offered none of §4.2's three inputs was never proposed into a cluster. Recording it would make the
abstention table a list of every image in the corpus.

**`media_type` is the ordinary §3.7 procedure and not a new mechanism.** The SPEC is explicit:
*"Resolution is the ordinary §3.7 procedure over the `media type` field: each tiered observation is a
weighted vote for one candidate (`photograph` or `screenshot`), the candidates are ranked, and the
winner must clear both the minimum score and the minimum margin."* So this module builds candidates
and hands them to Task 11's `fill_or_abstain`, which owns the ranking, the two thresholds and the
`below_margin` / `below_score_threshold` rows. The tier-to-weight mapping is injected; §3.7's numbers
are Deferred and the SPEC files these with them (*"The tier-to-weight mapping is deferred with the
other §3.7 weights"*).

**The one rule §3.7's arithmetic cannot reach, stated rather than smuggled.** A file whose only
tiered observations are in the screenshot band fills nothing and gets `reason = below_margin`,
**before** any ranking runs. This is the single place Task 16 states a rule the injected thresholds
could otherwise override, so here is the whole argument:

- A07 is a P6 gate case (`dimension: "fact"`), its `expected_outcome_kind` is `"abstained"` and its
  `forbidden_value` is `{"field": "media_type", "value": "screenshot"}` — verified in
  `tests/eval/fixtures/adversarial/A07.json`. Its subject is a real photograph a messaging app
  stripped, which therefore carries only what every image carries.
- Left to the arithmetic, that file has one candidate (`screenshot`) and no second-best, so it clears
  any margin the caller injects and A07's forbidden value is produced. The outcome would depend on a
  Deferred number, which is not what a Done-means-grade prohibition may rest on.
- §2.6 states the prohibition directly and unconditionally — *"must not mistake the absence of EXIF
  for proof that an image is a screenshot"* — and the screenshot band is, in
  `ocr_policy`'s own words, *"what every image has"*. Evidence every image carries separates the two
  hypotheses by nothing, and a separation of nothing clears no margin.
- `below_margin` is the SPEC's own home for this: its reason table reads *"§3.7 margin over
  second-best not cleared — **including the conflicting-image-signal case (§2.6)**"*. It is not
  `no_candidate_evidence`, because there is a candidate and its observations are cited on the row.

**A missing signal contributes nothing to either candidate, and that is provable rather than
asserted.** P5 records "no EXIF" on `ExtractionRun.completeness` or nowhere — P4's `runs.py` says so
and conformance rule 12 enforces it — so no absence observation exists for this module to read. Every
candidate's score is a sum over observations that are present; there is no branch anywhere that
subtracts for one that is not.

**OCR text density is never a screenshot signal.** §2.6 rules it out by name. The guard is
structural rather than behavioural: this module imports nothing from `evidence_shape.store`, never
calls `unit_for_observation`, and holds no identifier containing `text` or `unit`. The test asserts
that by parsing the module, and pairs it with the behavioural case — an image with a large OCR text
unit and one tier-1 camera reading is still `photograph`.

**The event's name is a digest.** Consistent with Tasks 14 and 15 and for the same reason: an event
identifier built from a folder, a filename or a timestamp would put a path fragment or an
unvalidated parse inside a value. The canonical value is
`sha256_of(canonical_json(sorted(member file ids)))` — deterministic, member-derived, carrying
nothing about where the photographs sat. Adding a member renames the event, which is stated rather
than hidden.

- [ ] **Step 1: Write the failing test**

```python
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
from facts.file_facts import facts_for_file
from facts.photo_event import (
    EVENT_FIELD, EVENT_INPUTS, EVENT_STATE, MEDIA_TYPES, MEDIA_TYPE_FIELD,
    PHOTO_BANDS, SCREENSHOT_BAND, PhotoEventClustering, media_type, photo_events,
)
from facts.states import is_stronger
from facts.unresolved import unresolved_for_file

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
             analysis_tier="native", text_units=()):
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
    assert is_stronger("direct", EVENT_STATE)
    assert is_stronger(EVENT_STATE, "possible")


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
    assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


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
    assert [r["reason"] for r in rows] == ["below_margin"]


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
    assert [r["reason"] for r in rows] == ["below_margin"]
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_photo_event.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.photo_event'`

- [ ] **Step 3: Write `photo_event.py`**

```python
# src/facts/photo_event.py
"""G7 — §4.2's deterministic photo event, and §2.6's media-type conflict (M2).

§4.2, the only sentence in the design that states this fact exists:

    "For a photo group, it might be a deterministic event created from camera, time,
     and GPS metadata."

§2.6, the hierarchy this module READS and never rebuilds:

    "camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped
     dimensions reinforce it; exact display resolutions, PNG format, and software
     metadata may support a screenshot hypothesis; conflicting signals should lead to
     abstention rather than an invented classification."

**The tier is read, never re-derived (M2).** P4 puts `signal_tier` on the observation
for exactly this consumer, so this module branches on the integer and on nothing else
-- not on `extractor_name`, not on the container-path label. An observation P5 left
untiered contributes to nothing. Deriving the band from a name would encode §2.6 in a
second place, which is the defect M2 exists to prevent.

**The bands are P4's published order, read.** `SIGNAL_TIERS == (1, 2, 3)` and §2.6's
three bands arrive in that order, so the screenshot band is `SIGNAL_TIERS[-1:]` and
the photo bands are the rest. `extractors/ocr_policy.py` already reads the same split
as `USABLE_METADATA_TIERS`; a literal `3` here would be a third home for one boundary.
Both are tuples rather than ints because a band index is not a threshold and must not
look like one to Task 25's namespace introspection.

**P5 spells the EXIF tag names and this module holds no copy.** The tag name a
container-path label carries is "the reader-supplied tag name, which P5 deliberately
never spells", so the labels arrive inside the injected `PhotoEventClustering`.

**The event is `validated`.** Not `direct` -- no explicit slot states an event. Not
`possible` -- P9 requires a seed fact to be Direct or Validated, so a `possible` event
is a seed P9 can never use and G7 would deliver nothing.

**`media_type` is the ordinary §3.7 procedure.** Each tiered observation is one
weighted vote, the candidates are ranked by `facts.facets.fill_or_abstain`, and that
function owns the two thresholds and the `below_margin` row. One rule is applied
BEFORE the ranking, and it is the only rule here the injected numbers cannot override:
a file whose only tiered observations are in the screenshot band fills nothing.
§2.6 -- "the system must not mistake the absence of EXIF for proof that an image is a
screenshot" -- and the screenshot band is what every image carries, so it separates
the two hypotheses by nothing. `below_margin` is the SPEC's own home for §2.6's
abstention: "margin over second-best not cleared -- including the
conflicting-image-signal case (§2.6)".

**OCR text density is never a signal here.** §2.6 rules it out by name, and this
module imports nothing from `evidence_shape.store` and holds no identifier that could
reach a text unit.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Mapping

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, SIGNAL_TIERS, check

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.facets import Candidate, fill_or_abstain
from facts.file_facts import FACT_ORIGINS, write_fact
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.11's Photos fields, snake_case per D6. Both already exist in the catalogue, so
#: this module creates no field: §3.12 lets values auto-create and fields never.
EVENT_FIELD: str = "event"
MEDIA_TYPE_FIELD: str = "media_type"

#: §3.13's definition of `validated` -- a deterministic rule that passes a contextual
#: check -- and the contextual check is the injected `same_event` predicate.
EVENT_STATE: str = "validated"

#: §4.2's three inputs, in §4.2's order: "camera, time, and GPS metadata". These are
#: the KEYS the injected label sets arrive under, not the labels themselves.
EVENT_INPUTS: tuple[str, str, str] = ("camera", "capture_time", "location")

#: §2.6's two hypotheses, photograph first. There is no third and no "unknown"
#: member: not filling the field IS the third outcome, and it is a row (B7).
MEDIA_TYPES: tuple[str, str] = ("photograph", "screenshot")

#: §2.6's three bands, read off P4's published order rather than re-spelled. Tuples,
#: not ints: a band index is not a threshold and must not look like one to Task 25.
PHOTO_BANDS: tuple[int, ...] = SIGNAL_TIERS[:-1]
SCREENSHOT_BAND: tuple[int, ...] = SIGNAL_TIERS[-1:]


@dataclass(frozen=True)
class PhotoEventClustering:
    """§4.2's three inputs, and the thresholds the design states for none of them.

    Every field is required and none has a default.

    `labels` maps each member of `EVENT_INPUTS` to the container-path labels P5's
    reader used for that input. P5 spells the EXIF tag names and this module holds no
    copy, so the mapping is the injection site and `EVENT_INPUTS` is its one address.

    `same_event` receives two files' signal mappings -- each `{kind: sorted raw
    values}` over `EVENT_INPUTS` -- and answers whether they describe one occasion.
    The time window, the GPS radius and the camera-identity test are Deferred
    together; they arrive as this one predicate rather than as three numbers.

    `minimum_members` is how many photographs make an event. §4.2 uses the event as a
    GROUP seed and states no count, so the count is the caller's.
    """
    labels: Mapping[str, frozenset[str]]
    same_event: Callable[[Mapping[str, tuple[str, ...]],
                          Mapping[str, tuple[str, ...]]], bool]
    minimum_members: int

    def __post_init__(self) -> None:
        for kind in EVENT_INPUTS:
            check(kind, self.labels, name="event input")


@dataclass(frozen=True)
class _Photo:
    """One (file, content hash) with its §4.2 inputs already read once."""
    file_id: str
    content_hash: str
    observations: tuple[Observation, ...]
    cited: tuple[Observation, ...]
    signals: Mapping[str, tuple[str, ...]]

    @property
    def offered(self) -> bool:
        """Did this file offer any of §4.2's three inputs at all?"""
        return any(self.signals[kind] for kind in EVENT_INPUTS)


def _read(conn: sqlite3.Connection, file_ids: Iterable[str],
          clustering: PhotoEventClustering) -> tuple[_Photo, ...]:
    """Every version, in file-id order, with its signals resolved.

    Sorted before anything is decided. P4's reads are in insertion order (verified by
    execution) and insertion order is a property of one database, not of the corpus.
    """
    photos: list[_Photo] = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        content_hash = row["content_hash"]
        observations = tuple(observations_for_version(conn, file_id, content_hash))
        signals: dict[str, tuple[str, ...]] = {}
        cited: dict[str, Observation] = {}
        for kind in EVENT_INPUTS:
            labels = clustering.labels[kind]
            readings = tuple(
                one for one in observations
                if one.signal_tier in PHOTO_BANDS
                and any(segment.label in labels
                        for segment in one.location.container_path))
            signals[kind] = tuple(sorted(one.raw_value for one in readings))
            for one in readings:
                cited[cite(one)] = one
        photos.append(_Photo(
            file_id=file_id, content_hash=content_hash, observations=observations,
            cited=tuple(cited[key] for key in sorted(cited)), signals=signals))
    return tuple(photos)


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a fact built from several observations.

    §3.4 states one extractor version and one analysis tier; a fact citing several
    observations has several of each, and no task owns the reconciliation. The rule
    is written out here rather than shared because `facts.cache` is another task's
    module: the versions are the canonical JSON of the sorted distinct
    (name, version) pairs, and the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a fact that cited an `ocr` reading
    lands outside the cache slot the native pass computed under, which is what makes
    preamble rule 5's pass 4 supersede rather than overwrite.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {analysis_tier_for_observation(conn, one) for one in observations}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)


def photo_events(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                 clustering: PhotoEventClustering) -> Mapping[str, str]:
    """Done-means 26. `file_id -> fact_id` for every member of a photo event.

    An image that offered none of §4.2's three inputs gets no fact AND no `unresolved`
    row: the abstention record names "the field that was attempted", and a file that
    proposed nothing was never attempted. Recording it would make the abstention table
    a list of every image in the corpus.
    """
    photos = _read(conn, file_ids, clustering)
    by_id = {photo.file_id: photo for photo in photos}
    offered = sorted(photo.file_id for photo in photos if photo.offered)
    parent = {file_id: file_id for file_id in offered}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    for left, right in combinations(offered, 2):
        if clustering.same_event(by_id[left].signals, by_id[right].signals):
            parent[find(left)] = find(right)

    components: dict[str, list[str]] = {}
    for file_id in offered:
        components.setdefault(find(file_id), []).append(file_id)

    written: dict[str, str] = {}
    for members in sorted(components.values()):
        if len(members) < clustering.minimum_members:
            continue
        canonical_value = sha256_of(canonical_json(sorted(members)))
        for file_id in members:
            photo = by_id[file_id]
            refs = tuple(sorted(cite(one) for one in photo.cited))
            value_id = ensure_value(
                conn, field_key=EVENT_FIELD, canonical_value=canonical_value,
                first_evidence_ref=refs[0], origin=VALUE_ORIGINS[0])
            written[file_id] = write_fact(
                conn, file_id=file_id, content_hash=photo.content_hash,
                field_key=EVENT_FIELD, value_id=value_id,
                reliability_state=EVENT_STATE, origin=FACT_ORIGINS[1],
                evidence_refs=refs,
                cache_key=_cache_key(conn, content_hash=photo.content_hash,
                                     observations=photo.cited),
                active=True)
    return written


def _abstain(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
             reason: str, considered: tuple[Observation, ...]) -> None:
    """B7: a refusal is a row naming the field, the reason, and what it looked at."""
    write_unresolved(
        conn, file_id=file_id, content_hash=content_hash,
        field_key=MEDIA_TYPE_FIELD, reason=reason,
        attempted_producers=(ATTEMPTED_PRODUCERS[1],),
        evidence_refs=tuple(sorted(cite(one) for one in considered)),
        cache_key=_cache_key(conn, content_hash=content_hash,
                             observations=considered))


def media_type(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               tier_weight: Mapping[int, float], minimum_score: float,
               minimum_margin: float) -> str | None:
    """Done-means 27. §2.6's two hypotheses, ranked by §3.7's ordinary procedure.

    Every tiered observation is one weighted vote: the screenshot band votes
    `screenshot`, every other band votes `photograph`. The weights are injected --
    §3.7's numbers are Deferred and the SPEC files the tier-to-weight mapping with
    them -- and the ranking, the score floor, the margin and the two refusal rows they
    produce all belong to `facts.facets.fill_or_abstain`.

    Two refusals happen here rather than there, and each is a sentence of §2.6:

    * no tiered observation at all -> `no_candidate_evidence`. Nothing was read about
      this image, so there is nothing to rank and nothing to cite (rule 1).
    * only screenshot-band observations -> `below_margin`. "The system must not
      mistake the absence of EXIF for proof that an image is a screenshot", and that
      band is what EVERY image carries, so it separates the two hypotheses by nothing.
      Left to the arithmetic this file has one candidate, no second-best, and clears
      any injected margin -- which is exactly A07's forbidden value. The reason is
      §2.6's own: the SPEC files "the conflicting-image-signal case (§2.6)" under
      `below_margin`.
    """
    observations = tuple(observations_for_version(conn, file_id, content_hash))
    tiered = tuple(one for one in observations if one.signal_tier in SIGNAL_TIERS)
    if not tiered:
        _abstain(conn, file_id=file_id, content_hash=content_hash,
                 reason="no_candidate_evidence", considered=())
        return None
    if all(one.signal_tier in SCREENSHOT_BAND for one in tiered):
        _abstain(conn, file_id=file_id, content_hash=content_hash,
                 reason="below_margin", considered=tiered)
        return None

    candidates: list[Candidate] = []
    for value, band in ((MEDIA_TYPES[0], PHOTO_BANDS),
                        (MEDIA_TYPES[1], SCREENSHOT_BAND)):
        voters = tuple(one for one in tiered if one.signal_tier in band)
        if not voters:
            # A candidate with nothing to cite is not a candidate (rule 1). It is
            # also not a subtraction: a signal P5 never wrote moves neither side.
            continue
        candidates.append(Candidate(
            value=value,
            score=sum(tier_weight[one.signal_tier] for one in voters),
            evidence_refs=tuple(sorted(cite(one) for one in voters))))

    return fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash,
        field_key=MEDIA_TYPE_FIELD, candidates=tuple(candidates),
        minimum_score=minimum_score, minimum_margin=minimum_margin)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_photo_event.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/photo_event.py tests/p6/test_p6_photo_event.py
git commit -m "feat(P6): G7 photo events and the media-type conflict — the tier is read, never re-derived"
```

---

### Wave D — the seams (17–23 parallelise)

### Task 17: The P8 seam — what P6 supplies, and the consequence of each verdict (O6)

**Files:**
- Create: `src/facts/llm_seam.py`
- Test: `tests/p6/test_p6_llm_seam.py`

**Interfaces:**
- Consumes: `facts.domains` — `active_field_allowlist`; `facts.evidence` —
  `observations_for_version`, `cite`, `analysis_tier_for_observation`; `facts.file_facts` —
  `facts_for_file`, `write_fact`, `FACT_ORIGINS`, `FieldNotInCatalogue` (raised through
  `write_fact`); `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`; `facts.values` —
  `ensure_value`, `VALUE_ORIGINS`; `facts.states` — `is_stronger`; `facts.cache.fact_cache_key`;
  `evidence_shape.canonical` — `canonical_json`; `evidence_shape.vocabulary` — `ANALYSIS_TIERS`,
  `check`, `NotInVocabulary`.
- Produces (`llm_seam.py`): `FOUR_CHECKS: tuple[str, ...]`, `CHECK_REASONS: Mapping[str, str]`,
  `UNKNOWN_REASON: str`, `LLM_STATES: tuple[str, str]`, `ProposalStateRefused(ValueError)`,
  `require_llm_state(reliability_state) -> str`,
  `FactRequest(file_id, content_hash, allowlist, citable_observations, existing_facts, normalizers)`,
  `Proposal(field_key, value, citations, unknown)`, `Verdict(passed, failed_check, reason)`,
  `build_request(conn, *, file_id, content_hash, activation_signals, normalizers) -> FactRequest`,
  `apply_verdict(conn, *, request, proposal, verdict, proposal_state, model_identifier,
  prompt_fingerprint) -> str | None`.

> **Additions to the skeleton's `Produces:` line, declared.** `CHECK_REASONS`, `UNKNOWN_REASON`,
> `LLM_STATES`, `ProposalStateRefused` and `require_llm_state` are added. The first two exist because
> the check-to-reason map is a closed correspondence that would otherwise be spelled once in the
> module and once in P8; the last three exist because §3.6's *"useful but too weak"* downgrade is a
> reliability-state choice that must be enforced at a function a test can call, which is Task 15's
> `require_possible` pattern applied to the one other place a state ceiling binds. `apply_verdict`
> and `build_request` fill in the skeleton's `...` with named keywords; no name it states is renamed.

**Done-means:** 11, 12, and the P8-absent half of 17.

**§3.6, quoted in full, because the four checks and the two outcomes are all in it:**

> Every LLM-produced fact must pass a validation step before it becomes active in the database. The validator checks that the proposed field exists in the relevant domain schema, that the model’s cited quote or metadata field is actually present in the stored evidence, that the proposed value can be normalized safely, and that no stronger direct or rule-validated fact contradicts it. A model that cannot cite sufficient evidence must return unknown. A model output that is useful but too weak to establish a fact may remain a possible clue for review; it must not quietly become a folder proposal or an asserted file property.

**P6 supplies the four inputs and owns none of the checking.** `apply_verdict` takes a `Verdict` it
did not compute. That is not a convenience — it is what lets P8 be built against this shape later
without P6 being rewritten, and it is what the skeleton states. The consequence is that a **passing**
verdict over a proposal citing a key absent from the evidence still writes a fact, and the test below
drives exactly that case and asserts the fact appears. Anything else would mean P6 re-ran a check it
does not own, and the two implementations would drift.

**One floor is not left to the verdict, and it is not P6 doing P8's job.** §3.12 and §3.5 are
absolute — *"The LLM is not allowed to invent a new fact schema, create an unsupported field"* — and
the field catalogue is closed at Task 2. So a passing verdict naming a field outside the catalogue
raises `FieldNotInCatalogue` through `write_fact`, not because this module checked anything but
because there is no row to point at. The allowlist is narrower than the catalogue and *is* left to
the verdict: it is check 1's input, and check 1 is P8's.

> ## ⚠ An unresolved seam: `normalize` and `contradicts` have no owner (round 4, C-5)
>
> **This must be decided before P8 is planned. It is not closed here and this task does not pick a
> side.**
>
> P8's SPEC, under *From P6 — facts and facets (§3.1–3.14)*, names four things it receives from P6.
> Two of them are functions, quoted verbatim from `planning/parts/P8-llm-harness-validator/SPEC.md`:
>
> > - A normalizer: `normalize(field, raw_value) -> value | not_normalizable` (§3.6), including the
> >   gazetteer and word-boundary discipline (§3.7).
> > - A contradiction oracle: `contradicts(claim, existing_fact) -> bool`.
>
> And P8's own Deferred table files the same pair back the other way:
>
> > | **The `contradicts()` and normalization predicates' domain logic** | §3.6, §3.7, P6 | P8 calls them; P6 defines what contradiction means per field |
>
> P6's Task 17, meanwhile, says P6 *"supplies the four inputs and owns none of the checking"*. So
> **each part hands these two functions to the other and neither builds them.** A gap of this shape
> does not surface at integration; it surfaces when P8's validator has no `contradicts` to call and
> someone writes one in a hurry, in P8, where P6's field semantics are not available.
>
> **What this task does about it, and what it deliberately does not.**
>
> - It supplies the four *inputs*, exactly as the skeleton says: the active field allowlist, the
>   citable observation set, the existing `direct`/`validated`/`user_confirmed` facts, and the
>   per-field normalizers as **injected data the request carries**. P6 authors none of the
>   normalizers' contents — the SPEC's Deferred table already holds *"Per-field normalizers and
>   alias tables"* open, with `U Chicago → University of Chicago → UChicago` named as *"one worked
>   example, not a table"*.
> - It builds **neither** `normalize` **nor** `contradicts`. Inventing them into `facts.llm_seam`
>   would answer a live question inside an implementation, which is the failure mode this plan
>   exists to avoid, and would make the gap invisible rather than closed.
> - It **pins P6's side in code** so the gap is visible from the repository and not only from a
>   document: a test asserts that no module in `facts` publishes a `normalize` or a `contradicts`.
>   The day someone adds one, that test fails and the decision gets made deliberately.
>
> **Owed:** a ruling on which part owns `normalize(field, raw_value)` and
> `contradicts(claim, existing_fact)`, before P8 is planned. If the answer is P6, it is a new P6
> task and not an edit to this one — the request shape above is unchanged either way, because both
> functions would be called by P8 on values this request already carries.

**Five verdicts, five reasons, and no shared bucket.** `Verdict` carries `passed`, the
`failed_check` that failed, and the P6 `unresolved` reason that follows from it. The reason is
**derived** in `__post_init__` from `CHECK_REASONS`, not supplied: P6 owns the `unresolved`
vocabulary and P8 must not spell a member of it. The fifth outcome is not a check at all — an
explicit `unknown` is the model declining before anything could be validated, so `apply_verdict`
records `model_returned_unknown` and never consults the verdict. `Proposal.__post_init__` refuses an
`unknown` proposal that also carries a value or citations, so "declined" and "proposed" cannot both
be true of one record.

**The useful-but-too-weak downgrade is a ceiling at a function.** §3.6's *"may remain a possible clue
for review; it must not quietly become a folder proposal"* is a statement about every route, so
`require_llm_state` is the only gate to an LLM-origin fact and it admits exactly `llm_supported` and
`possible`. A test attempts `validated` and requires the raise. Which of the two a given proposal
earns is §3.7's score-and-margin question and is Deferred, so `proposal_state` is a required keyword
with no default — P6 states no rule for how weak "too weak" is.

**Being `possible` is what keeps it out of a folder proposal, and that is by construction.** Same
mechanism as Task 15's session: §3.6's proposal-eligible read excludes `possible` and `rejected`, so
the downgrade *is* the exclusion. There is no second switch.

**The LLM fact's cache key is the one in this file that is not all-`None`.** §3.4's five parts are
`content hash + extractor version + analysis tier + model identifier + prompt fingerprint`, and P8's
SPEC states who supplies the last two: *"P8 computes and publishes the `prompt_fingerprint` and
`model_id` that P6's cache key requires; P6 owns cache-key composition."* So both arrive as required
keywords, and `analysis_tier` is `ANALYSIS_TIERS[-1]` — `llm` — unconditionally, because an
LLM-produced fact is at the LLM tier by definition. That is what puts it in a different cache slot
from the deterministic fact over the same evidence, so re-resolution supersedes rather than
overwrites (§8.2).

**All of it runs with P8 absent.** There is no model call, no client, no configuration and no
default `propose`. The whole module is exercised with hand-authored `Verdict` fixtures, which is
Done-means 17's shape and is exactly how P5 was built against P4 fixtures.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_llm_seam.py
"""O6 — Done-means 11 and 12. What P6 hands P8, and the consequence of each verdict."""
from __future__ import annotations

import dataclasses
import importlib
import importlib.util
import inspect
import json
import pkgutil
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

import facts
from facts import llm_seam
from facts.domains import ActivationSignals
from facts.fields import FieldNotInCatalogue
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact
from facts.llm_seam import (
    CHECK_REASONS, FOUR_CHECKS, LLM_STATES, UNKNOWN_REASON, FactRequest, Proposal,
    ProposalStateRefused, Verdict, apply_verdict, build_request, require_llm_state,
)
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"
MODEL = "test-model-1"
PROMPT = "sha256:prompt-fingerprint"

#: The empty value of each declared type, used to build an `ActivationSignals` that
#: activates nothing. Task 13 owns that type's shape and this test must not hard-code
#: one it does not own, so each field is filled from its own annotation.
_EMPTY = {"tuple": (), "frozenset": frozenset(), "set": frozenset(), "dict": {},
          "Mapping": {}, "list": [], "str": "", "bool": False, "int": 0}


def _no_signals() -> ActivationSignals:
    """An `ActivationSignals` that activates no domain, built from its own fields."""
    values = {}
    for field in dataclasses.fields(ActivationSignals):
        head = str(field.type).split("[")[0].split(".")[-1].strip("'\" ")
        assert head in _EMPTY, f"ActivationSignals.{field.name}: {field.type!r}"
        values[field.name] = _EMPTY[head]
    return ActivationSignals(**values)


#: The per-field normalizers the request CARRIES. P6 authors none of their contents:
#: "Per-field normalizers and alias tables" is a Deferred row, and `U Chicago ->
#: University of Chicago -> UChicago` is "one worked example, not a table".
NORMALIZERS = {"subject": lambda raw: raw.strip()}


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label="heading"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before="Syllabus — ")
    record_observation(conn, observation)
    return observation.observation_key


@pytest.fixture()
def subject_file(p6_conn, tmp_path):
    """One file with one citable heading observation."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300 Syllabus, Spring 2026")
    key = _observe(p6_conn, run_id="r-1", file_id=file_id,
                   content_hash=content_hash, raw="BUSIB 4300")
    return file_id, content_hash, key


def _request(conn, subject_file) -> FactRequest:
    file_id, content_hash, _ = subject_file
    return build_request(conn, file_id=file_id, content_hash=content_hash,
                         activation_signals=_no_signals(), normalizers=NORMALIZERS)


def _apply(conn, request, proposal, verdict, *, state=LLM_STATES[0]):
    return apply_verdict(conn, request=request, proposal=proposal, verdict=verdict,
                         proposal_state=state, model_identifier=MODEL,
                         prompt_fingerprint=PROMPT)


def _reasons(conn, request, field_key=None):
    return [r["reason"] for r in unresolved_for_file(
        conn, request.file_id, request.content_hash, field_key=field_key)]


def test_the_request_carries_the_four_inputs_and_nothing_else(subject_file, p6_conn):
    # O6. The four are the active field allowlist, the citable observation set, the
    # existing stronger facts, and the per-field normalizers.
    file_id, content_hash, key = subject_file
    request = _request(p6_conn, subject_file)
    assert [f.name for f in dataclasses.fields(FactRequest)] == [
        "file_id", "content_hash", "allowlist", "citable_observations",
        "existing_facts", "normalizers"]
    assert request.file_id == file_id and request.content_hash == content_hash
    assert "subject" in request.allowlist
    assert [one.observation_key for one in request.citable_observations] == [key]
    assert request.normalizers is NORMALIZERS
    assert request.existing_facts == ()


def test_the_allowlist_is_task_thirteens_and_not_a_second_computation(
        subject_file, p6_conn):
    # §3.5: the model "may extract only fields allowed by the relevant schema". The
    # skeleton requires that to be ONE computation, so the request holds Task 13's
    # answer rather than a second reading of the catalogue.
    from facts.domains import active_field_allowlist
    file_id, content_hash, _ = subject_file
    signals = _no_signals()
    request = build_request(p6_conn, file_id=file_id, content_hash=content_hash,
                            activation_signals=signals, normalizers=NORMALIZERS)
    assert request.allowlist == active_field_allowlist(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=signals)


def test_the_request_carries_the_stronger_facts_a_contradiction_check_needs(
        subject_file, p6_conn):
    # §3.6 check 4: "no stronger direct or rule-validated fact contradicts it". P6
    # supplies the facts; whether one CONTRADICTS is not computed here (see C-5).
    file_id, content_hash, key = subject_file
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="BUSIB 4300",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="validated", origin=FACT_ORIGINS[1],
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    request = _request(p6_conn, subject_file)
    assert [r["reliability_state"] for r in request.existing_facts] == ["validated"]


def test_a_citation_absent_from_evidence_produces_no_fact(subject_file, p6_conn):
    # Done-means 11, and §3.6 check 2.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=("sha256:not-in-the-store",), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[1])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == ["citation_absent_from_evidence"]


def test_a_field_outside_the_active_schema_produces_no_fact(subject_file, p6_conn):
    # Done-means 11, and §3.6 check 1.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="event", value="Graduation",
                        citations=(subject_file[2],), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[0])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == ["field_not_in_active_schema"]


def test_a_proposal_contradicted_by_a_stronger_fact_produces_no_fact(
        subject_file, p6_conn):
    # Done-means 11, and §3.6 check 4. The stronger fact is real and is in the
    # request; the VERDICT is the fixture, because P6 owns no contradiction oracle.
    file_id, content_hash, key = subject_file
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="BUSIB 4300",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="validated", origin=FACT_ORIGINS[1],
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="ECON 1010",
                        citations=(key,), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[3])
    assert _apply(p6_conn, request, proposal, verdict) is None
    subjects = [r for r in facts_for_file(p6_conn, file_id, content_hash)
                if r["field_key"] == "subject"]
    assert [r["canonical_value"] for r in subjects] == ["BUSIB 4300"]
    assert _reasons(p6_conn, request) == ["contradicted_by_stronger_fact"]


def test_a_value_that_cannot_be_normalized_produces_no_fact(subject_file, p6_conn):
    # §3.6 check 3: "that the proposed value can be normalized safely".
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="  ??  ",
                        citations=(subject_file[2],), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[2])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert _reasons(p6_conn, request) == ["normalization_failed"]


def test_an_explicit_unknown_is_the_model_declining_and_not_a_failed_check(
        subject_file, p6_conn):
    # §3.6: "A model that cannot cite sufficient evidence must return unknown."
    # Nothing was validated, so no verdict is consulted.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value=None, citations=(), unknown=True)
    assert _apply(p6_conn, request, proposal,
                  Verdict(passed=True, failed_check=None)) is None
    assert _reasons(p6_conn, request) == [UNKNOWN_REASON]
    assert UNKNOWN_REASON == "model_returned_unknown"
    # And "declined" and "proposed" cannot both be true of one record.
    with pytest.raises(ValueError):
        Proposal(field_key="subject", value="BUSIB 4300",
                 citations=("sha256:x",), unknown=True)


def test_five_verdicts_have_five_distinct_reasons_and_no_shared_bucket():
    assert FOUR_CHECKS == ("field_in_active_schema", "citation_present_in_evidence",
                           "value_normalizes_safely", "no_stronger_fact_contradicts")
    assert tuple(CHECK_REASONS[check] for check in FOUR_CHECKS) == (
        "field_not_in_active_schema", "citation_absent_from_evidence",
        "normalization_failed", "contradicted_by_stronger_fact")
    reasons = set(CHECK_REASONS.values()) | {UNKNOWN_REASON}
    assert len(reasons) == 5
    assert "rejected" not in reasons
    # The reason follows from the check; P8 does not spell a member of P6's
    # vocabulary, and a check outside the four is refused rather than stored.
    assert Verdict(passed=False, failed_check=FOUR_CHECKS[2]).reason == (
        "normalization_failed")
    with pytest.raises(NotInVocabulary):
        Verdict(passed=False, failed_check="vibes")
    with pytest.raises(ValueError):
        Verdict(passed=True, failed_check=FOUR_CHECKS[0])
    with pytest.raises(ValueError):
        Verdict(passed=False, failed_check=None)


def test_a_passing_verdict_writes_one_llm_supported_fact(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    fact_id = _apply(p6_conn, request, proposal, Verdict(passed=True))
    assert fact_id is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert len(rows) == 1
    assert rows[0]["reliability_state"] == LLM_STATES[0] == "llm_supported"
    assert rows[0]["origin"] == FACT_ORIGINS[2]
    assert json.loads(rows[0]["evidence_refs"]) == [subject_file[2]]
    assert unresolved_for_file(p6_conn, request.file_id,
                               request.content_hash) == []


def test_a_useful_but_too_weak_proposal_is_possible_and_never_proposal_eligible(
        subject_file, p6_conn):
    # Done-means 12. §3.6: it "may remain a possible clue for review; it must not
    # quietly become a folder proposal or an asserted file property". The exclusion
    # IS the state — §3.6's proposal-eligible read drops `possible` — so there is no
    # second switch and nothing to remember to turn off.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    assert _apply(p6_conn, request, proposal, Verdict(passed=True),
                  state=LLM_STATES[1]) is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert [r["reliability_state"] for r in rows] == ["possible"]
    read_surface = pytest.importorskip("facts.read_surface")
    eligible = read_surface.proposal_eligible(p6_conn, file_id=request.file_id,
                                              content_hash=request.content_hash)
    assert [r["field_key"] for r in eligible] == []


def test_no_code_path_can_write_an_llm_fact_at_another_state(subject_file, p6_conn):
    # §3.6's ceiling, attempted rather than inspected — Task 15's `require_possible`
    # applied to the one other place a state ceiling binds.
    assert LLM_STATES == ("llm_supported", "possible")
    for state in LLM_STATES:
        assert require_llm_state(state) == state
    for state in ("validated", "direct", "user_confirmed", "rejected"):
        with pytest.raises(ProposalStateRefused):
            require_llm_state(state)
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    with pytest.raises(ProposalStateRefused):
        _apply(p6_conn, request, proposal, Verdict(passed=True), state="validated")
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []


def test_p6_owns_none_of_the_checking(subject_file, p6_conn):
    # O6, and the reason the seam is shaped this way: `apply_verdict` takes a
    # `Verdict` it did not compute, so a PASSING verdict over a proposal citing a key
    # that is not in the store still writes a fact. If P6 re-ran the check, P6 and P8
    # would each hold half a validator and they would drift.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="ANYTHING",
                        citations=("sha256:not-in-the-store",), unknown=False)
    assert _apply(p6_conn, request, proposal, Verdict(passed=True)) is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert [r["canonical_value"] for r in rows] == ["ANYTHING"]


def test_the_closed_field_catalogue_is_the_one_floor_a_verdict_cannot_lift(
        subject_file, p6_conn):
    # §3.5: the LLM "is not allowed to invent a new fact schema, create an
    # unsupported field". That is not this module checking anything — there is no row
    # to point at, so `write_fact` refuses.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="vibe_score", value="9",
                        citations=(subject_file[2],), unknown=False)
    with pytest.raises(FieldNotInCatalogue):
        _apply(p6_conn, request, proposal, Verdict(passed=True))


def test_the_llm_fact_lands_at_the_llm_tier_with_p8s_two_values(
        subject_file, p6_conn):
    # §3.4's five parts. P8's SPEC: "P8 computes and publishes the
    # `prompt_fingerprint` and `model_id` that P6's cache key requires; P6 owns
    # cache-key composition." Both are required keywords here.
    signature = inspect.signature(apply_verdict)
    for name in ("proposal_state", "model_identifier", "prompt_fingerprint"):
        parameter = signature.parameters[name]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is inspect.Parameter.empty
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    deterministic_key = "sha256:the-native-pass-slot"
    fact_id = _apply(p6_conn, request, proposal, Verdict(passed=True))
    row = [r for r in facts_for_file(p6_conn, request.file_id,
                                     request.content_hash)
           if r["fact_id"] == fact_id][0]
    assert row["cache_key"] != deterministic_key
    assert ANALYSIS_TIERS[-1] == "llm"


def test_p6_publishes_neither_a_normalizer_nor_a_contradiction_oracle():
    """Round 4's C-5, pinned in code so the gap is visible from the repository.

    P8's SPEC names `normalize(field, raw_value) -> value | not_normalizable` and
    `contradicts(claim, existing_fact) -> bool` as things it receives FROM P6; P6's
    Task 17 says P6 owns none of the checking. Each part hands them to the other, so
    neither builds them. This task does not pick a side and does not invent them —
    it makes the day someone quietly adds one a failing test instead of a merge.
    """
    for owner in (llm_seam,):
        assert not hasattr(owner, "normalize")
        assert not hasattr(owner, "contradicts")
    for info in pkgutil.iter_modules(facts.__path__):
        module = importlib.import_module(f"facts.{info.name}")
        assert not hasattr(module, "normalize"), info.name
        assert not hasattr(module, "contradicts"), info.name


def test_the_whole_module_runs_with_p8_absent():
    # Done-means 17. No client, no model call, no configuration, no default
    # `propose`. Every verdict above was a hand-authored fixture.
    source = inspect.getsource(llm_seam)
    assert "propose" not in source
    for banned in ("http", "openai", "anthropic", "requests", "urllib", "socket"):
        assert banned not in source.lower(), banned
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_llm_seam.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.llm_seam'`

- [ ] **Step 3: Write `llm_seam.py`**

```python
# src/facts/llm_seam.py
"""O6 — what P6 hands P8, and the consequence of each verdict (§3.3, §3.5, §3.6).

§3.6, and every clause of it binds here:

    "Every LLM-produced fact must pass a validation step before it becomes active in
     the database. The validator checks that the proposed field exists in the relevant
     domain schema, that the model's cited quote or metadata field is actually present
     in the stored evidence, that the proposed value can be normalized safely, and
     that no stronger direct or rule-validated fact contradicts it. A model that
     cannot cite sufficient evidence must return unknown. A model output that is
     useful but too weak to establish a fact may remain a possible clue for review; it
     must not quietly become a folder proposal or an asserted file property."

**P6 supplies the four inputs and owns none of the checking.** `apply_verdict` takes a
`Verdict` it did not compute. A PASSING verdict over a proposal citing a key that is
not in the store therefore writes a fact -- deliberately, because the alternative is
P6 and P8 each holding half a validator and drifting apart. P8 can be built against
this shape without this module changing.

**One floor is not left to the verdict.** §3.5: the LLM "is not allowed to invent a
new fact schema, create an unsupported field". The field catalogue is closed, so a
passing verdict naming a field outside it raises `FieldNotInCatalogue` through
`write_fact` -- not because this module checked, but because there is no row to point
at. The ALLOWLIST is narrower than the catalogue and is check 1's input, which is
P8's.

**UNRESOLVED SEAM (round 4, C-5) -- do not close it here.** P8's SPEC names two
functions as P6's: a normalizer `normalize(field, raw_value) -> value |
not_normalizable` and a contradiction oracle `contradicts(claim, existing_fact) ->
bool`. P8's own Deferred table files their domain logic back to P6, and P6's task says
P6 owns none of the checking -- so each part hands them to the other and neither
builds them. This module supplies the four INPUTS (allowlist, citable observations,
existing stronger facts, per-field normalizers as injected data) and publishes NEITHER
function. A test asserts no module in `facts` publishes one, so the day someone adds
it, the decision gets made rather than absorbed. The ruling is owed before P8 is
planned.

**Five verdicts, five reasons, no shared bucket.** The reason is derived from the
failed check rather than supplied, because P6 owns the `unresolved` vocabulary and P8
must not spell a member of it. The fifth outcome is not a check at all: an explicit
`unknown` is the model declining before anything could be validated.

**The ceiling is a function, not a call site.** `require_llm_state` is the only gate to
an LLM-origin fact and admits exactly `llm_supported` and `possible`, so a test can
attempt the promotion and require the raise. Which of the two a proposal earns is
§3.7's score-and-margin question and is Deferred, so `proposal_state` is required with
no default.

**There is no model call here, and no default for one.** §3.3 puts every model call in
P8. `analysis_tier = "llm"` is a value recorded on a cache key, never a call.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from evidence_shape.canonical import canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from facts.cache import fact_cache_key
from facts.domains import active_field_allowlist
from facts.evidence import cite, observations_for_version
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact
from facts.states import is_stronger
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.6's four, in §3.6's own order. These are names for the CHECKS, which are P8's;
#: P6 publishes them so both parts address one list.
FOUR_CHECKS: tuple[str, ...] = (
    "field_in_active_schema",
    "citation_present_in_evidence",
    "value_normalizes_safely",
    "no_stronger_fact_contradicts",
)

#: The one correspondence between P8's checks and P6's `unresolved` reasons. It lives
#: here because P6 owns the reason vocabulary: a `Verdict` names the check that
#: failed, never the reason, so P8 never spells a member of P6's closed set.
CHECK_REASONS: Mapping[str, str] = {
    FOUR_CHECKS[0]: "field_not_in_active_schema",
    FOUR_CHECKS[1]: "citation_absent_from_evidence",
    FOUR_CHECKS[2]: "normalization_failed",
    FOUR_CHECKS[3]: "contradicted_by_stronger_fact",
}

#: The fifth outcome, and it is not a check: §3.6's "A model that cannot cite
#: sufficient evidence must return unknown" is the model declining before anything
#: could be validated.
UNKNOWN_REASON: str = "model_returned_unknown"

#: The only two states an LLM-origin fact may carry. §3.13 gives `llm_supported` to a
#: model conclusion that passed validation; §3.6 gives `possible` to one that is
#: "useful but too weak to establish a fact". Which of the two is §3.7's question and
#: is Deferred, so nothing here chooses between them.
LLM_STATES: tuple[str, str] = ("llm_supported", "possible")


class ProposalStateRefused(ValueError):
    """§3.6's ceiling, raised rather than documented."""


def require_llm_state(reliability_state: str) -> str:
    """The only gate to an LLM-origin fact.

    §3.6: a model output "must not quietly become a folder proposal or an asserted
    file property". That is a statement about every route, so it is enforced where
    every route has to pass rather than at the one call this module makes.
    """
    if reliability_state not in LLM_STATES:
        raise ProposalStateRefused(
            f"§3.6 admits an LLM-origin fact at {LLM_STATES!r} only; "
            f"{reliability_state!r} would give a model conclusion the standing of a "
            "directly extracted or rule-validated fact")
    return reliability_state


@dataclass(frozen=True)
class FactRequest:
    """The four inputs P6 supplies for one file version. P8 consumes; P6 checks none.

    `normalizers` is carried, not called. Per-field normalizers and alias tables are a
    Deferred row -- `U Chicago -> University of Chicago -> UChicago` is "one worked
    example, not a table" -- so P6 authors none of the contents and injects the whole
    mapping. See the C-5 note in the module docstring: `normalize` as a FUNCTION has
    no owner in either part's plan.
    """
    file_id: str
    content_hash: str
    allowlist: tuple[str, ...]
    citable_observations: tuple[Observation, ...]
    existing_facts: tuple[sqlite3.Row, ...]
    normalizers: Mapping[str, Callable[[str], Any]]


@dataclass(frozen=True)
class Proposal:
    """One thing the model said about one field, or its refusal to say anything."""
    field_key: str | None
    value: str | None
    citations: tuple[str, ...]
    unknown: bool

    def __post_init__(self) -> None:
        if self.unknown and (self.value is not None or self.citations):
            raise ValueError(
                "an `unknown` proposal is the model declining (§3.6); it carries no "
                "value and no citations, so 'declined' and 'proposed' cannot both be "
                "true of one record")
        if not self.unknown and self.value is None:
            raise ValueError("a proposal that is not `unknown` carries a value")


@dataclass(frozen=True)
class Verdict:
    """P8's answer for one proposal. P6 records the consequence and computes none.

    `reason` is DERIVED from `failed_check`, not supplied: the `unresolved` vocabulary
    is P6's and P8 must not spell a member of it.
    """
    passed: bool
    failed_check: str | None = None
    reason: str | None = field(default=None)

    def __post_init__(self) -> None:
        if self.passed and self.failed_check is not None:
            raise ValueError("a verdict that passed names no failed check")
        if not self.passed and self.failed_check is None:
            raise ValueError(
                "a verdict that failed names WHICH of §3.6's four checks failed; "
                "five verdicts carry five reasons and there is no shared bucket")
        if self.failed_check is not None:
            check(self.failed_check, FOUR_CHECKS, name="failed_check")
            object.__setattr__(self, "reason", CHECK_REASONS[self.failed_check])


def build_request(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                  activation_signals: Any,
                  normalizers: Mapping[str, Callable[[str], Any]]) -> FactRequest:
    """The four inputs, for one file version.

    The allowlist is Task 13's answer, not a second reading of the catalogue: §3.5's
    "may extract only fields allowed by the relevant schema" must be ONE computation,
    or the model is measured against one list and validated against another.

    `existing_facts` is every active fact stronger than an LLM conclusion --
    `user_confirmed`, `direct`, `validated` -- derived through `is_stronger` rather
    than listed, so §3.13's ordering has one home. These are check 4's input. Whether
    any of them CONTRADICTS a proposal is not decided here (C-5).
    """
    return FactRequest(
        file_id=file_id,
        content_hash=content_hash,
        allowlist=tuple(active_field_allowlist(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=activation_signals)),
        citable_observations=tuple(
            observations_for_version(conn, file_id, content_hash)),
        existing_facts=tuple(
            row for row in facts_for_file(conn, file_id, content_hash)
            if is_stronger(row["reliability_state"], LLM_STATES[0])),
        normalizers=normalizers)


def _cache_key(request: FactRequest, proposal: Proposal, *, model_identifier: str,
               prompt_fingerprint: str) -> str:
    """§3.4's five parts for an LLM-produced fact.

    The tier is `ANALYSIS_TIERS[-1]` unconditionally: an LLM-produced fact is at the
    LLM tier by definition, which is what puts it in a different cache slot from the
    deterministic fact over the same evidence, so re-resolution supersedes rather than
    overwrites (§8.2).

    The versions are the canonical JSON of the sorted distinct (name, version) pairs
    of the observations the proposal CITES, on the same rule the deterministic
    producers apply, so a re-extraction still invalidates this fact. A citation that
    matches nothing contributes no pair -- this module checks citations no more here
    than anywhere else.
    """
    keys = set(proposal.citations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in request.citable_observations if cite(one) in keys})
    return fact_cache_key(
        content_hash=request.content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=ANALYSIS_TIERS[-1],
        model_identifier=model_identifier,
        prompt_fingerprint=prompt_fingerprint)


def apply_verdict(conn: sqlite3.Connection, *, request: FactRequest,
                  proposal: Proposal, verdict: Verdict, proposal_state: str,
                  model_identifier: str, prompt_fingerprint: str) -> str | None:
    """Done-means 11 and 12. The consequence of one verdict, and never the check.

    Returns the new `fact_id`, or `None` when nothing was written -- in which case an
    `unresolved` row names the field and the reason (B7). Five outcomes, five reasons,
    no shared "rejected" bucket:

        unknown                         model_returned_unknown
        check 1 failed                  field_not_in_active_schema
        check 2 failed                  citation_absent_from_evidence
        check 3 failed                  normalization_failed
        check 4 failed                  contradicted_by_stronger_fact

    The `unknown` branch is taken BEFORE the verdict is read: the model declined, so
    there was nothing to validate and a verdict about it would be a statement nobody
    made.
    """
    cache_key = _cache_key(request, proposal, model_identifier=model_identifier,
                           prompt_fingerprint=prompt_fingerprint)

    def refuse(reason: str) -> None:
        write_unresolved(
            conn, file_id=request.file_id, content_hash=request.content_hash,
            field_key=proposal.field_key, reason=reason,
            attempted_producers=(ATTEMPTED_PRODUCERS[2],),
            evidence_refs=tuple(proposal.citations), cache_key=cache_key)

    if proposal.unknown:
        refuse(UNKNOWN_REASON)
        return None
    if not verdict.passed:
        refuse(verdict.reason)
        return None

    # The state is gated before anything is written, so a refused promotion leaves no
    # value row behind either.
    reliability_state = require_llm_state(proposal_state)
    value_id = ensure_value(
        conn, field_key=proposal.field_key, canonical_value=proposal.value,
        first_evidence_ref=proposal.citations[0] if proposal.citations else None,
        origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=request.file_id, content_hash=request.content_hash,
        field_key=proposal.field_key, value_id=value_id,
        reliability_state=reliability_state, origin=FACT_ORIGINS[2],
        evidence_refs=tuple(proposal.citations), cache_key=cache_key, active=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_llm_seam.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/llm_seam.py tests/p6/test_p6_llm_seam.py
git commit -m "feat(P6): O6 the P8 seam — four inputs, five verdicts, and no checking P6 owns"
```

---

### Task 18: Supersession, and the `preferred` pointer (M1)

**Files:**
- Create: `src/facts/supersede.py`
- Test: `tests/p6/test_p6_supersede.py`

**Interfaces:**
- Consumes: `database_agent.supersede` — `mark_superseded`, `chain`, `SUPERSEDE_COLUMNS`;
  `facts.file_facts` — `facts_for_file`, `FILE_FACTS_COLUMNS`; `facts.fields.get_field`;
  `facts.states` — `STATES`, `is_stronger`.
- Produces (`supersede.py`): `FACT_TABLE: str`, `PreferredNeverReverses(ValueError)`,
  `SupersedeAcrossSlots(ValueError)`,
  `supersede_fact(conn, *, old_fact_id, new_fact_id, reason) -> None`,
  `preferred_fact(conn, *, file_id, field_key) -> sqlite3.Row | None`,
  `fact_history(conn, *, file_id, field_key) -> list[sqlite3.Row]`.

> **Additions to the skeleton's `Produces:` line, declared.** `FACT_TABLE` exists because P1's
> `mark_superseded` and `chain` are addressed by table *name* and that string must have one home; the
> test below asserts it names a real table carrying both the `record_id` projection and the
> `preferred` column, so a drift fails at the first run rather than at review. The two exceptions
> exist because §8.2's two invariants — *"`preferred` never reverses §3.13's ordering"* and
> supersession happens inside one slot — are enforced at a function a test can call rather than at
> the one call site this module makes. Nothing the skeleton names is renamed.

**Done-means:** 29, and the history half of 15.

**§8.2, quoted, because the whole task is one paragraph of it:**

> The product must never overwrite the evidence record merely because a later extractor or model produces a different answer. A newer result should supersede an earlier result while retaining the old observation and the reason it was superseded. For example, if a first OCR pass produces unreadable text and a later improved OCR engine recovers a university name, both extraction records should remain available. The resolver may mark the newer value as preferred, but a user reviewing a placement should still be able to inspect the origin of the conclusion.

**`preferred` is a pointer, not a strength, and the SPEC states the negative directly:**

> **`preferred` is a pointer, not a strength.** It never enters the §3.6 contradiction check, never breaks a §3.7 margin tie, and never makes a fact destination-eligible. A reader that wants strength reads `reliability_state`.

**What this module writes, and what it deliberately does not.** P1's `mark_superseded` writes three
columns across two rows — `superseded_by` and `supersede_reason` on the old, `supersedes` on the new
— and, verified by execution, **knows nothing about `preferred`**. So `preferred` is this module's
whole addition: `0` on the superseded row, `1` on the survivor, set in the same call that links them
and nowhere else in `facts`.

**No event is appended here, and that is a decision rather than an omission.** §8.2's list gives P6
two event types, `fact creation` and `fact rejection`, both spelled with a space and both already in
P1's `RESERVED_EVENT_TYPES`. Supersession is neither: §8.7 keeps a `rejected` fact rather than
removing it, so *rejection* is a state a fact carries, while supersession is one fact replacing
another — and P1 publishes three columns for exactly that, one of which is the reason §8.2 asks to be
retained. The skeleton is also explicit that `subsystem = "P6"` is written in **one** module (M8), so
an `append_event` call here would be a second home for P6's authorship. Task 4 already appends
`fact creation` when the new fact is written; this call links two rows that both already exist.

**The chain is walked backwards before it is walked forwards, because P1's `chain` only goes one
way.** Verified by execution: with `a → b → c` recorded, `chain(a)` returns `[a, b, c]` and
`chain(c)` returns `[c]`. A history read that started from the newest row would return one row and
look correct. So `fact_history` finds the tail of each chain through the `supersedes` column first,
then walks forward from there. The walk terminates without a guard because `mark_superseded` refuses
a cycle at write time — it walks the prospective chain and raises *"supersede chain would cycle"* —
so the graph on disk is acyclic by construction rather than by a second check here.

**The slot is addressed through Task 4's reader and P1's columns, never through `field_key`.** Which
column `file_facts` uses to reference the catalogue is Task 4's schema decision, and a second module
spelling it would be a second home for one decision — the defect this project pays most for. So this
module reads `file_id` and `content_hash` (both in §3's own table block), gets the live rows and
their `field_key` from `facts_for_file`, and expands each into its full history with P1's `chain`.
The four columns it touches directly are asserted against `FILE_FACTS_COLUMNS` in a test, so a Task 4
rename fails here immediately.

**Why `preferred_fact` returns `None` for several live rows, rather than picking one.** OQ6 —
multiplicity — is Joseph's and is open: §3.11's `people` and `language` are plainly multi-valued and
the SPEC carries `multiplicity` as an *unanswered* column. So a slot holding several live,
unsuperseded facts has no preferred row, because "which of several simultaneous values is preferred"
*is* the multiplicity question and answering it inside a reader would close it by accident. Three
cases are answerable and are answered: a `user_confirmed` row wins outright (§3.13's ordering is not
negotiable and the SPEC names this case), a single live row is the answer even though `preferred` was
never set on it (the column is set *only* on supersession), and among several live rows exactly one
carrying `preferred` is the pointer.

**`preferred_fact` and `fact_history` span every content hash the file has had.** That is the
skeleton's signature — `(file_id, field_key)`, no content hash — and it is right for a *reader*: the
read surface published to P2 and the review UI is *"fact and value history, including superseded
rows"*, and a user inspecting the origin of a conclusion does not know which version produced it.
Supersession itself always happens inside one content hash, because §3.4's invalidation cases — a
bumped extractor version, a changed prompt fingerprint, a new analysis tier — all leave the bytes
alone; §8.2's own worked example is two OCR passes over one file version.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_supersede.py
"""M1 — Done-means 29 and the history half of 15. §8.2's worked example, run."""
from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import FACT_ORIGINS, FILE_FACTS_COLUMNS, facts_for_file, write_fact
from facts.states import STATES
from facts.supersede import (
    FACT_TABLE, PreferredNeverReverses, SupersedeAcrossSlots, fact_history,
    preferred_fact, supersede_fact,
)
from facts.unresolved import ATTEMPTED_PRODUCERS, unresolved_for_file, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: The three places §8.2 forbids the pointer from reaching. Each is another task's
#: module; a missing one is skipped rather than assumed, and the two that ship before
#: Wave D are required to be present so the guard cannot pass by being empty.
POINTER_FREE = {"facts.facets": True, "facts.fields": True,
                "facts.llm_seam": False, "facts.read_surface": False}


def _mentions(module_name: str) -> set[str]:
    """Every name, attribute and string literal a module's CODE contains."""
    module = importlib.import_module(module_name)
    tree = ast.parse(inspect.getsource(module))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.add(node.value)
    return found


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Scans", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, analysis_tier="ocr",
             extractor="ocr.vision", version="1.0.0"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type="ocr", analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type="ocr", raw_value=raw,
        location=Location("ocr", (Segment("page", index=1),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _fact(conn, *, file_id, content_hash, field_key, value, key, state, cache_key):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=FACT_ORIGINS[1],
                      evidence_refs=(key,), cache_key=cache_key, active=True)


@pytest.fixture()
def scanned(p6_conn, tmp_path):
    """§8.2's own case: one scanned file, and two OCR passes over it."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="transcript.pdf",
                                    body=b"a scanned transcript")
    first = _observe(p6_conn, run_id="ocr-1", file_id=file_id,
                     content_hash=content_hash, raw="C0lumb1a Un1vers1ty")
    second = _observe(p6_conn, run_id="ocr-2", file_id=file_id,
                      content_hash=content_hash, raw="Columbia University",
                      version="2.0.0")
    return file_id, content_hash, first, second


def test_the_table_this_module_addresses_carries_both_columns_it_needs(p6_conn):
    # P1's `mark_superseded` requires a column literally named `record_id`; the
    # pointer requires `preferred`. Both are Task 4's DDL and are asserted rather
    # than assumed, so a drift fails at the first run instead of at review.
    assert FACT_TABLE == "file_facts"
    columns = {row["name"] for row in
               p6_conn.execute(f"PRAGMA table_info({FACT_TABLE})")}
    assert "record_id" in columns
    assert "preferred" in columns
    assert set(SUPERSEDE_COLUMNS) <= columns
    # The four this module reads directly are Task 4's published set, not guesses.
    for column in ("fact_id", "file_id", "content_hash", "reliability_state",
                   "preferred"):
        assert column in FILE_FACTS_COLUMNS, column
    assert STATES[0] == "user_confirmed"      # P4 publishes the tuple strongest-first


def test_a_superseding_fact_is_preferred_and_the_superseded_row_is_not(
        scanned, p6_conn):
    # Done-means 29.
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    rows = {r["fact_id"]: r for r in fact_history(p6_conn, file_id=file_id,
                                                  field_key="subject")}
    assert not rows[old]["preferred"]
    assert rows[new]["preferred"]
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == new


def test_both_rows_both_states_and_both_evidence_chains_remain_readable(
        scanned, p6_conn):
    # Done-means 29 and 15. §8.2: "both extraction records should remain available".
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    history = fact_history(p6_conn, file_id=file_id, field_key="subject")
    assert [r["fact_id"] for r in history] == [old, new]          # oldest first
    assert [r["reliability_state"] for r in history] == ["possible", "validated"]
    assert history[0]["supersede_reason"] == "a later OCR engine recovered the name"
    assert history[1]["supersede_reason"] is None
    for row, key in ((history[0], first), (history[1], second)):
        assert json.loads(row["evidence_refs"]) == [key]
    # And P4's raw values are untouched by any of it (§3.2, rule 1).
    raws = {r["raw_value"] for r in p6_conn.execute(
        "SELECT raw_value FROM evidence WHERE file_id = ?", (file_id,))}
    assert raws == {"C0lumb1a Un1vers1ty", "Columbia University"}


def test_section_eight_two_s_worked_example_end_to_end(scanned, p6_conn):
    # "If a first OCR pass produces unreadable text and a later improved OCR engine
    # recovers a university name, both extraction records should remain available."
    # Under B7 the first pass is a ROW, not an absence. The unresolved -> fact
    # supersession is Task 5's; what is asserted here is that the refusal survives.
    file_id, content_hash, first, second = scanned
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason="no_candidate_evidence",
                     attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                     evidence_refs=(first,), cache_key="sha256:pass-zero")
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    refusals = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key="subject")
    assert [r["reason"] for r in refusals] == ["no_candidate_evidence"]
    assert len(fact_history(p6_conn, file_id=file_id, field_key="subject")) == 2
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == new


def test_preferred_is_set_only_on_supersession(scanned, p6_conn):
    # The SPEC: "It is set only on supersession" and "only by the resolver". A fact
    # written by a producer carries no pointer, and a slot with one live row is still
    # answerable — the row IS the answer, without the column being set.
    file_id, content_hash, first, _ = scanned
    only = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                 state="possible", cache_key="sha256:pass-one")
    row = [r for r in facts_for_file(p6_conn, file_id, content_hash)
           if r["fact_id"] == only][0]
    assert not row["preferred"]
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == only


def test_a_user_confirmed_fact_is_always_the_preferred_row(scanned, p6_conn):
    # §3.13's ordering is not negotiable and `preferred` never reverses it.
    file_id, content_hash, first, second = scanned
    confirmed = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value="Columbia University", key=first,
                      state=STATES[0], cache_key="sha256:user")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Colombia", key=second, state="llm_supported",
          cache_key="sha256:model")
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == confirmed


def test_preferred_never_reverses_the_reliability_ordering(scanned, p6_conn):
    # Attempted, not inspected: the refusal is at a function every route passes.
    file_id, content_hash, first, second = scanned
    confirmed = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value="Columbia University", key=first,
                      state=STATES[0], cache_key="sha256:user")
    weaker = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                   field_key="subject", value="Colombia", key=second,
                   state="validated", cache_key="sha256:rule")
    with pytest.raises(PreferredNeverReverses):
        supersede_fact(p6_conn, old_fact_id=confirmed, new_fact_id=weaker,
                       reason="a rule disagreed with the user")
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == confirmed


def test_supersession_happens_inside_one_slot(scanned, p6_conn):
    # §8.2 replaces an ANSWER; a row about a different field or a different file is
    # not an earlier version of this one.
    file_id, content_hash, first, second = scanned
    subject = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="subject", value="Columbia University", key=first,
                    state="validated", cache_key="sha256:one")
    other = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                  field_key="document_type", value="transcript", key=second,
                  state="validated", cache_key="sha256:two")
    with pytest.raises(SupersedeAcrossSlots):
        supersede_fact(p6_conn, old_fact_id=subject, new_fact_id=other,
                       reason="wrong slot")


def test_several_live_rows_have_no_preferred_row(scanned, p6_conn):
    # OQ6 — multiplicity — is open and the SPEC carries `multiplicity` as an
    # UNANSWERED column. "Which of several simultaneous values is preferred" IS that
    # question, so a reader that picked one would close it by accident.
    file_id, content_hash, first, second = scanned
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Columbia University", key=first, state="validated",
          cache_key="sha256:one")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Columbia College", key=second, state="validated",
          cache_key="sha256:two")
    assert preferred_fact(p6_conn, file_id=file_id, field_key="subject") is None
    assert len(fact_history(p6_conn, file_id=file_id, field_key="subject")) == 2


def test_an_empty_slot_has_no_preferred_row_and_no_history(scanned, p6_conn):
    file_id, _, _, _ = scanned
    assert preferred_fact(p6_conn, file_id=file_id, field_key="subject") is None
    assert fact_history(p6_conn, file_id=file_id, field_key="subject") == []


def test_preferred_appears_in_no_contradiction_margin_or_destination_path():
    # Done-means 29's third clause, and the SPEC's own negative: "`preferred` is a
    # pointer, not a strength. It never enters the §3.6 contradiction check, never
    # breaks a §3.7 margin tie, and never makes a fact destination-eligible."
    # Introspected, not read: each module's code is parsed and the column is looked
    # for by name.
    checked = 0
    for module_name, required in POINTER_FREE.items():
        if importlib.util.find_spec(module_name) is None:
            assert not required, module_name
            continue
        assert "preferred" not in _mentions(module_name), module_name
        checked += 1
    assert checked >= 2                       # the guard cannot pass by being empty


def test_preferred_is_not_plan_versioned():
    # §8.8: facts are shared across plan versions, so the pointer is not addressable
    # per plan version. If it were, this module's three functions would have to say
    # WHICH plan version they meant.
    for function in (supersede_fact, preferred_fact, fact_history):
        names = set(inspect.signature(function).parameters)
        assert not [name for name in names if "plan" in name or "version" in name]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_supersede.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.supersede'`

- [ ] **Step 3: Write `supersede.py`**

```python
# src/facts/supersede.py
"""§8.2 supersession, and the `preferred` pointer M1 places on P6 (§8.2, §8.7).

§8.2, and it is the whole task in one paragraph:

    "The product must never overwrite the evidence record merely because a later
     extractor or model produces a different answer. A newer result should supersede
     an earlier result while retaining the old observation and the reason it was
     superseded. ... The resolver may mark the newer value as preferred, but a user
     reviewing a placement should still be able to inspect the origin of the
     conclusion."

**What P1 does and what this module adds.** `mark_superseded` writes three columns
across two rows -- `superseded_by` and `supersede_reason` on the old, `supersedes` on
the new -- and knows nothing about `preferred`. So the pointer is this module's whole
addition, set in the same call that links the two rows and set nowhere else in
`facts`.

**No event is appended here.** §8.2 gives P6 two event types, `fact creation` and
`fact rejection`, and supersession is neither: §8.7 keeps a `rejected` fact rather
than removing it, so rejection is a STATE a fact carries, while supersession is one
fact replacing another -- and P1 publishes three columns for exactly that, one of
which is the reason §8.2 asks to be retained. M8 also puts `subsystem = "P6"` in one
module, so an `append_event` call here would be a second home for P6's authorship.

**The chain is walked backwards before forwards.** P1's `chain` walks forward only:
with `a -> b -> c` recorded, `chain(a)` is `[a, b, c]` and `chain(c)` is `[c]`. A
history read starting from the newest row would return one row and look correct, so
`fact_history` finds each chain's tail through `supersedes` first. The walk needs no
cycle guard: `mark_superseded` refuses a cycle at write time, so the graph on disk is
acyclic by construction rather than by a second policy here.

**The slot is addressed through Task 4's reader, never through `field_key`.** Which
column `file_facts` uses to reference the catalogue is Task 4's schema decision, and a
second module spelling it would be a second home for one decision. This module reads
`file_id` and `content_hash`, takes the field key off `facts_for_file`'s rows, and
expands each into its history with P1's `chain`.

**`preferred` is a pointer, not a strength.** The SPEC's negative is exact: "It never
enters the §3.6 contradiction check, never breaks a §3.7 margin tie, and never makes a
fact destination-eligible. A reader that wants strength reads `reliability_state`."
Nothing here exports it into those paths, and a test parses those modules for the
column by name.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from database_agent.supersede import chain, mark_superseded

from facts.file_facts import facts_for_file
from facts.states import STATES

#: The table P1's `mark_superseded` and `chain` are addressed by. Task 4 owns the DDL,
#: including the VIRTUAL `record_id` projection of `fact_id` that P1 requires and the
#: `preferred` column this module sets; the name has one home and the test asserts it
#: names a table carrying both.
FACT_TABLE: str = "file_facts"


class PreferredNeverReverses(ValueError):
    """§3.13's ordering, raised rather than documented.

    "A `user_confirmed` fact is always the preferred row for its `(file_id,
    field_key)`; §3.13's ordering is not negotiable and `preferred` never reverses it."
    """


class SupersedeAcrossSlots(ValueError):
    """§8.2 replaces an ANSWER, so both rows answer the same question."""


def _row(conn: sqlite3.Connection, fact_id: str) -> sqlite3.Row:
    row = conn.execute(
        f"SELECT * FROM {FACT_TABLE} WHERE fact_id = ?", (fact_id,)).fetchone()
    if row is None:
        raise KeyError(f"unknown fact {fact_id!r}")
    return row


def _tail(conn: sqlite3.Connection, fact_id: str) -> str:
    """The oldest row of this fact's chain.

    P1's `chain` walks forward only, so a history read has to find the start itself.
    No cycle guard: `mark_superseded` walks the prospective chain and refuses one at
    write time, so this loop terminates on any graph the writer could have produced.
    """
    row = _row(conn, fact_id)
    while row["supersedes"] is not None:
        row = _row(conn, row["supersedes"])
    return row["fact_id"]


def _slot(conn: sqlite3.Connection, *, file_id: str,
          field_key: str) -> list[sqlite3.Row]:
    """Every row for one (file, field) slot, superseded rows included.

    Spans every content hash the file has had, which is what a reader inspecting the
    origin of a conclusion needs: §8.2's user "does not know which version produced
    it". Supersession itself always happens inside one content hash, because §3.4's
    invalidation cases -- a bumped extractor version, a changed prompt fingerprint, a
    new analysis tier -- all leave the bytes alone.
    """
    hashes = sorted(row["content_hash"] for row in conn.execute(
        f"SELECT DISTINCT content_hash FROM {FACT_TABLE} WHERE file_id = ?",
        (file_id,)))
    reachable: dict[str, sqlite3.Row] = {}
    for content_hash in hashes:
        for row in facts_for_file(conn, file_id, content_hash):
            if row["field_key"] != field_key:
                continue
            for member in chain(conn, FACT_TABLE, _tail(conn, row["fact_id"])):
                reachable[member["fact_id"]] = member
    return [reachable[fact_id] for fact_id in sorted(reachable)]


def supersede_fact(conn: sqlite3.Connection, *, old_fact_id: str,
                   new_fact_id: str, reason: str) -> None:
    """Done-means 29. Link two facts, and move the pointer. Nothing is deleted.

    The reason is required by P1 and is the half §8.2 names explicitly -- "retaining
    the old observation AND the reason it was superseded".
    """
    old = _row(conn, old_fact_id)
    new = _row(conn, new_fact_id)
    if (old["file_id"], old["field_key"]) != (new["file_id"], new["field_key"]):
        raise SupersedeAcrossSlots(
            "§8.2 supersedes an answer: both facts must be for one file and one "
            f"field; {old_fact_id!r} and {new_fact_id!r} are not")
    if old["reliability_state"] == STATES[0] != new["reliability_state"]:
        raise PreferredNeverReverses(
            f"{old_fact_id!r} is {STATES[0]!r}; §3.13's ordering is not negotiable "
            "and `preferred` never reverses it, so a weaker fact cannot take the "
            "pointer from a user's own answer")
    mark_superseded(conn, FACT_TABLE, old_id=old_fact_id, new_id=new_fact_id,
                    reason=reason)
    conn.execute(f"UPDATE {FACT_TABLE} SET preferred = 0 WHERE fact_id = ?",
                 (old_fact_id,))
    conn.execute(f"UPDATE {FACT_TABLE} SET preferred = 1 WHERE fact_id = ?",
                 (new_fact_id,))


def preferred_fact(conn: sqlite3.Connection, *, file_id: str,
                   field_key: str) -> sqlite3.Row | None:
    """The row a reader should show for this slot, or `None`.

    Three cases are answerable and are answered:

    * a `user_confirmed` live row wins outright -- §3.13's ordering is not
      negotiable and the SPEC names this case;
    * a single live row is the answer even though `preferred` was never set on it,
      because the column is set ONLY on supersession;
    * among several live rows, exactly one carrying `preferred` is the pointer.

    Anything else returns `None`. OQ6 -- multiplicity -- is open and the SPEC carries
    `multiplicity` as an unanswered column, so "which of several simultaneous values
    is preferred" is that question and a reader that picked one would close it by
    accident.

    Live means not superseded. `active` is a different axis and is Task 4's: §8.2's
    mechanism for the pointer is supersession, and reading a second column here would
    make the pointer depend on two rules instead of one.
    """
    live = [row for row in _slot(conn, file_id=file_id, field_key=field_key)
            if row["superseded_by"] is None]
    confirmed = [row for row in live if row["reliability_state"] == STATES[0]]
    if confirmed:
        live = confirmed
    if len(live) == 1:
        return live[0]
    pointed = [row for row in live if row["preferred"]]
    return pointed[0] if len(pointed) == 1 else None


def fact_history(conn: sqlite3.Connection, *, file_id: str,
                 field_key: str) -> list[sqlite3.Row]:
    """Done-means 15's history half. Every row for the slot, oldest first.

    Superseded rows included, each carrying its own reliability state, its own
    evidence refs and the reason it was superseded -- §8.2's "a user reviewing a
    placement should still be able to inspect the origin of the conclusion".
    """
    rows = _slot(conn, file_id=file_id, field_key=field_key)
    tails = sorted({_tail(conn, row["fact_id"]) for row in rows})
    history: list[sqlite3.Row] = []
    for tail in tails:
        history.extend(chain(conn, FACT_TABLE, tail))
    return history
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_supersede.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/supersede.py tests/p6/test_p6_supersede.py
git commit -m "feat(P6): M1 supersession and the preferred pointer — a pointer, never a strength"
```

---

### Task 19: `no_usable_facts`, the recorded pass, and the ordering guard (M11)

**Files:**
- Create: `src/facts/usable.py`
- Modify: `src/facts/schema.py` (two lines — see Step 3b)
- Test: `tests/p6/test_p6_usable.py`

**Interfaces:**
- Consumes: `facts.file_facts.facts_for_file`; `facts.unresolved.unresolved_for_file`;
  `evidence_shape.vocabulary` — `ANALYSIS_TIERS`, `check`; `evidence_shape.canonical` —
  `canonical_json`, `sha256_of`; `extractors.failure.ContractViolation`.
- Produces (`usable.py`): `FACT_PASSES_TABLE: str`, `FACT_PASSES_DDL: str`,
  `create_fact_passes(conn) -> None`, `FactPassNotRun(ContractViolation)`,
  `record_pass(conn, *, file_id, content_hash, analysis_tiers: frozenset[str]) -> None`,
  `passes_for(conn, *, file_id, content_hash) -> tuple[frozenset[str], ...]`,
  `no_usable_facts_for(conn, *, usable_threshold) -> Callable[[str, str], bool]`.

> **Additions to the skeleton's `Produces:` line, declared.** `FACT_PASSES_TABLE`,
> `FACT_PASSES_DDL` and `create_fact_passes` are added because the skeleton's Files line says
> *modify `src/facts/schema.py`* and something has to hold the DDL. Keeping it in this module rather
> than in `schema.py` means a reviewer can reject Task 19 whole without touching four other tasks'
> table definitions, and `schema.py` gains two lines instead of a block. `FactPassNotRun`'s **base
> class changes** from the skeleton's `Exception` to `extractors.failure.ContractViolation` — that is
> a ratified change and the reason is below.

**Done-means:** 28, and the enforceable half of preamble rule 5. **Adversarial case:** A10.

**§2.2, quoted, because both halves of the verdict are in one sentence pair:**

> The system should also distinguish between a PDF with no text layer and one with a broken text layer. A file with no text should route directly to OCR; a file that technically produces text but yields no usable facts may receive targeted OCR as a fallback because scanned PDFs can contain unreadable or corrupted extracted text. The system should not use unreliable global language-quality checks that incorrectly punish multilingual or mathematics-heavy documents.

**§2.7, quoted, because it forbids the same shortcut a second time:**

> A document with a non-empty but unusable text layer should receive OCR only when its extracted evidence fails to produce usable facts, not because a broad quality heuristic says the text looks unusual.

---

> # ⛔ DO NOT WIRE THIS INTO `run_wave2`. Read this before writing a line of the module.
>
> **What this task builds is a read surface P6's own tests exercise. Wiring it into the caller is
> separate, later work and must not be done as "integration", as "finishing the seam", or as a
> tidy-up at the end of the phase.**
>
> The mechanism, verified in the source on 2026-08-22:
>
> 1. `extractors.ocr_policy.text_layer_state(*, result, file_id, content_hash, no_usable_facts)`
>    calls `no_usable_facts(file_id, content_hash)` for **every** document whose run produced any
>    non-empty text unit — that is every text-bearing PDF in the corpus.
> 2. It is called from `document_ocr_decision`, which is called inside `extract()` on the
>    freshly-built `ExtractionResult`, which `orchestrator._extract_one` calls inside
>    `run_wave2`'s **single** loop over `cache_verdicts`. `_write(sink, result, ...)` does not run
>    until after `_extract_one` returns, so at the moment of the call P4 does not yet hold the
>    observations, let alone any fact derived from them.
> 3. **P6 Task 26 — the caller restructure — is CUT (D5).** Nothing reorders that loop. Nothing in
>    this plan touches `src/orchestrator.py`.
> 4. `FactPassNotRun` inherits `ContractViolation`, and `orchestrator._extract_one` re-raises
>    `ContractViolation` by name rather than converting it into one `failed` run.
>
> **Therefore: if P6's resolver is ever passed to `run_wave2` as `no_usable_facts`, the first
> text-bearing PDF ends the scan.** Not one bad file — the scan.
>
> **The caller keeps passing `orchestrator.TARGETED_OCR_UNAVAILABLE`,** which is P5's own stub and
> whose docstring already says why. Wiring the real verdict is the four-pass work described under
> preamble rule 5, and it is owed together with the pass-3/pass-4 ordering — not before it, and not
> instead of it. A test in this task asserts the orchestrator still imports nothing from `facts`, so
> the day someone wires it, that test fails first.
>
> **This is not a reason to soften the raise.** See *Why raise rather than default* below: the raise
> is what makes the ordering checkable at all, and the loud failure above is the guard working, not
> the guard misfiring.

---

**Why `FactPassNotRun` inherits `ContractViolation` rather than `Exception`.** The skeleton wrote
`FactPassNotRun(Exception)`. A plain `Exception` raised from inside a `no_usable_facts` callable is
caught by `orchestrator._extract_one`'s broad `except Exception` and converted into one `failed`
extraction run — the file is recorded as unreadable, the scan continues, and the ordering defect
becomes a data-quality mystery in a corner of the corpus. `ContractViolation` is re-raised by name,
above that branch, with the reason stated in the orchestrator's own comment:

> A `ContractViolation` is not about this file at all, so recording it as the file's failure would be a false statement about the corpus AND would hide the defect it exists to surface.

That is precisely this exception's case: being asked for a verdict before the pass that defines it is
not a fact about the PDF. So the base class is `ContractViolation`.

**This is the one import `facts` makes from `extractors`, and it is worth naming.** P6's dependency
on P5 is otherwise zero — the skeleton is explicit that P6 consumes P5 *"only via P4's shape"*. An
exception base class is not per-format knowledge and creates no cycle (`extractors.failure` imports
nothing from `facts`), but it *is* an edge that did not exist before, and Task 25's guard should
permit exactly this one and no other. Flagged in the contract notes.

**The pass record is a fifth table, and the "four tables" line needs reading with it.** The skeleton
says P6 *"owns four tables and creates none of anyone else's"*, and Task 19's own Files line says to
modify `schema.py`. Both are the same author and both are right: the **four** are §3's published
records — `fields`, `values`, `file_facts`, `unresolved` — which neighbours read. `fact_passes` is
P6-internal bookkeeping that no other part reads and that carries no claim about any file. The clause
that actually binds is the second one, *"creates none of anyone else's"*, and this creates none.

**The pass record carries no timestamp, deliberately.** It answers a membership question — *has a
deterministic pass over this `(file_id, content_hash)` completed, and which analysis tiers did it
cover* — and a time column would invite a caller to reason about "the latest pass", which is the
kind of ordering P6 refuses to infer anywhere else (Global Constraints: P6 imposes its own total
order and inherits none). Recording the same pass twice writes one row, because `pass_id` is
`sha256_of(canonical_json([file_id, content_hash, sorted(tiers)]))`.

**Computed from the fact tables and nothing else.** The SPEC's negative is load-bearing and is stated
twice in the design — §2.2's *"should not use unreliable global language-quality checks"* and §2.7's
*"not because a broad quality heuristic says the text looks unusual"* — and A10 names the failure
literally: `forbidden_value: {"ocr_fallback": true, "triggered_by": "language_quality_heuristic"}`,
verified in `tests/eval/fixtures/adversarial/A10.json`. So the module reads `facts_for_file` and
`unresolved_for_file` and nothing else; it never touches a `text_unit`, never counts characters,
never inspects a language. The test parses the module and asserts no identifier mentions text, a
unit, a language, a ratio or a character, alongside the behavioural cases.

**`usable_threshold` is a required keyword with no default, and its polarity is stated once here.**
It receives `(facts, unresolved)` — the two row lists for the version — and returns **`True` when
the stored facts ARE usable**. The verdict returns the negation. Which facts count and how many is
Deferred by name (*"The `no_usable_facts` threshold — M11, P5 OQ1. Which facts count as usable and
how many. The design requires the verdict and states no threshold."*), so nothing here chooses, and
Task 25 asserts no threshold is a module-level constant by runtime introspection of the namespace.

**Why raise rather than default.** Returning `False` for an unrecorded pass would be safe — no OCR —
and would hide the bug forever; the current stub does exactly that, which is why the defect survived
to now. Returning `True` is the corpus-wide OCR the SPEC names outright (*"Consulted earlier it
would return `true` for every file and trigger OCR on the whole corpus"*). Raising is the only option
that makes a wrong call sequence a failing test rather than a silent behaviour, which is this
project's stated decision criterion: *"the one that … makes a wrong outcome impossible rather than
merely unlikely, wins"*. Note what the raise buys structurally: `True` is not a value the
unrecorded-pass branch can produce at all, so the SPEC's named disaster is unreachable rather than
unlikely.

**The termination condition is a lookup, not a flag.** A pass record carries which tiers it covered,
so *"have we already tried OCR for this content hash"* is `"ocr" in some recorded pass` — answerable
from the table. A file whose OCR pass also produced nothing is a file with no usable facts, not a
file to OCR again, and the verdict keeps answering after an `ocr` pass rather than raising. **Nothing
here asserts the caller does not loop** — that was Task 26's and Task 26 is cut. The non-looping
property is owed with the four-pass wiring, and until then no caller consults this verdict at all.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_usable.py
"""M11 — Done-means 28, A10, and the guard that makes preamble rule 5 checkable."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

import orchestrator

from database_agent.files_table import get_file, record_file

from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

from extractors.failure import ContractViolation
from extractors.ocr_policy import text_layer_state
from extractors.sink import ExtractionResult

from facts import usable
from facts.file_facts import FACT_ORIGINS, FORBIDDEN_COLUMN_SUBSTRINGS, write_fact
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.usable import (
    FACT_PASSES_TABLE, FactPassNotRun, no_usable_facts_for, passes_for, record_pass,
)
from facts.values import VALUE_ORIGINS, ensure_value

NATIVE = frozenset({ANALYSIS_TIERS[1]})            # "native"
WITH_OCR = frozenset({ANALYSIS_TIERS[1], ANALYSIS_TIERS[2]})


def _any_fact(facts, unresolved) -> bool:
    """The injected threshold. Returns True when the stored facts ARE usable.

    §2.2's threshold is Deferred by name, so the test states one and the module
    states none. This one is the simplest that distinguishes the two Done-means 28
    cases; it is not a proposal.
    """
    return bool(facts)


def _never_usable(facts, unresolved) -> bool:
    return False


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20).
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _identifiers(module) -> set[str]:
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
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Scans", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


@pytest.fixture()
def scanned(p6_conn, tmp_path):
    return _record(p6_conn, tmp_path, name="scan.pdf", body=b"a scanned page")


def test_the_returned_callable_is_exactly_the_shape_p5_already_requires(p6_conn):
    # Two P5 tests assert `no_usable_facts` has no default and is called
    # positionally; the factory must therefore return that shape with no adapter.
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    signature = inspect.signature(verdict)
    parameters = list(signature.parameters.values())
    assert [p.name for p in parameters] == ["file_id", "content_hash"]
    for parameter in parameters:
        assert parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert parameter.annotation == "str"
    assert signature.return_annotation == "bool"
    # And it binds against the seam the orchestrator already declares.
    seam = inspect.signature(orchestrator.run_wave2).parameters["no_usable_facts"]
    assert seam.kind is inspect.Parameter.KEYWORD_ONLY
    assert seam.default is inspect.Parameter.empty


def test_false_for_a_file_with_one_active_usable_fact(scanned, p6_conn):
    # Done-means 28, first half.
    file_id, content_hash = scanned
    key = "sha256:" + "a" * 64
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="Columbia University",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="validated", origin=FACT_ORIGINS[1],
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is False


def test_true_for_a_file_whose_evidence_produced_only_unresolved_rows(
        scanned, p6_conn):
    # Done-means 28, second half. §2.2's `text_layer_broken` case: text came out,
    # and no fact did. The `unresolved` rows are evidence FOR the verdict.
    file_id, content_hash = scanned
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason="no_candidate_evidence",
                     attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                     evidence_refs=(), cache_key="sha256:cache")
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is True


def test_the_threshold_decides_and_the_module_states_none(scanned, p6_conn):
    # Both polarities driven through the same stored rows, so the module cannot be
    # holding a rule of its own behind the injected one.
    file_id, content_hash = scanned
    key = "sha256:" + "b" * 64
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="Columbia University",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="possible", origin=FACT_ORIGINS[1],
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    assert no_usable_facts_for(
        p6_conn, usable_threshold=_any_fact)(file_id, content_hash) is False
    assert no_usable_facts_for(
        p6_conn, usable_threshold=_never_usable)(file_id, content_hash) is True
    parameter = inspect.signature(no_usable_facts_for).parameters["usable_threshold"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    # Task 25's technique: runtime introspection of the namespace, not a text search.
    numbers = {name: value for name, value in vars(usable).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {}


def test_no_recorded_pass_raises_rather_than_answering(scanned, p6_conn):
    # The SPEC: the verdict is "defined only after P6's deterministic pass on that
    # content hash has completed. Consulted earlier it would return `true` for every
    # file and trigger OCR on the whole corpus." `True` is not a value this branch
    # can produce, so that outcome is unreachable rather than unlikely.
    file_id, content_hash = scanned
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    with pytest.raises(FactPassNotRun):
        verdict(file_id, content_hash)


def test_the_verdict_is_per_file_version_and_not_per_file(p6_conn, tmp_path):
    # Keyed on (file_id, content_hash): a pass over one version says nothing about
    # another, because the §3.4 cache key differs and so do the facts.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf", body=b"one")
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is True
    with pytest.raises(FactPassNotRun):
        verdict(file_id, "f" * 64)


def test_the_raise_is_a_contract_violation_and_the_caller_cannot_swallow_it():
    # A plain Exception would be caught by `orchestrator._extract_one`'s broad
    # `except Exception` and become one `failed` run -- the file recorded as
    # unreadable, the scan continuing, the ordering defect turned into a data-quality
    # mystery. The orchestrator re-raises ContractViolation by name because "a
    # ContractViolation is not about this file at all".
    assert issubclass(FactPassNotRun, ContractViolation)


def test_consulting_it_during_extraction_ends_the_scan(p6_conn, tmp_path):
    """The danger, proved rather than described — this is why it is not wired in.

    `ocr_policy.text_layer_state` consults the verdict for every document whose run
    produced any non-empty text unit, inside `run_wave2`'s single loop, before P4
    holds the observations at all. Task 26 is cut, so nothing reorders that. This
    test IS the reason `orchestrator.TARGETED_OCR_UNAVAILABLE` is still the value the
    caller passes.
    """
    file_id, content_hash = _record(p6_conn, tmp_path, name="text.pdf",
                                    body=b"a text-bearing PDF")
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    result = ExtractionResult(run={},
                              text_units=({"text": "a non-empty text layer"},))
    with pytest.raises(FactPassNotRun):
        text_layer_state(result=result, file_id=file_id,
                         content_hash=content_hash, no_usable_facts=verdict)
    # A document with NO text never reaches the verdict, which is §2.2's other route
    # and needs no pass at all.
    assert text_layer_state(result=ExtractionResult(run={}), file_id=file_id,
                            content_hash=content_hash,
                            no_usable_facts=verdict) == "text_layer_absent"


def test_the_orchestrator_still_passes_the_stub_and_imports_nothing_from_facts():
    # D5, asserted from P6's side. The day someone wires this verdict into
    # `run_wave2`, this test fails before the scan does.
    assert orchestrator.TARGETED_OCR_UNAVAILABLE("any-file", "any-hash") is False
    tree = ast.parse(inspect.getsource(orchestrator))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
    assert "facts" not in imported


def test_a_pass_at_native_answers_and_a_pass_that_included_ocr_still_answers(
        scanned, p6_conn):
    # Pass 3's gate, and the termination condition. A file whose OCR pass also
    # produced nothing is a file with no usable facts, not a file to OCR again.
    file_id, content_hash = scanned
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    assert verdict(file_id, content_hash) is True
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=WITH_OCR)
    assert verdict(file_id, content_hash) is True
    # "Have we already tried OCR for this content hash" is a LOOKUP, not a flag.
    covered = passes_for(p6_conn, file_id=file_id, content_hash=content_hash)
    assert any(ANALYSIS_TIERS[2] in tiers for tiers in covered)
    assert NATIVE in covered and WITH_OCR in covered


def test_a_pass_recorded_twice_is_one_row(scanned, p6_conn):
    file_id, content_hash = scanned
    for _ in range(3):
        record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=NATIVE)
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == (
        NATIVE,)


def test_a_pass_records_only_tiers_p4_publishes(scanned, p6_conn):
    file_id, content_hash = scanned
    with pytest.raises(NotInVocabulary):
        record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=frozenset({"vibes"}))
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == ()


def test_it_is_computed_from_the_fact_tables_and_no_text_quality_heuristic(p6_conn):
    # Done-means 28's second half, and A10's forbidden value by name:
    # {"ocr_fallback": true, "triggered_by": "language_quality_heuristic"}.
    # §2.2 and §2.7 both forbid deciding this from text quality.
    mentioned = _identifiers(usable)
    for banned in ("text", "unit", "language", "quality", "ratio", "char", "ocr_"):
        assert not [name for name in mentioned if banned in name.lower()], banned
    assert "evidence_shape.store" not in mentioned
    assert "language_quality_heuristic" not in _code_strings(usable)
    # The two reads it IS built from.
    assert "facts_for_file" in mentioned and "unresolved_for_file" in mentioned


def test_the_pass_record_obeys_the_same_negative_contract_as_the_fact_tables(
        p6_conn):
    # §3.14, applied to the fifth table too: a reviewer checks it from the schema.
    columns = [row["name"] for row in
               p6_conn.execute(f"PRAGMA table_info({FACT_PASSES_TABLE})")]
    assert columns == ["pass_id", "file_id", "content_hash", "analysis_tiers"]
    for column in columns:
        for forbidden in FORBIDDEN_COLUMN_SUBSTRINGS:
            assert forbidden not in column, (column, forbidden)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_usable.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.usable'`

- [ ] **Step 3: Write `usable.py`**

```python
# src/facts/usable.py
"""M11 — `no_usable_facts`, the recorded pass, and the ordering guard (§2.2, §2.7).

§2.2 permits targeted OCR on a PDF with a non-empty but BROKEN text layer only when
its stored evidence yields no usable facts. This module is that verdict.

    "A file that technically produces text but yields no usable facts may receive
     targeted OCR as a fallback ... The system should not use unreliable global
     language-quality checks that incorrectly punish multilingual or
     mathematics-heavy documents."          -- §2.2

    "A document with a non-empty but unusable text layer should receive OCR only when
     its extracted evidence fails to produce usable facts, not because a broad quality
     heuristic says the text looks unusual."                              -- §2.7

**DO NOT WIRE THIS INTO `run_wave2`.** `extractors.ocr_policy.text_layer_state`
consults `no_usable_facts` for every document whose run produced any non-empty text
unit, inside the orchestrator's single extraction loop, before P4 has been handed the
observations at all. P6 Task 26 -- the caller restructure -- is CUT (D5), so nothing
reorders that. `FactPassNotRun` is a `ContractViolation` and the orchestrator re-raises
those by name, so passing this verdict to `run_wave2` today would END THE SCAN on the
first text-bearing PDF. The caller keeps `orchestrator.TARGETED_OCR_UNAVAILABLE`.
Wiring the real verdict is the four-pass work and is owed together with the pass-3 and
pass-4 ordering, not before it. A test asserts the orchestrator still imports nothing
from `facts`.

**Computed from the fact tables and nothing else.** The negative is load-bearing and
the design states it twice. A10 names the failure literally --
`triggered_by: "language_quality_heuristic"` is its forbidden value -- so this module
reads `facts_for_file` and `unresolved_for_file` and touches no text unit, no
character count and no language.

**Why it raises.** Returning `False` for an unrecorded pass would be safe and would
hide the bug forever -- the current stub does exactly that, which is why the defect
survived to now. Returning `True` is the corpus-wide OCR the SPEC names. Raising is
the only option that turns a wrong call sequence into a failing test, and it makes the
SPEC's named disaster UNREACHABLE rather than unlikely: `True` is not a value the
unrecorded-pass branch can produce.

**The pass record is a fifth table and no neighbour reads it.** The four P6 owns are
§3's published records -- `fields`, `values`, `file_facts`, `unresolved`. This one is
bookkeeping, carries no claim about any file, and creates none of anyone else's. It
has no timestamp on purpose: it answers a membership question, and a time column would
invite a caller to reason about "the latest pass", which is an ordering P6 refuses to
infer anywhere else.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Callable, Iterable, Sequence

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from extractors.failure import ContractViolation

from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

#: P6-internal bookkeeping. Not one of the four published records, and read by no
#: other part. `analysis_tiers` is canonical JSON of the sorted tier names, so one
#: pass has one representation.
FACT_PASSES_TABLE: str = "fact_passes"

FACT_PASSES_DDL: str = f"""
CREATE TABLE IF NOT EXISTS {FACT_PASSES_TABLE} (
    pass_id        TEXT PRIMARY KEY,
    file_id        TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    analysis_tiers TEXT NOT NULL
)
"""


class FactPassNotRun(ContractViolation):
    """The verdict was consulted before the pass that defines it.

    The base class is deliberate. A plain `Exception` raised from inside a
    `no_usable_facts` callable is caught by `orchestrator._extract_one`'s broad
    `except Exception` and becomes one `failed` extraction run: the file recorded as
    unreadable, the scan continuing, and the ordering defect turned into a
    data-quality mystery. The orchestrator re-raises `ContractViolation` by name for
    the reason its own comment gives -- "a ContractViolation is not about this file at
    all, so recording it as the file's failure would be a false statement about the
    corpus AND would hide the defect it exists to surface" -- which is exactly this
    exception's case.
    """


def create_fact_passes(conn: sqlite3.Connection) -> None:
    """Create the pass record. Called from `facts.schema.create_facts_schema`."""
    conn.execute(FACT_PASSES_DDL)


def record_pass(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                analysis_tiers: frozenset[str]) -> None:
    """A P6 deterministic pass over this file version, at these tiers, completed.

    Idempotent: `pass_id` is derived from the three values, so recording the same
    pass twice writes one row. The tiers are checked against P4's published tuple
    rather than stored as given -- a tier P4 does not publish is a spelling error
    that would make the termination lookup silently wrong.
    """
    for tier in sorted(analysis_tiers):
        check(tier, ANALYSIS_TIERS, name="analysis_tier")
    tiers = canonical_json(sorted(analysis_tiers))
    pass_id = sha256_of(canonical_json([file_id, content_hash, tiers]))
    conn.execute(
        f"INSERT OR IGNORE INTO {FACT_PASSES_TABLE} "
        "(pass_id, file_id, content_hash, analysis_tiers) VALUES (?, ?, ?, ?)",
        (pass_id, file_id, content_hash, tiers))


def passes_for(conn: sqlite3.Connection, *, file_id: str,
               content_hash: str) -> tuple[frozenset[str], ...]:
    """Every recorded pass over this file version, as its set of analysis tiers.

    Ordered by `pass_id` so the sequence is a property of the values rather than of
    insertion order, which P6 inherits from nothing. This is also the termination
    lookup: "have we already tried OCR for this content hash" is
    `any("ocr" in tiers for tiers in passes_for(...))`, a fact on disk rather than a
    flag someone remembers to set.
    """
    rows = conn.execute(
        f"SELECT analysis_tiers FROM {FACT_PASSES_TABLE} "
        "WHERE file_id = ? AND content_hash = ? ORDER BY pass_id",
        (file_id, content_hash)).fetchall()
    return tuple(frozenset(json.loads(row["analysis_tiers"])) for row in rows)


def no_usable_facts_for(
        conn: sqlite3.Connection, *,
        usable_threshold: Callable[[Sequence[sqlite3.Row], Sequence[sqlite3.Row]],
                                   bool]) -> Callable[[str, str], bool]:
    """Done-means 28. The exact `Callable[[str, str], bool]` P5 already requires.

    `usable_threshold` receives the two row lists for the version -- the facts, then
    the `unresolved` rows -- and returns **True when the stored facts ARE usable**.
    This function returns the negation, which is what §2.2 asks for. Which facts count
    and how many is Deferred by name ("The `no_usable_facts` threshold -- M11, P5
    OQ1"), so it is a required keyword with no default and nothing here chooses.

    The `unresolved` rows are passed because the SPEC makes them evidence FOR the
    verdict, not merely the absence of facts: a version whose every attempted field
    ended in a recorded refusal is a version whose text yielded nothing, and that is
    a stronger statement than an empty fact list.

    **Read the module docstring before passing this anywhere.**
    """

    def no_usable_facts(file_id: str, content_hash: str) -> bool:
        if not passes_for(conn, file_id=file_id, content_hash=content_hash):
            raise FactPassNotRun(
                f"no P6 deterministic pass is recorded for {file_id!r} at "
                f"{content_hash!r}; §2.2's verdict is defined only after that pass "
                "has completed, and answering here would be a statement about rows "
                "that do not exist yet")
        return not usable_threshold(
            facts_for_file(conn, file_id, content_hash),
            unresolved_for_file(conn, file_id, content_hash))

    return no_usable_facts
```

- [ ] **Step 3b: Add two lines to `src/facts/schema.py`**

`create_facts_schema` creates the four published records; the pass record is created with them so
one call still builds every table P6 owns. Add exactly these two lines — the import is **local to the
function**, not at module scope, because `facts.usable` imports `facts.file_facts` and
`facts.unresolved`, and a module-level import here would make the schema module depend on two
modules that may in turn reach back to it:

**Line 1**, as the last statement inside `create_facts_schema`, after the four published records
are created (if the function ends with a `return`, immediately before it):

```python
    create_fact_passes(conn)              # P6's fifth, internal table (PLAN Task 19)
```

**Line 2**, the import it needs, placed on the line *above* it — **inside the function body, not at
module scope**:

```python
    from facts.usable import create_fact_passes   # local import: see below
```

The import is local because `facts.usable` imports `facts.file_facts` and `facts.unresolved`, and a
module-scope import here would make the schema module depend on two modules that Tasks 4 and 5 build
against it. A function-local import is the standard fix and costs one call's lookup at schema
creation time, which happens once per database.

Nothing else in `schema.py` changes. No existing line is edited, reordered or removed.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_usable.py -v`
Expected: PASS — 14 passed

- [ ] **Step 5: Run the whole P6 suite, to prove the schema edit broke nothing**

Run: `pytest tests/p6 -q`
Expected: PASS — every earlier task's tests still green, because `create_facts_schema` gained one
table and changed none.

- [ ] **Step 6: Commit**

```bash
git add src/facts/usable.py src/facts/schema.py tests/p6/test_p6_usable.py
git commit -m "feat(P6): M11 no_usable_facts and the recorded pass — a read surface, deliberately unwired"
```

---

## Contract notes for Tasks 16–19

Reported, not resolved. Each is a decision someone owes; none is answered inside an implementation.

1. **`normalize` and `contradicts` have no owner (round 4, C-5, Task 17).** P8's SPEC names both as
   things it receives *from* P6, and files their domain logic back to P6 in its own Deferred table;
   P6's Task 17 says P6 owns none of the checking. Neither part builds them. Task 17 supplies the
   four inputs as the skeleton says, publishes neither function, and pins that with a test.
   **Owed: a ruling before P8 is planned.** If the answer is P6, it is a new P6 task — the request
   shape does not change either way.

2. **`facts` imports one name from `extractors` (Task 19).** `extractors.failure.ContractViolation`,
   as `FactPassNotRun`'s base class, and nothing else. It creates no cycle and carries no per-format
   knowledge, but it is an edge that did not exist in the skeleton's dependency picture. **Task 25's
   no-invention guard should permit exactly this import and no other from `extractors`.**

3. **The skeleton says four tables; Task 19 adds a fifth (Task 19).** `fact_passes` is P6-internal,
   read by no neighbour, and carries no claim about any file. The clause that binds — *"creates none
   of anyone else's"* — is untouched. Stated so a reviewer counting tables is not surprised.

4. **`FactPassNotRun`'s base class differs from the skeleton's `Exception` (Task 19).** Changed to
   `ContractViolation` on the ratified ruling, because a plain `Exception` is swallowed by
   `orchestrator._extract_one` into a `failed` run and the guard stops guarding.

5. **The tier-3-only refusal is a reading, and it is the one rule Task 16 states that §3.7's
   arithmetic cannot reach.** §2.6's *"must not mistake the absence of EXIF for proof that an image
   is a screenshot"* is unconditional and A07 is a Done-means-grade prohibition, so it cannot rest on
   an injected number. The reason is `below_margin` because the SPEC files *"the
   conflicting-image-signal case (§2.6)"* there by name. If a reviewer prefers a different reason, it
   is a one-word change in `media_type` and one word in the test.

6. **Task 16 assumes `fill_or_abstain` measures the margin against an absent second-best as zero
   (Task 11's contract).** A file carrying only photo-band observations passes one candidate. If
   Task 11 instead refuses a single-candidate list, `test_a_missing_signal_contributes_nothing_to_
   either_candidate` fails and the two authors reconcile — which is the correct place for a
   cross-task disagreement to surface, and is why it is written as a test rather than as an
   assumption in prose.

7. **`ActivationSignals`' shape is Task 13's (Task 17).** The test builds an empty one from the
   dataclass's own field list and annotations rather than hard-coding a shape it does not own; if
   Task 13 declares a field type outside the small map, the assertion fails with that field's name.

8. **The §3.4 cache-key reconciliation is still written out per producer.** Task 16 repeats the rule
   `PLAN-tasks-14-15.md` states once, for the same reason: `facts.cache` is Task 6's module and these
   tasks cannot add to it without breaking its contract. Task 17 is the one place in this file where
   `model_identifier` and `prompt_fingerprint` are not `None`, and its tier is `ANALYSIS_TIERS[-1]`
   unconditionally.
