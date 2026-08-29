# construction_property.site-diary — research notes (template row)

**Depth: J-DEPTH.** Deepening pass over a verified gist draft. Placeholder row (J-IND). Absorbs
legacy id `cons.site-diary` (ROSTER.md Appendix A), 1:1.

**Verdict: KEPT, on leg 1 alone.** The gist row's "stands" survives, but its *reasoning* is partly
reversed: the gist claimed the node test "passed on signals and dimensions both", and leg 2 is
withdrawn this pass. See **What changed** at the end for the full audit.

---

## Sources

- `planning/00-database-agent-product-design.md` — every quotation below and in the node file was
  machine-checked with `grep -F` against this file before writing. Quotations from neighbour memos
  are marked with the file they came from and were checked the same way (whitespace-normalised,
  because several span a line wrap).
- `planning/domains/CONNECTION.md` (node test §2, closed edge vocabulary §5, PR-6), `_CONTRACT.md`
  (rules 8, 10, 11–15), `planning/prompts/ALIGNMENT.md`, `DECISION-BRIEF.md` (D1 as narrowed, J-IND).
- `planning/domains/roster.json`, `canonical_fields.json`, `src/evidence_shape/vocabulary.py`.
- **Neighbours read in full before writing, per the addendum:**
  `construction_property.research.md` (the deepened schema anchor — the default template this row is
  measured against), `construction_property.construction-project.research.md` (the branch root),
  `construction_property.progress-photos.research.md` (the closest relative in *kind*),
  `construction_property.variation-claim.research.md`, `.snagging-defects.research.md`,
  `.timesheet.research.md` (a landed refusal that routes coverage *to* this row),
  `.site-health-safety.research.md` + `.json`, `.materials-delivery.research.md`,
  `business_operations.meeting-record.research.md`, `business_operations.project-delivery.research.md`.

---

## The charge against this row, stated at full strength

The dispatch put three charges. None is a straw version and the first is serious.

> **(a)** A diary is plausibly a **format** — a dated log — and the roster triage dropped 18 legacy
> ids as format/SOURCE_TYPE material including logs. **(b)** It may be a `work_type` of
> `construction-project`. **(c)** Its content may be entirely evidence *for* other rows — delays for
> `variation-claim`, defects for `snagging-defects` — leaving it a conduit rather than a world.

Charge (a) is the one that could kill the row, and it is sharper here than the roster triage makes it
sound. A log is a *shape*: a thing dated and appended to. Shift rotas, medication charts, mileage
sheets, delivery schedules, food diaries, ship's logs and lab notebooks all have it. `00`'s own
definition of the residual library is a description of what a shape-only row would be filing:
*"Residual templates provide safe, intentionally broad destinations for files that have no reliable
deeper association."* Against that, *"Domain templates create detailed, meaningful hierarchies for
recurring areas of life"* — and the whole question is whether "the daily record of a site" is a
recurring area of life or a recurring *file shape*.

The three charges are answered in the three sections that follow, then the node test is argued leg
by leg.

---

## Answering (a): the format charge, and why the answer is NOT `meeting-record`'s

`business_operations.meeting-record` faced a near-identical charge — *a record of what happened is a
format, not a world* — and answered it with a **series signal**: *"several documents whose titles
differ only by a date token and which share an identical internal heading skeleton"*, which it calls
*"a cross-file structural regularity"*. It was explicit about the cost: *"if the series signal is
rejected, this row is a residual."*

**A site diary must not answer the charge that way, and this pass rewrites the gist row so that it
does not.** Three reasons.

1. **It would be borrowed, not earned.** A diary is the most obvious series in the corpus. Answering
   the format charge with "but it recurs" concedes the charge — recurrence is a property of the
   *format*, not of the situation. A rota recurs. A payslip recurs.
2. **It would inherit an unsettled dependency for nothing.** `meeting-record`'s **NJ-BO-MR-1** asks
   whether a cross-file regularity is an activation signal at all, since *"Every other signal in the
   catalogue is read from one file"*. If that resolves against it, `meeting-record` falls. A diary
   row leaning on the same signal falls with it — and it does not have to.
3. **The false series is fatal to it.** `meeting-record`'s **NJ-BO-MR-3** names *a folder of blank
   meeting templates* as a false series. The construction analogue is worse and commoner: a pad of
   **blank daily-log forms** autosaved one per day. Perfect skeleton, perfect date token, zero
   content. It is now a named fixture (`Daily log template - BLANK.docx`) and its whole job is to
   fail this row.

### What this row answers with instead: exogenous slots and the nil return

The positive, single-file, machine-checkable thing that remains when you subtract "dated" and
"appended to" is a **fixed slot set for conditions exogenous to the work**: weather, labour present
counted *by trade*, plant on site (including plant standing idle), visitors, deliveries received.
These are not descriptions of what was produced. They are descriptions of the *circumstances under
which* production was or was not possible.

The sharp form of that, and the row's actual fingerprint, is the **nil return**. A diary page for a
day on which nothing happened is a complete, meaningful, filed document — labour 0 across every
trade, plant "standing", events box reading *"no works — site closed, persistent rain from 06:30"*,
signed anyway. Fixture: `Day sheet 2026-02-03 - rained off.pdf`.

**Every other row on `construction_property` produces documents that exist because something
occurred.** An instruction was issued (`variation-claim`). A valuation fell due (`final-account`). A
fault was found (`snagging-defects`). A drawing was superseded (`drawings-revisions`). A meeting was
convened (`meeting-record`). A delivery arrived (`materials-delivery`). None of them can produce a
document about a day on which nothing happened, because there was no trigger. This row can, and the
resulting document is not a degenerate case — it is the row's *most* characteristic one, because
proving that nothing happened is precisely what a diary is kept for.

That is not a format. "Dated log" is the format; "the schedule-driven record of exogenous site
conditions, filled independently of events" is the situation. And it satisfies `00`'s own bar for a
domain template over a residual: a nil-return day sheet has a strong, positive, machine-readable
association — to a site and to a run of conditions records — rather than *"no reliable deeper
association."*

**Honesty clause, stated as baldly as `meeting-record` stated its own dependency:** the nil-return
signal is **inference**, not a design-doc claim. `00` does not discuss nil returns anywhere; I read
the structure off the real document family and marked it `Provenance: inference` in the node file. If
R1c rejects it, this row's leg 1 collapses to "a form with a weather box", the format charge lands,
and the row should be refused into Independent Records and `construction-project`. I would rather
state that clearly than hide the row's single point of failure.

---

## Answering (b): the `work_type` charge — and why the spine's concession does not settle it

The branch root has already conceded the structure, twice and verbatim:

> "Similarly `variation-claim` owns the numbered instruction, **`site-diary` owns the dated daily
> record**, and `subcontract` owns the works package. The gist row claimed all of them."
> — `construction_property.construction-project.research.md`

> "`site-diary` holds the day; `final-account` holds the money; nobody holds the plan."
> — same file

and it demoted *"the site-record structure"* out of its own activation evidence to do so.

**That concession is not an answer to charge (b), and both `variation-claim` and `snagging-defects`
say so in the same words:** a spine concession *"establishes which of two rows owns a structure; it
does not establish that the structure earns a row at all. Both rows could be wrong together."* This
row does not lean on the concession. It leans on the section above.

What the concession *does* do is close a different door: it means the `work_type` reading is not
merely unproven but has been actively withdrawn by the row that would have to host it. And the schema
anchor's list of things that are values rather than rows — *`variation`, `snagging`, `dilapidations`,
`retention`, `preliminaries`, `certificate`, `drawing`, `schedule`, `survey`, `valuation` and
`report`* — is a list of **document types**. "Daily record of site conditions" is not on it and is not
of its kind: the listed values name what a document *is*, whereas a diary is defined by the *cadence
and trigger* under which it is filled.

---

## Answering (c): the conduit charge — the neighbours refuse the gift

Charge (c) says the diary's content belongs to its consumers. The consumers disagree, in their own
landed words:

- `variation-claim`: *"Citation in a bundle index is not a fact writer."* and *"Purpose may be read
  from that folder; ownership may not."* It names `Site Diary - Oakfield Rd - 2026-03-14.pdf` as its
  **outbound** fixture — *the file that must not be lost to it* — and turned that into its own
  `never_alone`.
- `snagging-defects`: *"the diary is a dated daily record and this row is a tracked list; the diary
  entry is a **citation** of a defect, and citation is not a fact writer."* It draws **no edge** at
  all and defers policing to this side.

So the conduit charge, taken seriously, would have this row hand its bytes to rows that have each
written a rule refusing to accept them. That is not a conduit; it is a source with disciplined
consumers.

There is also a quantitative answer, marked **inference**: the overwhelming majority of a diary's
pages are never cited by anything. A three-hundred-page run supports a claim on perhaps six of its
days. The other two hundred and ninety-four pages — weather, trades present, plant standing, nothing
of note — have no downstream consumer at all. A conduit whose content nobody downstream wants is not
a conduit. And the reason those pages are kept is itself evidential: **the diary is the only row in
this family that owns the negative record.** A delay claim needs the unremarkable days to prove they
were unremarkable. Nothing else in the corpus does that job.

---

## The closest relative in *kind*: how this row differs from `progress-photos`

`progress-photos` is the sibling this row most resembles in *rhythm*, and it earned its row on an
argument this row is **not allowed to use**:

> "Every other row on `construction_property` is recognised by document structure — a header, a
> reference, a table, a signature block. **This row is recognised by capture metadata, rhythm and
> place.** That is a different detection method, and a `work_type` *value* cannot carry a different
> detection method; only a template can."
> — `construction_property.progress-photos.research.md`

**This row is recognised by document structure, like every other sibling.** It cannot claim to have
left the family's detection method; it has to find its difference *inside* it. That is the harder
case and it is why the nil-return argument above had to be positive and single-file rather than
methodological.

The dispatch is also right that the two discriminators must differ, and they do:

| | `progress-photos` | `site-diary` |
|---|---|---|
| Detection method | capture metadata, rhythm, place | document structure |
| Discriminator | **repetition of place across time** — *"a camera roll goes to many places once, a site walk goes to one place many times"* | **exogenous slot set filled on a schedule**; sharpest as the nil return |
| What drives the rhythm | *attendance* — a capture exists only where someone went and pointed a camera | *the calendar* — a page exists for a day nobody visited, and says so |
| Behaviour on a nothing-day | no files produced | the row's most characteristic file |
| Evidence class | the works themselves, imaged | the conditions around the works, tabulated |

The last two rows of that table are the load-bearing distinction and they are the reason the
discriminators are genuinely different rather than rephrased. `progress-photos` is *observational*:
its evidence is generated by an act of observation, so an unobserved day leaves no trace.
`site-diary` is *obligational*: the entry is owed whether or not anything is seen, which is exactly
why an unbroken run is admissible and a gap is damaging. Repetition of place could never discriminate
this row, because a diary of a site that was closed for a fortnight has fourteen pages and zero
visits.

**Where the two compete for the same bytes:** the app-generated diary page with embedded photo
thumbnails, and the photo pack exported from the same app on the same day. Discriminator, already in
both JSONs and unchanged here: *"Camera EXIF, GPS, and capture time can support deterministic
photo-event proposals"* on standalone image files supports `progress-photos`; a document page with an
embedded thumbnail supports this row. Restated as a rule this row enforces on itself: a diary page is
complete without any photograph, and a photo set is nothing *but* its captures — so an image file
with no surrounding page never fires here, and a page whose photos are stripped still does.

I also record, without reopening it, that `progress-photos` sets `time_first: false` and the schema
anchor extends that to the whole family. This row sets it false for the same reason and is explicitly
**not** claiming the capture-media exception.

---

## The node test, argued leg by leg

**The default template this row is measured against**, verbatim from the deepened schema anchor:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles* (a service-charge year,
> a rent-review cycle). **Not time-first.**

### Leg 1 — detection signals: **PASSES**, and the row stands here or nowhere

The family default is recognised by instruction-bearing document furniture: a job reference, a fee or
appointment, a client party in a role slot, a title block, a valuation cycle. This row's fingerprint
is none of those. It is the exogenous slot set — weather paired with a **trade-counted** labour
return paired with plant-on-site — and the nil return that only a schedule-driven document can
produce. That pairing occurs on no other row in the family, and its behaviour on a nothing-day is
unavailable to every event-triggered sibling. Argument in full above.

Two supporting signals are held deliberately at *supporting* strength this pass:

- **Serial dating**, demoted (see What changed). It strengthens a reading; it never opens one.
- **Parent-folder context** naming a site, job number or month — a clue, never alone, per the
  family's constitutional never-alone on the address.

**Verdict: passes.** With the stated dependency on the nil-return inference surviving R1c.

### Leg 2 — recommended dimensions: **FAILS as a distinguishing leg** (reversed this pass)

The gist row claimed: *"this is the only construction row whose second level is genuinely a period,
because users retrieve a diary by date."* Both halves of that are true and neither earns anything.

The anchor's default *already licenses* a period level *"only where the situation genuinely
cycles"* — and if a service-charge year cycles, a daily diary cycles harder. So the diary's site →
period → function order is the default template **applied**, not departed from. The anchor is
explicit about the trap: *"Reversing is not a difference that earns a node"*, and it warns that dates
are the thing siblings will most be tempted to claim on, *"because this world is drowning in dates"*.

I am reversing the gist verdict here rather than defending it. The dimension recommendation is
preserved unchanged in the node file (site first — a bare 14 March is meaningless and actively
harmful across a contractor's corpus, per *"a parent dimension should provide the context required to
understand the child"*), but it is no longer offered as a node-test leg.

### Leg 3 — privacy rules: **FAILS as a distinguishing leg**

The row is `potentially_sensitive`, and the reason is real: a diary is a daily attendance record of
named individuals, and `00`'s corpus sentence names the categories the moment it does — the corpus
*"can include identity documents, account statements, tax records, medical information, legal
records, credentials, private correspondence, GPS metadata, employment materials, and educational
records"*. But `potentially_sensitive` **is** the `construction_property` default. Being at the family
posture is not a difference under CONNECTION.md §2. The row that genuinely runs stricter is
`site-health-safety`, which is exactly why this row defers the accident-book entry to it — a
concession that row records on its own side: *"the accident-book entry itself — deferred here by that
row, with the medical ordering running first."*

### Overall

**Kept on leg 1 alone.** That is the same footing as `construction-project` and `snagging-defects`,
and it inherits `snagging-defects`' **NJ-CP-SNAG-4** — if R1c rules that one passing leg is
insufficient on a field-less schema, this row falls *with* the family rather than being argued out
separately. Recorded as open question (3).

---

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence.

| File | Why it is not this row's |
|---|---|
| **`Site meeting 08 - minutes.pdf`** *(gist; kept, and it is the load-bearing collision)* | A dated narrative of a site, in the same folder, often by the same author. The trigger differs: a meeting was **convened**. It carries an attendee list, numbered actions with owners and a next-meeting date, and it cannot exist for a day when nothing was convened. `business_operations.meeting-record`. |
| **`Daywork sheet 018 - signed by CA.pdf`** *(added this pass — the refused `timesheet` row's own bytes)* | The same labour table this row claims, plus a **countersignature by the other side** and a reference to a described extra. `variation-claim` has landed it: *"The sheet is not a record of who worked; it is evidence tendered to someone who must pay."* Taking it here would contradict a landed refusal. Now a fixture and a `never_alone`. |
| **`Induction register - March 2026.xlsx`** *(added this pass)* | Names, dates, signatures, a serial dated structure and a site header — everything this row looks for. It is the statutory attendance roll, conceded to `site-health-safety` by the `timesheet` refusal, **under a stricter privacy posture**. A day page that *mentions* an induction stays here; the register does not. |
| **`Daily log template - BLANK.docx`** *(added this pass — the false-series fixture)* | Perfect form furniture, perfect dated recurrence, no content. It exists to fail this row, and it is the reason the nil-return signal is written as a page reading **zero**, not a page reading **empty**. Direct debt to `meeting-record`'s NJ-BO-MR-3. |
| **`Site diary 2026-03-12.docx`** *(added this pass — the sparse case)* | Genuinely this row's, and named here because `construction-project` names the same bytes: it carries **no job reference at all** — *"the `HW 3` case in construction clothing, and neither row may invent one."* It groups; it writes no site fact. |
| **`diary 2026.docx`** *(gist; preserved)* | A personal journal. Identical filename vocabulary, identical dated-entry structure, opposite privacy posture. Protected Records. NJ-CP-DIARY-1. |
| **`Accident book entry - 2026-03-14.pdf`** *(gist; preserved)* | An injury narrative about a named person. `site-health-safety` with `also_schema: "medical"`; the protective ordering runs first. |
| **A programme / Gantt (`Programme rev F.pdf`)** | A plan, not a record of a day. *"`site-diary` holds the day; `final-account` holds the money; nobody holds the plan."* — the branch root's own line; `construction-project`'s. |
| **A snagging schedule** | One row per fault with a rectification status: a **tracked list**, not a dated run. `snagging-defects`, which draws no edge back and asks only that a diary entry not be read as a register fact. |
| **A delivery note arriving alone** | Supplier furniture — note number, letterhead, order reference, itemised quantities. `materials-delivery`, or Receipts and Confirmations if it has no run around it. New edge below. |
| **A weekly RAG status report with no site conditions** | `business_operations.project-delivery`'s generic shape. New edge below. |
| **A lab notebook** | *(gist; re-checked)* Also a serial dated record, still rejected: no shared discriminating evidence at the token level — no weather slot, no trade names — so the edge would be topic similarity, which CONNECTION.md §5 excludes. |
| **A ship's log, a mileage sheet, a medication chart, a shift rota, a food diary** | The format charge's whole army. Each has date-plus-append and none has the exogenous slot set. They are why the row is argued on slots and not on recurrence. |
| **A CIS return or a site payroll run** | Hours against **rates**, for the purpose of paying someone. `hr` and `finance`; the `timesheet` refusal routed it there and this row does not reopen it. |

---

## The collision fixture, in both directions

**Inbound — the file that would wrongly fire this row:
`Daily log template - BLANK.docx`.**
Every deterministic signal this row has except one is satisfiable by it: the full slot set, the form
furniture, a perfect dated series, the right extension, the right folder. The single signal it fails
is the one this pass added — the slots are *empty*, not *filled with zero*. It is the cleanest
demonstration available that the row's case is the nil **return** and not the nil **page**, and it is
why serial dating had to be demoted: under the gist row's wording, fourteen autosaves of a blank pad
were this row's strongest evidence.

Second inbound, at lower confidence: **`diary 2026.docx`**. Filename, structure and source type all
match, and only content settles it — which is what P7 gates. NJ-CP-DIARY-1.

**Outbound — the file that must not be lost *to* this row:
`Site Diary - Oakfield Rd - 2026-03-14.pdf`.**
It is this row's, and `variation-claim` names the identical bytes on its side as *the file that must
not be lost to it*, because in practice it sits in `Oakfield claim/appendices/` and is cited by page
number in an extension-of-time index. That row wrote the rule; this row writes its half: **membership
of a claim folder, or citation in a bundle index, never activates `variation-claim` — and never
prevents this row from activating.** The reciprocal is exact and neither side had to be edited to
achieve it.

Third, for `site-health-safety`: **an injury described in a diary entry and in a report on the same
date** — that row's named shared bytes. Ordering: the safety/medical reading runs first, and this row
keeps only the day narrative.

---

## Reciprocal boundaries

Every neighbour below was read in full before this table was written and none is contradicted. Where
the boundary is authored **one-way** it is marked, and it is recorded as an open question rather than
written into anyone else's file.

| Neighbour | This row must not take | The neighbour must not take | Same bytes, both sides |
|---|---|---|---|
| `business_operations.meeting-record` **(one-way; reciprocal owed)** | an attendee list with numbered actions and a next-meeting date | a schedule-driven day page with weather, labour and plant, produced for a day with no meeting | `Site meeting 08 - minutes.pdf` |
| `construction_property.variation-claim` *(landed; states its side)* | a numbered variation or claim reference, a quantified time or money consequence, an addressed notice, a **countersigned** dayworks sheet | an unaddressed daily entry in an unbroken run | `Site Diary - Oakfield Rd - 2026-03-14.pdf`; `Daywork sheet 018 - signed by CA.pdf` |
| `construction_property.snagging-defects` *(landed; declares no edge)* | a tracked list with one row per fault, a rectification status and a responsible trade | a diary entry that records a fault being found — *citation is not a fact writer* | a defect first noted in a day page and later registered |
| `construction_property.construction-project` *(landed; conceded the structure)* | the award sequence, the contract-particulars block, the programme, the completion-and-handover envelope | the dated daily record, which it has demoted out of its own activation evidence | `Site diary 2026-03-12.docx` |
| `construction_property.progress-photos` *(landed)* | standalone captures with EXIF and a place that recurs | a document page with an embedded thumbnail | an app export containing both a day page and its photos |
| `construction_property.site-health-safety` *(landed; states its side)* | the accident-book entry, the permit form, the RAMS, the induction and attendance register | a day narrative that merely mentions a permit or an induction | `Induction register - March 2026.xlsx`; an injury on both a diary page and a report of the same date |
| `construction_property.materials-delivery` *(landed; **invited** this authorship)* | a delivery note with supplier furniture — note number, letterhead, order reference, itemised quantities | a "received 8no. lintels" line inside a day page | a signed delivery note filed with the week's diary |
| `construction_property.timesheet` *(**refused**; routed coverage here)* | — | — | it assigns the labour allocation sheet to this row as *"the numeric half of the daily record"*; this row accepts it and does not reopen the refusal |
| `business_operations.project-delivery` **(one-way; reciprocal owed)** | a RAG status, a workstream/deliverable breakdown, a sponsor, a stage gate | a progress report whose look-ahead is expressed as trades, plant and site conditions | `Weekly progress report No 12 - Oakfield.docx` |
| `hr.payroll-benefits-administration` *(gist edge, preserved)* | pay rates, deductions, a tax reference, a payroll-period header | a site or cost-code column, plant standing time, a weather line | `Labour allocation w-c 09-03-26.xlsx` |
| `logistics.route-dispatch` / `manufacturing.production-record` *(preserved)* | a vehicle registration and drop sequence; a batch, line or work-order reference | a fixed site, a trade-by-trade labour return, a weather slot | a daily operational log with hours and downtime |

**Neighbours considered that did NOT get an edge**, preserved from the gist pass and re-checked:
`finance.household-property` (a homeowner's builder day-sheets — nothing in its detection signals
fires on a labour return; and the anchor's professional-versus-householder seam turns on
**instruction**, not on the address); `legal.leases-agreements` (no shared evidence; a diary has no
execution block); `academic`/`research` (the lab notebook, above); `photos` as a schema (the
collision that matters is the sibling template, and `collides_with` joins same-kind pairs).

---

## `proposed_fields`

**None.** The `construction_property` schema declares no field rows (D1 as narrowed, PR-6,
`_CONTRACT` rules 10 and 15) and a template may not mint keys.

Two candidates are recorded **in prose only**, deliberately unminted, and this pass **seconds the
family's existing proposals rather than minting variants**, per the dispatch: a **site/project** key
(this row's true top dimension) and a **period** key. Nearly every row in this family wants both,
which is the argument for the schema row proposing them **once** rather than twenty-seven templates
proposing near-synonyms — exactly the one-concept-two-vocabularies failure `_CONTRACT` rule 8
documents. `progress-photos` reached the same conclusion from the other direction (reuse the `photos`
schema's keys through a co-activated file rather than mint `site_capture_year`), and
`business_operations.meeting-record` asks that its `organization` proposal be adjudicated *"once at
R1c together with the schema row's proposal and `construction_property`'s"*. This row asks to be
included in that single adjudication and proposes nothing of its own.

Explicitly **not** proposed: any date or day key. NJ-CP-VAR-3's reasoning applies unchanged, and a
row that has just withdrawn its dimensional claim has no business minting the key that would restore
it.

---

## NEEDS-JOSEPH

- **NJ-CP-DIARY-1 · The personal-journal collision.** *(preserved from the gist pass, unchanged.)* A
  site diary and a private journal share a filename vocabulary, a structure and a source type.
  Detection cannot separate them before content is read, and reading content is exactly what the
  privacy policy gates: *"Privacy policy must be enforced before content reaches any model or
  external connector."* Stated reciprocally: this row claims only files showing the diary form
  furniture; anything else named "diary", "journal" or "daybook" defaults to the protective residual
  home. **Alternatives and their costs.** (i) Protective default, as written — cost: some genuine
  site diaries land in Protected Records and are never offered to the construction tree. (ii) Allow a
  work-context override where the parent folder is a job folder — cost: the folder is the very clue
  the family's never-alone list forbids acting on alone, and it fails for a user who keeps a personal
  journal in a work folder. (iii) Ask the user once per diary-shaped cluster — cost: review burden,
  but it is the only option that is wrong in neither direction. My recommendation is (i) with (iii)
  offered at review.
- **NJ-CP-DIARY-2 · The labour allocation sheet.** *(preserved, unchanged.)* Its site reading is here
  and its pay reading is `hr.payroll-benefits-administration`'s; `construction_property.timesheet` is
  refused and routed it here as *"the numeric half of the daily record"*. This row claims the sheet
  only where it carries a site or cost-code column and no pay rates; where rates or deductions
  appear, the hr row and its stricter posture win. R1c should **confirm** the split rather than
  inherit it.
- **NJ-CP-DIARY-3 · NEW · Is the nil return a signal the pipeline can actually read?** The row's leg
  1 now rests on it, so the question is load-bearing. It requires distinguishing *a labelled slot
  filled with zero* from *a labelled slot left empty*, in an extracted representation. `00` says
  spreadsheet extraction yields *"visible cell values, table-like regions"* and text extraction
  yields *"structural information"*, but neither states whether a slot filled with "0", "nil" or a
  struck-through box is distinguishable from an unfilled one after extraction. **Alternatives.** (i)
  It is readable — the row stands as written. (ii) It is not readable, and the row must fall back to
  "the slot set exists and is populated at all", which readmits the blank-template false series and
  weakens leg 1 to roughly the strength the gist row had. (iii) Treat it as an LLM determination
  under P7 rather than a deterministic signal — safest, but it makes the row's defining evidence
  unavailable before content is read, which is the same bind as NJ-CP-DIARY-1. I cannot settle this
  from the design docs and have not guessed.
- **NJ-CP-DIARY-4 · NEW · Two one-way edges owed.** This row authors edges to
  `business_operations.meeting-record` and `business_operations.project-delivery`; neither names
  `construction_property` in its reciprocal table. A **site progress meeting** in particular is
  currently unowned: `meeting-record`'s carve-out leaves *"standing team meetings, one-to-ones, and
  counterparty call notes"*, and a weekly site progress meeting is a standing team meeting, but
  nothing assigns it. Recommended to R1c rather than written into a neighbour, per the hard
  constraint. The cost of leaving it: `Site meeting 08 - minutes.pdf` is this row's load-bearing
  collision fixture and only one of the two rows has written a rule about it.
- **NJ-CP-SNAG-4, inherited, not restated as new.** One passing leg on a field-less schema. This row
  now shares that exposure and asks to be answered with the family, not separately.

---

## What changed in this pass

**Preserved unchanged** (correct in the gist draft, not rewritten for its own sake): the row's
identity and purpose; the recognised material (day sheets, labour returns, plant returns, weather
records, visitor/delivery logs, progress reports, CVIs, delay records, app exports, notebook scans);
the whole `never_alone` list as written, including the address argument and the university-name
quotation with its inference marker; `proposed_context_terms`; `work_types`; `grouping_reasons`; all
six `falls_through_to` residuals with their quotations; the dimension **recommendation** itself; the
`potentially_sensitive` value and its corpus-sentence justification; all ten original file examples;
five of the seven original collisions verbatim; and both original NEEDS-JOSEPH items, one of which is
now expanded with alternatives rather than replaced. `variation-claim` records this row as already
*"states its side"*, and that line is intact.

**Added.**
1. The **nil-return / exogenous-slot** argument as leg 1's positive case, with its inference marker
   and its stated single point of failure — the row's answer to the format charge.
2. A new deterministic signal (the nil return) and a sharpened statement of the slot-set signal.
3. Five new `never_alone` entries: the demoted run of dates and the blank-template false series; the
   auto-inserted app weather line; claim-bundle citation (reciprocal to `variation-claim`'s own); the
   countersignature; the progress-plus-period shape.
4. Five new file examples: `Site diary 2026-03-12.docx`, `Day sheet 2026-02-03 - rained off.pdf`,
   `Daywork sheet 018 - signed by CA.pdf`, `Induction register - March 2026.xlsx`,
   `Daily log template - BLANK.docx`.
5. Two new collisions: `construction_property.materials-delivery` (authored at that row's explicit
   invitation) and `business_operations.project-delivery` (one-way, flagged).
6. The full leg-by-leg node test, the rejected-files table, the two-directional collision fixture,
   the reciprocal boundary table, and the explicit `progress-photos` differentiation — none of which
   the gist memo had.
7. Two new NEEDS-JOSEPH items (NJ-CP-DIARY-3, NJ-CP-DIARY-4) and alternatives-with-costs added to
   NJ-CP-DIARY-1.

**Reversed, explicitly.**
1. **Leg 2 is withdrawn.** The gist wrote *"Node test passed on signals and dimensions both"* and
   *"this is the only construction row whose second level is genuinely a period."* The deepened
   schema anchor licenses a period level in the default template *"only where the situation genuinely
   cycles"* and warns that *"Reversing is not a difference that earns a node"*. The ordering is the
   default applied, not a departure. The recommendation is kept; the leg is not. `template.why` and
   `one_line` in the node file now say so.
2. **Leg 3 is recorded as failing** as a distinguishing leg. The gist did not claim it; it is written
   down so no later reader mistakes `potentially_sensitive` for a difference when it is the family
   default.
3. **Serial dating is demoted** from "the file's organising principle … the SEQUENCE is the artefact"
   to explicitly supporting evidence, with the reason stated in the signal itself. This is the
   substantive change to the row's detection story and it is what makes the blank-template fixture
   fail rather than succeed.
4. **The verdict is restated as leg 1 alone.** The row still stands; `refuse_node` remains `false`.

**Depth note, honestly.** The memo grew from 5.3KB to roughly four times that, and the node file from
29.7KB to 41.4KB. The growth is arguments and fixtures, not restatement; where the gist draft was
already right — the never-alone list is the best thing in it — it was left alone rather than
reworded.
