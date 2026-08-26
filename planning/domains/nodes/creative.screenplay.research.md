# creative.screenplay — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.screenplay.json`](creative.screenplay.json).
No prior draft existed; both files are new.

**Verdict: `refuse_node: true`.** The row is a document type whose recognition is already declared
twice on its own schema, and it has no leg of the node test left to stand on. The coverage routes
without loss to `creative.film-production`, `creative.theatre-production`,
`creative.podcast-episode`, `creative.book-manuscript`, and the Review Later / Independent Records /
Reading Inbox residuals. One real gap survives the refusal and is recorded as NJ-SCREENPLAY-2.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief; the six depth requirements this
  memo is audited against, and the ratified rule that a `launch: placeholder` row still gets
  full-depth research.
- `python3 planning/domains/dispatch/make_prompt.py creative.screenplay` — the stamped assignment.
  It supplied the row metadata, the node test, the output shape, the closed edge vocabulary and the
  done-when list. Its `one_line_hint` is itself the primary evidence for the refusal (below).
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n -F` only.
  Every span quoted in the JSON was grep-matched verbatim against this file before it was written;
  the audit is at the bottom of this memo.
- `planning/domains/nodes/creative.json` — the schema anchor and, per the brief, the DEFAULT TEMPLATE
  this row is measured against. Read in full. It is where the refusal was decided.
- `planning/domains/nodes/creative.film-production.json` — read at its recognition, work_types,
  file_kinds, template, file_examples and edges. This is the sibling that already holds the evidence.
- `planning/domains/nodes/creative.performing-practice.json` — read at its refusal reason and two
  fixtures. It is the precedent: a creative sibling refused for duplicating the schema default's
  script-grammar signal, in almost exactly the terms this row must use.
- `planning/domains/nodes/creative.book-manuscript.json` — read only at the lines that name this row
  (`grep -n -B3 -A6 screenplay`). It had already argued the boundary against me from its side.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration named by the
  brief. Read once. It supplied the memo shape, the `also_holds_with_note` / `role_split_note`
  idiom, and the `role_split` refusal pattern I reuse verbatim in form.
- `planning/domains/roster.json` — confirmed the row, and mechanically confirmed all six
  `collides_with` targets, the `also_schema: "academic"` value and the four residual names.

I did **not** read `01-product-design-structured.md`, `CONNECTION.md` or the other 39 creative
siblings. `00` wins over `01` by rule, and CONNECTION's node test is restated in full in the stamped
assignment I was given. Reading forty siblings to refuse one row would have been the wrong spend.

## THE CHARGE, taken first

I was asked to state the strongest case that this row should not exist before writing anything. That
case turned out to be four cases, and none of them could be defeated.

**1. It is a document type.** The roster's own hint says so in its first clause — *"the one document
type in this slice with a strictly machine-readable structure."* A document type is a value of
`artifact_type`, and the creative schema's `artifact_type` example enum already lists `script` among
"working file, export, proof, master, stem, cut, render, layout, script, transcript, release form,
brief". The schema anchor states the consequence for its 41 children in terms that name this row
without naming it: the whole media-form vocabulary "is VALUES of this one field, which is the single
most important thing this schema row can say to its 41 siblings: no sibling may ask for a node per
media form".

**2. It is an existing work-type value — twice.** `script` is a member of the creative schema's
`work_types`. `screenplay` is the **first** member of `creative.film-production`'s. The stamped
assignment's rule is flat: "Work types are values. `work_types[]` is an enum of values for a
`work_type` (or equivalent) field. Do not ask R1a for a child node per work type."

**3. It is a medium and a format.** "for screen or stage" is a medium; the hint's second clause —
"the one most often reduced to a flat PDF" — is a file format, and `00` requires the engine to
"treat the file extension as a routing signal rather than an assumption about meaning". `.fdx` feels
uniquely screenplay-specific and is not: it is equally a downloaded sample, a template, a course
handout, and a collaborator's file the holder never opened.

**4. It duplicates its own schema's default template.** This is the one that actually killed it, and
it is quotable from the anchor. The creative schema's eighth deterministic signal reads:

> a SCRIPT structure: the strict element grammar of a screenplay or stage script - scene headings,
> character cues centred above dialogue, transitions - which survives even a flat PDF export and is
> the most deterministic single fixture this family has.

The row's entire proposed contribution is a signal its schema already declares and already advertises
as its best one. A template exists only where it differs from that default. This one *is* that default.

## The node test, all three legs

**Leg 1 — detection signals. FAIL.** I tried to find one discriminator that was not already declared
and could not. Every candidate resolved into four buckets:

- the schema's own SCRIPT signal (element grammar surviving a flat PDF export);
- an extension (`.fdx`, `.fountain`, `.celtx`, `.highland`);
- a document-type word in a filename (`script`, `screenplay`, `draft`, `sides`, `teleplay`) — and
  `script` is the most polluted such token in the whole corpus, naming a shell script, a test script,
  a sales call script, a narration and a run-of-show, the first two of which are `code`'s;
- evidence that genuinely *is* discriminating and belongs to a sibling. The best of these is the
  **revision-colour page set** — white/blue/pink pages, A-pages, asterisked change bars, locked scene
  numbers. It is strictly formatted, machine-legible and specific. It is also *production* evidence:
  those marks exist only because a production is scheduling around a locked script, and
  `creative.film-production` already claims the preproduction packet under "A preproduction packet
  containing a labelled call sheet or shooting schedule".

Two templates on the **same schema** firing on the same bytes with no discriminator is the exact
failure the node test exists to prevent, and `creative.performing-practice` was already refused in
those words: "duplicating them here would make the same bytes activate two same-schema templates with
no discriminator."

**Leg 2 — dimensions. FAIL, and cannot be rescued.** The creative schema declares no field rows
(D1 as narrowed, `_CONTRACT` rules 10 and 15, CONNECTION PR-6), so `dimension_order` is empty here as
it is for all 41 siblings — identical to the default by construction. I checked whether adoption
would rescue it, because that is the only honest way to test this leg. It would not. Under option (b)
of NJ-R1a-1 the correct recommendation for this material is the schema default *unchanged*:
`project → stage → artifact_type`, with `screenplay` as an `artifact_type` value and `2nd Draft` as a
`stage` value. The alternative — a script-first or draft-first order — inverts `00`'s parent-context
rule, since "a parent dimension should provide the context required to understand the child" and a
draft number is meaningless without the work in exactly the way Homework 3 is meaningless without the
course. A `screenplay` level above `project` is also the one-child collector level `00`'s own
validator rejects ("create meaningless one-child levels") in the ordinary case of one writer with one
script in progress.

**Leg 3 — privacy. FAIL.** An unfilmed script under option is confidential, and that is *verbatim*
the creative schema's own first sensitivity reason: unpublished work, where the harm is disclosure
rather than identity theft and the client's confidence is not the maker's to give away. The distinct
third-party-identity posture this material sometimes gets credited with belongs to its neighbours:
cast and crew contact blocks are on call sheets (`creative.shoot-day-media`), signed personal details
are on release forms (`creative.film-production`, `identity`). A script page carries characters, not
people. `sensitivity: potentially_sensitive` is kept on the node so the refusal does not accidentally
downgrade anything, but it is the schema's posture, not a distinct rule.

## Files considered and rejected

Ten fixtures are on the node. These are the tempting false positives, and why each is not this row's
evidence:

- **`Harbour Lights - screenplay v5.fdx`** — the perfect happy case, and it is *already
  `creative.film-production`'s own fixture*, carried verbatim in its `file_examples`. Kept on my node
  precisely to show the duplication rather than to claim it.
- **`SALT FLATS - 3rd Draft (Blue Revision 04-11-2026).pdf`** — the flat PDF the hint leans on, with
  the most script-specific structure that exists. Rejected: revision colours and locked scene numbers
  are scheduling instruments, so the file is production-packet evidence.
- **`untitled_spec.fountain`** — the strongest case *for* the row: no production anywhere, so
  `film-production` will not fire. Rejected anyway, and this is the crux: the schema's SCRIPT signal
  already fires on these bytes and already licenses everything a screenplay template could license,
  which is recognition plus the universals. The template adds nothing, so it is not a node.
- **`Ophelia sides - Act 3.pdf`** — `creative.performing-practice`'s fixture, on a row already
  refused for this exact reason. A second refused claimant on the same bytes would be the same error
  twice.
- **`Ep 04 - The Quarry - script (RUN OF SHOW).docx`** — cue-and-speaker layout indistinguishable
  from a stage script. Rejected: the timing column, ad-break cues and session-plus-takes
  neighbourhood are `creative.podcast-episode`'s.
- **`SCWR-210_week3_scene-exercise_submitted.pdf`** — eight pages of correct grammar and no work at
  all. Rejected on `creative.film-production`'s own never_alone, which names this file: "screenplay
  structure can be a writing sample, classroom exercise, theatre script, or an unrelated draft." The
  only fixture carrying `also_schema` — `academic`, verified as a roster schema id.
- **`Scene 14 rewrite.docx`** — the sparse `HW 3.pdf` case: dialogue under two cues, no title, no
  version token, two folders from a production. `group_without_copying_facts: true`; the
  neighbourhood may group it, and nothing may be copied onto it.
- **`TheLastFerry_shooting_script_LOCKED.zip`** — the archive packet with mixed members, manifest
  read without extraction. Rejected: schedule, sides and breakdown make it a *production* packet.
- **`MidnightRiver_screenplay_adaptation_v2.fdx`** — the adaptation, sitting beside the manuscript.
  Kept as the reciprocal fixture with `creative.book-manuscript`, not as a claim.

Rejected from the corpus entirely, so they are not on the node:

- **a table read audio file / a self-tape audition video** — `audio_video` with no script structure at
  all; they are performance capture, and `photos.home-video` or Review Later handles them.
- **a treatment, logline sheet or pitch deck** — real, and already `creative.film-production`'s
  "treatment or pitch" work-type value. Adding them would have widened a document-type row into a
  development row it has no evidence for.
- **a subtitle `.srt` for a finished film** — a delivery artefact `film-production` already carries in
  its extensions; and where it is a *translated* subtitle track it is `creative.translation-project`'s
  parallel-structure evidence.
- **a screenwriting app's autosave / backup directory** — bulk machine state, not a record. Nothing
  here fires that the schema's version-family universal would not.
- **a Final Draft template file (`.fdxt`) or a downloaded formatting cheat-sheet** — stock/reference
  material with no work around it, which is `Reference Clips`' own sentence.

## The collision fixture

**`Hamlet.txt` (Project Gutenberg plain-text download).** This is the file that most looks like this
row's evidence and is not — and it is worse than that, because its element grammar is *more complete
and more regular* than any file the row would legitimately claim: a dramatis personae page, act and
scene headings, a character cue above every single speech, bracketed stage directions throughout.
A grammar-based detector would rank it top of the corpus.

What discriminates it is entirely outside the document: a distributor header and a licence trailer
bracketing the text; no same-stem siblings; no version-shaped token; no working container anywhere on
the disk; and a downloads folder holding thirty other single-file title-and-author texts acquired
across one afternoon. The holder is **reading** this, not making it. It routes to `Reading Inbox`,
and the correct outcome is that no creative row fires at all — "Correct abstention is a successful
outcome because the product’s goal is reliable organization, not maximum file movement".

This fixture is the single best argument for the refusal. If the most perfect instance of the row's
defining structure must not activate the row, the structure was never the situation.

## Reciprocal boundaries

Six `collides_with` edges, each naming the same fixture on both sides. All six targets verified
against `roster.json`.

| Neighbour | Shared fixture | Their side | My side (as refused) |
|---|---|---|---|
| `creative.film-production` | `Harbour Lights - screenplay v5.fdx` | the screenplay as one member of a production lifecycle; `.fdx`/`.fountain` in file_kinds, `screenplay` as first work_type | there is no third position — a lone `.fdx` is caught by the schema's SCRIPT signal plus Review Later |
| `creative.theatre-production` | `Ophelia sides - Act 3.pdf` | the staging record — rehearsal schedule, programme, venue and run | the row tried to buy both media with one id, which is what makes "screen or stage" a medium |
| `creative.book-manuscript` | `MidnightRiver_*` pair | the chapter run and the compile container | the adaptation routes to film-production or the schema; their edge to me needs re-pointing (NJ-1) |
| `creative.podcast-episode` | `Ep 04 … RUN OF SHOW.docx` | timing column, ad-break cues, session-plus-takes | layout is shared; episode structure is not |
| `career.portfolio-work-samples` | `Sample - first 10 pages.pdf` | curated finished exports ordered for showing, beside a resume | a working draft is not a portfolio because a writer wrote it |
| `code.software-project` | a `.fountain` in a git repo with a Makefile | the preserved repository root; internal layout preserved, not re-filed | no creative row may propose moving anything inside a preserved repository root |

`creative.film-production`'s reciprocal was the decisive one and it is already written on their side:
their never_alone bars "A script-like document with no production identity". That bar is real and
correct — and it is precisely the hole this row was invented to fill. The finding is that the hole is
already covered by the schema and a residual, not that it needs a row.

`also_holds_with: []` by contract — `_CONTRACT` rule 14 restricts it to schema rows, and the creative
schema already declares photos / legal / business_operations / career. The one genuine double reading
in my corpus (the course exercise) is stated as `also_schema: "academic"` on the fixture, which is
where a template may say it.

`role_split: []`. The split this material wants is **the writer** against **the optioning or
commissioning party**, both sitting in the same title-page and copyright-notice zone. The writer side
is authorship, which `00` bars from being a destination at all; the counterparty side is already the
schema's declared `client` / `our_firm` split. Minting a producer-side key to solve one refused
template's problem is the move that produced thousands of private field names in the overnight pass.

## Neighbours considered that did NOT get an edge

- **`creative.submission-query`** — a script sent to an agency is real, but the discriminating evidence
  is the *letter and the log*, not the script. No shared evidence item; adding the edge would have
  given one file three claimants.
- **`creative.translation-project`** — a subtitled or translated script is genuinely parallel-structured,
  and that structure is translation's whole subject. It never competes for the script itself.
- **`creative.revision-round`** — refused already, on the version-token evidence my never_alone bars.
  Edging a refused row to a refused row records nothing.
- **`creative.short-form-writing`** — a sketch or a monologue in script format. The seam is a length,
  and a length is a value; this is exactly the charge, so no edge.
- **`academic`** — carried on the course-exercise fixture as `also_schema`, which is the contract-legal
  place for it on a template row. No schema-level edge minted from here.

## proposed_fields

**Empty, deliberately.** `fields: []` by rule (placeholder row, not an anchor). The two keys this
material makes tempting were both refused:

- **a scene/scene-number key.** Machine-readable, stable across drafts, and useless as a fact: a scene
  number is a coordinate inside one document, not a property of the file, and it could never be a
  folder level without producing hundreds of one-child directories.
- **a draft-colour or draft-state key.** It would be a synonym for the schema's `stage` proposal with a
  vocabulary borrowed from one industry — one concept in two vocabularies, which is the 574's failure.

`proposed_context_terms: []`. The creative schema already carries `scene`, `storyboard`, `call sheet`
and `shot list`, and a refused row proposing terms would be asking R6 to build detection for a node
that does not exist.

## NEEDS-JOSEPH (this node only)

- **NJ-SCREENPLAY-1 — a landed neighbour already points at this refused row.**
  `creative.book-manuscript.json` carries a `collides_with` entry naming `creative.screenplay`. That
  edge now targets a refused node. Alternatives: (a) **re-point it** at `creative.film-production`
  (screen adaptation) and `creative.theatre-production` (stage) — this preserves the discriminator
  book-manuscript actually argued and loses nothing; (b) leave it as a documented dangling marker
  recording that the boundary was argued and the far side refused; (c) revive this row, which requires
  answering NJ-2 first. **Recommendation: (a).** *Not done here — editing a neighbour's node is outside
  this row's mandate. This is a RECOMMENDATION TO R1c and nothing more.*
- **NJ-SCREENPLAY-2 — the lone screenwriter has no row, and that is the one real cost of this
  refusal.** A working screenwriter with a dozen specs and no shoot, call sheet or camera media has a
  genuine filing world, and after this refusal no template owns it: `creative.film-production`'s first
  signal prefers a production neighbourhood, `creative.self-initiated-work` is refused, and
  `creative.book-manuscript` is prose. Three answers: (a) **accept the schema default** — the SCRIPT
  signal fires, the universals and the version family are legal, drafts land in Review Later; cost is
  that a professional writer's corpus is recognised and never structured (this is what the node
  recommends today); (b) **widen `creative.film-production`'s first deterministic signal** to drop the
  production-neighbourhood preference so development-stage material activates before anything is shot
  — cheap, edits one sibling, **recommended**; (c) **mint a different row anchored on development as a
  RELATIONSHIP** rather than on a document — option or shopping agreement, coverage and reader reports,
  a notes-to-draft cycle, a submission log — which *would* be a situation with its own detection
  signals and its own counterparty privacy posture, and is the only honest version of this id. It is
  not *this* id, because this id is named for a document type. **Recorded, not resolved; no such node
  is proposed here.**
- **NJ-SCREENPLAY-3 — which residual owns a lone script.** `creative.film-production` routes a
  standalone script to `Independent Records`; this node routes most fixtures to `Review Later`. Both
  are defensible and should not disagree silently. The distinction offered: a **single finished** script
  with no siblings has "a durable purpose but no broader group" — Independent Records' sentence
  exactly; a **same-stem draft run** is meaning partly understood with the location still undecided —
  Review Later's. Confirm, or collapse both to one.

## Audits run before returning

- `python3 -m json.tool` — parses; 29 top-level keys, matching the landed creative siblings plus the
  two house `*_note` keys borrowed from `finance.crypto-assets`.
- Every `00` span quoted in the JSON was grep-matched with `grep -c -F` against
  `planning/00-database-agent-product-design.md` before writing. Eleven spans checked, eleven matched
  verbatim (count 1 each), including the curly apostrophe in "the product’s goal". **No `00`
  quotation in this node is fabricated or paraphrased inside quote marks.** Spans attributed to
  `creative.json`, `creative.film-production.json` and `creative.performing-practice.json` are quoted
  from those files, are labelled as such in prose, and are not attributed to `00`.
- All six `collides_with.domain` values resolve to `roster.json` `domain_id`s (6/6).
- All four `falls_through_to.residual_template` values are among `00` §7.3's nine names (4/4); all ten
  `falls_through_if_inactive` values likewise.
- Every `file_examples.source_type` is in the fourteen-member `SOURCE_TYPES` list (10/10); every
  `file_kinds.source_types` member likewise (7/7).
- `also_schema: "academic"` resolves to a roster schema id.
- `fields`, `proposed_fields`, `work_types`, `proposed_context_terms`, `also_holds_with`,
  `role_split` and `template.dimension_order` are all empty, each with a stated reason.
- Four `file_examples` carry `group_without_copying_facts: true`; every one of the ten has "a folder
  path" in `must_not_conclude`.
- No number in the file is a threshold, score or evidence count — the digits present are filenames,
  dates inside fixture names and prose references. No handling class is assigned.
- Only the two assigned files were written. No neighbour node, roster entry, canonical field, `src/`
  file or SPEC was touched.
