# business_operations.contract-administration — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`business_operations.json`, `legal.leases-agreements.json`, `career.consulting-client-engagement.json`.
Legacy row absorbed per `ROSTER.md` Appendix A line 823: `ops.contract-administration` (ROW). Note
that `ops.client-engagement` folded to `career.consulting-client-engagement`, not here, and that
boundary is respected by an authored collision rather than reclaimed.

## What it is for, and what it holds

Running a contract **after** it is signed. The register of what is in force, the obligations and
service levels it created, the notice and renewal dates that must be diarised, the variations that
amend it, the performance reports that test it, and the correspondence that manages it to expiry.

## Node test — passes, on the signature

The anchor is a **live obligation and its calendar**. The single most characteristic detection signal
is the **notice-date column** in a register table — it appears in no other family's tables, and it is
the cleanest evidence in this chunk that the situation is distinct from both the instrument and the
negotiation. Obligation trackers, formal notice letters with clause references, and contract abstracts
are produced by this function and by nothing else.

The instrument itself stays with the legal family; a single executed PDF with a manuscript renewal note
on the cover is genuinely both, and that is `collides_with`, not a defect.

## Files considered and rejected

- **`NDA template - mutual.docx`** with tracked changes — kept as the collision fixture. A template and
  a redline are negotiation artifacts, not administration ones.
- **`Employment contract - signed`** — kept as the second fixture. The shape matches perfectly and the
  counterparty is a person; the stricter side wins.
- **`PO-2026-0331.pdf`** — kept because it is honestly three rows at once (procurement's output, this
  row's call-off evidence, an accounting document) and the row should not pretend otherwise.
- **An insurance certificate held under a contract** — real, kept as a `work_type` rather than an
  example, because `finance.insurance-corporate` has landed and owns the artifact.
- **A signing-platform audit trail** — considered; it is a receipt of execution, and the row already
  carries the archive and receipt fallthroughs.

## proposed_fields

**None minted here, and the hole is named.** The **supplier / buying-side** role has no canonical key.
`00`'s pair is `our_firm` / `client`, which covers the professional-services reading; a buy-side
register's counterparty is a third role. This is the clearest place in the family where a `supplier`
key would be proposed, and this row deliberately does not mint one — it goes to R1c with the
`customer-account-management` sibling's parallel case.

## Neighbours considered that did NOT get an edge

- **`retail_hospitality.catering-contract`** and **`retail_hospitality.supplier-order`** — sector
  instances of the same situation. Left unedged; the `construction_property.subcontract` collision
  already carries the sector-statutory-regime discriminator once.
- **`logistics.shipment`** — carrier terms and consignment contracts. Same reason.
- **`finance.subscriptions-utilities`** — a personal subscription is a contract with a renewal date and
  is structurally near-identical. Not edged, because it is a *personal* record and the schema row's
  `career` / `finance` collisions already carry the whose-record-is-it discriminator; noted for R1c.

## NEEDS-JOSEPH

- **NJ-BO-8 · The buying-side role has no canonical key.** Widen `client`, or add a `role_split`
  sibling? For R1c; it interacts with NJ-BO-9 on the customer row.
- **NJ-BO-9 · Are `contract-administration` and `vendor-management` genuinely two situations?** Their
  detection signals overlap more than any other pair in this family. The honest reading is
  contract-anchored versus relationship-anchored, which is thin enough that R1c should confirm it
  rather than inherit it.
