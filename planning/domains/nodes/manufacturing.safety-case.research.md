# manufacturing.safety-case — lab notes (R1b)

Date: 2026-08-27
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: manufacturing`, `launch: placeholder`, `parent_id: null`.
Output: [`manufacturing.safety-case.json`](manufacturing.safety-case.json). No prior draft existed.
Verdict: **node survives**, on two full legs and one partial. The charge that nearly killed it is stated
first and at length, because on this row the charge is the research.

## Sources

`RESEARCH-BRIEF.md` and the stamped assignment. `00-database-agent-product-design.md` by targeted
`grep -n`/`grep -o` only — two paragraphs carried everything (the dimension-recommendation rule and the
residual library); every quoted span was matched back verbatim before use. **`manufacturing.json`**, my
schema anchor, is the load-bearing source: its `recognition`, `template`, `work_types`,
`grouping_reasons` and `file_examples` were extracted mechanically and my node test is decided by a
property of those arrays. `engineering.risk-analysis-fmea` (JSON + memo) for depth calibration and for
the landed launch-row key set, which this row's JSON matches exactly including `node_test`,
`fields_note`, `also_holds_with_note` and `role_split_note`.
`grep -rl "manufacturing.safety-case" planning/domains/nodes/` returned five landed rows that had
already argued against me — `engineering.risk-analysis-fmea`, `engineering.aerospace-airworthiness`,
`engineering.process-plant-design`, `business_operations.risk-register`,
`manufacturing.environmental-compliance` — read at matched lines only. **Four of the five changed what I
wrote**, and two of them talked me out of edges I had drafted. `roster.json` for edge endpoints: this is
where `manufacturing.quality-management-system` and `manufacturing.hse-incident` surfaced, neither named
by the assignment's `must_consider_neighbors` (`engineering`, `logistics`, `business_operations`), and
both sharper than `logistics`, which turned out not to be a seam at all.
Not read: my anchor's `.research.md`. The JSON left nothing undecided — the deciding fact is an
**absence** in a machine-checkable array, and an absence is checkable without prose.

## THE CHARGE — the strongest case that this row should not exist

Seven disqualifiers. Three are live and one is nearly fatal.

**1. It is a document-type word — a `work_type` value, not a node.** This is the strongest attack and it
deserves to be. "Safety case" is a *name for a kind of document*, exactly like "calibration certificate"
or "work order", and the manufacturing schema already carries fifteen `work_types` including *"site HSE
inspection, permit, risk assessment or incident record"*. It also already proposes reuse of `record_type`.
On that reading this row is one value of one field, and CONNECTION's node test explicitly says a
difference that is only a work type is not a node. Every argument I could make about hazards is an
argument about a *value*.

**2. It is a duplicate of its own schema's default template.** The manufacturing default is branch-shaped
and one of its three branches is *site → asset → record type*. A safety case is site-anchored. If my
recommended order is site → asset → record type, then I am the default wearing a hazard-shaped hat, which
is precisely why `engineering.bill-of-materials` refused.

**3. It is a duplicate of a neighbour — and it is on the wrong schema.** Every landed row that argued
against me is on `engineering`, and each of them described me in almost the same words:
`engineering.risk-analysis-fmea` — *"a structured argument that a system is acceptably safe, assembling
and CITING analyses beneath a claim-and-evidence structure"*; `engineering.aerospace-airworthiness` —
*"the spine is a hazard list with claims and evidence"*. If three engineering rows can define me that
precisely from outside, the suspicion is that I am an engineering artifact the roster mis-shelved, and
that the honest outcome is a refusal routing my coverage into `engineering.risk-analysis-fmea` plus
`engineering.product-certification`.

**4. Never-alone evidence.** The word "safety" is the single most promiscuous token in an industrial
corpus. A row whose only evidence is a word cannot activate. `Safety Case.pdf` — a real filename, and
usually a blank template or a vendor brochure — is the trap.

**5. It is a lifecycle stage.** Design-stage safety report, pre-operational case, operational case,
periodic review: these read as gates on one artifact, and a gate is not a node.

**6. It is defined by an absence.** Rejected quickly: nothing here is "the file that is not an
inspection record". The material has positive structure.

**7. It is a medium/length/format.** Not live. PDF, workbook, deck and archive all occur.

### Defeating the live three

**Against 1 (work-type value).** The discriminator is that "safety case" does not name a document *kind*;
it names a **relation between documents**. The body of a safety case is mostly *pointers into the user's
own other files*: claim identifier on the left, an identifier of a separately held report on the right,
an adequacy slot beside it. Nothing else in the manufacturing schema's fifteen work types is a document
composed principally of citations of the corpus it sits in. That is not a stylistic observation — it has
a direct organizational consequence the schema default cannot express, because it makes this file the
**root of a group whose members live under other rows** (inspection records, calibration certificates,
FMEAs, competence evidence). A `record_type` *value* cannot be a grouping root; a template can.

The anchor confirms it mechanically. `manufacturing.json`'s `grouping_reasons` has six entries and none
is "one argued justification across its cited evidence". The nearest is *"one quality event across
initial report, containment, investigation, action and effectiveness evidence"* — anchored on a
**realised** event that must be closed. My grouping reason is anchored on a **postulated** event that
must never happen and has nothing to close. Different tense, different closure semantics, different
group shape. The charge fails.

**Against 2 (duplicate of the default).** I read all twelve deterministic clauses of the anchor. Not one
describes an argument, and none of its eleven `file_examples` is a justification. The nearest clause is
worded by that row as *"an HSE inspection, permit or incident structure tied to a controlled site or
asset, with hazard, control, responsible role and closeout evidence"* — and it keys on **closeout of an
identified finding**. A safety case has no findings to close; it has claims to substantiate. On
dimensions I differ by one insertion and one deletion, both evidential and both stated in the JSON: the
**edition** goes in (00: *"a parent dimension should provide the context required to understand the
child"* — two editions of an evidence index in one folder actively disagree with each other), and
**asset** comes out (00 bars a template that would *"create meaningless one-child levels"*, and a case
argues across many assets). The charge fails, with the honest caveat that under PR-6 both orders live in
prose, so leg two is argued at the standing the schema's own default has, not above it.

**Against 3 (wrong schema / duplicate neighbour).** This one I only half-defeat, and I say so.
`engineering.process-plant-design`'s landed memo settles the *substance* in my favour without my asking:
it left me unedged because *"a safety case argues that an* operating *installation is acceptable to a
regulator"* — that is a manufacturing object, an operating plant with a site and a controlled asset
population, not a design deliverable. The design-side hazard analyses belong to
`engineering.risk-analysis-fmea` and they do, on both sides of the edge I wrote. But the placement
tension is real and I will not smooth it: it is **NJ-SC-1**, with three alternatives spelled out. What I
will not do is edit the roster to resolve my own discomfort.

**Against 4 (never-alone).** Conceded entirely, and encoded rather than argued away: seven `never_alone`
entries, including the bare words, the bare filename, the regulator and operator names (00 bars using *"an
author or organization merely as a collector"*), the standard number and the duty-holder's name. The row
activates on *relations between labelled slots*, never on vocabulary.

**Against 5 (lifecycle stage).** The stages are values inside `work_types`, and they are values of the
same object: one installation's case, re-argued. The proof is that identifiers **persist across the
stages** — assumption A-14 raised at design stage is closed at operation under the same number. A
lifecycle stage does not carry stable identifiers across itself; an edition series does. This is also why
I put the edition *above* the leaf rather than treating it as a gate.

## The node test, all three legs

Stated in full in the JSON's `node_test`; the reasoning in brief, each leg on its own evidence.

**Leg 1 — detection signals: DIFFER.** Argued from the absence above, and filled by five structures, each
a relation among labelled slots rather than a word: the **claim-to-evidence index** (claim id → external
document id → adequacy slot, with no measurements of its own); the **argument decomposition** (goal /
strategy / solution / context nodes, or a numbering where every leaf is a solution naming a report); the
**safety-critical-element register** (function + performance requirement + assurance activity + verifying
party); the **tolerability demonstration** (residual risk resolved by an explicit proportionality
argument ending in a decision by a duty-holder role, not in a score); and the **currency apparatus**
(system boundary and operating envelope, numbered assumptions written as obligations, a material-change
or periodic-review trigger, an external acceptance or independent assessment). The anchor that separates
all five from a corporate document is the **named installation whose operation is being justified** plus
a stated criterion for *safe enough*.

**Leg 2 — dimensions: DIFFER.** Default branch site → asset → record type; researched order site →
edition → part of case. Insertion and deletion argued above and in `template.why`. Not time-first, on
00's own words. `record_type` may return as an optional leaf and is the **only** level on which a
work-type value may appear.

**Leg 3 — privacy: PARTIAL, and the JSON says so.** The *value* does not differ — the anchor is already
`potentially_sensitive` and already says person names are search/privacy observations rather than
destinations, so repeating that is not a difference. What differs is a **derivation** rule the schema
does not state. This is the one document in the schema that gathers, in one place, how a major accident
could be caused, what is relied on to stop it, and — decisively — **the operator's own known weaknesses**:
open caveats, deferred actions, elements running on a temporary arrangement. So no scenario phrase,
hazard name, barrier deficiency, open-caveat title or tolerability verdict may become a folder level,
destination or group label, because a directory or a proposal card carrying one publishes the operator's
worst case *and its current gap*. Read across from 00's Protected Records requirement that such material
*"must not cause filenames or content to be exposed in model prompts"* — marked **inference by
read-across**; this row does not claim to be a protected record. CONNECTION's test is disjunctive; legs
one and two carry the node.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence.

- **`Safety Case.pdf`** — the archetype. Almost always a blank template, a consultancy brochure or a
  standard's guidance annex. No installation, no claim identifiers, no evidence index. → Review Later.
- **`HAZOP_Unit-200_Node-12_Worksheet.docx`** — primary analysis data, not an argument. Belongs to
  `engineering.risk-analysis-fmea` in both directions; see the edge.
- **`Management-system-manual_Rev-6.pdf`** — the collision fixture proper; see below.
- **`Site safety inspection Plant 2.pdf`** — the anchor's own HSE clause owns it: an observation, a
  control, a responsible role, a closeout. Findings to close, not claims to substantiate.
- **`Fire risk assessment - Unit 4.pdf`** — statutory duty-of-care shape with assessor competence and
  persons at risk. `business_operations.risk-register`'s memo already routes this to
  `hr.workplace-health-safety`; I do not add a third claimant.
- **`Method statement and permit to work_Hot-work.pdf`** — an authorisation for one job on one day. A
  case justifies a standing operating state, not a task.
- **`Safety-training-matrix_Plant-2.xlsx`** — competence evidence that a case *cites*. Cited evidence
  never inherits the case's facts; that is the anchor's own propagation rule and 00's refusal to copy a
  course fact onto `HW 3.pdf` because a group exists.
- **`Asset-register_Plant-2.xlsx`** — rows are machines to be maintained. My register's rows are
  *functions to be assured*, with a verifying party. Adjacent shapes, different objects.
- **`Environmental-permit-variation_Plant-2.pdf`** — see the non-edge to
  `manufacturing.environmental-compliance` below.
- **`Product-safety-datasheet_Resin-X.pdf`** — a hazard communication about a substance placed on the
  market. No installation, no claim structure, no operating envelope.
- **`Board-paper_top-safety-risks_May.pptx`** — a register snapshot in a governance pack.
  `business_operations.risk-register` owns the register and the committee apparatus; no claim tree.

## The collision fixtures

**Primary: `Management-system-manual_Rev-6.pdf`, contested with
`manufacturing.quality-management-system`.** This is the closest thing on the roster to my evidence and
it is not mine, because both documents are an *apex file whose body is pointers rather than primary
data* — the exact property I used to defeat the work-type charge. The discriminator is what the
**left-hand column of the pointer table holds**: a clause reference of a management standard (theirs —
the argument is that a system of work conforms) versus a claim or goal identifier about a physical hazard
(mine — the argument is that residual physical risk to people is acceptable, ending in a tolerability
decision). Corollary stated on both sides: a safety-management-system *description* embedded inside a
major-hazard safety report does **not** move the file to that row; it is one required section of mine.

**Secondary: `Scan_safety-case-acceptance-letter_2026.jpg`.** Looks like the crowning evidence of this
row and frequently is not. OCR of a letterhead plus a case reference plus a decision sentence — but the
sentence may be an *acknowledgement of receipt* rather than an acceptance, and the letterhead address is
the **sender's**, not the installation's. Two `must_not_conclude` entries encode this. → Receipts and
Confirmations when OCR supports only acknowledgement.

**Tertiary: `Bowtie_loss-of-containment_LPG-vessel.png`.** Barrier vocabulary, legible structure, and no
installation, edition or claim identifier in the image's own evidence. Inferring a site from a vessel
label is the observation-as-fact error. → Review Later, and the scenario phrase may not become a group
label even if the group is right.

## Reciprocal boundaries

Five edges, every one naming the **same fixture bytes on both sides**. Three of the five adopt the
neighbour's own fixture and wording, so the pair reads consistently from either direction.

| Neighbour | Theirs when | Mine when | Shared fixture |
|---|---|---|---|
| `engineering.risk-analysis-fmea` | the guide-word grid and per-row consequences are present as primary data — *including* when bound into my appendix | the analysis appears only as a reference identifier under a claim | `HAZOP_Unit-200_Node-12_Worksheet.docx` (their fixture) |
| `engineering.aerospace-airworthiness` | submitted as substantiation closing a named code paragraph, with checklist rows and an approval instrument | the spine is a hazard list with claims and evidence plus an acceptability statement for a defined envelope | `SSA_MLG-Retraction_Rev-C.pdf` (their fixture) |
| `manufacturing.quality-management-system` | the pointer table's left column is a standard clause | the pointer table's left column is a claim identifier, ending in a tolerability decision | `Management-system-manual_Rev-6.pdf` |
| `manufacturing.hse-incident` | occurrence date and persons-involved slots — a realised event | no occurrence date; a barrier set with performance expectations inside a claim structure | `Loss-of-containment_Unit-200.docx` |
| `business_operations.compliance-audit` | the finding cites a clause of an external standard, with a corrective-action register | the finding cites a **claim identifier** and opines on whether the evidence supports it | `Independent-assessment-report_Unit-200_Edition-4.pdf` |

`aerospace-airworthiness` stated its half first and said both rows may hold the file for different
reasons. I agree and reciprocate — but express the co-holding via `also_schema` on the file example, not
in `also_holds_with`, which the contract reserves for schema rows. The `compliance-audit` edge is the
**argument-versus-organisation** seam; `aerospace-airworthiness` already teaches
**product-versus-organisation** against the same neighbour and the two do not overlap.

## Neighbours considered that got no edge

- **`engineering.process-plant-design`** — considered me and declined: *"close on hazard language, but a
  safety case argues that an* operating *installation is acceptable to a regulator. Covered by the
  `manufacturing` co-activation."* Reciprocating an explicit, reasoned non-edge with an edge would be
  unilateral. Honoured, and their sentence is what settles NJ-SC-1 in favour of alternative (a).
- **`business_operations.risk-register`** — considered me in its deepening pass and declined: *"a safety
  case is an* argument *submitted to a regulator, not an inventory; the structures do not resemble each
  other closely enough for the bytes to be contested."* I agree and reciprocate the non-edge. My
  register-shaped artifact is the safety-critical-element register, whose rows are functions with
  performance requirements — nothing like likelihood × impact with a treatment owner.
- **`manufacturing.environmental-compliance`** — considered me and declined: *"a major-accident-hazard
  demonstration is a different obligation with a different receiving object; if landed sibling research
  shows a true same-bytes mutex, R1c can add it."* I looked for the mutex on
  `Environmental-permit-variation_Plant-2.pdf` and did not find one: a permit *authorises an activity
  under conditions* and its anchor is a permit reference and a determination; a case *argues that harm to
  people is tolerable* and its anchor is a claim structure. Non-edge honoured; the invitation is
  answered in the negative rather than left open.
- **`government.permit-licensing`** — genuinely contested for the acceptance instrument, and left
  unedged **deliberately**. `environmental-compliance` established that a third claimant on
  regulator-facing documents makes the seam unresolvable, and writing a one-way edge into an unlanded
  government row would create exactly that. Escalated as NJ-SC-3.
- **`logistics`** — named by the assignment's `must_consider_neighbors` and refused. Dangerous-goods
  transport documents are a real world, but they travel with a consignment and anchor on a shipment; no
  fixture on this row is contested with one.
- **`manufacturing.nonconformance-capa` / `manufacturing.failure-analysis`** — both are realised-event
  rows. The `hse-incident` edge already carries the realised-versus-postulated discriminator in-family
  and a second and third copy would be noise.

## `proposed_fields` — empty, deliberately

The one key this material wants is the **case edition**, and it is the level my whole dimension argument
rests on. I did not mint it. `case_edition` invented for a single template row is the move that produced
thousands of private field names, and `engineering.process-plant-design` refused the parallel move for a
role key in its own memo. The three real options — reuse the universal `version_family` (probably the
wrong shape: it groups drafts of the same bytes, while two accepted editions are distinct documents both
of which must stay retrievable); promote `revision_or_baseline`, which the landed
`engineering.risk-analysis-fmea.json` lists among `facts_legal` on its DFMEA fixture, to a canonical
cross-schema key; or mint — belong to R1c. Filed as NJ-SC-2.

## Sparse-file discipline

Two `file_examples` carry `group_without_copying_facts: true`, and both are the same rule: an evidence
index and a bowtie image sit *inside* a correct group and must still not receive the group's facts. The
governing case is the reverse direction and it matters more — a calibration certificate cited by claim
C-12 does **not** become a safety case. This row is the root of a group whose members belong to other
rows, which makes it the most propagation-prone template I could have been given; the rule is stated in
`grouping_reasons` in 00's own terms.

## Audits run

- `python3 -m json.tool` on the output JSON: parses.
- Key set diffed against `engineering.risk-analysis-fmea.json` (landed launch template row): identical,
  including the optional `node_test`, `fields_note`, `proposed_fields_note`,
  `proposed_context_terms_note`, `work_types_note`, `also_holds_with_note`, `role_split_note`.
- All five 00 quotations re-matched verbatim by `grep` before use; all four residual `design_cite`
  strings matched verbatim from 00's residual-library paragraph.
- All five `collides_with` endpoints and every id named in this memo checked against `roster.json`.
- `also_holds_with: []` — schema↔schema only, per CONNECTION §5 and the dispatch warning.
- Every `collides_with` entry is an object with `domain`/`signal`/`provenance` and names the same fixture
  on both sides. No `design_cite` was attached to an edge; none had a verifiable span.
- `fields: []`, `proposed_fields: []`, no new key, no threshold, no handling class, no regex.
- Files written: exactly the two assigned.

## Recommendations to R1c (not made here)

1. **Reciprocals owed.** Five edges written from this side; `risk-analysis-fmea`,
   `aerospace-airworthiness`, `quality-management-system`, `hse-incident` and `compliance-audit` should
   carry the matching half in their own words. Two already do in substance.
2. **Context-term dedupe.** This row's `proposed_context_terms` deliberately overlaps
   `engineering.risk-analysis-fmea`'s, because my terminal nodes cite that row's artifacts. Dedupe
   centrally; neither row should trim unilaterally. `top event` is left to that row on purpose.
3. **If NJ-SC-1 resolves to `engineering`**, this row's `site` reuse becomes `design_item` + project and
   the edition argument survives unchanged; the memo is written so the move costs one field swap.

## NEEDS-JOSEPH (this node only)

- **NJ-SC-1 — schema placement.** Manufacturing (operating installation) vs engineering (design-side
  argument) vs a split. Alternatives argued above; this row is written for manufacturing on
  `process-plant-design`'s own reasoning, and does not touch the roster.
- **NJ-SC-2 — the edition level.** `version_family` reuse, `revision_or_baseline` promoted to canonical,
  or a new key. No key minted here.
- **NJ-SC-3 — the acceptance instrument.** This row or a `government` row; no edge written, to avoid the
  third-claimant problem `environmental-compliance` identified.
- **NJ-SC-4 — the register seam.** Safety-critical-element register vs `risk-analysis-fmea`'s carried
  hazard register. My discriminator (functional performance requirement + verifying party vs residual
  classification per hazard) is the thinnest boundary in this file and should be confirmed or replaced.
