# research.conference-presentation — lab notes (R1b)

Roster row: `kind: template`, `schema_id: research`, `launch: placeholder`, `provenance: inference`,
`file_kind_owner: ["presentation"]`, `parent_id: null` (not authored here — PR-5 leaves browse
shelving to R1c).

**Verdict: node accepted.** Not refused, and the reason is written into the JSON's `node_test`
block rather than asserted here.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span this node puts inside
  quote marks was grep-verified against this file before it was written, mechanically, in one pass
  over the finished JSON (46 quoted spans; the only one that did not resolve was a phrase from the
  sibling node file, and it was rewritten to name its real source rather than left ambiguous).
- `planning/domains/_CONTRACT.md` — entry shape, rules 8, 11–15.
- `planning/prompts/ALIGNMENT.md` — the "not a node" rule for templates, work-types-are-values.
- `planning/domains/CONNECTION.md` — node test (§2), no schema inheritance (§3), activation shape
  (§4), the closed edge vocabulary (§5), field identity (§6).
- `planning/domains/CONNECTION-EXAMPLES.md` — fixtures 1 and 2 (the syllabus, and the abstract that
  holds two schemas).
- `planning/domains/roster.json` — confirmed the id, kind, schema, neighbours, `file_kind_owner`,
  and every edge target below exists as a roster row.
- `planning/domains/canonical_fields.json` — every field named here resolves to a canonical key; no
  key was minted.
- `planning/domains/nodes/research.json` — the schema this row points at; its fields, its default
  `dimension_order`, and its explicit note that `venue` is deliberately *not* a default dimension.
- `planning/domains/nodes/research.project-workspace.json` — the refused sibling, read to avoid
  duplicating its findings and to second its `file_kind_owner` question rather than restate it.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, checked programmatically against every
  `file_examples.source_type` and every member of `file_kinds.source_types`.
- `planning/01-product-design-structured.md` — only grepped for `venue|conference|poster|abstract`
  to confirm it adds nothing this domain needs beyond `00`'s own sentences. It does not; `00` was
  used throughout.

Not consulted: `planning/deferred-catalogues/`. This node's recognition needs an organisation
gazetteer that would carry conference and society names, but that is R4's content and naming its
members here would be inventing gazetteer contents. The node says "R4's orgs gazetteer content"
and stops.

## Why this row survives the node test

The test has three limbs and this row passes on two, which is stated as two rather than dressed up
as three.

1. **Detection signals — genuinely different.** The research schema row's `venue` signal is
   journal-shaped (a gazetteer hit in a cover-letter salutation or an editorial email subject) and
   its `stage` signal is the manuscript lifecycle. This situation's signals are meeting-shaped:
   a submission or abstract id beside a presentation-format word, a session or track code, a
   presenting-author line, a poster board number, a conference-management sender domain, a title
   slide carrying a venue token beside the project. `ASCB 2026 abstract submission A-2431
   received.eml` fires every signal on this row and none on the schema row. That is what makes the
   set this row's own.
2. **Dimensions — genuinely different.** `research.json`'s default is
   `[project, stage, artifact_type]` and its own `template.why` says venue belongs to a separate
   venue-scoped row. This row recommends `[venue, project, artifact_type]`. Two changes, both
   argued: venue promoted to the head, stage dropped because inside an accepted meeting bundle it
   collapses to a single value and `00` tells the canvas to "warn when a level produces only one
   child".
3. **Privacy — weak, and recorded as weak.** The real delta is exclusionary: a badge, a registration
   record and a book of abstracts (bulk personal data about other people) sit in the neighbourhood
   and must be kept out rather than filed in. No new handling class; none is P7's to give away here.

The sharper privacy rules on this schema live on `research.ethics-compliance` (participants) and
`research.manuscript-publication` (pre-publication material), and this node does not reach for them.

## Files considered and rejected

Fourteen made the JSON. These did not, with the reason:

- **`ASCB2026_certificate_of_presentation.pdf`** — real, but it is the `Independent Records`
  fallthrough shape and adds nothing the fallthrough entry does not already say. Named in
  `falls_through_to` instead of padding the fixture list.
- **`poster_tube_shipping_label.pdf`** — a genuine artefact of poster travel and genuinely not this
  domain; it is a transactional record already covered by the Hilton reservation fixture, whose
  discriminator is identical and stated once.
- **`ASCB2026_badge.pdf`** — carries the holder's name, affiliation and a QR code. Rejected as a
  fixture because its only teaching point is a privacy one already carried in `sensitivity_why`,
  and adding it would have tempted a `people`-shaped fact this schema does not legitimise.
- **`abstract_template_ASCB.docx`** (the conference's own blank submission template) — an empty
  form carrying the venue in its header and nothing else. Tempting as a false positive, but it is
  the same lesson as the programme book (a venue token with no holder-side content) and the
  programme book is the stronger fixture because it is also the generic hub.
- **A conference proceedings paper the holder DID author.** Deliberately left out of
  `file_examples` and put into `collides_with` with `research.manuscript-publication` instead,
  because the honest answer for it is abstention, and a fixture asserting `facts_legal` for it
  would have made a seam look decided. `00`: "conflicting signals should lead to abstention rather
  than an invented classification".
- **A poster PDF exported from the `.ai` file.** It is a `version_family` member of a fixture
  already present; carrying both would have taught nothing new and would have invited a
  version-suffix-as-stage error the JSON already forbids twice.

## `proposed_fields` — none, and that is the finding

The venue-first order raised one real gap and this node refused to fill it with a field.

A conference has *occurrences*: `ASCB 2026` and `ASCB 2025` are two meetings of one venue, and a
folder level named `venue` must distinguish them. The Research schema has no destination-eligible
time field — `term` is academic's, `capture_year` is photos', `tax_year` is finance's — so under
the current canonical list the occurrence year has to live inside the **value** (`ASCB 2026`).
That works, and it makes venue values inconsistent with journal values, which carry no year.

The tempting move was to propose `conference_year` / `venue_edition`. That is exactly the failure
`_CONTRACT.md` rule 8 names in its closing sentence (do not invent fields to make the gate green,
wrapped across two lines there and so paraphrased rather than quoted) — and it is also the
574's mechanism (a private field per situation). So: **`proposed_fields: []`**, and the fork is
recorded in `open_question` for Joseph. It is his because it decides whether someone's real folders
read `ASCB 2026/` or `ASCB/2026/`.

`00` supplies the reasoning but not the fix: "A course code alone should not merge different
semesters; course packet identity should include a term when it is available." The logic transfers
to a venue occurrence; the remedy (a `term` field) does not, because `term` is another domain's key
and reusing it here would be the schema-tree smuggling CONNECTION §3 forbids.

## Neighbours considered that did NOT get an edge, and why

- **`research.dataset-analysis`** — a results figure appears in both a poster and an analysis
  deliverable. No edge: the confusion is about a *figure value* of `artifact_type`, not about
  evidence that would activate the wrong situation. A shared value is not a collision.
- **`research.thesis-dissertation`** — a defence deck is a presentation with slide titles and
  speaker notes. Genuinely close, and deliberately left out: a defence names a committee and a
  degree programme, not a venue and a submission id, so `academic.teaching` and
  `academic.coursework` already carry the presentation-source_type discriminator this row needs,
  and a third copy of it would be noise. Flagged here so R1c can add it if it disagrees.
- **`research.grants-funding`** — a travel-award application names the meeting. No edge: the award
  file's own structure is a proposal-and-budget one, which is the grants row's signal, and the
  venue string inside it is context. Same shape as the travel/receipt collisions, which are already
  authored.
- **`photos.screenshot-captures`** — the portal-confirmation screenshot is a real seam, but
  `Screenshot 2026-01-14 at 22.03.11.png` is handled by `falls_through_to: Temporary Screenshots`
  plus the `never_alone` EXIF rule, and `photos.camera-events` already carries the image-side
  collision with the sharper fixture (the HEIC with camera EXIF). One image collision, not two.
- **`code.notebooks-experiments`** — no. A conference deliverable that is a notebook is the
  `research`/`code` seam, which the research SCHEMA row already carries; a template row restating
  it would duplicate an edge that lives one level up.
- **`academic` / `career` as schemas** (the roster's `must_consider_neighbors`) — considered and
  routed to their template rows instead. CONNECTION §5 restricts `collides_with` to same-kind
  pairs, so a template may not collide with a schema; the two schema neighbours the roster asked
  about are reached through `academic.teaching`, `academic.coursework` and `career.recruiting`,
  which is where the discriminating evidence actually lives. This is a case where CONNECTION is
  stricter than the dispatch prompt's edge table ("collides_with … Mutex" without the kind
  restriction) and CONNECTION wins, per its own closing rule.
- **`also_holds_with`** — left empty for the same reason: CONNECTION §5 says it joins schemas only,
  while the dispatch prompt's table describes it as "One file may legally carry both schemas".
  CONNECTION wins. The co-activations are on `research.json` already; the one this row contributes
  (the job talk) is recorded as `also_schema: "career"` on a fixture, not as an edge.

## Where the roster's hint was narrowed

The hint reads "registration and travel context nearby." This node reads *nearby* strictly: the
registration receipt, the hotel booking and the flight confirmation are **not** members of this
template. They are transactional records, `00` names them under Receipts and Confirmations, and
two `collides_with` edges plus a `never_alone` entry keep them out. Absorbing them would be the
`Travel/Flight Gate B12` move `00` forbids by name. The template still points at them via
`falls_through_to`, which is how a nearby thing is expressed without claiming it.

## NEEDS-JOSEPH (this node only)

1. **The conference-occurrence fork.** Does a conference occurrence stay a *value* of `venue`
   (`ASCB 2026`), or does the Research schema owe a destination-eligible time field? Recorded, not
   resolved: proposing the field here would have been minting a key to make a dimension work.
   Consequence is visible in someone's real folders (`ASCB 2026/` vs `ASCB/2026/`).
2. **Venue-first vs project-first.** This row recommends `venue → project → artifact_type` because
   the roster frames the situation as venue-scoped and the bundle coheres by meeting. The counter
   is `00`'s own general rule — "For document and record domains, project, function, or subject
   usually comes before time because putting year first scatters related work across calendar
   folders" — and a meeting occurrence is quasi-temporal. For one project shown at five meetings,
   project-first is better. The JSON states the counter-case in `template.why` rather than hiding
   it; the user can reverse it on the canvas, but the *recommendation* is a real choice about
   someone's filing habits and Joseph may want the other one.
3. **`file_kind_owner` semantics** — seconding the finding `research.project-workspace` filed. The
   roster makes this row owner of `presentation`, yet a lab-meeting status deck, a taught lecture
   deck and a job talk are all presentations belonging elsewhere. This node treats ownership as a
   research-assignment claim and writes it into `never_alone` as evidence of nothing. If a reviewer
   reads it as exclusivity, those decks are mis-shelved. R1c's to settle; recorded because two
   nodes on this schema have now hit it.
4. **`role_split` gap.** `venue` and `school` are the same entity type in different roles whenever a
   meeting is hosted on a campus, and both canonical rows carry an empty `role_split_with`. The
   split is authored on this node; widening `canonical_fields.json` is R1c's or Joseph's, never a
   node's.
