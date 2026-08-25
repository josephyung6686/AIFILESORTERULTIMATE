# business_operations.policy-handbook — lab notes (template row, deepened to J-DEPTH)

**Depth: J-DEPTH.** Deepened from a 4,091B gist memo written under the retired J-IND gist clause.

**Verdict: the row STANDS — but on one leg, not three, and the gist pass was wrong about which
legs.** The gist claimed the node test passed on detection signals *and* on privacy rules. Privacy
does not pass, and this memo says so and reverses it. Detection signals pass cleanly, the test is
disjunctive, and one clean leg is enough. The dispatch warned this row might not survive; it does,
and the reason it does is narrower than the gist thought.

**Status of the draft.** Verified-but-shallow, not untrusted: its quotations were machine-checked
verbatim, its key set matched the landed siblings exactly, and its arguments were sound where it
made them. It was **deepened, not rewritten**. What was preserved and what changed is itemised in
*What changed in this pass* at the end.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — the only document quoted. Every quotation in the
  JSON and in this memo was grep-verified verbatim against it (22 distinct spans, all `grep -c -F`
  = 1). The spans that did the real work here:
  - the **universal-facts sentence** — *"file type, creation date, language, duplicate family,
    version family, and sensitivity status"* — which is why reissue is not an argument for this row;
  - the **collision-policy sentence** — *"A content-hash match supports deduplication review; a
    filename match alone does not."* — same purpose, from the other end;
  - the **table sentence**, *"Tables matter because resumes, forms, applications, invoices, and
    administrative documents often place their most useful information in cells rather than body
    paragraphs."*, which is the licence to read a control block at all;
  - the **university-name sentence**, the family's never-alone source;
  - the **purpose/topic separation**, *"purpose answers what the file was for"*, which is the only
    thing that separates an adopted policy from a downloaded template.
- `planning/domains/nodes/business_operations.research.md` — **the schema anchor, read first and in
  full.** It is decisive twice, in opposite directions, and both are recorded below.
- `planning/domains/nodes/business_operations.organisational-records.json` + `.research.md` — read
  first, on the dispatch's instruction that this row might be heading the same way. It is not. Why
  not is argued at length under *Leg 2*.
- `planning/domains/nodes/construction_property.compliance-certificate.json` — read for the same
  reason: it was refused as a **document type**, which is the charge this row faces. Answered below.
- `planning/domains/nodes/business_operations.compliance-audit.research.md` — the sibling whose
  evidence is largely other rows' policies.
- The four in-family siblings whose own `work_types` name policy material, read directly from their
  JSON: `risk-register`, `vendor-management`, `facilities-workplace`, `support-operations`.
**Attribution note.** `00` is the only document quoted as *design*. Quotations elsewhere in this
memo are attributed in place to the local file they come from — the schema anchor's memo, the two
sibling refusals' `refuse_reason` fields, sibling `work_types`, and (once, marked as such) this
row's own superseded gist memo, recoverable at `git show HEAD:` its path. Each was verified verbatim
against that file, not against `00`.

- `CONNECTION.md` §2 (node test), §4 step 2 (never-alone), §9 (failure modes); `_CONTRACT.md` rules
  6, 10, 15; `ALIGNMENT.md`; `roster.json`; `canonical_fields.json`; `DECISION-BRIEF.md` (J-IND, D1,
  PR-6); `ROSTER.md` §4 + Appendix A lines 818–819.

---

## What it is for, and what it holds

Documents that state binding or authoritative rules for an organisation's people, and that then
**govern themselves**. Policies, employee handbooks, codes of conduct, standard operating procedures
and work instructions, together with the apparatus that makes them controlled documents: revision
histories, approvals, effective dates and review dates.

The second half of that sentence is the row. The first half is a document type.

---

## The node test, argued leg by leg

CONNECTION.md §2: a template row exists only when its **detection signals**, **recommended
dimensions**, or **privacy rules** differ from its schema's default template. The test is
disjunctive. Each leg is argued separately below, and two of the three fail.

### The schema's default template, stated so the difference is measurable

Quoted from the deepened schema anchor, which states it for exactly this purpose:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

### Leg 1 — dimensions. **FAILS.**

No difference, and none is possible. `template.dimension_order` is empty by binding contract
(PR-6, D1's deferral as narrowed, `_CONTRACT` rules 10 and 15): a dimension may only branch on a
field the same schema declares, and this placeholder declares none. Even held as prose, this row's
natural order — organisation → policy area → the governing document — is the schema's default with
*document function* promoted one level and *fiscal period* dropped, because a policy has no fiscal
period. That is a **degenerate case of the default, not a different order**, and I decline to dress
it up as one. This row is emphatically not time-first, and claims no exception: the schema anchor
reserves time-first for capture-based media and warns that *"A sibling claiming `time_first: true` is
claiming the photos exception without the photos evidence"*. An effective date is a fact **about** a
policy, not a home for it — *"For document and record domains, project, function, or subject usually
comes before time because putting year first scatters related work across calendar folders."*

### Leg 2 — detection signals. **PASSES.** This is the whole row.

The candidate signal is the **document-control block**: a labelled table or header pairing a
document owner or approver, a version, an effective or issue date, and a next-review date, **with
those slots filled**.

The schema anchor reaches this conclusion independently and names this row in doing so. Its leg-2
list gives the block as signal shape 2 and says of it: *"This block does not appear on personal
papers at all — it is the single cleanest discriminator this family has, and it is the reason
`policy-handbook` passes its node test."* I did not take that on authority; I re-ran the test. It
holds, and the reason it holds is the family's own never-alone rule:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** … Every detection signal a sibling writes must pair a **structure** with a
> **labelled slot**.

The control block **is** that pair, and it is one of the very few in the family that is a pair
before you argue for it. The structure is a fixed four-slot header; the slots are labelled
(`Owner`, `Version`, `Effective`, `Review`) and carry values, not vocabulary. Strip the word
*policy* from the document entirely and the block still fires. That is the operative test.

#### Answering the `organisational-records` charge — why this row is not that one

That refusal's core: *"an organisation name is constitutionally never-alone"*, so a row whose entire
support is an organisation name plus a document-type word *can never clear activation*, and would be
a row that never fires. Applied honestly here: strip this row's control block and what remains **is**
an organisation name plus the word *policy* — and it would be refused for the same reason, correctly.
The row does not survive because a handbook is important. It survives because there is one signal
left standing after the strip, and that signal is not never-alone. Note the asymmetry recorded in
`never_alone`: an **empty** control block — bracketed owner, no effective date — is now explicitly a
never-alone entry, because an unadopted template carries the block's shape without its evidence. The
block earns its keep only when filled.

#### Answering the `compliance-certificate` charge — why this row is not a document type

That refusal is the sharper test, and the closer analogy. Its argument had five parts. Taking them
in order:

1. *"DIMENSIONS: identical to the schema's default"* — **true here too.** Conceded above, leg 1.
2. *"PRIVACY RULES: identical to the schema's"* — **also true here.** Conceded below, leg 3.
3. *"Strip it and what remains is a document-type word plus an address — and BOTH halves are
   constitutionally never-alone."* — **this is where the two rows part.** The
   certificate's candidate signal decomposed entirely into never-alone halves. This row's does not:
   a four-slot control block with filled owner/version/effective/review slots is not an entity name
   and is not a document-type word. It is a structure. That single difference is the whole margin.
4. *"THE DECIDING EVIDENCE, which is that the coverage is already carried"* — the certificate was
   refused partly because `finance.household-property`, the `construction_property` schema row and
   `construction_property.building-control` each already listed the same documents. **I checked this
   row for the same defect, because it is the one that would kill it, and I nearly found it.** The
   `business_operations` schema row lists `"policy, procedure, standard, or controlled document"`
   among its own `work_types`, and four siblings list policy slivers of their own
   (`risk-register`: risk policy and framework, incident-response procedure; `vendor-management`:
   signed supplier code and policy acknowledgement; `facilities-workplace`: site induction and
   workplace handbook material; `support-operations`: support policy and service catalogue). That is
   a real finding and it was not in the gist. **It is not the certificate's defect, for two reasons.**
   First, a `work_type` on the *schema* row is not a competing template — it is the schema saying it
   handles the object, which is what a schema row does; the certificate's problem was three
   *situations* claiming it. Second, each sibling's sliver is anchored on that sibling's own
   situation, not on the governing document: `risk-register` owns the scoring matrix, not the
   appetite statement; `vendor-management` owns the countersigned code, not the unsigned one. Each
   is now written as a `collides_with` with the boundary stated in both directions and shared
   fixture bytes named. Four edges added in this pass for exactly this reason.
5. *"THE PURPOSE IS A RESIDUAL'S PURPOSE"* — the certificate's hint described *the document you have
   to produce years later*, which is Independent Records' job description verbatim. **This row's
   purpose is the opposite of a residual's.** A residual holds material with *"no broader group"*; a
   controlled document is defined by having one — its versions, its annexes, its approval, its
   successor. A single unattached policy PDF with no control block does fall to Independent Records,
   and the row says so.

#### And the version-family trap, which the dispatch warned about and this row does not fall into

Handbooks are reissued annually, and it would be easy to argue the row from that. **It is not
argued from that, deliberately.** Version family is a *universal* fact — 00 lists *"file type,
creation date, language, duplicate family, version family, and sensitivity status"* as the shared
set every file may carry — and the landed duplicate/version-family design already handles reissue
without a domain row. A version token is now a `never_alone` entry carrying that quotation and
*"A content-hash match supports deduplication review; a filename match alone does not."* The row
gains nothing from reissue and claims nothing from it.

**Verdict on leg 2: passes.**

### Leg 3 — privacy rules. **FAILS. This reverses the gist pass.**

The gist row asserted: *"Privacy rules also differ, in one direction only: the acknowledgement half
is a personnel roster, and that is what drives the row's `potentially_sensitive` value."* I am
reversing that, explicitly, and the reason is the schema anchor, which was deepened after the gist
was written and settles the seam in one line:

> A policy is this schema; the signed acknowledgements are `hr`.

With the acknowledgement half removed, the leg has nothing left. The governing documents themselves
are among the **least** sensitive material in this family — many are published deliberately. The
three residual grounds that keep the cautious value (third-party exposure, annexed case material in
disciplinary and whistleblowing procedures, hr bleed through co-activation) are the schema's own
grounds, inherited unchanged. Inheriting a posture is not differing from it. `sensitivity_why` in
the JSON was rewritten to say this rather than to keep the gist's claim.

**Verdict on leg 3: fails as a differentiator.** The value stays `potentially_sensitive`; the
*argument* for it changed.

### Overall

**Kept, on leg 2 alone.** CONNECTION §2 is disjunctive and one clean leg is sufficient. Saying so
plainly is better than the gist's three-legged claim, because it tells R1c exactly what to test if
it wants to overturn the row: if the control block is not a real, findable structure at corpus
scale, this row has nothing and should be refused. That is the row's single point of failure and it
is stated rather than hidden.

---

## Legacy ids absorbed (ROSTER.md Appendix A)

`ops.policy-handbook` (ROW, line 818) and `ops.process-documentation` (FOLD, line 819). The fold is
correct and worth stating: a policy says what must happen, a procedure says how, and organisations
keep them as one controlled set **under one control-block format** — which is the operative point,
since the control block is the row's anchor and both halves carry it. The fold is not a merger of
two topics; it is two topics sharing the one structure this row activates on.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. Named tempting false positives, and
what discriminates each.

| File | Why it is **not** this row's evidence |
|---|---|
| **`Home insurance policy 2026.pdf`** (kept as fixture) | The primary collision fixture, preserved from the gist and still the single most likely false positive. *Policy* names a contract of insurance as readily as a governing document, and both are numbered clause documents with exclusions. Discriminator: a policy number, an insured party, a premium and a period of cover — versus an owner, an effective date and a review date. `finance.insurance-personal` owns it. |
| **`Privacy Policy.pdf`** saved from a website footer (**added this pass** as a fixture) | The commonest false positive on a real disk, and the gist mentioned it only in `never_alone`. It fires the normative-clause signal, the scope-and-definitions signal and a date. It is somebody else's published notice to the **public**, not a document binding any organisation's **people**. Discriminator: a *last updated* line is not an owner, a version and a review date. **Reading Inbox.** |
| **`Supplier - code of conduct signed.pdf`** (kept as fixture) | A countersigned code imposed on a named counterparty is a contractual instrument. Confirmed in this pass from the other side: `business_operations.vendor-management` lists *"signed supplier code of conduct or policy acknowledgement"* in its own `work_types`, so the split is agreed rather than asserted. |
| **`Data protection policy - TEMPLATE.docx`** (kept as fixture) | Bracketed placeholders, empty owner, no effective date. The control block's *shape* without its *evidence*. *"purpose answers what the file was for"* — it was for adoption, not for governing. **Reading Inbox**, and now also a `never_alone` entry in its own right. |
| **A regulator's guidance note or a published standard** | Real, common, and identical in shape. Not the organisation's own rules. Reading Inbox; and where it is being *conformed to*, `business_operations.compliance-audit` owns the conformity. That sibling's memo makes the matching point from its side about `ISO 27001-2022 standard.pdf`. |
| **A client's code of conduct imposed by contract** | Reads identically to the organisation's own. Goes to contract administration with the instrument that imposed it. Named in `needs_llm`, because nothing deterministic separates them. |
| **A supplier's policy filed as due-diligence evidence** | Same document, third purpose. It is *evidence about a supplier*, and `vendor-management` or `compliance-audit` owns the pack it sits in. |
| **`Escalation process map.vsdx`** (kept as fixture) | Kept precisely because it is *weak*: swimlanes and decision diamonds, and no obligation prose at all. The same extension holds network diagrams, org charts and floor plans. It is in the row on its title block's procedure reference and revision, not on being a diagram. |
| **An undated, unversioned policy-shaped document** | The hardest real file here, common in small organisations, and it has **no control block** — which means the row's one passing leg does not fire on it. Honest consequence: **Review Later**, not this row. A row that claimed it would be claiming the never-alone evidence it just disowned. |
| **A board paper proposing a new policy** | Numbered, obligation-shaped, and a *draft*. `business_operations.board-governance` owns the pack; this row owns the document once it has an effective date. |
| **An MBA case study on corporate governance** | The schema anchor deliberately draws no `academic` edge and this row follows it: identical vocabulary, and `academic` fires on its own evidence. Noted, not edged. |

---

## The collision fixture, in both directions

The addendum requires one in each direction. Both are now in the JSON as real fixtures.

**Direction 1 — a file that would wrongly fire this row: `Home insurance policy 2026.pdf`.**
Preserved from the gist because it is right. The word in the filename is this row's own word; the
document is numbered clause prose with exclusions and a schedule; it is a PDF on a personal disk in
a folder plausibly called `Documents`. What discriminates is a **slot set**, not a topic: policy
number + insured party + premium + period of cover, versus owner + version + effective date + review
date. Both sides name the same bytes — `finance.insurance-personal` on the finance side, this row's
`collides_with` and `file_examples` on this side. What emphatically does **not** discriminate: the
presence of numbered clauses, which contracts, standards, statutes and specifications all have.

**Direction 2 — a file that must not be lost *to* this row: `Handbook acknowledgement - J Patel -
signed.pdf`.** **Added this pass**, and it is the fixture the gist most needed. It carries this
row's vocabulary and this row's document reference (`v4.2`), and it is an `hr` record: one named
individual, one employee number, one signature. Losing it to this row would drag a personnel record
into a row whose posture is built for published documents — which is precisely how the gist's
sensitivity argument went wrong. What discriminates: the acknowledgement has **no control block of
its own**. It is a receipt, not a controlled document. And the reference to `v4.2` does not make it
a member of the handbook's version family: a receipt naming a version is not a version.

The same bytes are named on both sides — here, and in `also_holds_with: hr`, where the container
case (a handbook pack whose final section is a signed page) is handled as disjoint-evidence
co-activation rather than a mutex, per the schema anchor's *"Where one file crosses, the stricter
side governs the members that identify people, even where this schema activates on the container."*

---

## Reciprocal boundaries, both directions

Read the neighbour's own file first and do not contradict it. Where a neighbour is unwritten, the
boundary is authored one-way here and R1c owes the reciprocal — the schema anchor records that this
is a catalogue-wide defect, not a judgement about any seam.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| **`hr`** / `hr.onboarding-offboarding` (unwritten) | an acknowledgement, attestation or induction checklist anchored on one **named** joiner | the governing document itself, which is controlled and exists independently of any joiner | `Handbook acknowledgement - J Patel - signed.pdf`; `Employee Handbook v4.2.pdf` |
| **`business_operations.compliance-audit`** (landed) | an audit or standard reference, a control identifier, a finding, or a position on an evidence-request list | the governing document with its control block, which exists whether or not an audit ever asks for it | an information-security policy sitting inside an ISMS evidence pack |
| **`business_operations.contract-administration`** | two named parties bound to each other, executed signature blocks, notice periods, an obligations register | a document binding an organisation's people generally | `Supplier - code of conduct signed.pdf` |
| **`business_operations.vendor-management`** (landed) | a code **countersigned** by a named counterparty — that row lists it in its own `work_types` | the organisation's own **unsigned** code, which carries the control block | `Supplier - code of conduct signed.pdf` |
| **`business_operations.risk-register`** (landed) | a document whose working content is a register — likelihood/impact columns, risk owners, residual ratings | the governing document that **sets** risk appetite, with clauses and no scoring columns | `Risk management policy and framework.pdf`, whose annex is a scoring matrix |
| **`business_operations.facilities-workplace`** (landed) | material anchored on a specific site or building — one floor's fire plan, one address's induction pack | an organisation-wide H&S or workplace policy with no site anchor | `Health and safety policy.pdf` with one building's evacuation appendix |
| **`business_operations.support-operations`** (landed) | obligations running to **customers** and measured — service levels, response targets, a service catalogue | an internal governing document binding staff generally | `Support policy.pdf` containing an SLA table |
| **`business_operations.board-governance`** | a notice, quorum, numbered papers or a resolution | the governing document the resolution approved | a board pack containing a draft policy and its approval minute |
| **`finance.insurance-personal`** | a policy number, insured party, premium, period of cover, schedule of cover | a scope-and-application section, an owner, an effective date, a review date | `Home insurance policy 2026.pdf` |
| **`manufacturing.work-instruction`** | a process, line, machine or product anchor with in-process controls | an administrative or people-facing procedure | `SOP-014 Goods receipt.docx` — genuinely both, and P10 chooses from an accepted group later |
| **`government.policy-development`** | a public consultation, a legislative or rulemaking anchor, an external audience | a document binding one organisation's own people | a public body's internal staff code |
| **`career`** | a document held to evidence the **holder's own** standing or employment | the organisation's population-level version of the same document | a policy acknowledgement — the same object with the roles reversed |

### Where `business_operations` stops and `hr` begins, for this row — written for the `hr` author

`hr` is unwritten and a staff handbook is its most obvious material, so this is stated in enough
detail to be written against, and it follows the schema anchor rather than diverging from it.

- **The line is the control block, and it runs through the document set, not around it.** This row
  owns the **rule**: any document whose subject is a population and which carries a filled
  owner/version/effective/review block. `hr` owns the **receipt and the case**: any document whose
  subject is a named individual — an acknowledgement, an attestation, a disciplinary case file, a
  grievance, an incident report, an induction checklist for one joiner.
- **The seam is not topical.** A workplace-safety *procedure* is this row; an incident report naming
  an injured employee is `hr`. A disciplinary *policy* is this row; a disciplinary *case* is `hr`.
  The same four words appear on both sides of every one of those pairs, which is why the test is
  the block and the subject, never the vocabulary.
- **Containers co-activate; they do not transfer.** A handbook PDF whose last page is a signed
  acknowledgement activates this row on the container and `hr` on the member, on disjoint evidence,
  and *"The graph does not automatically copy those missing facts onto sparse files."* This is
  `also_holds_with: hr`, added in this pass, and it is not a mutex.
- **Note for the `hr` author:** the roster has already given hiring away —
  `career.employer-side-hiring` absorbed four legacy `hr.*` recruiting ids. Check Appendix A before
  writing. And please carry NJ-BO-8 below from your side; do not assume this row quietly kept the
  acknowledgements.

---

## Neighbours considered that did NOT get an edge

- **`nonprofit.governance`**, **`government.public-authority-record`** — both keep policy libraries
  in exactly this shape. `government.policy-development` already carries the public-body confusion,
  and the schema anchor's `nonprofit` edge splits the whole family on owner type. Adding two more
  would restate one discriminator three times.
- **`clinical_practice.practice-administration`**, **`research.ethics-compliance`** — clinical
  protocols and study SOPs are governing documents with control blocks. The discriminator is the
  one `manufacturing.work-instruction` already states: a domain-specific anchor (a patient pathway,
  a study protocol number) versus an administrative one. Named, not edged.
- **`retail_hospitality`, `logistics`, `resource_operations`, `engineering`** — all run policy
  libraries. The schema anchor's ruling applies: edges to all of them would be *"true and useless"*
  and would rebuild the industry forest ALIGNMENT removed.
- **`academic`** — deliberately unedged, following the anchor.

---

## proposed_fields

**One, and it is a seconding, not a mint:** `organization`, already proposed by the
`business_operations` schema row and independently by `construction_property`, which asks that it be
adjudicated once. The argument is not restated; what this row contributes to R1c is the case where
the key does the most work anywhere in the family. **Policy titles are globally repeated.** *Data
protection policy*, *Code of conduct* and *Expenses policy* exist at every employer a person has had,
at every supplier who sent them a copy, and in every downloaded template pack — and nothing else in
this row separates them, because the title, the clause structure and the control block are identical
across employers. The seconding carries the schema row's seeded-ineligible caveat with it, because
the same property makes the key dangerous: in a single-employer corpus it names the user's employer
above everything they have ever filed, which is 00's *"use an author or organization merely as a
collector"* failure.

**Deliberately NOT proposed, and this is the more useful signal for R1c:** a controlled-document
identity key (document reference + version). The row wants one and should not have one —
`version_family` is already a universal fact and already does the job. Minting a domain key for it
would be the version-family trap in field form.

No other field is proposed. PR-6 forbids field rows on this schema and D1's deferral stands.

---

## NEEDS-JOSEPH

- **NJ-BO-8 · The acknowledgement residue.** *Renumbered.* The gist filed this as NJ-BO-6, which
  `business_operations.compliance-audit` already uses for a different question (its dependence on
  NJ-3). R1c should note the clash; I did not edit the sibling. The substance: the main question —
  policy or hr — is **settled** by the schema anchor and this row now complies. What remains is that
  `hr` is unwritten, so an acknowledgement routes to Protected Records today, which is safe but
  loses the join to the policy it attests: *who has signed v4.2* becomes unanswerable. Alternatives
  and costs: **(a)** wait for `hr` — safe, question unanswerable meanwhile; **(b)** let this row hold
  the acknowledgement as a grouped member with `hr` governing it — answers it, and puts a staff
  roster inside a row whose posture is built for published documents; **(c)** hold only the
  acknowledgement's policy-side facts here and none of its person-side facts — correct in principle,
  and it depends on member-level fact scoping this pass cannot confirm exists. Stated reciprocally
  for the `hr` author.
- **NJ-BO-9 · The undated policy.** The row's one passing leg is the control block, and a large
  share of real small-organisation policies have no control block at all. They currently route to
  Review Later. If that share is large in a real corpus, this row fires far less than its scope
  suggests — which is not a reason to widen the signal (widening it means falling back on the
  never-alone evidence that refused two sibling rows), but it is a reason for R1c to know the row's
  recall is deliberately traded for its precision. The alternative — accepting normative-clause
  structure alone as sufficient — would fire on every website privacy policy and downloaded
  template on the disk. I recommend against it and did not take it.
- **NJ-BO-10 · The in-family policy slivers.** Four siblings list policy material in their own
  `work_types` (`risk-register`, `vendor-management`, `facilities-workplace`, `support-operations`).
  Edges are now written from this side with boundaries in both directions, but those four rows were
  written without them and owe the reciprocal. This is the near-miss version of the defect that
  refused `construction_property.compliance-certificate`, and R1c should confirm the split rather
  than inherit it.
- Carries **NJ-J-IND-4** by inheritance from the schema row: the exposed party here is frequently
  not the user — a former employer's internal handbook — and no safety flag reaches this family.

---

## What changed in this pass

**Preserved unchanged** (verified correct, not rewritten): the whole `recognition` structure bar two
entries; `proposed_context_terms`; `work_types`; `grouping_reasons`; `template.why`; `file_kinds`;
seven of the nine original `file_examples`; all five `falls_through_to` entries; six of the seven
original `collides_with` edges; every quotation, all re-verified verbatim (`grep -c -F` = 1 each).

**Changed:**

1. **The node test is now argued leg by leg, and its verdict is narrower.** Legs 1 and 3 are
   conceded as failures; the row stands on leg 2 alone. **This reverses the gist's privacy-rules
   claim**, on the schema anchor's settlement of the acknowledgement seam.
2. **`sensitivity_why` rewritten.** The gist drove the value from the acknowledgement roster, which
   is no longer this row's material. Three residual grounds now carry it, all inherited from the
   schema rather than distinctive — and the memo says they are inherited.
3. **`open_question` replaced and renumbered** to NJ-BO-8, with three alternatives and their costs,
   and the NJ-BO-6 clash with `compliance-audit` flagged.
4. **`also_holds_with` populated** (was empty) with the `hr` container case, which the schema anchor
   names explicitly and the gist missed.
5. **Two `file_examples` added**: `Handbook acknowledgement - J Patel - signed.pdf` (the
   reverse-direction collision fixture the gist lacked) and `Privacy Policy.pdf` (the commonest real
   false positive, previously only a `never_alone` mention). The acknowledgements spreadsheet
   example was corrected to route to `hr`.
6. **Four `collides_with` edges added** — `risk-register`, `vendor-management`,
   `facilities-workplace`, `support-operations` — found by reading the four siblings' own
   `work_types`, each with the boundary in both directions and shared fixture bytes named. The
   `hr.onboarding-offboarding` edge was rewritten from an observation into a settled reciprocal.
7. **Two `never_alone` entries strengthened**: the version token now carries the universal-facts and
   content-hash quotations, closing the version-family trap explicitly; and an **empty** control
   block is now itself never-alone.
8. **`proposed_fields` populated** (was empty) with the `organization` seconding, plus the explicit
   refusal to mint a controlled-document identity key.
9. **`one_line` rewritten** to lead with the control block rather than with the document type, and
   to state the `hr` split rather than claiming the acknowledgements.
10. **Sections added to this memo** that a gist skipped: files considered and rejected (12 named),
    the two-direction collision fixture, the reciprocal boundary table (12 neighbours), the `hr`
    seam written for the `hr` author, the point-by-point answers to the two sibling refusals, and
    this section.

**Deliberately not added.** No edge to five sector schemas that all run policy libraries; no
time-first claim; no widened detection signal to catch undated policies; no minted field. Each is
argued above rather than silently omitted.
