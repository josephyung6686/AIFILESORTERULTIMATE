# Re-review after the fix round

Date: 2026-08-19
Scope: thirteen `parts/*/SPEC.md`, verified at **both ends of every seam** against
[`04-resolutions.md`](04-resolutions.md), [`05-minor-resolutions.md`](05-minor-resolutions.md),
[`03-contract-review.md`](03-contract-review.md), and the source of truth
[`00-database-agent-product-design.md`](00-database-agent-product-design.md).

**Verdict: not yet — six of the eight blockers and nine of the fifteen majors are genuinely closed at
both ends, but B7 is broken at three of six ends, the fix round introduced four new seam failures
(P13 is unreciprocated by every part it touches, `text_units` has no consumer, `destination.kind`
survives in two specs after P11 deleted it, `observation_id` survives throughout P7 after M14), and
the one edit `04` assigned to the lead — updating `02-segmentation-map.md` — did not happen at all.**

Nothing found here requires redesign. Every item below is a one-to-three-line edit in a named spec.
The estimate is one focused pass over eight files, then freeze.

---

## Summary

| Resolution | Landed both ends? | Evidence |
|---|---|---|
| **B1** one extraction-outcome record | **yes** | P4 §Record 2 publishes the eight `completeness` values incl. `metadata_only`; P5 line 154 reproduces all eight and states *"`extracted_empty` is `complete` with zero observations"*; P5 line 144 *"P5 publishes no status vocabulary of its own"*; P2 case A9 uses *"`completeness = capped` — P4's word, not a third one"*; P13 lists all eight. Counting restated in P5, P2 and P13. |
| **B2** one gate | **yes** | P7 §6 `Gate.release(ModelCallRequest) -> Released \| Denied \| NeedsConsent`; P8 line 84 identical, `seal` explicitly withdrawn; binding tuple `(model_target, prompt_fingerprint, policy_version)` in both; P8 line 353 *"There is deliberately no code for `NeedsConsent`, and none may be added"*; P8 Done-means 13 and P7 Done-means 7 both falsifiable; P13 §5 presents all four options. |
| **B3** node → path | **yes** | P10 line 205 *"P10 holds no filesystem path strings"* + Done-means 11 (grep test); P12 §Contract out 3 owns the full composition with five rules; P11 line 500 *"P12 resolves the node to a filesystem path"*; P12 OQ5 answered (directory creation + conditional removal, §7 dir-reversal outcomes); P13 shows the ancestor label chain, never a path. |
| **B4** destination profile → P10 | **yes** | P10 §Contract out 2 *"The profile is P10's alone (B4)"* with the full field table; P11 §Contract out 2 *"P11 publishes no profile table and holds no profiles in its plan-version state"*; P11 plan-versioning section repeats it. |
| **B5** open event vocabulary | **partial** | P1 §Contract out 3 publishes the four-clause registration rule and the reserved nineteen (verified: 19 names); P7 declares 8, P8 declares 5, P11 declares 8 — all three self-register. **But P1 contains zero occurrences of "P13", and P13 declares three types P1's registry table does not list.** |
| **B6** `accepts_placement` | **yes** | P10 line 187 + the derivation rule; P11 Contract-in carries all five B6 fields in bold; P11 Done-means 2 tests *"one naming a node whose `accepts_placement` is `false`"* separately from node existence. |
| **B7** `stage_output` | **NO** | P5 (`extraction`), P6 (`factual_validation`) and P9 (`retrieval`/`graph_construction`/`grouping`) emit legal ids. **P8 emits `stage_id = P8`, P10 emits `stage_id = P10`, P11 emits `stage_id = P11` — none is a member of P2's closed ten.** P6's `unresolved` abstention row ✓. |
| **B8** walking skeleton | **partial** | (a) P4 fixture 1 now reads `context_before: "Syllabus — "` ✓. (b) P11 states the vacuous-margin rule with `meets_margin ∈ true \| true_vacuous \| false` ✓, P10 Done-means 2(a) requires **two** frozen nodes ✓. **But `02-segmentation-map.md` still reads "a hand-authored single-node tree".** |
| **M1** supersede columns | **partial** | Spelling `supersede_reason` ✓ in P1/P3/P4/P6/P9; `preferred` on P6's `file_facts` alone ✓ (P4 line 711 explicitly declines it). **P11's `placement_decision` carries `supersedes` only — no `superseded_by`, no `supersede_reason`**, though M1 says *"P9 and P11 adopt the full set."* |
| **M2** `signal_tier` | **yes** | P4 line 184 + line 223 (§2.6-scoped, nullable); P5 E5 emits it per signal; P6 line 111 *"P6 consumes the tier and never re-derives it"*; P5's absence rule and conflict rule both point at P6's §3.7 margin. |
| **M3** conformance rule 9 | **yes** | P4 rule 9 restricts zero-observation to `unsupported`/`deferred`/`failed`; P5 line 162 *"Still carries the metadata-level observations §2.9 requires"*; P4 fixture 18 and Done-means 5 exercise it; P13 renders it as *"indexed but unreadable"*. |
| **M4** producer/creator discount | **yes** | P6 §Production rules publishes the two-tier rule keyed on `zone = metadata`; P5 line 226 *"There is no marker on the observation (M4)"* and P5 OQ13 closed at both ends; P6 Done-means 22. |
| **M5** three context fields | **yes** | P4 D9 + line 194; reproduced by name in P5 (line 73), P6 (line 108), P8 (line 138), P9 (line 72), P11 (line 187). |
| **M6** P11's full residual vocabulary in P2 | **partial** | P2 now carries all eight §7.7 actions and Done-means 12 asserts §7.8's Columbia case ✓. **But the `place` qualifier is `destination.kind ∈ approved_residual \| approved_parent` — a field P11 deleted under MINOR 6.** |
| **M7** one verdict vocabulary | **yes** | P9 line 106 *"P9 publishes no verdict enum of its own"* + the seven-row recovery table; P8 owns the five outcomes; P11 adopts the same five in `two_condition.verdict`. |
| **M8** acting part authors, P1 writes | **yes** | P1 §Provenance authorship table assigns all nineteen; P3 authors four; P12 authors six; `external modification detection` two authors stated identically in P1, P3 and P12, separable by `subsystem`. P1 Done-means 12 tests it. |
| **M9** dossier-token split | **yes** | P8 §Budgets *"P8 measures the dossier against the ceiling before it calls the gate"* + the four-rung ladder; P7 §Budgets withdraws the gate-only reading in the same words and keeps `dossier_over_budget` as a backstop; P7 fixture obliges P8 to prove the ladder ran. |
| **M10** residual library → P10 | **partial** | P10 §Contract out 6 holds the nine names, eight slots, enablement model, three dispositions ✓; P11 line 66 *"§7.2–§7.4 are P10's, not P11's"* ✓; P9, P12, P13 all point at P10 ✓. **P1, P3, P4 and P6 still attribute the residual library to P11 in their Deferred tables.** |
| **M11** `no_usable_facts` | **yes** | P6 read surface publishes `no_usable_facts(file_id, content_hash) -> bool` with the "computed from the fact tables and nothing else" negative; P5 Contract-in accepts it as a back-edge; P2 case A10 asserts it as *"the only condition that may trigger it"*. |
| **M12** P10 ← P9 field names | **partial** | `anchor_facts[]` renamed at both ends ✓; `group_category` is one field at both ends ✓; `excluded_members[]` derivation ✓. **Three residues: P11 carries only two of the three membership kinds; P10 calls the field `membership_kind` where P9 calls it `basis`; P10 reads `Group.state = rejected`, a value absent from P9's `state` enum.** |
| **M13** P12 ← P11 | **yes** | P12 Contract-in is written against P11's field names; both specs independently say *six* non-`place` outcomes and both explain why M13 said five; P12 branches on `outcome`, and both state `confidence_class` is descriptive only. |
| **M14** `observation_key` | **partial** | P4, P6, P8, P9, P11, P2, P10 and P13 all cite the key and several state the reason ✓. **P7 uses `observation_id` in five load-bearing places, including the releasable-item kinds P8 hands it.** |
| **M15** `group_acceptance` | **yes** | P9 §Contract out 8; `Group`/`Membership` carry no `plan_version_id`; P2's `bundle_accepted_group[]` resolves through it; P9 Done-means 11 asserts one shared evidence set across two acceptance rows. |
| **MINOR 1–3, 5, 7–10, 12** | **yes** | 1: P1 says eleven event fields (verified: 11) and thirteen file-record items (8 columns + 5 histories) with Done-means 7. 2: `OCR` spelled §8.2's way in P1/P4/P5. 3: `supersede_reason` in P4. 5: P1 *"P12 is the only caller"*, P11 calls nothing. 7: P11 uses `accept_context_supported` + `requires_review`. 8: both P4 and P2 state the divergence reason in one sentence each. 9: P2's `bundle_extraction_run[]` exists with a rationale paragraph. 10: `selected_by`/`user_id` nullable in P3 and P1, P1 OQ14 closed. 12: P8's Deferred row corrected. |
| **MINOR 4** V1–V4 framing | **partial** | P12 adopts P1's V1–V4 explicitly and disambiguates from P10's template V1–V6 ✓. **P13 Contract-in asks for *"the execution record with its three §8.2 checkpoint hashes"*.** |
| **MINOR 6** `node_role` sole vocabulary | **partial** | P10 owns it, P11 deleted `destination.kind` with a full rationale ✓. **P2 and P13 both still name `destination.kind`.** |
| **MINOR 11** one field, §2.9's name | **partial** | P3 renames ✓, P4 uses the new name ✓. **P1's column is still `directory_position`; P5 and P9 list *both* names as two separate fields; P6 and P10 use the old name only.** |
| **G1–G14** | **13 of 14** | G2–G14 all landed at their owners and, where applicable, their consumers. **G1's `text_units` appears in P4 and P5 and in no other spec.** |
| **S1–S5** | **yes** | S1 macOS-only stated in P5 with the non-macOS half of OQ9 closed; S2 P9 computes / P1 stores, with P9's six-rule boundary; S3 Career/Code/Finance deferred in P6 and P10; S4 P13 exists; S5 P1 holds the learning store and the fifteen-key budget object. |
| **02-segmentation-map** | **NO** | The lead's assigned edit — *"two-node skeleton, P13, M10 back-edges"* — is absent in all three respects. |

---

## STILL BROKEN — original findings not fully closed

### S-1 (BLOCKING) B7 — three parts emit a `stage_id` that does not exist

**Parts:** P2 ↔ P8, P10, P11. **§8.5.**

P2 §Contract out 1: *"The `stage_id` enumeration is **closed** and is exactly §8.5's list"* — the ten
values are `extraction`, `factual_validation`, `retrieval`, `graph_construction`,
`llm_interpretation`, `grouping`, `template_generation`, `tree_design`, `candidate_node_retrieval`,
`placement_scoring`. The envelope reads `stage_id  one of the ten`.

Against that:

- P8 line 439: *"P8 emits P2 `stage_output` with `stage_id = P8`"*
- P10 line 157: *"**Emits P2 `stage_output` with `stage_id = P10`**"*
- P11 line 225: *"**Emits P2 `stage_output` with `stage_id = P11`**"*

`04`'s B7 wrote the instruction with a placeholder — *"stage_id = \<id\>"* — and three of the six
measured parts pasted the placeholder as a part name. P5, P6 and P9 substituted correctly, which is
what makes this a transcription failure rather than a disagreement. The consequence is not cosmetic:
P2's `attributed_stage` is *"the earliest stage on this subject's `inputs[]` chain"*, so a run whose
LLM, template, tree, retrieval and scoring outputs are filed under three non-existent ids cannot
attribute a single error, and five of P2's ten dimensions have no producer. This is the exact failure
02 moved P2 into Wave 1 to prevent.

**Recommended resolution.** Each of the three names the stages it actually owns, per P2's own table:
P8 → `llm_interpretation`; P10 → `template_generation` **and** `tree_design`; P11 →
`candidate_node_retrieval` **and** `placement_scoring`. P9 is the model to copy — it already writes
`stage_id ∈ retrieval, graph_construction, grouping`, one per subject.

### S-2 (MAJOR) B7's second half — the envelope's `outcome` is confused with the record's `outcome`

**Parts:** P2 ↔ P8, P9, P10, P11. **§8.5, §8.6.**

P2's envelope has its own vocabulary: `outcome ∈ produced | abstained | deferred | not_implemented |
error` plus `budget_state ∈ within_ceiling | ceiling_reached`, and P2 Done-means 6 requires
*"`deferred` is reported separately from `divergent` for every dimension."*

P6 is the only part that maps into it explicitly — its five-row table (*"one or more facts written →
`produced`"* … *"an §8.6 ceiling stopped the work → `deferred` / `ceiling_reached`"*). The others
describe the separation in their **own** vocabulary and never name the envelope value:

- P11 line 227: *"`outcome = abstain` is the abstention value and `deferred_stage` with
  `abstention_reason = budget_deferred` is the distinct budget-deferral value"* — both of these are
  P11's `placement_decision.outcome`, not `stage_output.outcome`. Read literally, a budget deferral
  emits `stage_output.outcome = abstained`, and P2 scores it `abstained_correctly` or
  `abstained_incorrectly` rather than `deferred`.
- P8 line 441: *"`abstain` with `BUDGET_EXHAUSTED` is the budget deferral"* — same conflation.
- P9 and P10 assert the four obligations in one sentence and give no mapping at all.

**Recommended resolution.** P8, P9, P10 and P11 each add P6's two-column table: their own result →
P2's `outcome` + `budget_state`. Three lines each. Without it, P2's Done-means 6 ("a run whose only
change is a lower budget ceiling produces zero new divergences") is not satisfiable.

### S-3 (MAJOR) B5 — P13's three event types are unregistered, and P1 has never heard of P13

**Parts:** P1 ↔ P13. **§8.2, S4.**

P13 §Provenance: *"**Events P13 appends**, registered under P1's registration rule (B5)"* —
`review presentation`, `review action routed`, `apply review approval`.

P1's registry table lists exactly three declaring parts — P7 (8), P8 (5), P11 (8) — and `grep -n
"P13" P1-storage-identity-provenance/SPEC.md` returns **nothing**. P1's writer *"validates
`event_type` against the union of the reserved nineteen and every registered declaration. An
unregistered type is rejected at the writer"*, and P1 Done-means 11 tests exactly that rejection.

P1's rule 2 (*"The declaration is the definition"*) arguably self-heals this, but P1's registry, its
Contract-in, its Done-means fixtures and its learning-store consumer list are all written as if P13
does not exist. See also N-1, of which this is one instance.

**Recommended resolution.** Add a fourth row to P1's registration table — `P13 (§6.11, §7.5, §8.3) |
3 | new types: review presentation, review action routed, apply review approval` — and add P13 to
P1's Contract-in and to the `learning_records` consumer list in Contract out §7.

### S-4 (BLOCKING for the skeleton) B8(b) and S4 — `02-segmentation-map.md` was never updated

**Parts:** 02 ↔ P10, P11, P13. **§6.10, B8(b), S4, M10.**

`04`'s implementation partition assigns one row to the lead: *"02-segmentation-map | Updated by the
lead: two-node skeleton, P13, M10 back-edges."* None of the three landed:

1. 02's skeleton still reads *"P10  a hand-authored **single-node** tree; freeze it"*, while P10
   Done-means 2(a) requires *"**two** hand-authored frozen nodes … Two, not one: resolution B8(b)
   requires the skeleton to exercise §6.10's margin condition rather than bypass it"* — and cites 02
   as its source. P10 cites a document that contradicts it.
2. 02 is titled *"the twelve parts"*, its parts table stops at P12, and its build shape says *"All
   twelve `SPEC.md` files."* Thirteen exist.
3. 02 still records P10 as owning *"§5"* and P11 as owning *"§6, §7"* — M10 moved §7.2–§7.4 and B4
   moved §6.1. The acknowledged back-edges M10 names (P5 → P7, P8 → P10/P11) are absent.

**Recommended resolution.** Apply the three edits `04` already specified. The skeleton line becomes
*"a hand-authored two-node tree"*; add a P13 row and a fourteenth wave-6 entry or equivalent; correct
P10's and P11's Owns cells and add the back-edge note.

### S-5 (MAJOR) M14 — P7 never adopted `observation_key`

**Parts:** P7 ↔ P8, P4. **§8.4, §8.7.**

M14 named *"P6, P8, P9 and P11"* and P7 was not on the list, but P7 is on the citation path and its
five uses are load-bearing:

- Contract-in from P4: *"The gate materialises excerpts by `(observation_id, span)`"*
- Releasable item kinds: `excerpt { observation_id, span, reason }`,
  `redacted_identifier { observation_id, span, identifier_class }`
- Classification record: `evidence_refs[]  observation ids (P4)`
- Audit record: *"`excerpts_included` stores `(observation_id, span)` pairs"*
- §8.7 answer: *"stores the observation ids the detector fired on, so the same signal does not
  resurface the same false protection"*

P8, meanwhile, builds `ModelCallRequest.requested_items[]` out of P7's item kinds while its own
`evidence_ref` *"is P4's `observation_key` … not `observation_id` (M14)."* So P8 holds keys and P7's
item kinds ask for ids: the two ends of the only egress path in the product disagree on the handle.

M14's own argument applies to P7 with more force than to any other part. §8.4 requires the audit
record to answer *what left the device*, permanently; P7's own §8.7 answer depends on a detector
signal still resolving later. `observation_id` *"dies on extractor upgrade"* (P4), so both guarantees
decay silently at exactly the moment §8.5 exists to measure.

**Recommended resolution.** P7 replaces all five with `observation_key`. Note the one place where
this is *not* mechanical: `Released.materialised_items[]` and the `CITATION_SPAN_MISMATCH` check
compare against *what the model actually saw*, and P8 OQ4 (redaction reverse-mapping ownership) is
still open — the key change does not close it, but it does not worsen it either.

### S-6 (MAJOR) M12 — P11 cannot express a `user-attached` membership

**Parts:** P9 ↔ P11. **§4.3, §4.8, §4.9, §6.8.**

M12: *"P10 accepts **three** membership kinds (`direct-anchor`, `context-supported`, `user-attached`
— the third is §4.9's manual attachment for unreadable files)."* P9 publishes all three on
`Membership.basis`; P10 accepts all three; P2 reads all three by name.

P11 has two. Contract-in from P9: *"member files with membership kind (**direct anchor** vs
**context-supported**, §4.3)"*, and the record field is `group_support { group_id, membership:
direct-anchor | context-supported }`.

P9 invariant 5 is what makes this bite: *"A file whose evidence is unreadable, encrypted, corrupted
or of an unsupported format **may only** receive `basis = user-attached`."* Those files reach §6.8
group placement — P10 line 93 says a branch *"may be justified by it"* — and P11's record has no
value for them. The likely field-level failure is a `user-attached` member silently recorded as
`context-supported`, which P11 then routes to review as if evidence existed.

**Recommended resolution.** P11 adds `user-attached` to `group_support.membership` and to its
Contract-in from P9, plus one line saying it never yields `evidence_type = validated` and never
`review_policy = auto_eligible` (P10's constraint: *"P10 must not present a `user-attached` member as
evidence-derived"*).

### S-7 (MAJOR) M12/M15 interaction — P10 reads a `Group.state` value P9 does not publish

**Parts:** P9 ↔ P10. **§4.9, §8.7, §8.8.**

P10 Contract-in: *"`rejected_proposals[]` — derived from `Group.state = rejected`. A rejected proposal
must not be resurfaced as a branch candidate."*

P9's `Group.state` after M15: *"`candidate | supported | tentative-discovery | unresolved` — the
SHARED engine lifecycle. **`accepted` and `rejected` are resolved AS OF a plan version from
`group_acceptance` (8), never stored here.**"*

P9 tries to bridge it in prose — *"`rejected` is supplied by `group_acceptance` for the plan version
P10 is freezing. A consumer reads `Group.state` **as of** a plan version"* — but that is a derived
view P9 does not publish as a call, and P10's text is unchanged from before M15. An implementer reads
P10, looks for `rejected` in P9's enum, and does not find it.

**Recommended resolution.** P9 publishes the accessor explicitly (`group_state_as_of(group_id,
plan_version) -> candidate | supported | tentative-discovery | unresolved | accepted | rejected`) and
P10 cites it instead of the bare field. One line each.

### S-8 (MAJOR) M1 — P11's decision record is missing two of the three published columns

**Parts:** P1 ↔ P11. **§8.2.**

M1: *"P1's four columns are the published set … **P9 and P11 adopt the full set.**"* P1 §Contract out
4 lists the three shared columns and names *"P11's placement proposals (§6.11)"* among the adopters.

P11's `placement_decision` carries `supersedes  prior decision_id, or null — never overwritten §8.2`
and nothing else. Its Provenance section describes the semantics correctly — *"together with the
reason it was superseded"* — but the field to hold that reason does not exist in the record, and
`superseded_by` (P1: *"inverse link; the old row stays readable"*) is absent, so the forward link
from a superseded decision to its replacement cannot be followed. §8.8's *"twenty-three files now
require renewed review"* diff and P11 Done-means 16 both walk that link.

**Recommended resolution.** P11 adds `superseded_by` and `supersede_reason` beside `supersedes`.

### S-9 (MINOR) MINOR 11 — the rename landed in two specs of seven

**Parts:** P3 → P1, P5, P6, P9, P10. **§1.2, §2.9.**

MINOR 11: *"§2.9 says 'parent-folder context'. Ground truth wins; P3 renames."* P3 renames and P4
uses the new name. Five specs did not follow:

- P1's `files` column is literally `directory_position`, with an explanatory note beside it
- P5 Contract-in lists *"Size, timestamps, **directory position**"* **and**, three lines later,
  *"**Parent-folder context**"* — one field presented as two, which is the precise defect MINOR 11
  was raised to remove
- P9 Contract-in: *"directory position **and** parent-folder context"* — also two
- P6 and P10 use `directory position` only

**Recommended resolution.** P5 and P9 delete the duplicate line (blocking-grade for those two, since
an implementer would build two fields); P1, P6 and P10 rename. If P1 wants to keep the column
spelling, it must say so as a deliberate storage-name divergence rather than as a note.

### S-10 (MINOR) MINOR 4 — P13 asks for three checkpoint hashes

P13 Contract-in from P12: *"the execution record with its **three** §8.2 checkpoint hashes."* P12's
execution record carries four rows (V1, V2, V3, and `Destination confirmed pre-removal  V4`), and
MINOR 4 settled that *"P1's V1–V4 framing is adopted."* A review surface that renders three cannot
show the user the cross-volume pre-removal confirmation — the one verification that stands between a
mismatch and a deleted source. **Fix:** "four §8.2 checkpoint hashes (V4 on cross-volume moves only)."

### S-11 (MINOR) MINOR 5 is right but mis-cited, and P1 does this three times

**Part:** P1. `05` states the rule explicitly: *"Items in this document are cited as **`MINOR n`**,
never as `Mn`. `M1`–`M15` refer to the MAJOR findings … Do not conflate the two schemes."*

P1 conflates them in exactly the three cases where the collision is real:

| P1 line | Cites | Means | `Mn` with that number actually is |
|---|---|---|---|
| 88, 133 | `M11` | MINOR 11 (parent-folder rename) | `no_usable_facts` (cited correctly by P5) |
| 178, 603 | `M10` | MINOR 10 (`user_id` nullable) | the residual-library move (cited correctly by P10, P11) |
| 265, 464 | `M5` | MINOR 5 (P12 is the only V1–V4 caller) | the three-field context split (cited correctly by P4, P5, P6) |

P3 is inconsistent with itself — line 88 says `M11`, line 390 says `MINOR 11`. **Fix:** six
substitutions in P1, one in P3.

### S-12 (MINOR) M10 — four Deferred tables still name P11 as the residual-library owner

P1 line 381 (*"§7.2, §7.3 (P11)"*), P3 line 250 (*"§7.3, P11"*), P4 line 652 (*"P11."*), P6 line 603
(*"P11's surface"*). P9 and P12 and P13 all get it right. **Fix:** four one-word substitutions.

---

## NEWLY INTRODUCED — created by the fix round

### N-1 (BLOCKING) P13 is unreciprocated by every one of the twelve parts it touches

**Parts:** P13 ↔ P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12. **S4, G10, G13, G14.**

P13 declares Contract-in from nine parts and routes `review_action` to six (*"placement and residual
actions to P11; tree edits … to P10; consent choices and redaction settings to P7; refresh and apply
approval to P12; group changes to P9; a reset to P1"*). It publishes four records:
`review_action`, `progress_line`, `review_approval`, and the review item.

`grep -rn "review_action\|review_approval\|review presentation" parts/*/SPEC.md` outside P13 returns
**nothing**. Not one part declares P13 in its Contract-in, accepts a `review_action`, or names
`review_approval` as the record that satisfies §8.3's `Required review policy`.

Some parts point at P13 as a *destination* — P7 (*"surfaces the requirement … through P13"*), P8, P12
(*"the surface is P13"*), P6 (*"P13 review surface"*), P2. That is one-directional acknowledgement,
not a contract: none of them says what P13 hands back or in what shape. P12 is the sharpest case —
its OQ10 is *"Settled by S4 … P13 is where the user satisfies it. The plan's `Required review policy`
field is the seam"*, while P13 §4 says *"P13 produces the record that satisfies it."* Neither spec
names the other's record, so P12's precondition has no typed input and P12 Done-means has no fixture
for an approved plan.

This is the predictable consequence of writing P13 last and in isolation; it is also the single
largest remaining risk, because P13 sits on the §8.3 gate that P12 refuses without.

**Recommended resolution.** Three edits, not thirteen: (1) P12 Contract-in gains
`review_approval {approval_id, plan_id, verdict}` from P13 as the event that satisfies
`review_policy`, plus a fixture; (2) P11 and P10 Contract-in each gain a one-line "user decisions
arrive as P13 `review_action`, carrying `correction_scope`, and are authored by this part" —
consistent with M8's acting-part-authors rule, which P13 already restates correctly; (3) P1 registers
P13's three event types (S-3). P7 already has what it needs.

### N-2 (BLOCKING) P13 renders `destination.kind`, and so does P2 — a field P11 deleted

**Parts:** P11 → P2, P13. **MINOR 6, §6.11, §7.7.**

P11 line 345: *"**Why there is no `destination.kind`** (MINOR 6). An earlier draft carried `kind ∈
approved_child | approved_parent | scoped_fallback | approved_residual` alongside P10's `node_role`.
Two vocabularies for one concept is what M7 forbids."* P11's record now publishes
`destination { node_id, node_role }`, and the parent-versus-child distinction moved to
`decision_depth.unsupported_levels[]`.

Both consumers still read the deleted field:

- P13 Contract-in, line 82: `` `destination {node_id, kind}` `` — P13 was written before or
  independently of P11's MINOR 6 edit and never mentions `node_role` on the destination.
- P2 `bundle_expectation`, line 218: `` `place` + `destination.kind` ∈ approved_residual |
  approved_parent ``. Neither value exists in `node_role` (`ordinary | scoped-general | residual |
  shared-material`). This is inside the M6 fix itself — P2's expanded residual expectation was written
  against P11's pre-MINOR-6 draft.

The P2 case is the more serious of the two: dimension 10's expected values are the contract P2's
adversarial fixtures and Done-means 12 are built on, so §7.8's Columbia case would be asserted against
a vocabulary no part emits.

**Recommended resolution.** P13: `destination {node_id, node_role}`. P2: `place` + `node_role ∈
residual` for the approved-residual case, and `place` + non-empty
`decision_depth.unsupported_levels[]` for the approved-parent case — P11 states that mapping
explicitly and P2 can quote it.

### N-3 (MAJOR) `text_units` is a new record with no consumer, and P4 names three that never accept it

**Parts:** P4 → P2, P6, P7, P8. **G1, §2.2, §2.4, §2.7, §8.4, §8.5.**

G1 gave P4 the `text_units` record (`(run_id, container_path)`), and P4 D12 justifies it by naming
who needs it. P5 writes it. `grep -rl text_units` returns **P4 and P5 and nothing else.** Each of
P4's three named consumers contradicts the claim by silence:

| P4 says | The named part says |
|---|---|
| Rule 6: *"§4.4's 'short evidence excerpts' … are **cut from** these rows by P8 under P7's gate"* | P7's gate resolves `(observation_id, span)` against *"local storage"* and never mentions a text unit; P8 never mentions one either |
| *"§8.5's 'Did the expected text appear?' is a query against `text_units`"* | P2's bundle carries `bundle_extraction_output[]` (observations) and `bundle_extraction_run[]`. **No text units.** Dimension 1's *"Did the expected text … appear?"* has nothing to query |
| D12: *"§2.4 requires text-bearing files' full text"* consumed downstream | P6 reads *"the frozen observation shape and **nothing else**"* |

P2 is the blocking half. MINOR 9 correctly added the run rows to the bundle and stopped there;
without the units, a replay cannot answer the first of P2's ten dimensions, and P4's own claim about
§8.5 is false as the specs stand.

**Recommended resolution.** P2's replay bundle gains `bundle_text_unit[]` (or states in one sentence
that dimension 1 asserts over observations only and that P4's §8.5 claim is withdrawn — but the first
is right, since a `capped` OCR run's *recovered text* is precisely what a version-to-version diff
needs). P7 and P8 each add one line naming `text_units` as where an excerpt is cut from, which also
gives P7's always-local guarantee (*"complete extracted text … should remain local"*) a concrete
referent.

### N-4 (MAJOR) P13's `Owns:` line claims four sections P11 also claims

**Parts:** P11 ↔ P13, and P2/P12 secondarily. **S4.**

P13 header: *"Owns: **§6.11, §7.5–§7.6, §7.10**, §8.3 (review presentation), §8.4 (rendering +
consent), §8.5 (user view), §8.6 (legibility)."* The qualifying parentheses begin at §8.3; the first
four are claimed flat.

P11 header: *"Owns: §6 except §6.1 (P10), §7 except §7.2–§7.4 (P10)"* — which contains §6.11, §7.5,
§7.6 and §7.10. P11 §Contract out 1 calls the §6.11 record *"this part's primary obligation."*

S4 assigned P13 *"the review and approval surface"* and closed G10/G13/G14; it reassigned no section.
P13's own body agrees with P11 — its Explicitly-not-owned table concedes *"the residual **set
computation** and the semantics of a set decision, including §7.6's gating rule | P11"* — so only the
header is wrong. But 02's rule is one owner per slice, and `04`'s partition table promises *"No two
implementers write the same file"*; two headers claiming §6.11 is how that promise gets broken.

**Recommended resolution.** P13's header becomes *"Owns: the review and approval surface — §6.11,
§7.5–§7.6, §7.10, §8.3, §8.4, §8.5, §8.6 **(presentation and collection only; the records and their
semantics belong to P11, P12, P7, P2)**"*, or apply the same parenthetical qualifier to the first four
that it already applies to the last four.

### N-5 (MINOR) P10 respells P7's closed operation-mode vocabulary

P7: *"A value outside this set is a load error, not a fallback"*, for `offline | local_model |
hybrid | cloud_assisted`. P10 Contract-in: *"the active operation mode (`Fully offline` /
`Local-model` / `Hybrid` / `Cloud-assisted`)."* Same four modes, four different literals. P2 avoids
the trap by writing *"one of the four §8.4 operation modes"*. **Fix:** P10 uses P7's spellings.

### N-6 (MINOR, latent) B8(a) does not say the §3.5 context check is case-insensitive

P4's skeleton fixture sets `context_before: "Syllabus — "`. P6's rule is literal: a course fact
requires *"academic context — **"syllabus", "lecture", "credits", "instructor", or "semester"**"*, and
§3.5's terms are lowercase. P6's word-boundary and case discipline is specified for §3.7 facet
matching, not for the §3.5 context check.

B8(a)'s entire purpose was to make the skeleton's one fact resolvable, so an unstated case rule is
worth one sentence rather than a discovery during the skeleton build. **Fix:** P6 states that the
§3.5 context-term check is case-insensitive (or P4 changes the fixture to lowercase).

---

## VOCABULARY MISMATCHES

Closed enums appearing in more than one spec, checked member by member.

| Vocabulary | Owner | Status |
|---|---|---|
| `completeness` (8) | P4 | **Consistent.** P4, P5, P13 list all eight identically; P2 uses `capped`/`complete`/`unreadable` correctly. |
| `stage_id` (10) | P2 | **BROKEN** — see S-1. Three parts emit non-members. |
| `stage_output.outcome` (5) | P2 | **Under-specified at four parts** — see S-2. |
| Handling classes (5) | P7 | **Consistent.** P7's five snake_case values; P10's node example uses `personal_non_sensitive`; P12, P13, P2 refer to *"the five §8.4 classes"* without respelling. |
| Operation modes (4) | P7 | **Drift at P10** — see N-5. |
| `node_role` (4) | P10 | **Consistent at P10/P11/P12**; **P2 and P13 still name the deleted `destination.kind`** — see N-2. |
| `disposition` (3) | P10 | **Consistent.** P10, P11 and P12 all list `physical-destination \| review-only \| leave-in-place`. |
| `node_type` (5) | P10 | **Consistent** across P10, P11, P12, P13. |
| P8 `outcome` (5) | P8 | **Consistent.** P9 and P11 both adopt `accept_direct \| accept_context_supported \| weak \| reject \| abstain` verbatim (M7, MINOR 7). |
| §3.13 reliability states (6) | P6 | **Three spellings of one enum.** P4/P6 write `llm_supported`, `user_confirmed` (snake_case); P8 writes `LLM-supported`, `User-confirmed` (Title-Hyphen) in the ordering it treats as *"given"*; P11 writes `llm-supported`, `user-confirmed` (lower-hyphen). P4's conformance rule 2 rejects a value not *"drawn from the closed vocabularies"*, so a literal round-trip P6→P8→P11 fails on spelling alone. **Fix:** P6 publishes the canonical literals once; P8 and P11 adopt them. |
| P11 `evidence_type` (6) | P11 | **Undeclared divergence.** P11 cites *"§6.11, §3.13"* for `user-confirmed \| direct \| validated \| llm-supported \| **context-supported** \| possible` — five of §3.13's six plus one value that is a membership basis, with `rejected` dropped. §6.11 enumerates nothing, so P11 is entitled to define it, but it must say so rather than cite §3.13 for a list §3.13 does not contain. **Fix:** one sentence stating the divergence and why (`rejected` cannot support a placement; `context-supported` is the §4.8 basis surfacing at the decision layer). |
| `membership basis` (3) | P9 | **Two problems.** P11 has two of three (S-6); P10 calls the field `membership_kind` where P9 publishes `basis` (S-6, second half). P2 and P10 have all three values. |
| `Group.state` (4) | P9 | **P10 reads a fifth value** — see S-7. |
| `seed_kind` (4) | P9 | **The photo event has no member.** The design (§4.2) says *"A seed may be a strongly identified file, a validated shared fact, a structural family, or a user-created starting point"*, then gives the photo event as an *example*: *"For a photo group, it might be a deterministic event created from camera, time, and GPS metadata."* `04`'s G7 calls it *"§4.2's **fourth seed kind**"*, and P6 and P9 OQ11 both repeat that phrase — but §4.2's fourth kind is `user-created-starting-point`, and P9's enum has no value for a deterministic event. Under `05`'s fidelity rule (*"the design is ground truth … an implementer that finds a resolution here conflicting with §-text must not apply it, and must report the conflict"*) this is a reportable conflict. **Fix:** P9 states which existing `seed_kind` a photo `event` fact seeds under — `validated-shared-fact` is the natural reading, since the event is a `validated` P6 fact — and P6 and P9 drop the phrase "fourth seed kind". |
| §4.2 retrieval channels (6) | P9 | **Consistent with the design.** P9's `support_kind` and `edge_type` both list the six in §4.2's order, and P9 OQ3 correctly corrects the earlier "sixth" to "fifth" for the bounded session. |
| §7.7 actions (8) → P11 `outcome` (7) | P11 | **Consistent.** The mapping table collapses 8→7 with qualifiers; P12 and P2 both reproduce it correctly; P11 and P12 independently reconcile M13's "five" against the actual six non-`place` outcomes. |
| §8.6 count vocabulary | P5 | **Two small disagreements.** P5: *"**unreadable** = runs at `unreadable` **or `failed`**"*; P2 and P13 both map only `unreadable`. P5: *"**deferred** = runs at `deferred` or `capped`"*; P13 agrees, P2 names only `capped`. A `failed` run therefore appears in no P13 progress-line entry, which P13's own rule forbids (*"no indexed file may be absent from every entry"*). **Fix:** P2 and P13 adopt P5's two mappings. |
| §8.7 scopes (6) | P1 | **Consistent** across P1, P3, P6, P7, P8, P9, P10, P11, P12, P13. |
| §8.2 event names (19) | P1 | **Consistent.** Verified 19; `OCR` spelled §8.2's way in P1, P4 and P5 (MINOR 2). |
| §8.6 ceiling keys (15) | P1 | **Consistent.** P5 claims 4, P8 claims 3, P9 claims 4, P10 claims 1, P11 claims 7, P2 lists them, P12 and P13 claim none — all drawn from P1's namespaced set, with the `grouping.*`/`placement.*` split honoured by P9 and P11. |

---

## P13 — records it claims that do not exist as named

P13 was written last and blind, so every record it names was checked against the publishing spec.
Most check out; four do not.

| P13 claims | Publishing spec | Verdict |
|---|---|---|
| `destination {node_id, **kind**}` | P11 | **Does not exist.** P11 deleted it under MINOR 6; the field is `node_role`. See N-2. |
| *"the execution record with its **three** §8.2 checkpoint hashes"* | P12 | **Wrong cardinality.** Four (V1–V4). See S-10. |
| *"registered under P1's registration rule"* for three event types | P1 | **Not registered.** P1's table has P7/P8/P11 only. See S-3. |
| `review_approval` as the record that satisfies §8.3 | P12 | **Exists in P13 only.** P12 names no record; the seam is prose on both sides. See N-1. |
| Placement decision record — 24 named fields | P11 | **Verified field by field.** All present with matching names: `decision_id`, `plan_version`, `supersedes`, `origin_stage`, `returned_from`, `subject`, `group_plan_id`, `outcome`, `return_target`, `marked_state`, `ask`, `decision_depth{node_depth, supported_depth, unsupported_levels[]}`, `evidence_type`, `confidence_class`, `matching_facts[]`, `group_support`, `graph_anchors[]`, `conflicts_considered[]`, `alternatives[]`, `two_condition`, `abstention_reason`, `deferred_stage`, `privacy`, `review_policy`, `explanation`, `residual`. |
| `group_plan {shared_parent_node_id, member_decisions[], excluded_outliers[]}` | P11 | **Exists exactly.** |
| `residual_set` — seven §7.5 attributes | P11 | **Exists.** P11's record has all seven plus `reason_not_placed`. |
| `residual_set_decision` and its four choices | P11 | **Exists**, four choices verbatim. |
| Node record — 11 named fields | P10 | **All exist**, including `node_role`, `disposition`, `accepts_placement`, `root_anchor`. |
| Freeze record and node-level diff | P10 | **Exist** (§Contract out 4). |
| `Gate.display_policy()`, `Gate.summarize_protected()`, `Gate.may_move_automatically()`, `RevocationResult.retraction_limit`, `NeedsConsent {requirement, options}` | P7 | **All exist** with those exact names and the four verbatim options. |
| Move plan (13 §8.3 fields), precondition verdict, name resolution record, collision resolution record, journal entry, undo verdict | P12 | **All exist** under those names; the five staleness triggers match. |
| P3 `R5` counts | P3 | **Exist:** `files indexed`, `paths excluded, by rule`, `files deferred (scan budget exhausted)`. |
| P4 `extraction_runs.completeness` (8) and `coverage {units, processed, total}` | P4 | **Exist**, all eight values correct. |
| P2 `run_manifest`, `assertion` (+`attributed_stage`), `comparison.per_dimension[]`, `surfaced_examples[]`, `review_adjudication[]` | P2 | **All exist.** P13 says *"the per-stage `assertion` record with its **seven** verdicts"* — P2 lists exactly seven. Correct. |
| P1 learning projection and budget configuration object | P1 | **Exist** (Contract out §7, §8). |
| P6 `file_facts` + `observation_key` resolution | P6/P4 | **Exist.** |
| *"P13 emits no `stage_output` … inventing an eleventh stage would corrupt P2's closed `stage_id` enumeration"* | P2 | **Correct**, and notably the only spec in the set that reasons about the closed enumeration properly. |

P13's record-level fidelity is high — its errors are two stale field references, one cardinality slip
and one missing registration. The structural problem is not what it claims but that nothing claims it
back (N-1).

---

## READY — seams verified genuinely closed

Brief, because these need no further work.

- **B1.** One extraction-outcome record, one vocabulary, eight values, three restatements of the
  counting rules that agree. P5's deletion of its rival enum is explicit and its `extracted_empty`
  migration note is stated so an older draft can be read safely.
- **B2.** The strongest seam in the set. One gate signature, adopted verbatim, with the
  no-consent-code rule enforced structurally at both ends and falsifiable from either side (P7
  Done-means 7 tests the audit log; P8 Done-means 13 tests by grep and by fixture). P13's §5 closes
  the loop with three binding obligations.
- **B3.** P10 holds no paths and proves it by grep; P12 owns composition with five rules covering the
  existing-ancestor short-circuit, per-segment normalization, target-volume evaluation and the
  sibling-collision refusal; P11 and P13 both defer correctly. P12 OQ5 answered with a complete
  directory-reversal rule that does not touch §7.11.
- **B4.** Profile at P10, index at P11, with both specs stating the same reason for the boundary.
- **B6.** The legality flag is consumed and separately tested; P11 Done-means 2 explicitly says
  *"Both tests run; passing the first is not sufficient."*
- **M2, M3, M4, M5, M7, M8, M9, M11, M13, M15** — all verified at every end they touch, with the
  reasoning restated on both sides rather than asserted on one.
- **MINOR 1, 2, 3, 7, 8, 9, 10, 12** — verified, including the two counts (eleven event fields,
  thirteen file-record items) recomputed from P1's own tables.
- **S1, S2, S3, S5** and **G2–G14** (G1 excepted) — landed at owner and consumer alike. G6 and G7 are
  worth calling out: P6 authored both computations with the design's prohibitions attached
  (`download_session` capped at `possible` and `destination_eligible = FALSE`; the photo `event` as
  `validated`, never `direct`), and P9 consumes both.
- **The four cross-spec questions in `05`** — all four are recorded as settled in the specs that
  asked them (P10 OQ4, P5 OQ2 and OQ1, P8 Q9), with the P8/P10 template-validation split stated
  identically in both directions.

---

## Recommended order of work before freeze

Eight files, in dependency order. Nothing here is a redesign.

1. **P8, P10, P11** — correct `stage_id` (S-1) and add P6's envelope-mapping table (S-2). P9 adds the
   table too. *Blocks P2 entirely.*
2. **02-segmentation-map.md** — the three edits `04` already assigned (S-4).
3. **P2** — replace `destination.kind` with `node_role` / `unsupported_levels[]` (N-2); add
   `bundle_text_unit[]` or withdraw P4's §8.5 claim (N-3); adopt P5's `failed`/`capped` count mappings.
4. **P13** — `node_role`, four checkpoint hashes, the `Owns:` qualifier (N-2, S-10, N-4).
5. **P7** — `observation_id` → `observation_key`, five places (S-5).
6. **P11** — `user-attached`; `superseded_by` + `supersede_reason`; the `evidence_type` divergence
   sentence (S-6, S-8, vocabulary table).
7. **P1** — register P13's three types; six `Mn` → `MINOR n` substitutions; residual-library owner;
   optionally the column rename (S-3, S-11, S-12, S-9).
8. **P3, P4, P6, P9, P10** — residual-library owner (S-12), the parent-folder-context rename and the
   two duplicate lines (S-9), P9's `group_state_as_of` accessor and seed-kind sentence (S-7,
   vocabulary table), P10's operation-mode spellings (N-5), P6's case-insensitivity sentence (N-6),
   P6's canonical reliability-state literals.

After that pass, the contracts can freeze. The two largest risks that remain are not seam defects but
open questions the design genuinely does not answer — every numeric threshold in §3.7, §4, §5.9 and
§6.10, and the §8.4 deletion-versus-append-only conflict (P7 OQ4, P5 OQ6, P13 OQ11) — and both are
correctly recorded as open rather than guessed.
