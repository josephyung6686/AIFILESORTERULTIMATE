# P9 — Grouping

Owns: §4
Status: contract draft

## Purpose

P9 turns validated facts and a bounded local evidence graph into **candidate groups**, hands each one
as a limited dossier to the LLM harness, and publishes **accepted groups** plus **membership records
that distinguish direct-anchor membership from context-supported membership** (§4.3, §4.8).

Three prohibitions define the part more than any capability does:

- The LLM is **not** an autonomous clustering engine. It never receives a large folder and invents
  categories. Its role begins only after the rules engine and the local evidence graph have produced a
  candidate group **with an explicit reason for existing** (§4.1).
- The graph is **context assembly, not label propagation**. It does not copy a missing fact from a rich
  file onto a sparse one (§4.1, §4.3).
- **Embeddings never establish a group by themselves.** A semantic neighbour is only a file worth
  bringing into the evidence packet (§4.2). P9 **computes** the embeddings and P1 stores them as §0's
  compact local arrays; owning them changes nothing about this rule. They buy retrieval reach — the
  ability to find `HW 3.pdf`, which lacks the course code but resembles the lecture notes — and never
  establishment. §6.5 states the same bar downstream: *"a semantic embedding alone is insufficient."*

The output is a transparent, reviewable candidate membership — "`HW 3.pdf` may belong to the PHYS1401
course-material group, supported by two direct course anchors, compatible homework structure, and
mutual retrieval with related course documents" — not a course fact written onto `HW 3.pdf` (§4.3, §4.6).

## Design slice owned

| § | What P9 owns |
|---|---|
| §4.1 | The division of labour: rules supply hard facts and domain information; the graph locates files that may supply missing context; the LLM reviews a limited dossier |
| §4.2 | The four seed kinds, the six retrieval channels, the small ranked neighbour set, pre-model outlier flagging; **the computation of the local embeddings behind the sixth channel** (§0, §4.2 — P9 computes, P1 stores) |
| §4.3 | Bounded group evidence packet separating direct anchors from context-supported members; pre-model rule computations; generic-hub suppression |
| §4.4 | The candidate group dossier record — the actual model input |
| §4.5 | The four constrained tasks and the shape of the structured, evidence-citing response P9 requires |
| §4.6 | The worked example as a golden fixture and behavioural assertion |
| §4.7 | Purpose detection as a purpose packet built from measurable clues, not an open question to the model |
| §4.8 | **Group-level** validation assertions and the context-supported outcome; the separate logging of retrieval / interpretation / label failure |
| §4.9 | The six stop rules and the five accompanying constraints |
| §4.10 | The five-step pipeline and the seams between rules, graph, model, validator, user |

**Not owned, consumed instead.** §4.8's *validator mechanism* belongs to P8 (§3.3, §3.6, §4.8, §6.10,
§7.9 are one mechanism — bounded dossier, cited response, deterministic validator, accept/reject/abstain).
P9 states **what** group-level validation must check and passes those assertions to P8; it does not
implement a second validator. P9 likewise owns no fact schema (§3.11, P6), no privacy classification
(§8.4, P7), no template (§5, P10), and no destination node (§5.12, P10).

## Contract in

Each entry states the minimum P9 reads, so the producing part can publish a fixture that satisfies P9
before P9 exists.

**From P1 — storage, identity, provenance (§0, §8.2).**
Content hash as the stable identity of a file version; internal file ID; current path and path history;
the append-only event log P9 writes into; supersede-never-overwrite semantics. Group and membership
records key on `file_id` + `content_hash` together, because a content change is a new file version and
invalidates a membership's evidence (§8.2). **Vector storage**: P1 persists the embeddings P9 computes
as §0's compact local arrays — *"separately as compact local arrays … because a vector database would
add complexity without material value at the initial scale"* — keyed by `content_hash` so a content
change invalidates the vector with the rest of the file version's evidence (§0, §8.2).

**From P3 — scan and corpus selection (§1.1, §1.2).**
Corpus membership and exclusion outcome; directory position and parent-folder context; existing folder
structure. §4.2's *"files from an existing related folder"* retrieval channel and §4.9's requirement
that a curated user folder expresses intent both read this. Excluded directories (§1.1) never seed and
never enter a neighbourhood.

**From P4 / P5 — evidence shape and extractors (§2.8, §2.1–2.7, §2.9).**
Observations in the one frozen shape, each carrying source type, raw value, normalized candidate,
**location**, `context_before` / `context_after` / `context_truncated` (P4's three-field split of
§2.8's single "surrounding context" line, so a value can be redacted without dropping its context per
§8.4), occurrence count and reliability state, and both identifiers — `observation_id` per row and the
content-addressed **`observation_key`**. P9 cites `observation_key`, because a dossier excerpt must be
resolvable back to a stored observation for citation checking (§4.4, §4.8) and must survive an
extractor upgrade (§8.7), and
because positional weight distinguishes a page-one heading from a page-eighteen reference (§2.2, §3.7).
Unreadable / indexed-but-unreadable state (§2.9) drives the §4.9 unreadable-file constraint.

**From P6 — facts and facets (§3.1–3.14).**
`fields` / `values` / `file_facts` with the six reliability states (§3.13). Specifically:
seed and anchor facts must be `Direct` or `Validated`; a `Possible` clue such as bounded-session
membership may pull a file into a packet but can never anchor it (§3.9, §3.13, §4.2, §4.7).
Universal facts including duplicate family, version family and sensitivity status (§3.11) supply the
duplicate/version retrieval channel (§4.2). Domain-scoped schemas (§3.11) bound which facts may appear
in a dossier and which labels are legal (§3.5: the model may not invent a schema or field).
The `purpose` facet (§3.9) is a first-class input to §4.7.
Two further P6 outputs close channels P9 could not previously source: the **bounded download session**,
computed by P6 from P3's timestamps and emitted as a `possible` fact only (§3.9, §3.13), which is
§4.2's fifth retrieval channel and never an anchor; and the **photo `event` fact**, clustered
deterministically by P6 from camera, time and GPS metadata (§3.11, §2.6), which is §4.2's fourth seed
kind.

**From P7 — privacy and consent gate (§8.4).**
Handling class per file, active operation mode, and the redaction decision — applied **before** any
dossier content reaches a model or external connector (§8.4). P9 treats P7's verdict as binding: a
protected record contributes to grouping locally but its raw content, and by default its filename, do
not enter a cloud dossier or a general group summary (§8.4). §4.9's sensitive-file constraint is
executed jointly with P7 (see Open question 9).

**From P8 — LLM harness and validator (§3.3, §3.6, §4.5, §4.8).**
P9 submits a dossier and receives (a) a structured, evidence-citing response covering the four §4.5
tasks and (b) a per-claim validation verdict. **P9 publishes no verdict enum of its own; it consumes
P8's `Verdict` record directly** — `outcome ∈ accept_direct | accept_context_supported | weak | reject
| abstain`, plus `reasons[]`, `may_propose`, `requires_review` and `citations_checked[]`. §4.8's
central distinction survives intact: `accept_direct` is the valid-on-direct-evidence outcome that may
be accepted, `accept_context_supported` is the valid-but-context-supported outcome that must go to
user review, and P8 sets `requires_review: true` on every one of them. P9 also requires `unknown` /
abstention to be a first-class response, not an error (§3.3, §3.6, §4.3) — P8's `abstain`.

**From P2 — eval and replay harness (§8.5).**
Replay-bundle inputs and shadow-mode execution. P9 must be runnable from a bundle with the model
disabled and with embeddings disabled, independently — P2's `run_manifest.run_settings`
(`model_enabled`, `embeddings_enabled`) — so that retrieval quality, graph quality, LLM grounding and
grouping quality can be measured as separate stages (§8.5).

**From the user.**
Accept, reject, rename, merge, split, exclude-one-member, manually attach (§4.9, §8.7).

**From P13 — collected group changes (§4, §7.10).**
Those gestures reach P9 as P13's `review_action` in full, collected on `surface = group_plan` with
`subject_ref` a `group_plan_id`, and carrying `plan_version`, `action`, `bulk_member_refs[]`,
`bulk_basis`, `correction_scope` (§8.7) and `presented_state_ref`. P13 presents and collects; it
decides nothing. **P9 authors the group accept, reject or membership decision each action produces**
(M8) and P1 writes the event.

## Contract out

Nine numbered items. Groups, memberships, dossiers, typed edges and vectors are **shared evidence**
and carry **no** `plan_version_id` — §8.8 keeps the evidence database shared across plan versions and
§5.12 keeps accepted groups separate from the tree. Exactly one record is plan-versioned:
`group_acceptance` (8), which holds nothing but the acceptance, review and user-label state §8.8
places inside a plan version. `superseded_by` marks records that are replaced but never overwritten
(§8.2).

**Emits P2 `stage_output`** with `stage_id ∈ retrieval` (§4.2), `graph_construction` (§4.3) and
`grouping` (§4) — one per subject P9 decides about — each carrying `inputs[]`, an explicit abstention
value, a distinct budget-deferral value, and the version tuple (§8.5). All three are members of P2's
closed ten; P9 emits no fourth id and never the part name.

**P9's result → the envelope's vocabulary.** `stage_output.outcome` is P2's five-value enumeration and
is not any of P9's own vocabularies — not `Group.state`, not `coherence_verdict`, not the stop-rule
record's `outcome`. This table is the only mapping between them, and it applies per `stage_id`:

| P9 result | `stage_output.outcome` | `budget_state` |
|---|---|---|
| the stage wrote its record — neighbours retrieved (`retrieval`), typed edges written (`graph_construction`), a `Group` with its memberships (`grouping`) | `produced` | `within_ceiling` |
| an evidence-based refusal — a §4.9 stop rule fired (stop-rule `outcome ∈ no-group \| tentative-discovery`), `coherence_verdict = abstained`, or retrieval found no plausible anchor | `abstained` | `within_ceiling` |
| an §8.6 ceiling stopped the work — the group stays `candidate` with its anchor memberships intact and **no** `coherence_verdict` and **no** `display_label` | `deferred` | `ceiling_reached` |
| the stage failed | `error` | — |
| P9 not built yet | `not_implemented` | — |

The second and third rows are why the table exists. A stop-rule refusal is `abstained` and a ceiling
is `deferred`; neither ever takes the other's value, and `ceiling_reached` appears on the third row
and on no other. P2's Done-means 6 — a run whose only change is a lower budget ceiling produces zero
new divergences — is unsatisfiable if a deferral arrives as an abstention.

### 1. Group

```text
group_id
seed_ref, seed_kind          strongly-identified-file | validated-shared-fact |
                             structural-family | user-created-starting-point            (§4.2)
proposed_basis               the explicit reason this group exists, written by the
                             engine BEFORE the model sees anything                      (§4.1, §4.4)
anchor_facts[]               {field, value, file_ids[], reliability_state,
                             observation_key}                                            (§4.2, §8.7)
pre_model_signals            rule computations run before the dossier is assembled:
                             independent anchor count for the same value; presence of a
                             defining document type in the neighbourhood; compatibility
                             of work types and term evidence; detected conflicting
                             codes; suppressed generic hubs                             (§4.3)
anchor_count                 number of files that INDEPENDENTLY state the basis value   (§4.3)
coherence_verdict            coherent | not-coherent | abstained                        (§4.5 task 1)
coherence_citations[]        evidence refs supporting the verdict                       (§4.5)
group_category               the §3.11 / §3.15 DOMAIN vocabulary — not a second enum;
                             set only when coherence_verdict = coherent                 (§4.5 task 4, §3.15)
display_label                the engine or model proposal; set only when
                             coherence_verdict = coherent. A user-edited label is
                             plan-versioned and lives in group_acceptance (8)            (§4.5 task 4, §8.8)
label_source                 engine | llm-proposed | user-edited                        (§4.5, §8.7)
conflicts[]                  {kind, competing_values, file_ids[]}                       (§4.3, §4.4)
stop_rule_hits[]             SR1..SR6, empty if none fired                              (§4.9)
state                        candidate | supported | tentative-discovery | unresolved
                             — the SHARED engine lifecycle. `accepted` and `rejected`
                             are resolved AS OF a plan version from group_acceptance
                             (8), never stored here                                     (§4.8, §4.9, §5.1, §8.8)
sensitivity_state            from P7                                                    (§8.4)
dossier_id                   the dossier submitted, if any                              (§4.4)
llm_response_ref             P8 response, if any                                        (§4.5)
validation_verdict_ref       P8 verdict, if any                                         (§4.8)
created_by                   rules | rules+graph | user
created_at, superseded_by, supersede_reason                                             (§8.2)
```

`display_label` and `group_category` are **absent, not empty**, unless coherence holds — §4.5 makes the
label conditional on task 1. Example labels the design gives: `PHYS1401 — Spring 2026`,
`Columbia Application — 2026 Cycle`, `PVA/RDP — Manuscripts and Figures`, `EY Internship Application`
(§4.5). A group carries no folder path: the LLM "must not create a final folder hierarchy" (§4.5), and
groups stay separate from the destination tree (§5.12).

**`group_category` is the domain vocabulary, not a parallel one** (settles Open question 4). §4.5 asks
for "a group category" and enumerates none; §3.15's launch domains are the enumeration — academic
coursework, college applications, research and lab work, career and recruiting, photos and captures,
code projects. §4.5 task 1's organizing reasons ("one course, project, application, recruiting
process, photo event, or submission packet") are *instances* of those domains, not a second axis.
Consequence for P10, which aggregates accepted groups into branches by category (§5.1): the `domain`
and `category` it requests are **one field**, `group_category`, and the two fact-schema and
folder-template definitions §3.15 pairs per domain hang off the same value. `anchor_facts[]` is the
field P10 asks for under that name; it was `basis_facts[]` and is renamed here, not duplicated.

### 2. Membership

```text
membership_id
group_id, file_id, content_hash
basis                    direct-anchor | context-supported | user-attached              (§4.3, §4.8, §4.9)
decision                 included | excluded | uncertain                               (§4.5 task 2)
decision_source          rules | llm | validator | user                                (§4.1, §4.8, §8.7)
support[]                one or more {support_kind, observation_key, quote_or_field,
                         location, edge_ref}
                         support_kind ∈ shared-validated-fact | duplicate-or-version-link |
                         compatible-document-type | existing-related-folder |
                         bounded-session | mutual-semantic-retrieval                    (§4.2)
insufficient_evidence    boolean + the model's explicit statement, when it made one     (§4.5)
conflicts[]              conflicting course, institution, term, project, purpose or
                         document-type facts                                            (§4.5 task 3)
outlier_flag             engine-flagged | model-flagged | both | none                   (§4.2, §4.5 task 3)
validation_verdict_ref   the P8 Verdict for this membership. P9 publishes NO verdict
                         enum of its own: outcome ∈ accept_direct |
                         accept_context_supported | weak | reject | abstain,
                         plus reasons[], may_propose, requires_review                    (§4.8, P8)
review_state             resolved AS OF a plan version from group_acceptance (8) —
                         not stored here                                                (§4.8, §8.7, §8.8)
created_at, superseded_by, supersede_reason                                             (§8.2)
```

**Nothing is lost by dropping P9's verdict enum.** The five values P9 previously published are
recoverable as `(outcome, reason_code)` pairs over P8's registry, and the two P8 outcomes P9 had no
word for are gained:

| former P9 value | P8 `outcome` | P8 `reasons[]` |
|---|---|---|
| `valid-direct` | `accept_direct` | — |
| `valid-context-supported` | `accept_context_supported` | `CONTEXT_ONLY_SUPPORT` |
| `contradicted` | `reject` | `CONTRADICTED_BY_STRONGER` |
| `generic-similarity-only` | `reject` | `GENERIC_SIMILARITY_ONLY` |
| `unsupported` | `reject` | a citation-failure code — `UNCITED_CLAIM`, `CITATION_NOT_IN_DOSSIER`, `CITATION_NOT_FOUND`, `CITATION_SPAN_MISMATCH` |
| *(no P9 word)* | `weak` | non-contradicted but below the site's support bar; `may_propose: false`, so it may never become a folder proposal (§3.6) |
| *(no P9 word)* | `abstain` | the model returned `unknown`, or the harness refused to call (§3.3, §3.6) |

§4.8's central distinction — *valid on direct evidence* versus *valid but context-supported, therefore
routed to user review* — is carried by the `accept_direct` / `accept_context_supported` split, which
P8 makes decidable from the dossier's own direct/context marking rather than by judgement.

Invariants a consumer may rely on:

1. `basis = direct-anchor` requires at least one `support_kind = shared-validated-fact` resolving to a
   `Direct` or `Validated` fact on that file (§3.13, §4.3).
2. A membership whose support is only `mutual-semantic-retrieval` and/or `bounded-session` can never be
   `direct-anchor`, and can never by itself make a group `supported` (§4.2, §3.9, §4.9 SR2). See the
   embedding boundary in record 9.
3. `basis = context-supported` always requires review: P8 returns `accept_context_supported` with
   `requires_review: true`, and the membership opens at `review_state = pending-review` in every plan
   version's `group_acceptance` row until the user decides. §4.8 requires it to be sent to user review,
   never silently accepted.
4. A file may hold `included` memberships in **more than one accepted group** — the PVA/RDP abstract is
   both a Research artifact and a supporting document in a UChicago application packet (§4.9).
5. A file whose evidence is unreadable, encrypted, corrupted or of an unsupported format may only
   receive `basis = user-attached`. No purpose is inferred from its filename (§4.9).
6. Membership never writes a fact onto the member file. §4.3 is explicit: the output "does not directly
   create a course fact on `HW 3.pdf`". Any fact P6 later stores from a group conclusion is P6's
   LLM-supported fact under §3.5 / §3.6, produced through P8's validator, not a P9 side effect.

### 3. Candidate group dossier

The actual input to the LLM (§4.4). It **must not contain every file in full** — "a large, noisy prompt
encourages the model to find patterns that are not real" (§4.4).

```text
dossier_id, group_id
proposed_basis                                                                          (§4.4)
anchor_files[]           {file_id, content_hash, document_type, key_facts[], excerpts[]}
                         rich files carrying DIRECT evidence                            (§4.4)
candidate_files[]        context-supported candidates: same shape, plus why_retrieved
                         (which retrieval channel, which edges)                          (§4.4)
typed_edges[]            {from, to, edge_type, evidence_ref}                             (§4.4)
key_facts[]              {field, value, file_ids[], reliability_state}                   (§4.4)
excerpts[]               SHORT spans, each with location + observation_key               (§4.4, §2.8, §8.7)
conflicts[]                                                                              (§4.4)
engine_flagged_outliers[]  flagged BEFORE the model sees anything                        (§4.2)
omissions                what was withheld and why: budget cap, privacy redaction,
                         neighbourhood cap                                               (§8.4, §8.6)
privacy                  handling classes present, redactions applied, P7 decision ref   (§8.4)
budget                   token ceiling applied, neighbour cap applied, files dropped     (§8.6)
dossier_fingerprint      stable hash of the assembled dossier, for cache keying and
                         replay                                                          (§3.4, §8.5)
```

Hard constraints: `anchor_files` and `candidate_files` are **separate arrays and are never merged** —
"the dossier explicitly distinguishes direct evidence from inferred context… the LLM must be able to
say that a group is coherent while still marking particular members as uncertain" (§4.4). Every excerpt
must resolve to a stored observation by its `observation_key`, or P8 cannot verify the citation
(§4.8) — and a key that survives an extractor upgrade is what lets a rejected dossier still resolve as
a §8.7 negative example afterwards.

The two dossier shapes the design specifies by example are the **course dossier** and the **application
dossier** (§4.4); both are published as golden fixtures (see Done means).

### 4. Typed graph edge

```text
edge_id, from_file_id, to_file_id, edge_type, evidence_ref, weight?
edge_type ∈ shared-validated-fact | duplicate | version-family |
            compatible-document-type | existing-related-folder |
            bounded-session | mutual-semantic-retrieval                                 (§4.2, §4.3)
bridge_entity_ref        the entity this edge runs through, when it does
hub_suppressed           true when the bridging entity is a generic hub such as a
                         personal email address or a broad university domain            (§4.3, §4.9 SR3)
created_at, superseded_by                                                                (§8.2)
```

Edges are consumed by P11 for §6.3 retrieval and §6.5 node-local graph construction (see Open
question 5 on vocabulary alignment) and by P2 for §8.5 graph quality.

### 5. Stop-rule outcome

A group is **not formed as supported** when any rule fires (§4.9):

```text
SR1  no valid anchor
SR2  the graph is connected only by embeddings
SR3  one high-frequency entity acts as the only bridge
SR4  members carry irreconcilable course, institution, project, term or purpose facts
SR5  the LLM cannot explain the group with citations
SR6  the user has already rejected an equivalent proposal
```

Record: `{group_id, rules_fired[], evidence_refs[], outcome ∈ no-group | tentative-discovery}`. §4.9
permits a sparse anchorless group to be shown "only as tentative discovery candidates, **if at all**"
(see Open question 10).

Four further constraints ride with the stop rules and are asserted at group level:

- **A course code alone must not merge different semesters.** Course packet identity includes a term
  when a term is available (§4.9).
- **A university name alone must not create a group** — `Columbia` can be an authoring school, course
  provider, target institution, employer, research venue, or merely a cited organization (§4.9). This
  is the §3.8 role distinction applied to grouping.
- **Rare sensitive files may surface below a normal group-size threshold**, as protected records
  (§4.9, executed with P7 under §8.4).
- **Unreadable files keep metadata and stay manually attachable**, with no inferred purpose (§4.9).

### 6. Failure-point log

§4.8 is emphatic that a bad group can fail for three different reasons — the graph retrieved irrelevant
neighbours, the LLM overgeneralised from a good neighbourhood, or the label was simply not useful — and
that "the product must log and evaluate these failure points separately rather than treating all
mistakes as 'AI classification errors.'"

```text
{group_id, dossier_id, membership_id?,
 stage ∈ retrieval | graph | interpretation | validation | label | user-rejection,
 cause_code, evidence_ref,
 detected_by ∈ validator | user | replay}
```

Consumers must be able to compute §8.5's *Retrieval quality*, *Graph quality*, *LLM grounding* and
*Grouping quality* from this log without re-deriving which stage failed. Emitting a single collapsed
error class is a contract violation.

### 7. Pipeline position (§4.10)

```text
1  Rules find direct anchors and extract validated facts            P6 facts → P9 seeds
2  The graph retrieves complementary files, bounded neighbourhood   P9
3  The LLM evaluates coherence, purpose, membership, outliers,
   labels from an evidence dossier                                  P9 assembles → P8 executes
4  Deterministic validation checks every cited conclusion           P8 mechanism, P9 assertions
5  The user makes the final high-leverage decision                  P9 records the decision
```

### 8. Group acceptance (§8.8)

The **only** plan-versioned record P9 publishes. Groups, memberships, dossiers, edges and vectors live
in the shared evidence database and survive every plan version (§8.8: *"the evidence database remains
shared across plan versions"*; §5.12: facts and accepted groups stay separate from the tree). What a
plan version captures is §8.8's own phrase — "accepted and rejected group memberships" — which is a
*state about* those records, not the records themselves.

```text
acceptance_id
plan_version_id                                                                         (§8.8)
group_id
membership_id            null = the acceptance applies to the group as a whole          (§8.8)
acceptance               accepted | rejected | pending-review | deferred                (§4.8, §8.8)
review_state             not-required | pending-review | user-accepted | user-rejected |
                         user-excluded-from-packet | deferred                           (§4.8, §8.7)
user_edited_label        the user's label in THIS plan version; the engine or model
                         proposal stays on Group.display_label                          (§4.5, §8.7, §8.8)
aliases[]                                                                               (§8.8)
review_decision_ref                                                                     (§8.8)
decided_by               user | rules | validator                                       (§4.1, §4.8)
created_at, superseded_by, supersede_reason                                             (§8.2)
```

Why the split is not cosmetic:

- **Acceptance is per plan version, not global** (settles Open question 8). The same candidate group
  may be accepted in version 2 and rejected in version 3 with neither decision destroying the other,
  and without duplicating the group, its dossier, its model response, or a single line of its
  evidence. Carrying `plan_version_id` on `Group` would have forced exactly that duplication.
- §8.8's required diff — "N files now require renewed review because their previous destination no
  longer exists" — is a join of `group_acceptance` across two plan versions over one shared membership
  set.
- P10's freeze record entry *"Accepted and rejected group memberships — P9, referenced"* resolves to
  this record, for the version being frozen and no other (§8.8, §5.12).
- **The two derivations M12 gives P10 still hold, one of them through this record.**
  `excluded_members[]` from `Membership.decision = excluded` is unaffected — that decision is engine
  and model output, and is shared. `rejected_proposals[]` from `Group.state = rejected` resolves here:
  `Group.state` carries the shared lifecycle, and `rejected` is supplied by `group_acceptance` for the
  plan version P10 is freezing. A consumer reads `Group.state` **as of** a plan version, through the
  accessor below.
- The §8.7 negative-feedback store is **separate from and unaffected by** this record. A rejection is
  both an acceptance state in one plan version and a scoped learning record with its evidence; §4.9
  SR6 queries the learning record, so a rejection recorded under one plan version still stops the same
  attractive-but-incorrect grouping resurfacing under the next.

**The accessor that makes that derivation callable (S-7).** "As of a plan version" is a derived view,
not a stored field, so P9 publishes it as a call rather than leaving a consumer to look for `rejected`
in a `Group.state` enum that does not contain it:

```text
group_state_as_of(group_id, plan_version_id)
  -> candidate | supported | tentative-discovery | unresolved | accepted | rejected
```

Those six values are the exact set a consumer may receive, and they are the shape P10's
`rejected_proposals[]` derivation reads. The resolution rule: if a `group_acceptance` row exists for
this `(group_id, plan_version_id)` with `membership_id = null` and `acceptance ∈ accepted | rejected`,
that value is returned; otherwise the stored `Group.state` is returned unchanged. `pending-review` and
`deferred` acceptances are not returned — they are not lifecycle states, and the stored `Group.state`
still describes the group under them.

`Group.state` itself continues to store only the four shared-lifecycle values. The accessor adds the
two plan-versioned values at read time and stores nothing, which is what keeps M15 intact: acceptance
lives in `group_acceptance` and nowhere else (§8.8).

### 9. File embedding (§0, §4.2)

**P9 computes, P1 stores.** §4.2 and §6.3 both consume embeddings and §0 fixes the storage form, but
no § assigned the computation; this record is that assignment. Vectors are stored *"separately as
compact local arrays … because a vector database would add complexity without material value at the
initial scale"* (§0).

```text
content_hash             an embedding is a property of a file VERSION — a content change
                         invalidates it with the rest of that version's evidence        (§8.2, §3.4)
file_id
scope                    which text was embedded (extracted text, OCR text, or a bounded
                         excerpt set) — unauthored, see Deferred                        (§2.2, §2.7)
vector                   a compact local array held by P1; never a vector database      (§0)
embedding_model_id, embedding_version                                                   (§3.4, §8.5)
created_at, superseded_by                                                               (§8.2)
```

**The boundary, stated so that no later part can cross it.** Embeddings buy retrieval reach and
nothing else. §4.2: *"embeddings never establish the group by themselves. A semantic neighbour is
simply a file worth bringing into the evidence packet."*

1. A vector may produce exactly **two** things anywhere in P9's contract: a `mutual-semantic-retrieval`
   `support_kind` on `Membership.support[]`, and a `mutual-semantic-retrieval` `edge_type` on a typed
   edge. There is no third position, in this record or any other.
2. `anchor_facts[]`, `anchor_count`, `dossier.anchor_files[]` and `Membership.basis = direct-anchor`
   are each defined over `Direct` or `Validated` **facts** (§3.13, §4.3). A vector is not a fact and
   satisfies none of them. **No path exists by which a semantic neighbour becomes an anchor.**
3. SR2 fires when the graph is connected only by embeddings: no supported group forms, even when the
   model would call it coherent (§4.9, Done means 4).
4. Retrieval is **mutual** and bounded — §4.2's "small ranked set" of neighbours, with likely outliers
   flagged before the dossier reaches the model, because *"retrieval systems can introduce irrelevant
   context and increase unsupported conclusions when their context is too broad."*
5. §6.5 restates the same bar downstream for P11's node-local graph — *"a semantic embedding alone is
   insufficient"* and a target file *"connected only by generic similarity … must remain uncertain
   rather than being absorbed into an approved node."* P9 owning the vectors does not soften it.
6. Embeddings are **excluded from the walking skeleton**, which is deterministic by design. P2's
   `run_settings.embeddings_enabled = false` must still reproduce every group a direct anchor supports
   (Done means 1 and 5).

## Deferred — manual design required

Nothing below is invented here. Each names the § that defines it and the part that will author it.

| Deferred | Defined by | Note |
|---|---|---|
| The 200–300 domain-specific template library | §5.7 | P10's material. P9 consumes no template content; a group label is not a template name (§4.5 vs §5.4) |
| Domain fact-schema fields beyond §3.11's literal six-row table | §3.11, §3.15 | P6 authors. P9's legal facts and labels are bounded by whatever P6 publishes |
| Gazetteer contents | §3.7 | Validated gazetteers with word-boundary matching. §4.9's "a university name alone must not create a group" needs the entity kinds these carry |
| Residual library contents beyond the nine names in §7.3 | §7.3, §7.4 | P10 authors the definitions and freezes them as legal nodes (§7.4); P11 owns the residual workflow (§7.5–§7.11). Named here only because §4.9's protected-record surfacing may land in §7.3's Protected Records — see Open question 9 |
| All prompt text | §4.5, §4.7 | The wording of the four constrained tasks and the purpose-detection question set. P8 owns prompt text and prompt fingerprinting (§3.4) |
| The per-domain pre-model signal set beyond the five computations named in §4.3 | §4.3 | "Whether the neighbourhood has a syllabus" is academic-specific; the equivalent for application, research, career and photo groups is unauthored |
| ~~The closed `group_category` vocabulary~~ — **settled**, not deferred | §4.5, §3.15 | It *is* §3.15's launch-domain list: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, code projects. What stays deferred is the per-domain fact schema behind each value, one row above |
| Document-type compatibility tables | §4.2, §4.4 | "Files with compatible document types" and "incompatible document type" (§4.5 task 3) presuppose a per-domain table that no § authors |
| The embedding model, vector width, and embedded text scope | §0, §4.2 | Ownership is settled — P9 computes, P1 stores as §0 compact local arrays — but §0 says only "compact local arrays", and no § names a model, a dimension, or whether the embedded scope is extracted text, OCR text, or a bounded excerpt set. Gated on §8.5 measurement with the rest of §4's numbers |

## Done means

1. **Skeleton green.** With no model, no cloud and no embeddings, P9 forms a group of one from a single
   direct anchor and publishes a `direct-anchor` membership that P10 can freeze a node from and P11 can
   match against (segmentation map, walking skeleton; §4.2 seed kind 1).
2. **Golden dossiers published as fixtures** before P9 is implemented: the PHYS1401 course dossier
   (§4.3, §4.4, §4.6) and the Columbia application-packet dossier including the conflicting Duke essay
   (§4.4, §4.7). P8 can build its validator, and P10/P11 their consumers, against these alone.
3. **§4.6 reproduced exactly.** Given the course dossier, `Lecture 08.pdf` and `Midterm Practice.pdf`
   are `included` on direct evidence; `HW 3.pdf` is `uncertain`, not `included`, and carries
   `basis = context-supported` with `review_state = pending-review`; no course fact is written onto
   `HW 3.pdf` (§4.3, §4.6).
4. **Six stop-rule fixtures, one per rule**, each demonstrating that no supported group forms (§4.9).
   SR2 in particular: a neighbourhood connected only by mutual semantic retrieval yields no group even
   when the model would call it coherent.
5. **Embeddings-off equivalence.** Every group accepted with embeddings enabled that is *not* also
   reachable from a direct anchor with embeddings disabled is a defect, because embeddings never
   establish a group (§4.2). The replay harness runs both, through P2's
   `run_manifest.run_settings.embeddings_enabled` (§8.5).
6. **Purpose fixture.** An ID, transcript, resume, personal statement, certificate and portal
   screenshot are accepted as purpose-coherent only when the dossier carries direct application
   evidence — admissions language, a portal, a checklist, or a clearly targeted essay. The same set
   with only a tight download session yields no accepted purpose (§4.7).
7. **Multi-membership fixture.** One abstract holds accepted `included` memberships in a Research group
   and an application packet simultaneously (§4.9), and P11 can read both (§6.9).
8. **Failure-point separation.** Three seeded defects — an irrelevant retrieved neighbour, a model
   overgeneralisation from a clean neighbourhood, and a valid group with a useless label — produce three
   distinct `stage` values in the failure-point log, never one shared error class (§4.8, §8.5).
9. **Dossier discipline.** No dossier contains a file in full; `anchor_files` and `candidate_files` are
   never merged; every excerpt resolves to a stored observation (§4.4, §4.8).
10. **Privacy precedence.** No dossier reaches a model before P7 has classified every file in it, and no
    protected record's raw content or filename appears in a cloud dossier or a general group summary by
    default (§8.4).
11. **Acceptance is per plan version, evidence is not.** One candidate group is accepted in plan
    version 2 and rejected in version 3 over a **single** shared `Group`, `Membership`, dossier and
    edge set — two `group_acceptance` rows, zero duplicated evidence — and §8.8's "N files now require
    renewed review" diff is computable from the two acceptance sets alone (§8.8, §5.12).

## Cross-cutting answers

### Provenance (§8.2)

P9 appends three of §8.2's named event types: **graph-edge creation**, **group membership proposal**,
and **user group decision**. Each event carries event type, file ID, content hash, responsible
subsystem, model version and prompt fingerprint where a model was involved, user identity on explicit
user action, observation time, and a structured explanation or evidence reference (§8.2).

P9 **never overwrites**: candidate memberships, dossiers, model responses, validator verdicts, proposed
labels and rejected groups all persist. A revised conclusion **supersedes** its predecessor with a
recorded reason, and the earlier record stays inspectable so a user reviewing a placement can see the
origin of the conclusion (§8.2). Rejected groups are retained deliberately — §8.7 requires negative
feedback stored with the evidence that produced it, and §4.9 SR6 reads it.

Group and membership records key on `content_hash` alongside `file_id`, so a content change makes a
membership's evidence stale rather than silently re-pointing it at new bytes (§8.2). The same applies
to a vector (record 9). Embedding computation registers **no new event type**: a vector establishes
nothing, its model and version ride on the record itself, and every conclusion it contributed to is
already traceable through the `mutual-semantic-retrieval` support or edge that cites it (§8.2, §4.2).

### Budgets and degradation (§8.6)

P9 honours four of §8.6's configurable ceilings: **maximum retrieved neighbours per target file**,
**maximum local graph neighbourhood size**, **maximum candidate cluster size**, and **maximum dossier
tokens per model call**. Values are not fixed here (Open question 1).

Degradation order, as §8.6 states it:

- A local graph that exceeds its neighbourhood limit **reduces to the strongest anchors and the
  highest-quality edges** before it is shown to an LLM — it does not truncate arbitrarily.
- A dossier that exceeds its token budget must not truncate silently in a way that removes the decisive
  evidence. It **summarises deterministic facts, preserves anchor excerpts, splits the task, or defers
  the decision** — and records the choice in `omissions`.
- Graph retrieval activates only for files with meaningful incomplete evidence and a plausible anchor;
  LLM calls are reserved for bounded ambiguities, group coherence and purpose (§8.6).
- If the budget is exhausted, P9 retains the extracted evidence, marks the deferred stage, and leaves
  the group in review. **Cost exhaustion must never turn into lower-quality automatic classification**
  (§8.6). Concretely: a group with direct anchors but no model budget stays `candidate` with its
  anchor memberships intact and **no** `coherence_verdict` and **no** `display_label` — it does not
  fall back to an embedding-only or filename-only grouping.
- The deferred state is legible to the user, in §8.6's terms: completed work and deferred work are
  shown differently, never merged into an impression that the group was understood and found
  unimportant.

### Correction learning (§8.7)

P9 records these user actions as local learning records **with scope** (§8.7):

| Action | Scope |
|---|---|
| Accept or reject a group | group |
| Exclude one member from a packet | file-within-group — §8.7's own example: one transcript belongs in a Columbia packet without teaching that all transcripts do |
| Merge or split groups | group |
| Rename a group label | group; may raise to domain when repeated |
| Manually attach a file to a user-created group | file (§4.9) |
| Reject a proposed membership or label | group + the evidence that produced it (§8.7 negative feedback) |
| Repeatedly reject an association between authoring school and application documents | corpus — lower the weight of author-affiliation evidence (§8.7, §3.8) |

Rejected groups, rejected memberships and rejected labels are stored **with their evidence**, or the
system "will repeatedly resurface the same attractive but incorrect grouping" (§8.7). This store is
what §4.9 SR6 queries. Learned preferences must be inspectable and resettable (§8.7). P9 does not train
any model on the corpus; adaptation is local aliases, vocabulary, negative constraints and accepted
examples inside the user's own database (§8.7).

### Plan versioning (§8.8)

§8.8 lists **"Accepted and rejected group memberships"** among what a plan version captures, and §5.12
says facts and accepted groups remain separate from the tree so the user can change the visual
organization without destroying the underlying evidence. P9 splits accordingly:

**Shared evidence database** (survives every plan version, and carries **no** `plan_version_id`):
typed graph edges, candidate groups, dossiers, model responses, validator verdicts, membership records
with their support and citations, the vectors P1 stores, and the failure-point log.

**Plan version**: the acceptance / rejection state of each group and membership, user-edited display
labels and aliases, and the review decisions attached to them — all of it, and only it, in the
`group_acceptance` record (Contract out 8).

The records now match this answer. They previously did not: `Group` and `Membership` each carried a
`plan_version_id`, which contradicted their own placement in the shared database above and would have
forced a whole duplicate group — dossier, model response, verdicts and all — for every plan version
that reached a different decision.

A new plan version never silently reclassifies old files; it produces a new set of recommendations
subject to review (§8.8). When the user edits the tree, the diff must be able to state that N files now
require renewed review because their previous destination no longer exists (§8.8) — a join over
`group_acceptance` for the two versions across one shared membership set.

## Open questions

Six of the twelve are now settled. They are kept in place, marked, rather than deleted, so that
references to them by number — including those in `04-resolutions.md` — stay resolvable. The rest are
unanswered here: the design gates thresholds and neighbourhood sizes on measurement rather than fixing
values (§8.5, §8.6).

1. **Every numeric threshold in §4.** Maximum retrieved neighbours per target file; maximum local graph
   neighbourhood size; maximum candidate cluster size; maximum dossier tokens (all §8.6, configurable,
   unvalued); the "normal group-size threshold" §4.9 refers to but never sets; the frequency at which an
   entity becomes a generic hub for §4.3 suppression and §4.9 SR3; the minimum independent anchor count
   for `supported`; the rank cutoff for "a small ranked set" of neighbours (§4.2). All must be measured
   through P2 (§8.5) before any value is written down.
2. ~~**Are embeddings used at all, and which part owns them?**~~ **Settled — S2 / G2.** Embeddings ship
   in v1: **P9 computes them, P1 stores them as §0's compact local arrays**, never a vector database.
   They stay out of the walking skeleton, which is deterministic by design. §4.2's "embeddings never
   establish the group by themselves" and §6.5's "a semantic embedding alone is insufficient" are
   untouched — this is retrieval reach only; the boundary is stated as six numbered rules in Contract
   out 9. The model, the vector width and the embedded text scope are now Deferred, not open.
3. ~~**Who computes bounded-session boundaries?**~~ **Settled — G6: P6 computes it**, from P3's scan
   timestamps, and emits it as a `possible` fact only (§3.9, §3.13). It feeds §4.2's **fifth**
   retrieval channel (the numbering said "sixth" here; §4.2 orders the session fifth and semantic
   neighbours sixth) and §4.7's purpose packets, and can never anchor a membership.
4. ~~**Is `group_category` the same closed set as the §3.11 / §3.15 domain list?**~~ **Settled — M12:
   yes.** It is the §3.11 / §3.15 domain vocabulary, so the `domain` and `category` P10 requests are
   **one field**. §4.5 task 1's organizing reasons are instances of those domains, not a second axis.
   See Contract out 1.
5. **Must P9's edge-type vocabulary and P11's §6.5 relationship vocabulary be one enum?** §6.5 lists
   derivation links, direct references and matching time period, which §4.2 does not; §4.2 lists
   existing-related-folder and bounded-session, which §6.5 does not. Two enums means P11 re-derives
   edges it could have read. *Blocks:* P11.
6. ~~**Does P8's verdict vocabulary carry `valid-context-supported` as a distinct verdict?**~~
   **Settled — M7: yes, under a different name.** P8 publishes `accept_context_supported` with
   `requires_review: true`. P9 therefore drops its own five-value enum and consumes P8's `outcome` +
   `reasons[]` directly; the five old values are recoverable as `(outcome, reason_code)` pairs, and the
   mapping table is in Contract out 2.
7. **What makes two proposals "equivalent" for §4.9 SR6?** The stop rule turns on the user having
   already rejected an equivalent proposal. Same basis facts? Same member set? Same label? Undefined.
   Without an equivalence test, SR6 either never fires or fires on any overlap.
8. ~~**Is acceptance state per plan version or global?**~~ **Settled — M15: per plan version.** Groups
   and memberships are shared evidence and no longer carry `plan_version_id`; acceptance, review state
   and user-edited labels live in `group_acceptance` (Contract out 8). The same candidate group can be
   accepted in version 2 and rejected in version 3 simultaneously, over one shared evidence set.
9. **Where does §4.9's protected-record surfacing land?** §4.9 allows rare sensitive files to surface
   below the group-size threshold as protected records. §7.3 has a *Protected Records* residual
   template — defined by P10 and frozen as a legal node under §7.4 — and §8.4 makes protection P7's
   classification. Is this a P9 group with `group_id`, a P7 surface, or a residual destination P11
   routes to? *Blocks:* P7, P9, P10, P11.
10. **Are tentative discovery candidates surfaced in the initial release?** §4.9 says anchorless sparse
    groups should be shown "only as tentative discovery candidates, **if at all**". The design
    deliberately leaves this open. *Blocks:* P10's canvas, which would have to render a group class that
    may not exist.
11. ~~**Does a photo-event seed exist before P9?**~~ **Settled — G7: P6 computes it**, as a
    Photos-domain `event` fact clustered deterministically from camera, time and GPS metadata (§3.11,
    §2.6). P9 consumes it as §4.2's fourth seed kind; P11 reads the same fact for §6.3 photo-event
    retrieval.
12. **Must P9 publish intra-packet member roles?** §6.8 requires group-level placement as first-class:
    confirm the shared parent branch from the group's anchors, then route essays to Essays, checklists
    and portal screenshots to Forms and Portal Records, transcripts and resumes to Supporting Materials.
    Whether that member-role split is P9 output or P11 computation is not stated. *Blocks:* P11.
