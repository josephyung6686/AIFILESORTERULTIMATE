# src/grouping/naming.py
"""What the ENGINE can say about a group without asking anything.

`00` §4.5 gives the model four tasks and makes the fourth conditional on the
first: "only if coherence is supported, it proposes a concise human-readable
display label and a group category". P9's SPEC keeps the same shape and adds the
other two authors — `label_source ∈ engine | llm-proposed | user-edited`. This
module is the FIRST of those three, and it is the only one a deterministic
deployment has: `src/cli.py` runs with `p8_run_call=None`, so if the engine says
nothing about a group, nothing does.

Three answers, each derived from the group's own record and from P6's published
catalogue. Nothing here reads a file, opens a container or asks a model.

**The verdict.** §4.9's minimum-independent-anchor bar is a COUNT over facts P6
already validated, and `graph.meets_support_bar` has already applied it —
`Group.state == supported` is its answer. A group at that bar is one whose files
independently state the same validated fact, and saying so is reporting a rule
computation, not synthesising a judgement. A group BELOW it stays `candidate`
and this module writes nothing at all about it: that is the SPEC's third row —
"the group stays `candidate` with its anchor memberships intact and **no**
`coherence_verdict` and **no** `display_label`" — and it is what a deployment
with no model honestly has to show.

**The category.** M12 settled that `group_category` is the DOMAIN vocabulary and
not a second enum, so the value must be one of `facts.domains.SCHEMA_IDS` and is
never spelled here. `_SCHEMAS_BY_FIELD` is inverted from P6's own
`schema_fields`, so a schema added or a field moved upstream moves this with it.

**`None` is a real answer and it is the common one.** Seventeen of P6's field
keys are referenced by more than one schema — `project` by eight, `record_type`
by seven — and six more are universal and referenced by none. A group anchored on
one of those does not name a domain, and this module says `None` rather than
picking the first plausible schema. That matters more than the positive half: a
group with `domain=None` reaches P10 as a branch candidate that no applicability
row claims, which the user can see and act on, while a group with a CONFIDENT
WRONG domain files their matters into their coursework.

**Three of the twenty-three can never be derived, and that is right.**
`identity`, `medical` and `legal` are §3.15's safety domains and P6 declares no
field at all for them, so no anchor fact can point at one and the engine returns
`None` for a group of passports. P9 is not the part that decides a file is
identity material -- P7 is, and it says so through `sensitivity_state` and the
handling class, which travel beside the group and are what keep a protected
container marked, counted and unopened. A `group_category` of `identity` invented
here would be a second, weaker claim about the same thing.

**The label is the user's own words.** §5.1: the labels "should reflect the
user's vocabulary rather than a universal corporate taxonomy", and §5.7 is
blunter — "The system does not invent PHYS1401, UChicago, Spring 2026, or
PVA/RDP; those names emerge from validated facts, user-confirmed groups, and
accepted labels." So the engine's label is the anchor VALUES themselves, joined,
and it contains no word this file authored. A user-edited label is plan-versioned
and lives on `group_acceptance`; this one is what was edited.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from types import MappingProxyType

from facts.domains import SCHEMA_IDS, schema_fields

from grouping.records import AnchorFact, Group
from grouping.vocabulary import COHERENT, ENGINE, SUPPORTED

#: §4.5's own examples pair two values with an em dash — `PHYS1401 — Spring 2026`,
#: `Columbia Application — 2026 Cycle`. The separator is the only character in a
#: label this file contributes.
LABEL_JOIN: str = " — "

#: Which schemas REFERENCE each field key, inverted from P6's `schema_fields`
#: rather than written down. A field referenced by one schema names it; a field
#: referenced by several names none of them on its own; a universal field is
#: absent here entirely and names none.
_SCHEMAS_BY_FIELD = MappingProxyType({
    field_key: frozenset(
        schema_id for schema_id in SCHEMA_IDS
        if field_key in schema_fields(schema_id)
    )
    for schema_id in SCHEMA_IDS
    for field_key in schema_fields(schema_id)
})


def schemas_referencing(field_key: str) -> frozenset[str]:
    """Every recognised schema whose field set names `field_key`.

    Empty for a universal or structural key — `duplicate_family`, `capture_date`'s
    universal siblings, anything P6 declares outside a domain. Empty is the
    honest answer for those: they are true of files in every domain and single
    out none.
    """
    return _SCHEMAS_BY_FIELD.get(field_key, frozenset())


def domain_for(anchor_facts: Sequence[AnchorFact]) -> str | None:
    """The ONE domain every anchor fact belongs to, or `None`.

    An INTERSECTION, not a vote and not a first match. A group anchored on
    `school` (academic alone) and `work_type` (academic, career, law_practice,
    construction_property) is academic, because that is the only reading both
    facts allow. A group anchored on `school` and `employer` is two lives at once
    and this returns `None` — §3.11's "activation adds; it never chooses" applies
    to a group as much as to a file, and there is no tie here to break.
    """
    surviving: frozenset[str] | None = None
    for fact in anchor_facts:
        owners = schemas_referencing(fact.field)
        surviving = owners if surviving is None else (surviving & owners)
        if not surviving:
            return None
    if surviving is None or len(surviving) != 1:
        return None
    return next(iter(surviving))


def label_for(anchor_facts: Sequence[AnchorFact]) -> str | None:
    """The anchor values, deduplicated, in the order the facts carry them.

    `None` when no anchor fact states a value, which is the same condition that
    leaves a group with nothing to be coherent ABOUT.
    """
    values = [fact.value for fact in anchor_facts if fact.value]
    return LABEL_JOIN.join(dict.fromkeys(values)) or None


def engine_proposal(group: Group) -> Group:
    """`group`, with the engine's own verdict, label and category filled in.

    Returns the group UNCHANGED whenever the engine has nothing to say — below
    §4.9's bar, or with no anchor fact naming a value — so an unlabelled group
    stays a real, expressible state rather than acquiring a name by default.

    The two halves cannot come apart: a verdict is written only together with the
    label derived from the same facts, so `coherence_verdict == coherent` from
    this path always carries a name P10 can put on a branch. The category may
    still be `None` beside it, and that pairing is deliberate — a coherent group
    whose facts do not name one domain is nameable and unroutable, which is
    exactly what it is.
    """
    if group.state != SUPPORTED:
        return group
    label = label_for(group.anchor_facts)
    if label is None:
        return group
    return dataclasses.replace(
        group,
        coherence_verdict=COHERENT,
        coherence_citations=tuple(dict.fromkeys(
            fact.observation_key for fact in group.anchor_facts
            if fact.observation_key)),
        group_category=domain_for(group.anchor_facts),
        display_label=label,
        label_source=ENGINE,
    )
