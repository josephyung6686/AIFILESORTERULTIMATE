# `construction_property.agency-listing` — lab notes (R1b, deepened to J-DEPTH)

Row kind: **template**. Schema: `construction_property`. Launch: **placeholder** (`fields: []`).
Absorbs the legacy row `prop.listing` (ROSTER.md §4 / Appendix A). Verdict: **kept, not refused** —
and, unusually for this family, kept on **two** legs of the node test rather than one.

**Status of this pass.** The row was written once under the retired `Depth: GIST` label. The JSON was
already close to launch-row depth — house-correct key set, machine-verified quotations, a real
never-alone list, ten file examples that split observations from facts. The **memo** was not: it was
a two-page verdict sheet. This pass therefore **deepened the memo and reciprocated the JSON's edges**;
it did not rewrite arguments that were already sound. Every conclusion the gist draft reached is
preserved. See *What changed in this pass* at the end for the audit.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted, verbatim, everywhere.
  The spans that did real work on this row:
  - the collector prohibition, which is the whole basis of this row's one prohibition: *"A folder
    should not become a collection point for everything produced by the same person or
    organization."*
  - the dimension-order rule: *"For document and record domains, project, function, or subject
    usually comes before time because putting year first scatters related work across calendar
    folders."*
  - the recommendation clause, which keeps the tree advisory: *"The system recommends an order based
    on the domain template, but the user can reverse, remove, add, or flatten dimensions."*
  - the sparse-file rule, which this row needs constantly because a third of its evidence is a
    photograph with `DSC_0041.JPG` in the filename: *"The graph does not automatically copy those
    missing facts onto sparse files."*
  - the photo-event sentence, which grants the event and nothing more: *"Camera EXIF, GPS, and
    capture time can support deterministic photo-event proposals."*
  - the EXIF-absence warning: *"the system must not mistake the absence of EXIF for proof that an
    image is a screenshot"*.
  - the privacy-ordering sentence, which is the precondition on every detection signal this row
    lists: *"Privacy policy must be enforced before content reaches any model or external
    connector."*
  - the corpus sentence, which names by category most of what a marketing folder actually holds: the
    corpus *"can include identity documents, account statements, tax records, medical information,
    legal records, credentials, private correspondence, GPS metadata, employment materials, and
    educational records"*.
  - the abstention sentence, which is where the professional/householder seam ends when it does not
    settle: *"Correct abstention is a successful outcome because the product's goal is reliable
    organization, not maximum file movement."*
- `planning/domains/CONNECTION.md` §2 (the node test), §5 (the closed edge vocabulary), PR-6.
- `planning/domains/_CONTRACT.md` — rules 3 (no invented thresholds), 9 (jurisdiction stays a value),
  10 and 15 (a dimension may only branch on a field the entry's own schema declares).
- `planning/domains/canonical_fields.json` — 37 keys checked, one by one, against what this row
  wants. **Nothing holds a property, an instruction, a listing or an applicant. No key minted.**
- `planning/overnight/council/DECISION-BRIEF.md` — D1 as narrowed, D4, D6, PR-6, J-IND taken as
  ratified. J-DEPTH (2026-08-24) overrules J-IND's gist clause; this memo is written to launch-row
  standard.
- `src/evidence_shape/vocabulary.py` — every `source_type` on the row checked against `SOURCE_TYPES`.

### Neighbours read in full before writing, and not rewritten

- **`construction_property.research.md`** (the deepened schema anchor, 42KB) — the measuring stick.
  Its default-template paragraph and its constitutional never-alone are quoted below and this row
  is tested against them explicitly rather than against a remembered version of them.
- **`finance.household-property`** (landed launch row) — the professional/householder seam, from the
  householder's side. Its fixtures `IMG_6021.HEIC`, `Home Inspection Report - 42 Oak Street.pdf` and
  `Residential Appraisal Report - 42 Oak Street.pdf` were read before this row's own were finalised.
- **`legal.leases-agreements`** (landed launch row, safety domain) — the instrument side. Its fixture
  `Lease Agreement - 18 River Court - Signed.pdf` and the shared address `18 River Court` are used
  deliberately: this row's fixtures sit at the same address so the seam can be seen in one place.
- **`construction_property.sale-purchase`** and **`.tenancy-management`** — the two nearest siblings,
  both of which the dispatch flagged as plausibly overlapping. Both had already authored edges
  toward this row; **neither was reciprocated until this pass, and now both are.**
- **`construction_property.progress-photos`** — read in full, including its capture-rhythm argument,
  before writing anything about marketing photographs.
- **`construction_property.inventory-inspection`, `.survey-valuation`, `.development-appraisal`,
  `.commercial-lease`, `.drawings-revisions`** — all five had authored edges naming this row. All
  five are now reciprocated.
- **`creative.raw-photo-catalogue`** (landed J-DEPTH) — read for the rule that being catalogued is
  never evidence about subject matter; applied here to portal media libraries.

### A source that is *not* available, and it matters

**`00` never names this world.** Its template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections"*. Estate agency is absent, as is the whole `construction_property` family. That is why
`design_cite` is `null`, `provenance` is `proposal`, and **every** `collides_with` entry on this row
carries `provenance: inference`. `00` supplies the machinery — activation, never-alone, residuals,
dimension order, privacy ordering. This row supplies only the situation.

---

## What this row is, in one paragraph

A **marketing instruction**. Somebody has been told to sell or let a property that is not theirs, and
the file that produces is a campaign: the terms of business that start it, the particulars and their
drafts, the photograph set and the floor plan, the portal copy and its exports, the viewing diary and
the feedback, the applicants and their references, the offers, and the memorandum that ends it. The
anchor is not the building and not the money. It is the **instruction plus an audience**: a price or
a rent, addressed to people who do not yet live there.

That last clause is the reason this row exists and the reason it is the most privacy-loaded row in
the family. Everything in it is produced *about* strangers and *for* strangers.

---

## The node test, all three legs, argued against the schema's stated default

The schema anchor states the paragraph every sibling must differ from:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles*. **Not time-first.**

and the family's constitutional never-alone, read across from `00`'s university sentence: *"A
university name alone should not create a group because Columbia can appear as an authoring school,
course provider, target institution, employer, research venue, or merely a cited organization."*

CONNECTION.md §2 requires a difference in **detection signals**, **recommended dimensions**, or
**privacy rules**. One suffices. This row has two, and honestly fails the third.

### Leg 1 — detection signals. **Passes, and this is the strongest leg.**

The schema's default recognition is *document structure*: a header, a reference, a table, a
signature block, a title block, a valuation cycle. This row is recognised by structures that exist
nowhere else on the schema:

- **The marketing-particulars structure.** A price or rent line, a tenure or term line, a room
  schedule with dimensions and a stated total, a floor plan, a photograph montage and agency
  branding — laid out *for an audience rather than for a file*. No other row on this schema produces
  a document designed to be read by someone who has never seen the building. The co-occurrence is
  the signal; each half is worthless alone, and the JSON says so.
- **The portal-export structure**, with a marketing status vocabulary — *available, under offer, let
  agreed, withdrawn, sold subject to contract*. This is a genuinely distinctive lexicon. No survey,
  no drawing, no valuation, no tenancy file uses it. It is also the only structure on this row that
  usually arrives as a **screenshot or a data export** rather than a document.
- **The agency-instruction structure** — terms of business naming a vendor or landlord, a fee basis,
  and a sole-or-multiple-agency term. `sole agency` and `multiple agency` are terms of art that exist
  in no other row's vocabulary.
- **The viewing-and-feedback structure** and the **offer structure** — dated viewings by applicant
  with feedback text; an amount plus a *position* (chain, funding, proceedability).

Test of the leg's honesty: **strip the never-alone evidence and see what survives.** This is exactly
the test that killed `construction_property.compliance-certificate`, whose entire support reduced to
a document-type word plus an address. Strip the address, the money figure, the agency name, the
document-type word and the file extension from this row, and what remains is: *sole agency term*,
*let agreed*, *offers over*, *proceedable*, *memorandum of sale*, *viewing feedback*, *approximate
gross internal area*. That is a live vocabulary, not a residue. The leg holds.

### Leg 2 — recommended dimensions. **Fails as a difference, and is recorded as failing.**

`property → instruction → function` is exactly the family default. This row does not reverse it and
does not add a period level. Under the schema anchor's own warning — *"Reversing is not a difference
that earns a node"* — the row can claim nothing here.

The gist draft did **not** claim this leg either, and this pass agrees with it. What is worth
recording is *why* the row follows the default so exactly: an estate agency's entire filing life is
address-first, and the instruction level is unarguable because **one property is marketed
repeatedly** — the 2019 letting, the 2023 relaunch and the 2026 sale are three files about one flat,
often through three different agencies. The default fits so well that there is nothing to differ
about. That is a fact about the row, not a weakness in it, because leg 1 already carried the test.

**The one thing this row adds to the default is a prohibition, not a level: never an applicant
dimension.** An applicant is the natural second axis — an agent thinks in applicants — and it is
forbidden twice over. `00`: *"A folder should not become a collection point for everything produced
by the same person or organization."* And an applicant level would write a **named private
individual who is not the user** into a directory name that every other program on the machine can
read. `construction_property.tenancy-management` declined the same thing for a tenant (NJ-CP-TEN-3);
this row declines it for an applicant, on the same reasoning, and says so here so the two rows are
visibly consistent.

### Leg 3 — privacy rules. **Passes, and it is the leg the dispatch was right to ask about.**

The dispatch warning was: a listing is *public-facing marketing material* — photographs, floorplans,
particulars — so does that make this row **less** sensitive than the schema default?

**It does not, and the reasoning is worth stating carefully, because the intuition is reasonable.**

The published particulars are indeed public. But the published particulars are the *output*, and this
row is the *file that produced it*. The schema anchor's leg-3 grounds are that the material names a
real person's home and who is in it, that the exposed party is usually not the user and cannot
consent, and that `00`'s corpus sentence names this material by category. All three apply here in
their sharpest form, and one of them applies in a way that applies to no other row on this schema:

- **The photograph set is the inside of a stranger's occupied home**, with their possessions in
  frame and, routinely, their family photographs on the walls. The *published* set is cropped and
  curated. The *shoot* is not: forty frames, of which eight were used. The unused thirty-two are the
  normal case in this row's folder and were never public at all.
- **The applicant material was never public in any version.** Names, phone numbers, feedback, tenant
  referencing, affordability, and offers that state what a named private person can afford. `00`'s
  corpus sentence names *account statements* and *identity documents*; agency referencing carries
  both by design.
- **Almost none of these people are the product's user**, and none of them can consent to what the
  product does with the file. The vendor at least instructed somebody. The applicant who viewed a
  flat and did not buy it instructed nobody.

So the row's privacy posture differs from the schema default **in kind, not in degree**: the schema
default protects commercial confidence held on a client's behalf; this row's *ordinary* case is
**third-party personal data about people with no relationship to the user at all**. That is a
different rule, and it is what makes leg 3 pass rather than merely restate the family.

Two disciplines follow, and both are in the JSON:

1. The `sensitivity` value is `potentially_sensitive` and **no P7 handling class is assigned** —
   that is P7's to set, and this catalogue does not alias, rank or infer it.
2. Every entry in `recognition.deterministic` is prefaced by a precondition stating that it is a
   **detection** signal and never an extraction licence, on *"Privacy policy must be enforced before
   content reaches any model or external connector."* A row this rich in signals, on a schema with
   no fields, must not be read as licensing extraction.

**Verdict: kept, on legs 1 and 3, with leg 2 explicitly conceded.**

---

## The seam the dispatch called most important: the agent's instrument vs the householder's own home

Stated in both directions, as the brief requires.

`finance.household-property` landed first and holds *the household's own ownership, occupation,
taxation, insurance and maintenance record of its own home*. `legal.leases-agreements` landed first
and holds *the executed instrument*, and legal is a safety domain that protects first. This row holds
*a professional's marketing instruction over a property that is not theirs*.

**The seam is not the document.** A particulars PDF, an EPC, a floor plan, a set of interior
photographs and a memorandum of sale exist identically on both sides. The householder who sold their
own house keeps every one of them, and `finance.household-property` already lists *title, inspection,
warranty and completion certificate* among its own work types, which settles that document type
cannot decide anything here.

**The seam is the instruction apparatus.**

| Evidence present | Reading |
|---|---|
| terms of business, a fee basis, a sole-agency term, an applicant register, viewing feedback, offers received on behalf of another party | **this row** |
| the same particulars, EPC, floor plan and photographs held with **none** of that apparatus, as one household's record of its own home | **`finance.household-property`** |
| an executed instrument — party recitals, covenants, consideration, execution block | **`legal.leases-agreements`**, which protects first |
| the marketing has ended and an offer has been accepted; title, searches, enquiries, the contract, the transfer | **`construction_property.sale-purchase`** |
| a let has been agreed; deposit protection, served statutory documents, compliance calendar, rent ledger | **`construction_property.tenancy-management`** |
| the role does not settle and neither side's apparatus is present | **neither activates.** *"Correct abstention is a successful outcome because the product's goal is reliable organization, not maximum file movement."* |

**In the other direction, explicitly, so this row cannot creep:** a person selling their own home
holds particulars, photographs, an EPC and a memorandum, and **none of that is this row**. The
apparatus is absent because they never instructed themselves. This row takes the agent's file, not
the seller's. Where the seller is *also* the agent — an owner marketing a flat privately, a small
landlord advertising a let themselves — the apparatus is genuinely half-present, and this pass
declines to draw the line on scale, because a line drawn on scale needs a threshold and `_CONTRACT`
rule 3 forbids inventing one. That case is **NJ-CP-AL-2** below, and it is the same shape as the
schema anchor's NJ-CP-3 and `tenancy-management`'s NJ-CP-TEN-1. Three rows have now met the same
question from three sides and none has invented an answer; that consistency is itself the finding.

**And the sentence a reader of any of the three files should carry away:** *the property address does
not select a side.* It is present on both sides of every line in that table, which is precisely why
it is the family's constitutional never-alone — and why it is *doubly* never-alone here, because a
marketing folder is full of **other people's** addresses, held as comparables and competitor
listings.

---

## The photographs: against `photos.*`, and against this family's own `progress-photos`

The dispatch asked specifically whether marketing photographs collide with `photos.*` or with
`progress-photos`, and whether the capture-rhythm argument that row made cuts against this one.

**It does not cut against this row; it is the axis this row uses too.**

`progress-photos` earned its node on being recognised by *capture metadata, rhythm and place* rather
than by document structure, and drew its line against `photos.camera-events` as *"a camera roll goes
to many places once, a site walk goes to one place many times."* This row is on that same axis at a
third position:

| | places | visits | subject |
|---|---|---|---|
| `photos.camera-events` | many | once each | an occasion, people in frame |
| **this row's marketing shoot** | **one** | **once, completely** | **finished, staged, every room** |
| `construction_property.progress-photos` | one | **many, at intervals** | unlovely structural state |

The marketing shoot is a **single complete visit that is never repeated**: every room, one afternoon,
one camera, consistent exposure. The site walk is **the same place again next week**. That is a real
discriminator and it is authored on this row's `progress-photos` edge in exactly those terms, without
weakening that row's own argument — which this pass deliberately does not reopen.

Against `photos.camera-events` the discriminator is **the instruction around the images, never the
images**. A GPS cluster, a camera model and a capture window support a photo event and nothing more:
*"Camera EXIF, GPS, and capture time can support deterministic photo-event proposals."* The marketing
fact comes from the particulars, the listing and the instruction, or it does not come at all — and
membership in the cluster must never become the fact: *"The graph does not automatically copy those
missing facts onto sparse files."* The JSON's `DSC_0041.JPG` example carries
`group_without_copying_facts: true` for exactly this reason and `also_schema: "photos"`, because
the frame legitimately *is* a photo.

Against `construction_property.inventory-inspection` the honest position is that **no metadata
separates them at all**. A marketing frame and a check-in inventory frame of the same living room,
taken a week apart, are indistinguishable as files. The discriminator has to come from what surrounds
them: a room-by-room schedule with condition gradings and a signature block, versus a floor plan with
a stated area and a price line. The craft tendency — marketing frames are lit, wide and flattering;
inventory frames are close, unlit and record wear — is recorded on the edge **as a tendency and not
as evidence**, because building detection on it would be building on a photographer's habits.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. These were considered as this row's
evidence and are not:

| Considered | Why it is not this row's evidence |
|---|---|
| **Anti-money-laundering ID checks on a buyer** (`passport scan + bank statements`) | Real in every agency file, and squarely identity-safety material. Excluded deliberately: including it would have invited this row to describe handling that belongs to P7 and to the identity placeholder. `construction_property.sale-purchase` keeps it as a fixture with `also_schema: "identity"`, which is the right home for the argument. |
| **The tenancy agreement itself, and the deposit protection certificate** | The instrument is `legal.leases-agreements`', which protects first; the running relationship is `tenancy-management`'s. This row stops when the let is agreed. |
| **Board orders, signage orders, portal subscription invoices, advertising invoices** | Transactional service purchases. `Receipts and Confirmations`, and `finance.receipts-expenses` if the holder is running a business. Not a marketing instruction. |
| **A gas safety record, an electrical report, a building regulations completion certificate** | Required *for* marketing and equally a householder's own record. This is exactly why the family **refused** `construction_property.compliance-certificate`: a document-type word plus an address is never-alone evidence on both halves. The `EPC.pdf` fixture is kept precisely to make that visible. |
| **A `.vcf` of applicant contacts** | `00` requires contact data be privacy-protected rather than used to create folder proposals. A file-kind signal at most; using it as an example would mislead. |
| **The agency's own accounts, commission ledger and staff records** | The business of running an agency, not the marketing of a property. `business_operations.*` and `finance.small-business-bookkeeping`. |
| **A competitor's particulars saved for comparison** | Kept as a *fixture*, not as a claim: it is byte-identical to this row's own particulars and is reference material. `Reference Clips`. See the collision fixture below. |
| **A market appraisal presented as a valuation** | The reciprocal edge to `survey-valuation` handles it: a basis of valuation, an inspection date and a limitation of liability are that row's; an asking-price recommendation and a fee schedule are this row's. |

---

## The collision fixture, in both directions

**A file that would wrongly fire this row.**
`18 River Court - particulars FINAL.pdf`, downloaded by a **buyer** who is house-hunting. It carries
the asking price, the room schedule, the floor plan, the photograph montage and the agency branding
— every deterministic signal this row has, in full co-occurrence. It is not this row's evidence. The
discriminator is the **absent apparatus**: no terms of business, no applicant register, no viewing
feedback, no offer received. What is present instead is a folder of *other* agencies' particulars for
*other* addresses. That is a person browsing, and the honest home is **Reference Clips** — *"saved
visual inspiration, product references, quotes, recipes, short article captures, code snippets, or
other material that is useful for later retrieval but does not belong to a current project."* The
JSON records this on the fixture itself: `must_not_conclude` includes `"that the holder is the agent
rather than a buyer who downloaded it"`.

**A file that must not be lost *to* this row.**
`Lease Agreement - 18 River Court - Signed.pdf` — the landed `legal.leases-agreements` fixture, at
the address this row's own fixtures use. It concerns the same flat, arrives in the same folder, and
is the direct consequence of the letting instruction that this row holds. It is **not** this row's:
it is an executed instrument, legal is a safety domain, and it protects first. This row's letting
material ends at the memorandum of letting. Named on both sides, same bytes, same reading.

**And the same bytes named on a third seam:** `Move-in Inventory and Condition Report - 18 River
Court.pdf` appears as a fixture on **both** `finance.household-property` and
`legal.leases-agreements`. It is not this row's either — it is a condition record made after a
tenant moved in, which is `inventory-inspection`'s situation and those two rows' record. This row
photographed the flat to *let* it; it does not own what was done once somebody lived there.

---

## The dimension recommendation, held as prose

`template.dimension_order` is **empty by binding contract** — `_CONTRACT` rules 10 and 15 permit a
dimension only on a field the entry's own schema declares, and `construction_property` declares none
(D1 as narrowed, PR-6). That is a contract fact and not a claim that the situation has no shape.

The recommendation, for whoever answers NJ-CP-1: **property → instruction → document function.**
Property first because an agency's filing life is address-first and a building outlives every
instruction over it. Instruction second because one property is marketed repeatedly. Function last,
by the parent-context rule — an `Offer` or `Viewing feedback March` is meaningless without knowing
which instruction it belongs to, exactly as `Homework 3` is meaningless without the course. Not
time-first: *"For document and record domains, project, function, or subject usually comes before
time because putting year first scatters related work across calendar folders."* **Never an applicant
level**, for the two reasons argued under leg 2. And whatever lands stays advisory: *"The system
recommends an order based on the domain template, but the user can reverse, remove, add, or flatten
dimensions."*

---

## `proposed_fields`

**None**, and this is a deliberate position rather than an omission.

- The key this row actually needs is **`property`**, and it is proposed once, at the schema row, as
  NJ-CP-1. Re-proposing it here would be a variant of an existing proposal, which the brief forbids.
- An **`instruction`** or listing-reference key was considered and not proposed: a listing reference
  is a short token in an extremely crowded token space (four to eight characters, no checksum, no
  context) and would be never-alone evidence in any case.
- An **`applicant`** key was considered and **deliberately not proposed.** An applicant is a natural
  person; the row's own privacy argument forbids that value from ever becoming a destination; and a
  field that can never be a destination and can never be safely surfaced is a field this catalogue
  should not create. Recorded so R1c can see it was refused rather than overlooked.

---

## Neighbours considered that did **not** get an edge

- **`creative.commissioned-shoot`** — a property photographer's own engagement over the same shoot.
  Considered seriously and still rejected: the discriminating evidence is the *brief and deliverable*
  apparatus on the creative side, which is that row's to state, and a one-way edge authored from here
  would pre-empt it. Recorded so the absence is not read as a denial.
- **`creative.raw-photo-catalogue`** — a portal media library and a catalogue are both indexes of
  imported images. No edge: that row's own rule settles it — being catalogued is never evidence about
  subject matter — so a catalogue membership could not fire this row in the first place.
- **`business_operations.go-to-market`** — marketing material in general. No edge: the only shared
  evidence item would be *branding*, which is not an evidence item at all.
- **`finance.receipts-expenses`** — advertising and portal invoices. Covered by the receipts
  residual; no discriminating evidence item is shared.
- **`legal.leases-agreements`** and **`finance.household-property`** — argued at length above and
  carried as a `collides_with` for the household row only. The legal seam is expressed through
  `also_schema: "legal"` on the terms-of-business fixture and through the collision fixture, because
  `also_holds_with` joins **schemas** and this is a template row. Recorded so R1c does not read the
  empty `also_holds_with` as a denial of the legal seam.
- **`law_practice.conveyancing`** — the conveyance is `sale-purchase`'s seam, already authored; no
  second edge earns its place.

---

## NEEDS-JOSEPH (this node only)

- **NJ-CP-AL-1 · Third-party applicants.** The sharpest privacy question this pass met. An applicant
  is a natural person whose only relationship to the product's user is having viewed a flat, and
  their name, phone number, feedback and affordability sit in ordinary agency files. This row
  forbids an applicant *destination dimension* outright — but **forbidding a folder level is not the
  same as protecting the data.** The mechanism that would force P7 handling ahead of any model path
  for third-party personal material does not exist in this catalogue. Same gap as the schema
  anchor's NJ-CP-4 and the landed `business_operations` row, in its most acute form, because here
  the exposed party is furthest from the user. *Alternatives:* **(a)** a catalogue-level flag marking
  a row as carrying non-user personal data, which R1c would have to define and every affected row
  re-audit; **(b)** leave it entirely to P7, which is architecturally cleanest but means this
  catalogue records a known risk and no signal about it. Joseph's, because it is a policy choice.
- **NJ-CP-AL-2 · The private seller and the DIY landlord.** Where the marketing apparatus is
  half-present because the owner is their own agent, this row and `finance.household-property` both
  fire partially. This pass declines to draw the line on scale (a threshold `_CONTRACT` rule 3
  forbids) and declines to guess. *Alternatives:* **(a)** require the *fee* apparatus specifically —
  no fee, no instruction, so the householder row wins, which is crisp but excludes the salaried
  in-house agent; **(b)** let both abstain, which is safe and leaves a real file unfiled. Reciprocal
  with the schema anchor's NJ-CP-3 and `tenancy-management`'s NJ-CP-TEN-1.
- **NJ-CP-AL-3 · Where does the memorandum of sale live?** It closes this row's instruction and opens
  `sale-purchase`'s pack, and both rows can legitimately hold it. The edge is authored from both
  sides now and neither claims exclusivity. *Alternatives:* **(a)** assign it to the closing row
  (this one), so the marketing file is complete; **(b)** assign it to the opening row, so the
  transaction pack is complete; **(c)** let it be a genuine dual member. Related to but not the same
  as `sale-purchase`'s NJ-CP-13, which asks when a transaction stops being one.
- **Inherits NJ-CP-1** (does `property` become a canonical key). Property-first is this row's
  clearest recommendation and it cannot be declared without that key.

---

## Self-verification

- `construction_property.agency-listing.json` parses under `python3 -m json.tool`.
- Key set matches the landed siblings (`sale-purchase`, `tenancy-management`, `progress-photos`);
  no key added, none removed.
- `fields: []` and `proposed_fields: []` — no canonical key minted, no field row written.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; every `must_not_conclude` list ends with
  `"a folder path"`; no file example writes a path as a fact.
- Every edge target checked against `roster.json`. The six edges added this pass are all
  reciprocations of edges those rows had **already** authored toward this one, except
  `tenancy-management` and `progress-photos`, which are new from this side and stated so as not to
  contradict either row's own file.
- All `00` quotations were grep-verified verbatim out of
  `planning/00-database-agent-product-design.md` before writing.
- No threshold, statistic, confidence score, handling class or file count invented.
- Files written: only the two assigned.

---

## What changed in this pass

**Preserved, unchanged** — because it was already right:

- The verdict (kept, not refused) and the two legs it was kept on.
- All eleven `recognition.deterministic` entries, all four `needs_llm` entries, the whole
  `never_alone` list, the 39 `proposed_context_terms`, the 14 `work_types`, the seven
  `grouping_reasons`, all ten `file_examples`, the seven `falls_through_to` entries, the
  `template.why` prose, the `sensitivity` value and its full `sensitivity_why`, and the
  `open_question`.
- The four original `collides_with` entries (`finance.household-property`,
  `construction_property.drawings-revisions`, `photos.camera-events`,
  `construction_property.commercial-lease`).
- The three rejected files and the three no-edge neighbours the gist memo already named.
- `proposed_fields: []`, including the deliberate refusal to propose an applicant key.

**Added in the JSON:**

- Six reciprocal `collides_with` entries: `construction_property.sale-purchase`,
  `.inventory-inspection`, `.survey-valuation`, `.development-appraisal`, `.tenancy-management`,
  `.progress-photos`. Four of the six were edges those rows had already authored **toward** this one
  and which this row had left unreciprocated — a real gap, closed. The `tenancy-management` and
  `progress-photos` edges are new from both sides and were written after reading each row's own file
  so as not to contradict it. `collides_with` sorted by domain.
- `one_line` retitled from `"Gist-level placeholder"` to `"Placeholder row (J-IND, deepened to J-DEPTH)"`. Nothing else in the sentence touched.

**Added in this memo** (which was the shallow half — 3.4KB of verdict, no evidence):

- The full sources section, naming the `00` spans that did the work and the ten neighbour files read.
- The statement that `00` never names this world, and what that forces (`design_cite: null`,
  `provenance: proposal`, every edge marked `inference`).
- The node test argued **leg by leg against the schema anchor's stated default paragraph**, including
  the strip-the-never-alone test that killed `compliance-certificate`, and an explicit **concession
  of leg 2** rather than a silent pass.
- **A direct answer to the dispatch's row-specific warning**: why public-facing marketing material
  does *not* lower this row's privacy posture — the published set is the output, the file is the
  campaign, and the unused frames and the applicant material were never public.
- The professional/householder seam drawn **in both directions**, as a table, with the abstention
  sentence as its floor and the address named as the thing that decides nothing.
- The photographs section: the three-position rhythm table placing this row between
  `photos.camera-events` and `progress-photos` on `progress-photos`' **own** axis without reopening
  its argument, and the honest admission that nothing separates a marketing frame from an inventory
  frame as a file.
- **Files considered and rejected**, expanded from three items to eight, as a table with reasons.
- **The collision fixture in both directions**, plus a third seam naming `Move-in Inventory and
  Condition Report - 18 River Court.pdf` on the same bytes two landed rows already claim.
- Three NEEDS-JOSEPH items with alternatives and their costs, where the gist memo had one item and
  no alternatives.
- This audit section, and the self-verification above it.
