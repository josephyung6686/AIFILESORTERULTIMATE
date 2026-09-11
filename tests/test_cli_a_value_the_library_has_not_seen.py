# tests/test_cli_a_value_the_library_has_not_seen.py
"""`104` §18.2 gap 3, second half: what happens AFTER the person is asked.

`00`:298, the whole sentence, because only its first clause was built:

    "`work_type`, `subject`, `term` and user labels are model decisions grounded in
    the file's evidence. A value the shipped library has not seen is proposed once;
    THE USER CONFIRMS OR RENAMES IT; IT THEN BELONGS TO THAT USER'S VOCABULARY IN THE
    DATABASE. There are no alias tables or equivalence maps in code."

`cli.normalize_for_review` does the proposing. Nothing read the answer back, so a
value confirmed on Monday was proposed again on Tuesday and could never become a
folder however many times the person said yes -- `possible` is below
`PROPOSAL_ELIGIBLE_STATES` by construction. `cli.normalize_with_the_persons_own_values`
is the read: the shipped library answers first, and where it has nothing to say the
person's own confirmed values do.

The vocabulary is DATA in their database and not a table in this repo. A confirmation
is a `user_confirmed` fact -- §3.13's strongest state, which P6 already refuses to
demote -- and a rename is `facts.values.merge_values`, whose one job is to record an
alias and delete nothing. Two people who answer differently get different normalisers
out of the same code, which is what "that user's vocabulary" means.

WHAT IS NOT BUILT, AND IS ASSERTED NOWHERE BECAUSE IT DOES NOT EXIST: there is no
`--confirm` and no `--rename` on this command. These tests play the person by writing
what those gestures would write, through P6's own writers. The screen test at the foot
pins what the report says about that, because a screen that printed a flag nobody can
type would break `84` §6.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from database_agent.db import create_schema  # noqa: E402
from database_agent.files_table import get_file, record_file  # noqa: E402
from evidence_shape.location import Location, Segment  # noqa: E402
from evidence_shape.observation import Observation  # noqa: E402
from evidence_shape.runs import ExtractionRun  # noqa: E402
from evidence_shape.schema import create_evidence_schema  # noqa: E402
from evidence_shape.store import record_observation, record_run  # noqa: E402
from facts.cache import pass_cache_key  # noqa: E402
from facts.fields import create_fields  # noqa: E402
from facts.file_facts import (  # noqa: E402
    LLM_INTERPRETATION, USER_CORRECTION, write_fact,
)
from facts.read_surface import confirmed_spellings  # noqa: E402
from facts.read_surface import versions_in_fields  # noqa: E402
from facts.states import POSSIBLE, USER_CONFIRMED  # noqa: E402
from facts.values import VALUE_ORIGINS, ensure_value, merge_values  # noqa: E402

CLOCK = "2026-09-09T12:00:00+00:00"


@pytest.fixture()
def corpus(conn, tmp_path):
    """One indexed file with one reading, which is all any of these needs.

    The reading is real rather than a stub because `_print_values_to_confirm` walks a
    proposal back to the observation it cites and prints the line the model was
    reading; a fixture with no evidence would let that half pass while printing
    nothing.
    """
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    body = b"Proposed Scope of the module\nTrimester 2 2025 reading list\n"
    path = tmp_path / "module handbook.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="module handbook.pdf",
        normalized_filename="module handbook.pdf", extension=".pdf",
        observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id="r-1", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=body.decode("utf-8"),
        location=Location("heading", (Segment("field", label="heading"),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id="r-1")
    record_observation(conn, observation)
    return {"conn": conn, "file_id": file_id, "content_hash": content_hash,
            "key": observation.observation_key}


def _value(corpus, *, field_key: str, canonical: str) -> str:
    return ensure_value(
        corpus["conn"], field_key=field_key, canonical_value=canonical,
        first_evidence_ref=corpus["key"], origin=VALUE_ORIGINS[0])


def _proposed(corpus, *, field_key: str, canonical: str) -> str:
    """What site A writes for an `accept_context_supported` answer: a `possible` fact.

    `llm_harness.fact_validation.proposal_state_from_p8` is the one that decides this
    and it is not re-decided here -- the state is read off `facts.states`, and the
    tests in `tests/p8/test_p8_subject_title_to_review.py` are what pin that the seam
    produces it.
    """
    value_id = _value(corpus, field_key=field_key, canonical=canonical)
    write_fact(
        corpus["conn"], file_id=corpus["file_id"],
        content_hash=corpus["content_hash"], field_key=field_key,
        value_id=value_id, reliability_state=POSSIBLE, origin=LLM_INTERPRETATION,
        evidence_refs=(corpus["key"],),
        cache_key=pass_cache_key(
            corpus["conn"], file_id=corpus["file_id"],
            content_hash=corpus["content_hash"]) + f":{canonical}",
        active=True)
    return value_id


def _confirmed(corpus, *, field_key: str, canonical: str) -> str:
    """The person's answer, written the way the missing gesture would write it.

    `user_confirmed` with no citation: §3.1's evidence rule exempts exactly this state
    (`facts.file_facts._checked_refs` -- "a user asserting a fact is not citing
    evidence"), because the person is the evidence.
    """
    value_id = _value(corpus, field_key=field_key, canonical=canonical)
    write_fact(
        corpus["conn"], file_id=corpus["file_id"],
        content_hash=corpus["content_hash"], field_key=field_key,
        value_id=value_id, reliability_state=USER_CONFIRMED,
        origin=USER_CORRECTION, evidence_refs=(),
        cache_key=f"sha256:confirmed:{field_key}:{canonical}", active=True)
    return value_id


# --- the vocabulary the person builds ---------------------------------------------


def test_a_confirmed_proposal_is_normalised_on_the_next_run(corpus):
    """`00`:298's middle clause, which nothing read until `104` §18.2 gap 3.

    **SABOTAGE:** bind `normalize=normalize_for_model` at the composition root again,
    so nothing ever reads the person's answer back. The value is then proposed on
    every run for the rest of the corpus's life, the person confirms it again every
    time, and it never becomes a folder -- `possible` is below
    `PROPOSAL_ELIGIBLE_STATES`, so confirming would change nothing that anybody could
    see. "Proposed ONCE" is the design's own word, and once means the next run knows.

    The pure function is asserted unchanged in the same breath. `normalize_for_model`
    is P6's deployment rule and dozens of pins call it bare; what learns is the
    normaliser injected at the seam, which is the only one that can have a database.
    """
    normalize = cli.normalize_with_the_persons_own_values(corpus["conn"])

    assert cli.normalize_for_model("work_type", "Proposed Scope") is None
    assert normalize("work_type", "Proposed Scope") is None
    # ... and that is why it is a proposal rather than a rejection.
    assert cli.normalize_for_review(
        "work_type", "Proposed Scope") == "Proposed Scope"

    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    assert normalize("work_type", "Proposed Scope") is None, (
        "a proposal nobody has answered is not yet the person's vocabulary")

    _confirmed(corpus, field_key="work_type", canonical="Proposed Scope")
    assert normalize("work_type", "Proposed Scope") == "Proposed Scope"
    # The deployment's own rule did not move an inch.
    assert cli.normalize_for_model("work_type", "Proposed Scope") is None


def test_a_confirmed_term_is_normalised_on_the_next_run(corpus):
    """The same clause for the other field gap 3 opened.

    **SABOTAGE:** scope the confirmed-value read to `work_type`, or to `subject`, so
    one of the three fields `00`:298 names learns and the others do not. `105` §14.2
    ruled in five term forms and a person whose university writes a sixth is exactly
    the case the sentence is about; a `term` that has to be re-confirmed every run is
    the closed catalogue with an extra step.
    """
    normalize = cli.normalize_with_the_persons_own_values(corpus["conn"])

    assert normalize("term", "Trimester 2 2025") is None
    _confirmed(corpus, field_key="term", canonical="Trimester 2 2025")
    assert normalize("term", "Trimester 2 2025") == "Trimester 2 2025"
    # The five ruled-in forms still answer from the catalogue, in its spelling.
    assert normalize("term", "Spring-2026") == "Spring2026"


def test_a_renamed_proposal_maps_from_the_spelling_the_model_used(corpus):
    """`00`:298's "or renames it", and its next sentence in the same test.

    **SABOTAGE:** write a `{"Proposed Scope": "scope note"}` mapping into `src/` --
    or a casefold comparison, or a token match -- to make the rename work. `00`:298
    forbids all three in one line: *"There are no alias tables or equivalence maps in
    code."* The equivalence belongs in the person's database, and it is already there:
    `facts.values.merge_values` records the merged value's canonical wording as an
    alias of the survivor and deletes nothing, so one row answers to both spellings
    and a reader can still see where the old one went.

    This is what the missing rename gesture would do: the person is shown
    `Proposed Scope`, types their own word for it, and the model's spelling stops
    being a second folder.
    """
    conn = corpus["conn"]
    normalize = cli.normalize_with_the_persons_own_values(conn)

    proposed = _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    kept = _confirmed(corpus, field_key="work_type", canonical="scope note")
    merge_values(conn, keep=kept, merged=proposed,
                 reason="the person renamed the proposal")

    assert normalize("work_type", "Proposed Scope") == "scope note"
    assert normalize("work_type", "scope note") == "scope note"
    # AND THE MERGED ROW IS STILL READABLE (§8.2). Nothing was deleted to make the
    # rename work, so a fact that already pointed at the model's spelling resolves.
    merged_row = [row for row in conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (proposed,))][0]
    assert merged_row["merged_into"] == kept
    assert merged_row["canonical_value"] == "Proposed Scope"


def test_the_shipped_library_still_answers_first_and_in_its_own_spelling(corpus):
    """The seed is not overtaken by the person's vocabulary, and the order says so.

    **SABOTAGE:** ask the person's values first. Then a corpus in which somebody once
    confirmed `Lecture` (the document's casing) stops getting the library's `lecture`,
    and `LECTURE SLIDES week 1.pdf` and `Lecture Slides Week 2.pdf` are two folders
    for one kind of work -- `65` §4.2's recorded failure, arriving through the door
    this change opened. `00`:298: *"the ratified library is the vocabulary the model
    is shown first."*
    """
    normalize = cli.normalize_with_the_persons_own_values(corpus["conn"])
    _confirmed(corpus, field_key="work_type", canonical="Lecture")

    assert normalize("work_type", "Lecture") == "lecture"
    assert normalize("work_type", "  HOMEWORK  ") == "homework"


def test_a_confirmation_the_person_has_replaced_is_not_a_standing_answer(corpus):
    """Live rows only, which is `proposal_eligible`'s filter and not a new one.

    **SABOTAGE:** drop the `active` and `superseded_by` tests from
    `confirmed_spellings`. §8.2 keeps a replaced conclusion READABLE, and readable is
    not standing -- `read_surface.proposal_eligible`'s own docstring records what
    happened the last time two reads in that module disagreed about it: "a replaced
    conclusion reached P10's and P11's folder-proposal read, so a tree was proposed
    from stale truth". A withdrawn confirmation that still normalises is that defect,
    one field over.
    """
    conn = corpus["conn"]
    value_id = _confirmed(corpus, field_key="work_type", canonical="scope note")
    assert cli.normalize_with_the_persons_own_values(conn)(
        "work_type", "scope note") == "scope note"

    conn.execute("UPDATE file_facts SET active = 0 WHERE value_id = ?", (value_id,))
    assert cli.normalize_with_the_persons_own_values(conn)(
        "work_type", "scope note") is None


def test_a_spelling_that_reaches_two_confirmed_values_is_refused_not_guessed(corpus):
    """Refuse rather than guess, which is this codebase's answer everywhere else.

    **SABOTAGE:** keep the first row a sort happens to return. Two confirmed values
    can come to share a spelling -- the person renames A into B when B already carried
    that alias -- and answering with whichever sorted first would make the canonical
    form of somebody's folder depend on a `ORDER BY`. Left out, the value is proposed
    again and the person is asked; that is the same choice §3.7 makes when two
    candidates are within the margin.
    """
    conn = corpus["conn"]
    shared = _value(corpus, field_key="work_type", canonical="Proposed Scope")
    first = _confirmed(corpus, field_key="work_type", canonical="alpha note")
    second = _confirmed(corpus, field_key="work_type", canonical="beta note")
    # Both survivors absorb the same spelling as an alias.
    merge_values(conn, keep=first, merged=shared, reason="renamed once")
    conn.execute('UPDATE "values" SET aliases = ? WHERE value_id = ?',
                 (json.dumps(["Proposed Scope"]), second))

    reached = confirmed_spellings(conn, field_key="work_type")
    assert reached["alpha note"] == "alpha note"
    assert reached["beta note"] == "beta note"
    assert "Proposed Scope" not in reached
    assert cli.normalize_with_the_persons_own_values(conn)(
        "work_type", "Proposed Scope") is None


def test_a_field_with_no_facts_at_all_answers_empty_and_does_not_raise(corpus):
    """The read is asked of every field a model answers, including untouched ones."""
    assert confirmed_spellings(corpus["conn"], field_key="instructor") == {}


# --- the screen -------------------------------------------------------------------


def _screen(corpus) -> str:
    out = io.StringIO()
    cli._print_values_to_confirm(corpus["conn"], out)
    return out.getvalue()


def test_a_proposal_reaches_the_screen_with_the_line_the_model_was_reading(corpus):
    """`104` §18.2 gap 3's last clause: *a proposal the person SEES*.

    **SABOTAGE:** leave the `possible` row in the database and print nothing, which is
    what every run did between R-98 and this change. A proposal nobody is shown is not
    a proposal -- it is the same silent loss the `VALUE_NOT_NORMALIZABLE` rejection
    was, with a better state name on it, and `00`:259's standing rule is that what a
    run decided is reported rather than left in a table.

    The evidence beside it is the model's own citation, walked back to the P4
    observation through `read_surface.evidence_chain`. Gap 3 asks for it by name --
    "with the model's evidence beside it" -- because a question about a value with no
    line under it is a request to trust a machine.
    """
    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    _proposed(corpus, field_key="term", canonical="Trimester 2 2025")
    screen = _screen(corpus)

    assert "New values the model proposed, waiting on you:" in screen
    assert "work type: 'Proposed Scope' -- on 1 file" in screen
    assert "term: 'Trimester 2 2025' -- on 1 file" in screen
    assert "'module handbook.pdf'" in screen
    assert "The model was reading: 'Proposed Scope of the module'" in screen


def test_the_screen_offers_every_gesture_that_exists_and_no_other(corpus):
    """`84` §6: what the screen tells a person to type has to be true.

    **SABOTAGE:** print a flag because it reads better. Until `104` §18.2 gap 3's
    two gestures were built this test asserted the opposite -- `--confirm` must
    NOT appear, because there was no such flag and the one place the product asked
    a question would have been the one place it lied. The rule did not change; the
    flags did, so the assertion moved with them and the parser is now asked
    directly rather than trusted.

    Every command the screen prints is parsed here, so a gesture that is printed
    and then refused by argparse cannot survive a run of this file.
    """
    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    screen = _screen(corpus)

    assert "--reject 'module handbook.pdf:work_type=Proposed Scope'" in screen
    assert "--confirm 'module handbook.pdf:work_type=Proposed Scope'" in screen
    assert "--rename 'module handbook.pdf:work_type=" in screen
    assert "not a gesture this command has yet" not in screen

    # AND THE CONFIRM LINE THE SCREEN PRINTS ACTUALLY WORKS, which is the same
    # check `test_the_reject_line_the_screen_prints_actually_works` makes one
    # gesture along: printing a command is a promise that typing it does
    # something, and the form is where that promise is easiest to break.
    import shlex
    typed = next(shlex.split(line.strip())[1] for line in screen.splitlines()
                 if line.strip().startswith("--confirm "))
    cli.apply_confirmations(corpus["conn"], [typed], user_id="jy",
                            observed_at=CLOCK)
    assert cli.normalize_with_the_persons_own_values(corpus["conn"])(
        "work_type", "Proposed Scope") == "Proposed Scope"


def test_the_reject_line_the_screen_prints_actually_works(corpus):
    """`84` §6, checked rather than asserted in prose: the one gesture offered runs.

    **SABOTAGE:** print `--reject` beside a proposal without checking that
    `facts.learning.reject_claim` can find a `possible` fact. It raises `NoSuchClaim`
    for a claim it cannot find, and if its lookup were narrowed to proposal-eligible
    states -- which is what almost every other read in `read_surface` does -- the
    product would print a command that refuses, on the one screen where it asks the
    person a question. It works because `reject_claim` reads `facts_for_file`
    unfiltered, and this test is what stops that being "tidied" to match its
    neighbours.

    The second half is the part nothing else checks: a rejection CLOSES the question.
    The retraction supersedes the standing row, so the proposal drops out of the block
    on the next run and the person is not asked again about something they answered.
    """
    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    assert "--reject 'module handbook.pdf:work_type=Proposed Scope'" in _screen(corpus)

    cli.apply_rejections(
        corpus["conn"], ["module handbook.pdf:work_type=Proposed Scope"],
        user_id="jy", observed_at=CLOCK)

    assert _screen(corpus) == ""


def test_a_confirmed_value_is_no_longer_a_question(corpus):
    """The block asks about what is open, and a confirmation closes it.

    **SABOTAGE:** print every fact in the three fields rather than the `possible`
    ones. A person would then be re-asked about values they have already answered,
    which §12's own rule about set-aside questions forbids in the same words -- "the
    pressure of re-asking".
    """
    _confirmed(corpus, field_key="work_type", canonical="scope note")
    assert _screen(corpus) == ""


def test_a_run_with_nothing_to_confirm_prints_no_block_at_all(corpus):
    """An empty heading is a paragraph about nothing, and the screen has enough."""
    assert _screen(corpus) == ""


# --- the gestures themselves (`104` §18.2 gap 3's two owed flags) -------------------


def _typed(corpus, gesture: str, *flags: str) -> None:
    """One `--confirm` or `--rename` as `cli.main` would apply it.

    The applier is called rather than `cli.main`, and that is the whole reach of
    this fixture: every other test in this file builds its proposal by hand, so
    there is no run to hang a flag off. What it does exercise is the part the
    gesture is -- the parse, the file lookup, the refusal wording, and P6's two
    writes -- which is everything between the typed string and the database.
    """
    applier = (cli.apply_confirmations if gesture == "--confirm"
               else cli.apply_renames)
    applier(corpus["conn"], list(flags), user_id="jy", observed_at=CLOCK)


def _states(corpus, field_key: str) -> dict:
    """Canonical value -> reliability state, for every live fact in one field."""
    return {row["canonical_value"]: row["reliability_state"]
            for rows in versions_in_fields(
                corpus["conn"], field_keys=(field_key,)).values()
            for row in rows
            if row["active"] and row["superseded_by"] is None}


def test_confirming_a_proposal_makes_it_the_persons_answer(corpus):
    """`--confirm`, end to end through P6, and then read back by the next run.

    **SABOTAGE:** write the `user_confirmed` row and leave the `possible` one
    standing. `preferred_of_slot` would then have two live rows for one slot and
    the person's answer would win by a sort; §8.2 wants the old row readable, not
    live, which is why `confirm_claim` supersedes rather than deactivates.
    """
    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    _typed(corpus, "--confirm", "module handbook.pdf:work_type=Proposed Scope")

    assert _states(corpus, "work_type") == {"Proposed Scope": USER_CONFIRMED}
    normalize = cli.normalize_with_the_persons_own_values(corpus["conn"])
    assert normalize("work_type", "Proposed Scope") == "Proposed Scope"


def test_confirming_twice_is_one_correction_and_not_two(corpus):
    """A person re-runs this command by pressing up-arrow, `--confirm` and all.

    `reject_claim` found this by doing exactly that against the real command and
    `confirm_claim` inherits the answer: the second gesture returns the first
    one's event id, so §8.5's count of decisions does not read an up-arrow as a
    second decision.
    """
    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    _typed(corpus, "--confirm", "module handbook.pdf:work_type=Proposed Scope")
    _typed(corpus, "--confirm", "module handbook.pdf:work_type=Proposed Scope")

    assert _states(corpus, "work_type") == {"Proposed Scope": USER_CONFIRMED}


def test_confirming_something_nobody_proposed_is_refused_not_ignored(corpus):
    """A silently dropped confirmation is the worst of both: no effect, no way
    to tell. The refusal names the file in the person's own words."""
    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    with pytest.raises(cli.ConfirmationRefused) as refusal:
        _typed(corpus, "--confirm", "module handbook.pdf:work_type=Lecture")
    assert "module handbook.pdf" in str(refusal.value)
    assert "Lecture" in str(refusal.value)


def test_a_confirmation_that_is_not_a_pair_is_refused_with_the_form(corpus):
    with pytest.raises(cli.ConfirmationRefused) as refusal:
        _typed(corpus, "--confirm", "module handbook.pdf:work_type")
    assert "--confirm <file>:<field>=<value>" in str(refusal.value)


def test_renaming_a_proposal_gives_one_value_that_answers_to_both(corpus):
    """`--rename`, which is a confirmation of a different spelling.

    The two halves are asserted separately because either alone is a defect. The
    merge alone leaves this file's fact pointing at a row whose canonical wording
    is still the model's, so the folder keeps the name the person renamed away
    from; the confirmation alone leaves the model's spelling free to come back as
    a second value next run.

    **SABOTAGE:** compare spellings case-insensitively anywhere. `00`:298 --
    "There are no alias tables or equivalence maps in code" -- and the equivalence
    here is one the person stated once, in their own database.
    """
    proposed = _proposed(corpus, field_key="work_type",
                         canonical="Reading Response Draft")
    _typed(corpus, "--rename",
           "module handbook.pdf:work_type=Reading Response Draft>reading response")

    assert _states(corpus, "work_type") == {"reading response": USER_CONFIRMED}
    normalize = cli.normalize_with_the_persons_own_values(corpus["conn"])
    assert normalize("work_type", "Reading Response Draft") == "reading response"
    assert normalize("work_type", "reading response") == "reading response"
    # §8.2: nothing was deleted to make the rename work.
    merged = corpus["conn"].execute(
        'SELECT merged_into, canonical_value FROM "values" WHERE value_id = ?',
        (proposed,)).fetchone()
    assert merged["canonical_value"] == "Reading Response Draft"
    assert merged["merged_into"] is not None


def test_renaming_a_value_to_itself_is_refused_in_the_persons_words(corpus):
    """`merge_values` refuses a value merged into itself and its message is about
    value ids nobody has seen. Refused first, here, in the words they typed."""
    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    with pytest.raises(cli.ConfirmationRefused) as refusal:
        _typed(corpus, "--rename",
               "module handbook.pdf:work_type=Proposed Scope>Proposed Scope")
    assert "nothing to rename" in str(refusal.value)


def test_a_rename_without_the_separator_is_refused_with_the_form(corpus):
    """`>` and not a second `=`: these fields are free text a model read out of a
    document, and a value may carry an `=`."""
    with pytest.raises(cli.ConfirmationRefused) as refusal:
        _typed(corpus, "--rename", "module handbook.pdf:work_type=Proposed Scope")
    assert "<what it says>><what to call it>" in str(refusal.value)


def test_the_screen_offers_all_three_answers_and_says_so(corpus):
    """`84` §6, both ways. The block used to end by saying that saying YES was
    not a gesture this command had, which was true and is not any more; printing
    a flag that does not exist and withholding one that does are the same defect.
    """
    _proposed(corpus, field_key="work_type", canonical="Proposed Scope")
    screen = _screen(corpus)

    assert "--reject 'module handbook.pdf:work_type=Proposed Scope'" in screen
    assert "--confirm 'module handbook.pdf:work_type=Proposed Scope'" in screen
    assert ("--rename 'module handbook.pdf:work_type=Proposed Scope>Proposed "
            "Scope'") in screen
    assert "is not a gesture this command has yet" not in screen
