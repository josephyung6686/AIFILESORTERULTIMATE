# photos.scanned-documents — lab notes

Row: `kind: template`, `schema_id: photos`, `launch: full`, `provenance: inference`.
Node written, not refused. Output: [`photos.scanned-documents.json`](photos.scanned-documents.json).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  file was grep-verified against it before it was written; a final mechanical pass extracted all
  50 quoted spans from the JSON and confirmed each appears verbatim (0 failures). One span was
  edited during that pass: a trailing full stop I had added inside the Protected Records
  definition, which `00` continues with a semicolon. One other span was rewritten to stop the
  quotation before `00`'s curly-quoted list of academic context terms rather than re-typing them
  inside straight quotes.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (§4, the passport
  scan fixture, which is this template's hardest neighbour).
- `planning/domains/roster.json` — confirmed the row, its `schema_id`, its four
  `must_consider_neighbors` (identity, finance, academic, medical), its two
  `must_consider_residuals` (One-Off Images, Protected Records), and the template ids I was
  allowed to point at.
- `planning/domains/canonical_fields.json` — no new key was needed, so `proposed_fields` is empty.
- `planning/domains/nodes/photos.json` — the schema this template points at, read to make sure I
  reused its fields rather than restating them, and to make sure the node test is measured against
  its real default template (`capture_year → event`, `time_first: true`).
- `planning/domains/nodes/academic.transcripts-credentials.json` — read only for landed shape
  conventions (object-form `falls_through_to` / `collides_with`, `node_test`, `privacy_rules`,
  `work_types_note`), which I followed so R1c merges one shape rather than two.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; all twelve file examples check out
  mechanically.
- Deferred catalogues: none consumed. This template's recognition needs no gazetteer content, and
  R2 owns detector patterns, so `proposed_context_terms` is a candidate list of context *shapes*,
  explicitly marked proposal, with no regex.

## Node test — why this is a node and not the schema's default template

It differs from the photos schema's default template on all three axes, and the middle one is the
substantive find:

1. **Signals.** The default template's signals are camera EXIF, GPS and capture time agreeing
   across a run. This template's are the *absence or brokenness of a text layer*, scanner and
   scan-app producer strings, full-page geometry, and document structure inside the OCR region.
2. **Dimensions, reversed.** `00` grants photos the time-first exception because "capture date is
   a defining aspect of the material." For a scan it is not — the defining aspect is the document
   — so the sentence that governs is `00`'s other one, about document and record domains, where
   putting year first "scatters related work across calendar folders." The node therefore
   recommends `media_type → capture_year` with `time_first: false`, a direct reversal of its own
   schema's default. That reversal is the clearest evidence the row is a real organizational
   situation rather than a relabel.
3. **Privacy.** `00`'s protection sentence begins with exactly this material ("A scanned passport,
   tax statement, medical document …"), and the Protected Records residual names "passport scans"
   first. The photo-event template has no comparable constraint.

I considered refusing on the grounds that the row is "a media_type value wearing a template's
coat." I rejected that: `scan` *is* a value of `media_type`, but the node is not the value — it is
the situation of a capture whose content is a document, whose detection route is OCR, whose
recommended order is inverted, and whose usual correct outcome is deferral to another schema's
template. A row whose substance is "these files usually belong somewhere else, and here is how to
know that without inventing facts" is a template, not a value.

## Files considered and rejected

- **A born-digital PDF someone named `Scanned contract.pdf`.** Rejected as an example, kept as a
  `never_alone`: it is the reason a scan word in a filename cannot be a first signal.
- **A fax cover sheet as its own example.** Dropped — it adds a `media_type` value ("faxed
  document received as an image", kept in `work_types`) and no new evidence shape.
- **A `.vcf` / `.ics`.** This template never sees them. `00`'s calendar and contacts material is
  format, not capture; `CONNECTION-EXAMPLES` §5–6 already fixture them. The one messaging-shaped
  case that *is* real here is the mail carrying a scanner attachment, which I kept because it
  shows the capture facts belonging to the attachment record and not to the `.eml`.
- **A scanned photograph (a paper print on a flatbed).** Genuinely ambiguous and genuinely
  interesting, but it belongs to `photos.family-archive`, whose roster hint already claims
  "inherited and re-scanned family photographs". Left there rather than fought over; noted here so
  R1c can decide whether the two rows want a `collides_with` (I judged the seam thin enough that
  the media_type/geometry discriminators already cover it, and did not author the edge).
- **A drone-captured document.** Absurd; not written.
- **`IMG_4821.png` with no EXIF and no OCR.** Already the photos schema row's fixture, and its
  point is that *nothing* activates. Reusing it here would have implied this template can fire on
  absence, which is precisely what its `never_alone` list forbids.
- **`Hw 5.pdf` and the passport scan appear on the schema row too.** Kept deliberately, not by
  oversight: both are `00`'s own files and both are this template's route (a PDF with no usable
  text layer, and the protection seam). The readings do not conflict — the schema row asks what
  fields are legal, this row asks how the situation is recognised and where it defers.

## proposed_fields

None. The row reuses the schema's six inherited keys and branches only on `media_type` and
`capture_year`, both canonical and both `destination_eligible: true`. The two fields I felt
pressure to invent, and did not:

- A "document capture confidence" or "scan quality" field — that would be a score, and every
  threshold in this product is an injected slot; the honest home is `00`'s extraction-outcome
  record (`complete` / `capped`), which is P4's, not a domain field.
- A "captured document type" field — that is the other schema's field (`work_type`,
  `record_type`, `application_document_type`) reached by activating that schema, which is exactly
  what this template's deferral pattern is for. Minting a photos-side clone would be the 574's
  failure in miniature.

## Neighbours considered that did not get an edge

- **identity, finance, academic, medical (the roster's four `must_consider_neighbors`) as
  schemas.** No edge, by contract: `collides_with` joins same-kind pairs and `also_holds_with`
  joins schemas only, so a template row cannot point at a schema with either. Where the dispatch
  prompt implies a template may author `also_holds_with`, **CONNECTION wins and I followed
  CONNECTION** (noted in the node's `also_holds_with_note`). All four neighbours are honoured
  through their own *template* rows — `identity.core-documents`,
  `finance.receipts-expenses`, `academic.coursework`, `medical.personal-health-records` — and
  through `also_schema` on the file examples.
- **`legal.leases-agreements`.** The photographed lease example carries `also_schema: "legal"`,
  but I did not add a sixth collision: the discriminating evidence is the same clause-and-signature
  structure the identity and medical seams already illustrate, and six collisions is already the
  honest ceiling for one row. R1c may add it if reciprocity from the legal side wants it.
- **`photos.family-archive`, `travel.trip-photos`, `photos.social-media-export`.** Considered; no
  edge. The first is discussed above; the second and third confuse with `photos.camera-events`,
  not with this row.
- **`research.lab-notebook-protocols`.** A photographed lab notebook page is real, but the photos
  schema row already carries the research also-holds and the gel-image fixture; adding a template
  collision here would duplicate a seam that is already stated where it belongs.
- **`role_split`: empty.** I looked for one and there is none. A role split needs the same entity
  type in two roles (`school` ↔ `target_school`); this row's fields are capture facts, and
  "the scanner" versus "the document's issuer" is not one entity in two roles — the issuer is a
  fact on whichever schema the OCR activates, not on this one.

## Residual fallthrough — why five

Wider than a typical row, and deliberately so: deferral is this template's normal outcome, so its
leftovers are heterogeneous. Each of the five has a distinct fixture, and the roster's two are
both present. One-Off Images takes image-shaped captures, Independent Records takes document-shaped
scan PDFs with a durable purpose (`00`'s definition reads like this pile's inventory), Protected
Records is mandatory for the safety seam, Review Later takes the half-read (capped OCR, misaligned
scan-app text layer, unopened archive), and Unsupported or Encrypted takes what nothing can open.
I deliberately did **not** add Receipts and Confirmations, although `receipt_2026-03-02.jpg` would
suit it: that residual belongs to the finance side's fallthrough, and shadowing it here would
duplicate a home rather than offer one. The example falls to One-Off Images instead, which is the
honest answer when neither the finance side nor this one resolves.

## NEEDS-JOSEPH (this node only)

**When a scan's OCR does activate another schema, does `media_type = scan` still deserve a folder
level anywhere?** Two designs, both consistent with `00`, and it changes where several hundred of
someone's real files live:

- **A Scans branch that holds only the captures nothing claimed.** Everything resolved goes to the
  domain that claimed it; the branch is the residue.
- **No Scans branch at all.** `media_type` stays a search, explanation and privacy fact; the
  resolved captures live in their domains and the unresolved ones go to the residual homes above.

`00` supports both readings and states neither ("Templates use validated facts to create folder
proposals" against "It should recommend flattening when a dimension does not materially improve
retrieval"). This is the sharpest form of the fork the photos schema row already logged about
whether `media_type` may open a folder level at all, and it is a decision about someone's real
filesystem, so it is recorded rather than resolved.
