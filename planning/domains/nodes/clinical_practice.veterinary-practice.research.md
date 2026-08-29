# clinical_practice.veterinary-practice — deepening memo (REFUSED)

**Depth: J-DEPTH** (deepened from the retired gist standard).

## Verdict

**REFUSED.** This pass deliberately reverses the gist draft's `refuse_node: false` verdict. The draft correctly identified the decisive question but stopped early: is veterinary practice an organizational situation distinct from the `clinical_practice` default, or is veterinary the species/subject value and professional setting of records already owned by `patient-chart`, `pharmacy-operations`, `practice-administration`, `referral-correspondence`, `malpractice-incident`, Finance, government/resource rows, and `career.credentials-licenses`?

The completed subtraction test answers the latter. Every positive structure in the draft resolves to an existing situation once animal-valued slots are ignored. The tri-party structure is useful evidence, but it is a role arrangement within a chart or transaction, not a new situation. The privacy inversion matters to detection, but it does not establish a different privacy rule. Food-animal examples broaden subject values and neighbours; they do not make the umbrella coherent.

Refusal does not erase veterinary records. It retires only the umbrella label, routes concrete files through their operative structures, and preserves `ROSTER.md`'s refusal of owner-side pet material.

## Sources and authority

Read: `00-database-agent-product-design.md`; `ALIGNMENT.md`; `CONNECTION.md`; `CONNECTION-EXAMPLES.md`; `_CONTRACT.md`; `canonical_fields.json`; `DECISION-BRIEF.md`; `ROSTER.md` section 5.6 and Appendix A; the deepened `clinical_practice` schema anchor; `clinical_practice.patient-chart`; `clinical_practice.practice-administration`; `clinical_practice.pharmacy-operations`; `clinical_practice.referral-correspondence`; `clinical_practice.malpractice-incident`; refused `clinical_practice.licensure-credentialing`; `career.credentials-licenses`; and `medical.dependant-child-health`. The historical `pers.pet` row in `04-personal-household.*` was read as superseded prior art: the current roster explicitly drops it to residuals.

The exact design rules are load-bearing:

> “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically.”

> “One file may hold facts from more than one domain without losing information.”

> “The graph does not automatically copy those missing facts onto sparse files.”

> “Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.”

## Schema default

The deepened `clinical_practice` anchor defines practitioner-side material by custody and roles, not by species or specialty: the holder/practice is author or custodian and a separately labelled subject is the record's object. Its default includes the two-role author/subject structure, batched subjects, and address direction. It declares no fields or dimensions and protects third-party identifying material before model or placement paths.

The schema's proposed `subject_of_record` example explicitly includes “the person or animal a chart, referral letter, or incident report is about”. Animal subjecthood therefore lies inside the default. This row must differ on detection, dimensions, or privacy; it does not.

## Node test

### Leg 1 — fields: unsatisfiable, not a pass

This template must use `clinical_practice`, whose fields list is empty. It correctly retains `fields: []` and `proposed_fields: []`.

Species and breed are values in observed slots. Animal identity would be covered, if ever permitted, by the schema anchor's `subject_of_record` proposal; this row may not mint a species-specific synonym. Owner/client is a role: canonical `client` already has a commercial meaning and cannot silently be repurposed, while new `owner` would need global adjudication. Herd and holding are group-subject values or external administrative identifiers depending on the document.

The gist draft's prose `CLIENT → ANIMAL` order could never enter `dimension_order`; neither key is declared. That is evidence against the row, not deferred evidence for it.

### Leg 2 — detection: fails after subtraction

**Owner / animal / practice.** This is real structure, not a separate situation. `medical.dependant-child-health` demonstrates the general parent/patient/provider form without minting a species node. A dated record signed by the holder about a separately identified subject is `patient-chart`; an owner block is an additional representative or guarantor role. Delete animal-valued terms and the schema default remains.

**Clinical and priced content in one row.** The clinical narrative supports `patient-chart`; dispensing structure supports `pharmacy-operations`; invoice, amount, balance, or payment evidence supports Finance. 00 permits independent co-activation. Co-occurrence does not require a third umbrella.

**Privacy points at the owner.** A named human client block can expose address, contact, insurance, spending, debt, consent, and correspondence. It must be protected. Yet the rule is unchanged: clinical_practice protects third-party content and Finance/Legal activate their own safeguards. Both rows say `potentially_sensitive`; neither declares a different handling class. Which block a detector inspects is implementation detail, not a separate template.

**Food-animal practice.** A herd can be a group subject for a chart/plan; movement/testing can be government administration; production/assurance can be resource operations; controlled medicine is pharmacy operations. The holding identifier is contextual evidence whose operative document structure chooses the surviving situation.

After subtraction, the remaining veterinary vocabulary is never-alone: animal names, species/breed terms, microchip numbers, veterinary titles, practice names, medicine names, and holding identifiers occur in owner copies, photography, retail, research, coursework, insurance, credentials, government records, and agriculture.

### Leg 3 — dimensions: fails

`dimension_order` is empty because no destination fields exist. That matches the schema default. Client, animal, and species cannot be serialized into folder names, and may disclose a named person's relationship/account. `time_first: false` is the ordinary record default, not a discriminator.

### Privacy: fails as a differentiator

The bytes remain potentially sensitive, but there is no new regime. Practitioner charts receive clinical-practice protection; client accounts receive Finance protection; claims and authorities receive their own protection. Owner copies can route to Protected Records.

> “Privacy policy must be enforced before content reaches any model or external connector.”

> “Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it.”

Refusal preserves those rules.

## Concrete files and routing

The JSON retains ten fixtures so the refusal remains auditable.

1. `Consultation - BELLA (Smith) - 2026-04-14.pdf`: holder sign-off, patient/owner blocks, dated plan, priced lines. Clinical evidence routes to `patient-chart`; dispensing can co-activate `pharmacy-operations`; account evidence can co-activate Finance.
2. `Estimate and consent - Milo dental.pdf`: named animal, client signature, procedure, risk, total. Patient-specific consent belongs with chart/incident evidence; price and acceptance belong to Finance.
3. `Vaccination card - Bella.jpg`: in a practice corpus, custody/author plus accumulation can support patient-chart; in a personal corpus it is an owner's isolated copy and falls to Independent or Protected Records. The bytes alone do not establish holder role.
4. `CD register - practice.pdf`: running balance and accountability structure make it `pharmacy-operations` regardless of species.
5. `Client sales ledger Apr 2026.xlsx`: client/account/date/item/net/tax/balance structure is bookkeeping. Clinical item descriptions may add context but do not create an umbrella.
6. `pet insurance claim - continuation.pdf`: claim structure belongs to Finance; a completed clinical continuation may also support chart or referral. Possession does not prove holder role.
7. `herd health plan 2026 - holding 12-345-6789.docx`: the group may be a chart subject; production or authority evidence may activate resource/government neighbours. The holding number alone decides nothing.
8. `export health certificate - signed.pdf`: practitioner registration, animal identification, destination, declaration. Certificate/authority structure decides among administration, government, insurance, and chart readings.
9. `IMG_0912.jpg`: a dog in a garden. It is photo evidence. A neighbouring invoice copies no animal or clinical fact onto it.
10. `pms_backup_20260401.zip`: a proprietary database/attachments manifest remains protected and may fall to Unsupported or Encrypted; the archive name does not justify the umbrella.

## Files considered and rejected

- Boarding agreements, grooming records, training logs, pedigrees, pet-food invoices, pet-shop receipts: animal/owner shape without a clinical act.
- Veterinarian employment contracts, degrees, CPD, registrations, and indemnity: Career or Finance. The licensure sibling is already refused.
- Surgery leases, payroll, staff-only rotas, suppliers, generic policies: business or practice administration; letterhead is never-alone.
- Veterinary textbooks, research papers, lectures, public guidelines, medicine leaflets: topic is not live-practice purpose.
- Wildlife and pet photographs, rescue images, social screenshots: Photos or residual material.
- Farm production ledgers, feed schedules, movement returns, government testing notices: their administrative/production structures control.
- Owner-held vaccination cards, reminders, invoices, insurance copies: the current roster refuses the owner-side pet row. They route to residuals or independently evidenced schemas.

## Reciprocal boundaries

**Patient chart.** A dated clinical entry, accumulation, treatment plan, filed result, or patient-specific consent belongs to `clinical_practice.patient-chart` even when the subject is an animal or herd. Nothing routes toward this refused id. Shared bytes: `Consultation - BELLA (Smith) - 2026-04-14.pdf`.

**Pharmacy operations.** Register, stock, expiry, running balance, prescribing/dispensing, destruction, and controlled-drug accountability belong there regardless of species. Animal recipient and veterinary label are context. Shared bytes: `CD register - practice.pdf`.

**Practice administration.** Practice registration, inspection, standards, premises, populated clinic lists, recalls, system reports, or rotas connected to clinics belong there. Veterinary surgery is an organization value. Shared bytes: an inspection action plan.

**Referral correspondence.** Addressee, referrer, subject, and direction-of-send structure belong there whether the subject is human or animal. Species does not alter correspondence direction. Shared bytes: `Referral - Bella - orthopaedics.pdf`.

**Malpractice incident.** Complaint, incident-system reference, claim, indemnity, expert report, adverse-event review, or duty-of-candour structure belongs there. Animal procedure and owner consent are context. Shared bytes: `Complaint response - Milo dental.pdf`.

**Licensure/career.** The clinical licensure row is refused. A veterinarian's registration, renewal, CPD, good-standing letter, or credential ledger routes to `career.credentials-licenses`. Veterinary specialty/issuer context does not change the credential situation.

**Finance.** Invoice, account, tax, amount, payment, policy, premium, claim, and settlement activate Finance on their evidence. Patient narrative or prescription activates clinical rows independently. A fused line may support both, not a third node.

**Owner/pet household.** Practitioner templates require practitioner authorship/custody plus operative chart/pharmacy/referral/incident/admin structure. Household possession, patient-facing framing, and no practitioner-holder evidence route to residuals. Ambiguity remains protected. The `pers.pet` and `med.veterinary-pet-owner` refusals are not gaps to refill.

**Photos.** EXIF/capture/event evidence with no clinical document structure belongs to Photos. Positive OCR/document plus practitioner custody may support clinical rows. Animal name, folder name, missing EXIF, and proximity discriminate nothing.

**Government/resource operations.** Authority, statutory return, movement/testing reference, permit, and official declaration lean government. Production, assurance, feed, and output lean resource operations. A signed treatment plan can be a group-subject chart. Nothing remains for this umbrella.

## Collision fixtures in both directions

`Vaccination card - Bella.jpg` looks unmistakably veterinary but is not evidence for a practitioner template. In a household corpus it normally goes to a residual; in a practice corpus stronger custody and chart evidence can support patient-chart. Identical bytes do not prove role.

The inverse is `CD register - practice.pdf`: veterinary words may be absent, yet refusal must not lose it. Running-balance/accountability structure makes it pharmacy operations.

The second inverse is `Consultation - BELLA (Smith) - 2026-04-14.pdf`: it must not go to a household residual merely because the owner-side row is refused. Holder sign-off and dated clinical accumulation support patient-chart without needing species.

## Residuals

- `Protected Records`: sensitive chart/account/claim bytes without a safe group.
- `Independent Records`: isolated owner vaccination card, certificate, reminder, or notice.
- `Receipts and Confirmations`: isolated invoice, booking, or payment confirmation.
- `One-Off Images`: an animal photograph without event/document family.
- `Review Later`: unresolved holder role or clinical-versus-agricultural purpose.
- `Unsupported or Encrypted`: proprietary/encrypted practice exports.

> “Residual templates provide safe, intentionally broad destinations for files that have no reliable deeper association.”

## Proposed fields and NEEDS-JOSEPH

No proposed fields. `fields` remains exactly `[]`; no keys are minted. The schema anchor's `subject_of_record` proposal is not copied.

No node-local NEEDS-JOSEPH remains. The earlier NJ-CP-17 fold question is resolved: refuse. Schema-wide questions about `subject_of_record` and P7 remain on the schema anchor; duplicating them here would make a refused row appear load-bearing.

## What changed

- Reversed keep to refuse after completing all node-test legs.
- Preserved the 27-key shape, empty fields, ten fixtures, sensitivity, and residual routing.
- Recast positive structures as routing evidence to surviving templates.
- Removed node-owned veterinary context terms/work types; they are values or existing situations.
- Added reciprocal boundaries, rejected files, and collision fixtures in both directions.
- Closed the fold question and removed node-local open questions.

This memo is shorter than a schema anchor because the conclusion is subtractive: once surviving clinical/career situations and independent Finance/government/resource readings are named, no veterinary-specific template remains without padding.
