"""The walking skeleton's P1 step (02-segmentation-map.md):
hash, create the file record, append a discovery event — and P12's step reaches
P1's V1-V4 and gets true answers.

This test stays in the repository as the integration test every later part must
keep green. It is deterministic: no model, no cloud, no embeddings.
"""
from datetime import datetime, timezone
from pathlib import Path

from conftest import p3_basic_record
from database_agent.db import create_schema
from database_agent.events import append_event
from database_agent.files_table import get_file, observe_path
from database_agent.identity import hash_file
from database_agent.verify import VerificationPoint, verify_content


def test_skeleton_p1_step(conn, tmp_path: Path):
    create_schema(conn)

    # One PDF whose title carries a course code (the skeleton's input file).
    document = tmp_path / "corpus" / "syllabus-fixture.pdf"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_bytes(b"%PDF-1.4 fixture bytes")

    # P3's fixture hands P1 the §1.2 fields and authors the scan events (M8).
    # P1 hashes, creates the file record, and writes. It authors nothing.
    file_id = observe_path(
        conn, document, author="P3", component_version="p3-fixture",
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
        # P3 computes the R2 record once (O5); P1 stores it and derives none of it.
        **p3_basic_record(document),
    )
    append_event(
        conn, event_type="discovery", file_id=file_id,
        content_hash=hash_file(document, materialized=True), new_path=str(document),
        subsystem="P3", component_version="p3-fixture",
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation="skeleton fixture stands in for P3",
    )

    row = get_file(conn, file_id)
    assert row["content_hash"] == hash_file(document, materialized=True)
    assert row["hash_algorithm"]
    assert row["volume_id"]

    discovery = conn.execute(
        "SELECT * FROM events WHERE event_type = 'discovery' AND file_id = ?", (file_id,)
    ).fetchone()
    assert discovery is not None
    assert discovery["subsystem"] == "P3"

    # Nothing in the scan half of the skeleton is authored by P1 (Contract in, M8).
    scan_authors = conn.execute(
        "SELECT DISTINCT subsystem FROM events WHERE event_type IN "
        "('discovery', 'stat observation', 'hashing')"
    ).fetchall()
    assert [r["subsystem"] for r in scan_authors] == ["P3"]

    # P12's step reaches V1-V4 and gets true answers. Here the `hashing` event is
    # authored by P12 and performed by P1 — the one place `subsystem` is P1.
    for point in (VerificationPoint.V1, VerificationPoint.V2, VerificationPoint.V3):
        assert verify_content(conn, file_id, row["content_hash"], point=point,
                              author="P12", component_version="p12-fixture",
                              materialized=True) == "match"
    performed = conn.execute(
        "SELECT subsystem FROM events WHERE event_type = 'hashing' ORDER BY event_id DESC"
    ).fetchone()
    assert performed["subsystem"] == "P1"
