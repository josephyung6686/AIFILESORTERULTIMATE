# photos.camera-events — lab notes

Date: 2026-08-22
Row: `kind: template`, `schema_id: photos`, `launch: full`, built (not refused).
Output: [`photos.camera-events.json`](photos.camera-events.json)

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  (54 of them) was grep-matched against this file before it was written; the check was re-run
  against the finished JSON and reported 0 unverified.
- `planning/01-product-design-structured.md` — §2.6 Images, §2.7 OCR, §7.2–7.3 the residual
  library. Used only as a locator; `00` is what is quoted.
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`,
  `planning/domains/CONNECTION-EXAMPLES.md` (HEIC fixture), `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed the id, kind, `schema_id`, the two
  `must_consider_neighbors` (`identity`, `medical`) and the eight sibling templates on the photos
  schema. Every edge target was checked back against this file.
- `planning/domains/canonical_fields.json` — the six photos keys plus the universals. No key was
  minted; the one gap found is in `proposed_fields`.
- `planning/domains/nodes/photos.json` — the schema row this template points at, read closely
  because the node test is a comparison against its default template.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, `RELIABILITY_STATES`.
- `planning/deferred-catalogues/03-sensor-aspect-ratios.md` and `04-camera-filename-patterns.md` —
  consumed, not invented. Catalogue 03 supplied the reinforcement-never-proof rule for
  sensor-shaped dimensions; catalogue 04 supplied the recorded fact that iOS gives screenshots
  saved to Photos the same Apple/DCF `IMG_####` stem, and its rule 2 that a filename carries no
  signal tier. No regex and no ratio table was copied into the node.
- Sibling nodes read for edge shape and house style, not rewritten: `academic.coursework`
  (built despite dimensions identical to its schema), `research.project-workspace` (refused),
  `applications.purpose-packet`, `career.recruiting`, `academic.study-abroad`.

## The node test — why this row was built and not refused

This is the closest call in the photos family, and it deserves the argument in full because the
row's dimensions really are identical to `photos.json`'s default.

Refusal was the live option. `00` states exactly one order for this material — "a Photos template
may define year → event" — and `photos.json` already carries it. CONNECTION.md §8 explicitly
supports resolving a schema id "through the schema's default template", so nothing breaks if the
row does not exist. That is precisely the reasoning `research.project-workspace` used to refuse.

What separates the two cases is whether the row has a positive fingerprint or is a complement.
`research.project-workspace` refused because every signal it could claim was already a named
sibling's, leaving "a project identifier fires and no sibling dominates" — a definition by
subtraction. Here the arithmetic runs the other way. The photos schema has **nine** templates;
eight of them are deviations defined against the camera roll (screen-capture bands, OCR'd document
content, rephotographed prints, flight-log metadata, duration-led recordings, export layouts, chat
archives, away-from-routine GPS spans). The camera roll is the thing they deviate *from*, and its
signals are the ones no sibling claims: tier-1 EXIF make/model with `DateTimeOriginal`, sensor
aspect ratios, RAW+JPEG pairing, burst and `IMG_E####`/`.AAE` derivative families, and
spatio-temporal clustering of a *run* into an occasion. The schema row carries a one-line summary
of some of these because it must activate the schema; it does not and should not carry the
situation-selection fingerprint for nine siblings.

The concrete test I used: is there a file that cannot be adjudicated without this row? Yes —
`IMG_4602.PNG`, an iOS screenshot with a camera-shaped filename sitting in the middle of a camera
roll. Schema activation says "photos" and stops. Choosing between this row and
`photos.screenshot-captures` is what resolves it, and that comparison needs two rows.

Honesty about the limbs, recorded in the node's `node_test_note` and again in `open_question`:
dimensions identical, privacy rules materially identical, detection signals genuinely different.
Under CONNECTION.md §2's "or" test one limb suffices; under the dispatch prompt's "and" test the
row is not refusable. If R1c disagrees, the fold is cheap and the fork is written down rather than
silently resolved.

## Files considered and rejected

- **`.ics`, `.vcf`, `.eml`** — this situation never sees them. A calendar entry naming a birthday
  party is not evidence that a capture belongs to that occasion, and CONNECTION-EXAMPLES already
  settles that a calendar file is a `SOURCE_TYPE`, not a domain. Excluded from `file_kinds` on
  purpose, so R1c's coverage pass sees an honest gap rather than a padded claim.
- **`gel_run3_2026-02-11.tif`** (lab imaging) — a real capture, but its device metadata is an
  instrument's, not a camera's, and it belongs to the research templates. It is already the
  photos-schema fixture for `also_holds_with research`; repeating it here would have been a second
  copy of the schema row's work. Replaced by `IMG_7788.HEIC`, a handheld capture at a poster
  session, which carries the same two-schema shape on evidence this situation actually produces.
- **A scanned print of a 1994 photograph** — the family-archive sibling's core case, kept out
  except as the collision signal.
- **A Google Takeout `.zip`** — the export sibling's. The card-dump `.zip` I kept instead is the
  archive this situation really produces, and the pair is what the `photos.social-media-export`
  collision discriminates.
- **A screenshot with dense OCR of a receipt** — the screenshot sibling's, and `00`'s own warning
  that OCR density decides nothing is carried as a `never_alone` rather than as a fixture.
- **`Hw 5.pdf`, the photographed homework page** — kept on the schema row where it belongs; it
  reaches OCR through a PDF wrapper, not through a camera roll, and it is `photos.scanned-documents`'
  territory.

## `proposed_fields` — one, and why it is not padding

**`capture_date`.** `00` names this fact verbatim, twice — "capture date = 2026-07-17" appears
both in the list of what a fact is and in the observation/fact demonstration against EXIF
`DateTimeOriginal` — and `canonical_fields.json` has no key for it. `capture_year` is the Photos
sentence's key and is year-grained; `creation_date` is the universal filesystem/document timestamp
and its own canonical row separates the two concepts, with `00` warning that filesystem times get
rewritten by restores and syncs.

The reason it matters *here* rather than on the schema row: this template's `event` field is
`validated`, and the rule family that validates it clusters a run of captures by camera identity,
contiguous capture time and GPS. With only a year, no run can be bounded and no occasion can be
proposed deterministically — the one thing `00` says this material supports.

Seeded `destination_eligible: false` on purpose. `00`'s order is year then event, and day-level
folders are the failure it warns about ("a large number of tiny folders"). The proposal adds a
fact the design already names; it adds no folder level. Nothing was written into
`canonical_fields.json` and no dimension branches on it — R1c's call.

## Neighbours considered that did **not** get an edge

- **`photos.messenger-export`** — tempting, because the stripped-EXIF WhatsApp photograph is one
  of my fixtures. Rejected: that sibling is about conversation archives with embedded media, and a
  loose re-encoded JPEG in Downloads is not an export. The file is handled where it belongs, as a
  `never_alone` fixture for the absent-EXIF trap.
- **`photos.scanned-documents` vs `academic` / `finance`** — a photographed page can be any of
  them, but those collisions are the *scanned-documents* row's to carry, not this one's. This row
  collides with the sibling that owns the shape, once.
- **`code.*`** — a screenshot of a stack trace is `00`'s own example of what a screenshot might be
  of, but it never reaches this situation: no camera EXIF, and the screenshot sibling adjudicates it.
- **`career.portfolio-work-samples`** — a photographer's client shoot is arguably a work sample.
  Deliberately not edged: the discriminator would be occupation, not evidence, and this row has no
  observation that could carry it. Noted as a gap rather than guessed at.
- **`legal.*`** — a photographed accident scene or a document-of-record capture. No signal in this
  row's evidence separates it from an ordinary capture until OCR runs, at which point
  `photos.scanned-documents` owns the routing. Left unedged rather than asserted.
- **`identity` / `medical` as schemas** — the roster's `must_consider_neighbors` names them at
  schema level, but `collides_with` joins same-kind pairs only, so the edges point at
  `identity.core-documents` and `medical.personal-health-records`, which are the template rows that
  actually receive those files. Both are on the roster; both edges carry the protection-first
  reasoning from `00`. Reciprocity is R1c's.
- **`also_holds_with`** — authored as empty on purpose. CONNECTION.md §5 joins schemas only; the
  photos↔research pair already exists on `photos.json`. The prompt's node shape offers the slot to
  both kinds and CONNECTION narrows it; **CONNECTION wins, and this is the one place the two
  disagreed.** The fixture (`IMG_7788.HEIC`, `also_schema: research`) carries the evidence anyway.
- **`role_split`** — empty, after looking. The photos schema's six keys hold no two names for one
  entity type in two roles. The near-case is photographer versus subject, and it is already
  neutralised: `camera_information`, `people` and `authored_by` are all destination-ineligible, and
  `00` bars the authorship half from placement outright. Minting the pair to fill the slot would
  have been inventing a relationship the canonical list does not hold.

## Things this row deliberately does not conclude

- No file example writes a folder path. `Japan Trip 2025` appears only as a **value** and as the
  name of a folder the holder already made — evidence, never a destination this row asserts.
- No event fact is written from a single file, a session, a generic `DCIM`/`Photos` folder, or a
  GPS cluster alone. `IMG_4602.PNG` and the WhatsApp photograph are marked
  `group_without_copying_facts` for exactly the `HW 3.pdf` reason: a file may join a neighbourhood
  without the neighbourhood's facts being copied onto it.
- No thresholds, no scores, no handling classes. `sensitivity` is `potentially_sensitive` and
  stops there.

## NEEDS-JOSEPH (this node only)

1. **Is this row the schema's default template, or a row beside it?** Its `dimension_order` is
   `photos.json`'s, because `00` states one order for photo material. Fold it into the schema
   default (and move nine-way situation selection onto the schema row), or keep it as the row that
   holds the camera-roll fingerprint. Recorded in the node's `open_question`; the argument for
   keeping it is in `node_test_note`.
2. **An occasion that crosses a year boundary breaks under a `capture_year`-first order.** `00`
   offers the alternatives without choosing — "whether photographs should branch by year, event,
   location, or remain mostly flat" — and this is a decision about someone's real filesystem.
   Not resolved here.
3. **`capture_date` as a canonical key** (see above). `00` names the fact; the canonical list has
   no home for it; this node proposes it without authoring it.
4. **Inherited from the schema row, restated because this row is where it would bite:** `people`
   is seeded destination-ineligible for privacy reasons, and a person-level folder is the most
   commonly requested photo dimension there is. Widening it is Joseph's, never a schema's or a
   template's.
