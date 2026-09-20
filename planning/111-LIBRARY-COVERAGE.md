# 111 — LIBRARY COVERAGE: THE MEASURED CENSUS, AND WHY ALMOST NOTHING IS DRAFTED

> **STATUS.** Measurement + one drafted row + a ratification packet. Nothing in
> this document is installed. The one drafted row is at
> `src/tree_design/library/drafts/academic_teaching_institution.json`, wired to
> nothing, gated by `tests/p10/test_library_academic_teaching.py`.
>
> **THE HEADLINE CONTRADICTS THE BRIEF THIS WORK WAS GIVEN.** The brief said:
> *"`academic` has 11 situations for the owner's 95 academic files. `medical` has
> ZERO. The tree is thin because the library describes someone else's life."*
> The distribution finding is **confirmed and reproduced**. The prescription that
> followed it — draft situation rows for `academic` and `medical` first — is
> **not supported by the measurement**. `academic` has no missing situations at
> all; `medical`'s are already drafted or explicitly refuse folder levels in
> their own ratified text. The owner's branches are thin because of **fields and
> bindings**, not missing situation names. §5 and §7 are the real work.
>
> **NO NEW NAME IS MINTED ANYWHERE IN THIS DOCUMENT.** `109` row 21 warns that a
> new name enters a cloud-bound menu. Every proposal below reuses a name already
> in the shipped recognition release. The only drafted vocabulary is **one
> folder label**. See §8.

---

## 1. What was measured, and how to reproduce it

Everything in §2–§4 is read from the shipped release with no judgement applied:

* **Supply (tree_design):** the `applicabilities` lists of the five library files
  that carry rows, which are the files named in `production.LIBRARY_FILES` —
  `applicabilities.json`, `wave2_commerce.json`, `wave2_industrial.json`,
  `wave2_organisational.json`, `wave2_practice.json`. A situation's folder levels
  are `folder_levels_for`'s answer: the definition's `default_order.dimensions`
  in `order_index` order, each one carrying the applicability row's
  `role_bindings` label and field.
* **Names (recognition):** `schemas[*].situations[*].id` in
  `src/recognition/library/recognition.json`.
* **Fields:** `facts.fields.DOMAIN_FIELDS`, `UNIVERSAL_FIELDS`, and
  `FIELD_ROWS[*].destination_eligible`.
* **Demand:** `107` — the owner's own branch-template table and their own tree.

No corpus was opened and no file, folder or course name from the owner's own
material appears here. The corpus counts quoted in §4 are `104` §18.112's
already-published aggregates.

## 2. CENSUS — situations per schema in the shipped release

**208 applicability rows across 19 of the 23 recognised schemas.** Four schemas
carry none.

| schema | rows | life | schema | rows | life |
| --- | ---: | --- | --- | ---: | --- |
| `creative` | 28 | Creative and Hobbies | `logistics` | 6 | Career |
| `law_practice` | 26 | Career | `hr` | 6 | Career |
| `construction_property` | 22 | Career | `college_applications` | 5 | Education |
| `finance` | 18 | Finance and Taxes | `code` | 3 | Technology |
| `engineering` | 15 | Career | `career` | 3 | Career |
| `manufacturing` | 15 | Career | `government` | 3 | Career |
| `retail_hospitality` | 12 | Career | `nonprofit` | 2 | Personal |
| **`academic`** | **11** | Education | **`clinical_practice`** | **0** | Career |
| `photos` | 9 | Photos and Media | **`identity`** | **0** | Personal |
| `research` | 8 | Education | **`legal`** | **0** | Legal and Insurance |
| `resource_operations` | 8 | Career | **`medical`** | **0** | Health |
| `business_operations` | 8 | Career | | | |

**On the "113 of 208" figure.** The brief listed eight schemas — law practice,
construction, manufacturing, engineering, retail, logistics, HR, government.
Those eight sum to **105**, not 113. `104` §18.112's own list includes a ninth,
`resource_operations` (8), which is where 113 comes from. Both sums are
reproducible; **113 is `104`'s list and is the one used here**. The wider figure
is that **124 of 208 rows (59.6%) sit under the `Career` life**, and only 3 of
those 124 are the `career` schema itself — the one that holds an ordinary
person's own employment and job-hunting records.

**Depth, per schema** (levels `folder_levels_for` actually answers):

| schema | rows | max depth | mean depth |
| --- | ---: | ---: | ---: |
| `resource_operations` | 8 | 6 | 6.00 |
| `creative` | 28 | 4 | 4.00 |
| `career` | 3 | 4 | 3.67 |
| **`academic`** | **11** | **4** | **3.45** |
| `manufacturing` | 15 | 4 | 3.27 |
| `construction_property` | 22 | 4 | 3.09 |
| `research` / `engineering` | 8 / 15 | 4 / 3 | 3.00 |
| `retail_hospitality` | 12 | 3 | 2.83 |
| `finance` | 18 | 3 | 2.67 |
| `photos` | 9 | 3 | 2.56 |
| `law_practice` | 26 | 3 | 2.27 |
| `government` / `hr` | 3 / 6 | 1 | 1.00 |

A single professional schema (`resource_operations`, 8 rows) is deeper at every
row than any branch the owner's own tree draws.

## 3. CENSUS — the recognition library carries 86 more names than the tree does

This is the measurement the brief did not anticipate and it changes the
prescription.

* **recognition situations: 294** across the same 23 schemas.
* **tree_design applicability rows: 208.**
* **recognition situations bound by at least one tree_design row: 207.**
* **recognition situations with NO tree_design row: 87.**

(207 + 87 = 294. The 208th tree_design row carries the signal `recognition:
nonprofit`, a schema row rather than a situation row — `src/recognition/rules.py`
documents this exact case: "one of the 208 shipped situations (`nonprofit`) is a
schema row and has no template row of its own." It is not a defect.)

| schema | recognition names | tree rows | **unbound** | 107 demands it? |
| --- | ---: | ---: | ---: | --- |
| `government` | 29 | 3 | 26 | no — 107 silent |
| `business_operations` | 22 | 8 | 14 | no — 107 silent |
| `clinical_practice` | 6 | 0 | 6 | no — 107's person is not a clinician |
| `hr` | 11 | 6 | 5 | no — 107 silent |
| `nonprofit` | 6 | 2 | 5 | partly — Memberships |
| `legal` | 4 | 0 | **4** | **yes — Legal and Insurance** |
| `creative` | 32 | 28 | 4 | partly |
| `engineering` | 19 | 15 | 4 | no |
| `manufacturing` | 19 | 15 | 4 | no |
| `career` | 6 | 3 | **3** | **yes — Career/Profile, Memberships** |
| `identity` | 3 | 0 | **3** | **yes — Personal/identity records** |
| `medical` | 3 | 0 | **3** | **yes — Health** |
| `law_practice` | 28 | 26 | 2 | no |
| `retail_hospitality` | 14 | 12 | 2 | no |
| `logistics` | 7 | 6 | 1 | no |
| `photos` | 10 | 9 | 1 | partly |
| **`academic`** | **11** | **11** | **0** | **yes — and nothing is missing** |
| `code`, `college_applications`, `construction_property`, `finance`, `research`, `resource_operations` | — | — | 0 | — |

**`academic` has zero unbound situations.** Every name the recognition library
authored for it already has a tree_design row. There is no academic situation to
draft. The academic problem is real but it is a different problem — §5.

## 4. The demand side — `107`'s branches against what the library answers

`107`'s branch-template table is the owner's own description of their life. Read
against the shipped rows:

| `107` template | `107`'s default split order | best shipped answer | gap |
| --- | --- | --- | --- |
| Coursework | institution → **program** → term → course → work type | `school → term → subject → work_type` (1 row of 11) | **`program` is not a field.** 5 of 11 academic rows also bind no `term`. |
| Teaching | **institution** → term → course → teaching function | `term → subject → work_type` | **the institution slot exists and is unbound** — §5 |
| Current work | employer → year → **project or activity** → **stage** | `employer → job_title → ? → record_type` | **`project` and `stage` are not fields at `career`** |
| Career applications | year → organization and role → stage | `target_employer → job_title → recruiting_cycle → work_type` | order differs; no `year` level |
| Taxes | tax year → record class | `institution → record_type` (8 of 18) | tax year is not the lead level |
| Health | person → year or durable category → record type | **nothing** | drafted in `drafts/health_travel.json`, unratified |
| Travel | year → trip → function | `event → location` (photos only) | drafted in `drafts/health_travel.json`, unratified |
| Photos | year → event → **rendition** | `capture_year → event` | **`rendition` is not a field** |
| Family records | person → context → year → record type | `school → term → work_type` (K-12 row) | person level deliberately absent (`107` line 120) |
| Projects | project → stage or artifact class | `project → artifact_type → stage` | **aligned, and richer** |
| Property | property → function → project or year | `property → project → work_type` | aligned |
| Reference | status or topic → subtype | — | 107 silent on a schema for it |
| Residual | residual state → broad subtype | residual templates, separate machinery | out of scope here |

Corpus weight, from `104` §18.112's published aggregates: the owner's files are
`academic 95 | research 60 | photos 27 | career 22 | medical 4 | creative 3`,
against library rows `academic 11 | research 8 | photos 9 | career 3 | medical 0
| creative 28`. **The skew is confirmed.** What follows is what can honestly be
done about it.

## 5. PROPOSED SITUATION ROWS — there is exactly one, and it is `academic`

### 5.1 The row: `academic.teaching`, version 2 — the institution level

* **situation id:** `academic.teaching` — **already in the shipped release.** No
  new name.
* **schema:** `academic`. **life:** `Teaching`. **template:**
  `def.subject-work-record.third-party@1` — already shipped.
* **folder levels it would build, in default order:**

  | # | role | field | label | requirement |
  | ---: | --- | --- | --- | --- |
  | 0 | `holder_institution` | `school` | **"School I taught at"** ← the only drafted vocabulary | optional |
  | 1 | `cycle_period` | `term` | "Semester I taught" (unchanged from v1) | optional |
  | 2 | `subject_anchor` | `subject` | "Course I taught" (unchanged from v1) | required |
  | 3 | `artifact_kind` | `work_type` | "Kind of teaching material" (unchanged from v1) | required |

* **why that order is natural to teaching:** it is `107`'s own — *Institution →
  term → course → teaching function* — and `107`'s tree draws the institution
  explicitly above the term. A teaching load is re-planned each term, so the term
  keeps two offerings of one course apart; the institution sits above both
  because the same course title taught at two places is two different bodies of
  material, and because `107` principle 1 puts stable context before volatile
  document types. This is not a new order: the shipped definition already
  declares `holder_institution` as an **optional dimension at `order_index` 0**.
  The row simply binds it.
* **why it is safe:** `school` is live, destination-eligible, and declared at
  `academic`. **This row carries no dependency gap at all** — unlike the Health
  and Travel drafts, nothing has to be added to the facts layer first.
* **exclusions carried on the row:** no student name as a level (`107` line 120,
  and `107`'s Teaching branch marks Student Administration "protected; no
  student-name folders"); the lesson-week children beneath the teaching function
  are the person's to add, not a dimension this row binds.

### 5.2 THE COST OF WIRING IT, MEASURED — it cannot be added, only substituted

The standing orders permit **adding** a versioned row and forbid **editing** an
existing one. For applicability rows those two are not alternatives, and the test
measures it rather than asserting it. With v1 and v2 both loaded:

| call | behaviour |
| --- | --- |
| `folder_levels_for` | **REFUSES** — "carried by 2 applicability rows" |
| `life_of` | **REFUSES** — same reason |
| `template_id_for_situation` | **REFUSES** — same reason |
| `schema_for_situation` | **resolves** — it refuses only when rows *disagree*, and both say `academic` |
| `shipped_situations` (the cloud-bound menu) | **silently keeps v1's three labels**, still reports 208 situations |

A situation is resolved by scanning every row for its `recognition:` signal, and
a second row does not supersede the first — they coexist and the situation stops
resolving. **The menu would go on advertising three levels with no institution,
while the level-builder refused to build anything at all, and nothing would
raise.** The person is shown one answer and the product holds another.

So wiring this row means **replacing** `ap.academic.teaching@1`, which is an edit
to a shipped row. That is the owner's alone. It is question 1 of §8.

### 5.3 THE ROWS THAT ARE NOT PROPOSED, AND WHY — this is most of the finding

The test applied to every unbound recognition name in a schema `107` demands:
*draft it only if `107` draws a level below that branch which a
destination-eligible field at that schema can fill, and the situation's own
ratified text does not refuse folder depth.*

**`medical` — 0 new rows.** Not because the gap is not real, but because:
* `medical.personal-health-records` and `medical.dependant-child-health` are
  **already drafted** at `drafts/health_travel.json` under amendment 21. Drafting
  them again would collide on `(id, version)` and break both gate tests.
* `medical.wearable-health-exports` **refuses folder levels in its own ratified
  text**: it keeps the packet coherent "without turning any metric, device,
  person, condition, date range, or app name into a Medical fact or folder
  level." `107`'s Health leaves — Visits, Test Results, Prescriptions, Bills and
  Claims, Immunizations, Long-Term Records — never name a wearable export.
  **`107` is silent here and the row is not minted.**

**`identity` — 0 rows.** All three names refuse depth in their ratified text:
core documents "proposes no folder dimensions"; credentials "creates no
automatic folder depth"; immigration "recommends no folder dimensions ... because
the Identity schema is a field-less safety placeholder." `107`'s identity branch
splits by record kind (Passports / Birth and Citizenship / Licences and IDs /
Marriage and Family Status / Name and Address Changes) and `record_type` **is not
referenced at `identity`**. The only bindable field is universal `year`, and
`107` draws no year level under that branch. A `year`-only row would build a
level the owner did not draw. **That is inventing a taxonomy; it is not done.**

**`legal` — 0 rows.** Same shape. Estate planning "recommends no automatic folder
depth"; leases "authorizes no agreement facts and no deep destination tree";
personal matters "recommends no folder dimensions". `107`'s Estate Planning
splits by record kind (Will / Power of Attorney / Advance Directive) and
`record_type` is not referenced at `legal`. `legal.practice-matter-file` is a
practitioner's row and belongs to the professional side `107` does not describe.

**`career` — 0 rows, and this one is close.** `career.portfolio-work-samples`
maps to `107`'s Career/Profile/Portfolio, and `career.credentials-licenses` to
Personal/Memberships/Professional Associations. But `107` draws **both as
leaves** — no child level beneath either — and `107`'s Memberships splits by
*kind of body* (Professional Associations / Clubs and Community / Rewards and
Loyalty), which no field supplies. Binding `record_type` would build a different
split from the one the owner drew. **Left for question 4.**

**`nonprofit` — 0 rows.** `nonprofit.volunteering-and-club-life` maps to `107`'s
Memberships/Clubs and Community, which is again a leaf. `organization` is not
destination-eligible; `institution` is, but `107` draws no club-named level.

**`photos.personal-graphics` — 0 rows.** Its ratified text ends "Declares no
field rows under PR-6."

**`government` (26), `business_operations` (14), `clinical_practice` (6),
`hr` (5), `engineering` (4), `manufacturing` (4), `law_practice` (2),
`retail_hospitality` (2), `logistics` (1) — 0 rows. `107` is silent on all of
them.** These 64 unbound names are the professional side of the library. `107`
describes a product designer who studies part time and teaches occasionally; it
says nothing about a regulator, a plant, a fleet or a practice. **Where `107` is
silent, nothing is filled in.**

### 5.4 The branches `107` demands for which NO ratified name exists

`107` draws these and the recognition library has no situation for any of them.
They are recorded as a gap and **not minted**, because a new name is exactly what
`109` row 21 forbids:

Pets · Family Events · Personal Correspondence · Personal Planning (Goals,
Journals, Calendar Exports) · Recipes · Games · Devices and Software · Data
Exports · Reference Clips and Templates · Vehicles as a branch of its own
(`finance.vehicle-records` exists but `107` gives Vehicles a top-level home with
six functions beneath it).

## 6. WHERE THE DRAFT GOES, AND WHY IT IS NOT INSTALLED

**File:** `src/tree_design/library/drafts/academic_teaching_institution.json`,
following the precedent of `drafts/health_travel.json`.

**Wired to nothing.** It is absent from `production.LIBRARY_FILES`, so
`read_packaged_library_file` refuses it by name; it sits under `library/drafts/`,
which no shipped-vocabulary pin globs (the pins glob `*.py`); and it declares no
fragments and no definitions, reusing a shipped template.

**Gate test:** `tests/p10/test_library_academic_teaching.py`, 12 tests, all
passing. It asserts the draft parses through the real loader, mints no name,
carries v1's three bindings forward unchanged, builds `107`'s order, needs no new
field, names no person — and, as the gate, that the draft is absent from
`LIBRARY_FILES`, that `read_packaged_library_file` refuses it, and that adding it
beside v1 breaks the situation in the exact way §5.2 tabulates.

**Why not installed.** `cli.py` builds the situation menu that goes to a cloud
model from `shipped_situations(catalogue)`, and `_situations_of(schema_id)` hands
those names to the model at site G. Every label on a wired row crosses the
internet. Labels are the owner's vocabulary; and here wiring additionally means
replacing a shipped row, which is an edit no agent may make.

## 7. FIELD GAPS — the real constraint, and NOT a library question

Five of the seven gaps in §4 cannot be closed by any applicability row, because
the level has no field to bind. These are facts-layer vocabulary rulings and are
recorded here, **not proposed**:

| what `107` draws | field needed | state today |
| --- | --- | --- |
| Coursework: institution → **program** → term → course → work type | `program` | **does not exist.** Not `subject`, not `school`. |
| Photos: year → event → **rendition** (Originals / Selects / Edited / Exports) | `rendition` | **does not exist.** |
| Current work: employer → year → **project** → **stage** | `project`, `stage` at `career` | both exist elsewhere; **neither is referenced at `career`** |
| Health: year → **record type** | `record_type` at `medical` | `medical` is **field-less** by `facts.domains` §3.15 |
| Identity / Legal: **record kind** split | `record_type` at `identity`, `legal` | both **field-less** by the same ruling |

`identity`, `medical` and `legal` are field-less **by design** — `facts.domains`
names them "§3.15's three out-of-scope safety domains", and
`active_field_allowlist` deliberately contributes nothing for them so that "it
does not cause a field to be invented." Their zero in §2 is therefore **not an
authoring oversight in the template library. It is a downstream consequence of a
deliberate facts-layer ruling**, and no row written in `tree_design` reaches it.
That is the single most important correction in this document.

One structural note, already recorded in `production.py`: **125 of the
definitions' dimensions across the release have no binding at all** — a
definition is generic and each row binds the subset its situation uses. The
Teaching institution slot in §5.1 is one of those 125. Auditing the rest is a
larger piece of work than this one and is not attempted here.

## 8. RATIFICATION PACKET — seven questions, answerable in one sitting

**No name below is new.** Every situation id already ships in the recognition
release. `109` row 21 bolded `travel.trip-records` because it was a **minted**
name entering the `finance` menu; nothing here is minted, so nothing is bolded on
that ground. For completeness: **once wired, every situation name and every
folder label in a shipped row reaches the cloud model at site G** via
`shipped_situations` → `_situations_of`. That is true of the one label drafted in
question 1.

---

**1. `academic.teaching` — add the institution level?**
*Levels:* **School I taught at** → Semester I taught → Course I taught → Kind of
teaching material. (`school` → `term` → `subject` → `work_type`.)
*The one question:* `107` gives Teaching as *institution → term → course →
teaching function* and your tree draws the institution explicitly, but the
shipped row binds no institution. **Wiring this means REPLACING
`ap.academic.teaching@1`, not adding beside it** — §5.2 shows adding makes the
situation unresolvable while the menu silently keeps the old levels. Do you
authorise the replacement, and is **"School I taught at"** the label you want?
*(This is the only new vocabulary in this document.)*

**2. `medical.wearable-health-exports` — a home, or none?**
*Levels proposed:* none.
*The one question:* its ratified text refuses to turn any metric, device,
condition or date range into a folder level, and `107`'s Health leaves never name
a wearable export. Should it stay depth-less and fall to its protected home, or
do you want it filed under Long-Term Records as a durable category?

**3. `identity` (3 names) and `legal` (3 personal names) — an amendment-21-style
ruling, or stay depth-less?**
*Levels proposed:* none. *Names, unchanged:* `identity.core-documents`,
`identity.credentials-passwords`, `identity.immigration-visa`,
`legal.estate-planning`, `legal.leases-agreements`,
`legal.personal-legal-matters`.
*The one question:* `107` splits both branches by **record kind**, but all three
schemas are field-less by the §3.15 ruling and `record_type` is not referenced at
any of them, so today these seven situations can build **no folder at all**.
Amendment 21 made exactly this ruling for `medical`. Do you want the same for
`identity` and `legal` — and if so, is `record_type` the key, or a new one?

**4. `career.portfolio-work-samples` and `career.credentials-licenses` — leaves,
or split?**
*Levels proposed:* none.
*The one question:* `107` draws Career/Profile/Portfolio and
Memberships/Professional Associations as **leaves**, and your Memberships splits
by kind of body, which no field supplies. Do these stay flat, or do you want a
`record_type` split that is not the one your tree draws?

**5. `nonprofit.volunteering-and-club-life` — a home under Memberships?**
*Levels proposed:* none.
*The one question:* it maps to your Memberships/Clubs and Community, which is a
leaf. `institution` is bindable. Do you want a club-named level there, knowing
`107` draws none?

**6. Three coursework-shaped academic rows bind no term — bind it, or stay flat?**
*Names, unchanged:* `academic.continuing-education`, `academic.online-course`,
`academic.study-abroad`. *Level that would be added to each:* a term level
between the provider and the course (`term`, one label each).
*The one question:* all three use `def.subject-work-record`, whose `cycle_period`
slot is **optional at index 1 and unbound**, and `term` is live,
destination-eligible and declared at `academic` — the identical shape as question
1, with the same replace-not-add cost per row. `107`'s template table gives
Coursework a term level generically, but your tree draws none of these three
branches. Do you want the term bound on them, or do they stay flat because you
did not draw them?
*(`academic.standardized-testing` and `academic.transcripts-credentials` also
bind no term; they use different templates and `107` is silent on both, so they
are counted in §4's five and not asked about here.)*

**7. The five field gaps of §7 — which, if any, do you want ruled?**
`program` (Coursework), `rendition` (Photos), `project` and `stage` at `career`
(Current work), `record_type` at `medical` / `identity` / `legal`.
*The one question:* these are facts-layer vocabulary, not library rows, and each
is a closed-vocabulary addition only you can ratify. **`program` is the one that
most directly serves the owner's own corpus weight** — it is the missing level in
`107`'s deepest branch, and academic is the heaviest part of the corpus. Which do
you want opened, and in what order?

---

## 9. What this document did not do

* It did not open the corpus, and quotes no file, folder or course name.
* It did not mint a situation name, a schema, a life or a field.
* It did not fill in a branch where `107` is silent — §5.3 and §5.4 name those
  explicitly instead.
* It did not audit the other 124 unbound definition dimensions (§7).
* It did not edit any shipped library row, and the one change it proposes to a
  shipped row is question 1, not an action.
