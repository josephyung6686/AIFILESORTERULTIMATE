# construction_property.site-diary — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `cons.site-diary` (ROSTER.md Appendix A).

## Sources used

- `planning/00-database-agent-product-design.md` — every quotation in the node file was grep-matched
  verbatim against this file before it was written.
- `planning/domains/CONNECTION.md` (node test §2, closed edge vocabulary §5, PR-6), `_CONTRACT.md`
  (rules 8, 10, 11–15), `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — id, kind, schema_id, neighbours; every `collides_with` target was
  checked against the roster's node list mechanically.
- Landed siblings read for house standard and for reciprocal boundaries:
  `business_operations.contract-administration` (idiom and depth),
  `business_operations.organisational-records` (what a refusal looks like),
  `finance.household-property`, `legal.leases-agreements`, `career.employment-records`.

## What this row is, argued

The site diary is the only document family in construction whose *value is serial*. A single page
proves almost nothing; three hundred consecutive pages prove that a record was kept contemporaneously,
which is the whole reason the practice exists. That is a real organizational situation and not a
document kind: the same physical page is a diary because of the run it sits in.

Its detection signals differ from the schema's default in one specific and checkable way — no other
document in this family pairs a **weather slot** with a **labour count by trade**. That pairing is
the row's fingerprint. Its recommended dimensions differ too: this is the only construction row whose
second level is genuinely a period, because users retrieve a diary by date. Node test passed on
signals and dimensions both.

## Files considered and rejected

- **Site meeting minutes.** Rejected into `business_operations.meeting-record` and recorded as this
  row's load-bearing collision. Both are dated site narratives; the trigger differs (the day happened
  vs a meeting was convened) and the minute carries an attendee list and numbered actions.
- **A personal journal named `diary 2026.docx`.** Kept in the file examples deliberately as the
  never-alone fixture. The filename vocabulary of this row collides exactly with the most private
  document a user owns.
- **The accident book entry.** Left to `construction_property.site-health-safety` with `also_schema:
  "medical"`, because an injury narrative about a named person is health information and the safety
  ordering must run first.
- **Programme / Gantt files.** Considered and rejected: a programme is a plan, not a record of a day.
  It has no home in my ten and most plausibly belongs with `construction_property.construction-project`.

## proposed_fields

None. The construction_property schema declares no field rows (D1 as narrowed, PR-6), and a template
may not mint keys. Two candidates are worth recording *in prose* for whoever answers the schema row's
open_question, and are deliberately NOT minted here: a site/project key (the row's true top dimension)
and a period key. Both are wanted by nearly every row in this family, which is an argument for the
schema row proposing them once rather than twenty-seven templates proposing variants.

## Neighbours considered that did NOT get an edge

- `finance.household-property` — a homeowner's building-work file may contain a builder's day-sheets,
  but the household row's anchor is the property as a financial asset and nothing in its detection
  signals would fire on a labour return. No collision.
- `legal.leases-agreements` — no shared evidence; a diary has no execution block.
- `academic` / `research` — a lab notebook is also a serial dated record, and I considered a collision.
  Rejected: no shared discriminating evidence item exists at the token level (a lab notebook has no
  weather slot and no trade names), and the edge would have been topic similarity, which
  CONNECTION.md §5 explicitly excludes from `collides_with`.
- `photos` — the schema is real, but the collision that matters is with the sibling template
  `construction_property.progress-photos`, and `collides_with` joins same-kind pairs, so the sibling
  template is the correct endpoint.

## NEEDS-JOSEPH

- **NJ-CP-DIARY-1 · The personal-journal collision.** A site diary and a private journal share a
  filename vocabulary, a structure and a source type. Detection cannot separate them before content is
  read, and reading content is exactly what the privacy policy gates. Stated reciprocally: this row
  claims only files that show the diary form furniture; anything else named "diary", "journal" or
  "daybook" must default to the protective residual home rather than to this row. Joseph's call is
  whether that default is acceptable when it means some genuine site diaries land in Protected Records.
- **NJ-CP-DIARY-2 · The labour allocation sheet.** Its site reading is here and its pay reading is
  `hr.payroll-benefits-administration`'s; `construction_property.timesheet` is refused (see that row).
  Reciprocal statement: this row claims the sheet only where it carries a site or cost-code column and
  no pay rates; where rates or deductions appear, the hr row and its stricter posture win.
