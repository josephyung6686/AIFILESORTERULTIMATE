# tests/p5/test_p5_safety.py
"""11-ops-runtime.md §4b and §5 — the two ratified rules, and the fact that P5 has
no path around either of them."""
from pathlib import Path

import pytest

from extractors.safety import (
    UNTOUCHED_PROTECTED, DatalessRefused, ProtectedContainerRefused, SafetyPolicy,
    admit,
)

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)


def test_an_ordinary_path_is_admitted():
    assert admit(Path("/corpus/Syllabus.pdf"), policy=OPEN_POLICY) is None


def test_a_path_inside_a_protected_container_is_refused():
    # 11 §4b: "P3 does not descend into one... P12 never moves one, and no policy,
    # approval, or user gesture makes it movable."
    policy = SafetyPolicy(
        is_protected_container=lambda path: "Preview.app" in str(path),
        is_dataless=lambda path: False,
    )
    with pytest.raises(ProtectedContainerRefused):
        admit(Path("/Applications/Preview.app/Contents/Resources/help.pdf"),
              policy=policy)


def test_the_label_is_p3s_word_and_p5_coins_no_second_one():
    # P3's SPEC: "The label is `untouched_protected`, and it is a statement about the
    # product's restraint, not about the file."
    assert UNTOUCHED_PROTECTED == "untouched_protected"


def test_there_is_no_override_argument_anywhere_in_the_signature():
    # 11 §4b: "no policy, approval, or user gesture makes it movable - this is not a
    # default that review can override." A keyword that could turn the rule off would
    # be that override, so there is none to pass.
    import inspect
    parameters = set(inspect.signature(admit).parameters)
    assert parameters == {"path", "policy"}
    for forbidden in ("force", "override", "allow_protected", "approved", "consent"):
        assert forbidden not in parameters
    policy_fields = set(SafetyPolicy.__dataclass_fields__)
    assert policy_fields == {"is_protected_container", "is_dataless"}


def test_a_dataless_file_is_refused_before_anything_reads_it():
    # 11 §5: "Do not materialize, hash, or extract."
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        admit(Path("/corpus/Thesis.pdf"), policy=policy)


def test_the_protected_check_runs_before_the_dataless_check():
    # Inside a protected container P5 must not even ask a question about the file:
    # asking is a stat of its contents, which 11 §4b forbids.
    asked = []

    def is_dataless(path):
        asked.append(path)
        return False

    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=is_dataless)
    with pytest.raises(ProtectedContainerRefused):
        admit(Path("/Applications/Thing.app/x.pdf"), policy=policy)
    assert asked == []


def test_the_gate_opens_nothing_and_stats_nothing():
    # Detection is a filesystem observation made by P3 (11 §5); P5 consumes the
    # verdict. A second derivation would drift (O5), so there is nothing here to
    # drift from: this module reads no bytes and no stat result.
    import extractors.safety as module
    source = Path(module.__file__).read_text()
    for forbidden in ("open(", "read_bytes", "os.stat", "st_flags", "hash_file",
                      "SF_DATALESS"):
        assert forbidden not in source, forbidden


def test_a_refusal_writes_no_extraction_run(sink):
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        admit(Path("/corpus/Thesis.pdf"), policy=policy)
    # The GATE writes nothing, and that is still right: it raises, and a gate that
    # also wrote would be doing two jobs. P4 OQ6 closed on 2026-08-20 with a ninth
    # `completeness` value, `dataless`, so the refusal is now NAMEABLE -- but the row
    # is written by whoever CATCHES DatalessRefused (the router, Task 4), not here.
    # Until that caller exists, a dataless file is still absent from §8.6's count
    # line; what changed is that the vocabulary can now say why, instead of the file
    # being filed under a word that lies about it.
    assert sink.runs == []
