# P7 — Privacy and consent gate — PLAN, Tasks 17–19

> This file is one section of P7's implementation plan. Tasks 1–14 are written by other authors
> against the same [`PLAN-SKELETON.md`](PLAN-SKELETON.md); Tasks 15–16 are written in
> [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md) and everything both publish is consumed here under
> the names their `Interfaces:` blocks fix. Format and standard are
> [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md) and
> [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md).

**Verified against the live substrate, 2026-08-22.** `pytest tests/ -q` → **1300 passed** on
Python 3.12.4; P1–P5 are green. Every P1/P4 signature quoted below was read with
`inspect.signature` against the shipped packages, not from a PLAN:

- `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row` and
  `record_file(conn, path, *, filename, normalized_filename, extension, observed_size,
  observed_timestamps, parent_folder_context, mime_type, detected_format, scan_state,
  materialized, content_hash=None) -> str`. `record_file` computes the digest itself when
  `content_hash` is omitted, so `get_file(conn, file_id)["content_hash"]` is populated for a
  fixture file. **The stored digest carries no `sha256:` prefix** — checked live — so nothing below
  asserts one.
- `database_agent.files_table.set_sensitivity_state(conn, file_id, *, state: dict, author: str,
  component_version: str) -> None` exists (D2). Neither module in this section calls it: **all three
  of these tasks are readers.**
- `FILES_COLUMNS` is sixteen and includes `sensitivity_state`.

The rename settled on 2026-08-22 applies here as [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md)
applied it: the skeleton's `facts_seam.SensitivityFacts` in Tasks 17 and 18 is
`privacy.classification_store.ClassificationStore`, a concrete store over a table P7 owns —
`current(file_id, content_hash)`, `current_fact_id(...)`, `write(record)`,
`supersede(old, new, reason)`, `history(file_id)`.

---

## Four rulings that bind this section, applied rather than restated

**C4: these two modules refuse, and they write nothing.** *"the gate still raises and writes nothing
— a gate that also wrote would be doing two jobs."* `may_move_automatically` and
`summarize_protected` are **predicates over stored state**. They append no event, mint no policy
version, and issue no `UPDATE files`. They are not even the release path: §8.4's automatic-move
sentence and its display sentence are the two surfaces P7 publishes *outside* the model path
(SPEC *Purpose*). Each task carries a test that the event count is unchanged across the call, so
"writes nothing" is asserted rather than assumed.

**D2: the detector is unwritten, so absence is the ordinary case.** No task in any plan produces a
rule set. On a real corpus `ClassificationStore.current(...)` returns `None` for every file, and
Task 17's verdict is `unreadable_unclassified` for every file while Task 18's `count` is zero.
Both are correct answers, both are stated in a named test, and neither is a public/low class —
§8.6: cost exhaustion *"must never turn into lower-quality automatic classification"*, and the
failure that rule forbids is exactly defaulting an unclassified file to `public_low` so the
pipeline can continue.

**SPEC §2 and Open question 1: the `protected` flag decides, never the class.** *"Neighbouring
parts should consume the `protected` flag, not infer it from the class."* Task 17 keys on the flag
and Task 18 counts on the flag. Two tests construct the two records that would break an inference —
`public_low` with `protected=True` and `highly_sensitive_credential_bearing` with
`protected=False` — and assert the flag wins in both directions.

**Task 19 is an instrument, and the property it measures is P8's.** The coverage table already
says so of Done-means 3: *"**No — and this is a finding.** The transport is P8's. P7 proves the
instrument, the unforgeable token, and the single materialisation locus. The property itself is P8
Done-means 1."* P8's own Done-means 1 states the method — *"Verified by inspection plus a test that
the un-released path does not type-check / does not exist"* — and that is precisely what
`assert_single_egress` is: an **existence proof over a module namespace**, not a runtime check on a
call. It answers "does a string-prompt entry point exist in this module?" and it answers it by
resolving annotations, never by reading source text.

---

## Additions to the skeleton's `Interfaces:` blocks, reported rather than smuggled

Each is additive — no published name changes meaning, so the agents writing Tasks 1–16 and 20–22 in
parallel are unaffected.

1. **`display_policy` gains a required `plan_version` keyword.** SPEC §10 spells it
   `Gate.display_policy() -> RedactionSettings` and the skeleton spells it `display_policy(conn)`,
   but redaction settings live on `Policy`, and §8.8 places *"Privacy and model-consent policies"*
   inside the plan version. Task 5's reader is `current_policy(conn, *, plan_version)`. A
   `display_policy` with no plan version would have to pick one, which is exactly the silent choice
   §8.8 forbids. Signature: `display_policy(conn, *, plan_version) -> RedactionSettings`.
2. **`summarize_protected` gains a required `files_in_scope` keyword.** Same device, same reason and
   same wording as Task 15's `revoke`: Open question 3 — *"What is a 'corpus area'? … Consent grants
   cannot be scoped until this is named"* — is unanswered, so P7 cannot enumerate the files a scope
   covers and must not guess. The caller supplies `Callable[[str], Sequence[str]]`. Signature:
   `summarize_protected(conn, scope, *, files_in_scope) -> ProtectedSummary`.
3. **Task 18 publishes `settings_for(policy) -> RedactionSettings`, `FACET_VALUES`, `SHOWN`,
   `REDACTED`, `check_facet_value` and `UnknownFacetValue`.** SPEC §10 gives the two values —
   *"each `shown | redacted`"* — and Task 2's `Produces` block stops at `DISPLAY_FACETS`, so the
   value vocabulary has no other home. `settings_for` is the pure half of `display_policy`: it is
   what lets the fresh-install assertion run against `defaults.resolve_default_policy(None)` without
   this task taking a position on what `current_policy` does when nothing is stored, which is
   Task 5's to decide.
4. **Task 19 publishes `EgressGuardFailure` and `NoEgressPoint`** beside the skeleton's
   `MultipleEgressPoints` and `UnreleasedContentParameter`. Done-means 3 says *"exactly one entry
   point"*, and zero violates it as surely as two; calling a module with no entry point
   `MultipleEgressPoints` would be a lie in the exception name. `EgressGuardFailure` is the shared
   base so a test that does not care which failure occurred can catch one thing.
5. **Task 17's `automatic_move_permissions` is read as `Mapping[str, bool]` keyed by the grant's
   scope, and the only key P7 resolves is the `file_id`.** §8.4 requires a policy that
   *"explicitly permits it"*; a per-file key is the one key that is explicit without answering Open
   question 3. A grant recorded at any other key is not read as covering this file, and a test says
   so and names OQ3. This pins one field of Task 5's `Policy` for it; reported.

---

## Tasks

### Task 17: `may_move_automatically`

**Files:**
- Create: `src/privacy/moves.py`
- Test: `tests/p7/test_p7_moves.py`

**Interfaces:**
- Consumes: `privacy.classification.ClassificationRecord`,
  `privacy.classification.resolve_class(record: ClassificationRecord | None) -> str`,
  `privacy.classification_store.ClassificationStore` (`current(file_id, content_hash)
  -> ClassificationRecord | None`; the test also uses `current_fact_id`, `write` and
  `supersede`), `privacy.policy.Policy`, `privacy.policy.set_policy` (test only),
  `privacy.policy.current_policy(conn, *, plan_version) -> Policy`,
  `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row`.
- Produces (`moves.py`):
  - `NOT_PROTECTED: str = "not_protected"`
  - `POLICY_PERMITS: str = "policy_permits"`
  - `PROTECTED_WITHOUT_PERMITTING_POLICY: str = "protected_without_permitting_policy"`
  - `UNREADABLE_UNCLASSIFIED: str` — bound to `resolve_class(None)`, never typed a second time.
  - `MOVE_REASONS: tuple[str, ...]` — those four, in decision order.
  - `MoveVerdict` — frozen: `allowed: bool`, `reason: str`, `permitting_policy: str | None`.
  - `may_move_automatically(conn, file_id, plan_version) -> MoveVerdict`.

**Done-means:** 9, first clause. The coverage table holds the second: *"**Partly.** First clause
yes. The second is a property of P11 and P12, which do not exist; P7 makes it *possible* by naming
the permitting policy in the verdict."* A named test in this file carries that sentence so the
limitation lives in the suite rather than in a report nobody rereads.

**Three design sentences, none of them P7's, and each decides a branch.**

1. §8.4, verbatim: *"Protected material should not be included in cloud-model prompts by default,
   should not display raw content in general group summaries, and should not be moved automatically
   without a user policy that explicitly permits it."* — the third clause is this predicate.
2. §7.11, verbatim: the system *"must not delete files, mark them disposable, or move them out of a
   protected area without explicit user action."* This is why the refusal is the default branch and
   the permission is the exception, rather than the other way round.
3. §8.8, verbatim: *"A new plan should never silently reclassify or move old files."* The policy is
   read **at the asked-for plan version**, so a permission adopted later does not reach backwards
   and one adopted earlier does not leak forwards.

**The classification is not plan-scoped and the policy is.** §8.8: *"The evidence database remains
shared across plan versions, but the destination tree and user policy define which projections are
valid in each version."* So `ClassificationStore.current(...)` takes no plan version and
`current_policy(...)` requires one. That asymmetry is the whole of the §8.8 behaviour and it is
not a choice this task makes.

**`UNREADABLE_UNCLASSIFIED` is bound to `resolve_class(None)` rather than typed.** Task 3 owns the
rule that absence resolves to that class and refuses to resolve it to `public_low`. Spelling the
string a second time here would create a second place for the two to disagree, which is the defect
class this project has recorded most often. The module-level binding evaluates Task 3's function at
import, so a change there is a failing test here rather than a silent divergence.

**The order of the branches is load-bearing.** Absence is checked **before** the flag, because a
file nothing has classified has no `protected` flag to read and "no flag" must never be read as
"flag false". Then the flag, then the policy. A predicate that checked the flag first would answer
`not_protected` for every file in a corpus with no detector — the exact §8.6 failure, arrived at
from a different direction.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_moves.py
"""Done-means 9's first clause: §8.4's automatic-move predicate.

Three sentences decide every assertion here and none of them is P7's. §8.4: protected
material "should not be moved automatically without a user policy that explicitly
permits it." §7.11: the system "must not delete files, mark them disposable, or move
them out of a protected area without explicit user action." §8.8: "A new plan should
never silently reclassify or move old files."

The fourth fact is D2's, and it is why so much of this file is about absence: no
detector exists, so on a real corpus `store.current(...)` returns None for every file
and the verdict is `unreadable_unclassified` every time. That is the honest posture
rather than a gap, and one test says so by name.
"""
import dataclasses
import json

import pytest

from database_agent.files_table import get_file, record_file

from privacy.authorship import SUBSYSTEM
from privacy.classification import ClassificationRecord, resolve_class
from privacy.classification_store import ClassificationStore
from privacy.moves import (
    MOVE_REASONS, NOT_PROTECTED, POLICY_PERMITS,
    PROTECTED_WITHOUT_PERMITTING_POLICY, UNREADABLE_UNCLASSIFIED, MoveVerdict,
    may_move_automatically,
)
from privacy.policy import Policy, set_policy

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
PLAN_ONE = "plan-1"
PLAN_TWO = "plan-2"


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """A real P1 row: the classification is keyed on (file_id, content_hash) and a
    synthesized id would not exercise the hash lookup the predicate performs."""
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


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version=PLAN_ONE,
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


def stored(conn, **over) -> str:
    """Store a policy; return the version the gate minted for it.

    SPEC §6: "the gate owns the policy, so the caller does not supply this value, it
    echoes it." The tests below compare the verdict against the RETURNED version, not
    against the placeholder `a_policy` carries in, which is what makes
    `permitting_policy` a fact P11 and P12 can record rather than a value the caller
    already had.
    """
    return set_policy(conn, a_policy(**over), author=SUBSYSTEM,
                      component_version=COMPONENT, user_id="joseph")


def classify(store, file_id, content_hash, *, handling_class, protected):
    """Stand in for the detector that does not exist (D2).

    `basis = "user"` rather than `"detector"`, because Task 3 raises
    `UnbackedClassification` on a detector record with no `evidence_refs` and this
    test has no detector to have fired.

    A second call supersedes the first through Task 4's `current_fact_id` and
    `supersede`, which is Task 16's `reclassify` path rather than a second current
    record: §8.2 forbids overwriting, and two unsuperseded records would leave
    `current(...)` ambiguous and this file testing the wrong thing.
    """
    prior_fact_id = store.current_fact_id(file_id, content_hash)
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis="user", evidence_refs=(),
        reliability_state="user_confirmed", observed_at=FIXED_CLOCK)
    fact_id = store.write(record)
    if prior_fact_id is not None:
        store.supersede(prior_fact_id, fact_id, "the fixture revises its own record")
    return record


# --- the shape SPEC §9 published ---------------------------------------------

def test_the_verdict_carries_specs_three_fields_and_no_fourth(p7_conn):
    # SPEC §9: `Gate.may_move_automatically(file_id, plan_version) -> { allowed,
    # reason, permitting_policy? }`. Read off the dataclass, never off the class body.
    assert [f.name for f in dataclasses.fields(MoveVerdict)] == [
        "allowed", "reason", "permitting_policy"]


def test_the_four_reasons_are_the_only_ones_the_predicate_can_return(
        p7_conn, file_id, content_hash, store):
    assert len(MOVE_REASONS) == 4
    assert set(MOVE_REASONS) == {
        NOT_PROTECTED, POLICY_PERMITS, PROTECTED_WITHOUT_PERMITTING_POLICY,
        UNREADABLE_UNCLASSIFIED}
    seen = set()
    stored(p7_conn)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    stored(p7_conn, plan_version=PLAN_TWO,
           automatic_move_permissions={file_id: True})
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_TWO).reason)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=False)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    assert seen == set(MOVE_REASONS)


# --- absence, which is every file until a detector exists ---------------------

def test_absence_of_a_classification_refuses_and_never_reads_as_public(
        p7_conn, file_id):
    # D2: "Unreadable or unclassified is a GATE OUTCOME, not a file fact." §8.6: cost
    # exhaustion "must never turn into lower-quality automatic classification" -- the
    # forbidden move is exactly resolving absence to a low class so work can continue.
    stored(p7_conn)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == UNREADABLE_UNCLASSIFIED
    assert verdict.reason == "unreadable_unclassified"
    assert verdict.reason != "public_low"
    assert verdict.permitting_policy is None


def test_the_unclassified_reason_is_task_3s_value_and_not_a_second_spelling():
    # One string, one owner. A second literal here is a second place for the two to
    # disagree, and Task 3 owns the rule that absence resolves to this class.
    assert UNREADABLE_UNCLASSIFIED == resolve_class(None)


def test_with_no_detector_every_file_gets_that_verdict(p7_conn, tmp_path):
    # The honest v1 posture, stated in the suite rather than in a report. No task in
    # any plan produces a detector rule set (D2), so this is what a real corpus looks
    # like on the day P7 ships: a correct, locked door with nobody holding a key.
    stored(p7_conn)
    corpus = tmp_path / "many"
    corpus.mkdir()
    for index in range(3):
        document = corpus / f"file-{index}.pdf"
        document.write_bytes(f"%PDF-1.4 body {index}".encode())
        new_id = record_file(
            p7_conn, document, filename=document.name,
            normalized_filename=document.name.lower(), extension=".pdf",
            observed_size=document.stat().st_size,
            observed_timestamps=json.dumps({"mtime": 1.0}),
            parent_folder_context=str(corpus), mime_type="application/pdf",
            detected_format="pdf", scan_state="fixture-scan-state",
            materialized=True)
        verdict = may_move_automatically(p7_conn, new_id, PLAN_ONE)
        assert verdict == MoveVerdict(allowed=False,
                                      reason=UNREADABLE_UNCLASSIFIED,
                                      permitting_policy=None)


# --- protected material, with and without a permitting policy -----------------

def test_protected_material_without_a_permitting_policy_cannot_move(
        p7_conn, file_id, content_hash, store):
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it." §7.11: the system must not "move them out of
    # a protected area without explicit user action."
    stored(p7_conn)
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY


def test_a_policy_that_explicitly_permits_this_file_allows_the_move(
        p7_conn, file_id, content_hash, store):
    stored(p7_conn, automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is True
    assert verdict.reason == POLICY_PERMITS


def test_the_permitting_policy_is_named_in_the_verdict(
        p7_conn, file_id, content_hash, store):
    # Done-means 9's second clause depends on this field existing: P11 records the
    # answer in the placement decision (§6.11 "required review policy") and P12 in the
    # plan precondition (§8.3 "Sensitivity and consent state"), and neither re-derives
    # it. The version asserted is the one the GATE minted, not the placeholder in.
    version = stored(p7_conn, automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy == version


def test_a_refusal_names_no_permitting_policy(
        p7_conn, file_id, content_hash, store):
    # There is no policy to name, and naming one would let a caller record a
    # permission that never existed.
    stored(p7_conn)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy is None
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy is None


def test_a_withdrawn_permission_does_not_permit(
        p7_conn, file_id, content_hash, store):
    # §8.7's recorded action is "granting or withdrawing an automatic-move permission
    # for protected material". A withdrawal is a stored `False`, not an absent key,
    # and both refuse -- but only the stored `False` proves the branch reads the value
    # rather than the presence of the key.
    stored(p7_conn, automatic_move_permissions={file_id: False})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY


def test_a_grant_at_a_scope_p7_cannot_resolve_does_not_permit(
        p7_conn, file_id, content_hash, store):
    # Open question 3: "What is a 'corpus area'? ... Consent grants cannot be scoped
    # until this is named." P7 defines no area, so the only key it can resolve to a
    # file is the file's own id. A grant at "Academics" is not read as covering this
    # file, and the alternative -- guessing that it does -- would widen egress policy
    # on an unanswered question.
    stored(p7_conn, automatic_move_permissions={"Academics": True, "/Users/jy": True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False


# --- the flag, not the class (SPEC §2, Open question 1) -----------------------

def test_a_file_that_is_not_protected_may_move(
        p7_conn, file_id, content_hash, store):
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=False)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is True
    assert verdict.reason == NOT_PROTECTED
    assert verdict.permitting_policy is None


def test_the_verdict_keys_on_the_flag_and_not_the_handling_class(
        p7_conn, file_id, content_hash, store):
    # SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    # from the class." Open question 1 -- whether `protected` is exactly the top two
    # classes -- is unsettled, so both records below are legal and the flag wins in
    # both directions.
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=False)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is True


# --- §8.8: the plan version is not decoration ---------------------------------

def test_a_later_plan_version_does_not_retroactively_permit(
        p7_conn, file_id, content_hash, store):
    # §8.8: "A new plan should never silently reclassify or move old files." The
    # permission is adopted at plan-2; asking under plan-1 must not see it.
    stored(p7_conn, plan_version=PLAN_ONE, automatic_move_permissions={})
    stored(p7_conn, plan_version=PLAN_TWO,
           automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False
    assert may_move_automatically(p7_conn, file_id, PLAN_TWO).allowed is True


def test_a_permission_does_not_leak_forward_into_a_later_plan_either(
        p7_conn, file_id, content_hash, store):
    # The symmetric half. §8.8 makes the user policy one of the two things that
    # "define which projections are valid in each version", so a permission granted
    # under plan-1 is not in force under plan-2 unless plan-2 carries it too.
    stored(p7_conn, plan_version=PLAN_ONE,
           automatic_move_permissions={file_id: True})
    stored(p7_conn, plan_version=PLAN_TWO, automatic_move_permissions={})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is True
    assert may_move_automatically(p7_conn, file_id, PLAN_TWO).allowed is False


def test_the_classification_is_shared_across_plan_versions(
        p7_conn, file_id, content_hash, store):
    # §8.8: "The evidence database remains shared across plan versions." The
    # classification is looked up with no plan version at all; only the policy is
    # plan-scoped, and that asymmetry is §8.8's and not this task's.
    stored(p7_conn, plan_version=PLAN_ONE, automatic_move_permissions={})
    stored(p7_conn, plan_version=PLAN_TWO, automatic_move_permissions={})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    for plan_version in (PLAN_ONE, PLAN_TWO):
        assert may_move_automatically(
            p7_conn, file_id, plan_version).reason == (
                PROTECTED_WITHOUT_PERMITTING_POLICY)


# --- C4: a predicate writes nothing -------------------------------------------

def test_the_predicate_writes_nothing(p7_conn, file_id, content_hash, store):
    # C4: "a gate that also wrote would be doing two jobs." This one does not even
    # release; it answers a question P11 and P12 ask before they plan a move.
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    mirror = get_file(p7_conn, file_id)["sensitivity_state"]
    for plan_version in (PLAN_ONE, PLAN_TWO, PLAN_ONE):
        may_move_automatically(p7_conn, file_id, plan_version)
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert get_file(p7_conn, file_id)["sensitivity_state"] == mirror


# --- the half of Done-means 9 that cannot be proved here ----------------------

def test_p11_and_p12_consuming_the_answer_is_not_provable_inside_p7(p7_conn):
    """Done-means 9's second clause is a property of two parts that do not exist.

    The coverage table states it: "**Partly.** First clause yes. The second is a
    property of P11 and P12, which do not exist; P7 makes it *possible* by naming the
    permitting policy in the verdict." §6.11's "required review policy" and §8.3's
    "Sensitivity and consent state" are where the answer lands, and neither field has
    a schema in this repository yet.

    What P7 can assert is that the verdict is complete enough to be recorded without
    re-derivation: three fields, and the permitting policy named whenever one
    permitted. That is asserted above. The rest is P11's and P12's, and this test
    exists so the limitation is in the suite rather than in a report nobody rereads.
    """
    assert [f.name for f in dataclasses.fields(MoveVerdict)] == [
        "allowed", "reason", "permitting_policy"]
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_moves.py -v`
Expected: FAIL — `ImportError: cannot import name 'MOVE_REASONS' from 'privacy.moves'` (the module
does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/moves.py`**

```python
# src/privacy/moves.py
"""§8.4's automatic-move predicate — one of the two surfaces P7 publishes off the model path.

§8.4's sentence is the whole specification: protected material "should not be included
in cloud-model prompts by default, should not display raw content in general group
summaries, and should not be moved automatically without a user policy that explicitly
permits it." The third clause is this module. §7.11 states the same rule from the
residual side -- the system "must not delete files, mark them disposable, or move them
out of a protected area without explicit user action" -- which is why refusal is the
default branch and permission is the exception.

Three properties are deliberate and each has a test:

- **Absence is checked first.** A file nothing has classified has no `protected` flag,
  and "no flag" must never be read as "flag false". The verdict is
  `unreadable_unclassified`, which is Task 3's value and not a second spelling of it.
  With no detector built (D2) this is the verdict for every file in a real corpus.
- **The flag decides, never the class.** SPEC §2: "Neighbouring parts should consume
  the `protected` flag, not infer it from the class", and Open question 1 -- whether
  `protected` is exactly the top two classes -- is unsettled.
- **The policy is read at the asked-for plan version and the classification is not.**
  §8.8: "The evidence database remains shared across plan versions, but the destination
  tree and user policy define which projections are valid in each version", and "A new
  plan should never silently reclassify or move old files."

This module writes nothing (C4). It appends no event, mints no policy version and
issues no `UPDATE files`.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.files_table import get_file

from privacy.classification import resolve_class
from privacy.classification_store import ClassificationStore
from privacy.policy import current_policy

#: The file carries no `protected` flag, so §8.4's restriction does not attach.
NOT_PROTECTED: str = "not_protected"

#: Protected, and a user policy at this plan version explicitly permits this file.
POLICY_PERMITS: str = "policy_permits"

#: Protected, and no policy at this plan version permits it. §8.4's default answer.
PROTECTED_WITHOUT_PERMITTING_POLICY: str = "protected_without_permitting_policy"

#: Nothing has classified this file. Bound to Task 3's resolver rather than typed a
#: second time: Task 3 owns the rule that absence resolves here and never to
#: `public_low`, and two literals would be two places for one rule to drift.
UNREADABLE_UNCLASSIFIED: str = resolve_class(None)

#: The four, in the order the predicate decides them.
MOVE_REASONS: tuple[str, ...] = (
    UNREADABLE_UNCLASSIFIED,
    NOT_PROTECTED,
    POLICY_PERMITS,
    PROTECTED_WITHOUT_PERMITTING_POLICY,
)


@dataclass(frozen=True)
class MoveVerdict:
    """SPEC §9's return: `{ allowed, reason, permitting_policy? }`.

    `permitting_policy` is populated only when a policy permitted the move, and it
    carries the `policy_version` the gate minted. P11 records it in the placement
    decision (§6.11 "required review policy") and P12 in the plan precondition (§8.3
    "Sensitivity and consent state"); neither re-derives the answer, and neither can
    record a permission that did not exist, because a refusal names none.
    """

    allowed: bool
    reason: str
    permitting_policy: str | None


def may_move_automatically(conn: sqlite3.Connection, file_id: str,
                           plan_version: str) -> MoveVerdict:
    """May P11/P12 move this file without asking the user, under this plan version?

    Reads only. The branch order is absence, then the flag, then the policy, and it
    is not interchangeable: checking the flag first would answer `not_protected` for
    every file in a corpus nothing has classified, which is §8.6's forbidden move --
    "Cost exhaustion must never turn into lower-quality automatic classification" --
    reached from a different direction.
    """
    content_hash = get_file(conn, file_id)["content_hash"]
    record = ClassificationStore(conn).current(file_id, content_hash)
    if record is None:
        return MoveVerdict(allowed=False, reason=UNREADABLE_UNCLASSIFIED,
                           permitting_policy=None)
    if not record.protected:
        return MoveVerdict(allowed=True, reason=NOT_PROTECTED,
                           permitting_policy=None)
    policy = current_policy(conn, plan_version=plan_version)
    if policy.automatic_move_permissions.get(file_id) is True:
        return MoveVerdict(allowed=True, reason=POLICY_PERMITS,
                           permitting_policy=policy.policy_version)
    return MoveVerdict(allowed=False, reason=PROTECTED_WITHOUT_PERMITTING_POLICY,
                       permitting_policy=None)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_moves.py -v`
Expected: PASS — 18 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–17 green, and the 1300 P1–P5 tests still green (P7 modified no file
belonging to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/moves.py tests/p7/test_p7_moves.py
git commit -m "feat(P7): may_move_automatically, keyed on the protected flag and the asked-for plan version"
```

---

### Task 18: `display_policy` and `summarize_protected`

**Files:**
- Create: `src/privacy/display.py`
- Test: `tests/p7/test_p7_display.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.DISPLAY_FACETS` (§8.4's five),
  `privacy.vocabulary.HANDLING_CLASSES` (§8.4's five, for the breakdown's key order),
  `privacy.defaults.MORE_REDACTING: Mapping[str, str]`,
  `privacy.defaults.resolve_default_policy(stored) -> Policy` (test only),
  `privacy.policy.Policy`, `privacy.policy.current_policy(conn, *, plan_version) -> Policy`,
  `privacy.policy.set_policy` (test only),
  `privacy.classification_store.ClassificationStore`, `privacy.classification.ClassificationRecord`,
  `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row`.
- Produces (`display.py`):
  - `SHOWN: str = "shown"`, `REDACTED: str = "redacted"`,
    `FACET_VALUES: tuple[str, str] = (SHOWN, REDACTED)`.
  - `UnknownFacetValue`, `check_facet_value(value) -> str`.
  - `RedactionSettings` — frozen: `names`, `previews`, `thumbnails`, `ocr_text`, `location_data`,
    each `str` and each one of `FACET_VALUES`.
  - `settings_for(policy: Policy) -> RedactionSettings`.
  - `display_policy(conn, *, plan_version) -> RedactionSettings`.
  - `ProtectedSummary` — frozen: `count: int`, `class_breakdown: Mapping[str, int]`.
  - `summarize_protected(conn, scope, *, files_in_scope) -> ProtectedSummary`.

**Done-means:** 10, and the display half of 12. The coverage table on 10: *"**Yes** — proven at the
type level over `dataclasses.fields`."*

**§8.4's UI paragraph is four sentences and three of them are load-bearing here.** Grepped, not
recalled — `00-database-agent-product-design.md`:

> Privacy also applies to the user interface. A summary such as "11 protected identity records" may
> be safe to show, while a visible list of passport filenames on a shared screen may not be.
> Protected branches should have configurable redaction in the canvas and review screens. The user
> can choose whether names, previews, thumbnails, OCR text, or location data are shown.

Sentence two is the acceptance criterion for `summarize_protected`; sentence three is P13's Open
question 7; sentence four is the five facets, in that order. §7.5's residual surfacing screen
already renders the same form — *"11 protected personal records"* — and §5.2 applies the rule to the
tree canvas: a Finance or Identity proposal *"may be visible as a protected area, but the product
should avoid showing sensitive filenames."*

**`ProtectedSummary` is safe at the type level, not by a filter.** The skeleton is explicit that
this must be *"a type-level proof, not a runtime filter that a future caller could pass around, and
not a string scan."* The dataclass has two fields, an `int` and a `Mapping[str, int]`, and there is
no field a filename could occupy. The test asserts that with `typing.get_type_hints`, so an added
`examples: tuple[str, ...]` field is a failing test on the day it is written rather than a review
finding on the day it ships. The `class_breakdown` keys are handling classes drawn from
`HANDLING_CLASSES`, asserted as a subset, so the one `str`-shaped surface in the record is a closed
vocabulary rather than free text.

**The default is the more redacting value, per facet, and the rule applies to a facet the policy
does not mention.** W1's second clause: *"Where the design is silent on a redaction default, the
more redacting option is the default. Data-minimizing is the second half of the same `must`."* A
facet absent from `Policy.redaction_settings` **is** the design being silent, so the fallback is
per-facet and not only per-policy. That is why `settings_for` resolves each of `DISPLAY_FACETS`
independently instead of accepting the mapping whole.

**Why `settings_for` exists as a separate function.** Task 6's fresh-install obligation is stated
over `resolve_default_policy(stored)`, and what `current_policy` does when nothing at all is stored
is Task 5's to decide. Splitting the pure resolution out lets Done-means 12's display half be
asserted as `settings_for(resolve_default_policy(None))` without this task taking a position on a
neighbour's unstated behaviour — and it keeps `display_policy` to one line, which is the whole of
its content.

**`summarize_protected` counts the flag, and nothing else.** Not the class: Open question 1 is
unsettled. Not the unclassified: a file nothing has looked at is not a protected record, and with
no detector built that is every file, so the honest summary of a real corpus today is `count = 0`.
A named test says that zero is not a claim that nothing is sensitive — the same distinction §8.6
draws when it forbids *"the false impression that an unprocessed file was understood and found
unimportant."*

**This module writes nothing (C4)** and it never resolves an excerpt: no P4 text materialiser is
imported here, which Task 21 re-asserts repo-wide as layer L2.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_display.py
"""Done-means 10, and the display half of Done-means 12.

§8.4's UI paragraph, quoted from the design and not from a memory of it:

    "Privacy also applies to the user interface. A summary such as '11 protected
    identity records' may be safe to show, while a visible list of passport filenames
    on a shared screen may not be. Protected branches should have configurable
    redaction in the canvas and review screens. The user can choose whether names,
    previews, thumbnails, OCR text, or location data are shown."

Sentence two is the acceptance criterion for `summarize_protected`; sentence three is
P13's Open question 7, recorded here and not resolved; sentence four is the five
facets in the order this file asserts them.
"""
import dataclasses
import inspect
import json
from collections.abc import Mapping
from typing import get_type_hints

import pytest

from database_agent.files_table import get_file, record_file

from privacy.authorship import SUBSYSTEM
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING, resolve_default_policy
from privacy.display import (
    FACET_VALUES, REDACTED, SHOWN, ProtectedSummary, RedactionSettings,
    UnknownFacetValue, check_facet_value, display_policy, settings_for,
    summarize_protected,
)
from privacy.policy import Policy, set_policy
from privacy.vocabulary import DISPLAY_FACETS, HANDLING_CLASSES

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
PLAN_ONE = "plan-1"

#: §8.4's own sentence, in §8.4's own order. A reordering here is a failing test, not
#: an editorial choice: the facets are a closed vocabulary (SPEC §10).
EIGHT_FOUR_FACETS = ("names", "previews", "thumbnails", "ocr_text", "location_data")


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={facet: REDACTED for facet in EIGHT_FOUR_FACETS},
                automatic_move_permissions={}, plan_version=PLAN_ONE,
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


def stored(conn, **over) -> str:
    return set_policy(conn, a_policy(**over), author=SUBSYSTEM,
                      component_version=COMPONENT, user_id="joseph")


@pytest.fixture()
def corpus(p7_conn, tmp_path):
    """A small real corpus. `record_file` computes the digest, and the classification
    is keyed on it, so nothing here can be a synthesized id."""
    root = tmp_path / "corpus"
    root.mkdir()

    def add(name: str) -> str:
        document = root / name
        document.write_bytes(f"%PDF-1.4 {name}".encode())
        return record_file(
            p7_conn, document, filename=document.name,
            normalized_filename=document.name.lower(), extension=".pdf",
            observed_size=document.stat().st_size,
            observed_timestamps=json.dumps({"mtime": 1.0}),
            parent_folder_context=str(root), mime_type="application/pdf",
            detected_format="pdf", scan_state="fixture-scan-state",
            materialized=True)

    return add


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


def classify(conn, store, file_id, *, handling_class, protected):
    """Stand in for the detector that does not exist (D2). `basis = "user"` because
    Task 3 refuses a `detector` record with no `evidence_refs`."""
    record = ClassificationRecord(
        file_id=file_id, content_hash=get_file(conn, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=FIXED_CLOCK)
    store.write(record)
    return record


def all_of(*file_ids):
    """The `files_in_scope` resolver the caller supplies. Open question 3 -- "What is
    a 'corpus area'?" -- is unanswered, so P7 defines none and the test provides one
    the way P13 will."""
    return lambda scope: tuple(file_ids)


# --- the five facets, and their two values ------------------------------------

def test_the_five_facets_are_8_4s_own_list_in_8_4s_own_order():
    # "The user can choose whether names, previews, thumbnails, OCR text, or location
    # data are shown." Five, and the identifiers follow the sentence.
    assert DISPLAY_FACETS == EIGHT_FOUR_FACETS
    assert [f.name for f in dataclasses.fields(RedactionSettings)] == list(
        EIGHT_FOUR_FACETS)


def test_each_facet_takes_one_of_exactly_two_values():
    # SPEC §10: "names | previews | thumbnails | ocr_text | location_data   each
    # shown | redacted."
    assert FACET_VALUES == (SHOWN, REDACTED) == ("shown", "redacted")
    assert check_facet_value(SHOWN) == SHOWN
    assert check_facet_value(REDACTED) == REDACTED


def test_a_third_facet_value_is_a_load_error():
    # SPEC §1's rule for every closed vocabulary in this part: "A value outside this
    # set is a load error, not a fallback." A `blurred` is a contract revision.
    for value in ("blurred", "partial", "", "SHOWN"):
        with pytest.raises(UnknownFacetValue):
            check_facet_value(value)


def test_every_field_of_the_settings_is_one_of_the_two_values(p7_conn):
    stored(p7_conn)
    settings = display_policy(p7_conn, plan_version=PLAN_ONE)
    for field in dataclasses.fields(RedactionSettings):
        assert getattr(settings, field.name) in FACET_VALUES


# --- W1: the default is the more redacting value ------------------------------

def test_the_more_redacting_value_is_the_default_for_every_facet():
    # W1: "Where the design is silent on a redaction default, the more redacting
    # option is the default." §8.4's example settles the direction -- the aggregate is
    # the default, the expansion is the user's act.
    assert set(MORE_REDACTING) == set(DISPLAY_FACETS)
    assert set(MORE_REDACTING.values()) == {REDACTED}


def test_a_fresh_install_resolves_every_facet_to_redacted():
    # Done-means 12's display half, asserted over Task 6's resolver so this task takes
    # no position on what `current_policy` does with nothing stored -- that is Task 5's.
    settings = settings_for(resolve_default_policy(None))
    assert settings == RedactionSettings(
        names=REDACTED, previews=REDACTED, thumbnails=REDACTED, ocr_text=REDACTED,
        location_data=REDACTED)


def test_a_facet_the_policy_does_not_mention_resolves_to_the_more_redacting_value():
    # A facet absent from the stored mapping IS the design being silent, so the
    # fallback is per-facet and not merely per-policy. This is the branch a partial
    # migration reaches, and it is the one that must not resolve to `shown`.
    settings = settings_for(a_policy(redaction_settings={"names": SHOWN}))
    assert settings.names == SHOWN
    assert settings.previews == REDACTED
    assert settings.thumbnails == REDACTED
    assert settings.ocr_text == REDACTED
    assert settings.location_data == REDACTED


def test_an_empty_settings_mapping_resolves_to_all_redacted():
    assert settings_for(a_policy(redaction_settings={})) == settings_for(
        resolve_default_policy(None))


def test_the_users_expansion_is_honoured(p7_conn):
    # The `must` constrains the DEFAULT, not the user. §8.4: "The user can choose
    # whether names, previews, thumbnails, OCR text, or location data are shown."
    stored(p7_conn, redaction_settings={facet: SHOWN
                                        for facet in EIGHT_FOUR_FACETS})
    settings = display_policy(p7_conn, plan_version=PLAN_ONE)
    assert all(getattr(settings, facet) == SHOWN for facet in DISPLAY_FACETS)


def test_an_out_of_vocabulary_stored_value_is_refused_and_not_coerced(p7_conn):
    # Refusing beats silently substituting `redacted`: a stored value nobody in this
    # vocabulary wrote means the policy row is not what this build thinks it is.
    with pytest.raises(UnknownFacetValue):
        settings_for(a_policy(redaction_settings={"names": "blurred"}))


def test_display_policy_reads_the_policy_at_the_asked_for_plan_version(p7_conn):
    # §8.8 lists "Privacy and model-consent policies" inside the plan version, and
    # redaction settings are part of that policy (SPEC §5).
    stored(p7_conn, plan_version="plan-1",
           redaction_settings={facet: REDACTED for facet in EIGHT_FOUR_FACETS})
    stored(p7_conn, plan_version="plan-2",
           redaction_settings={facet: SHOWN for facet in EIGHT_FOUR_FACETS})
    assert display_policy(p7_conn, plan_version="plan-1").names == REDACTED
    assert display_policy(p7_conn, plan_version="plan-2").names == SHOWN


# --- the aggregate-safe summary -----------------------------------------------

def test_the_summary_has_two_fields_and_neither_can_hold_a_filename():
    """§8.4: "A summary such as '11 protected identity records' may be safe to show,
    while a visible list of passport filenames on a shared screen may not be."

    Asserted at the TYPE level. A runtime filter is something a future caller can
    route around and a string scan is something a docstring defeats; a record with no
    field of the wrong type cannot carry a filename at all. §5.2 states the same rule
    for the canvas -- a Finance or Identity proposal "may be visible as a protected
    area, but the product should avoid showing sensitive filenames."
    """
    hints = get_type_hints(ProtectedSummary)
    assert [f.name for f in dataclasses.fields(ProtectedSummary)] == [
        "count", "class_breakdown"]
    assert hints == {"count": int, "class_breakdown": Mapping[str, int]}


def test_eleven_protected_records_summarise_as_a_count(p7_conn, corpus, store):
    # §8.4's own example, and §7.5's residual screen renders the same form: "11
    # protected personal records."
    file_ids = [corpus(f"passport-{index}.pdf") for index in range(11)]
    for file_id in file_ids:
        classify(p7_conn, store, file_id,
                 handling_class="highly_sensitive_credential_bearing",
                 protected=True)
    summary = summarize_protected(p7_conn, "Identity",
                                  files_in_scope=all_of(*file_ids))
    assert summary.count == 11
    assert summary.class_breakdown == {"highly_sensitive_credential_bearing": 11}


def test_the_breakdown_sums_to_the_count(p7_conn, corpus, store):
    protected = [corpus("passport.pdf"), corpus("tax-2024.pdf"),
                 corpus("notes-to-self.pdf")]
    classify(p7_conn, store, protected[0],
             handling_class="highly_sensitive_credential_bearing", protected=True)
    classify(p7_conn, store, protected[1],
             handling_class="highly_sensitive_credential_bearing", protected=True)
    classify(p7_conn, store, protected[2], handling_class="sensitive_personal",
             protected=True)
    summary = summarize_protected(p7_conn, "Identity",
                                  files_in_scope=all_of(*protected))
    assert sum(summary.class_breakdown.values()) == summary.count == 3
    assert set(summary.class_breakdown) <= set(HANDLING_CLASSES)


def test_the_breakdown_is_ordered_by_the_closed_vocabulary(p7_conn, corpus, store):
    # A deterministic key order, taken from HANDLING_CLASSES rather than from
    # insertion, so two runs over the same corpus render the same screen.
    first = corpus("credential.pdf")
    second = corpus("statement.pdf")
    classify(p7_conn, store, first,
             handling_class="highly_sensitive_credential_bearing", protected=True)
    classify(p7_conn, store, second, handling_class="sensitive_personal",
             protected=True)
    summary = summarize_protected(p7_conn, "Identity",
                                  files_in_scope=all_of(first, second))
    assert list(summary.class_breakdown) == [
        name for name in HANDLING_CLASSES if name in summary.class_breakdown]


def test_a_file_that_is_not_protected_is_not_counted(p7_conn, corpus, store):
    # SPEC §2: consume the flag, never infer it from the class. Open question 1 is
    # unsettled, so a `highly_sensitive_credential_bearing` record with the flag off
    # is legal and is not a protected record.
    unprotected = corpus("poster.pdf")
    classify(p7_conn, store, unprotected,
             handling_class="highly_sensitive_credential_bearing", protected=False)
    flagged = corpus("passport.pdf")
    classify(p7_conn, store, flagged, handling_class="public_low", protected=True)
    summary = summarize_protected(p7_conn, "Identity",
                                  files_in_scope=all_of(unprotected, flagged))
    assert summary.count == 1
    assert summary.class_breakdown == {"public_low": 1}


def test_an_unclassified_file_is_not_a_protected_record(p7_conn, corpus, store):
    # It has no `protected` flag to read, and inventing one in either direction would
    # be the §8.6 failure: "Cost exhaustion must never turn into lower-quality
    # automatic classification."
    looked_at = corpus("passport.pdf")
    classify(p7_conn, store, looked_at, handling_class="sensitive_personal",
             protected=True)
    never_looked_at = corpus("mystery.pdf")
    summary = summarize_protected(
        p7_conn, "Identity", files_in_scope=all_of(looked_at, never_looked_at))
    assert summary.count == 1


def test_with_no_detector_the_summary_is_zero_and_that_is_not_a_safety_claim(
        p7_conn, corpus):
    """The honest posture, stated in the suite.

    No task in any plan produces a detector rule set (D2), so on a real corpus every
    file is unclassified and `count` is zero. Zero protected records is **not** a
    claim that nothing in the corpus is sensitive; it is the count of files something
    has classified and flagged, which is currently none. §8.6 names the adjacent
    failure -- "the false impression that an unprocessed file was understood and found
    unimportant" -- and the fix is the deferred count the UI shows beside this one,
    which is P13's surface and not P7's number.
    """
    file_ids = [corpus(f"unknown-{index}.pdf") for index in range(5)]
    summary = summarize_protected(p7_conn, "Identity",
                                  files_in_scope=all_of(*file_ids))
    assert summary == ProtectedSummary(count=0, class_breakdown={})


def test_a_file_outside_the_scope_is_not_counted(p7_conn, corpus, store):
    # Open question 3 is held by the injection, exactly as Task 15 holds it: a
    # resolver that returns nothing produces an empty summary rather than everything.
    inside = corpus("passport.pdf")
    classify(p7_conn, store, inside, handling_class="sensitive_personal",
             protected=True)
    assert summarize_protected(p7_conn, "Identity",
                               files_in_scope=all_of()).count == 0
    assert summarize_protected(p7_conn, "Identity",
                               files_in_scope=all_of(inside)).count == 1


def test_p7_defines_no_corpus_area(p7_conn):
    # `files_in_scope` is a required keyword with NO default. A default would be P7
    # answering Open question 3 -- "Consent grants cannot be scoped until this is
    # named" -- in an implementation instead of in a SPEC.
    parameters = inspect.signature(summarize_protected).parameters
    assert parameters["files_in_scope"].default is inspect.Parameter.empty
    assert parameters["files_in_scope"].kind is inspect.Parameter.KEYWORD_ONLY


# --- C4, and P13's open question ----------------------------------------------

def test_neither_surface_writes_anything(p7_conn, corpus, store):
    # C4: "a gate that also wrote would be doing two jobs." Both of these are reads.
    stored(p7_conn)
    file_id = corpus("passport.pdf")
    classify(p7_conn, store, file_id, handling_class="sensitive_personal",
             protected=True)
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    mirror = get_file(p7_conn, file_id)["sensitivity_state"]
    display_policy(p7_conn, plan_version=PLAN_ONE)
    summarize_protected(p7_conn, "Identity", files_in_scope=all_of(file_id))
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert get_file(p7_conn, file_id)["sensitivity_state"] == mirror


def test_p13_open_question_7_is_recorded_against_this_signature():
    """P13 Open question 7, quoted and not resolved.

        "**Does the user's redaction setting have a scope?** §8.4 says 'Protected
        branches should have configurable redaction', which reads per-branch, while
        P7's `Gate.display_policy()` takes no scope argument and reads global.
        *Threatens P7.*"

    `display_policy` therefore takes a plan version and no branch, node or scope. This
    test fails the day someone adds one, which is the point: adding it would answer
    P13's question in an implementation rather than in a SPEC, and the answer changes
    what P13's canvas and review screens have to render.
    """
    parameters = inspect.signature(display_policy).parameters
    assert set(parameters) == {"conn", "plan_version"}
    assert parameters["plan_version"].kind is inspect.Parameter.KEYWORD_ONLY
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_display.py -v`
Expected: FAIL — `ImportError: cannot import name 'FACET_VALUES' from 'privacy.display'` (the module
does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/display.py`**

```python
# src/privacy/display.py
"""§8.4's UI-level privacy — the second surface P7 publishes off the model path.

The paragraph, from the design:

    "Privacy also applies to the user interface. A summary such as '11 protected
    identity records' may be safe to show, while a visible list of passport filenames
    on a shared screen may not be. Protected branches should have configurable
    redaction in the canvas and review screens. The user can choose whether names,
    previews, thumbnails, OCR text, or location data are shown."

Two functions, and the shapes matter more than the code:

- `display_policy` resolves the five configurable facets against the policy in force
  at a plan version, falling back **per facet** to the more redacting value. W1:
  "Where the design is silent on a redaction default, the more redacting option is
  the default." A facet the policy never mentions is the design being silent.
- `summarize_protected` returns a count and a per-class breakdown and **has no field
  a filename could occupy**. That is a type-level property, not a filter: a filter is
  something a later caller routes around, and §7.3's residual template requires that
  filenames and content must not leave the machine for protected material at all.

Neither writes (C4). Neither resolves an excerpt: no P4 text materialiser is imported
here, which Task 21 re-asserts repo-wide as layer L2.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from database_agent.files_table import get_file

from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.policy import Policy, current_policy
from privacy.vocabulary import DISPLAY_FACETS, HANDLING_CLASSES

#: SPEC §10: "each `shown | redacted`". Two values, and a third is a load error.
SHOWN: str = "shown"
REDACTED: str = "redacted"
FACET_VALUES: tuple[str, str] = (SHOWN, REDACTED)


class UnknownFacetValue(ValueError):
    """A redaction value outside §8.4's two.

    Refused rather than coerced to `redacted`: a stored value nobody in this
    vocabulary wrote means the policy row is not what this build believes it is, and
    silently substituting the safe value would hide that from the one screen whose
    job is to show the user what is being hidden.
    """


def check_facet_value(value: str) -> str:
    if value not in FACET_VALUES:
        raise UnknownFacetValue(
            f"{value!r} is not one of §8.4's two redaction values {FACET_VALUES}")
    return value


@dataclass(frozen=True)
class RedactionSettings:
    """§8.4's five configurable facets, in §8.4's own order.

    "The user can choose whether names, previews, thumbnails, OCR text, or location
    data are shown."
    """

    names: str
    previews: str
    thumbnails: str
    ocr_text: str
    location_data: str


@dataclass(frozen=True)
class ProtectedSummary:
    """SPEC §10: "aggregate only, no filenames".

    Two fields, an `int` and a mapping of handling class to `int`. There is
    deliberately no `examples`, no `filenames`, no `preview` and no `sample` field:
    §8.4 contrasts "11 protected identity records" with "a visible list of passport
    filenames on a shared screen", and the only way to guarantee the second is
    unreachable is for the record to have nowhere to put it.
    """

    count: int
    class_breakdown: Mapping[str, int]


def settings_for(policy: Policy) -> RedactionSettings:
    """Resolve the five facets against one policy, per facet.

    The per-facet fallback is W1's, not a convenience: a facet the policy does not
    mention is a setting the design left silent, and the silent value is the more
    redacting one. Resolving the mapping whole would let a partial policy -- the shape
    a migration produces -- carry a facet with no value at all.
    """
    resolved = {
        facet: check_facet_value(
            policy.redaction_settings.get(facet, MORE_REDACTING[facet]))
        for facet in DISPLAY_FACETS
    }
    return RedactionSettings(**resolved)


def display_policy(conn: sqlite3.Connection, *,
                   plan_version: str) -> RedactionSettings:
    """§8.4's configurable redaction, for the plan version being displayed.

    `plan_version` is required because §8.8 places "Privacy and model-consent
    policies" inside the plan version and the redaction settings are part of that
    policy (SPEC §5). There is no scope, branch or node parameter: P13 Open question 7
    asks whether the setting is per-branch and it is unanswered, so this signature
    holds the question open rather than answering it here.
    """
    return settings_for(current_policy(conn, plan_version=plan_version))


def summarize_protected(conn: sqlite3.Connection, scope: str, *,
                        files_in_scope: Callable[[str], Sequence[str]]
                        ) -> ProtectedSummary:
    """Count the protected records in a scope. Aggregate only.

    `files_in_scope` has no default. Open question 3 -- "What is a 'corpus area'? ...
    Consent grants cannot be scoped until this is named" -- is unanswered, so P7
    defines no area and the caller resolves the scope, exactly as Task 15's `revoke`
    does.

    Counts the `protected` FLAG, never the handling class (SPEC §2, Open question 1),
    and never a file with no classification: absence carries no flag, and with no
    detector built (D2) that is every file in a real corpus. A zero here is the count
    of files something has classified and flagged, not a claim that the corpus holds
    nothing sensitive.
    """
    store = ClassificationStore(conn)
    counted: dict[str, int] = {}
    for file_id in files_in_scope(scope):
        content_hash = get_file(conn, file_id)["content_hash"]
        record = store.current(file_id, content_hash)
        if record is None or not record.protected:
            continue
        counted[record.handling_class] = counted.get(record.handling_class, 0) + 1
    ordered = {name: counted[name] for name in HANDLING_CLASSES if name in counted}
    return ProtectedSummary(count=sum(ordered.values()),
                            class_breakdown=MappingProxyType(ordered))
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_display.py -v`
Expected: PASS — 22 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–18 green, and the 1300 P1–P5 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/display.py tests/p7/test_p7_display.py
git commit -m "feat(P7): display_policy per facet, and a protected summary with nowhere to put a filename"
```

---
