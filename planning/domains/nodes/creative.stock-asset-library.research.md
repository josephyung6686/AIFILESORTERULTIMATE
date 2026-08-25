# creative.stock-asset-library — research memo

Research depth: **FULL R1b DEPTH (J-DEPTH)**

## Verdict

Keep, narrowly. The row is not licensed by “stock” as a subject, by an `Assets` folder, by file format, by tags, or by the absence of a project. It survives as an organizational situation only when the corpus shows a governed reusable inventory: acquisition or creation, catalogue identity, licence/provenance pairing, and reuse across otherwise unrelated projects. Those signals differ from the creative default’s one-work revision history, even though the field-less creative schema prevents this template from recommending folder dimensions.

The lifecycle is **acquisition → catalogue → licence → reuse**. Acquisition establishes where a component came from, catalogue evidence keeps asset identity distinct from a changing path, licence evidence constrains use, and linked-asset references show reuse without assigning any one project’s facts to the shared component. This is governance in the graph, not a forced directory tree.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped output of `make_prompt.py creative.stock-asset-library`.
- `planning/00-database-agent-product-design.md`, especially its observation/fact split, archive-manifest rules, linked-asset extraction, universal facts, grouping non-propagation, residual destinations, and prohibition on treating extensions or sessions as meaning.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`, `planning/domains/_CONTRACT.md`, `planning/domains/canonical_fields.json`, and `planning/domains/roster.json`.
- The landed `creative` schema and the neighbouring `creative.raw-photo-catalogue`, `creative.self-initiated-work`, `photos.family-archive`, and finance digital-asset work for house shape and reciprocal boundary reasoning. Neighbour files were read, not edited.

No web source is needed to establish that these named files exist: every example is an ordinary artifact emitted by asset vendors, library applications, creative tools, mail systems, or the filesystem. Product claims are grounded in the local authority stack; domain-specific conclusions below are marked as inference.

## Node test

### Detection signals

Passes, narrowly. The creative default centers a named work moving through stages and revisions. A stock library has the opposite stable unit: a component with independent identity that may be linked from several unrelated works. The decisive evidence is relational and administrative: an asset manifest agrees with an archive, preview, receipt and licence; a catalogue database indexes assets it does not contain; working files from unrelated projects reference the same master. None is merely an asset extension.

The false version fails. `texture.jpg` in a folder called `Assets` has no distinct signal. It may be a project dependency, reference image, photo, deliverable, screenshot, or download residue. A bounded download session is weak support only and never a topic. Tags and ratings are application metadata, not legal creative facts. The row activates only from a supported combination or from a dedicated structured catalogue/manifest whose role is legible.

### Recommended dimensions

This limb cannot carry the node. `creative` is a placeholder schema with no declared fields, and the contract forbids dimensions that no active field can populate. Therefore `dimension_order` is empty. Asset type, tags, vendor, licence class, and collection are not smuggled into a prose folder plan. `artifact_type`, if creative later adopts it, could hold values such as texture, mockup, brush, LUT, loop, or 3D model, but this template does not own that decision. Project-first would be actively misleading because the component belongs to no one project.

### Privacy and governance

Passes as a secondary difference. Library catalogues may expose local paths and project references; receipts expose purchaser and order data; licence documents expose names, contract terms and restrictions; proprietary packs may be encrypted or contract-limited. The operational rule is to preserve evidence and relations without asserting legal compliance. A licence file does not prove that every nearby asset is covered, and a purchase does not prove perpetual or transferable rights. No handling class is assigned here.

## Files considered — first eight depth fixtures

### 1. `PaperGrain_24K_v2.zip`

- Source type: `archive`; members include high-resolution TIFF textures, JPEG previews, a README and licence text.
- Observations: the manifest has a coherent product stem and internal structure; no project appears.
- Legal facts: universal facts only. The creative schema declares no fields.
- Unknown: vendor, asset type, licence scope and allowed use cannot become creative facts here. Manifest inspection is not permission to extract members during the normal scan.
- Why it matters: this is strong group evidence only when its product identifier agrees with independent acquisition or licence records.
- Fallthrough: `Review Later` when the pack’s purpose or provenance remains uncertain.

### 2. `PaperGrain_24K_license.pdf`

- Source type: `text_document`; labelled clauses describe media, restrictions and attribution.
- Observations: the title identifies the same product as the archive.
- Legal facts: none on the creative placeholder; the same bytes may activate `legal` on legal evidence.
- Unknown: a grant cannot be extended to similarly named assets outside the identified bundle. The system must not turn interpretation into legal advice.
- Why it matters: this is the collision fixture with `creative.licensing-rights`. Rights owns the governing document; the library owns its supported relation to asset members.
- Fallthrough: `Independent Records` when unattached.

### 3. `Order_88431_PaperGrain.eml`

- Source type: `email`; sender, order number, product identifier and attachment names are structured or extractable.
- Observations: identifiers agree with the archive and licence.
- Legal facts: none on creative; the same message can remain a finance record.
- Unknown: payment does not prove ownership, exclusivity, duration, sublicensing, or coverage of all files downloaded that day.
- Why it matters: acquisition is part of the governance chain, not a licence substitute.
- Fallthrough: `Receipts and Confirmations`.

### 4. `asset-library-export.json`

- Source type: `code_structured`; records contain local ids, paths, preview paths, tags, collections and missing-link state.
- Observations: this is the clearest dedicated library structure in the set.
- Legal facts: none on creative. Tags and collection names remain application metadata or group evidence.
- Unknown: referenced paths are not stable identity; missing entries are not permission to delete or relocate assets.
- Why it matters: a catalogue can recognize the situation without reading every proprietary asset.
- Fallthrough: `Independent Records` if no asset corpus can be joined safely.

### 5. `Concrete_017_4K.tif`

- Source type: `image`; dimensions and profile are extractable.
- Observations: its basename occurs in a manifest and in linked-asset lists from two unrelated projects.
- Legal facts: none on creative.
- Unknown: TIFF and high resolution do not mean stock; neither linking project’s project fact may be copied onto the asset; visual similarity does not establish licence coverage.
- Why it matters: cross-project reuse is the row’s strongest discriminator from an ordinary project dependency.
- Fallthrough: `One-Off Images` without the relations.

### 6. `NeonTitles.mogrt`

- Source type: `design_creative`; proprietary motion-template container.
- Observations: a same-stem preview and vendor manifest sit beside it; deeper parsing may be unavailable.
- Legal facts: none.
- Unknown: extension does not prove template intent, parameters, provenance or permitted use. Indexed-but-unreadable is an honest state.
- Why it matters: opaque creative assets are ordinary here and must not be treated as empty.
- Fallthrough: `Unsupported or Encrypted` if the contextual pair is absent or unsafe to inspect.

### 7. `CityAmbience_TransitLoop_03.wav`

- Source type: `audio_video`; duration, codec and embedded tags are available.
- Observations: pack manifest names it and two unrelated sessions reference the same master.
- Legal facts: none.
- Unknown: title does not establish recorded location; WAV or “loop” does not establish library membership; session facts do not propagate.
- Why it matters: it proves the row is not an image-format folder and that reuse relations work across media.
- Fallthrough: `Reference Clips` without governance evidence.

### 8. `BrandLaunch_Moodboard_Approved.pdf`

- Source type: `text_document`; pages arrange reference images under a named project.
- Observations: project title and approval language dominate; no catalogue, product id, licence pairing or cross-project use exists.
- Legal facts: none here.
- Unknown: embedded imagery is not necessarily stock or independently licensed.
- Why it matters: collision fixture against the creative default and `creative.client-engagement`. It looks like a stock collection but is one project artifact and must be rejected from this row.
- Fallthrough: `Reference Clips` if no creative project activation remains.

## Additional collision fixtures

`DSC_0342.NEF` beside XMP and a catalogue database belongs to `creative.raw-photo-catalogue` when the organizing fact is a managed capture archive. Camera RAW, catalogue membership and lack of a current project do not prove stock reuse. In the other direction, a TIFF texture with acquisition evidence and references from unrelated projects is not a camera archive merely because a catalogue indexes it. The competing bytes are the catalogue database, sidecar and image master; the discriminator is capture/edit lineage versus reusable-component governance.

`icons-source.svg` in an application repository belongs to `code.software-project` when code imports, build structure and repository scope explain it. Multiple symbols and a licence comment do not make a personal stock library. In the other direction, an independent icon pack with its own manifest, purchase/licence pair and reuse beyond the repository is not swallowed by code merely because one repository imports it. The same SVG bytes may be a dependency, but the organizational situation is established by surrounding relations.

`PaperGrain_24K_license.pdf` competes with `creative.licensing-rights`. Rights takes the document when the grant, clearance, term or obligation is the retrieval purpose; this row takes the governed asset group only when product identifiers join the document to concrete members. Neither side may infer legal compliance. The licence can remain attached to both supported groups without becoming two contradictory classifications.

`BrandLaunch_Moodboard_Approved.pdf` competes with `creative.client-engagement`. Client engagement takes a named work’s brief-to-review-to-delivery record. This row takes independently identified components reusable beyond any one job. A project’s `Assets` subfolder stays with the project unless independent catalogue, provenance and reuse evidence survives outside it.

## Files considered and rejected

- `Downloads/Assets/texture.jpg`: folder words and extension only; route to `One-Off Images` or `Review Later`.
- `Untitled-1.psd`: editable creative format but no reusable intent; default creative evidence may apply, not this row.
- `logo_final.svg`: a deliverable or project export until independent library evidence appears.
- `font-license.txt`: standalone rights record; it may govern an installed font, a design project, software bundle or typeface package. Filename alone is never enough.
- `inspiration-board.png`: flat reference capture with no component identities; `Reference Clips`.
- `SFX.zip`: opaque archive name and extension; inspect manifest safely, otherwise `Review Later`.
- `client_assets.zip`: project/client vocabulary dominates and may include supplied logos rather than reusable stock.
- `DSC_0342.NEF`: raw capture belongs to photos or raw-photo catalogue absent cross-project component governance.

## Fields and value discipline

`fields` is empty because this is a template and the creative schema is a field-less placeholder. `proposed_fields` is also empty.

Asset type is a value of the existing canonical `artifact_type` if and only if R1c later licenses that field for creative; values include texture, mockup, icon pack, brush, LUT, loop and model. It is not an `asset_type` field and not a child node per media class. Tags, ratings and colour labels are generic application metadata and retrieval observations, not destination facts. Licence category and permitted-use language belong primarily to the rights situation; this row does not mint `license_type`, `usage_rights`, `vendor`, `collection`, or `asset_library` solely to make a tree possible.

The genuine hole is rights scope. The creative schema memo already surfaces it across `creative.licensing-rights`, this row, and typeface work. This memo repeats the question rather than resolving it. A future field would require a carefully bounded type and reliability policy; free-text legal language cannot silently become a validated permission.

## Neighbours considered without an edge

- `career`: a portfolio may display a stock-backed mockup, but selection-to-show is a different positive purpose. The asset itself does not also become a career fact, so no direct edge is needed.
- `photos`: a downloaded stock photograph lacks personal capture/event evidence. `creative.raw-photo-catalogue` carries the sharper same-kind collision; the `DSC_0342.NEF` example records possible photos co-holding without claiming that all images collide.
- `photos.family-archive`: scans and inherited images are governed by provenance in an ordinary-language sense, but not by reusable licensing. The same bytes compete only if someone later turns a scan into a reusable texture; that transformation produces a derived component rather than changing the family record.
- `creative.typeface-font`: fonts can be library assets, but a typeface family’s design sources and specimens form a making record. The licence collision is already represented through `creative.licensing-rights`; a font extension alone cannot choose either row.
- `business_operations`: an organization’s digital-asset-management system could use similar catalogue files, but this row is scoped to a person or small creative team’s reusable components. No landed distinct DAM schema was found to support a reciprocal edge.

## Residual boundaries

`Reference Clips` receives useful media kept for later retrieval when catalogue, provenance and licence governance are absent. In the reverse direction, once a supported asset identity joins acquisition, licence or cross-project reuse, calling it merely a reference clip would discard operational obligations.

`Independent Records` receives unattached licences, catalogue exports and durable notices. In the reverse direction, an independent record joined by matching product or asset identifiers remains evidence for the governed library group without losing its own residual retrieval role.

`Review Later` receives ambiguous packs and mixed downloads. In the reverse direction, review must end in a supported group only after manifest and contextual evidence resolves the relationship; folder adjacency is insufficient.

`Unsupported or Encrypted` receives or represents unsafe proprietary databases and protected archives. In the reverse direction, unreadability does not erase known manifest or filesystem relations, but it blocks content claims.

## NEEDS-JOSEPH

1. **NJ-STOCK-1 — rights scope field or metadata only.** Option A: keep licence language as searchable generic metadata and let `creative.licensing-rights` own its interpretation. Option B: adopt a bounded canonical field on creative after defining extractor ceilings and non-advice semantics. This row recommends no field now.
2. **NJ-STOCK-2 — stable library membership.** Option A: keep catalogue membership as a reviewable graph relation, avoiding a new field and folder level. Option B: add a canonical collection identifier only if multiple schemas genuinely need the same join handle. A private `asset_collection` key for this row is rejected.
3. **NJ-STOCK-3 — reciprocal survival with licensing-rights.** If rights work concludes that licence pairing alone defines its row and acquisition-to-reuse adds no independent governance, merge this row into that template or the creative default. If cross-project reuse and dedicated catalogue structure remain sufficient positive signals, retain both with the boundary stated above.

## Self-check

The JSON uses the universal node keys from the stamped assignment, keeps `fields: []`, proposes no private fields, uses only allowed source types and residual names, and contains ten concrete file examples with the first eight expanded above. The JSON and memo agree on the keep verdict, empty dimensions, collisions, residuals and three open decisions. Every quoted product claim was avoided in the JSON or paraphrased in the memo, so no unverifiable quotation was introduced. The file ends cleanly here.
