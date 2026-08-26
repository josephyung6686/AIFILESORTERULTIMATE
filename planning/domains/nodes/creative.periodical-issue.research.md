# creative.periodical-issue — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.periodical-issue.json`](creative.periodical-issue.json).
Salvage: none — no prior draft of either file existed.
Verdict: **node kept**, `refuse_node: false`, on all three legs of the node test. `fields: []`,
`proposed_fields: []`, `role_split: []` — nothing was minted to keep the row.

## Sources actually used

- The stamped assignment (`make_prompt.py creative.periodical-issue`) and
  `planning/domains/dispatch/RESEARCH-BRIEF.md` — the node test, the output shape, and the six
  depth requirements this memo is structured against.
- `planning/00-database-agent-product-design.md` — authoritative, reached by targeted `grep` for
  the spans quoted, never streamed. Every quoted span was re-matched mechanically (audit below).
- `planning/domains/nodes/creative.json` — **the schema anchor and the DEFAULT TEMPLATE this row
  is measured against.** Read in full: its `template.why` holds the default order as prose, its
  `recognition.deterministic` the five default signals, its `sensitivity_why` the four default
  privacy reasons. The three legs below are differenced against exactly those.
- `planning/domains/roster.json` — confirmed the id, `kind`, `schema_id`, and every edge endpoint.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration named by the
  brief, read once.
- `creative.content-marketing.json` and `creative.print-production.json` — read compactly
  (one_line, `template`, edge lists) as the two landed siblings that compete hardest here, so the
  boundaries below are stated against what they actually claim.
- `grep -rl "creative.periodical-issue" planning/domains/nodes/` — **returned nothing.** No landed
  row has argued a boundary against this id, which is why several reciprocals below are
  recommendations to R1c rather than alignments.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength before anything was written, because on first reading it is a good case.

1. **It is a cadence, not a filing world.** "Issue" is a *date bucket*. Strip the label and every
   file has a better home: the articles are `creative.short-form-writing` or
   `creative.journalism-reporting`, the layouts are `creative.graphic-design-project`, the press
   files are `creative.print-production`, the schedule is `creative.content-marketing`. A row
   whose whole identity is "dated container" is a time dimension wearing a node's clothes — and
   00 reserves time-primacy for capture-based media, so a row that leans on datedness is leaning
   on the one thing it is not entitled to.
2. **"Magazine / journal / newspaper" is a medium name.** The anchor already ruled that the
   media-form vocabulary is VALUES of `artifact_type`. Periodical could be a value.
3. **It duplicates `creative.content-marketing`.** That row's landed `one_line` claims "a
   CONTINUING PROGRAMME with a calendar rather than one finished piece" and "a forward-dated
   editorial calendar whose rows are pieces that do not yet exist." That is, on its face, this
   row's definition.
4. **It duplicates `creative.publishing-title`.** A publisher moving text through typesetting to
   printed pages is a journal issue exactly.
5. **Its evidence is never-alone.** A masthead is an organisation name; a volume number is a bare
   number; `.indd` is an extension. 00 forbids each as sole proof.
6. **It is defined by an ABSENCE** — "many *independent* pieces", i.e. content-incoherence. A row
   whose definition is "these files have nothing in common" is describing the residual library.

### Defeating it

Points 2, 5 and 6 are conceded and absorbed rather than argued away. The medium name went into
`work_types` and nowhere else; the never-alone material became eight `never_alone` rules, five of
which name the tempting false file that trips them; and the content-incoherence was reframed
correctly — the pieces are not merely incoherent, they are **allocated**, which is the opposite
of unrelated.

Points 1, 3 and 4 are defeated by three objects the case did not account for.

- **The flatplan / folio map / pagination grid** — a real, named, ordinary document type: a grid
  whose cells are page positions across a bounded total, each assigned to a piece, an
  advertisement or house material, with a per-position status, existing *before most of its
  contents do*. That is a slot budget, not a calendar. Content-marketing's calendar allocates
  **dates** on an open-ended schedule; print-production's imposition sheet allocates
  **already-finished pages** to press signatures. Neither is a bounded page budget, and neither
  row claims one.
- **The `.indb` book file / multi-document master** — the file format of "many pieces assembled
  into one container": a document naming member documents it does not contain, imposing continuous
  pagination across them. 00 requires the extractor to yield the pointing half of this shape —
  "linked asset names" — for creative formats; the anchor generalises it to placed media, and this
  variant sits one level up, at the document-set level.
- **Third-party supplied advertisement material** — the finding that kills point 1 outright. An
  instalment folder holds finished, press-ready files the maker did not author, cannot edit, and
  did not commission, occupying page positions of their own, with a trafficking record beside
  them. `creative.stock-asset-library` holds bought material, but bought material is used *inside*
  a work; this material *is* a page.

Against point 4 specifically: a title is finished once and has no successor, no page budget shared
with advertisements, and no volume-and-number series. Recurrence across *adjacent folders* is the
discriminator, and it is written into the deterministic signal rather than asserted.

The row survives. Had the flatplan and the supplied-advertisement structure not been real, the
correct outcome would have been refusal, and the row would have routed to `Reading Inbox` and
`creative.content-marketing`. That was a live possibility for the first half of this pass.

## The node test, argued in full

CONNECTION.md's test: a template exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The anchor's
default is held as prose in `creative.json`. This row differs on all three, which matters, because
one leg alone here would have been thin.

**Leg 1 — detection signals differ.** The anchor's five defaults are LINKED-ASSET, LAYER/ARTBOARD,
REVISION-ROUND, BRIEF, and DELIVERY/HANDOFF. This row's eight discriminators are the flatplan /
page-budget allocation, the book / multi-document master, a compound designator recurring across
*sibling folders*, third-party supplied material with a trafficking record, a many-contributor
one-deadline set, the peer-review packet keyed by a submission identifier, and the masthead /
colophon page. Only the second is a variant of an anchor default; the rest are new, and three of
them (flatplan, supplied material, peer-review) exist in no other creative sibling at all.

**Leg 2 — recommended dimensions differ, and the difference is a hole.** The anchor's default order
is `client → project → stage → artifact_type`. This world needs a level the default does not have:
the **instalment**. It is not `project` (the project is the title; collapsing them makes every
issue a separate work and loses the series), not `stage` (stage is progression toward acceptance;
a designator is a serial *position* that does not move), and not `artifact_type` (which names the
document, not the container). This is a genuine, argued difference from the default — and it is
also the row's honest gap, recorded as **NJ-PERIODICAL-1** with three alternatives. `time_first`
is `false` and the argument is written out, because this is the creative row most likely to claim
time-primacy wrongly: press dates slip, numbers do not, and No 3 files beside No 2 regardless of
when it went to press.

**Leg 3 — privacy rules differ in kind.** The anchor's four reasons are unpublished work, releases
carrying third-party identity, source material, and the client's confidence. Two here are not on
that list. (a) **Peer-review anonymity is a structural confidentiality, not a disclosure risk** —
the protected thing is the *link* between a person and a document, the harm is de-anonymisation,
and it generates a rule unique in the family: a document-properties author slot that contradicts
a stripped author block is something to protect, never something to extract. (b) **Third-party
material the maker cannot consent for** — an advertiser's unreleased creative sits inside the
publication's folder under an embargo the publication did not set and cannot waive. The anchor's
client-confidence reason covers the commissioner's secret; this is a party with no relationship
to the maker's filing agent at all. This leg also earns the row a residual the anchor does not
route to: `Protected Records`.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence.

- **A single downloaded article PDF** — kept, as **the collision fixture** (below), not as
  positive evidence.
- **A newsletter send (`Issue 47 - The Thursday Note.eml`)** — kept as the **second** collision
  fixture. Numbered, dated, recurring, and not this row: the number is a send counter, there is
  no page budget, no second contributor and no supplied material. It is
  `creative.content-marketing`'s, on its slug-and-canonical-address evidence.
- **The masthead master / grid template (`Masthead_2026_master.indt`)** — rejected. It sits in
  every instalment folder and is tempting for exactly that reason, but it is the *invariant across
  instalments*, not the instalment's own material. It belongs to `creative.brand-identity`.
  Recognising it matters anyway, which is why "the invariant title-level material shared by every
  instalment" is a `grouping_reason` — so it is grouped *away* from the per-issue folders rather
  than copied into each one.
- **The imposition sheet, plate set and proof-approval chain** — rejected to
  `creative.print-production`, which already claims the "proof→press→run→delivery evidence" in its
  landed `one_line`. This row stops at assembly.
- **A contributor's invoice or a kill-fee record** — rejected to finance. It is in the folder; it
  is a payment record, and claiming it would give one evidence item a third home.
- **A subscriber list or circulation report** — rejected to `business_operations`, and noted as a
  privacy hazard rather than a holding: a list of named subscribers is not creative material and
  must not be drawn into a creative folder's handling.
- **A calendar entry for the issue close (`Issue 215 close.ics`)** — rejected as a file example. A
  bare `.ics` carrying an issue number is `never_alone` in its purest form; it is a deadline, and
  the schema's default already covers scheduling. It stays in `file_kinds.extensions` only.
- **A whitepaper or trade article about publishing** — rejected. Reading material about the
  activity is not the activity; `Reading Inbox`.
- **The web CMS export of the same articles** — rejected as a file example and converted into the
  `creative.content-marketing` collision instead. Page-slot evidence is this row's; URL, slug and
  canonical-address evidence is theirs. The same article can carry both, but the *file* carries
  one or the other.

## The collision fixture

**`Sandoval_2026_JChemMat_v18_p221-229.pdf`** — a single article PDF downloaded for reading.

It carries publisher letterhead, a registered serial identifier, a DOI, a compound
volume-and-number token, a page range, and received/revised/accepted dates. It fires **every
surface signal this row has** and it is not this row's evidence.

What discriminates it: **it was received, not assembled.** No flatplan, no sibling piece from the
same instalment anywhere on the disk, no working file, no submission identifier, no supplied
material — and it arrived inside a bounded download session with four unrelated papers. Two of
00's own prohibitions do the work: a session "should never be treated as proof of topic," and a
publisher's name alone cannot create a group, on the same reasoning as the university-name rule.

Its correct home is `Reading Inbox` — "papers, articles, reports, and saved PDFs that appear to be
reading material but have no active research, course, or project association" — unless an active
project explains it, in which case it is `research`'s. It is marked
`group_without_copying_facts: true`, because a shelf of such downloads is a neighbourhood and
never an activation.

The generalised form of this fixture is the row's most common false positive and is stated as a
`needs_llm` item: a folder of twelve issue PDFs someone **collected** is indistinguishable by
filename from a folder of twelve issues someone **made**. The discriminator is the presence of
pre-publication states.

## Reciprocal boundaries

Ten collisions and three co-holdings are in the JSON, each stated in both directions. The four
that carry the same fixture on both sides:

| Fixture | This row reads it as | The neighbour reads it as |
|---|---|---|
| `Vol47_No3_press_PDFX1a.pdf` | the instalment's final assembled state | `creative.print-production`: the file handed to the press |
| `Okonjo_feature_DRAFT3.docx` | a piece occupying a position, when the instalment neighbourhood exists | `creative.short-form-writing`: the writer's own copy of their piece |
| `Issue 47 - The Thursday Note.eml` | abstention — no page budget | `creative.content-marketing`: a programme send |
| an `.indb` book file | an instalment master, when a designator recurs across adjacent folders | `creative.publishing-title`: a title master, when the folder has no successor |

The reciprocals owed from the other side that **could not be written**, because those nodes have
not landed and this row may not touch another agent's file. These are **recommendations to R1c**:

- `creative.publishing-title` should carry: recurrence, a shared page budget with advertisements,
  and a volume-and-number series mean the material is an instalment, not a title.
- `creative.journalism-reporting` should carry: the reporting apparatus — notes, recordings,
  contact material, source-protection posture — never follows a story into an instalment folder's
  filing merely because the story ran there.
- `creative.content-marketing` should carry: a bounded page budget with third-party supplied
  material occupying positions in it is never a content-marketing programme, however regular the
  cadence. (That row's landed edge list names `creative.short-form-writing` and
  `creative.creative-brief` but not this id — the seam is currently one-directional.)
- `creative.print-production` should carry: the flatplan is not a press document; it allocates
  slots before any artwork exists.

## Neighbours considered that did **not** get an edge

- **`creative.deliverable-handoff`** — rejected. An instalment is not handed to a client; it is
  published. The handoff shape (a stem across format and size variants for a recipient) does not
  occur here, and the one file that does go to a recipient — the press file — is already the
  `creative.print-production` collision.
- **`creative.creative-brief`** — rejected. Commissioning letters to contributors are real, but a
  commissioning note is an assignment, not the purpose-coherent brief shape the anchor names, and
  adding the edge would give the same document three claimants.
- **`creative.exhibition`** — rejected. Superficially similar (many works, one dated container,
  a catalogue), but an exhibition's container is a *space* and its material is installation
  evidence. No shared discriminating evidence.
- **`career.employment-records`** — rejected. A staff editor's masthead credit is authorship, and
  authorship is not a destination.
- **`role_split` is empty, and that is the interesting refusal.** The split this material most
  wants is a **third** role: the *advertiser*, who buys a position inside the maker's own work
  rather than commissioning it. The anchor already splits `client` from `our_firm` and this row
  does not re-declare it; there is no third key, and minting one to solve a single template's
  problem on a schema that declares no fields at all is exactly the move the brief warns against.
  The refusal is written into the supplied-advertisement fixture's `must_not_conclude` instead,
  and raised as open question (2).

## `proposed_fields` — empty, deliberately

`fields` is empty because a template references its schema's fields and never copies them, and
because this schema declares none. `proposed_fields` is empty for a harder reason: the key this
row genuinely needs — an instalment or serial-position key — is the point of maximum temptation,
and the anchor sets the precedent by refusing to mint one for the family's rights-and-licence
hole under identical pressure. Proposing a key on a field-less schema would also pre-empt
NJ-R1a-1, which the anchor deliberately left open. The gap is stated as NJ-PERIODICAL-1 with
three costed alternatives instead.

`proposed_context_terms` (fourteen) are candidates for R6 and are marked PROPOSED. 00 states the
pattern-plus-context *shape* for course codes only; it does not list these, and the JSON does not
pretend it does.

## Sparse-file discipline

Three fixtures carry `group_without_copying_facts: true`, each for a different reason:

- `Okonjo_feature_DRAFT3.docx` — the `HW 3.pdf` of this node. It sits among nineteen files carrying
  a 214 prefix and says nothing about which instalment it is for. The neighbourhood is a grouping
  reason; it is not an extraction licence, and no designator may be copied onto it.
- `Sandoval_2026_JChemMat_v18_p221-229.pdf` — a shelf of downloads is a neighbourhood and never an
  activation.
- `Issue214_contributor_uploads.zip` — the archive's designator may not be written onto its
  members. A manifest is evidence of *enclosure*, not of authorship or assignment.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All **25** quoted spans of 25 characters or more were extracted mechanically from the JSON and
  matched against `00` under whitespace and curly-quote normalisation. **25/25 matched verbatim;
  0 failures.** No `00` quotation in this node is fabricated or paraphrased inside quote marks.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (12/12); every entry in
  `file_kinds.source_types` likewise (10/10).
- Every `collides_with.domain` (10), every `also_holds_with.domain` (3) and every `also_schema`
  (2) resolves to a `domain_id` in `roster.json` — 0 unresolved.
- Every `falls_through_to.residual_template` (5) and every `falls_through_if_inactive` (12) is one
  of 00's nine residual names — 0 invalid.
- Closed edge vocabulary only; no `related_to` invented. `fields`, `proposed_fields` and
  `role_split` are empty, each with its reason stated in the JSON or here.
- No threshold, score, statistic or file count anywhere; the digits present are inside fixture
  filenames, in signal counts, and in prose references.
- No handling class assigned; `sensitivity` is `potentially_sensitive` only, and
  `is_safety_domain` is not carried.
- Key set matches the landed creative siblings exactly (27 keys, compared against
  `creative.content-marketing.json`).
- **Only the two assigned files were written.** No roster, canonical-fields, `check.py`, `src/`,
  SPEC or neighbour-node edit.

## NEEDS-JOSEPH (this node only)

- **NJ-PERIODICAL-1 — the instalment has no key, and it is this row's defining level.** Even under
  option (b) of NJ-R1a-1, none of `project`, `stage`, `artifact_type`, `client` can carry a
  volume-and-number designator (reasoning in the JSON's `template.why` and `open_question`).
  Alternatives: (a) leave it unexpressed — what the row does today; a periodical corpus groups by
  instalment but can never branch on it, which costs the row the one folder level its material
  most obviously wants. (b) Mint an instalment / serial-position key on the shared vocabulary —
  the honest fit, but a field-table decision one template row must not make, and it immediately
  raises whether the level may nest under a title level. (c) Treat the designator as a value inside
  `artifact_type` — cheap, and wrong in the 574's way: a container identity inside a document-type
  vocabulary. **No field was proposed.** Recorded for R1c.
- **NJ-PERIODICAL-2 — the advertiser is a third role and there is no key for it.** Reading an
  advertiser name into `client` would make the publication appear to be working for its own
  advertisers. Confirm that the anchor's two-role `client` / `our_firm` split is sufficient and
  the advertiser stays unmodelled, or open the question at schema level. No key proposed.
- **NJ-PERIODICAL-3 — the produced-versus-collected seam has a middle this row cannot settle.**
  An archivist keeping a complete curated run of a publication they do not make — a zine
  collector, a librarian, a researcher with a full journal run — has folders that are numbered,
  dated and serially complete, with no working files *by design*. `Reading Inbox` is a poor home
  for a curated permanent collection, and this row is the wrong home for material its owner never
  made. Alternatives: a user-defined residual, which 00 explicitly supports, or a separate
  collecting row that is not this row's business to propose.
