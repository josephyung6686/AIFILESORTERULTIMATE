# clinical_practice.case-conference — lab notes (template row, deepened to J-DEPTH)

Node: `clinical_practice.case-conference`, `kind: template`, `schema_id: clinical_practice`,
`launch: placeholder`, `fields: []`.
Output: [`clinical_practice.case-conference.json`](clinical_practice.case-conference.json). No other
file was written.

This memo replaces the gist-depth memo written under the retired `Depth: GIST` label. The JSON was
**not** discarded: its facts were verified, its key set is house-correct, and its arguments were
sound, so this pass preserved it and made five additions, itemised in *What changed in this pass* at
the end. What the row was missing was never the JSON — it was the argument, and the argument is
below. Two things the earlier pass asserted are **narrowed** here, and both are called out where
they occur rather than quietly reversed.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — the authority. Every quoted span in the JSON (19
  spans) was `grep -F` verified against it in this pass; zero misses. This memo also quotes neighbour
  node files, always attributed to the file they come from and verified the same way. No section numbers are attributed to `00`, because
  `00` is prose.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/_CONTRACT.md` (rules 10 and 15 bind this row);
  `planning/domains/CONNECTION.md` (§2 node test, §4 activation, §5 edge table — `also_holds_with`
  joins **schemas only**, which is why this template row has none, §8 unasserted ≠ false);
  `planning/domains/CONNECTION-EXAMPLES.md` (fixture 5, the `.ics` case, is why this row's calendar
  fixture does not activate on `source_type` alone).
- `planning/domains/canonical_fields.json` — searched for a key that could hold *the person a case
  entry is about*; nothing can. See *proposed_fields*.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 and J-IND ratified; PR-6 (placeholder schemas
  carry no field rows). Not re-debated.
- `planning/domains/ROSTER.md` §4 + Appendix A line 592: this row absorbs the legacy id
  `med.clinician-case-conference` (ROW). That is the whole of its absorbed coverage — one legacy
  row, not a fold-in of several, which is worth stating because it means this row is not carrying
  hidden coverage debt from ids that used to be separate.

### The schema anchor, read first

`clinical_practice.research.md` (40KB, deepened) is this memo's measuring stick and was read in full
before anything was written. Three things it states are load-bearing here and are not re-derived:

1. **Leg 1 of the node test is unsatisfiable for this whole family**, because the schema declares no
   fields. The schema row records it as *not passed, argued* rather than pretending otherwise, and
   this row carries the same honesty forward instead of quietly satisfying it (see below).
2. **The family's default template, held as prose** — the paragraph a sibling must differ from:

   > The **professional situation** (a caseload, a credentialing cycle, an incident, a
   > correspondence register) → the **document function** within it. **Never** a patient level.
   > **Never** a diagnosis or condition level. **Not time-first.**

3. **The seam is the two-role structure** — an author/responsible-clinician block naming the holder
   beside a *separately labelled* subject block naming a **different** person, both filled. Not
   vocabulary, not letterhead, not clinical density.

The schema row's own sibling table already scores this row: *"multi-subject batching in a single
artefact; a meeting-shaped grouping"*, verdict *passes*. This memo is the working that the table summarises,
and it is written so that a reader can disagree with the verdict on the evidence rather than on the
table.

### Landed neighbours read before writing, and not edited

- `clinical_practice.patient-chart.json` + memo — the nearest sibling and the sharpest collision.
  Read in full; this row's fixture set now names bytes on both sides of it.
- `clinical_practice.malpractice-incident.json`, `.teaching-material.json`,
  `.practice-administration.json`, `.protocol-guideline.json` — the four other in-family rows this
  one can steal from.
- `business_operations.meeting-record.json` + memo, and
  `business_operations.retrospective-postmortem.json` — the two landed rows anywhere in the roster
  that name **this** row. Both were read before an edge was authored back, and neither is
  contradicted.
- `business_operations.organisational-records.json` — read for refusal quality only. Its
  `refuse_reason` is the standard this row's node test had to survive, and the shape of the refusal
  I was prepared to write.
- `medical.json`, `medical.personal-health-records.json` + memo — the clinician-authored versus
  patient-held seam, at launch depth.
- `legal.practice-matter-file.json` + memo — the structural analogue (a practitioner's file about
  another person, field-less).

---

## What this row is for, and what it holds

The organizational situation of material prepared for, presented at, or produced by a **recurring
meeting at which several named cases are discussed across services**: tumour boards and
multidisciplinary team meetings, morbidity-and-mortality and significant-event reviews, a
clinician's contribution to a safeguarding conference, ward rounds recorded as documents.

It holds agendas and numbered case lists, per-case presentation decks with imaging panels,
supporting result and pathology exports, outcomes-and-actions records, attendance and quorum
records, distribution emails and recurring invitations, recordings and transcripts, and the meeting's
own terms of reference.

**The organizing anchor is the MEETING, not any one patient.** That sentence is the row, and
everything below is an attempt to break it.

---

## Node test, argued leg by leg

CONNECTION §2 for a `kind: template` row: it exists only when its **detection signals**,
**recommended dimensions**, or **privacy rules** differ from its schema's default template. Three
legs, three separate arguments, and one of them cannot be run.

### Leg 1 — dimensions: **unsatisfiable, and not quietly satisfied**

`template.dimension_order` is `[]`. It has to be: a dimension may only branch on a field the same
schema declares, `clinical_practice` declares none (`_CONTRACT` rule 15, PR-6, D1 as narrowed), and
so **every** template on this family has an empty `dimension_order` by contract. This row's
dimensions are therefore identical to the schema's default, and the leg fails.

That failure is worth stating precisely rather than waving through, because it is the leg that
would, read literally, kill all ten siblings at once. It is a **roster-wide** consequence of J-IND,
not evidence about this row, and the schema memo already files it as such. This row does not invent
a dimension to pass it. Inventing one would be the 574's mistake with extra steps: a
`meeting → document function` order proposed today would be a folder label proposed on a field that
does not exist.

But the schema row's second reason for the empty template is independent of the contract and
**survives even if D1 lifts**, and that is where this row genuinely has something to say. The
schema's reason (2) is that every natural dimension here becomes a visible folder **label** naming a
third party. This row's natural dimension is the one exception in the family: a *meeting* name
discloses a service and a cadence, not a person. It is the least exposing anchor on the family. That
does not make the leg pass — a meeting branch still discloses a caseload through its members, and
the members themselves name several third parties at once — but it makes this row the only place in
the family where the question *"may a branch exist at all?"* has a plausible **yes**, which is why
it is `open_question` and NJ-CP-4 rather than a settled empty.

**Leg 1: does not pass. Recorded, argued, not padded.**

### Leg 2 — detection signals: **passes, and carries the row**

Three signals in `recognition.deterministic` are this row's and no sibling's:

1. **Several different subjects in one artifact, under one meeting header.** A numbered case list
   in which each item names a *different* person, beneath a header carrying a meeting name, a
   service, a date and an attendance-and-apologies list. No other row on this family has a fixture
   whose defining feature is that the subject **changes between items of the same document**. The
   schema row supplies the batched-multi-subject signal at family level (a clinic list, a theatre
   list, a handover sheet); this row narrows it with the thing those lack — a *meeting* frame with
   attendance, quorum and apologies around the batch. A theatre list is a work queue; an MDT agenda
   is a deliberative body's paper.
2. **The repeated per-case sub-shape.** A slide or section structure repeating a fixed skeleton —
   identifier, summary, imaging or results, *question for the meeting* — across several subjects in
   one file. The question line is the tell: it is prospective and addressed to a group. A chart entry
   records what was decided; a conference paper asks a body to decide.
3. **The outcome-and-actions table.** Per case: a decision, a responsible clinician, an action, a
   review date. `00` is the reason this is readable at all — *"Tables matter because resumes, forms,
   applications, invoices, and administrative documents often place their most useful information in
   cells rather than body paragraphs."* — and the reason it is *evidence* rather than a format is
   that its rows are **people**, not line items.

Each of the three is a **detection** signal only. The precondition at the head of
`recognition.deterministic` says so in the file itself, because a placeholder row that reads like an
extraction licence is exactly how a field row gets minted by accident: *"Privacy policy must be
enforced before content reaches any model or external connector."*

**Leg 2: passes.**

### Leg 3 — privacy rules: **passes, and this is the leg that matters most here**

The schema's privacy default already includes **bulk sensitivity** — a multi-subject list is not one
file's worth of exposure but N people's. So the honest question is not *"is this row bulk-sensitive?"*
(the family is), but *"does it need a rule the schema's default does not already give it?"* It does,
and the rule is **denser and structurally different in two ways**:

- **The aggregation is deliberate and cross-service, not incidental.** A clinic list aggregates the
  people one clinician will see in one room on one morning. A conference pack aggregates the people
  *several services* have each escalated as difficult, with a narrative attached to each. The
  selection criterion itself is disclosing: membership of the list is, on its face, a clinical
  signal about each member. Nothing in the schema's default covers a set whose *membership rule* is
  sensitive. **Provenance: inference.** `00` does not discuss aggregation criteria; it names the
  material and requires the transition — *"A scanned passport, tax statement, medical document,
  authentication key, or account record should enter a protected state immediately."*
- **The pack is purpose-coherent, so protection has to travel across content-incoherent members.**
  An agenda, four imaging exports, a spreadsheet and a **blank** outcomes form arrive together. `00`
  describes exactly this shape — *"The documents are content-incoherent but purpose-coherent."* — and
  the grouping machinery will legitimately assemble them. The consequence for this row is that the
  *least* individually-sensitive member (the blank form, the `.ics`, the untranscribed `.m4a`)
  travels inside a protected purpose group, and must not be treated as ordinary because it reads as
  empty. The `mdt_recording_20260514.m4a` fixture carries the sharpest form of this in
  `must_not_conclude`: unreadable at scan time is not safe, because a conference recording *speaks
  several patients' names aloud*, and transcription is itself a gated path — `00` allows
  speech-to-text *"only under an explicit privacy and compute policy"*.

Both rules bite before any model call, under the same operative limits: *"Protected material should
not be included in cloud-model prompts by default, should not display raw content in general group
summaries, and should not be moved automatically without a user policy that explicitly permits it."*
And in the interface, where a meeting-named branch is most tempting to render in full:
*"Protected branches should have configurable redaction in the canvas and review screens"*.

**Leg 3: passes.**

**Overall: the row stands, on legs 2 and 3, with leg 1 recorded as unsatisfiable.** Same margin as
its schema, for the same structural reason, and stated rather than smoothed.

---

## The row-specific risk, taken seriously: is this just a `work_type` of `patient-chart`?

This was the dispatch's warning and it deserves a real answer, because it is the argument that would
sink the row. It runs: material prepared for a meeting *about* a patient is chart material; the
outcome is filed to the chart; "MDT paper" is therefore a `work_type` value beside "clinical note"
and "treatment plan", exactly as `med.clinician-clinical-note` and `med.clinician-treatment-plan`
folded into `patient-chart` per ROSTER Appendix A lines 589–591. **The precedent for folding this row
in already exists inside its nearest sibling.**

Three reasons it does not fold, in order of weight:

1. **The cardinality is wrong for a chart work type.** A chart is *"The longitudinal record a practice keeps"* ... *"about one other person"* (`patient-chart`'s own memo). Every work type it folded in
   — a note, a plan — is a document about **one** subject that files **into one** record. An MDT
   agenda naming eleven people cannot be a work type of a one-subject record, because it cannot be
   filed into one; it files into eleven, or into none. A work-type value that forces its parent
   situation to fan out is not a value, it is a different situation. This is the decisive reason.
2. **The detection evidence is disjoint, not narrower.** A work type is recognised by a *narrower
   filter on the same signals* — the schema memo is explicit that *"A sibling justified only by
   "we hold letters" is the schema's default template with a narrower filename filter."* This row's
   signals are not a filter on the chart's; they are the chart's signals **inverted**. The chart
   requires one subject block and accumulation over time in one artifact. This row requires the
   subject to *change between items* of one artifact, plus a frame (attendance, quorum, apologies)
   the chart never has.
3. **The grouping anchor survives the subject.** One case travels across several meetings; one
   meeting covers several cases. Under the chart-only reading, the second relation has no
   representation at all — the recurring series would be reconstructed, if ever, by filename
   similarity, which `00` gives no licence for. The row's `grouping_reasons` name the series
   explicitly and name the danger of the first relation in the same breath: grouping one case across
   meetings is *"the one most likely to tempt a subject label onto members, which is exactly what
   must not happen"*, under *"The graph does not automatically copy those missing facts onto sparse
   files."*

**What survives of the objection, and is not dismissed:** the *outcome paragraph* genuinely is chart
material once pasted into a chart, and the same text then exists in both situations. That is not a
defect to be resolved by a boundary; it is one text with two custodies. The row handles it as a
fixture on both sides rather than as a rule (below), and `00` licenses leaving it unresolved —
*"Correct abstention is a successful outcome because the product's goal is reliable organization,
not maximum file movement."*

**I did not refuse this row.** Refusal was live through the whole of the analysis above and the
verdict is 1 above, not a preference for keeping the id. Had cardinality gone the other way — had
the batched multi-subject artifact turned out to be rare or reconstructible — the correct outcome
would have been `refuse_node: true` routing through Protected Records and a `work_type` value on
`patient-chart`, in the shape `business_operations.organisational-records` uses.

---

## The other row-specific risk: a case conference is a meeting

`business_operations.meeting-record` exists, survived its own refusal question, and **already names
this row** from its side, with the discriminator *"whether named patients are discussed; if they
are, the clinical row owns it and the file is protected material"*. So does
`business_operations.retrospective-postmortem`, for M&M reviews.

Before this pass, that edge was **one-way in the wrong direction**: the business rows named this
one, this one named neither. That is a reciprocity defect the addendum asks for specifically, and
the fix is now in the JSON — a `collides_with` entry for `business_operations.meeting-record`
worded to match the neighbour's own sentence rather than to compete with it. Stated in both
directions:

- **This row must not take** an agenda/attendance/actions artifact merely because it was produced in
  a clinical building, by clinicians, on a recurring series. A department's rota-and-budget meeting
  is `clinical_practice.practice-administration`'s; a company's is
  `business_operations.meeting-record`'s. The `Team meeting minutes 2026-05-14.docx` fixture is in
  the JSON precisely to make this checkable.
- **The business row must not take** a document because it is meeting-shaped and its subjects are
  anonymous-looking, when those subjects are third parties under care. This matters more in this
  direction than in the other, because the business row's residual posture is not protective and a
  wrong answer here **loses protection**, not just tidiness.
- **The contested bytes:** an outcomes table with columns *case / decision / responsible / action
  by*. That table is structurally identical on both sides. What discriminates is whether the rows
  are **attendees' own work items** (business) or **people who are not in the room** (this row).
  Neither side may use vocabulary: `00` — *"Topic answers what a file is about, while purpose
  answers what the file was for."*

The M&M case is genuinely three-cornered (this row, `malpractice-incident`,
`retrospective-postmortem`) and the JSON says so rather than picking: the `M&M review - Feb 2026.docx`
fixture carries *"which of this row and clinical_practice.malpractice-incident owns the file - both
anchors are genuinely present"*, and P10 chooses from an accepted group later.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. The tempting false positives:

| File | Why it is **not** this row's evidence |
|---|---|
| **`Journal club - May.pptx`** (fixture, kept) | The agenda-and-attendance frame is complete; there are **no cases**. Discriminator: not one item names a subject. Goes to reading material, not Protected Records — the privacy answer differs, which is why it earns a fixture rather than a sentence. |
| **`Team meeting minutes 2026-05-14.docx`** (fixture, kept) | Same frame, same recurring series, items are rotas and budgets. Discriminator: whether named cases are discussed. `practice-administration`'s. |
| **`Consultation 2026-05-15.docx`** (fixture, **added this pass**) | One subject, dated accumulation, holder's sign-off — and a **pasted MDT outcome paragraph**. The meeting text is quoted *into* the chart; it does not carry the chart out. The under-firing fixture. |
| **`Initial child protection conference - minutes.pdf`** (fixture, **added this pass**) | Header, chair, mixed-agency attendance, a named family, a plan category. Discriminator: **who convened it and who authored the artifact.** The authority's record is `government.social-services-casework`'s; the clinician's report *for* the conference is this row's. |
| A **trial management meeting / data monitoring committee** pack | Real, and identical in shape. Rejected as a fixture, kept as a `collides_with` signal against `research`: the discriminator is a project identifier, an approval or protocol number, or participant-facing framing. It would teach the same lesson as the journal-club fixture with a longer setup. |
| A **grand round** deck | Rejected: `clinical_practice.teaching-material`'s. `00` gives the test — the topic is identical to a real case, the purpose is not. Learning objectives, discussion questions and age-and-sex descriptors instead of identifiers. |
| A **handover sheet** or **theatre list** | Batched and multi-subject, and therefore tempting. Rejected: no meeting frame — no attendance, no apologies, no quorum, no decision-and-owner. It is a work queue, and it belongs to the schema's own batched-list signal, not to this row. This is the closest rejection in the set and the one most likely to be argued the other way. |
| A **safeguarding strategy meeting record** convened by a health trust | Kept in scope, as a `work_type` value, not a fixture: same shape as the MDT agenda with a different service. The *authority-convened* variant is now a fixture because it changes the owner; the health-convened one does not. |
| A **ward round** note for one patient | Rejected: a ward round documented per-patient is chart material. Only a ward round recorded as a single multi-patient document is this row's — which is the cardinality argument again, applied to a case that could go either way. |
| A **conferencing transcript `.vtt`** | Folded into the `.m4a` fixture. Same extractor story, same gated transcription path; a second fixture would restate it. |
| A **de-identified case-based-learning vignette** | `teaching-material`'s, and named there. Not re-fixtured. |
| A **blank outcomes form** | Not given its own fixture, but deliberately named *inside* the `needs_llm` purpose-packet entry, because its lesson is only visible as a **member of the pack** — alone it is a template and this row must not fire on it. |
| A **`.vcf` of the MDT distribution list** | `00` settles it: contact material is *"privacy-protected rather than used to create folder proposals"*. Nothing meeting-specific would be learned. |

---

## The collision fixture, in both directions

### Over-firing: `Journal club - May.pptx`

Meeting header, date, attendance line, a discussion-questions slide, a citation block. Every frame
signal this row has. **No case anywhere.** What discriminates is item content, not the frame — and
the consequence is visible in the fall-through, which is *Reading Inbox*, not *Protected Records*:
*"Reading Inbox may hold papers, articles, reports, and saved PDFs that appear to be reading
material but have no active research, course, or project association."* Firing wrongly here does not
merely misfile a paper; it drags an unprotected artifact into a protected posture and teaches the
user that the protected branch is noisy.

This is why `never_alone` leads with *"an agenda, attendance list, or minutes structure alone. Every
organisation on earth produces those"* and why meeting vocabulary — MDT, board, round, review,
conference, huddle — is listed as never-alone in its own right.

### Under-firing: `Consultation 2026-05-15.docx` — **added this pass**

One labelled subject block. A run of dated entries about that one person. The holder's
responsible-clinician sign-off. And, in the newest entry, a pasted paragraph naming the meeting, its
date and the agreed plan — **the same sentences that appear in the conference's own outcomes
record.**

What discriminates: **cardinality and container, not text.** One subject accumulating dated entries
is `patient-chart`. The meeting text is quoted *into* the chart. The fixture's `must_not_conclude`
makes both halves checkable — no activation of this row from the pasted paragraph, and no
meeting-series group anchor inferred for the file from that paragraph alone, under *"The graph does
not automatically copy those missing facts onto sparse files."*

**The same bytes are now named on both sides**, which is what the addendum asks for: `patient-chart`
holds the chart and this row holds the outcomes record, and the shared paragraph is a fixture on
this row rather than a rule on either. I did not edit `patient-chart.json` to add the mirror — it is
outside my two files. **R1c owes that reciprocal**, and it is a one-line addition rather than a
research task.

---

## Reciprocal boundaries

Every neighbour this row could steal from, both directions, contested bytes named.

| Neighbour | This row must **not** take | The neighbour must **not** take | Shared fixture bytes |
|---|---|---|---|
| `clinical_practice.patient-chart` | a one-subject longitudinal record, however much meeting text is pasted into it | an agenda, deck or outcomes record naming several subjects, merely because one of them is the patient whose chart it is filing | **`Consultation 2026-05-15.docx`** (added) beside `MDT outcomes 2026-05-14.xlsx` |
| `clinical_practice.malpractice-incident` | an incident reference number, a formal reporting form, a duty-of-candour letter, an indemnity or claims chain | the review *meeting's* recurring series, attendance and multi-case agenda | `M&M review - Feb 2026.docx` — both anchors present, P10 chooses |
| `clinical_practice.practice-administration` | rotas, budgets, equipment, departmental business, however clinical the room | a meeting whose items are named cases | `Team meeting minutes 2026-05-14.docx` |
| `clinical_practice.teaching-material` | learning objectives, a trainee audience, age-and-sex descriptors in place of identifiers | real identifiers, a service caseload and an outcomes-and-actions record | a case-based deck; the discriminator is purpose, not topic |
| `research` | a project identifier, an ethics or approval-number slot, participant-facing framing | routine care of named patients with no study anchor | a trial management meeting pack |
| `business_operations.meeting-record` | an agenda/actions artifact whose subjects are the attendees themselves | a meeting-shaped file whose subjects are third parties under care — a wrong answer here **loses protection** | an outcomes table: *case / decision / responsible / action by* |
| `business_operations.retrospective-postmortem` | an organisational service, product or delivery outcome with no patient | a clinical M&M's named patients and care episode, and its protective posture | contributory-factors and learning-points vocabulary, shared verbatim |
| `government.social-services-casework` (**edge added**) | the convening authority's own conference minutes, plan category and review record | the clinician's own report prepared *for* the conference, and it must not read the health attendee as proof of clinical custody | **`Initial child protection conference - minutes.pdf`** (added) |
| `hr.employee-relations` (**edge added**) | a conference about a member of staff with employment apparatus — allegation, right to be accompanied, absence record, appeal reference | a meeting about a patient or service user receiving care | a header + attendance + one named subject + decision and actions |

Reciprocity status, verified by grep across `nodes/` in this pass: the two `business_operations`
rows name this row and are now named back. `government.*` and `hr.*` have **not landed** — no files
exist under `planning/domains/nodes/` for either — so those two edges are authored one-way
knowingly, and R1c owes the reciprocals. `patient-chart` names this row already; the shared-bytes
mirror on its side is the outstanding item.

---

## Neighbours considered that did **not** get an edge

- **`academic`** — a grand round is teaching and academic at once, but the three-cornered case is
  already stated at schema level and against `clinical_practice.teaching-material` here. Tripling it
  would state one claim three times.
- **`legal` / `law_practice`** — a case conference minuted in contemplation of litigation may attract
  privilege. Genuinely adjacent, and deliberately unedged: the contested evidence (a privilege
  marking, an instructing-solicitor block, a matter reference) sits on
  `clinical_practice.malpractice-incident` and `.referral-correspondence`, where the files are, and
  the schema row already carries the `legal` pair. CONNECTION §8: unasserted means unasserted, not
  false.
- **`photos`** — an imaging panel pasted into a deck carries no EXIF worth an edge, and the schema
  row already handles the photographed-chart-page case.
- **`medical`** — this row's confusions are internal to its family. A patient does not hold an MDT
  agenda; they may hold a *letter* summarising the outcome, and that letter is
  `medical.personal-health-records`' by the holder-role seam the schema row draws, not by anything
  this row would add.

---

## `proposed_fields`

**None.** The one fact this world needs — the person a case entry is about — is proposed **once**,
on the schema row, as `subject_of_record` (string, `destination_eligible: false`,
`reliability_ceiling: possible`, `adjudicate: R1c`). This row **reuses that proposal and does not
mint a variant**, per the schema memo's explicit instruction that a sibling proposes a field only if
its situation needs a fact `subject_of_record` cannot carry.

I checked whether this row is such a case, because it is the one place in the family with a
plausible claim: this row's artifacts have **several** subjects each, and a scalar key cannot hold
them. The claim does not survive. A multi-valued `subject_of_record` is the *same* adjudication —
may another person's identity be stored as a fact at all — with a cardinality detail attached, and
`00`'s data model already separates the two concerns: *"The values table stores the specific answers
inside those fields"*, one field to many values. Minting `subjects_of_record` would hand R1c two
near-identical proposals to reconcile instead of one, which is exactly the failure the schema memo
warns against. **The cardinality point is recorded as a rider on NJ-CP-FIELD, not as a new key.**

---

## Open questions surfaced (NEEDS-JOSEPH)

- **NJ-CP-4 · Is a MEETING an acceptable branch anchor in v1 when a patient is not?** (This row's
  own; carried in `open_question`.) A meeting name discloses a **service and a cadence**, not a
  person, and meeting-first is how clinicians actually file this material. *Alternatives and costs:*
  (a) **yes, shallow and user-approved** — this row becomes the only one on the family carrying a
  non-redacted level, which must be recorded as a **deliberate exception** with a stated reason, or
  it will read as drift and the next author will generalise it; (b) **yes, but redacted** — a
  meeting branch whose label is masked in canvas and review, cheap under
  *"Protected branches should have configurable redaction in the canvas and review screens"*, at the
  cost of a branch the user cannot recognise at a glance, which is most of its value; (c) **no** —
  represent-in-place under Protected Records, consistent with the rest of the family, at the cost of
  never matching the user's real filing habit for the one situation where it is unambiguous. The
  question does **not** depend on whether `clinical_practice` ever gets field rows.
- **NJ-CP-5 · Staff-subject conferences** — **partly resolved in this pass.** The gist row left this
  unedged and flagged it; an `hr.employee-relations` `collides_with` edge is now authored with the
  employment-apparatus discriminator. What remains for R1c is only whether the pair should be a
  *collision* (mutex, as written) or *also-holds* (a genuine co-activation for occupational-health
  material that is clinical **and** employment at once). I wrote the mutex because `also_holds_with`
  joins schemas only (CONNECTION §5) and this is a template, so the co-activation, if it is real,
  belongs on `clinical_practice.json` — which the schema memo deliberately left unedged for `hr`,
  saying the evidence sits at template level. **The two decisions must be made together or the pair
  falls between them**, and that is the actual risk here.
- **NJ-CP-6 · The convening-body rule, generalised.** This pass discriminated the safeguarding case
  by *who convened the meeting and who authored the artifact*. That is a clean rule and it is
  **new** — it is not in the schema row's seam, which is about author-versus-subject roles within a
  document, not about the body that called the meeting. If R1c accepts it, it likely belongs
  upward at schema level (it would also settle multi-agency discharge planning, mental-health
  tribunals and child-death review); if it is rejected, this row's `government` edge should go with
  it. Flagged rather than promoted, because promoting it would be a template row editing its schema.
- Carried by inheritance, not restated as edges: **NJ-CP-SAFETY** (this material is
  patient-identifying by default and the schema does not carry `is_safety_domain`, so nothing
  currently forces P7 ahead of a model path — sharper here than anywhere in the family, because the
  pack's *purpose group* is what reaches the model), **NJ-CP-FIELD** (with the multi-subject
  cardinality rider above), **NJ-CP-EVIDENCE**, and **NJ-CP-1** (the clinician-authored versus
  patient-held boundary).

---

## What changed in this pass

**Preserved wholesale:** the entire `recognition` block (all three lists, including the two
preconditions), `proposed_context_terms`, `work_types`, `grouping_reasons`, the `template` argument
and its `why`, all nine original fixtures, the five original `collides_with` edges,
`falls_through_to`, `sensitivity`, `sensitivity_why`, and `open_question`. The gist draft's verdict
— that the row stands on the meeting anchor — is **confirmed**, not re-argued into different words.

**Five changes:**

1. `one_line` — the retired gist marker replaced ("Gist-level placeholder (J-IND)" →
   "Full-depth placeholder (J-IND, written to J-DEPTH)").
2. `one_line` — **a narrowing, stated rather than silent.** "safeguarding conferences" →
   "the clinician's contribution to a safeguarding conference". The gist draft claimed the whole
   situation; on the convening-body analysis the authority's own conference record is
   `government.social-services-casework`'s. I am narrowing the earlier claim, and NJ-CP-6 exists so
   the narrowing can be reversed if R1c rejects the rule it rests on.
3. **Two fixtures added** — `Consultation 2026-05-15.docx` (the under-firing direction; the gist row
   had an over-firing fixture and no under-firing one, so the addendum's both-directions
   requirement was genuinely unmet) and `Initial child protection conference - minutes.pdf` (the
   convening-body boundary, with bytes).
4. **Three `collides_with` edges added** — `business_operations.meeting-record` (reciprocating an
   edge the neighbour already asserted, worded to match its sentence),
   `government.social-services-casework`, and `hr.employee-relations` (resolving what the gist memo
   left unedged as NJ-CP-5).
5. The memo itself: the node test argued leg by leg with leg 1 recorded as unsatisfiable rather than
   summarised as "passes, on the anchor"; the `work_type`-of-`patient-chart` objection answered in
   full; the meeting boundary stated reciprocally; twelve files considered and rejected in place of
   four; the collision fixture in both directions; and NJ-CP-6 surfaced.

**Not changed, deliberately:** `fields: []`, `proposed_fields: []`, `role_split: []`,
`template.dimension_order: []`, `time_first: false`, `also_holds_with: []` (template rows cannot
carry it — CONNECTION §5), `refuse_node: false`.

## Audits run before returning

- `python3 -m json.tool` on `clinical_practice.case-conference.json` — parses.
- Key set and key order compared to `clinical_practice.patient-chart.json` — identical keys, same
  order; the two rows diff cleanly.
- Every curly-quoted span in the JSON (19) `grep -F`'d against
  `planning/00-database-agent-product-design.md` — all present verbatim, zero misses. Of this memo's 25
  quoted spans, 14 verify verbatim against `00` and 8 against the neighbour file they are attributed
  to; the remaining 3 are the memo's own rhetorical questions, not attributed quotations.
- No canonical field key minted; `proposed_fields` remains empty and the schema row's
  `subject_of_record` is reused by reference.
- Reciprocity re-verified by grep across `planning/domains/nodes/`: the two `business_operations`
  rows naming this row are now named back; `government.*` and `hr.*` have not landed and are
  authored one-way knowingly.
- `git status` — only `clinical_practice.case-conference.json` and
  `clinical_practice.case-conference.research.md` modified.
