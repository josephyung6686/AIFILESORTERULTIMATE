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
  `ExtractionResult(run={}, text_units=({"text": "..."},))` constructs. `ocr_policy._has_text`
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
