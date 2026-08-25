# `creative.brand-identity` — J-DEPTH research memo

## Verdict

**Retain as a placeholder template, not a schema.** Brand identity is a distinct organizational situation only when the corpus shows identity-system governance: a coordinated rule manual, controlled marks/assets, approval or supersession records, version history, and permitted-use guidance. A logo, colour palette, “brand” filename, or a single identity deliverable is a work-type value or an ordinary creative/client-engagement artifact and does not activate this row.

The three node-test legs land as follows:

1. **Detection differs.** Creative making evidence (layers, artboards, exports, revisions) is not enough. This row requires system-level coordination across multiple artifacts and an explicit governance relation: rules apply to marks and variants, an asset register maps approved resources, and a named authority approves or supersedes a revision. That is a positive signal, unlike the absence of a client or presence of a logo. A manual plus register plus approval can establish the identity situation even when no one file is named “brand identity.”
2. **Dimensions remain empty by contract.** The `creative` schema declares no fields; this template therefore writes `fields: []` and recommends no serialized dimensions. If R1c later adopts shared creative proposals such as `project`, `stage`, `artifact_type`, or `client`, identity-system governance should populate those shared dimensions. `identity system`, `logo`, `colour`, `typography`, and `approved` are values or observations, not new folder fields.
3. **Privacy differs in practice but not by a new handling class.** Internal standards, unreleased marks, vendor-use restrictions, source assets, and approval decisions can be sensitive. The same posture may apply to a client engagement, but this row has a stable trigger for protecting a governed packet: distribution controls and proprietary identity assets. Public reference guides and isolated marks do not inherit that posture merely because they use brand vocabulary.

This reading follows the design's distinction between observations and facts: “Extraction does not create a final folder path, invent domains, merge all files that share one string, or treat model output as proof.” The template detects a governance situation; it does not turn a logo string into a path.

## Sources and authority used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped output of `python3 planning/domains/dispatch/make_prompt.py creative.brand-identity`.
- `planning/prompts/ALIGNMENT.md`, especially the schema/template distinction, refusal rule, residual vocabulary, and “work types are values” rule.
- `planning/00-database-agent-product-design.md`, especially the evidence distinction, source-type extraction, version-family handling, purpose-first grouping, and template validation. Relevant verbatim anchors are: “A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive”; “A file fact is not inherently rule-based or LLM-based”; and “The product should not decide where a file belongs when it first discovers these facts.”
- `planning/domains/CONNECTION.md` and `CONNECTION-EXAMPLES.md` for activation versus grouping, `never_alone`, and evidence-item collision discipline.
- `planning/domains/nodes/creative.json`, `creative.client-engagement.json`, `creative.graphic-design-project.research.md`, `creative.creative-brief.json`, and `creative.deliverable-handoff.research.md` for the landed creative boundaries. Existing creative rows are comparison material only; no neighbour files were edited.

The concrete filenames below are practitioner fixtures and argued inferences, not claims about a particular vendor's file format. Extensions route extraction but never prove meaning; `.ai`, `.fig`, `.pdf`, `.xlsx`, and `.zip` are not identity facts.

## Bottom-up file investigation

### `Northwind Identity Standards v4.2.pdf`

This is the strongest anchor. It has a rule structure spanning mark construction, clear space, incorrect use, colour values, typography, imagery, voice, and applicability. Its revision table names an owner, approver, and superseded edition. The system-level rule coverage distinguishes it from a campaign concept deck or a single logo export. It may support the template; it cannot create a folder path, infer that all Northwind files are members, or prove legal trademark ownership.

### `Northwind Approved Marks Register.xlsx`

The register maps multiple lockups and colour variants to asset files, usage status, owner, system revision, and distribution date. It is not itself a legal rights instrument. Its value is the control relationship between many assets and one governed revision. If detached from the standards and without provenance, it becomes Review Later rather than an identity system.

### `Northwind_logo_master_v7.ai`

Multiple lockup artboards and matching identifiers make this a controlled asset candidate when the manual and register are present. `v7` is only a version-shaped observation; universal `version_family` can relate it to other bytes but cannot establish approval. Without governance companions, this is ordinary creative work or Review Later.

### `Identity Governance Decision - 2026-04-18.eml`

The message names the brand steward, approves v4.2, retires v4.1, and identifies affected marks and distribution audience. Sender identity alone is not enough; the decisive observations are the role, exact governed revision, and state transition. It may be grouped with the manual and assets without copying approval onto every neighbouring file.

### `Northwind Brand Portal Export.zip`

Its readable manifest lists the standards PDF, source marks, web/print exports, font references, usage notes, and a revision manifest under one recurring system identifier. The archive is a purpose-coherent packet, not proof that every member is approved. Manifest paths are observations; unreadable members remain indexed safely and may fall through to Review Later or Unsupported or Encrypted.

### `Northwind Rebrand Creative Brief.docx`

This has labelled client, objective, audience, deliverables, and deadline sections, requesting a manual and logo concepts. It opens or supports `creative.client-engagement`, but it does not prove that a governed system exists. A brief can ask for identity work without containing operative rules, controlled assets, or approval history. The same file may be grouped with a later identity packet, but no identity facts should be copied backward from that group.

### `Brand Guidelines - Acme.pdf`

It looks identical to a standards manual but has no holder-specific owner, approval, distribution, or provenance. It is a public or downloaded reference until stronger context exists. This is the key false positive: a document genre with brand vocabulary is not an identity system for the local corpus.

### `logo_final_v3_FINAL.ai`

The filename is deliberately noisy. One vector mark and repeated final/version suffixes provide no rule system, no controlled asset register, and no permitted-use guidance. `FINAL` and `v3` are universal/version observations, never-alone signals. Without companions it falls through to One-Off Images or Review Later.

### `Northwind Brand System Approval Screenshot.png`

OCR shows a portal approval for a named standards revision, while screen chrome supports screenshot routing. The screenshot can be a supporting member of a governed group, but it cannot establish the complete manual or asset set. Missing EXIF is not proof of screen origin; the positive screen evidence is the chrome and OCR. If the packet is absent, Temporary Screenshots is safer.

## What was rejected as evidence

- A single logo, wordmark, icon, swatch sheet, font file, or lockup: an artifact, not a governed system.
- A “brand” or “identity” heading: document genre and topic are not purpose or governance.
- A campaign poster, social crop, or packaging panel using a logo: creative project output; brand use is subject matter unless system rules govern the packet.
- A creative brief or statement of work: client-engagement evidence unless the file itself contains a system manual/register and approval structure.
- An invoice, purchase order, or legal trademark filing: finance/legal administration, not identity-system governance.
- A public style guide or downloaded template: Reading Inbox or Reference Clips until local ownership and approval are evidenced.
- A shared folder, asset library name, download session, or recurring company name: context clues only; the graph may group but cannot copy facts.
- `FINAL`, `APPROVED`, `LOCKED`, a date, or a version suffix: universal/version observations that need the governed object and role-bearing evidence.

## Reciprocal boundaries and collision fixture

### `creative.client-engagement`

Client engagement owns the commissioner-maker workflow: brief/scope, review, approval, and delivery of creative work. Brand identity owns a durable rule-and-asset system that may survive one engagement and govern many outputs. In the other direction, a brand name in a poster or a manual cited by a brief does not prove a client role. Same fixture bytes: `Northwind Rebrand Creative Brief.docx` belongs to the engagement side; `Northwind Identity Standards v4.2.pdf` plus `Northwind Approved Marks Register.xlsx` belong to the governance side. A signed scope can mention identity deliverables without making the scope itself a standards manual. No JSON edge is authored because this is a functional boundary, not a necessary mutex: the same accepted packet may legitimately contain both situations on disjoint evidence.

### `creative.graphic-design-project`

Graphic design is a medium/work-type candidate. A poster, logo, colour board, or layout remains ordinary creative work unless a multi-artifact governance system is evidenced. Conversely, the identity system may govern posters, packaging, interfaces, and documents without being a graphic-design project. Same fixture bytes: `Northwind_logo_master_v7.ai` can be a design artifact, while `Northwind Identity Standards v4.2.pdf` governs the system. The former does not activate this row alone; the latter needs system structure, not its title.

### `creative.deliverable-handoff`

Handoff owns package/recipient/acceptance evidence. Brand identity owns rules and controlled-use governance. A portal export may be both a governed identity packet and a delivery package, but a checksum manifest does not prove standards and a manual does not prove receipt. Same fixture: `Northwind Brand Portal Export.zip`. Grouping may connect them without copying approval, receipt, or rights facts.

### `career`, `code`, and `photos`

Career may own a polished identity case study when its purpose is showing the maker's work; the governed manual and source asset remain creative. Code owns a repository or implementation whose manifest/build structure is decisive; a design-system export inside it does not become a brand system merely from CSS or component names. Photos owns a screenshot or capture when EXIF/screen-origin evidence is present; a photographed logo does not prove authorship or governance. Same collision fixture for career/photos: `Northwind Brand System Approval Screenshot.png`—its screen evidence may support photos, while OCR content can only support identity as a group member after governance is independently established.

## Proposed fields and dimensions

`proposed_fields` is intentionally empty. Candidate concepts such as `identity_system`, `brand_owner`, `governance_status`, `approved_use`, `asset_set`, or `effective_revision` either duplicate the shared creative/project-stage-artifact structure, are role-sensitive owner facts, or are version/approval observations. Minting them would turn a template into a new schema, contrary to the stamped assignment and the empty `creative` declaration. R1c may later decide whether a compact canonical identity field set is warranted; this row must not pre-empt that decision.

## Residual routing and sensitivity

`Independent Records` is appropriate for a readable standalone manual or governance decision with no accepted system group. `Review Later` is for incomplete, detached, unsigned, or contradictory packets. `Reading Inbox` is for public or downloaded guides. `One-Off Images` is for an isolated logo raster or flat export. `Temporary Screenshots` is for portal/chat captures without a complete system packet. Unsupported or Encrypted remains available for unreadable proprietary archives; no filename inference should bypass it. These are residual destinations, not replacement schemas.

Identity material is **potentially sensitive** when it includes unreleased marks, internal strategy, vendor distribution controls, proprietary source files, or licensed assets. This is a protection posture, not a public/private handling class and not a reason to treat every brand image as sensitive.

## NEEDS-JOSEPH

**NJ-BRAND-1 — canonical identity facets.** Should R1c add a compact field set for governed identity systems, or keep the current empty creative schema and rely on structural detection plus universal version/sensitivity facts? Option A enables identity-specific destination proposals; Option B avoids another schema and treats system governance as a template condition.

**NJ-BRAND-2 — co-activation with client engagement.** When one accepted packet contains both a commissioned identity manual and its governing rules, should `creative.client-engagement` and this template co-activate on disjoint evidence, or should identity be a group subtype under engagement? The current JSON leaves `also_holds_with` empty because the closed vocabulary permits that edge only between schemas, while this is a template-level question.

**NJ-BRAND-3 — public versus local guide.** Is a public guide ever sufficient to activate a local identity system when no owner/approval record is present? Recommended: no; keep it Reading Inbox until holder-specific governance evidence appears.

## Consistency and self-verification

The JSON and this memo agree: the row is retained as `kind: template`, `launch: placeholder`, `fields: []`, `proposed_fields: []`, no dimensions, potentially sensitive, and activated only by identity-system governance rather than brand vocabulary or file type. The first eight JSON examples follow the first eight investigations above, including the same collision fixtures and residual outcomes. `python3 -m json.tool planning/domains/nodes/creative.brand-identity.json` passes; all `source_type` values are from the closed vocabulary; only the two assigned files were written.
