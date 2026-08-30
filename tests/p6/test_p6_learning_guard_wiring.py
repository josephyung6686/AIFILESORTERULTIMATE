# tests/p6/test_p6_learning_guard_wiring.py
"""I4's query-before-propose guard, AT ITS CALL SITE.

`tests/p6/test_p6_learning.py` drives `is_suppressed` directly and proves the rule.
It also proved, in `test_the_guard_stops_the_write_a_resolver_would_have_made`, that
a four-line loop SHAPED like a producer would honour it -- a loop the test wrote
itself, over claims the test made up, with no producer anywhere near it.

That is the shape of this codebase's dominant defect: the rule is tested, the
composition is not, and `is_suppressed` had no caller in `src/` at all. §8.7's failure
mode is not "the rule is wrong". It is that the product "will repeatedly resurface the
same attractive but incorrect grouping" -- which is what a guard with no call site
guarantees, however well it is tested.

So every test here goes through `facts.direct.direct_facts`, the ONE fact producer
this deployment runs (`src/cli.py:_resolver` binds `rule` and `llm` to `None`). The
subject is the guard's REACHABILITY, not its rule.

**Scope is `file` and only `file`, and that is forced rather than chosen.** I4's basis
for `proposal_class = fact` is `(file_id, field, value_id)` -- the file id is IN the
key -- so a record at any of §8.7's other five scopes carries a basis this producer can
never match. Querying them would be five lookups that cannot hit.

**A suppressed claim writes no `unresolved` row, and that is a decision.**
`UNRESOLVED_REASONS` has no member for it; minting one is a closed-vocabulary change
that needs the owner. It is also the right answer on the merits: an `unresolved` row
says the system tried and could not settle a field. Here the field IS settled -- the
user settled it -- and reporting their own decision back to them as an unresolved
refusal would be the product failing to remember, in the one place §8.7 exists to
make it remember.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from database_agent.learning import reset_preferences

from evidence_shape.location import Location, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.direct import DirectSlot, DirectSlots, direct_facts
from facts.discount import MetadataScreen
from facts.file_facts import facts_for_file
from facts.learning import FILE_SCOPE, record_correction
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

CLOCK = "2026-08-19T12:00:00+00:00"
NO_CATALOGUE = MetadataScreen()

#: The slot this deployment actually ships, in miniature: a span inside a body zone,
#: read into `subject`. `src/cli.py:DIRECT_SLOTS` is the real one and its predicate is
#: `reads_a_structured_string`; the shape that matters here is only that a reading
#: becomes a `subject` fact.
SUBJECT_SLOT = DirectSlot(
    slot_id="test.text.identifier", field_key="subject",
    names=lambda locator: locator.startswith("body#"),
    canonical=lambda raw: "".join(raw.split()))


def _file(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("body", (), TextSpan(0, len(raw))), occurrence_count=1,
        observed_at=CLOCK, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation


@pytest.fixture()
def one_file(p6_conn, tmp_path):
    """One file whose body says `PHYS1401` -- the claim the user will reject."""
    file_id, content_hash = _file(p6_conn, tmp_path, name="week3.pdf", body=b"%PDF-a")
    observation = _observe(p6_conn, run_id="run-1", file_id=file_id,
                           content_hash=content_hash, raw="PHYS1401")
    return file_id, content_hash, observation


def _run(conn, file_id, content_hash):
    return direct_facts(conn, file_id=file_id, content_hash=content_hash,
                        slots=DirectSlots(slots=(SUBJECT_SLOT,)),
                        screen=NO_CATALOGUE)


def _reject(conn, *, file_id, value_id, observation, field_key="subject"):
    return record_correction(
        conn, action="reject_fact", scope=FILE_SCOPE, subject=file_id,
        polarity="reject", file_id=file_id, field_key=field_key,
        value_id=value_id, evidence_refs=(observation.observation_key,),
        user_id="user-1", observed_at=CLOCK)


# --- the promise: a rejection is remembered on the next run ------------------------


def test_the_producer_does_not_rewrite_a_fact_the_user_rejected(p6_conn, one_file):
    """§8.7's whole point, through the producer a person's run actually calls.

    Run one proposes `subject = PHYS1401`. The person says no. Run two must not
    propose it again -- and before this guard was wired, it did, every time, because
    `direct_facts` never asked.
    """
    file_id, content_hash, observation = one_file

    first = _run(p6_conn, file_id, content_hash)
    assert len(first) == 1
    value_id = facts_for_file(p6_conn, file_id, content_hash)[0]["value_id"]

    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=observation)

    # The second run: the same file, the same bytes, the same slot.
    assert _run(p6_conn, file_id, content_hash) == ()


def test_the_rejection_survives_the_person_editing_the_file(p6_conn, tmp_path):
    """A NEW version of the same file must not resurrect the rejected claim.

    I4's basis is `(file_id, field, value_id)` and carries no content hash, and
    `placement.learning` states why in its own words: §8.7 "is about what the user
    decided, and editing a file does not un-decide it -- a versioned key would
    silently stop matching on the next save and resurface exactly the destination the
    user rejected."

    This is the test that a same-version re-run cannot make: `write_fact` is keyed on
    the version, so running twice over one content hash writes one row whether the
    guard fires or not. A second content hash is a genuinely new write.
    """
    path = tmp_path / "week3.pdf"
    path.write_bytes(b"%PDF-a")
    file_id, first_hash = _file(p6_conn, tmp_path, name="week3.pdf", body=b"%PDF-a")
    first = _observe(p6_conn, run_id="run-v1", file_id=file_id,
                     content_hash=first_hash, raw="PHYS1401")
    assert len(_run(p6_conn, file_id, first_hash)) == 1
    value_id = facts_for_file(p6_conn, file_id, first_hash)[0]["value_id"]
    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=first)

    # The person edits the file. Same file_id, new content hash, same reading.
    second_hash = "b" * 64
    _observe(p6_conn, run_id="run-v2", file_id=file_id, content_hash=second_hash,
             raw="PHYS1401")
    assert _run(p6_conn, file_id, second_hash) == ()
    assert facts_for_file(p6_conn, file_id, second_hash) == []


def test_the_suppression_needs_no_prior_pass(p6_conn, one_file):
    """The guard is asked BEFORE the first write, not only on a re-run.

    §8.7: a guard "that arrives after the first fact is written has already failed
    once". A rejection carried forward from an earlier version of the same file must
    stop the very first proposal this pass would make.
    """
    file_id, content_hash, observation = one_file
    # The value id is content-addressed, so it can be named before any fact exists.
    from facts.values import VALUE_ORIGINS, ensure_value
    value_id = ensure_value(p6_conn, field_key="subject", canonical_value="PHYS1401",
                            first_evidence_ref=observation.observation_key,
                            origin=VALUE_ORIGINS[0])
    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=observation)

    assert _run(p6_conn, file_id, content_hash) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []


# --- the guard is narrow: exactly the claim the user rejected ----------------------


def test_a_different_value_in_the_same_field_is_still_written(p6_conn, tmp_path,
                                                              one_file):
    """§8.7's governing sentence: rejecting one thing must not teach a rule.

    "one particular transcript belongs in a Columbia packet ... must not teach the
    engine that all transcripts belong there."
    """
    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    value_id = facts_for_file(p6_conn, file_id, content_hash)[0]["value_id"]
    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=observation)

    other_id, other_hash = _file(p6_conn, tmp_path, name="lab.pdf", body=b"%PDF-b")
    _observe(p6_conn, run_id="run-2", file_id=other_id, content_hash=other_hash,
             raw="CHEM2100")
    assert len(_run(p6_conn, other_id, other_hash)) == 1


def test_a_rejection_on_another_file_does_not_suppress_this_one(p6_conn, tmp_path,
                                                                one_file):
    # The same VALUE, a different FILE. I4's basis carries the file id, so `PHYS1401`
    # rejected on week3.pdf says nothing about week4.pdf.
    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    value_id = facts_for_file(p6_conn, file_id, content_hash)[0]["value_id"]
    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=observation)

    other_id, other_hash = _file(p6_conn, tmp_path, name="week4.pdf", body=b"%PDF-c")
    _observe(p6_conn, run_id="run-3", file_id=other_id, content_hash=other_hash,
             raw="PHYS1401")
    assert len(_run(p6_conn, other_id, other_hash)) == 1


def test_an_accept_is_not_a_suppression_at_the_producer(p6_conn, one_file):
    # I4 rule 4: only a reject suppresses. A person confirming a fact must not delete
    # it on the next run.
    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    value_id = facts_for_file(p6_conn, file_id, content_hash)[0]["value_id"]
    record_correction(
        p6_conn, action="accept_fact", scope=FILE_SCOPE, subject=file_id,
        polarity="accept", file_id=file_id, field_key="subject", value_id=value_id,
        evidence_refs=(observation.observation_key,), user_id="user-1",
        observed_at=CLOCK)

    assert len(_run(p6_conn, file_id, content_hash)) == 1


# --- resettable, which §8.7 requires by name --------------------------------------


def test_a_reset_lets_the_producer_propose_it_again(p6_conn, one_file):
    """§8.7: learned preferences must be "inspectable and resettable".

    Through the producer, so the reset is reachable from a run and not only from a
    unit test. Nothing is deleted (R6): the rejection is still on the events log.
    """
    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    value_id = facts_for_file(p6_conn, file_id, content_hash)[0]["value_id"]
    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=observation)
    assert _run(p6_conn, file_id, content_hash) == ()

    reset_preferences(p6_conn, FILE_SCOPE, file_id, author="P6",
                      component_version="0.1.0", user_id="user-1")
    assert len(_run(p6_conn, file_id, content_hash)) == 1
    assert p6_conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE polarity = 'reject'"
    ).fetchone()["n"] == 1


# --- what the guard must NOT do ---------------------------------------------------


def test_a_suppressed_claim_is_not_recorded_as_an_unresolved_refusal(p6_conn,
                                                                     one_file):
    """The user's own decision is not a refusal by the system.

    `UNRESOLVED_REASONS` carries no member for a suppression and this task mints
    none. Writing one of the existing thirteen would file the person's answer under
    a reason that is not what happened.
    """
    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    value_id = facts_for_file(p6_conn, file_id, content_hash)[0]["value_id"]
    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=observation)
    _run(p6_conn, file_id, content_hash)

    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_the_guard_mints_no_value_row_for_a_claim_it_refuses(p6_conn, one_file):
    # The value already exists -- a rejection cites the fact it rejected -- so the
    # guard must not leave a second, orphan `values` row behind on every later run.
    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    value_id = facts_for_file(p6_conn, file_id, content_hash)[0]["value_id"]
    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=observation)
    before = len(values_in_field(p6_conn, "subject"))
    _run(p6_conn, file_id, content_hash)
    assert len(values_in_field(p6_conn, "subject")) == before


def test_the_evidence_behind_the_rejection_survives(p6_conn, one_file):
    # §8.7: "Rejected facts persist with their evidence." Suppressing a proposal must
    # not remove the observation that produced it -- the person has to be able to see
    # why the product suggested it in the first place.
    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    value_id = facts_for_file(p6_conn, file_id, content_hash)[0]["value_id"]
    _reject(p6_conn, file_id=file_id, value_id=value_id, observation=observation)
    _run(p6_conn, file_id, content_hash)

    row = p6_conn.execute(
        "SELECT explanation FROM events WHERE polarity = 'reject'").fetchone()
    assert observation.observation_key in json.loads(row["explanation"])["evidence_refs"]


# --- the gesture side: turning a person's words into I4's basis --------------------
#
# `record_correction` takes a `value_id` and a list of evidence refs. A person has
# neither: they have a filename, a field and the word they saw on their screen. Every
# caller that closed that gap itself would be a second home for P6's schema in
# whatever module happens to be collecting the gesture -- which for this deployment is
# `src/cli.py`, the composition root, the one file that is supposed to hold no schema
# at all. So the gap is closed here, once.


def test_a_persons_words_reach_the_claim_they_are_about(p6_conn, one_file):
    from facts.learning import reject_claim

    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)

    reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="PHYS1401", action="reject",
                 user_id="user-1", observed_at=CLOCK)

    # And the producer honours it on the next run, which is the whole point.
    assert _run(p6_conn, file_id, content_hash) == ()


def test_the_rejection_carries_the_evidence_the_product_showed_the_person(p6_conn,
                                                                         one_file):
    """§8.7: rejected facts "persist with their evidence".

    The refs are taken from the fact being rejected rather than asked of the caller.
    A person cannot type an observation key, and a caller inventing one would store a
    rejection citing evidence that never produced the claim.
    """
    from facts.learning import reject_claim

    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="PHYS1401", action="reject",
                 user_id="user-1", observed_at=CLOCK)

    row = p6_conn.execute(
        "SELECT explanation FROM events WHERE polarity = 'reject'").fetchone()
    assert json.loads(row["explanation"])["evidence_refs"] == [
        observation.observation_key]


def test_a_claim_that_does_not_exist_is_refused_and_not_silently_dropped(p6_conn,
                                                                         one_file):
    """The person believes they have told the product something.

    `src/cli.py:apply_answers` states the rule for the other gesture this command
    has: an answer naming no question is "REFUSED rather than ignored ... a silently
    dropped answer is the worst of both -- no effect, and no way to tell". A
    rejection is the same shape and gets the same treatment.
    """
    from facts.learning import NoSuchClaim, reject_claim

    file_id, content_hash, _ = one_file
    _run(p6_conn, file_id, content_hash)

    with pytest.raises(NoSuchClaim):
        reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", value="CHEM2100", action="reject",
                     user_id="user-1", observed_at=CLOCK)
    # Nothing was written: a refused gesture leaves no half-record behind.
    assert p6_conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE polarity IS NOT NULL"
    ).fetchone()["n"] == 0


def test_the_action_name_is_the_callers_and_p6_coins_none(p6_conn, one_file):
    """P13 owns the gesture vocabulary and `facts` may not import P13.

    `record_correction`'s own rule: "the action vocabulary is P13's and P6 does not
    coin a name another part owns." So `action` is required and has no default, and
    this module holds no action string at all -- `src/cli.py` passes
    `review_surface.vocabulary.ACTION_REJECT`.
    """
    import inspect

    from facts import learning as learning_module
    from facts.learning import reject_claim

    signature = inspect.signature(reject_claim)
    assert signature.parameters["action"].default is inspect.Parameter.empty

    for name in dir(learning_module):
        value = getattr(learning_module, name)
        if isinstance(value, str) and not name.startswith("__"):
            assert "reject_fact" not in value and "reject_claim" not in value


# --- the other half of a rejection: the standing row is retracted -----------------
#
# The guard stops the NEXT proposal. On its own that is invisible: the row written on
# the run BEFORE the person objected is still there, still `direct`, still active, and
# still what P10 and P11 build a folder out of. Measured on a real three-file corpus
# (`src/cli.py` at HEAD, the loop driven by hand): a person rejected `subject =
# INV20261` on an invoice, ran the command again, and the plan came back identical.
#
# So §8.7's two sentences are two obligations, not one. "Rejected facts persist with
# their evidence so the same attractive-but-incorrect conclusion is not resurfaced"
# is the guard. "Each produces ... a `rejected` fact retained with the evidence that
# produced it" (SPEC, Correction learning) is this.


def test_the_standing_fact_is_retracted_not_just_the_next_one_blocked(p6_conn,
                                                                      one_file):
    from facts.learning import reject_claim
    from facts.read_surface import proposal_eligible

    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    assert [row["field_key"] for row in
            proposal_eligible(p6_conn, file_id=file_id,
                              content_hash=content_hash)] == ["subject"]

    reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="PHYS1401", action="reject",
                 user_id="user-1", observed_at=CLOCK)

    # THE VISIBLE CHANGE: no folder proposal may rest on it any more.
    assert proposal_eligible(p6_conn, file_id=file_id,
                             content_hash=content_hash) == []


def test_the_retracted_row_stays_readable_with_its_evidence(p6_conn, one_file):
    """§8.2 retains and never discards; §8.7 keeps the rejection WITH its evidence.

    "Not proposable" and "not readable" are different, and a person asking why the
    product ever suggested this has to be able to get an answer.
    """
    from facts.learning import reject_claim
    from facts.states import REJECTED
    from facts.supersede import fact_history

    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="PHYS1401", action="reject",
                 user_id="user-1", observed_at=CLOCK)

    history = fact_history(p6_conn, file_id=file_id, field_key="subject")
    assert [row["reliability_state"] for row in history] == ["direct", REJECTED]
    assert history[0]["supersede_reason"]
    for row in history:
        assert json.loads(row["evidence_refs"]) == [observation.observation_key]
    # And the rejection names who made it, which is what §8.7's column is for.
    assert "user-1" in history[1]["rejection_reason"]


def test_the_retraction_and_the_learning_record_are_one_gesture(p6_conn, one_file):
    """Either both land or neither does.

    A retraction with no learning record forgets the correction on the next run; a
    learning record with no retraction leaves the folder standing. Half of this
    gesture is worse than none of it, so it is one transaction.
    """
    from facts.learning import reject_claim

    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="PHYS1401", action="reject",
                 user_id="user-1", observed_at=CLOCK)

    rejections = p6_conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE polarity = 'reject'").fetchone()["n"]
    retracted = p6_conn.execute(
        "SELECT COUNT(*) AS n FROM file_facts WHERE reliability_state = 'rejected'"
    ).fetchone()["n"]
    assert (rejections, retracted) == (1, 1)


def test_rejecting_one_file_leaves_the_other_files_proposal_standing(p6_conn,
                                                                     tmp_path,
                                                                     one_file):
    # The scope sentence again, this time about the retraction rather than the guard.
    from facts.learning import reject_claim
    from facts.read_surface import proposal_eligible

    file_id, content_hash, observation = one_file
    other_id, other_hash = _file(p6_conn, tmp_path, name="week4.pdf", body=b"%PDF-c")
    _observe(p6_conn, run_id="run-4", file_id=other_id, content_hash=other_hash,
             raw="PHYS1401")
    _run(p6_conn, file_id, content_hash)
    _run(p6_conn, other_id, other_hash)

    reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="PHYS1401", action="reject",
                 user_id="user-1", observed_at=CLOCK)

    assert proposal_eligible(p6_conn, file_id=file_id, content_hash=content_hash) == []
    assert [row["canonical_value"] for row in
            proposal_eligible(p6_conn, file_id=other_id,
                              content_hash=other_hash)] == ["PHYS1401"]


# --- saying it twice ---------------------------------------------------------------
#
# A person does not re-run this command by editing one flag off the end of it. They
# press up-arrow and press return, `--reject` and all. Found by doing exactly that
# against the real command: the second run raised
#
#   ValueError: sha256:2123... is already superseded by sha256:70d9...;
#   the first supersede_reason is never overwritten (§8.2)
#
# P1 is right to refuse -- a second supersession of one row forks the slot's history.
# The bug was here: a gesture a person will repeat has to be repeatable.


def test_saying_the_same_thing_twice_is_not_an_error(p6_conn, one_file):
    from facts.learning import reject_claim

    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    first = reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                         field_key="subject", value="PHYS1401", action="reject",
                         user_id="user-1", observed_at=CLOCK)
    again = reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                         field_key="subject", value="PHYS1401", action="reject",
                         user_id="user-1", observed_at=CLOCK)
    # The same correction, not a second one: §8.5 counts refusals, and a person
    # pressing up-arrow twice must not read as two decisions.
    assert again == first
    assert p6_conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE polarity = 'reject'"
    ).fetchone()["n"] == 1
    assert p6_conn.execute(
        "SELECT COUNT(*) AS n FROM file_facts WHERE reliability_state = 'rejected'"
    ).fetchone()["n"] == 1


def test_a_reset_restores_the_guard_but_not_the_retracted_row(p6_conn, one_file):
    """A GAP, recorded where it is true rather than left to be discovered.

    §8.7 requires learned preferences to be resettable, and `reset_preferences` does
    reset them: `is_suppressed` stops firing and the producer runs again. What it
    cannot do is put the retracted `file_facts` row back, and the reason is
    structural rather than a missing line here.

    `write_fact` is idempotent on a fact identity that spans file, version, field,
    value, state, origin, cache key and evidence refs. A re-proposal after a reset
    matches every one of those, so it returns the SUPERSEDED row's id instead of
    writing a new one -- and a superseded row is not proposal-eligible. §8.2 is right
    that a supersession is permanent; what is missing is the way for a restored claim
    to be a NEW row rather than the old one.

    Nobody can hit this today: `reset_preferences` has no caller anywhere in `src/`,
    so a person has no way to reset anything. It belongs to P13's wave with the rest
    of the inspect/reset surface, and it is written down here so that whoever builds
    that surface finds the blocker instead of the idea.
    """
    from facts.learning import reject_claim
    from facts.read_surface import proposal_eligible

    file_id, content_hash, observation = one_file
    _run(p6_conn, file_id, content_hash)
    reject_claim(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="PHYS1401", action="reject",
                 user_id="user-1", observed_at=CLOCK)
    reset_preferences(p6_conn, FILE_SCOPE, file_id, author="P6",
                      component_version="0.1.0", user_id="user-1")

    # The guard is reset: the producer runs and is no longer suppressed.
    assert len(_run(p6_conn, file_id, content_hash)) == 1
    # But it landed back on the superseded row, so no proposal may rest on it.
    assert [row["field_key"] for row in
            proposal_eligible(p6_conn, file_id=file_id,
                              content_hash=content_hash)] == []
