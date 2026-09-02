"""§2.8's raw wording, on a real run: `raw_variants` is empty on every value.

`00` §2.8: "If a document says U Chicago, the raw observation remains exactly that
wording, while a resolver may normalize it to University of Chicago and the user may
later choose to display it as UChicago." Three renderings, three columns.

`facts.values.ensure_value` writes `raw_variants` as an EMPTY list and never appends
to it. `facts.values.add_raw_variant` is the only writer of that column and nothing in
`src/` called it, so the first of §2.8's three renderings did not exist in any shipped
database -- the product canonicalised `PHYS 1401` to `PHYS1401` and forgot that the
document had said `PHYS 1401`.

`cli.py:716-721` records why this matters in this deployment's own words: "`PHYS 1401`,
`PHYS-1401` and `PHYS1401` are one course code and must reach P6 as ONE value". That
collapse is correct and it is the whole reason the raw wording has to be kept
somewhere -- otherwise the canonical form is the only surviving evidence of what any
document actually printed.

Written through `cli.main` rather than a hand-built fixture. `85` §6.4 and `84` §5.5:
a part's own suite cannot see this defect class, because every part builds its own
fixture and sets up the state the run never reaches.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli


BODY = """{code} Syllabus

Section 001. Instructor: R. Feynman.
Meets Tuesday and Thursday.
"""

#: A SECOND course code, printed two ways inside ONE document and appearing in no
#: other file. This is the case that separates "every reading in this group" from "the
#: reading that created the row", and it took two attempts to build.
#:
#: `direct_facts` groups PER FILE, so with one spelling per file every group has a
#: single member and a first-sighting-only writer is indistinguishable from a correct
#: one. The obvious repair -- print PHYS both ways in a fourth file -- still does not
#: bite, because the other three files contribute those same two spellings and the
#: SET comes out complete anyway. That is `85` §13.8's masking exactly: the louder
#: case hides the quieter one. The code has to be one no other file supplies.
#:
#: Measured, not assumed: sabotaging the loop down to `[0]` stayed green through both
#: earlier corpora and goes red on this one.
SECOND_CODE = """CHEM 2100 Problem Set 3

Submit to the CHEM-2100 dropbox by Friday.
"""


@pytest.fixture()
def run(tmp_path):
    """One corpus, one course code printed three ways across four files."""
    holder = tmp_path / "holder"
    corpus = holder / "corpus"
    corpus.mkdir(parents=True)
    for index, code in enumerate(("PHYS 1401", "PHYS-1401", "PHYS1401")):
        (corpus / f"syllabus {index}.txt").write_text(
            BODY.format(code=code), encoding="utf-8")
    (corpus / "problem set 3.txt").write_text(SECOND_CODE, encoding="utf-8")
    database = holder / "plan.sqlite"
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=out)
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def _subject_values(conn):
    return conn.execute(
        'SELECT canonical_value, raw_variants FROM "values" '
        "WHERE field_key = 'subject' ORDER BY canonical_value").fetchall()


def test_the_spellings_collapse_to_one_value_per_code(run):
    """The premise. If this fails the corpus stopped exercising the collapse and the
    tests below are measuring nothing -- the failure mode `84` §5.3 names."""
    assert [row["canonical_value"] for row in _subject_values(run)] == [
        "CHEM2100", "PHYS1401"]


def test_the_run_keeps_the_wording_each_document_used(run):
    """§2.8's first rendering. Asserted as the WHOLE set, not a containment: a
    containment is satisfied by a run that kept one spelling and lost two, which is
    most of the defect."""
    variants = {row["canonical_value"]: json.loads(row["raw_variants"])
                for row in _subject_values(run)}
    assert variants["PHYS1401"] == ["PHYS 1401", "PHYS-1401", "PHYS1401"]


def test_one_document_that_says_it_twice_contributes_both(run):
    """The half a first-sighting-only writer would lose. `CHEM2100` is printed two
    ways inside a single file and by no other file, so nothing else can supply the
    spelling that writer drops."""
    variants = {row["canonical_value"]: json.loads(row["raw_variants"])
                for row in _subject_values(run)}
    assert variants["CHEM2100"] == ["CHEM 2100", "CHEM-2100"]
