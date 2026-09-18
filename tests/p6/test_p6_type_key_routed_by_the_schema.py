# tests/p6/test_p6_type_key_routed_by_the_schema.py
"""`106` Phase 6.2: the type keys `60` H6 named are produced, routed by the schema.

`facts.kind` is ONE mechanism for `work_type`, `artifact_type` and `record_type`, and
the recognition manifest ships the terms per schema. The production root wired
`work_type` alone, and its recorded reason was that the schema "is not known when the
producer runs -- `run_p1_p7` resolves facts BEFORE it classifies". Since `00` amendment
7(c) site G names a schema per file before the fact pass walks the roster, and
`_model_fact_pass` builds one resolver per schema. This binds the rule there.

H6.2, kept whole: the ACTIVE SCHEMA chooses the key, a file is never re-routed to the
nearest declared key, and a schema declaring `work_type` has already had its type
question answered corpus-wide. H6.3, kept whole: the vocabulary is the schema's OWN and
never the union -- `research`'s `protocol` must not be found in a `finance` file.
"""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.fields import DOMAIN_FIELDS
from facts.file_facts import facts_for_file
from facts.states import VALIDATED

import cli

CLOCK = "2026-09-18T00:00:00+00:00"


def _record(conn, tmp_path, *, name):
    path = tmp_path / name
    path.write_bytes(b"corpus")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=6,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _named(conn, *, file_id, content_hash, raw):
    record_run(conn, ExtractionRun(
        run_id="run-name", file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem.record", extractor_version="1.0.0",
        source_type="filesystem", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem.record", extractor_version="1.0.0",
        source_type="filesystem", raw_value=raw,
        location=Location("filename", ()), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id="run-name"))


def _typed(conn, file_id, content_hash, field_key):
    return [(row["canonical_value"], row["reliability_state"])
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == field_key and row["active"]]


def test_a_research_file_named_poster_gets_an_artifact_type(p6_conn, tmp_path):
    """SABOTAGE: return `None` from `type_key_rule` for every schema -- nothing is
    written, and every `research.*` branch's required `artifact_type` stays empty."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="NeurIPS poster final.pdf")
    _named(p6_conn, file_id=file_id, content_hash=content_hash,
           raw="NeurIPS poster final.pdf")
    stage = cli.type_key_rule("research")
    assert stage is not None
    assert len(stage(p6_conn, file_id, content_hash)) == 1
    assert _typed(p6_conn, file_id, content_hash, "artifact_type") == [("poster", VALIDATED)]
    assert _typed(p6_conn, file_id, content_hash, "work_type") == []


def test_a_finance_file_named_bank_statement_gets_a_record_type(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="bank statement march.pdf")
    _named(p6_conn, file_id=file_id, content_hash=content_hash,
           raw="bank statement march.pdf")
    stage = cli.type_key_rule("finance")
    assert stage is not None
    stage(p6_conn, file_id, content_hash)
    assert _typed(p6_conn, file_id, content_hash, "record_type") == [("bank statement", VALIDATED)]


def test_the_vocabulary_is_the_schemas_own_and_never_the_union(p6_conn, tmp_path):
    """H6.3. SABOTAGE: compile the union over every schema -- `bank statement` is
    found in a research file and written under `artifact_type`."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="bank statement march.pdf")
    _named(p6_conn, file_id=file_id, content_hash=content_hash,
           raw="bank statement march.pdf")
    cli.type_key_rule("research")(p6_conn, file_id, content_hash)
    assert _typed(p6_conn, file_id, content_hash, "artifact_type") == []


def test_a_schema_that_declares_work_type_routes_no_second_key():
    """`_rule_stage` already filled `work_type` for every file. SABOTAGE: route
    `record_type` for `career` -- `resume` lands under two keys on one file, which is
    the H6.3 collision `facts.kind` measured on 15 files."""
    for schema_id, fields in DOMAIN_FIELDS.items():
        if cli.WORK_TYPE_FIELD in fields:
            assert cli.type_key_for(schema_id) is None, schema_id
            assert cli.type_key_rule(schema_id) is None, schema_id


def test_every_routed_key_is_declared_by_its_schema():
    """H6.2: never re-routed to the nearest declared key."""
    routed = {schema_id: cli.type_key_for(schema_id) for schema_id in DOMAIN_FIELDS}
    assert any(routed.values()), "nothing routes -- the rule is dead"
    for schema_id, key in routed.items():
        assert key is None or key in DOMAIN_FIELDS[schema_id], (schema_id, key)
        assert key != cli.WORK_TYPE_FIELD


def test_a_schema_the_catalogue_carries_no_fields_for_routes_nothing():
    for schema_id in ("identity", "medical", "legal"):
        assert cli.type_key_rule(schema_id) is None


def test_a_type_key_carries_no_file_into_a_branch_and_anchors_no_move():
    """`artifact_type` is declared by five schemas and `record_type` by seven. A
    `validated` one is the same kind of claim as `work_type` -- what the file IS --
    and `work_type` is a bridge for that reason. SABOTAGE: leave the sets as they
    were -- a `poster` on a research file activates `code`, `creative` and
    `engineering` (`_schema_reached_by_the_facts`) and, un-named, is held between
    four branches (`partition_by_branch`)."""
    from branch_situation import BRIDGES_THAT_DO_NOT_REACH
    for key in (cli.ARTIFACT_TYPE_FIELD, cli.RECORD_TYPE_FIELD):
        assert key in cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE
        assert key in BRIDGES_THAT_DO_NOT_REACH
    assert cli.CAPTURE_YEAR_FIELD not in BRIDGES_THAT_DO_NOT_REACH, (
        "a capture time reaching `photos` is the truth about the file")


def test_every_resolver_the_fact_pass_builds_carries_the_rule():
    """The wiring, read off the code and not off a comment. `_model_fact_pass` is a
    closure inside `main`, so the whole module is parsed and every call of
    `model_fact_resolver` in it is the set -- the five build sites and no others.
    SABOTAGE: drop `rule=` at one of the five -- files of that schema get no type
    key, and nothing on the screen says which schema was left out."""
    tree = ast.parse(inspect.getsource(cli))
    builds = [node for node in ast.walk(tree)
              if isinstance(node, ast.Call)
              and getattr(node.func, "id", None) == "model_fact_resolver"]
    assert len(builds) == 5, [ast.dump(call.func) for call in builds]
    for call in builds:
        assert any(keyword.arg == "rule" for keyword in call.keywords), ast.dump(call)


# --- `106` Phase 6.3: the model's spelling of a type key is the library's ----------

def test_the_models_spelling_of_a_type_key_is_the_librarys(p6_conn):
    """`normalize_for_model`'s promise: "the model's value is canonicalised by the
    SAME rule the deterministic path uses for that field". `work_type` had that
    branch and the other two keys fell to "whitespace collapsed and nothing else",
    so `Poster` and `poster` were two values and would be two folders.
    SABOTAGE: drop the branch."""
    assert cli.normalize_for_model("artifact_type", "  POSTER ") == "poster"
    assert cli.normalize_for_model("record_type", "Bank  Statement") == "bank statement"


def test_a_type_value_the_library_has_not_seen_is_kept_as_the_model_wrote_it():
    """Unchanged behaviour for an unseen value: it is not refused here, because
    `normalize_for_review` answers for three fields and these are not among them
    (`REVIEW_NORMALISED_FIELDS`, an owner decision). Folding members to the library's
    spelling must not start rejecting non-members. SABOTAGE: return `None` on a miss."""
    assert cli.normalize_for_model("artifact_type", "Reading Copy") == "Reading Copy"
