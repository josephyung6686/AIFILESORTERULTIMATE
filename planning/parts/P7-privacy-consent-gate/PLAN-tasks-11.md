### Task 11: `Gate.release` — the request, the three-branch union, and no override parameter

> ### ⚠ CUT 4 — unratified. This task is a cut target; it is written in full anyway.
>
> `planning/overnight/reviews/round-5-scope.md` **CUT 4** recommends deleting **P7's `Gate` facade as
> a seven-method object**, on the argument that seven methods on one class is a namespace, not an
> abstraction, and that six of the seven are one-line delegations to modules that already publish the
> function. **Joseph has not ruled on it.** Of round 5's seven cuts exactly one is ratified (CUT 1,
> P6 Task 26, via D5); this is not that one.
>
> Written in full, per the authoring brief §9, because an unratified recommendation is not a decision
> and a half-written keystone is worth nothing to either outcome. **What the cut would and would not
> take:** it would take the *class*; it would not take `release`, which SPEC §6 publishes as
> `Gate.release(ModelCallRequest) -> ReleaseDecision` and which B2 makes P8's call verbatim. A build
> that adopts CUT 4 has to answer what `Gate.release` becomes — SPEC §6 names the method on an object
> — and that is a Contract-out revision, not an implementation choice. This task therefore ships
> `Gate` with **one** method and names the six that Tasks 15–18 add (see *What this task does not do*),
> which is the smallest form the published signature admits and the form a reviewer deciding CUT 4
> needs in front of them.

**Files:**
- Create: `src/privacy/release.py`, `src/privacy/gate.py`
- Test: `tests/p7/test_p7_release.py`

**Interfaces:**
- Consumes (`release.py`): `privacy.consent.NeedsConsent` (**the only `privacy` module `release.py`
  imports at run time besides `vocabulary`** — see *The import direction*),
  `privacy.vocabulary.check_denial_reason(value) -> str`, `.OutOfVocabulary`;
  under `TYPE_CHECKING` only: `privacy.resolve.Materialised`, `privacy.redaction.RedactionManifest`,
  `privacy.items.RequestedItem`, `privacy.denial.RemedyOption`.
- Consumes (`gate.py`): `privacy.release.*`; `privacy.classification.resolve_class(record) -> str`,
  `.UNREADABLE_UNCLASSIFIED`, `.ClassificationRecord`, `.completeness_implies_unclassified`;
  `privacy.classification_store.ClassificationStore`;
  `privacy.policy.Policy`, `.current_policy(conn, *, plan_version) -> Policy | None`;
  `privacy.items.Excerpt`, `.RedactedIdentifier`, `.check_item(item, *, unit_length, protected,
  sensitive_keys, allow_unratified) -> None`, `.sensitive_observation_keys(conn, file_id)
  -> frozenset[str]`, `.AlwaysLocalRequested`, `.WholeDocumentRequested`, `.kind_of(item) -> str`;
  `privacy.redaction.RedactionManifest`, `.apply_redaction(value, *, observation_key, span,
  context_before, context_after, context_truncated, classifier, transform)
  -> tuple[str, RedactionEntry]`;
  `privacy.resolve.materialise(conn, item) -> Materialised`;
  `privacy.audit.AuditRecord`, `.append_audit(conn, record, *, author, component_version,
  extra=None) -> int`;
  `privacy.authorship.SUBSYSTEM`;
  `privacy.consent.ConsentRequirement`, `.open_consent_request(conn, requirement, *, request,
  policy, content_hashes, user_id, component_version, observed_at) -> NeedsConsent`;
  `privacy.denial.DENIAL_ORDER`, `.DECIDABLE_FROM_REQUEST`, `.first_reason(reasons) -> str | None`,
  `.mode_forbids`, `.policy_revoked_for`, `.unclassified_denies`, `.is_protected_records`,
  `.protected_cloud_denies`, `.over_dossier_ceiling`, and the eight builders
  `deny_mode_forbids_target`, `deny_policy_revoked`, `deny_always_local_item`, `deny_unclassified`,
  `deny_protected_records_template`, `deny_protected_cloud_target`,
  `deny_whole_document_requested`, `deny_dossier_over_budget`, `.record_denial(conn, denied, *,
  request, policy, classification, content_hashes, user_id, component_version, observed_at) -> int`,
  `.PROTECTED_RECORDS_TEMPLATE`;
  `privacy.binding.mint_release(conn, *, policy, model_target, prompt_fingerprint, audit_id,
  minted_at) -> str`;
  `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row`,
  `database_agent.budget.get_ceiling(conn, key) -> int | None`.
- Produces (`release.py`):
  - `ModelTarget` — frozen: `locality: str`, `model_id: str`, `provider: str`; `LOCALITIES:
    tuple[str, str] = ("local", "cloud")`; `to_mapping() -> dict[str, str]`.
  - `Target` — frozen: `file_ids: tuple[str, ...]`, `group_id: str | None = None`.
  - `ModelCallRequest` — frozen; SPEC §6's **seven** exactly: `stage`, `target`, `model_target`,
    `requested_items`, `prompt_template_id`, `prompt_fingerprint`, `max_dossier_tokens`.
  - `Released` — frozen; SPEC §6's **six**: `release_id`, `audit_id`, `policy_version`,
    `materialised_items`, `redaction_manifest`, `model_target`.
  - `Denied` — frozen; **four**: `reason`, `explanation`, `remedy_options`, **`evidence_refs`**.
  - `NeedsConsent` — **re-exported** from `privacy.consent`, not redefined (Task 14 owns it).
  - `ReleaseDecision` — the union alias, `Released | Denied | NeedsConsent`.
  - `REQUEST_FIELDS`, `RELEASED_FIELDS`, `DENIED_FIELDS`, `NEEDS_CONSENT_FIELDS`,
    `DECISION_TYPES: tuple[type, ...]`, `DECISION_ORDER: tuple[str, ...]`,
    `FORBIDDEN_PARAMETER_NAMES: frozenset[str]`, `RELEASE_PARAMETERS: frozenset[str]`.
  - `MalformedRequest`, `MalformedDecision`, `NoPolicyInForce`.
- Produces (`gate.py`):
  - `TEXT_BEARING: tuple[type, ...]` — the two item kinds that resolve to local text.
  - `Gate(conn, *, store, plan_version, classifier, transform, unclassified_permits_local,
    scope_for, files_in_scope, component_version, now, user_id, measure_tokens=None,
    template_for=None)`.
  - `Gate.release(request) -> ReleaseDecision`.

**Done-means:** 3 (the gate half), and the entry point for 5, 6, 7.

---

#### Execution order — this task's two files sit on either side of Tasks 12 and 13

**Read this before scheduling the task.** The four modules of Tasks 11–14 form an acyclic *module*
graph, but the task numbering is not a valid *build* order, and neither Task 12 nor Task 13 nor
Task 14 carries a `Modify: src/privacy/release.py` line — each of the three states, in its own
"what this section leaves for its neighbours" table, that the wiring is Task 11's. Both facts are
true and together they force this task to land in two commits:

```text
consent.py   imports policy, audit, authorship, vocabulary        — needs no release
release.py   imports consent (NeedsConsent) and vocabulary        — needs consent
denial.py    imports release.Denied AT RUN TIME                   — needs release
binding.py   imports release under TYPE_CHECKING ONLY             — needs release only to type-check
gate.py      imports release, consent, denial, binding, and 2-10  — needs all four
```

**The order that builds is `… 10, 14, 11-a, 13, 12, 11-b`:**

| | What lands | Steps |
|---|---|---|
| **11-a** | `src/privacy/release.py` — nine frozen dataclasses and eight constants, no behaviour | Steps 1–2 |
| **11-b** | `src/privacy/gate.py` and `tests/p7/test_p7_release.py` | Steps 3–8 |

`release.py` carries no test of its own at 11-a, and that is deliberate rather than a gap:
`test_p7_release.py` tests **the door**, and the door is `gate.py`. Every assertion about `release.py`
is a shape assertion in that file, and in the interim Task 12's and Task 13's own tests import and
exercise the dataclasses. Splitting Task 11 into two numbered tasks instead would put
`FORBIDDEN_PARAMETER_NAMES` in one task and the signature it constrains in another, which is the one
thing the shape tests exist to keep together.

**Two consequences reported to their owners, not patched here:**

1. **Task 14 runs before Task 11-a**, and Task 14's assertion that *"the two branch types share no
   field name at all"* imports `release.Denied`. Either that one assertion moves to this file — where
   `test_the_three_branches_share_no_field_name` already makes it, over all three types rather than
   two — or Task 14 is scheduled after 11-a. **Reported to Task 14's author.**
2. **Task 20 pins `Gate.__init__`** (`GATE_ARGUMENTS`, ten keywords) and this task adopts all ten
   verbatim — `store`, `plan_version`, `classifier`, `transform`, `unclassified_permits_local`,
   `scope_for`, `files_in_scope`, `component_version`, `now`, `user_id`. It adds **two optional
   keywords Task 20's `gate_arguments` does not supply**, `measure_tokens` and `template_for`, both
   defaulting to `None`. See *Two denials the gate cannot reach without a keyword Task 20 omits*,
   below. **Reported to Task 20's author.**

---

#### The signature is adopted VERBATIM on both sides (B2), and everything else is constructor state

SPEC §6: *"`Gate.release(ModelCallRequest) -> ReleaseDecision`. **This is the only gate signature in
the product.** P8's `seal(...) -> SealedDossier | Refusal` is withdrawn; P8 adopts this call, this
return union, and these field names verbatim (B2). There is one door, named once."*

`Gate.release` therefore has **two** parameters, `self` and `request`. The connection, the
classification store, the policy scope, the two injected redaction protocols, the clock, the user
identity and the two open questions that need a value all live on `Gate.__init__`. That is not a
workaround for a cramped signature; it is what *"one door, named once"* costs, and it is what lets
the whitelist test be an **equality** rather than a subset.

**There is no override parameter, and the test proves it two ways.**

- **The whitelist** — `set(inspect.signature(Gate.release).parameters) == {"self", "request"}` —
  proves no unpublished parameter exists **at all**. This is the stronger half: a blacklist can only
  catch the words someone thought of.
- **The blacklist** — `FORBIDDEN_PARAMETER_NAMES` — names the specific words a future convenience
  would reach for, and asserts they appear in neither the signature, nor `Gate.__init__`, nor any
  field of the request, nor any field of any of the three branch types.

**Both are parsed from `inspect.signature` and `dataclasses.fields`, never from source text.** A
source scan matches comments and docstrings, and that technique has produced a false result eight
times on this project; the established mechanism where a token assertion is unavoidable is
`code_tokens()` in `tests/p3/test_p3_no_invention.py`, which walks the AST. This is P5's
`SafetyPolicy` discipline applied to the gate: *"Two fields, and deliberately no third."*

The blacklist is compared **token-wise**, on `name.split("_")`, not by substring. Substring matching
would fail `unclassified_permits_local` against a blacklisted `permit` and would tempt the next
author to rename a legitimate parameter to appease a test. Token-wise, every published name here is
clean: `{conn, store, plan, version, classifier, transform, unclassified, permits, local, scope,
for, files, in, component, now, user, id, measure, tokens, template, release, request, stage,
target, model, requested, items, prompt, fingerprint, max, dossier, audit, policy, materialised,
redaction, manifest, reason, explanation, remedy, options, evidence, refs, consent, requirement}`.

**Three constructor parameters carry no default, and each one is an open question refusing to be
guessed.** `classifier` and `transform` are SPEC *Deferred*'s row for identifier classes: *"Which
identifier classes exist and how each is transformed is not enumerated anywhere in the design."*
`scope_for` is Open question 3 — *"What is a 'corpus area'? … Consent grants cannot be scoped until
this is named"* — so the caller maps a `file_id` to an opaque scope string and P7 resolves none.
`unclassified_permits_local` is Open question 5 — *"Does `unreadable_unclassified` permit a local
model call?"* — and it reaches `denial.unclassified_denies`, whose own docstring records that P7
names no winner.

---

#### `Denied` has FOUR fields, and the fourth is `evidence_refs`

The skeleton's Task 11 `Produces` lists three. That is a defect in the skeleton and it is corrected
here, on three independent grounds that all point the same way:

1. **SPEC §6 requires it.** `Denied.explanation` is *"user-facing, evidence-referenced"*. A field
   that references evidence and a record that cannot carry the references are not the same thing.
2. **Task 13's own constructor takes it.** The skeleton spells
   `deny(reason, *, explanation, remedy_options, evidence_refs) -> Denied`, and the written Task 13
   implements exactly that signature. *A constructor that accepts a value the dataclass cannot hold
   is not writable* — Task 13's author raised this and it is honoured, not renegotiated.
3. **The one denial that has evidence to cite would silently drop it.**
   `deny_protected_cloud_target(*, file_ids, operation_mode, scope, evidence_refs=())` passes the
   classification's own refs through. SPEC §2 makes `evidence_refs` non-empty for any
   `basis = detector` classification, and §3.1's principle is that every fact preserves where it came
   from. A denial that says *"this file is protected"* and cannot say *on what evidence* has thrown
   away the half of §8.4 that makes the classification *"evidence-backed"*.

`evidence_refs` is `tuple[str, ...]` of P4 **`observation_key`** values, never `observation_id`
(M14, and SPEC *Correction learning*: *"The key, not the id, is what makes that durable"*). It
defaults to `()` because six of the eight denials are decided from the request and the policy and
have no evidence to cite — `deny_mode_forbids_target` passes `evidence_refs=()` explicitly, and an
empty tuple there is honest rather than lazy.

---

#### The import direction — fixed by Tasks 12–14, adopted here without renegotiation

The rule, quoted from the written Tasks 12–14 section, which says in its own words that this is
*"the one constraint these three tasks place on"* Task 11:

```text
release.py    ModelCallRequest · ModelTarget · Target · Released · Denied · ReleaseDecision
              imports privacy.consent for NeedsConsent, and no other privacy module
consent.py    NeedsConsent · ConsentRequirement       imports policy, audit, authorship, vocabulary
binding.py    the ledger                              imports release under TYPE_CHECKING ONLY
denial.py     the eight denials                       imports release.Denied at run time
gate.py       the Gate facade                         imports all four; holds the decision logic
```

Adopted. Three notes on how it is applied, each stated rather than done quietly:

- **`vocabulary` is the one addition, and it cannot create a cycle.** `Denied.__post_init__` calls
  `check_denial_reason`, so a hand-constructed `Denied("looks_fine", …)` is refused at construction
  and not only inside `denial.deny`. `privacy.vocabulary` is a **leaf**: Task 2's `Consumes` names
  no `privacy` module at all, and imports `scan_agent.exclusion` *in the test only*. `release` →
  `vocabulary` therefore cannot close any loop, and `denial.py` imports it too. The rule's purpose —
  `release.py` sits **below** `denial` and `binding` so they may import it — is preserved exactly.
- **`resolve`, `redaction`, `items` and `denial` are imported under `TYPE_CHECKING` only.**
  `Released.materialised_items` is `tuple[Materialised, ...]`, `Released.redaction_manifest` is a
  `RedactionManifest`, `ModelCallRequest.requested_items` is `tuple[RequestedItem, ...]`, and
  `Denied.remedy_options` is `tuple[RemedyOption, ...]`. Precise annotations with no run-time edge is
  exactly the device Task 12 sanctioned for `binding`, and `from __future__ import annotations` makes
  it work. The `denial` edge is a TYPE_CHECKING cycle — `denial` imports `release` at run time,
  `release` imports `denial` at type-check time — which type checkers resolve and the interpreter
  never sees. The **field name** `remedy_options` is fixed here; the **element type** is Task 13's.
- **`NeedsConsent` is not redefined here.** It is imported from `privacy.consent` and re-exported, so
  that `ReleaseDecision = Released | Denied | NeedsConsent` reads as one union in one module — the
  File Structure gives `release.py` *"Gate.release — the request, the three branches, the ordering"* —
  while Task 14 keeps the dataclass, its `consent_request_id`, its four-option invariant and its
  whole lifecycle. **One dataclass, one home, one import.** The skeleton lists `NeedsConsent` under
  both Task 11's and Task 14's `Produces`; this is that collision resolved, and the resolution is the
  one a sibling already wrote its task against.

---

#### `DECISION_ORDER` — published, because the order is the contract

```text
1  collect_request_denials   the six in DENIAL_ORDER decidable from request + policy + a row
2  needs_consent             a question only the user can answer — asked only if nothing denied
3  materialise               the ONLY content read, and the first step that touches text
4  collect_content_denials   whole_document_requested, dossier_over_budget
5  append_audit              §8.4: recording the authorization is part of granting it
6  mint_release              Task 12's ledger; the token exists only after the record does
```

It is published as a tuple so a reviewer can read the order without reading the function, and so a
reordering is a diff on a constant rather than an invisible behaviour change.

**The order is forced, not chosen, and Task 13's `DECIDABLE_FROM_REQUEST` is the proof obligation in
data form.** Its principle: *no denial that can be decided from the request alone may be decided
after one that requires reading the file.* A gate that materialised an excerpt and **then**
discovered the mode forbade the call has read a sensitive file for a call that was never going to
happen. `test_no_content_is_read_before_every_request_decidable_check_has_run` asserts it directly,
by handing the gate a `materialise` that fails the test if it is called at all.

**Within step 1 the gate does not re-decide precedence — it collects and delegates.** Four of the
eight reasons overlap on real inputs (a protected unclassified file under `offline` with a cloud
target satisfies three at once), so the gate gathers every triggered reason into a set and asks
`denial.first_reason(reasons)` which one wins. `DENIAL_ORDER` lives in `denial.py` and is Task 13's;
a gate that re-sorted them would be a second home for a total order, which is the defect class
§11 of the authoring brief was written to stop.

---

#### `Denied(unclassified)` is the ordinary path and this task is built for it

The detector is unwritten. D2 puts the rule set behind an injection and **no task in any plan
produces one**, so against a real corpus `ClassificationStore.current(file_id, content_hash)` returns
`None` for every file, `classification.resolve_class(None)` returns `unreadable_unclassified`, and the
call is denied. That is not a degraded mode; it is what a correct locked door does when nobody has
been handed a key.

It shapes this task concretely: the denial tests need no evidence setup at all, and the **one**
`Released` test is the one that has to write a classification by hand and says so in its docstring.
Absence never resolves to `public_low` — SPEC §1, which is §8.6's *"Cost exhaustion must never turn
into lower-quality automatic classification"* applied to the case that matters — and
`test_absence_never_resolves_to_a_lower_class` asserts it on the audit record the gate wrote, not on
an internal variable.

**`unreadable_unclassified` reaches `AuditRecord.file_sensitivity` and never
`files.sensitivity_state`** (D2: *"a GATE OUTCOME, not a file fact"*). The gate issues no
`UPDATE files` of its own; `test_the_gate_writes_no_classification_and_leaves_the_column_alone`
proves C4 and D2 with one assertion, which is why it is one test and not two.

---

#### `NeedsConsent` fires on the `protected` flag, and it answers no open question

The consent branch is reached when **no denial triggered**, the request carries text-bearing items,
at least one targeted file is `protected`, and the policy holds no grant for the scope. §8.4: *"If a
model needs text containing sensitive content, the user should see that requirement and choose
whether to allow a local model, a cloud model, a redacted prompt, or no model use."*

**It reads `ClassificationRecord.protected` and never a set of handling classes**, and that is
deliberate. SPEC §2: *"Whether `protected` is exactly co-extensive with the top two classes is **not
settled by the design** — see Open questions. Neighbouring parts should consume the `protected` flag,
not infer it from the class."* An earlier draft of this task published a
`SENSITIVE_CLASSES: tuple[str, str]` constant naming the top two; **that constant is removed here**,
because publishing it would answer NEEDS-JOSEPH **C5** (*"is `protected` exactly the top two handling
classes?"*) in an implementation instead of in a SPEC, which Task 21's guard exists to catch.

The cloud case never reaches this branch: `denial.protected_cloud_denies` decides it at position 6 of
`DENIAL_ORDER`, and its carve-out — `cloud_assisted` **plus** an explicit grant for the scope — is
§8.4's own sentence, *"User explicitly permits selected corpus areas to use a cloud model."* So the
branch that reaches the user is the **local** one, which is exactly the choice §8.4 describes: the
user is being asked whether a model may see sensitive text at all, and all four answers are open.

---

#### Two denials the gate cannot reach without a keyword Task 20 omits — reported, not invented

`Gate.__init__` adopts Task 20's ten pinned keywords verbatim and adds two optional ones. Both
default to `None`, and with the default the corresponding denial is **unreachable through the gate**
while remaining fully proven in Task 13:

- **`measure_tokens: Callable[[ModelCallRequest, tuple[Materialised, ...]], int] | None = None`.**
  `denial.over_dossier_ceiling(conn, *, measured_tokens)` needs a measurement and **P7 owns no
  tokenizer** — inventing one would invent a number, which SPEC *Deferred* and Task 21 both forbid.
  Task 13 is explicit that the check reads P1's stored ceiling and *"never `request.max_dossier_tokens`,
  which is only 'the caller's echo of it (M9)': a caller must not be able to raise its own ceiling by
  echoing a larger one."* So the measurement is injected. With none supplied there is nothing to
  compare, exactly as *"an UNSET ceiling cannot deny"* — the same shape, one level up. `dossier_over_budget`
  is M9's backstop that **should never fire in a correct pipeline**; do not delete the check.
- **`template_for: Callable[[str], str | None] | None = None`.**
  `denial.is_protected_records(template_name)` compares against §7.3's literal
  `PROTECTED_RECORDS_TEMPLATE = "Protected Records"`. The residual-template library that assigns a
  file to a template is P10's and P11's and **is unbuilt**; SPEC *Deferred* keeps its contents out of
  this contract. With no mapping supplied, no file is under a residual template.

**Reported to Task 20's author:** `gate_arguments(fixture, store=…)` supplies ten keywords, and
fixtures **4** and **16** (*"`Protected Records` residual, excerpt requested"* and *"…, filename
requested"*, both expecting `Denied(protected_records_template)`) cannot be replayed through the real
gate until it also supplies `template_for`. The two keywords are named here so that gap is a
one-line fixture change rather than a discovery during assembly.

---

#### `NoPolicyInForce` — the gate does not default a policy, and here is why that is not a gap

`policy.current_policy(conn, *, plan_version)` returns `Policy | None` (A6). When it returns `None`,
`Gate.release` raises `NoPolicyInForce`. It does **not** synthesise one.

The reason is brief §11's rule, applied: `defaults.effective_policy(conn, *, plan_version,
install_mode, set_at)` is Task 6's, it is where W1's local-first floor is resolved, and Done-means 12
is proven there. A gate that resolved its own default would be a **second home** for that floor,
which is the defect class this project has paid the most for — and it would need `install_mode`,
which is Open question 11 (*which* of `offline` and `local_model` ships) and which Task 20's pinned
constructor deliberately does not carry.

`NoPolicyInForce` is not a policy decision and it is not a `Denied`. It is the same class as
`resolve.UnresolvableSpan` — a call the gate cannot evaluate — and like those two it **propagates**.
It is not a *fourth branch*: `ReleaseDecision` has exactly three members and
`test_release_returns_one_of_exactly_three_types` asserts it.

---

#### What this task does not do

| Not done here | Owner | Why |
|---|---|---|
| The other six `Gate` methods — `revoke`, `reclassify`, `delete_derived`, `may_move_automatically`, `display_policy`, `summarize_protected` | Tasks 15–18 | Their modules do not exist at 11-b. Each of those tasks needs a `Modify: src/privacy/gate.py` line that its `Files` block currently omits; **named here so assembly can add it.** `files_in_scope` is constructor state held for `Gate.revoke` and is unused by `release`. |
| `DENIAL_ORDER`, `first_reason`, the eight builders, `RemedyOption`, `record_denial` | Task 13 | Published there; consumed here. The gate collects reasons and delegates the precedence. |
| The release ledger, `consume_release`, unforgeability | Task 12 | `gate.py` calls `mint_release`; L1 is proven in Task 12's own tests. |
| `NeedsConsent`'s dataclass, its id, `record_consent_choice`, the four-option invariant | Task 14 | `release.py` re-exports the type; `gate.py` calls `open_consent_request`. |
| Whether a caller absorbs `NeedsConsent` | P8 Done-means 13, P13 Done-means 16 | *"P7's obligation is to make the absorption unrepresentable, not to police it."* |
| Writing `bundle_file_entry.handling_class` | Task 22 / OQ8 | The gate never reaches P2's bundle. |
| A detector | **Nobody, and that is the finding** | D2 put the rule set behind an injection and no task supplies one. |

---

- [ ] **Step 1: Write `src/privacy/release.py`** — the request, the three branches, and the union

```python
# src/privacy/release.py
"""SPEC §6's request and its three-branch return. Types and constants only.

This module sits at the BOTTOM of P7's decision stack on purpose. `denial.py` imports
`Denied` from it at run time and `binding.py` imports `Released` from it under
TYPE_CHECKING, so anything this module imported from those two would close a cycle.
It therefore imports exactly two `privacy` modules at run time:

    privacy.consent      for NeedsConsent, which Task 14 owns and this module
                         re-exports so the union reads as one union in one place
    privacy.vocabulary   a LEAF -- it imports no `privacy` module at all -- for
                         `check_denial_reason`, so a hand-built `Denied` with an
                         invented reason is refused at construction

Everything else is annotation-only, under TYPE_CHECKING, which `from __future__ import
annotations` makes sufficient.

There is no override parameter anywhere in this file, and `FORBIDDEN_PARAMETER_NAMES`
plus `RELEASE_PARAMETERS` are what `tests/p7/test_p7_release.py` proves that with --
by parsing signatures and `dataclasses.fields`, never by reading source text.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from privacy.consent import NeedsConsent
from privacy.vocabulary import check_denial_reason

if TYPE_CHECKING:  # pragma: no cover - annotations only; no run-time edge
    from privacy.denial import RemedyOption
    from privacy.items import RequestedItem
    from privacy.redaction import RedactionManifest
    from privacy.resolve import Materialised

__all__ = [
    "LOCALITIES", "ModelTarget", "Target", "ModelCallRequest", "Released", "Denied",
    "NeedsConsent", "ReleaseDecision", "REQUEST_FIELDS", "RELEASED_FIELDS",
    "DENIED_FIELDS", "NEEDS_CONSENT_FIELDS", "DECISION_TYPES", "DECISION_ORDER",
    "FORBIDDEN_PARAMETER_NAMES", "RELEASE_PARAMETERS", "MalformedRequest",
    "MalformedDecision", "NoPolicyInForce",
]


class MalformedRequest(ValueError):
    """The request cannot be evaluated. Shape, not policy."""


class MalformedDecision(ValueError):
    """A branch value was constructed in a shape §8.4 does not permit."""


class NoPolicyInForce(RuntimeError):
    """No policy is stored for this plan version, so there is nothing to authorize by.

    NOT a fourth branch and NOT a `Denied`. §8.4's audit record names the "authorizing
    policy"; with none in force there is no answer to give, only a call that cannot be
    evaluated -- the same class as `resolve.UnresolvableSpan`, and it propagates.

    The gate deliberately does not synthesise a default. W1's local-first floor is
    resolved in `defaults.effective_policy`, which is where Done-means 12 is proven,
    and a second resolution here would be a second home for it.
    """


#: SPEC §6: `model_target { locality: local | cloud, model_id, provider }`.
LOCALITIES: tuple[str, str] = ("local", "cloud")


@dataclass(frozen=True, slots=True)
class ModelTarget:
    """Which model would receive the data. §8.4 audits it; §6 binds a release to it."""

    locality: str
    model_id: str
    provider: str

    def __post_init__(self) -> None:
        if self.locality not in LOCALITIES:
            raise MalformedRequest(
                f"locality {self.locality!r} is not one of {LOCALITIES}; a value "
                "outside a closed vocabulary is a load error, not a fallback")
        if not self.model_id or not self.provider:
            raise MalformedRequest(
                "§8.4 requires the audit record show WHICH MODEL received the data; "
                "an unnamed model or provider cannot satisfy that")

    def to_mapping(self) -> dict[str, str]:
        """The stored form. `AuditRecord.model` and the ledger both use it."""
        return {"locality": self.locality, "model_id": self.model_id,
                "provider": self.provider}


@dataclass(frozen=True, slots=True)
class Target:
    """§4.4, §7.7 -- what the call is about. Files, and optionally a group."""

    file_ids: tuple[str, ...]
    group_id: str | None = None

    def __post_init__(self) -> None:
        if not self.file_ids:
            raise MalformedRequest(
                "a release decision is about file versions; a target with no files "
                "has nothing to classify and nothing to audit")
        if len(set(self.file_ids)) != len(self.file_ids):
            raise MalformedRequest(
                f"file_ids {self.file_ids!r} repeats an id; the audit record's "
                "content_hashes would then double-count what left the device")


@dataclass(frozen=True, slots=True)
class ModelCallRequest:
    """SPEC §6's SEVEN fields, and deliberately no eighth.

    Every field is a REFERENCE. No field accepts a document string, a path, or an
    `Observation`: §8.4 puts "complete extracted text", "paths", "OCR output" and
    "raw sensitive values" in the always-local set, and a request that could carry one
    would have moved content before the gate had decided anything.

    `call_site` is NOT a field: B2 puts it inside `prompt_fingerprint` (§3.4, §8.2,
    §8.4), so it is neither a separate request field nor a separate binding term.
    """

    stage: str
    target: Target
    model_target: ModelTarget
    requested_items: tuple[RequestedItem, ...]
    prompt_template_id: str
    prompt_fingerprint: str
    max_dossier_tokens: int

    def __post_init__(self) -> None:
        if not self.stage:
            raise MalformedRequest(
                "§8.5 requires per-stage decomposition, so a call with no stage "
                "cannot be replayed or attributed")
        if not self.prompt_fingerprint:
            raise MalformedRequest(
                "§8.4 audits the prompt fingerprint, and B2 puts `call_site` inside "
                "it rather than beside it; an empty fingerprint audits nothing")
        if not self.prompt_template_id:
            raise MalformedRequest(
                "§8.8 reproduces the prompt in force at each call; that needs the "
                "template id")
        if not self.requested_items:
            raise MalformedRequest(
                "a request with no items has nothing to release")
        if self.max_dossier_tokens <= 0:
            raise MalformedRequest(
                "§8.6's ceiling is the caller's echo of P1's stored value (M9); zero "
                "or negative is not an echo of anything")


REQUEST_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(ModelCallRequest))


@dataclass(frozen=True, slots=True)
class Released:
    """SPEC §6's SIX fields. Single-use and bound; the ledger is Task 12's.

    Instantiating this dataclass outside the gate buys nothing: `consume_release`
    checks the ledger, and a `release_id` that was never minted raises
    `ReleaseNotIssued`. That is the property that makes the door real, and it is
    proven in Task 12, not here.
    """

    release_id: str
    audit_id: int
    policy_version: str
    materialised_items: tuple[Materialised, ...]
    redaction_manifest: RedactionManifest
    model_target: ModelTarget

    def __post_init__(self) -> None:
        if not self.release_id:
            raise MalformedDecision(
                "a release with no id cannot be bound or consumed (§6)")
        if not self.policy_version:
            raise MalformedDecision(
                "§6: the gate owns the policy and STAMPS the version; an unstamped "
                "release cannot be replayed under §8.8")


RELEASED_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(Released))


@dataclass(frozen=True, slots=True)
class Denied:
    """The gate's answer. Evidence-referenced (§6), and never a dead end (§8.6).

    FOUR fields. The skeleton's Task 11 block lists three and omits `evidence_refs`;
    SPEC §6 requires the explanation be "evidence-referenced" and Task 13's published
    `deny(reason, *, explanation, remedy_options, evidence_refs)` takes them, so a
    three-field dataclass makes that constructor unwritable.

    `evidence_refs` holds P4 `observation_key` values and never `observation_id`
    (M14): a per-row id dies on extractor upgrade, and `observation_key` deliberately
    excludes `extractor_version` (MINOR 8) so it survives one. It defaults to `()`
    because six of the eight reasons are decided from the request and the policy and
    have no evidence to cite; an empty tuple there is honest, not lazy.
    """

    reason: str
    explanation: str
    remedy_options: tuple[RemedyOption, ...]
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        check_denial_reason(self.reason)
        if not self.explanation or not self.explanation.strip():
            raise MalformedDecision(
                "§8.6 requires the product show 'what has been deferred, and why'; a "
                "denial with an empty explanation shows only the first half")
        if not self.remedy_options:
            raise MalformedDecision(
                "a denial with no legitimate alternative is a dead end the user "
                "cannot act on (§8.6)")


DENIED_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(Denied))
NEEDS_CONSENT_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(NeedsConsent))

#: SPEC §6: `ReleaseDecision = Released | Denied | NeedsConsent`. Three, and no fourth.
#: `NoPolicyInForce` is an exception, not a member: it says the call cannot be
#: evaluated, where all three of these say what the answer IS.
ReleaseDecision = Released | Denied | NeedsConsent

DECISION_TYPES: tuple[type, ...] = (Released, Denied, NeedsConsent)

#: The order `Gate.release` evaluates in, published so a reviewer can read it without
#: reading the function and so a reordering is a diff on a constant. It is forced, not
#: chosen: nothing materialises until every check that could deny has run, because a
#: gate that resolved first would hold the text in memory before deciding it was
#: allowed to. Task 13's `DECIDABLE_FROM_REQUEST` is the same principle as data, and
#: the test asserts the two agree.
DECISION_ORDER: tuple[str, ...] = (
    "collect_request_denials",
    "needs_consent",
    "materialise",
    "collect_content_denials",
    "append_audit",
    "mint_release",
)

#: The exact parameter names of `Gate.release`. Published so the whitelist assertion
#: is an EQUALITY against a named constant rather than a literal buried in a test.
RELEASE_PARAMETERS: frozenset[str] = frozenset({"self", "request"})

#: The words a future convenience would reach for. Compared TOKEN-WISE, on
#: `name.split("_")`, never by substring: substring matching would fail a legitimate
#: `unclassified_permits_local` and would tempt the next author to rename a parameter
#: to appease a test. This is the weaker of the two guards -- a blacklist only catches
#: the words someone thought of -- and it exists beside `RELEASE_PARAMETERS`, which
#: proves no unpublished parameter exists at all.
FORBIDDEN_PARAMETER_NAMES: frozenset[str] = frozenset({
    "force", "override", "bypass", "allow", "approved", "skip", "unsafe",
    "trusted", "internal", "escalate", "ignore", "disable", "raw", "plaintext",
})
```

- [ ] **Step 2: Commit `release.py` — this is commit 11-a, and it lands BEFORE Tasks 13 and 12**

Run first, because a types-only module either imports or it does not:

```bash
PYTHONPATH=src python3 -c "
import privacy.release as r
print(r.REQUEST_FIELDS)
print(r.RELEASED_FIELDS)
print(r.DENIED_FIELDS)
print(r.NEEDS_CONSENT_FIELDS)
"
```

Expected:

```text
('stage', 'target', 'model_target', 'requested_items', 'prompt_template_id', 'prompt_fingerprint', 'max_dossier_tokens')
('release_id', 'audit_id', 'policy_version', 'materialised_items', 'redaction_manifest', 'model_target')
('reason', 'explanation', 'remedy_options', 'evidence_refs')
('consent_request_id', 'requirement', 'options')
```

If the last line raises `ModuleNotFoundError: privacy.consent`, **Task 14 has not been executed yet**
and the order in *Execution order* was not followed.

```bash
git add src/privacy/release.py
git commit -m "feat(P7): the release request and the three-branch union, with Denied carrying evidence_refs"
```

> **Tasks 13 and 12 run now.** `denial.py` imports `release.Denied` at run time; `binding.py` imports
> `release.Released` under `TYPE_CHECKING`. Neither can be written before this commit exists.

---

- [ ] **Step 3: Write the failing test**

```python
# tests/p7/test_p7_release.py
"""§8.4's one door: the request, the three branches, and no way around it.

The shape tests are the point, and they come first. A gate whose decision logic is
right and whose signature carries an `override=` keyword is not a gate, and the second
failure is the one review does not catch. Every shape assertion here is parsed from
`inspect.signature` and `dataclasses.fields` -- never from source text, which matches
comments and docstrings and has produced a false result eight times on this project.

`Denied(unclassified)` is the ordinary path. The detector is unwritten (D2), so on a
real corpus every file lands there; the denial tests need no evidence at all, and the
ONE `Released` test is the one that has to write a classification by hand.
"""
from __future__ import annotations

import dataclasses
import inspect
import json
import sqlite3
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from database_agent.files_table import get_file, record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)

from privacy.authorship import COMPONENT_VERSION
from privacy.binding import consume_release
from privacy.classification import ClassificationRecord, UNREADABLE_UNCLASSIFIED
from privacy.classification_store import ClassificationStore
from privacy.consent import NeedsConsent
from privacy.defaults import MORE_REDACTING
from privacy.denial import DECIDABLE_FROM_REQUEST, DENIAL_ORDER
from privacy.gate import TEXT_BEARING, Gate
from privacy.items import Excerpt, Filename, RedactedIdentifier
from privacy.policy import Policy, UNSET_POLICY_VERSION, set_policy
from privacy.redaction import RedactionManifest
from privacy.release import (
    DECISION_ORDER, DECISION_TYPES, DENIED_FIELDS, FORBIDDEN_PARAMETER_NAMES,
    NEEDS_CONSENT_FIELDS, RELEASED_FIELDS, RELEASE_PARAMETERS, REQUEST_FIELDS,
    Denied, ModelCallRequest, ModelTarget, NoPolicyInForce, Released, Target,
)
from privacy.resolve import UnresolvableSpan
from privacy.schema import create_privacy_schema

OBSERVED_AT = "2026-08-22T09:00:00Z"
PLAN_VERSION = "plan-v1"
TEXT = "Passport number A1234567 was issued in 2019 to the applicant."
SPAN = TextSpan(start=16, end=24)          # "A1234567"
LOCAL = ModelTarget(locality="local", model_id="llama-local", provider="on-device")
CLOUD = ModelTarget(locality="cloud", model_id="big-model", provider="a-provider")


# --------------------------------------------------------------------------
# seeding -- P1 and P4 writers only, all introspected live 2026-08-22
# --------------------------------------------------------------------------

def _file(conn: sqlite3.Connection, name: str, content_hash: str) -> str:
    return record_file(
        conn, Path("/corpus") / name, filename=name,
        normalized_filename=name.lower(), extension=Path(name).suffix,
        observed_size=4096,
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
        content_hash=content_hash)


def _evidence(conn: sqlite3.Connection, file_id: str, content_hash: str) -> str:
    """One run, one text unit, one observation. Returns the `observation_key`."""
    run_id = new_id()
    page = (Segment(kind="page", index=1),)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="pdf", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1))
    record_text_unit(conn, TextUnit(run_id=run_id, container_path=page, text=TEXT))
    location = Location(zone="body", container_path=page, text_span=SPAN)
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="fixture.text",
        extractor_version="1.0.0", source_type="pdf",
        raw_value=TEXT[SPAN.start:SPAN.end], location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id=run_id,
        context_before=TEXT[:SPAN.start], context_after=TEXT[SPAN.end:],
        context_truncated=False))
    return observation_key(
        content_hash=content_hash, extractor_name="fixture.text",
        locator=serialize_locator(location), raw_value=TEXT[SPAN.start:SPAN.end])


def _policy(conn: sqlite3.Connection, mode: str, *, grants=()) -> Policy:
    """Store a policy and read back the version the gate will stamp."""
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode,
        consent_grants=tuple(grants), redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION, set_at=OBSERVED_AT)
    version = set_policy(conn, draft, component_version=COMPONENT_VERSION,
                         user_id="joseph", reason="test fixture")
    return dataclasses.replace(draft, policy_version=version)


def _classify(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
              handling_class: str, protected: bool, refs=("obs-key-1",)) -> None:
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis="detector", evidence_refs=tuple(refs),
        reliability_state="direct", observed_at=OBSERVED_AT))


def _classifier(value: str, *, context_before=None, context_after=None) -> str | None:
    """SPEC *Deferred* keeps identifier classes opaque; this enumerates nothing."""
    return "fixture-identifier-class"


def _transform(value: str, *, identifier_class: str) -> str:
    return "[redacted]"


def _gate(conn: sqlite3.Connection, **overrides) -> Gate:
    keywords: dict[str, object] = {
        "store": ClassificationStore(conn),
        "plan_version": PLAN_VERSION,
        "classifier": _classifier,
        "transform": _transform,
        "unclassified_permits_local": False,
        "scope_for": lambda file_id: "area-1",
        "files_in_scope": lambda scope: (),
        "component_version": COMPONENT_VERSION,
        "now": lambda: OBSERVED_AT,
        "user_id": "joseph",
    }
    keywords.update(overrides)
    return Gate(conn, **keywords)


def _request(*, items, model_target=CLOUD, file_ids=("f1",), stage="grouping",
             max_dossier_tokens=4000) -> ModelCallRequest:
    return ModelCallRequest(
        stage=stage, target=Target(file_ids=tuple(file_ids)),
        model_target=model_target, requested_items=tuple(items),
        prompt_template_id=f"template.{stage}",
        prompt_fingerprint=f"fingerprint.{stage}",
        max_dossier_tokens=max_dossier_tokens)


def _events(conn: sqlite3.Connection, event_type: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? ORDER BY event_id",
        (event_type,)).fetchall()


@pytest.fixture()
def gate_conn(p7_conn):
    create_privacy_schema(p7_conn)
    return p7_conn


# --------------------------------------------------------------------------
# 1-12  shape: the signature, the fields, and the absence of an override
# --------------------------------------------------------------------------

def test_release_takes_the_request_and_nothing_else():
    """B2: P8 adopts SPEC §6's signature verbatim, so there is no second parameter.

    The WHITELIST half, and it is the stronger one: an equality proves no unpublished
    parameter exists AT ALL, where a blacklist only catches words someone thought of.
    """
    assert set(inspect.signature(Gate.release).parameters) == RELEASE_PARAMETERS
    assert RELEASE_PARAMETERS == {"self", "request"}


def test_no_signature_and_no_branch_field_names_an_override():
    """The BLACKLIST half, token-wise over every published name in the part."""
    names = set(inspect.signature(Gate.release).parameters)
    names |= set(inspect.signature(Gate.__init__).parameters)
    for kind in (ModelCallRequest, Target, ModelTarget, *DECISION_TYPES):
        names |= {f.name for f in dataclasses.fields(kind)}
    tokens = {token for name in names for token in name.split("_")}
    assert tokens.isdisjoint(FORBIDDEN_PARAMETER_NAMES), sorted(
        tokens & FORBIDDEN_PARAMETER_NAMES)


def test_the_blacklist_is_compared_token_wise_and_not_by_substring():
    """`unclassified_permits_local` is legitimate and must stay legitimate.

    A substring comparison would have to drop `permit` from the blacklist or rename a
    parameter to appease a test. Both are worse than splitting on underscores.
    """
    name = "unclassified_permits_local"
    assert name in inspect.signature(Gate.__init__).parameters
    # A substring rule would have to keep `permit` out of the blacklist to let this
    # name through. A token rule does not: "permits" is not "permit".
    assert set(name.split("_")).isdisjoint(FORBIDDEN_PARAMETER_NAMES)
    assert "permit" not in FORBIDDEN_PARAMETER_NAMES


def test_the_request_carries_references_only():
    """§8.4 puts complete extracted text, paths and OCR output in the always-local set.

    A request field that accepted one would have moved content before the gate had
    decided anything. Asserted over the annotations, not over a value.
    """
    annotations = {f.name: str(f.type) for f in dataclasses.fields(ModelCallRequest)}
    assert annotations["target"] == "Target"
    assert annotations["model_target"] == "ModelTarget"
    assert annotations["requested_items"] == "tuple[RequestedItem, ...]"
    for name, annotation in annotations.items():
        assert "Observation" not in annotation, name
        assert "Path" not in annotation, name
    assert [f.name for f in dataclasses.fields(ModelCallRequest)
            if str(f.type) == "str"] == [
        "stage", "prompt_template_id", "prompt_fingerprint"]


def test_request_fields_are_specs_seven_in_specs_order():
    assert REQUEST_FIELDS == (
        "stage", "target", "model_target", "requested_items", "prompt_template_id",
        "prompt_fingerprint", "max_dossier_tokens")
    assert "call_site" not in REQUEST_FIELDS   # B2 puts it inside the fingerprint


def test_released_fields_are_specs_six_in_specs_order():
    assert RELEASED_FIELDS == (
        "release_id", "audit_id", "policy_version", "materialised_items",
        "redaction_manifest", "model_target")


def test_denied_carries_evidence_refs_as_its_fourth_field():
    """SPEC §6: the explanation is "evidence-referenced". Task 13's `deny` takes them.

    The skeleton's Task 11 block lists three fields and omits this one; a constructor
    that accepts a value the dataclass cannot hold is not writable.
    """
    assert DENIED_FIELDS == ("reason", "explanation", "remedy_options",
                             "evidence_refs")
    denied = Denied(reason="unclassified", explanation="why", remedy_options=("ask",),
                    evidence_refs=("obs-key-1", "obs-key-2"))
    assert denied.evidence_refs == ("obs-key-1", "obs-key-2")
    assert Denied(reason="unclassified", explanation="why",
                  remedy_options=("ask",)).evidence_refs == ()


def test_needs_consent_has_no_reason_field():
    """"`Denied` is the gate's answer, `NeedsConsent` is a question only the user can
    answer." A caller cannot map it onto a denial reason even by accident."""
    assert "reason" not in NEEDS_CONSENT_FIELDS
    assert "consent_request_id" in NEEDS_CONSENT_FIELDS


def test_the_three_branches_share_no_field_name():
    """Structurally distinct, so no branch can be read as another.

    This also carries the assertion Task 14 makes over two of the three; it is made
    here over all three because this is the module that publishes the union.
    """
    named = [{f.name for f in dataclasses.fields(kind)} for kind in DECISION_TYPES]
    for left in range(len(named)):
        for right in range(left + 1, len(named)):
            assert named[left].isdisjoint(named[right])


def test_release_returns_one_of_exactly_three_types():
    """SPEC §6: `ReleaseDecision = Released | Denied | NeedsConsent`. No fourth.

    `NoPolicyInForce` is an exception rather than a member: it says the call cannot be
    EVALUATED, where all three of these say what the answer IS.
    """
    assert DECISION_TYPES == (Released, Denied, NeedsConsent)
    assert not issubclass(NoPolicyInForce, tuple(DECISION_TYPES))


def test_release_py_imports_no_privacy_module_but_consent_and_vocabulary():
    """The import direction Tasks 12-14 fixed, asserted by module introspection.

    `denial` imports `release.Denied` at run time and `binding` imports `Released`
    under TYPE_CHECKING, so anything `release` imported back from those two would
    close a cycle. `vocabulary` is a leaf and cannot.
    """
    import privacy.release as module

    bound = {value.__name__ for value in vars(module).values()
             if getattr(value, "__module__", "").startswith("privacy.")}
    imported = {getattr(value, "__module__", "")
                for value in vars(module).values()
                if getattr(value, "__module__", "").startswith("privacy.")}
    assert imported <= {"privacy.consent", "privacy.vocabulary", "privacy.release"}
    assert "NeedsConsent" in bound          # re-exported, not redefined
    assert NeedsConsent.__module__ == "privacy.consent"


def test_decision_order_puts_every_request_decidable_denial_before_materialisation():
    """No denial decidable from the request may be decided after one that reads text.

    A gate that materialised an excerpt and THEN discovered the mode forbade the call
    has read a sensitive file for a call that was never going to happen.
    """
    assert DECISION_ORDER == (
        "collect_request_denials", "needs_consent", "materialise",
        "collect_content_denials", "append_audit", "mint_release")
    assert DECISION_ORDER.index("collect_request_denials") < \
        DECISION_ORDER.index("materialise")
    assert DECISION_ORDER.index("append_audit") < DECISION_ORDER.index("mint_release")
    late = {r for r in DENIAL_ORDER if r not in DECIDABLE_FROM_REQUEST}
    assert max(DENIAL_ORDER.index(r) for r in DECIDABLE_FROM_REQUEST) < \
        min(DENIAL_ORDER.index(r) for r in late)


# --------------------------------------------------------------------------
# 13-20  the denial branch -- the ordinary path
# --------------------------------------------------------------------------

def test_an_unclassified_file_is_denied_and_that_is_the_ordinary_path(gate_conn):
    """No detector exists (D2), so this is what the gate answers on a Tuesday.

    No classification is written by this test, which is the point: the setup for the
    normal case is nothing at all.
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"


def test_absence_never_resolves_to_a_lower_class(gate_conn):
    """SPEC §1: absence resolves to `unreadable_unclassified`, NEVER to `public_low`.

    §8.6: "Cost exhaustion must never turn into lower-quality automatic
    classification." Asserted on the audit record the gate wrote, not on an internal.
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    row = _events(gate_conn, "model_release_denied")[0]
    explanation = json.loads(row["explanation"])
    assert explanation["file_sensitivity"] == UNREADABLE_UNCLASSIFIED
    assert "public_low" not in row["explanation"]


def test_offline_mode_denies_a_cloud_target_before_anything_is_read(gate_conn):
    """§8.4: under offline "No content leaves the device". Outermost in DENIAL_ORDER."""
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"


def test_overlapping_reasons_resolve_through_first_reason(gate_conn):
    """An unclassified protected file under `offline` with a cloud target triggers
    three reasons at once. The gate collects and DELEGATES; `DENIAL_ORDER` is Task
    13's and a gate that re-sorted them would be a second home for a total order."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-passport")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert decision.reason == DENIAL_ORDER[0] == "mode_forbids_target"


def test_a_protected_file_with_a_cloud_target_is_denied(gate_conn):
    """SPEC §2's first protected consequence: not in cloud prompts BY DEFAULT."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True,
              refs=(key,))
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "protected_cloud_target"
    assert decision.evidence_refs == (key,)


def test_a_denial_appends_exactly_one_model_release_denied(gate_conn):
    """§8.2: "Every significant event affecting a file." One event, not two."""
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert len(_events(gate_conn, "model_release_denied")) == 1
    assert _events(gate_conn, "model_release") == []


def test_the_gate_writes_no_classification_and_leaves_the_column_alone(gate_conn):
    """C4 and D2 in one assertion, which is why it is one test and not two.

    C4: "a gate that also wrote would be doing two jobs." D2: "`Unreadable or
    unclassified` is a GATE OUTCOME, not a file fact ... it lives on the release
    decision and never in that column."
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    before = get_file(gate_conn, file_id)["sensitivity_state"]
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    after = get_file(gate_conn, file_id)["sensitivity_state"]
    assert after == before
    assert after is None or UNREADABLE_UNCLASSIFIED not in str(after)
    assert ClassificationStore(gate_conn).current(file_id, "hash-unknown") is None


def test_a_filename_on_a_protected_records_file_is_denied(gate_conn):
    """§7.3: for Protected Records, "filenames and content must not be exposed in
    model prompts at all" -- and it binds a LOCAL target too, which is why it
    outranks the cloud rule in DENIAL_ORDER."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "cloud_assisted", grants=(("area-1", "cloud_model"),))
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="highly_sensitive_credential_bearing", protected=True)
    decision = _gate(
        gate_conn,
        template_for=lambda _file_id: "Protected Records",
    ).release(_request(items=(Filename(file_id=file_id, value="passport.pdf"),),
                       model_target=LOCAL, file_ids=(file_id,), stage="residual"))
    assert isinstance(decision, Denied)
    assert decision.reason == "protected_records_template"


# --------------------------------------------------------------------------
# 21-23  the consent branch
# --------------------------------------------------------------------------

def test_a_protected_file_on_a_local_target_with_no_grant_needs_consent(gate_conn):
    """§8.4: "If a model needs text containing sensitive content, the user should see
    that requirement and choose." The cloud case is denied at DENIAL_ORDER 6; the
    local case is the one that reaches the user, and all four answers are open."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "local_model")
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, NeedsConsent)
    assert decision.consent_request_id
    assert len(_events(gate_conn, "consent_requested")) == 1
    assert _events(gate_conn, "model_release") == []


def test_the_consent_branch_reads_the_protected_flag_and_not_a_class_list(gate_conn):
    """SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    from the class." Whether `protected` is co-extensive with the top two classes is
    NEEDS-JOSEPH C5 and this module answers it nowhere."""
    import privacy.release as release_module
    import privacy.gate as gate_module

    assert not hasattr(release_module, "SENSITIVE_CLASSES")
    assert not hasattr(gate_module, "SENSITIVE_CLASSES")
    file_id = _file(gate_conn, "odd.pdf", "hash-odd")
    _policy(gate_conn, "local_model")
    key = _evidence(gate_conn, file_id, "hash-odd")
    _classify(gate_conn, file_id, "hash-odd",
              handling_class="personal_non_sensitive", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, NeedsConsent)


def test_a_granted_scope_does_not_ask_again(gate_conn):
    """Consent already given is not a question. §8.4's grant is per corpus area, and
    what a corpus area IS stays Open question 3 -- `scope_for` is the caller's."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "local_model", grants=(("area-1", "local_model"),))
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, Released)


# --------------------------------------------------------------------------
# 24-28  the release branch, the ordering guarantee, and what escapes
# --------------------------------------------------------------------------

def test_a_clean_call_returns_released_with_an_audit_id_already_in_the_log(gate_conn):
    """Done-means 4, and the ONE test that has to write a classification by hand.

    SPEC §6: "the audit record is appended ... BEFORE `Released` is returned. There is
    no interval in which content is releasable and unaudited." `append_audit` returns
    `cursor.lastrowid`, so the id exists only after the row does -- which makes the
    ordering a structural fact rather than a discipline.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    policy = _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False, refs=(key,))
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Released)
    assert decision.policy_version == policy.policy_version
    assert decision.model_target == CLOUD
    row = gate_conn.execute("SELECT * FROM events WHERE event_id = ?",
                            (decision.audit_id,)).fetchone()
    assert row is not None
    assert row["event_type"] == "model_release"
    assert row["subsystem"] == "P7"
    explanation = json.loads(row["explanation"])
    pairs = explanation["excerpts_included"]
    assert len(pairs) == 1 and pairs[0][0] == key
    # SPEC §7: the record stores (observation_key, span) pairs "not a second copy of
    # the text". The pair is enough to re-run `resolve.materialise`; the value is not
    # in the log.
    assert TEXT[SPAN.start:SPAN.end] not in row["explanation"]


def test_the_released_id_is_in_the_ledger_and_a_fabricated_one_is_not(gate_conn):
    """Task 12 proves single use; this proves the gate actually MINTED through it.

    A `Released` the gate returned consumes; one a caller builds does not, because the
    id it carries was never in the ledger.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    policy = _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    consume_release(gate_conn, decision, model_target=CLOUD,
                    prompt_fingerprint="fingerprint.grouping",
                    policy_version=policy.policy_version)
    forged = dataclasses.replace(decision, release_id="0" * 32)
    with pytest.raises(Exception):
        consume_release(gate_conn, forged, model_target=CLOUD,
                        prompt_fingerprint="fingerprint.grouping",
                        policy_version=policy.policy_version)


def test_no_content_is_read_before_every_request_decidable_check_has_run(
        gate_conn, monkeypatch):
    """The ordering property, proven by making materialisation fail the test.

    "Nothing materialises until every check that could deny has run" is the reason
    `DECISION_ORDER` exists, and a comment is not a proof.
    """
    import privacy.gate as gate_module

    def _explode(conn, item):   # pragma: no cover - the assertion IS not calling it
        raise AssertionError("the gate read content before it had decided")

    monkeypatch.setattr(gate_module, "materialise", _explode)
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-passport")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)


def test_materialised_items_hold_only_what_had_a_value_to_resolve(gate_conn):
    """SPEC §6: "materialised_items[] post-redaction values only."

    §4: an evidence reference is "an id only -- no content", and a filename, a
    candidate label and a metadata field carry no local content either. The gate does
    not echo back what it did not touch; the caller still holds the request it sent.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),
               Filename(file_id=file_id, value="notes.pdf")),
        file_ids=(file_id,)))
    assert isinstance(decision, Released)
    assert len(decision.materialised_items) == 1
    assert decision.materialised_items[0].observation_key == key
    assert decision.materialised_items[0].value == "[redacted]"
    assert isinstance(decision.redaction_manifest, RedactionManifest)
    assert decision.redaction_manifest.any_redacted is True
    assert TEXT_BEARING == (Excerpt, RedactedIdentifier)


def test_a_call_with_no_policy_in_force_raises_rather_than_defaulting(gate_conn):
    """W1's local-first floor is resolved in `defaults.effective_policy`, where
    Done-means 12 is proven. A second resolution here would be a second home for it,
    and it would need `install_mode`, which is Open question 11."""
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    key = _evidence(gate_conn, file_id, "hash-notes")
    with pytest.raises(NoPolicyInForce):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
            file_ids=(file_id,)))


def test_a_resolve_failure_propagates_and_is_not_a_denial(gate_conn):
    """A span the evidence does not carry is a contract violation by the CALLER.

    P4's `check_span_anchor` "raises; never returns a repair", and a gate that
    repaired would release text nobody addressed. `Denied` and `NeedsConsent` are
    values; these two are exceptions, and the difference is deliberate.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    with pytest.raises(UnresolvableSpan):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key="no-such-key", span=SPAN,
                           reason="heading"),),
            file_ids=(file_id,)))


def test_an_unset_dossier_ceiling_and_no_measurement_cannot_deny(gate_conn):
    """M9's backstop, and the two reasons it stays unreachable by default.

    `get_ceiling` returns `None` when nothing set it, and P7 owns no tokenizer, so
    `measure_tokens` is injected. With a ceiling AND a measurement the backstop fires;
    a P8 test that reaches it through the normal path is a P8 failure, not a gate
    result. Do not delete the check.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    request = _request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,))
    assert isinstance(_gate(gate_conn).release(request), Released)

    set_ceiling(gate_conn, "model.max_dossier_tokens_per_call", 10)
    decision = _gate(
        gate_conn, measure_tokens=lambda request, items: 11).release(request)
    assert isinstance(decision, Denied)
    assert decision.reason == "dossier_over_budget"
```

- [ ] **Step 4: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_release.py -q`

Expected: **FAIL — collection error**, `ModuleNotFoundError: No module named 'privacy.gate'`.
`src/privacy/release.py` exists from commit 11-a and `privacy.binding`, `privacy.denial` and
`privacy.consent` exist from Tasks 12, 13 and 14; `privacy.gate` is the one module still missing, so
the failure is one import and not thirty.

- [ ] **Step 5: Write `src/privacy/gate.py`**

```python
# src/privacy/gate.py
"""The one door. `Gate.release(ModelCallRequest) -> ReleaseDecision`, and nothing else.

B2 adopts SPEC §6's signature verbatim on both sides, so `release` takes the request
and NOTHING ELSE -- no override, no flag, no connection. Everything the gate needs
beyond the request is constructor state, and three of those constructor parameters
carry no default because each is an open question this plan will not guess:

    classifier / transform      SPEC *Deferred*: identifier classes and the redaction
                                transform are not enumerated anywhere in the design.
    scope_for                   Open question 3: "What is a 'corpus area'? ... Consent
                                grants cannot be scoped until this is named."
    unclassified_permits_local  Open question 5: does `unreadable_unclassified` permit
                                a LOCAL model call?

The gate writes exactly ONE thing -- the audit record -- and it writes it BEFORE the
decision is returned, because §8.4 makes recording the authorization part of granting
it (C4). It writes no classification, no `files.sensitivity_state`, no `stage_output`,
no placement decision and no P8 `Refusal`. The catcher is always the caller's.

It decides no precedence of its own: it COLLECTS every triggered reason and asks
`denial.first_reason` which one wins, because `DENIAL_ORDER` is Task 13's and a second
total order here would be a second home for it.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence

from database_agent.budget import get_ceiling
from database_agent.files_table import get_file
from evidence_shape.canonical import canonical_json

from privacy.audit import AuditRecord, append_audit
from privacy.authorship import SUBSYSTEM
from privacy.binding import mint_release
from privacy.classification import (
    UNREADABLE_UNCLASSIFIED, ClassificationRecord, resolve_class,
)
from privacy.consent import ConsentRequirement, open_consent_request
from privacy.denial import (
    deny_always_local_item, deny_dossier_over_budget, deny_mode_forbids_target,
    deny_policy_revoked, deny_protected_cloud_target,
    deny_protected_records_template, deny_unclassified,
    deny_whole_document_requested, first_reason, is_protected_records, mode_forbids,
    over_dossier_ceiling, policy_revoked_for, protected_cloud_denies, record_denial,
    unclassified_denies,
)
from privacy.items import (
    AlwaysLocalRequested, Excerpt, ProtectedItemRequested, RedactedIdentifier,
    WholeDocumentRequested, check_item, kind_of, sensitive_observation_keys,
)
from privacy.policy import current_policy
from privacy.redaction import RedactionManifest, apply_redaction
from privacy.release import (
    DECISION_ORDER, Denied, ModelCallRequest, NeedsConsent, NoPolicyInForce,
    ReleaseDecision, Released,
)
from privacy.resolve import Materialised, materialise

#: §4's two item kinds that address local text and therefore resolve to a value.
#: `candidate_label`, `metadata_field`, `evidence_reference` and `filename` carry no
#: local content -- §4: an evidence reference is "an id only -- no content" -- so they
#: are never materialised and never echoed back.
TEXT_BEARING: tuple[type, ...] = (Excerpt, RedactedIdentifier)


class Gate:
    """§8.4's gate. One object, one door, no second name.

    Task 20 pins the first ten keywords (`GATE_ARGUMENTS`) so its fixtures replay
    through the real gate. `measure_tokens` and `template_for` are two OPTIONAL
    additions, both defaulting to `None`, and both reported to Task 20:

    - `measure_tokens` -- P7 owns no tokenizer and inventing one would invent a
      number. With no measurement there is nothing to compare, exactly as an unset
      ceiling cannot deny.
    - `template_for` -- §7.3's residual-template library is P10's and P11's and is
      unbuilt. With no mapping, no file is under a residual template.
    """

    def __init__(self, conn: sqlite3.Connection, *, store, plan_version: str,
                 classifier, transform, unclassified_permits_local: bool,
                 scope_for: Callable[[str], str],
                 files_in_scope: Callable[[str], Sequence[str]],
                 component_version: str, now: Callable[[], str],
                 user_id: str | None,
                 measure_tokens: Callable[..., int] | None = None,
                 template_for: Callable[[str], str | None] | None = None) -> None:
        self._conn = conn
        self._store = store
        self._plan_version = plan_version
        self._classifier = classifier
        self._transform = transform
        self._unclassified_permits_local = unclassified_permits_local
        self._scope_for = scope_for
        #: Held for `Gate.revoke` (Task 15); `release` does not use it.
        self._files_in_scope = files_in_scope
        self._component_version = component_version
        self._now = now
        self._user_id = user_id
        self._measure_tokens = measure_tokens
        self._template_for = template_for

    # -- §8.4's only door ---------------------------------------------------

    def release(self, request: ModelCallRequest) -> ReleaseDecision:
        """See `release.DECISION_ORDER` for the order and why it is forced."""
        assert DECISION_ORDER[0] == "collect_request_denials"
        policy = current_policy(self._conn, plan_version=self._plan_version)
        if policy is None:
            raise NoPolicyInForce(
                f"no privacy policy is stored for plan version "
                f"{self._plan_version!r}. §8.4's audit record names the authorizing "
                "policy and there is none; W1's local-first floor is resolved in "
                "`defaults.effective_policy`, not here, so the gate refuses to "
                "invent one")

        observed_at = self._now()
        locality = request.model_target.locality
        file_ids = request.target.file_ids
        scope = self._scope_for(file_ids[0])
        granted = tuple(name for name, _option in policy.consent_grants)

        rows = {file_id: get_file(self._conn, file_id) for file_id in file_ids}
        hashes = tuple(rows[file_id]["content_hash"] for file_id in file_ids)
        records = {file_id: self._store.current(file_id, rows[file_id]["content_hash"])
                   for file_id in file_ids}
        classes = {file_id: resolve_class(record)
                   for file_id, record in records.items()}
        protected_ids = tuple(file_id for file_id, record in records.items()
                              if record is not None and record.protected)
        decisive = self._decisive(records, protected_ids, file_ids)
        sensitive_keys = frozenset().union(*(
            sensitive_observation_keys(self._conn, file_id) for file_id in file_ids))

        # 1 -- every reason decidable from the request, the policy and a row lookup.
        builders: dict[str, Callable[[], Denied]] = {}

        if mode_forbids(policy.operation_mode, locality):
            builders["mode_forbids_target"] = lambda: deny_mode_forbids_target(
                operation_mode=policy.operation_mode,
                model_target=request.model_target, file_ids=file_ids)

        if policy_revoked_for(self._conn, policy, scope):
            builders["policy_revoked"] = lambda: deny_policy_revoked(
                scope=scope, policy=policy, file_ids=file_ids)

        caught = self._precheck_items(request, protected=bool(protected_ids),
                                      sensitive_keys=sensitive_keys)
        if isinstance(caught, AlwaysLocalRequested):
            builders["always_local_item"] = lambda: deny_always_local_item(
                caught, file_ids=file_ids)
        elif isinstance(caught, ProtectedItemRequested):
            builders["protected_records_template"] = \
                lambda: deny_protected_records_template(
                    file_ids=file_ids, model_target=request.model_target)

        unclassified = tuple(sorted(
            file_id for file_id, name in classes.items()
            if name == UNREADABLE_UNCLASSIFIED))
        if unclassified and unclassified_denies(
                locality=locality,
                local_calls_on_unclassified=self._unclassified_permits_local):
            builders["unclassified"] = lambda: deny_unclassified(
                file_ids=unclassified, locality=locality,
                completeness=self._completeness(rows, unclassified[0]))

        if self._template_for is not None and any(
                is_protected_records(self._template_for(file_id))
                for file_id in file_ids):
            builders["protected_records_template"] = \
                lambda: deny_protected_records_template(
                    file_ids=file_ids, model_target=request.model_target)

        if protected_cloud_denies(protected=bool(protected_ids), locality=locality,
                                  operation_mode=policy.operation_mode, scope=scope,
                                  granted_scopes=granted):
            builders["protected_cloud_target"] = \
                lambda: deny_protected_cloud_target(
                    file_ids=protected_ids, operation_mode=policy.operation_mode,
                    scope=scope,
                    evidence_refs=(decisive.evidence_refs
                                   if decisive is not None else ()))

        chosen = first_reason(builders)
        if chosen is not None:
            return self._denied(builders[chosen](), request, policy, decisive,
                                hashes, observed_at)

        # 2 -- a question only the user can answer, asked only if nothing denied.
        text_items = tuple(item for item in request.requested_items
                           if isinstance(item, TEXT_BEARING))
        if text_items and protected_ids and scope not in granted:
            requirement = ConsentRequirement(
                file_ids=protected_ids,
                handling_class=classes[protected_ids[0]],
                items=tuple(kind_of(item) for item in text_items),
                why=("§8.4: this call needs text from files entered into protected "
                     f"state, and policy {policy.policy_version} holds no consent "
                     f"grant for scope {scope!r}"))
            return open_consent_request(
                self._conn, requirement, request=request, policy=policy,
                content_hashes=hashes, user_id=self._user_id,
                component_version=self._component_version, observed_at=observed_at)

        # 3 -- the only content read in the part.
        resolved, manifest = self._materialise(text_items)

        # 4 -- the two reasons that needed the resolved text.
        late: dict[str, Callable[[], Denied]] = {}
        caught = self._postcheck_items(request, resolved,
                                       protected=bool(protected_ids),
                                       sensitive_keys=sensitive_keys)
        if isinstance(caught, WholeDocumentRequested):
            late["whole_document_requested"] = \
                lambda: deny_whole_document_requested(caught, file_ids=file_ids)

        if self._measure_tokens is not None:
            measured = self._measure_tokens(request, resolved)
            if over_dossier_ceiling(self._conn, measured_tokens=measured):
                late["dossier_over_budget"] = lambda: deny_dossier_over_budget(
                    measured_tokens=measured,
                    ceiling=self._ceiling(), file_ids=file_ids)

        chosen = first_reason(late)
        if chosen is not None:
            return self._denied(late[chosen](), request, policy, decisive, hashes,
                                observed_at)

        # 5 -- the one write, before the value exists.
        audit_id = append_audit(
            self._conn,
            self._release_record(request, policy, classes, hashes, resolved,
                                 manifest, observed_at),
            author=SUBSYSTEM, component_version=self._component_version)

        # 6 -- the capability, recorded in Task 12's ledger and bound to three terms.
        release_id = mint_release(
            self._conn, policy=policy, model_target=request.model_target,
            prompt_fingerprint=request.prompt_fingerprint, audit_id=audit_id,
            minted_at=observed_at)

        return Released(
            release_id=release_id, audit_id=audit_id,
            policy_version=policy.policy_version, materialised_items=resolved,
            redaction_manifest=manifest, model_target=request.model_target)

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _decisive(records: Mapping[str, ClassificationRecord | None],
                  protected_ids: Sequence[str],
                  file_ids: Sequence[str]) -> ClassificationRecord | None:
        """The one record `record_denial` stores, which takes a single record.

        The first protected file if there is one, because that is the file the
        denial is about; otherwise the first target, whose record is `None` on the
        ordinary path and is exactly what `resolve_class` turns into
        `unreadable_unclassified`.
        """
        if protected_ids:
            return records[protected_ids[0]]
        return records[file_ids[0]]

    @staticmethod
    def _completeness(rows: Mapping[str, object], file_id: str) -> str | None:
        """P1 stores extraction status per tier; absent means nothing has run."""
        stored = rows[file_id]["extraction_status_by_tier"]
        return str(stored) if stored else None

    def _ceiling(self) -> int:
        """P1's stored ceiling, read for the denial's explanation only.

        Never `request.max_dossier_tokens`, which is "the caller's echo of it (M9)":
        a caller must not be able to raise its own ceiling by echoing a larger one.
        Reached only when `over_dossier_ceiling` already returned True, so the value
        is never `None` here; P7 invents no number for the case that cannot occur.
        """
        value = get_ceiling(self._conn, "model.max_dossier_tokens_per_call")
        if value is None:  # pragma: no cover - `over_dossier_ceiling` gated this
            raise AssertionError(
                "dossier_over_budget was reached with no ceiling stored; "
                "`over_dossier_ceiling` cannot return True in that state")
        return int(value)

    def _precheck_items(self, request: ModelCallRequest, *, protected: bool,
                        sensitive_keys) -> Exception | None:
        """Task 7's refusals that need no content. `unit_length=None` means unknown.

        `allow_unratified=True` because SPEC §4's flagged reading permits `filename`
        for non-protected files and denies it for protected ones; the denial is §7.3's
        and it arrives as `ProtectedItemRequested`, not as an unratified kind.
        """
        for item in request.requested_items:
            try:
                check_item(item, unit_length=None, protected=protected,
                           sensitive_keys=sensitive_keys, allow_unratified=True)
            except (AlwaysLocalRequested, ProtectedItemRequested) as caught:
                return caught
        return None

    def _postcheck_items(self, request: ModelCallRequest,
                         resolved: Sequence[Materialised], *, protected: bool,
                         sensitive_keys) -> Exception | None:
        """The one refusal that needs the resolved unit length."""
        lengths = {item.observation_key: item.unit_length for item in resolved}
        for item in request.requested_items:
            if not isinstance(item, TEXT_BEARING):
                continue
            try:
                check_item(item, unit_length=lengths.get(item.observation_key),
                           protected=protected, sensitive_keys=sensitive_keys,
                           allow_unratified=True)
            except WholeDocumentRequested as caught:
                return caught
        return None

    def _materialise(self, text_items: Sequence[object]
                     ) -> tuple[tuple[Materialised, ...], RedactionManifest]:
        """(observation_key, span) -> text -> redacted text. `resolve` is the only
        module under `src/privacy/` that binds a P4 text materialiser (L2)."""
        resolved: list[Materialised] = []
        entries = []
        for item in text_items:
            found = materialise(self._conn, item)
            value, entry = apply_redaction(
                found.value, observation_key=found.observation_key,
                span=found.span, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                classifier=self._classifier, transform=self._transform)
            resolved.append(Materialised(
                observation_key=found.observation_key, span=found.span, value=value,
                zone=found.zone, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                unit_length=found.unit_length))
            entries.append(entry)
        return tuple(resolved), RedactionManifest(entries=tuple(entries))

    def _release_record(self, request, policy, classes, hashes, resolved, manifest,
                        observed_at) -> AuditRecord:
        """SPEC §7's record for a release. `release_id` is None -- see the plan.

        §6 puts the append strictly BEFORE the release id exists, `mint_release`
        takes the `audit_id`, and `events` is append-only so the row cannot be
        back-filled. The join therefore runs ledger -> events, which is the
        direction Task 12 published the ledger's `audit_id` column for.
        """
        single = len(request.target.file_ids) == 1
        distinct = sorted(set(classes.values()))
        return AuditRecord(
            authorizing_policy=policy.policy_version,
            file_sensitivity=(distinct[0] if len(distinct) == 1
                              else canonical_json(distinct)),
            excerpts_included=tuple(
                (item.observation_key, item.span) for item in resolved),
            redaction_applied=manifest.any_redacted,
            model=request.model_target.to_mapping(),
            prompt_fingerprint=request.prompt_fingerprint,
            audit_id=None, release_id=None, observed_at=observed_at,
            stage=request.stage, file_ids=request.target.file_ids,
            group_id=request.target.group_id, content_hashes=hashes,
            operation_mode=policy.operation_mode,
            policy_version=policy.policy_version, plan_version=policy.plan_version,
            outcome="released",
            file_id=request.target.file_ids[0] if single else None,
            content_hash=hashes[0] if single else None,
            user_id=self._user_id,
            redaction_manifest=tuple(manifest.to_mapping()))

    def _denied(self, denied: Denied, request, policy, decisive, hashes,
                observed_at) -> Denied:
        """One `model_release_denied`, appended before the value is returned."""
        record_denial(self._conn, denied, request=request, policy=policy,
                      classification=decisive, content_hashes=hashes,
                      user_id=self._user_id,
                      component_version=self._component_version,
                      observed_at=observed_at)
        return denied
```

- [ ] **Step 6: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_release.py -v`

Expected: **PASS — 28 passed.**

- [ ] **Step 7: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`

Expected: **PASS** — Tasks 1–14 green, and P1–P5's 1300 collected tests still green.
`src/privacy/` still imports none of `extractors`' three refusals, and `src/privacy/gate.py` binds no
P4 text materialiser — `resolve` is still the only module that does, which Task 21 re-asserts
repo-wide.

- [ ] **Step 8: Commit `gate.py` and the test — this is commit 11-b**

```bash
git add src/privacy/gate.py tests/p7/test_p7_release.py
git commit -m "feat(P7): Gate.release, the three-branch union, and a signature with no override"
```

---

#### Reported by this task

| # | Finding | Who owns it |
|---|---|---|
| 1 | **The skeleton's `Denied` is missing `evidence_refs`.** Corrected here; SPEC §6 and Task 13's `deny` both require it. | closed here |
| 2 | **Task numbering is not a build order for 11–14.** The module graph is acyclic; the task graph is not. Executable order: `14, 11-a, 13, 12, 11-b`. | assembly |
| 3 | **SPEC §6 and SPEC §7 cannot both hold for `release_id`.** §6 puts the audit append strictly before the release exists; §7 lists `release_id` on the audit record; `events` is append-only so the row cannot be back-filled. Resolved by leaving `AuditRecord.release_id` `None` on a release record and joining ledger → events, the direction Task 12 built its `audit_id` column for. **Contract-out mismatch, not an implementation choice.** | Joseph / Task 10 |
| 4 | **Task 20's `GATE_ARGUMENTS` omits `template_for`**, so fixtures 4 and 16 (`Protected Records` residual) cannot be replayed through the real gate. One-line fixture change. | Task 20 |
| 5 | **Task 14's branch-disjointness assertion imports `release.Denied`**, so it needs 11-a first, or it moves here where `test_the_three_branches_share_no_field_name` already covers all three types. | Task 14 |
| 6 | **Tasks 15–18 each need a `Modify: src/privacy/gate.py` line** for the six remaining facade methods; their `Files` blocks omit it. Relevant to CUT 4. | Tasks 15–18 |
| 7 | **`SENSITIVE_CLASSES` is deliberately not published.** Naming the top two classes as "the sensitive ones" would answer NEEDS-JOSEPH **C5** in an implementation. The consent branch reads `ClassificationRecord.protected`, per SPEC §2's *"consume the `protected` flag, not infer it from the class."* | held open |
| 8 | **CUT 4 is unratified and this task is its target.** See the callout at the top. | Joseph |
