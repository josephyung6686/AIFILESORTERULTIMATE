# Research memo — `government.museum-collection`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.museum-collection.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node — but not for the reason its name suggests. It is not a row about museums. It is a row about
one thing: **a record whose described unit is an individual physical object bearing an accession number**, held
by whoever keeps it. Everything that makes the row survive the charge below follows from that unit of
description, and nothing follows from the institution's name, sector, or building.

It passes the node test on two of three legs — detection signals and privacy — and I record openly that it
fails the third, because PR-6 leaves the schema fieldless and my `dimension_order` is `[]` exactly as the
schema default's is. CONNECTION §2 requires only that "detection signals, recommended dimensions, **or**
privacy rules differ from its schema's default template." One leg is enough; padding an empty dimension list
into a fake difference would be the failure mode this brief exists to prevent.

## The charge — the strongest case that this row should not exist

I put six arguments against the row before writing anything. Two of them are strong enough that they change
the row's content even though they do not kill it.

**1. "Museum" is never-alone evidence, so a row named after it is a label, not a world.** This is not my
inference — the `government` schema anchor's own `never_alone` list already contains "a government
department, regulator, municipality, legislature, court, public school, archive, museum, or official-looking
seal alone". My row is named after a word my parent schema has already declared incapable of activating
anything. **Answer:** the objection is correct about the *name* and I have obeyed it — the first `never_alone`
entry in my JSON repeats the exclusion, and `Museum Store daily takings 2026-07.xlsx` is carried as a fixture
whose only museum evidence is the word "museum" and which is therefore explicitly not mine. The row does not
activate on the institution. It activates on a register row that carries an accession number beside a
measured dimension, and that shape does not occur in any neighbour.

**2. It is a `work_type` value of its own schema.** This is the sharpest form of the charge and I nearly
refused on it. The `government` schema anchor's `work_types` array literally contains: "public education,
accreditation, cultural-service, **museum**, library, archive, or records-management administration where the
body sits inside the state". My row's subject is already enumerated as a *value* on the parent. The brief's
own rule is that work types are values and never nodes. **Answer:** the anchor's value describes *administering
a cultural service* — governance, funding, staffing, opening hours, visitor programmes, the sector as a
function of the state. That is a different filing world from object custody, and I can name the seam with a
fixture: the museum-store takings sheet and a service-administration board paper sit on the anchor's
work-type value; `Accession Register 1987.43`, `Condition Report - 1987.43.1`, and `Outgoing Loan Agreement -
OL2026-08` sit here and have no home in that value at all. The value covers the body; the row covers the
object. Note that the same argument protects `government.library-administration` and
`government.archives-recordkeeping`, which the anchor's work-type value also names — the three sibling rows
stand or fall together on this point, and R1c should treat it as one adjudication rather than three.

**3. It is a lifecycle, not a world.** The roster's `one_line_hint` reads as a stage list: "acquisition,
cataloguing, condition and conservation, location and movement, loans and exhibition, and disposal." A row
whose content is a sequence of stages is a `work_type` enum wearing a node's clothes. **Answer:** I have
demoted every one of those stages into `work_types[]`, where they belong, and rebuilt the row's identity on
the unit of description instead. The row is not "the object lifecycle"; it is "records that describe one
object". The test that shows this is real: `Object Entry Form - OE2026-114` is custody **without**
accessioning and `Provenance dossier - 1938-1945 gap` is research **outside** any stage, and both are
squarely mine. A lifecycle row could not hold either.

**4. It is a duplicate of `government.archives-recordkeeping`.** That row landed first and had already
written a `collides_with` entry naming me "the closest neighbour by far", listing accessioning, donor
instruments, catalogue description, condition and preservation records, and loan or access control as
identical on both sides, with "the same deed of gift shape" appearing in both. **Answer:** I adopt that row's
own discriminator verbatim in direction and reciprocate it. Archives describes *records arising from an
activity*, hierarchically, where the described unit is a series or a file. I describe an *object*,
individually, with material, dimension, condition, and location slots. The archives row already conceded that
"a collection-level record with neither hierarchy nor object slots is undecidable and abstains" — my side
abstains on the identical fixture, so the mutex is genuinely symmetric rather than two rows each claiming the
overlap.

**5. It is defined only by the absence of something** — "objects that are not books and not records."
**Answer:** no. Every one of my sixteen deterministic signals is a positive structure with named slots, and
four of them (facility report, courier report, environmental datalogger keyed to a collections space, IPM
trap check) exist in neither neighbour at all. A row with four exclusive document types is not defined by an
absence.

**6. It is a folder name.** "Collection" is what people call a directory. **Answer:** conceded as a risk and
handled — "Collection, Catalogue, Objects, Accessions, Store, or Curatorial" as a parent folder name is in
`never_alone`, and `template.dimension_order` is empty, so the row cannot propose the very tree its name
suggests.

The row survives. Had the second argument found no seam, I would have refused.

## The node test, argued in full

**Leg 1 — detection signals differ from the schema default.** They do, and they differ in a specific way
worth stating precisely. The `government` schema's default demands *authority-side role* evidence: a bill
packet with an official identifier, a rulemaking instrument, a records-holder disclosure schedule, a
statistical collection record, an election operation, citizen casework. Not one of those shapes appears in
this row, and this row's anchor shape — an accession number beside a measured dimension and an acquisition
source — appears nowhere in the schema default. More importantly the two point in *different directions* on
holder role: the schema default cannot fire without a public body, while my row fires identically for a
charitable trust's register and a national museum's register, because a deed of gift does not change shape
when the recipient's legal form does. That divergence is real and it is the substance of my open question 1.

**Leg 2 — recommended dimensions do NOT differ.** Stated plainly because the brief asks for honesty rather
than a verdict: PR-6 leaves `government` fieldless, the schema default's `dimension_order` is `[]`, and mine
is `[]`. This leg is a tie and contributes nothing to the row's survival. What I did instead of inventing a
difference was record two *prohibitions* in `template.why` that would bind if PR-6 ever lifts: a physical
storage location must never become a folder level, because a browsable store/bay/shelf/case tree is a map to
valuable property; and a donor's name must never become one. Those are recommendations to R1c, not
dimensions, and I have not counted them toward the test.

**Leg 3 — privacy rules differ, and differ in kind.** The schema default's sensitivity rationale is built
around citizen casework, submissions, unsuccessful bids, restricted statistics, ballots, and pre-decisional
work. This row protects four things that rationale never contemplates. (a) *Object location* — the parent
schema has no concept of a record whose disclosure risk is physical theft. (b) *Per-object valuation* — a
sum-insured column is a target list, and it is the same bytes as an ordinary Finance schedule, which is why
the Finance collision is authored. (c) *Donor, lender, and depositor identity*, given in confidence and
separable from an object record that may itself be fully published. (d) *Provenance gaps, restitution
correspondence, culturally sensitive or sacred material, and human remains*, where exposure carries claim,
community, and ethical consequences the catalogue cannot weigh. Facility reports add a fifth: they are a
counterpart institution's security disclosures, confidential to the lender who holds them. The asymmetry
between a published catalogue record and its confidential neighbours is the row's defining privacy fact, and
it does not exist anywhere in the parent default. This leg carries the node on its own.

Design basis quoted verbatim, both grep-verified in `00`: "Privacy policy must be enforced before content
reaches any model or external connector", and protected material "should not be included in cloud-model
prompts by default". No handling class is assigned; P7 owns that vocabulary.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` as the single depth calibration row.
- `planning/domains/nodes/government.json` — the schema anchor, read as the default template I am measured
  against (`template`, `recognition.never_alone`, `work_types`, `collides_with`, `falls_through_to`,
  `sensitivity_why`, `open_question`).
- `planning/domains/CONNECTION.md` §2, read for the node-test clause quoted above.
- `planning/00-database-agent-product-design.md` — reached by targeted grep only. Every span I quote was
  `grep -c`-verified to occur verbatim before use: the extension-as-routing-signal line, the session line, the
  absent-EXIF line, the project-before-time line, the privacy-enforcement line, the cloud-prompt line, and the
  five residual descriptions.
- Landed neighbours, found with one grep for `museum` across `planning/domains/nodes/`:
  `government.archives-recordkeeping.json` (its `collides_with` entry naming me),
  `government.library-administration.json` (its `collides_with` entry naming me, plus its open question 3),
  `creative.exhibition.research.md` (its rejection line naming a museum collection-management export).
- `planning/domains/roster.json` — every edge id checked to exist; all seven do.

Real-world artifact knowledge (accession registers, object entry forms, deeds of gift, condition reports,
standard facility reports, courier reports, treatment reports, environmental logger series, IPM trap checks,
deaccession papers, provenance dossiers, collections-management-system exports) is drawn from ordinary
practice and is marked **inference** throughout; the JSON's `provenance` is `proposal` and no design citation
is claimed for any of it.

## The collision fixture

`Exhibition Checklist - Threads of Empire - final.xlsx`. It is the file most likely to be misfiled as mine and
the reason is that it is *more* object-like than several genuine fixtures: every row carries an accession
number, a maker, a date, and measured dimensions. It is not mine. What discriminates it is the lender column
— it names several owners, so the accession numbers on the sheet belong to different collections and none of
them evidences the holder's custody — together with room, wall, mount, and label-copy columns, which are
show-assembly slots with no custody meaning. `creative.exhibition` has already rejected the mirror case from
its side ("A museum's collection-management database export. Institutional systems of record, not a show"), so
the pair is reciprocal. The same object rows become mine the moment they appear inside a loan agreement
carrying a valuation and conditions of loan.

A second, quieter collision fixture is worth naming because it crosses schemas: `Location Movement Log
2026-Q2.csv` is column-for-column an IT asset movement log. Identifier, from-location, to-location, barcode,
custodian, timestamp. Neither row may claim it from columns alone.

## Files considered and rejected

- **`Family collection inventory.xlsx`** — a private collector's list of artworks with makers, purchase
  prices, and domestic rooms. It has objects and values and no register, no accession numbers, no transfer
  instrument, no institutional custody. Carried as a fixture precisely so the row cannot drift into personal
  property. Routes to Independent Records or, with insurance structure, to Finance.
- **`Museum Store daily takings 2026-07.xlsx`** — the word "museum" in the header and nothing else. The
  charge's first argument made concrete.
- **An auction or dealer catalogue** with lot numbers, provenance paragraphs, condition notes, and estimates.
  Structurally the closest published mimic of a register that exists. Rejected: the lot number is an offer
  reference, not a custody reference, and the holder is a buyer, seller, or reader. Reading Inbox.
- **A published collection catalogue or museum-studies article.** Contains hundreds of genuine object records.
  Rejected as reading material by the same logic the schema anchor applies to a downloaded law: publication
  by an institution is not custody by the holder.
- **A gallery visit's photographs**, including tightly framed shots of wall labels with accession numbers
  legible under OCR. Rejected — a legible accession number in a visitor photograph is exactly the case the
  `never_alone` accession-token rule exists to stop. Travel or Photos.
- **A curator's or registrar's employment file, timesheet, or CV.** The schema anchor already rules that a
  public-sector employer name on a resume is not the schema; the same holds for a museum employer here.
- **A live collections-management system** (TMS, Axiel, PastPerfect, CollectiveAccess). A source system is not
  a file node. Only a bounded export with a readable manifest is represented, and it is not unpacked to
  improve classification.
- **Building-management environmental data and facilities pest control.** Byte-identical to my preventive-
  conservation fixtures. Rejected unless the header keys the series to a named collections space; otherwise
  Review Later.
- **Digitisation masters and IIIF derivatives** as a class. Rejected as a file-format family, not a world;
  only an image tied to an accessioned object by target board or sidecar is carried.
- **Repatriation and restitution as a separate stage row.** Rejected — it is a `work_type` value and it also
  carries the row's heaviest privacy content, which belongs in `sensitivity_why` rather than in a second node.

## Reciprocal boundaries

Seven collisions are authored. Each names the fixture on both sides.

| Neighbour | Mine when | Theirs when | Shared fixture |
|---|---|---|---|
| `government.archives-recordkeeping` | described unit is an object with material/dimension/condition slots | described unit is a series or file in a provenance hierarchy | `Deed of Gift - Whitfield bequest` — object schedule vs box/series schedule; both abstain on a collection-level record with neither |
| `government.library-administration` | accession-register entry with object description and acquisition source | circulating stock — copies, barcodes, shelf classification, borrower lifecycle | a withdrawal/disposal list carrying only identifiers, reasons, dates — undecidable, both abstain |
| `creative.exhibition` | the keeping institution's custody of the object | assembly of a named show — checklist by room and wall, label copy, install schedule | `Exhibition Checklist - Threads of Empire - final.xlsx` |
| `business_operations.it-asset-inventory` | identifier resolves to an accessioned object with object-physical evidence in the group | serial, model, purchase order, assignee, warranty columns | `Location Movement Log 2026-Q2.csv` |
| `finance.insurance-corporate` | object schedule with accession numbers and per-object valuation | policy, insurer, broker, premium, period, claim slots | `Fine Art Insurance Schedule 2026 - collection.xlsx` — both may hold it; neither erases the other |
| `nonprofit.governance` | the paper's operative subject is objects in custody | the body's constitution, trusteeship, general board record | `Deaccession Proposal - 2026-04 board paper.docx` — board skin theirs, object schedule mine |
| `creative.raw-photo-catalogue` | frame or sidecar ties the image to an accessioned object | the photographer's own capture-and-selection workflow | `1987.43.1_recto_colourtarget.tif` |

Two of these — archives and library — were authored against me *before* I existed. I have restated both in my
direction using their own discriminators rather than inventing new ones, so R1c should find the pairs already
symmetric. The remaining five are mine alone; **R1c should add the reciprocal entry on `creative.exhibition`,
`business_operations.it-asset-inventory`, `finance.insurance-corporate`, `nonprofit.governance`, and
`creative.raw-photo-catalogue`.** I have not touched those files.

## Neighbours considered that did not get an edge

- `government.public-authority-record` and `government.municipal-administration` — a council that runs a
  museum produces both, but the overlap is at the *body* level, which the schema anchor already collides. No
  same-evidence mutex over object records.
- `academic` and `research.project-workspace` — a university museum's registers are mine; a researcher's
  study of the same objects is theirs. Genuinely different evidence (register slots vs research workspace
  structure), so a mutex would be noise.
- `legal` / `legal.practice-matter-file` — restitution claims and title disputes generate real legal matters,
  but those need practitioner-side representation evidence. Carried as `also_schema: "legal"` on the deed and
  provenance fixtures instead of as a collision.
- `photos.scanned-documents` — the accession-card scan is coactivation, not a mutex; carried as
  `also_schema: "photos"`.
- `business_operations.contract-administration` — loan agreements are contracts, but the object schedule plus
  conditions of loan is unambiguous. Adding this edge would collide the row with the entire contract world for
  no discriminating gain.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`, `role_split: []`,
`also_holds_with: []` — all deliberate.

Rejected candidates and why I am not proposing them, even though this world is saturated with two of them:

- `accession_number` — the obvious key, and the one I most wanted. Not proposed, because minting it
  immediately raises whether an object identifier may be a folder level, and the answer here is no (a tree of
  object numbers is unbrowsable and, combined with location, unsafe). Under PR-6 the government schema has no
  fields at all, so this must be adjudicated centrally rather than by a child row.
- `location` — refused on safety grounds, not on canonical grounds. A storage location must never be
  destination-eligible, and proposing it as a key invites exactly that.
- `donor` / `constituent` — the protected half of a disclosure pair, the same structural objection
  `government.library-administration` raised about a borrower identifier. Not proposed.
- `institution`, `record_type`, `artifact_type`, `purpose` — canonical but scoped elsewhere (Finance,
  Research/Code, College Applications). Reusing them here would be a synonym mint by another route.
- `work_type` — the row's stages live in `work_types[]` as values. The schema declares no field to carry them.

`also_holds_with` is empty for the same reason the landed `legal.practice-matter-file` left it empty: a
fieldless template cannot author schema-level coactivation. The genuine coactivations (Photos on the object
photograph and the card scan, Finance on the insurance schedule and the store takings, Legal on the deed and
the provenance dossier) are recorded as `also_schema` on the individual fixtures, which is the contract-safe
place for them. `role_split` is empty because lender-versus-borrower is a real role split with no field keys
to split on.

## Grouping without copied facts

Groups are bounded by exact references only: an accession number, a loan reference, an object-entry
reference, a treatment reference, an export manifest, or a dated series keyed to one named collections space.
Four fixtures are marked `group_without_copying_facts: true` — the movement log, the datalogger series, the
IPM sheet, and the card scan — because each can sit in an object's or a space's neighbourhood while the
object, donor, valuation, and location remain unknown. The exhibition checklist is marked the same way for the
opposite reason: it may be adjacent to a loan group without any of its accession numbers becoming the holder's.
An export archive is read from its manifest and not unpacked to improve classification.

## Open questions — NEEDS-JOSEPH

1. **Holder scope, and it is the big one.** The roster places this row under `government`, but most keeping
   institutions are charitable trusts, university departments, private foundations, or company collections,
   and their registers, deeds, loan agreements, and condition reports are byte-identical to a national
   museum's. Alternatives: (a) holder-scope the row to state-sector institutions and collide the rest out to
   `nonprofit`, `academic`, and `business_operations` — clean, but it strands the majority of real evidence;
   (b) treat it as a cross-schema situation that `government` merely hosts — matches the evidence, but breaks
   the roster's schema-per-row assumption; (c) leave it evidence-scoped as written, where holder status
   affects nothing about activation. I have implemented (c) and flagged it rather than deciding it.
   `government.library-administration` raised the identical question and the two should be answered together.
2. **The rare-books / local-studies collection inside a library service**, which `library-administration`'s
   own open question routes to Joseph between three siblings. My recommendation to R1c, not a decision:
   settle it on unit of description — bibliographic title with copies to library, provenance hierarchy to
   archives, individually catalogued object to this row — never on which department holds it.
3. **The work-type collision at the schema anchor.** `government.json`'s `work_types` enumerates "museum,
   library, archive" as a single administrative value while three sibling template rows exist for the same
   words. Either the value should be narrowed to service administration (my reading, and the basis on which I
   defeated the charge), or one of the four is redundant. This should be adjudicated once, across all three
   siblings, not row by row.
4. **If PR-6 lifts**, decide centrally whether an object identifier, a document function, and a bounded event
   reference may become keys — this row proposes none — and rule explicitly that a storage location and a
   donor name are never destination-eligible even if they become fields.
5. **Culturally sensitive material, sacred objects, and human remains.** `potentially_sensitive` is the only
   value available in this phase and it does not express a community-restricted access condition. Decide
   whether that is entirely P7's to model or whether the catalogue needs a way to mark it now.

## Self-verification

- `python3 -m json.tool` parses the node file.
- Key set matches the landed sibling `government.library-administration.json` exactly, including
  `proposed_context_terms`.
- All seven `collides_with` ids confirmed present in `planning/domains/roster.json`.
- All six `falls_through_to` names are from `00` §7.3's nine residual homes.
- Every quoted span was `grep -c`-verified in `00` before use; the two neighbour quotations are verbatim from
  `government.archives-recordkeeping.json` and `creative.exhibition.research.md`.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; every `facts_legal` is `[]` (fieldless schema); no
  fixture writes a folder path as a fact; no threshold number, score, or handling class appears anywhere.
- Files written: only `government.museum-collection.json` and `government.museum-collection.research.md`.

## Final recommendation

Keep `government.museum-collection` as a placeholder template with no fields, no dimensions, no schema
coactivation edge, and no time-first hierarchy. Its identity is the unit of description — an individually
accessioned physical object — not the institution in its name. Recognize it from register, custody, condition,
loan, and preventive-conservation structure; never from the words museum, collection, or accession; protect
location, valuation, donor identity, and provenance-gap material by default; group only through exact
references; and route everything unsettled to Protected Records or Review Later rather than guessing.
