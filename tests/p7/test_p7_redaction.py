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


def test_a_region_does_not_block_a_text_span_address():
    # Fixture 8's shape: the box is C3, the text span is not.
    boxed = Location(zone="ocr", container_path=(
        Segment(kind="page", index=4), Segment(kind="region", index=2)),
        text_span=TextSpan(0, 24), region=Region(0.08, 0.21, 0.55, 0.06, "norm"))
    assert span_address(boxed) == "ocr:page=4/region=2#0-24"


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
