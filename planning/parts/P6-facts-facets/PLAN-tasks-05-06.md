### Task 5: `unresolved` — the abstention row, and its thirteen reasons

**Files:**
- Create: `src/facts/unresolved.py`
- Modify: `src/facts/vocabulary.py`, `src/facts/schema.py`
- Test: `tests/p6/test_p6_unresolved.py`

**Interfaces:**
- Consumes: `facts.fields.get_field`, `facts.fields.FieldNotInCatalogue`;
  `evidence_shape.vocabulary.check`, `evidence_shape.vocabulary.NotInVocabulary`;
  `evidence_shape.canonical.canonical_json`; `database_agent.supersede.supersede_ddl`.
- Produces: `UNRESOLVED_REASONS: tuple[str, ...]` (the thirteen) **and one named constant per reason
  — `NO_CANDIDATE_EVIDENCE`, `BELOW_SCORE_THRESHOLD`, `BELOW_MARGIN`, `CONTEXT_CHECK_FAILED`,
  `CONTEXT_TRUNCATED`, `FIELD_NOT_IN_ACTIVE_SCHEMA`, `CITATION_ABSENT_FROM_EVIDENCE`,
  `NORMALIZATION_FAILED`, `CONTRADICTED_BY_STRONGER_FACT`, `MODEL_RETURNED_UNKNOWN`,
  `DISCOUNTED_TOOL_METADATA`, `PRIVACY_WITHHELD`, `BUDGET_DEFERRED`**,
  `ATTEMPTED_PRODUCERS: tuple[str, str, str]` (`direct`, `rule`, `llm`) **and one named constant per
  member — `DIRECT_ROUTE`, `RULE_ROUTE`, `LLM_ROUTE`** (suffixed, because `facts.states.DIRECT` and
  `facts.file_facts.RULE` are different vocabularies and several modules import both),
  `write_unresolved(conn, *, file_id, content_hash, field_key, reason, attempted_producers,
  evidence_refs, cache_key) -> str`,
  `unresolved_for_file(conn, file_id, content_hash, *, field_key=None, reason=None) -> list[sqlite3.Row]`,
  `NOT_ABSTENTIONS: frozenset[str]` (`budget_deferred`, `privacy_withheld`).

**Done-means:** 18, 19.

#### What this task is for, in one paragraph

§3.6 says a model that cannot cite sufficient evidence *"must return unknown"*, and stops there — no
fact. **B7 says no fact is not enough**, because §8.5 asks under Fact quality *"Did it abstain when
evidence was absent?"* and an absent row cannot answer a question about absence. So every refusal P6
makes writes a row naming the field it attempted, the reason, the routes it tried, and the
observation keys it looked at. Two rules make the row trustworthy and both are tests below: it is
**not a weak fact** (no `value_id`, no reliability state, absent from every fact read), and
`budget_deferred` and `privacy_withheld` are **not abstentions** — §8.6 requires the product to
*"mark the deferred stage, and leave the file or group in review rather than guessing"*, so that
reporting *"avoids the false impression that an unprocessed file was understood and found
unimportant"*. Merging them would report a budget stop as a considered refusal, which is that
impression exactly.

#### Verified by execution, 2026-08-22 — three things this task's shape depends on

Run before the code below was written, because reading a signature instead of importing it has cost
this project three defects.

```text
supersede_ddl("unresolved")   -> "supersedes TEXT, superseded_by TEXT, supersede_reason TEXT"
SUPERSEDE_COLUMNS             == ("supersedes", "superseded_by", "supersede_reason")
check(v, vocab, *, name)      -> v, or raises NotInVocabulary (a ValueError subclass)
```

1. **A VIRTUAL generated column does not appear in `PRAGMA table_info`.** Executed against a table
   built exactly like the DDL below: `PRAGMA table_info(unresolved)` returned
   `['unresolved_id', 'supersedes', 'superseded_by', 'supersede_reason']` and **not** `record_id`,
   while `SELECT record_id FROM unresolved` returned the `unresolved_id`. Both tests below depend on
   this: the negative-contract test reads `PRAGMA table_info` and would otherwise have to whitelist a
   column, and the `record_id` test must use a `SELECT` because the pragma cannot see it.

2. **P1's `mark_superseded` works across the two tables, in the one direction Task 5 needs, and
   silently declines the other.** Executed with an `unresolved` row `u1` and a `file_facts` row `f1`:
   `mark_superseded(conn, "unresolved", old_id="u1", new_id="f1", reason="…")` set
   `superseded_by="f1"` and `supersede_reason` on the `unresolved` row, left the row readable, and
   left `file_facts.supersedes` as `None` — because its last statement is
   `UPDATE unresolved SET supersedes = ? WHERE record_id = ?` and no `unresolved` row has id `f1`, so
   it matches zero rows and raises nothing. The forward link is recorded, the back-pointer is not.
   **This is stated rather than fixed.** `mark_superseded` takes one `table`, so a cross-table
   back-pointer is not expressible through P1's published surface; `src/facts/supersede.py` (§8.2,
   Task 23) owns supersession as an operation and is where a back-pointer would be decided. Task 5
   owns only the **schema affordance** — the three supersede columns and the `record_id` projection —
   and asserts the `unresolved` side of the link, which is the half Done-means 19 and SPEC rule 3
   require: *"A later fact … does not delete the row — it supersedes it, and the row remains
   readable."*

3. `record_file(...)` → `get_file(conn, file_id)["content_hash"]` is 64 lowercase hex with **no**
   `sha256:` prefix. Observation **keys** are `sha256:`-prefixed; content hashes are not. The two
   never share a validator.

#### Three rulings this task makes, each because leaving it implicit would be worse

- **`evidence_refs` may be empty; `attempted_producers` may be empty too.** The SPEC's schema is
  explicit for the first — *"the observation keys considered, where any were (may be empty)"*. The
  second follows from `budget_deferred`: an §8.6 ceiling can be reached **before** any producer runs,
  so a required-non-empty producer list would make the one reason that most needs recording
  unwritable. Neither absence is silent: both columns are `NOT NULL` and hold `[]`, so a reader can
  tell "looked at nothing" from "column never written".
- **`evidence_refs` entries are validated for the `sha256:` prefix, and nothing else.** The prefix is
  what distinguishes M14's `observation_key` from an `observation_id` or a row id, and getting that
  wrong is the defect Done-means 30 exists to catch. Whether the key **resolves** is not checked
  here: `observations_by_key` on an unknown key returns `[]` rather than raising, so a resolution
  check would need a policy for the empty result, and that policy is Task 7's.
- **The row is never de-duplicated and never updated.** Two abstentions for the same
  `(file_id, content_hash, field_key)` under two different cache keys are two rows, because §3.4's key
  is what makes them different events. `write_unresolved` only ever INSERTs.

---

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run the test and see it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_unresolved.py -x -q
```

**Expected failure:** collection fails before a single test runs —
`ModuleNotFoundError: No module named 'facts.unresolved'`. `src/facts/unresolved.py` does not exist,
so every one of the fourteen tests errors at import. This is the failure to see; a failure inside a
test body at this step would mean the module already existed and the task is mis-scoped.

- [ ] **Step 3: Append P6's third and fourth closed vocabularies to `src/facts/vocabulary.py`**

Task 2 created this module and owns everything already in it (`FIELD_SCOPES` and the field-scope
checks). Append the block below **unchanged**; edit nothing above it. The reasons and the producers
live here rather than in `unresolved.py` because the Global Constraints put P6's closed vocabularies
in **one** module, checked with P4's `check` — the same rule that keeps `FIELD_SCOPES` here.

```python
# ---------------------------------------------------------------------------
# Task 5 — the abstention vocabularies (§3.6, §8.5, §8.6; B7)
# ---------------------------------------------------------------------------

#: The thirteen reasons, one named constant each. This module owns the literal
#: spelling; every call site imports the CONSTANT (preamble §3.1). That
#: `write_unresolved` validates the reason through P4's `check` -- so a misspelling
#: raises `NotInVocabulary` rather than storing -- is true and worth knowing, and it
#: is NOT a reason to spell the reason inline: validation at the seam catches a TYPO,
#: it does not stop the literal being a SECOND HOME.
NO_CANDIDATE_EVIDENCE: str = "no_candidate_evidence"
BELOW_SCORE_THRESHOLD: str = "below_score_threshold"
BELOW_MARGIN: str = "below_margin"
CONTEXT_CHECK_FAILED: str = "context_check_failed"
CONTEXT_TRUNCATED: str = "context_truncated"
FIELD_NOT_IN_ACTIVE_SCHEMA: str = "field_not_in_active_schema"
CITATION_ABSENT_FROM_EVIDENCE: str = "citation_absent_from_evidence"
NORMALIZATION_FAILED: str = "normalization_failed"
CONTRADICTED_BY_STRONGER_FACT: str = "contradicted_by_stronger_fact"
MODEL_RETURNED_UNKNOWN: str = "model_returned_unknown"
DISCOUNTED_TOOL_METADATA: str = "discounted_tool_metadata"
PRIVACY_WITHHELD: str = "privacy_withheld"
BUDGET_DEFERRED: str = "budget_deferred"

#: The thirteen in the SPEC's own table order, for iteration and membership. Each is
#: fired by exactly one place, named in the comment beside it, so a reason with no
#: producer or a producer with no reason is visible by reading this list. To NAME one
#: reason, import the constant above -- never a literal, never an index.
UNRESOLVED_REASONS: tuple[str, ...] = (
    NO_CANDIDATE_EVIDENCE,           # no observation offered a candidate (§3.6)
    BELOW_SCORE_THRESHOLD,           # §3.7 minimum score not cleared
    BELOW_MARGIN,                    # §3.7 margin not cleared, incl. §2.6's conflict
    CONTEXT_CHECK_FAILED,            # §3.5 pattern matched, required context absent
    CONTEXT_TRUNCATED,               # §3.5 check failed on context_truncated = true (§8.6)
    FIELD_NOT_IN_ACTIVE_SCHEMA,      # §3.6 check 1
    CITATION_ABSENT_FROM_EVIDENCE,   # §3.6 check 2
    NORMALIZATION_FAILED,            # §3.6 check 3
    CONTRADICTED_BY_STRONGER_FACT,   # §3.6 check 4
    MODEL_RETURNED_UNKNOWN,          # §3.6 — the model declined
    DISCOUNTED_TOOL_METADATA,        # the §2.2/§2.3 producer/creator discount fired
    PRIVACY_WITHHELD,                # P7's handling class forbids the model route (§8.4)
    BUDGET_DEFERRED,                 # §8.6 ceiling reached — never merged with abstention
)

#: §3.5's three routes, one named constant each. `direct` and `rule` are P6's own;
#: `llm` is P8's, and P6 records that it was tried without owning the call (§3.3).
#: The `_ROUTE` suffix is deliberate: `facts.states.DIRECT` (a reliability state) and
#: `facts.file_facts.RULE` (a fact origin) are different vocabularies that happen to
#: share a word, and four modules import two of the three.
DIRECT_ROUTE: str = "direct"
RULE_ROUTE: str = "rule"
LLM_ROUTE: str = "llm"

ATTEMPTED_PRODUCERS: tuple[str, str, str] = (DIRECT_ROUTE, RULE_ROUTE, LLM_ROUTE)

#: The two reasons that are NOT abstentions (B7, §8.6). A refusal for either of these
#: means the question was never answered on the evidence: the budget stopped the work,
#: or the privacy class forbade the only remaining route. §8.6: "If the budget is
#: exhausted, the product should retain extracted evidence, mark the deferred stage,
#: and leave the file or group in review rather than guessing", and reporting
#: "avoids the false impression that an unprocessed file was understood and found
#: unimportant". Reporting either of these as a considered refusal is that impression.
#:
#: This is a frozenset and not a tuple because it is asked `in` and never iterated for
#: order, and because P2's writer (`record_stage_output`) already enforces the
#: consequence -- outcome `deferred` requires budget_state `ceiling_reached`, and
#: `ceiling_reached` refuses outcome `abstained`. P6 does not re-implement that rule;
#: it names the two reasons that must not be routed into it as abstentions.
NOT_ABSTENTIONS: frozenset[str] = frozenset({BUDGET_DEFERRED, PRIVACY_WITHHELD})
```

- [ ] **Step 4: Add the `unresolved` table to `src/facts/schema.py`**

Task 4 owns this module's shape: one `<TABLE>_DDL` string per table and one tuple of them that
`create_facts_schema` executes. Append the constant below and add `UNRESOLVED_DDL` as the **last**
member of that tuple — `unresolved` references no other P6 table, so its position only has to be
after nothing.

```python
from database_agent.supersede import supersede_ddl

#: §3.6's abstention (B7). Every column here is in the SPEC's `unresolved` sketch, and
#: nothing else is:
#:
#:   - no `value_id` and no `reliability_state`. Not "nullable" -- ABSENT. A nullable
#:     column is a place someone later writes a value, and then the abstention is a
#:     weak `possible` and SPEC rule 1 is gone.
#:   - no path, destination, folder or group column: the same negative contract
#:     `file_facts` carries (§3.14, §4.3), checkable by reading this DDL alone.
#:   - `cache_key` has the same composition as `file_facts` (§3.4), so an abstention is
#:     invalidated by exactly the events that invalidate a fact -- which is what makes
#:     preamble rule 5's pass 4 supersede a pass-2 refusal instead of ignoring it.
#:
#: `record_id` is a VIRTUAL projection of `unresolved_id`, for the same reason P4's
#: `evidence` table carries one: P1's `mark_superseded` and `chain` are literally
#: `... WHERE record_id = ?`, so the projection lets P1's tested functions be reused
#: verbatim rather than written a second time under a second name. It stores nothing,
#: cannot diverge, and does not appear in `PRAGMA table_info`.
#:
#: No foreign key to `files`. P4 made the same choice for the same reason: P6 must be
#: buildable and testable against P4's nineteen fixtures with no scan, no extractor and
#: no `files` row in existence.
UNRESOLVED_DDL = f"""
CREATE TABLE IF NOT EXISTS unresolved (
    unresolved_id       TEXT PRIMARY KEY,
    file_id             TEXT NOT NULL,
    content_hash        TEXT NOT NULL,
    field_key            TEXT NOT NULL,
    reason              TEXT NOT NULL,
    attempted_producers TEXT NOT NULL,
    evidence_refs       TEXT NOT NULL,
    cache_key           TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    {supersede_ddl("unresolved")},
    record_id           TEXT GENERATED ALWAYS AS (unresolved_id) VIRTUAL
);
CREATE INDEX IF NOT EXISTS unresolved_by_version
    ON unresolved (file_id, content_hash);
"""
```

- [ ] **Step 5: Write `src/facts/unresolved.py`**

```python
# src/facts/unresolved.py
"""§3.6's abstention, as a ROW -- B7, Done-means 18 and 19.

§3.6 stops at "no fact": "A model that cannot cite sufficient evidence must return
unknown." §8.5 then asks, under Fact quality, "Did it abstain when evidence was
absent?" -- and an absent row cannot answer a question about absence. P2 cannot tell a
considered refusal from a crash, a skip, or a file that was never reached. So every
refusal P6 makes is recorded here, naming the field it attempted, the reason, the §3.5
routes it tried, and the observation keys it looked at.

Four properties make the row trustworthy, and each is a test rather than a comment:

  1. It is NOT a fact. No `value_id`, no reliability state -- absent from the schema,
     not merely null -- and absent from every fact read including the proposal-eligible
     one. A reader that treats it as a weaker `possible` has broken it.
  2. It obeys `file_facts`' negative contract: no path, destination, folder or group
     column (§3.14, §4.3). The forbidden-substring list is imported from `file_facts`
     rather than copied, so the two tables cannot drift.
  3. A later fact SUPERSEDES it and never deletes it (§8.2, §8.7). This module builds
     the affordance -- P1's three supersede columns and the `record_id` projection --
     and `facts/supersede.py` owns the operation.
  4. `budget_deferred` and `privacy_withheld` are NOT abstentions (§8.6). They are
     rows; they are not answers. `NOT_ABSTENTIONS` is published so a caller can make
     the distinction without a second copy of the rule.

The vocabularies are defined in `facts.vocabulary` -- one home for every closed set P6
owns -- and re-exported here because `facts.unresolved` is the address the rest of the
part imports them from.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Iterable, Sequence

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import check

from facts.fields import get_field
from facts.vocabulary import (
    ATTEMPTED_PRODUCERS, BELOW_MARGIN, BELOW_SCORE_THRESHOLD, BUDGET_DEFERRED,
    CITATION_ABSENT_FROM_EVIDENCE, CONTEXT_CHECK_FAILED, CONTEXT_TRUNCATED,
    CONTRADICTED_BY_STRONGER_FACT, DIRECT_ROUTE, DISCOUNTED_TOOL_METADATA,
    FIELD_NOT_IN_ACTIVE_SCHEMA, LLM_ROUTE, MODEL_RETURNED_UNKNOWN,
    NO_CANDIDATE_EVIDENCE, NORMALIZATION_FAILED, NOT_ABSTENTIONS, PRIVACY_WITHHELD,
    RULE_ROUTE, UNRESOLVED_REASONS,
)

#: The vocabularies are re-exported here, beside `write_unresolved`, because this is
#: the module preamble §3.4 publishes and a call site should import the reason it
#: passes from the same place as the writer it passes it to.
__all__ = [
    "ATTEMPTED_PRODUCERS",
    "BELOW_MARGIN",
    "BELOW_SCORE_THRESHOLD",
    "BUDGET_DEFERRED",
    "CITATION_ABSENT_FROM_EVIDENCE",
    "CONTEXT_CHECK_FAILED",
    "CONTEXT_TRUNCATED",
    "CONTRADICTED_BY_STRONGER_FACT",
    "DIRECT_ROUTE",
    "DISCOUNTED_TOOL_METADATA",
    "FIELD_NOT_IN_ACTIVE_SCHEMA",
    "LLM_ROUTE",
    "MODEL_RETURNED_UNKNOWN",
    "NOT_ABSTENTIONS",
    "NO_CANDIDATE_EVIDENCE",
    "NORMALIZATION_FAILED",
    "PRIVACY_WITHHELD",
    "RULE_ROUTE",
    "UNRESOLVED_REASONS",
    "unresolved_for_file",
    "write_unresolved",
]

#: An observation key is `sha256:`-prefixed (P4's `sha256_of`); an `observation_id` and
#: a content hash are not. The prefix is the whole difference between citing M14's
#: version-independent key and citing a row id that an extractor upgrade invalidates.
_KEY_PREFIX = "sha256:"


def _checked_field_key(conn: sqlite3.Connection, field_key: str) -> str:
    """The catalogue row's identity, resolved through Task 2's published reader.

    Named `_checked_` rather than `_field_key` because after brief §17 it takes a key
    and returns the same key: its whole value is the refusal on the way through.

    `get_field` raises `FieldNotInCatalogue` for a key the catalogue does not carry,
    which is §3.12 -- "it should not invent new fields automatically" -- enforced at
    the abstention row exactly as hard as at the fact row. A refusal naming a field
    that does not exist is not a refusal, it is a typo.
    """
    return get_field(conn, field_key)["field_key"]


def _required(value: str, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required and must be a non-empty string")
    return value


def _evidence_refs(refs: Iterable[str]) -> list[str]:
    """The observation keys considered, "where any were" -- the SPEC allows none.

    An empty list is stored as `[]` in a NOT NULL column, so "looked at nothing" is
    distinguishable from "column never written". Membership in `evidence` is NOT
    checked here: `observations_by_key` returns `[]` rather than raising for an unknown
    key, so a resolution check would need a policy for the empty result and that policy
    is Task 7's.
    """
    out: list[str] = []
    for ref in refs:
        _required(ref, name="evidence_ref")
        if not ref.startswith(_KEY_PREFIX):
            raise ValueError(
                f"evidence_refs entry {ref!r} is not a P4 observation key: every "
                f"citation is an `observation_key` and starts {_KEY_PREFIX!r} (M14). "
                "An `observation_id` or a row id does not survive an extractor "
                "version bump and is not a citation (§8.7)."
            )
        out.append(ref)
    return out


def _attempted(producers: Iterable[str]) -> list[str]:
    """Which §3.5 routes were tried. May be empty.

    An §8.6 ceiling can be reached BEFORE any producer runs, so requiring at least one
    would make `budget_deferred` -- the reason that most needs recording -- unwritable.
    """
    return [check(one, ATTEMPTED_PRODUCERS, name="attempted_producer")
            for one in producers]


def write_unresolved(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                     field_key: str, reason: str,
                     attempted_producers: Sequence[str],
                     evidence_refs: Sequence[str], cache_key: str) -> str:
    """Record one refusal. Returns the `unresolved_id`.

    Always an INSERT, never an update and never de-duplicated: two refusals for the
    same `(file_id, content_hash, field_key)` under two different §3.4 cache keys are
    two different events, and §8.2 keeps both readable.
    """
    _required(file_id, name="file_id")
    _required(content_hash, name="content_hash")
    _required(cache_key, name="cache_key")
    field_key = _checked_field_key(conn, field_key)
    check(reason, UNRESOLVED_REASONS, name="reason")
    producers = _attempted(attempted_producers)
    refs = _evidence_refs(evidence_refs)

    unresolved_id = uuid.uuid4().hex
    conn.execute(
        """
        INSERT INTO unresolved (
            unresolved_id, file_id, content_hash, field_key, reason,
            attempted_producers, evidence_refs, cache_key, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unresolved_id, file_id, content_hash, field_key, reason,
         canonical_json(producers), canonical_json(refs), cache_key,
         datetime.now(timezone.utc).isoformat()),
    )
    return unresolved_id


def unresolved_for_file(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
                        field_key: str | None = None,
                        reason: str | None = None) -> list[sqlite3.Row]:
    """Every refusal recorded for one file VERSION, superseded rows included.

    Superseded rows are returned deliberately: SPEC rule 3 says a later fact "does not
    delete the row -- it supersedes it, and the row remains readable as the record of
    what was once refused". A reader that wants only live refusals filters on
    `superseded_by IS NULL` itself; hiding them here would delete the history at the
    read instead of at the write, which is the same loss by a quieter route.

    The order is `(created_at, unresolved_id)` -- P6's own total order, never SQLite's
    insertion order. P4's reads are `ORDER BY rowid`, which is stable within one
    database and is not a property of the corpus, so §8.5's replay would compare a run
    against itself and report a difference.
    """
    clauses = ["file_id = ?", "content_hash = ?"]
    params: list[str] = [file_id, content_hash]
    if field_key is not None:
        clauses.append("field_key = ?")
        params.append(_checked_field_key(conn, field_key))
    if reason is not None:
        clauses.append("reason = ?")
        params.append(check(reason, UNRESOLVED_REASONS, name="reason"))
    return list(conn.execute(
        "SELECT * FROM unresolved WHERE " + " AND ".join(clauses)
        + " ORDER BY created_at, unresolved_id",
        params,
    ))
```

- [ ] **Step 6: Run the test and see it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_unresolved.py -q
```

**Expected:** `14 passed`. Then the whole part, to prove Task 4's table and Task 2's catalogue are
undisturbed by the schema edit:

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q && python3 -m pytest tests -q
```

**Expected:** every P6 test green, and the 1302 P1–P5 tests still green — P6 modified no file outside
`src/facts/` and `tests/p6/`.

- [ ] **Step 7: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/unresolved.py src/facts/vocabulary.py \
  src/facts/schema.py tests/p6/test_p6_unresolved.py && \
git commit -m "feat(P6): unresolved — the abstention is a row, and two of its thirteen reasons are not abstentions"
```

---

### Task 6: §3.4's cache key, and what invalidates a fact

**Files:**
- Create: `src/facts/cache.py`
- Test: `tests/p6/test_p6_cache.py`

**Interfaces:**
- Consumes: `evidence_shape.canonical.sha256_of`, `evidence_shape.canonical.canonical_json`,
  `evidence_shape.vocabulary.ANALYSIS_TIERS`, `evidence_shape.vocabulary.check`,
  `evidence_shape.runs.ExtractionRun`. P4's `evidence` and `extraction_runs` tables are read **by
  SQL**, importing no sibling — see *"the two derived parts"* below.
- Produces: `CACHE_KEY_PARTS: tuple[str, ...]` (`content_hash`, `extractor_version`, `analysis_tier`,
  `model_identifier`, `prompt_fingerprint`),
  `fact_cache_key(conn, *, file_id: str, content_hash: str, model_identifier: str | None,
  prompt_fingerprint: str | None) -> str`,
  `is_stale(conn, *, file_id, content_hash, cache_key) -> bool`.

**Done-means:** 15, 16.

#### The design sentence, grepped before it was quoted

`planning/00-database-agent-product-design.md`, one line, one occurrence:

> *"Each extraction result is tied to the content hash and the exact process that produced it. The
> cache key includes content hash, extractor version, analysis tier, model identifier when relevant,
> and prompt fingerprint for model-derived results. This prevents stale results from surviving a
> content rewrite, avoids unnecessary work when a file is merely renamed, and makes model or prompt
> changes auditable."*

Every one of Done-means 15 and 16 is in the third sentence. `CACHE_KEY_PARTS` is the second sentence
in the second sentence's order, and the third sentence is what `is_stale` has to make true:

| the design's clause | what it forces | which test |
|---|---|---|
| *"prevents stale results from surviving a content rewrite"* | a changed `content_hash` is a different key, so the old facts are outside the new slot | Done-means 16, second half |
| *"avoids unnecessary work when a file is merely renamed"* | there is **no path input** — not a nullable one, not an ignored one, none | Done-means 16, first half |
| *"makes model or prompt changes auditable"* | `model_identifier` and `prompt_fingerprint` are parts of the key, so a prompt change re-resolves and both keys stay readable | Done-means 15 |

#### The naming trap, verified live rather than remembered

`extractors.runs.cache_key` **already exists** and is a **different key answering a different
question**. Read from the installed source on 2026-08-22, not from P5's PLAN:

```python
def cache_key(*, content_hash: str, extractor_name: str, extractor_version: str,
              analysis_tier: str, config_fingerprint: str) -> str:
    return canonical_json([content_hash, extractor_name, extractor_version,
                           analysis_tier, config_fingerprint])
```

Three differences, and each of them matters:

- **Different identity.** P5's key identifies an **extraction result** — which extractor, at which
  configuration, produced these observations. P6's identifies a **fact** — which evidence, under
  which model and prompt, produced this conclusion. §3.4's sentence covers both because §3.2 has not
  yet split observation from fact at that point in the design; the two parts split it.
- **Different parts.** P5 carries `extractor_name` and `config_fingerprint`; P6 carries
  `model_identifier` and `prompt_fingerprint`. Neither list is a subset of the other, so neither
  function can be expressed in terms of the other without adding a part that its own question does
  not have.
- **Different return shape.** P5 returns `canonical_json([...])` — a JSON array string. P6 returns
  `sha256_of(...)` — a `sha256:`-prefixed digest, which is the form `file_facts.cache_key` and
  `unresolved.cache_key` store and the form the test at the end of Task 5 already passes
  (`"sha256:cache-native-1"`).

**So `facts` does not import P5's, and the test asserts that by runtime introspection** — no object
in `facts.cache`'s namespace is `extractors.runs.cache_key` and none is the `extractors.runs` module.
Not by searching source text: a text search matches comments and docstrings, and this document's own
docstring names `extractors.runs.cache_key` twice.

**And this is the second implementation of one design sentence, which is a fact about the plan and
not a defect in it.** It is recorded here so a later reviewer meets it as a decision rather than as a
surprise: the design describes one cache key; the built system has two functions, because P4's
observation/fact split gave the sentence two subjects. If they are ever reconciled, the reconciliation
is a P4/P5/P6 seam change and not an edit inside `facts.cache`.

#### The two derived parts — the settled rule, and it is not the one three drafts carried

**`facts.cache` is this task's module and no other task may add to it. This task publishes ONE
helper, `fact_cache_key`, and every producer imports it.** Eight sibling sections had written their
own private `_cache_key` copy of the reconciliation below; one copy is the rule, eight are eight
places for it to drift.

Two of §3.4's five parts are scalars and a file version has many of each — several extractors,
several analysis tiers. The reconciliation is **this function's**, not the caller's, and it is:

> `extractor_version` is `canonical_json` of the sorted distinct `[extractor_name,
> extractor_version]` pairs of **every observation of that file version** — *not* of the
> observations the fact happens to cite — and `analysis_tier` is the **last tier present** across
> the same set, in `ANALYSIS_TIERS` order (`filesystem` < `native` < `ocr` < `llm`). The key is
> therefore one key per **(file version, deterministic pass)**.

**The deciding argument is the abstention.** The SPEC gives `unresolved.cache_key` the *"same
composition as `file_facts` (§3.4), so an abstention is invalidated by the same events that
invalidate a fact"* — and **an abstention with no citations has no cited observations to compute a
key from**. A per-cited-observation rule cannot key the row that Done-means 18 and 19 exist for. One
key per pass answers both, and it is why `file_id` and `content_hash` are the inputs rather than a
set of observations: **a caller cannot hand this function a filtered subset**, which is the whole
defect the rule was written against.

It is also what makes preamble §3.3's supersession work. A later, richer pass adds observations at a
higher tier, so both derived parts move, so the pass lands in a **different cache slot** and
supersedes rather than overwrites (§8.2).

**The two derived parts are read by SQL, importing no sibling.** One query joins P4's `evidence` to
its `extraction_runs`:

```sql
SELECT DISTINCT e.extractor_name, e.extractor_version, r.analysis_tier
  FROM evidence e JOIN extraction_runs r ON r.run_id = e.run_id
 WHERE e.file_id = ? AND e.content_hash = ?
```

`facts.evidence.observations_for_version` answers the same question and this module does **not**
import it, for the reason `is_stale` does not import `facts.file_facts`: every Wave B producer
imports both this module and those, and a module that imports none of its siblings cannot be half of
an import cycle. Column names verified live on 2026-08-22 — `evidence` carries `extractor_name`,
`extractor_version`, `file_id`, `content_hash` and `run_id`; `extraction_runs` carries `run_id` and
`analysis_tier`.

**A file version with no observations at all is not an error.** It is the abstention's own case, and
it keys at `analysis_tier = ANALYSIS_TIERS[0]` with an empty pair list — a real slot, distinct from
every slot that has evidence in it, so an abstention recorded before any extractor ran is not
mistaken for work done after one did.

#### The three rulings this task makes

- **Each part is `canonical_json`-encoded before it is hashed, and that is what makes `None`
  distinguishable from `""`.** `sha256_of` is length-prefixed over `str` parts, so it is injective
  over the tuple it is given — but it takes strings, and `None` is not one. Encoding each part
  through `canonical_json` gives `None` → `null` and `""` → `""` (four characters, including the
  quotes), which are different strings of different lengths, so the digests differ. The skeleton
  calls this *"a property to assert rather than a hazard to avoid"*, and the test asserts it.
- **No coupling rule between `model_identifier` and `prompt_fingerprint` is invented.** §3.4 says
  *"model identifier when relevant"* and *"prompt fingerprint for model-derived results"* and states
  no dependency between them. A guard requiring both-or-neither would be a rule this plan authored,
  and P8 — which does not exist — is the part that would know whether it is true. Both are
  independently `str | None`. The **deterministic** case is the one this plan can assert, and it does:
  both are `None`, on every fact P6 produces with no model configured (Done-means 17).
- **`is_stale` reads `file_facts` and `unresolved`, by SQL, importing neither module.** Both halves
  are deliberate. It reads both because the SPEC's `unresolved` schema says `cache_key` has the
  *"same composition as `file_facts` (§3.4), so an abstention is invalidated by the same events that
  invalidate a fact"* — a file whose pass-2 produced only abstentions has had work done under that
  key, and a reader that saw only `file_facts` would call it stale forever and re-resolve it on every
  loop. It uses SQL rather than importing `facts.file_facts` and `facts.unresolved` because Task 6's
  `Consumes:` block lists neither, and because `direct.py`, `rules.py`, `facets.py`, `families.py`
  and `session.py` all import **both** `facts.cache` and `facts.file_facts` — keeping `facts.cache`
  free of its siblings is what guarantees no import cycle forms as Wave B lands in parallel.

#### What `is_stale` means, stated as one sentence and then as three cases

**`is_stale` is `True` unless at least one record for `(file_id, content_hash)` — a fact or an
abstention — was written under exactly this cache key.**

| case | records for `(file_id, content_hash)` | verdict | why that is right |
|---|---|---|---|
| a rename, content unchanged, same versions | facts under this same key | `False` | §3.4 *"avoids unnecessary work when a file is merely renamed"*. Done-means 16, first half |
| a content rewrite | none — the new `content_hash` is a new slot | `True` | §3.4 *"prevents stale results from surviving a content rewrite"*. Done-means 16, second half |
| a bumped extractor version or a changed prompt fingerprint | facts, but under the **old** key | `True` | Done-means 15 — re-resolution, and the new fact then supersedes the old one |

The "no records at all" case resolving to `True` is the same case as the content rewrite, and it is
the only reading that lets one predicate serve all three: a file version nothing has been computed
for is a file version that needs computing. **`is_stale` does not itself re-resolve, supersede, or
write anything** — Done-means 15's supersession is `facts/supersede.py`'s (Task 23) and the
sequencing is `facts/resolver.py`'s (Task 24). This function answers one question and returns a bool.

---

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_cache.py
"""§3.4 — Done-means 15 and 16. The five-part key, and what invalidates a fact.

"The cache key includes content hash, extractor version, analysis tier, model
identifier when relevant, and prompt fingerprint for model-derived results. This
prevents stale results from surviving a content rewrite, avoids unnecessary work when
a file is merely renamed, and makes model or prompt changes auditable."
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import get_run, record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

from extractors.runs import cache_key as extraction_cache_key

from facts import cache as cache_module
from facts.cache import CACHE_KEY_PARTS, fact_cache_key, is_stale
from facts.file_facts import RULE, write_fact
from facts.states import POSSIBLE, VALIDATED
from facts.unresolved import (
    DIRECT_ROUTE, NO_CANDIDATE_EVIDENCE, RULE_ROUTE, write_unresolved,
)
from facts.values import ensure_value

CLOCK = "2026-08-22T12:00:00+00:00"

#: The design's five parts, in the design's own order, spelled independently of the
#: module under test so the assertion is a comparison and not an echo.
DESIGN_FIVE = ("content_hash", "extractor_version", "analysis_tier",
               "model_identifier", "prompt_fingerprint")

#: The deterministic pass, spelled once. P6 contains no model call of any kind (§3.3),
#: so both model parts are None on every fact it writes; Task 17's LLM-supported fact
#: is the one place that is not true, and it passes real values here.
DETERMINISTIC = dict(model_identifier=None, prompt_fingerprint=None)


def _record(conn, tmp_path: Path, *, name: str, body: bytes) -> tuple[str, str]:
    """A real P1 file row, so this test never assumes whether `file_facts` carries a
    foreign key to `files`. Returns `(file_id, content_hash)`."""
    path = tmp_path / "corpus" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=path.suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, file_id: str, content_hash: str, raw: str = "BUSIB 4300",
             extractor: str = "pdf.text", version: str = "1.0.0",
             tier: str = "native") -> str:
    """One real P4 run and one observation inside it. Returns the observation key.

    The two derived parts of the key come from these rows and from nowhere else --
    that is the point of the settled rule, so every test here builds the evidence it
    wants the key to reflect rather than passing a keyword.
    """
    run_id = f"run-{extractor}-{version}-{tier}"
    if get_run(conn, run_id) is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name=extractor, extractor_version=version,
            source_type="text_document", analysis_tier=tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type="text_document", raw_value=raw,
        location=Location("heading", (Segment("page", 1), Segment("heading", 2))),
        occurrence_count=1, observed_at=CLOCK, reliability=POSSIBLE, run_id=run_id))
    return observation_key(content_hash=content_hash, extractor_name=extractor,
                           locator="heading:page=1/heading=2", raw_value=raw)


def _write_subject_fact(conn, *, file_id: str, content_hash: str, key: str,
                        ref: str) -> str:
    value_id = ensure_value(conn, field_key="subject", canonical_value="BUSIB 4300",
                            first_evidence_ref=ref, origin="automatic")
    # Task 4 owns the literal spelling of `rule` and publishes the named constant.
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value_id=value_id,
                      reliability_state=VALIDATED, origin=RULE,
                      evidence_refs=(ref,), cache_key=key, active=True)


def test_the_key_is_exactly_section_3_4s_five_parts(p6_conn):
    assert CACHE_KEY_PARTS == DESIGN_FIVE

    parameters = inspect.signature(fact_cache_key).parameters
    # Two of the five are DERIVED from every observation of the version, so they are
    # deliberately absent from the signature: a caller that could pass them could pass
    # a narrower set than the version has, which is the defect the rule forbids.
    assert "extractor_version" not in parameters
    assert "analysis_tier" not in parameters
    # The rest are the caller's, and none of them defaults. A defaulted part is a part
    # that silently stops distinguishing cache slots.
    assert tuple(parameters) == ("conn", "file_id", "content_hash",
                                 "model_identifier", "prompt_fingerprint")
    assert all(p.default is inspect.Parameter.empty for p in parameters.values())
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY
               for name, p in parameters.items() if name != "conn")


def test_the_key_is_over_every_observation_of_the_version_not_the_ones_a_fact_cited(
        p6_conn, tmp_path):
    """The settled rule, and the reason for it is the abstention.

    An `unresolved` row cites nothing, and the SPEC gives its `cache_key` the "same
    composition as `file_facts` (§3.4)". A per-cited-observation rule cannot key a row
    with no citations at all; one key per (file version, pass) keys both.
    """
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash)
    one_extractor = fact_cache_key(p6_conn, file_id=file_id,
                                   content_hash=content_hash, **DETERMINISTIC)

    # A second extractor sees the same version. No fact cites it; the key still moves,
    # because the key describes the PASS and the pass now knows more.
    _observe(p6_conn, file_id=file_id, content_hash=content_hash,
             extractor="pdf.metadata", raw="Columbia")
    two_extractors = fact_cache_key(p6_conn, file_id=file_id,
                                    content_hash=content_hash, **DETERMINISTIC)
    assert two_extractors != one_extractor

    # And the abstention, which has no citations, computes the same key as the facts
    # of the pass that wrote it.
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="purpose", reason=NO_CANDIDATE_EVIDENCE,
                     attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
                     evidence_refs=(), cache_key=two_extractors)
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=two_extractors) is False


def test_changing_any_one_part_changes_the_key(p6_conn, tmp_path):
    """Each of §3.4's five parts moves the key on its own -- the three derived ones
    through the evidence they are derived from."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash)
    baseline = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                              **DETERMINISTIC)
    keys = {baseline}

    # content_hash: a different version of the same file.
    other_id, other_hash = _record(p6_conn, tmp_path, name="Syllabus-v2.pdf",
                                   body=b"BUSIB 4300 revised")
    _observe(p6_conn, file_id=other_id, content_hash=other_hash)
    keys.add(fact_cache_key(p6_conn, file_id=other_id, content_hash=other_hash,
                            **DETERMINISTIC))

    # model_identifier and prompt_fingerprint: the caller's two.
    keys.add(fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                            model_identifier="claude-x/2026-08",
                            prompt_fingerprint=None))
    keys.add(fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                            model_identifier=None,
                            prompt_fingerprint="sha256:prompt-1"))
    assert len(keys) == 4

    # extractor_version: the same extractor, bumped.
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, version="2.0.0")
    bumped = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                            **DETERMINISTIC)
    assert bumped not in keys
    keys.add(bumped)

    # analysis_tier: an OCR run over the same version.
    _observe(p6_conn, file_id=file_id, content_hash=content_hash,
             extractor="pdf.ocr", tier="ocr")
    assert fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                          **DETERMINISTIC) not in keys

    assert baseline.startswith("sha256:")
    assert fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                          **DETERMINISTIC) == fact_cache_key(
        p6_conn, file_id=file_id, content_hash=content_hash, **DETERMINISTIC), (
        "the key is a pure function of what the database holds")


def test_a_rename_cannot_reach_the_key(p6_conn, tmp_path):
    """Done-means 16, first half, at the strongest place to assert it: the key has no
    path input at all -- not ignored, not nullable, absent. `file_id` scopes the read
    of P4's evidence; it is not one of §3.4's five parts and never reaches the digest.
    """
    parameters = inspect.signature(fact_cache_key).parameters
    for forbidden in ("path", "current_path", "filename", "directory_position"):
        assert forbidden not in parameters

    before = _record(p6_conn, tmp_path, name="Syllabus.pdf", body=b"BUSIB 4300")
    after = _record(p6_conn, tmp_path, name="renamed.pdf", body=b"BUSIB 4300")
    assert before[1] == after[1], "same bytes, same content hash (P1 R1)"
    for file_id, content_hash in (before, after):
        _observe(p6_conn, file_id=file_id, content_hash=content_hash)
    assert (fact_cache_key(p6_conn, file_id=before[0], content_hash=before[1],
                           **DETERMINISTIC)
            == fact_cache_key(p6_conn, file_id=after[0], content_hash=after[1],
                              **DETERMINISTIC))


def test_a_rename_triggers_no_re_resolution_and_a_content_change_does(p6_conn, tmp_path):
    """Done-means 16, end to end, through the fact table."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    ref = _observe(p6_conn, file_id=file_id, content_hash=content_hash)
    key = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                         **DETERMINISTIC)
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash,
                        key=key, ref=ref)

    # The rename: P1's identity is the content hash, so the row is the same row and
    # the key is the same key.
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=key) is False

    # The content rewrite: a new content hash is a new slot, and nothing has been
    # computed in it.
    rewritten_id, rewritten = _record(p6_conn, tmp_path, name="Syllabus-v2.pdf",
                                      body=b"BUSIB 4300 revised")
    assert rewritten != content_hash
    _observe(p6_conn, file_id=rewritten_id, content_hash=rewritten)
    rewritten_key = fact_cache_key(p6_conn, file_id=rewritten_id,
                                   content_hash=rewritten, **DETERMINISTIC)
    assert is_stale(p6_conn, file_id=rewritten_id, content_hash=rewritten,
                    cache_key=rewritten_key) is True


def test_a_bumped_extractor_version_re_resolves(p6_conn, tmp_path):
    """Done-means 15's trigger. The supersession itself is Task 23's."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    ref = _observe(p6_conn, file_id=file_id, content_hash=content_hash)
    old = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                         **DETERMINISTIC)
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash,
                        key=old, ref=ref)

    _observe(p6_conn, file_id=file_id, content_hash=content_hash, version="2.0.0")
    bumped = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                            **DETERMINISTIC)
    assert bumped != old
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=bumped) is True
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=old) is False


def test_a_changed_prompt_fingerprint_re_resolves(p6_conn, tmp_path):
    """§3.4's "makes model or prompt changes auditable" -- both keys stay computable,
    and the fact written under the old one stays readable."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Essay.pdf",
                                    body=b"Columbia")
    ref = _observe(p6_conn, file_id=file_id, content_hash=content_hash,
                   raw="Columbia")
    first = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                           model_identifier="model-a",
                           prompt_fingerprint="sha256:prompt-1")
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash,
                        key=first, ref=ref)
    second = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                            model_identifier="model-a",
                            prompt_fingerprint="sha256:prompt-2")
    assert first != second
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=second) is True


def test_none_is_distinguishable_from_the_empty_string(p6_conn, tmp_path):
    """P4's `sha256_of` is length-prefixed and injective, and each part is
    canonical_json-encoded before it is hashed, so `null` and `""` are different
    strings of different lengths. A property to assert, not a hazard to avoid."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Essay.pdf", body=b"C")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="Columbia")

    def key(**model) -> str:
        return fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                              **dict(DETERMINISTIC, **model))

    assert key(model_identifier=None) != key(model_identifier="")
    assert key(prompt_fingerprint=None) != key(prompt_fingerprint="")
    # And no two parts can be smeared into each other by concatenation.
    assert (key(model_identifier="ab", prompt_fingerprint="c")
            != key(model_identifier="a", prompt_fingerprint="bc"))


def test_the_deterministic_fact_carries_neither_model_part(p6_conn, tmp_path):
    """Done-means 17's half of this task: P8 is absent, so both are None and the key
    is still computable. P6 contains no model call of any kind (§3.3)."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Essay.pdf", body=b"C")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="Columbia")
    assert fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                          **DETERMINISTIC).startswith("sha256:")
    assert DETERMINISTIC["model_identifier"] is None
    assert DETERMINISTIC["prompt_fingerprint"] is None


def test_the_analysis_tier_is_the_last_tier_present_and_p4_refuses_a_fifth(p6_conn,
                                                                          tmp_path):
    """P6 never infers a tier -- it comes from P4's `ExtractionRun` (Global
    Constraints) -- and the one it uses is the LAST present in P4's order, which is
    what makes a richer pass land in a different slot (preamble §3.3)."""
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    file_id, content_hash = _record(p6_conn, tmp_path, name="Scan.pdf", body=b"scan")

    seen = []
    for tier in ANALYSIS_TIERS:
        _observe(p6_conn, file_id=file_id, content_hash=content_hash,
                 extractor=f"pdf.{tier}", tier=tier)
        seen.append(fact_cache_key(p6_conn, file_id=file_id,
                                   content_hash=content_hash, **DETERMINISTIC))
    assert len(set(seen)) == 4, "each richer pass is its own slot"

    # A fifth tier never reaches this module: P4 refuses it at the run.
    with pytest.raises(NotInVocabulary):
        record_run(p6_conn, ExtractionRun(
            run_id="run-bad", file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="ocr_v2", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))

    for empty in ("file_id", "content_hash"):
        with pytest.raises(ValueError):
            fact_cache_key(p6_conn, **dict(
                dict(file_id=file_id, content_hash=content_hash, **DETERMINISTIC),
                **{empty: ""}))


def test_a_version_with_no_evidence_yet_is_its_own_slot(p6_conn, tmp_path):
    """The abstention's own case: a refusal recorded before any extractor ran must
    not be mistaken for work done after one did."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Blank.pdf", body=b"   ")
    empty = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                           **DETERMINISTIC)
    assert empty.startswith("sha256:")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="   ")
    assert fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                          **DETERMINISTIC) != empty


def test_an_abstention_counts_as_work_done_under_that_key(p6_conn, tmp_path):
    """The SPEC's `unresolved.cache_key` is "same composition as `file_facts` (§3.4),
    so an abstention is invalidated by the same events that invalidate a fact". A
    reader that saw only `file_facts` would call a file that produced only refusals
    stale forever and re-resolve it on every loop."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Blank.pdf", body=b"   ")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="   ")
    key = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                         **DETERMINISTIC)
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason=NO_CANDIDATE_EVIDENCE,
                     attempted_producers=(DIRECT_ROUTE, RULE_ROUTE), evidence_refs=(),
                     cache_key=key)
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=key) is False
    _observe(p6_conn, file_id=file_id, content_hash=content_hash,
             extractor="pdf.ocr", tier="ocr", raw="   ")
    ocr = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                         **DETERMINISTIC)
    assert ocr != key
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=ocr) is True


def test_the_fact_key_is_not_p5s_extraction_key(p6_conn, tmp_path):
    """The naming trap. Two functions, two questions, one design sentence."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Essay.pdf", body=b"C")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="Columbia")
    mine = fact_cache_key(p6_conn, file_id=file_id, content_hash=content_hash,
                          **DETERMINISTIC)
    theirs = extraction_cache_key(content_hash=content_hash,
                                  extractor_name="pdf.text",
                                  extractor_version="1.0.0",
                                  analysis_tier="native",
                                  config_fingerprint="sha256:config-1")
    assert mine != theirs

    ours = set(inspect.signature(fact_cache_key).parameters)
    p5 = set(inspect.signature(extraction_cache_key).parameters)
    assert "extractor_name" not in ours and "config_fingerprint" not in ours
    assert "model_identifier" not in p5 and "prompt_fingerprint" not in p5

    # Runtime introspection, not a source-text search: this file's own docstrings
    # name `extractors.runs.cache_key` and a text guard would match them.
    namespace = vars(cache_module).values()
    assert not any(one is extraction_cache_key for one in namespace)
    assert not any(getattr(one, "__name__", "") == "extractors.runs"
                   for one in namespace)
```

- [ ] **Step 2: Run the test and see it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_unresolved.py -x -q
```

**Expected failure:** collection fails before a single test runs —
`ModuleNotFoundError: No module named 'facts.unresolved'`. `src/facts/unresolved.py` does not exist,
so every one of the fourteen tests errors at import. This is the failure to see; a failure inside a
test body at this step would mean the module already existed and the task is mis-scoped.

- [ ] **Step 3: Append P6's third and fourth closed vocabularies to `src/facts/vocabulary.py`**

Task 2 created this module and owns everything already in it (`FIELD_SCOPES` and the field-scope
checks). Append the block below **unchanged**; edit nothing above it. The reasons and the producers
live here rather than in `unresolved.py` because the Global Constraints put P6's closed vocabularies
in **one** module, checked with P4's `check` — the same rule that keeps `FIELD_SCOPES` here.

```python
# ---------------------------------------------------------------------------
# Task 5 — the abstention vocabularies (§3.6, §8.5, §8.6; B7)
# ---------------------------------------------------------------------------

#: The thirteen reasons, one named constant each. This module owns the literal
#: spelling; every call site imports the CONSTANT (preamble §3.1). That
#: `write_unresolved` validates the reason through P4's `check` -- so a misspelling
#: raises `NotInVocabulary` rather than storing -- is true and worth knowing, and it
#: is NOT a reason to spell the reason inline: validation at the seam catches a TYPO,
#: it does not stop the literal being a SECOND HOME.
NO_CANDIDATE_EVIDENCE: str = "no_candidate_evidence"
BELOW_SCORE_THRESHOLD: str = "below_score_threshold"
BELOW_MARGIN: str = "below_margin"
CONTEXT_CHECK_FAILED: str = "context_check_failed"
CONTEXT_TRUNCATED: str = "context_truncated"
FIELD_NOT_IN_ACTIVE_SCHEMA: str = "field_not_in_active_schema"
CITATION_ABSENT_FROM_EVIDENCE: str = "citation_absent_from_evidence"
NORMALIZATION_FAILED: str = "normalization_failed"
CONTRADICTED_BY_STRONGER_FACT: str = "contradicted_by_stronger_fact"
MODEL_RETURNED_UNKNOWN: str = "model_returned_unknown"
DISCOUNTED_TOOL_METADATA: str = "discounted_tool_metadata"
PRIVACY_WITHHELD: str = "privacy_withheld"
BUDGET_DEFERRED: str = "budget_deferred"

#: The thirteen in the SPEC's own table order, for iteration and membership. Each is
#: fired by exactly one place, named in the comment beside it, so a reason with no
#: producer or a producer with no reason is visible by reading this list. To NAME one
#: reason, import the constant above -- never a literal, never an index.
UNRESOLVED_REASONS: tuple[str, ...] = (
    NO_CANDIDATE_EVIDENCE,           # no observation offered a candidate (§3.6)
    BELOW_SCORE_THRESHOLD,           # §3.7 minimum score not cleared
    BELOW_MARGIN,                    # §3.7 margin not cleared, incl. §2.6's conflict
    CONTEXT_CHECK_FAILED,            # §3.5 pattern matched, required context absent
    CONTEXT_TRUNCATED,               # §3.5 check failed on context_truncated = true (§8.6)
    FIELD_NOT_IN_ACTIVE_SCHEMA,      # §3.6 check 1
    CITATION_ABSENT_FROM_EVIDENCE,   # §3.6 check 2
    NORMALIZATION_FAILED,            # §3.6 check 3
    CONTRADICTED_BY_STRONGER_FACT,   # §3.6 check 4
    MODEL_RETURNED_UNKNOWN,          # §3.6 — the model declined
    DISCOUNTED_TOOL_METADATA,        # the §2.2/§2.3 producer/creator discount fired
    PRIVACY_WITHHELD,                # P7's handling class forbids the model route (§8.4)
    BUDGET_DEFERRED,                 # §8.6 ceiling reached — never merged with abstention
)

#: §3.5's three routes, one named constant each. `direct` and `rule` are P6's own;
#: `llm` is P8's, and P6 records that it was tried without owning the call (§3.3).
#: The `_ROUTE` suffix is deliberate: `facts.states.DIRECT` (a reliability state) and
#: `facts.file_facts.RULE` (a fact origin) are different vocabularies that happen to
#: share a word, and four modules import two of the three.
DIRECT_ROUTE: str = "direct"
RULE_ROUTE: str = "rule"
LLM_ROUTE: str = "llm"

ATTEMPTED_PRODUCERS: tuple[str, str, str] = (DIRECT_ROUTE, RULE_ROUTE, LLM_ROUTE)

#: The two reasons that are NOT abstentions (B7, §8.6). A refusal for either of these
#: means the question was never answered on the evidence: the budget stopped the work,
#: or the privacy class forbade the only remaining route. §8.6: "If the budget is
#: exhausted, the product should retain extracted evidence, mark the deferred stage,
#: and leave the file or group in review rather than guessing", and reporting
#: "avoids the false impression that an unprocessed file was understood and found
#: unimportant". Reporting either of these as a considered refusal is that impression.
#:
#: This is a frozenset and not a tuple because it is asked `in` and never iterated for
#: order, and because P2's writer (`record_stage_output`) already enforces the
#: consequence -- outcome `deferred` requires budget_state `ceiling_reached`, and
#: `ceiling_reached` refuses outcome `abstained`. P6 does not re-implement that rule;
#: it names the two reasons that must not be routed into it as abstentions.
NOT_ABSTENTIONS: frozenset[str] = frozenset({BUDGET_DEFERRED, PRIVACY_WITHHELD})
```

- [ ] **Step 4: Add the `unresolved` table to `src/facts/schema.py`**

Task 4 owns this module's shape: one `<TABLE>_DDL` string per table and one tuple of them that
`create_facts_schema` executes. Append the constant below and add `UNRESOLVED_DDL` as the **last**
member of that tuple — `unresolved` references no other P6 table, so its position only has to be
after nothing.

```python
from database_agent.supersede import supersede_ddl

#: §3.6's abstention (B7). Every column here is in the SPEC's `unresolved` sketch, and
#: nothing else is:
#:
#:   - no `value_id` and no `reliability_state`. Not "nullable" -- ABSENT. A nullable
#:     column is a place someone later writes a value, and then the abstention is a
#:     weak `possible` and SPEC rule 1 is gone.
#:   - no path, destination, folder or group column: the same negative contract
#:     `file_facts` carries (§3.14, §4.3), checkable by reading this DDL alone.
#:   - `cache_key` has the same composition as `file_facts` (§3.4), so an abstention is
#:     invalidated by exactly the events that invalidate a fact -- which is what makes
#:     preamble rule 5's pass 4 supersede a pass-2 refusal instead of ignoring it.
#:
#: `record_id` is a VIRTUAL projection of `unresolved_id`, for the same reason P4's
#: `evidence` table carries one: P1's `mark_superseded` and `chain` are literally
#: `... WHERE record_id = ?`, so the projection lets P1's tested functions be reused
#: verbatim rather than written a second time under a second name. It stores nothing,
#: cannot diverge, and does not appear in `PRAGMA table_info`.
#:
#: No foreign key to `files`. P4 made the same choice for the same reason: P6 must be
#: buildable and testable against P4's nineteen fixtures with no scan, no extractor and
#: no `files` row in existence.
UNRESOLVED_DDL = f"""
CREATE TABLE IF NOT EXISTS unresolved (
    unresolved_id       TEXT PRIMARY KEY,
    file_id             TEXT NOT NULL,
    content_hash        TEXT NOT NULL,
    field_key            TEXT NOT NULL,
    reason              TEXT NOT NULL,
    attempted_producers TEXT NOT NULL,
    evidence_refs       TEXT NOT NULL,
    cache_key           TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    {supersede_ddl("unresolved")},
    record_id           TEXT GENERATED ALWAYS AS (unresolved_id) VIRTUAL
);
CREATE INDEX IF NOT EXISTS unresolved_by_version
    ON unresolved (file_id, content_hash);
"""
```

- [ ] **Step 5: Write `src/facts/unresolved.py`**

```python
# src/facts/unresolved.py
"""§3.6's abstention, as a ROW -- B7, Done-means 18 and 19.

§3.6 stops at "no fact": "A model that cannot cite sufficient evidence must return
unknown." §8.5 then asks, under Fact quality, "Did it abstain when evidence was
absent?" -- and an absent row cannot answer a question about absence. P2 cannot tell a
considered refusal from a crash, a skip, or a file that was never reached. So every
refusal P6 makes is recorded here, naming the field it attempted, the reason, the §3.5
routes it tried, and the observation keys it looked at.

Four properties make the row trustworthy, and each is a test rather than a comment:

  1. It is NOT a fact. No `value_id`, no reliability state -- absent from the schema,
     not merely null -- and absent from every fact read including the proposal-eligible
     one. A reader that treats it as a weaker `possible` has broken it.
  2. It obeys `file_facts`' negative contract: no path, destination, folder or group
     column (§3.14, §4.3). The forbidden-substring list is imported from `file_facts`
     rather than copied, so the two tables cannot drift.
  3. A later fact SUPERSEDES it and never deletes it (§8.2, §8.7). This module builds
     the affordance -- P1's three supersede columns and the `record_id` projection --
     and `facts/supersede.py` owns the operation.
  4. `budget_deferred` and `privacy_withheld` are NOT abstentions (§8.6). They are
     rows; they are not answers. `NOT_ABSTENTIONS` is published so a caller can make
     the distinction without a second copy of the rule.

The vocabularies are defined in `facts.vocabulary` -- one home for every closed set P6
owns -- and re-exported here because `facts.unresolved` is the address the rest of the
part imports them from.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Iterable, Sequence

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import check

from facts.fields import get_field
from facts.vocabulary import (
    ATTEMPTED_PRODUCERS, BELOW_MARGIN, BELOW_SCORE_THRESHOLD, BUDGET_DEFERRED,
    CITATION_ABSENT_FROM_EVIDENCE, CONTEXT_CHECK_FAILED, CONTEXT_TRUNCATED,
    CONTRADICTED_BY_STRONGER_FACT, DIRECT_ROUTE, DISCOUNTED_TOOL_METADATA,
    FIELD_NOT_IN_ACTIVE_SCHEMA, LLM_ROUTE, MODEL_RETURNED_UNKNOWN,
    NO_CANDIDATE_EVIDENCE, NORMALIZATION_FAILED, NOT_ABSTENTIONS, PRIVACY_WITHHELD,
    RULE_ROUTE, UNRESOLVED_REASONS,
)

#: The vocabularies are re-exported here, beside `write_unresolved`, because this is
#: the module preamble §3.4 publishes and a call site should import the reason it
#: passes from the same place as the writer it passes it to.
__all__ = [
    "ATTEMPTED_PRODUCERS",
    "BELOW_MARGIN",
    "BELOW_SCORE_THRESHOLD",
    "BUDGET_DEFERRED",
    "CITATION_ABSENT_FROM_EVIDENCE",
    "CONTEXT_CHECK_FAILED",
    "CONTEXT_TRUNCATED",
    "CONTRADICTED_BY_STRONGER_FACT",
    "DIRECT_ROUTE",
    "DISCOUNTED_TOOL_METADATA",
    "FIELD_NOT_IN_ACTIVE_SCHEMA",
    "LLM_ROUTE",
    "MODEL_RETURNED_UNKNOWN",
    "NOT_ABSTENTIONS",
    "NO_CANDIDATE_EVIDENCE",
    "NORMALIZATION_FAILED",
    "PRIVACY_WITHHELD",
    "RULE_ROUTE",
    "UNRESOLVED_REASONS",
    "unresolved_for_file",
    "write_unresolved",
]

#: An observation key is `sha256:`-prefixed (P4's `sha256_of`); an `observation_id` and
#: a content hash are not. The prefix is the whole difference between citing M14's
#: version-independent key and citing a row id that an extractor upgrade invalidates.
_KEY_PREFIX = "sha256:"


def _checked_field_key(conn: sqlite3.Connection, field_key: str) -> str:
    """The catalogue row's identity, resolved through Task 2's published reader.

    Named `_checked_` rather than `_field_key` because after brief §17 it takes a key
    and returns the same key: its whole value is the refusal on the way through.

    `get_field` raises `FieldNotInCatalogue` for a key the catalogue does not carry,
    which is §3.12 -- "it should not invent new fields automatically" -- enforced at
    the abstention row exactly as hard as at the fact row. A refusal naming a field
    that does not exist is not a refusal, it is a typo.
    """
    return get_field(conn, field_key)["field_key"]


def _required(value: str, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required and must be a non-empty string")
    return value


def _evidence_refs(refs: Iterable[str]) -> list[str]:
    """The observation keys considered, "where any were" -- the SPEC allows none.

    An empty list is stored as `[]` in a NOT NULL column, so "looked at nothing" is
    distinguishable from "column never written". Membership in `evidence` is NOT
    checked here: `observations_by_key` returns `[]` rather than raising for an unknown
    key, so a resolution check would need a policy for the empty result and that policy
    is Task 7's.
    """
    out: list[str] = []
    for ref in refs:
        _required(ref, name="evidence_ref")
        if not ref.startswith(_KEY_PREFIX):
            raise ValueError(
                f"evidence_refs entry {ref!r} is not a P4 observation key: every "
                f"citation is an `observation_key` and starts {_KEY_PREFIX!r} (M14). "
                "An `observation_id` or a row id does not survive an extractor "
                "version bump and is not a citation (§8.7)."
            )
        out.append(ref)
    return out


def _attempted(producers: Iterable[str]) -> list[str]:
    """Which §3.5 routes were tried. May be empty.

    An §8.6 ceiling can be reached BEFORE any producer runs, so requiring at least one
    would make `budget_deferred` -- the reason that most needs recording -- unwritable.
    """
    return [check(one, ATTEMPTED_PRODUCERS, name="attempted_producer")
            for one in producers]


def write_unresolved(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                     field_key: str, reason: str,
                     attempted_producers: Sequence[str],
                     evidence_refs: Sequence[str], cache_key: str) -> str:
    """Record one refusal. Returns the `unresolved_id`.

    Always an INSERT, never an update and never de-duplicated: two refusals for the
    same `(file_id, content_hash, field_key)` under two different §3.4 cache keys are
    two different events, and §8.2 keeps both readable.
    """
    _required(file_id, name="file_id")
    _required(content_hash, name="content_hash")
    _required(cache_key, name="cache_key")
    field_key = _checked_field_key(conn, field_key)
    check(reason, UNRESOLVED_REASONS, name="reason")
    producers = _attempted(attempted_producers)
    refs = _evidence_refs(evidence_refs)

    unresolved_id = uuid.uuid4().hex
    conn.execute(
        """
        INSERT INTO unresolved (
            unresolved_id, file_id, content_hash, field_key, reason,
            attempted_producers, evidence_refs, cache_key, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unresolved_id, file_id, content_hash, field_key, reason,
         canonical_json(producers), canonical_json(refs), cache_key,
         datetime.now(timezone.utc).isoformat()),
    )
    return unresolved_id


def unresolved_for_file(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
                        field_key: str | None = None,
                        reason: str | None = None) -> list[sqlite3.Row]:
    """Every refusal recorded for one file VERSION, superseded rows included.

    Superseded rows are returned deliberately: SPEC rule 3 says a later fact "does not
    delete the row -- it supersedes it, and the row remains readable as the record of
    what was once refused". A reader that wants only live refusals filters on
    `superseded_by IS NULL` itself; hiding them here would delete the history at the
    read instead of at the write, which is the same loss by a quieter route.

    The order is `(created_at, unresolved_id)` -- P6's own total order, never SQLite's
    insertion order. P4's reads are `ORDER BY rowid`, which is stable within one
    database and is not a property of the corpus, so §8.5's replay would compare a run
    against itself and report a difference.
    """
    clauses = ["file_id = ?", "content_hash = ?"]
    params: list[str] = [file_id, content_hash]
    if field_key is not None:
        clauses.append("field_key = ?")
        params.append(_checked_field_key(conn, field_key))
    if reason is not None:
        clauses.append("reason = ?")
        params.append(check(reason, UNRESOLVED_REASONS, name="reason"))
    return list(conn.execute(
        "SELECT * FROM unresolved WHERE " + " AND ".join(clauses)
        + " ORDER BY created_at, unresolved_id",
        params,
    ))
```

- [ ] **Step 6: Run the test and see it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_unresolved.py -q
```

**Expected:** `14 passed`. Then the whole part, to prove Task 4's table and Task 2's catalogue are
undisturbed by the schema edit:

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q && python3 -m pytest tests -q
```

**Expected:** every P6 test green, and the 1302 P1–P5 tests still green — P6 modified no file outside
`src/facts/` and `tests/p6/`.

- [ ] **Step 7: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/unresolved.py src/facts/vocabulary.py \
  src/facts/schema.py tests/p6/test_p6_unresolved.py && \
git commit -m "feat(P6): unresolved — the abstention is a row, and two of its thirteen reasons are not abstentions"
```

---

### Task 6: §3.4's cache key, and what invalidates a fact

**Files:**
- Create: `src/facts/cache.py`
- Test: `tests/p6/test_p6_cache.py`

**Interfaces:**
- Consumes: `evidence_shape.canonical.sha256_of`, `evidence_shape.canonical.canonical_json`,
  `evidence_shape.vocabulary.ANALYSIS_TIERS`, `evidence_shape.vocabulary.check`,
  `evidence_shape.runs.ExtractionRun`. P4's `evidence` and `extraction_runs` tables are read **by
  SQL**, importing no sibling — see *"the two derived parts"* below.
- Produces: `CACHE_KEY_PARTS: tuple[str, ...]` (`content_hash`, `extractor_version`, `analysis_tier`,
  `model_identifier`, `prompt_fingerprint`),
  `fact_cache_key(conn, *, file_id: str, content_hash: str, model_identifier: str | None,
  prompt_fingerprint: str | None) -> str`,
  `is_stale(conn, *, file_id, content_hash, cache_key) -> bool`.

**Done-means:** 15, 16.

#### The design sentence, grepped before it was quoted

`planning/00-database-agent-product-design.md`, one line, one occurrence:

> *"Each extraction result is tied to the content hash and the exact process that produced it. The
> cache key includes content hash, extractor version, analysis tier, model identifier when relevant,
> and prompt fingerprint for model-derived results. This prevents stale results from surviving a
> content rewrite, avoids unnecessary work when a file is merely renamed, and makes model or prompt
> changes auditable."*

Every one of Done-means 15 and 16 is in the third sentence. `CACHE_KEY_PARTS` is the second sentence
in the second sentence's order, and the third sentence is what `is_stale` has to make true:

| the design's clause | what it forces | which test |
|---|---|---|
| *"prevents stale results from surviving a content rewrite"* | a changed `content_hash` is a different key, so the old facts are outside the new slot | Done-means 16, second half |
| *"avoids unnecessary work when a file is merely renamed"* | there is **no path input** — not a nullable one, not an ignored one, none | Done-means 16, first half |
| *"makes model or prompt changes auditable"* | `model_identifier` and `prompt_fingerprint` are parts of the key, so a prompt change re-resolves and both keys stay readable | Done-means 15 |

#### The naming trap, verified live rather than remembered

`extractors.runs.cache_key` **already exists** and is a **different key answering a different
question**. Read from the installed source on 2026-08-22, not from P5's PLAN:

```python
def cache_key(*, content_hash: str, extractor_name: str, extractor_version: str,
              analysis_tier: str, config_fingerprint: str) -> str:
    return canonical_json([content_hash, extractor_name, extractor_version,
                           analysis_tier, config_fingerprint])
```

Three differences, and each of them matters:

- **Different identity.** P5's key identifies an **extraction result** — which extractor, at which
  configuration, produced these observations. P6's identifies a **fact** — which evidence, under
  which model and prompt, produced this conclusion. §3.4's sentence covers both because §3.2 has not
  yet split observation from fact at that point in the design; the two parts split it.
- **Different parts.** P5 carries `extractor_name` and `config_fingerprint`; P6 carries
  `model_identifier` and `prompt_fingerprint`. Neither list is a subset of the other, so neither
  function can be expressed in terms of the other without adding a part that its own question does
  not have.
- **Different return shape.** P5 returns `canonical_json([...])` — a JSON array string. P6 returns
  `sha256_of(...)` — a `sha256:`-prefixed digest, which is the form `file_facts.cache_key` and
  `unresolved.cache_key` store and the form the test at the end of Task 5 already passes
  (`"sha256:cache-native-1"`).

**So `facts` does not import P5's, and the test asserts that by runtime introspection** — no object
in `facts.cache`'s namespace is `extractors.runs.cache_key` and none is the `extractors.runs` module.
Not by searching source text: a text search matches comments and docstrings, and this document's own
docstring names `extractors.runs.cache_key` twice.

**And this is the second implementation of one design sentence, which is a fact about the plan and
not a defect in it.** It is recorded here so a later reviewer meets it as a decision rather than as a
surprise: the design describes one cache key; the built system has two functions, because P4's
observation/fact split gave the sentence two subjects. If they are ever reconciled, the reconciliation
is a P4/P5/P6 seam change and not an edit inside `facts.cache`.

#### The two derived parts — the settled rule, and it is not the one three drafts carried

**`facts.cache` is this task's module and no other task may add to it. This task publishes ONE
helper, `fact_cache_key`, and every producer imports it.** Eight sibling sections had written their
own private `_cache_key` copy of the reconciliation below; one copy is the rule, eight are eight
places for it to drift.

Two of §3.4's five parts are scalars and a file version has many of each — several extractors,
several analysis tiers. The reconciliation is **this function's**, not the caller's, and it is:

> `extractor_version` is `canonical_json` of the sorted distinct `[extractor_name,
> extractor_version]` pairs of **every observation of that file version** — *not* of the
> observations the fact happens to cite — and `analysis_tier` is the **last tier present** across
> the same set, in `ANALYSIS_TIERS` order (`filesystem` < `native` < `ocr` < `llm`). The key is
> therefore one key per **(file version, deterministic pass)**.

**The deciding argument is the abstention.** The SPEC gives `unresolved.cache_key` the *"same
composition as `file_facts` (§3.4), so an abstention is invalidated by the same events that
invalidate a fact"* — and **an abstention with no citations has no cited observations to compute a
key from**. A per-cited-observation rule cannot key the row that Done-means 18 and 19 exist for. One
key per pass answers both, and it is why `file_id` and `content_hash` are the inputs rather than a
set of observations: **a caller cannot hand this function a filtered subset**, which is the whole
defect the rule was written against.

It is also what makes preamble §3.3's supersession work. A later, richer pass adds observations at a
higher tier, so both derived parts move, so the pass lands in a **different cache slot** and
supersedes rather than overwrites (§8.2).

**The two derived parts are read by SQL, importing no sibling.** One query joins P4's `evidence` to
its `extraction_runs`:

```sql
SELECT DISTINCT e.extractor_name, e.extractor_version, r.analysis_tier
  FROM evidence e JOIN extraction_runs r ON r.run_id = e.run_id
 WHERE e.file_id = ? AND e.content_hash = ?
```

`facts.evidence.observations_for_version` answers the same question and this module does **not**
import it, for the reason `is_stale` does not import `facts.file_facts`: every Wave B producer
imports both this module and those, and a module that imports none of its siblings cannot be half of
an import cycle. Column names verified live on 2026-08-22 — `evidence` carries `extractor_name`,
`extractor_version`, `file_id`, `content_hash` and `run_id`; `extraction_runs` carries `run_id` and
`analysis_tier`.

**A file version with no observations at all is not an error.** It is the abstention's own case, and
it keys at `analysis_tier = ANALYSIS_TIERS[0]` with an empty pair list — a real slot, distinct from
every slot that has evidence in it, so an abstention recorded before any extractor ran is not
mistaken for work done after one did.

#### The three rulings this task makes

- **Each part is `canonical_json`-encoded before it is hashed, and that is what makes `None`
  distinguishable from `""`.** `sha256_of` is length-prefixed over `str` parts, so it is injective
  over the tuple it is given — but it takes strings, and `None` is not one. Encoding each part
  through `canonical_json` gives `None` → `null` and `""` → `""` (four characters, including the
  quotes), which are different strings of different lengths, so the digests differ. The skeleton
  calls this *"a property to assert rather than a hazard to avoid"*, and the test asserts it.
- **No coupling rule between `model_identifier` and `prompt_fingerprint` is invented.** §3.4 says
  *"model identifier when relevant"* and *"prompt fingerprint for model-derived results"* and states
  no dependency between them. A guard requiring both-or-neither would be a rule this plan authored,
  and P8 — which does not exist — is the part that would know whether it is true. Both are
  independently `str | None`. The **deterministic** case is the one this plan can assert, and it does:
  both are `None`, on every fact P6 produces with no model configured (Done-means 17).
- **`is_stale` reads `file_facts` and `unresolved`, by SQL, importing neither module.** Both halves
  are deliberate. It reads both because the SPEC's `unresolved` schema says `cache_key` has the
  *"same composition as `file_facts` (§3.4), so an abstention is invalidated by the same events that
  invalidate a fact"* — a file whose pass-2 produced only abstentions has had work done under that
  key, and a reader that saw only `file_facts` would call it stale forever and re-resolve it on every
  loop. It uses SQL rather than importing `facts.file_facts` and `facts.unresolved` because Task 6's
  `Consumes:` block lists neither, and because `direct.py`, `rules.py`, `facets.py`, `families.py`
  and `session.py` all import **both** `facts.cache` and `facts.file_facts` — keeping `facts.cache`
  free of its siblings is what guarantees no import cycle forms as Wave B lands in parallel.

#### What `is_stale` means, stated as one sentence and then as three cases

**`is_stale` is `True` unless at least one record for `(file_id, content_hash)` — a fact or an
abstention — was written under exactly this cache key.**

| case | records for `(file_id, content_hash)` | verdict | why that is right |
|---|---|---|---|
| a rename, content unchanged, same versions | facts under this same key | `False` | §3.4 *"avoids unnecessary work when a file is merely renamed"*. Done-means 16, first half |
| a content rewrite | none — the new `content_hash` is a new slot | `True` | §3.4 *"prevents stale results from surviving a content rewrite"*. Done-means 16, second half |
| a bumped extractor version or a changed prompt fingerprint | facts, but under the **old** key | `True` | Done-means 15 — re-resolution, and the new fact then supersedes the old one |

The "no records at all" case resolving to `True` is the same case as the content rewrite, and it is
the only reading that lets one predicate serve all three: a file version nothing has been computed
for is a file version that needs computing. **`is_stale` does not itself re-resolve, supersede, or
write anything** — Done-means 15's supersession is `facts/supersede.py`'s (Task 23) and the
sequencing is `facts/resolver.py`'s (Task 24). This function answers one question and returns a bool.

---

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_cache.py
"""§3.4 — Done-means 15 and 16. The five-part key, and what invalidates a fact.

"The cache key includes content hash, extractor version, analysis tier, model
identifier when relevant, and prompt fingerprint for model-derived results. This
prevents stale results from surviving a content rewrite, avoids unnecessary work when
a file is merely renamed, and makes model or prompt changes auditable."
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import get_run, record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

from extractors.runs import cache_key as extraction_cache_key

from facts import cache as cache_module
from facts.cache import CACHE_KEY_PARTS, fact_cache_key, is_stale
from facts.file_facts import RULE, write_fact
from facts.states import POSSIBLE, VALIDATED
from facts.unresolved import (
    DIRECT_ROUTE, NO_CANDIDATE_EVIDENCE, RULE_ROUTE, write_unresolved,
)
from facts.values import ensure_value

CLOCK = "2026-08-22T12:00:00+00:00"

#: The design's five parts, in the design's own order, spelled independently of the
#: module under test so the assertion is a comparison and not an echo.
DESIGN_FIVE = ("content_hash", "extractor_version", "analysis_tier",
               "model_identifier", "prompt_fingerprint")

#: One deterministic baseline. `model_identifier` and `prompt_fingerprint` are None
#: because P6 contains no model call of any kind (§3.3) and P8 does not exist.
BASELINE = dict(content_hash="a" * 64, extractor_version="1.0.0",
                analysis_tier="native", model_identifier=None,
                prompt_fingerprint=None)


def _record(conn, tmp_path: Path, *, name: str, body: bytes) -> tuple[str, str]:
    """A real P1 file row, so this test never assumes whether `file_facts` carries a
    foreign key to `files`. Returns `(file_id, content_hash)`."""
    path = tmp_path / "corpus" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=path.suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _write_subject_fact(conn, *, file_id: str, content_hash: str, key: str) -> str:
    ref = observation_key(content_hash=content_hash, extractor_name="pdf.text",
                          locator="heading:page=1/heading=2", raw_value="BUSIB 4300")
    value_id = ensure_value(conn, field_key="subject", canonical_value="BUSIB 4300",
                            first_evidence_ref=ref, origin="automatic")
    # Task 4 owns the literal spelling of `rule` and publishes the named constant.
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value_id=value_id,
                      reliability_state=VALIDATED, origin=RULE,
                      evidence_refs=(ref,), cache_key=key, active=True)


def test_the_key_is_exactly_section_3_4s_five_parts(p6_conn):
    assert CACHE_KEY_PARTS == DESIGN_FIVE
    parameters = inspect.signature(fact_cache_key).parameters
    assert tuple(parameters) == CACHE_KEY_PARTS
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in parameters.values())
    assert all(p.default is inspect.Parameter.empty for p in parameters.values()), (
        "every part is supplied by the caller; a defaulted part is a part that "
        "silently stops distinguishing cache slots")


def test_changing_any_one_part_changes_the_key(p6_conn):
    baseline = fact_cache_key(**BASELINE)
    mutations = (
        dict(BASELINE, content_hash="b" * 64),
        dict(BASELINE, extractor_version="2.0.0"),
        dict(BASELINE, analysis_tier="ocr"),
        dict(BASELINE, model_identifier="claude-x/2026-08"),
        dict(BASELINE, prompt_fingerprint="sha256:prompt-1"),
    )
    keys = {baseline} | {fact_cache_key(**one) for one in mutations}
    assert len(keys) == 6, "each of the five parts must move the key on its own"
    assert baseline.startswith("sha256:")
    assert fact_cache_key(**BASELINE) == baseline, "the key is a pure function"


def test_a_rename_cannot_reach_the_key(p6_conn, tmp_path):
    """Done-means 16, first half, at the strongest place to assert it: the key has no
    path input at all -- not ignored, not nullable, absent."""
    parameters = inspect.signature(fact_cache_key).parameters
    for forbidden in ("path", "current_path", "filename", "file_id", "directory_position"):
        assert forbidden not in parameters

    before = _record(p6_conn, tmp_path, name="Syllabus.pdf", body=b"BUSIB 4300")
    after = _record(p6_conn, tmp_path, name="renamed.pdf", body=b"BUSIB 4300")
    assert before[1] == after[1], "same bytes, same content hash (P1 R1)"
    assert (fact_cache_key(**dict(BASELINE, content_hash=before[1]))
            == fact_cache_key(**dict(BASELINE, content_hash=after[1])))


def test_a_rename_triggers_no_re_resolution_and_a_content_change_does(p6_conn, tmp_path):
    """Done-means 16, end to end, through the fact table."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    key = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=key)

    # The rename: P1's identity is the content hash, so the row is the same row and
    # the key is the same key.
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=key) is False

    # The content rewrite: a new content hash is a new slot, and nothing has been
    # computed in it.
    _, rewritten = _record(p6_conn, tmp_path, name="Syllabus-v2.pdf",
                           body=b"BUSIB 4300 revised")
    assert rewritten != content_hash
    rewritten_key = fact_cache_key(**dict(BASELINE, content_hash=rewritten))
    assert is_stale(p6_conn, file_id=file_id, content_hash=rewritten,
                    cache_key=rewritten_key) is True


def test_a_bumped_extractor_version_re_resolves(p6_conn, tmp_path):
    """Done-means 15's trigger. The supersession itself is Task 23's."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    old = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=old)

    bumped = fact_cache_key(**dict(BASELINE, content_hash=content_hash,
                                   extractor_version="2.0.0"))
    assert bumped != old
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=bumped) is True
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=old) is False


def test_a_changed_prompt_fingerprint_re_resolves(p6_conn, tmp_path):
    """§3.4's "makes model or prompt changes auditable" -- both keys stay computable,
    and the fact written under the old one stays readable."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Essay.pdf",
                                    body=b"Columbia")
    first = fact_cache_key(content_hash=content_hash, extractor_version="1.0.0",
                           analysis_tier="llm", model_identifier="model-a",
                           prompt_fingerprint="sha256:prompt-1")
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=first)
    second = fact_cache_key(content_hash=content_hash, extractor_version="1.0.0",
                            analysis_tier="llm", model_identifier="model-a",
                            prompt_fingerprint="sha256:prompt-2")
    assert first != second
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=second) is True


def test_none_is_distinguishable_from_the_empty_string(p6_conn):
    """P4's `sha256_of` is length-prefixed and injective, and each part is
    canonical_json-encoded before it is hashed, so `null` and `""` are different
    strings of different lengths. A property to assert, not a hazard to avoid."""
    absent = fact_cache_key(**dict(BASELINE, model_identifier=None))
    empty = fact_cache_key(**dict(BASELINE, model_identifier=""))
    assert absent != empty
    assert (fact_cache_key(**dict(BASELINE, prompt_fingerprint=None))
            != fact_cache_key(**dict(BASELINE, prompt_fingerprint="")))
    # And no two parts can be smeared into each other by concatenation.
    assert (fact_cache_key(content_hash="ab", extractor_version="c",
                           analysis_tier="native", model_identifier=None,
                           prompt_fingerprint=None)
            != fact_cache_key(content_hash="a", extractor_version="bc",
                              analysis_tier="native", model_identifier=None,
                              prompt_fingerprint=None))


def test_the_deterministic_fact_carries_neither_model_part(p6_conn):
    """Done-means 17's half of this task: P8 is absent, so both are None and the key
    is still computable. P6 contains no model call of any kind (§3.3)."""
    assert fact_cache_key(**BASELINE).startswith("sha256:")
    assert BASELINE["model_identifier"] is None
    assert BASELINE["prompt_fingerprint"] is None


def test_the_analysis_tier_is_p4s_and_a_fourth_value_is_refused(p6_conn):
    """P6 never infers a tier -- it comes from P4's `ExtractionRun` (Global
    Constraints), and an unknown one raises rather than being hashed."""
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    for tier in ANALYSIS_TIERS:
        assert fact_cache_key(**dict(BASELINE, analysis_tier=tier))
    with pytest.raises(NotInVocabulary):
        fact_cache_key(**dict(BASELINE, analysis_tier="ocr_v2"))
    for empty in ("content_hash", "extractor_version"):
        with pytest.raises(ValueError):
            fact_cache_key(**dict(BASELINE, **{empty: ""}))


def test_a_run_supplies_the_two_parts_p6_must_not_invent(p6_conn, tmp_path):
    """Preamble rule 5, at the key: a native run and an OCR run over the same content
    hash land in different cache slots, which is why pass 4 supersedes rather than
    overwrites (§8.2). Both parts are read off P4's run, never inferred."""
    _, content_hash = _record(p6_conn, tmp_path, name="Scan.pdf", body=b"scanned")
    runs = [
        ExtractionRun(run_id=f"run-{tier}", file_id="file-scan",
                      content_hash=content_hash, extractor_name="pdf.text",
                      extractor_version="1.0.0", source_type="text_document",
                      analysis_tier=tier, config={}, completeness="complete",
                      started_at=CLOCK, finished_at=CLOCK)
        for tier in ("native", "ocr")
    ]
    keys = {fact_cache_key(content_hash=run.content_hash,
                           extractor_version=run.extractor_version,
                           analysis_tier=run.analysis_tier,
                           model_identifier=None, prompt_fingerprint=None)
            for run in runs}
    assert len(keys) == 2


def test_an_abstention_counts_as_work_done_under_that_key(p6_conn, tmp_path):
    """The SPEC's `unresolved.cache_key` is "same composition as `file_facts` (§3.4),
    so an abstention is invalidated by the same events that invalidate a fact". A
    reader that saw only `file_facts` would call a file that produced only refusals
    stale forever and re-resolve it on every loop."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Blank.pdf", body=b"   ")
    key = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason=NO_CANDIDATE_EVIDENCE,
                     attempted_producers=(DIRECT_ROUTE, RULE_ROUTE), evidence_refs=(),
                     cache_key=key)
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=key) is False
    ocr = fact_cache_key(**dict(BASELINE, content_hash=content_hash,
                                analysis_tier="ocr"))
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=ocr) is True


def test_the_fact_key_is_not_p5s_extraction_key(p6_conn):
    """The naming trap. Two functions, two questions, one design sentence."""
    content_hash = BASELINE["content_hash"]
    mine = fact_cache_key(**BASELINE)
    theirs = extraction_cache_key(content_hash=content_hash,
                                  extractor_name="pdf.text",
                                  extractor_version="1.0.0",
                                  analysis_tier="native",
                                  config_fingerprint="sha256:config-1")
    assert mine != theirs

    ours = set(inspect.signature(fact_cache_key).parameters)
    p5 = set(inspect.signature(extraction_cache_key).parameters)
    assert "extractor_name" not in ours and "config_fingerprint" not in ours
    assert "model_identifier" not in p5 and "prompt_fingerprint" not in p5

    # Runtime introspection, not a source-text search: this file's own docstrings
    # name `extractors.runs.cache_key` and a text guard would match them.
    namespace = vars(cache_module).values()
    assert not any(one is extraction_cache_key for one in namespace)
    assert not any(getattr(one, "__name__", "") == "extractors.runs"
                   for one in namespace)
```

- [ ] **Step 2: Run the test and see it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_cache.py -x -q
```

**Expected failure:** collection fails before any test body runs —
`ModuleNotFoundError: No module named 'facts.cache'`. All thirteen tests error at import.

- [ ] **Step 3: Write `src/facts/cache.py`**

```python
# src/facts/cache.py
"""§3.4's cache key, and what invalidates a fact -- Done-means 15 and 16.

The design, in one sentence: "The cache key includes content hash, extractor version,
analysis tier, model identifier when relevant, and prompt fingerprint for model-derived
results. This prevents stale results from surviving a content rewrite, avoids
unnecessary work when a file is merely renamed, and makes model or prompt changes
auditable."

Three consequences, and every one of them is a test:

  - There is NO path input. Not ignored, not nullable -- absent. That absence IS
    "avoids unnecessary work when a file is merely renamed": a rename cannot reach the
    key because the key has nowhere to put a path.
  - `content_hash` is a part, so a content rewrite is a different slot and the old
    facts cannot be found in it. That is "prevents stale results from surviving a
    content rewrite".
  - `model_identifier` and `prompt_fingerprint` are parts, so a prompt change
    re-resolves and BOTH keys stay computable and readable. That is "makes model or
    prompt changes auditable" -- §8.2's supersede-never-overwrite, at the cache.

TWO CACHE KEYS EXIST, AND THIS IS NOT THE OTHER ONE. `extractors.runs.cache_key(*,
content_hash, extractor_name, extractor_version, analysis_tier, config_fingerprint)`
identifies an EXTRACTION RESULT -- which extractor at which configuration produced
these observations. This one identifies a FACT -- which evidence, under which model and
prompt, produced this conclusion. §3.4 predates §3.2's observation/fact split, so one
design sentence has two subjects and the built system has two functions. Neither list
of parts is a subset of the other, so neither can be expressed in terms of the other,
and this module imports nothing from `extractors`.

`None` VS `""`. `sha256_of` is length-prefixed and therefore injective over the tuple
of strings it is handed, but it takes strings and `None` is not one. Every part is
encoded through `canonical_json` first: `None` becomes `null` and `""` becomes `""`
(with the quotes) -- different strings, different lengths, different digests. An absent
model identifier and an empty one are not the same cache slot.

WHAT IS NOT DECIDED HERE. §3.4 says "model identifier when relevant" and "prompt
fingerprint for model-derived results" and states no dependency between them, so no
both-or-neither guard is imposed: P8 is the part that would know whether one is true and
P8 does not exist.

WHAT IS DECIDED HERE, AND ONLY HERE. A file version has several extractor versions and
several analysis tiers, and §3.4 wants one of each. That reconciliation is THIS
function's: `extractor_version` is the canonical JSON of the sorted distinct
(extractor_name, extractor_version) pairs of EVERY observation of the version -- not of
the ones a fact happens to cite -- and `analysis_tier` is the last tier present in
ANALYSIS_TIERS order. So there is ONE key per (file version, deterministic pass), which
is what lets the abstention share the fact's key: an `unresolved` row with no citations
has no cited observations to compute a key from, and the SPEC gives it the "same
composition as `file_facts` (§3.4)". Taking `file_id` and `content_hash` rather than a
set of observations is deliberate: a caller CANNOT hand this function a filtered subset.
No producer writes its own copy of this rule; `facts.cache` is Task 6's module and no
other task adds to it.
"""
from __future__ import annotations

import sqlite3

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

__all__ = ["CACHE_KEY_PARTS", "fact_cache_key", "is_stale"]

#: §3.4's five parts, in §3.4's own order. The order is part of the key: the digest is
#: over an ordered tuple, so reordering this tuple would invalidate every stored key.
CACHE_KEY_PARTS: tuple[str, ...] = (
    "content_hash",
    "extractor_version",
    "analysis_tier",
    "model_identifier",
    "prompt_fingerprint",
)

#: The two tables whose rows record "work was done under this key". `unresolved` is
#: here because the SPEC gives its `cache_key` the "same composition as `file_facts`
#: (§3.4), so an abstention is invalidated by the same events that invalidate a fact".
#: A file whose deterministic pass produced only refusals HAS been resolved under that
#: key; a reader that saw only `file_facts` would call it stale forever.
#:
#: Addressed by SQL rather than by importing `facts.file_facts` and `facts.unresolved`,
#: because every Wave B producer imports both this module and those, and a module that
#: imports none of its siblings cannot be half of an import cycle.
_RECORD_TABLES: tuple[str, ...] = ("file_facts", "unresolved")

#: P4's evidence, joined to the run that produced it. Column names verified live on
#: 2026-08-22. `facts.evidence.observations_for_version` answers the same question and
#: is deliberately NOT imported, for the same reason as `_RECORD_TABLES` above.
_VERSION_PARTS_SQL = """
    SELECT DISTINCT e.extractor_name  AS extractor_name,
                    e.extractor_version AS extractor_version,
                    r.analysis_tier   AS analysis_tier
      FROM evidence e
      JOIN extraction_runs r ON r.run_id = e.run_id
     WHERE e.file_id = ? AND e.content_hash = ?
"""


def _required(value: str, *, name: str) -> str:
    """`file_id` and `content_hash` identify the work. An empty one means "unknown",
    and two unknowns must not silently share a cache slot with each other or with a
    real value."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required and must be a non-empty string")
    return value


def _version_parts(conn: sqlite3.Connection, *, file_id: str,
                   content_hash: str) -> tuple[str, str]:
    """§3.4's two derived parts for one file version: `(extractor_version, tier)`.

    Both are over EVERY observation of the version. A version with no observations
    yet keys at the first tier with an empty pair list -- a real slot, distinct from
    every slot that has evidence in it, which is what an abstention recorded before
    any extractor ran needs.

    The tier is the LAST one present in `ANALYSIS_TIERS` order, so a pass that reached
    OCR lands outside the slot the native pass computed under: preamble §3.3's
    supersede-rather-than-overwrite, at the key. `check` is applied to what P4 stored
    because P6 never infers a tier and a tier P4 does not publish is a contract
    revision, not a row this module quietly hashes.
    """
    rows = conn.execute(_VERSION_PARTS_SQL, (file_id, content_hash)).fetchall()
    pairs = sorted({(row["extractor_name"], row["extractor_version"])
                    for row in rows})
    tiers = {check(row["analysis_tier"], ANALYSIS_TIERS, name="analysis_tier")
             for row in rows}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return canonical_json([list(pair) for pair in pairs]), tier


def fact_cache_key(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   model_identifier: str | None,
                   prompt_fingerprint: str | None) -> str:
    """§3.4's key for one (file version, deterministic pass). A `sha256:` digest.

    THE ONE HELPER. Every producer imports this; no task writes its own copy of the
    reconciliation in `_version_parts`, and `facts.cache` is the module that owns it.

    `extractor_version` and `analysis_tier` are derived from every observation of the
    version rather than supplied, so a caller cannot narrow them to the observations
    one fact cited -- and so an `unresolved` row, which cites nothing, computes the
    SAME key as the facts of the pass that wrote it.

    The two model parts stay the caller's and carry no default: they are `None` on
    every deterministic fact P6 writes (§3.3), and Task 17's LLM-supported fact is the
    one place that is not true. A defaulted part is a part that silently stops
    distinguishing cache slots.
    """
    _required(content_hash, name="content_hash")
    _required(file_id, name="file_id")
    extractor_version, analysis_tier = _version_parts(
        conn, file_id=file_id, content_hash=content_hash)
    parts = (content_hash, extractor_version, analysis_tier,
             model_identifier, prompt_fingerprint)
    assert len(parts) == len(CACHE_KEY_PARTS)
    return sha256_of(*(canonical_json(part) for part in parts))


def is_stale(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
             cache_key: str) -> bool:
    """True unless some record for `(file_id, content_hash)` was written under exactly
    this key.

    Three cases, one rule:

      - a rename, content unchanged  -> facts under this same key   -> False
      - a content rewrite            -> new slot, nothing in it     -> True
      - a bumped version or prompt   -> facts under the OLD key     -> True

    "Nothing has been computed for this file version" and "the content was rewritten"
    are the same case, and both need computing, which is why one predicate serves all
    three. This function re-resolves nothing and writes nothing: §8.2's supersession is
    `facts/supersede.py`'s and the sequencing is `facts/resolver.py`'s.
    """
    _required(file_id, name="file_id")
    _required(content_hash, name="content_hash")
    _required(cache_key, name="cache_key")
    for table in _RECORD_TABLES:
        found = conn.execute(
            f"SELECT 1 FROM {table} "
            "WHERE file_id = ? AND content_hash = ? AND cache_key = ? LIMIT 1",
            (file_id, content_hash, cache_key),
        ).fetchone()
        if found is not None:
            return False
    return True
```

- [ ] **Step 4: Run the test and see it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_cache.py -q
```

**Expected:** `12 passed`.

- [ ] **Step 5: Run Wave A and then the whole suite**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q && python3 -m pytest tests -q
```

**Expected:** every P6 test green and the 1302 P1–P5 tests still green. Wave A is complete after this
step: `fields`, `values`, `file_facts`, `unresolved` and the cache key all exist, and Tasks 7–13 can
start in parallel.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/cache.py tests/p6/test_p6_cache.py && \
git commit -m "feat(P6): §3.4's five-part fact cache key — a rename is free, a version bump is not"
```

---

## Contract ambiguities these two tasks hit and did not resolve

Five, reported rather than patched, because each one belongs to a file another author owns.

1. ~~**`get_field(conn, field_key)` must return a `field_id`.**~~ **RESOLVED by brief §17 exactly as
   this author predicted.** The reasoning was right and the prediction was right: *"if Task 2's
   catalogue keys on `field_key` alone, that one line and Task 4's equivalent change together."*
   Task 2's catalogue now keys on `field_key` alone — its first draft carried BOTH `field_id` and
   `field_key` holding the identical string, and that second column is deleted. So `values`,
   `file_facts` and `unresolved` all carry `field_key`, `get_field(...)["field_key"]` is what the
   one-line helper reads, and `PLAN-tasks-16-19.md`'s `old["field_id"]` is corrected with them.
   The column exists in all of them under one name, which is the "in both tables or in neither"
   this item asked for.
2. **One design sentence, two cache-key functions.** §3.4 describes one key; the built system has
   `extractors.runs.cache_key` and `facts.cache.fact_cache_key`, because P4's observation/fact split
   gave the sentence two subjects after §3.4 was written. Task 6's test pins them apart rather than
   reconciling them. Reconciling them would be a P4/P5/P6 seam change.
3. **The cross-table supersede back-pointer does not exist and cannot, through P1's surface.**
   `mark_superseded(conn, table, *, old_id, new_id, reason)` takes **one** table, so superseding an
   `unresolved` row with a `file_facts` row records `superseded_by` on the abstention and leaves
   `file_facts.supersedes` as `None` — verified by execution, silently, with no error raised. Task 5
   asserts the half that Done-means 19 and SPEC rule 3 require. Whether the fact should also point
   back at the refusal it replaced is `facts/supersede.py`'s question (Task 23).
4. **A fabricated quotation lives in P6's SPEC and in the skeleton, and is not repaired here.**
   Both attribute to §8.6 the sentence *"visible as deferred, never as 'understood and found
   unimportant'"*. The design contains no such sentence. Its actual words, grepped: *"If the budget
   is exhausted, the product should retain extracted evidence, mark the deferred stage, and leave the
   file or group in review rather than guessing"*, *"Cost exhaustion must never turn into
   lower-quality automatic classification"*, *"The user interface should show the difference between
   completed work and deferred work"*, and *"avoids the false impression that an unprocessed file was
   understood and found unimportant"*. The paraphrase is faithful in substance, which is why it
   spread; it is still not a quotation. These two tasks quote the design's words instead. **The SPEC
   and `PLAN-SKELETON.md` still carry it** — they are not this author's files, and the same phrase
   should be expected in the other P6 and P7 task documents written against the same skeleton.

5. **The multi-observation reconciliation is stated in five places and owned by none.** A fact built
   from several observations has several extractor versions and several analysis tiers;
   `PLAN-tasks-07-09.md` and `PLAN-tasks-14-15.md` both state the same collapse rule
   (`extractor_version` = `canonical_json` of the sorted distinct `[name, version]` pairs;
   `analysis_tier` = the last tier present in `ANALYSIS_TIERS` order) and both flag that it belongs
   in `facts.cache`. **Task 6 deliberately does not build it.** Its `Interfaces:` block publishes
   three names and a collapse helper is not one of them, and adding a fourth would change a contract
   four parallel authors are already writing against. It is the resolver's (Task 24) or a follow-up
   to this task, and the decision needs the lead rather than an author working alone.
