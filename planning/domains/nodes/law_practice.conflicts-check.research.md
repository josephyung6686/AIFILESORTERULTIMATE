# Research memo — `law_practice.conflicts-check`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.conflicts-check.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch
Absorbed legacy id: `law.conflicts-check` (ROSTER.md §4 Appendix A, line 612 — ROW, not FOLD)

## Result

**Accept**, narrowly, and only after conceding that the larger and more obvious half of this row's
subject matter is already the schema's own activation signal. The row survives on the two artefact
shapes the `law_practice` default template structurally **cannot see**, on an inverted grouping rule,
and on a sensitivity argument that reaches three subjects the schema's own argument does not reach.

## The charge, stated at full strength before anything else

This row is a strong refusal candidate and I put the case against it first.

**Charge 1 — it is a duplicate of its own schema's default template, in the schema's own words.**
This is the serious one. `law_practice.json`'s second deterministic signal opens:

> "AN INTAKE-AND-CONFLICTS structure, and it is the family's cleanest signal because `legal`'s
> signals do not fire on it at all"

The schema anchor does not merely tolerate conflicts evidence — it names it *the family's cleanest
signal*, carries `Conflict search - Hartley acquisition - CLEARED.pdf` as one of its own
`file_examples`, and lists `conflict check`, `conflict search` and `conflict clearance` in its
`proposed_context_terms`. A template whose detection signals are its schema's *primary* activation
signals is, on the face of it, exactly what CONNECTION.md §2's node test refuses.

**Charge 2 — it is a duplicate of a sibling.** The schema's `work_types[]` contains the single value
`"client intake, identification and conflicts screen"`. The roster splits that one value across two
rows: `law_practice.client-intake` and this one. Splitting one enum value into two nodes is the 574's
signature error.

**Charge 3 — it is a lifecycle stage.** "Before the matter opens" is a *stage*, and the brief names
lifecycle stages as a disqualifier. `law.document-review` and `law.ediscovery-production` were FOLDed
into `law_practice.discovery` on exactly that reasoning ("review work product and productions are
stages of one disclosure exercise"). Intake → conflicts → engagement → matter is the same sequence.

**Charge 4 — its dimensions and privacy are identical to the schema's.** `dimension_order: []` and
`sensitivity: potentially_sensitive` on both. Two of the three legs look like a copy.

**Charge 5 — never-alone evidence only.** The word "conflict of interest" is used identically by
boards, auditors, procurement panels, journals and HR. If the row's evidence is that word plus a
firm name, it is two struck tokens and can never activate.

Charges 4 and 5 I defeat below. Charges 1–3 I defeat only **partially**, by shrinking the row: I
concede the clearance certificate to the schema as an activation fixture, concede the intake half to
the sibling, and keep the row on what is left. If the reader disagrees that what is left is
structural, the honest verdict is refusal — so I state exactly what is left and why it is not a stage.

## Node test, three legs, argued separately

### Leg 1 — detection signals differ from the schema's default

The schema's default is explicit that activation requires **both** legs:

> "(i) an exact matter, file or engagement reference repeated across two or more artefacts, and (ii)
> at least one artefact whose own labelled slots separate a PRACTITIONER OR FIRM role from a CLIENT
> role"

Two of this row's characteristic artefacts break one leg each, by construction, not by accident.

**(a) The prospective-client screen breaks leg (i).** A conflicts search happens *before* a file
reference exists. `Conflict search request - Hartley acquisition - 2026-08-11.pdf` has a labelled
`Prospective client` slot and **no matter number anywhere on the page**. Where the search is declined
or the enquiry lapses, no matter reference is ever created — the record is of a matter that does not
exist. The schema default, applied to that corpus, looks for the repeated reference and finds
nothing. A row whose characteristic file is the one its schema's first leg cannot reach is not a
stage of that schema's workflow; it is outside it.

**(b) The information barrier breaks leg (ii).** `Information barrier memo - Project Kestrel -
screened personnel.docx` has a screened-matter slot, a list of the holder's **own colleagues**, an
access-restriction instruction and an effective date. Its two labelled roles are practitioner
against practitioner. There is no client slot on the page. Nothing else in the 36-row family holds
it, and the schema's own second leg does not fire on it.

**(c) The cross-matter citation inversion.** The schema's `never_alone` strikes "MATCHING PARTY
NAMES, SUBJECT MATTER, CITATIONS or SEMANTIC SIMILARITY ACROSS TWO MATTERS" — cross-matter bridging
is suppressed family-wide as a privacy rule. On a hit report the cross-matter match is the
**document's own declared content**, inside a labelled `Matched in / Matter reference / Disposition`
result table the document supplies. The product reads a slot; it never performs a match. This is the
one row in the family where the suppressed pattern is legitimate evidence — a rule reversal, which
is a signal difference in the strict sense, not a new vocabulary token.

Both structures land through `00`'s direct-fact path — deterministic extractors create direct facts
when the source is explicit, "such as a content hash, EXIF timestamp, a document title, or a labeled
form field" — and its table path: "Tables matter because resumes, forms, applications, invoices, and
administrative documents often place their most useful information in cells rather than body
paragraphs." Both spans grep verbatim out of `planning/00-database-agent-product-design.md`
(lines 41 and 29).

Against **Charge 3**: a stage inherits its parent's evidence and adds only sequence. This row's two
characteristic artefacts *lack* the parent's evidence. `law_practice.discovery`'s FOLDed members
(review logs, production sets) all carry the matter reference and the two-role structure; they were
correctly folded. These do not.

### Leg 2 — recommended dimensions differ

Both arrays are empty under PR-6, so the comparison must be made on the **prose recommendation**, and
the schema anchor demands exactly that: it calls its own paragraph "the paragraph every one of the 36
templates must differ from." Its prose is *client (only if approved) → matter → function → period*.
This row inverts the top of it and suppresses two levels **affirmatively** rather than conditionally:

1. **The matter level is wrong here, not merely ineligible.** A cleared screen that never became an
   engagement has no matter to sit under. A hit report's decisive content names a *different*
   client's matter, so filing it under the prospective matter writes an unrelated client's identity
   into that folder. A barrier record filed inside the matter it walls off defeats itself.
2. **The prospective-client level is worse than the schema's client level.** The schema seeds its
   client level ineligible because it discloses a representation; a screening branch would name
   people the practice **refused**, a disclosure with no representation behind it to justify it. It
   is also `00`'s "create meaningless one-child levels" in the ordinary case, since most screens
   produce one document.
3. **What is left is function → period**, held as prose. This is the closest any row in the family
   comes to earning a time level — a register genuinely is chronological — and it still does not earn
   `time_first`, because a bare year folder of screening documents is unintelligible without the
   function level, on `00`'s rule read across that a work type "is meaningful only after the course is
   known", and because "For document and record domains, project, function, or subject usually comes
   before time because putting year first scatters related work across calendar folders."

A named third party — a searched counterparty, a surfaced existing client, a screened colleague —
may never be a folder level, against "The default posture must therefore be local-first and
data-minimizing." And the whole thing stays advisory: "The system recommends an order based on the
domain template, but the user can reverse, remove, add, or flatten dimensions." All four spans
grep verbatim.

**The grouping rule is the sharpest part of this leg.** The schema's grouping reason is "ONE MATTER
… joined by an exact repeated matter reference." This row's third grouping reason is an
**anti-grouping** rule: a barrier record must *not* be pulled into the matter it screens, even though
an exact matter reference invites it, because the record's entire content is that named personnel
must not reach that matter. Where the schema says *join by exact reference*, this row says *note the
reference, do not join*. That is a behavioural difference in P9, not a wording difference.

### Leg 3 — privacy rules differ

Same value (`potentially_sensitive` — the only strict value available in this phase), stricter rule,
on three subjects the schema's argument does not reach:

- **Plural disclosure.** The schema's rule is that the existence of *one* representation is
  disclosive. A hit report discloses several at once — it names the prospective engagement *and*
  cites existing clients and matter references from unrelated files. One document leaks a second and
  third representation into a context that had no business seeing them.
- **The non-client.** A declined record is about someone who never became a client. The schema
  protects "a client, an adverse party, a witness, a deponent, an accused, a child"; the declined
  enquirer is on none of those lists and is the most exposed subject in this row, because there is no
  representation to justify holding anything about them at all.
- **The colleague.** A screened-personnel list names the holder's own colleagues as excluded from
  something, inside a legal packet where no HR safeguard is watching, and a careless reader will
  attach an adverse inference the list does not carry.

Compounding: the register is a multi-subject list whose exposure scales with row count.

**Verdict: all three legs differ. Accept.** But see NJ-CC-1 — leg 3 arguably demands a *narrower*
posture than Protected Records currently offers, and I could not settle that from the design docs.

## Files considered and rejected

Naming what this row does **not** hold was the more useful half of the work.

- **`Conflicts policy and procedure v4.docx`** — a firm's written policy on how screening is done.
  Rejected: it names no prospective client, records no search, no outcome and no approver. It is the
  practice running itself, which the schema anchor explicitly excludes ("the firm running itself as a
  business"). Routes to `business_operations.policy-handbook` or `law_practice.precedent-bank`.
- **`Blank conflicts questionnaire - template.docx`** — the slots are structurally identical to a
  completed screen's, which is precisely this row's signal, so it is genuinely dangerous. Rejected:
  its party, date, outcome and approver slots are blank **by design** across the whole document. The
  schema anchor already reserves blank-slot precedents to `law_practice.precedent-bank`; authored as
  a `collides_with`.
- **`Legal opinion - conflict of interest - Hartley board.docx`** — an internal opinion about the
  *client's* conflict of interest. Rejected: the subject is the client's legal position, not the
  practice's ability to act. Belongs to `law_practice.opinions-advice`. This is the single easiest
  mistake to make on vocabulary alone.
- **`Client identification and verification - Hartley - passport.pdf`** — identity verification
  collected at intake. Rejected: it is collected *from* the prospective client for the practice's own
  record, which is `law_practice.client-intake`'s side of the boundary, and it independently carries
  Identity evidence.
- **`Access permissions review - DMS - 2026-Q3.csv`** — a list of people and the workspaces they can
  reach. Rejected: no screened matter, no screening episode, no effective date; it is an IT asset
  and access record (`business_operations.it-asset-inventory`). Only the presence of a *screened
  matter* slot plus an access-restriction instruction lifts such a list into this row.
- **`Conflicts inbox` as a mailbox folder** — rejected as evidence of anything. `00`: "A session
  should never be treated as proof of topic" (verified verbatim). A folder is an unlabelled position.
- **Practice-management and conflicts-search *systems*** — a live database is a source system, not a
  node. A bounded export with a readable manifest is represented (`Conflicts and screens - Q3
  export.zip`); connector ingestion is a later security decision.
- **Contact exports containing counterparty and colleague names** — rejected. A name list is this
  row's least discriminating and most disclosive structure simultaneously.

## The collision fixture

**`Independence declaration - Meridian audit engagement - 2026.pdf`.**

It carries *every* token this row's `never_alone` strikes: the words independence, conflict of
interest, engagement, declaration; a professional-firm footer; a signature; a date; a named
declarant. It is the file most likely to be mis-filed here, and it is not this row's evidence.

**What discriminates it:** what it *lacks*. There is no search over a client or matter population,
no result or hit slot, no clearance authority separate from the declarant, and no access-restriction
instruction. Its subject is the **declarant's own interests**; this row's subject is a prospective
client screened against the firm's existing population, or an access barrier over named personnel.
A self-attestation is not a search result. Routed to `career.consulting-client-engagement` where
consulting evidence surrounds it, otherwise Review Later.

A second collision fixture is authored for the governance side: `Board conflict of interest
declaration - 2026 - all directors.pdf`, discriminated by the direction of the disclosure — the
organisation's own officers declaring *to* the organisation, with no prospective external engagement.

## Reciprocal boundaries

Each names the same fixture on both sides.

| Neighbour | Shared fixture | Neighbour takes it when | This row takes it when |
|---|---|---|---|
| `law_practice.client-intake` | `New Matter Opening Form - Hartley - 2026-08-11.pdf` | the decisive labelled structure collects information **from/about** the prospective client (identity, verification, source of funds, scope) | the decisive labelled structure is a **search** over the practice's existing population, or an **access restriction** over named personnel |
| `legal` | `Screen undertaking - J Okonkwo - signed.pdf` | an execution or notarial block fires — `legal` is a safety domain and its protection runs first | no execution block exists: the request, result, certificate, register, barrier memo |
| `career.consulting-client-engagement` | `Independence declaration - Meridian audit engagement - 2026.pdf` | declarant-centred attestation about the signatory's own interests; consulting roles, deliverables, milestones | search-with-result-slot, or barrier-with-screened-personnel, inside a practitioner–client corpus |
| `business_operations.organisational-records` | `Board conflict of interest declaration - 2026 - all directors.pdf` | the declaring subjects are the organisation's **own** officers disclosing **to** the organisation | a **prospective external engagement** is screened against existing engagements |
| `hr.employee-relations` | `Screened personnel - Project Kestrel - access list.xlsx` | the subject is the **employment relationship** — conduct, capability, sanction — and the restriction is about the person | the subject is a **screened matter** and the restriction protects a client relationship |
| `law_practice.precedent-bank` | `Blank conflicts questionnaire - template.docx` | party, date, outcome and approver slots are **empty by design** throughout | those slots carry values |

Cross-row recommendations for R1c (I did not edit any neighbour):

1. `law_practice.client-intake` should carry the reciprocal of the new-matter-opening-form boundary
   in the same words, and should route the undecidable combined form to Review Later rather than
   claiming it by default.
2. `law_practice.precedent-bank` should carry the blank-slot reciprocal.
3. `hr.employee-relations` should carry an explicit note that a screened-personnel list carries **no**
   adverse implication about anyone named on it.
4. `law_practice.json` may wish to note that its "intake-and-conflicts" signal is an **activation**
   signal shared by two templates, so that the anchor's fixture is not read as claiming placement.

## Neighbours considered that did NOT get an edge

- `legal.practice-matter-file` (the landed launch row) — no direct same-evidence mutex. Its
  discriminator is practitioner-side representation workflow versus the holder's own position; a
  conflicts screen never appears on the personal side, because a private individual does not screen
  a prospective client. The `legal` collision above already covers the executed-instrument overlap.
- `legal.personal-legal-matters` — same reason. There is no personal-side analogue of this row.
- `finance.small-business-bookkeeping` — considered because `must_consider_neighbors` names `finance`
  and because source-of-funds and AML checks sit near screening. Rejected as an edge: source-of-funds
  is intake's, not this row's, and a conflicts record carries no financial slots at all. Naming a
  finance edge here would be padding.
- `business_operations.compliance-audit` and `business_operations.risk-register` — tempting on the
  word "risk", but a risk register's rows are organisational risks with owners and mitigations, not
  screening episodes with searched parties and outcomes. No shared fixture I could name honestly.
- `career.credentials-licenses` — a practising certificate is the schema's own struck token and
  belongs there; it never reaches this row.
- `identity.*` — a client identity copy encountered during verification is intake's, and it carries
  its own Identity evidence regardless. No edge from this row.

## proposed_fields

**Empty, deliberately.** `fields: []` and `dimension_order: []` follow from PR-6 and D1's standing
deferral; the schema declares no field rows, and a template may only reuse fields its schema
declares. Candidates rejected rather than minted:

- `screen_outcome` / `clearance_status` — the single most tempting key, and the one most likely to be
  misused: it would serialize a **legal conclusion** ("cleared", "conflicted") that this product must
  never reach. Even as a raw observation it would be read as a finding. Refused outright, not
  deferred.
- `prospective_client` — a variant of the canonical `client` key, which `law_practice` does not
  reference. Minting a near-synonym is the exact failure `canonical_fields.json` warns against.
- `screened_matter`, `screened_person`, `screening_date`, `approver` — none is canonical, and
  `screened_person` would put a named colleague into a fact slot that a path could later read.
- `our_firm` — canonical, but not referenced by this schema, and it cannot represent an approver,
  a searched party or a screened person.

## NEEDS-JOSEPH

- **NJ-CC-1 — the declined enquirer.** Should a screening episode with a DECLINED outcome be indexed
  at all? (a) Index it like any other episode, accepting that a refused enquirer's identity enters
  the graph; or (b) recognise it, mark it protected, and never surface its party names in any prompt,
  path, summary or search result — a posture narrower than Protected Records currently implies. I
  could not settle this from `00`; leg 3 of the node test points at (b).
- **NJ-CC-2 — the one-way barrier edge.** May P9 record the exact matter reference a barrier record
  names? The reference is what makes the record useful and simultaneously what would place it inside
  the matter it screens. Alternatives: a suppressed one-way edge the matter side cannot traverse, or
  no edge at all with the barrier record left standalone.
- **NJ-CC-3 — reciprocal with `law_practice.client-intake`.** The combined new-matter-opening form is
  either one artefact assigned by dominant structure, or an artefact both siblings legitimately
  recognise. The closed edge vocabulary has no way to express dual recognition between two templates
  on the **same** schema — `also_holds_with` is defined for two *schemas*. R1c needs to choose, or
  the vocabulary needs a term.
- **NJ-CC-4 — anchor overlap.** `law_practice.json` carries `Conflict search - Hartley acquisition -
  CLEARED.pdf` as a schema fixture and names intake-and-conflicts "the family's cleanest signal". If
  R1c reads that as the anchor *claiming* this material rather than activating on it, this row should
  be refused and folded into `law_practice.client-intake`. I have argued it is activation, not
  placement, but the ambiguity is real and I am not smoothing it.

## Self-verification

- `python3 -m json.tool` parses the node file; key set is **identical** to `law_practice.json`'s
  (no missing, no extra).
- Every `00` span in quote marks was grep-verified verbatim against
  `planning/00-database-agent-product-design.md` before writing: `a labeled form field` (41),
  `Tables matter because resumes, forms, applications, invoices, and administrative documents often
  place their…` (29), the three residual sentences (120), `A session should never be treated as proof
  of topic`, `The default posture must therefore be local-first and data-minimizing`, `…usually comes
  before time because putting year first scatters related work…`, `A university name alone should not
  create a group because Columbia…`, `The system recommends an order based on the domain template,
  but the user can reverse, remove, add, or flatten dimensions`, `It should avoid using authorship or
  creator identity as a destination dimension`, `create meaningless one-child levels` — each returned
  exactly one match. Spans attributed to `law_practice.json` are quoted from that file.
- Every `file_examples.source_type` is in `SOURCE_TYPES`.
- Every edge id verified present in `planning/domains/roster.json`: `law_practice.client-intake`,
  `law_practice.precedent-bank`, `legal`, `career.consulting-client-engagement`,
  `business_operations.organisational-records`, `hr.employee-relations`, `photos`, `hr`.
- Every `falls_through_to` and `falls_through_if_inactive` value is a `00` §7.3 residual name.
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `role_split: []`, `time_first: false`.
- No threshold numbers, no confidence scores, no handling classes, no folder path written as a fact.
- Wrote only the two assigned files. Did not touch `29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/`, or any neighbour node.
