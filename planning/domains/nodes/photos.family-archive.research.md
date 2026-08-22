# photos.family-archive — lab notes (R1b)

Roster row: `kind: template`, `schema_id: photos`, `launch: placeholder`, `provenance: inference`,
`must_consider_neighbors: [identity]`, `must_consider_residuals: [One-Off Images]`.
Verdict: **node kept.** Reasons in "Node test" below.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node JSON
  was grep-verified against this file before it was written (34 spans, one re-punctuated after the
  check showed 00's sentence continues with a comma, not a period). Provenance on the row is
  `inference`, and the `design_cite` says so in words rather than implying 00 describes a family
  archive — it does not.
- `planning/domains/_CONTRACT.md` (entry shape, rules 6, 8, 11–15), `planning/domains/CONNECTION.md`
  (node test §2, activation §4, closed edge vocabulary §5, field identity §6),
  `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 1–4).
- `planning/prompts/ALIGNMENT.md` (two roster kinds; work types are values; template ≠ schema).
- `planning/domains/canonical_fields.json` — every field named in the node resolves to a key here;
  no new key was minted.
- `planning/domains/roster.json` — confirmed my id, kind, schema, and every neighbour id I cite.
- `planning/domains/nodes/photos.json` — the schema I point at, read so this row would not repeat
  it. Its `open_question` (may `media_type` open a level; may `people` be widened) is upstream of
  my own third fork and is referenced, not re-decided.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; all eleven file examples use members of it.
- `planning/01-product-design-structured.md` — consulted only to locate the photos paragraphs
  (lines 198–226, 879, 899, 948, 1358–1359); every sentence actually used was then quoted from `00`.
  No § number appears in the node.

## Node test — why this is a node and not the schema's default template

`photos.camera-events` is the schema's default situation and carries 00's own order, year → event.
This row differs on all three of the things CONNECTION §2 asks about:

1. **Detection signals are disjoint from the default's.** The default fires on camera EXIF. This
   situation fires on the *absence* of camera exposure slots together with the *presence* of a
   digitizing device — scanner Make/Model, scanning software, a scanner resolution slot,
   print-proportioned dimensions, a no-text-layer scan PDF, OCR of handwriting on a verso. The one
   case where camera EXIF is present (a phone photograph of an album page) is precisely the
   collision, not the signal.
2. **The recommended dimension order is reversed, and the reversal is the point.** 00 makes photos
   the time-first exception *because* "capture date is a defining aspect of the material". In an
   inherited archive the capture date is the one thing not recoverable: every machine-readable
   timestamp belongs to the scanner, the capture card, or the phone that re-photographed the print.
   A `capture_year` level at the top would collect prints under the year somebody digitized them,
   which inverts 00's parent-context rule. So: `event` → `capture_year`, `time_first: false`, and
   flat is offered as a legitimate outcome under 00's own flattening and one-child warnings.
3. **Privacy posture is heavier.** The default's sensitivity comes from location and people on
   contemporary captures. Here people are the subject matter, and the batch itself is a reliable
   carrier of another domain's protected content — a shoebox digitized in one pass mixes prints with
   passports, diplomas, statements and clinic letters, all wearing identical scanner metadata.

Had only (1) held, I would have refused; a template whose sole difference is which extension it sees
is not a node. (2) is the load-bearing difference.

## Files considered and rejected

- **A `.jpg` with no EXIF at all, nothing else.** Rejected as a file example: it demonstrates only
  the never-alone rule, and photos.json already carries `IMG_4821.png` for that. It survives here as
  a `never_alone` entry ("absence of EXIF alone"), which is where it belongs.
- **A restored/retouched derivative (`Scan_0042_restored.tif`).** Rejected as an example because it
  adds nothing this row decides — it is a `version_family` universal fact plus a duplicate-family
  link, both already owned elsewhere. Kept only as a `work_types` value.
- **A genealogy-site screenshot (`ancestry-record.png`).** Genuinely tempting: OCR returns names and
  4-digit years, which is a nice adversarial case for the "bare 4-digit number" rule. Rejected
  because it is `photos.screenshot-captures`'s file end to end — a screen resolution, PNG, and
  screen-capture software metadata — and putting it here would have been the format-as-situation
  bug. The bare-4-digit rule is stated in `never_alone` without borrowing its fixture.
- **A `.vcf` of relatives.** Rejected: contacts are a `SOURCE_TYPE`, and 00 keeps VCF data
  privacy-protected rather than folder-proposing. It is not this template's evidence.
- **An email with attached scans.** Rejected: the attachments are the files; the mail is
  correspondence and belongs to whichever situation owns `email`. Including it would have widened
  `file_kinds` for no fact this row can fill.

Eleven examples were kept, above the eight the procedure asks for, because this situation's ugly
cases are the whole content of the node: the verso pair, the phone re-photograph, the statement
that shares a batch, the passport that shares a batch, the album PDF with no text layer, the
archive manifest, the tape transfer, the diploma that is also academic, and one contemporary HEIC
included specifically as a file that must *not* land here.

## proposed_fields — none, and why

The obvious candidate was a field for the digitization date, since `capture_year` is defined as
"the year a photo or capture was taken, from capture metadata" and on a scan that metadata is the
scanner's. I did not mint one:

- The universal `creation_date` already records when this file version came into being, which is
  what a scan's device timestamp is. A second key would be a synonym for it in this domain only —
  the exact defect D6's ratification exists to kill.
- The right handling is not a new column but an abstention: the node's `never_alone` and every
  affected file example forbid deriving `capture_year` from a digitizing timestamp, so the field
  stays empty rather than wrong. 00's rule for exactly this shape is that "conflicting signals
  should lead to abstention rather than an invented classification".
- A decade-level date ("1970s") needs no field either — `capture_year` is a string and values
  auto-create at runtime. Whether a decade branch may sit beside year branches in one level is a
  tree-shape question, and it is recorded in `open_question` rather than answered.

Likewise no `album`, no `family_side`, no `generation`: all three are *values* of `event`, and 00's
values rule ("The system may create new values when it sees a new course, project, company,
university, or event, but it should not invent new fields automatically") is explicit that a new
occasion is a value, not a field.

## Neighbours considered that did not get an edge

- **The `identity` *schema* (the roster's own must-consider) got no edge; the
  `identity.core-documents` *template* did.** This is the one place the dispatch prompt and
  CONNECTION disagree. The prompt offers `collides_with` and `also_holds_with` without restriction;
  CONNECTION §5 restricts `collides_with` to same-kind pairs (schema↔schema or template↔template)
  and `also_holds_with` to schema↔schema only. `identity` is a schema and I am a template, so
  neither edge is expressible against the schema and **CONNECTION wins**. The must-consider is
  honoured instead at the kind that is legal — `collides_with: identity.core-documents`, a roster
  template — on the true evidence-item mutex: a passport scanned in the same shoebox pass wears
  byte-identical scanner metadata, the same batch number and the same session as the prints. The
  file-level side is carried by `Grandma passport 1961.jpg` (`also_schema: "identity"`, facts_legal
  reduced to `media_type`, cloud dossier forbidden) and `falls_through_to: Protected Records`.
  `also_holds_with` is therefore empty by rule, not by oversight.
- **`medical`, `finance`, `academic` schemas** — same structural reason (schemas, and I am a
  template), and no template-level edge was added for them either: the scanned statement and the
  scanned diploma sit on the `photos.scanned-documents` seam, which I already collide with, so a
  second edge to `finance.personal-records` or `academic.transcripts-credentials` would duplicate
  a discrimination already made rather than add one. Carried as `also_schema` on the
  `Scan_0007.jpg` and `Dad graduation 1972 - diploma.jpg` examples and as `falls_through_to:
  Independent Records`.
- **`travel.trip-photos`** (template, so an edge *was* available). No edge: a trip photographed on a
  contemporary phone and a trip photographed in 1985 and scanned in 2019 are not confusable on any
  single evidence item — the digitizing-device slot separates them cleanly, and the pair would be
  a topic resemblance rather than 00's evidence-item mutex. Writing it would have been
  `collides_with` used to mean "these are similar", which CONNECTION §9 lists as a named failure.
- **`photos.social-media-export`** and **`photos.messenger-export`** — both produce EXIF-stripped
  JPEGs, which superficially resembles a scan with no camera slots. No edge: their discriminating
  evidence (export layout, JSON sidecars, platform-named filenames) is present on their side and
  absent on mine, so no single item supports both. The stripped-EXIF trap is instead stated as a
  `never_alone` here, which is where it does work.
- **`photos.drone-captures`** — no plausible confusion; not considered further.

Four edges were written, all template↔template: `photos.camera-events` (genuine camera EXIF on a
re-photographed print — the sibling row landed independently and already names this row back, so
that pair is reciprocal already), `photos.scanned-documents` (identical scanner metadata; OCR
content discriminates), `photos.home-video` (a creation-time tag that dates a transfer on one side
and a recording on the other), `identity.core-documents` (the protected record in the same scan
batch). Reciprocity on the other three is R1c's; each edge carries a non-empty `signal` and a
named fixture.

## Activation ≠ grouping — where it bites here

Four examples carry `group_without_copying_facts: true`, and the verso pair is the sharpest case in
this node. `Scan_0043.jpg` (the verso) legitimately yields `capture_year`, `event`, `location` and
`people` from OCR'd handwriting. Its recto, `Scan_0042.jpg`, is the same physical print and yields
none of them. P9 may absolutely assemble the pair — recto/verso is a real typed relationship — but
the year must not be written onto the recto because the neighbourhood contains it. This is 00's own
firewall ("The graph does not automatically copy those missing facts onto sparse files") applied to
a case that feels far more innocent than `HW 3.pdf`, which is exactly why it is written down.
Similarly, the scan batch (`family-photos-box3.zip`, and the shared import folder in
`IMG_5512.HEIC`) is a retrieval clue and never an event: "A session should never be treated as
proof of topic".

## NEEDS-JOSEPH (this node only)

- **NJ-photos.family-archive-1 · event before capture_year.** This row recommends `event` →
  `capture_year`, departing from 00's stated time-first default for photos. The reason is that 00's
  own justification for the default — capture date as "a defining aspect of the material" — is the
  thing an inherited archive lacks. It is still a recommendation about Joseph's real photographs and
  is recorded, not settled. (Also in the node's `open_question`.)
- **NJ-photos.family-archive-2 · decade-shaped values in `capture_year`.** May a `1970s` branch sit
  beside year branches in the same level? Values auto-create, so nothing forbids it; the question is
  tree shape, not schema.
- **NJ-photos.family-archive-3 · `people` as a folder level.** The canonical row seeds
  `people` `destination_eligible: false` and the roster hint marks the widening as pending Joseph.
  A family archive is the one situation where a person-first tree is what people actually build, and
  it is simultaneously the most privacy-loaded level this catalogue could propose. Not resolved
  here; it is a widening of a canonical row, which a template may never do on its own.
- Upstream and merely referenced, not re-opened: `photos.json`'s question about whether `media_type`
  may open a level in the default template.
