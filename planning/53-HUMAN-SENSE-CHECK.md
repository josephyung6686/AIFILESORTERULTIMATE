# 53 — HUMAN-SENSE CHECK

**Status:** proposal for the owner. Nothing in `src/`, `planning/domains/*.json` or the template
records was touched.
**Question it answers:** would a real person, looking at the tree this design produces, recognise it
as *theirs* — and would they say these words out loud?
**Canonical authority:** `00-database-agent-product-design.md`. Where I disagree with anything else,
`00` wins; where I disagree with `00`, I say so and mark it as mine.

---

## 0. The finding, before the evidence

The design already knows that the same file means different things to different people. It says so
in `00` §5.1 — labels *"should reflect the user's vocabulary rather than a universal corporate
taxonomy"* — and it proves it at corpus scale: **175 of 358 researched rows carry a screenshot as a
file example**, and exactly one row is *about* screenshots.

What the design does **not** have is any of the three things needed to act on that knowledge:

| Missing thing | Where it should live | What it is today |
|---|---|---|
| **A place to store the human name of a dimension** | `TemplateDimension` / `canonical_fields.json` | Neither carries a display label. `TemplateDimension` (`src/tree_design/templates.py:231`) has `role_ref` and `retrieval_rationale` and nothing else; a canonical field row has `key`, a prose `role`, and `aliases`. **The key string IS the UI string.** |
| **A way to offer two different SHAPES, not two orders of one shape** | `TemplateDefinition.candidate_orders` | `_check_orders` (`templates.py:353-359`) requires every candidate order to cover *the same roles*. Ordering is the only axis the user may choose on. **Every persona split found in this pass is a split in the dimension SET or in DEPTH, not in order.** |
| **Any conditioning of template DEPTH on how much of the disk the material is** | `TemplateApplicability` | Nothing. A schema either has a recipe or it does not. This is the whole of the legal problem in §3. |

Six sharp findings follow. §6 is the one to read if you read one.

---

## 1. Six personas, drawn from the corpus

Each is a real reading of researched rows, not an invention. Filenames are quoted verbatim from
`file_examples`.

### P1 · The litigator — `law_practice.*` (37 rows), `legal`, `identity`, `finance.small-business-bookkeeping`

**On disk:** `Requests for Production of Documents - Set One - Hartley v Nash.docx` ·
`Privilege log - Tranche 3.xlsx` · `VOL003_load.dat` ·
`Index to trial bundle - Hartley v Nash - vol 2 of 4.pdf` ·
`XX plan - Lee - topics and bundle refs.docx` ·
`Screenshot 2026-06-11 at 09.14.02 - e-filing portal - submitted.png`
(`law_practice.discovery`, `.trial-preparation`, `.pleadings`).

**How they talk:** *"the Hartley file."* Everything is a matter. Never "documents", never "legal
docs" — **all of it is legal docs, so the word carries no information.** The words that carry
information are the matter name, the side (ours / theirs), the exercise (this demand set, this
tranche, this bundle volume), and the deadline. `law_practice.discovery`'s own template prose
independently reaches the same order: *"the MATTER, then the EXERCISE as a document-function level
…, then the PERIOD last."*

### P2 · The content creator — `creative.short-form-writing`, `.content-marketing`, `.podcast-episode`, `photos.screenshot-captures`, `photos.social-media-export`, `finance.receipts-expenses`

**On disk:** `S03E04 - Rivers and Resilience - episode brief.docx` ·
`S03E04_Rivers_Resilience_edit_v2.rpp` · `S03E04_Rivers_Resilience_master.mp3` ·
`2026-Q3 Editorial Calendar.xlsx` · `newsletter-2026-08-14.html` ·
`takeout-20260118T090000Z-001.zip` · several thousand `Screenshot 2026-… .png`.

**How they talk:** *"the Rivers episode"*, *"the Q3 stuff"*, *"my references"*, *"receipts."* The
unit is a **piece that ships**, and everything else is either raw material for one or clutter. This
persona is the one for whom "all my legal docs in one folder" is exactly right and completely
uninteresting — a lease, an LLC filing and a contributor agreement, three files, one folder, never
opened.

### P3 · The hardware engineer — `engineering.pcb-layout`, `.cad-model`, `.change-order`, `code.software-project`, `business_operations.meeting-record`

**On disk:** `A2409-CTRL_RevD.GTL` · `A2409-CTRL_RevD_Fab.zip` · `A2409-CTRL.kicad_pcb` ·
`A2409-CTRL_odb.tgz` · a repository root with `requirements.txt` beside `src/` and `tests/` ·
`IMG_5512.png (a screenshot of a stack trace from a project's test run)`.

**How they talk:** *"the A2409 board, Rev D."* The part number and the revision are the whole
address. A screenshot of a stack trace is **a bug report**, and it is worthless three weeks later —
this is the one persona for whom the word *temporary* is honest.

### P4 · The sole-trader builder — `construction_property.trade-job`, `.progress-photos`, `.quote-estimate`, `finance.small-business-bookkeeping`

**On disk:** signed work records with a job number and a customer address block; hundreds of
site photographs; supplier invoices; a quote and a final account per job.

**How they talk:** *"the Ashcroft Road job."* Address first, always. `51` §4.6 concedes this
persona's problem in its own human-sense note: *"a builder photographing job sites wants the **site**
first, not the year."* `construction_property.trade-job` describes the atom precisely: *"One piece
of work for one client at one address."*

### P5 · The student-researcher — `academic.coursework`, `college_applications`, `research.*`, `photos.camera-events`, `code.*`

**On disk:** `Syllabus BUSIB 4300 Spring 2026.pdf` · `HW 3.pdf` ·
`PHYS1401 Lecture 08 - Rotational Dynamics.pptx` · `problem set 4 - final version (2).docx`.

**How they talk:** *"PHYS1401"*, *"the Columbia application"*, *"my thesis."* This is `00`'s own
worked persona and it is the persona the launch set serves: **all six field-declaring schemas —
`academic`, `code`, `college_applications`, `finance`, `photos`, `research` (`51` §1.2) — are this
person's schemas.** Worth stating plainly: the product currently ships one persona's tree.

### P6 · The two-child household administrator — `academic.k12-schooling`, `applications.k12-admission`, `medical.dependant-child-health`, `finance.personal-records`, `legal.leases-agreements`, `photos.family-archive`

**On disk:** report cards, permission slips, enrolment forms, two admission packets in one season,
insurance schedules, a lease, a will, fifteen years of family photos.

**How they talk:** *"Ada's school stuff"*, *"the important documents drawer."* The child's name is
the organizing fact and the corpus knows it: `academic.k12-schooling`'s template prose —
*"The order this situation actually wants is child → school year → work type, and no declared field
names the child."*

---

## 2. Screenshots — the position

### The numbers first, because they settle the argument

| Measure | Count |
|---|---:|
| Node rows mentioning a screenshot at all | **288 / 358** |
| Node rows carrying a screenshot as a `file_example` | **175 / 358** |
| Screenshot file examples across the corpus | **194** |
| Of those, falling through to **`Temporary Screenshots`** | **159 (82%)** |
| Rows whose *subject* is screenshots | **1** (`photos.screenshot-captures`) |

**A screenshot is a member of nearly every domain and the property of none.** That is the owner's
insight, measured. The design's handling of it is right in one place and wrong in three.

### What the design gets right — briefly, then move on

`photos.screenshot-captures` leads on `media_type`, not on `event`, and its stated reason is
correct: *"event … is the fact a screenshot characteristically cannot supply."* The routing is
excellent: the Columbia-portal capture returns to the applications group, the receipt capture goes to
`Receipts and Confirmations`, the recipe capture goes to `Reference Clips`, the account-screen
capture goes to `Protected Records`, and the illegible one abstains. `00`'s controlled action set —
*"The model must be allowed to conclude that no meaningful association exists"* — is the right rule
and the corpus applies it uniformly. **None of the three failures below is a routing failure.**

### Failure A — two screenshot folders under one Photos parent, and nothing distinguishes them

- Domain template: `photos.screenshot-captures`, `launch: full`, order `media_type > capture_year`
  → **`Photos / Screenshots / 2026`**.
- Residual template: `RESIDUAL_DEFAULT_PARENTS[TEMPORARY_SCREENSHOTS]` (`vocabulary.py:273`)
  → **`Photos / Temporary Screenshots`**.

A user who activates `photos` and enables the residual gets both, side by side, and no string
anywhere tells them which one their screenshot went into. The distinction is real (one has an
accepted group, one does not) and it is **invisible in the only place the user looks**. `00`'s own
one-child warning — *"repeats a concept already expressed in the parent"* — arguably fires on the
pair.

### Failure B — `Temporary` is a claim the evidence never makes, and `00` supplies the better word twice

82% of every screenshot in the corpus lands under a folder whose name means *you may throw this
away*. Look at what actually lands there:

- `law_practice.pleadings` → `Screenshot … - e-filing portal - submitted.png`,
  `falls_through_if_inactive: Temporary Screenshots`. **That is a litigator's proof of timely
  filing.** Calling it temporary is not a naming quibble; it is an invitation to a malpractice claim.
- `business_operations.support-operations` → a captured error dialog beside a live case thread.
- `finance.receipts-expenses` → a captured order confirmation with a legible total.

`00` uses **both** names for this destination: *"Temporary Screenshots"* three times, and
**`Screenshot Inbox` twice** — *"send them to a Screenshot Inbox"* and *"either remain in place or
enter an approved Screenshot Inbox."* The implementation resolved that inconsistency silently, in
favour of the name that asserts something the evidence does not support.

> **Recommendation.** Ship the display name as **`Screenshot Inbox`**. It is `00`'s own word, it
> asserts only *undecided*, and an inbox is a thing people already know how to empty. The internal
> `template_name` constant can stay `TEMPORARY_SCREENSHOTS` — `residuals.py` already separates the
> fixed internal name from the authored `display_name` slot, so this costs one slot value, not a
> rename. The `default_parent_location` chain at `vocabulary.py:273` is a **display-label** chain and
> must change with it.

### Failure C — it is one flat pile per year, and the mechanism to fix that is deferred with no values

`ResidualTemplate` carries `optional_shallow_subfolders` and `max_permitted_depth` — the exact
escape hatch — but `residuals.py`'s own docstring says *"Their slot VALUES are deferred and arrive
injected … None is invented here."* Nothing in the corpus authors them. So at launch a creator with
4,000 screenshots gets one folder holding 2,300 files with a year on it.

### The position, stated

**Is `Screenshots` the `Important Screenshot` anti-pattern?** No, and the distinction matters. `00`
§7.2's four bad names — `Random PDF Things`, `Important Screenshot`, `Miscellaneous Documents`,
`Travel/Gate B12` — are bad because each **asserts a judgement the evidence cannot support**
(*important*, *random*, *miscellaneous*, *this gate identifies this trip*). `Screenshots` is a
`media_type` value backed by positive metadata evidence. It is a legitimate folder.

**But a folder is not the same as a destination anyone wants.** My position, per persona:

| Persona | Does a `Screenshots` folder serve them? |
|---|---|
| P3 engineer | **Yes, and it should expire.** A stack-trace grab is a bug report; `max_permitted_depth: 1` plus `00`'s *"show temporary screenshots older than 30 days"* review policy is exactly right. |
| P2 creator | **No.** Their screenshots are working reference material — `Reference Clips` is their real destination and `00` already names the learning path: *"If the user repeatedly places product screenshots into Reference Clips, the system records that as a user preference."* A `Screenshots` folder for this persona is a pile they never open. |
| P1 litigator, P4 builder | **No — actively harmful.** Their captures are evidence of an event (a filing, a site condition on a date). These belong beside the matter or the job, and when they cannot be placed there the honest answer is `Review Later`, **not** a folder named temporary. |
| P5 student, P6 household | **Yes, shallow, and mostly to be emptied.** The junk-drawer reading is correct for them and `00`'s time-aware lifecycle is the whole feature. |

So: **keep the folder, rename it, and make its lifecycle the product feature rather than its depth.**
The thing that makes a screenshot pile bearable is not sub-structure — it is that somebody asks you
about it thirty days later. That is `00`'s own answer and it is the part currently unbuilt.

---

## 3. Legal documents — same file type, opposite correct answer

### For P6 (household): yes, one folder. The product currently produces **none.**

`legal` is `launch: safety` and declares no fields, so it recommends no dimensions — correctly, per
its own row: *"activating it legitimises the universal facts only and unlocks protection rather than
a filing tree."* Its four templates (`legal.leases-agreements`, `.personal-legal-matters`,
`.estate-planning`, `.practice-matter-file`) all inherit that.

The consequence: **the household's lease, will and insurance dispute papers have no destination in
the main tree at all.** They land in the residual library, under **`Protected Records`** — a
residual whose `00` posture is *"or, more safely, represent without moving"* and *"should normally
remain local-only."*

That is a correct **protection** answer and a wrong **product** answer to the question the user
asked. They asked for a folder. They got a posture. And they got it under a name — `Protected
Records` — that no person has ever said out loud (§4).

### For P1 (lawyer): catastrophic, and the corpus already documents the exact tear

`law_practice.json`'s `also_holds_with[legal]` states the seam in its own words:

> *"One matter folder holds an intake screen, a time export and a review log (this schema, on the
> matter-and-role apparatus) beside a pleading, an order and an executed settlement (`legal`, on the
> caption and execution structure) — disjoint evidence, one corpus, and **both schemas fieldless** …
> `legal` is a safety domain, so where they co-activate the protective ordering runs first."*

**J-WIDE-1 fixes half of this and makes the other half worse.** It widens the thirteen professional
schemas, `law_practice` among them, so the apparatus gets a matter tree. `legal` is **not** one of
the thirteen and stays fieldless. Result after J-WIDE-1:

```
Matters/ Hartley v Nash/          ← law_practice: intake, engagement, time, review log
(nowhere)                         ← legal: the pleadings, the order, the executed settlement
```

The half with the tree is the administrivia. The half with no tree is **the case**. And because
protection runs first, the substantive half is not merely unplaced — it is actively held back from
placement.

### Is fieldless-`legal` right for both? No. It is right for one and inverted for the other.

| | Household (P6) | Litigator (P1) |
|---|---|---|
| Share of disk that is `legal` material | ~2% | ~80% |
| What "protect it" means | a useful filter over a thin seam | a blanket over the entire corpus |
| What one flat protected folder delivers | roughly what they asked for | nothing usable |
| Is `legal`'s no-fields ruling right? | **Yes** — depth here would be `Legal/Leases/Amendments/…` for four files, which is `00`'s tiny-folders warning | **No** — it is not a safety posture at this share, it is a refusal to organize the disk |

### What the product must do to get both right, and whether it can express it

**The discriminator is not the file type. It is the material's share of the corpus.** Two files of
protected material is a drawer; two thousand is a practice. The same schema must produce a shallow
protected folder in the first case and a deep matter tree in the second.

**The design cannot currently express that.** `TemplateApplicability` binds a definition to a schema
and a context; it carries no condition on corpus share, and `TemplateDefinition` has no shallow/deep
variant axis — `candidate_orders` varies order only (`templates.py:353`). Volume *is* visible at the
horizontal canvas (`00` §5.1: candidates show *"how many files appear to support it"*), and `00` §5.9
requires live structural feedback before a split. So the **information** exists at exactly the right
moment; nothing consumes it to choose between two recipes.

> **Recommendation.** This is the single highest-value structural change in this document, and it is
> smaller than it sounds: let a schema register **two definitions with a stated share threshold**, or
> — cheaper and more honest — make it the **first-run question**, in J-WIDE-2's exact shape:
> *"We found 2,140 legal documents. Is legal work what you do, or are these your own records?"*
> One question, asked before the user has seen their tree, that flips `legal` between a protected
> drawer and the parent of a matter tree. `00` licenses the question form directly: *"The user can
> drag an accepted group into a top-level branch … or delete a suggested top-level area entirely."*

---

## 4. The name-out-loud test

**The test:** would a person say this word to another person to describe where something is?

**Why this is not cosmetic.** There is nowhere in the product to store a human name for a dimension.
`TemplateDimension` (`templates.py:231-236`) holds `role_ref` and `retrieval_rationale` — no label.
`DimensionOrder` (`templates.py:248-264`) holds `order_id` and `rationale` — no label. A
`canonical_fields.json` row holds `key`, a prose `role`, and `aliases` — no label. **When the canvas
asks "organize this branch by what?", the string it has is the key.** So these names ship.

### 4a. Canonical field keys that become folder levels

| Key | Verdict | What a person says |
|---|---|---|
| `school`, `term`, `subject`, `project`, `client`, `institution`, `event`, `location`, `venue`, `lab`, `repository`, `purpose`, `tax_year` | **PASS** | These are already the words. Nothing to do. |
| `target_university` | PASS | "the schools I applied to" — long, but unambiguous, and the role separation it encodes is `00`'s own. |
| `application_cycle`, `application_document_type` | BORDERLINE | People say *"the 2026 round"* and *"essays / transcripts / recs"*. The keys are precise and clunky; they are also scoped to one schema where the applicant does think in those terms. **Leave.** |
| `work_type` | PASS | "homework, exams, labs". A student says *"what kind of work"*. |
| `record_type` | BORDERLINE-PASS | "what kind of record". Survives because `finance`'s values (*statements, receipts, notices*) are what people say. |
| `media_type` | **FAIL as a picker label** | Nobody says "media type". They say **"photos or screenshots"**. The *values* pass; the key does not. |
| `account_type` | PASS | People say "checking, savings, brokerage". |
| **`artifact_type`** | **FAIL** | Nobody has ever said *"it's in the artifact type folder."* A researcher says **"what kind of thing it is"** — figures, data, drafts, protocols. `51`'s role rename to `artifact_kind` does not help; *artifact* is the failing word, not *type*. Proposed: **`work_kind`** (aligning it with `work_type`, which already passes). |
| `capture_year` | PASS | "the year I took them". |

### 4b. The 15-role vocabulary (`51` §2) — internal, but it leaks

Roles never become facts and never become folder labels. They *do* become the strings a dimension
picker has. On that basis:

- **PASS:** `place`, `subject_anchor`(borderline), `capture_time`, `capture_kind`(borderline).
- **FAIL, all of them:** `holder_institution`, `addressed_org`, `issuing_org`, `account_kind`,
  `scope_period`, `occasion_anchor`, `lifecycle_stage`, `repository_instance`, `purpose_anchor`,
  `artifact_kind`, `cycle_period`.

Nobody says *"occasion anchor."* They say **"what it was"**. Nobody says *"holder institution."*
They say **"my school"** or **"my lab"** — and note that the right word is *different per schema*,
which is the point: the role is a cross-schema abstraction and it must never be shown. The three-way
separation `holder_institution` / `addressed_org` / `issuing_org` is **correct and must be kept** —
`00`: *"The system must separate roles that happen to contain the same entity type"* — but the user
should see *"my school"*, *"where I applied"*, *"who issued it"*.

> **Recommendation.** Add one field to `TemplateDimension`: a per-binding `display_label`, authored on
> the **applicability** row (which knows the schema) rather than on the role (which does not). This is
> a smaller amendment than `51` JC 1's privacy field and it is the prerequisite for every other naming
> fix in this document.

### 4c. The four newly proposed keys

| Proposed | Verdict | Recommendation |
|---|---|---|
| **`record_period`** (47 §3.1) | **FAIL** | Nobody says *"it's in the record period folder."* `47` §3.4 argues it wins because *"it asserts the least"* — but "record" carries **zero** information in a product where every file is a record, which `47` §3.5 itself concedes. `47` then declines its own better name on a corpus-hygiene ground (no row minted it). That is a reason about the corpus, not about the user. **Take `covered_period`.** A person genuinely says *"what period does this cover"*, and it is the exact sentence `47` §2.1c says all 23 rows converged on. This is the one place I recommend overturning an adjudication's stated conclusion in favour of the same document's stated alternative. |
| **`subject_of_record`** (49 §1.7) | **FAIL, cheaply** | Nobody says this. It is `destination_eligible: false`, so it never becomes a folder — the failure is confined to the fact/search panel, where it is still bad. A person says **"who it's about."** Propose **`about_person`**: it says the thing, it is what nine refused synonyms (`patient`, `deponent`, `beneficiary`, `student`, `decedent`…) all mean, and it **avoids the adjacency hazard `49` §2.5 records and declines to resolve** — `subject` (the course) sitting next to `subject_of_record` (the human) on the `academic` schema. `49` calls that *"a readability cost"*; it is a readability cost that a different spelling removes for free. |
| **`product`** (49 §1.5) | **PASS for two worlds, FAIL for one** | A manufacturer and a shopkeeper both say "product". Nobody in mining says a product folder holds *overburden* and *waste rock* — `49` names this strain itself and calls the merge *"the least confident … in this document."* Endorse the fallback `retail_hospitality` proposed: narrow `product` to goods and dishes, leave `resource_operations` its own key, ship neither as a roster-wide synonym. |
| **`asset`** (49 §1.2) | **PASS** | A plant engineer, a fleet manager and a utility all genuinely say "the asset register". It is scoped to the schemas that proposed it. Nothing to change. |
| **`matter_anchor`** (role, `42`/`50`) | **PASS internally, FAIL if shown** | A lawyer says *"matter"*; a builder says *"job"*; a consultant says *"engagement"*; a creative says *"project"*. `49` routes all four to canonical `project`, which is right for facts and wrong for the picker — a litigator told *"organize by project"* will assume the product has misunderstood their work. Same fix as 4b: label per applicability row. |

### 4d. The nine residual folder names (`vocabulary.py:246-254`) — the worst-performing set in the product

| Shipped name | Verdict | What a person says |
|---|---|---|
| `Review Later` | **PASS** | Best name in the set. |
| `Receipts and Confirmations` | **PASS** | Exactly what people call it. |
| `Reading Inbox` | **PASS** | Recognisable; "Read Later" is more common but this is fine. |
| `Reference Clips` | **BORDERLINE** | A designer says "clips" or "refs". P1 and P6 do not. Consider **`Saved References`**. |
| `Temporary Screenshots` | **FAIL** | → **`Screenshot Inbox`**, `00`'s own alternative (§2). |
| `One-Off Images` | **FAIL** | Nobody says "one-off image". → **`Loose Pictures`**, or fold into the screenshot inbox — its 2 corpus fallthroughs against `Temporary Screenshots`' 159 do not justify a separate folder. |
| `Independent Records` | **FAIL** | Nobody says this, in any of the six personas. It is the second-most-used residual for P1 and P3. → **`Standalone Documents`** or, closer to speech, **`Odds and Ends`** — which sounds unserious and is exactly what the folder is. |
| `Unsupported or Encrypted` | **FAIL** | Two engineering words joined by a disjunction. → **`Can't Open These`**. |
| `Protected Records` | **FAIL, and it is the costly one** | This is where P6's legal documents go (§3) and where P1's witness statements go. A household says **"Important Documents"**; nobody says "protected records". |

**The cross-cutting failure:** a lawyer's default residual set reads
`Personal / Independent Records`, `Photos / Temporary Screenshots`, `Protected Records`,
`Reading Inbox`. Every one of those is a consumer word, and two of them (`Personal/`, `Photos/`) put
professional work under a personal parent. `RESIDUAL_DEFAULT_PARENTS` (`vocabulary.py:272-277`) hard-
codes `Photos` and `Personal` as the parents of the first four. **For four of six personas, the
residual library's default shape is wrong before a single file is placed.**

### 4e. One place the design already got this right — noted briefly

`00` §5.1's nine example top-level names (*Academics, Applications, … Media or Miscellaneous Personal
Material*) are illustrative, and `tests/p10/test_p10_candidates.py:122` **asserts they are absent
from the source**, with candidates derived only from the user's own accepted groups and labels. That
is exactly right, it is enforced by a test, and it is the single best piece of persona hygiene in the
codebase. (For the record: `Media or Miscellaneous Personal Material` is the worst name in the entire
corpus and it is good that it ships nowhere.)

---

## 5. Where one tree cannot serve two personas — and the product must ASK

### The structural finding that governs this whole section

`candidate_orders` is the ratified ask-the-user mechanism (J-WIDE-2 precedent: career ships both of
`00`'s orders and asks on first run). It can only vary **order**:

> `templates.py:353-359` — *"candidate orders must cover the same roles. An order that drops or adds
> a role is a different RECIPE, and offering it as an ordering choice would let the user silently
> change what the branch organizes by."*

That rule is correct. But **every persona split in this pass is a split in the dimension set or in
depth — not in order.** The one mechanism the design has for asking is pointed at the one axis where
personas differ least. Six places need an ask and cannot currently get one:

| # | The split | Personas | Currently | Can `candidate_orders` express it? |
|---|---|---|---|---|
| **A** | Screenshots: main-tree `Photos/Screenshots/<year>` vs residual inbox vs leave-in-place | P3 vs P2 vs P1/P4 | `photos.screenshot-captures` is `launch: full`, so screenshots enter the **main tree at freeze**. `00`'s screenshot question (§7.6) — *"leave them in place, review them with AI …, send them to a Screenshot Inbox, or create a custom branch?"* — is a **P11 residual-surfacing** question, asked **after**. Two answers to one question, at two different times, and the earlier one is not asked at all. | **No** — different destinations, not different orders. |
| **B** | `legal`: protected drawer vs matter tree | P6 vs P1 | Frozen to drawer for both (§3). | **No** — different depth. |
| **C** | `subject_of_record` eligibility | P6 (child's name as a folder: right) vs P1/clinician (third party's name as a folder: unacceptable) | `49` §2.4 seeds FALSE + a NEEDS-JOSEPH widening; `48` §7 flags that `canonical_fields.json` **has no per-schema `destination_eligible`** at all. Narrowing is legal via `metadata_only`; **widening is impossible**. | **No** — it is an eligibility flag, not an order. And the only person who knows whether the subject is their own child or someone else's client is the user. |
| **D** | Photos: year-first vs event-first vs **site-first** | P5/P6 vs P2 vs P4 | D21 ships two orders — **this one is right and is the pattern working.** But `51` §4.6's own note concedes the builder wants `site_anchor` first, a **third role**. | **Partly.** The two shipped orders are correct; the builder's case needs a role the recipe does not contain, so it is a different recipe. |
| **E** | The freelancer's proposal PDF | P2/P4 vs a company | `business_operations.partnerships-bd` states it perfectly: *"for a freelancer, a consultant or a sole trader they are one activity with two vocabularies, and the same proposal PDF is a bid on Monday and a job application on Tuesday. Putting a person's freelance pitches under a business-operations branch, or their company's proposals under a career branch, would both be wrong for somebody."* Resolved silently by a schema boundary. | **No** — it is a schema-selection question, one level above templates. |
| **F** | `Photos/Scans` — does it exist? | P6 (scans ARE the filing cabinet) vs P3 (noise) | `51` JC 5(e), deferred: *"the answer changes where several hundred of someone's real files live."* | **No** — it is a branch-exists question. |

**A and B are the two the owner named.** Both need an ask. Neither has one.

> **Recommendation.** Two changes, in order of value:
> 1. **Move `00`'s screenshot question earlier.** It already exists, verbatim, in `00` §7.6. It is
>    currently asked in the residual workflow, after the tree is frozen. Ask it during tree design,
>    before `photos.screenshot-captures` commits a main-tree branch. **This costs nothing new — it is
>    a sequencing fix to a question the design already wrote.**
> 2. **Generalise J-WIDE-2 from "two orders" to "two recipes".** The precedent the owner already
>    ratified is the right pattern; the record shape is what limits it to ordering. Either add a
>    sibling to `candidate_orders` that may vary the role set, or let a schema register two
>    definitions with a first-run question attached. B, D(builder) and F all resolve with the same
>    amendment.

---

## 6. The honest failure list

Places where a real person opens the tree and immediately rearranges it. Ordered by how many
personas they hurt.

**F1 · A lawyer's matter file is torn in half at freeze, and the half with no destination is the
case.** §3. `law_practice` gets a tree under J-WIDE-1; `legal` does not and is not in the thirteen;
protection runs first. Pleadings, orders and executed settlements — the substance — are held back
from placement while the intake screen and the time export get filed. The corpus documents the seam
in `law_practice.json`'s own `also_holds_with[legal]` and nobody has ruled on the consequence.

**F2 · 82% of every screenshot in the corpus is routed to a folder whose name means "disposable",
including a litigator's proof of filing and a support engineer's incident evidence.** §2, Failure B.
159 of 194 screenshot fallthroughs. `00` supplies the better name (`Screenshot Inbox`) twice and the
implementation took the other one.

**F3 · Four of the nine residual folder names are words no person says, and two of them are hard-
coded under `Photos/` and `Personal/` parents that are wrong for every professional persona.**
§4d, `vocabulary.py:246-277`. `Independent Records` and `Protected Records` between them absorb most
of what P1, P3 and P4 cannot place, under names drawn from a consumer product neither of them is
using.

**F4 · There is no field anywhere in the record shape to hold the human name of a dimension, so the
engine's internal vocabulary is the shipped UI vocabulary.** §4b. `TemplateDimension:231`,
`DimensionOrder:248`, `canonical_fields.json`. Eleven of the fifteen launch roles fail the say-it-
out-loud test. This is the cheapest fix in the document and it gates every other naming fix.

**F5 · A two-child household cannot keep two children's records apart, and the corpus has said so
four separate times.** `academic.k12-schooling` (*"no declared field names the child"*),
`.homeschool`, `.iep-accommodation-plans`, `applications.k12-admission` (*"every one of this
template's high-weight signals … can be identical across the two"*). `49` §2.4 recommends the fix and
correctly refuses to apply it unilaterally, because the same key is unacceptable for a clinician.
**This is not a preference; it is a sorting failure**, and it will be the first thing P6 notices.

**F6 · The product ships one persona's tree and it is `00`'s own author's.** All six field-declaring
schemas at launch (`51` §1.2) are P5's schemas: academic, code, college applications, finance,
photos, research. **278 of 335 template rows are gated** behind schemas with no live fields. J-WIDE-1
reverses the freeze, and the sequencing it implies — career, then creative, law_practice,
construction_property, manufacturing — is right. Until it lands, five of the six personas in this
document get a residual library and nothing else. Worth stating plainly rather than discovering at
first user test.

**F7 · `candidate_orders` requires every multi-dimension recipe to offer at least two orders
(`templates.py:361`), and `51` JC 3 admits ten of them were authored by an agent because the corpus
attests only one.** The interface will present ten invented alternatives beside orders that rows
argued from real corpora, with no way for the user to tell which is which — while the splits that
*are* attested (§5 A–F) cannot be offered at all. The mechanism is over-applied where evidence is
thin and unavailable where evidence is strong.

---

## 7. What I would put to the owner, in one place

1. **Rename `Temporary Screenshots` → `Screenshot Inbox`** in the authored `display_name` slot and in
   `RESIDUAL_DEFAULT_PARENTS`. `00`'s own word, twice. Cost: one slot value.
2. **Move `00` §7.6's screenshot question from the residual workflow into tree design**, before
   `photos.screenshot-captures` commits a main-tree branch. Cost: sequencing.
3. **Add a `display_label` to the dimension binding**, authored on the applicability row. Unblocks
   every other naming fix. Cost: one field on one record.
4. **Rename `record_period` → `covered_period`** — `47`'s own §3.5 alternative — and
   `subject_of_record` → `about_person`, which also removes the `subject` adjacency hazard `49` §2.5
   records and declines to resolve.
5. **Rename four residual folders**: `Protected Records` → *Important Documents*,
   `Independent Records` → *Standalone Documents*, `Unsupported or Encrypted` → *Can't Open These*,
   `One-Off Images` → fold into the screenshot inbox.
6. **Answer the legal question with a first-run question, in J-WIDE-2's shape**, and generalise that
   pattern from "two orders" to "two recipes". This is the largest item and the one that decides
   whether the product serves anyone but P5.

**What I did not do:** touch `src/`, any `planning/domains/*.json`, or any template record. Every
recommendation above is a proposal.
