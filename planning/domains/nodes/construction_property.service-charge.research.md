# construction_property.service-charge — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `roster.json`, `canonical_fields.json`, `DECISION-BRIEF.md`
(J-IND, D1, PR-6), `ROSTER.md` §4 → `13-trades-property-logistics.json` (line 923). Neighbours read
in full first: `finance.hoa-residents-association` (which absorbed the legacy
`npo.residents-association` row and holds the member's side), `finance.household-property`,
`legal.leases-agreements`.

## What it is for, and what it holds

Splitting a building's running costs among the people who live in it. Annual budgets and
apportionment schedules, demands carrying prescribed statutory wording, certified year-end accounts
with an accountant's certificate, balancing charges and credits, reserve and sinking fund
statements, major works consultation sequences, arrears schedules, ground rent demands arriving
beside them, resale and management packs, and the correspondence in which leaseholders challenge
all of it.

## Node test — passes, on the apportionment and the estimate-then-reconcile pair

1. **Signals differ:** a **cost table split by a fixed share per unit**, with the shares summing
   across a building, exists nowhere else in this catalogue. Second: the **estimate-then-reconcile
   pair** over a named accounting year — a budget followed by a certified account for the same
   period — which no ordinary bill has. Third: the **staged consultation** about spending, with a
   notice of intention, estimates and a statement of reasons.
2. **Dimensions differ:** building → service charge year → stage, with the *unit* deliberately
   *below* the year on the professional side.
3. **Privacy differs:** arrears schedules are a list of named neighbours and what they owe.

## Legacy id absorbed (ROSTER.md §4)

`prop.service-charge` (ROW), 1:1. Note that `npo.residents-association` folded into
`finance.hoa-residents-association` rather than here — the roster deliberately put the *member's*
side in finance and the *building's* side here, and this row is authored to respect that.

## The hardest thing about this row

**Two rows, one folder — twice over.**

- Against `construction_property.block-management` (another agent's row): the same agent, the same
  building, the same year. The split authored here is by *function* — this row is the money cycle,
  that row is operations, contractors, compliance and residents. It is a defensible split and it is
  **not** how a user would file, which is why it is the `open_question` and why the collision is
  written so the merge stays available.
- Against `finance.hoa-residents-association`: the professional/householder seam. That row's own
  signal ("dues, member-account, association-governance… structure points here") is reused in shape
  so the pair reads the same way from both ends. The discriminator authored is *whole building
  versus single member*.

**The trap:** a leaseholder's single scanned demand should **not** activate this professional row.
`Scan_demand_flat12.jpg` is the fixture that says so, and routes to a residual.

**A small factual point worth keeping:** a service charge year frequently does not run to the
calendar. That is why "a bare 4-digit number" is especially misleading here and why `template.why`
records the year level as a *named accounting period*, not a date.

## Files considered and rejected

- **`Ground rent demand - Flat 12.pdf`** — kept as the collision fixture: it arrives in the same
  envelope and is a legally different payment.
- **`Arrears schedule - March.xlsx`** — kept as the sensitivity fixture; it is the file that makes
  the group-summary risk concrete.
- **A section-of-lease extract** — rejected: `legal.leases-agreements` owns the instrument and gets
  the collision instead.
- **A block insurance claim file** — rejected: the recharge is here, the claim is
  `finance.insurance-personal`'s; the collision covers it.
- **Tribunal determination papers** — kept only as a `work_types` boundary case; the dispute file
  proper belongs to the legal family and is not authored thinly here.

## proposed_fields

**None.** PR-6 forbids field rows on this schema. Candidate dimensions (building/scheme, service
charge year, stage) are prose in `template.why` for R1c, with the note that *service charge year*
is a named period and not a date — if it ever became a field it must not be conflated with a
calendar year key.

## Neighbours considered that did NOT get an edge

- **`nonprofit.governance`** — a residents' management company has directors and meetings, but that
  is `finance.hoa-residents-association`'s and `construction_property.block-management`'s ground.
- **`finance.subscriptions-utilities`** — communal utility supplies are a cost heading inside the
  budget, not a separate claim on the file.
- **`government.*`** — the statutory regime shapes the documents but is jurisdiction-specific, and
  under D4 that is a **values** question, not an edge.

## NEEDS-JOSEPH

- **NJ-CP-17 · Merge with `construction_property.block-management`?** One agent, one building, one
  folder, split here by function. Stated reciprocally in both rows' collisions; the merge is
  Joseph's call and no research is lost either way.
- **NJ-CP-18 · Where is the threshold between one demand and a building's file?** A leaseholder's
  single scanned demand is `finance.hoa-residents-association`'s or a residual's; a budget plus
  accounts plus an apportionment schedule is this row's. The exact threshold is the same shape of
  judgement as NJ-CP-13 (when a transaction stops being a transaction) and is Joseph's for the same
  reason.
