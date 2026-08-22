# P7 — Privacy and consent gate — PLAN, Tasks 15–22

> This file is one section of P7's implementation plan. Tasks 1–14 are written by other authors
> against the same [`PLAN-SKELETON.md`](PLAN-SKELETON.md); everything they publish is consumed here
> under the names the skeleton's `Interfaces:` blocks fix. Format and standard are
> [`../P5-extractors/PLAN.md`](../P5-extractors/PLAN.md) and
> [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md).

**Verified against the live substrate, 2026-08-22.** Every P1–P5 signature quoted below was read
with `inspect.signature` against the shipped packages, not from a PLAN. `pytest tests/ -q` collects
**1302 tests** and P1–P5 are green. The three facts that most change what is written here:

- `database_agent.files_table.set_sensitivity_state(conn, file_id, *, state: dict, author: str,
  component_version: str) -> None` **exists** (D2). P7 calls it; P7 takes no writer protocol.
- **Thirteen tables** carry a `BEFORE DELETE … RAISE(ABORT)` trigger — `events`, `evidence`,
  `text_units`, `extraction_runs`, `exclusion_verdicts` and P2's eight `bundle_*` tables — and
  `database_agent.db._deny_events_history_loss` is installed by `open_database` as a
  `set_authorizer` hook returning `SQLITE_DENY` for `SQLITE_DROP_TABLE events` and for
  `SQLITE_DROP_TRIGGER` on `events_no_update` / `events_no_delete` / `events_no_replace`. A
  `DELETE FROM events` raises `sqlite3.IntegrityError: events is append-only (R6, 8.2)`; a
  `DROP TRIGGER events_no_delete` raises `sqlite3.DatabaseError: not authorized`. Done-means 8 is
  provable against the substrate rather than against P7's restraint.
- `orchestrator.run_wave2(...)` passes **literal `None`** for `add_file_entry`'s `handling_class`
  (`src/orchestrator.py:402`), with a comment saying the honest value is `None` *"because the class
  is unknown, not because another column happened to be empty."* That is the Wave-2 caller's field,
  not P7's — see Task 22.

---

## Three rulings that bind this section, applied rather than restated

**D3 (ratified) changes WHY `delete_derived` raises.** The sentence is:

> `events` is append-only forever. Derived projections may be tombstoned; "derived" is a **literal
> enumerated table-and-column list** and `delete_derived` raises on anything outside it. **No
> tombstone column is built** until P13 drives it.

So Task 15 writes the enumeration down — that is the substance of the task — and `delete_derived`
raises on **both** sides of it: `ScopeNotDerived` outside the list, so an unenumerated table is a
red test rather than a silent miss, and `UnratifiedResolution` inside it, because nothing is built.
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
file, Task 18's `count = 0` summary, Task 20's fixture 2, and Task 22's path-one classification —
which the test writes itself, standing in for the detector and saying so in its docstring.

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
mirror_state(record)                              -> dict
```

`current_fact_id` is **added by this section** and Task 4 must publish it. P1's `mark_superseded`
keys on a `record_id` column (`src/database_agent/supersede.py`), so superseding a classification
needs the prior row's id, and `ClassificationRecord`'s eight SPEC §2 fields do not carry one.
Without it Task 16's `reclassify` cannot supersede, which is Done-means 2's user half. Reported.

---

## Tasks
### Task 15: Revocation, the retraction limit, and `delete_derived`'s refusal (I6/D3)

**Files:**
- Create: `src/privacy/revocation.py`
- Modify: `src/privacy/gate.py` (add `Gate.revoke` and `Gate.delete_derived`, delegating to this module — SPEC §8 publishes it on the facade, and **D13 kept CUT 4**, so the facade is certain rather than provisional)
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
   `authorship.CONSENT_REVOKED` and `database_agent.events.append_event` beside it — a list that is
   only coherent if the event append is `revoke`'s. Two appends would put one act in the log twice,
   and §8.4's `prior_releases` is read back out of that log.
2. **`AuditRecord.model` stores the `ModelTarget` as a mapping** with `locality`, `model_id` and
   `provider`. SPEC §8 requires `prior_releases[]` to carry *"model, provider, when, which
   excerpts"*; a bare model-name string leaves `PriorRelease.provider` unfillable, and §8.4's audit
   field is *"which model received the data"*, which a provider-less identifier does not answer for
   a hosted model.

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
enumerate the files a scope covers and must not guess; the caller supplies
`Callable[[str], Sequence[str]]` and P7 defines no area.

**`prior_releases` is every release in scope, not only those under the revoked policy version.**
§8.4's purpose is to tell the user what has already left the device. A list filtered to one policy
version answers a narrower question than the one the user is asking, and the audit log carries
`policy_version` on each record for a reader who wants the narrower one.

**What D3 makes this task write down.** The enumeration is the deliverable:

```text
DERIVED_PROJECTIONS
  evidence     raw_value, normalized_value, context_before, context_after
  text_units   text
```

Those five columns are where a scanned passport's OCR text actually lives — verified against the
live schema with `PRAGMA table_xinfo(evidence)` and `PRAGMA table_xinfo(text_units)`. `NOT_DERIVED`
names the four live tables outside it and why, so the refusal is legible:

```text
NOT_DERIVED
  events              append-only forever (R6, §8.2, D3). Three triggers and an authorizer hook.
  files               sensitivity_state is a classification projection (D2); reclassify, never delete.
  extraction_runs     the record THAT a run happened, not what it read (§2.4's empty-versus-absent).
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
import json
import sqlite3

import pytest

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import CONSENT_REVOKED, SUBSYSTEM
from privacy.policy import UNSET_POLICY_VERSION, Policy
from privacy.revocation import (
    DERIVED_PROJECTIONS, NOT_DERIVED, RELEASED, DeleteDerivedRefused, DerivedScope,
    MissingRetractionLimit, PriorRelease, ScopeNotDerived, UnratifiedResolution,
    delete_derived, revoke,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"

#: §8.4's obligation is the product's; the words are P13's. The test supplies them the
#: way P13 will, so nothing in `src/privacy/` has to hold a sentence.
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
    respelled without breaking it, while a field it DOES read disappearing fails here,
    loudly, at the seam that cares.
    """
    missing = [name for name in AUDIT_FIELDS if name not in _TYPED_DEFAULTS]
    assert not missing, (
        f"AUDIT_FIELDS names {missing} and this test has no value for them; SPEC §7 "
        "moved and Task 15 needs a value, not a default")
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
def released(p7_conn) -> int:
    """One prior release, in the log, under the policy about to be revoked."""
    return append_audit(p7_conn, an_audit_record(), author=SUBSYSTEM,
                        component_version=COMPONENT)


def go(conn, **over):
    base = dict(user_id="joseph", component_version=COMPONENT, observed_at=LATER,
                retraction_limit=RETRACTION_LIMIT,
                files_in_scope=lambda scope: ("file-1",))
    base.update(over)
    return revoke(conn, a_policy(), "Academics", **base)


# --- forward-only -----------------------------------------------------------

def test_effective_from_is_the_moment_of_revocation(p7_conn, released):
    # SPEC §8: "effective_from  future gate calls only."
    assert go(p7_conn).effective_from == LATER


def test_a_revocation_mints_a_new_policy_version(p7_conn, released):
    # The forward-only property is carried by a BINDING TERM, not by a flag. A release
    # minted under policy-1 still consumes against policy-1 (Task 12's ledger records
    # the version it was minted under), and a request made after this revocation is
    # decided against the new version, which is what makes Task 13's `policy_revoked`
    # reachable. Those two halves are asserted in Tasks 12 and 13 against signatures
    # this task cannot see; the seam that makes both true is asserted here.
    go(p7_conn)
    row = p7_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id DESC",
        (CONSENT_REVOKED,)).fetchone()
    payload = json.loads(row["explanation"])
    assert payload["revoked_policy_version"] == "policy-1"
    assert payload["policy_version"] != "policy-1"
    assert payload["effective_from"] == LATER


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
    # excerpts." The audit log is what makes the retraction limit specific rather than
    # a generic disclaimer.
    assert go(p7_conn).prior_releases == (
        PriorRelease(model="acme-large", provider="Acme", when=FIXED_CLOCK,
                     excerpts=(("obs-key-1", "0-19"),)),
    )


def test_a_denied_record_is_not_a_prior_release(p7_conn, released):
    append_audit(p7_conn, an_audit_record(outcome="denied", release_id=None),
                 author=SUBSYSTEM, component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


def test_prior_releases_come_from_the_audit_log_and_not_a_second_store(p7_conn):
    # Nothing else in P7 records what left the device, and §8.4 forbids a second copy
    # of the text: "excerpts_included stores (observation_key, span) pairs ... not a
    # second copy of the text."
    assert go(p7_conn).prior_releases == ()
    append_audit(p7_conn, an_audit_record(), author=SUBSYSTEM,
                 component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


def test_a_file_outside_the_scope_is_not_listed(p7_conn, released):
    # Open question 3 is held by the injection: P7 defines no corpus area, so a
    # resolver returning nothing produces an empty list rather than everything.
    assert go(p7_conn, files_in_scope=lambda scope: ()).prior_releases == ()


def test_prior_releases_are_ordered_oldest_first(p7_conn, released):
    append_audit(p7_conn, an_audit_record(release_id="release-2", observed_at=LATER),
                 author=SUBSYSTEM, component_version=COMPONENT)
    assert [r.when for r in go(p7_conn).prior_releases] == [FIXED_CLOCK, LATER]


# --- the retraction limit ---------------------------------------------------

def test_the_retraction_limit_is_always_present(p7_conn, released):
    assert go(p7_conn).retraction_limit == RETRACTION_LIMIT


def test_an_empty_retraction_limit_is_refused(p7_conn, released):
    # §8.4 is a `must`: the product "must communicate that distinction clearly".
    # Presence is enforced; wording is P13's (SPEC Deferred).
    for empty in ("", "   "):
        with pytest.raises(MissingRetractionLimit):
            go(p7_conn, retraction_limit=empty)


def test_the_wording_is_the_callers_and_not_the_modules():
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
        p7_conn.execute("DELETE FROM events WHERE event_id = ?", (released,))


def test_updating_an_audit_record_aborts(p7_conn, released):
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        p7_conn.execute("UPDATE events SET subsystem = 'P8' WHERE event_id = ?",
                        (released,))


def test_the_append_only_triggers_cannot_be_dropped(p7_conn):
    # `db._deny_events_history_loss`, installed by `open_database` as a
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
                           (released,)).fetchone()["c"] == 1


# --- D3: the enumeration, and delete_derived refusing on both sides ----------

def test_delete_derived_refuses_an_enumerated_scope_and_names_i6():
    # D3 ratified the DIRECTION and built nothing: "No tombstone column is built until
    # P13 drives it." The surface exists; the semantics do not.
    with pytest.raises(UnratifiedResolution) as caught:
        delete_derived(DerivedScope("text_units", "text"))
    assert "I6" in str(caught.value)
    assert "D3" in str(caught.value)


def test_delete_derived_refuses_an_unenumerated_scope_by_name():
    # The point of a LITERAL enumeration: a table nobody listed is a red test, not a
    # silent miss. `ScopeNotDerived` is a different failure from "not built yet" and
    # the two must not be readable as one.
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("extraction_runs", "completeness"))
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("evidence", "reliability"))


def test_both_refusals_share_one_base_so_delete_derived_never_succeeds():
    for scope in (DerivedScope("text_units", "text"),
                  DerivedScope("nowhere", "nothing")):
        with pytest.raises(DeleteDerivedRefused):
            delete_derived(scope)


def test_events_is_named_as_outside_the_enumeration():
    # D3's first clause. `events` is not merely absent from DERIVED_PROJECTIONS; the
    # reason is written down, because absence and oversight look identical.
    assert "events" not in DERIVED_PROJECTIONS
    assert "events" in NOT_DERIVED
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("events", "explanation"))


def test_sensitivity_state_is_reclassified_and_never_deleted():
    # D2: the column is a PROJECTION of P7's authoritative record. The supported user
    # act is Task 16's reclassification, which supersedes; deleting a projection would
    # leave the authoritative record and its mirror disagreeing.
    assert "files" not in DERIVED_PROJECTIONS
    assert "files" in NOT_DERIVED
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("files", "sensitivity_state"))


def test_the_enumeration_names_only_live_tables_and_live_columns(p7_conn):
    # An enumeration that drifts from the schema is worse than none: it would refuse a
    # real column and accept a name that no longer exists.
    for table, columns in DERIVED_PROJECTIONS.items():
        live = {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}
        assert live, table
        assert set(columns) <= live, (table, sorted(set(columns) - live))
    for table in NOT_DERIVED:
        assert {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}


def test_the_enumerated_columns_are_where_ocr_text_actually_lives():
    # I6's own worked case: "The product cannot ship unable to forget a scanned
    # passport's OCR text." That text is `text_units.text` and `evidence.raw_value`
    # with M5's two context fields; nothing else in the schema holds it.
    assert DERIVED_PROJECTIONS["text_units"] == ("text",)
    assert DERIVED_PROJECTIONS["evidence"] == (
        "raw_value", "normalized_value", "context_before", "context_after")


def test_no_tombstone_column_was_built(p7_conn):
    # D3's second clause, and the whole reason it is a clause:
    # `files.sensitivity_state` spent this project as a column nothing wrote and
    # produced a second wrong value one column away. A migration later is cheaper.
    for table in DERIVED_PROJECTIONS:
        columns = {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}
        for token in ("tombstone", "tombstoned", "deleted", "deleted_at",
                      "redacted_at", "forgotten"):
            assert token not in columns, (table, token)


def test_thirteen_tables_already_refuse_a_delete(p7_conn):
    # The substrate D3 lands on top of, counted rather than remembered: events,
    # evidence, text_units, extraction_runs, exclusion_verdicts and P2's eight
    # bundle_* tables. "Deletion later is always available; un-deletion never is" is a
    # posture the schema already holds.
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
        "SELECT name FROM sqlite_master WHERE type = 'trigger' "
        "AND tbl_name = 'events'")}
    assert names == {"events_no_update", "events_no_delete", "events_no_replace"}
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_revocation.py -v`
Expected: FAIL — `ImportError: cannot import name 'DERIVED_PROJECTIONS' from 'privacy.revocation'`
(the module does not exist, so collection fails on the first import).

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
  or deleting an event. D3 ratifies the direction -- events append-only forever,
  derived projections tombstonable, "derived" a literal enumeration -- and ratifies
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

    This is why the list is literal rather than a predicate: a table nobody enumerated
    produces a red test here instead of being quietly deleted from, or quietly skipped,
    depending on which way a clever rule happened to fall.
    """


class UnratifiedResolution(DeleteDerivedRefused):
    """The scope IS derived, and no tombstone column is built (D3, I6).

    The name is the one the plan skeleton published and it is kept so the contract does
    not move; what it now reports is *unbuilt*, not *unratified*. D3 settled the
    direction on 2026-08-21 and deliberately built nothing, because a writer-less column
    is the defect `files.sensitivity_state` demonstrated for the length of this project.
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


#: D3's literal enumerated table-and-column list. These five columns are where the text
#: extracted from a file's bytes actually lives -- checked against the live schema, not
#: against a PLAN. Anything else is `NOT_DERIVED` and refused by name.
DERIVED_PROJECTIONS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "evidence": ("raw_value", "normalized_value", "context_before", "context_after"),
    "text_units": ("text",),
})

#: The live tables outside the enumeration, each with the reason. Absence and oversight
#: are indistinguishable, so the reason is written down.
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
        "extraction result from an extractor that does not yet exist, and dropping the "
        "run row collapses the two."
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

    `files_in_scope` has no default. Open question 3 -- "What is a 'corpus area'? ...
    Consent grants cannot be scoped until this is named" -- is unanswered, so the
    resolver is the caller's and P7 defines no area.

    `retraction_limit` has no default either, and for the opposite reason: §8.4 makes
    the statement mandatory and the SPEC defers its wording, so presence is enforced
    here and the words come from P13.
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

    Not filtered to the revoked policy version. §8.4's purpose is to tell the user what
    has already been sent; a list narrowed to one version answers a different question,
    and each record carries `policy_version` for a reader who wants it.
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
        enumerated = {table: list(cols)
                      for table, cols in DERIVED_PROJECTIONS.items()}
        raise ScopeNotDerived(
            f"{scope.table}.{scope.column} is not in D3's enumerated derived list "
            f"{enumerated}" + (f"; {reason}" if reason else "")
        )
    raise UnratifiedResolution(
        f"{scope.table}.{scope.column} is derived (D3), and no tombstone column is "
        "built. D3, ratified 2026-08-21, settled the direction and deliberately built "
        "nothing until P13 drives it; I6 named the §8.4-versus-§8.2 conflict it "
        "resolves. Deletion later is always available; un-deletion never is."
    )
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_revocation.py -v`
Expected: PASS — 22 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–15 green, and 1302 P1–P5 tests still green (P7 modified no file belonging
to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/revocation.py tests/p7/test_p7_revocation.py
git commit -m "feat(P7): revocation, the retraction limit, and delete_derived refusing on both sides of D3's enumeration"
```

---
### Task 16: Reclassification, and §8.7's query-before-classify

**Files:**
- Create: `src/privacy/learning_seam.py`
- Modify: `src/privacy/gate.py` (add `Gate.reclassify`, delegating to this module — SPEC §8 publishes it on the facade, and **D13 kept CUT 4**, so the facade is certain rather than provisional)
- Test: `tests/p7/test_p7_learning_seam.py`

**Interfaces:**
- Consumes: `database_agent.learning.learning_records(conn, scope, subject_id) -> list[sqlite3.Row]`,
  `.SCOPES`, `.reset_preferences`, `database_agent.events.CORRECTION_FIELDS`, `.CORRECTION_SCOPES`,
  `.append_event`, `database_agent.files_table.set_sensitivity_state`,
  `evidence_shape.canonical.canonical_json`, `privacy.classification.ClassificationRecord`,
  `privacy.classification_store.ClassificationStore`, `.mirror_state` (the skeleton's
  `facts_seam.SensitivityFacts` — see the rename note above), `privacy.authorship.SUBSYSTEM`,
  `.CLASSIFICATION_ASSIGNED`, `.CLASSIFICATION_SUPERSEDED`, `.event_defaults`,
  `privacy.vocabulary.check_handling_class`.
- Produces (`learning_seam.py`):
  - `PROPOSAL_CLASS: str = "privacy"`, `FILE_SCOPE: str = "file"`, `ACCEPT: str`, `REJECT: str`.
  - `RECORDED_ACTIONS: tuple[str, ...]` (SPEC *Correction learning*'s six),
    `RECORDED_ACTION_SOURCES: Mapping[str, str]` (each identifier → the SPEC's own phrase),
    `check_recorded_action(value) -> str`, `UnknownRecordedAction`.
  - `basis_key_for(file_id, handling_class) -> str`.
  - `suppressed(conn, file_id, handling_class) -> bool`.
  - `assign(conn, record, *, store, component_version) -> ClassificationRecord | None`.
  - `reclassify(conn, file_id, handling_class, reason, *, store, content_hash, protected,
    evidence_refs, user_id, component_version, observed_at, correction_scope=FILE_SCOPE)
    -> ClassificationRecord`.

**Done-means:** part of 2 (the user-revision half), and the §8.7 obligation.

**`assign` is added by this task and it is what makes the Done-means falsifiable.** The skeleton's
`Produces` block lists `suppressed` and stops, and 10-i4's Done-means is *"a fixture with one
unresected reject at the stated `basis_key` produces **zero re-emissions** of that proposal."* A
predicate returning `True` is not zero re-emissions; something has to be the emission that does not
happen. `assign` is the system-side write — the one a detector would call — and it returns `None`
when suppressed. Reported as an addition.

**Suppression guards `assign` and never `reclassify`.** 10-i4's table: *"**P7** | Before assigning a
handling class the user has already set or rejected at this scope | Do not re-prompt the same
classification."* What is suppressed is the product re-proposing, not the user acting. A
`reclassify` that consulted the suppression store would refuse the user's own correction on the
grounds that they had already made it.

**`assign` appends no correction field, so it can never be its own suppressor.** P1's
`learning_records` filters `user_id IS NOT NULL`, which makes a system assignment structurally
incapable of becoming a learning record. Only `reclassify`, which carries a `user_id`, writes one.

**One event per act, and the event is the rejection.** A reclassification over an existing
classification appends exactly one `classification_superseded` with `polarity = "reject"` at
`basis_key_for(file_id, prior_class)` — §8.7's negative example, *"stored with the evidence that
produced them"* — and supersedes through P1's three columns. A reclassification where nothing was
classified appends one `classification_assigned` with `polarity = "accept"` at the new class. There
is no accept-and-reject pair: 10-i4 rule 4 says *"A `polarity = accept` record at the same
`basis_key` is not a suppression and must not be read as one"*, so the second event would be a row
that changes nothing plus a second place for the two to disagree.

**The keys, not the ids (M14).** *"a per-row `observation_id` dies when the extractor is upgraded,
so a negative example recorded today would silently stop resolving and the same false protection
would return."* `evidence_refs` is a required keyword carrying P4 `observation_key` values; it lands
on the new record and is echoed into the superseding event's explanation as
`rejected_evidence_refs`.

**`correction_scope` defaults to `file`, and that default is the design's own.** §8.7's worked
warning: one transcript belonging in one packet *"should not teach the engine that all transcripts
belong there."* A broader scope is accepted when the caller passes one and is never inferred. Open
question 7 — *"Does repeated reclassification generalize?"* — stays open; nothing here counts
repetitions, and Task 21 asserts it.

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
    # SPEC §2, and Open question 1. A caller may mark a `public_low` file protected and
    # this module does not argue.
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


def test_open_question_7_is_not_answered_here(p7_conn, file_id, content_hash, store):
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
Expected: FAIL — `ImportError: cannot import name 'ACCEPT' from 'privacy.learning_seam'`

- [ ] **Step 3: Write `src/privacy/learning_seam.py`**

```python
# src/privacy/learning_seam.py
"""§8.7's query-before-classify, and reclassification as supersession.

Two directions across one seam. Reading: before the product assigns a handling class it
asks P1 whether the user has already rejected that class for that file, because
10-i4-learning-ops.md puts P7 in the query-before-propose table -- "Before assigning a
handling class the user has already set or rejected at this scope | Do not re-prompt the
same classification". Writing: a user reclassification is a new `user_confirmed` fact
that supersedes the prior one and leaves a negative example behind, because §8.7
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

#: SPEC *Correction learning*, "Recorded actions". The identifiers are P7's; the phrases
#: are the SPEC's, held beside them so a later paraphrase is a failing test.
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
            f"{value!r} is not one of SPEC Correction learning's six recorded actions "
            f"{RECORDED_ACTIONS}")
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

    `protected` is a parameter and is never derived from `handling_class`. Open question
    1 -- "Is `protected` exactly the top two handling classes?" -- is unsettled, and
    SPEC §2 says outright: "Neighbouring parts should consume the `protected` flag, not
    infer it from the class."

    `evidence_refs` carries P4 `observation_key` values (M14) -- the keys the detector
    fired on. They land on the new record and are echoed into the superseding event so
    §8.7's "stored with the evidence that produced them" has somewhere to be true.
    """
    check_handling_class(handling_class)
    if not reason or not reason.strip():
        raise ValueError(
            "§8.2 retains 'the old observation and the reason it was superseded'; a "
            "revision without a reason cannot satisfy it")
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
            "superseded_handling_class":
                None if prior is None else prior.handling_class,
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
git commit -m "feat(P7): reclassification as supersession, and 8.7's query-before-classify"
```

---

### Task 17: `may_move_automatically`

**Files:**
- Create: `src/privacy/moves.py`
- Test: `tests/p7/test_p7_moves.py`

**Interfaces:**
- Consumes: `privacy.classification_store.ClassificationStore` (the skeleton's
  `facts_seam.SensitivityFacts` — see the rename note), `privacy.policy.current_policy(conn, *,
  plan_version) -> Policy`, `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row`.
- Produces (`moves.py`):
  - `MoveVerdict` — frozen: `allowed: bool`, `reason: str`, `permitting_policy: str | None`.
  - `REASON_NOT_PROTECTED`, `REASON_UNCLASSIFIED`, `REASON_NO_PERMITTING_POLICY`,
    `REASON_POLICY_PERMITS` — the four verdict reasons, each carrying §8.4's own words.
  - `may_move_automatically(conn, file_id, plan_version, *, store, scope_for) -> MoveVerdict`.

**Done-means:** 9 (first clause; the second is P11's and P12's — see the skeleton's coverage table).

**`get_file` is added to the `Consumes` block.** The classification is keyed `(file_id,
content_hash)` (D2) and the published signature takes a `file_id` only, so the current version's
hash has to come from somewhere. P1's `get_file` is that somewhere, and using it is what makes the
verdict mean *"may this file, as it stands now, be moved"* — new bytes at a path are a new file
version and inherit no classification. Reported.

**`scope_for` is a required keyword with no default, and it is Open question 3 again.**
`Policy.automatic_move_permissions` is keyed by an opaque scope string because *"What is a 'corpus
area'?"* is unanswered. The caller maps a `file_id` to its scope; P7 defines no area and Task 21
asserts the parameter has no default.

**The verdict is keyed on the `protected` flag and never on the handling class.** SPEC §2:
*"Neighbouring parts should consume the `protected` flag, not infer it from the class"*, and Open
question 1 — whether `protected` is exactly the top two classes — is unsettled. A test constructs
the case that separates them: a `public_low` record with `protected = True`, which must be refused,
and a `highly_sensitive_credential_bearing` record with `protected = False`, which must not be.

**An unclassified file is refused, and today that is every file.** §8.4 makes classification a
precondition — *"classify data into handling classes before LLM escalation"* — and §8.6 forbids the
escape hatch: *"Cost exhaustion must never turn into lower-quality automatic classification."*
A file nothing has looked at has not met the precondition, so it is not automatically movable. D2
leaves the detector unwritten, so on a real corpus this is the ordinary verdict, and a named test
says so rather than leaving a reader to discover it.

**A later plan version never reaches back.** §8.8: *"A new plan should never silently reclassify or
move old files."* `current_policy(conn, plan_version=...)` is plan-scoped, so a permission adopted
at `plan-2` is invisible to a question asked at `plan-1`. §7.11 supplies the other half of the same
rule: the system must not *"move them out of a protected area without explicit user action."*

**The permitting policy is named in the verdict so P11 and P12 do not re-derive it.** §6.11's
*"required review policy"* and §8.3's *"Sensitivity and consent state"* both want to record which
policy allowed a move. A verdict that only said `True` would make each of them ask again, and two
answers to one question is the defect this project has paid for most.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_moves.py
"""Done-means 9's first clause: false for protected material absent an explicitly
permitting policy, and the permitting policy named when there is one."""
import json

import pytest

from database_agent.files_table import get_file, record_file

from privacy.authorship import SUBSYSTEM
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.moves import (
    REASON_NOT_PROTECTED, REASON_NO_PERMITTING_POLICY, REASON_POLICY_PERMITS,
    REASON_UNCLASSIFIED, MoveVerdict, may_move_automatically,
)
from privacy.policy import Policy, set_policy

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
ACADEMICS = "Academics"

SCOPE_FOR = lambda file_id: ACADEMICS


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "tax-statement-2025.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


def classify(p7_conn, store, file_id, *, handling_class, protected):
    store.write(ClassificationRecord(
        file_id=file_id, content_hash=get_file(p7_conn, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=FIXED_CLOCK))


def install(conn, *, plan_version="plan-1", permissions=None) -> str:
    """Returns the minted policy_version. The test never asserts its spelling: SPEC
    §6 says the gate owns the policy and the caller echoes it."""
    policy = Policy(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
                    consent_grants=(),
                    redaction_settings={"names": "redacted", "previews": "redacted",
                                        "thumbnails": "redacted",
                                        "ocr_text": "redacted",
                                        "location_data": "redacted"},
                    automatic_move_permissions=dict(permissions or {}),
                    plan_version=plan_version, set_at=FIXED_CLOCK)
    return set_policy(conn, policy, component_version=COMPONENT,
                      user_id="joseph",
                      reason="the fixture's starting policy")


def ask(conn, file_id, store, plan_version="plan-1"):
    return may_move_automatically(conn, file_id, plan_version, store=store,
                                  scope_for=SCOPE_FOR)


# --- the three verdicts -----------------------------------------------------

def test_protected_with_no_permitting_policy_is_refused(p7_conn, file_id, store):
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it."
    install(p7_conn)
    classify(p7_conn, store, file_id,
             handling_class="highly_sensitive_credential_bearing", protected=True)
    verdict = ask(p7_conn, file_id, store)
    assert verdict == MoveVerdict(allowed=False,
                                  reason=REASON_NO_PERMITTING_POLICY,
                                  permitting_policy=None)


def test_protected_under_an_explicitly_permitting_policy_is_allowed_and_names_it(
        p7_conn, file_id, store):
    # §6.11's "required review policy" and §8.3's "Sensitivity and consent state"
    # both record which policy allowed the move. The verdict names it so neither
    # P11 nor P12 asks the question a second time.
    version = install(p7_conn, permissions={ACADEMICS: True})
    classify(p7_conn, store, file_id, handling_class="sensitive_personal",
             protected=True)
    verdict = ask(p7_conn, file_id, store)
    assert verdict.allowed is True
    assert verdict.reason == REASON_POLICY_PERMITS
    assert verdict.permitting_policy == version


def test_an_unprotected_file_is_allowed(p7_conn, file_id, store):
    install(p7_conn)
    classify(p7_conn, store, file_id, handling_class="public_low", protected=False)
    verdict = ask(p7_conn, file_id, store)
    assert verdict == MoveVerdict(allowed=True, reason=REASON_NOT_PROTECTED,
                                  permitting_policy=None)


def test_a_permission_for_another_scope_does_not_permit_this_one(
        p7_conn, file_id, store):
    install(p7_conn, permissions={"Finance": True})
    classify(p7_conn, store, file_id, handling_class="sensitive_personal",
             protected=True)
    assert ask(p7_conn, file_id, store).allowed is False


def test_a_permission_set_to_false_is_not_a_permission(p7_conn, file_id, store):
    # "explicitly permits" is one value, not the absence of a denial.
    install(p7_conn, permissions={ACADEMICS: False})
    classify(p7_conn, store, file_id, handling_class="sensitive_personal",
             protected=True)
    assert ask(p7_conn, file_id, store).reason == REASON_NO_PERMITTING_POLICY


# --- the flag, not the class ------------------------------------------------

def test_a_public_low_file_marked_protected_is_still_refused(
        p7_conn, file_id, store):
    # SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    # from the class." Open question 1 -- whether `protected` is exactly the top two
    # classes -- is not settled, so this pair is the case that separates them.
    install(p7_conn)
    classify(p7_conn, store, file_id, handling_class="public_low", protected=True)
    assert ask(p7_conn, file_id, store).allowed is False


def test_a_top_class_file_not_marked_protected_is_allowed(p7_conn, file_id, store):
    install(p7_conn)
    classify(p7_conn, store, file_id,
             handling_class="highly_sensitive_credential_bearing", protected=False)
    assert ask(p7_conn, file_id, store) == MoveVerdict(
        allowed=True, reason=REASON_NOT_PROTECTED, permitting_policy=None)


def test_the_module_never_reads_the_handling_class_to_decide(p7_conn):
    # The proof that the pair above is structural and not coincidental: the decision
    # reads `.protected` and nothing else off the record. Asserted by AST over the
    # module's code, docstrings excluded -- a substring scan matches the sentence in
    # the docstring that explains the rule.
    import ast
    from pathlib import Path

    import privacy.moves as module

    tree = ast.parse(Path(module.__file__).read_text())
    docstrings = {id(node.body[0].value) for node in ast.walk(tree)
                  if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef))
                  and node.body and isinstance(node.body[0], ast.Expr)
                  and isinstance(node.body[0].value, ast.Constant)
                  and isinstance(node.body[0].value.value, str)}
    attributes = {node.attr for node in ast.walk(tree)
                  if isinstance(node, ast.Attribute)}
    literals = {node.value for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and id(node) not in docstrings
                and isinstance(node.value, str)}
    assert "protected" in attributes
    assert "handling_class" not in attributes
    assert not {"public_low", "personal_non_sensitive", "sensitive_personal",
                "highly_sensitive_credential_bearing"} & literals


# --- unclassified, which is today's ordinary case ---------------------------

def test_an_unclassified_file_is_refused(p7_conn, file_id, store):
    # §8.4 makes classification a precondition; §8.6 forbids the escape hatch:
    # "Cost exhaustion must never turn into lower-quality automatic classification."
    install(p7_conn)
    verdict = ask(p7_conn, file_id, store)
    assert verdict == MoveVerdict(allowed=False, reason=REASON_UNCLASSIFIED,
                                  permitting_policy=None)


def test_no_permitting_policy_can_move_an_unclassified_file(p7_conn, file_id, store):
    # The permission answers "may protected material move"; it does not answer
    # "has anything looked at this file". D2 leaves the detector unwritten, so this
    # is the verdict every file on a real corpus gets today.
    install(p7_conn, permissions={ACADEMICS: True})
    assert ask(p7_conn, file_id, store).reason == REASON_UNCLASSIFIED


def test_new_bytes_at_the_same_path_inherit_no_classification(
        p7_conn, file_id, store, tmp_path):
    # D2: "Keyed on the hash because a classification is about BYTES; new bytes at a
    # path are a new file version and inherit nothing."
    install(p7_conn, permissions={ACADEMICS: True})
    classify(p7_conn, store, file_id, handling_class="public_low", protected=False)
    assert ask(p7_conn, file_id, store).allowed is True
    p7_conn.execute("UPDATE files SET content_hash = ? WHERE file_id = ?",
                    ("sha256:different-bytes", file_id))
    assert ask(p7_conn, file_id, store).reason == REASON_UNCLASSIFIED


# --- plan versioning --------------------------------------------------------

def test_a_later_plan_version_does_not_retroactively_permit_a_move(
        p7_conn, file_id, store):
    # §8.8: "A new plan should never silently reclassify or move old files."
    install(p7_conn, plan_version="plan-1")
    install(p7_conn, plan_version="plan-2", permissions={ACADEMICS: True})
    classify(p7_conn, store, file_id, handling_class="sensitive_personal",
             protected=True)
    assert ask(p7_conn, file_id, store, plan_version="plan-1").allowed is False
    assert ask(p7_conn, file_id, store, plan_version="plan-2").allowed is True


def test_the_classification_is_shared_across_plan_versions(
        p7_conn, file_id, store):
    # §8.8: "The evidence database remains shared across plan versions." Policy is
    # plan-scoped; the classification is not.
    install(p7_conn, plan_version="plan-1", permissions={ACADEMICS: True})
    install(p7_conn, plan_version="plan-2", permissions={ACADEMICS: True})
    classify(p7_conn, store, file_id, handling_class="sensitive_personal",
             protected=True)
    for plan in ("plan-1", "plan-2"):
        assert ask(p7_conn, file_id, store, plan_version=plan).reason == (
            REASON_POLICY_PERMITS)


# --- what the reasons say ---------------------------------------------------

def test_every_reason_carries_the_designs_own_words():
    # A verdict a user is shown has to say why in the product's own terms, and §8.4
    # and §7.11 already supply them. Nothing here is UX copy P7 invented.
    assert "explicitly permits" in REASON_NO_PERMITTING_POLICY
    assert "explicitly permits" in REASON_POLICY_PERMITS
    assert "protected" in REASON_NOT_PROTECTED
    assert "unclassified" in REASON_UNCLASSIFIED


def test_scope_for_has_no_default(p7_conn):
    # Open question 3: "Consent grants cannot be scoped until this is named."
    import inspect
    parameter = inspect.signature(may_move_automatically).parameters["scope_for"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_moves.py -v`
Expected: FAIL — `ImportError: cannot import name 'REASON_NOT_PROTECTED' from 'privacy.moves'`

- [ ] **Step 3: Write `src/privacy/moves.py`**

```python
# src/privacy/moves.py
"""§8.4's automatic-move predicate, and nothing else.

One sentence is the whole specification: protected material "should not be moved
automatically without a user policy that explicitly permits it". §7.11 adds the
symmetric prohibition -- the system must not "move them out of a protected area
without explicit user action" -- and §8.8 adds the time rule: "A new plan should never
silently reclassify or move old files."

P11 (§6.10, §6.11) and P12 (§8.3) CONSUME this verdict. They do not re-derive it,
which is why `permitting_policy` is on the verdict: a bare `True` would make each of
them ask the question again, and two answers to one question is this project's most
expensive defect class.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from database_agent.files_table import get_file

from privacy.classification_store import ClassificationStore
from privacy.policy import current_policy

#: The four reasons, in the design's own words. Not a closed vocabulary P7 invented:
#: §8.4 supplies "explicitly permits", §8.4 and §8.6 supply "unclassified".
REASON_NOT_PROTECTED: str = "not protected"
REASON_UNCLASSIFIED: str = (
    "unreadable or unclassified; classification is a precondition (§8.4) and cost "
    "exhaustion must never turn into lower-quality automatic classification (§8.6)"
)
REASON_NO_PERMITTING_POLICY: str = (
    "protected, and no user policy explicitly permits an automatic move (§8.4)"
)
REASON_POLICY_PERMITS: str = (
    "protected, and a user policy explicitly permits an automatic move (§8.4)"
)


@dataclass(frozen=True)
class MoveVerdict:
    """SPEC §9's `{ allowed, reason, permitting_policy? }`."""

    allowed: bool
    reason: str
    permitting_policy: str | None


def may_move_automatically(conn: sqlite3.Connection, file_id: str, plan_version: str,
                           *, store: ClassificationStore,
                           scope_for: Callable[[str], str]) -> MoveVerdict:
    """False for protected material absent an explicitly permitting policy.

    `scope_for` has no default. `Policy.automatic_move_permissions` is keyed by an
    opaque scope string because Open question 3 -- "What is a 'corpus area'?" -- is
    unanswered; the caller maps a file to its area and P7 defines none.

    The decision reads `record.protected` and never `record.handling_class`. SPEC §2:
    "Neighbouring parts should consume the `protected` flag, not infer it from the
    class", and Open question 1 leaves the relation between them unsettled.
    """
    file_row = get_file(conn, file_id)
    record = store.current(file_id, file_row["content_hash"])
    if record is None:
        return MoveVerdict(allowed=False, reason=REASON_UNCLASSIFIED,
                           permitting_policy=None)
    if not record.protected:
        return MoveVerdict(allowed=True, reason=REASON_NOT_PROTECTED,
                           permitting_policy=None)
    policy = current_policy(conn, plan_version=plan_version)
    if policy.automatic_move_permissions.get(scope_for(file_id)) is True:
        return MoveVerdict(allowed=True, reason=REASON_POLICY_PERMITS,
                           permitting_policy=policy.policy_version)
    return MoveVerdict(allowed=False, reason=REASON_NO_PERMITTING_POLICY,
                       permitting_policy=None)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_moves.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/privacy/moves.py tests/p7/test_p7_moves.py
git commit -m "feat(P7): may_move_automatically, keyed on the protected flag and naming the permitting policy"
```

---
### Task 18: `display_policy` and `summarize_protected`

**Files:**
- Create: `src/privacy/display.py`
- Modify: `src/privacy/gate.py` (add `Gate.display_policy` and `Gate.summarize_protected`, delegating to this module — SPEC §10 publishes it on the facade, and **D13 kept CUT 4**, so the facade is certain rather than provisional)
- Test: `tests/p7/test_p7_display.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.DISPLAY_FACETS`, `.HANDLING_CLASSES`,
  `privacy.defaults.MORE_REDACTING`, `privacy.policy.current_policy(conn, *, plan_version) -> Policy`,
  `privacy.classification.resolve_class(record) -> str`,
  `privacy.classification_store.ClassificationStore` (the skeleton's `facts_seam.SensitivityFacts` —
  see the rename note), `database_agent.files_table.get_file`.
- Produces (`display.py`):
  - `SHOWN: str = "shown"`, `REDACTED: str = "redacted"`, `SETTING_VALUES: tuple[str, str]`.
  - `RedactionSettings` — frozen, five fields, one per §8.4 facet, in §8.4's order;
    `facet(name) -> str`.
  - `ProtectedSummary` — frozen: `count: int`, `class_breakdown: Mapping[str, int]`. Two fields,
    and deliberately no third.
  - `UnknownDisplaySetting`.
  - `display_policy(conn, *, plan_version) -> RedactionSettings`.
  - `summarize_protected(conn, scope, *, store, files_in_scope) -> ProtectedSummary`.

**Done-means:** 10, and the display half of 12.

**Two signature widenings, both reported.** The skeleton publishes `display_policy(conn)` and
`summarize_protected(conn, scope)`. `current_policy(conn, *, plan_version)` is plan-scoped — §8.8
lists *"Privacy and model-consent policies"* inside the plan version — so `display_policy` needs the
plan version and takes it as a keyword. `summarize_protected` needs the classification store and a
scope resolver for the same Open-question-3 reason `revoke` does. SPEC §10's published surface is
`Gate.display_policy()` and `Gate.summarize_protected(scope)`, and the facade holds both values, so
the SPEC's shape is unchanged where a caller sees it.

**`shown | redacted` is SPEC §10's own text**, not a vocabulary this task invented:
`names | previews | thumbnails | ocr_text | location_data     each shown | redacted`. Task 2 owns
`DISPLAY_FACETS`; the two values live here because no earlier task's `Produces` block claims them.

**The default is the more redacting value, per facet, and that is Task 6's rule applied.** §8.4's
`must` — *"The default posture must therefore be local-first and data-minimizing"* — with §8.4's own
worked example settling the direction: *"A summary such as '11 protected identity records' may be
safe to show, while a visible list of passport filenames on a shared screen may not be."* The
aggregate is the default and the expansion is the user's act. A facet absent from the stored policy
resolves through `defaults.MORE_REDACTING`, never to `shown`.

**`ProtectedSummary` cannot return a filename, and the proof is at the type level.** Done-means 10:
*"returns counts and class breakdown and cannot return filenames or content."* Asserted over
`dataclasses.fields(ProtectedSummary)` — a runtime filter is something a future caller can route
around, and a string scan matches the docstring that explains the rule. §5.2 applies the same rule
to the canvas: a Finance or Identity proposal *"may be visible as a protected area, but the product
should avoid showing sensitive filenames"*, and §7.5's residual screen already uses the form —
*"11 protected personal records."*

**`count` counts protected files; `class_breakdown` counts every file in scope by its resolved
class.** Both are needed and they answer different questions. `count` is §8.4's aggregate. The
breakdown includes `unreadable_unclassified`, which is what makes today's honest state visible: with
no detector (D2) every file resolves there, so a real corpus yields `count = 0` — and *"0 protected
records"* means *nothing has looked*, not *nothing is protected*. That is exactly why D2 keeps
`unreadable_unclassified` off `files.sensitivity_state` and on the gate outcome, and a named test
records it here rather than leaving a reader to find it.

**P13's open question is recorded against this signature and not resolved.** §8.4: *"Protected
branches should have configurable redaction in the canvas and review screens"* — which reads
per-branch — while `display_policy()` takes no branch. Quoted in a named test, unresolved.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_display.py
"""Done-means 10, and the display half of Done-means 12.

§8.4's UI paragraph, entire: "Privacy also applies to the user interface. A summary
such as '11 protected identity records' may be safe to show, while a visible list of
passport filenames on a shared screen may not be. Protected branches should have
configurable redaction in the canvas and review screens. The user can choose whether
names, previews, thumbnails, OCR text, or location data are shown."
"""
import dataclasses
import json

import pytest

from database_agent.files_table import get_file, record_file

from privacy.authorship import SUBSYSTEM
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.display import (
    REDACTED, SETTING_VALUES, SHOWN, ProtectedSummary, RedactionSettings,
    UnknownDisplaySetting, display_policy, summarize_protected,
)
from privacy.policy import Policy, set_policy
from privacy.vocabulary import DISPLAY_FACETS, HANDLING_CLASSES

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
IDENTITY = "Identity"

ALL_SHOWN = {facet: SHOWN for facet in DISPLAY_FACETS}


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


@pytest.fixture()
def corpus(p7_conn, tmp_path):
    """Eleven passport scans and two ordinary files, so §8.4's own example number is
    the number the summary produces."""
    root = tmp_path / "corpus"
    root.mkdir()
    file_ids = []
    for index in range(11):
        document = root / f"passport-scan-{index}.pdf"
        document.write_bytes(f"%PDF-1.4 passport {index}".encode())
        file_ids.append(_record(p7_conn, root, document))
    for name in ("syllabus.pdf", "notes.md"):
        document = root / name
        document.write_bytes(f"plain {name}".encode())
        file_ids.append(_record(p7_conn, root, document))
    return file_ids


def _record(conn, root, document):
    return record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=document.suffix,
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(root), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


def classify(conn, store, file_id, *, handling_class, protected):
    store.write(ClassificationRecord(
        file_id=file_id, content_hash=get_file(conn, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=FIXED_CLOCK))


def install(conn, *, plan_version="plan-1", redaction_settings=None) -> str:
    policy = Policy(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
                    consent_grants=(),
                    redaction_settings=dict(redaction_settings or {}),
                    automatic_move_permissions={}, plan_version=plan_version,
                    set_at=FIXED_CLOCK)
    return set_policy(conn, policy, component_version=COMPONENT,
                      user_id="joseph",
                      reason="the fixture's starting policy")


def summarize(conn, store, file_ids):
    return summarize_protected(conn, IDENTITY, store=store,
                               files_in_scope=lambda scope: tuple(file_ids))


# --- the five facets --------------------------------------------------------

def test_the_five_facets_are_8_4s_own_list_in_8_4s_order():
    # "whether names, previews, thumbnails, OCR text, or location data are shown."
    assert [field.name for field in dataclasses.fields(RedactionSettings)] == [
        "names", "previews", "thumbnails", "ocr_text", "location_data"]
    assert tuple(DISPLAY_FACETS) == tuple(
        field.name for field in dataclasses.fields(RedactionSettings))


def test_there_is_no_sixth_facet():
    assert len(dataclasses.fields(RedactionSettings)) == 5


def test_each_facet_takes_one_of_two_values(p7_conn):
    # SPEC §10: "each shown | redacted".
    assert SETTING_VALUES == (SHOWN, REDACTED) == ("shown", "redacted")
    install(p7_conn, redaction_settings=ALL_SHOWN)
    settings = display_policy(p7_conn, plan_version="plan-1")
    for facet in DISPLAY_FACETS:
        assert settings.facet(facet) in SETTING_VALUES


def test_a_third_value_is_a_load_error(p7_conn):
    # "A value outside this set is a load error, not a fallback" (SPEC §1's rule,
    # applied to the setting values §10 states).
    install(p7_conn, redaction_settings={**ALL_SHOWN, "names": "blurred"})
    with pytest.raises(UnknownDisplaySetting):
        display_policy(p7_conn, plan_version="plan-1")


def test_an_unknown_facet_is_a_load_error(p7_conn):
    install(p7_conn, redaction_settings={**ALL_SHOWN, "audio": REDACTED})
    with pytest.raises(UnknownDisplaySetting):
        display_policy(p7_conn, plan_version="plan-1")


# --- the default is the more redacting one ----------------------------------

def test_an_empty_policy_resolves_every_facet_to_its_more_redacting_value(p7_conn):
    # Done-means 12's display half: "every redaction setting the design leaves
    # configurable resolves to its more redacting value".
    install(p7_conn)
    settings = display_policy(p7_conn, plan_version="plan-1")
    for facet in DISPLAY_FACETS:
        assert settings.facet(facet) == MORE_REDACTING[facet] == REDACTED


def test_a_partial_policy_fills_the_missing_facets_from_the_more_redacting_rule(
        p7_conn):
    install(p7_conn, redaction_settings={"names": SHOWN})
    settings = display_policy(p7_conn, plan_version="plan-1")
    assert settings.names == SHOWN
    for facet in ("previews", "thumbnails", "ocr_text", "location_data"):
        assert settings.facet(facet) == REDACTED


def test_the_user_can_still_choose_shown(p7_conn):
    # §8.4: "The user can choose whether names, previews, thumbnails, OCR text, or
    # location data are shown." The floor is on the DEFAULT, never on the choice.
    install(p7_conn, redaction_settings=ALL_SHOWN)
    settings = display_policy(p7_conn, plan_version="plan-1")
    assert all(settings.facet(facet) == SHOWN for facet in DISPLAY_FACETS)


def test_settings_are_plan_scoped(p7_conn):
    # §8.8 lists "Privacy and model-consent policies" inside the plan version.
    install(p7_conn, plan_version="plan-1")
    install(p7_conn, plan_version="plan-2", redaction_settings=ALL_SHOWN)
    assert display_policy(p7_conn, plan_version="plan-1").names == REDACTED
    assert display_policy(p7_conn, plan_version="plan-2").names == SHOWN


# --- the aggregate-safe summary ---------------------------------------------

def test_protected_summary_has_two_fields_and_deliberately_no_third():
    # Done-means 10: "cannot return filenames or content". Proven at the TYPE level --
    # a runtime filter is something a future caller can route around, and a string
    # scan matches the docstring that explains the rule.
    names = [field.name for field in dataclasses.fields(ProtectedSummary)]
    assert names == ["count", "class_breakdown"]
    for forbidden in ("filename", "filenames", "path", "paths", "examples",
                      "members", "file_ids", "raw_value", "text", "preview",
                      "thumbnail"):
        assert forbidden not in names


def test_eleven_protected_identity_records(p7_conn, store, corpus):
    # §8.4's own example, as the acceptance criterion: "A summary such as '11
    # protected identity records' may be safe to show."
    for file_id in corpus[:11]:
        classify(p7_conn, store, file_id,
                 handling_class="highly_sensitive_credential_bearing",
                 protected=True)
    for file_id in corpus[11:]:
        classify(p7_conn, store, file_id, handling_class="public_low",
                 protected=False)
    summary = summarize(p7_conn, store, corpus)
    assert summary.count == 11
    assert summary.class_breakdown["highly_sensitive_credential_bearing"] == 11
    assert summary.class_breakdown["public_low"] == 2


def test_the_breakdown_covers_every_handling_class_zero_filled(
        p7_conn, store, corpus):
    for file_id in corpus:
        classify(p7_conn, store, file_id, handling_class="public_low",
                 protected=False)
    summary = summarize(p7_conn, store, corpus)
    assert set(summary.class_breakdown) == set(HANDLING_CLASSES)
    assert summary.class_breakdown["sensitive_personal"] == 0


def test_the_count_follows_the_flag_and_not_the_class(p7_conn, store, corpus):
    # SPEC §2, and Open question 1 again: a `public_low` file the user marked
    # protected is counted, and a top-class file that is not marked is not.
    classify(p7_conn, store, corpus[0], handling_class="public_low", protected=True)
    classify(p7_conn, store, corpus[1],
             handling_class="highly_sensitive_credential_bearing", protected=False)
    summary = summarize(p7_conn, store, corpus[:2])
    assert summary.count == 1
    assert summary.class_breakdown["public_low"] == 1
    assert summary.class_breakdown["highly_sensitive_credential_bearing"] == 1


def test_a_file_outside_the_scope_is_not_counted(p7_conn, store, corpus):
    classify(p7_conn, store, corpus[0],
             handling_class="highly_sensitive_credential_bearing", protected=True)
    assert summarize(p7_conn, store, ()).count == 0
    assert summarize(p7_conn, store, corpus[:1]).count == 1


def test_with_no_detector_the_summary_reads_zero_and_the_breakdown_says_why(
        p7_conn, store, corpus):
    # D2 leaves the detector unwritten, so this is the summary a real corpus produces
    # today. "0 protected records" means NOTHING HAS LOOKED, not "nothing is
    # protected" -- which is precisely why D2 keeps `unreadable_unclassified` off
    # `files.sensitivity_state` and on the gate outcome instead.
    summary = summarize(p7_conn, store, corpus)
    assert summary.count == 0
    assert summary.class_breakdown["unreadable_unclassified"] == len(corpus)
    assert sum(summary.class_breakdown.values()) == len(corpus)


def test_the_breakdown_is_not_mutable_by_a_caller(p7_conn, store, corpus):
    summary = summarize(p7_conn, store, corpus)
    with pytest.raises(TypeError):
        summary.class_breakdown["public_low"] = 99


# --- what is not resolved here ----------------------------------------------

def test_p13s_per_branch_question_is_recorded_and_not_answered(p7_conn):
    # §8.4: "Protected branches should have configurable redaction in the canvas and
    # review screens" -- which reads per-branch -- while SPEC §10 publishes
    # `Gate.display_policy()` with no branch. Recorded against the signature so the
    # reviewer sees where the gap is, and not resolved by this plan.
    import inspect
    parameters = set(inspect.signature(display_policy).parameters)
    assert parameters == {"conn", "plan_version"}
    assert "branch" not in parameters and "node_id" not in parameters


def test_files_in_scope_has_no_default(p7_conn):
    # Open question 3 once more: P7 defines no corpus area.
    import inspect
    parameter = inspect.signature(summarize_protected).parameters["files_in_scope"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_display.py -v`
Expected: FAIL — `ImportError: cannot import name 'REDACTED' from 'privacy.display'`

- [ ] **Step 3: Write `src/privacy/display.py`**

```python
# src/privacy/display.py
"""§8.4's UI privacy: the five configurable facets, and the aggregate-safe summary.

§8.4's paragraph gives both surfaces and both defaults. The facets are its own list --
"whether names, previews, thumbnails, OCR text, or location data are shown" -- and the
default direction is its own example: "A summary such as '11 protected identity
records' may be safe to show, while a visible list of passport filenames on a shared
screen may not be." The aggregate is the default; the expansion is the user's act.

`ProtectedSummary` has two fields because Done-means 10 says it "cannot return
filenames or content", and the cheapest way to make that true is for there to be
nowhere to put one.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, fields
from types import MappingProxyType

from database_agent.files_table import get_file

from privacy.classification import resolve_class
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.policy import current_policy
from privacy.vocabulary import DISPLAY_FACETS, HANDLING_CLASSES

#: SPEC §10: "each shown | redacted". Two values, and no third.
SHOWN: str = "shown"
REDACTED: str = "redacted"
SETTING_VALUES: tuple[str, str] = (SHOWN, REDACTED)


class UnknownDisplaySetting(ValueError):
    """A facet or a value outside §8.4's list. A load error, never a fallback."""


@dataclass(frozen=True)
class RedactionSettings:
    """§8.4's five configurable facets, in §8.4's order."""

    names: str
    previews: str
    thumbnails: str
    ocr_text: str
    location_data: str

    def facet(self, name: str) -> str:
        if name not in DISPLAY_FACETS:
            raise UnknownDisplaySetting(
                f"{name!r} is not one of §8.4's five display facets {DISPLAY_FACETS}")
        return getattr(self, name)


@dataclass(frozen=True)
class ProtectedSummary:
    """§8.4's aggregate: "11 protected identity records", and nothing that names a file.

    Two fields, and deliberately no third. There is no `examples`, no `file_ids` and no
    `filenames`, because Done-means 10 forbids returning one and a field that does not
    exist cannot be populated by a later caller in a hurry.
    """

    count: int
    class_breakdown: Mapping[str, int]


def display_policy(conn: sqlite3.Connection, *,
                   plan_version: str) -> RedactionSettings:
    """The five facets as they resolve under the policy in force for `plan_version`.

    A facet the stored policy does not mention resolves through `MORE_REDACTING`, never
    to `shown`: §8.4's `must` is that the default posture be "local-first and
    data-minimizing", and §8.4's own example settles which direction that points.

    `plan_version` is a keyword because §8.8 places "Privacy and model-consent policies"
    inside the plan version. SPEC §10's published surface is `Gate.display_policy()`;
    the facade holds the plan version and supplies it here.
    """
    stored = current_policy(conn, plan_version=plan_version).redaction_settings
    unknown = [facet for facet in stored if facet not in DISPLAY_FACETS]
    if unknown:
        raise UnknownDisplaySetting(
            f"{sorted(unknown)} are not among §8.4's five display facets "
            f"{DISPLAY_FACETS}")
    resolved = {}
    for facet in DISPLAY_FACETS:
        value = stored.get(facet, MORE_REDACTING[facet])
        if value not in SETTING_VALUES:
            raise UnknownDisplaySetting(
                f"{facet} = {value!r} is not one of {SETTING_VALUES}; a value outside "
                "the set is a load error, not a fallback")
        resolved[facet] = value
    return RedactionSettings(**resolved)


def summarize_protected(conn: sqlite3.Connection, scope: str, *,
                        store: ClassificationStore,
                        files_in_scope: Callable[[str], Sequence[str]]
                        ) -> ProtectedSummary:
    """Counts only. §5.2: "avoid showing sensitive filenames"; §7.5: "11 protected
    personal records".

    `count` follows the `protected` flag, never the handling class (SPEC §2, Open
    question 1). `class_breakdown` covers every file in scope by its RESOLVED class,
    so a corpus nothing has classified reports `unreadable_unclassified` rather than
    disappearing -- which is today's ordinary state, since D2 leaves the detector
    unwritten.

    `files_in_scope` has no default: Open question 3 leaves "corpus area" unnamed.
    """
    counts = {handling_class: 0 for handling_class in HANDLING_CLASSES}
    protected = 0
    for file_id in files_in_scope(scope):
        record = store.current(file_id, get_file(conn, file_id)["content_hash"])
        counts[resolve_class(record)] += 1
        if record is not None and record.protected:
            protected += 1
    return ProtectedSummary(count=protected,
                            class_breakdown=MappingProxyType(counts))
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_display.py -v`
Expected: PASS — 17 passed

- [ ] **Step 5: Commit**

```bash
git add src/privacy/display.py tests/p7/test_p7_display.py
git commit -m "feat(P7): display_policy and summarize_protected, aggregate-safe at the type level"
```

---
### Task 19: The transport guard — Done-means 3's instrument

**Files:**
- Create: `src/privacy/transport_guard.py`
- Create: `tests/p7/transport_fixtures.py`
- Test: `tests/p7/test_p7_transport.py`

**Interfaces:**
- Consumes: `inspect`, `typing`, `pathlib.Path`, `privacy.release.Released`,
  `evidence_shape.observation.Observation`, `evidence_shape.text_units.TextUnit`.
- Produces (`transport_guard.py`):
  - `CONTENT_PARAMETER_TYPES: frozenset[type]` = `{str, bytes, Path, Observation, TextUnit}`.
  - `egress_functions(module) -> list[Callable]`.
  - `assert_single_egress(module) -> None`.
  - `MultipleEgressPoints`, `NoEgressPoint`, `UnreleasedContentParameter`.

**Done-means:** 3 (the instrument; see the skeleton's coverage table for what remains).

**Say it plainly, here and in the report: this task proves the instrument, not the property.**
P8 Done-means 1 is the property — *"Exactly one function in the codebase constructs a model request,
and its only parameter type is P7's `Released`"* — and the transport is P8's, which does not exist.
P7 ships `assert_single_egress` and proves it correct in both directions against fixture transports.
Running it over the real transport is P8's obligation and cannot happen here. A named test in the
suite says so, so the limitation lives beside the code rather than in a report nobody rereads.

**`NoEgressPoint` is added by this task.** The skeleton names two exceptions, and a module with no
public function at all is neither of them — it is a transport that cannot send, which passes any
check written as `len(functions) <= 1` and is exactly the vacuous pass this layer exists to prevent.
Reported as an addition.

**The check reads resolved annotations, never source text.** `typing.get_type_hints` plus
`inspect.signature`, with unions and generic arguments flattened, so `prompt: str | None` and
`excerpts: list[str]` are both caught. A source scan sees the word `Released` in a docstring and
passes a transport that takes a string, which is the failure this repository has recorded more than
once and the reason `code_tokens()` exists in `tests/p3`.

**An unannotated parameter fails.** A transport whose parameter has no annotation is not a transport
whose only content parameter is a `Released`; it is a transport nobody can check, and a checker that
read "no annotation" as "not content" would pass the easiest possible bypass.

**A non-content parameter is permitted.** Done-means 3 constrains the *content* parameter, so a
`timeout_seconds: float` is fine and a fixture proves it. A checker that also banned those would be
rejected by P8 for a reason unrelated to privacy, and a rejected checker guards nothing.

- [ ] **Step 1: Write the fixture transports and the failing test**

```python
# tests/p7/transport_fixtures.py
"""One conforming transport and several that are not, as importable module objects.

They are built with `types.ModuleType` rather than as a dozen files because
`assert_single_egress` takes a MODULE, and a dozen single-function files under `tests/`
would be a dozen more names in pytest's rootless-module namespace -- the collision that
has already cost this project a whole-suite outage twice.

There is no `from __future__ import annotations` here on purpose: the checker resolves
annotations through `typing.get_type_hints`, and a fixture that stringified everything
would be exercising the resolution path rather than the parameter types.
"""
from pathlib import Path
from types import FunctionType, ModuleType

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.release import Released


def _module(name: str, **functions: FunctionType) -> ModuleType:
    """A module whose members are exactly `functions`, under the keyword's name.

    The keyword is the PUBLIC name: `send=_send` binds `module.send`, so a fixture
    written with a private local name still presents a public entry point. `__module__`
    is rebound too, so `egress_functions` can tell a function defined here from one
    merely imported -- the distinction that stops `from json import dumps` at the top
    of a transport counting as a second entry point.
    """
    module = ModuleType(name)
    for public_name, function in functions.items():
        function.__module__ = name
        function.__name__ = public_name
        function.__qualname__ = public_name
        setattr(module, public_name, function)
    return module


# --- conforming --------------------------------------------------------------

def _send(payload: Released) -> str:
    return payload.release_id


CONFORMING = _module("fixture_transport_conforming", send=_send)


def _send_with_timeout(payload: Released, *, timeout_seconds: float) -> str:
    return payload.release_id


#: Done-means 3 constrains the CONTENT parameter. A timeout is not content.
CONFORMING_WITH_A_TIMEOUT = _module("fixture_transport_timeout",
                                    send=_send_with_timeout)


def _send_public(payload: Released) -> str:
    return payload.release_id


def _helper(text: str) -> str:
    return text


#: A private helper taking a string is not an egress point.
CONFORMING_WITH_A_PRIVATE_HELPER = _module(
    "fixture_transport_private_helper", send=_send_public, _helper=_helper)


# --- non-conforming ----------------------------------------------------------

def _send_one(payload: Released) -> str:
    return payload.release_id


def _send_batch(payload: Released) -> str:
    return payload.release_id


TWO_ENTRY_POINTS = _module("fixture_transport_two", send=_send_one,
                           send_batch=_send_batch)


def _send_a_string(prompt: str) -> str:
    return prompt


TAKES_A_STRING = _module("fixture_transport_string", send=_send_a_string)


def _send_with_attachment(payload: Released, attachment: Path) -> str:
    return payload.release_id


TAKES_A_PATH = _module("fixture_transport_path", send=_send_with_attachment)


def _send_an_observation(observation: Observation) -> str:
    return observation.raw_value


TAKES_AN_OBSERVATION = _module("fixture_transport_observation",
                               send=_send_an_observation)


def _send_a_text_unit(unit: TextUnit) -> str:
    return unit.text


TAKES_A_TEXT_UNIT = _module("fixture_transport_text_unit", send=_send_a_text_unit)


def _send_optional_prompt(payload: Released, prompt: str | None = None) -> str:
    return payload.release_id


#: `str | None` is still a string parameter. A checker comparing the annotation to
#: `str` by identity would pass this.
TAKES_AN_OPTIONAL_STRING = _module("fixture_transport_optional_string",
                                   send=_send_optional_prompt)


def _send_a_list_of_strings(payload: Released, excerpts: list[str]) -> str:
    return payload.release_id


TAKES_A_LIST_OF_STRINGS = _module("fixture_transport_list_of_strings",
                                  send=_send_a_list_of_strings)


def _send_unannotated(payload) -> str:
    return str(payload)


TAKES_AN_UNANNOTATED_PARAMETER = _module("fixture_transport_unannotated",
                                         send=_send_unannotated)


def _send_no_released(*, timeout_seconds: float) -> str:
    return str(timeout_seconds)


TAKES_NO_RELEASED = _module("fixture_transport_no_released", send=_send_no_released)

NO_ENTRY_POINT = _module("fixture_transport_empty")
```

```python
# tests/p7/test_p7_transport.py
"""Done-means 3's instrument, proven in both directions.

A checker exercised only on the passing case is an assertion that has never been
tested. Every non-conforming shape below is one a real transport could plausibly grow.
"""
from pathlib import Path

import pytest

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.release import Released
from privacy.transport_guard import (
    CONTENT_PARAMETER_TYPES, MultipleEgressPoints, NoEgressPoint,
    UnreleasedContentParameter, assert_single_egress, egress_functions,
)

from transport_fixtures import (
    CONFORMING, CONFORMING_WITH_A_PRIVATE_HELPER, CONFORMING_WITH_A_TIMEOUT,
    NO_ENTRY_POINT, TAKES_AN_OBSERVATION, TAKES_AN_OPTIONAL_STRING,
    TAKES_AN_UNANNOTATED_PARAMETER, TAKES_A_LIST_OF_STRINGS, TAKES_A_PATH,
    TAKES_A_STRING, TAKES_A_TEXT_UNIT, TAKES_NO_RELEASED, TWO_ENTRY_POINTS,
)


# --- the conforming direction ------------------------------------------------

def test_a_conforming_transport_passes():
    assert assert_single_egress(CONFORMING) is None


def test_a_non_content_parameter_is_permitted():
    # Done-means 3 constrains the CONTENT parameter: "its only content parameter is a
    # `Released`". A checker that also banned a timeout would be rejected by P8 for a
    # reason unrelated to privacy, and a rejected checker guards nothing.
    assert assert_single_egress(CONFORMING_WITH_A_TIMEOUT) is None


def test_a_private_helper_is_not_an_egress_point():
    assert assert_single_egress(CONFORMING_WITH_A_PRIVATE_HELPER) is None


def test_egress_functions_lists_only_public_functions_defined_in_the_module():
    assert [f.__name__ for f in egress_functions(CONFORMING)] == ["send"]
    assert [f.__name__ for f in
            egress_functions(CONFORMING_WITH_A_PRIVATE_HELPER)] == ["send"]
    assert [f.__name__ for f in egress_functions(TWO_ENTRY_POINTS)] == [
        "send", "send_batch"]
    assert egress_functions(NO_ENTRY_POINT) == []


# --- the non-conforming direction --------------------------------------------

def test_two_entry_points_fail():
    with pytest.raises(MultipleEgressPoints):
        assert_single_egress(TWO_ENTRY_POINTS)


def test_no_entry_point_fails():
    # A transport that cannot send passes any check written as `len(functions) <= 1`,
    # and that vacuous pass is what this whole layer exists to prevent.
    with pytest.raises(NoEgressPoint):
        assert_single_egress(NO_ENTRY_POINT)


def test_a_transport_taking_a_string_fails():
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_A_STRING)


def test_a_transport_taking_a_path_fails():
    # §8.4 puts "Paths" in the always-local set.
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_A_PATH)


def test_a_transport_taking_an_observation_fails():
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_AN_OBSERVATION)


def test_a_transport_taking_a_text_unit_fails():
    # P4's `TextUnit.text` is complete extracted text -- also always-local.
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_A_TEXT_UNIT)


def test_an_optional_string_is_still_a_string():
    # A checker comparing the annotation to `str` by identity would pass this one.
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_AN_OPTIONAL_STRING)


def test_a_list_of_strings_is_still_content():
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_A_LIST_OF_STRINGS)


def test_an_unannotated_parameter_fails():
    # "No annotation" is not "not content"; it is a parameter nobody can check, and
    # treating it as safe is the easiest possible bypass.
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_AN_UNANNOTATED_PARAMETER)


def test_a_transport_with_no_released_parameter_fails():
    # SPEC Purpose: "The model transport accepts a `Released` and nothing else."
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_NO_RELEASED)


# --- how the check is made ---------------------------------------------------

def test_the_check_reads_signatures_and_never_source_text():
    # A source scan sees `Released` in a docstring and passes a transport that takes a
    # string. Proven by giving a non-conforming transport a docstring that says
    # `Released` three times and watching it fail anyway.
    TAKES_A_STRING.send.__doc__ = "Sends a Released. Released. Released."
    with pytest.raises(UnreleasedContentParameter):
        assert_single_egress(TAKES_A_STRING)


def test_the_forbidden_types_are_the_five_the_contract_names():
    assert CONTENT_PARAMETER_TYPES == frozenset(
        {str, bytes, Path, Observation, TextUnit})


def test_released_is_not_among_the_forbidden_types():
    assert Released not in CONTENT_PARAMETER_TYPES


# --- what this test file cannot do -------------------------------------------

def test_running_this_over_the_real_transport_is_p8s_obligation():
    """Done-means 3 is a STATIC PROPERTY OF A TRANSPORT P7 DOES NOT OWN.

    P8 Done-means 1: "Exactly one function in the codebase constructs a model request,
    and its only parameter type is P7's `Released`." P8 does not exist, so the property
    cannot be asserted here, and this suite proves only that the instrument is correct
    -- in both directions, which is the most P7 can honestly claim.

    The two layers P7 CAN prove are elsewhere and are green: L1, the unforgeable
    single-use token (Task 12), and L2, the single materialisation locus (Tasks 9 and
    21). This test exists so the gap is recorded in the suite rather than in a report.
    """
    import importlib.util
    assert importlib.util.find_spec("llm_harness") is None, (
        "P8 has landed: run `assert_single_egress` over its transport module and "
        "replace this test with that assertion")
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_transport.py -v`
Expected: FAIL — `ImportError: cannot import name 'CONTENT_PARAMETER_TYPES' from
'privacy.transport_guard'`

- [ ] **Step 3: Write `src/privacy/transport_guard.py`**

```python
# src/privacy/transport_guard.py
"""Done-means 3's instrument. P7 ships the checker; P8 runs it over its transport.

The property is P8's -- "Exactly one function in the codebase constructs a model
request, and its only parameter type is P7's `Released`" (P8 Done-means 1) -- and P8
does not exist. What P7 can do is make the check mechanical and prove it correct in
both directions, so that when P8 lands the assertion is already written and already
tested.

Everything here reads RESOLVED ANNOTATIONS. A source-text scan sees `Released` in a
docstring and passes a transport that takes a string; that technique has produced a
false result on this project more than once, which is why `code_tokens()` exists in
tests/p3 and why nothing here reads a `.py` file.
"""
from __future__ import annotations

import inspect
import typing
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.release import Released

#: The types a transport may not take. §8.4's always-local set is the reason: a `str`
#: or `bytes` is content, a `Path` is one of "Paths", and an `Observation` or a
#: `TextUnit` carries "complete extracted text". A `Released` is none of these -- it is
#: a capability the gate minted, and its payload is already redacted and already
#: audited.
CONTENT_PARAMETER_TYPES: frozenset[type] = frozenset(
    {str, bytes, Path, Observation, TextUnit})


class MultipleEgressPoints(Exception):
    """More than one public function constructs a model request."""


class NoEgressPoint(Exception):
    """No public function does.

    Not the same failure, and not a passing one: a module with nothing in it satisfies
    "at most one entry point" trivially, and a checker that accepted it would report
    success for the one arrangement that guarantees the check never runs on anything.
    """


class UnreleasedContentParameter(Exception):
    """A parameter is content, is unannotated, or the one `Released` is missing."""


def egress_functions(module: ModuleType) -> list[Callable]:
    """The module's public functions, defined in it, ordered by name.

    `__module__` is what separates a function DEFINED here from one imported for use;
    without it `from json import dumps` at the top of a transport would count as a
    second entry point.
    """
    found = [value for name, value in vars(module).items()
             if not name.startswith("_") and inspect.isfunction(value)
             and value.__module__ == module.__name__]
    return sorted(found, key=lambda function: function.__name__)


def assert_single_egress(module: ModuleType) -> None:
    """Exactly one entry point, and its only content parameter is a `Released`.

    Raises rather than returning a verdict, on the same principle as P4's
    `check_span_anchor`: a checker that returns a value is a checker a caller can
    ignore, and this one exists precisely because §8.4 says review discipline is not
    enough.
    """
    functions = egress_functions(module)
    if not functions:
        raise NoEgressPoint(
            f"{module.__name__} has no public function; a transport that cannot send "
            "satisfies a one-entry-point check vacuously")
    if len(functions) > 1:
        raise MultipleEgressPoints(
            f"{module.__name__} has {len(functions)} public functions "
            f"{[f.__name__ for f in functions]}; P8 Done-means 1 requires exactly one")

    function = functions[0]
    hints = typing.get_type_hints(function)
    released_parameters = []
    for name in inspect.signature(function).parameters:
        if name not in hints:
            raise UnreleasedContentParameter(
                f"{module.__name__}.{function.__name__}({name}) has no annotation; "
                "an unannotated parameter is not a checked one")
        types = _types_in(hints[name])
        forbidden = types & CONTENT_PARAMETER_TYPES
        if forbidden:
            raise UnreleasedContentParameter(
                f"{module.__name__}.{function.__name__}({name}: {hints[name]}) is a "
                f"content parameter ({sorted(t.__name__ for t in forbidden)}); §8.4's "
                "always-local set means the transport takes references, never content")
        if Released in types:
            released_parameters.append(name)

    if len(released_parameters) != 1:
        raise UnreleasedContentParameter(
            f"{module.__name__}.{function.__name__} takes {len(released_parameters)} "
            "`Released` parameters; exactly one is required -- the payload is minted "
            "by the gate and there is no other way in")


def _types_in(annotation: object) -> set[type]:
    """Every concrete type reachable inside an annotation.

    Flattened, so `str | None`, `list[str]` and `Sequence[Path]` are all recognised as
    content. A checker comparing the annotation to `str` by identity passes every one
    of them, and each is a shape a real transport plausibly grows.
    """
    found: set[type] = set()
    pending: list[object] = [annotation]
    while pending:
        current = pending.pop()
        if isinstance(current, type):
            found.add(current)
            continue
        pending.extend(argument for argument in typing.get_args(current)
                       if argument is not type(None))
    return found
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_transport.py -v`
Expected: PASS — 17 passed

- [ ] **Step 5: Commit**

```bash
git add src/privacy/transport_guard.py tests/p7/transport_fixtures.py \
        tests/p7/test_p7_transport.py
git commit -m "feat(P7): assert_single_egress, Done-means 3's instrument proven in both directions"
```

---
### Task 20: The published fixtures (SPEC §11)

**Files:**
- Create: `src/privacy/fixtures.py`
- Test: `tests/p7/test_p7_fixtures.py`

**Interfaces:**
- Consumes: `privacy.release.ModelCallRequest`, `.ModelTarget`, `.Target`, `.Released`, `.Denied`,
  `.NeedsConsent`, `.ReleaseDecision`, `.Gate`; `privacy.denial.deny`, `.RemedyOption`,
  `.PROTECTED_RECORDS_TEMPLATE`; `privacy.items.Excerpt`, `.RedactedIdentifier`, `.CandidateLabel`,
  `.MetadataField`, `.EvidenceReference`, `.Filename`; `privacy.classification.ClassificationRecord`;
  `privacy.policy.Policy`; `privacy.audit.AUDIT_FIELDS`, `.AuditRecord`;
  `privacy.vocabulary.DENIAL_REASONS`, `.CONSENT_OPTIONS`, `.OPERATION_MODES`;
  `evidence_shape.location.TextSpan`.
- Produces (`fixtures.py`):
  - `GateFixture` — frozen: `number`, `spec_case`, `request`, `decision`, `audit_record`, `policy`,
    `classification = None`, `p8_obligation = None`.
  - `FIXTURES: tuple[GateFixture, ...]` — sixteen.
  - `by_number(n) -> GateFixture`.
  - `FIXTURE_COVERAGE: Mapping[str, tuple[int, ...]]` — every SPEC §11 list member → fixture numbers.
  - `SPEC_11_CASES: tuple[str, ...]` — §11's list, item for item, in §11's order.
  - `GATE_ARGUMENTS: tuple[str, ...]`, `gate_arguments(fixture, *, store) -> dict[str, object]`.
  - `VOLATILE_AUDIT_FIELDS: frozenset[str]`, `IDENTITY_AUDIT_FIELDS: frozenset[str]`.
  - `FIXTURE_CEILING: int`, `FIXTURE_OVER_BUDGET: int`, `CEILING_KEY: str`.
  - `CLOUD: ModelTarget`, `LOCAL: ModelTarget`, `FIXTURE_CONTENT_HASH: str`.

**Done-means:** 11 (first clause; *"P8's harness passes its own tests against those fixtures"* is
P8's test run and cannot execute here — the skeleton's coverage table already says so).

**This task pins `Gate.__init__`, and that is reported.** Task 11 pins `Gate.release`'s parameters
and says nothing about the constructor, and a fixture that cannot be replayed through the real gate
is a fixture that will drift — *"a fixture that drifts from the implementation is worse than none."*
So `GATE_ARGUMENTS` is published here and Task 11's `Gate` must accept exactly these keywords:

```text
store                        ClassificationStore                    (Task 4)
plan_version                 str                                    (§8.8; policy is plan-scoped)
classifier                   IdentifierClassifier                   (Task 8, injected, no default)
transform                    RedactionTransform                     (Task 8, injected, no default)
unclassified_permits_local   bool                                   (Open question 5, no default)
scope_for                    Callable[[str], str]                   (Open question 3, no default)
files_in_scope               Callable[[str], Sequence[str]]         (Open question 3, no default)
component_version            str
now                          Callable[[], str]
user_id                      str | None
```

Every one traces to a published requirement or an open question. There is no `force`, no `override`
and no `bypass`; Task 11's `FORBIDDEN_PARAMETER_NAMES` check runs over this set too.

**Two fields are added to `GateFixture` and both are additive with defaults**, so the skeleton's
six-name positional order is unchanged. `classification` carries the `ClassificationRecord` the
fixture assumes — without it a fixture cannot be set up, and putting the classification in the test
would make each fixture's meaning live in two files. `p8_obligation` carries the sentence the
skeleton requires two fixtures to say *"in their own metadata"*. Reported.

**Two numbers live here, and they are the allowlist Task 21 names.** `FIXTURE_CEILING` and
`FIXTURE_OVER_BUDGET` exist so the `dossier_over_budget` fixture has a comparison to fail; the test
installs `FIXTURE_CEILING` through P1's `budget.set_ceiling`, so the gate still reads the ceiling
from `budget.get_ceiling` and P7 holds no product ceiling. Task 21's numeric guard allowlists
`privacy.fixtures` by name and by these two names only. Reported, because a numeric allowlist is
exactly the kind of hole that widens.

**The audit record is compared field for field, with the substitution made explicit.**
`VOLATILE_AUDIT_FIELDS` are the ones the gate mints at call time — `audit_id`, `release_id`,
`observed_at`, `appended_at`, `policy_version`, `authorizing_policy` — and `IDENTITY_AUDIT_FIELDS`
are the ones the test's real P1 row supplies — `file_id`, `file_ids`. Everything else must match
exactly. The volatile and identity fields are then asserted individually against the materialised
values, so nothing is skipped, only relocated.

**`content_hash` is NOT volatile.** P1's `record_file` accepts a `content_hash` keyword, so the
fixture's hash is the row's hash and the classification's `(file_id, content_hash)` key is the
fixture's own — which is the point of D2's keying.

**The sixteen fixtures, and what each is for.**

| # | Case | Mode | Decision |
|---|---|---|---|
| 1 | protected file, cloud target | `hybrid` | `Denied(protected_cloud_target)` |
| 2 | no classification, cloud target | `hybrid` | `Denied(unclassified)` |
| 3 | policy revoked | `cloud_assisted` | `Denied(policy_revoked)` |
| 4 | `Protected Records` residual, excerpt requested | `cloud_assisted` | `Denied(protected_records_template)` |
| 5 | excerpt spanning the whole text unit | `hybrid` | `Denied(whole_document_requested)` |
| 6 | caller's budget above the configured ceiling | `hybrid` | `Denied(dossier_over_budget)` — **P8 obligation** |
| 7 | GPS requested as an item | `hybrid` | `Denied(always_local_item)` |
| 8 | non-protected file, cloud target | `offline` | `Denied(mode_forbids_target)` |
| 9 | non-protected file, cloud target, grant present, identifier redacted | `cloud_assisted` | `Released` |
| 10 | dossier requires sensitive text | `hybrid` | `NeedsConsent` (four options) — **P8 obligation** |
| 11 | protected file, cloud target | `offline` | `Denied(mode_forbids_target)` |
| 12 | protected file, cloud target | `local_model` | `Denied(mode_forbids_target)` |
| 13 | protected file, cloud target, no grant for the area | `cloud_assisted` | `Denied(protected_cloud_target)` |
| 14 | unclassified file, **local** target, `unclassified_permits_local = False` | `local_model` | `Denied(unclassified)` |
| 15 | unclassified file, **local** target, `unclassified_permits_local = True` | `local_model` | `Released` |
| 16 | `Protected Records` residual, **filename** requested | `cloud_assisted` | `Denied(protected_records_template)` |

Fixtures 11, 12, 1 and 13 are §11's *"protected file under each of the four modes"*, in mode order.
Fixtures 14 and 15 are the two branches of **Open question 5** — *"Does `unreadable_unclassified`
permit a local model call?"* — carried as data rather than answered, which is the only way a fixture
set can hold an open question open. Fixture 16 is where **B5d / C9a** shows up: `filename` is P7's
sixth releasable kind and §8.4 names five, and §7.3 forbids filenames *and* content for Protected
Records, so the denial is the same either way and the fixture does not settle the question.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_fixtures.py
"""Done-means 11's first clause, and the replay that keeps the fixtures honest.

"a fixture that drifts from the implementation is worse than none." So every fixture
is replayed through the real gate and compared field for field, with the two classes of
field the gate or the test mints asserted separately rather than skipped.
"""
import dataclasses
import json

import pytest

from database_agent.budget import get_ceiling, set_ceiling
from database_agent.files_table import get_file, record_file

from privacy.audit import AUDIT_FIELDS, audit_records_for
from privacy.classification_store import ClassificationStore
from privacy.fixtures import (
    CEILING_KEY, FIXTURES, FIXTURE_CEILING, FIXTURE_CONTENT_HASH, FIXTURE_COVERAGE,
    GATE_ARGUMENTS, IDENTITY_AUDIT_FIELDS, SPEC_11_CASES, VOLATILE_AUDIT_FIELDS,
    by_number, gate_arguments,
)
from privacy.gate import Gate
from privacy.policy import set_policy
from privacy.release import Denied, NeedsConsent, Released, Target
from privacy.vocabulary import CONSENT_OPTIONS, DENIAL_REASONS, OPERATION_MODES

from privacy.authorship import SUBSYSTEM

COMPONENT = "0.1.0"


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


def materialise(conn, tmp_path, fixture, store):
    """Give the fixture a real P1 row and a real classification, and rebind the request.

    `record_file` mints the `file_id` and ACCEPTS the `content_hash`, so the identity
    substitution is exactly one field wide -- which is why `IDENTITY_AUDIT_FIELDS` has
    two members and not four.
    """
    root = tmp_path / f"fixture-{fixture.number}"
    root.mkdir()
    document = root / "subject.pdf"
    document.write_bytes(f"%PDF-1.4 fixture {fixture.number}".encode())
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(root), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True,
        content_hash=FIXTURE_CONTENT_HASH)
    content_hash = get_file(conn, file_id)["content_hash"]
    assert content_hash == FIXTURE_CONTENT_HASH
    if fixture.classification is not None:
        store.write(dataclasses.replace(fixture.classification, file_id=file_id))
    set_policy(conn, fixture.policy, component_version=COMPONENT,
               user_id="joseph",
               reason="the published fixture's policy")
    set_ceiling(conn, CEILING_KEY, FIXTURE_CEILING)
    request = dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,), group_id=None))
    return file_id, content_hash, request


def replay(conn, tmp_path, fixture, store):
    file_id, content_hash, request = materialise(conn, tmp_path, fixture, store)
    gate = Gate(conn, **gate_arguments(fixture, store=store))
    return file_id, content_hash, gate.release(request)


# --- SPEC §11's list, item for item -----------------------------------------

def test_every_spec_11_case_has_at_least_one_fixture():
    # "with a test that fails if a list member has no fixture."
    for case in SPEC_11_CASES:
        assert FIXTURE_COVERAGE.get(case), case


def test_every_denial_reason_has_at_least_one_fixture():
    for reason in DENIAL_REASONS:
        numbers = FIXTURE_COVERAGE.get(reason)
        assert numbers, reason
        for number in numbers:
            decision = by_number(number).decision
            assert isinstance(decision, Denied)
            assert decision.reason == reason


def test_every_coverage_entry_names_a_real_fixture():
    numbers = {fixture.number for fixture in FIXTURES}
    for case, listed in FIXTURE_COVERAGE.items():
        assert set(listed) <= numbers, case


def test_there_is_a_protected_file_under_each_of_the_four_modes():
    numbers = FIXTURE_COVERAGE["a protected file under each of the four modes"]
    modes = [by_number(number).policy.operation_mode for number in numbers]
    assert modes == list(OPERATION_MODES)
    for number in numbers:
        assert by_number(number).classification.protected is True


def test_the_numbers_are_dense_and_unique():
    assert [fixture.number for fixture in FIXTURES] == list(
        range(1, len(FIXTURES) + 1))
    assert len(FIXTURES) == 16


def test_by_number_raises_on_an_unknown_fixture():
    assert by_number(1) is FIXTURES[0]
    with pytest.raises(KeyError):
        by_number(99)


# --- the three branches are all present -------------------------------------

def test_there_is_a_clean_released_with_redaction_applied():
    fixture = by_number(FIXTURE_COVERAGE[
        "a clean `Released` with redaction applied"][0])
    assert isinstance(fixture.decision, Released)
    assert fixture.decision.redaction_manifest
    assert fixture.audit_record["redaction_applied"] is True


def test_the_needs_consent_fixture_offers_all_four_options():
    fixture = by_number(FIXTURE_COVERAGE[
        "a `NeedsConsent` returning all four options"][0])
    assert isinstance(fixture.decision, NeedsConsent)
    assert tuple(fixture.decision.options) == tuple(CONSENT_OPTIONS)
    assert len(CONSENT_OPTIONS) == 4


def test_the_two_open_question_5_fixtures_disagree_only_on_the_parameter():
    # OQ5: "Does `unreadable_unclassified` permit a *local* model call?" Carried as
    # data on both branches, which is the only way a fixture set holds a question open.
    denied, released = by_number(14), by_number(15)
    assert denied.classification is None and released.classification is None
    assert denied.request.model_target == released.request.model_target
    assert isinstance(denied.decision, Denied)
    assert isinstance(released.decision, Released)
    assert gate_arguments(denied, store=None)["unclassified_permits_local"] is False
    assert gate_arguments(released, store=None)["unclassified_permits_local"] is True


# --- the obligations on P8 --------------------------------------------------

def test_the_budget_fixture_says_it_is_p8s_ladder_that_must_run_first():
    fixture = by_number(FIXTURE_COVERAGE["dossier_over_budget"][0])
    assert fixture.p8_obligation
    assert "ladder" in fixture.p8_obligation
    assert "P8 failure" in fixture.p8_obligation


def test_the_consent_fixture_says_the_branch_must_reach_the_caller_intact():
    fixture = by_number(FIXTURE_COVERAGE[
        "a `NeedsConsent` returning all four options"][0])
    assert fixture.p8_obligation
    assert "abstain" in fixture.p8_obligation


def test_exactly_two_fixtures_carry_an_obligation_on_p8():
    carrying = [f.number for f in FIXTURES if f.p8_obligation]
    assert len(carrying) == 2


# --- the replay: every fixture, through the real gate -----------------------

@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_the_real_gate_reproduces_the_fixture_decision(
        p7_conn, tmp_path, store, number):
    fixture = by_number(number)
    _, _, decision = replay(p7_conn, tmp_path, fixture, store)
    assert type(decision) is type(fixture.decision)
    if isinstance(decision, Denied):
        assert decision.reason == fixture.decision.reason
        assert decision.explanation
        assert decision.remedy_options
    if isinstance(decision, NeedsConsent):
        assert tuple(decision.options) == tuple(CONSENT_OPTIONS)
    if isinstance(decision, Released):
        assert decision.release_id
        assert decision.audit_id


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_the_real_gate_reproduces_the_fixture_audit_record(
        p7_conn, tmp_path, store, number):
    # "each fixture carries the audit record the gate would have appended, and ...
    # replaying the fixture through the real gate reproduces that record field for
    # field."
    fixture = by_number(number)
    file_id, _, _ = replay(p7_conn, tmp_path, fixture, store)
    records = audit_records_for(p7_conn, file_id=file_id)
    assert len(records) == 1
    appended = dataclasses.asdict(records[0])

    skipped = VOLATILE_AUDIT_FIELDS | IDENTITY_AUDIT_FIELDS
    assert {name: value for name, value in appended.items()
            if name not in skipped} == {
        name: value for name, value in fixture.audit_record.items()
        if name not in skipped}


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_the_minted_and_substituted_fields_are_checked_and_not_skipped(
        p7_conn, tmp_path, store, number):
    fixture = by_number(number)
    file_id, content_hash, decision = replay(p7_conn, tmp_path, fixture, store)
    record = audit_records_for(p7_conn, file_id=file_id)[0]

    assert record.file_id == file_id
    assert tuple(record.file_ids) == (file_id,)
    assert record.content_hash == content_hash          # not volatile: P1 keyed on it
    assert record.audit_id
    assert record.observed_at
    assert record.policy_version
    assert record.authorizing_policy == record.policy_version
    if isinstance(decision, Released):
        assert record.release_id == decision.release_id
    else:
        assert record.release_id is None


def test_the_fixture_audit_records_name_every_spec_7_field():
    # A dropped field is a failing test: the fixtures are built from AUDIT_FIELDS, so
    # a §7 name with no fixture value cannot exist.
    for fixture in FIXTURES:
        assert set(fixture.audit_record) == set(AUDIT_FIELDS), fixture.number


def test_no_fixture_audit_record_carries_a_copy_of_the_text():
    # SPEC §7: `excerpts_included` stores "(observation_key, span) pairs plus the
    # redaction_manifest, not a second copy of the text".
    for fixture in FIXTURES:
        for pair in fixture.audit_record["excerpts_included"]:
            assert len(pair) == 2
            assert pair[0].startswith("sha256:")


# --- the ceiling is P1's, not P7's ------------------------------------------

def test_the_budget_fixture_reads_the_ceiling_from_p1(p7_conn, tmp_path, store):
    fixture = by_number(FIXTURE_COVERAGE["dossier_over_budget"][0])
    materialise(p7_conn, tmp_path, fixture, store)
    assert get_ceiling(p7_conn, CEILING_KEY) == FIXTURE_CEILING
    assert CEILING_KEY == "model.max_dossier_tokens_per_call"


def test_only_the_two_allowlisted_numbers_live_in_the_fixture_module():
    # Task 21 allowlists `privacy.fixtures` by name and by these two names only.
    import privacy.fixtures as module
    numbers = {name for name, value in vars(module).items()
               if not name.startswith("__")
               and isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {"FIXTURE_CEILING", "FIXTURE_OVER_BUDGET"}


# --- the constructor this task pins -----------------------------------------

def test_the_gate_accepts_exactly_the_published_constructor_keywords():
    import inspect
    parameters = inspect.signature(Gate.__init__).parameters
    keywords = [name for name, parameter in parameters.items()
                if parameter.kind is inspect.Parameter.KEYWORD_ONLY]
    assert set(keywords) == set(GATE_ARGUMENTS)
    assert list(parameters)[:2] == ["self", "conn"]


def test_the_open_question_injections_have_no_default():
    import inspect
    parameters = inspect.signature(Gate.__init__).parameters
    for name in ("unclassified_permits_local", "scope_for", "files_in_scope",
                 "classifier", "transform"):
        assert parameters[name].default is inspect.Parameter.empty, name


# --- what this suite cannot do ----------------------------------------------

def test_p8s_harness_passing_against_these_fixtures_is_p8s_test_run():
    """Done-means 11's second clause is not provable here.

    "Every one of the above has a published fixture, AND P8's harness passes its own
    tests against those fixtures with P7 unimplemented." The first half is this file.
    The second is a test run in a part that does not exist, and no assertion in P7 can
    stand in for it. Recorded in the suite so the split is not lost.
    """
    import importlib.util
    assert importlib.util.find_spec("llm_harness") is None
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_fixtures.py -v`
Expected: FAIL — `ImportError: cannot import name 'FIXTURES' from 'privacy.fixtures'`

- [ ] **Step 3: Write `src/privacy/fixtures.py`**

```python
# src/privacy/fixtures.py
"""SPEC §11's published fixtures, as golden records.

"Request -> decision pairs, one per `Denied.reason`, plus: a clean `Released` with
redaction applied; a `NeedsConsent` returning all four options; a protected file under
each of the four modes; an `unreadable_unclassified` file; a `Protected Records`
residual request. Each fixture carries the audit record the gate would have appended."

They exist so P8 can be built before P7 ships (Done-means 11). Two of them carry an
obligation on P8 specifically and say so in `p8_obligation`, because a fixture whose
purpose lives in a plan document is a fixture whose purpose is lost.

Nothing here is a stub. Every fixture is replayed through the real gate by
`tests/p7/test_p7_fixtures.py` and compared field for field -- a fixture that drifts
from the implementation is worse than none.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.location import TextSpan

from privacy.audit import AUDIT_FIELDS, AuditRecord
from privacy.classification import ClassificationRecord
from privacy.denial import PROTECTED_RECORDS_TEMPLATE, RemedyOption, deny
from privacy.items import (
    CandidateLabel, EvidenceReference, Excerpt, Filename, MetadataField,
    RedactedIdentifier,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, NeedsConsent, \
    Released, Target
from privacy.vocabulary import CONSENT_OPTIONS

#: The ceiling key P7 reads and never sets a value for (§8.6, M9).
CEILING_KEY: str = "model.max_dossier_tokens_per_call"

#: The two numbers in this package, and the whole of Task 21's numeric allowlist.
#: They are fixture data illustrating a comparison, not a product ceiling: the test
#: installs FIXTURE_CEILING through P1's `budget.set_ceiling`, so the gate still reads
#: it from `budget.get_ceiling`.
FIXTURE_CEILING: int = 4000
FIXTURE_OVER_BUDGET: int = 8000

FIXTURE_CONTENT_HASH: str = (
    "sha256:042896dc1966b8a6214e5383aba5b8b931cfa049d17aafa37eb8a77c859b95da")
FIXTURE_FILE_ID: str = "fixture-file"
OBSERVATION_KEY: str = (
    "sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd")
SENSITIVE_KEY: str = (
    "sha256:11e3d2a5b8c47f6019a4d3e5c7b2a10f9d8c6b4a3e2f1d0c9b8a7654321fedcba")
FIXTURE_OBSERVED_AT: str = "2026-08-22T12:00:00+00:00"

CLOUD: ModelTarget = ModelTarget(locality="cloud", model_id="acme-large",
                                 provider="Acme")
LOCAL: ModelTarget = ModelTarget(locality="local", model_id="llama-local",
                                 provider=None)

ACADEMICS: str = "Academics"
IDENTITY: str = "Identity"

#: Fields the gate mints at call time. Compared individually by the replay test, never
#: skipped -- only relocated.
VOLATILE_AUDIT_FIELDS: frozenset[str] = frozenset({
    "audit_id", "release_id", "observed_at", "appended_at", "policy_version",
    "authorizing_policy",
})

#: Fields whose value is the real P1 row's. `content_hash` is deliberately NOT here:
#: `record_file` accepts one, so the fixture's hash is the row's hash and D2's
#: (file_id, content_hash) key is the fixture's own.
IDENTITY_AUDIT_FIELDS: frozenset[str] = frozenset({"file_id", "file_ids"})

#: The keywords `Gate.__init__` accepts. Pinned here because the fixtures cannot be
#: replayed without it; every one traces to a published requirement or an open question.
GATE_ARGUMENTS: tuple[str, ...] = (
    "store", "plan_version", "classifier", "transform",
    "unclassified_permits_local", "scope_for", "files_in_scope",
    "component_version", "now", "user_id",
)

#: SPEC §11's list, item for item, in §11's order.
SPEC_11_CASES: tuple[str, ...] = (
    "protected_cloud_target", "unclassified", "policy_revoked",
    "protected_records_template", "whole_document_requested",
    "dossier_over_budget", "always_local_item", "mode_forbids_target",
    "a clean `Released` with redaction applied",
    "a `NeedsConsent` returning all four options",
    "a protected file under each of the four modes",
    "an `unreadable_unclassified` file",
    "a `Protected Records` residual request",
)


@dataclass(frozen=True)
class GateFixture:
    """One request -> decision pair, with the policy and classification it assumes."""

    number: int
    spec_case: str
    request: ModelCallRequest
    decision: object
    audit_record: Mapping[str, object]
    policy: Policy
    classification: ClassificationRecord | None = None
    p8_obligation: str | None = None


def by_number(number: int) -> GateFixture:
    for fixture in FIXTURES:
        if fixture.number == number:
            return fixture
    raise KeyError(f"no fixture numbered {number}")


def gate_arguments(fixture: GateFixture, *, store: object) -> dict[str, object]:
    """The keywords `Gate(conn, **...)` takes for this fixture.

    `unclassified_permits_local` is per fixture and has no default anywhere, because
    Open question 5 is unanswered: "Does `unreadable_unclassified` permit a *local*
    model call?" Fixtures 14 and 15 are its two branches.
    """
    return {
        "store": store,
        "plan_version": fixture.policy.plan_version,
        "classifier": _IDENTIFIER_CLASSIFIER,
        "transform": _REDACTION_TRANSFORM,
        "unclassified_permits_local": fixture.number == 15,
        "scope_for": lambda file_id: _SCOPE_BY_FIXTURE[fixture.number],
        "files_in_scope": lambda scope: tuple(fixture.request.target.file_ids),
        "component_version": "0.1.0",
        "now": lambda: FIXTURE_OBSERVED_AT,
        "user_id": "joseph",
    }


def _identifier_classifier(value: str) -> str:
    """The injected classifier, as a fixture. SPEC Deferred keeps the class opaque:
    "Which identifier classes exist and how each is transformed is not enumerated
    anywhere in the design." This returns one opaque string and enumerates nothing."""
    return "fixture-identifier-class"


def _redaction_transform(value: str, *, identifier_class: str) -> str:
    """The injected transform, as a fixture. Also deferred; also not enumerated."""
    return "[redacted]"


_IDENTIFIER_CLASSIFIER = _identifier_classifier
_REDACTION_TRANSFORM = _redaction_transform

_SCOPE_BY_FIXTURE: Mapping[int, str] = MappingProxyType({
    number: (IDENTITY if number in (1, 4, 11, 12, 13, 16) else ACADEMICS)
    for number in range(1, 17)
})


# --- builders ----------------------------------------------------------------

def _policy(mode: str, *, grants: Sequence[tuple[str, str]] = (),
            plan_version: str = "plan-1") -> Policy:
    return Policy(policy_version="", operation_mode=mode,
                  consent_grants=tuple(grants),
                  redaction_settings={"names": "redacted", "previews": "redacted",
                                      "thumbnails": "redacted",
                                      "ocr_text": "redacted",
                                      "location_data": "redacted"},
                  automatic_move_permissions={}, plan_version=plan_version,
                  set_at=FIXTURE_OBSERVED_AT)


def _classification(handling_class: str, *, protected: bool,
                    basis: str = "user") -> ClassificationRecord:
    return ClassificationRecord(
        file_id=FIXTURE_FILE_ID, content_hash=FIXTURE_CONTENT_HASH,
        handling_class=handling_class, protected=protected, basis=basis,
        evidence_refs=(OBSERVATION_KEY,) if basis == "detector" else (),
        reliability_state="user_confirmed" if basis == "user" else "validated",
        observed_at=FIXTURE_OBSERVED_AT)


def _request(*, stage: str, model_target: ModelTarget,
             requested_items: Sequence[object],
             max_dossier_tokens: int = FIXTURE_CEILING) -> ModelCallRequest:
    return ModelCallRequest(
        stage=stage,
        target=Target(file_ids=(FIXTURE_FILE_ID,), group_id=None),
        model_target=model_target,
        requested_items=tuple(requested_items),
        prompt_template_id=f"template.{stage}",
        prompt_fingerprint=f"fingerprint.{stage}",
        max_dossier_tokens=max_dossier_tokens)


def _audit(**over) -> Mapping[str, object]:
    """Built from `AUDIT_FIELDS`, so a §7 name with no fixture value cannot exist."""
    base = {
        "audit_id": None,
        "release_id": None,
        "policy_version": "",
        "plan_version": "plan-1",
        "stage": "grouping",
        "outcome": "denied",
        "operation_mode": "hybrid",
        "authorizing_policy": "",
        "file_sensitivity": "unreadable_unclassified",
        "excerpts_included": (),
        "redaction_applied": False,
        "redaction_manifest": (),
        "model": {"locality": "cloud", "model_id": "acme-large", "provider": "Acme"},
        "content_hashes": (FIXTURE_CONTENT_HASH,),
        "content_hash": FIXTURE_CONTENT_HASH,
        "prompt_fingerprint": "fingerprint.grouping",
        "file_id": FIXTURE_FILE_ID,
        "file_ids": (FIXTURE_FILE_ID,),
        "group_id": None,
        "consent_request_id": None,
        "user_id": "joseph",
        "observed_at": FIXTURE_OBSERVED_AT,
        "appended_at": FIXTURE_OBSERVED_AT,
    }
    missing = [name for name in AUDIT_FIELDS if name not in base]
    if missing:
        raise ValueError(
            f"AUDIT_FIELDS names {missing} and this module has no fixture value for "
            "them; SPEC §7 moved and the fixtures must move with it")
    base.update(over)
    return MappingProxyType({name: base[name] for name in AUDIT_FIELDS})


_EXCERPT = Excerpt(observation_key=OBSERVATION_KEY, span=TextSpan(0, 19),
                   reason="the heading names the course")
_SENSITIVE_EXCERPT = Excerpt(observation_key=SENSITIVE_KEY, span=TextSpan(0, 32),
                             reason="the clause naming the account holder")
_WHOLE_UNIT = Excerpt(observation_key=OBSERVATION_KEY, span=TextSpan(0, 4096),
                      reason="the whole page")
_IDENTIFIER = RedactedIdentifier(observation_key=SENSITIVE_KEY, span=TextSpan(4, 20),
                                 identifier_class="fixture-identifier-class")
_LABEL = CandidateLabel(label="BUSIB 4300")
_METADATA = MetadataField(name="page_count")
_EVIDENCE = EvidenceReference(evidence_id=OBSERVATION_KEY)
_FILENAME = Filename(file_id=FIXTURE_FILE_ID)
_GPS = MetadataField(name="gps")


def _denied(reason: str, explanation: str, remedy: str,
            evidence_refs: Sequence[str] = ()) -> Denied:
    return deny(reason, explanation=explanation,
                remedy_options=(RemedyOption(remedy),),
                evidence_refs=tuple(evidence_refs))


# --- the sixteen -------------------------------------------------------------

FIXTURES: tuple[GateFixture, ...] = (
    GateFixture(
        number=1,
        spec_case="protected file + cloud target under `hybrid` -- §8.4's "
                  "\"Sensitive files remain local\"",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "protected_cloud_target",
            "This file is protected, and `hybrid` keeps sensitive files local.",
            "Run this call against a local model, or grant cloud use for this area.",
            evidence_refs=(OBSERVATION_KEY,)),
        audit_record=_audit(file_sensitivity="sensitive_personal",
                            operation_mode="hybrid"),
        policy=_policy("hybrid"),
        classification=_classification("sensitive_personal", protected=True,
                                       basis="detector"),
    ),
    GateFixture(
        number=2,
        spec_case="a file with no classification -- and never a silent `public_low`",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "unclassified",
            "Nothing has classified this file, and §8.4 makes classification a "
            "precondition of escalation.",
            "Classify the file, or review it manually."),
        audit_record=_audit(operation_mode="hybrid"),
        policy=_policy("hybrid"),
        classification=None,
    ),
    GateFixture(
        number=3,
        spec_case="a revoked policy",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "policy_revoked",
            "The consent that authorized cloud use for this area has been revoked.",
            "Grant consent again, or run this call against a local model."),
        audit_record=_audit(file_sensitivity="public_low",
                            operation_mode="cloud_assisted"),
        policy=_policy("cloud_assisted"),
        classification=_classification("public_low", protected=False),
    ),
    GateFixture(
        number=4,
        spec_case="a `Protected Records` residual file, excerpt requested -- §7.3 "
                  "forbids filenames AND content",
        request=_request(stage="residual", model_target=CLOUD,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "protected_records_template",
            f"{PROTECTED_RECORDS_TEMPLATE} material must not have its filenames or "
            "content exposed in model prompts (§7.3).",
            "Review this file locally."),
        audit_record=_audit(file_sensitivity="highly_sensitive_credential_bearing",
                            operation_mode="cloud_assisted", stage="residual",
                            prompt_fingerprint="fingerprint.residual"),
        policy=_policy("cloud_assisted",
                       grants=((IDENTITY, "cloud_model"),)),
        classification=_classification("highly_sensitive_credential_bearing",
                                       protected=True),
    ),
    GateFixture(
        number=5,
        spec_case="an excerpt whose span covers the whole text unit",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_WHOLE_UNIT,)),
        decision=_denied(
            "whole_document_requested",
            "§8.4: do not send full documents where a short heading or OCR excerpt "
            "is enough to resolve the question.",
            "Request the heading span instead."),
        audit_record=_audit(file_sensitivity="public_low", operation_mode="hybrid"),
        policy=_policy("hybrid"),
        classification=_classification("public_low", protected=False),
    ),
    GateFixture(
        number=6,
        spec_case="a request declaring a budget above the configured ceiling",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT,),
                         max_dossier_tokens=FIXTURE_OVER_BUDGET),
        decision=_denied(
            "dossier_over_budget",
            "The declared dossier budget exceeds "
            "`model.max_dossier_tokens_per_call`.",
            "Run §8.6's reduction ladder before calling: summarize deterministic "
            "facts, preserve anchor excerpts, split the task, or defer the decision."),
        audit_record=_audit(file_sensitivity="public_low", operation_mode="hybrid"),
        policy=_policy("hybrid"),
        classification=_classification("public_low", protected=False),
        p8_obligation=(
            "This fixture exists so P8 can prove its ladder ran first. A P8 test that "
            "reaches this denial through the normal path is a P8 failure, not a gate "
            "result (M9)."),
    ),
    GateFixture(
        number=7,
        spec_case="GPS requested as a releasable item -- §8.4's always-local set",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_GPS,)),
        decision=_denied(
            "always_local_item",
            "GPS is in §8.4's always-local set and is not releasable by any mode.",
            "Request a non-sensitive metadata field instead."),
        audit_record=_audit(file_sensitivity="public_low", operation_mode="hybrid"),
        policy=_policy("hybrid"),
        classification=_classification("public_low", protected=False),
    ),
    GateFixture(
        number=8,
        spec_case="a non-protected file + cloud target under `offline`",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "mode_forbids_target",
            "`offline`: no content leaves the device; only local rules and local "
            "models may run.",
            "Switch to a local model, or change the operation mode."),
        audit_record=_audit(file_sensitivity="public_low",
                            operation_mode="offline"),
        policy=_policy("offline"),
        classification=_classification("public_low", protected=False),
    ),
    GateFixture(
        number=9,
        spec_case="a clean `Released` with redaction applied",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT, _IDENTIFIER, _LABEL, _METADATA,
                                          _EVIDENCE)),
        decision=Released(
            release_id="", audit_id=None, policy_version="",
            materialised_items=(), redaction_manifest=(), model_target=CLOUD),
        audit_record=_audit(
            outcome="released", file_sensitivity="personal_non_sensitive",
            operation_mode="cloud_assisted", redaction_applied=True,
            excerpts_included=((OBSERVATION_KEY, "0-19"),
                               (SENSITIVE_KEY, "4-20"))),
        policy=_policy("cloud_assisted", grants=((ACADEMICS, "cloud_model"),)),
        classification=_classification("personal_non_sensitive", protected=False),
    ),
    GateFixture(
        number=10,
        spec_case="a dossier requiring sensitive text -- `NeedsConsent`, four options",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_SENSITIVE_EXCERPT,)),
        decision=NeedsConsent(
            consent_request_id="",
            requirement="The dossier needs text from a sensitive-personal file.",
            options=tuple(CONSENT_OPTIONS)),
        audit_record=_audit(
            outcome="consent_requested", file_sensitivity="sensitive_personal",
            operation_mode="hybrid"),
        policy=_policy("hybrid", grants=((ACADEMICS, "cloud_model"),)),
        classification=_classification("sensitive_personal", protected=False),
        p8_obligation=(
            "This fixture exists so P8 can prove it returns the branch to its caller "
            "intact, with all four options, rather than folding it into `abstain` "
            "(B2)."),
    ),
    GateFixture(
        number=11,
        spec_case="a protected file + cloud target under `offline`",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "mode_forbids_target",
            "`offline`: no content leaves the device.",
            "Switch to a local model."),
        audit_record=_audit(file_sensitivity="sensitive_personal",
                            operation_mode="offline"),
        policy=_policy("offline"),
        classification=_classification("sensitive_personal", protected=True),
    ),
    GateFixture(
        number=12,
        spec_case="a protected file + cloud target under `local_model`",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "mode_forbids_target",
            "`local_model`: local extraction plus a user-installed local LLM; a cloud "
            "target is not eligible.",
            "Switch to the installed local model."),
        audit_record=_audit(file_sensitivity="sensitive_personal",
                            operation_mode="local_model"),
        policy=_policy("local_model"),
        classification=_classification("sensitive_personal", protected=True),
    ),
    GateFixture(
        number=13,
        spec_case="a protected file + cloud target under `cloud_assisted` with no "
                  "grant for that area",
        request=_request(stage="grouping", model_target=CLOUD,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "protected_cloud_target",
            "This file is protected, and no consent grant covers this area.",
            "Grant cloud use for this area, or run against a local model."),
        audit_record=_audit(file_sensitivity="sensitive_personal",
                            operation_mode="cloud_assisted"),
        policy=_policy("cloud_assisted"),
        classification=_classification("sensitive_personal", protected=True),
    ),
    GateFixture(
        number=14,
        spec_case="an `unreadable_unclassified` file + LOCAL target under "
                  "`local_model`, with `unclassified_permits_local = False` "
                  "(Open question 5, branch one)",
        request=_request(stage="grouping", model_target=LOCAL,
                         requested_items=(_EXCERPT,)),
        decision=_denied(
            "unclassified",
            "Nothing has classified this file, and this caller does not permit local "
            "calls on unclassified files.",
            "Classify the file, or permit local calls on unclassified files."),
        audit_record=_audit(
            operation_mode="local_model",
            model={"locality": "local", "model_id": "llama-local",
                   "provider": None}),
        policy=_policy("local_model"),
        classification=None,
    ),
    GateFixture(
        number=15,
        spec_case="an `unreadable_unclassified` file + LOCAL target under "
                  "`local_model`, with `unclassified_permits_local = True` "
                  "(Open question 5, branch two)",
        request=_request(stage="grouping", model_target=LOCAL,
                         requested_items=(_EXCERPT,)),
        decision=Released(
            release_id="", audit_id=None, policy_version="",
            materialised_items=(), redaction_manifest=(), model_target=LOCAL),
        audit_record=_audit(
            outcome="released", operation_mode="local_model",
            excerpts_included=((OBSERVATION_KEY, "0-19"),),
            model={"locality": "local", "model_id": "llama-local",
                   "provider": None}),
        policy=_policy("local_model"),
        classification=None,
    ),
    GateFixture(
        number=16,
        spec_case="a `Protected Records` residual request for the FILENAME -- "
                  "NEEDS-JOSEPH B5d / C9a, unresolved either way",
        request=_request(stage="residual", model_target=CLOUD,
                         requested_items=(_FILENAME,)),
        decision=_denied(
            "protected_records_template",
            f"{PROTECTED_RECORDS_TEMPLATE} material must not cause filenames or "
            "content to be exposed in model prompts (§7.3).",
            "Review this file locally."),
        audit_record=_audit(file_sensitivity="highly_sensitive_credential_bearing",
                            operation_mode="cloud_assisted", stage="residual",
                            prompt_fingerprint="fingerprint.residual"),
        policy=_policy("cloud_assisted", grants=((IDENTITY, "cloud_model"),)),
        classification=_classification("highly_sensitive_credential_bearing",
                                       protected=True),
    ),
)


FIXTURE_COVERAGE: Mapping[str, tuple[int, ...]] = MappingProxyType({
    "protected_cloud_target": (1, 13),
    "unclassified": (2, 14),
    "policy_revoked": (3,),
    "protected_records_template": (4, 16),
    "whole_document_requested": (5,),
    "dossier_over_budget": (6,),
    "always_local_item": (7,),
    "mode_forbids_target": (8, 11, 12),
    "a clean `Released` with redaction applied": (9,),
    "a `NeedsConsent` returning all four options": (10,),
    # In OPERATION_MODES order: offline, local_model, hybrid, cloud_assisted.
    "a protected file under each of the four modes": (11, 12, 1, 13),
    "an `unreadable_unclassified` file": (2, 14, 15),
    "a `Protected Records` residual request": (4, 16),
})
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_fixtures.py -v`
Expected: PASS — 68 passed (the three replay tests are parametrised over sixteen fixtures).

- [ ] **Step 5: Commit**

```bash
git add src/privacy/fixtures.py tests/p7/test_p7_fixtures.py
git commit -m "feat(P7): SPEC 11's sixteen fixtures, each replayed through the real gate"
```

---
### Task 21: The no-invention guard, and every open question held open

**Files:**
- Test: `tests/p7/test_p7_no_invention.py`

**Interfaces:**
- Consumes: every module under `src/privacy/`, by `importlib` + `vars(module)`; every package under
  `src/`, for the repo-wide layer-L2 guard; `privacy.vocabulary.OPEN_QUESTIONS`, `.NEEDS_JOSEPH`.
- Produces: nothing. This is the standing guard the rest of the build must keep green.

**Done-means:** the guard behind 1, 12, and the whole *Deferred* table.

**Two names Task 2 must publish that its `Produces` block omits.** `OPEN_QUESTIONS: Mapping[int, str]`
is named in the skeleton's Task 21 `Interfaces` block and nowhere in Task 2's `Produces`. And the two
items that must be held open **by name** are not among SPEC Open questions 1–11 as numbered, so they
need a second mapping: `NEEDS_JOSEPH: Mapping[str, str]`, keyed `"B5d/C9a"` and `"C5"`. Reported.

- **B5d / C9a — `filename` as a sixth releasable kind.** §8.4 permits *"selected excerpts, redacted
  identifiers, candidate labels, non-sensitive metadata, and evidence references"* — five — and puts
  *"Paths"* in the always-local set. P7's SPEC adds a sixth under its own flagged reading, and flags
  it: *"the design wins and the design does not name it."* It is Joseph's call and stays open.
- **C5 — does P6 keep a `sensitivity status` field row beside P7's authoritative record?** D2
  answered *which record is authoritative* and did not answer this. P7's own SPEC Contract-in pulls
  the other way, verbatim: *"**P6 must accept `sensitivity` as a first-class universal field**
  (§3.11) rather than a domain-scoped one"*, while D2 makes `ClassificationRecord` authoritative.
  Until it is answered, P6 creates no such row and P7 reads none.

**One guard INVERTS, and this is the reason to read this task before running it.** The skeleton's
Task 21 says P6 OQ11 stays open. **D2 closed it**, so a guard asserting it is open fails the day this
plan is executed. Replaced with a guard on the D2 shape: `ClassificationRecord` keyed
`(file_id, content_hash)` is authoritative, `files.sensitivity_state` is a projection written through
P1's published `set_sensitivity_state`, `src/privacy/` issues **no `UPDATE files`** of its own, and
`unclassified` never reaches that column.

**The refusal-import guard is now THREE names, not two.** `ProtectedContainerRefused` and
`DatalessRefused` live in `extractors.safety`; `ContractViolation` lives in `extractors.failure`
(`src/extractors/failure.py:25`). The three refusals stay three, and P7's is the third
(22-p1-p7-connection-contract.md §2). Verified against the live modules.

**The repo-wide L2 set in the skeleton is wrong in both directions, and the guard states the truth.**
The skeleton says the packages binding a P4 text materialiser are `{evidence_shape, extractors,
privacy}`. Introspected 2026-08-22 over every module under `src/`:

```text
evidence_shape.store        text_units_for_run, text_unit_at, unit_for_observation
evidence_shape.text_units   raw_value_at
orchestrator                text_units_for_run
```

`extractors` binds **none** of them, and `orchestrator` binds one — `src/orchestrator.py` copies text
units into P2's sealed replay bundle, which is a local, non-model use. So the true set today is
`{evidence_shape, orchestrator}`, becoming `{evidence_shape, orchestrator, privacy}` when Task 9's
`resolve.py` lands. The guard asserts that set with the reason for each member written down, because
a guard listing a package that binds nothing would pass forever without checking anything.
**Reported.**

**Every guard is runtime introspection.** A source-text guard matches its own comments and the design
quotations in its docstrings — this file's own prose names `hybrid`, `cloud_assisted`, `passport` and
a retention period, all of which are design quotations. Where a token assertion is unavoidable — the
SQL guard — it walks the AST and excludes docstrings, the mechanism `code_tokens()` establishes in
`tests/p3/test_p3_no_invention.py`.

**The numeric allowlist has exactly one module and exactly two names.** `privacy.fixtures`,
`FIXTURE_CEILING` and `FIXTURE_OVER_BUDGET`, both fixture data for a comparison, both installed
through P1's `budget.set_ceiling` by the test that uses them. Every other module under `src/privacy/`
holds no number at all — one assertion covering the SPEC's numeric-ceiling Deferred row, every
threshold, every retention period and every confidence cutoff, and it cannot be satisfied by a
rename.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_no_invention.py
"""The standing record that P7 answers no open question in code.

Every guard is RUNTIME INTROSPECTION. A source-text guard matches its own docstrings --
this file's prose names `hybrid`, `cloud_assisted`, `passport` and a retention period,
all of which are design quotations -- so nothing here reads a `.py` file except the one
SQL guard, which parses and skips docstrings the way `code_tokens()` does in tests/p3.
"""
import ast
import importlib
import inspect
import re
from pathlib import Path

import pytest

import privacy
from database_agent.files_table import set_sensitivity_state

from privacy.classification import ClassificationRecord
from privacy.classification_store import mirror_state
from privacy.defaults import LOCAL_FIRST_MODES, MORE_REDACTING
from privacy.moves import may_move_automatically
from privacy.revocation import DeleteDerivedRefused, DerivedScope, delete_derived
from privacy.vocabulary import (
    ALWAYS_LOCAL, DISPLAY_FACETS, HANDLING_CLASSES, ITEM_KINDS, NEEDS_JOSEPH,
    OPEN_QUESTIONS, OPERATION_MODES,
)

SOURCE_DIR = Path(privacy.__file__).parent
SRC_DIR = SOURCE_DIR.parent

#: The one module allowed to hold a number, and the only two names it may hold.
NUMERIC_ALLOWLIST = {"privacy.fixtures": {"FIXTURE_CEILING", "FIXTURE_OVER_BUDGET"}}

SQL_WRITE = re.compile(r"\b(INSERT|UPDATE|DELETE|REPLACE)\b", re.IGNORECASE)
TABLE_AFTER_WRITE = re.compile(
    r"\b(?:INSERT\s+(?:OR\s+\w+\s+)?INTO|UPDATE|DELETE\s+FROM|REPLACE\s+INTO)\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)


def p7_modules():
    return [importlib.import_module(f"privacy.{path.stem}")
            for path in sorted(SOURCE_DIR.glob("*.py")) if path.stem != "__init__"]


def constants(module):
    """Module-level names and values, minus dunders -- which is where `__doc__` is."""
    return {name: value for name, value in vars(module).items()
            if not name.startswith("__")}


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from strings(item)
    elif hasattr(value, "items"):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)


def module_strings():
    for module in p7_modules():
        for name, value in constants(module).items():
            if inspect.isclass(value) or inspect.isfunction(value) \
                    or inspect.ismodule(value):
                continue
            for text in strings(value):
                yield module.__name__, name, text


def code_string_literals():
    """String literals P7's code HOLDS, docstrings excluded (the tests/p3 mechanism)."""
    for path in sorted(SOURCE_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        skip = set()
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)) and body \
                    and isinstance(body[0], ast.Expr) \
                    and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                skip.add(id(body[0].value))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and id(node) not in skip \
                    and isinstance(node.value, str):
                yield path.name, node.value


def src_modules():
    for path in sorted(SRC_DIR.rglob("*.py")):
        relative = path.relative_to(SRC_DIR)
        name = (".".join(relative.parent.parts) if relative.name == "__init__.py"
                else ".".join(relative.with_suffix("").parts))
        if name:
            yield importlib.import_module(name)


# --- the value guards -------------------------------------------------------

def test_only_the_allowlisted_module_holds_a_number():
    # One assertion for the SPEC's numeric Deferred row, every threshold, every
    # retention period and every confidence cutoff. It cannot be satisfied by a rename.
    for module in p7_modules():
        allowed = NUMERIC_ALLOWLIST.get(module.__name__, set())
        for name, value in constants(module).items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                assert name in allowed, f"{module.__name__}.{name} = {value!r}"


def test_p7_holds_no_regex_anywhere():
    # SPEC Deferred: the detection rules, the gazetteer contents and the identifier
    # patterns are all hand-authored elsewhere. "src/privacy/ contains no regex, no
    # gazetteer, no filename pattern, no keyword list."
    for module in p7_modules():
        for name, value in constants(module).items():
            assert not isinstance(value, re.Pattern), f"{module.__name__}.{name}"
            assert getattr(value, "__name__", "") != "re", f"{module.__name__}.{name}"


def test_p7_enumerates_no_identifier_class():
    # SPEC Deferred: "`redaction_manifest` carries the class as an opaque string until
    # this is authored." The one class string in the package is the FIXTURE's, and it
    # says so in its own value.
    classes = [(module_name, name, text) for module_name, name, text
               in module_strings() if "identifier_class" in name.lower()]
    for module_name, name, text in classes:
        assert module_name == "privacy.fixtures", f"{module_name}.{name}"
    for module_name, name, text in module_strings():
        for token in ("passport", "ssn", "social_security", "iban", "credit_card",
                      "national_id", "tax_id", "account_number"):
            assert token not in text.lower(), f"{module_name}.{name} = {text!r}"


def test_the_classifier_and_the_transform_are_injected_with_no_default():
    # SPEC Deferred: two injected protocols, no default, so a build that forgets to
    # wire one cannot silently emit unredacted values.
    from privacy.redaction import apply_redaction
    parameters = inspect.signature(apply_redaction).parameters
    for name in ("classifier", "transform"):
        assert parameters[name].default is inspect.Parameter.empty, name
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY, name


def test_p7_states_no_retention_period():
    # OQ10: "How long audit records, consent grants, and superseded classifications
    # are kept. The design states no retention period anywhere."
    for module in p7_modules():
        for name in constants(module):
            for token in ("retention", "expire", "expiry", "ttl", "purge",
                          "max_age", "keep_for"):
                assert token not in name.lower(), f"{module.__name__}.{name}"
    for module in p7_modules():
        for name, value in constants(module).items():
            assert getattr(value, "__name__", "") not in ("timedelta",), name


def test_p7_defines_no_corpus_area():
    # OQ3: "What is a 'corpus area'? ... Consent grants cannot be scoped until this is
    # named." Every scope is a caller-supplied resolver with no default.
    from privacy.display import summarize_protected
    from privacy.revocation import revoke
    for function, name in ((may_move_automatically, "scope_for"),
                           (summarize_protected, "files_in_scope"),
                           (revoke, "files_in_scope")):
        parameter = inspect.signature(function).parameters[name]
        assert parameter.default is inspect.Parameter.empty, function.__name__
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, function.__name__
    for module_name, name, text in module_strings():
        for token in ("scan_root", "corpus_area", "Academics", "Finance"):
            if module_name == "privacy.fixtures":
                continue                          # fixture data, named as such
            assert token not in text, f"{module_name}.{name} = {text!r}"


def test_p7_makes_no_detection_decision():
    # SPEC Deferred: "The design states *what* is protected and never *how it is
    # recognised*." No function in the package decides that a file carries something.
    for module in p7_modules():
        for name, value in constants(module).items():
            if not callable(value):
                continue
            for token in ("detect", "recognize", "recognise", "sniff", "match_rule",
                          "score_sensitivity", "looks_like"):
                assert token not in name.lower(), f"{module.__name__}.{name}"


# --- one guard per open question --------------------------------------------

def test_all_eleven_open_questions_are_present_with_their_spec_text():
    assert set(OPEN_QUESTIONS) == set(range(1, 12))
    for number, text in OPEN_QUESTIONS.items():
        assert isinstance(text, str) and len(text) > 40, number


def test_oq1_protected_is_never_inferred_from_the_handling_class():
    # OQ1: "§8.4 lists five classes and, separately, five kinds of material that
    # 'enter a protected state immediately', without stating the relation."
    assert "protected" in OPEN_QUESTIONS[1].lower()
    record = ClassificationRecord(
        file_id="f", content_hash="sha256:abc", handling_class="public_low",
        protected=True, basis="user", evidence_refs=(),
        reliability_state="user_confirmed", observed_at="2026-08-22T12:00:00+00:00")
    assert record.protected is True
    # No module derives one from the other: a mapping from class to flag would be a
    # module-level container whose keys are handling classes and whose values are bools.
    for module in p7_modules():
        for name, value in constants(module).items():
            if hasattr(value, "items") and set(value) & set(HANDLING_CLASSES):
                assert not all(isinstance(v, bool) for v in value.values()), \
                    f"{module.__name__}.{name} maps handling classes to a flag"


def test_oq2_and_b5d_the_sixth_releasable_kind_stays_flagged():
    # §8.4 names FIVE releasable kinds and puts "Paths" in the always-local set; P7's
    # SPEC adds `filename` as a sixth under its own flagged reading. NEEDS-JOSEPH
    # B5d/C9a: "Recorded; the design wins. The SPEC flags it itself. Your call."
    assert len(ITEM_KINDS) == 6
    assert "filename" in ITEM_KINDS
    assert "paths" in ALWAYS_LOCAL
    assert "filename" in OPEN_QUESTIONS[2].lower() or "path" in OPEN_QUESTIONS[2].lower()
    held = NEEDS_JOSEPH["B5d/C9a"]
    assert "filename" in held and "five" in held


def test_oq3_is_present_and_unanswered():
    assert "corpus area" in OPEN_QUESTIONS[3].lower()


def test_oq4_and_i6_deletion_versus_append_only_stays_unbuilt():
    # OQ4 / I6. D3 ratified the direction and built nothing; the surface refuses.
    assert "delete" in OPEN_QUESTIONS[4].lower()
    with pytest.raises(DeleteDerivedRefused):
        delete_derived(DerivedScope("text_units", "text"))
    with pytest.raises(DeleteDerivedRefused):
        delete_derived(DerivedScope("events", "explanation"))


def test_oq5_the_unclassified_local_call_parameter_has_no_default():
    # OQ5: "Does `unreadable_unclassified` permit a *local* model call? ... Reading
    # escalation strictly denies local calls on unclassified files, which may block
    # exactly the OCR-opaque screenshots §2.7 and §7.8 want a model to interpret."
    from privacy.gate import Gate
    parameter = inspect.signature(Gate.__init__).parameters[
        "unclassified_permits_local"]
    assert parameter.default is inspect.Parameter.empty
    assert "local" in OPEN_QUESTIONS[5].lower()


def test_oq6_no_local_call_threshold_exists():
    # OQ6: "The threshold at which a local call needs a prompt is unstated."
    assert "local" in OPEN_QUESTIONS[6].lower()
    for module in p7_modules():
        for name in constants(module):
            assert "threshold" not in name.lower(), f"{module.__name__}.{name}"


def test_oq7_reclassification_does_not_generalize():
    # OQ7. Task 16 keeps `file` scope and generalizes never; nothing counts repetitions.
    from privacy.learning_seam import FILE_SCOPE, reclassify
    assert FILE_SCOPE == "file"
    assert inspect.signature(reclassify).parameters[
        "correction_scope"].default == FILE_SCOPE
    for module in p7_modules():
        for name in constants(module):
            for token in ("generalize", "generalise", "promote", "floor",
                          "repeat_count"):
                assert token not in name.lower(), f"{module.__name__}.{name}"


def test_oq8_p7_writes_nothing_into_a_replay_bundle():
    # OQ8: "May a replay bundle carry audit records and excerpt spans?" P7 never
    # reaches the bundle, which is also why `bundle_file_entry.handling_class` is the
    # Wave-2 caller's field and not P7's (22-p1-p7-connection-contract.md §1).
    import eval_harness.bundle as bundle
    writers = {name for name, value in vars(bundle).items()
               if callable(value) and (name.startswith("add_")
                                       or name in ("open_bundle", "seal_bundle"))}
    for module in p7_modules():
        assert not (set(constants(module)) & writers), module.__name__


def test_oq9_model_target_locality_has_exactly_two_values():
    # OQ9: "What is an 'external connector' besides a model?" `ModelTarget.locality`
    # is `local | cloud` and there is no third value. Asserted over the module-level
    # containers rather than over the dataclass, because a third value would arrive as
    # a widened vocabulary tuple before it arrived as a field.
    for module in p7_modules():
        for name, value in constants(module).items():
            if isinstance(value, tuple) and set(value) & {"local", "cloud"}:
                assert set(value) == {"local", "cloud"}, f"{module.__name__}.{name}"
    assert "connector" in OPEN_QUESTIONS[9].lower()


def test_oq10_retention_is_present_and_unanswered():
    assert "retention" in OPEN_QUESTIONS[10].lower()


def test_oq11_names_no_winner_between_the_two_local_modes():
    # W1: "What remains genuinely open is only WHICH OF THOSE TWO ships." Task 6
    # asserts the floor and refuses to name the winner.
    assert set(LOCAL_FIRST_MODES) == {"offline", "local_model"}
    assert len(LOCAL_FIRST_MODES) == 2
    for module in p7_modules():
        for name, value in constants(module).items():
            if not isinstance(value, str):
                continue
            if value in ("offline", "local_model"):
                assert "DEFAULT" not in name.upper(), f"{module.__name__}.{name}"
    assert set(MORE_REDACTING) == set(DISPLAY_FACETS)
    assert set(MORE_REDACTING.values()) == {"redacted"}


def test_no_module_holds_a_default_operation_mode():
    # The negative half of Done-means 12, by introspection rather than by grep: both
    # `hybrid` and `cloud_assisted` appear legitimately in `vocabulary.py`, in
    # MODE_SEMANTICS, in docstrings and in denial messages, so a grep either passes
    # vacuously or fails on a comment.
    for module in p7_modules():
        for name, value in constants(module).items():
            if isinstance(value, str) and value in OPERATION_MODES:
                assert module.__name__ in ("privacy.vocabulary", "privacy.defaults",
                                           "privacy.fixtures"), \
                    f"{module.__name__}.{name} = {value!r}"
            if "DEFAULT_MODE" in name.upper():
                pytest.fail(f"{module.__name__}.{name}")


# --- the D2 shape (this guard REPLACES the P6 OQ11 guard) -------------------

def test_d2_the_classification_record_is_the_authoritative_one(p7_conn):
    # D2, ratified 2026-08-21: "P7's `ClassificationRecord`, keyed
    # (file_id, content_hash), is authoritative." Keyed on the hash because a
    # classification is about BYTES.
    fields = {field.name for field in
              __import__("dataclasses").fields(ClassificationRecord)}
    assert {"file_id", "content_hash"} <= fields


def test_d2_p6_oq11_is_closed_and_p7_no_longer_holds_it_open():
    # The inverted guard. An entry asserting OQ11 open would fail the day D2 was
    # applied, which is the day this plan is executed.
    for text in OPEN_QUESTIONS.values():
        assert "one record or three" not in text.lower()
    assert "C5" in NEEDS_JOSEPH
    assert "sensitivity status" in NEEDS_JOSEPH["C5"].lower()


def test_d2_privacy_issues_no_write_against_a_table_it_does_not_own(p7_conn):
    # The projection goes through P1's published setter. Asserted over CODE string
    # literals -- the AST walk, docstrings excluded -- because this is the one
    # assertion of the form "this token appears nowhere" that cannot be made by
    # introspecting a namespace.
    from privacy.schema import create_privacy_schema

    before = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    create_privacy_schema(p7_conn)
    after = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    p7_tables = after - before
    assert p7_tables, "create_privacy_schema created no table"

    for filename, text in code_string_literals():
        if not SQL_WRITE.search(text):
            continue
        for table in TABLE_AFTER_WRITE.findall(text):
            assert table in p7_tables, f"{filename}: writes to {table!r}"


def test_d2_the_setter_p7_calls_is_p1s(p7_conn):
    import privacy.learning_seam as seam
    assert seam.set_sensitivity_state is set_sensitivity_state


def test_d2_unclassified_never_reaches_the_column():
    # "Unreadable or unclassified is a GATE OUTCOME, not a file fact. It lives on the
    # release decision and never in that column, so 'nothing has looked' can never be
    # read as 'this file carries nothing'."
    record = ClassificationRecord(
        file_id="f", content_hash="sha256:abc",
        handling_class="unreadable_unclassified", protected=False, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at="2026-08-22T12:00:00+00:00")
    with pytest.raises(ValueError):
        mirror_state(record)


# --- the three refusals stay three ------------------------------------------

def test_privacy_imports_none_of_extractors_refusals():
    # 22-p1-p7-connection-contract.md §2: "that list is now three names". P7's gate
    # refuses RELEASE; P3/P5 refuse READING and MATERIALIZING, and a file that failed
    # either never acquires the (file_id, content_hash) pair P7 keys on.
    from extractors.failure import ContractViolation
    from extractors.safety import DatalessRefused, ProtectedContainerRefused
    forbidden = (ProtectedContainerRefused, DatalessRefused, ContractViolation)
    for module in p7_modules():
        for name, value in constants(module).items():
            assert value not in forbidden, f"{module.__name__}.{name}"


def test_privacy_never_calls_the_upstream_safety_gate():
    import extractors.safety as safety
    for module in p7_modules():
        for name, value in constants(module).items():
            assert value is not safety.admit, f"{module.__name__}.{name}"
            assert value is not safety, f"{module.__name__}.{name}"


def test_the_denial_vocabulary_holds_no_bare_protected():
    from privacy.vocabulary import DENIAL_REASONS
    assert "protected" not in DENIAL_REASONS
    assert "protected_cloud_target" in DENIAL_REASONS
    assert "protected_records_template" in DENIAL_REASONS


# --- authorship -------------------------------------------------------------

def test_subsystem_is_set_in_exactly_one_module():
    # M8: the acting part authors and P1 writes. There is one place that value lives.
    from privacy.authorship import SUBSYSTEM
    holders = [module.__name__ for module in p7_modules()
               if constants(module).get("SUBSYSTEM") == SUBSYSTEM
               and module.__name__ != "privacy.authorship"]
    assert holders == []
    assert SUBSYSTEM == "P7"


def test_p7_registers_no_event_type():
    # B5 rule 4: registration is a spec-level act. P7's eight are already in P1's
    # frozen table; Task 1 asserts they are there and adds nothing.
    from database_agent.events import REGISTERED_EVENT_TYPES
    from privacy.authorship import P7_EVENT_TYPES
    assert set(P7_EVENT_TYPES) <= set(REGISTERED_EVENT_TYPES)
    for module in p7_modules():
        for name, value in constants(module).items():
            assert value is not REGISTERED_EVENT_TYPES or \
                module.__name__ == "privacy.authorship", f"{module.__name__}.{name}"


# --- layer L2, repo-wide ----------------------------------------------------

def test_exactly_one_module_under_privacy_binds_a_p4_text_materialiser():
    from evidence_shape.store import (
        text_unit_at, text_units_for_run, unit_for_observation,
    )
    from evidence_shape.text_units import raw_value_at
    materialisers = (raw_value_at, text_units_for_run, text_unit_at,
                     unit_for_observation)
    binding = [module.__name__ for module in p7_modules()
               if any(value is materialiser
                      for value in constants(module).values()
                      for materialiser in materialisers)]
    assert binding == ["privacy.resolve"]


def test_the_repo_wide_set_of_binding_packages_is_the_named_three():
    """Layer L2. The SKELETON's set was wrong in both directions and this is the
    measured one.

    `evidence_shape` defines them. `orchestrator` binds `text_units_for_run` to copy
    text units into P2's sealed replay bundle -- a local, non-model use, and naming it
    is better than a guard that silently omits it. `privacy.resolve` is the gate's one
    materialisation locus. `extractors` binds NONE, which is why the skeleton's list
    would have passed forever without checking anything.

    This guard passes trivially today and becomes load-bearing the moment P8 lands.
    """
    from evidence_shape.store import (
        text_unit_at, text_units_for_run, unit_for_observation,
    )
    from evidence_shape.text_units import raw_value_at
    materialisers = (raw_value_at, text_units_for_run, text_unit_at,
                     unit_for_observation)
    packages = set()
    for module in src_modules():
        if any(value is materialiser for value in vars(module).values()
               for materialiser in materialisers):
            packages.add(module.__name__.split(".")[0])
    assert packages == {"evidence_shape", "orchestrator", "privacy"}


def test_release_is_the_only_module_that_imports_resolve():
    import privacy.resolve as resolve
    binding = [module.__name__ for module in p7_modules()
               if any(value is resolve for value in constants(module).values())]
    assert binding == ["privacy.release"]
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_no_invention.py -v`
Expected: FAIL — collection succeeds and any guard whose forbidden value is present fails. If every
prior task was written as specified, the only expected failures are `OPEN_QUESTIONS` and
`NEEDS_JOSEPH` not existing on `privacy.vocabulary`, which is what Step 3 adds.

- [ ] **Step 3: Add `OPEN_QUESTIONS` and `NEEDS_JOSEPH` to `src/privacy/vocabulary.py`**

The two mappings append to Task 2's module; nothing already in it changes.

```python
# src/privacy/vocabulary.py
from types import MappingProxyType

#: SPEC *Open questions*, quoted. Task 21 holds each one open by name and fails the
#: moment someone answers one in an implementation instead of in a SPEC.
OPEN_QUESTIONS: Mapping[int, str] = MappingProxyType({
    1: "Is `protected` exactly the top two handling classes? §8.4 lists five classes "
       "and, separately, five kinds of material that 'enter a protected state "
       "immediately', without stating the relation.",
    2: "Filename vs. path. §8.4 puts paths in the always-local set; §7.7 puts the "
       "filename in the residual dossier; §7.3 forbids filenames in prompts only for "
       "Protected Records. This contract adopts the reading that makes §7.3 "
       "non-vacuous and flags it.",
    3: "What is a 'corpus area'? `cloud_assisted` permits a cloud model for 'selected "
       "corpus areas' (§8.4). A scan root, a frozen tree node, an accepted group, a "
       "domain? Consent grants cannot be scoped until this is named.",
    4: "Deletion versus append-only. §8.4 gives the user the right to 'review and "
       "delete local derived data'; §8.2 requires an append-only provenance log. "
       "Which wins, what counts as 'derived', and are audit records themselves "
       "deletable?",
    5: "Does `unreadable_unclassified` permit a local model call? Reading escalation "
       "strictly denies local calls on unclassified files, which may block exactly "
       "the OCR-opaque screenshots §2.7 and §7.8 want a model to interpret.",
    6: "Is a local-model call a consent event or only an audit event? The threshold "
       "at which a local call needs a prompt is unstated.",
    7: "Does repeated reclassification generalize? §8.7 allows a repeated residual "
       "destination to become a corpus-level preference; it does not say whether "
       "repeated privacy corrections may raise a sensitivity floor.",
    8: "May a replay bundle carry audit records and excerpt spans? Whether a bundle "
       "intended to leave the user's machine may carry audit records -- which name "
       "excerpts -- is unstated.",
    9: "What is an 'external connector' besides a model? §8.4 gates 'any model or "
       "external connector', but no non-model connector is named in the twelve parts. "
       "If a connector is added later, does it route through `Gate.release`?",
    10: "Retention. How long audit records, consent grants, and superseded "
        "classifications are kept. The design states no retention period anywhere.",
    11: "The local-first default -- narrowed, not open-ended (W1). What remains "
        "genuinely open is only which of those two ships, which turns on whether a "
        "local model is assumed present.",
})

#: The two questions that are open by NAME rather than by number, from
#: `planning/overnight/NEEDS-JOSEPH.md`. Neither is one of SPEC's eleven and both are
#: Joseph's call.
NEEDS_JOSEPH: Mapping[str, str] = MappingProxyType({
    "B5d/C9a":
        "`filename` as a releasable kind. §8.4's releasable list is five -- 'selected "
        "excerpts, redacted identifiers, candidate labels, non-sensitive metadata, "
        "and evidence references' -- and puts Paths in the always-local set. The SPEC "
        "adds a sixth under its own flagged reading. Recorded; the design wins; the "
        "SPEC flags it itself. Joseph's call.",
    "C5":
        "Does P6 keep a `sensitivity status` field row beside P7's authoritative "
        "record? D2 answered which record is authoritative and did not answer this. "
        "P7's own SPEC Contract-in requires 'P6 must accept `sensitivity` as a "
        "first-class universal field (§3.11) rather than a domain-scoped one', which "
        "pulls the other way. Until it is answered, P6 creates no such row and P7 "
        "reads none.",
})
```

- [ ] **Step 4: Fix whatever the guards catch**

No new module. If a guard fires, the fix is in the module that tripped it, never in the guard: the
guard is the SPEC's negative half. The one legitimate change is **narrowing** a token that proves to
be a false positive against a design-named value — which is why the ceiling guard here is about
**values** (`test_only_the_allowlisted_module_holds_a_number`) and never about names. Narrow; do not
delete.

- [ ] **Step 5: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_no_invention.py -v`
Expected: PASS — 30 passed

- [ ] **Step 6: Commit**

```bash
git add src/privacy/vocabulary.py tests/p7/test_p7_no_invention.py
git commit -m "test(P7): no-invention guard, every open question held open and D2's shape asserted"
```

---
### Task 22: The walking-skeleton P7 step, and 11 §9's second fixture path

**Files:**
- Test: `tests/p7/test_p7_skeleton_step.py`

**Interfaces:**
- Consumes: `orchestrator.run_wave2`, `.Wave2`, `.TARGETED_OCR_UNAVAILABLE`;
  `eval_harness.bundle.bundle_files`, `.get_bundle`; `database_agent.files_table.get_file`;
  `privacy.gate.Gate`; `privacy.fixtures.by_number`, `.gate_arguments`;
  `privacy.classification_store.ClassificationStore`; `privacy.learning_seam.assign`;
  `privacy.transport_guard.assert_single_egress`; `privacy.consent.record_consent_choice`;
  `privacy.audit.audit_records_for`; the whole gate.
- Produces: nothing. This is the integration test every later part must keep green.

**Done-means:** 13.

**Path one — the deterministic skeleton, where the door exists and is shut.**
02-segmentation-map.md notes the skeleton exercises no privacy gate *"because nothing leaves the
machine."* Done-means 13 requires it to assert five things anyway: the classification exists for the
scanned file; the gate is installed on the only egress path; `release` was called **zero** times; the
audit log is empty; and a deliberate attempted call under `offline` returns `Denied` with reason
`mode_forbids_target`.

**The test writes the classification itself, and says so.** D2 puts the rule set behind an injection
and no task in any plan produces one, so on a real corpus **every file resolves to
`Denied(unclassified)`**. The fixture stands in for the detector that does not exist. That is not a
convenience: it is the honest shape of *"P7 is done"* versus *"the product classifies files"*, and
the test's docstring says which of the two it is proving.

**The bundle's `handling_class` stays `None`, and this contradicts the skeleton.** The skeleton's
Task 22 says the test *"must also assert that after classification the Wave-2 bundle's
`handling_class` is non-null, closing the loop `src/orchestrator.py:259` left open."* It cannot and
must not:

- **P7 never reaches the bundle** — its own Open question 8 says so, and
  22-p1-p7-connection-contract.md §1 records the mis-attribution: *"`bundle_file_entry.handling_class`
  | mis-attributed here: **P7 never reaches the bundle** (its own OQ8 says so). The producer is the
  caller's stage 4, and **no task in either plan gives it a value**."*
- The live caller passes **literal `None`** (`src/orchestrator.py:402`) with a comment that is
  already the right answer: *"The honest value is None because the class is unknown, not because
  another column happened to be empty."*
- Making it non-null requires editing `src/orchestrator.py`, and P7 modifies no file it does not own.

So the test asserts `handling_class IS NULL`, names the field as the Wave-2 caller's, and records
what would close it: the caller reading P7's `ClassificationRecord` once a detector exists. A test
that forced a non-null value here would be P7 reaching into the bundle to satisfy a sentence, which
is exactly what OQ8 says it does not do. **Reported.**

**The one P2 surface P7 does touch is `open_bundle`'s `policy_settings`** (§8.5, and OQ8's own
carve-out: *"P7 writes nothing into a bundle; `open_bundle`'s `policy_settings` slot is the only
surface it touches"*). Path one passes P7's resolved display policy through it and asserts it
round-trips, so the one legitimate edge is exercised rather than assumed.

**Path two — 11 §9's second fixture path, verbatim:**

> ```text
> P7/P8   a dossier that requires sensitive text
>         Gate.release returns NeedsConsent
>         P13 presents the four §8.4 options
>         choosing no_model_use does not become abstain inside P8
> ```
>
> *"This is a contract test of B2, not an LLM test. It is the minimum that makes the one
> privacy-failure seam exercisable without waiting for full depth."*

P7 owns the first two clauses and asserts them here, against **published fixture 10** rather than a
locally rebuilt request, so the skeleton and the fixture set cannot drift apart. The third and
fourth are P13's Done-means 16 and P8's Done-means 13; the test names them as deferred to those
parts and does not fake a P8 that does not exist. What P7 *can* prove of the fourth clause is the
structural half — that `NeedsConsent` has no `reason` field, so a caller cannot map it onto a denial
reason even by accident, and that choosing `no_model_use` produces no `model_release`.

**One signature this task pins.** `consent.record_consent_choice(conn, consent_request_id, option, *,
user_id, component_version, observed_at) -> None`. Task 14 publishes it with an ellipsis, and path
two cannot record a choice without it. Reported.

**The Wave-2 helper is inlined rather than imported.** `tests/wave2/test_wave2_orchestrator.py`
carries a `go()` helper and deliberately has **no** `tests/wave2/conftest.py`, for the reason its own
comment gives: pytest's prepend import mode keys a rootless module on its basename, and a second
`conftest` claims `sys.modules["conftest"]` for the whole session. Importing that test module by name
from here would be the same hazard one level up. Forty duplicated lines is the cheaper of the two.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_skeleton_step.py
"""The walking skeleton's P7 step (02-segmentation-map.md), and 11 §9's second path.

Path one is the SEAM TEST: the door exists and is shut. The skeleton "exercises no
privacy gate, because nothing leaves the machine", and Done-means 13 requires that to
be asserted rather than assumed.

Path two is 11 §9's addendum -- a dossier that requires sensitive text, `Gate.release`
returning `NeedsConsent` -- which is a contract test of B2 and not an LLM test. P7 owns
two of its four clauses; the other two are named as P13's and P8's.

Neither path involves a model, a network call or an embedding.
"""
import dataclasses
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file
from eval_harness.bundle import bundle_files, get_bundle
from orchestrator import TARGETED_OCR_UNAVAILABLE, Wave2, run_wave2
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.selection import record_selection

from privacy.audit import audit_records_for
from privacy.authorship import (
    CONSENT_GRANTED, CONSENT_REQUESTED, MODEL_RELEASE, MODEL_RELEASE_DENIED,
    SUBSYSTEM,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.consent import record_consent_choice
from privacy.display import display_policy
from privacy.fixtures import by_number
from privacy.gate import Gate
from privacy.learning_seam import assign
from privacy.policy import Policy, set_policy
from privacy.release import Denied, NeedsConsent, Released, Target
from privacy.transport_guard import assert_single_egress
from privacy.vocabulary import CONSENT_OPTIONS

from transport_fixtures import CONFORMING

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
NEVER = lambda: False


# --- the Wave-2 harness, inlined ---------------------------------------------
#
# tests/wave2/test_wave2_orchestrator.py carries this helper and deliberately has NO
# tests/wave2/conftest.py: pytest's prepend import mode keys a rootless module on its
# BASENAME, so a second `conftest` claims sys.modules["conftest"] for the whole session
# and whichever directory imports first wins. Importing that test module by name from
# here is the same hazard one level up. Forty duplicated lines is the cheaper of the two.

def mime_for(path: Path) -> str | None:
    return {".pdf": "application/pdf", ".md": "text/markdown"}.get(path.suffix)


def readers():
    from extractors.archive import ArchiveManifest
    from extractors.dispatch import Readers
    from extractors.docx import DocxDocument
    from extractors.image import ImageRecord
    from extractors.long_tail import LongTailFile
    from extractors.pdf import PdfDocument, PdfPage
    from extractors.reading import Region
    from extractors.structured_text import TextDocument

    page = "BUSIB 4300 Course Information"
    return Readers(
        read_pdf=lambda p: PdfDocument(
            metadata={"Title": "BUSIB 4300 Syllabus"}, iso_dates={},
            pages=(PdfPage(number=1, text=page,
                           regions=(Region(zone="heading", start=0, end=29,
                                           ordinal=1,
                                           label="Course Information"),)),)),
        read_docx=lambda p: DocxDocument(core_properties={}),
        read_text_document=lambda p: TextDocument(text="BUSIB 4300 lecture notes"),
        read_long_tail=lambda p, transcribe=False: LongTailFile(),
        read_manifest=lambda p: ArchiveManifest(archive_type="zip"),
        read_image=lambda p: ImageRecord(image_format="PNG", dimensions="2880x1800",
                                         width=2880, height=1800),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None,
    )


@pytest.fixture()
def wired(p7_conn):
    from eval_harness.store import create_eval_schema
    from evidence_shape.schema import create_evidence_schema
    from extractors.schema import create_extraction_schema
    from scan_agent.schema import create_scan_schema
    create_scan_schema(p7_conn)
    create_evidence_schema(p7_conn)
    create_extraction_schema(p7_conn)
    create_eval_schema(p7_conn)
    return p7_conn


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "syllabus.pdf").write_bytes(b"%PDF-1.4 BUSIB 4300")
    (root / "notes.md").write_bytes(b"# BUSIB 4300\nlecture notes")
    return root


def wave2(conn, corpus: Path, *, policy_settings) -> Wave2:
    from evidence_shape.store import RunWriter
    from extractors.safety import SafetyPolicy
    from scan_agent.exclusion import is_protected_container

    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_wave2(
        conn, selection, source=FilesystemCorpusSource(), mime_type_for=mime_for,
        scan_state="scanned", budget_exhausted=NEVER,
        detect_format=lambda p: p.suffix.lstrip(".") or None,
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=readers(), sink=RunWriter(conn, author="P5"),
        now=lambda: FIXED_CLOCK, context_window=40,
        no_usable_facts=TARGETED_OCR_UNAVAILABLE,
        transcription_authorized=NEVER, corpus_form="snapshot",
        policy_settings=policy_settings,
        file_entry_body=lambda row: {"payload_ref": f"blobs/{row['content_hash']}"})


def p7_events(conn):
    return conn.execute(
        "SELECT * FROM events WHERE subsystem = ? ORDER BY event_id",
        (SUBSYSTEM,)).fetchall()


def install_offline(conn) -> str:
    return set_policy(conn, Policy(
        policy_version="", operation_mode="offline", consent_grants=(),
        redaction_settings={}, automatic_move_permissions={},
        plan_version="plan-1", set_at=FIXED_CLOCK),
        component_version=COMPONENT, user_id="joseph",
                      reason="the user granted cloud use for Academics")


def a_gate(conn, store, **over):
    base = dict(store=store, plan_version="plan-1",
                classifier=lambda value: "fixture-identifier-class",
                transform=lambda value, *, identifier_class: "[redacted]",
                unclassified_permits_local=False,
                scope_for=lambda file_id: "Academics",
                files_in_scope=lambda scope: (),
                component_version=COMPONENT, now=lambda: FIXED_CLOCK,
                user_id="joseph")
    base.update(over)
    return Gate(conn, **base)


# =============================================================== path one ====

def test_skeleton_p7_step(wired, corpus):
    """Done-means 13, all five clauses, plus the bundle field that is NOT P7's."""
    conn = wired
    store = ClassificationStore(conn)
    policy_version = install_offline(conn)

    # §8.5's "policy settings" slot is the ONE P2 surface P7 touches (OQ8). The gate
    # writes nothing into the bundle; the caller carries the settings across.
    settings = display_policy(conn, plan_version="plan-1")
    result = wave2(conn, corpus, policy_settings={
        "operation_mode": "offline",
        "policy_version": policy_version,
        "redaction_settings": {facet: settings.facet(facet)
                               for facet in ("names", "previews", "thumbnails",
                                             "ocr_text", "location_data")},
    })
    assert isinstance(result, Wave2)

    # 1 -- the classification exists for the scanned file.
    #
    # THE TEST WRITES IT, STANDING IN FOR THE DETECTOR THAT DOES NOT EXIST. D2 puts
    # the rule set behind an injection and no task in any plan produces one, so on a
    # real corpus every file resolves to Denied(unclassified). This asserts that P7 is
    # done, not that the product classifies files; those are different claims.
    file_ids = [row["file_id"] for row in
                conn.execute("SELECT file_id FROM files ORDER BY filename")]
    assert file_ids
    subject = file_ids[0]
    content_hash = get_file(conn, subject)["content_hash"]
    written = assign(conn, ClassificationRecord(
        file_id=subject, content_hash=content_hash,
        handling_class="personal_non_sensitive", protected=False, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=FIXED_CLOCK), store=store, component_version=COMPONENT)
    assert written is not None
    assert store.current(subject, content_hash) is not None
    assert json.loads(get_file(conn, subject)["sensitivity_state"])[
        "handling_class"] == "personal_non_sensitive"

    # 2 -- the gate is installed on the only egress path.
    #
    # The instrument, over a conforming transport. The REAL transport is P8's and does
    # not exist; `test_p7_transport.py` carries the same statement in its own suite.
    assert assert_single_egress(CONFORMING) is None

    # 3 -- `release` was called zero times, and 4 -- the audit log is empty.
    #
    # Zero P7 events of ANY of the eight types: no release, no denial, no consent
    # request. The classification events from clause 1 are the test's own act and are
    # excluded by type, not by subsystem, so a stray `model_release` still fails.
    assert [row["event_type"] for row in p7_events(conn)
            if row["event_type"] in (MODEL_RELEASE, MODEL_RELEASE_DENIED,
                                     CONSENT_REQUESTED)] == []
    assert audit_records_for(conn, file_id=subject) == []

    # 5 -- a deliberate attempted call under `offline` is denied.
    #
    # Fixture 8 IS this case, so the skeleton reuses it rather than rebuilding the
    # request: a locally rebuilt one is a second definition of the same thing.
    attempt = dataclasses.replace(
        by_number(8).request, target=Target(file_ids=(subject,), group_id=None))
    decision = a_gate(conn, store).release(attempt)
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"
    assert decision.explanation and decision.remedy_options

    # ... and the denial is audited, because §8.2 records "every significant event
    # affecting a file" and §8.6 requires the UI to show "what has been deferred, and
    # why". The door being shut is itself a record.
    denials = [row for row in p7_events(conn)
               if row["event_type"] == MODEL_RELEASE_DENIED]
    assert len(denials) == 1
    assert [row["event_type"] for row in p7_events(conn)
            if row["event_type"] == MODEL_RELEASE] == []

    # The §8.5 slot round-trips, and it is the only thing P7 put in the bundle.
    stored = json.loads(get_bundle(conn, result.bundle_id)["policy_settings"])
    assert stored["operation_mode"] == "offline"
    assert stored["redaction_settings"]["names"] == "redacted"


def test_the_bundles_handling_class_is_the_wave_2_callers_and_is_still_null(
        wired, corpus):
    """P7 never reaches the bundle -- its own Open question 8 says so.

    `src/orchestrator.py:402` passes literal `None`, with the comment that is already
    the right answer: "The honest value is None because the class is unknown, not
    because another column happened to be empty."

    The plan skeleton asked this test to assert the field is NON-null after a
    classification. It cannot: closing the loop means the CALLER reading P7's
    `ClassificationRecord`, which is an edit to `src/orchestrator.py`, a file P7 does
    not own -- and doing it from here would be P7 reaching into the bundle to satisfy a
    sentence, which is the one thing OQ8 says it does not do. Asserted as it stands,
    with the closing move named.
    """
    conn = wired
    store = ClassificationStore(conn)
    install_offline(conn)
    result = wave2(conn, corpus, policy_settings={})

    for row in conn.execute("SELECT file_id, content_hash FROM files"):
        assign(conn, ClassificationRecord(
            file_id=row["file_id"], content_hash=row["content_hash"],
            handling_class="personal_non_sensitive", protected=False, basis="user",
            evidence_refs=(), reliability_state="user_confirmed",
            observed_at=FIXED_CLOCK), store=store, component_version=COMPONENT)

    entries = bundle_files(conn, result.bundle_id)
    assert entries
    assert all(entry["handling_class"] is None for entry in entries)

    # And the value that WOULD close it is available, from P7's authoritative record,
    # for the caller that decides to read it.
    for entry in entries:
        record = store.current(entry["file_id"], entry["content_hash"])
        assert record is not None
        assert record.handling_class == "personal_non_sensitive"


def test_the_orchestrator_never_constructs_a_gate(wired, corpus):
    """The skeleton is deterministic BY CONSTRUCTION, not by discipline."""
    import orchestrator
    assert not [name for name, value in vars(orchestrator).items()
                if getattr(value, "__module__", "").startswith("privacy")]
    install_offline(wired)
    wave2(wired, corpus, policy_settings={})
    authors = {row["subsystem"] for row in wired.execute(
        "SELECT DISTINCT subsystem FROM events")}
    # `install_offline` appends P7's `policy_set`; the SCAN authors nothing but P3
    # and P5. No P7 event comes from inside `run_wave2`.
    assert authors <= {"P3", "P5", SUBSYSTEM}


# =============================================================== path two ====

def test_a_dossier_requiring_sensitive_text_returns_needs_consent(wired, corpus):
    """11 §9, clauses one and two. P7 owns these; the other two are named below.

    Built on PUBLISHED FIXTURE 10 rather than a locally rebuilt request, so the
    skeleton path and the fixture set cannot drift apart.
    """
    conn = wired
    store = ClassificationStore(conn)
    fixture = by_number(10)
    set_policy(conn, fixture.policy, component_version=COMPONENT,
               user_id="joseph",
               reason="the published fixture's policy")
    wave2(conn, corpus, policy_settings={})

    subject = conn.execute(
        "SELECT file_id, content_hash FROM files ORDER BY filename").fetchone()
    store.write(ClassificationRecord(
        file_id=subject["file_id"], content_hash=subject["content_hash"],
        handling_class="sensitive_personal", protected=False, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=FIXED_CLOCK))

    request = dataclasses.replace(
        fixture.request,
        target=Target(file_ids=(subject["file_id"],), group_id=None))
    decision = a_gate(conn, store).release(request)

    # Clause two: `Gate.release` returns `NeedsConsent`.
    assert isinstance(decision, NeedsConsent)
    assert decision.consent_request_id

    # Clause three's P7-side half: all four §8.4 options are present, so P13 has
    # something to present. "A surface that offers fewer has silently made the user's
    # decision for them."
    assert tuple(decision.options) == tuple(CONSENT_OPTIONS)
    assert set(CONSENT_OPTIONS) == {"local_model", "cloud_model", "redacted_prompt",
                                    "no_model_use"}

    # Done-means 7's own falsifiable form: a `consent_requested` event, and no
    # `model_release` for that request until a choice is recorded.
    records = audit_records_for(conn, consent_request_id=decision.consent_request_id)
    assert [record.outcome for record in records] == ["consent_requested"]
    assert [row["event_type"] for row in p7_events(conn)
            if row["event_type"] == MODEL_RELEASE] == []


def test_choosing_no_model_use_records_a_choice_and_releases_nothing(wired, corpus):
    """Clause four, the half P7 can prove: `no_model_use` produces no release."""
    conn = wired
    store = ClassificationStore(conn)
    fixture = by_number(10)
    set_policy(conn, fixture.policy, component_version=COMPONENT,
               user_id="joseph",
               reason="the published fixture's policy")
    wave2(conn, corpus, policy_settings={})
    subject = conn.execute(
        "SELECT file_id, content_hash FROM files ORDER BY filename").fetchone()
    store.write(ClassificationRecord(
        file_id=subject["file_id"], content_hash=subject["content_hash"],
        handling_class="sensitive_personal", protected=False, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=FIXED_CLOCK))
    request = dataclasses.replace(
        fixture.request,
        target=Target(file_ids=(subject["file_id"],), group_id=None))
    pending = a_gate(conn, store).release(request)

    record_consent_choice(conn, pending.consent_request_id, "no_model_use",
                          user_id="joseph", component_version=COMPONENT,
                          observed_at=FIXED_CLOCK)

    # P13 records the collection; P7 authors the grant (P13 SPEC).
    granted = [row for row in p7_events(conn)
               if row["event_type"] == CONSENT_GRANTED]
    assert len(granted) == 1
    assert granted[0]["subsystem"] == "P7"
    assert granted[0]["user_id"] == "joseph"

    # And still no release. `no_model_use` is a choice, not a call.
    assert [row["event_type"] for row in p7_events(conn)
            if row["event_type"] == MODEL_RELEASE] == []
    assert not [record for record in audit_records_for(
        conn, consent_request_id=pending.consent_request_id)
        if record.outcome == "released"]


def test_needs_consent_cannot_be_mapped_onto_a_denial_reason():
    """The structural half of B2, which is P7's obligation rather than P8's.

    "P7's obligation is to make the absorption unrepresentable, not to police it."
    `NeedsConsent` has no `reason` field, so a caller cannot fold it into a denial even
    by accident, and it is not a `Denied` subclass, so an `except`/`isinstance` written
    for one does not catch the other.
    """
    import dataclasses
    fields = {field.name for field in dataclasses.fields(NeedsConsent)}
    assert "reason" not in fields
    assert fields == {"consent_request_id", "requirement", "options"}
    assert not issubclass(NeedsConsent, Denied)
    assert not issubclass(NeedsConsent, Released)


def test_clauses_three_and_four_belong_to_p13_and_p8():
    """11 §9's remaining two clauses are DEFERRED, and named rather than faked.

    "P13 presents the four §8.4 options" is P13 Done-means 16. "choosing
    `no_model_use` does not become `abstain` inside P8" is P8 Done-means 13, and P8's
    own SPEC already says `PRIVACY_GATE_REFUSED` "covers the gate's `Denied` branch and
    nothing else" -- so the mapping P8 must not make is one its own registry has
    already been told not to have.

    Neither part exists. This test records the split so the skeleton is not later read
    as having proved all four clauses.
    """
    import importlib.util
    assert importlib.util.find_spec("llm_harness") is None
    assert importlib.util.find_spec("review_surface") is None
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_skeleton_step.py -v`
Expected: FAIL if any prior task is incomplete; otherwise PASS. The first failure to expect is
`ImportError: cannot import name 'record_consent_choice' from 'privacy.consent'` if Task 14 has not
adopted the signature this task pins.

- [ ] **Step 3: Run the whole suite one final time**

Run: `pytest -q --tb=short`
Expected: PASS — every P7 test from Tasks 1–22 green, and the 1302 P1–P5 tests still green. P7
created `src/privacy/` and `tests/p7/` and modified no file belonging to another part:
`pyproject.toml`, `tests/conftest.py`, `src/orchestrator.py` and everything under
`src/database_agent/`, `src/scan_agent/`, `src/evidence_shape/`, `src/extractors/` and
`src/eval_harness/` are untouched. Confirm with:

```bash
git status --porcelain
```

Expected: only `src/privacy/**` and `tests/p7/**` appear.

- [ ] **Step 4: Commit**

```bash
git add tests/p7/test_p7_skeleton_step.py
git commit -m "test(P7): walking-skeleton P7 step, the door shut, and 11 9's second fixture path"
```

---
## Self-Review — Tasks 15–22

**Spec coverage.** SPEC §8's revocation surface → Task 15. §8.7's *Correction learning* and
10-i4's query-before-propose row for P7 → Task 16. SPEC §9's automatic-move predicate → Task 17.
SPEC §10's display policy and aggregate summary → Task 18. Done-means 3's instrument → Task 19.
SPEC §11's fixture list, item for item → Task 20. The *Deferred* table and all eleven Open questions
→ Task 21. Done-means 13 and 11 §9's second path → Task 22.

Done-means in this section: **8** → T15 · **9** (first clause) → T17 · **10** → T18 · **3** (the
instrument only) → T19 · **11** (first clause) → T20 · **12** (the display half) → T18, (the
introspection half) → T21 · **2** (the user-revision half) → T16 · **13** → T22.

**Three items are not fully provable here and each names the part that closes it.** Done-means 3's
property is P8 Done-means 1 (T19 has a named test). Done-means 9's second clause is P11's and P12's
(T17 names the permitting policy so they can consume rather than re-derive). Done-means 11's second
clause is P8's test run (T20 has a named test). None is hidden.

**No invention.** No module in this section holds a number except `privacy.fixtures`, which holds
two, both allowlisted by name in Task 21 and both installed through P1's `budget.set_ceiling`. No
regex, no gazetteer, no identifier class outside the fixture's own opaque string, no retention
period, no corpus-area definition, no detection rule, no default operation mode. Every scope is a
required keyword with no default (`files_in_scope`, `scope_for`), and so is every question the design
leaves open (`unclassified_permits_local`, `retraction_limit`, `classifier`, `transform`).

**Every guard is runtime introspection**, with one exception that is stated where it occurs: Task 21's
SQL guard walks the AST and excludes docstrings, the `code_tokens()` mechanism from
`tests/p3/test_p3_no_invention.py`, because *"this token appears nowhere"* cannot be asserted by
introspecting a namespace.

**P7 modifies no file it does not own.** Every task creates only under `src/privacy/` and `tests/p7/`.
Task 22's final step checks it with `git status --porcelain`.

---

## Where the skeleton was ambiguous or self-contradictory

Each of these was resolved in the plan above and is listed so a reviewer can reject the resolution
rather than discover it.

| # | Where | What is wrong, and what this section did |
|---|---|---|
| 1 | Task 21 `Interfaces` · Task 2 `Produces` | The skeleton's **repo-wide L2 set `{evidence_shape, extractors, privacy}` is wrong in both directions.** Measured 2026-08-22: `extractors` binds **no** P4 text materialiser, and **`orchestrator` binds `text_units_for_run`** (`src/orchestrator.py`, copying text units into P2's sealed bundle). Task 21 asserts `{evidence_shape, orchestrator, privacy}` with a reason per member. A guard naming a package that binds nothing passes forever without checking anything. |
| 2 | Task 22 | **`bundle_file_entry.handling_class` cannot be made non-null by P7.** The skeleton asks Task 22 to assert it is non-null after a classification; P7's own OQ8 and 22-p1-p7-connection-contract.md §1 say P7 never reaches the bundle, and the live caller passes literal `None` at `src/orchestrator.py:402`. Task 22 asserts `NULL`, names the field as the Wave-2 caller's, and names the closing move. |
| 3 | SETTLED paragraph · Tasks 16, 17, 18 | The `facts_seam` → `classification_store` rename says *"Tasks 12, 13 and 14 change only the import and the type name"* — but **Tasks 16, 17 and 18 also name `facts_seam.SensitivityFacts`** in their `Consumes` blocks. Renamed here on the same ruling. |
| 4 | Task 4 `Produces` | `ClassificationStore` publishes `current`, `write`, `supersede`, `history` and **no way to get a record's id**, while P1's `mark_superseded` keys on a `record_id` column and `ClassificationRecord`'s eight SPEC §2 fields carry none. Task 16 cannot supersede. **Added `current_fact_id(file_id, content_hash) -> str \| None`.** |
| 5 | Task 5 `Produces` | `grant_consent(...)` and `revoke_consent(...)` are published **with literal ellipses**. Task 15 pins `revoke_consent(conn, policy, scope, *, user_id, component_version, observed_at) -> str`, returning the new `policy_version` and appending **no** event — the `consent_revoked` append is `revoke`'s, which is the only reading under which Task 15's `Consumes` list (`CONSENT_REVOKED` **and** `append_event` **and** `revoke_consent`) is coherent. |
| 6 | Task 14 `Produces` | `record_consent_choice(conn, consent_request_id, option, *, user_id, ...)` ends in an ellipsis. Task 22 pins `*, user_id, component_version, observed_at -> None`. |
| 7 | Task 11 · Task 20 | **`Gate.__init__` is unpinned anywhere**, and SPEC §11's fixtures cannot be replayed without it — and an unreplayed fixture is the drift the skeleton itself calls *"worse than none."* Task 20 publishes `GATE_ARGUMENTS`, ten keywords, each traceable to a published requirement or an open question. |
| 8 | Task 15 `Produces` · D3 | **`UnratifiedResolution` is now a misnomer** — D3 ratified the direction. The name is kept because it is the published contract, its docstring says what it now reports (*unbuilt*, not *unratified*), and a second exception `ScopeNotDerived` carries the other side of the enumeration. A rename is a contract revision and is left to Joseph. |
| 9 | Task 15 `Produces` | `revoke(conn, policy, scope, *, user_id, ...)` ends in an ellipsis and `RevocationResult.prior_releases` needs the files in scope, which OQ3 leaves unnamed. Added `files_in_scope` and `retraction_limit`, both required keywords with no default. |
| 10 | SPEC §7 vs the skeleton's audit-record paragraph | **`appended_at` versus `observed_at`.** SPEC §7 lists `appended_at`; the skeleton's *audit record's home* paragraph lists `observed_at` among the five fields with an `events` column and does **not** list `appended_at` among the thirteen without one. Tasks 15 and 20 read `record.observed_at` and build every fixture from `AUDIT_FIELDS` rather than a literal list, so a respelling of a field they do not read cannot break them — but **Task 10 must settle which name it publishes.** |
| 11 | Skeleton preamble | **`AUDIT_FIELDS` is said to be nineteen and SPEC §7's own list enumerates sixteen names**, with `content_hash`/`content_hashes` and `file_id`/`file_ids` appearing in both singular and plural forms across the two documents. Tasks 15 and 20 build from the published tuple and assert coverage rather than the count, so the count is Task 10's to settle. |
| 12 | Tasks 11 and 14 | **`NeedsConsent` is in both `Produces` blocks** — Task 11's branch-type list and Task 14's. Two definitions of one type is the defect class this project pays for most. This section imports it from `privacy.release` (Task 11's) throughout; Task 14 should re-export, not redefine. |
| 13 | Task 16 `Produces` | `suppressed` is a predicate, and 10-i4's Done-means is *"**zero re-emissions**"* — a predicate returning `True` is not an emission that did not happen. **Added `assign`**, the system-side write that returns `None` when suppressed. |
| 14 | Task 16 `Consumes` | The list omits `authorship`, `append_event` and `set_sensitivity_state`, while *"What its tests must prove"* requires `reclassify` to append `classification_superseded` and D2 requires the projection. Added. |
| 15 | Task 17 `Interfaces` | `may_move_automatically(conn, file_id, plan_version)` has no way to reach the `content_hash` the classification is keyed on (D2). Added `database_agent.files_table.get_file` and the keyword-only `store` and `scope_for`. |
| 16 | Task 18 `Interfaces` | `display_policy(conn)` cannot read a plan-scoped policy (§8.8) and `summarize_protected(conn, scope)` cannot enumerate a scope OQ3 leaves unnamed. Widened with keyword-only `plan_version`, `store` and `files_in_scope`; SPEC §10's published `Gate.display_policy()` / `Gate.summarize_protected(scope)` are unchanged where a caller sees them. |
| 17 | Task 18 | Neither Task 2's `DISPLAY_FACETS` nor Task 6's `MORE_REDACTING` claims the two **values** SPEC §10 states (`shown | redacted`). They are defined in `display.py`, which is the first module that needs them. |
| 18 | Task 19 `Produces` | Two exceptions, and a module with **no** public function is neither — it passes any `len(functions) <= 1` check, which is the vacuous pass this layer exists to prevent. Added `NoEgressPoint`. |
| 19 | Task 20 `Produces` | `GateFixture`'s six fields cannot express the classification a fixture assumes, nor the *"obligation on P8 ... in their own metadata"* the same paragraph requires. Added `classification` and `p8_obligation`, both with defaults, so the six-name positional order is unchanged. |
| 20 | Task 21 `Interfaces` | `vocabulary.OPEN_QUESTIONS` is asserted there and appears in **no** task's `Produces`. Task 21 adds it to `vocabulary.py`, together with `NEEDS_JOSEPH` for the two items held open by name (B5d/C9a and C5), which are not among SPEC's numbered eleven. |
| 21 | Task 21 · D2 | The skeleton's own Task 21 text says *"That **the D2 shape holds** — see §4"*, while §5 of the preamble still says *"Every open question stays open ... Eleven questions are open in P7's SPEC."* P6 OQ11 is closed and is **not** one of P7's eleven, so both are true — but a guard written from the second sentence without reading the first fails on execution day. The guard is written from D2. |
| 22 | Skeleton *Deferred* table vs Task 15 | The table keeps *"The **presence** of `retraction_limit` is asserted; the wording is not"*, but the `Produces` block gives `revoke` no way to receive a wording. `retraction_limit` is now a required keyword with no default, and Task 21 asserts no module-level string in `src/privacy/` contains the word. |

## What remains for Joseph, from this section only

1. **I6 / D3.** `delete_derived` refuses on both sides of the enumeration and writes nothing. The
   enumeration — `evidence.{raw_value, normalized_value, context_before, context_after}` and
   `text_units.text` — is written down here for the first time and is the thing to check.
   **No tombstone column exists**; P13 drives the migration.
2. **`UnratifiedResolution`'s name** (item 8 above). Keeping it is a contract-stability choice, not a
   semantic one.
3. **B5d / C9a — `filename` as a sixth releasable kind.** Held open by name in
   `vocabulary.NEEDS_JOSEPH` and exercised by fixture 16, where §7.3's Protected Records rule denies
   it either way, so the fixture does not settle it.
4. **C5 — does P6 keep a `sensitivity status` field row?** Held open by name. P7's SPEC Contract-in
   *requires* P6 to build it; D2 makes P7's record authoritative. Until it is answered, P6 creates no
   such row and P7 reads none.
5. **Open question 5** — whether `unreadable_unclassified` permits a local model call. Carried as
   `Gate(..., unclassified_permits_local=...)` with no default, and as fixtures 14 and 15, one per
   branch.
6. **Open question 3** — what a corpus area is. Three functions take a resolver with no default.
7. **The detector.** Not in this section's gift and not in any task's: D2 puts the rule set behind an
   injection and no plan produces one. Until it is supplied, `Denied(unclassified)` is what a real
   corpus gets, `summarize_protected` reports `count = 0`, and `may_move_automatically` refuses every
   file. Every task above is built for that being the ordinary path.
