# creative.client-engagement — J-DEPTH research memo

## Verdict

Keep the row as a placeholder template. It is not a synonym for the creative schema default and it is not a folder named `Clients`. Its distinct evidence is a commissioner–maker relationship made observable across a bounded creative lifecycle: a role-bearing brief or scope requests creative outputs; a proof or working artifact answers it; feedback and approval identify exact revisions; and a manifest or handoff identifies what was delivered. Remove those relationship-bearing links and the material falls back to the creative default, another operational schema, or a residual.

The row does **not** earn distinct fields or a distinct dimension order. `creative` still declares no field rows, and its proposals for `client`, `project`, `stage`, and `artifact_type` await R1c. Therefore `fields`, `proposed_fields`, and `template.dimension_order` are empty. The row passes the template node test on different detection signals and a specific privacy seam, not on format, work type, or hierarchy.

## Authority and sources used

Repository authority was read in this order: `planning/prompts/ALIGNMENT.md`; `planning/00-database-agent-product-design.md`; `planning/01-product-design-structured.md`; `planning/domains/CONNECTION.md`; `planning/domains/CONNECTION-EXAMPLES.md`; `planning/domains/_CONTRACT.md`; `planning/domains/canonical_fields.json`; `planning/domains/roster.json`; and `planning/overnight/council/DECISION-BRIEF.md`. The row was stamped with `planning/domains/dispatch/make_prompt.py creative.client-engagement`.

The principal local anchors were `creative.json`, `creative.creative-brief.json`, `creative.self-initiated-work.json`, `business_operations.customer-account-management.json`, `business_operations.project-delivery.json`, and `business_operations.contract-administration.json`. The creative schema supplies the default against which the node test must be run. The refused brief row supplies the direct routing decision: a brief is a document inside this situation, not a situation of its own. The three business rows supply the account, bounded-project, and post-signature administration seams.

External sources were used only to establish that the named artifacts and lifecycle are real, not to create product rules:

- AIGA, *Standard Form of Agreement for Design Services* (2022 update), describes a proposal, client-supplied material and instructions, creative deliverables, changes, delivery schedules, review, written comments, and written approval. This supports the scope/change/review/approval fixtures. It does not authorize the product to decide contractual effect, intellectual-property ownership, payment rights, or acceptance.
- Adobe, *The Complete Guide to Request Management*, describes a creative brief as a request record containing work, goals, schedule, budget, objectives, deliverables, participants and expected outcome, developed between client and creative services. This supports the role-bearing brief rather than the bare word `brief`.
- Adobe, *How to get design approval from clients*, describes kickoff, brief, objectives, timelines, responsibilities, stakeholders, feedback and sign-off authority. This supports the review and approval sequence without making any approval legally effective.
- Asana, *Creative production*, describes an end-to-end request flow with intake, in-progress work, review and completion, using requester, creative type and workflow state. This supports the request-system export fixture and demonstrates why a standing queue is not itself a client engagement.

These are practice materials, contract templates and workflow-product guidance, not a universal standard. The row imports no numeric limits, turnaround periods, fee assumptions, rights rules, retention rules or approval thresholds.

## Node test — all three legs

### Detection

The creative default activates from making-record structures: linked assets, layers or artboards, revision families, briefs, delivery sets, production paperwork and creative project files. This row is narrower. It requires evidence that connects that making record to a commissioner in a role, and it looks for artifacts produced at the boundary between maker and commissioner: a prepared-for/prepared-by brief, a signed creative scope paired with work product, client-side comments tied to an exact proof, written sign-off naming the accepted revision, or a delivery manifest naming both files and recipient.

That difference is material. `Northwind_logo_master_v7.ai` has strong creative evidence and weak engagement evidence. It joins this row only because an independently evidenced brief, review or manifest names it. Conversely, `Statement of Work - Northwind Rebrand - signed.pdf` has strong engagement and contract evidence but does not prove creative production until a creative artifact or deliverable specification connects it. The row therefore cannot activate from either half alone.

### Recommended dimensions

There is no serialized difference. The creative default's pending prose order is client where the corpus truly has several clients, then project, stage, and artifact type. That is also the natural order here. A separate order would be invented merely to preserve the row.

The contract requires dimensions to use fields declared by the schema. The schema declares none, so the JSON order is empty. If R1c adopts the existing proposals, `client` must flatten in an in-house or single-client corpus: otherwise it is a one-child collector exposing a relationship while adding no navigation. Project precedes stage because `Round 2`, `Approved`, and `Delivered` are unintelligible without the work. Artifact type remains deepest. Time is not first because request, creation, review, approval, contractual and delivery dates are different clocks.

### Privacy

The schema is already potentially sensitive, but this template concentrates a distinct relationship-level risk. A client branch or even a filename can reveal who commissioned unreleased work. Briefs contain strategy, audiences, launch dates, budgets, named approvers and competitor material. Proofs may contain personal likenesses or unreleased products. Delivery messages may contain transfer links or credentials. Agreements and invoices add commercial, address and signature data.

This does not justify a handling class or a legal conclusion. It justifies local-first recognition, minimum excerpts, suppressed raw previews in general summaries, no automatic exposure to connectors, and no assumption that a published deliverable makes its surrounding brief, review history or client relationship public.

**Node-test result:** keep. Detection differs enough even though dimensions do not. If Joseph rules that a sibling must differ in dimensions as well as detection, refuse this row into the creative default; current CONNECTION says detection, dimensions, **or** privacy, so keeping it is contract-consistent.

## Bottom-up file set

The first eight JSON fixtures are the required J-DEPTH core and are intentionally varied.

1. `Creative Brief - Northwind Rebrand - approved.pdf` is the clean opening anchor: labelled commissioner and maker roles plus objective, audience, outputs, timing and approver. It does not approve later art and writes no client fact.
2. `Statement of Work - Northwind Rebrand - signed.pdf` is the commercial/legal anchor. It becomes engagement evidence only when its creative deliverables or neighboring work product connect it to making. It remains independently Legal.
3. `Northwind_Identity_Concepts_R1.pdf` is a client-facing proof deck. The request for a selection is observable; which option was chosen is unknown.
4. `RE Northwind concepts round 1.eml` is feedback crossing the organisation boundary and naming an exact proof. Thread membership does not enroll unrelated attachments.
5. `Northwind_logo_master_v7.ai` is the sparse working source. Layers and links activate Creative; engagement membership comes from exact external references. The version token is not approval or stage.
6. `Northwind R2 markup 2026-08-12.pdf` represents OCR and annotated proofing. Coordinates and a named source proof are strong grouping evidence; unclear handwriting remains unknown.
7. `APPROVED - Northwind identity master.eml` is the sign-off fixture. The message body and roles matter; the filename token does not.
8. `Northwind Final Artwork - delivery manifest.xlsx` names exact files, intended variants, sender and recipient. It is stronger than a folder called Final and does not itself grant rights.

The remaining fixtures test ugly edges:

9. `Northwind_Rebrand_Handoff.zip` is a mixed archive read through its manifest without forced extraction. Brief, source, approval, invoice and rights members retain their own schemas.
10. `Commission request - portrait for anniversary.eml` is the rejection fixture for an enquiry that never became an engagement. A proposed price and date do not make the sender a client.
11. `Creative Brief Template.docx` contains the complete document structure and none of the situation. It proves why the brief-shaped row was correctly refused.
12. `Project Phoenix Weekly Status 2026-08-14.pptx` is the project-delivery collision. Governance, RAG, milestones and dependencies with no creative lineage belong to the business project row.
13. `Acme account quarterly review.pdf` is the customer-account collision. Relationship health, renewal and support across an ongoing account are not a bounded creative commission.
14. `Invoice 1048 - Northwind Rebrand.pdf` may join by exact job reference while retaining Finance evidence. Alone it falls to Receipts and Confirmations.

The set covers a labelled form, contract-shaped document, presentation, free-form email, creative proprietary source, OCR, spreadsheet, archive, template, enquiry, collision files and a financial coactivation. Calendar and audio/video are plausible source types but were not added merely to inflate examples: a kickoff invitation is transport evidence unless it names the accepted job and roles; a video proof behaves like the concept PDF only when review comments identify the exact cut or timecode.

## Files considered and rejected

- `Brief.pdf` — a bare homonym may be legal, policy, media-planning, educational or creative. The word is never-alone.
- `Creative Brief Template.docx` — a reusable form, not an engagement. Reference Clips is safer.
- `Commission request - portrait for anniversary.eml` — an approach, not acceptance. Review Later unless later evidence connects it.
- `logo_final_v3_FINAL.ai` — a making file with noisy version tokens, not client approval.
- `Brand Guidelines - Northwind.pdf` — may be a client-supplied input, a delivered result, a downloaded public guide or the brand-identity work itself. Citation by a brief proposes membership and copies no facts.
- `Invoice 1048 - Northwind Rebrand.pdf` — Finance first; exact job membership may coexist, but an amount and billed-to name do not prove making.
- `Northwind NDA.pdf` — legal or protected record. It can protect a job without proving any creative work occurred.
- `Acme account quarterly review.pdf` — ongoing account management with no artifact lineage.
- `Project Phoenix Weekly Status 2026-08-14.pptx` — bounded project governance without creative commissioner/maker evidence.
- `Final.zip` — unsupported or Review Later until a readable manifest or handoff identifies its members and recipient.
- `Screenshot 2026-08-18 at 14.20 - feedback.png` — Photos requires positive screen-origin evidence; engagement membership additionally requires OCR or neighboring exact review evidence. Missing EXIF proves neither.
- a contact card or address-book export for the client approver — relationship metadata, not a creative job file.
- a DAM export of published assets — asset management or a delivery copy depending on manifest and holder role; publication alone does not reconstruct a commission.

## Fields, proposals and work-type discipline

No fields are proposed. This is deliberate, not missing research.

- `client`, `project`, `stage`, and `artifact_type` are already canonical and already proposed by `creative.json`; duplicating those proposal objects here would make the template look like a second schema.
- `our_firm` is canonical but destination-ineligible and belongs to the role split, not the template hierarchy.
- `purpose` is not available to Creative under the current canonical ownership. The brief's objective is evidence, not a new Creative purpose field.
- `requester`, `approver`, `job_number`, `engagement`, `approval_status`, `deliverable`, `deadline`, `review_round`, `usage_rights`, `contract_status`, and `delivery_date` were considered and not minted. Several are operational or legal states; others are values of the pending stage/artifact fields; all require cross-family adjudication.

`work_types` are values only. Brief, proposal, proof, markup, sign-off and manifest do not become child nodes. In particular, the refusal of `creative.creative-brief` is preserved: its best evidence is this row's activation evidence.

## Reciprocal boundaries

### Creative default

This row must not take an authored creative source merely because a brand appears in it. The default must not erase a commissioner relationship when a role-bearing brief, exact feedback and delivery record exist. Shared bytes: `Northwind_logo_master_v7.ai`. Alone it is default Creative; named by exact review and manifest evidence it becomes a group member here without receiving copied client or stage facts.

### creative.self-initiated-work

Both sides use the same tools, file shapes and version habits. This row must not infer a client from subject, brand or recipient. Self-initiated work must not infer independence merely because no fee or signed contract is present. Shared bytes: the same layered poster source. Client-side request/review/acceptance supports this row; a self-set brief and maker-controlled release support the sibling.

### business_operations.customer-account-management

This row must not consume a standing account review, stakeholder map, health score, support history or renewal plan just because the account sometimes orders design. Customer-account management must not consume the proof/feedback/delivery lineage of a bounded creative job merely because a client contact participates. Shared bytes: a quarterly review deck with a slide linking recent creative deliveries. The account-health slides belong there; the linked exact proof and delivery manifest belong here.

### business_operations.project-delivery

This row must not take governance artifacts on the words project, deliverable or approval. Project delivery must not take a proof and markup merely because they follow milestones. Shared bytes: a creative-project closure pack. RAG, dependency, benefits and sponsor sections support project delivery; commissioner role, exact proof history and final-artwork manifest support this row. One archive may contain both sets.

### business_operations.contract-administration

This row must not decide obligations, notice, renewal, payment, amendment effect or acceptance effect. Contract administration must not take creative sources or reviews merely because a contract funds them. Shared bytes: `Statement of Work - Northwind Rebrand - signed.pdf` and a signed change request. The instrument can coactivate; the surrounding obligation register stays there and the surrounding proof lineage stays here.

### career.consulting-client-engagement

Both have prepared-for/prepared-by roles, scope, milestones, feedback and acceptance. This row needs a creative making structure: linked/layered source, media timeline, proof-to-revision lineage or variant delivery. Consulting owns analysis, recommendations, operating models and advisory implementation without that lineage. A brand-strategy engagement can contain both; membership is per file and group evidence, never a forced whole-folder choice.

### Legal, Finance, Photos and Career

These are coactivation seams, not mutexes. A signed agreement remains Legal; an invoice remains Finance; a screenshot retains Photos evidence; a delivered work becomes Career evidence only when the holder selects or presents it as a sample. Engagement membership never copies role, payment, capture or portfolio facts.

## Deliberate nonedges

- `code` was considered because creative website and interactive work may live in repositories. A repository with source/configuration/commit evidence activates Code independently; a client relationship does not create a mutex. If an exact brief names the repository deliverable, group membership may coexist without a schema edge here.
- `photos` is `also_holds_with`, not a collision. A photographed proof, shoot reference or feedback screenshot can carry positive capture evidence and engagement membership simultaneously.
- `creative.brand-identity` was considered. A brand-guidelines file may be one deliverable within the engagement, but a media/work-type child row must not replace the broader relationship template. No same-evidence mutex is needed at this pass.
- `creative.revision-round` was considered. The revision family is a stage/work-type view inside the same engagement, not an alternative commissioner situation; R1c should police sibling overlap without turning one file into competing activation templates.
- `business_operations.procurement-sourcing` was considered for competitive pitches and RFPs. A requester-side procurement packet and a maker-side accepted commission have different holder roles; an unanswered RFP remains Review Later or procurement evidence rather than this row.
- `finance.small-business-bookkeeping` was not used as a collision because invoices and receipts can coexist cleanly through `also_holds_with: finance`; no byte-level mutex is necessary.
- `legal.practice-matter-file` was not used merely because contracts are legal. The broad Legal schema coactivation states the real seam without pretending a creative-services contract is professional legal-practice work.

## Grouping without copying facts

Strong candidate joins use exact anchors: a brief or scope title; job/request reference; exact proof filename; same-stem review round plus client comments; message attachment identifier; delivery-manifest member name; archive manifest; or transfer receipt naming both set and recipient. A sparse source such as `Northwind_logo_master_v7.ai` can join the accepted engagement group through those anchors while retaining no inferred client, project, stage, approval or delivery fact.

Weak joins remain weak: shared brand name, sender domain, visual similarity, common subject, folder proximity, upload/download session, creation date, author metadata, `FINAL` token or semantic similarity. One client may commission several projects and one studio may serve several brands; neither relationship licenses merging projects. A delivery set may contain format variants without turning all neighboring files into deliverables.

The stop rule is especially important at client level. Files for two projects by one client do not merge merely because the client matches. Files for two clients on one campaign do not merge until the commissioner and producer roles are resolved. A sub-contractor's source can be supplied into the job without the sub-contractor becoming the client.

## Residual routing

- Independent Records: durable standalone brief, sign-off, agreement or delivery note with no accepted group.
- Review Later: enquiry, unlabelled feedback, ambiguous final export, mixed kickoff packet or uncertain holder role.
- Reference Clips: blank forms, example scopes, published case studies and reusable briefing material.
- Receipts and Confirmations: isolated invoice, payment receipt or transfer confirmation whose financial purpose is clear.
- Unsupported or Encrypted: unreadable transfer packages, proprietary review exports and password-protected client archives.
- Protected Records: isolated NDA, agreement, unreleased launch brief or contact-bearing document requiring conservative local handling.

No residual becomes a schema fact or a permanent forced destination.

## NEEDS-JOSEPH

1. **NJ-CCE-1 — node-test policy.** Confirm that materially different activation is sufficient even when a template inherits the schema default's dimension order exactly. CONNECTION currently says detection, recommended dimensions, **or** privacy; under that rule this row survives. If the intended rule is stricter, refuse into `creative` and preserve the recognition signals there.
2. **NJ-CCE-2 — in-house requester role.** Decide whether canonical `client` includes an internal commissioning department or stakeholder, or whether the product needs a distinct requester/commissioner role. This row mints nothing because a local synonym would fragment the same cross-boundary concept.
3. **NJ-CCE-3 — visible client dimension.** Decide whether a client-named branch may be shown or created automatically. The provisional recommendation is user-approved only, omitted in a single-client/in-house corpus, and redacted where the relationship itself is sensitive.
4. **NJ-CCE-4 — account reciprocity.** Set the reciprocal rule with `business_operations.customer-account-management`: a bounded accepted creative job may group under client after approval; a continuous account queue must not become a per-client creative hierarchy merely because it links deliverables.
5. **NJ-CCE-5 — membership representation.** Specify how P9 records exact brief/proof/comment/approval/manifest relationships without copying client, project, stage, approval or delivery facts onto sparse members.
6. **NJ-CCE-6 — contract/approval semantics.** Confirm that signed scopes, change requests and approvals are observational anchors only; Legal/P7 or user policy owns legal effect, rights, confidentiality, payment conditions and authority.
7. **NJ-CCE-7 — sibling overlap.** Decide whether `creative.revision-round`, delivery-oriented creative siblings and this engagement root are browse views under one accepted group or mutually activatable templates. The current row treats revision and delivery as work-type/stage evidence, not rival situations.

## Final recommendation

Keep `creative.client-engagement` as a fieldless placeholder template. Activate only from a commissioner–maker relationship joined to actual creative making through brief/scope, exact review, approval or delivery evidence. Keep the future order aligned with the creative default, flatten client when it adds no information, preserve commercial/legal/financial/capture facts on their own schemas, and abstain on enquiries, templates, filenames and final-looking exports that lack the relationship chain.
