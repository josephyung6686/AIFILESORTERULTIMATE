# tests/p6/test_p6_unresolved.py
"""B7 — Done-means 18 and 19. The abstention is a ROW, and two of the thirteen
reasons are not abstentions at all.

§3.6 stops at "no fact". §8.5 asks "Did it abstain when evidence was absent?" and an
absent row cannot answer a question about absence, which is the whole of B7.
"""
from __future__ import annotations

import json

import pytest

from database_agent.supersede import mark_superseded

from evidence_shape.observation import observation_key
from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import FieldNotInCatalogue
from facts.file_facts import (
    RULE, FORBIDDEN_COLUMN_SUBSTRINGS, facts_for_file, write_fact,
)
from facts.states import VALIDATED
from facts.unresolved import (
    ATTEMPTED_PRODUCERS, BELOW_MARGIN, BUDGET_DEFERRED, DIRECT_ROUTE, LLM_ROUTE,
    NOT_ABSTENTIONS, NO_CANDIDATE_EVIDENCE, PRIVACY_WITHHELD, RULE_ROUTE,
    UNRESOLVED_REASONS, unresolved_for_file, write_unresolved,
)
from facts.values import ensure_value

FILE_ID = "file-syllabus"
HASH = "6243c215e75e0f4a1d0c3b9e8a77215d5a4c9f6e2b1d0348ac59e7b0d1f2a3b4"
OTHER_HASH = "0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0"
CACHE_KEY = "sha256:cache-native-1"

#: The SPEC's thirteen, in the SPEC's own table order. Spelled here so the test is a
#: second, independent copy of the list rather than an echo of the module under test.
SPEC_THIRTEEN = (
    "no_candidate_evidence",
    "below_score_threshold",
    "below_margin",
    "context_check_failed",
    "context_truncated",
    "field_not_in_active_schema",
    "citation_absent_from_evidence",
    "normalization_failed",
    "contradicted_by_stronger_fact",
    "model_returned_unknown",
    "discounted_tool_metadata",
    "privacy_withheld",
    "budget_deferred",
)


def _key(raw: str) -> str:
    """A real P4 observation key. It needs no `evidence` row: `observation_key` is a
    pure function of content hash, extractor name, locator and raw value."""
    return observation_key(content_hash=HASH, extractor_name="pdf.text",
                           locator="heading:page=1/heading=2", raw_value=raw)


def _abstained(conn, file_id: str, content_hash: str, field_key: str) -> bool:
    """"Did P6 abstain on this field?" — the question a caller actually asks.

    This is deliberately NOT a published function. `NOT_ABSTENTIONS` is published so
    the caller can compute it; adding a predicate would be a second home for a rule
    §8.6 states once. The three lines are the whole of it.
    """
    rows = unresolved_for_file(conn, file_id, content_hash, field_key=field_key)
    return any(row["reason"] not in NOT_ABSTENTIONS for row in rows)


def _columns(conn) -> list[str]:
    return [row[1] for row in conn.execute("PRAGMA table_info(unresolved)")]


def test_the_thirteen_reasons_are_the_specs_thirteen(p6_conn):
    assert UNRESOLVED_REASONS == SPEC_THIRTEEN
    assert len(UNRESOLVED_REASONS) == 13
    assert len(set(UNRESOLVED_REASONS)) == 13


def test_a_fourteenth_reason_is_refused_at_the_write(p6_conn):
    with pytest.raises(NotInVocabulary):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
            reason="looked_wrong", attempted_producers=(DIRECT_ROUTE,),
            evidence_refs=(), cache_key=CACHE_KEY)
    assert unresolved_for_file(p6_conn, FILE_ID, HASH) == []


def test_the_three_attempted_producers_and_a_fourth_refused(p6_conn):
    assert ATTEMPTED_PRODUCERS == ("direct", "rule", "llm")
    with pytest.raises(NotInVocabulary):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
            reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE, "heuristic"),
            evidence_refs=(), cache_key=CACHE_KEY)


def test_the_row_carries_no_value_and_no_reliability_state_column(p6_conn):
    """Asserted from PRAGMA, not from a null check: a nullable `value_id` is a place
    someone will later write a value, and then `unresolved` is a weak fact."""
    columns = _columns(p6_conn)
    assert "value_id" not in columns
    assert "reliability_state" not in columns
    assert not [c for c in columns if "value" in c or "reliab" in c or "state" in c]


def test_the_row_obeys_file_facts_negative_contract(p6_conn):
    """The same list Task 4 publishes, imported rather than copied — one home for the
    forbidden set, so a column named `destination_node_id` fails both tables' tests on
    the day it is added (§3.14, §4.3)."""
    for column in _columns(p6_conn):
        for forbidden in FORBIDDEN_COLUMN_SUBSTRINGS:
            assert forbidden not in column, f"{column} violates the negative contract"


def test_record_id_projects_unresolved_id_so_p1_can_address_the_row(p6_conn):
    unresolved_id = write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
        evidence_refs=(), cache_key=CACHE_KEY)
    projected = p6_conn.execute(
        "SELECT record_id FROM unresolved WHERE unresolved_id = ?",
        (unresolved_id,)).fetchone()["record_id"]
    assert projected == unresolved_id
    # Verified by execution: a VIRTUAL generated column is invisible to the pragma,
    # which is exactly why the two tests above can read the pragma unqualified.
    assert "record_id" not in _columns(p6_conn)


def test_a_later_fact_supersedes_the_row_and_does_not_delete_it(p6_conn):
    """SPEC rule 3 and §8.2's worked example: the first pass refused, a later pass
    resolved, and the record of the refusal stays inspectable."""
    unresolved_id = write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
        evidence_refs=(), cache_key=CACHE_KEY)
    value_id = ensure_value(
        p6_conn, field_key="subject", canonical_value="BUSIB 4300",
        first_evidence_ref=_key("BUSIB 4300"), origin="automatic")
    # Task 4 owns the literal spelling of `rule` and publishes it as a named
    # constant; this call site imports the constant (preamble §3.1).
    fact_id = write_fact(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        value_id=value_id, reliability_state=VALIDATED, origin=RULE,
        evidence_refs=(_key("BUSIB 4300"),), cache_key="sha256:cache-ocr-1",
        active=True)

    mark_superseded(p6_conn, "unresolved", old_id=unresolved_id, new_id=fact_id,
                    reason="resolved on re-resolution over OCR evidence (§8.2)")

    rows = unresolved_for_file(p6_conn, FILE_ID, HASH)
    assert len(rows) == 1, "supersede must not delete the abstention"
    assert rows[0]["unresolved_id"] == unresolved_id
    assert rows[0]["superseded_by"] == fact_id
    assert rows[0]["supersede_reason"]
    assert rows[0]["reason"] == NO_CANDIDATE_EVIDENCE


def test_an_unresolved_row_is_absent_from_every_fact_read(p6_conn):
    """Done-means 19. The two tables never leak into one another."""
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=BELOW_MARGIN, attempted_producers=(RULE_ROUTE,),
        evidence_refs=(_key("BUSIB 4300"),), cache_key=CACHE_KEY)
    assert facts_for_file(p6_conn, FILE_ID, HASH) == []


def test_budget_deferred_and_privacy_withheld_are_not_abstentions(p6_conn):
    """B7's second half, and §8.6's "avoids the false impression that an unprocessed
    file was understood and found unimportant". All three are rows; only one is an
    abstention."""
    assert NOT_ABSTENTIONS == frozenset({"budget_deferred", "privacy_withheld"})
    assert NOT_ABSTENTIONS <= set(UNRESOLVED_REASONS)

    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
        evidence_refs=(), cache_key=CACHE_KEY)
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="purpose",
        reason=BUDGET_DEFERRED, attempted_producers=(),
        evidence_refs=(), cache_key=CACHE_KEY)
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="project",
        reason=PRIVACY_WITHHELD, attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
        evidence_refs=(), cache_key=CACHE_KEY)

    assert _abstained(p6_conn, FILE_ID, HASH, "subject") is True
    assert _abstained(p6_conn, FILE_ID, HASH, "purpose") is False
    assert _abstained(p6_conn, FILE_ID, HASH, "project") is False
    # All three are still RECORDS. Not an abstention is not the same as not a row.
    assert len(unresolved_for_file(p6_conn, FILE_ID, HASH)) == 3


def test_a_ceiling_reached_before_any_producer_ran_is_writable(p6_conn):
    """`attempted_producers` may be empty, and the column still says so out loud."""
    unresolved_id = write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="purpose",
        reason=BUDGET_DEFERRED, attempted_producers=(),
        evidence_refs=(), cache_key=CACHE_KEY)
    row = unresolved_for_file(p6_conn, FILE_ID, HASH)[0]
    assert row["unresolved_id"] == unresolved_id
    assert json.loads(row["attempted_producers"]) == []
    assert json.loads(row["evidence_refs"]) == []


def test_evidence_refs_hold_observation_keys_and_nothing_else(p6_conn):
    """M14: the citation is a KEY, never an `observation_id` and never a row id."""
    refs = (_key("BUSIB 4300"), _key("Columbia"))
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=BELOW_MARGIN, attempted_producers=(RULE_ROUTE,),
        evidence_refs=refs, cache_key=CACHE_KEY)
    stored = json.loads(unresolved_for_file(p6_conn, FILE_ID, HASH)[0]["evidence_refs"])
    assert stored == list(refs)
    assert all(ref.startswith("sha256:") for ref in stored)

    with pytest.raises(ValueError):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
            reason=BELOW_MARGIN, attempted_producers=(RULE_ROUTE,),
            evidence_refs=("obs-00000001",), cache_key=CACHE_KEY)


def test_a_field_outside_the_catalogue_cannot_be_abstained_on(p6_conn):
    """§3.12 — new values may be created automatically, new fields may not. The rule
    binds the refusal row as hard as it binds the fact row."""
    with pytest.raises(FieldNotInCatalogue):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="vibe_score",
            reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE,),
            evidence_refs=(), cache_key=CACHE_KEY)


def test_the_abstention_is_per_file_version_and_the_read_is_totally_ordered(p6_conn):
    """§3.4, §8.2 — the row is per content hash, and the reader imposes its own order
    rather than inheriting insertion order from SQLite."""
    for content_hash, reason in ((HASH, NO_CANDIDATE_EVIDENCE),
                                 (OTHER_HASH, BELOW_MARGIN)):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=content_hash, field_key="subject",
            reason=reason, attempted_producers=(RULE_ROUTE,),
            evidence_refs=(), cache_key=CACHE_KEY)

    native = unresolved_for_file(p6_conn, FILE_ID, HASH)
    assert [row["reason"] for row in native] == [NO_CANDIDATE_EVIDENCE]
    assert [row["reason"] for row in unresolved_for_file(
        p6_conn, FILE_ID, OTHER_HASH)] == [BELOW_MARGIN]

    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="purpose",
        reason=PRIVACY_WITHHELD, attempted_producers=(LLM_ROUTE,),
        evidence_refs=(), cache_key=CACHE_KEY)
    rows = unresolved_for_file(p6_conn, FILE_ID, HASH)
    order = [(row["created_at"], row["unresolved_id"]) for row in rows]
    assert order == sorted(order), "the reader imposes its own total order"
    assert len(unresolved_for_file(p6_conn, FILE_ID, HASH,
                                   reason=PRIVACY_WITHHELD)) == 1
    assert len(unresolved_for_file(p6_conn, FILE_ID, HASH,
                                   field_key="purpose")) == 1


def test_the_filters_refuse_a_value_outside_their_vocabulary(p6_conn):
    with pytest.raises(NotInVocabulary):
        unresolved_for_file(p6_conn, FILE_ID, HASH, reason="looked_wrong")
    with pytest.raises(FieldNotInCatalogue):
        unresolved_for_file(p6_conn, FILE_ID, HASH, field_key="vibe_score")
