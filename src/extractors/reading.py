# src/extractors/reading.py
"""The shapes P5's injected format readers return.

P5 adds no third-party runtime dependency: real PDF, DOCX, HEIC, archive and OCR
reading cannot be done in the standard library, so every format-specific reader is a
caller-supplied callable and these are the shapes it hands back. A deterministic
fixture reader in tests/p5/ implements each one; a real library implements the same
shape without changing an observation, a run or a text unit.

These are P5's own input types. They are NOT P4 records and never reach the sink.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    """A labelled stretch of a unit's text.

    `zone` is one of P4's fifteen: the reader says WHAT KIND OF PLACE this is,
    because that is library knowledge (a heading style, a table cell, a footer). Only
    `heading` also carries an address - P4's segment kinds include `heading` and
    include no `body` and no `reference_list`, because those are zones, not addresses
    (P4 D2: "The zone answers what kind of place; the container path answers which
    one").
    """
    zone: str
    start: int
    end: int
    ordinal: int | None = None
    label: str | None = None


@dataclass(frozen=True)
class StructuredString:
    """One of section 2.2's "URLs, email addresses, DOI values, citations,
    identifiers, and other structured strings".

    `kind` uses section 2.2's own words. The PATTERNS are Deferred - the SPEC's
    Deferred table says DOI is named and citations and identifiers are named as
    classes, but "The patterns" are not settled - so no pattern lives in
    src/extractors/ and the finder is supplied by the caller.
    """
    kind: str
    start: int
    end: int


#: Which of P4's zones a found string belongs to when its kind implies one.
#: P4's zone table: "`link` - a URL, email address, DOI or hyperlink";
#: "`reference_list` - a citation / reference list", citing section 2.2's "a
#: reference list on page eighteen". A kind not listed here takes the zone of the
#: region it was found in, because section 2.2 names the class and the region says
#: where it sits.
ZONE_BY_STRUCTURED_KIND: dict[str, str] = {
    "url": "link",
    "email": "link",
    "doi": "link",
    "citation": "reference_list",
}
