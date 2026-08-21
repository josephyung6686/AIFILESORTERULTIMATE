# P7 — Privacy and consent gate — PLAN, Tasks 15–22

> This file is one section of P7's implementation plan. Tasks 1–14 are written by other authors
> against the same [`PLAN-SKELETON.md`](PLAN-SKELETON.md); everything they publish is consumed here
> under the names the skeleton's `Interfaces:` blocks fix. Format and standard are
> [`../P5-extractors/PLAN.md`](../P5-extractors/PLAN.md) and
> [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md).

**Verified against the live substrate, 2026-08-22.** Every P1–P5 signature quoted below was read
with `inspect.signature` against the shipped packages, not from a PLAN. `pytest tests/ -q` collects
**1292 tests** and P1–P5 are green. The two facts that most change what is written here:

- `database_agent.files_table.set_sensitivity_state(conn, file_id, *, state: dict, author: str,
  component_version: str) -> None` **exists** (D2). P7 calls it; P7 takes no writer protocol.
- **Thirteen tables** carry a `BEFORE DELETE … RAISE(ABORT)` trigger — `events`, `evidence`,
  `text_units`, `extraction_runs`, `exclusion_verdicts` and P2's eight `bundle_*` tables — and
  `database_agent.db._deny_events_history_loss` is installed as a `set_authorizer` hook that returns
  `SQLITE_DENY` for `SQLITE_DROP_TABLE events` and for `SQLITE_DROP_TRIGGER` on
  `events_no_update` / `events_no_delete` / `events_no_replace`. A `DELETE FROM events` raises
  `sqlite3.IntegrityError: events is append-only (R6, 8.2)`; a `DROP TRIGGER events_no_delete`
  raises `sqlite3.DatabaseError: not authorized`. Done-means 8 is provable against the substrate.

---

## Three rulings that bind this section, applied rather than restated

**D3 (ratified) changes WHY `delete_derived` raises.** The sentence is:

> `events` is append-only forever. Derived projections may be tombstoned; "derived" is a **literal
> enumerated table-and-column list** and `delete_derived` raises on anything outside it. **No
> tombstone column is built** until P13 drives it.

So Task 15 writes the enumeration down — that is the substance of the task — and `delete_derived`
raises on **both** sides of it: `ScopeNotDerived` outside the list, so an unenumerated table is a red
test rather than a silent miss, and `UnratifiedResolution` inside it, because nothing is built.
**No writer-less tombstone column is added.** `files.sensitivity_state` spent this entire project as
a column nothing wrote and produced a second wrong value one column away; a migration later is
cheaper than that defect class.

**D2 (ratified) inverts one of Task 21's guards.** P6 OQ11 is **CLOSED**. A guard asserting it is
open fails the day this plan is executed. Task 21 asserts the D2 shape instead:
`ClassificationRecord` keyed `(file_id, content_hash)` is authoritative, `files.sensitivity_state`
is its projection written through P1's `set_sensitivity_state`, `src/privacy/` issues **no
`UPDATE files`** of its own, and `unclassified` never reaches that column.

**The detector is unwritten (D2), so `Denied(unclassified)` is the ordinary path.** No task in any
plan produces a rule set. Every task below is built for that: Task 17's verdict on an unclassified
file, Task 20's fixture 2, and Task 22's path-one classification — which the test writes itself,
standing in for the detector and saying so in its docstring — all assume it.

---

## The rename these tasks apply, which the skeleton applied only to Tasks 12–14

The skeleton's **SETTLED 2026-08-22** paragraph renames `src/privacy/facts_seam.py` to
`src/privacy/classification_store.py` and the `SensitivityFacts` protocol to a concrete
`ClassificationStore`, then says *"Tasks 12, 13 and 14 change only the import and the type name."*
**Tasks 16, 17 and 18 name `facts_seam.SensitivityFacts` in their `Consumes` blocks too**, and the
paragraph does not mention them. They are renamed here on the same ruling. Reported.

`ClassificationStore` as consumed below:

```text
ClassificationStore(conn)
  current(file_id, content_hash)                  -> ClassificationRecord | None
  current_fact_id(file_id, content_hash)          -> str | None
  write(record)                                   -> fact_id
  supersede(old_fact_id, new_fact_id, reason)     -> None
  history(file_id)                                -> list[ClassificationRecord]
```

`current_fact_id` is **added by this section** and Task 4 must publish it. P1's `mark_superseded`
keys on a `record_id` column (`src/database_agent/supersede.py`), so superseding a classification
needs the prior row's id and `ClassificationRecord`'s eight SPEC §2 fields do not carry one.
Without it Task 16's `reclassify` cannot supersede, which is Done-means 2's user half. Reported.

---

## Tasks

### Task 15: Revocation, the retraction limit, and `delete_derived`'s refusal (I6/D3)

**Files:**
- Create: `src/privacy/revocation.py`
- Test: `tests/p7/test_p7_revocation.py`

**Interfaces:**
- Consumes: `privacy.audit.audit_records_for(conn, *, file_id=None, release_id=None,
  consent_request_id=None) -> list[AuditRecord]`, `privacy.audit.AUDIT_FIELDS`,
  `privacy.authorship.CONSENT_REVOKED`, `privacy.authorship.event_defaults(*, event_type, **fields)
  -> dict[str, object]`, `privacy.policy.Policy`,
  `privacy.policy.revoke_consent(conn, policy, scope, *, user_id, component_version, observed_at)
  -> str`, `database_agent.events.append_event(conn, **fields) -> int`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`revocation.py`):
  - `RELEASED: str = "released"` — the `AuditRecord.outcome` value a prior release carries.
  - `PriorRelease` — frozen: `model: str`, `provider: str`, `when: str`,
    `excerpts: tuple[tuple[str, str], ...]`.
  - `RevocationResult` — frozen: `effective_from: str`, `prior_releases: tuple[PriorRelease, ...]`,
    `retraction_limit: str`.
  - `revoke(conn, policy, scope, *, user_id, component_version, observed_at, retraction_limit,
    files_in_scope) -> RevocationResult`.
  - `DERIVED_PROJECTIONS: Mapping[str, tuple[str, ...]]` — D3's literal enumeration.
  - `NOT_DERIVED: Mapping[str, str]` — table → the reason it is outside the enumeration.
  - `DerivedScope` — frozen: `table: str`, `column: str`.
  - `DeleteDerivedRefused`, `ScopeNotDerived`, `UnratifiedResolution`, `MissingRetractionLimit`.
  - `delete_derived(scope: DerivedScope) -> NoReturn`.

**Done-means:** 8.

**Two signatures this task pins for its neighbours, because it cannot be written without them.**

1. **`policy.revoke_consent(conn, policy, scope, *, user_id, component_version, observed_at) -> str`
   records the withdrawal and returns the new `policy_version`. It appends no event.** The
   `consent_revoked` event is appended **here**, once, by `revoke`. Task 5's `Produces` block spells
   the function `revoke_consent(...)` with an ellipsis, and Task 15's `Consumes` block lists
   `authorship.CONSENT_REVOKED` and `database_agent.events.append_event` alongside it — a list that
   is only coherent if the event append is `revoke`'s. Two appends would put one act in the log
   twice, and §8.4's `prior_releases` is read back out of that log.
2. **`AuditRecord.model` stores the `ModelTarget` as a mapping** with `locality`, `model_id` and
   `provider`. SPEC §8 requires `prior_releases[]` to carry *"model, provider, when, which
   excerpts"*; a bare model-name string leaves `PriorRelease.provider` unfillable, and §8.4's
   audit field is *"which model received the data"*, which a provider-less identifier does not
   answer for a hosted model.

**`retraction_limit` is a required keyword with no default, and the module holds no sentence.**
§8.4 states the `must`: *"Revocation cannot necessarily retract data already sent to an external
provider, so the product must communicate that distinction clearly."* The SPEC's *Deferred* table
puts the **wording** outside this contract — *"Consent-prompt and retraction-limit wording | §8.4 |
UX copy"* — while the plan's own Deferred row keeps the obligation: *"The **presence** of
`retraction_limit` is asserted; the wording is not."* So `revoke` refuses an empty one with
`MissingRetractionLimit` and stores whatever P13 supplies. Task 21 asserts no such sentence exists
as a module-level string anywhere under `src/privacy/`.

**`files_in_scope` is a required keyword with no default, and it is where Open question 3 lives.**
*"What is a 'corpus area'? … Consent grants cannot be scoped until this is named."* `revoke` cannot
enumerate the files a scope covers, and it must not guess; the caller supplies
`Callable[[str], Sequence[str]]` and P7 defines no area.

**`prior_releases` is every release in scope, not only those under the revoked policy version.**
§8.4's purpose is to tell the user what has already left the device. A list filtered to one policy
version answers a narrower question than the one the user is asking, and the audit log carries the
`policy_version` on each record for a reader who wants the narrower one.

**What D3 makes this task write down.** The enumeration is the deliverable:

```text
DERIVED_PROJECTIONS
  evidence     raw_value, normalized_value, context_before, context_after
  text_units   text
```

Those five columns are where a scanned passport's OCR text actually lives — verified against the
live schema, `PRAGMA table_xinfo(evidence)` and `PRAGMA table_xinfo(text_units)`. `NOT_DERIVED`
names the four live tables that are outside it and why, so the refusal is legible:

```text
NOT_DERIVED
  events            append-only forever (R6, §8.2, D3). Three triggers and an authorizer hook.
  files             sensitivity_state is a classification projection (D2); reclassify, do not delete.
  extraction_runs   the record THAT a run happened, not what it read (§2.4's empty-versus-absent).
  exclusion_verdicts  P3's refusal record; deleting it deletes the evidence of a refusal.
```

**No tombstone column is added.** `delete_derived` raises on both sides of the enumeration and
writes nothing. A test asserts that neither `evidence` nor `text_units` grew a deletion column.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_revocation.py
"""Done-means 8, and I6 held open under D3.

`retraction_limit` and the derived enumeration are the two halves of this task. The
first is a `must` whose wording is deferred, so the test asserts PRESENCE and refuses
to assert words. The second is D3's literal list, so the test asserts the list, the
refusal on both sides of it, and that no tombstone column was built.
"""
import sqlite3

import pytest

from database_agent.events import append_event
from database_agent.files_table import get_file, record_file

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import CONSENT_REVOKED, SUBSYSTEM
from privacy.policy import Policy
from privacy.revocation import (
    DERIVED_PROJECTIONS, NOT_DERIVED, RELEASED, DeleteDerivedRefused, DerivedScope,
    MissingRetractionLimit, PriorRelease, RevocationResult, ScopeNotDerived,
    UnratifiedResolution, delete_derived, revoke,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"

#: §8.4's sentence is the product's obligation and P13's copy. The test supplies it
#: the way P13 will, so nothing in `src/privacy/` has to hold a sentence.
RETRACTION_LIMIT = (
    "Revoking this policy stops future calls. It cannot retract the excerpts already "
    "sent to Acme, listed above."
)

_TYPED_DEFAULTS = {
    "audit_id": None,
    "release_id": "release-1",
    "policy_version": "policy-1",
    "plan_version": "plan-1",
    "stage": "grouping",
    "outcome": RELEASED,
    "operation_mode": "cloud_assisted",
    "authorizing_policy": "policy-1",
    "file_sensitivity": "personal_non_sensitive",
    "excerpts_included": (("obs-key-1", "0-19"),),
    "redaction_applied": False,
    "redaction_manifest": (),
    "model": {"locality": "cloud", "model_id": "acme-large", "provider": "Acme"},
    "content_hashes": ("sha256:abc",),
    "content_hash": "sha256:abc",
    "prompt_fingerprint": "fp-1",
    "file_id": "file-1",
    "file_ids": ("file-1",),
    "group_id": None,
    "consent_request_id": None,
    "user_id": None,
    "observed_at": FIXED_CLOCK,
    "appended_at": FIXED_CLOCK,
}


def an_audit_record(**over) -> AuditRecord:
    """Built from `AUDIT_FIELDS`, never from a literal keyword list.

    Task 10 owns SPEC §7's nineteen names and asserts they match §7 name for name.
    Constructing from the published tuple means a field this task never reads can be
    respelled without breaking it, while a field it DOES read disappearing fails
    here, loudly, at the seam that cares.
    """
    missing = [name for name in AUDIT_FIELDS if name not in _TYPED_DEFAULTS]
    assert not missing, (
        f"AUDIT_FIELDS names {missing} and this test has no value for them; "
        "SPEC §7 changed and Task 15 needs a value, not a default")
    values = {name: _TYPED_DEFAULTS[name] for name in AUDIT_FIELDS}
    values.update(over)
    return AuditRecord(**values)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


@pytest.fixture()
def released(p7_conn) -> str:
    """One prior release, in the log, under the policy about to be revoked."""
    return str(append_audit(p7_conn, an_audit_record(), author=SUBSYSTEM,
                            component_version=COMPONENT))


def go(conn, **over) -> RevocationResult:
    base = dict(user_id="joseph", component_version=COMPONENT, observed_at=LATER,
                retraction_limit=RETRACTION_LIMIT,
                files_in_scope=lambda scope: ("file-1",))
    base.update(over)
    return revoke(conn, a_policy(), "Academics", **base)


# --- forward-only -----------------------------------------------------------

def test_effective_from_is_the_moment_of_revocation(p7_conn, released):
    # §8.4 via SPEC §8: "effective_from  future gate calls only."
    assert go(p7_conn).effective_from == LATER


def test_a_revocation_mints_a_new_policy_version(p7_conn, released):
    # The forward-only property is carried by the BINDING TERM, not by a flag: a
    # release minted under policy-1 still consumes against policy-1 (Task 12's
    # ledger) and a request made after this revocation is decided against the new
    # version, which is what makes Task 13's `policy_revoked` reachable. Those two
    # halves are asserted in Tasks 12 and 13; the seam that makes them true is here.
    go(p7_conn)
    row = p7_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id DESC",
        (CONSENT_REVOKED,)).fetchone()
    import json
    payload = json.loads(row["explanation"])
    assert payload["revoked_policy_version"] == "policy-1"
    assert payload["policy_version"] != "policy-1"


def test_the_revocation_is_authored_by_p7(p7_conn, released):
    # M8: the acting part authors, P1 writes.
    go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_REVOKED,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["user_id"] == "joseph"
    assert row["observed_at"] == LATER


# --- the prior-release list -------------------------------------------------

def test_prior_releases_name_model_provider_time_and_excerpts(p7_conn, released):
    # SPEC §8: "prior_releases[]  from the audit log: model, provider, when, which
    # excerpts." The audit log is what makes the retraction limit specific rather
    # than a generic disclaimer.
    result = go(p7_conn)
    assert result.prior_releases == (
        PriorRelease(model="acme-large", provider="Acme", when=FIXED_CLOCK,
                     excerpts=(("obs-key-1", "0-19"),)),
    )


def test_a_denied_record_is_not_a_prior_release(p7_conn, released):
    append_audit(p7_conn, an_audit_record(outcome="denied", release_id=None),
                 author=SUBSYSTEM, component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


def test_prior_releases_come_from_the_audit_log_and_not_a_second_store(p7_conn):
    # Nothing else in P7 records what left the device, and §8.4 forbids a second
    # copy of the text: "excerpts_included stores (observation_key, span) pairs ...
    # not a second copy of the text."
    assert go(p7_conn).prior_releases == ()
    append_audit(p7_conn, an_audit_record(), author=SUBSYSTEM,
                 component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


def test_a_file_outside_the_scope_is_not_listed(p7_conn, released):
    # Open question 3 is held by the injection: P7 defines no corpus area, so a
    # resolver that returns nothing produces an empty list rather than everything.
    assert go(p7_conn, files_in_scope=lambda scope: ()).prior_releases == ()


def test_prior_releases_are_ordered_oldest_first(p7_conn, released):
    append_audit(p7_conn, an_audit_record(release_id="release-2", observed_at=LATER),
                 author=SUBSYSTEM, component_version=COMPONENT)
    result = go(p7_conn)
    assert [r.when for r in result.prior_releases] == [FIXED_CLOCK, LATER]


# --- the retraction limit ---------------------------------------------------

def test_the_retraction_limit_is_always_present(p7_conn, released):
    assert go(p7_conn).retraction_limit == RETRACTION_LIMIT


def test_an_empty_retraction_limit_is_refused(p7_conn, released):
    # §8.4 is a `must`: the product "must communicate that distinction clearly".
    # Presence is enforced; wording is P13's (SPEC Deferred).
    for empty in ("", "   "):
        with pytest.raises(MissingRetractionLimit):
            go(p7_conn, retraction_limit=empty)


def test_the_wording_is_the_callers_and_not_the_modules(p7_conn):
    # SPEC Deferred: "Consent-prompt and retraction-limit wording ... UX copy."
    import privacy.revocation as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("__") and isinstance(value, str)]
    assert not [text for text in held if "retract" in text.lower()]


# --- the substrate proves Done-means 8, not P7's restraint -------------------

def test_deleting_an_audit_record_aborts(p7_conn, released):
    # P1's `events_no_delete`. Done-means 8: revoke "never deletes an audit record",
    # and the proof is the database refusing, not P7 declining to try.
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        p7_conn.execute("DELETE FROM events WHERE event_id = ?", (int(released),))


def test_updating_an_audit_record_aborts(p7_conn, released):
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        p7_conn.execute("UPDATE events SET subsystem = 'P8' WHERE event_id = ?",
                        (int(released),))


def test_the_append_only_triggers_cannot_be_dropped(p7_conn):
    # `db._deny_events_history_loss` is installed by `open_database` as a
    # `set_authorizer` hook: SQLITE_DROP_TRIGGER on the three names, and DROP TABLE
    # events, both return SQLITE_DENY.
    for statement in ("DROP TRIGGER events_no_delete",
                      "DROP TRIGGER events_no_update",
                      "DROP TRIGGER events_no_replace",
                      "DROP TABLE events"):
        with pytest.raises(sqlite3.DatabaseError, match="not authorized"):
            p7_conn.execute(statement)


def test_a_revocation_adds_a_row_and_removes_none(p7_conn, released):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    go(p7_conn)
    after = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after == before + 1
    assert p7_conn.execute("SELECT count(*) c FROM events WHERE event_id = ?",
                           (int(released),)).fetchone()["c"] == 1


# --- D3: the enumeration, and delete_derived refusing on both sides ----------

def test_delete_derived_refuses_an_enumerated_scope_and_names_i6(p7_conn):
    # D3 ratified the DIRECTION and built nothing: "No tombstone column is built
    # until P13 drives it." The surface exists; the semantics do not.
    with pytest.raises(UnratifiedResolution) as caught:
        delete_derived(DerivedScope("text_units", "text"))
    assert "I6" in str(caught.value)
    assert "D3" in str(caught.value)


def test_delete_derived_refuses_an_unenumerated_scope_by_name(p7_conn):
    # The point of a LITERAL enumeration: a table nobody listed is a red test, not a
    # silent miss. `ScopeNotDerived` is a different failure from "not built yet" and
    # the two must not be readable as one.
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("extraction_runs", "completeness"))
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("evidence", "reliability"))


def test_both_refusals_share_one_base_so_delete_derived_never_succeeds(p7_conn):
    for scope in (DerivedScope("text_units", "text"),
                  DerivedScope("nowhere", "nothing")):
        with pytest.raises(DeleteDerivedRefused):
            delete_derived(scope)


def test_events_is_named_as_outside_the_enumeration(p7_conn):
    # D3's first clause. `events` is not merely absent from DERIVED_PROJECTIONS; the
    # reason is written down, because absence and oversight look identical.
    assert "events" not in DERIVED_PROJECTIONS
    assert "events" in NOT_DERIVED
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("events", "explanation"))


def test_sensitivity_state_is_reclassified_and_never_deleted(p7_conn):
    # D2: the column is a PROJECTION of P7's authoritative record. The supported
    # user act is Task 16's reclassification, which supersedes; deleting a projection
    # would leave the authoritative record and its mirror disagreeing.
    assert "files" not in DERIVED_PROJECTIONS
    assert "files" in NOT_DERIVED
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("files", "sensitivity_state"))


def test_the_enumeration_names_only_live_tables_and_live_columns(p7_conn):
    # An enumeration that drifts from the schema is worse than none: it would refuse
    # a real column and accept a name that no longer exists.
    for table, columns in DERIVED_PROJECTIONS.items():
        live = {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}
        assert live, table
        assert set(columns) <= live, (table, sorted(set(columns) - live))
    for table in NOT_DERIVED:
        assert {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}


def test_the_enumerated_columns_are_where_ocr_text_actually_lives(p7_conn):
    # I6's own worked case: "The product cannot ship unable to forget a scanned
    # passport's OCR text." That text is `text_units.text` and `evidence.raw_value`
    # with M5's two context fields; nothing else in the schema holds it.
    assert DERIVED_PROJECTIONS["text_units"] == ("text",)
    assert DERIVED_PROJECTIONS["evidence"] == (
        "raw_value", "normalized_value", "context_before", "context_after")


def test_no_tombstone_column_was_built(p7_conn):
    # D3's second clause, and the whole reason it is a clause: `files.sensitivity_state`
    # spent this project as a column nothing wrote and produced a second wrong value
    # one column away. A migration later is cheaper than that.
    for table in DERIVED_PROJECTIONS:
        columns = {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}
        for token in ("tombstone", "tombstoned", "deleted", "deleted_at",
                      "redacted_at", "forgotten"):
            assert token not in columns, (table, token)


def test_thirteen_tables_already_refuse_a_delete(p7_conn):
    # The substrate D3 lands on top of, counted rather than asserted from memory:
    # events, evidence, text_units, extraction_runs, exclusion_verdicts and P2's
    # eight bundle_* tables. "Deletion later is always available; un-deletion never
    # is" is a posture the schema already holds.
    from eval_harness.store import create_eval_schema
    from scan_agent.schema import create_scan_schema
    create_scan_schema(p7_conn)
    create_eval_schema(p7_conn)
    guarded = {row["tbl_name"] for row in p7_conn.execute(
        "SELECT tbl_name, sql FROM sqlite_master WHERE type = 'trigger'")
        if "BEFORE DELETE" in (row["sql"] or "")}
    assert len(guarded) == 13
    assert {"events", "evidence", "text_units", "extraction_runs",
            "exclusion_verdicts"} <= guarded


def test_p7_creates_no_trigger_of_its_own_on_events(p7_conn):
    # P1 owns R6. A second set of triggers under a second set of names is the
    # duplication that has cost this project most.
    names = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'trigger' AND tbl_name = 'events'")}
    assert names == {"events_no_update", "events_no_delete", "events_no_replace"}
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_revocation.py -v`
Expected: FAIL — `ImportError: cannot import name 'DERIVED_PROJECTIONS' from 'privacy.revocation'`
(the module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/revocation.py`**

```python
# src/privacy/revocation.py
"""§8.4's revocation, its stated limit, and the derived-data deletion D3 left unbuilt.

Three things are decided here and each is a quotation rather than a choice:

- **Revocation is forward-only.** §8.4 gives the user the right to "revoke a policy
  for future runs". A revocation appends; it never rewrites the record of what has
  already happened, because §8.4 also requires the product to say what already left,
  and that is unsatisfiable once the send record is erasable.
- **The retraction limit is mandatory and its wording is not P7's.** §8.4: "Revocation
  cannot necessarily retract data already sent to an external provider, so the product
  must communicate that distinction clearly." The SPEC defers the copy to P13; this
  module enforces presence and holds no sentence.
- **`delete_derived` refuses, on both sides of a literal list (D3).** §8.4 gives the
  user the right to "review and delete local derived data" and §8.2 forbids updating
  or deleting an event. D3 ratifies the direction — events append-only forever,
  derived projections tombstonable, "derived" a literal enumeration — and ratifies
  that NOTHING IS BUILT until P13 drives it. So the surface exists and the semantics
  do not, and an unenumerated scope fails differently from an unbuilt one.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import NoReturn

from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from privacy.audit import audit_records_for
from privacy.authorship import CONSENT_REVOKED, event_defaults
from privacy.policy import Policy, revoke_consent

#: The `AuditRecord.outcome` value that means content left the device (SPEC §7).
RELEASED: str = "released"


class MissingRetractionLimit(ValueError):
    """§8.4 requires the distinction be communicated; a blank statement is not one."""


class DeleteDerivedRefused(Exception):
    """`delete_derived` never succeeds today. It refuses for one of two reasons."""


class ScopeNotDerived(DeleteDerivedRefused):
    """The scope is outside D3's literal enumeration.

    This is the reason the list is literal rather than a predicate: a table nobody
    enumerated produces a red test here instead of being quietly deleted from, or
    quietly skipped, depending on which way a clever rule happened to fall.
    """


class UnratifiedResolution(DeleteDerivedRefused):
    """The scope IS derived, and no tombstone column is built (D3, I6).

    The name is the one the plan skeleton published and it is kept so the contract
    does not move; what it now reports is *unbuilt*, not *unratified*. D3 settled the
    direction on 2026-08-21 and deliberately built nothing, because a writer-less
    column is the defect `files.sensitivity_state` demonstrated for the length of
    this project.
    """


@dataclass(frozen=True)
class PriorRelease:
    """One row of SPEC §8's `prior_releases[]`: "model, provider, when, which excerpts"."""

    model: str
    provider: str
    when: str
    excerpts: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RevocationResult:
    """SPEC §8's return: forward-only, evidenced, and limited."""

    effective_from: str
    prior_releases: tuple[PriorRelease, ...]
    retraction_limit: str


@dataclass(frozen=True)
class DerivedScope:
    """One table-and-column D3's enumeration may or may not name."""

    table: str
    column: str


#: D3's literal enumerated table-and-column list. These five columns are where the
#: text extracted from a file's bytes actually lives -- checked against the live
#: schema, not against a PLAN. Anything else is `NOT_DERIVED` and refused by name.
DERIVED_PROJECTIONS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "evidence": ("raw_value", "normalized_value", "context_before", "context_after"),
    "text_units": ("text",),
})

#: The live tables outside the enumeration, each with the reason. Absence and
#: oversight are indistinguishable, so the reason is written down.
NOT_DERIVED: Mapping[str, str] = MappingProxyType({
    "events": (
        "append-only forever (R6, §8.2, D3). Three triggers and an authorizer hook "
        "enforce it, and §8.4's retraction limit is unsatisfiable without the log."
    ),
    "files": (
        "`sensitivity_state` is a projection of P7's authoritative ClassificationRecord "
        "(D2). The supported user act is reclassification, which supersedes."
    ),
    "extraction_runs": (
        "the record THAT a run happened, not what it read. §2.4 distinguishes an empty "
        "extraction result from an extractor that does not exist, and deleting the run "
        "row collapses the two."
    ),
    "exclusion_verdicts": (
        "P3's refusal record. Deleting it deletes the evidence that a refusal occurred, "
        "which is the whole record a protected container leaves behind (11 §4b)."
    ),
})


def revoke(conn: sqlite3.Connection, policy: Policy, scope: str, *, user_id: str,
           component_version: str, observed_at: str, retraction_limit: str,
           files_in_scope: Callable[[str], Sequence[str]]) -> RevocationResult:
    """Withdraw consent for `scope`, forward only, and say what already left.

    `files_in_scope` has no default. Open question 3 -- "What is a 'corpus area'?
    ... Consent grants cannot be scoped until this is named" -- is unanswered, so
    the resolver is the caller's and P7 defines no area.

    `retraction_limit` has no default either, and for the opposite reason: §8.4
    makes the statement mandatory and the SPEC defers its wording, so presence is
    enforced here and the words come from P13.
    """
    if not retraction_limit or not retraction_limit.strip():
        raise MissingRetractionLimit(
            "§8.4: revocation 'cannot necessarily retract data already sent to an "
            "external provider, so the product must communicate that distinction "
            "clearly' -- an empty statement does not communicate it"
        )
    new_version = revoke_consent(conn, policy, scope, user_id=user_id,
                                 component_version=component_version,
                                 observed_at=observed_at)
    prior = _prior_releases(conn, files_in_scope(scope))
    append_event(conn, **event_defaults(
        event_type=CONSENT_REVOKED,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "scope": scope,
            "revoked_policy_version": policy.policy_version,
            "policy_version": new_version,
            "effective_from": observed_at,
            "prior_release_count": len(prior),
            "retraction_limit": retraction_limit,
        }),
    ))
    return RevocationResult(effective_from=observed_at, prior_releases=prior,
                            retraction_limit=retraction_limit)


def _prior_releases(conn: sqlite3.Connection,
                    file_ids: Sequence[str]) -> tuple[PriorRelease, ...]:
    """Every release in scope, oldest first, read out of the one audit log.

    Not filtered to the revoked policy version. §8.4's purpose is to tell the user
    what has already been sent; a list narrowed to one version answers a different
    question, and each record carries `policy_version` for a reader who wants it.
    """
    found: list[tuple[str, int, PriorRelease]] = []
    for file_id in file_ids:
        for record in audit_records_for(conn, file_id=file_id):
            if record.outcome != RELEASED:
                continue
            target = record.model
            found.append((record.observed_at, int(record.audit_id), PriorRelease(
                model=target["model_id"],
                provider=target["provider"],
                when=record.observed_at,
                excerpts=tuple(tuple(pair) for pair in record.excerpts_included),
            )))
    found.sort(key=lambda item: (item[0], item[1]))
    return tuple(entry for _, _, entry in found)


def delete_derived(scope: DerivedScope) -> NoReturn:
    """§8.4's "review and delete local derived data" -- surfaced, and unbuilt (D3, I6).

    Raises `ScopeNotDerived` for anything outside `DERIVED_PROJECTIONS` and
    `UnratifiedResolution` for anything inside it. There is no third branch: no
    tombstone column exists, this function writes nothing, and P13 is the part that
    will drive the migration that gives it one.
    """
    columns = DERIVED_PROJECTIONS.get(scope.table)
    if columns is None or scope.column not in columns:
        reason = NOT_DERIVED.get(scope.table)
        raise ScopeNotDerived(
            f"{scope.table}.{scope.column} is not in D3's enumerated derived list "
            f"{ {table: list(cols) for table, cols in DERIVED_PROJECTIONS.items()} }"
            + (f"; {reason}" if reason else "")
        )
    raise UnratifiedResolution(
        f"{scope.table}.{scope.column} is derived (D3), and no tombstone column is "
        "built. D3, ratified 2026-08-21, settled the direction and deliberately "
        "built nothing until P13 drives it; I6 named the §8.4-versus-§8.2 conflict "
        "this resolves. Deletion later is always available; un-deletion never is."
    )
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_revocation.py -v`
Expected: PASS — 22 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–15 green, and 1292 P1–P5 tests still green (P7 modified no file
belonging to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/revocation.py tests/p7/test_p7_revocation.py
git commit -m "feat(P7): revocation, the retraction limit, and delete_derived refusing on both sides of D3's enumeration"
```

---

### Task 16: Reclassification, and §8.7's query-before-classify

**Files:**
- Create: `src/privacy/learning_seam.py`
- Test: `tests/p7/test_p7_learning_seam.py`

**Interfaces:**
- Consumes: `database_agent.learning.learning_records(conn, scope, subject_id) -> list[sqlite3.Row]`,
  `.SCOPES`, `database_agent.events.CORRECTION_FIELDS`, `.CORRECTION_SCOPES`, `.append_event`,
  `database_agent.files_table.set_sensitivity_state`,
  `evidence_shape.canonical.canonical_json`,
  `privacy.classification.ClassificationRecord` (the skeleton's `facts_seam.SensitivityFacts` —
  see the rename note above), `privacy.classification_store.ClassificationStore`, `.mirror_state`,
  `privacy.authorship.SUBSYSTEM`, `.CLASSIFICATION_ASSIGNED`, `.CLASSIFICATION_SUPERSEDED`,
  `.event_defaults`, `privacy.vocabulary.check_handling_class`.
- Produces (`learning_seam.py`):
  - `PROPOSAL_CLASS: str = "privacy"`, `FILE_SCOPE: str = "file"`, `ACCEPT`, `REJECT`.
  - `RECORDED_ACTIONS: tuple[str, ...]` (SPEC *Correction learning*'s six),
    `RECORDED_ACTION_SOURCES: Mapping[str, str]` (each identifier → the SPEC's own phrase).
  - `basis_key_for(file_id, handling_class) -> str`.
  - `suppressed(conn, file_id, handling_class) -> bool`.
  - `assign(conn, record, *, store, component_version) -> ClassificationRecord | None`.
  - `reclassify(conn, file_id, handling_class, reason, *, store, content_hash, protected,
    evidence_refs, user_id, component_version, observed_at, correction_scope=FILE_SCOPE)
    -> ClassificationRecord`.
  - `UnknownRecordedAction`, `check_recorded_action(value) -> str`.

**Done-means:** part of 2 (the user-revision half), and the §8.7 obligation.

**`assign` is added by this task and it is what makes the Done-means falsifiable.** The skeleton's
`Produces` block lists `suppressed` and stops, and 10-i4's Done-means is *"a fixture with one
unresected reject at the stated `basis_key` produces **zero re-emissions** of that proposal."* A
predicate returning `True` is not zero re-emissions; something has to be the emission that does not
happen. `assign` is the system-side write — the one a detector would call — and it returns `None`
when suppressed. Reported as an addition.

**Suppression guards `assign` and never `reclassify`.** 10-i4's table: *"**P7** | Before assigning a
handling class the user has already set or rejected at this scope | Do not re-prompt the same
classification."* The thing suppressed is the product re-proposing, not the user acting. A
`reclassify` that consulted the suppression store would refuse the user's own correction because
they had already made it.

**`assign` appends no correction field, and that is why it can never be its own suppressor.**
P1's `learning_records` filters `user_id IS NOT NULL`, so a system assignment is structurally
incapable of becoming a learning record. Only `reclassify`, which carries a `user_id`, writes one.

**One event per act, and the event is the rejection.** A reclassification over an existing
classification appends exactly one `classification_superseded` with `polarity = "reject"` at
`basis_key_for(file_id, prior_class)` — §8.7's negative example, *"stored with the evidence that
produced them"* — and supersedes through P1's three columns. A reclassification where nothing was
classified appends one `classification_assigned` with `polarity = "accept"` at the new class. There
is no accept-and-reject pair: 10-i4 rule 4 says *"A `polarity = accept` record at the same
`basis_key` is not a suppression and must not be read as one"*, so a second event would be a row
that changes nothing plus a second place for the two to disagree.

**The keys, not the ids (M14).** *"a per-row `observation_id` dies when the extractor is upgraded,
so a negative example recorded today would silently stop resolving and the same false protection
would return."* `evidence_refs` is a required keyword carrying P4 `observation_key` values; it lands
on the new record and is echoed into the superseding event's explanation as
`rejected_evidence_refs`.

**`correction_scope` defaults to `file`, and only that default is the design's.** §8.7's worked
warning: one transcript belonging in one packet *"should not teach the engine that all transcripts
belong there."* A broader scope is accepted when the caller passes one and is never inferred. Open
question 7 — *"Does repeated reclassification generalize?"* — stays open; nothing here counts
repetitions and Task 21 asserts it.

**`protected` is a required keyword on `reclassify` and is never derived.** SPEC §2:
*"Neighbouring parts should consume the `protected` flag, not infer it from the class"*, and Open
question 1 is unsettled.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_learning_seam.py
"""§8.7's query-before-classify, and reclassification as supersession.

The three assertions 10-i4-learning-ops.md's Done-means names, in its own words:
"a fixture with one unresected reject at the stated `basis_key` produces zero
re-emissions of that proposal ... A different `basis_key` at the same scope still
emits. A reset at that scope+subject allows emission again."
"""
import json

import pytest

from database_agent.events import CORRECTION_FIELDS, CORRECTION_SCOPES, append_event
from database_agent.files_table import get_file, record_file
from database_agent.learning import SCOPES, learning_records, reset_preferences

from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, SUBSYSTEM,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.learning_seam import (
    ACCEPT, FILE_SCOPE, PROPOSAL_CLASS, RECORDED_ACTIONS, RECORDED_ACTION_SOURCES,
    REJECT, UnknownRecordedAction, assign, basis_key_for, check_recorded_action,
    reclassify, suppressed,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
DETECTOR_KEYS = (
    "sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd",
    "sha256:11e3d2a5b8c47f6019a4d3e5c7b2a10f9d8c6b4a3e2f1d0c9b8a7654321fedcba",
)


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """A real P1 row: the classification is keyed on (file_id, content_hash) and a
    synthesized id would not exercise the projection onto `files`."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


def a_record(file_id, content_hash, handling_class="sensitive_personal", **over):
    base = dict(file_id=file_id, content_hash=content_hash,
                handling_class=handling_class, protected=True, basis="detector",
                evidence_refs=DETECTOR_KEYS, reliability_state="validated",
                observed_at=FIXED_CLOCK)
    base.update(over)
    return ClassificationRecord(**base)


def a_user_rejection(conn, file_id, content_hash, *, store):
    """The user downgrading `sensitive_personal`, which is what leaves the reject."""
    return reclassify(conn, file_id, "personal_non_sensitive",
                      "these are my own notes, not an identity record",
                      store=store, content_hash=content_hash, protected=False,
                      evidence_refs=DETECTOR_KEYS, user_id="joseph",
                      component_version=COMPONENT, observed_at=LATER)


# --- the vocabulary ---------------------------------------------------------

def test_the_proposal_class_is_the_one_10_i4_assigns_p7():
    # 10-i4-learning-ops.md's table: `privacy` | `(file_id, handling_class)` | P7.
    assert PROPOSAL_CLASS == "privacy"


def test_the_basis_key_is_file_id_and_handling_class_and_nothing_else():
    key = basis_key_for("file-1", "sensitive_personal")
    assert json.loads(key) == ["file-1", "sensitive_personal"]
    assert basis_key_for("file-1", "sensitive_personal") == key
    assert basis_key_for("file-1", "public_low") != key


def test_the_six_recorded_actions_carry_the_specs_own_words():
    # SPEC Correction learning, "Recorded actions". A paraphrase is a failing test and
    # not an editorial choice -- Task 2's MODE_SEMANTICS discipline, applied here.
    assert len(RECORDED_ACTIONS) == 6
    assert set(RECORDED_ACTION_SOURCES) == set(RECORDED_ACTIONS)
    assert RECORDED_ACTION_SOURCES["reclassify_private"] == (
        "reclassifying a file as private")
    assert RECORDED_ACTION_SOURCES["mark_private_residual_review"] == (
        "mark it as private")
    assert RECORDED_ACTION_SOURCES["downgrade_classification"] == (
        "downgrading a classification")
    assert RECORDED_ACTION_SOURCES["set_policy"] == (
        "granting, changing, or revoking a policy")
    assert RECORDED_ACTION_SOURCES["change_redaction_setting"] == (
        "changing a redaction setting")
    assert RECORDED_ACTION_SOURCES["set_automatic_move_permission"] == (
        "granting or withdrawing an automatic-move permission for protected material")


def test_a_seventh_recorded_action_is_a_load_error():
    assert check_recorded_action("downgrade_classification") == (
        "downgrade_classification")
    with pytest.raises(UnknownRecordedAction):
        check_recorded_action("delete_the_file")


def test_the_default_scope_is_file_and_it_is_one_of_p1s_six():
    # §8.7's worked warning: one transcript belonging in one packet "should not teach
    # the engine that all transcripts belong there."
    assert FILE_SCOPE == "file"
    assert FILE_SCOPE in SCOPES and FILE_SCOPE in CORRECTION_SCOPES


# --- query before classify --------------------------------------------------

def test_an_unrejected_class_is_not_suppressed(p7_conn, file_id):
    assert suppressed(p7_conn, file_id, "sensitive_personal") is False


def test_an_unreset_reject_produces_zero_re_emissions(
        p7_conn, file_id, content_hash, store):
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True

    before = p7_conn.execute(
        "SELECT count(*) c FROM events WHERE event_type = ?",
        (CLASSIFICATION_ASSIGNED,)).fetchone()["c"]
    again = assign(p7_conn, a_record(file_id, content_hash), store=store,
                   component_version=COMPONENT)
    after = p7_conn.execute(
        "SELECT count(*) c FROM events WHERE event_type = ?",
        (CLASSIFICATION_ASSIGNED,)).fetchone()["c"]

    assert again is None
    assert after == before


def test_a_different_basis_key_at_the_same_scope_still_emits(
        p7_conn, file_id, content_hash, store):
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    emitted = assign(
        p7_conn,
        a_record(file_id, content_hash,
                 handling_class="highly_sensitive_credential_bearing"),
        store=store, component_version=COMPONENT)
    assert emitted is not None
    assert emitted.handling_class == "highly_sensitive_credential_bearing"


def test_a_reset_restores_emission(p7_conn, file_id, content_hash, store):
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True
    reset_preferences(p7_conn, FILE_SCOPE, file_id, author=SUBSYSTEM,
                      component_version=COMPONENT, user_id="joseph")
    assert suppressed(p7_conn, file_id, "sensitive_personal") is False
    assert assign(p7_conn, a_record(file_id, content_hash), store=store,
                  component_version=COMPONENT) is not None


def test_p7_does_the_filtering_because_p1s_reader_does_not(
        p7_conn, file_id, content_hash, store):
    # `learning_records(conn, scope, subject_id)` filters on correction_scope,
    # correction_subject and `user_id IS NOT NULL` only. 10-i4 assigns proposal_class
    # and basis_key filtering to the acting part: "Ignores records at the wrong
    # `proposal_class`. Ignores records whose `basis_key` does not match."
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    rows = learning_records(p7_conn, FILE_SCOPE, file_id)
    assert len(rows) == 1
    assert rows[0]["proposal_class"] == PROPOSAL_CLASS
    assert rows[0]["basis_key"] == basis_key_for(file_id, "sensitive_personal")
    assert rows[0]["polarity"] == REJECT
    # Another part's rejection at the same subject is ignored, not counted.
    append_event(p7_conn, event_type="review action routed", subsystem="P13",
                 component_version=COMPONENT, observed_at=LATER,
                 explanation='{"note":"another part"}', user_id="joseph",
                 correction_scope=FILE_SCOPE, correction_subject=file_id,
                 polarity=REJECT, proposal_class="placement",
                 basis_key=basis_key_for(file_id, "sensitive_personal"))
    assert len(learning_records(p7_conn, FILE_SCOPE, file_id)) == 2
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True
    assert suppressed(p7_conn, file_id, "public_low") is False


def test_a_system_assignment_can_never_become_a_learning_record(
        p7_conn, file_id, content_hash, store):
    # P1's reader requires `user_id IS NOT NULL`. A detector's assignment carries no
    # user, so it is structurally incapable of suppressing the next one.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    assert learning_records(p7_conn, FILE_SCOPE, file_id) == []
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_ASSIGNED,)).fetchone()
    for field in CORRECTION_FIELDS:
        assert row[field] is None
    assert row["user_id"] is None


# --- reclassification is supersession, never overwrite ----------------------

def test_reclassify_writes_a_new_user_confirmed_fact(
        p7_conn, file_id, content_hash, store):
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    revised = a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert revised.reliability_state == "user_confirmed"
    assert revised.basis == "user"
    assert revised.handling_class == "personal_non_sensitive"
    assert store.current(file_id, content_hash) == revised


def test_both_records_remain_inspectable(p7_conn, file_id, content_hash, store):
    # §8.2's explicit rule, and §8.4's "can be revised by the user" -- a revision
    # supersedes and both remain available.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    history = store.history(file_id)
    assert [r.handling_class for r in history] == [
        "sensitive_personal", "personal_non_sensitive"]
    assert [r.basis for r in history] == ["detector", "user"]


def test_reclassify_appends_classification_superseded_and_not_an_overwrite(
        p7_conn, file_id, content_hash, store):
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_SUPERSEDED,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["user_id"] == "joseph"
    assert row["polarity"] == REJECT
    assert row["correction_scope"] == FILE_SCOPE
    assert row["correction_subject"] == file_id
    assert row["basis_key"] == basis_key_for(file_id, "sensitive_personal")


def test_a_first_classification_by_the_user_accepts_rather_than_rejects(
        p7_conn, file_id, content_hash, store):
    # Nothing was classified, so there is nothing to reject. One event, and it is an
    # assignment: 10-i4 rule 4 makes an accept-and-reject pair a row that changes
    # nothing plus a second place for the two to disagree.
    reclassify(p7_conn, file_id, "highly_sensitive_credential_bearing",
               "this is my passport", store=store, content_hash=content_hash,
               protected=True, evidence_refs=(), user_id="joseph",
               component_version=COMPONENT, observed_at=LATER)
    assert p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                           (CLASSIFICATION_SUPERSEDED,)).fetchone()["c"] == 0
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_ASSIGNED,)).fetchone()
    assert row["polarity"] == ACCEPT
    assert row["basis_key"] == basis_key_for(
        file_id, "highly_sensitive_credential_bearing")


def test_a_downgrade_stores_the_observation_keys_the_detector_fired_on(
        p7_conn, file_id, content_hash, store):
    # §8.7 and M14: "The key, not the id, is what makes that durable" -- a per-row
    # `observation_id` dies when the extractor is upgraded and the same false
    # protection returns.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    row = p7_conn.execute("SELECT explanation FROM events WHERE event_type = ?",
                          (CLASSIFICATION_SUPERSEDED,)).fetchone()
    payload = json.loads(row["explanation"])
    assert tuple(payload["rejected_evidence_refs"]) == DETECTOR_KEYS
    assert all(ref.startswith("sha256:") for ref in payload["rejected_evidence_refs"])
    assert payload["superseded_handling_class"] == "sensitive_personal"


def test_protected_is_carried_and_never_derived_from_the_class(
        p7_conn, file_id, content_hash, store):
    # SPEC §2, and Open question 1. A caller may mark a `public_low` file protected
    # and this module does not argue.
    record = reclassify(p7_conn, file_id, "public_low", "a scan of my own poster",
                        store=store, content_hash=content_hash, protected=True,
                        evidence_refs=(), user_id="joseph",
                        component_version=COMPONENT, observed_at=LATER)
    assert record.handling_class == "public_low"
    assert record.protected is True


def test_a_reason_is_required(p7_conn, file_id, content_hash, store):
    with pytest.raises(ValueError):
        reclassify(p7_conn, file_id, "public_low", "   ", store=store,
                   content_hash=content_hash, protected=False, evidence_refs=(),
                   user_id="joseph", component_version=COMPONENT, observed_at=LATER)


def test_a_scope_outside_8_7s_six_is_refused(p7_conn, file_id, content_hash, store):
    with pytest.raises(ValueError):
        reclassify(p7_conn, file_id, "public_low", "because", store=store,
                   content_hash=content_hash, protected=False, evidence_refs=(),
                   user_id="joseph", component_version=COMPONENT, observed_at=LATER,
                   correction_scope="everything")


def test_the_projection_onto_files_goes_through_p1s_setter(
        p7_conn, file_id, content_hash, store):
    # D2: `files.sensitivity_state` is the projection of the authoritative record,
    # written through P1's published `set_sensitivity_state`. Task 21 asserts
    # `src/privacy/` issues no `UPDATE files` of its own.
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    state = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert state["handling_class"] == "sensitive_personal"
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    state = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert state["handling_class"] == "personal_non_sensitive"


def test_open_question_7_is_not_answered_here(
        p7_conn, file_id, content_hash, store):
    # OQ7: "§8.7 allows a repeated residual destination to become a corpus-level
    # preference; it does not say whether repeated privacy corrections may raise a
    # sensitivity floor for a class of files." Two rejections stay two file-scoped
    # records; nothing counts them and nothing widens.
    for _ in range(2):
        assign(p7_conn, a_record(file_id, content_hash), store=store,
               component_version=COMPONENT)
        a_user_rejection(p7_conn, file_id, content_hash, store=store)
    for scope in ("corpus", "domain", "group", "node", "template"):
        assert learning_records(p7_conn, scope, file_id) == []
    import privacy.learning_seam as module
    assert not [name for name, value in vars(module).items()
                if not name.startswith("__")
                and isinstance(value, (int, float)) and not isinstance(value, bool)]
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_learning_seam.py -v`
Expected: FAIL — `ImportError: cannot import name 'PROPOSAL_CLASS' from 'privacy.learning_seam'`

- [ ] **Step 3: Write `src/privacy/learning_seam.py`**

```python
# src/privacy/learning_seam.py
"""§8.7's query-before-classify, and reclassification as supersession.

Two directions across one seam. Reading: before the product assigns a handling class
it asks P1 whether the user has already rejected that class for that file, because
10-i4-learning-ops.md puts P7 in the query-before-propose table -- "Before assigning
a handling class the user has already set or rejected at this scope | Do not re-prompt
the same classification". Writing: a user reclassification is a new `user_confirmed`
fact that supersedes the prior one and leaves a negative example behind, because §8.7
requires rejections be "stored with the evidence that produced them".

P1's `learning_records(conn, scope, subject_id)` filters on `correction_scope`,
`correction_subject` and `user_id IS NOT NULL` and nothing else. `proposal_class` and
`basis_key` filtering is the acting part's, by 10-i4's own assignment, so it happens
here.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from types import MappingProxyType

from database_agent.events import CORRECTION_SCOPES, append_event
from database_agent.files_table import set_sensitivity_state
from database_agent.learning import learning_records
from evidence_shape.canonical import canonical_json

from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, SUBSYSTEM, event_defaults,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore, mirror_state
from privacy.vocabulary import check_handling_class

#: 10-i4-learning-ops.md's table: `privacy` | `(file_id, handling_class)` | P7.
PROPOSAL_CLASS: str = "privacy"

#: §8.7's default, and the only scope this module supplies. "one particular transcript
#: belongs in a Columbia packet but should not teach the engine that all transcripts
#: belong there."
FILE_SCOPE: str = "file"

#: 10-i4: "`polarity ∈ accept | reject` ... supplied by the acting part, never inferred".
ACCEPT: str = "accept"
REJECT: str = "reject"

#: SPEC *Correction learning*, "Recorded actions". The identifiers are P7's; the
#: phrases are the SPEC's, held beside them so a later paraphrase is a failing test.
RECORDED_ACTIONS: tuple[str, ...] = (
    "reclassify_private",
    "mark_private_residual_review",
    "downgrade_classification",
    "set_policy",
    "change_redaction_setting",
    "set_automatic_move_permission",
)

RECORDED_ACTION_SOURCES: Mapping[str, str] = MappingProxyType({
    "reclassify_private": "reclassifying a file as private",
    "mark_private_residual_review": "mark it as private",
    "downgrade_classification": "downgrading a classification",
    "set_policy": "granting, changing, or revoking a policy",
    "change_redaction_setting": "changing a redaction setting",
    "set_automatic_move_permission":
        "granting or withdrawing an automatic-move permission for protected material",
})


class UnknownRecordedAction(ValueError):
    """A §8.7 action outside the SPEC's six. A value outside the set is a load error."""


def check_recorded_action(value: str) -> str:
    if value not in RECORDED_ACTIONS:
        raise UnknownRecordedAction(
            f"{value!r} is not one of SPEC Correction learning's six recorded "
            f"actions {RECORDED_ACTIONS}")
    return value


def basis_key_for(file_id: str, handling_class: str) -> str:
    """10-i4's `basis_key` for `proposal_class = privacy`: `(file_id, handling_class)`.

    P1 stores `basis_key` as one opaque TEXT column, so the pair is composed here as
    canonical JSON -- the same encoding P4 uses for its own comparable bytes, so two
    parts never disagree about how a tuple becomes a string.
    """
    return canonical_json([file_id, handling_class])


def suppressed(conn: sqlite3.Connection, file_id: str, handling_class: str) -> bool:
    """Has the user rejected this exact classification for this file, unreset?

    P1's reader already honours a later `reset_preferences` as a cutoff, so a reset
    restores emission without anything being deleted (R6).
    """
    key = basis_key_for(file_id, handling_class)
    for row in learning_records(conn, FILE_SCOPE, file_id):
        if row["proposal_class"] != PROPOSAL_CLASS:
            continue                                     # 10-i4 rule 1
        if row["basis_key"] != key:
            continue                                     # 10-i4 rule 2
        if row["polarity"] == REJECT:                    # 10-i4 rule 4
            return True
    return False


def assign(conn: sqlite3.Connection, record: ClassificationRecord, *,
           store: ClassificationStore,
           component_version: str) -> ClassificationRecord | None:
    """The system-side write, guarded by §8.7. Returns None when suppressed.

    None is the zero re-emission 10-i4's Done-means requires: "a fixture with one
    unresected reject at the stated `basis_key` produces zero re-emissions of that
    proposal". Nothing is written and no event is appended, so the log shows the
    proposal was not made rather than that it was made and hidden.

    This appends no `correction_*` field and no `user_id`, so a system assignment can
    never become the learning record that suppresses the next one.
    """
    check_handling_class(record.handling_class)
    if suppressed(conn, record.file_id, record.handling_class):
        return None
    store.write(record)
    _project(conn, record, component_version=component_version)
    append_event(conn, **event_defaults(
        event_type=CLASSIFICATION_ASSIGNED,
        file_id=record.file_id,
        content_hash=record.content_hash,
        component_version=component_version,
        observed_at=record.observed_at,
        explanation=canonical_json({
            "handling_class": record.handling_class,
            "protected": record.protected,
            "basis": record.basis,
            "reliability_state": record.reliability_state,
            "evidence_refs": list(record.evidence_refs),
        }),
    ))
    return record


def reclassify(conn: sqlite3.Connection, file_id: str, handling_class: str,
               reason: str, *, store: ClassificationStore, content_hash: str,
               protected: bool, evidence_refs: Sequence[str], user_id: str,
               component_version: str, observed_at: str,
               correction_scope: str = FILE_SCOPE) -> ClassificationRecord:
    """§8.4's "can be revised by the user", as a supersession and a negative example.

    `protected` is a parameter and is never derived from `handling_class`. Open
    question 1 -- "Is `protected` exactly the top two handling classes?" -- is
    unsettled, and SPEC §2 says outright: "Neighbouring parts should consume the
    `protected` flag, not infer it from the class."

    `evidence_refs` carries P4 `observation_key` values (M14) -- the keys the detector
    fired on. They land on the new record and are echoed into the superseding event so
    §8.7's "stored with the evidence that produced them" has somewhere to be true.
    """
    check_handling_class(handling_class)
    if not reason or not reason.strip():
        raise ValueError(
            "§8.2 retains 'the old observation and the reason it was superseded'; "
            "a revision without a reason cannot satisfy it")
    if correction_scope not in CORRECTION_SCOPES:
        raise ValueError(
            f"correction_scope {correction_scope!r} is not one of §8.7's six "
            f"{tuple(sorted(CORRECTION_SCOPES))}")
    prior = store.current(file_id, content_hash)
    prior_fact_id = store.current_fact_id(file_id, content_hash)
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis="user", evidence_refs=tuple(evidence_refs),
        reliability_state="user_confirmed", observed_at=observed_at)
    fact_id = store.write(record)
    if prior is not None and prior_fact_id is not None:
        store.supersede(prior_fact_id, fact_id, reason)
    _project(conn, record, component_version=component_version)

    if prior is None:
        event_type, polarity, subject = CLASSIFICATION_ASSIGNED, ACCEPT, handling_class
    else:
        event_type, polarity, subject = (
            CLASSIFICATION_SUPERSEDED, REJECT, prior.handling_class)
    append_event(conn, **event_defaults(
        event_type=event_type,
        file_id=file_id,
        content_hash=content_hash,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "handling_class": handling_class,
            "protected": protected,
            "reason": reason,
            "superseded_handling_class": None if prior is None else prior.handling_class,
            "rejected_evidence_refs": list(evidence_refs),
        }),
        correction_scope=correction_scope,
        correction_subject=file_id,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS,
        basis_key=basis_key_for(file_id, subject),
    ))
    return record


def _project(conn: sqlite3.Connection, record: ClassificationRecord, *,
             component_version: str) -> None:
    """D2's projection: P7 authors, P1 stores. `src/privacy/` writes no `UPDATE files`."""
    set_sensitivity_state(conn, record.file_id, state=mirror_state(record),
                          author=SUBSYSTEM, component_version=component_version)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_learning_seam.py -v`
Expected: PASS — 21 passed

- [ ] **Step 5: Commit**

```bash
git add src/privacy/learning_seam.py tests/p7/test_p7_learning_seam.py
git commit -m "feat(P7): reclassification as supersession, and 8.7 query-before-classify"
```

---
