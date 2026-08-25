# `business_operations.product-roadmap` — lab notes (template row, deepened to J-DEPTH)

**Depth: J-DEPTH** (ratified 2026-08-24; the retired `Depth: GIST` header this row carried is replaced).

Row kind: **template**. Schema: `business_operations`. Launch: **placeholder** (`fields: []`).
Verdict: **kept, not refused — but on a materially different argument from the gist's**, with three
things reversed and one boundary narrowed in a neighbour's favour.

**Status of this file.** The row was written under the retired J-IND *gist* standard: a 25.6KB JSON
and a 5.1KB memo. Per the deepening addendum the JSON was treated as **verified-but-shallow, not
untrusted** — its quotations were machine-checked and its key set was house-correct — so it was
**extended and corrected, not rewritten**. What was preserved, what was added and what was reversed
is itemised in *What changed in this pass* at the end, and every claim there was re-read against the
JSON actually on disk before this memo was finished.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted with quotation marks,
  except one verbatim span from `code.software-project.json` which is labelled as such inline. All
  25 quotation spans in the JSON were re-checked with `grep -F` after writing; the audit is at the
  end. The spans that did real work on this row:
  - the **dimension-order rule** and, immediately after it, **the exception it grants**:
    *"For document and record domains, project, function, or subject usually comes before time
    because putting year first scatters related work across calendar folders."* and *"Photos and
    capture-based media are the major exception: time often belongs first because capture date is a
    defining aspect of the material."* Both sentences are in the JSON now. The second is new this
    pass and it is the one that matters here, because this is the row in the family most likely to
    be accused of claiming the photos exception. A roadmap's quarters are **content periods**, not
    capture dates.
  - the **universal-facts list** — *"file type, creation date, language, duplicate family, version
    family, and sensitivity status"* — which is why supersession was demoted from a node-test ground
    to a handling hazard (charge (c), below).
  - the **near-duplicate caution** — *"A content-hash match supports deduplication review; a
    filename match alone does not."* — used twice, and in the second use pushed further than the
    sentence itself goes, which is marked as inference where it appears.
  - the **purpose-coherence sentence** — *"The documents are content-incoherent but
    purpose-coherent."* — which is this row's whole answer to charge (a).
  - the **stop rule** *"when one high-frequency entity acts as the only bridge"*, added to
    `never_alone` against a bare product name.
  - the **multi-role token sentence** about Columbia, read across to a company name and **marked as
    inference** where used, per the schema anchor's instruction.
- `planning/domains/CONNECTION.md` §2 (the node test) and §4 step 2 (activation), `_CONTRACT.md`
  rules 7, 10, 15, `canonical_fields.json`, `roster.json`, `ALIGNMENT.md`,
  `DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A line 830.

### Neighbour and family files read before writing (and not touched)

- **`business_operations.research.md`** (46KB, the deepened schema anchor) — the default template
  and the never-alone principle. Applied explicitly in *Leg 2* and audited signal by signal.
- **`business_operations.product-requirements.research.md`** (41KB) — the other half of the pair
  question. Read in full before anything was written, per the dispatch.
- **`business_operations.strategy-plan.research.md`** (30KB) — read for its refusal of altitude and
  its decision-axis claim. Reciprocated below.
- **`business_operations.go-to-market.research.md`** (47KB) — read for its fold analysis, which
  names this row. It won an argument against this row and the JSON now concedes it.
- **`business_operations.organisational-records.json`** — the family's refusal, read first on the
  dispatch's assumption that this row might be heading the same way. It is not, and *why not* is
  argued rather than asserted, in *Leg 2*.
- **`business_operations.policy-handbook.research.md`** — for the reissue precedent.
- **`business_operations.meeting-record.json`** — for its cession, now reciprocated.
- **`code.software-project.json`** — read because the gist pass pointed an edge at it. It is
  `refuse_node: true`; the edge is corrected.

### Sources deliberately not used

No `planning/deferred-catalogues/` entry was consulted: nothing in this row's recognition consumes a
gazetteer or a citation catalogue. No detector regex and no threshold appears anywhere in the JSON.

---

## The charge against this row, answered in three parts

The dispatch put three specific charges. Each is answered on its own, and one of them lands
partially.

### (a) "A roadmap is plausibly a document type — a deck — rather than a filing world."

**Answered: it is a world, and the test is the pile it produces.** A document *type* produces copies
of itself. A filing world produces a pile of unlike artefacts held together by one purpose, which is
exactly what `00` describes: *"The documents are content-incoherent but purpose-coherent."* One
planning cycle produces a deck, a scoring spreadsheet, a scope list with a cut line, a set of
replanning notes and a board capture. Those five share no content whatever — a scored table and a
themes grid have no vocabulary in common — and share one purpose completely. This is the same shape
`strategy-plan` used for its planning round and it is the schema anchor's licensed grouping reason
for the family, so the row is not inventing a private test.

The part of the charge that is true is conceded in the JSON rather than argued away: **`.pptx` is in
`never_alone` and the row must never be argued as "the deck row"**, with `00`'s extension-routing
sentence attached. Nothing in this row activates from a file type, and the strongest positive signal
below is available in a spreadsheet, a markdown file and a PNG as readily as in a deck.

### (b) "Its axis is time, and a period axis is a dimension the design already handles universally."

**This is the sharpest charge and it is answered by narrowing the claim, not defending it.** The
gist's own framing — *"time as a structural axis"*, the anchor being *"the HORIZON and the
audience"* — walked straight into it. A period axis really is a dimension: `00` treats period as a
level in every document world, and budgets, forecasts, board cycles, programmes and marketing
calendars all draw one. **If a period axis were this row's evidence, the charge would be fatal.**

It is not this row's evidence, and the JSON now says so twice. `never_alone` carries **a stated
horizon or a period axis alone**, worded to match the identical entry on `strategy-plan`. What
activates the row is one level down:

> **items committed to positions in an ORDER, at a stated level of commitment.**

Time is how that is usually *drawn*. It is not what it is. Two things follow, and both are checkable:

1. **A roadmap with no dates at all is still fully a roadmap.** A now / next / later board, or a
   committed / planned / exploring board, carries no period anywhere. It has an ordinal axis instead.
   The row takes both renderings and the JSON states them as one signal with two forms.
2. **A document with a period axis and no ordering is not this row's.** A budget's line items are
   not in an order; they are in a period each. That is why a `budget-forecast` edge was **added this
   pass** — the charge is answered most sharply against the sibling that most obviously also has a
   period axis. The discriminator there is variance against actuals (a backward comparison of money)
   versus commitments (a forward order), and neither row is discriminated by the axis itself.

So the answer to "if time is all you have, you may be a view rather than a world" is: **time is not
all this row has, and the row now says so in data.**

### (c) "It may be a version family: roadmaps are reissued every quarter."

**This one lands, against the gist, and the gist verdict is reversed here.** The gist named expiry as
the first of *"two things about this row that no sibling has"* and rested part of the node test on
it. `policy-handbook` had already established the rule for this family and the gist did not apply
it: version family is a **universal** fact — `00` lists *"file type, creation date, language,
duplicate family, version family, and sensitivity status"* as the shared set every file may carry —
so **reissue can never earn a row**, and a row that argues from it is arguing from something the
design already provides for free.

The distinction the gist wanted is real but it is not a *detection* distinction. Reissue is a new
version of the same document. Expiry is the *content ceasing to be true* — and there is no byte in a
superseded roadmap that says so. It is read off the version family plus content, which is the
universal machinery again. **Expiry is therefore not evidence and cannot be a node-test ground.**

What survives, and where it now lives:

- `never_alone` gained an entry naming **a version token and, more strongly, the fact of reissue**,
  carrying both the universal-facts quotation and the content-hash caution.
- `Roadmap 2024 - OLD.pptx` keeps its fixture but its `must_not_conclude` now states plainly that
  *supersession is not this row's evidence and the gist pass was wrong to lean on it*.
- The handling hazard stays where a hazard belongs — in `needs_llm`, labelled as a hazard — so that
  a model never reports an expired plan as current.
- `NJ-BO-12` was rewritten to the narrow question that actually remains, which is a product question
  about the universal, not a question about this row. See NEEDS-JOSEPH.

The row loses nothing it needed. It never needed reissue; it had four structures without it.

---

## The node test, argued leg by leg

### The schema's default template, quoted so the comparison is checkable

From `business_operations.research.md`, the paragraph every sibling must differ from:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* → the
> **governance body, project, contract, or account** the material belongs to → the **fiscal period**
> → the **document function**. Not time-first.

And the family's never-alone rule, which is the harder gate:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** ... Every detection signal a sibling writes must pair a **structure** with a
> **labelled slot**.

### Leg 1 — detection signals. **PASSES**, and this is the row's only strong leg.

Each signal audited against the pair rule, honestly, including the one that fails it:

| Signal | Structure | Labelled slot | Pair holds? |
|---|---|---|---|
| Ordering axis with items in cells | items placed into cells of an axis | axis headers: quarter/release labels, or now/next/later band labels | **yes** |
| Prioritisation model | a rank ordering over rows | named criteria columns — reach, impact, confidence, effort | **yes** |
| Release scope with a cut line | an in/out partition made visible | a version token, an in-scope list | **yes** |
| Changelog | entries grouped and repeated per version | version + date headings, added/changed/fixed/deprecated group labels | **yes**, but see below |
| Replanning record | a change of position | a previous-position slot and a revised-position slot | **yes** |
| Forward-looking disclaimer / audience marking | **none** | a sentence, a marking | **NO** |

The last row is the audit's finding and it produced a change: the disclaimer was an *activating*
deterministic signal in the gist and is now marked **CORROBORATING ONLY**, because it is a labelled
slot with no structure behind it and the family's rule forbids exactly that. It remains the most
useful corroborator the row has — it is close to unique in the corpus and it is the byte that decides
the privacy question — but it can no longer fire the row on its own.

The changelog is recorded in the JSON as the row's **weakest** deterministic signal, for a reason
worth stating because it cuts against the row's own story: a changelog is a *backward record*, it
*accumulates* rather than being superseded, and it is the one member of this row that does not point
forward at all. It is kept because the deletion test passes on it — strip the version headings and
the entries are an undifferentiated list — and not because the row needs it. Where it lives in a
repository the `code` schema co-holds it.

**The deletion test, repaired.** The requirements and strategy rows converged on *delete the dates
and see what survives*. That test is correct on every file they applied it to and **blind to the
dateless board**, which has no dates to delete and is fully this row's. The repair is one word:

> **Delete the ORDERING.** An unordered bag of themes is not a roadmap. An unordered set of
> requirements still reads. An unordered business case still reads. An unordered launch gate still
> reads.

This returns the identical verdict on `H1 roadmap.pptx`, on `PRD - saved views.md`, on
`Phoenix project plan.xlsx` and on a readiness gate, and additionally covers the case the original
could not see. It is offered as a **refinement, not a reversal**, and it is stated as such in the
`collides_with` entry for `product-requirements`.

### Leg 2 — recommended dimensions. **CANNOT PASS in data, and does not need to.**

`template.dimension_order` is `[]` by binding contract: a dimension may only branch on a field the
same schema declares, and `business_operations` declares none under PR-6. So this leg is unavailable
to *every* sibling in the family and it decides nothing either way — the same position
`product-requirements` and `go-to-market` recorded.

Held as prose, and the divergence from the default paragraph is real and nameable: **organisation →
PRODUCT → planning horizon or release → document function**. Two differences from the family default,
both stated in `template.why`:

- **A product/offering level where the default has a governance body, project, contract or account.**
  A product is none of those four. It is not a project (it has no intended end), not a contract, not
  an account, and not a governance body.
- **A horizon or release level where the default has a fiscal period.** A release is not a management
  period; a horizon is not a fiscal year. This is also the exact level where the paired requirements
  row **refuses** a level, which is the sharpest available demonstration that the two rows are not
  one situation.

`time_first` stays **false**, and the reason is now argued rather than asserted, because this is the
row most likely to be accused of claiming the photos exception. The exception is granted to
capture-based media *because capture date is a defining aspect of the material*; a roadmap's quarter
is a content period an author chose, not a capture date a sensor recorded. The schema anchor's
instruction — *a sibling claiming `time_first: true` is claiming the photos exception without the
photos evidence, and R1c should reject it on sight* — would have applied to this row above all
others, and it does not fire.

### Leg 3 — privacy rules. **PASSES**, narrowly, on one ground genuinely this row's.

The family's default posture is `potentially_sensitive` with a side-and-custody caution. This row has
something the schema does not: **the safe version and the unsafe version are near-identical files.**
An internal roadmap and its customer-facing cut share themes, layout and often a filename stem; only
a disclaimer or an audience marking separates them.

What makes that a *rule* rather than a mood is that it is a hazard about the **universal duplicate
and version machinery**, not about content. The machinery is the thing most likely to cause the harm
— by merging the pair, or by surfacing the wrong member as the survivor. `00`'s caution is the
operative one, *"A content-hash match supports deduplication review; a filename match alone does
not."*, and this row pushes it one step further: here even a **near**-match must not merge them.
That extension is marked as inference in the JSON. No other sibling in this family has a pair of
files whose members differ only in intended audience and whose confusion has a disclosure
consequence.

The row assigns only the catalogue value `potentially_sensitive`. It does not assign, alias, rank or
infer a P7 handling class.

### Why this row is not `organisational-records`

The dispatch asked this to be tested rather than assumed, and the refusal's own closure is the right
instrument. That row fails because it is defined by **subtraction** — carries an organisation and a
document type but no more specific operational sub-domain — and *"a negative definition cannot own a
positive structure"*. Its deletion test: delete every entity name and every document-type word and
nothing is left.

Run the same operation here. Delete every entity name, every product name, every document-type word
(*roadmap*, *plan*, *release*, *changelog*) and every period token from `H1 roadmap.pptx`. What
remains is **a grid of unlabelled bands with items placed in them in an order** — and that is still
recognisably this row, because the structure survived the deletion. The row is defined positively, by
a structure, not by what is missing from it. That is the whole difference between the two rows, and
it is why the refusal's escape-route closure does not reach this one.

---

## The pair question, confirmed from this side with independent reasoning

The dispatch is right that a boundary argued from one side is half a boundary, and right that the
gist's identical `open_question` on two rows was *"a well-documented deferral, not an answer."*
`product-requirements` settled it. **This row confirms the settlement — two worlds — and it confirms
it by re-deriving it, not by accepting it.** One refinement is offered; nothing is reversed.

That row's three separations were: what time is doing in the document; whether the document expires;
whether the atoms are obligations or positions. Here is the same verdict reached from three tests
this row chose independently, so the confirmation is worth something:

| Test | `product-roadmap` | `product-requirements` | Same verdict? |
|---|---|---|---|
| **Delete the ordering** | destroyed — an unordered bag of themes is not a roadmap | survives — requirements are a set, not a sequence | yes |
| **What can be *passed*?** | nothing; a position in an order has no test attached | every atom, via its acceptance criterion | yes |
| **Where the prose dimension orders diverge** | wants a horizon/release level | **refuses** a horizon level outright | yes |

Three independently chosen tests, one verdict. **Two rows.**

**The one thing this row contests, and it is a formulation, not an outcome.** That memo's leading
discriminator is *time as a structural axis*, tested by deleting the dates. That formulation cannot
see a dateless now / next / later board, which is a roadmap by every other measure and has no dates
to delete. Deleting the **ordering** returns the same verdict on every file that memo tested and also
covers the board. This is recorded in the `collides_with` entry for that row as a refinement offered,
explicitly not a reversal, and it changes no verdict either row reached. **It is not a silent
change**: it is named in the JSON, in this memo, and in the returned summary, and it is a
recommendation to R1c to reconcile the wording on both rows rather than a one-sided edit — this row
may not edit its neighbour, and a one-sided change would leave the pair contradicting each other.

**Where the merge case remains real, restated so it is not smoothed over.** In a two-person team
these documents share a folder, an author and sometimes a file; and the leg that would separate them
most visibly is unavailable to both under PR-6. It loses because the node test is about what evidence
**activates**, not about how a small team **stores** things — that memo's phrasing, adopted here
because it is right and re-phrasing it would be the churn the addendum forbids. `NJ-BO-10` is
downgraded on this row to the same narrow re-examination trigger.

---

## The strategy boundary, stated reciprocally

`strategy-plan` refused **altitude** as a discriminator — *"a roadmap is product-level, a strategy is
company-level"* — as *"exactly the move the schema anchor forbids"*, because a function or a unit is
a value of a dimension, not a structure. It claims a **decision axis versus a period axis**, testable
by deleting the dates, and it disclaims this row's horizon axis in its own JSON's `never_alone`.

**This row states the same boundary from its side, and accepts three of the four elements outright.**

1. **The altitude refusal is accepted and reciprocated in the sharper direction.** That row conceded
   that *"A company-wide roadmap is still a roadmap and this row does not claim it."* The reciprocal
   concession is the one that costs this row something and it is made explicitly in the JSON: **an
   option paper about a single product is the strategy row's, and this row does not claim it because
   the product is small.** A boundary where only one side gives ground is not reciprocal. Both
   concessions are now in this row's `collides_with` entry and in its `needs_llm`.
2. **The horizon disclaimer is accepted and matched.** That row's `never_alone` entry disclaiming a
   stated horizon and a period axis is now present on this row too, in matching terms. Both rows
   disclaim the same evidence, which is the correct outcome: **neither of us owns the period axis.**
3. **The axis contrast is accepted.** Their atoms are choices under an approval; this row's are
   positions in an order. An approval slot and a costed alternatives table are theirs and this row
   does not want them.
4. **The one place this row diverges, stated as divergence.** Their test is *delete the dates*. This
   row's is *delete the ordering*, for the dateless-board reason above. Applied to their own
   fixtures the two tests agree everywhere: delete the ordering from `Phoenix project plan.xlsx` and
   the objectives sheet still reads (so it is not this row's); delete the ordering from
   `Our 5 year plan.docx` and the goals still read (so it is not this row's either).

**The same bytes, named on both sides.** `H1 roadmap.pptx` is now named by three rows —
`product-requirements` as its collision fixture, `strategy-plan` as *"a file that must not be lost to
this row"*, and here as the row's **primary positive fixture, under that exact filename**. The gist
had called it `Product roadmap H1 2026 - internal.pptx`, which was the same situation under different
bytes; it was renamed this pass so all three accounts point at one file. Both neighbours describe it
as swimlanes across a quarter timeline with items in period cells and no acceptance criteria; this
row claims it on the same evidence, plus the now/next/later slide and the internal marking.

---

## The go-to-market boundary — this row lost an argument and the JSON concedes it

`go-to-market` analysed a proposed fold **into this row** and rejected it, correctly, in this row's
own terms: a readiness gate has no ordering axis, does not expire, and there is no current version of
a go / no-go that happened. That analysis is accepted without qualification.

Accepting it has a consequence the gist row had not drawn, and this pass draws it. That row's landed
edge takes the launch gate, positioning, enablement and **announcement material for one dated
release**. The gist row's `name` said *"and release communications"*, listed *"release announcement
or customer-facing update"* as a work type, and carried `Whats new in 4.2 - customer email.eml` as a
**positive** fixture. That is a straightforward overlap with a landed neighbour, in the neighbour's
favour, and the JSON now concedes it:

- `name` → *"Product roadmaps, release planning and release records"*.
- The announcement work type is **removed**.
- The `.eml` is now a **negative** fixture: `group_without_copying_facts: false`, and its
  `must_not_conclude` says go-to-market owns it, with the test that decides it — an announcement has
  no ordering axis, and deleting the ordering from it leaves it perfectly readable.
- The grouping reason for *one release* now names the scope definition and the changelog and
  explicitly states that the announcement for the same version is not listed here.

What this row **keeps**, on that row's own wording: the release-scope list with a cut line. That row
calls the evidence disjoint — a cut line here, a readiness column there — and says both may activate.
Nothing is conceded beyond the announcement.

---

## Files considered and rejected

The dispatch's own test: a row that only lists what it holds has not been researched. The first four
are kept as negative fixtures in the JSON.

| File | Why it is **not** this row's evidence |
|---|---|
| **`PRD - saved views.md`** (fixture) | Deliberately given a *single* target-release mention, so the fixture tests the right thing: one date does not make an ordering axis. Out-of-scope section, numbered requirement ids, acceptance criteria. Delete the ordering and it still reads. `product-requirements`. |
| **`Project plan - migration.xlsx`** (fixture) | Tasks with durations, predecessors, resources, percent-complete, a Gantt-shaped format. `project-delivery`'s own file names a dependency column as its strongest single discriminator and this row does not contest it. The Gantt shape is in `never_alone` because of this file. |
| **`Whats new in 4.2 - customer email.eml`** (fixture, **flipped to negative this pass**) | See above. `go-to-market`'s. |
| **`Atlassian public roadmap.pdf`** (**new fixture this pass**) | Every structural signal fires and the document is somebody else's plan. The discriminator is **custody**, not shape: a publications apparatus, another brand on the master, no internal audience marking and no approval route the holder is part of. Adopted in the same terms as `strategy-plan`'s `Corporate strategy 2030 - Rival plc.pdf`, so a reader checking either finds one account. **Reading Inbox.** |
| A **marketing campaign calendar** | Identical timeline shape; its items are sends, not commitments, and nothing is at a stated commitment level. Covered by the Gantt/timeline `never_alone` entry rather than given a fixture. |
| A **budget phasing sheet** | Period-scoped line items with variance against actuals. This is the file that best proves the period axis is not this row's evidence, and it produced the new `budget-forecast` edge rather than a fixture. |
| An **OKR set** | Objectives with measures and owners, no ordering axis, no cut line. `strategy-plan` folded the legacy OKR id into itself; this row does not contest it. |
| A **sprint backlog export** | Tempting, and rejected. Its ordering is a *work queue* recomputed continuously, with no commitment level and no audience; it is delivery machinery, not a communication. Where a repository is around it, `code` holds it. |
| A **public status page export** | Considered at gist depth and dropped as too instrument-specific; re-examined here and still dropped — it reports current state, has no forward order, and its rejection needs no new signal. |
| A **conference agenda** or an **event run-sheet** | Items placed in time cells with a labelled axis: the ordering-axis signal fires on shape alone. Discriminated by what the items are — sessions that will happen at a time, not intentions committed at a level. Named here because it is the closest false positive the repaired deletion test does **not** kill on its own. |
| An **architecture or system-dependency diagram** | The dependency signal fires. Its text layer names systems and processes rather than product items and periods, which is why that signal is marked corroborating rather than activating. |
| A **screenshot of a planning board with no context** | Kept as a fixture but routed to Temporary Screenshots when nothing is accepted around it; and the JSON repeats `00`'s warning that missing EXIF is not proof of a screenshot. |

---

## Collision fixtures, in both directions

**Direction one — a file that would wrongly fire this row and belongs to no named sibling:**
`Atlassian public roadmap.pdf`. Every structure fires; **custody** is the only discriminator, and it
is a discriminator no structural signal can see. Reading Inbox. This is the fixture the gist did not
have, and it is the row's genuinely hard case, because it is the one where the row's own signals are
all correct and the answer is still no.

**Direction two — files that must not be lost *to* this row:** `PRD - saved views.md`
(`product-requirements`), `Project plan - migration.xlsx` (`project-delivery`), and now
`Whats new in 4.2 - customer email.eml` (`go-to-market`). Each is named on both sides, on the same
bytes, with the same discriminator.

**The same bytes named by three rows:** `H1 roadmap.pptx`. `product-requirements` and `strategy-plan`
both name it as not-theirs and as the roadmap's; this row now names it as its primary positive
fixture, under the same filename, on the same evidence. A reader checking that one file finds three
consistent accounts.

---

## Reciprocal boundaries, both directions

Eight `collides_with` edges (one removed, two added this pass) and one `also_holds_with` (converted).
Direction of authorship recorded honestly.

| Neighbour | **They take** | **This row takes** | Contested bytes | Direction |
|---|---|---|---|---|
| `product-requirements` | out-of-scope sections, requirement ids, given-when-then criteria | an ordering axis with items in cells, a cut line, prioritisation scoring | `H1 roadmap.pptx` | **two-way**, settled there and confirmed here; one refinement offered |
| `strategy-plan` | costed alternatives, an owner column, an approval slot | items committed to positions in an order | a company-wide themes-by-quarter deck | **two-way**; both concessions now stated, including the one that costs this row |
| `go-to-market` | the readiness gate, positioning, enablement, the announcement | a release-scope list with a cut line, the ordering | `Whats new in 4.2 - customer email.eml` | **two-way**, narrowed this pass in their favour |
| `project-delivery` | a dependency-bearing schedule with resources and percent-complete | product items in an ordering axis with no task structure | `Project plan - migration.xlsx` | authored here; reciprocal owed |
| `budget-forecast` | period line items with variance against actuals | a forward order at a commitment level | a roadmap with costs per theme | **added this pass**; reciprocal owed |
| `meeting-record` | a standing team meeting that merely discusses the product | minutes of a review **of a named roadmap or release plan**, with a before/after position pair | roadmap-review minutes | **added this pass, reciprocating** that row's own cession, in its terms |
| `partnerships-bd` | a named counterparty being pursued, a proposal, a pre-contractual instrument | the roadmap itself, whatever folder it was sent from | a customer-cut deck in a pursuit folder | authored here; reciprocal owed |
| `board-governance` | notice, quorum, numbered papers, a resolution | the roadmap as a document inside the pack | a roadmap slide inside a board pack | authored here; reciprocal owed |
| `code` (**`also_holds_with`**, converted this pass) | the repository layout; a preserved root is not re-filed by this row | the document's release-record or ordering purpose | `CHANGELOG.md` | authored here; wording adopted from `product-requirements` so the two product rows do not diverge |

**The `code` edge was wrong and is corrected.** The gist carried `collides_with: code.software-project`.
That row is `refuse_node: true` — *"Fails the template half of the node test on all three limbs"* —
so the edge could never fire; it was a dangling pointer. And it was never mutex: the code schema
activates on evidence about a file's **location** (a repository root, a package manifest) while this
row activates on evidence about its **purpose**, and `00` licenses both being true of one file. Moved
to `also_holds_with`, pointed at the schema, with the reciprocal boundary stated: repository
atomicity is `code.json`'s own open question and `_CONTRACT` rule 7 forbids answering it by edge.
**This is a reversal of a gist decision and it is stated as one.** It is the identical correction
`product-requirements` made, adopted deliberately rather than re-derived.

## Neighbours considered that did NOT get an edge

- **`creative.content-marketing`** — the release announcement was the only overlap and it has been
  ceded to `go-to-market`, which already holds that boundary. Adding a third row to a two-row
  question would make the corpus less consistent, not more.
- **`engineering.stage-gate-review`** — a gated development plan. The `project-delivery` and
  `go-to-market` edges between them cover the schedule and the gate; a third edge would duplicate
  both.
- **`business_operations.market-research`** — a roadmap cites research and research recommends
  sequencing, but no file sits between them: research has a question, a method and a source set, and
  none of the three appears in this row's signals.
- **`business_operations.customer-account-management`** — customer-cut decks land in account folders.
  Covered by `partnerships-bd`; the discriminator (a named counterparty being pursued or served) is
  the same one, and stating it twice invites two answers.
- **`hr`** — a roadmap swimlane is labelled by team, not by person. If individuals appear with
  allocations it is `project-delivery` or `hr`, and either way the ordering axis has already stopped
  being the document's structure.

---

## Sparse-file discipline

The row's characteristic sparse file is `roadmap_board_export.png` sitting beside the deck. `00` is
explicit — *"The graph does not automatically copy those missing facts onto sparse files."* — and the
fixture's `must_not_conclude` says so. The row's other sparse hazard is a bare product name acting as
a bridge across a whole Downloads folder; `00`'s stop rule *"when one high-frequency entity acts as
the only bridge"* is now in `never_alone` for that reason. And a download session that dropped a
planning folder at once is not evidence of topic, per the session quotation the gist already carried.

## `proposed_fields`

**None**, and the temptation is named rather than acted on.

The obvious field-shaped hole is a **`product` / `offering`** key: this row's prose template argues
for a product level and cannot express one. It is **deliberately not proposed**, and this row
**seconds an existing recommendation rather than minting a variant**: `go-to-market` recorded that
if R1c licenses fields, the product/offering question should be adjudicated **once for the three
product rows** — `product-requirements`, `product-roadmap`, `go-to-market` — not separately on each,
and `product-requirements` declined for the same reason on the grounds that *arguing for a level is
not the same as being owed a key*. Three rows now agree; a fourth competing proposal would be the
574's mistake performed knowingly. **Recommendation to R1c: adjudicate the product/offering key once,
across the three product rows.**

A second hole is a **`release` / `horizon`** key. `go-to-market` named the same hole as
NJ-BO-GTM-2 and declined to propose it. This row declines identically: `fiscal_period` cannot express
a release (a release is not a management period) and `project` would assert that a release is a
project, which is precisely the claim the `project-delivery` boundary spends its argument denying.

The family's only live proposal is the schema row's `organization`, already flagged there as one
decision spanning two families. This row seconds it and adds nothing.

---

## NEEDS-JOSEPH

- **NJ-BO-10 · The pair question. *Settled as TWO rows; confirmed from this side and downgraded to a
  re-examination trigger.*** Settled in `product-requirements` on three separations; confirmed here
  on three independently chosen tests reaching the same verdict. The `open_question` on this row has
  been rewritten to record the settlement; **the paired row's still carries the gist wording, and
  this agent may not edit it. Ask for R1c: reconcile the two `open_question` texts**, and with them
  the delete-the-dates versus delete-the-ordering formulation, so the pair states one thing. The
  remaining trigger: if the fields pass never happens, or if real corpora show ordering axes and
  acceptance criteria co-occurring in one document more often than separately, re-examine the pair.
- **NJ-BO-12 · Supersession versus mere age — rewritten this pass, and narrower than the gist's.**
  The gist asked whether a superseded roadmap should be treated differently from an old version.
  Answered NO at the level of the node test: supersession cannot be this row's evidence, per the
  `policy-handbook` precedent. What remains open is a **product** question about the universal, not
  a question about this row: the version family has no notion of a member that has ceased to be
  *true* as opposed to merely being *older*, and this row is the clearest case in the catalogue where
  the difference has a user-visible consequence. Alternatives and their costs, as recorded in the
  JSON: **(a)** leave it — cheapest, risks a stale plan read as current; **(b)** let a row mark
  supersession as a handling hazard on the file — zero cost to the universal, no new machinery, and
  what this row does now; **(c)** extend the universal with an expiry notion — the largest change,
  touching every domain, out of proportion to one row's need. **This row takes (b) and recommends
  (b).**
- **NJ-BO-PR-1 · The audience level.** If R1c licenses fields, this row is the family's strongest
  case for an **audience** dimension, because the internal/customer cut is a near-duplicate pair with
  a disclosure consequence and no other level separates them. It is **not proposed** — it would be a
  new canonical key minted on a field-less schema by a placeholder row — but it is flagged, because
  the alternative is that the two members of that pair have no structural way to sit apart.
- **NJ-BO-GTM-2 · seconded, not restated.** The `release`/`horizon` key. `go-to-market` raised it;
  this row agrees and proposes nothing.

---

## Audits run before returning

1. **JSON parses** — `python3 -m json.tool` clean.
2. **Key set unchanged** from the gist and matching the landed siblings: 27 top-level keys, no key
   added or removed.
3. **Quotation audit** — all 25 quotation spans extracted by regex and checked with substring match
   against `planning/00-database-agent-product-design.md`. Three failures on the first run, all
   fixed: one was this row's own phrase in scare quotes (unquoted), one was a paraphrase of
   `go-to-market`'s edge presented as a quote (rewritten as attributed prose), and one was a genuine
   verbatim span from `code.software-project.json` (kept and labelled inline as such). Final run:
   **zero unverified spans.**
4. **Contract check** — `launch: "placeholder"`, `fields: []`, `proposed_fields: []`,
   `template.dimension_order: []`, `time_first: false`, `sensitivity: "potentially_sensitive"`,
   `role_split: []`, `design_cite: null`, `provenance: "proposal"`, `refuse_node: false`. No
   canonical key minted, no regex, no threshold, no file count, no statistic anywhere.
5. **Dangling-edge check** — every `collides_with` and `also_holds_with` target checked against
   `planning/domains/nodes/`. One dangling pointer found (`code.software-project`, refused) and
   corrected.
6. **Never-alone audit** — every deterministic signal checked against the schema anchor's
   structure-plus-slot rule. One failure found and demoted (the disclaimer).
7. **Files written** — exactly two, both this row's. No neighbour, no roster, no `src/`, no
   `check.py`. Every change wanted in a neighbour is a recommendation to R1c above.
8. **Self-audit of this memo's claims** — every assertion in *What changed in this pass* was re-read
   against the JSON on disk after it was written, per the dispatch.

---

## What changed in this pass

**Preserved unchanged** (the gist was right and re-phrasing it would be churn): the row's overall
*kept* verdict; `id`, `kind`, `schema_id`, `provenance`, `design_cite`, `launch`, `fields`,
`proposed_fields`, `sensitivity`, `role_split`, `file_kinds`; all five `falls_through_to` residuals
with their quotations; the prioritisation, release-scope, changelog and dependency signals; the
`needs_llm` precondition and the audience and mixed-deck entries; the `project-delivery`,
`partnerships-bd` and `board-governance` edges; seven of the nine file examples in substance; and the
core of `template.why` and `sensitivity_why`.

**Reversed, each stated as a reversal:**

1. **Expiry is no longer a node-test ground.** The gist named it the first of *"two things about this
   row that no sibling has"*. Reissue is a universal fact and cannot earn a row (`policy-handbook`'s
   precedent). Demoted to a handling hazard in `needs_llm`, with a new `never_alone` entry naming
   reissue and the `Roadmap 2024 - OLD.pptx` fixture now saying the gist was wrong to lean on it.
2. **The `code.software-project` collision edge is removed.** That row is `refuse_node: true`, so the
   edge could never fire, and the relationship was never mutex. Replaced by `also_holds_with: code`,
   in `product-requirements`' wording.
3. **The forward-looking disclaimer is demoted from activating to corroborating.** It is a labelled
   slot with no structure, which the family's never-alone rule forbids.
4. **The release announcement is ceded to `go-to-market`.** `name` changed, the announcement work
   type removed, the `.eml` flipped from a positive fixture to a negative one, the *one release*
   grouping reason narrowed.
5. **The anchor is restated.** From *"the HORIZON and the audience"* to **the ordered commitment**,
   because the gist's phrasing walked into charge (b). Time is now explicitly how the row is drawn
   and not what it is, and a period axis is disclaimed in `never_alone`.

**Added:**

- The **delete-the-ordering** test, offered as a refinement of the family's delete-the-dates test and
  shown to change no verdict, with the dateless board as the case the original could not see.
- The **dateless now/next/later rendering** as a first-class form of the row's primary signal.
- A **replanning / roadmap-review** deterministic signal (before-and-after position pair).
- Four new `never_alone` entries: a period axis or stated horizon (matching `strategy-plan`);
  reissue; the disclaimer and audience marking alone; a bare product name with `00`'s
  high-frequency-bridge stop rule.
- Two new edges — **`budget-forecast`** (answering charge (b) against the sibling that also has a
  period axis) and **`meeting-record`** (reciprocating its cession) — and rewritten signals on the
  `product-requirements`, `strategy-plan` and `go-to-market` edges stating both directions.
- A new fixture, **`Atlassian public roadmap.pdf`**, the custody case.
- The primary fixture **renamed to `H1 roadmap.pptx`** so all three rows that name it name the same
  bytes.
- The photos-exception quotation in `template.why`, and the two product-template divergences from the
  family default stated explicitly.
- The near-duplicate-pair argument in `sensitivity_why`, and `NJ-BO-PR-1`.
- `NJ-BO-12` rewritten to the narrow product question with three alternatives and a recommendation.

**Depth.** JSON 25.6KB → 41.0KB; memo 5.1KB → this file. The growth is neighbours argued with, false
positives named, and the node test actually reasoned through — not padding. Two sections the addendum
allows to be short are short because there is genuinely little to say: `proposed_fields` (none, and
the reason is a recommendation already made elsewhere that this row seconds) and `role_split` (empty
— unlike `procurement` or `contract-administration`, this row has no counterparty and therefore no
second side).
