# P7 — Privacy and consent gate — PLAN, Tasks 12–14

> This file is one section of P7's implementation plan. Tasks 1–11 and 15–22 are written by other
> authors against the same [`PLAN-SKELETON.md`](PLAN-SKELETON.md); everything they publish is
> consumed here under the names the skeleton's `Interfaces:` blocks fix, and Task 14 hands off to
> Task 15 as written in [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md). Format and standard are
> [`../P5-extractors/PLAN.md`](../P5-extractors/PLAN.md) and
> [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md).

**Verified against the live substrate, 2026-08-22.** Every P1–P5 name quoted below was read with
`inspect.signature` and `inspect.getsource` against the shipped packages, not from a PLAN.
`pytest tests/ -q --collect-only` collects **1300 tests** and P1–P5 are green. Five facts that
change what is written here:

- `database_agent.events.append_event(conn, **fields) -> int` returns `cursor.lastrowid`, rejects any
  key outside its seventeen `_WRITABLE` names with `MalformedEvent`, and requires
  `('event_type', 'subsystem', 'component_version', 'observed_at', 'explanation')` to be present and
  non-empty. All eight of P7's event types are already in `REGISTERED_EVENT_TYPES` with `base = None`.
- `database_agent.budget.CEILING_KEYS` has **sixteen** members and contains
  `model.max_dossier_tokens_per_call`. `get_ceiling(conn, key) -> int | None` — **`None` when nothing
  set it**, which is the ordinary state and which Task 13 must handle without inventing a number.
- `database_agent.db.open_database` opens with `isolation_level=None` (autocommit) and
  `row_factory = sqlite3.Row`, and installs `_deny_events_history_loss` as a `set_authorizer` hook
  that denies only `SQLITE_DROP_TABLE events` and `SQLITE_DROP_TRIGGER` on the three append-only
  trigger names. **`CREATE TABLE` is not denied**, so P7 may create its own tables on the same handle.
- `evidence_shape.canonical.canonical_json(value) -> str` is `json.dumps(..., sort_keys=True,
  separators=(",", ":"), ensure_ascii=False, allow_nan=False)`. Tuples serialise as arrays, so a
  frozen dataclass passed through `dataclasses.asdict` has exactly one stored form.
- The `events` table has **no `appended_at` column**. `AuditRecord.appended_at` lives in the
  `explanation` JSON, per the skeleton's *The audit record's home*.

---

## Four rulings that bind this section, applied rather than restated

**`Denied(unclassified)` is the ordinary path, not the exotic one.** No task in any plan produces a
detector (D2), so against a real corpus **every file resolves to `Denied(unclassified)`**. Task 13 is
therefore written with `unclassified` as its centre of gravity: it gets the longest explanation, the
most remedy options, its own precedence argument, and the test that proves absence resolves to
`unreadable_unclassified` and never to `public_low`. A `Denied` is what this gate returns on a
Tuesday. It is not an error path.

**`Unreadable or unclassified` is a gate OUTCOME, not a file fact (D2).** It appears on the release
decision and in `AuditRecord.file_sensitivity`, which is a field of the *decision* record. It never
reaches `files.sensitivity_state`. Task 13 asserts that a denial leaves that column exactly as it
found it — the same test proves C4 and D2 at once.

**The gate refuses RELEASE, not reading, and it raises and writes nothing beyond its audit record**
(C4: *"a gate that also wrote would be doing two jobs"*). Task 13 appends one `model_release_denied`
and writes nothing else. Task 14 appends one `consent_requested` and later one `consent_granted`, and
writes no classification, no `stage_output`, and no P8 `Refusal`. **The catcher is always the
caller's.**

**`no_model_use` must never become `abstain` inside P8, and P7's job is to make that
unrepresentable.** P8's SPEC: *"P8 must never map this branch to `abstain`: there is no reason code
for it, and none may be added… Consent pending is not consent refused."* Task 14 does two things
about it and no third: `NeedsConsent` carries no `reason` field, so it cannot be read as a `Denied`;
and choosing `no_model_use` writes a `consent_granted` event with a `user_id` and a timestamp, so a
later reader can tell a recorded refusal from silence. **Whether a caller absorbs the branch is P8
Done-means 13 and P13 Done-means 16; P7 does not police it.**

**P7 never reaches the bundle.** Open question 8 leaves it unsettled, so nothing in these three tasks
writes `bundle_file_entry.handling_class`. `src/orchestrator.py` passing literal `None` is honest
while no detector exists, and Task 22 owns whatever closes it.

---

## The import direction, decided here because Tasks 11–14 cannot all be written without it

Three of this section's modules need the branch dataclasses that Task 11 publishes, and Task 11's
`Gate.release` needs all three of this section's modules. Written naively that is an import cycle in
four places. It is broken once, at the type layer, and the rule is:

```text
release.py    ModelCallRequest · ModelTarget · Target · Released · Denied · ReleaseDecision
              imports privacy.consent for NeedsConsent, and no other privacy module
consent.py    NeedsConsent · ConsentRequirement       imports policy, audit, authorship, vocabulary
binding.py    the ledger                              imports release under TYPE_CHECKING ONLY
denial.py     the eight denials                       imports release.Denied at run time
gate.py       the Gate facade                         imports all four; holds the decision logic
```

`binding.py` never *constructs* a `Released` — `mint_release` returns a `str` and the facade builds
the value — so its need for the type is annotation-only and a `TYPE_CHECKING` guard is honest rather
than evasive. `denial.py` does construct a `Denied`, so it imports `release` at run time and
`release` must not import it back; the facade is where the two meet. `NeedsConsent` stays in
`consent.py` because the skeleton gives Task 14 its three fields and its four-option invariant, and
one dataclass cannot have two homes; `release.py` re-exports it so `ReleaseDecision` reads as one
union in one place. **Task 11's author owns `release.py` and this is the one constraint these three
tasks place on it.** Reported.

---

## What these three tasks add to the skeleton's `Produces` blocks, and why

Every addition is named here rather than appearing silently inside a code block.

| Added | Task | Why the task cannot be written without it |
|---|---|---|
| `Denied.evidence_refs` — a fourth field on Task 11's dataclass | 13 | The skeleton's own `deny(reason, *, explanation, remedy_options, evidence_refs)` takes them, and SPEC §6 requires the explanation be *"evidence-referenced"*. A constructor that accepts a value the dataclass cannot hold is not writable. |
| `DENIAL_ORDER: tuple[str, ...]` and `first_reason(reasons) -> str \| None` | 13 | The skeleton requires eight tests *"each reaching **exactly** that reason and no other"*. Four of the eight overlap on real inputs, so "exactly" is unmeetable without a stated total order. `Gate.release` consumes both. |
| `DECIDABLE_FROM_REQUEST: frozenset[str]` | 13 | The principle that orders them — no denial decidable from the request alone may be decided after one that needs the file's content — is only enforceable if it is data. |
| `MalformedDenial(ValueError)` | 13 | `deny` validates three things (non-empty explanation, at least one remedy, evidence refs that are keys). Three bare `ValueError`s are untestable apart. |
| `record_denial(conn, denied, *, …) -> int` | 13 | The skeleton lists `audit.append_audit` in Consumes and requires every denial to append. The helpers are pure because they do not see the request or the policy; something has to be the append. |
| `REVOKED_SCOPE_KEY: str = "scope"` | 13 | `policy_revoked` reads Task 15's `consent_revoked` explanation. The key is `"scope"`, verified against the written [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md); pinning it makes a rename a red test on both sides. |
| `IncompleteConsentOptions`, `UnknownConsentRequest`, `ConsentAlreadyRecorded` | 14 | Three distinct refusals: fewer than four options, an id nobody opened, and a second answer to a question already answered. `UnknownConsentOption` names none of them. |
| `CONSENT_AUTHORIZES: Mapping[str, bool]` | 14 | Three of the four options authorize a model and one does not. Which is which decides whether `policy.grant_consent` is called, and it must be data rather than an `if` a later reader can invert. |

**And one thing these tasks deliberately do NOT add: a `BEFORE DELETE` trigger on any P7 table.**
Task 15's `test_thirteen_tables_already_refuse_a_delete` counts the guarded tables on a `p7_conn`
and asserts **thirteen**. A fourteenth would fail a sibling task. The release ledger is a capability
record, not a provenance record; §8.2's R6 binds `events`, and P7 does not extend it by imitation.

---

## Two signatures these tasks pin for their neighbours

1. **`policy.grant_consent(conn, policy, scope, option, *, user_id, component_version, observed_at)
   -> str` records the grant and returns the new `policy_version`. It appends no event.** The one
   `consent_granted` event is appended by `consent.record_consent_choice`. This is the exact mirror
   of the ruling Task 15 already made for `revoke_consent` and `consent_revoked`, and for the same
   reason: two appends put one act in the log twice, and §8.4's `prior_releases` is read back out of
   that log. Task 5's `Produces` spells `grant_consent(...)` with an ellipsis, so the spelling is
   fixed here.
2. **`audit.append_audit` maps `AuditRecord.outcome` onto the event type**, `released` →
   `model_release`, `denied` → `model_release_denied`, `consent_requested` → `consent_requested`.
   Task 10 Consumes exactly those three authorship constants and `vocabulary.AUDIT_OUTCOMES` has
   exactly three members; the mapping is the only shape that uses both. Tasks 13 and 14 append
   through `append_audit` and never name an event type themselves.

---

## Tasks

### Task 12: Binding and single use

**Files:**
- Create: `src/privacy/binding.py`
- Modify: `src/privacy/schema.py` (execute `RELEASE_LEDGER_DDL`; Task 5 created the file)
- Test: `tests/p7/test_p7_binding.py`

**Interfaces:**
- Consumes: `privacy.release.Released` and `privacy.release.ModelTarget` (**annotation only** — see
  the import-direction section above), `privacy.release.RELEASED_FIELDS` (in the test),
  `privacy.policy.Policy`, `privacy.schema.create_privacy_schema(conn) -> None`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`binding.py`):
  - `RELEASE_LEDGER_DDL: str` — the one table this task owns.
  - `BINDING_TERMS: tuple[str, str, str] = ("model_target", "prompt_fingerprint", "policy_version")`.
  - `mint_release(conn, *, policy, model_target, prompt_fingerprint, audit_id, minted_at) -> str`.
  - `consume_release(conn, released, *, model_target, prompt_fingerprint, policy_version) -> None`.
  - `ReleaseNotIssued`, `ReleaseAlreadySpent`, `BindingMismatch`.

**Done-means:** 5, and layer L1 of 3.

**This task is the whole of the sentence the part exists for.** *"A call that bypasses P7 is not a
policy violation to be caught in review — it is a call that cannot be constructed."* Nothing else in
P7 makes that true. The vocabularies can be respelled, the denials can be argued about, the audit
record can be reshaped — and the door still holds, because the token a transport must present is
minted in one function, recorded in one table, and spent once. The three tests that carry it are
`test_a_hand_constructed_released_is_inert`, `test_a_second_use_of_the_same_release_is_refused`, and
the three binding-mismatch tests. Everything else in the file is scaffolding for those five.

**Why the ledger is not a second job (C4).** The plan's own §3 L1 says the `release_id` is *"minted
by the gate and recorded in P7's ledger"*, so the row is sanctioned by the layer it belongs to. The
argument is the same one that puts the audit append inside the release decision: a capability that
is single-use has to have somewhere that records it was used, and that record is not a second
subject — it is the capability. What C4 forbids is the gate writing about *other parts' subjects*:
a classification, `files.sensitivity_state`, a `stage_output`, a placement decision, P8's `Refusal`.
The ledger row is about the release and nothing else.

**`mint_release` takes the `Policy`; `consume_release` takes the echoed `policy_version` string.**
This asymmetry is SPEC §6 made structural: *"the gate owns the policy, so the caller does not supply
this value, it echoes it."* The minter is inside the gate and holds the policy object; the consumer
is the transport, outside the gate, and can only echo. A `mint_release` that accepted a
`policy_version` string would let a caller stamp a release with a version that was never in force.
A test asserts both halves by `inspect.signature`.

**The spend is one atomic `UPDATE … WHERE spent_at IS NULL`, and a mismatch never spends.** Reading
the row, deciding, and then marking spent would leave a window between the decision and the mark.
`UPDATE … WHERE release_id = ? AND spent_at IS NULL` with `rowcount != 1` as the refusal collapses
check and mark into one statement, so single-use survives a second caller arriving between them.
And the binding is checked **before** the spend, never after: a call under the wrong model must not
burn the token, because burning it would let a mis-wired caller destroy an authorization the user
granted, and because a release that never reached a model must not be recorded as one that did.

**`audit_id` is carried and never compared.** SPEC §6: *"`audit_id` remains a field of `Released` —
it is what makes the record traceable — but it is not a binding term: two releases differing only in
audit record are the same authorization, while a release spent under a different policy version is
not."* The column exists so a ledger row can be joined back to its `events` row; the comparison is
driven by `BINDING_TERMS`, which has three members and does not contain it. The test constructs
exactly the pair SPEC §6 describes and shows both consume.

**`audit_id` is `NOT NULL`, and that is the ordering guarantee's last mile.** §6: *"the audit record
is appended (P1, §8.2) **before** `Released` is returned. There is no interval in which content is
releasable and unaudited."* `append_event` returns `cursor.lastrowid`, which exists only after the
row does, so a mint that has no `audit_id` to pass is a mint whose audit record was never written —
and SQLite refuses the row rather than P7 remembering to. The test proves it against the substrate,
by catching `sqlite3.IntegrityError`, not against P7's restraint.

**The `release_id` is `secrets.token_hex(16)` and the ledger, not the entropy, is the authority.**
A caller that holds a legitimate id can spend it; entropy does not change that. What entropy buys is
that a caller holding *one* id cannot enumerate its way to another one minted for a different call
in the same run. The unforgeability property is the ledger lookup — `ReleaseNotIssued` — and the
test says so in its own name.

**`spent_at` is the only wall-clock read in these three tasks, and it is reported.** The skeleton
fixes `consume_release`'s signature and it carries no clock, so the module reads one. That is
tolerable precisely because the ledger is not a fact: the authoritative time of a model call is the
audit record's `observed_at`, which the caller supplies, and nothing in P7 reads `spent_at` back as
evidence. Widening the published signature to take an `observed_at` would have been the alternative
and it was rejected because the signature is a contract with the Task 19/20 authors and with P8.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_binding.py
"""Done-means 5, and layer L1 of Done-means 3.

SPEC §6: "A release is consumed on first transport use." "The binding tuple is
(model_target, prompt_fingerprint, policy_version)." And the property the part
exists for: "a call that bypasses P7 is not a policy violation to be caught in
review -- it is a call that cannot be constructed."

The last one is testable in exactly one way and this file does it: build a
`Released` by hand, with a `release_id` the gate never minted, and show that
spending it fails. The dataclass is constructible. It is simply inert.
"""
import inspect
import sqlite3
from dataclasses import FrozenInstanceError

import pytest

from privacy.binding import (
    BINDING_TERMS, BindingMismatch, ReleaseAlreadySpent, ReleaseNotIssued,
    consume_release, mint_release,
)
from privacy.policy import Policy
from privacy.release import RELEASED_FIELDS, ModelTarget, Released

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
FINGERPRINT = "fp-1"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
OTHER_CLOUD = ModelTarget(locality="cloud", model_id="acme-small", provider="Acme")
LOCAL = ModelTarget(locality="local", model_id="llama-3-8b", provider="local")

_TYPED_DEFAULTS = {
    "release_id": "release-never-minted",
    "audit_id": 1,
    "policy_version": "policy-1",
    "materialised_items": (),
    "redaction_manifest": (),
    "model_target": CLOUD,
}


def a_released(**over) -> Released:
    """Built from `RELEASED_FIELDS`, never from a literal keyword list.

    Task 11 owns SPEC §6's six field names. Constructing from the published tuple
    means a field this task never reads can be respelled without breaking it, while
    a field it DOES read disappearing fails here, at the seam that cares.
    """
    missing = [name for name in RELEASED_FIELDS if name not in _TYPED_DEFAULTS]
    assert not missing, (
        f"RELEASED_FIELDS names {missing} and this test has no value for them; "
        "SPEC §6 changed and Task 12 needs a value, not a default")
    values = {name: _TYPED_DEFAULTS[name] for name in RELEASED_FIELDS}
    values.update(over)
    return Released(**values)


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


def mint(conn, *, policy=None, model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
         audit_id=1, minted_at=FIXED_CLOCK) -> str:
    return mint_release(conn, policy=policy or a_policy(), model_target=model_target,
                        prompt_fingerprint=prompt_fingerprint, audit_id=audit_id,
                        minted_at=minted_at)


def spend(conn, released, **over) -> None:
    base = dict(model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
                policy_version="policy-1")
    base.update(over)
    consume_release(conn, released, **base)


@pytest.fixture()
def minted(p7_conn) -> Released:
    """One live release, bound to CLOUD / fp-1 / policy-1."""
    return a_released(release_id=mint(p7_conn))


# --- minting ----------------------------------------------------------------

def test_a_minted_release_is_recorded_in_the_ledger(p7_conn, minted):
    row = p7_conn.execute("SELECT * FROM release_ledger WHERE release_id = ?",
                          (minted.release_id,)).fetchone()
    assert row is not None
    assert row["prompt_fingerprint"] == FINGERPRINT
    assert row["policy_version"] == "policy-1"
    assert row["audit_id"] == 1
    assert row["minted_at"] == FIXED_CLOCK
    assert row["spent_at"] is None


def test_two_mints_with_the_same_binding_get_different_ids(p7_conn):
    # The ledger is the authority and the entropy is not. What the entropy buys is
    # that a caller holding one id cannot walk to another one minted in the same run.
    first, second = mint(p7_conn), mint(p7_conn)
    assert first != second
    assert p7_conn.execute("SELECT count(*) c FROM release_ledger").fetchone()["c"] == 2


def test_a_mint_without_an_audit_record_is_refused_by_the_substrate(p7_conn):
    # SPEC §6's ordering guarantee, at its last mile: "the audit record is appended
    # ... BEFORE `Released` is returned." `append_event` returns `lastrowid`, which
    # exists only after the row does, so a mint with no audit_id is a mint whose
    # audit record was never written. SQLite refuses it; P7 does not have to remember.
    with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
        mint(p7_conn, audit_id=None)


# --- single use -------------------------------------------------------------

def test_a_release_is_consumed_on_first_use(p7_conn, minted):
    # SPEC §6: "A release is consumed on first transport use."
    spend(p7_conn, minted)
    row = p7_conn.execute("SELECT spent_at FROM release_ledger WHERE release_id = ?",
                          (minted.release_id,)).fetchone()
    assert row["spent_at"] is not None


def test_a_second_use_of_the_same_release_is_refused(p7_conn, minted):
    spend(p7_conn, minted)
    with pytest.raises(ReleaseAlreadySpent):
        spend(p7_conn, minted)


def test_consuming_writes_no_event(p7_conn, minted):
    # C4: the gate writes its audit record and nothing else. The spend is a state
    # change on P7's own capability row, not a second entry in the one log; Task 10's
    # `model_release` is the record that a call was authorized.
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    spend(p7_conn, minted)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


# --- the three binding terms, one test each ---------------------------------

def test_a_different_model_target_is_refused(p7_conn, minted):
    # §8.4's audit record must show "which model received the data". A payload
    # replayable against another model makes that field false.
    replayed = a_released(release_id=minted.release_id, model_target=OTHER_CLOUD)
    with pytest.raises(BindingMismatch):
        spend(p7_conn, replayed, model_target=OTHER_CLOUD)


def test_a_different_prompt_fingerprint_is_refused(p7_conn, minted):
    # §8.4's sixth audit field is "the prompt fingerprint"; B2 puts `call_site`
    # inside it, so one fingerprint is one call site and one prompt.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, minted, prompt_fingerprint="fp-2")


def test_a_different_policy_version_is_refused(p7_conn, minted):
    # SPEC §6: "a release spent under a different policy version is not [the same
    # authorization]". This is the term that makes revocation forward-only rather
    # than retroactive -- see the policy-change test below.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, a_released(release_id=minted.release_id,
                                  policy_version="policy-2"),
              policy_version="policy-2")


def test_a_binding_mismatch_does_not_spend_the_release(p7_conn, minted):
    # A mis-wired caller must not be able to destroy an authorization the user
    # granted, and a release that never reached a model must not be recorded as one
    # that did. The binding is checked before the spend, never after.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, minted, prompt_fingerprint="fp-2")
    assert p7_conn.execute(
        "SELECT spent_at FROM release_ledger WHERE release_id = ?",
        (minted.release_id,)).fetchone()["spent_at"] is None
    spend(p7_conn, minted)


def test_a_released_whose_echo_disagrees_with_the_call_is_refused(p7_conn, minted):
    # `Released` echoes `model_target` and `policy_version` (SPEC §6). If the echo
    # and the checked binding could disagree, one of the audit record's two fields
    # would be false for whichever the transport actually used.
    with pytest.raises(BindingMismatch):
        consume_release(p7_conn, a_released(release_id=minted.release_id,
                                            model_target=LOCAL),
                        model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
                        policy_version="policy-1")


# --- audit_id is not a binding term -----------------------------------------

def test_the_binding_terms_are_the_specs_three(p7_conn):
    assert BINDING_TERMS == ("model_target", "prompt_fingerprint", "policy_version")
    assert "audit_id" not in BINDING_TERMS


def test_two_releases_differing_only_in_audit_record_both_consume(p7_conn):
    # SPEC §6, constructed exactly: "two releases differing only in audit record are
    # the same authorization".
    first = a_released(release_id=mint(p7_conn, audit_id=11), audit_id=11)
    second = a_released(release_id=mint(p7_conn, audit_id=12), audit_id=12)
    spend(p7_conn, first)
    spend(p7_conn, second)


def test_every_binding_term_is_a_ledger_column(p7_conn):
    # The comparison is driven by BINDING_TERMS. A fourth term added to the tuple
    # without a column to hold it fails here rather than silently comparing nothing.
    columns = {row[1] for row in p7_conn.execute("PRAGMA table_xinfo(release_ledger)")}
    assert set(BINDING_TERMS) <= columns


# --- unforgeability ---------------------------------------------------------

def test_a_hand_constructed_released_is_inert(p7_conn):
    # THE test. "A call that bypasses P7 is not a policy violation to be caught in
    # review -- it is a call that cannot be constructed."
    with pytest.raises(ReleaseNotIssued):
        spend(p7_conn, a_released(release_id="release-deadbeef"))


def test_constructing_a_released_is_permitted_and_useless(p7_conn):
    # The dataclass is not defended and does not need to be. Instantiating it is a
    # normal Python act that buys nothing, which is a stronger property than a
    # constructor that raises: nothing has to guess where the caller came from.
    forged = a_released(release_id="release-deadbeef")
    assert forged.release_id == "release-deadbeef"
    with pytest.raises(FrozenInstanceError):
        forged.release_id = "release-something-else"
    assert p7_conn.execute(
        "SELECT count(*) c FROM release_ledger WHERE release_id = ?",
        ("release-deadbeef",)).fetchone()["c"] == 0


def test_a_refused_consume_leaves_the_ledger_untouched(p7_conn, minted):
    before = p7_conn.execute("SELECT count(*) c FROM release_ledger").fetchone()["c"]
    with pytest.raises(ReleaseNotIssued):
        spend(p7_conn, a_released(release_id="release-deadbeef"))
    assert p7_conn.execute(
        "SELECT count(*) c FROM release_ledger").fetchone()["c"] == before


# --- the policy-version term is what makes revocation forward-only ----------

def test_a_release_minted_before_a_policy_change_still_consumes_against_its_own_version(p7_conn):
    # Task 15's `revoke` mints a new policy version and asserts `effective_from`
    # affects "future gate calls only". That property lives HERE: the ledger row
    # carries the version the release was minted under, so a token issued before the
    # revocation is still spendable against policy-1, while a call presented under
    # policy-2 is a different authorization. The other half -- that a request made
    # AFTER the revocation denies with `policy_revoked` -- is Task 13's.
    early = a_released(release_id=mint(p7_conn, policy=a_policy(policy_version="policy-1")))
    spend(p7_conn, early, policy_version="policy-1")
    late = a_released(release_id=mint(p7_conn, policy=a_policy(policy_version="policy-1")))
    with pytest.raises(BindingMismatch):
        spend(p7_conn, a_released(release_id=late.release_id,
                                  policy_version="policy-2"),
              policy_version="policy-2")


# --- shape ------------------------------------------------------------------

def test_mint_takes_the_policy_and_consume_takes_the_echo():
    # SPEC §6: "the gate owns the policy, so the caller does not supply this value,
    # it echoes it." The minter is inside the gate and holds the object; the
    # transport is outside it and can only echo a string.
    minting = inspect.signature(mint_release).parameters
    assert "policy" in minting and "policy_version" not in minting
    spending = inspect.signature(consume_release).parameters
    assert "policy_version" in spending and "policy" not in spending


def test_the_ledger_holds_no_content(p7_conn):
    # `excerpts_included` is "(observation_key, span) pairs ... not a second copy of
    # the text" (SPEC §7). A ledger that stored the payload would be that second
    # copy, in a table with no reason to have one.
    columns = {row[1] for row in p7_conn.execute("PRAGMA table_xinfo(release_ledger)")}
    assert columns == {"release_id", "model_target", "prompt_fingerprint",
                       "policy_version", "audit_id", "minted_at", "spent_at"}


def test_consume_release_is_the_only_spender():
    # Repo-wide, this is Task 21's. Here it is the module's own namespace: there is
    # no second function in `binding` that can mark a release spent.
    import privacy.binding as module
    published = {name for name, value in vars(module).items()
                 if not name.startswith("_") and callable(value)
                 and getattr(value, "__module__", None) == module.__name__}
    assert published == {"mint_release", "consume_release", "ReleaseNotIssued",
                         "ReleaseAlreadySpent", "BindingMismatch"}


def test_p7_adds_no_delete_trigger_to_its_own_ledger(p7_conn):
    # Task 15 counts the tables carrying `BEFORE DELETE ... RAISE(ABORT)` and asserts
    # THIRTEEN. A fourteenth here would fail a sibling task. §8.2's R6 binds `events`;
    # the ledger is a capability record and P7 does not extend R6 by imitation.
    triggers = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'trigger' "
        "AND tbl_name = 'release_ledger'")}
    assert triggers == set()
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_binding.py -v`
Expected: FAIL — `ImportError: cannot import name 'BINDING_TERMS' from 'privacy.binding'` (the
module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/binding.py`**

```python
# src/privacy/binding.py
"""The release ledger: what makes `Released` a capability rather than a value.

SPEC §6 states the property and the reason in one breath: "Binding and single use
exist to keep the audit record truthful. §8.4 requires the record to show *which
model received the data* and *the prompt fingerprint*; a payload that could be
replayed against a different model or under a different prompt would make both
fields false. A release is consumed on first transport use."

Three decisions, each forced rather than chosen:

- **The ledger is the authority, not the entropy.** `ReleaseNotIssued` is what makes
  a hand-constructed `Released` inert, and it is a lookup. The 128 bits are so that a
  caller holding one id cannot enumerate its way to another minted in the same run.
- **The binding is checked before the spend, and a mismatch spends nothing.** A
  mis-wired caller must not be able to burn an authorization the user granted, and a
  release that never reached a model must not be recorded as one that did.
- **`audit_id` is carried and never compared.** SPEC §6: "two releases differing only
  in audit record are the same authorization, while a release spent under a different
  policy version is not." It is `NOT NULL` because `append_event` returns
  `cursor.lastrowid`, which exists only after the audit row does -- so a mint with no
  audit_id is a mint whose audit record was never written, and SQLite refuses it.

This module imports `privacy.release` under `TYPE_CHECKING` only. It never constructs
a `Released` -- `mint_release` returns a `str` and the facade builds the value -- so
the need for the type is annotation-only, and the guard is what lets `release.py`
import nothing from here while `gate.py` imports both.
"""
from __future__ import annotations

import dataclasses
import secrets
import sqlite3
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from evidence_shape.canonical import canonical_json

from privacy.policy import Policy

if TYPE_CHECKING:  # pragma: no cover - annotation only; see the module docstring
    from privacy.release import ModelTarget, Released

#: SPEC §6, B2: "The binding tuple is (model_target, prompt_fingerprint,
#: policy_version)." Three terms, and `audit_id` is deliberately not one.
BINDING_TERMS: tuple[str, str, str] = (
    "model_target", "prompt_fingerprint", "policy_version",
)

#: P7's third table, inside P1's single local database (§0). No `BEFORE DELETE`
#: trigger: §8.2's R6 binds `events`, and this is a capability record, not a
#: provenance record. Task 15 counts the guarded tables and asserts thirteen.
RELEASE_LEDGER_DDL: str = """
CREATE TABLE IF NOT EXISTS release_ledger (
    release_id         TEXT PRIMARY KEY,
    model_target       TEXT NOT NULL,
    prompt_fingerprint TEXT NOT NULL,
    policy_version     TEXT NOT NULL,
    audit_id           INTEGER NOT NULL,
    minted_at          TEXT NOT NULL,
    spent_at           TEXT
);
"""


class ReleaseNotIssued(Exception):
    """The `release_id` is not in the ledger, so the gate never minted it.

    This is the refusal that makes the door real. A caller may construct a
    `Released` -- it is an ordinary frozen dataclass -- and doing so buys nothing.
    """


class ReleaseAlreadySpent(Exception):
    """SPEC §6: "A release is consumed on first transport use.\""""


class BindingMismatch(Exception):
    """The call does not match the terms the release was minted under.

    Raised before the spend and never after, so a mismatched call leaves the
    authorization intact.
    """


def _target_form(model_target: ModelTarget) -> str:
    """One stored form per model target.

    `canonical_json` over `dataclasses.asdict` rather than `str()`: §8.4's audit
    field is "which model received the data", and a hosted model is identified by
    provider AND id. A form that dropped either would let two different targets
    compare equal.
    """
    return canonical_json(dataclasses.asdict(model_target))


def _utcnow() -> str:
    """The ledger's own clock.

    The published `consume_release` signature carries no `observed_at`, and it is a
    contract with P8's transport. That is tolerable because `spent_at` is not a fact:
    the authoritative time of a model call is the audit record's `observed_at`, which
    the caller supplies, and nothing in P7 reads this column back as evidence.
    """
    return datetime.now(timezone.utc).isoformat()


def mint_release(conn: sqlite3.Connection, *, policy: Policy,
                 model_target: ModelTarget, prompt_fingerprint: str,
                 audit_id: int, minted_at: str) -> str:
    """Record one authorization and return its single-use id.

    Takes the `Policy` object, not a `policy_version` string: SPEC §6 says "the gate
    owns the policy, so the caller does not supply this value, it echoes it", and the
    minter is inside the gate. `consume_release` takes the echo.
    """
    release_id = "release-" + secrets.token_hex(16)
    conn.execute(
        "INSERT INTO release_ledger (release_id, model_target, prompt_fingerprint, "
        "policy_version, audit_id, minted_at, spent_at) "
        "VALUES (?, ?, ?, ?, ?, ?, NULL)",
        (release_id, _target_form(model_target), prompt_fingerprint,
         policy.policy_version, audit_id, minted_at),
    )
    return release_id


def consume_release(conn: sqlite3.Connection, released: Released, *,
                    model_target: ModelTarget, prompt_fingerprint: str,
                    policy_version: str) -> None:
    """Spend one release, once, against the terms it was minted under.

    Order: issued, then bound, then spent. Checking the binding after the spend
    would burn a token on a call that was never authorized for that model, and
    would report "already spent" for what is really a forgery-shaped event.
    """
    row = conn.execute("SELECT * FROM release_ledger WHERE release_id = ?",
                       (released.release_id,)).fetchone()
    if row is None:
        raise ReleaseNotIssued(
            f"{released.release_id!r} is not in the release ledger; the gate never "
            "minted it. A `Released` constructed outside `Gate.release` carries no "
            "authorization -- SPEC §6, and the reason a bypassing call cannot be "
            "constructed rather than merely being disallowed"
        )
    call = {
        "model_target": _target_form(model_target),
        "prompt_fingerprint": prompt_fingerprint,
        "policy_version": policy_version,
    }
    differing = [term for term in BINDING_TERMS if row[term] != call[term]]
    if differing:
        raise BindingMismatch(
            f"{released.release_id!r} was minted under different {differing}; SPEC §6 "
            "binds a release to (model_target, prompt_fingerprint, policy_version) so "
            "that §8.4's 'which model received the data' and 'the prompt fingerprint' "
            "stay true of the call that actually happened"
        )
    echoed = {
        "model_target": _target_form(released.model_target),
        "policy_version": released.policy_version,
    }
    disagreeing = [term for term, value in echoed.items() if call[term] != value]
    if disagreeing:
        raise BindingMismatch(
            f"{released.release_id!r} echoes {disagreeing} that the call does not "
            "use; the echo and the binding must agree or one of §8.4's audit fields "
            "is false for whichever the transport actually used"
        )
    spent = conn.execute(
        "UPDATE release_ledger SET spent_at = ? "
        "WHERE release_id = ? AND spent_at IS NULL",
        (_utcnow(), released.release_id),
    )
    if spent.rowcount != 1:
        raise ReleaseAlreadySpent(
            f"{released.release_id!r} was already consumed; SPEC §6: 'A release is "
            "consumed on first transport use.' The check and the mark are one "
            "statement so that single use survives a second caller arriving between "
            "them"
        )
```

- [ ] **Step 4: Add the ledger to `src/privacy/schema.py`**

Task 5 created `create_privacy_schema(conn)` and it is the one place P7's schema is applied, so a
caller does not have to know which modules own tables. The DDL text stays with the module that owns
the table's semantics; `schema.py` executes it. The import direction is `schema` → `binding`, which
is acyclic because `binding` imports nothing from `schema`.

```python
# src/privacy/schema.py  --  add the import and one executescript line
from privacy.binding import RELEASE_LEDGER_DDL
```

```python
    # inside create_privacy_schema(conn), alongside Task 5's policy and consent-grant
    # tables. Task 12's ledger is what makes `Released` single-use (SPEC §6).
    conn.executescript(RELEASE_LEDGER_DDL)
```

- [ ] **Step 5: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_binding.py -v`
Expected: PASS — 21 passed

- [ ] **Step 6: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–12 green, and the 1300 P1–P5 tests still green (P7 modified no file
belonging to another part).

- [ ] **Step 7: Commit**

```bash
git add src/privacy/binding.py src/privacy/schema.py tests/p7/test_p7_binding.py
git commit -m "feat(P7): the release ledger, its three binding terms, and single use"
```

---
