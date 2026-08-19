# P7 — Privacy and consent gate

Owns: §8.4
Status: contract draft

Design: [`../../01-product-design-structured.md`](../../01-product-design-structured.md) · source of truth:
[`../../00-database-agent-product-design.md`](../../00-database-agent-product-design.md) ·
segmentation: [`../../02-segmentation-map.md`](../../02-segmentation-map.md)

---

## Purpose

§8.4 opens with a sequencing requirement, not a policy statement: *"Privacy policy must be enforced
**before** content reaches any model or external connector."* The segmentation map orders P7 ahead of
P8 for exactly this reason — *"If the gate arrives after the harness, the first cloud call has already
shipped an unclassified document."*

P7 is therefore built as a **gate**, not as a policy document that P8 is trusted to consult. It owns the
only door through which file content may leave the device or reach any model, local or cloud. The
mechanism is a single asymmetry:

> **P8 never holds releasable content.** It composes a request out of *references* — observation keys,
> spans, field names, candidate labels. The gate resolves those references against local storage,
> applies redaction, appends the consent-aware audit record, and returns a `Released`. The model
> transport accepts a `Released` and nothing else. There is no entry point that takes a string.

Because the payload is minted only by the gate, is bound to one model target and one prompt fingerprint,
and is single-use, a call that bypasses P7 is not a policy violation to be caught in review — it is a
call that cannot be constructed.

P7 also publishes the two smaller surfaces §8.4 requires outside the model path: the automatic-move
predicate (*"should not be moved automatically without a user policy that explicitly permits it"*) and
the display redaction policy (*"a summary such as '11 protected identity records' may be safe to show,
while a visible list of passport filenames on a shared screen may not be"*).

P7 does **not** own the detection rules that decide a given file is a passport. §8.4 names the five kinds
of material that enter protected state; it never states how they are recognised. That content is
deferred (below). P7 owns the vocabulary, the record shapes, the modes, the audit record, and the gate.

---

## Design slice owned

| Obligation | Design |
|---|---|
| Five handling classes, assigned **before** LLM escalation | §8.4 |
| Classification is evidence-backed and user-revisable | §8.4 |
| Protected state entered immediately for the five named kinds; three prohibitions attach | §8.4 |
| The always-local set | §8.4 |
| The compact-dossier allowance — what may reach a cloud model | §8.4 |
| Four operation modes | §8.4 |
| **The default posture — local-first and data-minimizing.** A `must`, binding on whatever install default ships; P7 constrains it without choosing it (Contract out §5, W1) | §8.4 |
| The consent choice when a model needs sensitive text (four options) | §8.4 |
| The consent-aware audit record, per model call | §8.4 |
| Revocation, and the limit of revocation | §8.4 |
| UI-level privacy: aggregate-safe summaries, configurable redaction | §8.4 |

Held elsewhere in the design but enforced through P7's vocabulary:

- `sensitivity` is a **field** in the core model (§3.12) and `sensitivity status` is one of the small set
  of universal file facts (§3.11). P7 does not create a private table for classification — it owns the
  value vocabulary of an existing field and writes through P6.
- Finance, identity, medical and legal material ship first as **safety domains**: *"the system detects
  and protects them before any cloud or automated placement decision is allowed"* (§3.15).
- Rare sensitive files — passports, visas, legal documents — *"may be surfaced as protected records even
  when they do not meet a normal group-size threshold"* (§4.9). P7 publishes the flag; P9 does the
  surfacing.
- The `Protected Records` residual template is *"Normally local-only; must not cause filenames or content
  to be exposed in model prompts"* (§7.3). P7 publishes the denial; P11 consumes it.
- A frozen tree node may have type `protected` (§5.12) and a destination profile carries *"any privacy or
  policy restrictions"* (§6.1). P7 is the source of those restrictions; P10 stores them.
- Residual review must confirm *"that the model did not ignore a sensitivity restriction"* (§7.9) and
  placement validation must confirm *"that a sensitive file is handled under the user's privacy policy"*
  (§6.10). Both call P7's predicates rather than re-deriving them.

Explicitly **not** owned: the dossier's shape and the validator (P8, §3.6/§4.8/§6.10/§7.9); the mutation
transaction (P12, §8.3); node privacy storage (P10, §5.12); the six reliability states (P6, §3.13).

---

## Contract in

| From | What P7 requires | Design |
|---|---|---|
| **P1** | `file_id`, `content_hash`, current path, path history; an append-only event log that P7 appends to and never mutates; supersede-never-overwrite semantics | §0, §8.2 |
| **P3** | The corpus. Files excluded at scan never reach the gate | §1.1, §1.2 |
| **P4** | Observation records whose `Location` is precise enough to address a **bounded span** — document zone, page number, text offset (§2.2); table/row/cell (§2.3); EXIF field or OCR region (§2.8). The gate materialises excerpts by `(observation_key, span)` — P4's content-addressed citation handle, never the per-row `observation_id`, which dies on extractor upgrade (M14). It cannot honour "send the excerpt" if the observation is not span-addressable. | §2.8, §2.2 |
| **P5** | `reliability state` on each observation, and the *"indexed-but-unreadable"* marking for unsupported proprietary formats (§2.9). An unreadable extraction result maps to handling class `unreadable_unclassified`, and is distinct from an empty one — §2.4: *"an empty extraction result is different from an extractor that does not yet exist."* | §2.9, §2.4 |
| **P6** | The `sensitivity` field (§3.12) with the five class values; `file_facts` rows carrying evidence links; the six reliability states (§3.13), so a user reclassification is a `user_confirmed` fact that outranks a `validated` detector fact by the design's own ordering — P6's canonical snake_case literals, never a respelling. **P6 must accept `sensitivity` as a first-class universal field** (§3.11) rather than a domain-scoped one. | §3.11, §3.12, §3.13 |
| **P8** | Compliance with the calling discipline below: requests carry references, never materialised content. P8's transport exposes no string-prompt entry point. P8 calls `Gate.release` under the signature published in Contract out §6 — that signature is adopted verbatim on both sides (B2). P8 also measures `Maximum dossier tokens per model call` **before** it calls the gate and runs §8.6's reduction ladder there; the gate's `dossier_over_budget` denial is a backstop only (M9, below). | §8.4, §8.6 |
| **P10** | Node type `protected` (§5.12) and per-node privacy restrictions on the destination profile (§6.1), populated from P7's policy rather than authored independently. | §5.12, §6.1 |
| **P2** | A replay bundle slot for *"policy settings"* (§8.5). | §8.5 |

---

## Contract out

### 1. Handling classes — closed vocabulary (§8.4)

```text
public_low                          Public or low sensitivity
personal_non_sensitive              Personal but non-sensitive
sensitive_personal                  Sensitive personal
highly_sensitive_credential_bearing Highly sensitive or credential-bearing
unreadable_unclassified             Unreadable or unclassified
```

A value outside this set is a load error, not a fallback. **Absence of a classification resolves to
`unreadable_unclassified`, never to `public_low`.** §8.4 makes classification a precondition of
escalation (*"classify data into handling classes before LLM escalation"*), so a file that has not been
classified has not met the precondition for a model call — see Budgets, below.

### 2. Classification record (§8.4, written through P6's `sensitivity` field)

```text
file_id                 P1 identity
content_hash            P1 identity — a classification is bound to a file *version* (§8.2)
handling_class          one of the five above
protected               boolean; entered immediately for the §8.4 kinds
basis                   detector | safety_domain | user
evidence_refs[]         observation keys (P4, M14) that support the class — §8.4: "evidence-backed"
reliability_state       P6's six states (§3.13); user revision writes user_confirmed
observed_at             §8.2 "time of observation"
```

*Evidence-backed* (§8.4) means `evidence_refs` is non-empty for any `basis = detector` classification, on
the same principle as §3.1: every fact preserves where it came from. *User-revisable* (§8.4) means a user
reclassification is a new `user_confirmed` fact that **supersedes** the prior one; §8.2 forbids
overwriting the earlier record.

**Protected state** (§8.4) is entered immediately for: a scanned passport, tax statement, medical
document, authentication key, or account record. Its three consequences, verbatim from §8.4:

1. not included in cloud-model prompts by default;
2. no raw content displayed in general group summaries;
3. not moved automatically without a user policy that explicitly permits it.

Plus §7.3 for material held under the `Protected Records` residual template: filenames and content must
not be exposed in model prompts at all.

Whether `protected` is exactly co-extensive with the top two classes is **not settled by the design** —
see Open questions. Neighbouring parts should consume the `protected` flag, not infer it from the class.

### 3. The always-local set (§8.4) — never releasable by any mode

```text
paths                     complete extracted text        OCR output
file hashes               image EXIF                     GPS
user edits                group memberships              raw sensitive values
```

Nothing in this set can be named as a releasable item kind. The gate has no code path that materialises
one.

### 4. Releasable item kinds (§8.4) — the compact dossier, and nothing else

§8.4 permits *"selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata, and
evidence references"*, and forbids *"full documents where a short heading or OCR excerpt is enough"*.

```text
excerpt              { observation_key, span, reason }  resolved by the gate from local storage
redacted_identifier  { observation_key, span, identifier_class }
candidate_label      a label already present in the local database (§4.5, §5.4)
metadata_field       a named non-sensitive field (e.g. file type, page count, capture year)
evidence_reference   an id only — no content
filename             see the flag below
```

`excerpt` requests carry a span, so a "whole document" request is not expressible: an item that resolves
to the complete extracted text of a file is rejected as `whole_document_requested` (§8.4).

> **Flagged reading — `filename`.** §8.4 places *paths* in the always-local set; §7.7 lists *the
> filename* as part of the residual dossier; §7.3 forbids filenames in prompts **only** for Protected
> Records. This contract reads directory path ≠ filename — §7.3's carve-out is vacuous under any other
> reading — and therefore permits `filename` for non-protected files and denies it for protected ones.
> This is the one place where the contract resolves an apparent conflict rather than deferring it,
> because P8 and P11 cannot build without an answer. Listed in Open questions for the reviewer.

### 5. Operation modes (§8.4) — closed vocabulary, semantics verbatim

```text
offline         No content leaves the device; only local rules and local models may run.
local_model     Local extraction plus a user-installed local LLM for eligible dossiers.
hybrid          Sensitive files remain local; non-sensitive bounded dossiers may use a cloud LLM.
cloud_assisted  User explicitly permits selected corpus areas to use a cloud model.
```

The mode, together with per-area consent grants and redaction settings, is the **authorizing policy**
named by the audit record. §8.8 places *"Privacy and model-consent policies"* inside the plan version —
see Plan versioning, below.

**The shipped default is constrained, even though the design names no mode (W1).** §8.4 states a
`must`: *"The default posture **must** therefore be local-first and data-minimizing."* The design
does not say which of the four modes ships as the install default, so P7 does not pick one — but the
`must` binds whatever is picked, and P7 states the binding here rather than leaving it as a question:

- **The install default must be `offline` or `local_model`.** Those are the two modes under which no
  content leaves the device. `hybrid` and `cloud_assisted` both permit a cloud model without the user
  having asked for one, which is the posture §8.4's sentence forbids as a *default*. Either remains a
  legitimate mode the user may **choose**; neither may be what they find on install.
- **Where the design is silent on a redaction default, the more redacting option is the default.**
  Data-minimizing is the second half of the same `must`, and §8.4's own example — *"a summary such as
  '11 protected identity records' may be safe to show, while a visible list of passport filenames on a
  shared screen may not be"* — settles the direction: the aggregate is the default, the expansion is
  the user's act. The same rule applies to every redaction setting §8.4 calls *configurable*.
- **This is a floor, not a mode choice.** Which of `offline` and `local_model` ships is still open
  (Open question 11) and P7 will not guess it; what is closed is that the answer cannot be `hybrid` or
  `cloud_assisted`, and that no build configuration, first-run flow, or migration may set one of those
  as the state a user arrives at without choosing it.

### 6. The gate — call signature

```text
Gate.release(ModelCallRequest) -> ReleaseDecision
```

**This is the only gate signature in the product.** P8's `seal(...) -> SealedDossier | Refusal` is
withdrawn; P8 adopts this call, this return union, and these field names verbatim (B2). There is one
door, named once.

```text
ModelCallRequest
  stage                which pipeline stage is asking      §8.5 requires per-stage decomposition
  target               { file_ids[], group_id? }           §4.4, §7.7
  model_target         { locality: local | cloud, model_id, provider }
  requested_items[]    item kinds from §4 above — references only, never materialised content
  prompt_template_id
  prompt_fingerprint   §3.4, §8.2, §8.4 — `call_site` is already inside the fingerprint, so it is
                       not a separate request field and not a separate binding term (B2)
  max_dossier_tokens   §8.6 ceiling the caller is operating under; P8 has already measured against
                       it and applied §8.6's ladder before calling (M9)
```

```text
ReleaseDecision = Released | Denied | NeedsConsent
```

```text
Released
  release_id           single-use; bound to (model_target, prompt_fingerprint, policy_version)
  audit_id             the audit record, already appended before this value was returned
  policy_version       the privacy/consent policy in force, stamped by the gate — the gate owns the
                       policy, so the caller does not supply this value, it echoes it (§8.4, §8.8)
  materialised_items[] post-redaction values only
  redaction_manifest[] per item: identifier class, redacted yes/no
  model_target         echoed and bound
```

The binding tuple is `(model_target, prompt_fingerprint, policy_version)` (B2). `audit_id` remains a
field of `Released` — it is what makes the record traceable — but it is not a binding term: two
releases differing only in audit record are the same authorization, while a release spent under a
different policy version is not.

```text
Denied
  reason               protected_cloud_target | unclassified | policy_revoked
                     | protected_records_template | whole_document_requested
                     | dossier_over_budget | always_local_item | mode_forbids_target
                       — `dossier_over_budget` is a backstop that should never fire in a
                         correct pipeline; P8 measures and reduces before calling (M9)
  explanation          user-facing, evidence-referenced
  remedy_options[]     what the caller may legitimately do instead (§8.6)
```

```text
NeedsConsent
  requirement          which items require sensitive text, and why
  options              local_model | cloud_model | redacted_prompt | no_model_use
```

`NeedsConsent` is not an invention: §8.4 states that if a model needs text containing sensitive content,
*"the user should see that requirement and choose whether to allow a local model, a cloud model, a
redacted prompt, or no model use"* — those four options, exactly.

**`NeedsConsent` returns control to the calling part; it is never an outcome the caller may absorb**
(B2). The caller does not retry, does not downgrade the request, and does not record an abstention: it
surfaces the requirement and the four options through P13 (S4 — the review and approval surface) and
waits for the user's choice. A part that maps `NeedsConsent` onto its own abstention value has deleted
the §8.4 requirement rather than satisfied it, which is why this branch is distinct from `Denied`:
`Denied` is the gate's answer, `NeedsConsent` is a question that only the user can answer. Consent
pending is not consent refused.

**Binding and single use** exist to keep the audit record truthful. §8.4 requires the record to show
*which model received the data* and *the prompt fingerprint*; a payload that could be replayed against a
different model or under a different prompt would make both fields false. A release is consumed on first
transport use.

**Ordering guarantee:** the audit record is appended (P1, §8.2) **before** `Released` is returned. There
is no interval in which content is releasable and unaudited.

### 7. Consent-aware audit record (§8.4)

The six fields §8.4 requires, verbatim in intent:

```text
authorizing_policy    what policy authorized the call
file_sensitivity      whether the file was sensitive
excerpts_included     which excerpts were included
redaction_applied     whether values were redacted
model                 which model received the data
prompt_fingerprint    the prompt fingerprint
```

Carried additionally because other sections require it:

```text
audit_id, release_id
appended_at                            §8.2 "time of observation"
stage                                  §8.5 per-stage decomposition
target file_ids / group_id             §8.2 event record: file ID, content hash
content_hashes                         §8.2 — the record is bound to file versions
operation_mode at time of call         §8.4 — part of the authorizing policy
plan_version                           §8.8
outcome                                released | denied | consent_requested
```

`excerpts_included` stores `(observation_key, span)` pairs plus the `redaction_manifest`, not a second copy
of the text — the always-local text already exists once (§8.4). The requirement this must satisfy is that
the record can answer, exactly, *what left the device*; a record that cannot reconstruct the released
payload from local storage fails §8.4's stated purpose.

Every model call is recorded — §8.4 says *"Every model call"* without exempting local models. Denials and
consent requests are also appended, on the strength of §8.2 (*"Every significant event affecting a file"*)
and §8.6 (the UI must show *"what has been deferred, and why"*).

### 8. Revocation (§8.4)

```text
Gate.revoke(policy, scope)   -> RevocationResult
Gate.reclassify(file_id, handling_class, reason) -> new user_confirmed sensitivity fact
Gate.delete_derived(scope)   -> see Open questions (conflicts with §8.2)
```

```text
RevocationResult
  effective_from        future gate calls only
  prior_releases[]      from the audit log: model, provider, when, which excerpts
  retraction_limit      the mandatory statement that revocation cannot necessarily retract
                        data already sent to an external provider (§8.4)
```

The audit log is what makes `retraction_limit` truthful and specific rather than a generic disclaimer.
This is why a revocation may never delete audit records: §8.4 requires the product to *"communicate that
distinction clearly"*, which is impossible once the record of the send is gone.

### 9. Automatic-move predicate (§8.4)

```text
Gate.may_move_automatically(file_id, plan_version) -> { allowed, reason, permitting_policy? }
```

False for protected material unless a user policy explicitly permits it (§8.4). P11 records the answer in
the placement decision (§6.11 *"required review policy"*), P12 records it in the plan precondition
(§8.3 *"Sensitivity and consent state"*), and neither re-derives it. §7.11 adds that the system must not
*"move them out of a protected area without explicit user action."*

### 10. Display policy (§8.4)

```text
Gate.display_policy() -> RedactionSettings
  names | previews | thumbnails | ocr_text | location_data     each shown | redacted
Gate.summarize_protected(scope) -> { count, class_breakdown }  aggregate only, no filenames
```

The five configurable facets are §8.4's own list. The aggregate-safe rule is §8.4's own example — *"11
protected identity records"* is safe, a list of passport filenames is not — and it is the form §7.5's
residual surfacing screen already uses (`11 protected personal records`). §5.2 applies the same rule to
the tree canvas: a Finance or Identity proposal *"may be visible as a protected area, but the product
should avoid showing sensitive filenames."*

### 11. Fixtures published (so P8 can be built before P7 exists)

Request → decision pairs, one per `Denied.reason`, plus: a clean `Released` with redaction applied; a
`NeedsConsent` returning all four options; a protected file under each of the four modes; an
`unreadable_unclassified` file; a `Protected Records` residual request. Each fixture carries the audit
record the gate would have appended.

Two of these carry an obligation on P8 specifically. The `dossier_over_budget` fixture exists so P8 can
prove its ladder ran first — a P8 test that reaches this denial through the normal path is a P8 failure,
not a gate result (M9). The `NeedsConsent` fixture exists so P8 can prove it returns the branch to its
caller intact, with all four options, rather than folding it into `abstain` (B2).

---

## Deferred — manual design required

Nothing below is invented here. Each names what is deferred and which § defines it.

| Deferred | Defined by | Why it is not in this contract |
|---|---|---|
| **The sensitivity detection rules themselves** | §8.4 names five kinds that enter protected state; §3.15 names finance, identity, medical and legal as safety domains | The design states *what* is protected and never *how it is recognised*. The detector rule set, its signals, and its thresholds are hand-authored. P7 publishes the vocabulary the detectors write into. |
| **Gazetteer contents** | §3.7 | Named as a mechanism (*"validated gazetteers"*); contents never enumerated. |
| **The 200–300 template library, and each template's `privacy rules` / `sensitivity policy` fields** | §5.7 (library, `privacy rules`), §5.7 (LLM-generated templates carry a `sensitivity policy`) | Hand-authored per template. P7 publishes only the predicate §5.7's validator calls when it checks that a template does not *"expose protected information"*. |
| **Residual library contents beyond the nine §7.3 names** | §7.3 | The nine names and the `Protected Records` constraint are literal and used above; everything else, including the blank default locations, is hand-authored. |
| **Domain fact-schema fields beyond §3.11's table** | §3.11 | Only `sensitivity status` is used here, and it is literally in §3.11's universal set. |
| **Identifier classes and the redaction transform** | §8.4 says *"redacted identifiers"* and the audit record says *"whether values were redacted"* | Which identifier classes exist and how each is transformed is not enumerated anywhere in the design. `redaction_manifest` carries the class as an opaque string until this is authored. |
| **Numeric values for every ceiling** | §8.6 names the knobs, states they are *"configurable"*, and gives no values | Deferred to configuration, not to this contract. |
| **Consent-prompt and retraction-limit wording** | §8.4 requires the distinction be *"communicate[d] clearly"* | UX copy. |

---

## Done means

1. Five handling classes and four operation modes exist as closed vocabularies; an out-of-vocabulary
   value is a load error (§8.4).
2. Every file the gate can be asked about resolves to exactly one current `sensitivity` fact through P6,
   and absence resolves to `unreadable_unclassified` — never to `public_low` (§8.4, §8.6).
3. **Static property:** the model/connector transport has exactly one entry point and its only content
   parameter is a `Released`. No transport function accepts a string, a file path, or an
   observation record. Provable by inspection of the transport's signature, not by review discipline
   (§8.4).
4. Every `Released` carries an `audit_id` that already exists in the append-only log at the moment of
   return; no released payload has a missing or later-written audit record (§8.4, §8.2).
5. A release is bound to one `model_target` and one `prompt_fingerprint` and is consumed on first use;
   replaying it against a different model or prompt fails (§8.4).
6. Denials are produced, with reasons, for at minimum: a protected file with a cloud target under
   `hybrid` (§8.4); an `unreadable_unclassified` file (§8.4); an item that resolves to a whole document
   where a heading or excerpt exists (§8.4); a file under `Protected Records` (§7.3); an always-local
   item (§8.4); a request over `max_dossier_tokens` (§8.6 — the backstop of M9, reachable in test but
   not in a correct pipeline); a revoked policy (§8.4).
7. A request needing sensitive text returns `NeedsConsent` with all four §8.4 options, and **no caller
   converts it into an abstention, a denial, or a retry** — the branch reaches P13 and the user's choice
   comes back before any call is made (§8.4, B2). Testable from the gate side: the audit log holds a
   `consent_requested` event and no `model_release` for that request until a choice is recorded.
8. `revoke` changes only future calls, never deletes an audit record, and returns the prior-release list
   plus the retraction-limit statement (§8.4).
9. `may_move_automatically` is false for protected material absent an explicitly permitting policy, and
   P11/P12 consume the answer rather than re-deriving it (§8.4, §8.3, §6.11).
10. `summarize_protected` returns counts and class breakdown and cannot return filenames or content
    (§8.4, §5.2, §7.5).
11. Every one of the above has a published fixture, and P8's harness passes its own tests against those
    fixtures with P7 unimplemented.
12. **Local-first default (§8.4's `must`, W1).** With no user configuration present — a fresh install
    fixture and a migrated-from-nothing fixture — the resolved operation mode is `offline` or
    `local_model`, and every redaction setting the design leaves configurable resolves to its more
    redacting value (names redacted, protected sets aggregate-only). **Negative test:** no code path,
    build flag, packaged configuration file, or first-run flow produces a starting mode of `hybrid` or
    `cloud_assisted`; asserted by fixture and by grep over the shipped defaults, the way Done-means 1
    asserts the closed vocabularies. This test does **not** assert which of the two local modes ships —
    that stays open (Open question 11) — only that the default is one of them.
13. **Walking-skeleton obligation.** The map notes the skeleton exercises no privacy gate *"because
    nothing leaves the machine."* The skeleton must nonetheless assert: the classification exists for the
    scanned file; the gate is installed on the only egress path; `release` was called zero times; the
    audit log is empty; and a deliberate attempted call under `offline` returns `Denied` with reason
    `mode_forbids_target`. That is the seam test — that the door exists and is shut.

---

## Cross-cutting answers

### Provenance (§8.2)

**Appends:** `classification_assigned`, `classification_superseded` (including user reclassification),
`policy_set`, `consent_granted`, `consent_revoked`, `model_release`, `model_release_denied`,
`consent_requested`. Each carries the §8.2 event fields — event type, file ID, content hash, responsible
subsystem, model version and prompt fingerprint where applicable, user identity on explicit user action,
time of observation, and a structured explanation or evidence reference.

**Registration (B5).** These eight are **declared here as P7's event types** under P1's registration
rule: each part declares its types in its own SPEC, P1 validates against the union of the declarations,
and §8.2's nineteen names are reserved and may not be redefined by any part. None of the eight collides
with the nineteen. §8.2's list opens with *"This includes"*, so nineteen is a floor.

`model_release` and its consent-aware audit record are the same event; the audit record is the structured
explanation the §8.2 event format already provides for. **P1 OQ5 is settled: one log** (B5) — §8.2's own
event record already carries `prompt fingerprint`, which is P7/P8 audit data, so the design put model
audit and file provenance in the same log. §8.4's consent-aware record is that log with the consent
fields and `correction_scope`.

**Never overwrites:**

- a prior classification — a revision *supersedes* and both remain inspectable (§8.2's explicit rule, and
  its OCR example applies directly: an early detector and a later one may disagree and both survive);
- a prior audit record — revocation is a forward-only event, and §8.4's requirement to communicate that
  already-sent data cannot be retracted is unsatisfiable if the send record is erasable;
- a prior consent grant — a revocation is a new event, not an erasure of the grant that authorized
  earlier calls.

Note the unresolved tension with §8.4's *"review and delete local derived data"* — Open questions.

### Budgets and degradation (§8.6)

**`Maximum dossier tokens per model call` — the split, stated in both specs (M9).** **P8 measures the
dossier against this ceiling *before* it calls the gate, and runs §8.6's four-rung reduction ladder
there** — summarize deterministic facts, preserve anchor excerpts, split the task, defer the decision, in
that order. **P7 keeps `dossier_over_budget` as a backstop denial that should never fire.** The earlier
reading — that the gate is the only place the ceiling is real — is withdrawn: it is wrong in consequence,
because a gate-only check runs after the last point at which the dossier can still be reduced, so the
ladder would never execute and every over-budget dossier would become a denial instead of a summarize,
split, or defer. That is strictly less capable and, by §8.6's own preference for deferral over silent
loss, less accurate. The gate still enforces the ceiling because §8.6 forbids a prompt that *"truncate[s]
silently in a way that removes the decisive evidence"* and the gate is the last place to catch a caller
that skipped its ladder — but a `dossier_over_budget` denial in a running pipeline is a P8 defect to fix,
not a normal outcome. **The gate never truncates and never reduces**; reduction changes what the model
sees, which is a dossier decision, and the gate's only content operations are resolution and redaction.

**Ceilings P7 does not own:** `Maximum LLM calls per thousand files` and `Maximum model cost per scan`
are **P8's**, as the single egress point where calls and cost are countable (O9). P7 counts releases in
its audit log, which is evidence for those ceilings, never the enforcement of them.

**Ceilings P7 consumes:** classification runs before LLM escalation (§8.4) and is therefore inside the
cheap deterministic tier §8.6 puts first — it is not itself an LLM cost.

**Degradation:** if classification cannot complete within budget, the file takes
`unreadable_unclassified` and the gate denies escalation. This is the direct application of §8.6's rule
that **cost exhaustion must never turn into lower-quality automatic classification** — the failure mode
this forbids is precisely defaulting an unclassified file to `public_low` so the pipeline can continue.
Per §8.6 the evidence is retained, the stage is marked deferred, and the file goes to review rather than
being guessed at. The UI counts such files in the deferred summary §8.6 describes.

### Correction learning (§8.7)

**Recorded actions:** reclassifying a file as private (§8.4, and §8.7 lists *"marking a file private"*
among the user actions that carry organization information); §7.10's *"mark it as private"* in residual
review; downgrading a classification; granting, changing, or revoking a policy; changing a redaction
setting; granting or withdrawing an automatic-move permission for protected material.

**Scope:** each correction carries a scope drawn from §8.7's enumerated set — file / group / destination
node / template / domain / corpus. Default is **file** scope, following §8.7's own worked warning that one
transcript belonging in one packet *"should not teach the engine that all transcripts belong there."*
Broader scope is applied only where the user selects it. Whether repeated reclassification may
auto-generalize the way §8.7 lets a repeated residual destination become a corpus preference is not
settled — Open questions.

**Query before classify.** Before assigning a handling class the user has already set or rejected at
this scope, P7 queries P1 `learning_records` for `proposal_class = privacy` and
`basis_key = (file_id, handling_class)` ([`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)).
A matching unresected reject does not re-prompt the same classification. Generalization of *repeated*
reclassification to a corpus floor remains Open question 7.

**Negative feedback:** §8.7 requires rejections be stored *with the evidence that produced them*. A user
downgrading a classification stores the observation keys the detector fired on, so the same signal does
not resurface the same false protection. **The key, not the id, is what makes that durable** (M14): a
per-row `observation_id` dies when the extractor is upgraded, so a negative example recorded today
would silently stop resolving and the same false protection would return. The same reason binds the
§8.4 audit record above — it must answer *what left the device* permanently, not until the next
extractor version. Learned privacy preferences are inspectable and resettable, per §8.7.

**Not done:** no cross-user learning, no global training on the corpus (§8.7).

### Plan versioning (§8.8)

**Belongs to the plan version** — §8.8 lists it literally: *"Privacy and model-consent policies."* That
is the operation mode, per-area consent grants, redaction settings, and automatic-move permissions for
protected material.

**Belongs to the shared evidence database** — §8.8: *"The evidence database remains shared across plan
versions."* That is the classification facts (they are `file_facts`, §3.12), their evidence links, and
the audit records; §8.2 additionally places `Sensitivity state` in the file record, which is not
plan-scoped.

**Consequences.** Adopting a new plan version does not re-authorize a prior denial and does not
retroactively release anything — §8.8: *"A new plan should never silently reclassify or move old files."*
A diff between plan versions must show a privacy-policy change (mode change, consent granted or revoked,
redaction setting changed) as a first-class diff line, since §8.8 requires the diff be *"meaningful"* and
a silent widening of egress policy is the least acceptable silent change in the product. Audit records
carry `plan_version` so §8.5 replay can reproduce the policy in force at each call.

---

## Open questions

Settled since the contract review, by [`../../04-resolutions.md`](../../04-resolutions.md) — recorded
here so nothing is re-adjudicated: the gate signature and its binding tuple (B2); whether `NeedsConsent`
may be absorbed by a caller — it may not (B2); who enforces `Maximum dossier tokens per model call` and
runs §8.6's ladder (M9); whether P7 may declare event types outside §8.2's nineteen — yes, by
registration (B5); and whether §8.4's audit record is the same log as §8.2's provenance — yes (B5,
settling P1 OQ5, which P7 had answered without P1's agreement). None of the eleven below is settled by
that document; all eleven remain open.

1. **Is `protected` exactly the top two handling classes?** §8.4 lists five classes and, separately, five
   kinds of material that *"enter a protected state immediately"*, without stating the relation. Affects
   P9 (§4.9 sub-threshold surfacing), P10 (§5.12 `protected` node type), P11 (§6.10 sensitivity check).
2. **Filename vs. path.** §8.4 puts *paths* in the always-local set; §7.7 puts *the filename* in the
   residual dossier; §7.3 forbids filenames in prompts only for Protected Records. This contract adopts
   the reading that makes §7.3 non-vacuous (§4 above) and flags it. Affects P8 and P11 directly.
3. **What is a "corpus area"?** `cloud_assisted` permits a cloud model for *"selected corpus areas"*
   (§8.4). A scan root (§1.1)? A frozen tree node (§5.12)? An accepted group (§4)? A domain (§3.15)?
   Consent grants cannot be scoped until this is named. Affects P3, P9, P10.
4. **Deletion versus append-only.** §8.4 gives the user the right to *"review and delete local derived
   data"*; §8.2 requires an append-only provenance log and forbids overwriting the evidence record. Which
   wins, what counts as "derived", and are audit records themselves deletable? Affects P1's core contract
   and P6's facts.
5. **Does `unreadable_unclassified` permit a *local* model call?** §8.4 requires classification before LLM
   escalation, but under `offline` and `local_model` nothing leaves the device. Reading escalation
   strictly denies local calls on unclassified files, which may block exactly the OCR-opaque screenshots
   §2.7 and §7.8 want a model to interpret. Affects P8 and P11.
6. **Is a local-model call a consent event or only an audit event?** §8.4 audits *every* model call and
   offers *"a local model"* as one of the four consent options, implying local is a lesser but non-zero
   consent step. The threshold at which a local call needs a prompt is unstated. Affects P8.
7. **Does repeated reclassification generalize?** §8.7 allows a repeated residual destination to become a
   corpus-level preference; it does not say whether repeated privacy corrections may raise a sensitivity
   floor for a class of files. Affects P6 and P7's learning records.
8. **May a replay bundle carry audit records and excerpt spans?** §8.5 allows *"a frozen corpus snapshot
   or a metadata-safe representation of one"* and lists *"policy settings"*. Whether a bundle intended to
   leave the user's machine may carry audit records — which name excerpts — is unstated. Affects P2.
9. **What is an "external connector" besides a model?** §8.4 gates *"any model or external connector"*,
   but no non-model connector is named in the twelve parts; §8.3's cloud-synced directories are a
   filesystem concern, not a content egress. If a connector is added later, does it route through
   `Gate.release`? Affects P12 and anything added beyond the twelve.
10. **Retention.** How long audit records, consent grants, and superseded classifications are kept. The
    design states no retention period anywhere.
11. **The local-first default — narrowed, not open-ended (W1).** §8.4's `must` is now binding in
    Contract out §5 and tested by Done-means 12: the install default is `offline` or `local_model`, and
    every silent redaction setting defaults to its more redacting value. What remains genuinely open is
    only **which of those two** ships, which turns on whether a local model is assumed present — the
    design names no answer and P7 will not guess one. Nothing that remains open here permits `hybrid`
    or `cloud_assisted` as a default.

**UNRESOLVED — I6, deferred to this part's build (ratified 2026-08-19).** §8.4's right to "review and
delete local derived data" contradicts §8.2's R6, which forbids updating or deleting an event. The
product cannot ship unable to forget a scanned passport's OCR text, and cannot ship silently deleting
from the provenance log. The candidate resolution on the table is to tombstone derived projections
while keeping `events` append-only forever, but it is **not** ratified. P7 must resolve this before it
is built. P1 has been told not to assume derived rows are permanent, so the tombstone option stays
available. *Also open in:* P5 OQ6, P13 OQ11, P1 OQ16.
