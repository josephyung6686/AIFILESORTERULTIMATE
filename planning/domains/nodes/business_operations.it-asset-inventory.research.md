# business_operations.it-asset-inventory — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Provenance of this file: SALVAGE

The JSON for this row already existed as a structurally complete but **unverified** draft left by an
agent killed mid-wave, with no memo. It was not trusted and it was not discarded. What was done:

- **Verified mechanically.** Every `“…”` span in the file was normalised and matched against
  `00-database-agent-product-design.md`; all matched verbatim. Every `collides_with.domain` was
  checked against `roster.json` (`finance.small-business-bookkeeping`, `manufacturing.asset-register`,
  `business_operations.procurement-sourcing`, `business_operations.contract-administration`,
  `hr.onboarding-offboarding`, `business_operations.facilities-workplace`, `code.software-project` —
  all real ids). Every `source_type` was checked against `SOURCE_TYPES`; every
  `falls_through_to.residual_template` and `falls_through_if_inactive` against 00's nine names.
  `fields` is empty, as PR-6 requires.
- **Key set compared** against the reference standard `clinical_practice.case-conference.json`:
  identical key set, identical order, identical `template` sub-keys.
- **Repaired.** Two `never_alone` entries were run-on strings each carrying two distinct invariants
  ("a spreadsheet alone, or … an extension or a source_type alone"; "a hardware or software vendor's
  name alone. an organisation's name alone …"). Each was split into one entry per invariant, so the
  list is a list of invariants rather than of sentences. Nothing else was changed: the substance
  verified, and rewriting a sound draft to make it sound like me would have been the worse call.

## What it is for, and what it holds

Keeping a maintained record of the IT estate — what hardware and software exist, who holds each item,
what it is entitled to run, and how it is wired together. Registers, licence and entitlement records,
device-management exports, estate diagrams, handover and return forms, warranty cover, disposal
certificates, refresh plans, stocktake reconciliations.

## Node test — passes, on the anchor

The anchor is the **estate as a standing inventory**, not a purchase and not a contract. Detection
signals differ from the schema's default (identity-plus-custody header; entitlement-plus-seat-count;
estate diagram text layer). Privacy rules differ in a specific direction the draft got right: a
register is a staff directory joined to a serial list, and a diagram is a map of how to reach the
estate. Dimensions do not differ, and cannot, because the schema declares no fields.

## Legacy ids absorbed (ROSTER.md Appendix A, lines 693–694)

`soft.it-asset-inventory` (ROW) and `soft.network-diagram` (FOLD). Both are named in the row's
`one_line`, so a later reader can see what it owns.

## proposed_fields

**None.** PR-6 forbids field rows on this schema and no field was needed to state the row.

## Neighbours considered that did NOT get an edge

- **`business_operations.support-operations`** — asset records are pulled into ticket handling
  constantly, but the confusion is about lookup, not about which situation a file belongs to.
- **`government.public-authority-record`** — a public body's asset register is the same document under
  a records regime; left unedged at gist depth rather than guessed.

## NEEDS-JOSEPH

- **NJ-BO-1 · The single-person estate.** Carried from the draft's `open_question` and endorsed: a
  freelancer's list of their own laptops, warranties and subscriptions has exactly this shape and none
  of the organisational anchor. Deciding it silently would file someone's personal device list under a
  work branch. Relates to **NJ-BO-8** below (the same person-versus-organisation line, from
  `partnerships-bd`) — R1c should notice they are one question asked twice.
