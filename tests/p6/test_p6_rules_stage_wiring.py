# tests/p6/test_p6_rules_stage_wiring.py
"""§3.5's context check, composed as `FactResolver`'s `rule` stage. NOT YET SHIPPED.

`src/cli.py`'s `_resolver` binds `stages={"direct": ..., "rule": None, "llm": None}`,
and its docstring calls that a decision: "This deployment ships no authored rule set
and no model route." It was the right decision while no rule set existed. What it
costs is measurable, and it was measured on a real three-file corpus:

    invoice.txt | subject = INV20261        reliability_state = direct

An invoice number became a `subject` fact -- the field folders are named after -- with
no academic context anywhere near it. §3.5's worked requirement is the one thing that
would have refused it: "BUSIB 4300 becomes a course fact only when the engine finds a
course-code pattern together with academic context such as 'syllabus,' 'lecture,'
'credits,' 'instructor,' or 'semester.'" Done-means 8 states both halves, and only the
negative half is reachable today, from a producer that is never run.

THIS FILE PROVES THE COMPOSITION, NOT THE RULE. `tests/p6/test_p6_rules.py` already
drives `apply_rules` and covers the check itself. What was never tested is that
`apply_rules` FITS: that binding it as the `rule` stage of the resolver this command
builds produces §3.5's two outcomes over one file's real observations. It does, and it
needs no change to `facts.rules` -- `apply_rules` already has the `Stage` shape once a
caller binds `rules` and `screen`, which is what the `src/cli.py` patch does.

WHAT IS STILL THE DEPLOYMENT'S. The pattern is not P6's to author (§3.10's catalogue
beyond the three named date patterns is Deferred and a course-code pattern is not
among them), so the regex below is this TEST's, exactly as it would be `src/cli.py`'s.
`facts.rules` authors the five context terms §3.5 states literally and nothing else.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.discount import MetadataScreen
from facts.file_facts import facts_for_file
from facts.resolver import FactResolver
from facts.rules import ACADEMIC_CONTEXT_TERMS, Rule, apply_rules
from facts.states import VALIDATED
from facts.unresolved import unresolved_for_file
from facts.usable import record_pass

CLOCK = "2026-08-19T12:00:00+00:00"
NO_CATALOGUE = MetadataScreen(tool_producer_strings=(), metadata_property_names=())

#: `src/cli.py:_STRUCTURED`, verbatim. The deployment's identifier pattern, reused
#: rather than reinvented so this test asks the question the shipped command would.
IDENTIFIER = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")

SUBJECT_RULE = Rule(pattern=IDENTIFIER,
                    required_context_terms=ACADEMIC_CONTEXT_TERMS,
                    field_key="subject")


def _file(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, before, after):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="text.plain", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="text.plain",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("body", (), TextSpan(0, len(raw))), occurrence_count=1,
        observed_at=CLOCK, reliability="direct", run_id=run_id,
        context_before=before, context_after=after))


def _resolver_with_the_rule_stage():
    """`src/cli.py:_resolver`, with `rule` bound instead of `None`.

    Every other argument is that function's, unchanged, so the only difference
    between this composition and the shipped one is the line the patch changes.
    """
    def rule_stage(conn, file_id, content_hash):
        return apply_rules(conn, file_id=file_id, content_hash=content_hash,
                           rules=(SUBJECT_RULE,), screen=NO_CATALOGUE)

    return FactResolver(
        stages={"direct": None, "rule": rule_stage, "llm": None},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda file_id: False,
        record_pass=lambda conn, file_id, content_hash: record_pass(
            conn, file_id=file_id, content_hash=content_hash,
            analysis_tiers=frozenset(("filesystem", "native"))),
        cache_key_for=lambda file_id, content_hash: f"test-rule:{content_hash}",
        screen_metadata=lambda conn, file_id, content_hash: ())


def test_an_invoice_number_does_not_become_a_subject_when_the_rule_stage_runs(
        p6_conn, tmp_path):
    """Done-means 8's negative half, in composition. THE MEASURED DEFECT.

    On the shipped command this file yields `subject = INV20261`, `direct`, and a
    folder is proposed from it.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="invoice.txt",
                                  body=b"Invoice INV20261 from Northside Plumbing.")
    _observe(p6_conn, run_id="run-invoice", file_id=file_id,
             content_hash=content_hash, raw="INV20261",
             before="Invoice ", after=" from Northside Plumbing.")

    result = _resolver_with_the_rule_stage().resolve(
        p6_conn, file_id=file_id, content_hash=content_hash)

    assert result.fact_ids == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    # And the refusal is RECORDED, with the reason §3.5 gives it -- not silence.
    assert [row["reason"] for row in
            unresolved_for_file(p6_conn, file_id, content_hash)] == [
                "context_check_failed"]


def test_the_same_shape_with_academic_context_does_become_a_subject(p6_conn,
                                                                    tmp_path):
    """Done-means 8's positive half, which is unreachable in the shipped command.

    P4's skeleton fixture 1 carries `context_before: "Syllabus - "` with a capital S,
    and N-6 makes the §3.5 check case-insensitive precisely so that fixture resolves.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.txt",
                                  body=b"PHYS1401 syllabus")
    _observe(p6_conn, run_id="run-syllabus", file_id=file_id,
             content_hash=content_hash, raw="PHYS1401",
             before="Syllabus - ", after=" Introductory Physics")

    result = _resolver_with_the_rule_stage().resolve(
        p6_conn, file_id=file_id, content_hash=content_hash)

    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["canonical_value"], row["reliability_state"])
            for row in rows] == [("subject", "PHYS1401", VALIDATED)]
    assert len(result.fact_ids) == 1


def test_the_rule_stage_is_the_only_change_the_deployment_needs(p6_conn, tmp_path):
    """`apply_rules` already has the `Stage` shape. Nothing in `facts.rules` moves.

    This is the claim the `src/cli.py` patch rests on, so it is asserted rather than
    assumed: bind two things the caller owns and the result is `(conn, file_id,
    content_hash) -> tuple[str, ...]`, which is exactly what `FactResolver` calls.
    """
    import inspect

    parameters = inspect.signature(apply_rules).parameters
    assert list(parameters) == ["conn", "file_id", "content_hash", "rules", "screen"]
    for name in ("rules", "screen"):
        assert parameters[name].default is inspect.Parameter.empty, (
            f"{name} has a default; §3.5's catalogue is the deployment's and a "
            "default here would let a run ship with a rule set nobody chose")


def test_p6_authors_the_five_context_terms_and_no_pattern(p6_conn):
    # The division the patch depends on: the terms are §3.5's, quoted; the pattern is
    # the deployment's. A course-code regex inside `facts` would be P6 authoring a
    # catalogue the SPEC defers.
    assert ACADEMIC_CONTEXT_TERMS == (
        "syllabus", "lecture", "credits", "instructor", "semester")
    import facts.rules as rules_module
    assert not [value for value in vars(rules_module).values()
                if isinstance(value, re.Pattern)]
