# src/recognition/vocabulary.py
"""This package's own closed vocabularies, and the four domains `00` protects.

Closed means a caller may not add a value, on P7's own rule: *"A value outside this
set is a load error, not a fallback."* Nothing here is a threshold and nothing here
is a number that decides an outcome -- the one arity the detector applies is the word
`never_alone` read literally, and it is stated in `detector.py` beside the code that
applies it rather than as a knob here.
"""
from __future__ import annotations

from facts.domains import SCHEMA_IDS, UnknownSchema

#: Bumped when the compiled shape changes. `rules.load_rules` refuses any other
#: value rather than reading an older manifest optimistically: a manifest whose
#: shape has moved is a different rule set, and reading it partially would produce
#: a detector that silently recognises less than its release claims.
MANIFEST_VERSION: int = 1

#: Where a compiled term came from in the node row. Recorded so a later pass can
#: weight the two differently; the detector today counts DISTINCT terms and does not
#: gate on role, because `identity` and `research` authored no context terms at all
#: and a context-required rule would make both unrecognisable.
TERM_ROLES: tuple[str, ...] = ("context", "work_type")

#: Every reason the detector declines to classify. Abstention is a RESULT, so each
#: one is a named value a caller can read, count and act on -- never a bare `None`
#: with the reason lost.
#:
#: `protected_container` is first because it is checked first and because it is the
#: only one that is not about evidence: P3's rule is that an application or system
#: item is never read, and a detector's natural instinct is to open a file to
#: classify it. `needs_llm` is carried but never RETURNED by the deterministic
#: detector -- it rides on the other reasons as the readings P8 would need.
ABSTENTION_REASONS: tuple[str, ...] = (
    "protected_container",
    "no_evidence",
    "no_corroboration",
    "file_kind_implausible",
    "ambiguous",
    "unassigned_handling",
)


class UnknownAbstentionReason(ValueError):
    """A reason outside the closed set. A load error, not a fallback."""


def check_abstention_reason(value: object) -> str:
    if not isinstance(value, str) or value not in ABSTENTION_REASONS:
        raise UnknownAbstentionReason(
            f"{value!r} is not one of the {len(ABSTENTION_REASONS)} reasons this "
            "package defines. Adding one is a contract revision: an abstention "
            "nobody can name is indistinguishable from a detector that did not run."
        )
    return value


#: `00`:52, in `00`'s own order and words: *"Finance, identity, medical, and legal
#: material should be implemented first as safety domains, meaning the system detects
#: and protects them before any cloud or automated placement decision is allowed."*
#: Derived against `SCHEMA_IDS` at import so a widening or a rename there becomes an
#: ImportError here rather than four strings that quietly stop matching.
SAFETY_DOMAIN_IDS: tuple[str, ...] = ("finance", "identity", "medical", "legal")
for _schema_id in SAFETY_DOMAIN_IDS:
    if _schema_id not in SCHEMA_IDS:
        raise UnknownSchema(
            f"{_schema_id!r} is one of `00`:52's four safety domains and is not in "
            f"`facts.domains.SCHEMA_IDS`. The safety domains are the design's, so a "
            "schema roster that has dropped one has broken `00`:52, not this module."
        )
del _schema_id
