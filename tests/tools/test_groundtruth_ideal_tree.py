# tests/tools/test_groundtruth_ideal_tree.py  (drafted in the scratchpad; offered to the lead)
"""`tools/groundtruth/ideal_tree.py`: the tree the key describes, built from rules.

Synthetic key, synthetic paths, synthetic database. Nothing of the owner's.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

#: THIS checkout, derived from the file's own location rather than spelled.
#: A path naming one machine's home directory makes the test unrunnable on
#: every other machine, and under a worktree it silently imports the WRONG
#: tree -- the one the author happened to have, not the one under test.
ROOT = Path(__file__).resolve().parents[2]
for p in (str(ROOT), str(ROOT / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from database_agent.db import create_schema, open_database
from database_agent.files_table import get_file, record_file
from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields
from facts.file_facts import RULE, write_fact
from facts.states import LLM_SUPPORTED, POSSIBLE, VALIDATED
from facts.values import VALUE_ORIGINS, ensure_value
from production import load_shipped_catalogue, read_packaged_library_file
from tools.groundtruth import ideal_tree as it
from tools.groundtruth.labels import load_labels

COURSEWORK = "academic.coursework"          # school(G) / term / subject / work_type
CAMERA = "photos.camera-events"             # capture_year / event
CITED = "sha256:" + "0" * 64
LIFE = {COURSEWORK: "Education", CAMERA: "Photos and Media"}.get


@pytest.fixture()
def conn(tmp_path):
    c = open_database(tmp_path / "agent.sqlite")
    yield c
    c.close()


def _catalogue():
    return load_shipped_catalogue(read_packaged_library_file)


def _row(path, situation=COURSEWORK, fields=None, **over):
    row = {"path": path, "group": "g", "situation": situation,
           "destination": None, "expected_fields": fields or {}}
    row.update(over)
    return row


def _key(tmp_path, rows, aliases=None):
    doc = {"files": rows}
    if aliases:
        doc["aliases"] = aliases
    path = tmp_path / "key.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return load_labels(path, known_situations=it.known_situations(_catalogue()))


def _built(tmp_path, rows, life_of=LIFE, aliases=None):
    files = it.ideal_files(_key(tmp_path, rows, aliases), _catalogue(), life_of)
    return files, it.build(files)


# --- resolving the key against the library ---------------------------------

def test_a_coursework_row_gets_the_librarys_four_levels_in_its_order(tmp_path):
    files, _ = _built(tmp_path, [_row("a.pdf", fields={"subject": "PHYS1", "work_type": "hw"})])
    (f,) = files
    assert f.levels == ("school", "term", "subject", "work_type")
    assert f.values == (None, None, "PHYS1", "hw")
    assert f.unfilled == ("school", "term")
    assert f.group_level == ("school",)
    assert f.life == "Education"


def test_without_a_life_reader_the_root_is_the_marker_not_a_folder(tmp_path):
    """`life_of` does not exist at HEAD. SABOTAGE: default a life -- then a root the
    library never named is graded as if the owner had."""
    files, built = _built(tmp_path, [_row("a.pdf", fields={"subject": "X"})], life_of=None)
    assert files[0].life is None
    assert built.chains["a.pdf"][0] == it.NO_LIFE


def test_protected_uncertain_and_unresolvable_rows_are_bucketed_not_pathed(tmp_path):
    files, built = _built(tmp_path, [
        _row("p.pdf", protected=True),
        _row("u.pdf", uncertain="two courses cite it"),
    ])
    by = {f.path: f for f in files}
    assert by["p.pdf"].bucket == it.PROTECTED and "p.pdf" not in built.chains
    assert by["u.pdf"].bucket == it.UNCERTAIN
    assert built.chains["u.pdf"] == (it.REVIEW_ROOT,)


# --- the depth rules --------------------------------------------------------

def test_a_level_with_one_value_is_not_built(tmp_path):
    """`materialise.py:95`: one course across the branch is a folder you open to
    find one folder."""
    _, built = _built(tmp_path, [
        _row("a.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("b.pdf", fields={"subject": "PHYS1", "work_type": "exam"}),
    ])
    assert built.chains == {"a.pdf": ("Education", "hw"), "b.pdf": ("Education", "exam")}
    assert {(f.rule, f.field) for f in built.folds} >= {
        (it.DOES_NOT_DIVIDE, "school"), (it.DOES_NOT_DIVIDE, "term"),
        (it.DOES_NOT_DIVIDE, "subject")}


def test_a_single_child_run_with_nothing_beneath_folds_into_its_top(tmp_path):
    """`106` Phase 7 §B.2. Under PHYS1 every file is homework: no `hw` folder.
    Under MATH2 two kinds divide two-and-one: both kept."""
    _, built = _built(tmp_path, [
        _row("a.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("b.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("c.pdf", fields={"subject": "MATH2", "work_type": "hw"}),
        _row("c2.pdf", fields={"subject": "MATH2", "work_type": "hw"}),
        _row("d.pdf", fields={"subject": "MATH2", "work_type": "exam"}),
    ])
    assert built.chains["a.pdf"] == built.chains["b.pdf"] == ("Education", "PHYS1")
    assert built.chains["c.pdf"] == built.chains["c2.pdf"] == ("Education", "MATH2", "hw")
    assert built.chains["d.pdf"] == ("Education", "MATH2", "exam")
    assert ("Education", "PHYS1", "hw") not in built.nodes
    assert [f for f in built.folds if f.rule == it.SINGLE_RUN] == [
        it.Fold(it.SINGLE_RUN, "work_type", 4, False)]


def test_a_folder_per_file_is_not_built_beneath_a_built_node_but_is_kept_at_the_root(tmp_path):
    """`106` Phase 7 §B.1 and §A's last paragraph."""
    _, built = _built(tmp_path, [
        _row("a.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("b.pdf", fields={"subject": "PHYS1", "work_type": "exam"}),
        _row("c.pdf", fields={"subject": "PHYS1", "work_type": "notes"}),
        _row("d.pdf", fields={"subject": "MATH2", "work_type": "hw"}),
    ])
    # Beneath PHYS1 three files would be three folders: not built.
    assert {built.chains[p] for p in ("a.pdf", "b.pdf", "c.pdf")} == {("Education", "PHYS1")}
    # At the root two subjects, one of them a single file: kept.
    assert built.chains["d.pdf"] == ("Education", "MATH2")
    assert it.Fold(it.FOLDER_PER_FILE, "work_type", 4, False) in built.folds


def test_a_blank_at_a_built_level_blocks_and_at_an_unbuilt_level_does_not(tmp_path):
    files, built = _built(tmp_path, [
        _row("a.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("b.pdf", fields={"subject": "MATH2", "work_type": "exam"}),
        _row("c.pdf", fields={"work_type": "hw"}),          # subject blank, built
    ])
    assert built.chains["c.pdf"] == ("Education",)
    assert built.blocking["c.pdf"] == ("subject",)
    # school and term are blank on every row: unbuilt, owed, not blocking.
    assert built.blocking["a.pdf"] == ()
    assert {f.path: f.unfilled for f in files}["a.pdf"] == ("school", "term")
    provisional = {(f.field, f.provisional) for f in built.folds if f.rule == it.DOES_NOT_DIVIDE}
    assert provisional == {("school", True), ("term", True)}


def test_a_deliberate_none_rests_the_file_at_the_parent_and_is_not_owed(tmp_path):
    files, built = _built(tmp_path, [
        _row("a.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("b.pdf", fields={"subject": "PHYS1", "work_type": "exam"}),
        _row("c.pdf", fields={"subject": "PHYS1", "work_type": ""}),
    ])
    assert built.chains["c.pdf"] == ("Education",)
    assert built.blocking["c.pdf"] == ()
    assert "work_type" not in {f.path: f.unfilled for f in files}["c.pdf"]


def test_two_situations_under_one_life_are_two_branches_under_one_root(tmp_path):
    _, built = _built(tmp_path, [
        _row("a.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("b.pdf", fields={"subject": "MATH2", "work_type": "hw"}),
        _row("x.jpg", CAMERA, fields={"capture_year": "2024"}),
        _row("y.jpg", CAMERA, fields={"capture_year": "2025"}),
    ], life_of=lambda s: "Education")
    assert {n[0] for n in built.nodes} == {"Education"}
    assert built.chains["x.jpg"] == ("Education", "2024")
    assert built.chains["a.pdf"] == ("Education", "PHYS1")


# --- comparing --------------------------------------------------------------

def test_compare_counts_exact_prefixes_and_a_transparent_general():
    ideal = {"a": ("Education", "PHYS1", "hw"), "b": ("Education", "MATH2"),
             "c": ("Education", "MATH2"), "d": ("Education", "X")}
    actual = {"a": ("Education", "PHYS 1", "hw"), "b": ("Education", "MATH2", "General"),
              "c": ("academic", "MATH2"), "d": ("Photos",)}
    c = it.compare(ideal, actual)
    assert (c.gradeable, c.exact, c.not_placed) == (4, 2, 0)
    # c's root disagrees (a schema id where a life should be) but its course agrees:
    # invisible from the root, visible below it -- which is the point of two vectors.
    assert c.prefix_from_root == (2, 2, 1)
    assert c.prefix_below_root == (3, 1)


def test_compare_accepts_the_keys_own_alias_for_a_value():
    c = it.compare({"a": ("Education", "PYTHON1006")}, {"a": ("Education", "ENGI E1006")},
                   {"a": {"python1006": ("ENGI E1006",)}})
    assert c.exact == 1


# --- the database -----------------------------------------------------------

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
                      cache_key=f"test:{file_id}:{field_key}:{value}", active=True)


def test_reach_reads_agreement_disagreement_and_fills_off_the_database(conn, tmp_path):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    a, ha = _file(conn, tmp_path, "a.pdf")
    b, hb = _file(conn, tmp_path, "b.pdf")
    c, hc = _file(conn, tmp_path, "c.pdf")
    _fact(conn, a, ha, "subject", "PHYS1", VALIDATED)       # agrees
    _fact(conn, b, hb, "subject", "CHEM9", VALIDATED)       # disagrees
    _fact(conn, c, hc, "subject", "MATH2", LLM_SUPPORTED)   # key blank: db fills it
    _fact(conn, a, ha, "work_type", "hw", POSSIBLE)         # below the proposal bar
    conn.commit()
    conn.close()
    files, _ = _built(tmp_path, [
        _row("a.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("b.pdf", fields={"subject": "MATH2"}),
        _row("c.pdf", fields={"work_type": "exam"}),
    ])
    reach, actual, joined, protected_placed = it.read_database(
        tmp_path / "agent.sqlite", tmp_path, files)
    assert (joined, protected_placed) == (3, 0)
    s = reach["subject"]
    assert (s.rows, s.key_filled, s.key_blank, s.db_filled) == (3, 2, 1, 3)
    assert (s.agree, s.disagree, s.db_fills_blank) == (1, 1, 1)
    assert reach["work_type"].db_filled == 0
    assert reach["school"].group_level is True
    assert actual == {}                       # no tree, no placement: nothing to compare


# --- the report prints no path ------------------------------------------------

def test_main_prints_counts_and_never_a_path(tmp_path, capsys):
    key = tmp_path / "key.json"
    key.write_text(json.dumps({"files": [
        _row("secret-folder/very-private-name.pdf", fields={"subject": "PHYS1", "work_type": "hw"}),
        _row("secret-folder/other-private-name.pdf", fields={"subject": "MATH2", "work_type": "hw"}),
        _row("secret-folder/protected-name.pdf", protected=True),
    ]}), encoding="utf-8")
    out = tmp_path / "rows.json"
    assert it.main(["--labels", str(key), "--out", str(out)]) == 0
    text = capsys.readouterr().out
    assert "private-name" not in text and "secret-folder" not in text
    assert "IDEAL TREE  key rows 3" in text
    assert "placed 2  protected 1" in text
    assert "OWED" in text and "REACH" not in text
    rows = json.loads(out.read_text())
    assert {r["bucket"] for r in rows} == {it.PLACED, it.PROTECTED}


def test_a_refused_key_is_reported_by_its_rule_and_not_its_path(tmp_path, capsys):
    key = tmp_path / "key.json"
    key.write_text(json.dumps({"files": [
        _row("secret-folder/private-name.pdf", situation="not.a.situation")]}), encoding="utf-8")
    assert it.main(["--labels", str(key)]) == 2
    err = capsys.readouterr().err
    assert "refused by the loader" in err and "private-name" not in err


def _tree(conn, version, rows):
    """`rows`: (node_id, label, parent). Two versions may share a node_id."""
    conn.execute("insert into plan_versions (plan_version_id, predecessor_id, state, created_at, "
                 "cross_folder_moves, selection_id) values (?, null, 'frozen', ?, 0, 's')",
                 (version, version))
    for node_id, label, parent in rows:
        conn.execute(
            "insert into tree_nodes (node_id, plan_version_id, origin_node_id, node_type, "
            "display_label, parent_node_id, root_anchor, ordinal, associated_group_ids, "
            "explanation, node_role, accepts_placement, handling_class) values "
            "(?, ?, ?, 'proposed', ?, ?, 'r', 0, '[]', 'why', 'ordinary', 1, 'public_low')",
            (node_id, version, node_id, label, parent))


def _place(conn, version, file_id, content_hash, node_id, when):
    conn.execute(
        "insert into placement_decisions (record_id, subject_ref, plan_version, origin_stage, "
        "outcome, node_id, created_at, payload) values (?, ?, ?, 'direct', 'place', ?, ?, '{}')",
        (f"{version}:{file_id}", f"file:{file_id}:{content_hash}", version, node_id, when))


def test_the_products_chain_is_walked_inside_the_decisions_own_plan_version(conn, tmp_path):
    """A sort database holds many plan versions and `tree_nodes` is keyed
    `(plan_version_id, node_id)`. SABOTAGE: key the walk on `node_id` alone -- the
    later version's label wins for every version, and a chain crosses trees."""
    from placement.schema import create_placement_schema
    from tree_design.schema import create_tree_schema
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    create_tree_schema(conn)
    create_placement_schema(conn)
    a, ha = _file(conn, tmp_path, "a.pdf")
    p, hp = _file(conn, tmp_path, "p.pdf")
    _tree(conn, "v1", [("n1", "academic", None), ("n2", "PHYS1", "n1")])
    _tree(conn, "v2", [("n1", "Education", None), ("n2", "MATH2", "n1")])
    _place(conn, "v1", a, ha, "n2", "2026-09-18T00:00:00")
    _place(conn, "v2", p, hp, "n2", "2026-09-18T00:00:01")   # a protected file, placed
    conn.commit()
    conn.close()
    files, built = _built(tmp_path, [
        _row("a.pdf", fields={"subject": "PHYS1"}),
        _row("b.pdf", fields={"subject": "MATH2"}),
        _row("p.pdf", protected=True),
    ])
    reach, actual, joined, protected_placed = it.read_database(
        tmp_path / "agent.sqlite", tmp_path, files)
    assert actual == {"a.pdf": ("academic", "PHYS1")}
    assert protected_placed == 1
    c = it.compare(built.chains, actual)
    assert (c.gradeable, c.exact, c.not_placed) == (2, 0, 1)
    assert c.prefix_from_root == (0, 0) and c.prefix_below_root == (1,)
