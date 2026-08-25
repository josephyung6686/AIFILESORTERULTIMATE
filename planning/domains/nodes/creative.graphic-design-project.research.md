# Research memo — `creative.graphic-design-project`

Depth: **FULL R1b DEPTH (ratified J-DEPTH, 2026-08-24)**

## Verdict

Refuse the node. Graphic design is a medium and work-type vocabulary inside the creative schema's default making record. It does not establish a different organizational situation. The same project can contain a poster, social crop, brochure page, packaging panel and presentation board; splitting those by medium or output format would destroy the named-work and revision relationships that make the files intelligible.

The node test fails on every leg:

1. **Detection.** Layers, artboards, linked assets, placed-image references, same-stem revisions and working-file/export pairs are all genuine evidence, but they are already the creative default's signals. Press metadata establishes production characteristics, not a graphic-design situation. A flat poster PDF may instead be a downloaded reference, a portfolio sample, a photographed object or an isolated record.
2. **Dimensions.** The creative placeholder schema has `fields: []`, so this template cannot license a folder dimension. If R1c later adopts the creative schema's existing proposals (`project`, `stage`, `artifact_type`, `client`), graphic design remains a value beneath that common structure. `Poster`, `layout`, `brochure`, `packaging` and `social graphic` are work/artifact types, not parents that make one another intelligible.
3. **Privacy.** Unreleased artwork, brand strategy, licensed assets, contact details and candid review can be sensitive. That posture follows the containing project or client engagement. Two-dimensional design does not require a rule different from illustration, identity or the rest of the creative making record.

This is a structural refusal, not a claim that the files are unrecognizable. The creative schema should still activate from its default making-record evidence. `creative.client-engagement` can describe a counterparty-oriented workflow, and `creative.deliverable-handoff` can describe a recipient/package workflow. Neither distinction is created by graphic design itself.

## Sources and comparison set

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including J-DEPTH, refusal, evidence, collision and reciprocal-boundary requirements.
- The stamped assignment produced by `python3 planning/domains/dispatch/make_prompt.py creative.graphic-design-project`.
- `planning/domains/nodes/creative.json`, used as the schema default and field-contract comparison.
- `planning/domains/nodes/creative.client-engagement.json`, used to test whether a counterparty workflow supplies a genuine structural distinction.
- `planning/domains/nodes/creative.revision-round.json`, used as the refusal exemplar: a revision cycle is graph/group structure and universal `version_family`, not a template.
- Stamped assignments for `creative.brand-identity`, `creative.illustration`, and `creative.deliverable-handoff`, used to compare their stated situation boundaries without editing their rows.

No external source was needed to establish the node-test result. Concrete file types below are ordinary practitioner records used as argued inferences; no market statistic, extractor threshold or fabricated quotation is asserted.

## Bottom-up file investigation

### 1. `Harbour_Festival_Poster_v07.ai`

This is the strongest tempting positive: an Illustrator working file with named artboards, layers, placed images and a same-stem version token. It supports creative-schema activation because it is a making record rather than a flat artifact. It does not support a separate graphic-design template. The identical interior structures occur in brand-identity, illustration and editorial work. `Harbour Festival` may name the work, event depicted or commissioning organisation; without role-bearing evidence it is not a `client` fact. Because creative declares no fields, the filename cannot write `project`, `stage` or `artifact_type`.

### 2. `Harbour_Festival_Poster_A2_PRINT.pdf`

Page boxes, bleed, embedded fonts and CMYK output intent are useful observations. Together with the working file they support a working-file/export relationship. Alone, they merely describe a press-capable artifact. A print PDF can be an internal proof, printer upload, delivered master, archive copy or downloaded example. `PRINT` cannot silently become a stage. If the creative schema is inactive and no project association is recoverable, the durable PDF falls through to Independent Records.

### 3. `Harbour_Festival_Social_1080x1350.png`

The flat image shares a visual motif and filename stem with the poster, but similarity and size are not enough to copy the poster's project identity onto it. A group may be proposed for review while the sparse member retains only universal/image facts. If no making-record neighbourhood exists, it is exactly the collision fixture for One-Off Images. The extension and pixel dimensions cannot activate a graphic-design template.

### 4. `Harbour Festival creative brief.docx`

A labelled audience section, output list and deadline establish a brief-shaped record. Those features can activate the creative default or support client-engagement analysis; they do not identify the medium. The requested outputs might include illustration, photography, copy, video and environmental signage alongside a poster. The agency and festival names require role-bearing language before either can become a counterparty. A brief is therefore evidence for purpose coherence, not for graphic design as a node.

### 5. `Harbour_Poster_feedback_round2.eml`

The subject, attachment quotation and requested date change can link feedback to a candidate artifact. They do not prove the change was implemented, nor that the sender's organisation is the client. As the revision-round refusal establishes, review is graph structure plus universal version-family evidence, not its own creative template. Unattached or ambiguous feedback belongs in Review Later rather than a synthetic medium collector.

### 6. `Harbour_Festival_FINAL_ARTWORK.zip`

An archive manifest listing AI, press PDF, PNG and README members is strong handoff-shaped evidence only when package purpose or transmission is established. `FINAL` is not approval, and archive paths do not license member facts. The archive demonstrates why file formats and deliverable types cannot justify the requested row: their value is the relationship among source, variants, manifest and recipient. That is the proposed deliverable-handoff workflow, not graphic design.

### 7. `Swiss Poster Collection 1950-1970.pdf`

This is the collision fixture that looks maximally graphic-design-specific and is not a making record. It contains posters, designer names and design history, yet its local purpose is reading/reference. Depicted creators are not file authors, and poster content does not establish that the corpus owner made a poster project. Without another active schema, it falls through to Reading Inbox.

### 8. `Portfolio_Harbour_Poster_Case_Study.pdf`

This file may contain the same brief, sketches and final poster as the making record, but its purpose is to present the maker's capabilities. The polished case study belongs to `career` when work-sample evidence is present; the editable sources, proofs and exports remain in creative. This is a collision, not `also_holds_with`, because the competing question concerns which organizational purpose owns the file. Images of source artifacts do not prove those source bytes exist locally.

### Further ugly cases considered

- `Untitled-3.psd`: layers and a preview can support creative activation, but no project name may be inferred from a nearby named file without evidence. It is not graphic-design-specific; it could be illustration, compositing or a downloaded template.
- `logo_final_v3_FINAL.ai`: identity vocabulary and repeated final/version tokens do not prove approval, delivery or a separate medium template. It belongs under brand-identity only if that sibling proves a distinct system-level situation; it does not save graphic design.
- `poster_reference.jpg`: an image of a poster may be a screenshot, photograph or download. Capture evidence routes to `photos`; an isolated flat reference routes to One-Off Images or Reference Clips according to purpose.
- `package_dieline_v4.ai`: dielines and spot colours are production observations. The file might be structural packaging artwork, a printer template or a downloaded specification; format cannot settle the role.
- `Fonts.zip`: a licensed font bundle may support a project but is not itself authored design. It must not activate from proximity or file type alone.
- `Press specs.pdf`: printer requirements are reference/supporting material, not proof that a graphic project exists.
- `Invoice_Harbour_Festival.pdf`: a matching name does not make the invoice creative evidence. Business/finance purpose wins for the invoice bytes, while a reviewed relationship may connect it to an engagement.
- `harbour_campaign_repo.zip`: SVG and image assets inside a code repository do not turn repository structure into graphic design. The code neighbour wins when manifests, source tree and build structure establish repository purpose.

## Default and sibling comparison

### Creative schema default

The creative schema already defines the relevant unit: one named piece of work moving through revisions toward delivery, showing, or publication. Its recognition includes linked assets, layers/artboards, revision families, briefs and handoff sets. Every credible signal for graphic design is therefore already present in the default. The schema's proposed `artifact_type` vocabulary explicitly treats media forms as values. A graphic-design child would duplicate recognition while having no licensed dimensions.

### Client engagement

A client engagement can be structurally different because the accepted corpus is organised around a genuine counterparty relationship across briefs, correspondence, proofs, approvals and multiple works. Reciprocal boundary: an AI poster source remains the making record when no client role is established; a signed brief or role-bearing email may support the engagement even if the commissioned outputs span poster, photography and video. Conversely, brand names merely depicted in artwork cannot activate client engagement. This counterparty seam is real, but it cuts across media and therefore does not support the requested node.

### Revision round

Revision-round evidence is the same-stem family, feedback record and response/approval relation. Reciprocal boundary: those relations may be browsed within a graphic-design project, but they remain universal facts and P9 group edges; `R2` never makes a graphic-design template. Conversely, a poster filename cannot turn an unattached comment into a round. The existing refusal is directly analogous: neither revision nor graphic design creates a distinct dimension or privacy rule.

### Brand identity

Brand identity's stated corpus is a system of marks, typography, colour and usage rules. If that sibling survives its own node test, it must do so because a system governing multiple artifacts has a distinctive grouping/delivery structure, not because `.ai`, logo or colour values exist. Reciprocal boundary: one festival poster that uses a logo remains a project artifact; a standards manual plus coordinated master marks may belong to an identity system. Shared Illustrator files, swatches and exports are insufficient in both directions.

### Illustration

Illustration's stated distinction is drawn or painted image-making whose working file carries history in layers. That is still the creative default's layer/revision structure and may itself face refusal as a work-type value. Reciprocal boundary: an illustration placed inside the poster can be a linked asset or separate commissioned work; the poster layout does not absorb ownership of the illustration bytes, and an illustrated subject does not prove the flat export is an illustration project. No edge is written here because this row is refused and because the sibling's final verdict is not yet landed.

### Deliverable handoff

Handoff can differ through a package-and-recipient workflow: an export set, format variants, manifest and evidence of transfer or intended receipt. Reciprocal boundary: `Harbour_Festival_FINAL_ARTWORK.zip` is only handoff-shaped until package purpose or transmission exists; an editable poster and internal proof remain in the making record. Conversely, a delivered package can contain identity, illustration, video and copy, so its structure is independent of graphic design. This is the clearest proof that deliverable types cannot justify the requested row: the workflow, not the formats, is what might justify a template.

## Reciprocal external boundaries

### `career`

The same rendered poster can appear in both a project export and a portfolio case study. If the bytes are arranged to demonstrate the maker's skills, with explanatory case-study narrative and polished mockups, career owns the file purpose. Editable sources, linked assets, proofs and production variants remain creative. A portfolio mention does not reclassify every underlying project artifact; a poster depicted in a case study does not make the case-study PDF a making record.

### `photos`

The same visual content may exist as a native export, a screenshot, or a photograph of a printed poster. Native working-file/export relations support creative; EXIF, capture event and camera chronology support photos. A flat JPEG without either neighbourhood cannot be decided by appearance. Creative must not copy capture facts, and photos must not infer authored design from what the camera depicts.

### `code`

Graphic assets may be members of a software repository, but repository manifests, source-tree roles and build structure determine the code situation. A standalone SVG authored for a campaign may remain creative; the same SVG under a web component's assets directory may be grouped with code without receiving invented project/client facts. No JSON edge is written because the concrete collision is with repository context rather than evidence uniquely produced by this refused node.

## Files rejected as evidence for this node

The following tempting signals were explicitly rejected: creative extensions; poster/logo/brochure words; colour mode; bleed; crop marks; artboard count; a brand name; author metadata; `FINAL`; simultaneous export times; common folder membership; visual similarity; a single flat image; a packaged archive without purpose; and a portfolio depiction. Each can aid routing, retrieval or group review. None distinguishes graphic design from the creative default or establishes a separate dimension/privacy posture.

## Proposed fields

None. The template inherits no fields because the creative placeholder declares none. It must not duplicate the schema's pending proposals. `graphic_design`, `deliverable_type`, `file_format`, `medium` and `design_style` are not proposed:

- `graphic design` is a possible value or user label, not a field.
- deliverable form belongs under the already proposed canonical `artifact_type`, if adopted.
- file format and media characteristics are observations/universal facts, not schema facets.
- medium and style are open vocabularies that do not create an organizational parent here.

## Edge decisions

`career` and `photos` are recorded as collisions because the same flat visual bytes can support mutually competing purposes that require neighbourhood evidence to resolve. No `also_holds_with` edge is written: a career case study may depict the creative work, but the case-study file and editable source are different records; a photographed poster can carry photo facts, but that does not make graphic design a valid template.

No edge is written to brand-identity, illustration or deliverable-handoff. They are internal creative-template candidates whose final reciprocal contracts are not yet landed, and a refused node should not manufacture sibling competition. Their boundaries are nevertheless argued above. `code` was considered without an edge because repository evidence, rather than a graphic-design-specific activation signal, settles that collision.

Residual routes preserve coverage. Independent Records receives durable standalone artifacts; One-Off Images receives isolated flat graphics; Reading Inbox receives design references and catalogues; Review Later receives ambiguous feedback, approvals and unattached exports. Unsupported proprietary files would follow the creative schema's indexed-but-unreadable posture rather than become evidence for this row.

## Privacy

Potential sensitivity is retained despite refusal. The risk can include unreleased campaigns, embargoed launch dates, client strategy, contact data, candid critique, licence terms and third-party assets. The row is refused precisely because these controls apply to the enclosing creative project or engagement, not because a file is graphic design. No handling class or exposure threshold is invented.

## NEEDS-JOSEPH

**NJ-GRAPHIC-DESIGN-1 — product vocabulary after field adoption.** Should the interface expose `graphic design` as a suggested non-activating filter?

- Option A, recommended: keep it as a `work_type` or style value under the creative default.
- Option B: surface it only when it appears in user-curated vocabulary, without converting it to a schema fact.
- Option C: omit it and rely on `artifact_type` plus semantic retrieval.

All options preserve refusal. None licenses a roster node, field, folder dimension or detector.

**NJ-GRAPHIC-DESIGN-2 — sibling adjudication dependency.** Brand identity, illustration and deliverable handoff must independently pass the node test. The first two risk collapsing to work-type values; handoff has the stronger candidate distinction because package/manifest/recipient structure can alter activation. Their future decisions must not be inferred from this refusal.

## Final consistency statement

JSON and memo agree on refusal, empty `fields`, empty `proposed_fields`, no dimensions, potentially sensitive handling, the `career`/`photos` collisions, four residual routes, and the product-vocabulary open question. The first eight JSON examples correspond in order to the eight detailed investigations above. The refusal preserves the creative default rather than rebuilding a media taxonomy.
