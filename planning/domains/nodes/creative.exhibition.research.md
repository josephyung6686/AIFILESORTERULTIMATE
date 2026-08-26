# creative.exhibition — lab notes (R1b)

Depth: J-DEPTH
Date: 2026-08-26
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.exhibition.json`](creative.exhibition.json).
Salvage: none. Both files are new; no prior draft existed.

## Sources actually used

- `RESEARCH-BRIEF.md` (in full) and the stamped assignment. The assignment's `one_line_hint` carries
  the sentence that turned out to be this row's whole node test: *"where the artwork files and the
  exhibition files are different objects."*
- `planning/00-database-agent-product-design.md` — authoritative, reached by targeted `grep -o` only.
  Every span in quote marks in the JSON was pulled from this file **before** it was written.
- `planning/domains/nodes/creative.json` — the schema anchor, and specifically the **default template
  held as prose** in its `template.why`. This row is measured against that prose.
- `finance.crypto-assets.research.md` — the depth calibration named by the brief; read once for
  standard and idiom, not content.
- `creative.print-production.json` — the **only** landed node whose text contains "gallery". It
  carries a fixture this row must reciprocate (below), and it fixed the template-sibling key set:
  `collides_with` items are `domain_id`/`why`/`provenance`, and `also_holds_with` is `[]`.
- `ROSTER.md`, `canonical_fields.json` (checked for `venue` and `client` — both exist, nothing
  minted), `src/evidence_shape/vocabulary.py`.

`grep -rl "creative.exhibition" planning/domains/nodes/` returned **nothing**. No landed row has
claimed or refused this territory, so every boundary below is stated from this side first and is
offered to R1c as a reciprocation request.

## THE CHARGE — the strongest case that this row should not exist

I put the case at its strongest before writing anything, because four of the brief's named failure
shapes fit this id uncomfortably well.

**(a) It is a lifecycle stage, not a world.** The creative schema's own `one_line` lists the verbs
its material passes through: "designed, filmed, photographed on commission, modelled, recorded,
written, translated, reported, published, marketed, **exhibited**, printed or performed." On that
reading `exhibited` is the terminal value of `stage` — the moment a work is shown — and a row for it
is a row for a value, which ALIGNMENT forbids outright.

**(b) It is a work type.** The schema already declares the work type *"documentation of a physical
work"*. Installation views are exactly that. If the row's whole content is a documentation set, it
is an enum member wearing a node's clothes.

**(c) It is an organisation name — never-alone evidence.** Strip the show and what is left is a
venue: Whitechapel, Kettle's Yard, a fair. `00`'s rule against the university name as sole proof
generalises directly, and a row whose only evidence can never activate is not a row.

**(d) It is the union of neighbours already landed.** `creative.printmaking-editions` holds the
editions, `creative.print-production` holds the catalogue and the invitation,
`career.portfolio-work-samples` holds the install views, `creative.self-initiated-work` holds the
artist's studio, `creative.theatre-production` holds the live analogue,
`business_operations.project-delivery` holds the institutional programme. Nothing may be left.

### Why the charge fails

It fails on one piece of evidence that none of (a)–(d) can absorb: **the checklist**.

A show checklist is a tabular document whose *rows are works* — artist, title, year, medium,
dimensions, edition, catalogue number, courtesy or lender, insurance value, wall. It is decisive
because it **inverts the creative schema's declared unit.** The anchor states that unit explicitly:
"the unit is one named piece of work moving through revisions toward something delivered, shown or
published," anchored on "a PROJECT at a STAGE producing an ARTIFACT." A checklist is the opposite
object. It is a **register of many finished works, most of them made by other people**, assembled
because they will occupy one room for one span of dates. Nothing about it is a work in revision.

That kills (a) and (b) together. A stage value describes where one work has got to; a register
describes a set of works that already arrived. A documentation set is a *product* of the situation,
not the situation — and a row built only on documentation would indeed have been a work type, which
is why the row is not built on it.

It kills (c) because the checklist activates without any venue name at all. So do the paired
condition reports, the annotated hang plan, and the wall-text family. The venue name is demoted to a
`never_alone` in the JSON precisely because the charge is right about it in isolation.

It kills (d) because each named neighbour turns out to own a *different object* and the boundary in
each case is statable in both directions with a shared fixture — see the reciprocal table below.
The union claim only looks true if you count the show's *outputs*; it stops being true the moment you
ask who owns the register, the room and the custody chain. Nobody does.

**Verdict: the node stands.** `refuse_node: false`. Nothing was invented to keep it: `fields: []`,
`proposed_fields: []`, `also_holds_with: []`, `dimension_order: []`, and the two places where a new
key was genuinely tempting are parked in `open_question` rather than proposed.

## The node test, all three legs

CONNECTION's test: a template exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The creative
default is held as prose in `creative.json`'s `template.why`. Each leg passes on its own.

**1 — Detection signals differ, and differ completely.** The creative schema's default detection
structures are: linked assets, layers/artboards, a revision round, a brief, a delivery or handoff
set, production paperwork, a script. **Not one of them fires on this row's core evidence.** A
checklist has no linked assets and no layers. A condition report has no revisions. A hang plan is
not a brief, a delivery set or a script. The install schedule is the closest thing to production
paperwork and it is still a different animal: production paperwork records the making of a work, an
install schedule records the *placement of objects that already exist*. The row therefore contributes
seven structures the schema does not have — checklist, hang plan, loan-and-condition pair, run-dates
span, wall-text family, documentation set, install schedule — of which the first three belong to no
other roster row at all.

Two shapes here will fool a naive reader into seeing a version family, and the JSON blocks both on
the fixture. The **condition report occurs in a pair** — incoming and outgoing, around one object;
the pairing is the signal, and they are two events, not two drafts. The **wall-text family** is
several documents of *the same content at different lengths* (panel, label, large-print).

**2 — Recommended dimensions differ, in two arguable ways.** Both are prose, because
`dimension_order` must be `[]`: a dimension may only branch on a field the same entry's schema
declares, and the creative placeholder declares none. Within that constraint the recommendation is
`project` (the show) → `stage` → `artifact_type`, and it differs from the default twice.

- The default's optional top level is `client`. **This row drops it and would use `venue`.** An
  exhibiting institution is not a commissioning counterparty — it shows work it did not order — and
  a `client` level would open a branch the facts cannot fill for the large majority of shows. The
  substitution costs nothing: `venue` is already a canonical key.
- The default's `stage` values run draft → final, a **maturity** sequence. This row's run pre-install
  → install → run → deinstall → tour, a **custody** sequence. That difference is what makes a
  condition report dated *after* the closing date intelligible rather than anomalous.

Not time-first, on `00`'s own reasoning: "For document and record domains, project, function, or
subject usually comes before time because putting year first scatters related work across calendar
folders." The anchor grants a time-first exception to exactly two siblings by name
(`creative.shoot-day-media`, `creative.raw-photo-catalogue`) on the photos grounds. This row does not
claim it, even though its documentation set is capture-based, because the *packet* is not — claiming
it would be claiming the photos exception without the photos evidence. The parent-context test
decides the order: "a parent dimension should provide the context required to understand the child. A
work type such as Homework 3 is meaningful only after the course is known." `Condition report - cat
14 - incoming.pdf` is the exact analogue of `Homework 3`.

**3 — Privacy rules differ in kind, not in degree.** The creative schema's posture is confidentiality
of unpublished work. This row adds two things that are not degrees of that.

- **Third-party owners and their property.** Loan agreements, courtesy columns and condition reports
  carry names, addresses and agreed values of people who are not the corpus owner. The checklist row
  reading `Private collection` exists *because the owner refused to be named*; a filing agent must
  not undo that by resolving it.
- **A map of where valuable objects are and when they move.** A hang plan marking vitrine and plinth
  positions, plus a courier and crate schedule, plus an insurance schedule, is jointly a security
  document. The harm is physical loss, not disclosure or identity theft, and no other creative
  sibling produces it. This is the sharpest single reason the row is not a stage value: a stage value
  cannot have a threat model of its own.

Against both: "Privacy policy must be enforced before content reaches any model or external
connector." No handling class is assigned; `sensitivity` is `potentially_sensitive` only.

## Files considered and REJECTED

A row that only lists what it holds has not been researched. These were tempting and are not this
row's evidence.

- **`Artist CV 2026.docx`.** Its exhibitions list is dense with show titles, venues, years and the
  tokens `solo` and `group show` — the highest concentration of exhibition-shaped strings in any real
  file. It is `career.portfolio-work-samples`. The discriminator: the CV is *about the artist*, the
  packet is *about the show*, and the CV has no checklist, no plan, no custody counterpart. This is
  the strongest false positive the row will ever meet and it is written into `collides_with → career`
  as an explicit prohibition rather than left implicit.
- **The artwork's own working file** (`Untitled_v7.psd`, a sculpture's `.blend`). It is on the wall
  and it is not the show. `creative.self-initiated-work` or the relevant making sibling. This is the
  assignment hint's sentence, enforced.
- **A gallery membership renewal, shop receipt or mailing-list newsletter.** Venue name, nothing
  else. `Receipts and Confirmations` or `Reading Inbox`; not this row, by the venue-name
  `never_alone`.
- **A press cutting or review of the show.** Published writing *about* an exhibition. Its home is a
  reading residual; treating coverage as packet evidence would let any article about anything
  activate the domain it describes.
- **A gallery's lease or its building's fire plan.** Room-shaped, venue-named, and about the
  premises rather than the show. `legal.leases-agreements` and facilities material respectively.
- **An auction catalogue or a dealer's stock list.** Both carry checklist-shaped columns. Neither has
  a run, wall assignments or a lender column. Rejected from the kept corpus but retained as the
  reasoning behind the `A SPREADSHEET OF ARTWORKS alone` never_alone.
- **A museum's collection-management database export.** Institutional systems of record, not a show
  packet; and admitting it would make this row a collections row by the back door — see NJ-EXH-2.
- **`Opening night - 47 photos/`** (candid crowd shots). Same room, same evening, same EXIF as the
  documentation set. It is `photos.camera-events`. Retained in the JSON only as the reciprocal
  statement on the photos collision.

## The collision fixture

**`Collection inventory - insurance schedule 2026.xlsx`.**

It is a spreadsheet whose columns are Artist / Title / Year / Medium / Dimensions / Acquired / Value
/ Location. Read column-by-column against a checklist it is a near-perfect match, and it is the file
most likely to make this row fire wrongly.

What discriminates it, in the file itself and not by guesswork: **no catalogue numbers, no wall
assignments, no lender or courtesy column, no run dates, and no show title anywhere in the workbook.**
The `Location` column holds room names *in a private residence*, and a footer cell carries an
insurer's policy number. Every one of those is an absence-or-presence a reader can check without
inferring intent. It routes to `Independent Records`.

A second, milder collision is kept as a file example because it fails differently:
**`Frieze London 2026 - visitor floor plan.pdf`** has a plan, a venue, dates and hundreds of names —
but the names are **exhibitor organisations**, not works, there is no medium or dimensions column,
the document carries wayfinding furniture (entrances, toilets, cafés) that no hang plan has, and it
is addressed to an audience rather than to an installer. It routes to `Reference Clips`, on the
residual's own test — material "that is useful for later retrieval but does not belong to a current
project." Together the two fixtures cover the row's two failure modes: *register without a show* and
*plan without works*.

## Reciprocal boundaries — both directions, shared fixture named

Ten `collides_with` edges, every id verified on the roster. Each carries the boundary in both
directions and names the fixture where they compete.

| Neighbour | Shared fixture | This row owns | They own |
|---|---|---|---|
| `creative.printmaking-editions` | a checklist row reading `screenprint, edition 12/40` | the checklist — many works, one show, lenders | the impression register — one matrix, proofs, chop, numbering |
| `career.portfolio-work-samples` | `InstallView_03_SoftWeather_Whitechapel_2026.tif` | the sequenced set keyed to a plan, inside a packet | the curated ordered set beside a CV or statement |
| `photos.camera-events` | the twelve InstallView files; opening-night snapshots | documentation with a credit line and a checklist nearby | the candid gathering — a gallery depicted is not a packet |
| `creative.print-production` | `Catalogue_SoftWeather_cover_CMYK_press.pdf`; their `Museum poster on gallery wall.jpg` | the show the printed thing serves | the proof→press→run→delivery chain, whatever it depicts |
| `creative.interior-design` | `Hang plan - Gallery 2 - v4.pdf` | a plan whose annotated objects are named works | a plan whose annotated objects are furniture and finishes |
| `creative.theatre-production` | a one-evening performance inside the gallery | checklist + plan + condition reports | script + cast + call sheets |
| `legal.leases-agreements` | `Loan Agreement - Untitled 2019 - signed.pdf` | one link in one show's custody chain | the executed instrument, and its protective posture |
| `business_operations.project-delivery` | an institution's exhibition programme | the show packet | the budget, approval chain and variance report |
| `code.software-project` | a repo driving a screen in the room | never re-files inside a preserved repo root | the repository and its internal layout |
| `creative.self-initiated-work` | an artist's solo-show studio folder | the register, the room, the custody, the texts | the working files, linked assets and revision families |

The `creative.print-production` row is the one that already exists on disk with a competing fixture:
its `Museum poster on gallery wall.jpg` is a lone photograph of a poster on a wall, rejected there
and routed to `One-Off Images`. **This row reciprocates by rejecting it too**, on its own grounds —
one image, no sequence, no credit line, no checklist — which is the `AN IMAGE OF ART ON A WALL alone`
never_alone. Two rows independently declining the same fixture is the correct outcome:
"Correct abstention is a successful outcome because the product's goal is reliable organization, not
maximum file movement."

## `also_holds_with` is empty, deliberately

Two files here genuinely carry two readings — the loan agreement (legal instrument *and* custody
link) and the installation view (capture *and* documentation). Both are recorded on the file example
as `also_schema`, and the loan agreement additionally as a collision carrying the discriminator.
Neither becomes an `also_holds_with` edge, because a template may not widen its schema's
co-activation set; the landed sibling `creative.print-production` is `[]` for the same reason. Stated
here rather than left as an apparent omission.

## `proposed_fields` is empty, deliberately

`fields` is empty because a template references its schema's fields and never copies them, and the
creative placeholder declares none. Two strings this material is saturated with are deliberately
**not** proposed as keys:

- **the lender / courtesy line.** The most field-shaped thing on a checklist. Minting a key for it
  would immediately raise whether it may be a folder level, where the answer is no — a directory
  named for a private collector publishes exactly the identity the courtesy line was written to
  conceal. Recorded as NJ-EXH-1.
- **the insurance or agreed value.** A currency figure beside an object. It is a claim, a schedule or
  a sale before it is a loan; it is in `never_alone` and in the checklist fixture's
  `must_not_conclude`.

`venue` is **referenced, not proposed** — it is already a canonical key, and the recommendation that
the creative schema adopt it alongside its four candidates (`project`, `stage`, `artifact_type`,
`client`) is a recommendation to R1c recorded in `open_question`, not a change made here.

`proposed_context_terms` (thirty-five) are candidates for R6 and are marked PROPOSED. `00` states the
pattern-plus-context *shape* for course codes only; it does not list these, and the JSON does not
pretend otherwise.

## Sparse-file discipline

`IMG_2231.jpg` is this row's `HW 3.pdf`: a phone capture with no caption and no stem, sitting beside
twelve InstallView files and a checklist, where the neighbourhood is the only thing suggesting a
domain. It is `group_without_copying_facts: true`, its `facts_legal` is the universals only, and its
`must_not_conclude` blocks the show, the venue, the credit line and the screenshot-from-missing-EXIF
inference. `Private view - 19 March 18.30.ics` and `Catalogue_..._press.pdf` carry the same flag for
different reasons — attending is not staging, and depicting is not owning.

## Recommendations to R1c (cross-row; nothing was edited)

1. **Reciprocate the ten collisions.** None of the ten neighbours currently names this id.
   `career.portfolio-work-samples` and `photos.camera-events` matter most, because they are where the
   same bytes will actually be fought over.
2. **`creative.print-production` should name this row on `Museum poster on gallery wall.jpg`** so the
   shared rejection is visible from both sides rather than coincidental.
3. **Consider `venue` for the creative schema's adoption set** if NJ-R1a-1 ever resolves to option
   (b). This row is the family member that most needs it, and it costs no minting.

## Audits run before returning

`python3 -m json.tool` parses. All thirteen quoted spans of 25+ characters were extracted from the
JSON and matched against `00` under whitespace/curly-quote normalisation: twelve matched
mechanically, and the thirteenth (`Correct abstention…`) failed only because the checker did not
decode `’` — it was independently confirmed verbatim by `grep -o` before the file was written.
**No `00` quotation here is fabricated or paraphrased inside quote marks.** Every
`file_examples.source_type` is in `SOURCE_TYPES` (15/15) and every declared `file_kinds.source_types`
member likewise (11/11). Every `collides_with.domain_id` resolves on `ROSTER.md` (10/10), the
`role_split.other_domain` resolves, and all residual names are among the nine (7/7 edges, 15/15
fixtures). `venue` and `client` confirmed canonical; no key minted. `fields`, `proposed_fields`,
`also_holds_with` and `template.dimension_order` are all `[]` **with a stated reason**, not by
omission. No threshold, score, evidence count or handling class appears anywhere — the digits present
are filenames, dates inside fixture names, and one hanging centre-line figure quoted as an
*observation*. Only the two assigned files were written; no neighbour node, roster, canonical fields,
`check.py`, `src/`, SPEC or ownership register was touched.

## NEEDS-JOSEPH (this node only)

- **NJ-EXH-1 — the lender has no key and must not get one here.** The courtesy/lender line is real,
  recurrent and field-shaped, and no canonical key holds it. `client` is wrong (a lender does not
  commission); `venue` is wrong (a lender does not host). Alternatives: (a) leave it as content —
  searchable, never a dimension; this row's recommendation, because a folder named for a private
  collector publishes the identity the courtesy line was written to protect; (b) mint a
  counterparty-role key on the shared vocabulary and fence it destination-ineligible; (c) overload
  `venue` with a second role, which loses the distinction on tour. **No field proposed.**
- **NJ-EXH-2 — which row owns a standing collection inventory.** This row's collision fixture has no
  home: not a show, not a making record, columns identical to a checklist's. Routed to `Independent
  Records` here. If a collection-or-inventory row is ever added, the fixture and its four
  discriminators should move with it, and this row's spreadsheet-of-artworks `never_alone` becomes
  that row's boundary statement.
- **NJ-EXH-3 — touring breaks the single-project level.** One show, three venues: one stable
  checklist, three sets of plans, texts, schedules and documentation. Under the recommended prose
  order the show is the parent and the venue has nowhere to go except inside `stage`, which is a
  custody sequence and cannot carry an institution name. Alternatives: (a) show first, venue as a
  leaf under `stage` — lossy but harmless; (b) show first, `venue` as a genuine second level, which
  requires the creative schema to adopt `venue`; (c) venue first, which scatters one show across
  institutions and is the exhibition analogue of the year-first mistake `00` warns about.
  Recommendation offered, not taken: (b).
