### Task 22: §8.7 correction learning — query before propose (I4)

**Files:**
- Create: `src/facts/learning.py`
- Test: `tests/p6/test_p6_learning.py`

**Interfaces:**
- Consumes: `database_agent.learning` — `learning_records`, `reset_cutoff`;
  `database_agent.events` — `CORRECTION_SCOPES`, `CORRECTION_FIELDS`, `append_event`;
  `evidence_shape.canonical` — `canonical_json`; `facts.authorship` — `AUTHORED_EVENT_TYPES`,
  `event_defaults`.
- Produces: `PROPOSAL_CLASS: str` (`"fact"`), `POLARITIES: tuple[str, str]`,
  `MalformedCorrection`, `basis_key(*, file_id, field_key, value_id) -> str`,
  `is_suppressed(conn, *, scope, subject_id, file_id, field_key, value_id) -> bool`,
  `record_correction(conn, *, action, scope, subject, polarity, file_id, field_key, value_id,
  evidence_refs, user_id, observed_at) -> int`.

**Done-means:** none numbered; §8.7's obligations and I4's query-before-propose rule.

---

**Which half of this task binds now, and which is owed to P13's wave.** §8.7's corrections arrive
through P13's `review_action`, and **P13 does not exist**. That splits this task cleanly and the
split must be stated before the code, because a reader who assumes both halves are live will look
for a call site that is not there.

| | Built here | Reachable today | Owed to |
|---|---|---|---|
| **The read** — `basis_key`, `PROPOSAL_CLASS`, `is_suppressed` | yes | **yes, and it must be** | — |
| **The write** — `record_correction` | yes | **no** — nothing in this plan calls it | P13 routes the gesture |
| The gesture surface that collects `review_action` | no | — | P13 |
| The inspect / reset UI, and the call to P1's `reset_preferences` | no | — | P13 |
| The resolver's *call site* for the guard | no | — | Task 20 |

**The read half binds now even though the write half cannot fire**, and the reason is ordering, not
completeness. §8.7 requires that a rejected suggestion be **stored** and **not re-proposed** — I4
states the consequence for P6 as *"Before writing a `file_facts` row that would revive a `rejected`
claim … Leave the `rejected` row in place; do not propose the same `(field, value)` again."* A guard
that arrives after the first fact is written is a guard that has already failed once. So
`is_suppressed` ships with the fact tables, answers correctly against an empty store (`False`, no
records, nothing suppressed), and is correct on the day P13 starts filling the store. Building it
later would mean shipping a fact writer with a known missing check.

`record_correction` is built here rather than deferred because P6 **authors** the fact-level
consequence and P1 **writes** the event (M8) — the authorship is P6's whichever part collects the
gesture. It is P13's stand-in, and P6's tests drive it directly, exactly as the skeleton says of
every P13 fixture: *"Tests drive the fixture directly."*

**P6 mints no new §8.2 event type here, and that is the point of I4's design.** A user correction is
identified by two ordinary columns — `proposal_class` and `basis_key` — carried beside the eleven on
an ordinary event, never by a type of its own. Verified live: `database_agent.events.CORRECTION_FIELDS`
is `("correction_scope", "correction_subject", "polarity", "proposal_class", "basis_key")` and the
`events` table carries all five as real columns. The two event types this module uses are P6's own
authored pair from Task 1, `("fact creation", "fact rejection")`, both already members of §8.2's
reserved nineteen (verified: both are in `RESERVED_EVENT_TYPES`, both spelled with a space). Nothing
is registered, and a hypothetical `fact_correction` type would raise `UnregisteredEventType` at run
time — registration is a spec-level act, not a call.

**Why the basis key is canonical JSON and not a digest.** I4 fixes P6's equivalence as
`proposal_class = fact`, `basis_key = (file_id, field, value_id)`, and P1's `basis_key` is one TEXT
column — so the triple has to be serialized, and the deferred table names this task as the one place
that serialization may live. Three candidates:

- `f"{file_id}|{field_key}|{value_id}"` — **rejected, not injective.** A `|` inside any part collides
  two different claims onto one key, and a collision here silently suppresses a proposal the user
  never rejected.
- `sha256_of(file_id, field_key, value_id)` — injective, and rejected for a different reason: §8.7
  requires *"The user should be able to inspect or reset learned preferences, so personalization
  remains understandable and reversible."* A store whose every row's basis is an opaque digest is
  not inspectable, and P1 stores the column verbatim for exactly that reason.
- **`canonical_json({"field_key": …, "file_id": …, "value_id": …})` — chosen.** Injective, because
  JSON escapes its own delimiters; readable in a row dump; and it reuses P4's single canonical form
  rather than minting a second serializer in a project whose replay diff (§8.5) breaks the moment two
  equal records serialize two ways. `canonical_json` sorts keys, so the argument order at the call
  site cannot change the stored key.

**Why `reset_cutoff` is consumed by the test and not by the module.** `learning_records` already
applies the cutoff internally — verified by execution: a rejection appended, then
`reset_preferences` at the same scope and subject, and `learning_records` returns zero rows while the
rejection row is still in `events`. Calling `reset_cutoff` again inside `is_suppressed` would put the
cutoff rule in a second place, which is the defect class this project keeps hitting. The test
consumes it to **prove the mechanism** — that the reset's `event_id` is the cutoff and the rejection
sits below it — rather than to trust a docstring.

**Where the guard is called from.** Task 22 builds the guard; **Task 20's resolver is the call
site.** This task's test proves the guard's behaviour and proves the composition with a
resolver-shaped four-line helper defined in the test, so the red-green cycle is self-contained and
does not depend on Task 4's `write_fact` keyword list or on a conftest fixture whose name is not in
any published contract. The guard is read-only: it appends no event, writes no fact, and mutates
nothing — asserted, because a "guard" that writes is a guard that changes what it is guarding.

**Two names beyond the skeleton's four, both flagged.** `POLARITIES` is I4's own vocabulary
(*"`polarity ∈ accept | reject`** is the third required field and is not cosmetic"*) and Task 25's
introspection needs it published rather than inlined. `MalformedCorrection` follows the pattern
Tasks 2, 4 and 5 already set (`FieldNotInCatalogue`, `EvidenceRequired`) — `events` is append-only,
so a malformed correction cannot be repaired after the fact and must be refused at the writer.

**One thing this task deliberately does not decide.** I4's rule 4 is literal: *"On a record with
`polarity = reject` that no later reset covers: does not emit the proposal. A `polarity = accept`
record at the same `basis_key` is not a suppression and must not be read as one."* It says an accept
is not itself a suppression; it does **not** say a later accept *lifts* an earlier reject. Only a
reset does, in I4's text. This module implements the literal rule — **any** unreset reject at that
scope, subject, class and basis suppresses — and does not invent a newest-wins override. If Joseph
wants an accept to lift a reject without a reset, that is a decision, not a bug fix.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_learning.py
"""§8.7 correction learning: the query-before-propose guard, and what P6 may author.

The read half is live today. The write half is P13's stand-in -- P13 does not exist,
so these tests drive `record_correction` directly, which is how every P13 surface is
exercised in this plan.
"""
from __future__ import annotations

import inspect
import json
import sqlite3

import pytest

from database_agent import db
from database_agent.events import (
    CORRECTION_FIELDS,
    CORRECTION_SCOPES,
    RESERVED_EVENT_TYPES,
    MalformedEvent,
    append_event,
)
from database_agent.learning import learning_records, reset_cutoff, reset_preferences
from facts import learning as learning_module
from facts.authorship import AUTHORED_EVENT_TYPES
from facts.learning import (
    POLARITIES,
    PROPOSAL_CLASS,
    MalformedCorrection,
    basis_key,
    is_suppressed,
    record_correction,
)

CLOCK = "2026-08-22T09:00:00+00:00"
REF = "sha256:" + "e" * 64
OTHER_REF = "sha256:" + "d" * 64


@pytest.fixture()
def conn(tmp_path):
    connection = db.open_database(tmp_path / "p6-learning.db")
    db.create_schema(connection)
    yield connection
    connection.close()


def a_rejection(connection, **overrides) -> int:
    """The walking case: the user rejects `subject = BUSIB 4300` on one file."""
    fields = dict(
        action="reject_fact",
        scope="file",
        subject="file-1",
        polarity="reject",
        file_id="file-1",
        field_key="subject",
        value_id="value-busib-4300",
        evidence_refs=(REF,),
        user_id="user-1",
        observed_at=CLOCK,
    )
    fields.update(overrides)
    return record_correction(connection, **fields)


def event_count(connection) -> int:
    return connection.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]


# --- what P6 identifies a correction by -------------------------------------------


def test_the_proposal_class_is_the_claim_and_p6_mints_no_event_type():
    # I4's equivalence table: P6 owns proposal_class `fact`, basis (file_id, field, value_id).
    assert PROPOSAL_CLASS == "fact"
    # The two names this module writes are P6's own authored pair, and both are already
    # among 8.2's reserved nineteen -- so P6 registers nothing and mints nothing.
    assert AUTHORED_EVENT_TYPES == ("fact creation", "fact rejection")
    for name in AUTHORED_EVENT_TYPES:
        assert name in RESERVED_EVENT_TYPES
    assert POLARITIES == ("accept", "reject")


def test_the_basis_key_is_i4s_triple_serialized_once_and_readably():
    key = basis_key(file_id="file-1", field_key="subject", value_id="value-busib-4300")
    parsed = json.loads(key)
    # Exactly I4's three parts, and nothing else: no plan version, no dossier hash,
    # no display label, no member set.
    assert set(parsed) == {"file_id", "field_key", "value_id"}
    assert parsed["file_id"] == "file-1"
    assert parsed["field_key"] == "subject"
    assert parsed["value_id"] == "value-busib-4300"


def test_the_basis_key_is_deterministic_and_independent_of_argument_order():
    first = basis_key(file_id="f", field_key="subject", value_id="v")
    second = basis_key(value_id="v", file_id="f", field_key="subject")
    assert first == second


def test_the_basis_key_is_injective_over_its_three_parts():
    # A delimiter-joined key would collide these two, and a collision silently
    # suppresses a proposal the user never rejected.
    left = basis_key(file_id="a|b", field_key="subject", value_id="v")
    right = basis_key(file_id="a", field_key="b|subject", value_id="v")
    assert left != right
    assert basis_key(file_id="", field_key="x", value_id="y") != \
        basis_key(file_id="x", field_key="", value_id="y")


# --- the guard --------------------------------------------------------------------


def test_an_empty_store_suppresses_nothing(conn):
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_an_unreset_reject_suppresses_the_same_claim(conn):
    a_rejection(conn)
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is True


def test_the_guard_writes_nothing(conn):
    a_rejection(conn)
    before = event_count(conn)
    is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    )
    is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-other",
    )
    assert event_count(conn) == before


def test_a_different_basis_key_at_the_same_scope_still_emits(conn):
    a_rejection(conn)
    # A different value under the same field is a different claim (I4: "A different
    # value is a different proposal").
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4400",
    ) is False
    # A different field on the same file is a different claim.
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="term", value_id="value-busib-4300",
    ) is False


def test_a_record_at_the_wrong_proposal_class_is_ignored(conn):
    key = basis_key(file_id="file-1", field_key="subject", value_id="value-busib-4300")
    # P11's `placement` class, same scope, same subject, same basis string. P6 must
    # not read another part's rejection as its own.
    append_event(
        conn, event_type="placement recommendation", subsystem="P11",
        component_version="0.0.0", observed_at=CLOCK, explanation="{}",
        correction_scope="file", correction_subject="file-1", polarity="reject",
        proposal_class="placement", basis_key=key, user_id="user-1",
    )
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_an_accept_is_not_a_suppression(conn):
    a_rejection(conn, action="confirm_fact", polarity="accept", evidence_refs=())
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_a_reset_at_that_scope_and_subject_allows_emission_again(conn):
    rejection_id = a_rejection(conn)
    reset_id = reset_preferences(
        conn, "file", "file-1",
        author="P13", component_version="0.0.0", user_id="user-1",
    )
    # The mechanism, not a docstring: the reset's event_id IS the cutoff, and the
    # rejection sits below it, so `learning_records` stops returning it.
    assert reset_cutoff(conn, "file", "file-1") == reset_id
    assert rejection_id < reset_id
    assert learning_records(conn, "file", "file-1") == []
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False
    # R6: the reset deleted nothing. The rejection is still in the append-only log.
    surviving = conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE event_id = ?", (rejection_id,)
    ).fetchone()["n"]
    assert surviving == 1


def test_the_guard_stops_the_write_a_resolver_would_have_made(conn):
    """Task 20's resolver shape, four lines of it, so the composition is proved here."""
    a_rejection(conn)
    claims = [
        ("file-1", "subject", "value-busib-4300"),   # the rejected one
        ("file-1", "subject", "value-busib-4400"),   # a different value
        ("file-2", "subject", "value-busib-4300"),   # a different file
    ]
    written = []
    for file_id, field_key, value_id in claims:
        if is_suppressed(
            conn, scope="file", subject_id=file_id,
            file_id=file_id, field_key=field_key, value_id=value_id,
        ):
            continue
        written.append((file_id, field_key, value_id))
    assert written == [
        ("file-1", "subject", "value-busib-4400"),
        ("file-2", "subject", "value-busib-4300"),
    ]


# --- 8.7's scopes, and the two worked examples ------------------------------------


def test_every_scope_p1_accepts_p6_can_record(conn):
    assert CORRECTION_SCOPES == ("file", "group", "node", "template", "domain", "corpus")
    for index, scope in enumerate(CORRECTION_SCOPES):
        a_rejection(conn, scope=scope, subject=f"subject-{index}")
    assert event_count(conn) == len(CORRECTION_SCOPES)


def test_a_seventh_scope_is_refused_by_p1_and_p6_does_not_respell_the_six(conn):
    with pytest.raises(MalformedEvent):
        a_rejection(conn, scope="semester")
    # P6 holds no copy of the six: the refusal came from P1's writer, which is the
    # single place they are spelled.
    assert "semester" not in CORRECTION_SCOPES


def test_one_transcript_does_not_teach_the_engine_that_all_transcripts_belong_there(conn):
    # 8.7's own worked case: "a user may say that one particular transcript belongs in
    # a Columbia packet but should not teach the engine that all transcripts belong there."
    a_rejection(
        conn, scope="file", subject="transcript-1", file_id="transcript-1",
        field_key="institution", value_id="value-columbia",
    )
    assert is_suppressed(
        conn, scope="file", subject_id="transcript-1",
        file_id="transcript-1", field_key="institution", value_id="value-columbia",
    ) is True
    # A second transcript is untouched -- scope is exact, and the basis names the file.
    assert is_suppressed(
        conn, scope="file", subject_id="transcript-2",
        file_id="transcript-2", field_key="institution", value_id="value-columbia",
    ) is False
    # And the file-scoped record is invisible to a corpus-scoped read (P1's rule).
    assert learning_records(conn, "corpus", "transcript-1") == []


def test_a_repeated_corpus_scoped_rejection_is_readable_at_corpus_scope(conn):
    # 8.7's other worked case: "if the user repeatedly rejects an association between
    # their authoring school and application documents, the product can lower the role
    # or weight of author-affiliation evidence across that corpus."
    for index, file_id in enumerate(("app-1", "app-2", "app-3")):
        a_rejection(
            conn, scope="corpus", subject="corpus", file_id=file_id,
            field_key="authored_by", value_id="value-columbia",
            observed_at=f"2026-08-2{index}T09:00:00+00:00",
        )
    records = learning_records(conn, "corpus", "corpus")
    assert len(records) == 3
    assert {row["proposal_class"] for row in records} == {PROPOSAL_CLASS}
    assert {row["polarity"] for row in records} == {"reject"}
    # The three are distinguishable from one another by basis, so "repeatedly" is
    # countable by the consumer that weights. P6 weights nothing: 3.7's weights are
    # injected (Task 11) and this module publishes none.
    assert len({row["basis_key"] for row in records}) == 3
    # The corpus record is not a file-scoped one, and the file-scoped read is empty.
    assert learning_records(conn, "file", "app-1") == []


# --- what a correction record must carry ------------------------------------------


def test_a_correction_writes_all_five_of_p1s_correction_fields(conn):
    a_rejection(conn)
    row = conn.execute("SELECT * FROM events").fetchone()
    for column in CORRECTION_FIELDS:
        assert row[column] is not None and row[column] != ""
    assert row["proposal_class"] == PROPOSAL_CLASS
    assert row["polarity"] == "reject"
    assert row["correction_scope"] == "file"
    assert row["correction_subject"] == "file-1"
    assert row["basis_key"] == basis_key(
        file_id="file-1", field_key="subject", value_id="value-busib-4300"
    )


def test_the_polarity_chooses_p6s_own_event_type_and_no_other(conn):
    a_rejection(conn)
    a_rejection(conn, action="confirm_fact", polarity="accept", evidence_refs=())
    types = [row["event_type"] for row in conn.execute(
        "SELECT event_type FROM events ORDER BY event_id"
    )]
    assert types == ["fact rejection", "fact creation"]


def test_the_rejection_is_stored_with_the_evidence_that_produced_it(conn):
    a_rejection(conn, evidence_refs=(REF, OTHER_REF))
    row = conn.execute("SELECT explanation FROM events").fetchone()
    explanation = json.loads(row["explanation"])
    # 8.7: "Rejected groups, rejected destination matches, rejected labels, and
    # rejected residual recommendations must be stored with the evidence that
    # produced them."
    assert explanation["evidence_refs"] == [REF, OTHER_REF]
    assert explanation["proposal_class"] == PROPOSAL_CLASS
    assert explanation["action"] == "reject_fact"


def test_a_rejection_without_evidence_is_refused(conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(conn, evidence_refs=())
    assert event_count(conn) == 0


def test_a_correction_with_no_user_is_refused(conn):
    # `learning_records` filters `user_id IS NOT NULL`. A correction stored without one
    # is storable and permanently unreadable -- a silently lost user gesture.
    with pytest.raises(MalformedCorrection):
        a_rejection(conn, user_id="")
    assert event_count(conn) == 0


def test_an_unknown_polarity_is_refused(conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(conn, polarity="maybe")
    assert event_count(conn) == 0


def test_an_unnamed_action_is_refused(conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(conn, action="")
    assert event_count(conn) == 0


def test_p6_does_not_branch_on_the_action_it_is_handed(conn):
    # P13 owns the action vocabulary. P6 stores the string and branches on polarity.
    a_rejection(conn, action="disable_suggestion_type")
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is True


# --- the negatives 8.7 turns on ----------------------------------------------------


def test_the_correction_and_its_evidence_can_never_be_removed(conn):
    a_rejection(conn)
    # P1 enforces R6 by trigger, not by convention -- verified live: both raise
    # IntegrityError("events is append-only (R6, 8.2)").
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM events")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE events SET explanation = '{}'")
    assert event_count(conn) == 1


def test_suppression_is_versionless_and_survives_a_new_plan_version(conn):
    # I4: "a rejection in plan v2 has to stop the same proposal in v3 ... which is why
    # the store is a versionless projection over `events`."
    columns = {row[1] for row in conn.execute("PRAGMA table_info(events)")}
    assert "plan_version" not in columns
    assert "plan_id" not in columns
    parameters = inspect.signature(is_suppressed).parameters
    assert "plan_version" not in parameters
    assert set(parameters) == {
        "conn", "scope", "subject_id", "file_id", "field_key", "value_id"
    }
    assert "plan_version" not in inspect.signature(basis_key).parameters


def test_p6_performs_no_global_training_on_the_users_corpus(conn):
    # 8.7: "The product should not silently train a global model on a user's private
    # corpus." An accumulator at module scope is what that would look like, so there
    # is none -- checked by introspection, not by reading the source text.
    for name, value in vars(learning_module).items():
        if name.startswith("__"):
            continue
        assert not isinstance(value, (dict, list, set, bytearray)), name


def test_the_subsystem_is_named_in_exactly_one_module_and_it_is_not_this_one(conn):
    # M8: `subsystem = "P6"` is written once, in `facts.authorship`. This module gets
    # it from `event_defaults` and never spells it. Exact equality, not substring:
    # the module docstring may name P6; no module-level VALUE may be it.
    literals = {v for v in vars(learning_module).values() if isinstance(v, str)}
    assert "P6" not in literals
    a_rejection(conn)
    assert conn.execute("SELECT subsystem FROM events").fetchone()["subsystem"] == "P6"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_learning.py -v`

Expected: **FAIL** — collection error, `ModuleNotFoundError: No module named 'facts.learning'`. All
28 tests error at import.

- [ ] **Step 3: Write the implementation**

```python
# src/facts/learning.py
"""8.7 correction learning -- the query-before-propose guard (I4).

TWO HALVES, AND ONLY ONE OF THEM CAN FIRE TODAY.

READ (binding now).  8.7's failure mode is literal: without stored negative feedback
the system "will repeatedly resurface the same attractive but incorrect grouping."
I4 states P6's obligation as: before writing a `file_facts` row that would revive a
`rejected` claim, query the learning store; on an unreset reject, leave the `rejected`
row in place and do not propose the same (field, value) again.  `is_suppressed` is
that query.  It ships with the fact tables because a guard that arrives after the
first fact is written has already failed once.

WRITE (built, unreachable).  Corrections arrive through P13's `review_action`, and
P13 does not exist.  `record_correction` is the surface P13 will route a fact-level
gesture into; nothing in this plan calls it, and P6's tests drive it directly.  Owed
to P13's wave: the gesture surface, the inspect/reset UI, the routing decision, and
the call to `database_agent.learning.reset_preferences`.

P6 MINTS NO 8.2 EVENT TYPE HERE.  A user correction is keyed by `proposal_class` and
`basis_key` -- two ordinary columns beside 8.2's eleven -- never by a type of its own.
The two types used are P6's authored pair from `facts.authorship`, both already among
8.2's reserved nineteen, so nothing is registered.

P1 STORES, P6 INTERPRETS.  P1's own docstring is explicit that it "derives no polarity,
compares no basis_key, interprets no proposal_class".  Suppressing a proposal is the
acting part's rule, applied here.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from database_agent.events import append_event
from database_agent.learning import learning_records
from evidence_shape.canonical import canonical_json
from facts.authorship import AUTHORED_EVENT_TYPES, event_defaults

#: I4's equivalence table. P6 owns proposal class `fact`; its basis is the claim.
#: `group`, `membership`, `branch`, `placement`, `residual` and `privacy` belong to
#: P9, P10, P11 and P7, and a record at one of those classes is not P6's to read.
PROPOSAL_CLASS: str = "fact"

#: I4: "polarity in accept | reject ... supplied by the acting part, never inferred".
#: Every rule below turns on finding an *unreset reject*; a reader that could not
#: separate rejections from approvals would have to parse explanation free text.
POLARITIES: tuple[str, str] = ("accept", "reject")
ACCEPT, REJECT = POLARITIES

#: P6's two 8.2 names, taken from Task 1's tuple rather than respelled here. Both are
#: reserved names, spelled with a space; `fact_creation` would raise at the writer.
CREATION, REJECTION = AUTHORED_EVENT_TYPES


class MalformedCorrection(Exception):
    """Refused at the writer. `events` is append-only, so a bad row cannot be repaired."""


def basis_key(*, file_id: str, field_key: str, value_id: str) -> str:
    """I4's `(file_id, field, value_id)`, serialized once -- here, and nowhere else.

    Canonical JSON rather than a delimiter join (not injective: a `|` inside a part
    would collide two claims and suppress a proposal the user never rejected) and
    rather than a digest (8.7 requires the user "be able to inspect or reset learned
    preferences", and an opaque basis is not inspectable).  `canonical_json` sorts
    keys, so the argument order at the call site cannot change the stored key.

    Member set, dossier hash and display label are NOT in the basis (I4).
    """
    return canonical_json(
        {"field_key": field_key, "file_id": file_id, "value_id": value_id}
    )


def is_suppressed(conn: sqlite3.Connection, *, scope: str, subject_id: str,
                  file_id: str, field_key: str, value_id: str) -> bool:
    """True when an unreset rejection of exactly this claim stands at this scope.

    I4's query-before-propose, applied in order: ignore records at the wrong
    `proposal_class`; ignore records whose `basis_key` does not match; honour a later
    reset; and on a `polarity = reject` record that no later reset covers, do not
    emit.  An `accept` at the same basis is not a suppression and is not read as one.

    The reset is honoured by `learning_records` itself -- it applies the cutoff and
    returns nothing below it.  This function does not re-derive it: a second place
    the cutoff rule lives is a second place it can drift.

    Read-only.  It appends no event, writes no fact, and mutates nothing.
    """
    key = basis_key(file_id=file_id, field_key=field_key, value_id=value_id)
    for row in learning_records(conn, scope, subject_id):
        if row["proposal_class"] != PROPOSAL_CLASS:
            continue
        if row["basis_key"] != key:
            continue
        if row["polarity"] == REJECT:
            return True
    return False


def record_correction(conn: sqlite3.Connection, *, action: str, scope: str, subject: str,
                      polarity: str, file_id: str, field_key: str, value_id: str,
                      evidence_refs: Iterable[str], user_id: str,
                      observed_at: str) -> int:
    """Author the fact-level consequence of one user correction; P1 writes it (M8).

    P13's stand-in until P13 exists.  `action` is P13's gesture name: P6 stores the
    string in the explanation and branches on `polarity`, never on `action` -- the
    action vocabulary is P13's and P6 does not coin a name another part owns.

    `subject` is not derived from `file_id`.  Five of 8.7's six scopes have no file,
    so the correction's subject is always the caller's to supply.

    `scope` is validated by P1's writer against `CORRECTION_SCOPES`, which is the one
    place the six are spelled.  P6 keeps no copy.
    """
    if polarity not in POLARITIES:
        raise MalformedCorrection(
            f"polarity {polarity!r} is not one of {POLARITIES}; I4 requires it be "
            "supplied by the acting part and never inferred"
        )
    if not action:
        raise MalformedCorrection("action is required; it is P13's gesture name")
    if not user_id:
        raise MalformedCorrection(
            "user_id is required: learning_records filters `user_id IS NOT NULL`, so a "
            "correction stored without one is storable and permanently unreadable"
        )
    refs = tuple(evidence_refs)
    if polarity == REJECT and not refs:
        raise MalformedCorrection(
            "8.7 requires a rejection be stored with the evidence that produced it"
        )
    key = basis_key(file_id=file_id, field_key=field_key, value_id=value_id)
    explanation = canonical_json({
        "action": action,
        "basis_key": key,
        "evidence_refs": list(refs),
        "polarity": polarity,
        "proposal_class": PROPOSAL_CLASS,
    })
    payload = event_defaults(
        event_type=REJECTION if polarity == REJECT else CREATION,
        observed_at=observed_at,
        explanation=explanation,
        file_id=file_id,
        user_id=user_id,
        correction_scope=scope,
        correction_subject=subject,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS,
        basis_key=key,
    )
    return append_event(conn, **payload)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_learning.py -v`

Expected: **PASS** — 28 passed.

- [ ] **Step 5: Confirm the guard is reachable and the write half is not**

Run:

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
import inspect, facts.learning as L
print('read half :', [n for n in ('PROPOSAL_CLASS','basis_key','is_suppressed') if hasattr(L,n)])
print('write half:', 'record_correction' in vars(L))
print('module holds no accumulator:', not any(
    isinstance(v, (dict, list, set)) for n, v in vars(L).items() if not n.startswith('__')))
"
```

Expected: `read half : ['PROPOSAL_CLASS', 'basis_key', 'is_suppressed']`,
`write half: True`, `module holds no accumulator: True`.

Then confirm nothing in `src/facts/` calls the write half — it is P13's to call:

```bash
cd "/Users/jy/GRAPH AGENT" && grep -rn "record_correction" src/ | grep -v "src/facts/learning.py"
```

Expected: **no output.** A hit means some module invented a correction P13 has not routed.

- [ ] **Step 6: Commit**

```bash
git add src/facts/learning.py tests/p6/test_p6_learning.py
git commit -m "feat(P6): 8.7 query-before-propose over P1's learning records (I4)"
```

---
### Task 23: §8.8 plan versioning — what belongs to a plan version and what does not

**Files:**
- Create: `src/facts/plan_versions.py`
- Test: `tests/p6/test_p6_plan_versions.py`

**Interfaces:**
- Consumes: `facts.values` — `ensure_value`, `VALUE_ORIGINS`, and the `values` table;
  `facts.file_facts` — `FILE_FACTS_COLUMNS`, `FACT_ORIGINS`, `write_fact`;
  `facts.fields` — `create_fields`; `facts.cache` — `fact_cache_key`;
  `database_agent.supersede.SUPERSEDE_COLUMNS`.
- Produces: `PLAN_VERSIONED: tuple[str, ...]` (`display_label`, `aliases`),
  `SHARED_ACROSS_PLAN_VERSIONS: tuple[str, ...]`,
  `VALUE_RENDERINGS_COLUMNS: tuple[str, ...]`, `create_plan_version_tables(conn) -> None`,
  `display_label(conn, *, value_id, plan_version) -> str`,
  `set_display_label(conn, *, value_id, plan_version, label) -> None`.

**Done-means:** none numbered; §8.8's obligations.

---

**The whole task is one sentence of the design, and its two halves point opposite ways.** §8.8,
verbatim: *"A new plan should never silently reclassify or move old files. It creates a new set of
placement recommendations subject to review. The evidence database remains shared across plan
versions, but the destination tree and user policy define which projections are valid in each
version."*

- **The negative.** Nothing P6 stores as a *record* is plan-versioned. A new plan version
  re-resolves nothing, invalidates nothing and reclassifies nothing. This is the half that matters,
  and it is enforced by absence: none of P6's four record tables has a plan-version column, so
  there is no place a version could be written even by a later mistake.
- **The positive.** §8.8's list of what a plan version captures includes *"User labels and
  aliases"*. So the **rendering** of a value is the plan's: `UChicago` and `University of Chicago`
  are two labels for one value, and choosing between them is a plan-version decision that must
  leave the value and every fact pointing at it untouched.

**Why the rendering gets its own table, and why that is not a fifth record table.** Task 3 puts
`display_label` on the `values` row. If `set_display_label` wrote there, then changing a label in
plan v3 would rewrite a row that v2 shares — which is precisely the silent cross-version mutation
§8.8 forbids. The rendering therefore lives in a **plan-version-keyed side table**,
`value_renderings`, and the `values` row keeps the version-independent default Task 3 gives it. The
result is that the shared/versioned split is checkable from `PRAGMA table_info` alone, the same
reviewer-checkable-negative-contract principle Task 4 uses for paths and destinations.

> **Contradiction found, and flagged rather than papered over.** The skeleton's architecture
> paragraph says P6 *"owns **four** tables"*. This task adds a fifth, and Task 19 already adds one
> too (its recorded deterministic pass — its Files block reads *"modify `src/facts/schema.py`"*).
> The line should read **four record tables**: `fields`, `values`, `file_facts`, `unresolved` are
> the records, and `value_renderings` and Task 19's pass record are auxiliary. If a reviewer wants
> the count kept literally at four, the only alternative is putting per-version labels on the
> `values` row, and that alternative breaks §8.8. Flagging, not deciding.

> **Second, smaller contradiction.** Task 23's Files block lists no `modify src/facts/schema.py`,
> while Tasks 2–5 and 19 all list it. So this task declares its own DDL in `plan_versions.py` and
> publishes `create_plan_version_tables`, rather than editing a file its Files block does not name.
> **One line is then owed to whoever assembles `schema.py`:** its aggregate creator must call
> `create_plan_version_tables`, or the table exists only where a test creates it.

**`aliases` is named in `PLAN_VERSIONED` and has no writer, on purpose.** §8.8 versions *"labels and
aliases"*, so the boundary declaration names both. But the skeleton publishes accessors for the
label only, and Task 3 already uses `values.aliases` for something different — §0's taxonomy
aliases, which a merge records and which are **identity**, not rendering (Task 3: *"a merge records
an alias and deletes nothing"*). Inventing a `set_aliases` here would either duplicate that column
or build a surface no Done-means asks for. So `PLAN_VERSIONED` **declares** the boundary and
`value_renderings` carries only the column that has a writer — D3's rule against a writer-less
column, applied. The per-version alias override is **owed, not stubbed**; a named test in Task 25
should hold it open.

**P6 mints no §8.2 event type for a rendering change, and appends none.** §8.8's diff — *"Applications
was renamed to Admissions"* — belongs to the plan-version object, and that object is P10's and
P12's. `destination-tree edit` is already a reserved name and is not P6's to write. A test asserts
the event count is unchanged across a rendering change.

**Two cross-task assumptions this task makes explicit.** First, `facts.schema.create_facts_schema` —
the name follows P4's `evidence_shape.schema.create_evidence_schema` exactly, but it appears in no
`Interfaces:` block, so if Wave A names its creator otherwise, this one import changes. Second,
`write_fact` is called with exactly the ten keywords its Task 4 contract publishes, and with no P1
`files` row present (P1 puts no foreign key on `events.file_id` — verified). If Task 4 lands an
eleventh required keyword or a files-row precondition, it breaks this test *and* Task 20's resolver,
which is the right place for that to surface.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_plan_versions.py
"""8.8: the evidence database is shared across plan versions; the rendering is not.

The negative half is the one that matters and it is enforced by absence -- no P6
record table has a plan-version column, so there is nowhere a version could be
written. The positive half is one side table holding the label a plan version chose.
"""
from __future__ import annotations

import pytest

from database_agent import db
from database_agent.supersede import SUPERSEDE_COLUMNS
from evidence_shape.observation import observation_key
from facts.cache import fact_cache_key
from facts.fields import create_fields
from facts.file_facts import FACT_ORIGINS, FILE_FACTS_COLUMNS, write_fact
from facts.plan_versions import (
    PLAN_VERSIONED,
    SHARED_ACROSS_PLAN_VERSIONS,
    VALUE_RENDERINGS_COLUMNS,
    create_plan_version_tables,
    display_label,
    set_display_label,
)
from facts.schema import create_facts_schema
from facts.values import ensure_value

CONTENT_HASH = "sha256:" + "a" * 64
FORBIDDEN = ("path", "destination", "folder", "node", "group")
RECORD_TABLES = ("fields", "values", "file_facts", "unresolved")

REF = observation_key(
    content_hash=CONTENT_HASH,
    extractor_name="pdf.text",
    locator="heading:page=1/heading=2",
    raw_value="University of Chicago",
)
CACHE_KEY = fact_cache_key(
    content_hash=CONTENT_HASH,
    extractor_version="1.0.0",
    analysis_tier="native",
    model_identifier=None,
    prompt_fingerprint=None,
)


@pytest.fixture()
def conn(tmp_path):
    connection = db.open_database(tmp_path / "p6-plan-versions.db")
    db.create_schema(connection)
    create_facts_schema(connection)
    create_fields(connection)
    create_plan_version_tables(connection)
    yield connection
    connection.close()


@pytest.fixture()
def value_id(conn) -> str:
    # 3.8's target_school, which D1 ratifies into the catalogue. 2.8's three
    # renderings of one institution are the design's own worked example.
    return ensure_value(
        conn,
        field_key="target_school",
        canonical_value="University of Chicago",
        first_evidence_ref=REF,
        origin="automatic",
    )


@pytest.fixture()
def fact_id(conn, value_id) -> str:
    return write_fact(
        conn,
        file_id="file-1",
        content_hash=CONTENT_HASH,
        field_key="target_school",
        value_id=value_id,
        reliability_state="direct",
        origin=FACT_ORIGINS[0],
        evidence_refs=(REF,),
        cache_key=CACHE_KEY,
        active=True,
    )


def snapshot(connection) -> dict[str, list[str]]:
    """Every table's every row, byte-for-byte.

    Rows are compared as sorted reprs: SQLite guarantees no row order without an
    ORDER BY, `ORDER BY rowid` is not available on every table, and sorting the
    tuples themselves would compare None against str. Sorted reprs are total,
    deterministic, and still catch a single changed byte in any column.
    """
    names = [
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        )
    ]
    return {
        name: sorted(
            repr(tuple(row)) for row in connection.execute(f'SELECT * FROM "{name}"')
        )
        for name in names
    }


# --- the declaration -------------------------------------------------------------


def test_the_two_tuples_name_the_8_8_split_and_do_not_overlap():
    assert PLAN_VERSIONED == ("display_label", "aliases")
    assert set(PLAN_VERSIONED).isdisjoint(SHARED_ACROSS_PLAN_VERSIONS)
    for name in RECORD_TABLES:
        assert name in SHARED_ACROSS_PLAN_VERSIONS
    for name in ("evidence_refs", "reliability_state", "supersession_history"):
        assert name in SHARED_ACROSS_PLAN_VERSIONS


def test_what_is_declared_shared_is_actually_a_shared_record(conn):
    # 8.8: "The evidence database remains shared across plan versions."
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    for name in RECORD_TABLES:
        assert name in tables
    assert "evidence_refs" in FILE_FACTS_COLUMNS
    assert "reliability_state" in FILE_FACTS_COLUMNS
    for column in SUPERSEDE_COLUMNS:
        assert column in FILE_FACTS_COLUMNS


def test_no_record_table_carries_a_plan_version_column(conn):
    # Enforced by absence: there is nowhere a version could be written.
    for name in RECORD_TABLES:
        columns = {row[1] for row in conn.execute(f'PRAGMA table_info("{name}")')}
        assert "plan_version" not in columns, name
        assert "plan_id" not in columns, name


def test_no_plan_versioned_attribute_is_a_fact_column():
    # A fact is a claim, not a rendering. If `display_label` ever became a
    # `file_facts` column, a label change would rewrite facts.
    assert set(FILE_FACTS_COLUMNS).isdisjoint(PLAN_VERSIONED)


def test_the_renderings_table_is_keyed_by_version_and_carries_no_destination(conn):
    assert VALUE_RENDERINGS_COLUMNS == ("value_id", "plan_version", "display_label")
    columns = [row[1] for row in conn.execute("PRAGMA table_info(value_renderings)")]
    assert tuple(columns) == VALUE_RENDERINGS_COLUMNS
    # 3.14's negative contract, applied to this table too.
    for column in columns:
        for forbidden in FORBIDDEN:
            assert forbidden not in column, column


# --- the rendering ---------------------------------------------------------------


def test_two_plan_versions_render_one_value_two_ways(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(
        conn, value_id=value_id, plan_version="v3", label="University of Chicago"
    )
    assert display_label(conn, value_id=value_id, plan_version="v2") == "UChicago"
    assert (
        display_label(conn, value_id=value_id, plan_version="v3")
        == "University of Chicago"
    )


def test_a_version_that_chose_nothing_falls_back_and_never_borrows(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    # v3 chose nothing, so it renders the value's own label -- NOT v2's choice. A
    # rendering is scoped to the version that made it.
    assert display_label(conn, value_id=value_id, plan_version="v3") != "UChicago"


def test_the_fallback_chain_ends_at_the_canonical_string(conn, value_id):
    # Total by construction: 5.5 needs something to show for every value, and a
    # renderer that can return None shows nothing on a version that chose nothing.
    rendered = display_label(conn, value_id=value_id, plan_version="v9")
    assert isinstance(rendered, str) and rendered != ""


def test_re_rendering_the_same_version_replaces_rather_than_duplicates(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(conn, value_id=value_id, plan_version="v2", label="U Chicago")
    rows = conn.execute("SELECT COUNT(*) AS n FROM value_renderings").fetchone()["n"]
    assert rows == 1
    assert display_label(conn, value_id=value_id, plan_version="v2") == "U Chicago"


def test_a_rendering_for_a_value_that_does_not_exist_is_refused(conn):
    with pytest.raises(ValueError):
        set_display_label(
            conn, value_id="no-such-value", plan_version="v2", label="Ghost"
        )
    rows = conn.execute("SELECT COUNT(*) AS n FROM value_renderings").fetchone()["n"]
    assert rows == 0


def test_a_rendering_without_a_plan_version_is_refused(conn, value_id):
    with pytest.raises(ValueError):
        set_display_label(conn, value_id=value_id, plan_version="", label="UChicago")


# --- the guarantee -----------------------------------------------------------------


def test_a_new_plan_version_changes_no_shared_record_byte_for_byte(conn, value_id, fact_id):
    before = snapshot(conn)
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(
        conn, value_id=value_id, plan_version="v3", label="University of Chicago"
    )
    after = snapshot(conn)
    assert set(before) == set(after)
    for name in after:
        if name == "value_renderings":
            continue
        assert after[name] == before[name], name
    # And the versioned table is the only thing that moved.
    assert len(after["value_renderings"]) == 2
    assert before["value_renderings"] == []


def test_the_value_itself_is_untouched_by_a_rendering_change(conn, value_id):
    before = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    assert tuple(after) == tuple(before)


def test_every_fact_pointing_at_the_value_still_resolves_unchanged(conn, value_id, fact_id):
    before = [
        tuple(row)
        for row in conn.execute("SELECT * FROM file_facts WHERE value_id = ?", (value_id,))
    ]
    assert len(before) == 1
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = [
        tuple(row)
        for row in conn.execute("SELECT * FROM file_facts WHERE value_id = ?", (value_id,))
    ]
    assert after == before


def test_a_rendering_change_re_resolves_nothing_and_invalidates_no_cache_key(
    conn, value_id, fact_id
):
    # 3.4's cache key has five parts and a plan version is none of them, so a plan
    # edit cannot invalidate a fact. 8.8: "A new plan should never silently
    # reclassify or move old files."
    before = conn.execute(
        "SELECT cache_key FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()["cache_key"]
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute(
        "SELECT cache_key FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()["cache_key"]
    assert after == before == CACHE_KEY


def test_p6_appends_no_event_for_a_rendering_change(conn, value_id, fact_id):
    # 8.8's diff belongs to the plan-version object, which is P10's and P12's. P6
    # mints no 8.2 type here and writes none of anyone else's.
    before = conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    assert after == before
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_plan_versions.py -v`

Expected: **FAIL** — collection error, `ModuleNotFoundError: No module named 'facts.plan_versions'`.
All 16 tests error at import.

- [ ] **Step 3: Write the implementation**

```python
# src/facts/plan_versions.py
"""8.8 -- what belongs to a plan version, and what does not.

8.8's guarantee is one sentence: "A new plan should never silently reclassify or move
old files. It creates a new set of placement recommendations subject to review. The
evidence database remains shared across plan versions, but the destination tree and
user policy define which projections are valid in each version."

THE NEGATIVE, which is the half that matters.  Nothing P6 stores as a record is
plan-versioned: `fields`, value identity, `file_facts`, `unresolved`, every evidence
ref, every reliability state and all supersession history are shared.  Enforced by
ABSENCE -- no record table carries a plan-version column, so there is nowhere a
version could be written even by a later mistake.  A new plan version therefore
re-resolves nothing, invalidates nothing and reclassifies nothing; 3.4's cache key has
five parts and a plan version is none of them.

THE POSITIVE.  8.8's plan version captures "User labels and aliases", so the RENDERING
of a value is the plan's.  `UChicago` and `University of Chicago` are two labels for
one value, and choosing between them must leave the value and every fact pointing at
it untouched.  That is why the rendering lives here, in a plan-version-keyed side
table, and not on the `values` row: writing it there would rewrite a row every other
plan version shares, which is the silent cross-version mutation 8.8 forbids.

`aliases` is declared in PLAN_VERSIONED and has no writer here on purpose.  8.8
versions "labels and aliases", so the boundary names both; but `values.aliases` is
already 0's taxonomy aliases, which are identity rather than rendering, and no
Done-means asks for a per-version alias override.  Declaring the boundary is this
module's job; building a column with no writer is not (D3).

P6 MINTS NO 8.2 EVENT TYPE HERE and appends none.  8.8's plan diff ("Applications was
renamed to Admissions") belongs to the plan-version object, and that object is P10's
and P12's.  `destination-tree edit` is a reserved name and is not P6's to write.
"""
from __future__ import annotations

import sqlite3

#: 8.8: "User labels and aliases" are captured BY a plan version. A declaration of the
#: boundary, not a column list -- only `display_label` has a writer today.
PLAN_VERSIONED: tuple[str, ...] = ("display_label", "aliases")

#: Everything a plan version must NOT be able to change. The four record tables, plus
#: the three fact properties 8.8's guarantee turns on.
SHARED_ACROSS_PLAN_VERSIONS: tuple[str, ...] = (
    "fields",
    "values",
    "file_facts",
    "unresolved",
    "evidence_refs",
    "reliability_state",
    "supersession_history",
)

#: The one plan-version-keyed table P6 owns. Not a fifth RECORD table: it holds no
#: claim, no evidence and no reliability state, and nothing reads it to decide a fact.
VALUE_RENDERINGS_COLUMNS: tuple[str, ...] = ("value_id", "plan_version", "display_label")

_DDL = """
CREATE TABLE IF NOT EXISTS value_renderings (
    value_id      TEXT NOT NULL,
    plan_version  TEXT NOT NULL,
    display_label TEXT NOT NULL,
    PRIMARY KEY (value_id, plan_version)
)
"""


def create_plan_version_tables(conn: sqlite3.Connection) -> None:
    """Create the rendering table inside P1's database. Creates no other part's.

    Owed: `facts.schema`'s aggregate creator must call this, or the table exists only
    where a test creates it.
    """
    conn.execute(_DDL)


def _value_row(conn: sqlite3.Connection, value_id: str) -> sqlite3.Row:
    # `values` is a SQLite keyword; the identifier must be quoted or the statement is
    # a syntax error rather than a missing table.
    row = conn.execute(
        'SELECT canonical_value, display_label FROM "values" WHERE value_id = ?',
        (value_id,),
    ).fetchone()
    if row is None:
        raise ValueError(
            f"no value {value_id!r}: a rendering with no value to render would be a "
            "label the user can never trace back to a fact"
        )
    return row


def set_display_label(conn: sqlite3.Connection, *, value_id: str, plan_version: str,
                      label: str) -> None:
    """Record the label THIS plan version shows for one value. Touches no record.

    Writes only `value_renderings`: no fact, no value, no field, no event. A repeat
    for the same version replaces that version's choice rather than accumulating a
    second one -- a value renders one way per version or the display is ambiguous.
    """
    if not plan_version:
        raise ValueError("plan_version is required: a rendering belongs to a version")
    if not label:
        raise ValueError(
            "label is required: an empty rendering is not a choice, and clearing one "
            "is a different operation than making one"
        )
    _value_row(conn, value_id)
    conn.execute(
        "INSERT INTO value_renderings (value_id, plan_version, display_label) "
        "VALUES (?, ?, ?) "
        "ON CONFLICT (value_id, plan_version) DO UPDATE SET "
        "display_label = excluded.display_label",
        (value_id, plan_version, label),
    )


def display_label(conn: sqlite3.Connection, *, value_id: str,
                  plan_version: str) -> str:
    """This version's rendering, else the value's own label, else its canonical string.

    Total by construction: 5.5 shows the user "three schools, five terms, twelve course
    branches" before they commit, and a renderer that can return None shows nothing for
    a value whose version made no choice.

    The chain never borrows another version's label. A rendering is scoped to the
    version that chose it, exactly as 8.8 scopes everything else a plan captures.
    """
    chosen = conn.execute(
        "SELECT display_label FROM value_renderings "
        "WHERE value_id = ? AND plan_version = ?",
        (value_id, plan_version),
    ).fetchone()
    if chosen is not None:
        return chosen["display_label"]
    value = _value_row(conn, value_id)
    return value["display_label"] or value["canonical_value"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_plan_versions.py -v`

Expected: **PASS** — 16 passed.

- [ ] **Step 5: Confirm the negative from the schema alone**

A reviewer must be able to check §8.8's guarantee without reading a test:

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
import tempfile; from pathlib import Path
from database_agent import db
from facts.schema import create_facts_schema
from facts.plan_versions import create_plan_version_tables, PLAN_VERSIONED
c = db.open_database(Path(tempfile.mkdtemp())/'x.db'); db.create_schema(c)
create_facts_schema(c); create_plan_version_tables(c)
for t in ('fields','values','file_facts','unresolved'):
    cols = [r[1] for r in c.execute(f'PRAGMA table_info(\"{t}\")')]
    print(t, 'plan_version' in cols, sorted(set(cols) & set(PLAN_VERSIONED)))
"
```

Expected: `False []` for `fields`, `file_facts` and `unresolved`; `values` prints
`False ['aliases', 'display_label']` — the version-independent defaults Task 3 owns, which is the
one place the two tuples touch and the reason `value_renderings` exists.

- [ ] **Step 6: Commit**

```bash
git add src/facts/plan_versions.py tests/p6/test_p6_plan_versions.py
git commit -m "feat(P6): 8.8 plan versioning -- shared records, versioned renderings"
```
