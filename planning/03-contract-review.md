# Contract review — twelve parallel specs

Date: 2026-08-19
Reviewed: 12 `SPEC.md` against `02-segmentation-map.md`, `01-product-design-structured.md`, `00-database-agent-product-design.md` (source of truth)
Verdict: **Do not freeze.** The specs are individually strong and unusually disciplined about deferral, but eight seams are wired to incompatible contracts — most severely P4↔P5 (two extraction-outcome vocabularies), P7↔P8 (two different gate signatures), and the node→path chain (P10/P11/P12, where all three assume someone else resolves a node to a filesystem path).

---

## Summary

| Severity | Count |
|---|---|
| BLOCKING | 8 |
| MAJOR | 15 |
| MINOR | 12 |
| Coverage gaps | 14 |
| Overlaps | 12 |
| Deduplicated open questions | 48 (from 143 raw entries) |

**The three things that most need attention:**

1. **P4 and P5 published two different extraction-outcome records.** P4's `extraction_runs.completeness` is `complete | capped | partial | deferred | unsupported | unreadable | failed`, one row per *(file version × extractor)*. P5's router status is `extracted | extracted_empty | partially_inspected | unreadable | unsupported | metadata_only | deferred`, one row per *file*. Three values overlap. `metadata_only` has no P4 home, `failed` has no P5 home, and P5's single record cannot represent an image that ran through both E5 and E6. Every §8.6 user-facing count and P2's adversarial case A9 depend on this record. Six extractors are about to be written against the wrong one.

2. **P7 and P8 describe the same gate with different signatures, and P8 has no path for the consent case.** P7 publishes `Gate.release(ModelCallRequest) -> Released | Denied | NeedsConsent`. P8 requires `seal(dossier_request, call_site, model_target, policy_version) -> SealedDossier | Refusal`. P8 has no `NeedsConsent` branch at all — so §8.4's requirement that "the user should see that requirement and choose whether to allow a local model, a cloud model, a redacted prompt, or no model use" silently degrades to an abstention. The bindings also differ: P7 binds a release to `(model_target, prompt_fingerprint, audit_id)`, P8 binds a seal to `(call_site, model_target, policy_version)`. This is the one seam the segmentation map re-ordered the whole project to protect.

3. **Nobody resolves a destination node to a filesystem path.** P10 states "the tree is addressed by ID, never by path string" and gives a path field only for `node_type = existing`. P11 says "P12 resolves the node to a filesystem path." P12 says it "requires a resolved path for every node it is asked to write into" and that residual paths "must be supplied at tree design, never by P12." All three point at each other. The walking skeleton's final step (`P12 plan → move → undo`) cannot run.

---

## BLOCKING — must resolve before contracts freeze

### B1. Two incompatible extraction-outcome records (P4 ↔ P5, §2.4/§2.5/§2.7/§2.9/§8.6)

- **P4** (`Record 2 — extraction_runs`, D5): "One row per (file version × extractor)", `completeness ∈ complete | capped | partial | deferred | unsupported | unreadable | failed`, plus `coverage {units, processed, total}`.
- **P5** (`R — the router`): "Every file leaves the router with exactly one **extraction outcome record**", status `∈ extracted | extracted_empty | partially_inspected | unreadable | unsupported | metadata_only | deferred`.

Why it is a problem: only `deferred`, `unsupported`, `unreadable` are shared. P4 splits P5's `partially_inspected` into two distinct states (`capped` for a ceiling, `partial` for mixed readability) — §2.5 and §2.7 do require both. P5's `metadata_only` (§2.9's safe default for disk images, executables, encrypted containers) has no P4 value. P4's `failed` (§2.4: "an error is not an empty document") has no P5 value. And the cardinality differs: an opaque image runs E5 *and* E6, which is two P4 runs but one P5 outcome record — so P5 cannot express "EXIF read successfully, OCR capped." §8.6's sentence *"1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred after the OCR limit… 18 files remain unreadable"* is computed from this record by both specs, from different vocabularies. P2's adversarial case A9 names a third word again ("stage marked deferred") for what P5 calls `partially_inspected` and P4 calls `capped`.

Recommended resolution: **P4's `extraction_runs` wins** — it is per-extractor, carries `coverage`, and §2.7 requires provider/config/completeness which P5's record does not hold. Add `metadata_only` to P4's `completeness` (§2.9 requires it) and delete P5's parallel status vocabulary, keeping P5's router table (format → extractor) which P4 explicitly defers to P5. Restate P5's §8.6 counting rules against P4's values.

### B2. Two gate signatures, and P8 cannot express consent (P7 ↔ P8, §8.4)

- **P7** §6: `Gate.release(ModelCallRequest) -> ReleaseDecision`, `ReleaseDecision = Released | Denied | NeedsConsent`; `Released { release_id, audit_id, materialised_items[], redaction_manifest[], model_target }`; bound to `(model_target, prompt_fingerprint, audit_id)`.
- **P8** Contract in: `seal(dossier_request, call_site, model_target, policy_version) -> SealedDossier { content, redaction_map_ref, audit_record_id, policy_version, model_target, prompt_fingerprint_binding, single_use_token } | Refusal`; bound to `(call_site, model_target, policy_version)`.

Why it is a problem: different function name, different parameters, different return union, different field names for the same values, different binding tuple. Worse, `NeedsConsent` has no representation on P8's side; P8's only non-success is `Refusal`, which it maps to `abstain / PRIVACY_GATE_REFUSED`. §8.4 requires the *user* to be offered four options at that moment; under P8's contract that requirement disappears into an abstention. The segmentation map orders P7 before P8 *specifically* so this seam is exact, and it is the one seam where a mismatch is a privacy failure rather than a bug.

Recommended resolution: adopt **P7's** shape verbatim (it is the owner of §8.4 and its three-way return is the one §8.4 requires). Rename P8's `seal` to `Gate.release`, add a `NeedsConsent` branch that returns control to the calling part rather than abstaining, and reconcile the binding tuple — bind on `(model_target, prompt_fingerprint, policy_version)`; `call_site` is already inside `prompt_fingerprint` per P8's own fingerprint rule.

### B3. Node → filesystem path has no owner (P10 ↔ P11 ↔ P12, §5.12, §6.11, §8.3)

- **P10** node record: `node_id` — "the tree is addressed by ID, never by path string"; `existing_path` — "present only when `node_type = existing`."
- **P11** Contract out §5: "P12 resolves the node to a filesystem path, applies collision and normalization policy, and owns the transaction."
- **P12** Contract in from P10: "the node's **materialized filesystem path** … P12 requires a resolved path for every node it is asked to write into; five of the nine §7.3 residual templates carry no default location, so their paths must be supplied at tree design (§7.4), **never by P12**."

Why it is a problem: §8.3's plan record has both "Requested destination node" and "Resolved destination path" as separate fields, so the resolution step exists in the design and is unassigned. `proposed` and `user-created` nodes — which are most of the tree — have no path anywhere. P12's own Open question 5 ("Directory creation and its reversal") is downstream of this and cannot be answered either. The skeleton's P12 step is unrunnable.

Recommended resolution: assign path resolution to **P12**, since §8.3 gives P12 the filesystem-safety normalization, case-sensitivity, Unicode-form and length rules that any path resolution must obey, and P10 must not hold platform-specific strings inside a plan-versioned tree. P10 supplies `root_anchor` + the ancestor `display_label` chain (it already publishes both); P12 composes and normalizes. Remove P12's "supplied at tree design" clause and P11's "P12 resolves" clause becomes correct as written.

### B4. Destination profile is in two Contract-outs (P10 ↔ P11, §6.1/§6.2)

- **02-segmentation-map.md**, P10 row: *Publishes* — "**the frozen tree** — node types **and destination profiles**".
- **P10** Contract out §2: "P10 **emits the profile**; P11 **builds the retrieval index over it**." Done-means #1 lists the profile among "the five artefacts".
- **P11** Contract out §2: "The destination profile (§6.1) and retrieval index entry (§6.2) — **Built by P11** from each frozen node, after freeze." P11's Contract-in from P10 never mentions receiving a profile.

Why it is a problem: two full field tables for the same record, in two Contract-outs, with different field lists (P10 has `known_exclusions[]`, `user_edits[]`, `restrictions`; P11 restates §6.1's prose list). P11's plan-versioning answer also claims "all destination profiles and the whole retrieval index" as P11 plan-version state, while P10 claims the profile as its own artefact.

Recommended resolution: **P10 owns the profile** — the segmentation map says so in its own words, and §6.1's contents (template, expected values, accepted groups, user-selected label, privacy restrictions) are all P10-held. P11 owns only the retrieval index (§6.2), which P10 already concedes. Delete P11's Contract out §2 profile table and add the profile to P11's Contract in from P10.

### B5. Three parts invented event types against P1's frozen nineteen (P1 ↔ P7/P8/P11, §8.2)

- **P1**: "§8.2 introduces this list with 'This includes', so nineteen is a **floor, not a ceiling**. P1 freezes these nineteen as the contract minimum; **adding a type is an amendment to this spec, not a local decision by a consuming part**."
- **P7** appends: `classification_assigned`, `classification_superseded`, `policy_set`, `consent_granted`, `consent_revoked`, `model_release`, `model_release_denied`, `consent_requested` — **eight, none in the nineteen**.
- **P8** appends: `model_call_issued`, `model_response_received`, `validation_verdict`, `verdict_superseded`, `call_refused` — **five, none in the nineteen**.
- **P11** appends eight prose-named events ("destination profile built for a node", "candidate destination retrieval performed", "residual set surfaced", …), describing them as "this part's specializations" of `placement recommendation`.

Why it is a problem: P1's writer validates "event type in the published vocabulary" (Contract in), so as written P1 would reject every P7 and P8 event. Twenty-one new types is not an edge case — it is a third of the log. P1's own Open question 5 asks whether §8.4's audit record is even the same log; P7 answered *yes* ("`model_release` and its consent-aware audit record are the same event") without P1 agreeing.

Recommended resolution: P1 opens the vocabulary formally, with a registration rule: each part declares its types in its SPEC, P1 validates against the union, and the nineteen §8.2 names are reserved. Separately, settle P1 OQ5 now — P7's answer (one log) is the right one and should be adopted, since §8.2 already carries `prompt fingerprint` on the event record.

### B6. P11 does not consume P10's legality flag (P10 → P11, §5.12, §6.2, §6.10)

- **P10**: "the set of legal destinations is exactly `{node_id : plan_version = frozen version, accepts_placement = true}`", where `ignored` nodes are `false` and `protected` nodes are `true` only under an explicit automatic-move policy.
- **P11** Contract in from P10 lists: `node_id`, node type, display label, parent, associated groups, template context, explanation, residual-template identity and §7.4 mode. **`accepts_placement` is absent.** P11's Done-means #2 tests only that "a record naming an unknown node fails validation."

Why it is a problem: `accepts_placement` is the single field P10 built to keep P11 from placing into an `ignored` node — §5.10's guarantee that a user may leave an existing folder untouched. P11 as specified would place into it. The same gap loses §8.4's protected-node rule at the placement layer, which P7 also expects P11 to consume rather than re-derive.

Recommended resolution: add `accepts_placement`, `node_role`, `disposition`, `expected_values[]` and `handling_class` to P11's Contract in, and change P11 Done-means #2 to test `accepts_placement = true` as well as node existence.

### B7. P2's four obligations on measured parts are accepted by none of them (P2 ↔ P5/P6/P8/P9/P10/P11, §8.5)

**P2** Contract in §B: "These four are the whole reason P2 is ordered early. A part that does not satisfy them cannot be measured per-stage afterwards without rewriting its boundaries" — emit a `stage_output` envelope; record abstention as an explicit value; record budget deferral distinctly; stamp the version tuple. Plus a fifth: carry `inputs[]`.

Verified by grep: the strings `stage_output`, `version_tuple`, `not_implemented` and `budget_state` appear **only in P2's own spec**. No measured part's Contract out includes the envelope.

Why it is a problem: this is the exact failure the segmentation map moved P2 to Wave 1 to prevent ("Retrofitting per-stage measurement means rewriting every stage's boundaries"). Obligation 2 is already violated in substance by P6: §3.6 failures produce "no fact" — a missing row — which P2 says it cannot distinguish from a crash or a skip. P11's `outcome = abstain`, P9's `coherence_verdict = abstained` and P8's `abstain` do satisfy it, but by coincidence rather than contract.

Recommended resolution: add a one-line "Emits P2 `stage_output` with `stage_id = …`" clause to the Contract out of P5, P6, P8, P9, P10 and P11, and give P6 an explicit abstention row (a `file_facts` row with state `possible` or a dedicated `unresolved` marker) rather than an absence.

### B8. The walking skeleton's fact assertion cannot pass as specified (P4 ↔ P6 ↔ 02, §3.5, §6.10)

Two independent breaks in the one path that is supposed to prove the seams connect.

**(a) The fact.** The map's skeleton: "`P6` resolve it to ONE validated fact (course = X) with its evidence link". P4 nominates fixture 1 for this and asserts in Done-means #9: "P6 resolves `course = BUSIB 4300` from fixture 1 with no extractor present." Fixture 1 is `heading:page=1/heading=2`, `raw_value: "BUSIB 4300"`, with `context_before: "Course code: "` and `context_after: " — Spring 2026"`. But P6's Done-means #8, quoting §3.5 literally: "A course-code-shaped string with **no academic context term** in its surrounding context produces no course fact" — the required terms being "syllabus", "lecture", "credits", "instructor", or "semester". Fixture 1 carries none. P6 must refuse it, and correctly so.

**(b) The two-condition rule.** §6.10 requires *every* proposed destination to clear a minimum support threshold **and** exceed the next-best by a margin. The skeleton's tree is "a hand-authored single-node tree". With one node there is no next-best, so the margin condition is undefined; P11's `two_condition.margin_over_next` has no value to hold.

Recommended resolution: (a) change P4's fixture 1 context to carry one of §3.5's five terms (e.g. `context_before: "Syllabus — "`), which also makes it §3.2's own worked case; (b) P11 states the degenerate rule explicitly — a single legal candidate satisfies the margin condition vacuously — or the skeleton's tree gains a second node. Either way it must be written down before P11 is built.

---

## MAJOR — real inconsistency, resolvable without redesign

### M1. Four different supersede column sets, and a direct P1↔P4 contradiction (§8.2)

- **P1** publishes four columns "that every superseding record type adopts — **P4's evidence records (§2.8)**, P6's facts, P9's memberships, P11's placement proposals": `supersedes`, `superseded_by`, `supersede_reason`, `preferred`.
- **P4**: `superseded_by`, `supersession_reason` — and explicitly, "there is **no `preferred` field** in the observation. P4 records what was read and what superseded it; P6 decides which one wins."
- **P9**: `superseded_by`, `supersede_reason` (no `supersedes`, no `preferred`).
- **P6**: "`supersedes` / `superseded_by` + reason".
- **P11**: `supersedes` only.

Why it matters beyond naming: §8.2's own worked example — the failed first OCR pass and the later engine that recovers a university name — turns on *which one is preferred*, and P1 and P4 disagree about whether the observation layer records that at all.

Recommended resolution: adopt P1's four columns as the published set (`supersede_reason`, not `supersession_reason`) and resolve `preferred` in P4's favour — §8.2 says "the resolver may mark", and §3.2 places the resolver after extraction. P1 should move `preferred` off the shared column set and onto P6's `file_facts` only.

### M2. P4 forbids the observations P5's image extractor is built to emit (P4 ↔ P5, §2.6)

- **P4**: "**No negative observations.** An observation records presence, never absence. §2.6 forbids treating the absence of EXIF as proof of anything. Absence lives on the run record (`completeness`, `coverage`) or nowhere."
- **P5** E5, trap 1: "'No EXIF' is **emitted as an absence**, never as screenshot evidence." Trap 3: "E5 **records the conflict as an observation** and emits no resolution."
- **P5** E5 also: "E5 emits each signal as its own observation, **tagged with its tier**" (tiers 1–3 from §2.6's hierarchy). P4 has no tier field; its only strength fields are `reliability ∈ {direct, possible}` and an extractor-local `confidence`.

Why it is a problem: three of P5's ten required image fixtures (`whatsapp-stripped-exif.jpg`, `page-photo-dense-text.jpg`, `conflicting-signals.png`) assert behaviour P4's conformance validator would reject. P5's Open question 3 names this and P4 never answers it — P4's Deferred list does not mention the §2.6 tier at all.

Recommended resolution: P4 adds one field. Either `signal_tier ∈ {1,2,3}` on the observation (nullable, §2.6-scoped), or P6 re-derives the hierarchy from `extractor_name` + `location.field` label — which duplicates §2.6 in a second place, as P5 warns. Prefer the field. Separately, P5 must move "no EXIF" and "conflicting signals" off the observation record: absence belongs on `extraction_runs`, and a conflict is a P6 ranking outcome (§3.7's margin rule), not evidence.

### M3. `unreadable` ⇒ zero observations contradicts §2.9's "indexed-but-unreadable" (P4 ↔ P5, §2.9)

- **P4** conformance rule 9: "`unsupported`/`unreadable`/`deferred`/`failed` runs carry **zero observations**."
- **§2.9**, design/creative row: "**At minimum yield filename, format, dimensions or canvas properties, embedded metadata**, layers or artboards where accessible… Unsupported proprietary formats should be recorded as **indexed-but-unreadable** rather than silently treated as empty."
- **P5** fixture `design.psd`: "indexed-but-unreadable, never `extracted_empty`."

Why it is a problem: "indexed" means observations exist. Under P4's rule, an `unreadable` PSD carries none, and is therefore indistinguishable from a file nobody looked at — the precise conflation §2.4 forbids.

Recommended resolution: P4 relaxes rule 9 to `unsupported`/`deferred`/`failed` only, and allows `unreadable` and `partial` runs to carry the metadata-level observations §2.9 requires.

### M4. "Supporting evidence, not truth" — P5 asserts a mechanism P4 says does not exist (P4 ↔ P5, §2.2, §2.3)

- **P5** E1: producer/creator strings "are emitted … and **marked such that P6 cannot read them as content-bearing**; the marking mechanism is Open question #13."
- **P4** fixture 6 (`metadata:field=Producer` → `python-docx`, `direct`): "`direct` describes the *slot*, not the value's usefulness; **P6 discounts it**."

Why it is a problem: P5 tells the extractor author to set a marker; P4's conformance validator rejects any field it does not define; P6's spec contains no discount rule for tool-generated metadata and does not list one under Deferred. §2.2 and §2.3 both require the behaviour, so it is currently owned by nobody.

Recommended resolution: adopt P4's answer (no marker) and add the obligation explicitly to P6 — a `producer/creator` discount rule keyed on P4's `zone = metadata` plus the deferred tool-string list P5 already names. Then close P5 OQ13 as answered.

### M5. `surrounding context` is one field to five parts and two-or-three to P4 (§2.8)

P4 splits §2.8's single "Surrounding context" line into `context_before`, `context_after`, `context_truncated`. P5, P6, P8, P9 and P11 all quote §2.8's eleven-field list verbatim with "surrounding context" as one field; P5's Contract in reproduces it as such. An extractor author working from P5 emits one field and fails P4's conformance rule 1.

Recommended resolution: keep P4's split (it is well argued — §8.4 must redact a value without dropping its context) and correct the reproduced field lists in P5, P6, P8, P9, P11 to name P4's three fields.

### M6. P2 can only express half of §7.7's action set (P2 ↔ P11, §7.7, §7.9)

**P2** `bundle_expectation.expected_value`: "for `residual`: approved residual node | leave-in-place | review-later | abstain (§7.7)" — **four** of §7.7's **eight** actions.

Missing: return to a confirmed domain group; return to an accepted graph or purpose packet; choose an approved broad parent branch; mark as protected or unsupported. The first two are the §7.9 hand-back loop — the mechanism the segmentation map cites as the entire reason P11 fuses §6 and §7 — so P2's dimension 10 cannot record the expected outcome for §7.8's Columbia-submission screenshot, which is the design's own worked example.

Recommended resolution: replace P2's four-value residual expectation with P11's `outcome` vocabulary (`place | return_to_placement | mark_review_later | leave_in_place | mark_state | abstain`) plus the qualifier fields, which P11 already proved covers all eight.

### M7. P9 and P8 publish different verdict enums for the same verdict (§4.8)

- **P9** `Membership.validation_verdict`: `valid-direct | valid-context-supported | contradicted | unsupported | generic-similarity-only`.
- **P8** `Verdict.outcome`: `accept_direct | accept_context_supported | weak | reject | abstain`.

P8's `weak` and `abstain` have no P9 representation; P9's `contradicted`, `unsupported` and `generic-similarity-only` are P8 *reason codes* (`CONTRADICTED_BY_STRONGER`, `GENERIC_SIMILARITY_ONLY`), not outcomes. P9's Open question 6 asks whether P8 carries `valid-context-supported`; it does, under a different name — so P9's central §4.8 distinction survives, but the enum does not.

Recommended resolution: P9 consumes P8's `outcome` + `reasons[]` directly and drops its own enum. P9's five values are recoverable as `(outcome, reason_code)` pairs.

### M8. Provenance event ownership is claimed twice in three places (§8.2)

| Event | Claimed by | Also claimed by |
|---|---|---|
| `discovery`, `stat observation`, `hashing` | P1 ("Events P1 itself appends") | P3 ("Events P3 appends — three of the types §8.2 enumerates") |
| `external modification detection` | P1 ("Events P1 itself appends") | P12 ("P12 is the **sole author** of these six") |
| `undo` | P1 ("appended when P12 reverses an action") | P12 ("sole author") |

P1's "Events P1 accepts from others" list names P5, P6, P9, P10, P11, P12 — and omits P3 entirely, so P1 believes it writes P3's three itself. P1 assigns P12 four types; P12 claims six.

Recommended resolution: the acting part is the author; P1 is the writer. Move all three of P3's and both of P12's to P1's "accepts from others" list. `external modification detection` in particular belongs to P12 (§8.3's staleness triggers) and to P3 (§1.2's re-scan) — it needs two authors, which P1's current framing does not allow.

### M9. `Maximum dossier tokens per model call` has two owners who each claim exclusivity (§8.6)

- **P7**: "Ceilings P7 enforces at the boundary: `Maximum dossier tokens per model call` — the gate mints the payload, so this is **the only place the ceiling is real**." Over budget ⇒ `Denied / dossier_over_budget`.
- **P8**: "Ceilings **P8 owns**, from §8.6's list: … maximum dossier tokens per model call." Over budget ⇒ P8's four-rung reduction ladder, then a new seal.

P6, P9, P10 and P11 also list it among the ceilings they honour.

Why it matters: P8's reduction ladder (§8.6's own order) only works if P8 measures the budget *before* sealing. If the gate is the only real check, the ladder never runs and every over-budget dossier is a denial instead of a summarize/split/defer.

Recommended resolution: P8 enforces it pre-seal and runs the ladder; P7 keeps `dossier_over_budget` as a backstop denial that should never fire. Say so in both specs.

### M10. Wave order does not hold — three forward dependencies (02, *Order*)

| Dependency | Stated where | Wave |
|---|---|---|
| P5 → P7 | P5 Contract in: "From P7 — the operation mode, and the explicit privacy-and-compute policy that is the *only* thing that may authorize speech-to-text transcription" | Wave 2 → Wave 3 |
| P8 → P10, P8 → P11 | P8 Contract in: node-existence oracle over the frozen tree (P10); "the approved residual-library configuration (§7.4)"; "the placement dossier contents §6.6 enumerates" (P11) | Wave 3 → Waves 4, 5 |
| P10 → P11 | P10 Contract in: "From P11 — the residual library (§7.2–§7.4) … where enabled, admits them into the frozen tree" | Wave 4 → Wave 5 |

P10 → P11 is the substantive one: §7.4 says approved residual branches "become legal nodes in the frozen destination tree", so P10 cannot freeze a complete tree without P11's library. P5 → P7 is real but narrow (audio/video only). P8 → P10/P11 is mitigated by fixtures but should be acknowledged.

Recommended resolution: no re-ordering needed, but 02's *Order* section should record these three as fixture-mediated back-edges, the way it already records the three deviations it forced. Alternatively, split the residual-library **definitions** (§7.2/§7.3 — nine names + eight attribute slots) out of P11 into P10, leaving P11 only the residual *workflow* (§7.5–§7.11); that removes the cycle cleanly.

### M11. P5's targeted-OCR back-edge is unaccepted by P6 (P5 ↔ P6 ↔ P2, §2.2, §2.7)

- **P5** Contract in: "**From P6** — a *return* signal: for a PDF with a non-empty but unusable text layer, the verdict that its stored evidence produced no usable facts. This is the only condition that may trigger targeted OCR… **P6's contract must accommodate it.**"
- **P6**: no mention of P5, of a return signal, or of a "no usable facts" verdict anywhere in Contract out or the read surface.
- **P2** adversarial case A10 asserts exactly this behaviour and forbids the alternative.

Recommended resolution: add a `no_usable_facts(file_id, content_hash) -> bool` read to P6's published read surface, with the threshold recorded as a deferred configuration value (P5 OQ5 already flags that the design does not define it).

### M12. Four of the eight fields P10 requests from P9 do not exist under those names (P9 → P10, §4)

P10's Contract in from P9 asks for `group_id`, `label`, `category`, **`domain`**, `members[]` with `membership_kind ∈ {direct-anchor, context-supported}`, **`excluded_members[]`**, `anchor_facts[]`, **`rejected_proposals[]`**.

P9's Group record has no `domain`, no `excluded_members[]` and no `rejected_proposals[]` (the last two are derivable from `Membership.decision = excluded` + `conflicts[]`, and `Group.state = rejected`). P9's `basis_facts[]` is P10's `anchor_facts[]` renamed. And `Membership.basis` has **three** values — P9 adds `user-attached` for §4.9's unreadable files — while P10 expects two.

Recommended resolution: rename `basis_facts` → `anchor_facts` or vice versa; P10 accepts three membership kinds; and settle P9 Open question 4 (is `group_category` the §3.11/§3.15 domain list?) — if yes, `domain` and `category` are one field and P10's request resolves.

### M13. P12 consumes §6.11's prose, not P11's record (P11 → P12, §6.11)

P12's Contract in lists §6.11's design wording ("target file or group, proposed approved destination, decision depth, evidence type…") rather than P11's published field names, and refuses on "`abstain: no supported destination`" — which is a value of P11's `confidence_class`, not of `outcome`. P11 states "P12 consumes only records with `outcome = place`"; P12 never mentions `outcome`. P12 therefore has no stated behaviour for `return_to_placement`, `mark_review_later`, `leave_in_place`, `mark_state`, or `ask_user`.

Recommended resolution: rewrite P12's Contract in against P11's field names, and state explicitly that the five non-`place` outcomes produce no plan.

### M14. `evidence_ref` is ambiguous — two identifiers, and the wrong one is being cited (P4 ↔ P6/P8/P9/P11, §8.2, §8.7)

P4 publishes both `observation_id` (uuid, per row) and `observation_key` (`sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)`, deliberately version-independent). P4's §8.7 answer requires that "`observation_key` is **stable and permanently resolvable**, so a negative example recorded today still resolves after an extractor upgrade."

But P6 says `evidence_refs[] — one or more P4 **observation ids**`; P11 says "P11 cites **observation ids**"; P9 and P8 say `evidence_ref` without qualification. An upgraded extractor emits a new row with a new `observation_id`, so every stored negative example decays — exactly the §8.7 failure P4's answer promises to prevent.

Recommended resolution: P4 names `observation_key` as the citation handle in the Contract out, and the four consumers change "observation id" to "observation key."

### M15. P9's Group record contradicts P9's own plan-versioning answer (§8.8)

P9's `Group` carries `plan_version_id` as its second field, and `Membership` carries it too. P9's Plan-versioning answer then says: "**Shared evidence database** (survives every plan version): typed graph edges, **candidate groups**, dossiers, model responses, validator verdicts, **membership records** and their support and citations, the failure-point log. **Plan version**: the acceptance / rejection state of each group and membership."

If groups and memberships are shared, they cannot carry a `plan_version_id`; only their acceptance state can. P9's own Open question 8 asks whether acceptance is per-version or global.

Recommended resolution: remove `plan_version_id` from Group and Membership and add a separate per-version `group_acceptance` record. This also answers what P10's freeze record means by "Accepted and rejected group memberships | P9, referenced".

---

## MINOR — wording, naming, cosmetic drift

1. **P1 counts.** "Every event row carries the **twelve** §8.2 fields" — §8.2 lists eleven (counting old/new paths as two). "The file record retains at least **fourteen** named items" — §8.2's block has thirteen lines. Cosmetic, but P1's Done-means #7 tests against the count.
2. **`OCR` vs `ocr`.** §8.2 and P1 spell the event type `OCR`; P4 and P5 use `ocr`. Pick one before the writer validates against the vocabulary.
3. **`supersede_reason` (P1, P9) vs `supersession_reason` (P4).** Sub-case of M1; listed separately because it is a pure typo-level divergence.
4. **Verification-point count.** P1 publishes four (V1–V4); P12 says "the **three** checksum verification points and cross-volume copy-and-delete fixity". Same four things, two framings.
5. **P11 never calls `verify_content`.** P1 names "P12 (§8.3) and **P11 (§6)**" as the callers of V1–V4; P11's spec contains no reference to fixity, hashing, or verification. Either drop P11 from P1's caller list or state why §6 needs it.
6. **`destination.kind` vs `node_role`.** P11 emits `approved_child | approved_parent | scoped_fallback | approved_residual`; P10 publishes `node_role ∈ ordinary | scoped-general | residual | shared-material`. Related but not aligned — P11 has no way to say "this is the shared-material branch" except via `confidence_class`.
7. **`two_condition.verdict = review`.** P11's three-value verdict (`accept | review | unresolved`) has no P8 counterpart; P8 expresses review through `requires_review: true` on `accept_context_supported`.
8. **P2 keys extraction output by extractor version.** `bundle_extraction_output[] … keyed by content hash + extractor version`, while P4 deliberately excludes version from `observation_key` so replay diffs work. Compatible in practice; worth a sentence so nobody "fixes" it.
9. **P2's bundle has no run records.** `bundle_extraction_output[]` carries observations only, so P4's `completeness`/`coverage` — which §8.6's counts and P2's own case A9 depend on — is not in the bundle.
10. **P3's `selected_by`** records "user identity (§8.2 event field)" while P1's Open question 14 asks whether `user_id` is real at all in a single-user product. Harmless, but they should agree.
11. **P5's Contract in from P3** lists "Parent-folder context" as a field P3 supplies; P3's R2 lists "directory position" and flags the relationship as unsettled (P3 OQ3). Two names, one field, until settled.
12. **P8 Deferred says P2 authors the adversarial suite; P2 says it authors the twelve cases but defers "the hand-labelled reference corpus."** Consistent, but P8's row reads as if the whole suite is deferred.

---

## Coverage gaps — design obligations no part owns

| # | Obligation | § | Who noticed | Recommended owner |
|---|---|---|---|---|
| G1 | **Where bulk extracted text lives.** "Complete text by page" (§2.2), full text for text-bearing files (§2.4), "raw recognized text" (§2.7). P4's `text_span` presupposes a stored, addressable text unit and explicitly declines to own it; P5 emits it with no home. | §2.2, §2.4, §2.7 | P4 OQ3 ("the largest open question in P4's area") | **P4** — the span semantics are already P4's; add a `text_units` record keyed by `(run_id, container_path)`. Blocks the skeleton. |
| G2 | **Embedding computation and vector storage.** §0 mandates "compact local arrays if embeddings are used" and rules out a vector DB; §4.2 and §6.3 both consume embeddings. No part computes or stores them. | §0, §4.2, §6.3 | P1 OQ8, P9 OQ2 | **P9** (first consumer), or an explicit decision that the skeleton and v1 ship without embeddings. |
| G3 | **The §8.7 learning-record store.** §8.7 requires scoped local learning records and stored negative feedback. P1 carries `correction_scope` on events; six parts write corrections; **nobody owns the store that reads them.** | §8.7 | P1 OQ7 | New micro-part, or **P1** as a scoped projection over `events`. |
| G4 | **The §8.6 budget configuration object.** Twelve ceilings, "configurable", no owner. Six parts say "values are configuration, not contract." | §8.6 | P1 OQ15, P3 OQ15, P5 OQ10, P9 OQ1, P10 OQ1, P11 OQ1 | **P1** (it already owns the database and the storage budget line). |
| G5 | **Duplicate family and version family computation.** §2.9 lists "duplicate and version-family signals" in basic filesystem extraction; §3.11 makes both universal facts. Content hash is P1, perceptual hash is P5, **version family has no owner anywhere.** | §2.9, §3.11, §8.3 | P3 OQ5, P5 OQ8, P12 OQ7 | **P6** — they are universal facts, derived from P1 hashes and P5 perceptual hashes. |
| G6 | **Bounded download session computation.** §3.9 and §4.2 both require it; §3.13 makes it a `Possible` clue. Neither P3 (has the timestamps) nor P6 (has the facts) nor P9 (does the retrieval) claims it. | §3.9, §4.2 | P6 OQ7, P9 OQ3 | **P6** as a `possible` fact, computed from P3's timestamps. |
| G7 | **Photo-event clustering.** §4.2's fourth seed kind is "a deterministic event created from camera, time, and GPS metadata." No part computes it; §6.3 also retrieves on it. | §4.2, §6.3 | P9 OQ11 | **P6** (it is a Photos-domain `event` fact under §3.11) or **P9** (it is a seed). |
| G8 | **`cross_folder_moves` enforcement.** §1.1 lets the user choose "whether files may move across high-level folders." P3 records it, P10 stores it at freeze, **§6 and §7 never mention it and no part enforces it.** | §1.1 | P3 OQ12 | **P12** — it is a mutation-time constraint, alongside the volume check. |
| G9 | **Curated-versus-incidental signal for existing folders.** §5.10 requires the canvas to show it; §1.1's AIKonic case requires the scan to know it. Neither P3 nor P10 claims the computation. | §1.1, §5.10 | P3 OQ10, P10 OQ6 | **P3** — it is an observation over the directory inventory it already publishes. |
| G10 | **The review and approval surface.** §6.11 ("the user should see these distinctions in the review interface"), §7.10 (residual review interface), §8.3 ("show it to the user where policy requires review"), §5.2/§5.9/§5.11 (canvas). P10 owns the canvas *data contract*; nothing owns the placement/residual/apply review UI. | §6.11, §7.10, §8.3 | P12 OQ10 | Out of scope for the twelve, but must be stated as such — otherwise §8.3's "required review policy" has no consumer. |
| G11 | **Career and recruiting fact schema.** §3.15 names it a **launch** domain; §3.11's table gives it no field row. P6 correctly refuses to invent one, so a launch domain ships with no fact schema. | §3.11, §3.15 | P6 Deferred, P10 OQ7 | Author it — this is a genuine hole in the design, not a spec defect. Same for Code and Finance *templates* (§5.4 names five of the six launch domains). |
| G12 | **Non-macOS OCR.** §2.7 says "On macOS, Apple Vision…" and names no other provider. | §2.7 | P5 OQ9 | Scope decision: macOS-only v1, stated. |
| G13 | **User-facing evaluation surface.** §8.5 says the replay system lets "the engineering team **and the user**" evaluate changes. No part owns a user-facing eval view. | §8.5 | P2 OQ12 | Defer explicitly. |
| G14 | **§8.6's progress/legibility surface.** "1,842 files indexed; 1,611 fully extracted; 89 deferred…" — P3 supplies `indexed`, P5/P4 supply extracted/deferred/unreadable, P8 supplies model-review. **No part assembles or renders the line.** | §8.6 | none | **P2** or the same UI owner as G10. |

---

## Overlaps — obligations claimed by more than one part

| # | Obligation | Claimed by | Should own | Why |
|---|---|---|---|---|
| O1 | Destination profile (§6.1) | P10, P11 | **P10** | 02's own *Publishes* column: "node types **and destination profiles**". See B4. |
| O2 | Extraction outcome / status record (§2.4, §2.9) | P4 (`extraction_runs`), P5 (router outcome) | **P4** | Per-extractor granularity + §2.7's config/completeness fields. See B1. |
| O3 | `discovery` / `stat observation` / `hashing` events | P1, P3 | **P3 authors, P1 writes** | P1's own framing everywhere else ("append through P1's writer"). |
| O4 | `external modification detection`, `undo` events | P1, P12 | **P12** (plus P3 for re-scan detection) | The acting part authors; P1 is the log. |
| O5 | Basic filesystem record (§1.2 vs §2.9) | P3, P5 | **P3** computes; P5 emits `source_type: filesystem` observations that reference it | Written twice, it is built twice with two shapes (P3 OQ5's own words). |
| O6 | §3.6 fact validation | P6, P8 | **P8** mechanism, **P6** inputs + consequence | Both specs already say exactly this; P6 OQ2 just needs closing. Sound as written. |
| O7 | §6.10 / §7.9 validation | P8, P11 | **P8** mechanism + verdict, **P11** destination-specific checks + record | Both specs propose this split (P11 OQ11); confirm it and the drift closes. |
| O8 | `Maximum dossier tokens per model call` | P7 ("only place it is real"), P8 ("P8 owns"), + P6, P9, P10, P11 as consumers | **P8** enforces pre-seal; **P7** backstops | Otherwise §8.6's reduction ladder never runs. See M9. |
| O9 | `Maximum LLM calls per thousand files`, `Maximum model cost per scan` | P6, P8, P10, P11 | **P8** | Single egress point owns the call budget; others consume. |
| O10 | `Maximum retrieved neighbors`, `local graph neighborhood size`, `candidate cluster size` | P9 (§4.2 group neighbourhood), P11 (§6.4 node-local graph) | **Both**, on different graphs | Legitimate; label them `grouping.*` and `placement.*` so the config object is unambiguous. |
| O11 | Residual-library configuration in the plan version (§8.8) | P10, P11 | **P10** | P10 freezes; P11 reads. P10 already scopes it as "P11 definitions, P10 enable/rename/relocate choices". |
| O12 | Residual template definitions (§7.2, §7.3) | P10 Contract-in expects them "From P11"; P11 defers their contents | **P11** publishes the nine names + eight slots; contents deferred | Consistent, but creates the P10→P11 wave cycle (M10). Consider moving the definitions to P10. |

---

## Consolidated open questions

143 raw entries deduplicate to 48 clusters. "Blocks skeleton?" is judged against the map's walking skeleton: one PDF, no LLM, no cloud, no embeddings, one-node tree, one move, one undo, one replay.

| # | Question | Raised by | Blocks skeleton? | Recommended owner |
|---|---|---|---|---|
| 1 | Where does bulk extracted text live, and who owns the addressable text unit? | P4 OQ3 | **Yes** — RAW-1 has nothing to index into | P4 |
| 2 | Does a content change create a new `files` row or advance the existing one? | P1 OQ1, P4 OQ2 | **Yes** — every foreign key | P1 |
| 3 | Is the §8.2 event vocabulary closed, and is §8.4's audit record the same log? | P1 OQ5, P7 (answered yes), P8 | **Yes** — P7/P8/P11 invent 21 types | P1 |
| 4 | Do observations and facts share one reliability vocabulary? | P4 OQ4, P5 OQ4, P6 OQ12 | **Yes** — P4 cannot freeze without it | P4 + P6 |
| 5 | What are the analysis tiers? | P4 OQ1, P5 OQ7, P6 OQ1, P2 (`version_tuple.analysis_tier`) | **Yes** — §3.4's cache key cannot be formed | P5 |
| 6 | `scan state` (§1.2) vs `extraction status by tier` (§8.2) vs `completeness` (P4) vs router status (P5) — how many fields? | P3 OQ4, and B1 | **Yes** | P4 + P3 |
| 7 | Who resolves a destination node to a filesystem path, and who creates the directory? | P12 OQ5, and B3 | **Yes** — the skeleton's move step | P12 |
| 8 | Does the two-condition rule have a defined behaviour with a single legal candidate? | none — found in review | **Yes** — one-node skeleton tree | P11 |
| 9 | Which hash algorithm? | P1 OQ10 | Yes (any choice, but it must be made) | P1 |
| 10 | Can two files coexist with the same content hash (duplicate family vs one identity)? | P1 OQ2, P4 OQ2 | No | P1 |
| 11 | Are §8.2's file-record items columns or projections? | P1 OQ4 | No | P1 |
| 12 | How do events with no single file (`destination-tree edit`, `template application`, `graph-edge creation`) record their subject? | P1 OQ3, P3 OQ13 | No | P1 |
| 13 | Do exclusion verdicts get events? | P3 OQ13 | No | P1 |
| 14 | Which timestamps does §1.2 mean? | P1 OQ13, P3 OQ2 | No | P3 |
| 15 | What is `normalized filename`? | P3 OQ1 | No (but §3.7's `MIT`/`submit` guard depends on it) | P3 |
| 16 | `directory position` (§1.2) vs `parent-folder context` (§2.9) — one field or two? | P3 OQ3, P5 (Contract in) | No | P3 |
| 17 | Who determines MIME — P3 by extension, or P5 by signature? | P3 OQ6, P5 (router) | No | P5 sniffs; P3 records provisional |
| 18 | Scan-time traversal of symlinks, aliases, `.app` bundles, network mounts, cloud dirs | P3 OQ7 | No | P3 |
| 19 | May the user override an exclusion, and is that an §8.7 correction? | P3 OQ8 | No | P3 |
| 20 | Does the project-root rule exclude the root itself or only descendants? | P3 OQ9 | No | P3 |
| 21 | The AIKonic case — threshold for "dense with software material" with no marker file | P3 OQ10 | No | P3 |
| 22 | Does the corpus-selection record (sources/roots/cross-folder flag) live in the plan version? | P3 OQ11 | No | P10 |
| 23 | Where is `cross_folder_moves` enforced? | P3 OQ12 | No | P12 |
| 24 | Disappearance and re-scan cadence; who emits `external modification detection` | P3 OQ14, and M8 | No | P3 + P12 |
| 25 | Is there a hashing / traversal ceiling? | P1 OQ15, P3 OQ15 | No | P1 |
| 26 | Who owns the §8.6 budget configuration object and its values? | P1 OQ15, P5 OQ10, P9 OQ1, P10 OQ1/2, P11 OQ1 | No | P1 |
| 27 | Who owns the §8.7 learning-record store? | P1 OQ7 | No | unassigned — G3 |
| 28 | Who owns embeddings (computation + the §0 array store)? | P1 OQ8, P9 OQ2 | No (skeleton has none) | P9 |
| 29 | Is the volume/root identifier stable across remount, rename, cloud re-sync? | P1 OQ9 | No | P1 |
| 30 | Is `user_id` real in a single-user product? | P1 OQ14, P3 (`selected_by`) | No | P1 |
| 31 | One database, or one per corpus root? | P1 OQ16 | No | P1 |
| 32 | Does P1 validate other parts' vocabularies? | P1 OQ17 | No (but interacts with #3) | P1 |
| 33 | What must survive a "rebuild from the filesystem"? | P1 OQ11 | No | P1 |
| 34 | Is `preferred` chain-scoped or (file, field)-scoped — and does the observation carry it at all? | P1 OQ12, P4 (says no), and M1 | No | P6 |
| 35 | Where do OCR languages/config/confidence/capped live? | P5 OQ2 (open) vs P4 D5 (**settled**) | No — **answered by P4** | close as answered |
| 36 | Is `Location` a flat string or structured? | P5 OQ1 (open) vs P4 D1–D4 (**settled**) | No — **answered by P4** | close as answered |
| 37 | Where does an image observation record its §2.6 evidence tier? | P5 OQ3 | No (skeleton is a PDF) | P4 — M2 |
| 38 | How is "supporting evidence, not truth" expressed on the record? | P5 OQ13 (asserts a marker) vs P4 fixture 6 (**no marker**) | No | P6 — M4 |
| 39 | Who invokes targeted OCR on a broken-text-layer PDF, and what is "no usable facts"? | P5 OQ5 | No | P6 — M11 |
| 40 | Routing precedence for formats §2.9 lists twice (CSV, PDF decks) | P5 OQ6 | No | P5 |
| 41 | Do spreadsheets and presentations ship at launch or as `unsupported`? | P5 OQ11 | No | release scope |
| 42 | Does reclassifying a file as private delete or only gate stored observations? (§8.4 delete vs §8.2 append-only) | P5 OQ12, P7 OQ4 | No | P1 + P7 |
| 43 | Does P5 assign a handling class or only supply the signal? | P5 OQ14, P7 (Contract in) | No | P7 |
| 44 | May a nested archive's manifest be read one level down, in memory? | P5 OQ15 | No | P5 |
| 45 | Library/engine choices for every format except macOS OCR; non-macOS OCR provider | P5 OQ9 | No | P5 |
| 46 | May a user author or correct an observation directly? | P4 OQ6 | No | P6 |
| 47 | Is the §8.4 handling class per observation or per file? | P4 OQ5, P7 OQ1 | No | P7 |
| 48 | Is `purpose` universal or Applications-scoped? Are `subject` and `course` one field? Multiplicity of (file, field)? Equal-rank contradiction? | P6 OQ3, OQ4, OQ6, OQ10 | No | P6 |
| 49 | Does Finance activate as a fact schema at launch, or is it detection-and-protection only? | P6 OQ5 | No | P6 + P7 |
| 50 | Does user approval of an LLM-generated custom template create `fields` rows, and at what scope? | P6 OQ8, P10 OQ11 | No | P6 + P10 |
| 51 | After the user accepts a group, does §4.7's purpose become a fact on non-anchor members? | P6 OQ9 | No | P6 + P9 |
| 52 | Is `sensitivity` one record or three (§3.11 fact / §8.2 file-record state / §8.4 handling class)? Is `protected` exactly the top two classes? | P6 OQ11, P7 OQ1, P9 OQ9, P10 OQ3 | No | P7 |
| 53 | Filename vs path in §8.4's always-local set | P7 OQ2 (**resolved and flagged**) | No | confirm P7's reading |
| 54 | What is a "corpus area" for `cloud_assisted` consent? | P7 OQ3 | No | P7 |
| 55 | Does `unreadable_unclassified` permit a *local* model call? Is a local call a consent event? | P7 OQ5, OQ6 | No | P7 |
| 56 | Retention of audit records, consent grants, superseded classifications; the install-default mode and redaction settings | P7 OQ10, OQ11 | No | P7 |
| 57 | What is an "external connector" besides a model? | P7 OQ9 | No | P7 |
| 58 | Which model serves each call site; is the response schema the same for local and cloud? | P8 Q1 | No | P8 |
| 59 | What quantity is §6.10's "support" measured in? | P8 Q2, P11 OQ2, P2 OQ2 | No (but blocks any threshold work) | P11 |
| 60 | Does the two-condition rule apply beyond site C? | P8 Q3 | No | P8 |
| 61 | Who holds the redaction reverse-mapping, and for how long? | P8 Q4 | No | P7 |
| 62 | What makes a proposal "equivalent" to one already rejected (§4.9 SR6, §8.7)? | P8 Q5, P9 OQ7 | No | P9 |
| 63 | May a `weak` / `possible` output re-enter a later dossier as evidence? | P8 Q6 | No | P8 |
| 64 | Must conflicting evidence always be shown to the model (silent at sites A and D)? | P8 Q7 | No | P8 |
| 65 | Retry on `SCHEMA_INVALID` — new seal, budget, grounding denominator? | P8 Q8 | No | P8 |
| 66 | Site E's validation boundary between P8 and P10 | P8 Q9, P10 (**claims V1–V6**) | No — **P10 accepted the split** | close as answered |
| 67 | Batch granularity at site D (one call or N?) | P8 Q10 | No | P11 |
| 68 | Is `group_category` the §3.11/§3.15 domain list or a separate vocabulary? | P9 OQ4, P10 (asks for `domain`) | No | P9 |
| 69 | Must P9's edge types and P11's §6.5 relationship types be one enum? | P9 OQ5 | No | P9 + P11 |
| 70 | Is group acceptance per plan version or global? | P9 OQ8, and M15 | No | P9 |
| 71 | Where does §4.9's protected-record surfacing land — P9 group, P7 surface, or P11 residual? | P9 OQ9, P7 OQ1 | No | P7 |
| 72 | Are tentative discovery candidates surfaced at all in v1? | P9 OQ10 | No | P9 |
| 73 | Must P9 publish intra-packet member roles for §6.8? | P9 OQ12 | No | P9 |
| 74 | Depth limit value; §5.9 warning thresholds | P10 OQ1, OQ2 | No | P10 |
| 75 | May the user add a node after freeze, and does that re-freeze? | P10 OQ4 (**open**) vs P11 (**settled: new plan version**) | No | see E18 below |
| 76 | Is `node_id` stable across plan versions? | P10 OQ5, P12 (`destination_changed`) | No | P10 |
| 77 | Do Code and Finance ship with folder templates? | P10 OQ7 | No | design gap — G11 |
| 78 | Is the scoped `General` branch auto-proposed or opt-in per parent? | P10 OQ8 | No | P10 |
| 79 | Is the shared-material policy tree-global or per-branch? | P10 OQ9, P11 OQ12 | No | P10 |
| 80 | Are user-saved personal templates plan-versioned or library-scoped? | P10 OQ11 | No | P10 |
| 81 | Is `confidence_class` a closed list? Is `abstention_reason` closed? | P11 OQ3, OQ4 | No | P11 |
| 82 | Does the two-condition rule apply per member inside a group plan? | P11 OQ5 | No | P11 |
| 83 | §6.9 — abstain *or* ask: which, when? | P11 OQ6 | No | P11 |
| 84 | Is §6.9's "reference or alias convention" a filesystem link? | P11 OQ7, P12 OQ8 | No | P12 |
| 85 | How many times may a file cycle between §7 and §6? | P11 OQ8 | No (threatens P2 determinism) | P11 |
| 86 | Are residual set-level decisions versioned and reversible? Is §7.5's set partition canonical? | P11 OQ9, OQ10 | No | P11 |
| 87 | Deterministic collision-suffix format | P12 OQ1 | No | P12 |
| 88 | Does P11 emit one decision per file or per group, and who expands it? | P12 OQ2 | No | P11 |
| 89 | Behaviour for locked files, files open elsewhere, aliases, shortcuts | P12 OQ3 | No | P12 |
| 90 | Batch bound and halt rule | P12 OQ4 | No | P12 |
| 91 | What becomes of an unverified destination copy after a failed cross-volume move? | P12 OQ6 | No | P12 |
| 92 | Where do version-family and deduplication review surface? | P12 OQ7 | No | P11 |
| 93 | Journal and undo lifetime | P12 OQ9 | No | P12 |
| 94 | Where is the required-review gate enforced? | P12 OQ10 | No | G10 |
| 95 | Do the two §8.5 ten-item lists (stages vs dimensions) reconcile? | P2 OQ1 | No | P2 |
| 96 | Pass thresholds / regression tolerance for any dimension | P2 OQ2 | No | P2 |
| 97 | Does attribution follow `inputs[]` across subjects? | P2 OQ3 | No | P2 |
| 98 | Is `tree` an assertion or an observation, and is it replayable? | P2 OQ4 | No | P2 |
| 99 | May a metadata-safe bundle leave the device, and what does "metadata-safe" exclude? | P2 OQ5, P7 OQ8 | No | P7 |
| 100 | No attribution stage for scan, privacy, or apply | P2 OQ6 | No | P2 |
| 101 | May replay write to the shared evidence database? Does shadow mode write to `events`? | P2 OQ7, P1 OQ6 | No | P2 |
| 102 | Does shadow mode get its own budget? | P2 OQ8 | No | P2 |
| 103 | Is the adversarial gate blocking or advisory? | P2 OQ9 | No | P2 |
| 104 | Can a shadow adjudication become an §8.7 correction? | P2 OQ10 | No | P2 |
| 105 | Is a run reproducible, given unspecified sampling parameters? | P2 OQ11 | No | P8 |
| 106 | Is there a user-facing eval surface, and how are shadow examples selected? | P2 OQ12 | No | G13 |

*(Clusters are numbered 1–106 after merging; 48 distinct subjects, several carrying multiple sub-questions from the same raiser.)*

### Open questions two parts answered differently

| Question | One spec says | The other says | Resolve as |
|---|---|---|---|
| Does the observation carry `preferred`? | **P1**: yes — "P4's evidence records" adopt it | **P4**: "there is no `preferred` field in the observation" | P4 — §8.2 puts preference on "the resolver" |
| Who owns the destination profile? | **P10**: "P10 emits the profile" | **P11**: "Built by P11 from each frozen node" | P10 — 02's own *Publishes* column |
| Who resolves a node to a path? | **P11**: "P12 resolves the node to a filesystem path" | **P12**: paths "must be supplied at tree design, never by P12" | P12 |
| Who authors `external modification detection` and `undo`? | **P1**: "Events P1 itself appends" | **P12**: "P12 is the sole author of these six" | P12 authors, P1 writes |
| Who authors `discovery` / `stat observation` / `hashing`? | **P1**: P1 appends them | **P3**: "Events P3 appends — three of the types §8.2 enumerates" | P3 authors, P1 writes |
| Who enforces `Maximum dossier tokens per model call`? | **P7**: "the only place the ceiling is real" | **P8**: "Ceilings P8 owns" | P8 pre-seal, P7 backstop |
| Is tool-generated metadata marked on the record? | **P5**: "marked such that P6 cannot read them as content-bearing" | **P4**: no marker — "P6 discounts it" | P4; give P6 the rule |
| May the user create a folder after freeze? | **P10 OQ4**: open | **P11**: settled — "a tree edit, routed to P10 and producing a new plan version" | P11's answer; close P10 OQ4 |
| Where do OCR config / languages / confidence / capped live? | **P5 OQ2**: open, "the single most likely place P5 and P4 fail to meet" | **P4 D5**: settled — `extraction_runs` | P4; close P5 OQ2 |
| Is `Location` structured? | **P5 OQ1**: open, "the single highest-risk item between P4 and P5" | **P4 D1–D4**: settled — structured record + canonical locator | P4; close P5 OQ1 |
| Does P8's verdict distinguish context-supported? | **P9 OQ6**: open | **P8**: yes — `accept_context_supported` | P8; close P9 OQ6 (rename per M7) |
| Who runs §5.7's six template checks? | **P8 Q9**: open, "the design does not draw that line" | **P10**: claims V1–V6 explicitly | P10; close P8 Q9 |

---

## What is sound

These seams were checked in detail and genuinely agree. Do not re-examine them.

**P8's four-into-one merge is complete.** I walked §3.6's four checks, §4.8's six, §6.10's five plus the two-condition rule, and §7.9's four against P8's reason-code registry. Every one has a code, at the right site, with the right outcome class. §3.3's "appropriate for a proposal rather than merely a search hint" survives as `SEARCH_HINT_ONLY → weak`; §7.9's strengthening of the citation check ("inside **this file's** record") survives as a distinct `EVIDENCE_NOT_IN_FILE_RECORD`; §4.8's requirement that retrieval, interpretation and label failures be logged *separately* survives as `dossier_builder` on the grounding report, and P9 independently built the matching failure-point log with the same three stages. Nothing was lost in the merge. The one composition P8 performed itself (`reject` + `STRONGER_RELATIONSHIP_OVERLOOKED` → `return_to_placement`) is flagged in its own spec for exactly this review.

**§7.7's eight actions survive intact at both ends.** P11 reproduces all eight verbatim, maps every one into the single `outcome` + qualifier vocabulary with no ninth action and no field the §6 path lacks, and P8 enforces closure over the same set with `ACTION_NOT_IN_CONTROLLED_SET`. The mapping table is correct. (P2's four-value expectation is the only break — M6.)

**Deferral discipline held across all twelve blind agents.** Nobody authored a template from the 200–300 library; nobody wrote a gazetteer entry; nobody invented a domain fact field beyond §3.11's literal six-row table (P6 lists exactly that table and explicitly refuses to fill §3.11's unnamed "several additional fields"); nobody added a tenth residual template. I grepped for invented numeric thresholds and found none — every number in the specs traces to the design (`200 DPI` from §2.7, `30 days` explicitly marked as a §7.11 user example, `1,842/89/18` quoted from §8.6). Four separate specs independently identified that §3.15 names Career a launch domain while §3.11 gives it no fields, and all four deferred rather than inventing it.

**§8.8's plan-version split is unanimous.** All twelve quote the same sentence — "the evidence database remains shared across plan versions" — and land on the same line: files, events, observations, facts, values, groups and edges are shared; tree, node identifiers, template versions and ordering, labels and aliases, residual configuration, privacy and placement policies, and acceptance/review decisions are versioned. P6's refinement (the *value* is shared, its display label is versioned, per §8.8's "User labels and aliases") is correct and consistent with P4's three-form raw/normalized/display table. Only P9 has an internal wobble (M15).

**§8.6's degradation clause is answered consistently by all twelve.** Every spec states its own concrete form of "cost exhaustion must never turn into lower-quality automatic classification" — P1: budget pressure never weakens a fixity check; P4: a capped run never interpolates and never adjusts `reliability`; P6: a field reachable only by LLM stays empty rather than being filled from a `possible` clue; P7: an unclassified file takes `unreadable_unclassified`, never `public_low`; P8: never substitute a cheaper model; P10: freeze is never auto-completed; P12: a plan that cannot be verified is parked, never applied best-effort. This is the cleanest cross-cutting answer in the set.

**P4 ↔ P6 on the observation→fact boundary.** P6 reads P4's shape as opaque values with no per-format branching (its Done-means #6 tests exactly that), never edits or re-normalizes an evidence row, and both agree that a fact never overwrites a raw value and that a user correction lands on the fact, never the observation. P4's positional-weighting handoff is correct: P4 publishes the closed `zone` vocabulary, P6 owns what each zone is worth. The one break is the `surrounding context` field split (M5).

**P4 ↔ P7 on redaction granularity.** P7 requires observations to be span-addressable so the gate can materialise `(observation_id, span)` excerpts and reject a whole-document request; P4 delivers exactly that with `text_span`, `region`, `time_span` and the canonical locator. This is the property §8.4's "selected excerpts, redacted identifiers" depends on, and it holds.

**P1 ↔ P12 on fixity.** P1's V1–V4 and P12's three checkpoints plus cross-volume pre-removal confirmation are the same four points from §8.2, in the same order, with the same consequence (a mismatch leaves the source in place and yields `failed`). The framing differs; the substance does not.

**P9's stop rules and P8's pre-call suppression agree.** §4.9's SR6 ("the user has already rejected an equivalent proposal") is enforced at P8's boundary as `abstain / USER_REJECTED_EQUIVALENT`, and P9 correctly declines to re-implement the validator. Both flag the same missing definition (what makes two proposals equivalent) rather than inventing one.

**Nobody let the model invent a destination.** P9 forbids a folder hierarchy in a group response; P10 makes freeze an ID-membership test; P11 makes `destination` a `node_id` so invention is inexpressible; P8 adds `INVENTED_NODE`, `NODE_NOT_IN_FROZEN_TREE` and `INVENTED_FOLDER`; P12 refuses a plan whose destination is not in the frozen tree of the referenced plan version. Five independent parts, five compatible enforcements of §6.12's central prohibition.
