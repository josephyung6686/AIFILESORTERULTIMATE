# tests/p6/test_p6_usable.py
"""M11 — Done-means 28, A10, and the guard that makes preamble rule 5 checkable."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

import orchestrator

from database_agent.files_table import get_file, record_file

from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

from extractors.failure import ContractViolation
from extractors.ocr_policy import text_layer_state
from extractors.sink import ExtractionResult

from facts import usable
from facts.file_facts import FORBIDDEN_COLUMN_SUBSTRINGS, write_fact, RULE
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.schema import create_facts_schema
from facts.usable import (
    FACT_PASSES_TABLE, FactPassNotRun, no_usable_facts_for,
    passes_for, record_pass, targeted_ocr_needed_for,
)
from facts.values import VALUE_ORIGINS, ensure_value

NATIVE = frozenset({ANALYSIS_TIERS[1]})            # "native"
WITH_OCR = frozenset({ANALYSIS_TIERS[1], ANALYSIS_TIERS[2]})


def test_create_facts_schema_creates_the_pass_record(p6_conn):
    """The seam PLAN Task 19 Step 3b asks for, proved rather than assumed.

    This test is why the fixture that used to stand here is gone. `fact_passes` was
    created ONLY by an autouse fixture calling `create_fact_passes`, so every case
    below passed against a table production never made: consulting the verdict early
    raised `sqlite3.OperationalError`, which `orchestrator._extract_one` swallows into
    one `failed` run, instead of the `FactPassNotRun` the orchestrator re-raises by
    name. The whole safety argument of the module was unreachable in a real database.
    """
    rows = p6_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (FACT_PASSES_TABLE,)).fetchall()
    assert len(rows) == 1


def _any_fact(facts, unresolved) -> bool:
    """The injected threshold. Returns True when the stored facts ARE usable.

    §2.2's threshold is Deferred by name, so the test states one and the module
    states none. This one is the simplest that distinguishes the two Done-means 28
    cases; it is not a proposal.
    """
    return bool(facts)


def _never_usable(facts, unresolved) -> bool:
    return False


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20).
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _identifiers(module) -> set[str]:
    """Every name the module's CODE binds or reads.

    `def`, `class` and parameter names are collected as well as `ast.Name` and
    `ast.Attribute`, because a bare walk over those three misses exactly the shape
    the ban below is for: `def _text_quality_ratio(): ...` is a `FunctionDef`, its
    name is not an `ast.Name` node, and a guard that skipped it would pass while the
    heuristic sat in the module. Verified by mutation: adding that function to
    `usable.py` fails the ban with this version and passed without it.
    """
    tree = ast.parse(inspect.getsource(module))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, ast.keyword):
            names.add(node.arg or "")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(alias.name for alias in node.names)
            names.update(alias.asname or "" for alias in node.names)
            names.add(getattr(node, "module", "") or "")
    return names


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Scans", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


@pytest.fixture()
def scanned(p6_conn, tmp_path):
    return _record(p6_conn, tmp_path, name="scan.pdf", body=b"a scanned page")


def test_the_returned_callable_is_exactly_the_shape_p5_already_requires(p6_conn):
    # Two P5 tests assert `no_usable_facts` has no default and is called
    # positionally; the factory must therefore return that shape with no adapter.
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    signature = inspect.signature(verdict)
    parameters = list(signature.parameters.values())
    assert [p.name for p in parameters] == ["file_id", "content_hash"]
    for parameter in parameters:
        assert parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert parameter.annotation == "str"
    assert signature.return_annotation == "bool"
    # And it binds against the seam the orchestrator already declares.
    seam = inspect.signature(orchestrator.run_wave2).parameters["no_usable_facts"]
    assert seam.kind is inspect.Parameter.KEYWORD_ONLY
    assert seam.default is inspect.Parameter.empty


def test_false_for_a_file_with_one_active_usable_fact(scanned, p6_conn):
    # Done-means 28, first half.
    file_id, content_hash = scanned
    key = "sha256:" + "a" * 64
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="Columbia University",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="validated", origin=RULE,
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is False


def test_true_for_a_file_whose_evidence_produced_only_unresolved_rows(
        scanned, p6_conn):
    # Done-means 28, second half. §2.2's `text_layer_broken` case: text came out,
    # and no fact did. The `unresolved` rows are evidence FOR the verdict.
    file_id, content_hash = scanned
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason="no_candidate_evidence",
                     attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                     evidence_refs=(), cache_key="sha256:cache")
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is True


def test_the_unresolved_rows_reach_the_threshold_and_are_not_merely_absent(
        scanned, p6_conn):
    # The second argument is a promise, not decoration: a threshold that reads the
    # abstentions must be handed them. This fails if the factory ever passes an
    # empty sequence, `None`, or the facts twice.
    file_id, content_hash = scanned
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason="no_candidate_evidence",
                     attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                     evidence_refs=(), cache_key="sha256:cache")
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    seen: list[tuple[int, tuple[str, ...]]] = []

    def _reads_the_abstentions(facts, unresolved) -> bool:
        seen.append((len(facts), tuple(row["reason"] for row in unresolved)))
        return bool(unresolved)

    verdict = no_usable_facts_for(p6_conn,
                                  usable_threshold=_reads_the_abstentions)
    assert verdict(file_id, content_hash) is False
    assert seen == [(0, ("no_candidate_evidence",))]


def test_the_threshold_decides_and_the_module_states_none(scanned, p6_conn):
    # Both polarities driven through the same stored rows, so the module cannot be
    # holding a rule of its own behind the injected one.
    file_id, content_hash = scanned
    key = "sha256:" + "b" * 64
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="Columbia University",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="possible", origin=RULE,
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    assert no_usable_facts_for(
        p6_conn, usable_threshold=_any_fact)(file_id, content_hash) is False
    assert no_usable_facts_for(
        p6_conn, usable_threshold=_never_usable)(file_id, content_hash) is True
    parameter = inspect.signature(no_usable_facts_for).parameters["usable_threshold"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    # Task 25's technique: runtime introspection of the namespace, not a text search.
    numbers = {name: value for name, value in vars(usable).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {}


def test_no_recorded_pass_raises_rather_than_answering(scanned, p6_conn):
    # The SPEC: the verdict is "defined only after P6's deterministic pass on that
    # content hash has completed. Consulted earlier it would return `true` for every
    # file and trigger OCR on the whole corpus." `True` is not a value this branch
    # can produce, so that outcome is unreachable rather than unlikely.
    file_id, content_hash = scanned
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    with pytest.raises(FactPassNotRun):
        verdict(file_id, content_hash)


def test_facts_alone_do_not_stand_in_for_the_recorded_pass(scanned, p6_conn):
    # The stored rows are not the record. A fact written by some other path -- a user
    # correction, an import -- must not make the verdict answerable, because the
    # question is whether P6's pass RAN, not whether anything happens to be stored.
    file_id, content_hash = scanned
    key = "sha256:" + "c" * 64
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="Columbia University",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="validated", origin=RULE,
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    with pytest.raises(FactPassNotRun):
        verdict(file_id, content_hash)


def test_the_verdict_is_per_file_version_and_not_per_file(p6_conn, tmp_path):
    # Keyed on (file_id, content_hash): a pass over one version says nothing about
    # another, because the §3.4 cache key differs and so do the facts.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf", body=b"one")
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is True
    with pytest.raises(FactPassNotRun):
        verdict(file_id, "f" * 64)


def test_a_pass_over_another_file_at_the_same_hash_does_not_answer_for_this_one(
        scanned, p6_conn):
    # The other half of the key. `passes_for` filters on both columns, so a sibling
    # file that shares a content hash -- a duplicate, which §3 expects -- cannot
    # answer for a file whose own pass has not run.
    file_id, content_hash = scanned
    record_pass(p6_conn, file_id="some-other-file", content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    with pytest.raises(FactPassNotRun):
        verdict(file_id, content_hash)
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == ()


def test_the_raise_is_a_contract_violation_and_the_caller_cannot_swallow_it():
    # A plain Exception would be caught by `orchestrator._extract_one`'s broad
    # `except Exception` and become one `failed` run -- the file recorded as
    # unreadable, the scan continuing, the ordering defect turned into a data-quality
    # mystery. The orchestrator re-raises ContractViolation by name because "a
    # ContractViolation is not about this file at all".
    assert issubclass(FactPassNotRun, ContractViolation)


def test_consulting_it_during_extraction_ends_the_scan(p6_conn, tmp_path):
    """The danger, proved rather than described — this is why it is not wired in.

    `ocr_policy.text_layer_state` consults the verdict for every document whose run
    produced any non-empty text unit, inside `run_wave2`'s single loop, before P4
    holds the observations at all. Task 26 is cut, so nothing reorders that. This
    test IS the reason `orchestrator.TARGETED_OCR_UNAVAILABLE` is still the value the
    caller passes.
    """
    file_id, content_hash = _record(p6_conn, tmp_path, name="text.pdf",
                                    body=b"a text-bearing PDF")
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    result = ExtractionResult(run={},
                              text_units=({"text": "a non-empty text layer"},))
    with pytest.raises(FactPassNotRun):
        text_layer_state(result=result, file_id=file_id,
                         content_hash=content_hash, no_usable_facts=verdict)
    # A document with NO text never reaches the verdict, which is §2.2's other route
    # and needs no pass at all.
    assert text_layer_state(result=ExtractionResult(run={}), file_id=file_id,
                            content_hash=content_hash,
                            no_usable_facts=verdict) == "text_layer_absent"


def test_the_orchestrator_still_passes_the_stub_and_imports_nothing_from_facts():
    # D5, asserted from P6's side. The day someone wires this verdict into
    # `run_wave2`, this test fails before the scan does.
    assert orchestrator.TARGETED_OCR_UNAVAILABLE("any-file", "any-hash") is False
    tree = ast.parse(inspect.getsource(orchestrator))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
    assert "facts" not in imported


def test_a_pass_at_native_answers_and_a_pass_that_included_ocr_still_answers(
        scanned, p6_conn):
    # Pass 3's gate, and the termination condition. A file whose OCR pass also
    # produced nothing is a file with no usable facts, not a file to OCR again.
    file_id, content_hash = scanned
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    assert verdict(file_id, content_hash) is True
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=WITH_OCR)
    assert verdict(file_id, content_hash) is True
    # "Have we already tried OCR for this content hash" is a LOOKUP, not a flag.
    covered = passes_for(p6_conn, file_id=file_id, content_hash=content_hash)
    assert any(ANALYSIS_TIERS[2] in tiers for tiers in covered)
    assert NATIVE in covered and WITH_OCR in covered


def test_targeted_ocr_is_needed_only_after_an_unusable_pass_without_ocr(
        scanned, p6_conn):
    file_id, content_hash = scanned
    needed = targeted_ocr_needed_for(
        p6_conn, usable_threshold=_never_usable)

    with pytest.raises(FactPassNotRun):
        needed(file_id, content_hash)

    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    assert needed(file_id, content_hash) is True

    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=WITH_OCR)
    assert needed(file_id, content_hash) is False


def test_targeted_ocr_is_not_needed_when_native_facts_are_usable(
        scanned, p6_conn):
    file_id, content_hash = scanned
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    needed = targeted_ocr_needed_for(p6_conn, usable_threshold=lambda facts, _: True)
    assert needed(file_id, content_hash) is False


def test_targeted_ocr_names_the_ocr_tier_without_positional_vocabulary_coupling():
    source = inspect.getsource(usable)
    assert "ANALYSIS_TIERS[2]" not in source


def test_a_pass_recorded_twice_is_one_row(scanned, p6_conn):
    file_id, content_hash = scanned
    for _ in range(3):
        record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=NATIVE)
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == (
        NATIVE,)


def test_a_pass_records_only_tiers_p4_publishes(scanned, p6_conn):
    file_id, content_hash = scanned
    with pytest.raises(NotInVocabulary):
        record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=frozenset({"vibes"}))
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == ()
    # And a set with one good tier and one bad one writes nothing at all: the check
    # runs over every tier before the INSERT, so a refusal leaves no partial row.
    with pytest.raises(NotInVocabulary):
        record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=frozenset({ANALYSIS_TIERS[1], "vibes"}))
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == ()


def test_it_is_computed_from_the_fact_tables_and_no_text_quality_heuristic(p6_conn):
    # Done-means 28's second half, and A10's forbidden value by name:
    # {"ocr_fallback": true, "triggered_by": "language_quality_heuristic"}.
    # §2.2 and §2.7 both forbid deciding this from text quality.
    mentioned = _identifiers(usable)
    permitted_ocr_names = {
        "ocr_tier", "targeted_ocr_needed_for", "targeted_ocr_needed",
    }
    for banned in ("text", "unit", "language", "quality", "ratio", "char", "ocr_"):
        matches = [name for name in mentioned if banned in name.lower()]
        if banned == "ocr_":
            matches = [name for name in matches if name not in permitted_ocr_names]
        assert not matches, banned
    assert "evidence_shape.store" not in mentioned
    assert "language_quality_heuristic" not in _code_strings(usable)
    # The two reads it IS built from.
    assert "facts_for_file" in mentioned and "unresolved_for_file" in mentioned


def test_the_pass_record_obeys_the_same_negative_contract_as_the_fact_tables(
        p6_conn):
    # §3.14, applied to the fifth table too: a reviewer checks it from the schema.
    columns = [row["name"] for row in
               p6_conn.execute(f"PRAGMA table_info({FACT_PASSES_TABLE})")]
    assert columns == ["pass_id", "file_id", "content_hash", "analysis_tiers"]
    for column in columns:
        for forbidden in FORBIDDEN_COLUMN_SUBSTRINGS:
            assert forbidden not in column, (column, forbidden)


def test_creating_the_pass_record_twice_is_harmless_and_keeps_the_rows(
        scanned, p6_conn):
    # `create_facts_schema` is the ONLY creator of this table now -- the standalone
    # `create_fact_passes` was deleted, because it created a table the aggregate
    # creator already creates and no caller in `src/` wanted the one table alone. The
    # property is unchanged: the creator runs on every open of an existing database,
    # so the fifth table must survive a second creation like the other four do.
    file_id, content_hash = scanned
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    create_facts_schema(p6_conn)
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == (
        NATIVE,)
