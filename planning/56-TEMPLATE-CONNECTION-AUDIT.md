# 56 — Do the drafted templates connect? Built and run against the live records

Date: 2026-08-28 · Status: **AUDIT. Nothing built here ships; nothing under `src/` was edited.**
Method: every record in [`51-LAUNCH-TEMPLATE-DRAFT.md`](51-LAUNCH-TEMPLATE-DRAFT.md) was constructed
as a real Python object against `src/tree_design/templates.py` and pushed through
`src/tree_design/routing.py`. The harness lives in the session scratchpad, not the repo.

---

## 0. The answer first

**The draft is substantially correct as a set of records, and substantially wrong about what the
composer will do with them.**

| | |
|---|---:|
| Fragments that construct (3 shared + 19 carriers) | **22 / 22** |
| `TemplateDefinition` records that construct | **29 / 29** |
| `TemplateApplicability` records that construct | **54 / 54** |
| Applicability rows that bind — compose to a candidate, alone, on their own schema | **54 / 54** |
| `(definition, schema)` compositions that succeed | **32 / 32** |
| Compositions whose nesting the composer **changes** | **3** |
| Compositions where the composer produces the **non-recommended** candidate order | **3** (the same 3) |
| Candidates any two-domain branch produces | **0** |
| Claim (b) — a definition-local dimension sorts last | **CONFIRMED** |
| Claim (c) — the 3 shared fragments derive 00's Academic order | **REFUTED** |

Nothing refuses. Not one `MalformedTemplateRecord`, not one `ConfigurationRequired`, not one
`TypeError` across 105 records. The one record that refuses is **D30**, and the draft already
predicted that refusal (JC 7).

So the interesting finding is not a construction failure. It is this: **the composer never reads
`candidate_orders`.** The whole runtime-ordering mechanism the record was amended to carry — the
thing §5.3 and §5.8 turn on, the thing `41` §4.1 asked for and got — is a fifth concept in the
"fully built, fully tested, wired to nothing" list. `routing.py` derives its nesting from fragment
edges alone and never consults the definition's recommendation. Where the fragment edges under-
determine the order (three cases), the composer silently produces the order the draft explicitly
declined to recommend, and there is no code path by which the recommendation can win.

---

## 1. Construction — 105 records, 0 refusals

### 1.1 The 29 definitions

All 29 construct. Every gate the brief flagged as a landmine was cleared by the draft as written:

* **`DimensionOrder` exactly-one-default** — 29/29 name exactly one. No refusal.
* **All candidate orders cover the same role set** — 29/29. No refusal. The draft's Rule A
  ("depth is not identity") is what makes this hold: a shallower row is an `optional` role on the
  same order, not a shorter order.
* **A 2+-role recipe offers 2+ orders** — 26 definitions have 2+ roles and all 26 offer 2+ orders.
  The three single-role definitions (**D09** `def.preserved-root`, **D13** `def.purpose-packet`,
  **D20** `def.group-scoped-record`) offer one order each, which `_check_orders` permits because
  `len(roles) > 1` is false.
* **`sensitivity_policy_ref` non-empty** — 29/29. The record only requires a non-empty string, so
  all seven `sp.*@1` refs pass. Nothing validates the namespace.
* **`example_label_chains` carry no path separator** — the draft's chains are clean.

### 1.2 The one refusal: D30 (career)

```
MalformedTemplateRecord: 0 candidate orders are marked default. A definition RECOMMENDS
exactly one and the end user picks per branch (§5.3, §5.8); none means nothing can be
previewed, and two means the recommendation is undefined.
```

Constructed from `templates.py:361` (`_check_orders`, the `len(defaults) != 1` branch). This is
exactly what **JC 7** predicted, verified rather than reasoned. J-WIDE-2's "neither is the default"
is not constructible, and the record does not offer a third state.

### 1.3 The 22 fragments

All 22 construct. `TemplateFragment` requires only non-empty `roles` and non-empty `provenance`; the
19 carriers each name one context and that is enough. **The record cannot tell a shared fragment
from a carrier** — the shared/carrier distinction the draft draws in §3.1 vs §3.3 exists only in
prose, exactly as JC 2 says.

### 1.4 The 54 applicability rows

All 54 construct. The `role_bindings ⊆ allowed_fields` check (`templates.py:439`) passes on every
row because the draft derives each row's `allowed_fields` from its own bindings.

**Field legality against the LIVE catalogue, re-derived from `src/facts/fields.py`:**

`FIELD_ROWS` carries **37** rows, of which **24** are `destination_eligible`. Per declaring scope:

| scope | declared | destination-eligible | never a level |
|---|---:|---|---|
| `universal` | 10 | `target_school` · `client` | `file_type` `creation_date` `language` `duplicate_family` `version_family` `download_session` `authored_by` `our_firm` |
| `academic` | 5 | `school` `term` `subject` `work_type` | `instructor` |
| `college_applications` | 4 | `target_university` `application_cycle` `application_document_type` `purpose` | — |
| `research` | 5 | `project` `stage` `artifact_type` `lab` `venue` | — |
| `finance` | 4 | `institution` `account_type` `tax_year` `record_type` | — |
| `photos` | 7 | `capture_year` `event` `location` `media_type` | `people` `camera_information` `capture_date` |
| `code` | 2 | `repository` | `programming_language` |

The 54 rows bind **22 distinct field keys**. All 22 are in the live catalogue and all 22 are
destination-eligible, so **C2 passes on every one of the 54 rows**. The two destination-eligible
keys the draft never binds are `target_school` and `client`.

> **The brief's "30 fields across 6 schemas" is not the live figure.** The live catalogue has 37
> rows; 27 of them are declared at the six domain scopes (5·4·5·4·7·2) and 10 at `universal`.
> The draft's §1.2 table is also not the live figure — it reads `planning/domains/nodes/*.json`,
> which disagrees with `fields.py` on four of six schemas (`college_applications` there declares
> `school`, `research` declares `authored_by`, `code` declares four, `photos` declares six). **None
> of that breaks anything**, because C2 checks catalogue membership and destination-eligibility
> globally and never checks the field's scope against the row's `uses_schema` — see §5, record
> defect R4.

---

## 2. Composition — 32 of 32 succeed, 3 change the order

Every `(definition, schema)` pair was routed with a matching accepted group.
32 pairs, 32 candidates, 0 conflicts.

### 2.1 The three the composer changes

| Definition | Schema | Draft's recommended default | What the composer actually nests |
|---|---|---|---|
| **D01** `def.subject-work-record` | academic | `holder_institution › cycle_period › subject_anchor › artifact_kind` | `holder_institution › subject_anchor › cycle_period › artifact_kind` |
| **D02** `def.subject-work-record.third-party` | academic | `cycle_period › subject_anchor › artifact_kind` | `subject_anchor › cycle_period › artifact_kind` |
| **D03** `def.subject-work-record.household` | academic | `cycle_period › subject_anchor › artifact_kind` | `subject_anchor › cycle_period › artifact_kind` |

In all three the composer produces the definition's **second** candidate order,
`ord.affiliation-subject-period-kind` — the one the draft ships as the alternative. D01's default is
00's own sentence, *"An Academic template may define school → term → course → work type"*. The
composer files `PHYS1401` above `2026-Spring`.

The same three appear when each row is routed alone: `ap.academic.coursework`,
`ap.academic.teaching`, `ap.academic.homeschool`. The other 51 rows compose in the order the draft
intends.

### 2.2 Why — and it is not a bug in these three definitions

`merge_fragment_constraints` unions the fragments' `relative_order` edges and runs Kahn's algorithm
(`templates.py:602`). Kahn returns **one** linear extension of a partial order that usually admits
several, and the one it returns depends on the order the roles were first seen — which is the order
`fragment_refs` happens to list the fragments in. Family A's edge set is:

```
holder_institution -> subject_anchor      (frag.holder-affiliation-prefix)
cycle_period       -> artifact_kind       (frag.cycle-then-artifact)
subject_anchor     -> artifact_kind       (frag.subject-then-artifact)
holder_institution -> cycle_period        (frag.affiliation-prefix-to-cycle, the carrier)
```

**Nothing in that set orders `cycle_period` against `subject_anchor`.** Two linear extensions
satisfy it; the composer picks whichever the listing order produces. Over all 24 permutations of
D01's four `fragment_refs`, 12 give 00's order and 12 give the inversion. The draft's own listing
order is one of the 12 that inverts.

**This is a general property, not a Family A quirk:** the nesting a definition composes to is
sensitive to the sequence its `fragment_refs` are written in, which is not a semantic fact about the
recipe. Any future definition whose fragments under-determine the order inherits the same coin-flip.

### 2.3 The composer never reads `candidate_orders`

`routing.py` derives `position` from `merged.ordered_roles` and nothing else (`routing.py:271`).
It never touches `definition.candidate_orders` or `definition.default_order`. The only reader of
either is `templates.branch_dimension_roles`, and grep over `src/` finds **no caller** — only a
docstring mention in `health.py:92` and four tests. So:

* the recommended order cannot influence a preview;
* a user's `chosen_order_id` cannot influence a preview either, because the binding is written after
  routing and nothing re-derives the nesting from it;
* `MergedConstraints.optional_roles`, `.metadata_only_roles`, `.roles`, `.relative_order` and
  `.allowed_values` are computed by the merge and **read by nothing** — `routing.py` reads only
  `.ordered_roles`, `.order_was_overridden` and `.privacy_floor`.

**This is the fifth "built, tested, wired to nothing" concept**, beside §5.9's warnings,
`parent_concepts`, the residual disposition and `node_type=PROTECTED`.

### 2.4 Rule A collapses at routing

`route_branch` groups every eligible row by `(template_id, template_version)` and unions their role
bindings into one composition (`routing.py:361`, `:226`). Row-level depth has no effect. Four
definitions have rows of differing depth, and every shallow row gets levels it explicitly declined:

| Definition / schema | Levels the composition resolves | Rows that asked for fewer |
|---|---|---|
| D01 / academic | 4 | `continuing-education`, `online-course`, `study-abroad` (+1 each); `standardized-testing` (+2) |
| D11 / college_applications | 3 | `graduate-professional` (+1) |
| D14 / finance | 3 | eight rows (+1 each) |
| D22 / photos | 3 | `home-video`, `family-archive` (+1); `messenger-export` (+2) |

`academic.standardized-testing` says *"no institution in these files occupies the school role"* and
*"a test date is not a term"*; the composer gives it a `school` level and a `term` level anyway. The
`omitted` action the draft relies on (§4.0 Rule A) exists in `DIMENSION_ACTIONS` but no routing code
emits it — the router hard-codes `ACTION_SELECTED` (`routing.py:280`).

### 2.5 No two-domain branch produces a candidate

| Branch domains | Candidates | Conflicts |
|---|---:|---|
| `academic` | 7 | 0 |
| `code` | 3 | 0 |
| `college_applications` | 3 | 0 |
| `finance` | 7 | 0 |
| `photos` | 5 | 0 |
| `research` | 7 | 0 |
| `academic` + `research` | **0** | 12 conflicts: 10×C6 (refuse) + 2×C4 (resolvable) |
| `academic` + `code` | **0** | 9 conflicts: 8×C6 + 1×C4 |
| `academic` + `research` + `code` | **0** | 14 conflicts: 12×C6 + 2×C4 |
| `research` + `college_applications` | **0** | 10 conflicts: 10×C6, no C4 |

C6 fires because a template's rows cover one schema each, so the other domain's members are
"dropped". C4 fires on the cross-schema definitions D01/D02, whose academic and research rows offer
`subject_anchor -> ['project', 'subject']` and `artifact_kind -> ['artifact_type', 'work_type']`.

**This falsifies §6.3.** The draft's worked case — 00's own abstract that is both research material
and an application packet — routes to **zero candidates and ten C6 refusals** (no C4 — the two definitions share no role), not to "two
definitions, two one-schema bindings, one branch". C6 is REFUSE-class, so no user gesture clears it.

C4 on a mixed academic+research branch is WARN-class and a `CompositionOverride` can resolve it, but
that turns the draft's headline claim into its opposite: the cross-schema definition does not compose
silently across schemas, it *demands a user decision* the moment two of its schemas meet in one
branch. Within one schema at a time, D01 works exactly as drafted.

---

## 3. Binding — 54 of 54

Every row, routed alone on its own schema with a matching accepted group, produces a
`CompositionCandidate`. C1 resolves, C2 passes (all 22 field keys are live and destination-eligible),
C3 passes (only `ap.applications.purpose-packet` carries a `purpose_profile_ref`, and
`pp.application-submission@1` satisfies the `pp.` namespace at `templates.py:165`), C4 never fires
within a single schema, C5 never cycles, C6 covers, C7 takes `baseline`.

Three of the 54 bind at a nesting other than the one intended: `ap.academic.coursework`,
`ap.academic.teaching`, `ap.academic.homeschool` (§2.1).

Two rows carry content the pipeline silently discards:

* `ap.academic.iep-plans` declares `exclusions: ("work_type as a folder level",)`. `exclusions` has
  **zero readers** in `src/`. The one privacy rule in the launch set that removes a *dimension* has
  no enforcement — it works today only because the row also omits `work_type` from its bindings.
* D27's `artifact_kind` is drafted `metadata_only`. `ResolvedDimension` **has no `metadata_only`
  attribute**; `materialise_branch` takes `metadata_only_roles` as a caller-supplied argument
  (`materialise.py:97`) and nothing carries the fragment's or the dimension's flag to it. A
  metadata-only role that were ever bound would become a folder level.

---

## 4. The two named claims

### 4.1 Claim (b) — "a definition-local dimension sorts LAST" — **CONFIRMED**

Reproduced concretely. `def.venue-bundle` written the way the draft would have written it *without*
inventing a carrier — `addressed_org` as a definition-local dimension, only
`frag.subject-then-artifact` supplying edges:

```
definition default : addressed_org > subject_anchor > artifact_kind
fragments supply   : subject_anchor -> artifact_kind
router nests       : subject_anchor(idx=0) > artifact_kind(idx=1) > addressed_org(idx=2)
```

`routing.py:281` positions `addressed_org` at `position.get(role, len(position))` = 2, the leaf.
`research.conference-presentation`'s recipe — *"A branch named Poster is meaningless on its own"* —
is inverted exactly as the draft reports.

**And the draft's own remedy works.** With `frag.venue-prefix@1` (`addressed_org → subject_anchor`)
in `fragment_refs`, the same row composes to `addressed_org › subject_anchor › artifact_kind`. D29
as shipped is correct; the mechanism the draft warns about is real.

### 4.2 Claim (c) — "the 3 shared fragments derive 00's Academic order" — **REFUTED**

The draft calls this *"the single best piece of evidence in this document that the role cut is
right."* It is an artifact of Kahn's queue discipline.

```
merged constraint set:  holder_institution -> subject_anchor
                        subject_anchor     -> artifact_kind
                        cycle_period       -> artifact_kind

cycle_period vs subject_anchor is ordered by: NOTHING

the constraint set admits 3 valid topological orders:
    cycle_period       > holder_institution > subject_anchor > artifact_kind
    holder_institution > cycle_period       > subject_anchor > artifact_kind   <-- 00's
    holder_institution > subject_anchor     > cycle_period   > artifact_kind

over the 6 orders you can list the 3 fragments in, the merge returns:
    holder_institution > cycle_period > subject_anchor > artifact_kind   (3 of 6)
    cycle_period > holder_institution > subject_anchor > artifact_kind   (3 of 6)
```

The three fragments do not derive 00's order. They admit it, along with two others, and the
composer picks one by listing order. The draft's own reproduction script in the appendix happens to
list them in one of the three arrangements that produces 00's; §4.1's listing produces a different
one. **The draft says so itself and does not connect it:** §3.1 records that
`frag.cycle-then-artifact` *"fixes `cycle_period < artifact_kind` and asserts nothing else."* An
order that is not asserted is not derived.

Add the carrier D01 actually ships and it gets worse: the four-fragment set admits two orders, the
draft's listing produces the inversion, and 00's order is now a 12-of-24 coin flip.

**The fix is one edge.** Give the carrier `cycle_period → subject_anchor` as well as
`holder_institution → cycle_period` — the claim the draft is really making, stated as a constraint
rather than hoped for as an emergent property:

```
3 shared                             linear extensions=3   merge outputs over listing orders=2
3 shared + draft carrier hi->cp      linear extensions=2   merge outputs over listing orders=2
3 shared + carrier hi->cp->sa        linear extensions=1   merge outputs over listing orders=1
                                     -> holder_institution > cycle_period > subject_anchor > artifact_kind
```

One linear extension, one merge output, listing-order independent. That is what "derives" means.

**What survives.** The role cut is not damaged by this. `holder_institution › subject_anchor` (5/5,
11/11 at full corpus), `subject_anchor › artifact_kind` (14 rows, 3 schemas, zero reversals) and
`cycle_period › artifact_kind` (7/7) are all real and all attested. What is refuted is only the
claim that they *jointly imply* 00's four-level order without further input. They do not; the
missing input is a `cycle_period › subject_anchor` edge, which the corpus does attest —
`academic.coursework`: *"a course code recurs every term and the term is what keeps two enrolments
apart."* It just never made it into a fragment.

---

## 5. What must change, ranked — draft errors and record defects kept apart

### Record defects — these go to `build-p10-review`, and no draft edit can fix them

| # | Defect | Evidence | Consequence |
|---|---|---|---|
| **R1** | **`routing.py` never reads `candidate_orders` or `default_order`.** `branch_dimension_roles` — their only reader — has no caller in `src/`. | `routing.py:271`; grep over `src/` | The recommended order cannot reach a preview, and neither can the user's `chosen_order_id`. The runtime-ordering amendment is inert. **Highest severity: it is the feature the record exists for.** |
| **R2** | **Composition order depends on the sequence `fragment_refs` are listed in.** Kahn returns one arbitrary linear extension of an under-determined partial order. | `templates.py:602`, `:658`; §4.2 above | The same recipe nests two ways depending on authorship order. Silent, and it already bites 3 of 32 compositions. |
| **R3** | **`route_branch` unions every row of one definition, so row-level depth is discarded.** No code emits `ACTION_OMITTED`. | `routing.py:361`, `:226`, `:280`; §2.4 | Rule A does not hold at runtime. 16 of 54 rows would receive levels their own research explicitly refused. |
| **R4** | **C2 does not check that a bound field belongs to the row's `uses_schema`.** A `photos` row binding `subject_anchor → tax_year` composes cleanly. | verified: `resolve_role_to_field` checks catalogue membership + destination-eligibility only | The "exactly one `uses_schema`" guarantee is self-declared by `allowed_fields`, not verified. Adding a `fields_in_scope` check would close it. |
| **R5** | **`TemplateApplicability.exclusions` has no reader.** | grep over `src/` | The one dimension-removing privacy rule in the launch set (`ap.academic.iep-plans`) is decorative. |
| **R6** | **`metadata_only` cannot reach materialisation.** `ResolvedDimension` has no such field; `materialise_branch` takes it as a caller argument. | `templates.py:455`, `materialise.py:97` | A metadata-only role becomes a folder level. Latent — no launch row binds one — but D27 drafts one. |
| **R7** | **`optional_roles`, `allowed_values`, `validation_constraints`, `optional_branch_patterns`, `detection_signal_refs` have zero readers.** | grep over `src/` | Everything the draft writes into those five fields is documentation. Worth knowing before anyone spends a review cycle on their content. |
| **R8** | **No definition can serve a branch whose accepted groups span two schemas** — C6 refuses, unconditionally, and C6 is not overridable. | §2.5 | 00's mixed-domain purpose packet has no path. This is a design question, not a typo. |
| **R9** | `_check_orders` has no "no recommendation" state. | `templates.py:361` | JC 7, confirmed. Career cannot land as J-WIDE-2 words it. |

### Draft errors — these go back to `template-draft-launch`, and are cheap

| # | Error | Fix |
|---|---|---|
| **D-a** | **§3.4(c) is false as stated.** The three shared fragments do not derive 00's Academic order; they admit three orders and the composer picks by listing order. | Rewrite §3.4(c) as a *gap*, and add the missing `cycle_period → subject_anchor` edge to `frag.affiliation-prefix-to-cycle@1`. Verified: it collapses the merge to one deterministic output equal to 00's order. |
| **D-b** | **D01, D02, D03 violate the draft's own §3.4 rule** ("the default candidate order equals the order the fragments derive"). They derive the *second* order. | Same one-edge fix; then re-check all 29 against the rule mechanically rather than by reading. |
| **D-c** | **§6.3 does not compose.** The mixed-domain purpose packet produces 0 candidates and 10 C6 refusals. | Withdraw the worked example or restate it as R8, a blocked case. |
| **D-d** | **§1.2's field table describes `planning/domains/`, not `src/facts/fields.py`.** They disagree on four of six schemas; the live catalogue is 37 rows / 24 destination-eligible, not "30 live fields". | Label the table as the corpus view and add the live figures beside it. The 22 bound keys are all legal either way — the composition consequence is nil. |
| **D-e** | §3.4(b) is right and under-sold: it is not a definition-local quirk, it is R2 in a special case. | Cross-reference. |

### What is not wrong

The 29-definition cut, the 54-row join, the role vocabulary, the field legality and the three shared
fragments' *pairwise* evidence all survive contact with the code. Every record constructs; every row
binds; 29 of 32 compositions nest exactly as intended. **JC 1, JC 2, JC 3, JC 4, JC 5, JC 6 and JC 8
are unaffected by anything in this audit** — they are judgment calls about the corpus, not claims
about the code. **JC 7 is confirmed by execution.**

---

## Appendix — reproduction

The harness is five scripts in the session scratchpad
(`.../scratchpad/draft_records.py`, `audit.py`, `audit2.py`, `audit3.py`, `audit4.py`), run from the
repo root against `PYTHONPATH=src` with an `open_database` + `create_fields` fixture, on
branch `build/p6-p7-first-packages` at `3605aa1` plus the working tree of 2026-08-28. `templates.py`, `routing.py`, `validation.py` and `catalogue.py` were unmodified at run time; `upstream.py` carried 60 added lines from another lane, none of them in
`resolve_role_to_field`. It constructs
22 fragments, 29 definitions and 54 applicability rows as real objects, loads them through
`catalogue.load_catalogue`, and calls `evaluate_composition` / `route_branch` per
`(definition, schema)` pair, per row alone, and per multi-domain branch. Nothing was written to
`src/` and no existing test was touched.

---

## 6. Addendum, 2026-08-28 — the shipped library, after `RoleBinding.label` landed

`connect-p10-p11` reported that `def.subject-work-record` cannot route. **Confirmed, and it is four
times larger than reported.** Re-run against the library that has since shipped
(`src/tree_design/library/{fragments,definitions,applicabilities}.json`, 22 / 30 / 54) — not the
draft transcription §1–§5 used:

| | |
|---|---:|
| `(definition, schema)` pairs | 32 |
| pairs that compose | **25** |
| pairs that refuse | **7** |
| **multi-row pairs that compose** | **0 of 7** |
| applicability rows reachable | **25** |
| **applicability rows unreachable** | **29 of 54 (54%)** |

**Every multi-row `(definition, schema)` pair in the launch library refuses**, on the label branch of
C4 (`routing.py:359-370`):

| Definition / schema | Rows | Role that collides |
|---|---:|---|
| `def.issuer-record` / finance | **11** | `issuing_org → institution` under 10 names |
| `def.subject-work-record` / academic | 5 | `holder_institution → school` under 4 names |
| `def.capture-time-events.third-party` / photos | 4 | `capture_time → capture_year` under 4 names |
| `def.addressee-packet` / college_applications | 3 | `addressed_org → target_university` under 3 names |
| `def.capture-time-events` / photos | 2 | `capture_time → capture_year` under 2 names |
| `def.group-scoped-record` / finance | 2 | `artifact_kind → record_type` under 2 names |
| `def.research-lineage` / research | 2 | `subject_anchor → project` under 2 names |

The 11-row finance spine — the largest definition in the launch set — is unreachable, as is the
cross-schema headline. `connect-p10-p11`'s second point is also confirmed: `CompositionOverride`
carries `role_choices: role → FIELD` and the label block never consults `by_gate`, so no override
exists that could answer this. The refusal reports `overridable=True` because `C4` is WARN-class,
and nothing can act on it. **A gate that reports itself resolvable and offers no resolution is worse
than a refusal.**

### 6.1 Neither proposed fix is the right one

**Splitting the rows onto distinct definitions** would take 29 definitions to roughly 48 and make
the definition count equal the row count for every multi-row case — collapsing the many-to-many seam
the record exists for. It removes `def.issuer-record`'s 11-row reuse and `def.subject-work-record`'s
three-schema reach: the two results the draft was built to demonstrate. That fixes a router
behaviour by deleting the feature.

**A resolution rule that picks a label** is what `routing.py:360`'s own comment correctly refuses —
*"Taking the first would make the user-visible name depend on the order the rows were listed in"* —
which is R2 again, and the instinct is right.

### 6.2 This is R3, not a new defect

`RoleBinding.label`'s docstring states the design plainly: *"one role reads differently per schema…
which is a statement about the AUDIENCE, and the audience is what a `TemplateApplicability` row
selects."* The record makes the label **per row**. `evaluate_composition` then unions every row of
one definition in the branch (`routing.py:361`, `:286`) and demands the per-row labels agree. The
label is doing exactly what it was designed for; **the grouping is the defect** — the same grouping
that already discards row-level depth for 16 of 54 rows (R3).

The evidence is in the library itself. Where the label field is used the way its docstring argues
for — *across* schemas — it works and nothing refuses:

```
def.subject-work-record   academic  holder_institution -> school  'My school'
                          research  holder_institution -> lab     'My lab'
                          academic  artifact_kind -> work_type     'Kind of work'
                          research  artifact_kind -> artifact_type 'Kind of bench record'
                          code      subject_anchor -> project      'Experiment'
```

**All 7 collisions are within a single schema.** Not one is the cross-schema case the field was
added for.

The real fix is the one neither side named: **stop unioning rows the branch's evidence does not
select.** `eligible_rows` filters on `uses_schema` alone, and `detection_signal_refs` — the field
that says which situation a row recognises — has zero readers in `src/` (R7). A student's coursework
branch should route `ap.academic.coursework`, not coursework + continuing-education + online-course
+ study-abroad + standardized-testing merged into one recipe with four names for `school`. Filtering
by detection signal closes the label collision, R3's phantom levels and §2.4's Rule A collapse in
one change, because all three are the same bug.

### 6.3 Interim, if the filter is out of scope

Author **one label per `(definition, schema, role, field)`**. That is 15 keys and 60 individual
`role_binding` labels across 7 rows-groups, out of 74 keys total — a library data edit, no record
change. It costs nothing the docstring argues for, because per-audience naming *across* schemas
survives untouched; only per-row naming *within* one schema is given up, and that is precisely what
the router cannot represent today.

Ranking: this supersedes **R3** as the highest-severity item after **R1**. R1 makes the recommended
order unreachable; this makes 54% of the library unreachable.
