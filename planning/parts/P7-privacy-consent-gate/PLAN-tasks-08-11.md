# P7 — Privacy and consent gate — PLAN, Tasks 8–11

> This file is one section of P7's implementation plan. Tasks 1–7 are written by another author
> against the same [`PLAN-SKELETON.md`](PLAN-SKELETON.md), and Tasks 12–22 by two more; everything
> they publish is consumed here under the names the skeleton's `Interfaces:` blocks fix. Format and
> standard are [`../P5-extractors/PLAN.md`](../P5-extractors/PLAN.md) and
> [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md), and the sibling section
> [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md). No placeholders, anywhere.

**Verified against the live substrate, 2026-08-22.** Every P1–P4 signature quoted below was read
with `inspect.signature` against the shipped packages and every behaviour below was executed against
a real SQLite database, not read out of a PLAN. The six facts that most change what is written here:

- `evidence_shape.store.observations_by_key(conn, observation_key) -> list[Observation]` returns
  **two rows** when two extractor versions carry one key, and `Observation` — seventeen fields —
  carries **neither `observation_id` nor `superseded_by`**. Supersession lives on the `evidence`
  **row**, not on the dataclass. Task 9 therefore cannot pick the current row out of that list, and
  the gap is closed here with one narrow read plus P4's published `get_observation`. Reported.
- `evidence_shape.store.get_observation(conn, observation_id) -> Observation` exists and is
  published. It is the second half of the current-row rule.
- `evidence_shape.store.unit_for_observation(conn, observation)` returns **`None`** for a
  container-path-only address — there is no `TextUnit` at a spreadsheet cell — which is what makes
  §2.3's addressing a **second** resolution path and not a degenerate case of the first.
- `evidence_shape.text_units.check_span_anchor(observation, unit)` **raises `SpanAnchorError` when
  `observation.location.text_span is None`**, with the message *"rule 10 applies to an observation
  with a non-null text_span; this one has none and needs no unit"*. It cannot be used as a
  general-purpose validator; it is the text-span path's precondition and nothing else's.
- `evidence_shape.locator.serialize_locator(location)` **drops the region**. A
  `Location(zone="ocr", container_path=(page=2,), region=Region(...))` serialises to `'ocr:page=2'`,
  and `parse_locator(text, *, region=None)` takes the region back as a **separate argument**. P4's
  own canonical address cannot carry a bounding box, which is the mechanical form of C3 below.
- `database_agent.events.append_event` accepts seventeen named columns and rejects a hidden
  eighteenth with `MalformedEvent`; five of them are what the audit record has a column for
  (`file_id`, `content_hash`, `prompt_fingerprint`, `user_id`, `observed_at`), and `_REQUIRED`
  includes `explanation` and rejects the empty string. `append_event` returns `cursor.lastrowid`.

---

## Four rulings that bind this section, applied rather than restated

**Task 9 is the one place in the repository where an `(observation_key, span)` becomes a string of
document text.** Not "the one place in P7" — the one place in the product. Everything else holds
references. `resolve.py` is the only module under `src/privacy/` that binds a P4 text materialiser,
`release.py` is the only module that imports `resolve`, and Task 21 asserts both repo-wide. The
handle is P4's content-addressed `observation_key` and **never** the per-row `observation_id`, which
dies on extractor upgrade (M14): *"The key, not the id, is what makes that durable."*

**The gate refuses RELEASE, not reading, and it is the third of four refusals.** P5's
`ProtectedContainerRefused` refuses *reading* and produces nothing at all; `DatalessRefused` refuses
*reading* and produces one `dataless` run; P7's `Denied` refuses *release* — the bytes were read
locally, lawfully, long ago — and is the only one of the three that consent may override.
`ContractViolation` is a fourth kind and is about the CALL, so it always propagates. `src/privacy/`
imports **none** of `extractors`' three refusals and Task 21 asserts their absence.

**`Gate.release` writes exactly one thing and raises nothing.** C4: *"a gate that also wrote would
be doing two jobs."* The one write is the audit event, and it is inside the decision because §8.4
makes it a precondition of the release rather than a consequence of it — *"Every model call should
be recorded in a consent-aware audit record."* A release returned before its record existed would
open an interval in which content is releasable and unaudited. Everything else the outcome implies —
P8's `Refusal`, P13's consent routing, a classification write — is the **caller's**.

**Absence of a classification resolves to `unreadable_unclassified`, never to a public or low class,
and the detector is unwritten.** No task in any plan produces a rule set, so on a real corpus every
file resolves to `Denied(unclassified)`. Task 11 is written for that: the denial path is the
**ordinary** path and the release path is the one that needs a fixture. `Unreadable or unclassified`
is a gate OUTCOME and never reaches `files.sensitivity_state` (D2).

---

## Two names this section pins for its neighbours, because it cannot be written without them

1. **`redaction.span_address(location) -> str` is published by Task 8 and imported by Task 9.** The
   skeleton gives neither task an address serialiser, and both need one: Task 8's `RedactionEntry`
   has a `span` field and Task 9's `Materialised` has a `span` field, and two independent
   serialisations of one address is the "three spellings" defect this plan already records once. It
   lands in Task 8 because Task 8 is written first and because the reason a region address has **no**
   serialisation is a redaction question (C3, below). Reported as an addition.
2. **`span` is the canonical locator string, everywhere.** `serialize_locator(observation.location)`
   — `'body:page=2#16-27'` for a text span, `'table:sheet=1/row=4/cell=3'` for a container-path
   address. It round-trips through P4's `parse_locator`, which is what makes SPEC §7's requirement
   real: *"a record that cannot reconstruct the released payload from local storage fails §8.4's
   stated purpose."* An opaque `"0-19"` would satisfy the type and not the requirement.

---

## Tasks

### Task 8: Redaction, and a manifest whose identifier class stays opaque

**Files:**
- Create: `src/privacy/redaction.py`
- Test: `tests/p7/test_p7_redaction.py`

**Interfaces:**
- Consumes: `evidence_shape.location.Location`, `.Region`, `.TextSpan`, `.REGION_UNITS`,
  `evidence_shape.locator.serialize_locator(location) -> str`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`redaction.py`):
  - `REGION_ORIGIN_UNDECIDED: str = "NEEDS-JOSEPH C3"` — the key of the open decision, not a
    sentence about it.
  - `IdentifierClassifier` — `Protocol`, `__call__(value: str, *, context_before: str | None,
    context_after: str | None) -> str | None`. **Injected, no default.**
  - `RedactionTransform` — `Protocol`, `__call__(value: str, *, identifier_class: str) -> str`.
    **Injected, no default.**
  - `RedactionEntry` — frozen: `observation_key: str`, `span: str`, `identifier_class: str | None`,
    `redacted: bool`, `context_before: str | None`, `context_after: str | None`,
    `context_truncated: bool`.
  - `RedactionManifest` — frozen: `entries: tuple[RedactionEntry, ...]`; properties `any_redacted`,
    `identifier_classes`; `to_mapping() -> list[dict]`.
  - `RedactionIneffective`, `RegionOriginUnspecified`.
  - `span_address(location: Location) -> str`.
  - `apply_redaction(value: str, *, observation_key: str, span: str, context_before: str | None,
    context_after: str | None, context_truncated: bool, classifier: IdentifierClassifier,
    transform: RedactionTransform) -> tuple[str, RedactionEntry]`.

**Done-means:** 4 (`redaction_applied`), and the redaction half of 12.

**Three deviations from the skeleton's `Interfaces` block, each reported rather than absorbed.**

1. **`apply_redaction` gains `observation_key`, `span` and `context_truncated` as keywords.** The
   skeleton's signature is `apply_redaction(value, *, context_before, context_after, classifier,
   transform)` and its `RedactionEntry` carries `observation_key` and `span` — which that signature
   cannot fill. Three keywords are added, not invented: two are the entry's own published fields and
   the third is M5's third context field, which the skeleton separately requires be *"carried through
   to the manifest, because §8.6 forbids anything being truncated silently."*
2. **`RedactionEntry` gains `context_before`, `context_after` and `context_truncated`.** The
   skeleton requires that redaction *"replaces the **value** and preserves `context_before` and
   `context_after`"*. A function that never returns the context cannot be shown to have preserved
   it; putting the two fields on the entry makes the preservation an assertion instead of an absence.
   This is the whole reason P4 split them (M5): *"M5's three context fields exist so §8.4 can redact
   a value without dropping its context."*
3. **`redaction.py` imports neither `privacy.items` nor `evidence_shape.observation`.** The
   skeleton's `Consumes` names both. `apply_redaction` takes flat values so that Task 7's
   `RedactedIdentifier` and Task 9's `Materialised` can each feed it without `redaction` depending on
   a module written in parallel by a different author. M5's three fields are consumed **as values**,
   which is the substance; the test imports `evidence_shape.observation.Observation` and drives the
   three fields through it, so the seam is still proved against P4's real record.

**The identifier class is an opaque string and this module enumerates none.** SPEC *Deferred*:
*"Which identifier classes exist and how each is transformed is not enumerated anywhere in the
design. `redaction_manifest` carries the class as an opaque string until this is authored."* The
classifier is injected, its return value is stored unexamined, and the test drives a deliberately
absurd class name through to prove nothing validates it. There is no regex, no gazetteer, no keyword
list, and no module-level collection constant of any kind — asserted by **runtime introspection of
the module namespace**, not by scanning source text, because a source scan matches docstrings and
that technique has produced a false result on this project more than once.

**Both protocols are injected with no default, and that is a safety property rather than a style.**
A build that forgets to wire a transform must fail loudly at the call, not emit unredacted values
under a helpful identity function. The test asserts it two ways: the parameters are `KEYWORD_ONLY`
with `inspect.Parameter.empty` defaults, and calling `apply_redaction` without them raises
`TypeError`. A transform that returns its input unchanged is refused with `RedactionIneffective` for
the same reason — an identity transform is the shape a forgotten wiring takes when someone does
supply one.

**C3 — the bounding box, and the guess this task refuses to make.** P4's region is exactly
`(x, y, w, h, unit)` with `unit` in `("px", "norm")`, validated by
`evidence_shape.location.region_from_mapping`. **`norm` does not say which corner it measures
from.** Apple Vision reports normalized coordinates from the **bottom-left**; most tooling — PDF
viewers, HTML canvases, the majority of OCR SDKs — measures from the **top-left**. A redaction that
picked the common convention and was wrong would blank a band mirrored about the horizontal centre
of the page: it would leave the passport number visible and cover something else, while the manifest
recorded `redacted = True`. That is worse than refusing, because the audit record would be false.

So `span_address` **raises `RegionOriginUnspecified`** on a region-addressed location, the message
names `REGION_ORIGIN_UNDECIDED`, and P7 redacts only what it can address in text. The mechanical
evidence that this is a real gap and not a scruple is in P4 itself: `serialize_locator` **drops the
region entirely** — an `ocr` location with a region serialises to `'ocr:page=2'` — and
`parse_locator(text, *, region=None)` takes it back as a separate argument, so P4's own canonical
address has no slot for a box. The test pins `REGION_UNITS == ("px", "norm")` and pins that
`dataclasses.fields(Region)` names no origin, so the day an origin is added the test goes red and
this refusal is revisited rather than forgotten. **NEEDS-JOSEPH C3.**

**The manifest never holds a second copy of the value.** `RedactionEntry` has no `value` field and
no `redacted_value` field, asserted over `dataclasses.fields`. §8.4 puts *"raw sensitive values"* in
the always-local set; a manifest that stored the pre-redaction value would be a local record of
exactly the thing the redaction removed, sitting in the same JSON blob that gets written to the audit
log. What the entry stores is the class, the yes/no, the address, and the context — which is what
SPEC §6 asks for: *"redaction_manifest[]  per item: identifier class, redacted yes/no."*

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_redaction.py
"""§8.4's "redacted identifiers", and the manifest that records what was redacted.

Four things this test refuses to let the implementation do:

- **Name an identifier class.** The SPEC's *Deferred* table says the classes are not
  enumerated anywhere in the design, so a nonsense class name is driven end to end and
  nothing may validate it.
- **Ship a default transform.** A build that forgets to wire one must fail at the call.
- **Throw away the context.** M5 split `context_before` / `context_after` /
  `context_truncated` out of `raw_value` precisely so §8.4 could redact a value without
  dropping what surrounds it.
- **Guess which corner `Region`'s `norm` unit measures from.** NEEDS-JOSEPH C3.
"""
import dataclasses
import inspect
import json

import pytest

from evidence_shape.canonical import canonical_json
from evidence_shape.location import (
    REGION_UNITS, Location, Region, Segment, TextSpan, TimeSpan,
)
from evidence_shape.locator import parse_locator, serialize_locator
from evidence_shape.observation import Observation

import privacy.redaction as redaction_module
from privacy.redaction import (
    REGION_ORIGIN_UNDECIDED, RedactionEntry, RedactionIneffective, RedactionManifest,
    RegionOriginUnspecified, apply_redaction, span_address,
)

CONTENT_HASH = "a" * 64
VALUE = "992-33-1188"
BEFORE = "Passport number "
AFTER = " issued 2019."
PAGE = (Segment(kind="page", index=2),)
TEXT_LOCATION = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
CELL_LOCATION = Location(zone="table", container_path=(
    Segment(kind="sheet", index=1), Segment(kind="row", index=4),
    Segment(kind="cell", index=3)))
OCR_LOCATION = Location(zone="ocr", container_path=PAGE,
                        region=Region(0.10, 0.22, 0.30, 0.04, "norm"))
KEY = "sha256:" + "b" * 64

#: Deliberately not a plausible identifier class. If anything in `src/privacy/`
#: validated, normalised, or recognised the class, this string would not survive.
ABSURD_CLASS = "  zzz-NOT-A-REAL-CLASS-éé  "


def classifier_naming(name):
    """An injected classifier. P7 owns no rule that decides what an identifier is."""
    def classify(value, *, context_before, context_after):
        return name
    return classify


def classifier_declining(value, *, context_before, context_after):
    """The other half of the injection: a value that is not an identifier."""
    return None


def transform_masking(value, *, identifier_class):
    return "[redacted]"


def transform_returning_the_value(value, *, identifier_class):
    """The shape a forgotten wiring takes when somebody does supply one."""
    return value


def redact(**over):
    base = dict(observation_key=KEY, span=span_address(TEXT_LOCATION),
                context_before=BEFORE, context_after=AFTER, context_truncated=False,
                classifier=classifier_naming("passport_number"),
                transform=transform_masking)
    base.update(over)
    return apply_redaction(VALUE, **base)


# --- the class is opaque, and this module enumerates none ---------------------

def test_the_identifier_class_is_whatever_the_classifier_said():
    # SPEC *Deferred*: "`redaction_manifest` carries the class as an opaque string
    # until this is authored." Whitespace, case and non-ASCII all survive, which is
    # what "opaque" means and what "normalised" would not.
    _, entry = redact(classifier=classifier_naming(ABSURD_CLASS))
    assert entry.identifier_class == ABSURD_CLASS


def test_src_privacy_redaction_enumerates_no_identifier_class():
    # The no-invention guard, by RUNTIME INTROSPECTION of the module namespace and
    # not by reading source text: a text scan matches docstrings, and this project
    # has already recorded that failure more than once. The one string constant is
    # the key of an open question; there is no collection constant at all.
    strings, collections = {}, {}
    for name, value in vars(redaction_module).items():
        if name.startswith("_"):
            continue
        if isinstance(value, str):
            strings[name] = value
        elif isinstance(value, (tuple, list, set, frozenset, dict)):
            collections[name] = value
    assert set(strings) == {"REGION_ORIGIN_UNDECIDED"}, strings
    assert collections == {}, (
        "a gazetteer, a class list, or a transform table would land here; §8.4 "
        "states WHAT is protected and never HOW it is recognised")


def test_the_open_question_is_carried_as_a_key_and_not_as_a_sentence():
    # The same rule the retraction limit follows: P7 asserts the obligation and
    # holds none of the copy.
    assert REGION_ORIGIN_UNDECIDED == "NEEDS-JOSEPH C3"


# --- both protocols are injected, with no default -----------------------------

def test_the_classifier_and_the_transform_are_keyword_only_with_no_default():
    parameters = inspect.signature(apply_redaction).parameters
    for name in ("classifier", "transform"):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert parameters[name].default is inspect.Parameter.empty, (
            f"{name} has a default; a build that forgets to wire one would then "
            "emit unredacted values under a helpful identity function")


def test_apply_redaction_cannot_be_called_without_them():
    with pytest.raises(TypeError):
        apply_redaction(VALUE, observation_key=KEY, span=span_address(TEXT_LOCATION),
                        context_before=BEFORE, context_after=AFTER,
                        context_truncated=False)


def test_a_transform_that_returns_the_value_is_refused():
    with pytest.raises(RedactionIneffective):
        redact(transform=transform_returning_the_value)


# --- what redaction does, and what it leaves alone ----------------------------

def test_redaction_replaces_the_value():
    redacted, entry = redact()
    assert redacted == "[redacted]"
    assert entry.redacted is True


def test_a_declining_classifier_leaves_the_value_alone():
    # Not every materialised value is an identifier. §8.4 permits "selected excerpts"
    # beside "redacted identifiers"; an excerpt the injected rule set does not
    # recognise passes through, and the entry records that it was not redacted.
    redacted, entry = redact(classifier=classifier_declining)
    assert redacted == VALUE
    assert entry.redacted is False
    assert entry.identifier_class is None


def test_redaction_preserves_the_context():
    # M5, and the reason P4 split the field: "a redaction that returns the whole
    # surrounding text has thrown away the reason the fields were split" -- and one
    # that blanks the context has thrown away the other half.
    observation = Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name="pdf_text",
        extractor_version="1.0.0", source_type="text_document", raw_value=VALUE,
        location=TEXT_LOCATION, occurrence_count=1,
        observed_at="2026-08-22T12:00:00+00:00", reliability="direct", run_id="run-1",
        context_before=BEFORE, context_after=AFTER, context_truncated=False)
    redacted, entry = apply_redaction(
        observation.raw_value, observation_key=KEY,
        span=span_address(observation.location),
        context_before=observation.context_before,
        context_after=observation.context_after,
        context_truncated=observation.context_truncated,
        classifier=classifier_naming("passport_number"), transform=transform_masking)
    assert redacted == "[redacted]"
    assert entry.context_before == BEFORE
    assert entry.context_after == AFTER
    assert VALUE not in entry.context_before + entry.context_after


def test_context_truncated_is_carried_through_to_the_entry():
    # §8.6 forbids anything being truncated silently. The flag is P4's third context
    # field and it is not a detail the manifest may drop.
    _, entry = redact(context_truncated=True)
    assert entry.context_truncated is True


def test_the_entry_holds_no_copy_of_the_value():
    # "raw sensitive values" are in §8.4's always-local set. A manifest that stored
    # the pre-redaction value would be a local copy of exactly what was removed,
    # inside the JSON that gets written to the audit log.
    names = {field.name for field in dataclasses.fields(RedactionEntry)}
    assert names == {"observation_key", "span", "identifier_class", "redacted",
                     "context_before", "context_after", "context_truncated"}
    assert "value" not in names and "redacted_value" not in names


def test_the_entry_is_frozen():
    _, entry = redact()
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.redacted = False


# --- the manifest -------------------------------------------------------------

def test_the_manifest_is_the_per_item_record():
    # SPEC §6: "redaction_manifest[]  per item: identifier class, redacted yes/no."
    _, one = redact(classifier=classifier_naming("passport_number"))
    _, two = redact(classifier=classifier_declining)
    manifest = RedactionManifest(entries=(one, two))
    assert manifest.identifier_classes == ("passport_number", None)
    assert manifest.any_redacted is True


def test_a_manifest_with_nothing_redacted_says_so():
    _, only = redact(classifier=classifier_declining)
    assert RedactionManifest(entries=(only,)).any_redacted is False
    assert RedactionManifest(entries=()).any_redacted is False


def test_the_manifest_serialises_as_canonical_json():
    # It travels inside the audit record's `explanation` (the preamble's shape
    # decision), so it has to survive `canonical_json` without a custom encoder.
    _, entry = redact()
    payload = canonical_json(RedactionManifest(entries=(entry,)).to_mapping())
    assert json.loads(payload) == [{
        "observation_key": KEY, "span": "body:page=2#16-27",
        "identifier_class": "passport_number", "redacted": True,
        "context_before": BEFORE, "context_after": AFTER,
        "context_truncated": False}]


# --- span_address, and the two forms it serialises ----------------------------

def test_span_address_of_a_text_span_is_p4s_canonical_locator():
    assert span_address(TEXT_LOCATION) == "body:page=2#16-27"
    assert parse_locator(span_address(TEXT_LOCATION)) == TEXT_LOCATION


def test_span_address_of_a_container_path_address_is_the_same_serialiser():
    # §2.3's table/row/cell has no text span at all; the address IS the citation.
    assert span_address(CELL_LOCATION) == "table:sheet=1/row=4/cell=3"
    assert parse_locator(span_address(CELL_LOCATION)) == CELL_LOCATION


# --- C3: the bounding box this task will not guess at -------------------------

def test_a_region_address_is_refused_and_names_the_open_decision():
    with pytest.raises(RegionOriginUnspecified) as caught:
        span_address(OCR_LOCATION)
    assert REGION_ORIGIN_UNDECIDED in str(caught.value)


def test_p4s_region_names_no_origin():
    # (x, y, w, h, unit) and unit in ("px", "norm"). Neither says which corner the
    # origin sits in: Apple Vision measures from bottom-left, most tooling from
    # top-left, and a wrong guess covers a band mirrored about the page centre --
    # leaving the value visible while the manifest records `redacted = True`.
    assert REGION_UNITS == ("px", "norm")
    assert tuple(f.name for f in dataclasses.fields(Region)) == (
        "x", "y", "w", "h", "unit")


def test_p4s_own_canonical_address_cannot_carry_a_region_either():
    # The mechanical form of C3, and the reason this is a gap rather than a scruple:
    # `serialize_locator` drops the region, and `parse_locator` takes it back as a
    # SEPARATE argument. There is no slot for a box in the address.
    assert serialize_locator(OCR_LOCATION) == "ocr:page=2"
    assert parse_locator("ocr:page=2").region is None
    assert parse_locator("ocr:page=2", region=OCR_LOCATION.region) == OCR_LOCATION


def test_a_time_span_address_is_refused_too():
    # A transcript offset is an address P7 publishes no redaction for. §2.9 puts
    # speech-to-text behind "an explicit privacy and compute policy" and this task
    # owns none of it; refusing is the honest answer, and it is not C3's question.
    spoken = Location(zone="transcript", container_path=(),
                      time_span=TimeSpan(1000, 2000))
    with pytest.raises(RegionOriginUnspecified):
        span_address(spoken)
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_redaction.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.redaction'`. Collection fails on the
import line; no test runs.

- [ ] **Step 3: Write `src/privacy/redaction.py`**

```python
# src/privacy/redaction.py
"""§8.4's "redacted identifiers", and the manifest that says what was redacted.

Four things are decided here, and each is a quotation or a refusal rather than a
choice:

- **The identifier class is an opaque string.** SPEC *Deferred*: "Which identifier
  classes exist and how each is transformed is not enumerated anywhere in the design.
  `redaction_manifest` carries the class as an opaque string until this is authored."
  Nothing in this module validates, normalises, or recognises one.
- **The classifier and the transform are injected with no default.** §8.4 states WHAT
  is protected and never HOW it is recognised. A default would be a rule set, and a
  default that did nothing would be an unredacted value emitted by a build that forgot
  to wire one.
- **The value is replaced and its context is not.** M5 split `context_before`,
  `context_after` and `context_truncated` out of the observation "precisely so §8.4
  can redact a value without dropping its context". Both halves of that are properties
  of the entry this module returns, so both can be asserted.
- **A region address is refused, by name (NEEDS-JOSEPH C3).** P4's region is
  `(x, y, w, h, unit)` with `unit` in `("px", "norm")` and neither unit names the
  corner the origin sits in. Apple Vision measures normalized coordinates from the
  bottom-left; most tooling measures from the top-left. Guessing would blank a band
  mirrored about the page's horizontal centre -- the value still visible, the manifest
  still saying `redacted = True`, which is worse than refusing because it makes the
  audit record false. P4's own `serialize_locator` drops the region and `parse_locator`
  takes it back separately, so there is not even an address to record.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from evidence_shape.location import Location
from evidence_shape.locator import serialize_locator

#: The open decision this module refuses to make. A key, not a sentence: the wording
#: belongs to whoever answers it, exactly as §8.4's retraction-limit copy does.
REGION_ORIGIN_UNDECIDED: str = "NEEDS-JOSEPH C3"


class RedactionIneffective(Exception):
    """The transform returned its input. That is not a redaction, and recording it
    as one would put a false `redacted = True` in the audit log."""


class RegionOriginUnspecified(Exception):
    """The address is a bounding box and no origin corner is defined (C3).

    Also raised for a time span, for the narrower reason that P7 publishes no
    redaction for a transcript offset at all. Both are "this address has no
    redactable form here", and neither is a silent fallback to the whole unit.
    """


class IdentifierClassifier(Protocol):
    """The injected rule set. Returns an opaque class name, or None for a value that
    is not an identifier. P7 ships no implementation of this protocol."""

    def __call__(self, value: str, *, context_before: str | None,
                 context_after: str | None) -> str | None: ...


class RedactionTransform(Protocol):
    """The injected transform. §8.4 says "redacted identifiers" and never says how."""

    def __call__(self, value: str, *, identifier_class: str) -> str: ...


@dataclass(frozen=True, slots=True)
class RedactionEntry:
    """One row of SPEC §6's `redaction_manifest[]`: "per item: identifier class,
    redacted yes/no" -- plus the address it applies to and M5's three context fields.

    There is deliberately no `value` and no `redacted_value`. §8.4 puts "raw sensitive
    values" in the always-local set, and this record travels inside the audit event's
    `explanation`.
    """

    observation_key: str
    span: str
    identifier_class: str | None
    redacted: bool
    context_before: str | None
    context_after: str | None
    context_truncated: bool

    def to_mapping(self) -> dict[str, object]:
        return {
            "observation_key": self.observation_key,
            "span": self.span,
            "identifier_class": self.identifier_class,
            "redacted": self.redacted,
            "context_before": self.context_before,
            "context_after": self.context_after,
            "context_truncated": self.context_truncated,
        }


@dataclass(frozen=True, slots=True)
class RedactionManifest:
    """SPEC §6's `redaction_manifest[]`, as one object so `Released` carries one field."""

    entries: tuple[RedactionEntry, ...]

    @property
    def any_redacted(self) -> bool:
        """§8.4's audit field: "whether values were redacted"."""
        return any(entry.redacted for entry in self.entries)

    @property
    def identifier_classes(self) -> tuple[str | None, ...]:
        return tuple(entry.identifier_class for entry in self.entries)

    def to_mapping(self) -> list[dict[str, object]]:
        return [entry.to_mapping() for entry in self.entries]


def span_address(location: Location) -> str:
    """P4's canonical locator, and the two addressing forms P7 can redact.

    A text span serialises to `body:page=2#16-27`; a container-path address to
    `table:sheet=1/row=4/cell=3`. Both round-trip through `parse_locator`, which is
    what lets SPEC §7's audit record "reconstruct the released payload from local
    storage" rather than merely name it.

    A region or a time span raises. `serialize_locator` drops a region, so the string
    it returns would silently address the whole page.
    """
    if location.region is not None:
        raise RegionOriginUnspecified(
            f"{location.zone}:{serialize_locator(location)} carries a bounding box "
            f"and `Region(x, y, w, h, unit)` names no origin corner -- `norm` is "
            f"bottom-left in Apple Vision and top-left in most other tooling, so a "
            f"redaction band placed from a guess covers a mirrored region while the "
            f"manifest records it as redacted. P4's own locator drops the region "
            f"(`{serialize_locator(location)}`) and `parse_locator` takes it back as "
            f"a separate argument, so there is no address to record either. "
            f"{REGION_ORIGIN_UNDECIDED}")
    if location.time_span is not None:
        raise RegionOriginUnspecified(
            f"{serialize_locator(location)} is a transcript offset and P7 publishes "
            f"no redaction for one; §2.9 puts speech-to-text behind an explicit "
            f"privacy and compute policy this task does not own")
    return serialize_locator(location)


def apply_redaction(value: str, *, observation_key: str, span: str,
                    context_before: str | None, context_after: str | None,
                    context_truncated: bool, classifier: IdentifierClassifier,
                    transform: RedactionTransform) -> tuple[str, RedactionEntry]:
    """Redact one materialised value, and record what was done to it.

    Returns `(value_to_release, entry)`. The context is returned on the entry
    unchanged: M5's fields exist so a value can be redacted without dropping what
    surrounds it, and a caller that has both can prove it kept them.
    """
    identifier_class = classifier(value, context_before=context_before,
                                  context_after=context_after)
    if identifier_class is None:
        return value, RedactionEntry(
            observation_key=observation_key, span=span, identifier_class=None,
            redacted=False, context_before=context_before,
            context_after=context_after, context_truncated=context_truncated)
    redacted = transform(value, identifier_class=identifier_class)
    if redacted == value:
        raise RedactionIneffective(
            f"the transform returned its input for identifier_class "
            f"{identifier_class!r}; recording that as `redacted = True` would put a "
            f"false statement in the §8.4 audit record, and returning it as redacted "
            f"would release the value")
    return redacted, RedactionEntry(
        observation_key=observation_key, span=span,
        identifier_class=identifier_class, redacted=True,
        context_before=context_before, context_after=context_after,
        context_truncated=context_truncated)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_redaction.py -v`
Expected: PASS — 21 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–8 green, and P1–P5's 1292 tests still green (P7 modified no file belonging
to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/redaction.py tests/p7/test_p7_redaction.py
git commit -m "feat(P7): redaction with an opaque identifier class, and a region address refused by name (C3)"
```

---

### Task 9: Excerpt resolution — the only place content materialises

**Files:**
- Create: `src/privacy/resolve.py`
- Test: `tests/p7/test_p7_resolve.py`

**Interfaces:**
- Consumes: `evidence_shape.store.observations_by_key(conn, observation_key) ->
  list[Observation]`, `.get_observation(conn, observation_id) -> Observation`,
  `.unit_for_observation(conn, observation) -> TextUnit | None`,
  `evidence_shape.text_units.raw_value_at(unit, text_span) -> str`,
  `.check_span_anchor(observation, unit) -> None`, `.SpanAnchorError`,
  `evidence_shape.location.TextSpan`, `privacy.redaction.span_address(location) -> str`,
  `.RegionOriginUnspecified`.
- Produces (`resolve.py`):
  - `Materialised` — frozen: `observation_key: str`, `span: str`, `value: str`, `zone: str`,
    `context_before: str | None`, `context_after: str | None`, `context_truncated: bool`,
    `unit_length: int | None`.
  - `MATERIALISERS: Mapping[str, tuple[str, ...]]` — the P4 functions that turn a record into text,
    by module, so the single-locus guard has a subject rather than a guess.
  - `UnresolvableSpan`, `AmbiguousObservationKey`.
  - `current_observation(conn, observation_key) -> Observation`.
  - `materialise(conn, item) -> Materialised`.

**Done-means:** substrate for 3 (L2), 4, 5, 6.

**This module is the door's threshold, and everything about it is narrow on purpose.** It is the
only module under `src/privacy/` that imports a P4 text materialiser; `release.py` is the only module
that imports it; and Task 21 re-asserts both repo-wide. `MATERIALISERS` is published here so that
guard names the eight functions rather than pattern-matching on the word "text".

**The current-row rule, and the P4 gap it exposes — reported, and closed with one narrow read.**
P4's docstring is explicit that the reader is multi-valued: *"A LIST: two extractor versions carry
one key, which is what MINOR 8 arranged and what §8.5's cross-version diff reads."* The gate must
resolve to the **current** row, because resolving to a superseded one releases text an extractor
upgrade has already retracted. But — verified by import, 2026-08-22 — `Observation` has seventeen
fields and **`observation_id` and `superseded_by` are not among them**; supersession lives on the
`evidence` row, and P4's `supersede_chain(conn, observation_id)` needs an id the list does not carry.
**There is no published reader that returns the current row for a key.**

So `current_observation` does exactly one thing P4 does not publish — a read-only

```sql
SELECT observation_id FROM evidence WHERE observation_key = ? AND superseded_by IS NULL
```

— and then hands the id straight back to P4's published `get_observation`. It is a **read**, not a
write; P7 modifies no P1–P5 file; and the whole of the record's construction stays P4's. **The
addition that would remove it is one function, `evidence_shape.store.current_observation_by_key(conn,
observation_key) -> Observation | None`**, and it belongs in P4 rather than here. Reported, not
patched — the same posture this plan takes on P5's zero-argument `transcription_authorized`.

**Two resolvers, and no third; a missing resolver is a refusal, not a fallback.**

- **`text_span` → `raw_value_at(unit, text_span)`.** The precondition is P4's own
  `check_span_anchor`, which *"raises; never returns a repair"*. A `SpanAnchorError` becomes
  `UnresolvableSpan`, chained with `from`, and no substring is returned. A gate that repaired would
  release text nobody addressed — and P4 does **not** validate the anchor at write time (verified: a
  non-anchoring observation records cleanly), so this check is load-bearing rather than belt-and-braces.
- **container-path only → `Observation.raw_value`.** §2.3's table/row/cell and §2.8's EXIF field are
  addressed entirely by `container_path`, and `unit_for_observation` returns **`None`** for them —
  verified against a real database. There is no unit, so there is nothing to take a substring of, and
  the materialisable value is the observation's own `raw_value`. It must **never** fall back to the
  whole unit: that is how "send the cell" becomes "send the sheet".
- **A region or a time span raises `RegionOriginUnspecified`** through `span_address` (Task 8, C3).
  P7 publishes no third resolver, and the refusal is what keeps the two above honest.

**Task 9 pins one field of Task 7's items, because it cannot resolve without knowing its type.**
`Excerpt.span` and `RedactedIdentifier.span` are `evidence_shape.location.TextSpan | None` — `None`
for the container-path form, where the address is the whole citation. SPEC §4 spells the items as
`{ observation_key, span, reason }` and `{ observation_key, span, identifier_class }`; P4's span type
is `TextSpan` and Task 7's `Consumes` already imports it. Reported as a pin.

**The caller's span is a claim; the observation's span is the answer.** SPEC §4: an excerpt is
*"resolved by the gate from local storage"*. If `item.span` disagrees with
`observation.location.text_span`, that is `UnresolvableSpan` — the caller has addressed something the
key does not carry, and the gate neither honours the caller's coordinates nor silently substitutes
its own.

**M14, made falsifiable.** A caller who passes an `observation_id` where an `observation_key` belongs
gets `UnresolvableSpan`, because `observations_by_key` returns `[]` for it. That is the test that
makes *"The key, not the id, is what makes that durable"* a property rather than a convention.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_resolve.py
"""The one place in the repository where (observation_key, span) becomes text.

Everything here is about narrowness. Two resolvers and no third; the current row and
not the first; a refusal where P4 gives no answer, never a best-effort substring; and
an AST guard proving no other module under `src/privacy/` binds a P4 materialiser.
"""
import ast
import dataclasses
import pathlib

import pytest

from evidence_shape.location import Location, Region, Segment, TextSpan, TimeSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    get_observation, observations_by_key, record_observation, record_run,
    record_text_unit, supersede_observation, unit_for_observation,
)
from evidence_shape.text_units import TextUnit

import privacy
from privacy.redaction import RegionOriginUnspecified, span_address
from privacy.resolve import (
    MATERIALISERS, AmbiguousObservationKey, Materialised, UnresolvableSpan,
    current_observation, materialise,
)

CONTENT_HASH = "a" * 64
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T13:00:00+00:00"
PAGE = (Segment(kind="page", index=2),)
BODY = "Passport number 992-33-1188 issued 2019."
VALUE = "992-33-1188"
BEFORE = "Passport number "
AFTER = " issued 2019."
CELL = (Segment(kind="sheet", index=1), Segment(kind="row", index=4),
        Segment(kind="cell", index=3))


class Item:
    """Stands in for Task 7's `Excerpt` / `RedactedIdentifier`.

    Task 9 reads exactly two attributes -- `observation_key` and `span` -- and Task 7
    owns the rest of the shape. A local stand-in keeps this test from going red when a
    field this module never touches is added next door, and states the pin: `span` is
    a `TextSpan | None`.
    """

    def __init__(self, observation_key: str, span: TextSpan | None):
        self.observation_key = observation_key
        self.span = span


@pytest.fixture()
def evidence(p7_conn):
    create_evidence_schema(p7_conn)
    return p7_conn


def a_run(conn, run_id, version, started):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="pdf_text", extractor_version=version,
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=started, observation_count=1))


def an_observation(conn, *, run_id, version, location, raw_value=VALUE,
                   context_before=BEFORE, context_after=AFTER,
                   context_truncated=False, extractor_name="pdf_text",
                   source_type="text_document", observed_at=FIXED_CLOCK) -> str:
    return record_observation(conn, Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name=extractor_name,
        extractor_version=version, source_type=source_type, raw_value=raw_value,
        location=location, occurrence_count=1, observed_at=observed_at,
        reliability="direct", run_id=run_id, context_before=context_before,
        context_after=context_after, context_truncated=context_truncated))


def key_for(location, *, extractor_name="pdf_text", raw_value=VALUE) -> str:
    """P4 mints the key from `serialize_locator`, not from `span_address`.

    They agree on the two forms P7 can resolve and differ on the two it refuses --
    `span_address` raises for a region and a time span, and P4 still has a key for
    both. The key is P4's, so the test computes it P4's way.
    """
    return observation_key(content_hash=CONTENT_HASH, extractor_name=extractor_name,
                           locator=serialize_locator(location), raw_value=raw_value)


@pytest.fixture()
def one_excerpt(evidence):
    """One run, one unit, one observation: the ordinary text-span case."""
    a_run(evidence, "run-1", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-1", version="1.0.0", location=location)
    return key_for(location), location


# --- the ordinary text-span path ---------------------------------------------

def test_a_text_span_materialises_the_substring(evidence, one_excerpt):
    key, location = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.value == VALUE
    assert result.value == BODY[16:27]


def test_the_result_carries_the_key_the_address_and_the_zone(evidence, one_excerpt):
    key, location = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.observation_key == key
    assert result.span == "body:page=2#16-27" == span_address(location)
    assert result.zone == "body"


def test_the_three_context_fields_travel_with_the_value(evidence, one_excerpt):
    # M5, and Task 8's whole reason for existing: §8.4 redacts the value without
    # dropping what surrounds it, so the value cannot arrive at the redactor alone.
    key, _ = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.context_before == BEFORE
    assert result.context_after == AFTER
    assert result.context_truncated is False


def test_context_truncated_travels_too(evidence):
    # §8.6 forbids anything being truncated silently, so the flag reaches the manifest.
    a_run(evidence, "run-t", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-t", container_path=PAGE, text=BODY))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-t", version="1.0.0", location=location,
                   context_truncated=True)
    result = materialise(evidence, Item(key_for(location), TextSpan(16, 27)))
    assert result.context_truncated is True


def test_materialised_holds_no_path_and_no_file_id(evidence, one_excerpt):
    # §8.4 puts "Paths" in the always-local set. The type cannot carry one.
    names = {field.name for field in dataclasses.fields(Materialised)}
    assert names == {"observation_key", "span", "value", "zone", "context_before",
                     "context_after", "context_truncated", "unit_length"}
    assert not names & {"file_id", "path", "current_path", "filename", "content_hash"}


def test_unit_length_travels_so_the_whole_document_check_can_run(evidence, one_excerpt):
    # §8.4: "It should not send full documents where a short heading or OCR excerpt
    # is enough to resolve the question." Task 7's `check_item(item, *, unit_length)`
    # needs the stored length, and this is the only module that may ask P4 for it.
    key, _ = one_excerpt
    assert materialise(evidence, Item(key, TextSpan(16, 27))).unit_length == len(BODY)


def test_a_container_path_address_has_no_unit_length(evidence, one_cell):
    key, _ = one_cell
    assert materialise(evidence, Item(key, None)).unit_length is None


def test_materialised_is_frozen(evidence, one_excerpt):
    key, _ = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.value = "anything else"


# --- the current-row rule ------------------------------------------------------

@pytest.fixture()
def two_versions(evidence):
    """P4's guaranteed shape: two extractor versions, one key (MINOR 8)."""
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    a_run(evidence, "run-1", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    old = an_observation(evidence, run_id="run-1", version="1.0.0", location=location)
    a_run(evidence, "run-2", "2.0.0", LATER)
    record_text_unit(evidence, TextUnit(run_id="run-2", container_path=PAGE, text=BODY))
    new = an_observation(evidence, run_id="run-2", version="2.0.0", location=location,
                         observed_at=LATER)
    return key_for(location), old, new


def test_p4_really_does_return_two_rows_for_one_key(evidence, two_versions):
    # The premise. If P4 ever made the key unique this test goes red and the
    # current-row rule below becomes unnecessary rather than silently wrong.
    key, _, _ = two_versions
    assert len(observations_by_key(evidence, key)) == 2


def test_resolution_picks_the_current_row_and_not_the_first(evidence, two_versions):
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    resolved = current_observation(evidence, key)
    assert resolved.extractor_version == "2.0.0"
    assert resolved.run_id == "run-2"
    assert resolved == get_observation(evidence, new)


def test_two_unsuperseded_rows_raise_rather_than_picking_one(evidence, two_versions):
    # "an unresolvable ambiguity raises rather than picking the first." Releasing the
    # wrong one of two live rows is a silent release of retracted text.
    key, _, _ = two_versions
    with pytest.raises(AmbiguousObservationKey):
        current_observation(evidence, key)


def test_p1s_writer_refuses_to_build_a_headless_chain(evidence, two_versions):
    # Verified against the live substrate: `mark_superseded` rejects a cycle and
    # rejects re-superseding a superseded row, so a key with no live head cannot be
    # reached through P1's published writer at all. Asserted here so the next test's
    # raw UPDATE is legible as "around the writer" rather than as normal usage.
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    with pytest.raises(ValueError, match="cycle"):
        supersede_observation(evidence, old_observation_id=new,
                              new_observation_id=old,
                              reason="a cycle nobody meant to write")


def test_a_key_with_no_live_row_raises(evidence, two_versions):
    # Reachable only by writing around P1's writer -- which is what a hand-edited,
    # half-restored, or partially migrated database looks like. The gate answers it
    # with a refusal rather than with whichever row it happened to see last.
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    evidence.execute("UPDATE evidence SET superseded_by = ? WHERE observation_id = ?",
                     (old, new))
    with pytest.raises(AmbiguousObservationKey):
        current_observation(evidence, key)


def test_an_unknown_key_is_unresolvable(evidence):
    with pytest.raises(UnresolvableSpan):
        current_observation(evidence, "sha256:" + "f" * 64)


def test_an_observation_id_is_not_a_citation_handle(evidence, one_excerpt):
    # M14: "a per-row `observation_id` dies on extractor upgrade". A caller who
    # passes one gets a refusal here rather than a resolution that stops working
    # the next time an extractor ships.
    key, location = one_excerpt
    row = evidence.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?", (key,)
    ).fetchone()
    with pytest.raises(UnresolvableSpan):
        current_observation(evidence, row["observation_id"])


def test_p4_publishes_no_current_row_reader(evidence, one_excerpt):
    # The reported gap, asserted so it cannot be quietly forgotten: the published
    # reader returns records with no id and no supersession column, so P7 cannot
    # ask P4 which row is current. `store.current_observation_by_key` would close it.
    key, _ = one_excerpt
    (only,) = observations_by_key(evidence, key)
    names = {field.name for field in dataclasses.fields(only)}
    assert "observation_id" not in names
    assert "superseded_by" not in names


# --- the second resolver: a container-path address -----------------------------

@pytest.fixture()
def one_cell(evidence):
    a_run(evidence, "run-c", "1.0.0", FIXED_CLOCK)
    location = Location(zone="table", container_path=CELL)
    an_observation(evidence, run_id="run-c", version="1.0.0", location=location,
                   raw_value="4,200.00", extractor_name="xlsx_tables",
                   source_type="spreadsheet", context_before=None, context_after=None)
    return key_for(location, extractor_name="xlsx_tables", raw_value="4,200.00"), location


def test_a_container_path_address_materialises_the_raw_value(evidence, one_cell):
    key, location = one_cell
    result = materialise(evidence, Item(key, None))
    assert result.value == "4,200.00"
    assert result.span == "table:sheet=1/row=4/cell=3"
    assert result.zone == "table"


def test_a_container_path_address_has_no_text_unit_at_all(evidence, one_cell):
    # The reason it is a SECOND resolver and not a degenerate first: there is
    # nothing to take a substring of.
    key, _ = one_cell
    assert unit_for_observation(evidence, current_observation(evidence, key)) is None


def test_a_container_path_address_never_falls_back_to_a_unit(evidence, one_cell):
    # Even with a unit sitting at the same run, the cell address resolves to the
    # cell. "Send the cell" must not become "send the sheet".
    key, _ = one_cell
    record_text_unit(evidence, TextUnit(run_id="run-c", container_path=CELL,
                                        text="the whole sheet, flattened"))
    assert materialise(evidence, Item(key, None)).value == "4,200.00"


# --- refusals ------------------------------------------------------------------

def test_a_span_that_does_not_anchor_is_unresolvable(evidence):
    # P4 does NOT validate the anchor at write time -- verified against the live
    # store, a non-anchoring observation records cleanly -- so this check is the
    # only thing standing between a stale span and released text.
    a_run(evidence, "run-x", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-x", container_path=PAGE,
                                        text="X" * 40))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-x", version="1.0.0", location=location)
    with pytest.raises(UnresolvableSpan) as caught:
        materialise(evidence, Item(key_for(location), TextSpan(16, 27)))
    assert "RAW-1" in str(caught.value.__cause__)


def test_a_failed_anchor_returns_no_substring_at_all(evidence):
    # "P4's checker raises; never returns a repair, and a gate that repaired would
    # release text nobody addressed." The wrong substring is right there in the
    # unit; nothing hands it back.
    a_run(evidence, "run-y", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-y", container_path=PAGE,
                                        text="X" * 40))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-y", version="1.0.0", location=location)
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location), TextSpan(16, 27)))


def test_a_span_beyond_the_stored_unit_is_unresolvable(evidence):
    a_run(evidence, "run-z", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-z", container_path=PAGE,
                                        text="short", truncated=True))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(10, 20))
    an_observation(evidence, run_id="run-z", version="1.0.0", location=location,
                   raw_value="beyond")
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location, raw_value="beyond"),
                                   TextSpan(10, 20)))


def test_a_text_span_with_no_unit_is_unresolvable(evidence):
    a_run(evidence, "run-w", "1.0.0", FIXED_CLOCK)
    location = Location(zone="body", container_path=(Segment(kind="page", index=9),),
                        text_span=TextSpan(0, 6))
    an_observation(evidence, run_id="run-w", version="1.0.0", location=location,
                   raw_value="orphan")
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location, raw_value="orphan"),
                                   TextSpan(0, 6)))


def test_the_callers_span_must_match_the_one_the_key_carries(evidence, one_excerpt):
    # SPEC §4: an excerpt is "resolved by the gate from local storage". The caller's
    # coordinates are a claim, and a claim that disagrees with the record is refused
    # rather than honoured or silently replaced.
    key, _ = one_excerpt
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key, TextSpan(0, 39)))


def test_a_region_addressed_observation_is_refused(evidence):
    # NEEDS-JOSEPH C3, reached through Task 8's `span_address`.
    a_run(evidence, "run-r", "1.0.0", FIXED_CLOCK)
    location = Location(zone="ocr", container_path=PAGE,
                        region=Region(0.10, 0.22, 0.30, 0.04, "norm"))
    an_observation(evidence, run_id="run-r", version="1.0.0", location=location,
                   raw_value="992-33-1188", extractor_name="ocr_engine",
                   source_type="ocr")
    key = key_for(location, extractor_name="ocr_engine")
    with pytest.raises(RegionOriginUnspecified):
        materialise(evidence, Item(key, None))


def test_a_time_span_addressed_observation_is_refused(evidence):
    a_run(evidence, "run-a", "1.0.0", FIXED_CLOCK)
    location = Location(zone="transcript", container_path=(),
                        time_span=TimeSpan(1000, 2000))
    an_observation(evidence, run_id="run-a", version="1.0.0", location=location,
                   raw_value="spoken", extractor_name="whisper_local",
                   source_type="audio_video")
    key = key_for(location, extractor_name="whisper_local", raw_value="spoken")
    with pytest.raises(RegionOriginUnspecified):
        materialise(evidence, Item(key, None))


# --- the single-locus guard ----------------------------------------------------

def test_the_materialiser_list_names_p4s_functions_and_not_a_pattern():
    assert MATERIALISERS["evidence_shape.text_units"] == ("raw_value_at",)
    assert "unit_for_observation" in MATERIALISERS["evidence_shape.store"]
    assert "get_observation" in MATERIALISERS["evidence_shape.store"]


def test_resolve_is_the_only_module_under_src_privacy_that_binds_one():
    # Asserted by walking the AST, not by reading source text: a text scan matches
    # docstrings and comments, and this repository has recorded that false result
    # more than once. Task 21 runs the same walk over the finished package.
    package = pathlib.Path(privacy.__file__).parent
    offenders: dict[str, list[str]] = {}
    for path in sorted(package.glob("*.py")):
        if path.name == "resolve.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        bound: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                names = MATERIALISERS.get(node.module or "", ())
                bound |= {f"{node.module}.{a.name}" for a in node.names
                          if a.name in names}
            elif isinstance(node, ast.Import):
                bound |= {a.name for a in node.names if a.name in MATERIALISERS}
        if bound:
            offenders[path.name] = sorted(bound)
    assert offenders == {}, (
        f"{sorted(offenders)} bind a P4 materialiser; resolve.py is the only module "
        "under src/privacy/ that may, and release.py is the only one that may import "
        "resolve")
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_resolve.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.resolve'`. Collection fails on the
import line; no test runs.

- [ ] **Step 3: Write `src/privacy/resolve.py`**

```python
# src/privacy/resolve.py
"""(observation_key, span) -> text. The only module in the product that does this.

Everything about this module is narrow deliberately:

- **The handle is the key, never the id** (M14). SPEC *Correction learning*: "The key,
  not the id, is what makes that durable" -- a per-row `observation_id` dies when the
  extractor is upgraded, and a citation that stops resolving is a citation that stops
  being evidence.
- **The current row, not the first.** P4's reader is a LIST on purpose: "two extractor
  versions carry one key, which is what MINOR 8 arranged". Resolving to a superseded
  row would release text a later extractor already retracted.
- **Two resolvers and no third.** A `text_span` materialises through P4's
  `raw_value_at` behind P4's own `check_span_anchor`; a container-path-only address
  (§2.3's table/row/cell, §2.8's EXIF field) materialises `Observation.raw_value`,
  because `unit_for_observation` returns None for one and there is nothing to take a
  substring of. Anything else raises. A fallback to the whole unit is how "send the
  cell" becomes "send the sheet".
- **A failure is a refusal, never a repair.** P4's checker "raises; never returns a
  repair", and P4 does not validate the anchor at write time, so this is the only
  thing between a stale span and released text.

One thing here is not P4's, and it is reported rather than hidden: P4 publishes no
reader that returns the CURRENT row for a key. `observations_by_key` returns records
carrying neither `observation_id` nor `superseded_by`, and `supersede_chain` needs an
id those records do not have. `current_observation` therefore issues one read-only
SELECT for the live id and hands it straight back to P4's published `get_observation`.
The one-function fix belongs in P4 -- `store.current_observation_by_key(conn,
observation_key) -> Observation | None` -- and this module is the caller waiting for it.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.store import (
    get_observation, observations_by_key, unit_for_observation,
)
from evidence_shape.observation import Observation
from evidence_shape.text_units import SpanAnchorError, check_span_anchor, raw_value_at

from privacy.redaction import span_address

#: The P4 functions that turn a stored record into a string of document text, by
#: module. Published so Task 21's single-locus guard names them instead of matching
#: on the word "text" -- an AST walk needs a subject, and a guess is how a guard
#: passes vacuously.
MATERIALISERS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "evidence_shape.store": (
        "get_observation", "observation_row", "observations_by_key",
        "observations_for_file", "observations_for_run", "text_unit_at",
        "text_units_for_run", "unit_for_observation",
    ),
    "evidence_shape.text_units": ("raw_value_at",),
})


class UnresolvableSpan(Exception):
    """The address does not resolve, and the gate does not guess.

    Raised for an unknown key, an id passed where a key belongs, a span that does not
    anchor, a span with no unit, and a caller span that disagrees with the record.
    """


class AmbiguousObservationKey(Exception):
    """The key resolves to no live row, or to more than one.

    P4's reader is multi-valued on purpose; the supersession chain is what makes it
    single-valued again. When it does not, picking one would release the wrong text
    silently, so this raises instead.
    """


@dataclass(frozen=True, slots=True)
class Materialised:
    """One resolved item, with M5's three context fields still attached.

    No `file_id`, no path, no `content_hash`: §8.4 puts "Paths" and "file hashes" in
    the always-local set, and the type is where that is cheapest to enforce.

    `unit_length` is the STORED length of the text unit the span points into, or None
    for a container-path address that has no unit. Task 7's whole-document check --
    §8.4's "It should not send full documents where a short heading or OCR excerpt is
    enough to resolve the question" -- needs it, and this module is the only one that
    may ask P4 for it.
    """

    observation_key: str
    span: str
    value: str
    zone: str
    context_before: str | None
    context_after: str | None
    context_truncated: bool
    unit_length: int | None


def _live_observation_ids(conn: sqlite3.Connection,
                          observation_key: str) -> list[str]:
    """The rows for this key that nothing has superseded.

    The one read P4 does not publish. See the module docstring: `Observation` carries
    neither the id nor the supersession columns, so the current-row rule cannot be
    expressed with the published readers alone.
    """
    return [row["observation_id"] for row in conn.execute(
        "SELECT observation_id FROM evidence "
        "WHERE observation_key = ? AND superseded_by IS NULL ORDER BY rowid",
        (observation_key,))]


def current_observation(conn: sqlite3.Connection,
                        observation_key: str) -> Observation:
    """The one live row for a key, or a refusal."""
    candidates = observations_by_key(conn, observation_key)
    if not candidates:
        raise UnresolvableSpan(
            f"no observation carries key {observation_key!r}. P4's citation handle is "
            "the content-addressed `observation_key`, not the per-row "
            "`observation_id`, which dies on extractor upgrade (M14)")
    live = _live_observation_ids(conn, observation_key)
    if not live:
        raise AmbiguousObservationKey(
            f"key {observation_key!r} has {len(candidates)} rows and every one is "
            "superseded; the chain has no head, so there is no current text to release")
    if len(live) > 1:
        raise AmbiguousObservationKey(
            f"key {observation_key!r} has {len(live)} live rows. P4 returns a list "
            "because two extractor versions carry one key (MINOR 8); the supersession "
            "chain is what makes it single-valued, and picking one of two would "
            "release text an upgrade may already have retracted")
    return get_observation(conn, live[0])


def materialise(conn: sqlite3.Connection, item) -> Materialised:
    """Resolve one requested item against local storage.

    `item` is Task 7's `Excerpt` or `RedactedIdentifier`: it needs an
    `observation_key` and a `span` of `TextSpan | None`, and nothing else is read.
    """
    observation = current_observation(conn, item.observation_key)
    location = observation.location
    address = span_address(location)  # refuses a region (C3) and a time span
    text_span = location.text_span
    if item.span != text_span:
        raise UnresolvableSpan(
            f"the request addresses {item.span!r} and key "
            f"{item.observation_key!r} carries {text_span!r}. SPEC §4 has the gate "
            "resolve the excerpt from local storage, so a caller's coordinates are a "
            "claim; a claim that disagrees with the record is refused, not honoured "
            "and not silently replaced")
    if text_span is None:
        value, unit_length = observation.raw_value, None
    else:
        unit = unit_for_observation(conn, observation)
        if unit is None:
            raise UnresolvableSpan(
                f"{address} has a text span and no text unit at "
                f"{location.container_path!r} in run {observation.run_id!r}; there is "
                "nothing to take a substring of and the whole file is not a fallback")
        try:
            check_span_anchor(observation, unit)
        except SpanAnchorError as error:
            raise UnresolvableSpan(
                f"{address} does not anchor in run {observation.run_id!r}: {error}. "
                "P4's checker raises and never returns a repair, and a gate that "
                "repaired would release text nobody addressed"
            ) from error
        value, unit_length = raw_value_at(unit, text_span), unit.length
    return Materialised(
        observation_key=item.observation_key, span=address, value=value,
        zone=location.zone, context_before=observation.context_before,
        context_after=observation.context_after,
        context_truncated=observation.context_truncated, unit_length=unit_length)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_resolve.py -v`
Expected: PASS — 28 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–9 green, and P1–P5's 1292 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/resolve.py tests/p7/test_p7_resolve.py
git commit -m "feat(P7): the one materialisation locus - key to current row to text, two resolvers and no fallback"
```

---

### Task 10: The consent-aware audit record, and the ordering guarantee

**Files:**
- Create: `src/privacy/audit.py`
- Test: `tests/p7/test_p7_audit.py`

**Interfaces:**
- Consumes: `database_agent.events.append_event(conn, **fields) -> int`, `.EVENT_FIELDS`,
  `.CORRECTION_FIELDS`, `.MalformedEvent`, `evidence_shape.canonical.canonical_json(value) -> str`,
  `privacy.authorship.SUBSYSTEM`, `.MODEL_RELEASE`, `.MODEL_RELEASE_DENIED`, `.CONSENT_REQUESTED`,
  `.event_defaults(*, event_type, **fields) -> dict[str, object]`,
  `privacy.vocabulary.AUDIT_OUTCOMES`.
- Produces (`audit.py`):
  - `AUDIT_FIELDS: tuple[str, ...]` — SPEC §7's **nineteen**, in §7's order.
  - `CARRIED_FIELDS: tuple[str, str, str]` = `("user_id", "consent_request_id",
    "redaction_manifest")` — three names §7 does not list as fields, each with a reason.
  - `COLUMN_FIELDS: tuple[str, ...]` — the five with an `events` column.
  - `EXPLANATION_FIELDS: tuple[str, ...]` — the sixteen with none.
  - `OUTCOME_EVENT_TYPES: Mapping[str, str]` — outcome → P7 event name.
  - `AuditRecord` — frozen, twenty-two fields (`AUDIT_FIELDS + CARRIED_FIELDS`, the three carried
    defaulting to `None` / `()`).
  - `MalformedAudit`.
  - `append_audit(conn, record, *, author, component_version) -> int`.
  - `audit_record(conn, audit_id) -> AuditRecord`.
  - `audit_records_for(conn, *, file_id=None, release_id=None, consent_request_id=None)
    -> list[AuditRecord]`.

**Done-means:** 4, and the record half of 6, 7, 8.

**The nineteen, resolved name by name — this is the largest shape decision in the section.** SPEC §7
lists six required fields and a *"carried additionally"* block, and the skeleton fixes the total at
nineteen. Reading §7 literally gives sixteen, so three of §8.2's own event columns complete it, and
one §7 name is respelled. Both moves are recorded here rather than absorbed:

```text
§8.4's six          authorizing_policy · file_sensitivity · excerpts_included ·
                    redaction_applied · model · prompt_fingerprint
§7's carried        audit_id · release_id · observed_at · stage · file_ids · group_id ·
                    content_hashes · operation_mode · policy_version · plan_version · outcome
§8.2's per-file     file_id · content_hash
```

- **`appended_at` is spelled `observed_at`.** §7 annotates it *"§8.2 'time of observation'"*, and
  §8.2's time of observation is P1's `events.observed_at` column. A second name for one column is
  exactly the three-spellings defect this plan already records for `sensitivity`; there is one name
  and it is P1's.
- **`policy_version` is a field beside `authorizing_policy`.** §8.8 requires audit records to carry
  enough to *"reproduce the policy in force at each call"*, and `policy_version` is Task 12's third
  binding term. The sibling section reads it off the record by that name.
- **`file_ids` / `group_id` stay two fields, not one `target`.** §7 writes them on one line; the
  sibling section's fixtures already name them separately, and one composite field would break a
  written neighbour to gain nothing.
- **`file_id` and `content_hash` are the singular §8.2 columns and are not duplicates of the
  plurals.** §8.2's event record is per file — *"the event type, file ID, content hash"* — so a
  single-file request fills both, and a group request fills the plurals and leaves the singulars
  `NULL`. Without them `audit_records_for(file_id=...)` would have to search a JSON array, and §8.2's
  own log would not be per-file.

**Three carried fields, and why each is outside the nineteen.** `CARRIED_FIELDS` exists so that
`AUDIT_FIELDS == §7` stays a testable identity while the record still holds what neighbouring tasks
need. `user_id` is §8.2's *"user identity when there is an explicit user action"* and has an `events`
column; a model release has no live user, so it is normally `None` and is filled on a
`consent_requested` a person triggered. `consent_request_id` is **added by Task 14** — P13's
`subject_ref` is one and `NeedsConsent` as published carries no id — and Done-means 7's *"a
`consent_requested` event and no `model_release` for that request"* has no join key without it.
`redaction_manifest` is §7's *"plus the `redaction_manifest`"* clause: §7 folds it into
`excerpts_included`, but `excerpts_included` is read elsewhere as pairs, so the manifest travels
beside them as its mapping form. All three are reported.

**One events row, and canonical JSON in `explanation`.** P1's `append_event` accepts seventeen named
columns and `MalformedEvent`s an eighteenth; MINOR 1 fixes §8.2's list at eleven forever; B5 settles
that there is **one log**. The only shape that satisfies all three: five fields land in their
columns, the other sixteen land in `explanation` as canonical JSON — §8.2's own *"structured
explanation or evidence reference"* slot, the same device P5's Task 16 used, and queryable through
`json_extract`. **P7 adds no column to `events` and does not ask P1 to.**

**The ordering guarantee is structural, not a discipline.** `append_event` returns
`cursor.lastrowid` and the row exists at that moment, so `audit_id` **cannot be produced before the
record exists**. SPEC §6: *"the audit record is appended … before `Released` is returned"*; there is
no interval in which content is releasable and unaudited, because the only source of an `audit_id`
is a completed append. The test asserts it from both sides: the returned id is immediately
`SELECT`-able, and it equals the `event_id` of the row.

**`excerpts_included` is what left the device, and it is not a copy of it.** SPEC §7: *"a record
that cannot reconstruct the released payload from local storage fails §8.4's stated purpose."* The
field holds `(observation_key, span)` pairs where `span` is P4's canonical locator, and the test
proves the reconstruction by **re-running `resolve.materialise` from the stored pairs** and comparing
against what was released. That is why Task 9's `span` is a locator and not an opaque offset.

**Every model call, including local ones.** §8.4 says *"Every model call should be recorded in a
consent-aware audit record"* and names no exemption; Open question 6 asks whether a local call is
also a *consent* event, and that stays open. Denials and consent requests are appended too, on §8.2's
*"Every significant event affecting a file"* and §8.6's requirement that the UI show *"what has been
deferred, and why"*.

**`author` is checked, not trusted.** M8 gives authorship to the acting part, and Task 1's
`event_defaults` refuses a caller-supplied `subsystem`. `append_audit` keeps the published `author`
keyword and rejects anything but `SUBSYSTEM`, so `privacy` still writes `"P7"` in exactly one place.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_audit.py
"""§8.4's consent-aware audit record, as one events row plus canonical JSON.

The two properties that matter: the field list IS SPEC §7's, name for name, so a
dropped field is a red test rather than a quiet omission; and the record can
reconstruct what left the device, proved by re-running the resolver over the stored
pairs rather than by asserting that a string was kept.
"""
import dataclasses
import json

import pytest

from database_agent.events import EVENT_FIELDS, MalformedEvent, append_event
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import parse_locator, serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit

from privacy.audit import (
    AUDIT_FIELDS, CARRIED_FIELDS, COLUMN_FIELDS, EXPLANATION_FIELDS,
    OUTCOME_EVENT_TYPES, AuditRecord, MalformedAudit, append_audit, audit_record,
    audit_records_for,
)
from privacy.authorship import (
    CONSENT_REQUESTED, MODEL_RELEASE, MODEL_RELEASE_DENIED, SUBSYSTEM,
)
from privacy.resolve import materialise
from privacy.vocabulary import AUDIT_OUTCOMES

COMPONENT = "0.1.0"
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
CONTENT_HASH = "a" * 64
PAGE = (Segment(kind="page", index=2),)
BODY = "Passport number 992-33-1188 issued 2019."
LOCATION = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
SPAN = serialize_locator(LOCATION)
KEY = observation_key(content_hash=CONTENT_HASH, extractor_name="pdf_text",
                      locator=SPAN, raw_value="992-33-1188")
CLOUD = {"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}
LOCAL = {"locality": "local", "model_id": "llama-local", "provider": "self-hosted"}


def a_record(**over) -> AuditRecord:
    base = dict(
        authorizing_policy="policy-1", file_sensitivity="sensitive_personal",
        excerpts_included=((KEY, SPAN),), redaction_applied=True, model=CLOUD,
        prompt_fingerprint="fp-1", audit_id=None, release_id="release-1",
        observed_at=FIXED_CLOCK, stage="grouping", file_ids=("file-1",),
        group_id=None, content_hashes=(CONTENT_HASH,), operation_mode="cloud_assisted",
        policy_version="policy-1", plan_version="plan-1", outcome="released",
        file_id="file-1", content_hash=CONTENT_HASH)
    base.update(over)
    return AuditRecord(**base)


def go(conn, **over) -> int:
    return append_audit(conn, a_record(**over), author=SUBSYSTEM,
                        component_version=COMPONENT)


class Item:
    """Task 7's item shape, as Task 9 reads it."""

    def __init__(self, observation_key, span):
        self.observation_key = observation_key
        self.span = span


@pytest.fixture()
def excerpt(p7_conn):
    """A real observation, so the reconstruction test resolves against real storage."""
    create_evidence_schema(p7_conn)
    record_run(p7_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="pdf_text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=1))
    record_text_unit(p7_conn, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    record_observation(p7_conn, Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name="pdf_text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="992-33-1188", location=LOCATION, occurrence_count=1,
        observed_at=FIXED_CLOCK, reliability="direct", run_id="run-1",
        context_before="Passport number ", context_after=" issued 2019.",
        context_truncated=False))
    return p7_conn


# --- SPEC §7's field list ------------------------------------------------------

def test_audit_fields_are_spec_7s_nineteen_name_for_name():
    # §8.4's six required, then §7's carried block, then §8.2's two per-file columns.
    assert AUDIT_FIELDS == (
        "authorizing_policy", "file_sensitivity", "excerpts_included",
        "redaction_applied", "model", "prompt_fingerprint",
        "audit_id", "release_id", "observed_at", "stage", "file_ids", "group_id",
        "content_hashes", "operation_mode", "policy_version", "plan_version",
        "outcome", "file_id", "content_hash")
    assert len(AUDIT_FIELDS) == 19


def test_the_six_84_requires_are_all_present():
    # "what policy authorized the call, whether the file was sensitive, which
    # excerpts were included, whether values were redacted, which model received the
    # data, and the prompt fingerprint."
    assert set(AUDIT_FIELDS[:6]) == {
        "authorizing_policy", "file_sensitivity", "excerpts_included",
        "redaction_applied", "model", "prompt_fingerprint"}


def test_the_three_carried_fields_are_outside_the_nineteen():
    assert CARRIED_FIELDS == ("user_id", "consent_request_id", "redaction_manifest")
    assert not set(CARRIED_FIELDS) & set(AUDIT_FIELDS)


def test_the_record_is_exactly_the_nineteen_plus_the_three():
    names = tuple(field.name for field in dataclasses.fields(AuditRecord))
    assert names == AUDIT_FIELDS + CARRIED_FIELDS


def test_the_split_between_column_and_explanation_is_total_and_disjoint():
    assert COLUMN_FIELDS == ("file_id", "content_hash", "prompt_fingerprint",
                             "observed_at", "user_id")
    assert set(COLUMN_FIELDS) <= set(EVENT_FIELDS), (
        "P7 adds no column to `events` and does not ask P1 to")
    assert not set(COLUMN_FIELDS) & set(EXPLANATION_FIELDS)
    assert set(COLUMN_FIELDS) | set(EXPLANATION_FIELDS) | {"audit_id"} == set(
        AUDIT_FIELDS + CARRIED_FIELDS)
    assert len(EXPLANATION_FIELDS) == 16


def test_the_record_is_frozen(p7_conn):
    with pytest.raises(dataclasses.FrozenInstanceError):
        a_record().outcome = "denied"


# --- one events row, and the JSON explanation ----------------------------------

def test_the_five_column_fields_land_in_their_columns(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["file_id"] == "file-1"
    assert row["content_hash"] == CONTENT_HASH
    assert row["prompt_fingerprint"] == "fp-1"
    assert row["observed_at"] == FIXED_CLOCK
    assert row["user_id"] is None


def test_the_rest_land_in_explanation_as_canonical_json(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT explanation FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    payload = json.loads(row["explanation"])
    assert set(payload) == set(EXPLANATION_FIELDS)
    assert payload["authorizing_policy"] == "policy-1"
    assert payload["model"] == CLOUD
    # canonical: sorted keys, so two identical records serialise identically.
    assert row["explanation"] == json.dumps(payload, sort_keys=True,
                                            separators=(",", ":"), ensure_ascii=False)


def test_p7_authors_and_p1_writes(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["component_version"] == COMPONENT


def test_a_foreign_author_is_refused(p7_conn):
    # M8: the acting part authors. `privacy` writes "P7" in exactly one place and
    # this entry point is not a second one.
    with pytest.raises(MalformedAudit):
        append_audit(p7_conn, a_record(), author="P8", component_version=COMPONENT)


def test_p1_would_reject_an_eighteenth_column(p7_conn):
    # The constraint the JSON shape exists to satisfy, asserted against P1 rather
    # than quoted: none of §7's own field names is a column.
    with pytest.raises(MalformedEvent):
        append_event(p7_conn, event_type=MODEL_RELEASE, subsystem="P7",
                     component_version=COMPONENT, observed_at=FIXED_CLOCK,
                     explanation="{}", release_id="release-1")


# --- the round trip ------------------------------------------------------------

def test_the_record_round_trips(p7_conn):
    audit_id = go(p7_conn)
    assert audit_record(p7_conn, audit_id) == a_record(audit_id=audit_id)


def test_tuples_come_back_as_tuples(p7_conn):
    # JSON has one sequence type; the record has frozen fields that get compared.
    recovered = audit_record(p7_conn, go(p7_conn))
    assert recovered.excerpts_included == ((KEY, SPAN),)
    assert recovered.content_hashes == (CONTENT_HASH,)
    assert recovered.file_ids == ("file-1",)


def test_an_unknown_audit_id_raises(p7_conn):
    with pytest.raises(KeyError):
        audit_record(p7_conn, 999999)


# --- the ordering guarantee ----------------------------------------------------

def test_the_returned_id_is_already_selectable(p7_conn):
    # SPEC §6: "the audit record is appended ... BEFORE `Released` is returned."
    # `append_event` returns `cursor.lastrowid`, so an `audit_id` cannot exist
    # before its row does. There is no interval in which content is releasable and
    # unaudited, and the property is structural rather than a discipline.
    audit_id = go(p7_conn)
    (count,) = p7_conn.execute("SELECT count(*) FROM events WHERE event_id = ?",
                               (audit_id,)).fetchone()
    assert count == 1


def test_the_returned_id_is_the_rows_event_id(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT event_id FROM events ORDER BY event_id DESC "
                          "LIMIT 1").fetchone()
    assert row["event_id"] == audit_id


def test_audit_ids_are_monotonic(p7_conn):
    first, second = go(p7_conn), go(p7_conn, release_id="release-2")
    assert second > first


# --- outcomes, and what each one appends ---------------------------------------

def test_each_outcome_maps_to_its_own_p7_event_type(p7_conn):
    assert OUTCOME_EVENT_TYPES == {
        "released": MODEL_RELEASE,
        "denied": MODEL_RELEASE_DENIED,
        "consent_requested": CONSENT_REQUESTED}
    assert tuple(OUTCOME_EVENT_TYPES) == AUDIT_OUTCOMES


def test_a_denial_is_recorded_too(p7_conn):
    # §8.2: "Every significant event affecting a file"; §8.6: the UI must show "what
    # has been deferred, and why".
    audit_id = go(p7_conn, outcome="denied", release_id=None)
    row = p7_conn.execute("SELECT event_type FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["event_type"] == MODEL_RELEASE_DENIED


def test_a_consent_request_is_recorded_with_its_id(p7_conn):
    # Done-means 7's join key. Task 14 adds the field; the record carries it.
    audit_id = go(p7_conn, outcome="consent_requested", release_id=None,
                  consent_request_id="consent-1", user_id="joseph")
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["event_type"] == CONSENT_REQUESTED
    assert row["user_id"] == "joseph"
    assert json.loads(row["explanation"])["consent_request_id"] == "consent-1"


def test_a_local_model_call_is_audited(p7_conn):
    # §8.4: "Every model call should be recorded" -- no exemption is named, and
    # Open question 6 (is a local call also a CONSENT event?) stays open.
    audit_id = go(p7_conn, model=LOCAL, operation_mode="local_model")
    assert audit_record(p7_conn, audit_id).model == LOCAL


def test_an_outcome_outside_the_vocabulary_is_refused(p7_conn):
    with pytest.raises(MalformedAudit):
        go(p7_conn, outcome="probably_fine")


def test_an_empty_stage_is_refused(p7_conn):
    # §8.5 requires per-stage decomposition; an unattributed call cannot be
    # decomposed later.
    with pytest.raises(MalformedAudit):
        go(p7_conn, stage="")


# --- the readers ---------------------------------------------------------------

def test_records_are_found_by_file_by_release_and_by_consent_request(p7_conn):
    first = go(p7_conn)
    second = go(p7_conn, release_id="release-2", file_id="file-2",
                file_ids=("file-2",))
    third = go(p7_conn, outcome="consent_requested", release_id=None,
               consent_request_id="consent-1")
    assert [r.audit_id for r in audit_records_for(p7_conn, file_id="file-1")] == [
        first, third]
    assert [r.audit_id for r in audit_records_for(p7_conn, release_id="release-2")] == [
        second]
    assert [r.audit_id for r in
            audit_records_for(p7_conn, consent_request_id="consent-1")] == [third]


def test_the_readers_return_records_in_append_order(p7_conn):
    ids = [go(p7_conn), go(p7_conn, release_id="release-2"),
           go(p7_conn, release_id="release-3")]
    assert [r.audit_id for r in audit_records_for(p7_conn, file_id="file-1")] == ids


def test_the_readers_see_only_p7s_three_event_types(p7_conn):
    # The log is shared (B5). A `discovery` event on the same file is not an audit
    # record and must not appear in one.
    go(p7_conn)
    append_event(p7_conn, event_type="discovery", subsystem="P3",
                 component_version="0.1.0", observed_at=FIXED_CLOCK,
                 explanation="a scan saw it", file_id="file-1")
    assert len(audit_records_for(p7_conn, file_id="file-1")) == 1


def test_no_filter_at_all_is_refused(p7_conn):
    # Returning the whole log for a call that named nothing is how a "show me the
    # releases for this file" screen quietly becomes "show me every release".
    go(p7_conn)
    with pytest.raises(MalformedAudit):
        audit_records_for(p7_conn)


# --- what left the device ------------------------------------------------------

def test_excerpts_included_holds_pairs_and_not_a_second_copy_of_the_text(excerpt):
    audit_id = go(excerpt)
    payload = json.loads(excerpt.execute(
        "SELECT explanation FROM events WHERE event_id = ?",
        (audit_id,)).fetchone()["explanation"])
    assert payload["excerpts_included"] == [[KEY, SPAN]]
    assert "992-33-1188" not in json.dumps(payload)
    assert BODY not in json.dumps(payload)


def test_the_stored_pairs_reconstruct_what_left_the_device(excerpt):
    # SPEC §7: "a record that cannot reconstruct the released payload from local
    # storage fails §8.4's stated purpose." Proved by re-running the resolver over
    # the stored pairs, which is why Task 9's `span` is P4's canonical locator and
    # not an opaque offset.
    recovered = audit_record(excerpt, go(excerpt))
    for key, span in recovered.excerpts_included:
        again = materialise(excerpt, Item(key, parse_locator(span).text_span))
        assert again.value == "992-33-1188"
        assert again.span == span
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_audit.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.audit'`. Collection fails on the
import line; no test runs.

- [ ] **Step 3: Write `src/privacy/audit.py`**

```python
# src/privacy/audit.py
"""§8.4's consent-aware audit record, as ONE `events` row plus canonical JSON.

§8.4: "Every model call should be recorded in a consent-aware audit record. The record
should show what policy authorized the call, whether the file was sensitive, which
excerpts were included, whether values were redacted, which model received the data,
and the prompt fingerprint."

Three constraints meet here and are jointly satisfiable exactly one way. P1's
`append_event` accepts seventeen named columns and rejects an eighteenth; MINOR 1 fixes
§8.2's list at eleven forever; B5 settles that there is ONE log -- "§8.4's consent-aware
record is that log with the consent fields". So five fields land in their columns and
the other sixteen land in `explanation`, which is §8.2's own "structured explanation or
evidence reference" slot. P7 adds no column to `events` and does not ask P1 to.

Two properties this module exists to make structural rather than procedural:

- **`audit_id` cannot exist before the record does.** It IS the `event_id` P1 returns
  from a completed insert, so SPEC §6's "the audit record is appended ... before
  `Released` is returned" is not a discipline anyone can forget.
- **The record says what left the device without holding a copy of it.**
  `excerpts_included` is `(observation_key, span)` pairs, where `span` is P4's canonical
  locator; re-running `resolve.materialise` over them reproduces the payload exactly.
  §8.4 puts "raw sensitive values" in the always-local set, and the text already exists
  once.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from types import MappingProxyType

from database_agent.events import EVENT_FIELDS, append_event
from evidence_shape.canonical import canonical_json

from privacy.authorship import (
    CONSENT_REQUESTED, MODEL_RELEASE, MODEL_RELEASE_DENIED, SUBSYSTEM, event_defaults,
)
from privacy.vocabulary import AUDIT_OUTCOMES

#: SPEC §7's nineteen, in §7's order: §8.4's six required, §7's carried block, then
#: §8.2's two per-file columns. `appended_at` is spelled `observed_at` because §7
#: annotates it '§8.2 "time of observation"' and that is P1's column; one thing has
#: one name.
AUDIT_FIELDS: tuple[str, ...] = (
    "authorizing_policy", "file_sensitivity", "excerpts_included",
    "redaction_applied", "model", "prompt_fingerprint",
    "audit_id", "release_id", "observed_at", "stage", "file_ids", "group_id",
    "content_hashes", "operation_mode", "policy_version", "plan_version", "outcome",
    "file_id", "content_hash",
)

#: Three names SPEC §7 does not list as fields, kept outside the nineteen so
#: `AUDIT_FIELDS == §7` stays a testable identity. Each is reported in the plan.
CARRIED_FIELDS: tuple[str, str, str] = (
    "user_id", "consent_request_id", "redaction_manifest",
)

#: The five with an `events` column. Everything else has none.
COLUMN_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "prompt_fingerprint", "observed_at", "user_id",
)

#: The sixteen that travel as canonical JSON. `audit_id` is in neither list: it is the
#: row's identity, assigned by the insert and read back off `event_id`.
EXPLANATION_FIELDS: tuple[str, ...] = tuple(
    name for name in AUDIT_FIELDS + CARRIED_FIELDS
    if name not in COLUMN_FIELDS and name != "audit_id"
)

#: outcome -> the P7 event type that records it. `model_release` and its consent-aware
#: record are the same event (B5).
OUTCOME_EVENT_TYPES: Mapping[str, str] = MappingProxyType({
    "released": MODEL_RELEASE,
    "denied": MODEL_RELEASE_DENIED,
    "consent_requested": CONSENT_REQUESTED,
})

_TUPLE_FIELDS = ("excerpts_included", "file_ids", "content_hashes",
                 "redaction_manifest")
_PAIR_FIELDS = ("excerpts_included",)


class MalformedAudit(Exception):
    """Shape check at the writer. An append-only row cannot be repaired later."""


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """SPEC §7's nineteen, plus three carried names §7 does not list as fields."""

    authorizing_policy: str
    file_sensitivity: str
    excerpts_included: tuple[tuple[str, str], ...]
    redaction_applied: bool
    model: Mapping[str, str]
    prompt_fingerprint: str
    audit_id: int | None
    release_id: str | None
    observed_at: str
    stage: str
    file_ids: tuple[str, ...]
    group_id: str | None
    content_hashes: tuple[str, ...]
    operation_mode: str
    policy_version: str
    plan_version: str
    outcome: str
    file_id: str | None
    content_hash: str | None
    user_id: str | None = None
    consent_request_id: str | None = None
    redaction_manifest: tuple[Mapping[str, object], ...] = ()


def _check(record: AuditRecord, author: str) -> None:
    if author != SUBSYSTEM:
        raise MalformedAudit(
            f"author {author!r} is not {SUBSYSTEM!r}. M8 gives authorship to the "
            "acting part, and `privacy` writes its subsystem name in one place")
    if record.outcome not in AUDIT_OUTCOMES:
        raise MalformedAudit(
            f"outcome {record.outcome!r} is not one of {AUDIT_OUTCOMES}; a value "
            "outside a closed vocabulary is a load error, not a fallback")
    for name in ("stage", "authorizing_policy", "operation_mode", "policy_version",
                 "plan_version", "file_sensitivity", "prompt_fingerprint",
                 "observed_at"):
        if not getattr(record, name):
            raise MalformedAudit(
                f"{name} is required on every audit record; §8.5 decomposes replay "
                "by stage and §8.8 reproduces the policy in force at each call, and "
                "neither is possible from a record that omitted one")
    if not record.model:
        raise MalformedAudit(
            "§8.4 requires the record show which model received the data")


def append_audit(conn: sqlite3.Connection, record: AuditRecord, *, author: str,
                 component_version: str) -> int:
    """Append one audit record and return its `audit_id`.

    The id is P1's `event_id`, produced by the insert, so it cannot be handed to a
    caller before the row exists. That is SPEC §6's ordering guarantee, structurally.
    """
    _check(record, author)
    explanation = canonical_json(
        {name: _jsonable(getattr(record, name)) for name in EXPLANATION_FIELDS})
    columns = {name: getattr(record, name) for name in COLUMN_FIELDS}
    return append_event(conn, **event_defaults(
        event_type=OUTCOME_EVENT_TYPES[record.outcome],
        component_version=component_version, explanation=explanation, **columns))


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, Mapping):
        return dict(value)
    return value


def _record_from_row(row: sqlite3.Row) -> AuditRecord:
    import json

    payload = json.loads(row["explanation"])
    values: dict[str, object] = {name: payload[name] for name in EXPLANATION_FIELDS}
    values.update({name: row[name] for name in COLUMN_FIELDS})
    values["audit_id"] = row["event_id"]
    values["redaction_applied"] = bool(values["redaction_applied"])
    for name in _TUPLE_FIELDS:
        values[name] = tuple(
            tuple(item) if name in _PAIR_FIELDS else item
            for item in values[name])
    return AuditRecord(**values)


def audit_record(conn: sqlite3.Connection, audit_id: int) -> AuditRecord:
    """One record, by the id `append_audit` returned."""
    row = conn.execute("SELECT * FROM events WHERE event_id = ? AND event_type IN "
                       "(?, ?, ?)",
                       (audit_id, MODEL_RELEASE, MODEL_RELEASE_DENIED,
                        CONSENT_REQUESTED)).fetchone()
    if row is None:
        raise KeyError(f"no audit record {audit_id!r}")
    return _record_from_row(row)


def audit_records_for(conn: sqlite3.Connection, *, file_id: str | None = None,
                      release_id: str | None = None,
                      consent_request_id: str | None = None) -> list[AuditRecord]:
    """Audit records matching every filter given, in append order.

    At least one filter is required. A reader that returned the whole log for a call
    that named nothing is how "the releases for this file" becomes "every release".
    """
    clauses = ["event_type IN (?, ?, ?)"]
    parameters: list[object] = [MODEL_RELEASE, MODEL_RELEASE_DENIED, CONSENT_REQUESTED]
    if file_id is not None:
        clauses.append("file_id = ?")
        parameters.append(file_id)
    for name, value in (("release_id", release_id),
                        ("consent_request_id", consent_request_id)):
        if value is not None:
            clauses.append(f"json_extract(explanation, '$.{name}') = ?")
            parameters.append(value)
    if len(clauses) == 1:
        raise MalformedAudit(
            "audit_records_for needs at least one of file_id, release_id or "
            "consent_request_id")
    rows = conn.execute(
        f"SELECT * FROM events WHERE {' AND '.join(clauses)} ORDER BY event_id",
        parameters)
    return [_record_from_row(row) for row in rows]
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_audit.py -v`
Expected: PASS — 29 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–10 green, and P1–P5's 1292 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/audit.py tests/p7/test_p7_audit.py
git commit -m "feat(P7): the consent-aware audit record as one events row, and the ordering guarantee"
```

---

### Task 11: `Gate.release` — the request, the three-branch union, and no override parameter

**Files:**
- Create: `src/privacy/release.py`, `src/privacy/gate.py`
- Test: `tests/p7/test_p7_release.py`

**Interfaces:**
- Consumes: everything from Tasks 2–10 — `vocabulary.HANDLING_CLASSES`, `.DENIAL_REASONS`,
  `.CONSENT_OPTIONS`, `.check_handling_class`, `.check_denial_reason`,
  `classification.resolve_class(record) -> str`, `classification_store.ClassificationStore`,
  `policy.Policy`, `.current_policy(conn, *, plan_version) -> Policy`,
  `defaults.LOCAL_FIRST_MODES`, `items.Excerpt`, `.RedactedIdentifier`, `.check_item(item, *,
  unit_length) -> None`, `.WholeDocumentRequested`, `redaction.apply_redaction`,
  `.RedactionManifest`, `resolve.materialise(conn, item) -> Materialised`,
  `audit.AuditRecord`, `.append_audit`, `authorship.SUBSYSTEM`;
  `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row`,
  `database_agent.budget.get_ceiling(conn, key) -> int | None`.
- Produces (`release.py`):
  - `ModelTarget` — frozen: `locality: str`, `model_id: str`, `provider: str`; `LOCALITIES`.
  - `Target` — frozen: `file_ids: tuple[str, ...]`, `group_id: str | None = None`.
  - `ModelCallRequest` — frozen; SPEC §6's **seven** exactly: `stage`, `target`, `model_target`,
    `requested_items`, `prompt_template_id`, `prompt_fingerprint`, `max_dossier_tokens`.
  - `Released` — frozen; SPEC §6's **six**: `release_id`, `audit_id`, `policy_version`,
    `materialised_items`, `redaction_manifest`, `model_target`.
  - `Denied` — frozen: `reason`, `explanation`, `remedy_options`.
  - `NeedsConsent` — frozen: `requirement`, `options`.
  - `ReleaseDecision` — the union alias.
  - `REQUEST_FIELDS`, `RELEASED_FIELDS`, `FORBIDDEN_PARAMETER_NAMES: frozenset[str]`,
    `UNCLASSIFIED: str`, `SENSITIVE_CLASSES: tuple[str, str]`, `TEXT_BEARING: tuple[type, ...]`,
    `DECISION_ORDER: tuple[str, ...]`.
  - `MalformedRequest`, `MalformedDecision`.
- Produces (`gate.py`):
  - `Gate(conn, *, plan_version, component_version, classifier, transform, consent_scope_for,
    unclassified_permits_local, clock)`.
  - `Gate.release(request) -> ReleaseDecision`.

**Done-means:** 3 (the gate half), and the entry point for 5, 6, 7.

**The signature is adopted verbatim on both sides (B2), so everything else is constructor state.**
SPEC §6 publishes `Gate.release(ModelCallRequest) -> ReleaseDecision` and P8 calls it under exactly
that signature. `Gate.release` therefore has **two** parameters, `self` and `request`, and the
connection, the policy scope, the two injected redaction protocols, the clock and the two open
questions that need a parameter all live on `Gate.__init__`. That is not a workaround; it is what
"one door, named once" costs, and it is why the whitelist test can be an equality rather than a
subset.

**There is no override parameter, and the test proves it two ways.** The whitelist —
`set(inspect.signature(Gate.release).parameters) == {"self", "request"}` — proves no unpublished
parameter exists **at all**, which is the stronger half. The blacklist,
`FORBIDDEN_PARAMETER_NAMES`, names the specific words a future convenience would use and asserts
they appear in neither the signature nor any field of the request or of the three branch types.
**Both are parsed from the signature and from `dataclasses.fields`, never from source text** — a
source scan matches comments and docstrings, and that technique has produced a false result eight
times on this project. This is P5's `SafetyPolicy` discipline applied to the gate: *"Two fields, and
deliberately no third."*

**Three parameters on `Gate.__init__` have no default, and each one is an open question refusing to
be guessed.** `classifier` and `transform` are the SPEC's *Deferred* row for identifier classes
(Task 8). `consent_scope_for` is Open question 3 — *"What is a 'corpus area'? … Consent grants
cannot be scoped until this is named"* — so the caller maps a `file_id` to a scope name and P7
defines no area, the same posture the sibling section's `revoke` takes with `files_in_scope`.
`unclassified_permits_local` is Open question 5 — *"Does `unreadable_unclassified` permit a local
model call?"* — and the skeleton requires the parameter carry **no default** until it is answered.

**What Tasks 12–14 change, stated here so they do not each invent it.** `release.py` mints its
`release_id` with `secrets.token_hex(16)` and records no ledger; **Task 12 modifies `release.py` to
call `binding.mint_release` and adds the ledger.** `Denied` is constructed inline here with an
explanation and remedy options; **Task 13 modifies `release.py` to route all eight reasons through
`denial.deny` and adds `RemedyOption`**, so `Denied.remedy_options` may become
`tuple[RemedyOption, ...]` — the field **name** is fixed here and the element type is Task 13's.
`NeedsConsent` carries `requirement` and `options` here; **Task 14 modifies `release.py` to add
`consent_request_id`**, which P13's `subject_ref` needs and SPEC §6 omits. Each is a `Modify:` line
in that task, the pattern P5's Task 10 already used for `schema.py`. Nothing else in `release.py`
moves.

**`DECISION_ORDER` is published because the order is the contract.** Five denials, then consent,
then the budget backstop, then the audit, then the token. It is published as a tuple so a reviewer
can read the order without reading the function, and so a reordering is a diff on a constant rather
than an invisible behaviour change. The order is forced, not chosen: the mode/target check needs no
classification, the classification checks need no content, and **nothing materialises until every
check that could deny has run** — a gate that resolved first would have the text in memory before it
decided whether it was allowed to.

**The gate raises nothing of its own, and the two exceptions that do escape are about the CALL.**
`resolve.UnresolvableSpan` and `resolve.AmbiguousObservationKey` propagate: a request that addresses
a span the evidence does not carry is a contract violation by the caller, the fourth kind of
refusal, and it always propagates. `Denied` and `NeedsConsent` are values. The catcher is the
caller's: `Denied` → P8 writes its `Refusal` with `PRIVACY_GATE_REFUSED`; `NeedsConsent` → the
calling part routes to P13 and **never absorbs it** (B2).

**`Denied(unclassified)` is the ordinary path, and this task is built for that.** The detector is
unwritten (D2), so against a real corpus `ClassificationStore.current` returns `None` for every file
and `resolve_class(None)` returns `unreadable_unclassified`. The denial fixture needs no setup; the
`Released` fixture is the one that has to write a classification by hand, and its test says so.

**`materialised_items` holds only what had a value to resolve.** SPEC §6: *"materialised_items[]
post-redaction values only."* `excerpt` and `redacted_identifier` carry `(observation_key, span)` and
resolve to text; `candidate_label`, `metadata_field`, `evidence_reference` and `filename` carry no
local content — §4 says an evidence reference is *"an id only — no content"* — so they were never
materialised and the caller still holds them on the request it sent. The gate does not echo back
what it did not touch.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_release.py
"""§8.4's one door: the request, the three branches, and no way around it.

The shape tests are the point. A gate whose decision logic is right and whose
signature has an `override=` keyword is not a gate, and the second failure is the one
review does not catch.
"""
import dataclasses
import inspect

import pytest

from database_agent.budget import set_ceiling
from database_agent.files_table import record_file
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit

from privacy.audit import audit_record, audit_records_for
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.gate import Gate
from privacy.items import Excerpt
from privacy.policy import Policy, create_privacy_schema, set_policy
from privacy.release import (
    DECISION_ORDER, FORBIDDEN_PARAMETER_NAMES, RELEASED_FIELDS, REQUEST_FIELDS,
    SENSITIVE_CLASSES, UNCLASSIFIED, Denied, ModelCallRequest, ModelTarget,
    NeedsConsent, Released, Target,
)
from privacy.resolve import Materialised

COMPONENT = "0.1.0"
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
CONTENT_HASH = "a" * 64
PAGE = (Segment(kind="page", index=2),)
BODY = "Passport number 992-33-1188 issued 2019."
LOCATION = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
SPAN = serialize_locator(LOCATION)
KEY = observation_key(content_hash=CONTENT_HASH, extractor_name="pdf_text",
                      locator=SPAN, raw_value="992-33-1188")
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
LOCAL = ModelTarget(locality="local", model_id="llama-local", provider="self-hosted")


def classifier(value, *, context_before, context_after):
    return "passport_number"


def transform(value, *, identifier_class):
    return f"[{identifier_class}]"


def a_request(**over) -> ModelCallRequest:
    base = dict(stage="grouping", target=Target(file_ids=("file-1",)),
                model_target=CLOUD,
                requested_items=(Excerpt(observation_key=KEY, span=TextSpan(16, 27),
                                         reason="the group's subject"),),
                prompt_template_id="group-coherence-v1", prompt_fingerprint="fp-1",
                max_dossier_tokens=800)
    base.update(over)
    return ModelCallRequest(**base)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(), redaction_settings={
                    facet: "redacted" for facet in
                    ("names", "previews", "thumbnails", "ocr_text", "location_data")},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


@pytest.fixture()
def corpus(p7_conn):
    """A file, a run, a unit, one observation, and a policy. No classification.

    No classification is the REALISTIC state (D2: the detector is unwritten), so the
    fixture that denies needs no setup and the fixture that releases has to write one
    by hand.
    """
    create_evidence_schema(p7_conn)
    create_privacy_schema(p7_conn)
    record_file(p7_conn, file_id="file-1", current_path="/corpus/passport.pdf",
                content_hash=CONTENT_HASH)
    record_run(p7_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="pdf_text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=1))
    record_text_unit(p7_conn, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    record_observation(p7_conn, Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name="pdf_text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="992-33-1188", location=LOCATION, occurrence_count=1,
        observed_at=FIXED_CLOCK, reliability="direct", run_id="run-1",
        context_before="Passport number ", context_after=" issued 2019.",
        context_truncated=False)) 
    set_policy(p7_conn, a_policy(), author="P7", component_version=COMPONENT,
               user_id="joseph")
    return p7_conn


def classify(conn, handling_class, *, protected):
    """Stands in for the detector nobody has written (D2).

    The test writes the classification itself and says so, because until a rule set
    is supplied every real file resolves to `Denied(unclassified)` and the release
    path would be unreachable.
    """
    ClassificationStore(conn).write(ClassificationRecord(
        file_id="file-1", content_hash=CONTENT_HASH, handling_class=handling_class,
        protected=protected, basis="user", evidence_refs=(KEY,),
        reliability_state="user_confirmed", observed_at=FIXED_CLOCK))


def a_gate(conn, **over) -> Gate:
    base = dict(plan_version="plan-1", component_version=COMPONENT,
                classifier=classifier, transform=transform,
                consent_scope_for=lambda file_id: "Academics",
                unclassified_permits_local=False, clock=lambda: FIXED_CLOCK)
    base.update(over)
    return Gate(conn, **base)


# --- the signature: no override, and nothing unpublished ----------------------

def test_release_takes_the_request_and_nothing_else():
    # B2: "P8 adopts this call, this return union, and these field names verbatim."
    # An equality, not a subset: the whitelist is what proves no unpublished
    # parameter exists at all.
    assert set(inspect.signature(Gate.release).parameters) == {"self", "request"}


def test_no_forbidden_word_appears_in_any_published_name():
    published = set(inspect.signature(Gate.release).parameters)
    for kind in (ModelCallRequest, Released, Denied, NeedsConsent, Target,
                 ModelTarget):
        published |= {field.name for field in dataclasses.fields(kind)}
    assert not published & FORBIDDEN_PARAMETER_NAMES


def test_the_blacklist_names_the_words_a_convenience_would_use():
    assert {"force", "override", "bypass", "allow", "approved", "skip", "unsafe",
            "trusted", "internal"} <= FORBIDDEN_PARAMETER_NAMES


def test_the_constructor_carries_no_override_either():
    parameters = set(inspect.signature(Gate.__init__).parameters)
    assert not parameters & FORBIDDEN_PARAMETER_NAMES


def test_three_constructor_parameters_have_no_default():
    # Each is an open question refusing to be guessed: the redaction transform
    # (SPEC *Deferred*), "what is a corpus area" (OQ3), and whether an unclassified
    # file permits a LOCAL call (OQ5).
    parameters = inspect.signature(Gate.__init__).parameters
    for name in ("classifier", "transform", "consent_scope_for",
                 "unclassified_permits_local"):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert parameters[name].default is inspect.Parameter.empty


# --- the request carries references, never content ----------------------------

def test_the_request_is_spec_6s_seven_fields():
    assert REQUEST_FIELDS == ("stage", "target", "model_target", "requested_items",
                              "prompt_template_id", "prompt_fingerprint",
                              "max_dossier_tokens")
    assert tuple(f.name for f in dataclasses.fields(ModelCallRequest)) == REQUEST_FIELDS


def test_no_request_field_accepts_a_document_a_path_or_an_observation():
    # "P8 never holds releasable content. It composes a request out of REFERENCES."
    # Asserted over the annotations, so a field typed to take a string of document
    # text is a red test rather than a code review someone has to remember to do.
    annotations = {f.name: str(f.type) for f in dataclasses.fields(ModelCallRequest)}
    assert annotations["stage"] == "str"
    assert annotations["prompt_template_id"] == "str"
    assert annotations["prompt_fingerprint"] == "str"
    assert annotations["max_dossier_tokens"] == "int"
    assert annotations["target"] == "Target"
    assert annotations["model_target"] == "ModelTarget"
    assert annotations["requested_items"] == "tuple[object, ...]"
    for annotation in annotations.values():
        assert "Observation" not in annotation
        assert "Path" not in annotation
        assert "TextUnit" not in annotation


def test_call_site_is_not_a_request_field():
    # B2: "`call_site` is already inside the fingerprint, so it is not a separate
    # request field and not a separate binding term."
    assert "call_site" not in REQUEST_FIELDS


def test_released_is_spec_6s_six_fields():
    assert RELEASED_FIELDS == ("release_id", "audit_id", "policy_version",
                               "materialised_items", "redaction_manifest",
                               "model_target")
    assert tuple(f.name for f in dataclasses.fields(Released)) == RELEASED_FIELDS


def test_the_decision_order_is_published():
    assert DECISION_ORDER == (
        "mode_forbids_target", "unclassified", "protected_cloud_target",
        "protected_records_template", "always_local_item", "needs_consent",
        "whole_document_requested", "dossier_over_budget", "audit", "release")


# --- the three branches -------------------------------------------------------

def test_an_unclassified_file_is_denied_and_this_is_the_ordinary_path(corpus):
    # D2: the detector is unwritten, so on a real corpus EVERY file lands here.
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification" -- there is no path from "nothing has looked" to `public_low`.
    decision = a_gate(corpus).release(a_request())
    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"


def test_a_denial_never_resolves_to_a_low_class(corpus):
    decision = a_gate(corpus).release(a_request())
    assert UNCLASSIFIED == "unreadable_unclassified"
    assert "public_low" not in decision.explanation


def test_a_cloud_target_under_a_local_first_mode_is_denied(corpus):
    # §8.4: "Fully offline mode: No content leaves the device."
    set_policy(corpus, a_policy(policy_version="policy-2", operation_mode="offline"),
               author="P7", component_version=COMPONENT, user_id="joseph")
    decision = a_gate(corpus).release(a_request())
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"


def test_a_protected_file_with_a_cloud_target_is_denied(corpus):
    # §8.4: "Protected material should not be included in cloud-model prompts by
    # default." The flag is consumed, never inferred from the class (Open question 1).
    classify(corpus, "personal_non_sensitive", protected=True)
    decision = a_gate(corpus).release(a_request())
    assert isinstance(decision, Denied)
    assert decision.reason == "protected_cloud_target"


def test_a_sensitive_file_without_a_grant_needs_consent(corpus):
    # §8.4: "If a model needs text containing sensitive content, the user should see
    # that requirement and choose whether to allow a local model, a cloud model, a
    # redacted prompt, or no model use."
    classify(corpus, "sensitive_personal", protected=False)
    decision = a_gate(corpus).release(a_request())
    assert isinstance(decision, NeedsConsent)
    assert decision.options == ("local_model", "cloud_model", "redacted_prompt",
                                "no_model_use")
    assert SENSITIVE_CLASSES == ("sensitive_personal",
                                 "highly_sensitive_credential_bearing")


def test_a_grant_for_the_scope_turns_consent_into_a_release(corpus):
    classify(corpus, "sensitive_personal", protected=False)
    set_policy(corpus, a_policy(policy_version="policy-3",
                                consent_grants=(("Academics", "cloud_model"),)),
               author="P7", component_version=COMPONENT, user_id="joseph")
    decision = a_gate(corpus).release(a_request())
    assert isinstance(decision, Released)


def test_a_clean_release_carries_the_redacted_value_and_the_manifest(corpus):
    classify(corpus, "personal_non_sensitive", protected=False)
    decision = a_gate(corpus).release(a_request())
    assert isinstance(decision, Released)
    (item,) = decision.materialised_items
    assert isinstance(item, Materialised)
    assert item.value == "[passport_number]"
    assert item.context_before == "Passport number "
    assert decision.redaction_manifest.any_redacted is True
    assert decision.model_target == CLOUD
    assert decision.policy_version == "policy-1"


def test_the_released_payload_holds_no_unredacted_value(corpus):
    classify(corpus, "personal_non_sensitive", protected=False)
    decision = a_gate(corpus).release(a_request())
    assert "992-33-1188" not in str(decision.materialised_items)


def test_an_over_budget_request_is_denied_as_the_m9_backstop(corpus):
    # M9: P8 measures and runs §8.6's ladder BEFORE calling. A
    # `dossier_over_budget` denial in a running pipeline is a P8 defect to fix, not
    # a normal outcome -- reachable in test, and it should never fire in a correct
    # pipeline. The ceiling is read from P1; no number is written here.
    classify(corpus, "personal_non_sensitive", protected=False)
    set_ceiling(corpus, "model.max_dossier_tokens_per_call", 100)
    decision = a_gate(corpus).release(a_request(max_dossier_tokens=4000))
    assert isinstance(decision, Denied)
    assert decision.reason == "dossier_over_budget"


def test_a_whole_document_excerpt_is_denied(corpus):
    # §8.4: "It should not send full documents where a short heading or OCR excerpt
    # is enough to resolve the question."
    classify(corpus, "personal_non_sensitive", protected=False)
    whole = Excerpt(observation_key=KEY, span=TextSpan(0, len(BODY)),
                    reason="all of it")
    decision = a_gate(corpus).release(a_request(requested_items=(whole,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "whole_document_requested"


def test_every_denial_carries_an_explanation_and_a_remedy(corpus):
    # §8.6 requires the UI show "what has been deferred, and why", and a denial with
    # no legitimate alternative is a dead end the user cannot act on.
    decision = a_gate(corpus).release(a_request())
    assert decision.explanation
    assert decision.remedy_options


# --- the ordering guarantee, from the gate's side ------------------------------

def test_the_audit_record_exists_before_the_released_is_returned(corpus):
    classify(corpus, "personal_non_sensitive", protected=False)
    decision = a_gate(corpus).release(a_request())
    record = audit_record(corpus, decision.audit_id)
    assert record.outcome == "released"
    assert record.release_id == decision.release_id
    assert record.excerpts_included == ((KEY, SPAN),)


def test_a_denial_is_audited_too(corpus):
    decision = a_gate(corpus).release(a_request())
    (record,) = audit_records_for(corpus, file_id="file-1")
    assert record.outcome == "denied"
    assert isinstance(decision, Denied)


def test_a_consent_request_is_audited_and_no_release_accompanies_it(corpus):
    # Done-means 7, from the side Done-means 7 itself says is testable: "the audit
    # log holds a `consent_requested` event and no `model_release` for that request
    # until a choice is recorded."
    classify(corpus, "sensitive_personal", protected=False)
    a_gate(corpus).release(a_request())
    outcomes = [r.outcome for r in audit_records_for(corpus, file_id="file-1")]
    assert outcomes == ["consent_requested"]


def test_nothing_materialises_before_every_denying_check_has_run(corpus):
    # The reason DECISION_ORDER is published: a gate that resolved first would hold
    # the text in memory before deciding it was not allowed to.
    seen = []

    def watching_classifier(value, *, context_before, context_after):
        seen.append(value)
        return "passport_number"

    decision = a_gate(corpus, classifier=watching_classifier).release(a_request())
    assert isinstance(decision, Denied)
    assert seen == []


# --- one door -----------------------------------------------------------------

def test_release_is_the_only_public_entry_point_that_returns_a_released(corpus):
    # Done-means 3's gate half. Every other public callable on the facade is checked
    # by return annotation, so a second door has to be added deliberately AND
    # annotated as returning something else to hide.
    classify(corpus, "personal_non_sensitive", protected=False)
    gate = a_gate(corpus)
    doors = []
    for name in dir(gate):
        if name.startswith("_"):
            continue
        member = getattr(type(gate), name, None)
        if not callable(member):
            continue
        annotation = str(inspect.signature(member).return_annotation)
        if "Released" in annotation or "ReleaseDecision" in annotation:
            doors.append(name)
    assert doors == ["release"]


def test_a_contract_violation_propagates_rather_than_becoming_a_denial(corpus):
    # The fourth kind of refusal. A request that addresses a span the evidence does
    # not carry is about the CALL, and the gate does not convert a caller's mistake
    # into a policy outcome the caller might then absorb.
    from privacy.resolve import UnresolvableSpan
    classify(corpus, "personal_non_sensitive", protected=False)
    bad = Excerpt(observation_key="sha256:" + "f" * 64, span=TextSpan(16, 27),
                  reason="a key nothing carries")
    with pytest.raises(UnresolvableSpan):
        a_gate(corpus).release(a_request(requested_items=(bad,)))


def test_the_gate_imports_none_of_p5s_three_refusals():
    # Task 21 asserts this repo-wide; asserted here because the gate is where the
    # confusion would land. P7 refuses RELEASE; P5's two refuse READING, and a file
    # that failed either never acquired the (file_id, content_hash) P7 keys on.
    import privacy.gate
    import privacy.release
    for module in (privacy.gate, privacy.release):
        for name in ("ProtectedContainerRefused", "DatalessRefused",
                     "UnauthorizedTranscription"):
            assert not hasattr(module, name)
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_release.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.gate'`. Collection fails on the
import line; no test runs.

- [ ] **Step 3: Write `src/privacy/release.py`**

```python
# src/privacy/release.py
"""SPEC §6's request, its three-branch return, and the words that may not be parameters.

§8.4 opens with a sequencing requirement -- "Privacy policy must be enforced before
content reaches any model or external connector" -- and this module is the shape that
makes it structural. P8 composes a request out of REFERENCES; the gate resolves them,
redacts, audits, and mints a `Released`; the transport takes a `Released` and nothing
else. There is no entry point that takes a string.

`ReleaseDecision` has three branches and they are not interchangeable. `Released` is a
capability. `Denied` is the gate's answer, and it is the only one of the product's
refusals that consent may override -- which is what separates it from P5's protected
container and dataless refusals, both of which refuse READING and neither of which has
a consent path. `NeedsConsent` is a question only the user can answer: B2 forbids a
caller from absorbing it into an abstention, a denial, or a retry. Consent pending is
not consent refused.
"""
from __future__ import annotations

from dataclasses import dataclass, fields

from privacy.items import Excerpt, RedactedIdentifier
from privacy.redaction import RedactionManifest
from privacy.resolve import Materialised
from privacy.vocabulary import (
    CONSENT_OPTIONS, check_denial_reason, check_handling_class,
)

#: §6: "{ locality: local | cloud, model_id, provider }". Two values and no third:
#: Open question 9 asks what an "external connector" besides a model is, and until it
#: is answered `ModelTarget` cannot describe one.
LOCALITIES: tuple[str, str] = ("local", "cloud")

#: Checked against Task 2's vocabulary at import, so these are provably members and
#: not a second spelling of them.
UNCLASSIFIED: str = check_handling_class("unreadable_unclassified")

#: §8.4's "text containing sensitive content", as the two classes the design names
#: that way: "Sensitive personal" and "Highly sensitive or credential-bearing".
#: This is about the CLASS. Whether `protected` is co-extensive with these two is
#: Open question 1 and is not answered here -- the flag is consumed separately.
SENSITIVE_CLASSES: tuple[str, str] = (
    check_handling_class("sensitive_personal"),
    check_handling_class("highly_sensitive_credential_bearing"),
)

#: The two item kinds that resolve to document text. The other four carry none: §4
#: says an evidence reference is "an id only -- no content".
TEXT_BEARING: tuple[type, ...] = (Excerpt, RedactedIdentifier)

#: The order the decision runs in, published so a reordering is a diff on a constant
#: rather than an invisible behaviour change. Nothing materialises before "needs_consent".
DECISION_ORDER: tuple[str, ...] = (
    "mode_forbids_target", "unclassified", "protected_cloud_target",
    "protected_records_template", "always_local_item", "needs_consent",
    "whole_document_requested", "dossier_over_budget", "audit", "release",
)

#: The words a future convenience would reach for. Asserted disjoint from every
#: published parameter and field name, by parsing the signature -- never by scanning
#: source text, which matches comments and docstrings.
FORBIDDEN_PARAMETER_NAMES: frozenset[str] = frozenset({
    "force", "override", "bypass", "allow", "allow_all", "approved", "skip",
    "unsafe", "trusted", "internal", "admin", "debug", "escalate", "ignore_policy",
    "no_audit", "unaudited", "raw", "plaintext", "content", "text", "document",
    "already_approved", "assume_consent", "privileged",
})


class MalformedRequest(ValueError):
    """Shape check on the call. A request that cannot be decided is not denied."""


class MalformedDecision(ValueError):
    """A branch constructed outside its published shape."""


@dataclass(frozen=True, slots=True)
class ModelTarget:
    """§6: which model, and whether it is on this device."""

    locality: str
    model_id: str
    provider: str

    def __post_init__(self) -> None:
        if self.locality not in LOCALITIES:
            raise MalformedRequest(
                f"locality {self.locality!r} is not one of {LOCALITIES}")
        if not self.model_id or not self.provider:
            raise MalformedRequest(
                "§8.4 audits which model received the data; a provider-less "
                "identifier does not answer that for a hosted model")

    def to_mapping(self) -> dict[str, str]:
        return {"locality": self.locality, "model_id": self.model_id,
                "provider": self.provider}


@dataclass(frozen=True, slots=True)
class Target:
    """§6: "{ file_ids[], group_id? }" (§4.4, §7.7)."""

    file_ids: tuple[str, ...]
    group_id: str | None = None

    def __post_init__(self) -> None:
        if not self.file_ids:
            raise MalformedRequest("a request names at least one file")


@dataclass(frozen=True, slots=True)
class ModelCallRequest:
    """SPEC §6's seven fields, exactly. References only, never materialised content."""

    stage: str
    target: Target
    model_target: ModelTarget
    requested_items: tuple[object, ...]
    prompt_template_id: str
    prompt_fingerprint: str
    max_dossier_tokens: int

    def __post_init__(self) -> None:
        if not self.stage:
            raise MalformedRequest("§8.5 decomposes replay by stage")
        if not self.prompt_fingerprint:
            raise MalformedRequest(
                "§8.4 audits the prompt fingerprint, and B2 puts `call_site` inside "
                "it rather than beside it")
        if not self.requested_items:
            raise MalformedRequest("a request with no items has nothing to release")


REQUEST_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(ModelCallRequest))


@dataclass(frozen=True, slots=True)
class Released:
    """SPEC §6's six fields. Single-use and bound; Task 12 adds the ledger."""

    release_id: str
    audit_id: int
    policy_version: str
    materialised_items: tuple[Materialised, ...]
    redaction_manifest: RedactionManifest
    model_target: ModelTarget


RELEASED_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(Released))


@dataclass(frozen=True, slots=True)
class Denied:
    """The gate's answer. Evidence-referenced, and never a dead end (§8.6)."""

    reason: str
    explanation: str
    remedy_options: tuple[str, ...]

    def __post_init__(self) -> None:
        check_denial_reason(self.reason)
        if not self.explanation:
            raise MalformedDecision(
                "§8.6 requires the UI show what has been deferred, and why")
        if not self.remedy_options:
            raise MalformedDecision(
                "a denial with no legitimate alternative is a dead end the user "
                "cannot act on (§8.6)")


@dataclass(frozen=True, slots=True)
class NeedsConsent:
    """A question only the user can answer. Task 14 adds `consent_request_id`."""

    requirement: str
    options: tuple[str, ...]

    def __post_init__(self) -> None:
        if tuple(self.options) != CONSENT_OPTIONS:
            raise MalformedDecision(
                f"§8.4 offers exactly {CONSENT_OPTIONS}; a caller that saw fewer "
                "would be choosing on the user's behalf")
        if not self.requirement:
            raise MalformedDecision(
                "§8.4: the user should SEE that requirement before choosing")


ReleaseDecision = Released | Denied | NeedsConsent
```

- [ ] **Step 4: Write `src/privacy/gate.py`**

```python
# src/privacy/gate.py
"""The one door. `Gate.release(ModelCallRequest) -> ReleaseDecision`, and nothing else.

B2 adopts this signature verbatim on both sides, so `release` takes the request and
NOTHING ELSE -- no override, no flag, no connection. Everything the gate needs beyond
the request is constructor state, and four of those constructor parameters carry no
default because each is an open question this plan will not guess:

    classifier / transform      SPEC *Deferred*: identifier classes and the redaction
                                transform are not enumerated anywhere in the design.
    consent_scope_for           Open question 3: "What is a 'corpus area'? ... Consent
                                grants cannot be scoped until this is named."
    unclassified_permits_local  Open question 5: does `unreadable_unclassified` permit
                                a LOCAL model call?

The gate writes exactly one thing -- the audit record -- and it writes it BEFORE the
decision is returned, because §8.4 makes recording the authorization part of granting
it. It raises nothing of its own: `Denied` and `NeedsConsent` are values, and the
catcher is always the caller's. The two exceptions that do escape come from
`resolve` and are about the CALL rather than about policy.

Tasks 12, 13 and 14 modify this file: Task 12 replaces `_mint` with `binding`'s ledger,
Task 13 routes the eight denials through `denial.deny`, and Task 14 adds the
`consent_request_id`. The signature does not move.
"""
from __future__ import annotations

import secrets
import sqlite3
from collections.abc import Callable

from database_agent.budget import get_ceiling
from database_agent.files_table import get_file
from evidence_shape.canonical import canonical_json

from privacy.audit import AuditRecord, append_audit
from privacy.authorship import SUBSYSTEM
from privacy.classification import resolve_class
from privacy.classification_store import ClassificationStore
from privacy.defaults import LOCAL_FIRST_MODES
from privacy.items import WholeDocumentRequested, check_item
from privacy.policy import current_policy
from privacy.redaction import RedactionManifest, apply_redaction
from privacy.release import (
    SENSITIVE_CLASSES, TEXT_BEARING, UNCLASSIFIED, Denied, ModelCallRequest,
    NeedsConsent, ReleaseDecision, Released,
)
from privacy.resolve import materialise
from privacy.vocabulary import CONSENT_OPTIONS

_DOSSIER_CEILING = "model.max_dossier_tokens_per_call"


class Gate:
    """§8.4's gate. One object, one door, no second name."""

    def __init__(self, conn: sqlite3.Connection, *, plan_version: str,
                 component_version: str, classifier, transform,
                 consent_scope_for: Callable[[str], str],
                 unclassified_permits_local: bool,
                 clock: Callable[[], str]) -> None:
        self._conn = conn
        self._plan_version = plan_version
        self._component_version = component_version
        self._classifier = classifier
        self._transform = transform
        self._consent_scope_for = consent_scope_for
        self._unclassified_permits_local = unclassified_permits_local
        self._clock = clock
        self._store = ClassificationStore(conn)

    def release(self, request: ModelCallRequest) -> ReleaseDecision:
        """§8.4's only door. See `release.DECISION_ORDER` for the order and why."""
        policy = current_policy(self._conn, plan_version=self._plan_version)
        cloud = request.model_target.locality == "cloud"
        state = self._classifications(request)
        classes = {file_id: resolve_class(record)
                   for file_id, (_, record) in state.items()}

        if cloud and policy.operation_mode in LOCAL_FIRST_MODES:
            return self._deny(
                request, policy, state, classes, "mode_forbids_target",
                f"the policy is in {policy.operation_mode!r} mode, under which no "
                f"content leaves the device, and this call targets "
                f"{request.model_target.provider!r}",
                ("run this stage against a local model",
                 "change the operation mode, which is a first-class plan diff"))

        unclassified = sorted(f for f, c in classes.items() if c == UNCLASSIFIED)
        if unclassified and (cloud or not self._unclassified_permits_local):
            return self._deny(
                request, policy, state, classes, "unclassified",
                f"{len(unclassified)} of {len(classes)} targeted files have no "
                "classification, and §8.4 makes classification a precondition of "
                "escalation. Absence resolves to `unreadable_unclassified`, never to "
                "a lower class",
                ("classify the file and call again",
                 "leave the file in review, which §8.6 prefers to a guess"))

        protected = sorted(f for f, (_, record) in state.items()
                           if record is not None and record.protected)
        if cloud and protected:
            return self._deny(
                request, policy, state, classes, "protected_cloud_target",
                f"{len(protected)} targeted files are protected, and protected "
                "material is not included in cloud-model prompts by default",
                ("run this stage against a local model",
                 "grant consent for this area, which is a recorded user act"))

        if self._needs_consent(request, policy, classes):
            return self._request_consent(request, policy, state, classes)

        materialised, manifest = self._materialise(request)
        ceiling = get_ceiling(self._conn, _DOSSIER_CEILING)
        if ceiling is not None and request.max_dossier_tokens > ceiling:
            return self._deny(
                request, policy, state, classes, "dossier_over_budget",
                f"the caller is operating under {request.max_dossier_tokens} tokens "
                f"and the configured ceiling is {ceiling}. M9 puts the measurement "
                "and §8.6's reduction ladder in the caller, before this call; "
                "reaching this denial in a running pipeline is a caller defect",
                ("summarize deterministic facts", "preserve anchor excerpts",
                 "split the task", "defer the decision"))

        release_id = self._mint()
        audit_id = self._append(
            request, policy, state, classes, outcome="released",
            release_id=release_id, excerpts=self._pairs(materialised),
            manifest=manifest)
        return Released(
            release_id=release_id, audit_id=audit_id,
            policy_version=policy.policy_version,
            materialised_items=materialised, redaction_manifest=manifest,
            model_target=request.model_target)

    # -- the pieces, in the order `release` uses them --------------------------

    def _classifications(self, request: ModelCallRequest) -> dict:
        state = {}
        for file_id in request.target.file_ids:
            content_hash = get_file(self._conn, file_id)["content_hash"]
            state[file_id] = (content_hash,
                              self._store.current(file_id, content_hash))
        return state

    def _needs_consent(self, request, policy, classes) -> bool:
        """§8.4: "If a model needs text containing sensitive content"."""
        if not any(isinstance(item, TEXT_BEARING)
                   for item in request.requested_items):
            return False
        sensitive = [f for f, c in classes.items() if c in SENSITIVE_CLASSES]
        if not sensitive:
            return False
        granted = set(policy.consent_grants)
        option = "cloud_model" if request.model_target.locality == "cloud" \
            else "local_model"
        return any((self._consent_scope_for(file_id), option) not in granted
                   for file_id in sensitive)

    def _materialise(self, request: ModelCallRequest):
        resolved, entries = [], []
        for item in request.requested_items:
            if not isinstance(item, TEXT_BEARING):
                continue
            found = materialise(self._conn, item)
            check_item(item, unit_length=found.unit_length)
            value, entry = apply_redaction(
                found.value, observation_key=found.observation_key,
                span=found.span, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                classifier=self._classifier, transform=self._transform)
            resolved.append(
                type(found)(observation_key=found.observation_key, span=found.span,
                            value=value, zone=found.zone,
                            context_before=found.context_before,
                            context_after=found.context_after,
                            context_truncated=found.context_truncated,
                            unit_length=found.unit_length))
            entries.append(entry)
        return tuple(resolved), RedactionManifest(entries=tuple(entries))

    @staticmethod
    def _pairs(materialised) -> tuple[tuple[str, str], ...]:
        return tuple((item.observation_key, item.span) for item in materialised)

    @staticmethod
    def _mint() -> str:
        """Task 12 replaces this with `binding.mint_release` and its ledger."""
        return secrets.token_hex(16)

    def _deny(self, request, policy, state, classes, reason, explanation,
              remedy_options) -> Denied:
        self._append(request, policy, state, classes, outcome="denied",
                     release_id=None, excerpts=(),
                     manifest=RedactionManifest(entries=()))
        return Denied(reason=reason, explanation=explanation,
                      remedy_options=tuple(remedy_options))

    def _request_consent(self, request, policy, state, classes) -> NeedsConsent:
        self._append(request, policy, state, classes, outcome="consent_requested",
                     release_id=None, excerpts=(),
                     manifest=RedactionManifest(entries=()))
        return NeedsConsent(
            requirement=(
                "this call needs text from files classified "
                f"{sorted({c for c in classes.values() if c in SENSITIVE_CLASSES})}, "
                f"and the policy holds no grant for the scope"),
            options=CONSENT_OPTIONS)

    def _append(self, request, policy, state, classes, *, outcome, release_id,
                excerpts, manifest) -> int:
        """The one write. It happens before the decision is returned (§8.4)."""
        single = len(request.target.file_ids) == 1
        distinct = sorted(set(classes.values()))
        record = AuditRecord(
            authorizing_policy=policy.policy_version,
            file_sensitivity=(distinct[0] if len(distinct) == 1
                              else canonical_json(distinct)),
            excerpts_included=excerpts,
            redaction_applied=manifest.any_redacted,
            model=request.model_target.to_mapping(),
            prompt_fingerprint=request.prompt_fingerprint,
            audit_id=None, release_id=release_id, observed_at=self._clock(),
            stage=request.stage, file_ids=request.target.file_ids,
            group_id=request.target.group_id,
            content_hashes=tuple(h for h, _ in state.values()),
            operation_mode=policy.operation_mode,
            policy_version=policy.policy_version, plan_version=policy.plan_version,
            outcome=outcome,
            file_id=request.target.file_ids[0] if single else None,
            content_hash=state[request.target.file_ids[0]][0] if single else None,
            redaction_manifest=tuple(manifest.to_mapping()))
        return append_audit(self._conn, record, author=SUBSYSTEM,
                            component_version=self._component_version)
```

- [ ] **Step 5: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_release.py -v`
Expected: PASS — 25 passed

- [ ] **Step 6: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–11 green, and P1–P5's 1292 tests still green.

- [ ] **Step 7: Commit**

```bash
git add src/privacy/release.py src/privacy/gate.py tests/p7/test_p7_release.py
git commit -m "feat(P7): Gate.release, the three-branch union, and a signature with no override"
```

---
