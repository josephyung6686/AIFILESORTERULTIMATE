"""Task 12: two independent interpreter processes emit identical probe output."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from p8.determinism_probe import RELEASED, SCHEMA, VOCABULARY, run_probe
from llm_harness.fingerprint import dossier_content_address

REPO = Path(__file__).resolve().parents[2]
PROBE = ["env", f"PYTHONPATH={REPO / 'src'}", sys.executable, str(REPO / "tests/p8/determinism_probe.py")]


def test_two_fresh_interpreters_emit_byte_identical_probe_output(tmp_path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    subprocess.run(PROBE, check=True, stdout=a.open("w"), cwd=REPO)
    subprocess.run(PROBE, check=True, stdout=b.open("w"), cwd=REPO)
    assert a.read_bytes() == b.read_bytes()


def test_probe_dossier_address_ignores_release_ids_and_changes_with_visible_bytes():
    payload = run_probe()
    address = payload["dossier_content_address"]
    assert address == dossier_content_address(
        RELEASED,
        allowed_vocabulary=VOCABULARY,
        allowed_schema_bytes=SCHEMA,
        evidence_snapshot_id="other-snap",
        release_id="other-release",
        audit_id=0,
    )
    assert address != dossier_content_address(
        RELEASED + b"x",
        allowed_vocabulary=VOCABULARY,
        allowed_schema_bytes=SCHEMA,
    )
