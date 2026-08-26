"""Task 12: two independent interpreter processes emit identical probe output."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from p8.determinism_probe import _dossier, _prompt, run_probe
from llm_harness.dossier import canonical_dossier_bytes, dossier_address

REPO = Path(__file__).resolve().parents[2]
PROBE = ["env", f"PYTHONPATH={REPO / 'src'}", sys.executable, str(REPO / "tests/p8/determinism_probe.py")]


def test_two_fresh_interpreters_emit_byte_identical_probe_output(tmp_path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    subprocess.run(PROBE, check=True, stdout=a.open("w"), cwd=REPO)
    subprocess.run(PROBE, check=True, stdout=b.open("w"), cwd=REPO)
    assert a.read_bytes() == b.read_bytes()


def test_probe_dossier_address_ignores_release_ids_and_changes_with_visible_bytes():
    import dataclasses

    payload = run_probe()
    dossier = _dossier()
    prompt = _prompt()
    assert payload["dossier_content_address"] == dossier_address(dossier, prompt)
    # A different release over the same content is the same dossier.
    other_release = dataclasses.replace(dossier, release_id="other-release")
    assert dossier_address(other_release, prompt) == payload["dossier_content_address"]
    # A different released value is a different dossier.
    changed = dataclasses.replace(
        dossier,
        released_evidence=(
            dataclasses.replace(dossier.released_evidence[0], value="Cornell"),
        ),
    )
    assert dossier_address(changed, prompt) != payload["dossier_content_address"]
    assert canonical_dossier_bytes(changed, prompt) != canonical_dossier_bytes(
        dossier, prompt
    )
