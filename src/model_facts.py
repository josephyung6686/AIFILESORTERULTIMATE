# src/model_facts.py
"""P6's §8.6 `llm` producer: one A_fact call for one file version.

**Why this file exists at all.** `facts.resolver` takes three producers and the
third is a `Stage` -- `(conn, file_id, content_hash) -> tuple[fact_id, ...]`. Every
deployment so far has passed `None` for it, and `FactResolver`'s docstring names
that as "the ordinary case for `llm`, because P8 does not exist". P8 exists now, and
nothing in `src/` turned a file into a `DossierRequest` at site A: `p8_seam.py` does
it for P9's groups and there is no counterpart for P6's files. That gap is the whole
of why the product filled 2 of its 56 declared fields on a real folder.

**Why it is not in `facts/` and not in `llm_harness/`.** `llm_harness.fact_validation`
imports `facts.llm_seam`, so a builder inside `facts/` that reached for
`llm_harness.records` would invert the layer P8 already depends on --
`tests/p8/test_p8_architecture.py` reads those directions. And P8 does not build
dossier requests for its callers: `run_call` takes one. So this is the deployment
layer, a sibling of `production.py`, which is where the same argument put the P1-P7
composition.

**Nothing here is a number and nothing here is a policy.** Every threshold, cap,
budget, clock, model, prompt, normaliser and oracle arrives in `FactCallAuthorities`
with no default, and `src/cli.py` is the only file that fills one in. What this
module owns is the SHAPE of the request and the order the checks run in.

**The three refusals that happen before a call is built**, each because the
alternative is worse than not asking:

  * nothing pending -- every field the schema allows is already settled, so the
    question has no content and the spend buys a repetition of what is known;
  * nothing releasable -- every observation is in an always-local zone, is
    unbounded, or was signalled sensitive, so the dossier would be empty and the
    model would be asked to answer from nothing;
  * no allowlist -- no domain activated and no universal field remains, so §3.5's
    closed vocabulary is empty and every answer would be out of schema.

Each returns `()` and leaves no `unresolved` row: they are not refusals ABOUT the
file, they are the absence of a question. The refusals that ARE about the file --
the privacy bar and the budget bar -- belong to `FactResolver`, which writes them,
and to `Gate`, which records its own.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from database_agent.db import transaction
from evidence_shape.canonical import canonical_json
from evidence_shape.locator import serialize_locator
from evidence_shape.store import unit_length_for_observation
from facts.domains import ActivationSignals, active_field_allowlist
from facts.file_facts import facts_for_file
from facts.evidence import observations_for_version
from facts.llm_seam import FactRequest, build_request
from facts.states import EXCLUDED_STATE
from llm_harness.budgets import ScanBudget
from llm_harness.dossier import dossier_address
from llm_harness.fact_validation import FactValidationDependencies, judgement_version
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.harness import CallDependencies, run_call
from llm_harness.records import (
    REFUSAL_EXCEPTIONS,
    DossierRequest, EvidenceItem, FolderLevel, MalformedRecord, P8Verdict,
    PromptDefinition, ValidationUnavailable,
)
from llm_harness.sites import FactSiteDependencies, SiteDependencies, dispatch
from llm_harness.store import (
    answered_fields,
    call_identity,
    last_response,
    load_dossier,
    prior_call,
    record_call_identity,
    record_call_reuse,
    record_verdict,
    refusal_outcome,
    standing_verdicts,
    supersede_verdict,
)
from llm_harness.transport import ModelClient
from llm_harness.validation import DOSSIER_BUILDER
from llm_harness.vocabulary import A_FACT, DIRECT_ANCHOR, REMAINS_AMBIGUOUS
from privacy.gate import Gate
from privacy.policy import policy_at
from privacy.items import Excerpt, Filename, sensitive_observation_keys
from privacy.resolve import (
    AmbiguousObservationKey, UnresolvableSpan, current_location,
    filename_address,
)
from privacy.release import ModelCallRequest, ModelTarget, Target
from privacy.vocabulary import ALWAYS_LOCAL_ZONES

#: P8's own stage name for a fact call, and the `ModelCallRequest.stage` §8.4's audit
#: record carries. P9 spells its own as `group_interpretation` in `p8_seam.py`.
FACT_STAGE: str = "fact_interpretation"

#: §8.7's scope this call's learning suppression is read at, and the class of
#: proposal it is. One call covers every pending field of one file, so the basis is
#: the file VERSION and not a field=value pair.
#:
#: KNOWN LIMITATION, written here rather than solved: a person who rejects one
#: field's value records a narrower basis than this, so `assess_call`'s
#: `USER_REJECTED_EQUIVALENT` will not fire for an A_fact call the way it does for a
#: group. Making it fire means a per-field call or a per-field basis, and both are
#: decisions about what a call IS -- the owner's, not this module's.
LEARNING_SCOPE: str = "file"
PROPOSAL_CLASS: str = "fact.llm_extraction"

#: The zones §2.2 ranks as meaningful evidence, most placed first. A dossier is
#: capped, so WHICH observations survive the cap is a real choice: a title or a
#: page-one heading carries more meaning than a late body reference, which is §3.7's
#: own sentence. Zones outside this list keep their stored order behind it.
_ZONE_PREFERENCE: tuple[str, ...] = (
    "title", "heading", "metadata", "body", "table", "notes",
)


def require_folder_levels(
        folder_levels: Sequence[FolderLevel]) -> tuple[FolderLevel, ...]:
    """The situation's folder levels, or a refusal. There is no empty situation.

    Every one of the shipped library's 208 situations declares at least one level --
    `tests/integration/test_template_levels_wiring.py` walks all of them -- so an
    empty list here is never "this situation designs no folders". It is a
    deployment that did not read the library, and the damage it does is invisible:
    the dossier stays well-formed and the model is simply asked the flat-vocabulary
    question again, which is the question that filled `work_type` once in 199 files.

    A mapping is refused rather than converted. A `dict` here would be a caller
    authoring a level, and the labels and the `required`/`optional` words are the
    library's own text -- transcribed, never authored, the rule `field_glossary`
    already stands on.
    """
    if not folder_levels:
        raise ValueError(
            "an A_fact call carries the folder levels of the situation the person "
            "named. Every shipped situation declares at least one, so an empty "
            "list is a deployment that never read the template library -- and it "
            "fails silently, by asking the model the question it was already "
            "failing to answer")
    levels = tuple(folder_levels)
    if any(not isinstance(level, FolderLevel) for level in levels):
        raise TypeError(
            "folder levels are `FolderLevel` records read off the shipped template "
            "library. A mapping here is a caller authoring a label, and the labels "
            "are the library's own words")
    return levels


def order_vocabulary_by_levels(
        allowed_vocabulary: Sequence[str],
        folder_levels: Sequence[FolderLevel]) -> tuple[str, ...]:
    """The same closed vocabulary, read in the order the tree is built in.

    **The set is untouched and that is the whole safety argument.** §3.5's closed
    vocabulary is ONE computation shared by the dossier and the validator, and check
    1 asks membership, not position -- so reordering cannot reject an answer the old
    order accepted. What it changes is what the model reads first.

    Why that is worth doing: `active_field_allowlist` lists "the universal rows in
    stored order, then each active schema". The universal rows are `file_type`,
    `creation_date`, `language` and `authored_by`, none of which is ever a folder
    level, and all four sit above every field the person's situation actually
    builds on. Measured over 199 real files the model answered in that order -- 59,
    19, 4 and 34 claims against a single `work_type`.

    The levels lead, in the LIBRARY's order rather than required-first, because the
    dossier's `folder_levels` key prints that same order and two orders of one list
    in one document is a contradiction the model has to resolve. Which levels are
    required is said once, where it is said plainly.
    """
    levels = [level.field for level in folder_levels]
    allowed = tuple(allowed_vocabulary)
    outside = [field for field in levels if field not in allowed]
    if outside:
        raise ValueError(
            f"folder levels {sorted(outside)} are outside this file's allowlist. "
            "The vocabulary and the levels are one computation; leading the list "
            "with a field the validator will reject is how a model is punished for "
            "obeying its instructions")
    seen = set(levels)
    return tuple(levels) + tuple(f for f in allowed if f not in seen)


def open_question(pending: Sequence[str],
                  folder_levels: Sequence[FolderLevel]
                  ) -> tuple[tuple[str, ...], tuple[FolderLevel, ...]]:
    """What is still OPEN on this file: the vocabulary to offer, and the levels to show.

    **Why the dossier asks about pending rather than about the whole schema.** A
    field a stronger fact already settled is not a question. §3.13 ranks `validated`
    and `user_confirmed` above `llm_supported`, so check 4 rejects a model answer
    there before it can become a fact -- the claim was spent to be thrown away.
    Measured on a real run: of the 27 files the model answered about, 8 already
    carried a rule-written `work_type` at `validated`, and `work_type` is the field
    that decides where the file goes.

    It costs more than the wasted claim. One malformed claim destroys every claim in
    the answer (the ratified rule 11), so every question that cannot pay is another
    chance to lose the ones that can. Claims per response measured 7.0 before the
    template link and 9.0 after it; this is the half of that increase nobody wanted.

    **The subset direction is the safe one and it is the only one taken.** Check 1
    measures a proposal against `FactRequest.allowlist`, the full active schema.
    Everything offered here is inside that, so nothing the model is told it may
    propose can be rejected for not being in the active schema -- which is the
    failure `pending_fields_for` warns about, and it happens in the other direction.

    A settled LEVEL is dropped from the shown list too, and that keeps the
    projection exact: `dossier._folder_levels_body` refuses a level naming a field
    the vocabulary does not carry. `()` here is truthful -- this file has no folder
    level still open -- and it is not the empty list `require_folder_levels` refuses,
    which is about a deployment that never read the library at all.
    """
    #: CONSTITUTION 3, AND IT REPLACES ORDERING WITH EXCLUSION. This used to offer
    #: everything pending and merely sort the levels to the front, which does not
    #: stop a model answering what it was shown. Measured on 199 real files with a
    #: model in the loop: 28 `file_type`, 16 `authored_by`, 9 `creation_date`, and
    #: ZERO `subject` -- the required level of the situation being run. The library
    #: forbids two of those from ever becoming a level in its own words, and a
    #: `file_type` cannot divide a branch either, so each was tokens bought to be
    #: thrown away, and each was another chance for rule 11 to void the whole answer.
    #:
    #: The valid options are the situation's OWN, read from `role_bindings` by
    #: `production.folder_levels_for` and passed in here. Nothing is authored: a
    #: library that adds a level widens this with no edit.
    #:
    #: Still a SUBSET of `FactRequest.allowlist`, which is the direction that keeps
    #: check 1 from rejecting something the model was invited to say.
    level_fields = {level.field for level in folder_levels}
    open_fields = set(pending) & level_fields
    offered = tuple(field for field in pending if field in open_fields)
    visible = tuple(level for level in folder_levels if level.field in open_fields)
    return order_vocabulary_by_levels(offered, visible), visible


@dataclass(frozen=True)
class FactCallAuthorities:
    """Everything one A_fact call needs and this module authors none of.

    `evidence_resolver` answers "does this observation key still resolve in the
    store" for §3.6 check 2's coarse half; `normalize` and `contradicts` are the
    C-5 pair neither P6 nor P8 owns, which `cli.normalize_for_model` and
    `cli.contradicts_stronger` answer for this deployment.

    `on_result` is a reporting sink, not an authority: it is handed the file id and
    the object `run_call` returned, so the composition root can count refusals,
    abstentions and failed calls for the screen. `None` means nobody is counting.
    """

    gate: Gate
    model_client: ModelClient
    prompt: PromptDefinition
    model_target: ModelTarget
    activation_signals: ActivationSignals
    #: The folder levels of the situation the person named, read off the shipped
    #: template library by the composition root. Required with no default: absent
    #: means refuse, and a call built without them asks the model the flat-
    #: vocabulary question that filled one `work_type` in 199 files.
    folder_levels: tuple[FolderLevel, ...]
    normalizers: Mapping[str, Callable[[str], Any]]
    normalize: Callable[[str, str], object]
    contradicts: Callable[..., bool]
    evidence_resolver: Callable[[str], object]
    scan_budget: ScanBudget
    estimated_cost: Decimal
    actual_cost: Decimal
    policy_version: str
    wire_handle_key: bytes
    max_released_observations: int
    max_dossier_tokens: int
    observed_at: Callable[[], str]
    on_result: Callable[[str, object], None] | None
    #: THE AUTHORED READINGS, AND THE WALL THEY STOP AT (`104` R-08). The shipped
    #: recognition release carries 314 `needs_llm` rows -- prose saying, per
    #: situation, what a model must decide here and when it must abstain -- which
    #: `recognition.rules` loads into `SchemaRules.deferred_readings` and which
    #: reached nothing (`102` §3: they appear "nowhere outside `src/recognition/`").
    #: The composition root now hands them in, because this is the record one A_fact
    #: call is built from and there is nowhere further for them to go.
    #:
    #: **They are collected and counted here and they are not sent.** The A_fact
    #: template tells the model the dossier "has these keys and no others" and lists
    #: fifteen; `llm_harness.dossier._body` writes exactly those fifteen. A
    #: sixteenth makes the model's own instructions false about the bytes beside
    #: them, and prompt text is the owner's to ratify. The key is the D2 packet's to
    #: add, and `tests/integration/test_deferred_readings_reach_the_boundary.py`
    #: fails the day it appears.
    #:
    #: Defaulted, unlike `folder_levels` above: an absent level list is a wiring
    #: failure and refuses, while a deployment whose release compiled no reading for
    #: a schema truthfully has none.
    #:
    #: Measured: `academic` holds 69 readings, 14,491 characters, against a 4,000
    #: dossier ceiling -- so a SCHEMA's readings can never be sent per call. The
    #: situation's own share (`academic.coursework` plus the schema-wide row) is 11
    #: readings and 2,015, which is affordable in a stable prompt prefix (`104`
    #: R-52). Narrowing this to the situation needs `recognition.rules._schema` to
    #: keep the `row` each reading came from; today it flattens them and drops it.
    deferred_readings: tuple[str, ...] = ()
    #: `104` R-14's one-slot mailbox, or `None`. The composition root builds it,
    #: the transport fills it, and `run_call` takes from it after `settle_call` to
    #: write the usage row. Carried here rather than on `CallDependencies` because
    #: that bundle is for authorities a caller MUST supply -- every field of it is
    #: undefaulted and `tests/p8/test_p8_no_invention.py` enforces that -- while a
    #: usage sink is optional by design: the local transport reports no usage, and
    #: a deployment recording none is a real deployment.
    usage_recorder: object | None = None
    #: CHECK 3'S REVIEW HALF (`104` R-98), the third member of the C-5 pair's family
    #: and the deployment's like the other two. `cli.normalize_for_review` answers it
    #: here; a deployment that authors none has no review path, which is what check 3
    #: did before this field existed, so the default is the old behaviour rather than
    #: a fallback that guesses.
    normalize_for_review: Callable[[str, str], object] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "folder_levels",
                           require_folder_levels(self.folder_levels))
        if self.max_released_observations < 1:
            raise ValueError(
                "a dossier with no released evidence is a model asked to answer "
                "from nothing; the cap is a bound on what is sent, not a switch")
        if self.model_client.model_target != self.model_target:
            # The gate decides about one destination and the transport sends to
            # another. `test_live_path` names the same rule at site B.
            raise ValueError(
                "the gate is asked about `model_target` and the client sends to "
                "`model_client.model_target`; two values here would authorise one "
                "destination and deliver to a different one")


def pending_fields_for(conn: sqlite3.Connection, *, file_id: str,
                       content_hash: str,
                       activation_signals: ActivationSignals) -> tuple[str, ...]:
    """Fields the active schema allows that this file version does not yet carry.

    The allowlist is `active_field_allowlist`, which is §3.5's ONE computation and
    is also what the dossier's `allowed_vocabulary` is built from -- a model
    measured against one list and validated against another can be rejected for
    obeying its instructions.

    A field with a `rejected` fact is still pending: §3.13 makes `rejected` an
    exclusion rather than a value, so the field is open and nothing holds it.
    """
    allowed = active_field_allowlist(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=activation_signals)
    settled = {row["field_key"] for row in facts_for_file(conn, file_id, content_hash)
               if row["active"] and row["reliability_state"] != EXCLUDED_STATE}
    return tuple(field for field in allowed if field not in settled)


def dossier_tokens(values: Iterable[str]) -> int:
    """`00`:251's "Maximum dossier tokens per model call", measured in CHARACTERS
    and used as an UPPER BOUND on tokens. `104` SF-5.

    **Why a bound and not a tokenizer.** P7 says it in its own words -- "P7 owns no
    tokenizer and inventing one would invent a number" -- and hands the measurement
    to the caller. This deployment is the caller and it has no tokenizer for the
    models it talks to either: the one file in `src/readers/` that carries a
    tokenizer is `embedding_minilm.py`, whose WordPiece vocabulary belongs to a
    sentence-embedding model, needs 90 MB of downloaded weights to load at all, and
    would answer a question about a different model's arithmetic.

    **Why characters are an honest answer rather than a placeholder.** Every BPE and
    WordPiece token consumes at least one character of its input, so a payload of N
    characters is at most N tokens under any of them. The count therefore errs in
    exactly one direction -- it can refuse a call the true count would have allowed,
    and can never allow one the true count would have refused -- which is the
    direction a safety ceiling has to err in. The familiar `characters / 4` rule is
    the other direction and is an English-prose average: it under-counts CJK by
    roughly four times, and this owner's corpus is Hong Kong coursework.

    **What it does NOT count.** The prompt template, the folder levels, the
    vocabulary and the evidence metadata all travel with the dossier and are not
    here. They are bounded by the library and the schema -- the same on every file
    in a situation -- and the ceiling exists for the part that is not: the released
    content, which grows with the document. `privacy.fixtures._measure_tokens`, P7's
    own published example of what a caller supplies, counts exactly this and nothing
    else, and P8's own name for the request's copy of the number is "the caller's
    echo of it".
    """
    return sum(len(value) for value in values)


def measure_released_tokens(request, resolved: Sequence) -> int:
    """`Gate.measure_tokens`'s binding for site A: `(request, resolved) -> int`.

    `resolved` is what is about to leave, AFTER redaction -- so the number the door
    compares against P1's ceiling is the number of characters the provider would
    receive. The three reference-only kinds carry no value and are absent from
    `resolved` by design (`gate.REFERENCE_ONLY`), so they add nothing here, which is
    correct: an evidence reference is "an id only -- no content".

    The FILENAME is not one of them since `104` R-06 (`gate.NAME_BEARING`): it
    resolves to the person's own name for the file and its characters are counted
    here like any other released value, because they are characters the provider
    would receive.

    `request` is unread, and is taken because P7's signature offers it. A caller
    that measured `request.max_dossier_tokens` instead of the payload would be
    reading its own echo of the ceiling back to the gate.
    """
    return dossier_tokens(item.value for item in resolved)


def releasable_observations(conn: sqlite3.Connection, *, file_id: str,
                            content_hash: str, limit: int) -> tuple:
    """The observations this file may offer a model, most placed first, capped.

    Four exclusions, and each is one of the gate's own refusals applied a step early
    so the call is never BUILT rather than built and denied. Every one of them
    refuses the WHOLE request, not the item -- one bad observation among eight costs
    the file its call -- which is why they are read here and not left to the door:

      * `ALWAYS_LOCAL_ZONES` -- `path` and `filename`, the two zones §8.4's members
        1 and 6 have a route out through. The filesystem extractor writes one
        observation per file whose raw value is the parent directory.
        `Denied(always_local_item)`.
      * `sensitive_observation_keys` -- P5's per-value signal.
        `ProtectedItemRequested`.
      * a span that covers the whole of its text unit, and a span-less observation
        whose value is at least as long as the unit standing at its own path. That
        is `items.is_whole_document` read against P4's own length-only lookup,
        and §8.4's sentence behind it: the engine "should not send full documents
        where a short heading or OCR excerpt is enough to resolve the question."
        `Denied(whole_document_requested)`, and it fires AFTER the text has been
        resolved, so leaving it to the gate means paying to materialise a document
        in order to refuse it.
      * a span-less observation with no unit at its path is offered, because that is
        §2.3's cell and §2.8's EXIF field -- the shape where the address IS the
        whole citation and there is no document for it to be the whole of.

    The span is the observation's OWN, never a synthesised `(0, len(value))`:
    `p8_seam` records what that cost at site B -- every unbounded observation
    refused with `UnresolvableSpan` after the release had been minted.
    """
    sensitive = sensitive_observation_keys(conn, file_id)
    offered = []
    for observation in observations_for_version(conn, file_id, content_hash):
        where = observation.location
        if where.zone in ALWAYS_LOCAL_ZONES:
            continue
        if observation.observation_key in sensitive:
            continue
        if not observation.raw_value:
            continue
        unit_length = unit_length_for_observation(conn, observation)
        if where.text_span is None:
            # The two span-less shapes, told apart exactly as `resolve.materialise`
            # tells them apart: by the unit at the observation's own path.
            if (unit_length is not None
                    and len(observation.raw_value) >= unit_length):
                continue
        else:
            if unit_length is None:
                # `materialise` raises `UnresolvableSpan` here rather than denying:
                # a span with nothing to take a substring of is a contract failure,
                # and this call is not the place to discover it.
                continue
            if (where.text_span.start <= 0
                    and where.text_span.end >= unit_length):
                continue
        offered.append(observation)

    def placed(observation) -> tuple[int, str]:
        zone = observation.location.zone
        rank = (_ZONE_PREFERENCE.index(zone) if zone in _ZONE_PREFERENCE
                else len(_ZONE_PREFERENCE))
        return (rank, observation.observation_key)

    return tuple(sorted(offered, key=placed)[:limit])


def _evidence_items(observations: Sequence) -> tuple[EvidenceItem, ...]:
    """The builder's reference metadata, one per offered observation.

    `build_dossier` requires every released key to have one of these: without it P8
    would have to invent `kind`, `location`, `reliability_state` and `basis`, which
    §1 forbids. `basis` is `direct_anchor` because these are P4's own readings of
    the file, not a neighbour's inference about it.
    """
    return tuple(
        EvidenceItem(
            evidence_ref=observation.observation_key,
            kind="excerpt",
            location=serialize_locator(observation.location),
            excerpt_span=(None if observation.location.text_span is None else
                          (observation.location.text_span.start,
                           observation.location.text_span.end)),
            reliability_state=observation.reliability,
            basis=DIRECT_ANCHOR,
        )
        for observation in observations
    )


def filename_citation(conn, file_id: str) -> EvidenceItem | None:
    """The builder's metadata for §7.7's filename, or `None` when P4 cannot address it.

    THE REQUEST HAS TO ASK FOR WHAT THE DOOR RELEASES (`104` R-06, the merge). The
    gate materialises the name through `resolve.filename_address`; P8's dossier
    refuses a released key that is not among the requested ones AND not among the
    builder's `evidence_items`. Both halves are this one row, and it names the same
    observation the gate will, because both call `filename_address`.

    `None` rather than a raise when there is nothing to name. `filesystem` writes a
    name for every indexed file, so this is the corpus assembled without that
    extractor rather than a contract failure -- and the precedent is
    `_offerable_observations` filtering an unaddressable observation out BEFORE
    offering it: "this call is not the place to discover it". The consequence is
    visible, not silent: no `Filename` item is offered, so the payload instrument's
    `offered` column falls with its `released` column rather than the two parting.

    `basis` is `direct_anchor` and `reliability_state` is P4's own for that
    observation: a filename is the person's label read verbatim off the file, which
    is the definition of a direct anchor rather than an inference.
    """
    try:
        address = filename_address(conn, file_id)
        located = current_location(conn, address.observation_key,
                                   within_file_ids=(file_id,))
    except (UnresolvableSpan, AmbiguousObservationKey):
        return None
    location = located.location
    span = location.text_span
    return EvidenceItem(
        evidence_ref=address.observation_key,
        kind="filename",
        location=serialize_locator(location),
        excerpt_span=None if span is None else (span.start, span.end),
        reliability_state=_filename_reliability(conn, address.observation_key),
        basis=DIRECT_ANCHOR,
    )


def _filename_reliability(conn, observation_key: str) -> str:
    """P4's own word for the filename observation, never a constant typed here."""
    row = conn.execute(
        "SELECT reliability FROM evidence WHERE observation_key = ? "
        "AND superseded_by IS NULL LIMIT 1", (observation_key,)).fetchone()
    if row is None:
        raise UnresolvableSpan(
            f"observation {observation_key!r} resolved a location and then had no "
            f"row; P4's evidence table answered two ways about one key")
    return row["reliability"]


def build_fact_request(
    request: FactRequest,
    observations: Sequence, *,
    filename: EvidenceItem | None = None,
    model_target: ModelTarget,
    prompt: PromptDefinition,
    max_dossier_tokens: int,
) -> DossierRequest:
    """A reference-shape conversion and nothing else. No text crosses this line.

    `prompt_fingerprint` is the PROMPT's. `transport.issue` recomputes it from the
    `PromptDefinition` it is about to send and refuses the release when the two
    disagree, so a request bound to anything else -- the dossier's own address, say
    -- raises `BindingMismatch` after P7 has already spent the release. That is the
    defect that kept P9's first real group call from ever reaching a model, and it
    is written down here so site A does not rediscover it.
    """
    return DossierRequest(
        call_site=A_FACT,
        # The FILE, because `validate_fact_proposal` refuses a dossier whose
        # `subject_ref` is not the `FactRequest`'s `file_id`: a dossier describing
        # one file must not write a fact onto another.
        subject_ref=request.file_id,
        # §3.5's own words for why a model is asked at all: the deterministic
        # producers ran first and left these fields open. `remains_ambiguous` is the
        # first of FACT_ELIGIBILITY's three and is the one that is true of every
        # file that reaches here.
        eligibility_reason=REMAINS_AMBIGUOUS,
        # THE FILENAME'S ROW FIRST, and among the FILE's keys rather than the
        # frame's: `_FILE_KEYS` holds `evidence_items` and `released_evidence`,
        # and R-58's shared prefix is the frame, which is constant across the
        # files of one situation. A per-file name in it would end the prefix at
        # the first file.
        evidence_items=((filename,) if filename is not None else ())
        + _evidence_items(observations),
        # P6 holds no conflict record of its own; §3.7's competing-value case is
        # settled by the ranking before a model is asked, so a file that reaches
        # here has none to declare.
        conflicts=(),
        model_call_request=ModelCallRequest(
            stage=FACT_STAGE,
            target=Target(file_ids=(request.file_id,), group_id=None),
            model_target=model_target,
            # THE FILENAME LEADS, and it is the sixth kind going through the door
            # built for it. `releasable_observations` drops every `filename`-zone
            # observation and is right to: one arriving as an `Excerpt` is this kind
            # reaching the model where §7.3's protected-records ban does not apply,
            # which `privacy.vocabulary` says in those words. What was missing is
            # the OTHER half of that sentence -- nothing constructed the `Filename`
            # item the ban DOES cover, so the name reached the model through no door
            # at all. `gate._precheck_items` passes `allow_unratified=True` for the
            # express purpose of admitting this and refusing it as
            # `ProtectedItemRequested` on a protected file; that refusal is now
            # reachable instead of moot.
            #
            # Measured on the owner's 199 files: `filename` and `path` are the only
            # two zones present on ALL of them, and for a file like
            # `Desktop/Python 1006/homework0.py` the model otherwise sees two
            # metadata rows -- while the word `homework` sits in the field it never
            # receives. A `file_id` and never a name: §6 says requests carry
            # references, and `Filename` itself refuses an id holding a separator.
            requested_items=((
                Filename(file_id=request.file_id,
                         observation_key=filename.evidence_ref),
            ) if filename is not None else ()) + tuple(
                Excerpt(
                    observation_key=observation.observation_key,
                    span=observation.location.text_span,
                    reason="a reading of this file the fields may rest on",
                )
                for observation in observations
            ),
            prompt_template_id=prompt.template_id,
            prompt_fingerprint=prompt_fingerprint(prompt),
            max_dossier_tokens=max_dossier_tokens,
        ),
        # Null at A and B (`records._require_plan_version`): a fact is about a file
        # version and not about a plan, and the same fact survives a re-plan.
        plan_version=None,
        evidence_snapshot_id=None,
    )


def fact_dependencies(
        authorities: FactCallAuthorities) -> FactValidationDependencies:
    """The C-5 trio this deployment answers, in ONE spelling.

    A live call and `104` R-127's re-judgement of a stored one must be judged by
    the same three callbacks, and `judgement_version` digests exactly this bundle.
    Built twice from the same authorities it would still be the same functions --
    but the day a fourth callback is added, one of the two spellings would get it
    and the other would not, and the version would then describe a validator that
    is not the one that ran.
    """
    return FactValidationDependencies(
        normalize=authorities.normalize,
        contradicts=authorities.contradicts,
        normalize_for_review=authorities.normalize_for_review)


def _call_dependencies(
    request: FactRequest,
    allowed_vocabulary: Sequence[str], *,
    folder_levels: Sequence[FolderLevel],
    authorities: FactCallAuthorities,
    observations: Sequence,
) -> CallDependencies:
    """`observations` is the list the request was BUILT from, and it is here so that
    §8.6's first ladder rung is measured rather than asserted (`103` C7).

    Measured on the raw values rather than on the released ones, because the ladder
    runs before `gate.release` -- `run_call` plans the reduction, then reserves, then
    releases -- so the redacted text does not exist yet. Redaction only ever
    shortens (`apply_redaction` refuses a transform that returns its input), so the
    pre-call number is at or above what the door will measure, and the two therefore
    agree about every dossier either would refuse.
    """
    return CallDependencies(
        proposal_class=PROPOSAL_CLASS,
        basis_key=request.content_hash,
        learning_scope=LEARNING_SCOPE,
        learning_subject_id=request.file_id,
        evidence_resolver=authorities.evidence_resolver,
        site_dependencies=SiteDependencies(
            fact=FactSiteDependencies(
                fact_request=request,
                fact_dependencies=fact_dependencies(authorities)),
            placement=None, residual=None, template=None),
        contradicts=authorities.contradicts,
        # MEASURED, not asserted. This was the literal `True`, which told §8.6's
        # ladder that every dossier ever built fits -- including the 45,843-byte one
        # `104` §5 measured on the owner's own files. A ceiling nothing compares
        # against is not a ceiling, and `00`:257 asks for the opposite of a silent
        # pass: "A model prompt that exceeds its token budget should not truncate
        # silently in a way that removes the decisive evidence."
        #
        # The other three rungs stay honestly absent. `00`:257 offers four remedies
        # -- summarize deterministic facts, preserve anchor excerpts, split the task,
        # or defer -- and this deployment can build none of the first three: the
        # dossier is already the capped observation set, and there is no second,
        # smaller shape of it. Claiming a rung nothing can produce would make
        # `plan_reduction` choose a shape `_units` cannot return. So when the first
        # rung fails, the fourth is what is left, and `plan_reduction` takes it:
        # `DEFERRED`, with a `PreCallAbstention` carrying `BUDGET_EXHAUSTED`, before
        # `reserve_call` and before `gate.release`, so a deferred call spends no
        # budget and mints no release. That is `00`:259's "mark the deferred stage,
        # and leave the file in review rather than guessing".
        unreduced_fits=dossier_tokens(
            observation.raw_value for observation in observations
        ) <= authorities.max_dossier_tokens,
        summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        scan_budget=authorities.scan_budget,
        estimated_cost=authorities.estimated_cost,
        actual_cost=authorities.actual_cost,
        allowed_vocabulary=tuple(allowed_vocabulary),
        # The SAME tuple the vocabulary above was ordered by, not a second read of
        # the library: two answers here would print one order and validate another.
        # It is the OPEN subset, so every level shown names a field still on offer.
        folder_levels=folder_levels,
        policy_version=authorities.policy_version,
        wire_handle_key=authorities.wire_handle_key,
    )


def _policy_content(conn: sqlite3.Connection, policy_version: str) -> str:
    """The policy IN FORCE, by what it says rather than by which row it is.

    `00`:44 puts the policy among the cache key's terms. Keyed on the version STRING
    the cache could never hit once, and that is measured rather than argued:
    `privacy.policy._persist` mints `policy-{uuid4().hex}` on every call, and
    `cli._model_fact_pass` sets a policy at the start of every run, so two runs under
    an identical policy carry two version ids. Two runs measured on one corpus:
    `policy-44204e77...` and `policy-47123308...`, same mode, same grants, same
    redaction settings.

    So the dimension is the CONTENT: mode, grants, redaction settings, move
    permissions, suspended kinds and the plan the policy belongs to. `policy_version`
    and `set_at` are left out because they are the two that move without the policy
    changing. A policy that really does change -- consent withdrawn, a redaction
    setting raised -- changes this string and invalidates every answer under it,
    which is the half of `00`:44 that matters.
    """
    policy = policy_at(conn, policy_version)
    return canonical_json({
        "automatic_move_permissions": dict(policy.automatic_move_permissions),
        "consent_grants": [list(pair) for pair in policy.consent_grants],
        "operation_mode": policy.operation_mode,
        "plan_version": policy.plan_version,
        "redaction_settings": dict(policy.redaction_settings),
        "suspended_item_kinds": sorted(policy.suspended_item_kinds),
    })


def call_identity_dimensions(
    conn: sqlite3.Connection, *,
    file_id: str,
    content_hash: str,
    observations: Sequence,
    authorities: FactCallAuthorities,
) -> dict[str, object]:
    """`00`:44's cache key for one A_fact call, term by term.

    > "Each extraction result is tied to the content hash and the exact process that
    > produced it. The cache key includes content hash, extractor version, analysis
    > tier, model identifier when relevant, and prompt fingerprint for model-derived
    > results. This prevents stale results from surviving a content rewrite, avoids
    > unnecessary work when a file is merely renamed, and makes model or prompt
    > changes auditable."

    Every term is read from something the call is actually built from, so a dimension
    cannot say one thing while the call does another:

      * `content_hash` is the file VERSION. A rewrite invalidates; a rename does not,
        which is the second sentence's own promise.
      * `extractor_versions` is the `(name, version)` of every observation this call
        would carry -- the "exact process that produced it", read off the evidence
        rather than off a constant, so an upgraded reader invalidates the answers
        that rested on its output and no others.
      * `model_id` is the target the gate is asked about and the client sends to.
      * `prompt_fingerprint` covers the template, its id, the response schema and the
        shaping policy, so any of them moving re-asks. §8.6's "analysis tier" is
        inside it: `PromptDefinition.call_site` and `call_site_version` are two of the
        six terms `fingerprint.prompt_fingerprint` hashes.
      * `schema_id` is the situation's domain, which decides the field allowlist.
      * `policy` is the policy's content -- see `_policy_content`.
      * `plan_version` is `None` here and is carried anyway, for the reason
        `store.CALL_IDENTITY_DIMENSIONS` gives.
    """
    return {
        "call_site": A_FACT,
        "content_hash": content_hash,
        "extractor_versions": sorted(
            {(observation.extractor_name, observation.extractor_version)
             for observation in observations}),
        "model_id": authorities.model_target.model_id,
        # Null at A, and `build_fact_request` says why in its own words: "a fact is
        # about a file version and not about a plan, and the same fact survives a
        # re-plan". Read from the same place rather than restated, so the two cannot
        # disagree about a call that is about to be built.
        "plan_version": None,
        "policy": _policy_content(conn, authorities.policy_version),
        "prompt_fingerprint": prompt_fingerprint(authorities.prompt),
        "schema_id": sorted(
            signal.schema_id for signal in authorities.activation_signals.signals),
        "subject_ref": file_id,
    }


#: What one supersession says it was, in `llm_verdict_supersession.reason`.
#: `104` R-127, `105` §14.7's words: the response is unchanged and the judgement
#: of it is not, so the reason names the judgement and not the answer.
REVALIDATED: str = "re-validated under {version}"


def _reuse_is_current(conn: sqlite3.Connection, prior, *, request: FactRequest,
                      vocabulary: Sequence[str],
                      authorities: FactCallAuthorities) -> bool:
    """Are the prior's verdicts a judgement THIS validator would still make?

    `104` R-127 / `105` §14.7: *"validator or normalisation changes must
    re-evaluate cached responses rather than retain obsolete verdicts"*. The reuse
    identity carries the prompt and the schema fingerprints and says nothing about
    the code that judged the answer, so a verdict written before R-119 taught the
    validator that an empty value is an abstention, or before R-98 taught it that a
    course title is a candidate rather than a refusal, went on suppressing the
    question under a conclusion the validator no longer reaches.

    **Re-judged, not re-asked, and the identity is untouched.** Adding the version
    to `CALL_IDENTITY_DIMENSIONS` would have been the shorter change and it would
    have bought the same model answer a second time for every validator edit --
    the dimension comment says what the key is for, and the answer is not what
    changed. The stored response is the model's; only the reading of it moved. So
    nothing here calls a model, and `True` from this function means the prior's
    conclusions are the current validator's own.

    **When it answers `False` the caller asks again**, and every one of those is a
    case where this deployment cannot honestly re-read the bytes:

    * no stored response -- the identity was recorded for a dossier whose answer is
      not in this database (a seeded run that copied verdicts and not responses, a
      row from before responses were kept). Nothing to re-judge.
    * the dossier row will not rebuild, or rebuilds to different bytes than the
      ones it is addressed by. `dossier_id` is the content address of the
      MODEL-VISIBLE bytes and those carry handles keyed by a per-database secret
      (`cli.wire_handle_key_for`, "minted once per database"), so a database that
      inherited another's responses -- which is exactly what `104` R-123's
      `--reuse-answers-from` builds -- holds bytes this run cannot resolve. Judged
      anyway, every citation in them would fail to resolve and the run would record
      a fresh rejection for each and reuse THAT. Asking again costs a call and
      tells the truth; the alternative is a wrong answer for free.
    * the re-judgement is `ValidationUnavailable` -- an authority is missing, so
      there is no verdict, so there is nothing to stand on.
    """
    version = judgement_version(fact_dependencies(authorities))
    standing = standing_verdicts(conn, prior["dossier_id"])
    open_fields = set(vocabulary)
    if not any(row["claim_ref"] in open_fields
               and row["validator_version"] != version for row in standing):
        # Either everything standing was written by this exact validator and these
        # exact normalisers, or what was not is about a claim this call is not
        # asking about. A stale verdict on a field nobody has open changes no
        # decision, and re-judging it every run to find that out again would
        # append a supersession per run for nothing.
        return True

    response = last_response(conn, prior["dossier_id"])
    if response is None:
        return False
    dossier = load_dossier(
        conn, prior["dossier_id"], release_id=response["release_id"])
    if dossier is None:
        return False
    if dossier_address(dossier, authorities.prompt,
                       handle_key=authorities.wire_handle_key) != dossier.dossier_id:
        return False

    checked = dispatch(
        conn, dossier, bytes(response["response_bytes"]),
        site_dependencies=SiteDependencies(
            fact=FactSiteDependencies(
                fact_request=request,
                fact_dependencies=fact_dependencies(authorities)),
            placement=None, residual=None, template=None),
        evidence_resolver=authorities.evidence_resolver,
        contradicts=authorities.contradicts,
        model_id=response["model_id"],
        prompt_fingerprint=response["prompt_fingerprint"],
        dossier_builder=DOSSIER_BUILDER,
        release_audit_id=response["release_audit_id"],
        policy_version=dossier.policy_version,
        # A REPLAY WRITES NO SECOND CONSEQUENCE, and `dispatch` says why in its
        # own words: `apply_verdict` writes P6's fact or its `unresolved` row and
        # `write_unresolved` is always an INSERT, so a re-judgement that applied
        # its consequence would record that the model declined twice for one
        # thing it declined once. `pending_fields_for` has already run for this
        # file too, so a consequence written here would move the ground the
        # `vocabulary` below is measured against.
        apply_consequence=False,
        handle_key=authorities.wire_handle_key,
    )
    if isinstance(checked, ValidationUnavailable):
        return False
    verdicts, _report = checked
    if not verdicts:
        return False

    # ONE TRANSACTION, AND A REFUSAL RATHER THAN A CRASH IF IT CANNOT CLOSE.
    #
    # `record_verdict` raises `MalformedRecord` when this address already holds a
    # DIFFERENT conclusion, and there is one way to reach that: the version covers
    # the validator and the deployment's three callbacks, and it does not cover the
    # live authorities they are handed -- `evidence_resolver` answers "does this
    # observation key still resolve in the store", and an observation that has since
    # gone takes check 2's coarse half with it. One version, two conclusions, and
    # the second is not something to write over the first.
    #
    # A run must not end on it. `transaction` rolls back to its savepoint, so
    # nothing is half-recorded, and a re-judgement that cannot be written is a
    # re-judgement this deployment does not have -- which is the same answer as a
    # response it cannot read: ask the question again.
    try:
        with transaction(conn):
            recorded = {}
            for verdict in verdicts:
                # No id is minted here. `validate_fact_proposal` already put the
                # judgement version in the address of every Site A verdict, so a
                # re-judgement arrives at a row of its own and a repeat of one
                # arrives back at the row it wrote -- where `record_verdict`
                # compares the payload and does nothing, which is what makes a
                # run that died between the record and the supersession finish
                # the job on the next pass instead of duplicating half of it.
                record_verdict(
                    conn, verdict,
                    model_id=response["model_id"],
                    prompt_fingerprint=response["prompt_fingerprint"],
                    release_audit_id=response["release_audit_id"],
                    observed_at=authorities.observed_at())
                recorded[verdict.claim_ref] = verdict.verdict_id
            # EVERY standing verdict on the dossier, not only the stale ones and
            # not only the open fields. The response was re-read whole, so every
            # conclusion drawn from it is replaced by the conclusion this
            # validator draws; a row left standing under the old version would
            # put the comparison above back into `False` on the next run and
            # re-judge for ever. A claim the re-judgement no longer names at all
            # -- a stricter parser answering one `schema_invalid` verdict for the
            # whole response -- is superseded by that verdict, which is the
            # truthful link: the response as a whole is now judged differently.
            #
            # A row this validator has ALREADY written is skipped rather than
            # linked to itself, and that is what closes the loop after an
            # ask-again: a run that could not re-judge asked instead and left the
            # old conclusion standing beside the new one, so this pass supersedes
            # the old and leaves the new alone. One run, not a chain.
            fallback = recorded.get(verdicts[0].claim_ref)
            for row in standing:
                new_id = recorded.get(row["claim_ref"], fallback)
                if new_id is None or new_id == row["verdict_id"]:
                    continue
                supersede_verdict(
                    conn, row["verdict_id"], new_id,
                    reason=REVALIDATED.format(version=version),
                    model_id=response["model_id"],
                    prompt_fingerprint=response["prompt_fingerprint"],
                    release_audit_id=response["release_audit_id"],
                    observed_at=authorities.observed_at())
    except MalformedRecord:
        return False
    return True


def fact_call_stage(authorities: FactCallAuthorities):
    """One `facts.resolver.Stage`: the §8.6 `llm` producer, wired to a real model.

    Returns the ids of the facts THIS call wrote, read back by diffing the version's
    fact rows -- `validate_fact_proposal` calls `apply_verdict` and discards the id
    it returns, and a stage that answered `()` would tell `ResolveResult` the model
    contributed nothing while its facts sat on disk.

    It never swallows an exception, for the reason `FactResolver.resolve` gives:
    P6's failures are `ContractViolation`s and a caller that catches one still owes
    P2 an envelope. Every outcome `run_call` can RETURN -- a refusal, an abstention,
    a call failure, an unavailable validation -- is already a record on disk by the
    time it comes back, and is handed to `on_result` for counting.
    """

    def stage(conn: sqlite3.Connection, file_id: str,
              content_hash: str) -> tuple[str, ...]:
        pending = pending_fields_for(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals)
        if not pending:
            return ()
        observations = releasable_observations(
            conn, file_id=file_id, content_hash=content_hash,
            limit=authorities.max_released_observations)
        if not observations:
            return ()
        request = build_request(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals,
            normalizers=authorities.normalizers)
        if not request.allowlist:
            return ()

        # What is still open on THIS file, in the order the tree is built in. A
        # subset of `request.allowlist`, which is what check 1 measures the answer
        # against, so nothing offered here can be rejected for being out of schema.
        vocabulary, visible_levels = open_question(
            pending, authorities.folder_levels)

        # `104` R-13, AND IT IS HERE FOR ONE REASON: everything after this line
        # costs. `run_call` reserves a budget slot, `gate.release` mints an audit
        # row and a single-use capability, and `transport.issue` spends it. A
        # lookup keyed on `dossier_id` -- the obvious key, and a stable one since
        # R-58 -- could not run here at all: that address hashes `released_evidence`
        # and so exists only AFTER the release is minted and the slot is taken. So
        # the key is the identity of the question's CONTEXT, computed from the same
        # inputs that determine the dossier, and the prior's `dossier_id` is stored
        # on the row so a reuse names the answer it is reusing.
        identity = call_identity_dimensions(
            conn, file_id=file_id, content_hash=content_hash,
            observations=observations, authorities=authorities)
        identity_id = call_identity(identity)
        prior = prior_call(conn, identity_id)
        if prior is not None and vocabulary and _reuse_is_current(
                conn, prior, request=request, vocabulary=vocabulary,
                authorities=authorities):
            # `104` R-127 STANDS BEFORE `answered_fields` AND NOT AFTER IT, because
            # what it changes is which verdicts are standing. A re-judgement
            # supersedes the conclusions it replaces, and `answered_fields` reads
            # only the non-superseded rows -- so asking "is every open field
            # answered" first would answer it against the judgement this validator
            # has just stopped making.
            answered = answered_fields(conn, prior["dossier_id"])
            if set(vocabulary) <= answered:
                # EVERY field still open was already ANSWERED under this exact
                # identity. Asking again buys the same answer and spends a call for
                # it -- measured on a two-file corpus, 2 calls on the first run and
                # 2 more on an unchanged second, for 6 repeated abstentions.
                #
                # ANSWERED, NOT DECLINED, and `104` R-109 is the difference. The
                # comparison was against the ABSTENTIONS alone, so a field the model
                # answered and the validator REJECTED counted as unanswered: no fact
                # was written, the field came back open, and the next run asked the
                # identical question under the identical identity for the identical
                # rejection. On the owner's resumed run every verdict but a handful
                # was a reject, and `llm_call_reuse` stayed at 0 while 120 recorded
                # responses went unconsulted. `answered_fields` says which outcomes
                # count and which states record no answer at all.
                #
                # The `vocabulary` guard keeps an EMPTY offer on the path it is
                # already on: a call that offers the model nothing is a different
                # defect and reusing an answer for it would hide one behind the
                # other.
                record_call_reuse(
                    conn, identity_id=identity_id,
                    prior_dossier_id=prior["dossier_id"], call_site=A_FACT,
                    subject_ref=file_id, reused_fields=vocabulary,
                    observed_at=authorities.observed_at())
                return ()

        before = {row["fact_id"] for row in facts_for_file(
            conn, file_id, content_hash)}
        # `104` R-O. The `try` covers the BUILDER as well as the call, and that is
        # the whole reason it is here rather than only inside `run_call`:
        # `build_fact_request` constructs the `ModelCallRequest` whose
        # `__post_init__` raises `MalformedRequest`, and it builds the spans the
        # gate later resolves. Both raised on the owner's corpus, from an argument
        # expression `run_call` never sees.
        #
        # ONE FILE, NOT THE RUN. The stage returns the facts this file already has
        # and the loop asks about the next one; nothing is written that would stop
        # the next run asking again, because the identity below is recorded only
        # for a verdict.
        try:
            result = run_call(
                conn,
                build_fact_request(
                    request, observations,
                    filename=filename_citation(conn, file_id),
                    model_target=authorities.model_target,
                    prompt=authorities.prompt,
                    max_dossier_tokens=authorities.max_dossier_tokens),
                gate=authorities.gate,
                model_client=authorities.model_client,
                prompt=authorities.prompt,
                validation_dependencies=_call_dependencies(
                    request, vocabulary, folder_levels=visible_levels,
                    authorities=authorities, observations=observations),
                observed_at=authorities.observed_at,
                # `104` R-14. Handed to `run_call` and not to `CallDependencies`:
                # it is optional, and that bundle's every field is required by
                # construction.
                usage_recorder=authorities.usage_recorder,
            )
        except REFUSAL_EXCEPTIONS as refusal:
            result = refusal_outcome(
                conn, call_site=A_FACT, subject_ref=file_id, error=refusal,
                observed_at=authorities.observed_at())
        if isinstance(result, P8Verdict):
            # ONLY on a verdict, and the exclusions are the point. A refusal, a
            # call failure and a `ValidationUnavailable` are all states where no
            # model answered this question, and remembering one as an answer would
            # turn a transient failure -- a denied release, a provider that hung up
            # -- into a permanent silence about the file. Those must be retried on
            # the next run, which is what writing nothing here means.
            #
            # A PRE-CALL ABSTENTION IS THE ONE THAT SLIPS THROUGH THIS TEST, and it
            # is excluded a step later instead. `harness._persist_abstention` RETURNS
            # a `P8Verdict`, so an exhausted budget or a suppressed subject writes a
            # row here -- addressed to `pre_call_address`, which `vocabulary` shapes
            # so it "cannot be mistaken for, or joined to" a dossier. It carries no
            # `llm_verdict` row, so `answered_fields` reads `frozenset()` off it and
            # the next run asks, which is the same answer by a different route.
            # MEASURED: a first pass with a zero budget leaves two identity rows
            # addressed `pre-call:A_fact:<file>`, the pass after it asks both files,
            # and the pass after that reuses -- so the row costs nothing, because a
            # reuse is decided BEFORE the budget is reserved and a complete prior
            # answer is therefore never standing behind one of these.
            record_call_identity(
                conn, identity_id=identity_id, dossier_id=result.dossier_id,
                call_site=A_FACT, subject_ref=file_id, dimensions=identity,
                observed_at=authorities.observed_at())
        if authorities.on_result is not None:
            authorities.on_result(file_id, result)
        return tuple(row["fact_id"] for row in facts_for_file(
            conn, file_id, content_hash) if row["fact_id"] not in before)

    return stage
