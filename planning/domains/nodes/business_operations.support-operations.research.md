# business_operations.support-operations — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the gist draft of the same name. The gist draft's facts and JSON key
set were correct and are preserved; what it lacked was the argument. Nothing it asserted is silently
reversed here, and the one place I extend it — a second collision fixture pointing the opposite way —
is marked as an addition, not a correction.

**Verdict: the row STANDS.** I am not reversing the gist verdict. But the dispatch was right that this
row sits closer to the format boundary than any other survivor in this family, and the sections below
answer that charge with bytes rather than with confidence.

---

## Sources

- `planning/00-database-agent-product-design.md` — authoritative; every quotation below was
  machine-checked verbatim with `grep -F` before it was written into either file.
- `planning/domains/CONNECTION.md` §2 (the node test), §4 (activation, step 2 never-alone),
  §9 failure mode 6; `_CONTRACT.md` rules 6, 10, 15; `planning/prompts/ALIGNMENT.md`.
- `planning/domains/nodes/business_operations.research.md` — the deepened schema anchor. Read first,
  as the addendum requires. It states the family's default template and generalises the never-alone
  principle for all 24 siblings; both are applied explicitly below.
- `planning/domains/nodes/business_operations.organisational-records.json` — the family's refusal,
  read on the assumption that this row might be heading the same way. It is not, and §"Node test"
  says exactly which leg saves it that the refused row could not clear.
- `planning/domains/nodes/business_operations.customer-account-management.research.md` — the row that
  makes a direct claim on this material. Read in full on the support seam; answered in §"Charge (b)".
- `planning/domains/nodes/business_operations.partnerships-bd.research.md` — read for the three-row
  counterparty settlement. **Not reopened.**
- `planning/domains/nodes/business_operations.product-requirements.research.md` — read for the
  ticket→requirement seam; its handling is adopted rather than contested.
- `planning/domains/nodes/business_operations.meeting-record.research.md` — read for HOW the format
  charge is answered, deliberately **not** for WHAT the answer is. Its answer is a cross-file series
  regularity. This row has no series signal worth the name and does not borrow one.
- `legal.practice-matter-file.json` — read for the matter-register collision; its confidentiality
  posture is respected, not overridden.
- `ROSTER.md` Appendix A lines 695 and 826: `ops.support-operations` (ROW), `soft.helpdesk-ticket`
  (FOLD). This row owns that absorbed coverage.

---

## What it is for, and what it holds

An organisation runs a desk that answers the people who use its product or service, and the desk
produces a continuous stream of records about the answering. The row holds ticket and case exports,
individual case threads, service-level and queue reporting, knowledge-base and macro content,
escalation matrices and on-call rotas, satisfaction exports, customer-supplied screenshots and log
excerpts, and session recordings.

The anchor, stated once so the legs can be tested against it: **the support function as a continuous
queue** — a stream of individually small third-party interactions, whose primary artifact is a
*periodic snapshot of a workflow system's own state.* Every other row in this family is anchored on a
bounded effort (a project, a tender, an audit), a standing cycle (a budget year, a board year), or one
named counterparty. None is anchored on a queue.

---

## Charge (a): "a support corpus is a FORMAT, not a domain"

This is the charge the dispatch raised first and it is the serious one. Written at full strength
before any answer:

> *A support corpus is ticket exports, chat logs, email threads and call recordings. The roster triage
> already dropped eighteen legacy ids as "format / SOURCE_TYPE" material — calendar, mail, chat, call,
> logs — on precisely that reasoning. A ticket is the container format of a helpdesk tool exactly as
> an `.eml` is the container format of a mail client; `soft.helpdesk-ticket` even names the container
> in the id. The desk is a workflow, and its files are its dumps. Strip out the containers and what
> is left is `customer-account-management`'s relationship material and `retrospective-postmortem`'s
> incident material. A row whose evidence is a format is not a domain, and this row is closer to the
> boundary than `meeting-record` was, because a meeting at least produces an authored document.*

Every clause of that is either true or nearly so, and three concessions are owed before the answer.

**Concession 1 — the containers really are containers, and this row does not get them.** A chat
transcript, a saved mail thread, a call recording and a screen-share file are `SOURCE_TYPES`. `00`
settles their status directly: *"The engine should treat the file extension as a routing signal rather
than an assumption about meaning, inspect the real MIME type or file signature where possible, and
dispatch each file to a type-specific extractor."* A container is a dispatch decision. The gist draft
already had "a single support email thread saved out of a mailbox, with no ticket identifier" in
`needs_llm`; this pass **hardens that into an explicit `never_alone` entry** covering all four
containers at once, and adds `chat_transcript_2026-05-14_1409.txt` as a file example whose whole job
is to be a file the support desk genuinely produced that must **not** fire this row. If the row's
detection had rested on those, it would deserve to fall.

**Concession 2 — the id names a container.** `soft.helpdesk-ticket` does read like a format id, and
that is a fair reason to have been suspicious of it. It was folded, not kept as a row.

**Concession 3 — `meeting-record`'s answer is unavailable here.** That row survives on a cross-file
*series* regularity: N files, one varying date token, one invariant heading skeleton. This row's
monthly exports superficially look like that, but the resemblance is worthless as an argument — a
monthly dump is a re-export of an overlapping row set, which is a duplicate-family problem (and the
JSON's `grouping_reasons` treats it as one), not a positive association. I am not claiming the series
signal.

### The answer: the queue register is a structure, not a container

The family bar, from the schema anchor, is exact:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**.

The load-bearing signal is: **a header row pairing a case or ticket identifier with a requester
name-or-email, a status, a priority, a paired created/resolved timestamp, an assigned agent and a
queue.** Test it against the bar and against the format charge in turn.

1. **It is a structure with labelled slots, and `00` puts reading it in the rules layer, not the model
   layer.** Rules are named as *necessary* for *"finding spreadsheet headers"*, and separately:
   *"Tables matter because resumes, forms, applications, invoices, and administrative documents often
   place their most useful information in cells rather than body paragraphs."* Seven co-occurring
   named columns is not a shape word; it is a slot set.
2. **A slot set is not a container.** `.csv` is the container; `email` is a container; *requester ×
   agent × queue × status × elapsed-to-resolution* is a **vocabulary of a situation** — one party asks,
   another party is assigned, the asking is measured against a commitment and closed. No `SOURCE_TYPE`
   definition contains any of those words, and no extractor dispatches on them. That is the precise
   difference between this row and the eighteen dropped ids: those ids named the transport (`mail`,
   `chat`, `call`, `calendar`, `logs`), and this row names the *roles inside the table*.
3. **The row is not one structure but five, four of them authored by a person.** A service-level
   report pairs a target with an attainment per period. A knowledge article carries symptom / cause /
   resolution / applies-to. An escalation matrix pairs severity levels with response commitments plus
   a rota and an invocation procedure. A satisfaction export carries a score plus free text keyed to a
   closed case. None of those is a dump of anything, and no container produces them. A charge that the
   row is only exports has to explain away four fifths of its `work_types`.
4. **Falsifiable, and I state the falsifier.** If R1c judges that the seven-slot header is in fact the
   *generic tracker header* — that identifier + person + status + assignee is a shape every workflow
   tool emits and therefore a document shape alone — then leg 1 fails on the family principle and the
   row's remaining support is its privacy posture. I do not think that judgement is right, because the
   discriminating slots are *requester* and *elapsed-to-resolution-against-commitment*, which a bug
   tracker, a change register and a matter register do not carry. But the row's `never_alone` list
   already concedes half of it — "a status-and-priority column pair alone: every tracker ever written
   has one" — and the honest position is that this row's leg 1 is the *narrowest* pass in the family.

**Charge (a): answered, with concessions.** The containers are conceded outright and now excluded in
the JSON. The row stands on the queue register and on four authored structures beneath it.

---

## Charge (b): "this is a slice of `customer-account-management`, not a world"

Answered largely by that row itself, which read this one first and declined the material. Its deepened
file rejects a ticket export from its own examples in terms:

> **"A support ticket export"** — rejected as an example, held as a `collides_with` against
> `support-operations` instead. That row's own file refuses a per-customer dimension for exactly this
> material; putting the export in this row's examples would have read as contesting that refusal.

and again for satisfaction data: *"`support-operations` holds satisfaction exports and its file says
so."* So the neighbour with the strongest claim has inspected the claim and does not press it.

That is not sufficient on its own — a neighbour's courtesy is not an argument — so the substantive
separation, in the neighbour's own vocabulary:

- **Cardinality.** That row's anchor is *"one customer as an ongoing relationship"*. This row's anchor
  is a queue whose defining property is that no single requester matters. A relationship file is
  *about* a named party; a queue export is about *the work*, and the named parties in it are incidental
  and numerous. That is not a slice of one thing, it is the opposite orientation to the same people.
- **The dimension consequence proves it.** Because that row is one-counterparty-shaped, a
  per-counterparty folder is at least arguable there, and its file argues for one, user-approved.
  Because this row is queue-shaped, a per-counterparty folder here would build a folder per customer
  containing everything they ever complained about, which is `00`'s collector failure exactly: *"A
  folder should not become a collection point for everything produced by the same person or
  organization."* Two rows that reach **opposite** answers on the same dimension from the same
  material are not one row.
- **Audience.** This row folds an *internal* IT service desk. There is no customer relationship at all
  when the requester is a colleague. A slice of `customer-account-management` cannot contain a case
  where the counterparty is the holder's own staff.

**Charge (b): declined, and the neighbour concurs.** The one live disagreement between the two rows —
whether a per-counterparty level is ever acceptable — is recorded on both sides (its NJ-BO-CAM-4, this
row's `open_question`), and this pass writes the concurrence into this row's `collides_with` signal so
the edge reads the same from both ends.

---

## The node test, leg by leg, against the family's stated default template

The default template this row must differ from, quoted from the deepened schema anchor:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* → the
> **governance body, project, contract, or account** the material belongs to → the **fiscal period** →
> the **document function**. Not time-first.

CONNECTION §2: *"A **template** row exists only if its detection signals, recommended dimensions, or
privacy rules differ from its schema's default template."* Three legs, and a row needs one.

### Leg 1 — detection signals: PASSES, narrowly, and the narrowness is stated

Argued in full under Charge (a). The queue-register header is a structure paired with labelled slots
and clears the family bar. The refused sibling, `organisational-records`, failed here because *"Its
only candidate signal is an organisation name plus a document-type word"* — both never-alone, so *"it
would be a row that never fires."* This row's signal contains no entity name and no document-type word
at all; it is seven column labels. That is the specific difference between this row and the family's
refusal, and it is worth being blunt that it is the *only* leg on which the two rows are far apart.

Weakest point, named rather than hidden: the vocabulary half of this row's recognition (*ticket, case,
support, incident, issue*) is worth nothing, and the JSON says so — *"case names a legal matter, a
clinical case and an HR case, and incident names an outage and a workplace accident."* Strip the
vocabulary and the header structure is what remains. It has to carry the leg alone, and it does.

### Leg 2 — recommended dimensions: PASSES, and uniquely in this family

This row differs from the default paragraph in a way no sibling does: it is the only row in the family
whose `template.why` states a **negative** constraint — a per-customer level must **not** be
recommended, at all, regardless of user approval, on `00`'s collector prohibition. Every other sibling
differs from the default by reordering or substituting a level. Reaching a *prohibition* the schema's
default does not contain is a difference in recommended dimensions in the strictest sense the test
admits.

The positive recommendation, held as prose because the schema declares no fields and *"a dimension may
only branch on a field the same schema declares"*: the product or service supported → the document
function (case material / reporting / knowledge content / procedure) → the reporting period last.
Period last, and **not time-first**: the anchor's rule that *"`00` grants the time-first exception to
capture-based media only. **No sibling in this family may claim it.**"* is obeyed here even though this
row is the most tempted in the family, because its material genuinely arrives as a dated stream. A
monthly ticket export's date is a content period, not a capture date; `time_first` stays `false`.

Note the substitution against the default: the default's second level is *"the governance body,
project, contract, or account"*, and this row replaces it with the **service supported** while
explicitly deleting *account* from the list of permissible values at that level. The deletion is the
whole of leg 2.

### Leg 3 — privacy rules: PASSES

This is the densest concentration of third-party personal data in the family, and it arrives in bulk:
one monthly export is a register of thousands of named people, their addresses and, in the free-text
column, whatever they wrote about their own circumstances. `00` names the corpus — it *"can include
identity documents, account statements, tax records, medical information, legal records, credentials,
private correspondence, GPS metadata, employment materials, and educational records."* — and requires
an immediate transition for the account-shaped records that turn up inside case threads: *"A scanned
passport, tax statement, medical document, authentication key, or account record should enter a
protected state immediately."*

The rule that is *different* rather than merely strong, and which no sibling states: **the support
corpus is the family's worst case for the high-frequency-entity failure.** Two or three agent names
sign thousands of records, so the corpus is riddled with a bridge that is not an anchor. `00` makes
this a stop rule outright — the system *"should not form a supported group when there is no valid
anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the
only bridge"*. This pass writes that into the JSON's `never_alone` as a new entry, because the gist
draft had the aggregation danger but not the bridge danger, and they are different failures.

**Overall: three legs, three passes, one of them narrow.** Refusal was considered seriously — the
containers concession removes a real part of what people imagine this row holds — and rejected because
what remains after the concession is five structures, not zero.

---

## Files considered and rejected

- **`matters_open_2026.xlsx`** — **kept** as the inbound collision fixture, chosen over the more
  obvious CRM export because the harm is larger: an identifier-person-status-fee-earner table is
  structurally indistinguishable from a ticket export, and misreading a legal caseload as a helpdesk
  queue files client-confidential material in an operations branch.
- **`chat_transcript_2026-05-14_1409.txt`** — **added this pass**, and it is the deepening's main new
  evidence. It is the fixture pointing the other way: a file the support desk really did produce,
  which must not fire the row, because a transcript is a container. Without it, the row's answer to the
  format charge is only prose.
- **`csat_responses.csv`** — kept; it makes a point no other example makes, that a customer-facing
  export is *simultaneously* unsolicited written commentary on named employees.
- **`session_recording_88214.mp4`** — kept; a support screen-share can show the customer's own inbox
  and credentials, the sharpest exposure in the row. Note it is a *container* too and its
  `must_not_conclude` says the filename's identifier token does not license a case fact.
- **A community-forum export** — rejected. Publication changes the privacy analysis enough to need its
  own treatment, and it is rare in a personal corpus.
- **A bug tracker export** — rejected as an example and held as a `collides_with` to
  `code.software-project` instead. As an example it would have implied a claim on the developer side of
  the same table.
- **A product feature request list distilled from tickets** — rejected. It is
  `product-requirements`', and that row's file has already settled the direction (below).
- **A vendor's own SLA in a supply contract** — rejected. The commitment as an *instrument* is
  `contract-administration`'s; only the desk's reporting *against* a commitment is this row's.
- **An IT change record** — rejected. `INC-`/`CHG-` are minted by the same tool, but a change record is
  anchored on an approved change window and a back-out plan, neither of which this row has.

---

## Reciprocal boundaries

**↔ `business_operations.customer-account-management`** — argued in full under Charge (b). **From that
side:** *"one customer as an ongoing relationship"*, an account plan's stakeholder map, an adoption
record, a renewal preparation. **From this side:** a queue of individually small interactions in which
no one requester is the subject. **Same bytes, named on both sides:** an **outage record** — a
major-incident ticket here, an escalation summary there; that row's
`Escalation summary - Acme - outage 14 Feb.docx` already carries the tension in its own
`must_not_conclude`. **Live disagreement, not smoothed:** the per-counterparty dimension. Recorded both
sides; this row does not overrule.

**↔ `business_operations.partnerships-bd`** — **settled territory; not reopened.** That row settled
that *pursuit, account and vendor are three worlds* and accepted the premise that a counterparty's
**role is a field value, not a domain**. This row sits inside that settlement and takes nothing from
it: this row's recognition names no counterparty role at all. Stated so that R1c can check the row is
consistent with the settlement rather than silent about it: a support case's requester is not a
*role-typed counterparty* in that sense — they are the *subject of one interaction*, and this row
never proposes to file by them. No edge; the settlement covers it.

**↔ `business_operations.product-requirements`** — **the seam, stated as that row states it.** Its
file assigns *"A support knowledge-base article describing how a feature works"* here, on `00`'s test
— *"Topic answers what a file is about, while purpose answers what the file was for"* — with the
direction as the discriminator: the article describes what the product **does**, externally; a
specification describes what it **should do**, internally. It then declines an edge deliberately: *"A
boundary rule without an edge."* **Accepted verbatim in substance, and reciprocated by matching its
decision:** no `collides_with` is authored from this side either, because authoring one here would
contradict a neighbour's stated, reasoned choice. The related seam — support tickets *becoming*
requirements — runs through `user-research`, which carries it; this row does not triple it.

**↔ `legal.practice-matter-file`** — **from that side:** a matter type, a limitation or key date, a fee
earner, a client counterparty, and a confidentiality posture this row must never override. **From this
side:** a queue, a priority, a resolution time against a commitment. **Same bytes:**
`matters_open_2026.xlsx`. Edge authored from this side because the risk is one-directional and it is
this row that would do the stealing.

**↔ `business_operations.it-asset-inventory`** — **from that side:** an asset tag, an entitlement, a
custody assignment. **From this side:** a request, an agent, a resolution. **Same bytes:** an export
keyed on the same laptop and the same employee. Edge authored.

**↔ `business_operations.retrospective-postmortem`** — **from that side:** a timeline plus causal
analysis plus remediation commitments, anchored on one event. **From this side:** the operational case
record and its service-level reporting. **Same bytes:** a major-incident review citing this row's
ticket identifiers. Edge authored.

**↔ `business_operations.risk-register`** — **from that side:** a recovery time objective, a
critical-activity analysis, a continuity test. **From this side:** severity-to-response commitments for
routine service. **Same bytes:** `On-call rota and escalation matrix.docx`, which is genuinely both.
Edge authored.

**↔ `hr.employee-relations`** and **↔ `code.software-project`** — as written in the JSON; the
discriminators (employee-as-*subject* plus a process name; component/branch/release plus repository
residence) are unchanged from the gist draft and were correct.

---

## Neighbours considered that did NOT get an edge, and why

- **`medical` / `clinical_practice`** — a clinical caseload is another identifier-plus-person table.
  Left unedged **deliberately**: an edge authored from an operations row toward protected clinical
  material points the wrong way, and the `legal.practice-matter-file` edge already carries the lesson
  in a form R1c can generalise.
- **`business_operations.product-requirements`** — see above; matching a neighbour's reasoned refusal
  to edge.
- **`finance.subscriptions-utilities`** — the mirror image, where the holder is the *requester* of
  someone else's support desk. Genuinely interesting, owned by another agent, left as NJ-BO-SO-3.
- **`business_operations.meeting-record`** — a support call is not a meeting record; that row activates
  on a four-part meeting-note structure this material never carries. No edge, no tension.

## `also_holds_with`: deliberately empty

Not an oversight. CONNECTION's edge table is schema ↔ schema, and every genuine both-at-once case this
row has — the outage record, the escalation matrix — is with a **sibling template on the same schema**,
which the edge cannot express. `customer-account-management` reached the same conclusion for the same
reason and states it in prose. Prose on both sides, and P10's to choose from an accepted group.

---

## proposed_fields

**Changed this pass.** The gist draft proposed none. This pass **seconds the two proposals the schema
row already made** rather than staying silent, because the addendum asks siblings to second rather
than mint and because a silent row gives R1c nothing to adjudicate with.

- **`organization`** — seconded, not minted; adjudicated once at the schema row. Row-specific
  argument *for*: this template folds an internal desk and an external desk, and `organization` is the
  only proposed key that can record which desk a file came from without naming a requester.
  Row-specific argument *against*, stated because it is real: in a single-entity corpus the value is
  constant, which is `00`'s meaningless-one-child failure. Seconded on the schema row's own condition
  that it remain a template-time check, and `destination_eligible: false` here.
- **`fiscal_period`** — seconded **with a reservation that is this row's own**: a support desk reports
  on an *operational* period — a month, a week, a rolling window — far more often than a fiscal one,
  and this row's recurring artifact is `tickets_export_2026-05.csv`, not an FY deck. If the key lands
  as strictly fiscal, this row is left without a period concept. It does **not** mint a monthly variant,
  because that is exactly the synonym the contract forbids. Flagged for R1c as NJ-BO-SO-4.
- **A `ticket_id`-style key — rejected outright**, as in the gist draft and for the same reason,
  restated because it is the row's most tempting mistake: a per-case identifier is a *record-level*
  value, never a folder dimension, and minting it would license precisely the per-customer aggregation
  leg 2 exists to forbid.

---

## NEEDS-JOSEPH

- **NJ-BO-SO-1 · Internal service desk vs external customer support.** The roster folded
  `soft.helpdesk-ticket` here and the detection shapes are identical, but the requesters differ —
  colleagues on one side, customers on the other — and the privacy consequence differs with them.
  **Alternatives and costs:** (i) keep the fold, as this pass does — cost: one row carries two privacy
  postures and the stronger one has to govern both, which over-protects the internal desk; (ii) split
  into two templates on one schema — cost: two rows with identical `recognition` blocks, which is the
  574's pattern and would likely fail leg 1 on the second row; (iii) make audience a *value* on the
  proposed `organization` key — consistent with `partnerships-bd`'s accepted premise that role is a
  field value, and my preferred option, but it presupposes `organization` landing. Fold kept on
  detection grounds; doubt recorded.
- **NJ-BO-SO-2 · What may a bulk export of thousands of named third parties do at all?** This row
  states it must not acquire a per-customer branch. Whether such a file should be organised, merely
  *represented without moving* (as `00` offers for unreadable material), or left untouched entirely is
  a P7/P10 policy question this catalogue cannot answer. `customer-account-management` cites this row's
  represent-without-moving proposal in its own NJ; the two should be resolved together.
- **NJ-BO-SO-3 · The holder as requester.** A person's own support correspondence with a supplier is
  this row's material seen from the wrong side. No edge authored — the household mirror is another
  agent's row; R1c should decide whether it is stated.
- **NJ-BO-SO-4 (new) · `fiscal_period` may not fit an operational cadence.** See `proposed_fields`.
  Alternatives: broaden the key's definition to any recurring management period (cheap, but weakens a
  key another schema also depends on); let this row use `creation_date` at the period level (wrong —
  that is when the bytes were made); or accept that this row has no period dimension in v1 (honest, and
  it costs the row the least, since function-before-period still yields a usable recommendation).
- **NJ-BO-SO-5 (new) · Is the seven-slot queue header a domain signal or a generic tracker shape?**
  This is leg 1's falsifier, surfaced rather than smoothed. If R1c judges *identifier + person + status
  + assignee* to be a document shape alone, leg 1 fails and the row survives on legs 2 and 3 only —
  which is still a pass under CONNECTION §2, but it would make this the family's thinnest surviving
  row and R1c should know that before it lands.
- **Carries NJ-BO-CAM-4 from the other side** — the per-counterparty dimension rule is contested inside
  the family. This row forbids it for bulk queue exports; `customer-account-management` wants it
  user-approved for a bounded relationship file. One rule, stated once, is needed. This row does not
  claim to be that rule.

---

## What changed in this pass

Checked line by line against the JSON actually written, per the addendum.

1. **`one_line`** — the trailing "Gist-level placeholder (J-IND)" sentence replaced with a J-DEPTH
   statement naming the format charge as answered. `launch` unchanged (`placeholder`); `fields` still
   `[]`; `refuse_node` still `false`.
2. **`recognition.never_alone`** — two entries **added** (8 → 10). One excludes all four containers
   (chat transcript, call recording, mail thread, screen-share) from activating the row, quoting `00`'s
   routing-signal sentence. One adds the high-frequency-entity stop rule, quoting `00`'s group stop
   rules. No existing entry was altered or removed.
3. **`file_examples`** — one **added** (9 → 10): `chat_transcript_2026-05-14_1409.txt`, the format
   fixture, inserted immediately after `matters_open_2026.xlsx` so the two opposite-pointing fixtures
   sit together. No existing example altered.
4. **`proposed_fields`** — **changed from empty to two entries**, both seconding existing schema-row
   proposals (`organization`, `fiscal_period`), each with a row-specific argument and, for
   `fiscal_period`, a stated reservation. No new key minted.
5. **`collides_with[customer-account-management].signal`** — **extended** with the reciprocation now
   that the neighbour's deepened file exists: its verbatim rejection of the ticket export, the shared
   outage-record bytes, and the open per-counterparty disagreement with its NJ-BO-CAM-4 reference.
   No other edge was touched.
6. **Memo** — rewritten from 4.9KB of notes to a full memo: the format charge stated at strength and
   answered with three concessions; charge (b) answered with the neighbour's own words; the node test
   argued leg by leg against the anchor's stated default paragraph, including leg 1's falsifier; nine
   files considered-and-rejected; reciprocal boundaries stated in both directions for nine neighbours across eight entries;
   `also_holds_with`'s emptiness justified; two new NEEDS-JOSEPH items.
7. **Nothing reversed.** The gist draft's verdict, anchor, sensitivity, `template.why`, `work_types`,
   `grouping_reasons`, `falls_through_to` and `open_question` are preserved unchanged. The one place
   this pass goes *further* than the draft is the container exclusion, which narrows the row rather
   than widening it.
8. **Nothing outside the two assigned files was written.**

## Self-verification

- `python3 -m json.tool` on the node file: parses.
- Every `00` quotation newly introduced in either file checked with `grep -cF` against
  `planning/00-database-agent-product-design.md`: each returns 1.
- Quotations from neighbour memos (`customer-account-management`, `product-requirements`,
  `partnerships-bd`, `organisational-records`, the schema anchor) taken verbatim from those files.
- `fields: []`, `launch: "placeholder"`, no minted canonical key, no threshold or count invented.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; every edge target is a roster id; every
  `falls_through_to` name is one of `00`'s nine residuals.
- Section 1–5 claims above re-read against the written JSON after writing, not before.
