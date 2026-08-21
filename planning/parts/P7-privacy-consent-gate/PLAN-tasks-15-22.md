
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
    policy = Policy(policy_version="", operation_mode="local_model",
                    consent_grants=(),
                    redaction_settings={"names": "redacted", "previews": "redacted",
                                        "thumbnails": "redacted",
                                        "ocr_text": "redacted",
                                        "location_data": "redacted"},
                    automatic_move_permissions=dict(permissions or {}),
                    plan_version=plan_version, set_at=FIXED_CLOCK)
    return set_policy(conn, policy, author=SUBSYSTEM, component_version=COMPONENT,
                      user_id="joseph")


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
