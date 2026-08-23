# construction_property.compliance-certificate — gist research memo

Depth: GIST
Row: `construction_property.compliance-certificate` · kind `template` · schema `construction_property`
· launch `placeholder` · **REFUSED** · absorbs and retires the legacy row `trade.compliance-certificate`.

## Verdict

**`refuse_node: true`.** The dispatch flagged this row as possibly a document *type* rather than a
filing world. Applying the node test honestly, it is — and it is also, in its second half, a
residual.

## The test, leg by leg

| Leg | Result |
|---|---|
| Recommended dimensions differ from the schema default? | **No.** A certificate wants property → instruction → function, which *is* the family default. Empty in any case, since the schema declares no fields. |
| Privacy rules differ? | **No.** Address plus a named installer or occupier — identical to every sibling on this schema, already covered by the schema's `potentially_sensitive`. |
| Detection signals differ? | **The only leg with a case, and it does not hold.** |

The third leg in full: the candidate signal is *scheme or standard + installation address +
installer registration + signed declaration*. Strip it to what would actually have to fire and two
things remain — a **document-type word** and an **address**. Both are constitutionally never-alone:
the address on `00`'s own university-name reasoning (which the schema row makes this family's
governing never-alone), the word because certificates are a `work_type` **value**, and CONNECTION §9
lists work types as schemas among the failure modes forbidden by construction. A row whose entire
support is never-alone evidence cannot clear activation (CONNECTION §4 step 2). It would never fire.

What remains of the candidate signal — the certified-declaration structure — is real, and it is
**already authored where it belongs**: on the `construction_property` schema row's own deterministic
list. It makes the *schema* plausible. It does not name a *situation*, because the situation is
always whichever job, application, block or household the certificate evidences.

## The deciding evidence: the coverage is already carried three times

- Landed `finance.household-property` lists **"completion or compliance certificate"** and
  **"property-system warranty"** among its own `work_types`.
- The `construction_property` schema row lists **"installation or compliance certificate and test
  record"** among its `work_types`.
- `construction_property.building-control` owns the **authority-issued** completion certificate
  under an application reference.

A fourth authoring of the same documents is one concept in four places — the defect this roster pass
exists to remove.

## And the framing is a residual's framing

The roster hint's own words are "the document that has to be produced years later" — a durable
standalone record with no broader group. `00` answers that by name, and names certificates first:
Independent Records holds *standalone certificates, notices, confirmations, forms, and PDFs that
have a durable purpose but no broader group*. A row built on that framing is a residual wearing a
domain's clothes (`_CONTRACT` rule 6; CONNECTION §2; failure mode 6 in §9).

## Where the coverage goes — four routes, all stated in the JSON

1. **Authority completion / final certificate** → `construction_property.building-control`.
2. **Installer's declaration inside a job** → `construction_property.construction-project`
   (handover pack is one of its `work_types` and one of its `grouping_reasons`).
3. **Recurring compliance evidence for a managed building** →
   `construction_property.block-management`.
4. **A householder's own certificate** → landed `finance.household-property`.
5. Anything left over → **Independent Records**, by design rather than by omission.

## Files considered

Eight are kept in the JSON specifically because each one shows the id was a label: an EICR, a gas
safety record, an EPC (which is a *sale and letting* document far more often than a build one), an
authority completion certificate that shares only a filename with an installer's, a structural
warranty that is really insurance, a photographed certificate, a handover pack (the clearest case —
the pack is the group and the job is the situation), and a fire-door inspection schedule that
belongs to a managed block.

Rejected as examples: asbestos registers and fire-risk assessments, because they are
`block-management`'s recurring evidence rather than one-off declarations, and including them would
have made the refused row look broader than it is.

## Neighbours considered that did NOT get an edge

None were authored at all. A refused row must not carry `collides_with` or `also_holds_with` edges:
the edges would name a node that does not activate, and R1c would then owe reciprocals to nothing.
Every real boundary this row touches is stated on the rows that survive.

## NEEDS-JOSEPH (this node only)

- **Routing confirmation for R1c** (in `open_question`): verify all four routes above actually
  landed on their target rows. Three of the four are rows I own and do state it; the fourth
  (`finance.household-property`) already did before this pass.
- If R1c overturns the refusal, the minimum honest form is a detection-signal-only row on the
  certified-declaration structure — but that signal identifies a *schema*, not a *situation*, and is
  already on the schema row.
