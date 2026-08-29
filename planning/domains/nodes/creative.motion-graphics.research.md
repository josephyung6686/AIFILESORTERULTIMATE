# Research memo — creative.motion-graphics

**Depth: J-DEPTH.**

## Verdict

Keep as a `kind: template` placeholder on `schema_id: creative`; do not refuse. The row earns a distinct node because motion graphics has a production lifecycle and evidence topology that the generic creative making record does not: storyboard/treatment → animatic or animation/compositing → review → render → delivery. The lifecycle is a template-level inference, not a new schema and not a set of fields. The creative schema is explicitly field-less at launch, so JSON correctly has `fields: []`, no proposed fields, and no dimensions.

The distinction is not “video extension” or “animation word.” A `.mov` can be a camera original, a render, a lecture, or a downloaded trailer. The decisive evidence is the relationship among a designed timeline/composition, generated or keyed visual elements, review changes, and a variant delivery set. This is a useful template boundary even while the schema deferral remains open.

## Authority and evidence

Sources read: `planning/00-database-agent-product-design.md`, `planning/01-product-design-structured.md`, `planning/domains/CONNECTION.md`, `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION-EXAMPLES.md`, `planning/domains/canonical_fields.json`, the stamped assignment from `make_prompt.py`, and the landed `creative` schema plus neighbouring creative nodes.

The design requires that “Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present, and—only under an explicit privacy and compute policy—speech-to-text transcripts.” That supports duration/codec/caption observations, not a motion fact. It also says “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text.” Those layers, artboards, links, and previews are the strongest deterministic observations for a motion project.

The design's observation/fact rule is binding: filenames, titles, headings, metadata, and manifests are observations; facts are later conclusions with cited evidence. This memo therefore treats `Storyboard_v03`, `Approved`, `R3`, codec, dimensions, and archive paths as clues, never as automatic stage, approval, project, or ownership facts. The design also states that the extension is a routing signal rather than an assumption about meaning, which is why `file_kinds.never_alone` is true.

## J-DEPTH file pass (first eight)

### 1. `Product_Explainer_Storyboard_v03.pdf`

This is a `text_document` (PDF). Its ordered panels, shot labels, timing notes, narration cues, and transition notes are direct observations of a planned moving work. It can support recognition of a motion-production packet and grouping with its animatic and project file. `v03` supports universal version-family evidence, not “review” or “approved.” Nothing here writes a folder path, a project field, a client, or proof that the final animation exists. Without corroborating packet members it falls through to Independent Records.

### 2. `Product_Explainer_Animatic.mp4`

This is `audio_video`. A rough timed sequence of storyboard panels with temporary voiceover is an animatic-shaped observation; duration and codec are extractor metadata. The container alone does not distinguish a render from a camera clip. It may group with the storyboard and later proofs, but it must not imply final approval, authorship, or a project name from metadata. If isolated, Review Later is safer.

### 3. `Product_Explainer_Master.aep`

This is `design_creative`. Named scenes, text layers, keyframes, precompositions, linked SVGs, and output modules are a strong production-structure signal. The filename is not sufficient to make `Product Explainer` a fact, nor does `.aep` prove delivery. Linked assets may be absent, stale, or external. If the proprietary format cannot be read, retain indexed-but-unreadable metadata and let the surrounding packet carry recognition; otherwise the detached file goes to Review Later.

### 4. `Explainer_R2_Client_Notes.pdf`

This is a `text_document` and a collision/also-context fixture. Annotated timing, easing, copy, and transition changes tied to a preceding proof are review evidence. The word Client does not establish a client fact, and requested changes do not establish approval. It may be grouped with `creative.client-engagement`, but this catalogue layer must not copy a client or project fact from neighbourhood context onto the file. With no coherent work packet it remains Independent Records.

### 5. `Explainer_16x9_1080p_R3.mov`

This is `audio_video`. The same stem across square and vertical variants is a delivery-set observation; dimensions, duration, and codec are direct metadata. `R3`, `1080p`, and the word render do not prove approval or stage. A project composition or manifest is needed to separate this from a camera or edited-footage export. Detached renders go to Review Later.

### 6. `Explainer_Delivery_Manifest.xlsx`

This is a `spreadsheet`. Platform, aspect ratio, subtitle language, filename, checksum, and handoff status columns are a strongly labelled handoff structure. A status cell is not legal acceptance; a listed filename is not proof the member exists. The manifest groups with the render set when stems and identifiers agree. Alone it is Independent Records.

### 7. `Character_Rig_and_Assets.zip`

This is an `archive`. Its manifest can show vector parts, rig files, textures, font references, audio, and proxies repeating the work stem. Archive paths are observations, not facts about the files' contents, and proprietary members may be unreadable. It is a motion packet member when the manifest and a readable composition connect it to the work; otherwise Review Later.

### 8. `Brand_Kinetic_Titles_Approved.mogrt`

This is `design_creative` and a deliberate false positive. Editable text controls and animation presets show a reusable template, but no brief, storyboard, review packet, or local work identity exists. “Approved” is a filename token, not approval. It may be related to brand identity as a deliverable or asset, but it does not activate this motion template on its own. Review Later is the residual outcome.

## Additional collision fixtures

`Festival_Trailer_Camera_Original_0042.MOV` is `creative.shoot-day-media`, not motion graphics: camera-original naming and capture metadata are present, while animation structure is absent. This is the same `.MOV` evidence class that could otherwise be misrouted.

`Animated_Logo_Research_References.pdf` is Reading Inbox material: it contains public examples, URLs, and commentary but no local source, brief, proof, or render. “Animated logo” is not enough to turn references into authored work.

`creative.post-production` competes when a project contains a timeline, compositing, review exports, and rendered video. The reciprocal boundary is source ontology: designed motion has generated/keyed/vector/text elements and storyboard-to-render evidence; post-production is anchored by recorded footage and editorial/finishing evidence. A hybrid may plausibly activate both; that remains the open question below.

`code` competes when Lottie, SVG, JSON, or scripts appear. Repository roots, package manifests, tests, and build structure support code; a motion project may consume code but is not thereby a repository. `photos` competes on style frames and screenshots; EXIF/capture-event evidence supports photos, while a style frame needs motion-packet linkage.

## Why there are no fields

The assignment's inherited field list is empty because the creative schema is a ratified field-less placeholder. I found no licence to mint a motion-specific canonical key. `project`, `stage`, and `artifact_type` are already canonical proposals in the creative schema's research, but adding `motion_stage`, `animation_type`, `render_format`, or `delivery_platform` would duplicate concepts or turn values into fields. Those values belong in future template logic after Joseph resolves the creative schema question. `fields: []` is therefore intentional and contract-compliant.

The provisional dimension prose in JSON is not a hidden schema: if the schema is later expanded, client (only where non-collecting), project, stage, artifact type is the plausible order. Stage values are storyboard, animatic, animation, review, render, and delivery. The user may later reverse, remove, or flatten dimensions; no path is written here.

## Reciprocal boundaries and edges

- `creative.post-production`: collision, because the same timeline/render packet can be confused; source-footage versus generated-motion evidence is the discriminator.
- `creative.shoot-day-media`: collision, because both carry moving-image containers; camera-original/capture metadata versus generated composition evidence separates them.
- `code`: collision, because web-animation source can look like both; repository/build structure versus authored visual production separates them.
- `photos`: collision, because style frames/screenshots can look like still images; capture evidence versus storyboard/review/render linkage separates them.
- `creative.client-engagement`: a review note can belong to both a motion work and a client engagement. The JSON records this as `also_schema` on the example for contextual grouping, while `also_holds_with` remains empty because the closed contract permits that edge only between schemas, not template rows.

No edge is asserted to `creative.brand-identity`: a kinetic-title template may be an identity-system asset, but the evidence is not enough to say every such file carries both templates. The false-positive example explicitly blocks activation from the asset alone.

## Residual routing

Independent Records is the safe home for a coherent standalone storyboard, review note, or manifest without an accepted work group. Review Later catches detached renders, ambiguous project files, unsupported proprietary formats, and incomplete packets. Reading Inbox catches public references and tutorials. One-Off Images catches isolated style frames or thumbnails without production linkage. These are fallthrough destinations, not domain nodes.

## NEEDS-JOSEPH

- **NJ-MOTION-1:** Should future creative fields `project`, `stage`, and `artifact_type` make this lifecycle a destination-capable template, or should motion remain structural on the field-less placeholder? Option A improves project → stage → artifact retrieval; Option B avoids premature fields.
- **NJ-MOTION-2:** When a motion project composites substantial camera-original footage, should it co-activate `creative.post-production`, or should one template own the accepted group and the other remain a collision boundary? Both choices preserve the observation/fact split; they differ in grouping and review semantics.

## Claims and self-verification

Claims are limited to inference from the authority documents and concrete file fixtures above. No thresholds, confidence scores, new field keys, handling classes, invented gazetteers, or source-type values were added. `fields` and `proposed_fields` are empty. The JSON parses with `python3 -m json.tool`; all ten examples use allowed source types, and the first eight are fully discussed above. Only the assigned JSON and memo files were created.
