"""Sites C/D placement and residual validation.

Tree/policy oracles are required injections with no defaults. The residual
controlled-action set is P8's Task 1 `RESIDUAL_ACTIONS`.

Site C's decision rule is the owner's of 7 Sep 2026 (`105` §14.1): the unique
fully supported destination after resolving ancestors and shared branches.
`support` and `next_support` are recorded diagnostics and never a veto; a level
marked `context` is verified against the dossier's accepted groups; a placement
every level of which is `context` may carry no citation at all.

**Site C rejects on three things and flags the rest** (`104` §18.2 gap 2, under
`00`'s amendment of 2026-09-05: "deterministic validation rejects only a
structurally invalid answer"). The three are the frozen tree (`node_exists`),
grounding (a level whose value the file's own released text does not state, and a
`context` level whose group the dossier does not say the person accepted), and
shape (a required key absent or not a number) -- plus the person's own privacy
policy, which is theirs and not this module's opinion. Everything else --
a destination P11's shortlist did not happen to contain, an unechoed conflict id,
a generic hub, a placement with no supported level, a populated `alternatives`
list -- is recorded on the verdict and sent to a person by `requires_review`.
See `_flagged`.
"""
from __future__ import annotations

import dataclasses
import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from database_agent.db import transaction
from llm_harness.records import CheckedCitation, Dossier, P8Verdict, ValidationUnavailable
from llm_harness.store import record_verdict, supersede_verdict
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    ACTION_NOT_IN_CONTROLLED_SET,
    BELOW_SUPPORT_THRESHOLD,
    C_PLACEMENT,
    CHOOSE_BROAD_PARENT,
    CHOOSE_RESIDUAL_DESTINATION,
    CONFLICT_IGNORED,
    D_RESIDUAL,
    DESTINATION_NOT_IN_FROZEN_TREE,
    EVIDENCE_NOT_IN_FILE_RECORD,
    GENERIC_HUB_ONLY,
    INSUFFICIENT_MARGIN,
    WEAK_RETRIEVAL_REPORTED,
    INVENTED_DATE,
    INVENTED_FOLDER,
    INVENTED_INSTITUTION,
    INVENTED_NODE,
    INVENTED_PROJECT,
    LEAVE_IN_CURRENT_LOCATION,
    LEAVE_IN_PLACE,
    MARK_PROTECTED_OR_UNSUPPORTED,
    MARK_REVIEW_LATER,
    MOVE_PLAN_ELIGIBLE,
    NO_DESTINATION,
    NO_SUPPORTED_DESTINATION,
    NODE_NOT_IN_FROZEN_TREE,
    REJECT,
    REJECTED,
    RESIDUAL_ACTIONS,
    RESIDUAL_DESTINATION,
    RESIDUAL_DESTINATION_REVIEW,
    RETURN_ACCEPTED_PACKET,
    RETURN_CONFIRMED_GROUP,
    RETURN_TO_PLACEMENT,
    REVIEW_LATER,
    SCHEMA_INVALID,
    SENSITIVITY_POLICY_VIOLATION,
    SENSITIVITY_RESTRICTION_IGNORED,
    SLOT_FILLED_WITHOUT_EVIDENCE,
    STRONGER_RELATIONSHIP_OVERLOOKED,
    UNRESOLVED,
    VALID_REVIEW_REQUIRED,
    WEAK,
)
from llm_harness.wire_handles import issued_conflict_handles, local_ref

_TARGET_ACTIONS = frozenset({
    RETURN_CONFIRMED_GROUP,
    RETURN_ACCEPTED_PACKET,
    CHOOSE_RESIDUAL_DESTINATION,
    CHOOSE_BROAD_PARENT,
})

_IDENTITY_DDL = """
CREATE TABLE IF NOT EXISTS llm_cd_plan_identity (
    verdict_id TEXT PRIMARY KEY,
    plan_version TEXT NOT NULL,
    evidence_snapshot_id TEXT NOT NULL
);
"""


@dataclass(frozen=True, slots=True)
class PlacementDependencies:
    """Site C's authorities.

    `support_threshold` and `margin_predicate` are still required injections --
    the composition root supplies them and the seam tests name them -- but since
    `105` §14.1 neither is consulted: the two counts the model writes are
    recorded, not compared. The two codes they used to raise now mean something
    the validator can observe (`_placement_site`).
    """

    node_exists: Callable[[str, str], bool]
    support_threshold: object
    margin_predicate: Callable[[object, object], bool]
    sensitivity_policy: Callable[[Dossier, Mapping[str, object]], bool]


@dataclass(frozen=True, slots=True)
class ResidualDependencies:
    node_exists: Callable[[str, str], bool]
    sensitivity_policy: Callable[[Dossier, Mapping[str, object]], bool]
    approved_target_ids: tuple[str, ...]


def _payload_of(raw: object) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        return {}
    payload = raw.get("payload")
    if isinstance(payload, Mapping):
        return payload
    return {}


def _rewrite(
    verdict: P8Verdict,
    *,
    outcome: str | None = None,
    disposition: str | None = None,
    reasons: tuple[str, ...] | None = None,
    may_propose: bool | None = None,
    requires_review: bool | None = None,
    verdict_id: str | None = None,
    plan_version: str | None = None,
) -> P8Verdict:
    new_outcome = verdict.outcome if outcome is None else outcome
    new_review = verdict.requires_review if requires_review is None else requires_review
    if new_outcome == ACCEPT_CONTEXT_SUPPORTED:
        new_review = True
    new_propose = verdict.may_propose if may_propose is None else may_propose
    if new_outcome == WEAK:
        new_propose = False
    return dataclasses.replace(
        verdict,
        verdict_id=verdict.verdict_id if verdict_id is None else verdict_id,
        outcome=new_outcome,
        disposition=verdict.disposition if disposition is None else disposition,
        reasons=verdict.reasons if reasons is None else reasons,
        may_propose=new_propose,
        requires_review=new_review,
        plan_version=verdict.plan_version if plan_version is None else plan_version,
    )


def _reject(verdict: P8Verdict, reason: str, disposition: str) -> P8Verdict:
    return _rewrite(
        verdict,
        outcome=REJECT,
        disposition=disposition,
        reasons=(reason,),
        may_propose=False,
        requires_review=False,
    )


def _flagged(verdict: P8Verdict, reasons: tuple[str, ...]) -> P8Verdict | None:
    """`104` §18.2 gap 2: what a NON-structural check does instead of rejecting.

    `00`'s amendment of 2026-09-05 is one sentence and it is the whole of this
    function's argument: "deterministic scores rank and shortlist the candidates
    the model is shown, and deterministic validation REJECTS ONLY A STRUCTURALLY
    INVALID ANSWER: a node that is not in the frozen tree, or a cited fact that is
    not in the evidence." Everything a site check asks that is neither of those is
    an opinion about the answer's QUALITY, and an opinion held by code that saw
    less of the file than the model did.

    So the answer survives, keeps its outcome, and carries the reason to the
    person: `requires_review` is set, `_placement_disposition` turns that into
    `valid_review_required`, and `p8_seam.transcribe` -- which already reads
    `requires_review` to gate `review_policy` and not the outcome -- puts the file
    in front of somebody with the code beside it. Nothing auto-moves on a flagged
    verdict, which is the property the six rejections were really buying.

    **The reasons accumulate.** A rejection could return at the first thing it
    found because the answer was over; a flag cannot, or a placement with three
    things worth telling the person would tell them one. `reasons` is appended to
    whatever the claim-level validator already recorded, in the order the checks
    ask, so the histogram counts each check once per verdict it fired on.

    `None` when nothing was flagged, because that is `_placement_site`'s own
    contract for "this site has no objection" and a verdict rewritten with no
    change is a rewrite a reader has to check for.
    """
    if not reasons:
        return None
    return _rewrite(
        verdict,
        reasons=verdict.reasons + reasons,
        requires_review=True,
    )


def _missing_placement(dependencies: PlacementDependencies | None) -> tuple[str, ...]:
    names = (
        "node_exists", "support_threshold", "margin_predicate", "sensitivity_policy",
    )
    if dependencies is None:
        return names
    missing = [name for name in names if getattr(dependencies, name) is None]
    return tuple(missing)


def _missing_residual(dependencies: ResidualDependencies | None) -> tuple[str, ...]:
    names = ("node_exists", "sensitivity_policy", "approved_target_ids")
    if dependencies is None:
        return names
    missing = [name for name in names if getattr(dependencies, name) is None]
    return tuple(missing)


def _dimensions(payload: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    raw = payload.get("per_dimension_support")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ()
    return tuple(item for item in raw if isinstance(item, Mapping))


def _real_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


#: The three levels `00`:114 names when it says the validator checks "that the
#: model did not invent a date, institution, project, or node". The node is the
#: destination and is checked above; these three are levels of the path.
_DIMENSION_REASON: Mapping[str, str] = {
    "date": INVENTED_DATE,
    "institution": INVENTED_INSTITUTION,
    "project": INVENTED_PROJECT,
}


def _stated_by_the_file(value: object, dossier: Dossier) -> bool:
    """Whether the file's OWN released evidence says this.

    The same predicate `validation._check_citation` uses, and deliberately the
    same source: a cited span is matched against `ReleasedEvidence.value` and
    nothing else, because that is what the model was shown. Matching a level's
    value against the store instead would accept a value the model could not
    have read and reject the one it did.
    """
    if not isinstance(value, str) or not value:
        return False
    return any(value in item.value for item in dossier.released_evidence)


def _invented_dimension(payload: Mapping[str, object], dossier: Dossier) -> str | None:
    """GROUNDING, which is what `104` §13.6 makes the hard check.

    **R-15, and it was not hypothetical.** This compared a level's VALUE against
    `dossier.allowed_vocabulary`, which at site C is the list of legal NODE IDS.
    A node id is not a value and a value is not a node id, so the first real
    `project`, `institution` or `date` a model reported was rejected as invented
    the day C was wired -- and the only way a fixture could pass was to put
    values into the node-id list, which `_C_VOCAB` did until this landed.

    **Every level except a `context` one.** A `context` level's value comes from
    the accepted group the file belongs to rather than from its own text
    (`00`:111, the C draft's rule 3), and the dossier carries no group values to
    ground it against (packet §7 G3: the live C dossier has no node profiles and
    no accepted-group items). Grounding one against the FILE's evidence would
    re-create R-15 one step over -- every context-supported level rejected as
    invented -- so the check does not fire on one, and `00`:111's own example is
    the reason: `HW 3.pdf` is placed under a course it never names.

    That exemption is written as "everything but `context`" rather than "only
    `direct`" ON PURPOSE. `support` has two legal words and the response schema
    enumerates them; a THIRD word is a malformed answer, and a check that
    grounded only the word it recognised would let any unrecognised one through
    ungrounded -- fail-open on exactly the input that is already wrong. The
    model's own "unsupported" keeps its more precise reason because
    `SLOT_FILLED_WITHOUT_EVIDENCE` is asked first, above.

    **The schema half of §13.6 has no channel at C, and is not faked here.** At
    site A the schema check is real: the dossier's vocabulary IS the domain's
    field keys, so "the field exists" is a lookup. At C the dimensions a model
    may name are the frozen tree's own levels; `Dossier.folder_levels` is empty
    at C by design ("empty at B, C and D, which design no tree") and
    `allowed_vocabulary` is node ids, so nothing in the dossier says which levels
    exist. The response schema constrains `dimension` to a non-empty string and
    `SCHEMA_INVALID` carries that much. Naming the levels is the node-profile
    change R-17 makes; a check invented here would be a rule guessing at the
    tree.

    **WHAT THAT MISSING CHANNEL IS AND IS NOT AN EXCUSE FOR (`104` R-77).** It
    excuses the SCHEMA half -- "this level does not exist in the tree" cannot be
    asked without a list of the tree's levels, and R-17's node profiles reach the
    dossier as one free-text `location` string per candidate
    (`placement/index.py`'s `node_profile`), which is prose and not an
    enumeration, so the list still is not here. It never excused the GROUNDING
    half, which asks only whether the file's own released text states the value
    and needs no list at all. Those two were tangled: the grounding loop reached
    for `_DIMENSION_REASON` to get a reason code and treated a miss as "not my
    business", so an unrecognised level name skipped the check that did not
    depend on recognising it. Untangled above. The schema half stays owed and
    stays outside this module: it wants `Dossier.folder_levels` filled at C
    (`model_placement.py`:448 sets `()` for C and D alike) or a node-profile
    field that names the levels, either of which is a change to what the dossier
    carries and not a check this file may invent.
    """
    for item in _dimensions(payload):
        if item.get("support") == "context":
            continue
        if _stated_by_the_file(item.get("value"), dossier):
            continue
        # `104` R-77. EVERY non-`context` LEVEL IS GROUNDED, AND THE THREE NAMED
        # ONES ONLY GET A MORE PRECISE WORD FOR IT. This used to read
        # `reason = _DIMENSION_REASON.get(...)` / `if reason is None: continue`,
        # so a level named anything but `date`, `institution` or `project` was
        # skipped BEFORE it was grounded -- and `dimension` is `{"type": "string",
        # "minLength": 1}` in the wired C schema, so any word at all reached that
        # skip. A model that answered `{"dimension": "course", "value": "Advanced
        # Sculpture", "support": "direct"}` about a file whose text says neither
        # was admitted, while the same invention spelled `project` was rejected.
        # The name the model chose decided whether its evidence was checked.
        #
        # `00`:114's sentence is about the four things a model must not invent,
        # not about a vocabulary of level names, and §13.6 makes GROUNDING the
        # hard check. So grounding runs on the level, and `_DIMENSION_REASON` is
        # what it is called -- a lookup for the report, not a gate on the check.
        # `SLOT_FILLED_WITHOUT_EVIDENCE` is the fallback because that is already
        # C's code for a slot filled with something the file does not state (it
        # is what the model's own `unsupported` and an unverifiable `context`
        # level both get, above), and because naming a new code here would be a
        # closed-vocabulary addition.
        return _DIMENSION_REASON.get(item.get("dimension"),
                                     SLOT_FILLED_WITHOUT_EVIDENCE)
    return None


#: An `accepted_group` evidence item in this reliability state is a group the
#: person accepted the file into. Any other state (`possible` is the bench's) is
#: a group the file was merely retrieved as a candidate member of, which `00`:109
#: and `105` §14.1 say is a resemblance and not support.
ACCEPTED_MEMBERSHIP_STATE: str = "user_confirmed"
ACCEPTED_GROUP_KIND: str = "accepted_group"
#: The per-level key a `context` level names its group in (schema v2).
CONTEXT_GROUP_KEY: str = "context_group"


def _accepted_groups(dossier: Dossier) -> frozenset[str]:
    return frozenset(
        item.evidence_ref for item in dossier.evidence_items
        if item.kind == ACCEPTED_GROUP_KIND
        and item.reliability_state == ACCEPTED_MEMBERSHIP_STATE
    )


def _unverified_context_level(payload: Mapping[str, object], dossier: Dossier) -> bool:
    """A `context` level whose group support the validator cannot verify.

    `105` §14.1 allows accepted-group support without a file citation ONLY when
    it is verifiable: the level names the group (`context_group`), and that group
    is one the dossier says the person accepted the file into. A level that names
    no group, a group the dossier does not carry, or a group the file was merely
    retrieved for is a slot filled on evidence the validator cannot see.
    """
    accepted = _accepted_groups(dossier)
    for item in _dimensions(payload):
        if item.get("support") != "context":
            continue
        group = item.get(CONTEXT_GROUP_KEY)
        if not isinstance(group, str) or group not in accepted:
            return True
    return False


def _context_only_claim(dossier: Dossier, raw: object) -> str | None:
    """`validation.validate_response`'s `uncited_claim` hook for site C.

    A placement whose every listed level is `context` has nothing in the file's
    text to cite and is admitted with no citations, as `accept_context_supported`
    (review required, `00`:111). Whether the groups it leans on are ones the
    person accepted is `_placement_site`'s check, not this one's: this only says
    the SHAPE may proceed. Anything else without a citation stays uncited.
    """
    payload = _payload_of(raw)
    destination = payload.get("destination")
    if destination in (None, "none"):
        return None
    levels = _dimensions(payload)
    if not levels or any(item.get("support") != "context" for item in levels):
        return None
    return ACCEPT_CONTEXT_SUPPORTED


def _alternatives(payload: Mapping[str, object]) -> tuple[object, ...]:
    raw = payload.get("alternatives")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ()
    return tuple(raw)


def _considered_conflicts(
    payload: Mapping[str, object],
    field: str,
    *,
    handles: Mapping[str, str],
) -> set[str]:
    """The LOCAL conflict ids the model's `field` list names.

    `dossier._body` shows the model a keyed handle of every `conflict_id` and
    never the id, so a list of the handles it was shown is what comes back. Both
    checks below hold `dossier.conflicts`, whose ids are local, and the list has
    to be read into that language before either can ask whether one is missing.

    Un-digested exactly as a citation is (`validation._validate_claim`): a string
    this dossier never issued comes back unchanged, so an invented handle matches
    no conflict and the conflict it was meant to name stays unconsidered. That
    also means a model that echoes a local id in the clear is taken at its word,
    which is the answer the citation path gives the same input -- and an id the
    model was never shown is no easier to guess here than an `observation_key`
    is there.
    """
    considered = payload.get(field)
    if not isinstance(considered, Sequence) or isinstance(considered, (str, bytes)):
        return set()
    return {
        local_ref(item, handles=handles)
        for item in considered if isinstance(item, str)
    }


def _placement_site(
    dossier: Dossier,
    raw: object,
    verdict: P8Verdict,
    dependencies: PlacementDependencies,
    conflict_handles: Mapping[str, str],
) -> P8Verdict | None:
    payload = _payload_of(raw)
    destination = payload.get("destination")
    vocab = set(dossier.allowed_vocabulary)
    plan_version = dossier.plan_version or ""
    if destination in (None, "none"):
        return _rewrite(
            verdict,
            outcome=ABSTAIN,
            disposition=NO_SUPPORTED_DESTINATION,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    destination = str(destination)
    # THE STRUCTURAL WALL, AND IT IS THE FROZEN TREE (`104` §18.2 gap 2). `00`'s
    # amendment names exactly two things a placement may be rejected for, and this
    # is the first of them: "a node that is not in the frozen tree". It is asked
    # FIRST now, ahead of the vocabulary flag below, so that a destination which
    # is neither on the shortlist nor in the tree is refused as the invention it
    # is rather than sent to a person as a folder they might want.
    if not dependencies.node_exists(destination, plan_version):
        return _reject(verdict, NODE_NOT_IN_FROZEN_TREE, NO_DESTINATION)
    # THE MODEL'S OWN ADMISSION FIRST. A level it marks `unsupported` is a slot
    # filled without evidence and has a reason code of its own; grounding it
    # would relabel a failure the model reported honestly as an invention.
    # Everything else goes to the grounding check below.
    if any(item.get("support") == "unsupported" for item in _dimensions(payload)):
        return _reject(verdict, SLOT_FILLED_WITHOUT_EVIDENCE, NO_DESTINATION)
    # A `context` level is verified, not trusted: the group it names must be one
    # the person accepted the file into. The nearest code in the closed set is
    # the one for a slot filled on evidence the validator cannot see.
    if _unverified_context_level(payload, dossier):
        return _reject(verdict, SLOT_FILLED_WITHOUT_EVIDENCE, NO_DESTINATION)
    invented = _invented_dimension(payload, dossier)
    if invented is not None:
        return _reject(verdict, invented, NO_DESTINATION)
    # THE PRIVACY CHECK STAYS A REJECTION, AND IT IS THE ONE EXCEPTION `104`
    # §18.2 GAP 2 IS NOT ALLOWED TO MAKE (recorded so the owner can strike it).
    # The gap's patch says the non-structural downgrades become flags; this one
    # is not a downgrade of an answer's quality. `00`:114 names it beside the
    # structural checks in the same sentence -- the validator confirms "that a
    # sensitive file is handled under the USER'S PRIVACY POLICY" -- and the
    # policy is the person's own instruction, not code's opinion about evidence.
    # A flag here would move a sensitive file into a folder their policy forbids
    # and tell them afterwards, which is the one direction this product does not
    # trade for coverage. `dependencies.sensitivity_policy` is injected by the
    # composition root, so what it forbids is configuration and never this
    # module's guess.
    if not dependencies.sensitivity_policy(dossier, payload):
        return _reject(verdict, SENSITIVITY_POLICY_VIOLATION, NO_DESTINATION)
    # THE TWO COUNTS ARE DIAGNOSTICS (`105` §14.1). They must be present and be
    # numbers -- that is the shape, and a shape violation destroys the answer --
    # but they are never compared to a threshold or to each other: one passage
    # can support a parent and its child, and several citations can repeat one
    # nondiscriminating fact, so a count establishes nothing about uniqueness.
    # They stay in the recorded response; nothing here reads their values.
    #
    # SCHEMA IS THE SECOND STRUCTURAL REFUSAL AND STAYS ONE: an answer whose
    # required key is absent or is not a number is not an answer this validator
    # can read at all, which is a different thing from an answer it disagrees
    # with.
    for key in ("support", "next_support"):
        if key not in payload or not _real_number(payload[key]):
            return _reject(verdict, SCHEMA_INVALID, NO_DESTINATION)
    # ----------------------------------------------------------------------
    # EVERYTHING BELOW IS A FLAG (`104` §18.2 gap 2). Five checks that used to
    # destroy or downgrade the answer, each now recorded on a verdict that
    # requires review. See `_flagged` for the ruling they all rest on.
    # ----------------------------------------------------------------------
    flags: list[str] = []
    # INVENTED_NODE NOW MEANS: A REAL FOLDER P11 DID NOT SHOW YOU.
    #
    # This was a rejection and it was the gap's headline: `allowed_vocabulary` is
    # the shortlist P11's six retrieval channels reached, `node_exists` above has
    # already confirmed the destination is a frozen, approved node of this plan,
    # and rejecting it here told the person their own folder was invented. The
    # amendment's structural test is the tree, and the tree said yes. What is
    # left worth saying is that the engine did not think of this folder, which is
    # a reason for a person to look and not a reason to lose the answer.
    if destination not in vocab:
        flags.append(INVENTED_NODE)
    considered_ids = _considered_conflicts(
        payload, "conflicts_considered", handles=conflict_handles)
    if dossier.conflicts and any(
        item.conflict_id not in considered_ids for item in dossier.conflicts
    ):
        # The prompt asks the model to echo every `conflict_id` "so that it is on
        # record that you saw it", and the dossier already showed it each one. A
        # missing echo is a bookkeeping failure about a flag the model was given,
        # not a fact about the destination -- and `00`:42's amendment for the
        # same shape at site A is explicit that a contradiction "is shown to the
        # model as a flag with its evidence, and the model reconciles".
        flags.append(CONFLICT_IGNORED)
    if payload.get("generic_hub") is True or destination == "node-hub":
        # §6.5's "connected only by generic similarity or one high-frequency
        # entity must remain uncertain rather than being absorbed". Uncertain is
        # what a review IS; `weak` also made it unproposable, which is the
        # product declining to say anything at all about a file.
        flags.append(GENERIC_HUB_ONLY)
    # BELOW_SUPPORT_THRESHOLD now means: no level of the chosen candidate is
    # supported -- the model placed the file and listed nothing that holds it.
    if not _dimensions(payload):
        flags.append(BELOW_SUPPORT_THRESHOLD)
    # INSUFFICIENT_MARGIN now means: the model itself reports a second fully
    # supported candidate still standing beside its destination. The text
    # defines `alternatives` as exactly that -- what stood after ancestors and
    # shared branches were resolved -- and tells the model that a non-empty list
    # is a `none`.
    #
    # **THIS IS THE CODE ARM OF `104` §18.2 GAP 7** and it is worth naming,
    # because that gap is marked OWNER'S WORD: gap 7 records that "`:501-509`
    # converts any non-empty `alternatives` into `INSUFFICIENT_MARGIN`, which the
    # prompt never says (it invites a populated list)" and offers two remedies --
    # "make alternatives non-fatal, or say in the text that a populated list is
    # an abstention". §18.2 gap 2's patch chooses the first for the reason gap 2
    # is about; the second is a prompt change and stays the owner's. A
    # cooperative model that lists what else it considered keeps its placement
    # and a person sees the list.
    if _alternatives(payload):
        flags.append(INSUFFICIENT_MARGIN)
    if payload.get("weak_retrieval") is True:
        # THE ONE FLAG WITH NO WORD OF ITS OWN, and it had none as a downgrade
        # either -- this arm set `reasons=()`, so nothing it fired on could be
        # counted in a histogram or explained to anybody. The site-C reason set is
        # closed and adding a member to it is the owner's call (the precedent is
        # `VALUE_NOT_IN_CITED_TEXT`, added at site A "WITH THE OWNER'S APPROVAL,
        # RECORDED HERE"), so what this does today is set the review flag and no
        # more, which is strictly more than the person got before. The proposed
        # name is in the report. `c_placement_response_schema.json` forbids the
        # key outright (`additionalProperties: false`), so in the product this
        # arm is reachable only through `llm_harness.fixtures`' bench payloads.
        # THE WORD, since 9 Sep 2026: `WEAK_RETRIEVAL_REPORTED`, the owner's
        # approval recorded beside the constant in `vocabulary`. The flag now
        # counts in a histogram and explains itself like its siblings.
        flags.append(WEAK_RETRIEVAL_REPORTED)
    return _flagged(verdict, tuple(flags))


def _placement_disposition(verdict: P8Verdict) -> P8Verdict:
    """The disposition each outcome lands on, asked once after every check.

    **`ACCEPT_DIRECT` NOW READS `requires_review`** (`104` §18.2 gap 2). It did not
    have to before: nothing could set that flag on a direct acceptance, so the
    outcome alone decided and `move_plan_eligible` was safe. `_flagged` can now,
    and this is the line that makes a flag mean something -- without it, a
    placement carrying `INVENTED_NODE` or `INSUFFICIENT_MARGIN` would be
    `move_plan_eligible`, which is the flag written into the record and the file
    moved anyway. That is a worse product than the rejection it replaced.

    Read off `requires_review` rather than off `reasons`, because `requires_review`
    is the field `p8_seam.transcribe` and `PlacementDecision.review_policy` already
    gate on, and a second predicate over the same question is how the two come to
    disagree.
    """
    if verdict.outcome == ACCEPT_DIRECT:
        disposition = (VALID_REVIEW_REQUIRED if verdict.requires_review
                       else MOVE_PLAN_ELIGIBLE)
    elif verdict.outcome == ACCEPT_CONTEXT_SUPPORTED:
        disposition = VALID_REVIEW_REQUIRED
    elif verdict.outcome == WEAK:
        disposition = UNRESOLVED
    elif verdict.outcome == REJECT:
        disposition = NO_DESTINATION
    elif verdict.outcome == ABSTAIN:
        disposition = NO_SUPPORTED_DESTINATION
    else:
        disposition = verdict.disposition
    return _rewrite(verdict, disposition=disposition)


def _same_file_evidence(dossier: Dossier, verdict: P8Verdict) -> bool:
    """Every reference this claim leans on names the file the dossier is about.

    `104` R-158. This read the model's citations as it wrote them, and the model
    writes what it was shown: `wire_ref` keys a P4 `observation_key` before it
    leaves the device, so the lookup below missed on every real key and the
    citation was skipped -- the check could not fire on any run, and passed only
    because the fixtures cite a reference that is not a P4 key and so travels in
    the clear.

    `verdict.citations_checked` is the same list after `validation._validate_claim`
    has un-digested it, which is the one place that translation happens. It also
    arrives already resolved: a reference outside the dossier is
    `CITATION_NOT_IN_DOSSIER` and the claim is rejected before any site validator
    sees it, so a reference here always names an item and `by_ref` never misses.
    """
    by_ref = {item.evidence_ref: item for item in dossier.evidence_items}
    for citation in verdict.citations_checked:
        item = by_ref.get(citation.citation_ref)
        if item is not None and item.location != dossier.subject_ref:
            return False
    return True


def _residual_site(
    dossier: Dossier,
    raw: object,
    verdict: P8Verdict,
    dependencies: ResidualDependencies,
    conflict_handles: Mapping[str, str],
) -> P8Verdict | ValidationUnavailable | None:
    payload = _payload_of(raw)
    if "support" in payload and "next_support" in payload:
        return ValidationUnavailable(missing=("site_d_support_rule",))
    action = payload.get("action")
    if action not in RESIDUAL_ACTIONS:
        return _reject(verdict, ACTION_NOT_IN_CONTROLLED_SET, REJECTED)
    target = payload.get("target")
    if isinstance(target, str) and "/" in target:
        return _reject(verdict, INVENTED_FOLDER, REJECTED)
    plan_version = dossier.plan_version or ""
    if action in _TARGET_ACTIONS:
        if not isinstance(target, str) or not target:
            return _reject(verdict, DESTINATION_NOT_IN_FROZEN_TREE, REJECTED)
        approved = set(dependencies.approved_target_ids)
        if not dependencies.node_exists(target, plan_version):
            return _reject(verdict, DESTINATION_NOT_IN_FROZEN_TREE, REJECTED)
        if target not in approved and target not in dossier.allowed_vocabulary:
            return _reject(verdict, DESTINATION_NOT_IN_FROZEN_TREE, REJECTED)
    if not _same_file_evidence(dossier, verdict):
        return _reject(verdict, EVIDENCE_NOT_IN_FILE_RECORD, REJECTED)
    if not dependencies.sensitivity_policy(dossier, payload):
        return _reject(verdict, SENSITIVITY_RESTRICTION_IGNORED, REJECTED)
    considered_ids = _considered_conflicts(
        payload, "relationships_considered", handles=conflict_handles)
    if any(
        item.kind == "stronger_relationship" and item.conflict_id not in considered_ids
        for item in dossier.conflicts
    ):
        return _reject(verdict, STRONGER_RELATIONSHIP_OVERLOOKED, RETURN_TO_PLACEMENT)
    if action == MARK_REVIEW_LATER:
        return _rewrite(
            verdict,
            outcome=WEAK,
            disposition=REVIEW_LATER,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    if action == ABSTAIN:
        # `104` R-56'S STRUCTURAL "NONE OF THESE" AT THIS SITE, AND IT WAS NOT
        # SCORED. `abstain` is one of the response schema's three
        # `no_target_actions`, so the model may take it without volunteering a
        # word of prose -- which is the whole point of a structural option, since
        # `qwen3:8b` produced zero abstentions at C and D under every wording
        # tried. The validator walked past it: not a member of `_TARGET_ACTIONS`,
        # so no target was checked, and no rewrite, so the claim kept the
        # acceptance its citations earned. A model that said it could not tell was
        # recorded as having chosen a residual destination, with `target` null
        # underneath it.
        #
        # Site C has had this since it was written -- `destination in (None,
        # "none")` is the first line of `_placement_site` -- and this is its twin,
        # written the way `mark_review_later` above is written.
        #
        # `leave_in_place` because that is what an abstention at the residual site
        # LEAVES, and `00`:114's correct abstention is a successful outcome rather
        # than a rejection or a move. NOT `WEAK`: `mark_review_later` is the model
        # asking for the file to come back, and "I cannot tell" is not a request.
        return _rewrite(
            verdict,
            outcome=ABSTAIN,
            disposition=LEAVE_IN_PLACE,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    return None


def _residual_disposition(verdict: P8Verdict, raw: object | None = None) -> P8Verdict:
    """§7.7's action, in P8's coarser disposition vocabulary.

    `104` R-104. `leave_in_current_location` had `abstain`'s unscored
    fall-through: it is not a member of `_TARGET_ACTIONS`, so `_residual_site`
    checked no target and rewrote nothing, and this function -- reading
    `accept_direct` with an action that is neither of the two returns -- reached
    for the only branch left and recorded `residual_destination`. A model asking
    for the file to STAY was recorded as having named a home, with `target` null
    underneath it.

    **"Leave it here" is a decision, not an abstention, and not a destination.**
    `abstain` is the model saying it cannot tell; this is the model reading the
    evidence and concluding that where the file already sits is where it belongs.
    So the outcome stays the one the citations earned -- `accept_direct`, or
    `accept_context_supported` with its review -- and only the disposition
    changes, to the one the offline residual ladder has always used for this same
    choice (`placement/residual.py`'s `ACTION_OUTCOME`:
    `LEAVE_IN_CURRENT_LOCATION: LEAVE_IN_PLACE`). The two halves of one answer now
    read the same in `llm_verdict` and in `placement_decisions`.

    **Scored HERE and not in `_residual_site`**, unlike `abstain` and
    `mark_review_later`. Those two replace the verdict; this one keeps it, and
    keeping it means the fall-through has to run so that grounding, the
    file-record check, the sensitivity policy and the stronger-relationship check
    all still hold -- a leave is checked like any accepted claim, because it is
    one.

    `may_propose=False` with it: `outcome_for_action` returns `(leave_in_place,
    None)` and P12 builds a plan from `place` alone, so `True` would be P8 saying
    a move plan may follow a decision that moves nothing. It is the answer
    `mark_review_later` and `abstain` beside it already give.

    **`mark_protected_or_unsupported` HAD THE SAME FALL-THROUGH, AND IT IS THE
    SECOND HALF OF R-104.** The ratified D text offers it as one of the eight and
    tells the model in as many words that its `"target" is the word "protected"
    or the word "unsupported"` (`d_residual_template.ladder.txt`:41). It is not a
    member of `_TARGET_ACTIONS`, so `_residual_site` checks no node for it --
    correctly, because the two words are not node ids and `node_exists` would
    refuse the only legal answer -- and it then arrived here with an
    `accept_direct` outcome and neither of the two returns, took the last branch
    left and was recorded `residual_destination`. A model saying "this is
    protected material, do not file it" was recorded as having named a home, with
    the word "protected" standing where a node id belongs.

    So it joins `leave_in_current_location` on the same branch and for the same
    reason: **a mark moves nothing.** `LEAVE_IN_PLACE` is P8's coarser word for
    that -- P8's disposition axis has no member meaning "marked", and minting one
    is a closed-vocabulary addition and the owner's -- and the distinction is not
    lost, because P11 keeps it on its own axis: `outcome_for_action` answers
    `(mark_state, <the word>)` and `PlacementDecision` carries `marked_state`
    (`placement/records.py`:503). `may_propose=False` for the same reason it is
    False for a leave: a move plan must not follow a decision that moves nothing,
    and least of all one whose whole content is that the file is not to be
    handled.

    **THE WORD ITSELF IS STILL UNCHECKED HERE, AND DELIBERATELY SO.** Refusing a
    target outside the two would need the two words, and P8 has no home for them:
    `llm_harness.vocabulary` carries the ACTION `mark_protected_or_unsupported`
    and neither of its states, `placement.vocabulary.MARKED_STATES` is P11's and
    `tests/p8/test_p8_architecture.py`'s `NEIGHBOUR_PRODUCERS` forbids every P8
    module from importing `placement`, and deriving the pair by splitting the
    action's own spelling would be a word list built by parsing. Until the two
    words have a P8 home the refusal cannot honestly be made here; what that
    costs is recorded on `placement.residual.outcome_for_action`'s raise, which is
    where a stray word lands today, and pinned as a strict xfail in
    `tests/llm_harness/test_d2_contract_gaps.py`.
    """
    if STRONGER_RELATIONSHIP_OVERLOOKED in verdict.reasons:
        return _rewrite(verdict, disposition=RETURN_TO_PLACEMENT)
    payload = _payload_of(raw) if raw is not None else {}
    action = payload.get("action")
    leaving = action == LEAVE_IN_CURRENT_LOCATION
    marking = action == MARK_PROTECTED_OR_UNSUPPORTED
    moves_nothing = leaving or marking
    may_propose = False if moves_nothing else None
    if verdict.outcome == ACCEPT_DIRECT:
        if action in {RETURN_CONFIRMED_GROUP, RETURN_ACCEPTED_PACKET}:
            disposition = RETURN_TO_PLACEMENT
        elif moves_nothing:
            disposition = LEAVE_IN_PLACE
        else:
            # `104` R-20's residual: the same line `_placement_disposition`
            # already carries for gap 2, made here for gap 1's half. A residual
            # destination a stronger fact contradicts is a flagged acceptance,
            # and `residual_destination_review` is the word this site already
            # uses for an accepted destination a person must see first -- the
            # `accept_context_supported` arm below picks it for exactly that
            # state. Without this line the flag would be in the payload and the
            # destination would read as settled.
            disposition = (RESIDUAL_DESTINATION_REVIEW
                           if verdict.requires_review else RESIDUAL_DESTINATION)
    elif verdict.outcome == ACCEPT_CONTEXT_SUPPORTED:
        # The review survives -- `_rewrite` keeps `requires_review` True for this
        # outcome by construction -- and only the word "destination" goes.
        disposition = (LEAVE_IN_PLACE if moves_nothing
                       else RESIDUAL_DESTINATION_REVIEW)
    elif verdict.outcome == WEAK:
        disposition = REVIEW_LATER if action == MARK_REVIEW_LATER else LEAVE_IN_PLACE
    elif verdict.outcome == REJECT:
        disposition = REJECTED
    elif verdict.outcome == ABSTAIN:
        disposition = LEAVE_IN_PLACE
    else:
        disposition = verdict.disposition
    return _rewrite(verdict, disposition=disposition, may_propose=may_propose)


def _finish(result, *, adjust):
    if isinstance(result, ValidationUnavailable):
        return result
    verdicts, report = result
    return tuple(adjust(item) for item in verdicts), report


def validate_placement_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    contradicts,
    dependencies: PlacementDependencies | None,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
    handle_key: bytes,
):
    missing = _missing_placement(dependencies)
    if missing:
        return ValidationUnavailable(missing=missing)

    conflict_handles = issued_conflict_handles(
        (item.conflict_id for item in dossier.conflicts), key=handle_key)

    def site(dossier_arg, raw, verdict):
        return _placement_site(
            dossier_arg, raw, verdict, dependencies, conflict_handles)

    result = validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
        handle_key=handle_key,
        uncited_claim=_context_only_claim,
    )
    return _finish(result, adjust=_placement_disposition)


def validate_residual_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    contradicts,
    dependencies: ResidualDependencies | None,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
    handle_key: bytes,
):
    missing = _missing_residual(dependencies)
    if missing:
        return ValidationUnavailable(missing=missing)

    conflict_handles = issued_conflict_handles(
        (item.conflict_id for item in dossier.conflicts), key=handle_key)

    def site(dossier_arg, raw, verdict):
        return _residual_site(
            dossier_arg, raw, verdict, dependencies, conflict_handles)

    result = validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
        handle_key=handle_key,
    )
    if isinstance(result, ValidationUnavailable):
        return result
    verdicts, report = result
    try:
        parsed = json.loads(response_bytes)
        raws = parsed.get("claims") if isinstance(parsed, dict) else []
    except (ValueError, TypeError, UnicodeDecodeError):
        raws = []
    if not isinstance(raws, list):
        raws = []
    adjusted = []
    for index, verdict in enumerate(verdicts):
        raw = raws[index] if index < len(raws) else {}
        adjusted.append(_residual_disposition(verdict, raw))
    return tuple(adjusted), report


def _ensure_identity_table(conn: sqlite3.Connection) -> None:
    """`execute`, never `executescript`.

    `sqlite3.Connection.executescript` COMMITs any pending transaction before it
    runs the script. This DDL is lazy -- it runs on every C/D verdict write, and
    `harness._issue_and_validate` holds ONE transaction over the consequence and
    the verdict that justifies it -- so `executescript` here committed the
    harness's transaction from under it, and the harness's own COMMIT then raised
    `cannot commit - no transaction is active`. `_IDENTITY_DDL` is one statement,
    so one `execute` runs it inside whatever transaction the caller owns.
    """
    conn.execute(_IDENTITY_DDL)


def record_cd_verdict(
    conn: sqlite3.Connection,
    verdict: P8Verdict,
    *,
    evidence_snapshot_id: str,
    model_id: str,
    prompt_fingerprint: str,
    release_audit_id: int,
    observed_at: str,
) -> str:
    if not evidence_snapshot_id:
        raise ValueError("evidence_snapshot_id is required for C/D verdicts")
    if not verdict.plan_version:
        raise ValueError("C/D verdicts require plan_version")
    _ensure_identity_table(conn)
    # ONE transaction over both writes. `record_verdict` opens its own, but
    # `transaction` is reentrant via SAVEPOINT, so the inner scope nests instead of
    # committing. Without this the verdict row committed and a failing identity insert
    # left a C/D verdict with no plan/snapshot identity -- a row that cannot say which
    # plan it judged, which is the one thing a C/D verdict exists to record.
    with transaction(conn):
        record_verdict(
            conn, verdict,
            model_id=model_id,
            prompt_fingerprint=prompt_fingerprint,
            release_audit_id=release_audit_id,
            observed_at=observed_at,
        )
        conn.execute(
            "INSERT INTO llm_cd_plan_identity ("
            "verdict_id, plan_version, evidence_snapshot_id"
            ") VALUES (?, ?, ?)",
            (verdict.verdict_id, verdict.plan_version, evidence_snapshot_id),
        )
    return verdict.verdict_id


def _verdict_from_payload(payload: Mapping[str, object]) -> P8Verdict:
    checked = tuple(
        CheckedCitation(
            citation_ref=str(item["citation_ref"]),
            resolved=bool(item["resolved"]),
            span_matched=bool(item["span_matched"]),
        )
        for item in payload["citations_checked"]
    )
    return P8Verdict(
        verdict_id=str(payload["verdict_id"]),
        dossier_id=str(payload["dossier_id"]),
        claim_ref=str(payload["claim_ref"]),
        outcome=str(payload["outcome"]),
        disposition=str(payload["disposition"]),
        reasons=tuple(payload["reasons"]),
        may_propose=bool(payload["may_propose"]),
        requires_review=bool(payload["requires_review"]),
        citations_checked=checked,
        scope=str(payload["scope"]),
        validator_version=str(payload["validator_version"]),
        policy_version=str(payload["policy_version"]),
        plan_version=payload["plan_version"],
    )


def revalidate_for_plan(
    conn: sqlite3.Connection,
    *,
    current_plan_version: str,
    current_evidence_snapshot_id: str,
    previous_verdict_id: str,
    dossier: Dossier,
    response_bytes: bytes,
    evidence_resolver,
    contradicts,
    dependencies: PlacementDependencies | ResidualDependencies | None,
    observed_at: str,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
    handle_key: bytes,
) -> P8Verdict | ValidationUnavailable:
    _ensure_identity_table(conn)
    row = conn.execute(
        "SELECT payload, plan_version FROM llm_verdict WHERE verdict_id = ?",
        (previous_verdict_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"unknown verdict {previous_verdict_id!r}")
    identity = conn.execute(
        "SELECT plan_version, evidence_snapshot_id FROM llm_cd_plan_identity "
        "WHERE verdict_id = ?",
        (previous_verdict_id,),
    ).fetchone()
    stored_plan = identity["plan_version"] if identity is not None else row["plan_version"]
    stored_snapshot = (
        identity["evidence_snapshot_id"] if identity is not None else None
    )
    if (
        stored_plan == current_plan_version
        and stored_snapshot == current_evidence_snapshot_id
    ):
        return _verdict_from_payload(json.loads(row["payload"]))

    if dossier.call_site == C_PLACEMENT:
        missing = _missing_placement(
            dependencies if isinstance(dependencies, PlacementDependencies) else None
        )
    else:
        missing = _missing_residual(
            dependencies if isinstance(dependencies, ResidualDependencies) else None
        )
    if missing:
        return ValidationUnavailable(missing=missing)

    updated = dataclasses.replace(dossier, plan_version=current_plan_version)
    if dossier.call_site == C_PLACEMENT:
        result = validate_placement_response(
            updated,
            response_bytes,
            evidence_resolver=evidence_resolver,
            contradicts=contradicts,
            dependencies=dependencies,
            model_id=model_id,
            prompt_fingerprint=prompt_fingerprint,
            dossier_builder=dossier_builder,
            release_audit_id=release_audit_id,
            handle_key=handle_key,
        )
    else:
        result = validate_residual_response(
            updated,
            response_bytes,
            evidence_resolver=evidence_resolver,
            contradicts=contradicts,
            dependencies=dependencies,
            model_id=model_id,
            prompt_fingerprint=prompt_fingerprint,
            dossier_builder=dossier_builder,
            release_audit_id=release_audit_id,
            handle_key=handle_key,
        )
    if isinstance(result, ValidationUnavailable):
        return result
    fresh = result[0][0]
    stamped = _rewrite(
        fresh,
        verdict_id=(
            f"{previous_verdict_id}::{current_plan_version}::"
            f"{current_evidence_snapshot_id}"
        ),
        plan_version=current_plan_version,
    )
    record_cd_verdict(
        conn, stamped,
        evidence_snapshot_id=current_evidence_snapshot_id,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        release_audit_id=release_audit_id,
        observed_at=observed_at,
    )
    supersede_verdict(
        conn, previous_verdict_id, stamped.verdict_id,
        reason="plan_or_snapshot_changed",
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        release_audit_id=release_audit_id,
        observed_at=observed_at,
    )
    return stamped
