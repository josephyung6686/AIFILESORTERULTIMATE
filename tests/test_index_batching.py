"""The hot index reads and writes, batched, with the same rows as before.

A 2,000-file profile counted 680,699 `SELECT * FROM memberships WHERE
membership_id` calls, all from carrying one source group once per subject
file that had joined it. These tests pin the rows that carry produces and
the reads it no longer repeats. They do not use anyone's Downloads.
"""
from __future__ import annotations

from pathlib import Path

from cli import _draft_as_one
from database_agent.db import rebuildable_durability
from database_agent.files_table import get_file, record_file
from grouping.pipeline import GroupingResult
from grouping.records import (
    AnchorFact,
    Group,
    Membership,
    Support,
    TypedEdge,
)
from grouping.schema import create_grouping_schema
from grouping.store import (
    carry_memberships,
    edges_for_group,
    memberships_for_group,
    record_edges,
    record_group,
    record_membership,
)
from grouping.vocabulary import (
    CANDIDATE,
    CONTEXT_SUPPORTED,
    INCLUDED,
    LLM,
    RULES,
    SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
)
from questions.records import QuestionOption, StructuralAnswer, StructuralQuestion
from questions.schema import create_questions_schema
from questions.store import (
    activated_schemas, answered_options, record_answer, record_question,
)
from questions.vocabulary import CONFIRMED, STRUCTURAL
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

T0 = "2026-08-27T00:00:00Z"
KEY = "sha256:" + "c" * 64
CLOCK = "2026-08-29T12:00:00+00:00"


def _group(group_id: str) -> Group:
    return Group(
        group_id=group_id, seed_ref=f"seed-{group_id}",
        seed_kind=STRONGLY_IDENTIFIED_FILE, proposed_basis="subject=PHYS1401",
        anchor_facts=(AnchorFact(
            field="subject", value="PHYS1401", file_ids=("file-1",),
            reliability_state="validated", observation_key=KEY),),
        pre_model_signals={"anchor_count": 1}, anchor_count=1,
        coherence_verdict=None, coherence_citations=(), group_category=None,
        display_label=None, label_source=None, conflicts=(), stop_rule_hits=(),
        state=CANDIDATE, sensitivity_state="none", dossier_id=None,
        llm_response_ref=None, validation_verdict_ref=None, created_by=RULES,
        created_at=T0)


def _membership(membership_id: str, group_id: str, file_id: str) -> Membership:
    return Membership(
        membership_id=membership_id, group_id=group_id, file_id=file_id,
        content_hash=f"h-{file_id}", basis=CONTEXT_SUPPORTED,
        support=(Support(
            support_kind=SHARED_VALIDATED_FACT, observation_key=KEY,
            quote_or_field="subject", location="heading", edge_ref=None),),
        decision=INCLUDED, decision_source=LLM, insufficient_evidence=False,
        insufficiency_statement=None, conflicts=(), outlier_flag="none",
        validation_verdict_ref=None, created_at=T0)


def _result(group: Group, file_id: str) -> GroupingResult:
    return GroupingResult(
        subject_file_id=file_id, subject_content_hash=f"h-{file_id}",
        seeds=(), neighborhood=None, graph=None, stop_rule_outcome=None,
        group=group, memberships=(), dossier=None, model_result=None,
        not_implemented_reason=None)


def _ready(conn):
    from database_agent.db import create_schema

    create_schema(conn)
    create_grouping_schema(conn)
    return conn


def _statements(conn) -> list[str]:
    log: list[str] = []
    conn.set_trace_callback(lambda statement: log.append(" ".join(statement.split())))
    return log


def test_a_source_group_is_carried_once_however_many_files_joined_it(conn):
    """Two subject results for one group copy its members once, not twice.

    The merged group's members are the source members. A second result that
    names the same group does not ask for those rows again.
    """
    db = _ready(conn)
    course = _group("course")
    notes = _group("notes")
    record_group(db, course)
    record_group(db, notes)
    record_membership(db, _membership("m1", "course", "f1"))
    record_membership(db, _membership("m2", "course", "f2"))
    record_membership(db, _membership("m3", "notes", "f3"))
    log = _statements(db)
    merged_id = _draft_as_one(
        db,
        (_result(course, "f1"), _result(course, "f2"), _result(notes, "f3")),
        group_category="academic", label="Library", created_at=T0)
    merged_again = _draft_as_one(
        db,
        (_result(course, "f1"), _result(course, "f2"), _result(notes, "f3")),
        group_category="academic", label="Library", created_at=T0)
    assert merged_again == merged_id
    carried = memberships_for_group(db, merged_id)
    assert {item.file_id for item in carried} == {"f1", "f2", "f3"}
    assert len(carried) == 3
    lookups = [
        line for line in log
        if line.startswith("SELECT * FROM memberships WHERE membership_id")]
    # Three members, looked up on the first draft and again on the second.
    # Not five on the first (course carried twice) and five on the second.
    assert len(lookups) == 6


def test_new_carried_memberships_are_one_insert(conn):
    """Three new carried rows are one executemany, and they match one-by-one inserts."""
    db = _ready(conn)
    record_group(db, _group("course"))
    for index, file_id in enumerate(("f1", "f2", "f3"), start=1):
        record_membership(db, _membership(f"m{index}", "course", file_id))
    log = _statements(db)
    carried = carry_memberships(db, from_group_id="course", into_group_id="merged")
    assert {item.file_id for item in carried} == {"f1", "f2", "f3"}
    stored = memberships_for_group(db, "merged")
    assert [item.file_id for item in stored] == ["f1", "f2", "f3"]
    assert len(stored) == len(carried)
    inserts = [line for line in log if line.startswith("INSERT INTO memberships")]
    commits = [line for line in log if line.split()[0].upper() == "COMMIT"]
    # executemany still runs the statement once per row. The batch is the
    # single commit around those rows, where each used to commit alone.
    assert len(inserts) == 3
    assert len(commits) == 1
    again = carry_memberships(db, from_group_id="course", into_group_id="merged")
    assert len(again) == 3
    assert len(memberships_for_group(db, "merged")) == 3


def test_edges_are_looked_up_together_and_a_repeat_adds_no_event(conn):
    db = _ready(conn)
    edges = (
        TypedEdge(
            edge_id="e1", from_file_id="f1", to_file_id="f2",
            edge_type=SHARED_VALIDATED_FACT, evidence_ref=KEY, weight=None,
            bridge_entity_ref="subject=PHYS1401", hub_suppressed=False,
            created_at=T0),
        TypedEdge(
            edge_id="e2", from_file_id="f1", to_file_id="f3",
            edge_type=SHARED_VALIDATED_FACT, evidence_ref=KEY, weight=0.5,
            bridge_entity_ref="subject=PHYS1401", hub_suppressed=True,
            created_at=T0),
    )
    log = _statements(db)
    record_edges(db, "course", edges, created_at=T0)
    assert edges_for_group(db, "course") == edges
    selects = [
        line for line in log
        if line.upper().startswith("SELECT") and "group_edges" in line
        and "edge_id IN" in line]
    assert len(selects) == 1
    events = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    record_edges(db, "course", edges, created_at=T0)
    assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events
    assert edges_for_group(db, "course") == edges


def test_get_file_is_reread_after_a_write(conn, tmp_path: Path):
    from database_agent.db import create_schema

    create_schema(conn)
    path = tmp_path / "a.txt"
    path.write_text("hello")
    file_id = record_file(
        conn, path, filename="a.txt", normalized_filename="a.txt",
        extension=".txt", observed_size=path.stat().st_size,
        observed_timestamps="{}", parent_folder_context=str(tmp_path),
        mime_type=None, detected_format=None, scan_state="scanned",
        materialized=True)
    log = _statements(conn)
    assert get_file(conn, file_id)["scan_state"] == "scanned"
    assert get_file(conn, file_id)["filename"] == "a.txt"
    selects = [
        line for line in log
        if line.startswith("SELECT * FROM files WHERE file_id")]
    assert len(selects) == 1
    conn.execute(
        "UPDATE files SET scan_state = ? WHERE file_id = ?",
        ("superseded_content", file_id))
    assert get_file(conn, file_id)["scan_state"] == "superseded_content"


def test_a_settled_answer_is_read_once_until_the_person_answers_again(conn):
    create_questions_schema(conn)
    question = StructuralQuestion(
        question_id="relationship.organization:columbia",
        answer_class=STRUCTURAL,
        prompt="Which describes your relationship to Columbia?",
        evidence_context="We found files connected to Columbia.",
        unlocks="This helps distinguish coursework from professional material.",
        will_not_do="It will not create or move folders by itself.",
        scope="organization:columbia", handling_class="personal_non_sensitive",
        options=(
            QuestionOption("study", "I study there", activates_schema="academic"),
            QuestionOption("not_mine", "It is not about me"),
        ),
        evidence_refs=(KEY,))
    record_question(conn, question, asked_at=CLOCK)
    log = _statements(conn)
    assert answered_options(conn) == ()
    assert answered_options(conn) == ()
    assert activated_schemas(conn) == frozenset()
    scans = [
        line for line in log
        if line.startswith("SELECT * FROM structural_questions")]
    assert len(scans) == 1
    assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id="study", state=CONFIRMED,
        scope=question.scope, user_id="jy", recorded_at=CLOCK, inferred=False))
    assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2
    assert activated_schemas(conn) == frozenset({"academic"})


def test_rebuildable_writes_use_normal_and_the_connection_returns_to_full(conn):
    assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2
    with rebuildable_durability(conn):
        assert conn.execute("PRAGMA synchronous").fetchone()[0] == 1
    assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2


def test_an_error_inside_rebuildable_writes_restores_full(conn):
    try:
        with rebuildable_durability(conn):
            assert conn.execute("PRAGMA synchronous").fetchone()[0] == 1
            raise RuntimeError("stop")
    except RuntimeError:
        pass
    assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2


def test_a_scan_of_one_file_leaves_synchronous_full(conn, tmp_path: Path):
    from database_agent.db import create_schema

    create_schema(conn)
    create_scan_schema(conn)
    corpus = tmp_path / "folder"
    corpus.mkdir()
    (corpus / "note.txt").write_text("hello")
    log = _statements(conn)
    selection = record_selection(
        conn, sources=[corpus], candidate_roots=[],
        cross_folder_moves=False, selected_by=None)
    scan(conn, selection, source=FilesystemCorpusSource(),
         mime_type_for=lambda _path: None, scan_state="scanned",
         budget_exhausted=lambda: False)
    assert any("PRAGMA synchronous = NORMAL" in line for line in log)
    assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM files").fetchone()[0] == 1
