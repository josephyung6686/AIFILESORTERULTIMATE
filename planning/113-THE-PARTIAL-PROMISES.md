# 113 — The Partial Promises

**Three of the nine statements in `107` §"What 'perfect' means" are not delivered.
This is the diagnosis of each to a root cause, the smallest mechanism that would
deliver it, and what that mechanism costs.**

Everything below is a row, a line of code, or a count produced by reading the
shipped library. No corpus was scanned: the file-grained figures are `108` §5's
and `production.py`'s own, quoted with their grain. Where this document
contradicts the brief that commissioned it, it says so and says why.

**One thing was built.** `9bf7432a` — promise 2's smallest mechanism, with two
tests. Promises 1 and 3 are drafted and not installed, for reasons each section
states.

---

## 0. The three promises, in one line each

| `107`'s sentence | verdict | root cause | mechanism |
| --- | --- | --- | --- |
| Coursework and teaching are visibly different | **the tree is ready; nothing routes to it** | no producer writes the situation BELOW the kind, and the evidence that separates the two is pooled at the schema level where it cannot discriminate | draft: per-situation role evidence + ask the question once per group |
| A file with several meanings remains discoverable | **BUILT** (`9bf7432a`) | `memberships` written every run since P9 shipped; no reader anywhere printed one | a sixth `--trail` stage over rows already written |
| Each domain uses a split order natural to it | **1 of 7 domains agrees** | the library ships 119 alternate orders that nothing can select, and `year` is bound in zero shipped rows | audit below; the control is `107`'s own and the owner's to shape |

---

## 1. "Coursework and teaching are visibly different even when they mention the same institution and course vocabulary"

### 1.1 The tree already delivers the visible difference. Nothing reaches it.

This is the finding that reframes the brief. The brief asked what evidence would
separate coursework from teaching, and implied the blocker is `subject` — known
for 35 of 371 files, with 35 of 43 labelled files carrying no course code in
their own bytes.

**`subject` is not the blocker, and the promise says so itself:** *"even when
they mention the same institution and course vocabulary."* A course code cannot
be the discriminator in a sentence whose whole point is that both sides carry the
same course code. Neither can `institution`, for the same reason.

The shipped library already separates them, on all three axes a person would see:

| | `academic.coursework` | `academic.teaching` |
| --- | --- | --- |
| life (top-level folder) | `Education` | `Teaching` |
| template | `def.subject-work-record` | `def.subject-work-record.third-party` |
| levels built | `school → term → subject → work_type` | `term → subject → work_type` |
| labels a person reads | "My school", "Semester", "Course", "Kind of work" | "Semester I taught", "Course I taught", "Kind of teaching material" |

(`src/tree_design/library/applicabilities.json`, rows `ap.academic.coursework`
and `ap.academic.teaching`.) Two different top-level folders and three
role-marked labels: if a file's situation were known, `107`'s promise would be
kept. **The failure is entirely upstream of the tree.**

### 1.2 Root cause: nothing writes a situation finer than the kind

`00` amendment 30 (`planning/00-…md`:644) rules the unit: *"the judge names the
KIND, and which situation within it remains the person's answer."* Site G
therefore returns `academic`. The finer value is written by the level stage, and
`src/production.py:657-660` records what that is worth today:

> *"Measured by the lead on the owner's corpus (18 Sep): 257 files carry a
> situation fact and 218 of them carry the KIND — `academic`, not
> `academic.coursework` — because the level stage that writes the finer value has
> mostly not run."*

218 of 257. For those files the product cannot choose between two situations of
one kind, so it cannot choose between two lives, two templates and two label
sets. It is not that the difference is invisible; it is that no file arrives at
it.

### 1.3 The evidence exists, and is stored where it cannot discriminate

The two situation rows state the real discriminator in prose
(`src/recognition/library/recognition.json`, `schemas.academic.situations`):

- coursework — *"on the student's side … a single holder's own study record.
  Material a teacher handed to you is yours here, not the teacher's."*
- teaching — *"files the holder made AS the instructor … the roster, gradebook
  and submission material that carries other people's names and grades. A brief
  or rubric the holder received as a student is coursework, not this."*

So the discriminator is **the holder's role** — author vs recipient — and its
proxy is **other people's names and grades on the page**.

Some of that evidence is already enumerated. `schemas.academic.work_type_terms`
holds 124 terms. Read one at a time rather than keyword-matched, a small number
of them sit on one side only:

- instructor's side: `answer key`, `class roster`, `gradebook`, `lesson plan`,
  `teaching notes`, `course proposal`.
- student's side: `homework`, `worksheet`, `essay`, `reading log`,
  `study schedule` — each backed by the coursework row's own sentence
  (*"handouts, worksheets and textbook pages you were given … the assignments,
  essays and practice work you handed in"*).

**No count is given for the rest, and that is the point.** Most of the 124 are
two-sided, and two of them are two-sided by the library's OWN sentences: the
teaching row lists *"the assignment briefs and rubrics"* as teaching and then
says *"A brief or rubric the holder received as a student is coursework, not
this."* A term list cannot settle `rubric`. Only the holder's role can. That is
why §1.5 puts the question first and the terms second.

**`work_type_terms` is a property of the SCHEMA, not of a situation.** Both
situations draw from the same pool. A situation row carries exactly three keys —
`id`, `name`, `one_line` — and no terms at all. So the one list in the library
that could separate the two is stored at the level where, by construction, it
separates nothing.

Nor is there a fact for it. `src/facts/authorship.py` is P6's §8.2 event authoring
and writes no holder-role fact; `fields.py`'s role pairs (`authored_by` /
`target_school`, `our_firm` / `client`) are entity roles on a document, not the
holder's own posture towards a course.

### 1.4 Does the corpus carry it? — what can honestly be said

Corpus scans are the lead's alone, so this is answered from aggregates. `108` §5:
`work_type` is known on 46 of 371 files and `model_returned_unknown` on 163.
`work_type` is the field that would carry `answer key` or `rubric`, so **on the
measured run the evidence is present on at most 46 files and absent or unasked on
the rest.** That is the ceiling, and it is a ceiling on the FIELD, not on the
bytes: `no_candidate_evidence` for `work_type` is 332 with
`attempted_producers=["rule"]`, which `104` §18.109 already corrected — it is the
deterministic rule abstaining and says nothing about what a model would find.
**Whether the bytes carry a roster or an answer key has not been measured.** It
should be, and the measurement is one the lead can run and this document cannot.

### 1.5 The smallest mechanism — DRAFT ONLY, three parts, in order of size

**(a) Ask once per group, not once per file.** The holder's role is constant
across a course-term: a person is a student of a course or the instructor of it,
not both in one term. So the question *"were you taking this course or teaching
it?"* is a group-grained question, and the product already has group-grained
questions and accepted groups. One answer settles a packet. This is the cheapest
of the three by an order of magnitude and it needs no new evidence at all — it
needs the existing question asked at the group's grain instead of the file's.
**It is question text, so it is the owner's alone. DRAFT.**

**(b) Carry the teaching-side `work_type` values as candidate evidence into that
question.** The one-sided terms listed in §1.3 are already in the library; what is
missing is a key from term to situation. The smallest form is a `situation_terms` key on the
two situation rows — an ADDED key on an existing row, not an edit to a member of
a closed vocabulary. `108` §7 permits adding a versioned row in
`src/recognition/library/**` and forbids editing one; adding a key to an existing
row is neither, so **DRAFT, and the owner rules whether it is an add or an edit.**

**(c) A holder-role recogniser.** A deterministic observation for "this page
carries several other people's names beside marks" would settle the teaching side
without a model. It is the largest of the three, it is a new producer, and `109`
records what this codebase does to invented parallel machinery. **Do not build it
until (a) is measured and found insufficient.**

**Blocked on the owner**, all three: (a) and (b) are library text, (c) should not
be built before (a) is tried.

### 1.6 One defect found in passing, and it is a preference, not a defect

`ap.academic.teaching` leaves `holder_institution` unbound and omits `school` from
`allowed_fields`, so Teaching builds `term → subject → work_type` where `107`'s
table says *"Institution → term → course → teaching function"*. That looks like a
plain defect. It is not: the row's own provenance memo
(`planning/domains/nodes/academic.teaching.research.md`:54-55, 157-158) states the
choice and raises it as an open question —

> *"`school` is dropped (one employer → a one-child level) … **Does the teaching
> recommendation keep `school`?** Dropped here as a one-child level, which is
> right for a full-time instructor and wrong for an adjunct teaching at two
> institutions."*

`108` §7's reading of `00` amendment 24, exactly: which level comes first, and whether a
one-child level is worth its folder, depends on the user. **Preference. The
library's own author already flagged it and it belongs in §4's list, not in a
patch.**

---

## 2. "A file with several meanings remains discoverable through every accepted relationship, even though it has one physical path"

### 2.1 The lead's finding is confirmed, and it was narrower than the truth

The lead reported finding no mechanism. Verified, and the diagnosis is sharper
than "no mechanism": **the mechanism was complete except for a reader.**

What exists and runs:

- `src/grouping/schema.py:71` — `memberships`, one row per file per group, with
  `basis`, `decision`, `decision_source`, `support`, `outlier_flag`, and
  `CREATE INDEX memberships_file ON memberships (file_id, content_hash)`. The
  index for this exact question was already there.
- `src/grouping/schema.py:103` — `group_edges`, indexed from and to.
- `src/grouping/store.py:383` — `live_memberships_of_file`, the reader, written
  and used by `grouping/pipeline.py:509` and `cli.py:14479` (`accepted_memberships_of`).
- `src/tree_design/vocabulary.py:367-378` — §6.9's `shared-branch`,
  `primary-home`, `reference-or-alias`, `mandatory-review`, with a writer at
  `tree_design/store.py:408`.

What did not exist: **any reader that put one of those rows on a person's screen.**
`grep -c "membership\|group_id\|groups" src/review_surface/trail.py` returned
**0**. `--trail` — the product's one per-file surface, `104` §18.27 gap 25 —
printed five stages ending at `PLACED`. A person reading a trail was shown the one
meaning that won and none of the ones that did not.

Two clarifications the honest version needs:

- **No alias or symlink is ever minted on disk.** `reference-or-alias` names a
  POLICY that resolves to a destination; `placement.groups.resolve_multi_home`
  chooses where the file goes. It is a placement answer, not a discoverability
  one, and `107`'s sentence explicitly concedes the single physical path.
- **There is no search command.** The CLI is one command with 43 flags
  (`src/cli.py:25365`); there is no `find`, no `search`. `--trail` is the only
  gesture that takes a file's name.

### 2.2 The mechanism, BUILT — `9bf7432a`

A sixth trail stage, `RELATED`, after `PLACED`:

- reads `memberships` joined to the live `groups` row, for THIS file version,
  which is `live_memberships_of_file`'s own rule;
- prints the group's label, category, state and coherence verdict, the
  membership's basis and who decided it, plus insufficiency and outlier when set;
- prints a sentence when there are none, because this module's standing rule is
  that every stage prints including the empty ones (`00`:259);
- prints the `decision` verbatim rather than filtering to the accepted ones —
  `104` R-16 is that `draft_for_review` writes `included` for everything today, and
  a reader that dropped the rest would print an identical screen on the day that
  stops being true.

It opens no file, asks no model, mints nothing on disk and adds no table. It
reads rows every run already wrote. Read as rows rather than through P9, which is
`_placed`'s own choice one table over.

**Both directions of the promise now exist** — verified, not inferred from
`--accept-groups`' help text. Relationship → files was already there:
`review_surface/items.py:239, 274-277` gives `GroupPlanReviewItem` a
`member_items` tuple, one ordinary `PlacementReviewItem` per member read off
`plan.member_decisions`, and its docstring is explicit that this is *"a framing,
never a wrapper that hides its members."* File → relationships is what this adds.
Naming the file prints every accepted relationship it keeps, from whatever folder
it ended up in.

One boundary: that projection is of P11's GROUP PLAN, so its member list is the
plan's. The `RELATED` stage reads P9's `memberships` directly, which is the wider
set — a membership exists whether or not a plan was built from it.

**Cost:** ~70 lines in `src/review_surface/trail.py`, 2 tests.
`tests/test_cli_trail.py`: 12 passed.
`tests/integration/test_site_g_records_a_file_with_no_route.py`: 4 passed.
`tests/p13/test_p13_no_invention.py`: 8 passed — the guard `trail.py`'s own
docstring names over this package, run because ~70 new lines in it are exactly
what it inspects.

**What it does NOT deliver, stated plainly.** 133 of 371 files were in a group on
the measured run (`108` §5). For the other 238 the stage correctly prints that the
file belongs to nothing, which is true and is not the promise. The promise is kept
for a file that HAS several meanings; making more files have them is coverage
work, not a reader.

---

## 3. "Work projects, career applications, family records, taxes, health, travel, and photos each use a split order natural to that domain"

### 3.1 What the machinery actually is

The shipped release is 8 files (`production.LIBRARY_FILES`), **63 template
definitions and 208 applicability rows**. Each definition carries
`candidate_orders`; each applicability row binds roles to P6 field keys.
`production.folder_levels_for` (`src/production.py:564-621`) joins the two — it
walks `definition.default_order.dimensions` by `order_index` and takes the row's
binding for each role, skipping a role the row does not bind.

Two facts about that join govern everything below.

**(a) Only the default order is ever read.** `templates.py:427` names it *"The one
order the recipe RECOMMENDS. **Not the one it imposes**"*, and `templates.py:386`
refuses a definition with two defaults because *"a definition RECOMMENDS exactly
one and **the end user picks per branch (§5.3, §5.8)**; … **the branch binding
records the chosen id**."* The library was built for the person to pick.
`folder_levels_for` reads `default_order` unconditionally and nothing anywhere
reads a non-default `candidate_order`. **119 of 208 rows ship an alternate order
that nothing in the product can select.**

**(b) An unbound role is a skipped level, by design and not by accident.** 125 of
628 default-order dimensions across the release have no binding — a figure
`folder_levels_for`'s own docstring already states and explains: *"a definition is
generic and an applicability row binds the subset its situation uses. A role with
no field is not a level this situation builds."* So an unbound role is NOT a
defect on its own. Exactly one row in the whole release leaves a **required**
dimension unbound (`ap.business_operations.procurement-sourcing`, missing
`record_function`), and that is outside every domain `107` names.

### 3.2 The audit — `107`'s stated order against the shipped order

`107` names seven domains in this promise. Shipped levels are what
`folder_levels_for` returns, field keys as bound.

| `107` domain | `107`'s stated order | shipped row | shipped levels | verdict |
| --- | --- | --- | --- | --- |
| **Taxes** | Tax year → record class | `ap.finance.tax-filings` | `tax_year(req) → record_type(req)` → *issuing_org unbound* | **AGREES** — the only one that does |
| **Work projects** ("Current work") | Employer → year → project or activity → stage | `ap.career.employment-records` | `employer(req) → job_title(opt) → `*cycle_period unbound*` → record_type(req)` | **DEFECT** — `year` absent, no project level |
| **Career applications** | Year → organization and role → application stage | `ap.career.recruiting` | `target_employer(req) → job_title(opt) → recruiting_cycle(opt) → work_type(req)` | **PREFERENCE** — right dimensions, inverted order |
| **Family records** | Person → context → year or cycle → record type | `ap.academic.k12-schooling`, `.homeschool`, `.iep-plans` | `school → term → work_type` / `term → subject → work_type` / `school → term` | **PREFERENCE + coverage** — no person level anywhere |
| **Health** | Person → year or durable category → record type | `ap.finance.insurance-healthcare` only | `institution(req) → record_type(req)` | **COVERAGE GAP** — one row in the whole life; `medical` has 0 situations (`108` §6.1) |
| **Travel** | Year → trip → function | `ap.travel.bookings-confirmations` | `record_type(req) → institution(opt)` | **DEFECT in principle** — inverts `107` design principle 1 |
| | | `ap.travel.trip-photos` | `event(req) → location(opt) → `*capture_time unbound* | **PREFERENCE** — trip first, year unreachable |
| **Photos** | Year → event → rendition | `ap.photos.camera-events`, `.drone-captures` | `capture_year(req) → event(opt)` | **PREFERENCE** — no rendition level exists on the first-party recipe |
| | | `ap.photos.social-media-export` | `capture_year(req) → event(opt) → media_type(opt)` | **AGREES** |

And, for completeness, the other `107` table rows:

| `107` template | `107`'s stated order | shipped levels | verdict |
| --- | --- | --- | --- |
| Coursework | Institution → program → term → course → work type | `school → term → subject → work_type` | **PREFERENCE** — no `program` field exists |
| Teaching | Institution → term → course → teaching function | `term → subject → work_type` | **PREFERENCE** — §1.6, the memo already flagged it |
| Projects | Project → stage or artifact class | `project → artifact_type → stage` | **AGREES** |
| Property | Property → function → project or year | `record_type` alone; `institution → record_type` | **COVERAGE GAP** — `property` is bound on 13 wave-2 rows, none of them in the Home and Property life |
| Reference | Status or topic → subtype | `project → artifact_type` | **AGREES** |

**One of seven named domains agrees. Taxes.**

### 3.3 Which are defects and which are preferences (`00` amendment 24)

Amendment 24's test: a **truth** is the library's to settle; a **preference** is
the person's, and shipping it as a fixed default is the defect rather than the
value being wrong.

**DEFECTS — the library is wrong, not merely opinionated:**

1. **`year` is bound as a folder level in ZERO shipped rows.** `00` amendment 20
   added the field (`facts/fields.py:231`) with a producer (`cli.year_facts`, over
   `creation_date`), citing `107`'s three orders by name. `00` amendment 22 then
   ruled it bound on Current work and Career applications. It is bound in exactly
   one place in the repository — `src/tree_design/library/drafts/health_travel.json`:107,
   133, 159 — which `108` §3 records is *"wired to NOTHING, with a gate test
   asserting the names are absent from the shipped release."* A ratified ruling
   with a producer and no binding is a defect.
2. **Travel bookings file by function before context.** `record_type → institution`
   puts the volatile document type above the stable one, which is `107` design
   principle 1 inverted (*"Stable context comes first"*). It is not fixable here:
   the trip is a P9 group and not a fact (`108` §3 ruling 21), so the level `107`
   asks for cannot be bound to anything. **Blocked on ruling 21.**
3. **Health has one applicability row in the entire release**, and it is an
   insurance row. `107` gives Health its own order. There is nothing to disagree
   with. **Library coverage, not code** — `108` §6.1's finding, unchanged.

**PREFERENCES — the value is arguable and the missing thing is the control:**

4. Career applications' order (`107` wants year first; shipped is employer first).
5. Photos' rendition level, Coursework's `program`, Teaching's `school`, Family
   records' person level, Property's property level.
6. Travel photos' trip-before-year.

Every one of 4-6 is a *"change split order"* or *"change depth"* row in `107`
§Customization. `108` §7 states the consequence: *"`107` promises 'every split can
be changed before freeze' and **that control does not exist**."*

### 3.4 `tax_year` — the brief's claim, corrected

The brief states `tax_year` has **no producer** and is *"a level that is correct
and permanently blank."* Half right, and the correction matters.

- `tax_year` is a registered field (`facts/fields.py:366`), in the model's glossary
  with a meaning (`llm_harness/library/field_glossary.json`), and bound **required**
  on two shipped rows: `ap.finance.tax-filings` (`tax_year → record_type`) and
  `ap.finance.payroll-received` (`institution → tax_year → record_type`).
- **No DETERMINISTIC producer exists.** Zero field targets in
  `src/recognition/library/recognition.json` name it; the seven mentions there are
  all prose in `one_line` sentences.
- **A producer does exist: site E**, the level pass (`cli.py:10390`), which asks a
  model for whatever `folder_levels_for` returns, over a local target only. So
  the honest statement is: **`tax_year`'s only producer is the site-E local model,
  and that stage has mostly not run** — the same sentence `production.py:658`
  already writes about the fine situation. It is not structurally unfillable; it
  is unfilled.

**Smallest mechanism, DRAFT ONLY.** A labelled-slot recogniser — a document that
prints its own tax year in a labelled field — is a recogniser row in
`src/recognition/library/**`, and library rows are added by the owner. It is also
the narrow case `recognition.json` already states twice: *"`tax_year` as an
optional leaf only where a document carries its own labelled tax-year slot."*
The library already knows the rule; nothing implements it.

### 3.5 The smallest mechanism for the rest — PROPOSE, do not build

`108` §3 recorded amendment 22 as blocked because *"rows cannot do it …
`folder_levels_for` builds levels only from the template's default-order
dimensions and silently DROPS any other binding … Needs a dimension in
`definitions.json`, and one default order cannot serve both `employer → year` and
`year → organization`."*

**The first half is right and the conclusion is larger than it needs to be.** One
default order indeed cannot serve both — but a definition already carries several
orders, and `def.career-search-and-tenure` already ships `ord.cycle-kind-employer-role`
beside its default. What is missing is not a dimension: **it is a reader for the
order the row or the person chose.** The smallest shape is a chosen-order id on
the applicability row or the branch binding, which `templates.py:384-390` says the
design already expects (*"the branch binding records the chosen id"*), and
`folder_levels_for` preferring it over `default_order`.

That single change would convert every preference in §3.3 from a defect into a
setting, which is what `107` §Customization and `00` amendment 24 both ask for,
and it would unblock 119 of 208 rows at once.

**It is deliberately NOT built here.** It is the *"change split order"* control —
the one `108` §7 names as the thing most of the owner's 18 Sep questions should
have been. A control that shapes how every future question is asked is the
owner's to see before it is installed, and building it inside a diagnosis
document is exactly the invented-parallel-machinery move `109` records this
codebase punishing. It needs `year` bound as well, which is amendment 22's own
ruling and a library edit.

---

## 4. Blocked on the owner — the short list this produces

1. **The coursework/teaching question, asked once per group** (§1.5a). Question
   text. The single cheapest thing in this document.
2. **Whether `situation_terms` may be added to a situation row** (§1.5b) — an
   added key on an existing row, which `108` §7 neither clearly permits nor
   clearly forbids.
3. **Whether Teaching keeps `school`** (§1.6) — the row's own memo raises it
   verbatim; adjunct vs full-time instructor.
4. **`year` bound on Current work and Career applications** (§3.3.1) — amendment
   22, ratified, still bound in no shipped row.
5. **A chosen-order reader** (§3.5) — the "change split order" control. Shape it
   before it is built.
6. **A labelled-slot `tax_year` recogniser** (§3.4) — the library already states
   the rule.

## 5. Where this contradicts its brief

- **Promise 1 is not a `subject` problem.** The promise's own wording rules out
  course code and institution as discriminators. The discriminator is holder role,
  some of the evidence for it is already in the library, and it is stored on the schema
  where it cannot separate two situations of that schema.
- **Promise 2's mechanism was not missing.** Every row, index and reader existed;
  only the surface did not. That is why it cost 70 lines.
- **`year` is NOT bound where `107` says.** The brief states it is. It is bound in
  zero shipped applicability rows, and in exactly three lines of an unwired draft.
- **`tax_year` is not producer-less.** It has no deterministic producer; its
  producer is the site-E local model, and the level stage has mostly not run.
- **The default orders are not mostly wrong.** One of seven named domains agrees,
  but five of the six disagreements are preferences, and they are defects only
  because the control `107` promises for exactly this does not exist.
