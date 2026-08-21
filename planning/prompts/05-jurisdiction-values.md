# Dispatch prompt — R5 · one jurisdiction's value lists

Copy everything below the line into a new agent. The agent should not need this chat.

Give it read access to the repo. It writes under `planning/deferred-catalogues/11-jurisdiction-values/`. It does **not** add jurisdiction as a folder dimension. It does **not** invent new **fields** (`w2_tax_year` is a field; `W-2` is a value of `record_type`). `00` §3.12: values auto-create; fields do not.

---

You are authoring **jurisdiction-dependent values**, not a jurisdiction field.

## Why you are here

The design never says "United States" or "GDPR." Overnight catalogues still had to name tax forms, courts, permits, and certificates, and they **split**: design examples are American (`W-2`, `UChicago`, `BUSIB 4300`); domain authors wrote UK-shaped prose (England/UK mentions dominate the 560). Council D4 (recommendation, not ratified): ship **one** jurisdiction matching Joseph's corpus; `jurisdiction` is a **value**, never a field name, **never a destination dimension** (a tree that branches on country is P10's one-way door).

Without value lists, finance/legal/government recognition cannot complete. With the wrong lists, a user outside that region sees a giant residual pile and concludes the product does not work — unless residual can say "this domain is not modelled for your region" (D4 risk seat). You will author that string-slot too.

## Product constraint

Read:

- `planning/00-database-agent-product-design.md` — zero mentions of jurisdiction/country/HIPAA/GDPR. This is **absent**, not under-specified. You are inventing a data pack, not reading a hidden decision.
- `planning/01-product-design-structured.md` §3.11–3.12, §3.15, §5.4, §7.3
- `planning/overnight/council/DECISION-BRIEF.md` D4
- `planning/overnight/NEEDS-JOSEPH.md` B4
- `planning/domains/` finance, law, government slices — mine for values that snuck in as field names
- `planning/deferred-catalogues/10-gazetteers/` if R4 has landed — do not duplicate institution lists; you own **form types, court names, statute labels, permit names**
- `planning/domains/CONNECTION.md` if present

Rules:

- **Fields stay jurisdiction-neutral** (`record_type`, `tax_year`, `court`, `permit_type`).
- **Values** are the packed list (`W-2`, `1099-NEC`, `P60`, `VAT return`) and are loaded per deployment.
- Never a destination dimension. Say so in the schema so P10 cannot put `jurisdiction` in `dimension_order`.
- Safety domains (finance, identity, medical, legal) still activate without a matching value list — protection must not wait on a form name. A UK user with a US-only tax list still gets Protected Records / safety, not `public_low`.

## What to research

**First line of RESEARCH.md:** which one jurisdiction you are packing, and why (Joseph's corpus if stated anywhere; otherwise **stop and write NEEDS-JOSEPH "which one"** with two seed packs sketched, do not pick silently). If you must proceed to keep the schema honest, author **the file shape** plus a tiny `00`-example seed (W-2 is in overnight prose as design-adjacent, not in `00` — mark `proposal`).

Then, for the chosen jurisdiction, value lists for:

1. **Tax record types** (income, property, sales/VAT, info returns) — names as values of `record_type`
2. **Identity document types** (passport, national id, driver's licence, visa classes) — values, not fields
3. **Court / matter types** that appear on real PDFs a person keeps (not the entire civil procedure code)
4. **Permit / licence names** a household or small business actually files
5. **Healthcare record types** that appear on exports (EOB, discharge summary) — careful: detecting them is R2; naming them as values is you
6. **Academic calendar tokens** that are jurisdiction-flavoured beyond R6's three (`Michaelmas` is already in `00` as a required pattern — that one is design, keep it even if your pack is US)

Each value row: `value_id`, `field_key` (must exist in the canonical field list or be marked `field_pending_R1`), `label`, `aliases[]`, `jurisdiction`, `provenance`, `safety_relevant` (bool — if true, R2 should have a detector hook, you do not write the regex).

Also: `unsupported_region_copy` — one string residual/UI can show. Do not invent UX voice beyond a factual slot.

Mark catalogue entries that **already** baked a jurisdiction into a **field name** (if any `w2_tax_year` appears). List them for deletion/rename. D4 said none of 560 had done that as of overnight — re-check; 574 now.

## What you must not do

- Do not ship multiple jurisdictions "to be safe." D4 option 2 was refused.
- Do not add `jurisdiction` to any template `dimension_order`.
- Do not treat HIPAA/GDPR as folder trees.
- Do not close "which jurisdiction" if Joseph has not said. Schema + seed + NEEDS-JOSEPH is a valid done.
- Do not edit `src/`.

## Output

```text
planning/deferred-catalogues/11-jurisdiction-values/
  README.md                 injection; one pack per deployment; never a dimension
  _SCHEMA.md
  PACKS.md                  which pack is v1, which are empty stubs
  us/ or uk/ or <chosen>/   value JSON files by field_key
  unsupported-region.md     the slot + proposed string (proposal)
  field-hygiene.md          field names that smuggled a jurisdiction
  RESEARCH.md
  check.py                  no field_key named jurisdiction in dimension_order anywhere you touch;
                            every value points at a field_key;
                            00's Michaelmas pattern is not deleted
```

## Done when

- Field/value split is mechanical (check.py).
- One pack is either filled or explicitly `awaiting Joseph` with a seed.
- Safety does not depend on the pack.
- P10 cannot discover a jurisdiction dimension from your files.
