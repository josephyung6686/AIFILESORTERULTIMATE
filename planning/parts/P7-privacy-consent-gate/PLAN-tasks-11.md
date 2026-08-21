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
  `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row`.
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
