# R1c — record / subject / artifact key adjudication

Date: 2026-08-27
Status: **PROPOSAL for the product owner.** Nothing here is adopted. No `src/` file and no
`planning/domains/**.json` was edited by this pass.
Scope: the "what a record IS and what it is ABOUT" cluster.
On conflict: [`00-database-agent-product-design.md`](00-database-agent-product-design.md) wins,
then [`domains/CONNECTION.md`](domains/CONNECTION.md), then this document.

---

## 0. Counts, re-derived in this document

Every number below was recomputed from `planning/domains/nodes/*.json` in this pass.

| Fact | Value |
|---|---|
| Node rows on disk | 358 |
| `kind: template` / `kind: schema` | 335 / 23 |
| `refuse_node: true` | 44 |
| Non-refused templates | 291 |
| Schemas declaring live `fields` | 6 — `academic`, `code`, `college_applications`, `finance`, `photos`, `research` |
| Live field entries across those 6 | **30** (27 distinct keys; `school`, `project` and `artifact_type` are each declared twice) |
| Canonical keys in `domains/canonical_fields.json` | **37** |
| Rows carrying `proposed_fields` | 87 |
| Distinct proposed keys | 80 |
| Proposal instances | 170 |
| Keys with ≥3 proposers | 16 |
| Keys with exactly 2 proposers | 8 |
| Keys with exactly 1 proposer | 56 |
| Non-refused templates with a non-empty, fully-bound `dimension_order` | **54** |
| Non-refused templates with an EMPTY `dimension_order` | **237** |
| Non-refused templates naming an undeclared field in `dimension_order` | **0** |

**Two corrections to the premise, both verified in this pass.**

*(a) The live-field figure is 30, not 31, and it changed during this pass.* Commit `b2dbb08`
(landed 2026-08-27 22:29, mid-analysis) moved `finance.account_holder` out of `fields[]` and into
`proposed_fields`, because *"It was the only non-canonical key in the whole corpus."* Every other
number in this table was recomputed after that commit and is current. `account_holder` is
therefore a **1-signature proposal**, not a live field — see §2.7, where it is the one near-miss
this document declines to merge.

*(b) The binding ceiling is not the count of declarations.* `canonical_fields.json` holds **37
adjudicated keys**; 27 are declared by at least one schema and 10 are not. Seven of the ten are
universal fields that need no schema declaration (`file_type`, `creation_date`, `language`,
`duplicate_family`, `version_family`, `sensitivity_status`, `download_session`). The remaining
three — **`client`, `our_firm`, `target_school`** — are fully adjudicated vocabulary that no schema
has yet referenced. This matters to the cost arithmetic in §6: `law_practice` referencing `client`
and `our_firm` is a *declaration of an existing key*, not a mint, and it is the cheapest class of
decision in this whole exercise.

**The blocker is not "no key exists."** Zero templates fail because a `dimension_order` names an
undeclared field — the gate makes that impossible. 237 of the 291 non-refused templates carry an
empty `dimension_order` because **their schema declares no fields at all**. 17 of the 23 schemas
are fieldless. Every unlock claim in this document is therefore a claim about giving a fieldless
schema its first destination-eligible declared field, never about repairing a broken row.

---

## 1. The nine named keys — MINT or EXTENSION, and the decision

### Legend
- **EXTENSION** — the key already exists in `canonical_fields.json`; the ask is that another schema
  may reference it, possibly with the canonical `role` sentence widened. Cost: one line in
  `canonical_fields.json` plus one reference per schema. No new vocabulary.
- **MINT** — no canonical key holds the concept; a new row in `canonical_fields.json` is required.

---

### 1.1 `record_type` — **EXTENSION** (8 rows), plus one row asking a different question

**Proposers (9 rows, 4 schema families):** `manufacturing`, `manufacturing.energy-audit`,
`manufacturing.production-planning`; `resource_operations`,
`resource_operations.grid-connection`, `resource_operations.mining-operations`,
`resource_operations.oil-gas-operations`; `logistics`; `law_practice.ip-prosecution`.

**Eight of the nine are explicit extension requests and say so in their own words.**
`manufacturing`: *"REUSE, not a new spelling: the canonical Finance key already names what kind of
record a file is."* `logistics` goes further and refuses to raise a second thread: *"`manufacturing`'s
NJ-MFG-1 already asks whether the canonical Finance-role key is global enough for operational
records, and duplicating that question under a second schema would give R1c two threads on one
decision."* `resource_operations.mining-operations`, `.oil-gas-operations`, `.grid-connection` and
`manufacturing.production-planning` are all labelled `SECONDING, NOT MINTING` and each names the
private synonym it is declining: `record_class`, `mining_record_type`, `oil_gas_record_type`,
`connection_document_type`, `planning_record_type`, `resource_record_type`.

**DECISION: ADOPT as an extension.** Widen the canonical `role` from *"what kind of financial record
this is"* to *"what kind of record of a transaction or operation this is"* and permit
`manufacturing`, `resource_operations` and `logistics` to reference it. Keep `enum`; keep
`destination_eligible: true`; members stay values (`00`: *"The system may create new values … but
it should not invent new fields automatically"*).

**Refuse by name**, so no template author reaches for them:
`record_class`, `mining_record_type`, `oil_gas_record_type`, `resource_record_type`,
`connection_document_type`, `planning_record_type`, `document_kind`.

**The ninth row is not this question and must not be answered by it.**
`law_practice.ip-prosecution` names `record_type` only as *"the nearest existing key"* for an
**office-issued right identifier** (application number, publication number, registration number),
and its own stated preference is *option (a) — no key*: *"the identifier stays a literal
observation used for linkage during local review and is never stored as a fact."* Its reason is a
disclosure reason: *"An application number resolves in one public search to a named proprietor and
a technical disclosure."* **DECISION: take option (a).** Grant the row what it asked for and
record that `patent_number`, `application_number`, `registration_number`, `official_number`,
`right_id`, `ip_family` and `docket_number` are all refused. This row belongs to the identifier
collision in §4.3, not to the document-function extension.

Ceiling: `possible` on the extension, which is what all eight extension rows wrote. Every one of
them says the same thing in its own words — `resource_operations`: *"A labelled form title and its
supporting structure may establish a value. Extension, filename and isolated type words do not."*

---

### 1.2 `asset` — **MINT** (8 rows, 4 schema families). Adopt.

**Proposers:** `manufacturing`, `manufacturing.asset-register`; `resource_operations`,
`.grid-connection`, `.mining-operations`, `.oil-gas-operations`; `engineering.commissioning-handover`;
`logistics`.

This is the cleanest proposal in the corpus. One anchor (`manufacturing`), seven rows that adopt
its exact spelling and each name the synonym they are refusing:
`engineering.commissioning-handover` — *"this row deliberately adopts that spelling rather than
minting `installed_instance`, `tag_number` or `unit_id`"*; `logistics` — *"This row deliberately
does NOT mint `vehicle`, `registration` or `fleet_number`; a vehicle is a value of `asset`, and
minting a domain-shaped synonym for a key another schema already proposed is the 574's mistake in
miniature"*; `resource_operations.mining-operations` — *"a mining-specific `pit_id` would be a
private synonym."*

No canonical key covers it, and the elimination is done identically by all eight: `repository` is
software, `camera_information` is capture equipment, `project` is bounded work, `location` is the
Photos capture-place role.

**DECISION: ADOPT as a mint.** `destination_eligible: true`, `reliability_ceiling: validated`
(rule family: an asset-tag pattern inside a labelled Asset / Equipment / Instrument / Machine /
Well / Meter / Vehicle slot, corroborated by register-row structure or a local controlled asset
list — R2/R6 own the pattern).

**Carry one restriction onto the key, because `manufacturing.asset-register` is the reason it
exists:** `asset` is a destination dimension only for a file that carries ONE asset value. *"A
multi-asset register export has no single value and must not be forced under an asset level; it
belongs at the site level as the site's population document."* That restriction belongs on the key,
not restated by 8 templates.

**Two open sub-questions the rows raise and I do not close:**
(a) `manufacturing.calibration-record` NJ-CAL-1 — may one `asset` key carry both the producing
machine and the measuring instrument? (b) `manufacturing.production-planning` proposes
`production_line` and asks R1c to *"widen `asset` with a resource role or admit this exact key"* —
see §4.2.

---

### 1.3 `project` — **EXTENSION** (4 rows, 3 schema families). Adopt; and refuse `instruction`.

**Proposers:** `creative`; `construction_property.development-appraisal`; `law_practice`,
`law_practice.appeals`.

All four are extension requests. `creative`: *"ADOPTION PROPOSAL, NOT A NEW KEY. This row mints
nothing; `project` is already canonical."* `law_practice`: *"THIS ROW DECLINES TO MINT `matter`,
AND THE DECLINE IS THE ARGUMENT … `matter`, `case_ref`, `file_number`, `engagement_id` and `docket`
are ALL variants of this one key and none of them may be minted."*
`construction_property.development-appraisal`: *"NOT a mint — a REUSE of an existing canonical key …
Minting `instruction` here would ship a near-duplicate of a canonical key, the exact defect D6
exists to kill."*

**DECISION: ADOPT the extension** for `creative`, `construction_property` and `law_practice`.
Widen the canonical `role` from *"the named project a file belongs to; shared by the research and
code schemas"* to *"the named bounded undertaking or engagement a file belongs to"*.

**Two conditions the rows themselves attach, and both should be honoured:**

1. **`law_practice` cannot inherit canonical destination eligibility unchanged.** Its own words:
   *"a matter reference is DISCLOSIVE in a way a project name is not — `41127-0006 Hartley v Nash`
   names a dispute and two parties — so if `project` is adopted here it cannot inherit `project`'s
   canonical destination eligibility."* Its preference (a) is *"destination eligibility conditioned
   on explicit user approval."* That is a per-schema **narrowing**, which the design permits
   (`college_applications.school`: *"a schema may narrow one of its own fields, never widen it"*).
   Recommend: canonical stays `true`; `law_practice` narrows to user-approval-gated.
2. **The appellate cardinality question stays open and needs no field.** `law_practice.appeals`:
   *"an appellate artefact … carries an ORDERED PAIR … A single-valued `project` string can hold
   either half but cannot hold the relation."* Its own preference (b) — express the pair as a
   group-to-group edge in P9, not as a field — is correct and costs this cluster nothing. Its
   fallback is that the row *"stays fieldless and loses nothing, because the pair is used as
   ACTIVATION EVIDENCE, which needs no field to exist."*

---

### 1.4 `instruction` — **REFUSE.** It is `project` under a second spelling.

**Proposers (3 rows, all `construction_property`):** `construction_property`,
`.subcontract`, `.variation-claim`.

The anchor proposes it *with its own defeat attached*: *"Proposed with a live alternative, and R1c
should feel free to take the alternative. The alternative is to REUSE the canonical key `project`
… If R1c decides `project` stretches far enough, this proposal should be dropped rather than
shipped beside it — a near-duplicate of a canonical key is the exact defect D6's ratification
exists to kill."* And a fourth row on the same schema —
`construction_property.development-appraisal` — refuses to second it: *"This row therefore does NOT
second `instruction`, and says so openly rather than omitting it silently."*

**The deciding argument is consistency, and the corpus supplies it.** `law_practice` faced the
identical question about `matter` — *"a bounded professional engagement with an opening, a
reference repeated across content-incoherent artefacts, and a closure"* — and resolved it by
reusing `project`. A conveyance, a will and a standing retainer are exactly as un-project-shaped as
a tenancy, a sale instruction or a block-management appointment. The corpus contains the same
argument reaching two opposite conclusions; only one can ship.

**DECISION: REFUSE `instruction`; route `construction_property` to `project`.**

**The cost, stated because `construction_property.subcontract` stated it:** *"a WORKS PACKAGE is an
instruction that is not a project and is nested inside one. If `project` is stretched to cover it,
one job's five packages either collapse into one value or each become a sibling 'project' of the
job that contains them."* That cost is real and it is the price of one vocabulary. The mitigation
is inside the design already: a package is either a value of `work_type` beneath the job, or the
job/package pair is one `project` value (`00`: values are *"the changing, user-specific content
discovered from files"*). Neither requires a key.

---

### 1.5 `product` and `output_stream` — **ONE key, MINT.** Recommended spelling: `product`.

**`product` — 3 rows, 2 schema families:** `manufacturing`, `manufacturing.production-planning`,
`retail_hospitality`.
**`output_stream` — 4 rows, 1 schema family:** `resource_operations`, `.grid-connection`,
`.mining-operations`, `.oil-gas-operations`.

**`resource_operations` handed this fork to R1c explicitly:** *"Manufacturing's proposed `product`
is close but implies an article or formulation made through transformation … **R1c may widen
`product` to a neutral output key, but must not retain both as synonyms if one global role
works.**"* And `retail_hospitality` reached for `product` from a third world without minting:
*"REUSE, NOT A MINT … minting `sku`, `menu_item`, `line_item` or `room_type` would produce four
synonyms for one fact."*

**Signature counts mislead here and the correction matters.** `output_stream` has more rows (4 vs
3) but all four are one schema family; `product` has three rows across two independent schemas.
Independent-family count is the better signal of a shared concept, and on that measure `product`
leads 2–1.

**DECISION: ONE key, spelled `product`, `destination_eligible: true`,
`reliability_ceiling: validated`** (rule family: a labelled Product / Part / Material / SKU / Dish /
Room type / Commodity / Crop / Species / Fuel / Product Stream slot; a code-shaped token alone is
never sufficient — `retail_hospitality`'s own rule family). Record `output_stream`, `sku`,
`menu_item`, `line_item`, `room_type`, `ticket_class`, `commodity`, `crop`, `species` as **aliases**,
which `canonical_fields.json` defines as *"strings that must NOT become new keys"*.

**Two honest strains, both recorded by the rows themselves, neither of which is a structural error:**
- *Waste is not a product.* `resource_operations.mining-operations` names `overburden` and
  `waste rock` as values. Filing overburden under `product` is a vocabulary stretch in one folder
  name; a second key is a permanent fork in the organization language. Take the stretch.
- *Sold capacity is not an object.* `retail_hospitality` flagged it first: *"a room type and a
  ticket class are sold CAPACITY rather than an object, and if R1c judges that manufacturing's
  `product` cannot stretch that far, the correct outcome is to narrow this row's claim to goods and
  dishes and leave capacity unkeyed, NOT to mint a variant."*

**This is the least confident merge in this document.** If the product owner rejects it, the correct
fallback is the one `retail_hospitality` named: narrow `product` to manufacturing and retail goods,
let `resource_operations` keep `output_stream`, and **never ship both as roster-wide synonyms**.

**One eligibility divergence to carry:** `retail_hospitality`'s `product` proposal carries no
`destination_eligible` field at all and is marked destination-hostile in prose — *"a catalogue of
ten thousand SKUs would produce ten thousand one-child branches, which the validator sentence
rejects outright."* Canonical stays `true`; `retail_hospitality` **narrows to false**. This is why
`retail_hospitality` is excluded from my unlock arithmetic in §6.

---

### 1.6 `people_cycle` — **MINT** (4 rows, 1 schema family: `hr`). Adopt, conditional on a joint read with the period cluster.

**Proposers:** `hr`, `hr.compensation-planning`, `hr.onboarding-offboarding`, `hr.training-development`.

`hr`'s elimination is precise and correct as far as it goes: *"`fiscal_period` is a
business_operations proposal for a management calendar, `tax_year` is statutory, `term` is
academic, and `creation_date` says when bytes were made rather than which onboarding, review,
survey, pay, or consultation cycle they serve. This is purpose-bearing process identity, not
generic time."*

**The collision the `hr` rows did not name, and I must.** Canonical `application_cycle` is *already*
that concept in another world — a named bounded process instance that is not a calendar period
(`Fall 2026`, an admissions cycle). `people_cycle` (`FY2026 annual review`, `2026 graduate intake`,
`March 2026 payroll run`) is the same role in the HR world. Under this document's own routing
principle, that would make `people_cycle` an EXTENSION of `application_cycle`, not a mint.

**Why I still recommend the mint.** `canonical_fields.json` scopes `application_cycle` by 00's own
College-applications sentence, and `purpose` — from the same sentence — is already pinned there by
PR-1 (*"purpose stays exactly where 00's sentence puts it … No per-domain purpose clones may be
minted"*). Stretching a second key out of that sentence contradicts a ratified provisional
resolution. A mint is the cheaper decision.

**DECISION: ADOPT as a mint**, `destination_eligible: true`, `reliability_ceiling: possible` — the
ceiling every one of the four rows wrote, and `hr.onboarding-offboarding` gives the reason no rule
family can raise it: *"the same date appears as document date, effective date, probation end,
payroll cut-off and notice expiry."*

**CONDITION:** this key must be adjudicated in one sitting with the period cluster
(`fiscal_period` 12, `reporting_period` 6, `record_period` 3, `planning_period` 1, `aid_year` 1)
so the roster does not finish with six bounded-period keys. That is the period adjudicator's
cluster, not mine; this is a hand-off, flagged in §7.

**One ordering correction the rows earned:** the `hr` anchor's prose default puts work type first;
two of its own templates contradict it with better arguments. `hr.onboarding-offboarding` wants the
cycle to LEAD (*"An intake or a leaver event is the only thing that makes a checklist, an induction
agenda, a handover receipt, an acknowledgement and an exit note intelligible together"*);
`hr.training-development` wants it BELOW the programme (*"a cohort is unintelligible without its
course while a course is perfectly intelligible without a cohort"*). Both are right for their own
situation. That is a template-ordering matter, not a key matter — record it and let P10 carry it.

---

### 1.7 `subject_of_record` — **MINT** (6 proposing rows, 3 schema families; 15 rows touch it). Adopt.

**Proposers:** `clinical_practice`; `law_practice`, `law_practice.depositions-testimony`,
`law_practice.estates-administration`, `law_practice.expert-materials`; `nonprofit`.
**Nine further rows reference it in prose without proposing it** — `clinical_practice.patient-chart`,
`.licensure-credentialing`, `.teaching-material`, `law_practice.closing-binder`, `.criminal-defence`,
`.family-law`, `.investigation`, `.opinions-advice`, `nonprofit.grant-reporting` — which makes 15 of
358 rows structurally dependent on a key that does not exist.

The elimination is done once and never re-derived, which is the behaviour this pass is trying to
reward. `clinical_practice`: *"`authored_by` is the opposite role and is the role this holder
occupies. `client` is a commercial engagement counterparty … and a patient is not a client of the
person who wrote the note. `people` is the photos-side co-occurrence facet. `institution` is the
facility, not the person."* `nonprofit` adopted it rather than minting `beneficiary`; `law_practice`
adopted it rather than minting `party`, `adverse_party`, `deponent` or `witness`;
`law_practice.expert-materials` refuses `expert` and `author_role`;
`law_practice.estates-administration` refuses `deceased`, `estate_of`, `testator` and `decedent`.
Nine refused synonyms, zero minted.

**DECISION: ADOPT as a mint.** `reliability_ceiling: possible` — `clinical_practice`'s own pinning
is the right one and the reason is not evidential: *"A labelled patient block is a `direct` slot in
the P4 sense, but the LEGAL question — may the product store another person's identity as a stored
fact at all — is not this row's to answer."* `destination_eligible: **false**`, seeded on the key —
see §2, which is where the `student` rows change this answer's shape.

---

### 1.8 `student` — see §2. **It is the same key as `subject_of_record`.**

---

### 1.9 `output_stream` — folded into §1.5. **REFUSE as a separate key.**

---

## 2. `student` and `subject_of_record`: one key or two?

**Answer: ONE key, spelled `subject_of_record`, with `student` recorded as an alias.**

### 2.1 The rows say the same sentence

`academic.k12-schooling`: *"No canonical key names the person a record is ABOUT when the holder is
not that person."*
`clinical_practice`: *"`subject_of_record` for the person a record is ABOUT as distinct from the
person who holds it."*

Those are one sentence. Both sides eliminate the same four candidates for the same reasons —
`authored_by` is the producer, `people` is photo-side and seeded ineligible, `subject` means the
course, the institution keys name institutions not humans. Both propose the identical
`role_split_with: ["authored_by"]`. Both cite the same 00 sentence as their licence: *"The system
must separate roles that happen to contain the same entity type."*

### 2.2 The corpus contains a row that sits on both sides at once, and it decides the question

`law_practice.family-law`: *"a named CHILD is a subject_of_record who is not the client, not the
counterparty, and cannot consent at any age."*

That is the **same person-type** as `academic.homeschool`'s and `academic.k12-schooling`'s child.
If the roster carried two keys, one child in a custody file would be a `subject_of_record` and the
same child's report card would be a `student`, and the product could never link them, never protect
them consistently, and never explain to the parent why one folder redacts and the other does not.
That is precisely the "one concept, two spellings" failure — and here it fragments a **protection**,
not merely a folder level. `academic.homeschool` anticipated the shape of this when it said the same
thing about its own sibling: *"The SAME key academic.k12-schooling already proposes, for the same
gap, deliberately not re-derived under a second spelling — R1c should merge these into one canonical
row, never two."*

### 2.3 The role-name test kills `student` as the spelling

`law_practice.expert-materials` states the rule that decides the naming: *"`expert` and `author_role`
would both encode a role name in a key, and the schema already ruled that a role name cannot carry a
node."* `student`, `patient`, `beneficiary`, `deponent`, `decedent`, `witness` and `child` are all
role names for one relation. `subject_of_record` names the relation. **Keep the relation, alias the
roles.**

Aliases to record on the key: `student`, `patient`, `beneficiary`, `deponent`, `decedent`,
`testator`, `witness`, `data_subject`, `child`, `service_user`, `member`.

### 2.4 The real conflict is destination eligibility — and it is resolvable under one key

This is where the merge is expensive and I will not smooth it.

| Side | Rows | `destination_eligible` asked for |
|---|---|---|
| Practitioner | `clinical_practice`, `nonprofit`, `law_practice` + 3 templates | **FALSE, and demanded ON THE KEY** |
| Household | `academic.k12-schooling`, `academic.homeschool`, `applications.k12-admission` | **"recommended true, but this is Joseph's call"** |

The practitioner side is emphatic and asks that the ban not be restated per template — `nonprofit`:
*"asks that `destination_eligible` be FALSE for the nonprofit family regardless of what
clinical_practice needs, and that the reason be recorded on the key rather than left to each
template."* `law_practice.estates-administration` goes one step further for a dead subject: *"unlike
the anchor's client level it must not become eligible on user approval either."*

The household side is not symmetric with that: all three rows explicitly defer
(*"recommended true, but this is Joseph's call and R1c's to place, not this node's"*), and all three
already carry a working `dimension_order` today. They lose folder quality, not function.

**RECOMMENDATION: seed `destination_eligible: false` on the key, and record ONE widening question
for the product owner.** Three reasons:

1. **It matches the precedent the corpus set for every person-shaped key it has.** All three
   person-shaped canonical keys are seeded ineligible: `people` (photos) — *"Widening is Joseph's
   call (ROSTER.md NEEDS-JOSEPH), never a schema's"*; `instructor` (academic); `authored_by`
   (research). `finance`'s `account_holder` proposal asks for the same — *"a search and privacy
   field … it must never become a folder level"*. A fourth person-key seeded true would be the only
   one.
   **The honest counter, stated because the `student` rows lean on it:** the canonical table *does*
   seed one target-side key eligible — `client`, *"eligible because 00 places a document's purpose,
   project, subject, or target above its authorship as the informative basis for placement"*. But
   `client` is an **organization**, and 00's prohibition it is escaping is the authorship one, not a
   privacy one. No canonical key names a *person* and opens a folder level. That is the line this
   recommendation keeps, and the widening below is the request to cross it deliberately rather than
   by default.
2. **Narrowing is legal, widening is not.** `college_applications.school`: *"a schema may narrow one
   of its own fields, never widen it."* Seeding `true` would let any future schema — including one
   generated by the novel-domain path in `planning/46-NOVEL-DOMAIN-HANDLING.md` — open a folder
   level named for a third party **by default**. Seeding `false` makes the dangerous direction the
   one that requires a human.
3. **The widening mechanism already exists and is the one `people` uses.** Record the household
   case as a NEEDS-JOSEPH widening on the key, scoped to `academic` and `college_applications`,
   where the subject is the holder's own dependant and the folder name is the household's existing
   filing vocabulary.

**My recommendation to the product owner on that widening: say yes, scoped to those two schemas.**
The household case is one of the most common consumer situations in the corpus and the current
default is demonstrably wrong for it. `academic.k12-schooling` states the damage in its own
`template.why`: *"The order this situation actually wants is child → school year → work type, and no
declared field names the child."* `applications.k12-admission` names the failure mode:
*"a household applying for two children in the same season has no declared field that separates
their two packets, and every one of this template's high-weight signals (entering grade, entry year,
target school) can be identical across the two."* Two children's admission packets currently merge
into one indistinguishable folder. That is a sorting-engine defect, not a preference.

### 2.5 The naming hazard, flagged as `academic.k12-schooling` asked

The row warned: *"`subject` in this catalogue means the course, not the human being — a naming
hazard R1c must not resolve by overloading `subject`."* This recommendation does not overload
`subject`, but `subject` and `subject_of_record` will sit adjacent on the `academic` schema. That is
a readability cost, not a correctness one, and renaming `subject` is closed by D6 (ratified
2026-08-21). Recorded, not resolved.

### 2.6 What is NOT `subject_of_record`

`law_practice.opinions-advice` drew this boundary itself and it should be kept: *"`subject_of_record`
… is the person a record is ABOUT; the addressee is the person a record is TO, and on an
enforceability opinion the subject is an instrument and the addressee is a bank — two different
slots on the same page."* `addressee` is a different concept; see §4.4.

### 2.7 The near-miss I decline to merge: `finance.account_holder`

`account_holder` is the closest thing in the corpus to a fourth `subject_of_record` proposer, and
its own note reads like one: *"a safety domain needs to know whose record this is in order to
protect it and to keep another household member's statement out of a group."* That is the
subject-of-record function almost word for word.

**Keep it separate anyway, for two reasons the row itself supplies.**
- Its `role_split_with` is **`institution`**, not `authored_by`. It is the holder-vs-issuer split
  that `00` names directly — *"A finance document may mention an account holder and an issuing
  bank"* — and it is one of the four role fields `CONNECTION.md` section 6 seeds from §3.8.
  `subject_of_record`'s split is producer-vs-subject. Different axes.
- The defining condition of `subject_of_record` is that **the holder is not that person**. On an
  ordinary statement the account holder *is* the user. The overlap is only the edge case (a joint
  account, another household member's statement), and an edge case is not a concept.

Recorded because a careless pass would swallow it, and because if the product owner disagrees the
merge is defensible — but it must then be argued from the household-member case, not assumed.

---

## 3. The type-key family — the largest one-concept-many-spellings hazard in the corpus

Six spellings of "what kind of document/artifact is this" are live or proposed:
`record_type` (live, finance), `work_type` (live, academic), `artifact_type` (live, research+code),
`application_document_type` (live, college_applications), `media_type` (live, photos), plus
`engineering_artifact_type` (proposed, `engineering`).

**Collapsing them is not available.** `00` itself names five of them separately, one per domain
sentence, and `00` wins on conflict. `engineering` asked the right question anyway:
*"R1c should either widen canonical `artifact_type` and reuse it here or accept this role-specific
key; **it must not retain both as duplicate spellings**."*

**DECISION: keep the five 00-named keys; mint none; route every new request by role.** The routing
rule, derived from how the corpus already uses them:

| Key | Role | Route here when the document… |
|---|---|---|
| `work_type` | the work product of a bounded engagement or course | …**is** the work: syllabus, homework, pleading, motion, affidavit, opinion |
| `artifact_type` | an artifact in a making process | …is an **output of making**: manuscript, figure, notebook, export, master, drawing, CAD model, schematic, calculation |
| `record_type` | a record of a transaction or operation | …**evidences that something happened**: statement, invoice, proof of delivery, batch production record, production return, meter read |
| `application_document_type` | role inside an application packet | scoped to `college_applications` by 00's sentence |
| `media_type` | kind of capture | scoped to `photos` by 00's sentence |

**Every contested row routes cleanly under this rule:**
- `engineering`'s requirement / drawing / CAD model / schematic / calculation / interface definition
  → `artifact_type`. **REFUSE `engineering_artifact_type`**, which is what the row offered as its own
  first option.
- `creative`'s working file / export / proof / master / stem / cut / render → `artifact_type`.
  `creative` already reached this answer alone: *"no sibling may ask for a node per media form, and
  no sibling may mint a `deliverable_type` or `asset_type` synonym."*
- `law_practice`'s pleading / motion / order / affidavit / exhibit / opinion → `work_type`, exactly
  as `law_practice` proposed, and it supplies the enforcement sentence: *"R1c should refuse any
  request for a `document_kind`, `pleading_type`, `filing_type` or `instrument_type` key as a
  respelling of it."*
- `manufacturing` / `logistics` / `resource_operations` → `record_type` (§1.1).

**Boundary cases are resolved by the design, not by a sixth key.** A drawing on a manufacturing site
can carry `artifact_type` from `engineering` and `record_type` from `manufacturing` when both
schemas activate — `00`: *"One file may hold facts from more than one domain without losing
information."*

**Same treatment for `stage`.** `creative` adopts canonical `stage` and refuses `creative_stage`
(*"A `creative_stage` key would be precisely the 574's failure — one concept in two vocabularies"*).
`engineering` proposes `lifecycle_stage` and exposes the same fork: *"widen `stage` once or retain
this role-specific key; do not ship both as synonyms."* **DECISION: widen `stage`; REFUSE
`lifecycle_stage`, `creative_stage`, `design_maturity`.** Draft→under review→published (research),
brief→draft→approved→delivered (creative), and concept→preliminary→detailed→qualification→released
(engineering) are one role with three value vocabularies, and value vocabularies are values.

---

## 4. Triage of the 56 single-proposer keys

The lead's instruction was to triage, not to adjudicate each. Four buckets.

### 4.1 EXTENSIONS of existing canonical vocabulary, disguised as proposals (6 keys) — highest value per decision

| Key | Row | Live field it extends | Recommendation |
|---|---|---|---|
| `work_type` | `law_practice` | `work_type` (academic) | **ADOPT** — see §3 |
| `artifact_type` | `creative` | `artifact_type` (research, code) | **ADOPT** — see §3 |
| `stage` | `creative` | `stage` (research) | **ADOPT** — see §3 |
| `account_holder` | `finance` | — (**not** a live field since commit `b2dbb08`) | **MINT, 1 signature.** Not an extension. Adopt with `institution` as its `role_split` partner; `destination_eligible: false`. See §2.7 |

`law_practice`'s `work_type` is the **single cheapest high-value decision in this cluster**: it is a
one-line reference to an existing key, and it is the only destination-eligible field
`law_practice` can obtain from my cluster (its `project`, `record_type` and `subject_of_record`
proposals are all `destination_eligible: false` as proposed). It alone unlocks 28 templates.

`law_practice`'s `our_firm` proposal is the same shape and is **not** a duplicate: `our_firm` is
canonical but declared by no schema (§0b), so referencing it is a real, one-line decision. The same
applies to its `client` proposal, which belongs to the entity adjudicator.

### 4.2 Genuine collisions — an early signal of a concept other rows need under another spelling

**(a) The bounded-occurrence collision — 7 spellings, 10 proposal instances, 6 schemas.**
`quality_event` (2, `manufacturing`), `work_order` (2, `manufacturing`), `personnel_case` (1, `hr`),
`consignment` (1, `logistics`), `trading_occasion` (2, `retail_hospitality`), `build_event` (1,
`engineering`), `campaign` (1, `nonprofit`).

Three of these rows independently ask for exactly this adjudication.
`manufacturing`: *"The alternative is a broader globally canonical `case` key; R1c should prefer
that if another schema proves the same semantics rather than retain a manufacturing-only synonym."*
`manufacturing.maintenance-work-order`: *"R1c should prefer folding this into the broader canonical
`case`/`event` key already asked for in the manufacturing anchor's NJ-MFG-2 rather than ratifying a
manufacturing-only synonym."* `nonprofit.fundraising-donor`: *"this row's FIRST preference is that
R1c simply reuse [`project`] … explicitly DO NOT mint `appeal`, `fund`, `fund_code`, `source_code`
or `solicitation`."*

**My read, split three ways:**
- **True bounded occurrences → one key** (canonical `event`, role widened from the photos capture
  occasion to *"the bounded occurrence a set of records is about"*): `quality_event`, `work_order`,
  `personnel_case`, `consignment`, `trading_occasion`. `logistics` objects to `event` — *"`event` is
  the Photos capture-occasion key and carries a time-primary reading this family must not inherit"* —
  but time-primacy is a property of 00's **photos template order** (capture year then event), not of
  the field, so the objection is answerable by widening the role sentence.
  `manufacturing.maintenance-work-order`'s objection to `quality_event` (*"forcing [a routine job]
  into a nonconformance key would make every planned job read as a quality escape"*) dissolves under
  a neutral key name, which is why the neutral name matters.
- **`campaign` → `project`**, which is the proposing row's own first preference.
- **`build_event` → `asset`, not the occurrence key.** `engineering.prototype-build` names it an
  event but describes a thing: *"No canonical or currently-proposed key identifies ONE MADE
  ARTICLE."* An enduring identified physical instance is what `asset` is. Lower confidence than the
  rest; the row's own fallback (*"if R1c declines the mint, this row's recommended order collapses
  to design_item alone"*) is survivable.

**This collision is larger than several of my named keys and I do not own it.** `quality_event`,
`work_order` and `trading_occasion` are 2-signature keys assigned to no adjudicator in this pass.
Flagged in §7 as needing an owner.

**(b) `design_item` (1, `engineering`) vs `asset` (8).** `engineering.commissioning-handover`
already drew the line and it holds: *"the anchor's proposed `design_item` names the designed
configuration (Chiller model CH-2000) and one design item yields many separately commissioned
instances."* Type vs instance. **Genuinely two keys. Keep both.** `design_item` is a MINT with 1
signature; recommend it be adopted with `asset`, since `engineering`'s whole dimension order depends
on it and adopting `asset` alone leaves the type level unnamed.

**(c) `production_line` (1, `manufacturing.production-planning`) → widen `asset`.** The row asks for
this itself: *"R1c should widen `asset` with a resource role or admit this exact key; no
machine-specific synonym is minted."* A line is an enduring identified operating unit; that is
`asset`'s role. **REFUSE as a separate key.**

**(d) `vehicle` (1, `finance.vehicle-records`) → `asset`.** `logistics` already refused to mint
`vehicle` on the grounds that *"a vehicle is a value of `asset`."* Two rows, one concept, and one of
them already declined the mint. **REFUSE `vehicle`; `finance.vehicle-records` references `asset`.**
Note this is a cross-schema extension of a mint — worth flagging to the product owner as the first
test of whether `asset` is genuinely global.

**(e) `energy_system` (1) and `emission_point` (1), both `manufacturing.environmental-compliance` /
`.energy-audit`.** Both argue against `asset` and both arguments are correct — an energy system
*"spans many assets and distribution"*; an emission point *"has no maintenance history and no asset
tag."* But both are still *"an enduring identified operating boundary that records accumulate
against"*. **Recommend: values of `asset` with the role widened, not two more keys.** Lower
confidence; if the product owner disagrees, they are 1-signature mints on one schema and can wait.

**(f) `part` (1, `manufacturing.spare-parts`) vs `product`.** The row's distinction is real —
*"a spare is consumed, not produced"* — but it is a **role** distinction on the same entity type,
which is the licence for a role split, not for a second unrelated key. Recommend: adjudicate as a
`role_split` pair with `product` (the §3.8 mechanism), or accept it as a `product` value. Not a
blocking decision.

**(g) `lifecycle_stage` (1) → `stage`; `engineering_artifact_type` (1) → `artifact_type`.** §3.

**(h) `learning_programme` (1, `hr.training-development`) and `programme` (1,
`government.grant-programme-administration`) and `target_program` (1,
`applications.graduate-professional`).** Three spellings of "the named programme". Two are almost
certainly `project` under this document's widened role; `target_program` is application-side and
belongs with `target_university`. **Flagged as a collision; belongs to the entity adjudicator.**

### 4.3 The identifier collision — 8 keys, and the corpus's own answer is mostly "no key"

`drawing_number` (`engineering.drawing-package`, DE=false), `manuscript_id`
(`research.manuscript-publication`, DE=false), `protocol_id` (`research.ethics-compliance`,
DE=false), `dataset_name` (`research.dataset-analysis`, DE=false), `entity_registration_number`
(`law_practice.corporate-secretarial`, DE=false), `standard_designation`
(`engineering.standards-library`), `title_reference` (`law_practice.conveyancing`),
`invention_family` (`engineering.invention-disclosure`), plus `law_practice.ip-prosecution`'s right
identifier (§1.1).

**These are not one key and must not be merged.** They split cleanly:
- **Join handles that are not folder levels** — `manuscript_id`, `protocol_id`, `dataset_name`,
  `drawing_number`, `entity_registration_number`. Five rows, five schemas, all proposing
  `destination_eligible: false`, all making the same structural argument that `version_family`
  cannot hold them. `research.ethics-compliance`: *"consent form v1 and v4 are different families
  under one protocol."* **Recommend: one mint is defensible here — a generic `reference_id` — but I
  do not recommend it in this pass.** Five DE-false keys buy zero folder quality and add five
  entries to the organization language; the design's own preference for such cases is
  `law_practice.ip-prosecution`'s option (a), *"the identifier stays a literal observation."*
  **Default to no key for all five; revisit only if P9 proves the grouping fails without one.**
- **Genuinely different things that happen to be identified by a token** — `title_reference` (a land
  parcel), `invention_family` (an invention), `standard_designation` (a published standard). Each is
  a distinct entity in its own world, each has exactly one signature, none collides with another.
  **Leave them local; adopt only if their schema is otherwise unbuildable.**

### 4.4 Genuinely local to one row — leave them (29 keys)

`addressee` (`law_practice.opinions-advice` — and the row itself prefers the decline:
*"this row is fully functional under that outcome and recommends it if there is any doubt"*),
`aid_year`, `approval_instrument`, `authorisation`, `batch_lot`, `carrier`, `channel`, `chapter`,
`colourway`, `conformity_scheme`, `credential_expiry`, `duration`, `employer`, `export_source`,
`host_school`, `issuing_body`, `job_grade`, `legal_entity`, `material_role`, `our_firm` (canonical
but undeclared — see §4.1), `people`
(`creative.journalism-reporting` — **not a proposal at all**: *"this entry exists only to record a
PROHIBITION against it"*), `revision_or_baseline`, `role`, `study_type`, `transcript_status`,
`verification_method`, `verification_status`, `workforce_unit`. Plus `planning_period`
(`manufacturing.production-planning`), which is not this cluster's — it goes to the period
adjudicator with `fiscal_period`, `reporting_period`, `record_period` and `aid_year`.

Three of these deserve a line each because they are prohibitions or warnings rather than requests
and should survive into whatever the product owner ratifies:
- `creative.journalism-reporting`'s `people` prohibition: *"a folder named for a confidential source
  publishes that source to anyone who opens the disk, to a backup, and to any future dossier that
  carries paths."*
- `law_practice.hearing-transcripts`'s `transcript_status`: *"THE TEMPTING EXISTING KEY IS
  `version_family`, AND IT IS ACTIVELY WRONG HERE … A rough transcript, an uncertified transcript, a
  certified transcript and a corrected transcript OF THE SAME SITTING DAY … Every generic version
  heuristic in the product will read them as one version family and prefer the newest."* This is a
  P9 constraint wearing a field's clothes and should be routed there, not adopted as a key.
- `career.employment-records`'s `role`: *"'role' as a field key sits uncomfortably beside the
  `role_split` EDGE name in CONNECTION §5; a different spelling may be preferable."*

**One two-row signal inside this bucket worth surfacing.** `engineering`'s `revision_or_baseline`
and `law_practice.hearing-transcripts`'s `transcript_status` are unrelated keys making the *same*
complaint about a universal field: `version_family` says a file is a member of a family and
deliberately does not say *which* member, and both rows need the latter.
`engineering`: *"A revision token is not necessarily a version-family identifier and a baseline can
include many artifacts at different revisions."* Two independent schemas hitting one universal
field's limit is a signal about `version_family`, not a case for two domain keys. **Route to
whoever owns the universal fields; adopt neither here.**

---

## 5. Recommended keys — `destination_eligible` and `reliability_ceiling`

Ceilings use §3.13's states only (`_CONTRACT.md` rule 4). A `validated` claim asserts a rule family
will confirm the value; R2/R4/R6 own the patterns and none is written here.

| Key | Verdict | `destination_eligible` | `reliability_ceiling` | Note |
|---|---|---|---|---|
| `record_type` | EXTENSION | `true` (canonical unchanged) | `possible` | role widened to records of transactions/operations |
| `work_type` | EXTENSION | `true` (canonical unchanged) | `validated` (live value) | `law_practice` references it |
| `artifact_type` | EXTENSION | `true` (canonical unchanged) | `validated` (live value) | `creative`, `engineering` reference it |
| `stage` | EXTENSION | `true` (canonical unchanged) | `possible` | role widened past research |
| `project` | EXTENSION | `true` canonical; `law_practice` **narrows** to user-approval-gated | `possible` | `creative` sets the ceiling: no gazetteer can hold invented project names |
| `asset` | MINT | `true`, restricted to single-asset files | `validated` | labelled asset-tag slot + register/list corroboration |
| `product` | MINT | `true` canonical; `retail_hospitality` **narrows** to `false` | `validated` | absorbs `output_stream` |
| `people_cycle` | MINT | `true` | `possible` | conditional on joint read with the period cluster |
| `subject_of_record` | MINT | **`false`**, seeded on the key + one NEEDS-JOSEPH widening for `academic` / `college_applications` | `possible` | absorbs `student` |
| `design_item` | MINT (1 sig) | `true` | `validated` | type-level counterpart of `asset` |
| `account_holder` | MINT (1 sig) | `false` | `direct` | `role_split_with: institution`; §2.7 — **not** `subject_of_record` |
| `instruction` | **REFUSE** | — | — | → `project` |
| `output_stream` | **REFUSE** | — | — | → `product` |
| `student` | **REFUSE as a key; ADOPT as an alias** | — | — | → `subject_of_record` |
| `engineering_artifact_type` | **REFUSE** | — | — | → `artifact_type` |
| `lifecycle_stage` | **REFUSE** | — | — | → `stage` |
| `production_line`, `vehicle` | **REFUSE** | — | — | → `asset` |

**Net vocabulary change: 6 mints (`asset`, `product`, `people_cycle`, `subject_of_record`,
`design_item`, `account_holder`), 5 extensions (`record_type`, `work_type`, `artifact_type`,
`stage`, `project`), and 7 refusals of keys that were already written down** (`instruction`,
`output_stream`, `student`, `engineering_artifact_type`, `lifecycle_stage`, `production_line`,
`vehicle`). The refusals are the point: every one was named as a synonym by the row that proposed
it or by a sibling.

---

## 6. Unlock arithmetic, re-derived

### 6.1 The lead's figure, verified

Adopting the 16 keys with ≥3 proposers gives a first declared field to 12 of the 17 fieldless
schemas, unlocking **192** templates: 54 → **246 of 291**. Confirmed exactly. Breakdown:
`business_operations` 22, `clinical_practice` 6, `construction_property` 22, `creative` 32,
`engineering` 19, `hr` 11, `law_practice` 28, `logistics` 7, `manufacturing` 19, `nonprofit` 4,
`resource_operations` 8, `retail_hospitality` 14.

Still locked at 246: `career` (6), `government` (29), `identity` (3), `legal` (4), `medical` (3) —
45 templates whose schemas propose nothing with ≥3 signatures.

### 6.2 This cluster's share

**By key presence: my nine keys reach 170 of those 192 rows** (11 of the 12 schemas; only
`business_operations`, which needs `organization`/`fiscal_period`, is outside my cluster).

**By expressible dimension order — the honest number: 146.** A `dimension_order` needs a
**destination-eligible** declared field, and two of my cluster's adoptions are proposed
destination-ineligible by their own rows:

| Schema | Rows | Unlocked by this cluster? |
|---|---|---|
| `creative` | 32 | ✅ via `project`, `artifact_type`, `stage` |
| `law_practice` | 28 | ✅ via `work_type` (the only *unconditionally* eligible one) and `project` (eligible on explicit user approval, per §1.3); its `record_type` and `subject_of_record` are DE-false |
| `construction_property` | 22 | ✅ via `project` |
| `engineering` | 19 | ✅ via `asset` |
| `manufacturing` | 19 | ✅ via `asset`, `product`, `record_type` |
| `hr` | 11 | ✅ via `people_cycle` |
| `resource_operations` | 8 | ✅ via `asset`, `record_type` |
| `logistics` | 7 | ✅ via `asset`, `record_type` |
| `retail_hospitality` | 14 | ❌ its `product` is destination-hostile; needs `site` (entity cluster) |
| `clinical_practice` | 6 | ❌ `subject_of_record` is DE-false; needs a destination-eligible field it does not yet propose |
| `nonprofit` | 4 | ❌ same; needs `organization` / `fiscal_period` |
| **Total** | **146** | 54 → **200 of 291** on this cluster alone |

### 6.3 The minimum sufficient set — three decisions carry all 146

Computed by exhaustive subset search over the recommended set: the smallest number of adoptions
that reaches the full 146.

> **`project` + `asset` + `people_cycle` = 146 of 146.**

| Key | Verdict | Schemas it is the sole route into | Rows |
|---|---|---|---|
| `project` | EXTENSION | `construction_property`, `creative`, `law_practice` | 82 |
| `asset` | MINT | `engineering`, `logistics`, `manufacturing`, `resource_operations` | 53 |
| `people_cycle` | MINT | `hr` | 11 |

The other six recommended adoptions (`record_type`, `product`, `work_type`, `artifact_type`,
`stage`, `design_item`) add **zero** further unlock — every schema they reach is already reached by
one of the three. They should be judged on folder *quality* and on preventing synonym mints, not on
unlock count.

**Strictly exclusive marginal** — the schemas that lose their last eligible field if one key is
dropped from the full recommended set: `project` → `construction_property` (22); `people_cycle` →
`hr` (11); everything else → 0. `asset` shows 0 exclusive only because `design_item` covers
`engineering` and `record_type` covers the other three; drop `asset` *and* those, and 53 rows go.

**If the product owner adopts only keys with ≥3 signatures** — i.e. no extensions, no `design_item` —
the picture changes and the extensions are missed: `project` alone would then carry 54,
`work_type` 28, `asset` 19, `people_cycle` 11. That is the case for approving the four cheap
extensions in §4.1 alongside the mints.

### 6.4 `student` unlocks nothing, and that is not an argument against it

`academic` and `college_applications` both already declare fields, and all three `student` rows
already carry a working `dimension_order`. Adopting the household widening changes **0** rows from
locked to bindable. What it changes is the **correctness of the default tree on 3 rows** — the
multi-child household that currently has no way to separate two children's report cards or two
children's admission packets. `academic.k12-schooling` states it plainly: *"The order this situation
actually wants is child → school year → work type, and no declared field names the child."* This is
a quality claim, and it should be judged as one rather than compared against unlock counts it will
always lose.

---

## 7. What this pass did NOT decide — hand-offs

1. **The bounded-occurrence key (§4.2a).** 7 spellings, 10 instances, 6 schemas, no assigned
   adjudicator. Three rows explicitly asked for one roster-wide answer. **Needs an owner before
   ratification**, or `quality_event`, `work_order`, `personnel_case`, `consignment` and
   `trading_occasion` ship as five names for one thing.
2. **`people_cycle` vs the period cluster.** Must be read with `fiscal_period` (12),
   `reporting_period` (6), `record_period` (3), `planning_period` (1), `aid_year` (1) so the roster
   does not finish with six bounded-period keys. Period adjudicator's call.
3. **`organization` / `site` / `property` / `client` / `our_firm` / `employer` / `legal_entity` /
   `institution`.** Entity adjudicator's cluster. Two of my conclusions depend on theirs:
   `retail_hospitality` (14 rows) and `nonprofit` (4 rows) are unlockable only from that side.
4. **`manufacturing.calibration-record` NJ-CAL-1** — one `asset` key for both the producing machine
   and the measuring instrument? Left open, as the row left it.
5. **The `subject_of_record` widening** is a NEEDS-JOSEPH question by construction. The three
   `student` rows deferred it to the product owner in their own text, and this document does the
   same rather than pre-empting it.
6. **Refusal review.** 44 rows are refused and were excluded from all arithmetic here. If any is
   reinstated the unlock counts move; none of the key decisions do.
7. **None of this is wired into `src/` yet, which is why it is still cheap to change.**
   `src/facts/domains.py:51-53` closes `SCHEMA_IDS` at ten ids — the six field-bearing schemas plus
   `career`, `identity`, `medical`, `legal`. The roster declares 23, and the 13 professional worlds
   that carry every key in this document (`manufacturing`, `resource_operations`, `law_practice`,
   `engineering`, `creative`, `hr`, `logistics`, `construction_property`, `retail_hospitality`,
   `clinical_practice`, `nonprofit`, `business_operations`, `government`) have no counterpart there.
   Commit `b2dbb08` recorded that gap. Every recommendation in this document is a change to
   `canonical_fields.json` and to schema `fields[]` blocks only; none of it can be adopted in `src/`
   until that vocabulary question is settled, and settling it is not this pass's.
