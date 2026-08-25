# `construction_property.site-survey` — lab notes

Depth: J-DEPTH. Placeholder row (J-IND). Template on `construction_property`. Absorbs the legacy id
`cons.site-survey` (ROSTER.md §4 / Appendix A), 1:1.

**Verdict: `refuse_node: false`. Kept, on two passing legs of the node test and one that honestly does
not pass.** The gist pass reached the same verdict; this pass reaches it by a longer road, concedes a
leg the gist row implicitly claimed, and reverses nothing.

---

## Sources actually used

**Binding.**
`planning/prompts/ALIGNMENT.md`; `planning/00-database-agent-product-design.md` (every quotation below
machine-checked with `grep -F` against that file before it was written — see Audit);
`planning/domains/CONNECTION.md` (node test §2, activation §4, closed edge vocabulary §5, PR-6),
`CONNECTION-EXAMPLES.md`, `_CONTRACT.md` (rules 3, 8, 10, 11–15); `planning/domains/canonical_fields.json`;
`planning/domains/roster.json` (every edge id checked mechanically against the roster);
`planning/overnight/council/DECISION-BRIEF.md` (D1 as narrowed, D6 unset, J-IND);
`src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`.

**Neighbours read before writing, and not rewritten.**
`construction_property.research.md` (43KB, J-DEPTH — the schema anchor; this row's node test is measured
against its stated default template); `construction_property.survey-valuation.research.md` (36KB,
J-DEPTH — the paired row, which confirmed this split from its own side);
`construction_property.development-appraisal.research.md` (46KB, J-DEPTH — the *third term*);
`construction_property.construction-project.research.md` and its JSON (38KB — the spine, and the row the
charge says should absorb this one); `construction_property.progress-photos.research.md` (the row whose
detection method differs, and which routed one file kind here);
`construction_property.drawings-revisions`, `construction_property.inventory-inspection`,
`creative.raw-photo-catalogue` for the capture-based reading.

**A source that does not exist, and it matters.** `00` **never uses the word "survey"**, and never uses
"construction", "blueprint" or "floor plan" in a domain sense — checked with `grep -i`. Nothing on this
row can be `provenance: design` about its subject matter. Every subject-matter claim below is therefore
either an argued **inference**, a named real document type, or a `00` quotation about a *mechanism*
(never-alone evidence, abstention, purpose-versus-topic, residuals) applied to this material. The JSON
carries `provenance: "proposal"` and `design_cite: null` for exactly this reason.

---

## What this row is, in one paragraph

The record of **what was found at a site before anything was designed, priced or built**: measured and
topographical surveys, setting-out and control schedules, coordinate and level files, point clouds and
scan registration reports, drainage and CCTV surveys, utility and services searches, ground
investigation and borehole logs, asbestos and opening-up surveys, and the photographs that evidence the
existing condition. Its defining property is that **the deliverable is measured geometry, and its whole
value is that it was true on the day it was taken.** It is an input to design, not a document addressed
to anybody.

---

## The schema's default template, quoted, and exactly how this row differs

The anchor states the paragraph every sibling must differ from:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles* (a service-charge year,
> a rent-review cycle). **Not time-first.**

And it states the standard bluntly: *`variation`, `snagging`, `dilapidations`, `retention`,
`preliminaries`, `certificate`, `drawing`, `schedule`, `survey`, `valuation` and `report` are **values of
`work_type`**, not rows.* **The anchor names `survey` on that list by name.** That is the charge this row
has to answer, and it is not answered by asserting that surveys feel different.

This row's recommendation, held as prose because `dimension_order` is empty by binding contract
(`_CONTRACT` rules 10 and 15, CONNECTION PR-6 — the schema declares no fields, so nothing may branch):

> **site or property → survey type → survey date.**

Two of the three levels differ from the default, and the differences are the argument:

- **The middle level is not the instruction.** This is the real one. A survey routinely exists with **no
  surviving instruction at all** — commissioned for a scheme that was abandoned, a bid that was lost, a
  purchase that fell through, or by an owner two owners ago. Filing it under the instruction files it
  under something that no longer exists and that the holder may never have been party to. What actually
  joins one site's surveys across twenty years and four commissions is **what was measured**: the
  topographic survey of 2006 and the drainage survey of 2019 are two facts about one piece of ground.
  The anchor's own warning applies in reverse here — an instruction level on this row would frequently
  be the *"meaningless one-child level"* the validator rejects, because most sites carry one survey per
  commission and the commission is often unnamed in the bytes.
- **The date is promoted to a real level, and the anchor does not license this.** The default grants a
  period level *only where the situation genuinely cycles*, and **a survey does not cycle** — it is a
  one-off. I am asking for a date level anyway, on a different ground: a survey's entire claim is that
  it was **true on a day**, so two surveys of one site are not versions of one document but different
  facts about the world, and the date is the only thing that distinguishes them. This is a **stated
  exception to the family default, not a silent one**, and it is filed as open question (2) below for
  R1c rather than assumed.
- **Site first, and the date is third, not first.** Not time-first: *"For document and record domains,
  project, function, or subject usually comes before time because putting year first scatters related
  work across calendar folders."* A corpus keyed on survey date scatters one property's investigations
  across decades, which is precisely the failure that sentence describes. Site must be the root because
  a coordinate file's filename says nothing at all and a survey type is unintelligible without knowing
  what was surveyed — *"a parent dimension should provide the context required to understand the child"*.
- **And whatever lands is a recommendation:** *"The system recommends an order based on the domain
  template, but the user can reverse, remove, add, or flatten dimensions."*

The anchor also pre-empts the cheap version of this argument: *"**Reversing is not a difference that
earns a node**"*. I am not claiming a reversal. Site still leads. The claim is that the **middle level is
a different field entirely** and the third level is licensed on a different ground.

---

## The node test, leg by leg

### Leg 1 — detection signals. Differ, but less dramatically than the gist row implied.

The schema's default recognition is **documentary structure about an instruction**: a header, a
reference, a measured-works or valuation table, a signature block, a party in a role slot. This row's
fingerprint is documentary too — and that honesty matters, because it means leg 1 here is **weaker than
`progress-photos`' leg 1**, which differs in evidence *class*. Within the documentary class, though, the
structures this row fires on are not the default's:

- **A delimited coordinate list** — point number, easting, northing, level, feature code; thousands of
  rows; no header row of the business-spreadsheet kind. *"Tables matter because resumes, forms,
  applications, invoices, and administrative documents often place their most useful information in
  cells rather than body paragraphs."* — the mechanism is `00`'s; the *shape* is not on its list, and no
  other document family in this catalogue produces a file like it.
- **A datum and a projection statement**, spot levels scattered across a sheet, a north point and a
  stated scale ratio. Nothing in the default template has a datum.
- **A register keyed to LOCATIONS rather than to a transaction** — an asbestos survey's room-by-room
  sample register, a manhole schedule of cover and invert levels, a borehole log indexed by depth.

The distinguishing property, stated so R1c can test it: **the default's structures are keyed to an
instruction and a counterparty; this row's are keyed to a position in space.** A `work_type` *value*
selects a document within a recognition method; it cannot supply a fingerprint the method does not have.
That is the same shape of argument `progress-photos` made — *"a `work_type` value cannot carry a
different detection method; only a template can"* — applied a rung lower, and I say plainly that it is
the weaker version of it. **Leg 1: passes, narrowly.**

### Leg 2 — recommended dimensions. Differ, and this is the decisive leg.

Argued in full in the section above. The middle level is `survey type` where the family's is
`instruction`, and the ground is that **a survey outlives, and often precedes, every instruction it could
be filed under.** That is not a preference about folder names; it is a claim that filing this material by
instruction loses it. **Leg 2: passes, and it carries the row.**

### Leg 3 — privacy rules. **Do not differ. This leg fails, and the gist row did not say so.**

The row's value is `potentially_sensitive`. So is the schema's. And when I checked the anchor's three
grounds, my three reasons turned out to be **instances of them, not additions**: the anchor already names
*"a building's security-relevant layout"* and already says *"The exposed party is usually not the user"*,
and *"cannot consent"*. An asbestos register and a utility search are exactly that, more sharply — but a
**sharper instance of the schema's own reason is not a different privacy rule.** The one thing that is
arguably mine is that this row routes an unusual share of its material to **Protected Records** and to
**Unsupported or Encrypted**, and that is a residual-routing consequence rather than a rule.

**Leg 3: does not pass.** CONNECTION §2 needs *one* of the three, so the row still stands — but it stands
on legs 1 and 2, and anyone re-auditing it should test leg 2 first.

**Overall: `refuse_node: false`, on 2 of 3 legs.**

---

## The three charges, answered

### Charge (a) — "a survey is a `work_type` stage of `construction-project`"

This is the strongest charge and the anchor puts `survey` on its list of values by name.

**The empirical answer first.** I read `construction_property.construction-project.json` before writing.
Its `work_types` list **begins at** *"tender enquiry, priced return or tender report (pre-award…)"* and
contains **no survey value at all**; its `collides_with` names fifteen neighbours and **this row is not
among them**. The spine, deepened to J-DEPTH by an author who enumerated ten values it does *not* own,
did not claim the survey. That is not proof, but it is the opposite of the charge's premise.

**The argument.** A `work_type` value lives *on* an instruction. This row's material routinely has no
instruction to live on, and — the sharper half — **survives instructions it was never on**:

- A topographical survey commissioned in 2006 for a scheme that was never built is re-read in 2026 by a
  different owner for a different scheme. Under the charge, that file's home is a project that was
  abandoned before the current holder existed.
- A ground investigation commissioned by a **losing bidder** is bought and re-used by the winner.
- A householder's asbestos survey exists with no construction project anywhere in the corpus, and it is
  a standing duty-holder record that outlives every job done to the building.

**A `work_type` value cannot outlive the instruction it is a value on. This material does, routinely.**
That is the difference between a value and a situation, and it is why the charge fails.

**What would make me reverse.** If the corpus in practice were dominated by surveys that arrive inside a
named project folder and are never re-read outside it, then `survey` would be a stage of the project and
the correct outcome would be to fold this row into `construction-project`'s function level. I cannot
settle that from the design docs — `00` has no corpus statistics and `_CONTRACT` rule 3 forbids me
inventing any. The reasons above are structural rather than frequency-based, which is why they stand
without a count. Recorded honestly rather than smoothed.

Reciprocity: a `collides_with` entry for `construction_property.construction-project` was **added to this
row's JSON this pass**, stating the boundary in both directions and noting that the neighbour's file does
not name this row, so R1c should carry the other half across rather than treating my statement as agreed.

### Charge (b) — "a survey report is a *document type*, the charge that refused `compliance-certificate`"

The refusal's test, applied honestly: `compliance-certificate` was refused because when its candidate
signal was **stripped to what would actually have to fire**, two things remained — *a document-type word
and an address* — and both are constitutionally never-alone on this schema. A row whose entire support is
never-alone evidence can never clear activation (CONNECTION §4 step 2). Its other legs failed outright:
default dimensions, default privacy.

Strip this row the same way and the residue is different. Delete *every* document-type word from this
row's signals — delete "survey", "topographical", "borehole", "asbestos" — and delete the address. What
remains is: **a delimited list of coordinate triples with feature codes; a datum and projection
statement; spot levels on a scaled sheet; a location-keyed sample or manhole register with invert and
cover levels; a scan registration report with target residuals.** Those are **structures, not words.**
They are not never-alone in the way a document-type word is, because they do not appear in the other
roles a word appears in — a datum note has exactly one meaning.

**Where the charge lands, and it partly does.** The *report* members of this row — the interpretative GI
report, the survey report letter — really are only a document-type word plus an address once stripped,
and on their own they would be refused for the same reason `compliance-certificate` was. They activate
here **only as members of a pack whose other members carry the structures above**, which is what the
row's `grouping_reasons` say and what `never_alone` enforces. So the honest answer is: **the charge
succeeds against part of this row's material and fails against its core**, and the core is what the row
is named for. `compliance-certificate` had no such core.

### Charge (c) — "its captured material belongs to `progress-photos` or to the landed `photos.*` family"

`progress-photos` earned its row by arguing that it is recognised by **capture metadata, rhythm and
place** rather than by document structure, and that *"a `work_type` value cannot carry a different
detection method; only a template can"*. **I do not contradict that and I do not compete for it.**

The concession, written into this row's `collides_with` this pass: **this row's photographs are never
self-sufficient evidence of this row.** Where the *only* evidence is a run of images on a site,
`progress-photos`' capture-based method is the nearer reading and this row concedes. An existing-condition
image activates here only as a member of a pack whose other members are documentary — a photograph
schedule keyed to a location plan, a survey drawing, a sample register.

Two further things follow, and both run in that row's favour rather than mine:

- **Its own discriminator separates us, not just it from `photos.*`.** *"a camera roll goes to many
  places once, a site walk goes to one place many times"* — a **pre-works survey visits one place
  once.** On rhythm, this row looks more like a camera roll than like a site walk, which is precisely why
  this row must not claim images on rhythm.
- **It routed a file kind to me and I accepted it.** Its rejected-files list says a thermal-imaging survey
  image *"is a survey instrument output and `construction_property.site-survey` is nearer"*. Added this
  pass as a `work_type` value, marked as assigned here by that row. That is the correct direction of
  travel: the neighbour's reading adopted, not re-argued.

Against the landed `photos.*` family the instrument is `also_schema: "photos"` on the capture fixture,
not an edge — `also_holds_with` joins **schemas** and this is a template row (CONNECTION §5). `00`
licenses the double reading directly: *"One file may hold facts from more than one domain without losing
information."* And `creative.raw-photo-catalogue`'s rule applies here unchanged and is endorsed rather
than reopened: **being catalogued is never evidence about subject matter.**

---

## The `site-survey` / `survey-valuation` split — my original argument, and whether their confirmation
matches it

**It matches, and it is not a restatement. The two arguments run in opposite directions and meet.**

The gist argument from this side: the deliverables differ. Mine is **measured data** — coordinates,
levels, strata, sample registers — with **no addressee**, consumed by the design that follows. Theirs is
**an opinion** — a figure, a rating, a recommendation — addressed to a named party, for a stated purpose,
under a reliance clause, consumed by a lender or a buyer. *Measuring the land vs pricing the asset.*

Their confirmation, verbatim from their memo: *"Their argument is that a measured survey has **no
addressee**. Mine is that this row has **nothing else**."* They then argue that stripping a valuation of
its reliance furniture leaves no document at all, whereas *"A measured survey loses nothing at all if you
remove its cover letter; the coordinate file is still the deliverable, and it is still true."*

**That is the same split established by a different test, and the pairing is stronger than either half.**
Mine is a test on **presence** (does the addressee apparatus exist?); theirs is a test on
**load-bearingness** (does the document survive its removal?). A presence test alone is fragile — a
surveying practice that happens to staple a cover letter to a coordinate file would defeat it. Their test
does not have that failure mode, and it repairs the weakest point in my own argument. **I adopt their
formulation as the primary one and keep mine as the operational signal.**

**Divergence: none that I can find.** Their consequence-for-filing paragraph — a measured survey is
consumed once and becomes a dated record of the ground, a valuation is re-read years later by people who
need to know what was known when — is a claim my gist row did not make and I agree with it; it is in fact
the strongest available support for my leg-2 argument that the **date** deserves a level here.

**The hard middle case is agreed and reciprocal.** A structural engineer's inspection report measures and
then opines. The rule, written identically into both nodes: **where a document carries an addressee, a
stated purpose and a reliance clause, the opinion reading wins, because that is what the document is
FOR** — `00`'s *"Topic answers what a file is about, while purpose answers what the file was for."* This
pass **added the shared fixture to this row's JSON in the same bytes their file names**:
`Structural inspection - rear bay - Meridian Eng.pdf`, as a negative example here. The reciprocal
negative on their side, `1042-EX-01 Existing site plan Rev A.pdf`, was already a positive example here.

**What would make me reverse.** Their statement of it is the right one and I do not improve on it: if the
reliance structure sat on *both* rows' deliverables in practice, the split would rest on file format
alone, which is `SOURCE_TYPES` and not a node. It does not. This row's file list is dominated by
coordinate CSVs, point clouds and scan registration reports, and **a coordinate file has no addressee to
give.**

**And the family's third term is honoured.** `development-appraisal` extended this same distinction to
*pricing a scheme that is not there*, and explicitly called itself the third term against this pair. This
row does not contradict it: an appraisal's residual chain contains no measured deliverable and this row
never wants it.

---

## Files considered and rejected

| File | Why it is not this row's evidence |
|---|---|
| **`1042-GA-10 Proposed ground floor Rev C.pdf`** | The primary collision fixture, kept in the JSON. Same practice, same title block, same drawing-number family, same folder — and it records what is to be **built**, not what **exists**. `construction_property.drawings-revisions`. The discriminant is often the single word *Existing* versus *Proposed*, which is why it is in `needs_llm` and not in `deterministic`. |
| **`Level 2 Home Survey - 14 Oakfield Rd.pdf`** | The second fixture, and the one this row's *name* invites. Addressee, condition ratings, limitations section. `survey-valuation`'s, by the agreed rule. |
| **`Structural inspection - rear bay - Meridian Eng.pdf`** | **Added this pass.** The reciprocal fixture — the file that must not be lost **to** this row. It measures, in a numbered schedule keyed to a sketch; it also has an addressee and a liability limit. Opinion wins. Named in the same bytes on `survey-valuation`. |
| **An EPC** | Considered here because a surveyor visits and measures. Rejected: a registered certificate with a rating and an expiry, travelling with tenancy compliance. That shape is exactly what the family **refused** as `compliance-certificate`, and this row does not smuggle it back in through a side door. |
| **A Land Registry title plan, or a searches pack** | A title plan is a **legal boundary record**, not a measured survey: no datum, no levels, no accuracy statement, and its authority is registration rather than measurement. `law_practice.conveyancing` / `construction_property.sale-purchase`. |
| **A `survey results.csv` from a questionnaire tool** | The word collides outright, and this is the funniest false positive in the row: a delimited data file about **people** against a delimited data file about **places**. Respondent rows, question headers and Likert values versus coordinate triples and feature codes. `business_operations.user-research`. Carried as a `collides_with` edge precisely because the word, not the world, collides. |
| **A GPS track or a fitness export** | Also a delimited file of coordinates, and it defeats a naive coordinate detector completely. No datum, no feature codes, no levels, no point numbering — and a timestamp per row, which a survey point file does not have. Not this schema at all. |
| **A structural calculation package** | Loads, load cases, code references and a proposed solution. `engineering.civil-structural`: the discriminator is the **design step**. A record of what was found with no design step is this row; an analysis is not. |
| **A planning application pack containing the existing-site survey** | The same PDF genuinely sits in both worlds. An application reference, a validation letter, a consultee response or an officer's report supports `government.planning-application`; the survey deliverable itself supports this row. Edged, not claimed. |
| **Exploration borehole logs and strata files from a mining licence area** | Byte-identical artefacts. A licence area, a resource estimate or an extraction framing supports `resource_operations.mining-operations`; a site address and a construction commission supports this row. |
| **A manufacturing inspection record** | Considered at gist depth and rejected again for the same reason, which survives the deeper test: **no shared discriminating evidence item.** A part number and a drawing tolerance are not a datum and a level. `survey-valuation` reached the identical conclusion on its own side; the two rows are consistent. |
| **A manufacturer's standard detail library or downloaded CAD block** shipped inside a survey deliverables ZIP | Reference material that arrives with records. Reference Clips. It is the reason `.dwg` alone is on the never-alone list. |
| **A tenancy check-in inventory photo set** | The same forty images of the same rooms as a pre-works condition set. A tenancy, a tenant name and a contents list support `construction_property.inventory-inspection`; a measured deliverable alongside the photographs supports this row. |
| **A published guide to measured surveying** containing every context term this row lists | The `development-appraisal` row's best fixture, and it applies here identically: no site, no commission, no holder involvement. Reading Inbox. **Context terms are not evidence.** |

---

## The collision fixture, in both directions

- **Would wrongly fire this row:** `1042-GA-10 Proposed ground floor Rev C.pdf`. Every structural signal
  this row has except one is true of it — scaled plan, north point, title block, drawing number,
  surveying-adjacent practice, same site folder. What discriminates: **no datum note, no spot levels, no
  accuracy statement**, and a for-construction issue status. It is in the JSON with
  `must_not_conclude` naming `drawings-revisions`.
- **Must not be lost to this row:** `Structural inspection - rear bay - Meridian Eng.pdf`, added this
  pass, named identically on `survey-valuation`. It measures. It is still not this row.
- **And the abstention case:** where both readings are supported and neither is settled, the required
  outcome is neither. *"conflicting signals should lead to abstention rather than an invented
  classification"*, and *"Correct abstention is a successful outcome because the product’s goal is
  reliable organization, not maximum file movement."*

---

## Reciprocal boundaries

Every neighbour this row could steal from. Each is authored in `collides_with`; each neighbour's own file
was read first, and no neighbour is contradicted.

| Neighbour | This row holds | That row holds | Same bytes named on both sides |
|---|---|---|---|
| `construction_property.survey-valuation` | measured geometry with no addressee — coordinates, levels, datum, feature codes, sample register | the reliance-bearing opinion: addressee, purpose, basis, ratings, liability limit | `Structural inspection - rear bay - Meridian Eng.pdf` (middle case, theirs) and `1042-EX-01 Existing site plan Rev A.pdf` (mine, negative there) — **both now on both sides** |
| `construction_property.drawings-revisions` | what exists: datum, spot levels, surveyor's accreditation, an *as-existing* status | what is proposed: design status stamp, for-construction issue, revision-controlled sequence | `1042-EX-01` vs `1042-GA-10` |
| `construction_property.construction-project` | a measured deliverable with **no instruction apparatus** | the instruction: contract, appointment, programme, payment application, handover pack | **added this pass**; that row's file does not yet name this one, so R1c must carry the other half |
| `construction_property.progress-photos` | images only as members of a documentary pack | images as evidence in themselves, by capture metadata, rhythm and place | a run of site images — **conceded to that row where the images stand alone** |
| `construction_property.inventory-inspection` | pre-works condition set alongside a measured deliverable | tenancy, tenant, deposit, check-in/check-out framing, contents list | forty images of the same rooms |
| `engineering.civil-structural` | the record of what was found, with no design step | the analysis, the calculation, the proposed solution | borehole logs feeding a foundation design |
| `government.planning-application` | the survey deliverable | the application: reference, validation letter, consultee responses | the existing-site survey inside the submission pack |
| `resource_operations.mining-operations` | boreholes under a construction commission at an address | boreholes under a licence area with a resource estimate | strata logs and coordinate files |
| `business_operations.user-research` | a delimited file about **places** | a delimited file about **people** | `survey results.csv` |

**Where this row concedes rather than competes:** `progress-photos` on standalone image runs;
`survey-valuation` on any document carrying reliance apparatus; `construction-project` on the as-built and
handover deliverable; `development-appraisal` on anything priced rather than measured.

---

## Neighbours considered that did **not** get an edge

- **`photos` (schema).** A real overlap on the existing-condition image set, and deliberately **not** an
  edge: `also_holds_with` joins schemas and this is a template row (CONNECTION §5). Expressed as
  `also_schema: "photos"` on the `IMG_0114.HEIC` example, which is the correct instrument.
- **`finance.household-property`.** A homeowner really does keep survey reports. But that row's anchor is
  the property as a **financial asset**, and the edge that matters there is with `survey-valuation`, not
  with a coordinate file — a household corpus contains valuations, not point clouds. `survey-valuation`
  authored that boundary and this row does not reopen it.
- **`legal.leases-agreements`.** Considered for schedules of condition annexed to leases. Rejected: an
  annexed schedule of condition travels with the **instrument** and legal is a safety domain that
  protects first. The family anchor's seam table settles it.
- **`business_operations.facilities-workplace`.** Considered for a firm's surveys of its own premises.
  Rejected as **topical adjacency without a shared discriminating evidence item** — that row's evidence is
  occupation and running-the-office, and a datum note never appears in it.

---

## `proposed_fields` and `role_split` — both deliberately empty

`fields: []` and `proposed_fields: []`. The `construction_property` schema declares no field rows (D1 as
narrowed, PR-6, `_CONTRACT` rules 10 and 15), so this row writes none and mints nothing.

What this row **seconds**, without minting a variant — these are the anchor's own proposals and R1c should
settle them there, once, not here:

- **`property`** — seconded, unchanged. This row needs exactly the key the anchor describes: *the thing
  measured*, not `location` (a capture reading, which would file a survey under wherever the surveyor was
  standing) and not `client`.
- **`instruction`** — seconded **only weakly, and this row is evidence for dropping it.** The anchor
  offered it *with a live alternative that R1c should feel free to take*: reuse canonical `project`. This
  row's leg-2 argument is that **its material frequently has no instruction at all**, which is a datum
  against making `instruction` load-bearing anywhere in this family. `00`: *"The system may create new
  values when it sees a new course, project, company, university, or event, but it should not invent new
  fields automatically."*
- **`organization`** — not this row's proposal and not re-argued; it is `business_operations`' and R1c
  settles it there for both.

The one key this row would most like and **does not propose**: a **survey-date** key distinct from
`creation_date` — because a survey's asserted date of truth is not the file's creation date, and a report
typed up three weeks after the visit has two different dates that matter. **Not minted.** Minting on a
schema that declares no fields, at exactly the moment it is most convenient, is the 574's original
mistake performed knowingly. It is filed as open question (2) instead, where it belongs.

`role_split: []` — genuinely empty. The surveying practice, the commissioning client and the eventual
holder are three roles on one file, but they are the family's roles, not a role split this row can author
without keys to point at.

---

## Sparse-file discipline

`Sketch - rear extension measurements.jpg` and a bare `points.csv` are the commonest real files in this
row and neither carries a site. **Activation ≠ grouping.** They may join a P9 neighbourhood without this
row activating and without any fact being copied onto them — `group_without_copying_facts: true` on both
in the JSON. The stop rules apply as written: *"when members carry irreconcilable course, institution,
project, term, or purpose facts"* two sites' surveys in one folder do not merge. And a whole-project
folder pulled down at once proves nothing: *"A session should never be treated as proof of topic"*.

---

## NEEDS-JOSEPH

- **NJ-CP-SURV-1 · As-built and record surveys. Now half-answered, and downgraded.** The gist note said
  *"Someone owning the project row must state the other half."* **They have.** The deepened
  `construction_property.construction-project` lists *"handover pack, as-built assembly or O&M manual"*
  among its **own** work types. **This row accepts that and no longer competes**; the JSON's as-built
  `work_type` value is now marked as not claimed as a situation here, retained only so a file of that
  shape is recognised as survey-shaped and then routed. **The residue for R1c:** the two deliverables
  remain byte-for-byte identical, so no detection signal separates them and only the project timeline can,
  which activation may not read. *Alternatives:* (i) accept as-built to the project row and let this row
  abstain when a project context is present — cost: an as-built survey held by a party with no project
  file goes to Independent Records rather than to the site's survey record; (ii) claim both readings here
  and let the project row browse it — cost: contradicts a J-DEPTH neighbour, which this row will not do
  unilaterally. **Recommendation: (i).**
- **NJ-CP-SURV-2 · Asbestos surveys have two lives.** Claimed here as a pre-works investigation, but an
  asbestos register is also a **standing duty-holder compliance record** that outlives the works and has
  consequences for occupants. Stated reciprocally with `construction_property.site-health-safety`: **this
  row claims the survey deliverable; the ongoing management-plan reading is not claimed here.**
  *Alternatives:* (i) survey deliverable here, management plan there — cost: one PDF is often both, and
  the split is invisible in the bytes; (ii) route all of it protectively and let neither row own it —
  cost: loses the site association entirely. **Recommendation: (i), with Protected Records as the route
  either way,** which is what the JSON does.
- **NJ-CP-SURV-3 · NEW. Does the survey-date level survive?** This row asks for a **date level the family
  anchor does not license**, since the anchor grants a period level only where a situation *cycles* and a
  survey does not. *Alternatives:* (i) grant the exception on the ground that a survey's claim is dated
  truth — cost: every sibling drowning in dates will cite it; (ii) refuse it and let the date live in the
  filename — cost: two surveys of one site ten years apart become indistinguishable siblings under one
  survey-type folder. **Recommendation: (i), narrowly and named as an exception**, which is why it is
  written as a question rather than taken.
- **NJ-CP-SURV-4 · NEW. Leg 3 does not pass, and one other row may be in the same position.** This row's
  privacy posture is the schema's, not its own. That is disclosed rather than dressed up. R1c should know
  that at least one `construction_property` template stands on **two** legs, and may wish to spot-check
  whether other siblings claimed a third leg by restating the anchor's reasons in sharper words.

---

## What changed in this pass — each claim re-checked against the JSON as written

**Preserved unchanged.** The JSON was a verified draft whose *memo* was shallow, not whose data was
wrong. Untouched: all 10 `deterministic` signals, all 7 `needs_llm` entries, all 10 `never_alone`
entries, all 39 `proposed_context_terms`, all 6 `grouping_reasons`, `template.why` and
`time_first: false`, `file_kinds`, all 6 `falls_through_to` entries, `sensitivity` and
`sensitivity_why`, `fields: []`, `proposed_fields: []`, `role_split: []`, `also_holds_with: []`, and 10
of the 11 `file_examples`.

**Added to the JSON — five changes, each verified in the file after writing:**

1. **One new `file_example`** — `Structural inspection - rear bay - Meridian Eng.pdf`, `text_document`,
   `falls_through_if_inactive: "Protected Records"`, `group_without_copying_facts: false`. The reciprocal
   fixture the addendum requires, in the same bytes `survey-valuation` names. `file_examples`: **10 → 11**.
2. **One new `collides_with` edge** — `construction_property.construction-project`, answering charge (a)
   reciprocally and recording that the neighbour's file does not yet name this row. `collides_with`:
   **8 → 9**.
3. **One `collides_with` signal extended** — `construction_property.progress-photos` now states this row's
   **concession** (images alone are that row's), quotes its detection-method argument so as not to
   contradict it, and records that its own rhythm discriminator separates the two rows.
4. **`work_types` edited and extended** — the `as-built or record survey` value is now **marked as not
   claimed as a situation here**, accepting `construction-project`'s claim; and
   *thermal or instrument-imaging survey output* was **added**, accepting the assignment
   `progress-photos` made to this row. `work_types`: **16 → 17**.
5. **`open_question` rewritten** — from one question to two: the as-built item downgraded to its
   half-answered state, and the new survey-date question added.

Plus the label correction: `one_line` said *"Gist-level placeholder (J-IND)"* and now says
*"Placeholder row (J-IND, researched to J-DEPTH)"*; this memo's `Depth: GIST` header is now `Depth: J-DEPTH`.

**Reversed: one thing, and it is a concession, not a verdict change.** The gist memo asserted the node
test passed *"in all three of the node test's grounds at once"*. **That is wrong on leg 3** and is
reversed here: this row's privacy posture is the schema's own, and a sharper instance of the anchor's
reason is not a different rule. The verdict `refuse_node: false` is unchanged, but it now rests on two
legs and says so. NJ-CP-SURV-4 records it.

**Not reversed:** the split with `survey-valuation`. That row confirmed it from its own side by a
different and better test, and I adopt their formulation as primary while keeping mine as the operational
signal. **Because a refusal here would have been a recommendation to R1c about *both* rows** — that row
has now relied on this one's existence in its own reciprocal boundary table — and no refusal is warranted,
no such recommendation is made and no neighbour needs repair.

**Not done, and why:** `dimension_order` stays empty (binding contract), `proposed_fields` stays empty
(PR-6), no field key was minted including the survey-date key this row wants most, and no neighbour file
was touched.

---

## Audit

- `python3 -m json.tool` parses the JSON. Key set is **identical** to the landed
  `construction_property.survey-valuation.json` — checked by set difference, empty both ways.
- Every quotation in this memo and in the JSON was checked with `grep -F` against
  `planning/00-database-agent-product-design.md` before writing; all pass. Note that `00` uses a curly
  apostrophe in *"the product’s goal"* and it is reproduced as such.
- `00` contains **no** occurrence of *survey*, *construction* (in a domain sense), *blueprint* or
  *floor plan* — checked with `grep -i`. Hence `provenance: "proposal"`, `design_cite: null`, and no
  subject-matter claim marked `design`.
- Every `file_examples.source_type` is in `SOURCE_TYPES`: `spreadsheet`, `text_document`, `image`,
  `ocr`, `archive`.
- Every edge id is a real roster id; every `falls_through_to` name is a `00` §7.3 residual.
- No file example writes a folder path as a fact. No thresholds, no counts, no confidence scores, no
  handling classes.
- Only two files written: `construction_property.site-survey.json` and this memo.
