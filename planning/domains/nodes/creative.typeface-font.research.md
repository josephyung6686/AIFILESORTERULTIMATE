# creative.typeface-font — lab notes (R1b)

Date: 2026-08-25  
**Depth: J-DEPTH.**  
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.  
Verdict: **REFUSE NODE**.  
Output: `creative.typeface-font.json`.

## Sources used

- `planning/domains/dispatch/make_prompt.py creative.typeface-font` — the stamped assignment and
  the requirement that a template may not repeat its schema's default and must write no fields.
- `planning/00-database-agent-product-design.md` — authoritative design source. The relevant
  boundary is the design's warning that “The engine should treat the file extension as a routing
  signal rather than an assumption about meaning”, its rule that “One file may hold facts from more
  than one domain without losing information”, and its instruction that “The system must separate
  roles that happen to contain the same entity type.” These are quoted only as local design
  principles; none names a typeface domain.
- `planning/domains/_CONTRACT.md` and `planning/domains/CONNECTION.md` — template node test,
  closed edges, residual names, `fields: []` for the placeholder creative schema, and the rule
  that dimensions may only branch on fields declared by the same schema.
- `planning/domains/nodes/creative.json` — the default creative situation is the making record of
  a work, but it declares no fields and explicitly warns that “a font file [is] read as a
  typeface project” never alone; an installed or licensed font is an asset and type design has
  sources, a build and a specimen.
- `planning/domains/nodes/creative.stock-asset-library.json` — reusable assets are detected by a
  governed package/catalogue/manifest and rights or acquisition pairing; it already lists fonts
  among plausible asset formats and routes uncertainty to residuals.
- `planning/domains/nodes/creative.licensing-rights.json` — licence, release, EULA, purchase and
  rights-scope material is refused as a creative template and routed to legal/rights handling.
- `planning/domains/nodes/creative.deliverable-handoff.json` — recipient-facing manifests,
  receipts, acceptance, custody and package membership make an embedded font a handoff member,
  not a font-library or type-production member.
- `planning/domains/nodes/creative.graphic-design-project.json` and `creative.brand-identity.json`
  — a font used in a layout or bespoke identity may be grouped with that consuming work; the
  font's presence does not create an independent typeface situation.
- `src/evidence_shape/vocabulary.py` — source types checked against the closed vocabulary.

## Bottom-up files considered

The JSON lists ten concrete fixtures. Together they cover source, build, binary, web distribution,
specimen, EULA, acquisition email, mixed handoff archive, screenshot/OCR, and build code:

| Fixture | What it proves | What it does not prove |
|---|---|---|
| `AcmeSans.glyphs` | a glyph-source document and, with neighbouring members, a possible production graph | a licence, client, release, or legal destination |
| `AcmeSans.designspace` | variable-font masters/axes and family/version adjacency | that a reproducible release exists |
| `AcmeSans-Bold.otf` | binary format and labelled internal family/style metadata | designed ownership or rights |
| `AcmeSans-webfont.woff2` | a webfont output consumed by a code package | web distribution permission |
| `AcmeSans-Specimen.pdf` | specimen/presentation material | purchase, ownership, or licence scope |
| `AcmeSans-EULA.pdf` | a rights instrument naming a family | that every nearby member is covered |
| `Order-4821-AcmeSans.eml` | acquisition and vendor context | type-production stage |
| `Brand_Rebrand_Fonts_Handoff.zip` | font binaries embedded in a recipient package | that the package contains source or transfers rights |
| `Installed-Fonts-Screenshot.png` | OCR evidence of an installation view | ownership, licence, or type design |
| `build-fonts.py` | code/build evidence | that code is a typeface domain rather than a software project |

The ugly cases are important. `AcmeSans-Bold.otf` and `AcmeSans-EULA.pdf` are the same-byte
collision fixture for asset versus rights versus proposed production. `Brand_Rebrand_Fonts_Handoff.zip`
is also a creative handoff; it must not be split merely because its archive contains `.otf` files.
`Installed-Fonts-Screenshot.png` is a screenshot, not proof of a font library. The sparse binary
and screenshot examples can be grouped near a known family without copying a family or licence
fact onto them.

## Node test

1. **Detection signals.** The only distinct activation candidate is a linked production graph:
   glyph sources plus feature files/designspace, a build configuration, generated binaries, and a
   specimen or release output. A lone font binary is explicitly never-alone; a licence document
   activates rights evidence; a manifest/acquisition pair activates a reusable asset situation.
   The production graph is materially more specific than the creative schema's broad making
   signal, but the current schema declares no fields and no creative template can write a source,
   family, version, or role fact. This is not enough to make a load-bearing node.

2. **Recommended dimensions.** A tempting order would be `typeface → style → source/build/release`.
   None is legal: `typeface`, `style`, `source_format`, `foundry`, and `licence_class` are not
   declared canonical fields on `creative`; a template may not mint them. `project → stage →
   artifact_type` is the only future-shaped order suggested by the creative schema, but that is
   the default making-work proposal and does not distinguish type production. Asset/provider or
   licence/term ordering belongs to the existing stock and rights situations. Therefore the
   recommended order is intentionally empty.

3. **Privacy/routing rules.** This material can expose unreleased type designs, source paths,
   client names, vendor orders, and licence restrictions, so a potentially-sensitive posture is
   warranted. That posture is not a distinct privacy rule: the same protection applies to stock
   assets, rights records, and handoffs. No privacy difference rescues this row.

All three legs fail to establish a separate template under the present schema contract. Refusal is
the honest result, not a missing-depth result.

## Boundaries and rejected false positives

- **`creative.stock-asset-library`** owns a governed reusable font package: catalogue/manifest,
  acquisition evidence, and licence pairing. This proposed row would own only a source/build/
  specimen graph. The same `AcmeSans-Bold.otf` is the collision fixture in both directions: binary
  alone is not enough; manifest plus purchase supports asset library, while glyph sources plus
  reproducible build supports production. No such schema fields exist here, so route to stock.
- **`creative.licensing-rights`** owns `AcmeSans-EULA.pdf`, a purchase confirmation, or a rights
  schedule as the grant/obligation record. A family name in a licence must not activate type
  production. Conversely, a source graph does not become a rights record merely because a specimen
  names a foundry. Route the instrument to licensing-rights/legal.
- **`creative.deliverable-handoff`** owns `Brand_Rebrand_Fonts_Handoff.zip` when the package has a
  manifest, recipient, receipt, acceptance, or custody evidence. The font binary is a package
  member. Conversely, a source/build directory with no recipient-facing package is not a handoff.
- **`code`** owns `build-fonts.py` and the repository manifest when repository structure and imports
  are the organizing evidence. Conversely, a source graph can contain build scripts without being
  a general software project, but that distinction is unresolved without a future creative field.
- **`creative.graphic-design-project` / `creative.brand-identity`** own a font as a linked or
  bespoke component of a consuming work. A brand specimen or a layout reference does not prove an
  independent typeface project; conversely, a genuine source/build graph may be grouped with the
  identity but cannot receive an invented typeface destination.
- **`photos`** owns `Installed-Fonts-Screenshot.png` as capture/screenshot evidence when its photo
  signals activate. OCR family names are not font facts. The screenshot may be near font files
  without copying their metadata.

The rejected false positives are therefore not “less creative fonts.” They are different roles:
asset, rights instrument, handoff member, code dependency, consuming design component, or
screenshot. Treating extensions, style names, or foundry names as a node would repeat the catalogue
failure the contract is designed to prevent.

## Proposed fields

`proposed_fields: []`. No new key is justified. `typeface`, `style`, `foundry`, `source_format`,
`font_role`, and `licence_class` are tempting labels, but the first two are values read from a
font's metadata, `source_format` is routing evidence, `font_role` is a role decision already split
between asset/production/handoff, and `licence_class` belongs to licensing-rights. Minting any of
them would make the refused row load-bearing by private vocabulary rather than by the design.

## NEEDS-JOSEPH

- **NJ-TYPE-1:** Should a future creative schema adopt the existing canonical `project`, `stage`,
  and `artifact_type` proposals before any type-production template is reconsidered, or should
  typeface production remain a work-type value under creative? Adopting fields allows a production
  graph to be grouped; it does not justify `typeface` or `style` as destination keys.
- **NJ-TYPE-2:** Should font licence scope remain exclusively in `creative.licensing-rights`, or
  become searchable metadata on stock assets? The former keeps grants and obligations in one role;
  the latter improves asset retrieval but risks duplicating legal interpretation.
- **NJ-TYPE-3:** Should a future production node require a reproducible source/build/output graph,
  or would a foundry specimen plus binaries suffice? The former avoids mistaking purchased fonts for
  designed type; the latter broadens recall but will over-fire on vendor downloads.

## Self-verification

- `make_prompt.py creative.typeface-font` was run before authoring.
- Only the assigned JSON and research memo were created.
- JSON keys follow the stamped universal shape; `fields` and `proposed_fields` are empty.
- Every `file_examples.source_type` is in the closed `SOURCE_TYPES` vocabulary.
- All `falls_through_to` values are residual template names; all collision targets are roster ids.
- The refusal is explicit and routes coverage instead of inventing a schema.
