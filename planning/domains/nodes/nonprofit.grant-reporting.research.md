# Research memo — `nonprofit.grant-reporting`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/nonprofit.grant-reporting.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, placeholder launch
Result: **REFUSED** (`refuse_node: true`)

## Result in one paragraph

Recipient-side grant reporting is real, is the family's strongest non-exchange case, and is not a child node. The `nonprofit` schema's own second deterministic signal — the restricted-grant lifecycle on the grantee side — already names the funder/grantee pair, the restricted purpose clause, the payment schedule, the milestone reports, and the expenditure reconciliation joined by one award reference. The roster hint (reports, claims, drawdowns, variations, monitoring visits, closure) either restates that signal or lists lifecycle stages of it. A template that differs from its schema only by pinning the default "grant" counterparty, or by renaming stages of the same award, fails CONNECTION §2 on every leg. Coverage is not lost: the schema fires; `government.grant-programme-administration` holds the funder twin; `research.grants-funding` holds research money; `nonprofit.fundraising-donor` holds the unconditional gift; `legal` holds the instrument.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped R1b prompt from `make_prompt.py nonprofit.grant-reporting`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the one landed launch row read for depth calibration (structure and refusal-adjacent honesty, not content).
- `planning/domains/nodes/nonprofit.json` — the schema anchor, read through recognition, template prose, work_types, grouping_reasons, file_examples, collides_with, also_holds_with, falls_through_to, sensitivity_why, role_split, and open_question (NJ-NP-2, NJ-NP-4).
- `planning/domains/nodes/nonprofit.fundraising-donor.json` — sibling that already authored a SAME-FIXTURE edge against this id (`Community Trust - award letter 2026.pdf`); read at the matched spans only.
- `planning/domains/nodes/government.grant-programme-administration.json` — neighbour that already authored the claim-workbook edge against this id; read at the matched spans only.
- `planning/domains/nodes/nonprofit.standards-body.research.md` and `nonprofit.governance.json` — refusal shape for this family (how to decline inherited edges; how also_holds_with stays empty).
- `planning/00-database-agent-product-design.md` — reached only by `grep -F`. Every quotation in the JSON was verified verbatim before writing; all matched.
- `planning/domains/roster.json` — every id named below confirmed present.

`CONNECTION.md` §2 (node test) and §5 (`also_holds_with` is schema ↔ schema only) applied as stated in the dispatch. No external web sources: artefact shapes are marked inference.

## The charge — strongest case this row should not exist

Stated first, before any defence.

**1. It is a duplicate of the schema's default template.** The schema's restricted-grant lifecycle signal is this row's entire world. Its first file_example is already `Grant agreement - REF GT-2024-118 - signed.pdf`. Its first grouping reason is already "one GRANT from call to closure". Its work_types open with "grant application, offer, agreement, drawdown and monitoring report on the grantee side". ALIGNMENT: a template that would only repeat its schema's fields and dimension order is not a node — it is the schema's default template.

**2. It is a lifecycle stage sequence.** The hint names reports, claims, variations, monitoring, closure — states of one award. `nonprofit.standards-body` was refused partly for that shape; the same disqualifier applies.

**3. It is a work_type enum promoted to a node.** Strip the hint and you get values the schema already lists.

**4. It is a document-type cluster.** "Grant report", "claim", "monitoring letter" are document-type words; the schema strikes those as never-alone beside an association name.

**5. Neighbours already carved the only seams.** fundraising-donor owns gift-versus-grant; government.grant-programme-administration owns funder-versus-grantee; research.grants-funding owns research-versus-programme; legal owns the instrument. After those subtractions the residue is the schema default.

**6. NJ-NP-4 projected it, but projection is not the node test.** The schema listed "grant-funding-received" among seven defensible templates. That list is evidence of authorial intent, not of a detection difference. Contact with the recognition text shows the coverage is already written as the default.

Unlike five refused siblings (advocacy, governance, political-campaign, standards-body, volunteer-management), this row does **not** fail the non-exchange precondition. Funder and grantee with a restricted purpose is exactly the relation the anchor requires. The charge is duplication of default, not inability to activate.

## Defeating the charge — attempted, and it fails

The keep-case deserves a full hearing because two landed neighbours and the schema's own NJ-NP-4 treat this id as live.

**Keep argument A — residue beyond the schema sentence.** Claims, variation requests, and monitoring-visit letters are not named verbatim in the schema's restricted-grant bullet. If they were distinctive structures, the row would have leg-1 residue.

They are not. Each carries the same award reference, the same funder/grantee pair, and the same purpose restriction already required to fire the schema. A claim is a payment-schedule instalment made concrete; a variation is an amendment of the same instrument's dates or headings; a monitoring visit is a funder-authored checkpoint against the same reporting clause. Renaming stages of one relation does not create a second detection set. The schema already says a single application with no award and no reporting is not the lifecycle — completeness is gated at the parent.

**Keep argument B — dimension difference.** Recommend grant-reference → period of performance → function, unlike a generic "fund" level.

Fails: the schema's prose default already permits "the grant" as the counterparty-or-fund level. Pinning that level to grant is a filter on a permitted value, not a different order — the electrical-schematic finding. Both machine-readable `dimension_order` arrays are `[]` under PR-6 anyway.

**Keep argument C — privacy difference.** Monitoring returns name beneficiaries; claim workbooks expose programme failure.

Fails: the schema's sensitivity paragraph already argues third-party exposure under need, forbids person-named folder levels, and places Protected Records first among residuals for exactly this payload. A child cannot claim a stricter rule the parent already owns, and claiming a looser one would be wrong.

**Keep argument D — the fundraising-donor seam needs a named neighbour.** That sibling's collision prose is real and useful.

Fails as a reason to keep *this* row. The seam is gift (unconditional, printed non-exchange) versus grant (conditional, report-back). The grant side of that seam is the schema default. R1c can retarget the edge to `nonprofit` without inventing a child. “Nobody has a named target for my edge” is not the node test — the same finding standards-body used against “nobody owns the comment table.”

Three legs, three failures. Refuse.

## The node test, all three legs

### Leg 1 — detection signals

CONNECTION §2: a template exists only if detection signals differ from the schema's default. The schema's restricted-grant signal is co-extensive with this row's candidate set. Sort the file list: every positive fixture either is the schema's flagship agreement example, or is a stage of that lifecycle, or is already claimed by a neighbour on a different discriminator (side, research-versus-programme, gift-versus-grant). **Fails.**

### Leg 2 — recommended dimensions

Machine comparison is vacuous (`[]` vs `[]`). Prose comparison: schema default is association → counterparty-or-fund (explicitly including the grant) → period → function. This row wants grant → period → function. That is the default with one value pinned. **Fails.**

### Leg 3 — privacy rules

Schema posture already covers beneficiary-named returns and disclosive funder relationships. No operative rule this child would add (roll-level bans, self-declared disclosure flags, non-consent prospect dossiers) appears in the grant-reporting file set the way they appear for fundraising-donor or member-association. **Fails** — identical in kind, not merely in degree.

## Files considered and rejected

Tempting false positives, and why each is not this row's evidence:

1. **`Grant agreement - REF GT-2024-118 - signed.pdf`** — schema's own flagship. Activates the parent; cannot support a child that must differ from the parent.
2. **`GT-2024-118 - Q2 claim and monitoring workbook.xlsx`** — real, and the shared fixture with government.grant-programme-administration. Side decides; with this row refused the grantee side is the schema.
3. **`GT-2024-118 - interim narrative report - Jul 2026.docx`** — named inside the schema signal ("milestone or interim or final report").
4. **`GT-2024-118 - variation request - extend end date.pdf`** — lifecycle stage, not a situation.
5. **`GT-2024-118 - monitoring visit letter - 14 Mar 2026.pdf`** — same award relation; funder outbound copy may be government when authority status is evidenced.
6. **`Community Trust - award letter 2026.pdf`** — fundraising-donor's shared fixture; conditional side is the schema, not a child.
7. **`NOA - R01GM123456 - period of performance.pdf`** — research.grants-funding.
8. **`Programme budget 2026-27.xlsx`** — business_operations.budget-forecast without fund/award axis.
9. **`Scholarship application - Jordan Lee - personal statement.pdf`** — applications.scholarship-fellowship (individual applicant).
10. **`Funder guidance - eligible expenditure 2026.pdf`** — Reading Inbox exemplar.
11. **`Thank you for your gift.pdf`** (schema's own donation fixture) — fundraising-donor / finance by side; no report-back.
12. **`Trustee board minutes - 12 March 2026.pdf`** — business_operations; schema already concedes.
13. **A live grants-portal connector** — source system, not a file node; only a bounded export with a readable manifest is representable.

## The collision fixture

Headline: **`Community Trust - award letter 2026.pdf`**.

It looks like this row's evidence: award amount, restricted purpose, instalments, and — crucially — a printed no-goods sentence that also satisfies fundraising-donor's gate. fundraising-donor already named it as the shared fixture and assigned the conditional side here.

It is not this child's, because the child does not exist. What discriminates gift from grant is the reporting-and-reconciliation obligation. What holds the grant side is the nonprofit schema's restricted-grant default. Recording the fixture preserves the seam for R1c without padding an id.

Secondary collision: **`GT-2024-118 - Q2 claim and monitoring workbook.xlsx`** against government.grant-programme-administration — same bytes, side discriminator, already authored from the neighbour; this memo accepts and states it back with the child declined.

## Reciprocal boundaries (memo only; also_holds_with empty)

`also_holds_with` is empty by contract — template ↔ template is forbidden; schema ↔ schema only — and a refused template authors no coactivation licence. Boundaries for R1c, each naming one fixture both ways:

| Neighbour | Same fixture both sides | This refused row | Neighbour / real owner |
|---|---|---|---|
| `nonprofit.fundraising-donor` | `Community Trust - award letter 2026.pdf` | nothing (declined) | unconditional gift vs schema restricted-grant |
| `government.grant-programme-administration` | `GT-2024-118 - Q2 claim and monitoring workbook.xlsx` | nothing | funder side vs schema grantee side |
| `research.grants-funding` | `NOA - R01GM123456 - period of performance.pdf` | nothing | research money vs schema programme money |
| `legal` | `Grant agreement - REF GT-2024-118 - signed.pdf` | nothing | instrument vs schema lifecycle after signature |
| `business_operations.budget-forecast` | `Programme budget 2026-27.xlsx` | nothing | period plan vs schema award/fund reconciliation |
| `applications.scholarship-fellowship` | `Scholarship application - Jordan Lee - personal statement.pdf` | nothing | individual applicant vs organisational programme ask |
| `finance` | drawdown on bank statement beside claim workbook | nothing | custodial account vs schema partition |

## Neighbours considered that got no edge

- **`business_operations.contract-administration`** — a commissioned public-service contract is an exchange; the schema already routes it away. No same-evidence mutex with grant reporting beyond that.
- **`business_operations.partnerships-bd`** — sponsorship with valued benefits; fundraising-donor already owns that seam.
- **`hr`** — grant budgets naming post-holders may co-activate hr on the schema's also_holds_with; not this child's edge.
- **`nonprofit.member-association` / `religious-institution`** — no grant-lifecycle contact.
- **`nonprofit.governance` / `standards-body` / `volunteer-management` / `advocacy-campaign` / `political-campaign`** — already refused; no edge to a refused sibling.

## `proposed_fields`

None. The schema already proposes `organization`, `fiscal_period`, `sponsor`, and `subject_of_record` for R1c. Minting `grant_reference`, `award_number`, or `funder` here would be the synonym-mint the brief forbids, and a refused row must not enlarge the proposal surface. If R1c wants a destination-eligible award key, adjudicate the schema's existing `sponsor` / `fiscal_period` cluster once.

## NEEDS-JOSEPH

1. **NJ-GR-1 — inherited edges.** Retarget fundraising-donor and government.grant-programme-administration collisions from this id to `nonprofit`, leave documented aliases, or reverse the refusal with new residue. Preference: retarget to schema.
2. **NJ-GR-2 / NJ-NP-2 — research fork.** Unchanged by this refusal; still needs one reciprocal discriminator between research.grants-funding and the nonprofit schema.
3. **NJ-GR-3 / NJ-NP-4 — projected template list.** Drop or rename "grant-funding-received" on the schema's defensible list, or narrow the schema signal before minting a child. Do not pad.

## Final recommendation

Keep `refuse_node: true`. Do not invent a child to save the id. Recipient-side grant reporting remains covered by the nonprofit schema's restricted-grant default, with residual routing as written, and with neighbour seams preserved as recommendations for R1c.
