# tests/p6/test_p6_supersede.py
"""M1 — Done-means 29 and the history half of 15. §8.2's worked example, run."""
from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import FILE_FACTS_COLUMNS, RULE, facts_for_file, write_fact
from facts.states import USER_CONFIRMED
from facts.supersede import (
    FACT_TABLE, PreferredNeverReverses, SupersedeAcrossSlots, fact_history,
    preferred_fact, supersede_fact,
)
from facts.unresolved import (
    NO_CANDIDATE_EVIDENCE, RULE_ROUTE, unresolved_for_file, write_unresolved,
)
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: The three places §8.2 forbids the pointer from reaching. Each is another task's
#: module; a missing one is skipped rather than assumed, and the two that ship before
#: Wave D are required to be present so the guard cannot pass by being empty.
POINTER_FREE = {"facts.facets": True, "facts.fields": True,
                "facts.llm_seam": False, "facts.read_surface": False}

#: A second catalogue key, so "supersession happens inside one slot" is falsifiable.
#: NOT `document_type`: D6 rules that word is never a key, and the shipped catalogue
#: has no such row — a fact could not be written for it at all.
OTHER_FIELD = "institution"


def _mentions(module_name: str) -> set[str]:
    """Every name, attribute and string literal a module's CODE contains."""
    module = importlib.import_module(module_name)
    tree = ast.parse(inspect.getsource(module))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.add(node.value)
    return found


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Scans", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, analysis_tier="ocr",
             extractor="ocr.vision", version="1.0.0"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type="ocr", analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type="ocr", raw_value=raw,
        location=Location("ocr", (Segment("page", index=1),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _fact(conn, *, file_id, content_hash, field_key, value, key, state, cache_key):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=RULE,
                      evidence_refs=(key,), cache_key=cache_key, active=True)


@pytest.fixture()
def scanned(p6_conn, tmp_path):
    """§8.2's own case: one scanned file, and two OCR passes over it."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="transcript.pdf",
                                    body=b"a scanned transcript")
    first = _observe(p6_conn, run_id="ocr-1", file_id=file_id,
                     content_hash=content_hash, raw="C0lumb1a Un1vers1ty")
    second = _observe(p6_conn, run_id="ocr-2", file_id=file_id,
                      content_hash=content_hash, raw="Columbia University",
                      version="2.0.0")
    return file_id, content_hash, first, second


def test_the_table_this_module_addresses_carries_both_columns_it_needs(p6_conn):
    # P1's `mark_superseded` requires a column literally named `record_id`; the
    # pointer requires `preferred`. Both are Task 4's DDL and are asserted rather
    # than assumed, so a drift fails at the first run instead of at review.
    # `table_xinfo`, not `table_info`: verified by execution, `record_id` is a
    # VIRTUAL generated column and `table_info` does not list one.
    assert FACT_TABLE == "file_facts"
    columns = {row["name"] for row in
               p6_conn.execute(f"PRAGMA table_xinfo({FACT_TABLE})")}
    assert "record_id" in columns
    assert "preferred" in columns
    assert set(SUPERSEDE_COLUMNS) <= columns
    # The four this module reads directly are Task 4's published set, not guesses.
    for column in ("fact_id", "file_id", "content_hash", "reliability_state",
                   "preferred"):
        assert column in FILE_FACTS_COLUMNS, column
    assert USER_CONFIRMED == "user_confirmed"      # P4 publishes the tuple strongest-first


def test_a_superseding_fact_is_preferred_and_the_superseded_row_is_not(
        scanned, p6_conn):
    # Done-means 29.
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    rows = {r["fact_id"]: r for r in fact_history(p6_conn, file_id=file_id,
                                                  field_key="subject")}
    assert not rows[old]["preferred"]
    assert rows[new]["preferred"]
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == new


def test_both_rows_both_states_and_both_evidence_chains_remain_readable(
        scanned, p6_conn):
    # Done-means 29 and 15. §8.2: "both extraction records should remain available".
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    history = fact_history(p6_conn, file_id=file_id, field_key="subject")
    assert [r["fact_id"] for r in history] == [old, new]          # oldest first
    assert [r["reliability_state"] for r in history] == ["possible", "validated"]
    assert history[0]["supersede_reason"] == "a later OCR engine recovered the name"
    assert history[1]["supersede_reason"] is None
    for row, key in ((history[0], first), (history[1], second)):
        assert json.loads(row["evidence_refs"]) == [key]
    # And P4's raw values are untouched by any of it (§3.2, rule 1).
    raws = {r["raw_value"] for r in p6_conn.execute(
        "SELECT raw_value FROM evidence WHERE file_id = ?", (file_id,))}
    assert raws == {"C0lumb1a Un1vers1ty", "Columbia University"}


def test_section_eight_two_s_worked_example_end_to_end(scanned, p6_conn):
    # "If a first OCR pass produces unreadable text and a later improved OCR engine
    # recovers a university name, both extraction records should remain available."
    # Under B7 the first pass is a ROW, not an absence. The unresolved -> fact
    # supersession is Task 5's; what is asserted here is that the refusal survives.
    file_id, content_hash, first, second = scanned
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason=NO_CANDIDATE_EVIDENCE,
                     attempted_producers=(RULE_ROUTE,),
                     evidence_refs=(first,), cache_key="sha256:pass-zero")
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    refusals = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key="subject")
    assert [r["reason"] for r in refusals] == [NO_CANDIDATE_EVIDENCE]
    assert len(fact_history(p6_conn, file_id=file_id, field_key="subject")) == 2
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == new


def test_preferred_is_set_only_on_supersession(scanned, p6_conn):
    # The SPEC: "It is set only on supersession" and "only by the resolver". A fact
    # written by a producer carries no pointer, and a slot with one live row is still
    # answerable — the row IS the answer, without the column being set.
    file_id, content_hash, first, _ = scanned
    only = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                 state="possible", cache_key="sha256:pass-one")
    row = [r for r in facts_for_file(p6_conn, file_id, content_hash)
           if r["fact_id"] == only][0]
    assert not row["preferred"]
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == only


def test_a_user_confirmed_fact_is_always_the_preferred_row(scanned, p6_conn):
    # §3.13's ordering is not negotiable and `preferred` never reverses it.
    file_id, content_hash, first, second = scanned
    confirmed = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value="Columbia University", key=first,
                      state=USER_CONFIRMED, cache_key="sha256:user")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Colombia", key=second, state="llm_supported",
          cache_key="sha256:model")
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == confirmed


def test_preferred_never_reverses_the_reliability_ordering(scanned, p6_conn):
    # Attempted, not inspected: the refusal is at a function every route passes.
    file_id, content_hash, first, second = scanned
    confirmed = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value="Columbia University", key=first,
                      state=USER_CONFIRMED, cache_key="sha256:user")
    weaker = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                   field_key="subject", value="Colombia", key=second,
                   state="validated", cache_key="sha256:rule")
    with pytest.raises(PreferredNeverReverses):
        supersede_fact(p6_conn, old_fact_id=confirmed, new_fact_id=weaker,
                       reason="a rule disagreed with the user")
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == confirmed
    # The refusal is total: P1's three columns are untouched too, so nothing is
    # half-linked with only the pointer left behind.
    linked = p6_conn.execute(
        "SELECT supersedes, superseded_by, supersede_reason, preferred "
        "FROM file_facts WHERE fact_id IN (?, ?)", (confirmed, weaker)).fetchall()
    for row in linked:
        assert row["supersedes"] is None
        assert row["superseded_by"] is None
        assert row["supersede_reason"] is None
        assert not row["preferred"]


def test_a_user_confirmed_fact_may_still_be_superseded_by_another(scanned, p6_conn):
    # The guard is about REVERSING the ordering, not about freezing the slot: a
    # second user answer is not weaker, so it links and takes the pointer.
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia College", key=first,
                state=USER_CONFIRMED, cache_key="sha256:user-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state=USER_CONFIRMED, cache_key="sha256:user-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="the user corrected their own earlier answer")
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == new


def test_supersession_happens_inside_one_slot(scanned, p6_conn):
    # §8.2 replaces an ANSWER; a row about a different field or a different file is
    # not an earlier version of this one.
    file_id, content_hash, first, second = scanned
    subject = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="subject", value="Columbia University", key=first,
                    state="validated", cache_key="sha256:one")
    other = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                  field_key=OTHER_FIELD, value="Columbia University", key=second,
                  state="validated", cache_key="sha256:two")
    with pytest.raises(SupersedeAcrossSlots):
        supersede_fact(p6_conn, old_fact_id=subject, new_fact_id=other,
                       reason="wrong slot")
    # And the other slot's own history is untouched by the refusal.
    assert [r["fact_id"] for r in
            fact_history(p6_conn, file_id=file_id, field_key=OTHER_FIELD)] == [other]


def test_supersession_across_two_files_is_refused(scanned, p6_conn, tmp_path):
    # The slot is (file_id, field_key): the same field on a different file is a
    # different question, not an earlier version of this answer.
    file_id, content_hash, first, second = scanned
    other_id, other_hash = _record(p6_conn, tmp_path, name="second.pdf",
                                   body=b"a different scanned transcript")
    mine = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="Columbia University", key=first,
                 state="validated", cache_key="sha256:mine")
    theirs = _fact(p6_conn, file_id=other_id, content_hash=other_hash,
                   field_key="subject", value="Columbia University", key=second,
                   state="validated", cache_key="sha256:theirs")
    with pytest.raises(SupersedeAcrossSlots):
        supersede_fact(p6_conn, old_fact_id=mine, new_fact_id=theirs,
                       reason="a different file entirely")


def test_history_starts_at_the_oldest_row_of_a_three_link_chain(scanned, p6_conn):
    # The preamble's ordering constraint, made falsifiable: `chain()` walks FORWARD
    # only, so a reader that started at the newest row would return one row and look
    # correct. Three links, and the read is asked for by slot, not by row.
    file_id, content_hash, first, second = scanned
    one = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a", key=first,
                state="possible", cache_key="sha256:one")
    two = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia Univ", key=second,
                state="possible", cache_key="sha256:two")
    three = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                  field_key="subject", value="Columbia University", key=second,
                  state="validated", cache_key="sha256:three")
    supersede_fact(p6_conn, old_fact_id=one, new_fact_id=two, reason="pass two")
    supersede_fact(p6_conn, old_fact_id=two, new_fact_id=three, reason="pass three")
    assert [r["fact_id"] for r in
            fact_history(p6_conn, file_id=file_id, field_key="subject")] == [
                one, two, three]
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == three
    # The middle row keeps its OWN reason: the first is never overwritten (§8.2).
    reasons = {r["fact_id"]: r["supersede_reason"] for r in
               fact_history(p6_conn, file_id=file_id, field_key="subject")}
    assert reasons == {one: "pass two", two: "pass three", three: None}


def test_history_spans_every_content_hash_the_file_has_had(scanned, p6_conn):
    # The signature is (file_id, field_key) with no content hash, and that is right
    # for a reader: §8.2's user "does not know which version produced it".
    file_id, content_hash, first, second = scanned
    old_version = _fact(p6_conn, file_id=file_id, content_hash="0" * 64,
                        field_key="subject", value="Columbia College", key=first,
                        state="validated", cache_key="sha256:v1")
    current = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="subject", value="Columbia University", key=second,
                    state="validated", cache_key="sha256:v2")
    assert {r["fact_id"] for r in
            fact_history(p6_conn, file_id=file_id, field_key="subject")} == {
                old_version, current}


def test_several_live_rows_have_no_preferred_row(scanned, p6_conn):
    # OQ6 — multiplicity — is open and the SPEC carries `multiplicity` as an
    # UNANSWERED column. "Which of several simultaneous values is preferred" IS that
    # question, so a reader that picked one would close it by accident.
    file_id, content_hash, first, second = scanned
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Columbia University", key=first, state="validated",
          cache_key="sha256:one")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Columbia College", key=second, state="validated",
          cache_key="sha256:two")
    assert preferred_fact(p6_conn, file_id=file_id, field_key="subject") is None
    assert len(fact_history(p6_conn, file_id=file_id, field_key="subject")) == 2


def test_a_superseded_row_is_not_live_so_one_survivor_is_the_answer(scanned, p6_conn):
    # Two chains, one of them retired: the retired chain's rows are not live, so the
    # slot is answerable again and OQ6 is not reached.
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a", key=first,
                state="possible", cache_key="sha256:one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:two")
    assert preferred_fact(p6_conn, file_id=file_id, field_key="subject") is None
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new, reason="pass two")
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == new


def test_an_empty_slot_has_no_preferred_row_and_no_history(scanned, p6_conn):
    file_id, _, _, _ = scanned
    assert preferred_fact(p6_conn, file_id=file_id, field_key="subject") is None
    assert fact_history(p6_conn, file_id=file_id, field_key="subject") == []


def test_one_slot_never_sees_another_slot_s_rows(scanned, p6_conn):
    # `field_key` is a filter, not decoration: a fact in a neighbouring slot must not
    # appear in this slot's history or become its preferred row.
    file_id, content_hash, first, second = scanned
    subject = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="subject", value="Columbia University", key=first,
                    state="validated", cache_key="sha256:one")
    other = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                  field_key=OTHER_FIELD, value="Columbia University", key=second,
                  state="validated", cache_key="sha256:two")
    assert [r["fact_id"] for r in
            fact_history(p6_conn, file_id=file_id, field_key="subject")] == [subject]
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key=OTHER_FIELD)["fact_id"] == other


def test_supersession_appends_no_event(scanned, p6_conn):
    # §8.2 gives P6 two event types and supersession is neither; P1 publishes three
    # columns for it, one of which is the reason §8.2 asks to be retained.
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a", key=first,
                state="possible", cache_key="sha256:one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:two")
    before = p6_conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new, reason="pass two")
    after = p6_conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    assert after == before
    assert "append_event" not in _mentions("facts.supersede")


def test_preferred_appears_in_no_contradiction_margin_or_destination_path():
    # Done-means 29's third clause, and the SPEC's own negative: "`preferred` is a
    # pointer, not a strength. It never enters the §3.6 contradiction check, never
    # breaks a §3.7 margin tie, and never makes a fact destination-eligible."
    # Introspected, not read: each module's code is parsed and the column is looked
    # for by name.
    checked = 0
    for module_name, required in POINTER_FREE.items():
        if importlib.util.find_spec(module_name) is None:
            assert not required, module_name
            continue
        assert "preferred" not in _mentions(module_name), module_name
        checked += 1
    assert checked >= 2                       # the guard cannot pass by being empty


def test_the_pointer_has_exactly_one_home_in_facts():
    # `preferred` is set in the same call that links the two rows and NOWHERE else in
    # `facts`. Runtime introspection over every shipped module of the package, not a
    # text search of the tree.
    package = importlib.import_module("facts")
    home = "facts.supersede"
    writers = []
    for path in sorted(Path(package.__file__).parent.glob("*.py")):
        name = f"facts.{path.stem}" if path.stem != "__init__" else "facts"
        mentions = _mentions(name)
        if any("preferred = " in text or "preferred=" in text
               for text in mentions if isinstance(text, str)):
            writers.append(name)
    assert writers == [home], writers


def test_preferred_is_not_plan_versioned():
    # §8.8: facts are shared across plan versions, so the pointer is not addressable
    # per plan version. If it were, this module's three functions would have to say
    # WHICH plan version they meant.
    for function in (supersede_fact, preferred_fact, fact_history):
        names = set(inspect.signature(function).parameters)
        assert not [name for name in names if "plan" in name or "version" in name]
