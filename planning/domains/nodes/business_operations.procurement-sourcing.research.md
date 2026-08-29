# business_operations.procurement-sourcing — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the gist draft of 2026-08-24. The gist draft's arguments were sound
and are **preserved in their own terms**; what is added here is the node test argued leg by leg
against the family's now-explicit default template, the row's position inside the settled three-row
counterparty boundary, files considered and rejected, a two-directional collision fixture, reciprocal
boundaries checked against the neighbours' own landed files, and the open questions stated with their
alternatives. A *What changed in this pass* section closes the memo.

**Verdict: the row stands, and the gist verdict is confirmed rather than reversed.** The dispatch
asked me to consider two charges honestly and to treat refusal — or handing the coverage to a sibling
— as a success. I did, at full strength; both charges fail, and the reasons they fail are the most
interesting thing in this memo. They are argued in *The two charges* below, before anything else,
because a reader who does not accept that section should not accept the rest.

---

## Sources

- `planning/00-database-agent-product-design.md` — authoritative. **Every quotation below was
  machine-verified verbatim with `grep -F` against this file.** Nothing is paraphrased inside quote
  marks.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/_CONTRACT.md` (rules 6, 10, 11, 15);
  `planning/domains/CONNECTION.md` §2 (node test), §4 (activation, step 2 never-alone), §9 (failure
  modes); `CONNECTION-EXAMPLES.md`.
- `planning/domains/roster.json` — id, kind, `schema_id`, neighbours; **every edge id in the JSON was
  re-checked against this file this pass**, including `government.public-procurement`,
  `manufacturing.supplier-qualification`, `retail_hospitality.supplier-order`,
  `construction_property.quote-estimate` and `legal.leases-agreements`. All exist.
- `planning/domains/canonical_fields.json`; `src/evidence_shape/vocabulary.py` (`SOURCE_TYPES`).
- `planning/overnight/council/DECISION-BRIEF.md` — J-IND, D1, PR-6, all ratified and not re-debated.
- `ROSTER.md` §4 + Appendix A, lines 555 and 822.
- **The schema anchor, read first and closely:** `business_operations.research.md` (46KB), for the
  default template stated for the 24 siblings and the never-alone principle generalised for them.
- **Neighbours' own landed files, read before writing any boundary:**
  `business_operations.organisational-records.research.md` (the family's refusal),
  `.partnerships-bd.research.md` (36KB, which settled the three-row counterparty question),
  `.vendor-management.research.md`, `.contract-administration.research.md` (39KB).

---

## The two charges, taken at full strength

The dispatch put two charges. Neither is a straw man and I did not treat them as one.

### Charge (a): procurement is an *activity*, not a filing world — a `work_type`, not a node

This is the charge the schema anchor itself teaches siblings to fear, and it names this row while
doing it:

> **Differing in business function is not automatically a difference**: "procurement", "facilities",
> "risk" and "IT asset" are *values of a function dimension*.

So the anchor puts "procurement" on the list of words that are *not* nodes. If the row's entire claim
were the word, the charge would win outright and I would refuse. It is not, and the anchor's very
next sentence says what would save it:

> What earns those rows their node is a distinct **structure** — a tender evaluation matrix, an asset
> register with serials and lifecycle dates, a risk register with likelihood/impact scoring columns —
> not the topic word. This is the single most important sentence in this memo for the sibling authors,
> and it is the sentence that would have prevented the 574.

**The anchor names this row's structure by name, as the first of its three examples.** That is not
this row asserting its own case; it is the schema row, written by another agent, choosing *the tender
evaluation matrix* as its paradigm of a structure that earns a node. Charge (a) therefore fails on the
family's own stated test, and it fails for a reason I can state independently of the anchor's
endorsement: the evaluation matrix, the clarification log and the solicitation's reference-plus-
deadline-plus-schedule triple are **document structures with labelled slots**, not topic words. The
family rule is that every detection signal must "pair a **structure** with a **labelled slot**". This
row's signals do:

| Structure | Labelled slot that pairs with it |
|---|---|
| criteria × suppliers scoring grid with weightings and a total column | the solicitation reference in the sheet header; evaluator initials on the moderation tab |
| numbered bidder questions with dated answers issued to all | the reference; the issue date; the anonymised bidder column |
| instructions-to-bidders section over a numbered specification schedule | the reference repeated per page; the submission deadline with a time |
| line items with quantities and unit prices under an ORDER framing | a labelled PO number; an authorised-by line; a delivery address |

None of those four is an entity name, a business vocabulary word, or a bare document shape. The
family's disqualifier is not met.

### Charge (b): it is `vendor-management` seen at an earlier moment, so the counterparty settlement already covers it

This is the stronger charge, and it is the one I spent the most of this pass on. It fails for a
reason that also fixes the row's position in the family, so it gets its own section.

---

## Where this row sits relative to the settled counterparty boundary

`partnerships-bd` settled the three-row question and I read that settlement before writing a word of
this. Its holding, in its own words: **"Verdict: three rows, not one."** Its separations are
*whether the relationship exists yet*, *what the register is a register of*, and *whether the world
has a terminal state that is nothing*. It accepted the premise the objection rests on — that role is
a field value and no row may rest on it — quoting `00`:

> "The system must separate roles that happen to contain the same entity type."

**This row is not inside that settlement, and it does not contradict it. It sits outside it, because
it is not a counterparty-anchored row at all.** That is the precise answer the dispatch asked for,
and it is worth stating as sharply as possible:

> `partnerships-bd` holds relationships that **do not exist yet**. `customer-account-management` and
> `vendor-management` hold ones that **do**. All three are anchored on **one counterparty**. This row
> is anchored on **one requirement** — and it holds **several counterparties at once, none of whom is
> yet the holder's anything, and most of whom never will be.**

Three consequences follow, each checkable against a real file.

**1. Cardinality is the discriminator the settlement did not need and this row does.** Every one of
the three counterparty rows has cardinality one: an account plan is about one customer, a scorecard
about one supplier, a pipeline row about one opportunity. A sourcing file's *characteristic* document
— the evaluation matrix — is **unreadable at cardinality one**. Delete every row but the winner's and
the file stops being an evaluation matrix and becomes a summary. That is the same shape of argument
`partnerships-bd` used against merging the pipeline into the registers ("delete those four columns and
the file stops being a pipeline"), applied one level up, and it is not available to any of the three.

**2. The relationship-existence test cuts *across* this row, not along it.** `partnerships-bd`'s first
separation says its documents "can only exist *before*" a relationship and its siblings' "cannot
predate one". A sourcing file **contains both kinds simultaneously**: the specification and the
clarification log predate any relationship; the award letter creates one; and the purchase order that
follows presupposes it. A world whose single bounded object spans the whole existence transition is
not a slice of any of the three worlds the settlement partitioned. It is the **transition event
itself**, which is exactly the object the settlement's three rows hand off across without holding.

**3. `vendor-management` has already rejected charge (b) from its own side, and I am not overriding
it — I am endorsing it.** Its landed memo states, unprompted, where it thinks a merge should go if one
happens:

> "if R1c collapses anything in this family, the candidates to merge are **vendor-management and
> contract-administration**, not vendor-management and procurement-sourcing — because a sourcing event
> genuinely ends, and a relationship and its contract genuinely do not."

That is the neighbour, writing about itself, declining the merge charge (b) proposes. The reciprocal
edge in this row's JSON now says the same thing in the same terms and cites it.

**The decisive form of the argument, borrowed from the family's refusal.** `partnerships-bd`'s
strongest move was to ask what the merged row's anchor would be, and to find it was *an external
organisation the holder has dealings with* — the anchor `organisational-records` was refused for. Run
the same test on charge (b)'s merger. Merge sourcing into vendor management and the merged row's
anchor is *a supplier*. But at the moment of issue **there is no supplier**, and at the moment of
evaluation **there are five**. The merged row would either have to activate on a counterparty that
does not exist yet, or activate five times on one competition, or — the actual outcome — fall back to
activating on a supplier name, which is the never-alone anchor the family already refused a row for.
So charge (b), like the merge case the settlement rejected, does not simplify the family: it produces a
row that fires wrongly or not at all, and destroys one that fires cleanly.

**Stated reciprocally, and this is a recommendation for R1c, not an edit to a neighbour:** if R1c
accepts this section, the reciprocal sentence owed on `vendor-management` and `partnerships-bd` is
that *procurement-sourcing is not a fourth counterparty row and must not be read as one* — its anchor
is the event reference, and a counterparty branch over it would be a dimension-time answer, exactly as
`partnerships-bd` concluded for the other three.

---

## The node test, leg by leg, against the family's stated default template

`CONNECTION.md` §2: a template row exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The schema anchor
states that default explicitly so siblings can be measured against it:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* → the
> **governance body, project, contract, or account** the material belongs to → the **fiscal period** →
> the **document function**. Not time-first.

### Leg 1 — detection signals: **passes, decisively**

The default template's implied detection is the schema's own: business-shaped material carrying an
organisation, a cycle and a document function. This row's signals are narrower than that in a way that
is checkable rather than rhetorical. Two of them exist **nowhere else in the catalogue**:

- **The clarification log.** Numbered questions submitted by competing parties, answered with dates,
  and issued to *all* of them — the anonymised-questioner column is the giveaway. No other situation in
  any of the ten schemas produces this document, because no other situation has a set of mutually
  blind parties who must be kept equally informed. I looked for a counter-example and could not find
  one: an FAQ has no questioners, a Q&A minute has named ones, a support ticket has one.
- **The evaluation matrix at cardinality > 1**, argued above. `00` licenses reading it structurally:
  *"Tables matter because resumes, forms, applications, invoices, and administrative documents often
  place their most useful information in cells rather than body paragraphs."*

Two more are strong but not unique, and I say so rather than overclaiming: the solicitation triple
(reference + deadline + numbered schedule) is shared with `government.public-procurement`, which is
this situation under statute; and the PO structure is shared with `retail_hospitality.supplier-order`,
which is this shape at replenishment volume. Both are edged, both discriminated, and neither is
claimed as exclusive.

### Leg 2 — recommended dimensions: **differs, but the difference is prose-only under PR-6**

`template.dimension_order` is `[]` by binding contract — `business_operations` declares no field rows,
so no dimension can branch. Stated honestly: **this leg cannot be scored at all in the current pass**,
for this row or for any of its 24 siblings, and I will not pretend it carries weight it cannot.

What the row *would* recommend, held as prose, and where it genuinely departs from the anchor's
paragraph:

> organisation *(conditional, and seeded ineligible for the anchor's own reason)* → the **sourcing
> event, identified by its reference** → the **stage** of the event (issued / responses / evaluation /
> award) → and, **only inside the responses stage**, the **supplier**.

Three departures from the default, each with a reason:

1. **The event replaces "governance body, project, contract, or account."** An event is bounded and
   dies; the anchor's level-two objects persist. This is a real difference in kind, not a rename.
2. **`fiscal_period` drops out of the order entirely.** The anchor puts it third and justifies it by
   the parent-context rule. Here a fiscal period is *noise*: a competition can straddle two of them
   and its reference identifies it better than any year does. This is the sharpest departure and I
   flag it as such — a sibling that quietly keeps the anchor's paragraph has not differed; this one
   removes a level and says why.
3. **A `stage` level the anchor does not have**, and a **supplier level deliberately demoted below
   it.** Supplier-first scatters one competition across its bidders and hides the thing being decided.
   `00`: *"The recommendation should follow the practical rule that a parent dimension should provide
   the context required to understand the child."* A pricing schedule is meaningless without knowing
   which competition and whose response it is — the `HW 3.pdf` argument exactly.

**Not time-first**, and this row explicitly does not claim the exception the anchor reserves to
capture-based media, even though a sourcing event is unusually well bounded in time. `00`: *"project,
function, or subject usually comes before time"*. The anchor's warning — "A sibling claiming
`time_first: true` is claiming the photos exception without the photos evidence" — is accepted.

The `organization` level is **seconded from the anchor, not re-minted**, exactly as the dispatch
directs: conditional, template-time, and seeded ineligible for `00`'s own validator reasons —
*"create meaningless one-child levels"* and *"use an author or organization merely as a collector"*.
Likewise this row proposes **no `fiscal_period` variant**; it simply argues the level out of its own
order and leaves the key to the family.

### Leg 3 — privacy rules: **passes, and on a distinct kind of sensitivity**

This is the leg most siblings pass weakly. This row passes it on something structurally unusual:
**most of the file is other organisations' confidential commercial material held in trust, and the
obligation is fairness rather than privacy.** An unopened bid is protected not because it identifies
anyone but because opening it early corrupts a competition. Nothing else in `business_operations` has
that. Layered on top there *is* ordinary personal data — bidders' staff CVs inside submission
archives, and named evaluators recorded against the judgements they made about other organisations —
which lands inside the corpus `00` describes, one that *"can include identity documents, account
statements, tax records, medical information, legal records, credentials, private correspondence, GPS
metadata, employment materials, and educational records."*

The operative limits are `00`'s, and this row asserts none of its own: *"Protected material should not
be included in cloud-model prompts by default, should not display raw content in general group
summaries, and should not be moved automatically without a user policy that explicitly permits it."*
The row assigns only the catalogue value `potentially_sensitive` and **does not** assign, alias, rank
or infer a P7 handling class.

**Overall: three legs offered, two scored, both passed; the third unscorable this pass and said so.**

---

## Files considered and rejected

A row that only lists what it holds has not been researched. These were considered as candidate
evidence for this row and rejected, with the reason.

| Considered | Why it is **not** this row's evidence |
|---|---|
| `Meridian invoice 33012.pdf` *(kept as a fixture)* | A demand for payment is a bookkeeping transaction **even when it quotes a PO number**. The PO reference is the trap: it makes the invoice look like the event's own file. `finance.small-business-bookkeeping` owns it. |
| `Scan_20260212_quote.jpg` *(kept as a fixture)* | One quote, no competition, no reference, no deadline. A quote is not a sourcing event; `construction_property.quote-estimate` is the nearer home for a trade quote. |
| `Pricing model v4.xlsx` *(new fixture this pass)* | The quietest false positive and the most common file in the world: a costing workbook with no reference, no supplier and no deadline. Evidence of nothing. `business_operations.budget-forecast` is at least as likely, and so is a supplier's internal cost model. |
| `Call-off order - Framework FA-2024-03 - Lot 2.pdf` *(new fixture this pass)* | The framework call-off, which the gist draft named and deliberately left in prose "at gist depth". It is now a fixture because it is the cleanest statement of the signature boundary: the competition happened **once**, when the framework was let; this order points **backwards** to an executed instrument, which is `contract-administration`'s own stated discriminator. |
| `PQQ response - ITT-2026-014.docx` *(new fixture this pass)* | Not rejected — added as the **two-directional** fixture, being the same bytes `partnerships-bd` names from its side. |
| `Meridian - certificate of insurance 2026-27.pdf` | Collected during a competition and reused afterwards. It is `vendor-management`'s: a certificate proves a party is safe to deal with, and says nothing about a competition. Rejected from this row's examples so as not to steal it. |
| `FW updated bank details - urgent.eml` | Considered because supplier bank details do arrive during sourcing. Rejected outright: `vendor-management` holds it and makes it the single most important example in its file, for good reason. This row must not touch a payment fact. |
| A **reverse-auction portal event log** | Real, and genuinely this situation. Rejected as an example because it is instrument-specific — a log of one platform's bidding rounds — and the signals it would add duplicate the solicitation triple. Left out rather than padded in. |
| A **supplier's unsolicited proposal** | Looks like a bid, arrived without a competition. It is `partnerships-bd`'s from the sender's side and, from the receiver's side, a document with no event to belong to. Handled in `needs_llm` rather than given a fixture. |
| A **conflict-of-interest declaration signed by an evaluator** | Genuinely produced by this situation and nowhere else. Not given a fixture only because its lesson (named individuals recorded against judgements) is already carried by the evaluation matrix's moderation tab; it is folded into `work_types` reasoning instead. Flagged here so the omission is visible rather than silent. |
| A **grant-funded purchase file** | Extra evidence duties, same situation. `nonprofit.grant-reporting` inherits the reporting, not the buying. No edge; the `government` edge already covers the regulated case. |

---

## The collision fixtures, in both directions

The addendum asks for a file that would **wrongly fire** this row, and a file that must **not be lost
*to*** it. This row has one of each, plus one file that is genuinely both directions at once.

**Wrongly fires → `Meridian invoice 33012.pdf`.** Supplier name, line items, a total, and a PO number
in the reference line. Everything a naive procurement detector wants. What discriminates it: an
**invoice number, a tax treatment, payment terms and bank details**, and the framing of a *demand for
payment* rather than an *order*. Named on both sides: `finance.small-business-bookkeeping`'s side owns
it; this row's `collides_with` states the same discriminator.

**Must not be lost to this row → `Pricing model v4.xlsx`.** A budget owner's cost model sitting in the
same folder tree as a live tender. If this row activates on rate-and-quantity structure, it eats the
finance and planning material of the whole organisation. What discriminates it: the **absence** of a
reference, a deadline and a counterparty — and the presence of a fiscal period, a cost-centre
breakdown or a variance column, which are `budget-forecast`'s. New `collides_with` edge this pass.

**Both directions at once → `PQQ response - ITT-2026-014.docx`.** The same bytes exist in the buyer's
file and in every bidder's, and the document is silent about which holder has it. This is the file
`partnerships-bd`'s deepened memo names for the same purpose, in the same words, from the other side.
It is not resolvable from content; only **possession of the evaluation apparatus** resolves it, and
`00` says why the question is a purpose question rather than a topic one: *"Topic answers what a file
is about, while purpose answers what the file was for."*

---

## Reciprocal boundaries

Stated in both directions. Where a neighbour has landed, its file was read first and is not
contradicted; where I diverge or the neighbour is silent, that is said openly.

**↔ `business_operations.partnerships-bd`** — the mirror-image seam. That row's file preserves this
boundary in this row's own terms and names `PQQ response - ITT-2026-014.docx` as the shared bytes.
Reciprocated unchanged. **Added this pass, and it is an addition rather than a contradiction:** this
row is *not* a counterparty row, so it does not sit inside that row's three-row settlement and makes
no claim on it. Direction A: possession of several responses, a scoring matrix and an award to issue →
this row. Direction B: one organisation's own outbound proposal, win themes, pipeline position and
pricing approvals → that row. A pricing schedule alone → neither.

**↔ `business_operations.vendor-management`** — existence and cardinality. That row: a solicitation
reference, a deadline or an award is this row's; an onboarding form with a remittance block, a
supplier register with a relationship owner, a scorecard, renewal diligence is that row's.
Reciprocated, with the narrowing added this pass: **one relationship measured** → that row; **several
candidate relationships compared, none of them yet real** → this row. That row's own recommendation
against merging with this one is endorsed rather than argued with. Same bytes both sides: a supplier
diligence questionnaire, which is collected in a competition and re-used in a relationship.

**↔ `business_operations.contract-administration`** — the boundary is **the signature**, and both
sides now say so identically. That row quotes this row's gist wording back verbatim and adds the
one-word narrowing this row accepts: *anything whose reference points backwards to an executed
agreement* is that row's. Same bytes both sides: a purchase order — that row carries `PO-2026-0331.pdf`
as *"procurement's output, this row's call-off evidence, and an accounting document at once"*, which
is the same three-way statement this row's `open_question` makes from its side. **No disagreement
found.** The new call-off fixture here is the case that narrowing was written for.

**↔ `finance.small-business-bookkeeping`** — order versus payment. Direction A: an ORDER framing with a
delivery address and an authorisation → this row. Direction B: a demand for payment with an invoice
number, tax treatment, payment terms and a posting reference → bookkeeping. Same bytes both sides:
`Meridian invoice 33012.pdf`. **Note stated reciprocally rather than settled:** NJ-BO-7 below could
move the whole PO half across this seam.

**↔ `government.public-procurement`** — this situation under statute. Direction A: a published contract
notice, a named regulated procedure, a transparency publication or a statutory standstill → the
government row. Direction B: a private organisation's own competition, however formal → this row.
That row has not landed; the boundary is authored from this side only and R1c should check it when it
does.

**↔ `business_operations.budget-forecast`** *(new edge this pass)* — argued above. Reciprocal
recommendation for R1c: that row should carry the mirror sentence, since the fixture is a budget file
this row must not take.

**↔ `manufacturing.supplier-qualification`**, **`construction_property.quote-estimate`**,
**`retail_hospitality.supplier-order`** — carried forward from the gist draft unchanged; their
discriminators (a part number and a process qualification; a site and measured quantities; repeating
replenishment against a catalogue) were re-checked against the roster and stand. None of the three has
landed a file; all are authored from this side only.

### Neighbours considered that did **not** get an edge

- **`nonprofit.grant-reporting`** — grant-funded procurement carries extra evidence duties, but the
  buying is the same situation and the `government` edge already covers regulated procedure. The
  *reporting* is that row's; the *event* is this one's.
- **`logistics.*`** — freight tendering is this row in a sector. A sector is not a node. No edge:
  the confusion there is about *what* is being bought, and that is a value.
- **`hr.onboarding-offboarding` / `hr.training-development`** — a recruitment panel and a training
  provider are both procured. Rejected for the same reason `vendor-management` rejected them: same
  situation, different category, and a category is a value.
- **`legal.leases-agreements`** — **promoted to `also_holds_with`, not `collides_with`**, and that is a
  deliberate distinction rather than a soft call: a letter of acceptance really is the award document
  *and* the instrument, and `00` licenses the double reading — *"One file may hold facts from more than
  one domain without losing information."*
- **`business_operations.it-asset-inventory`** — likewise `also_holds_with`. A PO for laptops is the
  acquisition record of an asset and the last act of the event, both truly. That row already carries
  procurement-facing signals from its side, so the reading is reciprocated in substance.
- **`business_operations.compliance-audit`** — likewise. In an audited or grant-funded organisation the
  sourcing file *is* the audit evidence; a second purpose attaches to unchanged bytes. *"A file may
  validly belong to more than one accepted group"*.

---

## The archive case, and why it gets its own paragraph

`tender_submission_ITT-2026-014.zip` is not a decorative example. `00` uses an archive of exactly this
shape as its worked illustration of purpose-coherence: *"A ZIP file named submission.zip may contain a
transcript, personal statement, resume, certificate, and form, which is meaningful evidence of a
purpose-defined application packet even when the outer archive name is vague."* A tender submission is
the commercial twin of that packet — a form of tender, a method statement, a pricing sheet, two
certificates and a CV set — and it is why this row's `grouping_reasons` lead with *"The documents are
content-incoherent but purpose-coherent."*

Three constraints follow and are written on the row:

1. Members are extracted as their own files; the manifest does **not** license a single domain for the
   whole archive. *"the normal scan should never extract archive contents to the filesystem"*.
2. Tender portals routinely encrypt submissions until the opening deadline, so the unreadable case is
   **normal here rather than exceptional**: *"Password-protected, malformed, nested, or oversized
   archives should be marked as unreadable or partially inspected rather than forced open"*. Hence the
   `Unsupported or Encrypted` fall-through, which is not a hedge on this row but the expected outcome
   for a live competition.
3. The CVs inside belong to named individuals at another organisation. They are the reason this row's
   sensitivity is not merely commercial.

---

## Grouping, and the trap specific to this row

The strongest grouping case in the family, and also the most dangerous. The event group — one
specification, its annexes, every response, the clarification log, the scores and the award — is held
together by **purpose**, and that is legitimate. What is not legitimate is the group that a naive
implementation would actually form: **one supplier's name across everything in the corpus.** `00`'s
stop rules strike it directly — a group must not form *"when one high-frequency entity acts as the only
bridge"* — and the family's own refusal generalises the same point from *"A university name alone
should not create a group because Columbia can appear as an authoring school, course provider, target
institution, employer, research venue, or merely a cited organization."*

That is now written as a `never_alone` on the row in those terms. The practical consequence: a PO, an
acknowledgement and a delivery note grouping is real and useful, and it is the single most likely
place for a supplier fact to leak onto an unrelated invoice from the same company. *"The graph does not
automatically copy those missing facts onto sparse files."*

**No group at all remains a valid outcome** and is stated on the row: one quote emailed by a supplier,
with no competition around it, is a standalone record.

---

## proposed_fields

**None.** PR-6 forbids field rows on this schema and D1's deferral stands; `fields: []` and
`proposed_fields: []`.

Three keys this row would want if the deferral were lifted, recorded as prose for R1c so the demand is
visible without minting anything:

- **`organization`** — **seconded from the schema row's proposal**, not re-proposed, and with the
  anchor's conditionality and destination-ineligibility accepted unchanged.
- **`fiscal_period`** — **seconded, and simultaneously argued out of this row's dimension order.** The
  key is right for the family; the level is wrong for this row. Both statements can be true and R1c
  should have them.
- **A counterparty-role key** — wanted here too, but **deliberately not proposed**, and the reason is
  the interesting one. `vendor-management` recorded (NJ-BO-VM-2) that the schema row assigned the
  `supplier` proposal to `contract-administration`, that `contract-administration` landed with
  `proposed_fields: []`, and that the key is therefore **proposed by nobody**; `partnerships-bd`
  escalated the same gap as NJ-BO-PB-1, now load-bearing for four rows. Adding a fifth claimant from
  the row that has the *weakest* claim — this row's anchor is not a counterparty at all — would be the
  duplicate-vocabulary failure those rows were guarding against. **This row therefore adds pressure,
  not a proposal**, and the pressure is a distinct one worth recording: whatever key is minted must
  tolerate **several counterparties on one object at once**, which a per-file `supplier` slot does not.

`proposed_context_terms` are carried forward unchanged from the gist draft. They are proposals; `00`
did not list them and the row does not pretend otherwise.

---

## NEEDS-JOSEPH

- **NJ-BO-7 · Does the purchase order belong to the event or to the money?** *(carried forward,
  sharpened, still the row's central open question.)* A PO is the last act of a competition for a large
  purchase; for most small organisations POs are a high-volume accounts-payable stream with no
  competition behind them at all. The roster hint folds `biz.procurement-po` in here and the audit
  trail from requirement to order is genuinely what users want held together — but the routine half is
  a large, transactional pile that would drown a row about tenders.
  **Alternatives and their costs:** (i) *keep as now* — audit trail intact, cost is that routine
  reordering lands in a tender row; (ii) *split at competitive-versus-routine* — matches how the
  material actually behaves, cost is that the split point is a judgement no evidence in the file
  settles, so it becomes a user-policy question; (iii) *move the PO half wholesale to
  `finance.small-business-bookkeeping`* — cleanest for the routine case, cost is that it severs
  requirement-to-order for the competitive case, which is the thing worth keeping. **Recommendation:**
  (ii), as a user-facing setting rather than a roster decision. Stated reciprocally:
  `finance.small-business-bookkeeping` and `retail_hospitality.supplier-order` are the rows that would
  inherit the routine half, and the collision signals on both are authored so the question is visible
  from either side. `contract-administration` names the same bytes as a third reading.
- **NJ-BO-PS-2 · Is `government.public-procurement` a separate row or this row under statute?**
  *(new this pass.)* The two share the entire document set; the government row adds notices, standstill
  and publication duties. **Alternatives:** (i) *two rows* — as the roster has it; cost is a boundary
  that must be maintained on evidence which is often absent from the file itself, since a private
  tender and a regulated one look identical until you find the notice; (ii) *one row with a
  regulated-procedure value* — cost is that the publication duties are a genuine privacy inversion
  (public procurement documents are *meant* to be published, this row's are *meant* to be
  confidential), and a single row would have to hold both postures. **Recommendation:** keep two, on
  the privacy inversion, which is a leg-3 difference rather than a vocabulary one. Not settled here
  because that row has not landed and I will not pre-empt its author.
- **NJ-BO-PS-3 · The counterparty-role key must survive multiplicity.** *(new this pass; a rider on
  NJ-BO-PB-1 rather than a new question.)* Whatever key R1c mints, this row needs it to express
  *several counterparties on one object, with the winner unknown until an award exists*. A per-file
  `supplier` slot cannot. Flagged because the four rows currently pressing for the key all want
  cardinality one, and a key designed only for them would silently exclude this row.

---

## What changed in this pass

**Preserved, unchanged, because the gist draft got them right:** the anchor on the sourcing event;
the `partnerships-bd` mirror-image argument and its *possession of the evaluation apparatus*
discriminator (which `partnerships-bd`'s own deepened file explicitly kept "in its own terms"); the
`vendor-management`, `contract-administration`, `finance`, `government`, `manufacturing`,
`construction_property` and `retail_hospitality` edges; all nine original file examples; the
`work_types` list; the sensitivity posture and its quotations; the five `falls_through_to` routes;
NJ-BO-7; `proposed_context_terms`; and `fields`/`proposed_fields` empty.

**Added:**
- The two charges taken at full strength and answered — including the schema anchor's own naming of
  *the tender evaluation matrix* as its paradigm of a node-earning structure.
- This row's position relative to the settled three-row counterparty boundary: **outside it, because
  it is not counterparty-anchored** — with the cardinality argument, the existence-transition
  argument, and the merged-row-would-be-the-refused-row argument.
- The node test argued leg by leg against the anchor's stated default paragraph, including three named
  departures from it and an honest statement that leg 2 is unscorable under PR-6.
- Files considered and rejected (ten entries), including four rejections the gist draft did not make.
- Three new file examples: `PQQ response - ITT-2026-014.docx` (two-directional fixture),
  `Call-off order - Framework FA-2024-03 - Lot 2.pdf` (the framework case the gist draft left in prose),
  `Pricing model v4.xlsx` (the must-not-be-lost-to-this-row fixture).
- One new `collides_with` (`business_operations.budget-forecast`) and three `also_holds_with`
  (`legal.leases-agreements`, `business_operations.it-asset-inventory`,
  `business_operations.compliance-audit`), where the gist draft had `also_holds_with: []`.
- One new `never_alone` (the high-frequency-counterparty bridge, with `00`'s stop rule) and one new
  `needs_llm` (competition versus framework call-off).
- The archive paragraph, the grouping-trap paragraph, and the reciprocal boundary section with
  neighbours' own landed wording quoted back.
- NJ-BO-PS-2 and NJ-BO-PS-3.

**Reversed or contradicted: nothing.** No neighbour's landed file was contradicted, and no argument in
the gist draft was silently replaced. The gist verdict — the row stands — is confirmed, on stronger
grounds than the gist draft had available, because the schema anchor and three neighbours had not yet
been deepened when it was written.

**Files written this pass:** `planning/domains/nodes/business_operations.procurement-sourcing.json`
and `planning/domains/nodes/business_operations.procurement-sourcing.research.md`. Nothing else.
