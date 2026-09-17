"""What one run of the product actually did, read out of its plan database.

The database is the measurement surface, not the report on screen. The report is
written for a person and changes as its sentences improve; `placement_decisions`,
`tree_nodes`, `file_facts`, `extraction_runs`, `classifications` and
`release_ledger` are the product's own record of what it concluded, and they say
things the report does not -- including, on the day this was written, that three
files were marked protected while the screen said none were.

`release_ledger` joined that list on 10 Sep 2026 for `104` §18.7. The scorecard's
protected verdict has to answer "did this file's bytes leave the device", and the
only truthful answer is the one the gate WROTE when it minted the release: the
ledger stores the whole `ModelTarget`, locality included, so the harness reads a
recorded fact rather than guessing a destination from a model's name.

Nothing here opens a file of the owner's. It reads a SQLite database the product
wrote, and the one thing it deliberately does NOT read is `text_units.text`:
`complete_extracted_text` is in `privacy.vocabulary.ALWAYS_LOCAL`, and the
harness only ever needs to know HOW MANY units there are, never what is in them.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

#: `filesystem.record` observes the directory entry -- name, size, timestamps --
#: and never the bytes. Every other extractor opens the file.
FILESYSTEM_ONLY = "filesystem.record"

#: Extractors that recover text a person would recognise as the file's content.
#: `image.metadata` is not among them: a JPEG's EXIF coming back `complete` is
#: metadata recovered, not content, and counting it as content would flatter the
#: extraction number for every photograph in the corpus.
TEXT_PRODUCING = frozenset({
    "pdf.text", "text.structured", "docx.structure", "ocr", "ocr.apple_vision",
    "archive.manifest", "pptx.structure", "xlsx.structure", "html.structure",
    "email.structure",
})

#: P4's completeness words, best first. A file gets the best word any of its
#: content extractors returned: if `pdf.text` says `complete`, the content was
#: recovered, whatever a second-tier attempt said afterwards.
COMPLETENESS_ORDER = (
    "complete", "capped", "partial", "metadata_only", "deferred",
    "unsupported", "failed", "unreadable",
)
_RANK = {word: i for i, word in enumerate(COMPLETENESS_ORDER)}

#: P8's spelling for the placement site, and the two verdict outcomes
#: `placement.p8_seam.transcribe` turns into a placement. Spelled here rather than
#: imported from `src/llm_harness/vocabulary.py` for the reason every other value
#: in this package is read from the database and not from the product: the harness
#: measures what a run WROTE, and a run written by an older build is still a run
#: this must read. `shadow.ACCEPTING` is this tuple, imported, so there is one
#: spelling and not two.
C_PLACEMENT = "C_placement"
ACCEPTING_VERDICTS = ("accept_direct", "accept_context_supported")

#: The verdict outcomes that mean the model's answer FAILED -- `105` §14.7's
#: "invalid output". The validator refused the claim, so the run got no usable
#: answer for that file however the placement was afterwards decided.
#:
#: WHY THE VERDICT AND NOT THE RESPONSE BYTES. A response that did not decode, or
#: decoded and did not fit the shape, is recorded as a `reject` verdict carrying
#: the reason `SCHEMA_INVALID` (`tests/p8/test_p8_json_decode_at_the_tail.py`), so
#: "failed schema or validation" is entirely readable from `llm_verdict.outcome`.
#: Reading `llm_response.response_bytes` here to tell the two apart would put a
#: column that carries `cited_span` -- quoted file content -- inside the one module
#: whose docstring promises it counts and never reads.
#:
#: `abstain` is deliberately NOT here. It is the model declining to answer, which
#: is an abstention and is scored as one; calling it invalid would count the
#: caution the harness asks for as a defect.
FAILED_VALIDATION = ("weak", "reject")

#: P11's review policies, spelled here for the reason `C_PLACEMENT` is spelled
#: here: the harness reads what a run WROTE, and a run written by an older build
#: is still a run this must read. Importing `placement.vocabulary` would make the
#: instrument agree with the product by construction.
#:
#: `104` R-151. A HELD PLACEMENT IS A PLACEMENT. The model named a folder; the only
#: thing the policy withholds is the MOVE, and a person reading the screen sees a
#: held placement as a proposal -- "we suggest this folder; confirm". So these
#: words never reach `score_sorting`: the five classes compare the proposed node
#: against the label whatever is written here, and the hold is counted BESIDE them,
#: because "exact" and "exact, and waiting for you" are two different facts and a
#: reader needs both.
BLOCKED_PENDING_USER = "blocked_pending_user"
REVIEW_REQUIRED = "review_required"
AUTO_ELIGIBLE = "auto_eligible"

#: The policies that mean nothing moves until the person says so.
HELD_POLICIES = (BLOCKED_PENDING_USER, REVIEW_REQUIRED)

#: `104` R-165's three, spelled here for the reason the policies above are: this
#: harness has to read a database an older build wrote, so it cannot import a
#: vocabulary that may not have existed when the run happened.
#: `test_groundtruth_held_proposals.py` pins the spellings against
#: `placement.vocabulary` so a rename fails a test instead of silently counting
#: nothing.
DECIDED_BY_MODEL = "model"
DECIDED_BY_RULE = "rule"
DECIDED_BY_USER = "user"
DECIDERS = (DECIDED_BY_MODEL, DECIDED_BY_RULE, DECIDED_BY_USER)


#: SPEC §6's locality that means the bytes LEFT THE DEVICE. `privacy.vocabulary`
#: owns it; this is spelled here for the reason `C_PLACEMENT`, the review policies
#: and the deciders are spelled here -- the harness reads a database an older build
#: wrote, and importing the product's vocabulary would make the instrument agree
#: with the product by construction. `test_groundtruth_protected_release.py` pins
#: this spelling against `privacy.vocabulary.CLOUD_LOCALITY`, so a rename over
#: there fails a test here instead of silently measuring nothing.
CLOUD_LOCALITY = "cloud"

#: What a target that cannot be read out of the ledger is called.
#:
#: NOT dropped, and that direction is the point. A `release_ledger` row was written
#: by the gate itself, so a row whose `model_target` this cannot parse is a release
#: that happened and whose destination is unknown -- and unknown is not "local". The
#: harsher reading is `_placeable_chains`'s own ("a number that flatters the product
#: on the strength of a missing column is the one failure this package exists to
#: refuse"), and it can only ever fire on a defect: either the target's stored shape
#: moved and this reader is stale, or the gate wrote something it should not have.
UNREADABLE_TARGET = "unreadable_model_target"

#: The tables that name a `release_id` beside the `dossier_id` it was spent on.
#:
#: `llm_call_failure` IS ONE OF THEM, deliberately, and `transport.issue` is why.
#: It spends the release inside its transaction -- "before the spend, before the
#: socket" -- and only then calls `model_client.invoke`; both `record_call_failure`
#: arms sit past that call, one on the client raising and one on it returning bytes
#: of the wrong type. So a row in this table is a call whose payload had already
#: gone to the client. Reading only the successful two would let a provider's
#: timeout launder a release nobody can recall, and "the answer was unusable" is
#: not the same sentence as "nothing was sent".
#:
#: The weaker claim holds even where that ordering someday does not: the gate
#: MINTED a cloud release for this file, so the per-file predicate had already let
#: the door open cloud-ward on protected material. What the provider did afterwards
#: is not what the ruling is about.
#:
#: Read defensively, one table at a time: a database written before any one of them
#: existed still yields what the others hold, where a single joined SELECT naming a
#: missing table would come back empty and report a clean run.
RELEASE_BEARING_TABLES = ("llm_response", "llm_call_usage", "llm_call_failure")


@dataclass(frozen=True)
class Observation:
    """What the run concluded about one file."""

    path: str                      # corpus-relative
    indexed: bool
    excluded_by: str | None        # the §1.1 rule that set it aside, if any
    opened: bool                   # any extractor beyond `filesystem.record`
    text_units: int                # how many, never what
    #: `evidence` rows from the file's own BYTES -- `filesystem.record` excluded,
    #: because it observes the directory entry and every file has four of them.
    #: Counting those made a first attempt at this line read "199 of 199, 100%",
    #: which is true and says nothing.
    evidence_rows: int
    #: Of those, the ones a vocabulary could match a word against: the same
    #: text-producing extractors `content_recovered` uses. EXIF from a JPEG is
    #: an observation and is not prose, and the difference decides whether a
    #: file that went unmarked was SHOWN the words or merely never read.
    prose_evidence_rows: int
    extractors: tuple[str, ...]
    completeness: str              # the P4 word
    content_recovered: bool
    protected_marked: bool
    handling_class: str | None
    fields: Mapping[str, str]      # field_key -> canonical value, active facts
    #: Where each filled field came from -- 'rule', 'direct', 'llm_interpretation'.
    #: The only way to tell which half of the pipeline earned a number.
    field_origins: Mapping[str, str]
    unresolved_fields: tuple[str, ...]
    outcome: str | None            # 'place', 'abstain', ... or None
    destination: tuple[str, ...]   # folder labels, root first
    asked: bool                    # the decision carried a question for the person
    #: The model's own answer ABOUT THIS FILE failed schema or validation --
    #: `105` §14.7's fifth outcome class. See `FAILED_VALIDATION` for why this is
    #: read from the verdict and never from the response bytes.
    #:
    #: Last, and defaulted, so every existing construction of this class keeps
    #: working unchanged. A database with no `llm_*` tables leaves it `False` for
    #: every file, which is the truth about such a run: no model answered, so no
    #: model answer failed.
    invalid_model_output: bool = False
    #: What P11 wrote in the decision's `review_policy` -- `auto_eligible`,
    #: `review_required`, `blocked_pending_user`, or None when the run recorded
    #: none. `104` R-151: read so the scorecard can say whether a placement it
    #: scored is one the product would MOVE or one it is holding out as a proposal.
    #:
    #: READ FROM THE PAYLOAD, not from the column, and for the same reason `asked`
    #: is: `_rows` raises rather than swallowing, so naming a column in the SELECT
    #: would make a run written before that column existed unreadable ENTIRELY --
    #: every decision in it would vanish, and the scorecard would read `no
    #: decision` for a corpus the product had sorted. The payload is
    #: `asdict(decision)`, so it carries the field for every build that had it.
    #:
    #: Last and defaulted, like `invalid_model_output` above, so every existing
    #: construction of this class keeps working unchanged.
    review_policy: str | None = None
    #: WHO chose the folder this run proposed -- `model`, `rule`, `user`, or None
    #: when the run recorded nobody. `104` R-165: §13.5 rules that every placement
    #: goes through the model, and until this field existed the scorecard graded
    #: the row on where files landed and could not say who decided, so a rule that
    #: fired first was indistinguishable from a model verdict on every number.
    #:
    #: READ FROM THE PAYLOAD, and for the same reason `review_policy` is: `_rows`
    #: raises rather than swallowing, so naming a column that a run written before
    #: this build has not got would make every decision in it vanish.
    #:
    #: None IS NOT A FOURTH DECIDER. It is the absence of one, and the block that
    #: prints these counts prints that remainder separately, exactly as
    #: `POLICY_NOT_RECORDED` is printed beneath the review policies.
    decided_by: str | None = None
    #: `104` §18.100: the GROUPS this run put this file in, ids only.
    #:
    #: Last and defaulted, for `review_policy`'s own stated reason: a database
    #: written before the grouping tables existed has none, and the truthful
    #: reading of such a run is that it formed no groups -- not that it is
    #: unreadable. `group_cohesion` counts a file with no group against its
    #: owner's group, which is `00`:259's rule and not an accident of this
    #: default.
    group_ids: tuple[str, ...] = ()
    #: Every CLOUD target this run released this file's dossier to, named
    #: `provider/model_id` out of the release the gate minted. Empty means nothing
    #: about this file left the device -- which is the ordinary case and, for a
    #: protected file, the required one.
    #:
    #: `104` §18.7 (9 Sep 2026), the owner confirmed twice: protected material IS
    #: opened on this machine and shown to the LOCAL model; what it may never do is
    #: reach a cloud one. So "was it opened" stopped being the protected question
    #: and "where did it go" became it, and this is the column that answers it.
    #:
    #: READ OFF THE LEDGER'S OWN `locality`, never off the model's name. `readers.
    #: model_ollama` is the local provider on this machine today and the local model
    #: is whatever `GRAPH_AGENT_LOCAL_MODEL` names, both of which change without the
    #: meaning of this column changing; a harness that compared `model_id` against a
    #: remembered name would report a breach the day the owner pulled a different
    #: local model, and would report a clean run the day a cloud provider served one
    #: with the same name. `privacy.binding` stores the whole `ModelTarget` beside
    #: the release it minted, locality included, so the run has already written down
    #: the answer and this only has to read it.
    #:
    #: Last and defaulted, like the two above, so every existing construction of this
    #: class keeps working unchanged and a database with no `llm_*` tables leaves it
    #: empty for every file -- the truth about such a run: nothing was released
    #: because nothing was called.
    cloud_releases: tuple[str, ...] = ()

    @property
    def released_to_cloud(self) -> bool:
        """This file's dossier reached a target off this device."""
        return bool(self.cloud_releases)

    @property
    def held(self) -> bool:
        """This run PLACED the file and is holding the move for the person.

        Only a placement can be held. An abstention carries a review policy too --
        P11 computes one for every decision -- and counting that would report a
        hold on a file nothing was proposed for.
        """
        return self.outcome == "place" and self.review_policy in HELD_POLICIES

    @property
    def branch(self) -> str:
        """The top-level folder this file went into, or `""` if it went nowhere.

        `00` amendment 7 makes each branch one situation, so this is the whole of
        "which life was it filed under" and `score_situation` reads contamination
        off it. A PROPERTY and not a field: `destination` is already the folder
        chain root first -- the same root every chain in `RunObservation.
        node_paths` starts with -- so a stored copy would be a second answer to a
        question the record already answers.
        """
        return self.destination[0] if self.destination else ""

    @property
    def extension(self) -> str:
        suffix = Path(self.path).suffix.lower()
        return suffix or "(none)"

    @property
    def classified(self) -> bool:
        """P7 gave this file a handling class.

        §8.4 makes a handling class a precondition of asking a model, so an
        unclassified file cannot reach one whatever else is wired. This is the
        gate every later stage stands behind, which is why it is reported on a
        line of its own rather than folded into extraction.
        """
        return self.handling_class is not None


@dataclass(frozen=True)
class RunObservation:
    """What one `--situation` run of the product did to the whole corpus."""

    situation: str
    label: str
    promised_levels: tuple[str, ...]
    files: Mapping[str, Observation]
    structural_questions: int
    node_count: int
    built_depth: int               # deepest folder chain below the top level
    report: str
    #: What the model path actually did this run. Every count is a table the
    #: product wrote, never a guess from the report on screen.
    model: Mapping[str, int] = field(default_factory=dict)
    #: How many of `model`'s rows were HANDED to this run by
    #: `--reuse-answers-from` rather than bought by it (`104` R-123). Empty on
    #: every ordinary run. Carried beside `model` and never subtracted from it
    #: here: this class reports what is in the database, and what that means for a
    #: reader is the scorecard's sentence to write.
    seeded: Mapping[str, int] = field(default_factory=dict)
    #: The prior run those rows came from, as a line a person can act on: the
    #: directory and the commit that produced it. Counts without a source cannot
    #: be checked by anybody, which is the whole reason a seeded row is labelled.
    seeded_from: str = ""
    #: R-46's two-sided count: files this run stopped BEFORE a model, split by
    #: which of the two stops caught them. A scoreboard that asked
    #: `cli.model_route_permitted` and stopped reported "19 blocked" while 130
    #: more were refused at the door, and a number meaning "the route let N
    #: through" was read as "N reached a model".
    blocked_at_route: int = 0
    #: The door's own refusals, keyed by the word it refused with. Read from what
    #: the run RECORDED, not predicted by re-running the gate --
    #: `tools.groundtruth.payload` is the instrument that predicts, and the two
    #: answer different questions about the same corpus.
    gate_refusals: Mapping[str, int] = field(default_factory=dict)
    #: Files that reached neither: nothing releasable, so no dossier was built and
    #: there was nothing for the gate to refuse. Counted because R-46 is that a
    #: file which did not reach a model must be counted somewhere.
    never_built: int = 0
    #: Every folder chain this run's tree holds that a file may actually be filed
    #: into, root first -- `tree_nodes` where `accepts_placement`. It is what
    #: `105` §14.7's "the run had no legal candidate" is decided against: a file
    #: whose right folder the run never built could not have been filed there, and
    #: an abstention on it is the honest answer rather than a miss.
    #:
    #: `accepts_placement` and not merely "a node with that name": legal is the
    #: product's own word, and a hub that refuses placement is not a candidate.
    #: Empty on a run that built no tree, which makes every abstention appropriate
    #: -- the right attribution, because the loss is the tree's and not the
    #: placer's.
    node_paths: tuple[tuple[str, ...], ...] = ()


#: The tables the LLM path writes. A run that called nothing leaves them all at
#: zero, which is a measurement and not an absence of one.
MODEL_TABLES = ("llm_dossier", "llm_response", "llm_verdict", "llm_refusal",
                "llm_call_failure", "llm_pre_call_abstention",
                "llm_grounding_report", "llm_budget_reservation")


#: Where `record_refusal` puts P7's word. `_payload` serialises the whole
#: `Refusal`, whose `denied` half carries the reason, so the word is one level in.
#: Read defensively: a payload this cannot read is counted under its own name
#: rather than dropped, because dropping it would be the undercount again.
def _refusal_reason(payload: str) -> str:
    try:
        loaded = json.loads(payload)
    except (TypeError, ValueError):
        return "unreadable_refusal_payload"
    if isinstance(loaded, dict):
        denied = loaded.get("denied")
        if isinstance(denied, dict) and isinstance(denied.get("reason"), str):
            return denied["reason"]
        if isinstance(loaded.get("reason"), str):
            return loaded["reason"]
    return "unstated"


def _blocked_tally(connection) -> tuple[int, dict[str, int], int]:
    """The three numbers R-46 needed, all from tables the product wrote.

    **Route.** `unresolved` rows reading `privacy_withheld` are what
    `facts.resolver` writes when `cli.model_route_permitted` says no, one per open
    field, so the FILES are what is counted and not the rows.

    **Gate.** `llm_refusal`, grouped by the reason inside the payload P7 denied
    with. Grouped rather than summed because "protected" and "no safety evidence"
    are different things to fix and one number hides which.

    **Never built.** Files with no dossier, no refusal and no response: nothing
    releasable, so there was nothing to refuse. A file that reached no model has
    to be counted somewhere, and this is the somewhere for these.
    """
    try:
        route = _rows(connection, "select count(distinct file_id) as n from "
                                  "unresolved where reason = 'privacy_withheld'")
        at_route = route[0]["n"] if route else 0
    except sqlite3.Error:
        at_route = 0
    gate: dict[str, int] = {}
    try:
        for row in _rows(connection, "select payload from llm_refusal"):
            reason = _refusal_reason(row["payload"])
            gate[reason] = gate.get(reason, 0) + 1
    except sqlite3.Error:
        gate = {}
    # THE REMAINDER, SO THE THREE PARTITION AND CANNOT DOUBLE-COUNT. A file
    # withheld at the route has no dossier row, and so does a file the gate
    # refused: `record_dossier` fires inside `_issue_and_validate`, which
    # `run_call` reaches only after `gate.release` has returned `Released`. So
    # "included files with no dossier" is all three groups at once, and printing
    # it as the third beside the other two would report 19 + 149 + 176 blocked
    # files out of 176 -- R-46's own failure, counting one file twice, on the
    # line built to stop it.
    #
    # Never-built is therefore what is LEFT: no dossier, not withheld at the
    # route, and not one of the door's refusals. One refusal is one file here
    # because A_fact asks once per file, which is what makes the subtraction
    # sound; a negative would mean that stopped being true, so it is reported
    # rather than clamped away.
    try:
        without = _rows(connection, """
            select count(*) as n from files f
             where f.scan_state = 'included'
               and not exists (select 1 from llm_dossier d
                                where d.subject_ref = f.file_id)
               and not exists (select 1 from unresolved u
                                where u.file_id = f.file_id
                                  and u.reason = 'privacy_withheld')
        """)[0]["n"]
    except sqlite3.Error:
        without = 0
    never = without - sum(gate.values())
    return (at_route, dict(sorted(gate.items(), key=lambda kv: (-kv[1], kv[0]))),
            never)


def _subject_file_id(subject_ref: str) -> str | None:
    """The file id inside `file:{file_id}:{content_hash}`, or `None`.

    `placement.store.subject_ref_of`, read back. The kind comes off the front by
    the FIRST colon -- the kinds are a closed vocabulary with no colon in them --
    and the hash off the back by the LAST, which is safe because a sha256 hex
    digest contains none and P11 promises nothing about a file id's shape.
    `shadow._file_id_of` is the same reading; this is deliberately the narrower
    one, because a subject that is not a file is not a file of this corpus and has
    nothing on the scorecard to be counted against.
    """
    kind, separator, rest = subject_ref.partition(":")
    if not separator or kind != "file":
        return None
    identifier, hash_separator, _hash = rest.rpartition(":")
    if not hash_separator:
        return rest or None
    return identifier or rest or None


def _invalid_model_outputs(connection) -> set[str]:
    """File ids whose recorded site-C answer failed schema or validation.

    ONE ANSWER PER FILE, the last one. A site can be asked twice about one subject
    -- a retry, or a second call after a code change -- and the last recorded
    verdict is the run's answer, which is `store.last_response_bytes`'s own "most
    recent for this dossier" rule and the rule `shadow._observed` follows. Ordered
    by rowid because a reader of an old database has no other ordering.

    A file whose last answer was ACCEPTED, or who was never asked, is not here: the
    set holds only the failures, so a run with no model tables at all contributes
    nothing and reports nothing, which is the truth about it.
    """
    try:
        verdicts = {
            row["dossier_id"]: row["outcome"]
            for row in _rows(connection,
                             "select dossier_id, outcome from llm_verdict "
                             "where superseded_by is null order by rowid")}
        dossiers = _rows(connection,
                         "select dossier_id, subject_ref from llm_dossier "
                         "where call_site = ? order by rowid", C_PLACEMENT)
    except sqlite3.Error:
        # No `llm_*` tables: an offline run, or a database written before P8's
        # schema existed. "No model answered" is a measurement and not a failure,
        # so it comes back empty rather than raising.
        return set()

    failed: dict[str, bool] = {}
    for dossier in dossiers:
        file_id = _subject_file_id(dossier["subject_ref"])
        if file_id is None:
            continue          # a group, or a subject this corpus has no file for
        outcome = verdicts.get(dossier["dossier_id"])
        if outcome is None:
            # A refusal, a pre-call abstention or a failed call. None of those is a
            # model RESPONSE that failed, so none of them is counted here -- the
            # BLOCKED lines are where a file stopped before an answer is counted.
            continue
        failed[file_id] = outcome in FAILED_VALIDATION
    return {file_id for file_id, bad in failed.items() if bad}


def _cloud_target_of(stored: str) -> str | None:
    """The `provider/model_id` of a release that left the device, or `None`.

    `stored` is `binding._target_form`'s output: `canonical_json` over
    `ModelTarget.to_mapping()`, which is `{locality, model_id, provider}` and, for a
    local target with a window of ours to state, `context_tokens` beside them.

    THE `locality` KEY IS THE WHOLE READING. It is the run's own record of where the
    bytes went, written by the gate at the moment it authorised them, and it is why
    this module never needs to know what the local model is called.

    A row this cannot parse comes back as `UNREADABLE_TARGET` rather than as `None`:
    see that constant for why the unknown destination is counted and not dropped.
    """
    try:
        loaded = json.loads(stored)
    except (TypeError, ValueError):
        return UNREADABLE_TARGET
    if not isinstance(loaded, dict):
        return UNREADABLE_TARGET
    locality = loaded.get("locality")
    if not isinstance(locality, str):
        return UNREADABLE_TARGET
    if locality != CLOUD_LOCALITY:
        return None
    provider, model = loaded.get("provider"), loaded.get("model_id")
    named = "/".join(part for part in (provider, model) if isinstance(part, str) and part)
    return named or UNREADABLE_TARGET


def _cloud_releases(connection) -> dict[str, tuple[str, ...]]:
    """File id -> every cloud target this run released that file's dossier to.

    Three joins, each of them a table the product wrote:

      1. `release_ledger` says WHERE. One row per release the gate minted, carrying
         the whole `ModelTarget`; the cloud ones are kept and the local ones are
         dropped here, so nothing downstream has to know a locality vocabulary.
      2. `llm_dossier.subject_ref` says WHICH FILE, read back through
         `_subject_file_id` -- the same narrow reading the rest of this module uses,
         so a subject that is not a file of this corpus is not counted against one.
      3. `RELEASE_BEARING_TABLES` say WHICH RELEASE PAID FOR WHICH DOSSIER. A
         release is single-use and bound to one call, so the pair is the join.

    A RELEASE THIS RUN'S LEDGER DOES NOT HOLD IS NOT THIS RUN'S RELEASE, and that is
    a correctness requirement and not a leniency. `tools.groundtruth.reuse` copies
    `llm_dossier` and `llm_response` forward under `--reuse-answers-from` and
    deliberately does NOT copy the ledger -- "a single-use capability that paid for a
    call in another run has not paid for anything in this one" -- so on every seeded
    database the `release_id` columns dangle ON PURPOSE. Counting a dangling id as a
    destination would report a cloud breach for every answer a prior run bought,
    including answers it bought locally, and the number would grow with reuse rather
    than with releases. What a prior run sent was measured when that run was scored.

    A database with no ledger table at all yields nothing, and that is the honest
    reading rather than a flattering one: `release_ledger` is created by
    `privacy.schema.create_privacy_schema` and `llm_response.release_id` is NOT NULL
    because the gate mints it, so a database that has responses and no ledger was
    written by something with no door in it -- not by this product declining to use
    one. An unreadable ROW, which is the case this instrument could actually meet, is
    counted under `UNREADABLE_TARGET` instead.
    """
    try:
        targets = {row["release_id"]: named
                   for row in _rows(connection, "select release_id, model_target "
                                                "from release_ledger")
                   if (named := _cloud_target_of(row["model_target"])) is not None}
    except sqlite3.Error:
        return {}
    if not targets:
        return {}

    try:
        subjects = {}
        for row in _rows(connection, "select dossier_id, subject_ref from llm_dossier"):
            file_id = _subject_file_id(row["subject_ref"])
            if file_id is not None:
                subjects[row["dossier_id"]] = file_id
    except sqlite3.Error:
        return {}

    reached: dict[str, set[str]] = {}
    for table in RELEASE_BEARING_TABLES:
        try:
            rows = _rows(connection, f'select dossier_id, release_id from "{table}"')
        except sqlite3.Error:
            continue          # an older database without this table
        for row in rows:
            named = targets.get(row["release_id"])
            file_id = subjects.get(row["dossier_id"])
            if named is not None and file_id is not None:
                reached.setdefault(file_id, set()).add(named)
    return {file_id: tuple(sorted(named)) for file_id, named in reached.items()}


def _placeable_chains(connection, nodes) -> tuple[tuple[str, ...], ...]:
    """Every folder chain a file could legally have been filed into, root first.

    `where accepts_placement` is an exact filter and not a truthiness guess:
    `tree_design.schema` declares the column `INTEGER NOT NULL CHECK
    (accepts_placement IN (0, 1))`, so there is no NULL for it to drop silently. A
    node that vanishes from this list refused placement and did not merely fail to
    say so.

    A database whose `tree_nodes` has no such column at all -- an older build -- is
    read as though every node accepted one. That is the HARSHER direction on
    purpose: it makes more abstentions "unnecessary" rather than excusing them with
    a column this run cannot see, and a number that flatters the product on the
    strength of a missing column is the one failure this package exists to refuse.
    """
    try:
        placeable = {row["node_id"] for row in _rows(
            connection, "select node_id from tree_nodes where accepts_placement")}
    except sqlite3.Error:
        placeable = set(nodes)
    return tuple(sorted(_destination_of(node_id, nodes)
                        for node_id in nodes if node_id in placeable))


def _model_tally(connection) -> dict[str, int]:
    tally = {}
    for table in MODEL_TABLES:
        try:
            tally[table] = _rows(connection, f'select count(*) as n from "{table}"')[0]["n"]
        except sqlite3.Error:
            tally[table] = 0          # an older database without the table
    return tally


def _group_memberships(connection) -> dict[str, tuple[str, ...]]:
    """file_id -> the groups the RUN put it in. `104` §18.100.

    ONE QUERY FOR THE WHOLE RUN, not one per file: the scorecard walks every file
    and a per-file query would be N round trips for a mapping that does not
    change.

    `memberships` AND NOT `group_edges`. The edge table is the similarity GRAPH --
    `from_file_id`, `to_file_id`, `edge_type` -- and carries no `group_id` at all;
    joining to it is what made the lead's first reading of this return nothing.

    `decision` IS FILTERED, NOT ASSUMED. An excluded or uncertain member is not a
    member: counting a file the model excluded would score the product on a
    judgement it made in the other direction.

    Read defensively, like every other reader here: a database written before
    these tables existed has none, and that is a run which formed no groups rather
    than one that cannot be read.
    """
    try:
        rows = _rows(connection,
                     "select file_id, group_id from memberships "
                     "where superseded_by is null and decision = 'included'")
    except sqlite3.OperationalError:
        return {}
    found: dict[str, list[str]] = {}
    for row in rows:
        found.setdefault(row["file_id"], []).append(row["group_id"])
    return {file_id: tuple(sorted(groups)) for file_id, groups in found.items()}


def _rows(connection, sql, *args):
    connection.row_factory = sqlite3.Row
    return list(connection.execute(sql, args))


def _destination_of(node_id, nodes) -> tuple[str, ...]:
    chain, seen = [], set()
    while node_id and node_id in nodes and node_id not in seen:
        seen.add(node_id)
        label, parent = nodes[node_id]
        chain.append(label)
        node_id = parent
    return tuple(reversed(chain))


def observe_run(database: str | Path, corpus_root: str | Path, *,
                situation: str, label: str, promised_levels=(), report: str = "",
                seeded: Mapping[str, int] | None = None,
                seeded_from: str = "") -> RunObservation:
    """Read one plan database into observations, one per corpus-relative path."""
    root = str(Path(corpus_root).resolve())
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return _observe(connection, root, situation, label,
                        tuple(promised_levels), report, dict(seeded or {}),
                        seeded_from)
    finally:
        connection.close()


def _relative(path: str, root: str) -> str | None:
    if path == root:
        return None
    prefix = root.rstrip("/") + "/"
    return path[len(prefix):] if path.startswith(prefix) else None


def _observe(connection, root, situation, label, promised_levels, report,
             seeded=None, seeded_from=""):
    nodes = {r["node_id"]: (r["display_label"], r["parent_node_id"])
             for r in _rows(connection, "select node_id, display_label, "
                                        "parent_node_id from tree_nodes")}

    excluded: dict[str, str] = {}
    for row in _rows(connection, "select path, rule from exclusion_verdicts"):
        relative = _relative(row["path"], root)
        if relative is not None:
            excluded[relative] = row["rule"]

    files, by_id = {}, {}
    for row in _rows(connection, "select file_id, current_path from files"):
        relative = _relative(row["current_path"], root)
        if relative is not None:
            by_id[row["file_id"]] = relative

    runs: dict[str, list[sqlite3.Row]] = {}
    for row in _rows(connection, "select file_id, extractor_name, completeness, "
                                 "run_id from extraction_runs"):
        runs.setdefault(row["file_id"], []).append(row)

    units: dict[str, int] = {}
    for row in _rows(connection,
                     "select e.file_id as file_id, count(*) as n from text_units t "
                     "join extraction_runs e on t.run_id = e.run_id group by e.file_id"):
        units[row["file_id"]] = row["n"]

    observations: dict[str, int] = {}
    prose: dict[str, int] = {}
    for row in _rows(connection, "select file_id, extractor_name, count(*) as n "
                                 "from evidence where superseded_by is null "
                                 "group by file_id, extractor_name"):
        if row["extractor_name"] == FILESYSTEM_ONLY:
            continue
        observations[row["file_id"]] = observations.get(row["file_id"], 0) + row["n"]
        if row["extractor_name"] in TEXT_PRODUCING:
            prose[row["file_id"]] = prose.get(row["file_id"], 0) + row["n"]

    protected, handling = {}, {}
    for row in _rows(connection, "select file_id, protected, handling_class from "
                                 "classifications where superseded_by is null"):
        protected[row["file_id"]] = bool(row["protected"])
        handling[row["file_id"]] = row["handling_class"]

    facts: dict[str, dict[str, str]] = {}
    origins: dict[str, dict[str, str]] = {}
    for row in _rows(connection,
                     'select f.file_id as file_id, f.field_key as field_key, '
                     'f.origin as origin, v.canonical_value as value from file_facts f '
                     'join "values" v on f.value_id = v.value_id where f.active = 1'):
        facts.setdefault(row["file_id"], {})[row["field_key"]] = row["value"]
        origins.setdefault(row["file_id"], {})[row["field_key"]] = row["origin"]

    unresolved: dict[str, set[str]] = {}
    for row in _rows(connection, "select file_id, field_key from unresolved "
                                 "where superseded_by is null"):
        unresolved.setdefault(row["file_id"], set()).add(row["field_key"])

    routing: dict[str, str] = {}
    for row in _rows(connection, "select file_id, unrouted_completeness from "
                                 "extraction_routing where unrouted_completeness "
                                 "is not null"):
        routing[row["file_id"]] = row["unrouted_completeness"]

    invalid_outputs = _invalid_model_outputs(connection)
    cloud_releases = _cloud_releases(connection)
    memberships = _group_memberships(connection)

    decisions: dict[str, sqlite3.Row] = {}
    for row in _rows(connection, "select subject_ref, outcome, node_id, payload from "
                                 "placement_decisions where superseded_by is null"):
        parts = row["subject_ref"].split(":")
        if len(parts) >= 2 and parts[0] == "file":
            decisions[parts[1]] = row

    for file_id, relative in by_id.items():
        my_runs = runs.get(file_id, [])
        content = [r for r in my_runs if r["extractor_name"] != FILESYSTEM_ONLY]
        extractors = tuple(sorted({r["extractor_name"] for r in my_runs}))
        n_units = units.get(file_id, 0)

        if content:
            word = min((r["completeness"] for r in content), key=lambda w: _RANK.get(w, 99))
        else:
            word = routing.get(file_id, "unreadable" if not my_runs else "unsupported")

        recovered = any(
            r["extractor_name"] in TEXT_PRODUCING
            and r["completeness"] in ("complete", "capped", "partial")
            for r in content) and n_units > 0

        decision = decisions.get(file_id)
        outcome = decision["outcome"] if decision else None
        destination = _destination_of(decision["node_id"], nodes) if decision else ()
        asked = False
        review_policy = None
        decided_by = None
        if decision:
            try:
                body = json.loads(decision["payload"])
            except (ValueError, TypeError):
                body = {}
            asked = body.get("ask") is not None
            policy = body.get("review_policy")
            review_policy = policy if isinstance(policy, str) else None
            decider = body.get("decided_by")
            decided_by = decider if isinstance(decider, str) else None

        files[relative] = Observation(
            path=relative,
            indexed=True,
            excluded_by=excluded.get(relative),
            opened=bool(content) or n_units > 0,
            text_units=n_units,
            evidence_rows=observations.get(file_id, 0),
            prose_evidence_rows=prose.get(file_id, 0),
            extractors=extractors,
            completeness=word,
            content_recovered=recovered,
            protected_marked=protected.get(file_id, False),
            handling_class=handling.get(file_id),
            fields=facts.get(file_id, {}),
            field_origins=origins.get(file_id, {}),
            unresolved_fields=tuple(sorted(unresolved.get(file_id, ()))),
            outcome=outcome,
            destination=destination,
            asked=asked,
            invalid_model_output=file_id in invalid_outputs,
            review_policy=review_policy,
            decided_by=decided_by,
            cloud_releases=cloud_releases.get(file_id, ()),
            group_ids=memberships.get(file_id, ()),
        )

    # A file the scan set aside never becomes a `files` row, and "never silently
    # omitted" means it still has to appear in the scorecard. The corpus on disk
    # is what decides which files exist, not the `files` table -- otherwise a
    # file the product dropped would be invisible to the instrument that exists
    # to notice it.
    #
    # An exclusion verdict may name a DIRECTORY: §1.1's software-project rule
    # sets aside `matcher/match`, not the eleven modules under it. So a verdict
    # is matched against a path and against every path beneath it.
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file():
            continue
        relative = _relative(str(path), root)
        if relative is None or relative in files:
            continue
        rule = excluded.get(relative)
        if rule is None:
            parts = relative.split("/")
            for cut in range(len(parts) - 1, 0, -1):
                rule = excluded.get("/".join(parts[:cut]))
                if rule is not None:
                    break
        files[relative] = Observation(
            path=relative, indexed=False, excluded_by=rule, opened=False,
            text_units=0, evidence_rows=0, prose_evidence_rows=0,
            extractors=(), completeness="unreadable",
            content_recovered=False, protected_marked=False, handling_class=None,
            fields={}, field_origins={}, unresolved_fields=(), outcome=None,
            destination=(), asked=False, invalid_model_output=False)

    depth = 0
    for node_id in nodes:
        depth = max(depth, len(_destination_of(node_id, nodes)))

    _blocked = _blocked_tally(connection)
    return RunObservation(
        situation=situation,
        label=label,
        promised_levels=promised_levels,
        files=files,
        structural_questions=_rows(connection, "select count(*) as n from "
                                               "structural_questions")[0]["n"],
        model=_model_tally(connection),
        seeded=dict(seeded or {}),
        seeded_from=seeded_from,
        blocked_at_route=_blocked[0],
        gate_refusals=_blocked[1],
        never_built=_blocked[2],
        node_count=len(nodes),
        built_depth=max(0, depth - 1),   # below the top-level folder
        node_paths=_placeable_chains(connection, nodes),
        report=report,
    )
