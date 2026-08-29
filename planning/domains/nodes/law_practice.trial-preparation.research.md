# Research memo — `law_practice.trial-preparation`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/law_practice.trial-preparation.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`
Absorbs the legacy row `law.jury-materials`

## Result

**Accept, narrowly, and record the rename I would rather have.** The node survives its own strongest
attack only by claiming much less than its name: it holds artefacts **whose own structure is an
enumeration over other documents or over events in an imposed order**, anchored to **one identified
tribunal listing**. It does not hold everything a practice makes before a trial.

Three things make it a real row rather than a stage label: (1) its characteristic files **fail the
schema's own second precondition leg** — a bundle index, a chronology and a running order have no
practitioner/client role pair, no execution block and no addressee, so the schema default cannot
activate on them; (2) the enumerating-plus-listing structure is a **different activation path**, not
a filename filter; (3) it carries a privacy claim no sibling can make — **a compilation defeats
member-level protection**, because every protection this product offers is applied to files and a
bundle converts protected files into pages.

If R1c disagrees on any of it, the honest outcome is a **rename to `compilation-and-bundle`**, not a
padded defence of the word "trial". That is NJ-TP-1 and I would welcome it.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full); stamped assignment via `make_prompt.py`.
- `planning/00-database-agent-product-design.md` — reached by targeted grep, per the token
  instruction. Every span quoted in the JSON was grep-verified verbatim before it was written; the
  verification run is recorded at the end of this memo.
- `planning/domains/nodes/law_practice.json` — the schema anchor: its `recognition`, `template.why`,
  `work_types`, `sensitivity_why`, `falls_through_to`, `proposed_fields`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the one landed launch row read
  for depth calibration, plus its JSON for the client/matter-label span.
- Landed siblings, read only where they already argued a boundary against this id, found with one
  grep: `law_practice.evidence-exhibits`, `.depositions-testimony`, `.hearing-transcripts`,
  `.pleadings`, `.discovery`, `.appeals`.
- `planning/domains/canonical_fields.json` (key list only), `planning/domains/roster.json` (id
  existence check for every edge target).

## THE CHARGE — the strongest case that this row should not exist

I put six attacks to the row before writing a line of it. Two of them nearly landed.

**Attack 1 — it is a lifecycle stage, and stages are values of `stage`.** This is the strongest one.
"Trial preparation" names a phase of a matter exactly as "pre-trial", "discovery" and "appeal" do.
`stage` is a canonical key. A row whose content is "the phase between close of pleadings and the
first day" is a `work_type`/`stage` value wearing a node's clothes, and the 574's recorded failure
was minting nodes for values.

*Defeated, but only by shrinking the row.* The row does **not** claim material by when it was made.
A pleading drafted the week before trial is still a pleading; a deposition taken for trial is still a
deposition; an exhibit marked for trial is still an exhibit. The siblings' own landed edges already
say so, in their words, and I adopted rather than renegotiated them. What is left after those
concessions is not a period of time — it is an **artefact class with a structure no sibling
produces**: a table whose rows *are other documents* (index), or *are events with source references*
(chronology), or *are positions in a sequence* (running order, numbered instruction set). Pleadings
produce captioned prose. Transcripts produce Q&A pages with page-and-line coordinates. Discovery
produces review logs keyed to a reviewer decision. Exhibits produce a designator schedule. None of
them produces an ordering over members. The test is structural, not temporal, and that is what makes
it a node. I record the residual risk as NJ-TP-1 rather than smoothing it.

**Attack 2 — it is a bag of document types.** "Bundle, chronology, skeleton, running order, jury
instructions" is a list of document-type words, and document-type words are `work_types`.

*Defeated by the deletion test.* Delete every one of those words from every fixture — bundle, trial,
hearing, index, chronology, brief, jury — and what survives on the anchor fixture is: a table of
member descriptions with tab numbers and a page range that is *continuous across the compilation
rather than internal to any member*, under a header stating one part of a declared total, plus a
listing anchor. That structure survives the deletion; the words do not, and they are all in
`never_alone` precisely because they are the material of this attack.

**Attack 3 — it is a medium or a length.** A trial bundle is "a big paginated PDF". Format is not a
world.

*Defeated, and this attack produced the row's second never-alone.* Continuous pagination, tab
markers, separator sheets and a long page count are shared by a scanned textbook, an appellate
record, a closing binder and a printed policy manual. I built the collision fixture set around
exactly this: `Table of Cases and Index - Civil Procedure (2026 ed).pdf` has an index *and*
continuous pagination and is Reading Inbox. Pagination is never a leg.

**Attack 4 — it duplicates `law_practice.evidence-exhibits`.** Both hold paginated compilations with
indexes, and that neighbour's own open question says so.

*Defeated on the ordering key, and I accept the neighbour's merge direction as insurance.* The
neighbour's key is a **designator namespace over tendered items**, and its schedule survives the
hearing. Mine is a **tab plus a continuous compilation page** over the whole case including material
that will never be tendered — pleadings, statements, correspondence, authorities. The neighbour named
the shared fixture (`Bundle index - Hartley v Nash - vol 2.pdf`), gave it to this row, and said the
reciprocal was owed; the reciprocal is now written with the same fixture named on both sides. I do
not think a merge is needed, because the two rows protect different things: the neighbour protects a
re-identification layer, this row protects an aggregation.

**Attack 5 — it duplicates the schema default.** The schema already covers "matter apparatus".

*Defeated on the default's own text, and this is the cleanest leg.* The `law_practice` default
requires **both** an exact matter reference repeated across artefacts **and** an artefact whose
labelled slots separate a practitioner-or-firm role from a client role. This row's characteristic
files satisfy the first and **fail the second by construction** — internal work product has no party
pair. If the row did not exist, the schema's own precondition would refuse to fire on a bundle index,
a chronology and a witness order, and they would go to Protected Records unrecognised. The row exists
to supply the missing second leg with a different one.

**Attack 6 — it is defined by an absence.** "The working material that is not a filed document."

*Conceded as a real danger and designed against.* An absence-defined row cannot activate, which is
the brief's own rule. Every signal in `recognition.deterministic` is a positive structure — an
enumerating table, a declared volume total, a date-event-source triple, a sequence column, a
disposition column, an archive member set. The `XX plan` fixture carries an explicit
`must_not_conclude` forbidding the absence-of-caption reading, because that fixture is where the
temptation is worst.

## Node test, all three legs

**Leg 1 — detection signals differ from the schema default.** Argued above under Attack 5. The
schema's second precondition leg is replaced, not supplemented: enumeration over members or events,
plus a listing anchor. Both legs required; the collision fixture
`Completion bundle index - Project Larkspur.pdf` is the proof that the enumerating structure alone is
insufficient, and `Hearing 12 June - listing.ics` is the proof that the listing anchor alone is
insufficient. A row whose signals could be satisfied by either half would be a filename filter.

**Leg 2 — recommended dimensions differ.** `dimension_order` is `[]`, as it must be for every
template on this fieldless schema (D1/PR-6, `_CONTRACT`, CONNECTION PR-6), so the difference has to
be argued in the prose recommendation, which is what the schema's own `template.why` demands of all
36 siblings. The schema's default prose is *client (only on explicit approval) → matter → document
function → period*. Mine is *client (same guard) → matter → **the sitting** → nothing*. Two
differences, and the second is the sharper: **document function is removed as a level, not
reordered.** Pleadings / statements / medical / correspondence / authorities are the bundle's own
*sections*; turning them into folders dissolves the only object that exists. And the row is **not**
time-first despite everything in it pointing at one date — 00 settles that against the temptation:
"For document and record domains, project, function, or subject usually comes before time because
putting year first scatters related work across calendar folders." A chronology spanning eleven years
belongs to one sitting. The sitting is an *event* anchor, not a time dimension, and I say so
explicitly so no later reader reads the sitting level as a licence for year-first.

**Leg 3 — privacy rules differ.** This is the row's strongest leg and it is genuinely new material,
not an inheritance restated. Two claims:

*Aggregation defeats member-level protection.* Every protection in this product is applied to files.
00 names the four safety domains — "Finance, identity, medical, and legal material should be
implemented first as safety domains, meaning the system detects and protects them before any cloud or
automated placement decision is allowed." A claimant's passport, a discharge summary, a bank
statement and a child's school report each individually trip those detectors as files, and inside
volume 3 of a bundle they trip **nothing**, because there is no passport file to detect. The fixture
`Bundle - Hartley v Nash - vol 3 - medical and financial.pdf` exists solely to carry that claim, and
its `must_not_conclude` names the wrong conclusion as the one that does real harm.

*The index is separately disclosive.* A bundle index is a one-line abstract of every document in a
case — small, textual, and exactly the artefact a summariser reaches for. 00's own contrast governs
it: "A summary such as “11 protected identity records” may be safe to show, while a visible list of
passport filenames on a shared screen may not be." An index read aloud *is* that visible list.

The row also widens the exposed class further than any sibling: a juror or panel member has no
relationship with the holder at all and gave their address, employer and household details to a
court, not to a law firm. And it argues one *relaxation*, marked as a recommendation and not a
permission: a sitting level expressed as a date and a room usually discloses far less than a client
or party level — though in a small corpus a lone dated hearing level identifies the matter above it,
so it is not automatic.

All three legs differ. The node stands.

## Files considered and rejected

- **A filed skeleton argument or written case with a caption and a filing mark.** Tempting because it
  is written for one sitting and cites bundle pages. It goes to `law_practice.motions-and-briefs` /
  `.pleadings`: a filing and service apparatus is their evidence, not mine. Taking it would be the
  lifecycle claim Attack 1 warns against. See NJ-TP-2.
- **A designation / counter-designation table.** Built for a hearing, enumerating, tabular — and not
  mine. Its rows are page-and-line coordinates into a transcript, which is
  `law_practice.depositions-testimony`'s structure, in that row's own landed words. I adopted its
  firewall rather than renegotiating it.
- **A disclosure review log.** A table of documents in a matter, produced in the run-up to a hearing.
  It is `law_practice.discovery`'s because its rows *decide* something about a document (responsive,
  privileged, redact). Mine *place* a document in a sequence.
- **A record on appeal.** Compiled, indexed, continuously paginated, multi-volume, with a court name
  on the cover. `law_practice.appeals`' — its anchor is a lodged appeal reference and its pagination
  is the appellate record's own.
- **A witness statement or proof of evidence.** Prepared for the hearing, drafted by the practitioner.
  `law_practice.depositions-testimony` absorbed it and flagged the seam itself (its NJ-DEP-1); its
  own proposed alternative (c) was to route statements here. I decline that: a statement is one
  person's attested evidence anchored on the person, and it has no enumerating structure at all.
- **A hearing transcript, and a key-passages index over it.** Retrospective, coordinate-keyed,
  `law_practice.hearing-transcripts`'.
- **A dated hearing entry, a limitation table, a key-date diary.** `law_practice.deadlines-diary`'s.
  A listing reference is a `never_alone` here.
- **A cast list of counsel and a service list.** A list of names with no imposed order is a contact or
  service artefact for the matter file, not a running order. The sequence is the evidence.
- **Downloaded judgments and practice texts.** Reading Inbox unless compiled into a tabbed, paginated
  authorities volume cross-referenced from a reading list — and the compiled version competes with
  `law_practice.legal-research`, which is why that edge is written.
- **A photograph of lever-arch spines.** An image of an object. One-Off Images; it supports no
  membership and licences no fact, whatever the case name on the spine says.
- **A live document-management or practice system.** Not a file node. A bounded archive whose member
  set reads as a compilation is represented; live ingestion is a later connector decision.

## Reciprocal boundaries

Ten edges, each written as an object with a `signal` naming **the same fixture on both sides** and
the discriminating evidence, per the edge-shape repair. The four that matter most:

| Neighbour | Shared fixture | This row owns | Neighbour owns | Discriminator |
|---|---|---|---|---|
| `law_practice.evidence-exhibits` | `Bundle index - Hartley v Nash - vol 2.pdf` | the compilation and its index | the schedule of exhibits inside it | ordering key: tab + continuous compilation page vs designator namespace |
| `law_practice.closing-binder` | `Completion bundle index - Project Larkspur.pdf` | set anchored to a tribunal listing | set anchored to a transaction completion | the anchor event in the header — often one line |
| `law_practice.depositions-testimony` | `Designations and counter-designations - Lee - with objections.xlsx` | enumerations over documents/events | enumerations over transcript coordinates | what the rows address |
| `law_practice.discovery` | a spreadsheet of documents with dates and descriptions | rows carrying tab / order / compilation page | rows carrying reviewer + decision | does the row decide about a document or place it? |

Also written: `hearing-transcripts` (prospective vs retrospective, in that row's own landed words),
`motions-and-briefs` (filing apparatus), `appeals` (appeal reference vs first-instance listing),
`legal-research` (enumeration serving an argument vs serving a hearing's pagination),
`deadlines-diary` (is the artefact a date record or an ordering anchored to one), and `legal` — where
the boundary is not symmetric in force: `legal` is a safety domain, its protection runs first on any
member it fires on, and this row's compilation claim never discharges it.

**Neighbours considered that did NOT get an edge.** `career` and `finance` were in
`must_consider_neighbors`. `career` earns nothing: a consulting statement of work has organisations,
fees and deliverables but no enumeration over members and no listing, and the landed
`legal.practice-matter-file` already holds that false friend. `finance` earns nothing *at this row*:
a bundle volume containing bank statements is an aggregation problem, handled in `sensitivity_why`
and in the `legal` edge, not a competing claim over the compilation. `law_practice.investigation` was
considered for the juror questionnaire batch and rejected here but raised as NJ-TP-3.

**`also_holds_with` is empty and deliberately so.** CONNECTION §5 makes it schema ↔ schema only and
this row is a template. The intent I would otherwise have recorded there, left for R1c: a compiled
bundle volume plausibly carries `medical`, `identity` and `finance` material simultaneously as pages,
and that is a question for the `law_practice` schema row's own edges, not for a template.

## The collision fixtures

Two, because one was not enough to cover both halves of the two-leg test.

1. **`Completion bundle index - Project Larkspur.pdf`** — structurally *indistinguishable* from this
   row's anchor: member descriptions, tab numbers, continuous pagination, a volume marker. It has the
   enumerating structure and **no listing anchor**; its anchor event is a completion. Discriminated by
   one header line. This fixture is the entire reason the second leg is a *listing* anchor rather than
   merely "a compilation structure", and it is the collision I would most expect a naive detector to
   get wrong.
2. **`Table of Cases and Index - Civil Procedure (2026 ed).pdf`** — an enumerating table over
   documents with page references, inside a long continuously paginated PDF, full of legal
   vocabulary. Discriminated by what is enumerated (published decisions, not matter material) and by
   the absence of any matter reference, listing or declared volume total. It falls to Reading Inbox,
   and it is why continuous pagination is a `never_alone`.

## Fields

`fields: []` and `proposed_fields: []`, both intentional. The schema owns the fields and declares
none under D1/PR-6; a template may not mint. I considered and rejected proposing `event` (canonical,
destination-eligible) as the carrier of the sitting level: it would be a *schema* declaration, the
schema's own `proposed_fields` already stakes out `client` and `our_firm` for R1c with the
destination-eligibility condition attached, and adding a third proposal from a template row would
pre-empt an adjudication that is not mine. If R1c lifts PR-6, the recommendation to carry forward is:
**the sitting level should reuse canonical `event`, not a minted `hearing` or `listing` key**, and its
destination eligibility should be conditioned the same way `client`'s is.

`proposed_context_terms` is populated (bundle index, tab, volume of, core bundle, dramatis personae,
running order, given, refused, as modified, listing reference, …) and every one of them is a
*proposal*, not a claim that 00 listed them. None of them is sufficient alone; all of them are inside
the `never_alone` sweep.

## NEEDS-JOSEPH

- **NJ-TP-1 — the name is a lifecycle stage and the row is not.** Alternatives: (a) keep the id, read
  the roster name "Hearing and trial preparation" narrowly — recommended; (b) **rename to
  `compilation-and-bundle`**, which kills the stage reading outright and which I would welcome;
  (c) refuse and disperse — opposed, because the aggregation-defeats-protection claim would then have
  no home.
- **NJ-TP-2 — the advocacy-document seam.** `motions-and-briefs` and `pleadings` are unlanded and the
  boundary turns on a filing apparatus a working copy may simply lack. Alternatives: (a) as drawn;
  (b) all written advocacy to the neighbours, shrinking this row's `work_types` by three — cleaner;
  (c) all hearing-directed advocacy here — rejected as the NJ-TP-1 lifecycle claim.
- **NJ-TP-3 — the absorbed `law.jury-materials`.** The numbered instruction set fits this row's
  structural test cleanly; a juror questionnaire batch does not order anything and is structurally
  closer to `law_practice.investigation`'s interview records, while carrying the sharpest privacy
  problem in the row. Alternatives: (a) keep as absorbed — recommended, since splitting on a document
  type is the 574's mistake; (b) questionnaire batches to Protected Records unconditionally;
  (c) generalise clinical_practice's multi-subject-list rule at schema level.
- **NJ-TP-4 — the compilation posture has no mechanism.** The row asserts a compilation inherits the
  strictest posture of any member it plausibly contains, and nothing expresses that: sensitivity here
  is only `none` | `potentially_sensitive`, a bundle volume and an office memo take the same value,
  and handling classes are P7's. Alternatives: (a) P7 defines a container posture and this becomes a
  P7 input; (b) the schema records a container rule suppressing interior excerpting for any artefact
  whose structure is an enumeration over members; (c) nothing, and a bundle is protected only as well
  as its outer file type suggests — which I believe is wrong, and record so the choice is deliberate.

## Recommendations for R1c (not made here — cross-row)

1. Reciprocals owed **to** this row from `law_practice.closing-binder`, `.discovery`,
   `.motions-and-briefs`, `.legal-research`, `.deadlines-diary`, `.appeals` (all unlanded), using the
   same fixtures named in this row's `collides_with`.
2. `law_practice.evidence-exhibits` asked for this reciprocal and it is now written; its NJ-EX-2
   merge direction (merge *into* this row) is accepted as insurance but not requested.
3. If PR-6 lifts, declare `event` on `law_practice` for the sitting level with conditioned
   destination eligibility — do not mint `hearing` or `listing`.

## Self-verification

- `python3 -m json.tool planning/domains/nodes/law_practice.trial-preparation.json` → parses.
- Key set matches the landed sibling `law_practice.evidence-exhibits.json` exactly, including
  `proposed_context_terms`.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (`text_document`, `spreadsheet`, `archive`,
  `ocr`, `image`, `calendar`).
- Every edge target checked against `planning/domains/roster.json`: `evidence-exhibits`,
  `depositions-testimony`, `hearing-transcripts`, `closing-binder`, `discovery`, `motions-and-briefs`,
  `appeals`, `legal-research`, `deadlines-diary`, `legal` — all present. Every
  `falls_through_to.residual_template` is one of 00's nine residual homes.
- Every `collides_with` entry is an object with `domain` / `signal` / `provenance`, and every signal
  names the same fixture on both sides. `also_holds_with` is empty (template row).
- Every quotation grep-verified verbatim against its source before writing: the purpose-coherence
  span, the archive-inspection span, the project-function-before-time span, the four residual-library
  spans, "no valid anchor", "meaningless one-child levels", "implemented first as safety domains",
  "11 protected identity records", "does not automatically copy those missing facts onto sparse
  files", and the client-or-matter-label span (verified in
  `planning/domains/nodes/legal.practice-matter-file.json`, attributed as the landed neighbour's
  words, not 00's).
- No threshold numbers, no confidence scores, no handling classes; sensitivity is
  `potentially_sensitive`. `design_cite` is a grep-verified span.
- Files written: exactly the two assigned. Nothing else in the repository was touched.
