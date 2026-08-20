# src/evidence_shape/vocabulary.py
"""The six closed vocabularies of §2.8's shape, and the questions P4 holds open.

Closed means an extractor may not add a value. D2: "Six extractors then produce
`heading`, `Heading`, `hdg`, `h1` and §3.7's weighting table has no stable key."
Adding a zone or a kind is a P4 contract revision plus a shape-version bump
(segment-kind rule 5), never a local decision inside an extractor.

Every member below is the SPEC's, in the SPEC's order, and each carries a design
citation in the SPEC's own tables. Nothing here is invented.
"""
from __future__ import annotations

from collections.abc import Collection, Mapping
from types import MappingProxyType

#: Bumped when a vocabulary gains a member or the shape gains a field (D2, rule 5).
SHAPE_VERSION = 1

#: §2.2's "document zone". Fifteen places the design names as carrying evidence.
#: P4 publishes the vocabulary; P6 owns what each zone is *worth* (§3.7).
ZONES: tuple[str, ...] = (
    "filename", "path", "metadata", "title", "heading", "body", "table",
    "header_footer", "notes", "link", "annotation", "reference_list",
    "manifest", "ocr", "transcript",
)

#: Addressed by a 1-based index (D3). A label may accompany one and is descriptive
#: only: rule 2 keeps it out of the locator, and rule 3 puts a format's own native
#: address there (a spreadsheet cell is `sheet=2/row=7/column=3`, label "C7").
INDEXED_SEGMENT_KINDS: tuple[str, ...] = (
    "page", "slide", "sheet", "heading", "paragraph", "table", "row", "column",
    "cell", "region", "layer", "artboard",
)

#: Addressed by a label and carrying no index. `field` holds the source format's own
#: slot name verbatim (D7) -- never a product field name, which is P6's `fields`
#: table and which §3.12 forbids creating automatically.
LABEL_SEGMENT_KINDS: tuple[str, ...] = ("field", "entry", "key")

SEGMENT_KINDS: tuple[str, ...] = INDEXED_SEGMENT_KINDS + LABEL_SEGMENT_KINDS

#: §2.9's format families, verbatim (D6). OCR output is `ocr`, never the underlying
#: format -- §2.2 requires "no text layer" and "broken text layer" be
#: distinguishable, and §8.5 requires evaluation decomposed by stage.
SOURCE_TYPES: tuple[str, ...] = (
    "filesystem", "text_document", "spreadsheet", "presentation", "image", "ocr",
    "email", "calendar", "contacts", "code_structured", "audio_video",
    "design_creative", "archive", "opaque_binary",
)

#: §3.13's six, in §3.13's order. The only reliability vocabulary the design defines.
RELIABILITY_STATES: tuple[str, ...] = (
    "user_confirmed", "direct", "validated", "llm_supported", "possible", "rejected",
)

#: D11. An extractor may write two of the six: `direct` for an explicit, labeled,
#: machine-structured slot, `possible` for free text, OCR, a filename or any
#: unlabeled position. The other four are fact-layer outcomes (§3.5) and §2.8
#: forbids extraction from treating model output as proof.
EXTRACTOR_RELIABILITY_STATES: tuple[str, ...] = ("direct", "possible")

#: B1's eight. The single extraction-outcome record's vocabulary; there is no second,
#: per-file status vocabulary anywhere in the system.
COMPLETENESS: tuple[str, ...] = (
    "complete", "capped", "partial", "metadata_only", "deferred", "unsupported",
    "unreadable", "failed", "dataless",
)

#: Conformance rule 9, as M3 relaxed it. `unreadable` and `partial` runs carry the
#: metadata-level rows §2.9's "indexed-but-unreadable" requires. `metadata_only` does
#: not (settled 2026-08-20, matching worked example 19: the stopping extractor emits
#: nothing and the file stays indexed through its `filesystem` observations), and
#: neither does `dataless` (C4) -- nothing was opened, so nothing was seen.
ZERO_OBSERVATION_COMPLETENESS: tuple[str, ...] = (
    "unsupported", "deferred", "failed", "metadata_only", "dataless")

#: I4. P5 writes the first three; P8 is the only writer of `llm`. A fifth is rejected.
ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr", "llm")

#: §2.6's three-level hierarchy for image signals (M2). Null everywhere else.
SIGNAL_TIERS: tuple[int, ...] = (1, 2, 3)

#: §2.7's "locations or bounding boxes where available".
REGION_UNITS: tuple[str, ...] = ("px", "norm")

#: The questions the design leaves unsettled in P4's area. Each blocks or endangers a
#: named neighbouring part, and each is guarded by a test that fails if it is answered
#: in code instead of in a SPEC. OQ1 closed as I4 and is deliberately absent.
#: Closed and therefore ABSENT: OQ1 (I4), OQ2 (content hash owns the observation),
#: OQ3 (C1 — one reliability vocabulary), OQ5 (C3 — users correct facts, never
#: raw_value), OQ6 (C4 — the ninth completeness value is `dataless`). All ratified
#: 2026-08-20. OQ4 alone remains: C2 is P7's to settle before its schema.
#: A closed question is DELETED from this mapping, never left with an answer beside
#: it — an entry here means "still unanswered", and that is what Task 18 reads.
OPEN_QUESTIONS: Mapping[str, str] = MappingProxyType({
    "OQ4": (
        "Is the §8.4 handling class stored per observation or only per file? §8.4 "
        "names no granularity; §8.2's file record carries one sensitivity state, yet "
        "only selected excerpts may reach a cloud model. Which unit does P7 classify?"
    ),
})


class NotInVocabulary(ValueError):
    """A value outside a closed vocabulary. P4 rejects; it never coerces."""


def check(value, vocabulary: Collection, *, name: str):
    """Membership, or a rejection. No case folding, no stripping, no nearest match."""
    if value not in vocabulary:
        raise NotInVocabulary(
            f"{name}={value!r} is not one of {tuple(vocabulary)}; adding a member is "
            "a P4 contract revision and a shape-version bump, not a local decision "
            "inside an extractor (segment-kind rule 5)"
        )
    return value
