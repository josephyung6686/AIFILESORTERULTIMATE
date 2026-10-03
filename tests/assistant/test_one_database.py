"""One product on one database: default path, clean empty state, plan create."""
from __future__ import annotations

import io
from pathlib import Path

import pytest

from database_agent.db import shared_database_path
from database_agent.entrypoint import main

NOTHING = "Nothing indexed yet — run: database-agent <FOLDER>"

EMPTY_STATE_COMMANDS = [
    ["search", "cv"],
    ["ask", "where is my cv", "--local-only"],
    ["view"],
    ["view", "table"],
    ["suggest"],
    ["watch", "--seconds", "0.1"],
    ["plan", "show", "--plan-id", "p1"],
    ["plan", "create", "--item-id", "x", "--dst", "/tmp/y"],
    ["preview-plan", "p1"],
    ["memory", "status"],
    ["db", "check"],
    ["db", "rebuild-index"],
]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    """Nothing here may touch the real ~/.graph-agent."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    return home


def test_default_database_is_one_file_in_the_home_folder(home, tmp_path, monkeypatch):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    path = shared_database_path()
    assert path == home / ".graph-agent" / "database-agent.sqlite"
    assert oct(path.parent.stat().st_mode & 0o777) == "0o700"


def test_the_sorter_does_not_spell_the_default_itself():
    cli = (Path(__file__).parents[2] / "src" / "cli.py").read_text(encoding="utf-8")
    assert "database-agent-plan.sqlite" not in cli


@pytest.mark.parametrize("argv", EMPTY_STATE_COMMANDS, ids=lambda a: " ".join(a[:2]))
def test_empty_database_prints_one_plain_line(argv, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(argv) == 2
    captured = capsys.readouterr()
    assert captured.out.strip() == NOTHING
    assert "Traceback" not in captured.err


def test_an_empty_database_with_the_schema_is_also_nothing(tmp_path, monkeypatch, capsys):
    from database_agent.db import open_database
    from items.schema import create_items_schema
    monkeypatch.chdir(tmp_path)
    conn = open_database(shared_database_path(), scan_roots=[])
    create_items_schema(conn)
    conn.commit()
    conn.close()
    assert main(["search", "cv"]) == 2
    assert capsys.readouterr().out.strip() == NOTHING


def test_nothing_indexed_leaves_no_database_file_behind(home, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["search", "cv"]) == 2
    assert list((home / ".graph-agent").iterdir()) == []


def _index(tmp_path, monkeypatch):
    """A person's folder, indexed into ./database-agent-plan.sqlite."""
    from database_agent.db import open_database
    from items.identity import reconcile_tree
    from items.schema import create_items_schema
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "essay.txt").write_text("body", encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    conn = open_database(shared_database_path(), scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, lib)
    item_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label='essay.txt'"
    ).fetchone()[0]
    conn.commit()
    conn.close()
    return lib, item_id


def test_plan_created_on_the_command_line_applies_and_undoes(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    lib, item_id = _index(tmp_path, monkeypatch)
    dst = lib / "filed" / "essay.txt"
    assert main(["plan", "create", "--item-id", item_id, "--dst", str(dst)]) == 0
    plan_id = capsys.readouterr().out.split()[-1]
    assert main(["plan", "approve", "--plan-id", plan_id, "--full-list-viewed"]) == 0
    assert main(["plan", "apply", "--plan-id", plan_id, "--full-list-viewed"]) == 0
    assert dst.is_file() and not (lib / "essay.txt").exists()
    assert main(["plan", "undo", "--plan-id", plan_id]) == 0
    assert (lib / "essay.txt").is_file() and not dst.exists()


def test_plan_create_refuses_a_destination_outside_the_chosen_folders(tmp_path, monkeypatch, capsys):
    lib, item_id = _index(tmp_path, monkeypatch)
    capsys.readouterr()
    assert main(["plan", "create", "--item-id", item_id,
                 "--dst", str(tmp_path / "elsewhere" / "essay.txt")]) == 2
    assert "outside the folders you chose" in capsys.readouterr().out


def test_plan_missing_arguments_show_usage(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as e:
        main(["plan", "create"])
    assert e.value.code == 2
    assert "usage:" in capsys.readouterr().err


def test_restore_over_an_existing_target_names_replace(tmp_path, monkeypatch, capsys):
    lib, item_id = _index(tmp_path, monkeypatch)
    backup = tmp_path / "b.sqlite"
    assert main(["db", "backup", str(backup)]) == 0
    capsys.readouterr()
    assert main(["db", "restore", str(backup)]) == 2
    out = capsys.readouterr().out
    assert "--replace" in out and "Traceback" not in out


def test_top_level_help_lists_every_subcommand(capsys):
    assert main(["--help"]) == 0
    out = capsys.readouterr().out
    for word in ("search", "ask", "plan", "preview-plan", "watch", "view",
                 "suggest", "db", "memory", "database-agent <FOLDER>"):
        assert word in out
