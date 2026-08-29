# Template decision brief

Date: 2026-08-27 · For: Joseph · **6 decisions, all pre-filled. Say yes, or change one.**

Approving this brief ships nothing (§8). It writes nothing into `planning/domains/`, `src/`, or
`tools/`, and opens no gate.

Built on [`37-TEMPLATE-REUSE-INVENTORY.md`](37-TEMPLATE-REUSE-INVENTORY.md) ·
governed by [`domains/TEMPLATE-BUILDING-HANDOFF.md`](domains/TEMPLATE-BUILDING-HANDOFF.md) ·
`00-database-agent-product-design.md` wins on conflict.

> **Audit note added 2026-08-27 22:30.** This brief was written before
> [`42-REUSE-FULL-CORPUS-CHECK.md`](42-REUSE-FULL-CORPUS-CHECK.md) and
> [`44-SAMPLING-AUDIT.md`](44-SAMPLING-AUDIT.md) existed, and it cited neither. **Two statements in
> §3 (Decision 2) have since been refuted** and now carry inline corrections — read those before
> answering Decision 2. Everything else stands: the catalogue closed at 358/358 rows on 2026-08-27
> and the number this brief rests on, **54 bindable template rows across the same 6 field-declaring
> schemas, did not move** — so Decisions 1, 3, 4, 5 and 6 are now permanent rather than provisional.

Every number and quotation below came from a command I ran against `planning/domains/nodes/*.json`.
Nothing is quoted from memory.

---

## 1. What you are approving

The first wave of the folder-template library: **3 shared recipes, 24 template definitions, 54 bindings**,
covering the six domains that can actually produce folders today — photos, research, academics,
applications, finance, code. The other 17 domains have no fields yet and are wave 2.

Your six decisions, in order:

| | Decision | Where |
|---|---|---|
| **1** | The names of your top-level folders — `Academics` vs `School` vs `Uni` | §2.1 |
| **2** | The words the canvas uses inside a branch — `Course` vs `Class` | §2.2 |
| **3** | Three shared recipes — accept all, or cut one | §3 |
| **4** | The **default** order for 7 folder families (the user switches at runtime) | §4 |
| **5** | The bindings — one glance, then it's mine | §5 |
| **6** | Which checks refuse outright vs warn and let you override | §6 |

Everything else is mechanical and mine (§7). 38 of the 54 rows wrote a question naming you personally;
this brief exists so you answer 6 instead of 38.

> **The launch evidence has not moved.** The research swarm has landed 17 more rows since the inventory
> froze (329 complete now, up from 312). Recomputed against the current files, the set of rows that can
> produce a folder today is still **exactly 54** — same rows, same orders, nothing changed. It cannot
> grow: no unfinished row sits on any of the six domains.

---

## 2. Decision 1 — the folder names you'll actually see

**Recommendation: pick one wording per row below. Ignore §2.2 entirely — that's plumbing.**

00 §5.1 makes this yours:

> *"The exact labels should reflect the user's vocabulary rather than a universal corporate taxonomy."*

You said a mix of both. So the middle column is 00's own systematic wording and the right columns are
shorter, more personal. **Mix freely — pick per row.**

### 2.1 Your top-level folders — THE DECISION

| Domain | 00's wording (systematic) | Shorter | Yours? |
|---|---|---|---|
| academic | **Academics** | `School` | `Uni` |
| college_applications | **Applications** | `Admissions` | `College Apps` |
| research | **Research** | `Lab` | `Projects` |
| finance | **Finance and Administration** | `Finance` | `Money` |
| photos | **Photos and Captures** | `Photos` | `Pictures` |
| code | **Code and Projects** | `Code` | `Dev` |

**My pick: the middle column for `Academics`, `Applications`, `Research`; the short column for
`Finance`, `Photos`, `Code`.** The three long ones are long for no reason once the folder exists.

`Career`, `Personal Records` and `Media or Miscellaneous Personal Material` are also on 00's list but
have no fields yet — wave 2, nothing to decide.

### 2.2 The words inside a branch — also yours, lower stakes

These are what the canvas says when it offers you a split ("branch first by …"):

| Inside | 00's words | Shorter |
|---|---|---|
| Academics | School · Term · **Course** · Work type | School · Semester · Class · Type |
| Applications | Target institution · Admissions cycle · Document type | University · Season · Document |
| Research | Project · Stage · Artifact type | Project · Status · Kind |
| Finance | Institution · Account type · Record type | Bank · Account · Kind |
| Photos | Year · Event · Media type | Year · Occasion · Kind |
| Code | Project · Repository · Artifact type | Project · Repo · Kind |

**My pick: 00's words.** They are already the ones the design writes to the user, and "Course" is a live
example of why the split in §2.3 matters — the underlying field is called `subject`, but
`academic.coursework` records that the user-facing word is 00's: *"(stored as subject under D6; course is
00's prose)"*.

### 2.3 Role names — internal plumbing, **you do not need to approve these**

Listed only so you can see there is no hidden taxonomy. These never appear on screen and never become
folder names. Folder names are always real values out of your files — `Columbia`, `BUSIB 4300`, `Chase`.

`artifact_kind` (40 uses) · `subject_anchor` (17) · `issuing_org` (13) · `holder_institution` (8) ·
`cycle_period` (8) · `capture_time` (8) · `addressed_org` (6) · `occasion_anchor` (6) · `account_kind` (5)
· `lifecycle_stage` (4) · `capture_kind` (3) · `scope_period` (2) · `purpose_anchor` (1) · `place` (1) ·
`repository_instance` (1)

Only one thing about them is a real rule rather than a naming choice, and 00 states it:

> *"The system must separate roles that happen to contain the same entity type."*

That is why the school **you attend**, the university you **apply to**, and the bank a statement **comes
from** are three different things and can never be merged, even though all three are "an organization."
`finance.insurance-corporate` puts it bluntly: *"a certificate holder must never fill institution, and a
carrier must never fill client."*

> Verified: all 22 folder levels in use map to exactly one of those 15 roles; every one resolves to a
> real field its own domain declares. Unmapped levels: **0**.

---

## 3. Decision 2 — the three shared recipes

**Recommendation: accept all three. The evidence picks them, not me — and there is no fourth.**

> ⚠️ **CORRECTION added 2026-08-27 22:30 by the catalogue audit — read before answering Decision 2.**
> **"There is no fourth" is false**, and this brief was written before the evidence existed. It was
> computed over the 54 bound rows only. [`42-REUSE-FULL-CORPUS-CHECK.md`](42-REUSE-FULL-CORPUS-CHECK.md) §0
> ran the same test over the full corpus and found a fourth recipe that is **bigger than all three**:
> `matter_anchor > artifact_kind` ("the case then the kind"), **55 rows across 11 domains, zero
> counter-examples**. It is invisible here because the role it needs does not exist in the 15-role
> vocabulary this brief uses. [`44-SAMPLING-AUDIT.md`](44-SAMPLING-AUDIT.md):139 grades the claim
> **OVERSTATED**.
>
> **This does not change the recommendation — accept all three.** The fourth recipe cannot bind at
> launch (it needs a role that does not yet exist), so the launch wave is still exactly these three.
> What changes is that "there is no fourth" must not be read as settled; it is a wave-2 question.

A "shared recipe" is a piece of folder logic reused across domains, written once. The bar: it must show
up in **two or more different domains**. I counted every adjacent pair of folder levels across all 54
rows. Exactly three clear that bar:

| Recipe | In plain English | Rows | Domains |
|---|---|---:|---|
| **1. Subject then kind** | the project-or-course folder always sits above the what-kind-of-thing folder | **14** | academics, research, code |
| **2. My institution first** | an **optional** folder for the school or lab *you* belong to, on top | 4 | academics, research |
| **3. Term then kind** | an **optional** term-or-season folder above the what-kind-of-thing folder | 4 | academics, applications |

```
Recipe 1   Academics/Columbia/Spring 2026/BUSIB 4300/Syllabus
           Research/Chen Lab/PVA-RDP/manuscript
           Code/graphify/notebook            <- same recipe, three domains, no shared data
```

Every other pattern in the corpus lives in **one** domain only, including the biggest one
(finance's `Chase/checking/statement`, 8 rows) — that is just the finance recipe, not a shared thing.

**The case against each, honestly.** Recipe 1: research and code use literally the same two underlying
fields, so you could argue it spans two domains, not three — still passes, but by less than it looks.
Recipe 2 is the weakest: only 4 rows, 3 of them academic. ~~**If you want one cut, cut Recipe 2**~~ — the cost
is writing the same thing twice instead of once, and nothing else.

> ⚠️ **CORRECTION added 2026-08-27 22:30 by the catalogue audit — do NOT cut Recipe 2.**
> The "only 4 rows, 3 of them academic" count is an artefact of this brief's 6-domain sample, not a
> property of Recipe 2. [`42-REUSE-FULL-CORPUS-CHECK.md`](42-REUSE-FULL-CORPUS-CHECK.md) §0 re-ran it
> over the full corpus: **11 rows across 5 domains, zero counter-examples** — it was mis-flagged as
> weakest only because five of the domains that use it were not in the sample. 42's verdict is
> literally *"Do not cut it."*, confirmed as a defect in this brief at
> [`44-SAMPLING-AUDIT.md`](44-SAMPLING-AUDIT.md) §1.1.
>
> The sentence above is struck rather than deleted, so the reasoning that produced it stays visible. Recipe 3 merges an academic *term* with
an admissions *season*, which are not quite the same kind of time.

**What got rejected, so you can see the bar is real.** The most tempting near-miss had *better* numbers
than Recipes 2 and 3 — merging "the bank a record came from" with "the university you applied to" into one
"organization" level: **10 rows, 2 domains**. Refused, because it is 00's forbidden merge, and split
correctly it collapses to 8 finance rows and 2 applications rows — both single-domain. The whole
cross-domain claim was an illusion created by the merge. Two more went the same way (`repository` vs
`account_type` — a named thing vs a category; and finance's own 11-row default, which is just finance's
template wearing a costume).

**All three recipes originally proposed in the handoff were refuted by the actual rows.** One is realized
by **zero** rows; two by **one** row each. That is the bar working.

---

## 4. Decision 3 — the default order (the user picks the rest at runtime)

**This changed. You are no longer picking one order per family — you are picking the default.**

Each template will carry **2–3 candidate orders**, and the user chooses per branch when they open it.
That is what 00 already requires: §5.3 says the user decides *"whether its internal structure should
separate schools, terms, courses, work types, or some combination"*, and §5.5 shows three options side by
side with real branch counts. §5.8 requires uneven depth on top of that. A single baked-in order fights
both.

**So the only thing you decide here is which option is pre-selected.** Seven families, seven picks —
all pre-filled with my recommendation in bold.

---

**A · Academics** — 6 rows

```
DEFAULT  Academics/Columbia/Spring 2026/BUSIB 4300/Syllabus
Option B Academics/BUSIB 4300/Spring 2026/Syllabus
Option C Academics/Columbia/BUSIB 4300/
```
All three are 00 §5.5's own options. Default A because a course code repeats every term and the term is
what keeps two enrolments apart; 00 names B's risk: *"Option B would merge material across schools when
course codes collide."* C is there for people with few files.

---

**B · Research work** — 2 rows · **the one place the design contradicts itself**

```
DEFAULT  Research/PVA-RDP/manuscript/under review
Option B Research/PVA-RDP/under review/manuscript      <- this is what 00 §5.4 says
Option C Research/PVA-RDP/manuscript
```

> **Zero landed rows** produce 00's order. Where both levels appear, kind sits above stage, 2 out of 2.

Both rows explain why. `research.dataset-analysis`: *"one dataset keeps all of those forms while its
stage moves … Putting stage above artifact_type therefore splits one dataset's raw table from the cleaned
table derived from it."* `research.thesis-dissertation`: *"putting stage on top interleaves a chapter
draft with a defense deck under one Revision folder."* **Default the flip, keep 00's order as Option B.**
Worth knowing: the creative domain's prose backs 00's original order, but creative has zero fields and
cannot vote yet — so this may reopen in wave 2.

---

**C · Research manuscripts** — 1 row · **the row says this one is yours**

```
DEFAULT  Research/PVA-RDP/under review
Option B Research/PVA-RDP/Nature Methods/under review
```
`research.manuscript-publication` verbatim: *"The fork decides a real folder structure and is Joseph's."*
**Default flat**, because the row states its own trap: *"a researcher whose manuscripts each go to one
journal gets a one-child level, which is precisely what 00 asks the canvas to warn about."* This is the
one place I override the landed row.

---

**D · Applications** — 4 rows

```
DEFAULT  Applications/UChicago/Fall 2026/supplemental essay
Option B Applications/Fall 2026/supplemental essay/UChicago
Option C Applications/UChicago/supplemental essay
```
Both A and B are landed and both are right for different people, which is why they must both ship —
00: *"the product should not assume that all applications are best organized in the same way."* B is for
scholarship season: *"one applicant addresses many sponsors in one season, most of them receiving one
essay and one form"* — A there gives you a shelf of one-file folders. C drops the season for the mirror
reason (K-12: one entry year, several schools).

---

**E · Photos** — 9 rows

```
DEFAULT  Photos/2026/Japan Trip 2025
Option B Photos/Japan Trip 2025/2026
Option C Photos/Japan Trip 2025
```
00 licenses year-first for photos specifically: *"time often belongs first because capture date is a
defining aspect of the material."* But look at the default path — the year is in the folder name *and* the
trip name. `travel.trip-photos` flags exactly that and drops the year level. **Default A, but B and C
matter more here than anywhere else.** Scanned prints need B outright:
`photos.family-archive` — *"a capture_year level at the top would collect prints under the year somebody
digitized them."* Scans and screenshots get their own default, `Photos/screenshot/2026`.

---

**F · Finance** — 18 rows, the biggest family

```
DEFAULT  Finance/Chase/checking/statement
Option B Finance/statement/Chase
Option C Finance/2025/statement
```
A wins 12 rows to 1. B is for working books — *"a general ledger, invoice register, expense report or
receivables report refers to many banks and counterparties."* C is for tax filings only, and it is the
one place outside photos where time goes first; the row argues it and flags itself as inference:
*"it cannot scatter a filing, because the filing IS the year. That reasoning is mine, not 00's."*

---

**G · Code** — 3 rows

```
DEFAULT  Code/graphify/notebook
Option B Code/graphify/
```
Default A, **except** a curated notes vault, which is pinned flat and should stay that way —
`code.pkm-vault`: *"One dimension, deliberately"*, because 00 says *"Existing folders must not be
automatically flattened, renamed, or reorganized simply because a template would produce a different
structure."*

---

### 4.1 This needs a P10 plan change — flagging, not making it

The runtime record cannot carry more than one order today. Verified:

- `docs/superpowers/plans/2026-08-25-p10-tree-design-freeze.md:3702` — `class TemplateDefinition` has
  `dimensions: tuple[TemplateDimension, ...]`, a single ordered list.
- `:3685` — `class TemplateDimension` has `order_index: int`, one integer position per level.
- `:3737` — a validator **rejects** two levels sharing a position, with this message:
  *"two dimensions claim one order_index; the recommended order must be one order, even though the user
  may reverse or flatten it"* — and `:5104`
  `test_two_dimensions_claiming_one_order_index_are_rejected` locks it in.
- `:3710` — `optional_branch_patterns` is `tuple[str, ...]`, free text. It cannot hold an order.

**The good news is that half the work is already there.** The P10 SPEC already requires the side-by-side
preview — *"that Option A 'would create three schools, five terms, and twelve course branches'; that
Option B 'would merge material across schools when course codes collide'"* (`SPEC.md:626`) — and the user
edit vocabulary already includes `reordered`. What's missing is that today's alternatives exist only as a
free-form drag, not as 2–3 authored, named, previewable options.

**Required amendment:** `TemplateDefinition` carries a list of candidate orderings (one flagged default),
each a permutation of the same levels, with the uniqueness check applied *within* each ordering instead of
across the record. **Another agent owns that plan — I have not touched it.**

---

## 5. Decision 4 — the bindings

**Recommendation: glance at the two facts below, then approve. I own all 54 rows.**

**Fact 1 — the reuse mechanism works, but exactly one template uses it at launch.** Of 24 templates, one
serves three domains at once:

```
                    "subject then kind" template
                              |
        +---------------------+---------------------+
        |                     |                     |
   Academics             Research                Code
   subject -> subject    subject -> project     subject -> project
   kind    -> work_type  kind    -> artifact    kind    -> artifact
   6 rows                3 rows                 1 row

   Academics/Columbia/Spring 2026/BUSIB 4300/Syllabus
   Research/Chen Lab/PVA-RDP/manuscript
   Code/graphify/notebook
```

Three domains, one recipe, **zero shared data** — the academics binding physically cannot read a research
field and vice versa. The recipes spread wider than the templates do: "subject then kind" is used by four
different templates, which is why it covers 14 rows while its biggest template covers 10.

The other 23 templates each serve one domain. Per domain: finance 7 templates / 18 rows · photos 4 / 9 ·
academics 4 / 11 · research 5 / 8 · applications 3 / 5 · code 3 / 3. **Total 54.**

**Fact 2 — nothing is missing today, but five things will be.**

> Verified: across all 54 bindings, folder levels with no real field behind them: **0**. Nothing needs a
> field invented.

Five places where a level *could* be wanted and there is no field for it. All are latent, none blocks
launch, and none may be fixed by inventing a field:

| | Gap | Effect |
|---|---|---|
| 1 | code has no "my institution" | the optional top folder can't be offered for code |
| 2 | research and code have no "term" | the optional term folder can't be offered there |
| 3 | applications declares your own school but deliberately forbids it as a folder | permanent, and correct — *"never a folder level for this domain"* |
| 4 | photos has no "kind of document" | Recipe 1 can never reach photos |
| **5** | **research has no time field** | **this one changes a real folder name** |

Gap 5 is worth ten seconds: conference folders will read `ASCB 2026` as a single name rather than
`ASCB/2026`, because the year has to live inside the venue's name. The row asks you directly: *"does a
conference occurrence stay a venue value, or does the Research schema owe a time field?"* Minting a field
here is forbidden outright, so this is a schema question, not a template one. **OPEN.**

---

## 6. Decision 5 — what refuses vs what warns

**Recommendation: confirm the pre-filled column. Twelve checks refuse; two warn and let you override.**

Plain English, one line each. The rule I applied: **privacy and correctness refuse. Tidiness advises.**

| Check | The stupid outcome it prevents | **My call** |
|---|---|---|
| C1 | a folder plan pointing at a recipe that no longer exists | **Refuse** |
| C2 | a folder level no file can ever fill — a `Term` folder when nothing knows its term | **Refuse** |
| C3 | running your bank statements through the coursework recipe because both mention a school | **Refuse** |
| C4 | the system quietly guessing when two different schools could both fill one level | **Refuse** — show you the choice |
| C5 | a folder ending up inside itself, or an order that can't physically be built | **Refuse** |
| C6 | files silently vanishing from the preview instead of showing up as leftovers | **Refuse** |
| C7 | a sensitive file landing somewhere less protected than where it started | **Refuse — never overridable** |
| C8 | anything touching real folders before you said yes to that specific branch | **Refuse — never overridable** |
| V1 | `Academics/Columbia/Columbia` | **Refuse** |
| **V2** | **a folder that would hold exactly one thing** | **Warn — you can override** |
| **V3** | **burying files five levels deep** | **Warn — you can override** |
| V4 | one folder becoming the dumping ground for everything one person or company produced | **Refuse** |
| V5 | a folder name leaking a diagnosis or an account number | **Refuse — never overridable** |
| V6 | empty folders getting created | **Refuse** |

**Two things worth knowing.**

First, **none of C1–C8 is a tidiness check** — they are all correctness, privacy, or consent, and the
design already decided they fail closed: *"Conflict handling is fail-closed and explanatory … There is no
hidden precedence rule."* The override you asked for genuinely lives in V2 and V3.

Second, **00 contradicts itself on exactly V2 and V3**, which is why they are the ones to relax:

> §5.7 calls them validation: *"The engine **validates** that the proposed template does not … create
> meaningless one-child levels, exceed practical depth limits …"*

> §5.9 calls them warnings: *"It should **warn** when a level produces only one child … creates excessive
> depth …"*

Same concepts, once as a refusal and once as a warning. Warn-and-allow resolves it in your favour: you
should be able to say *"yes, I really do want a one-file folder."* Also, V3 has no number behind it
anywhere — the P10 spec marks the depth limit *"open question"* — so refusing on it today would be
refusing on a threshold nobody has set.

"Fail closed" must never mean "dead end." For C3–C6 the refusal has to name the way out, and the spec
already lists them: *"omit one fragment, change the order, flatten a level, keep the branch shallow, or
defer."*

---

## 7. What I own — no decision needed

1. Which of the 54 rows attaches to which of the 24 templates, and every level-to-field mapping.
2. Recipe IDs, versioning, and import rules.
3. Which templates use which recipes, and which levels stay local to one template.
4. Evidence, exclusions and provenance on every binding, back to the ratified research rows.
5. Depth variants — a row that drops a level while keeping the same relative order is a variant, not a new
   template. That rule alone is what keeps 54 rows at 24 templates instead of 31.
6. The compiler, its output records, and the wording of every failure report.
7. Exclusions: currently 40 refused rows, 2 partial, 27 unfinished. Verified closed — no unfinished row
   sits on any of the six live domains, so no future research can add a folder to this wave.
8. Wave-2 arithmetic: 266 kept rows + 29 owed − ~4 expected refusals ≈ **291** against 00's *"roughly
   200–300"*. Recipes should reach ~5–10 at full size, not ~50 — the three found are the general ones and
   the long tail is domain-specific.
9. The privacy split that forces two templates where the shape is identical: `academic.teaching` *"routinely
   holds other people's data"*, `academic.coursework` *"holds the holder's own record and should not
   accumulate other people's."* Same recipe, opposite exposure, two templates. Mechanical once stated.

---

## 8. Approving this ships nothing — four things must land first

| | Blocker | Verified status | Whose |
|---|---|---|---|
| **1** | **P10 doesn't exist.** It is the thing that compiles and checks all of this. | `src/` has no tree-design module at all. The one template file, `src/llm_harness/template_validation.py`, is P8's shape check and says so: *"P10 owns template design quality. P8 does not invent or score a hierarchy."* | build P10 |
| **2** | **The safety flag is missing on 3 of the 4 safety domains.** No privacy floor can be computed without it. | `finance.json` **ABSENT** · `identity.json` **ABSENT** · `medical.json` **ABSENT** · `legal.json` `true`. Finance *asserts* the status in prose — *"Consequences carried by the safety flag, not invented here"* — but the flag it names is not set. A compiler reading these files today would treat finance as an ordinary domain. | R1c / the domain gate — **not fixable from here**, another session owns those files |
| **3** | **212 of 266 rows have no field to attach to.** 17 of 23 domains declare zero fields. | Not patchable by inventing fields — the contract says *"Do not invent fields to make the gate green."* `creative.3d-asset`: *"The creative schema declares no field rows, so no folder dimensions are legal at launch."* | R1c / you |
| **4** | **Career is empty**, and career is 00's own example of one of the rejected recipes. | `career.json` declares 0 fields. Its own note: *"EMPTY BY CONTRACT, not by refusal … a dimension may only branch on a field the schema declares, and this placeholder declares none."* The contract: *"Career is owed before P10, where a destination dimension first needs one."* | **you, explicitly** |

Plus the P10 plan amendment in §4.1, and the research swarm finishing (every number here is a snapshot).

---

## OPEN — things the evidence genuinely does not settle

| | Question | What would settle it |
|---|---|---|
| O1 | Applications: addressee first or season first? Attested **1 for 1**. | Nothing. Both rows are right for different people — **shipping both as options is the answer**, not a compromise. |
| O2 | Research: project first or venue first? Attested **1 for 1**. | Same. Both ship. |
| O3 | Conference folders: `ASCB 2026` or `ASCB/2026`? | You, or R1c granting research a time field. Inventing one here is forbidden. |
| O4 | Do shared recipes carry their own privacy floor, or does that live on the domain? | Blocked behind blocker 2. My working answer: the domain, not the recipe — otherwise one recipe spanning a public reading list and a file of other people's grades must either over-restrict or under-restrict one of them. |
| O5 | How deep is too deep (V3)? | Nobody has set a number. The P10 spec marks it *"open question."* |
| O6 | When a domain and a situation state the same recipe, which one owns it? | `academic.coursework`: *"two rows now state one recommendation … R1c or Joseph decides which row owns it."* If the domain owns it, two of my rejections become contract decisions rather than my judgment. |
| O7 | Does `purpose` stay applications-only? | Decides whether the purpose-packet template generalizes in wave 2. |
| O8 | Photo run crossing 31 December — does the year level yield to the event? | 00 gives no sentence. Recommend the canvas decides per branch rather than baking it in. |

---

## Appendix — reproduction

```bash
cd "/Users/jy/GRAPH AGENT"

# the 54 rows that can produce a folder today, and their orders
python3 -c "
import json,os
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'; f=set(os.listdir(N))
ids=[n['domain_id'] for n in r['nodes'] if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
rows=[json.load(open(N+i+'.json')) for i in ids]
live=[d for d in rows if d['kind']=='template' and not d.get('refuse_node') and d['template'].get('dimension_order')]
print(len(live))
for v in sorted(live,key=lambda x:(x['schema_id'],x['id'])):
    print(v['id'],' > '.join(v['template']['dimension_order']))"

# every folder level maps to a real, folder-eligible field
python3 -c "
import json,os
sch={s:{x['field']:x['destination_eligible'] for x in json.load(open('planning/domains/nodes/%s.json'%s))['fields']}
     for s in ['academic','research','photos','college_applications','finance','code']}
N='planning/domains/nodes/'; bad=[]
for fn in os.listdir(N):
    if not fn.endswith('.json'): continue
    d=json.load(open(N+fn))
    if d.get('kind')!='template' or d.get('refuse_node'): continue
    for t in d['template'].get('dimension_order') or []:
        if not sch.get(d['schema_id'],{}).get(t): bad.append((d['id'],t))
print('violations:',len(bad))"

# the missing safety flag
for s in finance identity medical legal; do
  python3 -c "import json;print('$s',json.load(open('planning/domains/nodes/$s.json')).get('is_safety_domain','ABSENT'))"
done

# the P10 record that can only hold one order
grep -n "class TemplateDefinition" -A 12 docs/superpowers/plans/2026-08-25-p10-tree-design-freeze.md
sed -n '3737,3742p' docs/superpowers/plans/2026-08-25-p10-tree-design-freeze.md
```
