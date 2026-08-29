# `construction_property.construction-project` — lab notes (R1b, deepened to J-DEPTH)

Row kind: **template**. Schema: `construction_property`. Launch: **placeholder** (`fields: []`).
Absorbs the legacy row `cons.project`. Verdict: **kept, not refused — but on a materially narrower
basis than the gist pass claimed.**

**Status of this pass.** The row existed at the retired gist depth: a 25KB JSON whose key set was
house-correct and whose quotations were machine-verified, and a 3.3KB memo. The JSON was **verified
and extended, not discarded.** The memo is replaced. One substantive reversal was made and it is
declared in full below rather than performed silently: *five of the row's eight structural detection
signals have been demoted out of its activation evidence and conceded to the sibling rows that own
them.* See **The reversal**, and **What was preserved, what was added** at the end.

This is the family's **branch root**, and the dispatch is right that several siblings were argued by
reference to it. That is exactly why the reversal matters: a branch root that keeps its siblings'
evidence is not a root, it is a sink.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted, and every quotation in
  the JSON was re-verified verbatim this pass with `grep -c -F` (29 quoted spans, each returning
  exactly one match). The spans doing real work here:
  - the purpose-coherence sentence, which is *the* justification for a container row: *"The documents
    are content-incoherent but purpose-coherent."* A job file is a contract, a Gantt chart, a
    photograph, a spreadsheet and a signed certificate. Nothing joins them except the instruction.
  - the sparse-file rule: *"The graph does not automatically copy those missing facts onto sparse
    files."* This row is the single most dangerous place on the roster for that rule, because a job
    folder is a standing invitation to stamp a job reference onto every file inside it.
  - the dimension-order rule: *"For document and record domains, project, function, or subject
    usually comes before time because putting year first scatters related work across calendar
    folders."*
  - the template-validator prohibition that decides this row's tree order against the family default:
    *"create meaningless one-child levels"*, and *"use an author or organization merely as a
    collector"*.
  - the abstention sentence, which this row needs more than most: *"Correct abstention is a
    successful outcome because the product's goal is reliable organization, not maximum file
    movement."*
  - the never-alone reasoning the whole family inherits: *"A university name alone should not create
    a group because Columbia can appear as an authoring school, course provider, target institution,
    employer, research venue, or merely a cited organization."*
  - the multi-domain sentence, for the `also_holds_with` set: *"One file may hold facts from more
    than one domain without losing information."*
  - the safety-domain sentence, which orders the `legal` co-activation: *"Finance, identity, medical,
    and legal material should be implemented first as safety domains"*.
  - the residual definitions for all six `falls_through_to` entries.
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance, no fabricated quotes, no invented
  numbers), 8, 10 (no field rows on a placeholder schema), 11–15 (closed edge vocabulary).
- `planning/domains/CONNECTION.md` — §2 node test (applied leg by leg below), §3 **activation ≠
  grouping and the browse-only parent**, which is the section this pass leans on hardest, §4
  activation ordering, §5 closed edge vocabulary, §9 failure modes, PR-6.
- `planning/prompts/ALIGNMENT.md` — *"would only repeat its schema's fields and dimension_order"* …
  *"it is the schema's default template."*
- `planning/domains/canonical_fields.json` — confirmed `work_type`, `client`, `our_firm`, `project`,
  `location`, `event`, `capture_year` exist, and that **nothing holds the property**. **No key
  minted here.**
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D6, PR-6, J-IND taken as
  ratified. J-DEPTH (2026-08-24) overrules J-IND's gist clause and is why this memo exists.
- `planning/domains/ROSTER.md` §4 + Appendix A, `roster.json` — confirmed `cons.project` is the
  absorbed legacy id, and enumerated the **27 sibling templates** on this schema.

### Neighbours read in full before writing, and not rewritten

- **`construction_property.research.md` (the deepened schema anchor, 43KB)** — the measuring stick.
  Its default-template paragraph is what this row must differ from, and it **pre-licenses this row's
  reversal by name**: *"A row whose entire life is one job at one address — `construction_property.trade-job`,
  `construction_property.construction-project` — may honestly put the instruction first."* It also
  warns, in the same breath, that **the reversal alone earns nothing**. That warning is what forced
  this pass to find the row's own evidence rather than resting on the tree order the gist memo led
  with.
- **`construction_property.progress-photos`** (JSON + memo) — the family's best argument, and it
  defines itself against this row. Read in full; **its argument is accepted here unchanged** rather
  than contested. See the section on it below.
- **`construction_property.timesheet.json`** and **`construction_property.compliance-certificate.json`**
  — the family's two refusals. Both route coverage partly toward this row and both are quoted below,
  because a branch root that accepts routed coverage must show that the coverage lands somewhere real.
- **`finance.household-property`** and **`legal.leases-agreements`** — the landed launch rows at full
  depth. The professional-versus-householder seam is drawn on the schema row and is **applied**, not
  re-drawn, here; `Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf` is now carried as a fixture
  on this row too, with the landed row's reading reproduced unchanged.
- **All ten sibling rows this row competes with** — `final-account`, `variation-claim`, `site-diary`,
  `snagging-defects`, `subcontract`, `drawings-revisions`, `quote-estimate`, `trade-job`,
  `block-management`, `development-appraisal`. Five of them already name `construction-project` in
  their own `collides_with`, in their own words. **Those five sentences were read first and are
  adopted verbatim in substance**, which is what produced the reversal.

### A source that does not exist, and it matters

`00` **never names this world.** Its template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections"* — construction is absent. So `design_cite` is `null`, `provenance` is `proposal`, and
every `collides_with` entry is `provenance: inference`. `00` supplies the machinery; this row
supplies the situation. No quotation in this memo is offered as design authority for the situation
itself.

---

## The reversal, stated plainly

**The gist pass gave this row eight structural detection signals. Five of them belong to siblings,
and this pass concedes all five.**

The gist memo's node-test argument was: *"Two structures exist nowhere else on the roster: the
contract-sum-with-date-for-possession particulars block, and the
valuation-against-works-executed-less-previously-certified payment cycle … The completion / defects /
making-good triple is a third."*

The first of those three is right and survives. The second and third are **wrong at row level** —
not factually (the structures are real and are peculiar to construction) but **jurisdictionally**.
`construction_property.final-account` exists and owns the payment cycle; it says so itself:

> *the payment cycle apparatus — applications, notices, certificates, retention — supports this row;
> award documents, programmes, instructions, correspondence and the general project record support
> the project row.*

`construction_property.snagging-defects` exists and owns the defects tracker, and it recorded the
collision **deliberately** because its own node test asked whether it was merely a `work_type` of
this row:

> *a defects-liability period, a re-issue sequence with a status column, and activity AFTER practical
> completion support this row; anything inside the construction period supports the project row.*

Similarly `variation-claim` owns the numbered instruction, `site-diary` owns the dated daily record,
and `subcontract` owns the works package. The gist row claimed all of them.

**Why this is not a technicality.** If the branch root activates on the same bytes as its ten
children, then every file in the family fires two rows, the mutex resolves arbitrarily, and the
family's careful per-row arguments become decorative. CONNECTION.md §3 already forbids the mechanism
that would make this feel harmless — the parent is **browse-only**, and *activation ≠ grouping*.
A job file's members belong to the job in the **browse** sense while the row that owns each member
**activates**. That distinction is now written into `grouping_reasons`, into `never_alone`, and into
the `must_not_conclude` list of every affected fixture, so it is checkable file-by-file.

**What that leaves, and whether it is enough** is the node test, next.

---

## The node test, all three legs, argued

CONNECTION.md §2: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. Any one leg
suffices. This row is examined on all three, and it is examined *after* the demotions, which is the
only honest order.

### Leg 1 — detection signals of its own

The question after the reversal is sharp: **does anything activate this row that does not activate a
sibling?** Four structures do.

1. **The award sequence.** An invitation to tender, a tender report, a letter of intent, and a
   letter of acceptance naming an accepted sum and a described scope. This is the only structure in
   the family that **constitutes** the job rather than reporting on it. `quote-estimate` explicitly
   stops at this moment — its own anchor is *"a PROSPECT - an address and an enquiry"* which *"may
   go quiet"* — so acceptance is an unclaimed boundary and this row is on the far side of it.
2. **The contract-particulars block.** Employer and contractor in party slots, a described works
   scope at a described site, a contract sum, **and a date for possession paired with a date for
   completion.** The pair is the discriminator: a professional appointment carries a fee, a supply
   agreement carries a price, a subcontract order carries a package — none of them carries
   possession-and-completion for the whole of the works. This is the gist pass's one surviving
   original claim and it survives intact.
3. **The programme.** A baseline-against-actual comparison issued under a contract reference and a
   revision. `site-diary` holds the day; `final-account` holds the money; nobody holds the plan.
   `business_operations.project-delivery` holds the **generic** Gantt, which is why a Gantt shape
   alone is on the never-alone list.
4. **The completion-and-handover envelope.** A practical or sectional completion certificate, and
   the handover / O&M / building-manual pack whose manifest names as-builts, commissioning results,
   warranties and a health-and-safety file. The **members** of that pack are siblings' documents.
   The **assembly** — a container-of-containers pinned to one contract at one site — is claimed by
   no sibling, and it is the artefact a practitioner actually reaches for years later.

Verdict on leg 1: **passes, narrowly, on four structures rather than the eight the gist claimed.**
It would have failed on the demoted five, and saying so is the point of this pass.

### Leg 2 — recommended dimensions

Available only as prose, since the schema declares no fields (`_CONTRACT` rules 10 and 15, PR-6), and
`dimension_order` is therefore `[]` **by contract, not by judgement**.

The family default, from the anchor: **`property` or site → `instruction` → document function.**
This row **reverses the first two levels**: **job first, then function.** The reason is the
one-child rule — a construction contract's whole life is one instruction at one site, so a property
level above it would produce exactly the *"meaningless one-child levels"* the template validator
rejects, and would be the schema's other prohibition too, *"use an author or organization merely as
a collector"*, with the address doing the collecting.

**And leg 2 is nonetheless disclaimed as a basis for the node.** The anchor is explicit that
*"Reversing is not a difference that earns a node"*. The gist memo led with the reversal, which read
as though it were doing work. It is not. It is recorded because a sibling author needs to know this
row's tree order, not because it justifies the row's existence.

One further consequence, now that leg 1 has narrowed: **the function level of this row's tree is
where a sibling's activated file is browsed**, not where this row extends its reach. `Valuation 07`
lives under the job in the tree and belongs to `final-account` in the graph. That sentence is now in
`template.why`.

Verdict on leg 2: **the order differs from the default, and the difference is deliberate — but it
is offered as information, not as a passing leg.**

### Leg 3 — privacy rules

Also **not** a passing leg, and the gist memo never tested it. Three grounds are stated in
`sensitivity_why` — the material names the people on site and in the building, it carries a third
party's confidential prices and margins, and it routinely contains photographs of the inside of
somebody's property — and `00`'s corpus sentence covers what a job file accumulates: the corpus
*"can include identity documents, account statements, tax records, medical information, legal
records, credentials, private correspondence, GPS metadata, employment materials, and educational
records"*.

**But every one of those grounds is the schema's, not this row's.** The schema row already sets
`potentially_sensitive` on the same three grounds for all 27 siblings. This row is not stricter than
its schema; `site-health-safety` is (the `timesheet` refusal notes it operates *"under a stricter
privacy posture than this schema's default"*), and this row is not that row. No P7 handling class is
assigned here; that is P7's.

Verdict on leg 3: **identical to the schema default. Fails as a distinguishing leg, and is recorded
as failing.**

### Overall

**Kept, on leg 1 alone.** One leg is all §2 requires, and pretending two or three passed would be
the kind of unsourced confidence the brief forbids. If R1c judges the four surviving structures too
thin, the honest alternative is spelled out in the JSON's `open_question` and in NJ-CP-11 below.

---

## Why the row is still called the branch root, if it owns so little

Because *branch root* is a claim about **browse structure**, not about evidence. Every other
construction-side row on this schema is unintelligible without a job around it: a drawing revision,
an instruction number, a valuation number, a diary date and a snagging item are all **positions
inside a job**. That is `00`'s own reason for putting a course above a homework number, applied to a
different world — and it is a **template dimension order**, never a `parent_id`, never schema
inheritance (CONNECTION §3).

The gist memo said exactly this and it was right; it is preserved. What this pass adds is the
corollary the gist memo missed: **being the parent dimension of a document is not evidence about
it.** The two claims sound similar and pull in opposite directions, and keeping them apart is the
whole discipline of a branch-root row.

---

## Files considered and rejected

The brief's own test: a row that only lists what it holds has not been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| `Valuation 07 - application for payment.xlsx` *(kept in the JSON, re-read as a sibling's)* | The payment cycle is `final-account`'s. The head-contract reference on the sheet corroborates the envelope; the `to date, less previously certified` arithmetic is the sibling's activation, not this row's. |
| `AI 014 - relocate soil stack.pdf` *(same)* | A numbered instruction is `variation-claim`'s. The gist row read the contract reference as its own evidence; that is the branch-root error in miniature. |
| `Site diary 2026-03-12.docx` *(same)* | `site-diary`'s. It also carries **no job reference at all** — the `HW 3` case in construction clothing, and neither row may invent one. |
| `Snagging schedule - Block C - rev 2.xlsx` *(same)* | `snagging-defects`', which argued precisely this against precisely this row. The boundary drawn on both sides is practical completion. |
| `Sub-contract order 2431-08 groundworks.pdf` *(same)* | `subcontract`'s, on the engaging side. The head-contract reference is what this row reads. |
| A signed dayworks sheet | Routed by the **`timesheet` refusal** to `variation-claim`, not here. The dispatch is right that the refusal routes coverage *partly* toward this row's lifecycle — but the refusal names `variation-claim` as the destination, and this row must not quietly collect it. That is the clearest live test of the reversal, and the reversal passes it. |
| A site attendance or induction register | Same refusal, routed to `site-health-safety` under a stricter privacy posture. Not this row's. |
| A CIS or subcontractor tax return; a site payroll run | `finance` and `hr`. Real in a builder's folder; finance and employment apparatus, not works apparatus. The gist memo said this and it stands. |
| A method statement or risk assessment | Genuinely this world, and `construction_property.site-health-safety` owns it. |
| Plant hire and materials delivery notes | `plant-hire` (asset + hire period) and `materials-delivery` (the delivery event). They appear here only as residual examples. |
| `Building Regulations Completion Certificate - 18 River Court.pdf` *(added this pass — the inbound collision fixture)* | See below. |
| `Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf` *(added this pass — the outbound collision fixture)* | See below. |
| A construction-management textbook chapter; a standard or guidance note | Reading Inbox — *"papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* Full vocabulary overlap, zero evidence. |
| A rendered exterior view of the same building | `creative.architectural-visualisation`. The schema row already carries this collision and repeating it at row level would add nothing. |
| A `.rvt` or `.dwg` with nothing readable in it | Not rejected as material — recorded as **indexed-but-unreadable**, which `00` treats as the correct condition rather than a failure. It is a `file_kinds` and residual matter, not a signal. |

---

## The collision fixture — both directions, as the addendum requires

**Inbound (a file that would wrongly fire this row):
`Building Regulations Completion Certificate - 18 River Court.pdf`.**

It satisfies an authority-decision structure, a property address in a labelled slot, and a
document-type word from this row's own `work_types` list, and it sits in a folder full of building
paperwork. It is still **a householder's own record of their own home**, which the landed
`finance.household-property` row claims and lists among its own work types.

**What discriminates it:** the **contract envelope is absent** — no contract reference, no parties
block, no contract sum, no possession-and-completion pair. What remains is *a document-type word
plus an address*, and **both halves are constitutionally never-alone on this schema**. This is
exactly the reduction on which `construction_property.compliance-certificate` was **refused**, and
this row must not accept through a fixture what the family refused as a row. Where the same
certificate sits inside a handover pack against a contract reference, this row fires and both
readings hold.

**Outbound (a file that must not be lost *to* this row):
`Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf`.**

It is the landed `finance.household-property` row's own fixture and this row reproduces its reading
unchanged: a tradesperson's invoice with a property address, **no job reference, no works
measurement**, and a service address that is the holder's own home. A householder's building
paperwork does not become a professional instruction because a professional produced it.

**The same bytes are named on both sides** — the certificate and the invoice run in opposite
directions across the same seam — which is what makes the reciprocal checkable rather than asserted.

A third fixture does the same work *inside* the family: `Programme rev F.pdf` — a Gantt with no
title block, no job reference and no site address, sitting in a folder named after a job number.
This row **does** own the programme situation, and it still may not write a job fact from the folder.
Owning a situation is not a licence to extract a fact the file does not carry.

---

## Reciprocal boundaries, both directions

Every entry below was read on the neighbour's side **first**. Where a neighbour had already stated
the line, its wording is adopted rather than re-authored, and no line is contradicted.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `construction_property.final-account` *(states its side already)* | applications, notices, certificates, retention, the reconciliation | award documents, programmes, correspondence, the general project record | `Valuation 07 - application for payment.xlsx`; `Final account - Kilnfield Phase 2 - agreed.pdf` |
| `construction_property.variation-claim` | numbered instructions, CVIs, EOT and loss-and-expense submissions, dispute bundles | the contract those instructions vary | `AI 014 - relocate soil stack.pdf` |
| `construction_property.site-diary` | the dated daily record — weather, labour, plant, events | the contract the diary is kept under, and the programme it is measured against | `Site diary 2026-03-12.docx` |
| `construction_property.snagging-defects` *(states its side already)* | defects-liability-period activity, re-issue sequences with status columns, anything after practical completion | anything inside the construction period, and the completion certificate itself | `Snagging schedule - Block C - rev 2.xlsx` |
| `construction_property.subcontract` | the enquiry, order, competence evidence and payment cycle of engaging another firm | the head contract those packages deliver | `Sub-contract order 2431-08 groundworks.pdf` |
| `construction_property.drawings-revisions` | drawing number + revision + status, and the transmittal register | the contract the drawings are issued under; and the **assembled** as-built set inside a handover pack | the as-built set — final assembly here, one controlled issue there |
| `construction_property.quote-estimate` | a priced return with no award, revised as scope moves | the letter of acceptance and everything after it | a priced schedule of works, which settles nothing on its own |
| `construction_property.trade-job` *(states its side already)* | a customer-and-address anchor, a single visit, a signature capture, a five-file corpus | an interim valuation, a certifying role, a programme, works packages, a retention regime | quote → photographs → certificate → invoice, which both produce identically |
| `construction_property.block-management` *(states its side already)* | consultation notices, observations, leaseholder apportionment, reserve-fund drawdown | the contract sum, instructions, valuations against measured works, the final account | one roof renewal, which produces both sets — per-evidence-item mutex |
| `construction_property.development-appraisal` *(states its side already)* | a forecast of a scheme that may never be built, from rates per unit area | works actually executed and certified, from measured quantities | a site address and a build-cost figure, which count for neither |
| `construction_property.progress-photos` | a site walk's captures, merely because a job exists around them | the photographic members of a handover pack, which arrive as an assembled deliverable | `IMG_2231.HEIC` |
| `business_operations.project-delivery` | a plan, a RAG status, a decision log, a change record, a closure document — the generic shapes | a fit-out or a scheme with a contract sum, measured works and a valuation cycle | a Gantt chart, which counts for neither |
| `business_operations.contract-administration` | an organisation's generic contract register entry | a construction contract's works apparatus | a signed agreement with a change log |
| `finance.household-property` *(landed)* | a householder's own record of their own home, with no instruction around it | a professional's instructed job file because the property is a house | the two collision fixtures above |
| `construction_property.commercial-lease` | licences to alter, schedules of condition, dilapidations — the lease's apparatus | valuations and instructions serving the building contract | one fit-out, which sits in both |

`finance.household-property` and `legal.leases-agreements` landed before this family and do not name
`construction_property` in their own memos. **R1c owes those two reciprocals**; the fixture bytes are
named here so the reciprocal can be checked rather than asserted.

---

## `progress-photos` — read, and agreed with rather than contested

The dispatch flags that this sibling defines itself against this row. It does, and its argument is
accepted here without amendment:

> Every other row on `construction_property` is recognised by **document structure**. `progress-photos`
> is recognised by **capture metadata, rhythm and place**. That is a different detection method, and
> *a `work_type` value cannot carry a different detection method; only a template can.*

That is decisive against the "it is just a `work_type` of `construction-project`" challenge, and this
row does not reopen it. Two consequences are recorded on this side:

- **This row must not reclaim site captures** because a job exists around them. `IMG_2231.HEIC` stays
  `group_without_copying_facts: true` here, with `photos` as `also_schema` — cluster membership
  proves a photo event and nothing more.
- **The one place the sibling must not follow** is the handover pack: its photographic members
  arrive as an assembled deliverable under a contract reference, not as a capture rhythm. That is a
  narrow carve-out and it is stated on this row so the sibling can check it.

The sibling's `NJ-CP-9` — *under the project, or beside it?* — is this row's question too, and it is
answered here only as far as the browse/activation distinction goes: photographs browse under the
job, `progress-photos` activates. Whether the *filesystem* puts them inside or beside is `00`'s
frozen-tree question and neither row can settle it.

---

## The two refusals, and what they route here

Both refusals name this row's lifecycle in their routing, and a branch root that accepts routed
coverage owes an account of where it lands.

- **`timesheet`** was refused partly because *"A SIGNED DAYWORK SHEET, countersigned by the client's
  agent, is contractual evidence that extra work was done at cost — its purpose is to be produced in
  support of a change, which is construction_property.variation-claim's situation."* The dayworks
  content belongs to **`variation-claim`**, which belongs to **this project's lifecycle**. Both halves
  of that sentence are true and they are not the same claim: the lifecycle is browse, the situation
  is activation. This row therefore takes **none** of the timesheet coverage directly.
- **`compliance-certificate`** was refused because its candidate signal reduces to *a document-type
  word plus an address*, both never-alone. Its coverage routes to Independent Records and to *"the
  situations that actually produce certificates"* — of which this row is one, for the **practical
  completion certificate** specifically, because that certificate is issued under a contract and by a
  named certifier rather than being a scheme declaration about an address. That is the one place
  refused coverage genuinely lands here, and the inbound collision fixture marks the line beyond
  which it does not.

---

## Sparse-file discipline

Eight of the fifteen fixtures carry `group_without_copying_facts: true`, and this row needs the rule
more than any other in the family because the job folder is the most persuasive false context on the
schema. A `.zip` handover pack whose members are never extracted, an `IMG_2231.HEIC` in a GPS
cluster, a title-block-less programme in a folder named after a job number, a diary entry with no
reference — in every one, the neighbourhood may legitimately group the file while **no** job fact is
written onto it. *"The graph does not automatically copy those missing facts onto sparse files."*

Every fixture also carries *"any construction_property fact — the schema declares none"* in its
`must_not_conclude`, so the placeholder status is checkable file-by-file.

---

## `proposed_fields`

**None. The row proposes no key of its own, and that is deliberate.**

It relies entirely on the schema row's two proposals — `property` (NJ-CP-1) and `instruction`, with
`project` reuse offered as the live alternative (NJ-CP-2) — and on `organization`, which the schema
row explicitly defers to `business_operations`. Minting a job key here while the schema row proposes
one for the whole family is the near-duplicate defect D6 exists to kill, and `00` is explicit: *"The
system may create new values when it sees a new course, project, company, university, or event, but
it should not invent new fields automatically."*

The gist row said exactly this and it was right. It is preserved unchanged.

`proposed_context_terms` (33 entries) is preserved unchanged too. These are **proposals**, not `00`'s
floor — `00`'s named context-term floor is the academic one, and this row does not pretend otherwise.

---

## Neighbours considered that did **not** get an edge

- **`government.planning-application`** — the job file contains condition-discharge correspondence,
  but the authority-decision structure belongs to `construction_property.building-control`, which
  states the government boundary from the applicant's side. Routing it twice would be duplicate
  authorship. *(Preserved from the gist memo; still right.)*
- **`hr`** — site inductions and competence cards name individuals, but the confusable document
  family is `site-health-safety`'s, and the `timesheet` refusal already routed it there under a
  stricter privacy posture. Contradicting that would invalidate a landed refusal.
- **`creative.architectural-visualisation`** — the schema row carries this collision; a row-level
  copy would add nothing.
- **`legal.practice-matter-file`** *(landed)* — a construction dispute becomes a solicitor's matter
  file, and the same adjudication bundle sits in both. No edge, because the bundle is
  `variation-claim`'s on this side, not this row's — the seam is between the sibling and the legal
  row, and authoring it here would be reaching across a boundary this pass just spent its argument
  drawing.
- **`engineering`, `logistics`, `manufacturing`** — the schema row draws all three seams (the site
  gate for goods, article-versus-installation for fabrication) and two of the three schemas are not
  yet written. Row-level duplication would risk contradicting a reciprocal that does not exist yet.
- **`career`, `academic`** — full vocabulary overlap, zero evidence overlap.

---

## Audits run before returning

- `python3 -m json.tool` on the node → **parses**.
- **Key set compared programmatically against `construction_property.final-account.json`** (a landed
  sibling) → **empty symmetric difference**.
- **Every quoted span in the JSON re-verified verbatim** against `00-database-agent-product-design.md`
  by exact substring match — **29 spans, zero failures**. Every quotation in this memo likewise
  grep-verified with `grep -c -F`, each returning exactly one match.
- **Every `file_examples.source_type` in `SOURCE_TYPES`** → clean (15 fixtures).
- **Every `falls_through_to` and `falls_through_if_inactive` is one of the nine residual names**,
  spelled `00`'s way → clean.
- **Every `collides_with` and `also_holds_with` target resolves in `roster.json`** → clean (15
  collisions, 4 co-holdings).
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `launch: "placeholder"`,
  `refuse_node: false`; **no canonical key minted, no threshold, statistic, file count or P7 handling
  class anywhere.**
- **Files written: exactly two** — the node JSON and this memo. No roster edit, no sibling row, no
  `src/`, no `check.py`.

---

## What was preserved, what was added

**Preserved unchanged** (verified this pass, not rewritten): the seed detection signal (the
contract-particulars block) and the precondition entry that opens `recognition.deterministic`; the
job-reference-in-a-labelled-slot, folder-context, email, calendar and archive-manifest signals; the
original `needs_llm` entries; the entire original `never_alone` list; `proposed_context_terms`;
`template.time_first: false` and the prose recommendation's reasoning; `file_kinds`; the four
original `collides_with` entries; all six `falls_through_to` entries; `role_split` (empty);
`sensitivity` and `sensitivity_why`; the ten original `file_examples` and their `observations`; the
`proposed_fields` position and its D6 argument; and the gist memo's four correct rejections and three
correct no-edge calls, which are reproduced above with attribution.

**Reversed, explicitly** (the addendum requires this be stated, not performed silently): five
deterministic signals — the valuation cycle, the instruction structure, the site-record structure,
the defects half of the completion triple, and the final-account structure — are **demoted out of
this row's activation evidence** and conceded to `final-account`, `variation-claim`, `site-diary`
and `snagging-defects`. The gist memo's claim that the valuation cycle and the completion/defects
triple were this row's distinguishing structures is **withdrawn**. It was made before those siblings
had landed their own arguments; they have, and they are better.

**Added this pass:** two retained-as-own signals (the award sequence, the handover envelope) and the
programme carve-out, which is what the row now stands on; two new `never_alone` entries, one of them
the branch-root rule itself; two new `needs_llm` entries; **eleven new reciprocal `collides_with`
entries**, each adopting the neighbour's own wording where the neighbour had already stated the line;
four `also_holds_with` entries where the gist row had none; five new fixtures, including the
**inbound and outbound collision fixtures**; sibling-ownership notes in the `must_not_conclude` of
seven existing fixtures; an annotated `work_types` list marking which values are owned as situations
elsewhere; the branch-root discipline written into `grouping_reasons` and `template.why`; a third
`open_question`; a corrected `one_line` that states the row's obligation and its limits instead of
announcing gist depth; and this memo, replacing the 3.3KB gist note — with the node test argued leg
by leg (including **two legs recorded as failing**), the rejected-files table, the reciprocal
boundary table, the two-way collision fixture, and the accounts of `progress-photos` and the two
refusals.

The `Depth: GIST` header is removed; the label is retired.

---

## NEEDS-JOSEPH (this node only)

- **Inherits NJ-CP-1 and NJ-CP-2** from the schema row. Without a `property` or
  `instruction`/`project` key, this row can recommend a job-first order only in prose, and its leg 2
  is unavailable in the JSON at all.
- **NJ-CP-11 · Is a branch root a row, or a browse-only parent?** *New this pass, and it is the
  question the reversal creates.* After conceding five signals to siblings, this row activates on
  four structures: the award sequence, the contract-particulars block, the programme, and the
  completion-and-handover envelope. **Alternatives and costs:** *(a) keep it as a row* — the envelope
  is real, unclaimed, and is what a practitioner reaches for years later; costs a row whose corpus is
  thinner than its `one_line` suggests. *(b) demote it to a browse-only parent with no activation* —
  intellectually clean and matches CONNECTION §3's parent semantics exactly; costs the four
  structures a home, and the award letter would fall to Independent Records, which is plainly wrong.
  *(c) fold the envelope into a larger sibling* — no natural host: `final-account` is the money,
  `trade-job` is the other scale. **This row's recommendation, offered not taken: (a).**
- **NJ-CP-12 · Job-first versus property-first for a building that receives repeated contracts over
  decades.** *Preserved from the gist memo, which recorded it rather than resolving it, and that was
  right.* This pass keeps job-first for this row and property-first for the family. A surveyor
  looking back at one building's history would choose the reverse. It is a judgement, not a design
  claim, and no threshold distinguishes the two cases.
- **NJ-CP-13 · Where does the handover pack sit when it is also a controlled issue?** An as-built
  transmittal to a client is this row's closing artefact and `drawings-revisions`' latest issue at
  the same time. This pass draws the line at **assembled-and-final versus one-of-a-sequence**, which
  is a judgement about intent rather than about bytes, and the sibling has not stated its side. R1c
  owes the reciprocal.
- **NJ · Do 27 templates survive R1c on a field-less schema?** Inherited from the schema row, and
  sharpened here: if this row's leg 2 and leg 3 both fail as distinguishing legs, so do most of its
  siblings', and the family's node tests all rest on detection signals alone. Two rows have already
  refused on exactly that basis.
