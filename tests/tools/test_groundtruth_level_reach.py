# tests/tools/test_groundtruth_level_reach.py
"""`106` Phase 6's gate: a file has a level to nest under, or it does not.

WHAT THIS MEASURES. Not placement and not fact count. A file reaches a level when it
carries, at a state a folder proposal may rest on (`PROPOSAL_ELIGIBLE_STATES`), a fact
on a `destination_eligible` field that its OWN situation builds a folder from
(`production.folder_levels_for`). `file_type` on 249 files reaches nothing, because no
situation those files are in has a `file_type` level. A file with no situation fact is
in the denominator: a file the judge never placed is a file this phase did not help.
"""
from __future__ import annotations

import json
from pathlib import Path

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields
from facts.file_facts import RULE, write_fact
from facts.llm_seam import SITUATION_FIELD
from facts.states import LLM_SUPPORTED, POSSIBLE, VALIDATED
from facts.values import VALUE_ORIGINS, ensure_value
from production import load_shipped_catalogue, read_packaged_library_file
from tools.groundtruth.level_reach import level_reach

COURSEWORK = "academic.coursework"
CAMERA = "photos.camera-events"

#: `write_fact` refuses a non-`user_confirmed` fact with no citation and checks the
#: SHAPE of the key (`file_facts._checked_refs`: `sha256:` + 64 hex), never that it
#: resolves. The gate reads states and fields and walks no evidence, so a well-formed
#: key that points at nothing is the honest fixture here.
CITED = "sha256:" + "0" * 64


def _file(conn, tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"bytes")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=5,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, file_id, content_hash, field_key, value, state):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=CITED, origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=RULE, evidence_refs=(CITED,),
                      cache_key=f"test:{file_id}:{field_key}", active=True)


def _store(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return load_shipped_catalogue(read_packaged_library_file)


def test_a_coursework_file_with_a_subject_reaches_a_level(conn, tmp_path):
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, COURSEWORK, LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "subject", "PHYS1401", VALIDATED)
    reach = level_reach(conn, catalogue)
    assert (reach.files, reach.with_situation, reach.reached) == (1, 1, 1)
    assert reach.by_field == {"subject": 1}


def test_a_file_type_fact_reaches_nothing(conn, tmp_path):
    """The 249. SABOTAGE: count every destination-eligible fact, or every fact at
    all -- then `file_type` on a coursework file scores as a level and the gate reads
    as already met on a tree that is flat."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, COURSEWORK, LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "file_type", "pdf", VALIDATED)
    reach = level_reach(conn, catalogue)
    assert (reach.files, reach.with_situation, reach.reached) == (1, 1, 0)


def test_a_possible_fact_reaches_nothing(conn, tmp_path):
    """`PROPOSAL_ELIGIBLE_STATES` excludes `possible`; a proposal the person has not
    answered is not a level. SABOTAGE: drop the state filter."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, COURSEWORK, LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "subject", "PHYS1401", POSSIBLE)
    assert level_reach(conn, catalogue).reached == 0


def test_a_file_with_no_situation_is_in_the_denominator(conn, tmp_path):
    """SABOTAGE: `if situation is None: continue` -- then a run whose judge placed
    nobody scores 0 of 0 and prints as perfect. `00`:259 one stage earlier."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "IMG_1.jpg")
    _fact(conn, file_id, content_hash, "capture_year", "2024", VALIDATED)
    reach = level_reach(conn, catalogue)
    assert (reach.files, reach.with_situation, reach.reached) == (1, 0, 0)


def test_a_situation_that_is_only_a_schema_id_is_unresolvable_not_reached(conn, tmp_path):
    """Before Phase 2(b) the `situation` fact holds `academic`; `folder_levels_for`
    refuses it and so must this. Counted, named, never guessed at."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, "academic", LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "subject", "PHYS1401", VALIDATED)
    reach = level_reach(conn, catalogue)
    assert (reach.with_situation, reach.unresolvable, reach.reached) == (1, 1, 0)


def test_a_level_of_another_situation_does_not_count(conn, tmp_path):
    """`capture_year` is photos' level and not coursework's. SABOTAGE: test
    destination eligibility alone -- then any eligible fact anywhere reaches."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, COURSEWORK, LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "capture_year", "2024", VALIDATED)
    assert level_reach(conn, catalogue).reached == 0
    photo, photo_hash = _file(conn, tmp_path, "IMG_2.jpg")
    _fact(conn, photo, photo_hash, SITUATION_FIELD, CAMERA, LLM_SUPPORTED)
    _fact(conn, photo, photo_hash, "capture_year", "2024", VALIDATED)
    assert level_reach(conn, catalogue).reached == 1
