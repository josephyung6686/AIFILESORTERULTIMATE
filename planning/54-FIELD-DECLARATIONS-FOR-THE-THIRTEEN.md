# 54 — Field declarations for the thirteen (J-WIDE-1), and what this session did

Date: 2026-08-27 · Session: `graph-agent-89` (catalogue) · For: `graph-agent-ee` (build) and Joseph
Status: **PROPOSAL. Nothing adopted. No `src/`, no `planning/domains/**.json`, no `canonical_fields.json`
was edited to produce it.** Every agent in this pass was read-only and verified as such.

Governing: `00-database-agent-product-design.md` wins on conflict → `domains/CONNECTION.md` →
`domains/_CONTRACT.md` → the adjudications `47`/`48`/`49` → this document.

---

## 0. What this session did, in order

1. **Audited the closed 358-row catalogue** — seven read-only lanes plus mechanical passes. Findings
   in `27-dispatch-run-log.md`. Headline: zero fabricated quotations across 2,335 checked spans, zero
   silent coverage loss (574/574 legacy ids cited, 533/533 folds resolve), PR-6 held perfectly.
2. **Corrected six documents** — `41` (was unsafe to answer: it told Joseph "there is no fourth" and
   "cut Recipe 2", both refuted by `42`), `01c` (R1c could not repair 364 of the findings it exists
   to close), `_CONTRACT` rule 12 (the contract was stale, not the corpus), `42-HANDOFF` (closed),
   `31` (superseded), and `finance.account_holder` (the only non-canonical key in `fields[]`
   corpus-wide; moved to `proposed_fields`, so `fields[] ⊆ canonical_fields.json` now holds at 0
   violations).
3. **Took four rulings from Joseph** (`DECISION-BRIEF.md`, J-WIDE) — widen to all 23 schemas;
   career ships both orders with no default; a repository root is atomic; the courier seam is group
   membership. Then two more: portfolio lives in both; `employer-side-hiring` left open.
4. **Dispatched the field research** — 1 structure map + 13 field agents + 1 merge + 1 adversarial.
5. **Caught the vocabulary collision before it happened.** The dispatch was stopped after the map
   agent and before the 13 fired, because its data — computed from raw `proposed_fields` vote counts
   — named `fiscal_period` (12 votes) and treated `organization` as one key. Both are exactly what
   `47`/`48` overrule. The adjudications were injected and the run resumed. **§3 shows it worked.**
6. **Researched `career` separately**, because it was invisible to the J-WIDE-1 list (that list was
   "schemas the code does not recognise", and career is already inside `SCHEMA_IDS`) yet declares
   zero fields and proposes zero.

## 1. The two things the build session needs first

**(a) These fields are INERT without the code change.** `src/facts/domains.py`:52 `SCHEMA_IDS` is a
closed tuple of ten. Declaring fields on the thirteen changes nothing until it widens — no fact will
activate them and no folder will be built. That change is `graph-agent-ee`'s and is deliberately
sequenced AFTER this document, because `FIELD_LESS_SCHEMA_IDS` is derived from `SCHEMA_IDS` and
widening alone would make it mean two incompatible things at once ("field-less by privacy design"
and "field-less pending research").

**(b) `medical`, `identity` and `legal` stay field-less and are NOT in the thirteen.** Their silence
is `00` working as written — detect and protect, not file. Note `clinical_practice` IS in the
thirteen and `medical` is out: the practitioner's business records versus the patient's protected
data. That cut is not obvious from the schema names and someone reading the roster cold would
plausibly merge them.

## 2. The thirteen field sets, as proposed

Each agent worked blind to the other twelve. `MINT` = a new canonical key is required; `CANON` =
the key already exists in `canonical_fields.json`. `DEST` = may become a folder level.

### `creative` — 32 kept rows · confidence **high** · 5 fields

- **`project`** — CANON, DEST
- **`artifact_type`** — CANON, DEST
- **`stage`** — CANON, DEST
- **`client`** — CANON, DEST
- **`venue`** — CANON, DEST

  Recommended order: `client > project > stage > artifact_type`

  ⚠ Open: Four things only Joseph can settle. (1) THE STRONGEST CASE FOR FEWER, stated as charged. Creative was field-less BY DECISION, not by omission — J-IND answered NJ-R1a-1 with option (a), and the anchor's one_line calls it a 'Gist-free placeholder schema'. Three of my five keys (project, stage, artifac

### `law_practice` — 28 kept rows · confidence **high** · 6 fields

- **`project`** — CANON, DEST
- **`work_type`** — CANON, DEST
- **`client`** — CANON, DEST
- **`our_firm`** — CANON, fact-only
- **`subject_of_record`** — MINT, fact-only
- **`record_period`** — MINT, DEST

  Recommended order: `client > project > work_type > record_period`

  ⚠ Open: THE ONE THING ONLY JOSEPH CAN SETTLE, and four of my six fields depend on it: can `canonical_fields.json` express a PER-SCHEMA destination-eligibility narrowing, or must the gate live in the template contract? Canonical `client` and `project` are both destination_eligible true globally, and law_prac

### `government` — 29 kept rows · confidence **medium** · 5 fields

- **`project`** — CANON, DEST
- **`record_type`** — CANON, DEST
- **`record_period`** — MINT, DEST
- **`property`** — MINT, DEST
- **`subject_of_record`** — MINT, fact-only

  Recommended order: `property > project > record_period > record_type`

  ⚠ Open: Three things only Joseph can settle. (1) `property` is the weakest of the five and the one to cut if the honest budget is four: it serves 9 of 29 rows, one row (government.international-development) bans it outright as a folder level, and one (government.housing-authority) requires it be displayed a

### `business_operations` — 22 kept rows · confidence **medium** · 6 fields

- **`organization`** — MINT, fact-only
- **`record_period`** — MINT, DEST
- **`project`** — CANON, DEST
- **`client`** — CANON, DEST
- **`supplier`** — MINT, DEST
- **`record_type`** — CANON, DEST

  Recommended order: `project > client > supplier > record_period > record_type`

  ⚠ Open: FOUR, in descending order of what only Joseph can settle.

(1) SIX IS THE CAP AND I AM AT IT — is the counterparty pair worth the two slots? The honest case for FOUR fields (organization, record_period, project, record_type) is real and I want it on the record: neither `client` nor `supplier` appear

### `construction_property` — 22 kept rows · confidence **high** · 5 fields

- **`property`** — MINT, DEST
- **`project`** — CANON, DEST
- **`work_type`** — CANON, DEST
- **`client`** — CANON, DEST
- **`our_firm`** — CANON, fact-only

  Recommended order: `property > project > work_type`

  ⚠ Open: THREE, and the first is the one I would put to Joseph as a live sixth-slot decision.

(1) `record_period` — DOES THIS SCHEMA GET A PERIOD FIELD AS ITS SIXTH? I did not take it, and the call is close enough that it should be Joseph's rather than mine. FOR: five rows name a period level — block-manage

### `engineering` — 19 kept rows · confidence **high** · 5 fields

- **`design_item`** — MINT, DEST
- **`artifact_type`** — CANON, DEST
- **`asset`** — MINT, DEST
- **`project`** — CANON, DEST
- **`stage`** — CANON, DEST

  Recommended order: `project > design_item > artifact_type`

  ⚠ Open: Five things only Joseph can settle. (1) NJ-ENG-1 is answered here in the REUSE direction - canonical `stage` and `artifact_type` widened rather than lifecycle_stage/engineering_artifact_type minted - which matches 49 section 5 but contradicts the literal spelling used in all 19 engineering rows; if 

### `manufacturing` — 19 kept rows · confidence **medium** · 6 fields

- **`site`** — MINT, DEST
- **`product`** — MINT, DEST
- **`asset`** — MINT, DEST
- **`event`** — CANON, DEST
- **`record_period`** — MINT, DEST
- **`record_type`** — CANON, DEST

  Recommended order: `site > product > asset > event > record_period > record_type`

  ⚠ Open: FOUR things only Joseph can settle, in descending cost.

(1) THE `event` FOLD IS THE WHOLE PROPOSAL'S HINGE AND NO ONE OWNS IT. 49 §4.2(a) says so in its own words: 'This collision is larger than several of my named keys and I do not own it. `quality_event`, `work_order` and `trading_occasion` are 2

### `retail_hospitality` — 14 kept rows · confidence **medium** · 5 fields

- **`site`** — MINT, DEST
- **`event`** — CANON, DEST
- **`record_type`** — CANON, DEST
- **`record_period`** — MINT, DEST
- **`product`** — MINT, fact-only

  Recommended order: `site > event > record_period > record_type`

  ⚠ Open: FOUR, ranked, and the first is the only one that changes the field count. (1) IS A NON-PHYSICAL CHANNEL A `site` VALUE, OR A SIXTH KEY? 48:450 and 48:549 already flag this as unresolved and say "`retail_hospitality.ecommerce-ops` depends on the answer" — and so does guest-feedback, which is the one 

### `hr` — 11 kept rows · confidence **high** · 5 fields

- **`people_cycle`** — MINT, DEST
- **`work_type`** — CANON, DEST
- **`subject_of_record`** — MINT, fact-only
- **`workforce_unit`** — MINT, fact-only
- **`event`** — CANON, fact-only

  Recommended order: `people_cycle > work_type`

  ⚠ Open: Three eligibility toggles only Joseph can settle; none of them changes whether the five fields exist. (1) WORKFORCE_UNIT DESTINATION ELIGIBILITY. I seed it FALSE, following 48's table ("Search/privacy/join only") and four rows that refuse a visible unit level — hr.dei-program ("publishes the composi

### `resource_operations` — 8 kept rows · confidence **high** · 6 fields

- **`site`** — MINT, DEST
- **`asset`** — MINT, DEST
- **`authorisation`** — MINT, fact-only
- **`product`** — MINT, DEST
- **`record_period`** — MINT, DEST
- **`record_type`** — CANON, DEST

  Recommended order: `site > asset > product > record_period > record_type`

  ⚠ Open: Three, for Joseph only. (1) NJ-RESOURCE-2 / NJ-FOREST-2, and I have taken a position 48 §7 does not: should `authorisation` be destination-eligible by default? 48 §7 says true; I seed FALSE-and-unlockable because every attested value is an instrument identifier ('OCS-G 12345'), 4 of my 8 rows refuse

### `logistics` — 7 kept rows · confidence **medium** · 6 fields

- **`record_type`** — CANON, DEST
- **`consignment`** — MINT, DEST
- **`site`** — MINT, DEST
- **`asset`** — MINT, DEST
- **`record_period`** — MINT, DEST
- **`carrier`** — MINT, fact-only

  Recommended order: `site > consignment > asset > record_type > record_period`

  ⚠ Open: (1) NJ-DC-1, the family's sharpest and the one only Joseph can settle: `logistics.driver-compliance` is entirely about ONE NAMED PERSON - licence entitlements, a medical fitness examination, training hours, tachograph infringements - and it deliberately proposes NO subject key, holding the driver do

### `clinical_practice` — 6 kept rows · confidence **medium** · 4 fields

- **`record_type`** — CANON, DEST
- **`record_period`** — MINT, DEST
- **`subject_of_record`** — MINT, fact-only
- **`authored_by`** — CANON, fact-only

  Recommended order: `record_type > record_period`

  ⚠ Open: THREE, and the first gates the whole slate — none are mine to settle.

(1) MAY `subject_of_record` BE STORED AT ALL FOR THIS SCHEMA? The anchor's own open_question (2) asks it: "Whether `subject_of_record` may exist as a stored field key at all... it is the sharper version of it, because here the su

### `nonprofit` — 4 kept rows · confidence **medium** · 5 fields

- **`organization`** — MINT, fact-only
- **`project`** — CANON, DEST
- **`record_period`** — MINT, DEST
- **`record_type`** — CANON, DEST
- **`subject_of_record`** — MINT, fact-only

  Recommended order: `project > record_period > record_type`

  ⚠ Open: Four, in descending cost. (1) SHOULD THIS BE FOUR FIELDS, NOT FIVE? The honest case against project: it binds cleanly on only two of four kept rows, one of which (nonprofit.trade-union) declares itself 'PLACEHOLDER ROW (J-IND)' in its own one_line, and its two bindings - a named mail appeal and an o


## 3. Cross-schema key census — the convergence result

**24 distinct keys across all thirteen schemas.** Not thirteen private vocabularies.

| key | schemas | which |
|---|---|---|
| `record_period` | 9 | law_practice, business_operations, government, retail_hospitality, resource_operations, clinical_practice, manufacturing, logistics, nonprofit |
| `record_type` | 8 | business_operations, government, retail_hospitality, resource_operations, clinical_practice, manufacturing, logistics, nonprofit |
| `project` | 7 | creative, law_practice, business_operations, engineering, government, construction_property, nonprofit |
| `subject_of_record` | 5 | law_practice, government, hr, clinical_practice, nonprofit |
| `client` | 4 | creative, law_practice, business_operations, construction_property |
| `asset` | 4 | engineering, resource_operations, manufacturing, logistics |
| `site` | 4 | retail_hospitality, resource_operations, manufacturing, logistics |
| `work_type` | 3 | law_practice, construction_property, hr |
| `event` | 3 | retail_hospitality, hr, manufacturing |
| `product` | 3 | retail_hospitality, resource_operations, manufacturing |
| `artifact_type` | 2 | creative, engineering |
| `stage` | 2 | creative, engineering |
| `our_firm` | 2 | law_practice, construction_property |
| `organization` | 2 | business_operations, nonprofit |
| `property` | 2 | government, construction_property |

Single-schema keys (9): `authored_by`, `authorisation`, `carrier`, `consignment`, `design_item`, `people_cycle`, `supplier`, `venue`, `workforce_unit`
**The adjudications held.** `record_period` was adopted by **9 of 13** — and `fiscal_period`,
`reporting_period`, `instruction` and `output_stream` appear **zero times** across all thirteen.
`record_type` 8×, `subject_of_record` 5×, both as `47`/`49` ruled. Had the original dispatch run,
these would have been thirteen private vocabularies; the injection is why they are not.

**Every schema landed inside `00`:48's 3–6 cap on its own** — 4 to 6 fields each, no padding.

## 4. `career` — researched separately (J-WIDE-2)

5 fields, inside the cap: **`target_employer`**, **`employer`**, **`job_title`**,
**`recruiting_cycle`** (all mints) and **`record_type`** (live key, role extension — career becomes
its 4th domain after manufacturing/logistics/resource_operations, so no new precedent).

Independently verified: `canonical_fields.json` contains **zero** occurrences of `employer`, `job`,
`recruit` or `position` — not even as an alias. Career is unserved down to the alias level, so the
mints are unavoidable; the discipline was keeping them to four.

**New role split: `employer` ↔ `target_employer`**, and the corpus already wrote the discriminator —
candidacy language with a still-open process, versus an executed signature block with a labelled
effective-date slot. It also corrects `career.employer-side-hiring`, which had authored
`authored_by ↔ target_school` — a *school* key standing in for a candidate, which that row itself
called "the place where this template's vocabulary is visibly short by one key."

**Product finding:** company-first fragments. On a constructed 15-application hunt (~51 files), about
**8 of 15 companies land at one or two files**, and with a role level each becomes a one-child chain —
`Career/Ramp/Backend Engineer/Cover Letter/ramp-cover.pdf`, four levels for one file. `00`:99 tells
the interface to warn on one-child levels, on many tiny folders, and to recommend flattening. **It
trips all three at once.** Recorded with the estimate flagged as constructed, not measured.

## 5. Still running at the time of writing

- **The merge pass** — resolving the fifteen multi-schema keys in §3 into one vocabulary. It hit a
  truncation bug in this session's dispatch script (the proposals block was capped at 60,000 chars;
  the real payload is 290KB, so it received 3 of 13) and was re-fed the complete set from the run
  journal. **That was this session's defect, not the agent's.**
- **The adversarial pass** — attacking the merged result for cap violations, minted synonyms,
  facts-as-paths, jargon folder names, tiny-folder risk, and schemas being given a field set to be
  consistent with siblings rather than because their rows support one.

Both land after this document. Treat §2 and §3 as the proposal and the merge as the arbiter where
they disagree.

## 6. Open questions carried to Joseph — do NOT close these in code

1. **`recruiting_cycle` vs `people_cycle`** — the charge that one is the other respelled was **not
   defeated**. `49` §1.6 attached a hard condition that `people_cycle` be adjudicated in one sitting
   with the period cluster so the roster does not end with six bounded-period keys. `recruiting_cycle`
   belongs in that sitting.
2. **Per-schema destination-eligibility.** `law_practice` raises it and four of its six fields depend
   on it: canonical `client` and `project` are `destination_eligible: true` *globally*, but
   law_practice needs them narrowed. Can `canonical_fields.json` express a per-schema narrowing, or
   must that gate live in the template contract? **This is the single most load-bearing open question
   in the pass.**
3. **`career.employer-side-hiring`** (J-WIDE-6) — Joseph asked "could it be both?". The mechanism
   exists (one owning schema + an `also_holds_with` edge) but does not settle the privacy question
   that prompted it. Recommended: own in `hr`, co-hold from `career`.
4. **`job_title` vs `role`** — a spelling departure from `00`'s prose word, with D6 precedent
   (`subject`, not `course`).
5. **`creative` was field-less BY DECISION** (J-IND answered NJ-R1a-1 with option (a)), and its agent
   flagged that three of its five keys already exist. J-WIDE-1 overrules that decision — but the
   agent's own charge against itself is worth reading before adopting.
6. **`government.property`** serves 9 of 29 rows, one row bans it as a folder level outright, and
   another requires it displayed differently. It is the field to cut if the honest budget is four.

## 7. What `graph-agent-ee` should do with this

- Build `TemplateDefinition` records against §2/§4, **treating the merge pass as the arbiter** on the
  fifteen shared keys.
- **Career is two definitions, not one with two orders** — recorded as J-WIDE-2-R mechanics in
  `DECISION-BRIEF.md`, because `templates.py`:353-360 requires candidate orders to cover the same
  roles and career's two have disjoint role sets.
- **The `warnings_for` blocker stands.** `health.py`:156 has zero production callers (verified: 2
  references in `src/`, both inside `health.py` itself; 14 in its test file). Until it is wired,
  "both orders, no default" ships an unguided question.
- Widen `SCHEMA_IDS` in one coherent pass once the merge lands, per your own sequencing.

---

# THE MERGE RESULT — landed 2026-08-27 23:30

Read-only throughout. **Net: 37 canonical keys → 52.** Fifteen additions, three refusals, seven
role-sentence rewrites. All fourteen schemas (13 + career) land inside `00`:48's 3–6 cap.

## 8. Two corrections to THIS SESSION'S OWN BRIEF — both verified, both mine

**(a) I mis-cited `00`:52 at all fourteen agents.** I passed them *"prematurely hand-authoring
hundreds of specialized schemas"* as a governor on **field** count. Grep-verified: **that sentence's
object is SCHEMAS** — `00`:52 opens *"Each domain consists of two related definitions: a fact schema
… and a folder template"*. And `00`:48 says the **opposite** about fields, verbatim: *"Across the
whole product, there may eventually be many specialized fields because different domains genuinely
require different information."* The governor on fields is `00`:48's per-domain cap plus reuse
discipline — not a global ceiling. Fifteen additions across thirteen previously field-less schemas is
not premature by `00`'s own text; fifteen near-synonyms would be, which is what the three refusals
prevent.

**(b) I passed a stricter cap than `00` states.** I wrote "3 to 6 fact fields" as a hard total.
`00`:48 verbatim: *"usually three to six that may help build a future folder proposal **and several
additional fields used only for search, privacy protection, explanation, or later review**."* The
3–6 caps **destination-candidate** fields; `dest=false` fields are *additional*. The merge enforced
my stricter reading anyway and reported both counts — the conservative choice — but **Joseph should
pick deliberately**, because it is the difference between `law_practice` sitting at its ceiling and
sitting comfortably.

## 9. The additions (15)

`record_period` · `subject_of_record` · `site` · `asset` · `product` · `property` · `organization` ·
`supplier` · `people_cycle` · `design_item` · `authorisation` · `workforce_unit` (**only if narrowed**)
· `employer` · `target_employer` · `job_title`

**Reused instead of minted (10):** `project` (now 9 schemas — the single highest-value line in the
merge), `record_type` (10), `work_type` (4), `artifact_type` (4), `stage` (3), `client` (4),
`our_firm` (2), `event` (4), `venue` (2), `authored_by` (2).

**Refused (3):** `consignment` → `event` · `carrier` → `supplier` · `recruiting_cycle` → `people_cycle`.
Plus `issuing_body` **held**, not added — adding it now creates a second unreferenced orphan beside
`target_school`.

**The four unassigned clusters all resolve to ONE key each:** `event`, `site`, `asset`, `supplier`.

## 10. THE DECISION THAT BLOCKS A CLEAN LANDING — put this to Joseph first

**`canonical_fields.json` cannot express a per-schema `destination_eligible`, and five of the fifteen
additions now need it.** Not an edge case — demanded independently by `client` (law_practice: eligible
only on approval; family-law: ineligible outright), `subject_of_record`, `product` (retail narrows to
false), `property` (one government row requires an aliased label, another bans it as a level outright)
and `job_title` (career: eligible but flatten by default). **Five keys across seven schemas.**

Either `canonical_fields.json` grows a per-schema override, or every one of these narrowings moves
into the template contract and the catalogue records only the loosest value. **This blocks five of
the fifteen.**

## 11. Other rulings worth Joseph's eye

- **`event` widened** to *"the bounded occurrence a set of records is about"* — absorbing 5 spellings
  across 4 schemas at zero mint cost. 49 §4.2(a) had said outright *"I do not own it"*; the merge
  ruled it. The counter nearly won (`00` names `event` in both the Photos field sentence AND the
  Photos template sentence — the same double-naming that fences `media_type`), and **49 §3 supplies
  no principle distinguishing keys it widens from keys it fences, which is a real defect in it.**
  Decided on one textual fact: `event`'s *live* role already reads "a capture **or record** belongs
  to" — verified.
- **`record_type`'s role sentence: both existing candidates are wrong.** Recommended
  *"what kind of record this is — a record that evidences that something happened or was decided"* —
  admits minutes and finding aids (government's objection was correct) while keeping the discriminator
  that separates it from `work_type` and `artifact_type`. With **10 schemas on this key**, the risk is
  gravitational not mechanical: **49 §3's routing table must be written into the key's `notes` in
  `canonical_fields.json`, not left in an adjudication doc.** A routing rule nobody reads at
  extraction time is not a routing rule.
- **`business_operations.compliance-audit` loads two roles onto one key** and the schema is at its
  6-field ceiling, so it cannot be fixed by addition. Three options offered; **recommended: let it
  fall to a template-local label under 46's W2 classifier** — already built and green, costs one row
  rather than a schema, and keeps a merged-roles key out of the permanent vocabulary.
- **`hr` and `clinical_practice` land at only 2 destination-eligible fields** — below `00`'s "usually
  three". For clinical_practice that is arguably right (it borders the out-of-scope medical schema).
  **For hr it is a real weakness**: if `workforce_unit` is refused, hr's entire folder proposal is
  `people_cycle > work_type`.

## 12. Status of the adversarial pass — stated honestly

The challenge agent **ran but on truncated input** (same 60KB/40KB cap bug that hit the merge; it
received a partial proposals block and the merge output had not yet landed). **Its verdict therefore
covers partial data and should not be read as a clean adversarial check of the merged result.**

Mitigating, and the reason this is not being re-run: the merge itself did adversarial work — it
**refused three proposed keys**, corrected two of this session's own brief instructions, found a
defect in 49 §3, found a self-contradiction in 48 (§2 refuses `carrier`, §7 adopts it), and recorded
eight live disagreements rather than papering over them. A dedicated re-run should still happen
before any of this is written into `canonical_fields.json`.
