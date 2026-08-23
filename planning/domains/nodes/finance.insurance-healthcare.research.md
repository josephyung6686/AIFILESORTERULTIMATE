# finance.insurance-healthcare — lab notes (R1b)

Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`, `parent_id: null`.
Output: `planning/domains/nodes/finance.insurance-healthcare.json`. No other file written.

**Provenance of this file.** The node JSON already existed as an untrusted partial draft from an
interrupted session; this memo did not exist. Every line of that draft was re-verified against the
authorities below and I take full ownership of it. What I changed is listed under *Salvage* near
the end.

## Sources actually used

- `planning/00-database-agent-product-design.md` — the source of truth. Every quoted span in the
  node file was verified mechanically before this memo was written: the node was walked as a JSON
  tree, every double-quoted run of 15+ characters extracted, whitespace- and
  smart-quote-normalised, and matched against a normalised copy of 00. **56 of 59 matched
  verbatim.** The three that did not are not 00 quotes and are not presented as such: one is a
  CONNECTION.md PR-8 quote (verified verbatim there, see below), one is the record_type *value*
  `"explanation of benefits"`, and one is a scare-quoted hypothetical user sentence inside
  `open_question`. No fabricated 00 quotation survives in the file.
- 00 **never uses the word "insurance"** and never names health coverage. That is why `provenance`
  is `inference` and why `design_cite` says so in its own text rather than claiming a design
  sentence. What 00 does supply, and what the node leans on, is: the Finance field sentence
  ("Finance files may use institution, account type, tax year, and record type"), the
  safety-domain sentence, the immediate-protection sentence, the template-definition sentence, the
  parent-dimension rule, the one-child/flattening warnings, the project-before-time ordering rule
  for record domains, the narrow-date rule, the word-boundary rule, the positional-weighting rule,
  the several never-alone rules (name ambiguity, missing EXIF, session-as-topic, extension as
  routing signal, unreadable-file filenames), the authorship-is-never-a-destination rule, and the
  nine residual definitions.
- `planning/01-product-design-structured.md` — used only as a locator. No quotation was taken from
  01's rendering; the residual quotations come from 00's own sentences.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (fixture 8 is the
  binding fixture for this row and is quoted in the node's `design_cite`).
- `planning/overnight/council/DECISION-BRIEF.md` — D1 as narrowed, D4, D6 and PR-6 treated as
  binding and not re-debated. They are the reason two facets this material genuinely has were
  *not* minted (below).
- `planning/domains/roster.json` — id, kind, schema_id and neighbours confirmed; **every id used
  on an edge was checked to exist on the roster** (10 collision targets and 5 distinct
  `also_schema` values, all present).
- `planning/domains/canonical_fields.json` — every `facts_legal` entry and every
  `dimension_order` entry checked against the canonical key set. All canonical, with the single
  documented exception of `account_holder` (below).
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` imported and checked against every
  `file_examples[].source_type` and every `file_kinds.source_types` member. All 14 examples and
  all 8 declared source types are members.
- Landed neighbours read for edge alignment and house style, **not rewritten**: `nodes/finance.json`
  (the schema row and its `account_holder` proposal), `nodes/finance.insurance-personal.json` and
  `nodes/finance.receipts-expenses.json` (nearest finance siblings), and — because this row sits on
  the finance/medical boundary — `nodes/medical.personal-health-records.json` and
  `nodes/medical.json`.

### Where CONNECTION.md beats the dispatch prompt

The dispatch prompt's edge table invites a template row to author `also_holds_with`. CONNECTION.md
§5 restricts that edge to **schema ↔ schema** pairs. CONNECTION wins, as instructed, and the
disagreement is recorded here as required. Consequences:

1. `also_holds_with` is `[]` on this row — empty by contract, not by omission. Fixture 8 places
   this situation's headline join (finance ↔ medical, reciprocal) on the **schema** rows, and it is
   already authored on `finance.json`. This row does not duplicate it.
2. The co-activations this situation actually produces are recorded per file in
   `file_examples[].also_schema`: `medical` on the EOB, the lab result, the archive, the pharmacy
   receipt and the claims CSV; `photos` on the card photograph and the portal capture; `identity`
   on the year-end coverage form; `career` on the enrollment confirmation.
3. `parent_id` is browse-only and R1b never authors it (PR-5). Left `null`.

## The node test — why this is a node and not padding

CONNECTION §2's test is disjunctive. This row clears **all three** clauses, which is why it was not
refused:

- **Dimensions differ.** The finance schema row's default is `institution → account_type →
  record_type`. Fixture 8 fixes this row at `institution → record_type`, and that is independently
  defensible: a household normally holds one health plan per carrier at a time, so an
  `account_type` level would open a branch with a single child — the exact shape 00 tells the
  canvas to warn about. `account_type` survives as an optional branch pattern for the person who
  genuinely holds two plans at one carrier.
- **Signals differ.** The schema row's `recognition` is the union across every finance situation
  and fires on labelled period-and-balance pairs. This row's discriminators are structures no
  other finance situation has: the claim-adjudication **set** (claim number + billed + plan-paid +
  patient-responsibility + date of service) and the card **pair** (member id + group number). The
  set/pair framing is load-bearing — a provider bill has a total and no plan-paid column, and a
  name beside one number is the identity collision, not this situation.
- **Privacy rules differ.** This is the one finance situation whose *ordinary* documents carry
  clinical content — a procedure or diagnosis column sits on a routine EOB — so the medical safety
  placeholder co-activates on its own evidence and protection runs on both readings before any
  model path. Separately, a coverage card is credential-grade: member id + group number is enough
  to transact against the plan, so it must not surface in a group summary, thumbnail caption or
  folder label even when the file is left in place. The finance schema row's general posture says
  neither of those.

## Files considered and rejected

Fourteen file examples landed. These were considered and deliberately left out, or kept only as
collision fixtures:

- **A blank claim form downloaded from a portal.** Rejected as a fixture in its own right: it is
  the same structure as the submitted claim form with every labelled slot empty, so it adds a
  `record_type` value rather than a discrimination problem. It is a `work_types` value.
- **A provider's "superbill" / itemised statement.** Genuinely tempting — it carries procedure
  codes, a date of service and amounts. Rejected as a separate example because
  `CVS receipt.jpg` and the `finance.receipts-expenses` collision already carry the same lesson
  (a total without a plan-paid column is not adjudication), and a second fixture would have been
  padding.
- **A wearable or app health export (CSV/JSON).** Rejected outright: that is
  `medical.wearable-health-exports`, and the medical sibling already names the three-way
  disambiguation (clinical summary / device telemetry / claims-and-coverage data) on its own row.
  Adding it here would have been me authoring the neighbour's fixture.
- **A dental or vision plan document.** Rejected: same structures, different plan line. That is a
  `record_type` / `account_type` **value**, not a node and not a fixture. Minting
  `finance.insurance-dental` would be the 574 failure at the situation level.
- **A life or disability policy.** Rejected as belonging to `finance.insurance-personal`; it is
  covered there and the sibling collision entry names the seam.
- **A `.vcf` of a carrier's member-services contact.** Rejected: 00 keeps contacts
  privacy-protected rather than a proposal basis, so the example would have had an empty
  `facts_legal` and taught only what the `.ics` fixture already teaches about file-kind-alone.
- **A claims-history spreadsheet export — KEPT, and added by me.** The draft declared
  `spreadsheet` in `file_kinds.source_types` with no fixture exercising it. Rather than delete the
  declaration I added `claims_history_export.csv`, because it is a real portal artifact and it
  earns its place by carrying a lesson no other example carries: the claim-adjudication column set
  fires the situation while the **carrier is simply absent from the file**, so `institution` must
  stay unknown rather than be inferred from the filename stem or the parent folder. It also
  isolates the row-versus-file distinction — one export is many claims, and the individual episodes
  are a P9 grouping question, not file-level facts.

## `proposed_fields` — argued, and deliberately empty

I propose **no** new fields. This is a positive finding, not an omission, and it is the part of
this row I want reviewed most carefully. The material has two facets with no canonical key, and
both were left unmodelled on purpose:

1. **The patient** — who a claim is *about*, distinct from the subscriber whose name the plan is
   in. A household EOB names both in two different labelled slots. Minting a `patient` or
   `covered_person` key would put a **person-identifying field on health material** into the shared
   vocabulary, which reverses D1-as-narrowed and PR-6 (medical writes no field rows) through a
   *template* row rather than through a decision. That is exactly the side door the contract's
   rule 10 exists to close.
2. **The plan sponsor** — an employer, distinct from the carrier that fills `institution`. Minting
   a `sponsor` key would add a second organization field beside `institution` with no 00 sentence
   behind it.

Both are instead recorded in `open_question` and pinned as `must_not_conclude` items on the two
file examples where they actually bite (`Explanation of Benefits 2026-03-14.pdf` and
`benefits_enrollment_2026.pdf`). The patient stays a P9 grouping question; the sponsor stays
evidence.

**`account_holder` is used but is not canonical.** It appears in `facts_legal` on five examples. It
is *not* in `canonical_fields.json`; it is a `proposed_fields` entry on the **finance schema row**
(`nodes/finance.json`), proposed with a `design` provenance from 00's "an account holder and an
issuing bank" role-split sentence, marked `destination_eligible: false`. This row therefore
consumes a proposal rather than making one — consistent with the contract's rule that a template
never copies its schema's field list. Flagged here so R1c does not read it as a mint by this row.
If R1c rejects the schema row's proposal, the five `facts_legal` entries here fall with it.

## `role_split` — empty, and why

`role_split` lives between canonical **field keys**. The two splits this vocabulary already needs
(`institution` vs `school`, `institution` vs `target_university`) are authored on the finance schema
row. The two further tensions this situation surfaces — sponsor vs carrier, patient vs subscriber —
have **no canonical counterpart key to split against**, and minting one from a template row to make
the split expressible is precisely the overnight pass's failure. Left empty; recorded in
`open_question`.

## Neighbours considered that did NOT get an edge

- **`medical.wearable-health-exports`** — no edge. The evidence does not overlap: telemetry has no
  claim, member or coverage structure, and the discrimination it needs is against
  `medical.personal-health-records`, which that row already authors. An edge here would be
  decorative.
- **`identity.credentials-passwords`** — considered because a portal login for a carrier is
  adjacent. No edge: a stored credential is not a coverage record, and nothing in this situation's
  evidence tempts that read. The `identity.core-documents` edge is the real one (card vs government
  credential) and it is authored.
- **`legal.personal-legal-matters`** — considered because an EOB is routinely evidence in an
  injury matter. No edge, deliberately: that is **multi-membership of a group**, not a collision of
  evidence, and it is recorded as a `grouping_reasons` entry ("a record that supports another
  purpose as well") rather than as an edge that would imply the two situations confuse each other.
- **`finance.subscriptions-utilities`** — considered because a premium notice is a recurring bill.
  No edge: a premium invoice carries a carrier and a plan, and the recurring-billing situation's
  discriminator is a service account with a usage or service-period structure. The overlap is the
  word "recurring", not the evidence.
- **`medical.dependant-child-health`** — **did** get an edge, after some hesitation. It earns one
  because a dependant's EOB names the subscriber and the patient in two labelled slots and both
  situations legitimately retrieve it; the edge exists to stop either side reading the subscriber's
  name as the patient's.

## Reciprocity status (for R1c)

- `medical.personal-health-records` **already names this row reciprocally** and its signal agrees
  substantively with mine (claim-and-amounts / member-plus-group here; result-and-reference-range,
  dispensing or clinical narrative there). Verified by reading that file; not edited.
- The other nine collision targets are authored one-way from this side and are **R1c's reciprocity
  debt**. Two of them (`finance.insurance-personal`, `finance.insurance-corporate`) are sibling
  rows being written in parallel in this same session, so R1c should expect to reconcile wording
  rather than assume absence means disagreement.
- `finance.json` and `medical.json` do not name this template row, and correctly should not —
  schema rows carry the schema-level `also_holds_with`, which is already there.

## Salvage — what I changed in the inherited draft

The draft was substantively sound and its quotations held up. Changes made:

1. **Moved `proposed_context_terms` and `proposed_context_terms_note` out of `recognition` to the
   top level**, matching the landed sibling key order exactly
   (`… recognition, proposed_context_terms, proposed_context_terms_note, work_types …`). The draft
   had nested them inside `recognition`, which no landed node does and which would have put
   proposed terms inside the object a consumer reads as fired signals.
2. **Added the `claims_history_export.csv` file example** (reasoning above), closing the
   `spreadsheet` source-type declared-but-unexercised gap. Examples went 13 → 14.
3. **Verified rather than changed** the rest: all 10 collision ids against the roster, all
   `also_schema` values against the roster, all `facts_legal` and `dimension_order` entries against
   canonical fields, all `source_type` values against `SOURCE_TYPES`, all residual names against
   00's nine, the presence of "a folder path" in every example's `must_not_conclude`, the empty
   `fields` / `proposed_fields` / `also_holds_with` / `role_split`, `sensitivity` restricted to
   00's phrase with no handling class, and the absence of threshold numbers and confidence scores.

## NEEDS-JOSEPH

- **NJ-IH-1 — Does the PATIENT become a canonical field?** A household EOB names a subscriber and a
  patient in two labelled slots; today only the subscriber has a (proposed) key. Three different
  products follow: (a) leave it unmodelled, which is what this row does — the patient stays a
  grouping question and no health-related person-field ever enters the vocabulary; (b) mint a
  patient/covered-person key, which reverses D1-as-narrowed and PR-6 and must arrive as a decision,
  not as a template edit; (c) something narrower, e.g. a protection-scope marker that is not a
  person's name. **This is not a modelling nicety:** without the facet, the product cannot express
  "protect my dependant's records more tightly than my own", and *with* it, a family member's name
  enters the shared vocabulary as a side effect of a folder recommendation. Joseph's call.
- **NJ-IH-2 — Does the plan SPONSOR become a canonical field?** An enrollment confirmation names an
  employer as sponsor beside a carrier as insurer. `institution` holds the carrier. Collapsing both
  into `institution` would destroy exactly the role separation 00 requires; adding a sponsor key
  means a second organization field with no design sentence behind it. Currently unmodelled and the
  employer stays evidence only.
- **NJ-IH-3 — Reciprocal statement of the finance/medical boundary, as CONNECTION.md requires.**
  Stated from this side: **an EOB, a coverage card, a claim form and a premium notice are this
  (finance) situation even though they carry clinical content; a lab result, a clinical narrative,
  a dispensing record and an immunization record are the medical situation even though they carry a
  health-sector organization name and a person's name.** The discriminator is *structural*
  (claim-and-amounts / member-plus-group vs result-and-reference-range / dispensing / narrative),
  never topical — "being health-related" decides nothing. Both **schemas** may co-activate on one
  file on disjoint evidence; that is the schema-level join and it is desirable, because it makes
  P7 run on both readings. The medical sibling's landed row already states the mirror of this. What
  is **not** settled and is Joseph's: whether a household filing a claim expects the EOB to live
  under the carrier (this row's recommendation) or under the person it is about — which is NJ-IH-1
  wearing a folder hat.
- **NJ-IH-4 — `launch` stayed `placeholder` per the roster row**, but this material is
  `potentially_sensitive` on two readings at once and the node recommends protection before any
  cloud or placement path. If Joseph wants the safety posture *active* at launch rather than
  described, this row wants `launch: safety` (the shape `finance.receipts-expenses` and the
  `medical.*` rows already use). I did not change it, because the roster is not mine to edit and
  the assignment stamped `placeholder`.
