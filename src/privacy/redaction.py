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

    A region without a text span, or a time span, raises. `serialize_locator`
    drops a region, so a box-only locator would silently address the whole page.
    A location that already has a text span is addressable; the box is C3, the
    span is not.
    """
    if location.region is not None and location.text_span is None:
        raise RegionOriginUnspecified(
            f"{serialize_locator(location)} carries a bounding box "
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
