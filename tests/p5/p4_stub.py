# tests/p5/p4_stub.py
"""P4's SPEC, stubbed - a TEST-HARNESS file, not a production module.

Reconstructed from ../../P4-evidence-shape/SPEC.md: the five closed vocabularies, the
locator serialization with its escaping rules, and the twelve conformance rules.
Every extractor test in tests/p5/ validates its output through this file, so a P5
extractor cannot ship a record P4 would reject.

WHEN P4 LANDS: delete this file and change the imports in tests/p5/ to
    # When P4 ships, this stub is deleted and these are the real imports:
    #   from evidence_shape.locator import parse_locator, serialize_locator
    #   from evidence_shape.vocabulary import SOURCE_TYPES, ZONES
    #   from evidence_shape.conformance import validate_observation
    # P4 publishes `serialize_locator`, not `locator_for`, and keeps the vocabularies
    # in their own module. There is no `evidence` package -- it is `evidence_shape`.
Nothing under src/extractors/ imports this file, so nothing under src/extractors/
changes.

Two rules are checked structurally rather than semantically, and this file says so
rather than pretending otherwise: rule 8 (determinism) is a property of two runs and
is asserted in tests/p5/test_p5_one_shape.py; rule 12 (no absence, no conflict) is
checked here as "no absence or conflict field, and a non-empty raw_value", with the
substantive check living in tests/p5/test_p5_image.py where section 2.6's three traps
are.
"""
from __future__ import annotations

import hashlib
from typing import Any, Iterable, Mapping

#: P4 "Zone vocabulary (closed)". Fifteen rows.
ZONES: tuple[str, ...] = (
    "filename", "path", "metadata", "title", "heading", "body", "table",
    "header_footer", "notes", "link", "annotation", "reference_list", "manifest",
    "ocr", "transcript",
)

#: P4 "Segment kinds (closed)". Fifteen rows.
SEGMENT_KINDS: tuple[str, ...] = (
    "page", "slide", "sheet", "heading", "paragraph", "table", "row", "column",
    "cell", "region", "layer", "artboard", "field", "entry", "key",
)

#: P4 segment-kind rule 2 - addressed by label, never by index.
LABEL_ADDRESSED: tuple[str, ...] = ("field", "entry", "key")

#: P4 "`source_type` vocabulary (section 2.9's families, closed)". Fourteen.
SOURCE_TYPES: tuple[str, ...] = (
    "filesystem", "text_document", "spreadsheet", "presentation", "image", "ocr",
    "email", "calendar", "contacts", "code_structured", "audio_video",
    "design_creative", "archive", "opaque_binary",
)

#: Section 3.13's six. An extractor may write the first two only (P4 D11).
RELIABILITY_STATES: tuple[str, ...] = (
    "direct", "possible", "validated", "llm_supported", "user_confirmed", "rejected",
)
EXTRACTOR_RELIABILITY: tuple[str, ...] = ("direct", "possible")

#: P4 `completeness` (closed), after B1 added `metadata_only` and C4 added `dataless`.
COMPLETENESS: tuple[str, ...] = (
    "complete", "capped", "partial", "metadata_only", "deferred", "unsupported",
    "unreadable", "failed", "dataless",
)

#: P4 conformance rule 9, as M3 relaxed it: `unreadable` and `partial` runs MAY and
#: normally DO carry observations (section 2.9's "indexed-but-unreadable").
#: P4 conformance rule 9. MUST equal P4's tuple: `metadata_only` joined it when
#: fixture 19 was frozen (the stopping extractor emits nothing; the file stays
#: indexed through its `filesystem` run), and `dataless` joined it with C4 (nothing
#: was opened, so nothing was seen). This is not documentation -- the rule-9 check
#: below reads it, so a three-value copy here would let P5 emit observations on a
#: `metadata_only` run that P4 forbids: one rule, two parts, opposite behaviour.
ZERO_OBSERVATION_COMPLETENESS: tuple[str, ...] = (
    "unsupported", "deferred", "failed", "metadata_only", "dataless")

#: I4, closed.
ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr", "llm")

OBSERVATION_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version",
    "source_type", "raw_value", "normalized_value", "location",
    "context_before", "context_after", "context_truncated",
    "occurrence_count", "observed_at", "reliability",
    "confidence", "signal_tier",
)
NULLABLE_OBSERVATION_FIELDS: tuple[str, ...] = ("normalized_value", "confidence",
                                                "signal_tier")

#: P4's prohibitions, as schema-level rejections (conformance rule 6).
FORBIDDEN_OBSERVATION_FIELDS: tuple[str, ...] = (
    "locator", "path_proposal", "destination", "destination_node", "domain",
    "category", "field_name", "fact", "group_id", "node_id", "template_id",
    "plan_id", "plan_version", "handling_class", "sensitivity_state", "preferred",
    "absent", "conflict", "resolution", "screenshot", "media_type",
)

_ESCAPE = set("%/=#@:")


def _escape(label: str) -> str:
    """P4: percent-encode % / = # @ : and control characters, uppercase hex, UTF-8."""
    out = []
    for ch in label:
        if ch in _ESCAPE or ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.extend(f"%{byte:02X}" for byte in ch.encode("utf-8"))
        else:
            out.append(ch)
    return "".join(out)


def _unescape(text: str) -> str:
    raw = bytearray()
    i = 0
    while i < len(text):
        if text[i] == "%":
            raw.append(int(text[i + 1:i + 3], 16))
            i += 3
        else:
            raw.extend(text[i].encode("utf-8"))
            i += 1
    return raw.decode("utf-8")


def unit_locator_for(container_path: Iterable[Mapping[str, Any]]) -> str:
    parts = []
    for seg in container_path:
        kind = seg["kind"]
        addr = _escape(seg["label"]) if kind in LABEL_ADDRESSED else str(seg["index"])
        parts.append(f"{kind}={addr}")
    return "/".join(parts)


def locator_for(location: Mapping[str, Any]) -> str:
    """P4's canonical serialization.

    locator := zone [":" segments] ["#" text_span | "@" time_span]
    """
    text = location["zone"]
    segments = unit_locator_for(location["container_path"])
    if segments:
        text += ":" + segments
    span, time_span = location.get("text_span"), location.get("time_span")
    if span is not None:
        text += f"#{span['start']}-{span['end']}"
    elif time_span is not None:
        text += f"@{time_span['start_ms']}-{time_span['end_ms']}"
    return text


def parse_locator(text: str) -> dict:
    """Inverse of locator_for. Labels escape # and @, so the first raw one delimits."""
    head, mark, tail = text, None, ""
    for i, ch in enumerate(text):
        if ch in "#@":
            head, mark, tail = text[:i], ch, text[i + 1:]
            break
    zone, _, segment_text = head.partition(":")
    container_path = []
    if segment_text:
        for chunk in segment_text.split("/"):
            kind, _, addr = chunk.partition("=")
            if kind in LABEL_ADDRESSED:
                container_path.append({"kind": kind, "index": None,
                                       "label": _unescape(addr)})
            else:
                container_path.append({"kind": kind, "index": int(addr),
                                       "label": None})
    span = time_span = None
    if mark == "#":
        start, _, end = tail.partition("-")
        span = {"start": int(start), "end": int(end)}
    elif mark == "@":
        start, _, end = tail.partition("-")
        time_span = {"start_ms": int(start), "end_ms": int(end)}
    return {"zone": zone, "container_path": tuple(container_path),
            "text_span": span, "time_span": time_span, "region": None}


def observation_key(observation: Mapping[str, Any]) -> str:
    """P4: sha256(content_hash + extractor_name + locator + raw_value), DELIBERATELY
    excluding extractor_version so section 8.5's replay can diff versions (MINOR 8).
    P4 assigns it; this stub computes it so tests can assert its stability."""
    material = "\x1f".join((observation["content_hash"], observation["extractor_name"],
                            locator_for(observation["location"]),
                            observation["raw_value"]))
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def validate_observation(observation: Mapping[str, Any], *,
                         text_units: Iterable[Mapping[str, Any]] = ()) -> None:
    """P4's conformance validator, rules 1-7 and 9-12. Fails; never coerces."""
    # Rule 1 - every section 2.8 field present, three context fields, not one.
    assert tuple(observation) == OBSERVATION_FIELDS, tuple(observation)
    for name in OBSERVATION_FIELDS:
        if name not in NULLABLE_OBSERVATION_FIELDS:
            assert observation[name] is not None, name
    # Rule 6 - no destination, domain, field name, group, node, template or plan.
    for name in FORBIDDEN_OBSERVATION_FIELDS:
        assert name not in observation, name
    assert isinstance(observation["file_id"], str)

    location = observation["location"]
    # Rule 2 - closed vocabularies.
    assert location["zone"] in ZONES, location["zone"]
    assert observation["source_type"] in SOURCE_TYPES, observation["source_type"]
    for seg in location["container_path"]:
        assert seg["kind"] in SEGMENT_KINDS, seg
        if seg["kind"] in LABEL_ADDRESSED:
            assert seg["index"] is None and seg["label"] is not None, seg
        else:
            assert isinstance(seg["index"], int) and seg["index"] >= 1, seg
    # Rule 3 - an extractor writes `direct` or `possible`.
    assert observation["reliability"] in EXTRACTOR_RELIABILITY, observation["reliability"]
    # Rule 4 - the locator round-trips.
    text = locator_for(location)
    back = parse_locator(text)
    assert back["zone"] == location["zone"], text
    assert len(back["container_path"]) == len(location["container_path"]), text
    for parsed, built in zip(back["container_path"], location["container_path"]):
        assert parsed["kind"] == built["kind"], text
        if built["kind"] in LABEL_ADDRESSED:
            assert parsed["label"] == built["label"], text
        else:
            assert parsed["index"] == built["index"], text
    assert back["text_span"] == location["text_span"], text
    assert back["time_span"] == location["time_span"], text
    # Rule 7 - occurrence_count >= 1.
    assert observation["occurrence_count"] >= 1
    # Rule 11 - signal_tier is section 2.6-scoped.
    if observation["signal_tier"] is not None:
        assert observation["signal_tier"] in (1, 2, 3)
        assert observation["source_type"] == "image", (
            "signal_tier is section 2.6's image hierarchy")
    # Rule 12 - an observation is a reading, never an absence or a comparison.
    assert observation["raw_value"] != "", "an absence has no value to record (2.6)"
    # Rules 5 and 10 - RAW-1 against the unit the container path names.
    span = location["text_span"]
    if span is not None:
        units = [u for u in text_units
                 if tuple(u["container_path"]) == tuple(location["container_path"])]
        assert units, f"no text_units row for {text} (rule 10)"
        stored = units[0]["text"]
        assert stored[span["start"]:span["end"]] == observation["raw_value"], (
            f"RAW-1 fails at {text}")


def validate_run(run: Mapping[str, Any], observation_count: int) -> None:
    """P4 conformance rule 9 plus the run-level vocabularies."""
    assert run["completeness"] in COMPLETENESS, run["completeness"]
    assert run["analysis_tier"] in ANALYSIS_TIERS, run["analysis_tier"]
    assert run["analysis_tier"] != "llm", "P8 is the only writer of `llm` (I4)"
    assert run["source_type"] in SOURCE_TYPES, run["source_type"]
    assert set(run["coverage"]) == {"units", "processed", "total"}, run["coverage"]
    assert run["observation_count"] == observation_count
    if run["completeness"] in ZERO_OBSERVATION_COMPLETENESS:
        assert observation_count == 0, (
            f"an {run['completeness']} run carries zero observations (rule 9)")
    if run["completeness"] in ("unreadable", "failed"):
        assert run["failure_reason"], "failure_reason is required here"
