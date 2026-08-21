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
