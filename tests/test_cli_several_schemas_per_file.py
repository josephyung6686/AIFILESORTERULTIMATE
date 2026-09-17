# tests/test_cli_several_schemas_per_file.py
"""The owner's ruling of 11 Sep 2026: several schemas per file, by evidence.

`00` Amendments of 2026-09-11 item 3, `104` §18.43: §3's two lines are read
together -- "activate domain-specific schemas only when the evidence indicates a
domain is plausible" and "one file may hold facts from more than one domain" --
so activation is PER SCHEMA, BY EVIDENCE.

P6 has always been able to hold several: `active_domains` returns a set and
`active_field_allowlist` unions the field sets, and `tests/p6/test_p6_domains.py`
pins both. What could not was the composition root, which injected exactly one
signal at three sites -- `ActivationSignal(schema_id=<the branch's schema>,
activates=lambda facts: True)` -- so §3.11's own worked case (a research abstract
submitted with a university application) could not happen on a real run whatever
its evidence said.

**The signals are the ones the product already has, and none is invented here.**
`cli.evidence_activation` builds them from `branch_situation`'s own two
fact-derived reach signals, at P9's anchor bar:

* a `work_type` fact whose term exactly one schema authored (`WORK_TYPE_OWNER`) --
  "a syllabus anchors coursework; a cover letter anchors applications";
* a fact on one of the schema's own `DOMAIN_FIELDS`, less the two bridges
  `work_type` and `term` that `104` R-37 measured carrying a cover letter into a
  course.

The recogniser's READING is deliberately not among them, for `branch_situation`'s
measured reason: it answers what a file is made of, not which life it is part of,
and it is a reach signal into a schema an anchor has already opened.

**The branch's own schema stays unconditionally active.** Coverage is sacred: a
file under a branch is asked that branch's questions whatever its own evidence
says, which is `104` R-140 and is what a file no branch reaches lives on. The
ruling widens; it takes nothing away.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from evidence_shape.schema import create_evidence_schema

from facts.domains import active_domains, active_field_allowlist
from facts.fields import DOMAIN_FIELDS, create_fields
from facts.file_facts import RULE, write_fact
from facts.states import LLM_SUPPORTED, VALIDATED
from facts.values import VALUE_ORIGINS, ensure_value

from llm_harness.dossier import field_glossary

import cli

EVIDENCE_REF = "sha256:" + "a" * 64
CACHE_KEY = "sha256:" + "b" * 64

#: The two schemas this module measures with. Their own field sets overlap in
#: nothing but the bridges, which is why they are the pair `104` R-37 measured.
ACADEMIC_OWN = set(DOMAIN_FIELDS["academic"]) - cli.BRIDGES_THAT_DO_NOT_REACH
CAREER_OWN = set(DOMAIN_FIELDS["career"]) - cli.BRIDGES_THAT_DO_NOT_REACH


@pytest.fixture()
def facts_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return conn


def _record(conn, tmp_path, *, name):
    body = b"one file, two lives"
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, *, file_id, content_hash, field_key, value,
          state=VALIDATED):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=EVIDENCE_REF,
                            origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=RULE,
                      evidence_refs=(EVIDENCE_REF,), cache_key=CACHE_KEY,
                      active=True)


def _allowlist(conn, file_id, content_hash, schema_id):
    return active_field_allowlist(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=cli.evidence_activation(schema_id))


def _active(conn, file_id, content_hash, schema_id):
    return active_domains(conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=cli.evidence_activation(schema_id))


# --- a file whose evidence names two schemas carries both -----------------------


def test_a_file_with_signals_for_two_schemas_gets_both_allowlists(
        facts_conn, tmp_path):
    """The ruling's own case: one file, two lives, and neither is dropped.

    A résumé attached to a course's application: `subject` is academic's own
    field, `job_title` is career's, and both are at the anchor bar. Under the
    academic branch the file is asked BOTH schemas' fields.
    """
    file_id, content_hash = _record(facts_conn, tmp_path, name="two lives.txt")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="subject", value="PHYS1401")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="job_title", value="Software Engineer")

    assert {"academic", "career"} <= _active(
        facts_conn, file_id, content_hash, "academic")
    allowed = set(_allowlist(facts_conn, file_id, content_hash, "academic"))
    assert ACADEMIC_OWN <= allowed, allowed
    assert CAREER_OWN <= allowed, allowed


def test_the_facts_say_which_schema_each_field_belongs_to(facts_conn, tmp_path):
    """Fields carry their schema already: the catalogue answers for the row.

    A fact row names a `field_key`; `facts.fields.DOMAIN_FIELDS` says which
    schemas reference it and the `fields` table's own `scope` column says which
    one DECLARES it. So "which schema is this fact under" is answerable about
    every row written here without a column being added to carry it.
    """
    file_id, content_hash = _record(facts_conn, tmp_path, name="two lives.txt")
    for field_key, value in (("subject", "PHYS1401"),
                             ("job_title", "Software Engineer")):
        _fact(facts_conn, file_id=file_id, content_hash=content_hash,
              field_key=field_key, value=value)
    scopes = {row["field_key"]: row["scope"] for row in facts_conn.execute(
        "SELECT field_key, scope FROM fields")}
    assert scopes["subject"] == "academic"
    assert scopes["job_title"] == "career"
    for field_key, schema_id in (("subject", "academic"),
                                 ("job_title", "career")):
        assert field_key in DOMAIN_FIELDS[schema_id]


def test_the_field_glossary_for_site_a_lists_both_schemas_fields(
        facts_conn, tmp_path):
    """`00`:42's glossary is built from the allowlist, so it widens with it."""
    file_id, content_hash = _record(facts_conn, tmp_path, name="two lives.txt")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="subject", value="PHYS1401")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="job_title", value="Software Engineer")

    allowed = _allowlist(facts_conn, file_id, content_hash, "academic")
    defined = {entry["field"] for entry in field_glossary(allowed)}
    assert "subject" in defined and "job_title" in defined, sorted(defined)


# --- a file whose evidence names one schema gets one ----------------------------


def test_a_file_with_signals_for_one_schema_gets_one(facts_conn, tmp_path):
    """Today's behaviour, preserved: no second schema's fields appear."""
    file_id, content_hash = _record(facts_conn, tmp_path, name="syllabus.txt")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="subject", value="PHYS1401")

    assert _active(facts_conn, file_id, content_hash, "academic") == frozenset(
        {"academic"})
    allowed = set(_allowlist(facts_conn, file_id, content_hash, "academic"))
    assert ACADEMIC_OWN <= allowed
    assert not (CAREER_OWN - ACADEMIC_OWN) & allowed, allowed


def test_a_file_with_no_facts_at_all_still_carries_its_branchs_schema(
        facts_conn, tmp_path):
    """`104` R-140 and the constitution's coverage rule: the branch still asks.

    A file whose own evidence names no schema is not a file with no questions:
    it is under a branch, and the branch's schema is what it is asked. This is
    the arm that keeps the ruling a widening.
    """
    file_id, content_hash = _record(facts_conn, tmp_path, name="survey.txt")
    assert _active(facts_conn, file_id, content_hash, "academic") == frozenset(
        {"academic"})
    assert set(DOMAIN_FIELDS["academic"]) <= set(
        _allowlist(facts_conn, file_id, content_hash, "academic"))


# --- what does NOT activate a second schema -------------------------------------


def test_a_bridge_field_does_not_open_a_second_schema(facts_conn, tmp_path):
    """`104` R-37's measured finding: `work_type` and `term` carry no file.

    `Summer2026` shared between a syllabus and a cover letter is the bridge that
    filed the cover letters under Coursework, and a `work_type` VALUE the
    library gave two owners anchors neither.
    """
    file_id, content_hash = _record(facts_conn, tmp_path, name="anything.txt")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="term", value="Summer2026")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="work_type", value="reference letter")
    assert _active(facts_conn, file_id, content_hash, "academic") == frozenset(
        {"academic"})


def test_a_work_type_term_one_schema_authored_opens_that_schema(
        facts_conn, tmp_path):
    """The anchor of `104` R-37, read here as an activation signal.

    `cover letter` is career's alone, so a file carrying it is asked career's
    fields even under the coursework branch -- which is exactly the résumé the
    ruling is about.
    """
    file_id, content_hash = _record(facts_conn, tmp_path, name="letter.txt")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="work_type", value="cover letter")
    assert cli.WORK_TYPE_OWNER["cover letter"] == "career"
    assert {"academic", "career"} <= _active(
        facts_conn, file_id, content_hash, "academic")


def test_a_fact_below_the_anchor_bar_opens_nothing(facts_conn, tmp_path):
    """P9's bar, and the same one `_anchor_facts_of` reads.

    An `llm_supported` fact is a model's own answer, not a rule's; letting one
    widen what a model may propose would let a model author its next question.
    """
    file_id, content_hash = _record(facts_conn, tmp_path, name="maybe.txt")
    _fact(facts_conn, file_id=file_id, content_hash=content_hash,
          field_key="job_title", value="Software Engineer", state=LLM_SUPPORTED)
    assert _active(facts_conn, file_id, content_hash, "academic") == frozenset(
        {"academic"})


def test_one_signal_per_schema_and_the_branchs_own_is_not_doubled():
    """`ActivationSignals` refuses two signals for one schema, so the builder
    must not add the branch's schema twice."""
    signals = cli.evidence_activation("academic")
    ids = [signal.schema_id for signal in signals.signals]
    assert len(ids) == len(set(ids)), ids
    assert "academic" in ids


# --- end to end: the offer a real run makes about a file with two lives ---------

#: `104` R-37's own stub and call log, reused rather than rebuilt: what is
#: asserted is which fields each file was OFFERED, read off the product's own
#: dossier rows, which is the whole of this ruling in calls.
R37 = Path(__file__).resolve().parent / "integration"


def _r37_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "r37_per_branch_situation", R37 / "test_r37_per_branch_situation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_real_run_activates_both_schemas_and_still_asks_one_situations_levels(
        tmp_path, monkeypatch):
    """One branch, one situation typed, and a file whose own facts name two lives.

    The corpus is all coursework -- every kind-of-file anchor the library owns
    here is academic's -- so there is ONE branch and the run is the run it was.
    The notes file also states a job title, which is career's own field and no
    bridge, so its evidence makes career plausible and this ruling lets the file
    carry both schemas: §3.5's closed vocabulary for it is the union, and a claim
    on `job_title` is no longer out of schema.

    **The QUESTION does not widen, and that is the owner's morning rule.**
    `model_facts.open_question` bounds what is offered by the SITUATION's own
    folder levels, and placement still gives a file one home -- so the coursework
    file is still asked coursework's levels. The ruling widens what may be
    proposed and recorded about a file, not which folders a run builds.
    """
    import io

    from facts.file_facts import facts_for_file
    from readers.model_ollama import BASE_URL_NAME as LOCAL_BASE_URL_NAME
    from readers.model_ollama import MODEL_NAME as LOCAL_MODEL_NAME

    r37 = _r37_module()
    stub_module = r37._stub_module()
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "PHYS 1401 cover letter.txt").write_text(
        "PHYS 1401\nCover Letter\n\nInstructor: Dr. Lee. Lecture Mondays.\n"
        "Dear Hiring Manager, I am writing to apply for the position.\n")
    database = tmp_path / "holder" / "plan.sqlite"

    out = io.StringIO()
    with stub_module.StubOllama() as running:
        running.dossier_in = stub_module.dossier_in
        monkeypatch.setenv(LOCAL_MODEL_NAME, "stub-qwen3:8b")
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, running.base_url)
        code = cli.main([str(corpus), "--situation", "academic.coursework",
                         "--label", "Coursework", "--user", "t",
                         "--database", str(database)], out=out)
        assert code == 0, out.getvalue()

    import sqlite3
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT file_id, content_hash FROM files WHERE filename = ?",
            ("PHYS 1401 cover letter.txt",)).fetchone()
        held = {(fact["field_key"], fact["canonical_value"])
                for fact in facts_for_file(
                    conn, row["file_id"], row["content_hash"])
                if fact["active"] and fact["superseded_by"] is None}
        fields = {field for field, _value in held}
        assert "subject" in fields, (sorted(held), out.getvalue())
        # (`104` §18.95's invariant is asserted where a run actually reaches an
        # ACCEPTED site-G verdict; this run does not, and a conditional assertion
        # here would only look like coverage. See
        # `tests/integration/test_situation_site_boundary.py`.)
        assert any(field == "work_type"
                   and cli.WORK_TYPE_OWNER.get(value) == "career"
                   for field, value in held), (sorted(held), out.getvalue())
        # Both ways round: under either branch's schema the file's OWN evidence
        # names the other one, and neither is dropped.
        for branch_schema in ("academic", "career"):
            active = _active(conn, row["file_id"], row["content_hash"],
                             branch_schema)
            assert {"academic", "career"} <= active, (branch_schema,
                                                      sorted(active))
            allowed = set(_allowlist(conn, row["file_id"],
                                     row["content_hash"], branch_schema))
            assert ACADEMIC_OWN <= allowed and CAREER_OWN <= allowed, (
                branch_schema, sorted(allowed))
    finally:
        conn.close()

    # And the QUESTION is still the situation's own levels: no career field was
    # put to the model about a file under the coursework branch.
    log = r37._call_log(database)
    offered = frozenset().union(
        *log.get("PHYS 1401 syllabus.txt", [frozenset()]))
    assert offered, (log, out.getvalue())
    assert not offered & (CAREER_OWN - ACADEMIC_OWN), (sorted(offered), log)
