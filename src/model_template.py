# src/model_template.py
"""Site E's live caller. `104` §7's packet G12, closed.

**What G12 says, in full.** *"E: No live caller: `routing.py`'s C3 refusal never
becomes an E request (`103` §28 table). E can be ratified and stay inert; the
bakeoff is the only exercise it gets."* Every other half of site E already exists:
`tree_design.template_schema` builds the request (`build_template_request`) and the
two authorities (`template_dependencies`), `llm_harness.sites` dispatches to
`validate_template_response`, and the library holds a drafted text, a response
schema and a shaping policy. What nothing did was ASK.

**Why the C3 refusal is the trigger and not a choice made here.** C3 is the gate
that refuses to widen "to every row sharing a schema", and its message is the one
place the product says *"no recipe recognises the situation these files are in"*.
`00`:97's site E is exactly the answer to that sentence: a branch whose material no
shipped template covers is the branch a template has to be DESIGNED for.
`ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE` is P8's own controlled eligibility
reason and it says the same thing in P8's words, so the trigger is read off the
refusal rather than invented.

**One request per accepted group, and that is the eligibility reason's own grain.**
"An accepted group fits no existing template" is a claim about ONE group; a request
covering a branch would be a claim about several and would name a subject P8's
`subject_ref` has no shape for.

**Observe-only, unconditionally, and this site is the one where that is not a
temporary state.** B, C and D withhold their answers while their text is a draft
and begin applying the day the owner ratifies it. E does not: `00`:97 ends with
"valid shape is not activation -- the person reviews, edits and accepts or
discards", and the canvas that review happens on is Release 2 (`104` §13.3). So the
answer is recorded and applied to nothing whatever the prompt's status says, and
the sentence saying so is here rather than in a lever somebody could move.

Nothing here authors a template, a dimension, a label or a level. It reads the
group P9 accepted, offers P7 the excerpts that group's anchors already cite, and
hands P8 the two authorities P10 published.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence

from facts.read_surface import proposal_eligible
from llm_harness.records import EvidenceItem
from llm_harness.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR
from model_placement import releasable_excerpts
from privacy.release import ModelCallRequest, Target
from tree_design.template_schema import build_template_request

#: P8's stage name for a template call, and the `ModelCallRequest.stage` §8.4's
#: audit record carries. `model_facts` spells `fact_interpretation`, `p8_seam`
#: `group_interpretation` and `model_placement` `placement_interpretation`; this is
#: the fourth and it is spelled once.
TEMPLATE_STAGE: str = "template_interpretation"

#: The `EvidenceItem.kind` a group member arrives under, and P9's word for it at
#: site B. One spelling for one concept across two sites: a second word here would
#: describe the same reference twice.
MEMBER_KIND: str = "member"

#: And the kind a cited reading arrives under. Same argument.
EXCERPT_KIND: str = "excerpt"


def _member_items(members: Sequence[object]) -> tuple[EvidenceItem, ...]:
    """Every member of the group, as a reference and never as content.

    `basis` is P9's own membership basis carried through, because "this file
    states the group's basis" and "this file was retrieved into the group" are
    different claims and a template designed from them should be able to tell
    them apart.
    """
    return tuple(
        EvidenceItem(
            evidence_ref=member.file_id,
            kind=MEMBER_KIND,
            location=member.basis,
            excerpt_span=None,
            reliability_state=(
                "direct" if member.basis == DIRECT_ANCHOR else "possible"),
            basis=(DIRECT_ANCHOR if member.basis == DIRECT_ANCHOR
                   else CONTEXT_SUPPORTED),
        )
        for member in members
    )


def _fact_items(conn: sqlite3.Connection,
                members: Sequence[object]) -> tuple[EvidenceItem, ...]:
    """The readings a template's dimensions may cite. `00`:97's E-R4.

    **The group's ANCHORS and not every member**, which is the same rule the group
    dossier applies at site B: a context-supported member is in the group because
    something retrieved it, and a dimension justified by what it happens to say is
    a level built on a retrieval guess.

    **Proposal-eligible only**, which is `00`:42's bar: a template dimension is a
    folder proposal by definition, and a weak reading "must not quietly become
    one". The read is `read_surface.proposal_eligible`, the same one P10 uses.

    Deduplicated on the observation key, because two members citing one reading
    are one reading and P7 is asked for it once.
    """
    import json

    found: dict[str, EvidenceItem] = {}
    for member in members:
        if member.basis != DIRECT_ANCHOR:
            continue
        for row in proposal_eligible(conn, file_id=member.file_id,
                                     content_hash=member.content_hash):
            try:
                refs = json.loads(row["evidence_refs"] or "[]")
            except ValueError:
                continue
            for ref in refs:
                if not isinstance(ref, str) or ref in found:
                    continue
                found[ref] = EvidenceItem(
                    evidence_ref=ref,
                    kind=EXCERPT_KIND,
                    # The FIELD this reading settled, which is what a dimension
                    # would be named after. Not a path and not a zone: `location`
                    # is model-visible and §8.4's always-local set includes both.
                    location=row["field_key"],
                    excerpt_span=None,
                    reliability_state=row["reliability_state"],
                    basis=DIRECT_ANCHOR,
                )
    return tuple(found.values())


def template_request_for(
    conn: sqlite3.Connection, *, group: object, plan_version: str,
    model_target: object, prompt: object, max_dossier_tokens: int,
) -> object | None:
    """One reference-only site-E request for one accepted group, or `None`.

    `None` when the group's anchors cite nothing P7 may release, which is a real
    state and not an error: a template designed from no evidence would be
    `00`:97's "cannot invent unsupported facts" happening at the one site whose
    whole output is structure.

    Every span refusal `releasable_excerpts` applies at site C applies here for
    the same reasons -- the filename and the path are the most tempting evidence
    about how a person's folders should be shaped and are the one thing that may
    never leave the device.
    """
    from llm_harness.fingerprint import prompt_fingerprint

    members = tuple(group.members)
    facts = _fact_items(conn, members)
    requested = releasable_excerpts(
        conn, evidence_refs=tuple(item.evidence_ref for item in facts))
    if not requested:
        return None
    releasable = {item.observation_key for item in requested}
    items = _member_items(members) + tuple(
        item for item in facts if item.evidence_ref in releasable)
    return build_template_request(
        subject_ref=group.group_id,
        plan_version=plan_version,
        evidence_items=items,
        conflicts=(),
        model_call_request=ModelCallRequest(
            stage=TEMPLATE_STAGE,
            # THE GROUP, named as a group. `Target.group_id` is what a release
            # about several files at once is addressed by, and the file ids are
            # the members whose readings are being asked for.
            target=Target(file_ids=tuple(m.file_id for m in members),
                          group_id=group.group_id),
            model_target=model_target,
            requested_items=requested,
            prompt_template_id=prompt.template_id,
            prompt_fingerprint=prompt_fingerprint(prompt),
            max_dossier_tokens=max_dossier_tokens),
    )
