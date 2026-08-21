# src/extractors/shape.py
"""P4's records, built by P5.

This module is a BUILDER for `../P4-evidence-shape/SPEC.md`'s three records, not a
second definition of them. It restates exactly two things, both of which are P5's own
half of the contract:

    EXTRACTOR_RELIABILITY   P4 D11 - an extractor may write two of section 3.13's six
    ANALYSIS_TIERS          I4 (closed) - P5 owns the vocabulary, writes the first three

`zone`, segment `kind`, `source_type` and `completeness` are P4's closed vocabularies
and are NOT restated: this module accepts the string it is handed and P4's validator
is the gate. Restating a closed vocabulary in the consumer is how one concept ends up
with two names, which is the defect this project has paid for most often.

Not computed here, because they are P4-assigned: `observation_id`, `observation_key`,
`run_id`, the canonical `locator`, `unit_locator`, and the three supersede columns.
P5 emits the structured location; P4 serializes it.
"""
from __future__ import annotations

from evidence_shape.location import region_from_mapping

import re
import unicodedata
from typing import Any, Mapping, Sequence

# `canonical_json` is re-exported under P4's own name, never redefined:
# `extractors/events.py` imports it from this module, so the name stays importable
# here -- but the form itself is P4's, because §8.5's replay diff and §3.4's cache key
# are both comparisons of stored bytes, and a second serialization is a second answer
# to "what are these bytes". P5 held a byte-identical copy of it while `fingerprint`
# below already delegated its DIGEST to P4; one edit to P4's canonical form and the
# fingerprint would have diverged again, silently, with no test failing.
from evidence_shape.canonical import canonical_json
from evidence_shape.observation import NON_EMPTY_FIELDS, check_non_empty
from evidence_shape.runs import config_fingerprint

#: Section 2.8's field list, in section 2.8's order, plus the additions P4 marks with
#: a cross. The three context fields are P4's published shape of section 2.8's single
#: "Surrounding context" line (M5): section 8.4 must be able to redact a value
#: without dropping its context.
OBSERVATION_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version",
    "source_type", "raw_value", "normalized_value", "location",
    "context_before", "context_after", "context_truncated",
    "occurrence_count", "observed_at", "reliability",
    "confidence", "signal_tier",
)

#: P4 D1. One shape for every source type; never a per-format string.
LOCATION_FIELDS: tuple[str, ...] = ("zone", "container_path", "text_span",
                                    "time_span", "region")

#: P4 D5 `extraction_runs`, minus `run_id`, which P4 assigns.
RUN_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version", "source_type",
    "analysis_tier", "config", "config_fingerprint", "completeness", "coverage",
    "observation_count", "started_at", "finished_at", "failure_reason",
)

#: P4 D12 / G1 `text_units`, minus `run_id` and `unit_locator`, which P4 assigns.
TEXT_UNIT_FIELDS: tuple[str, ...] = ("container_path", "text", "length", "truncated")

#: P4 D11: "Extractors may write only two of section 3.13's six reliability states."
#: `validated`, `llm_supported`, `user_confirmed` and `rejected` are fact-layer
#: outcomes (section 3.5); section 2.8 forbids extraction treating model output as
#: proof.
EXTRACTOR_RELIABILITY: tuple[str, str] = ("direct", "possible")

#: I4, ratified 2026-08-19 - closed. P5 owns the vocabulary.
ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr", "llm")

#: "P5 writes the first three; P8 is the only writer of `llm`."
P5_ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr")

#: P4 segment-kind rule 2: a label-addressed kind has no index.
LABEL_ADDRESSED_KINDS: tuple[str, ...] = ("field", "entry", "key")

#: P4's `observation.NON_EMPTY_FIELDS`, minus the one member P5 never receives.
#: `run_id` is P4-assigned (see this module's docstring), so it is the only field on
#: P4's list the builder cannot check. DERIVED by subtraction and not retyped: a
#: seventh field added to P4's tuple is gated here the same day, and P5 keeps no
#: second list of which fields may not be empty. The rule itself is P4's
#: `check_non_empty`, called -- not restated, the way the vocabularies above are not.
BUILDER_NON_EMPTY_FIELDS: tuple[str, ...] = tuple(
    name for name in NON_EMPTY_FIELDS if name != "run_id")

_SOFT_HYPHEN = "­"
_LINE_BREAK_HYPHEN = re.compile(r"-\n\s*")


class ForbiddenReliability(Exception):
    """P4 D11 - a fact-layer state reached an extractor."""


class ForbiddenAnalysisTier(Exception):
    """I4 - P5 attempted to write `llm`, which only P8 writes."""


def fingerprint(config: Mapping[str, Any]) -> str:
    """P4's `config_fingerprint` - "so section 3.4's key and section 8.5's diff can
    tell configs apart".

    This is the ONLY digest anywhere in P5's surface, and it is a digest of
    configuration, never of file bytes: the content hash is P1's and P5 never
    recomputes it (O5).

    **It delegates to P4 and computes nothing itself.** P5 previously called
    `hashlib.sha256` on the same canonical JSON, while P4's `sha256_of`
    length-prefixes the part before hashing. The canonical bytes were identical and
    the digests never were, so P4 rejected EVERY run record P5 emitted -- and because
    `config_fingerprint` is in §3.4's cache key and rule 8's four-field replay key,
    two runs of one process would never have matched and replay would have reported
    divergence that did not happen. P4 owns the field, so P4 computes it; a second
    computation of one value is the same defect as a second name for one concept.

    It calls P4's published function rather than repeating its two steps here. The
    first fix left P5 spelling out `sha256_of(canonical_json(...))`, which is the same
    defect one level up: P4 could add a step to `config_fingerprint` and P5 would
    diverge again with no test failing. `dict(...)` only because P4 takes a Mapping
    and the canonical form serializes a dict.
    """
    return config_fingerprint(dict(config))


def segment(kind: str, *, index: int | None = None, label: str | None = None) -> dict:
    """One typed segment of P4's `container_path`.

    P4 D3: indices are 1-based, because section 2.8's own examples are ("page 1,
    heading 2") and they appear in user-visible section 8.2 explanations.
    P4 segment-kind rule 2: an indexed kind is addressed by its index and its label
    is descriptive only; a label-addressed kind (`field`, `entry`, `key`) has no
    index.
    """
    if index is None and label is None:
        raise ValueError(f"segment {kind!r} needs an index or a label")
    if index is not None and index < 1:
        raise ValueError(f"container-path indices are 1-based (P4 D3); got {index!r}")
    if kind in LABEL_ADDRESSED_KINDS and index is not None:
        raise ValueError(f"{kind!r} is label-addressed and takes no index (P4 rule 2)")
    return {"kind": kind, "index": index, "label": label}


def location(*, zone: str, container_path: Sequence[Mapping[str, Any]] = (),
             text_span: Mapping[str, int] | None = None,
             time_span: Mapping[str, int] | None = None,
             region: Mapping[str, Any] | None = None) -> dict:
    """P4 D1's addressing scheme. Outermost -> innermost.

    No `locator` key: the canonical string is P4's serialization and P5 owns no
    second implementation of it.
    """
    if text_span is not None and time_span is not None:
        raise ValueError("a location carries a text_span or a time_span, not both")
    if region is not None:
        # P4 owns the region shape; this calls P4's rule rather than restating it,
        # because a second copy of a vocabulary is this project's costliest defect.
        # Invoked HERE so a wrong shape fails where the region is made -- it used to
        # surface as `KeyError('w')` during a database write, after every extraction
        # in the scan had already succeeded.
        region_from_mapping(region)
    return {
        "zone": zone,
        "container_path": tuple(container_path),
        "text_span": dict(text_span) if text_span is not None else None,
        "time_span": dict(time_span) if time_span is not None else None,
        "region": dict(region) if region is not None else None,
    }


def observation(*, file_id: str, content_hash: str, extractor_name: str,
                extractor_version: str, source_type: str, raw_value: str,
                location: Mapping[str, Any], observed_at: str, reliability: str,
                normalized_value: str | None = None,
                context_before: str = "", context_after: str = "",
                context_truncated: bool = False, occurrence_count: int = 1,
                confidence: float | None = None,
                signal_tier: int | None = None) -> dict:
    """One row of P4's `evidence`, in P4's field order.

    `raw_value` is exactly the source substring (RAW-1): no case folding, no Unicode
    normalization, no whitespace collapse and no trimming happens here or anywhere
    else in P5.

    An empty `raw_value` is refused HERE, by P4's own `check_non_empty`, and not left
    to the store: a span of empty text used to leave the extractor and die at write
    time, deep in a scan, on a file the extractor had already finished with.
    """
    if reliability not in EXTRACTOR_RELIABILITY:
        raise ForbiddenReliability(
            f"{reliability!r} is a fact-layer state; an extractor may write "
            f"{EXTRACTOR_RELIABILITY} only (P4 D11, conformance rule 3)"
        )
    if occurrence_count < 1:
        raise ValueError("occurrence_count >= 1 (P4 conformance rule 7)")
    if signal_tier is not None and signal_tier not in (1, 2, 3):
        raise ValueError(
            "signal_tier is section 2.6's three-level image hierarchy: 1, 2, 3 or "
            "null (P4 conformance rule 11)"
        )
    row = {
        "file_id": file_id,
        "content_hash": content_hash,
        "extractor_name": extractor_name,
        "extractor_version": extractor_version,
        "source_type": source_type,
        "raw_value": raw_value,
        "normalized_value": normalized_value,
        "location": dict(location),
        "context_before": context_before,
        "context_after": context_after,
        "context_truncated": context_truncated,
        "occurrence_count": occurrence_count,
        "observed_at": observed_at,
        "reliability": reliability,
        "confidence": confidence,
        "signal_tier": signal_tier,
    }
    for name in BUILDER_NON_EMPTY_FIELDS:
        check_non_empty(row[name], name=name)
    return row


def text_unit(*, text: str, container_path: Sequence[Mapping[str, Any]] = (),
              truncated: bool = False) -> dict:
    """One row of P4's `text_units` (D12, G1) - the ONE home for bulk extracted text.

    `container_path: ()` is the whole file (section 2.4). `length` is counted in
    Unicode scalar values (D4), which is what makes RAW-1 checkable for CJK and emoji
    alike.
    """
    return {
        "container_path": tuple(container_path),
        "text": text,
        "length": len(text),
        "truncated": truncated,
    }


def run(*, file_id: str, content_hash: str, extractor_name: str,
        extractor_version: str, source_type: str, analysis_tier: str,
        config: Mapping[str, Any], completeness: str, coverage: Mapping[str, Any],
        observation_count: int, started_at: str, finished_at: str,
        failure_reason: str | None = None) -> dict:
    """One row of P4's `extraction_runs` - THE extraction-outcome record (B1).

    One row per (file version x extractor). P5 publishes no parallel status
    vocabulary of its own: an opaque image runs the image extractor AND OCR, which is
    two rows, and a per-file status cannot say "EXIF read successfully, OCR capped."
    """
    if analysis_tier not in P5_ANALYSIS_TIERS:
        raise ForbiddenAnalysisTier(
            f"P5 writes {P5_ANALYSIS_TIERS}; {analysis_tier!r} is refused. "
            "P8 is the only writer of `llm` (I4)."
        )
    return {
        "file_id": file_id,
        "content_hash": content_hash,
        "extractor_name": extractor_name,
        "extractor_version": extractor_version,
        "source_type": source_type,
        "analysis_tier": analysis_tier,
        "config": dict(config),
        "config_fingerprint": fingerprint(config),
        "completeness": completeness,
        "coverage": dict(coverage),
        "observation_count": observation_count,
        "started_at": started_at,
        "finished_at": finished_at,
        "failure_reason": failure_reason,
    }


def normalize_mechanical(raw: str) -> str:
    """P4 D8 - the four mechanical transforms, and nothing else.

    "Unicode NFC, whitespace collapse, soft-hyphen/line-break repair, and an ISO-8601
    rendering of a timestamp the source stored as a structured date. It may not
    resolve entities, expand abbreviations, or parse a date out of free text."

    Section 2.8's own example is the test: `U Chicago` stays `U Chicago`. Turning it
    into `University of Chicago` is a resolver's job and the resolver is P6's (3.2).
    """
    repaired = raw.replace(_SOFT_HYPHEN, "")
    repaired = _LINE_BREAK_HYPHEN.sub("", repaired)
    return unicodedata.normalize("NFC", " ".join(repaired.split()))


def context_for(text: str, start: int, end: int, *,
                window: int) -> tuple[str, str, bool]:
    """Section 2.8's surrounding context, as P4's three fields (M5).

    `window` is required and has no default: section 8.6 makes the context budget
    configurable and P4 owns the ceiling, so the number is configuration and naming
    one here would be an invented value. Returns
    (context_before, context_after, context_truncated); the flag is set whenever the
    window cut anything, because section 8.6 forbids truncating silently.
    """
    before_available, after_available = text[:start], text[end:]
    before = before_available[-window:] if window else ""
    after = after_available[:window] if window else ""
    truncated = (len(before) < len(before_available)
                 or len(after) < len(after_available))
    return before, after, truncated
