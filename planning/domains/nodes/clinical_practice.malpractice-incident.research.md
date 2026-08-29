# clinical_practice.malpractice-incident — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the retired gist standard. The gist draft's facts were checked and
its arguments were sound; this pass keeps them, argues the node test leg by leg against the deepened
schema anchor, answers the three charges the dispatch laid, repairs two reciprocals that were missing
(and one of which a neighbour's landed file already asserted as existing), and adds four boundaries
the gist draft named and declined to author. **The verdict is not reversed — the row stands** — but it
is *narrowed*, and the narrowing is written into `one_line` so it is checkable rather than asserted in
a memo. Not padded; where I have less to say than a landed launch row, I say less.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — every quotation in this memo and in the JSON was
  machine-checked with an exact-substring pass before writing. 27 spans checked in the memo pass, 25
  curly-quoted spans re-checked inside the finished JSON. Zero misses in both runs.
- `planning/domains/CONNECTION.md` — §2 (the node test), §5 (the closed edge vocabulary and its
  invariants), PR-6, PR-8.
- `planning/domains/_CONTRACT.md` rules 10 and 15.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/canonical_fields.json`,
  `src/evidence_shape/vocabulary.py`, `planning/domains/roster.json`.
- `planning/overnight/council/DECISION-BRIEF.md` — D1–D6 and J-IND ratified; not re-debated.
- `ROSTER.md` Appendix A line 595 — the absorbed legacy id is `med.clinician-malpractice-incident`
  (ROW). One legacy id, one row; nothing was folded in that this row is quietly failing to cover.

### The schema anchor, read first and treated as binding

`clinical_practice.research.md` (40KB, deepened). Three things in it govern this row directly:

1. **Leg 1 of the schema's own node test is unsatisfiable** — the schema declares no fields, so the
   field leg *cannot be run*, and the anchor refuses to pretend otherwise: it is *"\*not\* quietly
   satisfied by pointing at the one field the world needs"* This row carries that treatment through
   honestly to its own dimension leg (below) rather than quietly satisfying it.
2. **The default template, held as prose**, which a sibling must differ from: *the professional
   situation → the document function; never a patient level; never a diagnosis level; not
   time-first.* This is what leg 1 of my test is measured against.
3. **The family seam is the two-role structure** — a holder-as-author block beside a separately
   labelled subject block naming a *different* person. The anchor also delegated one question to me
   by name: medico-legal instruction *"is a `malpractice-incident` / `referral-correspondence`
   question, not a schema one."* Answered below.

### `clinical_practice.patient-chart.research.md` (37KB, deepened) — read, and applied

The dispatch asked me to apply its two-role reasoning or say why it does not fit. **It fits, with a
divergence I have to state, and the divergence is this row's single most important finding.** Full
treatment in its own section below rather than reinvented in fragments.

### `legal.practice-matter-file.research.md` and `legal.personal-legal-matters.research.md`

Both read in full. This is the load-bearing seam and it gets its own section, stated in both
directions. The gist draft already had both edges and both were correct; what it lacked was the
neighbours' own selectors quoted back at them, and the reason the *third* possible reading — that
this row is simply legal's material — does not hold.

### Also read

`clinical_practice.licensure-credentialing.research.md` (a claim can end a licence — now an edge);
the landed `finance.insurance-corporate` JSON (professional liability is a *value* of `account_type`
there, which is exactly why the two rows do not compete for the same fact);
`business_operations.risk-register.research.md` (which explicitly invited this row to author a pair
it declined to author itself); the landed `clinical_practice.patient-chart`, `.pharmacy-operations`,
`.case-conference` and `.protocol-guideline` JSON, for their inbound edges;
`construction_property.agency-listing.json` for its privacy posture, cited below.

---

## What this row is for, and — new in this pass — what it is not

**Unchanged from the gist draft, and still right:** something has gone wrong, or is alleged to have
gone wrong, in the holder's clinical care, and the indemnity cover standing behind it. The lifecycle
runs internal incident report → complaint → duty-of-candour letter → investigation → claim → expert
report → disclosure → outcome.

**New, and it is a narrowing rather than an addition.** Working through charge (b) forced a
distinction the gist draft blurred. The row has a **centre** and a **periphery**, and only the centre
is owned:

- **The centre — owned.** The practitioner-side record of an adverse event and the complaint about
  it: the incident form, the escalated near-miss, the duty-of-candour or open-disclosure letter, the
  clinician statement, the root-cause analysis, the learning return. Every one of these is authored
  by the holder about a named third party's care. **None of them is a litigation document, and most
  never become one.** This is the material no other row on the roster holds.
- **The periphery — recognised and protected, co-active, not owned.** The litigation members (letter
  of claim, expert report, disclosure bundle, tribunal or regulator notice) and the indemnity members
  (policy schedule, certificate, premium invoice). These carry legal's and finance's structures, and
  the schema row has already authored the schema-level `also_holds_with` edges that license both.

`one_line` now says this, so a reader can check the narrowing against the file rather than against
this memo. It also states the operative consequence: **neither an indemnity schedule nor a premium
invoice activates this row on its own**, and both fixtures now carry that in `must_not_conclude`.

---

## The three charges

### Charge (a) — "legal's material wearing a clinical label; a matter file about a clinician"

**Does not hold for the centre; lands squarely on the periphery, which is why the periphery is not
owned.**

The test is not vocabulary. `legal.practice-matter-file` states its own activation requirement and it
is a role-and-workflow test: strong evidence *"combines labelled roles and a workflow"*, and *"Legal
words, names, captions, identifiers, dates, public availability, folder paths, metadata, shared
download sessions, semantic similarity, and confidentiality legends do not activate this row alone."*
Run that test against the centre:

| Centre member | Practitioner-side representation workflow? | Verdict |
|---|---|---|
| Internal incident form | none — no client, no counsel, no matter, no engagement | not legal's |
| Escalated near-miss report | none | not legal's |
| Duty-of-candour letter | none — the holder writes to the patient, not through counsel | not legal's |
| Clinician statement (internal) | none | not legal's |
| Root-cause analysis | none | not legal's |
| Learning / action-plan return | none | not legal's |

An internal incident report is a **patient-safety** artefact whose entire audience is the reporting
organisation. It exists whether or not anyone ever alleges anything, it is generated in volume by
events that harm no one, and it has no party, no forum, no deadline and no counsel. Calling that
corpus "legal material" would be the same error in reverse as calling a chart entry an incident.

The charge lands where I have conceded it: on the periphery. A letter of claim genuinely *is*
litigation, and it is co-active with `legal`, not owned here. That is what the JSON's two legal
collisions and the schema's `also_holds_with` edge together say.

### Charge (b) — "two worlds forced into one: the insurance policy (finance) and the incident (legal or clinical), joined only by subject matter"

**Partly conceded, and the concession is now enforced in the fixtures rather than argued away.**

The gist draft's implicit answer was that the policy and the incident are one workflow because the
policy is the instrument that responds to the incident and a notification obligation binds them.
That is true of the *world* and irrelevant to the *product*, which observes documents and cannot
observe an obligation. So the honest answer is the charge's: on the evidence, an indemnity schedule
and an incident report share nothing structural at all.

What follows is not a refusal but a rule, and it is now in the file twice:

- `Premium invoice 2026-27.pdf` already carried it — *"activation of this row on the invoice alone: an
  invoice is a finance record and the indemnity context comes from the policy number, not from the
  amount"*
- `MDU policy schedule 2026-27.pdf` **did not**, which was the actual defect. It now carries: the
  schedule alone does not activate this row, because *nothing about a coverage record reports that
  anything went wrong*, and the incident context comes from an incident, a complaint or a claim
  beside it, never from the existence of cover.

With that rule in place the two worlds are not forced into one: the finance members are held
**adjacently and protectively**, and they cannot drag the row into existence by themselves. What
remains genuinely joint — one claim reference appearing on a claims letter, a reserve figure and a
policy schedule at once — is exactly the disjoint-evidence case CONNECTION PR-8 describes for this
family, and the schema row already carries the `finance` pair for it.

### Charge (c) — "an incident-shaped `work_type` of `patient-chart`, since the underlying facts are chart facts"

**Does not hold, and the neighbour has already said so.** `clinical_practice.patient-chart` landed
with a `collides_with` edge pointing here, carrying the discriminator itself: continued accumulation
of routine dated entries about one subject under a responsible-clinician sign-off is the chart; an
incident-system reference, a complaint, a letter of claim, an indemnity schedule or an expert report
is this row. A neighbour that authors a mutex against a row has already rejected the claim that the
row is one of its own values.

The structural reason, stated independently so this does not rest on deference: patient-chart's
carrying signal is **longitudinal accumulation about one named subject.** An incident pack is the
opposite shape — a **bounded lifecycle about one event**, whose membership is decided by a reference
rather than by a person, and several of whose members (a policy schedule, a claims letter, a premium
invoice) contain no clinical content whatsoever and could not sit in a chart at all. A work type is a
value of a field; this is a different grouping principle.

**The gap this pass closed:** the edge was one-way. It is now reciprocated, on the same bytes
(`Consultation 2026-05-15.docx`, patient-chart's own fixture, now this row's under-firing fixture).

---

## The two-role reasoning, applied — and where it diverges

`patient-chart` drew the distinction I was asked to apply or refute. Its argument, in its terms: the
never-alone failure `00` describes is **role ambiguity** — *"A university name alone should not create
a group because Columbia can appear as an authoring school, course provider, target institution,
employer, research venue, or merely a cited organization."* — and *"A row supported by a \*relation
between two labelled roles\* is not a row supported by never-alone tokens, even though each of its
tokens is never-alone on its own"*

**It applies to the centre unchanged.** An incident form has a filled reporter/author block naming
the holder and a separately labelled affected-person block naming someone else. A duty-of-candour
letter has a holder sign-off and an addressee who is the patient or a relative. A clinician statement
has both. These are the schema's own two-role signal with no adaptation, and the reasoning transfers
without restatement.

**It does not apply to the periphery, and that is the finding.** On a letter of claim, an expert
report or a tribunal notice, the holder occupies the **respondent** role — addressee of an
allegation, author of nothing — and the author is a third party entirely (a solicitor, an instructed
expert, a regulator). The schema's defining activation signal **does not fire on this row's most
characteristic litigation members.** What carries recognition there is not a relation between two
labelled roles at all; it is a **process structure**: a reference, plus a deadline, plus an
allegation list.

I have not smoothed this. It is now:

- a `recognition.deterministic` entry in its own right, stating the two role structures separately
  and marked as inference;
- a `never_alone` entry, because the practical failure it predicts is real — *a claim reference beside
  the holder's own name does not establish which role the holder occupies*, since the identical token
  appears where the holder is the respondent clinician, where the holder is a personal party in an
  unrelated dispute, and where the holder is the instructed expert;
- `open_question` (3), with its alternatives and their costs.

The cost of the reading I took is stated there: a family whose defining signal is *not universal
across it*. The alternative — narrow the row to the practitioner-authored centre and route the
litigation members wholly to `legal` — is defensible, and I say in the JSON that I did not take it.
The reason I did not: it splits one obviously coherent lifecycle across two schemas and, worse, the
half that leaves takes the protective posture with it, which is the expensive direction to be wrong
in (see the privacy section).

---

## The node test, leg by leg

CONNECTION §2: *"A **template** row exists only if its detection signals, recommended dimensions, or
privacy rules differ from its schema's default template."*

### Leg 1 — detection signals: **passes, and carries the row**

Measured against the anchor's stated default (two-role structure, batched multi-subject structure,
direction of address), not against a vague sense of it. Three signals here are not narrowings of
those:

1. **The event-report structure.** A labelled incident-reference slot beside a **date-and-time of
   incident** slot that is distinct from the document date, a location or service slot, and a
   category or severity designation drawn from the *reporting system's own* vocabulary. No sibling
   has an event timestamp separate from the document timestamp; a chart entry, a clinic list, a
   guideline and a case-conference deck are all dated once. `00` supplies why the structure is
   readable at all: *"Tables matter because resumes, forms, applications, invoices, and
   administrative documents often place their most useful information in cells rather than body
   paragraphs."*
2. **The complaint-and-deadline structure.** A complainant block, an acknowledgement or
   response-deadline slot, a chronology of the care complained of, and a formal response naming a
   responsible officer. A deadline imposed by a third party on the holder appears nowhere else in
   this family.
3. **The process structure of the periphery** — reference plus deadline plus allegation list —
   discussed above, and honestly labelled as *not* a schema signal.

Signal 1 is the row. Note what it rules *out*, which is the discipline the schema row asks for: the
severity designation is a **raw observation copied from a source system**, never this product's
classification, and that is in `never_alone`.

**Verdict: passes.**

### Leg 2 — privacy rules: **passes, and passes hardest**

Two rules here are not the family default's, and one is not any other row's on the roster.

**Two-sided exposure.** The family default protects a third party. `patient-chart`'s version of the
harm is *aggregation about someone who is not the user*. This row's material does that **and**
simultaneously constitutes an allegation against the holder personally. A leak harms someone who is
not the user *and* someone who is, and the two interests point in opposite directions on the same
bytes. That is a different rule, not a stronger version of the same one, and the JSON now says why it
decides the posture: the patient *"is not present, cannot review a proposal, cannot correct a wrong
grouping, cannot consent, and gains nothing from the tidying"*, while the holder can do all of those.
Where two interests in one file diverge, the cautious setting is the only one safe for the absent
party.

`construction_property.agency-listing` is the calibration the dispatch pointed at, and its lesson
transfers exactly: *"Almost none of those people are the product's user, and none of them can consent
to what the product does."* Its expensive error would have been a permissive posture. This row
aggregates a named patient's clinical detail, a named clinician's alleged conduct, and legal
correspondence in one place — the strongest case on the roster for the same conclusion.

**Disclosure by structure.** This is the row where **the folder label is more dangerous than the
folder contents.** A branch named for an incident, a claim or a patient discloses, from the namespace
alone and without any file being opened, that an allegation exists. `00` pushes the same way inside
the product's own surfaces — *"Protected branches should have configurable redaction in the canvas
and review screens"* — and the residual definition carries the operative limit:
*"Protected Records may represent sensitive isolated material such as passport scans, medical
documents, account statements, visas, legal forms, or credentials; it should normally remain
local-only and must not cause filenames or content to be exposed in model prompts."*

**Verdict: passes.**

### Leg 3 — recommended dimensions: **unsatisfiable for this family, and not quietly satisfied**

`template.dimension_order` is `[]`, empty for two independent reasons, and I record the leg the way
the anchor recorded its own unsatisfiable leg rather than skipping it.

**By contract**, a dimension may only branch on a field the same schema declares, and
`clinical_practice` declares none (`_CONTRACT` rules 10 and 15, CONNECTION PR-6, D1 as narrowed).
So this leg **cannot differ from the schema's default for this row or for any of its ten siblings**,
because the default is empty and so is every sibling's. If R1c reads §2's dimension clause literally,
this leg fails identically for all eleven rows in the family. That is a family-wide question, not
this row's to answer — `patient-chart` filed it as NJ-CP-DIM and I do not open a second copy of it.

**By privacy**, independently, and this is the part that survives if D1 lifts: every dimension this
situation naturally wants — the patient, the incident, the claim — becomes a visible folder label
naming a third party or an allegation. See leg 2. The present recommendation is therefore one
shallow, redacted, user-approved packet with **no automatic internal depth and no label derived from
the matter**, held as prose in `template.why`. Not time-first —
*"For document and record domains, project, function, or subject usually comes before time because
putting year first scatters related work across calendar folders."*

**Overall: kept, on legs 1 and 2, with leg 3 recorded as unsatisfiable rather than satisfied.** The
gist verdict is **confirmed, not reversed** — but confirmed on two legs of three, and the row's own
`open_question` now carries the sharper version of the doubt.

---

## Files considered and rejected

The tempting false positives, and what discriminates each. Two of these are new fixtures in the JSON;
the rest were considered in this pass and deliberately not fixtured.

| File | Why it is **not** this row's evidence |
|---|---|
| **`Incident reporting policy v7.pdf`** (kept from the gist draft) | A policy is *about* incidents and is not one. Discriminator: a version token, a review date, an approval committee and a worked example, with no reference, no subject and no account. `clinical_practice.protocol-guideline` owns it and already states the reciprocal. |
| **`Ward incident - sharps injury - staff.pdf`** (**added this pass**) | The single best false positive on this row, and the gist draft had nothing like it. **The same reporting-system form, the same reference vocabulary, the same category list** — and the affected person is an employee. The form structure discriminates *nothing*. `hr.workplace-health-safety` owns it. Now the second over-firing fixture. |
| **`Consultation 2026-05-15.docx`** (**added this pass**) | The under-firing direction, and the same bytes `patient-chart` already fixtures. A chart entry narrating a deterioration and an escalation is still chart accumulation. What would move it here is a reference, a complaint or claims correspondence — none present. Event vocabulary is evidence for neither. |
| **`near miss log Q1.docx`** (**added this pass**) | `pharmacy-operations`'s own fixture, whose `must_not_conclude` asserts the boundary is *"stated on both sides"* — which **was not true** until this pass, because this row had no pharmacy edge. A routine periodic quality log with initials and an action column is dispensary material; a single named near-miss escalated into a report with a reference is this row's. |
| **A medico-legal report the holder *wrote*, on a solicitor's instruction** | The question the schema anchor delegated to this row by name. **Answered: not this row.** This row is about incidents concerning *the holder's own* care; an authored expert opinion about a third party's care, produced to instruction and sent outward, is an outbound authored opinion and belongs with `clinical_practice.referral-correspondence`, whose signal is direction of address. The *received* expert report — instructed by someone else, about the holder's care — stays here and is the existing fixture. Not fixtured twice; recorded so the delegation is discharged. |
| **An engagement letter, a docket sheet, a notice of electronic filing to a practitioner account, a matter-system export** | `legal.practice-matter-file`'s, on its own test. Even where the underlying facts are clinical, representation workflow is not this row's material and this row must never take it. |
| **A coroner's inquest bundle** | Real and in scope, structurally identical to the disclosure-bundle fixture already present. Earns a `work_type` value, not a second archive fixture. |
| **A patient's own complaint letter, held by the patient** | The role reversal. `medical` / `legal.personal-legal-matters` material. The whole family's holder-role test excludes it and the schema row states it. |
| **A clinical-risk register naming litigation exposure** | Carries both vocabularies and neither anchor. A register entry is a *possibility*; an incident record is a *realised event*. Now an authored edge to `business_operations.risk-register` rather than a fixture — see below. |
| **A journal article or a safety alert about a class of adverse events** | Same false-positive family as the policy. Folded into `never_alone` item 1 rather than given three more fixtures. |
| **A password-protected claims export** | If it cannot be read, the row never activates. That is a residual case (`Unsupported or Encrypted`), already routed, not a fixture that teaches anything. |
| **A CPD certificate for a patient-safety course** | Considered because the vocabulary overlaps completely. Rejected: it is evidence about the holder's standing, `clinical_practice.licensure-credentialing` / `career.credentials-licenses`. The overlap is now handled by an edge, not silence. |

---

## The collision fixture, in both directions

**Over-firing — a file that would wrongly fire this row.** Two, now:
`Incident reporting policy v7.pdf` (guidance about incidents, owned by `protocol-guideline`), and the
new `Ward incident - sharps injury - staff.pdf` (the *identical form* with a staff subject, owned by
`hr.workplace-health-safety`). The second is the more instructive, because the first can be caught by
noticing an absent subject while the second has a filled subject block and fails anyway. The
discriminator is *what kind of person the subject is*, and that is a separate observation from the
form.

**Under-firing — a file that must not be lost *to* this row.** Two, both naming the same bytes as the
neighbour that owns them: `Consultation 2026-05-15.docx` (patient-chart's) and `near miss log Q1.docx`
(pharmacy-operations'). Both are exactly the appetite failure this row is prone to: an incident-shaped
row that reads adverse-event vocabulary as its own would swallow the chart and the dispensary log,
and the protective posture would then *look* like a reason to keep them.

---

## Reciprocal boundaries, both directions

Eleven collisions now, five preserved from the gist draft and six added. Every one names the contested
bytes where they compete. **All edges on this row are authored one-way except where noted; R1c owes
the reciprocals.** Four of the eleven are reciprocals of edges neighbours had already landed pointing
here.

| Neighbour | This row must **not** take | The neighbour must **not** take | Contested bytes |
|---|---|---|---|
| `legal.personal-legal-matters` | a matter where the holder is a personal party with no clinical account — a tribunal caption, a dispute anchored outside clinical care | the internal incident form, the near-miss escalation, the duty-of-candour letter, the clinician statement, the root-cause analysis — none is a litigation document and most never become one | `Letter of claim - ref 24-8871.pdf`; `disclosure bundle 24-8871.zip` |
| `legal.practice-matter-file` | representation workflow — an engagement record, a docket, a filing notice to a practitioner account, a matter-system export | the same list as above, plus the indemnity schedule | the expert report and the disclosure bundle, which appear in both corpora unchanged |
| `finance.insurance-corporate` | the policy-number / cover-period / premium structure — those are finance's fields on finance's evidence (PR-8) | the incident and complaint material sharing a folder with the schedule, or the practice because the invoice names it | `MDU policy schedule 2026-27.pdf`; `Premium invoice 2026-27.pdf` |
| `clinical_practice.patient-chart` **(reciprocal, added)** | routine dated accumulation about one subject under a sign-off | the bounded incident lifecycle, whose members include documents with no clinical content at all | `Consultation 2026-05-15.docx` |
| `clinical_practice.pharmacy-operations` **(reciprocal, added)** | a routine periodic quality log with initials and an action column | a named single event with a reference, a complaint, a claim or a regulator's notice | `near miss log Q1.docx` |
| `clinical_practice.case-conference` **(reciprocal, preserved)** | a recurring meeting series with attendance and a multi-case agenda | a formal reporting form, a complaint, or claims correspondence | an M&M / significant-event review carrying both anchors |
| `clinical_practice.protocol-guideline` **(reciprocal, preserved)** | a version token, review date, approval committee and worked example | a real reference, a real subject, a real account | `Incident reporting policy v7.pdf` |
| `clinical_practice.licensure-credentialing` **(added)** | a notice read as a fact about standing to practise, filed beside registration and privileging material | a regulatory notice arising from a *named care event*, filed beside the incident it came from | a conditions-on-practice notice — a genuine both-rows file |
| `hr.workplace-health-safety` **(added)** | an event whose affected person is an employee, with an occupational-health or return-to-work line | an event whose affected person is a patient, with a clinical account | `Ward incident - sharps injury - staff.pdf` |
| `hr.employee-relations` **(added)** | an allegation about employment conduct with a contractual disciplinary-procedure citation | an allegation about clinical care of a named patient with an incident, indemnity or regulator anchor | an investigation report, which supports neither alone |
| `business_operations.risk-register` **(added, on invitation)** | repeated scored rows across many unrelated hazards under one review cycle | a single event with a reference, a subject and an account | a clinical-risk register naming litigation exposure |

**Two of the additions need their reasons stated, because the gist draft consciously declined them.**

- **`hr.*`.** The gist draft left `hr` unedged on the ground that *"the `hr` row has not landed and I
  did not want to author its half of a pair blind."* **That ground was wrong and I am reversing it
  explicitly, not silently.** An edge requires a *roster* id, not a landed file — the dispatch says
  so, and `hr.employee-relations` and `hr.workplace-health-safety` are both on the roster as
  templates. Authoring my half is not authoring theirs. Leaving it unedged meant the sharpest false
  positive on the row (one form, two kinds of subject) had no boundary at all, which is a worse
  outcome than a one-way edge R1c reciprocates.
- **`business_operations.risk-register`.** Its own memo declined the pair *from its side*, reasoning
  that *"an edge authored unilaterally from the operations side could be read as pulling protected
  material toward a management branch"* and that *"the pair should be stated from the protected side
  first"*, filing it as NJ-BO-RR-3. This row **is** the protected side. Authoring it here is the
  action that memo asked for, and I state it in those terms so R1c can close NJ-BO-RR-3 rather than
  discovering a mystery edge.

**Deliberate non-edges**, recorded rather than left silent:

- **`manufacturing.hse-incident`** — genuinely the same shape one industry over. Not edged: the
  bytes are not contested, because a manufacturing incident has no patient and a clinical incident
  has no plant. `risk-register` reached the same conclusion about the pair from its side.
- **`government`** — regulator investigations are statutory. The contested evidence is the regulator
  notice, and that is now handled by the `licensure-credentialing` edge, which is where the files
  actually sit. A second copy would state one claim twice.
- **`medical.personal-health-records`** — the role reversal (the patient's own copy of the complaint)
  is the *schema* row's business and it states it. A template cannot collide with a schema (§5), and
  the sibling template's version of the same claim would be a different claim.
- **`career.credentials-licenses`** — the CPD-certificate overlap is real, and it is
  `licensure-credentialing`'s known problem, carried in that row's own memo. Reaching across it from
  here would duplicate a boundary its owner is already arguing.

---

## `also_holds_with` is empty, and that is a contract fact, not an omission

Worth stating because a reader will reasonably ask why a row whose fixtures carry
`also_schema: finance` and `also_schema: legal` has no co-activation edge. CONNECTION §5 confines
`also_holds_with` to **schema ↔ schema only**. A template cannot author one. `legal.practice-matter-
file` records the identical constraint on its own row.

The co-activation this situation needs is therefore owed at the schema level — and it is **already
authored there**, by the deepened `clinical_practice.json`, in terms that name this row's exact case:
the `legal` pair is justified as *"A clinical incident that becomes a claim"*, and the `finance` pair
as CONNECTION PR-8 read for this world. So nothing is missing; the edges exist one level up, and the
per-file `also_schema` markers on the fixtures are the template-level record of the same fact.
`role_split` is empty for the same reason a fieldless schema has no roles to split.

---

## `proposed_fields` — empty, deliberately, and not re-minted

**None.** The row defers to the schema row's single `subject_of_record` proposal, and this pass
**reuses that proposal rather than minting a variant**, as the dispatch requires.

The temptation here is specific and I want it on the record: an **incident-reference** or
**claim-reference** key. It is refused on two independent grounds.

1. **It is a value, not a field.** `00`: *"The system may create new values when it sees a new
   course, project, company, university, or event, but it should not invent new fields
   automatically"*. An incident reference is the value of a document reference in exactly the way
   `BUSIB 4300` is the value of a course.
2. **Minting per-situation identifier keys is the 574's failure mode**, rebuilt one row at a time.
   Every situation on the roster has a reference number; eleven rows minting eleven reference keys is
   the giant form the node test exists to prevent.

The schema anchor also asks siblings not to duplicate its one proposal, and specifically not to
produce *"eleven near-identical proposals to reconcile instead of one."* Followed.

`proposed_context_terms` carries 23 terms and is explicitly a **proposal**, not `00`'s floor —
`00`'s only literal context-term list is the academic one. Unchanged this pass; I found nothing to add
that was not already there and did not pad it to look busier.

---

## Sparse-file discipline

Seven of the twelve fixtures carry `group_without_copying_facts: true` (the three added this pass are
all bounded single-neighbour cases and carry `false`). This world needs the rule
sharply, because the reference number makes grouping *easy* and the material makes it *dangerous*: a
stray clinician statement, an unextracted bundle, a screenshot of a reporting form. In every one the
neighbourhood may legitimately group the file while **no** clinical fact, no subject, no cause and no
fault is written onto it — *"The graph does not automatically copy those missing facts onto sparse
files."*

Every fixture carries `"any clinical_practice fact - none is declared"` (or the equivalent) in
`must_not_conclude`, so the placeholder status is checkable file by file rather than asserted once in
a header. That is the mechanism by which a reader can verify this row did not quietly grow fields
during a deepening pass.

The abstention discipline is unchanged from the gist draft and I endorse it rather than rephrasing
it: no inference of fault, causation, breach, liability, privilege or admissibility; a source
system's own harm or severity designation is a raw observation, never this product's classification;
an apology is not an admission, an allegation is not a finding, a claim is not a liability. `00`
licenses the posture directly — *"Correct abstention is a successful outcome because the product's
goal is reliable organization, not maximum file movement."*

---

## NEEDS-JOSEPH

- **NJ-CP-7 · May an incident or claim packet be MOVED at all, even inside a frozen tree?**
  (Preserved from the gist draft; still open, still this row's sharpest operational question.)
  Moving a claim bundle changes paths other people's processes may depend on, and the existence of a
  differently-named branch is itself a disclosure. *Alternatives:* (a) represent-in-place permanently
  for this row, independently of whether the schema ever gets fields — defensible, and cheap, but it
  makes one row behave unlike every other placeholder; (b) allow movement into one shallow packet
  under explicit user policy, which is what `00` requires anyway — *"should not be moved
  automatically without a user policy that explicitly permits it"* — at the cost that the packet's
  name is itself the disclosure; (c) defer with the rest of the family, which leaves the
  disclosure-by-label problem unaddressed until D1 lifts. Not recommended.
- **NJ-CP-8 · The boundary against `legal.practice-matter-file` when the holder is BOTH clinician and
  instructing party.** (Preserved.) A clinician-director receiving a claim about a colleague's care
  occupies the respondent role *and* an instructing role at once. Evidence supports both rows; the
  roster gives no rule. *Alternatives:* (a) a reciprocal edge on the legal side with the
  clinical-account anchor as discriminator; (b) treat it as an unresolved-outcome case routed to
  `Review Later`, which is honest but gives up on a common real situation; (c) a role observation
  that the product records and does not resolve. R1c's call.
- **NJ-CP-ROLE · New this pass, and the one I would most like answered.** The schema's defining
  activation signal (holder-as-author beside a labelled different subject) does not fire on this
  row's litigation members, where the holder is the respondent. Is a template allowed to recognise on
  a structure its own schema does not declare as a signal? *Alternatives and costs* are spelled out
  in the JSON's `open_question` (3); the short form is (a) accept two recognition structures in one
  template, (b) narrow the row to the practitioner-authored centre and lose the protective posture on
  the half that leaves, or (c) leave the periphery co-active as it now is. This row takes (c) and says
  so.
- **NJ-CP-SAFETY** — not re-raised. The schema anchor owns it (`is_safety_domain` is not carried by
  this family and nothing currently forces P7 ahead of a model path for it). This row's material is
  the strongest instance of the gap, which I note there rather than opening a second ticket.

---

## What changed in this pass

Checked line by line against the JSON that was actually written, per the dispatch's instruction.

**Preserved wholesale** — the entire gist draft's `recognition.needs_llm` block, all 23
`proposed_context_terms`, all 14 `work_types`, all 5 `grouping_reasons`, the whole `template.why`
argument including the disclosure-by-label reasoning, all six `falls_through_to` routings, the
original nine fixtures, the five original `collides_with` edges, `fields: []`, `proposed_fields: []`,
`also_holds_with: []`, `role_split: []`, `refuse_node: false`, `launch: "placeholder"`, and the whole
abstention discipline. Nothing correct was rewritten to sound different.

**Changed — nine edits, all verified present in the file:**

1. `one_line` — the retired "Gist-level placeholder (J-IND)" label replaced, **and** the narrowing
   added: the centre/periphery distinction and the rule that neither an indemnity schedule nor a
   premium invoice activates the row alone.
2. `recognition.deterministic` — **one entry added**, stating the two role structures separately
   (author role on the centre, respondent role on the periphery) and marked as inference.
3. `recognition.never_alone` — **two entries added**: a claim reference beside the holder's name does
   not establish which role the holder occupies; an incident-report *form* structure alone does not
   establish a patient-harm incident.
4. `MDU policy schedule 2026-27.pdf` — a `must_not_conclude` entry added: the schedule alone does not
   activate this row. This is charge (b) answered in the fixture rather than in prose.
5. **Three fixtures added** (nine → twelve): `Ward incident - sharps injury - staff.pdf` (second
   over-firing collision fixture), `Consultation 2026-05-15.docx` and `near miss log Q1.docx` (the
   two under-firing fixtures, each naming the same bytes as the neighbour that owns them).
6. **Six `collides_with` edges added** (five → eleven): `clinical_practice.patient-chart` and
   `clinical_practice.pharmacy-operations` (reciprocals of landed inbound edges that were missing —
   and pharmacy's own fixture already claimed this boundary was "stated on both sides", which was
   untrue until now), `hr.workplace-health-safety`, `hr.employee-relations`,
   `clinical_practice.licensure-credentialing`, `business_operations.risk-register`.
7. `open_question` — "Two" → "Three", with the role-divergence question added in full, its three
   alternatives, and a plain statement of which one the row takes and which defensible reading it
   did not take.
8. `sensitivity_why` — one clause added on the absent party who cannot consent, correct or benefit,
   and the holder whose interest in the same bytes runs the opposite way.
9. Depth header on this memo: `GIST` → `J-DEPTH`.

**Reversed — one, stated plainly:** the gist draft's decision to leave `hr` unedged *because the hr
row had not landed*. The reason was wrong (an edge needs a roster id, not a landed file) and the
consequence was that the row's sharpest false positive had no boundary. Two `hr` edges are now
authored one-way.

**Not reversed:** the row stands. The gist verdict is confirmed, on legs 1 and 2, with leg 3 recorded
as unsatisfiable — and the row is narrower than the gist draft left it.

---

## Audits run before returning

- `python3 -m json.tool` — parses.
- Key set **and order** compared against `clinical_practice.patient-chart.json` — identical, 27 keys.
- Every curly-quoted span inside the finished JSON re-extracted by regex and exact-substring checked
  against `00` — 25 spans, **zero misses**. Every quotation in this memo checked the same way — 27
  spans, zero misses.
- Every `collides_with.domain` checked against `roster.json` — all 11 present, all `kind: template`
  (§5 requires same-kind endpoints).
- Every `file_examples.source_type` and every `file_kinds.source_types` entry checked against
  `SOURCE_TYPES` — all valid.
- Every `falls_through_to.residual_template` and every `falls_through_if_inactive` checked against
  `00`'s nine residual names — all valid.
- `fields: []`, `proposed_fields: []`, `template.dimension_order: []`, `also_holds_with: []`,
  `role_split: []`, `refuse_node: false`, `launch: "placeholder"` — all confirmed unchanged.
- No canonical field key minted; no threshold, statistic, confidence score or handling class written.
- `git status` — only this row's two files touched.
