"""Task 12: two independent interpreter processes emit identical probe output."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from p8.determinism_probe import _dossier, _prompt, run_probe
from llm_harness.dossier import canonical_dossier_bytes, dossier_address
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

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
    assert payload["dossier_content_address"] == dossier_address(dossier, prompt, handle_key=FIXTURE_HANDLE_KEY)
    # A different release over the same content is the same dossier.
    other_release = dataclasses.replace(dossier, release_id="other-release")
    assert dossier_address(other_release, prompt, handle_key=FIXTURE_HANDLE_KEY) == payload["dossier_content_address"]
    # A different released value is a different dossier.
    changed = dataclasses.replace(
        dossier,
        released_evidence=(
            dataclasses.replace(dossier.released_evidence[0], value="Cornell"),
        ),
    )
    assert dossier_address(changed, prompt, handle_key=FIXTURE_HANDLE_KEY) != payload["dossier_content_address"]
    assert canonical_dossier_bytes(changed, prompt, handle_key=FIXTURE_HANDLE_KEY) != canonical_dossier_bytes(
        dossier, prompt, handle_key=FIXTURE_HANDLE_KEY
    )


def test_the_probe_walks_replay_the_dispatcher_and_a_real_p2_row():
    """R5: the probe must exercise the path the product takes, not a shortcut."""
    import ast
    from pathlib import Path

    payload = run_probe()
    assert payload["p2_stage_outcome"] == "produced"
    assert payload["p2_budget_state"] == "within_ceiling"
    # The P2 payload is read back from the row, so it carries P8's opaque fields.
    assert "validator_version" in payload["p2_payload"]
    assert payload["grounding_report"]["citations_span_matched"] == 1

    source = Path(__file__).resolve().parent / "determinism_probe.py"
    tree = ast.parse(source.read_text())
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "validate_response" not in called, "the probe must go through replay"
    assert "replay_recorded_response" in called
    assert "emit_stage_output" in called
    assert not [
        node for node in ast.walk(tree)
        if isinstance(node, ast.keyword) and node.arg == "site_validator"
    ]
