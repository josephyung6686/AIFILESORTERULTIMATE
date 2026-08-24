# construction_property.variation-claim — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `cons.variation-claim` (ROSTER.md Appendix A).

## Sources used

- `planning/00-database-agent-product-design.md` — all quotations grep-matched verbatim before writing.
- `CONNECTION.md` (node test §2, the grouping firewall §4 step 9, closed edges §5, PR-6),
  `_CONTRACT.md` (rules 5, 6, 8, 10, 11–15), `ALIGNMENT.md`, `roster.json` (collisions checked).
- Landed neighbours read and reciprocated: `business_operations.contract-administration` (which already
  names `construction_property.subcontract` for the adjacent reason), `legal.leases-agreements`,
  `finance.household-property`, `business_operations.organisational-records`.

## The node test, applied honestly (the brief asked)

Challenge: is this a `work_type` value of `construction-project`? **Node**, on all three grounds, and the
argument is specific rather than enthusiastic:

1. **Detection signals.** Two structures exist nowhere else in the catalogue: a register pairing a MONEY
   column with a TIME-EFFECT column beside a DISPUTE STATUS, and a notice that asserts its own timeliness
   ("served within X days of becoming aware"). The self-referential time-bar sentence is a genuine
   fingerprint — contracts create rights that die if the paper is late, and nothing else writes like that.
2. **Dimensions.** The recommended shape is contract → the change or claim as its own container →
   function, and the middle level is forced by the artefact: this row's defining object is a BUNDLE of
   files that share no content, held together by one argument. A document-type-first tree would scatter
   precisely the files that must stay together. That is a different dimension recommendation from the
   project row's default, which is the second of CONNECTION.md §2's three grounds.
3. **Privacy.** Without-prejudice material, settlement positions and internal assessments of an opponent
   are a different posture from ordinary project material, and the harm from exposure is the loss of the
   claim rather than embarrassment.

## Files considered and rejected

- **A manufacturing/engineering change order.** Kept as a fixture; the structure is identical and only
  the anchors (a machine and a line) separate it. Routed to `engineering.change-order`.
- **The snagging list.** Kept as the load-bearing fixture, reciprocated word-for-word on both rows.
- **Payment notices and pay-less notices.** Considered here — they are notice-bound and adversarial —
  but rejected into `construction_property.subcontract` and `construction_property.final-account`,
  because their anchor is a payment cycle rather than a change to the works.
- **Programmes / Gantt charts.** Rejected as their own thing; they appear here only as claim appendices,
  and the appendix relationship must not transfer ownership.

## The bundle, and the grouping firewall

This row is where 00's "content-incoherent but purpose-coherent" sentence stops being an example and
becomes the everyday case. A claim bundle's index cites diary pages, weather reports and photographs
that belong to other rows. The node file states in two places that citation in a bundle index is not a
fact writer, on the strength of CONNECTION.md §4 step 9 and 00's own sentence that the graph does not
copy missing facts onto sparse files. It also records the nastier version: bundles deliberately include
comparator files from *other projects*, so a bundle folder is a place where the stop rules must hold.

## proposed_fields

None. Schema declares no field rows (D1 as narrowed, PR-6). Prose candidates: a contract/project key,
a change-or-claim identifier key (the row's true second dimension), and the which-side-am-I role that
three other rows in this catalogue independently want. Not minted; recorded for R1c.

## Neighbours considered that did NOT get an edge

- `legal` (schema) — real, expressed as `also_schema: "legal"` on the bundle and without-prejudice file
  examples rather than as an edge, since `also_holds_with` joins schemas only and this is a template row.
- `government.public-procurement` — public-sector variation regimes are similar; rejected because the
  discriminating evidence (a contracting authority, a published notice) already separates them cleanly
  through `business_operations.contract-administration`'s existing edge, and duplicating it here adds
  shelving rather than evidence.
- `manufacturing.warranty-claim` — the word "claim" collides, but the evidence does not; the collision
  that matters there is captured on `construction_property.snagging-defects`.

## NEEDS-JOSEPH

- **NJ-CP-VAR-1 · Defect or variation.** Reciprocal with `construction_property.snagging-defects`, same
  wording on both rows. Recognise both, abstain, and let Joseph decide whether a genuinely-both file is
  offered twice or once.
- **NJ-CP-VAR-2 · The claim bundle and the firewall.** A bundle is a purpose group whose members belong
  to other rows and sometimes other projects. This row asserts no new mechanism and relies on the
  existing firewall; whether that is sufficient when a bundle folder is scanned as a folder is worth a
  decision before P9 builds grouping.
