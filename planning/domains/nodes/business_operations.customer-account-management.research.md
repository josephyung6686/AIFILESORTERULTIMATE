# business_operations.customer-account-management — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`business_operations.json`, `career.consulting-client-engagement.json` (where `00`'s `our_firm` /
`client` role split lives), `creative.client-engagement.json`. Legacy row absorbed per `ROSTER.md`
Appendix A line 825: `ops.customer-success` (ROW).

## What it is for, and what it holds

Managing an **existing named customer relationship after the sale**. Account plans and stakeholder
maps, onboarding and success plans, periodic business reviews, usage and adoption records, health and
churn assessments, escalation summaries, renewal preparation and expansion proposals, customer meeting
notes, feedback exports, reference and case-study material — and the customer's own material held
inside the relationship.

## Node test — passes, on the post-sale relationship

The anchor is **one customer as an ongoing relationship**. Detection signals differ from every
sibling: an account plan's named-stakeholder map with roles and sentiment, a co-branded periodic review
addressed to one recipient, a per-customer adoption or licence-consumption record, and a renewal
preparation sheet that combines a contract end date with an *internal* recommendation.

## The reason this row matters out of proportion to its size

It is the clearest case in the whole family where **the exposed party is not the user**. A stakeholder
map, a contacts export, a usage record with named end users and a customer's own confidential strategy
document are third parties' personal data and third parties' commercial secrets sitting on the
holder's machine, and none of those parties can consent to what the product does with them. `00`'s
contacts rule is quoted directly on the row for that reason. It is also why `Protected Records` is the
row's first fallthrough rather than its last.

## Files considered and rejected

- **`QBR template - blank.pptx`** — kept as the collision fixture.
- **`Acme - company strategy 2026.pdf`** — kept deliberately, because a third party's confidential
  document held in a relationship is the row's most important and least obvious member.
- **`acme-contacts.vcf`** — kept as the contacts fixture, where `00` states the rule outright.
- **A signed order form** — dropped; it is the contract sibling's, and the renewals-forecast fixture
  already carries that seam.
- **A support ticket export** — left as a `collides_with` against
  `business_operations.support-operations` rather than a file example.
- **A win/loss analysis** — considered and dropped: it is pre-sale, and the row is explicitly post-sale.

## proposed_fields

**None minted, and the hole is named.** The **customer** role has no canonical key. `00`'s pair is
`our_firm` / `client`, which is the professional-services reading; a subscription customer is a related
but distinct role and a supplier is a third. Whether `client` should widen or whether a `role_split`
sibling is needed is R1c's call, and it interacts with the identical hole on
`business_operations.contract-administration`.

## Neighbours considered that did NOT get an edge

- **`business_operations.market-research`** — voice-of-the-customer and NPS material sits in both.
  Left unedged because the `go-to-market` and `partnerships-bd` collisions already carry the commercial
  cluster's discriminators, and a fourth would be true and useless.
- **`hr`** — account teams and named internal owners appear on every artifact here. Not edged; the
  whose-record-is-it discriminator is the schema row's.
- **`nonprofit.fundraising-donor`** — donor stewardship is structurally the same situation with a
  different owner type. Genuinely close; noted for R1c rather than guessed.

## NEEDS-JOSEPH

- **NJ-BO-9 (shared with the contract row) · No canonical key for the customer or supplier role.**
- **NJ-BO-11 · Is a CUSTOMER-named folder acceptable in v1?** It is how people in this role really
  file, and it discloses the relationship, its commercial state, and by aggregation the holder's whole
  book. Provisional posture: a user-approved customer level with no automatic depth.
- Carries **NJ-J-IND-4** in its sharpest form — this row's material is third-party confidential by
  default and no safety flag reaches it.
