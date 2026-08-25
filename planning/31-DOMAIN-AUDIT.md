# Domain map and cohesion audit

Date: 2026-08-25
Status: **inventory and integrity audit complete; cohesion gaps are recorded, not silently repaired.**

## Inventory

- Roster IDs: **358**
- Node JSON files: **167**
- Missing/unwritten roster rows: **191**
- Schema anchors: **23**
- Templates: **144**
- Every node JSON has a paired research memo.
- No duplicate node IDs and no node files outside the roster.

Template coverage by schema:

| Schema | Templates |
|---|---:|
| academic | 11 |
| business_operations | 24 |
| career | 6 |
| clinical_practice | 10 |
| code | 5 |
| college_applications | 5 |
| construction_property | 27 |
| creative | 10 |
| finance | 18 |
| identity | 3 |
| legal | 4 |
| medical | 3 |
| photos | 9 |
| research | 9 |

The newer anchors `engineering`, `government`, `hr`, `law_practice`, `logistics`,
`manufacturing`, `nonprofit`, `resource_operations`, and `retail_hospitality` currently have
no landed child templates. That is expected under schema-first ordering, not a missing reciprocal.

## Integrity findings

- Node IDs are unique and all roster-backed.
- Schema/template relationships resolve.
- Cross-file edge checking found no dangling node IDs. Two `hr` references are the residual
  labels `Protected Records` and `Independent Records`, not node IDs.
- Ownership register has 12 claims: 8 complete and 4 active; no duplicate ownership claims.
- `planning/domains/check.py`: **566 legacy in-file problems, 0 cross-file problems**. The legacy
  failures are primarily dimensions branching on undeclared fields; they are not being rewritten
  as part of this audit.

## Cohesion gaps requiring follow-up

1. **Universal-key drift.** 57 node rows omit `proposed_context_terms`; 46 rows carry additional
   explanatory keys such as `node_test`, `*_note`, or `privacy_rules`. The content is often useful,
   but the serialized node shape is not uniform. Resolve by choosing one contract and migrating in
   a dedicated schema-shape pass, not by ad hoc row edits.
2. **Memo-depth marker drift.** 87 existing memos do not contain a literal `J-DEPTH` marker in
   their first eight lines. Some may use older equivalent depth wording; a migration should
   distinguish genuinely shallow rows from header-only drift before changing verdict content.
3. **Coverage gap.** 191 roster rows remain unwritten. Continue schema-first, then author child
   templates under each landed anchor. Do not claim the forest is complete until roster coverage is
   358/358.
4. **Semantic merge seams.** The landed memos repeatedly flag cross-region decisions—creative/legal/
   finance rights, manufacturing/resource operations, HR/career, clinical/career credentialing,
   and construction/logistics. These are recorded as reciprocal edges and NEEDS-JOSEPH items, but
   they still require an R1c merge decision before they can be called resolved.

## Operating rule for the next waves

Agents must own one roster ID at a time, claim it in `planning/29-DOMAIN-OWNERSHIP.md`, write only
that ID's JSON and memo, and run the row-level checks before reporting completion. No source/test/docs
changes, shared-file edits, stash, rebase, pull, or reset are allowed while the other workstream's
working tree is dirty.
