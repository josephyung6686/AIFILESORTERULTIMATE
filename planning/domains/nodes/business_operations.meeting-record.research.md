# business_operations.meeting-record — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A line 810. Reference standard for
depth, idiom and key set: the landed `clinical_practice.*` files — in particular
`clinical_practice.case-conference.json`, which is the same shape of row in a different world.

## The refusal question, answered honestly

The dispatch brief flagged this row as possibly a **format** rather than a domain, and that is the
strongest argument against it. It runs: agenda / minutes / actions is a document FORMAT; every sibling
row already lists meeting artifacts among its own work types (board packs, project status meetings,
retrospectives, sourcing clarification meetings, case conferences); and what remains after subtracting
them is a file with no reliable deeper association, which is 00's own definition of a **residual**, not
a domain.

**The row is kept, narrowed.** Three reasons, in order of weight:

1. **The leftover pile is real and coherent, not residual.** Standing team meetings, running
   one-to-ones and counterparty call notes are a large recurring stream whose anchor is a **meeting
   series** that belongs to nothing else. A residual is for files with no association; these files
   have a strong one.
2. **The node test is met on its first leg.** CONNECTION.md §2: a template row exists if its detection
   signals, dimensions, **or** privacy rules differ from the schema's default. The signals differ
   sharply (the four-part meeting-note structure; the actions table; the date-varying series with an
   identical heading skeleton).
3. **Refusing it costs protection.** The running one-to-one note is the most quietly sensitive file in
   the whole `business_operations` family — one named person's pay, performance and complaints
   accumulating in one document. Refusing the row leaves it with no recognizer.

The counter-argument is not dismissed; it is recorded as the row's `open_question` and as **NJ-BO-2**,
and the row is written narrow (an explicit carve-out in `one_line`) so the decision stays reversible.

## Files considered and rejected

- **`Board pack - March 2026.pdf`** and **`Retro - sprint 41.docx`** — kept as the two collision
  fixtures; they are the shape without the situation.
- **A wedding or committee-of-a-club agenda** — real, identical shape, no organisation. It belongs to
  personal administration or a nonprofit row, not here; left as a boundary noted in prose rather than
  as a ninth fixture.
- **A conferencing transcript `.vtt`** — folded into the recording example rather than given its own,
  because the extractor story is the same and gist depth does not need both.

## proposed_fields

**None.** PR-6 forbids field rows on this schema. Nothing about the row needed one to be stated.

## Neighbours considered that did NOT get an edge

- **`research`** — lab meetings and supervision meetings are this shape, but the confusion is already
  carried by `clinical_practice.case-conference` for the meeting-versus-research pair, and doubling it
  at gist depth adds nothing.
- **`academic.teaching`** — office hours and staff meetings, same reasoning.
- **`government.legislative-record`** — formally recorded proceedings; genuinely different apparatus,
  and `board-governance` already carries the formal-proceedings edge.

## NEEDS-JOSEPH

- **NJ-BO-2 · Is a working meeting a situation or a format?** Stated above and in the row's
  `open_question`. If the answer is *format*, this row folds into a work-type value on every sibling
  plus `Independent Records` / `Review Later`, and the one-to-one protection question below must be
  re-homed rather than dropped.
- **NJ-BO-3 · Where does a running one-to-one note live?** It is simultaneously an ordinary work file
  and an employment record about a named person, and it drifts into `hr.employee-relations` mid-file
  without any structural change. Reciprocally stated: the `hr.employee-relations` side should carry the
  same question. Not resolved here, because the answer decides whether a manager's notes folder is
  ordinary or protected material.
