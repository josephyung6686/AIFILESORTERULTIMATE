# business_operations.support-operations — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.project-delivery.research.md`; all quotations
machine-verified verbatim against `00-database-agent-product-design.md`. Landed siblings read for key
set and idiom: `business_operations.json`, `business_operations.it-asset-inventory.json`,
`legal.practice-matter-file.json` (read specifically for the matter-register collision, and its posture
respected rather than overridden). Legacy rows absorbed per `ROSTER.md` Appendix A lines 695 and 826:
`ops.support-operations` (ROW), `soft.helpdesk-ticket` (FOLD).

## What it is for, and what it holds

An organisation runs a desk that answers the people who use its product or service, and the desk
generates a continuous stream of records about it. The row holds ticket and case exports, individual
case threads, service-level and queue reporting, knowledge-base and macro content, escalation matrices
and on-call rotas, satisfaction exports, customer-supplied screenshots and log excerpts, and session
recordings.

## Node test — passes

The anchor is a **continuous queue of third-party interactions**, which nothing else in this family has —
every sibling is organised around a bounded effort, a standing cycle, or one named counterparty. The
detection shape (identifier + requester + status + agent in one header row) is close to unique, and the
**privacy rule is different in a way that changes the template**: this is the only row in the family whose
`template.why` refuses a dimension outright (per-customer), on 00's collector prohibition.

## Files considered and rejected

- **`matters_open_2026.xlsx`** — kept as the collision fixture, and chosen over the more obvious CRM export
  because the harm is larger: a legal caseload read as a helpdesk queue.
- **`csat_responses.csv`** — kept because it makes a point no other example makes: a customer-facing export
  is *simultaneously* unsolicited written commentary on named employees.
- **`session_recording_88214.mp4`** — kept because a support screen-share can show the customer's own inbox
  and credentials, which is the sharpest exposure in the row.
- **A chat-widget transcript** — rejected as an example; it is the case thread in another container and adds
  nothing at gist depth.
- **A community-forum export** — considered and left out: publication changes the privacy analysis enough
  that it would need its own treatment, and it is rare in a personal corpus.

## proposed_fields

**None.** The natural anchor would be the product or service supported, and the counterparty concept is
already covered by the canonical `client` / `our_firm` role pair. A `ticket_id`-style key was considered and
**rejected outright**: a per-case identifier is a *record-level* value, it is never a folder dimension, and
minting it would license exactly the per-customer aggregation this row refuses. The schema row's proposed
`organization` and `fiscal_period` cover what remains; not restated here.

## Neighbours considered that did NOT get an edge

- **`business_operations.product-requirements`** — support feedback becomes requirements, but the edge runs
  through `user-research`, which already carries it. Not tripled.
- **`medical` / `clinical_practice`** — a clinical caseload is another identifier-plus-person table. Left
  unedged **deliberately**, for the same reason as on the risk row: an edge authored from here toward
  protected material is the wrong direction. The `legal.practice-matter-file` edge carries the lesson.
- **`finance.subscriptions-utilities`** — a consumer's own support correspondence with their utility is the
  mirror image (the holder is the *requester*). Genuinely interesting and left as an open question rather
  than an edge, since it is a household row owned by another agent.

## NEEDS-JOSEPH

- **NJ-BO-SO-1 · Internal service desk vs external customer support.** The roster folded
  `soft.helpdesk-ticket` here and the shapes are identical, but the requesters differ — colleagues on one
  side, customers on the other — and the privacy consequence differs with them. Fold kept on detection
  grounds; doubt recorded.
- **NJ-BO-SO-2 · What may a bulk export of named third parties do at all?** This row states that it must not
  acquire a per-customer branch. Whether such a file should be organised, merely *represented* without
  moving, or left untouched entirely is a P7/P10 policy question that this catalogue cannot and should not
  answer.
- **NJ-BO-SO-3 · The holder as requester.** A person's own support correspondence with a supplier looks like
  this row's material from the wrong side. No edge authored; R1c should decide whether the household mirror
  is stated.
