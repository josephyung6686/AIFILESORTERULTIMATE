# tests/p6/test_p6_read_surface.py
"""Task 24 — the read surface published to neighbours.

Done-means 12 (a `possible` fact is absent from the proposal-eligible read), 13 (an
`authored_by` value is never returned as destination-eligible) and the read half of 19
(an `unresolved` row is absent from every fact read).
"""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import NotInVocabulary

from facts import read_surface
from facts.cache import pass_cache_key
from facts.domains import ActivationSignal, ActivationSignals
from facts.families import DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD
from facts.fields import FieldNotInCatalogue
from facts.file_facts import (
    DETERMINISTIC_EXTRACTOR, FORBIDDEN_COLUMN_SUBSTRINGS, RULE, write_fact,
)
from facts.photo_event import EVENT_FIELD
from facts.read_surface import (
    PROPOSAL_ELIGIBLE_STATES, DanglingCitation, active_allowlist_for, evidence_chain,
    event_facts, facts_for, family_facts, history, is_destination_eligible,
    proposal_eligible, session_facts, unresolved_for, values_with_counts,
)
from facts.session import DOWNLOAD_SESSION_FIELD
from facts.states import (
    DIRECT, LLM_SUPPORTED, POSSIBLE, REJECTED, STATES, STRENGTH_ORDER,
    USER_CONFIRMED, VALIDATED,
)
from facts.supersede import supersede_fact
from facts.unresolved import ATTEMPTED_PRODUCERS, UNRESOLVED_REASONS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: Task 1 owns every state name; Task 4 owns every origin name. Imported, never
#: indexed, never unpacked from a ladder whose order is the opposite of this comment.
DETERMINISTIC = DETERMINISTIC_EXTRACTOR

#: The P6 tables a read must not grow. `values` is a SQL keyword and every statement
#: naming it must quote it (preamble §3.4's second trap); `events` is P1's and a read
#: that appended one would double-count the provenance log.
COUNTED_TABLES = ('fields', '"values"', "file_facts", "unresolved", "events")


def _record(conn, tmp_path, *, name, body, parent="Downloads"):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label,
             extractor="pdf.text", zone="metadata", source_type="text_document"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _fact(conn, *, file_id, content_hash, field_key, value, ref, state, origin=None):
    """One fact through Task 4's published writer, at §3.4's key for the pass."""
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=ref, origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        value_id=value_id, reliability_state=state,
        origin=DETERMINISTIC if origin is None else origin,
        evidence_refs=(ref,),
        cache_key=pass_cache_key(conn, file_id=file_id, content_hash=content_hash),
        active=True)


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken tasks on this project before. This reads the code.
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


@pytest.fixture()
def syllabus(p6_conn, tmp_path):
    """One file carrying §3.2's worked case, plus the four rows the negatives need:
    a `possible` fact, a `rejected` fact, an `authored_by` fact and an `unresolved`
    row."""
    file_id, content_hash = _record(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"BUSIB 4300 Syllabus, Spring 2026")
    subject_ref = _observe(p6_conn, run_id="r-1", file_id=file_id,
                           content_hash=content_hash, raw="BUSIB 4300", label="title")
    author_ref = _observe(p6_conn, run_id="r-2", file_id=file_id,
                          content_hash=content_hash, raw="Jane Chen", label="Author")
    weak_ref = _observe(p6_conn, run_id="r-3", file_id=file_id,
                        content_hash=content_hash, raw="Downloads", label="parent")
    dead_ref = _observe(p6_conn, run_id="r-4", file_id=file_id,
                        content_hash=content_hash, raw="Spring 2026", label="heading")
    subject_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                       field_key="subject", value="BUSIB 4300", ref=subject_ref,
                       state=VALIDATED, origin=RULE)
    author_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="authored_by", value="Jane Chen", ref=author_ref,
                      state=DIRECT)
    session_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                       field_key=DOWNLOAD_SESSION_FIELD, value="2026-07-17T09:00Z",
                       ref=weak_ref, state=POSSIBLE)
    rejected_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                        field_key=EVENT_FIELD, value="Graduation", ref=dead_ref,
                        state=REJECTED)
    write_unresolved(
        p6_conn, file_id=file_id, content_hash=content_hash, field_key="work_type",
        reason=UNRESOLVED_REASONS[0], attempted_producers=(ATTEMPTED_PRODUCERS[0],),
        evidence_refs=(dead_ref,),
        cache_key=pass_cache_key(p6_conn, file_id=file_id, content_hash=content_hash))
    return {"file_id": file_id, "content_hash": content_hash,
            "subject_ref": subject_ref, "author_ref": author_ref,
            "subject_id": subject_id, "author_id": author_id,
            "session_id": session_id, "rejected_id": rejected_id}


# ---------------------------------------------------------------- Done-means 12 and 19

def test_the_proposal_eligible_read_excludes_possible_and_rejected(syllabus, p6_conn):
    """§3.6: a weak output "may remain a possible clue for review; it must not quietly
    become a folder proposal or an asserted file property". Both negatives at once —
    they are the two §3.6 turns on."""
    rows = proposal_eligible(p6_conn, file_id=syllabus["file_id"],
                             content_hash=syllabus["content_hash"])
    states = {row["reliability_state"] for row in rows}
    assert POSSIBLE not in states
    assert REJECTED not in states
    assert {row["field_key"] for row in rows} == {"subject", "authored_by"}


def test_proposal_eligible_states_are_derived_and_never_spelled():
    """The exclusions come from Task 1's published order, so P6 has one spelling of a
    state name and `read_surface` is not a second.

    Task 1 publishes the ladder WEAKEST FIRST — `strength()` is `STRENGTH_ORDER.index`
    and larger is stronger — so the derivation drops the FIRST member, not the last.
    """
    assert STRENGTH_ORDER[0] == POSSIBLE, "the ladder is weakest-first"
    assert PROPOSAL_ELIGIBLE_STATES == STRENGTH_ORDER[1:]
    assert POSSIBLE not in PROPOSAL_ELIGIBLE_STATES
    assert REJECTED not in PROPOSAL_ELIGIBLE_STATES
    assert set(PROPOSAL_ELIGIBLE_STATES) < set(STATES)


def test_the_strongest_states_are_never_dropped_from_a_proposal(syllabus, p6_conn):
    """The teeth of the derivation. Slicing the ladder from the wrong end would drop
    `user_confirmed` — a user's own answer — out of every folder proposal while
    excluding nothing weak, and the two assertions above would still hold if the only
    thing checked were "possible is absent"."""
    assert USER_CONFIRMED in PROPOSAL_ELIGIBLE_STATES
    assert VALIDATED in PROPOSAL_ELIGIBLE_STATES
    assert DIRECT in PROPOSAL_ELIGIBLE_STATES
    assert LLM_SUPPORTED in PROPOSAL_ELIGIBLE_STATES
    # And it is not vacuous: the fixture's two strong facts do come back.
    rows = proposal_eligible(p6_conn, file_id=syllabus["file_id"],
                             content_hash=syllabus["content_hash"])
    assert len(rows) == 2


def test_no_state_name_is_spelled_in_this_module():
    """§3.1 of the conventions: a bare literal is a second home for a published
    vocabulary. Read from the CODE, so a state named in a docstring does not count and
    a state named in a comment cannot hide one."""
    assert _code_strings(read_surface) & set(STATES) == set()


def test_an_unresolved_row_is_absent_from_every_fact_read(syllabus, p6_conn):
    """Done-means 19's read half. `unresolved` is not a weak fact: it appears in no fact
    read at all, including the proposal-eligible one, and `work_type` — the field it
    names — comes back from none of them."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    reads = (facts_for(p6_conn, **args),
             facts_for(p6_conn, states=STATES, **args),
             facts_for(p6_conn, domain="academic", **args),
             proposal_eligible(p6_conn, **args),
             event_facts(p6_conn, **args),
             session_facts(p6_conn, **args),
             family_facts(p6_conn, **args))
    for rows in reads:
        assert "work_type" not in {row["field_key"] for row in rows}
    assert [row["field_key"] for row in unresolved_for(p6_conn, **args)] == ["work_type"]


def test_the_unresolved_read_carries_no_value_and_no_state(syllabus, p6_conn):
    """It is an abstention, not a `possible`. A reader that could read a state off it
    would eventually treat it as one."""
    row = unresolved_for(p6_conn, file_id=syllabus["file_id"],
                         content_hash=syllabus["content_hash"])[0]
    assert "value_id" not in row.keys()
    assert "reliability_state" not in row.keys()


def test_unresolved_for_filters_by_field_and_by_reason(syllabus, p6_conn):
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    assert len(unresolved_for(p6_conn, field_key="work_type", **args)) == 1
    assert unresolved_for(p6_conn, field_key="subject", **args) == []
    assert len(unresolved_for(p6_conn, reason=UNRESOLVED_REASONS[0], **args)) == 1
    assert unresolved_for(p6_conn, reason=UNRESOLVED_REASONS[1], **args) == []


# ------------------------------------------------------------------- Done-means 13, §3.8

def test_an_authored_by_value_is_never_returned_as_destination_eligible(p6_conn):
    """§3.8: "It should avoid using authorship or creator identity as a destination
    dimension." Done-means 13, asserted from the read rather than from the catalogue."""
    assert is_destination_eligible(p6_conn, field_key="authored_by") is False


def test_the_creator_identity_fields_are_refused_and_the_other_two_are_not(p6_conn):
    """§3.8 names four — "authored_by and target_school, or our_firm and client" — and
    D9 splits them: authorship and creator identity are the two refused, so the read
    must say False for those two and True for the other two. A read that answered False
    for all four would pass a one-sided check while quietly banning two legitimate
    destination dimensions."""
    for field_key in ("authored_by", "our_firm"):
        assert is_destination_eligible(p6_conn, field_key=field_key) is False
    for field_key in ("target_school", "client"):
        assert is_destination_eligible(p6_conn, field_key=field_key) is True


def test_the_download_session_and_the_role_of_the_photo_event(p6_conn):
    """§3.9's session window is a review aid, never a folder level."""
    assert is_destination_eligible(p6_conn, field_key=DOWNLOAD_SESSION_FIELD) is False
    assert is_destination_eligible(p6_conn, field_key=DUPLICATE_FAMILY_FIELD) is False
    assert is_destination_eligible(p6_conn, field_key=VERSION_FAMILY_FIELD) is False


def test_a_destination_question_about_an_unknown_field_raises(p6_conn):
    """Silently answering False for a field that does not exist would let a typo read as
    a policy. §3.12 forbids inventing fields; this read does not invent one either."""
    with pytest.raises(FieldNotInCatalogue):
        is_destination_eligible(p6_conn, field_key="destination")


# --------------------------------------------------------------------- the evidence walk

def test_evidence_chain_walks_a_fact_back_to_its_p4_observations(syllabus, p6_conn):
    """Every step resolves, and what comes back is P4's frozen shape with its raw value
    unchanged (§3.2)."""
    chain = evidence_chain(p6_conn, fact_id=syllabus["subject_id"])
    assert [o.observation_key for o in chain] == [syllabus["subject_ref"]]
    assert chain[0].raw_value == "BUSIB 4300"
    assert isinstance(chain[0], Observation)


def test_evidence_chain_returns_p4s_shape_unaltered(syllabus, p6_conn):
    """The carve-out, asserted rather than assumed: this read hands back P4 objects, so
    `container_path` is a locator inside the document and not a P6 column."""
    observation = evidence_chain(p6_conn, fact_id=syllabus["subject_id"])[0]
    assert observation.location.container_path[0].label == "title"
    assert observation.location.zone == "metadata"


def test_a_citation_that_resolves_to_nothing_raises(syllabus, p6_conn):
    """§3.1: "Every fact preserves where it came from." A fact whose citation is gone is
    broken; returning an empty list would let an evidence-walk check pass by counting
    zero.

    The dangling citation is built by CITING a key that was never recorded rather than
    by deleting an observation: P4's `evidence_no_delete` trigger refuses the delete
    ("observations are superseded, never removed"), and `write_fact` checks a
    citation's SHAPE — `sha256:` and 64 hex — but never that it resolves. That gap is
    exactly what this read is here to catch.
    """
    ghost = "sha256:" + "0" * 64
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="GHOST 0000",
                            first_evidence_ref=ghost, origin=VALUE_ORIGINS[0])
    broken = write_fact(
        p6_conn, file_id=syllabus["file_id"],
        content_hash=syllabus["content_hash"], field_key="subject",
        value_id=value_id, reliability_state=VALIDATED, origin=RULE,
        evidence_refs=(ghost,),
        cache_key=pass_cache_key(p6_conn, file_id=syllabus["file_id"],
                                 content_hash=syllabus["content_hash"]),
        active=True)
    with pytest.raises(DanglingCitation):
        evidence_chain(p6_conn, fact_id=broken)
    # And the fact that IS whole still walks, so the guard is not refusing everything.
    assert evidence_chain(p6_conn, fact_id=syllabus["subject_id"])


def test_evidence_chain_on_an_unknown_fact_raises(p6_conn):
    with pytest.raises(LookupError):
        evidence_chain(p6_conn, fact_id="fact-that-was-never-written")


def test_a_dangling_citation_is_a_lookup_error_a_caller_can_catch_broadly(syllabus,
                                                                          p6_conn):
    """`DanglingCitation` is a `LookupError`, so a review UI that catches the unknown
    fact case does not have to grow a second `except` to stay safe."""
    assert issubclass(DanglingCitation, LookupError)


# -------------------------------------------------------------------- §5.5's branch counts

def test_values_with_counts_supports_the_branch_preview(p6_conn, tmp_path):
    """§5.5: "The interface can state that Option A would create three schools, five
    terms, and twelve course branches". The read has to answer that before the user
    commits, so it counts FILES per value, which is what a branch will hold."""
    for index, (name, subject) in enumerate((
            ("a.pdf", "BUSIB 4300"), ("b.pdf", "BUSIB 4300"),
            ("c.pdf", "BUSIB 4300"), ("d.pdf", "ECON 2100"),
            ("e.pdf", "STAT 1001"))):
        file_id, content_hash = _record(p6_conn, tmp_path, name=name,
                                        body=f"{subject} number {index}".encode())
        ref = _observe(p6_conn, run_id=f"run-{index}", file_id=file_id,
                       content_hash=content_hash, raw=subject, label="title")
        _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
              value=subject, ref=ref, state=VALIDATED, origin=RULE)
    assert values_with_counts(p6_conn, field_key="subject") == [
        ("BUSIB 4300", 3), ("ECON 2100", 1), ("STAT 1001", 1)]


def test_branch_counts_are_totally_ordered_so_the_preview_is_stable(p6_conn, tmp_path):
    """Count descending, then canonical value ascending. Ties are broken by the value and
    never by insertion order, which is a property of one database and not of the
    corpus."""
    for index, (name, subject) in enumerate((
            ("z.pdf", "ZOOL 1000"), ("a.pdf", "ANTH 1000"))):
        file_id, content_hash = _record(p6_conn, tmp_path, name=name,
                                        body=f"{subject}".encode())
        ref = _observe(p6_conn, run_id=f"tie-{index}", file_id=file_id,
                       content_hash=content_hash, raw=subject, label="title")
        _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
              value=subject, ref=ref, state=VALIDATED, origin=RULE)
    assert values_with_counts(p6_conn, field_key="subject") == [
        ("ANTH 1000", 1), ("ZOOL 1000", 1)]


def test_a_value_no_active_fact_points_at_is_not_a_branch(syllabus, p6_conn):
    """§3.12 lets a value auto-create on first sight. A value with no file behind it
    would preview an empty folder, so it is not a branch — the count read shows what
    will be filed, not what has ever been named."""
    ensure_value(p6_conn, field_key="subject", canonical_value="HIST 9999",
                 first_evidence_ref=syllabus["subject_ref"], origin=VALUE_ORIGINS[0])
    assert "HIST 9999" not in dict(values_with_counts(p6_conn, field_key="subject"))


def test_a_superseded_value_is_not_previewed_as_a_branch(syllabus, p6_conn):
    """§8.2 keeps the superseded row readable, and `history` is where it stays readable.
    A branch preview built from it would offer a folder for a reading the corpus no
    longer asserts — so the count read drops it while `history` keeps it."""
    ref = _observe(p6_conn, run_id="r-ocr", file_id=syllabus["file_id"],
                   content_hash=syllabus["content_hash"], raw="BUSIB 4300",
                   label="heading")
    newer = _fact(p6_conn, file_id=syllabus["file_id"],
                  content_hash=syllabus["content_hash"], field_key="subject",
                  value="BUSIB 4300 Business Analytics", ref=ref, state=VALIDATED,
                  origin=RULE)
    supersede_fact(p6_conn, old_fact_id=syllabus["subject_id"], new_fact_id=newer,
                   reason="a later pass read the heading")
    assert values_with_counts(p6_conn, field_key="subject") == [
        ("BUSIB 4300 Business Analytics", 1)]
    assert len(history(p6_conn, file_id=syllabus["file_id"], field_key="subject")) == 2


def test_counts_for_an_unknown_field_raise(p6_conn):
    with pytest.raises(FieldNotInCatalogue):
        values_with_counts(p6_conn, field_key="folder")


# ------------------------------------------------------------------- filtering and history

def test_facts_for_filters_by_state(syllabus, p6_conn):
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"], states=(POSSIBLE,))
    assert [row["field_key"] for row in rows] == [DOWNLOAD_SESSION_FIELD]


def test_facts_for_filters_by_domain(syllabus, p6_conn):
    """`domain` is a field scope. §3.11 puts `subject` in Academic; the role fields and
    `download_session` are universal, so the academic read returns one row."""
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"], domain="academic")
    assert [row["field_key"] for row in rows] == ["subject"]
    photos = facts_for(p6_conn, file_id=syllabus["file_id"],
                       content_hash=syllabus["content_hash"], domain="photos")
    assert [row["field_key"] for row in photos] == [EVENT_FIELD]


def test_the_two_filters_compose_rather_than_replacing_each_other(syllabus, p6_conn):
    """A caller narrowing by both must get the intersection. If either filter overwrote
    the other, one of these two would return a row."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    assert facts_for(p6_conn, states=(POSSIBLE,), domain="academic", **args) == []
    assert [row["field_key"] for row in
            facts_for(p6_conn, states=(VALIDATED,), domain="academic", **args)
            ] == ["subject"]


def test_an_unknown_state_or_domain_raises_rather_than_returning_nothing(syllabus,
                                                                        p6_conn):
    """An empty list for a misspelled filter is how a caller concludes there are no
    facts. P4's `check` is the project's one vocabulary gate and this read uses it."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    with pytest.raises(NotInVocabulary):
        facts_for(p6_conn, states=("LLM-supported",), **args)
    with pytest.raises(NotInVocabulary):
        facts_for(p6_conn, domain="Academic", **args)


def test_the_unfiltered_read_still_shows_rejected_facts(syllabus, p6_conn):
    """§3.13 makes `rejected` an exclusion from proposals, not from the record. The
    review UI must be able to see what was rejected and why, or §8.5's "Did it abstain
    when evidence was absent?" is unanswerable from the outside."""
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"])
    assert REJECTED in {row["reliability_state"] for row in rows}


def test_history_returns_superseded_rows(syllabus, p6_conn):
    """§8.2's worked example arriving as the ordinary path: the old row stays readable."""
    ref = _observe(p6_conn, run_id="r-ocr", file_id=syllabus["file_id"],
                   content_hash=syllabus["content_hash"], raw="BUSIB 4300",
                   label="heading")
    newer = _fact(p6_conn, file_id=syllabus["file_id"],
                  content_hash=syllabus["content_hash"], field_key="subject",
                  value="BUSIB 4300 Business Analytics", ref=ref, state=VALIDATED,
                  origin=RULE)
    supersede_fact(p6_conn, old_fact_id=syllabus["subject_id"], new_fact_id=newer,
                   reason="a later pass read the heading")
    rows = history(p6_conn, file_id=syllabus["file_id"], field_key="subject")
    assert [row["fact_id"] for row in rows] == [syllabus["subject_id"], newer]


def test_history_for_an_unknown_field_raises(p6_conn, syllabus):
    with pytest.raises(FieldNotInCatalogue):
        history(p6_conn, file_id=syllabus["file_id"], field_key="folder")


def test_the_three_handed_families_have_their_own_reads(syllabus, p6_conn):
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    assert [row["field_key"] for row in session_facts(p6_conn, **args)] == [
        DOWNLOAD_SESSION_FIELD]
    assert [row["field_key"] for row in event_facts(p6_conn, **args)] == [EVENT_FIELD]
    assert family_facts(p6_conn, **args) == []


def test_the_active_allowlist_is_the_domain_modules_answer(syllabus, p6_conn):
    """§3.12: "it should not invent new fields automatically". The allowlist read adds no
    field of its own — it republishes Task 13's under the name neighbours use, and is
    asserted to be EQUAL to it rather than merely to contain the right things."""
    from facts.domains import active_field_allowlist

    signals = ActivationSignals((ActivationSignal("academic", lambda facts: True),))
    allowlist = active_allowlist_for(
        p6_conn, file_id=syllabus["file_id"], content_hash=syllabus["content_hash"],
        activation_signals=signals)
    assert "subject" in allowlist
    assert "course" not in allowlist          # D6: the catalogue carries no such key
    assert allowlist == active_field_allowlist(
        p6_conn, file_id=syllabus["file_id"], content_hash=syllabus["content_hash"],
        activation_signals=signals)


def test_an_empty_signal_set_activates_nothing_beyond_the_universal_fields(syllabus,
                                                                          p6_conn):
    """P6 authors no activation signal, so the honest behaviour of an unauthored rule is
    the universal set and nothing else."""
    allowlist = active_allowlist_for(
        p6_conn, file_id=syllabus["file_id"], content_hash=syllabus["content_hash"],
        activation_signals=ActivationSignals(()))
    assert "subject" not in allowlist
    assert DOWNLOAD_SESSION_FIELD in allowlist


# ----------------------------------------------------------- the negative contract, §3.14

def test_no_read_returns_a_path_a_destination_a_folder_or_a_group(syllabus, p6_conn):
    """§3.14: "A fact such as subject = BUSIB 4300 does not itself dictate one permanent
    folder path." Task 4 asserts this from `PRAGMA table_info`; this asserts it from the
    shapes that leave the package, so a column that reached a neighbour would fail
    twice."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    reads = (facts_for(p6_conn, **args),
             proposal_eligible(p6_conn, **args),
             unresolved_for(p6_conn, **args),
             event_facts(p6_conn, **args),
             session_facts(p6_conn, **args),
             family_facts(p6_conn, **args),
             history(p6_conn, file_id=syllabus["file_id"], field_key="subject"))
    assert all(rows for rows in reads[:3])
    for rows in reads:
        for row in rows:
            for key in row.keys():
                for forbidden in FORBIDDEN_COLUMN_SUBSTRINGS:
                    assert forbidden not in key.lower(), (key, forbidden)


def test_the_forbidden_key_guard_can_fail():
    """The teeth of the assertion above. If `FORBIDDEN_COLUMN_SUBSTRINGS` were empty, or
    the key comparison were case-sensitive against an upper-case column, the loop would
    pass over every row for the wrong reason."""
    assert FORBIDDEN_COLUMN_SUBSTRINGS
    offences = [key for key in ("destination_node_id", "FOLDER_PATH", "group_id")
                if any(f in key.lower() for f in FORBIDDEN_COLUMN_SUBSTRINGS)]
    assert offences == ["destination_node_id", "FOLDER_PATH", "group_id"]


def test_the_read_surface_writes_nothing(syllabus, p6_conn):
    """A read that could change what it reports is not a read. Asserted over the whole
    module by comparing every P6 table — and P1's `events` — before and after every read
    runs."""
    def snapshot():
        return {table: p6_conn.execute(
                    f"SELECT count(*) FROM {table}").fetchone()[0]
                for table in COUNTED_TABLES}

    before = snapshot()
    assert all(before[table] for table in COUNTED_TABLES)
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    facts_for(p6_conn, **args)
    facts_for(p6_conn, states=(VALIDATED,), domain="academic", **args)
    proposal_eligible(p6_conn, **args)
    unresolved_for(p6_conn, **args)
    event_facts(p6_conn, **args)
    session_facts(p6_conn, **args)
    family_facts(p6_conn, **args)
    history(p6_conn, file_id=syllabus["file_id"], field_key="subject")
    evidence_chain(p6_conn, fact_id=syllabus["subject_id"])
    values_with_counts(p6_conn, field_key="subject")
    is_destination_eligible(p6_conn, field_key="authored_by")
    active_allowlist_for(p6_conn, activation_signals=ActivationSignals(()), **args)
    assert snapshot() == before


def test_no_read_accepts_a_group(p6_conn):
    """§4.3 and §4.1: the graph "does not automatically copy those missing facts onto
    sparse files". A read that took a group id would be the place that started."""
    checked = 0
    for name, member in vars(read_surface).items():
        if name.startswith("_") or not callable(member):
            continue
        if getattr(member, "__module__", None) != read_surface.__name__:
            continue
        if isinstance(member, type):
            # `DanglingCitation` is a class, and `inspect.signature` raises
            # `ValueError: no signature found for builtin type` on an exception
            # subclass that defines no `__init__`. A class takes no read arguments;
            # the functions below are the surface this guard is about.
            continue
        parameters = set(inspect.signature(member).parameters)
        assert not parameters & {"group_id", "group", "group_ids", "members",
                                 "member_ids", "anchor", "anchor_file_id"}, name
        checked += 1
    assert checked >= 11, "the whole published surface must have been inspected"


def test_every_published_read_is_keyword_only_past_the_connection():
    """A positional `(conn, file_id, content_hash)` call is how two arguments get
    swapped silently. Every read here takes its narrowing by name."""
    for name, member in vars(read_surface).items():
        if name.startswith("_") or not callable(member):
            continue
        if getattr(member, "__module__", None) != read_surface.__name__:
            continue
        if isinstance(member, type):
            continue
        positional = [p for p in inspect.signature(member).parameters.values()
                      if p.kind is p.POSITIONAL_OR_KEYWORD]
        assert [p.name for p in positional] == ["conn"], name


def test_the_branch_preview_counts_only_proposal_eligible_facts(p6_conn, tmp_path):
    """The two reads in this one module must not disagree about the same file.

    `values_with_counts` counted every live fact, so a `rejected` conclusion and a
    `possible` one each got their own branch while `proposal_eligible` returned
    nothing for those files. §5.5's preview promised folders no proposal could rest
    on — §3.6 says a `possible` fact "must not quietly become a folder proposal", and
    §8.7 names resurfacing a rejected grouping as the failure the learning store
    exists to stop.
    """
    kept, rejected, possible = None, None, None
    for index, (name, subject, state) in enumerate((
            ("keep.pdf", "BUSIB 4300", VALIDATED),
            ("no.pdf", "ECON 2100", REJECTED),
            ("weak.pdf", "HIST 3000", POSSIBLE))):
        file_id, content_hash = _record(p6_conn, tmp_path, name=name,
                                        body=f"{subject} number {index}".encode())
        ref = _observe(p6_conn, run_id=f"pe-{index}", file_id=file_id,
                       content_hash=content_hash, raw=subject, label="title")
        _fact(p6_conn, file_id=file_id, content_hash=content_hash,
              field_key="subject", value=subject, ref=ref, state=state, origin=RULE)
        if state is VALIDATED:
            kept = (file_id, content_hash)
        elif state is REJECTED:
            rejected = (file_id, content_hash)
        else:
            possible = (file_id, content_hash)

    assert values_with_counts(p6_conn, field_key="subject") == [("BUSIB 4300", 1)]

    # and the preview agrees with the eligibility read, file by file
    assert proposal_eligible(p6_conn, file_id=kept[0], content_hash=kept[1])
    assert proposal_eligible(p6_conn, file_id=rejected[0],
                             content_hash=rejected[1]) == []
    assert proposal_eligible(p6_conn, file_id=possible[0],
                             content_hash=possible[1]) == []


# ---------------------------------------------- a replaced conclusion is not proposable

def test_a_superseded_conclusion_is_not_proposal_eligible(syllabus, p6_conn):
    """§3.13 makes `rejected` an exclusion from proposals; §8.2 keeps a superseded row
    READABLE. A readable old row is not a folder the product still proposes — which
    `values_with_counts` says in its own docstring 23 lines below and enforces in SQL,
    and which `proposal_eligible` did not. The replaced conclusion reached P10's and
    P11's folder-proposal read, so a tree was proposed from stale truth."""
    ref = _observe(p6_conn, run_id="r-newer", file_id=syllabus["file_id"],
                   content_hash=syllabus["content_hash"], raw="BUSIB 4301",
                   label="heading")
    newer = _fact(p6_conn, file_id=syllabus["file_id"],
                  content_hash=syllabus["content_hash"], field_key="subject",
                  value="BUSIB 4301", ref=ref, state=VALIDATED, origin=RULE)
    supersede_fact(p6_conn, old_fact_id=syllabus["subject_id"], new_fact_id=newer,
                   reason="a later pass read the heading")

    args = {"file_id": syllabus["file_id"], "content_hash": syllabus["content_hash"]}
    proposable = {row["fact_id"] for row in proposal_eligible(p6_conn, **args)}
    assert syllabus["subject_id"] not in proposable
    assert newer in proposable
    # and §8.2's "still able to inspect the origin" is untouched by the narrowing
    assert syllabus["subject_id"] in {row["fact_id"]
                                      for row in facts_for(p6_conn, **args)}
    assert syllabus["subject_id"] in {
        row["fact_id"] for row in history(p6_conn, file_id=syllabus["file_id"],
                                          field_key="subject")}


def test_an_inactive_fact_is_not_proposal_eligible(syllabus, p6_conn):
    """`active = 0` and a non-null `superseded_by` are both "this conclusion was
    replaced". The state filter alone answered neither."""
    ref = _observe(p6_conn, run_id="r-dead", file_id=syllabus["file_id"],
                   content_hash=syllabus["content_hash"], raw="HIST 1000",
                   label="heading")
    value_id = ensure_value(p6_conn, field_key="subject", canonical_value="HIST 1000",
                            first_evidence_ref=ref, origin=VALUE_ORIGINS[0])
    inactive = write_fact(
        p6_conn, file_id=syllabus["file_id"], content_hash=syllabus["content_hash"],
        field_key="subject", value_id=value_id, reliability_state=VALIDATED,
        origin=RULE, evidence_refs=(ref,),
        cache_key=pass_cache_key(p6_conn, file_id=syllabus["file_id"],
                                 content_hash=syllabus["content_hash"]),
        active=False)

    args = {"file_id": syllabus["file_id"], "content_hash": syllabus["content_hash"]}
    assert inactive not in {row["fact_id"]
                            for row in proposal_eligible(p6_conn, **args)}
    assert inactive in {row["fact_id"] for row in facts_for(p6_conn, **args)}


def test_the_two_reads_in_this_module_agree(syllabus, p6_conn):
    """The defect `values_with_counts` was written to fix, from the other side: for one
    field, the values a proposal may rest on are exactly the values the branch preview
    counts. They disagreed about the same file in both directions."""
    ref = _observe(p6_conn, run_id="r-agree", file_id=syllabus["file_id"],
                   content_hash=syllabus["content_hash"], raw="BUSIB 4301",
                   label="heading")
    newer = _fact(p6_conn, file_id=syllabus["file_id"],
                  content_hash=syllabus["content_hash"], field_key="subject",
                  value="BUSIB 4301", ref=ref, state=VALIDATED, origin=RULE)
    supersede_fact(p6_conn, old_fact_id=syllabus["subject_id"], new_fact_id=newer,
                   reason="a later pass read the heading")

    proposable = {row["canonical_value"]
                  for row in proposal_eligible(
                      p6_conn, file_id=syllabus["file_id"],
                      content_hash=syllabus["content_hash"])
                  if row["field_key"] == "subject"}
    counted = {value for value, _count in values_with_counts(p6_conn,
                                                             field_key="subject")}
    assert proposable == counted
