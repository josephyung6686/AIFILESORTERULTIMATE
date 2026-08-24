# identity.immigration-visa — lab notes

Date: 2026-08-22

Output: [`identity.immigration-visa.json`](identity.immigration-visa.json)

Roster row: `identity.immigration-visa`, `kind: template`, `schema_id: identity`, `launch: safety`

## Binding sources read

- `planning/26-research-dispatch-state.md` and the live R1b workflow script
- the exact stamped assignment from `planning/domains/dispatch/make_prompt.py`
- `planning/00-database-agent-product-design.md`, read in full
- the assigned sections of `planning/01-product-design-structured.md`
- `planning/prompts/ALIGNMENT.md`
- `planning/domains/_CONTRACT.md`
- `planning/domains/CONNECTION.md` and all eight fixtures in
  `planning/domains/CONNECTION-EXAMPLES.md`
- the D1, D2, D6, D4, and J-IND ratifications in
  `planning/overnight/council/DECISION-BRIEF.md`
- `planning/domains/roster.json`, `planning/domains/canonical_fields.json`, and
  `src/evidence_shape/vocabulary.py`
- landed neighbors, especially `identity.json`, `legal.json`,
  `applications.purpose-packet.json`, `academic.study-abroad.json`,
  `travel.bookings-confirmations.json`, `travel.trip-photos.json`,
  `career.employment-records.json`, and `career.employer-side-hiring.json`

The precedence used was `00`, then ALIGNMENT, then CONNECTION and its fixtures, then the stamped
prompt. CONNECTION is more specific than the prompt on edge kinds and on the field-less safety
placeholder rule.

## Official artifact research

Only official government sources were used for external fact checking. They were used to verify
which files and records people actually receive or retain, not to encode legal advice, eligibility,
deadlines, retention rules, or jurisdiction-specific field vocabularies.

- The US Department of State [DS-160 application page](https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/forms/ds-160-online-nonimmigrant-visa-application.html)
  and [DS-160 FAQ](https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/forms/ds-160-online-nonimmigrant-visa-application/ds-160-faqs.html)
  establish the submitted application confirmation or barcode page, interview scheduling, and fee
  step as ordinary artifacts of one visa workflow.
- USCIS describes receipt and approval notices, appointment notices, and evidence requests in its
  official [Form I-797 types and functions](https://www.uscis.gov/node/44651) and
  [Form I-797C notice guidance](https://www.uscis.gov/node/44883). The node generalizes those
  lifecycle functions rather than treating US form numbers as fields or universal vocabulary.
- Immigration, Refugees and Citizenship Canada documents the
  [biometric instruction letter](https://www.canada.ca/en/immigration-refugees-citizenship/services/biometrics/how-to-give.html)
  and the later passport-request, decision, and refusal correspondence on its
  [visitor-visa next-steps page](https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada/after-apply-next-steps.html).
- GOV.UK documents an eVisa as a digital record of identity, immigration status, and conditions,
  and explains the view-and-prove flow on its [eVisa guide](https://www.gov.uk/evisa) and
  [status-sharing page](https://www.gov.uk/evisa/view-evisa-get-share-code-prove-immigration-status).
  This supports saved HTML and portal-screenshot examples while also showing why codes and live
  status must not become ordinary catalogue facts.
- US Customs and Border Protection provides a printable arrival or admission record and separates
  it from travel-history assistance on the [official I-94 service](https://i94.cbp.dhs.gov/I94/)
  and [I-94 automation fact sheet](https://www.cbp.gov/document/fact-sheets/i-94-fact-sheet).
  That distinction is why the node includes an admission record but rejects an airline itinerary
  as immigration evidence.
- The education seam was checked against the UK
  [Student visa course and CAS guidance](https://www.gov.uk/student-visa/course) and Canadian
  [study-permit document guidance](https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/study-permit/get-documents.html).
  A school-issued acceptance, enrolment, or sponsorship record may support an immigration filing,
  but it retains its Academic or Applications reading and does not become government-issued status.

The cross-jurisdiction comparison mattered. Paper confirmation pages, mailed notices, secure-account
letters, saved status pages, physical cards, passport vignettes, and electronic admission records
are all real. Their names, identifiers, and workflows differ. The JSON therefore encodes structural
roles such as issuing authority plus applicant or case reference plus lifecycle function, and does
not hard-code one country, one form series, or one route list.

## Node test and alternatives

Three approaches were considered.

1. Refuse the row and fold all material into `identity.core-documents` or the Identity schema
   default. This would preserve the empty field and dimension surface, but it would erase a real
   workflow boundary. A passport biographical page is a durable identity proof. An application
   confirmation, biometrics notice, evidence request, decision, digital status record, and entry
   record form one authority-facing lifecycle with different anchors and different collision risks.
2. Put the packet on College Applications or Legal, or mint immigration-specific fields so it can
   branch by applicant, destination, route, case, stage, status, or validity. This fails the binding
   architecture. PR-1 keeps `purpose` Applications-scoped, D1 and PR-6 keep Identity and Legal
   field-less, and D4 makes jurisdiction a value rather than a field or dimension.
3. Keep a distinct safety template on `identity`, with richer workflow recognition, grouping,
   collision, and privacy rules while authoring no fields and no dimensions. This is the implemented
   approach. It differs from the schema default on detection and neighbor boundaries, so it passes
   the template node test without reversing the safety deferral.

The assignment already fixed the roster row and requested this R1b design. That serves as approval
for the third approach; the two-file ownership rule forbids a separate design document.

## Bottom-up file set

Seventeen concrete fixtures are in the JSON. Together they cover the required happy paths and the
uncomfortable ones.

- `Visa application confirmation.pdf` — labelled submitted form, applicant slots, reference, and
  barcode; only universal facts become legal under Identity.
- `Biometrics instruction letter.pdf` — official instruction notice; it must not be mistaken for a
  file containing the biometric measurements themselves.
- `Visa interview appointment.eml` — structured sender, subject, appointment details, and attached
  confirmation; email is a source type, never the meaning.
- `Request for additional evidence.pdf` — formal evidence request that can also activate Legal on
  its own content; requested documents do not inherit packet facts.
- `Visa decision letter.pdf` — approval or refusal artifact with review language; the result and
  status remain observations because both safety schemas are field-less.
- `eVisa status - saved page.html` — a real digital-status artifact that must not be treated as a
  live status query or a place to store a reusable access code.
- `Residence permit front and back.jpg` — image or scan with both capture and permission evidence;
  Photos may retain `media_type`, while Identity keeps protection.
- `Arrival and admission record.pdf` — border-authority record, deliberately separated from a
  carrier itinerary and from an informal travel-history export.
- `Visa application fee receipt.pdf` — one file that can carry Finance facts from its transaction
  structure and Identity protection from its explicit application linkage.
- `immigration_submission.zip` — mixed archive manifest inspected without unpacking; composition is
  a packet clue and never a fact-propagation licence.
- `Certificate of Enrollment for Visa Application.pdf` — the reciprocal study-abroad seam. School,
  term, and work type remain Academic facts; passport and consular observations remain protected.
- `Employer support letter for work permission.pdf` — Career and Identity may co-activate, but the
  letter does not grant permission and the Career placeholder writes no fields.
- `Portal status screenshot.png` — OCR plus positive screen-origin evidence; raw pixels and OCR stay
  local, and a status line is not a legal catalogue fact.
- `Flight confirmation - HKG to LHR.pdf` — tempting travel neighbor that does not activate Identity.
- `Graduate admission offer with visa guidance.pdf` — Applications artifact whose generic visa
  paragraph does not make it an immigration record.
- `Visitor visa guide.pdf` — public guidance, not a personal case; it falls to Reading Inbox.
- `Application Materials.zip` — password-protected archive whose filename cannot establish purpose;
  it falls to Unsupported or Encrypted.

Specific candidates rejected from the shipped set:

- A plain passport biographical page belongs to `identity.core-documents`; the immigration row
  needs a permission, application, decision, status, or entry function.
- A card statement from the Visa payment network belongs to Finance. This is the strongest reason
  the word `visa` is never-alone evidence.
- A blank government visa form and a downloaded instruction booklet are reference material until
  applicant or submission evidence appears.
- A boarding pass, hotel confirmation, or flight itinerary remains a travel transaction even when
  it shares a destination and session with the application.
- A generic university acceptance or employer offer remains Applications, Academic, or Career
  unless the file itself states an immigration submission role.
- A practitioner copy inside a client matter is organized by `legal.practice-matter-file` when
  positive practice custody and work-product signals exist; the same government notice in the
  person’s own records remains this template.

## Fields and dimensions

`fields` and `proposed_fields` are both empty. This is deliberate.

The inherited Identity field set is empty under D1 and PR-6. Tempting concepts include the
applicant, issuing authority, application linkage, permission category, decision or status,
sponsor role, and validity. Recording any of them here would turn a template agent into the author
of the deferred Identity schema. It would also make the most privacy-loaded values in the corpus
queryable without a ratified storage policy.

Existing canonical keys do not solve the problem:

- `purpose` is College-applications-scoped under PR-1 and cannot be cloned or silently widened.
- `target_university`, `application_cycle`, and `application_document_type` describe admissions,
  not a government permission workflow.
- `institution` and `record_type` are Finance fields and are legal only on independently evidenced
  fee or transaction records.
- `school`, `term`, and `work_type` remain Academic facts on an enrolment certificate.
- `event` and `location` do not turn an admission record into a travel template.
- `jurisdiction` is explicitly a value and never a field or destination dimension under D4.

The empty `dimension_order` follows mechanically. A template may branch only on fields its schema
declares, and the schema declares none. The safety result points the same way: a branch label naming
a visa category, refusal, sponsor, or status discloses the protected fact through the filesystem
tree before anyone opens a file. The prose recommendation is one shallow protected area, with depth
only after an explicit user choice and a later field/privacy decision. Time is not first because
this is one workflow or status record rather than capture-defined media.

## Recognition and privacy boundary

The deterministic families are structural rather than lexical:

- official authority plus applicant or travel-document slot plus labelled application reference;
- official notice plus case linkage plus a lifecycle function;
- permission or digital-status proof with separate bearer and status regions;
- border authority plus admission-record structure;
- official email sender plus case action and attached notice;
- explicit school, employer, or family sponsorship for an immigration filing;
- a coherent archive manifest with an in-file anchor.

Every tempting shortcut is listed in `never_alone`: visa vocabulary, country, nationality, person
name, document number, case reference, seal, barcode, fee, flight, source type, extension, filename,
folder, session, missing EXIF, OCR density, and an encrypted filename.

The privacy rule is intentionally stricter than ordinary template research:

- The fixtures use generic synthetic filenames and no real identifiers.
- Identity protection precedes every model and placement path.
- Raw paths, complete text, OCR, hashes, EXIF, GPS, group memberships, user edits, and raw values
  stay local.
- A filename, thumbnail, status label, family relationship, sponsor, or case summary can itself be
  a disclosure and is redacted in shared UI by policy.
- `needs_llm` names recognition problems, not cloud authorization. Local interpretation or
  abstention is the default. Any allowed external assistance would still require the product’s
  separate consent gate and bounded redaction policy.
- `sensitivity` is only `potentially_sensitive`. No P7 handling class, alias, ranking, or detector
  outcome is authored here.

## Edges and neighbor decisions

`collides_with` contains only roster templates, as CONNECTION requires.

- `identity.core-documents` — same bearer-document shape; identity or citizenship proof versus
  permission or entry function is the discriminator.
- `applications.purpose-packet` — same heterogeneous member composition; educational submission
  evidence versus government immigration workflow evidence is the discriminator.
- `academic.study-abroad` — reciprocal with the landed row; enrolment function versus permission
  function on a visa-facing school certificate.
- `travel.trip-photos` — reciprocal with the landed row; genuine camera facts cannot pull a
  photographed visa or permit into a trip event.
- `legal.practice-matter-file` — same case documents, but positive practitioner custody and legal
  work product distinguish a practice matter from personally held paperwork.

Edges deliberately not written:

- `legal.personal-legal-matters` — an evidence request, refusal, review, or appeal may genuinely
  activate both Identity and Legal. That is schema co-activation, not a template mutex. The JSON
  records it with `file_examples[].also_schema` and leaves schema edges to the schema rows.
- `travel.bookings-confirmations` — its landed research already records the correct boundary. A
  booking records transport or lodging; a visa or admission record evidences permission or status.
  A passenger name and destination activate neither Identity nor a shared purpose.
- `photos.scanned-documents` and `photos.screenshot-captures` — capture origin may activate Photos
  on disjoint evidence. The core-documents and trip-photo seams already carry the discriminators;
  adding another edge would repeat them.
- `identity.credentials-passwords` — an eVisa page may offer a share-code control and an account may
  require a login, but this template holds the status record, not a credential store. Any visible
  access code is a raw sensitive value to redact; a separate password-manager export, recovery-code
  file, or authentication key belongs to the credential template on its own evidence.
- `applications.graduate-professional` and `applications.undergraduate-packet` — admission files can
  support an immigration packet without becoming immigration records. The packet-level confusion is
  already represented once against `applications.purpose-packet`.
- `career.employment-records` and `career.employer-side-hiring` — work authorization or sponsor
  evidence can co-activate Career and Identity. Holder-side custody may change the useful group, but
  the document does not become one schema instead of the other.
- `finance.receipts-expenses` — an application-fee record legitimately carries Finance facts and
  Identity protection on disjoint evidence, so a mutex edge would be wrong.

`also_holds_with` is empty because CONNECTION restricts it to schema pairs. Real co-activations are
shown only through `file_examples[].also_schema`. `role_split` is empty because it belongs between
canonical field keys and this row declares none. `parent_id` remains `null` because R1b never authors
browse shelving. `shares_field` is not serialized because it is derived-only.

The landed reciprocal pairs are `academic.study-abroad` and `travel.trip-photos`. The three edges
toward `identity.core-documents`, `applications.purpose-packet`, and `legal.practice-matter-file`
remain one-way until those missing or previously completed rows are reconciled in R1c. No neighboring
file was modified.

## Residuals

- `Protected Records` is the primary home for any recognized but ungrouped personal immigration
  record.
- `Unsupported or Encrypted` represents an unreadable or password-protected packet without forcing
  it open.
- `Reading Inbox` catches public guidance that does not describe the holder’s case.
- `Receipts and Confirmations` catches an isolated fee, courier, or travel transaction when no
  immigration workflow is evidenced.
- `Temporary Screenshots` catches a sparse portal capture whose origin is known but whose content
  does not establish the domain.

These are residual names from the closed nine-name library, not roster nodes or extra domains.

## Binding tensions carried forward

1. The generic Identity schema already mentions one immigration packet in its grouping reasons.
   This row remains non-duplicate because it adds the real authority-notice lifecycle, digital
   status and entry-record shapes, holder-versus-practice custody, and concrete template collisions.
   If R1c concludes those differences are not enough, refusal remains preferable to a hollow row.
2. The prompt asks templates to recommend dimensions, while D1 and PR-6 make every Identity
   dimension illegal. The binding contract wins and the order is empty.
3. The prompt exposes `also_holds_with` on every node, while CONNECTION limits it to schemas. The
   array is empty and fixture-level `also_schema` carries the evidence instead.
4. The packet plainly has a purpose, but PR-1 forbids an immigration-specific clone and NJ-3 leaves
   the scope unresolved. Group coherence may be recorded; no `purpose` fact is written.
5. Official sources show that jurisdictions use different forms, references, and digital products.
   The node stores no jurisdiction-specific field or route list and authors no detector regex.

## NEEDS-JOSEPH — this node only

1. Does Identity ever gain any field rows when D1 is revisited, and if so which immigration values
   are safe to store as facts rather than only as local evidence?
2. Does `purpose` remain College-applications-scoped, or may a non-admissions packet such as this one
   use the same canonical field? PR-1 is followed until that decision changes.
3. May a protected immigration area carry any visible folder depth, and may any model path inspect
   this material beyond local processing or explicit bounded consent? The current row answers both
   conservatively: no dimensions and no cloud-model path by default.
