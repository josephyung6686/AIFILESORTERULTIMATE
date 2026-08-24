# `construction_property` — lab notes (R1b, J-IND row written to J-DEPTH)

Row kind: **schema**. Launch: **placeholder** (`fields: []`). Verdict: **kept, not refused.**

This is the schema row for the second-largest family on the roster — **27 sibling templates** measure
their node test against the default template stated here, and two of them have already refused on it.
The memo is written on the assumption that a sibling author reads *this file* before writing theirs,
so the posture, the vocabulary, the default template and the seams are stated explicitly rather than
left to be inferred from the JSON.

**Status of this pass.** The row was written once under the retired `Depth: GIST` label. It was a
verified-but-shallow draft: the JSON key set was house-correct, its quotations were machine-verified,
and its arguments were right. This pass **deepened rather than rewrote** — see *What was preserved,
what was added* at the end. Nothing that was already right was changed for the sake of change.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted. Every quotation in
  `construction_property.json` was grep-verified back out of it verbatim (see **Audits**). The spans
  that did the work here:
  - the dimension-order rule and its capture exception: *"For document and record domains, project,
    function, or subject usually comes before time because putting year first scatters related work
    across calendar folders."* and *"time often belongs first because capture date is a defining
    aspect of the material."* The second half is claimed by exactly one sibling and refused to it —
    see the progress-photos section.
  - the multi-role-token warning, which is this family's **constitutional** sentence: *"A university
    name alone should not create a group because Columbia can appear as an authoring school, course
    provider, target institution, employer, research venue, or merely a cited organization."* Read
    across to a postal address, it is the single most load-bearing line on the row.
  - the template-validator prohibitions — *"create meaningless one-child levels"*, *"use an author
    or organization merely as a collector"* — which are what hold `organization` to
    `destination_eligible: false` and what make a single-property corpus somebody else's row.
  - the table sentence, the source of the priced-works signal: *"Tables matter because resumes,
    forms, applications, invoices, and administrative documents often place their most useful
    information in cells rather than body paragraphs."*
  - the extractor sentence for proprietary formats, which is why an unreadable `.rvt` is a normal
    condition here rather than a failure: *"Design and creative formats such as PSD, AI, SVG, Figma
    exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas
    properties, embedded metadata, layers or artboards where accessible, linked asset names, and
    preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable
    rather than silently treated as empty."*
  - the sparse-file rule, which this family needs more than most because half its evidence is a
    photograph or a CAD file with nothing in the filename: *"The graph does not automatically copy
    those missing facts onto sparse files."*
  - the safety-domain sentence, which decides the `legal` seam: *"Finance, identity, medical, and
    legal material should be implemented first as safety domains"*.
  - the abstention sentence, which is the correct outcome for this family more often than for any
    other on the roster: *"Correct abstention is a successful outcome because the product's goal is
    reliable organization, not maximum file movement."*
  - the residual-library definitions, for all eight `falls_through_to` entries.
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance, no fabricated quotes, no numbers), 8
  (snake_case; a dimension may only branch on a declared field), 10 (no field rows on placeholder
  schemas), 11–15 (`kind`, closed edge vocabulary, `is_safety_domain`).
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation (step 2 never-alone, step 5
  protective ordering), §5 closed edge vocabulary, §6 field identity, §9 failure modes, PR-6.
- `planning/prompts/ALIGNMENT.md` — the sentence that decides what this row owes its siblings:
  *"would only repeat its schema's fields and dimension_order"* … *"it is the schema's default
  template."* Stating the default template in enough detail to make a sibling's refusal *checkable*
  is the whole service this row performs.
- `planning/domains/canonical_fields.json` — the 37 keys, all `design` provenance. Confirmed that
  `work_type`, `client`, `our_firm`, `location`, `event`, `capture_year` and `project` exist with the
  roles this row relies on, and that **nothing holds the property**. **No key minted.**
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D6, PR-6 and J-IND taken as
  ratified and not re-debated. J-DEPTH (2026-08-24) overrules J-IND's gist clause; this memo is
  written to the launch-row standard.
- `planning/domains/ROSTER.md` §4 + Appendix A, `planning/domains/roster.json` — the 27 sibling ids,
  their `one_line_hint`s, and the legacy `trade.*` / `cons.*` / `prop.*` ids this family absorbed.

### Landed neighbours read before writing (and not rewritten)

- `finance.household-property.json` + memo — a landed launch row at full depth, and **the** neighbour
  this family shares the most contested bytes with. Its fixture
  `Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf` is reproduced on this row as a **negative**
  example, with the same reading on both sides.
- `legal.leases-agreements.json` + memo — likewise landed and full-depth; its fixture
  `Lease Agreement - 18 River Court - Signed.pdf` is reproduced here as a negative example.
- `creative.json` + memo — the J-DEPTH schema-anchor exemplar, written for exactly this purpose. Its
  *"the default template, stated for the 41 siblings"* section is the model for this row's own.
- `creative.raw-photo-catalogue.json` + memo — landed at J-DEPTH, and it argues directly with this
  family's `progress-photos` row. Read in full; this row stays consistent with it (below).
- `business_operations.json` + memo — key set, `proposed_fields` shape, `role_split` spelling, and the
  shared `organization` proposal. Same professional-world posture; deliberately not contradicted.
- `business_operations.organisational-records.json` — the refusal standard, and the model both of this
  family's own refusals follow.
- This family's own two refusals, `construction_property.compliance-certificate` and
  `construction_property.timesheet`, read in full so that the schema posture stated here cannot
  quietly invalidate arguments that have already landed.

### A source that is *not* available, and it matters

**`00` never names this world.** The template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections"* — construction, trades and property are absent. That is why `design_cite` is `null`,
`provenance` is `proposal`, and every `collides_with` entry on this row is marked
`provenance: inference`. Sibling authors must not manufacture a `design_cite` for their rows either:
the honest position is that `00` supplies the *machinery* (extraction, activation, never-alone,
residuals, dimension order) and this family supplies the *situation*.

---

## What this family is, in one paragraph

An **occupation, not a topic**. Somebody is *instructed* about a property that is not necessarily
their own: to price it, survey it, design it, build it, approve it, certify it, value it, sell it,
let it or manage it. The record that occupation leaves is unusually well-structured — a title block,
a measured-works table, a valuation cycle, a conditions schedule, an apportionment schedule — and
**that structure, not the vocabulary of buildings, is what makes the schema detectable.** Any row on
this schema that cannot point at a structure of that kind is a document type wearing a domain's
clothes, and should refuse.

---

## Did this row survive the node test? All three legs, argued

`kind: schema`, so CONNECTION.md §2's schema test applies: can you name a distinct 3–6 field set, or
would you only repeat another schema, or need a giant form? The row declares **no fields at all**
under D1 as narrowed, so — as `creative` did — the test has to be run against the field set the row
*would* declare if the deferral were lifted. All three legs, separately:

### Leg 1 — a distinct field set

The candidate set is `property`, `instruction`, `work_type`, `client`, `our_firm`. Five keys, inside
the 3–6 band. Three of the five already exist; two are proposed and both are argued in the JSON.

The honest challenge is: **is this just `business_operations` with buildings in it?** A contractor is
an organisation running itself, and `business_operations` already holds contracts, projects, budgets
and vendors. Three answers, in ascending order of strength:

1. **`property` is a subject key that `business_operations` has no analogue for.** Its anchor is an
   organisational unit running a cycle or a project; the *thing the work is about* is not a slot it
   declares. Here the thing the work is about is a fixed, addressable, long-lived asset that outlives
   every job done to it and every firm that ever touched it. That is a different kind of noun, and it
   is the level a practitioner actually returns to years later.
2. **The custody triple.** One job's papers exist in three custodies at once — the client who
   commissioned the works, the professional who was instructed, the contractor who carried them out —
   and the *same bytes* are a different record in each. `00` gives this its own role-split pair
   (`client` / `our_firm`), and this family is where that pair bites hardest. `business_operations`
   has one custody by construction: its own.
3. **What is NOT offered as an argument.** The vocabulary. `variation`, `snagging`, `dilapidations`,
   `retention`, `preliminaries` are **values of `work_type`**, not fields, and a schema that
   justified itself on domain nouns would be rebuilding the 574's industry forest. This row says so
   explicitly, because it is the mistake a sibling author is most likely to make on their own leg 1.

Verdict on leg 1: **passes.** It passes on `property` and on the custody triple, and it would fail
without them. That narrowness is filed as NJ-CP-1 rather than smoothed away, because if R1c refuses
`property` a canonical key, leg 1 of this schema's own test loses its strongest limb.

### Leg 2 — detection signals of its own

This is the strongest leg and it does not depend on the field question at all. Four structures in
`recognition.deterministic` belong to no other schema on the roster:

1. **The title block.** A bordered zone on a drawing sheet carrying, *in labelled slots and together*,
   a project or site name, a drawing-number-shaped token, a revision designator, a scale, a status
   word and an originator. Nothing else in the catalogue has this. `creative` has linked-asset
   structure; `code` has manifests; `research` has figures. None of them has a *sheet border with a
   governed status word inside it*. Note carefully what is **not** the signal: a revision designator
   alone (every version family has one), a `.dwg` extension (a routing signal, not a meaning), or a
   project name.
2. **The measured-works table.** A line-item table whose rows are described *works or trades* and
   whose columns are quantity, unit, rate and amount, with a preliminaries or provisional-sum block.
   `00`'s table sentence licenses reading cells; what makes this table *this schema's* is the works
   description and the measured quantity, **not** the presence of money. Every schema on the roster
   that touches money has amounts in cells.
3. **The `to date, less previously certified` shape.** An interim valuation states cumulative works
   executed and subtracts what has already been certified. That arithmetic exists in this world and,
   as far as this pass could establish, nowhere else in the catalogue — an invoice is a snapshot, a
   statement is a ledger, a valuation is a *running cumulative claim*. Marked as inference; it is the
   kind of claim R2 could turn into a real pattern rule.
4. **The apportionment schedule.** Rows that are units or leaseholders *within one building*, columns
   that are a percentage share and a demanded amount, attached to a budget for that building. A
   share-of-a-fixed-asset table is structurally unlike a customer ledger or a payroll run.

Verdict on leg 2: **passes cleanly**, and it is the leg a sibling should try first.

### Leg 3 — privacy rules of its own

Three grounds, all in `sensitivity_why`, none of them the generic "documents can be sensitive":

- **The material names a real person's home and who is in it** — an occupier's address, a tenant's
  references and arrears, a leaseholder's correspondence, photographs of the inside of somebody's
  house taken to sell it. An address is not merely identifying; it is *locating*.
- **`00`'s own corpus sentence names material this family carries as a matter of course**: the corpus
  *"can include identity documents, account statements, tax records, medical information, legal
  records, credentials, private correspondence, GPS metadata, employment materials, and educational
  records"*. Site photography carries GPS metadata by default; tenant referencing carries account
  statements and identity documents by design.
- **The exposed party is usually not the user**, and cannot consent. A client's appraisal, a tenant's
  financials, a building's security-relevant layout: the holder is a custodian of somebody else's
  confidence. This is the sharpest of the three and it is the reason the setting is
  `potentially_sensitive` rather than something lighter.

Verdict on leg 3: **passes.** The row does **not** carry `is_safety_domain` — `00` names four safety
domains and this is not among them — and it assigns no P7 handling class. The gap that leaves is
NJ-CP-4.

**Overall: kept**, on three passing legs, one of them narrowly and conditionally.

---

## The default template, stated for the 27 siblings

`template.dimension_order` is **empty by binding contract**: a dimension may only branch on a field
the same entry's schema declares, and this schema declares none. That is a contract fact, not a
judgement that the world has no shape — it has an unusually clear one. The recommendation is
therefore held as prose, and **this is the paragraph every sibling must differ from**:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles* (a service-charge year,
> a rent-review cycle). **Not time-first.**

Why each level, and why in that order:

- **`property` first, not `instruction`.** A building outlives every job done to it, every firm that
  worked on it and every owner it ever had. The surveyor, the conveyancer and the block manager all
  return to *the building* years later, and a tree keyed on jobs scatters that history. This is the
  most contestable decision in the memo and it is stated as a recommendation, not a rule.
- **The reversal is licensed, and a sibling must say so.** A row whose entire life is one job at one
  address — `construction_property.trade-job`, `construction_property.construction-project` — may
  honestly put the instruction first, because property-first would produce exactly the *"meaningless
  one-child levels"* the validator rejects. **Reversing is not a difference that earns a node**; it
  is one of the things a template is *for*, and a sibling claiming a node on the reversal alone has
  claimed nothing.
- **Document function last**, by the parent-context rule. `Valuation 07` and `Rev C` are meaningless
  without the job, exactly as `Homework 3` is meaningless without the course.
- **Not time-first**, and this is the rule siblings will be most tempted to break, because this world
  is drowning in dates — issue dates, valuation dates, inspection dates, capture dates. `00` grants
  the time-first exception to **capture-based media only**. In this family **no sibling may claim it,
  including the photographic one** — see the next section, where `progress-photos` sets
  `time_first: false` and explains why.
- **Whatever lands stays a recommendation:** *"The system recommends an order based on the domain
  template, but the user can reverse, remove, add, or flatten dimensions."*

**The single most important sentence in this memo for a sibling author:** *`variation`, `snagging`,
`dilapidations`, `retention`, `preliminaries`, `certificate`, `drawing`, `schedule`, `survey`,
`valuation` and `report` are **values of `work_type`**, not rows.* A row exists where the detection
signals, the recommended dimensions, or the privacy rules differ from the paragraph above. Nowhere
else.

### The two refusals this family has already made, and why they are consistent with the above

Both were argued before this deepening pass and both survive it unchanged. They are restated here
because a sibling author needs to see the standard applied, not merely described.

- **`compliance-certificate` refused.** Its dimensions are the schema default; its privacy posture is
  the schema's; and its one candidate detection signal reduces, when stripped, to *a document-type
  word plus an address* — and **both halves are constitutionally never-alone on this schema**. A row
  whose entire support is never-alone evidence can never clear activation, so it would be a row that
  never fires. The coverage routes to Independent Records and to the situations that actually produce
  certificates. This is the cleanest possible demonstration of the never-alone list doing real work.
- **`timesheet` refused.** *"three documents that share a table shape"* — a signed dayworks sheet
  (that is `variation-claim`'s situation), a site attendance register (that is `site-health-safety`'s,
  and under a **stricter** privacy posture than this schema's default), and a labour allocation sheet
  (that is `site-diary`'s). What remains after the split is hours-against-rates for the purpose of
  paying someone, which is `hr` and `finance`. The lesson for siblings: **a shared table shape is not
  a situation.**

Neither refusal is a failure. Both are the node test working.

---

## `progress-photos` — the one row recognised by something other than document structure

This family's best piece of reasoning, preserved verbatim in argument and re-checked here:

> Every other row on `construction_property` is recognised by **document structure** — a header, a
> reference, a table, a signature block. `progress-photos` is recognised by **capture metadata,
> rhythm and place**. That is a different detection method, and *a `work_type` value cannot carry a
> different detection method; only a template can.*

That is leg 1 of its node test and it is decisive against the "it is just a `work_type` of
`construction-project`" challenge. Its discriminator against the `photos.*` family is **repetition of
place across time** — in its own words, *"a camera roll goes to many places once, a site walk goes to
one place many times."*

**Consistency with the landed `creative.raw-photo-catalogue` (J-DEPTH).** That row read this argument
and **agreed with it**, adding one thing that runs in its favour: *being catalogued must never be
read as evidence about subject matter*, because a catalogue indexes whatever was imported. It also
observed that the two rows recommend *opposite* tree orders — `progress-photos` puts site first
because one place recurs; the catalogue row puts capture date first because no place, client or
project recurs across a general archive — and concluded that this is the **same rule applied to
different material**, not a contradiction. **This schema row endorses that reading and does not
reopen it.** The shared fixture is named on both sides: `Marsh Lane week 14/IMG_2044.HEIC`.

The schema-level consequence, stated so it can be overruled once rather than 27 times: a placeholder
schema whose default recognition is documentary **may** host a capture-based template, because
CONNECTION.md §2 makes *differing detection signals* sufficient on its own. Filed as open question (6).

---

## The professional-versus-householder seam, drawn explicitly

This is the single most important seam for this family, and the dispatch is right that it must be
stated reciprocally. Drawn:

**The seam is not the document type, the address, the money, the trade, or the format.** A completion
certificate, a survey, a warranty, a quotation, an invoice, a floor plan and a set of photographs
exist identically on both sides of it. Any test built on document type will be wrong in both
directions, and the landed `finance.household-property` row lists *title, inspection, warranty and
completion certificate* among **its own** work types, which settles the point.

**The seam is INSTRUCTION**, and it is a checklist of structures:

| Evidence present | Reading |
|---|---|
| a job/matter/instruction reference, a fee or appointment, a client party in a role slot, a works measurement, a title block, a valuation cycle | professional practice — **this schema**, and an instruction-bearing sibling |
| a householder's own ownership, occupation, taxation, insurance and maintenance record of their **own** home, with no instruction around it | **`finance.household-property`**, which landed first and holds it |
| an executed **instrument** — party recitals, covenants, consideration, execution block — held as the holder's own agreement record | **`legal.leases-agreements`**; legal is a safety domain and protects first |
| an organisation's occupation of its own premises as part of running itself | **`business_operations.facilities-workplace`** |
| role does not settle, and neither side's evidence is present | **neither activates.** *"Correct abstention is a successful outcome because the product's goal is reliable organization, not maximum file movement."* |

**The consequence a sibling author is most likely to get wrong:** *an address does not select a side.*
The property address is the one thing present on **both** sides of every one of these lines, which is
precisely why it is the family's constitutional never-alone.

**Where the seam is genuinely uncomfortable, and it is not hidden:** a self-builder, a small landlord
with four flats, a leaseholder who project-manages their own extension. Each of them produces
instruction-shaped documents about their own home. This pass draws the line on instruction anyway,
because a line drawn on scale would need a threshold and `_CONTRACT` rule 3 forbids inventing one.
Filed as NJ-CP-3.

---

## Files considered and rejected

The dispatch's own test: a row that only lists what it holds has not been researched. Named tempting
false positives, and what discriminates each.

| File | Why it is **not** this schema's evidence |
|---|---|
| `Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf` *(kept in the JSON as a negative fixture)* | A tradesperson's invoice with a property address on it — the most tempting file in the catalogue. Discriminator: **no job reference, no works measurement, and the service address is the holder's own home.** The landed `finance.household-property` row already claims it and this row reproduces its reading unchanged. |
| `Building Regulations Completion Certificate - 18 River Court.pdf` *(added this pass as **the** collision fixture — see below)* | Every deterministic signal short of the instruction pair is satisfied. Still a householder's record. |
| `Lease Agreement - 18 River Court - Signed.pdf` *(kept as a negative fixture)* | The operative instrument. Legal is a safety domain and protects first. What this schema holds is the **estate-management lifecycle around** it — the rent-review memorandum, the schedule of condition, the dilapidations schedule, the apportionment, the licence to alter. |
| A CV of a site manager | `career`. It names sites, projects, contract values and trades, and it is a person's own record of themselves. Zero instruction structure. |
| A payroll run for site operatives; a CIS or subcontractor tax return | `hr` and `finance`. Real files in a builder's folder; not evidence of *this* schema. This is the same reasoning the `timesheet` refusal used, and the two must stay consistent. |
| A `.vcf` of site contacts | `00` requires contact data be privacy-protected rather than used to create folder proposals. It can be a file-kind signal at most, and using it as an example would have been misleading. |
| An architecture dissertation; a construction-management textbook chapter | `academic` and Reading Inbox. Shares the entire vocabulary and **no evidence item at all**. This is the clearest demonstration that this family is not detected by its nouns. |
| Standards, guidance notes, a saved market report, a manufacturer's technical PDF | Reading Inbox. These accumulate heavily in a practitioner's folder and are not job records — *"papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* |
| A structural engineer's calculation package | Genuinely this world **and** genuinely `engineering`'s. Not rejected — recorded as a shared-evidence case on the new `engineering` collision entry. Its detection is the title block and specification already listed, so it adds no *new* signal. |
| A rendered exterior view of a proposed building | `creative.architectural-visualisation`. Same subject, same `design_creative` source type, same project name. Discriminator: **the title block and its status/revision apparatus.** Construction information is issued, superseded and built from; a visualisation has a brief, a round of amends and a deliverable handoff. |
| A portal listing screenshot | May be a comparable, a competitor's listing, or idle browsing. Kept as a fixture precisely so the wrong conclusion is written down. |
| `node_modules/`, `.git/` inside a site-monitoring repo | Removed from organisation by the exclusion rule; where a repository root fires, `code` owns the layout and this schema must not propose re-filing anything inside it. |
| A haulage confirmation and a warehouse pick list | `logistics` (not yet written). This schema stops at the **site gate** — see the seam below. |
| A factory works order and a production batch record | `manufacturing` (not yet written). This schema holds the article's **installation and approval at a named site**, not its making. |

---

## The collision fixture, named

**`Building Regulations Completion Certificate - 18 River Court.pdf`.**

It is the hardest file in this family's world, and it was added to the JSON this pass because the row
did not previously carry one that failed on *the instruction pair specifically*. It satisfies:

- the **authority-decision structure** — a building-control body's letterhead, an
  application-reference-shaped token, a completion declaration;
- a **property address in a labelled slot**;
- a **document-type word** from this family's own `work_types` list;
- and it sits in a folder full of building paperwork.

And it is still **a householder's own record of their own home** — which the landed
`finance.household-property` row already claims, listing completion and compliance certificates among
its own work types.

**What discriminates it:** the *neighbourhood*, not the file. No job or instruction reference, no fee
or appointment, no client party, no works measurement, and a custody in which the holder is the owner
rather than the instructed party. Where the same certificate sits in a builder's handover pack
against a contract reference, this schema fires and both readings hold.

**The reciprocal, which `finance.household-property` must carry when R1c makes the edges two-way:**
*a householder's own building paperwork never becomes a professional instruction because a
professional produced it.* The same fixture bytes are named on **both** sides — this one, and
`Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf` running the other way.

---

## Reciprocal boundaries, both directions

| Neighbour | This schema must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `finance.household-property` **(landed)** | a householder's own ownership, occupation, tax, insurance and maintenance record of their own home, with no instruction around it | a professional's instructed job file because the property is a house | `Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf`; `Building Regulations Completion Certificate - 18 River Court.pdf` |
| `legal.leases-agreements` **(landed)** | the operative clause structure of the instrument — recitals, covenants, consideration, execution | the estate-management apparatus around it: rent-review memoranda, schedules of condition, dilapidations, apportionments, licences to alter | `Lease Agreement - 18 River Court - Signed.pdf` |
| `business_operations` | a desk-booking policy, an office move plan, a facilities vendor register — an organisation occupying premises while running itself | a fit-out with a contract sum, drawings and interim valuations, merely because the occupier commissioned it | a lease of the office; a fit-out contract |
| `government` | an issuing authority's own case file, statutory powers, or decision-making record | an applicant's or agent's submission, acknowledgement, and the conditions it must discharge | `Decision Notice - 24-01187-FUL - 18 River Court.pdf` — the application reference is on both copies and discriminates nothing |
| `photos` | camera originals with no job reference and no diary entry around them | a site walk's originals as a mere photo event, proposing a capture-year home for a professional record | `IMG_2231.HEIC`; `Marsh Lane week 14/IMG_2044.HEIC` |
| `creative` | a persuasive rendered image with a brief, amends rounds and a deliverable handoff | a drawing sheet under revision control because it is a `design_creative` file with a project name | a `.skp` model and a PDF view of the same building |
| `engineering` | a drawing set for a product, machine, vessel or system that has **no site** | a site-anchored drawing set with statutory approval, valuation and handover downstream of it | a structural calculation package for a named building |
| `logistics` *(not yet written)* | the carrier, route, fleet and warehouse — everything before the site gate | a delivery note keyed to a plot and a job reference and signed by a site manager | a delivery note |
| `manufacturing` *(not yet written)* | the production run, batch, works order and factory quality regime | a shop drawing carrying a project title block and revision status, or a test certificate inside a handover pack | a material or test certificate |

The three seams marked *(landed)* and *(not yet written)* are authored **one-way here**. The two
landed rows do not name `construction_property` in their own memos, and the two unwritten schemas
cannot yet. **R1c owes all of these reciprocals**, and the fixture bytes are named on this side so
that the reciprocal can be checked rather than asserted.

---

## Neighbours considered that did **not** get an edge

- **`career` / `hr`** — the people who do this work are a different world. No document family is
  genuinely confusable at *schema* level; the one confusion that exists is at row level (a site
  timesheet), and that row **already refused**, for reasons this schema row is careful not to
  contradict.
- **`academic` / `research`** — full vocabulary overlap, zero evidence overlap. Naming an edge here
  would be conceding that this family is detected by its nouns, which is exactly what it is not.
- **`code`** — BIM and parametric authoring files are structured data by format, but the file-kind
  lists already separate `design_creative` from `code_structured` and no document is confusable.
- **`retail_hospitality`, `nonprofit`, `resource_operations`** — all three commission building work.
  That makes them **values of `client`**, not neighbours. Naming them as edges would rebuild the
  industry forest ALIGNMENT.md removed.
- **`identity`** — tenant referencing packs carry passports and bank statements. The schema-level
  relationship is **protection, not a shared reading**, and it is handled through `sensitivity` and
  the Protected Records fallthrough rather than an edge — the same move `photos.json` makes.
- **`clinical_practice` / `law_practice`** — structurally the closest analogues on the whole roster
  (a professional, an instruction, a file, a third party's confidence) and therefore worth naming as
  a **posture** sibling rather than an edge. They contest no evidence with this family whatsoever.

---

## Sparse-file discipline

Six of the eleven fixtures carry `group_without_copying_facts: true`, and this world needs the rule
more than most because its sparse files are the **normal** case: an unreadable `.rvt` in a folder
named after a job number, an `IMG_2231.HEIC` in a GPS cluster, a `.zip` handover pack whose members
are never extracted, a portal screenshot, a calendar entry. In every one, the neighbourhood may
legitimately group the file while **no** property or instruction fact is written onto it. `00`'s
sentence is the authority: *"The graph does not automatically copy those missing facts onto sparse
files."*

Every fixture also carries *"any construction_property fact — the schema declares none"* in its
`must_not_conclude`, so the placeholder status is checkable file-by-file and not only in the header.

---

## `proposed_fields` — the full list

**Three entries. One is a mint, one is a mint offered with its own alternative, and one is explicitly
not this row's proposal at all.**

- **`property`** — **new, and the load-bearing hole.** No canonical key holds *the thing built or
  managed*. `location` is the photos key for where an image was *captured* and carries a capture
  reading, not a subject reading — folding them would file a progress photo taken from the pavement
  opposite under the pavement. `institution` is a finance counterparty; `venue` is a publication
  venue; `client` is a person or organisation, not an asset; `project` names the *job*, not the
  address it happens at, and one property carries many jobs across decades while one job may span
  several plots. `destination_eligible: true` proposed, with the countervailing point stated rather
  than hidden. Ceiling `possible`; `validated` would need an address-plus-role rule family that R2
  owns and this row does not write. **Adjudicate: R1c (NJ-CP-1).**
- **`instruction`** — **new, and proposed *with a live alternative that R1c should feel free to
  take*: reuse the canonical `project`.** Half this family's instructions genuinely are projects; the
  other half — a tenancy, a sale instruction, a portal listing, a standing block-management
  appointment — are engagements with a start, a fee and an end, and calling them projects shows up as
  a bad folder name. **If `project` stretches far enough, this proposal should be dropped, not
  shipped beside it.** A near-duplicate of a canonical key is the exact defect D6 exists to kill, and
  `00` is explicit: *"The system may create new values when it sees a new course, project, company,
  university, or event, but it should not invent new fields automatically."* **Adjudicate: R1c
  (NJ-CP-2).**
- **`organization`** — **NOT this row's proposal.** It is a **reuse** of the key the landed
  `business_operations` schema row already proposed, and **R1c must settle it as ONE decision, there,
  for both rows.** The need is identical — the custody question of whose record a file is — and this
  row records it only to add the construction-side datum: *one job, three custodies*. Its
  `destination_eligible: false` follows `business_operations`' reasoning unchanged and this row does
  not reopen it.

**No fourth key is proposed, and one deliberately is not.** `work_type`, `client`, `our_firm`,
`location`, `event` and `capture_year` are canonical and are referenced, never respelled. The
`role_split` entry records a genuine third gap — the **contractor** role has no key while `client`
and `our_firm` do — and this row **does not mint one**, for the same reason `creative` declined to
mint a rights key at its own point of maximum temptation: minting on a schema that declares no
fields, at exactly the moment it would be most convenient, is the 574's original mistake performed
knowingly.

`proposed_context_terms` carries this family's practice vocabulary (`title block`, `issued for
construction`, `superseded`, `provisional sum`, `previously certified`, `retention`, `practical
completion`, `snagging`, `dilapidations`, `apportionment`, `residual land value`, …). These are
**proposals**, not `00`'s floor — `00`'s named context-term floor is the academic one, and this row
does not pretend otherwise.

---

## Audits run before returning

- `python3 -m json.tool planning/domains/nodes/construction_property.json` → parses.
- **Key set identical to the landed `creative.json` and `business_operations.json`**, same 27 keys in
  the same order — compared programmatically, empty symmetric difference.
- **Every quotation used in this memo grep-verified verbatim** against
  `00-database-agent-product-design.md` with `grep -c -F`, each returning exactly one match. The
  quotations already in the JSON were machine-verified on the previous pass and were not disturbed.
- **Every `file_examples.source_type` is in P5's `SOURCE_TYPES`**; the new fixture uses
  `text_document`.
- **Every `falls_through_to` and `falls_through_if_inactive` is one of the nine residual names**,
  spelled `00`'s way.
- **Every `collides_with` and `also_holds_with` target exists in `roster.json`** — including the two
  newly added schema ids `logistics` and `manufacturing`, and `engineering`, all three confirmed
  present as schema rows.
- `fields: []`, `dimension_order: []`, no canonical key minted, no threshold, statistic, file count or
  P7 handling class anywhere.
- **Files written: exactly two** — `planning/domains/nodes/construction_property.json` and this memo.
  No roster edit, no sibling row, no `src/`, no `check.py`.

---

## What was preserved, what was added

**Preserved unchanged** (verified this pass, not rewritten): the three `proposed_fields` entries and
all their arguments, including `organization`'s explicit deference to `business_operations`; the
entire `recognition` block (deterministic, needs_llm and the never-alone list); `work_types`;
`grouping_reasons`; `proposed_context_terms`; `template.why` and its prose recommendation;
`file_kinds`; the six original `collides_with` entries; all five `also_holds_with` entries; all eight
`falls_through_to` entries; `role_split`; `sensitivity` and `sensitivity_why`; and the ten original
`file_examples` with their `must_not_conclude` lists.

**Added this pass:** the collision fixture
`Building Regulations Completion Certificate - 18 River Court.pdf`; three new reciprocal
`collides_with` entries (`logistics`, `manufacturing`, `engineering`); two new open questions (the
logistics/manufacturing seam, and the schema-level capture-based-template question); a corrected
`one_line` that states this row's obligation to 27 siblings rather than announcing gist depth; a
corrected sibling count in `open_question` (it said *eight rows in this family*; there are 27
templates plus this row); and this memo, rewritten from 7.3KB to J-DEPTH with the node test argued
leg by leg, the default template stated for siblings, the rejected-files table, the reciprocal
boundary table, the collision fixture, and the consistency check against
`creative.raw-photo-catalogue`.

---

## NEEDS-JOSEPH (this node only)

- **NJ-CP-1 · Does `property` become a canonical field key?** Every row on this schema wants it; no
  canonical key holds it; its absence is why all 28 rows in this family recommend dimension orders in
  prose and declare none. **Alternatives and costs:** *(a) mint it* — gives the family its only real
  folder level and makes leg 1 of this schema's own node test sound; costs a new global key and forces
  the address-privacy question into the open. *(b) refuse, and reuse `location`* — mints nothing;
  costs the family a subject/capture conflation that will produce visibly wrong folders for every
  photographic and survey row. *(c) refuse entirely* — the family is grouped but never structured,
  and 27 templates recommend nothing. **This row's recommendation, offered and not taken: (a).**
- **NJ-CP-2 · `project` reuse, or a new `instruction` key?** **Pick one; shipping both is the D6
  defect.** *(a) reuse `project`* — mints nothing, and is this row's preference for the
  project-shaped siblings; costs a stretch on tenancies, listings and standing appointments. *(b)
  mint `instruction`* — covers the whole family honestly; costs a near-duplicate of a canonical key.
  *(c) both* — **rejected in advance.**
- **NJ-CP-3 · The professional/householder line is drawn on INSTRUCTION by this pass, not by `00`.**
  A self-builder, a small landlord and an owner project-managing their own extension sit exactly on
  it. A line drawn on scale would need a threshold, which `_CONTRACT` rule 3 forbids. Joseph's call
  whether instruction is the right axis.
- **NJ-CP-4 · No `is_safety_domain`, correctly — but the material carries third-party personal data
  routinely.** `00` names four safety domains and this is not one. Occupier addresses, tenant
  references and leaseholder arrears are personal data by any ordinary reading, so the substitute
  mechanism that forces P7 ahead of a model path for **third-party** personal material needs a home.
  **This is the same gap the landed `business_operations` row records**, and the two should be
  answered together.
- **NJ-CP-5 · The `logistics` and `manufacturing` seams are drawn here, one-way, because neither
  schema exists yet.** The proposed lines — the site gate for goods, article-versus-installation for
  fabrication — were drawn by this pass. Whoever writes those schemas may reasonably draw them
  elsewhere; R1c owes the reciprocal either way.
- **NJ · Do 27 templates survive R1c on a field-less schema?** If D1's deferral holds, the dimensions
  leg of the node test is unavailable to all 27 equally, and each must justify itself on detection
  signals and privacy rules alone. Two have already refused on exactly that basis. Several more —
  `plant-hire`, `materials-delivery`, `snagging-defects` — may then be `work_type` values on a
  sibling rather than rows of their own.
