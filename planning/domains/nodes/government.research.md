# Government and public administration — J-DEPTH research memo

Status: **KEEP NARROWLY as a fieldless placeholder schema anchor.**

The row passes only on a role-and-custody distinction: it is the public authority's own operational record of exercising, developing, administering, or accounting for a public function. It is not a bucket for documents issued by government, documents about law or policy, a public-sector employer, or a regulated organization's copy of a filing. `government.json` is the complete serialized recommendation; this memo explains the evidence, exclusions, neighbour seams, and unresolved decisions.

## Sources and limits

The binding sources were `planning/00-database-agent-product-design.md`, `planning/01-product-design-structured.md`, `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md`, `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `planning/overnight/council/DECISION-BRIEF.md`, `src/evidence_shape/vocabulary.py`, and the stamped `government` dispatch prompt. The landed `finance.crypto-assets`, `medical.personal-health-records`, and `legal.practice-matter-file` rows were depth references; `business_operations` and its children were used for current house shape and neighbouring boundaries, not as depth exemplars.

The concrete government document families are grounded in named, widely used administrative artifacts rather than a claim that one jurisdiction's law governs all: bills, amendments, committee papers, vote records and transcripts; notices of proposed rules, comments and final instruments; consultation documents and response analyses; agendas, committee reports and minutes; tender notices, received bids and evaluation records; planning applications, permits, inspections and decisions; information requests, search schedules, disclosure logs and review responses; census instruments, methodology and controlled-data documentation; nomination, polling, ballot-account and count records; constituent or ombudsman casework. This pass does not derive deadlines, validity, legal effect, disclosure duties, procurement rules, election rules, retention schedules, or public-body status from those names.

All quotations in the JSON are exact spans from `00`. The design itself does not name a Government schema, so this row is `provenance: proposal` and `design_cite: null`. Design quotations support product-wide evidence, grouping, privacy, and residual behavior only; none is presented as proof that Government belongs in the schema set.

## Node test, argued in full

### Distinct field set

The schema cannot honestly declare a distinct three-to-six-field set in this round. The roster instructs it to write no field rows under PR-6, `inherited_field_keys` is empty, and the contract forbids minting private schema keys to rescue a legacy industry label. Therefore `fields: []`, `proposed_fields: []`, and `template.dimension_order: []` are deliberate.

That would normally argue for refusal. The narrow reason to keep the row is that this is a roster-approved **placeholder schema anchor** for children and its activation changes something material even before government-specific fields exist: which child templates become plausible, which files receive a protected posture, and which holder-role interpretation is allowed. Activation still writes only the six universal facts used consistently in every fixture: `file_type`, `creation_date`, `language`, `duplicate_family`, `version_family`, and `sensitivity_status`.

No child may repair this lack of schema fields by inventing `authority`, `jurisdiction`, `case_number`, `programme`, `permit_type`, `rulemaking_stage`, or `record_type`. Work types remain values. Jurisdiction remains unavailable as a field or dimension. A later canonical decision may add a small role-safe vocabulary once for the schema; until then the safe structure is recognition without government fact writes.

### Distinct detection signals

The default test is not entity recognition. A public-body name appears as issuer on a citizen's permit, counterparty on a supplier's tender, regulator on a company's filing, employer on a resume, party in a judgment, venue in research, and publisher of reading material. Those are values or observations in another holder's record. They cannot activate Government.

The distinct positive signal is an **authority-side workflow**. It combines public-body status with a producer, custodian, administrator, decision-maker, legislature, regulator, records-holder, official-statistics producer, election administrator, or public-casework role. The structures are observable: received-submission registers, evaluation and approval sheets, official bill-version sequences, rulemaking identifiers across proposal/comments/final instrument, authority decision blocks, disclosure search and redaction schedules, count reconciliations, or public case-system exports. Holder role is sometimes explicit in account export metadata, mailbox direction, file-plan structure, authorized-officer blocks, or repeated internal workflow artifacts. Where the role is not explicit, the system abstains.

This prevents the schema from becoming the 574-style industry category. A public-sector workplace folder does not fire because its employer is government. A legal opinion about a regulator does not fire. A corporate compliance return does not fire because the addressee is an authority. A downloaded government report does not fire because the publisher is public.

### Distinct recommended dimensions and privacy rules

No dimensions are serialized because there are no declared destination-eligible fields. The prose structure, deferred rather than smuggled into keys, is: public function or bounded proceeding/programme/case first; exact reference or cycle next; document function next; time only later. Named citizens, applicants, bidders, witnesses, complainants, staff, voters, or respondents are never the default folder dimension. The design supports the general ordering rule exactly: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

Privacy is materially different from a generic public-sector industry label. Government files are not presumptively public merely because some final outputs are published. The same packet may hold received consultation responses, unsuccessful bids, declarations of interest, complainant identities, citizen authorization, enforcement evidence, restricted microdata, election operations, addresses, identity copies, or internal pre-decisional analysis. The schema therefore uses `potentially_sensitive`, local-first evidence processing, redacted summaries, and no default cloud escalation for protected content. Published laws, reports, notices, and statistics can be ordinary reading files, but they do not lower the posture of the authority's working packet.

### Verdict

Keep narrowly. Refuse any broader reading. If implementation cannot enforce the authority-side role precondition or the protected default, this node should be disabled rather than degraded into a government-name classifier.

## Bottom-up files considered

The JSON contains sixteen fixtures with observation/fact separation. Their purposes are:

1. `Rulemaking 2026-14 - Response to Comments and Final Instrument.pdf` tests a regulator-side rulemaking sequence and independent Legal co-evidence without asserting validity or applicability.
2. `Council Housing Committee - Agenda Pack - 18 August 2026.pdf` tests public-body governance plus a sensitive appendix. The public meeting label cannot sanitize named residents.
3. `Tender Evaluation Panel - IT Service 2026.xlsx` tests buyer-side procurement, structured tables, supplier confidentiality, evaluator declarations, and the Business Operations seam.
4. `Permit Case PL-2026-184 - Officer Report and Decision.docx` tests an authority-side application and decision record, including a labelled form-like structure and operative-status abstention.
5. `FOI 26-041 - Search Schedule and Redaction Log.xlsx` tests public-records administration, structured search evidence, redaction uncertainty, and the Legal/privacy seam.
6. `Census 2026 - Enumerator Training and Collection Manual.pptx` tests official-statistics production, presentation notes, and a public manual that may fall to reading when authority-side custody is absent.
7. `Election Count Reconciliation - North District.csv` tests structured election administration without inferring certification, correctness, or voter choice.
8. `Casework 8841 - consent and agency chase.eml` tests email roles, a named citizen, case authorization, and protected processing without deciding legal entitlement or consent validity.
9. `Inspection visit - Licensing Case LC-1198.ics` tests calendar structure and grouping without copying a licence, event-occurrence, or compliance fact.
10. `Consultation responses export - transport strategy.zip` tests a purpose-coherent archive packet and the design rule that the manifest is inspected without unpacking.
11. `Screenshot 2026-08-19 - Grants portal assessment.png` tests OCR, screen-origin evidence, Photos coactivation, and the inability of portal text alone to prove funder-side custody.
12. `Annual Return 2026 - Example Holdings - filing acknowledgement.pdf` is the corporate/regulatory collision fixture. The registry is an issuer/counterparty; the held record is the company's Business Operations artifact.
13. `Passport Renewal - application and appointment confirmation.pdf` is the identity/civic collision fixture. Government is issuer; the individual's record stays Identity and Protected Records.
14. `Community Association AGM Minutes 2026.pdf` is the Nonprofit collision fixture. Identical governance furniture belongs to a private association even when it receives a public grant.
15. `Supreme Court judgment - Example Agency v Example Ltd.pdf` is the Legal/reference collision fixture. Government as party and court publication do not make it authority administration.
16. `Citizen case management backup.gdb` tests an opaque source system export. Its filename cannot manufacture contents or role; it remains unsupported without an approved extractor.

The set covers labelled forms, prose, tables, presentations, email, calendar, OCR, images, archives, structured data, and opaque binaries. Extensions are never sufficient. The schema also plausibly receives contacts and audio/video, but those are not expanded into extra fixtures because a contact list is especially dangerous as an activation source and a recording requires the same authority-side workflow anchor as its transcript.

## Files considered and rejected

- An enacted statute, final regulation, judgment, gazette notice, official report, statistics bulletin, or policy paper downloaded from a public website is normally Reading Inbox unless an accepted authority-side workflow or research group says otherwise. Publication is not custody.
- A permit, licence, visa, identity card, tax notice, benefit decision, voter confirmation, registry extract, or appointment confirmation held by the subject is a personal administrative, Identity, Legal, Finance, Academic, Medical, or residual record. Government is only issuer.
- A corporate annual return, regulated filing, audit response, compliance certificate, bid submission, contract invoice, or grant report held by the company is Business Operations. Government is addressee, regulator, buyer, or funder.
- A private charity's, union's, church's, campaign's, standards body's, accreditor's, or membership association's minutes and election papers are Nonprofit even when statutory language, public grants, or public-service contracts appear.
- A law firm's regulatory submission, advice, hearing bundle, public-law litigation file, or client correspondence is Legal or a professional matter. A government agency as party or regulator is insufficient.
- A public employee's resume, employment contract, payslip, pension statement, training certificate, expense claim, or personal calendar is Career, HR, Finance, or a personal record. Public-sector industry does not convert holder role.
- A university course file, public-school report, museum image, archive catalogue, or library reading list is not Government solely because the institution is state-run. The relevant Academic, Photos, Research, or reading evidence remains independent.
- A political party manifesto, campaign leaflet, advocacy submission, lobby paper, petition, or community organizing pack is Nonprofit/civic or reading material unless it is held inside an evidenced authority consultation or legislative workflow.
- A blank official form or template has no completed authority-side case. Its typography, seal, and labels can support retrieval but not activation.
- A live case-management database, mailbox, procurement platform, records system, or election system is a source system, not one file. Only a bounded export with readable evidence is in scope.

## Reciprocal neighbour boundaries

### Legal

Government → Legal: an authority's own rulemaking, enforcement administration, decision workflow, information-request processing, or public casework stays Government even though it contains law, reasons, hearings, or legal advice. Legal language is a work type/value signal, not a schema switch.

Legal → Government: a citizen's legal form, a lawyer's client matter, a public judgment downloaded for reference, or litigation against an agency stays Legal/read-only. The same `Rulemaking 2026-14...pdf`, `Permit Case PL-2026-184...docx`, `FOI 26-041...xlsx`, `Casework 8841...eml`, and `Supreme Court judgment...pdf` bytes are discriminated by holder role and workflow, not the named agency.

This is a mutex collision at default activation. Individual fixtures can still record independent `also_schema: legal` evidence because one file may contain legal structure; that does not erase the holder-role boundary or authorize legal-status conclusions.

### Business Operations and corporate/regulatory filings

Government → Business Operations: a public authority's buyer-side tender evaluation, regulator-side filing receipt register, public-body committee pack, grant-administration file, or programme budget stays Government when the authority role is evidenced.

Business Operations → Government: a company's tender response, annual return, regulatory submission, compliance pack, supplier contract, or grant report stays Business Operations. The same `Tender Evaluation Panel...xlsx` and `Annual Return 2026...pdf` fixture types can exist on both sides. Sender/recipient, buyer/bidder, regulator/filer, funder/grantee, and custodian roles discriminate them. A regulator name never copies Government onto the corporate record.

### Nonprofit

Government → Nonprofit: a public consultation register, grant award process, statutory-body meeting, public election administration, or government accreditation workflow stays Government when public-body ownership and authority function are evidenced.

Nonprofit → Government: private-association minutes, board elections, advocacy, standards work, accreditation, member discipline, grant applications, and public-service contracts stay Nonprofit unless public-body status is independently established. `Community Association AGM Minutes 2026.pdf` is the collision fixture: governance structure and government mentions do not outweigh private ownership.

Hybrid and quasi-public bodies remain unresolved. Public-interest language, statutory recognition, government funding, public contracting, or use of an official-sounding name is not enough. A deployment-specific gazetteer plus legal-form/context evidence or user confirmation may eventually settle them; this row invents neither catalogue nor rule.

### Identity and civic records

Government → Identity: a passport office's internal issuance workflow or protected authority case export may be Government as an operational record, while embedded identity bytes retain independent Identity evidence and protection.

Identity → Government: the person's passport, visa, civil-status certificate, voter confirmation, national identifier, or appointment record stays Identity/Protected Records. `Passport Renewal - application and appointment confirmation.pdf` is the shared-byte fixture. Government is issuer or counterparty, not the holder's operational role.

No authored edge to `identity` appears because `identity` was not one of the roster-stamped schema neighbours and this pass avoids adding a non-reciprocal schema collision casually. The memo preserves the boundary for R1c review.

## Schema default versus children

The schema default is the authority-side precondition plus conservative privacy. Children refine organizational situations; they do not acquire fields or inherit activation through `parent_id`.

- `government.public-authority-record` should be the narrow residual child for an authority-side record that has authority/workflow evidence but no more specific public-function template. It must not accept every official letter.
- Policy, legislative, rulemaking, and consultation children distinguish working sequences: options-to-decision; bill/amendment/proceedings; proposal/comments/final instrument; invitation/responses/analysis/outcome. Legal vocabulary remains values and evidence.
- Municipal administration is the authority's own governance cycle. It is not a synonym for Business Operations merely because both have budgets, policies, projects, meetings, and procurement.
- Grant administration and public procurement are funder/buyer-side. Applicant, grantee, bidder, and supplier-side packets stay Nonprofit or Business Operations.
- Planning, permit, and licensing children are deciding/issuing-side. Applicant or recipient records stay Construction/Property, Legal, Business Operations, Identity, or a protected residual.
- Public-records access is records-holder-side. A journalist's or citizen's research packet is not automatically Government.
- Statistical programmes cover production and controlled access, not every downloaded government spreadsheet.
- Elections administration covers the administering body's operations, not campaigns, political parties, voter confirmations, or civic advocacy.
- Constituent casework has the strongest named-person protection and must not group across people through issue similarity, agency names, addresses, or demographic attributes.
- Education/accreditation, cultural institutions, archives, and international development need the same public-body-role test. State ownership must be evidenced; topic or funding is insufficient.

The anchor therefore gives children a shared refusal rule: if the public authority is only issuer, counterparty, subject, employer, cited organization, or industry value, Government does not fire.

## Fields, work types, grouping, and dimensions

`fields` and `proposed_fields` are empty. Tempting candidates were rejected:

- `authority` or `public_body` would encode owner/custodian, but neither is canonical and hybrid-body resolution is unresolved.
- `organization` is only proposed elsewhere and has a collector-level problem. This row does not depend on another unratified proposal.
- `institution` is a Finance role, not a general public-body key.
- `matter_id`, `case_reference`, `programme`, `proceeding`, `consultation`, `election`, `permit`, and `document_function` are not canonical government fields.
- `record_type` is Finance-scoped under the present list. Reusing it would silently collapse distinct schema roles.
- `project` and `artifact_type` are Research/Code keys, not generic escape hatches.
- `purpose` is scoped to College Applications.
- `jurisdiction` is explicitly a value, not a field or destination dimension.
- names of citizens, staff, politicians, applicants, bidders, regulated parties, witnesses, respondents, authors, and issuing officers are unsafe collector dimensions.

Work types are therefore descriptive enum candidates only; they do not create nodes or facts. Grouping may use exact repeated identifiers and accepted workflow anchors, but it must not copy an authority, person, case, programme, legal status, or sensitivity conclusion onto sparse neighbors. A calendar event, email, screenshot, annex, or archive member may join a reviewable group without gaining Government facts.

No time-first template is proposed. Dates in government records have incompatible meanings: meeting, filing, publication, receipt, decision, effective, inspection, election, collection, disclosure, and filesystem creation. Year-first would scatter one proceeding and can expose a citizen case chronology. The user may later choose, reverse, remove, add, or flatten dimensions after the field vocabulary and privacy policy are settled.

## Recognition and privacy boundary

Deterministic signals are deliberately conjunctive. Document structure plus official branding is still insufficient unless role is present. Folder context, file-plan codes, system exports, mailbox direction, repeated identifiers, and authorized-office blocks can support role, but no one clue is universal. A model may interpret ambiguous prose only after privacy policy, with a compact redacted dossier, exact evidence citation, and an `unknown` outcome when custody is unclear.

The system must never infer from this schema:

- legal validity, legal effect, jurisdiction, applicability, compliance, violation, entitlement, eligibility, public-body status, or official truth;
- whether a bill passed, a rule is operative, a permit is current, a filing is accepted, a procurement award is proper, a count is certified, a statistic is accurate, or a disclosure exemption applies;
- whether consent, authority, waiver, privilege, confidentiality, secrecy, classification, publication, redaction, retention, deletion, or access is legally sufficient;
- a citizen's identity, immigration, health, financial, educational, political, benefit, complaint, or legal status;
- that published material makes its surrounding working packet safe for cloud use or automatic movement.

Named-person cases require local-only processing by default, redacted display labels, minimal excerpts, and no semantic similarity across cases. Bidder responses, consultation submissions, enforcement evidence, restricted data, and election operations require the same conservative posture until P7/user policy decides more. The catalogue assigns only `potentially_sensitive`; it does not invent handling classes.

## Edges and deliberate nonedges

Authored `collides_with` edges are limited to the three required schema neighbours: `legal`, `business_operations`, and `nonprofit`. Each is same-kind and carries a concrete role discriminator. Reciprocity belongs to R1c; no neighbour file was edited.

`also_holds_with` is empty. Schema-level coactivation is plausible—an authority decision can also be Legal, an evaluation can also expose Business Operations structure, and a portal screenshot can also be Photos—but the strongest immediate concern is mutex default ownership by holder role. Fixture-level `also_schema` preserves independent evidence without serializing broad reciprocal schema edges prematurely.

`role_split` is empty because this schema declares no fields. Issuer/recipient, authority/applicant, regulator/filer, buyer/bidder, funder/grantee, administrator/voter, and records-holder/requester are real role seams, but the closed edge contract allows `role_split` only through canonical fields. Prose records the seam without minting keys.

Deliberate nonedges include Academic, Photos, Research, Finance, Construction/Property, HR, and Identity. They can coexist or collide in particular fixtures, but the roster did not stamp them as primary schema neighbours and this anchor should not create a star of non-reciprocal edges. Child research and R1c can add only those pairs that prove structurally necessary.

Residual routing is intentionally broad: Independent Records for durable standalone public notices and confirmations; Protected Records for personal, legal, identity, casework, restricted-data, bid, or submission material; Reading Inbox for public reference; Review Later for unresolved holder role; Unsupported or Encrypted for inaccessible systems and archives. Temporary Screenshots is used at fixture level when positive screen-origin evidence exists but workflow does not fire.

## NEEDS-JOSEPH

1. **NJ-GOV-1 — fieldless anchor policy.** Confirm that a placeholder schema with no domain fields may remain solely because recognition, child-template gating, and privacy differ materially. If not, refuse `government` and leave its work as residual/template-only coverage until a field vocabulary is ratified.
2. **NJ-GOV-2 — minimal canonical vocabulary.** If PR-6 is lifted, decide centrally whether Government may store an authority-side owner/custodian, bounded proceeding/programme/case reference, and document function. Decide destination eligibility separately. Children must not mint private variants.
3. **NJ-GOV-3 — public-body resolution.** Decide whether deployment-specific gazetteers are sufficient for known authorities and which evidence or user confirmation can recognize statutory, hybrid, devolved, indigenous, treaty, public-corporation, state-owned, contracted, and quasi-public bodies. Funding and naming alone must remain insufficient.
4. **NJ-GOV-4 — recipient-side official records.** Confirm that permits, licences, notices, filings, identity/civic documents, benefits, and confirmations held by recipients do not activate Government merely because the issuer is public. If product navigation wants an official-records view, it should be a query or residual/template policy, not this authority-side schema.
5. **NJ-GOV-5 — privacy display and grouping.** Decide how case references are represented without exposing citizen names, addresses, regulated-party identities, complainants, bidders, respondents, or political data in folder labels and summaries, and how P9 prevents cross-case semantic joins.
6. **NJ-GOV-6 — publication boundary.** Decide whether a public-release marker may lower the handling posture for one exact file while leaving annotations, search history, submissions, and surrounding packets protected. The schema-level default should remain potentially sensitive.
7. **NJ-GOV-7 — schema coactivation.** R1c should decide whether `government` needs reciprocal `also_holds_with` edges to Legal or other schemas, or whether fixture-level co-evidence plus role collisions is safer until fields exist.

## Final recommendation

Keep `government` as a J-DEPTH, fieldless, placeholder schema anchor with a strict authority-side role precondition, no dimensions, no time-first ordering, no automatic person-named branches, and a potentially-sensitive default. Its core refusal sentence should be treated as a product invariant: **government may be only issuer, counterparty, subject, employer, cited organization, or public-sector industry value; none activates this schema.** If that invariant cannot be implemented, refuse the node rather than turning it into an industry classifier.
