# Research memo — `creative.illustration`

Depth: **FULL R1b DEPTH (ratified J-DEPTH, 2026-08-25)**

## Verdict

Refuse the node. Illustration is a medium/work-type label within the creative schema's default making record, not a distinct organizational situation. Layered drawings, painting documents, sketches, references, proofs, exports and version families are the same evidence used by graphic design, identity, editorial, game art and other creative work. Commission, revision, delivery and rights records can matter, but those are workflows that cut across media.

The node test fails on all three legs:

1. **Detection.** A layered `.kra`, `.psd`, `.procreate` or `.ai` file with a preview, linked references and same-stem exports is strong evidence of creative making, but not of illustration specifically. A flat character PNG can be an authored export, a downloaded reference, a portfolio depiction or a photo of a physical drawing. A signed release or commission can prove a rights or counterparty relation, not the medium.
2. **Dimensions.** The `creative` placeholder declares `fields: []`. If later proposals such as `project`, `stage`, `artifact_type` and `client` are adopted, illustration belongs beneath the same common order. Subject, style, technique, brush, canvas size, page number and format would be values or observations, not valid dimensions. The commission and rights workflows may have different structures, but their difference is recipient/role/grant evidence, not illustration.
3. **Privacy.** Unreleased work, private subjects, children's imagery, client briefs, contact details, reference licences and releases can be sensitive. Those protections attach to the containing creative project, client engagement or rights record. They do not require an illustration-specific privacy rule.

This is a structural refusal, not a claim that illustration files are unrecognizable. The creative default still activates from authored making evidence. `creative.client-engagement` can organize a genuine commissioner relationship; `creative.deliverable-handoff` can organize a package and recipient; `creative.licensing-rights` can organize a grant or release. None should be inferred merely because a file depicts a character or painting.

## Sources and comparison set

- `planning/domains/dispatch/make_prompt.py creative.illustration` and its stamped assignment.
- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including J-DEPTH, refusal, collision, reciprocal-boundary and residual requirements.
- `planning/00-database-agent-product-design.md`, `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md` and `planning/domains/CONNECTION.md` for the observation/fact, fieldless-placeholder, activation/grouping and closed-edge rules.
- `planning/domains/roster.json`, confirming the row's `creative` schema, neighbours `career`, `code`, `photos`, and residuals.
- `planning/domains/nodes/creative.json`, the default creative recognition and template comparison.
- Landed sibling `creative.graphic-design-project.json` and memo, used as the closest medium-refusal comparison; `creative.deliverable-handoff.json` and `creative.licensing-rights.json` were inspected for workflow boundaries without editing them.
- `planning/domains/nodes/finance.crypto-assets.research.md`, used only as the J-DEPTH memo-shape calibration.

No external source was needed. The concrete file names below are ordinary practitioner records and argued inferences; no market statistic, detector threshold or fabricated quotation is asserted.

## Bottom-up file investigation

### 1. `Moth_Character_Sketches_07.kra`

This is the strongest apparent positive: a layered Krita painting with sketch, ink and colour groups. It supports creative-schema activation because it is an authored working record and a version family. It does not establish an illustration node: the same layers and revisions occur in concept art, editorial composition, game assets and graphic design. `Moth` may name a subject, title or internal nickname, while `07` is universal version evidence. With no active fields, neither can become a project or a style fact. If no creative project can be recovered, the durable source falls through to Independent Records.

### 2. `Moth_Character_Approved.png`

The transparent PNG shares a stem and shows a character. It may be a rendered export from the source, a copy delivered to a client, a portfolio image, or a downloaded asset. `Approved` is not proof of sign-off; a flat file contains no recipient or approval record. The member may join a P9 version-family group without receiving source-file facts. Without authored-work evidence it is an isolated image, not an illustration situation.

### 3. `Picture_Book_Brief.docx`

The labelled brief provides an audience, page count, tone, art requirements, deadline and revision expectations. It is evidence for purpose coherence and possibly a client engagement. It does not prove that a particular illustration exists, and a picture-book brief may commission writing, lettering, design and production as well as images. Publisher and author names require role-bearing text before they become counterparty facts. The brief remains a creative/default or engagement support record, never evidence for illustration as a node.

### 4. `Editor_notes_round2.eml`

The email quotes image filenames and requests page-level changes. Cross-domain sender/recipient slots make a counterparty workflow plausible, but email domains alone do not establish client role. The requested changes are not proof of implementation or approval. Revision is graph/group structure and universal version evidence, not a medium-specific template. Unattached or unresolved feedback routes to Review Later.

### 5. `Picture_Book_Art_Delivery.zip`

The mixed archive contains TIFFs, web JPEGs, a PDF proof and a README with page assignments and output specifications. This is handoff-shaped only if package purpose, recipient or transmission is established. The archive name does not prove delivery, and archive paths do not license member facts. Its distinctive structure is package/recipient workflow and may contain illustrations plus copy, design and production paperwork. That is why deliverable handoff—not illustration—is the candidate structural distinction.

### 6. `Watercolour_Technique_Reference.jpg`

The image looks maximally illustration-specific yet is a downloaded scan. Browser/download metadata, absent layered sources and no project neighbourhood distinguish reference consumption from authored work. The depicted painter is not the corpus owner's author. It falls through to Reference Clips, demonstrating why visual content and style vocabulary cannot activate this node.

### 7. `Illustrator_Portfolio_Case_Study.pdf`

This presentation uses finished illustrations to demonstrate the maker's capabilities. Its purpose is career evidence; it is not the making record, even when it repeats the same title and shows the same final image. Editable sources, proofs and delivery files remain creative. A pictured illustration does not imply that its source bytes exist locally. This is a collision with `career`, not `also_holds_with`: the competing purpose belongs to different records.

### 8. `Model_and_Property_Release.pdf`

The signed form names a person or location, usage scope, territory and term. It can support a rights/release workflow, but it does not identify the illustrator, the work, or which nearby images the grant covers. It must not activate illustration or copy rights facts onto a sparse PNG. Without a recoverable rights or project association it remains an Independent Record.

## Further ugly cases considered

- `Untitled-3.psd`: layers and a preview support creative making, but the absence of a title does not establish illustration; it could be compositing, a template or a study.
- `Editorial spot art_final.ai`: “spot art” and `final` are work-type/version vocabulary. They do not prove a commission, sign-off or separate medium node.
- `Character_Reference_Board.pdf`: a moodboard can support a project, but a downloaded board is a reference record; visual coherence does not prove authorship.
- `Sketchbook_2025.pdf`: a scan of personal pages may be a personal archive or photos/scan record, not a professional illustration project.
- `Sprite_Sheet.png`: game-engine naming and atlas dimensions may indicate `code`/game-art context; the raster itself does not prove an illustration situation.
- `Cover_Illustration_CaseStudy.pdf`: portfolio purpose belongs to `career` when the document explains capability; the case study does not absorb the source files.
- `Stock_Watercolour_Texture.tif`: a reusable purchased asset belongs to stock/library handling, even if it is painterly and used by an illustrator.
- `Invoice_PictureBook.pdf`: a matching title is finance/business evidence, not creative activation.
- `Reference_Screenshot.png`: capture metadata or screenshot structure may route to `photos`; it is not authored illustration merely because it shows a drawing.

## Default and sibling comparison

### Creative schema default

The creative default already covers one named work across working files, references, revisions, proofs, exports and related paperwork. Illustration's strongest signals—layers, brushes, canvas properties, rendered variants and same-stem version families—are all default making-record signals. Its placeholder schema has no fields, so the proposed order remains held as prose: if fields arrive later, project-first, then stage and artifact type, with client only where a counterparty workflow is genuinely established.

### Graphic design project

The landed graphic-design refusal supplies the closest reciprocal comparison. A poster, editorial layout or illustration may share the same source formats, artboards, linked assets and export family. Conversely, an illustration placed in a poster is not automatically absorbed by the poster's project: the linked source can be a separately commissioned asset. Both are work-type labels unless project/role evidence creates a different workflow. No edge is added because the rows are both internal medium candidates and the refusal does not need a new mutex.

### Client engagement

A labelled commission, role-bearing email or brief can support `creative.client-engagement` across several outputs. Reciprocal boundary: `Moth_Character_Sketches_07.kra` remains a creative making record when no client role is established; a signed brief can support engagement even if it commissions illustration, copy, layout and photography together. Conversely, a publisher name printed in a picture-book cover does not prove a client relationship. The counterparty, not the medium, is the structural distinction.

### Deliverable handoff

`Picture_Book_Art_Delivery.zip` becomes handoff-shaped only with a recipient, transmission or package-purpose record. Reciprocal boundary: an editable source and internal proof remain in the making record; a delivered package may contain illustrations, layouts, copy and colour specs. Package/recipient evidence therefore belongs to handoff, while illustration cannot own the archive merely because its members are painted images.

### Licensing and rights

`Model_and_Property_Release.pdf` can belong to rights handling when the grant is explicit. Reciprocal boundary: the release does not make nearby PNGs illustrations, and an illustration export without a rights record does not establish a licence. Rights can cover references, models, locations, fonts or downstream uses, so the grant/territory/term structure is cross-media.

### Career

`Illustrator_Portfolio_Case_Study.pdf` is a collision fixture. If its purpose is presenting capability, career owns the case-study bytes; the editable source, proof and delivery set remain creative. Conversely, a creative project brief or layered source does not become career material merely because the maker later includes a thumbnail in a portfolio.

### Photos

`Reference_Screenshot.png` or a photographed sketch may share the same visual content as an illustration export. EXIF, capture event and camera chronology support photos; layered source/export relations support creative. Conversely, a native PNG with no camera evidence cannot be called a photo solely from its flatness, and a photograph of a drawing cannot be called authored illustration solely from appearance.

### Code

`Sprite_Sheet.png` can sit beside a game repository, but manifests, source-tree roles and engine import structure establish code/game-art context. A standalone sprite source can remain creative; neither extension nor atlas dimensions creates illustration activation. No collision edge is authored because the decisive evidence belongs to repository context rather than an illustration-specific signal, and the row's required neighbour is only considered, not claimed.

## Proposed fields

None. `illustration`, `medium`, `style`, `technique`, `subject`, `brush`, `canvas_size` and `deliverable_format` are not proposed fields: the first four are work-type/style vocabulary, subject is content rather than organizational context, and the others are artifact observations. `project`, `stage`, `artifact_type` and `client` remain creative schema proposals for R1c; this template cannot copy or redefine them.

## Edges and residual coverage

`career` and `photos` are collisions because the same rendered or flat image bytes can support mutually competing purposes and require neighbourhood evidence to resolve. No `also_holds_with` edge is written: a portfolio case study and a source file are distinct records, while a photographed sketch is not simultaneously an authored illustration record. No edge is written to `code`, graphic design, client engagement, deliverable handoff or licensing rights; these were considered as workflow or context boundaries, not as reciprocal mutexes for a refused medium label.

Residuals preserve coverage. Independent Records receives durable standalone briefs, sources, releases and exports. One-Off Images receives isolated flat graphics. Reference Clips receives downloaded visual studies. Review Later receives ambiguous feedback, approvals and unproven packages. Unsupported proprietary illustration files retain creative's indexed-but-unreadable posture when they cannot be opened; they do not become evidence for a separate node.

## Privacy

Potential sensitivity includes unreleased commissions, private or child subjects, client strategy, contact details, candid editorial feedback, reference assets, model/property releases and licence terms. The row is refused because these controls belong to the enclosing creative project, client engagement or rights workflow. No handling class or exposure threshold is invented.

## NEEDS-JOSEPH

**NJ-ILLUSTRATION-1 — post-field product vocabulary.** Should the interface expose `illustration` as a non-activating `work_type`, `artifact_type` or style value after the creative schema adopts fields?

- Recommended: keep it as a searchable value under the creative default; do not create a node or dimension.
- Alternative: surface it only from user-curated vocabulary, without converting it to a schema fact.
- Alternative: omit the label and rely on artifact properties plus semantic retrieval.

All options preserve the refusal.

**NJ-ILLUSTRATION-2 — workflow-row independence.** Should commission, handoff and rights rows be adjudicated independently before any illustration vocabulary is exposed? Recommended: yes. A package, counterparty or rights grant may justify its own template only from its own evidence and must not inherit activation from a medium label.

## Final consistency statement

JSON and memo agree on `refuse_node: true`, empty `fields` and `proposed_fields`, no dimensions, `potentially_sensitive` handling, `career`/`photos` collisions, four residual routes, and the non-activating vocabulary recommendation. The first eight JSON examples correspond in order to the eight detailed investigations above. The clean ending is intentional: no trailing unresolved claim or partial section remains.
