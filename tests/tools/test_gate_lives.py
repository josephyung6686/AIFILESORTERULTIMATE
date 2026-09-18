# tests/tools/test_gate_lives.py
"""`tools/gate_lives.py` resolves a situation fact's value the way the
partition does -- the situation's row, else the KIND's word -- so the gate
counts the files the tree counts. The gate's first draft counted lives only
and passed the owner's corpus with ONE life while 218 of 257 files reached
none; `measure` now reports both numbers and `main` asserts the second.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from collections import Counter  # noqa: E402

from production import load_shipped_catalogue, read_packaged_library_file  # noqa: E402
from tools.gate_lives import failures_of, life_of_value  # noqa: E402


def test_a_kind_fact_reaches_the_kinds_life_and_a_situation_fact_its_rows():
    catalogue = load_shipped_catalogue(read_packaged_library_file)

    assert life_of_value(catalogue, "academic") == "Education"
    assert life_of_value(catalogue, "research") == "Education"
    assert life_of_value(catalogue, "medical") == "Health"
    assert life_of_value(catalogue, "academic.coursework") == "Education"
    assert life_of_value(catalogue, "academic.teaching") == "Teaching"
    assert life_of_value(catalogue, "nonprofit") == "Personal"
    assert life_of_value(catalogue, "no.such.situation") is None
    assert life_of_value(catalogue, "") is None


# --- the verdict itself (`00` amendment 18: BOTH numbers) ----------------------


def _run(*, files=257, with_fact=257, reached=257, lives, life_roots,
         decided=257):
    """`measure`'s dict on hand-built numbers; `lives` is life -> files."""
    lives = Counter(lives)
    return {"files": files, "with_fact": with_fact, "reached": reached,
            "unmapped": Counter({"academic": with_fact - reached}),
            "lives": lives, "roots": list(life_roots),
            "life_roots": list(life_roots), "shipped_lives": set(lives),
            "decided": decided}


def test_one_life_with_most_files_in_none_is_a_failure_and_not_a_narrow_pass():
    """THE CASE THE FIRST DRAFT PASSED. On the owner's corpus the per-situation
    mapping emitted ONE life (`Personal`, 39 files) and 218 of 257 files
    reached none; "fewer than sixteen" was true and the run had failed.
    SABOTAGE: assert the life count only. This passes again."""
    failures = failures_of(_run(reached=39, lives={"Personal": 39},
                                life_roots=["Personal"]))
    assert any("218 of 257" in f and "NO life" in f for f in failures), failures


def test_every_file_in_a_life_and_a_few_roots_passes():
    failures = failures_of(_run(
        lives={"Education": 155, "Photos and Media": 27, "Career": 22,
               "Health": 4, "Creative and Hobbies": 3},
        life_roots=["Education", "Photos and Media", "Career", "Health",
                    "Creative and Hobbies"], reached=211, with_fact=211))
    assert failures == []


def test_no_life_root_and_the_sixteen_folder_skeleton_both_fail():
    reached = _run(lives={"Education": 257}, life_roots=[])
    assert any("no life root" in f for f in failures_of(reached))
    sixteen = [f"Life {n}" for n in range(16)]
    skeleton = _run(lives={life: 1 for life in sixteen}, life_roots=sixteen,
                    reached=16, with_fact=16)
    assert any("sixteen" in f for f in failures_of(skeleton))


def test_a_root_no_file_reached_and_an_undecided_file_both_fail():
    empty_root = _run(lives={"Education": 257},
                      life_roots=["Education", "Vehicles"])
    assert any("no file's situation supports" in f for f in failures_of(empty_root))
    undecided = _run(lives={"Education": 257}, life_roots=["Education"],
                     decided=256)
    assert any("no placement decision" in f for f in failures_of(undecided))
