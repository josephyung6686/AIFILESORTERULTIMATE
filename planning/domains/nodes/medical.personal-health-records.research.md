# medical.personal-health-records — R1b lab notes

Roster row: `kind: template`, `schema_id: medical`, `launch: safety`, `provenance: design`.
Verdict: **node accepted** (`refuse_node: false`).

## Sources actually used

### Binding local authority

- `planning/00-database-agent-product-design.md` — read in full. It controls the
  observation/fact split, the field allow-list, the Medical safety posture, grouping without fact
  propagation, template semantics, the nine residual names, local/cloud boundaries, UI redaction,
  and abstention. Curly double-quoted spans in the JSON are reserved for verbatim text from this
  file; domain-research wording is not placed inside quotation marks.
- `planning/01-product-design-structured.md` — relevant numbered renderings only: facts and
  schemas (§3), templates and tree depth (§5), the residual library (§7), and privacy (§8.4). It
  was used as a locator and never as higher authority than `00`.
- `planning/prompts/ALIGNMENT.md` — template versus schema, one file/many facts, activation versus
  grouping, safety domains, and residual separation.
- `planning/domains/_CONTRACT.md` — especially rules 5, 8, 10–15. D1/PR-6 forbids Medical field
  rows; templates reuse their schema; `collides_with` is same-kind; `also_holds_with` is
  schema-to-schema; `role_split` belongs to canonical fields; P7 owns handling classes.
- `planning/domains/CONNECTION.md` — node test; activation steps; safety split; grouping firewall;
  closed edge vocabulary; PR-2, PR-4, PR-6, and PR-8.
- `planning/domains/CONNECTION-EXAMPLES.md` — passport safety fixture, calendar/source-type
  negative, sparse grouping without fact copying, and Finance/Medical insurance co-activation.
- `planning/domains/roster.json` — exact assignment and output paths; the two sibling Medical
  templates; required Finance and Identity neighbours; required `Protected Records` residual.
- `planning/domains/canonical_fields.json` — six design universals plus the project-wide additions
  and domain keys. It contains no Medical field. That absence is binding, not a research gap this
  row may repair.
- `src/evidence_shape/vocabulary.py` — exact fourteen-member `SOURCE_TYPES` vocabulary.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 keeps placeholder fields empty; D2 makes
  P7's `(file_id, content_hash)` `ClassificationRecord` authoritative; D4 keeps jurisdiction out
  of fields and dimensions; D6 keeps snake_case; J-IND rewards honest gist coverage rather than
  field inflation.
- `planning/26-research-dispatch-state.md` and a freshly generated
  `planning/domains/dispatch/make_prompt.py medical.personal-health-records` prompt — exact R1b
  checkpoint, assignment, procedure, output shape, and done-when list.

### Landed nodes and history

- `nodes/medical.json` and its research notes — broad Medical safety activation, empty fields,
  empty dimensions, schema-level Finance/Identity/Academic/Research boundaries, and the explicit
  rule that detection is not extraction.
- Landed inbound template neighbours, read but not changed:
  `career.employment-records`, `finance.insurance-healthcare`,
  `finance.insurance-personal`, `medical.dependant-child-health`,
  `medical.wearable-health-exports`, `photos.camera-events`, `photos.home-video`,
  `photos.scanned-documents`, `research.ethics-compliance`, and
  `research.lab-notebook-protocols`. Every one already named this target in a collision; this row
  reciprocates all ten.
- Other landed rows used to test boundaries, not rewritten: `identity`,
  `identity.core-documents`, `finance`, `photos`, `photos.screenshot-captures`, `research`,
  `academic.coursework`, and `career`.
- `git blame` ties the roster row to commit `13bff36`: a safety template on Medical, with portal
  exports, lab results, prescriptions and visit summaries in the hint; Finance and Identity as
  mandatory neighbours; `Protected Records` as the required residual.
- Two superseded catalogue rows were harvested bottom-up, not adopted:
  `med.personal-health-record` in `06-healthcare-medicine.json` and `pers.medical-record` in
  `04-personal-household.json`. Their concrete files and role problems survived; their private
  schemas did not.

### Primary issued-record sources

These sources establish that the fixtures and boundaries resemble files people actually receive.
They do not override `00`, do not define product policy, and are paraphrased rather than quoted.

- [HHS — individual access to personal health information](https://www.hhs.gov/hipaa/for-professionals/faq/2042/what-personal-health-information-do-individuals/index.html)
  describes a broad U.S. designated-record-set example spanning medical records, clinical lab
  reports, X-rays, treatment consent and clinical notes, while also including billing, payment,
  claims and insurance records. That breadth is why this catalogue needs a clinical-record
  template and a separate Finance insurance template rather than pretending the legal-access set
  is one folder situation.
- [NHS — GP health record in the NHS App](https://www.nhs.uk/nhs-app/help/health-records-in-the-nhs-app/gp-health-record/)
  lists prescriptions, appointment notes, test results, documents, vaccinations, conditions and
  allergies. It supports the ordinary portal artifacts in the file list and also shows that a
  portal view can be partial rather than a complete lifetime record.
- [VA — My VA Health user guide](https://www.va.gov/files/2023-09/UserGuide_My_VA_Health_Final.pdf)
  shows downloadable visit summaries, clinical notes, discharge instructions, scanned documents,
  radiology/pathology reports, medication lists, dosage/directions, prescription identifiers and
  provider information. It supports the visit-summary, radiology, medication and secure-message
  fixtures.
- [VA — what its downloadable lab report contains](https://www.myhealth.va.gov/en/ss20190520-ways-to-check-va-lab-tests)
  identifies test name, performed date, location, ordering/performing provider, result and reference
  range. That is the concrete basis for the lab-table recognition structure; the values remain
  observations because Medical has no fields.
- [ONC — view, download and transmit test method](https://healthit.gov/test-method/view-download-and-transmit-to-3rd-party)
  tests both human-readable ambulatory/inpatient summaries and machine-readable CCD documents. It
  supports treating a PDF/text summary and a structured XML companion as real sibling artifacts,
  not as a file-format-defined domain.
- [CDC — vaccination records](https://www.cdc.gov/vaccines/hcp/imz-best-practices/vaccination-records.html)
  gives a real administration-record shape: administration date, manufacturer, lot, and the person
  administering. It supports the immunization-row fixture without turning any of those observations
  into a Medical fact.
- [Apple Support — Health data export](https://support.apple.com/guide/iphone/share-your-health-data-iph5ede58c3d/26/ios/26)
  documents an XML export of health and fitness data. That is positive evidence for the sibling
  `medical.wearable-health-exports` boundary, not evidence that every health-shaped XML belongs to
  this provider-record template.
- [CMS Blue Button API — sample data](https://bluebutton.cms.gov/api-documentation/explore-the-api/)
  provides a synthetic ZIP of JSON Patient, ExplanationOfBenefit and Coverage resources. It is the
  concrete claims/coverage counterexample for `finance.insurance-healthcare`: FHIR-shaped JSON and a
  patient resource do not by themselves make a provider-authored clinical record.

## Node test — why this is not Medical's default template

This is the closest node-test call in the assignment. The Medical schema already recognizes a
broad safety union: clinical documents, claims/benefits material, school health material, consumer
health exports, appointments and health-sector mail. It has the same empty dimensions and the same
protection-first posture as this row. Repeating that union would fail the template test.

The accepted row is narrower in a load-bearing way:

- **This template requires a personal provider-record situation.** Its positive structures are a
  provider- or portal-authored clinical document about a patient: visit/discharge summary, result,
  medication or immunization record, diagnostic report, continuity-of-care summary, or records
  fulfillment packet.
- **It explicitly excludes three Medical siblings/adjacent situations.** A direct proxy or
  representative marker points to `medical.dependant-child-health`; app/device provenance plus
  repeated telemetry points to `medical.wearable-health-exports`; claim/member/payment structure
  points to `finance.insurance-healthcare` even when clinical words occur.
- **It refuses subject-role guessing.** A labelled patient block can activate Medical protection,
  but without direct self/proxy evidence or user confirmation it cannot select this template over
  the dependant sibling. That abstention is a real privacy rule, not an empty label.
- **It keeps topic out.** Anatomy teaching, clinical research, public guidance, veterinary records
  and medical advertising can be medically dense while never being the holder's personal health
  record.

So detection differs even though dimensions and high-level privacy inherit. The template remains
useful with no fields: it narrows review, supplies collision discriminators, keeps clinical records
out of claims/device/research branches, and offers the protected residual without exposing a
clinical folder taxonomy.

## Observation/fact boundary and fields

`fields: []` and `proposed_fields: []` are deliberate.

The legacy rows proposed or asserted all of these: `subject_person`, `patient_role`, `record_source`,
`facility`, `provider`, `record_date`, `document_type`, `record_type`, `episode`, and
`body_system_or_specialty`. None survives as a field here:

- D1 as narrowed and PR-6 forbid Medical field rows. Putting a key under `proposed_fields` would
  reverse that decision through a template instead of through the schema decision site.
- `record_type` is canonical but explicitly financial in its current role. Reusing it for clinical
  document kind would collapse two roles into one column, the exact field-identity failure D6 is
  meant to stop.
- `institution` is the financial issuing institution, not a provider/facility field. Reuse would
  let a lab, insurer, hospital and bank occupy one role.
- `authored_by` is producer identity, not patient, provider or record subject, and it is never a
  destination dimension.
- `creation_date` is a file-version timestamp, not encounter date, collection date, report date,
  administration date or export period.
- A subject/holder key would be both the main sibling discriminator and a highly identifying
  search field. Whether it exists, and whether it participates in a `role_split`, is Joseph's
  schema-level decision.

Consequently, a positive fixture's `facts_legal` contains only universal facts. A fixture that
also supports Photos, Finance, Research, Career, Identity or Academic lists that schema in
`also_schema` and may list only that other schema's canonical fields. Medical observations never
appear in `facts_legal`.

The sixteen strings under `work_types` are recognition and review vocabulary only. There is no
Medical `work_type` or clinical `record_kind` field, so the engine cannot store those strings as
facts or turn them into folder levels.

## Bottom-up corpus coverage

The JSON carries twenty-two concrete fixtures:

1. provider-issued after-visit summary;
2. CBC laboratory report with units and reference ranges;
3. consolidated patient-download report with mixed provider and self-entered sections;
4. machine-readable CCD XML companion;
5. current/historical medication list;
6. immunization record that also resembles an identity credential;
7. radiology report with findings and impression sections;
8. unlabelled referral letter whose roles require bounded local interpretation;
9. records-request archive inspected only through its manifest;
10. portal email whose attachment remains a separate file;
11. provider calendar attachment that cannot prove attendance;
12. patient-portal screenshot recovered through OCR;
13. phone photograph of a laboratory-result letter with genuine camera facts;
14. appointment audio with no authorized transcript, requiring abstention;
15. explanation of benefits — Finance neighbour, not this template;
16. personal-injury claim with a provider-authored treatment section;
17. employer leave form with a clinician certification page;
18. child immunization record reached through direct proxy access — dependant sibling;
19. consumer health-app export archive — wearable sibling;
20. blank study consent — Research ethics neighbour;
21. coded-subject sample log — Research notebook neighbour; and
22. anatomy lecture — medical topic but Academic record.

Together they cover labelled forms and prose, human-readable and structured exports, screenshot
OCR, a photographed page, archive, spreadsheet, email/message semantics, audio/video policy,
same-schema siblings, same-evidence collisions, multi-schema files, sparse grouping, and the
medical-topic false positive. No example writes a path as a fact.

## Privacy and safety consequences

- The catalogue sets only `sensitivity: potentially_sensitive`. It does not assign, enumerate or
  translate P7 handling classes.
- D2's `ClassificationRecord` keyed `(file_id, content_hash)` is authoritative. This row does not
  run the detector, populate the record, mirror a class, or infer a class from extension, source
  type, filename, topic or template match.
- Recognition exists to get the file onto the protected path. Medical's empty field list means
  detection unlocks universal facts plus protection, not clinical extraction.
- Every `needs_llm` item is conditional on P7 first. Default cloud prompting is unavailable;
  permitted use is local or explicitly authorized/redacted under user policy, and the model can
  only propose template plausibility or group decisions with citations.
- Raw path, complete extracted text, OCR, hashes, EXIF/GPS, group memberships and sensitive values
  remain local under `00`. General summaries show neither raw clinical content nor an unredacted
  list of protected filenames.
- `dimension_order` is empty because no field is legal and because diagnosis, condition, provider,
  patient or record-type folder labels would themselves disclose the protected content. A flat
  protected area is the current recommendation; user-created structure remains possible after
  explicit review.
- `falls_through_to` contains only `Protected Records`. It is an opt-in residual candidate, not an
  automatic move permission. An unreadable file whose medical-looking filename cannot establish
  Medical goes instead through the residual workflow for unsupported/encrypted material.

## Edges and reciprocity

All collision targets are roster template ids and all signals name the discriminating evidence.
This row reciprocates every already-landed inbound edge:

| Already-landed neighbour | Discriminator retained here | Reciprocity now |
|---|---|---|
| `finance.insurance-healthcare` | claim/member/payment table versus clinical result, medication or narrative structure | yes |
| `finance.insurance-personal` | loss/adjuster/settlement structure versus provider/patient/encounter structure | yes |
| `career.employment-records` | employer leave workflow versus clinician certification | yes |
| `photos.camera-events` | capture metadata versus clinical OCR; protection decides home first | yes |
| `photos.scanned-documents` | page-capture geometry versus clinical document content | yes |
| `photos.home-video` | media container versus policy-authorized clinical content; otherwise abstain | yes |
| `research.ethics-compliance` | study/protocol/participant role versus patient/provider/treatment role | yes |
| `research.lab-notebook-protocols` | project/sample/operator provenance versus patient/provider/encounter provenance | yes |
| `medical.dependant-child-health` | direct patient access versus proxy/guardian role | yes |
| `medical.wearable-health-exports` | provider-authored clinical record versus app/device telemetry | yes |

Two additional evidence-backed edges are intentionally one-way until R1c or the missing neighbour
rows land:

- `identity.core-documents` — bearer credential function versus clinical administration/history;
  and
- `photos.screenshot-captures` — screen origin versus protected clinical content.

`also_holds_with` is empty because CONNECTION restricts that edge to schema pairs. Real
co-activations are shown per fixture through `also_schema`; schema-level Medical joins already live
on `medical.json`. `role_split` is empty because it belongs in `canonical_fields.json` and neither
side of a Medical subject/holder split exists there.

## Neighbours considered that did not get an edge

- **`medical`** — `schema_id` is the join. A template cannot collide with the schema it uses and
  must not copy the schema's edges or fields.
- **`finance` and `identity` schemas** — same-kind rules prohibit template-to-schema collisions.
  Their schema-level Medical joins already exist; the concrete Finance and Identity templates
  above carry the situation-level mutexes.
- **`legal.personal-legal-matters` and `legal.estate-planning`** — a consent, advance directive,
  injury file or health-care authorization may be both legal and medical on disjoint evidence.
  That is not item-level mutex, and template rows may not author `also_holds_with`; the existing
  Medical↔Legal schema join is the proper place.
- **`applications.purpose-packet`** — a health record can be a supporting member of an application
  packet, but packet purpose is P9 context and must not be copied onto the protected record. No
  collision.
- **`academic.coursework`** — the anatomy deck is a tempting false file, but direct course and
  lecture structure makes it Academic while medical topic contributes nothing to this template.
  The broader Medical↔Academic schema collision already records the topic boundary; another
  one-way template edge would add no new discriminator.
- **`finance.receipts-expenses`** — a pharmacy receipt can contain a drug name and prescription
  identifier while remaining a transaction record. A genuine provider prescription structure can
  co-exist on disjoint zones; the Finance schema and the healthcare-insurance template already own
  the protection/transaction boundary, so this row does not add a weaker duplicate edge.
- **contacts (`.vcf`)** — a clinician contact is not a health record. `00` keeps contact exports
  privacy-protected rather than using them as folder-proposal evidence, and Identity owns the
  contacts file-kind row.

## Files considered and rejected from the JSON

- a public disease fact sheet, treatment guideline and saved medical article — Reading Inbox or
  Research reading material; topic only;
- a blank patient-intake form — no patient or encounter and no evidence the holder completed it;
- a veterinary discharge summary — clinically shaped but the patient is not a person; a future
  veterinary template or residual decision is needed rather than forcing it here;
- a pharmacy sales receipt — purchase structure, not a provider-authored clinical record unless a
  separate dispensing section supplies the stronger evidence;
- a personal symptom diary or therapy journal — real private material, but opening free prose to
  choose a template raises the schema's unresolved local-extraction question and should not be
  normalized through one R1b row;
- a clinician/practice chart export containing many patients — professional custody and role are
  different from a person's own record; J-IND's clinician-practice world is the future home;
- an encrypted `medical_records.pdf` or ZIP — filename alone cannot establish Medical; represent
  it under Unsupported or Encrypted until the user attaches it to a protected group;
- a calendar reminder and a provider contact card — source types and workflow clues, not clinical
  records; and
- a DICOM file with no approved dedicated extractor and no companion manifest — metadata-only,
  protected if user-attached, otherwise unsupported rather than treated as empty or inferred from
  `.dcm`.

## Contract tensions

- The dispatch prompt's generic node test says refuse a template if it repeats its schema default.
  This row would fail if it copied the Medical schema's broad union. It is accepted only because
  the narrower provider/patient clinical-record boundary and the self-versus-proxy abstention rule
  materially change detection.
- The prompt skeleton makes `also_holds_with` and `role_split` appear available on every node;
  CONNECTION narrows them to schema↔schema and canonical-field↔canonical-field respectively.
  CONNECTION wins, so both arrays are empty.
- The prompt asks for recommended dimensions even on a safety template. `_CONTRACT` rule 10 and
  CONNECTION PR-6 forbid all Medical fields, while safety independently argues against visible
  clinical path labels. Empty dimensions are therefore the complete answer, not missing work.
- External sources describe legal/access sets and product exports, not this product's ontology.
  They validate the fixtures only. `00`, ALIGNMENT and CONNECTION remain the policy and edge
  authority.

## NEEDS-JOSEPH — personal health records

- **NJ-med-phr-1 · Template choice without a subject field.** When clinical evidence activates
  Medical but the file does not say direct patient versus proxy access, should P10 show this row
  and `medical.dependant-child-health` as unresolved alternatives, or suppress both until explicit
  user confirmation? The current row keeps the file protected and unresolved.
- **NJ-med-phr-2 · Medical field vocabulary.** If D1's deferral lifts, decide centrally whether
  subject-of-record, holder role, provider, clinical record kind and encounter date become
  canonical fields, and whether holder/subject requires a `role_split`. This template proposes none.
- **NJ-med-phr-3 · Protected filesystem depth.** Even with fields, may any patient, provider,
  specialty, condition, diagnosis or record-kind value become a visible path label, or must Medical
  remain flat behind one redacted protected node? Until answered, `dimension_order` stays empty.

No R1b implementation blocker remains: all three questions have conservative defaults that preserve
protection, abstention and an empty Medical allow-list.
