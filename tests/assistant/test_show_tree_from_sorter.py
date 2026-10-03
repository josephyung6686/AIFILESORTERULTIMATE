"""The assistant reads the sorter's tree from the database; it does not build its own.

A real sorter run (`cli.main`, no model) writes `plan_versions`, `tree_nodes` and
`placement_decisions` for a small synthetic corpus. `show_tree` and the quick sort
(`propose_tree` over the files the person names) must report exactly what those
rows say, withhold the paths of held files, and point at `database-agent` when no
tree exists yet.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "integration"))

import cli  # noqa: E402
from assistant import organize_tools as ot  # noqa: E402
from assistant.registry import deferred_schemas_for  # noqa: E402
from database_agent.db import open_database  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402
from test_an_unsettled_default_still_builds_the_rest import TWO_LIVES  # noqa: E402
from tree_design.store import latest_plan_version  # noqa: E402

#: Three files the rules hold as protected (finance, medical, identity).
HELD = {
    "May statement.txt":
        "Bank Statement\nAccount number: 12345678\nSort code 12-34-56\n"
        "Statement period: 1 May 2026 - 31 May 2026\nOpening balance 1,000.00\n"
        "Closing balance 900.00\n",
    "clinic letter.txt":
        "Patient: John Doe\nDate of birth: 01/01/1980\nDiagnosis: hypertension\n"
        "Prescription: lisinopril 10mg\nNHS number 123 456 7890\n",
    "passport scan.txt":
        "PASSPORT\nPassport No: 123456789\nNationality: British\n"
        "Date of expiry 2030\n",
}


@pytest.fixture(scope="module")
def sorted_db(tmp_path_factory):
    root = tmp_path_factory.mktemp("sorter")
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in {**TWO_LIVES, **HELD}.items():
        (corpus / name).write_text(body)
    database = root / "plan.sqlite"
    code = cli.main([str(corpus), "--user", "t", "--database", str(database),
                     "--situation", "academic.coursework", "--accept-groups"],
                    out=io.StringIO())
    assert code == 0
    conn = open_database(database)
    yield conn
    conn.close()


def _item(conn, label: str) -> dict:
    row = conn.execute(
        "SELECT item_id, typing_state FROM items WHERE display_label = ? "
        "AND presence = 'live' AND superseded_by IS NULL", (label,)).fetchone()
    assert row is not None, label
    return dict(row)


def test_show_tree_reports_the_sorters_latest_plan_and_every_file(sorted_db):
    out = ot.show_tree(sorted_db)
    assert out["ok"] is True and out["moved"] is False
    version = latest_plan_version(sorted_db)
    assert out["plan_version"] == version
    paths = {f["path"] for f in out["folders"]}
    assert "Academic/PHYS1401/lecture" in paths
    # Coverage: the counts add up to every file the sorter decided about.
    decided = {d.subject.file_id for d in decisions_for_plan(
        sorted_db, plan_version=version) if d.subject.file_id}
    assert out["files"]["decided"] == len(decided) == len(TWO_LIVES) + len(HELD)
    assert sum(out["files"]["by_outcome"].values()) == len(decided)
    assert out["files"]["by_outcome"]["place"] == sum(
        f["files"] for f in out["folders"])
    assert out["files"]["held"] == len(HELD)
    # The sorter's own run stops short of a freeze: no move plans yet.
    assert out["frozen_moves"] == 0


def test_quick_sort_cites_the_sorters_placement(sorted_db):
    lecture = _item(sorted_db, "Lecture 08.txt")
    out = ot.propose_tree(sorted_db, item_ids=[lecture["item_id"]])
    assert out["ok"] is True and out["moved"] is False
    assert out["source"] == "sorter_tree"
    [one] = out["files"]
    assert one["destination"] == "Academic/PHYS1401/lecture"
    assert one["outcome"] == "place"
    assert one["decision_id"] and one["why"]


def test_quick_sort_says_why_a_file_was_not_placed(sorted_db):
    survey = _item(sorted_db, "survey results.txt")
    [one] = ot.propose_tree(sorted_db, item_ids=[survey["item_id"]])["files"]
    assert one["destination"] is None
    assert one["outcome"] == "abstain"
    assert one["reason"]


def test_quick_sort_withholds_a_held_files_path(sorted_db):
    held = _item(sorted_db, "May statement.txt")
    assert held["typing_state"] == "held"
    [one] = ot.propose_tree(sorted_db, item_ids=[held["item_id"]])["files"]
    assert one["held"] is True
    assert one["open_target"] is None
    assert one["destination"] is None


def test_quick_sort_needs_the_files_named(sorted_db):
    out = ot.propose_tree(sorted_db)
    assert out["ok"] is False
    unknown = ot.propose_tree(sorted_db, item_ids=["no-such-item"])
    assert unknown["files"][0]["error"] == "item not found"


def test_no_tree_yet_says_what_to_run(tmp_path):
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "a.txt").write_text("x")
    conn = open_database(tmp_path / "assistant.sqlite")
    ot.scan_refresh(conn, str(lib))
    shown = ot.show_tree(conn)
    assert shown["ok"] is True and shown["plan_version"] is None
    assert "database-agent" in shown["next_step"]
    item_id = conn.execute("SELECT item_id FROM items").fetchone()[0]
    quick = ot.propose_tree(conn, item_ids=[item_id])
    assert quick["source"] == "type_buckets"
    assert "database-agent" in quick["next_step"]
    assert quick["files"][0]["bucket"]


def test_folders_the_sorter_set_aside_are_counted(tmp_path):
    corpus = tmp_path / "holder" / "corpus"
    project = corpus / "proj"
    project.mkdir(parents=True)
    (project / "requirements.txt").write_text("requests\n")
    (project / "main.py").write_text("print(1)\n")
    for name, body in TWO_LIVES.items():
        (corpus / name).write_text(body)
    database = tmp_path / "plan.sqlite"
    assert cli.main([str(corpus), "--user", "t", "--database", str(database),
                     "--stop-after", "tree"], out=io.StringIO()) == 0
    conn = open_database(database)
    aside = conn.execute(
        "SELECT count(DISTINCT path) FROM exclusion_verdicts").fetchone()[0]
    assert aside > 0
    assert sum(ot.show_tree(conn)["set_aside_by_rule"].values()) == aside
    # The count is the LATEST scan's: the project gone, nothing is set aside.
    for child in project.iterdir():
        child.unlink()
    project.rmdir()
    assert cli.main([str(corpus), "--user", "t", "--database", str(database),
                     "--stop-after", "tree"], out=io.StringIO()) == 0
    assert ot.show_tree(conn)["set_aside_by_rule"] == {}


def test_a_tree_with_no_placements_yet_says_so(tmp_path):
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in TWO_LIVES.items():
        (corpus / name).write_text(body)
    database = tmp_path / "plan.sqlite"
    assert cli.main([str(corpus), "--user", "t", "--database", str(database),
                     "--situation", "academic.coursework", "--accept-groups",
                     "--stop-after", "tree"], out=io.StringIO()) == 0
    conn = open_database(database)
    shown = ot.show_tree(conn)
    assert shown["plan_version"] and shown["files"]["decided"] == 0
    assert "--stop-after" in shown["next_step"]
    item_id = _item(conn, "Lecture 08.txt")["item_id"]
    [one] = ot.propose_tree(conn, item_ids=[item_id])["files"]
    assert one["destination"] is None and "--stop-after" in one["reason"]


def test_a_frozen_plan_cites_the_move_plan(tmp_path):
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in TWO_LIVES.items():
        (corpus / name).write_text(body)
    database = tmp_path / "plan.sqlite"
    assert cli.main([str(corpus), "--user", "t", "--database", str(database),
                     "--situation", "academic.coursework", "--accept-groups",
                     "--freeze"], out=io.StringIO()) == 0
    conn = open_database(database)
    assert ot.show_tree(conn)["frozen_moves"] > 0
    [one] = ot.propose_tree(
        conn, item_ids=[_item(conn, "Lecture 08.txt")["item_id"]])["files"]
    assert one["destination"] == "Academic/PHYS1401/lecture"
    assert one["move_plan_id"]


def test_registry_offers_show_tree_and_quick_sort_takes_item_ids():
    schemas = {s["function"]["name"]: s["function"]
               for s in deferred_schemas_for("organize_propose")}
    assert "show_tree" in schemas
    assert schemas["propose_tree"]["parameters"]["required"] == ["item_ids"]
