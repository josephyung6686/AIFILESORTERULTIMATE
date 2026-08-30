"""M14: cite the key, resolve the key, and show the failure when it will not.

`74` §6 B2's named test is `test_an_unresolvable_observation_key_renders_a_named_failure`
and its negative twin is `test_get_observation_by_id_is_unreachable_from_review_surface`.
The twin is a guard, so it is asserted in BOTH directions -- against the real
package and against sabotage modules that reach for an id -- because a guard
proven only by "it found nothing" is indistinguishable from one that can find
nothing (`tests/p10/test_p10_no_invention.py`:13-16).
"""
from __future__ import annotations

import ast
import pathlib

from evidence_shape.observation import Location, Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from placement.records import MatchingFact

from review_surface.citations import (
    RESOLVED,
    UNRESOLVABLE,
    resolve_citation,
    resolve_matching_facts,
)

T0 = "2026-08-29T00:00:00Z"
HASH_A = "a" * 64
HASH_B = "b" * 64


def _observation(*, content_hash, run_id, file_id, raw_value, before, after,
                 truncated=False, zone="body"):
    return Observation(
        file_id=file_id, content_hash=content_hash,
        extractor_name="fixture-pdf", extractor_version="1",
        source_type="text_document", raw_value=raw_value,
        location=Location(zone=zone, container_path=(), text_span=None,
                          time_span=None, region=None),
        occurrence_count=1, observed_at=T0, reliability="direct",
        run_id=run_id, normalized_value=raw_value, context_before=before,
        context_after=after, context_truncated=truncated, confidence=None,
        signal_tier=None)


def _run(*, run_id, file_id, content_hash):
    return ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="fixture-pdf", extractor_version="1",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, observation_count=1,
        coverage=None, finished_at=T0, failure_reason=None)


def _seed(conn) -> str:
    record_run(conn, _run(run_id="run-1", file_id="f-1", content_hash=HASH_A))
    observation = _observation(
        content_hash=HASH_A, run_id="run-1", file_id="f-1",
        raw_value="PHYS1401", before="Course ", after=" Spring 2026")
    record_observation(conn, observation)
    return observation.observation_key


def test_an_unresolvable_observation_key_renders_a_named_failure(p13_conn):
    """`74` §6 B2's named test, and Done-means 3's second clause.

    A broken citation is a RECORD, not a shorter list. Silently dropping it turns
    an explanation with three citations into an explanation with two and nothing
    to say a third existed, and §6.4's rule that an explanation "must not claim
    evidence the file does not carry" is only checkable by a reader if the
    missing evidence is visible AS missing.
    """
    citation = resolve_citation(p13_conn, "obs-key-that-never-existed")
    assert citation.state == UNRESOLVABLE
    assert citation.excerpt is None
    assert citation.observation_key == "obs-key-that-never-existed"
    assert "obs-key-that-never-existed" in citation.explanation
    # And the failure survives a fact list: two facts in, two pairs out.
    key = _seed(p13_conn)
    facts = (
        MatchingFact(file_fact_id="ff-1", field="subject", value="PHYS1401",
                     reliability="direct", evidence_ref=key),
        MatchingFact(file_fact_id="ff-2", field="subject", value="PHYS1401",
                     reliability="direct", evidence_ref="gone"),
    )
    pairs = resolve_matching_facts(p13_conn, facts)
    assert len(pairs) == 2, "an unresolvable citation is rendered, not omitted"
    assert [fact.file_fact_id for fact, _ in pairs] == ["ff-1", "ff-2"]
    assert pairs[0][1].state == RESOLVED
    assert pairs[1][1].state == UNRESOLVABLE


# --------------------------------------------------------------------------
# The twin: M14's guard, asserted in both directions.
# --------------------------------------------------------------------------

#: Every way P4 publishes to reach an observation by its ID rather than by its
#: KEY. `get_observation` is the function; `observation_id` is the column and the
#: attribute. Either one in `review_surface` breaks M14's promise that a negative
#: example recorded today still resolves after an extractor upgrade.
ID_ROUTES: tuple[str, ...] = ("get_observation", "observation_id")


def _package_modules() -> list[tuple[pathlib.Path, ast.Module]]:
    import review_surface
    root = pathlib.Path(review_surface.__file__).resolve().parent
    return [(path, ast.parse(path.read_text()))
            for path in sorted(root.glob("*.py"))]


def _fake(source: str, name: str = "offender.py"):
    return [(pathlib.Path(name), ast.parse(source))]


def _documentation_strings(tree: ast.Module) -> set[int]:
    """Docstrings and bare string statements, by NODE IDENTITY, not by regex.

    A text search over this file's own source would match the banned names in
    this very docstring; that false result has happened on this project before.
    """
    return {id(node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)}


def _id_routes(trees) -> list[str]:
    """Every place a module names an observation by id rather than by key.

    Parsed, not grepped: an import, an attribute, a call, a keyword argument and
    a subscript key all count, and a comment or a docstring does not.
    """
    offenders: list[str] = []
    for path, tree in trees:
        documentation = _documentation_strings(tree)
        for node in ast.walk(tree):
            found = None
            if isinstance(node, ast.Name) and node.id in ID_ROUTES:
                found = node.id
            elif isinstance(node, ast.Attribute) and node.attr in ID_ROUTES:
                found = node.attr
            elif isinstance(node, ast.keyword) and node.arg in ID_ROUTES:
                found = node.arg
            elif isinstance(node, ast.alias) and node.name in ID_ROUTES:
                found = node.name
            elif (isinstance(node, ast.Constant)
                  and isinstance(node.value, str)
                  and node.value in ID_ROUTES
                  and id(node) not in documentation):
                found = node.value
            if found is not None:
                offenders.append(f"{path.name}:{getattr(node, 'lineno', 0)} {found}")
    return offenders


def test_get_observation_by_id_is_unreachable_from_review_surface(p13_conn):
    """`74` §6 B2's negative twin. M14, asserted on the package AND on sabotage.

    The real package must be clean, and the guard must REJECT each of the four
    ways someone would reach for an id. Asserting only the first half would pass
    just as well if `ID_ROUTES` were empty.
    """
    assert _id_routes(_package_modules()) == []
    assert _id_routes(_fake(
        "from evidence_shape.store import get_observation\n"))
    assert _id_routes(_fake("row = store.get_observation(conn, x)\n"))
    assert _id_routes(_fake("x = fact.observation_id\n"))
    assert _id_routes(_fake('x = row["observation_id"]\n'))
    # And the key route the package DOES take is not caught, so the guard is a
    # guard against ids rather than against citations.
    assert _id_routes(_fake(
        "from evidence_shape.store import observations_by_key\n")) == []


def test_a_live_key_resolves_to_a_displayable_excerpt(p13_conn):
    key = _seed(p13_conn)
    citation = resolve_citation(p13_conn, key)
    assert citation.state == RESOLVED
    assert citation.excerpt == "PHYS1401"
    assert citation.context_before == "Course "
    assert citation.context_after == " Spring 2026"
    assert citation.extractor_name == "fixture-pdf"
    assert citation.reliability == "direct"


def test_an_empty_fact_list_resolves_to_an_empty_tuple(p13_conn):
    assert resolve_matching_facts(p13_conn, ()) == ()


def test_the_context_truncation_flag_survives_to_the_surface(p13_conn):
    """A truncated context shown as whole would misstate the evidence."""
    record_run(p13_conn, _run(run_id="run-2", file_id="f-2",
                              content_hash=HASH_B))
    observation = _observation(
        content_hash=HASH_B, run_id="run-2", file_id="f-2",
        raw_value="Columbia", before="...applying to ", after=" Univ...",
        truncated=True)
    record_observation(p13_conn, observation)
    assert resolve_citation(
        p13_conn, observation.observation_key).context_truncated is True


def test_two_rows_under_one_key_are_reported_and_never_adjudicated(p13_conn):
    """A key is content-addressed, so several rows are one observation re-recorded.

    P13 picks none over another -- that would be a judgement -- and says in the
    explanation that there were several.
    """
    key = _seed(p13_conn)
    record_run(p13_conn, _run(run_id="run-1b", file_id="f-1",
                              content_hash=HASH_A))
    record_observation(p13_conn, _observation(
        content_hash=HASH_A, run_id="run-1b", file_id="f-1",
        raw_value="PHYS1401", before="Course ", after=" Spring 2026"))
    citation = resolve_citation(p13_conn, key)
    assert citation.state == RESOLVED
    assert "2" in citation.explanation
