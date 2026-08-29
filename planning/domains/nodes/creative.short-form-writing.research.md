# creative.short-form-writing — lab notes (R1b)

Depth: J-DEPTH
Date: 2026-08-26
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.short-form-writing.json`](creative.short-form-writing.json).
Salvage: none. No prior JSON or memo existed for this id; both files are new.
Verdict: **node kept**, but under a researched name that is not the roster label, and only after the
charge below came very close to killing it.

## Sources actually used

- `RESEARCH-BRIEF.md` and the stamped assignment from `make_prompt.py creative.short-form-writing`.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n` only,
  never streamed. Every phrase inside quote marks in the JSON was re-matched against it (audit
  below).
- `planning/domains/nodes/creative.json` — **the schema anchor and the default template I am
  measured against.** Read its `recognition`, `template.why`, `sensitivity_why`, `work_types`,
  `file_kinds`, `also_holds_with` and `falls_through_to` programmatically rather than in full. Its
  `.research.md` was **not** opened: the JSON settled the node test without ambiguity, because the
  anchor states the default order and the two named time-first exceptions outright.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the one landed launch row read for
  depth calibration, per the brief.
- Neighbour rows that had already argued a boundary against me, found with one
  `grep -rl "creative.short-form-writing" planning/domains/nodes/` and read only at the matched
  lines: `creative.book-manuscript.json` and `creative.content-marketing.json` / `.research.md`.
- `planning/domains/roster.json` — every edge endpoint confirmed;
  `applications.graduate-professional` and `code.pkm-vault` were looked up specifically because I
  needed them and they are not in `must_consider_neighbors`.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, checked mechanically.

## THE CHARGE — the strongest case that this row should not exist

I state it first because it nearly won, and because two of its seven limbs survive into the node as
permanent constraints.

**1. It is a LENGTH, and a length is a value.** "Short-form" names nothing but size. This is not my
invention: `creative.book-manuscript` opened its own collision entry against me with *"THE
LOAD-BEARING COLLISION AND THIS ROW'S OWN CHARGE, because 'book-length' names a LENGTH and a length
is a value, not a situation."* If book-manuscript's label is a length, mine is the reciprocal
length, and two rows that split a single world by word count are one row with a value pretending to
be a boundary.

**2. It is a bag of document types.** "Essays, short stories, poems, columns and criticism" is an
enum. The creative anchor already holds `manuscript draft` in its `work_types[]`, and the assignment
is explicit that work types are values, never nodes.

**3. It is a medium and a format.** Prose in `.docx` / `.md`. `00` treats the extension as a routing
signal, not a meaning, and a `SOURCE_TYPE` is not a node.

**4. It may be a duplicate of `creative.self-initiated-work`.** Many small works by one writer with
no commissioner is, on its face, exactly the self-initiated situation on the creative schema.

**5. It may be defined only by an ABSENCE** — no client, no brief, no production paperwork, no
linked assets. A row whose evidence is what is missing can never activate.

**6. Its submission trail may be `creative.submission-query`'s.** The roster hint leans on "each
with its own submission history", and a landed row already owns submission packets.

**7. It may be a duplicate of the creative default template.** If the recommendation collapses to
project → stage → artifact_type with the client level empty, that is the anchor's default verbatim
and the row is a relabelling.

### How the charge was defeated, and where it was conceded

Limbs 1, 2, 3 and 5 are **conceded and encoded as prohibitions**, not defeated. The row does not fire
on length (an explicit `never_alone`, written in both directions and reciprocating book-manuscript's
clause), does not fire on a genre word (`never_alone`), does not fire on prose-in-a-text-format
(`never_alone`), and does not fire on the absence of a brief (`never_alone`, and the reason the
`creative.self-initiated-work` collision entry exists at all).

Limbs 4, 6 and 7 are defeated by positive objects, and the defeat is what makes the node real. The
world contains **four artifacts that exist nowhere else in the creative family**:

- a **submissions ledger** — a labelled table whose rows are TITLES crossed with MARKETS, carrying a
  response vocabulary and dates, in which several title cells resolve to the stems of siblings that
  are unrelated to each other. Its shape is a one-to-many index over *other files in the corpus*.
  A shot list indexes parts of one production; an editorial calendar indexes pieces of one
  programme; an agency-tracking list indexes many markets for **one** work. Cardinality is the
  discriminator, and it is what kills limb 6: many works × many markets is not one work × many
  markets, and `creative.submission-query` cannot hold a ledger indexing works no single packet
  contains.
- a **cover letter to an editor** — salutation to an editorial role, a declared-length line, a
  third-person bio, a simultaneous-submission disclosure. Four slots, purpose-coherent and
  content-incoherent with what it encloses. This is `00`'s own shape: *"Purpose must be a
  first-class facet. Topic answers what a file is about, while purpose answers what the file was
  for."*
- a **contributor's proof** — a typeset PDF whose page numbering starts mid-sequence and whose
  contributor note names the holder among several. Mid-sequence pagination is a structural fact that
  says *the holder is a guest in someone else's object*, which no other creative sibling's material
  asserts.
- a **version family whose branches are destinations**, not stages: `Glass Houses - Ploughshares
  sub`, `Glass Houses - AGNI proof`, `Glass Houses (collected)`, across years.

Limb 7 is defeated in the next section, on the dimensions.

**The name, however, does not survive.** The node the evidence defends is *a many-works-one-byline
corpus tracked by submission*, and I named it that. NJ-SFW-1 asks R1c to settle the label.

## The node test, all three legs

CONNECTION's rule: a template row exists only where its detection signals, its recommended
dimensions, or its privacy rules differ from its schema's default. All three differ here, and the
first one differs almost totally.

### Leg 1 — detection signals

The creative anchor's deterministic signals are LINKED-ASSET, LAYER-or-ARTBOARD, REVISION-ROUND,
BRIEF, DELIVERY-or-HANDOFF, PRODUCTION-PAPERWORK, SCRIPT, and TIMELINE-and-MEDIA. **Not one of them
can fire on a prose corpus.** There are no linked assets, no layers, no artboards, no format-and-
size delivery matrix, no call sheets, no scene headings, no media folder for a project file to
reference. The one that grazes it — REVISION-ROUND — is explicitly the *structural* half that `00`
collects universally, and a version token alone is a `never_alone` here.

That is a stronger result than "differs": this row is not a refinement of the anchor's detection
surface, it is **the part of the creative world the default is blind to**. Its own six deterministic
structures (ledger, cover letter, contributor-in-issue, many-unrelated-stems, same-stem-across-
addressees, rights-and-fee satellite) share no evidence with the anchor's eight. Leg 1 passes on
disjointness, not on nuance.

### Leg 2 — recommended dimensions

The anchor's default, quoted from its own `template.why`: client only where the corpus genuinely
serves more than one client, then project, then stage, then `artifact_type`. My recommendation
differs in three places, and each difference is evidential rather than aesthetic.

- **No client level, ever — and not merely "usually absent".** An outlet is not a commissioner. The
  relationship runs the other way: the piece is offered and may be refused, and the *same* piece has
  many outlets in sequence. A client level here is either empty or duplicates one work across
  folders. `00`'s parent-context rule is what settles it — *"a parent dimension should provide the
  context required to understand the child"* — and a destination that **rejected** the piece
  explains nothing about it.
- **No stage level.** The default's `stage` is monotonic: a work passes through concept, draft,
  review, final, delivered once. The state that matters here **repeats per destination**, so a stage
  level collapses one piece's AGNI rejection and its Ploughshares acceptance into a single folder
  called "submitted". The recommendation is the piece, then `artifact_type`.
- **A flattening rule the default does not have.** Where the corpus is forty poems or a year of
  columns, a per-piece level yields forty folders holding one file each, which is not organisation.
  In that shape the recommendation flattens to `artifact_type` alone.

Two of four levels dropped plus a corpus-shape-dependent flattening rule is not the default
relabelled. Limb 7 of the charge fails.

`time_first: false`, and the temptation was real — columns and submissions are dated, and a naive
reading would file by year. The anchor grants time-first to two named siblings on `00`'s capture
exception, *"Photos and capture-based media are the major exception"*; this material is not
capture-based, so a date-first order here would be claiming the photos exception without the photos
evidence. `00`'s standing rule governs instead: *"For document and record domains, project,
function, or subject usually comes before time because putting year first scatters related work
across calendar folders"* — and scattering is precisely what year-first does to a piece that took
three years and four markets to place.

`dimension_order` is nonetheless `[]` **by contract**, because a dimension may only branch on a
field the entry's schema declares and the creative placeholder declares none. The recommendation is
prose in `template.why`, exactly as the anchor and `creative.content-marketing` do it.

### Leg 3 — privacy rules

The anchor's posture rests on four grounds: unpublished work, third-party identity in releases and
call sheets, source material, and client confidence. Two of those (releases, source material) do not
apply here at all — they are `creative.commissioned-shoot`'s and `creative.journalism-reporting`'s.
So the row is not simply "the anchor, again, weaker".

What differs is the **shape**, not the degree. Everywhere else in this family the sensitive object
is *separable*: a release form, a call sheet, a brief, a recording. A dossier can describe the work
and withhold the paperwork. Short-form nonfiction inverts that — a personal essay names living
family members, an illness, a divorce, an employer, and those names are in the **body text of the
primary artifact**. That changes what may enter a prompt: the excerpt limit bites on the work
itself, not on its satellites. `00`: *"It should not send full documents where a short heading or
OCR excerpt is enough to resolve the question."*

The second ground is one no sibling has: **a ledger of the holder's own refusals**, crossed with
named organisations. Its disclosure harm is reputational, and it has no reason ever to leave the
machine. `sensitivity: potentially_sensitive`. No handling class assigned; that is P7's.

## Files considered and REJECTED

A row that only lists what it holds has not been researched. These were all tempting and are all
out:

- **A `.md` note in an Obsidian vault** — kept, but as the **collision fixture**, not as evidence.
- **A curated clips folder** (`clips/best-of-2025/`) — a *showing*, not a *making*. It is
  `career.portfolio-work-samples`; claiming it would give one folder two making-side owners.
- **A downloaded article by another writer, with a masthead** — indistinguishable on the surface
  from a contributor copy. Routed to `Reading Inbox` and written into `falls_through_to` as this
  row's most dangerous false positive.
- **A seminar paper on a novel** — criticism by form, coursework by context. `academic.coursework`,
  and the collision entry states the boundary in both directions.
- **A reading list / TBR spreadsheet** — a labelled table of titles, which is *ledger-shaped* and is
  not a ledger: no market column, no response vocabulary, and its titles resolve to nothing in the
  corpus. This is why the ledger signal is specified as titles × markets × responses and not as "a
  spreadsheet of titles".
- **A writing-group critique thread (`.eml`)** — the addressee is a peer, not an editor, and no
  submission exists. Grouping material at best.
- **A word-count log or a NaNoWriMo tracker** — rejected precisely because it counts words, which
  this row has forsworn as evidence in both directions.
- **A published book of collected essays (`.epub`)** — `creative.publishing-title`'s and
  `creative.book-manuscript`'s object; the *pieces inside it* are mine, the volume is not.
- **A pitch deck for a podcast about essays** — tempting only because the word "essay" appears in
  it, which is the `never_alone` this row leans on hardest.

Twelve fixtures were kept, deliberately weighted toward the ugly cases: a labelled table
(`Submissions.xlsx`), unlabelled prose (`aubade with power lines.docx`), an archive packet read by
manifest (`submission_packet.zip`), mail (`Re - Your submission to Ploughshares.eml`), an OCR of
material already in the corpus (`Scan 2026-03-02.jpg`), two collision fixtures, and the sparse file
that gets nothing.

## The collision fixture

**`Untitled.md`** — prose in markdown with YAML frontmatter carrying `tags: [essay, draft]` and
wikilinks in the body. It is this row's material *by content* and is emphatically not this row's
evidence.

What discriminates it is structural and lives outside the file: a `.obsidian/` configuration folder
at the tree root, a wikilink graph, and hundreds of same-format members. `00` licenses exactly that
test — *"Code-related files should rely heavily on local structural evidence, including repository
roots and package files, rather than forcing semantic analysis to infer a project from arbitrary
code text."* The file belongs to `code.pkm-vault`.

The reciprocal duty matters as much: this row must not harvest a vault by genre tags, **and** the
vault row must not swallow a written corpus that merely happens to be authored in markdown when a
ledger and cover letters are sitting beside it. Same bytes, and the discriminator is a sibling
directory neither row's content reading would ever see.

A second, softer collision fixture is `Personal Statement - Iowa MFA.docx`: untitled first-person
prose sitting in a directory with three short stories. It is `applications.graduate-professional`'s,
and the boundary is reciprocal — the packet must not absorb the stories, which predate it and carry
their own submission trails.

## Reciprocal boundaries — both directions, same fixture

Eleven `collides_with` entries, each naming one shared fixture and stating the claim on both sides.
Two were **authored against me first** and are adopted rather than renegotiated:

- **`creative.book-manuscript`** wrote the boundary on `Nightwork_ch03_draft.docx`: that row claims
  it when a compile container, a full-manuscript sibling of the same stem, or a resolved ordered run
  makes it a section of a continuous reading sequence; I claim it when it is complete in itself, has
  its own addressee, or belongs to a run of unrelated stems. Adopted verbatim in sense, including
  the mutual ban on word count, page count and file size. Where neither resolves, both abstain —
  `00`: *"Correct abstention is a successful outcome because the product's goal is reliable
  organization, not maximum file movement."*
- **`creative.content-marketing`** wrote the boundary on `Byline - essay on remote work -
  final.docx`: brand ownership of the destination supports that row; a personal byline, a submission
  to an outlet the holder does not own, an external editor's marks or a fee note supports mine.
  Adopted unchanged. Its memo records that it drafted my row's side first; I have not altered it. I
  add only the reciprocal duty it could not write for itself: a holder who runs a content programme
  *and* writes under their own byline holds both, and a shared employer token discriminates neither
  way.

Nine authored from this side, each stating the other row's claim as fairly as my own:
`creative.submission-query` (cardinality: one work × many markets vs many works × many markets),
`creative.periodical-issue` (the contributor's copy vs the assembled issue — same outlet name on
both sides, discriminating neither), `creative.journalism-reporting` (what the piece is made **of**,
not where it was sent), `code.pkm-vault`, `career.portfolio-work-samples` (making vs showing —
opposite directions of travel through the same bytes), `creative.self-initiated-work` (the
duplication charge, written as an edge because it is the likeliest reason to kill the row),
`creative.licensing-rights` (instrument vs satellite), `applications.graduate-professional`, and
`academic.coursework`.

**`also_holds_with`** — two, both on genuinely disjoint evidence:
`creative.translation-project` (a source text and a translator's rights note on one side; a ledger
row, a letter and a proof under the translator's byline on the other) and `creative.revision-round`
(an editor's marked-up return is both a state of this corpus and a real revision round).

**`role_split`** — one, and it is the interesting one. A magazine appears here as a **destination**
the holder offers work to and that may refuse it, and in `creative.periodical-issue` as a
**publisher** the holder assembles an issue for. It is not a field-key split, because the creative
placeholder declares no fields; it is recorded so that if the anchor's option (b) is ever taken, the
outlet is never quietly resolved into `client` on this side.

**Neighbours considered that got no edge:** `photos.*` — the assignment names `photos`, but the only
contact is a headshot in a submission packet and a scanned page, both of which are covered by
`One-Off Images` and by the OCR fixture's `must_not_conclude`; inventing a photos edge for a
headshot would give one file two owners for no gain. `code.*` beyond `pkm-vault` — a writer's
`.md` files touch `code.software-project` only through the extension, which is a `never_alone`.
`career.*` beyond `portfolio-work-samples` — a fee is not payroll and an outlet is not an employer;
that is stated in `must_not_conclude` on the email fixture rather than as an edge.
`research.reading-library` — genuinely tempting for the saved-articles case, but the correct
destination there is the `Reading Inbox` residual, not a second claimant.

## `proposed_fields`: empty, and what was rejected

`fields: []` because a template may not copy its schema's list, and the creative placeholder
declares none. `proposed_fields: []` deliberately. Four candidates were seriously considered:

- **`outlet` / `market`** — this row's most-used real axis, and still rejected. Minting it is a
  decision about the shared field table that one template must not make; folding it into the
  anchor's proposed `client` is wrong in kind, because a destination that refused the work is not a
  commissioner. It also fails the destination test on its own terms: one piece has many outlets in
  sequence, so a level would duplicate the work across folders. Recorded as NJ-SFW-2 instead.
- **`genre`** — a value of the anchor's proposed `artifact_type`. Minting it would be the
  one-concept-two-vocabularies failure `creative.content-marketing` correctly refused for `channel`.
- **`submission_status`** — a lifecycle stage, and worse, a *mutable* one. It is a value of the
  anchor's proposed `stage`, and the whole point of leg 2 is that this state is non-monotonic and
  cannot be a level.
- **`word_count`** — rejected twice over: it is a number, and it is the exact evidence both this row
  and `creative.book-manuscript` have forsworn.

`proposed_context_terms` carries ten candidates for R6, each flagged PROPOSED in the list's own
first element. `00` states the pattern-plus-context *shape* for course codes only and lists none of
these; the entry says so rather than implying design provenance.

## Sparse-file discipline

`aubade with power lines.docx` is this node's `HW 3.pdf`. One page of lineated text, no title, no
metadata beyond timestamps, one of forty stems that share nothing, and a ledger in the directory
naming eleven titles including this one. It is marked `group_without_copying_facts: true`, its
`facts_legal` is the universals only, and its `must_not_conclude` says outright that the ledger row
licenses nothing. `00`: *"The graph does not automatically copy those missing facts onto sparse
files."* Four of twelve fixtures carry the same flag — the ledger itself, the vault note, the
archive packet and the OCR scan — because in each case the neighbourhood is real and the fact
transfer is not.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All 22 quoted spans of twenty characters or more were extracted mechanically from the JSON and
  matched against `00` under whitespace and curly-quote normalization. **22 of 22 matched verbatim.
  No `00` quotation in this node is fabricated or paraphrased inside quote marks.**
- Every `file_examples.source_type` is in `SOURCE_TYPES` (12/12); every `file_kinds.source_types`
  member likewise.
- Every `collides_with.domain` (11), `also_holds_with.domain` (2) and `role_split.domain` (1)
  resolves to a `roster.json` id.
- Every `falls_through_to.residual_template` (4) and every `falls_through_if_inactive` (12) is one
  of `00`'s nine residual names.
- `fields: []`, `proposed_fields: []`, `dimension_order: []` — all three empty by contract, each
  with the reason stated in the file.
- No threshold, score, count of evidence or handling class appears. The digits present are inside
  fixture filenames and page numbers in observations.
- No file example writes a folder path as a fact; every one lists "a folder path" first in
  `must_not_conclude`.
- Only the two assigned files were written. `29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/` and every neighbour node are untouched.

## Recommendations to R1c (cross-row, not applied)

1. **Reciprocate the eleven collisions.** Nine were authored from this side and need the other half
   written into the neighbour rows, most urgently `creative.submission-query` (cardinality),
   `code.pkm-vault` (the `.obsidian/` discriminator) and `creative.self-initiated-work` (the
   absence-is-not-evidence rule, which protects both rows).
2. **Propagate the length ban.** `creative.book-manuscript` and this row now both forbid word count,
   page count and file size as evidence. `creative.screenplay` and `creative.periodical-issue` sit
   on the same frontier and should carry it too.
3. **Settle the label** — NJ-SFW-1.

## NEEDS-JOSEPH (this node only)

- **NJ-SFW-1 — the name is a length and the node is not.** The row landed as "Short-form writing"
  and its own charge is that a length is a value. The evidence defended a different node: a
  many-works-one-byline corpus tracked by submission, and the researched `name` says so.
  Alternatives: (a) adopt the researched name, and let the roster label become browse-only
  vocabulary; (b) keep the roster label, but record in **both** this row and
  `creative.book-manuscript` that the label is vocabulary only and that length is inadmissible
  evidence on either side. Doing neither leaves a standing invitation for a future pass to file by
  word count, which is the failure this row was one argument away from being.
- **NJ-SFW-2 — the outlet has no home in the vocabulary.** Stated in full in the JSON's
  `open_question`; three alternatives, this row's preference is (a) leave it a value, and
  `proposed_fields` is empty so that R1c decides rather than inherits.
- **NJ-SFW-3 — which row owns a piece that is both reported and essayistic.** A reported personal
  essay carries interview notes **and** a bio-and-cover-letter trail. This row's preference is that
  the presence of source material naming third parties routes the whole neighbourhood to
  `creative.journalism-reporting`, because that row's privacy posture is stricter and the safer
  error is to over-protect. Confirm, or invert.
