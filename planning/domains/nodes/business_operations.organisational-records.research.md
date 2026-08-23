# business_operations.organisational-records — lab notes (REFUSED template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Verdict

**`refuse_node: true`.** A refused node is a success; inventing a schema or a situation to save an id
is the 574's failure, and this id is a label rather than a situation.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md` (rules 6, 10, 11, 15), `CONNECTION.md` §2 (the node test), §4 step 2 (the never-alone
rule), §5 invariant 5, §9 failure mode 6, `roster.json`, `DECISION-BRIEF.md`, `ROSTER.md` §4 +
Appendix A line 804 (`ops.business-records` → this id).

## The argument, compressed

The roster hint defines the row as material that "carries an organisation and a document type but no
more specific operational sub-domain". That is not a description of an organizational situation. It is
a description of the **absence** of one, which is precisely what 00 gives the residual library to hold.

Three independent failures, any one of which is sufficient:

1. **No detection signal that is not never-alone.** Its only candidate evidence is an organisation name
   plus a document-type word. An organisation name alone is struck at activation step 2 by the same
   reasoning 00 gives for a university name — role ambiguity — and a document-type word is a value of a
   document-function field. A row whose entire support is never-alone evidence **can never fire**.
2. **Node test, both remaining legs.** Dimensions identical to the schema's default (and empty in any
   case under PR-6); privacy rules identical. ALIGNMENT: a template that repeats its schema's fields and
   dimension order is the schema's default template, not a node.
3. **It is a residual wearing a domain's clothes.** `_CONTRACT.md` rule 6 and `CONNECTION.md` §2 keep
   residual homes out of this namespace entirely — they are P10/P11's nine names. Building this row
   would be `CONNECTION.md` §9's failure mode 6 in its purest form.

## Where the coverage actually goes — nothing is dropped

- The **`business_operations` schema's own default template** covers anything that legitimately
  activates the schema without a sibling situation firing. That is what a schema default template is
  *for*, and it is the reason a branch-root template row is redundant rather than merely weak.
- **`Independent Records`** is the broad destination when nothing reliable lands — its 00 definition is
  almost word-for-word this row's job description.
- **`Review Later`**, **`Protected Records`** and **`Unsupported or Encrypted`** carry the ambiguous,
  the personal and the unreadable cases respectively.

All four are authored on the row as `falls_through_to`, so the refusal is connected rather than a hole.

## Files considered — and what they showed

The eight examples in the JSON were chosen to demonstrate the refusal rather than to describe a
situation. Six of the eight (`Certificate of incorporation`, `Org chart`, `Employee handbook`,
`Company letterhead template`, `Business card scan`, `Misc work stuff.zip`) turned out to have a real
home elsewhere the moment they were looked at — `corporate-regulatory-filings`, `hr.org-design-headcount`,
`policy-handbook`, `creative.brand-identity`, contact-privacy handling, and per-member extraction. The
two that did not (`Acme Ltd - company profile.pdf`, `Scan_20260218.pdf`) are exactly the files 00 sends
to a residual home. That distribution **is** the finding.

## Edges

None authored. `collides_with` joins same-kind pairs and asserts an evidence-item mutex; a row that
never activates cannot be one side of a mutex, and authoring edges from a refused row would leave R1c
reconciling reciprocity against something that does not exist. Only `falls_through_to` is written,
because that is the statement of where the material really goes.

## proposed_fields

**None**, and the refusal makes the question moot.

## NEEDS-JOSEPH

- **NJ-BO-4 · Was something narrower meant?** There is a real, coherent pile this refusal might be
  throwing out with the branch root: the **corporate identity documents of an entity a person owns or
  administers** — incorporation certificate, constitution, share register, registered-office notices.
  Today that splits across `business_operations.corporate-regulatory-filings`,
  `business_operations.board-governance` and `finance.cap-table-equity`. If that is what the id was
  reaching for, the honest fix is a **new narrow row named for that situation**, not the reinstatement
  of a branch root. This agent did not mint one: creating a replacement roster id is outside what a
  single node agent may do.
- **NJ-BO-5 · Confirm the legacy fold.** `ops.business-records` is retired here rather than rebuilt.
  ROSTER.md §4 counts it as a 1:1 row; that arithmetic changes if this refusal is accepted, and R1c
  should recount rather than let the table drift.
