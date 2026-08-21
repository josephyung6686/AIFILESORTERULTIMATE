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
| `append_audit(..., extra: Mapping[str, object] \| None = None)` — one keyword on Task 10's writer | 13, 14 | SPEC §7 enumerates a **release** record. A denial's `reason` and `remedy_options[]` and a consent request's `requirement` and `options` have no field in it, and §8.6 requires the product to show *"what has been deferred, and why"*. `extra` merges into the same canonical-JSON `explanation` as `EXPLANATION_FIELDS`, which is §8.2's own *"structured explanation or evidence reference"* slot. **Task 10's author owns this keyword.** |
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

Two lines are added to Task 5's file and nothing else in it changes — the import at module
level, and the execution inside `create_privacy_schema`, alongside Task 5's own policy and
consent-grant tables:

```text
src/privacy/schema.py

  module level, with the other imports
      from privacy.binding import RELEASE_LEDGER_DDL

  inside create_privacy_schema(conn), after Task 5's own executescript calls
      # Task 12's ledger is what makes `Released` single-use (SPEC §6).
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

### Task 13: The eight denials

**Files:**
- Create: `src/privacy/denial.py`
- Test: `tests/p7/test_p7_denials.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.DENIAL_REASONS`, `.check_denial_reason(value) -> str`,
  `.OutOfVocabulary`, `privacy.classification.ClassificationRecord`,
  `.resolve_class(record) -> str`, `privacy.policy.Policy`,
  `privacy.items.AlwaysLocalRequested`, `.WholeDocumentRequested`,
  `privacy.audit.AuditRecord`, `.AUDIT_FIELDS`,
  `.append_audit(conn, record, *, author, component_version) -> int`,
  `privacy.authorship.SUBSYSTEM`, `privacy.release.Denied` (run time — see the import-direction
  section), `database_agent.budget.get_ceiling(conn, key) -> int | None`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`denial.py`):
  - `PROTECTED_RECORDS_TEMPLATE: str = "Protected Records"` — §7.3's literal name.
  - `REVOKED_SCOPE_KEY: str = "scope"` — the key Task 15's `revoke` writes into `explanation`.
  - `DENIAL_ORDER: tuple[str, ...]` — the eight, in evaluation order.
  - `DECIDABLE_FROM_REQUEST: frozenset[str]` — the six that need no content read.
  - `RemedyOption` — frozen: `action: str`, `detail: str`.
  - `MalformedDenial(ValueError)`.
  - `deny(reason, *, explanation, remedy_options, evidence_refs) -> Denied`.
  - `first_reason(reasons) -> str | None`.
  - Predicates: `mode_forbids(operation_mode, locality) -> bool`,
    `policy_revoked_for(conn, policy, scope) -> bool`,
    `unclassified_denies(*, locality, local_calls_on_unclassified) -> bool`,
    `is_protected_records(template_name) -> bool`,
    `protected_cloud_denies(*, protected, locality, operation_mode, scope, granted_scopes) -> bool`,
    `over_dossier_ceiling(conn, *, measured_tokens) -> bool`.
  - Eight builders: `deny_mode_forbids_target`, `deny_policy_revoked`, `deny_always_local_item`,
    `deny_unclassified`, `deny_protected_records_template`, `deny_protected_cloud_target`,
    `deny_whole_document_requested`, `deny_dossier_over_budget`.
  - `record_denial(conn, denied, *, request, policy, classification, content_hashes, user_id,
    component_version, observed_at) -> int`.

**Done-means:** 6.

**This is the ordinary path and it is written as one.** The detector is unwritten (D2). No task in
any plan produces a rule set. So on a real corpus, `Gate.release` is asked about a file with no
`ClassificationRecord`, `resolve_class(None)` returns `unreadable_unclassified`, and the call is
**denied**. That is not a degraded mode; it is what a correct locked door does when nobody has been
given a key. The consequences run through this whole task: `deny_unclassified` gets the longest
explanation and the most remedy options; the `unclassified` test is the one that also proves absence
never resolves to `public_low`; and the audit-record test uses an unclassified file, because that is
what the audit log will actually be full of.

**The eight reasons need a total order, and it is `DENIAL_ORDER`.** The skeleton requires eight
tests *"each reaching **exactly** that reason and no other"*, and four of the eight overlap on real
inputs — a protected file with a cloud target under `offline` satisfies both `mode_forbids_target`
and `protected_cloud_target`; an unclassified protected file satisfies `unclassified` and
`protected_cloud_target`; a `Protected Records` file satisfies both of the latter. "Exactly one" is
unmeetable without saying which wins. The order and the reason for each position:

```text
1  mode_forbids_target          the mode is outermost. §8.4: offline is "No content leaves the
                                device"; a cloud target is refused before anything about the file
                                is consulted. This is also Done-means 13's asserted reason.
2  policy_revoked               with no authorizing policy for the scope there is nothing to
                                evaluate the remaining rules against.
3  always_local_item            §8.4: "Nothing in this set can be named as a releasable item kind."
                                Decidable from the item kind, and true of every file.
4  unclassified                 §8.4 makes classification "a precondition of escalation". With no
                                record there is no `protected` flag to read, so every rule below
                                this line is literally unevaluable above it.
5  protected_records_template   §7.3 binds LOCAL calls too, so it must precede the cloud rule or a
                                local call on a Protected Records file would pass.
6  protected_cloud_target       protected + cloud, under a mode that otherwise permits cloud.
7  whole_document_requested     needs the resolved unit length, so it is the first rule that
                                requires the file's content.
8  dossier_over_budget          M9's backstop, last: P8 measured and ran its ladder before calling.
```

**The principle that orders them, and `DECIDABLE_FROM_REQUEST` is it in data form: no denial that
can be decided from the request alone may be decided after one that requires reading the file.**
A gate that materialised an excerpt and *then* discovered the mode forbade the call has read a
sensitive file for a call that was never going to happen. Six of the eight are decidable from the
request, the policy and a row lookup; two — `whole_document_requested` and `dossier_over_budget` —
need the resolved text. A test asserts every member of the first set precedes every member of the
second, so a future reordering that puts a content-reading check first is a red test.

**Every denial appends exactly one `model_release_denied`, and the gate writes nothing else.** The
audit obligation is §8.2's *"Every significant event affecting a file should be preserved in an
append-only provenance log"* and SPEC §7's *"Denials and consent requests are also appended."* The
builders are pure and the append is one function, because the audit record needs the request and the
policy and a builder sees neither; a builder that took them would compose SPEC §7's record eight
times over, and Task 10 owns that record once. `Gate.release` calls a builder and then
`record_denial`; that wiring is Task 11's.

**`AuditRecord.file_sensitivity` is where `unreadable_unclassified` belongs, and
`files.sensitivity_state` is where it must never appear.** D2: *"`Unreadable or unclassified` is a
GATE OUTCOME, not a file fact. It lives on the release decision and never in that column, so
'nothing has looked' can never be read as 'this file carries nothing'."* `record_denial` computes
the field with `classification.resolve_class(record)` — the same function, so the outcome is not
re-derived — and one test asserts the column is exactly as the denial found it. That test proves C4
and D2 with one assertion, which is why it is written as one test and not two.

**`dossier_over_budget` reads P1's ceiling and counts no tokens.** `get_ceiling(conn,
"model.max_dossier_tokens_per_call")` returns `int | None`, and `None` is the ordinary state.
**An unset ceiling cannot deny**, because P7 owns no number: SPEC *Deferred* puts every numeric
ceiling outside this contract and Task 21 asserts none appears in `src/privacy/`. The size itself is
the **caller's** measurement, passed as `measured_tokens` with no default, for the same reason the
redaction transform is injected with no default — P7 has no tokenizer and inventing one would invent
a number. And the check reads P1's stored ceiling, never `request.max_dossier_tokens`, which is only
*"the caller's echo of it (M9)"*: a caller must not be able to raise its own ceiling by echoing a
larger one. Its test says in its own docstring that this denial is **an M9 backstop that should
never fire in a correct pipeline**, so a later reader does not delete the check on the grounds that
P8 already ran the ladder.

**`policy_revoked` is "granted and then withdrawn", not "never granted".** Never-granted is
`protected_cloud_target` or `mode_forbids_target`, and its remedy is *ask*. Withdrawn is a different
fact with a different remedy and §8.7's negative-feedback rule attached — the user has already said
no once, so the option is offered and never re-proposed automatically. The predicate is therefore
two-sided: the current policy carries no grant for the scope **and** the log holds a
`consent_revoked` for it. A re-grant puts the scope back in `policy.consent_grants` and the denial
stops firing, which is what makes revocation forward-only rather than permanent. The scope is read
from the `consent_revoked` explanation under the key `"scope"` — verified against the written
[`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md), where `revoke` composes
`canonical_json({"scope": scope, "revoked_policy_version": …})` — and pinned as
`REVOKED_SCOPE_KEY` so a rename is a red test on both sides.

**`unclassified_denies` is parameterised on locality and the parameter has no default.** Open
question 5: *"Does `unreadable_unclassified` permit a *local* model call? … Reading escalation
strictly denies local calls on unclassified files, which may block exactly the OCR-opaque
screenshots §2.7 and §7.8 want a model to interpret."* Unanswered, so
`local_calls_on_unclassified` is a required keyword and calling without it is a `TypeError` the
test asserts. P7 supplies no answer and Task 21 holds the question open.

**`always_local_item` and `whole_document_requested` are translations, not re-derivations.** Task 7
refuses those at construction with `AlwaysLocalRequested` and `WholeDocumentRequested`. Task 13's two
builders take the caught exception and turn it into the gate's `Denied`, so the rule lives in one
place and the gate's answer carries the item that failed. A builder that re-decided which names are
always-local would be a second copy of §8.4's nine.

**Remedy options are composed per denial and are deliberately not a closed vocabulary.** §8.6 names
four ladder rungs for an over-budget dossier; §8.4 names four consent options for a sensitive text
request; §8.6 names deferral and review for an exhausted budget. Collapsing those into one
`REMEDY_ACTIONS` tuple would invent a fifth thing that no section states. `denial.py` publishes no
such enumeration and Task 21 asserts none exists. What is enforced is presence: §8.6 requires the UI
to show *"what has been deferred, and why"*, and a denial with no legitimate alternative is a dead
end the user cannot act on, so `deny` refuses an empty `remedy_options`.

**M14 is not re-checked here.** `Denied.evidence_refs` carries whatever the classification carried,
and the observation-key-versus-id rule is Task 3's on `ClassificationRecord.evidence_refs`. `deny`
validates that each ref is a non-empty string and no more; a second copy of M14's shape rule is a
second place for it to drift.

**One finding for Task 10, reported rather than worked around.** `events` has one `file_id` column,
so a group-scoped denial cannot put all of its files in it. `record_denial` sets the column when the
call is about exactly one file and always stores the full tuple as `file_ids` in the explanation
JSON. **`audit_records_for(conn, file_id=…)` must therefore match the explanation's `file_ids` and
not only the column**, or Task 15's `prior_releases` under-reports every group-scoped release.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_denials.py
"""Done-means 6 -- all eight reasons, and the one that is the ordinary case.

The detector is unwritten (D2), so on a real corpus every file resolves to
`Denied(unclassified)`. This file is written for that: `unclassified` gets the
longest section, and the audit-record tests run against an unclassified file
because that is what the log will actually be full of.

SPEC §6's eight: protected_cloud_target | unclassified | policy_revoked |
protected_records_template | whole_document_requested | dossier_over_budget |
always_local_item | mode_forbids_target.
"""
import json

import pytest

from database_agent.budget import CEILING_KEYS, set_ceiling
from database_agent.events import append_event
from database_agent.files_table import get_file, record_file

from privacy.audit import AUDIT_FIELDS, audit_record
from privacy.authorship import CONSENT_REVOKED, MODEL_RELEASE_DENIED, SUBSYSTEM
from privacy.classification import ClassificationRecord
from privacy.denial import (
    DECIDABLE_FROM_REQUEST, DENIAL_ORDER, PROTECTED_RECORDS_TEMPLATE,
    REVOKED_SCOPE_KEY, MalformedDenial, RemedyOption, deny,
    deny_always_local_item, deny_dossier_over_budget, deny_mode_forbids_target,
    deny_policy_revoked, deny_protected_cloud_target,
    deny_protected_records_template, deny_unclassified,
    deny_whole_document_requested, first_reason, is_protected_records,
    mode_forbids, over_dossier_ceiling, policy_revoked_for,
    protected_cloud_denies, record_denial, unclassified_denies,
)
from privacy.items import AlwaysLocalRequested, WholeDocumentRequested
from privacy.policy import Policy
from privacy.release import REQUEST_FIELDS, Denied, ModelCallRequest, ModelTarget, Target
from privacy.vocabulary import DENIAL_REASONS, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
CEILING_KEY = "model.max_dossier_tokens_per_call"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
LOCAL = ModelTarget(locality="local", model_id="llama-3-8b", provider="local")
DETECTOR_KEYS = (
    "sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd",
)

_REQUEST_DEFAULTS = {
    "stage": "grouping",
    "target": Target(file_ids=("file-1",), group_id=None),
    "model_target": CLOUD,
    "requested_items": (),
    "prompt_template_id": "template-1",
    "prompt_fingerprint": "fp-1",
    "max_dossier_tokens": 4000,
}


def a_request(**over) -> ModelCallRequest:
    """Built from `REQUEST_FIELDS`; Task 11 owns SPEC §6's seven names."""
    missing = [name for name in REQUEST_FIELDS if name not in _REQUEST_DEFAULTS]
    assert not missing, (
        f"REQUEST_FIELDS names {missing} and this test has no value for them; "
        "SPEC §6 changed and Task 13 needs a value, not a default")
    values = {name: _REQUEST_DEFAULTS[name] for name in REQUEST_FIELDS}
    values.update(over)
    return ModelCallRequest(**values)


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
def file_id(p7_conn, tmp_path) -> str:
    """A real P1 row, because the denial must be shown NOT to write to it."""
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


def all_eight() -> dict[str, Denied]:
    """One built `Denied` per reason, so the audit test can parameterise over them."""
    return {
        "mode_forbids_target": deny_mode_forbids_target(
            operation_mode="offline", model_target=CLOUD, file_ids=("file-1",)),
        "policy_revoked": deny_policy_revoked(
            scope="Academics", policy=a_policy(consent_grants=()),
            file_ids=("file-1",)),
        "always_local_item": deny_always_local_item(
            AlwaysLocalRequested("GPS"), file_ids=("file-1",)),
        "unclassified": deny_unclassified(
            file_ids=("file-1",), locality="cloud", completeness=None),
        "protected_records_template": deny_protected_records_template(
            file_ids=("file-1",), model_target=LOCAL),
        "protected_cloud_target": deny_protected_cloud_target(
            file_ids=("file-1",), operation_mode="hybrid", scope="Academics",
            evidence_refs=DETECTOR_KEYS),
        "whole_document_requested": deny_whole_document_requested(
            WholeDocumentRequested("span 0-4096 covers the whole unit"),
            file_ids=("file-1",)),
        "dossier_over_budget": deny_dossier_over_budget(
            measured_tokens=9000, ceiling=4000, file_ids=("file-1",)),
    }


# --- the order, and the principle behind it ---------------------------------

def test_denial_order_is_a_permutation_of_the_vocabulary():
    assert set(DENIAL_ORDER) == set(DENIAL_REASONS)
    assert len(DENIAL_ORDER) == len(DENIAL_REASONS) == 8


def test_nothing_that_needs_content_is_decided_before_something_that_does_not():
    # The principle: a gate that materialised an excerpt and THEN discovered the mode
    # forbade the call has read a sensitive file for a call that was never going to
    # happen. Six reasons are decidable from the request; two need the resolved text.
    assert DECIDABLE_FROM_REQUEST < set(DENIAL_REASONS)
    needs_content = set(DENIAL_REASONS) - DECIDABLE_FROM_REQUEST
    assert needs_content == {"whole_document_requested", "dossier_over_budget"}
    last_cheap = max(DENIAL_ORDER.index(r) for r in DECIDABLE_FROM_REQUEST)
    first_costly = min(DENIAL_ORDER.index(r) for r in needs_content)
    assert last_cheap < first_costly


def test_dossier_over_budget_is_last():
    # M9: P8 measures and runs §8.6's ladder BEFORE calling. The gate is "the last
    # place to catch a caller that skipped its ladder", so it is checked last.
    assert DENIAL_ORDER[-1] == "dossier_over_budget"


def test_first_reason_returns_none_when_nothing_triggered():
    assert first_reason(()) is None
    assert first_reason(set()) is None


def test_mode_outranks_protected_cloud_target():
    # The negative-tests table: protected + cloud under `offline` or `local_model` is
    # `mode_forbids_target`, not `protected_cloud_target`. The mode is outermost.
    assert first_reason({"protected_cloud_target", "mode_forbids_target"}) == \
        "mode_forbids_target"


def test_unclassified_outranks_protected_cloud_target():
    # §8.4 makes classification "a precondition of escalation". With no record there
    # is no `protected` flag to read, so the rule below is literally unevaluable.
    assert first_reason({"protected_cloud_target", "unclassified"}) == "unclassified"


def test_protected_records_template_outranks_protected_cloud_target():
    # §7.3 binds local calls too, so it must precede the cloud-only rule.
    assert first_reason({"protected_cloud_target", "protected_records_template"}) == \
        "protected_records_template"


# --- 1. mode_forbids_target -------------------------------------------------

def test_mode_forbids_target_under_offline_and_local_model():
    # §8.4: "Fully offline mode: No content leaves the device; only local rules and
    # local models may run." A local model is permitted under both; a cloud one is not.
    assert mode_forbids("offline", "cloud") is True
    assert mode_forbids("local_model", "cloud") is True
    assert mode_forbids("offline", "local") is False
    assert mode_forbids("local_model", "local") is False
    assert mode_forbids("hybrid", "cloud") is False
    assert mode_forbids("cloud_assisted", "cloud") is False
    assert deny_mode_forbids_target(operation_mode="offline", model_target=CLOUD,
                                    file_ids=("file-1",)).reason == "mode_forbids_target"


# --- 2. policy_revoked ------------------------------------------------------

def test_policy_revoked_after_a_scope_is_withdrawn(p7_conn):
    # Task 15's `revoke` appends this event with `canonical_json({"scope": scope, ...})`.
    # "Granted and then withdrawn" is a different fact from "never granted": the user
    # has already said no once, so §8.7's negative feedback applies to the remedy.
    granted = a_policy()
    assert policy_revoked_for(p7_conn, granted, "Academics") is False
    append_event(p7_conn, event_type=CONSENT_REVOKED, subsystem=SUBSYSTEM,
                 component_version=COMPONENT, observed_at=LATER,
                 explanation=json.dumps({REVOKED_SCOPE_KEY: "Academics"}))
    withdrawn = a_policy(consent_grants=(), policy_version="policy-2")
    assert policy_revoked_for(p7_conn, withdrawn, "Academics") is True
    assert deny_policy_revoked(scope="Academics", policy=withdrawn,
                               file_ids=("file-1",)).reason == "policy_revoked"


def test_a_re_granted_scope_stops_denying(p7_conn):
    # Revocation is forward-only, not permanent: a new grant puts the scope back and
    # the denial stops. The ledger half -- a token minted before the revocation still
    # consuming -- is Task 12's.
    append_event(p7_conn, event_type=CONSENT_REVOKED, subsystem=SUBSYSTEM,
                 component_version=COMPONENT, observed_at=LATER,
                 explanation=json.dumps({REVOKED_SCOPE_KEY: "Academics"}))
    assert policy_revoked_for(p7_conn, a_policy(), "Academics") is False


# --- 3. always_local_item ---------------------------------------------------

def test_always_local_item_translates_task_sevens_refusal():
    # §8.4: "Nothing in this set can be named as a releasable item kind." Task 7
    # refuses at construction; this builder turns that refusal into the gate's answer
    # rather than re-deciding which of the nine names are always-local.
    caught = AlwaysLocalRequested("GPS")
    denied = deny_always_local_item(caught, file_ids=("file-1",))
    assert denied.reason == "always_local_item"
    assert "GPS" in denied.explanation


# --- 4. unclassified -- the ordinary case -----------------------------------

def test_unclassified_is_the_ordinary_denial():
    # D2: no detector exists, so every real file lands here. §8.4: "classify data into
    # handling classes before LLM escalation" makes classification a PRECONDITION.
    assert unclassified_denies(locality="cloud",
                               local_calls_on_unclassified=True) is True
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    assert denied.reason == "unclassified"


def test_absence_of_a_classification_never_resolves_to_public_low():
    # SPEC §1: "Absence of a classification resolves to `unreadable_unclassified`,
    # never to `public_low`." §8.6's rule it applies: "Cost exhaustion must never turn
    # into lower-quality automatic classification."
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    assert "unreadable_unclassified" in denied.explanation
    assert "public_low" not in denied.explanation


def test_a_local_call_on_an_unclassified_file_has_no_default():
    # Open question 5, unanswered: "Does `unreadable_unclassified` permit a LOCAL
    # model call? ... which may block exactly the OCR-opaque screenshots §2.7 and §7.8
    # want a model to interpret." The parameter is required; P7 names no winner.
    with pytest.raises(TypeError):
        unclassified_denies(locality="local")
    assert unclassified_denies(locality="local",
                               local_calls_on_unclassified=True) is False
    assert unclassified_denies(locality="local",
                               local_calls_on_unclassified=False) is True


def test_unclassified_offers_a_remedy_the_user_can_actually_take():
    # §8.6 requires the UI to show "what has been deferred, and why", and §8.6's own
    # answer to an exhausted budget is to "leave the file or group in review rather
    # than guessing". A denial nobody can act on is a dead end.
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    actions = {option.action for option in denied.remedy_options}
    assert "classify" in actions
    assert "defer" in actions


# --- 5. protected_records_template ------------------------------------------

def test_protected_records_template_denies_local_targets_too():
    # §7.3: Protected Records "should normally remain local-only and must not cause
    # filenames or content to be exposed in model prompts." No locality qualifier --
    # which is why this reason must outrank the cloud-only one.
    assert is_protected_records(PROTECTED_RECORDS_TEMPLATE) is True
    assert is_protected_records("Reading Inbox") is False
    for target in (LOCAL, CLOUD):
        denied = deny_protected_records_template(file_ids=("file-1",),
                                                 model_target=target)
        assert denied.reason == "protected_records_template"


def test_the_template_name_is_section_seven_threes_literal():
    assert PROTECTED_RECORDS_TEMPLATE == "Protected Records"


# --- 6. protected_cloud_target ----------------------------------------------

def test_protected_cloud_target_under_hybrid():
    # §8.4: "Hybrid mode: Sensitive files remain local". And SPEC §2's first protected
    # consequence: "not included in cloud-model prompts BY DEFAULT" -- the carve-out
    # that `cloud_assisted` plus an explicit grant satisfies.
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=("Academics",)) is True
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted", scope="Academics",
                                  granted_scopes=("Academics",)) is False
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted", scope="Taxes",
                                  granted_scopes=("Academics",)) is True
    assert protected_cloud_denies(protected=False, locality="cloud",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=()) is False
    assert protected_cloud_denies(protected=True, locality="local",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=()) is False
    denied = deny_protected_cloud_target(file_ids=("file-1",),
                                         operation_mode="hybrid", scope="Academics",
                                         evidence_refs=DETECTOR_KEYS)
    assert denied.reason == "protected_cloud_target"
    assert denied.evidence_refs == DETECTOR_KEYS


def test_the_corpus_area_is_the_callers_and_p7_defines_none():
    # Open question 3: "What is a 'corpus area'? ... Consent grants cannot be scoped
    # until this is named." The scope is a string the caller supplies; P7 compares it
    # and never resolves it.
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted",
                                  scope="whatever-the-caller-calls-it",
                                  granted_scopes=("whatever-the-caller-calls-it",)) \
        is False


# --- 7. whole_document_requested --------------------------------------------

def test_whole_document_requested_translates_task_sevens_refusal():
    # §8.4: "It should not send full documents where a short heading or OCR excerpt is
    # enough to resolve the question."
    caught = WholeDocumentRequested("span 0-4096 covers the whole unit")
    denied = deny_whole_document_requested(caught, file_ids=("file-1",))
    assert denied.reason == "whole_document_requested"
    assert "narrow_span" in {option.action for option in denied.remedy_options}


# --- 8. dossier_over_budget -- the backstop ---------------------------------

def test_dossier_over_budget_is_a_backstop_that_should_never_fire(p7_conn):
    """M9: P8 measures against the ceiling and runs §8.6's four-rung ladder BEFORE it
    calls the gate. A `dossier_over_budget` denial in a running pipeline is a P8
    defect to fix, not a normal outcome -- and the check stays because §8.6 forbids a
    prompt that "truncate[s] silently in a way that removes the decisive evidence"
    and the gate is the last place to catch a caller that skipped its ladder.
    Reachable in test; not reachable in a correct pipeline. Do not delete it.
    """
    assert CEILING_KEY in CEILING_KEYS
    set_ceiling(p7_conn, CEILING_KEY, 4000)
    assert over_dossier_ceiling(p7_conn, measured_tokens=9000) is True
    assert over_dossier_ceiling(p7_conn, measured_tokens=4000) is False
    denied = deny_dossier_over_budget(measured_tokens=9000, ceiling=4000,
                                      file_ids=("file-1",))
    assert denied.reason == "dossier_over_budget"
    ladder = {option.action for option in denied.remedy_options}
    assert ladder == {"summarize_deterministic_facts", "preserve_anchor_excerpts",
                      "split_the_task", "defer_the_decision"}


def test_an_unset_ceiling_cannot_deny(p7_conn):
    # `get_ceiling` returns None when nothing set it, which is the ordinary state.
    # P7 owns no number: SPEC Deferred puts "Numeric values for every ceiling"
    # outside this contract, and Task 21 asserts none appears in `src/privacy/`.
    assert over_dossier_ceiling(p7_conn, measured_tokens=10 ** 9) is False


def test_a_caller_cannot_raise_its_own_ceiling_by_echoing_a_larger_one(p7_conn):
    # `ModelCallRequest.max_dossier_tokens` is "the caller's echo of it (M9)". The
    # check reads P1's stored ceiling and never the echo.
    set_ceiling(p7_conn, CEILING_KEY, 4000)
    request = a_request(max_dossier_tokens=10 ** 6)
    assert request.max_dossier_tokens > 4000
    assert over_dossier_ceiling(p7_conn, measured_tokens=9000) is True


def test_the_measurement_is_the_callers_and_has_no_default(p7_conn):
    # P7 has no tokenizer and inventing one would invent a number -- the same
    # discipline as Task 8's injected redaction transform with no default.
    with pytest.raises(TypeError):
        over_dossier_ceiling(p7_conn)


# --- what every denial carries ----------------------------------------------

def test_every_denial_carries_a_non_empty_explanation():
    for reason, denied in all_eight().items():
        assert denied.reason == reason
        assert denied.explanation.strip(), reason


def test_every_denial_carries_at_least_one_remedy_option():
    # §8.6: the UI must show "what has been deferred, and why". A denial with no
    # legitimate alternative is a dead end the user cannot act on.
    for reason, denied in all_eight().items():
        assert denied.remedy_options, reason
        assert all(isinstance(option, RemedyOption)
                   for option in denied.remedy_options), reason


def test_a_denial_with_no_remedy_is_refused():
    with pytest.raises(MalformedDenial):
        deny("unclassified", explanation="nothing classified this file",
             remedy_options=(), evidence_refs=())


def test_a_denial_with_an_empty_explanation_is_refused():
    for blank in ("", "   "):
        with pytest.raises(MalformedDenial):
            deny("unclassified", explanation=blank,
                 remedy_options=(RemedyOption("defer", "leave it in review"),),
                 evidence_refs=())


def test_a_denial_with_an_out_of_vocabulary_reason_is_refused():
    # SPEC §1: "A value outside this set is a load error, not a fallback."
    with pytest.raises(OutOfVocabulary):
        deny("too_sensitive", explanation="made up",
             remedy_options=(RemedyOption("defer", "leave it in review"),),
             evidence_refs=())


def test_denied_carries_no_audit_id_and_no_content():
    # `Denied` is the gate's answer, not its record. The audit_id is reachable through
    # `audit_records_for`; putting it on the branch would invite a caller to treat the
    # answer as the log.
    from dataclasses import fields
    names = {field.name for field in fields(Denied)}
    assert names == {"reason", "explanation", "remedy_options", "evidence_refs"}


def test_no_two_reasons_share_one_remedy_list():
    # Proof that the remedies were authored per reason rather than defaulted from one
    # list. There is no REMEDY_ACTIONS vocabulary: §8.6 names four ladder rungs for one
    # situation and §8.4 names four consent options for another, and one enumeration
    # over both would invent a fifth thing no section states.
    lists = [tuple(sorted(option.action for option in denied.remedy_options))
             for denied in all_eight().values()]
    assert len(set(lists)) == len(lists)


# --- the audit record every denial appends ----------------------------------

def a_denial_record(conn, file_id, denied, *, classification=None, **over) -> int:
    base = dict(request=a_request(target=Target(file_ids=(file_id,), group_id=None)),
                policy=a_policy(), classification=classification,
                content_hashes=(get_file(conn, file_id)["content_hash"],),
                user_id=None, component_version=COMPONENT, observed_at=FIXED_CLOCK)
    base.update(over)
    return record_denial(conn, denied, **base)


def test_every_denial_appends_a_model_release_denied_event(p7_conn, file_id):
    # SPEC §7: "Denials and consent requests are also appended", on the strength of
    # §8.2's "Every significant event affecting a file".
    for reason, denied in all_eight().items():
        audit_id = a_denial_record(p7_conn, file_id, denied)
        row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                              (audit_id,)).fetchone()
        assert row["event_type"] == MODEL_RELEASE_DENIED, reason
        assert row["subsystem"] == "P7", reason
        assert json.loads(row["explanation"])["reason"] == reason


def test_the_denial_record_says_unreadable_unclassified(p7_conn, file_id):
    # D2: `Unreadable or unclassified` is a GATE OUTCOME. This is the field it lives
    # in -- `AuditRecord.file_sensitivity`, on the release decision.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert audit_record(p7_conn, audit_id).file_sensitivity == "unreadable_unclassified"


def test_a_denial_writes_no_classification(p7_conn, file_id):
    # C4: "a gate that also wrote would be doing two jobs." D2: the outcome "lives on
    # the release decision and never in that column, so 'nothing has looked' can never
    # be read as 'this file carries nothing'." One assertion, both rulings.
    before = get_file(p7_conn, file_id)["sensitivity_state"]
    a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert get_file(p7_conn, file_id)["sensitivity_state"] == before


def test_a_denial_records_the_class_a_classified_file_actually_has(p7_conn, file_id):
    classified = ClassificationRecord(
        file_id=file_id, content_hash=get_file(p7_conn, file_id)["content_hash"],
        handling_class="sensitive_personal", protected=True, basis="detector",
        evidence_refs=DETECTOR_KEYS, reliability_state="validated",
        observed_at=FIXED_CLOCK)
    audit_id = a_denial_record(p7_conn, file_id,
                               all_eight()["protected_cloud_target"],
                               classification=classified)
    assert audit_record(p7_conn, audit_id).file_sensitivity == "sensitive_personal"


def test_the_denial_record_names_no_released_content(p7_conn, file_id):
    # Nothing left the device, so `excerpts_included` is empty and
    # `redaction_applied` is false. A denial that listed excerpts would be a record of
    # a release that did not happen.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    record = audit_record(p7_conn, audit_id)
    assert record.outcome == "denied"
    assert record.release_id is None
    assert record.excerpts_included == ()
    assert record.redaction_applied is False


def test_the_denial_record_carries_every_audit_field(p7_conn, file_id):
    # SPEC §7's nineteen names are Task 10's; this asserts the denial path fills the
    # published tuple rather than a subset a later reader would have to guess at.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    record = audit_record(p7_conn, audit_id)
    for name in AUDIT_FIELDS:
        assert hasattr(record, name), name


def test_a_group_scoped_denial_names_all_its_files(p7_conn, file_id):
    # `events` has one `file_id` column. The column carries the id only when the call
    # is about exactly one file, so `WHERE file_id = ?` never over-reports; the full
    # tuple is always in the explanation. Task 10's `audit_records_for(file_id=...)`
    # must read the explanation too, or Task 15's `prior_releases` under-reports.
    request = a_request(target=Target(file_ids=(file_id, "file-2"), group_id="group-1"))
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"],
                               request=request)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["file_id"] is None
    assert json.loads(row["explanation"])["file_ids"] == [file_id, "file-2"]


def test_a_denial_appends_exactly_one_event(p7_conn, file_id):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before + 1
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_denials.py -v`
Expected: FAIL — `ImportError: cannot import name 'DECIDABLE_FROM_REQUEST' from 'privacy.denial'`
(the module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/denial.py`**

```python
# src/privacy/denial.py
"""§8.4's eight refusals -- and the one that is the ordinary case.

The detector is unwritten (D2). No task in any plan produces a rule set, so against a
real corpus `Gate.release` is asked about a file with no `ClassificationRecord`,
`resolve_class(None)` returns `unreadable_unclassified`, and the call is denied. That
is not a degraded mode. It is what a correct locked door does when nobody has been
given a key, and this module is written for it: `unclassified` carries the longest
explanation and the most remedies, because it is what the audit log will be full of.

Three things are decided here:

- **The eight reasons have a total order** (`DENIAL_ORDER`), because four of them
  overlap on real inputs and SPEC §6 requires one answer. The ordering principle is
  `DECIDABLE_FROM_REQUEST`: no denial that can be decided from the request alone may
  be decided after one that requires reading the file. A gate that materialised an
  excerpt and then discovered the mode forbade the call has read a sensitive file for
  a call that was never going to happen.
- **The builders are pure and the append is one function.** SPEC §7: "Denials and
  consent requests are also appended." The record needs the request and the policy,
  which a builder does not see; a builder that took them would compose §7's record
  eight times over, and Task 10 owns it once.
- **`unreadable_unclassified` goes in `AuditRecord.file_sensitivity` and nowhere
  else.** D2: it "lives on the release decision and never in that column, so 'nothing
  has looked' can never be read as 'this file carries nothing'." This module issues no
  `UPDATE files`.

It owns no detection rule, no numeric ceiling and no remedy vocabulary. The class of a
file arrives as a `ClassificationRecord`; the ceiling arrives from
`database_agent.budget.get_ceiling`; the remedies are composed per denial from the
design's own sentences, because §8.6 names four ladder rungs for one situation and
§8.4 names four consent options for another, and one enumeration over both would
invent a fifth thing no section states.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from database_agent.budget import get_ceiling

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import CONSENT_REVOKED, SUBSYSTEM
from privacy.classification import ClassificationRecord, resolve_class
from privacy.items import AlwaysLocalRequested, WholeDocumentRequested
from privacy.policy import Policy
from privacy.release import Denied
from privacy.vocabulary import check_denial_reason

#: §7.3's literal template name, the one residual-library name P7 uses.
PROTECTED_RECORDS_TEMPLATE: str = "Protected Records"

#: The key Task 15's `revoke` writes into the `consent_revoked` explanation. Pinned so
#: a rename on either side is a red test rather than a denial that stops firing.
REVOKED_SCOPE_KEY: str = "scope"

#: P1's key for §8.6's dossier ceiling. The VALUE is never P7's -- SPEC Deferred puts
#: "Numeric values for every ceiling" outside this contract.
_DOSSIER_CEILING_KEY: str = "model.max_dossier_tokens_per_call"

#: The eight, in evaluation order. See the module docstring for each position.
DENIAL_ORDER: tuple[str, ...] = (
    "mode_forbids_target",
    "policy_revoked",
    "always_local_item",
    "unclassified",
    "protected_records_template",
    "protected_cloud_target",
    "whole_document_requested",
    "dossier_over_budget",
)

#: The six decidable from the request, the policy and a row lookup. The other two need
#: the resolved text, and every member of this set precedes both of them.
DECIDABLE_FROM_REQUEST: frozenset[str] = frozenset({
    "mode_forbids_target",
    "policy_revoked",
    "always_local_item",
    "unclassified",
    "protected_records_template",
    "protected_cloud_target",
})

#: §8.4's two modes under which no content leaves the device.
_LOCAL_ONLY_MODES: tuple[str, str] = ("offline", "local_model")


class MalformedDenial(ValueError):
    """A denial missing its explanation or its remedy.

    §8.6 requires the UI to show "what has been deferred, and why", and a denial with
    no legitimate alternative is a dead end the user cannot act on.
    """


@dataclass(frozen=True)
class RemedyOption:
    """One thing the caller may legitimately do instead (SPEC §6, §8.6).

    Not a closed vocabulary, deliberately. `action` is a short identifier for the
    surface to key on and `detail` is the sentence it came from.
    """

    action: str
    detail: str


def deny(reason: str, *, explanation: str,
         remedy_options: Sequence[RemedyOption],
         evidence_refs: Sequence[str]) -> Denied:
    """Build one refusal, validated.

    `evidence_refs` carries whatever the classification carried. M14's key-versus-id
    rule is Task 3's, on `ClassificationRecord.evidence_refs`; a second copy of it
    here would be a second place for it to drift.
    """
    check_denial_reason(reason)
    if not explanation or not explanation.strip():
        raise MalformedDenial(
            f"{reason}: SPEC §6 requires the explanation be 'user-facing, "
            "evidence-referenced'; an empty one is neither"
        )
    if not remedy_options:
        raise MalformedDenial(
            f"{reason}: §8.6 requires the product show 'what has been deferred, and "
            "why'. A denial with no legitimate alternative is a dead end"
        )
    refs = tuple(evidence_refs)
    if any(not isinstance(ref, str) or not ref for ref in refs):
        raise MalformedDenial(f"{reason}: every evidence ref must be a non-empty key")
    return Denied(reason=reason, explanation=explanation,
                  remedy_options=tuple(remedy_options), evidence_refs=refs)


def first_reason(reasons: Iterable[str]) -> str | None:
    """The highest-precedence reason among those that fired, or None.

    SPEC §6 gives one `reason`, and four of the eight overlap on real inputs, so the
    gate needs a total order rather than whichever check happened to run first.
    """
    triggered = {check_denial_reason(reason) for reason in reasons}
    for reason in DENIAL_ORDER:
        if reason in triggered:
            return reason
    return None


# --- the six decidable from the request -------------------------------------

def mode_forbids(operation_mode: str, locality: str) -> bool:
    """§8.4: under `offline` and `local_model`, no content leaves the device.

    A LOCAL model is permitted under both -- "only local rules and local models may
    run" -- so this refuses the target's locality, never the call.
    """
    return locality == "cloud" and operation_mode in _LOCAL_ONLY_MODES


def policy_revoked_for(conn: sqlite3.Connection, policy: Policy, scope: str) -> bool:
    """Granted and then withdrawn -- not "never granted", which is a different reason.

    Two-sided on purpose: a re-grant puts the scope back in `policy.consent_grants`
    and this stops firing, which is what makes revocation forward-only rather than
    permanent (§8.4: "revoke a policy for future runs").
    """
    if any(granted == scope for granted, _option in policy.consent_grants):
        return False
    for row in conn.execute(
            "SELECT explanation FROM events WHERE event_type = ?", (CONSENT_REVOKED,)):
        payload = json.loads(row["explanation"])
        if payload.get(REVOKED_SCOPE_KEY) == scope:
            return True
    return False


def unclassified_denies(*, locality: str, local_calls_on_unclassified: bool) -> bool:
    """§8.4 makes classification a precondition of escalation.

    `local_calls_on_unclassified` has NO default. Open question 5: "Does
    `unreadable_unclassified` permit a LOCAL model call? ... Reading escalation
    strictly denies local calls on unclassified files, which may block exactly the
    OCR-opaque screenshots §2.7 and §7.8 want a model to interpret." Unanswered, so
    the caller answers it and P7 names no winner.
    """
    if locality == "cloud":
        return True
    return not local_calls_on_unclassified


def is_protected_records(template_name: str | None) -> bool:
    """§7.3's carve-out, and it binds local calls too."""
    return template_name == PROTECTED_RECORDS_TEMPLATE


def protected_cloud_denies(*, protected: bool, locality: str, operation_mode: str,
                           scope: str, granted_scopes: Sequence[str]) -> bool:
    """SPEC §2's first protected consequence: "not included in cloud-model prompts BY
    DEFAULT" -- and `cloud_assisted` plus an explicit grant is the carve-out.

    §8.4: "Cloud-assisted mode: User explicitly permits selected corpus areas to use a
    cloud model." What a "corpus area" is stays Open question 3, so `scope` is an
    opaque string the caller supplies and P7 resolves none.
    """
    if not protected or locality != "cloud":
        return False
    if operation_mode == "cloud_assisted" and scope in tuple(granted_scopes):
        return False
    return True


# --- the two that need the resolved content ---------------------------------

def over_dossier_ceiling(conn: sqlite3.Connection, *, measured_tokens: int) -> bool:
    """M9's backstop. An UNSET ceiling cannot deny.

    `get_ceiling` returns `int | None` and `None` is the ordinary state. P7 owns no
    number, so with nothing configured there is nothing to exceed. `measured_tokens`
    is the caller's -- P7 has no tokenizer and inventing one would invent a number.
    Reads P1's stored ceiling and never `request.max_dossier_tokens`, which is "the
    caller's echo of it (M9)": a caller must not raise its own ceiling by echoing a
    larger one.
    """
    ceiling = get_ceiling(conn, _DOSSIER_CEILING_KEY)
    if ceiling is None:
        return False
    return measured_tokens > ceiling


# --- the eight builders -----------------------------------------------------

def deny_mode_forbids_target(*, operation_mode: str, model_target,
                             file_ids: Sequence[str]) -> Denied:
    return deny(
        "mode_forbids_target",
        explanation=(
            f"the operation mode is {operation_mode!r} and the request targets a "
            f"{model_target.locality} model ({model_target.provider}/"
            f"{model_target.model_id}). §8.4: under fully offline mode 'No content "
            "leaves the device; only local rules and local models may run.' "
            f"{len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("use_local_model",
                         "§8.4: local rules and local models may run under this mode"),
            RemedyOption("change_operation_mode",
                         "§8.4's four modes are the user's to choose; the default is "
                         "local-first and changing it is an explicit act (W1)"),
        ),
        evidence_refs=(),
    )


def deny_policy_revoked(*, scope: str, policy: Policy,
                        file_ids: Sequence[str]) -> Denied:
    return deny(
        "policy_revoked",
        explanation=(
            f"consent for {scope!r} was granted and then withdrawn; policy "
            f"{policy.policy_version} carries no grant for it. §8.4 gives the user "
            "the right to 'revoke a policy for future runs', and this is a future "
            f"run. {len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("grant_consent",
                         "§8.4's four options are offered again through P13 -- offered, "
                         "not re-proposed: §8.7 stores the withdrawal as negative "
                         "feedback so the same proposal does not resurface by itself"),
            RemedyOption("use_local_model",
                         "§8.4: a local model is one of the four consent options"),
        ),
        evidence_refs=(),
    )


def deny_always_local_item(caught: AlwaysLocalRequested, *,
                           file_ids: Sequence[str]) -> Denied:
    """Task 7's construction-time refusal, translated into the gate's answer.

    The nine names live in `vocabulary.ALWAYS_LOCAL` and the refusal in `items`. A
    builder that re-decided which of them are always-local would be a second copy of
    §8.4's list.
    """
    return deny(
        "always_local_item",
        explanation=(
            f"{caught}. §8.4: 'Paths, complete extracted text, OCR output, file "
            "hashes, image EXIF, GPS, user edits, group memberships, and raw "
            "sensitive values should remain local.' Nothing in that set can be named "
            f"as a releasable item kind. {len(tuple(file_ids))} file(s) were not "
            "released."
        ),
        remedy_options=(
            RemedyOption("request_excerpt",
                         "§8.4's compact dossier: 'selected excerpts, redacted "
                         "identifiers, candidate labels, non-sensitive metadata, and "
                         "evidence references'"),
        ),
        evidence_refs=(),
    )


def deny_unclassified(*, file_ids: Sequence[str], locality: str,
                      completeness: str | None) -> Denied:
    """The ordinary denial. No detector exists (D2), so this is the normal path.

    The explanation says `unreadable_unclassified` and never `public_low`: SPEC §1's
    "Absence of a classification resolves to `unreadable_unclassified`, never to
    `public_low`", which is §8.6's "Cost exhaustion must never turn into
    lower-quality automatic classification" applied to the one case that matters.
    """
    seen = ("no extraction run has completed for it"
            if completeness is None else f"its extraction completeness is {completeness!r}")
    return deny(
        "unclassified",
        explanation=(
            f"{len(tuple(file_ids))} file(s) resolve to handling class "
            "'unreadable_unclassified': no classification record exists and "
            f"{seen}. §8.4 requires the system to 'classify data into handling "
            "classes before LLM escalation', so an unclassified file has not met the "
            f"precondition for a {locality} model call. Absence of a classification "
            "is not evidence that the file carries nothing, and it never resolves to "
            "a lower class so the pipeline can continue."
        ),
        remedy_options=(
            RemedyOption("classify",
                         "§8.4: the classification 'is itself evidence-backed and can "
                         "be revised by the user'; a user may set one directly"),
            RemedyOption("defer",
                         "§8.6: 'retain extracted evidence, mark the deferred stage, "
                         "and leave the file or group in review rather than guessing'"),
            RemedyOption("review",
                         "§8.6: the user 'should be able to see what is running, what "
                         "has been deferred, and why'"),
        ),
        evidence_refs=(),
    )


def deny_protected_records_template(*, file_ids: Sequence[str],
                                    model_target) -> Denied:
    """§7.3, and it binds a LOCAL target too -- which is why it outranks the cloud rule."""
    return deny(
        "protected_records_template",
        explanation=(
            f"{len(tuple(file_ids))} file(s) are held under the "
            f"{PROTECTED_RECORDS_TEMPLATE!r} residual template. §7.3: it 'should "
            "normally remain local-only and must not cause filenames or content to "
            "be exposed in model prompts.' That binds every model, so the "
            f"{model_target.locality} target does not change the answer."
        ),
        remedy_options=(
            RemedyOption("decide_locally",
                         "§7.3: normally local-only; deterministic rules and local "
                         "placement still apply"),
            RemedyOption("review",
                         "§7.11: the system must not act on protected material "
                         "'without explicit user action'"),
        ),
        evidence_refs=(),
    )


def deny_protected_cloud_target(*, file_ids: Sequence[str], operation_mode: str,
                                scope: str,
                                evidence_refs: Sequence[str] = ()) -> Denied:
    return deny(
        "protected_cloud_target",
        explanation=(
            f"{len(tuple(file_ids))} file(s) are protected and the request targets a "
            f"cloud model under mode {operation_mode!r}. §8.4: 'Protected material "
            "should not be included in cloud-model prompts by default', and 'Hybrid "
            f"mode: Sensitive files remain local.' Scope {scope!r} carries no "
            "explicit grant."
        ),
        remedy_options=(
            RemedyOption("use_local_model",
                         "§8.4: 'Local-model mode: Local extraction plus a "
                         "user-installed local LLM for eligible dossiers'"),
            RemedyOption("grant_consent",
                         "§8.4: 'Cloud-assisted mode: User explicitly permits "
                         "selected corpus areas to use a cloud model'"),
        ),
        evidence_refs=evidence_refs,
    )


def deny_whole_document_requested(caught: WholeDocumentRequested, *,
                                  file_ids: Sequence[str]) -> Denied:
    return deny(
        "whole_document_requested",
        explanation=(
            f"{caught}. §8.4: the engine 'should not send full documents where a "
            "short heading or OCR excerpt is enough to resolve the question.' "
            f"{len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("narrow_span",
                         "§8.4's compact dossier is 'selected excerpts' -- a bounded "
                         "span, addressed by (observation_key, span)"),
        ),
        evidence_refs=(),
    )


def deny_dossier_over_budget(*, measured_tokens: int, ceiling: int,
                             file_ids: Sequence[str]) -> Denied:
    """M9's backstop. It should never fire in a correct pipeline. Do not delete it.

    §8.6 forbids a prompt that "truncate[s] silently in a way that removes the
    decisive evidence", and the gate is the last place to catch a caller that skipped
    its ladder. The four remedies ARE that ladder, in §8.6's own order and words.
    """
    return deny(
        "dossier_over_budget",
        explanation=(
            f"the dossier measures {measured_tokens} tokens against a ceiling of "
            f"{ceiling} for {len(tuple(file_ids))} file(s). §8.6's ladder runs in the "
            "caller before the gate is asked (M9); reaching this denial in a running "
            "pipeline is a caller defect, not a gate result. The gate never truncates "
            "and never reduces -- reduction changes what the model sees, which is a "
            "dossier decision."
        ),
        remedy_options=(
            RemedyOption("summarize_deterministic_facts", "§8.6, rung one"),
            RemedyOption("preserve_anchor_excerpts", "§8.6, rung two"),
            RemedyOption("split_the_task", "§8.6, rung three"),
            RemedyOption("defer_the_decision", "§8.6, rung four"),
        ),
        evidence_refs=(),
    )


# --- the one append ---------------------------------------------------------

def record_denial(conn: sqlite3.Connection, denied: Denied, *, request,
                  policy: Policy, classification: ClassificationRecord | None,
                  content_hashes: Sequence[str], user_id: str | None,
                  component_version: str, observed_at: str) -> int:
    """Append the one `model_release_denied` record and return its `audit_id`.

    `file_sensitivity` is computed with `classification.resolve_class`, the same
    function the rest of P7 uses, so the gate outcome is not re-derived. It lands
    HERE -- on the release decision -- and never in `files.sensitivity_state` (D2).

    The `events` table has one `file_id` column, so it carries the id only when the
    call is about exactly one file and `WHERE file_id = ?` therefore never
    over-reports. The full tuple is always in the explanation as `file_ids`.

    SPEC §7 enumerates a RELEASE record, so it has no field for a denial's own
    `reason` and `remedy_options[]`. They go through `append_audit`'s `extra`, into
    the same canonical-JSON `explanation` -- §8.2's "structured explanation or
    evidence reference" slot -- because §8.6 requires the product to show "what has
    been deferred, and why" and there is nowhere else for the why to live.
    """
    file_ids = tuple(request.target.file_ids)
    values = {
        "audit_id": None,
        "release_id": None,
        "policy_version": policy.policy_version,
        "plan_version": policy.plan_version,
        "stage": request.stage,
        "outcome": "denied",
        "operation_mode": policy.operation_mode,
        "authorizing_policy": policy.policy_version,
        "file_sensitivity": resolve_class(classification),
        "excerpts_included": (),
        "redaction_applied": False,
        "redaction_manifest": (),
        "model": {"locality": request.model_target.locality,
                  "model_id": request.model_target.model_id,
                  "provider": request.model_target.provider},
        "content_hashes": tuple(content_hashes),
        "content_hash": content_hashes[0] if len(tuple(content_hashes)) == 1 else None,
        "prompt_fingerprint": request.prompt_fingerprint,
        "file_id": file_ids[0] if len(file_ids) == 1 else None,
        "file_ids": file_ids,
        "group_id": request.target.group_id,
        "consent_request_id": None,
        "user_id": user_id,
        "observed_at": observed_at,
        "appended_at": observed_at,
    }
    unfilled = [name for name in AUDIT_FIELDS if name not in values]
    if unfilled:
        raise MalformedDenial(
            f"SPEC §7 names {unfilled} and the denial path has no value for them; a "
            "field Task 10 publishes must be filled at the seam, not defaulted"
        )
    record = AuditRecord(**{name: values[name] for name in AUDIT_FIELDS})
    return append_audit(conn, record, author=SUBSYSTEM,
                        component_version=component_version, extra={
                            "reason": denied.reason,
                            "explanation": denied.explanation,
                            "remedy_options": [option.action
                                               for option in denied.remedy_options],
                            "evidence_refs": list(denied.evidence_refs),
                        })
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_denials.py -v`
Expected: PASS — 29 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–13 green, and the 1300 P1–P5 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/denial.py tests/p7/test_p7_denials.py
git commit -m "feat(P7): the eight denials, their precedence, and the audit record each one writes"
```

---

### Task 14: `NeedsConsent`, its id, and the P13 seam

**Files:**
- Create: `src/privacy/consent.py`
- Test: `tests/p7/test_p7_consent.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.CONSENT_OPTIONS`, `privacy.audit.AUDIT_FIELDS`, `.AuditRecord`,
  `.append_audit(conn, record, *, author, component_version, extra=None) -> int`,
  `privacy.authorship.SUBSYSTEM`, `.CONSENT_REQUESTED`, `.CONSENT_GRANTED`,
  `.event_defaults(*, event_type, **fields) -> dict[str, object]`,
  `privacy.policy.Policy`,
  `privacy.policy.grant_consent(conn, policy, scope, option, *, user_id, component_version,
  observed_at) -> str`, `database_agent.events.append_event(conn, **fields) -> int`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`consent.py`):
  - `CONSENT_AUTHORIZES: Mapping[str, bool]` — which of the four permit a model call.
  - `ConsentRequirement` — frozen: `file_ids`, `handling_class`, `items`, `why`.
  - `NeedsConsent` — frozen: `consent_request_id`, `requirement`, `options`.
  - `open_consent_request(conn, requirement, *, request, policy, content_hashes, user_id,
    component_version, observed_at) -> NeedsConsent`.
  - `record_consent_choice(conn, consent_request_id, option, *, policy, scope, user_id,
    component_version, observed_at) -> None`.
  - `pending_consent(conn, consent_request_id) -> NeedsConsent | None`.
  - `UnknownConsentOption`, `IncompleteConsentOptions`, `UnknownConsentRequest`,
    `ConsentAlreadyRecorded`.

**Done-means:** 7.

**The whole task exists so that `no_model_use` cannot become `abstain`.** §8.4: *"If a model needs
text containing sensitive content, the user should see that requirement and choose whether to allow
a local model, a cloud model, a redacted prompt, or no model use."* P8's SPEC: *"P8 must never map
this branch to `abstain`: there is no reason code for it, and none may be added. That mapping is the
precise failure B2 was raised to remove — §8.4 requires the *user* to see the requirement and choose,
so an abstention makes the choice for them, silently selecting 'no model use' without asking.
Consent pending is not consent refused."* P7 does exactly two things about that and no third:

1. **`NeedsConsent` carries no `reason` field**, so it is not a `Denied` in disguise and a caller
   cannot map it onto a denial reason even by accident. Asserted over `dataclasses.fields`, both
   ways: the field is absent, and the two branch types share no field name at all.
2. **A recorded `no_model_use` is a `consent_granted` event with a `user_id` and a timestamp.** An
   abstention is the *absence* of an answer. A recorded refusal is an answer. The difference is
   readable in the log by anyone who looks, which is what makes the two outcomes distinguishable
   after the fact rather than only in P8's source.

**Whether a caller absorbs the branch is P8 Done-means 13 and P13 Done-means 16.** P7 makes the
absorption unrepresentable; it does not police it, and no test here reaches into P8.

**`no_model_use` is a choice and changes no policy — `CONSENT_AUTHORIZES` is that as data.** Three of
the four options authorize a model and one does not, so `record_consent_choice` calls
`policy.grant_consent` for three and skips it for one. Written as an `if option !=
"no_model_use"` it would be one negation away from silently granting; written as a mapping it is a
table a reviewer can read and a test can iterate. The event is appended for **all four**, because
§8.2 preserves *"Every significant event affecting a file"* and a user deciding not to use a model is
significant — it is the decision §8.7 would learn from.

**Task 14 adds no table. The audit log is the store.** `consent_request_id` has no `events` column,
so it lands in the canonical-JSON `explanation` that the skeleton's *The audit record's home* already
decided on, and `pending_consent` reads it back with `json_extract`. That is not a shortcut: Done-means
7's own falsifiable form is *"the audit log holds a `consent_requested` event and no `model_release`
for that request until a choice is recorded"*, so the log **is** the state, and a second store beside
it would be a second place for the two to disagree. A test asserts no consent table exists.

**`consent_request_id` is P13's field name, not an invention.** P13's routing table: *"P7 |
`consent`, `privacy_settings` | `review_action` in full; `subject_ref` is a `consent_request_id`;
`action = select_consent_option | set_redaction | mark_private`."* SPEC §6's `NeedsConsent` carries
no id, and Done-means 7 needs a join key, so Task 14 adds it under P13's spelling. It is minted with
`uuid.uuid4()` rather than `secrets`, and the contrast with Task 12's `release_id` is deliberate: a
release id is a **capability** and must not be guessable, a consent request id is a **join key** that
P13 will put in a `subject_ref` column and that carries no authority at all.

**The grant is P7's even though P13 collected the gesture.** P13's SPEC: *"The chosen option is
routed to P7, which authors the §8.4 consent events and the consent-aware audit record. P13 records
the collection, not the grant."* `subsystem = "P7"` on every event this module writes (M8).

**One `consent_granted` per choice, appended here — the mirror of Task 15's ruling.** Task 15 already
settled that `policy.revoke_consent` records the withdrawal and appends nothing, and that `revoke`
appends the single `consent_revoked`. The same split holds on the grant side: `policy.grant_consent`
records the grant and returns the new `policy_version`; `record_consent_choice` appends the one
`consent_granted`. Two appends would put one act in the log twice, and §8.4's `prior_releases` is
read back out of that log. **This pins Task 5's `grant_consent`**, whose `Produces` entry is spelled
with an ellipsis.

**The handoff to Task 15 is one string: `scope`.** The `consent_granted` this task writes and the
`consent_revoked` Task 15 writes both carry the scope under the key `"scope"`, which Task 13 pins as
`REVOKED_SCOPE_KEY` and reads to decide `policy_revoked`. Grant here, withdraw there, deny in
between — three tasks, one key. What a scope *is* stays Open question 3: *"What is a 'corpus area'?
… Consent grants cannot be scoped until this is named."* `scope` is a required keyword with no
default and P7 defines no area, exactly as Task 15's `files_in_scope` does.

**`record_consent_choice` returns `None`, and the new `policy_version` is read back through
`policy.current_policy`.** The skeleton fixes the return type and it is the right one: SPEC §6 says
*"the gate owns the policy, so the caller does not supply this value, it echoes it"*, and handing a
freshly minted `policy_version` back from a consent recorder would give the caller a value from a
path that is not the gate. The caller re-reads the policy, which is what it would have to do anyway
— **the original request is never resumed.** P8's SPEC: *"When the user chooses, the caller composes
a **new** `ModelCallRequest` under the chosen option; the original is never resumed, because the
policy it was composed under is not the policy that now applies."* That sentence is also why one
request accepts exactly one choice, and why a second raises `ConsentAlreadyRecorded` rather than
overwriting — a second answer to an answered question would let a caller turn a recorded
`no_model_use` into a `cloud_model` after the fact.

**The requirement carries references, never text.** `ConsentRequirement.items` is
`(observation_key, span)` pairs, the same shape as `excerpts_included`, for the same reason SPEC §7
gives: *"not a second copy of the text — the always-local text already exists once."* A consent
prompt that embedded the sensitive value would have released it in order to ask permission to
release it. Asserted over `dataclasses.fields`, not by reading the class body.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_consent.py
"""Done-means 7 -- all four options, and no release until a choice is recorded.

§8.4: "If a model needs text containing sensitive content, the user should see that
requirement and choose whether to allow a local model, a cloud model, a redacted
prompt, or no model use." Those four, exactly.

The centre of this file is that `no_model_use` is an ANSWER and an abstention is
SILENCE, and that the log can tell them apart. P8 Done-means 13 and P13 Done-means 16
own whether a caller absorbs the branch; nothing here reaches into either.
"""
import json
from dataclasses import fields

import pytest

from privacy.audit import audit_records_for
from privacy.authorship import CONSENT_GRANTED, CONSENT_REQUESTED, SUBSYSTEM
from privacy.consent import (
    CONSENT_AUTHORIZES, ConsentAlreadyRecorded, ConsentRequirement,
    IncompleteConsentOptions, NeedsConsent, UnknownConsentOption,
    UnknownConsentRequest, open_consent_request, pending_consent,
    record_consent_choice,
)
from privacy.denial import REVOKED_SCOPE_KEY
from privacy.policy import Policy, current_policy, set_policy
from privacy.release import REQUEST_FIELDS, Denied, ModelCallRequest, ModelTarget, Target
from privacy.vocabulary import CONSENT_OPTIONS

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
SCOPE = "Academics"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
EXCERPTS = (
    ("sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd", "0-19"),
)

_REQUEST_DEFAULTS = {
    "stage": "grouping",
    "target": Target(file_ids=("file-1",), group_id=None),
    "model_target": CLOUD,
    "requested_items": (),
    "prompt_template_id": "template-1",
    "prompt_fingerprint": "fp-1",
    "max_dossier_tokens": 4000,
}


def a_request(**over) -> ModelCallRequest:
    missing = [name for name in REQUEST_FIELDS if name not in _REQUEST_DEFAULTS]
    assert not missing, (
        f"REQUEST_FIELDS names {missing} and this test has no value for them; "
        "SPEC §6 changed and Task 14 needs a value, not a default")
    values = {name: _REQUEST_DEFAULTS[name] for name in REQUEST_FIELDS}
    values.update(over)
    return ModelCallRequest(**values)


def a_requirement(**over) -> ConsentRequirement:
    base = dict(file_ids=("file-1",), handling_class="sensitive_personal",
                items=EXCERPTS,
                why="the grouping question turns on a value the detector marked "
                    "potentially sensitive")
    base.update(over)
    return ConsentRequirement(**base)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


@pytest.fixture()
def stored_policy(p7_conn) -> Policy:
    """A policy in force, so `grant_consent` has something to supersede."""
    set_policy(p7_conn, a_policy(), author=SUBSYSTEM, component_version=COMPONENT,
               user_id="joseph")
    return current_policy(p7_conn, plan_version="plan-1")


def open_request(conn, policy, **over) -> NeedsConsent:
    base = dict(request=a_request(), policy=policy, content_hashes=("sha256:abc",),
                user_id="joseph", component_version=COMPONENT,
                observed_at=FIXED_CLOCK)
    base.update(over)
    return open_consent_request(conn, a_requirement(), **base)


def choose(conn, needs, option, policy, **over) -> None:
    base = dict(policy=policy, scope=SCOPE, user_id="joseph",
                component_version=COMPONENT, observed_at=LATER)
    base.update(over)
    record_consent_choice(conn, needs.consent_request_id, option, **base)


# --- the four options, always all four --------------------------------------

def test_the_four_options_are_the_designs_own_four():
    # §8.4: "choose whether to allow a local model, a cloud model, a redacted prompt,
    # or no model use." Those four, in that order.
    assert CONSENT_OPTIONS == ("local_model", "cloud_model", "redacted_prompt",
                              "no_model_use")


def test_the_options_default_to_all_four():
    needs = NeedsConsent(consent_request_id="consent-1", requirement=a_requirement())
    assert needs.options == CONSENT_OPTIONS


def test_a_needs_consent_with_three_options_raises():
    # P13's SPEC: "All four options are always presentable. A surface that offers
    # fewer has silently made the user's decision for them."
    with pytest.raises(IncompleteConsentOptions):
        NeedsConsent(consent_request_id="consent-1", requirement=a_requirement(),
                     options=("local_model", "cloud_model", "redacted_prompt"))


def test_dropping_no_model_use_in_particular_raises():
    # The one a caller would be tempted to drop, because "no model" looks like "no
    # call". It is the option that makes the branch a question rather than a refusal.
    with pytest.raises(IncompleteConsentOptions):
        NeedsConsent(consent_request_id="consent-1", requirement=a_requirement(),
                     options=tuple(o for o in CONSENT_OPTIONS if o != "no_model_use"))


def test_an_option_outside_the_vocabulary_raises():
    with pytest.raises(UnknownConsentOption):
        NeedsConsent(consent_request_id="consent-1", requirement=a_requirement(),
                     options=CONSENT_OPTIONS + ("maybe_later",))


# --- structurally not a denial ----------------------------------------------

def test_needs_consent_has_no_reason_field():
    # SPEC §6: "`Denied` is the gate's answer, `NeedsConsent` is a question that only
    # the user can answer. Consent pending is not consent refused."
    names = {field.name for field in fields(NeedsConsent)}
    assert names == {"consent_request_id", "requirement", "options"}
    assert "reason" not in names


def test_needs_consent_shares_no_field_with_denied():
    # A caller cannot map one onto the other even by accident: there is no shared name
    # to copy across.
    assert not ({field.name for field in fields(NeedsConsent)}
                & {field.name for field in fields(Denied)})


def test_the_requirement_carries_references_and_not_text():
    # SPEC §7: `(observation_key, span)` pairs, "not a second copy of the text". A
    # consent prompt embedding the value would have released it in order to ask
    # permission to release it.
    names = {field.name for field in fields(ConsentRequirement)}
    assert names == {"file_ids", "handling_class", "items", "why"}
    assert not (names & {"text", "value", "content", "excerpt", "raw_value"})
    assert a_requirement().items == EXCERPTS


# --- the id, and the P13 seam -----------------------------------------------

def test_opening_a_request_mints_an_id(p7_conn, stored_policy):
    # P13's routing table: "`subject_ref` is a `consent_request_id`". SPEC §6 carries
    # no id and Done-means 7 needs a join key, so Task 14 adds it under P13's name.
    first = open_request(p7_conn, stored_policy)
    second = open_request(p7_conn, stored_policy)
    assert first.consent_request_id
    assert first.consent_request_id != second.consent_request_id


def test_pending_consent_round_trips_the_requirement(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    recovered = pending_consent(p7_conn, opened.consent_request_id)
    assert recovered == opened


def test_pending_consent_is_none_for_an_id_nobody_opened(p7_conn):
    assert pending_consent(p7_conn, "consent-nobody-opened") is None


def test_consent_adds_no_table(p7_conn, stored_policy):
    # Done-means 7's falsifiable form reads the audit log, so the audit log IS the
    # state. A second store beside it is a second place for the two to disagree.
    open_request(p7_conn, stored_policy)
    tables = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert not [name for name in tables if "consent" in name]


# --- Done-means 7, in its own words -----------------------------------------

def test_opening_a_request_appends_consent_requested(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_REQUESTED,)).fetchone()
    assert row["subsystem"] == "P7"
    payload = json.loads(row["explanation"])
    assert payload["consent_request_id"] == opened.consent_request_id
    assert payload["options"] == list(CONSENT_OPTIONS)


def test_no_model_release_exists_until_a_choice_is_recorded(p7_conn, stored_policy):
    # Done-means 7 verbatim: "the audit log holds a `consent_requested` event and no
    # `model_release` for that request until a choice is recorded."
    opened = open_request(p7_conn, stored_policy)
    records = audit_records_for(p7_conn, consent_request_id=opened.consent_request_id)
    assert [record.outcome for record in records] == ["consent_requested"]
    choose(p7_conn, opened, "cloud_model", stored_policy)
    outcomes = [record.outcome for record in
                audit_records_for(p7_conn,
                                  consent_request_id=opened.consent_request_id)]
    assert "released" not in outcomes


def test_recording_a_choice_releases_nothing(p7_conn, stored_policy):
    # C4: the gate writes its record and does not act on it. Recording consent is not
    # a release; P8's SPEC: "the caller composes a NEW `ModelCallRequest` under the
    # chosen option; the original is never resumed."
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "cloud_model", stored_policy)
    assert p7_conn.execute(
        "SELECT count(*) c FROM release_ledger").fetchone()["c"] == 0


def test_recording_a_choice_clears_the_pending_request(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "no_model_use", stored_policy)
    assert pending_consent(p7_conn, opened.consent_request_id) is None


# --- no_model_use is an answer, not silence ---------------------------------

def test_no_model_use_is_recorded_as_a_choice_not_as_silence(p7_conn, stored_policy):
    """B2, and P8's SPEC: "P8 must never map this branch to `abstain` ... an
    abstention makes the choice for them, silently selecting 'no model use' without
    asking." An abstention is the ABSENCE of an answer. This is an answer: it has a
    user, a time, and an event of its own, and a later reader can tell them apart.
    """
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "no_model_use", stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_GRANTED,)).fetchone()
    payload = json.loads(row["explanation"])
    assert payload["option"] == "no_model_use"
    assert payload["authorized"] is False
    assert row["user_id"] == "joseph"
    assert row["observed_at"] == LATER


def test_no_model_use_grants_no_policy_change(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    before = current_policy(p7_conn, plan_version="plan-1").consent_grants
    choose(p7_conn, opened, "no_model_use", stored_policy)
    assert current_policy(p7_conn,
                          plan_version="plan-1").consent_grants == before


def test_the_three_authorizing_options_change_the_policy(p7_conn, stored_policy):
    # `grant_consent` is Task 5's; this asserts the three that reach it do.
    for option in ("local_model", "cloud_model", "redacted_prompt"):
        opened = open_request(p7_conn, stored_policy)
        choose(p7_conn, opened, option, stored_policy)
        grants = current_policy(p7_conn, plan_version="plan-1").consent_grants
        assert (SCOPE, option) in grants


def test_consent_authorizes_is_data_and_not_an_if(p7_conn):
    # Written as `if option != "no_model_use"` this would be one negation away from
    # silently granting. Written as a mapping it is a table a reviewer can read.
    assert set(CONSENT_AUTHORIZES) == set(CONSENT_OPTIONS)
    assert CONSENT_AUTHORIZES["no_model_use"] is False
    assert all(CONSENT_AUTHORIZES[option] is True
               for option in CONSENT_OPTIONS if option != "no_model_use")


def test_every_option_appends_exactly_one_event(p7_conn, stored_policy):
    # §8.2 preserves "Every significant event affecting a file", and a user deciding
    # not to use a model is significant -- it is the decision §8.7 would learn from.
    for option in CONSENT_OPTIONS:
        opened = open_request(p7_conn, stored_policy)
        before = p7_conn.execute(
            "SELECT count(*) c FROM events WHERE event_type = ?",
            (CONSENT_GRANTED,)).fetchone()["c"]
        choose(p7_conn, opened, option, stored_policy)
        after = p7_conn.execute(
            "SELECT count(*) c FROM events WHERE event_type = ?",
            (CONSENT_GRANTED,)).fetchone()["c"]
        assert after == before + 1, option


# --- authorship, and the handoff to Task 15 ---------------------------------

def test_the_grant_is_authored_by_p7_though_p13_collected_it(p7_conn, stored_policy):
    # P13's SPEC: "The chosen option is routed to P7, which authors the §8.4 consent
    # events and the consent-aware audit record. P13 records the collection, not the
    # grant." M8: the acting part authors, P1 writes.
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "cloud_model", stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_GRANTED,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["component_version"] == COMPONENT


def test_the_grant_and_the_revocation_key_on_the_same_scope(p7_conn, stored_policy):
    # The handoff: this task grants, Task 15 withdraws, Task 13 denies in between --
    # three tasks, one key. Open question 3 leaves what a scope IS to the caller.
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "cloud_model", stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_GRANTED,)).fetchone()
    assert json.loads(row["explanation"])[REVOKED_SCOPE_KEY] == SCOPE


# --- refusals ---------------------------------------------------------------

def test_a_second_choice_for_one_request_is_refused(p7_conn, stored_policy):
    # P8's SPEC: "the caller composes a NEW `ModelCallRequest` under the chosen
    # option; the original is never resumed." A second answer to an answered question
    # would let a caller turn a recorded `no_model_use` into a `cloud_model` after
    # the fact.
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "no_model_use", stored_policy)
    with pytest.raises(ConsentAlreadyRecorded):
        choose(p7_conn, opened, "cloud_model", stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_GRANTED,)).fetchone()
    assert json.loads(row["explanation"])["option"] == "no_model_use"


def test_a_choice_for_an_unknown_request_is_refused(p7_conn, stored_policy):
    with pytest.raises(UnknownConsentRequest):
        record_consent_choice(p7_conn, "consent-nobody-opened", "cloud_model",
                              policy=stored_policy, scope=SCOPE, user_id="joseph",
                              component_version=COMPONENT, observed_at=LATER)


def test_an_unknown_option_is_refused(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    with pytest.raises(UnknownConsentOption):
        choose(p7_conn, opened, "maybe_later", stored_policy)


def test_a_refused_choice_writes_nothing(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    with pytest.raises(UnknownConsentOption):
        choose(p7_conn, opened, "maybe_later", stored_policy)
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert pending_consent(p7_conn, opened.consent_request_id) == opened


def test_the_scope_has_no_default(p7_conn, stored_policy):
    # Open question 3: "What is a 'corpus area'? ... Consent grants cannot be scoped
    # until this is named." Task 15's `files_in_scope` holds it the same way.
    opened = open_request(p7_conn, stored_policy)
    with pytest.raises(TypeError):
        record_consent_choice(p7_conn, opened.consent_request_id, "cloud_model",
                              policy=stored_policy, user_id="joseph",
                              component_version=COMPONENT, observed_at=LATER)
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_consent.py -v`
Expected: FAIL — `ImportError: cannot import name 'CONSENT_AUTHORIZES' from 'privacy.consent'`
(the module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/consent.py`**

```python
# src/privacy/consent.py
"""§8.4's consent question, its id, and the seam P13 collects the answer through.

§8.4: "If a model needs text containing sensitive content, the user should see that
requirement and choose whether to allow a local model, a cloud model, a redacted
prompt, or no model use." Those four, exactly, and always all four -- P13's SPEC: "A
surface that offers fewer has silently made the user's decision for them."

This module exists to make one failure unrepresentable. P8's SPEC: "P8 must never map
this branch to `abstain`: there is no reason code for it, and none may be added ... an
abstention makes the choice for them, silently selecting 'no model use' without
asking. Consent pending is not consent refused." P7 does two things about that:

- `NeedsConsent` carries no `reason` field, so it is not a `Denied` in disguise and
  cannot be mapped onto a denial reason by accident;
- a recorded `no_model_use` is a `consent_granted` event with a user and a time, so an
  answer and a silence are distinguishable in the log by anyone who looks.

Whether a caller absorbs the branch is P8 Done-means 13 and P13 Done-means 16. P7 does
not police it.

**No table.** Done-means 7's falsifiable form is "the audit log holds a
`consent_requested` event and no `model_release` for that request until a choice is
recorded", so the log IS the state, and a second store beside it would be a second
place for the two to disagree.

**One `consent_granted` per choice, appended here.** `policy.grant_consent` records the
grant and returns the new `policy_version`; it appends nothing. That is the mirror of
Task 15's ruling for `revoke_consent` and `consent_revoked`, and for the same reason:
two appends put one act in the log twice, and §8.4's `prior_releases` is read back out
of that log.

This module imports no `privacy` module that imports it: `release.py` re-exports
`NeedsConsent` for the `ReleaseDecision` union, so the request object arrives here as
an argument and its type is an annotation only.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING

from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import (
    CONSENT_GRANTED, CONSENT_REQUESTED, SUBSYSTEM, event_defaults,
)
from privacy.policy import Policy, grant_consent
from privacy.vocabulary import CONSENT_OPTIONS

if TYPE_CHECKING:  # pragma: no cover - annotation only; see the module docstring
    from privacy.release import ModelCallRequest

#: Which of §8.4's four permit a model call. Data rather than a negated `if`, which
#: would be one edit away from silently granting. `no_model_use` is a CHOICE -- it is
#: recorded like the others and changes no policy.
CONSENT_AUTHORIZES: Mapping[str, bool] = MappingProxyType({
    "local_model": True,
    "cloud_model": True,
    "redacted_prompt": True,
    "no_model_use": False,
})

#: The key the scope is stored under, shared with Task 13's `REVOKED_SCOPE_KEY` and
#: Task 15's `revoke`. Grant here, withdraw there, deny in between.
_SCOPE_KEY: str = "scope"


class UnknownConsentOption(ValueError):
    """A value outside §8.4's four. SPEC §1: "a load error, not a fallback.\""""


class IncompleteConsentOptions(ValueError):
    """Fewer than four options.

    P13's SPEC: "All four options are always presentable. A surface that offers fewer
    has silently made the user's decision for them."
    """


class UnknownConsentRequest(LookupError):
    """No `consent_requested` event carries this id."""


class ConsentAlreadyRecorded(ValueError):
    """This request already has an answer.

    P8's SPEC: "the caller composes a NEW `ModelCallRequest` under the chosen option;
    the original is never resumed." A second answer would let a caller turn a recorded
    `no_model_use` into a `cloud_model` after the fact.
    """


@dataclass(frozen=True)
class ConsentRequirement:
    """SPEC §6: "which items require sensitive text, and why".

    `items` is `(observation_key, span)` pairs -- the same shape as
    `excerpts_included`, and for SPEC §7's reason: "not a second copy of the text".
    A consent prompt that embedded the value would have released it in order to ask
    permission to release it.
    """

    file_ids: tuple[str, ...]
    handling_class: str
    items: tuple[tuple[str, str], ...]
    why: str


@dataclass(frozen=True)
class NeedsConsent:
    """SPEC §6's third branch. It carries no `reason`, and that is load-bearing.

    "`Denied` is the gate's answer, `NeedsConsent` is a question that only the user
    can answer. Consent pending is not consent refused."
    """

    consent_request_id: str
    requirement: ConsentRequirement
    options: tuple[str, ...] = CONSENT_OPTIONS

    def __post_init__(self) -> None:
        unknown = [option for option in self.options if option not in CONSENT_OPTIONS]
        if unknown:
            raise UnknownConsentOption(
                f"{unknown} are not among §8.4's four options {CONSENT_OPTIONS}"
            )
        if tuple(self.options) != CONSENT_OPTIONS:
            raise IncompleteConsentOptions(
                f"{tuple(self.options)} is not §8.4's four in order; P13: 'A surface "
                "that offers fewer has silently made the user's decision for them'"
            )


def _requirement_form(requirement: ConsentRequirement) -> dict[str, object]:
    return {
        "file_ids": list(requirement.file_ids),
        "handling_class": requirement.handling_class,
        "items": [list(pair) for pair in requirement.items],
        "why": requirement.why,
    }


def _requirement_from(form: Mapping[str, object]) -> ConsentRequirement:
    return ConsentRequirement(
        file_ids=tuple(form["file_ids"]),
        handling_class=form["handling_class"],
        items=tuple(tuple(pair) for pair in form["items"]),
        why=form["why"],
    )


def _event_for(conn: sqlite3.Connection, event_type: str,
               consent_request_id: str) -> sqlite3.Row | None:
    """The one event of this type carrying this id.

    `consent_request_id` has no `events` column, so it lives in the canonical-JSON
    `explanation` the skeleton's *The audit record's home* decided on, and is read
    back with `json_extract`.
    """
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? "
        "AND json_extract(explanation, '$.consent_request_id') = ? "
        "ORDER BY event_id LIMIT 1",
        (event_type, consent_request_id),
    ).fetchone()


def open_consent_request(conn: sqlite3.Connection, requirement: ConsentRequirement, *,
                         request: ModelCallRequest, policy: Policy,
                         content_hashes: Sequence[str], user_id: str | None,
                         component_version: str, observed_at: str) -> NeedsConsent:
    """Ask §8.4's question, record that it was asked, and return all four options.

    The id is `uuid.uuid4()`, not `secrets`: a `release_id` is a capability and must
    not be guessable, while a `consent_request_id` is a join key P13 puts in a
    `subject_ref` column and carries no authority at all.
    """
    consent_request_id = "consent-" + str(uuid.uuid4())
    needs = NeedsConsent(consent_request_id=consent_request_id,
                         requirement=requirement)
    file_ids = tuple(request.target.file_ids)
    values = {
        "audit_id": None,
        "release_id": None,
        "policy_version": policy.policy_version,
        "plan_version": policy.plan_version,
        "stage": request.stage,
        "outcome": "consent_requested",
        "operation_mode": policy.operation_mode,
        "authorizing_policy": policy.policy_version,
        "file_sensitivity": requirement.handling_class,
        "excerpts_included": (),
        "redaction_applied": False,
        "redaction_manifest": (),
        "model": {"locality": request.model_target.locality,
                  "model_id": request.model_target.model_id,
                  "provider": request.model_target.provider},
        "content_hashes": tuple(content_hashes),
        "content_hash": content_hashes[0] if len(tuple(content_hashes)) == 1 else None,
        "prompt_fingerprint": request.prompt_fingerprint,
        "file_id": file_ids[0] if len(file_ids) == 1 else None,
        "file_ids": file_ids,
        "group_id": request.target.group_id,
        "consent_request_id": consent_request_id,
        "user_id": user_id,
        "observed_at": observed_at,
        "appended_at": observed_at,
    }
    unfilled = [name for name in AUDIT_FIELDS if name not in values]
    if unfilled:
        raise ValueError(
            f"SPEC §7 names {unfilled} and the consent path has no value for them; a "
            "field Task 10 publishes must be filled at the seam, not defaulted"
        )
    record = AuditRecord(**{name: values[name] for name in AUDIT_FIELDS})
    append_audit(conn, record, author=SUBSYSTEM,
                 component_version=component_version, extra={
                     "requirement": _requirement_form(requirement),
                     "options": list(needs.options),
                 })
    return needs


def pending_consent(conn: sqlite3.Connection,
                    consent_request_id: str) -> NeedsConsent | None:
    """The open question, or None if it was never asked or has been answered."""
    asked = _event_for(conn, CONSENT_REQUESTED, consent_request_id)
    if asked is None:
        return None
    if _event_for(conn, CONSENT_GRANTED, consent_request_id) is not None:
        return None
    payload = json.loads(asked["explanation"])
    return NeedsConsent(consent_request_id=consent_request_id,
                        requirement=_requirement_from(payload["requirement"]),
                        options=tuple(payload["options"]))


def record_consent_choice(conn: sqlite3.Connection, consent_request_id: str,
                          option: str, *, policy: Policy, scope: str,
                          user_id: str, component_version: str,
                          observed_at: str) -> None:
    """Record the user's answer, and grant only where the answer authorizes a model.

    Returns None. SPEC §6: "the gate owns the policy, so the caller does not supply
    this value, it echoes it" -- handing a freshly minted `policy_version` back from a
    consent recorder would give the caller a value from a path that is not the gate.
    The caller re-reads `current_policy`, which it has to do anyway: the original
    request is never resumed.

    `scope` has no default. Open question 3: "What is a 'corpus area'? ... Consent
    grants cannot be scoped until this is named."
    """
    if option not in CONSENT_OPTIONS:
        raise UnknownConsentOption(
            f"{option!r} is not among §8.4's four options {CONSENT_OPTIONS}"
        )
    if _event_for(conn, CONSENT_REQUESTED, consent_request_id) is None:
        raise UnknownConsentRequest(
            f"no consent_requested event carries {consent_request_id!r}"
        )
    if _event_for(conn, CONSENT_GRANTED, consent_request_id) is not None:
        raise ConsentAlreadyRecorded(
            f"{consent_request_id!r} already has an answer; P8's SPEC: 'the caller "
            "composes a NEW ModelCallRequest under the chosen option; the original is "
            "never resumed'"
        )
    authorized = CONSENT_AUTHORIZES[option]
    if authorized:
        grant_consent(conn, policy, scope, option, user_id=user_id,
                      component_version=component_version, observed_at=observed_at)
    append_event(conn, **event_defaults(
        event_type=CONSENT_GRANTED,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "consent_request_id": consent_request_id,
            "option": option,
            "authorized": authorized,
            _SCOPE_KEY: scope,
            "collected_by": "P13",
        }),
    ))
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_consent.py -v`
Expected: PASS — 26 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–14 green, and the 1300 P1–P5 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/consent.py tests/p7/test_p7_consent.py
git commit -m "feat(P7): NeedsConsent, its consent_request_id, and the P13 seam"
```

---

## What this section leaves for its neighbours

| Left open | Owner | Why it is not closed here |
|---|---|---|
| `Gate.release` calling `mint_release` after `append_audit` and before returning | Task 11 | The facade is Task 11's file. Task 12 proves the ledger; the wiring is one call in `gate.py`. |
| `Gate.release` collecting triggered reasons and calling `first_reason` | Task 11 | Same. Task 13 publishes the order and the resolver; the collection is the facade's. |
| `append_audit`'s `extra` keyword | Task 10 | SPEC §7 enumerates a release record, and a denial's `reason` and a consent request's `requirement` have no field in it. Reported in the additions table. |
| `audit_records_for(file_id=…)` matching the explanation's `file_ids`, not only the column | Task 10 | `events` has one `file_id` column. Without this, Task 15's `prior_releases` under-reports every group-scoped release. Reported. |
| `policy.grant_consent` appending no event | Task 5 | Pinned here, as the mirror of Task 15's ruling for `revoke_consent`. |
| `Denied` carrying `evidence_refs` | Task 11 | The skeleton's own `deny(...)` takes them and SPEC §6 requires the explanation be evidence-referenced. |
| `release.py` re-exporting `NeedsConsent` and importing no other `privacy` module | Task 11 | The import-direction rule above. It is the one constraint these tasks place on Task 11. |
| Whether a caller absorbs `NeedsConsent` | P8 Done-means 13, P13 Done-means 16 | *"P7's obligation is to make the absorption unrepresentable, not to police it."* |
| A detector that produces a `ClassificationRecord` | **Nobody, and that is the finding** | D2 put the rule set behind an injection and no task in any plan supplies one. Until it is, `Denied(unclassified)` is every real file's verdict, which is what Task 13 is built for. |
