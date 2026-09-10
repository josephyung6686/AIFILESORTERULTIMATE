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

from facts.read_surface import is_destination_eligible, proposal_eligible
from llm_harness.records import EvidenceItem
from llm_harness.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR, LEVEL_REQUIRED
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
                found[ref] = _fact_item(ref, row)
    return tuple(found.values())


def _fact_item(ref: str, row) -> EvidenceItem:
    """One proposal-eligible reading, as a reference and never as content.

    Lifted out of `_fact_items` above so the group builder and the per-file builder
    at the foot of this module cannot describe one reading two ways. `location` is
    the FIELD this reading settled, which is what a dimension would be named after.
    Not a path and not a zone: `location` is model-visible and §8.4's always-local
    set includes both.
    """
    return EvidenceItem(
        evidence_ref=ref,
        kind=EXCERPT_KIND,
        location=row["field_key"],
        excerpt_span=None,
        reliability_state=row["reliability_state"],
        basis=DIRECT_ANCHOR,
    )


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
        conn, evidence_refs=tuple(item.evidence_ref for item in facts),
        # `104` R-159: this call's own target, the one named on the request below.
        # `model_target` arrives here as `object` because this builder takes P7's
        # record without reading it; the locality is the one field the release
        # question needs, and taking it from anywhere else would let the rules
        # answer about a destination the bytes are not going to.
        locality=model_target.locality)
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


def file_fits_its_situation(conn: sqlite3.Connection, *, file_id: str,
                            content_hash: str,
                            folder_levels: Sequence[object],
                            group_level_fields: frozenset[str]) -> bool:
    """`00`:97 at the grain of ONE FILE: do this file's accepted facts fit the
    folders the person's situation would build?

    **THE TEST IS THE PRODUCT'S OWN AND IS NOT A THRESHOLD.** No score, no count,
    no bar to tune. Two things make a file not fit, and each is a sentence the
    product already says somewhere else:

    * **a required level with no fact.** The library grades every dimension
      `required` or `optional` in its own words (`FolderLevel.requirement`, read off
      `default_order.dimensions` by `production.folder_levels_for`), and a tree
      cannot be built to its required depth for a file that answers none of them.
      `placement.pipeline` says it one stage later -- "a candidate with an unfilled
      level is struck" -- and this is that sentence asked before a candidate exists.
    * **a fact with no level.** The file states something that would divide a branch
      and the situation has no folder for it. `00`:97's custom template is exactly
      the answer to material an existing template does not express.

    **WHICH LEVELS EACH HALF READS, and both splits are the product's own.** The
    required half reads the levels this deployment ASKS OF A FILE -- `folder_levels`
    minus `group_level_fields`, the split `cli.run` already makes for site A on
    `104` §11.2 step 2 -- because a group-level role is filled from the accepted
    group and no per-file fact ever holds one. Three of the release's 208 situations
    mark a group-level role `required` (`academic.transcripts-credentials`,
    `academic.k12-schooling`, `academic.iep-accommodation-plans`, all of them
    `school`), so reading the required half over the whole list would declare every
    file of those three unfit and buy a template call for each. The second half
    reads the WHOLE list, because a fact naming a group-level field DOES have a
    level in this situation -- the group's.

    **`is_destination_eligible` is what keeps the second half from firing on every
    file**, and it is P6's own column rather than a list written here. §3.8: the
    product "should avoid using authorship or creator identity as a destination
    dimension", so `authored_by` and `our_firm` are never eligible -- and neither is
    any of §3.11's universal set (`file_type`, `creation_date`, `language`,
    `duplicate_family`, `version_family`) or §3.9's `download_session`, none of
    which is ever a folder level in any situation. Without that column the first
    `creation_date` on any file would make it unfit, and every file in every corpus
    would be asked for a template of its own.

    **"Accepted" is `proposal_eligible`**, the same read `_fact_items` offers to the
    group call and the same one P10 uses: §3.6's bar that a weak model output "must
    not quietly become a folder proposal", plus §8.2's replaced conclusions
    excluded. A `possible` reading is not a fact this file HAS for the purpose of
    filling a folder.
    """
    held = {row["field_key"] for row in proposal_eligible(
        conn, file_id=file_id, content_hash=content_hash)}
    asked = tuple(level for level in folder_levels
                  if level.field not in group_level_fields)
    if any(level.requirement == LEVEL_REQUIRED and level.field not in held
           for level in asked):
        return False
    level_fields = {level.field for level in folder_levels}
    return not any(
        field not in level_fields
        and is_destination_eligible(conn, field_key=field)
        for field in sorted(held))


def file_template_request_for(
    conn: sqlite3.Connection, *, file_id: str, content_hash: str,
    plan_version: str, model_target: object, prompt: object,
    max_dossier_tokens: int,
) -> object | None:
    """One reference-only site-E request for ONE FILE, or `None`.

    **`00`:97's other grain, and §5.7 says it in the half of its last sentence the
    group builder above does not quote.** "The user ... either accepts it as a
    one-off structure or saves it as a reusable personal template": a one-off
    structure is a template for material that recurs nowhere, and the smallest
    subject that can hold one is a file. `template_request_for` answers for an
    accepted group whose whole membership fits no recipe; this answers for a file
    whose own accepted facts fit no level of the situation it is under, which
    `file_fits_its_situation` decides above and this builder never re-asks.

    **THE ELIGIBILITY REASON SAYS "accepted group" ABOUT A FILE, AND THAT IS
    RECORDED RATHER THAN QUIETLY FIXED HERE.** `TEMPLATE_ELIGIBILITY` is P8's closed
    set for this site, it has exactly one member, and `tests/p8/test_p8_vocabulary.
    py` pins the tuple by equality -- so a truthful per-file word is a P8
    controlled-vocabulary widening and is the owner's, exactly as
    `privacy.denial.deny_protected_records_template` records a tenth denial reason
    as owed rather than minting it. The STATE the word names -- "fits no existing
    template" -- is true of this subject; the noun is not, it is model-visible
    (`dossier._FRAME_KEYS` carries `eligibility_reason`), and the candidate word is
    with the owner.

    `None` when the file's accepted facts cite nothing P7 may release, which is a
    real state and not an error: a template designed from no evidence would be
    `00`:97's "cannot invent unsupported facts" at the one site whose whole output
    is structure. Every span refusal `releasable_excerpts` applies at site C applies
    here -- the filename and the path are the most tempting evidence about how a
    person's folders should be shaped and are the one thing that may never leave the
    device.
    """
    import json

    from llm_harness.fingerprint import prompt_fingerprint

    found: dict[str, EvidenceItem] = {}
    for row in proposal_eligible(conn, file_id=file_id,
                                 content_hash=content_hash):
        try:
            refs = json.loads(row["evidence_refs"] or "[]")
        except ValueError:
            continue
        for ref in refs:
            if isinstance(ref, str) and ref not in found:
                found[ref] = _fact_item(ref, row)
    requested = releasable_excerpts(
        conn, evidence_refs=tuple(found), locality=model_target.locality)
    if not requested:
        return None
    releasable = {item.observation_key for item in requested}
    items = tuple(item for ref, item in found.items() if ref in releasable)
    return build_template_request(
        subject_ref=file_id,
        plan_version=plan_version,
        evidence_items=items,
        conflicts=(),
        model_call_request=ModelCallRequest(
            stage=TEMPLATE_STAGE,
            # ONE FILE, named as a file. `Target.group_id` is what a release about
            # SEVERAL files at once is addressed by, and there is no group here: the
            # subject is the file, and a group id would make the audit row claim a
            # membership P9 never accepted.
            target=Target(file_ids=(file_id,)),
            model_target=model_target,
            requested_items=requested,
            prompt_template_id=prompt.template_id,
            prompt_fingerprint=prompt_fingerprint(prompt),
            max_dossier_tokens=max_dossier_tokens),
    )
