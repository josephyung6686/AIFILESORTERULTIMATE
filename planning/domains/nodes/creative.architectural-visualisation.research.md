# creative.architectural-visualisation — J-DEPTH research memo

## Verdict

**KEEP, narrowly, as a placeholder template.** The row survives because a visualisation can be recognised as an architectural source-to-output chain: commission or brief → named scene/model and views → rendered stills/animation/boards → review and approval → display/publication/use conditions. It is not justified by the words `render`, a 3D extension, a building name, or an image style. `fields: []` and `dimension_order: []` are required because the creative schema declares no field rows (PR-6 / D1 deferral).

This is an inference extending the design's named creative-project coverage. No fabricated design quotation is used. I ran `python3 planning/domains/dispatch/make_prompt.py creative.architectural-visualisation` before authoring.

## Sources and comparison set

I used the stamped assignment, `planning/domains/dispatch/RESEARCH-BRIEF.md`, `planning/00-database-agent-product-design.md`, `planning/01-product-design-structured.md`, `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`, `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `src/evidence_shape/vocabulary.py`, and the landed creative and construction neighbours. In particular: `creative.client-engagement` for commission/review boundaries; `creative.revision-round` for universal version/review evidence; `creative.licensing-rights` for rights boundaries; and `construction_property.drawings-revisions` / `construction_property.construction-project` for issue-controlled drawing boundaries.

The roster calls this “The visual side of architecture — drawing sets, renders, models, competition boards — for one building or scheme.” I retained that gist but tightened activation to the source-to-render chain and use/approval evidence. The model itself may be authored for construction/BIM rather than visualisation; the output and purpose relationship decides.

## Node test

### Detection

The creative default can group generic source files, exports and version families. This row adds a specific relational object: a building/scheme brief or commission names view purposes; scene/model metadata or a manifest joins cameras/materials to renders; review records identify exact views; and approval/use records name the same render set. Delete “FINAL”, “CGI”, extensions and folder labels from the fixtures and the joins remain. A single render, model, or approval does not activate.

### Dimensions

No distinct dimension order can be serialized. A scheme, view, camera, software package, renderer, output format, competition and publication channel would either be values or retrieval metadata, or would require new creative schema fields. If R1c later adopts the pending creative proposals, the safe prose order is project → stage → artifact_type, flattening a client level when it would be a one-child collector. Dates are not first because request, modelling, render, review, approval and publication are separate clocks.

### Privacy and use

The row is `potentially_sensitive`: unreleased massing, private sites, security-sensitive views, competition embargoes, source models, linked stock/texture/font assets, people/property imagery, recipient contacts and use restrictions can all be present. A public-looking render does not prove public permission. Rights schedules remain rights evidence; this row only joins a schedule when it identifies the exact render/view package.

## Concrete files considered (first eight core fixtures)

| File | What it contains and why it matters | Legal facts / unknowns | Residual if inactive |
|---|---|---|---|
| `Harbour House Visualisation Brief - issued.pdf` | Labelled client, maker, scheme, views, audience, outputs, deadline and approver; opens the commission. | No creative fields; must not infer requested views exist, planning consent, ownership or use rights. | Independent Records |
| `Harbour_House_scene_v06.skp` | Layered scene with building geometry, materials, cameras and linked assets; README repeats the scheme reference. | Version is universal evidence, not approval; linked assets' licences and construction status unknown. | Review Later |
| `Harbour House exterior views R2.zip` | Archive manifest lists named stills, cameras, colour profiles and source-scene reference; no acceptance record. | Packaging/R2 does not prove delivery or approval; archive paths do not create member facts. | Review Later |
| `RE Harbour House views round 2.eml` | Cross-organisation review email names exact views and requests façade/planting changes. | Does not prove implementation, client authority or publication permission. | Review Later |
| `Harbour House CGI approval - signed.pdf` | Approver role names exact R3 views and permitted website/brochure uses, while excluding construction documents. | Does not transfer copyright or approve unnamed views/planning work. | Protected Records |
| `Harbour House marketing-use schedule.xlsx` | Maps render IDs to channels, territory/window, attribution and supplied assets; references approved R3. | A schedule is not itself a grant or proof that neighbours are covered. | Protected Records |
| `Harbour House competition boards.pdf` | Presentation boards combine diagrams and renders, name a competition and deadline, and reference (but do not contain) the source scene. | Submission/win and source-file existence remain unknown; may also support career. | Independent Records |
| `A-201 Harbour House Ground Floor Plan Rev C.pdf` | Controlled title block, drawing number, revision, issue status and transmittal; collision fixture for construction drawings. | Must not activate this row or infer render approval. | Independent Records |

Additional fixtures in JSON cover an isolated render, a flythrough, and the same source-to-output relationship in archive and mail forms. The `Harbour House sunset render.jpg` is intentionally a false positive: without source, brief, review or rights joins it falls to One-Off Images and may also be photos.

## Boundaries and edges

- **`construction_property.drawings-revisions`**: issue-controlled sheets, title blocks, registers and transmittals stay construction. A render may sit beside a drawing set but does not inherit its revision/status facts.
- **`creative.client-engagement`**: the broader commissioner-maker relationship owns brief, scope, fees and general review. This row activates only for the architecture-specific scene/model/view/render chain; one packet may support both without copying facts.
- **`creative.revision-round`**: R2/R3 and markups are universal version/review evidence. This row does not turn a round into a node; exact architectural source/view/output joins are the discriminator.
- **`career`**: a board or case study whose purpose is demonstrating capability or recording a competition submission belongs to career when no local making chain exists. The same source/render packet remains creative.
- **`photos`**: camera metadata, capture chronology and photographic provenance own photographs; rendered appearance alone does not. A phone photo of a render can be both grouped with photos and linked to this packet without copying project facts.
- **`code`**: parametric scripts and automation belong to code when the repository is the object; a script may be an input to a visualisation packet without making the whole repository creative.
- **`creative.licensing-rights`**: licences, releases, expiry and ownership remain rights records. They cohere here only when they name the exact render/view/member or its manifest.

No `also_holds_with` edge is authored: no schema overlap is required for activation. `collides_with` edges are limited to real roster neighbours. Residuals use the closed vocabulary from the design.

## Claims and open questions

Claims are deliberately narrow: the node is not “architecture files”; it is a purpose-coherent visualisation chain. A scene/model may be construction, survey, engineering, or code material; a render may be marketing, portfolio, reference, or photograph. Correct abstention is success where the chain cannot be joined.

`NJ-ARCHVIZ-1` asks whether future creative fields should expose project/stage/artifact_type for this situation; recommendation is to preserve the fieldless placeholder until that schema decision. `NJ-ARCHVIZ-2` asks whether planning/marketing submission envelopes should co-hold with source/render packets or remain separate purpose activations. This memo does not decide either product-level question.

