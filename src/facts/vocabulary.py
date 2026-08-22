# src/facts/vocabulary.py
"""P6's own closed vocabularies, published once, checked through P4's `check`.

Global constraint: "`unresolved` reasons and `origin` values are P6's own closed
vocabularies, published once, in one module, checked with P4's
`evidence_shape.vocabulary.check(value, vocabulary, *, name)` so a bad value raises
`NotInVocabulary` rather than being stored."

The six reliability states are NOT here — they are P4's, re-exported by
`facts.states`, and a second copy is what preamble rule 2 forbids.

Task 5 adds `UNRESOLVED_REASONS` and `ATTEMPTED_PRODUCERS` to this module.
"""
from __future__ import annotations

#: §3.11's six domain families plus the universal scope. Exactly the SPEC's list, in
#: the SPEC's order. Adding a member is a contract revision: §3.15 names Career and
#: recruiting, identity, medical and legal, and §3.11 gives them no field row, so
#: they are Deferred rather than empty scopes (S3).
FIELD_SCOPES: tuple[str, ...] = (
    "universal",
    "academic",
    "college_applications",
    "research",
    "finance",
    "photos",
    "code",
)

#: How a field's values normalize (SPEC, `fields` table). Exactly the four kinds
#: `planning/domains/canonical_fields.json` uses; P6 invents no fifth.
#:
#: The SPEC's column comment adds "date/term fields must use §3.10 rules", but that
#: file types `term` as `string`. Rather than mint a `term` kind the design does not
#: name, the §3.10 obligation stays in `facts.dates`, keyed on the field, with its
#: injected patterns. The gap is named in the plan, not closed here.
VALUE_KINDS: tuple[str, ...] = ("string", "date", "identifier", "enum")
