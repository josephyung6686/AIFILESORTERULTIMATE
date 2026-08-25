# clinical_practice.licensure-credentialing — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the retired gist draft.
**Verdict: REFUSED (`refuse_node: true`), reversing the gist pass's "kept, but weakly".**
The reversal is the point of this memo, and it is argued rather than announced.

---

## The one-paragraph finding

This row described a real pile of paper and named it after the wrong thing. Proving that a
practitioner may treat patients produces certificates, good-standing letters, applications,
enrolment records, renewal notices and CPD evidence — and every one of those is
`career.credentials-licenses`' landed structure with a health regulator, a hospital credentialing
office or a payer standing in the **issuer slot**. The issuer is a *value*. Measured against the
`clinical_practice` default template — which the deepened schema row now states as a **structure**,
not a vocabulary — these files do not *differ from* the default, they fall *outside* it: they carry
one person, the holder, where this schema's defining signal is a second, differently-labelled
subject. What is left after that subtraction is a list of document types. The row folds into
`career.credentials-licenses`, which absorbs it without amendment.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — every quotation below machine-checked with
  `grep -F` against this file before writing. Twenty-seven distinct spans checked; one candidate
  (`The user's frozen tree should therefore include a policy for shared material…`) failed on a
  curly apostrophe and was re-cut to the substring that verifies.
- `planning/domains/CONNECTION.md` §2 (the node test), §5 (edge kinds), PR-6.
- `planning/domains/_CONTRACT.md` rules 10 and 15.
- `planning/prompts/ALIGNMENT.md`; `planning/overnight/council/DECISION-BRIEF.md` (D1, D4, J-IND).
- `planning/domains/ROSTER.md` §4 + Appendix A lines 593–594 — the two legacy ids this row absorbed:
  `med.clinician-licensure-credentialing` (ROW) and `med.clinician-cme` (FOLD).

### Landed neighbours read before writing, and **not** edited

- **`clinical_practice.research.md`** (40KB) — the schema anchor, and the document that decides this
  row. Two things in it are load-bearing here. First, it states the family's default template as a
  structure and gives the four-row reading table, one cell of which reads this row's files exactly.
  Second, it had already measured me: *"`licensure-credentialing` | the holder's own standing — no
  third-party subject in most members | **weakest**; carries its own fold question against
  `career.credentials-licenses`"*, and its `open_question` (4) named me as one of the two rows R1c
  should look at. This pass answers that question rather than re-asking it.
- **`clinical_practice.patient-chart.research.md`** (37KB) — the two-role distinction. Its table
  routes *"The holder's **own** registration, appraisal, CPD log or CV"* to `career` /
  this row, on the observation *"no third-party subject appears"*. That observation is the refusal.
- **`career.credentials-licenses.json` and `.research.md`** (45.6KB / 13KB) — read in full. This is
  the load-bearing seam and it is the file that closes the case. Details below.
- `career.employment-records`, `career.recruiting`, `career.research.md` — read for the career
  family's internal seams, because the employment-contract fixture migrates into them.
- `identity.core-documents.research.md` (22.9KB) — the identity seam.
- `clinical_practice.malpractice-incident.research.md` (42KB) — it names me twice and holds an edge
  to me; the reciprocity it is owed is filed for R1c below.
- `clinical_practice.practice-administration.json`, `.teaching-material.json`,
  `.veterinary-practice.json` — each routes material here by name. Same reciprocity list.
- `business_operations.organisational-records.json` — read as the refusal-quality exemplar. Its
  structure (findings recorded so the refusal is checkable; the escape route closed inside the JSON
  so the row cannot be resurrected from its own file) is imitated here deliberately.

---

## What the row claimed to be for

Preserved from the gist draft, because it was accurate and remains the best statement of the pile:

> Proving, repeatedly and to several different bodies, that the holder may **treat patients**:
> statutory registration and revalidation, hospital privileging, payer or panel enrolment,
> scope-of-practice authorisations, and the continuing-education, audit and logbook evidence those
> cycles consume.

Nothing in this memo disputes that the pile exists, that it is coherent to a human, or that a
clinician thinks of it as one drawer. The question the node test asks is different and narrower:
**does a template row need to exist for the product to file it correctly?**

---

## The node test, leg by leg

CONNECTION §2, verbatim: *"A **template** row exists only if its detection signals, recommended
dimensions, or privacy rules differ from its schema's default template. ALIGNMENT: a template that
would only repeat its schema's fields and dimension order **is not a node** — it is the schema's
default template."*

### Leg 1 — fields: unsatisfiable, and **not** a pass

`clinical_practice` declares no field rows. `_CONTRACT` rule 15 permits it, CONNECTION PR-6 defines
it, and J-IND ratifies it. So a template on this schema declares none either, and the field leg
cannot be run as written. The schema row states the same finding about itself and refuses to launder
it into a pass — the leg is *"unsatisfiable for this row, and would be unsatisfiable in exactly the
same way for every J-IND placeholder schema"*. I inherit that finding rather than restating it.

The honest consequence: **an unsatisfiable leg carries no weight in either direction.** It is not a
point in the row's favour and it is not the reason for the refusal. The row had to survive on legs 2
and 3, exactly as the schema itself did.

One thing this leg *does* contribute, and it is evidence against the row rather than for it.
`career.credentials-licenses` proposes exactly one field, `credential_expiry`, *recorded, not
written* under D1 — its own words: `"RECORDED, NOT WRITTEN. This is a proposal for the moment
S3/D1's deferral lifts; it writes no field row here and reverses nothing."` Its argument is that the
concept is *"the load-bearing fact of this situation - a credential is a standing with an end date,
which is what separates it from a completion certificate, a diploma and a transcript"*. That is the
load-bearing fact of **this** row's material too. The concept the pile needs is already proposed, on
the career side, by the row that already holds the files. Note D1 is respected here in both
directions: I mint nothing, I propose nothing, and I do not re-open `credential_expiry`.

### Leg 2 — detection signals: **the decisive failure**

This is where the gist pass stopped early. It reasoned — correctly about the test's shape — that a
template is compared against *its own schema's default*, and that an overlap with a row on a
*different* schema is an `collides_with` edge rather than a refusal. Then it never finished running
the comparison it had named. Run to the end, the row fails, and it fails twice over.

**(i) It does not differ from the family default; it falls outside it.**

The schema row does not state the default as a vocabulary. It states it as a structure — an author
or responsible-clinician block naming the holder **beside** a separately labelled subject block
naming a **different** person, both filled — plus its batched multi-subject and direction-of-address
variants. And it supplies a reading table, one cell of which is this row's entire file list:

| What is observable | Reading (schema row's own table) |
|---|---|
| an author block naming the holder, subject block **absent or empty** (a blank template, **a certificate, a registration notice**) | *"this schema at most weakly, and usually `career` or Independent Records"* |

A registration certificate, a good-standing letter, a privileging application, a panel-enrolment
record, a CPD certificate and a renewal notice have exactly one person in them, and that person is
the holder. **This row is that table cell, promoted to a node.** The seam the family turns on —
*"the subject block being filled by a different person is the activation, and the second role is
what discriminates"* — never fires on this material.

This is also the honest answer to the never-alone charge the dispatch raised. Being single-role does
not merely make the row *weaker* than its siblings; it means the row cannot borrow the structure
that makes its siblings legible. `patient-chart` defeats a never-alone charge with a relation
between two labelled roles. I have no second role to point at. What I have is an issuer and a
holder — and an issuer-plus-holder pair is the shape of *every* credential document in the corpus: a
passport, a diploma, an insurance certificate, a warranty. It discriminates nothing. That escape
route is closed inside the JSON's `never_alone` list so the row cannot be rebuilt from its own file.

**(ii) What remains is `career.credentials-licenses`' signal list, item for item.**

Subtract the two-role structure and this row's evidence is: an issuing body, a credential title, a
labelled identifier slot, a validity window. Set against the landed career row:

| This row proposed | `career.credentials-licenses` already landed |
|---|---|
| issuing health regulator at a word boundary + labelled registration-number slot + status + validity window | *"a regulatory board, licensing authority, certifying body or professional association"* in the issuer position + credential term; and, separately, the labelled issue/expiry pair as *"the structural signature of this template"* |
| payer enrolment: provider-identifier slot + effective-date slot | the identifier slot and the validity-window pair, unchanged |
| revalidation portfolio: archive manifest naming credential-shaped members, read unextracted | its seventh deterministic signal: an archive manifest listing credential-shaped members read without unpacking |
| CPD certificate: accrediting body + credit designation + completion date | work type `continuing-education compliance record`; grouping reason *"a credential and the continuing-education evidence submitted to keep it"* |
| renewal email from a regulator's domain | its fifth deterministic signal: a renewal term in the subject slot, a licensing board in the sender slot |
| CPD activity log / credential ledger spreadsheet | its sixth: column headers reading `credential, number, issued, expires, renewed` |
| verification / primary-source-verification response | work type `good-standing or verification letter`; its fourth signal, a verification affordance in a labelled slot |
| renewal notice, fee receipt, disciplinary notice, wallet card | work types `renewal notice`, `dues invoice or renewal receipt`, `disciplinary or status notice`, `wallet card or pocket credential` |
| privileging or licensure application | work type `registration or licensure application` |

**Every signal is one of those with a health regulator in the issuer slot.** And 00 says what that
is: *"The system may create new values when it sees a new course, project, company, university, or
event, but it should not invent new fields automatically"*. A row whose only discriminator is which
body appears in an already-declared position is a **value of a field wearing a node's clothes** —
which is exactly charge (a), and it is the strongest charge because it is unanswerable.

**The four residual structures, taken one at a time.** These were the gist row's genuine claims and
they deserve individual disposal, not a wave:

1. **A requested-privileges / scope-of-practice list.** The gist draft called it *"the discriminating
   structure - an employment application does not carry one"*, and that observation is true. It is
   still not a node. The list enumerates *the procedures the applicant asks to be permitted* —
   work types, which are values, by the sentence quoted above. Structurally, it is a form section on
   an application, and `career.credentials-licenses` already lists the application as a work type.
   A list of permitted activities is not a second labelled party.
2. **A payer or panel enrolment designation.** A labelled provider-identifier slot beside an
   effective-date slot is the identifier-plus-validity-window pair, unchanged, with a payer in the
   issuer position. This is the clearest single instance of the value-not-structure charge.
3. **A revalidation or appraisal portfolio.** Its claim was the archive manifest, which is the career
   row's seventh signal verbatim, with a *requirement partition* inside it — and the partitions name
   document types. Worse for the row: a portfolio is a **packet**, and a packet is a *group*, not a
   node. 00: *"A file may validly belong to more than one accepted group"*. Its members activate on
   their own evidence; the audit return can reach the `clinical_practice` schema and Protected
   Records while the CPD certificates reach career, out of the same zip.
4. **Continuing education.** The legacy `med.clinician-cme` fold rested on "CME is the evidence a
   registration consumes". That reading is fine and it still has a home: the career row already
   carries the compliance-record work type *and* the group that binds a credential to the evidence
   submitted to keep it, and `academic.continuing-education` holds the course-side reading. There
   was never a third seat at that table.

**Verdict on leg 2: fails.**

### Leg 3 — privacy rules: **no difference in either direction**

The gist row's privacy content was: route to Protected Records; do not expose in model prompts;
enforce policy before any model path; assign no P7 class. All correct, and none of it is this row's.

- `career.credentials-licenses` states the same routing from the same 00 sentence, **and** adds two
  rules this row never had: the isolated-file licence (*"Rare but sensitive files such as passports,
  visas, and legal documents may be surfaced as protected records even when they do not meet a
  normal group-size threshold"*) and the identity-spillover rule for a credential carrying a date of
  birth or a national identifier.
- The `clinical_practice` schema's own posture is *stronger* than both — its dimension prohibition
  and its bulk-sensitivity rule — and applies to anything that activates the schema, with or without
  a sibling row.

So the row is squeezed from both sides: weaker privacy rules than the neighbour that holds the
files, and no rule of its own that the schema does not already state. **Fails.**

### Overall

Leg 1 unsatisfiable, legs 2 and 3 failed. **Refused.**

---

## The three charges, answered directly

**(a) It is `career`'s material wearing a clinical label.** *Conceded, and it is the refusal.* The
comparison table above is the answer. The only discriminator is that the professional is a
clinician, and that is a value of the issuer/credential position, not a structure.

**(b) Its documents are certificates and forms — a document type.** *Conceded.* Strip the reasoning
and the row's content is a list: certificate, good-standing letter, privileging application,
enrolment record, CPD certificate, CPD log, case log, verification response, renewal notice,
disciplinary notice, scope authorisation, revalidation portfolio. Twelve document types; nine are
already the career row's landed work types. The schema row forbids exactly this in advance —
*"A sibling justified only by "we hold letters" is the schema's default template with a narrower
filename filter."* — and it is the charge that refused `construction_property.compliance-certificate`.
`work_types` is emptied in the JSON for this reason, with the list preserved in the note as evidence
of what the row actually was.

**(c) Being single-role, it may fail never-alone where its siblings survive on the two-role
structure.** *Conceded, and it is worse than "may".* Run the deletion test. Strike every organisation
name (regulator, college, society, hospital, payer) — never-alone by read-across from *"A university
name alone should not create a group because Columbia can appear as an authoring school, course
provider, target institution, employer, research venue, or merely a cited organization."* (marked
**inference**: 00 writes that sentence about a university, and a professional body appears as issuer,
employer, examiner, publisher and conference host by the same logic). Strike every document-type
word, every person's name, every bare number, every certificate layout. What remains that is true of
this row and false of `career.credentials-licenses` is **nothing**. The brief states the
consequence: such a row can never activate.

---

## The load-bearing seam, stated in both directions

**`clinical_practice.licensure-credentialing` → `career.credentials-licenses`:** everything. The
registration or licence certificate, the good-standing or verification letter, the renewal notice and
fee receipt, the membership record, the wallet or registration card, the licensure or privileging
**application**, the panel-enrolment record, the continuing-education compliance record, and the
disciplinary or status notice about standing. The career row's landed `work_types` already name nine
of these, so it absorbs the material **without amendment** — which is itself the strongest single
piece of evidence for this refusal. A neighbour that needs no change to take your whole file list was
already holding it.

**`career.credentials-licenses` → here:** nothing comes back, because the row no longer exists. Under
the gist draft this direction would have read "a document whose issuing body regulates the right to
treat patients rather than to hold a job leans clinical" — the phrasing `clinical_practice.json` uses
today. That sentence is now the thing being refused: *which* body regulates is a value.

**I have not edited `career.credentials-licenses` and I do not contradict it.** Where its work_types
enumeration does not quite reach — the hospital or facility **privileging grant**, which is neither a
licence nor a membership — that is recorded as a recommendation to R1c in `open_question` (2). It is
a *work type*, i.e. a value. It is emphatically not a request for a node, and R1a must not read it
as one.

### The same fixture bytes, named on both sides

The competition is cleanest on files both rows would have claimed:

| Fixture | The gist row's claim | The career row's claim | Who holds it now |
|---|---|---|---|
| `RN_License_California_2026.pdf` (**the career row's own landed fixture** — a *nurse's* licence, sitting on the career side since it landed) | would have fired on regulator + registration number | credential title + labelled identifier + validity window; offered Protected Records before Independent Records | **career**, and it always did. That a clinician's licence was already a career fixture, uncontested, is the fold question answered before it was asked. |
| `GMC certificate of good standing 2026.pdf` (this row's headline fixture) | regulator letterhead, registration slot, status line | same structure, different issuer value | **career** |
| `credentials.zip` | not claimed | live on career's seam with `identity.credentials-passwords` and `academic.transcripts-credentials` | **career's seam to hold**, unchanged by this refusal |

---

## The collision fixture, in both directions

### Over-firing — a file that would wrongly have fired this row

**`Revalidation guidance for doctors.pdf`.** Preserved from the gist draft, and it survives the
refusal intact because it was never an argument *for* the row. A regulator's letterhead, a
publication date, prose describing what practitioners must submit, a version token — and no name, no
number, no evidence. Every vocabulary signal the row would have used is present and the file is
*about* the process rather than evidence of it. Discriminator: **no holder, no identifier, no
validity window.** It goes to `clinical_practice.protocol-guideline`, the family's mirror row, whose
whole point is instruction with no subject, or to Reading Inbox: *"Reading Inbox may hold papers,
articles, reports, and saved PDFs that appear to be reading material but have no active research,
course, or project association."*

### Under-firing — a file that must not be lost *to* this row's disappearance

**`Procedure logbook 2025-26.xlsx`.** This was the gist pass's best argument — the one member
carrying third-party material, and the stated reason the row sat on the `clinical_practice` schema
at all. It matters most, so it gets the fullest answer. It does **not** rescue the row, and it is
**not** lost:

1. *It is not a credential document.* It is a record about other people's care that happens to be
   **submitted as** credentialing evidence. Submission is a purpose, and 00 separates the two:
   *"Topic answers what a file is about, while purpose answers what the file was for."* A row cannot
   own a file on the strength of what it was submitted for while the file's content belongs
   elsewhere.
2. *It does not need this row to be seen.* Column headers reading `date, record number, procedure,
   role, supervisor, outcome` across several hundred rows and many subjects **is** the
   `clinical_practice` schema's own batched multi-subject signal, whose bulk-sensitivity rule the
   schema row states and owns (*"a multi-subject list is bulk-sensitive as a whole"*). The schema
   activates; Protected Records receives it when no sibling situation fires.
3. *The purpose does not travel to the facts.* A group may hold the logbook beside the privileging
   application without either copying facts onto the other — *"The graph does not automatically copy
   those missing facts onto sparse files"*.

The residual coverage is genuinely complete: `Protected Records` (identifier-bearing records and
anything with a third party), `Independent Records` (the standalone certificate), `Receipts and
Confirmations` (the fee receipt), `Review Later` (the unresolved certificate — the honest home for
precisely the ambiguity this row was invented to absorb), `Reading Inbox` (guidance),
`Unsupported or Encrypted` (the locked portfolio), `One-Off Images` (the photographed card).

---

## Reciprocal boundaries with the neighbours that are *not* career

**`identity.core-documents`.** Stated in both directions, and **unchanged by the refusal** — only the
row on my side of it moves. A professional registration card and a passport both pair a name with an
official number under a seal, and credentialing bundles physically contain identity documents. The
discriminator: a document establishing **who someone is**, issued by a civil authority, is identity;
a document establishing **what someone may do**, issued by a sectoral regulator or a facility, is a
credential. A name beside a number and a seal discriminates neither. After this refusal, the credential
side of that boundary is `career.credentials-licenses`, which already states its own version of it
(the date-of-birth / national-identifier spillover rule, where the identity schema is *a separate
activation on that file's own evidence*, not a transfer of the file). Shared fixture:
`licence card photo.HEIC` — camera EXIF present, so the screenshot reading is forbidden outright
(*"the system must not mistake the absence of EXIF for proof that an image is a screenshot"*), and
GPS metadata is not safe merely because the photographed subject is a card.

**`clinical_practice.malpractice-incident`.** It holds an edge to me and names the
conditions-on-practice notice as *"a genuine both-rows file"*. That reading survives; the row on the
other side of the edge becomes `career.credentials-licenses`, which already carries
`disciplinary or status notice` as a work type. Its own memo already anticipated this — it wrote that
reaching across the seam was awkward because of *"`licensure-credentialing`'s known problem, carried
in that row's own memo"*. The problem is now resolved rather than carried. Its rejected file
(*"A CPD certificate for a patient-safety course"*) was already routed to
`clinical_practice.licensure-credentialing` / `career.credentials-licenses`; only the second name
survives.

**`academic.continuing-education`.** The CPD certificate is the same artefact from two angles. That
seam is real and it is now `career.credentials-licenses`' to hold against academic, not mine to
arbitrate. Where both readings are supported, the design decides rather than the model:
*"conflicting signals should lead to abstention rather than an invented classification"*.

**`career.employment-records`.** The gist row's collision fixture,
`Employment contract - consultant post.pdf` (an employer letterhead, a job title, a salary scale,
and a clause requiring the holder to maintain registration), is preserved and **reassigned**: the
seam is now internal to the career family, `employment-records` against `credentials-licenses`,
which is where it always belonged. That my collision fixture resolves entirely inside a neighbouring
family, without reference to me, is itself evidence for the refusal — a row whose hardest boundary
case is settled by two other rows was standing in their family.

---

## Files considered and rejected

Beyond the two collision fixtures above:

| File | Why it is **not** this row's evidence |
|---|---|
| **A medical school degree certificate** | An academic credential. The row was about the right to practise, not the qualification behind it. `academic.transcripts-credentials`. Preserved from the gist draft. |
| **A conference badge photo / hotel receipt from a CPD trip** | Noise. `One-Off Images` and `Receipts and Confirmations`. Preserved from the gist draft. |
| **A practice's own CQC/registration certificate** | Rejected, and the discriminator is stated on **both** sides already: `clinical_practice.practice-administration` carries `"activation of clinical_practice.licensure-credentialing: this registration is the PRACTICE's, not an individual's"` in a `must_not_conclude`. The organisation-versus-individual line is real; it just does not need a second row on the individual side. |
| **An employer-internal competency sign-off** (a "signed off on cannulation" form) | Tempting: an issuing organisation, a named holder, a skill, a date. Rejected — the career row already names this exact model problem, *deciding whether the organization named on a certificate is the issuing authority or the holder's employer*. It is career's ambiguity, resolved on career's evidence. |
| **A BLS/ALS resuscitation training card** | The purest form of the trap: a certificate layout, an accrediting body, an expiry, a clinical topic. It is a `continuing-education compliance record` on career, or `academic.continuing-education`, and the clinical vocabulary in the course title changes nothing. |
| **An indemnity / malpractice insurance certificate** | Considered because privileging applications require it and it travels in the same packet. Rejected, and instructively: the career row already names `Certificate of Liability Insurance - 2026.pdf` as its own never-alone fixture (an expiry plus an issuing organisation, and still the finance neighbour's record). A file I would have inherited via a packet is already fixtured, on the other side, against the packet reading. |
| **An occupational-health clearance or immunisation record** | A real member of a credentialing bundle, and rejected outright: it is the holder's own health record, which is `medical`'s, and a packet does not launder a health record into a credential. This is the sharpest example of members activating individually. |
| **A CV / clinical portfolio of work** | `career.portfolio-work-samples` and `career.employment-records`. A CV *lists* credentials, and the career memo already settles that: *a section that lists credentials is a résumé; the section is not a credential document*. |
| **A DBS / background-check certificate** | Considered and left unasserted. Structurally a credential (issuer, identifier, date) but not a standing to practise; it belongs to whichever career row R1c places it on, and asserting it here would be a refused row making a placement. |
| **A rota or job-plan showing sessions and supervision** | `clinical_practice.practice-administration` and `hr`, per that row's own landed statement. Not credential evidence, even when it is submitted as evidence of activity. |

---

## `proposed_fields`

**None**, and none deferred either. The gist draft proposed nothing and deferred to the schema row's
single `subject_of_record` proposal — the correct call, preserved unchanged; **no variant is minted
here.** A refused row proposes no fields in any case.

Recorded for R1c because it bears on the refusal rather than on any field: `credential_expiry` is
already proposed on `career.credentials-licenses`, *recorded, not written* under D1, with the
argument that a credential is a standing with an end date. That the one concept this pile needs is
already proposed by the row that already holds the files is not a coincidence — it is the same
finding as leg 2, arriving from the field side.

---

## Neighbours considered that did **not** get an edge

A refused row carries **no edges at all** — `collides_with` is emptied deliberately, so the row
cannot be reconstructed from its own JSON. Recorded here for R1c:

- **`career.credentials-licenses`** — was the gist row's headline `collides_with`. It is no longer a
  collision, because it is an **identity**. Two rows describing one structure over one set of files
  is one row.
- **`career.employment-records`**, **`academic.continuing-education`**, **`identity.core-documents`**
  — the gist row's other three edges. Preserved as arguments above; the boundaries survive, with
  `career.credentials-licenses` on the far side of each.
- **`finance.subscriptions-utilities`** — considered again and again left unasserted. A regulator's
  annual fee is a recurring payment, but it is not a subscription and the confusion is thin.
- **`government`** — a health regulator is a statutory body. Still not authored: the discriminator
  (does the body license clinical practice specifically?) needs the `government` row's own view,
  which has not landed, and a refused row should not author a first edge into an unlanded family.
- **`hr`** — appraisal is an employer process as well as a regulatory one.
  `clinical_practice.practice-administration` already draws that line and I do not redraw it.

---

## NEEDS-JOSEPH

- **NJ-CP-2 — is now ANSWERED rather than asked.** The gist row and the schema row both carried it:
  should this row fold into `career.credentials-licenses`? **This pass answers: fold, by refusal.**
  If Joseph overrules, the thing to reinstate is *not* this row as written — it is a narrow row named
  for the artefact described under "what would reopen this row" below, and that row does not exist
  yet. Reinstating this id as written would rebuild the row the evidence refutes.
- **NJ-CP-6 — where does continuing education live?** Also answered, and downgraded from a fork to a
  seam: not here. The `med.clinician-cme` fold is retired with the row. The live question is the
  ordinary `career.credentials-licenses` ↔ `academic.continuing-education` seam, which both rows
  already carry, and it is not this row's to settle.
- **NJ-LC-REC — reciprocity owed, and the largest operational consequence of this refusal.** Six
  landed files route material to this id **by name** and must be repointed at
  `career.credentials-licenses`. I have not edited any of them. The exact list:
  1. `clinical_practice.json` — `collides_with` toward career, whose signal text says the overlap
     "is real enough that `clinical_practice.licensure-credentialing` carries a NEEDS-JOSEPH asking
     whether it should fold"; also its `open_question` (4), which names this row as one of the two
     for R1c.
  2. `clinical_practice.practice-administration.json` (two places) — the hr-family argument, which
     says an individual's own appraisal or revalidation portfolio "supports neither, because the
     sibling `clinical_practice.licensure-credentialing` owns it"; and a `collides_with` entry.
  3. `clinical_practice.teaching-material.json` (two places) — the portfolio fixture's
     `must_not_conclude`, and a `collides_with` entry.
  4. `clinical_practice.patient-chart.json` / `.research.md` — the card-shaped-files routing and the
     holder's-own-registration table row.
  5. `clinical_practice.malpractice-incident.json` / `.research.md` — the edge for the
     conditions-on-practice notice.
  6. `clinical_practice.veterinary-practice.json` — "the surgeon's own registration is
     `licensure-credentialing`".
  In every case the substitution is mechanical (`career.credentials-licenses` for this id) and no
  neighbour's *argument* changes, because each was drawing a boundary against **the holder's own
  standing**, which career holds. R1c owns the edit.
- **NJ-LC-PRIV — a small but real gap the refusal creates.** `clinical_practice` has a stronger
  privacy posture than `career`. The `Revalidation portfolio 2026.zip` case now splits: its CPD
  members reach career, its audit return reaches the schema and Protected Records. That is correct
  per-member behaviour, but it means **no row holds the packet as a whole**, and the packet is more
  sensitive than any ordinary member of it. Two alternatives, with costs. *(a)* Rely on the
  member-level routing plus 00's shared-material policy — *"should therefore include a policy for
  shared material: a shared branch, a primary-home convention, a reference or alias convention, or
  mandatory review."* — cost: a bundle is only ever as protected as its most protected member is
  *individually* detected. *(b)* Have P7 treat an archive as inheriting its most sensitive member's
  posture — cost: it is a P7 mechanism, not a roster question, and this row may not assign a handling
  class. I recommend (a) and flag (b) for P7.
- **NJ-LC-SAFETY (inherited, restated with this row's evidence).** The schema's NJ-CP-SAFETY notes
  that CONNECTION §4 step 5's protect-before-model ordering is keyed to `is_safety_domain`, which
  `clinical_practice` does not carry. The refusal makes this slightly *more* pressing, not less:
  material that would have sat on a clinical row now sits on `career`, which does not carry the flag
  either. The requirement stands in prose from 00 whichever row receives the file: *"Privacy policy
  must be enforced before content reaches any model or external connector."*

---

## What would reopen this row — recorded so it is not reopened on the wrong evidence

**Not** a longer document-type list. **Not** a specialty (cardiology, midwifery, dentistry — values,
and D4 makes jurisdiction a value too). **Not** the observation that credentialing packets often
contain patient material, because the members activate individually. **Only** this: a named
artefact, routinely kept, in which the holder occupies one labelled role and a **different named
party** occupies another labelled role whose relation the artefact records, and which
`career.credentials-licenses`' identifier-plus-validity-window structure cannot read. If such an
artefact can be named, the right response is a **new narrow row named for that situation** — not the
reinstatement of this one. Minting that id is outside what a single node agent may do.

This paragraph is duplicated inside the JSON's `refuse_reason` (8) on purpose, so a reader holding
only the node file reaches the same gate.

---

## What changed in this pass

Checked line by line against the JSON actually written.

**Reversed**

- `refuse_node`: `false` → **`true`**, with a ~7,000-character argued `refuse_reason` in eight
  numbered parts. This is the substantive change and everything else follows from it.
- `name` → suffixed `(REFUSED)`; `one_line` rewritten to state the refusal, the reason, and the
  routing, and to record that the two legacy ids are **retired** rather than rebuilt.
- The gist verdict's reasoning is not deleted — it is quoted and answered in "leg 2" above, because
  it was right about the test's shape and wrong about the outcome.

**Emptied, each with a `_note` explaining why the emptying is part of the argument**

- `work_types` (12 → `[]`) — a document-type list is the charge, not a defence.
- `proposed_context_terms` (20 → `[]`) — thirteen were career's list or synonyms; a refused row must
  not leave what looks like an activation surface.
- `grouping_reasons` (5 → `[]`) — two are career's landed grouping reasons; the rest need no row.
- `collides_with` (4 → `[]`) — a refused row never fires, so it collides with nothing; leaving edges
  would let it be rebuilt from its own file.
- `recognition.deterministic` (8 → 2 entries, the first stating "None. This is the finding, not an
  omission", the second recording labelled-slot and gazetteer discipline **for the receiving rows**).
- `recognition.needs_llm` (5 → 2, both stating that nothing is routed here).

**Added**

- An eleventh `never_alone` entry closing the **two-role escape route** inside the JSON, so the row
  cannot be resurrected via the `patient-chart` argument.
- A tenth file example, `Panel enrolment - provider participation confirmation.pdf`, because
  enrolment was one of the four residual structures and had no fixture.
- A seventh `falls_through_to` residual, `One-Off Images`, for the photographed card (marked
  `inference`).
- `proposed_fields_note`, `work_types_note`, `proposed_context_terms_note`, `grouping_reasons_note`,
  `collides_with_note` — the house `_note` idiom already used on `career.credentials-licenses`.
- `open_question` rewritten from a fold question into three items: the reciprocity R1c owes, the one
  work type career may want (the privileging **grant**), and the fold question marked answered.

**Preserved unchanged, deliberately**

- All nine gist file examples, with `must_not_conclude` entries rewritten to teach the refusal
  rather than the activation. `Employment contract` and `Revalidation guidance` survive intact as
  fixtures — both were always arguments about where files *don't* go.
- `sensitivity: potentially_sensitive` and its two 00 quotations. A refusal that downgraded
  sensitivity would be a privacy regression; the material is now *more* dependent on the residual
  routing, not less.
- `launch: "placeholder"`, `fields: []`, `proposed_fields: []`, `schema_id`, `kind`, `parent_id`,
  the `file_kinds` block, `template.dimension_order: []` and `time_first: false`.
- The gist memo's four "files considered and rejected" entries, now joined by seven more.

**Memo**: 5,287 B → this file. `Depth: GIST` → `Depth: J-DEPTH`.

---

## Audits run before returning

1. `python3 -m json.tool` on the node file — parses.
2. Every 00 quotation re-checked with `grep -F` against `planning/00-database-agent-product-design.md`
   — 27 spans, all exact. One candidate failed on a curly apostrophe and was re-cut to a verifying
   substring rather than quietly corrected.
3. Every quotation *of a neighbour file* re-checked with `grep -F` against that file —
   `career.credentials-licenses.json` (7 spans), `clinical_practice.research.md` (3),
   `clinical_practice.practice-administration.json` (1).
4. Every `file_examples.source_type` checked against `SOURCE_TYPES` in
   `src/evidence_shape/vocabulary.py`: `text_document`, `archive`, `spreadsheet`, `image`, `email`
   — all present.
5. Every `falls_through_to.residual_template` checked against 00's nine residual names.
6. Edge ids: none written (all edge arrays empty), so no id can be off-roster. Ids named *in prose*
   (`career.credentials-licenses`, `career.employment-records`, `academic.continuing-education`,
   `identity.core-documents`, and the five clinical siblings) were each confirmed to exist as files
   under `planning/domains/nodes/`.
7. No thresholds, no counts, no scores, no regexes, no gazetteer contents, no handling class, no
   folder path written as a fact.
8. Files written: exactly the two assigned. `git status` confirms no neighbour, roster,
   `canonical_fields.json`, `src/` or `check.py` was touched.
