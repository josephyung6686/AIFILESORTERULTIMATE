"""The runtime side reads one compiled manifest through an INJECTED reader.

`tree_design.catalogue.load_catalogue` is the model and the shape is copied
deliberately: *"An injected reader rather than a path keeps this module out of the
filesystem entirely, which is what makes the 'no repository scanning' guard checkable
by import inspection rather than by hope."*
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from facts.domains import SCHEMA_IDS, UnknownSchema
from recognition.compile import compile_rules
from recognition.rules import RecognitionRulesRequired, load_rules
from recognition.vocabulary import MANIFEST_VERSION

MANIFEST_PATH = (Path(__file__).resolve().parents[2] / "src" / "recognition"
                 / "library" / "recognition.json")


def reader(payload) -> callable:
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return lambda: text


def one_schema(**overrides):
    entry = {
        "schema_id": "academic",
        "context_terms": ["syllabus"],
        "work_type_terms": ["lecture"],
        "source_types": ["text_document"],
        "extensions": [".pdf"],
        "file_kind_never_alone": True,
        "rows": ["academic.coursework"],
        "refused_rows": [],
        "needs_llm": [],
        "never_alone_rows": [],
    }
    entry.update(overrides)
    return {"manifest_version": MANIFEST_VERSION, "compiled_rows": 1,
            "refused_rows": 0, "schemas": {entry["schema_id"]: entry}}


# --- the reader is the caller's ------------------------------------------------

def test_a_path_is_not_a_reader():
    with pytest.raises(RecognitionRulesRequired):
        load_rules(str(MANIFEST_PATH))


def test_there_is_no_empty_default_rule_set():
    # An empty release would make every guard pass by having nothing to recognise.
    with pytest.raises(RecognitionRulesRequired):
        load_rules(None)


# --- the manifest is a release --------------------------------------------------

def test_a_manifest_from_another_shape_version_is_refused():
    stale = one_schema()
    stale["manifest_version"] = MANIFEST_VERSION + 1
    with pytest.raises(RecognitionRulesRequired):
        load_rules(reader(stale))


def test_a_manifest_naming_a_schema_outside_SCHEMA_IDS_is_a_load_error():
    payload = one_schema()
    payload["schemas"]["astrology"] = dict(payload["schemas"]["academic"],
                                           schema_id="astrology")
    with pytest.raises(UnknownSchema):
        load_rules(reader(payload))


def test_a_manifest_whose_key_and_entry_disagree_about_the_schema_is_refused():
    payload = one_schema()
    payload["schemas"]["academic"]["schema_id"] = SCHEMA_IDS[-1]
    with pytest.raises(RecognitionRulesRequired):
        load_rules(reader(payload))


# --- what the loader publishes --------------------------------------------------

def test_compiled_rules_round_trip_through_json_unchanged():
    compiled = compile_rules([{
        "id": "academic.coursework", "schema_id": "academic", "refuse_node": False,
        "proposed_context_terms": ["syllabus"], "work_types": ["lecture"],
        "file_kinds": {"source_types": ["text_document"], "extensions": [".pdf"],
                       "never_alone": True},
        "recognition": {"deterministic": [], "needs_llm": ["a prose essay"],
                        "never_alone": ["a bare number"]},
    }])
    rules = load_rules(reader(compiled))
    schema = rules.schemas["academic"]
    assert schema.context_terms == ("syllabus",)
    assert schema.work_type_terms == ("lecture",)
    assert schema.extensions == frozenset({".pdf"})
    assert schema.deferred_readings == ("a prose essay",)
    assert rules.manifest_version == MANIFEST_VERSION


def test_the_packaged_manifest_loads_and_covers_every_schema_the_rows_named():
    rules = load_rules(MANIFEST_PATH.read_text)
    assert set(rules.schemas) <= set(SCHEMA_IDS)
    assert rules.compiled_rows == 358
    # Not asserted as a literal count of schemas: `SCHEMA_IDS` is widening
    # underneath this package, so the guard is that every compiled schema is a
    # recognised one and that the rule set is not empty.
    assert rules.schemas
    for schema in rules.schemas.values():
        assert schema.context_terms or schema.work_type_terms, schema.schema_id


def test_every_term_in_the_packaged_manifest_is_already_normalised():
    # The detector matches against normalised text and does not re-normalise the
    # rule side at query time. A term that arrived unnormalised would never match.
    rules = load_rules(MANIFEST_PATH.read_text)
    for schema in rules.schemas.values():
        for term in schema.context_terms + schema.work_type_terms:
            assert term == " ".join(term.split()).casefold(), (
                schema.schema_id, term)
