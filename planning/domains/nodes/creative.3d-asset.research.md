# creative.3d-asset — J-DEPTH research memo

## Verdict

**KEEP as a narrow placeholder template.** The distinctive object is a lifecycle: brief/build request → model, material, rig or scene sources → versioned review → manifest/handoff → acceptance or use-rights evidence. A 3D extension, a render, or a folder name is not activation. The creative schema is fieldless, so `fields: []`, `proposed_fields: []`, and an empty dimension order are intentional.

This is an inference extending the design’s named creative coverage; no new schema or fabricated design quotation is introduced. The stamped prompt was generated with `python3 planning/domains/dispatch/make_prompt.py creative.3d-asset`.

## Sources and comparison set

I used the stamped assignment, `planning/00-database-agent-product-design.md`, `planning/01-product-design-structured.md`, `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`, `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, and `src/evidence_shape/vocabulary.py`. Neighbour boundaries were checked against `creative.game-art-asset`, `creative.client-engagement`, `creative.revision-round`, `creative.licensing-rights`, `career.portfolio-work-samples`, `code`, `photos`, and construction drawing/model rows.

## Concrete files considered

The JSON contains eleven fixtures, including labelled brief, binary scene, mixed archive packet, review presentation, email acceptance, manifest, rights instrument, rendered video, procedural code collision, manufacturing CAD collision, and isolated reference image. The first eight core fixtures are the lifecycle chain:

`Orbital Drone Asset Brief.pdf` establishes requested purpose and deliverables but not existence, approval, ownership or rights. `orbital_drone_scene_v07.blend` gives source/dependency observations and a version-family fact, but not approval or license facts. `orbital_drone_textures_4k.zip` has a manifest and license note; archive membership does not copy facts to every member. `Drone lookdev review R3.pptx` names exact outputs and requested changes; R3 is not approval. `RE drone asset accepted.eml` accepts a named manifest while excluding sources; it does not transfer copyright. `drone_release_manifest.xlsx` maps IDs to formats and recipients but cannot grant rights. `drone_usage_rights_signed.pdf` limits named assets by use and territory; it does not cover unnamed variants. `drone_turntable_final.mp4` joins by asset identifier but lacks embedded permission evidence.

The procedural repository is `also_schema: code` and should remain code when the repository is the object. The STEP housing is a construction/manufacturing collision based on controlled issue evidence. The downloaded robot image is `also_schema: photos` only as a possible image record; without authored 3D lineage it falls through to One-Off Images.

## Boundaries, dimensions, and safety

Game-art is a collision where engine/platform evidence is the discriminator. Code owns repositories and generators. Photos owns camera capture evidence. Construction owns CAD/BIM issue control, tolerances and transmittals. Career owns a portfolio presentation without local making evidence. Licensing-rights owns the rights instrument; this node only joins it when it names the asset package.

No destination dimensions are legal while creative remains fieldless. Asset name, stage, software, renderer, format, LOD, platform, polygon budget and channel are values or retrieval metadata, not invented fields. The lifecycle is not time-first because build, review, handoff and permitted use have distinct clocks.

The node is `potentially_sensitive`: unreleased geometry, client/product designs, proprietary techniques, licensed dependencies, restricted models, recipient data and use terms can be sensitive. Public appearance is not permission.

## NEEDS-JOSEPH

- **NJ-3D-1:** Decide whether creative should eventually expose `project`, `stage`, and `artifact_type` for this lifecycle; recommendation is to retain the fieldless placeholder until then.
- **NJ-3D-2:** Decide whether general 3D and game-art packages co-hold or activate independently when one package has both creative and engine-purpose evidence.

## Claims

Claims are limited to a purpose-coherent build/version/review/delivery chain. Models may instead be engineering, BIM, scientific, game, code-generated, or reference material; renders may instead be photos, portfolio samples, marketing assets, or downloads. Correct abstention is the intended behavior where joins are absent.
