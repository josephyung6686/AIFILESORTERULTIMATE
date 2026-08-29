# construction_property.service-charge — deepening memo

Depth: J-DEPTH. Placeholder row, `fields: []`.

**Verdict: REFUSE.** This reverses the gist verdict. Service-charge files form a real documentary
cycle, but the cycle is already an explicit signal and work-type family of the deepened
`construction_property` default. What remains differs from invoices, tenancy records and facilities
accounting only by property/tenant role values and billing-stage `work_type` values.

---

## Sources actually used

Binding sources: `planning/00-database-agent-product-design.md`, `ALIGNMENT.md`, `_CONTRACT.md`,
`CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `canonical_fields.json`, the roster entry, and the stamped
output of `make_prompt.py construction_property.service-charge`. The row was measured first against
the deepened `construction_property` anchor. Comparisons were
`construction_property.tenancy-management`, `business_operations.facilities-workplace`,
`finance.household-property`, `finance.receipts-expenses`, and
`finance.small-business-bookkeeping`. The shallow draft was preserved where correct.

## Why the gist premise no longer holds

The old memo claimed that a cost table split by fixed unit shares existed nowhere else in the catalogue.
The deepened schema anchor now explicitly recognises that apportionment structure and names
service-charge budget, apportionment schedule, demand and reconciliation in its default work-type
vocabulary. Under CONNECTION the schema row is also the family default template. A child must differ
from it in signal, dimensions or privacy; repeating the inherited structure is not a difference.

The estimate-to-reconciliation sequence remains a sound real-world observation: estimated costs lead
to demands, actual expenditure and a balancing charge or credit. But at schema level this is exactly
the inherited apportionment/reconciliation structure; at Finance level it is billing, receivable and
accounting material contextualised by a building; at tenancy level it is one charge stream in an
account relationship. *Service charge*, *budget*, *demand*, *account* and *balancing statement* are
values. They cannot do the work of a node.

## Node test, leg by leg

### Detection — fails by duplication and subtraction

The positive cycle is:

`estimated building costs -> unit apportionment -> demands -> actual costs -> reconciliation`.

Its main roles are manager/freeholder, building or scheme, leaseholder/unit, contractor/supplier and
accountant. Subtract the default's apportionment structure and work types, and the proposed child has
only property and party values, money/date observations, invoice/account structures and billing-stage
values. Each is never-alone, undeclared, or `work_type`.

A two-role relation does not rescue it. Landlord/tenant is tenancy-management's relation;
issuer/customer is Finance; facilities provider/occupier is facilities-workplace. If roles are clear,
a named situation owns them. If unclear, an address and money table cannot activate a narrow row.

### Dimensions — fails exactly

The schema declares no fields, so both the default and this row require `dimension_order: []`. The
old draft kept its desired building -> service-charge period -> stage order only in prose. Building,
property, unit, tenant and accounting period are not legal destination fields here, and billing stage
is only a work-type value. A template cannot open levels no fact can populate.

Even if shared property and reporting-period keys later land, the schema anchor already recommends
property/site -> instruction -> document function, adding a period where the situation cycles and
explicitly citing service-charge year. The proposed order is the default instantiated with values.

### Privacy — fails to differ

Arrears schedules and disputes can expose resident names, exact addresses, unit numbers, balances,
recovery notes and neighbour positions. That warrants `potentially_sensitive` and protected
fallthrough. It does not distinguish this child: the anchor and tenancy neighbour already cover the
same tenant, address, payment and dispute material. Protection attaches through P7 and independently
active safety schemas. Refusal does not weaken it.

## Bottom-up fixtures

The JSON retains ten files:

1. `Service charge budget 2026-27 - Halstead Court.pdf` — estimates, reserve contribution and unit
   shares; evidence for the schema default, not a child.
2. `Demand - Flat 12 - half year to September.pdf` — amount, due date, unit and rights text;
   invoice/receipt-adjacent and no proof of payment.
3. `Certified accounts - year to 31 March 2026.pdf` — estimate/actual comparison, balancing figure
   and certificate; its reporting period is not automatically `tax_year`.
4. `Arrears schedule - March.xlsx` — the privacy fixture; named balances are observations, not
   permission to expose people or declare every amount owed.
5. `Notice of intention - roof replacement.pdf` — proposed rather than completed work, with an
   independent legal reading.
6. `Facilities recharge invoice - West Tower - Q2.pdf` — hostile false positive: shared-cost billing
   exists for an occupied workplace.
7. `Rent and charges statement - 18 River Court.eml` — tenancy/Finance collision; line labels do not
   create separate template activations.
8. `service-charge-pack.zip` — purpose-coherent grouping without member-fact propagation.
9. `Ground rent demand - Flat 12.pdf` — different charge with identical party, premises and due
   fields, proving those values cannot distinguish this row.
10. `IMG_4412.jpg` — sparse OCR; nearby accounts must not copy tenant, unit, period or purpose.

Universal facts remain legal. No construction-property facts are written because its schema declares
none. `also_schema` marks independent schema plausibility on bytes; it does not create template-level
`also_holds_with`, which CONNECTION reserves for schema pairs.

## Files considered and rejected

- A signed lease extract: protected Legal instrument, not a demand.
- A managing agent's contractor invoice: possible bookkeeping input; it becomes no leaseholder
  demand until an apportionment relationship is shown.
- A bank payment confirmation: transaction proof, not proof of the charge's legal character.
- A generic property-management article: reading material, not a completed holder record.
- A blank budget template: headings and formulas without filled roles prove no situation.
- Tribunal papers: independently protected legal dispute material.
- A roof specification: works-lifecycle material; later cost recovery does not change its function.
- A residents' meeting minute: governance may discuss a budget, but topic is not billing structure.
- Ground-rent demand and facilities recharge were retained as opposing collision fixtures.

## Reciprocal boundaries and neighbour recommendations

No neighbour file was edited and no mutex edge is authored from a refused node. Recommendations:

- **Construction-property default.** Shared bytes are the annual budget, apportionment, demand and
  reconciliation. Default -> refused child: keep these as default work types/group stages. Child ->
  default: all former positive signals already belong there. R1c should preserve the anchor signal
  and make the refusal discoverable.
- **Tenancy management.** Shared bytes: `Rent and charges statement - 18 River Court.eml`. Tenancy ->
  child: landlord/tenant account and tenancy reference organize the set; service-charge is a line
  value. Child -> tenancy: a whole-building budget is not a tenancy account merely because units are
  named. Recommend explicitly striking per-charge child activation.
- **Facilities/workplace.** Shared bytes: `Facilities recharge invoice - West Tower - Q2.pdf`.
  Facilities -> child: occupied-premises shared services remain facilities operations. Child ->
  facilities: landlord apportionment among leaseholders is not an organisation running its own
  workplace. Recommend holder role/instruction as the seam, never cost headings.
- **Household property.** Shared bytes: the Flat 12 demand. Household -> child: an isolated owner's
  demand is a property-lifecycle or transaction record, not a manager-side branch. Child -> household:
  a whole-building apportionment and manager arrears schedule are not one household's records.
  Recommend retaining professional instruction versus holder's-own-property; never portfolio size.
- **Receipts/expenses.** Shared bytes: the demand or paid confirmation. Receipt -> child: invoice id,
  amount, due date and payment status are transactional. Child -> receipt: aggregate budget and
  apportionment are not receipts. Recommend residual/group membership for isolated demands and never
  infer paid status from a demand.
- **Small-business bookkeeping.** Shared bytes: certified accounts and facilities recharge invoice.
  Books -> child: invoices, receivables and reconciliations belong to working books when operation
  role is evidenced. Child -> books: an accountant-certified building account held by a leaseholder
  is not the holder's business book. Recommend issuer/holder role evidence; property words and
  accounting-software metadata count for neither.

## Fields, work types and residual coverage

`fields: []`, `proposed_fields: []`, and `work_types: []` are deliberate. No key is minted. Plausible
future dimensions—property/building, reporting period, unit/tenancy—are shared-vocabulary questions;
billing stage is a value. The refused row owns none privately.

Standalone demands and confirmations fall through to Receipts and Confirmations; durable budgets and
accounts to Independent Records; named arrears material may require Protected Records; ambiguity goes
to Review Later; unreadable packs remain Unsupported or Encrypted. Every file survives the refusal.

## NEEDS-JOSEPH

- **NJ-CP-SC-1 — shared subject and period vocabulary.** Should shared property/asset and operational
  reporting-period keys be added across construction-property, tenancy, facilities and Finance?
  Either choice changes grouping/display, but cannot rescue this row because the default owns the
  cycle and billing stage remains a value.
- **NJ-CP-SC-2 — refused-id discoverability.** Should R1c retain refused ids as aliases/explanations
  so a search for service charge points to the default plus Finance/residual options? Silent removal
  harms discovery; activation recreates the duplicate. This is a merge/UI choice, not an exception.

## What changed in this pass

- Reversed `refuse_node: false` to `true` after the deepened anchor invalidated the uniqueness claim.
- Replaced child recognition with the finding that the cycle detects only the default.
- Removed child context terms and work types, which were values masquerading as a node.
- Preserved ten concrete fixtures and safe residuals; documented reciprocal recommendations only.
- Kept `fields: []`, proposed no keys, and surfaced two Joseph decisions.

## Validation

JSON parse, exact 27-key shape, header/end marker, source types, roster schema ids, residual names,
quote matches and JSON/memo agreement were checked. Only the two assigned files changed.

**END — construction_property.service-charge — REFUSE**
