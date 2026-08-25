# `construction_property.survey-valuation` — lab notes

Depth: J-DEPTH. Row kind: **template** on schema `construction_property`. Launch: **placeholder**
(`fields: []`). Absorbs and retires the legacy row `prop.survey-valuation` (ROSTER.md Appendix A).

**Verdict: kept, not refused.** The row was challenged on two grounds by the dispatch — that it may be
one world with `site-survey` under two names, and that a valuation is a *document type*, which is the
charge that refused `compliance-certificate`. Both are answered below, in full, and neither holds.

**Status of this pass.** The row was written once under the retired `Depth: GIST` label. The JSON was
already substantial (~32KB) and its arguments were sound; the memo was 4.5KB and carried almost none of
them. This pass therefore **deepened the memo and extended the JSON in three targeted places**, rather
than rewriting. Nothing that was already right was changed. See *What changed in this pass* at the end,
which is written against the JSON as it now stands rather than against intent.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — the only document quoted. Every quotation in the
  JSON and in this memo was grep-verified back out of it verbatim (see **Audit** at the end).
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation (step 2 never-alone, step 5 protective
  ordering), §5 closed edge vocabulary, §9 failure modes, PR-1, PR-6.
- `planning/domains/_CONTRACT.md` — rules 1–3, 5, 8, 10, 11–15.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/roster.json` (every collision target checked
  mechanically against the roster); `planning/domains/canonical_fields.json`.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 as narrowed, J-IND, J-DEPTH.
- **Neighbour files read in full before writing, as the dispatch required:**
  `construction_property.research.md` (the deepened schema anchor — the default template is quoted
  below and this row's node test is measured against it), `construction_property.site-survey.research.md`
  (the paired row, whose split argument is answered reciprocally), `construction_property.development-appraisal.research.md`
  (J-DEPTH, 46KB), `construction_property.compliance-certificate.research.md` (the refusal this row is
  charged with resembling), `construction_property.mortgage-brokering.research.md`,
  `construction_property.sale-purchase.research.md`, `construction_property.agency-listing.research.md`,
  and the landed launch row `finance.household-property` (both files).

---

## The schema's default template, and exactly how this row differs

The anchor states the paragraph every sibling must differ from:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles*. **Not time-first.**

And it states the trap in one sentence: *`variation`, `snagging`, `dilapidations`, `retention`,
`preliminaries`, `certificate`, `drawing`, `schedule`, `survey`, `valuation` and `report` are values of
`work_type`, not rows.* **`survey` and `valuation` are both on that list, and both are in this row's
name.** That is not an accident of naming — it is the charge, and the row has to answer it on evidence
rather than on the strength of being a familiar industry noun.

The difference this row claims is **not** the noun. It is that the schema default's second level is the
**instruction** — the job, the letting, the scheme, the block — and this row's natural second level is
the **purpose the opinion was given for**. Those are different things and they produce different trees.
The same property, inspected by the same surveyor in the same month, produces a report *for a purchase*,
a report *for a lender*, a report *for insurance* and a report *for probate*, and the four are nearly
identical documents with four different addressees and four different bases. `00`'s own distinction is
exactly this: *"Topic answers what a file is about, while purpose answers what the file was for."* An
instruction-first tree collapses those four into one drawer, or scatters them across four instructions
that are really one property's history. That is a genuine divergence from the default paragraph, and it
is leg 2 of the node test.

The recommendation, held as prose (the JSON's `dimension_order` is empty by binding contract, because a
dimension may only branch on a field the entry's schema declares and this schema declares none —
`_CONTRACT` rules 10 and 15, CONNECTION PR-6): **property → purpose/transaction → report type**.
`property` stays first for the anchor's reason — a building outlives every instruction ever given about
it, and a surveyor returns to *the building*. Report type is last by the parent-context rule: *"a parent
dimension should provide the context required to understand the child"* — `Level 2 report` names no
property, exactly as `Homework 3` names no course. Not time-first: *"For document and record domains,
project, function, or subject usually comes before time because putting year first scatters related work
across calendar folders."* And whatever eventually lands is a recommendation, not a filesystem: *"The
system recommends an order based on the domain template, but the user can reverse, remove, add, or
flatten dimensions."*

**One honest caveat, stated rather than smoothed.** The anchor also says the *reversal* of the default
order is licensed and that **reversing is not a difference that earns a node**. This row is not claiming
a reversal — it keeps `property` first and changes the *second* level from instruction to purpose. That
is a substitution, not a reversal, and it is a weaker claim than leg 1 or leg 3 below. Leg 2 alone would
not carry this row. It does not have to.

---

## The node test, leg by leg

CONNECTION §2: a template row exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. Any one leg suffices.
This row clears all three, and the strongest is the first.

### Leg 1 — detection signals. Differ, and this is the decisive leg.

The signal is not a word. It is a **structure**, and it is the structure of *reliance*:

> a labelled **addressee block** naming the party entitled to rely · a stated **purpose** of the
> valuation or inspection · a **basis** or standard the opinion is given under · an **inspection date
> distinct from the report date** · a **limitation-of-liability, exclusions or third-party-reliance
> clause**.

Five co-occurring labelled structures, none of which is a document-type word and none of which is an
address. That combination appears on no other document in this family. A drawing has a title block and a
revision apparatus; a certificate has a scheme reference and a signed declaration; a contract has
recitals and an execution block; a schedule of works has a priced table. **None of them has an addressee
who is entitled to rely, or a clause limiting who may.** The reliance block exists because the document
is written to be *acted on by a named party who may sue the author* — that is a purpose, and it leaves a
structural fingerprint.

The second signal is independent of the first and would carry the row alone: the **condition-rating
structure** — building elements listed down the page, roof, walls, windows, services, drainage, each
carrying a coded rating and a narrative, with a front-loaded summary of urgent and further-investigation
items. It is a table, and it is the table `00` warns is where the meaning lives: *"Tables matter because
resumes, forms, applications, invoices, and administrative documents often place their most useful
information in cells rather than body paragraphs."*

The third is the **comparables table** behind a figure — addresses, dates, prices, floor areas and
adjustment columns. It is worth naming separately because it is the row's sharpest privacy problem (leg
3) and because it is the one member that routinely arrives detached from its report, as a spreadsheet.

### Leg 2 — recommended dimensions. Differ, on `purpose` as the second level.

Argued above. Substituting purpose for instruction at level two. The weakest of the three legs, said so.

### Leg 3 — privacy rules. Differ from the schema default, and this is the second-strongest leg.

The schema's default posture is `potentially_sensitive` on the strength of *an address plus a named
party*. This row's posture differs in **kind**, not degree, on one fact: **the exposed party is
routinely not the holder, and cannot consent.**

- A **comparables schedule** lists other people's homes, with their sale dates and prices, in rows.
- A **schedule of dilapidations** is a costed argument about a named tenant's alleged breaches.
- A **probate valuation** is about someone who has died.
- A **mortgage valuation** names a private individual, the property they are buying, a lender, a sum of
  money, and a defect that would change what the property is worth — in one file.

`00`'s corpus sentence covers several of those categories in one breath: the corpus *"can include
identity documents, account statements, tax records, medical information, legal records, credentials,
private correspondence, GPS metadata, employment materials, and educational records"*. And the handling
consequence is stated where this row routes primarily, Protected Records: *"Protected material should
not be included in cloud-model prompts by default, should not display raw content in general group
summaries, and should not be moved automatically without a user policy that explicitly permits it."*

The third-party point is marked **inference**: `00` does not write a sentence about non-consenting third
parties in a survey report. It is an argued extension of the protective posture, not a design claim.
This row assigns only the catalogue value `potentially_sensitive`; the handling class is P7's.

**Verdict: three legs, two of them independently sufficient. `refuse_node: false`.**

---

## Charge (a): is this one world with `site-survey` under two names? — answered from this side

The paired row argued the split from its own side and concluded **two worlds, separated by deliverable
rather than by subject**: *measuring the land vs pricing the asset*. The dispatch is right that the
argument was made once, from one side, and never confirmed from this one. **Confirmed. I am not
reversing it,** and the reasoning from this side is not a restatement of theirs — it runs the other way.

Their argument is that a measured survey has **no addressee**. Mine is that this row has **nothing
else**. Strip a valuation report of its reliance furniture and there is no document left: a market value
with no basis and no valuation date is a guess, a condition rating with no inspection date is an
opinion about nothing, and a defect conclusion with no author designation is a rumour. **The addressee
and the basis are not decoration on this row's documents — they are what makes the document a document.**
A measured survey loses nothing at all if you remove its cover letter; the coordinate file is still the
deliverable, and it is still true. That asymmetry is the split, seen from here: one row's value survives
the loss of its framing and the other's does not.

The consequence for filing, which is what actually matters: a measured survey is consumed **once**, by
the design that follows it, and then becomes a dated record of a state of the ground. A valuation is
consumed **at a moment, by a named party, for a stated purpose**, and is then re-read years later by
people who need to know *what was known when* — the buyer who finds subsidence, the tenant served with a
dilapidations claim, the executor. Their filing lives are different lengths and different shapes.

**The hard middle case, and it is genuinely hard.** A structural engineer's inspection report measures
crack widths against a numbered schedule and then concludes. Both rows want it. The rule, written
identically into both nodes' `collides_with` so the pair is reciprocal: **where a document carries an
addressee, a stated purpose and a reliance clause, the opinion reading wins, because that is what the
document is FOR** — `00`'s topic-versus-purpose distinction applied directly. The fixture
`Structural inspection - rear bay - Meridian Eng.pdf` carries it on both sides.

**The reciprocal fixture the other way.** `1042-EX-01 Existing site plan Rev A.pdf` — a scaled plan with
a north point, spot levels, a datum note and a surveying practice's title block, and **no addressee, no
purpose statement, no liability wording.** It must not fire this row. It is named as a negative fixture
here and as the paired row's own material there.

**What would make me reverse.** If the reliance structure turned out to sit on *both* rows' deliverables
in practice — if measured surveys were routinely issued with addressee blocks and reliance clauses —
then the split would rest on file format alone, which is `SOURCE_TYPES` and not a node, and the correct
outcome would be one row. Nothing in the design docs or in the paired row's file list suggests that, and
its file list is dominated by coordinate CSVs, point clouds and scan registration reports, which have no
addressee to give. The split stands.

---

## Charge (b): is a valuation a *document type*, like `compliance-certificate`? — answered

This is the more serious charge and it deserves the refusal's own test applied honestly rather than
deflected. `compliance-certificate` was refused because, when its candidate signal was stripped to what
would actually have to fire, **two things remained: a document-type word and an address** — and both are
constitutionally never-alone on this schema. A row whose entire support is never-alone evidence cannot
clear activation (CONNECTION §4 step 2), so it would be a row that never fires. Its other two legs
failed outright: its dimensions were the schema default, and its privacy posture was the schema's.

Run the same strip on this row and a different residue remains.

| The refusal's test | `compliance-certificate` | this row |
|---|---|---|
| What survives stripping the signal to what must fire? | a document-type word (*certificate*) + an address | a **five-part labelled reliance structure** + a **coded condition-rating table** — neither is a word, neither is an address |
| Dimensions differ from the schema default? | No — property → instruction → function *is* the default | **Yes** — purpose substitutes for instruction at level two |
| Privacy differs from the schema default? | No — address + named installer, identical to every sibling | **Yes** — the exposed party is routinely a non-consenting third party (comparables, tenants, the deceased) |
| Is the coverage already authored elsewhere? | **Yes, three times** — `finance.household-property`, the schema row, `building-control` | **No** — no other row in the catalogue carries the reliance structure or the condition-rating table |
| Is the framing a residual's framing? | Yes — *"a durable purpose but no broader group"* is Independent Records by name | No — this row's material is transaction- and dispute-coherent, and its primary residual is Protected Records, which is a *protection* route rather than a *no-group* route |

The row is aware that it is *called* by a `work_type` value. So is `progress-photos`, which the anchor
holds up as the family's best reasoning, and which survives because it is recognised by a **different
detection method** rather than by its noun. The same logic saves this row: it is recognised by the
reliance structure, not by the word `valuation`. **The name is a liability, not the argument** — and the
JSON's first `never_alone` says so in as many words: *the word 'survey' alone — the row's own name is
the trap.*

**Where the charge lands partially, and it is not hidden.** `compliance-certificate`'s deciding evidence
was that the coverage was already carried three times. This row's coverage is carried **once** elsewhere,
by the landed `finance.household-property`, whose own `work_types` include *appraisal* and *inspection*
and whose own file examples include an appraisal report and an inspection report. That is not a fourth
authoring, but it is a second one, and it is the reason NJ-CP-VAL-3 below is a real question rather than
a formality.

---

## Files considered and rejected

The tempting false positives, and what discriminates each. A row that only lists what it holds has not
been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| `Free market appraisal - Oakfield - Hart & Co.pdf` *(kept in the JSON as a collision fixture)* | An estate agent's appraisal is **written to resemble a valuation** and gives the same kind of figure for the same property. Discriminator: no basis of valuation, no inspection date, no liability limitation — and an agency fee schedule at the back. It is marketing, and it routes to `construction_property.agency-listing` and to Receipts and Confirmations. Kept precisely *because* it imitates this row on purpose. |
| `1042-EX-01 Existing site plan Rev A.pdf` *(kept as the load-bearing fixture)* | The paired-row fixture. Same practice, same address, same PDF. Discriminator: a datum and spot levels, and **no addressee at all**. |
| An **EPC** | A registered certificate with a rating and an expiry — `compliance-certificate`'s shape, and travelling with tenancy compliance rather than with an instruction. Not claimed here, and `site-survey` rejected it for the same reason. |
| An **insurance policy schedule** | `finance.insurance-personal` / `finance.insurance-corporate`. The reinstatement-cost **assessment** is this row's opinion; the **policy it feeds** is finance's record. The fixture `Reinstatement cost assessment 2026.pdf` carries the split on its face. |
| A homebuyer's own **snagging list** | `construction_property.snagging-defects`. A list of defects written by the person who owns them is not an opinion given under a basis to an addressee. |
| A **tenancy inventory / check-in report** | Byte-for-byte the same shape as a schedule of condition — dated, photographed, room by room. Discriminator: a tenancy, a tenant, a deposit and a check-in/check-out framing route to `construction_property.inventory-inspection`; a professional author, a lease-clause reference and costed breaches stay here. |
| A **development appraisal** with residual land value | `construction_property.development-appraisal`, whose J-DEPTH memo already argued this seam and named the third term. It prices a scheme that does not exist; this row prices an asset that does. **Reciprocated this pass**: that row assigns the *investment valuation of a standing income-producing asset* to this row, and this row has accepted it into `work_types` rather than leaving the assignment unclaimed. |
| `Residential Appraisal Report - 42 Oak Street.pdf` *(added this pass as the reciprocal fixture)* | The file that must not be **lost to** this row. See the section below. |
| A **specimen report** or published guidance on survey levels, downloaded | Reference Clips. It is a template, not a record, and it names no property. This is the commonest bulk contaminant in a practitioner's folder. |
| A **surveyor's fee invoice** or survey booking confirmation | Receipts and Confirmations, by `00`'s own definition — *"isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents"*. It sits next to the report and is not one. |
| An **expert report** with a duty-to-the-court declaration | `law_practice.expert-materials`. Discriminator: a matter reference, a declaration of duty to the court, or an instruction from a solicitor. A client-addressed report given under a professional basis stays here. |
| A **contacts file** of surveying firms | `00` requires contact data be privacy-protected rather than used to create folder proposals. A file-kind signal at most; using it as an example would have been misleading. |

---

## The collision fixture, in both directions

The addendum requires both halves, and requires the same bytes to be named on both sides where two rows
compete. Both are now in the JSON.

**A file that would wrongly fire this row:** `Free market appraisal - Oakfield - Hart & Co.pdf`. It has a
property, a figure, a firm and a signature, and it is deliberately laid out to read as a professional
opinion. The discriminating absence is the reliance furniture — no basis, no inspection date, no
liability limitation. This is the fixture that proves the row is detected by structure and not by the
presence of a number next to an address.

**A file that must not be lost *to* this row:** `Residential Appraisal Report - 42 Oak Street.pdf`. This
is not a hypothetical — it is a **file example on the landed `finance.household-property` row**, named
here in the same words. It has an appraisal firm's certification block, a labelled Subject Property and
effective valuation date, comparable-sale tables, and a lender as intended user. Every one of this row's
deterministic signals fires on it. **And it is still the homeowner's record.** The resolution, written
into the fixture's `must_not_conclude` this pass: finance is a safety domain — *"Finance, identity,
medical, and legal material should be implemented first as safety domains"* — so under CONNECTION §4
step 5 the protective ordering runs first and the household reading leads. This row concedes it rather
than competing for it. The unresolved half is NJ-CP-VAL-3.

---

## Reciprocal boundaries

Every neighbour this row could steal from, stated in both directions. Each is authored in
`collides_with` in the JSON and each was checked against the neighbour's own file before being written.

| Neighbour | This row holds | That row holds | Same bytes named on both sides |
|---|---|---|---|
| `construction_property.site-survey` | the reliance-bearing opinion: addressee, purpose, basis, ratings, liability limit | measured geometry: coordinates, levels, datum, feature codes, sample register — no addressee | `Structural inspection - rear bay - Meridian Eng.pdf` (middle case) and `1042-EX-01 Existing site plan Rev A.pdf` (negative here) |
| `construction_property.agency-listing` | a basis of valuation, an inspection date, a liability limitation | a marketing recommendation, an asking price, a fee schedule, portal copy | `Free market appraisal - Oakfield - Hart & Co.pdf` |
| `finance.household-property` | the professional opinion **as** a commissioned instruction | the same document as one record in a household's permanent property-and-money file; **it leads, because finance protects first** | `Residential Appraisal Report - 42 Oak Street.pdf` |
| `finance.loans-mortgage` | inspection, basis of valuation, reliance clause | offer, product, rate, repayment schedule, account number | `Mortgage valuation - case 88213.pdf` |
| `construction_property.mortgage-brokering` | the valuation as a professional deliverable | the same PDF as one item in a broker's case file, under that row's ownership discriminator (fact find, checklist, suitability letter) | `Mortgage valuation - case 88213.pdf` — that row's memo already states the offer's *three* homes; this row does not reopen it |
| `construction_property.sale-purchase` | the report | the same report **supplied into** a live transaction pack, discriminated by stage vocabulary and open enquiries | the survey supplied in; that row's NJ-CP-13 owns the residue question and this row defers to it |
| `construction_property.commercial-lease` | a surveyor's dated inspection, costed remedies, a professional opinion | the lease itself, its rent reviews, its schedules | `Schedule of dilapidations - Unit 4 - served.pdf` |
| `construction_property.inventory-inspection` | professional author, lease-clause reference, costed breaches | tenancy, tenant, deposit, check-in/check-out framing | a schedule of condition versus a check-in report |
| `construction_property.development-appraisal` | a completed asset inspected on a date and reported to an addressee | a residual land value, build cost inputs, a finance and profit model | an investment valuation of a standing asset — **assigned to this row by that row, accepted here** |
| `law_practice.expert-materials` | a client-addressed report under a professional basis | a matter reference, a duty-to-the-court declaration, a solicitor's instruction | a surveyor's report written for proceedings; a Scott schedule |

---

## Neighbours considered that did **not** get an edge

- **`legal` and `finance` as schemas.** Real overlaps, but `also_holds_with` joins **schemas** and this
  is a template row (CONNECTION §5). The overlap is therefore expressed as `also_schema` on the
  dilapidations, mortgage-valuation and household-appraisal file examples, which is the correct
  instrument. `also_holds_with` is deliberately empty and this is why.
- **`government.housing-authority`.** Considered for statutory disrepair inspections. Rejected: no
  shared *discriminating evidence item* appears on this row's files — only topical adjacency, which is
  shelving rather than evidence.
- **`academic` / `business_operations.user-research`.** The word *survey* collides outright, and it is
  the row's own name. But the collision that matters is between the **measured** survey and the
  **questionnaire**, and it is already authored on `construction_property.site-survey` against
  `business_operations.user-research`. Duplicating it here would author a collision on a word rather
  than on evidence. It is instead recorded where it belongs, as this row's first `never_alone`.
- **`construction_property.building-control`.** Considered because a valuation sometimes cites building
  regulations status. Rejected: the citation is a sentence, not a shared evidence structure. That row's
  fingerprint is an application reference and an authority decision.
- **`manufacturing.inspection-record`.** Similar inspect-and-report shape. Rejected for the reason
  `site-survey` gave: a part number and a drawing tolerance are not an address and a basis of valuation.

## `role_split` — deliberately empty

`role_split` requires *different field keys* pointing at the neighbour holding the other role. This row
declares no fields and the schema declares none, so a `role_split` here would name keys that do not
exist. The role problem is real and is recorded as NJ-CP-VAL-1 instead — three rows in this catalogue
now independently want the same key, and one canonical proposal at R1c should serve all three.

---

## `proposed_fields`

**None**, and the prohibition is doing real work here rather than being a formality. `fields: []` is
required by D1 as narrowed and CONNECTION PR-6; the schema declares no field rows.

The prose candidates, recorded for R1c and **not minted**:

1. **A property key.** Wanted by every row on this schema. This row seconds the schema row's existing
   proposal rather than minting a variant, per the dispatch's instruction. Note the difficulty this row
   adds to it: the address on these documents appears simultaneously as the subject property, the
   addressee's home, the surveyor's office and *several other people's homes in the comparables table*.
   Whoever mints it owes a rule for which row of a table is the subject.
2. **A purpose-of-report key.** Blocked by PR-1 — `purpose` stays College-applications-scoped, and this
   row must not mint a clone. This row is the clearest non-admissions purpose-coherent situation in the
   construction family and is recorded as **evidence for NJ-3** rather than resolved here (NJ-CP-VAL-2).
3. **A transaction-side role key.** NJ-CP-VAL-1. Not minted; three rows want it and one of them should
   get it once.

---

## NEEDS-JOSEPH

- **NJ-CP-VAL-1 · The transaction-side role.** A mortgage valuation is commissioned by a lender, paid
  for by a buyer, seen by a broker and filed by all three; the addressee block names one party in one
  role without saying whose filesystem it is. Reciprocal with
  `business_operations.contract-administration` (buying versus selling) and
  `construction_property.site-health-safety` (authored versus submitted); `construction_property.mortgage-brokering`
  states the same hole as an **ownership** problem. Four rows, one missing key. This row mints nothing.
  *Alternatives and their costs:* (a) one canonical `party_role`-shaped key at R1c — serves four rows,
  but the value set has to be settled once across finance, construction and business_operations; (b)
  leave it unminted — every one of the four rows keeps guessing, and the guess is invisible to the user;
  (c) resolve it as a **group** property rather than a file fact — cheaper, but activation may not read
  group membership, so it would not help detection.

- **NJ-CP-VAL-2 · May `purpose` be a dimension here at all?** Purpose is this row's load-bearing second
  level — the same property reported on for purchase, for lending, for insurance and for probate — but
  under PR-1 `purpose` is a College-applications field. *Alternatives:* (a) generalise `purpose` beyond
  admissions, which affects far more than this row and belongs to NJ-3; (b) mint a construction-scoped
  clone, which is exactly the synonym-minting the contract forbids; (c) leave the recommendation as
  prose, which is what this row does — at the cost that the row's second-strongest node-test leg is
  unexpressible in the JSON.

- **NJ-CP-VAL-3 · The household seam, stated reciprocally.** The landed `finance.household-property`
  already claims appraisal and inspection reports among its own `work_types` and names
  `Residential Appraisal Report - 42 Oak Street.pdf` as its own file example. Neither row is wrong: the
  document is this row's situation held for that row's reason. This pass resolves the *activation*
  question in the household row's favour, because finance is a safety domain and protects first. What
  remains for Joseph is the *proposal* question: in a homeowner's corpus, which row should the product
  offer first — and does a professional's copy of the same report in an instruction file behave
  differently from the homeowner's copy? That is a question about someone's real filing life, not about
  evidence in the file. *Alternatives:* (a) always household-first for a private corpus, professional
  only where an instruction reference is present — clean, but silently loses the purpose dimension for
  homeowners; (b) offer both and let the user choose — honest, at the cost of a decision on every
  report; (c) split on corpus type, which needs a corpus-level signal this product does not yet have.

- **NJ-CP-VAL-4 · The comparables spreadsheet.** `Comparables - Oakfield.xlsx` arrives detached from any
  report, has no addressee and no narrative, and lists **other people's addresses and sale prices**. It
  currently routes to Review Later. That is honest but arguably too permissive: as a standalone file it
  is third-party personal data with no protective framing around it. Raised because the row's own
  privacy leg argues for the cautious reading and the current routing does not take it. Not changed
  unilaterally, because Protected Records is a strong route and a spreadsheet with no addressee has none
  of the row's reliance structure to justify it.

---

## What changed in this pass — checked against the JSON as written

The dispatch warned that a memo documenting edits its data lacks is worse than a thin row. Every claim
below was verified against the file after writing it.

**Preserved unchanged** — the JSON was a verified-but-shallow draft only in its *memo*; the data was
already at depth and was not rewritten. Untouched: all 9 `deterministic` signals, all 7 `needs_llm`
entries, all 10 `never_alone` entries, all 43 `proposed_context_terms`, all 6 `grouping_reasons`, the
`template.why` prose recommendation, `file_kinds`, all 6 `falls_through_to` entries, `sensitivity` and
`sensitivity_why`, `open_question`, `fields: []`, `proposed_fields: []`, `role_split: []`,
`also_holds_with: []`, and 10 of the 11 `file_examples`.

**Added to the JSON (three changes, all verifiable in the file):**

1. **A new file example** — `Residential Appraisal Report - 42 Oak Street.pdf`, `text_document`,
   `also_schema: "finance"`, falling through to Protected Records. It is the reciprocal collision
   fixture the addendum requires: the file that must not be **lost to** this row, named in the same
   words the landed `finance.household-property` row uses. Its `must_not_conclude` carries the safety-
   domain resolution verbatim. `file_examples` count: **10 → 11**.
2. **A new `work_type` value** — *investment valuation of a standing income-producing asset*, accepting
   the assignment the J-DEPTH `development-appraisal` row made to this row and left unclaimed.
   `work_types` count: **17 → 18**.
3. **Two `collides_with` signals extended** — `construction_property.development-appraisal` now records
   the three-term reading reciprocally and states that this row accepts the assignment;
   `finance.household-property` now names the shared fixture bytes and states that the household reading
   leads because finance protects first. No new edges were added and none were removed; the count stays
   at **8**.

Plus one label correction: `one_line` said `Gist-level placeholder (J-IND)` and now says
`Placeholder row (J-IND, researched to J-DEPTH)`. The `Depth: GIST` header on this memo is replaced by
`Depth: J-DEPTH`.

**Added to the memo (everything else on this page).** The gist memo carried the verdict; it carried
almost none of the argument. New: the schema default template quoted and the difference from it stated;
the node test argued leg by leg with a stated weakness on leg 2; charge (a) answered *from this side*
with a non-duplicative argument and an explicit statement of what would make me reverse; charge (b)
answered against the `compliance-certificate` refusal's own test, in a table, including where the charge
lands partially; the rejected-files table expanded from 4 entries to 12; the collision fixture stated in
both directions; a 10-row reciprocal boundary table; `role_split`'s emptiness explained; the
`proposed_fields` candidates given arguments; and NJ-CP-VAL-1/2/3 given explicit alternatives with
costs, plus a new **NJ-CP-VAL-4**.

**Reversed: nothing.** The gist verdict was `refuse_node: false` and it survives the full test. The
gist row's split with `site-survey` is confirmed, not reversed. No neighbour's file was edited; the
development-appraisal and household-property readings were **adopted**, not contradicted.

**Not done, and why:** `dimension_order` stays empty (binding contract), `proposed_fields` stays empty
(PR-6), and no field key was minted. The row is shorter on schema content than a launch row by design,
not by omission.

---

## Audit

- JSON parses (`python3 -m json.tool`). Key set matches the landed siblings on this schema.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (`text_document`, `spreadsheet`, `image`,
  `archive`).
- Every `collides_with.domain` was checked mechanically against `roster.json`; every
  `falls_through_to.residual_template` is a `00` §7.3 residual name.
- Every quotation in this memo and in the JSON was grep-matched verbatim out of
  `planning/00-database-agent-product-design.md`, including the curly apostrophe in *"the product's
  goal"*. No numeric thresholds, no confidence scores, no handling classes.
- Only the two assigned files were written. No neighbour, roster, `src/` or `check.py` file was touched.
