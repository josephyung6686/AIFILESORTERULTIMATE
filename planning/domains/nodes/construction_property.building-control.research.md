# `construction_property.building-control` — lab notes (R1b, deepened to J-DEPTH)

Depth: J-DEPTH
Row: `construction_property.building-control` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `cons.building-control` (ROSTER.md line 912).

**Verdict: the row STANDS — but on narrower ground than the gist draft claimed, and with one of the
gist draft's three supporting arguments withdrawn.** The dispatch asked whether this row survives at
all against three named failure modes. It does, decisively on one leg, respectably on a second, and
**not at all on the third — which the gist memo had wrongly counted in its favour.** Both the
narrowing and the withdrawal are stated below rather than smoothed.

**Status of this pass.** The row was written once under the retired `Depth: GIST` label. It was a
verified-but-shallow draft: its JSON key set was house-correct, its 22 quotations all grep back out
of `00` verbatim, and its central argument — that the load-bearing boundary is *side, not topic* —
was right and is preserved unchanged. This pass **deepened rather than rewrote.** See *What changed
in this pass* at the end.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — the only document quoted. All **25** quotations in
  the JSON (22 preserved + 3 added this pass) were grep-verified back out of it verbatim; see
  **Audits**. The spans that did real work here:
  - the multi-role-token sentence, which the schema row makes this family's **constitutional**
    never-alone: *"A university name alone should not create a group because Columbia can appear as
    an authoring school, course provider, target institution, employer, research venue, or merely a
    cited organization."* Read across to a **council**, it is even stronger than it is for an
    address — see leg 2.
  - **new this pass**, and the sharpest single line for this row: rules should *"suppress generic
    hubs such as a personal email address or broad university domain."* An authority email domain is
    exactly such a hub, and the portal era makes it the most tempting false signal on the row.
  - **new this pass**, twice: *"The graph does not automatically copy those missing facts onto sparse
    files."* This is what stops an application group enriching a bare inspection slip, and it is also
    what forced the narrowing in leg 1.
  - the purpose-coherence sentence, which is what a case *is*: *"The documents are content-incoherent
    but purpose-coherent."*
  - the dimension rule and its non-exception here: *"For document and record domains, project,
    function, or subject usually comes before time because putting year first scatters related work
    across calendar folders."*
  - the abstention sentence, which is this row's answer whenever side does not settle: *"Correct
    abstention is a successful outcome because the product's goal is reliable organization, not
    maximum file movement."*
  - the residual definitions, for all six `falls_through_to` entries.
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance; no fabricated quotes; **no invented
  numbers**, which is why NJ-CP-7 below is filed rather than answered), 8, 10 and 15 (no field rows
  on a placeholder schema), 11–14.
- `planning/domains/CONNECTION.md` — §2 node test (applied leg by leg), §3 activation ≠ grouping,
  §4 step 2 never-alone, §5 closed edge vocabulary, §9 failure modes, PR-6.
- `planning/prompts/ALIGNMENT.md` — *"would only repeat its schema's fields and dimension_order"* …
  *"it is the schema's default template."* This sentence is what withdrew argument (3) below.
- `planning/domains/canonical_fields.json` — 37 keys checked. **Nothing minted, nothing proposed.**
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D4, D6, PR-6, J-IND taken as
  ratified. J-DEPTH (2026-08-24) overrules J-IND's gist clause.
- `planning/domains/ROSTER.md` §4 + Appendix A — confirmed `cons.building-control` is this row's only
  absorbed legacy id, and confirmed that **`government.planning-application` and
  `government.permit-licensing` are real roster rows** (ROSTER.md §12), so both `collides_with` edges
  point at ids that exist rather than at a hypothesis.

### Neighbours read in full before writing, and not rewritten

- **`construction_property.research.md`** (the deepened schema anchor, 43KB) — read first, as the
  addendum requires. It states the family default template, the professional-versus-householder
  seam, and — critically — it already draws **the `government` seam with this row's own fixture**.
- **`construction_property.compliance-certificate.json` + memo** — the landed refusal in this family,
  and my nearest danger. Read closely; answered in full below.
- **`construction_property.construction-project.research.md`** (the family spine, 38KB) — read
  because failure mode (b) says I might be a stage of it. It **defers to this row in prose** and I
  owed it an edge, which this pass supplies.
- `business_operations.organisational-records.json` — the refusal standard, re-read before deciding
  whether to reverse the gist verdict.

### The source that does not exist, and it matters twice

**`00` never names this world.** Its template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections."* Neither construction nor public administration appears. That is why `design_cite` is
`null`, `provenance` is `proposal`, and **every `collides_with` entry on this row is marked
`provenance: inference`.** `00` supplies the machinery; this family supplies the situation. It
matters twice here because the second missing source is a whole schema — see the `government`
section.

---

## The three failure modes the dispatch named, answered before the node test

The dispatch was right to put these first: if any of them holds, the node test is moot.

### (a) "It is a document type, exactly as `compliance-certificate` was"

**It is not, and the difference is precise rather than rhetorical.**

The refusal's own reasoning is the fair test, so it is applied verbatim to me. `compliance-certificate`
was refused because its candidate signal, *stripped to what would actually have to fire*, reduced to
**a document-type word plus an address** — and both halves are constitutionally never-alone on this
schema, so it would be *"a row that never fires"*

Run the same strip on this row. What remains is **not** a word and an address. It is a **four-part
co-occurrence** — an issuing body that resolves to a planning or building-control authority, **plus**
an application-reference-shaped token *in a labelled reference slot*, **plus** a decision word,
**plus** a numbered schedule of conditions. Remove any one and the row does not fire; that is stated
as a precondition in `recognition.deterministic` rather than left implicit. Two further structures
stand on their own: the **condition-number-against-application-reference pair**, which exists in no
other row on the roster, and the **staged inspection sequence** (excavation → foundation → damp proof
course → drainage → structure → completion) issued by the authority rather than the contractor.

But the honest discriminator is not the count of parts. It is this:

> **A certificate is a document. An application is a CASE.**

`compliance-certificate` had no lifecycle to point at — an installer signs a declaration and it is
finished, which is exactly why `00` answers it by name under *"standalone certificates, notices,
confirmations, forms, and PDFs that have a durable purpose but no broader group."* This row's whole
content is a lifecycle: validated → consulted → decided → conditioned → discharged → inspected →
completed, with **one identifier recurring across every member**, and members that are a form, a
drawing, an essay, a letter, an objection, a site photograph and a certificate. That is `00`'s own
description of a group: *"The documents are content-incoherent but purpose-coherent."*

**The narrowing this forced, and it is a real concession.** If the case is what makes the row, then
an authority document *without* a case around it is **not** this row — even when it carries an
application reference. The gist draft implied otherwise by holding "the completion or final
certificate that closes the file" unconditionally. It is now conditional, in `one_line`, in
`recognition.needs_llm`, and in the fixtures. A lone Building Regulations completion certificate in a
householder's folder is `finance.household-property`'s or Independent Records', and this row **must
not accept through a fixture what the family refused as a row.** `00`'s sparse-file rule is the
authority for refusing to manufacture the missing case: *"The graph does not automatically copy those
missing facts onto sparse files."*

**Where I remain genuinely exposed, and it is not hidden:** three of my `work_types` — completion
certificate, final certificate, validation letter — are literally the refused row's material. I hold
them *only* inside a case. If R1c decides that "inside a case" is not checkable at activation time,
this row loses those three and shrinks to the decision-and-conditions core. It would still stand on
that core; it would just be smaller. That is filed as **NJ-CP-7**.

### (b) "It is a `work_type` stage of `construction-project`"

**It is not, and the sibling has already said so in writing.** `construction-project.research.md`
lists `government.planning-application` among the *neighbours it did NOT give an edge to*, on the
express ground that *"the authority-decision structure belongs to `construction_property.building-control`,
which states the government boundary from the applicant's side."* Its JSON carries fifteen
`collides_with` entries and none of them is me — the deference is one-way prose. **This pass supplies
the reciprocal edge**, because a boundary asserted only in a neighbour's prose is not a boundary.

Three independent arguments, and the third is the decisive one:

1. **The counterparty is different in kind.** Every other row on this schema is *bilateral commerce*:
   a client instructs, a contractor performs, money moves against measured works, and the apparatus is
   a contract sum, a programme, an interim valuation, a retention and a final account. Building
   control is a **statutory** relationship with a body that is not a party to the contract, cannot be
   negotiated with, is not paid against measured works, and whose decision binds regardless of what
   the contract says. The job row's own activation evidence — *"the contract envelope"* — is absent
   from every document this row holds, and vice versa.
2. **A `work_type` value cannot carry a different counterparty.** The schema anchor makes exactly this
   move for `progress-photos`: *"a `work_type` value cannot carry a different detection method; only a
   template can."* The same logic applies to a different *relationship*. `variation`, `snagging` and
   `retention` are values because they are things that happen inside the contract. A planning
   permission happens outside it.
3. **It pre-dates the job, outlives it, and routinely exists without one.** A planning permission is
   commonly obtained years before there is a contractor and often before there is a design; it can be
   sold with the land; it lapses; it is refused; a lawful-development certificate is frequently
   obtained purely to complete a sale, with no works ever contemplated. A stage *inside*
   `construction-project` cannot exist without the job. **This one routinely does — and that is the
   argument the job row cannot absorb**, because absorbing it would require the branch root to hold
   files that have no branch.

The shared fixture is named on both sides: **`Condition 4 discharge - drainage details.pdf`**. The
job file holds it as project correspondence; this row holds it as the condition sequence. Both
readings hold, neither excludes the other, and the edge exists to stop either row claiming it
exclusively.

### (c) "It is `government`'s material"

**Half of it is, and the seam runs through the middle of every document — which is why this is a
SIDE collision rather than a topic one.** It is the most important thing this memo has to say, and
the dispatch is right that `government`'s author needs it written down before they start.

**Where `construction_property` stops and `government` begins.** The seam is **custody and role**, not
subject matter. Both sides handle the same building, the same address and the same reference number.

| Evidence present | Side |
|---|---|
| an applicant's or agent's **submission** — a completed statutory form with the holder's own declaration, a fee payment made by the holder, a supporting statement the holder commissioned | **`construction_property.building-control`** |
| an **acknowledgement or validation letter addressed to the holder**, and a decision notice **received** — conditions stated as obligations *the holder must discharge* | **`construction_property.building-control`** |
| condition-discharge material the holder **assembled and submitted**, and the authority's confirmation **back** to them | **`construction_property.building-control`** |
| an **issuing** letterhead and signature block the holder controls; a **case file** rather than a case; an **officer's report or delegated report** written to justify a decision; a consultation exercise the holder is **running** | **`government.planning-application`** |
| statutory **power** exercised — an enforcement notice **issued**, a committee agenda, a register entry, a scheme of delegation | **`government.planning-application`** or `government.municipal-administration` |
| an instrument that licenses an **activity or an occupation of the public realm** — a street-works permit, a scaffold licence, a skip permit, a hoarding licence — rather than approving **building works** under a planning or building-regulations regime | **`government.permit-licensing`** |
| the **objector's** own file: a neighbour's copy of their own objection, the notification they received, their correspondence about somebody else's application | **neither.** It is a personal-administration record about a property that is not the subject; Independent Records or Protected Records |
| role does not settle | **neither activates** — *"Correct abstention is a successful outcome because the product's goal is reliable organization, not maximum file movement."* |

**The thing the `government` author most needs to know:** *the application reference is on both
copies and discriminates nothing.* It is the strongest-looking token in the world and it is worthless
as a side discriminator. The schema anchor already says this, naming the same bytes —
**`Decision Notice - 24-01187-FUL - 18 River Court.pdf`** — in its reciprocal-boundaries table:
*construction_property must not take* "an issuing authority's own case file, statutory powers, or
decision-making record"; *government must not take* "an applicant's or agent's submission,
acknowledgement, and the conditions it must discharge." **This row is consistent with that and does
not extend it.**

**And the fourth role nobody has authored.** An **approved inspector** is a *private* body
discharging a *statutory* function competitively, for a fee, under an appointment. It is neither a
public authority nor an ordinary consultant. Its own file is a professional instruction and belongs on
this schema; the notices it issues are statutory instruments and read as `government`'s material in
every respect except the identity of the issuer. **No row on the roster owns this and this pass does
not invent one.** Recorded for R1c as part of NJ-CP-6.

**Verdict on (c): the row survives, but only as the applicant's half.** If R1c decides that side is
unextractable in practice, the honest consequence is that *both* rows abstain on the contested
documents — not that either wins.

---

## The node test, leg by leg, against the family's stated default

CONNECTION.md §2: *"A **template** row exists only if its detection signals, recommended dimensions,
or privacy rules differ from its schema's default template."* Any one leg suffices. The schema anchor
states the default so that this is checkable rather than assertable:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation genuinely cycles. **Not time-first.**

### Leg 1 — recommended dimensions: **FAILS, and the gist memo was wrong to claim it**

This is the withdrawal. The gist memo argued that the row differs because it is **property-first**,
*"following the family default deliberately"*, and offered that as support. **That argument is
withdrawn.** The deepened schema anchor is explicit in the opposite direction:

> *"Reversing is not a difference that earns a node; it is one of the things a template is for, and a
> sibling claiming a node on the reversal alone has claimed nothing."*

If *reversing* the default earns nothing, then **following** it earns strictly less. And the second
level does not rescue it either: this row would recommend property → **application** → function, and
an application is honestly an *instruction-shaped container* — a named engagement about a property,
which is precisely the slot the default's `instruction` level already holds. Calling it "application"
instead of "instruction" is a rename, not a different tree.

**Leg 1 does not carry, and the row does not need it.** `dimension_order` is empty by binding contract
in any case (a dimension may only branch on a field the same entry's schema declares, and this schema
declares none — `_CONTRACT` rules 10 and 15, PR-6), so nothing in the JSON changes. What changes is
that the memo no longer counts an empty box as evidence.

### Leg 2 — detection signals: **PASSES, decisively, and the row rests here**

Three structures belong to no other row on this schema and, as far as this pass could establish, to
no other row on the roster:

1. **The authority-decision structure** — issuing body **+** application reference in a labelled slot
   **+** decision word **+** numbered conditions schedule, *all four together*. The nearest analogues
   elsewhere on the roster are a court order (`legal`, which has a caption and a proceeding rather
   than an application and conditions) and a regulator's determination (`government`'s own, which is
   the other side of this same document). Neither is on this schema.
2. **The condition-number-against-application-reference pair.** A document that says, in effect,
   **here is what condition 4 of 24/01187/FUL requires, and here it is** A compound of two
   identifiers where neither alone means anything and the pair means one thing exactly. Nothing else
   in this family or its neighbours has this shape.
3. **The staged inspection sequence.** Not "an inspection" — the word is never-alone and is now listed
   as such — but a *governed ordered series of visit records against one reference*, each naming a
   stage of works that must be signed off before the next may proceed. A contractor's quality record
   has visits; it has no statutory gate and no external issuer.

None of these is a document type, and none is shared with a sibling. Compare the refused row, whose
best leg reduced to a word and an address. **This is the difference between the two rows, stated as
plainly as it can be.**

### Leg 3 — privacy rules: **PASSES, secondarily and on grounds the schema does not already cover**

The refused row failed here because *"a certificate names an address and an installer; so does every
other row on this schema."* That is a fair description of the schema default and it is **not** a
description of this row. Three grounds, all now in `sensitivity_why`:

1. **The exposed third party is a stranger.** On every other row on this schema the exposed party is a
   client, a tenant or an occupier — someone in a relationship with the holder. Here the file
   routinely contains a **named neighbour's objection carrying their own home address**. That person
   is not a party to anything, has no relationship with the holder, and never consented.
2. **Enforcement correspondence is an allegation against the holder.** No other row on this schema
   carries material in which the holder is the accused. It changes the posture of the whole file and
   may co-activate the protected legal side.
3. **The file contains a complete internal layout of a real, addressed dwelling** — published
   alongside its address. An address here is not merely identifying; it is **locating**.

Set to `potentially_sensitive`, cautiously rather than precisely, because much of this material is
public record by design and the honest reading of a mixed row is the stricter one. `00`'s corpus
sentence names material of this kind — *"can include identity documents, account statements, tax
records, medical information, legal records, credentials, private correspondence, GPS metadata,
employment materials, and educational records."* **No P7 handling class is assigned; that is P7's.**

**Overall: STANDS on legs 2 and 3. Leg 1 withdrawn.** One passing leg suffices under §2; this row has
two, and says openly which one it lost.

---

## Files considered and rejected

The tempting false positives, and what discriminates each. A row that only lists what it holds has
not been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| `Building Regulations Completion Certificate - 18 River Court.pdf` *(the family's shared collision fixture; kept in the JSON as a **negative** example)* | Satisfies an authority letterhead, a completion declaration, a labelled address, and a `work_type` word from this row's own list — and still does not fire, because **the case is absent**: no acknowledgement, no discharge exchange, no inspection sequence. Stripped of its neighbourhood it is a document-type word plus an address, the exact reduction on which `compliance-certificate` was refused. Named identically by the schema anchor, by `construction-project` and by landed `finance.household-property`. |
| `Council letter.pdf` *(kept as a negative fixture)* | The never-alone made concrete. Same letterhead, same address, and it is as likely to be council tax, refuse, highways, housing or an employment matter. The council name concludes **nothing**. |
| A street-works permit, a scaffold licence, a skip permit, a hoarding licence | `government.permit-licensing`. Same issuer, same site, same reference shape. Discriminator: they license an **activity or an occupation of the public realm**, not building works under a planning or building-regulations regime. |
| A **party-wall award or notice** | Adjacent, real, and frequently filed in the same folder — and **not an authority document at all**. It is a surveyor's award between two private owners under a private statutory mechanism; there is no application, no reference issued by a body, and no conditions schedule. **No row on the roster owns it.** Recorded for R1c rather than annexed, because annexing it would be exactly the reflex this pass exists to resist. |
| An **EPC**, an EICR, a gas safety record | The refused row's material, and mostly a **sale and letting** document rather than a build one. No application reference, no authority issuer, no conditions. Routes to `finance.household-property` or Independent Records. |
| A **structural warranty** (NHBC and similar) | Reads like an approval and is **insurance**. Different issuer, different instrument, no statutory power. `finance.household-property` or `finance` proper. |
| `Householder guide to permitted development.pdf` *(kept as a fixture)* | Published guidance with no site, no reference and no applicant. Reading Inbox — *"papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* This is the clearest demonstration that this row is not detected by its vocabulary: the guide contains **every** context term and **no** evidence item. |
| A planning consultant's **fee proposal and appointment letter** | Genuinely this schema, and genuinely `quote-estimate`'s / `construction-project`'s: it is a professional instruction with a fee, not an application. The application it later produces is mine; the engagement that produced it is theirs. |
| A **development appraisal** priced on an assumed consent | `construction_property.development-appraisal`. Tense discriminates: an appraisal forecasts a scheme that may not happen; this row records a case that is actually running. A consent reference appearing as an *input assumption* in a spreadsheet is not this row's evidence. |
| An **objecting neighbour's own file** | Neither this row nor `government`. It is personal administration about somebody else's property. Independent Records, or Protected Records where it names them. |
| A council **tax bill**, a **housing benefit** letter, a **school place** decision | `finance`, `government`, `academic`. Identical letterhead, identical address, and — in the school case — even a decision word and an appeal right. The four-part structure is what excludes them: no application reference *about a site*, no conditions schedule. |
| An architecture **dissertation** on planning policy | `academic` / Reading Inbox. Full vocabulary overlap, zero evidence overlap. |
| A **portal screenshot** *(kept as a fixture)* | May be the holder's case, a neighbour's, or idle browsing. Temporary Screenshots, and the JSON records the wrong conclusion explicitly so it is not drawn — including that *"the system must not mistake the absence of EXIF for proof that an image is a screenshot."* |

---

## The collision fixture, both directions

**Inbound — a file that would wrongly fire this row:**
**`Building Regulations Completion Certificate - 18 River Court.pdf`.** Argued above and carried in
the JSON as a negative example. It is the family's shared fixture and the reading here is identical
to the readings on the schema anchor, on `construction-project` and on landed
`finance.household-property`. **Nothing is contradicted.**

**Outbound — a file that must not be lost *to* this row:**
**`Objection letter - 22 River Court.pdf`.** It cites the application reference, names the site, and
sits in the middle of the case — every reason to sweep it in. It must not be swept in *silently*: it
carries a **named private individual who is not a party**, and their own home address, which is a
**different address from the site**. The JSON's `must_not_conclude` names that trap directly ("two
addresses appear and only one is the subject"), and the file falls through to **Protected Records**
rather than to this row's default when the row does not fire. The protective ordering (CONNECTION §4
step 5) wins over the join.

**The reference itself, named on both sides:** `24-01187-FUL`, on
`Decision Notice - 24-01187-FUL - 18 River Court.pdf`. It appears on the authority's copy and the
applicant's copy identically and **discriminates nothing**. It is named here, and named in the schema
anchor's `government` row, so that the reciprocal can be checked rather than asserted.

---

## Reciprocal boundaries, both directions

| Neighbour | This row must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `government.planning-application` *(schema unwritten)* | an issuing authority's own case file, officer report, statutory power or decision-making record | an applicant's or agent's submission, its acknowledgement, and the conditions the holder must discharge | `Decision Notice - 24-01187-FUL - 18 River Court.pdf` |
| `government.permit-licensing` *(schema unwritten)* | a permit or licence for an activity or an occupation of the public realm | an approval of building works under a planning or building-regulations regime | a scaffold licence for the same site as the consent |
| `construction_property.construction-project` **(landed)** | a contract sum, a programme, an interim valuation, an instruction, a practical-completion certificate, a final account | an application reference, a decision word, a conditions schedule, a discharge exchange, a statutory inspection visit | `Condition 4 discharge - drainage details.pdf` |
| `construction_property.drawings-revisions` **(landed)** | the sheet itself, its title block, its revision and its transmittal register | the pairing of a sheet with an application reference and a form's drawing schedule | a `for planning` elevation sheet inside an application pack |
| `construction_property.block-management` **(landed)** | the recurring management cycle of one building with leaseholders in it | an application case with a reference, a decision and conditions, merely because the block generated it | the same roof renewal's paperwork — a per-evidence-item mutex, not a claim about the works |
| `finance.household-property` **(landed)** | a householder's own durable record of their own home, with no case around it | a live application or inspection sequence with an authority, merely because the property is a house | `Building Regulations Completion Certificate - 18 River Court.pdf` |

The two `government` seams are authored **one-way here** — that schema does not yet exist. The
three `construction_property` seams are two-way: `construction-project` deferred to this row in prose
and now receives an edge back; `block-management`'s and `drawings-revisions`' own wordings are adopted
without amendment so the family does not diverge. **R1c owes the `government` reciprocals**, and the
fixture bytes are named on this side so they can be checked.

---

## Neighbours considered that did **not** get an edge

- **`legal.personal-legal-matters` (landed)** — an enforcement notice or a planning appeal can become
  a dispute. No edge authored: the discriminating evidence (a proceeding, a tribunal caption, a
  represented party) is already stated on the legal side, legal is a safety domain and protects first,
  and a one-way copy would add noise rather than a join. *(Preserved from the gist memo; still right.)*
- **`business_operations.compliance-audit`** — organisational compliance evidence overlaps, but the
  schema row already carries the `business_operations` collision at family level; a row-level copy
  adds nothing.
- **`construction_property.development-appraisal`** — considered and rejected as an edge rather than
  as a file. A consent reference inside an appraisal is an *input assumption*, not a case member, and
  no document is genuinely contested between them. Recorded here so the omission is visible.
- **`identity`** — a statutory application form carries the applicant's personal details and
  declaration. The relationship is **protection, not a shared reading**, and is handled through
  `sensitivity` and the Protected Records fallthrough, exactly as the schema anchor does it.

---

## `proposed_fields`

**None**, and this is unchanged from the gist pass and re-examined rather than inherited.

The row relies on the schema row's existing `property` proposal (NJ-CP-1) and its `instruction`
proposal. An **`application_reference` key was considered again this pass and again not proposed**:
it is a short structured token in the same space as case, matter, claim and account references across
the roster, it would carry a `possible` ceiling from filename evidence and a `direct` one only from a
labelled slot, and it has **no destination value** — nobody browses to a reference number they cannot
remember. The schema row's `instruction` proposal already covers the container concept if R1c takes
it. **Seconding an existing family proposal rather than minting a variant is the instruction, and it
is followed.**

---

## NEEDS-JOSEPH

- **NJ-CP-6** *(preserved, and widened this pass)* — **side-undecidable authority documents.** Where
  the holder's role cannot be established, abstain on **both** sides rather than defaulting to either.
  Authored one-way here; every `government.*` row owes the reciprocal. **Widened:** the
  **approved inspector** is a fourth role — a private body discharging a statutory function for a fee
  — which no row on the roster owns. Its instruction file is this schema's; the notices it issues read
  as `government`'s. R1c should route it rather than let either family annex it.
- **NJ-CP-7** *(new this pass)* — **the case threshold.** This row now requires a *case*, not a
  document. Alternatives, with costs: **(a)** require the application reference to recur across at
  least two distinct members — checkable, but it is a count, and `_CONTRACT` rule 3 forbids this pass
  inventing one; **(b)** require one non-decision member (an acknowledgement, a discharge or an
  inspection) alongside the decision — no number, and weaker; **(c)** leave it to activation
  confidence, which risks re-admitting the refused row through the back door. **This memo takes (b)
  as its stated posture and flags (a) for R1c.**
- **Jurisdiction — recorded, not asked.** Every term in `proposed_context_terms` is one regime's
  vocabulary. D4 already settles that jurisdiction is a **value**, never a field or a dimension, so
  the row is correct as written; it is simply the row where a single-jurisdiction gazetteer will most
  visibly under-serve everyone else. R4 owns the gazetteer.
- **Party-wall material** has no owner on the roster. Recorded, not annexed.
- Inherits **NJ-CP-1** (if R1c refuses `property` a canonical key, this schema's own leg 1 loses its
  strongest limb).

---

## Audits

- `python3 -m json.tool` on the JSON: **parses.**
- Key set compared against the landed sibling `construction_property.construction-project.json`:
  **identical, no symmetric difference.**
- All **25** curly-quoted spans in the JSON grep back out of
  `planning/00-database-agent-product-design.md` **verbatim** (whitespace- and curly-quote-normalised):
  **0 missing.** The 3 added this pass are the generic-hub sentence and two uses of the sparse-file
  sentence.
- Both `government.*` ids named in `collides_with` confirmed present in `ROSTER.md` §12
  (`gov.planning-application` → `government.planning-application`;
  `gov.permit-licensing-authority` → `government.permit-licensing`).
- `fields: []` and `proposed_fields: []` confirmed; **no canonical key minted, no field row written.**
- Files written: **only** this row's two. Nothing else touched.

---

## What changed in this pass

**Preserved unchanged** (verified-but-shallow, and right):

- The central argument that the load-bearing boundary is **side, not topic**, and that the application
  reference discriminates nothing. This was the gist draft's best idea and it is now the spine of the
  `government` section.
- All 11 `recognition.deterministic` entries and their precondition; all 4 `needs_llm` entries; the 7
  original `never_alone` entries; all 33 `proposed_context_terms`; all 12 `work_types`; the 7 original
  `grouping_reasons`; all 6 `falls_through_to` entries; the `file_kinds` block; 9 of the 10 original
  `file_examples`.
- The four original `collides_with` edges (`government.planning-application`,
  `government.permit-licensing`, `finance.household-property`, `construction_property.drawings-revisions`),
  unamended.
- The decision to propose **no fields**, re-argued rather than inherited.
- The refusal of an edge to `legal.personal-legal-matters`.

**Reversed** (stated, not silent):

- **Leg 1 of the node test is withdrawn.** The gist memo counted the row's property-first dimension
  recommendation as support. The deepened schema anchor says reversal earns nothing, and following the
  default therefore earns less. The row now rests on legs 2 and 3 and says so.

**Narrowed:**

- From "authority documents about building" to **an application case**. A lone authority document
  with no case around it no longer fires this row. Reflected in `one_line`, in a new `needs_llm`
  entry, and in the fixtures. Filed as **NJ-CP-7**.

**Added:**

- The three named failure modes answered head-on, before the node test.
- The node test argued **leg by leg against the family's stated default**, including the leg it fails.
- **The `government` seam as a full role table**, written so that family's author has something to
  write against — plus the unowned **approved inspector** role.
- **Files considered and rejected** — 13 named false positives, none previously present.
- **A collision fixture in both directions**, with the inbound one being the family's *shared* fixture
  now named identically on four rows.
- **Reciprocal boundaries** as a two-direction table with shared fixture bytes.
- Two `collides_with` edges the row owed: **`construction_property.construction-project`** (the
  sibling deferred in prose and got nothing back) and **`construction_property.block-management`**.
- A positive fixture, `Final certificate - 24-01187-FUL - 18 River Court.pdf`, so the same certificate
  appears as both a firing and a non-firing example and the difference is the case.
- Two `never_alone` entries: the **authority email domain** (with `00`'s generic-hub sentence) and the
  bare **stage word**.
- A `grouping_reasons` entry carrying the sparse-file rule, so a group cannot enrich its members.
- A sharpened `sensitivity_why` resting on three grounds the schema default does **not** cover.

**Not done, deliberately:** no padding. The row is genuinely narrower than the family spine and its
memo is correspondingly shorter than the 38–46KB anchors. It is not inflated to meet a number.
