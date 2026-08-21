### Task 5: `unresolved` — the abstention row, and its thirteen reasons

**Files:**
- Create: `src/facts/unresolved.py`
- Modify: `src/facts/vocabulary.py`, `src/facts/schema.py`
- Test: `tests/p6/test_p6_unresolved.py`

**Interfaces:**
- Consumes: `facts.fields.get_field`, `facts.fields.FieldNotInCatalogue`;
  `evidence_shape.vocabulary.check`, `evidence_shape.vocabulary.NotInVocabulary`;
  `evidence_shape.canonical.canonical_json`; `database_agent.supersede.supersede_ddl`.
- Produces: `UNRESOLVED_REASONS: tuple[str, ...]` (the thirteen),
  `ATTEMPTED_PRODUCERS: tuple[str, str, str]` (`direct`, `rule`, `llm`),
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
`budget_deferred` and `privacy_withheld` are **not abstentions** — §8.6 requires deferred work be
*"visible as deferred, never as 'understood and found unimportant'"*, and merging them would report a
budget stop as a considered refusal.

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
  `(file_id, content_hash, field_id)` under two different cache keys are two rows, because §3.4's key
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
    FACT_ORIGINS, FORBIDDEN_COLUMN_SUBSTRINGS, facts_for_file, write_fact,
)
from facts.unresolved import (
    ATTEMPTED_PRODUCERS, NOT_ABSTENTIONS, UNRESOLVED_REASONS,
    unresolved_for_file, write_unresolved,
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
            reason="looked_wrong", attempted_producers=("direct",),
            evidence_refs=(), cache_key=CACHE_KEY)
    assert unresolved_for_file(p6_conn, FILE_ID, HASH) == []


def test_the_three_attempted_producers_and_a_fourth_refused(p6_conn):
    assert ATTEMPTED_PRODUCERS == ("direct", "rule", "llm")
    with pytest.raises(NotInVocabulary):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
            reason="no_candidate_evidence", attempted_producers=("direct", "heuristic"),
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
        reason="no_candidate_evidence", attempted_producers=("direct", "rule"),
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
        reason="no_candidate_evidence", attempted_producers=("direct", "rule"),
        evidence_refs=(), cache_key=CACHE_KEY)
    value_id = ensure_value(
        p6_conn, field_key="subject", canonical_value="BUSIB 4300",
        first_evidence_ref=_key("BUSIB 4300"), origin="automatic")
    # FACT_ORIGINS is addressed BY INDEX -- §3.1's five, in §3.1's order, index 1 is
    # `rule`. Task 4 owns the literal spelling and `PLAN-tasks-07-09.md` records the
    # same convention, so no second document guesses at the string.
    fact_id = write_fact(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        value_id=value_id, reliability_state="validated", origin=FACT_ORIGINS[1],
        evidence_refs=(_key("BUSIB 4300"),), cache_key="sha256:cache-ocr-1",
        active=True)

    mark_superseded(p6_conn, "unresolved", old_id=unresolved_id, new_id=fact_id,
                    reason="resolved on re-resolution over OCR evidence (§8.2)")

    rows = unresolved_for_file(p6_conn, FILE_ID, HASH)
    assert len(rows) == 1, "supersede must not delete the abstention"
    assert rows[0]["unresolved_id"] == unresolved_id
    assert rows[0]["superseded_by"] == fact_id
    assert rows[0]["supersede_reason"]
    assert rows[0]["reason"] == "no_candidate_evidence"


def test_an_unresolved_row_is_absent_from_every_fact_read(p6_conn):
    """Done-means 19. The two tables never leak into one another."""
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason="below_margin", attempted_producers=("rule",),
        evidence_refs=(_key("BUSIB 4300"),), cache_key=CACHE_KEY)
    assert facts_for_file(p6_conn, FILE_ID, HASH) == []


def test_budget_deferred_and_privacy_withheld_are_not_abstentions(p6_conn):
    """B7's second half, and §8.6's "visible as deferred, never as 'understood and
    found unimportant'". All three are rows; only one is an abstention."""
    assert NOT_ABSTENTIONS == frozenset({"budget_deferred", "privacy_withheld"})
    assert NOT_ABSTENTIONS <= set(UNRESOLVED_REASONS)

    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason="no_candidate_evidence", attempted_producers=("direct", "rule"),
        evidence_refs=(), cache_key=CACHE_KEY)
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="purpose",
        reason="budget_deferred", attempted_producers=(),
        evidence_refs=(), cache_key=CACHE_KEY)
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="project",
        reason="privacy_withheld", attempted_producers=("direct", "rule"),
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
        reason="budget_deferred", attempted_producers=(),
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
        reason="below_margin", attempted_producers=("rule",),
        evidence_refs=refs, cache_key=CACHE_KEY)
    stored = json.loads(unresolved_for_file(p6_conn, FILE_ID, HASH)[0]["evidence_refs"])
    assert stored == list(refs)
    assert all(ref.startswith("sha256:") for ref in stored)

    with pytest.raises(ValueError):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
            reason="below_margin", attempted_producers=("rule",),
            evidence_refs=("obs-00000001",), cache_key=CACHE_KEY)


def test_a_field_outside_the_catalogue_cannot_be_abstained_on(p6_conn):
    """§3.12 — new values may be created automatically, new fields may not. The rule
    binds the refusal row as hard as it binds the fact row."""
    with pytest.raises(FieldNotInCatalogue):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="vibe_score",
            reason="no_candidate_evidence", attempted_producers=("direct",),
            evidence_refs=(), cache_key=CACHE_KEY)


def test_the_abstention_is_per_file_version_and_the_read_is_totally_ordered(p6_conn):
    """§3.4, §8.2 — the row is per content hash, and the reader imposes its own order
    rather than inheriting insertion order from SQLite."""
    for content_hash, reason in ((HASH, "no_candidate_evidence"),
                                 (OTHER_HASH, "below_margin")):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=content_hash, field_key="subject",
            reason=reason, attempted_producers=("rule",),
            evidence_refs=(), cache_key=CACHE_KEY)

    native = unresolved_for_file(p6_conn, FILE_ID, HASH)
    assert [row["reason"] for row in native] == ["no_candidate_evidence"]
    assert [row["reason"] for row in unresolved_for_file(
        p6_conn, FILE_ID, OTHER_HASH)] == ["below_margin"]

    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="purpose",
        reason="privacy_withheld", attempted_producers=("llm",),
        evidence_refs=(), cache_key=CACHE_KEY)
    rows = unresolved_for_file(p6_conn, FILE_ID, HASH)
    order = [(row["created_at"], row["unresolved_id"]) for row in rows]
    assert order == sorted(order), "the reader imposes its own total order"
    assert len(unresolved_for_file(p6_conn, FILE_ID, HASH,
                                   reason="privacy_withheld")) == 1
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

#: The thirteen reasons, in the SPEC's own table order. Each is fired by exactly one
#: place, named in the comment beside it, so a reason with no producer or a producer
#: with no reason is visible by reading this list.
UNRESOLVED_REASONS: tuple[str, ...] = (
    "no_candidate_evidence",         # no observation offered a candidate (§3.6)
    "below_score_threshold",         # §3.7 minimum score not cleared
    "below_margin",                  # §3.7 margin not cleared, incl. §2.6's conflict
    "context_check_failed",          # §3.5 pattern matched, required context absent
    "context_truncated",             # §3.5 check failed on context_truncated = true (§8.6)
    "field_not_in_active_schema",    # §3.6 check 1
    "citation_absent_from_evidence",  # §3.6 check 2
    "normalization_failed",          # §3.6 check 3
    "contradicted_by_stronger_fact",  # §3.6 check 4
    "model_returned_unknown",        # §3.6 — the model declined
    "discounted_tool_metadata",      # the §2.2/§2.3 producer/creator discount fired
    "privacy_withheld",              # P7's handling class forbids the model route (§8.4)
    "budget_deferred",               # §8.6 ceiling reached — never merged with abstention
)

#: §3.5's three routes. `direct` and `rule` are P6's own; `llm` is P8's, and P6
#: records that it was tried without owning the call (§3.3).
ATTEMPTED_PRODUCERS: tuple[str, str, str] = ("direct", "rule", "llm")

#: The two reasons that are NOT abstentions (B7, §8.6). A refusal for either of these
#: means the question was never answered on the evidence: the budget stopped the work,
#: or the privacy class forbade the only remaining route. §8.6 requires deferred work
#: be "visible as deferred, never as 'understood and found unimportant'", and reporting
#: either of these as a considered refusal is exactly that failure.
#:
#: This is a frozenset and not a tuple because it is asked `in` and never iterated for
#: order, and because P2's writer (`record_stage_output`) already enforces the
#: consequence -- outcome `deferred` requires budget_state `ceiling_reached`, and
#: `ceiling_reached` refuses outcome `abstained`. P6 does not re-implement that rule;
#: it names the two reasons that must not be routed into it as abstentions.
NOT_ABSTENTIONS: frozenset[str] = frozenset({"budget_deferred", "privacy_withheld"})
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
    field_id            TEXT NOT NULL,
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
    ATTEMPTED_PRODUCERS, NOT_ABSTENTIONS, UNRESOLVED_REASONS,
)

__all__ = [
    "ATTEMPTED_PRODUCERS",
    "NOT_ABSTENTIONS",
    "UNRESOLVED_REASONS",
    "unresolved_for_file",
    "write_unresolved",
]

#: An observation key is `sha256:`-prefixed (P4's `sha256_of`); an `observation_id` and
#: a content hash are not. The prefix is the whole difference between citing M14's
#: version-independent key and citing a row id that an extractor upgrade invalidates.
_KEY_PREFIX = "sha256:"


def _field_id(conn: sqlite3.Connection, field_key: str) -> str:
    """The catalogue row's identity, resolved through Task 2's published reader.

    `get_field` raises `FieldNotInCatalogue` for a key the catalogue does not carry,
    which is §3.12 -- "it should not invent new fields automatically" -- enforced at
    the abstention row exactly as hard as at the fact row. A refusal naming a field
    that does not exist is not a refusal, it is a typo.
    """
    return get_field(conn, field_key)["field_id"]


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
    same `(file_id, content_hash, field_id)` under two different §3.4 cache keys are
    two different events, and §8.2 keeps both readable.
    """
    _required(file_id, name="file_id")
    _required(content_hash, name="content_hash")
    _required(cache_key, name="cache_key")
    field_id = _field_id(conn, field_key)
    check(reason, UNRESOLVED_REASONS, name="reason")
    producers = _attempted(attempted_producers)
    refs = _evidence_refs(evidence_refs)

    unresolved_id = uuid.uuid4().hex
    conn.execute(
        """
        INSERT INTO unresolved (
            unresolved_id, file_id, content_hash, field_id, reason,
            attempted_producers, evidence_refs, cache_key, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unresolved_id, file_id, content_hash, field_id, reason,
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
        clauses.append("field_id = ?")
        params.append(_field_id(conn, field_key))
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

**Expected:** every P6 test green, and the 1300 P1–P5 tests still green — P6 modified no file outside
`src/facts/` and `tests/p6/`.

- [ ] **Step 7: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/unresolved.py src/facts/vocabulary.py \
  src/facts/schema.py tests/p6/test_p6_unresolved.py && \
git commit -m "feat(P6): unresolved — the abstention is a row, and two of its thirteen reasons are not abstentions"
```
