# src/facts/learning.py
"""§8.7 correction learning -- the query-before-propose guard (I4).

TWO HALVES, AND BOTH OF THEM FIRE. For most of this module's life only the read half
could, because nothing called it and nothing could write to it; that is what the
paragraphs below are written against, and it is worth keeping the reason visible.

READ (binding now).  §8.7's failure mode is literal: without stored negative feedback
the system "will repeatedly resurface the same attractive but incorrect grouping."
I4 states P6's obligation as: before writing a `file_facts` row that would revive a
`rejected` claim, query the learning store; on an unreset reject, leave the `rejected`
row in place and do not propose the same (field, value) again.  `is_suppressed` is
that query.  It ships with the fact tables because a guard that arrives after the
first fact is written has already failed once.

ITS CALL SITE IS `facts.direct.direct_facts`, and it is the last thing asked before
the row exists.  For a long time this docstring said the call site was Task 20's
resolver; that sentence was not in the PLAN and was not true, and while it stood, I4's
obligation -- query BEFORE writing a row that would revive a `rejected` claim -- was
enforced by nothing, which is precisely the "already failed once" case named above.

WHY THE PRODUCER AND NOT THE RESOLVER.  The guard is keyed on `(file_id, field,
value_id)`, and a value id exists only after a producer has picked a field and
canonicalised a reading.  `FactResolver` sequences stages and never sees either, so a
guard bound there could only be handed the question after the answer.  Task 20's
`test_the_resolver_imports_no_producer_module` also pins the resolver's imports, which
is what made the injected-callable route look necessary; the producer needs no such
route, because `facts` may import `facts` and the check belongs beside `write_fact`.

`facts.direct` is the ONE production stage this deployment runs -- `src/cli.py`'s
`_resolver` binds `rule` and `llm` to `None` -- so the guard is on the live path today
rather than on a path that exists in a test.  `facts.rules.apply_rules` is the other
producer that writes a claim, and when a deployment binds it the same three lines are
owed there; it has no caller in `src/` at all today, so there is nothing yet to guard.

WRITE (reachable from the command, still owed a surface).  `record_correction` is what
P13 will route a fact-level gesture into and it still takes P13's shape: a value id, a
tuple of observation keys, an action name P6 does not coin.  A PERSON has none of
those, so `reject_claim` sits above it and takes the three words they do have -- the
file, the field, and the value the product printed on their screen.  That is what
`src/cli.py --reject` calls, which is what makes §8.7 something a person can reach
today rather than on the day P13 lands.

A rejection does BOTH halves.  It supersedes the standing `file_facts` row into
§3.13's `rejected` state -- which is what a person sees, on the very next run -- and it
stores the §8.7 record that stops the claim being proposed again.  Doing only the
second is invisible: measured on a real corpus, a rejection with no retraction left
the folder standing and the plan came back byte-identical.

Still owed to P13's wave, and named rather than quietly absent: the review surface
itself, the inspect/reset UI, the routing decision, and the call to
`database_agent.learning.reset_preferences` -- so a person can reject a fact today but
cannot yet undo it without a script.

P6 MINTS NO §8.2 EVENT TYPE HERE.  A user correction is keyed by `proposal_class` and
`basis_key` -- two ordinary columns beside §8.2's eleven -- never by a type of its own.
The two types used are P6's authored pair from `facts.authorship`, both already among
§8.2's reserved nineteen, so nothing is registered.

P1 STORES, P6 INTERPRETS.  P1's own docstring is explicit that it "derives no polarity,
compares no basis_key, interprets no proposal_class".  Suppressing a proposal is the
acting part's rule, applied here.

WHAT THIS MODULE DELIBERATELY DOES NOT DECIDE.  I4 says an `accept` is not itself a
suppression; it does not say a later `accept` *lifts* an earlier `reject`.  Only a
reset does, in I4's text.  The literal rule is implemented -- any unreset reject at
that scope, subject, class and basis suppresses -- and no newest-wins override is
invented.  An accept lifting a reject without a reset would be a decision for Joseph.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Iterable

from database_agent.db import transaction
from database_agent.events import append_event
from database_agent.learning import learning_records
from evidence_shape.canonical import canonical_json
from facts.authorship import AUTHORED_EVENT_TYPES, event_defaults
from facts.file_facts import USER_CORRECTION, facts_for_file, write_fact
from facts.states import REJECTED
from facts.supersede import supersede_fact

#: I4's equivalence table. P6 owns proposal class `fact`; its basis is the claim.
#: `group`, `membership`, `branch`, `placement`, `residual` and `privacy` belong to
#: P9, P10, P11 and P7, and a record at one of those classes is not P6's to read.
PROPOSAL_CLASS: str = "fact"

#: THE ONLY SCOPE A FACT SUPPRESSION CAN MATCH AT, and that is forced rather than
#: chosen. I4's basis for `proposal_class = fact` is `(file_id, field, value_id)` --
#: the file id is IN the key -- so a record stored at any of §8.7's other five scopes
#: carries a subject this basis can never be found under. A producer that queried all
#: six would make five lookups that cannot hit and would read as a breadth it does not
#: have. §8.7's own words for why the scope is narrow: one particular transcript
#: belonging in a Columbia packet "must not teach the engine that all transcripts
#: belong there".
#:
#: Spelled here rather than imported, exactly as `privacy.learning_seam.FILE_SCOPE` is,
#: and DELIBERATELY without a membership assert: importing `CORRECTION_SCOPES` to check
#: it would put a copy of all six into this module's namespace, which is precisely what
#: `test_a_seventh_scope_is_refused_by_p1_and_p6_does_not_respell_the_six` forbids. The
#: check is not lost -- `learning_records` runs `_check(scope)` on every query, so a
#: wrong spelling here raises on the first call rather than reading nothing and
#: reporting that the user had rejected nothing.
FILE_SCOPE: str = "file"

#: I4: "polarity in accept | reject ... supplied by the acting part, never inferred".
#: Every rule below turns on finding an *unreset reject*; a reader that could not
#: separate rejections from approvals would have to parse explanation free text.
POLARITIES: tuple[str, str] = ("accept", "reject")
ACCEPT, REJECT = POLARITIES

#: P6's two §8.2 names, taken from Task 1's tuple rather than respelled here. Both are
#: reserved names, spelled with a space; `fact_creation` would raise at the writer.
CREATION, REJECTION = AUTHORED_EVENT_TYPES


class MalformedCorrection(Exception):
    """Refused at the writer. `events` is append-only, so a bad row cannot be repaired."""


class NoSuchClaim(LookupError):
    """The words a person typed name no claim this version of this file carries."""


def basis_key(*, file_id: str, field_key: str, value_id: str) -> str:
    """I4's `(file_id, field, value_id)`, serialized once -- here, and nowhere else.

    Canonical JSON rather than a delimiter join (not injective: a `|` inside a part
    would collide two claims and suppress a proposal the user never rejected) and
    rather than a digest (§8.7 requires the user "be able to inspect or reset learned
    preferences", and an opaque basis is not inspectable).  `canonical_json` sorts
    keys, so the argument order at the call site cannot change the stored key.

    This is NOT a §3.4 cache key and is not one of `facts.cache`'s three: it is I4's
    proposal identity, a different rule over a different triple.

    Member set, dossier hash and display label are NOT in the basis (I4).
    """
    return canonical_json(
        {"field_key": field_key, "file_id": file_id, "value_id": value_id}
    )


def is_suppressed(conn: sqlite3.Connection, *, scope: str, subject_id: str,
                  file_id: str, field_key: str, value_id: str) -> bool:
    """True when an unreset rejection of exactly this claim stands at this scope.

    I4's query-before-propose, applied in order: ignore records at the wrong
    `proposal_class`; ignore records whose `basis_key` does not match; honour a later
    reset; and on a `polarity = reject` record that no later reset covers, do not
    emit.  An `accept` at the same basis is not a suppression and is not read as one.

    The reset is honoured by `learning_records` itself -- it applies the cutoff and
    returns nothing below it.  This function does not re-derive it: a second place
    the cutoff rule lives is a second place it can drift.

    Read-only.  It appends no event, writes no fact, and mutates nothing.
    """
    key = basis_key(file_id=file_id, field_key=field_key, value_id=value_id)
    for row in learning_records(conn, scope, subject_id):
        if row["proposal_class"] != PROPOSAL_CLASS:
            continue
        if row["basis_key"] != key:
            continue
        if row["polarity"] == REJECT:
            return True
    return False


def record_correction(conn: sqlite3.Connection, *, action: str, scope: str, subject: str,
                      polarity: str, file_id: str, field_key: str, value_id: str,
                      evidence_refs: Iterable[str], user_id: str,
                      observed_at: str) -> int:
    """Author the fact-level consequence of one user correction; P1 writes it (M8).

    P13's stand-in until P13 exists.  `action` is P13's gesture name: P6 stores the
    string in the explanation and branches on `polarity`, never on `action` -- the
    action vocabulary is P13's and P6 does not coin a name another part owns.

    `subject` is not derived from `file_id`.  Five of §8.7's six scopes have no file,
    so the correction's subject is always the caller's to supply.

    `scope` is validated by P1's writer against `CORRECTION_SCOPES`, which is the one
    place the six are spelled.  P6 keeps no copy.
    """
    if polarity not in POLARITIES:
        raise MalformedCorrection(
            f"polarity {polarity!r} is not one of {POLARITIES}; I4 requires it be "
            "supplied by the acting part and never inferred"
        )
    if not action:
        raise MalformedCorrection("action is required; it is P13's gesture name")
    if not user_id:
        raise MalformedCorrection(
            "user_id is required: learning_records filters `user_id IS NOT NULL`, so a "
            "correction stored without one is storable and permanently unreadable"
        )
    refs = tuple(evidence_refs)
    if polarity == REJECT and not refs:
        raise MalformedCorrection(
            "§8.7 requires a rejection be stored with the evidence that produced it"
        )
    key = basis_key(file_id=file_id, field_key=field_key, value_id=value_id)
    explanation = canonical_json({
        "action": action,
        "basis_key": key,
        "evidence_refs": list(refs),
        "polarity": polarity,
        "proposal_class": PROPOSAL_CLASS,
    })
    payload = event_defaults(
        event_type=REJECTION if polarity == REJECT else CREATION,
        observed_at=observed_at,
        explanation=explanation,
        file_id=file_id,
        user_id=user_id,
        correction_scope=scope,
        correction_subject=subject,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS,
        basis_key=key,
    )
    return append_event(conn, **payload)


def reject_claim(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                 field_key: str, value: str, action: str, user_id: str,
                 observed_at: str) -> int:
    """One correction, stated in the words a person actually has. Returns the event id.

    `record_correction` above takes a `value_id` and a tuple of observation keys. A
    person has neither: they have a filename, the field the product named on their
    screen, and the word it printed beside it. Something has to turn the second into
    the first, and where that something lives is the whole decision here.

    IT LIVES IN P6 BECAUSE THE SCHEMA DOES. The only other place it could go is
    whatever module collects the gesture, which for this deployment is `src/cli.py` --
    the composition root, the file whose own docstring says it decides deployment
    numbers and nothing else. A `SELECT` over `file_facts` and `values` written there
    would be a second home for P6's tables in the one file that should hold none, and
    a second home for one rule is this project's named defect. So the lookup is here,
    once, and the caller passes words.

    `action` is REQUIRED and has no default. §8.7's gesture vocabulary is P13's --
    `review_surface.vocabulary.ACTIONS` -- and `facts` may not import P13 (its import
    allowlist is `facts`, `database_agent`, `evidence_shape`, `eval_harness`,
    `extractors`). A default here would be P6 coining a name it does not own, which
    `record_correction` already refuses to do one level down.

    THE EVIDENCE IS TAKEN FROM THE FACT, NOT FROM THE CALLER. §8.7 requires a
    rejection be stored with the evidence that produced it, and a caller inventing a
    citation would store a rejection pointing at something that never produced the
    claim. The refs come off the row being rejected, which is exactly what the
    product showed the person before they said no.

    A CLAIM THAT DOES NOT EXIST IS REFUSED, never ignored. `src/cli.py`'s
    `apply_answers` states the rule for this command's other gesture: a silently
    dropped answer "is the worst of both -- no effect, and no way to tell". A
    rejection is the same shape. Nothing is written on the refused path.

    TWO OBLIGATIONS, NOT ONE, AND THEY ARE BOTH DONE HERE.

    §8.7's guard -- "so the same attractive-but-incorrect conclusion is not
    resurfaced" -- is about the NEXT proposal, and `is_suppressed` is what enforces
    it. The SPEC's other sentence is about THIS one: a correction produces "a
    `rejected` fact retained with the evidence that produced it".

    Doing only the first is invisible, and it was measured rather than reasoned. On a
    real three-file corpus, a person rejected `subject = INV20261` on an invoice, ran
    the command again, and got a byte-identical plan: the row written before they
    objected was still `direct`, still active, still what P10 built a folder out of.
    A correction that changes nothing the person can see is a correction the product
    did not make.

    So the standing row is superseded by a `rejected` one carrying the SAME evidence.
    `read_surface.proposal_eligible` drops it on both counts -- `rejected` is not a
    proposal-eligible state, and the old row now has a `superseded_by` -- so no folder
    can rest on it any more, while `fact_history` still returns both rows and §8.2's
    "retaining the old observation AND the reason it was superseded" holds.

    ONE TRANSACTION. Half of this gesture is worse than none: a retraction with no
    learning record forgets the correction on the next run, and a learning record with
    no retraction leaves the folder standing.

    The new row keeps the old row's `cache_key`. §3.4's key identifies a COMPUTATION
    and a person's correction is not one, so minting a key here would claim a pass
    that never ran, and would put this row outside the invalidation the claim it
    retracts is subject to.
    """
    named = [row for row in facts_for_file(conn, file_id, content_hash)
             if row["field_key"] == field_key and row["canonical_value"] == value]
    if not named:
        raise NoSuchClaim(
            f"this version of {file_id!r} carries no {field_key} of {value!r}. A "
            "rejection names something the product actually proposed; refusing is "
            "the only answer that does not leave you believing you were heard.")

    # SAYING IT TWICE IS NOT AN ERROR, and this is the whole of why the loop is
    # written over a filtered list. A person does not re-run this command by editing
    # one flag off the end of it; they press up-arrow and press return, `--reject`
    # and all. Found by doing exactly that against the real command, which raised
    # P1's `mark_superseded` refusal -- "already superseded by ...; the first
    # supersede_reason is never overwritten". P1 is right; a gesture a person will
    # repeat has to be repeatable.
    standing = [row for row in named
                if row["superseded_by"] is None
                and row["reliability_state"] != REJECTED]
    if not standing:
        for record in learning_records(conn, FILE_SCOPE, file_id):
            if record["proposal_class"] != PROPOSAL_CLASS:
                continue
            if record["basis_key"] != basis_key(file_id=file_id,
                                                field_key=field_key,
                                                value_id=named[0]["value_id"]):
                continue
            if record["polarity"] == REJECT:
                # The same correction, not a second one. §8.5 counts decisions, and
                # an up-arrow must not read as two of them.
                return record["event_id"]
        raise NoSuchClaim(
            f"the {field_key} of {value!r} on {file_id!r} was already replaced by "
            "something else, so there is no standing claim to reject. Nothing was "
            "written; §8.2 keeps the old row readable and this refusal leaves it "
            "exactly as it is.")

    # EVERY standing row that names this claim, not just the first. One version can
    # carry the same (field, value) from two producers -- a `direct` slot and a
    # `validated` rule both reaching `subject = PHYS1401` -- and retracting one would
    # leave the other proposable, so the person's rejection would half work. This
    # deployment binds one producer and cannot make that case today; the loop is
    # written for the day a deployment binds two, because a half-honoured correction
    # is the failure that is hardest to see.
    with transaction(conn):
        for row in standing:
            refs = json.loads(row["evidence_refs"])
            retraction = write_fact(
                conn, file_id=file_id, content_hash=content_hash,
                field_key=field_key, value_id=row["value_id"],
                reliability_state=REJECTED, origin=USER_CORRECTION,
                evidence_refs=refs, cache_key=row["cache_key"], active=True,
                # SPEC's `file_facts` shape: "`rejection_reason` -- for `rejected`:
                # who rejected it and on what evidence". The evidence is the row's
                # own `evidence_refs`, carried across unchanged; this is the who,
                # and the gesture they made.
                rejection_reason=canonical_json(
                    {"action": action, "rejected_by": user_id}))
            supersede_fact(
                conn, old_fact_id=row["fact_id"], new_fact_id=retraction,
                reason=f"{user_id} rejected this claim ({action})")
        # ONE correction for one gesture, however many rows it retracted. §8.7 stores
        # what the person decided, and they decided once.
        return record_correction(
            conn, action=action, scope=FILE_SCOPE, subject=file_id,
            polarity=REJECT, file_id=file_id, field_key=field_key,
            value_id=standing[0]["value_id"],
            evidence_refs=json.loads(standing[0]["evidence_refs"]),
            user_id=user_id, observed_at=observed_at)
