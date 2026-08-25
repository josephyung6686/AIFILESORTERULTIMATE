# `clinical_practice.referral-correspondence` — lab notes (template row, deepened to J-DEPTH)

Verdict: **kept, narrowly.** This is not a node for a document type called “referral letter.” It is
the professional situation of a clinician's outward correspondence file: an item addressed by the
holder to another service about a third person, replies paired to that item, and the register that
tracks sending and acknowledgement. The gist verdict survives the stronger charge that every letter
may merely be a work type inside `patient-chart`.

The existing JSON was a verified and unusually substantive 26KB draft. Per the deepening addendum I
preserved its arguments. The only JSON change is the depth label in `one_line`; the full argument that
was absent from the shallow memo is supplied here.

## Sources actually used

Binding sources: `planning/00-database-agent-product-design.md` (source of truth and the only product
authority quoted); `ALIGNMENT.md`; `CONNECTION.md`; `CONNECTION-EXAMPLES.md`; `_CONTRACT.md`;
`canonical_fields.json`; `roster.json`; `src/evidence_shape/vocabulary.py`; the council
`DECISION-BRIEF.md`; and `ROSTER.md` Appendix A. The absorbed legacy id is
`med.clinician-referral-sent`.

Required comparisons read before writing, and not edited:

- `clinical_practice.research.md`, the J-DEPTH schema anchor. Its landed principle is decisive: one
  name or role is never enough, while two separately labelled roles filled by different people form
  a relation. This row must still add something beyond that family-wide relation.
- `clinical_practice.patient-chart.research.md`, owner of longitudinal accumulation about one subject.
- `clinical_practice.practice-administration.research.md`, owner of clinical operations and purely
  procedural onward-sends.
- `medical.personal-health-records.research.md`, owner where the holder is patient/subject.
- `business_operations.meeting-record.research.md`, read because correspondence can record an
  interaction. It supplied no contested bytes: minutes are event records, not directed messages.
- `legal.practice-matter-file.research.md` and `career.consulting-client-engagement`, the closest
  structural analogues for labelled professional roles and fee-bearing reports.

## What this row is — and is not

The positive corpus is a clinician's **outward correspondence workflow**: referrals sent, clinic and
discharge letters written, onward referrals, acknowledgements and appointment offers received against
an earlier referral, secure-message threads, third-party clinical reports, dictation and signed
versions, and the sent-letters/chase register.

Three observable relations define it:

1. **Address:** the holder is sender, signatory, or referrer; a different clinician, service, insurer,
   employer, school, court, or agency is addressee.
2. **Subject:** a third person occupies a separately labelled `re`, patient, subject, or record-number
   block. Subject is neither inferred from clinical prose nor copied from neighbours.
3. **Workflow:** the item is sent, acknowledged, chased, answered, or joined to a reply by an exact
   reference/quoted date; a register repeats subject/addressee/status columns.

This is not “all referral correspondence,” “all clinical letters,” or “letters in a chart.” Referral
guidance, a blank template, a patient's own copy, an administrative records request, meeting minutes
mentioning referrals, and a letter merely filed inside one chart do not establish it. *Referral* and
letter layout are both never-alone.

## The charge against existence

The refusal case is real. A referral letter is normally filed in a chart; “letter” could be only a
`work_type`; and the schema anchor already recognizes practitioner-authored material where holder and
subject occupy two labelled roles. If that were all this row added, it would be the schema default or
`patient-chart` with a narrower filename filter and should be refused.

It survives because the **third labelled role and workflow relation are load-bearing**. The schema's
two-role floor says holder is practitioner and someone else is subject. This row additionally requires
a recipient distinct from both, or a reply/register structure preserving direction between
institutions. Those structures occur outside charts: a sent-letters log spans hundreds of subjects; a
secure-message mailbox is threaded by recipient; a chase list is organized by unanswered item. A SOAP
note and treatment plan have holder/subject roles but no external addressee or sent/answered lifecycle.

The labelled-role principle is not an automatic escape:

- sender + addressee without a distinct subject is ordinary professional mail and does not fire;
- holder-author + subject without external addressee/lifecycle supports the schema and often chart,
  not this row;
- holder-author + external addressee + different subject in labelled blocks supports this row;
- the same names only in prose require local interpretation and may remain unknown;
- a register with labelled subject, addressee, kind, and sent/acknowledged columns supports this row
  even though no row is a whole letter.

That register is decisive. A multi-subject sent-letters register cannot be a work type inside one
patient's chart without destroying its structure. The node is a professional situation, not a MIME
type, heading, or clinical topic.

## Node test, leg by leg

### Leg 1 — detection signals: passes

The schema default is protected practitioner-side material about others, recognized through
holder-role plus separately labelled subject-role structures, multi-subject registers, or
professional custody. This row changes activation by requiring a labelled external recipient in
addition to holder and subject; referral-specific labelled slots (`referred by`, `referred to`, reason,
pathway); or a reply/sent/acknowledged structure.

Those signals reject chart-native notes/plans, ordinary business mail, and patient-held copies. The
register is structured evidence, not keyword inference: “Tables matter because resumes, forms,
applications, invoices, and administrative documents often place their most useful information in
cells rather than body paragraphs.” **Pass.** The sender/recipient/subject relation plus workflow state
carries the row.

### Leg 2 — privacy rules: does not independently distinguish

Recipient service can disclose why a named person is being investigated; the register aggregates many
such relations. Yet chart, conference, and practice-side clinical administration are also protected
third-party corpora. The correspondence graph has a distinct harm shape, but `00` licenses no distinct
handling class or policy. This leg reinforces why subject/service cannot be visible folder levels; it
does not carry existence.

### Leg 3 — dimensions: unsatisfiable, not claimed as a pass

`clinical_practice` declares no fields. A template cannot put undeclared keys into `dimension_order`,
so every sibling has `[]`. Patient, recipient, direction, and function are not legal facts here, and
patient/service path labels would disclose third-party information.

The JSON's prose recommendation is non-operative: if fields later land, consider direction and
document function before subject. Today: one shallow, redacted, user-approved packet, no automatic
depth. Not time-first: “For document and record domains, project, function, or subject usually comes
before time because putting year first scatters related work across calendar folders.” This leg does
not distinguish. Overall, the node stands on leg 1 alone.

## Bottom-up corpus

The JSON carries ten concrete fixtures:

1. `Referral - Orthopaedics - Jane Doe.pdf` — labelled referral with holder, service, subject, reason.
2. `Letter to Dr Patel re Jane Doe 2026-03-04.docx` — clearest three-role directed letter.
3. `Letter from cardiology re Mr Smith.pdf` — inbound reply explicitly answering holder's referral.
4. `Your appointment - outpatient cardiology.pdf` — patient's own copy; PHR collision.
5. `Insurance medical report - consent attached.pdf` — third-party clinical report with consent and
   fee note; Finance on independent evidence.
6. `Referral letter template.docx` — blank merge template, primary false-positive fixture.
7. `sent letters log 2026.csv` — multi-subject register, decisive existence fixture.
8. `RE Referral - BROWN A.eml` — secure-message reply; attachment extracted separately.
9. `letters_to_type_20260408.m4a` — untranscribed multi-patient dictation; grouping copies no facts.
10. `scan0142.tif` — OCR addressee, `re` line, signature, fax header; no screenshot inference.

Together: labelled form/document, prose requiring interpretation, spreadsheet, email, audio, OCR,
template, reply, and multi-schema material. Every fixture separates observations from facts, writes no
path as fact, and respects the empty schema.

## Files considered and rejected

- **Blank referral template:** same layout/vocabulary, no filled subject/addressee. Independent record.
- **Patient appointment letter:** holder is addressee/subject. `medical.personal-health-records`.
- **Referral pathway PDF:** instruction about a class, no subject/event. Guideline or Reading Inbox.
- **SOAP note/treatment plan:** holder and subject, no external recipient/reply/status. Patient chart.
- **Records request cover:** purely procedural production, not clinical reason/report. Administration
  or Legal on independent evidence.
- **Practice meeting minutes mentioning referral performance:** participant/agenda/action event shape;
  referral statistics do not make minutes correspondence.
- **Consulting report with fee:** fee/addressee do not discriminate. It enters here only with patient,
  consent, and clinical-report relation; commercial scope supports consulting.
- **Fax cover alone:** wrapper without recoverable subject/body. May group; cannot inherit facts.
- **Copied clinic letter in one chart:** same bytes may support both situations. Chart context does not
  erase directed correspondence; letter body alone does not establish a register.

## Collision fixture and reciprocal boundaries

### `clinical_practice.patient-chart`

Shared bytes: **`Referral Letter - Orthopaedics.pdf`** (this row's positive fixture names the same
document shape `Referral - Orthopaedics - Jane Doe.pdf`). Body discriminates nothing.

- This row: labelled sender/addressee/subject plus sent/reply evidence.
- Chart: one subject's longitudinal dated accumulation, filed-on/chart-section structure.
- Both may hold for byte-identical copies. `duplicate_family` joins; P9 grouping copies no facts.

### `medical.personal-health-records`

Shared bytes: **`Your appointment - outpatient cardiology.pdf`** or the patient's copy of the clinic
letter.

- This row: holder in sign-off/referred-by, different subject, external recipient.
- PHR: holder in patient/`re` slot or second-person addressee, no professional author role.
- Letterhead, specialty, headings, record numbers, and patient cc discriminate neither.

The medical row does not yet name this template; R1c owes reciprocity (NJ-CP-1).

### `clinical_practice.practice-administration`

Shared shape: records-request response or chase naming subject/addressee.

- This row requires clinical reason-for-referral/report content and a directed item.
- Administration owns procedural production, invoices, appointment operations, aggregate workflow.
- Subject name alone does not move administration here; layout alone does not move this row there.

The edge is one-way from this row; R1c owes reciprocal if both stand.

### `career.consulting-client-engagement`

Shared shape: scoped third-party report with fee note.

- This row requires named patient, consent/authority, clinical content.
- Consulting requires statement of work, commercial scope, deliverable/engagement lifecycle.
- Fee, sign-off, and addressee suffice for neither.

### Meeting-record — considered, no edge

No contested bytes. Meeting event/participant/agenda/action structure and directed
sender/recipient/subject structure can coexist in a bundle, but a file does not plausibly become the
other. A meeting mentioning referrals stays minutes; a letter attached to an agenda is separately
extracted. An edge would manufacture a mutex where evidence discriminates cleanly.

## `proposed_fields`: deliberately empty

`fields: []` and `proposed_fields: []`. A template must not copy or privately extend its field-less
schema. Tempting keys were `direction`, `subject_of_record` (already proposed once at schema level),
`recipient_service`, `correspondence_status`, and clinical `document_function`. None is minted.
`authored_by` cannot carry subject/recipient and is never a destination; `institution` cannot
distinguish authoring practice from receiving service; financial `record_type` cannot silently become
clinical function. Direction/status remain observations and prose pending central adjudication.

## Grouping without propagation

Valid groups: one referral plus acknowledgement/reply; one item across dictation/draft/signed/sent
versions; one subject's outward letters; one third-party report with request/consent/invoice. These are
P9 relationships, not extraction licences. “The graph does not automatically copy those missing facts
onto sparse files.” Audio may join drafts without receiving subject; attachment extracts separately;
fax cover may join without inheriting content; chart copy does not make neighbours correspondence.
Exact reference, quoted date, thread id, or universal `version_family` beats similar names. No group is
also valid.

## Residuals and safety

- `Protected Records`: recognized letters/registers/replies without accepted group or packet.
- `Review Later`: letter-shaped material with unresolved holder/subject/addressee roles.
- `Unsupported or Encrypted`: unreadable exports, encrypted mail, unauthorized transcription.
- `Independent Records`: blank forms/templates with no subject.
- `Reading Inbox`: pathway guidance/service directories with no case.

Only `potentially_sensitive` is assigned, never a P7 class. Protection precedes model/connector use.
Raw names, body, OCR, and recipient-service relations must not enter general summaries or automatic
path labels. Empty dimensions are contract-correct and safety-conservative.

## Neighbours considered without an edge

- `legal.practice-matter-file`: court-directed report may carry Legal independently; not necessarily
  mutex, and malpractice/production owns the sharper boundary.
- `finance.insurance-healthcare`: insurer report may carry Finance facts independently, shown in the
  fixture; co-activation is not template collision.
- `hr`: occupational reports are adjacent, but no landed reciprocal contested bytes.
- `clinical_practice.case-conference`: meeting outcome and directed letter are separate artefacts.
- `clinical_practice.protocol-guideline`: referral guidance is a clean negative, not collision.
- `photos`: scan/photo capture evidence can co-activate while OCR invokes clinical protection.

## NEEDS-JOSEPH

- **NJ-CP-1 — clinician-authored versus patient-held reciprocity.** This row names PHR; PHR does not
  name it. Add reciprocal with the same holder-role discriminator, or leave one-way at the cost of a
  PHR-first review not seeing author/subject reversal.
- **NJ-CP-9 — separate from chart?** Recommendation: yes, because the multi-subject sent/answered
  register and recipient lifecycle cannot be a chart work type without loss. Folding loses direction
  and status; keeping costs overlap on identical letters, handled by duplicates and reviewable groups.
- **NJ-CP-10 — fee-bearing clinical reports.** Keep here when patient/consent/clinical evidence
  dominates; administration/consulting when procedural/commercial scope dominates. Decide whether
  this is one correspondence work type or another situation; this row mints neither field nor node.
- **NJ-CP-DIM — field-less dimension leg.** Treat CONNECTION's “or” as disjunctive (current); recheck
  all siblings as failing this leg; or lift D1 centrally, a much larger decision.
- **NJ-CP-RECIP — one-way edges.** `patient-chart` names this row, but
  `practice-administration` does not. R1c should reconcile; neither neighbour was edited here.

## What changed in this pass

Cross-checked against the files as written:

1. JSON `one_line` changed only from `Gist-level placeholder (J-IND)` to
   `Full-depth placeholder (J-IND, deepened to J-DEPTH)`.
2. JSON remains `refuse_node: false`; `fields`, `proposed_fields`, `dimension_order`, and `role_split`
   remain empty. Ten fixtures, four collisions, recognition, grouping, residuals, sensitivity, and
   open question are preserved.
3. Memo replaced: added existence charge; careful three-role test; node-test legs; fixture/rejection
   accounting; reciprocal shared-byte boundaries; meeting comparison; field-zero argument; grouping,
   safety, and explicit alternatives/costs.

**Reversed:** nothing. **Narrowed:** expressly not a referral-letter document type; it stands only as
the sender/recipient/subject correspondence workflow and register.
