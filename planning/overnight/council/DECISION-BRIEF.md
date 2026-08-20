# Decision brief — the council's six

Date: 2026-08-21 (overnight)
For: **Joseph.** Three seats sat: [design reading](seat-design-reading.md) · [what ships](seat-what-ships.md) · [what goes wrong](seat-what-goes-wrong.md).
Source of truth: [`00-database-agent-product-design.md`](../../00-database-agent-product-design.md). **Every quotation below was matched mechanically against its named source — 61 spans, 0 failures.** Where a seat is quoted it says so.

**How to read this.** Six decisions. Each one gives you the question, what is already settled (several
are less open than they look), the options, where the seats disagree and what the disagreement turns
on, and a sentence you can write. **The seats do not agree everywhere, and where they do not, this
document says so rather than averaging them.**

**One caveat about sources.** Rounds 1–4 are on disk and are used throughout. **Round 4 landed while
this was being written and it changes three sections** — D2 gains a second question, D5's fix is
narrowed to one option by execution, and one seat argument is corrected. Round 5 (scope) does not
exist yet.

---

## Read this first — it reframes two of the six

**`00` contains no tables.** Zero pipe characters in 286 lines; no section numbers either. The
`| Domain | Fields |` table that D1 and D6 are both arguments about, and the §-numbers the whole
project cites, exist only in `01-product-design-structured.md` — a rendering made for implementation
reference, whose own header, dated 2026-08-19, before any SPEC in this wave, reads:

> Status: **structured view** — derived from the source of truth, not a substitute for it
> Source of truth: `00-database-agent-product-design.md` — Joseph's wording is authoritative

What `00` actually says in §3.11 is six sentences, each hedged:

> Academic files **may use** school, term, course, instructor, and work type. College application
> files **may use** target university, application cycle, application document type, and purpose. …

`01` rendered them under a column headed `Fields`, and the modal disappeared. Four downstream
artifacts then cited the table as the design.

This matters twice below: it removes the "prose vs table" question in D6 entirely (a precedence rule
was written and then not applied — nothing needs deciding), and **it invalidates the stated
justification two of three seats gave for their D6 recommendation.** See D6.

It does not weaken round 1's F-1 proof, which is the thing that opened D1: §3.8's four role fields
appear in none of §3.11's six *sentences* either. That proof survives the correction intact.

---

# D1 · The field catalogue — how far open

### The question
**Does the launch field catalogue follow §3.11's six domain sentences, or §3.15's six launch domains
— and does the 560-entry catalogue write field rows at all?**

### What is already settled
- **The fully-closed reading is internally impossible.** Round 1 F-1: §3.8 states four role fields
  outright — *"The agent should model these as distinct facets, such as authored_by and target_school,
  or our_firm and client"* — and P6's Done-means 13 and 22 both require `authored_by`, which
  Done-means 2 forbids. So the question is *how far*, not *whether*. **This is not a matter of
  judgement.**
- **Launch scope is stated, unhedged, in one sentence (§3.15):** *"The initial release should fully
  support only the domains required to validate the product on real heterogeneous corpora: academic
  coursework, college applications, research and lab work, career and recruiting, photos and captures,
  and code projects."*
- **The catalogue is not deleted under any option.** §3.15: *"Other domains remain placeholders until
  user demand and corpus evidence justify detailed templates."* Placeholder is the design's own word.
- **A domain is both things (§3.15):** *"a fact schema describing the information the system may
  extract from files in that domain, and a folder template describing the small subset of those facts
  that may become physical folder levels."* "Routing aid instead of fact schema" is not a
  distinction the design offers — but *the catalogue writes no field rows at launch* still is.
- **`capture date` is a file fact.** §3.2: *"capture date = 2026-07-17 is the file fact derived from
  it."* Its absence from P6's catalogue is a consequence of D1, not a naming question.

### The options
| | Name | What ships |
|---|---|---|
| **1** | **§3.11 launch set** | §3.11's six domain sentences + the six universal fields + `download_session` + §3.8's four + `capture date` ≈ **42 fields**. Finance has fields; career/recruiting has none. Catalogue writes no field rows. |
| **2** | **§3.15 launch set** | Option 1 **plus a career/recruiting fact schema** — §5.4 already gives its dimensions: *"a Career template may define company → role or recruiting cycle → document type"*. ≈ **46 fields**. |
| **3** | **Fully open** | §3.11 as seed; the 560-entry catalogue loaded as §3.6's validator allow-list — **2,233 fields, 429 of 560 entries marked `provenance: proposal`**. |

### The seats
- **Design:** neither of the framed options. §3.15 already scoped this; the catalogue needs a
  launch/placeholder flag, not a deletion.
- **Ships:** option 1. One task touched (P6 Task 2), nothing re-done, and **opening is the two-way
  direction while closing is not** — 2,233 fields down to 42 means superseding every fact written
  against a removed field, which §8.2 forbids deleting.
- **Risk:** option 2, explicitly — *"Ship §3.15's list, not §3.11's table, and not the catalogue."*
  SERIOUS. Option 3's failure needs cloud mode plus a misactivation; option 1's failure is a visible
  residual pile.

### The conflict, and what it turns on
**Nobody recommends option 3, and the three seats' real disagreement is exactly four fields.**

Options 1 and 2 differ on one thing only: **does career/recruiting get a fact schema at launch?**
Finance is not the other half of the difference — §3.15 says finance ships *"first as safety
domains"*, and "first" sequences rather than excludes, so Finance keeping its §3.11 fields is
compatible with both.

What the career question turns on is not the design — §3.15 settles that career ships — but a
**binding standing decision**. `04-resolutions.md` (marked *binding*) S3: *"Career/recruiting fact
schema (§3.11) and Code + Finance templates (§5.4) stay deferred … Joseph authors these when those
parts come up."* Option 2 requires you to author them now, which is what "when those parts come up"
now means, since P6 is the part.

**One thing changes regardless of your answer, and it is not a decision.** P6 Task 2 currently reads
*"recruiting, identity, medical and legal have no field rows and acquiring one fails the test (S3)"*
(`PLAN-SKELETON.md:581`). S3 said **deferred**. Task 2 hardened that into **forbidden**. Deferral is
not prohibition, and the hardening is a drift from S3 that both the design and risk seats caught
independently.

**Where the risk seat overstates.** Its case against option 3 is a privacy path — a protected
characteristic reaching a cloud prompt as a candidate label — that needs cloud mode, a wrong domain
activation, and a `destination_eligible` column nobody has filled. It says so itself. Nobody is
arguing for option 3 anyway.

### Recommendation
**Option 2**, from the **risk seat**, with the design seat's textual backing (§3.15 is the only
unhedged scope sentence in the document, and career is in it).

**Ships-seat dissent, and it is a good one:** option 1 is the minimum edit and career can be added
later at near-zero cost, since **adding fields is the reversible direction by its own analysis**. If
you would rather not author career fields at 3am, option 1 plus a note that career is owed before P10
loses you very little. The ships seat's other dissent — that a catalogue consumed by nobody until P10
will rot, and re-verifying 560 entries later costs more than wiring them now — argues for option 3
and it explicitly declines to press it.

**One thing no option fixes, and round 4 raised its cost.** Round 1 F-2 found that four of the seven
universal fields Task 2 creates have no producer — `file type`, `creation date`, `language`,
`sensitivity status`. Round 4 adds that three of them are named **literally** in a downstream SPEC's
Contract-in: P11's residual dossier (§7.7, marked *literal*) lists *"filename, file type, creation
date, extracted text or OCR, metadata, sensitivity state…"*, and P9 reads `sensitivity status`. These
are not spare columns waiting for a later part — **two later parts read them on day one.** Either name
the producing task or put the row in Deferred naming P11 §7.7 and P9 §4.2 as the blocked consumers.
(C-11)

### Reversibility
**Two-way opening, one-way closing.** Growing 42 → 46 → more is additive. Shrinking is not: facts
written against a removed field cannot be deleted under §8.2, only superseded, and a superseded fact
whose field no longer exists is unreadable. Cost of being wrong in the narrow direction: a later
additive edit. Cost of being wrong in the open direction: a data migration you cannot fully perform.

### What it blocks
**P6 Task 2 and Task 13.** Task 2 is the second task of the next part anyone builds.

### The sentence to write
> The launch field catalogue is §3.11's universal set + `download_session` + §3.11's six domain rows
> + §3.8's four role fields + `capture date` + a career/recruiting schema from §5.4's dimensions.
> It is extensible only by a ratified edit to the authored table, never at run time. The 560-entry
> catalogue is a placeholder library and a recognition aid; it writes no field rows at launch.

---

# D2 · `sensitivity` — one record or three

### The question
**Which single record is authoritative for a file's sensitivity — the fact layer's row, or the
privacy gate's classification — and *which part produces a classification at all?***

Round 4 added the second half and it is not a detail. **No part in `02-segmentation-map.md`'s
thirteen claims the sensitivity detector**, and no SPEC names an owner. P7's Deferred row: *"The
detector rule set, its signals, and its thresholds are hand-authored. P7 publishes the vocabulary
the detectors write into."* So until you name a part: `basis = detector` has no producer,
`Gate.release` returns `Denied(unclassified)` for **every real file**, `files.sensitivity_state`
stays NULL after P7 ships, and P9's, P10's, P11's and P12's *carried from P7, never re-derived* rows
carry nothing. **A deferral needs a part to be deferred to.** (C-2)

### What is already settled
- **All three seats say one record.** No seat defends three. The ships seat: *"I would not build
  it."* Agreement here is total; move on.
- **It is a fact.** §3.1: a file can be *"potentially sensitive. These are separate facts about the
  same file."* §3.11 puts `sensitivity status` in the universal set; §3.12 names `sensitivity` in the
  `fields` table; §8.4 says *"The classification is itself evidence-backed and can be revised by the
  user."*
- **A user reclassification is a `user_confirmed` fact**, conditionally on the above — §3.13 defines a
  user-confirmed fact as one *"explicitly accepted, entered, renamed, merged, or corrected by the
  user"*, and §8.4's reclassification is a correction.
- **The defect has already fired here once.** `src/orchestrator.py` fed P2's `handling_class` from
  P1's `sensitivity_state` — two concepts, one column apart — and **no test failed, because both were
  NULL.** It now reads `handling_class=None` with a comment explaining why.
- **The two plans do not currently join here at all.** Counted over P6's 1,621 lines by round 4:
  `SensitivityFacts` **0** · `ClassificationRecord` **0** · `mirror_state` **0** ·
  `SensitivityStateWriter` **0**. P7 is built on a four-method protocol it says P6 implements, and
  P6's read surface publishes no method of that shape. Round 3 A9 found the two plans joining on a
  *name*; round 4 found that on P6's side **there is no name at all.** Whichever option you pick, one
  task has to publish the surface.

### The options
| | Name | Authority |
|---|---|---|
| **i** | **Fact-layer authority** | The §3.11 `sensitivity status` fact in `file_facts` is authoritative; §8.4's five classes are its values; `files.sensitivity_state` is a mirror. |
| **ii** | **Gate authority** | P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative; the §3.11 fact is a read-only projection with no independent writer; `files.sensitivity_state` holds a `HANDLING_CLASSES` member verbatim or is dropped. |
| **iii** | **Three records, reconciled** | Nobody recommends it. |

### The seats
- **Design:** (i) — *"One record, in the fact layer, and §8.4's five classes are its values."*
  Confidence: *implies it*, not *states it*.
- **Ships:** (ii) — **zero new tasks.** P7 Task 4 is already written for it (`SensitivityFacts`
  protocol, injected `SensitivityStateWriter`, `mirror_state`); P1 needs a ~15-line publish; the
  orchestrator needs one line.
- **Risk:** (ii), and this is **the one risk it would not ship without resolving.** CRITICAL —
  *"the only one whose failure is invisible at rest."*

### The conflict, and what it turns on
The (i)/(ii) split is **smaller than it reads** and collapses on the part that matters: both key the
record per `(file, content_hash)`, so neither loses the version binding that round 3 A3(b) shows the
cost of. What is left is which layer holds the writer, and the ships seat's answer — P6 owns the row,
P7 owns the value, P1 mirrors as an identity — satisfies both readings.

**The real open question is one the agreement hides, and the design seat is the only seat that
raises it:**

§8.4's five classes are `Public or low sensitivity` · `Personal but non-sensitive` · `Sensitive
personal` · `Highly sensitive or credential-bearing` · `Unreadable or unclassified`.

The first four answer *"what is this file"*. **The fifth answers *"why can I not decide"* — an
extraction outcome, not a property of the content**, and §3.13's reliability states already carry
that role. If the fifth belongs to the gate rather than to the file, §8.4's list is a gate vocabulary
and the §3.11 fact needs its own — **two records, and the seats' agreement on "one" was agreement on
the wrong noun.** The design seat says plainly it cannot claim the design implies its answer over
that one.

**This is the same hole round 1 F-9 found from the other end.** F-9: P7's mapping from P4's nine
`completeness` values to `unreadable_unclassified` has no design source, in a part whose first
constraint is that it owns no detection rule. Nine extraction outcomes are being mapped onto a
sensitivity vocabulary because one member of that vocabulary is itself an extraction outcome. **Two
review artifacts found the same seam and neither connected them.** Answering D2 without answering
this leaves F-9 unanswerable.

### Recommendation
**(ii)**, from the **risk seat**, endorsed by the ships seat at zero task cost. Plus two disciplines
neither plan currently carries:

1. **`mirror_state` is a validator, not a translator.** `files.sensitivity_state` holds a
   `HANDLING_CLASSES` member verbatim. A mapper implies a second vocabulary, which is a fourth
   spelling. (Round 3 A10.)
2. **Every assertion about the value compares a value, never non-nullness.** P7 Task 22 currently
   asserts non-null, and the shortest edit that turns it green is restoring exactly the wrong line
   that was deleted on 08-21.

**Design-seat dissent:** it reads the fact layer as the home and flags that §8.2 lists `Sensitivity
state` and `Current and historical file facts` as two separate lines, which is a real textual
argument for two records. It is the best argument on that side and it does not defeat (ii).

**And answer two more things in the same breath**, or the record you pick stays empty:

- **The fifth-class question** above, or round 1's F-9 stays open.
- **Which part runs the detector.** Round 4's recommended form of an answer is that it be *stated* —
  it be *stated* — a fourteenth part, or P7's caller deferred to Wave 3, but *"stated in
  `02-segmentation-map.md`, not left implicit in a Deferred cell"*. Verified live after a real
  `run_wave2`: `bundle_file_entry.handling_class None, None` · `files.sensitivity_state None, None`.

### Reversibility
**Close to one-way.** Classifications written against the wrong authority accumulate under §8.2's
no-delete rule; reversing means superseding every one and re-deriving. The *spelling* is two-way
today and one-way the moment P6 Task 2 runs, because `field_key` becomes the join key P7, P8, P9,
P10 and P13 all read. Cost of being wrong: a medical document in a cloud prompt — and §8.4 says
revocation *"cannot necessarily retract data already sent to an external provider"*.

### What it blocks
P6 Task 2's row for this field; P7 Task 4's protocol shape. **Not P7's build** — 21 of 22 P7 tasks
build with P6 absent.

### The sentence to write
> P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative. §3.11's
> `sensitivity status` is a projection with no independent writer. `files.sensitivity_state` holds a
> `HANDLING_CLASSES` member verbatim; `mirror_state` is a validator. Every test compares the value.
> [And: does `Unreadable or unclassified` belong to the file or to the gate?]

---

# D3 · Deletion versus append-only

### The question
**What may a user actually delete — and what does "local derived data" mean, given the design uses
"derived" in a sense that excludes OCR text?**

### What is already settled
- **Append-only has already shipped, and beyond the log.** **13 tables carry `BEFORE DELETE …
  RAISE(ABORT)` triggers** — `events`, `evidence`, `text_units`, `extraction_runs`,
  `exclusion_verdicts`, and all eight `bundle_*` tables — with an authorizer hook refusing
  `SQLITE_DROP_TRIGGER`. So §8.4's right is **currently unimplementable without a migration**, and
  P7 Task 15 correctly ships `delete_derived` as a function that refuses.
- **§8.2's `must` does not forbid user deletion.** Its scope is its own clause: *"The product must
  never overwrite the evidence record merely because a later extractor or model produces a different
  answer."* What collides with §8.4 is §8.2's first sentence — *"Every significant event affecting a
  file should be preserved in an append-only provenance log"* — a `should` against a `should`.
- **But §8.1's `must` is unhedged and favours retention:** *"The key principle is that the system must
  be able to reconstruct what it knew, what it proposed, what the user approved, what changed on
  disk, and why every change occurred."* **The design's `must` favours retention, its `should`
  favours the user, and it never noticed.** It runs the same collision again in §8.7.

### The options
| | Name | What it means |
|---|---|---|
| **A** | **Append-only wins** | Nothing deletes. P7 Task 15 keeps refusing. Zero cost. |
| **B** | **Enumerated tombstone** | `events` append-only forever; "derived" is a literal table-and-column list in the SPEC; a tombstone hides a row from every read and blanks its `raw_value` / `text`; `delete_derived` **raises** on any table not in the list. |
| **C** | **Real deletion** | Ships seat: *"strictly worse than (B) — same work, and §8.2's reconstruction is lost. Ignore"*. |

### The seats
- **Design:** the design does not settle this. It gives the deletion right as a `should` and retention
  as a `must`, and never joins them. **Silent on everything the decision needs.**
- **Ships:** ratify B as direction now; add the tombstone column to P4 and P6 Task 4 **before P6
  starts**, while P4's reader surface is still one module (10 SQL sites); leave `delete_derived`
  refusing until P13.
- **Risk:** B, with the enumeration made a hard requirement. SERIOUS — because the built system
  currently *refuses* rather than lies. **It becomes CRITICAL the day a `delete_derived` ships that
  touches some tables and not others.**

### The conflict, and what it turns on
**The design seat has found something that cuts against the other two, and against P7's SPEC.**

`00` uses "derived" in a technical sense exactly once, in §3.2: *"an EXIF field called
`DateTimeOriginal` is raw metadata; capture date = 2026-07-17 is the file fact derived from it."*
**Under the design's own vocabulary, OCR output is raw evidence, not derived data.** P7's SPEC says
*"The product cannot ship unable to forget a scanned passport's OCR text"* — and a deletion right
read faithfully to §3.2 does not reach it. §0's competing sense (*"It can be rebuilt from the
filesystem if necessary"*) points at the entire database.

The two readings are far apart and **the design chooses neither.** This is not a question you can
settle by reading; it is one you have to legislate. That is what makes D3 different from D1 and D6.

**Where the seats converge, and it is the urgent part.** Ships and risk independently name the same
thing: `run_wave2` copies **every text unit of every run** into a sealed, trigger-protected P2 bundle
(`src/orchestrator.py:317-318`), unconditionally, with no handling-class filter. Ships: *"A tombstone in P4 does not reach a sealed bundle."* … *"`delete_derived` is a lie for any corpus that has
ever been bundled"*. Risk: *"it manufactures a second undeletable corpus of everything on every scan"*.
**The cost of deferring D3 grows with every scan anyone runs, not with every part shipped.**

**Round 4 confirms nothing in either plan changes this.** Executed after a live `run_wave2`:
`stage_output` rows **0**, `bundle_file_entry.handling_class` `None, None`, `files.sensitivity_state`
`None, None`, `policy_settings` `'{}'`. P7's OQ8 says *"P7 writes nothing into a bundle"* and no P7
task fills the one slot it touches. So the bundle keeps copying text units with no handling-class
filter after P6 and P7 both ship, unless someone is told to change it. (C-7)

**Ships-seat self-dissent, which is live and which I would take seriously.** Its own recommendation
adds a column nothing writes — *"the exact defect class this project has been bitten by five times"*.
Its honest counter: don't add it; take the migration later, because a migration on a product with no
users is cheap. That counter and the risk seat's position are compatible: ratify B as direction, add
no column, keep the refusal.

### Recommendation
**Ratify B as the direction; build nothing yet; rule separately and now on the bundle copy.** From
ships + risk, converged. Take the ships seat's *own counter* on the column: **do not add a
writer-less tombstone column** — the migration later is cheaper than the defect class.

The enumeration is the part that must be written down: `delete_derived` raises on any table not in
the literal list, so an unenumerated table is a red test rather than a silent miss.

### Reversibility
**A → B is two-way**, with a bill that grows linearly in parts shipped. **The sealed bundles are the
one-way component and they grow per scan run.** Cost of being wrong toward retention: an honest
refusal you can fix later — *"Deletion later is always available. Un-deletion never is."* Cost of
being wrong toward deletion: an audit record that cannot be reconstructed —
`11-ops-runtime.md` §2 is explicit that rebuild-from-filesystem does not recover `events`, learning
records, plan versions or consent grants.

### What it blocks
**P7 Task 15 only — 1 of 22.** Nothing in P6. Its *direction* should land before P6 Task 4's DDL.

### The sentence to write
> `events` is append-only forever. Derived projections may be tombstoned; "derived" is a literal
> enumerated table-and-column list and `delete_derived` raises on anything outside it. No tombstone
> column is built until P13 drives it. Separately: the Wave-2 bundle stops copying text units
> unconditionally.

---

# D4 · Jurisdiction at launch

### The question
**Which jurisdiction's gazetteers ship in v1 — and is `jurisdiction` a value or a field?**

### What is already settled
- **The design says nothing.** `jurisdiction`, `country`, `locale`, `GDPR`, `HIPAA`, `United States`:
  **zero occurrences each.** This is absent, not under-specified. **Entirely yours to invent.**
- **What varies by jurisdiction is values, not fields.** §3.12: *"The system may create new values
  when it sees a new course, project, company, university, or event, but it should not invent new
  fields automatically."* Values auto-create; fields do not. That is what makes this cheap.
- **The design is not silent on internationalization** — §2.7 requires *"appropriate language support
  including CJK where required"*, §3.10 names *"Michaelmas Term 2024"* as a required pattern, and
  `language` is a universal fact.

### The options
| | Name | |
|---|---|---|
| **1** | **One jurisdiction, `jurisdiction` as a value field** | Ship one gazetteer set; a jurisdiction is a data file handed to an injected matcher. |
| **2** | **Multiple at launch** | §3.15: *"without prematurely hand-authoring hundreds of specialized schemas."* Nobody recommends it. |

### The seats
All three say option 1. **Agreement is total on the shape.** Design: the design gives nothing to read,
and its jurisdiction-neutral vocabulary should not be mistaken for a decision — *"It has not decided
anything."* Ships: two-way and unusually cleanly so; **blocks nothing in P6 or P7.** Risk: MODERATE —
an unsupported jurisdiction fails toward **refusal, not exposure**, because P7 Task 3 resolves absence
to `unreadable_unclassified`, which is `Denied(unclassified)`.

### The conflict, and what it turns on
Only **which one**, and the two seats that answered pointed opposite ways without noticing:

- **Risk:** US-shaped, from the design's worked examples — `BUSIB 4300`, `W-2`, `UChicago`.
- **Ships, measured over the 560 entries:** England 8, UK 8, United Kingdom 7, EU 6, Canada 2,
  Ireland 2, **United States 1**, Scotland 1.

**The design skews American; the catalogue its authors wrote skews British.** Whichever you pick, one
of the two bodies of work is pointed the wrong way — and the catalogue is the cheaper one to re-point,
because it names structures rather than statutes.

**The one part with a deadline is not the jurisdiction list.** Ships seat: `jurisdiction` must never
be a destination dimension. §5's folder templates (P10) may want it in a `dimension_order`, and a tree
that branches on jurisdiction for one launch region and not another is a **tree-shape decision, which
is P10's one-way door.** Two-way in P6, potentially one-way in P10.

### Recommendation
**Option 1, jurisdiction matching your own corpus**, from all three seats. Write the never-a-dimension
line tonight; defer the list. Risk seat adds two cheap things worth taking: mark jurisdiction-dependent
catalogue entries with a structured key (124 already say it in prose), and give the residual surface
one string that can say *this domain is not modelled for your region* — otherwise a user outside the
shipped jurisdiction sees a big residual pile and concludes the product does not work.

**Risk-seat caveat on its own MODERATE:** the whole reassurance rests on P7 Task 3's
absence-resolves-to-`unreadable_unclassified` rule, which is not built. If a classifier ever defaults
unrecognised document types to `public_low`, this item inverts to something much worse.

### Reversibility
**Two-way, cleanly**, and it stays two-way as long as no jurisdiction-specific name enters the *field*
catalogue (a `w2_tax_year` field). None of the 560 entries has done that.

### What it blocks
**Nothing in P6 or P7.** It blocks the completeness of tax/legal/government recognition rules, which
are injected with no defaults.

### The sentence to write
> `jurisdiction` is a value, never a field name and never a destination dimension. v1 ships one
> jurisdiction's gazetteers, injected per deployment; the list is decided when P10 is planned.

---

# D5 · The `no_usable_facts` pass structure

### The question
**Do you take the four-pass restructure — and do you accept that its stated guard mechanism does not
work?**

### What is already settled
- **Facts must be attempted before targeted OCR.** §2.7: *"A document with a non-empty but unusable
  text layer should receive OCR only when its extracted evidence fails to produce usable facts, not
  because a broad quality heuristic says the text looks unusual."* Consulting `no_usable_facts` inside
  the extraction loop is a defect, not a preference.
- **The guard as specified is broken. Four independent parties executed it.** Round 3 A1, round 2
  B-1, the ships seat and round 4 each ran it separately: `FactPassNotRun` becomes
  `completeness = failed` on **every text-bearing PDF**, which maps toward `unreadable_unclassified`,
  which is `Denied(unclassified)` — so the gate refuses the entire document corpus **while the scan
  reports success and Task 26's own acceptance test passes.**
- **Round 4 closed the remaining escape route, and this changes the fix.** The substrate has already
  moved: `_extract_one` now re-raises `ContractViolation` (`src/orchestrator.py:151`), and
  `src/extractors/failure.py:25-48` names this exact defect in its docstring. **`ContractViolation`
  appears zero times in either plan.** Round 4 executed *both* base classes on the repo's own
  fixture:

  ```
  FactPassNotRun(Exception)          run_wave2 RETURNED NORMALLY, bundle sealed
                                     pdf.text · native · failed
  FactPassNotRun(ContractViolation)  propagated out of run_wave2 on the first text-bearing PDF
                                     no pdf.text run written at all
  ```

  **Neither is acceptable**, and the reason is structural: `ocr_policy.text_layer_state` consults the
  verdict **unconditionally for every text-bearing PDF**. Round 2 costed this as *"one bad file ends
  the run"*; round 4's addition is that **it is not one bad file, it is every ordinary PDF, because
  the consult is not conditional on anything being wrong.**
- **The blast radius is genuinely narrow.** `no_usable_facts` is consulted in exactly one place, in
  one branch of one extractor family. The plan's claim that the split is narrower than it looks is
  correct and was verified.

### The options
| | Name | |
|---|---|---|
| **1** | **Four passes as written** | **Not available.** Refuted by execution, four times. |
| **2** | **Four passes; `dispatch` splits** | `dispatch` gains a native-only entry point and a targeted-OCR entry point, so loop 1 **cannot reach the verdict by construction**; `FactPassNotRun` inherits `ContractViolation` as a guard that then never fires; the tier map is merged, not replaced. Round 4: *"Recommendation: do both."* |
| **3** | **Per-file state machine** | Design seat: extraction → facts → OCR → facts for one file at a time satisfies every sentence in the design equally. The design describes per-file preconditions and **never a batching architecture.** |

**Round 4's four-pass verdict, verbatim:** *"The shape is right; every mechanism that implements it is
wrong."* Passes 1 and 3 do not connect at all; pass 2 is sound; pass 4 reads fine and **writes
ambiguously.**

### The seats
- **Design:** the design fully supports the four-pass plan's *correctness* and does not require its
  *shape*. "Four passes" is a caller design, not a design reading. §8.6's scan-level ceilings mildly
  favour batching — inference, not text.
- **Ships:** option 2, and it **revised its own estimate upward after reading round 2**: 3 tasks not 1,
  ~50 tests not ~15. It names a fourth defect nobody else did — **`set_extraction_status` replaces the
  whole map**, so loop 3 silently erases the `filesystem` and `native` tiers on exactly the files that
  needed OCR.
- **Risk:** CRITICAL **for the fix, not for the structural choice** — *"The four-pass shape is right
  and is barely Joseph's decision; what needs deciding is that Task 26 does not land as written."*

### The conflict, and what it turns on
**There is almost none, and that is the finding.** Three seats and three review rounds converge on
option 2 without having seen each other. The only divergence is the design seat's option 3, raised as
*the design does not require the shape*, not as *you should do this instead*.

**Round 4 corrects one seat on a matter of fact, and it matters.** The **risk seat's fix item 1** —
*"`_extract_one` re-raises `FactPassNotRun` beside the two admit refusals"* — describes a substrate
that has already changed, and round 4 **executed that exact configuration**: it ends the scan on the
first ordinary PDF. Its item 2 (loop 1 hands `extract()` no verdict at all) is the half that works,
and it is the ships seat's position and round 2's NEEDS JOSEPH 1. **The risk seat's recommendation is
half-right and the wrong half is the one it listed first.**

**What is actually yours here is not the structure.** Three things:
1. **A P5 contract revision.** `dispatch` must publish a native-only entry and a targeted-OCR entry.
   P6 Task 26 says *"`dispatch.py` … does not change."* One of those two sentences has to go, and
   round 2, round 4 and the ships seat all say it is the second. The alternative — the orchestrator
   calling `dispatch._ocr` directly — is a private call across a part boundary.
2. **A scheduling call.** P6 Task 26 and P7 Task 22 both edit `run_wave2` and **neither plan knows the
   other does** (round 3 A17, round 2 B-15). And the one line that closes the P7 seam —
   `handling_class=None` at `src/orchestrator.py:311` — sits inside the loop Task 26 declares
   *unchanged*, owned by nobody in forty-nine tasks.
3. **An operating rule.** The code is two-way; the data it produces is not. A wrong shape writes
   `extraction_runs` rows and `files.extraction_status_by_tier` values that §8.2 makes unrewritable.

**And one genuinely new question round 4 surfaced, which decides whether pass 4 works at all.**
§3.4's cache key takes **one** `analysis_tier` and **one** `extractor_version`; a fact's
`evidence_refs[]` are plural and already span two extractors at two tiers before OCR enters — round 4
executed this on the skeleton PDF. So the plan's claim that *"the two cache keys differ by
`analysis_tier` alone"* is **not derivable from the code**, and until a rule is stated, pass 4 may
collide with pass 2 rather than supersede it. Round 4's proposed rule: the key's tier is the highest
among the cited runs and the version is a canonical digest of the `{extractor: version}` map. This is
engineering's to write, but somebody has to write it before Task 26's supersession test is
expressible.

**Ships-seat honest discount, and it is the strongest counter to its own verdict:** loops 3 and 4 are
no-ops while `readers.ocr_engine is None`, so "provably free" means "provably untested" — *"exactly
the argument that made §2.7's OCR path dead for a week"*. The honest scope is Task 26 **plus a fake
OCR engine wired into the Wave-2 fixture**, which nobody has costed.

### Recommendation
**Option 2**, from the **ships seat**, corroborated by rounds 2, 3 and 4 — and by round 4 it is now
the *only* remaining shape, not the preferred one. Say yes to the `dispatch` split; schedule Task 26's
three parts and P7 Task 22 as **one diff with one owner** against a green suite; give
`src/orchestrator.py:311` an owner in that diff. **Do not run a real corpus through a half-wired pass
structure.** No seat dissents on the structure; the risk seat's first fix item is superseded by round
4's execution.

### Reversibility
**Code two-way** — the suite is 1,237 tests in 9.93 seconds, so trying and reverting costs ten
seconds. **Data one-way** under §8.2.

### What it blocks
**Nothing can start on it.** Task 26 is last in P6 by design. It blocks *shipping* P6, not building it.

### The sentence to write
> Take the four passes. `extractors.dispatch` may grow a native-only entry and a targeted-OCR entry —
> that is a P5 contract revision and it is approved. P6 Task 26 and P7 Task 22 land as one diff with
> one owner, and no real corpus runs until it is green.

---

# D6 · Field naming

### The question
**Are field keys spaced (`work type`) or snake_case (`work_type`) — and is the Academic field called
`subject` or `course`?**

### What is already settled
- **Prose beats table, and it was ratified on 2026-08-19.** `01`'s own header: *"not a substitute for
  it"*, *"Joseph's wording is authoritative"*. **There is no prose-vs-table question to decide.** The
  rule was written, printed at the top of the page, and then not applied — four times, by four
  authors, in the same direction each time.
- **`subject` and `course` are one field under two words, not two fields.** §3.14 (*"A fact such as
  subject = BUSIB 4300"*) and §5.4 (`school → term → course → work type`) name the same value under
  each. Two fields would store `BUSIB 4300` twice from one piece of evidence. **The count is settled;
  the word is not.**
- **`capture date`, `creation date` and `capture year` are three different quantities**, not three
  names for one. A photo has all three: `creation date` is universal, `capture date` is derived from
  EXIF (§3.2), `capture year` is the Photos folder dimension (§5.4: `year → event`). C15's framing of
  this as a naming conflict is a misclassification.
- **This is the clearest one-way door of the six and the cheapest to close.** Two-way today; one-way
  the moment P6 Task 2 runs, because `field_key` becomes a stored join key under §8.2's no-delete rule
  — and a superseded fact whose field no longer exists is unreadable.

### The options
**Style:** spaced lowercase · snake_case. **Identity:** `subject` · `course` (one rule settles four of
P6's five naming questions).

### The seats
- **Design:** the design never addresses spelling and it is not a design question — *"`00` is prose."*
  If you want the one signal anyway, **§3.8's snake_case is it**, because §3.8 is the only place the
  design names *fields as fields*. Labelled INFERENCE. On identity: leans `subject`, explicitly as a
  tiebreak, not a reading.
- **Ships:** *"Field keys are spaced lowercase. §3.11's table is the design's own spelling and the
  design wins."* On identity: **3–3, a genuine tie; cost is identical either way; pick either, in the
  next sentence you write.**
- **Risk:** *"Style: spaced wins. §3.11's table is the design's own convention"*. SERIOUS. On identity:
  no preference — *"either is safe once it is one."*

### The conflict, and what it turns on
**This is the sharpest genuine conflict in the brief, and it is a matter of fact, not of taste.**

Two of three seats recommend spaced, and **both give the same justification: that §3.11's table is the
design's own convention.** That justification is false. `00` contains **zero pipe characters** in 286
lines — I checked. §3.11 is six prose sentences. The table is `01`'s rendering, which `01`'s own header
subordinates to the prose. Neither seat's *preference* is refuted; their *stated grounds* are gone.

And the signal that survives points the other way. **`00` contains exactly five snake_case tokens:**

```
authored_by · our_firm · target_school · file_facts · node_modules
```

Three are §3.8's field identifiers. One is §3.12's table name (*"The file_facts table connects one
file to one field and one value"*). One is a directory. **Every identifier in the design is
snake_case. Every spaced name appears inside a sentence describing content** — `00` also writes
"content hash", "file fact" and "handling class" the same way, and nobody proposes `content hash` as a
column name.

What it turns on: whether "the design's own spelling" means the words it uses in prose, or the tokens
it writes when it is naming a thing as a thing. **`00` does not settle it** — the design seat is right
that this is silent. But if you are deciding on *what does the design say*, the only evidence available
says snake_case, and the two seats that said otherwise were reading a rendering.

**Cost is symmetric and does not break the tie.** The catalogue holds 914 spaced and 959 snake_case
names; either direction touches roughly half of 560 entries and **merges 124 collision pairs**
(`record_type` meets `record type` in 30 entries, `issue_date` meets `issue date` in 5, and 122 more)
— each of which someone must confirm is one concept. One to two hours, either way, **today**.

**One consequence worth knowing.** Under snake_case field keys, the ships seat's D2 compromise
disappears: it currently keeps `sensitivity status` (field key) and `sensitivity_state` (column) alive
on a namespace technicality, and its own weakness section says *"If Joseph wants one spelling
everywhere, do it now. It will never be cheaper than tonight."*

**On `subject` vs `course` the seats are genuinely tied and I will not pretend otherwise.** The design
seat's tiebreak is that §3.12 is the only sentence enumerating the `fields` table's contents by name,
and it says `subject`. The counter is equally available: §3.5 states a *rule* (*"becomes a course fact
only when the engine finds a course-code pattern together with academic context"*), §3.11 states the
domain's activated set, §5.4 states the template dimension — three operational sentences against three
illustrative ones. **And whichever you pick, one design sentence gets reworded**: pick `subject` and
§5.4's template reads `school → term → subject → work type`; pick `course` and §3.12's `fields` list
does. The trade is even.

### Recommendation
**Style: snake_case**, from the **design seat**, strengthened by the `file_facts` evidence above.
**Ships and risk both dissent and both prefer spaced** — but their stated grounds do not survive, and
their cost argument is neutral. If you prefer spaced on taste, say so; it is a legitimate answer and it
costs the same. What is not legitimate is leaving it unsaid.

**Identity: `subject`**, from the design seat, and **relayed as a tiebreak with no weight behind it.**
The ships seat's advice is the operative one: pick either, in the next sentence you write. The cost of
picking is zero; the cost of not picking compounds across 560 entries and hardens at P6 Task 2.

### Reversibility
**One-way at P6 Task 2**, for the same reason as D1 and D2: `field_key` is a stored join key read by
P7, P8, P9, P10 and P13. Cost of being wrong: this project has shipped one-concept-two-names **four
times** — `fingerprint`/`config_fingerprint`, three spellings of one OCR engine, a published order that
was uuid4 order, and `handling_class` fed `sensitivity_state`. **None of the four failed a test at the
time.** Round 3 A13 shows the shape it takes here: `suppressed()` returns **False** when the query
matches nothing, so a rejection recorded under `document type` never matches a proposal under
`document_type`, and the wrong claim returns forever.

**One correction to the risk seat, in your favour.** It cites round 3's A2 as *"still live in a
different form"*. Round 4 closed A2: `src/orchestrator.py:230` now sets
`signal_target = routed[0] if routed else None` and `Dispatched.__post_init__` raises if signals ride
with more than one result, so the mis-keying is **unconstructible rather than merely fixed.** Four
prior instances, not five.

### What it blocks
**P6 Task 2 — the second task of the next part anyone builds.** Also blocks D1's fully-open option
entirely, since you cannot load a catalogue that spells one concept two ways.

### The sentence to write
> Field keys are snake_case; SQL column names are snake_case; they are one namespace, not two. The
> Academic field is `subject`. Apply by script across all 13 catalogues before P6 Task 1, confirm the
> 124 merges, and add the assertion to `planning/domains/check.py`.

---

## Also waiting on you, outside the council's six

Not council business, listed so this is the only document you have to open.

| # | What | Why it is yours |
|---|---|---|
| **C2** | Install default — `offline` or `local_model`? | If it is `offline`, D1's privacy failure never fires in v1 and the risk seat's D1 case *collapses to* "a bigger surface is bigger." |
| **C3** | What is a "corpus area"? | Consent grants cannot be scoped until it is named. Affects P3, P9, P10. |
| **C5** | Is `protected` exactly the top two handling classes? | §8.4 gives five classes and, separately, five kinds of document that *"enter a protected state immediately"*, and joins them nowhere. Blocks P9, P10, P11. |
| **C7** | Retention periods | The design states none, for anything. |
| **B5c** | Was W1 ratified? | P7 now tests as contract a derivation the fidelity audit headed *"Nearest faithful fix (not applied)"*. |
| **§4b** | `LABEL_UNTOUCHED_PROTECTED` has no writer and no reader | The carrier of your protected-container promise never reaches the database; its only use anywhere asserts a constant equals its own literal. Three lines to fix in P3, and the risk seat is right that leaving it *"reads as done and is not."* |
| **R4-3** | Who owns the `contradicts` oracle and `normalize`? | P8's SPEC lists both under *From P6*; P6 Task 17 says *"P6 supplies the four inputs and owns none of the checking."* Two of P6's thirteen `unresolved` reasons are written from a check nobody wrote. |
| **R4-4** | Who authors a `StageAdapter`? | Named in **no SPEC**, and it is the only connector between a stage and P2's replay machinery. A live scan writes **zero** `stage_output` rows today, and after P6 and P7 it still will. §8.5's per-stage measurement is currently true of the harness and not of the product. |

Two housekeeping items that need no decision at all: **restore the dropped hedges to `01`'s tables**
(a mechanical edit that closes the largest open question in the wave without you deciding anything),
and **strike P6 Task 2's "acquiring one fails the test"**, which hardened S3's deferral into a
prohibition S3 never wrote.

---

## The answering order

**D6 → D2 → D1 → D3 → D5 → D4.** This is the ships seat's order and neither other seat contests it.

```
D6 (naming)      ──blocks──> P6 Task 2  ·  D1's open option  ·  D2's expressibility
D2 (sensitivity) ──blocks──> P6 Task 2's row · P7 Task 4's shape · D3's definition of "derived"
D1 (catalogue)   ──blocks──> P6 Task 2, P6 Task 13
D3 (deletion)    ──blocks──> P7 Task 15 only (1 of 22); P6 Task 4's DDL is the cheap moment
D5 (passes)      ──blocks──> nothing to start; it is P6's LAST task
D4 (jurisdiction)──blocks──> nothing
```

**Why D6 leads even though D2 is the more serious.** D2's answer *is* a field key plus a record
choice — you cannot write it down without D6's rule. And D6 is one sentence with no design content on
the style half. **Why D2 is second:** the risk seat calls it the one risk it would not ship without
resolving, and D3 cannot define "derived" without knowing which record holds the sensitivity that
decides what is derived-and-protected.

**D2 now carries two questions, not one.** Round 4: naming which record is authoritative is inert
until you also name **which part produces a classification**, because today no part does. Both fit in
one sentence and both are yours — round 4 says of the first half that *"it cannot be settled below
Joseph."*

**Why D1 falls to third, having been framed as the biggest:** most of it is already settled. §3.15
gives the launch scope in one unhedged sentence, `01`'s header gives the precedence rule, and the
residual question is four career fields.

---

## What you can safely defer, and for how long

| | Defer until | Cost of deferring |
|---|---|---|
| **D4** | P10 is planned — four parts away | **Zero**, provided `jurisdiction` is never a destination dimension, written tonight |
| **D3's implementation** | P13 exists to drive a delete | Zero — but its **direction** should land before P6 Task 4, and **the bundle question gets worse with every scan anyone runs**, which is unusual and is why this one cannot sit indefinitely |
| **D5** | The end of P6 | Zero to build. **Non-zero to run** — a half-wired pass structure writes `extraction_runs` rows that §8.2 makes unrewritable |
| **D1, D2, D6** | **Cannot be deferred past P6 Task 2** | All three become one-way doors the moment `field_key` becomes a stored join key |

The one fact that governs all of this: **the suite is 1,237 tests in 9.93 seconds.** Every decision
here can be tried and reverted inside a coffee break *as code*. What cannot be reverted is data
written under §8.2's append-only rule, and vocabulary frozen into a join key. Every one-way door in
this list is one for one of those two reasons and no other.

---

## If you have ten minutes

**Answer D6.** Both halves, in one sentence: the spelling convention, and `subject` or `course`.

It is the cheapest of the six to answer, it has the nearest hard deadline (P6 Task 2, the second task
of the next thing anyone builds), it is the clearest one-way door, it gates D1's expensive option, and
**D2's answer cannot be written down until it is settled.** The coin flip is the answer; not flipping
is the only wrong move.

Then spend sixty more seconds on **D2**, whose first half is already drafted and costs zero new tasks
— P7 Task 4 is written for it. **Its second half is new as of round 4 and needs a name, not a
design:** which part runs the sensitivity detector. Until one is named, whichever record you make
authoritative stays empty, and §8.4's door denies every file.

**Dissent, recorded:** the risk seat would spend the ten minutes on D2 rather than D6, calling it the
only one of the six whose failure is invisible at rest, on a concept this project has already shipped
wrong once. That ranking is right about severity. It is D6 that is right about sequence, because a
record choice you cannot spell is not yet an answer.
