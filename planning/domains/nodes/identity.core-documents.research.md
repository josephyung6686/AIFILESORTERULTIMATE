# R1b lab notes — `identity.core-documents`

Date: 2026-08-22  
Assignment: `kind: template` · `schema_id: identity` · `launch: safety`  
Result: **keep the node** (`refuse_node: false`), but keep it field-less, dimension-less and protection-first.

## Node test

This row is not merely the Identity schema under a second name. It has a narrow file-level job: recognize recurring structures of passports, government identity cards, birth/citizenship evidence and civil-status records used as identity evidence; protect them before interpretation; and own VCF/contact-export routing without using the people inside those files to propose folders. The neighbouring Identity rows have materially different signals: immigration/visa is a workflow of applications, permissions and adjudications, while credentials/passwords is authentication material such as key blocks, recovery codes and password-manager containers.

Three implementation approaches were tested:

1. **Refuse the row and let the Identity schema catch everything.** This would erase useful boundaries between core civil evidence, immigration workflows, authentication secrets and the roster-assigned contact-file owner. It would also leave `.vcf` ownership vague.
2. **Recreate the legacy holder → document tree.** The pre-R0 row proposed document type, holder role, issuing authority, validity period and document status. Carrying those forward would contradict D1's field deferral, turn raw civil attributes into catalogue language and expose sensitive document/holder labels through folder paths.
3. **Keep a safety-only template.** This is the chosen design. It recognizes enough structure to enter a protected state, writes no Identity facts, recommends no destination dimensions, forbids default cloud prompting, and uses `Protected Records` when there is no accepted deeper group.

The third approach is useful even without a folder tree. It supplies a conservative detector boundary, prevents camera/screenshot/session evidence from sweeping identity scans into ordinary media folders, distinguishes person credentials from lookalike insurance/vehicle/professional/academic cards, and gives VCF/contact exports an explicit privacy-preserving owner.

## Authority and repository sources read

- `planning/00-database-agent-product-design.md` — read in full; authoritative.
- `README.md` — product goals and standing constraints.
- `planning/01-product-design-structured.md` — only the relevant contact-file, safety-domain, residual and privacy sections; `00` wins.
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/_CONTRACT.md`.
- `planning/domains/CONNECTION.md` and all fixtures in `CONNECTION-EXAMPLES.md`.
- `planning/26-research-dispatch-state.md` and `planning/domains/dispatch/r1b-swarm.workflow.js`.
- the complete stamped output of `python3 planning/domains/dispatch/make_prompt.py identity.core-documents`.
- `planning/overnight/council/DECISION-BRIEF.md`: D6 requires snake_case; D2 says classification authority is injected rather than authored as a handling class; D1/PR-6 leaves Identity without field rows; J-IND keeps independent records available without weakening safety.
- `planning/domains/roster.json`, `canonical_fields.json`, and `src/evidence_shape/vocabulary.py`.
- the complete landed Identity schema node and its research companion, plus the relevant edge and fixture sections of landed same-kind nodes cited in the collision audit.
- committed pre-R0 history for `pers.identity-document` and `comms.contact-record`. The former attempted five Identity fields; the latter documented VCF structure and privacy. Both were superseded, but their evidence was examined rather than silently discarded.

## External evidence used

The sources below verify recurring **container and document structures** only. They do not justify authenticity judgments, document-number extraction into new facts, jurisdiction-specific regexes, layout coordinates, form numbers, validity periods, age rules, evidence grades or confidence thresholds.

- [ICAO — Machine Readable Travel Documents, Doc 9303](https://www.icao.int/publications/doc-series/doc-9303) is the primary international specification family for machine-readable travel documents. Its [Part 4 specification](https://www.icao.int/publications/documents/9303_p4_cons_en.pdf) supports the recurring passport data-page distinction between a visual inspection zone and a machine-readable zone. The node uses that structural cluster, not fixed coordinates or a country-specific parser.
- [U.S. Department of State — Citizenship Evidence](https://travel.state.gov/en/passports/apply/help/citizenship-evidence.html) confirms that birth certificates, consular birth records, naturalization certificates and citizenship certificates are recurring forms of primary citizenship evidence. The page also reinforces the difference between a document's evidence role and a bare name/date observation.
- [USCIS — Certificate of Naturalization](https://www.uscis.gov/es/node/73963) confirms the certificate as documentary proof and illustrates a recurring authority, person-identification, photograph/signature, certificate and seal structure. The node does not infer current status or authenticity from a scan.
- [IETF RFC 6350 — vCard Format Specification](https://www.rfc-editor.org/info/rfc6350/) supplies the content-level container grammar for vCard, including its boundary, version and formatted-name properties. That justifies inspecting the container rather than trusting a `.vcf` extension.
- [NIST SP 800-63A-4 — Identity Proofing and Enrollment](https://pages.nist.gov/800-63-4/sp800-63a.html) distinguishes physical/digital evidence and evidence issued by authoritative or credible sources. It is used only to discipline the issuer/evidence distinction; this catalogue does not encode NIST assurance levels, validation procedures or scoring thresholds.
- [UK General Register Office — Guide to Birth Certificates](https://assets.publishing.service.gov.uk/media/69987e2e047739fe61889edd/Birth_certificates_leaflet_Web._Oct_25_v.3.pdf) provides a second jurisdiction's civil-registration example and demonstrates why certificate layouts, roles and wording vary. Recognition therefore depends on a labelled registry/certificate cluster, not a single national layout.

## Bottom-up file set

The JSON records the complete observation/fact split and abstention rules for these files.

| Concrete file | Why it matters |
|---|---|
| `Passport - biodata page.pdf` | strongest native-text passport structure; validity and authenticity remain unproved |
| `passport scan.pdf` | OCR route; absent text layer and scanner metadata cannot activate Identity |
| `IMG_2231.jpg` | genuine camera EXIF plus passport content; document safety outranks photo-event placement |
| `driver-licence-front-back.heic` | front/back government credential; exact vehicle-registration lookalike boundary |
| `Certified Birth Certificate.pdf` | registry/certification structure and legal co-activation; recorded event differs from certificate issue |
| `Certificate of Naturalization.pdf` | citizenship evidence with person, authority, signature and seal roles |
| `Social Security Card.jpg` | tax/social identifier card; name-plus-number is not enough and does not make a Finance record |
| `Mobile Driver Licence Wallet.png` | screenshot origin plus protected credential; pixels do not prove cryptographic validity |
| `Alice Chen.vcf` | one complete vCard container; no person-named folder and no identity claim about the contact |
| `contacts-backup.vcf` | repeated containers and revision/category properties; never one folder per card/category |
| `Contacts Export.csv` | structured contact-header cluster versus CRM/roster/directory lookalikes |
| `Identity Copy Request.eml` | enclosing native email becomes protected only because the attachment is independently recognized |
| `Core Identity Documents.zip` | mixed protected archive; manifest inspection does not establish holder, authenticity or safe unpacking |
| `ID card scan.jpg` | accepted application-packet member; purpose and target institution must not copy onto it |
| `Nursing License 2026.pdf` | professional-licence false positive with issuer, seal, number and expiry |
| `Insurance Card Front.jpg` | healthcare coverage false positive with person, issuer and identifier |
| `Vehicle Registration Card.jpg` | government card false positive; vehicle/owner structure is not a person credential |
| `Official Transcript with ID Photo.pdf` | academic false positive with person, photo, seal and identifier |
| `Family Scan Batch.zip` | scan-session context cannot turn every member into a family photo or an identity document |
| `Passport Copy - WhatsApp.jpg` | messenger packaging and stripped metadata cannot lower protection or explain purpose |
| `Name Change Order.pdf` | one file can support identity use and record a legal proceeding without copying legal roles into Identity |
| `visa-application-packet.zip` | core passport member versus immigration workflow expressed by the packet |

The set covers native text, OCR, camera images, screenshots, vCard, CSV, email and archive paths. It includes singletons, multi-file groups, context-only membership, false positives, multi-schema files, unsupported authenticity questions and protected fallthroughs.

## Scope and neighbour boundaries

### Core documents versus immigration/visa

A passport, birth certificate or citizenship certificate is core evidence because of its own issuer/bearer/civil-status structure. A visa or immigration situation additionally requires application, permit, entry-record, appointment, sponsorship or adjudication structure. A passport alone never proves an immigration workflow. In a mixed packet, the outer packet and relevant members may activate immigration while the passport remains an independently protected core document; packet purpose is not copied onto it.

### Core documents versus credentials/passwords

The word *credential* is dangerously broad. This node covers government/civil evidence whose own function is identifying the bearer or establishing civil status. Authentication secrets require a password-manager schema, key block, recovery-code set, token seed, certificate/key container or similarly specific authentication structure. The words identity, certificate, key or credential alone activate neither template.

### Core documents versus contact exports

The roster assigns the legacy contacts evidence owner to this row, so `contacts` is a legal source type here. That is routing and protection ownership, not a claim that every contact is an identity document or that a person's name/email/phone becomes an Identity fact. VCF/CSV contents can be parsed locally for usefulness, but the design expressly excludes them from folder proposals. A `.vcf` extension is only a clue; a complete vCard container or repeated/structured contact-export pattern is required.

### Core documents versus legal, finance, academic and photo material

- A civil certificate or name-change order may also be legal, but legal procedure/party/order structure and identity-evidence structure are separate signals.
- Insurance cards, loan/application forms, payroll/tax records and vehicle registrations can all carry names and identifiers. Their plan/debt/payment/employment/vehicle structures decide those situations; the token itself decides nothing.
- Transcripts and professional licences may show a portrait, birth date, seal and identifier. School/course/award or professional-authorization structure keeps them outside this node.
- Camera, scanner, messenger and screenshot origin are real observations but cannot demote a recognized identity document into an ordinary media destination. Protection is evaluated first.

## Field analysis — none proposed

The current Identity schema intentionally contains no field rows. This node therefore has:

```text
fields: []
proposed_fields: []
dimension_order: []
```

The superseded `pers.identity-document` row attempted `document_type`, `holder_role`, `issuing_authority`, `validity_period` and `document_status`. They are not carried forward:

- `document_type` would immediately become a sensitive branch label and is not required for protection.
- `holder_role` invites a repeated name or packet context to become a holder fact.
- `issuing_authority` is a useful observation but does not justify a shared Identity dimension by itself.
- `validity_period` conflates issue, expiry and jurisdiction-specific rules, and a scan cannot establish current validity.
- `document_status` would require authoritative validation/revocation evidence, not appearance or OCR.

The node may still write canonical universal facts supported by the file: `file_type`, filesystem `creation_date`, `language`, `duplicate_family`, `version_family` and `sensitivity_status`. Examples that genuinely co-activate another schema may write that schema's fields independently, such as Finance `institution`/`account_type`/`record_type` on an insurance card or Academic `school`/`work_type` on a transcript. They do not become Identity fields and are never copied from a neighbouring group.

R1c should retain the five legacy concepts as research evidence if it revisits Identity, but should not treat their pre-R0 existence as approval. Any future field proposal must show a privacy-safe product need across multiple nodes and explain how raw identifiers, names and civil attributes stay out of paths and ordinary summaries.

## Recognition and abstention boundary

Deterministic recognition uses clusters, not tokens:

- travel-document title/issuer, labelled bearer slots, portrait/signature regions and machine-readable structure;
- government identity-card title/issuer, labelled bearer attributes and document/validity slots;
- civil-registry title/authority, labelled registrant/event/role slots and certification block;
- citizenship/naturalization title/authority, person-identification block and issuance/seal/signature block;
- tax/social identifier card heading plus issuer, holder and identifier slots in the card's own structure;
- complete vCard boundaries plus version and formatted-name properties, or repeated complete containers;
- a multi-column contact-export header cluster, with concrete header vocabularies deferred to detector implementation.

Names, addresses, dates of birth, portraits, signatures, opaque numbers, issuer names, seals, barcodes, filenames, extensions, OCR density, scanner metadata and parent folders are all never-alone signals. A local/explicitly permitted model may help with partial, multilingual or mixed material, but safety activation occurs before interpretation. The model cannot infer authenticity, current status, holder identity, cryptographic validity, packet purpose or a folder path.

## Template decision

There is no automatic destination order. D1 leaves the schema without legal destination fields, and the product's privacy rule makes an empty order affirmatively safer: a branch named for document type, holder or citizenship status discloses protected content even if the file itself remains local. Contacts are specifically barred from folder proposals.

The safe current flow is:

```text
recognized protected record → accepted protected group if one exists → otherwise Protected Records
```

Grouping can still join a credential's front/back/rescans through universal duplicate/version evidence; join a certified copy with its translation; retain a protected item inside an accepted application/legal/loan/immigration packet; or retain an address-book export with its manifest/revisions. Group membership never writes the group's label onto the file, and a protected singleton is valid. Time is metadata-only, not a destination dimension.

## Edges authored

The node authors sixteen same-kind `collides_with` edges. Twelve were reciprocal at the final edge audit:

- `academic.transcripts-credentials`
- `applications.purpose-packet`
- `career.employer-side-hiring`
- `career.employment-records`
- `finance.insurance-healthcare`
- `finance.loans-mortgage`
- `finance.vehicle-records`
- `photos.camera-events`
- `photos.family-archive`
- `photos.messenger-export`
- `photos.scanned-documents`
- `identity.immigration-visa`

Four are explicitly outward discovery obligations:

- `career.credentials-licenses` had landed but did not yet name this row. A board-issued professional licence can share the authority, person, portrait, number, seal and validity structure of a government credential; authorization-to-practise versus civil/bearer identity is the discriminator.
- `photos.screenshot-captures` had landed but did not yet name this row. The shared item is a screen-origin digital credential; screenshot evidence cannot override protection or prove credential validity.
- `identity.credentials-passwords` was roster-valid but its node file had not landed. The collision is civil evidence versus authentication secrets despite shared identity/credential/certificate vocabulary.
- `legal.personal-legal-matters` was roster-valid but its node file had not landed. The collision is a civil-status/identity instrument that may also record a proceeding or order.

R1c should require reciprocity or remove a pair after evidence review; this row does not pretend those four are already symmetric. No schema id appears in `collides_with`. Because a template cannot author schema-to-schema co-activation, `also_holds_with` is empty. Per-file `also_schema` fixtures record independently supported Photos, Finance, Academic, Career, Legal or College Applications activation, while the landed Identity schema owns its schema-level relationships.

## Neighbours considered but not edged

- **`finance.personal-records`** — general account statements can contain identity data, but the sharper collisions are insurance, loans and vehicle records. A name or national identifier on a Finance document is already excluded by the never-alone rule.
- **`photos.social-media-export`** — messenger export is the more concrete shared evidence item for transmitted identity images. Broad social-media packaging does not need another edge.
- **other legal templates** — estate, lease and agreement packets can contain an ID copy, but packet membership is handled by independent activation and no-copy grouping. Personal legal matters is the sharper civil-order boundary.
- **`medical.personal-records`** — medical files may contain a name, birth date and patient number, but the healthcare insurance card is the most tempting card-shaped collision. Medical content does not resemble an identity credential once structure is required.
- **`code`** — cryptographic certificates and key files are better handled by the credentials/passwords sibling boundary. This core-document row should not collide broadly with every code or config artifact containing the word certificate.
- **`Protected Records`** — this is a residual, not a domain collision. It is the required and only broad fallthrough for the row.

## Files considered and rejected from activation

- professional licence or membership card — issuer/name/number/expiry is insufficient; require the card's civil/government identity function;
- healthcare insurance card — plan/member/group/coverage structure is Finance/healthcare evidence;
- vehicle title or registration card — vehicle/ownership/registration structure is not bearer identity;
- academic transcript, diploma or student card — school/course/award structure wins unless a separate government credential is embedded;
- bank statement, loan form, payroll statement or tax return — a national identifier inside another record does not turn the record into the identifier card;
- generic portrait, signature image or passport-style photograph — may join an accepted credential group but cannot activate alone;
- generic certificate, seal, QR code, barcode or card-shaped graphic — structurally ubiquitous;
- file named `passport.pdf`, `IDs.zip` or `contacts.vcf` with unreadable or contradictory content — filename/extension cannot rescue it;
- event roster, CRM export or employee directory with one `Name` or `Email` column — not a contact export without a broader person/contact header cluster;
- calendar reminders, expiry reminders and appointment messages — planned events are not the underlying identity document.

## Provenance, quote discipline and safety

Only two JSON `design_cite` spans are direct quotations from `00`; both were checked byte-for-byte against the authoritative file. One establishes immediate protection for scanned identity-like material. The other assigns VCF/contact extraction to a privacy-protected, no-folder-proposal path. All concrete recognition structures, examples and collision signals use provenance `inference`; no external standard is represented as product-design authority.

This node assigns the catalogue sensitivity value `potentially_sensitive` and **no P7 handling class**. The distinction is deliberate: classification authority is injected elsewhere under D2. Operationally, the evidence is among the corpus's sharpest—names, birth data, portraits, signatures, government identifiers, addresses, citizenship/status evidence and contact graphs—so protection precedes model access and placement. Raw values remain local, general summaries require redaction, and cloud prompting is never the default.

## NEEDS-JOSEPH / merge tension

1. **Protected path depth.** Should a protected identity area expose any default document-type or holder depth when the branch labels themselves reveal sensitive content? This node recommends no automatic depth until a product-wide privacy decision says otherwise.
2. **Identity fields after D1.** If field research reopens, does Identity need any stored fields at all? The legacy five-field set is evidence, not approval. In particular, document number, holder and civil-status facts should not emerge merely because OCR can read them.
3. **Permitted local-model policy.** May a local model inspect ambiguous protected documents by default, or must every model invocation require explicit per-policy authorization? The node is closed to default cloud prompting either way.
4. **Contact ownership is a roster constraint, not semantic fusion.** R1c should preserve one source-type owner for `.vcf`/contact exports while keeping contact people out of Identity facts and folder proposals. If ownership moves later, this boundary must move explicitly rather than being duplicated.

There is no blocker to landing this safety node. Its limitation is intentional and visible: it provides protection, recognition, collision discipline and residual routing, but it does not manufacture an Identity filing taxonomy while field and privacy authority remain unresolved.
