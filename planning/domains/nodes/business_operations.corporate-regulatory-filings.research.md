# business_operations.corporate-regulatory-filings — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the retired gist draft. The gist draft's facts and JSON key set
were correct and are preserved; what it lacked was the node test argued leg by leg, the rejected
files, a two-way collision fixture, reciprocal boundaries against neighbours that have since landed,
and the `government` seam. Those are the additions. Nothing here is padding; where this row has less
to say than a launch row, it says so.

**Verdict: the row STANDS.** The gist draft's verdict is upheld, not reversed — but only after all
three charges in the dispatch were taken seriously enough that a refusal was a live outcome for most
of this pass. The argument for standing is narrower than the gist draft's, and the narrowing is the
most important thing in this memo: **this row is not "filings". It is the submission apparatus.**

---

## Sources actually used

### Binding
- `planning/00-database-agent-product-design.md` — every quotation below machine-verified with
  `grep -F` against this file before writing. Where a quote carries a typographic apostrophe it is
  reproduced with one.
- `planning/domains/_CONTRACT.md` (rules 6, 10, 11, 15), `planning/domains/CONNECTION.md` §2 (node
  test), §4 step 2 (never-alone), §5 invariants, §9 failure mode 6.
- `planning/domains/canonical_fields.json` — no key minted here; two seconded.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D4, J-IND taken as ratified.
  D4 shaped this row more than any other.
- `ROSTER.md` §4 + Appendix A line 542: legacy `corp.regulatory-filings` (ROW) is absorbed here.

### The schema anchor, read first
`business_operations.research.md` (deepened). Two things in it bind this row directly:

1. **The default template every sibling must differ from** — *the organisational unit or entity only
   where the corpus genuinely spans more than one → the governance body, project, contract, or
   account → the fiscal period → the document function. Not time-first.*
2. **The never-alone principle generalised for all 24 siblings**: *"No sibling may rest its
   activation on an entity name, a business vocabulary word, or a document shape alone. Each of the
   three is never-alone here. Every detection signal a sibling writes must pair a structure with a
   labelled slot."*

Leg 2 and the whole of §"Charge (c)" below are answered against that pair.

### Neighbours read, not edited
- `business_operations.organisational-records.json` + memo — **the family's refusal, read first and
  on the assumption this row might be next.** Its NJ-BO-4 names this row explicitly.
- `business_operations.board-governance.research.md` (deepened) — it wrote this seam from its side.
- `business_operations.compliance-audit.research.md` (deepened) — adjacent; seam stated below.
- Landed launch rows: `finance.tax-filings`, `finance.small-business-bookkeeping`,
  `finance.cap-table-equity`, `finance.json`, `legal.json`, `legal.leases-agreements`,
  `legal.personal-legal-matters`, `legal.practice-matter-file`.
- `construction_property.building-control.research.md` — the only file in the catalogue that has
  already written the `government` seam. This row adopts it and does not extend it.

---

## What it is for, and what it holds

Documents an entity — or a person acting for one — is **required** to submit to an authority or
registry, and the authority's responses. Annual confirmations and returns, registry change
notifications, beneficial-ownership statements, sector returns, submission receipts,
acknowledgements, registry certificates and searches, reminder and penalty notices, filing calendars,
and agent authorisations.

The anchor is an **obligation to an authority** with a deadline and a filing reference: a document
whose existence is compelled from outside. `board-governance` states the same discriminator from its
side more sharply than this row originally did, and it is adopted here: a resolution's existence is
compelled from **inside**, by the body's own constitution.

---

## The node test, all three legs, argued

The test is CONNECTION §2 as the schema anchor restates it: a template row exists only where its
**detection signals**, its **recommended dimensions**, or its **privacy rules** differ from its
schema's default template.

### Leg 1 — detection signals. **Passes, and this is the leg the row survives on.**

The anchor requires a **structure paired with a labelled slot**. This row can name four such pairs
that no sibling can, and they are not vocabulary:

- **Submission receipt.** A machine-issued acknowledgement carrying a submission reference, a
  received timestamp, a return name and the submitting entity's identifier. No other row in this
  family has a counterparty that generates documents back at you on a schedule.
- **Registry certificate.** A seal or crest, a registered number, an effective date. The issuer is
  not the holder — the only sibling material with that property.
- **Compelled notice.** A case reference, a statutory deadline, and a **consequence statement**.
  The consequence statement is the discriminating element; a chase email from a supplier has a
  deadline and no statutory consequence.
- **Statutory-form structure.** A labelled entity-identifier slot **and** a labelled period-or-as-at
  slot **and** a declaration block, together. Any one of the three alone is never-alone.

Each is a structure with labelled slots, which is exactly what the anchor demands and exactly what
`organisational-records` could not produce. The row also inherits the family's table sentence
honestly — *"Tables matter because resumes, forms, applications, invoices, and administrative
documents often place their most useful information in cells rather than body paragraphs."*

**The narrowing.** These four are all **submission apparatus**, not subject matter. That is why the
row survives and it is also the boundary of what it may claim: a document about a company's
obligations, without apparatus, is not this row's. `AA01 blank.pdf` (new fixture) is the proof — a
statutory form with an entity name and a form number and nothing else does not fire.

### Leg 2 — recommended dimensions. **Differs, and the difference is real but held as prose.**

`template.dimension_order` is `[]` by binding contract (PR-6): a dimension may only branch on a field
the same entry's schema declares, and `business_operations` declares none. The recommendation is
prose, and it differs from the anchor's default paragraph in two places:

- **The entity level is unconditional here, where the anchor makes it conditional.** The anchor
  seeds `organization` ineligible because in a single-entity corpus it is *"a collection point for
  everything produced by the same person or organization"* and the validator forbids templates that
  *"use an author or organization merely as a collector"*. This row is the situation where the
  condition genuinely fails: a filing has an obligated entity **by definition**, and one person
  filing for two entities is the ordinary shape rather than an edge case. Marked as a divergence
  from the family default, not smuggled.
- **The second level is the authority or return type, not a governance body, project, contract or
  account.** None of the anchor's four apply — a return belongs to an obligation, not to a project.

Then the period, then the document function (return / receipt / certificate / notice). **Still not
time-first**, and this row refuses the exception more explicitly than any sibling needs to, because
it is the most period-dense row in the family and therefore most tempted: *"For document and record
domains, project, function, or subject usually comes before time because putting year first scatters
related work across calendar folders."* One filing occurrence — return, receipt, acknowledgement —
carries one year on every member and is still scattered by a year-first tree. The anchor's ruling
that no sibling here may claim `time_first: true` is accepted without exception.

And whatever eventually lands stays a recommendation: *"The system recommends an order based on the
domain template, but the user can reverse, remove, add, or flatten dimensions."*

### Leg 3 — privacy rules. **Differs, on a specific and unusual ground.**

The family's default posture is commercial confidentiality. This row differs because its forms carry
**identifiable individuals' dates of birth, residential or service addresses and personal
references** as their *purpose* — an officer appointment and a beneficial-ownership statement exist
to record exactly that. `00` names the class in its corpus sentence and requires the immediate
transition: *"A scanned passport, tax statement, medical document, authentication key, or account
record should enter a protected state immediately."*

The unusual part, and the one that would be got wrong by default: **a registry publishing some of
this does not make the holder's own copy safe to expose.** The holder's copy sits beside drafts,
workings and correspondence that were never published, and the download that produced it was a
bounded session — *"A session should never be treated as proof of topic"*. Marked as inference; `00`
does not discuss registry publication. `sensitivity` is `potentially_sensitive`; the handling class
is P7's and is not set here.

**All three legs pass. One would have sufficed.**

---

## The three charges in the dispatch, answered

### (a) "It is a document type" — the charge that refused `construction_property.compliance-certificate`

**Taken seriously; it does not land, and the reason is worth stating precisely.** "Filing" is indeed
a document-function word, and a row whose whole claim is *these are the filings* would be a value of
a function dimension wearing a row's clothes — the anchor's own warning that *"procurement",
"facilities", "risk" and "IT asset" are values of a function dimension*.

What saves this row is that it is **not defined by the document's shape but by a relationship**:
compelled submission to an external authority. That relationship is evidenced by apparatus that
exists nowhere else — a counterparty who issues receipts, seals, and consequence statements. A
document type would have to be recognised by looking at one document; this row is recognised by the
**round trip**. That is a structural difference, not a topical one.

The honest cost: where the round trip is absent from the corpus — a lone filed return, no receipt,
no notice — this row is much weaker than it looks, and the correct outcome is often abstention or
`Independent Records`. Stated rather than smoothed.

### (b) "It is `finance`'s material, or `legal`'s"

**Partly lands, and the row is narrowed rather than defended.**

- **`finance` (statutory accounts).** Corporate accounting was deliberately folded onto `finance` in
  triage, and `finance.small-business-bookkeeping` is a landed launch row whose subject is *"Working
  books for a person's own small operation: journals and ledgers … financial statements"*. A set of
  filed statutory accounts is both. **The concession:** the accounts are bookkeeping's *output* and
  this row's *attachment*. This row claims the **filing wrapper** — the registry stamp, the
  submission reference, the acknowledgement — and does not claim the accounts as accounts. `finance`
  is a safety schema and its protective ordering runs first where both fire. New fixture and new
  edge; NJ-J-IND-3 carries the residue.
- **`legal` (constitutional documents).** Here the dispatch's premise turned out to be **weaker than
  stated, and that is a finding.** `legal.json` declares no field rows and its landed rows are
  person-side and practice-side — `leases-agreements`, `personal-legal-matters`,
  `practice-matter-file`, `estate-planning`. **None of them names a corporate constitution.** The
  seam is therefore asserted into a gap rather than against a written claim, and this row states it
  conservatively: an adopted constitution with an execution block and no submission apparatus reads
  as `legal`'s executed instrument; the same document with a registry stamp or accompanied by a
  change-of-articles form is this row's. New fixture (`Articles of association - adopted 2019.pdf`)
  and new edge, both marked inference.

### (c) The never-alone failure — an organisation name plus a form number

**This is the charge that nearly refused the row, and it is answered with a fixture rather than an
argument.** The anchor's principle is that a row resting on an entity name, a business vocabulary
word, or a document shape alone *can never clear activation*. An entity name plus a form number is
exactly that pair.

The row's answer is that the pair is **explicitly refused in its own recognition block** — the
`never_alone` list already struck an authority gazetteer hit alone, regulatory vocabulary alone, a
reference-shaped token alone, a period-shaped token alone, and a company gazetteer hit alone — and
that it now carries `AA01 blank.pdf` as a fixture whose whole point is that this row **must not
fire** on it. A row that can name its own worst case and decline it has cleared the principle;
`organisational-records` could not, because the pair was all it had.

---

## Files considered and rejected

The tempting false positives, and what discriminates each.

| File | Why it is **not** this row's evidence |
|---|---|
| `Companies House filing guidance.pdf` **(the collision fixture)** | An authority letterhead, dense filing vocabulary, and **no entity identifier, no period, no submission reference**. It is the authority's published guidance — reading material about the obligation, not the obligation. *"purpose answers what the file was for"*. **Reading Inbox.** |
| `Planning application - 26-00412-FUL.pdf` | Obligation versus **request**. An application seeks a permission. Same bytes `construction_property.building-control` names; both rows reject them for the same reason, and the edge now says so. |
| `AA01 blank.pdf` **(new)** | The never-alone pair with nothing attached. Entity name from a template header, form number in the footer, every value slot empty. **Review Later.** |
| `Articles of association - adopted 2019.pdf` **(new)** | An executed instrument with no submission apparatus. `legal`, and safety ordering first. |
| `Annual accounts YE 31-12-2025 - filed copy.pdf` **(new)** | Genuinely both. Claimed only for its filing wrapper; `also_schema: finance`. |
| A **personal self-assessment return** | The person's own record. `finance.tax-filings`, a safety row whose `one_line` puts *the return copy as filed* on its own side. Keeping it here would quietly annex safety-domain material. |
| An **accountancy firm's newsletter** on filing deadline changes | Maximum vocabulary density, zero apparatus. **Reading Inbox.** |
| A **filing agent's engagement letter** held by the agent, with a matter reference and a time-recording anchor | `law_practice`. Side, not subject — the anchor's rule. |
| `CT600-2025-2026.xml` | Kept as the **format** fixture: the `.xml` extension fires nothing. *"treat the file extension as a routing signal rather than an assumption about meaning"*. The root element and the labelled period elements fire. |
| `Screenshot 2026-01-12 at 16.31.07.png` of a portal confirmation | Evidence a page was seen, not that a return exists. **Temporary Screenshots.** |
| `filings-2026.zip` | *"the normal scan should never extract archive contents to the filesystem"*, and this is the archive most likely to span two entities. |
| A **supplier's invoice** carrying a tax registration number | A registration number is a never-alone token; an invoice is a transaction. **Receipts and Confirmations.** |
| A **job description** naming a regulator as the employer | `career`. An authority name is the multi-role token, which is the whole reason for the never-alone rule. |

---

## The collision fixture, in both directions

**`Companies House filing guidance.pdf` versus `Confirmation statement - filed 12 Jan 2026.pdf`.**

Both are PDFs. Both carry the same registry's crest and letterhead. Both are dense in *confirmation
statement*, *registered office*, *due date*, *late filing penalty*. A vocabulary detector cannot tell
them apart, and a gazetteer hit on the authority fires identically on both.

- **The file that would wrongly fire this row:** the guidance. What discriminates it is the **absence
  of all three slots at once** — no entity identifier, no period or as-at date, no submission
  reference. Guidance is written to be true for everybody, which is precisely why it names nobody.
- **The file that must not be lost *to* this row:** the guidance again, in the other direction — if
  this row takes it, a genuine Reading Inbox item is buried inside an entity's filing history where
  the user will never look for it. And symmetrically, the **filed statutory accounts** are the file
  that must not be lost *to* `finance`: strip the filing wrapper and the submission trail
  disappears. Both neighbours name those same bytes now.

---

## Reciprocal boundaries, both directions

### `business_operations.board-governance` — **reciprocated this pass**
That row authored the edge toward this one; this row did not name it. Fixed. **In this direction:** a
registry form, a submission reference, a statutory deadline, or an authority's acknowledgement. **In
the other:** a body's own signed resolution with a circulation block and no submission apparatus.
Its formulation — compelled from *outside* versus compelled from *inside* — is adopted as the
cleanest statement of the seam. Appoint a director, minute it, file the form, keep the receipt: both
rows are right about their half, and *"A file may validly belong to more than one accepted group"*
settles it later.

### `business_operations.compliance-audit`
That row already names this one, in words this row does not contradict. **This direction:** a
submission to a named authority with a filing reference and an acknowledgement. **The other:** a
control, a finding, a corrective action with an owner and a due date, or an assessor's report
structure. Both authors note the same hazard: a single regulator's pack routinely carries both, and
neither row may take it whole.

### `finance.tax-filings` and `finance.small-business-bookkeeping`
Authored one-way from this side; neither landed row names `business_operations`. **This direction:**
the filing wrapper — registry or revenue letterhead, submission reference, statutory deadline,
acknowledgement. **The other:** the return as the person's own custodial record, the payer-issued
year-end forms, the ledgers and reconciliations behind the accounts. Both are safety rows and their
protective ordering runs first. NJ-J-IND-3 is live on exactly these bytes.

### `finance.cap-table-equity`
Share allotments, transfers and capital reductions are simultaneously registry filings and cap-table
events. **This direction:** the statutory form and its receipt. **The other:** the share register,
the shareholder agreement, the option-grant record. That landed row does not name this one.

### `legal.leases-agreements` (and `legal` generally)
Stated above under charge (b). Asserted into a gap, marked inference, conservative on purpose.

### `construction_property.building-control`
Same bytes, same rejection, consistent reasoning. Edge authored so the two families do not diverge.

### `government.*` — where `business_operations` stops
`government` is an unwritten schema. `construction_property.building-control` has already written
this seam and **this row adopts it without extending it**, so the family does not diverge:

| Evidence present | Side |
|---|---|
| the **submitted** return with the holder's own declaration; a fee the holder paid | **this row** |
| an acknowledgement or validation letter **addressed to the holder**; a decision or notice **received** | **this row** |
| an **issuing** letterhead and signature block the holder controls; a **case file** rather than a case | **`government.public-authority-record`** |
| statutory **power** exercised — an enforcement notice **issued**, a register entry, a scheme of delegation | **`government.public-authority-record`** |
| an instrument licensing an **activity or a permission sought** rather than a periodic compelled return | **`government.permit-licensing`** |
| role does not settle | **neither activates** — *"Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement."* |

**The thing the `government` author most needs to know, and it is `building-control`'s sentence, not
this row's invention:** *the filing reference is on both copies and discriminates nothing.* It is the
strongest-looking token in this world and it is worthless as a side discriminator. Both edges are
one-way; **R1c owes the `government` reciprocals.**

---

## Neighbours considered that did **not** get an edge

- **`identity.core-documents`** — a certificate of incorporation is the entity's identity document
  and the parallel is real. Not edged: `identity` is a safety schema whose subject is a *person*, and
  asserting the pair would blur that. Noted for R1c.
- **`government.statistical-programme`, `government.public-records-foi`** — authority-side rows with
  returns of their own; the which-side discriminator is already carried by the
  `government.public-authority-record` edge and tripling it adds nothing.
- **`logistics.customs-export`** — customs declarations are compelled returns with references and
  deadlines, and this is the closest unedged neighbour in the catalogue. Left unedged because the
  row has not landed and a shipment/consignment anchor plainly discriminates it; flagged for R1c.
- **`hr`** (a dispatch `must_consider` neighbour) — employer-side statutory returns about employees
  exist, but the moment a document identifies individuals as employees it is `hr`'s, and the never-
  alone discipline here is stricter than an edge would express.
- **`career`** (a dispatch `must_consider` neighbour) — a person's own professional registration
  renewal is the individual's record, not an entity's obligation. Side, again.

---

## `proposed_fields` — two, both **secondings**, no mints

- **`organization`** — seconded from the schema row. This row is the family's **strongest** case,
  because the schema row's own conditional wording (*only where the corpus genuinely spans more than
  one*) is routinely satisfied here: a filing has an obligated entity by definition. R1c should weigh
  this vote above the family average, and should note that refusing the key leaves this row with
  nothing that separates two entities' returns.
- **`fiscal_period`** — seconded **with a warning that differs from `compliance-audit`'s**. The
  periods here are not one object: an accounts period, a VAT quarter, a confirmation-statement
  *as-at instant* and a registry event date are four different things, and only the first two are
  fiscal periods at all. This row will abstain from writing the key more often than the other three
  claimants, and that is correct rather than a gap. It will never write `tax_year` on a registry
  period, which its own `must_not_conclude` already refuses.

Nothing minted. The family's `organization` decision is one decision across two schemas
(`business_operations` and `construction_property`) and R1c should settle it once.

---

## NEEDS-JOSEPH

- **NJ-J-IND-3 (carried, in its most literal form).** A corporate tax return, and equally a set of
  filed statutory accounts, is simultaneously this row's compelled filing and the finance safety
  schema's custodial record. **Alternatives and costs:** (i) *finance takes the bytes whole* — safe,
  but the submission trail (receipt, acknowledgement, penalty notice) has no home and scatters to
  Independent Records; (ii) *this row takes them whole* — coherent filing history, but a
  business_operations row annexes safety-schema material, which is the thing the safety split exists
  to prevent; (iii) *co-activation with safety ordering first, which is what this row implements* —
  correct but leaves P10 to choose placement on the commonest document in the pile. This row cannot
  settle it.
- **NJ-BO-10 · Gazetteer coverage gates this row.** Under D4 the row names no authorities, so it
  fires only as far as R4/R5 reach. **Cost of each branch:** if v1 ships one jurisdiction's
  gazetteers, this row is effectively one-jurisdiction at launch — which is a defensible scope
  decision but should be a *stated consequence* rather than a surprise discovered in testing. The
  alternative, letting the row carry its own authority names, is refused outright: D4 is ratified.
- **NJ-BO-4 · answered from this side, not left open.** `organisational-records` asks whether a home
  was meant for the corporate identity documents of an entity a person owns or administers. This
  row's position: the pile splits **by evidence**, correctly, three ways — registry-issued and filed
  documents here, unfiled executed constitutions to `legal`, share registers to
  `finance.cap-table-equity` — and no fourth row is needed. If R1c mints the narrow row anyway, this
  row yields the registry certificates to it and keeps the returns and receipts. Stated so R1c has a
  reciprocal answer rather than an open question.
- **NJ-BO-NEW · the `government` reciprocals are unwritten.** Both `government.*` edges here, and
  `building-control`'s two, are authored one-way into a schema that does not exist. R1c should route
  this as a family-level obligation rather than let each row re-derive the seam.

---

## What changed in this pass

Verified against the JSON as written, not against intention.

**Preserved unchanged** (the gist draft was right and is not rewritten): the `one_line`'s
obligation-to-an-authority anchor, all nine `recognition.deterministic` signals, all seven
`needs_llm` entries, all nine `never_alone` entries, the 30 `proposed_context_terms`, the 13
`work_types`, the six `grouping_reasons`, the prose `template.why` recommendation with
`time_first: false`, `file_kinds`, all six `falls_through_to` residuals, `sensitivity` and its
two-ground `sensitivity_why`, and all ten original `file_examples` including the four fixtures the
draft chose well (`Companies House filing guidance.pdf`, `Planning application - 26-00412-FUL.pdf`,
`CT600-2025-2026.xml`, `AP01 - appointment of director.pdf`).

**Added to the JSON:**
- `proposed_fields`: **0 → 2** — `organization` and `fiscal_period`, both explicitly seconding the
  schema row, each with its own argument, neither a variant.
- `collides_with`: **9 → 13** — `business_operations.board-governance` (reciprocating an edge that
  row had already authored toward this one), `finance.small-business-bookkeeping` (the statutory-
  accounts bytes), `construction_property.building-control` (same rejected bytes, consistent
  reasoning), `legal.leases-agreements` (the constitutional-document seam).
- `file_examples`: **10 → 13** — `Annual accounts YE 31-12-2025 - filed copy.pdf` (`also_schema:
  finance`), `Articles of association - adopted 2019.pdf` (`also_schema: legal`), and `AA01
  blank.pdf`, the never-alone fixture the row must **not** fire on.
- `open_question`: **2 → 4** — adds the NJ-BO-4 answer and the `government` custody-and-role seam.
- `one_line`: the phrase "Gist-level placeholder (J-IND)" replaced with the J-DEPTH statement. The
  substance of the sentence is unchanged.

**Added to this memo:** the node test argued leg by leg with the two divergences from the family
default named; the three dispatch charges answered individually, with charge (b) producing a real
narrowing and charge (c) producing a fixture; thirteen rejected files; the collision fixture in both
directions; reciprocal boundaries for eight neighbours plus five deliberately unedged; the
`government` role table adopted from `building-control`; NJ items with alternatives and costs.

**Reversed:** nothing. The gist verdict `refuse_node: false` stands and is now argued rather than
asserted. What *is* a substantive change of position is the **scope**: the row's claim is the
submission apparatus, not the subject matter, and under that reading it concedes the accounts to
`finance` and the unfiled constitution to `legal` — territory the gist draft's `one_line` (statutory
account submission is still listed as a `work_type`) implicitly held more of.

**Not done, and why:** no neighbour file was edited. The `board-governance` reciprocity gap it
recorded is closed **from this side only**; the `finance`, `legal` and `construction_property` edges
are one-way because those are landed launch rows this pass may not touch. R1c owes the other halves.

---

## Audits run before returning

- `python3 -m json.tool` on the JSON: parses.
- Top-level key set and `file_examples` key set diffed against
  `business_operations.board-governance.json`: **identical, no missing or extra keys.**
- Every quotation in this memo `grep -F`'d against
  `planning/00-database-agent-product-design.md` before writing; all found verbatim. The
  `Correct abstention…` sentence was corrected to the source's typographic apostrophe after a first
  check failed on the straight one.
- `launch: "placeholder"`, `fields: []`, `refuse_node: false`, `design_cite: null`,
  `provenance: "proposal"`, `template.dimension_order: []`, `time_first: false` — all confirmed
  unchanged in the written file.
- The "what changed" counts above were re-read out of the written JSON (13 collisions, 13 examples,
  2 proposed fields), not from intention.
- Files written: this memo and
  `planning/domains/nodes/business_operations.corporate-regulatory-filings.json`. Nothing else.
