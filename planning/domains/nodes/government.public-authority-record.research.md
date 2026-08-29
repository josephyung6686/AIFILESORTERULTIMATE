# Research memo — `government.public-authority-record`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/government.public-authority-record.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch
Result: **REFUSED** (`refuse_node: true`)

## Result

Refused. This is the branch root of a schema that already has thirty named children and a fully
written default template, and its roster hint defines it by what it is *not*: "a document issued by,
or addressed to, a public body that carries an authority and a record type but no more specific
governmental sub-domain." Strip the absence clause and what remains — a public body plus a record
type — is evidence the `government` anchor already lists as never-alone. Keep the absence clause and
what remains is a routing rule about the sibling set, which is what a residual home is, and `00`
already names the residual homes. Coverage is held twice over without this row: the `government`
schema's own default template accepts anything that legitimately activates the schema without a
sibling firing, and Independent Records, Protected Records, Reading Inbox, Review Later and
Unsupported or Encrypted hold the standalone official document that never reaches a group. Refusing
costs no coverage and no protection, because activation, safety posture, universal facts and
grouping all attach through the schema, which this refusal does not touch.

## Sources

`RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`; `legal.practice-matter-file.research.md`
as the depth calibration; the `government` schema anchor JSON in full and its research memo's line on
this id; `business_operations.organisational-records.json` as the refusal exemplar;
`planning/domains/roster.json` (358 nodes) for id validity; targeted greps of
`planning/00-database-agent-product-design.md` for every quoted span; and the nine landed neighbour
JSONs that already carry an edge naming this id.

## The charge

Five of the brief's named failure modes apply to this row at once, which is itself the finding.

**Defined only by an ABSENCE.** The operative clause is "no more specific governmental sub-domain."
No extractor can observe an absence; there is no evidence shape for "thirty other templates failed
to fire." That is a dispatcher's fallthrough rule, and fallthrough rules belong to the residual
library, which is P10/P11's namespace, not this one.

**A duplicate of its own schema's default template.** This is not my inference — it is how the landed
rows already talk. `government.elections-administration` writes that "The generic authority-side
default and this row compete over exactly the fixture Election Count Reconciliation - North
District.csv, which the government schema already carries as its own example." Both halves matter:
the neighbour says *the default* where the roster says *this id*, and the fixture it names is the
schema anchor's own file example. `government.legislative-record` does it more explicitly, edging
this id with "The schema's own default template already accepts a legislature packet as one
authority-side workflow among ten" and closing "stays with the default template." Two independent
agents, arguing a boundary against this id, used the id and the schema default interchangeably in
the same paragraph. When neighbours cannot tell two things apart while drawing a line against one of
them, they are one thing.

**Evidence that is an organisation type.** The anchor's first never_alone entry is "a government
department, regulator, municipality, legislature, court, public school, archive, museum, or
official-looking seal alone; the entity may be issuer, counterparty, subject, employer, cited
authority, research venue, or service provider." That is exactly what this row would run on once the
absence clause is removed.

**A hint that collapses two opposite custody roles.** "Issued by, *or addressed to*" is a disjunction
of a role and its negation. Holder side is the one axis the whole `government` family turns on —
every sibling boundary I found is argued on it — and this row's definition refuses to take a
position. Worse, the "addressed to" half is already disowned by the schema: "an authority-issued
permit, licence, tax notice, benefit letter, identity card, visa, voting confirmation, filing
acknowledgement, or registry extract held by the recipient" is never-alone for `government`.

**A refusal the project has already made.** `business_operations.organisational-records` is this row
in another schema — hint: "an organisation name and a document type but no more specific operational
sub-domain" — refused because it "is not an organizational situation but the ABSENCE of one." The
government wording is a find-and-replace of it. Refusing one and keeping the other is incoherent.

## The node test, all three legs

CONNECTION.md: a template row exists only when its **detection signals**, **recommended dimensions**,
or **privacy rules** differ from its schema's default template. One leg would be enough. This row
loses all three.

### Leg 1 — detection signals: identical to the schema's

The anchor's default template is not a stub. It carries deterministic signals for all thirteen
declared work types: legislature packets with a repeated official bill identifier; rulemaking
dockets; public-body governance cycles (agenda, numbered papers, minute, resolution, public notice);
funder-side grant administration; buyer-side procurement; deciding-side planning, permit, inspection
and enforcement casework; records-holder-side disclosure and redaction work; statistical collection
and release cycles; election operations; citizen casework; public education, library, archive and
museum administration; intergovernmental programmes. Its grouping reasons cover the proceeding
lifecycle, the governance cycle, the received-submissions packet, the statistics cycle, the
protected citizen case, the export manifest, and version families.

I looked for one signal true of this row and false of the schema. Every candidate falls into one of
three buckets:

1. **Already a sibling's.** Every authority-side situation with real structure has a named roster
   row — thirty of them, from `policy-development` and `regulatory-rulemaking` through
   `permit-licensing`, `public-records-foi`, `statistical-programme`, `constituent-casework`,
   `archives-recordkeeping` to `school-district-administration`. The schema's own thirteen work
   types map onto them without residue.
2. **Already the schema's.** An authority-side file with genuine role evidence but no
   sibling-specific apparatus — a department's internal briefing chain, a mixed correspondence
   register — activates `government` and lands on its default template. The schema's default
   template *is* the catch.
3. **Owner type only.** What genuinely remains uncovered is a public body's internal corporate
   paperwork: the device register, staff rota, facilities log, purchase-card statement. These are
   `business_operations` shapes whose only claim on `government` is who owns them.
   `business_operations.it-asset-inventory` reached this independently and left its edge deliberately
   unauthored, recording that "the confusion is about the *owner type*, which the schema anchor
   already handles at family level." That agreement is fatal: an owner type is an organisation name,
   and an organisation name is never-alone.

Provenance: the sibling enumeration is roster fact; the three-bucket exhaustion is **inference**,
argued rather than asserted, and checkable by anyone who can name a fourth bucket.

### Leg 2 — recommended dimensions: identical, and empty on both sides

PR-6 leaves `government` fieldless, so `dimension_order: []` on both sides — the two orders cannot
differ. Even the prose recommendation is already written and owned by the anchor: authority-side
function or bounded proceeding first, then an exact reference or cycle, then work type; named people
must never become the organizing dimension; time is not first, because `00` says "For document and
record domains, project, function, or subject usually comes before time because putting year first
scatters related work across calendar folders." This row would restate that paragraph verbatim. I
declined to propose fields to manufacture a difference — PR-6 blocks it, and if such keys are ever
ratified they belong on the schema where all thirty siblings can use them.

### Leg 3 — privacy rules: identical

Both carry `potentially_sensitive` with the same operative limit: "Protected material should not be
included in cloud-model prompts by default, should not display raw content in general group
summaries, and should not be moved automatically without a user policy that explicitly permits it."
I found no posture this row should adopt that the schema does not.

The contrast with siblings that *win* this leg is why I trust the refusal.
`government.legislative-record` treats recorded votes and column-numbered verbatim reports as
published by design while treating inquiry submissions and pre-introduction drafting as *stricter*
than the default — a genuine two-directional departure. `government.constituent-casework` adds
cross-person suppression around an intermediary holding an authority-to-act. This row proposes
neither. `potentially_sensitive` is still recorded on the refused JSON so the refusal cannot read as
a downgrade — the posture attaches through P7 and the schema regardless of which template holds the
file.

**Verdict: refuse.** Three legs, three identities.

## Files considered and rejected

Eleven fixtures are carried in the JSON with observations split from facts. Why none rescues the row:

- **`Retention and Disposal Schedule - Planning Function - v4.xlsx`** — the best case for the row:
  real records-management structure, an issuing authority, no sibling apparatus. It still fails,
  because the anchor's default template already accepts a records-management instrument as
  authority-side work.
- **`Improvement notice - 18 River Court - received.pdf`** — the collision fixture; see below.
- **`Annual Return 2026 - Example Holdings - filing acknowledgement.pdf`** — a registry, a reference
  and a timestamp look like authority evidence, but it is the *filer's* copy, which the schema lists
  as never-alone. To `business_operations.corporate-regulatory-filings`; residual Receipts and
  Confirmations.
- **`Complaint CC-2026-0442 - final response - Council Complaints Team.pdf`** — one body plus one
  citizen is the respondent authority's own record, which lands on the schema default.
- **`Post registry transfer 2026 - retired consular files.zip`** — three landed rows contest these
  bytes and none of the three resolutions needs a branch root. Manifest read without extraction.
- **`Council device register - ICT asset list Q3.xlsx`** — the strongest remaining candidate and the
  one I most wanted to keep, since no sibling squarely holds a public body's internal operations. It
  fails on owner type. Review Later.
- **`Election Count Reconciliation - North District.csv`** — the schema anchor's *own* file example,
  contested by a sibling against *this id*. Carrying it is the refusal in one line.
- **`Scheme of Delegation - Example Agency - adopted 2026.pdf`** — the honest exception, escalated as
  NJ-2 rather than smoothed.
- **`Statutory guidance for local authorities - August 2026.pdf`** — publication by government is not
  authority-side custody. Reading Inbox.
- **`Screenshot 2026-08-19 - Grants portal assessment.png`** — "the system must not mistake the
  absence of EXIF for proof that an image is a screenshot", and the converse holds: a capture of an
  official portal is a capture, not a custody. Photos coactivates; no government fact is created.
- **`Citizen case management backup.gdb`** — a filename cannot manufacture a case, a body, a
  sensitivity finding, or a group. Unsupported or Encrypted, no forced inspection.

Rejected wholesale without fixtures: a public body's HR and payroll files (owner type again); a
public-sector employer's name on a resume or payslip (never-alone per the anchor); a downloaded law
or judgment (Reading Inbox); contact exports containing officials' names.

## The collision fixture

**`Improvement notice - 18 River Court - received.pdf`**, a safety regulator's improvement notice. It
carries every feature the hint asks for: a public authority, an inspector's signature block, a case
reference, a stated contravention, a statutory power on its face. If one file were going to justify
a generic public-authority row, this is it.

The discriminator is not the one a reader expects. **The reference number discriminates nothing** —
the identical number appears on both custodies, the regulator's case file and the duty holder's
received copy. `construction_property.site-health-safety` made exactly this point when it authored
its edge at this id: the notice "exists in two custodies with the SAME reference number on both
copies, so the reference discriminates nothing."

What discriminates is the **addressee block and the filing neighbourhood**: a notice *addressed to*
the holder, stating a contravention to remedy by a date, filed beside the method statement it
contradicts, is the duty holder's record. An *issuing* letterhead the holder controls, an inspector's
own visit report, a register entry, or an enforcement decision justifying a statutory power is
authority-side — and lands on the schema default, which needs no branch root to receive it.

The fixture matters to the refusal because "issued by, or addressed to" would have put **both**
copies in this row. A row that cannot separate the two custodies of one document is not a row; it is
a topic.

## Reciprocal boundaries — nine landed rows, all resolving to the schema

Nine landed rows already author a `collides_with` naming this id. "Theirs" is the landed row's claim
as written; the right column is what the material resolves to now — in every case the `government`
**schema default**, not a branch root. This row authors no edges (a refused row cannot be a mutex
partner) and edits no neighbour file; every line is a recommendation to R1c.

| Neighbour (landed) | Shared fixture | Theirs when | Resolves to the `government` schema default when |
|---|---|---|---|
| `government.legislative-record` | a chamber packet | stage-endorsed print, coordinate-addressed amendment, named-member division, or column-numbered verbatim report | the packet lacks the chamber apparatus, or has a case reference rather than a proceeding chain — their words: "stays with the default template" |
| `government.elections-administration` | `Election Count Reconciliation - North District.csv` | poll-operational structure: an account that must balance, a nomination or absent-vote register, station and seal logistics, adjudication, a declaration tied to a contest identifier | the only evidence is an authority office producing a record *about* an election — a committee report on election policy, a budget line, a boundary review |
| `government.emergency-management` | an incident packet | a named activation bounded by declaration and stand-down and subdivided into operational periods, or a standing plan or exercise family | the anchor is a bounded proceeding, case, request, or programme with an exact reference |
| `government.constituent-casework` | `Complaint CC-2026-0442 - final response.pdf` | the holder is the **intermediary** — a second office with an authority-to-act and its own separate reference | the holder is the **respondent** answering under its own scheme: one body, one citizen, no authorisation |
| `government.archives-recordkeeping` | `Retention and Disposal Schedule - Planning Function - v4.xlsx` | the schedule is cited by a transfer instrument or disposal certificate moving or destroying a series under a custodial function | the schedule governs the authority's live files in its own business use; the repository's own board minutes and budget always resolve here |
| `government.diplomatic-consular` | `Post registry transfer 2026 - retired consular files.zip` | the post / sending-state / host-state triangle is in the evidence | a body name and internal governance shape with no triangle. Reciprocally the default must not claim a note verbale, a consular protection case, or an issuance register |
| `business_operations.board-governance` | a council or school-board agenda pack | a private body's own confidential pack | a statutory power, a public-notice obligation, or a published-agenda framing |
| `business_operations.corporate-regulatory-filings` | `Annual Return 2026 - filing acknowledgement.pdf` | a submitted return and a received acknowledgement held by the filer | a statutory power, case-handling framing, or an issuing letterhead written FROM the authority |
| `construction_property.site-health-safety` | `Improvement notice - 18 River Court - received.pdf` | a notice addressed to the holder, stating a contravention to remedy by a date, filed beside the RAMS it contradicts | an issuing letterhead the holder controls, an inspector's own visit report or case file, a register entry, an enforcement decision |

Read the last two columns down the page and the pattern is unmistakable: **every one of these
boundaries is argued on holder side or on structural apparatus, and every one is a schema-level
argument.** Not one needs a template between the schema and the sibling. That is ninefold external
confirmation of the refusal.

Two further neighbours considered and deliberately **not** listed: `business_operations.risk-register`,
which examined this id and left it unedged because "the confusion is about the OWNER TYPE rather
than about the document", and `business_operations.it-asset-inventory`, which kept the same non-edge
for the same reason. Both non-edges are correct and both are more evidence: two independent agents
looked directly at this row and found nothing to draw a boundary against.

The three schema-level neighbours in my assignment (`legal`, `nonprofit`, `business_operations`) are
already handled where they belong — the `government` anchor carries a `collides_with` for each:
Legal over rule, order, permit, enforcement, disclosure, hearing and casework bytes;
business_operations over procurement, policy, budget, audit, filing and meeting shapes; nonprofit
over minutes, grants, consultation responses, advocacy and standards. Restating those on a branch
root would be a third copy, not a boundary.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `proposed_context_terms: []`, `dimension_order: []`,
`time_first: false`. All intentional and binding: PR-6 leaves `government` fieldless and a refused
row proposes nothing. The schema anchor's own open question already asks Joseph whether a role-safe
vocabulary may exist; duplicating that request here would only fragment the decision.

## NEEDS-JOSEPH

**NJ-1 — Nine landed edges point at a refused id.** `government.legislative-record`,
`government.elections-administration`, `government.emergency-management`,
`government.constituent-casework`, `government.archives-recordkeeping`,
`government.diplomatic-consular`, `business_operations.board-governance`,
`business_operations.corporate-regulatory-filings` and `construction_property.site-health-safety`
each carry a `collides_with` naming this id. This row edits none of them. Alternatives for R1c:
**(a)** re-point each edge at the `government` schema — recommended, because the table above shows
all nine are schema-level holder-side arguments that read correctly with the target swapped;
**(b)** retain the id on the roster as a refused alias so existing edges resolve without rewriting
nine files, at the cost of a roster entry that never activates; **(c)** reinstate the row, which
requires overturning the three-leg analysis and, for consistency, the
`business_operations.organisational-records` refusal too. I recommend (a), with (b) as a mechanical
interim.

**NJ-2 — One real pile may go down with the branch root.** A public body's own constitutional and
governance instruments — constitution, standing orders, scheme of delegation, members' register of
interests, code of conduct, statement of accounts — are a purpose-coherent pile with real structure
(numbered delegating clauses, an adopting body, an adoption date, a review clause).
`government.municipal-administration` plausibly holds them for a council, but no row holds them for
a non-municipal agency, regulator, or trust, and they are not a records-management, procurement,
casework, or proceeding artifact. Alternatives: **(a)** confirm
`government.municipal-administration` is scoped to public bodies generally rather than
municipalities specifically — cheapest, checkable by reading one landed row; **(b)** mint a new
narrow row named for the situation, the honest fix if (a) fails; **(c)** leave the pile on the
schema default, safe but losing a genuine situation. This row creates no replacement id, because
minting one is outside what a single node agent may do. I flag it rather than using it to justify a
catch-all: a real narrow pile argues for a narrow row, never for a branch root.

**NJ-3 — Public-body status itself.** The anchor already asks whether public-authority status comes
only from deployment gazetteers or may be user-confirmed for hybrid and quasi-public bodies
(arm's-length bodies, public corporations, contracted providers, chartered regulators). I note only
that the branch root was the row most exposed to getting this wrong — it would have activated on
body status alone — and that refusing it removes the exposure rather than resolving the question,
which stays with the schema.

## Self-verification

- `python3 -m json.tool` parses the JSON: **OK**. Key set matches
  `business_operations.organisational-records.json`, the landed refusal exemplar.
- Every span quoted from `00` was grep-verified verbatim before being written: the five residual
  definitions (Independent Records, Protected Records, Reading Inbox, Review Later, Unsupported or
  Encrypted), "A session should never be treated as proof of topic", "treat the file extension as a
  routing signal rather than an assumption about meaning", "Protected material should not be
  included in cloud-model prompts by default, should not display raw content in general group
  summaries, and should not be moved automatically without a user policy that explicitly permits
  it.", "the system must not mistake the absence of EXIF for proof that an image is a screenshot",
  and "For document and record domains, project, function, or subject usually comes before time
  because putting year first scatters related work across calendar folders." All matched. Spans
  taken from sibling node files or the `government` anchor are labelled as such and never presented
  as `00`.
- No threshold numbers, statistics, file counts, confidence scores, or handling classes.
  `sensitivity` is one of the two permitted values.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (`text_document`, `spreadsheet`, `image`,
  `archive`, `opaque_binary`). No file example writes a folder path as a fact; every `facts_legal`
  is empty because the schema declares no field rows.
- Every `falls_through_to.residual_template` is one of `00`'s nine residual names, and both
  residuals required by the assignment (Independent Records, Protected Records) are present.
- `collides_with`, `also_holds_with`, `role_split` are empty; every neighbour id named in prose was
  confirmed present in `planning/domains/roster.json` (358 nodes).
- Exactly two files written. No roster, canonical-fields, `check.py`, `src/`, SPEC, or neighbour file
  was modified.
