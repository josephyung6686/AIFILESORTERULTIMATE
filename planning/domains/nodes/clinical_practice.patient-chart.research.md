# `clinical_practice.patient-chart` — lab notes (template row, deepened to J-DEPTH)

Node: `clinical_practice.patient-chart`, `kind: template`, `uses_schema: clinical_practice`,
`launch: placeholder`, `fields: []`.
Output: [`clinical_practice.patient-chart.json`](clinical_practice.patient-chart.json). No other
file was written.

This memo replaces the gist-depth memo written under the retired `Depth: GIST` label. **The JSON was
not rewritten.** Its facts were verified, its key set matches `medical.personal-health-records.json`
exactly, and its arguments — where it made any — were sound. This pass preserved all of it and added
four `collides_with` edges, two file examples, one `never_alone` entry, and one `one_line` word.
Those additions are enumerated against the file itself in *What changed in this pass*, at the end.

**The charge this row was deepened under was not "does it survive?"** It was: *be precise about what
is NOT in it.* A chart that absorbs everything about a patient is a residual wearing a domain's
clothes, which is the exact thing `business_operations.organisational-records` was refused for. The
long middle of this memo is therefore subtraction, not addition.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — the authority, and the only document quoted
  inside quote marks. Every curly-quoted span in the JSON and in this memo was `grep -cF` verified
  against it in this pass; all present verbatim, zero misses. No section numbers are attributed to
  `00`, because `00` is prose.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/_CONTRACT.md` (rules 10 and 15 bind this row);
  `planning/domains/CONNECTION.md` §2 (the node test, quoted below), §4 step 2, §5, §8.
- `planning/domains/canonical_fields.json` — searched, and the search's whole result is recorded
  under *`proposed_fields`* below: it is a deliberate **zero**.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 and J-IND read as ratified, not re-argued.
- `planning/domains/ROSTER.md` Appendix A lines 589–591 — the legacy rows this row owns:
  `med.clinician-patient-chart` (ROW), `med.clinician-clinical-note` (FOLD),
  `med.clinician-treatment-plan` (FOLD).
- `src/evidence_shape/vocabulary.py` — no `source_type` was invented.

### The schema anchor, read first and treated as binding on this row

`clinical_practice.research.md` (40KB, J-DEPTH). Three things in it govern this memo:

1. It states the family's **default template** as a prose paragraph, and every sibling must differ
   from *that paragraph*, not from a vague sense of the schema.
2. It records that the node test's **field leg is unsatisfiable for this family**, because the
   schema declares no fields, and it refuses to paper that over. **This memo carries the same
   honest treatment and does not quietly satisfy it** — see leg 3 below.
3. It measures the ten siblings in a table, and rates this row *"the one-subject longitudinal
   accumulation; the strongest form of the 'never a patient level' prohibition — passes."* That is
   the verdict this pass had to re-earn at full depth, not inherit.

### Landed neighbours read before writing, and not edited

- `medical.personal-health-records.json` + memo (22KB, launch row, full depth) — read in full. The
  clinician-authored versus patient-held seam is this row's defining boundary. Its 22 fixtures were
  read individually; two of them are contested with this row and are now named on this side.
- `medical.json` — the source of the `After Visit Summary.pdf` reciprocal fixture bytes.
- `clinical_practice.case-conference.research.md` (37KB, deepened) — it argued its boundary against
  this row and won that argument. This row states its side, and corrects one factual claim the
  sibling made about this file.
- `clinical_practice.referral-correspondence.json` + memo, `.malpractice-incident.json` + memo —
  the two siblings that take material out of, and add material to, a chart.
- `clinical_practice.teaching-material.json`, `.practice-administration.json` — the two remaining
  in-family rows this one could steal from.
- `legal.practice-matter-file.research.md` (24KB) — the structural analogue.
- `business_operations.organisational-records.json` — read for refusal quality, because the charge
  against this row is precisely that it could become that.

---

## What this row is for — and the sentence that has to hold

The longitudinal record a practice keeps **about one other person**: dated entries, consultation and
admission records, treatment and care plans, results filed against orders the holder placed, consent
forms the holder took, letters filed inward, discharge summaries, and the export or subject-access
packet the whole thing becomes when it is requested.

Two structural claims, and both are load-bearing:

**Notes and plans are the chart's own contents.** This is why `med.clinician-clinical-note` and
`med.clinician-treatment-plan` fold in rather than standing beside it. The schema anchor supplies
the general rule — *"A sibling justified only by 'we hold letters' is the schema's default template
with a narrower filename filter"* — and a note and a plan are `work_types` values, not worlds. That
fold is also the precedent `case-conference` had to defeat to exist, which it did, on cardinality;
see below.

**"About one other person" is a cardinality, and it is doing real work.** It is what distinguishes
this row from `case-conference` (many subjects in one artefact), from `practice-administration`
(often no subject at all), and from `protocol-guideline` (a class of patients, never a person). It
is also the clause that stops this row becoming a residual, which is the next section.

---

## The charge: is this a residual wearing a domain's clothes?

Taken seriously, because it is the dispatch's warning and because the shape that failed for
`business_operations.organisational-records` is genuinely available here. That row's refusal reads:
its only candidate signal was *"an organisation name plus a document-type word"*, and *"A row whose
entire support is never-alone evidence can never clear activation."*

The parallel charge against this row would run: *its only candidate signal is a person's name plus a
clinical document-type word, and both are never-alone; so it can never clear activation either, and
"everything about a patient" is Protected Records with a nicer label.*

**It does not hold, and the reason is that this row's signal is a two-place structure, not a token.**

`00` states the never-alone problem in the form the refusal quoted, about a university:
*"A university name alone should not create a group because Columbia can appear as an authoring
school, course provider, target institution, employer, research venue, or merely a cited
organization."* The failure there is **role ambiguity** — one token, many possible roles, no way to
choose. This row's activation is the opposite construction: it requires two person-shaped blocks
whose **roles are separately labelled and filled by different people**. The ambiguity `00` describes
is exactly what the second block resolves. A row supported by a *relation between two labelled
roles* is not a row supported by never-alone tokens, even though each of its tokens is never-alone
on its own — and the JSON says so token by token, listing the clinical headings, the record-number
token, the facility gazetteer hit, the folder name, the session membership and the PDF author string
as never-alone, seven entries deep, before any of them is used.

That is the difference in one line: **`organisational-records` had nothing left after you deleted its
never-alone evidence. This row has the whole of its recognition left.**

But the charge lands partially, and I am recording where. **The residual risk is not in activation;
it is in scope.** A chart is defined by accumulation, and accumulation is an appetite: every document
that mentions the patient is *filable*. Nothing in the structure stops this row from swallowing the
referral register, the incident pack, the conference outcomes and the administrative traffic, since
copies of all four legitimately sit in real charts. The discipline has to come from the boundaries,
not from the definition — which is why the next section is the longest in this memo, and why four
edges were added to the JSON in this pass rather than one.

---

## The node test, leg by leg

CONNECTION §2: *"A **template** row exists only if its detection signals, recommended dimensions, or
privacy rules differ from its schema's default template."*

### Leg 1 — detection signals: **passes, and carries the row**

Measured against the schema's stated default, not against a vague sense of it. The schema's own
signals are the two-role structure, the batched multi-subject structure, and direction of address.
This row narrows one of them and adds one no sibling has:

1. **Longitudinal accumulation about a single named subject.** Several dated entries about the
   **same** person, in one artefact or in one directory read through P3 parent-folder context, over
   months. This is not a narrower filter on a schema signal — the schema's batched signal requires
   the subject to **change** between items, and this one requires it not to. They are disjoint.
   `00` supplies why the structure is readable at all: *"Tables matter because resumes, forms,
   applications, invoices, and administrative documents often place their most useful information in
   cells rather than body paragraphs."*
2. **The practice-system record header** — a printed-by or exported-by slot naming the holder beside
   a patient banner, in a high-weight zone: *"It should use positional weighting because a value in
   a filename or document title carries more meaning than the same value in a footer or a late body-
   page reference."*
3. **The filed-result direction** — a report whose header names an **ordering** clinician who is the
   holder, filed against a subject who is not. The direction of the request is the evidence, not the
   laboratory letterhead. Note what this rules out, and it is `medical`'s own fixture: PHR carries
   `Lab Results - CBC - 2026-03-14.pdf` and recognises it by *"the result-and-reference-range
   structure"*. The same bytes with the same table are that row's when the holder is the subject.
   **Neither side reads the table itself as its evidence**, and this row does not either.

Verdict: **passes.** Signal 1 is the row.

### Leg 2 — privacy rules: **passes, and passes hardest of the three**

Two rules here are not the family default's, and one of them is not any other row's on the roster.

**Third-party density.** The schema anchor states the general prohibition on a patient level. This
row is the case that prohibition was written for: its natural organising dimension, in the source
practice system, *is* the patient. The anchor names it — this row is *"the row most tempted by it"*.
So the strongest form of the family rule lives here, and it is not inherited flavour; it changes the
template recommendation, which is what leg 2 asks.

**Aggregation as the harm, not any one document.** A chart is dangerous because it is *assembled*.
`00` names the corpus material — it *"can include identity documents, account statements, tax
records, medical information, legal records, credentials, private correspondence, GPS metadata,
employment materials, and educational records"* — and requires the immediate transition:
*"A scanned passport, tax statement, medical document, authentication key, or account record should
enter a protected state immediately."* The operative limits are `00`'s:
*"Protected material should not be included in cloud-model prompts by default, should not display
raw content in general group summaries, and should not be moved automatically without a user policy
that explicitly permits it."*

The asymmetry that makes this row's version stricter than `medical`'s is one `00` states about
revocation and does not resolve for third parties: *"Revocation cannot necessarily retract data
already sent to an external provider, so the product must communicate that distinction clearly."*
The person to whom that would need communicating is, here, not present, cannot review the canvas,
cannot correct a wrong grouping, and gains nothing from the tidying. **Marked as inference** — `00`
does not discuss practitioner-side custody anywhere.

Verdict: **passes.**

### Leg 3 — recommended dimensions: **unsatisfiable for this family, and not quietly satisfied**

`template.dimension_order` is `[]`, and it is empty for two independent reasons, only the first of
which is about this row.

**By contract**, a dimension may only branch on a field the same entry's schema declares, and
`clinical_practice` declares none (`_CONTRACT` rules 10 and 15, CONNECTION PR-6, D1 as narrowed).
So this leg **cannot differ from the schema's default template, for this row or for any of its ten
siblings**, because the default is empty and so is every sibling's. The schema anchor recorded this
about its own field leg and refused to pretend otherwise; the template-side counterpart is recorded
here in the same terms rather than skipped. **If R1c reads §2's dimension clause literally, this leg
fails identically for all eleven rows in the family**, and it is a family-wide question, not this
row's to answer. Filed as NJ-CP-DIM below.

**By privacy**, and this is the part that survives even if D1 lifts: the dimension this situation
obviously wants is THE PATIENT, and a folder named for a patient publishes a third person's identity
and the fact of their care in the filesystem namespace. `00` argues against person-shaped dimensions
even for the user's own material — *"It should avoid using authorship or creator identity as a
destination dimension."* — and requires redaction in the product's own surfaces:
*"Protected branches should have configurable redaction in the canvas and review screens"*.

So the honest statement of the empty template is: **it is empty for a contract reason that proves
nothing about this row, and for a privacy reason that would keep it empty anyway.** The recommendation
held as prose, for whoever answers the schema row's open question: document function would precede
time, and a subject level would remain off by default. Not time-first — *"For document and record
domains, project, function, or subject usually comes before time because putting year first scatters
related work across calendar folders."*

**Overall: kept, on legs 1 and 2, with leg 3 recorded as unsatisfiable rather than satisfied.** The
gist verdict is confirmed, not reversed — but it is confirmed on two legs rather than three, and the
JSON's `open_question` already says the harder version of this out loud.

---

## What is NOT in this row

The dispatch's actual charge. Each line names the owner, and each is reciprocal — stated the same way
on the other side, or flagged where the other side has not landed.

| Material | Not this row, because | Owner |
|---|---|---|
| A document naming the **holder** in the patient slot, however clinical its letterhead | the roles are reversed; there is no author sign-off naming the holder as clinician | `medical.personal-health-records` |
| An **outbound** letter tracked by an addressee, a copies-to line, a sent/acknowledged status, or a reply pairing | the anchor is the correspondence item and its direction, not the accumulated record | `clinical_practice.referral-correspondence` |
| An artefact whose subject **changes between items** — an MDT agenda, a theatre list, a handover sheet | a work type of a one-subject record cannot fan out to eleven subjects; the sibling's decisive argument, and it is correct | `clinical_practice.case-conference` |
| An **incident** reference, complaint, letter of claim, indemnity schedule, or expert report | the holder's own jeopardy is the anchor, not the subject's care record | `clinical_practice.malpractice-incident` |
| Procedural traffic **about** the record — a records-request acknowledgement, a chase, a retention schedule, a transfer-out cover sheet | it carries a patient banner and no account of care | `clinical_practice.practice-administration` |
| An **age-and-sex descriptor** in place of an identifier, plus learning objectives | de-identified by construction; there is no subject to accumulate about | `clinical_practice.teaching-material` |
| Instruction about a **class** of patients — a guideline, a pathway, a safety alert | no named person at all, and therefore an *unprotected* residual | `clinical_practice.protocol-guideline` |
| A **household** record about a child or dependant, with no professional authorship | a relationship, not a custody role | `medical.dependant-child-health` |
| The holder's **own** registration, appraisal, CPD log or CV | no third-party subject appears | `career` / `clinical_practice.licensure-credentialing` |
| A **medico-legal report** commissioned by a solicitor, evidenced by an engagement record or a firm matter identifier | the commission is the anchor; the clinical body is not | `legal.practice-matter-file` |
| An **unreadable** practice export, an encrypted record store, an untranscribed dictation | the schema never activates, so it is a residual case rather than this node's file | Unsupported or Encrypted |
| A chart-shaped document whose **author-versus-subject role is unresolved** | correct abstention, and the answer is neither row | Review Later |

The pattern worth stating once: **seven of those twelve are lost to in-family siblings**, not to
`medical` and not to residuals. The residual risk in this row is intra-family, and that is why the deepening
added three in-family edges.

---

## Files considered and rejected

A row that only lists what it holds has not been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| **`SOAP template blank.docx`** (kept in the JSON, as the collision fixture) | Every documentation heading, a practice logo, and clinician author metadata — and **no subject and no completed entry**. This is the over-firing fixture. `00`: *"PDF metadata should be treated as supporting evidence, not as truth"* — a practice template names its author on every blank form it ever generated. |
| **`After Visit Summary.pdf`** (kept, as the *reciprocal* fixture) | Identical bytes-level shape to a letter a clinician wrote. The holder is in the patient slot; there is no author sign-off. `medical.json` names these bytes too, deliberately, so both sides point at the same artefact. **Not disturbed in this pass.** |
| **`case 4 - 68yo with chest pain.docx`** (kept) | A full documentation structure with an age-and-sex line where an identifier would be, and learning objectives at the end. `clinical_practice.teaching-material`'s, and `00` supplies the test: *"Topic answers what a file is about, while purpose answers what the file was for."* |
| `Lab Results - CBC - 2026-03-14.pdf` | PHR's own fixture. A result-and-reference-range table is not this row's signal; **the ordering direction is**, and this file has no ordering clinician who is the holder. Not re-fixtured — naming it here would imply this row contests bytes it does not. |
| `Records_Request_Fulfillment_2026-06.zip` | Genuinely contested with PHR, and the JSON keeps its own `subject access request - full record.zip` rather than duplicating PHR's filename: same shape, opposite custody. Both sides refuse extraction — *"the normal scan should never extract archive contents to the filesystem"*. |
| `Patient_Summary_CCD.xml` | A structured continuity-of-care document. `code_structured` on PHR's side, about the holder. On this side it would be a chart export — but a CCD is *generated from* a chart, not a chart, and it carries no accumulation. Rejected: it teaches nothing the `.zip` fixture does not. |
| A DICOM study / `IM-0001-0001.dcm` | Already carried honestly on `medical.json` as `opaque_binary`. Imaging belongs to a chart by **filing**, not by structure, so it is not this row's recognition evidence. |
| `MDT outcomes 2026-05-14.xlsx` | The case-conference sibling's fixture. Deliberately **not** claimed here; the chart-side mirror is the `Consultation 2026-05-15.docx` bytes instead — see below. |
| A practice `.vcf` or contacts export | `00` settles it: contact material is *"privacy-protected rather than used to create folder proposals"*. A patient list in an address book is not a chart. |
| A hospital payslip or Trust employment contract | Employer-shaped, about the holder, no third-party subject. `career`. The gazetteer hit on the hospital name discriminates nothing. |
| A wearable export, a gym plan, a nutrition photo | Holder-owned, no author role, no third party. `medical.wearable-health-exports` / `medical`. |
| An appointment reminder `.ics` | CONNECTION-EXAMPLES fixture 5 is the reason this cannot fire on `source_type` alone, and PHR already carries the calendar case with the correct caveat — a calendar item is not proof an encounter occurred. Not duplicated. |

---

## The collision fixture — in both directions

### Over-firing: `SOAP template blank.docx`

Preserved from the gist draft unchanged, and it is the right fixture. Every deterministic signal is
present except a filled subject. What discriminates: **the subject block must be filled, by a person
different from the author.** The JSON's `must_not_conclude` makes the negative checkable rather than
merely asserted, and this pass added the matching `never_alone` entry from the *other* direction —
a filled subject block with **no author role beside it** is the holder's own record, which is the
mistake this row makes more often in real corpora than the blank-template mistake.

### Under-firing: `After Visit Summary.pdf`

Clinic letterhead, visit date, medication table, prose instructions in the second person. The named
person in the patient slot is the holder. What discriminates is the holder's **role**: subject →
`medical`; author beside a different subject → this row; letterhead alone → neither, and neither is
the right answer. *"Correct abstention is a successful outcome because the product's goal is
reliable organization, not maximum file movement."*

**The same bytes are named on both sides.** `medical.json` carries them with the medication-table
observations; this row carries them with the extra observation that makes the negative checkable —
no author sign-off naming the holder as clinician — and a `must_not_conclude` naming
`medical.personal-health-records` as the true home. *Preserved untouched.* One note for R1c: the
landed `medical.personal-health-records.json` fixture is named
`After Visit Summary - 2026-03-14.pdf`, while `medical.json`, `clinical_practice.json` and this row
all use `After Visit Summary.pdf`. Same artefact, three files agreeing and one dated variant. Not a
contradiction; worth normalising, and **not mine to edit**.

### The third direction, added this pass: `Consultation 2026-05-15.docx`

The case-conference sibling added these bytes as **its** under-firing fixture — one subject, dated
entries, a pasted meeting paragraph in the newest one — and its memo states, correctly, that the
mirror on this side was outstanding. This pass authored it. The same file now appears on both rows
with the same discriminator: **cardinality and container, not text.** The meeting text is quoted
*into* the chart; it does not carry the chart out.

---

## Reciprocal boundaries

Every neighbour this row could steal from, both directions, contested bytes named.

| Neighbour | This row must **not** take | The neighbour must **not** take | Shared fixture bytes |
|---|---|---|---|
| `medical.personal-health-records` | a document naming the holder in the patient slot, or second-person instructional prose addressed to the holder | a clinician-authored entry, plan or filed result merely because it is clinical and identifies a person | **`After Visit Summary.pdf`** — named on both sides; the sign-off block is the discriminator |
| `clinical_practice.referral-correspondence` | an addressee block, a copies-to distribution, a sent/acknowledged status, a reply pairing | the same letter sitting inside one subject's accumulated record under a filed-on slot | **`Referral Letter - Orthopaedics.pdf`** (added) — a three-way artefact, also PHR's own fixture |
| `clinical_practice.case-conference` | a meeting header with attendance, apologies and several named subjects | a one-subject longitudinal record, however much meeting text is pasted in | **`Consultation 2026-05-15.docx`** (added, mirroring the sibling) beside `MDT outcomes 2026-05-14.xlsx` |
| `clinical_practice.malpractice-incident` | an incident reference, a complaint, a letter of claim, an indemnity schedule, an expert report | routine dated entries about one subject under a responsible-clinician sign-off, merely because they narrate the same event | a duty-of-candour letter — filed into both, and P10 chooses |
| `clinical_practice.practice-administration` | a procedural request or return concerning a record's handling | a dated clinical entry, plan or filed result about the subject | a records-request cover sheet carrying a patient banner |
| `clinical_practice.teaching-material` | an age-and-sex descriptor, initials, learning objectives, discussion questions | a real named subject with a date of birth or record number beside an author role | a completed case write-up; the discriminator is purpose, not topic |
| `medical.dependant-child-health` | a household relationship with no professional authorship | an author-role or practice-system custody structure | a record about a third person — which alone discriminates neither |
| `legal.practice-matter-file` | a signed engagement record, a firm matter-system identifier, counsel work product | a clinical account by the holder about a person in the holder's care | a medico-legal report — clinical body, legal commission |

**Reciprocity status, verified by grep across `nodes/` in this pass:**

- `clinical_practice.referral-correspondence` **names this row** and is named back. Reciprocal, both
  directions, and neither side is contradicted.
- `clinical_practice.case-conference` **names this row**. Its memo states that *"`patient-chart`
  names this row already"* — **it did not.** I checked `collides_with` on this file before this pass
  and it held four edges, none of them the sibling. The claim was wrong; the edge now exists,
  authored on this side, saying what the sibling says. Recorded rather than silently fixed, because
  the addendum asks for auditability and because R1c should know one sibling's reciprocity claim was
  unverified.
- `clinical_practice.malpractice-incident` and `.practice-administration` do **not** name this row.
  Both edges are authored one-way here, knowingly. **R1c owes the reciprocals.**
- `medical.personal-health-records` does **not** name `clinical_practice` anywhere — neither its JSON
  nor its 22KB memo mentions the family. Verified by grep in this pass; I did not edit it. This is
  NJ-CP-1 and it is unchanged from the gist draft, which was right about it.
- `legal.practice-matter-file` does not name this row. One-way, knowingly.

---

## `proposed_fields` — deliberately empty, and that is the argument

**None.** The one fact this world needs — the person a record is *about* — is proposed exactly once,
as **`subject_of_record`**, on the schema row, for R1c. `canonical_fields.json` holds nothing that
can carry it: `authored_by` is the *opposite* role and the one the holder occupies; `client` is a
commercial counterparty whose `role_split` partner is `our_firm`; `people` is the photos-side
co-occurrence facet; `institution` is the facility, not the person; `record_type` is scoped to a
financial record kind.

I confirmed the reuse rather than minting a variant, and I did not re-propose it here. The schema
anchor sets the discipline explicitly — duplicating the question ten times would give R1c eleven
near-identical proposals to reconcile instead of one — and `career.credentials-licenses` set the
same precedent. **Proposing it again on this row would be this row answering a decision that is not
its own.**

One thing this row can contribute to R1c's adjudication, from having read the structural analogue:
the anchor's argument that the two families **break at the `client` key** is confirmed from this
side. `legal.practice-matter-file` can lean on `client`/`our_firm` because a legal client genuinely
is the engaging counterparty. A patient is not the client of the person writing about them — the
letter is usually addressed to a *third* clinician and the payer is frequently a fourth party. The
`legal` memo's own note that *"`client` and `our_firm` are canonical engagement-role keys, but the
Legal schema does not reference them"* means even that family has not spent them. The analogy holds
for the two-role **structure** and fails for the **key**, and R1c should not read the two families'
consistency as licence to reuse `client` here.

---

## Neighbours considered that did NOT get an edge

- **`clinical_practice.protocol-guideline`** — the family's mirror row, and the contrast is
  instructive (instruction about a class of patients, no subject, therefore Reading Inbox rather
  than Protected Records). But there are no contested bytes: a guideline has no subject block at
  all, so nothing can be taken in either direction. An edge would state a non-collision.
- **`clinical_practice.pharmacy-operations`** — a dispensing entry is a chart `work_type` on this
  row and a register entry on that one. Real, but the sibling's anchor is the statutory register
  structure, which this row has no version of. Left to R1c rather than pre-empted; **flagged here so
  it is not lost.**
- **`legal`** (schema) — appears as `also_schema` on the subject-access-request archive, since a
  records request is a legal instrument. No edge row: `also_holds_with` joins **schemas only**
  (CONNECTION §5) and this is a template, so the pair is carried on `clinical_practice.json`.
- **`photos`** — appears as `also_schema` on the phone-photo fixture, which carries real EXIF facts
  from the photos schema on its own evidence. The co-activation is already carried on the photos
  side. CONNECTION §8: an unasserted pair means unasserted, not false.
- **`academic`** — a student's clinical logbook is chart-adjacent, but the discriminating evidence is
  academic context, and the collision is already stated at schema level.
- **`identity`** — a chart contains identity data but is not an identity document. That confusion
  lives on `licensure-credentialing`, where the card-shaped files are.
- **`business_operations.meeting-record`** — names `case-conference`, not this row, correctly. A
  chart is not a meeting artefact and the sibling is the right intermediary.

---

## Sparse-file discipline

Four of the eleven fixtures carry `group_without_copying_facts: true`, and seven of the eleven carry
an explicit no-fields line in `must_not_conclude` — either `"any clinical_practice fact - none is
declared"` or `"the schema declares no field rows"`. **The other four do not, and that is a gap, not
a design:** `SOAP template blank.docx`, `After Visit Summary.pdf`, `case 4 - 68yo with chest pain.docx`
and `chart.enc` each carry a *non-activation* `must_not_conclude` instead, which implies the fields
point without stating it. I checked this rather than assuming it, and I did not paper over it by
editing four fixtures whose existing negatives are correct and load-bearing. **R1c: four one-line
additions** would make the placeholder status checkable file-by-file across the whole set. The multi-subject results extract,
the unextracted export, the encrypted store and the phone photo are all cases where the
neighbourhood may legitimately group a file while **no** clinical fact is written onto it —
*"The graph does not automatically copy those missing facts onto sparse files."*

---

## NEEDS-JOSEPH

- **NJ-CP-1 · The clinician-authored versus patient-held boundary, stated reciprocally.**
  *Preserved from the gist draft, still open, and re-verified.* This row's `collides_with` names
  `medical.personal-health-records` and gives the discriminator. The landed
  `medical.personal-health-records.json` **does not name `clinical_practice`** — nor does its memo.
  R1c owes the reciprocal on the medical side; until it lands the boundary is asserted from one side
  only. *Alternatives:* (a) R1c adds the edge — cheap, and the shared `After Visit Summary.pdf` bytes
  are already named on both sides, so it is one entry, not research; (b) leave one-way — cost is
  that a PHR-first classification never learns the sign-off discriminator exists.

- **NJ-CP-DIM · The dimension leg of the template node test is unsatisfiable for all eleven rows in
  this family.** *New in this pass.* CONNECTION §2 requires a template to differ from its schema's
  default on signals, dimensions **or** privacy. `clinical_practice` declares no fields, so every
  template on it has an empty `dimension_order` by contract and **cannot** differ on that leg. Read
  literally, the leg fails identically for the schema's default and all ten siblings. This row
  passes on the other two legs and does not need it — but R1c should decide the reading, because a
  family-wide unsatisfiable leg is a roster fact, not eleven independent coincidences.
  *Alternatives:* (a) read §2's "or" as genuinely disjunctive and record the leg as inapplicable for
  field-less schemas — cheapest and matches what the schema anchor already did with its own field
  leg; (b) treat it as a failure and re-examine all eleven — would refuse rows that are clearly
  distinct on signals and privacy; (c) lift D1 for this family — out of scope and much larger.

- **NJ-CP-3 · May a practitioner-side chart be OFFERED a physical destination at all in v1?**
  *Preserved, and it is the one this row most wants answered.* Any branch that groups chart material
  is a branch whose existence discloses a caseload; any branch that does not group it is not a chart.
  Represent-in-place under Protected Records is a defensible **permanent** answer here, and unlike
  every other placeholder row on this roster this question does **not** depend on whether the schema
  ever gets field rows. *Alternatives:* (a) never offer a destination — safest, and costs the user
  the organisation they installed the product for; (b) offer one shallow user-approved packet with no
  automatic internal depth, which is what the JSON currently recommends — costs a folder whose name
  discloses that a caseload exists, though not whose; (c) offer depth on document function only —
  costs little privacy and delivers little value, since function is usually already the source
  system's own structure. This is a decision about someone's real professional obligations, not a
  fact about files. Joseph's.

- **NJ-CP-RECIP · Three edges authored one-way.** `malpractice-incident`, `practice-administration`
  and `legal.practice-matter-file` do not name this row. All three are one-line additions on their
  side, not research tasks. R1c.

---

## What changed in this pass

Cross-checked against the JSON as written, not against intent.

**In `clinical_practice.patient-chart.json` — six changes, all additive:**

1. `one_line`: `"Gist-level placeholder (J-IND)"` → `"Full-depth placeholder (J-IND, written to
   J-DEPTH)"`, matching the deepened sibling `clinical_practice.case-conference`. One phrase; nothing
   else in `one_line` was touched.
2. `recognition.never_alone`: **one entry added** (now 8), at position 2 — *a filled subject block
   alone, with no author role beside it.* The seam read in the direction this row actually fails.
3. `collides_with`: **four entries added** (4 → 8) — `clinical_practice.case-conference` (the
   reciprocal the sibling wrongly believed already existed), `.malpractice-incident`,
   `.practice-administration`, and `legal.practice-matter-file`.
4. `file_examples`: **two entries added** (9 → 11) — `Consultation 2026-05-15.docx` (the shared-bytes
   mirror of the case-conference fixture) and `Referral Letter - Orthopaedics.pdf` (the three-way
   artefact shared with PHR and `referral-correspondence`), the latter falling through to
   `Review Later` rather than `Protected Records`, since an unresolved role is exactly that residual's
   case.
5. `proposed_fields`: **unchanged, still `[]`** — deliberately, and now argued rather than asserted.
6. `template.dimension_order`: **unchanged, still `[]`**; `fields`: **unchanged, still `[]`**;
   `launch`: **unchanged, `"placeholder"`**; `refuse_node`: **unchanged, `false`**. Recognition
   `deterministic` and `needs_llm`, `work_types`, `grouping_reasons`, `sensitivity`,
   `sensitivity_why`, `falls_through_to`, `open_question` and the nine original fixtures were
   **preserved verbatim.**

**In this memo:** rewritten from 4.9KB. Added the residual charge answered against
`business_operations.organisational-records`'s refusal; the node test argued leg by leg with leg 3
recorded as unsatisfiable rather than satisfied; a twelve-row *what is NOT in this row* table; a
twelve-row files-considered-and-rejected table; the collision fixture in three directions; an
eight-row reciprocal boundary table with grep-verified reciprocity status; the `proposed_fields`
zero argued, including the `client`-key finding read back against `legal.practice-matter-file`;
seven neighbours considered without an edge; and NJ-CP-DIM and NJ-CP-RECIP as new open questions.

**Reversed:** nothing. The gist verdict — the row stands — is confirmed, on two legs of three, with
the third recorded honestly. **Corrected:** one factual claim in a sibling's memo, that this row
already named `case-conference`. It did not; it does now.
