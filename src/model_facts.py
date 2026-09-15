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

**The four states in which no call is built**, each because the alternative is
worse than not asking, and each NAMED since `104` §18.2 gap 4 (9 Sep 2026):

  * nothing pending -- every field the schema allows is already settled, so the
    question has no content and the spend buys a repetition of what is known;
  * no route -- neither gate permits this file a model, which is a fact about the
    person's policy and about this file's class;
  * nothing releasable -- either P5 read nothing at all, or every observation is in
    an always-local zone, is unbounded, or was signalled sensitive, so the dossier
    would be empty and the model would be asked to answer from nothing;
  * no allowlist -- no domain activated and no universal field remains, so §3.5's
    closed vocabulary is empty and every answer would be out of schema.

**Each of them used to return a bare `()`, and that was the defect.** No call, no
`unresolved` row, and `FactResolver` then appended `llm` to `stages_run` because it
recorded the stage's INVOCATION rather than its outcome -- so the run reported the
file as one a model had been asked about and had had nothing to say. §13.1's bar and
the constitution's second rule both say the opposite: what is skipped is counted and
NAMED, never silently omitted. Each now returns a `facts.resolver.StageOutcome`
carrying one of the words in `NOT_ASKED_REASONS` and the P6 `unresolved` reason it
owes a row under; the resolver writes one row per pending field and publishes the
word in `ResolveResult.stages_not_asked`, and `cli._print_fact_pass` prints "not
asked" with the sentence that word earns. The reason vocabulary is P6's own and this
module mints no member of it.

The refusals that are decided BEFORE the stage is reached -- the privacy bar and the
budget bar -- still belong to `FactResolver`, which writes them through the same
writer, and to `Gate`, which records its own.
"""
from __future__ import annotations

import json
import sqlite3

from readers import model_deepseek
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
# `104` R-175: the per-file ceiling's default clock, aliased at the import so the
# dataclass default is the FUNCTION and not a call of it, and so a test that
# injects its own clock is replacing something with a name.
from time import monotonic as _monotonic
from types import MappingProxyType
from typing import Any

from database_agent.budget import CEILING_KEYS, get_ceiling
from database_agent.db import transaction
from evidence_shape.canonical import canonical_json
from evidence_shape.locator import (
    location_from_mapping, serialize_container_path, serialize_locator,
)
from evidence_shape.store import (
    DERIVED_NAMESPACE, opening_reading_for, record_observation,
    unit_length_for_observation,
    unit_stands_at,
)
from facts.domains import (
    ActivationSignals, active_domains, active_field_allowlist,
)
from facts.file_facts import LLM_INTERPRETATION, facts_for_file
from facts.evidence import observations_for_version
from facts.llm_seam import FactRequest, build_request
from facts.resolver import StageOutcome
from facts.states import (
    EXCLUDED_STATE,
    LLM_SUPPORTED as LLM_SUPPORTED_STATE,
    is_stronger,
)
from facts.unresolved import (
    FIELD_NOT_IN_ACTIVE_SCHEMA, NO_CANDIDATE_EVIDENCE, PRIVACY_WITHHELD,
)
from llm_harness.budgets import ScanBudget
from llm_harness.dossier import dossier_address, released_item_wire_bytes
from llm_harness.fact_validation import FactValidationDependencies, judgement_version
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.harness import CallDependencies, drive_inline, run_call_steps
from llm_harness.records import (
    REFUSAL_EXCEPTIONS,
    Conflict, DossierRequest, EvidenceItem, FolderLevel, MalformedRecord, P8Verdict,
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
from llm_harness.vocabulary import (
    A_FACT, CONTEXT_SUPPORTED, DIRECT_ANCHOR, REMAINS_AMBIGUOUS,
)
from privacy.gate import Gate
from privacy.policy import policy_at
from privacy.redaction import span_address
from privacy.items import Excerpt, Filename, sensitive_observation_keys
from privacy.resolve import (
    AmbiguousObservationKey, UnresolvableSpan, current_location,
    filename_address,
)
from privacy.release import (
    ModelCallRequest, ModelTarget, Target,
)
from privacy.vocabulary import (
    ALWAYS_LOCAL_ZONES, ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET, CLOUD_LOCALITY,
    LOCALITIES,
)

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

#: WHY THE FACT STAGE DID NOT ASK ABOUT A FILE (`104` §18.2 gap 4, 9 Sep 2026).
#:
#: The stage has four ways to return before a call is built, and until this ruling all
#: four returned a bare `()`: no call, no `unresolved` row, and `FactResolver` then
#: appending `llm` to `stages_run` because it recorded the stage's INVOCATION. The run
#: told a person the model had been asked about the file and had had nothing to say,
#: which §13.1's bar and constitution rule two both forbid -- what is skipped is
#: counted and NAMED.
#:
#: One word per state, and the states are kept apart because the sentence a person is
#: owed differs for each. "Nothing about this file could be read" is about the reader;
#: "everything readable about it is in an always-local zone or was signalled
#: sensitive" is about the privacy rules; "no model may see this file" is about their
#: policy; "the schema left no field to ask" is about the situation they chose. One
#: bucket would say the wrong one of those four to three files out of four.
NOT_ASKED_SETTLED: str = "every_field_already_settled"
NOT_ASKED_NO_ROUTE: str = "no_model_route"
NOT_ASKED_NOTHING_READ: str = "nothing_was_read"
NOT_ASKED_ALL_REFUSED: str = "every_reading_refused"
NOT_ASKED_NO_SCHEMA: str = "no_field_in_active_schema"

#: THE `unresolved` REASON EACH WORD OWES A ROW UNDER, from P6's own closed
#: vocabulary and never a new member of it: this stage names a state, it does not mint
#: a reason. `FactResolver._write_bars` writes one row per pending field under the
#: reason named here, which is the same obligation and the same writer the privacy and
#: budget bars already use.
#:
#: `NOT_ASKED_SETTLED` maps to `None` and that is not an omission: there is no pending
#: field left to write a row about, so a row would have no field to name. The state is
#: still recorded -- `ResolveResult.stages_not_asked` carries the word -- and it is the
#: one of the five that is not a gap in coverage but the answer "this file is done".
NOT_ASKED_REASONS: Mapping[str, str | None] = MappingProxyType({
    NOT_ASKED_SETTLED: None,
    NOT_ASKED_NO_ROUTE: PRIVACY_WITHHELD,
    NOT_ASKED_NOTHING_READ: NO_CANDIDATE_EVIDENCE,
    NOT_ASKED_ALL_REFUSED: NO_CANDIDATE_EVIDENCE,
    NOT_ASKED_NO_SCHEMA: FIELD_NOT_IN_ACTIVE_SCHEMA,
})


def _not_asked(word: str) -> StageOutcome:
    """The stage declining to ask, with its reason, as `FactResolver` reads it.

    One spelling of the pair, so a state cannot be named in the outcome and left out
    of the rows: the word and the `unresolved` reason are read from one mapping.
    """
    return StageOutcome(not_asked=word, unresolved_reason=NOT_ASKED_REASONS[word])

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
                  folder_levels: Sequence[FolderLevel] | None,
                  settled: Sequence[str] = (),
                  ) -> tuple[tuple[str, ...], tuple[FolderLevel, ...]]:
    """What this file is ASKED: the vocabulary to offer, and the levels to show.

    **THE SETTLED LEVEL FIELDS ARE ASKED TOO, AND THAT IS `104` §18.2 GAP 1.**
    `00`:42's amendment of 2026-09-05 rules that every contradiction check *including
    the precedence of rule facts over model facts* "is shown to the model as a flag
    with its evidence, and the model reconciles". This function used to do the
    opposite: it dropped a field a rule had settled out of the question entirely, so
    the model was never given the chance the ruling reserves for it. Measured on r15:
    16 `subject` facts and 17 `work_type` facts on labelled coursework were written by
    a regex and shown to no model, and three of them disagreed with the label. The
    field that decides where the file goes was decided by a pattern, silently.

    So a settled level field is offered again, and it is offered WITH ITS FLAG:
    `rule_conflicts` builds one `Conflict` per settled field naming the field and the
    reading the rules settled it from, and the model may confirm it or contradict it
    with evidence of its own. A contradiction is no longer a rejection either --
    `llm_harness.fact_validation` records it `requires_review` and the resolver writes
    it `possible` beside the rule's fact, which is `00`:42's other half.

    **What the OLD argument was, and what is left of it.** It was that a claim spent
    on a settled field is a claim thrown away, because check 4 rejected it; and that
    one malformed claim destroys every claim in the answer (the ratified rule 11), so
    every question that cannot pay is another chance to lose the ones that can. The
    first half is now false by construction: check 4 no longer rejects, so the claim
    is not thrown away -- it becomes a proposal beside the rule's value or a
    confirmation of it. The second half stands and is the cost this gap accepts on the
    owner's ruling: a longer question is a larger surface for rule 11. It is bounded
    the same way the rest of the question is, by the situation's own folder levels --
    a settled field that is not a LEVEL is still not asked, because it decides no
    folder and would buy nothing for the risk.

    **The subset direction is the safe one and it is still the only one taken.** Check
    1 measures a proposal against `FactRequest.allowlist`, the full active schema.
    `settled` comes from `settled_fields_for`, which reads the same
    `active_field_allowlist` `pending_fields_for` reads, so everything offered here is
    inside that and nothing the model is told it may propose can be rejected for not
    being in the active schema -- which is the failure `pending_fields_for` warns
    about, and it happens in the other direction.

    **The two halves do not cover the allowlist, and the hole is deliberate.** A field
    held only by a `possible` or `llm_supported` fact is in neither: it is a model's
    own earlier answer, or gap 3's proposal standing in front of a PERSON, and
    `00`:298's *"proposed once"* is only true while the field stays closed to this
    question. `settled_fields_for` says why in full. Nothing here has to know: it
    offers what it is given.

    A level whose field is neither pending nor settled is dropped from the shown list,
    and that keeps the projection exact: `dossier._folder_levels_body` refuses a level
    naming a field the vocabulary does not carry. `()` here is truthful -- this file
    has no folder level to ask about -- and it is not the empty list
    `require_folder_levels` refuses, which is about a deployment that never read the
    library at all.

    **`settled` DEFAULTS TO EMPTY, and that is a caller stating a fact rather than a
    shape appearing.** A caller that passes none is asking only what is open, which is
    exactly what this function did before gap 1; the production stage passes the
    settled set, and a test that wants the old question can still ask it.
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
    #:
    #: `None` IS THE NO-SITUATION STATE and takes the arm below the concatenation.
    # PENDING FIRST, THEN SETTLED, and the order is not decoration. A field nothing
    # holds is the question the call exists for; a field the rules already answered is
    # the one being re-opened. `order_vocabulary_by_levels` re-orders this by the
    # tree's nesting anyway, so the concatenation decides only what happens to two
    # fields at the same level -- and asking the open one first is the honest shape of
    # the question. `dict.fromkeys` keeps a field that is somehow in both lists once:
    # `pending_fields_for` and `settled_fields_for` partition the allowlist, so it
    # cannot happen from the production caller and a duplicate from any other would be
    # a field asked twice in one vocabulary.
    asked = tuple(dict.fromkeys(tuple(pending) + tuple(settled)))
    if folder_levels is None:
        # **NO SITUATION IS CHOSEN, SO THE SCHEMA'S OWN QUESTION IS THE QUESTION**
        # (13 Sep 2026). The narrowing below is the SITUATION's -- "the valid
        # options are the situation's OWN" -- and there is no situation to narrow
        # by: `branch_situation.the_one_situation` refuses to pick one of the
        # eight the library carries under `research`, and the person has not yet
        # said which. `None` is `FactCallAuthorities.folder_levels`' own word for
        # that state and it is the ONE input that reaches this arm; `()` is still
        # refused at `__post_init__`, so the SILENT flat-vocabulary question the
        # narrowing exists against -- a deployment that never read the template
        # library -- is still impossible.
        #
        # It is the flat question, and that is the trade the owner made rather
        # than one taken here: measured, a file whose schema the judge had read
        # correctly and whose situation was open was asked NOTHING, and its facts
        # column came out empty. The fields are the schema's and the schema is
        # known; only the folders wait for the answer. No level is shown, because
        # there is no level -- `dossier._folder_levels_body` emits `[]` for that
        # and says so.
        return order_vocabulary_by_levels(asked, ()), ()
    level_fields = {level.field for level in folder_levels}
    open_fields = set(asked) & level_fields
    offered = tuple(field for field in asked if field in open_fields)
    visible = tuple(level for level in folder_levels if level.field in open_fields)
    return order_vocabulary_by_levels(offered, visible), visible


@dataclass(frozen=True)
class AnchorOnlyLevels:
    """The levels asked of an ANCHOR and of no other file (`105` §14.4, `104` R-131).

    `104` §11.2 step 2 withdrew `school` from the per-file question outright, and
    `104` R-102 is what that cost: nothing writes a `school` fact any more, so no
    corpus grows a school level at all. The owner's ruling of 7 Sep restores the
    question to the files that can answer it -- "Answer school only when a
    permitted anchor establishes the institution's relevant relationship to the
    course or enrollment being organized" -- and leaves it withdrawn everywhere
    else.

    **Anchor kind is necessary and it is not sufficient**, which is §14.4's own
    sentence and the reason this record carries a kind rather than a verdict: a
    transcript may name transfer institutions and a syllabus released by another
    university does not establish attendance, so what the KIND buys is the right
    to be asked, and the prompt decides the answer -- the drafted rule 12 of
    `tools/promptbench/drafts/a_fact_template.v2.txt`, which is the owner's to
    ratify and which nothing loads. Nothing here reads a value.

    **The kind is the file's own settled kind and never the model's.**
    `anchor_only_levels` reads it off `FactRequest.existing_facts`, which
    `facts.llm_seam.build_request` has already computed as every ACTIVE fact
    stronger than an LLM conclusion -- so the kind behind the question is
    `validated`, `direct` or `user_confirmed`, and a model's own guess about what
    a file is can never open the question about it. No second read and no second
    definition of "validated".

    **The protected half is the route's answer, asked again here rather than
    respelled.** §14.4 binds this to §14.3: "a tuition or housing statement
    classified protected cannot become model-eligible because it is also an
    anchor". This deployment already bars a protected file from every model on
    every locality (`cli.model_route_permitted`, held by
    `tests/integration/test_local_model_fact_pass.py::
    test_a_protected_file_is_never_sent_to_the_local_model_either`), so the flag
    is READ through that same predicate -- one function, two call sites -- and
    P7's classification is not re-derived here. A second spelling of the gate's
    rule beside the gate's rule is how the two came to disagree once already
    (`104` R-02).

    `levels` is a tuple of the situation's own `FolderLevel` records, split off by
    the composition root from the levels it withholds; `kind_field` and
    `anchor_kinds` are the deployment's, drawn from the shipped recognition
    release. This module authors none of the three.
    """

    levels: tuple[FolderLevel, ...]
    kind_field: str
    anchor_kinds: frozenset[str]
    may_reach_a_model: Callable[[str], bool]

    def __post_init__(self) -> None:
        if not self.levels:
            raise ValueError(
                "an anchor-only rule with no level withholds nothing and restores "
                "nothing; a deployment that asks every file the same question "
                "supplies no rule at all rather than an empty one")
        # The same check the every-file list gets, from the same function: these
        # levels reach `open_question` beside those, and a mapping here would be a
        # caller authoring a label exactly as it would there.
        object.__setattr__(self, "levels", require_folder_levels(self.levels))
        if not self.anchor_kinds:
            raise ValueError(
                "`105` §14.4 admits a file to the question by its KIND, so a rule "
                "with no anchor kinds can never admit one -- which is the same "
                "silence as `104` R-102 and would be indistinguishable from it")


def anchor_only_levels(request: FactRequest,
                       rule: AnchorOnlyLevels | None) -> tuple[FolderLevel, ...]:
    """§14.4's predicate: the levels this ONE file may be asked, beyond the rest.

    Called with the request the builder has just built, so the kind it reads is
    the one `build_request` already established and not a second reading of the
    store. `()` for every file that is not an anchor of a permitted kind, which is
    `open_question`'s own way of not asking: a level absent from the offered
    vocabulary is a question the dossier never puts.

    The cheap test runs first and it is also the safe one: the kind is already in
    memory, and the classification is read only for a file that would otherwise be
    asked.
    """
    if rule is None:
        return ()
    if _settled_kind(request, rule.kind_field) not in rule.anchor_kinds:
        return ()
    if not rule.may_reach_a_model(request.file_id):
        return ()
    return rule.levels


def _settled_kind(request: FactRequest, kind_field: str) -> str | None:
    """What this file version IS, as its own settled facts say, or `None`.

    `existing_facts` is `build_request`'s own tuple -- active, not excluded and
    stronger than an LLM conclusion -- so this ranks no state and names none. A
    file carrying two live facts at that field is not resolved here: the first is
    taken, and P6's slot had to settle the field before either became a fact.
    """
    for row in request.existing_facts:
        if row["field_key"] == kind_field:
            return row["canonical_value"]
    return None


class FileTookTooLong(RuntimeError):
    """One FILE spent more wall-clock in a pass than the deployment allows it.

    NOT a timeout and not a refusal, and the difference is why it has a name of its
    own. A timeout is about one CALL and `readers.model_ollama.OllamaRanOutOfTime`
    is where it is raised (`104` R-175 part a). This is about a file that has
    already had its turn -- however that time went -- and it exists because a
    per-call deadline still lets one file hold a run: two calls of six hundred
    seconds each is twenty minutes on one file, and a pass that walks 199 of them
    has no other way to notice.

    It is recorded through `store.refusal_outcome`, which is the same path a
    `MalformedRequest` from the builder takes, so the outcome is one the report and
    the scoreboard already read. The point of raising it rather than returning
    quietly: a file skipped in silence is indistinguishable from a file the model
    had nothing to say about, which is `104` R-04's failure exactly.
    """


@dataclass(frozen=True)
class PerFileCeiling:
    """How long one FILE may hold a pass, measured from the first time it is seen.

    **`104` R-175 part b, and it is the second half of one fix.** Part (a) put one
    deadline over a whole local call, so no CALL can run for ever. That is not the
    same as no FILE running for ever: `104` §17.1 and §17.13 have one file asked at
    site G and then at site A within a single pass, so a file's turn is as long as
    the calls it makes, and a deployment whose patience is ten minutes a call gives
    one file twenty. r19 held 199 files behind one of them (§18.22).

    **The number is not chosen here.** `seconds` is injected by whoever composes the
    run, exactly as `refuse_if_busy`'s load ceiling is: this class is mechanism and
    the ceiling is a deployment fact, derived from the local timeout and the call
    sites one file can be asked at. A number this class picked for itself would be a
    policy decided in the wrong place and invisible to whoever changed their mind
    about it.

    **IT MEASURES THE FILE'S OWN TURNS AND NOT THE WALL-CLOCK SINCE IT WAS FIRST
    SEEN, and the difference is the whole correctness of the thing.** The passes
    are SEQUENTIAL over the roster: `_model_fact_pass` asks site G about all 199
    files and only then walks them again at site A. So "seconds since this file was
    first seen" is, by the time the second pass reaches file 1, the length of the
    entire first pass -- hours -- and every file would be over any ceiling worth
    setting. What is charged to a file is the time the run spends WITH it:
    `open_turn` starts its turn, the next `open_turn` (or `close_turn`) ends it, and
    the turns add up. A loop walking files one at a time needs nothing else, and the
    charge covers everything the turn does rather than only the call -- a dossier
    that takes minutes to assemble is exactly as much of a stuck file as a call that
    never returns.

    **THE FACT PASS IS NO LONGER THAT LOOP (`104` §18.15), and the two callbacks
    are how it stays honest.** Its cloud sends go out several at a time, so a batch
    has one wait shared by seven files and then several files' rows written with no
    call in flight at all. `harness.in_walk_order` is handed `close_turn` as its
    `on_pause` and `open_turn` as its `on_resume`: the shared window is charged to
    nobody, and a file whose own call runs alone -- which is every LOCAL file, the
    slow ones this ceiling is for -- has its turn reopened before that call and
    charged for it by the next file's arrival. Nothing about the measurement
    changed; what changed is who is holding the run at each moment, and the pass
    now says so.

    **Nothing is interrupted.** `check` is consulted at the top of each turn and
    raises before any of it is done, so a file already past its ceiling is skipped
    and the loop moves on. It does not cut a call that is in flight -- part (a) is
    what bounds that, and reaching for `signal.setitimer` to cut one would put an
    alarm in a run whose cloud lane is meant to become threaded, where alarms do not
    arrive. So this is the BACKSTOP behind part (a) and is stated as one: with every
    call ending at its own deadline a file's turns cannot reach this ceiling, and
    what it catches is the day that stops being true -- a deadline that fails to
    cover some phase, which is R-175 itself, or work outside a call that will not
    end.
    """

    seconds: float
    #: `time.monotonic` by default, and injectable so a test can hold a file past
    #: its ceiling without spending the wall-clock the ceiling is measured in.
    #: Monotonic and never `time.time`: a wall-clock that steps backwards over a
    #: nine-hour run would make an over-budget file look fresh.
    clock: Callable[[], float] = _monotonic
    #: File id to the seconds the run has already spent with it, summed over every
    #: turn it has had. Mutable inside a frozen record because the ceiling is the
    #: policy and this is the measurement the policy is applied to.
    spent: dict[str, float] = field(default_factory=dict)
    #: The turn now open, as `[file_id, started_at]`, or empty. A list because the
    #: record is frozen and this is the one thing about it that moves.
    open_turn_cell: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.seconds, (int, float)) or isinstance(
                self.seconds, bool) or self.seconds <= 0:
            raise ValueError(
                f"a per-file ceiling is a positive number of seconds and "
                f"{self.seconds!r} is not one. Zero is not a ceiling; it is a run "
                f"that skips every file while reporting that it asked.")

    def open_turn(self, file_id: str) -> None:
        """Start this file's turn, charging the previous one for the time it took.

        Called at the top of a per-file loop's body, which is the one position that
        needs no `with` and survives every `continue` in it: a loop that walks files
        one at a time has exactly one turn open, and the next file's arrival is the
        previous file's end.
        """
        now = self.clock()
        self.close_turn(now=now)
        self.open_turn_cell[:] = [file_id, now]

    def close_turn(self, *, now: float | None = None) -> None:
        """End the open turn, if there is one. Idempotent, and safe to leave unsaid.

        A pass that forgets to call this leaves its last file's final turn uncharged
        -- which under-counts one file and never over-counts one, so a forgotten
        close cannot invent a skipped file.
        """
        if not self.open_turn_cell:
            return
        file_id, started = self.open_turn_cell
        moment = self.clock() if now is None else now
        self.spent[file_id] = self.spent.get(file_id, 0.0) + (moment - started)
        self.open_turn_cell.clear()

    def check(self, file_id: str) -> None:
        """Raise if this file has already had more than its share of the run."""
        already = self.spent.get(file_id, 0.0)
        if already > self.seconds:
            raise FileTookTooLong(
                f"this file has already held the run for {already:.0f} seconds "
                f"against a ceiling of {self.seconds:.0f}, so it was not asked "
                f"again and the run moved on. `104` R-175: one file that will not "
                f"finish is not allowed to be the whole corpus's wait. What is left "
                f"open here is open, not answered -- the next run asks it again.")


def _one_route_pair(client: ModelClient,
                    target: ModelTarget) -> tuple[ModelClient, ModelTarget]:
    """The pair, checked to be one destination and not two descriptions of it.

    The gate is asked about `model_target` and the transport sends to
    `model_client.model_target`; two values here would authorise one destination
    and deliver to a different one. `test_live_path` names the same rule at site
    B. Checked at construction for the single-pair spelling and at every read for
    the per-file one, because a route that returns a mismatched pair for one file
    is exactly as wrong as a mismatched field and there is no earlier moment to
    catch it.
    """
    if client.model_target != target:
        raise ValueError(
            "the gate is asked about `model_target` and the client sends to "
            "`model_client.model_target`; two values here would authorise one "
            "destination and deliver to a different one")
    return client, target


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
    #: THE ONE PAIR, or `None` twice when the route is per file. `104` §17.13
    #: ruling 3 gives one call site two destinations -- the cloud model for the
    #: files the cloud gate permits, the local one for the rest -- so a single
    #: client here cannot describe the run. A deployment with ONE destination
    #: still states it as this pair and `route_for` below is derived from it,
    #: which is why every existing caller is unchanged; a deployment with two
    #: passes `None` to both and supplies `route_for` instead. Exactly one of the
    #: two spellings is in force, checked below: two would be the "authorise one
    #: destination and deliver to another" defect one level up.
    model_client: ModelClient | None
    prompt: PromptDefinition
    model_target: ModelTarget | None
    activation_signals: ActivationSignals
    #: The folder levels of the situation the person named, read off the shipped
    #: template library by the composition root. Required with no default: absent
    #: means refuse, and a call built without them asks the model the flat-
    #: vocabulary question that filled one `work_type` in 199 files.
    #:
    #: **`None` MEANS NO SITUATION IS NAMED FOR THIS RUN**, and it is not `()`
    #: respelled. `--situation` is optional (`00` Amendments of 2026-09-11 item 2)
    #: and a folder whose own evidence names a schema but not one of the N
    #: situations under it has nothing to read levels off. This bundle is still
    #: built, because sites G and H read neither these levels nor
    #: `activation_signals` and both must run before anybody can answer the
    #: question, and `__post_init__` keeps `()` refused so the silent
    #: flat-vocabulary dossier the guard exists against is still impossible.
    #:
    #: **AND AN A_fact CALL IS BUILT FROM IT (13 Sep 2026).** It used to be that
    #: none was -- `pending_fields_for` raised on `None` the moment one was
    #: attempted -- and the cost of that was measured the day
    #: `branch_situation.the_one_situation` stopped resolving a schema to the
    #: alphabetically first of its situations: every file site G named reached the
    #: pass with no situation, and a person whose folder the judge had read
    #: correctly got an EMPTY facts column. The situation decides the folder
    #: LEVELS and the template; the FIELDS are the schema's, and the schema is
    #: known. So the levels are absent, the anchor levels are absent, and the
    #: file is asked its schema's own question -- which is what the
    #: `allowed_vocabulary` was always computed from. `pending_fields_for` reads
    #: `or ()` at the two places that walk them and says so at the first.
    folder_levels: tuple[FolderLevel, ...] | None
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
    #: `104` R-135. `(conn, file_id, content_hash, fields) -> Sequence[Observation]`:
    #: readings of OTHER files this call may show as context, or `()`. The composition
    #: root's, entirely -- which neighbours speak for a file, which field their words
    #: answer, and which of them privacy allows are three deployment questions and this
    #: module answers none of them. `cli.anchor_context_observations` is this
    #: deployment's answer and it says why each of its narrowings is structural.
    #:
    #: `None` is not a stub: a deployment that offers no context is a real deployment,
    #: and every site-A call it makes is exactly the call it made before this field
    #: existed. The consequence of supplying one is visible rather than silent -- the
    #: target gains the stating file's id, the gate classifies it, and a fact resting
    #: only on a neighbour's words is `ACCEPT_CONTEXT_SUPPORTED` and carries a review
    #: obligation.
    anchor_context_for: Callable[..., Sequence] | None = None
    #: `104` R-145. The same offer as `anchor_context_for`, in §8.6's PRESERVED
    #: ANCHORS shape: each anchor's own span rather than the line it sits on. Asked
    #: only when the lines do not fit the dossier ceiling, so a deployment that
    #: supplies it gains a second rung and one that does not keeps exactly the ladder
    #: it had -- `anchors_fit` is `False` whenever this is `None`. Measured on r12: a
    #: neighbour's "line" of 27,510 characters deferred all 17 files in its folder
    #: family at site A, each recorded `BUDGET_EXHAUSTED` with no reservation made.
    anchor_excerpts_for: Callable[..., Sequence] | None = None
    #: `105` §14.4 / `104` R-131 and R-102. The levels a file is asked ONLY when it
    #: is an anchor of a permitted kind, on top of `folder_levels` above, which
    #: every file of the situation is asked. `None` is the state `104` R-102
    #: measured -- the group-level fields withheld from every file, so nothing
    #: writes a `school` fact and no corpus grows a school level -- and it stays the
    #: default, because restoring the question is the OWNER's ruling and a
    #: deployment that has not read it must not start asking by omission.
    anchor_only: AnchorOnlyLevels | None = None
    #: WHICH MODEL ANSWERS ABOUT THIS FILE, or `None` for a file that may reach
    #: none (`104` §17.13 ruling 3). `cli.target_for` builds it: it asks
    #: `model_route_permitted` for the cloud first and the local second and hands
    #: back the routing's pair for whichever permits, so the route's predicate and
    #: the destination are one answer rather than two that can disagree -- which is
    #: the `104` R-02 defect, in the direction that sends.
    #:
    #: Defaulted to `None` because the single-pair spelling above is the one every
    #: deployment with one destination uses, and a required field here would make
    #: every caller state a route it does not have. `route` below is the ONLY read:
    #: nothing in this module touches `model_client` or `model_target` directly, so
    #: the two spellings cannot drift into two behaviours.
    route_for: Callable[[str], tuple[ModelClient, ModelTarget] | None] | None = None
    #: `104` R-175's per-file wall-clock ceiling, or `None` for a run that sets
    #: none. HERE and not on `CallDependencies`, for the reason `usage_recorder`
    #: gives above and one more: `cli.ask_the_situation` is handed this same bundle
    #: as `fact_authorities`, so site G's loop and site A's stage consult ONE
    #: ceiling with one set of sightings -- which is what makes it a ceiling on the
    #: file's whole turn rather than two independent budgets a file can spend twice.
    #:
    #: `None` is the shipped default and is not a stub. A person's own scan has a
    #: person watching it who can stop it; the run this was built for is the 199-file
    #: scoreboard, where nobody is at the screen for nine hours and one stuck file
    #: costs the whole measurement (§18.22). The composition root decides.
    per_file_ceiling: "PerFileCeiling | None" = None

    def __post_init__(self) -> None:
        # `None` PASSES AND `()` STILL REFUSES -- see the field. The guard is
        # about a deployment that never read the library and would ask the model
        # the flat question in silence; a run that read the library and found no
        # situation named says so with `None`, which nothing downstream can treat
        # as a level list.
        if self.folder_levels is not None:
            object.__setattr__(self, "folder_levels",
                               require_folder_levels(self.folder_levels))
        if self.max_released_observations < 1:
            raise ValueError(
                "a dossier with no released evidence is a model asked to answer "
                "from nothing; the cap is a bound on what is sent, not a switch")
        if self.route_for is None:
            if self.model_client is None or self.model_target is None:
                raise ValueError(
                    "a call site with no `route_for` states its one destination as "
                    "`model_client` and `model_target`, and one of them is absent. "
                    "A site with neither spelling has no model and no way to say "
                    "so, which is a call built against nothing rather than a "
                    "deployment that decided not to make one")
            _one_route_pair(self.model_client, self.model_target)
            return
        if self.model_client is not None or self.model_target is not None:
            # TWO SPELLINGS OF ONE FACT, which is how the gate and the route came
            # to disagree the first time (`104` R-02). A per-file route makes the
            # single pair a statement about a destination that is only sometimes
            # the one used, and a reader trusting it would be right about some
            # files and silently wrong about the rest.
            raise ValueError(
                "`route_for` chooses this call's destination per file, so the "
                "single `model_client`/`model_target` pair beside it describes a "
                "destination that is only sometimes the one used. State one or the "
                "other, never both")

    def route(self, file_id: str) -> tuple[ModelClient, ModelTarget] | None:
        """The client and the target THIS FILE is answered by, or `None` for none.

        One read for both spellings, so a deployment with one destination and a
        deployment with two go down the same line of code. `None` means the file
        may reach no model at all -- `cli.target_for` returns it when neither the
        cloud nor the local gate permits the file -- and the caller records
        `privacy_withheld` rather than sending anywhere.
        """
        if self.route_for is None:
            return self.model_client, self.model_target
        chosen = self.route_for(file_id)
        if chosen is None:
            return None
        client, target = chosen
        return _one_route_pair(client, target)


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
    held = _held_field_keys(conn, file_id=file_id, content_hash=content_hash)
    return tuple(field for field in allowed if field not in held)


def _held_field_keys(conn: sqlite3.Connection, *, file_id: str,
                     content_hash: str) -> set[str]:
    """The field keys this file version holds ANY active, unexcluded fact for.

    `pending_fields_for` subtracts this from the allowlist, which is what "pending"
    has always meant: a field something already answered is not open, whoever
    answered it. A `rejected` fact is not an answer (§3.13 makes it an exclusion),
    so the field stays open.
    """
    return {row["field_key"] for row in facts_for_file(conn, file_id, content_hash)
            if row["active"] and row["reliability_state"] != EXCLUDED_STATE}


def _rule_settled_field_keys(conn: sqlite3.Connection, *, file_id: str,
                             content_hash: str) -> set[str]:
    """The field keys a fact STRONGER than an LLM conclusion holds. `104` §18.2 gap 1.

    **THE SAME PREDICATE `facts.llm_seam.build_request` BUILDS `existing_facts` FROM,
    and it has to be, or the question and the flag disagree about the same file.**
    `build_request` supplies check 4 with "every ACTIVE fact stronger than an LLM
    conclusion -- `user_confirmed`, `direct`, `validated` -- derived through
    `is_stronger` rather than listed", and `rule_conflicts` builds the flags off
    exactly those rows. A field this said was settled but that set did not carry
    would be a field gap 1 re-opened with NO flag beside it: the model would be asked
    to reconcile a disagreement it was never shown, which is the state r15 measured
    and the state this gap exists to end.

    **AND IT IS WHY A `possible` OR `llm_supported` FIELD IS NOT RE-OPENED.** Those
    are a model's own earlier answers, not the rules', and gap 1 is about the rules
    deciding a level behind the model's back. Re-asking one would also break
    `00`:298's *"proposed once"*: gap 3 writes an unseen value `possible` and
    `cli._print_values_to_confirm` asks the person about it, and a field held by that
    proposal is excluded from `pending` -- which is the ONLY thing that stopped the
    next run proposing it again. It stays excluded from both halves of the question:
    `pending ∪ settled` is a SUBSET of the allowlist and the remainder is exactly the
    LLM-held fields, which are open questions in front of a person rather than in
    front of a model.
    """
    return {row["field_key"] for row in facts_for_file(conn, file_id, content_hash)
            if row["active"] and row["reliability_state"] != EXCLUDED_STATE
            and is_stronger(row["reliability_state"], LLM_SUPPORTED_STATE)}


def settled_fields_for(conn: sqlite3.Connection, *, file_id: str,
                       content_hash: str,
                       activation_signals: ActivationSignals) -> tuple[str, ...]:
    """The allowed fields A RULE settled: the ones asked again WITH A FLAG.

    `104` §18.2 gap 1. `00`:42's amendment of 2026-09-05 rules that the precedence of
    a rule fact over a model fact "is shown to the model as a flag with its evidence,
    and the model reconciles" -- so a field the deterministic pass answered is no
    longer a field that is not asked, it is a field that is asked with the rules'
    answer beside it. This names them.

    **THE SAME ALLOWLIST, WHICH IS HALF THE POINT OF THE FUNCTION EXISTING.** It is
    one computation over `active_field_allowlist`, the same one `pending_fields_for`
    reads and the same one the dossier's `allowed_vocabulary` is built from. A settled
    field read from anywhere else could name a key outside §3.5's closed vocabulary,
    and `open_question` would then offer the model a field check 1 rejects it for
    proposing -- "a model measured against one list and validated against another can
    be rejected for obeying its instructions", which is the sentence
    `pending_fields_for` above is written against.

    **A SUBSET AND NOT A COMPLEMENT, AND THE REMAINDER IS NAMED.** `pending_fields_for`
    excludes every field ANY active fact holds; this includes only the fields a fact
    STRONGER than an LLM conclusion holds (`_rule_settled_field_keys`, the predicate
    `facts.llm_seam.build_request` builds check 4's `existing_facts` from). So
    `pending ∪ settled` is a subset of `allowed`, and what is in neither is exactly
    the fields held by a `possible` or `llm_supported` fact -- a model's own earlier
    answer, or gap 3's proposal waiting on the person. Those are deliberately asked of
    nobody again: `00`:298 says an unseen value is *"proposed once"*, and the field
    being closed to the question is the only thing that makes "once" true.

    Making the two an exact partition would have been the tidier arithmetic and it is
    the wrong one: `rule_conflicts` reads `existing_facts`, so a field called settled
    here that `build_request` does not carry is a field re-opened with no flag beside
    it -- the model asked to reconcile a disagreement it was never shown, which is the
    defect gap 1 exists to remove.

    **ORDER IS THE ALLOWLIST'S**, not the fact table's, for the first reason again:
    the vocabulary the model is shown is ordered by `order_vocabulary_by_levels` off
    this list, and a list ordered by whatever SQLite returned would put a different
    question in front of two models for one file.

    A field whose only fact is `rejected` is settled for nobody: §3.13 makes
    `rejected` an exclusion rather than a value, so nothing holds the field, there is
    no rule's answer to flag, and `pending_fields_for` leaves it open.
    """
    allowed = active_field_allowlist(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=activation_signals)
    settled = _rule_settled_field_keys(
        conn, file_id=file_id, content_hash=content_hash)
    return tuple(field for field in allowed if field in settled)


def rule_conflicts(existing_facts: Sequence, *, file_id: str,
                   fields: Sequence[str]) -> tuple[Conflict, ...]:
    """The flags `00`:42 requires: what the rules settled, beside the readings.

    `104` §18.2 gap 1. `model_facts` hardcoded `conflicts=()` on every site-A request
    with the comment that "P6 holds no conflict record of its own; §3.7's
    competing-value case is settled by the ranking before a model is asked, so a file
    that reaches here has none to declare". That was true only because the settled
    fields were not asked. Now that they are, the ranking is exactly what the model
    has to be told about, and the amendment names the shape: "shown to the model as a
    flag WITH ITS EVIDENCE, and the model reconciles".

    **REFERENCE-ONLY, AND THREE SEPARATE THINGS SAY IT MUST BE.** `DossierRequest` is
    documented "Reference-only. No materialised content, excerpts, or observation
    bodies"; `llm_harness.dossier` says in its own first paragraph that it "authors no
    content" and that every value it serialises came from P7's release, the builder's
    reference metadata, the injected prompt or the shipped glossary; and the ratified
    A_fact template tells the model "You cannot see this file's existing facts" and
    "You may be judged against facts you were never shown". Writing a fact's VALUE
    into a flag would break all three at once -- and it would put a `school`, an
    `instructor` or an `authored_by` on the wire through no gate, which is the release
    path's whole reason for existing. So the flag names the field and POINTS at the
    reading; the value the model reads is the one P7 released and redacted.

    **THE SHAPE IS P9'S, WITH NO NEW KEY.** `records.Conflict` carries `conflict_id`
    and `kind` and `dossier._body` writes exactly those two, keying every
    `conflict_id` through `wire_handles.wire_handle`. So:

      * `kind` is THE FIELD KEY the rules settled. It is already in the dossier --
        `allowed_vocabulary` carries it and `field_glossary` defines it -- so the flag
        adds no word the model was not already shown, and it is the same register B
        and C use, where a `kind` is the dimension the disagreement is about.
      * `conflict_id` is THE OBSERVATION KEY the rule's fact cites. `_released_body`
        keys `observation_key` with the same function and the same run key, so the
        two strings are equal in the bytes the model reads: the flag and the reading
        it points at are joinable by the model without either being printed in the
        clear. That is "because of Y" said in the one language the dossier has.

    One flag per (field, cited observation), because a rule fact may cite several and
    a flag that named one of them would be evidence half-shown. `facts_for_file`
    orders its rows and `file_facts._checked_refs` sorts every fact's citations, so
    the list this returns is deterministic -- which `dossier_id` depends on, since it
    is the content address of these bytes and a replay is recognised by it.

    **THE FALLBACK, AND THE ONE STATE THAT NEEDS IT.** `_checked_refs` lets only a
    `user_confirmed` fact stand without a citation (§3.1: "Every fact preserves where
    it came from"). A person's own answer therefore has no reading to point at, and a
    settled field with no flag at all would be the gap re-opened for the one value the
    person cared most about. Such a flag carries P9's own id shape,
    `f"{subject}:{kind}"` -- `grouping.p8_seam` writes `f"{group_id}:{kind}"` -- so it
    is still an id this product spells somewhere, and it still keys to something the
    model cannot reverse.

    **THE BOUND, STATED RATHER THAN HIDDEN.** A flag resolves for the model only when
    the reading it names survived into `released_evidence`: R-159's fill spends the
    ceiling on the context and the filename first, and `may_be_released` may refuse
    the reading outright. Nothing here forces it in -- doing so would let a flag
    reorder a dossier that three separate measurements agree about -- so a flag whose
    reading was cut is a field the model is told the rules answered without being
    shown from where. That is strictly more than it was told before, and it is less
    than the amendment asks for; closing it is the fill's question, not this one.

    `fields` is the vocabulary this call actually offers. A flag about a field the
    model may not propose is a flag it can do nothing with, and rule 11 makes every
    unusable line in a dossier a cost.
    """
    wanted = set(fields)
    flags: list[Conflict] = []
    for row in existing_facts:
        field_key = row["field_key"]
        if field_key not in wanted:
            continue
        refs = json.loads(row["evidence_refs"]) or [f"{file_id}:{field_key}"]
        flags.extend(Conflict(conflict_id=ref, kind=field_key) for ref in refs)
    return tuple(flags)


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


def released_wire_cost(observation) -> int:
    """What ONE reading costs the dossier if it is carried: its bytes on the wire.
    `104` R-174 (9 Sep 2026).

    **Why the value's characters stopped being the measure at the fill.** `00`:251
    bounds "tokens per model call", and the model reads a reading as
    `dossier._released_body` writes it -- address, keyed handle, value, zone and the
    four key names -- not as the value alone. While a call carried at most twelve
    readings the envelope was a rounding difference; `104` §17.13 removed the count
    cap so that a whole page could reach the model, and the same rule then let a
    spreadsheet's 509 cells, ~30 characters each, all fit under a 4,000-character
    ceiling while their envelopes made a 241 KB payload the local window refused
    (`gt-local-w3-r18`, four site-G calls). A bound that counts what the model is
    not shown is not a bound on the call.

    So the FILL -- `within_dossier_budget`, the offer's withholding in
    `ordered_releasable_observations`, the excerpt condition in
    `mint_opening_excerpts`, and the ladder's three measurements -- spends the
    ceiling in wire bytes, measured off the function that writes the wire. The
    address is spelled by `privacy.redaction.span_address`, the same spelling the
    gate's `resolve.materialise` gives the released item, so the two addresses are
    one string. The value is the RAW value, on `_call_dependencies`' standing
    reason: this runs before redaction exists.

    **What the gate measures is unchanged, and the order between them still holds.**
    `measure_released_tokens` still counts the released values' characters, and a
    wire cost is never less than its value's characters, so every dossier the fill
    admits under a ceiling is one the door measures under it; nothing this admits
    can be refused `dossier_over_budget`. Making the door count wire bytes too is
    an open row under R-174, and it is a widening of what the door REFUSES, so it
    is the owner's to rule on and not this function's to assume.

    **What is bounded indirectly.** `evidence_items` -- the citation metadata
    beside each released reading -- scales with the same count and is not measured
    here; bounding the released list's bytes bounds its count, and the count is
    what made the metadata large.
    """
    return released_item_wire_bytes(
        observation_key=observation.observation_key,
        address=span_address(observation.location),
        value=observation.raw_value,
        zone=observation.location.zone)


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


def document_order(observation) -> tuple[int, ...]:
    """Where this reading stands in the file, as P4's own locator already says.

    `104` R-159. The tuple of `index` values along `location.container_path`,
    outermost first -- `page=7` before `page=12`, and a paragraph inside a page after
    the page's own reading, because a shorter prefix sorts first and a page-level
    address IS a prefix of the addresses inside it. A label-only segment (§2.3's
    sheet, a `field` name) carries no index and contributes `0`.

    THIS IS NOT A PREFERENCE, and the distinction is the whole reason it is written
    down. What runs before it is `zone_evidence_counts` -- a MEASUREMENT of where
    this corpus's recognisers have cited the fields being asked, since `104` §18.2
    gap 6 replaced the six typed zone names that used to stand there -- and this term
    decides every tie that measurement leaves, which on a cold run is every tie there
    is. What this replaces is the `observation_key` tie-break that used to break ties
    WITHIN a zone: a content-addressed SHA-256, so among a PDF's forty body pages the
    twelve that reached a dossier were the twelve whose digests happened to sort
    lowest. That is not a reading of the document; it is a reading of a hash. The
    document's own order is the one fact P4 records about where a page stands, and
    using it invents nothing -- the key stays as the last term, because two readings
    at one address still need a total order.
    """
    return tuple(
        0 if segment.index is None else segment.index
        for segment in observation.location.container_path)


def _span_start(observation) -> int:
    """The reading's offset into its unit, or `0` where it has no span.

    `0` is the honest value rather than a chosen one: a span-less observation is the
    whole of the unit standing at its path (`items.is_whole_document`'s own reading
    of it), and the whole of a unit starts where the unit starts. It is spelled here
    so that the ordering has no branch a later reader has to reconstruct.
    """
    span = observation.location.text_span
    return 0 if span is None else span.start


def _check_locality(locality: str) -> str:
    """`104` R-159's keyword, refused rather than defaulted. `items.check_item` says
    why in full: every arm that reads it tests `== CLOUD_LOCALITY`, so an
    unrecognised value takes the LOCAL branch and releases a path."""
    if locality not in LOCALITIES:
        raise ValueError(
            f"locality {locality!r} is not one of SPEC §6's {LOCALITIES}; a value "
            f"outside a closed vocabulary is a load error, not a fallback, and the "
            f"fallback here would be the permissive half")
    return locality


#: §8.6's per-call dossier ceiling, in P1's spelling. Spelled here because P1 holds
#: the §8.6 configuration object and publishes no constant for one key at a time --
#: `privacy.gate` spells the same string for the same reason -- and checked against
#: P1's published set at import, on `extractors/budgets.py`'s pattern, so a rename in
#: P1 is an ImportError here rather than a ceiling that silently reads `None`.
DOSSIER_CEILING_KEY: str = "model.max_dossier_tokens_per_call"

if DOSSIER_CEILING_KEY not in CEILING_KEYS:
    raise ImportError(
        f"P8 names a ceiling key P1 does not publish: {DOSSIER_CEILING_KEY!r}. P1 "
        f"owns the §8.6 configuration object (G4) and P8 defines no key of its own.")

#: The extractor name a minted OPENING EXCERPT carries. Its own, and never the name of
#: the extractor that read the document: `observation_key` hashes the extractor name,
#: so an excerpt and the page it was cut from are two different handles.
#:
#: IN P4'S DERIVED NAMESPACE, which is what makes `evidence_shape.store.is_derived`
#: true of it, on `facts.anchor_statements.LINE_EXTRACTOR`'s precedent and for `104`
#: R-135's stated reason: this reading is an addressable copy of text an earlier pass
#: already stored, so that it can be CITED. It says nothing new about what the file
#: IS, and the rule pass and the recogniser skip it through that one predicate. The
#: release path does not, because the words are the file's own.
OPENING_EXCERPT_EXTRACTOR: str = DERIVED_NAMESPACE + "release.opening_excerpt"

#: This producer's version, moved when what it cuts changes. `observation_key` does
#: NOT hash it (MINOR 8), so a bump re-reads the same corpus into the same handles.
OPENING_EXCERPT_EXTRACTOR_VERSION: str = "1.0.0"


def opening_excerpt_bound(conn: sqlite3.Connection, *, limit: int,
                          ceiling: int | None = None) -> int | None:
    """How many characters of a unit one minted excerpt may carry. `104` R-164.

    **NOT A NUMBER CHOSEN HERE, and that is the whole of why this is a function.**
    `104` R-159 is an owner ruling that nothing be built on an invented length: the
    excerpt producer it describes has "only number ... `max_dossier_tokens_per_call`".
    Both operands below are already stored. The ceiling is P1's, read out of
    `budget_ceilings`, and the cap is the `limit` the caller was going to spend
    anyway -- `cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS`, the one place §8.4's
    unnumbered "selected excerpts" becomes a count in this deployment.

    **The quotient is one reading's share of a full call.** A call may carry `limit`
    readings under `ceiling` characters, so `ceiling // limit` is the largest excerpt
    at which a call carrying its full complement of them still fits. On this
    deployment that is 4,000 // 12 = 333, and the arithmetic is the point rather than
    the number: change either stored value and the excerpt follows it.

    `None` when P1 holds no ceiling, and `None` means no excerpt is minted at all.
    A deployment that has not been given a bound is not given one here.
    """
    if ceiling is None:
        ceiling = get_ceiling(conn, DOSSIER_CEILING_KEY)
    if ceiling is None or limit <= 0:
        return None
    bound = int(ceiling) // limit
    return bound if bound > 0 else None


def mint_opening_excerpts(conn: sqlite3.Connection, observations: Sequence, *,
                          sensitive: frozenset, locality: str,
                          bound: int | None, ceiling: int | None) -> tuple:
    """An opening excerpt for each reading of this file that cannot travel as itself.

    **SUPERSESSION, 9 Sep 2026, `104` §17.13.** A whole unit now travels to EITHER
    target when it fits under the stored ceiling, so "cannot travel as itself" is no
    longer the cloud's whole-unit refusal: it is a reading refused outright, or a
    reading LONGER THAN THE CEILING, which no call on any target can carry and which
    `items.check_item` now calls a whole document. That is the one case this producer
    still serves, for both targets alike: a 39,000-character `.txt` unit reaches the
    model as its opening rather than as nothing. `ceiling` is P1's stored value,
    `None` when none is stored, and `None` mints nothing here for the same reason
    `bound` does. The paragraphs below are the R-164 history of the producer.

    **The defect, stated once.** Every text extractor writes one span-less `body`
    observation over each page or paragraph, and `may_be_released` refuses a span-less
    reading whose value is at least as long as the unit standing at its own path. That
    rule is SF-1 / `104` R-07 -- a whole DOCX body travelled span-less at 45,843
    bytes -- and it is correct. A PDF page arrives in the SAME shape, so the rule
    refuses every page of every document, and `104` §16 measured what the model was
    left with: three metadata fields and a heading fragment, a median dossier body of
    212 characters under a 4,000-character ceiling, and 23 labelled files whose course
    code sat in the extracted text and never in the dossier. None of the 23 was
    answered right; the two files that did carry it both were.

    **So this does not release the page.** `00`:186: the engine sends "selected
    excerpts" and "should not send full documents where a short heading or OCR excerpt
    is enough to resolve the question". The excerpt is minted -- a reading over the
    OPENING of the unit, with a span of its own inside it -- and the whole-unit
    refusal goes on refusing the whole unit. `evidence_shape.store.opening_reading_for`
    does the cutting, where the text lives; this function decides which readings may
    have one, which is the division `104` R-135 already drew between P4 and the
    producer that mints a line.

    **Four conditions, and each is a refusal asked BEFORE anything is cut.**

      * The reading is refused as it stands. A reading the call can already carry
        needs no second copy of itself -- which is what keeps `104` R-159's ruling
        whole: a LOCAL target may be shown the page, so a local call mints nothing and
        spends the ceiling once.
      * Its zone is not one of `ALWAYS_LOCAL_ZONES`. `path` and `ocr` are released to
        a local target by the owner's ruling and to no cloud one, and `filename` to
        neither as an excerpt. An excerpt cut from one of those would be that ruling
        walked around by a producer.
      * P5 signalled nothing on it. The per-value signal refuses the whole request and
        is not divided by the target; cutting the opening off a signalled reading
        would release the part P5 objected to.
      * There is a bound. See `opening_excerpt_bound`: no stored ceiling, no excerpt.

    With the first three settled, the reading was refused by the whole-unit arm or by
    an empty value, and `opening_reading_for` answers the second by returning `None`
    when there is no unit longer than the bound to cut.

    **Recorded, because the gate resolves a request against the STORED reading.**
    `privacy.resolve.materialise` reads the observation back by key and refuses a
    requested span that disagrees with the recorded one, so an excerpt that existed
    only in this process would be `UnresolvableSpan` at the door -- `p8_seam` records
    what that cost at site B. The handle is content-addressed, so the row is written
    once however many times this is asked; the check is against the readings already
    in hand rather than a `SELECT` per candidate.
    """
    if bound is None or ceiling is None:
        return ()
    known = {observation.observation_key for observation in observations}
    minted: list = []
    for observation in observations:
        # `104` §17.13: `path` and `ocr` release to every target, so an
        # over-ceiling OCR unit gets its opening like a page does; `filename`
        # alone has no excerpt, because it has no release as an excerpt at all.
        if observation.location.zone in ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET:
            continue
        if observation.observation_key in sensitive:
            continue
        if (may_be_released(conn, observation, sensitive=sensitive,
                            locality=locality)
                and released_wire_cost(observation) <= ceiling):
            continue
        excerpt = opening_reading_for(
            conn, observation, extractor_name=OPENING_EXCERPT_EXTRACTOR,
            extractor_version=OPENING_EXCERPT_EXTRACTOR_VERSION, bound=bound)
        if excerpt is None or excerpt.observation_key in known:
            continue
        record_observation(conn, excerpt)
        known.add(excerpt.observation_key)
        minted.append(excerpt)
    return tuple(minted)


def ordered_releasable_observations(conn: sqlite3.Connection, *, file_id: str,
                                    content_hash: str, locality: str,
                                    limit: int, fields: Sequence[str] = (),
                                    ceiling: int | None = None,
                                    zones_last: Sequence[str] = (),
                                    zones_first: Sequence[str] = ()) -> tuple:
    """Every reading of this file the gate would release, in the order it offers
    them. NO cap and no fill -- `within_dossier_budget` below spends the budget.

    Split out from `releasable_observations` for `104` R-159, because the fill needs
    the two questions apart. `fact_call_stage` asks THIS one to decide whether the
    file has anything to say at all -- the rule that a file with no readings of its
    own is not asked is about the file, not about what fits -- and asks the budget
    function once per context shape, over one database read.

    The order is `(-cited readings in this zone, document order, span start,
    observation_key)`; the exclusions are `may_be_released`'s, asked of every reading.

    **`fields` IS THE ORDER'S ONLY INPUT, and it is measured (`104` §18.2 gap 6).**
    `zone_evidence_counts` carries the argument in full: the first term used to be
    `zone_rank`, a six-name table typed in this file, and it is now the count of
    readings this corpus's own recognisers have cited for the fields THIS call is
    asking. A caller that names no field measures nothing and gets the document's own
    order, which is also what the first file of a cold run gets -- and is the answer
    `104` §18.2 gap 6 asks for where no measurement exists.

    **`limit` is here for the EXCERPT and for nothing else (`104` R-164).** This
    function still caps nothing -- `within_dossier_budget` below spends the budget and
    this one returns the whole offer -- but `mint_opening_excerpts` needs a bound, and
    `opening_excerpt_bound` derives it from the stored ceiling and the cap the call
    was going to spend anyway. Reading the cap here rather than inventing a length is
    the whole of `104` R-159's ruling about invented numbers, and it is the same
    number the caller passes on to the fill a moment later.

    **The minting runs BEFORE the offer is taken, and adds no reading that would not
    have been offered had the document arrived cut up in the first place.** A page
    that this call cannot carry as itself is offered as its opening instead; a page it
    can carry is offered as itself and nothing is minted beside it.
    """
    sensitive = sensitive_observation_keys(conn, file_id)
    stored = observations_for_version(conn, file_id, content_hash)
    # THE CALL'S OWN CEILING, since 12 Sep 2026. This read the stored ceiling
    # (4,000) whatever the call's bound was, so the opening excerpt was minted at
    # 4,000 // limit tokens and the gate, bounded at 1,200, could not take it:
    # on the owner's corpus every file with a full page released its path, its
    # metadata and its title and not one line of its text, and the local model
    # cleared an immigration paper and an account statement with the words "the
    # text shows a file's metadata and path, but no record". The excerpt is sized
    # by the bound it has to fit.
    if ceiling is None:
        ceiling = get_ceiling(conn, DOSSIER_CEILING_KEY)
    mint_opening_excerpts(conn, stored, sensitive=sensitive, locality=locality,
                          bound=opening_excerpt_bound(conn, limit=limit,
                                                      ceiling=ceiling),
                          ceiling=None if ceiling is None else int(ceiling))

    # ONE READ FOR THE WHOLE OFFER, not one per reading: the counts are a property of
    # the fields being asked, not of any reading, so they are measured once here and
    # the sort key only looks a zone up in them.
    cited = zone_evidence_counts(conn, fields=fields)

    def placed(observation) -> tuple:
        # NEGATED, so that MORE citations sort FIRST, and a zone this corpus has
        # never stated these fields in scores 0 -- tying with every other unmeasured
        # zone and leaving `document_order` to decide, rather than being sent behind
        # them all the way `zone_rank` sent `ocr` and `path`.
        #
        # `zones_last` is the calling site's word for the zones that answer its
        # question last -- the gate's path and metadata records, which every file
        # carries and which filled a 1,200-token dossier before one line of its
        # text (12 Sep 2026: six records of 4 to 111 characters, ~170 wire
        # tokens each, and the OCR excerpt of a scanned health form left out).
        #
        # `zones_first` IS ITS MIRROR AND IS THE SAME KIND OF WORD (13 Sep 2026).
        # `cli.SITUATION_ZONES_LAST` already claims one -- "The path stays first: a
        # folder is named after the situation its files are in, and that is
        # evidence this site is asked for" -- and it was not true: with no field to
        # place by, `cited` is empty, every zone ties at 0, and `document_order`
        # decides, which puts whatever the extractor wrote first first. Measured on
        # a synthetic corpus at the cloud bound (2,750): a text file whose opening
        # excerpt is 2,445 characters took two body readings and the ceiling then
        # CUT the path, both metadata readings and the third body reading. A site
        # that says a zone is its first evidence needs a term that says so, and
        # this is that term rather than a re-sort in the caller: the order is one
        # question and `104` R-07 is that one question has one answer.
        return (observation.location.zone not in zones_first,
                observation.location.zone in zones_last,
                -cited.get(observation.location.zone, 0),
                document_order(observation), _span_start(observation),
                observation.observation_key)

    # A READING LONGER THAN THE STORED CEILING IS NOT ON OFFER (`104` §17.13). No
    # call on any target can carry it, `items.check_item` refuses it as the whole
    # document when it covers its unit, and the opening excerpt minted above is
    # its stand-in. Leaving it on offer would let `_without_superseded_excerpts`
    # drop that excerpt in its favour and `within_dossier_budget` then skip the
    # page for length -- the unit reaching the model as nothing, which r169b
    # measured at 4896628 (365-character page, ceiling 182: body offered, excerpt
    # yielded, body skipped, nothing carried). The stage and the gate answer the
    # same about it: neither carries it.
    offered = [observation
               for observation in observations_for_version(conn, file_id,
                                                           content_hash)
               if may_be_released(conn, observation, sensitive=sensitive,
                                  locality=locality)
               and (ceiling is None
                    or released_wire_cost(observation) <= int(ceiling))]
    return tuple(sorted(_without_superseded_excerpts(offered), key=placed))


def _without_superseded_excerpts(offered: Sequence) -> list:
    """An excerpt is offered INSTEAD OF the reading it was cut from, never beside it.

    `104` R-164. A minted excerpt is recorded, so it outlives the call that minted it
    and a later call under different rules finds it standing in the evidence table.
    The rules it would be found under are exactly the ones that did not need it: a
    LOCAL target may be shown the whole unit (`104` R-159), so a corpus first read for
    a cloud target and then read again for a local one would offer the page AND its
    own opening -- the same characters twice, and the second copy spending a ceiling
    the ruling meant for the first.

    So the excerpt yields whenever the reading it was cut from is itself on offer.
    Since `104` §17.13 a reading longer than the stored ceiling is NOT on offer
    (`ordered_releasable_observations` withholds it), so its excerpt stands; a
    reading that fits is on offer for either target, and its excerpt yields.
    They are matched by ADDRESS -- same zone, same container path, the excerpt
    span-bearing and the reading it copies span-less -- because that is what
    `opening_reading_for` preserved and it needs no second record of where the excerpt
    came from.
    """
    covered = {(one.location.zone,
                serialize_container_path(one.location.container_path))
               for one in offered if one.location.text_span is None}
    return [one for one in offered
            if not (one.extractor_name == OPENING_EXCERPT_EXTRACTOR
                    and (one.location.zone,
                         serialize_container_path(
                             one.location.container_path)) in covered)]


@dataclass(frozen=True)
class DossierFill:
    """What `within_dossier_budget` did to one offer: what it took AND what it cut.

    `104` §18.2 gap 5 (9 Sep 2026). The fill used to return the taken half alone and
    drop the rest with a bare `continue`, so the cut existed for the length of one
    loop iteration and nowhere after it. A person reading the run's report could not
    tell a file whose whole evidence reached the model from a file that offered forty
    readings and carried four, and `00`:257's promise -- a prompt over its budget
    "should not truncate silently in a way that removes the decisive evidence" -- had
    no record behind it to be true or false against.

    **Two lists and one derived number, and the number is derived rather than
    accumulated.** `dropped_bytes` re-measures the dropped readings with the same
    `released_wire_cost` the fill spent, so the reported bytes cannot drift from the
    bytes the ceiling was spent in; a counter incremented in the loop would be a
    second spelling of the same measure and the two would disagree the day one of
    them changed.

    **It is not a refusal and it does not become one.** The taken half is byte-for-
    byte what the old return was, in the caller's order, under the same ceiling. The
    owner's word on the day this was built is "files should not be refused; make sure
    all necessary information is processed and used", so what this record buys is a
    true sentence about a cut that was already happening -- never a shorter dossier.
    """
    taken: tuple
    dropped: tuple

    @property
    def dropped_bytes(self) -> int:
        """The cut, in the same wire bytes the ceiling was spent in."""
        return sum(released_wire_cost(one) for one in self.dropped)


def within_dossier_budget(observations: Sequence, *, ceiling: int) -> DossierFill:
    """What of an ordered offer a call may carry: `ceiling` bytes on the wire.
    `104` R-159, measured per `104` R-174.

    **R-174 (9 Sep 2026): the cost of a reading is `released_wire_cost`**, its
    bytes as the model sees them, and no longer its value's characters. The
    paragraphs below say why the fill is bounded by the ceiling alone; R-174 is
    what makes that bound hold for a document of many small readings, which is
    where a character count admitted 509 readings and a 241 KB payload.

    **SUPERSESSION, 9 Sep 2026, `104` §17.13.** The cloud is shown what the local
    model is shown, within the same ceiling, so the count cap the R-164 paragraph
    below kept for a cloud call is gone with the locality it divided by: ONE bound,
    the ceiling, for either target. `cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS` still
    exists and is spent on one thing only, the excerpt bound
    (`opening_excerpt_bound`). The paragraphs below are this function's history.

    **A CLOUD call keeps the count cap, AND is bounded by the ceiling (`104` R-164).**
    §8.4 says "selected excerpts" and states no number; `cli.FACT_CALL_MAX_RELEASED_
    OBSERVATIONS` is where this deployment chooses one, and `104` R-159 did not touch
    it. What R-164 adds is the second bound, and it adds it for R-159's OWN reason,
    now true of a cloud call as well: once each of the twelve readings may be a minted
    excerpt rather than a heading fragment, a COUNT stops being an honest bound on how
    many characters leave. R-159 could write "the ceiling is slack" for a cloud target
    because no page could be released to one; R-164 mints an excerpt of every page
    that cannot, so it is not slack any more. The gate already refuses an over-ceiling
    dossier (`dossier_over_budget`, 2 files of 199 at `gt-w1bn`); asking the same
    ceiling one step early turns a refused CALL into a shorter one, and `104` R-07 is
    that one question has one answer. The cap is not replaced: both bounds apply, and
    a cloud call still carries at most `limit` readings however slack the ceiling.

    **A LOCAL call is bound by the ceiling instead, and the ceiling alone.** Once a
    whole page is releasable the count stops being the honest bound: twelve readings
    of a spreadsheet's cells are a few hundred characters and twelve pages of a PDF
    are twenty thousand. Measured in the scratchpad before this was written, over the
    same 199-file corpus r15 ran: with the 12-cap under local rules 47 files exceed
    the 4,000-character ceiling and 26 PDF/docx files get NO body reading at all --
    heading fragments win the twelve slots and the pages behind them never fit --
    while with the ceiling as the only bound, files carrying zero body text drop from
    118 to 5.

    **A reading that does not fit is SKIPPED and the walk continues.** Stopping at
    the first over-long reading would let one 39,000-character `.txt` unit (`104`
    R-164) cost a file every smaller reading behind it; skipping it costs that file
    only the reading that would not have fitted anyway. The order is the caller's and
    is not re-sorted here: `ordered_releasable_observations` has already put the
    document in its own order, and picking "the ones that fit best" would be this
    function choosing what a person reads first.

    The measurement is `dossier_tokens` -- characters, P7's own upper bound on tokens
    -- over the RAW values, which is what `_call_dependencies` and the gate's
    `measure_released_tokens` both count. The ceiling passed in is the caller's
    remainder, never the whole of `max_dossier_tokens`: what a page has to fit under
    is what the anchor context and the filename left.

    **AND THE CUT COMES BACK WITH IT (`104` §18.2 gap 5).** The skip below was a bare
    `continue` and the dropped reading existed nowhere afterwards, which made two
    silences out of one: the report could not say what was cut, and
    `_call_dependencies` measured §8.6's first rung over THIS FUNCTION'S OWN OUTPUT --
    "does what fits fit" -- so the ladder answered yes for every dossier ever built
    and its DEFERRED rung could not fire for a file's own evidence. `DossierFill`
    returns both halves; the taken half is unchanged, in the caller's order, under the
    same ceiling, and nothing here refuses more than it refused before.
    """
    taken: list = []
    dropped: list = []
    spent = 0
    for observation in observations:
        cost = released_wire_cost(observation)
        if spent + cost > ceiling:
            # THE SKIP IS UNCHANGED AND IS NOW RECORDED. Stopping here would cost
            # the file every smaller reading behind the long one, which is the state
            # R-159 ended; keeping the reading in a second list costs it nothing and
            # is what lets the run say out loud what the ceiling took.
            dropped.append(observation)
            continue
        taken.append(observation)
        spent += cost
    return DossierFill(taken=tuple(taken), dropped=tuple(dropped))


def fill_reserving_top_reading(offered: Sequence, context: Sequence, *,
                               ceiling: int) -> tuple[Sequence, DossierFill]:
    """The file's own readings AND the context they travel beside, under one ceiling
    -- with the file's own strongest reading admitted before the context spends it.

    `ceiling` is what the dossier ceiling has left after the FILENAME, because the
    name is the one released value neither half of this can bargain with: it is a
    single item, §7.7 puts it through its own door, and there is nothing to trim off
    it. What this function divides is the rest, between the file and its neighbours.

    **`104` §18.2 gap 6 (9 Sep 2026), and it is a coverage defect with a measured
    shape.** The order used to be: the anchor context takes what it wants, the name
    takes its bytes, the file's own readings fill the remainder. `104` R-135 gathers
    the context from a NEIGHBOUR under a rule that knows nothing about how much room
    is left, so a folder holding one long syllabus produced a remainder of zero and
    the file reached the model carrying not one word of its own. The model was then
    asked what THIS file is and shown only what the file next door says -- and an
    answer built that way is a fact about the syllabus, which is exactly the failure
    `_within_ceiling`'s own comment describes from the other end.

    **So the top reading is reserved, and only the top reading.** `offered[0]` is the
    strongest reading of the file's own offer under `ordered_releasable_observations`'
    measured order; it is admitted whenever it fits under this ceiling AT ALL, and
    the context fills what is left. Reserving more than one would be this function
    choosing how much of a file is enough, which is the model's question; reserving
    none is the state above. "At least its own strongest reading when one fits
    alone" is the whole promise, and it is the smallest one that makes the call be
    about the file it names.

    **The context yields by the same rule the file's readings yield by, and its cut
    is recorded rather than silent.** `within_dossier_budget` does the trimming --
    the same walk, the same `released_wire_cost`, the same skip-and-continue -- and
    the readings it dropped come back in the SAME `DossierFill.dropped` as the file's
    own, so `GroundingReport.readings_dropped` still counts every reading this
    ceiling took and `104` §18.2 gap 5's promise is not re-broken one object over.
    Two lists would be two numbers for one question.

    **NOTHING MOVES ON THE ORDINARY PATH, and that is asserted by identity rather
    than by equality.** When the context already leaves the top reading room, the
    context comes back as the SAME OBJECT -- `fact_call_stage` decides whether to pay
    for a second `build_request` by asking `shown is not context` -- and the fill is
    byte-for-byte the one this stage built before the reserve existed.

    An EMPTY offer is a state this function is never asked about: `fact_call_stage`
    returns `not_asked` for a file with no readings of its own before the fill is
    reached, because a file that has nothing to say is not asked at all.
    """
    spent_on_context = sum(released_wire_cost(one) for one in context)
    kept, cut = context, ()
    head = released_wire_cost(offered[0])
    if head <= ceiling and head > ceiling - spent_on_context:
        # THE ONE STATE THE RESERVE CHANGES, and neither half of the condition is a
        # default. A top reading that cannot travel even alone is not rescued by
        # taking the context away -- there is no room to give it -- and a top reading
        # the context already left room for needs no rescue, so the context keeps
        # every line it had.
        context_fill = within_dossier_budget(context, ceiling=ceiling - head)
        kept, cut = context_fill.taken, context_fill.dropped
        spent_on_context = sum(released_wire_cost(one) for one in kept)
    own = within_dossier_budget(offered, ceiling=ceiling - spent_on_context)
    return kept, DossierFill(taken=own.taken, dropped=tuple(cut) + own.dropped)


def releasable_observations(conn: sqlite3.Connection, *, file_id: str,
                            content_hash: str, limit: int, locality: str,
                            ceiling: int, fields: Sequence[str] = (),
                            zones_last: Sequence[str] = (),
                            zones_first: Sequence[str] = ()) -> tuple:
    """The observations this file may offer a model, most placed first, bounded.

    The two halves above, composed: `ordered_releasable_observations` for what may be
    offered and in what order, `within_dossier_budget` for how much of it this call
    can carry. A caller that needs them apart -- `fact_call_stage`, which fills the
    same offer into two different remainders -- asks them separately over one read.

    Four exclusions, and each is one of the gate's own refusals applied a step early
    so the call is never BUILT rather than built and denied. Every one of them
    refuses the WHOLE request, not the item -- one bad observation among eight costs
    the file its call -- which is why they are read here and not left to the door:

      * `ALWAYS_LOCAL_ZONES` -- `path`, `filename` and `ocr`, the three zones §8.4's
        members 1, 3 and 6 have a route out through. The filesystem extractor writes
        one observation per file whose raw value is the parent directory.
        `Denied(always_local_item)`. **Since `104` R-159 this is a question about the
        TARGET**: `path` and `ocr` are released to a local model by the owner's
        ruling and `filename` is not, which `may_be_released` states in full.
      * `sensitive_observation_keys` -- P5's per-value signal.
        `Denied(always_local_item)`, from `items.check_item`'s
        `AlwaysLocalRequested` under §8.4's `raw_sensitive_values`. NOT
        `ProtectedItemRequested`, which is §7.3's refusal of an unratified item
        KIND on a protected file and is reached a different way -- `104` §17.6
        named the wrong one and the mistake is worth one line here, because both
        cost the whole request and only one of them is this. Not divided by the
        target either way: a recognised human identifier is not a fact about where
        the value is going. Since `104` R-161 this arm actually fires on a text
        document -- the format's own person-valued fields.
      * a span that covers the whole of its text unit, and a span-less observation
        whose value is at least as long as the unit standing at its own path. That
        is `items.is_whole_document` read against P4's own length-only lookup,
        and §8.4's sentence behind it: the engine "should not send full documents
        where a short heading or OCR excerpt is enough to resolve the question."
        `Denied(whole_document_requested)`, and it fires AFTER the text has been
        resolved, so leaving it to the gate means paying to materialise a document
        in order to refuse it. **Cloud only since `104` R-159**, and the ceiling is
        what bounds a local call instead.
      * a span-less observation with no unit at its path is offered, because that is
        §2.3's cell and §2.8's EXIF field -- the shape where the address IS the
        whole citation and there is no document for it to be the whole of.

    The span is the observation's OWN, never a synthesised `(0, len(value))`:
    `p8_seam` records what that cost at site B -- every unbounded observation
    refused with `UnresolvableSpan` after the release had been minted.

    **THE TAKEN HALF, AND THE BOUNDARY IS NAMED RATHER THAN WIDENED (`104` §18.2
    gap 5).** `within_dossier_budget` now hands back the dropped readings beside the
    taken ones, and this composition throws the dropped half away. That is honest
    here and nowhere else: the caller that needs the cut is `fact_call_stage`, which
    asks the two halves separately over one read "because it fills the same offer
    into two different remainders", and it is that stage's dossier the cut is
    recorded on. A caller of this function is asking "what may this file offer,
    bounded" and has no call to record anything against. If one ever does, it takes
    the `DossierFill` rather than this, and the record goes with it.

    **`fields` PASSES STRAIGHT THROUGH AND DEFAULTS TO NONE (`104` §18.2 gap 6).**
    The order is measured off the fields a call is asking about, and the three cli
    sites that compose this one -- site B's excerpt read, site C's remainder fill,
    the review surface's -- are not asking a field question at all. They measure
    nothing and get the document's own order, which is what they had before any
    preference existed; a field invented for them here would be this module deciding
    what they are asking.
    """
    return within_dossier_budget(
        ordered_releasable_observations(
            conn, file_id=file_id, content_hash=content_hash, locality=locality,
            limit=limit, fields=fields, ceiling=ceiling, zones_last=zones_last,
            zones_first=zones_first),
        ceiling=ceiling).taken


#: The origin whose citations are NOT counted below, and the one exclusion in the
#: measurement (`104` §18.2 gap 6). A model's own fact cites the reading the model was
#: shown, so counting `llm_interpretation` would make the next dossier's order an echo
#: of the last dossier's order: the zone a reading happened to be offered in becomes
#: the reason the next file's reading of that zone is offered first, and the
#: measurement stops being about where the CORPUS states a field. Rule one is that the
#: LLM decides; it is not that the LLM's answers silently re-rank the evidence the
#: next call is shown. Every other origin -- the deterministic extractor, the rules,
#: the person's own correction, an approved folder -- is a recogniser or a human
#: saying "the value is here", and all four are counted.
_ECHOED_ORIGIN: str = LLM_INTERPRETATION


def zone_evidence_counts(conn: sqlite3.Connection, *,
                         fields: Sequence[str]) -> Mapping[str, int]:
    """WHERE THIS CORPUS HAS ACTUALLY STATED THESE FIELDS, per zone, measured.

    **`104` §18.2 gap 6 (9 Sep 2026), and it is constitution rule one.** What stood
    here was `_ZONE_PREFERENCE`, six zone names typed in this file's own order --
    title, heading, metadata, body, table, notes -- with `zone_rank` sending every
    zone outside the six behind all six. Two consequences, both of them the rule's
    own subject. A hand-typed table decided which readings survived a capped dossier,
    which is domain knowledge deciding what the model sees. And it disagreed with the
    product's other table: `cli.ZONE_WEIGHT` weighs metadata, body, ocr and path
    equally, while this one ranked metadata third, body fourth, and `ocr` and `path`
    -- the two zones §17.13 had just opened to every target -- dead last, behind
    zones no reader in this deployment produces. A page of OCR text, the only reading
    a scanned syllabus has, queued behind an empty `notes`.

    **What replaces it is a count, not a better table.** For the fields this call is
    about to ask, every fact the store already holds is read, every `evidence_refs`
    entry on it is resolved to the reading it cites, and the zones those readings
    stand in are counted. A field whose values this corpus states in `ocr` scores
    `ocr` highest for that field; a field stated in headings scores `heading`
    highest. Nothing is named here and nothing is ranked here: the corpus is asked
    where its own answers to this question have been found, and the answer is
    whatever it is.

    **A zone with no measurement is not sent last.** It scores zero, ties with every
    other unmeasured zone, and the sort's next term -- `document_order`, the
    document's own order -- decides between them. That is the whole of the "unlisted
    zone" defect: `zone_rank` gave an unmeasured zone a rank WORSE than every named
    one, which is a judgement about a zone nobody had measured. Zero is the honest
    score for "this corpus has not yet stated this field here", and it is the score
    every zone carries on the first file of a cold run -- where the order is then the
    document's own, alone, which is what `104` §18.2 gap 6 asks for.

    **`fields` is required and empty is meaningful.** A caller that is not asking
    about a field -- `cli`'s site B and site C reads of `releasable_observations` --
    passes nothing, measures nothing, and gets the document's own order. Guessing a
    field for them would be this module deciding what they are asking.

    **One GROUP BY and not a resolve per citation.** `facts.evidence`'s own docstring
    records what a per-observation Python loop cost this package once
    (`analysis_tier_for_observation`: 441,386 calls on one 413-file folder). The join
    is `json_each` over the stored refs into `evidence` by `observation_key`, which
    is the indexed column, and the count is over DISTINCT `(fact, key)` pairs because
    a key carries one row per extractor version (`evidence_key` is deliberately not
    unique, MINOR 8) and a version bump is not a second statement.

    **The order this makes depends on the corpus, and that is the point.** A file
    asked early in a cold run is ordered by its own document order and a file asked
    late by what the run has learned, so two runs over the same corpus in the same
    roster order agree, and a run over half a corpus orders differently from a run
    over all of it. Nothing here DECIDES anything -- the model reads every reading in
    the dossier and the order says only which one the ceiling keeps when it cannot
    keep them all -- which is why this is the one place a corpus-derived answer is
    better than a stable table, and why `cli.ZONE_WEIGHT`, which decides a stored
    fact, is deliberately not derived this way (its own comment carries that).
    """
    named = tuple(sorted({field for field in fields if field}))
    if not named:
        return MappingProxyType({})
    placeholders = ", ".join("?" * len(named))
    rows = conn.execute(
        "SELECT json_extract(e.location, '$.zone') AS zone, "
        "       COUNT(DISTINCT f.fact_id || ' ' || r.value) AS citations "
        "FROM file_facts AS f "
        "JOIN json_each(f.evidence_refs) AS r "
        "JOIN evidence AS e ON e.observation_key = r.value "
        f"WHERE f.field_key IN ({placeholders}) "
        "  AND f.active = 1 "
        "  AND f.origin <> ? "
        "  AND e.superseded_by IS NULL "
        "GROUP BY zone",
        (*named, _ECHOED_ORIGIN)).fetchall()
    return MappingProxyType({row["zone"]: int(row["citations"])
                             for row in rows if row["zone"]})


def may_be_released(conn: sqlite3.Connection, observation, *,
                    sensitive: frozenset, locality: str) -> bool:
    """The four exclusions above, asked of ONE reading. No ranking and no cap.

    **`locality` divides two of the four (`104` R-159), and it has no default.** The
    owner ruled §15.4 item 14 the first way on 8 Sep 2026: a LOCAL model may be shown
    a whole text unit, the person's folder path and OCR text, within the dossier
    ceiling; the cloud restrictions stand unchanged for a cloud target.
    `items.check_item` carries the reasoning and the OCR residual in full, and this
    is the same rule asked a step early -- the two must not answer differently, which
    is why both read `vocabulary.RELEASED_TO_EVERY_TARGET` rather than each
    spelling the ruling's two zones.

    **A `filename`-zone observation stays refused as an excerpt for BOTH targets**,
    and that is the one member of `ALWAYS_LOCAL_ZONES` the ruling does not release.
    The name already arrives through `NAME_BEARING`'s own item -- `filename_citation`
    below builds it and `build_fact_request` puts it first -- so a second copy of it
    as an excerpt is noise the ceiling pays for, and it would reach the model through
    a door where §7.7's `allow_unratified` opt-in and §7.3's protected-records ban do
    not apply.

    Split out for `104` R-135's third defect, which is worth writing down because the
    code read as though it were doing the right thing. `anchor_context_observations`
    collected the line readings it wanted and then kept only those that also appeared in
    `releasable_observations(file_id=<the stating file>, limit=...)` -- that file's own
    RANKED, CAPPED dossier. A minted body line is `possible` reliability in the `body`
    zone and never reaches a syllabus's top twelve, so it was dropped for losing a
    competition it was never in. Measured over the first 9 files asked on r9: 120
    statements refused as "line not among releasable", 7 of 9 files ending with no
    context at all, while nothing about those readings was unreleasable.

    So the question a caller asks about a NAMED reading is asked about that reading.
    The rules are identical and are not restated: this function IS the body of the
    loop above.

    Not here, and deliberately: the classification gate. Whether the file this reading
    belongs to is protected or unclassified is a question about the FILE, and
    `cli.anchor_context_observations` asks it once per stating file through
    `ClassificationStore` before it asks anything about readings. Asking it per reading
    would be one `classifications` read per line for one answer.
    """
    # SUPERSESSION, 9 Sep 2026, `104` §17.13: the cloud is shown what the local
    # model is shown, so the two arms that once divided by `cloud` -- the zone arm
    # and the whole-unit arm -- are gone. `filename` is refused as an excerpt for
    # every target (its door is `Filename`), and a whole unit is no longer refused
    # HERE by its coverage: what bounds it is the ceiling, in `within_dossier_budget`
    # (a reading that does not fit is skipped) and in `items.check_item` (a whole
    # unit longer than the stored ceiling is the whole document the gate refuses).
    # `locality` is still validated: a caller must say where the bytes go.
    _check_locality(locality)
    where = observation.location
    if where.zone in ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET:
        return False
    if observation.observation_key in sensitive:
        return False
    if not observation.raw_value:
        return False
    if where.text_span is None:
        # The two span-less shapes -- the cell or field with no unit at its path,
        # and the whole unit -- both release now; the unit is bounded by the ceiling.
        return True
    if not unit_stands_at(conn, observation):
        # `materialise` raises `UnresolvableSpan` here rather than denying: a span
        # with nothing to take a substring of is a contract failure, and this call
        # is not the place to discover it. Asked as a presence, not a length: the
        # length sits behind the unit's whole text in the row (run 14, 15 Sep).
        return False
    return True


def releasable_readings(conn: sqlite3.Connection, *, file_id: str,
                        content_hash: str, keys, locality: str) -> tuple:
    """The NAMED readings of one file that a model may be shown. No ranking, no cap.

    `releasable_observations` above answers "what may this file offer, best first,
    capped" -- the question a call about that file asks. This answers "may these
    particular readings be shown", which is the question a caller asks when the file is
    a NEIGHBOUR and the readings were chosen for a reason of its own. `104` R-135's
    context builder is that caller; `may_be_released` records what happened when the
    two questions were answered with one function.

    Returned in `keys`' own order, so the caller's reason for choosing them survives to
    wherever it does its own ordering.

    `locality` is forwarded and not decided here (`104` R-159): the question this asks
    is `may_be_released`'s, and a neighbour's reading leaves by the same door the
    file's own does.
    """
    wanted = tuple(dict.fromkeys(keys))
    if not wanted:
        return ()
    sensitive = sensitive_observation_keys(conn, file_id)
    by_key = {
        observation.observation_key: observation
        for observation in observations_for_version(conn, file_id, content_hash)
    }
    return tuple(
        by_key[key] for key in wanted
        if key in by_key and may_be_released(conn, by_key[key],
                                             sensitive=sensitive,
                                             locality=locality))


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


def filename_characters(conn, item: EvidenceItem | None) -> int:
    """How many characters the filename item will cost the dossier, or `0`.

    `104` R-159. `measure_released_tokens` counts the resolved filename like any
    other released value -- `104` R-06 put it in `NAME_BEARING` precisely so it is
    resolved and not reference-only -- so a builder that filled its readings up to
    the ceiling and then added the name would hand the gate a dossier the gate
    refuses `over_dossier_ceiling`. This is that cost, measured before the fill.

    Measured on the observation's RAW VALUE rather than by materialising it, on
    `_call_dependencies`' own rule for the readings beside it: the ladder runs before
    `gate.release`, redaction only ever shortens, so a raw-value count is at or above
    what the door will measure and the two agree about every dossier either would
    refuse. It is also the same measurement the other two items in the total get,
    which is what makes the total one number rather than three.

    **`104` R-174: the same measurement is now `released_wire_cost`'s** -- the
    name's bytes as `dossier._released_body` writes them, address and handle and
    zone included -- so that the total stays one number when the readings beside
    the name are measured that way. The name has no `Observation` in hand here,
    only its row, so the cost is spelled from the row's own columns through the
    same function the readings go through.
    """
    if item is None:
        return 0
    row = conn.execute(
        "SELECT raw_value, location FROM evidence WHERE observation_key = ? "
        "AND superseded_by IS NULL LIMIT 1", (item.evidence_ref,)).fetchone()
    if row is None:
        raise UnresolvableSpan(
            f"observation {item.evidence_ref!r} was addressed as this file's name "
            f"and then had no row; P4's evidence table answered two ways about one "
            f"key")
    location = location_from_mapping(json.loads(row["location"]))
    return released_item_wire_bytes(
        observation_key=item.evidence_ref, address=span_address(location),
        value=row["raw_value"], zone=location.zone)


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


def _context_items(observations: Sequence) -> tuple[EvidenceItem, ...]:
    """`104` R-135's context metadata: a NEIGHBOUR's reading, marked as one.

    Identical to `_evidence_items` in every field but `basis`, and that field is the
    whole point. `direct-anchor` says the file itself carries this; `context-supported`
    says something near it does. `validation._acceptance_outcome` reads the bases of
    the items a claim cited and returns `ACCEPT_CONTEXT_SUPPORTED` when every one of
    them is context, which `_make_verdict` turns into `requires_review=True` -- so a
    `subject` the model read off a neighbouring syllabus is recorded, and recorded as
    a fact a person still has to confirm. A file that also cites its own text gets the
    ordinary direct outcome, because the mixed case is not a context-only answer.

    §8.4's gate decides what of this is releasable, and P7 refuses an item whose
    observation resolves outside `Target.file_ids` -- which is why the site-A target
    gains the stating file's id below. Withholding the id and offering the item would
    be an `UnresolvableSpan` at the door, after the release had been minted.
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
            basis=CONTEXT_SUPPORTED,
        )
        for observation in observations
    )


def build_fact_request(
    request: FactRequest,
    observations: Sequence, *,
    filename: EvidenceItem | None = None,
    context: Sequence = (),
    model_target: ModelTarget,
    prompt: PromptDefinition,
    max_dossier_tokens: int,
    fill: "DossierFill | None" = None,
    asked_fields: Sequence[str] = (),
) -> DossierRequest:
    """A reference-shape conversion and nothing else. No text crosses this line.

    **`asked_fields` IS THE QUESTION, AND IT IS WHAT THE FLAGS ARE ABOUT (`104` §18.2
    gap 1).** It is `open_question`'s vocabulary -- the field keys this call actually
    offers -- and the only thing done with it is to decide which of the file's already
    settled facts become `Conflict` flags. `rule_conflicts` reads them off
    `request.existing_facts`, which P6 already built as every ACTIVE fact stronger
    than an LLM conclusion, so nothing is queried here and nothing is authored: this
    function stays the reference-shape conversion its first line says it is. `()` is a
    caller that offers no vocabulary and therefore has nothing to flag -- the shape
    every hand-built test request had before this field existed, and the same empty
    tuple that used to be hardcoded.

    **`fill` IS THE CUT THIS REQUEST WAS BUILT UNDER (`104` §18.2 gap 5).** It is the
    `DossierFill` whose `taken` half is the `observations` above, and the only thing
    read off it is the two counts: how many readings the ceiling dropped and their
    bytes. `None` is a caller that did not fill -- a test building a request by hand
    -- and reports a cut of nothing, which is the truthful answer for an offer that
    was never trimmed. Passing the observations and the fill separately would let
    them disagree, so the assertion below is that they do not: the fill's taken half
    IS what is being described.

    `prompt_fingerprint` is the PROMPT's. `transport.issue` recomputes it from the
    `PromptDefinition` it is about to send and refuses the release when the two
    disagree, so a request bound to anything else -- the dossier's own address, say
    -- raises `BindingMismatch` after P7 has already spent the release. That is the
    defect that kept P9's first real group call from ever reaching a model, and it
    is written down here so site A does not rediscover it.
    """
    if fill is not None and tuple(fill.taken) != tuple(observations):
        raise MalformedRecord(
            "the fill handed to `build_fact_request` describes a different set of "
            "readings than the ones the request carries: a cut counted against a "
            "dossier that was not built from it is a number about nothing"
        )
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
        + _evidence_items(observations)
        # `104` R-135, LAST rather than first, and for `filename`'s reason read the
        # other way: R-58's shared prefix is the frame, and these vary per file.
        + _context_items(context),
        # `104` §18.2 GAP 1. This read `conflicts=()` with the note that "P6 holds no
        # conflict record of its own; §3.7's competing-value case is settled by the
        # ranking before a model is asked, so a file that reaches here has none to
        # declare". The ranking is still what settles it -- and `00`:42's amendment
        # rules that the ranking is a thing the model is SHOWN and reconciles, not a
        # thing decided behind it. `rule_conflicts` names the fields the rules already
        # answered and points each at the reading they answered it from; it carries no
        # value, because a `DossierRequest` is reference-only and a fact's value has
        # no door through the gate.
        conflicts=rule_conflicts(
            request.existing_facts, file_id=request.file_id, fields=asked_fields),
        model_call_request=ModelCallRequest(
            stage=FACT_STAGE,
            # `104` R-135: THE SUBJECT FILE FIRST, and every file a context reading
            # was taken from after it. `gate._resolve` refuses an item whose
            # observation lives outside `target.file_ids` (`UnresolvableSpan`,
            # "outside request.target.file_ids"), so a context excerpt offered
            # without its file's id here is refused at the door after the release has
            # been minted. FIRST is load-bearing too: `gate._decisive` reads
            # `records[file_ids[0]]` as the handling class this release is judged
            # under, and that must be the file the call is about.
            #
            # The gate now classifies every id in this tuple, which is the widening
            # this row accepts on purpose: a protected or unclassified neighbour
            # denies the whole call. `fact_call_stage`'s context authority applies
            # that refusal a step early -- `releasable_observations`' own rule, "each
            # is one of the gate's own refusals applied a step early so the call is
            # never BUILT rather than built and denied" -- so an ordinary file does
            # not lose its own fact call to a syllabus nobody classified.
            target=Target(
                file_ids=(request.file_id,) + tuple(dict.fromkeys(
                    observation.file_id for observation in context
                    if observation.file_id != request.file_id)),
                group_id=None),
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
            ) + tuple(
                # `104` R-135. The same kind of item and the same door; what marks it
                # context is `EvidenceItem.basis` above, not a second channel. P7 has
                # no notion of context and must not be given one: it decides what may
                # leave, and this is text of a file exactly as the rest is.
                Excerpt(
                    observation_key=observation.observation_key,
                    span=observation.location.text_span,
                    reason="a reading near this file the fields may rest on",
                )
                for observation in context
            ),
            prompt_template_id=prompt.template_id,
            prompt_fingerprint=prompt_fingerprint(prompt),
            max_dossier_tokens=max_dossier_tokens,
        ),
        # Null at A and B (`records._require_plan_version`): a fact is about a file
        # version and not about a plan, and the same fact survives a re-plan.
        plan_version=None,
        evidence_snapshot_id=None,
        # `104` §18.2 gap 5. Counts, not readings: what the ceiling cut never reaches
        # this record in any other form, and it must not -- a `DossierRequest` is
        # reference-only and a dropped reading's text is exactly the content this
        # line is forbidden to carry.
        readings_dropped=0 if fill is None else len(fill.dropped),
        readings_dropped_bytes=0 if fill is None else fill.dropped_bytes,
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
    name_characters: int,
    anchor_observations: Sequence | None = None,
    unreduced_observations: Sequence | None = None,
) -> CallDependencies:
    """`observations` is the list the request was BUILT from, and it is here so that
    §8.6's first ladder rung is measured rather than asserted (`103` C7).

    `anchor_observations` is the second shape (`104` R-145): the file's own readings
    with the anchors' own spans in place of their lines. `None` means the deployment
    offers no such shape, and the rung is then honestly absent as it always was.

    `unreduced_observations` is the offer BEFORE the fill spent the ceiling on it
    (`104` §18.2 gap 5), and it is what the first rung now measures. `None` keeps the
    old spelling for a caller that never filled -- there the built list IS the whole
    offer and the two questions have one answer.

    Measured on the raw values rather than on the released ones, because the ladder
    runs before `gate.release` -- `run_call` plans the reduction, then reserves, then
    releases -- so the redacted text does not exist yet. Redaction only ever
    shortens (`apply_redaction` refuses a transform that returns its input), so the
    pre-call number is at or above what the door will measure, and the two therefore
    agree about every dossier either would refuse.

    **`104` §18.2 GAP 5: WHAT "UNREDUCED FITS" MEANS, AND WHY NO FILE IS REFUSED FOR
    THE CHANGE.** Until this patch the first rung was measured over `observations` --
    the list `within_dossier_budget` had ALREADY trimmed to fit -- so it asked "does
    what fits fit" and could only answer yes. Every dossier ever built therefore
    recorded `reduction_rung = none`, including the ones that reached the model
    carrying four of a document's forty readings, and §8.6's ladder was a decoration
    on a measurement that could not fail. The rung a person reads on the record was
    the one thing telling them a reduction had happened, and it said none.

    So the first rung measures the UNFILLED offer: it is true only when nothing was
    cut. What replaces it when something was cut is `anchors_fit`, and that is the
    whole of the safety argument, because `plan_reduction` falls from `unreduced_fits`
    to `summarized_fits` to `anchors_fit` to the shards and then to DEFERRED -- and
    DEFERRED is a `PreCallAbstention` that sends nothing. The owner's word on the day
    this was built is "files should not be refused; make sure all necessary
    information is processed and used", so the arithmetic below is written to leave
    the deferred set EXACTLY as it was:

      * `anchors_fit` is true when the shape that was BUILT fits, or when R-145's
        excerpts shape fits. The built shape is the fill's output plus the shown
        context plus the name, and the fill's own ceiling is `max_dossier_tokens`
        less the context and the name -- so it fits by construction whenever that
        remainder is not negative. `PRESERVED_ANCHORS` is the honest name for it:
        `00`:257's second remedy is to preserve the excerpts that matter and drop the
        rest, which is precisely what the fill did.
      * DEFERRED is therefore reached in exactly one state, the same state that
        reached it before: the context and the filename alone exceed the ceiling, so
        no reading of the file's own fits, AND R-145's excerpts shape does not fit
        either. Before this patch `unreduced_fits` was false in that state for the
        same reason and the ladder fell the same way.

    A file that was asked before is asked now; what changed is that its record says
    `preserved_anchors` instead of `none` when the ceiling took part of its evidence,
    and `GroundingReport.readings_dropped` says how much.

    **`104` §18.2 GAP 6 NARROWED THAT LAST STATE FURTHER, AND THE ARITHMETIC HERE IS
    UNTOUCHED.** This function still answers DEFERRED for a shape that does not fit;
    what changed is upstream, in what `fact_call_stage` BUILDS. Since the reserve,
    the context yields room to the file's own strongest reading instead of consuming
    the whole ceiling, so the "no reading of the file's own fits" state is no longer
    produced by a large context -- only by a FILENAME whose own bytes exceed the
    ceiling, which leaves no room to reserve. The state above is still the state this
    ladder defers; the stage simply stops manufacturing it out of a neighbour's
    words, which is the half of it that ever cost a file its call.
    """
    built_fits = sum(
        released_wire_cost(observation) for observation in observations
    ) + name_characters <= authorities.max_dossier_tokens
    offered = observations if unreduced_observations is None else (
        unreduced_observations)
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
        # Two of the other three rungs stay honestly absent. `00`:257 offers four
        # remedies -- summarize deterministic facts, preserve anchor excerpts, split
        # the task, or defer -- and this deployment can build the SECOND (`104`
        # R-145): the file's own readings are the capped set already, but the
        # context readings beside them have a smaller shape, each anchor's own span
        # in place of the line it sits on. `anchors_fit` measures that shape when
        # the composition root supplies one and is `False` when it does not, so
        # `plan_reduction` never names a rung `_units` cannot hand `run_call`; the
        # stage builds the request in whichever shape the ladder will pick. When
        # neither fits, the fourth is what is left, and `plan_reduction` takes it:
        # `DEFERRED`, with a `PreCallAbstention` carrying `BUDGET_EXHAUSTED`, before
        # `reserve_call` and before `gate.release`, so a deferred call spends no
        # budget and mints no release. That is `00`:259's "mark the deferred stage,
        # and leave the file in review rather than guessing".
        #
        # `104` R-159: `name_characters` IS PART OF BOTH RUNGS, and it is what made
        # this measurement a different measurement from the gate's. `observations`
        # here is already the file's own readings PLUS the context the request was
        # built with -- the caller concatenates them -- and the filename was the one
        # released value neither this nor `_within_ceiling` counted while
        # `measure_released_tokens` did. All three now count own + shown context +
        # the name, so a dossier the ladder passes at rung NONE is a dossier the door
        # measures under the ceiling.
        #
        # `104` §18.2 GAP 5: over the UNFILLED offer, so "unreduced" means what the
        # word says. The docstring above carries the argument that this refuses no
        # file: what the first rung stops claiming, the third rung claims instead.
        unreduced_fits=sum(
            released_wire_cost(observation) for observation in offered
        ) + name_characters <= authorities.max_dossier_tokens,
        summarized_fits=False,
        # THE SHAPE THAT WAS BUILT, OR R-145'S SECOND ONE. `00`:257's second remedy
        # is to preserve the excerpts that matter and drop the rest, and both of these
        # are that remedy: the fill preserving the file's own readings that fit, and
        # the anchors' own spans standing in for the lines they sit on. A dossier the
        # ceiling trimmed records `preserved_anchors` rather than `none`, which is the
        # one word on the record that tells a person a reduction happened at all.
        anchors_fit=built_fits or (anchor_observations is not None and sum(
            released_wire_cost(observation) for observation in anchor_observations
        ) + name_characters <= authorities.max_dossier_tokens),
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


#: What a grant made over THIS RUN'S OWN SCAN is called in `00`:44's cache key.
#: Not a scope anything looks up -- `privacy.gate` matches the raw scope and never
#: reads this string -- and not a value any real scope can collide with: every
#: scope a run mints is a `uuid4` hex id.
STANDING_GRANT_SCOPE: str = "the run's own scan"


def _scan_run_ids(conn: sqlite3.Connection) -> frozenset[str]:
    """Every scan this database has recorded, or nothing if it has recorded none.

    Read through `sqlite_master` rather than caught as an `OperationalError`,
    because a database with no P3 scan is the ordinary case for the harness's own
    fixtures and a swallowed exception here would also swallow a real fault in the
    table. The read is one scan of a table with one row per run.
    """
    if not conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            ("scan_runs",)).fetchone():
        return frozenset()
    return frozenset(
        row[0] for row in conn.execute("SELECT scan_run_id FROM scan_runs"))


def _consent_grants_content(conn: sqlite3.Connection,
                            grants: Sequence) -> list[list[str]]:
    """The grants a policy carries, with no run id among them.

    **`R-172a` is a PROPOSED row and not one `104` carries.** It is written here as
    the shortest handle for what follows, and the register entry -- or a different
    number -- is the lead's; every reference to it in this checkout is a reference
    to the argument below and to nothing filed anywhere else.

    **R-109's own closing sentence is the invariant this keeps**: *"No dimension
    carries a run id, a timestamp or a path (two runs of one checkout over
    unchanged files: two identity ids, both stable)."* `policy` is one of the
    dimensions that sentence covers, and `104` §18.7 broke it without anyone
    measuring the cost. The owner's ruling -- protected material reaches the LOCAL
    model -- is recorded by `cli.standing_consent_grants` as the real §8.4 grant it
    is, and the only scope the run has to make it over is the scan: `Gate`'s
    `scope_for` is `lambda file_id: scan_run_id`, which `privacy/gate.py` calls
    "Open question 3's placeholder rather than a root". A scan run id is a fresh
    `uuid4` on every run. So the policy CONTENT moved on every run although the
    policy said the identical thing, every `llm_call_identity` digest moved with
    it, and R-109's reuse and R-123's `--reuse-answers-from` both bought every
    answer again -- measured as a second run of one unchanged database making all
    of its fact calls a second time, and a seeded run reusing nothing at all.

    The remedy is the one `_policy_content` already applies to `policy_version` and
    `set_at`: a term that moves without the policy changing is not the policy. A
    grant made over the scan this run happens to be is the deployment's standing
    permission and says nothing a person decided about a durable corpus area, so it
    is recorded under `STANDING_GRANT_SCOPE` -- the OPTION verbatim, because the
    option is the whole of what was authorised and `local_model` and `cloud` are
    two different policies.

    **The scope is canonicalised HERE and nowhere else.** `standing_consent_grants`
    must keep minting the scan's own id: `Gate.release` matches
    `policy.consent_grants` against `self._scope_for(file_id)`, so a grant under any
    other name answers `NeedsConsent` for every protected file and §18.7's ruling
    stops holding. What changes is what the CACHE KEY remembers about it, which is
    what `00`:44 asks for -- "the exact process that produced it", not the label the
    process was filed under.

    A grant over a scope this database has no scan for is left exactly as it is: it
    names something outside this run, and the identity must move when it moves.
    """
    scans = _scan_run_ids(conn)
    return [[STANDING_GRANT_SCOPE if scope in scans else scope, option]
            for scope, option in grants]


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
    changing -- and the grants are read through `_consent_grants_content` for the
    THIRD one, `104` §18.7's standing grant, whose scope is the run's own scan id. A policy that really does change -- consent withdrawn, a redaction
    setting raised -- changes this string and invalidates every answer under it,
    which is the half of `00`:44 that matters.
    """
    policy = policy_at(conn, policy_version)
    return canonical_json({
        "automatic_move_permissions": dict(policy.automatic_move_permissions),
        # `104` R-172a: the grants, with the run's own scan named as the standing
        # scope it is. `_consent_grants_content` carries the whole argument.
        "consent_grants": _consent_grants_content(conn, policy.consent_grants),
        "operation_mode": policy.operation_mode,
        "plan_version": policy.plan_version,
        "redaction_settings": dict(policy.redaction_settings),
        "suspended_item_kinds": sorted(policy.suspended_item_kinds),
    })


def _routed_target(authorities: "FactCallAuthorities",
                   file_id: str) -> ModelTarget:
    """The target this file is routed to, refusing rather than guessing.

    `call_identity_dimensions` is only ever built for a call that is about to be
    made, so a file with no route cannot reach here; a `None` would mean the
    identity is being recorded for a call nothing authorised, and a dimension
    invented for it would key an answer under a destination that was never asked.
    """
    chosen = authorities.route(file_id)
    if chosen is None:
        raise ValueError(
            f"file {file_id!r} is routed to no model, so there is no `model_id` "
            f"for `00`:44's cache key to record. A call identity written without "
            f"one would key this file's answers under a destination nothing sent "
            f"them to")
    return chosen[1]


def call_identity_dimensions(
    conn: sqlite3.Connection, *,
    file_id: str,
    content_hash: str,
    observations: Sequence,
    authorities: FactCallAuthorities,
    context: Sequence = (),
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
      * `context_refs` is `104` R-135's, and it is the KEYS and not a count.

    **Why the context needs a term of its own, measured against the terms that were
    already here.** `extractor_versions` is the only term read off the readings, and it
    is a SET of `(name, version)` pairs: a syllabus read by `pdf.text 1.0.0` beside
    coursework read by `pdf.text 1.0.0` adds nothing to it. So folding the context
    observations into `observations` leaves the digest byte-identical to the digest of
    the call that never saw them -- and `answered_fields` counts an abstention as an
    answer (R-109), so a file whose prior verdict was `unknown` about `subject` would
    be reused forever and never shown the heading. That is the 19 missing course codes
    this row is about, kept missing by the cache built to save money on them.

    THE KEYS, because an observation key is content-addressed: a different heading, a
    re-extracted one, or one that a later reading retracted all produce a different
    term. A count would say "one anchor" about two different anchors.

    A file with no anchor near it carries `[]` here, which is what every call in a
    deployment that offers no context carries -- so those identities are the same
    shape they were, and only their digest moved, once, when the term was added.
    """
    return {
        "call_site": A_FACT,
        "content_hash": content_hash,
        "context_refs": sorted(
            observation.observation_key for observation in context),
        "extractor_versions": sorted(
            {(observation.extractor_name, observation.extractor_version)
             for observation in observations}),
        # THE ROUTE'S OWN ANSWER FOR THIS FILE (`104` §17.13 ruling 3). The
        # target is per file now, so a constant here would key two destinations'
        # answers under one dimension: a file answered by the local model would
        # reuse the cloud model's cached verdict, and `00`:44's "makes model or
        # prompt changes auditable" would be false in the one direction that
        # matters. Asked through `route` rather than off a field, which is the
        # only read this module makes.
        # The release bound (`llm_harness.store.EMPTY_DIMENSION_VALUES` says why).
        "max_dossier_tokens": authorities.max_dossier_tokens,
        "sampling": model_deepseek.JUDGE_SAMPLING,
        "model_id": _routed_target(authorities, file_id).model_id,
        # Null at A, and `build_fact_request` says why in its own words: "a fact is
        # about a file version and not about a plan, and the same fact survives a
        # re-plan". Read from the same place rather than restated, so the two cannot
        # disagree about a call that is about to be built.
        "plan_version": None,
        "policy": _policy_content(conn, authorities.policy_version),
        "prompt_fingerprint": prompt_fingerprint(authorities.prompt),
        # THE DOMAINS THIS FILE ACTIVATED, and not the signals the run carries.
        # The dimension's own sentence is "the situation's domain, which decides
        # the field allowlist", and under the owner's ruling of 11 Sep 2026 --
        # activation is per schema, by evidence -- the signal set is every schema
        # the deployment could activate and is therefore the same list for every
        # file. Keying on it would key two different allowlists under one identity,
        # which is the one thing `00`:44 asks this row to prevent. `active_domains`
        # is the same computation `active_field_allowlist` starts from, so the
        # dimension and the allowlist cannot disagree. Unchanged for a file with one
        # active domain, which is the whole of a run before the ruling.
        "schema_id": sorted(active_domains(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals)),
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

    # ONE BAD ROW IS ONE FILE'S COST, NEVER THE RUN'S. `104` R-142, and R-136 and
    # R-O before it. r10 died 1.3 minutes in with zero calls made, because a prior
    # dossier that would not rebuild raised out of this decision and out of the
    # stage; a reuse that cannot be decided is a reuse that does not happen, and
    # the file is asked. Every refusal below already returns `False` for exactly
    # that reason, and a row this deployment cannot read is one more of them.
    try:
        response = last_response(conn, prior["dossier_id"])
        if response is None:
            return False
        dossier = load_dossier(
            conn, prior["dossier_id"], release_id=response["release_id"])
        if dossier is None:
            return False
        if (dossier_address(dossier, authorities.prompt,
                            handle_key=authorities.wire_handle_key)
                != dossier.dossier_id):
            return False
    except MalformedRecord:
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


def _within_ceiling(observations: Sequence, context: Sequence,
                    name_characters: int,
                    authorities: FactCallAuthorities) -> bool:
    """Whether a dossier built from these readings fits `00`:251's ceiling.

    The same count `_call_dependencies` hands §8.6's ladder, asked a step earlier so
    the stage can build the request in the shape the ladder will pick (`104` R-145).
    One expression in one place: a second spelling here and a third in the ladder
    would drift the day either changed.

    **`name_characters` closes the third gap (`104` R-159).** Until 8 Sep 2026 this
    summed the file's own readings and the context and stopped, while the gate's
    `measure_released_tokens` counted every resolved value INCLUDING the filename --
    so the ladder could pass a dossier at rung NONE that the door then denied
    `over_dossier_ceiling`. With whole pages releasable that stopped being a rounding
    difference.

    `filename_characters` supplies the number, and it is measured off the ITEM the
    request will carry rather than off any condition: `fact_call_stage` builds
    `filename` once and hands that same variable to this measurement and to
    `build_fact_request`, so "no item is offered" and "no characters are counted"
    cannot come apart. There are two ways the item is `None` and neither needs a
    branch here -- the vocabulary does not admit the name (`name_may_be_cited` is
    False), or `filename_citation` could not address one because the filesystem
    extractor never ran over this file -- and in both the request carries no
    `Filename`, so the door releases no name either.
    """
    return sum(
        released_wire_cost(observation)
        for observation in tuple(observations) + tuple(context)
    ) + name_characters <= authorities.max_dossier_tokens


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

    **THE THREE CEILING CHECKS AND WHAT EACH ONE NOW COUNTS (`104` R-159).** Three
    places measure this dossier against `00`:251's ceiling, and before 8 Sep 2026
    they measured three different things -- which was harmless only because almost
    nothing was releasable. Once whole pages reach a local model it stops being
    harmless: a dossier the ladder passes at rung NONE would arrive at a door that
    denies it `over_dossier_ceiling`, and the file loses its call after the budget
    slot is reserved. All three now measure ONE total, the file's own readings plus
    the context shape the request is built in plus the filename when the call offers
    one:

      1. `_within_ceiling`, in this stage, choosing between R-145's two context
         shapes: `sum(len(own fill for that shape)) + sum(len(that context)) +
         name_characters`.
      2. `_call_dependencies`, feeding §8.6's ladder: `unreduced_fits` over the LINES
         shape's own fill plus the lines plus the name; `anchors_fit` over the
         preserved-anchors shape's own fill plus those excerpts plus the name. Each
         rung is measured over the fill that rung would carry, because the two shapes
         leave different remainders.
      3. `gate.measure_released_tokens`, at the door, over every RESOLVED value --
         the same three sets, after materialisation and redaction. It is at or below
         the two above: redaction only ever shortens, and `apply_redaction` refuses a
         transform that returns its input.

    The order of work in the stage follows from that. The context is gathered first
    because a neighbour rule cannot know what room is left; the vocabulary is settled
    next because it decides whether the name is offered at all; the name is measured
    third; and the file's own readings fill whatever remains. Building the file's own
    readings first -- twelve of them, by count -- is what let a dossier exceed a
    ceiling the ladder had already passed.
    """

    def steps(conn: sqlite3.Connection, file_id: str, content_hash: str):
        # `104` §18.15: A GENERATOR, AND THE ONE `yield` IS INSIDE `run_call_steps`.
        # Everything in this function reads or writes the database and therefore
        # stays on the thread that owns the connection, in the order it is written
        # here; the suspension point is the socket and nothing else. Read it as the
        # straight line it still is. `stage` below drives it inline for any caller
        # that wants one file and one answer; `harness.in_walk_order` drives many,
        # which is what lets the cloud lane hold several round trips at once.
        #
        # `104` R-175: FIRST, BEFORE ANY WORK, and recorded rather than dropped.
        # This is the second of the two turns one file gets -- site G's loop is the
        # first -- and by the time the stage is reached the file may already have
        # spent its whole budget there. Building the dossier for a call that is
        # about to be abandoned costs the run the same minutes again.
        #
        # `open_turn` before `check`, so this stage's own seconds are charged to
        # this file whatever the check decides: a file skipped here still cost the
        # run the moment it took to skip it, and the previous file's turn ends here
        # whether or not this one begins.
        #
        # `refusal_outcome` and not a quiet `return ()`: `104` R-04's failure is a
        # starved site looking exactly like a site nobody wired, and a file skipped
        # in silence looks exactly like a file the model had nothing to say about.
        # The row is the same shape a `MalformedRequest` from the builder writes, so
        # the screen and `tools.groundtruth` read it with what they already read.
        if authorities.per_file_ceiling is not None:
            authorities.per_file_ceiling.open_turn(file_id)
            try:
                authorities.per_file_ceiling.check(file_id)
            except FileTookTooLong as over:
                result = refusal_outcome(
                    conn, call_site=A_FACT, subject_ref=file_id, error=over,
                    observed_at=authorities.observed_at())
                if authorities.on_result is not None:
                    authorities.on_result(file_id, result)
                return ()
        pending = pending_fields_for(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals)
        # `104` §18.2 GAP 1: the fields the rules already answered. They are asked
        # too, with the rule's answer beside them as a flag, because `00`:42's
        # amendment gives the model the reconciliation and not the code.
        settled = settled_fields_for(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals)
        # THE LEVELS THIS RUN'S SITUATION BUILDS, read here only to decide whether a
        # settled field is worth re-opening. `open_question` applies the same set
        # further down, over `authorities.folder_levels + anchor_levels`; the anchor's
        # own levels are deliberately NOT consulted here, because reaching them needs
        # the `FactRequest` this stage has not built yet and because a settled
        # anchor-only field re-opened on its own would send a call whose entire
        # question is one flag. That narrowness is stated rather than hidden: a file
        # whose every ordinary level is settled and whose only re-openable field is
        # the anchor's `school` is still declined here, exactly as before gap 1.
        # `or ()` IS THE NO-SITUATION STATE AND NOT A DEFENCE. `folder_levels`
        # is `None` when a SCHEMA is known and no situation has been chosen
        # under it, and such a call is built and sent: the fields are the
        # schema's and only the LEVELS belong to the situation. `()` is still
        # refused at `__post_init__`, so the silent flat-vocabulary dossier
        # `require_folder_levels` exists against is still impossible -- what
        # is permitted here is the state that says so out loud.
        run_level_fields = {level.field
                            for level in (authorities.folder_levels or ())}
        # THE SETTLED HALF OF THE QUESTION, COMPUTED ONCE. It is the settled fields
        # the RUN's own situation builds folders from, and it is deliberately not
        # every settled field the file carries: `anchor_only_levels` adds `school` to
        # an anchor's levels under `105` §14.4, and a settled `school` re-opened here
        # would put back the per-file school question `104` §11.2 step 2 withdrew --
        # the one twenty files answered with whatever institution each of them
        # mentioned, filing five university essays under a high school (`104` §11.1).
        # R-131 restored that question to the files that can answer it and left it
        # withdrawn everywhere else; gap 1 is about the rules deciding a level behind
        # the model's back, and it has no business widening a different ruling.
        settled_levels = tuple(
            field for field in settled if field in run_level_fields)
        if not pending and not settled_levels:
            # THE ONE DECLINE THAT IS NOT A GAP IN COVERAGE. Every field the schema
            # allows is settled AND none of the settled ones is a folder level this
            # situation builds, so the question has no content: there is nothing open
            # to ask and nothing settled worth re-opening. `NOT_ASKED_REASONS` says so
            # with a `None`. It is still named rather than returned silently, because
            # "asked and the model said nothing" and "there was nothing left to ask"
            # are the two sentences `104` §18.2 gap 4 exists to keep apart.
            #
            # `104` §18.2 GAP 1 NARROWED THIS ROW AND DID NOT REMOVE IT. It used to
            # fire on `not pending` alone, and that is what the gap is about: a file
            # whose `subject` and `work_type` a regex had written reached no model at
            # all, and the run recorded it as settled rather than as unasked. A file
            # that still reaches this line is one no model could contribute to.
            return _not_asked(NOT_ASKED_SETTLED)
        # WHICH MODEL ANSWERS ABOUT THIS FILE, before a dossier exists, because
        # the locality is what decides what may go into one (`104` §17.13 ruling
        # 3). `None` is a file neither gate permits; the resolver's own
        # `model_route_permitted` is built from this same callable, so it has
        # already recorded `privacy_withheld` and stopped -- this is the backstop
        # for anyone who wires a stage another way, and it sends nothing.
        chosen = authorities.route(file_id)
        if chosen is None:
            # `104` §18.2 gap 4. The backstop names its reason like every other
            # decline, and the row it asks for is `privacy_withheld` -- the same
            # reason `_write_bars` writes when the resolver's own
            # `model_route_permitted` stops first, because it is the same fact about
            # the same file. Reaching this line at all means the two predicates
            # disagreed, and a duplicate row under the right reason is a far smaller
            # defect than a file recorded as asked.
            return _not_asked(NOT_ASKED_NO_ROUTE)
        model_client, model_target = chosen
        locality = model_target.locality
        # `104` R-159: WHAT THIS FILE MAY OFFER, ordered, and not yet bounded. The
        # cap and the ceiling are spent below, once the context and the filename have
        # taken their share; this set is the answer to "does the file have anything
        # to say", which is a different question and is the one the guard asks.
        offered = ordered_releasable_observations(
            conn, file_id=file_id, content_hash=content_hash, locality=locality,
            limit=authorities.max_released_observations,
            # `104` §18.2 gap 6: THE PENDING FIELDS ARE WHAT THE ORDER IS MEASURED
            # OFF. The offer is ordered for the question this call is about to ask,
            # and the question is `pending` -- not the whole allowlist, which
            # includes fields this file has already settled and whose evidence would
            # then be ordering the readings for fields nobody is asking.
            fields=pending)
        if not offered:
            # A file with no readings of its own is not asked, and context does not
            # change that. `104` R-135 carries a NEIGHBOUR's words to a file that has
            # something to say and cannot say this; a file with nothing at all would be
            # answered entirely out of another document, which is a fact about that
            # document. Constitution 2's "any successfully-read file must reach the
            # model" is about files that were read.
            #
            # THE GUARD IS ON THE UNBOUNDED SET AND NOT ON THE FILL (`104` R-159).
            # "Nothing may be released" and "everything releasable is longer than
            # what the context left" are different states, and only the first is this
            # file having nothing to say. In the second the call still goes out
            # carrying the context and the name, and the ladder measures that truthfully
            # -- reporting `unreduced_fits=False` to force a deferral would be lying
            # to §8.6 about a dossier that does fit.
            #
            # AND THE TWO WAYS OF HAVING NOTHING TO SAY ARE DIFFERENT SENTENCES
            # (`104` §18.2 gap 4). A file P5 could not read at all offers nothing
            # because nothing was extracted, and that is a fact about the reader; a
            # file with forty readings every one of which is in an always-local zone,
            # is the whole document, or carries a sensitive signal offers nothing
            # because the privacy rules refused them all, and that is a fact about
            # what may leave the device. The store is asked ONLY here, on the path
            # that is already about to return, so an ordinary call pays nothing for
            # the distinction.
            read_anything = bool(observations_for_version(
                conn, file_id=file_id, content_hash=content_hash))
            return _not_asked(NOT_ASKED_ALL_REFUSED if read_anything
                              else NOT_ASKED_NOTHING_READ)
        # `104` R-135: the anchor headings near this file, if the deployment offers
        # any and this call is asking a field they answer. BEFORE the request, because
        # they are part of what it is built from -- the identity below, the budget
        # measurement, the citable set and the release target all have to see them.
        #
        # AND BEFORE THE FILE'S OWN READINGS ARE CHOSEN (`104` R-159), which is the
        # order this stage did not have. The context is gathered by a neighbour rule
        # that knows nothing about how much room is left; the file's own readings are
        # what fills whatever remains. Doing it the other way round -- twelve of the
        # file's own pages first -- is how a dossier came to exceed the ceiling that
        # the ladder had already passed.
        # `104` §18.2 GAP 1: THE FIELDS THIS CALL IS ABOUT, which since gap 1 is not
        # the pending ones alone. The neighbour rule is asked which anchor headings
        # answer these fields, and a `subject` the rules settled and the model is now
        # being asked to reconcile is exactly the field a syllabus beside the file
        # speaks to -- withholding the context for it would flag the disagreement and
        # then take away the one reading that could settle it. The set is `pending`
        # plus the settled fields this situation builds folders from, which is the
        # same set the decline above tests and a superset of what `open_question`
        # finally offers; a neighbour rule that is asked about one field too many
        # returns readings the fill may drop, and one asked about one too few returns
        # nothing that could be dropped back in.
        answerable = tuple(pending) + settled_levels
        context = ()
        if authorities.anchor_context_for is not None:
            context = tuple(authorities.anchor_context_for(
                conn, file_id=file_id, content_hash=content_hash,
                fields=answerable))
        request = build_request(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals,
            normalizers=authorities.normalizers,
            # So a citation naming one of them passes §3.6's check 2. Without this the
            # model would be shown a reading it is forbidden to cite, which is worse
            # than not showing it: `CITATION_NOT_FOUND` rejects the whole claim.
            context_observations=context)
        if not request.allowlist:
            # `104` §18.2 gap 4. No domain activated and no universal field remains,
            # so §3.5's closed vocabulary is empty and every answer would be out of
            # schema -- which is `field_not_in_active_schema`, the reason P6 already
            # publishes for exactly that judgement at §3.6's check 1. The row is
            # written for the fields that are still PENDING, which is the honest
            # subject: they are open, and this situation's schema has no place to
            # put an answer to them.
            return _not_asked(NOT_ASKED_NO_SCHEMA)

        # What is still open on THIS file, in the order the tree is built in. A
        # subset of `request.allowlist`, which is what check 1 measures the answer
        # against, so nothing offered here can be rejected for being out of schema.
        #
        # THE ANCHOR'S OWN LEVELS ARE ADDED HERE AND NOWHERE ELSE (`105` §14.4).
        # `authorities.folder_levels` is what every file of the situation is asked;
        # `anchor_only_levels` answers what THIS file may be asked on top of it,
        # and it answers `()` for all but an anchor of a permitted kind. Added
        # before `open_question` rather than after it so the vocabulary and the
        # shown levels are one computation: a level offered without its field, or a
        # field offered without its level, is the mismatch
        # `dossier._folder_levels_body` refuses.
        anchor_levels = anchor_only_levels(request, authorities.anchor_only)
        vocabulary, visible_levels = open_question(
            # `None` STRAIGHT THROUGH, and not `or ()`: the two mean opposite
            # things to `open_question`. `()` narrows the question to nothing;
            # `None` says there is no situation to narrow it BY, and the schema's
            # own fields are what this file is asked.
            pending, (None if authorities.folder_levels is None
                      else authorities.folder_levels + anchor_levels),
            # `104` §18.2 GAP 1. A settled level field is a question again, flagged
            # with what the rules answered -- and it is `settled_levels` and not the
            # whole settled set, so the ANCHOR-ONLY levels added above can pick up
            # nothing from it. `open_question` intersects with the levels it is given
            # exactly as it does for the pending half; passing everything settled
            # would let `105` §14.4's `school` back into a per-file question through
            # a door gap 1 did not open.
            settled_levels)
        # A FILENAME IS NEVER A SOURCE FOR AN ANCHOR-ONLY FIELD (`105` §14.4), and
        # the only way to say that to a model is not to show it the name. A call
        # whose whole question is the anchor's own -- the syllabus whose subject,
        # term and kind are already settled, asked its school and nothing else --
        # is offered no `Filename` item, so the name cannot be cited for the one
        # field the ruling forbids it to answer.
        #
        # MEASURED, on the six-file corpus of `tests/integration/
        # test_local_model_fact_pass.py`: the local model answered `school` by
        # copying the file's own name, `PHYS 1401 syllabus.txt`, the single
        # `school` fact the run wrote cited the filename observation and nothing
        # else -- `104` R-95's finding reproducing live -- and that fact then
        # entered the group dossier and cost the run its site-B call. `104` R-95's
        # own corpus is the same failure at scale: 38 model facts on 52 files,
        # every one a `school`, most of them filenames.
        #
        # NARROW ON PURPOSE, and the gap is stated rather than papered over: a
        # call that offers `school` BESIDE an open `subject` or `term` still shows
        # the name, because those two are answered from names legitimately and
        # blinding them would cost the coverage this wave exists to win. On such a
        # call the model may still cite the name for `school`; the fact is written,
        # and P10's two-anchor rule refuses it a folder level
        # (`upstream._group_level_agreed`). Closing it at the fact itself needs a
        # per-field citation screen inside P8's check 2, which is a seam this
        # module does not own.
        name_may_be_cited = bool(
            set(vocabulary) - {level.field for level in anchor_levels})

        # ================================================================
        # `104` R-159: THE FILL, and it runs here because it needs every term
        # above it. The three things a site-A dossier releases are the file's own
        # readings, the anchor context, and the filename -- and the filename is
        # offered only when `name_may_be_cited`, which is not known until the
        # vocabulary is. So the order is: context, then vocabulary, then the name's
        # cost, then whatever room is left goes to the file's own readings.
        #
        # `104` §18.2 GAP 6 PUT ONE READING AHEAD OF THE CONTEXT IN THAT ORDER. The
        # file's own strongest reading is admitted before the context spends the
        # ceiling, because the call is about this file and a dossier carrying only a
        # neighbour's words answers a question about the neighbour. `own_readings`
        # carries the whole argument and the two states it distinguishes.
        #
        # For a CLOUD target this changes nothing measurable: `within_dossier_budget`
        # returns the same first `max_released_observations` readings it always did,
        # and the remainder below is only a ceiling the count cap almost never
        # reaches. For a LOCAL target the count cap yields to the ceiling, and the
        # remainder is what makes "within the dossier ceiling" in the owner's ruling
        # a real bound rather than a hope.
        # ================================================================
        filename = (filename_citation(conn, file_id)
                    if name_may_be_cited else None)
        name_characters = filename_characters(conn, filename)

        def own_readings(shown_context: Sequence) -> tuple[Sequence, DossierFill]:
            """`fill_reserving_top_reading` with this call's three terms bound.

            The closure exists to carry `offered` and the name's cost, which do not
            change between the two context shapes; the arithmetic and the argument
            for it are the published function's, so a test can drive the reserve
            without building a stage around it.
            """
            return fill_reserving_top_reading(
                offered, shown_context,
                ceiling=authorities.max_dossier_tokens - name_characters)

        lines_context, lines_fill = own_readings(context)
        lines_readings = lines_fill.taken
        fill = lines_fill
        observations = lines_readings
        # `104` R-145: §8.6's preserved-anchors shape of the same context, or `None`
        # when the lines fit or the deployment offers no second shape. `shown` is
        # the shape the request is BUILT in, which is the shape the ladder will
        # pick: the lines when they fit, the anchors' own spans when only those do,
        # and the lines again when neither does -- that call is deferred before
        # any of it is sent, and `_call_dependencies` measures both shapes so the
        # dossier records the rung it was actually built at.
        #
        # The rung still matters under the fill, and this is when: the fill can only
        # give the file's own readings the room the CONTEXT left, so a context that
        # exceeds the ceiling on its own leaves a remainder of zero and no reading
        # fits. That is exactly the state R-145 built the second shape for, and it is
        # now reached by measuring rather than by counting readings.
        #
        # **THE TRIGGER IS MEASURED AGAINST THE WHOLE CONTEXT, AND THAT IS THE POINT
        # AFTER `104` §18.2 gap 6's RESERVE.** The reserve makes the LINES shape fit
        # by taking context lines away, so asking this question about the trimmed
        # context would answer yes every time and R-145's shape would never be built
        # again. It is asked about the context as it arrived: "does the anchor
        # context fit whole beside this file's own readings", and when it does not,
        # the anchors' own spans are tried BEFORE any line is dropped. Dropping whole
        # lines is the blunter remedy of the two -- it can take the very line that
        # names the course -- so it stays the last one.
        excerpts = None
        own_excerpts = None
        if (authorities.anchor_excerpts_for is not None
                and authorities.anchor_context_for is not None
                and not _within_ceiling(observations, context, name_characters,
                                        authorities)):
            excerpts = tuple(authorities.anchor_excerpts_for(
                conn, file_id=file_id, content_hash=content_hash,
                # THE SAME SET THE LINES SHAPE WAS GATHERED FOR (`104` §18.2 gap 1).
                # R-145's two shapes are two renderings of ONE neighbourhood, and a
                # second shape gathered for a different question would make the
                # ladder's two measurements about two different dossiers.
                fields=answerable))
            excerpts_context, excerpts_fill = own_readings(excerpts)
            own_excerpts = excerpts_fill.taken
        if (excerpts is not None
                and _within_ceiling(own_excerpts, excerpts, name_characters,
                                    authorities)):
            shown, observations = excerpts_context, own_excerpts
            # THE CUT OF THE SHAPE THAT WAS BUILT (`104` §18.2 gap 5). The excerpts
            # shape leaves a different remainder than the lines shape, so it drops a
            # different set; the call carries this one and the record must be about
            # the call.
            fill = excerpts_fill
        else:
            # THE LINES, TRIMMED ONLY IF THE RESERVE HAD TO TRIM THEM, and otherwise
            # `context` itself. Reaching here with a trimmed shape is the state that
            # used to send the file's own evidence as nothing and let §8.6's ladder
            # fall to DEFERRED: the context and the name alone over the ceiling. It
            # now sends the file's strongest reading and as much of the neighbour's
            # words as the ceiling leaves, which is `104` §18.7's ruling in the
            # owner's own words -- "files should not be refused at all" -- and the
            # trim is on the record rather than silent.
            shown = lines_context
        if shown is not context:
            # The ONLY field that changes is the context, and `build_request` is
            # asked again rather than the tuple being patched onto the record it
            # already returned: `FactRequest` is frozen, and the allowlist and the
            # existing facts it also carries are reads of the store this call must
            # not make twice and get two answers to. Reached only when the lines
            # shape did not fit, which is where the second read was always paid.
            request = build_request(
                conn, file_id=file_id, content_hash=content_hash,
                activation_signals=authorities.activation_signals,
                normalizers=authorities.normalizers,
                context_observations=shown)

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
            observations=observations, authorities=authorities,
            # `104` R-135: the context READINGS are part of the question, and they
            # need a TERM of their own. Folded into `observations` they would change
            # nothing -- the only term read off the readings is the set of
            # `(extractor, version)` pairs, and a syllabus is read by the same
            # extractor as the file beside it. `context_refs` says why in full.
            context=shown)
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
            # `104` §18.15: `yield from`, so a refusal raised on the far side of
            # the socket still lands in this `try`. An exception carried back
            # through a resume propagates out of the sub-generator exactly as one
            # raised inside a call did, which is what keeps R-O's record intact.
            result = yield from run_call_steps(
                conn,
                build_fact_request(
                    request, observations,
                    # The item measured above, not a second call for the same row:
                    # a name counted at one length and released at another is the
                    # gap `104` R-159 closed.
                    filename=filename,
                    context=shown,
                    # THE PAIR THIS FILE WAS ROUTED TO, chosen once at the top
                    # of the stage and carried down. Reading the authorities again
                    # here would be a second answer to a per-file question.
                    model_target=model_target,
                    prompt=authorities.prompt,
                    max_dossier_tokens=authorities.max_dossier_tokens,
                    # `104` §18.2 gap 5: the fill that produced `observations`, so
                    # the request carries how much of this file's offer the ceiling
                    # took. `fill` is `lines_fill` or `excerpts_fill` above, chosen
                    # by the same branch that chose `shown` -- the cut recorded is
                    # the cut of the dossier that is about to be sent.
                    fill=fill,
                    # `104` §18.2 gap 1: THE VOCABULARY, not the pending set. The
                    # flags are about the fields this call OFFERS, and the offer is
                    # `open_question`'s answer -- a flag about a field the model may
                    # not propose is a line it can do nothing with, and rule 11 makes
                    # every unusable line a cost.
                    asked_fields=vocabulary),
                gate=authorities.gate,
                model_client=model_client,
                prompt=authorities.prompt,
                validation_dependencies=_call_dependencies(
                    request, vocabulary, folder_levels=visible_levels,
                    authorities=authorities,
                    # `104` R-135: the ladder measures what the DOSSIER will carry,
                    # and it will carry the context readings too. Measuring the file's
                    # own alone would tell §8.6's first rung a dossier fits that does
                    # not. `104` R-145: the first rung is the LINES shape and the
                    # preserved-anchors rung is the excerpts shape, each measured as
                    # its own list, so the rung the dossier records is the one it
                    # was built at.
                    #
                    # `104` R-159: EACH RUNG IS MEASURED OVER ITS OWN FILL. The two
                    # shapes leave different remainders for the file's own readings,
                    # so `lines_readings` belongs to the lines rung and
                    # `own_excerpts` to the anchors rung; passing the chosen shape's
                    # fill to both would report a total for a dossier that was never
                    # built. `name_characters` is added to both by
                    # `_call_dependencies`, because the name travels in either.
                    #
                    # `104` §18.2 GAP 6: EACH RUNG TAKES ITS SHAPE'S OWN CONTEXT,
                    # `lines_context` and `excerpts_context`, and that is not
                    # tidiness. The reserve can trim a context to leave the file's
                    # own strongest reading room, and the shape that goes out is the
                    # trimmed one -- so measuring the rung against the context AS IT
                    # ARRIVED would report a dossier over the ceiling for a call that
                    # fits, `anchors_fit` would answer False, and `plan_reduction`
                    # would DEFER a call whose bytes were already under the bound.
                    # The rung is about the dossier that was built, which is the
                    # rule the two `_within_ceiling` calls above already follow.
                    observations=tuple(lines_readings) + tuple(lines_context),
                    name_characters=name_characters,
                    anchor_observations=(
                        None if excerpts is None
                        else tuple(own_excerpts) + tuple(excerpts_context)),
                    # `104` §18.2 gap 5: THE OFFER BEFORE THE FILL SPENT THE CEILING
                    # ON IT, which is what "unreduced" has to mean for the word to
                    # be worth recording. `offered` is what
                    # `ordered_releasable_observations` returned at the top of the
                    # stage; the context beside it is the LINES shape's, because the
                    # first rung is the shape a file would have been asked in had
                    # nothing needed reducing at all.
                    unreduced_observations=tuple(offered) + context),
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

    def stage(conn: sqlite3.Connection, file_id: str,
              content_hash: str) -> "tuple[str, ...] | StageOutcome":
        """One file, asked and answered on this thread. `104` §18.15's serial form.

        `FactResolver` reaches for `stage.steps` when it is driving a lane and
        calls this when it is not, so a stage table wired anywhere else keeps
        working with no knowledge of either.
        """
        return drive_inline(steps(conn, file_id, content_hash))

    #: THE SAME STAGE, LEFT UNDRIVEN, for a caller that owns a lane. Hung off the
    #: callable rather than returned beside it because `facts.resolver.Stage` is a
    #: one-argument protocol every branch of `DEGRADATION_ORDER` is read through,
    #: and widening that protocol for one producer would make every other stage
    #: answer a question it has no round trip to have an opinion about.
    stage.steps = steps
    return stage
