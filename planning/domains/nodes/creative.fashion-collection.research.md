# Research notes — creative.fashion-collection

**Depth: J-DEPTH.** Mechanical deepening marker; the node remains a placeholder template over the empty creative schema.

## Sources used

- `planning/00-database-agent-product-design.md` (authoritative design): files carry many facts; schemas stay small; templates describe organizational situations; work types are values; grouping does not copy facts; residuals are broad fall-through homes.
- `planning/prompts/ALIGNMENT.md`: creative is a placeholder schema with no field rows; template dimensions may not invent fields.
- `planning/domains/_CONTRACT.md` and `planning/domains/CONNECTION.md`: template node test, observation/fact split, closed edges, source types, and residual vocabulary.
- `planning/domains/roster.json`: confirmed `creative.fashion-collection` is a template over `creative`; considered `career.portfolio-work-samples`, `photos`, `creative.brand-identity`, and `creative.client-engagement`.

## Concrete file fixtures

The JSON covers ten realistic records: collection overview, technical flat, tech pack, fit-review spreadsheet, line sheet, production archive, lookbook image, launch email, public trend report, and a brand-identity manual. It includes labelled structured records, prose/email, OCR-adjacent image material, a mixed archive, a sparse/isolated image collision, and a neighbour-owned brand guide. Observations are kept separate from legal facts; no filename, folder, season token, or group membership is copied into a fact.

## Why this template survives the node test

This is not a garment, extension, season, or work-type node. Its positive situation is a collection lifecycle: concept → style development → sample/fit → line sheet → production → launch. The coordinated identifiers and cross-stage evidence differ materially from a default creative artifact bucket. The template remains placeholder because the shared creative schema declares no fields; it therefore writes no `fields` or `proposed_fields`, and its `dimension_order` is empty.

## Fields and proposed fields

None. `creative` is intentionally empty under PR-6/J-IND. Candidate concepts such as collection, season/drop, lifecycle stage, style, and artifact type are recorded only as observations/work-type values and as a NEEDS-JOSEPH question; minting private field keys here would violate the canonical-field contract.

## Neighbours considered without an edge

- `code`: pattern/CAD files can be stored in software repositories, but no roster evidence required a code edge; repository structure would be a separate positive code signal.
- `photos.camera-events`: this template already collides with the `photos` schema for lookbook/campaign images; a separate camera-event template edge is unnecessary and would over-specify the same boundary.
- `creative.licensing-rights`: rights and model/fabric permissions may co-occur, but operative grants are owned by the rights situation; no `also_holds_with` is authored because that edge is schema-to-schema and this is a template.
- `creative.stock-asset-library`: purchased fabrics, textures, or references can appear in a packet, but independent reusable inventory is a different situation; the file-level distinction is covered by residual/review handling rather than a required edge.

## NEEDS-JOSEPH

- NJ-FASHION-1: ratify whether collection/project, lifecycle stage, artifact type, and season/drop should become shared canonical creative fields, or remain runtime values/search facets.
- NJ-FASHION-2: decide whether commissioned fashion work can co-activate `creative.client-engagement` and this template from disjoint evidence, or whether engagement is the sole activation and fashion is selected during grouping.
- NJ-FASHION-3: decide whether a lookbook image's launch role should remain a creative work-type value when it also activates `photos`, rather than introducing a media-specific field.
