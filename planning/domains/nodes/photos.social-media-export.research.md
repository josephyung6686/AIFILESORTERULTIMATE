# Lab notes — `photos.social-media-export`

Date: 2026-08-22 · R1b · one roster row (`kind: template`, `schema_id: photos`)
Output: [`photos.social-media-export.json`](photos.social-media-export.json)

Verdict: **built, not refused.** Node test applied in `node_test_note` on the entry itself.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  was `grep -F`-verified against this file **before** it was written; two batches, thirty-six and
  nineteen spans, all matched. No quotation appears in the node that was not machine-checked.
- `planning/prompts/ALIGNMENT.md` — the two roster kinds, work-types-are-values, and the rule
  that a template repeating its schema's dimensions is not a node.
- `planning/domains/CONNECTION.md` (§2 node test, §3 no-inheritance, §5 closed edge vocabulary,
  §6 field identity) and `CONNECTION-EXAMPLES.md` (fixtures 4, 5, 6, 8 all bear on this row).
- `planning/domains/_CONTRACT.md` — rules 1–6, 8, 11–15.
- `planning/domains/roster.json` — confirmed id, kind, `schema_id: photos`, `launch: placeholder`,
  `provenance: proposal`, `must_consider_neighbors: [code]`, residuals Review Later / One-Off Images,
  `file_kind_owner: [archive]`.
- `planning/domains/canonical_fields.json` — the six photos keys reused, nothing minted.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` and `RELIABILITY_STATES` read from the module,
  not from memory; every `file_examples.source_type` was checked against it programmatically.
- Sibling nodes already landed: `photos.json`, `photos.camera-events.json` (its collision edge to
  this id is what I reciprocated), plus the roster hints for `photos.screenshot-captures`,
  `photos.messenger-export`, `code.software-project`.
- `planning/deferred-catalogues/07-archive-recognizable-markers.md` — read in full, because this
  row's whole detection story is manifest-shaped and I needed to know whether the marker set
  already exists. It does not (see the gap below).
- `planning/01-product-design-structured.md` — **not read.** Nothing in the assignment cited a
  section of it, and `00` covers archives, images, OCR, privacy and the template library directly.
  Recorded so the omission is deliberate rather than silent.

## The node test, and why the row survived

The refusal condition is a template whose detection signals, dimension order **and** privacy rules
are its schema's default. This row differs on all three; the first alone would carry it.

- **Detection.** Every sibling on the photos schema runs on capture metadata. This situation has
  none — the platform stripped it on upload, which `00` names as a mechanism. What is left is
  structural: an export-tool layout in an archive manifest, an exact-stem media/sidecar pairing,
  and labelled slots inside the sidecar. Not one of those appears on `photos.camera-events`,
  `photos.screenshot-captures` or `photos.scanned-documents`.
- **Dimensions.** `capture_year → event → media_type`. The first two are `00`'s Photos order;
  the third is the difference. `photos.camera-events` explicitly refuses `media_type` as a
  dimension because a camera roll is single-valued on it. An account export is the opposite: one
  bundle returns stills, clips, uploaded screenshots and profile images. The leaf sits last under
  `00`'s parent-context rule.
- **Privacy.** A camera roll is media; an account export is the account. Contact data,
  correspondence and account records arrive in the same bundle, and `00` protects two of those
  outright. That is a different regime, not a stricter reading of the same one.

## Files considered and rejected

- **`.ics` inside a takeout bundle.** Real — exports do carry calendars — and cut. It would have
  been a fourth privacy example saying what `contacts.vcf` already says better, and `00` gives the
  VCF case an explicit *do not create folder proposals* sentence that the calendar case lacks.
  `calendar` was dropped from `file_kinds.source_types` with it.
- **A `.eml`/`.mbox` member.** Cut for the same reason: `message_1.json` under an inbox path is the
  same evidence in the shape platform exports actually use, and it doubles as the
  `photos.messenger-export` collision fixture.
- **A member that is also a receipt.** An uploaded photograph of a receipt would have been a
  second `also_schema` example. Dropped because `IMG_2318.jpg` (identity) already carries the
  co-holding case *and* the protection-ordering case, and a second one adds no new mechanism.
- **A thumbnail/derivative pair.** `00`'s duplicate and near-duplicate machinery covers it, and the
  more useful version of that observation is in `grouping_reasons` — the same photograph existing
  once in the roll with EXIF and once in the export stripped, which is a shared-material decision
  rather than a second home.
- **An `.html` post page rather than `archive_browser.html`.** Both are export-tool output; the
  root index is the one whose misreading actually costs something (it is the bundle's anchor, and
  reading it as saved reading material sends the anchor to a reading residual).

## `proposed_fields` justification

One field, `export_source`, and it is a **proposal for R1c, not an authored key** — nothing was
written into `canonical_fields.json` and no dimension branches on it.

- *Why it is needed:* it is the only thing this situation knows that no canonical key can hold —
  which service produced the bundle. It is load-bearing for explanation: a `capture_year` on a
  member here came from a sidecar written by an export tool, not from the file, and the product
  owes the user that origin.
- *Why no existing key works:* `media_type` answers what kind of capture a member is, not who
  produced the container; `institution` is the finance schema's record-issuing institution and is
  not on this schema; `authored_by` is the wrong role; `file_type` is a routing signal.
- *Why `destination_eligible: false`:* a per-platform folder is exactly the collector `00`
  forbids — *"A folder should not become a collection point for everything produced by the same
  person or organization."* Refusing the folder level was the harder half of this proposal and it
  is the right answer.
- *Ceiling `validated`, not `direct`:* the value is concluded by a layout rule over manifest paths.
  The rule family is named in the entry; **no pattern, marker string or regex is written here** —
  that is R2's.

**Not re-proposed: `capture_date`.** `photos.camera-events` already proposes it, with `00`'s own
two sentences behind it. This situation needs the same day-grained fact for the same reason (a
sidecar's capture slot is day-grained, `capture_year` cannot hold it) and would have proposed it
independently. Recorded here as *concurrence* rather than as a second row, so R1c sees two
independent nodes needing one field instead of two competing proposals.

## Neighbours considered that did **not** get an edge

- **`photos.scanned-documents`** — an export can contain a photographed document, but the
  discriminating evidence is OCR content, which is not the evidence this row runs on. No shared
  evidence item, so no collision. The case is carried on `IMG_2318.jpg` instead.
- **`photos.family-archive`** — both meet EXIF-less images. Rejected because the confusion is
  already fully described by the `photos.screenshot-captures` edge (absent EXIF discriminates
  nothing here) and a third edge on the same item would dilute rather than sharpen it.
- **`travel.trip-photos`** — an export's album folder often names a trip. But a template collision
  needs a shared *evidence item*, and the trip situation's discriminator is a bounded GPS span,
  which no member of an export carries. An album name is a label the user accepts, not evidence
  that fires two rows.
- **`code.pkm-vault`, `code.notebooks-experiments`** — both are archive-adjacent. Rejected because
  `code.software-project` owns the archive `file_kind` on the code side, and the confusable item
  (package manifests and a `src` segment in a manifest) is that row's, so one edge is the honest
  count.
- **`identity.core-documents`, `medical.personal-health-records`** — real hazards inside a bundle,
  and **not** edges from this row: `collides_with` joins same-kind pairs, and the capture-versus-
  protected-record collision is already authored at schema level on `photos.json` (`photos ↔
  identity`, `photos ↔ medical`) and at template level on `photos.camera-events`. Re-authoring it
  here would be a third copy of one relationship. It is carried as `also_schema` on the file
  example and as a `Protected Records` fallthrough.
- **`also_holds_with` is empty** by contract, not by absence — it joins schemas only, and this is a
  template row. Noted on the entry.
- **`role_split` is empty** after checking: the near-case (the producing platform versus an
  organization inside a member's content) has no canonical pair, and both halves would be
  destination-ineligible anyway.

## Where this row disagrees with nothing, and where it takes a position

- **CONNECTION.md vs the dispatch prompt:** no conflict encountered. The prompt's "if present"
  clauses were all present; the closed edge vocabulary, activation ≠ grouping, browse-only
  `parent_id` (left `null`, per PR-5, R1b never authors it) and the never-authored `shares_field`
  were all followed as written.
- **The position this row does take** is the sidecar seam, and it is recorded as `open_question`
  rather than settled: an exact-stem sidecar is a *named structural* pairing, not a retrieved
  neighbour, so it is not the `HW 3.pdf` case — but the fact it produces on the media member is
  **`validated` via the exact-stem rule, never `direct`**, and proximity never substitutes for the
  name match. If P6 rules that a cross-file labelled slot cannot bear a fact at all, every member
  of every export is a bare image and this whole situation collapses into `One-Off Images`. That
  consequence is stated in the entry so the decision is visible rather than buried.

## Gap found in an existing catalogue (not filled here)

`deferred-catalogues/07-archive-recognizable-markers` has **no export-layout marker family**. Its
`kind` vocabulary is closed at P5's two — `source-code manifest` and `document name` — and its
`ref-document-type-vocabulary` row deliberately refuses to grow the second. So the manifest
markers this situation needs (an export root, per-service folders, an exact-stem sidecar pairing)
have nowhere to live under the current kind vocabulary: they are neither a source-code manifest nor
a document name, and inventing a third kind is `UnknownMarkerKind` at run time, not a modelling
choice. **Flagged, not fixed** — R1b writes no detector content. Whoever owns R2 should decide
whether the pairing is a marker at all or a relationship P6 computes over the member list, which is
the same shape as catalogue 07's own open `unc-python-package-layout` row.

## NEEDS-JOSEPH — this node only

- **NJ-export-1 · Does a per-file metadata sidecar write a fact onto the media file it names?**
  The sidecar's slot is a labelled machine-structured slot (`00`'s definition of direct evidence),
  but it sits on a different file, and `00`'s firewall says the graph does not copy facts onto
  sparse files. This node's provisional position is above (structural name-pairing ⇒ `validated`,
  never `direct`, never by proximity). A *no* answer does not shrink this row — it deletes it.
- **NJ-export-2 · Is an export's folder layout the holder's structure or the tool's?** `00`
  protects existing user structure from being flattened or reorganized, and an export mixes both:
  the album names are the holder's, the service folders and date-named directories are the export
  tool's. Preserve the bundle whole as a packet, re-branch it by the recommended dimensions, or
  split along that seam — a decision about someone's real filesystem, and `00` gives no sentence
  for it.
- **NJ-export-3 (small) · `export_source` as a field at all.** R1c should decide whether it lands
  in `canonical_fields.json` as a search/explanation key or is dropped. It is proposed
  destination-ineligible either way; the only thing that would change is whether the product can
  explain where a member's capture facts came from.
