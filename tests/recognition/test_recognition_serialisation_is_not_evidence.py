# tests/recognition/test_recognition_serialisation_is_not_evidence.py
"""R-166: a container's own format is not one of the file's words.

**The measurement this file exists for.** A `.ipynb` whose entire content is the
line `PYTHON 1006 Spring 2026` -- an empty code cell, no prose, nothing that says
anything about programming -- came back `Recognition(code)`. Measured on 2026-09-08
at `5ff35c0` and, identically, at `8eb41e0` before the `104` R-160 merge, so this is
not something R-160 introduced and not something it fixed.

WHERE `code` GOT ITS TERM. `extractors.structured_text` emits the reader's
`document.language` as an observation of its own, `zone="metadata"`,
`locator="metadata:field=language"`. For a notebook that value is the string
`Jupyter notebook`, and `code` ships `notebook` as a `work_type_term`. So EVERY
notebook in the world carries one `code` term before a single word of it is read --
`IMG_0001.ipynb` below is a notebook with two empty cells and it carries it too.

WHERE ITS SECOND SIGNAL CAME FROM. `never_alone` says one signal never activates a
schema, and the corroboration gate seconds a leader with a schema-agnostic
identifier. The identifiers on that file are `PYTHON 1006` and `Spring 2026` -- a
course code and an academic term, which are evidence of COURSEWORK. So a file was
recognised as a code project by its file format plus its course number.

THE FOUR `Python 1006` NOTEBOOKS OF THE OWNER'S CORPUS ARE THAT CASE. They were the
only files that run placed, `tests/integration/test_step4_recognition_as_a_gate.py`
called them "the four the run places", and the schema they were placed under was
reached this way.

THE RULE, and it is the detector's own sentence twice over. `_matches` already
refuses the `path` locator because "the absolute path is not one of the file's own
words"; the name of the file's FORMAT is the same category. And `_decide` already
holds that `file_kind_plausible` "is a constraint and never a signal" -- reading the
kind back in as an authored term is exactly the kind acting as a signal, and the
kind is already doing its constraining job through `source_types` and the extension.

These tests drive the real `cli.main` over synthetic notebooks. No model is
configured (`conftest` sets `GRAPH_AGENT_NO_DOTENV=1`) and nothing reaches a network.
"""
from __future__ import annotations

import io
import json
import sqlite3

import pytest

import cli
from questions.store import activated_schemas
from recognition.detector import Abstention, Detector, Recognition
from recognition.rules import load_rules

#: Named so nothing in the NAME can be read as evidence. The defect was measured
#: with descriptive filenames first and `retail_hospitality` matched `course` out of
#: `B_course_only.ipynb`, which is the same mistake in a different place.
BARE = "IMG_0001.ipynb"
COURSE_LINE_ONLY = "IMG_0002.ipynb"
PYTHON_SOURCE_ONLY = "IMG_0003.ipynb"

#: What the reader hands `structured_text` as `document.language` for a notebook,
#: and the string the `code` work-type term `notebook` is found inside.
THE_FORMATS_OWN_NAME = "Jupyter notebook"


def _cell(kind: str, source: list[str]) -> dict:
    cell = {"cell_type": kind, "metadata": {}, "source": source}
    if kind == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell


def _notebook(cells: list[dict]) -> str:
    return json.dumps({
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.0"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    })


@pytest.fixture(scope="module")
def measured(tmp_path_factory):
    """One offline run over three notebooks, read back by every test here."""
    root = tmp_path_factory.mktemp("serialisation")
    corpus = root / "corpus"
    corpus.mkdir()
    # Nothing at all: two empty cells and the container around them.
    (corpus / BARE).write_text(
        _notebook([_cell("markdown", []), _cell("code", [])]))
    # The four real notebooks, reduced to what actually decided them: one line
    # naming a course, and an empty code cell.
    (corpus / COURSE_LINE_ONLY).write_text(
        _notebook([_cell("markdown", ["PYTHON 1006 Spring 2026\n"]),
                   _cell("code", [])]))
    # Real Python and nothing that says coursework -- the honest `code` case, and
    # the one that must not be broken by narrowing anything here.
    (corpus / PYTHON_SOURCE_ONLY).write_text(
        _notebook([_cell("code", ["import numpy as np\n", "def main():\n",
                                  "    return 42\n"])]))

    database = root / "plan.sqlite"
    out = io.StringIO()
    assert cli.main(
        [str(corpus), "--situation", "academic.coursework", "--label", "Coursework",
         "--user", "t", "--database", str(database)], out=out) == 0, out.getvalue()

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _detector(conn) -> Detector:
    """Composed as `cli.run` composes it, for the same reason `test_step4` does."""
    return Detector(
        load_rules(cli._RECOGNITION_MANIFEST.read_text),
        handling_for=cli.HANDLING_POLICY,
        now=lambda: "2026-09-08T00:00:00+00:00",
        is_protected=cli.is_protected_container,
        corroborating_observations=cli._identifier_observations,
        settled_by_user=lambda: activated_schemas(conn))


def _version(conn, filename: str) -> tuple[str, str]:
    row = conn.execute(
        "SELECT file_id, content_hash FROM files WHERE filename = ?",
        (filename,)).fetchone()
    assert row is not None, f"{filename!r} is not in the run"
    return row["file_id"], row["content_hash"]


def _matches(conn, filename: str):
    found, _ = _detector(conn)._matches(conn, *_version(conn, filename))
    return found


def _verdict(conn, filename: str):
    return _detector(conn).explain(conn, *_version(conn, filename))


# --- the container is stored, and it is stored as an observation -----------------


def test_the_formats_own_name_is_stored_as_an_observation_of_every_notebook(
        measured):
    """THE PREMISE, measured rather than assumed, and true of the empty one too.

    If this ever stops being true the tests below stop proving anything, so it is
    asserted first. `metadata:field=language` is `structured_text.LANGUAGE_FIELD`,
    §2.4's "language where relevant"; for a notebook the reader fills it with the
    format's name.
    """
    for filename in (BARE, COURSE_LINE_ONLY, PYTHON_SOURCE_ONLY):
        file_id, content_hash = _version(measured, filename)
        rows = measured.execute(
            "SELECT raw_value, location FROM evidence WHERE file_id = ? AND "
            "content_hash = ? AND superseded_by IS NULL", (file_id, content_hash)
        ).fetchall()
        formats = [row for row in rows
                   if json.loads(row["location"]).get("locator")
                   == "metadata:field=language"]
        assert len(formats) == 1, f"{filename}: {[dict(r) for r in rows]}"
        assert formats[0]["raw_value"] == THE_FORMATS_OWN_NAME, filename


# --- and it may not be an authored term ------------------------------------------


def test_a_notebook_with_no_content_matches_no_authored_term(measured):
    """THE GUARD. A file that says nothing has no evidence about itself.

    `IMG_0001.ipynb` is two empty cells. Every authored term it could match would
    have to come from the container, and a container is not a document. This is the
    test that fails the day a schema's term is satisfied by a serialization slot
    again -- whichever slot, and whichever schema.
    """
    found = _matches(measured, BARE)

    assert found == [], (
        "a notebook with no content matched an authored term, so the term was "
        "satisfied by the container's own structure rather than by the document: "
        + repr(found))


def test_a_notebook_saying_only_a_course_code_is_not_a_code_project(measured):
    """THE CASE THAT WAS SHIPPING. `Recognition(code)` at `5ff35c0` and at `8eb41e0`.

    One `code` term from the format's name, seconded by `PYTHON 1006` and
    `Spring 2026` -- a course code and an academic term. Every signal in that
    arithmetic was either the container or evidence of coursework, and the answer
    was a code project.
    """
    outcome = _verdict(measured, COURSE_LINE_ONLY)

    assert not (isinstance(outcome, Recognition) and outcome.schema_id == "code"), (
        "a notebook whose whole content is a course code is a code project again. "
        "Its `code` term is the string 'Jupyter notebook' in "
        "`metadata:field=language`, and its corroboration is the course number: "
        + repr(outcome))
    assert "code" not in {match.schema_id for match in _matches(
        measured, COURSE_LINE_ONLY)}, "the format's name is a `code` term again"


def test_narrowing_this_does_not_cost_the_honest_code_case(measured):
    """THE OTHER DIRECTION, because a cure that makes `code` unreachable is worse.

    `IMG_0003.ipynb` is real Python with nothing academic in it. It abstains today
    for want of a second signal, which is `never_alone` working -- what must not
    happen is that it starts matching the format's name to get one.
    """
    outcome = _verdict(measured, PYTHON_SOURCE_ONLY)

    assert isinstance(outcome, Abstention), (
        "real Python source became a recognition, and the only new term available "
        "to it is the container's: " + repr(outcome))
    assert "code" not in {match.schema_id
                          for match in _matches(measured, PYTHON_SOURCE_ONLY)}
