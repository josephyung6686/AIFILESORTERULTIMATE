# photos — lab notes (R1b, `kind: schema`)

Node: `planning/domains/nodes/photos.json`. Not refused: the six fields are `00`'s own Photos
sentence, they are distinct from every other roster schema (no other schema references
`capture_year`, `event`, `location`, `people`, `camera_information`, `media_type`), and they are
six, inside `00`'s "usually three to six that may help build a future folder proposal".

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every quoted span
  in the node was `grep -cF`-verified against this file before it was written (17 + 5 + 5 spans,
  all count 1). The load-bearing paragraphs for this node are the images paragraph, the OCR
  paragraph, the domain-scoped-schemas paragraph, the template-order paragraph containing the
  photos time-first exception, the reliability-states paragraph, the residual-library paragraph,
  the privacy-boundary paragraph, and the adversarial-suite paragraph.
- `planning/01-product-design-structured.md` §2.6, §2.7, §3.11, §3.15 only — the numbered
  rendering of those same paragraphs. Nothing was taken from it that `00` does not say.
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`,
  `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 4 and 8 are the ones that bind here),
  `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed `photos` is `kind: schema`, `launch: full`,
  `file_kind_owner: ["image"]`, with eight template rows pointing at it
  (`photos.camera-events`, `photos.screenshot-captures`, `photos.scanned-documents`,
  `photos.family-archive`, `travel.trip-photos`, `photos.home-video`, `photos.drone-captures`,
  `photos.social-media-export`, `photos.messenger-export`).
- `planning/domains/canonical_fields.json` — all six field keys resolve; `proposed_fields` is
  empty and no synonym was minted.
- `src/evidence_shape/vocabulary.py` — every `source_type` used is in `SOURCE_TYPES`; every
  `reliability_ceiling` is in `RELIABILITY_STATES`.
- No `planning/deferred-catalogues/` file was consumed: nothing here needs a gazetteer's
  *contents*. `location` names the place-gazetteer rule family (R4's) without inventing a member,
  and no detector regex is written (R2's).
- `planning/domains/nodes/` was empty when this ran, so no neighbour file was aligned against or
  rewritten.

## What the schema is, restated so it is not read as a category

`photos` is not "image files". It is the schema that becomes legal when a file's own evidence says
something was *captured*: a device, a time, a place, a kind of capture. A JPEG is not a photo fact;
`source_type = image` is a routing signal and is never-alone by construction. Conversely a `.mov`,
a `.zip` of an export bundle, and an OCR'd photographed page can all carry capture evidence.

The schema's four destination-eligible fields are `capture_year`, `event`, `location`,
`media_type`; `people` and `camera_information` are the "additional fields used only for search,
privacy protection, explanation, or later review" half of `00`'s sentence. The default template
uses only `00`'s two — year then event — and `time_first` is `true` because this is the one domain
`00` names as the exception to putting subject before time.

## Files considered and rejected

- **`invite.ics`, `contacts.vcf`.** Rejected outright. `photos` never sees them; a calendar event
  titled with a trip name is not capture evidence, and `00` puts VCF data on the privacy side
  rather than the folder-proposal side. CONNECTION-EXAMPLES fixtures 5 and 6 already cover them.
- **`Scan_20260210_0001.pdf` (flatbed output).** Dropped as redundant with the photographed-
  homework example, which makes the same point (no text layer → OCR → the capture reading and the
  content reading are two different facts) and is `00`'s own file.
- **`Logo-final-v3.psd`, `poster.ai`.** Rejected: `design_creative` is a `SOURCE_TYPE`, and
  authored artwork is not a capture. Putting it here would be the format-as-schema bug.
- **`portrait.jpg` in a downloaded stock-image folder.** Rejected: it would only have restated the
  never-alone rule already carried by `IMG_4821.png`.
- **A `.aae` sidecar.** Rejected: it is an edit-family artifact, which is the universal
  `version_family` fact, not a photos field.
- **Kept deliberately because they are ugly:** `IMG_4821.png` (no EXIF, OCR pending — activation
  is legitimately empty), the WhatsApp file (`00`'s own adversarial item: stripped EXIF on a real
  photograph), the photographed passport and the photographed lab letter (protected content
  wearing genuine capture metadata), the takeout archive (manifest-only inspection, `00`'s
  `submission.zip` discipline applied to media), and `Hw 5.pdf` (`00`'s own photographed-homework
  file, which is where `group_without_copying_facts` matters).

## proposed_fields

None. Every field is a canonical key with a verbatim `00` sentence behind it. Two temptations were
refused:

- a `capture_date` or `capture_month` key beside `capture_year`. `00` names only capture year.
  Finer granularity is a *value* question and a template question, not a second column.
- a `device_type` key beside `camera_information` to separate phone / DSLR / scanner / screen
  capture. That distinction is already `media_type`'s job plus `camera_information`'s content;
  minting it would be the 574's failure in miniature.

## Neighbours considered that did NOT get an edge

- **`code`, `finance`, `college_applications`.** These are the screenshot template's neighbours
  (`00`: a screenshot "may be a screenshot of a receipt, application portal, conversation, code
  error, or research figure"), and the roster gives them to `photos.screenshot-captures`. At the
  *schema* level the confusion is not between `photos` and those schemas — a screenshot's OCR
  content evidences them on its own terms while `media_type = screenshot` stays a capture fact.
  Authoring three more collisions here would inflate the mutex list without a discriminating
  evidence item to name. Left to that template.
- **`academic`.** `Hw 5.pdf` is an `also_schema` in the file examples but got no schema edge:
  the roster does not list it as a `photos` neighbour, and the honest relation is "OCR of a
  capture may evidence academic on its own" — which is how every domain reads an OCR'd capture,
  not a fact about photos specifically. If R1c finds academic authoring the reciprocal, that is
  the moment to add it, not now.
- **`identity`, as `also_holds_with`.** Considered and deliberately not authored, though it is
  arguably true (a phone photo of a passport has disjoint camera evidence and identity evidence).
  Two reasons: `identity` is a field-less safety placeholder (PR-6), so co-activation legitimises
  no additional field and buys nothing; and asserting it invites exactly the reading PR-2 forbids,
  that a protected record is also photo-event material with a year folder. The collision edge,
  which says *do not let the capture metadata decide this file's home*, carries the whole truth
  here. Same reasoning for `medical`.
- **`travel`.** Not a roster schema — `travel.trip-photos` is a template over this schema and
  `travel.bookings-confirmations` is a template over finance. Nothing to point at.

## `role_split` — one observation, not authored

`people` (who appears in a capture) and `authored_by` (who took or produced it) are the same entity
type in different roles, which is `00`'s own split shape. It is not authored here because
`role_split` lives in the canonical field list (CONNECTION §6) and this agent may not edit
`canonical_fields.json`; today `authored_by.role_split_with` is `["target_school"]` and `people`
has none. Flagged for R1c rather than written.

## NEEDS-JOSEPH — this node only

1. **May `media_type` be a folder level in the Photos default template?** `00` gives year → event
   and nothing else, yet photo-vs-screenshot is the split most corpora visibly want, and two of
   this schema's four destination-eligible fields go unused by `00`'s order. Recorded in the
   node's `open_question`; not resolved, because it is a decision about the shape of someone's
   real filesystem.
2. **Does `people` ever become destination-eligible?** `canonical_fields.json` seeds it `false`
   for privacy reasons and already flags the widening as Joseph's. Restated here only because the
   `photos.family-archive` template is the place it will next be asked.
3. **Granularity of `capture_year`.** A year-only dimension puts a whole year of captures in one
   branch before `event` splits it. Whether the recommendation should offer year-month is a
   template question for `photos.camera-events`, but it starts from this field, so it is recorded
   here for whoever writes that node.
