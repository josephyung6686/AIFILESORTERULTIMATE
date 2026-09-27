"""An unnamed folder must not file a group under a situation name or its label.

`applications.*` belongs to `college_applications`. The prefix `applications`
is not a domain, and neither is the folder's display name. A coursework
fixture stays green when the category is read off `academic`, which is a
domain, so the label has to be something that is not.

Two folders. One names no kind at all: the run refuses in a sentence, and
that sentence is not `MalformedGroupRecord`. The other is the coursework pair
the rest of the suite already drafts, with a label that is only a display
name. The stored category is a domain.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from facts.domains import SCHEMA_IDS  # noqa: E402


LABEL = "Fall intake"


def _run(corpus: Path, database: Path) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "jy", "--label", LABEL,
                     "--accept-groups", "--stop-after", cli.STOP_AFTER_TREE,
                     "--database", str(database)], out=out)
    return code, out.getvalue()


def _categories(database: Path) -> set[str]:
    if not database.is_file():
        return set()
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
        if "groups" not in tables:
            return set()
        return {row[0] for row in conn.execute(
            "SELECT group_category FROM groups "
            "WHERE group_category IS NOT NULL")}
    finally:
        conn.close()


def test_a_folder_that_names_no_kind_refuses_without_a_bad_category(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "personal statement.txt").write_text(
        "Personal statement for the Fall2026 undergraduate application.\n"
        "Fall2026 deadline.\n")
    (corpus / "recommendation.txt").write_text(
        "Recommendation letter for the Fall2026 undergraduate application.\n")
    before = sorted(path.name for path in corpus.iterdir())
    code, report = _run(corpus, tmp_path / "plan.sqlite")

    assert "MalformedGroupRecord" not in report, report
    assert "Traceback" not in report, report
    assert code == 2, report
    assert "nothing in it said what kind of material" in report, report
    assert sorted(path.name for path in corpus.iterdir()) == before
    categories = _categories(tmp_path / "plan.sqlite")
    assert categories <= set(SCHEMA_IDS)
    assert LABEL not in categories
    assert "applications" not in categories


def test_a_drafted_folder_stores_a_domain_and_not_its_label(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr Lee. Credits: 3.\n")
    (corpus / "PHYS 1401 homework 3.txt").write_text(
        "PHYS 1401 Homework 3\n\nSpring 2026 lecture notes.\n")
    before = sorted(path.name for path in corpus.iterdir())
    database = tmp_path / "plan.sqlite"
    code, report = _run(corpus, database)

    assert code == 0, report
    assert "MalformedGroupRecord" not in report, report
    assert sorted(path.name for path in corpus.iterdir()) == before
    categories = _categories(database)
    assert categories, report
    assert categories <= set(SCHEMA_IDS), categories
    assert LABEL not in categories
    assert "academic.coursework" not in categories
