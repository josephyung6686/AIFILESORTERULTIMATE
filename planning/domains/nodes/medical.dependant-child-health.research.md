# medical.dependant-child-health — R1b research notes

Node: `medical.dependant-child-health` · `kind: template` · `schema_id: medical` ·
`launch: safety` · exact roster name: `A dependant's health records`.

Outputs are this note and
[`medical.dependant-child-health.json`](medical.dependant-child-health.json) only.

## Result and node test

Verdict: **kept** (`refuse_node: false`), with no fields and no automatic folder depth.

I compared three honest treatments before writing the row:

1. **Refuse it and merge everything into the Medical default.** That would preserve the empty
   schema but erase the file-level distinction the roster assigned: a record about the corpus
   holder versus a record held for a different human patient. It would also leave no place to
   encode the proxy-access privacy boundary, the school-health collision, or the legal-authority
   collision. The recognition and privacy rules therefore do differ from the default.
2. **Recreate the legacy child and dependant-adult trees.** The legacy catalogue proposed
   `subject_person`, `guardian`, `paediatric_practice`, `visit_date`, `record_type`,
   `school_or_programme_requirement`, `carer`, `authority_instrument`, `care_service`,
   `care_period`, and `coordination_contact`, then put person and record-kind values into folder
   dimensions. D1 and PR-6 forbid Medical field rows. More importantly, those branches would put
   a patient's identity, relationship, care need, or authority status into a visible path. The
   legacy shape was evidence, not approval, and was rejected.
3. **Keep one field-less safety template covering both child and dependant-adult records.** The
   invariant is the same in both: the record identifies a human patient and independently labels
   another person's parent, guardian, proxy, representative, or carer role. This treatment allows
   structure-based protection without encoding jurisdictional age, capacity, consent, or access
   rules. It is the selected design.

The row passes the template node test on two independent limbs:

- **Detection differs.** Generic Medical protects clinical structure. This situation additionally
  requires explicit patient-versus-representative evidence or an official proxy-access workflow;
  one name, a child term, or possession is not enough.
- **Privacy differs.** A model must not infer that the corpus owner is the named parent, guardian,
  proxy, or carer, that the relationship has legal effect, or that the holder may access or disclose
  the record. Ambiguity stays protected and unknown.

The dimension limb cannot differ lawfully because Medical declares no fields. That is recorded as
`dimension_order: []`, not padded with a proposed person or record-kind key.

## Authority and project sources

- `planning/00-database-agent-product-design.md` — read completely and treated as authority.
  The three spans in `design_cite` and the Protected Records span in `falls_through_to` were copied
  verbatim and checked against this file. In particular, `00` says: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." It also says: "Privacy policy must be enforced before content reaches any model or external connector."
- `planning/01-product-design-structured.md` — used only as a locator; it does not override `00`.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, and `planning/domains/CONNECTION-EXAMPLES.md` — node test,
  no inheritance, activation/grouping separation, closed edges, safety ordering, and PR-6.
- `planning/domains/roster.json` and `planning/domains/ROSTER.md` — exact assignment and the fold
  from the legacy patient-side Medical entries into three field-less templates.
- `planning/domains/canonical_fields.json` — the authoritative 37-key catalogue. It contains no
  Medical field and no holder/subject/guardian/proxy relationship pair.
- `src/evidence_shape/vocabulary.py` — authoritative `SOURCE_TYPES`.
- `planning/overnight/council/DECISION-BRIEF.md` — D1, D2, D6, and J-IND. D1 leaves Medical
  field-less; D2 keeps handling classification outside this catalogue; D6 fixes snake_case; J-IND
  permits a useful placeholder without invented fields.
- Landed nodes read for reciprocal signals and fixture alignment:
  `medical.json`, `academic.iep-accommodation-plans.json`, `academic.k12-schooling.json`,
  `applications.k12-admission.json`, `finance.insurance-healthcare.json`, and
  `identity.core-documents.json`. `medical.personal-health-records.json` and
  `medical.wearable-health-exports.json` landed during authoring; both finished JSON and research
  notes were then read before verification. The personal-health row already names this target,
  making that collision reciprocal. `legal.estate-planning` had not landed, so its roster row was
  used and that edge remains a one-way obligation.
- Legacy medical catalogue entries were read as historical evidence only: paediatric child health,
  caregiving for a dependant, and their inbound references. None of their fields was carried.

## External research — structure only, never a legal rule

This is a high-stakes privacy seam, so I used primary or official material. The sources inform
recurring **document roles and shapes** only. They do not authorize the product to decide legal
status, consent, capacity, access rights, disclosure rights, or validity.

- [HHS guidance on personal representatives](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html)
  distinguishes the patient from a personal representative and makes the representative's scope
  dependent on the authority involved. It also describes exceptions and safety concerns. Product
  consequence: recognize labelled patient, representative, authority-basis, and scope slots; never
  infer entitlement or universalize one jurisdiction's rules.
- [NHS England proxy-access guidance](https://www.england.nhs.uk/long-read/proxy-access/)
  describes access through a proxy's own account, potentially tailored scope, identity and consent
  checks, review or withdrawal, and safeguarding. Product consequence: proxy identity, patient
  identity, scope, status, review, and withdrawal are distinct observations; none is a durable
  catalogue fact here.
- [HL7 FHIR RelatedPerson](https://hl7.org/fhir/relatedperson.html) models a person related to a
  Patient and keeps that person distinct from the target of care. Product consequence: a Patient
  plus a referencing RelatedPerson and patient-linked clinical resources is a strong structured
  detection shape, but the relation is not proof of legal authority.
- [HL7 FHIR Consent](https://hl7.org/fhir/consent.html) separates the patient or consumer,
  representative or performer, permitted actors, scope, and period. Product consequence: these are
  distinct source roles and slots; this row does not store or adjudicate them.
- [HHS and US Department of Education student-health privacy guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/ferpa-hipaa/index.html)
  confirms that student health records sit on an education/health privacy seam. Product consequence:
  school issuer and educational-eligibility evidence must stay separate from provider, patient,
  vaccine, medication, and clinical evidence. No jurisdictional regime is encoded.
- [CDC vaccination-record guidance](https://www.cdc.gov/vaccines/hcp/imz-best-practices/vaccination-records.html)
  supplies a recurring vaccination-record shape: administration detail, product or manufacturer,
  lot, and administering professional or site, with records commonly maintained for children.
  Product consequence: repeated vaccine rows plus completed patient/guardian/provider roles are a
  useful protection signal. The page's legal and operational requirements are not copied into this
  catalogue.

The JSON intentionally contains no age threshold, capacity rule, legal test, jurisdiction,
retention rule, consent rule, document identifier, detector regex, score, or confidence threshold.
The mere presence of a file never proves lawful possession or present authority.

## Bottom-up file set

Every row maps one-for-one to `file_examples`. Facts named here are canonical keys only. Medical
itself contributes no field; neighbor facts are legal only where that neighbor schema independently
activates. A residual is the safe outcome if this template does not fire, not permission to weaken
another active safety schema.

| File | Source | What is inside | Facts legal if independently supported | Must remain unknown / negative result | Inactive residual |
|---|---|---|---|---|---|
| `Immunization Record - Emma.pdf` | `text_document` | Completed child and guardian blocks, clinic attestation, repeated vaccine rows | universals only | patient, guardian, vaccine and authority facts; authenticity or completeness | Protected Records |
| `School Medication Authorization - Emma.pdf` | `text_document` | School/student, guardian, clinician, medication and timing slots | universals; `school`, `work_type` under Academic | enrollment, medical roles, medication, copied school/year | Protected Records |
| `Asthma Action Plan - Summer Camp.pdf` | `text_document` | Participant/guardian/clinician blocks and patient-specific response plan | universals only | camp event, condition, medication, person roles, condition branch | Protected Records |
| `Proxy Access Approval - Jayden.pdf` | `text_document` | Provider portal, distinct patient/proxy, basis, scope and review workflow | universals only | legal sufficiency, currency, portability, identity of corpus holder | Protected Records |
| `related-person-bundle.json` | `code_structured` | Patient, referencing RelatedPerson, and linked clinical resources | universals only | consent, custody, authority, current or complete record | Protected Records |
| `Child Portal Export.zip` | `archive` | Manifest names patient, proxy, visit, result, vaccine and access members | universals only | member facts from manifest; automatic extraction; propagation | Protected Records |
| `After Visit Summary - Noah.pdf` | `text_document` | One patient plus encounter and follow-up, but no holder role | universals only | self-versus-dependant classification without local context | Protected Records |
| `Grandma Medication Schedule.xlsx` | `spreadsheet` | Informal medicine schedule and carer initials, no labelled roles | universals only | who Grandma is; authorized carer; medical fields | Protected Records |
| `Care Plan - Mrs Li.pdf` | `text_document` | Adult client, representative/carer, provider, support and review sections | universals only | capacity, dependency, diagnosis, authority, holder identity | Protected Records |
| `Health and Welfare Power of Attorney.pdf` | `text_document` | Operative instrument, principal/agent, witness and execution structure | universals; Legal may protect independently | dependant-health activation; validity, effect, revocation, provider acceptance | Protected Records |
| `Speech and Language Evaluation - Emma.pdf` | `text_document` | School issuer, evaluator role, educational-eligibility purpose | universals; `school`, `work_type` under Academic | medical activation from credentials/topic; diagnosis | Protected Records |
| `IEP and Health Packet.zip` | `archive` | Mixed IEP, evaluation, vaccine, medication and parent-notice members | universals only on outer archive | one schema for every member; filename facts; propagation | Protected Records |
| `K12 Admission Health Form - Emma.pdf` | `text_document` | Admission target/cycle plus completed clinical and guardian zones | universals; application fields on direct evidence | admission decision, copied purpose/cycle, Medical fields | Protected Records |
| `Dependant EOB - Emma.pdf` | `text_document` | Subscriber/patient split and claim/amount columns | universals; `institution`, `record_type` under Finance | parent/proxy inference; clinical diagnosis; target activation from names | Protected Records |
| `1095-C 2025.pdf` | `text_document` | Tax/coverage form and covered-individuals table | universals; `institution`, `tax_year`, `record_type` under Finance | any listed person as a patient or care subject | Protected Records |
| `Birth Certificate - Emma.pdf` | `text_document` | Registry, registrant, parent and certification structure | universals; Identity protects independently | parent as holder/guardian/proxy; Medical activation | Protected Records |
| `Paediatric Appointment - Emma.ics` | `calendar` | Clinic, appointment-for wording and one adult contact | universals only | patient or guardian identity; attendance; diagnosis | Protected Records |
| `Your child's test results are ready.eml` | `email` | Portal sender, explicit proxy/patient roles, scope and linked result | universals only | diagnosis from subject; current access; role facts | Protected Records |
| `IMG_4418.jpg` | `image` | Camera photo of a completed child immunization card | universals; Photos capture fields on its own evidence | photo-event destination; people, patient, vaccine, guardian | Protected Records |
| `Proxy Access Screenshot.png` | `ocr` | Screen-origin evidence and truncated portal role/scope panel | universals; `media_type` under Photos | which person has which role; legal effect; missing-EXIF shortcut | Protected Records |
| `newborn-discharge-packet.pdf` | `ocr` | Distinct birthing-parent and infant patient zones with shared encounter text | universals only | copying instructions, diagnoses or roles between patients | Protected Records |
| `family-health-backup.bin` | `opaque_binary` | Unknown binary with only a suggestive filename | filesystem universals only | every medical, family, archive, app and encryption claim | Unsupported or Encrypted |
| `Blank Student Health Form.pdf` | `text_document` | Empty student, guardian, clinician, vaccine and signature slots | universals only | any completed role, care, enrollment or consent claim | Independent Records |
| `Milo - Veterinary Vaccination Certificate.pdf` | `text_document` | Animal patient/species, owner block and vaccine rows | universals only | human child/dependant-adult situation; human relationship fact | Independent Records |

### Coverage of awkward cases

- Labelled forms and unlabelled prose/spreadsheets are both represented.
- One clinical image and one OCR portal screenshot separate capture evidence from protected content.
- Two archives test manifest-only inspection and the grouping firewall.
- Native email and calendar records test structured source slots without treating source type as
  meaning.
- The EOB, school evaluation, legal instrument, tax/coverage form, birth certificate, blank form,
  and veterinary record are deliberately tempting negatives.
- School medication, admission health, image, screenshot, EOB, and mixed packet fixtures carry
  another schema on independent evidence; they use `also_schema` or legal neighboring facts without
  creating a template-level `also_holds_with` edge.
- `After Visit Summary - Noah.pdf`, the calendar item, informal spreadsheet, mixed archive, and
  newborn packet use `group_without_copying_facts: true` where context may retrieve or group a sparse
  item but cannot manufacture the holder-versus-subject fact.

## Holder, subject, proxy, and authority boundaries

This template recognizes a **document situation**, not a person's legal state.

- The patient/subject must be a human child or adult whose care is represented in the record.
  Child or dependant wording alone is not enough, and veterinary material is a negative fixture.
- The other role must be independently labelled as parent, guardian, proxy, representative, carer,
  or an equivalent role in the source. A second name can instead be a clinician, emergency contact,
  guarantor, subscriber, witness, translator, or recipient.
- A relationship record is not an authority record. An authority record is not proof of validity,
  effectiveness, current scope, or provider acceptance. A proxy-access approval from one service is
  not automatically portable to another service.
- Possession is not a role. The product cannot infer that the corpus owner is any named person, that
  the file was lawfully obtained, or that its contents may be disclosed.
- Minors, adolescents, adults with support needs, and adults represented under formal instruments
  may have very different rules across services and jurisdictions. This row encodes none of those
  rules. It recognizes only the file's explicit role and workflow structure and then protects it.

## Fields, proposed fields, role split, and dimensions

All four are deliberately empty:

- `fields: []` — templates reference their schema and never copy fields. Medical has none.
- `proposed_fields: []` — D1 as narrowed and PR-6 forbid Medical field rows. A proposed field would
  be the same forbidden field arriving one level lower.
- `role_split: []` — although holder-versus-subject is the organizing seam, a role split must name
  canonical field keys. No canonical `subject`, `holder`, `patient`, `guardian`, `proxy`, `carer`,
  `authority_basis`, or `access_scope` key exists for Medical. Inventing the pair would reverse D1.
- `dimension_order: []` — there is no destination-eligible Medical key. An empty order also avoids
  leaking a person, relationship, condition, care need, proxy status, provider, or record kind in
  the path. It is not time-first; one protected subject or episode is more coherent than a year.

Tempting existing keys were rejected too. Canonical `record_type` is scoped to Finance, not a generic
document-kind escape hatch. `people` is a Photos search/privacy field and cannot become patient or
holder. `purpose` remains Applications-scoped under PR-1. `authored_by` is a creator role and `00`
disfavours creator identity as a destination. None solves this situation.

## Recognition discipline

The deterministic list is a set of **co-occurring structures**, not token or score rules. Its core
shape is:

1. an explicit patient or subject block;
2. an independently labelled parent, guardian, proxy, representative, or carer block; and
3. clinical, care-plan, or provider proxy-access structure.

Structured Patient/RelatedPerson bundles, completed school health forms, proxy-access records,
care plans, archive manifests, native messages, and OCR regions are variations of that shape. The
row authors no regex, gazetteer contents, product identifiers, or detector thresholds.

The model list is deliberately broader than the deterministic list but has a stricter gate. Model
use is local or explicitly permitted by user policy, bounded to the smallest necessary dossier,
and allowed to return unknown. Raw names, relationships, diagnoses, identifiers, legal documents,
and proxy-access details are never default cloud content. The model may identify evidence and
ambiguity; it may not make a legal or clinical determination.

The `never_alone` list is especially strict because false certainty is dangerous here. Names,
family terms, a second contact, a subscriber/patient pair, a parent signature line, a covered-person
table, a legal seal, a clinic name, a school name, medication vocabulary, filenames, folder names,
sessions, and source types all fail alone. Missing EXIF and dense OCR also fail, as `00` requires.

## Grouping firewall

Grouping supports retrieval without converting relationship context into facts:

- a user may accept one subject's protected record set without the system writing the subject or
  making a person-named folder;
- a care episode may join linked orders, results, summaries and correspondence, but a sparse member
  does not inherit a patient, provider, date, or diagnosis;
- a school, admission, IEP, insurance, or legal packet may include a medical record, while each file
  retains only its own independently supported facts;
- a proxy-access lifecycle may connect request, approval, review and withdrawal without asserting
  current legal authority; and
- a singleton remains valid. Protection never depends on reaching a group-size threshold.

`falls_through_to` contains only Protected Records. The only fixtures using another residual are the
opaque unreadable file and the independently blank or non-human negatives; those residuals are not
alternative homes for a file once this safety template is active.

## Edges and reciprocity

Template edges point only to roster template ids. `also_holds_with` stays empty because CONNECTION
restricts that edge to schemas. Files with disjoint Academic, Applications, Finance, Identity,
Legal, or Photos evidence express that through `also_schema` and their canonical facts instead.

| Edge | Why it is needed | Reciprocal state at authoring |
|---|---|---|
| `academic.iep-accommodation-plans` | School educational-eligibility evaluation versus clinic patient/diagnosis/referral structure | already names this target |
| `academic.k12-schooling` | completed clinical school form versus enrolled-student record | already names this target |
| `applications.k12-admission` | physician health attachment versus admission-role workflow | already names this target |
| `finance.insurance-healthcare` | dependant EOB subscriber/patient split versus dependant clinical record | already names this target |
| `medical.personal-health-records` | identical clinical content; holder is patient versus explicitly distinct patient/proxy roles | landed during authoring and already names this target; reciprocal |
| `legal.estate-planning` | operative health-authority instrument versus provider access workflow or patient-specific care record | target file not yet landed; one-way for R1c |

The collisions are mutex at the evidence-item level, not a denial that two schemas may protect one
file. For example, Finance can write `institution` and `record_type` from an EOB's claim structure
while Medical protection remains active on independent clinical evidence. The collision prevents
subscriber and patient names from being reused as holder/proxy proof.

## Neighbors considered that did not get an edge

- **`identity.core-documents`** — a birth certificate is the strongest tempting negative, but its
  civil-record structure and a completed clinical/proxy record use different evidence. Parent and
  child names alone activate neither. Example-level `also_schema: identity` is sufficient; a
  standing template mutex would overstate the overlap.
- **`legal.personal-legal-matters`** — custody and guardianship orders can accompany child health
  records, but `legal.estate-planning` is the sharper roster neighbor because it expressly includes
  powers of attorney and advance directives. The packet can group both without another near-duplicate
  edge.
- **`medical.wearable-health-exports`** — a proxy may export a dependant's wearable data, so both
  situation descriptions can be true on disjoint evidence. Template-level `also_holds_with` is not
  legal, and treating them as mutex would be wrong. The landed wearable row protects bulk data on
  its own app-, device-, telemetry-, and export-manifest structure and likewise authors no edge to
  this target.
- **Photos templates** — a camera photo or screenshot carries genuine capture facts independently;
  `also_schema: photos` on the fixtures is the right mechanism. Capture origin is not a competing
  medical destination once protected content appears.
- **`identity.credentials-passwords`** — a portal access export may include authentication material,
  but the access credential should be recognized and protected from its own key or credential
  structure. A portal name or account label creates no standing situation edge.
- **`academic.homeschool`** — parent-held school material is not enough. The completed health form
  collision is already represented through `academic.k12-schooling`; institution-versus-homeschool
  organization does not change the medical evidence.

## Files considered but not added as fixtures

- **A physician or caregiver vCard.** A contact record can name a clinic and relationship label but
  proves no patient, proxy, or care episode. `identity.core-documents` already covers privacy-first
  contact exports; adding the file here would teach only source-type ambiguity.
- **A recorded consultation.** `audio_video` is plausible in real corpora, but without a transcript
  it provides duration and container evidence only. `00` gates transcription behind explicit
  privacy and compute policy. The target therefore does not claim the source type in this pass.
- **A wearable activity archive.** It belongs to the assigned wearable-health template, whether the
  wearer is the holder or someone else. This row should not steal the format family before that
  sibling lands.
- **A generic nutrition or fitness article.** It is a health topic, not a patient record. The blank
  school form and veterinary certificate are stronger target-specific negatives.
- **A guardianship order.** It is useful as an accepted packet member but is covered more sharply by
  the estate-planning collision and the power-of-attorney fixture. A court order alone cannot make a
  clinical record or prove current provider access.
- **A clinician-only calendar contact.** A provider name and appointment time are already covered by
  the calendar fixture and `never_alone`; a second fixture would add format, not a new evidence shape.

## Privacy and safety posture

- Protection occurs before model use, cloud use, connectors, placement, preview, or grouping
  automation.
- Raw names, dates of birth, relationships, diagnoses, medications, identifiers, OCR, patient-portal
  details, legal-authority documents, and group memberships stay local.
- The catalogue asserts only `potentially_sensitive`. It does not author or repeat any P7 handling
  class, and it does not interpret sensitivity from a path.
- A local model is not automatically authorized merely because it is local. Product policy still
  decides whether the raw protected dossier may be inspected.
- No filename, folder, archive path, account label, or session becomes a fact or a prompt payload.
- No person, condition, proxy status, care service, diagnosis, or authority appears in an automatic
  folder dimension.

## NEEDS-JOSEPH — this node only

1. **Evidence retention granularity.** When the detector finds a patient/proxy role pair, may P4/P6
   store the matched role and clinical text locally, or only a protected marker and evidence
   locations? This sharpens Medical's existing local-evidence question.
2. **Future canonical role vocabulary.** If D1's Medical deferral ever lifts, should the system store
   patient/subject, holder, representative role, relationship, authority basis, or access scope at
   all? If any keys land, are all permanently destination-ineligible? Until that decision, no
   proposed field or `role_split` is legal.
3. **Model policy for protected ambiguity.** What explicit policy permits local-model review of an
   ambiguous proxy, minor, capacity, confidential-section, or mixed-family packet? Is redacted cloud
   review ever allowed, and who defines the redaction contract? The provisional row defaults to no
   cloud dossier.
4. **One template or two.** The selected fold treats child and dependant-adult records as one
   holder-versus-subject situation. Split them only if corpus evidence shows materially different
   detection structures or privacy workflows; do not split them merely to encode jurisdictional age,
   consent, capacity, or access rules.
5. **Shallow forever or only for now.** If Medical fields later exist, does this template remain a
   flat protected area because branch names leak, or may a user explicitly enable subject or record
   depth under a redacted local-only UI? The current answer is no automatic depth.

None blocks this R1b row. The conservative launch behavior is field-less activation, immediate
protection, local-only ambiguity review under explicit policy, no legal inference, no automatic
folder depth, and Protected Records as the sole designed residual.
