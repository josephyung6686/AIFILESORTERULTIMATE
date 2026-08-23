# legal.estate-planning — R1b research notes

Verdict: **accept the node, but only as a flat, protection-first Legal situation with no Legal fields or dimensions.** The useful boundary is the document situation: testamentary instruments, trust instruments, delegated-authority instruments, advance directives, beneficiary directions, and closely linked personal estate-administration records. The node does not determine whether any instrument is valid, effective, current, complete, enforceable, revoked, or controlling, and it does not determine capacity, ownership, entitlement, inheritance, or medical wishes.

This is deliberately narrower than the Legal schema default. It gives recognition and collision rules for a coherent class of especially sensitive personal records while preserving D1/PR-6's decision that Legal remains field-less. Protection can activate for a single credible document; destination depth cannot.

## Sources actually used

### Ratified project hierarchy

I regenerated and read the exact dispatch prompt for this row with `planning/domains/dispatch/make_prompt.py legal.estate-planning`, then followed its authority order:

1. `planning/00-database-agent-product-design.md`, read in full. The controlling points are Legal's safety-domain launch, protection before model or placement work, local-first handling of protected content, evidence local to each file, graph multi-membership without fact inheritance, extension-as-routing-signal, archive manifest inspection without extraction, sparse-file preservation, and the opt-in residual policy.
2. `planning/prompts/ALIGNMENT.md`, including the rule that schemas own fields while templates own recognition, grouping, and collision behavior.
3. `planning/domains/_CONTRACT.md`, especially the closed source-type vocabulary, canonical field ownership, exact file-example shape, reciprocal collision requirement, residual vocabulary, schema-only `also_holds_with`, and canonical-field-only `role_split`.
4. `planning/domains/CONNECTION.md` and `planning/domains/CONNECTION-EXAMPLES.md`, used to distinguish a true evidence-boundary collision from mere topical adjacency.
5. The landed `legal` schema row and its research notes. D1 and PR-6 intentionally defer Legal field design, so this template inherits no fields and proposes none.
6. The current roster entry and generated assignment for `legal.estate-planning`. The row is a safety-launch template with `medical` and `finance` as must-consider neighbours and `Protected Records` as its must-consider residual.
7. Current neighbouring template rows and research notes, especially `finance.investment-brokerage` and `medical.dependant-child-health`, because both already contain an inbound collision to this node.
8. The legacy rows `legal.wills-trusts-estates`, `legal.power-of-attorney`, `med.advance-directive`, and `pers.estate`. These were mined as hypothesis lists only, not treated as authority.
9. Git history for the roster and legacy rows. Commit `13bff36a12430dcc28f29d2bdfffa927f9dbfe70` is the landed source of the current assignment label; history does not turn old vocabulary into canonical fields.

### External primary or official artifacts

These sources were used only to identify recurring artifact structures and boundary cases. Their legal instructions are jurisdiction-specific and are not encoded as universal recognition requirements, validity tests, or legal advice.

- [GOV.UK — Making a will](https://www.gov.uk/make-will): evidence that a will workflow distinguishes the instrument, executors, signing, witnesses, storage, and later changes. Used to motivate will, codicil, execution-block, and storage/delivery fixtures—not to decide whether a file is legally valid.
- [GOV.UK — Lasting power of attorney forms](https://www.gov.uk/government/publications/lasting-power-of-attorney-forms): evidence that delegated-authority records can separate property/financial and health/welfare functions and can include continuation, notification, and registration paperwork.
- [GOV.UK — Trusts and taxes](https://www.gov.uk/trusts-taxes): evidence for the distinct settlor, trustee, and beneficiary roles and for the separation between a trust instrument and later tax or account records.
- [GOV.UK — Trust record keeping for tax purposes](https://www.gov.uk/guidance/trust-record-keeping-for-tax-purposes): evidence that trust administration may collect identity, asset, transaction, and tax records without making every such record the trust instrument.
- [GOV.UK — Applying for probate by post when there is a will](https://www.gov.uk/government/publications/form-pa1p-apply-for-probate-the-deceased-had-a-will/how-to-apply-for-probate-by-post-if-there-is-a-will): evidence for the distinction among a will, death evidence, application workflow, grant, and estate-administration packet.
- [US National Institute on Aging — Advance care planning and advance directives](https://www.nia.nih.gov/health/advance-care-planning/advance-care-planning-advance-directives-health-care): evidence that advance directives can include treatment instructions and health-care proxy appointments, creating a real Legal/Medical seam.
- [US Department of Veterans Affairs — VA Form 10-0137](https://www.va.gov/forms/10-0137/): an official example of an advance-directive artifact that combines a health-care-agent appointment with personal treatment choices. Used for fixture shape only.
- [IRS — Retirement topics: beneficiary](https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-beneficiary): evidence that retirement-plan beneficiary directions belong to an account/plan workflow while also carrying estate-planning relevance.
- [FINRA — Plan ahead: transfer your brokerage account assets on death](https://www.finra.org/investors/insights/plan-ahead-transfer-your-brokerage-account-assets-death): evidence for transfer-on-death registration as a brokerage-account workflow with a genuine estate-planning reading.
- [California Courts Self-Help Guide — Legal documents that help plan for death or incapacity](https://selfhelp.courts.ca.gov/wills-estates-probate/legal-documents): evidence that wills, trusts, powers of attorney, advance health-care directives, and beneficiary-related directions commonly coexist while retaining different functions.

No external source supplied a field, quantitative cutoff, ranking rule, jurisdiction catalogue, handling class, or binding legal test. Terms such as testator, settlor, trustee, principal, agent, executor, and beneficiary are recognition vocabulary and observed roles only.

## Why this row survives the node test

The Legal schema default is intentionally broad and flat. This row is narrower in three concrete ways:

- Its positive evidence requires recognizable instrument or administration structure, not merely legal-looking language: for example, will plus dispositive and execution structure; trust plus distinct operative roles; authority instrument plus principal/agent and scope structure; directive plus health-specific instructions or appointment and execution structure; or an estate inventory/account tied to an explicit estate or grant reference.
- It has sharp negative boundaries against ordinary agreements, adversarial matters, professional matter custody, provider-authored clinical records, Finance account/tax/insurance records, civil-status records, public blank forms, encrypted filename-only artifacts, and non-legal uses of estate terminology.
- It supports a useful protected multi-file situation—one plan, one instrument family, one trust, one personal administration, one beneficiary direction, or one directive delivery chain—without requiring a person, estate, adviser, instrument status, or jurisdiction folder.

That is enough incremental value to accept the node. A refusal would discard high-value detector and collision work; a deeper folder template would overstate what the ratified schema permits.

The accepted scope is personal evidence of:

- testamentary instruments and their amendments or revocations;
- trust instruments and directly referenced amendments, restatements, or certifications;
- property/financial and health/welfare delegated-authority instruments;
- advance directives or living wills;
- beneficiary, payable-on-death, and transfer-on-death directions;
- grants, representation records, inventories, accounts, and distribution records in a personal estate-administration packet;
- instrument-specific registration, signature, delivery, or adviser correspondence; and
- a manifest-supported estate-plan or administration archive.

The scope excludes:

- general contracts, deeds, leases, and signed forms lacking estate-instrument structure;
- will contests, fiduciary disputes, and other adversarial personal matters;
- a lawyer's multi-client matter export, billing, advice drafts, and professional work product;
- clinician orders, patient charts, and provider proxy-access workflows;
- account statements, insurance policy/claim workflows, and tax returns merely involving an estate, trust, or beneficiary;
- death certificates and other registry-issued vital records;
- generic sample forms with empty party and execution slots;
- unreadable/encrypted files known only by filename; and
- software, architecture, property-market, or ordinary-language uses of will, trust, estate, agent, or beneficiary.

## Observation/fact boundary and the legacy fields rejected

The canonical field result is intentionally empty:

- `fields: []`
- `proposed_fields: []`
- `template.dimension_order: []`
- `also_holds_with: []`
- `role_split: []`

Legal has no canonical schema fields under D1/PR-6. Therefore a template cannot quietly create them, borrow another schema's fields for Legal meanings, or promote observed document roles into facts. Universal facts remain legal when directly evidenced on the file. When a fixture genuinely activates another schema, only that schema's existing canonical fields appear in `facts_legal`.

The useful but non-canonical terms from legacy rows were explicitly rejected as fields:

- estate or plan role;
- instrument type;
- estate, testator, maker, settlor, or grantor;
- executor or personal representative;
- trustee;
- beneficiary;
- principal or donor;
- attorney, attorney-in-fact, agent, proxy, or representative;
- authority scope;
- execution, signing, witnessing, notarization, registration, filing, or grant date;
- jurisdiction;
- registration, execution, revocation, validity, current, or supersession status;
- professional adviser, firm, court, registry, matter, grant, or proceeding reference; and
- dispositive, asset, treatment-wish, or inheritance outcome.

Some of those observations are essential to recognition. They remain quoted or labelled evidence tied to the source file. They are not normalized facts, folder dimensions, graph facts donated to neighbours, or assertions that a role or status is legally effective.

`institution`, `account_type`, `record_type`, and `tax_year` are used only on fixtures that independently expose Finance structure. `project` and `artifact_type` are used only on the software false friend. Photos fields appear only where independent capture-origin evidence exists. None is repurposed as a Legal field. `creation_date` remains the universal file date; it is not an execution, death, grant, revocation, or effective date.

Jurisdiction deserves a separate warning. A deployment may inject jurisdiction-specific form names and vocabulary under R6, but jurisdiction is a value, never a field or dimension in this row. The detector must not infer a jurisdiction from a law-firm footer, venue reference, notarial block, or form resemblance.

## Bottom-up corpus coverage

The JSON contains 27 fixtures. They were selected before finalizing recognition so the rule set had to survive positive, sparse, multimembership, privacy, wrong-node, and unreadable cases.

1. `Last Will and Testament - signed.pdf` — strong will structure; never proves validity or current effect.
2. `Codicil to Last Will - signed.pdf` — explicit parent-instrument reference and execution structure; supports a candidate version relationship only.
3. `Revocable Family Trust Agreement.pdf` — trust roles and operative administration clauses; does not establish ownership or entitlement.
4. `Durable Power of Attorney - Property and Finance.pdf` — delegated-authority structure; does not establish current authority or capacity.
5. `Advance Health Care Directive - signed.pdf` — genuine Legal/Medical multimembership with separate evidence for each reading.
6. `Health and Welfare Power of Attorney.pdf` — legal appointment plus a possible Medical context; never turns the appointment into a clinical fact.
7. `Beneficiary Designation - Retirement Plan.pdf` — estate direction and retirement-plan workflow; Finance fields remain Finance-only.
8. `Transfer on Death Registration - Brokerage.pdf` — estate direction and brokerage workflow; no beneficiary entitlement or registration status is inferred.
9. `Grant of Probate - Estate of Morgan Lee.pdf` — official administration record; the example does not assert the grant's present effect.
10. `Estate Inventory and Account.xlsx` — estate-linked rows plus independent Finance record structure; amounts do not prove ownership, valuation, or distribution.
11. `Funeral and Memorial Wishes.txt` — ambiguous prose that requires protected local review and may remain `Review Later`.
12. `Estate Plan Package.zip` — manifest-supported packet inspected without unpacking; member facts stay with members.
13. `Completed Estate Documents.eml` — message-level workflow evidence only; no attachment contents or legal effect are inherited.
14. `Estate Plan Signing.ics` — planned event, not proof of execution; it may remain `Review Later`.
15. `IMG_7782.jpg` — photographed instrument with independent capture evidence; page content and capture origin stay disjoint.
16. `Screenshot 2026-07-18 at 10.22.11.png` — portal/screenshot ambiguity; visible workflow labels do not prove completion or legal status.
17. `Will Contest Petition.pdf` — adversarial false friend routed toward `legal.personal-legal-matters`.
18. `Client Matter Export - Estate Planning.zip` — practitioner-custody false friend routed toward `legal.practice-matter-file`.
19. `Residential Lease Agreement - signed.pdf` — execution-furniture false friend routed toward `legal.leases-agreements`.
20. `Portable Medical Order - Morgan Lee.pdf` — provider-authored end-of-life false friend routed toward `medical.personal-health-records`.
21. `Trust Account Statement - Q2 2026.pdf` — trust-title false friend routed toward `finance.investment-brokerage`.
22. `Life Insurance Beneficiary Designation.pdf` — deliberate insurance/estate seam; policy structure and beneficiary direction use disjoint evidence.
23. `Estate Tax Return 2025.pdf` — estate-word false friend routed toward `finance.tax-filings`.
24. `Death Certificate - Morgan Lee.pdf` — packet-adjacent civil record routed toward `identity.core-documents`.
25. `Blank Last Will Template.pdf` — title-positive but completion-negative sample that falls through to `Independent Records`.
26. `Estate Documents (password protected).zip` — filename-only encrypted artifact that falls through to `Unsupported or Encrypted`.
27. `IT Estate Architecture Review.pptx` — non-legal estate false friend with independent Code evidence and `Review Later` fallback.

The set covers every declared source type used by the template: text document, spreadsheet, image, OCR, email, calendar, archive, and presentation. Extensions are routing signals only. Several examples deliberately retain `group_without_copying_facts: true` because packet membership or multi-membership is useful while fact propagation remains forbidden.

## Recognition and grouping discipline

Deterministic recognition uses conjunctions of independently visible structures. No single role word, person name, organization, signature, seal, date, filename, folder, session, extension, or neighbouring document activates this situation. A sparse file can join only through direct cross-reference, an exact/version relationship, a manifest-supported packet, or a user decision; the graph must not fill in missing people, roles, assets, dates, statuses, wishes, or account details.

The model-review list is intentionally narrow and downstream of protection. It covers ambiguous prose, version comparison, vocabulary ambiguity, custody, unusual/foreign forms, mixed archives, correspondence, OCR captures, cross-schema evidence, and authorized transcript cases. It may return cited plausibility or abstention. It may not render legal advice or decide validity, capacity, operative status, ownership, entitlement, inheritance, medical wishes, or the governing instrument.

Grouping is non-destructive and relationship-first. The most useful candidate groups are one plan, one directly linked instrument family, one trust, one estate administration, one beneficiary direction with Finance multimembership, or one advance-directive delivery chain. Every member retains independent file evidence, and a protected singleton remains useful without a fabricated group.

## Privacy and safety consequences

Estate material can expose not only the corpus holder but also third parties: family relationships, intended beneficiaries, replacement decision-makers, incapacity planning, treatment preferences, signatures, asset descriptions, account references, addresses, and disputes. The consequences in this row are therefore operational, not decorative:

- P7 runs before any model or external connector. The authoritative `ClassificationRecord` is keyed by `file_id` and `content_hash`; this row neither implements the detector nor invents its handling vocabulary.
- Protected content is local-first. A cloud prompt does not receive filenames, raw clauses, party names, account identifiers, wishes, or relationship details by default.
- General group summaries remain redacted. A label should not reveal a person, estate, beneficiary, diagnosis, treatment choice, asset, adviser, or dispute.
- No automatic move follows from recognition. The top-level fallback is the opt-in `Protected Records` residual, and representing a file there does not authorize a filesystem action.
- No destination dimension is recommended. Person, estate, instrument kind, beneficiary, adviser, status, medical-wish, and matter labels all risk disclosure and all lack canonical Legal fields.
- Image/OCR, archive, email, calendar, and transcript handling keeps the same privacy boundary. A different container or extractor does not lower sensitivity.
- The row never attempts to open encrypted archives, guess credentials, or unpack archive members to disk during the normal scan.

The JSON sets only the template-level `potentially_sensitive` posture required by the contract. It does not assign a P7 result to any fixture, infer one from content, or define handling classes.

## Edges and reciprocity ledger

I recalculated live inbound collisions during final review. Exactly four current node files point to `legal.estate-planning`, and all four are reciprocated:

| Inbound node | Reciprocal seam in this row |
|---|---|
| `finance.investment-brokerage` | Beneficiary designation, transfer-on-death registration, or trust-titled account: account/custodian/holdings evidence belongs to Finance; completed beneficiary/owner authorization or operative estate-instrument evidence belongs here. |
| `legal.leases-agreements` | Trust, authority, or testamentary instrument versus an ordinary deed, lease, or agreement: estate roles and unilateral future direction belong here; reciprocal duties, counterparty roles, rent, or grant of use belong to leases and agreements. |
| `legal.personal-legal-matters` | Planning or routine administration versus an adversarial will or fiduciary dispute: instrument/appointment evidence belongs here; claims, opposing parties, service, hearings, or requested relief belong to personal legal matters. |
| `medical.dependant-child-health` | Health/welfare authority, advance directive, guardianship, and provider proxy workflow: legal appointment/execution evidence belongs here; patient/provider access and care-workflow evidence belongs to dependant health. |

The remaining seven outbound edges are real evidence-boundary collisions but were not yet reciprocal when checked. They are explicitly left for R1c rather than silently editing another owner's row:

- `medical.personal-health-records` — advance directive versus provider-authored order or clinical record;
- `legal.practice-matter-file` — a person's protected packet versus a practitioner's multi-client matter custody;
- `finance.insurance-personal` — completed beneficiary direction versus policy, premium, coverage, or claim workflow;
- `finance.tax-filings` — grant-linked administration versus tax-authority form and computation schedules;
- `identity.core-documents` — estate packet versus registry-issued death or other vital record;
- `photos.scanned-documents` — document-content evidence versus independent scan/camera-origin evidence; and
- `photos.screenshot-captures` — protected portal content versus independent screenshot-origin evidence.

Each signal describes what distinguishes the two nodes. Mere topical relationship, shared person, shared estate, shared account, shared vocabulary, or packet proximity is not an edge criterion and cannot donate facts.

## Neighbours considered that did not get an edge

- `finance.loans-mortgage`: a closing or security packet can later appear in estate administration, but the sharper boundary remains document role—loan/charge evidence versus an estate instrument. No recurring same-file collision was strong enough beyond packet adjacency.
- `finance.personal-records`: this is broad Finance context. The investment-brokerage, insurance, and tax edges express the concrete same-file seams more precisely, so a generic Finance edge would add noise.
- `research.ethics-compliance`: advance directives and research consents can both discuss authorization, capacity, representatives, or medical choices, but form purpose and issuer/workflow distinguish them. No corpus-backed same-file collision justified an edge.
- `code.software-project`: IT estate is an important lexical false friend, but independent software-project evidence resolves it; a `never_alone` rule and negative fixture are more precise than an edge.
- `photos.camera-events`: a camera roll may contain a photographed will, but `photos.scanned-documents` is the sharper page-capture collision. Event proximity alone must not pull protected documents into an event group.
- academic/history/genealogy topics: family and death research may quote wills or probate records, but the current roster has no dedicated genealogy template and topical quotation is not the same as holding the personal instrument.

## Files considered but not added as fixtures

- A public estate-planning article or downloaded explainer: useful as a reading-reference false friend, but the blank-form fixture already protects against title-only activation and `Reading Inbox` can handle generic reference material.
- A video will or audio statement of wishes: transcription is separately policy-gated, and legal recognition or validity would be jurisdiction-dependent. The text wishes fixture plus authorized-transcript abstention rule covers the safe boundary.
- An organ-donor card: it has medical and identity implications, but it is not reliably an estate-planning instrument and would widen the node through topic alone.
- A crypto seed phrase or password handoff note: inheritance context does not reduce credential risk. Identity/credential protection must dominate, and no such secret should appear in research fixtures.
- A provider DNR/POLST-style form beyond the included portable medical-order fixture: the existing negative already exercises the directive/order seam without multiplying jurisdiction-specific forms.
- A pet trust or veterinary instruction: it is a possible corpus member but adds no new evidence-boundary mechanism beyond the trust and wishes fixtures.

## Contract and prompt tensions resolved conservatively

1. **Node value versus empty dimensions.** The generic assignment asks for the deepest useful dimension order, but the Legal schema supplies no fields. The node is accepted for detector, grouping, privacy, and collision value while remaining flat.
2. **Legacy specificity versus D1/PR-6.** Legacy rows offered many tempting party, role, instrument, jurisdiction, and status fields. The ratified schema decision outranks them, so every such concept remains observation vocabulary or an open question.
3. **Edge skeleton versus schema-only arrays.** `also_holds_with` is schema-row-only and `role_split` can contain only canonical fields. Both are empty here; template-to-template ambiguity lives in `collides_with`.
4. **Official forms versus universal rules.** External artifacts demonstrate recurring shapes. They do not justify a global witness count, registration requirement, execution formula, legal-effect test, or jurisdiction inference.
5. **Protection versus placement.** Safety launch permits early detection and safe surfacing, not automatic movement. `Protected Records` is the sole top-level fallback and is opt-in.
6. **Estate planning versus estate administration.** The row includes closely linked personal grants, inventories, accounts, and distributions because the corpus situation is coherent, but it does not absorb litigation, practitioner matter files, tax filings, vital records, or every asset record.

## NEEDS-JOSEPH — this node only

1. **Legal field vocabulary.** If D1's deferral is lifted, decide centrally whether subject/estate, holder role, instrument kind, party roles, matter or grant reference, execution date, and supersession state should exist at all. This row proposes none and must not pre-empt the schema decision.
2. **Situation split and custody.** Decide whether personal planning and post-death administration stay one protected situation or split after corpus evidence, and define how P10 distinguishes a person's own records from professional custody without relying on folder names or an invented holder-role field.
3. **Protected destination depth and legal-status policy.** Decide whether any Legal values may ever appear in filesystem paths or general summaries, and whether the product will categorically abstain from validity/current/supersession decisions or support a separately governed human-confirmed workflow. Until then, this row remains flat and abstains.

None of these forks blocks the conservative row. The safe present behavior is deterministic protection on conjunctive document structure, local/redacted review for ambiguity, no Legal facts, no inferred legal effect, no automatic placement, and explicit collision boundaries.
