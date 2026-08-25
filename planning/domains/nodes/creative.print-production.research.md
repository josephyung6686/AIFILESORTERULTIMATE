# Research memo — `creative.print-production`

**Depth: J-DEPTH.** Deepened print-production workflow memo; the placeholder verdict stands.

## Verdict

Keep as a non-refused placeholder template. It is not merely “print files”: the distinctive situation is governance of a physical run—preflight and proof, press approval, imposition/plates, run inspection, packing and delivery. That sequence is materially narrower than the creative default or graphic-design making record. No fields or dimensions are written because the `creative` schema is explicitly fieldless pending the broader schema decision.

## Sources used

- `planning/00-database-agent-product-design.md` — records have many facts; observation is not a fact; schemas are small; templates recommend dimensions; work types are values; grouping must not copy facts; residual destinations are separate; source type is never sufficient alone.
- `planning/01-product-design-structured.md` — structured rendering of the same design constraints.
- `planning/domains/_CONTRACT.md` — node shape, provenance, field and edge rules, and the fieldless placeholder rule.
- `planning/prompts/ALIGNMENT.md` — R1b procedure, especially template-vs-schema and observation/fact discipline.
- `planning/domains/roster.json` — confirms `creative.print-production` is a template over `creative`, with creative, manufacturing, logistics and vendor neighbours available.
- `planning/domains/canonical_fields.json` — confirms no approved print-job field exists and no private synonym may be minted.
- `src/evidence_shape/vocabulary.py` — source-type vocabulary used in the node.

## Files considered

The JSON covers nine concrete fixtures: contract proof, preflight report, imposition plan, press-approval email, press-sheet photograph, run spreadsheet, delivery manifest, mixed production archive and a gallery-wall photograph collision. This deliberately includes labelled evidence, OCR/scan-like ambiguity, email, spreadsheet, image, design-native file context and a mixed archive. A poster photograph belongs to `photos`/`One-Off Images` without production evidence; a printer invoice, courier label or purchase order alone belongs to vendor/logistics/receipts rather than activating this template.

## Field decision

`proposed_fields` is empty. Existing canonical keys do not contain a print job, vendor, quantity, stock, process or delivery-batch handle. Adding those would turn a deliverable/format/vendor workflow into an unauthorized new schema and would duplicate the unresolved creative schema design. `dimension_order` is therefore empty as required by the fieldless placeholder. The open question records the future decision about `project`, `stage`, `artifact_type`, `client`, or a dedicated production-job field.

## Neighbour decisions

- `creative.graphic-design-project`: collision. Press-ready PDFs and proofs can be ordinary design exports; only linked production evidence supports this template.
- `business_operations.vendor-management`: collision. Supplier administration, quotes and invoices are not job production records.
- `manufacturing.production-record`: collision. Both have run/batch records; print-specific artwork/proof context separates this template from generic manufacturing.
- `logistics.shipment`: collision. Tracking and delivery paperwork alone is transport; it joins print production only through the same job packet.
- `photos`: considered but no collision edge was authored because the photo fixture is an `also_schema` example for photos only; the practical boundary is handled by recognition and residual fallthrough.
- `creative.client-engagement`: considered but no edge was needed; a commissioned print job may also be part of a client engagement, while the production template is about press governance rather than commissioner relationship.

## Claims and limits

All print workflow language is marked proposal/inference. No press standards, vendor gazetteer, colour-management rule, quantity threshold, confidence score or handling class is invented. Filename tokens, extensions, metadata, folder names and download sessions remain observations and never activate the node alone.
