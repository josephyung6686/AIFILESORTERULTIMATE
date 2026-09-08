# src/model_placement.py
"""§6.12 step 7 and §7.7's model path: the injections P11 has never been given.

**Why this file exists at all.** `PipelineInputs` carries eight fields for the
model path -- `gate`, `model_client`, `prompt`, `call_dependencies`,
`model_call_request`, `chosen_node_of`, `residual_action_of`,
`sensitivity_policy` -- and `src/cli.py` passed `None` for every one of them from P11 landing
until the R-55 work began supplying `sensitivity_policy`, and
`model_path_available()` reads them as a set, so it was `False` on every run
this product had made and step 7 had never executed. `model_path_available()` has therefore been `False` on every run
this product has ever made, and step 7 has never executed. P11 is complete:
`_judge_with_model` assembles the request, `p8_seam` holds the four Site C
authorities and the three Site D ones, and `placement_validation` runs fifteen
checks. Nothing had built the injections. `model_facts.py` did this job for Site A
and this is its sibling.

**This module is built to the prompt and stops there, and that is the honest
state rather than an unfinished one.** `planning/82-FACT-PROMPT-DRAFT.md` §0
records the owner ratifying prompt text for `A_fact` and for nothing else. There
is no ratified `C_placement` text and no ratified `D_residual` text, `run_call`
refuses a site with no prompt, and an agent may not author one. So `prompt` is a
parameter with no default and no fallback, `None` is a first-class value here, and
with `None` every other injection is withheld WITH it -- see
`model_path_injections` for why withholding them together is the point.

**Nothing here is a number and nothing here is a policy.** Every ceiling, cost,
clock, key, client and policy version arrives in `PlacementCallAuthorities` with
no default, and `src/cli.py` is the only file that fills one in. What this module
owns is the SHAPE of the release request and the rule about what may be in it.

**The rule about what may be in it is the reason this file is worth reading.**
Placement is about where a file belongs, and where a file already IS is a path --
`ALWAYS_LOCAL` member 1, with member 6 (filenames) beside it. The observations
that bear most obviously on the question are exactly the ones that may never leave
the device. `releasable_excerpts` is where that is enforced, and it is enforced
before the request is built rather than at the gate, for the reason
`model_facts.releasable_observations` gives: a refusal at the door costs the file
its whole call, and one of these refusals costs it after a document has already
been materialised to refuse.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from decimal import Decimal

from evidence_shape.store import get_observation
from llm_harness.budgets import ScanBudget
from llm_harness.harness import CallDependencies
from llm_harness.records import EvidenceItem, PromptDefinition
# `104` R-159: site A's own release predicate, asked here rather than retyped. The
# import direction is safe and stays that way -- `model_facts` reaches `privacy`,
# `facts` and `llm_harness` and never this module -- and the alternative is two
# spellings of a rule the owner has now divided by the destination.
from model_facts import may_be_released
from privacy.items import Excerpt, sensitive_observation_keys
from privacy.release import ModelCallRequest, ModelTarget, Target
from placement.vocabulary import FILE

#: P8's stage name for a placement call, and the `ModelCallRequest.stage` §8.4's
#: audit record carries. `model_facts` spells its own `fact_interpretation` and
#: `p8_seam` P9's `group_interpretation`; this is the third and it is spelled once.
PLACEMENT_STAGE: str = "placement_interpretation"

#: The eight `PipelineInputs` fields `model_path_available()` reads as a set. Named
#: here so the absent case and the present case cannot drift apart: a field added
#: to one and forgotten in the other is exactly the half-injection
#: `model_path_available` exists to catch, and it would be caught after a dossier
#: had been built.
MODEL_PATH_FIELDS: tuple[str, ...] = (
    "gate", "model_client", "prompt", "residual_prompt", "call_dependencies",
    "model_call_request", "chosen_node_of", "residual_action_of",
    "sensitivity_policy", "model_target", "usage_recorder",
)


@dataclass(frozen=True)
class PlacementCallAuthorities:
    """Everything Sites C and D need, and this module authors none of it.

    `prompt` is `PromptDefinition | None` and the `None` is not a convenience: no
    text is ratified for either site, and a module that supplied placeholder text
    so the path would light up would be announcing a call it could not honestly
    make. See `model_path_injections`.

    `chosen_node_of` and `residual_action_of` are the two reads P11 files back to
    its caller: `P8Verdict` names a `claim_ref` and not a destination, and P8
    rewrites §7.7's eight actions into its own coarser disposition, so which node
    and which action the model chose can only be read by whoever knows the
    response shape -- which is whoever supplied the prompt.

    `sensitivity_policy` is P7's answer about this release. `p8_seam` refuses a
    non-callable one by name: P8 returns `ValidationUnavailable` without it and
    P11 invents no permission.
    """

    gate: object
    model_client: object
    prompt: PromptDefinition | None
    #: SITE D'S OWN TEXT, and `None` is legal on exactly the terms
    #: `residual_action_of`'s is: a deployment may wire C and not D, and
    #: `PipelineInputs.prompt_for` refuses at the moment a residual set actually
    #: asks for a model rather than at composition.
    #:
    #: It exists because `_judge_with_model` serves BOTH placement sites and read
    #: one field, so the composition root had to pick one prompt for two sites and
    #: picked C's. A residual answer names one of §7.7's eight actions; C's
    #: response schema has no `action` key, and C's shaping policy describes a
    #: different question. `llm_harness.run_call` now refuses a request whose call
    #: site is not the prompt's, so the borrow is a refusal before the gate rather
    #: than a verdict nobody can account for.
    residual_prompt: PromptDefinition | None
    model_target: ModelTarget
    evidence_resolver: Callable[[str], object]
    contradicts: Callable[..., bool]
    scan_budget: ScanBudget
    estimated_cost: Decimal
    actual_cost: Decimal
    policy_version: str
    wire_handle_key: bytes
    sensitivity_policy: Callable[..., bool]
    chosen_node_of: Callable[[object], str]
    #: Site D only, and `None` is legal: a deployment may wire C and not D.
    #: `_residual_action_and_target` refuses a non-callable one at the moment a
    #: residual set actually asks for a model, which is the right moment -- it is
    #: not a defect in a run that never had one.
    residual_action_of: Callable[[object], tuple[str, object]] | None
    #: `104` R-14's one-slot usage mailbox, the same object site A's `run_call`
    #: takes from, or `None` for a transport that reports no usage. Defaulted for
    #: `FactCallAuthorities.usage_recorder`'s reason: it is optional by design,
    #: and a deployment recording none is a real deployment. `104` R-145: site C
    #: wrote responses with no `llm_call_usage` row until it travelled here.
    usage_recorder: object | None = None


def releasable_excerpts(conn: sqlite3.Connection, *,
                        evidence_refs: Sequence[str],
                        locality: str) -> tuple[Excerpt, ...]:
    """The observations a placement call may ask P7 to release. Five exclusions.

    **`locality` is required with no default (`104` R-159), and this function is the
    reason the ruling could not stop at site A.** The owner ruled §15.4 item 14 the
    first way on 8 Sep 2026 -- a local model may be shown a whole text unit, the
    person's folder path and OCR text, within the dossier ceiling -- and the brief
    for that build named `model_facts.may_be_released`, `privacy.items.check_item`
    and the gate. It did not name this, and without it the ruling would have been
    half applied: `_model_call_request_builder` below builds the gate's
    `requested_items` from what this returns, so a whole page refused HERE never
    reaches the door at all and site C would have gone on seeing exactly what it saw
    before. The five refusals are one question -- *may this reading leave the device*
    -- and one question does not get two answers because two sites ask it.

    The zone and whole-unit arms below now DELEGATE to
    `model_facts.may_be_released`, which is the same predicate site A asks and the
    same one `104` R-156 already made this seam's other half ask. What stays here is
    the live-row selection, which is the one place this function deliberately does
    not follow `model_facts` -- see the fifth bullet.

    Each is one of the gate's own refusals applied a step early, so the request is
    never BUILT rather than built and denied. The count is FIVE and not four
    because the fifth -- P5's per-value signal -- was missing when this module was
    first written, and neither of the rules that look like they would catch it
    can: a flagged card number sits in an ordinary zone and is a fraction of its
    unit, so the zone test and the whole-unit test both pass it through.

      * `ALWAYS_LOCAL_ZONES` -- `path`, `filename` and `ocr`. This is the one that
        matters most at this site and it is the reason this function exists:
        placement is about where a file belongs, so the observation naming where
        it already is looks like the most relevant evidence in the store and is
        the one thing that may never leave the device. `Denied(always_local_item)`
        at the gate; not offered at all here. **Since `104` R-159 the first and
        third are offered to a LOCAL target** -- nothing leaves the device, and 20
        of r15's 43 labelled coursework files named their course only in the folder
        the person filed them in -- while `filename` is refused to both, because
        §7.7's kind has its own door.
      * a span that covers the whole of its unit, which is §8.4's "should not send
        full documents where a short heading or OCR excerpt is enough".
        `Denied(whole_document_requested)` -- and that fires only after the text
        has been materialised, so leaving it to the door means paying to build a
        document in order to refuse it. **Cloud only since `104` R-159**: §8.4's
        sentence sits under `00`:186's "when a cloud model is used", and what
        bounds a local call instead is the dossier ceiling, which at this site
        `cli.evidence_for` spends by handing `reading_citations` the remainder the
        facts and the anchor lines left.
      * a span whose unit is not there. `materialise` raises `UnresolvableSpan`
        for this rather than denying, because a span with nothing to take a
        substring of is a contract failure, and a placement call is not the place
        to discover one.
      * a value P5 signalled `potentially_sensitive`. This is the only per-value
        sensitivity signal in the product -- P7 owns no detector -- and neither
        of the rules above can see it: a card number sits in an ordinary `body`
        zone and is a fraction of its unit, so the zone test and the whole-unit
        test both pass it. `model_facts.releasable_observations` reads it at site
        A and this is its counterpart. `Denied(ProtectedItemRequested)` at the
        gate; not offered at all here.
      * a ref with no LIVE observation behind it -- a citation handle that no
        longer resolves, or one whose reading a later extraction retracted.

        The live row is selected in SQL rather than through
        `observations_by_key`, and that is the one place this function does not
        follow `model_facts`. `observations_by_key` returns EVERY row for a key
        on purpose -- §8.5's cross-version diff needs both -- and `Observation`
        carries no supersede state at all: `observation_row` says in its own
        docstring that it exists because "the emitted record has no" it. So there
        is no way to filter after the fact, and a caller taking the newest row by
        insertion order would offer a superseded reading whenever the replacement
        happened to be written first. `cli._stored_value_of` filters
        `superseded_by IS NULL` at the resolving end of this same seam; this is
        the releasing end, where getting it wrong sends the retracted value.

    **The span is the observation's OWN.** `cli.evidence_for` builds every
    `EvidenceItem` with `excerpt_span=(0, len(canonical_value))` -- a span over the
    VALUE, laid against a text unit the value did not come from. P7 resolves a span
    by taking that substring of the UNIT, so such a span releases the first N
    characters of the document rather than the value that was cited. `model_facts`
    writes the same rule down for Site A and `p8_seam` records what a synthesised
    span cost at Site B: every unbounded observation refused with
    `UnresolvableSpan`, after the release had been minted.

    A span-less observation with no unit is offered: that is §2.3's cell and
    §2.8's EXIF field, the shape where the address IS the whole citation.
    """
    offered: list[Excerpt] = []
    # Cached per file, because the lookup walks every extraction run for a file
    # and a corpus asks about the same file once per candidate.
    signalled: dict[str, frozenset[str]] = {}
    for ref in evidence_refs:
        row = conn.execute(
            "SELECT observation_id FROM evidence WHERE observation_key = ? "
            "AND superseded_by IS NULL ORDER BY rowid DESC LIMIT 1",
            (ref,)).fetchone()
        if row is None:
            continue
        observation = get_observation(conn, row["observation_id"])
        where = observation.location
        if observation.file_id not in signalled:
            signalled[observation.file_id] = sensitive_observation_keys(
                conn, observation.file_id)
        # THE OTHER FOUR REFUSALS, ASKED THROUGH SITE A'S OWN PREDICATE (`104`
        # R-159). The always-local zone, P5's signal, the empty value and the two
        # whole-unit tests were retyped here when this module was written, and the
        # ruling divided two of them by the destination -- so a second spelling would
        # have been a second answer to the ruling as well as to the rules. The bullets
        # above describe what `may_be_released` does; they are its reasoning, kept
        # here because this is where a reader of site C looks for it.
        if not may_be_released(conn, observation,
                               sensitive=signalled[observation.file_id],
                               locality=locality):
            continue
        offered.append(Excerpt(
            observation_key=observation.observation_key,
            span=where.text_span,
            reason="a reading of this file the destination may rest on"))
    return tuple(offered)


def _model_call_request_builder(conn: sqlite3.Connection, *,
                                authorities: PlacementCallAuthorities,
                                file_id_of: Callable[[str], str]):
    """P7's release request, in the shape `_judge_with_model` asks for it.

    P11 holds the builder and never a `Gate`, and assembles this AFTER
    `may_assemble_dossier` has answered -- which is what keeps §8.4's gate on the
    right side of the spend. What arrives here is the subject and the evidence
    metadata; what goes back is a request for the excerpts that survived
    `releasable_excerpts` and no others.

    `prompt_fingerprint` is the PROMPT's, recomputed by `transport.issue` from the
    `PromptDefinition` it is about to send and refused when the two disagree. A
    request bound to anything else raises `BindingMismatch` after P7 has already
    spent the release, which is the defect that kept P9's first real group call
    from ever reaching a model.
    """
    from llm_harness.fingerprint import prompt_fingerprint

    prompt = authorities.prompt

    def build(*, subject_ref: str, evidence_items: Sequence[EvidenceItem],
              max_dossier_tokens: int) -> ModelCallRequest:
        return ModelCallRequest(
            stage=PLACEMENT_STAGE,
            # ONE file. A placement call decides where one subject goes, and a
            # target naming more would authorise a release about files the judge
            # was never asked about.
            target=Target(file_ids=(file_id_of(subject_ref),), group_id=None),
            model_target=authorities.model_target,
            requested_items=releasable_excerpts(
                conn,
                evidence_refs=tuple(
                    item.evidence_ref for item in evidence_items
                    if item.evidence_ref),
                # `104` R-159: the SAME target the request is addressed to, three
                # lines above. Reading it off the authorities twice would let the
                # release rules answer about one destination while `model_target`
                # named another.
                locality=authorities.model_target.locality),
            prompt_template_id=prompt.template_id,
            prompt_fingerprint=prompt_fingerprint(prompt),
            max_dossier_tokens=max_dossier_tokens)

    return build


def _file_id_of(subject_ref: str) -> str:
    """P11's `subject_ref_of`, read back. THE FILE FORM HAS THREE PARTS.

    `placement.store.subject_ref_of` writes `f"{FILE}:{file_id}:{content_hash}"`
    for a file and `f"{kind}:{group_id}"` for a group. This partitioned on the
    first colon and returned everything after it, so every file address came back
    as `<file_id>:<content_hash>` -- an id that matches no row in `files`. Dead
    while nothing called it, wrong the moment site C is wired, which is the wave
    that wires it.

    **BOTH ENDS ARE TRIMMED AND NEITHER IS TRIMMED BY GUESSWORK.** The kind comes
    off the front by the first colon, which is right because the kind is a closed
    vocabulary with no colon in it. The content hash comes off the BACK by the
    last colon, which is right for the reason the old docstring gave for refusing
    a right-hand split: P11 promises nothing about a file id's shape, so an id
    containing a colon must survive. A hash cannot contain one -- it is sha256
    hex -- so the LAST colon is the boundary between id and hash however many the
    id has.

    The kinds are imported from P11's own vocabulary rather than spelled here: a
    second copy of `"file"` is a second thing to keep true.
    """
    kind, separator, rest = subject_ref.partition(":")
    if not separator:
        return subject_ref
    if kind != FILE:
        return rest or subject_ref
    identifier, hash_separator, _content_hash = rest.rpartition(":")
    if not hash_separator:
        # A file address with no hash is not one `subject_ref_of` writes. Returned
        # whole rather than repaired: a caller looking up half an address gets no
        # row, and inventing the missing half would get it the WRONG row.
        return rest
    return identifier or rest


def _call_dependencies(authorities: PlacementCallAuthorities) -> CallDependencies:
    """The half of `CallDependencies` the caller owns. P11 replaces the other half.

    `_judge_with_model` overwrites `site_dependencies`, `allowed_vocabulary`,
    `proposal_class`, `basis_key`, `learning_scope`, `learning_subject_id` and both
    budget ceilings with its own, and says why for each: a caller-supplied
    vocabulary is a caller-supplied answer to "which nodes exist", and a
    caller-supplied budget is a caller-supplied answer to "what did the user agree
    to spend". They are `None` here rather than guessed, because a value that is
    about to be replaced is a value someone will one day read.

    The reduction ladder is one rung for `model_facts`' reason: the dossier is
    built at the cap already and there is no second, smaller shape of it to fall
    back to, so the rest are honestly absent rather than declared and unbuildable.
    """
    return CallDependencies(
        proposal_class=None, basis_key=None, learning_scope=None,
        learning_subject_id=None,
        evidence_resolver=authorities.evidence_resolver,
        site_dependencies=None, contradicts=authorities.contradicts,
        unreduced_fits=True, summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        scan_budget=authorities.scan_budget,
        estimated_cost=authorities.estimated_cost,
        actual_cost=authorities.actual_cost,
        allowed_vocabulary=None,
        # C and D place a file inside a tree that is already designed. They propose
        # no field and build no level, so the truthful list is empty -- not `None`,
        # which `run_call` reads as a caller who never answered.
        folder_levels=(),
        policy_version=authorities.policy_version,
        wire_handle_key=authorities.wire_handle_key)


def model_path_injections(conn: sqlite3.Connection,
                          authorities: PlacementCallAuthorities, *,
                          plan_version: str) -> dict[str, object]:
    """The eight `PipelineInputs` fields, all present or all absent.

    **All absent when there is no ratified prompt, and the "all" is the point.**
    `model_path_available()` reads seven of the eight as a set and its own
    docstring says why: a run with no model injections is a CORRECT run -- §6.6
    decides a unique direct match with zero model calls -- and "what is NOT legal
    is discovering the injections are missing after a dossier has been assembled".
    Handing over a gate and a client while withholding the prompt would produce
    exactly that: `model_path_available()` would be `False`, so nothing would
    break, and the next person to add a prompt would find a gate built under a
    plan version nobody checked. Withheld together, the absence is one fact with
    one cause and the cause is written down.

    `plan_version` is the FROZEN version and is required for that reason. It is
    not `PLAN_VERSION`, the working version the fact pass runs under:
    `_model_fact_pass` writes its own policy row against the working version
    because P9's groups are recorded there, and says in the same breath that
    `set_privacy_policy`'s row is written against the frozen version "because that
    is the version P11 asks about". Placement IS P11. A gate built under the
    working version would authorise a release against a policy row that describes
    a different plan.
    """
    if authorities.prompt is None:
        return dict.fromkeys(MODEL_PATH_FIELDS, None)
    return {
        "gate": authorities.gate,
        "model_client": authorities.model_client,
        "prompt": authorities.prompt,
        "residual_prompt": authorities.residual_prompt,
        "call_dependencies": _call_dependencies(authorities),
        "model_call_request": _model_call_request_builder(
            conn, authorities=authorities, file_id_of=_file_id_of),
        "chosen_node_of": authorities.chosen_node_of,
        "residual_action_of": authorities.residual_action_of,
        "sensitivity_policy": authorities.sensitivity_policy,
        # `104` R-118: §8.4's gate reads the target's LOCALITY before a dossier
        # exists, and the builder above closes over the same target too late.
        "model_target": authorities.model_target,
        "usage_recorder": authorities.usage_recorder,
    }
