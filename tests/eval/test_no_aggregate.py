# tests/eval/test_no_aggregate.py
"""Done-means 3 and the two vocabulary/authorship guards.

§8.5: "A single overall 'accuracy' number hides the mechanism that needs repair."
This is a negative acceptance test, not a style preference.
"""
import ast
from pathlib import Path

from database_agent.db import create_schema

from eval_harness.assertions import verdict_counts
from eval_harness.counts import bundle_counts
from eval_harness.store import EVAL_TABLES, create_eval_schema

SRC = Path(__file__).resolve().parents[2] / "src" / "eval_harness"

#: Whole identifier parts, compared after splitting on "_". `placement_scorer_version`
#: splits to {placement, scorer, version} and is therefore clean; `overall_score`
#: splits to {overall, score} and is not.
FORBIDDEN_PARTS = {
    "accuracy", "score", "aggregate", "overall", "rate", "percent", "grade",
    "f1", "precision", "recall", "total",
}

#: Other parts' closed vocabularies. P2 stores their values; it declares none.
#: This is the ONE list. Task 5 deliberately carries no second copy of the P7 rows
#: — two lists for one rule drift on one member and whichever runs last wins.
FOREIGN_VOCABULARY = [
    # P7 §8.4: the five handling classes and all FOUR operation modes, copied from
    # `../P7-privacy-consent-gate/SPEC.md` Contract out §4 and §5. `offline` and
    # `hybrid` are ordinary English words and are the two likeliest false positives
    # here; both were checked against every src/eval_harness/ file in this plan and
    # neither occurs. If a later task needs one of these words for its own meaning,
    # rename the identifier — do not shorten this list.
    "public_low", "personal_non_sensitive", "sensitive_personal",
    "highly_sensitive_credential_bearing", "unreadable_unclassified",
    "offline", "local_model", "hybrid", "cloud_assisted",
    # P6 §3.11 domain fact fields
    "target_university", "application_cycle", "artifact_type", "tax_year",
    "capture_year",
    # §7.3 residual template names
    "reference clips", "reading inbox", "review later", "protected records",
    # §3.13 reliability states as P2 vocabulary
    "llm-supported", "user_confirmed",
]


def _identifier_parts(name: str) -> set[str]:
    return {part.lower() for part in name.split("_") if part}


def test_no_p2_column_is_an_aggregate(eval_conn):
    create_eval_schema(eval_conn)
    present = {r["name"] for r in eval_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    # Every table P2 declares has actually been created by now.
    assert set(EVAL_TABLES) <= present, sorted(set(EVAL_TABLES) - present)
    for table in EVAL_TABLES:
        for column in eval_conn.execute(f"PRAGMA table_info({table})"):
            offending = _identifier_parts(column["name"]) & FORBIDDEN_PARTS
            assert not offending, f"{table}.{column['name']}: {offending}"


def test_no_reader_returns_an_aggregate_key(eval_conn):
    from eval_harness.bundle import open_bundle, seal_bundle
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(eval_conn, corpus_form="snapshot",
                            source_scan_ref="s", pinned_plan_id="p",
                            pinned_plan_version="1", policy_settings={})
    seal_bundle(eval_conn, bundle_id)
    for reader_result in (bundle_counts(eval_conn, bundle_id),
                          verdict_counts(eval_conn, "no-such-run")):
        for key in reader_result:
            offending = _identifier_parts(str(key)) & FORBIDDEN_PARTS
            assert not offending, f"{key}: {offending}"


def test_no_source_identifier_is_an_aggregate():
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                names.append(node.name)
            elif isinstance(node, ast.Name):
                names.append(node.id)
            for name in names:
                offending = _identifier_parts(name) & FORBIDDEN_PARTS
                assert not offending, f"{path.name}: {name} -> {offending}"


def test_no_string_literal_is_the_word_accuracy():
    # §8.5's sentence is quoted in comparison.py's docstring and must stay there.
    # What may not exist is a string that IS the word — a field name, a key, a
    # column. The AST distinguishes the two; a substring search cannot.
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert node.value.strip().lower() != "accuracy", path.name


def test_p2_declares_no_other_parts_vocabulary():
    offenders = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for term in FOREIGN_VOCABULARY:
            if term in text:
                offenders.append(f"{path.name}: {term!r}")
    assert not offenders, "P2 declared another part's vocabulary: " + "; ".join(offenders)


def test_p2_ships_no_expectation_content():
    # SPEC Deferred: the hand-labelled reference corpus, the template library, the
    # gazetteer and the residual library are hand work. P2 publishes
    # bundle_expectation; it does not fill it. Every expected value P2 handles
    # arrives as an argument, so a LITERAL one in source would be P2 authoring it.
    assert not list(SRC.rglob("*.json"))
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "expected_value":
                assert not isinstance(node.value, (ast.Dict, ast.List)), \
                    f"{path.name}: a literal expected_value"


def test_p2_appends_no_event_and_writes_no_correction(eval_conn):
    # "The acting part authors" — and evaluation acts on no file. §8.2's event
    # list is a list of things that happen TO a file.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "append_event" not in text, path.name
        assert "INSERT INTO events" not in text, path.name
        assert "correction_scope" not in text, path.name
    assert eval_conn.execute("SELECT count(*) AS n FROM events").fetchone()["n"] == 0


def test_p2_never_deletes_from_events():
    # I6 (tombstone vs append) is deferred to P7. Nothing here forecloses it, and
    # nothing here deletes provenance.
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert "delete from events" not in text, path.name


def test_the_whole_suite_runs():
    # A reminder for the executor, not an assertion: run `pytest -q` before the
    # commit below.
    assert True
