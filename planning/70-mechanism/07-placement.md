# 7. Placement — where each file would go

P11 is the last part that exists. It takes a **frozen tree** from P10 and, for every file and every
accepted group, names **one approved node in that tree — or says it cannot**. It moves nothing:
`src/placement/records.py:14-15` states the boundary in the record itself — *"No field here can
hold a filesystem path, a deletion, or an expiry."* P12, which turns a named node into a path and a
move, does not exist.

The part owns §6 (everything except §6.1, which is P10's) and §7 (everything except §7.2–§7.4, the
residual *library*, which is also P10's). Its SPEC is
`planning/parts/P11-placement-residual/SPEC.md`, 838 lines. Its code is sixteen modules under
`src/placement/`, 6,555 lines. Roughly a third of that code has no caller on the shipped run path,
and §7.13 below is the inventory.

Two sentences from the design govern everything here, and both are in the code as constants rather
than as comments:

> No system component may invent a new destination after freeze, silently override a direct fact, or
> move an uncertain file simply because it resembles an existing folder. (§6.12)

> **Correct abstention is a successful outcome.** (§6.10)

The second is the one a reader must hold onto, because on a real run today it is the *only* outcome
that happens. §7.14 says what that looks like to a person.

---

## 7.1 The destination index — turning a frozen tree into something searchable

**What P10 hands over.** A `FrozenTree` carrying, per node: a `node_id`, a `node_role` (`ordinary` |
`scoped-general` | `residual` | `shared-material`), a `display_label`, a `parent_node_id`, a
`root_anchor`, a `handling_class`, a `refinement_disposition`, an `accepts_placement` flag, a list
of `expected_values`, and — on residual nodes only — a `disposition`. Beside the nodes it hands over
one **§6.1 destination profile** per node, and a `freeze_record` naming the legal set.

**Legality is P10's, and P11 proves it is only projecting it.** `index.py:502-508` compares the set
of nodes it indexed against `tree.freeze_record.legal_destination_ids` and raises if they differ:
*"P10 owns legality and P11 only projects it."* One entry exists per node with `accepts_placement =
true` and per nothing else (`index.py:490-493`). That single line is where §5.10's guarantee lives —
a folder the user marked `ignored` is not *rejected* at validation time, it **never enters the
index**, so it can be neither retrieved nor suppressed and a file that resembles it produces an
abstention rather than a warning the user has to read (`index.py:7-10`, `retrieval.py:21-22`).

**What an entry holds.** `IndexEntry` (`index.py:47-71`) is 22 fields: the node's identity and
ancestry (`depth`, `ancestor_labels`, computed by walking `parent_node_id` and raising on a cycle or
a missing parent, `index.py:74-91`), and the §6.2 ingredients flattened out of P10's profile —
`template_fields`, `expected_values`, `accepted_group_ids`, `group_labels`, `representative_files`,
`anchor_excerpt_keys`, `known_document_types`, `parent_context`, `child_context`,
`known_exclusions`, `user_edits`.

**Expected values** are the `field = value` assertions a node makes: a node meaning *Columbia
application* asserts `target institution = Columbia`. They arrive as P10's frozen `ExpectedValue`
objects and are flattened to `(field, value)` pairs (`index.py:125-127`).

**What is actually indexed is narrower than what is stored.** `TERM_SOURCES` (`index.py:153-155`)
is three fields — `expected_values`, `accepted_group_ids`, `display_label` — and the docstring gives
the rule: *"Anything else on the entry — the ancestor labels, the representative files, the document
types — is read AFTER a node is already a candidate, so indexing it would build a term nothing
queries."*

So the index is two tables. `placement_index_entries` holds one JSON payload per node (the record
store). `placement_index_terms` holds one row per `(node, source_field, term_key, term_value,
ordinal)` — the inverted projection retrieval actually reads. Labels are casefolded once at build
time (`index.py:174-175`), because *"`retrieve` casefolds the SUBJECT's labels, which are few, and
never the tree's, which are many."*

**A third table exists only to make a count honest.** `placement_index_term_counts` stores, per
`(plan_version, source_field, term_key)`, how many term rows the build wrote for it. Its whole
reason is §6.3's suppression count (see §7.2). If a term matched or contradicted something and has
no aggregate row, `reachable_entries` raises `IndexCountsUnavailable` rather than falling back to
the length of a list — *"the count would fall back to the bounded list and report four destinations
ruled out where the plan ruled out eight hundred"* (`index.py:429-446`).

**One legality authority, shared with P8.** `index.node_exists` (`index.py:595-608`) returns a
closure over one plan version and is handed to P8's Site C and Site D as their `node_exists`
authority. A dossier stamped with a different plan version answers `False`. The point is stated at
`index.py:12-15`: two sources could disagree and *"the disagreement would look like a model error."*

---

## 7.2 Retrieval — matching a file's evidence against nodes, and suppressing what conflicts

**Six channels, none of which decides.** `retrieval.py:36-48` names §6.3's six: `direct_fact`,
`accepted_group`, `graph_relationship`, `structural_relationship`, `semantic_neighbour`,
`curated_folder`. Two of them — semantic and curated — are declared `NON_DECIDING_CHANNELS`
(`retrieval.py:52`): a node reached only by those is recorded in `semantic_only_node_ids` and can
never carry a placement on its own, which is §6.5's *"a semantic embedding alone is insufficient."*

**Only two of the six are ever assigned.** `retrieve`'s loop (`retrieval.py:125-148`) appends
`DIRECT_FACT`, `ACCEPTED_GROUP`, `CURATED_FOLDER` and `SEMANTIC_NEIGHBOUR`. `GRAPH_RELATIONSHIP` and
`STRUCTURAL_RELATIONSHIP` are declared, weighted in the scorer, and **never assigned to a
candidate anywhere in `src/`.** This has a direct arithmetic consequence, which §7.3 works out.

**What a matching fact is.** A `MatchingFact` (`records.py:173-184`) is `(file_fact_id, field,
value, reliability, evidence_ref)` — P6's row, carried, with the `evidence_ref` being P4's
content-addressed `observation_key` rather than a per-row uuid, so a rejection recorded today still
resolves to its evidence after an extractor upgrade (SPEC:203-211). A fact matches a node when the
subject's `(field, value)` pair equals one of the node's `expected_values` pairs — exact, not fuzzy.

**Facts are filtered before they can reach a node at all.** `_eligible_facts`
(`retrieval.py:72-83`) drops any fact whose field P6's catalogue marks
`destination_eligible = False`. This is where `00`:44's prohibition on person-shaped destinations is
enforced: `authored_by`, `our_firm`, `instructor` and `people` never reach a candidate node.
`groups.py:23-29` explicitly declines to re-check it — *"A second check here would be a second
opinion with no way to be reconciled."*

**Retrieval is one bounded read, not a scan.** `reachable_entries` (`index.py:282-465`) issues
seven SQL reads sized to the *answer*, not to the tree: four to find what the subject's own evidence
reaches (matched pairs, group ids, labels, semantic node ids), a fifth asking only those nodes which
of the subject's stated fields they state *differently*, a sixth reading a bounded sample of
further ruled-out nodes per field, and a seventh reading one integer per field. The earlier
implementation deserialised every legal node once per file — O(files × nodes) — measured at ×4.2 per
file in `planning/58-SCALE-STRESS.md` §2.

**What a conflict is.** The subject states `target institution = Duke`. Every legal node stating
`target institution` with any other value is suppressed. The suppression happens *inside* retrieval,
not as a later filter, because §6.3 makes it part of retrieval (`pipeline.py:305-306`).
`Reachable.contradicted_node_ids` is the suppression set and is kept separate from the naming list,
so a node the sample had no room to name is still barred from the candidates
(`index.py:360-370`, `240-251`).

**The recorded failure: naming everything.** `index.py:196-223` records why the list is bounded. On
`planning/58-SCALE-STRESS.md` §2's tree the suppression list is 799 long *for every file*, eight
million ids across a 10,000-file disk, and *"the sentence the user reads names every folder they
own."* The document's own words for the same failure elsewhere: *"the warning list outgrows the tree
it describes."*

**So the list is a bounded sample and the count is exact.** `ConflictConsidered`
(`records.py:210-263`) carries `suppressed_node_ids` (named) and `suppressed_node_count` (total),
and refuses a record where the count is smaller than the list. Which nodes get named is not
arbitrary: the ones a retrieval channel actually **reached** go first — *"they are the ones the user
is about to ask 'why not that one?'"* — and the remainder of the budget is filled from the field's
own stable index order. The budget is `max_retrieved_neighbors`, the same ceiling that bounds the
candidate list, deliberately: *"both answer one question — how many destinations should a human read
about one file — from opposite sides."*

**What the person sees.** `pipeline._explain` (`pipeline.py:499-521`) renders it as
`ruled out A, B and 795 further destinations on conflicting evidence`, or, when nothing the file's
evidence reached was ruled out, `ruled out 799 destinations on conflicting evidence, none of which
this file's evidence reached`.

**Candidates are ranked deterministically** — strongest channel first, then node id, never insertion
order (`retrieval.py:159-169`) — and truncated to `max_retrieved_neighbors`.

---

## 7.3 The node-local graph — §6.4 and §6.5

`build_node_local_graph` (`graph.py:79-164`) builds one graph per candidate node. Vertices are the
subject plus the files already accepted in that node (`entry.representative_files`); edges are typed
relationships supplied by the caller from P6 facts, P9 memberships and P3 folder context. P11
discovers no relationship of its own — *"that would be a second grouping engine and P9 owns
grouping"* (`graph.py:84-86`).

Five edge types (`graph.py:39-52`): `shared_validated_fact`, `duplicate`, `version_family`,
`compatible_document_type`, `existing_related_folder`. A semantic neighbour is **deliberately not an
edge type** — it is a retrieval channel only, *"because an embedding alone is insufficient and an
edge type would make it look like evidence of the same kind as a shared fact."* An untyped edge
raises.

Locality is structural, not declared: an edge survives only if it touches a file already accepted in
*this* node (`graph.py:103-107`), so *"there is no code path along which whole-corpus reclustering
could happen."* `foreign_node_ids` is a seam assertion on top of that and raises if non-empty.

Two §8.6 ceilings apply, in an order the code argues for: the **cluster** (`max_candidate_cluster_
size`, a bound on files) is cut before the **neighbourhood** (`max_local_graph_neighborhood`, a
bound on edges), because the other order does not converge (`graph.py:111-136`).

`is_typed_support` (`graph.py:167-182`) is §6.5's bar: a graph supports a placement only if it has
at least one entity that is *not* a high-frequency entity. The frequency cut-off is injected; P11
picks none.

---

## 7.4 Scoring and the two conditions (§6.10)

**The score.** `scoring.py` computes a weighted count of independent channels, normalised to the
policy's declared scale:

```
_CHANNEL_WEIGHT = {DIRECT_FACT: 3, ACCEPTED_GROUP: 2,
                   GRAPH_RELATIONSHIP: 1, STRUCTURAL_RELATIONSHIP: 1}   # _MAX_WEIGHT = 7
support_score = policy.support_scale_max * weight / _MAX_WEIGHT          # scoring.py:81
```

The weights are structural rather than tuned: *"a direct fact outweighs a group membership
outweighs a relationship, which is §3.13's own ordering, and the two non-deciding channels
contribute nothing at all"* (`scoring.py:38-47`). Semantic and curated weigh 0.

**The channels are deduplicated before they are weighed.** `retrieval.py:146` stores
`tuple(dict.fromkeys(channels))`, so a candidate whose five direct facts all match scores exactly
the same 3 as a candidate matching one. The score counts *kinds of evidence*, not *amount*.

**Condition one: support.** `best.support_score >= policy.minimum_support_threshold`
(`scoring.py:129`).

**Condition two: margin.** `policy.margin_predicate(best, next_best)`, which is
`best - next_best >= margin_threshold` (`config.py:88-90`). Where there is no next-best, B8(b)
applies: `margin_over_next` is `None` and `meets_margin` is the string `true_vacuous`, never a
measured `true` (`scoring.py:130-142`). `TwoCondition.__post_init__` (`records.py:298-324`) enforces
the pairing both ways — a vacuous margin with a number is malformed, and a measured margin without
one is malformed.

**Both thresholds are injected and both are recorded.** `SupportPolicy` (`config.py:48-90`) carries
`policy_id`, `support_scale_max`, `minimum_support_threshold`, `margin_threshold`, and refuses a
threshold outside `0..scale` — *"a threshold no score can reach abstains on everything and a
threshold every score clears gates nothing."* `require_policy` refuses `None`: *"Absent means
refuse, not guess"* (`config.py:111-117`). The SPEC leaves both numbers open (Open questions 1 and
2) and the code ships no default for either.

**The shipped deployment's numbers** are in `src/cli.py:115-117`:

```python
SUPPORT_POLICY = SupportPolicy(
    policy_id="cli-support-v1", support_scale_max=1.0,
    minimum_support_threshold=0.50, margin_threshold=0.20)
```

with the reasoning at `cli.py:108-115`: *"0.50 as the support bar because that is the band a direct
fact alone (3/7) falls below and a direct fact plus an accepted group (5/7) clears."*

**What that arithmetic means in practice.** Since two of the four weighted channels are never
assigned (§7.2), the reachable scores are exactly: `0`, `0.286` (group only), `0.429` (direct fact
only), `0.714` (direct fact + group). Against a threshold of `0.50`, **a placement in this
deployment requires the accepted-group channel to fire.** A file whose facts uniquely and correctly
match one node's expected values, with no group, scores `0.429` and cannot be placed.

**`policy_id` does not travel on the decision.** `cli.py:113-114` asserts *"A run under these is
auditable because `policy_id` travels on every decision — change a number and change the id with
it."* It does not. `TwoCondition` (`records.py:280-296`) carries `support_threshold` and
`margin_threshold` and no id; `PlacementDecision` has no policy field; `store.PROJECTION_COLUMNS`
has none; `placement/events.py` never logs one. `grep -rn policy_id src/` returns hits only in
`config.py`, `cli.py`'s comment, and P10's unrelated shared-material policy table. Two runs under
different policies with the same numbers are indistinguishable, and the audit trail the comment
promises is the two floats.

**"Unique direct match" is a property of the facts, not of the candidate set**
(`scoring.py:154-186`). It is true when exactly one candidate carries the `DIRECT_FACT` channel,
that candidate is the best-scoring one, **and** both §6.10 conditions hold. The code argues both
exclusions explicitly: keying it on "there was only one candidate at all" would make B8(b)
unsatisfiable, and requiring a graph anchor would mean *"a syllabus whose subject fact names exactly
one course could never be decided deterministically, which is the case §6.6 exists to keep off the
model."*

A unique direct match sets `verdict = accept_direct`, `confidence_class = "exact fact match"`,
`requires_review = False`, and — via `needs_model_call` (`scoring.py:230-237`) — **issues zero model
calls**. Anything else that clears both conditions is `accept_context_supported` with
`requires_review = True`, because *"calling it `accept_direct` would name a fact match that never
happened"* (`scoring.py:188-198`). `records.py:320-324` refuses an `accept_context_supported` record
that does not require review.

**The degenerate case stays binding.** With one legal candidate the margin is vacuous and the
support threshold is the sole gate. A file below it abstains `no_supported_destination` *even though
that one destination is the only one available* — *"the scarcity of destinations is not evidence
about the file, and a tree with one branch must not become a funnel"* (`scoring.py:16-18`).

---

## 7.5 The outcomes, and what a person is told for each

Seven outcomes on one record shape (`vocabulary.py:105-116`): `place`, `return_to_placement`,
`mark_review_later`, `leave_in_place`, `mark_state`, `ask_user`, `abstain`. Exactly one
outcome-shaped field may be filled, and `PlacementDecision.__post_init__` (`records.py:416-436`)
enforces presence *and* absence in both directions: `destination` exists exactly on `place`,
`return_target` exactly on `return_to_placement`, `marked_state` exactly on `mark_state`, `ask`
exactly on `ask_user`, `abstention_reason` exactly on `abstain` — *"an unexplained one is silence,
and a reason on any other outcome contradicts the decision."*

**Only `place` produces a plan.** `PLAN_BEARING_OUTCOMES` is a one-member tuple
(`vocabulary.py:118-120`). `abstain` is not a deferred move.

### The nine abstention reasons

`ABSTENTION_REASONS` (`vocabulary.py:240-244`) holds nine. The SPEC enumerates eight —
`multiple_supported_homes` appears **zero times** in `planning/parts/P11-placement-residual/SPEC.md`
and is P11's own addition, made because of a finding in `planning/59-FINAL-UX-EVALUATION.md` §3a.

The sentence a person reads is built by `_abstention_explanation` (`pipeline.py:535-607`). Its
governing rule is stated in its own docstring: two reasons get a rewritten sentence because *"the
default sentence describes [them] falsely"*, and every other reason keeps the default, because
*"giving all of them a reassuring new voice would erase the one honest report of a genuine evidence
failure."*

| reason | when | what the person is told |
|---|---|---|
| `no_supported_destination` | nothing cleared the support threshold, or nothing was retrieved | the default: *"No legal destination cleared §6.10's conditions (no_supported_destination). Abstaining is the correct outcome; the evidence is retained and the file has not moved."* |
| `low_margin` | the margin failed and **only one** candidate cleared support on its own | the default sentence, with `low_margin` in the parentheses |
| `multiple_supported_homes` | the margin failed and **two or more** candidates cleared support on their own | its own sentence: *"…each cleared §6.10's support threshold and nothing in the evidence separates them, so this file has more than one supported home. Nothing moved: which one is its home is a choice about your material, not a gap in the evidence."* |
| `semantic_only` | the best candidate was reached only by embedding/label similarity | the default |
| `generic_hub_only` | the best candidate's graph has anchors but no informative entity | the default |
| `conflicting_facts` | nothing survived retrieval **and** a conflict fired | the default |
| `no_shared_branch` | §6.9 multi-home with no shared branch | never reaches this function — `_multi_home_decision` writes its own sentence (below) |
| `budget_deferred` | an §8.6 ceiling stopped the work | the default, with `budget_deferred` in the parentheses |
| `privacy_blocked` | §8.4 declined the dossier | three distinct sentences, below |

**`multiple_supported_homes` is the important one.** Two legal homes is a real state, not a
confidence failure. `scoring._reason` (`scoring.py:87-117`) tells the two margin failures apart by
counting how many candidates cleared the support threshold *on their own* — counted over all
candidates, not the top two, *"so three tied homes read the same as two"* (`scoring.py:144-151`).
The docstring names the defect it fixes: *"a research paper that is also school homework, reported
as an evidence-quality complaint… one makes them distrust the extraction and the other lets them
just pick."* Nothing about routing changes — both are `weak`, both require review, neither moves a
file. Only the sentence differs.

**`privacy_blocked` has three distinct causes and three distinct sentences**
(`pipeline.py:563-602`):

1. **Unclassified** — nothing has said what kind of material this is.
   > *"This file has not been classified — nothing has yet said what kind of material it is — so it
   > was not shown to a model and nothing moved. It is waiting for you to say what it is, not marked
   > sensitive and not judged on thin evidence."*

   This sentence was **corrected on 2026-08-29**. It used to end *"nothing has been able to read
   enough of it"*, and `planning/65` §4.1 caught that on a live run: all four files had a `direct`
   fact in `file_facts` and zero rows in `classifications`. *"Reading is the step that WORKED and it
   was the step the sentence blamed."* The comment at `pipeline.py:565-584` records the rule it now
   obeys: P11 knows nothing classified the file; whether it was *readable* is P4's
   `extraction_runs`, which P11 does not read *"and must not guess at"*, so the sentence names the
   step that stopped and claims nothing about the one before it.

2. **Protected** — the user marked this material sensitive.
   > *"This file is protected material (§8.4), so nothing about it was assembled for a model and it
   > was left exactly where it is. That is a deliberate decision about sensitivity, not a failure to
   > find a destination."*

3. **Offline install / mode denial** — the operation mode forbids cloud egress.
   > *"Deciding this file needed a model, and §8.4 did not clear this file for a model call. Nothing
   > about it left this device and nothing moved; the evidence is retained."*

The three are kept apart by `privacy.py`. `is_unclassified` is a single definition
(`privacy.py:138-145`) precisely because *"two callers ask it for two different purposes… and a
second spelling is how the two would come to disagree about the same file."* The module is emphatic
that unclassified and protected never collapse: *"A passport is material the user marked sensitive
and the product deliberately did not open; an unreadable scan is material nothing could tell
anything about."*

**`no_shared_branch`** is written by `_multi_home_decision` (`pipeline.py:993-996`) with its own
sentence for all three of §6.9's outcomes:

> *"This file has accepted membership in more than one packet. §6.9 permits a shared branch, a
> question, or an abstention, and never an arbitrary choice between the packets."*

**Budget deferral is structurally separated from abstention.** `_abstention`
(`pipeline.py:620-624`) refuses a record where `reason == budget_deferred` and `deferred_stage` is
`None`, or the reverse; `records.py:455-460` refuses the same shape; and `stage_output.py:43-65`
maps P11's three results to three *distinct* P2 envelopes, asserted distinct at import, so a
deferral is `deferred`/`ceiling_reached` and never `abstained`/`within_ceiling`. The reason is
stated at `stage_output.py:11-14`: scored as `abstained`, P2 *"would grade a ceiling-truncated run
`abstained_correctly` or `abstained_incorrectly` — a judgement about evidence — when no judgement
was made."*

That separation holds in the record and in the P2 envelope. It does **not** hold in the sentence:
see §7.15.

---

## 7.6 Group plans — placing a group rather than a file (§6.8)

`place_group` (`pipeline.py:802-868`) runs §6.8 in §6.8's order:

1. **Read the group as this plan version sees it.** `accepted_group_as_of`
   (`groups.py:99-125`) asks P9's `group_state_as_of` at P10's frozen version and refuses anything
   that is not `accepted`. Reading `Group.state` directly *"would answer `supported` in every
   version, and P11 would place a group nobody accepted."*
2. **Classify each member through the ordinary path**, passing `group_plan_id` down so the
   **stored row** carries it. It is passed in rather than patched on afterwards because *"a row
   written without it would make the review surface show several unrelated file moves while the
   in-memory plan looked correct"* (`pipeline.py:281-284`).
3. **Confirm the shared parent.** `confirm_shared_parent` (`groups.py:191-200`) returns the single
   distinct parent if all members agree, and `None` otherwise. It is explicitly **never a majority
   vote**: *"A majority would place the minority members somewhere their own evidence does not
   support, which is exactly the 'moved because it resembles a folder' failure §6.12 prohibits."*
4. **Exclude outliers.** A member P9 flagged is excluded and explained, never forced in.
   `excluded_outlier_for` (`groups.py:203-231`) refuses to build an exclusion for a member P9 did
   *not* flag — *"building an exclusion for a member P9 called `none` would publish a finding P9
   never made."* The exclusion carries P9's competing values as `conflicting_fact`, an
   `evidence_ref`, and a route: the node it went to instead, or `review_queue`.

`GroupPlan.__post_init__` (`groups.py:154-177`) enforces two invariants: every member decision
shares the plan's id — *"that shared id is what makes the review surface show one plan rather than
several unrelated file moves"* — and no file appears both as a member and as an excluded outlier,
because *"one presentation cannot say a file was placed with the group and left out of it."*

`_record_group_plan` (`pipeline.py:871-910`) persists it to `placement_group_plans`, superseding any
live plan for the same group first. Without it *"a review surface reopened a day later would find
four file decisions and no evidence they were ever one plan."*

**§6.9, the multi-home file.** `run_corpus` detects multi-home membership **before anything is
placed** (`pipeline.py:1231-1246`) and passes those file ids to every `place_group` as
`skip_file_ids`, because *"placing it inside the first plan and correcting afterwards would mean the
arbitrary choice was made and then withdrawn, which is not the same as never making it."*

`resolve_multi_home` (`groups.py:234-279`) then returns `(place, shared_branch)`,
`(ask_user, competing_ids)` or `(abstain, no_shared_branch)`. Its guarantee is structural:
*"There is no branch of this function that returns a member of `candidate_node_ids`."* It raises
`InstitutionalDestinationRefused` if the shared branch offered *is* one of the competing homes —
*"§6.9's shared branch is a destination above the competition, not one side of it."* Whether the
answer is `abstain` or `ask_user` is SPEC Open question 6; the selector is injected and its absence
refuses.

---

## 7.7 Residual sets (§7.5) and the set-level gate (§7.6)

**Residual runs second, enforced by a raise.** `surface_residual_sets`
(`residual.py:133-205`) refuses a caller passing `placement_pass_complete=False`: *"Surfacing now
would call a file unplaceable before the engine finished trying."* `run_corpus` calls it once, after
every group and every file has been through §6 (`pipeline.py:1304-1310`).

**The partition is injected. P11 invents no set names.** `residual.py:145-150` refuses a `None`
partition, citing §7.5's own preface — *"'It may show' — illustrative counts, not a fixed
taxonomy (SPEC Open question 10)."*

**Nothing may be dropped and nothing invented.** `residual.py:158-166` checks that the partition's
member ids are exactly the unplaced ids, and names both directions of the failure: *"Every unplaced
file appears in exactly one review set or it is never shown."* The reason is that *"the residual
screen is the last place a file can be mentioned at all."*

**Seven attributes each set must carry**, plus its id, label and members (`ResidualSet`,
`residual.py:74-108`):

| attribute | §7.5's question |
|---|---|
| `representative_examples` | what is in here? |
| `file_type_distribution` | what kinds? |
| `age_range` | how old? |
| `evidence_availability` | is there OCR/text, or nothing? |
| `sensitivity_status` | is any of this sensitive? |
| `weak_graph_neighbours` | what is it faintly connected to? |
| `reason_not_placed` | why could the pipeline not safely place these? |

`reason_not_placed` is required by a raise: *"a set with no reason is a pile."* `file_count` must
equal `len(member_file_ids)`, *"or the review screen reports a number no one can expand."*
`protected` must be a real boolean, never `None`, because *"a null here would be read as `false` by
every consumer that tests it — a protected set becoming an ordinary one."*

**The batch ceiling splits; it never truncates.** `residual.py:171-177`:

```python
batches = [members[i:i + ceiling] for i in range(0, len(members), ceiling)]
```

with the comment *"Split, never truncate: §8.6 reduces work and never drops files."* Each batch
becomes its own set, labelled `(1 of 2)`, `(2 of 2)`. `planning/68-PERSONA-RERUN.md` §3 F7 records
this working on a real corpus: 13 unplaced files, `residual.max_files_per_review_batch = 8`, two
sets of 8 and 5 — and records that its first draft misdiagnosed the cause and was corrected.

**The set-level gate.** `require_set_decision` (`residual.py:244-261`) raises if the set has no
recorded decision, and `require_model_call_permitted` (`residual.py:280-305`) is the one gate in
front of a per-file model call. It has **three** refusals in a deliberate order:

1. **Protected first, and independently of any decision.** `ProtectedSetNotReadable` — *"a
   protected set that refuses for want of a decision would invite the fix 'decide it', and the
   answer to a protected set is never a decision. It is counted, explained and left closed."* It
   raises rather than returning `False` because *"`False` is indistinguishable from 'the user chose
   to leave this alone'… one is a choice, the other is a prohibition"* (`residual.py:15-21`).
2. No set decision → `SetDecisionRequired`.
3. A decision that did not ask for a model → `ModelCallNotAuthorised`. Exactly one of §7.6's four
   choices asks for one; a set the user chose to leave in place produces **zero** calls.

**The residual library is P10's.** P11 holds no template definitions (M10). An enabled residual
branch arrives as an ordinary node carrying `node_role = residual` and a `disposition`, and a
template the user did not enable has **no node** — *"so the §7.7 model cannot name it and P11 needs
no residual-specific legality path at all"* (`residual.py:23-26`). Which fallback folders exist is
therefore entirely a function of what the user enabled at tree design.

---

## 7.8 The eight actions and the loop back to §6

`ACTION_OUTCOME` (`residual.py:323-334`) maps §7.7's eight actions onto §6's outcomes, and asserts
at import that its keys are exactly P8's `RESIDUAL_ACTIONS` — *"a P8 addition break[s] here loudly
rather than fall[s] through to a default"* — and that `ask_user` is not among the values, because
the residual path is closed to it.

| §7.7 action | outcome | qualifier |
|---|---|---|
| return to a confirmed domain group | `return_to_placement` | `return_target.kind = confirmed_domain_group` |
| return to an accepted graph/purpose packet | `return_to_placement` | `return_target.kind = accepted_graph_or_purpose_packet` |
| choose one approved residual destination | `place` | `destination.node_role = residual` |
| choose an approved broad parent branch | `place` | `node_role = ordinary`, levels in `unsupported_levels[]` |
| mark for Review Later | `mark_review_later` | — |
| leave in current location | `leave_in_place` | — |
| mark protected or unsupported | `mark_state` | `marked_state` |
| abstain | `abstain` | `abstention_reason` |

`outcome_for_action` (`residual.py:342-390`) requires a target exactly where the record needs one and
refuses one exactly where it does not, because *"Returning `(place, None)` for a destination-less
choice would build a decision `PlacementDecision` cannot construct, and the failure would land a
stage away from the action that caused it."*

**The §7.9 loop.** When a residual review finds a credible connection, the file goes back through
§6. `_review_set_with_model` (`pipeline.py:1196-1208`) writes the residual decision, calls
`place_file` with `returned_from` set to it, then calls `link_return`. Both records persist —
`link_return` (`residual.py:393-427`) refuses to log the traversal unless the placement names the
residual decision, and refuses if the two records concern different subjects: *"§7.9 hands ONE file
back, and a loop joining two subjects explains neither of them."*

The loop is bounded by an injection. `check_return_cycle` (`residual.py:430-465`) refuses without
`max_return_cycles`, citing SPEC Open question 8 — *"an unbounded loop is a replay that never
terminates."* It counts only live rows, because counting superseded ones *"would make the number
mean 'times somebody edited the record'."*

---

## 7.9 Review policy — how much trust a decision demands

Three values (`vocabulary.py:255-260`): `auto_eligible`, `review_required`, `blocked_pending_user`.
`review_policy_for` (`privacy.py:197-241`) is the single producer, and **every** path to
`auto_eligible` is narrow: six things each forbid it on their own, in this order.

```
is_unclassified                        -> blocked_pending_user
not moves_files(disposition)           -> review_required   (§7.4 review-only / leave-in-place)
protected and not automatic_move_permitted -> review_required   (Design:185)
two_condition.requires_review          -> review_required   (§6.10)
group_support.membership == user-attached -> review_required (M12)
not unique_direct_match                -> review_required   (§6.6)
                                       -> auto_eligible
```

**The ordering is argued, not incidental.** The unclassified check is first because
`blocked_pending_user` and `review_required` are different obligations: *"a reviewer can confirm a
decision that merely needs confirming and cannot confirm one whose subject nothing has
classified"* (`privacy.py:244-250`). The disposition check is second because 00:121's word is
*"never"*, and *"a disposition gate placed after the scoring checks would be one a high enough score
could reason its way past."*

**This is where §6.11's demand — that a direct placement and a context-supported one must not demand
the same trust — is realised.** Only a `unique_direct_match` can be `auto_eligible`. A
context-supported placement always carries `requires_review = True` from
`assess` (`scoring.py:198`), and `records.py:462-471` refuses an `auto_eligible` record whose
verdict requires review or which rests on a `user-attached` membership.

`destination_disposition` has **no default parameter**, deliberately: *"A caller that forgot it
would get the ordinary-node answer and silently lose the gate, which is precisely the state this
field was already in — written, validated, and read by nothing"* (`privacy.py:221-223`). That is the
record of a real prior defect: `IndexEntry.disposition` was built and validated by `index.py` and
read by nothing until this function was wired to it.

**`model_eligibility` is derived, not read** (`privacy.py:10-24`), because §8.4's three values have
no producer in `src/privacy/`. Three separate causes produce `local_only`: an unclassified file, a
mode that forbids cloud egress, or the protected flag. Each gate is a live P7 predicate —
`mode_forbids`, `unclassified_denies`, `may_move_automatically` — asked rather than re-derived, *"so
if P7 ever moves a mode across the line P11 moves with it."*

**An absent classification blocks the file, not the run.** `privacy.py:26-35` records the change and
its reason: raising *"meant ONE such file refused an entire corpus. A person with ten thousand files
and one ambiguous scan got a traceback where a plan with one file marked for review was the correct
answer."*

---

## 7.10 Correction learning (§8.7)

**A correction record is an event, not a second store.** `record_correction`
(`learning.py:166-193`) appends to P1's `events` table with §8.7's columns: `correction_scope`,
`correction_subject`, `polarity` (`accept` | `reject`), `proposal_class` (`placement` | `residual`),
`basis_key`, plus the action name, the user id, and an explanation. *"P1 owns `events` and its §8.7
columns, and `learning_records` already honours a reset as a cutoff without deleting anything."*

**The basis key is the pair §8.7 names**: `basis_key_for` (`learning.py:76-78`) returns
`f"{subject_id}->{node_id}"`. It deliberately **omits the content hash**: *"§8.7 is about what the
user decided, and editing a file does not un-decide it — a versioned key would silently stop
matching on the next save and resurface exactly the destination the user rejected."*

**Scope is the whole safety property, and it is never widened.** Six scopes: `file`, `group`, `node`,
`corpus`, `template`, `domain`. `_subject_ids` (`learning.py:81-121`) can address four of them — the
file, the group, each candidate node, and a corpus subject the caller names — and **refuses**
`template` and `domain` outright:

> *"answering `()` for them would report 'the user rejected nothing' for a question that was never
> asked. That is the difference between a suppression that is absent and one that was never looked
> for, and only one of them is safe to auto-place on."*

That is the code's expression of §8.7's governing example: one transcript belonging in a Columbia
packet must not teach the engine that all transcripts do. `learning.py:8-11` states it as the rule
the module exists for.

**Suppression is consulted before `place` is emitted.** `pipeline.py:316-337` queries
`suppressed_nodes` at the `file` scope only, and drops the rejected nodes from the candidate set.
Only `file` — *"asking for them here would look like a wider check and perform none."* A hit means
the node is skipped, *"never auto-placed and never silently re-ranked, because a silent re-rank
would hide from the user that their own correction was the reason"* (`learning.py:128-133`).

**A residual rejection is not a placement fact.** `review._PROPOSAL_CLASS` (`review.py:55-58`) maps
each of P13's four surfaces to the store the correction belongs in: *"A rejection taken on a
residual surface is a residual fact: read back as a placement fact it would suppress a node the user
never saw in the §6 pass."*

**`change_destination` records the node moved *away from*, not to.** `_node_in_question`
(`review.py:176-196`) reads the live decision's own node, because *"Keying the rejection on the
payload instead would suppress the destination the user had just chosen, and the mistake would only
surface on a later run."*

**`defer` has no polarity.** `_POLARITY` (`review.py:70-75`) maps six actions and asserts `defer` is
absent: *"it is a decision to decide later, and recording it under either polarity would teach the
engine something the user did not say."* The action is still logged, because *"a deferral the log
cannot show is a gap in the reconstruction §8.2 exists to make possible."*

**Creating a folder is P10's edit, and the routing is readable.** `routes_to_p10`
(`review.py:103-110`) returns `()` and writes one log line, *"because the prohibition (§6.12) is
about the SYSTEM inventing one and this is the user"* — and *"a receiver that swallowed it silently
would look identical from every assertion about what did NOT happen."*

---

## 7.11 Plan versions (§8.8)

Every P11 table carries `plan_version`, because a decision, a group plan, a set decision and the
whole index are *projections of one frozen tree* (`schema.py:1-8`). Every table is append-only by
trigger: a `BEFORE DELETE` raise and a `BEFORE UPDATE OF <every non-supersede column>` raise
(`schema.py:176-190`), so a writer correcting an outcome in place fails rather than losing the
original.

`store.record_decision` (`store.py:78-149`) does the supersede, the insert and the event in **one
transaction**, and supersedes *before* it inserts because `one_current_placement_decision` is a
partial unique index over unsuperseded rows.

`versions.reproject` (`versions.py:67-…`) is §8.8's re-projection and *"marks, and it never
matches."* It matches through **lineage** — `decision.node_id → from-version entry →
origin_node_id → to-version entry` — because P10 mints a new `node_id` per version, so matching on
`node_id` *"would mark every decision for renewed review after any tree edit at all — including a
pure rename, which §8.8 forbids by name."* There is deliberately no third branch: a removed node
usually has a plausible survivor, and matching onto it *"is the 'silent reclassification' §8.8
prohibits by name."* It writes nothing to `placement_decisions`; the mark is a computed diff.

---

## 7.12 Where P11 is measured (§8.5)

Two stage ids, drawn from P2's closed ten: `candidate_node_retrieval` and `placement_scoring`
(`vocabulary.py:356-358`). `P11` is not a stage id.

`stage_output.py` maps P11's three results — `decision_written`, `evidential_abstention`,
`budget_deferral` — onto three distinct `(outcome, budget_state)` envelopes, asserted distinct at
import. The retrieval stage's subject ref is namespaced `candidates:{plan_version}:{subject_ref}`
(`stage_output.py:134-150`) because `retrieval` is already P9's dimension name and an un-namespaced
ref *"would make a full-pipeline replay raise `IntegrityError` the moment P9 and P11 both keyed a
`retrieval` row on the same file."*

Both stage emissions are conditional on a `P2Run` injection (`pipeline.py:264-267`, `338-341`). The
shipped CLI passes `p2=None` (`cli.py:731`), so **a real run writes no stage outputs at all** — a
declared state, not a gap (`pipeline.py:140-149`).

---

## 7.13 What is built and inert

Grepped across `src/`, excluding each function's own module, the following P11 entry points have
**no caller anywhere on the run path**:

- The whole §7 review workflow: `review_residual_sets`, `run_residual_file`, `record_set_decision`,
  `require_model_call_permitted`, `model_calls_permitted`, `outcome_for_action`, `link_return`,
  `check_return_cycle`, `ACTION_OUTCOME`. `surface_residual_sets` is the only §7 function `run_corpus`
  reaches. **The eight §7.7 actions exist, are mapped, are tested — and nothing in a shipped run can
  invoke one.**
- The whole §8.7 receiver: `placement/review.py` (`apply_review_action`, `correction_scope_of`,
  `routes_to_p10`) and `learning.record_correction`. Corrections can be *read* (`suppressed_nodes`
  is called by `place_file`) but nothing in `src/` can *write* one. The learning store is
  permanently empty on a real run.
- §8.8's `versions.reproject` and `learned_preferences_still_applicable`. Only mentioned in a P10
  docstring.
- `store.decision_history`, `store.placed_node_ids`, `index.entries_for_plan`,
  `privacy.moves_files` as a public predicate, `placement/fixtures.py`.
- Two of the four weighted retrieval channels — `GRAPH_RELATIONSHIP` and
  `STRUCTURAL_RELATIONSHIP` — are declared in `CHANNELS` and weighted in `_CHANNEL_WEIGHT` and are
  **never assigned to a candidate**.
- `Subject(kind="group")` is a legal record shape with validation of its own and is **never
  constructed in `src/`**. §6.8 places a group as N file decisions sharing a `group_plan_id`, not as
  one group-subject decision.
- `CorpusResult.group_plans`, `CorpusResult.unplaced_file_ids` and `GroupPlan.excluded_outliers`
  are read by **nothing** in `cli.py` or `production.py`.

The common cause for the first three bullets is P13: every one of them is a receiver for a user
gesture, and the review screen that produces the gesture does not exist.

---

## 7.14 What actually happens on a real run today

`planning/68-PERSONA-RERUN.md` ran the shipped command over four corpora — a litigator, a PhD
student who TAs, a two-child household, and one person who is all three — 26 files total.

**Every file abstained. Zero files were placed. In all four runs.**

The chain that produces this, in the code:

1. **No classifier ships.** The CLI injects a detector that produces nothing;
   `classifications` holds zero rows in all four databases while `file_facts` holds a `direct` fact
   for every file. `privacy_state_for` (`privacy.py:118-135`) therefore resolves every file to
   `unreadable_unclassified`, and `unclassified_denies` makes `model_eligibility = local_only`.
2. **The support threshold is not reached deterministically.** The deployment writes one direct
   fact per file (`cli.py`'s `DIRECT_SLOTS`, one regular expression). One direct-fact channel scores
   `3/7 = 0.429` against a threshold of `0.50`, so `meets_threshold` is `False`, so
   `unique_direct_match` is `False` (`scoring.py:180-186`), so `needs_model_call` returns `True`.
3. **The privacy gate fires before the model-path check.** `place_file` (`pipeline.py:372-374`)
   asks `may_assemble_dossier(privacy)` first and returns the abstention immediately.
4. So the recorded reason is `privacy_blocked`, cause **unclassified**, and the sentence is the one
   corrected on 2026-08-29.

**What the person reads.** The report (`cli.py:864-975`) leads with protected containers, then the
tree, then one block per *kind* of outcome. For all 26 files that block is:

```
  Waiting for you to say what these are -- 5 files
    motion-to-compel.pdf
    ...
    Same reason for each: This file has not been classified -- nothing has yet
    said what kind of material it is -- so it was not shown to a model and
    nothing moved. It is waiting for you to say what it is, not marked sensitive
    and not judged on thin evidence.
    Held for review as "Not yet placed": no destination in this tree matched them
    well enough to decide without asking you.

Nothing was moved.
```

`68` §4 is fair to this: *"Nothing was misfiled anywhere… the product placed nothing it could not
justify, invented no destination, and moved nothing"* and *"The refusals are legible. A person
reading the report knows what stopped, that nothing moved, and that the product is waiting on them
rather than confused."*

It is also blunt about the result: *"Four people, four disks, one outcome. Nothing was misfiled and
nothing was lost… but nobody got an organisation, and nobody got a single file placed."*

Note what this means for reading the rest of this section: **almost none of the machinery described
above executes on a real run.** No model call, no graph edges, no group plan with a shared parent
that matters, no residual review, no correction, no reprojection. What runs is: build the index,
retrieve candidates, score, fail the threshold, hit the privacy gate, abstain, surface one residual
set.

---

## What looks wrong here

1. **`policy_id` does not travel on any decision, and a comment says it does.** `cli.py:113-114`
   justifies the shipped thresholds on the grounds that *"`policy_id` travels on every decision —
   change a number and change the id with it, or a replay silently compares two different rules."*
   `TwoCondition` (`records.py:280-296`) carries the two floats and no id, `PlacementDecision` has no
   policy field, and `placement/events.py` logs none. Two policies with different ids and identical
   numbers are indistinguishable in the store, which is the exact failure the comment claims is
   prevented. SPEC:802-804 requires both thresholds recorded and does not require the id; the code
   satisfies the SPEC and contradicts its own justification.

2. **Two of the four weighted scoring channels are unreachable, which caps the score at 0.714.**
   `GRAPH_RELATIONSHIP` and `STRUCTURAL_RELATIONSHIP` are weighted in `scoring._CHANNEL_WEIGHT`
   (`scoring.py:42-47`) and are never appended to `Candidate.channels` anywhere in `retrieval.py`.
   The reachable support scores are `{0, 0.286, 0.429, 0.714}`. Against `cli.py`'s threshold of
   `0.50`, **a placement in the shipped deployment is impossible without the accepted-group
   channel** — a file whose facts uniquely and correctly match one node scores `0.429`. The scale
   normalises by 7 for a maximum only 5 of which can occur.

3. **The score counts kinds of evidence, not amount.** `retrieval.py:146` deduplicates channels
   before `scoring.py:75` weighs them, so a candidate matching five of the subject's facts scores
   identically to one matching one. A five-fact match and a one-fact match against the same node are
   the same number on the record, and `alternatives[]` cannot tell a reviewer them apart.

4. **A budget deferral prints as an ordinary abstention, and tells the person the abstention was
   correct.** The record, the P2 envelope and `stage_output.py`'s three-way assert all keep deferral
   apart from abstention. `_abstention_explanation`'s default branch
   (`pipeline.py:603-607`) then renders it as *"No legal destination cleared §6.10's conditions
   (budget_deferred). Abstaining is the correct outcome; the evidence is retained and the file has
   not moved."* `cli.py:800` heads the block *"Waiting for you to say what these are"*, and `cli.py`
   reads `deferred_stage` nowhere. That is precisely the *"understood and found unimportant"*
   impression §8.6 exists to forbid, arriving in the one place a person actually reads. Done-means
   14 is satisfied in the record and defeated in the sentence.

5. **`multiple_supported_homes` is not in the SPEC.** It appears zero times in
   `planning/parts/P11-placement-residual/SPEC.md`, including in the Contract-out mapping table that
   enumerates the non-budget abstention reasons P2 must score as `abstained`. It is a good change —
   `59` §3a's finding is real — but it was made to a vocabulary the SPEC enumerates in three places,
   without amending any of them, while SPEC Open question 4 explicitly asks whether that vocabulary
   is closed.

6. **With no model injections, a context-supported match places without ever consulting the judge
   §6.6 designates.** `place_file` (`pipeline.py:372-401`) calls the model only
   `if inputs.model_path_available()`; when it is not available and `assessment.abstention_reason` is
   `None`, control falls straight through to the `place` at `pipeline.py:407`. The result is a
   `place` with `confidence_class = "context-supported group match"` and `requires_review = True` —
   so not auto-eligible — but §6.6's *"hierarchical destination judge"* was silently skipped rather
   than the decision being deferred. `PipelineInputs.model_path_available`'s docstring defends a
   model-free run on the grounds that *"§6.6 decides a unique direct match with zero model calls"*,
   which is a narrower claim than the code's behaviour.

7. **An outlier's decision row is stamped with the plan that excluded it.** `place_group`
   (`pipeline.py:834-860`) calls `place_file(..., group_plan_id=group_plan_id)` for **every**
   membership, then drops the flagged ones from `member_decisions`. `GroupPlan`'s invariant only
   inspects `member_decisions`, so it passes — but the stored row for the excluded file carries the
   `group_plan_id` of the plan that excluded it. Anything reading `placement_decisions` by
   `group_plan_id` reconstructs a plan that includes its own outliers.

8. **An excluded outlier is invisible in the report.** Its decision is not in
   `CorpusResult.decisions` (`pipeline.py:1258-1260` extends only `plan.member_decisions`), its file
   id is in `covered` so it is never re-placed, and it is therefore not in `unplaced` and never
   reaches a residual set. `cli.py` reads neither `group_plans` nor `excluded_outliers`. A file P9
   flagged as an outlier is decided, stored, and **never mentioned to the person** — the silent
   omission the residual screen exists to prevent, arriving through the group path.

9. **§6.8's "one coherent group plan" is computed, stored, and never shown.** `group_plans`,
   `excluded_outliers` and `unplaced_file_ids` have no reader in `cli.py` or `production.py`. The
   report groups files by `(outcome, destination, explanation)`, which is a grouping by *reason*, not
   by *plan*. The invariant at `groups.py:160-166` — the shared id *"is what makes the review surface
   show one plan rather than several unrelated file moves"* — is enforced against a surface that does
   not consume it.

10. **The shipped residual partition hardcodes `protected: False` and `sensitivity_status: "none"`
    for every set.** `cli.py:710-711`. `ResidualSet` argues at length (`residual.py:101-108`) that a
    null here would turn a protected set into an ordinary one, and then the one partition in `src/`
    asserts `False` unconditionally — including for a set containing a client's passport. It is inert
    today only because `require_model_call_permitted` has no caller; the moment §7 review is wired
    up, `ProtectedSetNotReadable` never fires.

11. **The shipped `evidence_for` hands every file every accepted group id.** `cli.py:692`:
    `group_ids=tuple(accepted_ids)`. The `ACCEPTED_GROUP` channel therefore fires for every file
    against every node associated with any accepted group, regardless of whether that file is a
    member. Given finding 2 — that a placement requires this channel — the only channel that can lift
    a file over the support threshold is one the deployment fires indiscriminately.

12. **Re-running against the same plan version raises `IntegrityError`.**
    `build_destination_index` (`index.py:518-524`) and `surface_residual_sets`
    (`residual.py:192-197`) both plain-`INSERT` with a deterministic `record_id`, and neither
    supersedes an existing row. Both tables carry supersede columns nothing writes.
    `placement_decisions` and `placement_group_plans` handle this correctly; the index and the
    residual sets do not.

13. **`ProtectedSetNotReadable` propagates out of `review_residual_sets`.** `pipeline.py:1344-1351`
    deliberately does not catch it, with a good argument. But the caller is a corpus-level loop: one
    protected set aborts the review of every set after it in `result.residual_sets`, including
    unprotected ones. That is the same shape as the defect `privacy.py:26-35` records and fixed for
    unclassified files — *"ONE such file refused an entire corpus"* — reintroduced one level up.

14. **The `explanation` on a residual decision states an outcome and nothing about the file.**
    `pipeline.py:1092-1095`: *"Residual review of set {set_id} returned {outcome!r}. The set-level
    decision authorised this review and the file has not moved."* §6.11 requires the explanation to
    *"state the actual basis"*. `{outcome!r}` renders as `'place'` or `'mark_review_later'` — a
    Python repr of a machine token, in the field a person reads — and the sentence claims *"the file
    has not moved"* even on `outcome = place`, which is the one outcome that becomes a move.

15. **`ResidualContext.lifecycle_policy_ref` is always `None`.** Every construction site
    (`pipeline.py:1026`, `1151`) passes `None`. §7.11's non-destructive lifecycle has a field on the
    record and no producer; the guarantee that a lifecycle policy is *"a review policy — never a
    deletion or expiry"* is currently true by vacuity.

16. **`ReturnTarget.id` is set to the file id, not to the target.**
    `pipeline.py:1073-1074`: `ReturnTarget(kind=qualifier, id=subject.file_id)`. The SPEC's field is
    the id of the group or packet the file is being returned **to** (SPEC's `return_target { kind,
    id }`, §7.9), and `outcome_for_action` (`residual.py:360-367`) refuses the action unless the
    caller supplies that target — then discards it and stores the subject's own file id. A consumer
    reading `return_target.id` learns which file, not which group.

17. **`_multi_home_decision`'s explanation is the same sentence for all three outcomes**, including
    `place` into a shared branch (`pipeline.py:993-996`). A user whose transcript was successfully
    filed into a shared branch is told that §6.9 *"permits a shared branch, a question, or an
    abstention"* — a statement of policy where the record has an actual answer, and the only §6
    `place` in the codebase whose explanation names no destination.

18. **A third of the part is inert, and the inert third is the half a person interacts with.**
    §7.13 lists it. The eight §7.7 actions, the whole §8.7 write path, `reproject`, and the group-plan
    surface are complete, argued, tested, and unreachable. `suppressed_nodes` is called on every
    placement and queries a table nothing can write to — a correctness check that can only ever
    return empty. Every one of these waits on P13, which does not exist.
