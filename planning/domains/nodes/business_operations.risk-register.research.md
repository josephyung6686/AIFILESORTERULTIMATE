# business_operations.risk-register — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the gist-era draft. The gist verdict on the node test is
**confirmed, not reversed** — but only after the spreadsheet-shape charge and the artefact-of-a-parent
charge are argued out in full, and the confirmation is worth exactly as much as those arguments. Two
gist-era judgements **are** reversed and are named as reversals below: the decision to leave
`business_operations.support-operations` and `business_operations.policy-handbook` unedged (both of
those rows already name this one, so the catalogue was asymmetric), and the decision to route the
committee risk paper as a pure collision when it is a genuine co-activation.

`launch: "placeholder"`, `fields: []`. `proposed_fields` seconds two existing family proposals and
mints nothing.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the source of truth. Every `“…”` span in the JSON
  and in this memo was machine-matched against it after writing, verbatim.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`
  (§2 node test, §4 activation — step 2 never-alone is load-bearing here), `CONNECTION-EXAMPLES.md`.
- `planning/domains/canonical_fields.json` — read before proposing anything, and the reason this row
  proposes nothing new.
- `planning/domains/roster.json` — every `collides_with.domain` and `also_holds_with.domain` in the
  JSON was re-checked against it after the deepening edits. All exist.
- `src/evidence_shape/vocabulary.py` — every `source_type` in the JSON is in `SOURCE_TYPES`.
- `planning/domains/ROSTER.md` Appendix A lines 816–817 — the absorbed legacy ids.

### The schema anchor, read first and read as binding

`business_operations.research.md` (46KB) states the family's default template and a family-wide rule.
Three of its rulings govern this file:

1. **The default template a sibling must differ from** — *"the **organisational unit or entity**
   *only where the corpus genuinely spans more than one* → the **governance body, project, contract,
   or account** the material belongs to → the **fiscal period** → the **document function**. Not
   time-first."*
2. **The never-alone principle, generalised for all 24 siblings** — *"No sibling may rest its
   activation on an entity name, a business vocabulary word, or a document shape alone."* Each of the
   three is never-alone; *"Every detection signal a sibling writes must pair a **structure** with a
   **labelled slot**."*
3. **The function-words-are-values rule**, which the anchor calls the single most important sentence
   in its memo for sibling authors — and which **names this row by name** as an example of a row that
   earns its node on structure: what earns such a row its node is *"a distinct **structure** — a
   tender evaluation matrix, an asset register with serials and lifecycle dates, a risk register with
   likelihood/impact scoring columns — not the topic word."*

Being named there is a licence to argue, not a verdict. The anchor is describing the *shape* that
could earn a node; whether *this* row's shape survives contact with its neighbours is the work below.

### Siblings and neighbours read before writing

- `business_operations.organisational-records.json` — read **first**, on the dispatch's instruction
  that this row might be heading the same way. It is not, and the section below says exactly where.
- `business_operations.it-asset-inventory.research.md` — read for its handling of the identical
  spreadsheet-shape charge. Its argument is adopted, with one divergence stated openly.
- `business_operations.compliance-audit.json` — being deepened in parallel. It already names this row
  and the boundary here is written to agree with it. **Not edited.**
- `business_operations.project-delivery.research.md` / `.json`, `.strategy-plan.research.md`,
  `.retrospective-postmortem.json`, `.vendor-management.json`, `.support-operations.json`,
  `.policy-handbook.json`, `.board-governance.json`.

---

## What it is for, and what it holds

An organisation keeps a written list of what could go wrong, who owns each item, what is being done
about it, and when it will next be looked at — and, because of that list, keeps plans for the things
it cannot prevent. The row holds risk registers and scoring worksheets, appetite and tolerance
statements, heat maps and committee risk papers, business impact analyses, continuity and
disaster-recovery plans, crisis procedures and call trees, and continuity test and exercise reports.

**The anchor is a living register with no end date.** That sentence does all the work, and every
boundary below is a corollary of it.

---

## The node test, argued leg by leg

CONNECTION §2: a **template** row exists only if its detection signals, recommended dimensions, or
privacy rules differ from its schema's default template. Three legs, argued separately, because two
pass on real evidence and one **cannot pass at all** — and saying which is which is the point of
running the test rather than announcing a verdict.

### The hostile reading, stated first

The dispatch levels three charges, and they compound. I take the `it-asset-inventory` memo's method —
state the hostile case at full strength before answering it — and I take its charges in the order
that hurts most.

**(a) The spreadsheet-shape charge.** A risk register is a table of numbered rows with an owner, a
score and a date. That is a *document format*, not a filing world. Every one of its candidate signals
— the word *risk*, an organisation name, a table — is individually never-alone under the anchor's
rule and under `00`'s own sentence, *"A university name alone should not create a group because
Columbia can appear as an authoring school, course provider, target institution, employer, research
venue, or merely a cited organization."* CONNECTION §2 forbids a schema per file format; a row whose
whole support is "it is a table" is a row about `.xlsx`.

**(b) The artefact-of-a-parent charge.** The register is plausibly a *component* of
`project-delivery` (where it is the R in the RAID log) or of `compliance-audit` (where findings
become risks). A component of a bounded situation is not its own situation.

**(c) The version-family charge.** The register is reissued monthly. `policy-handbook` established
that reissue cannot earn a row: version family is a universal fact — `00` lists *"file type, creation
date, language, duplicate family, version family, and sensitivity status"* as the shared set every
file may carry — so arguing a row from revision behaviour is arguing it from something every file
already has.

Charge (c) is **conceded outright and not answered**, because it is correct. Nothing below rests on
reissue, revision, or a version token. The `never_alone` list carries a version-token entry so that
the concession is machine-readable rather than a promise in prose, and the one place the living-
document property *is* used — the argument against a period-first tree — is a claim about **dimension
order**, not about activation, and is stated as such.

Charges (a) and (b) are answered, and answering them is the substance of legs 1 and 3.

### Leg 1 — detection signals. **Passes, and this is the strong leg.**

The anchor's rule does not forbid a structure; it forbids an **unpaired** one. Four signal shapes,
each pairing a structure with a labelled slot, none of them a topic word and none of them the
schema's default template:

1. **The scored-row header.** A header row carrying a risk identifier and a description *together
   with* a likelihood or probability column and a *separate* impact or consequence column, beside an
   owner and a treatment and a next-review date. The pairing matters more than any single column:
   likelihood and impact as **two adjacent labelled columns beside a remedy** is close to unique in
   the whole catalogue. `00` licenses reading it — *"Tables matter because resumes, forms,
   applications, invoices, and administrative documents often place their most useful information in
   cells rather than body paragraphs."* This is the structure the anchor named by name.
2. **The inherent-versus-residual pair.** The same risk scored *twice*, in adjacent column groups,
   before and after controls. This is the strongest signal this row has and it is worth isolating,
   because it is the one shape **no** neighbour produces: a RAID log scores once, a findings tracker
   rates a severity once, an FMEA multiplies three factors into one number once. Scoring the same
   object twice against a control is a claim about *treatment effectiveness*, and only a managed
   register makes it.
3. **The appetite or tolerance statement.** Prose or a small table declaring how much of a named risk
   category the organisation is *willing to accept*. It has no analogue anywhere else in the family —
   a project does not declare an appetite, an auditor does not, an insurer states an excess instead.
   It is also the cleanest evidence of the **standing scope** that discriminates this row from (b).
4. **The continuity structure.** A critical activity or process paired with a recovery time
   objective and a recovery point objective, a dependency list and an invocation procedure — and its
   dated cousin, the exercise report with a scenario, a participant list, an observation log and an
   improvement-actions table.

**Answering charge (a) mechanically.** The `it-asset-inventory` memo proposed a good test and I adopt
it: *could this row's detection signals fire on a file that names no organisation?* For
`organisational-records`, no — nothing would be left. For this row, **yes**: a workbook whose header
reads `Risk ID | Description | Inherent L | Inherent I | Controls | Residual L | Residual I | Owner |
Next review` names no entity anywhere and fires cleanly on structure alone. That asymmetry is the
whole difference between a node and a label.

**Where I diverge from `it-asset-inventory`, explicitly.** That row answers the spreadsheet charge by
pointing at *identity* columns — serial, asset tag, hostname — which are proper nouns of a kind. This
row has no equivalent: a risk has no serial number, and `Risk 07` is a bare ordinal that `00`
forbids as sole proof. So this row cannot borrow that answer and does not try to. Its structure is
**relational rather than identifying**: two graded columns and a remedy, describing a relation
between a hazard and a response. That is a weaker kind of evidence than a serial, and I would rather
say so than overclaim. The consequence is written into the JSON as a discipline, not as a caveat: the
row leans on the *pair* (leg-1 signal 2) rather than on any single column, and the `never_alone` list
disqualifies each column individually.

### Leg 2 — recommended dimensions. **Cannot pass, and does not need to.**

`template.dimension_order` is `[]` and must be: `business_operations` declares **no field rows**
(PR-6, D1's deferral as narrowed, `_CONTRACT` rules 10 and 15), and a dimension naming an undeclared
field opens a tree level no fact could fill. This leg is **structurally unavailable to all 24
siblings**, not failed by this one. §2 requires signals *or* dimensions *or* privacy rules to differ,
so the row is entitled to pass on the other two. Worth stating plainly: a sibling on this schema that
claims a dimension difference is claiming something the contract forbids it to have.

Held as prose, for the pass that may license fields, and **differing from the anchor's paragraph in
one specific place**: the natural anchor is the organisational unit or entity whose register it is,
then the **document function** — register, analysis, plan, test — with the review period **last**.
The anchor's second level is *governance body / project / contract / account*, and a standing
register has none of those four: it belongs to the entity, not to a body or a project, and that is
precisely the property that answers charge (b). The parent-context rule is `00`'s — *"The
recommendation should follow the practical rule that a parent dimension should provide the context
required to understand the child."* — and a continuity test report is unintelligible before the
reader knows which plan it exercised.

Emphatically **not time-first**, and the reason is sharper here than anywhere else in the family: the
register is *one artefact re-saved*, so a period-first tree would shatter a single version family
across calendar folders. `00`: *"For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar folders."*
The anchor forbids any sibling here from claiming the time-first exception, which is granted to
capture-based media only. This row does not claim it. Note the discipline against charge (c): the
living-document property is used **only** here, as a dimension-order argument, and never as an
activation signal.

### Leg 3 — privacy rules. **Passes, and it is stricter than the family default.**

The anchor's family-level privacy argument is that *the exposed party is usually not the user* — a
third party appearing as a counterparty or in an appendix. This row has that property and two more
that the family does not:

- **Adversarial self-disclosure.** A risk register is an organisation's own candid written statement
  of where it is weakest, and a continuity plan is that statement joined to the procedure for
  operating while it is being exploited. This is not "documents can be sensitive"; it is a harm shape
  where the *content itself* is the hazard, distinct from the third-party exposure the family
  describes. The nearest analogue in the catalogue is `it-asset-inventory`'s network diagram, and
  this row's version is broader: the register enumerates weaknesses across every function at once.
- **The call-tree appendix.** In almost every real continuity plan there is an appendix of named
  staff with personal mobile numbers and home addresses. That is not an edge case; it is a
  structural feature of the document type, which puts it inside the corpus `00` describes — material
  that *"can include identity documents, account statements, tax records, medical information, legal
  records, credentials, private correspondence, GPS metadata, employment materials, and educational
  records."* Personal contact details for named individuals warrant the transition `00` requires:
  *"A scanned passport, tax statement, medical document, authentication key, or account record should
  enter a protected state immediately."*

The operative limits are `00`'s: *"Protected material should not be included in cloud-model prompts
by default, should not display raw content in general group summaries, and should not be moved
automatically without a user policy that explicitly permits it."* And because a branch named after a
risk theme **discloses the theme** — a folder called *Insolvency risk* is a disclosure before anyone
opens it — the redaction hook applies: *"Protected branches should have configurable redaction in the
canvas and review screens."* Concretely, the recommendation is that a register be summarised **by
structure** (a scored table of N rows across M categories) rather than by contents, that no risk
description and no call-tree name reach a cloud prompt or a general group summary, and that this row
never acquire automatic internal depth named after risk themes.

The row assigns only the catalogue value `potentially_sensitive`, carries **no** `is_safety_domain`,
and authors **no** P7 handling class.

### Overall

**Stands, on legs 1 and 3.** Leg 2 is structurally unavailable to the whole family. Charge (c) is
conceded and load-bears nothing. Charge (a) fails against the paired structure; charge (b) fails
against standing scope, argued next.

---

## Why this row is not `organisational-records`

Read first, as instructed. That row's hint described material carrying an organisation name and a
document type but no more specific sub-domain — which is not a situation but **the absence of one**,
and the absence of a situation already has homes (the schema's own default template, and Independent
Records).

This row fails that description at the only point that matters. Its support is not "an organisation
name plus a document-type word"; it is a specific paired header structure that can be described
without naming any organisation, and a P4 extractor could evaluate it on a file whose entity is
unknown. Where the refusal's candidate evidence *evaporates* when you subtract the entity name, this
row's does not.

There is a second, less obvious inheritance from that refusal, and it constrains this row rather than
excusing it: *"keeping a row to preserve a legacy id is the 574's mistake."* This row absorbs **two**
legacy ids, which doubles the temptation to keep it for bookkeeping reasons. The fold of
`ops.business-continuity` is therefore defended on its own merits below and not on the ground that it
had an id.

---

## Answering charge (b): why this is not an artefact of `project-delivery` or `compliance-audit`

This is the charge the gist memo answered thinly, and it deserves the space.

**Against `project-delivery`.** A project's RAID log genuinely contains this row's structure — that
is why `RAID log.xlsx` is the primary collision fixture and why both rows name the same bytes. What
separates them is not shape at all; it is **lifespan and scope**, and both are readable from the
file. A RAID log carries a project name in the header, sheets for Assumptions, Issues and
Dependencies beside the Risks sheet, and it *ends*: it has a closure date, because the project does.
A corporate register has an enterprise or unit scope, an appetite statement the project cannot make,
an inherent-versus-residual pair the project log does not carry, and a review cadence with **no end
date**. The claim "the register is a component of the project" inverts the containment: an
organisation that runs no projects at all still keeps a register, because the register exists to
outlive whatever created its entries. `project-delivery`'s own file states this discriminator from
its side in the same terms, and this row does not contradict it.

**Against `compliance-audit`.** Here the parent claim is stronger and I want to be careful, because
`compliance-audit` is being deepened in parallel and already names this row. Its statement of the
boundary — *"an inherent-and-residual rating pair with a likelihood and impact scale supports the
risk register; a finding raised by an identified assessment, with a severity and a corrective action,
supports this row"* — is adopted here verbatim in substance, stated from this side, and **not
diverged from**. The reciprocal in one sentence each way: *this row must not take* the audit's own
apparatus — a finding keyed to an identified assessment, a control reference from an external
standard, an auditor, an assurance opinion, a corrective action with a management response; *that row
must not take* the management-owned standing register, its appetite statement, or its inherent/
residual pair, **even when an audit requested the register as evidence.** Being cited as evidence
does not transfer ownership — a point `it-asset-inventory` makes for the same neighbour, and it is
right. The direction of travel matters too: audit findings *become* register entries, which means the
register is downstream of the audit rather than inside it, and a downstream artefact with its own
lifespan is not a component.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. The tempting false positives, and what
discriminates each.

| File | Why it is **not** this row's evidence |
|---|---|
| `RAID log.xlsx` (**kept as the primary collision fixture**) | The full register shape, one bounded project. Discriminator: project name in the header, Assumptions/Issues/Dependencies sheets, a closure date. `business_operations.project-delivery`, which names the same bytes from its side. |
| `Fire risk assessment - Unit 4.pdf` (**kept as the second fixture, and the file that must not be lost TO this row**) | Called a risk assessment outright, with hazard/persons-at-risk/controls/further-action columns. Discriminator: a **statutory duty-of-care frame** — an assessor competence statement, a premises and floor reference, a regulator-facing form layout. `hr.workplace-health-safety`. Reading it as corporate risk would file a statutory record in a management branch. |
| An **FMEA worksheet** (`FMEA - pump assembly rev C.xlsx`) — **added in this pass, and the most instructive rejection** | Severity, Occurrence and Detection columns multiplied into a Risk Priority Number, plus a recommended action and an owner. It is *more* numerically risk-shaped than a corporate register and it is not this row. Discriminators: the object scored is a **part or a process step**, not an organisational exposure; the arithmetic is a three-factor product rather than a likelihood×impact pair; there is a design or process revision anchor. `engineering.risk-analysis-fmea`. A new `collides_with` entry was added for it. |
| An **information-security risk treatment plan** | Risks paired with controls, often with residual ratings — the closest thing to a true tie. Discriminator: **control identifiers drawn from an external standard** and a statement of applicability. Left as a `compliance-audit` signal rather than a third JSON fixture, deliberately: it teaches the same lesson the audit boundary already teaches. |
| A **findings and corrective-actions tracker** | Same table, different header. Discriminator: each row traces to an *identified assessment* and carries a severity and a management response, not a likelihood-and-impact pair. `compliance-audit`. |
| A **lessons-learned register** | The identical accumulate-forever, one-row-per-entry, owner-and-status shape. Discriminator is **tense**: an entry describing something that already happened supports `retrospective-postmortem`; something that might happen, with a treatment, supports this row. That row states it from its side. |
| A **supplier risk questionnaire** | One row per *supplier* with diligence answers and a derived rating. Discriminator: the **unit of the row** — an organisation with a relationship owner is `vendor-management`; a risk with a treatment and an internal owner is this row. |
| An **insurance renewal submission** | Restates the organisation's risk profile and continuity arrangements in the insurer's vocabulary. Discriminator: a policy number, a premium, a schedule of cover, an underwriter counterparty. `finance.insurance-corporate`. |
| An **incident report** (`manufacturing.hse-incident`, `clinical_practice.malpractice-incident`) | A realised harm with a date, an injured party and an investigation. A register entry is a *possibility*; an incident report is an event. Left unedged — see the non-edges section. |
| An **on-call rota or escalation matrix** | Genuinely filed by both support and continuity, often in one document. Discriminator: severity-to-response commitments for *routine service* is `support-operations`; a recovery time objective and a critical-activity analysis is this row. That row already names this one; an edge was added back — see the reversals. |
| A **risk management policy or framework** | The governing document *about* how risks are managed, as opposed to the register itself. Discriminator: a controlled-document header — reference, version, approver, review owner. `policy-handbook`, which names this row already. Edge added back. |
| An **emergency plan for a public authority** | A flood or major-incident plan, structurally identical to a corporate continuity plan. Discriminator: a **statutory duty** and a public-body issuing letterhead, and a plan addressed to the public rather than to staff. `government.emergency-management`. New edge added. |
| A **project or strategy pack's risk appendix** | A slide of top risks inside a strategy document. Discriminator: it has no standing scope of its own — it is a *snapshot quoted into* another artefact. `strategy-plan`; new edge added, because the same slide deck is genuinely contested. |
| A **heat-map-shaped image** with no register nearby | A coloured grid with axes is also drawn for prioritisation matrices, effort-value plots and skills matrices. A grid alone activates nothing; `never_alone` says so. **One-Off Images**. |
| A **blank risk assessment template** | Fires every structural signal with every slot empty. It is a `work_type`, not a register, and it must never produce an owner fact or an organisation fact. **Independent Records**. |
| A **screenshot of a risk dashboard** | OCR yields scored rows and no header semantics. **Temporary Screenshots** unless an accepted register group is around it. |

---

## The collision fixture, in both directions

**Direction one — a file that would wrongly fire this row: `RAID log.xlsx`.** Every lexical and
structural signal fires: likelihood, impact, owner, mitigation, review date, a numbered risk
identifier. **What discriminates:** the bounded scope on the file itself — a project name in the
header row, the three sibling sheets, a closure date. What emphatically does **not** discriminate:
the word *risk*, the presence of scoring columns, the file extension, or the folder it sits in.

**Direction two — a file that must not be lost *to* this row: `Fire risk assessment - Unit 4.pdf`.**
Here the risk runs the other way. If this row is allowed to read "a table of hazards with likelihood
and control columns" as sufficient, it swallows statutory health-and-safety records whole — records
that belong to a duty-of-care regime with its own retention and its own regulator. **The
discriminating evidence is the frame, not the table**: an assessor competence statement, persons at
risk, a premises. `hr.workplace-health-safety` owns it; this row's fixture says so in
`must_not_conclude`.

**The bytes both neighbours must name.** Two cases, and they are different in kind:

- *A contest:* a workbook containing an enterprise register sheet **and** a project RAID sheet. One
  file, two scopes, and only one can be the anchor. This is where the `never_alone` discipline earns
  its keep — neither row may claim the other's sheet, and the honest outcome is **Review Later** until
  the user decides.
- *Not a contest:* `Risk paper - Audit Committee May.pptx`. The register content and the committee
  anchor are **both genuinely present and disjoint**, which is `00`'s co-activation case rather than a
  collision. This is one of the two gist judgements reversed in this pass; see below.

---

## Reciprocal boundaries, both directions

Every neighbour's own file was read before its boundary was written. Where a neighbour does not name
this row, that is stated rather than assumed.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| **`business_operations.project-delivery`** (gist, **names this row**) | the bounded log — a project name in the header, Assumptions/Issues/Dependencies sheets, a closure date | the standing register, its appetite statement, and its inherent/residual pair | `RAID log.xlsx`, named identically from both sides |
| **`business_operations.compliance-audit`** (being deepened, **names this row**) | findings keyed to an identified assessment, control references from an external standard, auditor correspondence, assurance opinions | the management-owned register, even when the audit **requested it as evidence** — citation is not ownership | a register attached to an ISO or SOC evidence pack |
| **`hr.workplace-health-safety`** (roster) | the statutory duty-of-care frame: assessor competence, persons at risk, premises, regulator-facing form | an enterprise category set with an appetite statement | `Fire risk assessment - Unit 4.pdf`. **One-way — that row does not name `business_operations`; R1c owes the reciprocal** |
| **`business_operations.retrospective-postmortem`** (gist, **names this row**) | an entry about something that already happened, with a causal analysis and a recommendation | an entry about something that might happen, with a likelihood, an impact and a treatment | a lessons register; and `DR test report - March.docx`, where the discriminator is that the event was **deliberate and scheduled** |
| **`business_operations.vendor-management`** (gist, **names this row**) | the supplier relationship — onboarding, diligence, scorecards, exit records | one row per **risk** with a treatment and an internal owner | `Supplier risk questionnaire - responses.xlsx` |
| **`business_operations.board-governance`** (gist) | the meeting apparatus — notice, agenda, pack pagination, minutes | the register table and its supporting analysis | `Risk paper - Audit Committee May.pptx`. **Now `also_holds_with` as well as `collides_with`** — see the reversals. One-way; R1c owes the reciprocal |
| **`business_operations.support-operations`** (gist, **names this row — and this row did not name it back**) | severity-to-response commitments for routine service, ticket and case anchors, on-call rotas run for service levels | a recovery time objective, a critical-activity analysis, a continuity invocation or test | an escalation matrix serving both. **Edge added in this pass** |
| **`business_operations.policy-handbook`** (gist, **names this row — and this row did not name it back**) | the governing framework document with a controlled-document header — reference, version, approver | a document whose working content is a register, however policy-shaped its cover page | `Risk management framework v3.pdf`. **Edge added in this pass**, adopting that row's own wording |
| **`business_operations.strategy-plan`** (gist) | the strategy narrative, objectives, options analysis | a standing register quoted into a strategy pack as a snapshot appendix | a board strategy deck with a top-risks slide. **One-way; R1c owes the reciprocal** |
| **`finance.insurance-corporate`** (roster) | policy numbers, premiums, schedules of cover, underwriter correspondence | the internally owned register with treatments and review dates | a renewal submission restating the risk profile. **One-way** |
| **`engineering.risk-analysis-fmea`** (roster, not yet written) | a part or process step scored on severity × occurrence × detection into an RPN, against a design revision | an organisational exposure scored on likelihood × impact with a treatment owner | an FMEA filed in a corporate quality pack. **Written here for that row's author to write against** |
| **`government.emergency-management`** (roster, not yet written) | a statutory emergency duty, a public-body issuing authority, a plan addressed to the public | a private organisation's continuity plan for its own operations | a resilience forum plan naming a company as a participant. **One-way** |
| **`manufacturing.safety-case`** (roster) | a safety argument submitted to a regulator for a hazardous facility | a corporate register | left **unedged** — see below |

---

## The gist judgements I am reversing

Stated explicitly rather than changed quietly, per the addendum.

**1. `support-operations` and `policy-handbook` were left unedged, and both of those rows name this
one.** The gist memo did not consider them at all. That is not a judgement I disagree with so much as
a gap: the catalogue was **asymmetric in the wrong direction**, with two siblings pointing here and
nothing pointing back. Both edges are now written, adopting each neighbour's own wording so that the
pair reads consistently. The `policy-handbook` seam is the sharper of the two and its discriminator is
worth stating once more: *a framework is about how risks are managed; a register is the management
itself.*

**2. The committee risk paper was treated as a pure collision. It is a co-activation.** The gist JSON
recorded `Risk paper - Audit Committee May.pptx` only under `collides_with: board-governance`, with
`must_not_conclude` saying P10 chooses later. On a closer reading that is the wrong edge type. `00`'s
collision case is *the same evidence confusing two rows*; the co-activation case is a file legally
carrying **both** schemas on **disjoint** evidence. Here the committee footer and the register table
are two independent structures in one file, and neither is being mistaken for the other. The
`collides_with` entry is **kept** — because the *narrative* risk paper with no register table in it
really is contested — and an `also_holds_with` is added for the disjoint case. Same reasoning as
`it-asset-inventory`'s treatment of a device export carrying a credential column.

**Not reversed, and worth saying so:** the fold of business continuity into this row, and the three
non-edges to `legal.personal-legal-matters`, `government` and the clinical rows. All four were
argued at gist depth and the arguments survive; two are strengthened below.

---

## Neighbours considered that did NOT get an edge

- **`legal.personal-legal-matters`** — litigation risk sits in registers, but the edge would be about
  *content* rather than *shape*. A register row saying "adverse judgment in the Smith claim" does not
  look like a pleading. Rejected as thin; unchanged from the gist pass.
- **`government.public-authority-record`** — public-body risk registers are published and statutory.
  Same shape, different publication regime, so the confusion is about the **owner type** rather than
  about which situation the file belongs to. The schema anchor already handles owner type at family
  level. Kept unedged, with the reason upgraded from the gist memo's bare "not an evidence confusion".
  Note this is a *different* row from `government.emergency-management`, which **did** get an edge,
  because there the confusion really is about the document.
- **`clinical_practice.*` / `medical.*`** — a clinical risk register is real and shares the table
  exactly. Left unedged **deliberately**, and I endorse the gist reasoning: those rows carry a
  protective posture, and an edge authored unilaterally from the operations side could be read as
  pulling protected material toward a management branch. CONNECTION's stricter-side-wins principle
  says the pair should be stated from the protected side first. Filed as NJ-BO-RR-3.
- **`manufacturing.safety-case`** — a safety case is an *argument* submitted to a regulator, not an
  inventory; the structures do not resemble each other closely enough for the bytes to be contested.
  Considered and rejected in this pass rather than overlooked.
- **`manufacturing.hse-incident` / `clinical_practice.malpractice-incident`** — considered in this
  pass. An incident report is a realised event and this row holds possibilities; the `retrospective-
  postmortem` edge already teaches the possibility-versus-event discriminator in-family, and a third
  copy of it would be noise. No edge.

---

## The continuity fold, defended on its merits

`ops.business-continuity` was folded here (ROSTER.md Appendix A line 817). The fold is defensible and
worth defending explicitly, because a continuity plan *looks* like a different world — it is
narrative and procedural where a register is tabular.

The case for the fold: continuity planning is what an organisation does about the register entries it
cannot reduce, which makes the plan the **treatment side of the same artefact**; the two are produced
by the same function on the same review cycle; they are stored together; and they are one
purpose-coherent packet — `00`'s *"The documents are content-incoherent but purpose-coherent."*
Splitting them would produce a row whose only distinguishing content was a document format, which
CONNECTION §2 forbids by name.

The case against is real and I record it rather than winning the argument: in many organisations
continuity is owned by a different function, kept in a different place, and shaped as a plan rather
than as a register. It also has the more acute privacy posture (the call tree), so a split would let
the protective rules attach more precisely. This pass keeps the fold on detection grounds and files
the doubt as **NJ-BO-RR-1**.

---

## `proposed_fields` — two, both seconded, none minted

`fields: []` by contract. The dispatch's instruction was to second the family's existing proposals
rather than mint variants, and that is what the JSON now does — with an argument on each, for R1c.

- **`organization`** — seconded, not proposed anew. R1c should read this as one decision across
  several rows: the `business_operations` schema row proposes it, `construction_property` seconds it,
  `it-asset-inventory` seconds it a third time, and this is a fourth. Seconded
  `destination_eligible: false`, with a reason **specific to this row**: a risk corpus is almost
  always single-entity, so an `organization` level here creates exactly the branch `00` forbids — *"A
  folder should not become a collection point for everything produced by the same person or
  organization."* Seconded ceiling `possible`, with a register-specific reason it cannot rise: the
  entity names most reliably present on this row's files are the **subjects of the risks** — a named
  supplier, a named regulator, a named competitor, listed in the description column — not the owning
  entity. A rule that read the strongest entity token would systematically read a threat as the
  owner.
- **`fiscal_period`** — seconded. This row's own reason for wanting it: the review cadence
  (quarterly register review, annual continuity test) is a real period fact of a management calendar
  that no statutory year governs. Seconded `destination_eligible: true` and explicitly **not first**,
  for the reason given in leg 2 — the register is a living document, and a period level above it
  scatters one version family. One caution for R1c, and it is the mirror of the caution
  `it-asset-inventory` filed: the most common date token on this row's files is a **next-review**
  date, which is *prospective* — it names a period the file is not from. A rule family that cannot
  separate a review-due date from a period-of-record belongs at `possible`, not `validated`.

**Deliberately not proposed, and this is the more useful signal for R1c:** any risk-domain key —
`risk_category`, `risk_owner`, `likelihood`, `impact`, `residual_rating`, `recovery_time_objective`.
Every one of them is tempting and every one is wrong here. Categories are **values**, exactly as
`00`'s work types are values, and a key per category would be the 574 failure at field level. Scores
are worse: a likelihood or an impact rating is a **cell in someone else's scale**, and minting a key
for it would invite the product to compare numbers across two organisations' incompatible scales, or
to read a score as a threshold. `00` grounds the abstention — *"A model that cannot cite sufficient
evidence must return unknown."* And a risk owner is a **person**, which the authorship prohibition
keeps out of destinations entirely. Also not proposed: any continuity objective key, for the same
scale-relative reason.

---

## Sparse-file discipline

Seven of ten fixtures carry `group_without_copying_facts: true`, and this row needs the rule as much
as any in the family, because its most common companion files are sparse by nature: an exported heat
map with numbered markers and no descriptions, a call-tree spreadsheet, a scanned signature page, an
archive read from its manifest. A risk folder is the archetypal place where a dozen thin files sit
beside one that names everything, and `00` settles it: *"The graph does not automatically copy those
missing facts onto sparse files."* Concretely: `risk heatmap Q2.png` may be grouped with the register
beside it and must acquire **no** risk fact from it; and `bcp_pack.zip`'s stray personal photograph
inherits no continuity context from its siblings in the manifest.

The licence for grouping at all is `00`'s purpose-coherence sentence: a register export, a heat map,
a narrative paper and a blank form are *"content-incoherent but purpose-coherent."* And **no group is
a valid outcome** — a lone blank risk assessment template is Independent Records.

---

## Legacy ids absorbed (ROSTER.md Appendix A, lines 816–817)

`ops.risk-register` (ROW) and `ops.business-continuity` (FOLD), defended above.

---

## NEEDS-JOSEPH

- **NJ-BO-RR-1 · Should business continuity have stayed folded here?** Carried from the gist pass and
  now argued in full. (a) Keep the fold — cost: a plan-shaped, differently-owned document is filed
  under a register row, and the sharper call-tree privacy posture is diluted across a row that also
  holds ordinary spreadsheets. (b) Split it into its own row — cost: the split row's only
  distinguishing content may be a document format, which CONNECTION §2 forbids, and the two are
  almost always stored together. This pass recommends **(a)** and records the doubt.
- **NJ-BO-RR-2 · The personal or household version.** A person's list of what to do if the boiler
  fails, who to call, and where the stopcock is has exactly this shape and none of the organisational
  anchor. (a) Let it fall to personal administration / Independent Records — cost: a real recurring
  situation gets no template. (b) Let this row take it — cost: someone's household plan is filed
  under a work branch on evidence that never mentioned work. This row recommends **(a)** and refuses
  to decide it silently. This is the **same question** `it-asset-inventory` filed as NJ-BO-1 and
  `partnerships-bd` as NJ-BO-8; R1c should notice it is one question asked three times, and answer it
  once at family level.
- **NJ-BO-RR-3 · Clinical and safety registers.** No edge was authored to `clinical_practice` or
  `medical`, because doing so unilaterally risks pulling protected material toward this row. R1c
  should decide whether the pair is stated, and if so, **state it from the protected side first**.
- **NJ-BO-RR-4 · Reciprocals owed.** Six boundaries here are authored **one-way** — to
  `hr.workplace-health-safety`, `business_operations.board-governance`,
  `business_operations.strategy-plan`, `finance.insurance-corporate`,
  `engineering.risk-analysis-fmea` and `government.emergency-management`. None names
  `business_operations.risk-register`. This is a catalogue defect for R1c, not a judgement about the
  seams. It is the same class of defect `it-asset-inventory` filed as NJ-BO-IT-4.
- **NJ-BO-RR-5 · Theme-named branches are a disclosure. (New this pass.)** The privacy leg above
  identifies a harm the catalogue currently has no way to express: a *folder name* derived from this
  row's content discloses the content. `00` offers redaction in the canvas and review screens, but
  that is a display control, not a naming control. (a) Leave it as prose — cost: the row's most
  specific privacy fact is one nothing enforces. (b) Let R1c mint a catalogue-level marker for rows
  whose dimension values are themselves disclosures, covering this row and parts of `legal` and
  `hr` — cost: new vocabulary on a field-less placeholder. This row recommends **(b)** and notes it
  is adjacent to `it-asset-inventory`'s NJ-BO-IT-2 and the anchor's NJ-J-IND-4; all three are asking
  for a privacy expression the catalogue lacks.

---

## What changed in this pass

**Preserved.** The one_line and its living-register anchor; all eight original `deterministic`
signals; the `needs_llm` list **entirely unchanged** — no model step was added or reworded — and
the `never_alone` list extended by two entries, not rewritten; all 27
`proposed_context_terms`; all ten `work_types`; all five `grouping_reasons`; the `template.why`
paragraph; all nine `file_examples`; all seven original `collides_with` entries; all five
`falls_through_to` entries; the `sensitivity_why` paragraph; the `open_question`. The gist memo's
arguments were correct where it made them, and none is discarded.

**Added.** The three-charge hostile reading with charge (c) conceded outright; the node test argued
leg by leg with the divergence from `it-asset-inventory`'s answer stated openly; the
`organisational-records` comparison; the full answer to charge (b) against both candidate parents; a
sixteen-row files-considered-and-rejected table; the collision fixture in both directions with the
contest/co-activation distinction; a thirteen-row reciprocal boundary table marking which are
one-way; the continuity fold defended on its merits with the case against recorded; two argued
`proposed_fields` seconds and an argued list of six keys deliberately **not** minted; the
sparse-file discipline section; two new NEEDS-JOSEPH items. In the JSON: **five** new
`collides_with` edges (`support-operations`, `policy-handbook`, `strategy-plan`,
`engineering.risk-analysis-fmea`, `government.emergency-management`), taking that list from seven to
**twelve**; one new `also_holds_with` (`business_operations.board-governance`), taking that list from
empty to **one**; **two** `proposed_fields` (`organization` and `fiscal_period`, both seconded,
neither minted), taking that list from empty to two; **two** new `never_alone` entries — a version
token, and a single scoring column read as a threshold — taking that list from seven to **nine**; and
**one** new file example, the FMEA worksheet, taking that list from nine to **ten** (it carries
`group_without_copying_facts: false`, like the other two collision fixtures). The `deterministic`
list is unchanged at eight entries, and `needs_llm` is unchanged at five: **the deepening added no
detection signal and no model step.**

**Reversed.** (1) The non-edges to `support-operations` and `policy-handbook` — both of those rows
name this one, and the catalogue was asymmetric. (2) The committee risk paper's edge type: it is a
co-activation on disjoint evidence as well as a collision, and an `also_holds_with` now says so.

**Not reversed, and stated so.** The node-test verdict (stands, on legs 1 and 3), the continuity
fold, and the three deliberate non-edges to `legal`, `government.public-authority-record` and the
clinical rows.

**Reconciliation pass (added after the fact).** The deepening agent was cut off by the usage limit
between writing this memo and writing the JSON, so the memo above described edits the JSON did not
yet contain. This pass closed the gap. Every JSON change the memo's arguments require was
**applied** rather than walked back: the five new `collides_with` edges, the `board-governance`
`also_holds_with`, the two seconded `proposed_fields`, the two new `never_alone` entries, and the
FMEA file example. Three of the memo's own claims were **corrected to match reality** instead: the
`needs_llm` list was described as extended and was not (the memo's arguments never asked for a new
model step, so the claim was the error, not the data); the sparse-file section's fixture tally moved
from "six of nine" to "seven of ten", since seven of the original nine already carried the flag and
the FMEA fixture is the tenth; and NJ-BO-RR-4 said "five" one-way boundaries while listing six. No
argument in this memo was rewritten, weakened, or added to — only the bookkeeping was made true.
