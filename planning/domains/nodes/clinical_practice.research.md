# `clinical_practice` — lab notes (schema row, J-IND row deepened to J-DEPTH)

Node: `clinical_practice`, `kind: schema`, `launch: placeholder`, `fields: []`.
Output: [`clinical_practice.json`](clinical_practice.json). No other file was written.

This memo replaces the gist-depth memo written under the retired `Depth: GIST` label. The JSON it
describes was **not** rewritten: its facts were verified and its key set is house-correct, so this
pass preserved it and added three things (listed in *What changed in the JSON*, at the end). What
was missing was never the JSON — it was the argument behind it, and that is what follows.

**This is the schema row for an eleven-row family, and it is written to be read first.** Ten sibling
templates point `uses_schema` here. Each of them exists only if it differs from *this row's* default
template, detection signals, or privacy rules, so those three things are stated below explicitly and
in one place, rather than left to be reconstructed from the JSON.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — the authority, and the only document quoted
  inside quote marks. Every quoted span in `clinical_practice.json` and in this memo was
  `grep -cF` verified against it; 23 quoted spans in this memo and every curly-quoted span in the JSON checked in this pass, all present verbatim,
  zero misses. No section numbers are attributed to `00`, because `00` is prose.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/_CONTRACT.md` (rules 5, 10, 14, 15 bind this
  row); `planning/domains/CONNECTION.md` (§2 node test, §4 steps 3/5, §5 edge table + invariants,
  §8, PR-2, PR-4, PR-6, PR-8); `planning/domains/CONNECTION-EXAMPLES.md` (fixture 5, the `.ics`
  case, is the reason the calendar fixture on this row does not activate on `source_type` alone).
- `planning/domains/canonical_fields.json` — searched for a key that could hold *the person a
  record is about*. There is none. That search is the whole of the `proposed_fields` argument below.
- `planning/overnight/council/DECISION-BRIEF.md` — D1, D6 and J-IND read as **ratified** and not
  re-argued.
- `planning/domains/ROSTER.md` §4 line 80, §5, NJ-J-IND-4 (line 311), Appendix A lines 589–604 —
  the legacy folds this row owns: the whole `med.clinician-*` block, `med.clinical-protocol-guideline`,
  `med.medical-teaching-material`, `med.practice-administration`, `med.pharmacy-operations`,
  `med.veterinary-practice`, and the residual disposal of `med.veterinary-pet-owner`.
- `src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`. No `source_type` was invented.

### Landed neighbours read before writing, and not edited

- `nodes/medical.json` + `medical.research.md`, and `medical.personal-health-records.json` — the
  nearest neighbour, a landed launch row at full depth, read in full. The reciprocal fixture with it
  is the most important sentence in this memo.
- `nodes/legal.practice-matter-file.json` + memo — the **structural analogue**: a practitioner's
  file about another person, field-less, and distinguished by holder role rather than by content.
  Read specifically to check that the two families say the same thing about the two-role structure.
- `nodes/creative.json` + `creative.research.md` — the model for what a J-DEPTH *schema* row owes
  its siblings (a stated default template, a stated seam, a named collision fixture).
- `nodes/career.json`, `career.credentials-licenses.json` — the precedent for a field-less
  placeholder that still carries recognition, work types and a stated-empty template, and the
  neighbour `clinical_practice.licensure-credentialing` competes with.
- `nodes/business_operations.organisational-records.json` — read for refusal quality only.
- The ten landed `clinical_practice.*` sibling rows, re-read at the end of this pass to check the
  default template below actually discriminates them. It does; the result is recorded under
  *Measuring the ten siblings*.

Key set and key order in `clinical_practice.json` match `medical.json` exactly (same 27 keys, same
order). That is deliberate: the two rows are role-reverses of each other and a reader should be able
to diff them.

---

## What this world is FOR

`medical` is the safety domain for **the holder's own** health material. This row is its role-reverse:
the holder is the **author and custodian** of material **about other people**.

That single reversal is the entire licence for the row. It is worth being precise about why it is not
merely a size difference. A clinician's corpus is not "a large `medical` corpus":

1. **The privacy owner changes.** In `medical`, the sensitive party is the user — the person who
   installed the product, who can review its proposals, who can revoke, and who benefits from the
   organisation. Here the sensitive party is a third person who never chose this filesystem, cannot
   see the canvas, cannot correct a wrong grouping, and gains nothing from the tidying. `00` is
   blunt about the limit of the remedy that exists — *"Revocation cannot necessarily retract data
   already sent to an external provider, so the product must communicate that distinction clearly."*
   — and the person to whom that distinction would need communicating is, here, not present.
2. **The document set changes**, even where the document *types* coincide. A patient holds results
   filed to them; a practitioner holds requests issued, results filed against them, letters sent
   onward, lists covering many people at once, and obligations owed to a regulator. The batched
   multi-subject document (a clinic list, a theatre list, an MDT deck) has no counterpart at all on
   the `medical` side.
3. **The failure mode changes.** A missed `medical` file exposes the user to themselves. A missed
   `clinical_practice` file can put another person's identified clinical narrative into a cloud
   prompt or a shared folder name.

Provenance discipline: point 1's second half and points 2 and 3 are **inference**. `00` does not
discuss practitioner-side custody anywhere. Everything asserted from `00` in the JSON is asserted
only as `00` wrote it, and every extension is marked `inference` at the point of use.

---

## Did this row survive the node test?

`kind: schema`, so CONNECTION §2's test is: *is the field set genuinely distinct, or is it a subset
or respelling of an existing schema's?* All three legs, argued separately, and one of them does not
pass.

### Leg 1 — a distinct field set: **unsatisfiable, and I am not going to pretend otherwise**

This row declares **no fields at all**, so the leg cannot be run as written. That is not evasion; it
is what three documents that outrank the dispatch prompt require:

- `_CONTRACT` rule 15: *"A placeholder schema (career, identity, medical, legal) may carry
  `schema: []` — a row may describe the domain and still write no field rows"*, with rule 10
  standing.
- CONNECTION PR-6: placeholder schemas exist as `kind: schema` rows with an empty field list.
- J-IND, ratified: the new professional schemas are placeholders that describe a domain without
  minting fields.

So the honest statement of leg 1 is: **it is unsatisfiable for this row, and would be unsatisfiable
in exactly the same way for every J-IND placeholder schema.** If R1c reads the schema node test
literally, this row fails it — and so do `hr`, `law_practice` and every other J-IND schema,
identically. That is a roster-wide question, not this row's to answer, and it is *not* quietly
satisfied by pointing at the one field the world needs. The field is filed as a **proposal for R1c**
(below), which is a request for adjudication, not a satisfied check.

What can be said, and is the actual argument for the row existing: **the concept the field set would
be built on is unheld by any existing schema.** `medical`'s field set (if D1 ever lifts) would be
built on *the holder's* record. This row's would be built on *someone else's*. A schema whose central
fact is a different person is not a subset or a respelling of one whose central fact is the user —
which is the thing §2's first bullet actually forbids. Leg 1 is recorded as **not passed, argued**,
and carried as `open_question` (2) and NJ-CP-FIELD.

### Leg 2 — detection signals of its own: **passes cleanly, and carries the row**

Three signals in `recognition.deterministic` belong to no other schema in the roster:

1. **The two-role structure.** A clinical narrative whose signature, sign-off, letterhead or
   practice-system printed-by block names the holder as the **author**, beside a *separately
   labelled* block naming a **different person** as the subject. Two person-shaped blocks in two
   different labelled roles. Neither block alone is anything: `medical` has the patient block,
   `career` has the sign-off, and only this row requires both, filled, by different people.
2. **The batched multi-subject structure.** One document holding a repeated per-person block —
   a clinic list, a theatre list, a handover sheet — several named subjects under one date and one
   facility. A patient's own record is about one person; a practitioner's working document is
   routinely about many. `00` supplies the reason this is readable at all: *"Tables matter because
   resumes, forms, applications, invoices, and administrative documents often place their most
   useful information in cells rather than body paragraphs."* No other schema in the roster has a
   fixture whose sensitivity scales with its **row count**.
3. **Direction of address.** An addressee block naming a clinician or practice *other than* the
   holder, a subject line naming a third person, and a sign-off naming the holder. The `medical`
   side's letters point the other way — addressed *to* the holder. Direction, not vocabulary, is the
   evidence.

Verdict: **passes.** These signals are what the row is for, and none of them depends on the field
question.

### Leg 3 — privacy rules of its own: **passes, and passes harder than the field leg fails**

Two rules here are not `medical`'s:

- **The dimension prohibition is stronger.** `medical`'s empty template is justified because a
  condition or provider label would publish what protection exists to hide, for the user. Here the
  same label would publish it **for someone else**, and the user cannot consent on their behalf.
  Same rule, strictly stronger case.
- **Bulk sensitivity.** A clinic list is not "one file's worth" of exposure; it is N people's. The
  theatre-list fixture carries `"that a list is low-risk because each row is short: a multi-subject
  list is bulk-sensitive as a whole"` in `must_not_conclude` for exactly this reason. `medical` has
  no analogous rule because a patient's own record is never bulk.

And one ordering consequence that is a genuine gap, not a rule: `CONNECTION` §4 step 5's
protect-before-model ordering is keyed to `is_safety_domain`, which this row does not carry. The row
therefore states the requirement in prose from `00` — *"Privacy policy must be enforced before
content reaches any model or external connector."* — and files the gap as NJ-CP-SAFETY.

Verdict: **passes.**

**Overall: kept, on legs 2 and 3, with leg 1 recorded as unsatisfiable rather than satisfied.**
Two of three is not a comfortable margin, and the row says so in its own `open_question` rather than
in this memo only.

---

## The default template, stated for the ten siblings

`template.dimension_order` is `[]`, and it is empty **twice over** — the JSON says so, and the two
reasons are independent:

1. **By contract.** A dimension may only branch on a field the same schema declares, and this
   schema declares none.
2. **By privacy, independently of (1).** Every dimension this world would naturally take — the
   patient, the condition, the specialty, the incident — becomes a visible folder **label**, and
   here that label names a third party. `00` pushes the same way inside the product's own UI:
   *"Protected branches should have configurable redaction in the canvas and review screens"*.

Reason (2) is the one that matters for siblings, because it survives even if D1 lifts. **A sibling
that proposes a `dimension_order` is proposing a folder label, and must answer reason (2), not just
reason (1).**

The recommendation held as prose — **this is the paragraph a sibling must differ from**:

> The **professional situation** (a caseload, a credentialing cycle, an incident, a correspondence
> register) → the **document function** within it. **Never** a patient level. **Never** a diagnosis
> or condition level. **Not time-first.**

Why each clause:

- **Situation before function**, because `00` puts subject/function above time for record domains:
  *"For document and record domains, project, function, or subject usually comes before time because
  putting year first scatters related work across calendar folders."*
- **Never a patient level.** This is the single most important line in this memo for a sibling
  author, and `clinical_practice.patient-chart` is the row most tempted by it — its whole material is
  organised, in the source practice system, by patient. `00` states the principle for creator
  identity — *"It should avoid using authorship or creator identity as a destination dimension."* —
  and a patient level is the stronger case, because the named party is not the user.
- **Not time-first**, and no sibling in this family may claim otherwise. `00` grants the time-first
  exception to capture-based media, and nothing in this world is capture-based. A clinic list dated
  2026-04-14 is not a capture event; a case-conference deck dated 14 May is not a photo shoot. A
  sibling claiming `time_first: true` is claiming the photos exception without the photos evidence,
  and R1c should reject it on sight. All ten landed siblings carry `time_first: false`.

**Differing in specialty is not a difference.** Cardiology, dermatology, oncology, midwifery,
physiotherapy, dentistry, optometry, veterinary medicine — these are *values*, not nodes. `00` says
where values come from: *"The system may create new values when it sees a new course, project,
company, university, or event, but it should not invent new fields automatically"*. A row per
specialty would be the 574's original mistake, rebuilt inside one family. The family has ten rows,
not a hundred, precisely because the discriminator is **situation**, never **specialty**.

**Differing in document type is not a difference either.** A letter, a note, a consent form, a
result, a certificate and a return are `work_types` on this row. A sibling justified only by
"we hold letters" is the schema's default template with a narrower filename filter.

### Measuring the ten siblings against it

Run at the end of this pass against the landed rows, and reported honestly:

| Sibling | Differs on | Verdict |
|---|---|---|
| `patient-chart` | the one-subject longitudinal accumulation; the strongest form of the "never a patient level" prohibition | passes |
| `case-conference` | multi-subject batching in a single artefact; a meeting-shaped grouping | passes |
| `referral-correspondence` | direction of address plus a register; the outbound file is a distinct situation | passes |
| `malpractice-incident` | an incident lifecycle, and a privacy posture that additionally touches the holder's own jeopardy | passes |
| `protocol-guideline` | inverse recognition — instruction *about* a class of patients, no subject at all, and therefore an unprotected residual (Reading Inbox) rather than Protected Records | passes, and is the family's mirror row |
| `teaching-material` | de-identified-by-construction material with the same vocabulary; a different privacy answer to identical text | passes |
| `pharmacy-operations` | a dispensing and accountability register with a statutory register structure | passes |
| `practice-administration` | the organisation rather than the person; many members carry no third-party subject at all | passes, with the caveat below |
| `veterinary-practice` | a **three-party** structure (practice / animal / owner) where the subject is not a person, so this schema's two-role signal does not read straight across | passes, and is structurally the odd one |
| `licensure-credentialing` | the holder's own standing — no third-party subject in most members | **weakest**; carries its own fold question against `career.credentials-licenses` |

The two the ten-row shape actually rests on are `practice-administration` and
`licensure-credentialing`: both are largely *subjectless*, and a subjectless row on a schema whose
defining signal is a second, differently-labelled subject is the shape most worth R1c's attention.
That, not the family's size, is the real question in `open_question` (4).

---

## The seam this family turns on, drawn explicitly

Siblings need one line they can apply. Drawn:

**The seam is not the vocabulary, the letterhead, the format, the record-number token, or the
clinical density.** A guideline PDF, a nursing lecture, a drug leaflet, a patient's own discharge
letter and a clinician's referral are *all* dense in clinical language, and several carry a clinical
letterhead. Any test built on vocabulary is wrong in both directions.

**The seam is the two-role structure**, and it is a checklist of observable blocks:

| What is observable | Reading |
|---|---|
| an author/responsible-clinician block naming the holder **and** a separately labelled subject block naming a **different** person, both filled | `clinical_practice` — the schema fires |
| a subject block naming the **holder**, addressed to them, no author role for them | `medical` — this schema must not fire |
| an author block naming the holder, subject block **absent or empty** (a blank template, a certificate, a registration notice) | this schema at most weakly, and usually `career` or Independent Records — see the collision fixture |
| **no** subject and **no** author role — clinical text only | not this schema. `clinical_practice.protocol-guideline`, `academic`, or Reading Inbox |
| a subject present but de-identified by construction, in an audience-facing artefact | `clinical_practice.teaching-material`, not `patient-chart` |

The load-bearing consequence for sibling authors: **the subject block being filled by a different
person is the activation, and the second role is what discriminates, not the first.** The row's
`never_alone` list carries this so it is checkable rather than merely stated: *"a person's name plus
a date of birth alone"* is listed precisely because that pair appears on the holder's own record, on
an identity document and on a school form, and *"What discriminates is whether a SECOND person
occupies the author role."*

---

## Files considered and rejected

A row that only lists what it holds has not been researched. The tempting false positives, and what
discriminates each:

| File | Why it is **not** this row's evidence |
|---|---|
| **`Consultation letter TEMPLATE - blank.docx`** (added to the JSON in this pass as a fixture) | Every deterministic signal is present *except* a filled subject: letterhead, holder sign-off, registration number, the full history/examination/impression/plan skeleton. Discriminator: the subject slot is empty or holds a bracketed placeholder. This is the over-firing collision fixture — see the section below. |
| `Guideline - management of community-acquired pneumonia v4.pdf` (kept as a fixture) | Total clinical density, no named person, no author role for the holder. Belongs to `clinical_practice.protocol-guideline` and, when unaccepted, to Reading Inbox — *"Reading Inbox may hold papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* |
| `After Visit Summary.pdf` (kept as a fixture, **and named on `medical.json` too**) | Clinic letterhead, visit date, medication table — and the holder is in the *patient* slot with no author sign-off. This is `medical` / `medical.personal-health-records`. The reciprocal fixture; see below. |
| A drug leaflet, a nursing lecture, a saved journal article | Same false-positive family as the guideline; folded into `never_alone` item 1 rather than given four more fixtures. |
| A de-identified teaching case / case-based-learning vignette | Real, and rejected here: it is `clinical_practice.teaching-material`'s. `00` supplies the test — *"Topic answers what a file is about, while purpose answers what the file was for."* The topic is identical to a real case; the purpose is not. |
| `IM-0001-0001.dcm` and imaging studies | Already carried honestly on `medical.json` as `opaque_binary`. Not re-litigated here; a dictation `.m4a` is used instead as this family's unreadable-but-dangerous case, because it is the one where unreadability is *not* safety — a dictation almost certainly speaks a name aloud. |
| `Fluffy - discharge instructions.pdf` | `medical.research.md` rejected it because its subject is not a person and no neighbour held it. **This family now holds it**, at `clinical_practice.veterinary-practice` — but on the *practice* side only. An owner's own pet records still have no honest schema (ROSTER §5.6 dropped `med.veterinary-pet-owner` to residual), and this row does not quietly re-adopt them. |
| A physician's `.vcf`, a practice's contact export | `00` settles it — contact material is *"privacy-protected rather than used to create folder proposals"* — and `career.json` already fixtures the shape. Nothing clinical-specific would be learned. |
| A gym plan, a nutrition-label photo, a wellness-app export | Health-adjacent, holder-owned, no author role and no third party. `medical`'s problem, not this row's, and `medical` already covers it. |
| An anatomy lecture deck (`medical.json`'s collision fixture) | Deliberately **not** duplicated here. It is already `medical`'s named collision fixture, and re-fixturing it would state the same claim twice while implying this family owns it. Its practitioner-authored counterpart lives at `clinical_practice.teaching-material`. |
| A password-protected practice export | Considered for a fixture. If it cannot be read, the schema never activates, so it is a residual case rather than this node's file — the same reasoning `medical.research.md` recorded. The `practice_export_20260401.zip` fixture (readable manifest, unextracted members) teaches more. |
| A hospital payslip, an NHS/Trust employment contract | Employer-shaped, about the holder, no third-party subject. `career`. The gazetteer hit on the hospital name discriminates nothing — see the `never_alone` entry, marked `inference` because `00` writes that sentence about a university. |

---

## The collision fixture, named — in both directions

This row has **two**, because it can fail in two directions, and both are in the JSON.

### Over-firing: `Consultation letter TEMPLATE - blank.docx`

Practice letterhead. The holder's sign-off block. A professional registration number. Labelled
patient, date-of-birth and record-number slots. A history / examination / impression / plan
skeleton. Duplicated across a forms folder under several names. **Every signal this schema has,
except one:** the subject slots are empty, or hold bracketed placeholders.

What discriminates: **the second role must be filled, by a different person.** Nothing else in the
fixture changes. This is why `recognition.deterministic` says *"Two person-shaped blocks in two
different labelled roles is the shape; either block alone is never enough"* rather than listing the
letterhead and the sign-off as signals in their own right, and it is why `never_alone` carries the
clinician-title entry with `00`'s warning that *"PDF metadata should be treated as supporting
evidence, not as truth"* — a practice template names a clinician on every blank form it ever
generated.

The consequence in the JSON is a `must_not_conclude` most fixtures do not need: *"a sensitivity_status
of protected from a labelled patient slot that holds nothing"* An empty slot is not a person.

### Under-firing, and the direction that matters most: `After Visit Summary.pdf`

Clinic letterhead in the title zone. A visit date in a labelled slot. A medication table with drug,
dose and directions columns. Prose instructions. **Identical bytes-level shape to a letter a
clinician wrote.** The named person in the patient slot is the holder, and there is no author
sign-off block naming the holder as clinician.

What discriminates: the holder's **role**. Subject → `medical`. Author beside a different subject →
`clinical_practice`. Letterhead alone → neither, and neither is the right answer: *“Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.”*

**The same fixture bytes are named on both sides.** `medical.json` carries
`After Visit Summary.pdf` with observations *"clinic letterhead in the title zone; a visit date in a
labelled slot"*, *"a medication list rendered as a table with drug, dose, and directions columns"*.
This row carries the same file, with the extra observation that makes the negative checkable —
*"no author sign-off block naming the holder as clinician"* — and a `must_not_conclude` that names
`medical.personal-health-records` as its true home. This was preserved from the earlier draft
unchanged; it is the one place the family and its nearest neighbour already agree on a shared
artefact, and it should not be disturbed.

---

## Reciprocal boundaries, both directions

Every neighbour this family could steal from, stated in both directions, with the contested bytes
named. All edges on this row are authored **one-way** (no landed node names `clinical_practice`
except two `business_operations` rows that point at the `case-conference` *sibling*); R1c owes the
reciprocals.

| Neighbour | This row must **not** take | The neighbour must **not** take | Shared fixture bytes |
|---|---|---|---|
| `medical` | a document addressed to the holder as patient, or naming the holder in the patient slot, however clinical its letterhead | a practitioner's authored note, list or outbound letter merely because it is clinical and identifies a person | **`After Visit Summary.pdf`** — named on both sides, with the sign-off block as the discriminator |
| `career` | the holder's own registration certificate, CPD log, appraisal or CV where no third-party subject appears | a credentialing packet's case logs and audit returns — those are about other people's care | `GMC revalidation portfolio 2026.zip` (carries `also_schema: career`) |
| `legal` | a tribunal caption, a claim identifier, an instructing-solicitor block, a medico-legal report written for a court | a practice-internal incident form, a duty-of-candour letter, or the clinical entry describing the event | an incident file that becomes a claim — both anchors in one folder |
| `academic` | a course-code token with academic context, or a coursework work type | a real named subject beside a practitioner author-role structure, merely because the deck is clinical | `Anatomy Lecture 04 - The Brachial Plexus.pptx` — `medical`'s fixture, deliberately not re-fixtured here; the three-cornered case runs through `clinical_practice.teaching-material` |
| `research` | a project identifier, an ethics or approval-number slot, participant-facing framing | a routine-care note with a clinical author-role structure, because a clinician-investigator holds both in one folder | a source note verified against a case report form |
| `finance` | the line-item / policy-number / premium structure of an indemnity certificate — those are finance's fields on finance's evidence (PR-8) | the practitioner-side clinical material that shares a folder with the invoice, or the practice itself because the invoice names it | `Indemnity certificate 2026-27.pdf` (carries `also_schema: finance`) |
| `photos` | an EXIF-bearing capture as clinical evidence in its own right | a clinical fact from a photographed chart page | `Screenshot 2026-06-02 at 11.03.44.png` — and neither side may read absent EXIF as proof of a screenshot: *"the system must not mistake the absence of EXIF for proof that an image is a screenshot"* |

Note the pattern the table makes visible: with `medical` the relationship is a **mutex on one
evidence item** (the role of the named holder) *and* a co-activation on disjoint evidence — the
clinician who is also a patient in their own system. CONNECTION §5 invariant 1 permits both on one
pair at the price of a non-empty discriminating `signal`, which the row carries. `medical.json` does
the same thing with `finance`, for the same reason, so the shape is house-consistent.

---

## Neighbours considered that did **not** get an edge

- **`photos`** — appears as `also_schema` on file examples (a phone photo of a chart page carries
  real EXIF facts) but gets no `also_holds_with` row. The co-activation is already carried on the
  photos side by its own EXIF evidence; asserting it here would add a maintenance burden and no
  information. CONNECTION §8: an unasserted pair means unasserted, not false.
- **`identity`** — the identity/coverage-card confusion is already on `medical.json`'s
  `collides_with`. This family's version of it (a professional registration card versus an issued
  identity document) belongs on `clinical_practice.licensure-credentialing`, where the files are.
- **`hr`** — genuinely adjacent: staff occupational health is a practice's file about an employee,
  which is *both* families' shape at once. Deliberately unedged from the schema row, because the
  contested evidence sits at template level (`practice-administration` versus an HR row) and R1c
  should place it there rather than have the schema pre-empt it. **Flagged here so it is not lost.**
- **`law_practice`** — medico-legal instruction (a report commissioned by a solicitor) touches both.
  Same reasoning: it is a `malpractice-incident` / `referral-correspondence` question, not a schema
  one. `legal` already carries the schema-level edge and doubling it would state the claim twice.
- **`business_operations`** — a practice is an organisation with meetings and retrospectives, and
  `business_operations.meeting-record` and `.retrospective-postmortem` both already name
  `clinical_practice.case-conference` on their side. That edge belongs at the sibling, where those
  rows put it, and duplicating it upward would create a schema-level claim neither side made.
- **`college_applications`** — a health form in an admissions packet is a purpose join (PR-1 fences
  `purpose` inside applications), and this schema contributes nothing to it: the packet's health form
  is the applicant's own record, i.e. `medical`.

---

## `proposed_fields` — one, argued

**`subject_of_record`** — string, `destination_eligible: false`, `reliability_ceiling: possible`,
`adjudicate: R1c`. **Preserved from the earlier draft**, and argued here properly rather than
re-minted as a variant.

It is the one fact that separates this schema from every neighbour, and `canonical_fields.json`
holds nothing that can carry it:

- **`authored_by`** is the *opposite* role, and it is the role the **holder** occupies. Using it for
  the subject would put two different people into one key depending on the document — the D6 defect
  in its purest form.
- **`client`** is a commercial engagement counterparty whose `role_split` partner is `our_firm`. A
  patient is not the client of the person writing about them: the letter is usually addressed to a
  *third* clinician entirely, and the payer is frequently a fourth party. `legal.practice-matter-file`
  can lean on client/counsel because a legal client genuinely is the engaging counterparty; the
  structural analogy between the two families **breaks at exactly this key**, and that is the single
  most useful thing this row learned from reading that neighbour.
- **`people`** is the photos-side co-occurrence facet — who appears in a frame.
- **`institution`** is the facility, not the person.
- **`record_type`**'s canonical row is scoped to a *financial* record kind. `medical.research.md`
  rejected reusing it for the same reason, and this row does not reopen that.

Two independent grounds for **never** destination-eligible: `00`'s principle that a system
*"should avoid using authorship or creator identity as a destination dimension"*, and the stronger
point that here the label would name a **third party** — publishing in the filesystem namespace the
single fact the protection exists to hide, for someone who cannot object.

The ceiling is `possible`, not `probable`, and the reason is not evidential shyness: a labelled
patient block is as `direct` a slot as this product ever sees. The ceiling is pinned because the
**legal** question — may the product store another person's identity as a stored fact at all — is
not this row's to answer. Pinning at `possible` says "adjudicate me", where `probable` would say
"a rule will confirm this", which is a claim about a rule that does not exist.

**The ten siblings propose nothing, deliberately.** Duplicating this question ten times would be ten
rows answering a decision that is not theirs, and R1c would have eleven near-identical proposals to
reconcile instead of one. `career.credentials-licenses` sets the same discipline and this family
followed it. A sibling author reading this file should propose a field only if their situation needs
a fact `subject_of_record` cannot carry — and `veterinary-practice`'s three-party structure is the
one place that might genuinely be true, which is why its memo, not this one, is where that argument
belongs.

`proposed_context_terms` carries 24 clinical practice terms and is explicitly a **proposal**, not
`00`'s floor: `00`'s only literal context-term list is the academic one.

---

## Sparse-file discipline

Seven of the fourteen fixtures carry `group_without_copying_facts: true`, and this world needs the
rule as sharply as any: a dictation `.m4a` sitting beside signed letters, an unextracted practice
export, a theatre list, an MDT deck. In every one, the neighbourhood may legitimately group the file
while **no** clinical fact is written onto it — *"The graph does not automatically copy those missing
facts onto sparse files."*

Every fixture also carries `"any clinical_practice fact - none is declared"` in `must_not_conclude`,
so the placeholder status is checkable file-by-file rather than asserted once in the header. That is
the mechanism by which a reader can verify this row did not quietly grow fields.

---

## NEEDS-JOSEPH (this node)

- **NJ-CP-SAFETY** (restates ROSTER NJ-J-IND-4 with this row's evidence, and blocks the rest).
  `is_safety_domain: true` marks `00`'s four named domains and this row does not carry it. But the
  material is patient-identifying by default and the case is arguably **stronger** here than for
  some of the four, because the exposed party is not the user and cannot revoke.
  *Alternatives and costs:* (a) grant the flag — cheapest mechanically, but invents a fifth safety
  domain, which rule 15 / PR-2 reserve; (b) withhold it and **name the substitute mechanism** —
  CONNECTION §4 step 5's protect-before-model ordering is keyed to the flag and nothing else
  currently forces P7 ahead of a model path for this schema, so "withhold" without (b) leaves a real
  hole; (c) withhold and accept the hole — not recommended, and the row does not assume it.
- **NJ-CP-FIELD.** May `subject_of_record` exist as a stored key at all? Not `medical`'s
  holder-versus-subject question repeated — the sharper version, because here the subject is
  definitionally *not* the holder. *Alternatives:* (a) the key exists, never destination-eligible;
  (b) the key exists as a search-only field never surfaced in a proposal; (c) no key, and the
  subject is never stored — which would make detection store a marker plus a location only, and
  makes NJ-CP-EVIDENCE the same decision.
- **NJ-CP-EVIDENCE** (NJ-2 for this domain). May matched clinical text about a third party be stored
  in the local evidence table like any other observation, or should detection store only a protected
  marker plus a location? A stored third-party narrative is a much larger local surface than a flag,
  and every later dossier builder reads that table. `medical.research.md` raises this for the user's
  own text; the third-party case is strictly harder and the answers need not match.
- **NJ-CP-SHAPE.** Is ten templates on a field-less schema the right shape? This row's answer, now
  that all ten are written, is in the table above: eight differ cleanly on detection signals or
  privacy rules; `practice-administration` and `licensure-credentialing` are the two whose members
  are largely **subjectless**, which sits awkwardly on a schema defined by a second subject. *The
  alternatives:* fold `licensure-credentialing` into `career.credentials-licenses` (its own memo
  carries this as NJ-CP-2) and/or re-site `practice-administration` toward `business_operations` —
  against the cost that both moves scatter one practitioner's obviously-coherent corpus across
  three schemas.

---

## Reciprocity owed to R1c

Every edge on this row is authored **one-way**. Verified by grep across `nodes/`: no landed node
names `clinical_practice` as a schema-level neighbour; the only two references anywhere point at the
`clinical_practice.case-conference` *sibling*, from `business_operations.meeting-record` and
`business_operations.retrospective-postmortem`. R1c owes the reciprocals on `medical.json`,
`legal.json`, `career.json`, `finance` and `research` for the `also_holds_with` pairs, and on
`medical.json`, `career`, `legal`, `academic` and `research` for the `collides_with` pairs. The
`medical` pair is the one that must not be dropped: it is both a collision and a co-activation, and
the shared `After Visit Summary.pdf` bytes are already named on both sides, so the reciprocal is a
one-line addition rather than a research task.

---

## What changed in the JSON in this pass

Preserved wholesale: the entire recognition block, `proposed_context_terms`, `work_types`,
`grouping_reasons`, the template argument, all thirteen original fixtures including the
`After Visit Summary.pdf` reciprocal, every edge, `falls_through_to`, `sensitivity` and
`sensitivity_why`, and the `subject_of_record` proposal. Three changes only:

1. `one_line` — "Gist-level placeholder (J-IND)" → "Full-depth placeholder (J-IND, written to
   J-DEPTH)". The retired label was the only gist marker in the file.
2. **Added one fixture**, `Consultation letter TEMPLATE - blank.docx`, as the over-firing collision
   fixture. The old memo described it as "kept as a collision fixture in two rows" but the schema
   row had no such fixture — the claim was true of siblings and not of this file. Now it is true
   here, and the negative (`a sensitivity_status of protected from a labelled patient slot that
   holds nothing`) is checkable.
3. `open_question` (4) — rewritten against the **ten landed siblings** rather than the five that
   existed when the draft was written, and now names `practice-administration` and
   `licensure-credentialing` as the two that need R1c, instead of reporting a partial view.

## Audits run before returning

- `python3 -m json.tool` on `clinical_practice.json` — parses.
- Key set and key order compared to `medical.json` — identical, 27 keys, same order.
- Every quoted span in this memo and in the JSON `grep -cF`'d against
  `planning/00-database-agent-product-design.md` — all present verbatim, zero misses.
- `fields: []`, `role_split: []`, `template.dimension_order: []`, `refuse_node: false` — confirmed
  unchanged. No canonical field key minted; one `proposed_fields` entry, preserved not re-minted.
- `git status` — only `clinical_practice.json` and `clinical_practice.research.md` modified.
