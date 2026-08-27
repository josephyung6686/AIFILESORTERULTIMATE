# 57 — Adversarial re-run of the field declarations (the check `54` was owed)

Date: 2026-08-28 · Read-only pass. **No `src/`, no `canonical_fields.json`, no
`planning/domains/**/*.json` was edited to produce this.**
Governing on conflict: `00-database-agent-product-design.md` → `domains/_CONTRACT.md` →
`47`/`48`/`49` → `54` → this document.

`54` §12 recorded that its adversarial agent *"ran but on truncated input"* and that
*"a dedicated re-run should still happen before any of this is written into `canonical_fields.json`."*
This is that re-run. It attacked the merged result on the seven tests in the brief and **found
eleven things wrong**, four of which are blocking.

---

## 0. Numbers re-derived in this document

Recomputed from `planning/domains/nodes/*.json` and `planning/domains/canonical_fields.json`
on 2026-08-28, after every commit in this session.

| Fact | Value |
|---|---|
| Node rows on disk | **358** (335 `template`, 23 `schema`) |
| `refuse_node: true` | **44** → **291** kept templates |
| Canonical keys in `canonical_fields.json` | **37** |
| Schemas declaring live `fields` | **6** — `academic` (5), `code` (4), `college_applications` (5), `finance` (4), `photos` (6), `research` (6) |
| `SCHEMA_IDS` at `src/facts/domains.py`:52 | **10** — confirmed, unchanged |
| Rows carrying `proposed_fields` | 87 · **80 distinct keys · 170 instances** |
| Kept rows in the thirteen | creative 32 · government 29 · law_practice 28 · business_operations 22 · construction_property 22 · engineering 19 · manufacturing 19 · retail_hospitality 14 · hr 11 · resource_operations 8 · logistics 7 · clinical_practice 6 · nonprofit 4 · (career 6) |

**`54`'s kept-row counts are all correct.** So are its 24-key census and its "13 + career" scope.

**One structural fact `54` never states, and it changes how every claim in it must be read.**
**All fourteen schemas carry ZERO non-empty `template.dimension_order`** — every one of the 291
kept rows on these schemas has `dimension_order: []`, because the schemas are field-less by
`PR-6`. Their field demand therefore exists in exactly two places: `proposed_fields` (structured,
countable) and `template.why` / `open_question` prose (unstructured). **`54` reports neither.**
This document supplies the structured count, which is what makes test 7 answerable at all.

---

## 1. The signature table — the evidence `54` does not show

Each proposed key folded to its `47`/`48`/`49` winner, counted per schema over all 291 kept rows
plus the 23 schema rows. **"Assigned"** is `54` §2/§4/§9. **"Signed"** is who actually asked.

| key | schemas `54` assigns it to | schemas that actually proposed it (instances) | **assigned with NO signature** |
|---|---|---|---|
| `record_period` | 9 | business_operations 9 · resource_operations 4 · manufacturing 3 · finance 3 · law_practice 2 · nonprofit 1 · retail_hospitality 1 | **government · clinical_practice · logistics** |
| `record_type` | 10 | resource_operations 4 · manufacturing 3 · logistics 1 · law_practice 1 | **business_operations · government · retail_hospitality · clinical_practice · nonprofit · career** |
| `project` | 9 | construction_property 4 · law_practice 2 · creative 1 · government 1 · hr 1 · nonprofit 1 | **business_operations · engineering** |
| `subject_of_record` | 5 | law_practice 4 · hr 2 · clinical_practice 1 · nonprofit 1 (+academic 2, college_applications 1 as `student`) | **government** |
| `client` | 4 | creative 1 · law_practice 1 | **business_operations · construction_property** |
| `work_type` | 4 | law_practice 1 | **construction_property · hr** |
| `supplier` | 2 (business_operations, logistics-via-carrier) | **manufacturing 1 · retail_hospitality 1** | **business_operations** — and see §5.4 |
| `property` | 2 | construction_property 4 · finance 1 | **government** |
| `our_firm` | 2 | law_practice 1 | **construction_property** |
| `authored_by` | 2 | — | **clinical_practice** |
| `site` · `asset` · `product` · `organization` · `people_cycle` · `design_item` · `authorisation` · `workforce_unit` · `event` · `stage` · `artifact_type` | as assigned | all cleanly signed | — |
| `venue` | creative | 0 in `proposed_fields`, **13 of 32 creative rows in prose** incl. `creative.exhibition`, `.theatre-production`, `.periodical-issue`, `.submission-query` | — (earned, see §2) |
| `employer` · `job_title` | career | `career.employment-records` (`employer`, `role`) | — |
| `target_employer` | career | 0 | — (earned by rule, see §2) |

---

## 2. Verdict per addition (15)

**ACCEPT (9).**

- **`site`** — 10 proposing rows, 4 schemas, all seeding `true`, all eliminating `location`
  identically. `48` §1b is right. No collision with any canonical key or alias.
- **`asset`** — the cleanest proposal in the corpus (`48`: 8 rows, every one after the first says
  *"SECOND — DO NOT MINT"*). Carry `manufacturing.asset-register`'s restriction onto the key: a
  multi-asset register export has no single value and sits at `site`.
- **`product`** — `49` §1.5's fold of `output_stream` is sound; independent-family count is the
  right tiebreak. Sound in one line.
- **`property`** — earned by `construction_property` (4) and `finance.household-property` (1).
  A place, not an author; `00`:44 does not reach it. **But strip `government` from it** — §3.
- **`organization`** — 14 rows, and `48` §3's reading of `00`:44 (*"produced by"* is authorship;
  *"merely"* is a template-time test) is correct and is the only reading that also satisfies
  `00`:70, which puts a company first in a folder template. Seeded `false`, template-time
  promotable, as `48` recommends.
- **`design_item`** — earned, but **NARROW**: see §5.2, it was never checked against `product`.
- **`subject_of_record`** — 9 refused synonyms across 3 families, zero minted; `49` §1.7 is right,
  and `48`'s `destination_eligible: false` **on the key, never per-template** must survive
  verbatim into `canonical_fields.json`.
- **`employer`** and **`target_employer`** — `target_employer` has zero signature but is required
  by `00`:44's own rule (*"An application essay can mention the author's current school and the
  university to which the essay is addressed. Those are not the same field."*) and mirrors the
  live `school` ↔ `target_university` split exactly. **Condition:** the pair's `notes` must state
  the discriminator against `our_firm`, because for an employee the employer *is* "the holder's
  own organization" — the two keys differ only in role and eligibility, and nothing in `48` or
  `54` says so. Without it, extractors will fill both from one letterhead.

**ACCEPT WITH A CHANGED NAME (1).**

- **`authorisation`** → **`authorization`**. `00` uses *"organization"* 27 times and
  *"organisation"* **zero** times; its one use of the stem is *"authorized"*. Shipping
  `organization` (z) and `authorisation` (s) in the same 15 additions puts two orthographies in
  one snake_case namespace — *"two spellings of a field key are two columns"*, which is the exact
  defect D6 exists to kill, arriving through the back door as house style. `48` §6a picked
  `authorisation` over `operating_authority` and `approval_instrument` on the merits and never
  checked the orthography. Secondary: `authoris*` shares a stem with canonical `authored_by`
  (alias `author`); if Joseph wants distance as well as consistency, `operating_permit` is
  available and `manufacturing.environmental-compliance`'s *"never a regulator's name"* survives
  either way.

**NARROW (3).**

- **`record_period`** — the key is right (`47` is the strongest of the three adjudications; 23
  proposing rows, one hole found 23 times). **The narrowing is on scope, not on the key:** strike
  `clinical_practice` and `logistics`, which have **zero** signature in `proposed_fields` *and*
  appear nowhere in `47`'s 23 proposers, `47`'s 13 open-question raisers, or `47`'s "48 rows
  across 9 schemas" prose census. `government` has exactly one row
  (`government.emergency-management`) out of 29. See §3.
  **And a live alias collision `47` did not catch:** canonical `tax_year` already carries the
  alias **`fiscal_year`**, while `47` §3.1 recommends recording **`fiscal_period`** as an alias of
  `record_period`. That ships `fiscal_year → tax_year` and `fiscal_period → record_period` in one
  file, one character apart, for two genuinely different objects — which is the precise confusion
  `business_operations` raised when it minted the key (*"an entity's fiscal year routinely does not
  coincide with [the statutory filing year], and reusing the key would quietly assert that it
  does"*). **`tax_year` must drop the `fiscal_year` alias, or both keys need a disambiguating
  `notes` line.** Also note `aid_year` becoming an alias of `record_period` while `tax_year` and
  `capture_year` stay keys: `*_year` strings now resolve to three different columns.
- **`workforce_unit`** — `54` says "only if narrowed" and is right, but the narrowing it means
  (`destination_eligible: false`) is a **rejection of the proposing row's own seed**: `hr` proposes
  it `true` *"only after a real multi-unit corpus is established"*. `48`'s `false` is the safer
  seed; adopt it, but adopt it the way `organization` was adopted — **seeded false, template-time
  promotable** — not banned. Same shape, same argument, same row family; there is no principled
  reason for `organization` to be promotable and `workforce_unit` not to be. This also removes
  `54` §11's dilemma: `hr` gets a third destination-candidate field the moment the corpus is
  multi-unit, which is the only condition under which the level is not a one-child vanity level.
- **`people_cycle`** — see §5.1. The key is real; its **spelling and its scope are both wrong**.

**REJECT (2 assignments, not 2 keys).**

- **`property` on `government`** — zero signature; `54` itself records that it serves 9 of 29 rows,
  that `government.international-development` bans it as a folder level outright, and that
  `government.housing-authority` requires it displayed differently. Against that, the `government`
  schema row's `open_question` says in its own words: *"**Keep the schema fieldless for this pass.**
  If PR-6 is later lifted, adjudicate a minimal role-safe vocabulary **centrally rather than in
  children**."* Overruling a schema's own refusal on a key it never proposed, on a 9/29 hit rate,
  with two of the nine objecting, is the weakest single line in `54`.
- **`record_type` on `career`** — `00`'s Career sentence names the fourth dimension **"document
  type"**, which is already the *alias* of canonical `application_document_type`; and `49` §3's own
  routing rule sends a tailored resume, a cover letter and a portfolio case study to **`work_type`**
  (*"…**is** the work"*), not to `record_type` (*"…**evidences** that something happened"*). Career's
  corpus is roughly half work-product (`career.recruiting`, `career.portfolio-work-samples`,
  `career.consulting-client-engagement`) and half record (`career.employment-records`,
  `career.credentials-licenses`). A career schema holding **only** `record_type` has no legal home
  for the work-product half, which is exactly the gravity failure §5.3 describes. **Career needs
  `work_type` as well, or instead.**

---

## 3. Test 7 — schemas given a field set to match their siblings

The brief named `nonprofit` (4 rows) and `clinical_practice` (6 rows) as the suspects. **Both are
guilty, and `government` is worse than either.**

**`clinical_practice` — 4 fields, 1 earned.** Its schema row proposes exactly one key,
`subject_of_record`, and asks *"whether `subject_of_record` may exist as a stored field key at
all."* Its 6 kept rows carry **zero** `proposed_fields` between them. `54` gives it four:
`record_type`, `record_period`, `subject_of_record`, `authored_by`.
- `record_period` — zero signature; `clinical_practice` appears **nowhere** in `47`, in any of its
  three demand counts.
- `record_type` — zero signature.
- `authored_by` — zero signature, and *worse than unearned*: the schema's defining sentence is that
  **the holder is the author** (*"here the holder is its author and custodian"*). A field whose
  value is the same on every file the schema activates carries no information and can never
  separate anything. **Cut it.**
The honest `clinical_practice` field set is **one key**, `subject_of_record`, `destination_eligible:
false`, plus the universal facts — which is what a schema bordering the out-of-scope `medical`
safety domain *should* look like. `54` §11 half-concedes this (*"for clinical_practice that is
arguably right"*) and then ships three unearned keys anyway.

**`nonprofit` — 5 fields, 2 earned, and the one hole it named is unfilled.** Its schema row
proposes four keys: `organization`, `fiscal_period` (→ `record_period`), **`sponsor`**, and
`subject_of_record`. `54` ships `organization`, `record_period`, `subject_of_record` — **drops
`sponsor`** and **adds `project` and `record_type`**, neither of which nonprofit proposed.
`54`'s own §2 note concedes `project` *"binds cleanly on only two of four kept rows, one of which
declares itself 'PLACEHOLDER ROW (J-IND)' in its own one_line."*
Meanwhile the row said of `sponsor`: *"Without a funder role the family's strongest node —
restricted money with strings — has no key, **and a template author will mint one**."* `48` §2
refuses `sponsor` in favour of declaring canonical **`institution`** on `research` and `nonprofit`
— that is a live, cheap, adjudicated instruction, and **`54` carries neither the refusal nor its
replacement**. So nonprofit's grant-funding node ships unserved while two unrequested keys ship.
**Correct set: `organization`, `record_period`, `subject_of_record`, `institution` (per `48` §2).**
And record, as the row asked, that it *"would rather be refused than kept to save an id"* — NJ-NP-1
is still open and `54` did not answer it.

**`government` — 5 fields, ZERO earned, on a schema that asked to stay field-less.** 29 kept rows;
**one** `proposed_fields` key across all of them (`programme`, on
`government.grant-programme-administration`, which `49` §4.2(h) routes to `project`); the schema row
proposes **none** and explicitly asks to remain field-less this pass. `54` gives it `project`,
`record_type`, `record_period`, `property`, `subject_of_record` — of which `project` has one
signature and the other four have zero. This is the purest instance of the failure the re-run
exists to catch: a field set assembled from what its siblings got.
**Recommendation: `government` takes `project` only** (one signature, canonical key, zero mint
cost), or stays field-less until Joseph answers its own `open_question`. Everything else waits.

**`hr` — 5 fields, 3 earned, and its only two destination-candidates rest on one unsigned key.**
`people_cycle` is well signed (4). `work_type` has **zero** hr signature — it comes from
`law_practice`. Since `54` seeds `subject_of_record`, `workforce_unit` and `event` all `false`,
`hr`'s entire folder proposal is `people_cycle > work_type`, and **half of it is unearned**.
Worse: `hr`'s own `open_question` NJ-HR-1 makes this existential — *"The row survives only if
`workforce_member`, `workforce_unit`, `people_cycle`, and `personnel_case` form a legal, distinct
set… If those keys are rejected as role variants of generic person/organization/purpose, then 'our
firm is employer' is not a structural distinction and **HR should be refused**."* `54` rejects two
of the four as role variants (`workforce_member` → `subject_of_record`, `personnel_case` → `event`)
and does not answer NJ-HR-1. **That question must be put to Joseph explicitly before `hr` gets any
field row.**

---

## 4. Verdict per refusal (3), plus the one held key

**`consignment` → `event`: REJECT THE REFUSAL. This is the sharpest error in the merge.**

Three independent grounds:

1. **It creates a `dimension_order` that repeats its own parent.** `logistics.last-mile-pod`'s
   `template.why`, verbatim: *"the useful projection is **consignment/parcel -> delivery event or
   record_type**."* One row, one sentence, both concepts as adjacent levels. Fold them and that
   order reads `event > event` — which `00`:97 forbids by name: the validator checks *"that the
   proposed template does not **repeat a parent dimension**."*
2. **A consignment is a thing, not an occurrence.** `logistics`'s own definition: *"one described
   quantity of goods travelling under one carrier's undertaking"*, and *"a consignment reference
   identifies **goods**, not a person."* The other four members of `49` §4.2(a)'s fold —
   `quality_event`, `work_order`, `personnel_case`, `trading_occasion` — are genuinely occurrences.
   A consignment is the same ontological category as `asset` (an enduring identified physical
   thing carrying a reference), which `49` §4.2(b)–(d) treats as a *separate* category in the very
   same section. The fold puts one member on the wrong side of a line `49` itself drew.
3. **`49` answered the wrong objection.** `logistics` objected that *"`event` … carries a
   time-primary reading this family must not inherit"*; `49` replied that time-primacy is a
   property of `00`'s photos template order, not of the field. That is correct **and it does not
   touch the ontological objection**, which `49` never quotes and never answers.

**Recommendation: mint `consignment`** (`destination_eligible: true`, ceiling `validated` — the row
supplies the rule family: a labelled Consignment / Waybill / AWB / B/L / Container / Booking /
Tracking slot). It is the only destination-safe level `logistics` has: *"the one key in this family
that is safe to fold a folder on."* Refusing it leaves `logistics` filing by `site`, `asset` and
`supplier` — all counterparty- or facility-shaped — which is precisely what four of its seven rows
argue against. Cost: sixteenth key. Accept it.

**`carrier` → `supplier`: ACCEPT, with a condition.** `48` §2 refuses it and the proposing row
invites the refusal (*"R1c may reasonably seed it ineligible"*). But `logistics` also warns that
*"a consignment note routinely names three organizations — consignor, consignee and carrier — in
three different roles on one page"*, and once `carrier` folds into `supplier` the extractor must
pick one of three org tokens with no discriminator. **Condition: `supplier`'s `notes` must carry
`logistics`'s labelled-slot rule (Carrier / Haulier / Forwarder / Shipping Line / Airline) and the
three-role warning.** Also record the `48` self-contradiction plainly: **§2 refuses `carrier`, §7
lists it under "Adopt as search/privacy-only".** `54` found this; it should be fixed in `48`, not
just noted in `54`.

**`recruiting_cycle` → `people_cycle`: REJECT THE REFUSAL — the fold runs backwards.** §5.1.

**`issuing_body` held: REVERSE, under `54`'s own §8(b).** `48` §7 recommends it as one of seven
mints and warns that without it *"`business_operations.compliance-audit` loses the only fact
separating its own audits from its suppliers' evidence packs."* `54` holds it on an
inventory-hygiene reason — *"adding it now creates a second unreferenced orphan beside
`target_school`"* — which is **circular**: it is an orphan only because `54` allocated no schema to
it, and it is unallocated only because `54` believed `business_operations` was at a hard 6-field
ceiling. `54` §8(b) corrects that belief itself. Under the loose reading `business_operations` sits
at **5 destination-candidates with one slot free** (§5 table), so `issuing_body` is affordable and
`54` §11's *"the schema is at its 6-field ceiling, so it cannot be fixed by addition"* is **false by
`54`'s own §8(b)**. This is an internal contradiction, not a judgement call.
Second cost of the hold, which `54` never mentions: `career.credentials-licenses`'s
`template.why` recommends *"the **ISSUING AUTHORITY** first, then the CREDENTIAL, then the DOCUMENT
TYPE"* — and none of `54`'s five career keys serves any of the three. **A whole career row ships
with no representable folder proposal.**

---

## 5. The three adjudications, decided

### 5.1 `recruiting_cycle` / `people_cycle` / `record_period` — the one sitting `49` §1.6 required

**The sitting has already happened for half of it, and `54` missed it.** `47` §2.2 is titled *"The
corpus's own two non-members — do NOT merge these"* and its first entry is `people_cycle`, adjudicated
against the full period cluster with the reason stated: *"A '2026 graduate intake' answers **which
instance of a recurring process**, not what interval the content covers… Merging would put an
onboarding checklist and an oil-field production return on one folder level. **Keep separate.**"*
`49` §1.6's condition — *"adjudicated in one sitting with the period cluster so the roster does not
end with six bounded-period keys"* — **is satisfied**. `54` §6 item 1 carries it forward as open;
it is closed. **`people_cycle` is NOT `record_period`. Six bounded-period keys did not happen: the
roster ends with one period key plus one process-instance key.**

**The live question is the other half, and `54` decided it the wrong way round.**

`00`:70, verbatim: *"a Career template may define **company → role or recruiting cycle → document
type**."* **`00` names "recruiting cycle" itself.** Nothing in `00` names `people_cycle`. `54`
refuses the `00`-named spelling as *"a respelling"* of an un-`00`-named mint. Under D6's own
precedent — the stored key is `subject`, *"'course' is 00's prose"* — the direction of a fold
between an `00` word and a non-`00` word is settled: **the `00` word does not lose.**

Applying `47` §2.1's own three-part test to the pair:
- **One rule family?** Similar shape, different value gazetteers. Inconclusive.
- **One tree position?** No. `hr` puts `people_cycle` *below* a programme or workforce unit
  (*"should follow a programme or workforce unit rather than lead"*); `00`:70 puts the recruiting
  cycle in the **second** slot, as the alternative to `role`, under company.
- **Identical negative space?** **No, and this is decisive.** `hr` eliminates `fiscal_period`,
  `tax_year`, `term`, `creation_date`. `career.json`'s own `open_question` eliminates `institution`,
  `client`, **`application_cycle`** — a key `hr` never considered. Different holes.

**And the roles are opposite in the sense `00`:44 governs.** In `hr` the holder **runs** the cycle;
in `career` the holder is **subject to** it. That is *"roles that happen to contain the same entity
type"* — the same licence that produced `school`/`target_university` and `our_firm`/`client`.
One file can name both: `career.employer-side-hiring` is the employer side sitting inside the career
namespace, which is exactly why `54` §6 item 3 has to ask "could it be both?".

**DECISION: two keys, declared as a `role_split` pair — `recruiting_cycle` ↔ `people_cycle`** — with
the discriminator written on both: *the holder runs the cycle* vs *the holder is a participant in
it*. If Joseph prefers one key, **the surviving spelling must be `recruiting_cycle`**, because it is
the only one `00` wrote; `54`'s outcome — mint the unnamed spelling, refuse the named one — is the
one option not available.

**Third key in the same family, and it must be checked:** canonical `application_cycle` already
carries the bare alias **`cycle`**. Whatever ships, an unqualified "cycle" token now resolves
ambiguously across two or three keys. `49` §1.6 noticed the `application_cycle` collision and
declined the extension by citing PR-1 — but **PR-1 pins `purpose`, not `application_cycle`**
(verified: `canonical_fields.json`'s PR-1 note sits on `purpose` and nowhere else). The stated
reason for the mint is therefore wrong. The *conclusion* survives on a better principle — §5.3's
fence test — but the reasoning in `49` §1.6 should be corrected rather than inherited.
**Required either way: `application_cycle` drops the bare alias `cycle`.**

### 5.2 `workforce_unit`, and the narrowing `hr` actually needs

`54` says "only if narrowed", and the narrowing it means is `destination_eligible: false`.
**Adopt `48`'s `false` — but as a seed, not a ban**, identically to `organization` (§2). The two
keys make the same argument from the same row family and `48` grants promotion to one and not the
other with no stated reason.

**This does not save `hr`.** With `workforce_unit` seeded false, `hr`'s destination proposal is
`people_cycle > work_type`, and `work_type` has zero `hr` signature. `hr`'s real problem is not a
missing sixth field, it is that **only one of its two proposed folder levels was asked for by its
own rows**. Put NJ-HR-1 to Joseph before declaring anything (§3).

**Unchecked collision `54` inherited: `design_item` vs `product`.** `engineering`'s own elimination
checks `project`, `subject`, `property` and `repository` — **it never checks `product`**, because
`product` was minted in a different section of a different adjudication (`49` §1.5 / `48`). But
`design_item`'s worked example is *"Chiller model CH-2000"*, and `49` §1.5 defines `product` as *"an
article or formulation made through transformation"* widened to a neutral output key with `sku`,
`menu_item` and `commodity` as aliases. **A chiller model is a product model.** `49` §4.2(b) drew
the type-vs-instance line between `design_item` and `asset` and got it right; nobody drew the line
between `design_item` and `product`. **NARROW `design_item` to "the controlled design configuration
whose definition a file governs — never a saleable or sold article, which is `product`"**, and put
that sentence in both keys' `notes`, or the two will be filled from the same token.

### 5.3 Is `49` §3's routing rule enough to keep `record_type`, `work_type` and `artifact_type` apart?

**No. It is necessary, correct in direction, and insufficient in three specific ways.**

**(a) The rewritten `record_type` role sentence re-opens the door it was written to close.**
`54` §11 recommends *"a record that evidences that something happened **or was decided**"* so that
`government`'s minutes and finding aids are admitted. But a pleading evidences that a filing
happened; an approved drawing evidences that a design was decided; a signed SOW evidences that an
engagement was agreed. The added clause re-admits every signed or approved artifact in the corpus —
i.e. most of what `49` §3 had just routed to `work_type` and `artifact_type`.
**Fix: state the discriminator negatively and make `record_type` the residual of the three.**
Recommended `notes` text: *"If the file **is** the work product of a bounded engagement or course
→ `work_type`. If it is an **output of a making process** → `artifact_type`. `record_type` is what
remains: the file evidences that a transaction, operation or decision occurred. Where two readings
are both supported, `00` requires abstention, not the nearest declared key."*

**(b) The rule routes by document nature and says nothing about what happens when the routed key is
not declared by the active schema.** This is the actual gravity mechanism and neither `49` nor `54`
names it. `career` under `54` declares `record_type` and not `work_type`; a cover letter routes to
`work_type`, finds it undeclared, and the extractor's only options are to force it onto
`record_type` or abstain. Nothing tells it which. **Fix, and it must be in the key's `notes` not in
a doc: "a file whose routed type key is not declared by the active schema returns unknown; it is
never re-routed to the nearest declared type key."** Without that sentence, ten schemas sharing one
key guarantees the drift `54` predicted.

**(c) The rule keeps the keys apart and does nothing about the values inside them.** `record_type`
is an `enum` *"whose members are VALUES … never roster nodes"*, and P6's values table is per-field.
With ten schemas on one key, one value namespace holds a bank statement, a production return, a
proof of delivery, a chart note and a grant report. P9 groups on shared validated facts — so
`record_type = "return"` can join a tax return to an oil-field production return. **The routing
table has no value-side half. It needs one, or `record_type` needs a schema-qualified value scope.**
This is the same shape as `54` §14.2's `display_name` finding and belongs in the same fix.

**On `49` §3's missing fence principle** — `54` §11 correctly calls this *"a real defect"* but
diagnoses it as double-naming (*"`00` names `event` in both the Photos field sentence AND the Photos
template sentence — the same double-naming that fences `media_type`"*). **That diagnosis is wrong on
the facts.** `media_type` appears in `00`:48's Photos sentence **only**; it is not in `00`:70's
Photos template sentence (*"a Photos template may define year → event"*). And the keys `00` *does*
double-name — `school`, `term`, `course`, `work_type`, `application_cycle`, `project`, `stage`,
`artifact_type`, `event` — include four that `49` §3 and `54` widen freely. Double-naming is not the
fence.
**The principle that actually fits every case, offered for adoption:** *a key is **fenced** when its
role sentence cannot be stated without naming its domain* — `media_type` = "kind of **capture**",
`application_document_type` = "role inside an **application** packet", `application_cycle` = "the
**admissions** cycle an application belongs to". *A key is **widenable** when its role is
domain-neutral* — `project`, `stage`, `artifact_type`, `work_type`, `record_type`, and `event` once
widened to "the bounded occurrence a set of records is about". Under this principle the merge's
`event` widening is **correct** (and better justified than by the textual accident `54` relied on),
`media_type`/`application_document_type` stay fenced, and — as §5.1 needs — `application_cycle`
stays fenced, so career genuinely does need its own cycle key.

---

## 6. Per-schema field counts under BOTH cap readings

`00`:48 verbatim: *"usually three to six that may help build a future folder proposal **and several
additional fields used only for search, privacy protection, explanation, or later review**."*
**Strict** = 3–6 caps the total. **Loose** = 3–6 caps destination-candidates; `dest=false` are
additional. `54` §8(b) is right that loose is the reading `00` states; §14.3 owed this table.

| schema | fields (`54` §2/§9) | total | dest | fact-only | strict 3–6 | loose 3–6 | loose headroom |
|---|---|---|---|---|---|---|---|
| creative | project·artifact_type·stage·client·venue | 5 | **5** | 0 | ✅ | ✅ | 1 |
| law_practice | project·work_type·client·**our_firm**·**subject_of_record**·record_period | 6 | **4** | 2 | ✅ *at ceiling* | ✅ | **2** |
| government | project·record_type·record_period·property·**subject_of_record** | 5 | **4** | 1 | ✅ | ✅ | 2 |
| business_operations | **organization**·record_period·project·client·supplier·record_type | 6 | **5** | 1 | ✅ *at ceiling* | ✅ | **1** |
| construction_property | property·project·work_type·client·**our_firm** | 5 | **4** | 1 | ✅ | ✅ | 2 |
| engineering | design_item·artifact_type·asset·project·stage | 5 | **5** | 0 | ✅ | ✅ | 1 |
| manufacturing | site·product·asset·event·record_period·record_type | 6 | **6** | 0 | ✅ *at ceiling* | ✅ *at ceiling* | 0 |
| retail_hospitality | site·event·record_type·record_period·**product** | 5 | **4** | 1 | ✅ | ✅ | 2 |
| **hr** | people_cycle·work_type·**subject_of_record**·**workforce_unit**·**event** | 5 | **2** | 3 | ✅ | ❌ **below 3** | 4 |
| resource_operations | site·asset·**authorisation**·product·record_period·record_type | 6 | **5** | 1 | ✅ *at ceiling* | ✅ | 1 |
| logistics | record_type·event*·site·asset·record_period·**supplier*** | 6 | **5** | 1 | ✅ *at ceiling* | ✅ | 1 |
| **clinical_practice** | record_type·record_period·**subject_of_record**·**authored_by** | 4 | **2** | 2 | ✅ | ❌ **below 3** | 4 |
| nonprofit | **organization**·project·record_period·record_type·**subject_of_record** | 5 | **3** | 2 | ✅ | ✅ *at floor* | 3 |
| career | target_employer·employer·job_title·people_cycle*·record_type | 5 | **5** | 0 | ✅ | ✅ | 1 |

**bold** = `dest=false`. `*` = post-merge substitution (`consignment`→`event`, `carrier`→`supplier`,
`recruiting_cycle`→`people_cycle`), all three of which §4/§5.1 recommend reversing.

**What the two readings actually change — and it is not what `54` §14.3 expected.**
- `54`'s claim *"every schema landed inside `00`:48's 3–6 cap"* holds under the strict reading and
  **fails under the loose one** for `hr` and `clinical_practice`, which fall **below** the floor of
  three. **The loose reading makes `hr` worse, not better.** `54` §14.3's framing — that loose
  reading turns hr's weakness into "a question about which of its `dest=false` fields deserves
  promotion" — is only half right: it supplies headroom, but `00`:48's *"usually three to six that
  may help build a future folder proposal"* is a floor as well as a ceiling, and 2 is below it
  either way. `hr` needs a third destination-candidate or it needs Joseph to answer NJ-HR-1.
- For `clinical_practice`, 2 is **correct** and the fix is to go lower, not higher (§3): one key.
- The loose reading's real beneficiaries are `law_practice` (2 free dest slots) and
  **`business_operations` (1 free slot — which is exactly where `issuing_body` goes, §4)**.
- Under **either** reading `manufacturing` is genuinely full at 6 destination-candidates and is the
  only schema with no room to absorb a correction.

---

## 7. What `54` got wrong

Ranked by consequence, evidence-first.

1. **`clinical_practice`, `government` and `logistics` were given `record_period`; `government` was
   given four unsigned keys; `clinical_practice` was given three.** Test 7 fails on three schemas,
   not the two the brief suspected. §1, §3.
2. **`consignment` → `event` produces `event > event` in `logistics.last-mile-pod`'s own recorded
   order** — a `00`:97 validator failure, in the corpus, today. §4.
3. **`54` §11's *"business_operations… is at its 6-field ceiling, so it cannot be fixed by
   addition"* is false under `54` §8(b).** Internal contradiction; it is the sole basis for holding
   `issuing_body`, which in turn strands `career.credentials-licenses` entirely. §4, §6.
4. **The fold direction on the cycle key discards the only spelling `00` wrote.** `00`:70 names
   *"recruiting cycle"*; nothing names `people_cycle`. §5.1.
5. **`54` reports `49` §1.6's condition as unmet. `47` §2.2 met it** — `people_cycle` was
   adjudicated against the whole period cluster and excluded, with reasons. An open question was
   carried to Joseph that is already closed. §5.1.
6. **`supplier` is assigned to the two schemas that never proposed it and withheld from the two that
   did.** `manufacturing` and `retail_hospitality` are the corpus's only `supplier` proposers and
   neither receives it; `business_operations` (zero signature — `48` §6b proves the hole is
   proposed *nowhere* in that family) does. §1.
7. **`authorisation` ships British-s beside `organization`'s American-z**, in a namespace whose
   founding rule is that two spellings are two columns. `00` is 27–0 for `organization`. §2.
8. **`tax_year`'s existing alias `fiscal_year` collides with `record_period`'s new alias
   `fiscal_period`.** Neither `47` nor `54` checked the new aliases against the live ones. §2.
9. **`design_item` was never checked against `product`.** Cross-adjudication gap inherited whole.
   §5.2.
10. **`54` §11 misdiagnoses the `media_type` fence as double-naming.** `media_type` is not in
    `00`:70. The correct fence principle is supplied in §5.3 and it *strengthens* the `event`
    widening `54` made on weaker grounds.
11. **`finance.account_holder` fell through the pass.** It was moved out of `finance.fields[]` into
    `proposed_fields` during this session (commit `b2dbb08`); `49` §4.1 and §2.7 recommend adopting
    it as a mint with `institution` as its `role_split` partner, `destination_eligible: false`;
    **it is not among `54`'s fifteen.** `finance` is a live `SCHEMA_IDS` member, so unlike the
    thirteen this is a field a shipping schema lost with no replacement.

Two things `54` got right that deserve saying, because they were the hard calls: the `event`
widening (right answer, wrong reason — §5.3), and the refusal of `instruction` and the
`fiscal_period`/`reporting_period` collapse inherited from `49`/`47`, which are the two best pieces
of work in the whole cluster.

---

## 8. Ranked list — what must change before this touches `canonical_fields.json`

**Blocking (4).**

1. **Strip the unsigned assignments.** `record_period` off `clinical_practice` and `logistics`;
   `record_type` off `clinical_practice` and `government`; `authored_by` off `clinical_practice`;
   `property` off `government`. Reduce `government` to `project` or to nothing; reduce
   `clinical_practice` to `subject_of_record`. (§1, §3)
2. **Reverse `consignment` → `event`; mint `consignment`.** Sixteenth key. (§4)
3. **Put NJ-HR-1 to Joseph before `hr` receives a field row**, and answer it in the same sitting as
   `hr`'s `work_type`, which has zero hr signature. (§3, §6)
4. **Decide the cycle family in one place** — `recruiting_cycle` ↔ `people_cycle` as a `role_split`
   pair (recommended), or one key spelled `recruiting_cycle`; and drop the bare alias `cycle` from
   `application_cycle`. (§5.1)

**High (5).**

5. **Reverse the `issuing_body` hold.** `business_operations` has the slot under `54` §8(b); it
   fixes `compliance-audit` and `career.credentials-licenses` together. (§4)
6. **Write the routing rule into `record_type`'s `notes` with all three halves**: the negative
   discriminator, the *"routed key not declared → unknown, never re-route"* clause, and a value-side
   scope. The rule `54` proposes is one third of what is needed. (§5.3)
7. **Fix the alias collisions before they land**: `tax_year` drops `fiscal_year`;
   `application_cycle` drops `cycle`. (§2, §5.1)
8. **Rename `authorisation` → `authorization`.** (§2)
9. **Restore `nonprofit`'s funder role** by declaring canonical `institution` on `nonprofit` and
   `research` per `48` §2, and drop `project` and `record_type` from `nonprofit`. (§3)

**Medium (4).**

10. **Narrow `design_item` against `product`** and write the sentence on both keys. (§5.2)
11. **Give `career` `work_type`** alongside or instead of `record_type`. (§2)
12. **State the `employer` ↔ `our_firm` discriminator** on both keys. (§2)
13. **Carry `finance.account_holder` into the pass** per `49` §4.1, or record explicitly that
    `finance` is shipping without it. (§7)

**Also fix in the source documents, not just here (2).**

14. `48` §2 refuses `carrier`; `48` §7 adopts it. One of the two is wrong — §7 appears to be the
    stale line.
15. `49` §1.6 justifies the `people_cycle` mint by citing PR-1, which pins `purpose` and not
    `application_cycle`. The conclusion survives under §5.3's fence principle; the reasoning should
    be replaced rather than inherited.

---

## 9. What this pass did not check

- The **prose** demand in 291 `template.why` / `open_question` blocks was sampled, not enumerated.
  The signature table in §1 counts `proposed_fields` only. Where a key is marked "no signature",
  that means no structured proposal — `venue` on `creative` is the worked example of a key that has
  zero structured signature and 13 rows of prose support, and it is accepted for that reason. The
  three schemas failing test 7 in §3 were each checked against prose as well as structure; the rest
  were not exhaustively.
- **`reliability_ceiling`** per key was not re-derived. `47`/`48`/`49` each set them and this pass
  did not attack them.
- **`role_split` reciprocity** and the `check.py` gate's reaction to 15–16 new keys were not run.
- The **`51` launch template draft** and `53`'s human-sense-check verdicts were not re-tested
  against the amended field sets; `53` failed 11 of 15 launch roles on the *existing* vocabulary and
  nothing in this pass changes whether a real person would say `record_period` or `subject_of_record`
  out loud. **That test is still owed on the new keys**, and §5.3's value-side gap is where it will
  bite first.
