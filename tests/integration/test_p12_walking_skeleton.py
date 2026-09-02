"""F4 -- Done-means 1, end to end, on real bytes and a real database.

*"The walking-skeleton line passes end to end: resolve node -> plan -> verify
preconditions -> create any missing directories -> move -> verify hash -> undo ->
verify restored."*

Everything is written out in one function on purpose. The unit suites each prove
one joint; this proves that the joints are connected, and a reader who wants to
know what P12 actually does to a person's file can read it here without
assembling a fixture chain in their head. Nothing is mocked: a real SQLite
database with P1's, P7's, P10's, P11's and P12's tables, a real directory tree,
real bytes, and P1's real hashes at all four verification points.
"""
from __future__ import annotations

import dataclasses
import itertools
import json
from datetime import timedelta
from pathlib import Path

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from eval_harness.store import create_eval_schema
from placement.fixtures import GOLDEN_DECISIONS
from placement.records import Destination, Subject
from placement.schema import create_placement_schema
from placement.vocabulary import PLACE
from privacy.classification_store import ClassificationRecord, ClassificationStore
from privacy.schema import create_privacy_schema
from tree_design.records import Node

from mutation import vocabulary as v
from mutation.constraints import FilesystemConstraints
from mutation.execute import apply_plan
from mutation.plan import build_plan, record_plan
from mutation.retention import (
    UndoRetention, activity, apply_report, current_undo_retention,
    set_undo_retention,
)
from mutation.schema import create_mutation_schema
from mutation.undo import entry_by_id, undo

#: The composition root's answers, stated here because this test IS a
#: composition root: the constraint table, the collision suffix, the clock, the
#: id minter, the retention period, and the sentence about an unconfirmed copy.
#: `src/mutation/` holds none of them (A7).
CONSTRAINTS = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=True, max_component_bytes=255,
    max_path_bytes=4096, prohibited_characters=frozenset(),
    reserved_names=frozenset(), replacement_character="_")

PROTECTED_CLASSES = frozenset({
    "sensitive_personal", "highly_sensitive_credential_bearing"})

DISPOSITION = ("The copy on the other drive was kept and is listed below; "
               "nothing was removed.")

RETENTION = UndoRetention(choice=v.RETENTION_NINETY_DAYS,
                          period=timedelta(days=90))


def _node(node_id, label, parent):
    return Node(
        node_id=node_id, plan_version_id="plan-1", node_type="proposed",
        display_label=label, parent_node_id=parent,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="walking skeleton", node_role="ordinary",
        accepts_placement=True, handling_class="personal_non_sensitive",
        origin_node_id=node_id)


NODES = (_node("n-course", "Coursework", None),
         _node("n-phys", "PHYS1401", "n-course"))
LEGAL = frozenset({"n-course", "n-phys"})


def _points(conn):
    return [json.loads(row[0])["point"] for row in conn.execute(
        "SELECT explanation FROM events WHERE event_type = 'hashing' "
        "ORDER BY event_id")]


def _types(conn):
    return [row[0] for row in conn.execute(
        "SELECT event_type FROM events ORDER BY event_id")]


def test_one_file_moves_end_to_end_and_is_reversible(conn, tmp_path):
    # --- the world: a real database and a real folder landscape -------------
    for create in (create_schema, create_eval_schema, create_privacy_schema,
                   create_placement_schema, create_mutation_schema):
        create(conn)

    documents = tmp_path / "Documents"
    inbox = documents / "Inbox"
    inbox.mkdir(parents=True)
    source = inbox / "Syllabus.pdf"
    source.write_bytes(b"PHYS1401 syllabus")

    ids = itertools.count()
    minutes = itertools.count()
    mint_id = lambda: f"id-{next(ids)}"                       # noqa: E731
    clock = lambda: f"2026-08-29T00:{next(minutes):02d}:00Z"  # noqa: E731

    # --- P1 knows the file, P7 has classified it ----------------------------
    stat = source.stat()
    file_id = record_file(
        conn, source, filename=source.name, normalized_filename="syllabus.pdf",
        extension=".pdf", observed_size=stat.st_size,
        observed_timestamps=str(stat.st_mtime), parent_folder_context="Inbox",
        mime_type="application/pdf", detected_format="pdf",
        scan_state="included", materialized=True)
    content_hash = conn.execute(
        "SELECT content_hash FROM files WHERE file_id = ?",
        (file_id,)).fetchone()[0]
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="personal_non_sensitive", protected=False,
        basis="user", evidence_refs=(), reliability_state="direct",
        observed_at="2026-08-29T00:00:00Z"))

    # --- the person states the one setting `66` §11 makes theirs ------------
    set_undo_retention(conn, RETENTION, user_id="user-1",
                       set_at="2026-08-29T00:00:00Z", record_id="retention-1")
    assert current_undo_retention(conn) == RETENTION

    # --- P11's decision: this file belongs at that node ---------------------
    decision = dataclasses.replace(
        next(item for item in GOLDEN_DECISIONS if item.outcome == PLACE),
        destination=Destination(node_id="n-phys", node_role="ordinary"),
        subject=Subject(kind="file", file_id=file_id,
                        content_hash=content_hash, group_id=None,
                        member_file_ids=()))

    # --- 1. resolve the node, and 2. build the plan -------------------------
    built = build_plan(
        conn, decision, nodes=NODES, legal_destination_ids=LEGAL,
        cross_folder_moves=True, constraints=CONSTRAINTS,
        high_level_folders={"root_documents": documents},
        volume_of=lambda path: "vol-main",
        protected_handling_classes=PROTECTED_CLASSES,
        protected_label_classes={},
        collision_policy=v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX,
        expiration_state="no expiry configured",
        now=lambda: "2026-08-29T00:00:00Z", mint_id=mint_id)
    assert built is not None
    plan, resolution = built
    record_plan(conn, plan, resolution, created_at="2026-08-29T00:00:00Z",
                component_version="p12-skeleton")

    # The tree is addressed by id and the path is P12's own composition; the
    # designed structure is not on disk yet.
    assert plan.requested_destination_node == "n-phys"
    assert plan.resolved_destination_path == str(
        documents / "Coursework" / "PHYS1401" / "Syllabus.pdf")
    assert not (documents / "Coursework").exists()

    # --- 3. preconditions, 4. directories, 5. move, 6. verify ---------------
    record = apply_plan(
        conn, plan, legal_destination_ids=LEGAL, source_root=tmp_path,
        destination_root=tmp_path, extra_protected=None,
        conflict_copies=lambda path: (), dataless_of=lambda path: False,
        approval_for=lambda plan_id: None, constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8, normalize_filename=lambda name: name,
        unverified_copy_disposition=DISPOSITION, scan_state="included",
        materialized=True, component_version="p12-skeleton", user_id="user-1",
        now=clock, mint_id=mint_id)

    assert record.result == v.APPLIED
    assert record.mode == v.ATOMIC_RENAME
    assert record.hash_after_completion == "match"
    assert record.directories_created_by_this_action == (
        str(documents / "Coursework"),
        str(documents / "Coursework" / "PHYS1401"))
    destination = Path(record.final_destination_path)
    assert destination.read_bytes() == b"PHYS1401 syllabus"
    assert not source.exists()
    assert get_file(conn, file_id)["current_path"] == str(destination)
    # V1 and V2 before the move, V3 after it. V4 is not asked, because nothing
    # crossed a volume -- that is a question never put, not a check skipped.
    assert _points(conn) == ["V1", "V2", "V3"]

    # The run says what it did, and the activity list says what the person can
    # still do about it.
    report = apply_report(conn, plan_ids=(plan.plan_id,))
    assert (report.applied, report.total, report.declines) == (1, 1, ())
    row = activity(conn, retention=RETENTION, at="2026-08-29T01:00:00Z")[0]
    assert row.source_path == str(source)
    assert row.destination_path == str(destination)
    assert row.status == v.APPLIED
    assert row.undo_available is True

    # --- 7. undo, and 8. verify restored ------------------------------------
    entry = entry_by_id(conn, conn.execute(
        "SELECT entry_id FROM move_journal WHERE plan_id = ? AND entry_kind = ?",
        (plan.plan_id, v.ENTRY_APPLIED)).fetchone()[0])
    verdict = undo(
        conn, entry.entry_id, constraints=CONSTRAINTS,
        unverified_copy_disposition=DISPOSITION,
        normalize_filename=lambda name: name, scan_state="included",
        materialized=True, component_version="p12-skeleton", user_id="user-1",
        now=clock, mint_id=mint_id)

    assert verdict.verdict == v.REVERSED
    assert source.read_bytes() == b"PHYS1401 syllabus", (
        "byte-identical content, back at the path it came from")
    assert not destination.exists()
    assert get_file(conn, file_id)["current_path"] == str(source)
    # The folders the move made are gone, and the folder the person made is not.
    assert not (documents / "Coursework").exists()
    assert inbox.exists() and documents.exists()
    assert verdict.directory_outcomes == (
        (str(documents / "Coursework" / "PHYS1401"), v.DIR_REMOVED),
        (str(documents / "Coursework"), v.DIR_REMOVED),
        (str(documents), v.DIR_RETAINED_NOT_CREATED))
    # The reversal ran the same discipline: three more hashes, in the same order.
    assert _points(conn) == ["V1", "V2", "V3", "V1", "V2", "V3"]

    # --- nothing was edited; everything was appended ------------------------
    assert _types(conn).count(v.PLANNED_MOVE) == 1
    assert _types(conn).count(v.EXECUTED_MOVE) == 1
    assert _types(conn).count(v.UNDO) == 1
    assert v.FAILED_MOVE not in _types(conn)
    assert v.REFUSED_MOVE not in _types(conn)
    entries = conn.execute(
        "SELECT entry_kind, reverses_entry_id FROM move_journal "
        "ORDER BY record_id").fetchall()
    assert [tuple(item) for item in entries] == [
        (v.ENTRY_APPLIED, None), (v.ENTRY_REVERSAL, entry.entry_id)]

    # And the person can see, afterwards, that it happened and was undone.
    row = activity(conn, retention=RETENTION, at="2026-08-29T02:00:00Z")[0]
    assert row.undo_available is False
    assert row.reversed_at is not None
