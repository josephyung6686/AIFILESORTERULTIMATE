# P2 — Evaluation and replay harness

Owns: §8.5
Status: contract draft

---

## Purpose

§8.5 requires a replay system that lets the engineering team and the user evaluate changes
**without touching a live filesystem**, and requires that evaluation be **decomposed by stage**:
"If the final destination is wrong, the system should identify whether the error began with
extraction, factual validation, retrieval, graph construction, LLM interpretation, grouping,
template generation, tree design, candidate-node retrieval, or placement scoring. A single overall
'accuracy' number hides the mechanism that needs repair."

P2 publishes the machinery that makes that possible: the replay bundle format, the stage-output
envelope every measured part emits, the per-stage assertion record, the run-to-run comparison
record, shadow mode, and the adversarial test suite named in §8.5.

P2 is ordered before the stages it measures (`02-segmentation-map.md`, *Order*: "per-stage
measurement cannot be retrofitted"). Its contract is therefore written to be usable by parts that
do not exist yet: a stage id that has no implementation is a legal, representable value with
outcome `not-implemented`, not an error. A neighbouring part can be built against P2's envelope
and assertion fixtures before P2 is built, and P2 can be built and its skeleton test made to pass
while nine of the ten measured stages are still absent.

---

## Design slice owned

P2 owns §8.5 in full, and nothing else:

- the replay bundle (§8.5, ¶1) — its contents, its two corpus forms, its pinned versions;
- stage decomposition (§8.5, ¶2) — the ten named attribution stages and the earliest-divergence
  obligation;
- the ten measured dimensions (§8.5, ¶3) and their assertion records;
- the adversarial test suite (§8.5, ¶4) — twelve named cases and the pre-live-plan gate;
- shadow mode (§8.5, ¶5) — parallel recommendations, disagreement sets, selected human review;
- the explicit prohibition on a single overall accuracy number (§8.5, ¶2).

**Not owned by P2**, and consumed only through the owning part's contract: the observation shape
(P4, §2.8), any stage's internal payload (P5/P6/P8/P9/P10/P11), the provenance event log (P1,
§8.2), the consent-aware audit record and handling classes (P7, §8.4), the correction record and
its scope (§8.7, written by the part that receives the correction), the plan version object (P10,
§8.8), and the mutation transaction (P12, §8.3). P2 reads these; it defines none of them.

P2 asserts on outcomes. It does not repair them, does not re-rank, and does not feed its verdicts
back into any live decision path.

---

## Contract in

### A. What P2 reads from neighbouring parts

| From | What P2 reads | § |
|---|---|---|
| P1 | `files` identity: internal file ID, content hash + algorithm, path history; the append-only `events` log, including responsible subsystem, extractor or model version, prompt fingerprint, time of observation, evidence reference | §8.2 |
| P3 | the corpus selection and exclusion decisions in force for the scan a bundle was captured from | §1.1 |
| P4 | the observation record — read as an opaque payload, compared by value, and cited by `observation_key` (content-addressed), never `observation_id` (per-row, dies on extractor upgrade); the `extraction_runs` row that scopes it, for its `completeness` and `coverage`; and the `text_units` rows that run emitted, which are where §8.5's "Did the expected text … appear?" is asserted (P4 D12, G1) | §2.8, §2.7, §2.2, §2.4, §8.7 |
| P5 | extraction outputs per file version, stamped with extractor name and version | §2.1–2.7, §2.9 |
| P6 | file facts with field, value, evidence link, and reliability state (one of the six in §3.13); and the explicit `unresolved` marker P6 emits when §3.6 validation fails, carrying the field attempted and the reason — never a missing row | §3.12, §3.13, §3.6 |
| P7 | each file's handling class (one of the five in §8.4) and the consent-aware audit record for every model call | §8.4 |
| P8 | the dossier sent, the cited response, and the validation verdict — including `unknown` returns | §3.6, §4.8, §6.10, §7.9 |
| P9 | candidate neighbourhoods, typed graph edges, candidate groups, and membership basis — `direct-anchor`, `context-supported`, or §4.9's `user-attached` (manual attachment for an unreadable file) | §4.2–4.5, §4.8, §4.9 |
| P10 | proposed branches, template applications, the frozen tree, destination profiles, and the plan version id | §5.4, §5.12, §6.1, §8.8 |
| P11 | the placement decision record — proposed node, decision depth, evidence type, confidence class, alternatives, and abstentions | §6.11, §7.7 |
| P6/P9/P10/P11 | correction records with their §8.7 scope, including the explicit **negative** records (rejected groups, destination matches, labels, residual recommendations) | §8.7 |

### B. Obligations P2 places on every measured part

These four are the whole reason P2 is ordered early. A part that does not satisfy them cannot be
measured per-stage afterwards without rewriting its boundaries.

1. **Emit a stage output through the envelope.** Every measured part writes one
   `stage_output` record per subject it decides about, with the envelope fields below. The
   `payload` is opaque to P2 and remains the producing part's to define; the envelope is not.
   Required by §8.5's per-stage decomposition.

2. **Record abstention as an explicit value, never as an absence.** §8.5 measures "Did it abstain
   when evidence was absent?" (fact quality) and "did the engine choose the correct frozen node, an
   appropriate shallow fallback, or **abstain**?" (placement quality); §6.10 states that "correct
   abstention is a successful outcome." If a part represents abstention by writing no row, P2
   cannot distinguish a correct abstention from a crash, a skip, or a budget deferral, and two of
   the ten dimensions become unmeasurable.

3. **Record budget deferral as distinct from abstention and from a wrong answer.** §8.6: when the
   budget is exhausted the product "should retain extracted evidence, mark the deferred stage, and
   leave the file or group in review rather than guessing," and "cost exhaustion must never turn
   into lower-quality automatic classification." A deferral scored as a divergence would read as a
   quality regression when it is a budget event.

4. **Stamp every output with the version tuple.** §8.5 requires the same bundle to be re-processed
   by "a new extractor version, graph algorithm, LLM prompt, model, template library, or placement
   scorer and compared against prior results"; §3.4 fixes the cache key as content hash, extractor
   version, analysis tier, model identifier, and prompt fingerprint. Without the stamp, a
   comparison between two runs cannot name what changed.

A fifth is required by §8.5's "where the error **began**" wording but is not named by the design:
each `stage_output` must carry `inputs[]`, the subject references of the stage outputs it consumed.
Attribution to the earliest divergent stage is only computable over that edge set. The design
states the obligation, not the mechanism; this is the minimum the obligation implies. See Open
question 3.

**Accepted, not assumed.** All five obligations are now stated in the Contract out of every measured
part — P5, P6, P8, P9, P10 and P11 each declare that they emit a `stage_output` with their own
`stage_id`, carrying `inputs[]`, an explicit abstention value, a distinct budget-deferral value, and
the version tuple. Two consequences bind P2's own surface:

- **P6 emits an explicit `unresolved` abstention row.** A §3.6 validation failure previously produced
  a missing row, which P2 cannot distinguish from a crash, a skip, or a budget deferral. P6 now emits
  a marker carrying the field attempted and the reason, so dimension 2's "Did it abstain when
  evidence was absent?" is measurable rather than inferred from an absence.
- **No measured part's abstention is left to coincidence.** P11's `outcome = abstain`, P9's
  `coherence_verdict = abstained` and P8's `abstain` satisfy obligation 2 by contract now, not by
  accident of design.

---

## Contract out

### 1. The ten attribution stages (§8.5, ¶2)

The `stage_id` enumeration is closed and is exactly §8.5's list, in §8.5's order — which is also
the pipeline order of §4.10 and §6.12.

| # | `stage_id` | §8.5 name | owning part |
|---|---|---|---|
| 1 | `extraction` | extraction | P5 (§2), shape from P4 (§2.8) |
| 2 | `factual_validation` | factual validation | P6 (§3.5, §3.6) |
| 3 | `retrieval` | retrieval | P9 (§4.2) |
| 4 | `graph_construction` | graph construction | P9 (§4.3) |
| 5 | `llm_interpretation` | LLM interpretation | P8 (§3.3, §4.5) |
| 6 | `grouping` | grouping | P9 (§4) |
| 7 | `template_generation` | template generation | P10 (§5.4, §5.7) |
| 8 | `tree_design` | tree design | P10 (§5) |
| 9 | `candidate_node_retrieval` | candidate-node retrieval | P11 (§6.2) |
| 10 | `placement_scoring` | placement scoring | P11 (§6.10) |

§8.5 names no attribution stage for scan and exclusion (P3, §1.1), the privacy gate (P7, §8.4), or
apply and undo (P12, §8.3). P2 reads from those parts but attributes no error to them. See Open
question 6.

### 2. The ten measured dimensions (§8.5, ¶3)

§8.5 lists the measured dimensions as a **separate** ten-item list from the attribution stages. The
two lists are not the same list and P2 does not merge them. Each row records §8.5's question
verbatim as the assertion's meaning.

| # | `dimension` | §8.5 question | subject of the assertion | producing part | plan-scoped? |
|---|---|---|---|---|---|
| 1 | `extraction` | "Did the expected text, metadata, table values, OCR text, or image facts appear?" | (content hash, extractor id) | P5 | no |
| 2 | `fact` | "Did the system create the correct direct and validated facts? Did it abstain when evidence was absent?" | (file, field) | P6 | no |
| 3 | `retrieval` | "For sparse files, did the correct anchors appear in the top candidate neighborhood?" | (seed file) | P9 | no |
| 4 | `graph` | "Did edges reflect meaningful typed relationships? Did generic hubs create false neighborhoods?" | (neighbourhood) | P9 | no |
| 5 | `llm_grounding` | "Did every cited excerpt exist? Did the model return unknown when evidence was insufficient?" | (model call) | P8 | no |
| 6 | `grouping` | "Did candidate groups include correct members, exclude outliers, and identify purpose correctly?" | (candidate group) | P9 | yes |
| 7 | `template` | "Did a template generate useful real branches without needless depth?" | (template application to a branch) | P10 | yes |
| 8 | `tree` | "Did users accept, rename, merge, split, or reject proposed branches?" | (proposed branch) | P10 | yes |
| 9 | `placement` | "Did the engine choose the correct frozen node, an appropriate shallow fallback, or abstain?" | (file or accepted group) | P11 | yes |
| 10 | `residual` | "Did the system avoid inventing associations for isolated files?" | (residual file) | P11 | yes |

Two asymmetries between the lists are stated as found, not resolved: `factual_validation` and
`candidate_node_retrieval` are attribution stages with no same-named dimension, and `residual` is a
dimension with no same-named attribution stage. See Open question 1.

Dimension 8 (`tree`) is phrased by §8.5 as an observation of what users did, not as a correctness
check against an expectation. Its recorded outcome is a distribution over the five verbs §8.5 names
— accept, rename, merge, split, reject — sourced from §8.7 correction records. See Open question 4.

Dimension 9 (`placement`) has three legal correct outcomes, not one: the correct frozen node
(§6.11), an appropriate shallow fallback — an approved shallower path or an approved scoped
`General` node (§6.7, §5.9) — or abstention (§6.10).

### 3. Replay bundle

Bundle contents are exactly §8.5's list: "a frozen corpus snapshot or a metadata-safe
representation of one, content hashes, extraction outputs, expected facts, accepted groups, tree
versions, policy settings, and expected placement or abstention outcomes."

```text
bundle_manifest
  bundle_id
  created_at
  corpus_form               snapshot | metadata_safe                        §8.5
                            **metadata_safe does not round-trip file identity**
                            (ratified 2026-08-20). It carries hashes but no bytes,
                            and P1 records a `files` row only by hashing bytes it
                            opened (R1) — so a metadata_safe replay reproduces
                            exclusion verdicts, cache verdicts and curation signals,
                            and writes no `files` row. The alternative was a P1
                            entry point that records identity from a supplied hash,
                            rejected because a second way to mint identity is how R1
                            stops being a single rule.
  source_scan_ref           P3's published `scan_run_id` (P3 OQ16, closed
                            2026-08-20). Before it closed this was an opaque handle
                            P2 stored and never joined on.                    §1.1
  pinned_plan_version       plan id + version                                §8.5 "tree versions", §8.8
  policy_settings                                                            §8.5
    privacy_mode            one of the four §8.4 operation modes
    placement_policy                                                         §8.8
    budget_ceilings         the §8.6 ceiling set in force
  supersedes_bundle_id      nullable; a rebuilt bundle supersedes, never overwrites   §8.2

bundle_file_entry[]
  file_id                                                                    §8.2
  content_hash + hash_algorithm                                              §8.2, §8.5
  handling_class            one of the five §8.4 classes
  body                      payload_ref (corpus_form=snapshot)
                          | metadata_only (corpus_form=metadata_safe)        §8.5

bundle_extraction_output[]  opaque observation payloads, keyed by content hash + extractor version   §8.5, §2.8, §3.4
bundle_extraction_run[]     P4's `extraction_runs` rows for those outputs — the run half of §8.5's
                            "extraction outputs": run_id, file_id, content_hash, extractor name and
                            version, source_type, config_fingerprint, completeness, coverage,
                            observation_count. Read exactly as P4 publishes them; P2 defines
                            none of it.                                               §8.5, §2.7, §8.6
bundle_text_unit[]          P4's `text_units` rows for those same runs — the text half of §8.5's
                            "extraction outputs": run_id, container_path, unit_locator, text,
                            length, truncated. Read exactly as P4 publishes them (P4 D12, G1).
                            Populated when corpus_form = snapshot; whether a metadata_safe bundle
                            may carry them is the export rule P2 does not define — see Open
                            question 5.                                      §8.5, §2.2, §2.4, §2.7
bundle_learning_record[]    P1 `learning_records` rows needed for SR6 /
                            USER_REJECTED_EQUIVALENT fixtures — scope, subject_id,
                            proposal_class, basis_key, polarity, evidence refs.
                            Without these, a store-populated run and a store-empty run
                            compare as a grouping regression when the cause is a missing
                            negative example ([`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)).
bundle_accepted_group[]     accepted groups as of the pinned plan version — resolved through P9's
                            per-version `group_acceptance` record, since the group and membership
                            records themselves are shared across plan versions      §8.5, §8.8, §5.12

bundle_expectation[]        the expected side of every assertion
  dimension                 one of the ten
  subject_ref
  expected_value            for `fact`: field + value + reliability state (§3.13)
                            for `placement`: node id | shallow-fallback node id | abstain (§8.5, §6.7, §6.10)
                            for `residual`: P11's `outcome` value plus its qualifier field —
                              `place`               + `destination.node_role` = residual
                                                       (§7.7 action 3, the approved residual node)
                                                    | `destination.node_role` = ordinary with a
                                                       non-empty `decision_depth.unsupported_levels[]`
                                                       (§7.7 action 4, the approved broad parent)
                              `return_to_placement` + `return_target.kind` ∈ confirmed_domain_group
                                                       | accepted_graph_or_purpose_packet
                              `mark_review_later`
                              `leave_in_place`
                              `mark_state`          + `marked_state` ∈ protected | unsupported
                              `abstain`             + `abstention_reason`
                                                                       (§7.7's eight actions, §7.9)
  expected_outcome_kind     produced | abstained | not-applicable
  source                    hand-labelled | captured-from-accepted-user-decision
```

**Why the run rows and the text rows are in the list.** P4 splits the extraction outcome into three
records — the observation (`evidence`), the run (`extraction_runs`, P4's D5) and the bulk text
(`text_units`, P4's D12) — so a bundle carrying only the observations carries one third of §8.5's
"extraction outputs", and can say nothing at all about a file whose run produced none.
`completeness` and `coverage` exist only on the run row, and P2's two §8.6 obligations are computed
from them: the count line — "1,842 files indexed" (the `bundle_file_entry[]` count), "1,611 fully
extracted" (files every one of whose runs over the current content hash is `complete`), "89 scanned
PDFs deferred after the OCR limit" (runs at `completeness = deferred` **or** `capped`, with
`coverage` saying how far the read got), "18 files remain unreadable" (runs at
`completeness = unreadable` **or** `failed`) — these four are P5's published mappings, adopted
verbatim rather than restated differently — and adversarial case A9,
whose expected outcome *is* a `capped` run row with its `coverage`. Without `bundle_extraction_run[]`
the bundle cannot reproduce the counts it exists to verify, and A9 has nothing to assert against.
§8.6's fifth count, "34 files require model review", is a review-state count rather than an
extraction outcome and is not derived from these rows.

**Why the text rows are in the list** (N-3). Dimension 1 is §8.5's *"Did the expected text,
metadata, table values, OCR text, or image facts appear?"* After P4's D12 the text is not on the
observation — an observation is a *located value*, and `text_units` is the unit it points into, which
P4 rule 6 also makes the only home for §8.4's always-local *"complete extracted text"*. Without
`bundle_text_unit[]` the first of P2's ten dimensions has nothing to query, and a `capped` OCR run's
recovered text — exactly what a version-to-version comparison of a new OCR engine must diff — is
absent from the bundle. P4's claim that *"§8.5's 'Did the expected text appear?' is a query against
`text_units`"* is therefore accepted, not withdrawn.

**Keying, deliberately divergent from P4.** `bundle_extraction_output[]` is keyed by content hash
**plus extractor version** so one bundle can hold two versions' outputs side by side for a diff,
while P4's `observation_key` deliberately **excludes** the version so a citation recorded today
still resolves after an extractor upgrade (§8.7) — the two serve the same replay goal from opposite
ends, and neither should later be "fixed" into agreement with the other.

The `residual` expectation is P11's published `outcome` vocabulary, not a P2 vocabulary.

**The qualifier on `place` is P10's `node_role`, carried verbatim by P11 — there is no
`destination.kind`** (MINOR 6): two vocabularies for one concept is what M7 forbids, and
`approved_residual` and `approved_parent` are not members of `node_role`
(`ordinary | scoped-general | residual | shared-material`). §7.7's approved residual destination is
`node_role = residual`; its approved broad parent is `node_role = ordinary` with a non-empty
`decision_depth.unsupported_levels[]` naming the levels deliberately left unfilled (§6.7). P2 quotes
P11's own mapping table and defines nothing.

The earlier four-value form (approved residual node / leave-in-place / review-later / abstain)
expressed **four** of §7.7's **eight** actions. The two most consequential omissions were §7.9's
hand-back loop —
*"if the LLM finds a credible connection to an accepted project, course, application, photo event, or
career group, the file should be returned to the standard node-aware placement engine rather than
being trapped in a generic residual folder"* — which is the mechanism P11 fuses §6 and §7 to provide.
Without `return_to_placement` and its `return_target.kind`, dimension 10 could not record the
expected outcome for §7.8's own worked example: the screenshot reading *"Your Columbia University
application has been submitted"*, whose correct outcome is retrieval of the accepted Columbia
application group and a **return to placement**, not a residual destination.

`ask_user` is absent by design, not by omission: P11 emits it only on the placement path under §6.9,
and closes the residual path to it. A `return_to_placement` expectation is satisfied by the residual
decision that hands the file back; the subsequent placement decision (P11's `returned_from`) is a
separate subject and is asserted under dimension 9.

A bundle is immutable once created. A bundle rebuilt under a new plan version is a **new** bundle
that supersedes the old, retaining the old (§8.2 supersede-never-overwrite; §8.8 "a new plan should
never silently reclassify or move old files").

`corpus_form` is declared per bundle and `handling_class` is recorded per entry, so that P7's §8.4
policy can be applied to a bundle without P2 deciding it. P2 does not define the export rule; see
Open question 5.

### 4. Stage output envelope

The one record every measured part emits. P2 owns the envelope; the producing part owns `payload`.

```text
stage_output
  run_id
  stage_id             one of the ten                                        §8.5
  subject_ref          content hash | group id | node id | branch id | model-call id | plan-version id
  outcome              produced | abstained | deferred | not_implemented | error   §8.5, §8.6
  payload              opaque to P2; shape owned by the producing part       §2.8 for extraction
  version_tuple_ref                                                          §8.5, §3.4
  inputs[]             subject_refs of the stage outputs consumed            (attribution; see Contract in B5)
  budget_state         within_ceiling | ceiling_reached                      §8.6
  produced_at
```

`not_implemented` exists so the harness is runnable before the stages exist
(`02-segmentation-map.md`, *Order*). A run in which nine stages report `not_implemented` is a valid
run with nine `not-run` assertion verdicts, not a failure.

### 5. Run manifest

```text
run_manifest
  run_id
  bundle_id
  run_kind             replay | shadow | adversarial                         §8.5
  version_tuple                                                              §8.5, §3.4
    extractor_versions{}
    graph_algorithm_version
    prompt_fingerprint
    model_identifier
    template_library_version
    placement_scorer_version
    analysis_tiers_enabled[]  subset of filesystem | native | ocr | llm      §3.4, I4
  budget_ceilings      the §8.6 ceilings this run was given
  run_settings         independent stage disables — NOT version axes:
                       model_enabled, embeddings_enabled                     §8.5, §0
  pinned_plan_version                                                        §8.8
  started_at / finished_at
```

The six axes in `version_tuple` are exactly the six things §8.5 says a bundle may be re-processed
by. Two runs are only comparable when they were given the same `budget_ceilings`; a comparison
across different ceilings must be labelled, because deferral changes outputs (§8.6).

`run_settings` is separate from `version_tuple` because a disable changes *which stages ran*, not
*which version produced them*. Two are required. §8.5's stage decomposition asks retrieval quality
and LLM grounding as separate questions, so a bundle must be re-runnable with the model disabled and
with embeddings disabled, **independently**. Embeddings ship in v1 — P9 computes them, P1 stores them
as §0's compact local arrays — and `embeddings_enabled = false` is the run that makes P9's equivalence
obligation checkable: a group accepted with embeddings on that is not also reachable from a direct
anchor with embeddings off is a defect, because *"embeddings never establish the group by
themselves"* (§4.2). The walking skeleton runs with both disabled.

### 6. Per-stage assertion record

```text
assertion
  run_id
  dimension            one of the ten                                        §8.5
  subject_ref
  expected             from bundle_expectation
  observed             from stage_output
  verdict              match
                     | divergent
                     | abstained_correctly        evidence was absent and the stage abstained   §8.5, §6.10
                     | abstained_incorrectly      evidence was present and the stage abstained
                     | asserted_incorrectly       the stage produced where it should have abstained
                     | deferred                   budget, not quality                            §8.6
                     | not_run                    stage reported not_implemented
  attributed_stage     the earliest stage on this subject's inputs[] chain whose own
                       assertion verdict is divergent / asserted_incorrectly                     §8.5
  evidence_ref         the observation, citation, or event that supports or fails the verdict;
                       a P4 observation is referenced by `observation_key`, never `observation_id`  §8.2, §8.7
```

`attributed_stage` is the mechanism for §8.5's "identify whether the error **began** with…". For a
wrong terminal outcome it names exactly one of the ten stages.

### 7. Comparison record

```text
comparison
  baseline_run_id
  candidate_run_id
  bundle_id
  version_tuple_delta        which of the six §8.5 axes differ
  per_dimension[]            one block per dimension, never collapsed
    dimension
    newly_matching[]         subject_refs
    newly_divergent[]        subject_refs
    unchanged_count
    deferral_changed[]       subject_refs where budget_state changed          §8.6
    attribution_histogram    attributed_stage → count                          §8.5
  disagreements[]            subject_ref, baseline verdict, candidate verdict, attributed_stage
```

**The comparison record has no aggregate accuracy field, and the report renderer must not compute
one.** §8.5: "A single overall 'accuracy' number hides the mechanism that needs repair." This is a
negative acceptance test, not a style preference — see *Done means*.

### 8. Shadow mode

§8.5: "A new model or algorithm can generate parallel recommendations without changing the
user-visible tree or move plan. The product can compare old and new outputs, identify
disagreements, and surface only selected examples for human review."

```text
shadow_run                   run_manifest with run_kind = shadow, plus:
  shadow_namespace           all outputs written here
  plan_version_writes        MUST be empty                                    §8.8, §8.5
  move_plan_entries          MUST be empty                                    §8.3, §8.5
  user_visible_tree_delta    MUST be empty                                    §8.5
  disagreement_set[]         comparison.disagreements against the live run
  surfaced_examples[]        the selected subset shown for human review       §8.5
  review_adjudication[]      reviewer verdict per surfaced example
  model_call_audit_refs[]    every model call this run made                   §8.4
```

Two constraints follow from other sections and are stated here because they bind P2's surface:

- A shadow model call is still a model call. It is gated by P7 before content reaches the model and
  is recorded in the consent-aware audit record with the authorizing policy, sensitivity, included
  excerpts, redaction, model, and prompt fingerprint (§8.4).
- Shadow disagreements are surfaced **selectively** (§8.5), not as a full diff dumped on the user.
  What "selected" means is P2's to implement; the selection criterion is not settled by the design.

### 9. Adversarial test suite

§8.5 requires "a small adversarial test suite containing the failure modes already observed in real
corpora," and gates on it: "Every new extractor, model, prompt, or graph mechanism should run
against this suite before it affects a user's live plan."

Twelve cases, exactly as §8.5 names them. Each is a fixture plus an expected and a forbidden
outcome, and each names the § that states the correct behaviour.

| # | Case (§8.5 wording) | Attacks | Expected outcome | Forbidden outcome | § |
|---|---|---|---|---|---|
| A1 | `MIT` inside "submit" | facet matching | no `MIT` facet is created | a school/institution facet from a substring hit | §3.7 word-boundary matching |
| A2 | `UNC` inside "uncertainty" | facet matching | no `UNC` facet is created | as above | §3.7 |
| A3 | course-code patterns that are actually ZIP codes **or** device models (at least two fixtures, one of each) | rule-validated facts | abstain: no course fact without academic context | a `course` fact from the pattern alone | §3.5 (pattern **plus** "syllabus", "lecture", "credits", "instructor", "semester"), §3.10 |
| A4 | generic author metadata (`python-docx`, `Mozilla/5.0`, browser producer strings) | metadata trust | metadata retained as supporting evidence only | a facet, group, or destination dimension keyed on creator identity | §2.2, §2.3, §3.8 ("avoid using authorship or creator identity as a destination dimension") |
| A5 | multiple institutions in one application essay | roles vs entity types | `authored_by` and `target_school` kept as distinct facets; abstain if the role is undecidable | one institution silently chosen; the packet absorbing a conflicting target institution | §3.8, §4.8, §4.9 ("a university name alone should not create a group") |
| A6 | duplicate suffixes on unrelated files | family detection, collision policy | not merged into a duplicate or version family | dedup or merge from a filename match | §8.3 ("a content-hash match supports deduplication review; a filename match alone does not") |
| A7 | stripped EXIF on messaging-app photographs | screenshot detection | not classified as a screenshot; abstain on conflicting signals | absence of EXIF treated as proof of screenshot | §2.6 |
| A8 | screenshots with unreadable OCR | residual interpretation | labelled generic screenshot / unresolved image; leave in place or an approved Screenshot Inbox | an invented association or narrative | §7.8, §7.9 |
| A9 | long scanned books | OCR budget | the read stops at §2.7's page and time limits and P4's `extraction_runs` row records `completeness = capped` with its `coverage {units, processed, total}` — P4's word, not a third one | silent truncation, or a lower-quality automatic classification from the partial read | §2.7, §8.6, §2.9 |
| A10 | documents with corrupted text layers | extraction routing | targeted OCR fallback triggered because P6's published `no_usable_facts(file_id, content_hash)` read returns true over the stored evidence — the only condition that may trigger it | OCR triggered by a global language-quality heuristic; or the broken layer treated as a valid empty extraction | §2.2, §2.7, §2.4 |
| A11 | shared resumes across applications | multi-home placement | prefer an approved shared branch if one exists; otherwise abstain or ask for a primary home | one institution chosen arbitrarily | §6.9 |
| A12 | files that legitimately belong to more than one purpose group | multi-membership | both memberships preserved; placement resolves via the shared-material policy or abstains | one membership dropped to force a single home | §4.9, §3.11, §6.9 |

The suite is a **gate**, not a report: it runs before a new extractor, model, prompt, or graph
mechanism affects a user's live plan (§8.5). Whether the gate blocks or advises is not settled —
Open question 9.

Cases A1–A12 are enumerated here in full because §8.5 names them. The fixture bodies are authored
per case against the expected/forbidden outcomes above; they are not the hand-labelled reference
corpus, which is deferred below.

---

## Deferred — manual design required

Each item below is content that must be authored by hand. P2 defines the record that holds it and
invents none of it.

| Deferred | Defined by | Why P2 cannot author it |
|---|---|---|
| The 200–300 domain template library | §5.7 | P2 measures template quality (dimension 7) but the templates — allowed fact fields, detection signals, recommended dimensions, order, privacy rules, validation constraints — are hand-authored. §5.7 and §3.15 also state only the core domains exist at launch; expectations for dimension 7 can reference only templates that exist. |
| Domain fact-schema fields beyond §3.11's literal table | §3.11 | Dimension 2 expectations may name only the six domains and the fields §3.11 literally states (Academic, College applications, Research, Finance, Photos, Code). §3.11 anticipates "many specialized fields" but does not enumerate them. |
| Gazetteer contents | §3.7 | Cases A1/A2 assert §3.7's **word-boundary matching rule**, which is a matching behaviour and is fully specified. The validated gazetteer entries themselves are not. |
| Residual library contents beyond the nine §7.3 names | §7.3 | Dimension 10 expectations may reference the nine named templates plus whatever residual nodes the user approved into the frozen tree (§7.4). §7.3's user-defined residual areas are by definition user-authored. |
| The hand-labelled reference corpus | §8.5 | §8.5 requires a bundle to carry "expected facts" and "expected placement or abstention outcomes" but does not author them. The corpus selection, the labelling, and the per-subject expected values are hand work. P2 publishes `bundle_expectation`; it does not fill it. |

---

## Done means

1. A replay bundle can be built, stored, and re-run **without touching a live filesystem** (§8.5),
   in both `corpus_form` variants, with every field in §8.5's contents list present.
2. All ten §8.5 dimensions have a distinct assertion record. None is collapsed into another.
3. **No aggregate accuracy scalar exists anywhere in the output** — bundle, run, assertion,
   comparison, or rendered report. A test asserts its absence (§8.5).
4. Every wrong terminal outcome yields exactly one `attributed_stage` drawn from the ten §8.5
   stages (§8.5).
5. `abstained_correctly` is a passing verdict and is reported as such, not as a miss (§8.5, §6.10:
   "correct abstention is a successful outcome").
6. `deferred` is reported separately from `divergent` for every dimension, and a run whose only
   change is a lower budget ceiling produces zero new divergences (§8.6).
7. A run in which a stage reports `not_implemented` completes and yields `not_run` verdicts for
   that stage's dimension — the harness is runnable before the stages exist
   (`02-segmentation-map.md`, *Order*).
8. Two runs over one bundle differing in one of the six §8.5 version axes produce a comparison
   naming that axis, a per-dimension delta, and an attribution histogram (§8.5).
9. A shadow run produces a disagreement set and a surfaced-example set, with `plan_version_writes`,
   `move_plan_entries`, and `user_visible_tree_delta` all provably empty (§8.5, §8.3, §8.8), and
   every model call it made present in P7's audit record (§8.4).
10. All twelve adversarial cases A1–A12 have a fixture and a pass/fail assertion, and the suite runs
    as a gate before a new extractor, model, prompt, or graph mechanism affects a live plan (§8.5).
11. The walking-skeleton step passes: "the whole run replays from a bundle and asserts each stage's
    output" (`02-segmentation-map.md`, *The walking skeleton*), with the other nine stages absent or
    minimal, and with `model_enabled` and `embeddings_enabled` both false.
12. **Dimension 10 can express all eight of §7.7's actions.** Specifically, §7.8's worked example —
    the screenshot reading "Your Columbia University application has been submitted" — is
    representable as an expected outcome of `return_to_placement` with
    `return_target.kind = confirmed_domain_group`, and a run in which the file lands in a generic
    residual folder instead is `divergent`, not a match (§7.7, §7.8, §7.9).
13. **§8.6's count line is reproducible from the bundle alone.** Files indexed, fully extracted,
    deferred after the OCR limit, and unreadable are computed from `bundle_extraction_run[]`'s
    `completeness` and `coverage`, with no live filesystem present (§8.6, §8.5).

---

## Cross-cutting answers

### Provenance (§8.2)

**What P2 appends.** P2 appends no file-level provenance event — §8.2's enumerated event list is a
list of things that happen *to a file*, and evaluation does none of them. P2 appends run-scoped
records to its own store: `bundle_manifest`, `run_manifest`, `stage_output`, `assertion`,
`comparison`, `shadow_run`, and `review_adjudication`. Every model call made during a replay,
shadow, or adversarial run appends a consent-aware audit record through P7 (§8.4) — P2 does not
write that record, it requires it and links to it.

**What P2 never overwrites.** Three things.

- **The evidence record.** §8.2: "The product must never overwrite the evidence record merely
  because a later extractor or model produces a different answer." Replay reads evidence; its
  derived outputs are written to a run-scoped namespace, and shadow outputs to
  `shadow_namespace`. (Whether replay may write *any* derived evidence into the shared database is
  Open question 7.)
- **A prior run's results.** A re-run supersedes, retaining the earlier run and the `version_tuple`
  that produced it — the same supersede-never-overwrite discipline §8.2 applies to extraction
  results. This is what makes "compared against prior results" (§8.5) possible at all.
- **A bundle.** Bundles are immutable; a rebuild creates a new bundle with `supersedes_bundle_id`
  set.

Every `assertion` carries `evidence_ref`, so a verdict can be traced to the observation or event
that produced it (§8.2's reconstruction requirement). Where that reference is a P4 observation it is
the content-addressed `observation_key`, not the per-row `observation_id`: §8.7 requires a negative
example recorded today to still resolve after an extractor upgrade, and an upgraded extractor emits a
new row with a new `observation_id`. A bundle expectation cited by `observation_id` would decay
silently across exactly the version change §8.5 exists to measure.

### Budgets and degradation (§8.6)

**Ceilings P2 operates under.** A replay or shadow run executes real stages and is therefore bound
by the same §8.6 ceilings as a live run — maximum pages OCRed per file, OCR time per file and per
scan, image-analysis operations per scan, LLM calls per thousand files, model cost per scan,
dossier tokens per call, retrieved neighbours per target file, local graph neighbourhood size,
candidate cluster size, residual review batch size, folder proposals and depth. The run manifest
records the ceiling set it was given, because a comparison across different ceilings is not a
like-for-like comparison.

**P2's own ceilings.** Bundle count and bundle storage size (a `snapshot` bundle carries file
bytes); adversarial suite wall-clock; and — if the design settles it — a shadow-run model budget
separate from the live scan budget (Open question 8).

**What P2 does when a budget is exhausted.**

- A stage that defers is recorded with `outcome = deferred`, `budget_state = ceiling_reached`, and
  its assertion verdict is `deferred` — never `divergent`. §8.6: "cost exhaustion must never turn
  into lower-quality automatic classification"; scoring a deferral as a quality failure would
  create exactly that pressure.
- P2 never substitutes a cheaper approximation of an assertion. If P2's own budget is exhausted,
  the assertion is `not_run` and the report says so. A partial evaluation is reported as partial.
- Following §8.6's legibility requirement, a run reports completed versus deferred work per
  dimension, in the same spirit as its "1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs
  deferred after the OCR limit" example. Those counts are read off `bundle_extraction_run[]`'s
  `completeness` and `coverage`; P2 does not recompute them from the observations.

### Correction learning (§8.7)

**What P2 records.** One user action is P2's own: the reviewer's adjudication of a shadow
disagreement surfaced under §8.5. It is recorded as `review_adjudication` at **run scope** — it
judges a candidate algorithm, not a file. Promoting it into a live §8.7 correction would make the
shadow run change user-visible state, which is the one thing §8.5 says shadow mode must not do.
Whether such promotion is nonetheless permitted is Open question 10.

**What P2 consumes.** P2 reads §8.7 correction records, including their scope (file / group / node
/ template / domain / corpus), and reads the explicit **negative** records — rejected groups,
rejected destination matches, rejected labels, rejected residual recommendations — which §8.7
requires be stored with the evidence that produced them. These are the source for dimension 8
(`tree`: accept / rename / merge / split / reject) and contribute to dimensions 6, 9, and 10. P2
reads scope; it never assigns or widens it.

**Scope discipline.** A correction recorded at file scope is used as an expectation for that file
only. P2 must not generalise a file-scoped correction into a dimension-wide expectation — §8.7's
own example: one transcript belonging in a Columbia packet "should not teach the engine that all
transcripts belong there."

### Plan versioning (§8.8)

**Plan-version state.** A bundle pins exactly one plan version (`pinned_plan_version`), which
supplies §8.5's "tree versions" and "policy settings" and §8.8's destination tree and node
identifiers, node types, template versions and ordering, accepted and rejected group memberships,
labels and aliases, residual-library configuration, privacy and model-consent policies, placement
policy, and associated review decisions. Five of the ten dimensions — `grouping`, `template`,
`tree`, `placement`, `residual` — are meaningful only relative to that pinned version, and their
expectations move with it.

**Shared-evidence state.** The other five — `extraction`, `fact`, `retrieval`, `graph`,
`llm_grounding` — are keyed to content hash plus version tuple (§3.4) and are plan-version
independent, because §8.8 states "the evidence database remains shared across plan versions." An
extraction expectation survives a tree redesign unchanged.

**P2's own state** — bundles, runs, assertions, comparisons, shadow records — belongs to neither.
It is eval state, keyed by `run_id`, referencing a plan version without being part of one. A new
plan version does not invalidate a completed run; it makes the run's five plan-scoped dimensions
stale, which the report states rather than silently recomputing (§8.8: "a new plan should never
silently reclassify or move old files").

---

## Open questions

Each is something §8.5 or its neighbours leave unsettled. P2 does not answer them.

1. **The two ten-item lists do not match.** §8.5's attribution stages include `factual validation`
   and `candidate-node retrieval`, which have no same-named measured dimension; its measured
   dimensions include `Residual quality`, which has no attribution stage. Does §7 residual handling
   get its own attribution stage, and does §6.2 candidate-node retrieval get its own dimension?
   *Threatens P11, which owns both §6.2 and §7.*

2. **No thresholds anywhere.** §8.5 states no pass threshold, target rate, or regression tolerance
   for any dimension. What distinguishes a regression from run-to-run noise, and who sets it? Note
   §6.10's two-condition rule (minimum support **and** a margin over next-best) is a *placement*
   rule, not an eval threshold, and must not be borrowed as one.

3. **Attribution across subjects.** A wrong placement for file A can originate in a wrong fact on
   file B — §4.3's anchor mechanism means a sparse file's outcome depends on other files' stage
   outputs. Does earliest-divergence attribution follow `inputs[]` edges across subjects, or only
   within one subject's own chain? *Threatens P9 and P11, which must emit the cross-file edges if
   the answer is "across".*

4. **Is `tree` an assertion or an observation?** §8.5's tree-quality question — "Did users accept,
   rename, merge, split, or reject proposed branches?" — describes user behaviour, not correctness.
   Does it have a pass/fail verdict, and can it be evaluated in a bundle replay at all, given that
   it requires live user decisions? *Threatens P10.*

5. **May a bundle leave the device?** §8.5 offers "a metadata-safe representation" of the corpus,
   and §8.4 requires paths, full extracted text, OCR output, hashes, EXIF, and GPS to remain local.
   §8.4 governs model prompts and external connectors; a bundle export is literally neither. May a
   metadata-safe bundle containing protected-class entries be exported for team-side regression
   runs, and under which of §8.4's four operation modes? What exactly does "metadata-safe" exclude?
   *Threatens P7.*

6. **No attribution stage for scan, privacy, or apply.** An error caused by an §1.1 exclusion rule
   (a file never scanned), by the §8.4 gate blocking a model call, or by an §8.3 stale-plan
   rejection has no home in §8.5's ten stages. Are these out of scope for stage attribution, or a
   gap? *Threatens P3, P7, P12.*

7. **May replay write to the shared evidence database?** §8.5 forbids changing the user-visible
   tree or move plan and is silent on evidence writes; §8.8 says the evidence database is shared
   across plan versions. Must all replay-derived output live in a run-scoped namespace, or may a
   replay contribute evidence?

8. **Does shadow mode get its own budget?** §8.6's ceiling list has no shadow entry, yet a shadow
   run roughly doubles model spend against "maximum LLM calls per thousand files" and "maximum
   model cost per scan."

9. **Is the adversarial gate blocking or advisory?** §8.5 says a new mechanism "should run against
   this suite before it affects a user's live plan." Does a failing case block the change, and is
   the gate enforced by P2 or by the release process?

10. **Can a shadow adjudication become an §8.7 correction?** A reviewer judging a surfaced shadow
    disagreement is expressing a real preference. Promoting it would give shadow mode a path into
    user-visible state; discarding it wastes the signal. §8.5 and §8.7 do not connect.

11. **Reproducibility of a run.** §8.5's comparison assumes that re-running one bundle under one
    version tuple is meaningful, but §3.4's cache key pins model identifier and prompt fingerprint
    and says nothing about sampling parameters. Is a run required to be reproducible, and by what
    mechanism? Without an answer, `newly_divergent` cannot be distinguished from model sampling
    variance. *Threatens P8.*

12. **By what criterion are shadow examples selected?** §8.5 says shadow mode surfaces "only
    selected examples for human review" and states no criterion. *Partly settled:* the surface
    itself exists — §8.5's user-facing evaluation view is P13's, so "the engineering team **and the
    user**" both have a consumer for P2's records, and P2 renders none of it itself. What P2 still
    cannot answer is which disagreements are worth a human's attention.
