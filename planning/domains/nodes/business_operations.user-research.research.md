# business_operations.user-research — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.project-delivery.research.md`; all quotations
machine-verified verbatim against `00-database-agent-product-design.md`. Landed siblings read for key set
and idiom: `business_operations.json`, `business_operations.it-asset-inventory.json`. **Read specifically
because the dispatch brief flagged a possible collision:** `research.json` (the schema row),
`research.ethics-compliance.json`, `research.project-workspace.json`, `research.dataset-analysis.json`.
No legacy row is recorded for this id in `ROSTER.md` Appendix A beyond `ops.user-research` (ROW, line 832).

## What it is for, and what it holds

A product team wants to know what the people who use their product actually do and need, so it runs
studies on them. The row holds study plans and discussion guides, screeners, participant consent forms and
information sheets, session recordings and screen captures, transcripts, observation notes, survey
instruments and response exports, affinity maps and coding sheets, personas and journey maps, and findings
readouts with their highlight reels.

## Node test — passes; and the flagged collision was checked, not assumed

The brief warned that this row may collide with the landed `research.*` rows. I read them before answering.

**They stay separate**, for two reasons about the *situation* rather than the vocabulary:

1. **The output differs absolutely.** A product study ends in an internal readout that changes a backlog. An
   academic study ends in a manuscript at a venue. `research`'s own fields — `stage`, `lab`, `venue` — are the
   fields of that second world, and none of them fits a usability test.
2. **The governance differs.** `research.ethics-compliance` exists precisely to hold the review-board
   apparatus (protocol number, approval letter, training certificates) that product research usually does not
   have.

**But the overlap is real and is carried, not hidden:** a `collides_with` to `research.ethics-compliance` for
the case where the *same* evidence would be misread, and an `also_holds_with` to the `research` **schema** for
the industry-research case where two disjoint evidence sets are both genuinely true. That is 00's
abstract-and-application shape in a product setting, and it is a join rather than a mutex.

## Files considered and rejected

- **`Interview - Dr Adeyemi - IRB 2026-114.docx`** — kept as the fixture for exactly the collision above, and
  it is the one example in my seven rows carrying `also_schema: "research"`.
- **`Discovery call - Northwind Ltd.docx`** — kept as the second fixture: interview shape, selling purpose.
- **`transcript_P04.vtt`** — kept because it makes the point that matters most here: a participant volunteers
  an employer, a home city and a bank name while describing a task, and that volunteered detail is protected
  material regardless of the study's own framing.
- **`Personas - v3.fig`** — kept for one narrow reason: a persona name is a *fabricated composite*, and treating
  it as a person fact is a specific, plausible error.
- **A card-sort or tree-test export** — real, folded into `work_types` rather than given an example.
- **An analytics or clickstream export** — deliberately excluded: it is behavioural telemetry, not evidence
  gathered *from* people under consent, and admitting it would blur the row's defining property.

## proposed_fields

**None.** A `study` anchor would reuse the existing canonical `project` key rather than mint a synonym — the
contract names that exact failure mode (`course_name` when `course` exists). A `participant` key was considered
and **rejected on principle**: it would be a key whose only use is a folder level naming a named third party,
which is the level this row's template explicitly refuses to recommend. Minting a key to enable a dimension the
row argues against would be incoherent.

## Neighbours considered that did NOT get an edge

- **`creative`** — research artifacts live in design tools and design workspaces. The `.fig` example carries the
  ambiguity in prose; a full edge would be about file residence rather than evidence.
- **`academic.teaching`** — student research projects share the shape. Covered by the `research` edges.
- **`government`** — public-sector service design and consultation exercises are the same situation under a
  statutory consultation duty. Genuinely in scope and left unedged at gist depth; flagged below.

## NEEDS-JOSEPH

- **NJ-BO-UR-1 · Confirm the product/academic separation** and the reciprocity it needs. The `also_holds_with`
  to the `research` schema is **authored one-way here**; the landed research rows do not name
  `business_operations`, and R1c owes the reciprocal.
- **NJ-BO-UR-2 · Should the raw session layer be its own protected sub-situation?** Recordings, transcripts and
  signed consent forms are the only material in the entire `business_operations` family collected under an
  explicit promise to a third party about how it would be used. Careless handling breaches the consent that
  licensed the collection, not merely a preference. This pass holds them as `work_type` values inside one row and
  records that the promise arguably deserves its own mechanism.
- **NJ-BO-UR-3 · Public-sector consultation.** Same situation, statutory duty, different retention rules. No edge
  authored to `government`; R1c should decide.
