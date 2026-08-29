# P8 — LLM harness and validator

Owns: §3.3, §3.6, §4.8, §6.10, §7.9
Status: contract draft

---

## Purpose

The design describes one mechanism four times: **a bounded evidence dossier goes to a model, the
model must answer with citations to that evidence or say it does not know, a deterministic
validator checks every citation and constraint, and the result is accepted, downgraded, rejected,
or abstained.** §3.6 states it for facts, §4.8 for groups, §6.10 for placements, §7.9 for residual
files. §5.7 applies the same discipline to LLM-generated custom templates.

P8 is that mechanism, built once. It is the **only** component in the product that issues a model
call. Every other part builds a dossier request and receives a verdict; no other part talks to a
model, parses a model response, or decides whether model output is trustworthy.

Two consequences follow, and they are the reason this part exists:

1. **§8.4's gate cannot be bypassed.** Privacy policy must be enforced *before content reaches any
   model*. One egress point means one place to enforce it, and the harness is structured so that a
   call without a P7 `Released` cannot be constructed at all (see
   [Contract out §7](#7-the-single-egress-point)).
2. **§8.5's "LLM grounding" metric is one measurement, not four.** *Did every cited excerpt exist?
   Did the model return `unknown` when evidence was insufficient?* Both are answerable per call
   because every call, at every site, emits the same grounding report.

The validator is **deterministic** (§4.8's word). It never calls a model to check a model. Given the
same released dossier, the same response bytes, the same evidence snapshot, and the same policy
version, it produces a byte-identical verdict. Without that property §8.5's replay and shadow mode
cannot exist.

---

## Design slice owned

| § | What P8 owns from it |
|---|---|
| §3.3 | The rules/LLM boundary: which cases are eligible for a model call at all; the citation obligation; the mandatory `unknown`; the four validator clauses including *"appropriate for a proposal rather than merely a search hint"* |
| §3.6 | Fact-level validation: field in active schema, cited quote present in stored evidence, value normalizes safely, no stronger direct or rule-validated fact contradicts; the useful-but-weak → possible-clue downgrade |
| §4.8 | Group-level validation: the six checks, plus the context-supported-membership outcome routed to user review, plus the requirement that retrieval / interpretation / validation / acceptance failures be logged separately |
| §6.10 | Placement-level validation: node exists in the frozen tree, no invented date/institution/project/node, stronger conflicts not ignored, sensitive file handled under privacy policy; the **two-condition acceptance rule**; correct abstention as a success outcome |
| §7.9 | Residual-level validation: destination exists in the frozen tree, evidence appears in the file record, no sensitivity restriction ignored, no stronger existing relationship overlooked; the hand-back of credibly-connected files to the §6 engine |

**Also enforced by P8, owned elsewhere:**

- §4.5 — the four constrained group tasks and *"the model's response must be structured and
  evidence-citing"*. P8 owns the response schema that makes this enforceable; P9 owns the task
  semantics.
- §6.6, §6.7 — the hierarchical-destination-judge call shape and the rule that the model *"should
  never fill a missing slot merely because a complete-looking path is aesthetically preferable."*
  P8 owns the per-dimension support check that catches it; P11 owns the placement engine.
- §7.7 — the eight-item controlled action set. P8 enforces closure over it; P11 owns the actions'
  effects.
- §5.7 — *"structured output constraints and schema validation should enforce the required template
  shape."* P8 owns structured-output enforcement and the citation check for generated templates;
  P10 owns the template design-quality checks §5.7 assigns to "the engine" (repeated parent
  dimension, one-child levels, depth limits, author-as-collector, protected exposure, empty
  branches). **Settled** — this split is adopted by
  [`../../05-minor-resolutions.md`](../../05-minor-resolutions.md); it is no longer an open
  question.
- §8.5 — the LLM-grounding row. P8 emits the measurement; P2 owns the harness that reads it.
- §3.4 — P8 computes and publishes the `prompt_fingerprint` and `model_id` that P6's cache key
  requires; P6 owns cache-key composition.

**Explicitly not owned:** dossier *content selection* (P6/P9/P10/P11 decide what goes in), retrieval
quality (P9/P11), §4.9's stop rules (P9's pre-dossier gate — P8 only enforces the two of them §4.8
and §8.7 restate), the placement decision record (§6.11, P11's), and prompt wording (deferred).

---

## Contract in

### From P7 — privacy and consent gate (§8.4) — hard dependency

P8 requires exactly one function, and its signature is what makes the gate unbypassable. **The
signature is P7's, adopted verbatim** (B2). P8's earlier `seal(dossier_request, call_site,
model_target, policy_version) -> SealedDossier | Refusal` is withdrawn: two names for one door is the
failure this seam exists to prevent, and P7 owns §8.4.

```text
Gate.release(ModelCallRequest) -> Released | Denied | NeedsConsent
```

```text
ModelCallRequest   stage · target · model_target · requested_items[] · prompt_template_id ·
                   prompt_fingerprint · max_dossier_tokens          -- references only
Released           release_id · audit_id · policy_version · materialised_items[] ·
                   redaction_manifest[] · model_target
Denied             reason · explanation · remedy_options[]
NeedsConsent       requirement · options: local_model | cloud_model | redacted_prompt | no_model_use
```

- `ModelCallRequest` carries **references only** — file IDs, evidence refs, node IDs, group IDs, and
  requested excerpt spans. It carries no document text, no OCR text, no paths, no raw values.
- The gate is the only component that resolves a reference into text. Content therefore materialises
  for the first time *inside* P7, after handling-class classification, redaction, and mode policy
  (§8.4's four modes) have been applied.
- A `Released` is single-use and bound to `(model_target, prompt_fingerprint, policy_version)` (B2).
  `call_site` is **not** a binding term — it is already inside `prompt_fingerprint` under P8's own
  fingerprint rule (see [Provenance](#provenance-82)), so binding on it separately would restate the
  same constraint under a second name. A release approved for a local model cannot be spent on a
  cloud model; a release cannot be replayed.

**The three branches, and what P8 does with each.**

`Released` — the call proceeds. This is the only branch that reaches a model.

`Denied` — the gate has answered, and the answer is no. P8 records it as its **`Refusal`**: outcome
`abstain`, reason `PRIVACY_GATE_REFUSED`, carrying the gate's `reason` and `remedy_options[]`.
**`Refusal` names gate denial and nothing else** (B2). It is a normal outcome, never an error to
swallow (see [Budgets](#budgets-and-degradation-86)).

`NeedsConsent` — **the call is not refused, it is unanswered, and only the user can answer it.** P8
**returns control to the calling part** with the requirement and §8.4's four options intact — local
model, cloud model, redacted prompt, or no model use — and the caller surfaces them through P13, the
review and approval surface (S4). P8 issues no call and produces no verdict. **P8 must never map this
branch to `abstain`**: there is no reason code for it, and none may be added. That mapping is the
precise failure B2 was raised to remove — §8.4 requires the *user* to see the requirement and choose,
so an abstention makes the choice for them, silently selecting "no model use" without asking. Consent
pending is not consent refused. When the user chooses, the caller composes a **new**
`ModelCallRequest` under the chosen option; the original is never resumed, because the policy it was
composed under is not the policy that now applies.

Also required: the handling classes and operation modes (§8.4), and the consent-aware audit record
that P8 references by `audit_id` on every call event.

### From P4 — evidence shape (§2.8)

A stable `evidence_ref` that resolves to one observation. **`evidence_ref` is P4's
`observation_key`** — the content-addressed handle — **not `observation_id`** (M14). An extractor
upgrade emits a new row with a new `observation_id`, so every verdict, stored rejection and §8.7
negative example citing the id would decay on upgrade; the key stays permanently resolvable, which
is what §8.7 requires of a negative example recorded today.

From it: raw value, normalized candidate value, location, **`context_before`, `context_after`,
`context_truncated`** (M5 — P4's three-field split of §2.8's single "surrounding context" line, kept
because §8.4 must be able to redact a value without dropping the context around it; P8 reproduces
the three names, not the one), occurrence count, reliability state, extractor name and version. P8
validates citations against the **raw** value (§2.8: raw is retained separately from normalized).

### From P6 — facts and facets (§3.1–3.14)

- The active domain schema for a subject file — the allowed field set (§3.11), needed for
  `FIELD_NOT_IN_ACTIVE_SCHEMA`.
- A normalizer: `normalize(field, raw_value) -> value | not_normalizable` (§3.6), including the
  gazetteer and word-boundary discipline (§3.7).
- A total ordering over the six reliability states (§3.13) so that "stronger" in §3.6/§4.8/§6.10 is
  decidable: `User-confirmed > Direct > Validated > LLM-supported > Possible`, with `Rejected`
  excluded. P8 treats this ordering as given; it does not define it.
- A contradiction oracle: `contradicts(claim, existing_fact) -> bool`.

### From P1 — storage, identity, provenance (§0, §8.2)

File identity by content hash, the append-only event log, and supersede-never-overwrite semantics
for the records P8 writes.

### From P9 — grouping (§4)

The candidate group dossier contents §4.4 enumerates, with the direct-anchor / context-supported
distinction already marked (P8 does not infer it), and the typed graph edges.

### From P10 — tree design and freeze (§5)

- A node-existence oracle over the **frozen** tree, per plan version: `node_exists(node_id,
  plan_version) -> bool` (§6.10, §7.9).
- Destination profiles (§6.1) for dossier construction.
- The approved residual-library configuration (§7.4) — the closed target set for site D.
- The strict template JSON schema (§5.7) — the response schema for site E.

### From P11 — placement and residual (§6, §7)

The placement dossier contents §6.6 enumerates including deterministic scores and the candidate
ranking, and the residual dossier contents §7.7 enumerates.

### From P2 — eval and replay (§8.5)

The replay bundle format, and the per-item expectation annotations (expected accept / expected
abstain) that turn P8's observed grounding report into a pass/fail.

---

## Contract out

### 1. The dossier

The dossier is the **only** input to a model call (§4.4: *"the dossier is the actual input to the
LLM"*). It is closed-world: the model may cite nothing that is not in it, and may name no candidate
that is not in it (§4.5: *"may not invent group members beyond those retrieved by the engine"*;
§6.6: the model *"does not receive the whole folder tree"*).

**Common envelope — every site:**

```text
dossier_id
call_site               A_fact | B_group | C_placement | D_residual | E_template
subject                 file_id | group_id | file_or_group_id | file_or_batch_id | group_id
eligibility_reason      one value from this site's closed list (see §2 below)
plan_version            null at A and B; required at C, D, E              (§8.8)
policy_version          privacy/consent + placement policy in force        (§8.4, §8.8)
allowed_vocabulary      the closed set the response may draw from          (per site, below)
evidence_items[]        evidence_ref, kind, location, excerpt_span,
                        reliability_state, basis: direct-anchor
                        | context-supported                                (§2.8, §3.13, §4.4)
conflicts[]             known conflicting facts and suppressed candidates  (§4.4, §6.6)
budget                  max_dossier_tokens, reduction_rung_applied         (§8.6)
release                 P7's `Released` — absent means no call is possible (§8.4, B2)
```

`basis` is supplied by the dossier builder, never inferred by P8. §4.4 is explicit that the
dossier *"explicitly distinguishes direct evidence from inferred context"*; it is what makes the
`accept_direct` / `accept_context_supported` split decidable rather than a judgement call.

**It is P9's vocabulary, under P9's name** (MINOR 6's rule: the part that owns the concept names it).
This field was `support_kind: direct | context` and was wrong twice. **P9 already publishes
`support_kind` for something else** — the six retrieval channels on `Membership.support[]`
(`shared-validated-fact`, `duplicate-or-version-link`, …) — so one name meant two things across the
seam where P9's groups become P8's dossiers, and a validator checking "the" `support_kind` vocabulary
would reject every valid value from the other side. And `direct | context` was a third spelling of
`Membership.basis = direct-anchor | context-supported`, which P8's own `accept_direct` /
`accept_context_supported` outcomes already use. One concept, one name, one spelling: P9's.
Which of P9's three `basis` values can reach a given call site is the per-site question below;
this rule fixes the vocabulary, not the eligibility.

**Per-site payload — the four sites side by side.** Every row is quoted from the design; nothing is
added by the merge:

| | A — fact (§3.3) | B — group (§4.4) | C — placement (§6.6) | D — residual (§7.7) |
|---|---|---|---|---|
| Subject | one file | one candidate group | one file **or** one accepted group (§6.8) | one file **or** one small homogeneous batch |
| Evidence | that file's observations only | anchor files (rich), context-supported candidate members, short evidence excerpts | target's direct + validated facts, extracted excerpts or OCR, accepted group memberships, graph anchor evidence | filename, file type, creation date, extracted text or OCR, metadata, weak graph relationships |
| Structure | active domain schemas (§3.11); the file's existing facts with reliability states | proposed grouping basis; typed graph edges; key facts | candidate node profiles, representative files already accepted in those nodes, missing fields, deterministic scores | user-approved residual library, existing relevant folders, representative examples from approved residual destinations |
| Conflicts | existing stronger facts | conflicts (§4.4) | known conflicts (§6.6) | — |
| Policy | — | — | sensitivity state | sensitivity state; the user's residual-placement policy |
| `allowed_vocabulary` | fields of the active domain schemas | allowed domain schemas + group categories | the top legal candidate node IDs **only** | the eight actions + approved residual node IDs + approved parent branch IDs + accepted group IDs |

Site E (§5.7) payload: group dossier, representative files, validated facts, the user-approved group
label, existing destination vocabulary, structural constraints.

### 2. Call eligibility

§6.6: the model *"should not be called for direct, unique matches."* §8.6: *"LLM calls are reserved
for bounded ambiguities, group coherence, custom-template generation, and residual interpretation."*
The harness enforces this by requiring `eligibility_reason` from a closed per-site list and refusing
the call otherwise (`NOT_ELIGIBLE_FOR_MODEL`):

| Site | Closed list, quoted from the design |
|---|---|
| A (§3.3) | remains ambiguous · has multiple plausible domains · contains language that requires interpretation |
| B (§4.x) | a candidate group with a valid anchor exists and needs coherence, membership, outlier, or label judgement (§4.5). §4.9's stop rules are P9's pre-dossier gate; P8 does not re-implement them |
| C (§6.6) | several legal nodes remain plausible · file is an accepted context member but lacks a key branch-level fact · a group may need to be placed together · a custom template requires semantic interpretation · OCR or filenames are vague · direct facts conflict |
| D (§7.6, §7.7) | the user has opted this residual set in to AI review |
| E (§5.7) | an accepted organizational group does not fit any existing template |

### 3. The response

Structured output, schema-enforced per site. Every response is a set of **claims**; every claim
carries either citations or an explicit insufficiency statement — §4.5 requires *"an exact
supporting quote, metadata field, graph relationship, or explicit statement that there is
insufficient evidence."*

```text
Claim {
  ...site-specific payload...
  citations[]      : { evidence_ref, cited_span | metadata_field_name, why_it_supports }
  unknown          : { insufficiency_statement }     -- mutually exclusive with citations
}
```

**Citation is by reference *and* verbatim span.** This is the one deliberate generalisation across
the four sites, and it is load-bearing:

- §3.6 requires the cited quote be *"actually present in the stored evidence"*; §4.8 requires *"every
  cited text span or metadata field exists in SQLite."* A free-text quote alone makes this a fuzzy
  string search. A reference alone lets a hallucinated quote ride on a real reference.
- Requiring both makes the check two exact comparisons: the ref resolves, and the span appears
  verbatim in what the model was shown. That is what makes §8.5's *"did every cited excerpt exist?"*
  a boolean per citation rather than a similarity score.

Per-site response shapes:

| Site | Claim payload | Constraint from the design |
|---|---|---|
| A | `{ field, value }` or `unknown` | field must be in `allowed_vocabulary` (§3.3, §3.5) |
| B | `{ coherent: yes\|no\|insufficient, basis }`, `members[]: { file_id, include\|exclude\|uncertain }`, `outliers[]: { file_id, conflict_kind }`, `label?: { display_label, category }` | label present **only if** coherence supported (§4.5); no final folder hierarchy; no member outside the dossier (§4.5) |
| C | `{ destination: node_id \| none, per_dimension_support[]: { dimension, value, direct \| context \| unsupported }, alternatives[], conflicts_considered[] }` | destination must be in `allowed_vocabulary`; a dimension marked `unsupported` may not appear in the chosen path (§6.7) |
| D | `{ action: one of the eight (§7.7), target: group_id \| node_id \| none, stop_reason }` | action must be in the controlled set; target in `allowed_vocabulary` (§7.7) |
| E | the strict template JSON schema (§5.7), with citations per proposed dimension and a retrieval justification per level | §5.7 |

### 4. The verdict

One verdict record per claim. The **outcome vocabulary is uniform across all sites**; the
**disposition is site-specific** and names what the owning part does with it.

```text
Verdict {
  verdict_id, dossier_id, claim_ref
  outcome        : accept_direct | accept_context_supported | weak | reject | abstain
  disposition    : per-site, below
  reasons[]      : reason codes (below)
  may_propose    : bool     -- false forbids any folder proposal or asserted property (§3.6)
  requires_review: bool     -- true on every accept_context_supported (§4.8, §6.10)
  citations_checked[] : { citation_ref, resolved: bool, span_matched: bool }
  scope          : file | group | node | template | domain | corpus   (§8.7, supplied, never inferred)
  validator_version, policy_version, plan_version
}
```

- `accept_direct` — validated, resting on evidence marked `direct` in the dossier.
- `accept_context_supported` — validated, but resting on context rather than direct anchors. §4.8:
  *"records it as a context-supported membership and sends it to user review."* §6.10: *"may be valid
  but still require review."* Always `requires_review: true`.
- `weak` — non-contradicted but below the site's support bar. §3.6: *"useful but too weak to
  establish a fact may remain a possible clue for review; it must not quietly become a folder
  proposal or an asserted file property."* Enforced by `may_propose: false`, which is a **checkable
  invariant for P2**: no folder proposal, fact assertion, or move plan may reference a verdict whose
  `may_propose` is false.
- `reject` — a validation check failed; `reasons[]` says which.
- `abstain` — the model returned `unknown`, or the harness refused to call. §6.10: *"correct
  abstention is a successful outcome."* Abstention is reported separately from rejection in every
  P8-emitted metric and is never counted as a failure by P8.

**Outcome → disposition, per site:**

| Outcome | A — fact (§3.6, §3.13) | B — group (§4.8) | C — placement (§6.10, §6.11) | D — residual (§7.7, §7.9) |
|---|---|---|---|---|
| `accept_direct` | fact enters as reliability state **LLM-supported** | direct membership | eligible for a suggested or automatic move plan | `return_to_placement` if the action was "return to a confirmed domain group / accepted graph or purpose packet"; else the chosen residual destination |
| `accept_context_supported` | LLM-supported + review | **context-supported membership** → user review | valid, review required | residual destination + review |
| `weak` | **Possible** clue only; never a folder proposal | unresolved | unresolved (low margin, weak retrieval, generic hub) | `review_later` or `leave_in_place` |
| `reject` | **Rejected**; no fact | rejected or left unresolved | no destination | rejected; `return_to_placement` when the reason is `STRONGER_RELATIONSHIP_OVERLOOKED` |
| `abstain` | no fact, no clue | left unresolved | `abstain: no supported destination` (§6.11's own label) | `leave_in_place`, `review_later`, or abstain (§7.9) |

The D-row hand-back is the §7.9 loop the segmentation map cites as the reason P11 fuses §6 and §7:
*"the file should be returned to the standard node-aware placement engine rather than being trapped
in a generic residual folder."* A `return_to_placement` disposition re-enters at site C with a fresh
dossier; it is not a residual outcome.

`reject` + `STRONGER_RELATIONSHIP_OVERLOOKED` → `return_to_placement` is a **composition of §7.9's
two clauses** (the validator checks the model "did not overlook a stronger existing relationship";
§7.9 then says a credible connection goes back to §6). Flagged here so a reviewer can confirm the
composition rather than discover it.

### 5. The reason-code registry

Every check is a named code. The registry is the completeness test for the merge: if a check named
in §3.6, §4.8, §6.10, or §7.9 has no code, something was lost.

**Universal — run at every site:**

| Code | Outcome | Trace |
|---|---|---|
| `SCHEMA_INVALID` | reject | §3.5 (may not invent a schema), §5.7 (structured output enforcement) |
| `UNCITED_CLAIM` | reject | §4.5 — a decision needs a quote, field, relationship, or an explicit insufficiency statement |
| `CITATION_NOT_IN_DOSSIER` | reject | §4.5 closed world; §6.6 bounded dossier |
| `CITATION_NOT_FOUND` | reject | §4.8 — every cited span or metadata field exists in SQLite |
| `CITATION_SPAN_MISMATCH` | reject | §3.6 — the cited quote is actually present in the stored evidence |
| `CONTRADICTED_BY_STRONGER` | reject | §3.6, §4.8, §6.10 |
| `NOT_ELIGIBLE_FOR_MODEL` | abstain | §6.6, §8.6 — refused before issue |
| `PRIVACY_GATE_REFUSED` | abstain | §8.4 — the gate returned **`Denied`**; refused before issue |
| `BUDGET_EXHAUSTED` | abstain | §8.6 — refused before issue; never a downgraded call |
| `USER_REJECTED_EQUIVALENT` | abstain | §4.9 stop rule, §8.7 negative feedback — refused before issue |

**There is deliberately no code for `NeedsConsent`, and none may be added** (B2).
`PRIVACY_GATE_REFUSED` covers the gate's `Denied` branch and nothing else. A consent requirement is
not a validation outcome: it is a question returned to the caller and, through P13, to the user. The
registry is the completeness test for the merge, so the absence is recorded here rather than left to
be read as an omission — a code for consent would be the mechanism by which the §8.4 choice
disappears into an abstention.

**Site A adds (§3.3, §3.6):**

| Code | Outcome |
|---|---|
| `FIELD_NOT_IN_ACTIVE_SCHEMA` | reject |
| `VALUE_NOT_NORMALIZABLE` | reject |
| `SEARCH_HINT_ONLY` | weak — §3.3's *"appropriate for a proposal rather than merely a search hint"*; §3.6's possible-clue downgrade |

**Site B adds (§4.5, §4.8):**

| Code | Outcome |
|---|---|
| `TERM_MERGE_UNSUPPORTED` | reject — a course group does not merge different terms without evidence |
| `CONFLICTING_TARGET_INSTITUTION` | reject — an application packet does not silently absorb a conflicting target institution |
| `INVENTED_DATE` / `INVENTED_PROJECT` / `INVENTED_PURPOSE` / `INVENTED_MEMBERSHIP` | reject — §4.8's four |
| `LABEL_WITHOUT_COHERENCE` | reject — §4.5: a label only if coherence is supported |
| `FOLDER_HIERARCHY_PROPOSED` | reject — §4.5: the model must not create a final folder hierarchy |
| `CONTEXT_ONLY_SUPPORT` | accept_context_supported — §4.8's valid-but-context path |
| `GENERIC_SIMILARITY_ONLY` | reject/unresolved — §4.8: *"based only on generic similarity"* |

**Site C adds (§6.7, §6.10):**

| Code | Outcome |
|---|---|
| `NODE_NOT_IN_FROZEN_TREE` | reject |
| `INVENTED_DATE` / `INVENTED_INSTITUTION` / `INVENTED_PROJECT` / `INVENTED_NODE` | reject — §6.10's four |
| `SLOT_FILLED_WITHOUT_EVIDENCE` | reject — §6.7: never fill a missing slot because a complete-looking path is preferable; §6.10's invented-value clause. Fires when a path dimension has no direct or context citation |
| `CONFLICT_IGNORED` | reject — stronger conflicts were not ignored |
| `SENSITIVITY_POLICY_VIOLATION` | reject — a sensitive file is handled under the user's privacy policy |
| `BELOW_SUPPORT_THRESHOLD` | weak — two-condition rule, condition 1 |
| `INSUFFICIENT_MARGIN` | weak — two-condition rule, condition 2 |
| `GENERIC_HUB_ONLY` | weak — §6.10, §6.5 |

The **two-condition acceptance rule** (§6.10) is a single gate applied after all other checks pass:
the best legal destination must reach the minimum support threshold **and** exceed the next-best by
a meaningful margin. Failing either yields `weak` → unresolved, never `reject` — the claim was not
wrong, it was not strong enough. Both conditions are evaluated and both codes reported, so P2 can
tell a low-support case from a close-call case.

**Site D adds (§7.7, §7.9):**

| Code | Outcome |
|---|---|
| `ACTION_NOT_IN_CONTROLLED_SET` | reject — §7.7's eight actions |
| `DESTINATION_NOT_IN_FROZEN_TREE` | reject — §7.9 (same check as C's node check) |
| `EVIDENCE_NOT_IN_FILE_RECORD` | reject — §7.9 strengthens the universal citation check: the citation must resolve inside **this file's** record, not merely somewhere in the store |
| `SENSITIVITY_RESTRICTION_IGNORED` | reject — §7.9 |
| `STRONGER_RELATIONSHIP_OVERLOOKED` | reject → disposition `return_to_placement` — §7.9 |
| `INVENTED_FOLDER` | reject — §7.8: must not invent `Travel/Flight Gate B12` |

### 6. The grounding report — §8.5's measurement

Emitted per call, in the shape §8.5's LLM-grounding row asks for:

```text
GroundingReport {
  dossier_id, call_site, model_id, prompt_fingerprint, validator_version
  citations_total, citations_resolved, citations_span_matched
  claims_total, claims_abstained, claims_accepted_direct,
  claims_accepted_context, claims_weak, claims_rejected
  reasons_histogram   : reason_code -> count
  reduction_rung      : none | summarized_facts | preserved_anchors | split | deferred   (§8.6)
  release_audit_id      P7's `audit_id` for this release                                  (§8.4)
  dossier_builder     : which stage produced this dossier                                (§4.8)
}
```

- *"Did every cited excerpt exist?"* → `citations_resolved ∧ citations_span_matched / citations_total`.
- *"Did the model return `unknown` when evidence was insufficient?"* → `claims_abstained` against
  P2's per-item expectation. P8 supplies the observation; P2 owns the expectation format.
- `dossier_builder` exists because §4.8 requires that *"a bad group can fail because the graph
  retrieved irrelevant neighbors, because the LLM overgeneralized… or because the candidate label
  was simply not useful"* be logged as **separate** failure points. P8 owns only the middle one; the
  tag is what lets P2 attribute the other two elsewhere.

**Replayability.** P8 persists, per call: the released dossier's content address, `prompt_fingerprint`,
`model_id`, the raw response bytes, and every verdict. P2 can therefore re-run validation without
re-calling a model, which is what makes shadow mode (§8.5) affordable.

**P2's envelope (B7).** P8 emits P2 `stage_output` with `stage_id = llm_interpretation` — stage 5 of
§8.5's closed ten, and the only stage P8 owns. `P8` is **not** a member of that enumeration and must
never appear in the field. Each output carries `inputs[]`, an explicit abstention value, a distinct
budget-deferral value, and P2's live seven-field version tuple `(extractor_versions,
graph_algorithm_version, prompt_fingerprint, model_identifier, template_library_version,
placement_scorer_version, analysis_tiers_enabled)`. `validator_version` and `policy_version` remain
inside P8's opaque payload and verdict/report records; they are not P2 version-tuple axes.

**P8's result → the envelope's vocabulary.** `stage_output.outcome` is P2's five-value enumeration,
**not** P8's five-value `Verdict.outcome`. They are different vocabularies and this table is the only
mapping between them:

| P8 result | `stage_output.outcome` | `budget_state` |
|---|---|---|
| a verdict was issued — `accept_direct`, `accept_context_supported`, `weak` or `reject` | `produced` | `within_ceiling` |
| `abstain` because the model returned `unknown`, or `abstain` with `NOT_ELIGIBLE_FOR_MODEL`, `PRIVACY_GATE_REFUSED` or `USER_REJECTED_EQUIVALENT` | `abstained` | `within_ceiling` |
| `abstain` with `BUDGET_EXHAUSTED` — an §8.6 ceiling stopped the call after the reduction ladder was exhausted | `deferred` | `ceiling_reached` |
| the stage failed | `error` | — |
| P8 not built yet | `not_implemented` | — |

The third row is the reason the table exists. `BUDGET_EXHAUSTED` is a P8 `abstain` but a P2
`deferred`: mapping it to `abstained` would have P2 score it as a correct or incorrect abstention,
and P2's Done-means 6 — a run whose only change is a lower budget ceiling produces zero new
divergences — would be unsatisfiable. `ceiling_reached` appears on that row and on no other.

`NeedsConsent` produces **no** `stage_output` at all: P8 issued no call and refused none (B2, and
[§7](#7-the-single-egress-point) above). It is not an `abstained` row, for the same reason it is not
an outcome and not a reason code.

**Cached responses are re-validated, never re-used blind.** §3.4's cache key covers content hash,
extractor version, tier, model id, and prompt fingerprint — it does **not** cover the evidence
snapshot, and §8.2 allows a later extractor to supersede an earlier observation. A cached response
whose citations now point at superseded evidence must re-validate against the current snapshot
before use.

### 7. The single egress point

**How a model call that has not passed the §8.4 gate is made impossible:**

1. P8 exposes exactly one function that speaks to a model, and its only parameter is a P7
   `Released`. P8 cannot construct a `Released`; only `Gate.release` returns one, and it returns one
   only on the `Released` branch.
2. P8 never resolves an evidence reference into content on the request path. It builds a
   reference-only `ModelCallRequest` and hands it to P7. Content first exists inside the gate. There
   is no P8 code path where un-gated content and the model client are both in scope.
3. Releases are single-use and bound to `(model_target, prompt_fingerprint, policy_version)` (B2). A
   retry, a re-issue after a schema failure, a reduction under §8.6's ladder, or a switch of model
   target requires a **new** release and therefore a new gate decision and a new audit record.
4. P8 reads the evidence store directly **only after** a response returns, for validation. Validation
   is a local comparison and performs no egress.
5. Every call event records P7's `audit_id` (§8.4's consent-aware audit record: what policy
   authorized the call, sensitivity, excerpts included, redactions, which model, prompt fingerprint).
6. **The other two branches never become a call.** `Denied` becomes a `Refusal`, and `NeedsConsent`
   is handed back to the caller unchanged for P13 to surface. Neither branch yields a value the
   transport accepts, so neither can be coerced into a call by a caller that would rather proceed —
   and `NeedsConsent` in particular has no representation in P8's outcome vocabulary at all, so there
   is no value P8 could downgrade it into (B2).

This is structural, not procedural: the enforcement is that the un-released call cannot be expressed,
not that a reviewer remembers to check. The consent guarantee is structural in the same way: the
degradation `NeedsConsent → abstain` is unavailable because `NeedsConsent` is not an outcome, is not
a reason code, and is not a refusal — it is a return to the caller.

**Consequence for validation.** If P7 redacts an excerpt, the model's cited span is the redacted
text while the stored evidence holds the raw text. `CITATION_SPAN_MISMATCH` therefore compares the
cited span against **the released dossier's excerpt — what the model actually saw** — while
`CITATION_NOT_FOUND` resolves the reference against the store. The release must survive for the
lifetime of validation. Ownership of the reverse mapping is [Q4](#open-questions).

### 8. Events appended (§8.2)

`model_call_issued` · `model_response_received` · `validation_verdict` · `verdict_superseded` ·
`call_refused` (carrying the refusal reason code).

**Registration (B5).** These five are **declared here as P8's event types** under P1's registration
rule: each part declares its types in its own SPEC, P1 validates against the union of the
declarations, and §8.2's nineteen names are reserved and may not be redefined by any part. None of
the five collides with the nineteen. §8.2 introduces its list with *"This includes"*, so nineteen is
a floor rather than a ceiling. P7's `consent_requested` — not one of P8's — is the event that records
a `NeedsConsent`; P8 appends nothing for that branch, because P8 neither issued a call nor refused
one.

P8 appends **only** these. The domain events §8.2 lists — fact creation, fact rejection, group
membership proposal, placement recommendation — are appended by their owning parts, each referencing
a `verdict_id`.

### 9. Fixtures published for neighbours

So P6/P9/P10/P11 can be built before P8 exists: for each site, a dossier fixture, a set of recorded
response fixtures (one per reason code plus the accept and abstain paths), and the expected verdict
for each. A neighbour builds against recorded responses and the verdict shape, with no model in the
loop.

---

## Deferred — manual design required

Everything here is hand-authored content that P8's machinery consumes but does not define. Nothing
below is invented in this spec.

| Deferred | Defined by | Why P8 does not author it |
|---|---|---|
| **All prompt text, every site** | §3.3, §4.5, §6.6, §7.7, §5.7 describe what is asked; the wording is hand-authored | P8 owns the response *schema* and the dossier *shape*, not the words. Prompt text changes the `prompt_fingerprint` (§3.4) and is versioned with it |
| **The 200–300 template library** | §5.7 | Site E's target vocabulary and the built-in comparison set. §5.7 itself says the product begins with core domains and expands |
| **Domain fact-schema fields beyond §3.11's literal table** | §3.11, P6 | Site A's `FIELD_NOT_IN_ACTIVE_SCHEMA` needs the schema. §3.11 states six domains and their fields literally; §3.11 also anticipates "many specialized fields" later. P8 takes the schema as input |
| **Gazetteer contents** | §3.7, P6 | Feeds `VALUE_NOT_NORMALIZABLE` |
| **Residual library contents beyond §7.3's nine names** | §7.3, §7.4 | Site D's `allowed_vocabulary`. The nine are named; user-defined residual areas (§7.3) are per-corpus |
| **Threshold and margin *values* for §6.10's two conditions** | §6.10 states the rule, no values | Calibration against §8.5's adversarial suite, not a design decision. The *definition* of the support quantity is [Q2](#open-questions), which is different |
| **The `contradicts()` and normalization predicates' domain logic** | §3.6, §3.7, P6 | P8 calls them; P6 defines what contradiction means per field |
| **The hand-labelled reference corpus behind §8.5's suite** | §8.5, P2 | Only the corpus is deferred. The twelve adversarial cases §8.5 names are authored by P2 and are not deferred; what nobody has authored yet is the hand-labelled corpus of expected facts and expected placement or abstention outcomes. P8 must pass the suite either way |

---

## Done means

Falsifiable, in the order a reviewer would check them:

1. **One egress.** Exactly one function in the codebase constructs a model request, and its only
   parameter type is P7's `Released`. A call without a release is not constructible. Verified by
   inspection plus a test that the un-released path does not type-check / does not exist.
2. **Reason-code coverage.** Every code in the registry has at least one fixture: a dossier plus a
   hand-written response that triggers exactly that code and no other. A code with no fixture is an
   unimplemented check.
3. **Hallucinated citation is rejected.** A response citing a real `evidence_ref` with an altered
   span yields `reject` / `CITATION_SPAN_MISMATCH`. This is the minimum adversarial bar; if it
   passes, the grounding metric is meaningless.
4. **Uncited claim is rejected, not softened.** A claim with no citation and no `unknown` yields
   `reject` / `UNCITED_CLAIM` — never an accept with a lower confidence.
5. **`unknown` validates to `abstain` at all five sites**, never to `reject`, and is excluded from
   every failure count P8 emits (§6.10).
6. **`may_propose: false` holds.** Replay asserts that no folder proposal, asserted file property, or
   move-plan entry references a verdict with `may_propose: false` (§3.6).
7. **Two-condition rule.** A candidate above threshold but within the margin of the next-best yields
   `weak` / `INSUFFICIENT_MARGIN` → unresolved, not a placement (§6.10).
8. **Hand-back works.** A site-D response choosing "return to a confirmed domain group" with valid
   citations produces disposition `return_to_placement`, and P11's fixture shows the file re-entering
   at site C rather than landing in a residual folder (§7.9).
9. **Determinism.** Every fixture validated twice, in two processes, yields byte-identical verdicts.
10. **Refusals are abstentions, not guesses.** A gate `Denied`, budget exhaustion, ineligibility, and
    already-rejected-equivalent each produce `abstain` with their specific code, with no model call
    issued and no lower-quality substitute (§8.4, §8.6). `NeedsConsent` is **not** in this list and
    must not be added to it.
11. **Grounding report emitted on every call**, including refused calls, with the fields §8.5 names.
12. **A neighbour builds against it.** P9 or P11 can complete its own done-means using only P8's
    fixtures, with no model configured.
13. **Consent cannot degrade to abstention** (B2, §8.4). Fed P7's `NeedsConsent` fixture, P8 returns
    the requirement and all four options — local model, cloud model, redacted prompt, no model use —
    to its caller; emits no verdict, no `abstain`, no reason code, and no `call_refused` event; and
    issues no model call. Falsifiable two ways: grep the outcome vocabulary and the reason-code
    registry for any consent value (there must be none), and replay the fixture asserting the caller
    received a consent branch and P13 was handed the four options. A build in which `NeedsConsent`
    reaches a metric as an abstention fails this item even if every other item passes.

---

## Cross-cutting answers

### Provenance (§8.2)

**Appends:** `model_call_issued`, `model_response_received`, `validation_verdict`,
`verdict_superseded`, `call_refused`. Each carries the §8.2 event fields, and P8 is the part that
supplies the two §8.2 names specifically for model work — **model version** and **prompt
fingerprint** — on every one of them, alongside `validator_version`, `policy_version`, and P7's
`audit_id` (B2 — the field is P7's `audit_id`, not a P8-local name for it).

**Never overwrites.** A re-run under a new model, prompt, or validator version **supersedes**; the
prior response bytes and prior verdict remain, with the reason for supersession recorded. §8.2's
worked example is OCR — *"if a first OCR pass produces unreadable text and a later improved OCR
engine recovers a university name, both extraction records should remain available"* — and the same
rule applies to model output: a better model's answer does not erase the answer a user may have
already reviewed. The resolver may mark the newer verdict preferred; the older stays inspectable.

P8 also never overwrites the evidence it validates against. Validation is read-only over the evidence
store; the only writes are P8's own event records.

**Publishes for §3.4:** `prompt_fingerprint` and `model_id`. The fingerprint must change whenever
anything shaping the model's input changes — prompt template, response schema, call-site version,
dossier assembly version. `validator_version` and `policy_version` are recorded **separately**,
because a validator change must invalidate a cached *verdict* without invalidating the cached
*response*: the response is still what the model said, and re-validating it is free.

### Budgets and degradation (§8.6)

**Ceilings P8 owns**, from §8.6's list: `Maximum LLM calls per thousand files` · `Maximum model cost
per scan` · `Maximum dossier tokens per model call`.

The first two are P8's because P8 is the **single egress point** — the only place a call exists to be
counted and the only place a cost is incurred, so it is the only place either ceiling can be enforced
rather than estimated (O9). Every other part **consumes** them: a part may read the remaining budget
to decide whether to build a dossier at all, and must not keep its own count or enforce its own
limit, because a per-part count of a shared ceiling is a count of the wrong thing.

**`Maximum dossier tokens per model call` — the split, stated in both specs (M9). P8 measures the
dossier against the ceiling *before* it calls the gate, and runs the ladder below at that point.**
P7 retains `dossier_over_budget` as a **backstop denial that should never fire**. The measurement has
to happen pre-release because that is the last moment the dossier can still be reduced: a gate-only
check runs after reduction is possible, so the ladder would never execute and every over-budget
dossier would become a denial instead of a summarize, split, or defer. Reaching P7's
`dossier_over_budget` through the normal path is therefore a **P8 defect**, not a gate result, and
P7 publishes a fixture for it precisely so P8 can prove its ladder ran first.

**Ceilings P8 consumes but does not own** (they bound the dossier before it arrives): maximum
retrieved neighbors per target file, maximum local graph neighborhood size, maximum candidate cluster
size, maximum residual files in one review batch. P8 rejects an over-budget dossier back to its
builder rather than trimming it silently.

**Over-token behaviour is a declared ladder, in §8.6's own order**, and the rung used is recorded on
the grounding report:

```text
1  summarize deterministic facts
2  preserve anchor excerpts        (anchors are never the thing dropped)
3  split the task
4  defer the decision
```

P8 is the part that runs them (M9); the gate neither reduces nor truncates.

§8.6: *"A model prompt that exceeds its token budget should not truncate silently in a way that
removes the decisive evidence."* Silent truncation is not an available rung. Because the release binds
the dossier, a reduction produces a **new** `ModelCallRequest` and therefore a new release — a reduced
dossier cannot be sent under a release granted for the full one. Each rung is a fresh gate decision
and a fresh audit record, so the ladder is visible in the audit log rather than hidden inside P8.

**On exhaustion:** the harness refuses the call and returns `abstain` / `BUDGET_EXHAUSTED`, the item
stays in review, and extracted evidence is retained with the stage marked deferred. §8.6:
*"Cost exhaustion must never turn into lower-quality automatic classification."* Concretely, P8
**never** substitutes a cheaper or weaker model on budget exhaustion. Routing to a local model is a
user policy choice under §8.4's modes, never an automatic budget fallback.

**Refusal is visible.** §8.6 requires the interface to distinguish completed from deferred work, so
every refusal is a first-class recorded outcome with a code — never a silent skip that reads
downstream as "nothing to say about this file."

### Correction learning (§8.7)

**What P8 records:** P8 records no user action directly — corrections are made against facts (P6),
groups (P9), nodes (P10), and placements (P11). What P8 owes §8.7 is the other half of its
requirement: *"Rejected groups, rejected destination matches, rejected labels, and rejected residual
recommendations must be stored with the evidence that produced them."*

The evidence that produced them **is** the dossier, the response, and the verdict. P8 therefore makes
every verdict durably addressable by `verdict_id` for the life of the corpus, so any downstream
rejection attaches to the exact model input and output that caused it. A rejection whose cause cannot
be retrieved will, in §8.7's words, *"repeatedly resurface the same attractive but incorrect
grouping."*

**Pre-call suppression.** §4.9's stop rule — *"the user has already rejected an equivalent
proposal"* — is enforced at P8's boundary. Before `Gate.release`, P8 queries P1
`learning_records(scope, subject_id)` for the call site's `proposal_class` and `basis_key`
([`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)). An unresected reject with a matching
pair is refused (`abstain` / `USER_REJECTED_EQUIVALENT`) rather than re-issued. Equivalence is that
pair, not dossier bytes — a trivial dossier edit must not resurface the same claim, and a different
`basis_key` must not be suppressed. `NeedsConsent` is still not an abstention (B2).

**Scope discipline.** §8.7's six scopes — file / group / node / template / domain / corpus — appear
on every verdict, **supplied by the owning part and never inferred or widened by P8**. §8.7's own
example is the constraint: a user saying one particular transcript belongs in a Columbia packet must
not teach the engine that all transcripts do. P8 widening a scope would be exactly that failure.

### Plan versioning (§8.8)

§8.8: *"The evidence database remains shared across plan versions, but the destination tree and user
policy define which projections are valid in each version."* P8's state splits along that line:

| Shared evidence database | Plan-versioned |
|---|---|
| Site A dossiers, responses, verdicts — claims about a file, not about a plan (§3.14: facts are separate from the destination tree) | Site C and site D dossiers, responses, verdicts — they cite frozen-tree node IDs and the residual/privacy/placement policies §8.8 lists in a plan version |
| Site B dossiers, responses, verdicts — computations over corpus evidence | Site E template verdicts — §8.8's plan version captures template versions and ordering choices |
| Response bytes and grounding reports for all sites — audit material, never re-scoped | The *acceptance* derived from a B verdict — §8.8 lists "accepted and rejected group memberships" in the plan version. P9/P10 own that split; P8 keeps the verdict shared and the acceptance out of its own state |

**A new plan never silently reclassifies.** §8.8 is explicit, and P8's rule is that a site-C/D verdict
from an earlier plan version **never migrates** into a new one. On plan change, every such verdict is
re-validated against the new frozen tree, which is free because validation is deterministic and
model-free:

- every cited node still exists → the verdict stands, re-stamped with the new `plan_version`;
- a cited node is gone → `reject` / `NODE_NOT_IN_FROZEN_TREE`, and the item returns to review. This
  is the mechanism behind §8.8's *"twenty-three files now require renewed review because their
  previous destination no longer exists."*

`policy_version` is recorded on every verdict for the same reason: a verdict validated under one
privacy or placement policy is not evidence of compliance with a different one.

---

## Open questions

Settled since the contract review, by [`../../04-resolutions.md`](../../04-resolutions.md) — recorded
here so nothing is re-adjudicated: the gate's signature, return union and binding tuple, and the rule
that `NeedsConsent` returns to the caller and never becomes an abstention (B2); whether P8 may declare
event types outside §8.2's nineteen — yes, by registration (B5); which identifier `evidence_ref` names
(M14 — `observation_key`); §2.8's context field split (M5 — P4's three fields); who measures the
dossier-token ceiling and runs §8.6's ladder (M9 — P8, pre-release, with P7 backstopping); and who
owns the call-count and cost ceilings (O9 — P8, as the single egress point).

Settled since, by [`../../05-minor-resolutions.md`](../../05-minor-resolutions.md): **site E's
validation boundary** — the former Q9, now closed as P8 proposed it. **P10** runs §5.7's six
semantic checks over the generated template (no repeated parent dimension, no meaningless one-child
level, depth limit, no author-or-organization-as-collector, no protected-information exposure, no
empty branches when tested against the accepted group), because §5.7 puts them on the engine that
validates against the accepted group, which is P10's freeze-time job. **P8** enforces the strict
JSON-schema conformance §5.7 requires of the generated template, and with it the citation and
no-invented-facts checks §5.7 states in the same breath — *"cite the file facts that justify each
proposed dimension"*, *"cannot invent unsupported facts"* — which are P8's grounding job at every
other site and are not among the six.

Each of the nine below names the part whose contract it threatens. None is answered here.

1. **Model selection.** The design names no model anywhere. Open: which model serves each call site,
   whether one model serves all five, and whether §8.4's local-model mode requires a different
   response schema because structured-output support differs between local and cloud models. *Threatens:
   P7 (releases bind a model target), P2 (grounding is comparable across models only if the schema
   is).*
2. **What "support" is measured in.** §6.10 requires a *"minimum support threshold"* and a
   *"meaningful margin"* but never defines the quantity being thresholded. §3.13 permits internal
   numeric scores without specifying them; §3.7 states an analogous score-and-margin rule for
   deterministic facet extraction. Open: is placement support a deterministic score from P11, a
   model-reported confidence, a count of independent direct citations, or a composite? A
   model-reported confidence would make the two-condition rule a model self-report, which sits badly
   with §4.8's *deterministic* validator. *Threatens: P11, P2.*
3. **Does the two-condition rule apply beyond site C?** §6.10 states it for placement only. §3.7
   states a score-and-margin rule for facet extraction (P6's deterministic path, not P8's). The design
   is silent on whether group membership (B) and residual destination choice (D) get a margin
   requirement. *Threatens: P9, P11.*
4. **Redaction reverse-mapping ownership.** When P7 redacts an excerpt, something must map a cited
   span in redacted text back to the stored raw evidence so both `CITATION_SPAN_MISMATCH` and
   `CITATION_NOT_FOUND` can be evaluated. §8.4 requires redaction; §8.5 requires the excerpt-existence
   check; neither says who holds the map or how long it lives. *Threatens: P7.*
5. ~~**What makes a proposal "equivalent" to one the user already rejected?**~~ **Settled — I4/learning
   resolution.** Same `proposal_class` + `basis_key`, queried from P1 `learning_records` before
   `Gate.release`. Not dossier bytes, not member-set, not display label. See Pre-call suppression and
   [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md).
6. **May a `weak` output re-enter a later dossier as evidence?** §3.6 forbids a possible-clue becoming
   a folder proposal or an asserted property, and §3.13 keeps `Possible` as a real state, but the
   design does not say whether a model may later *see* one. Including them risks a model confirming
   its own earlier guess; excluding them discards §3.9's session clues and §4.2's semantic neighbours.
   *Threatens: P9, P11 (dossier composition).*
7. **Must conflicting evidence always be shown to the model?** §4.4 puts conflicts in the group
   dossier and §6.6 puts known conflicts in the placement dossier, so the answer is yes at B and C. The
   design is silent at A and D. If conflicts are omitted at A, `CONTRADICTED_BY_STRONGER` becomes a
   post-hoc rejection of a model that was never shown the contradiction — measurable as a grounding
   failure that is really a dossier-construction failure. *Threatens: P6, P11, and §8.5's failure
   attribution.*
8. **Retry on `SCHEMA_INVALID`.** The design does not say whether an unparseable or non-conforming
   response may be re-requested. Open: is a retry permitted, does it consume a new release (P8's answer
   is yes — releases are single-use), does it count against §8.6's call budget, and does the discarded
   response count in §8.5's grounding denominator? *Threatens: P2 (metric definition), P11 (budget
   accounting).*
9. **Batch granularity at site D.** §7.7 permits a dossier covering *"a small homogeneous batch."*
   Open: does one response carry per-file claims, does a single schema violation void the whole batch
   or only the offending claim, and does the batch count as one call or N against §8.6's
   calls-per-thousand-files ceiling? *Threatens: P11, P2.*
