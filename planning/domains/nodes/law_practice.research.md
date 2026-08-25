# `law_practice` — lab notes (schema anchor, J-IND row written at J-DEPTH)

The largest unwritten family on the roster: **36 templates**, every one of which measures its node
test against the default template stated here. So this memo spends most of its length on two things
the 36 authors actually need — the charge against the schema's existence, answered first, and the
default template, stated precisely enough to be *differed from*.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — every quoted span in the JSON and in this memo was
  machine-checked with `grep -F` against this file before writing. 39 spans checked in the first
  pass; a second automated pass over the finished JSON extracted every `"…"` span of 15+ characters
  and re-checked all of them against `00` **or** against the landed node file the span was borrowed
  from. Result: **0 unverified.** The script is reproduced at the end of this memo.
- `planning/domains/_CONTRACT.md` (rules 10 and 15), `CONNECTION.md` §2 (the node test), §4 step 5
  (protective ordering), PR-6 (fieldless placeholder schemas).
- `planning/domains/canonical_fields.json` — `client` and `our_firm` are **already canonical**. That
  single fact changed this row's `proposed_fields` from a mint list into a reuse list.
- `planning/domains/ROSTER.md` §4 line 81 and lines 610–652 — the 43 `law.*` legacy ids and where
  each landed. `law.matter-file` FOLDs to the existing `legal.practice-matter-file`; 36 become
  `law_practice.*`; six FOLD into siblings.

### Landed neighbours read in full, and not edited

`legal`, `legal.practice-matter-file`, `legal.personal-legal-matters`, `legal.leases-agreements`,
`legal.estate-planning`, `clinical_practice` (+ its memo's node-test and default-template sections),
`business_operations` (+ its never-alone principle section), `business_operations.organisational-records`
(the refusal and its two-role closure), `business_operations.contract-administration`, `nonprofit`,
`government`, `career.consulting-client-engagement`, `clinical_practice.malpractice-incident`,
`construction_property.subcontract`, `hr`.

---

## The charge, answered first: **is this `legal` with a practising certificate?**

It very nearly is, and the row has to earn the difference rather than assert it.

**What would have made it a refusal.** If the only discriminator were *a lawyer produced these
bytes*, the row is dead on arrival: a practising certificate, a bar number, a firm letterhead and a
regulated-profession footer are all **role names**, and a role name is never-alone evidence. The
generalised rule is already written in this project, in `business_operations`' memo:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.**

A schema resting on "a solicitor made it" would fail activation at CONNECTION §4 step 2 on every
file, and 36 templates would hang off a row that never fires. That is the counterfactual, and it is
recorded verbatim in the JSON's `collides_with.legal` entry so it cannot be lost.

**Why it is not a refusal.** Run the **deletion test** that
`business_operations.organisational-records` states — *delete every entity name and every
document-type word, and see what survives.*

| File | After deletion | Verdict |
|---|---|---|
| Law-firm letterhead on a PDF | nothing | struck — this is the charge, conceded |
| Conflicts screen | a labelled slot set: prospective-client / matter-description / responsible-practitioner / search-result / review-action | **survives** |
| Time-recording export | a column set: matter-ref / fee-earner / activity / units / rate | **survives** |
| Limitation diary | a portfolio table: one row per matter, key-date column, owning practitioner | **survives** |
| Privilege log | one row per withheld document: author / recipient / date / stated basis | **survives** |
| Precedent bank | an instrument with **empty** party and execution slots and drafting notes | **survives, inverted** |
| File-closure record | outcome / undertakings-discharged / papers-returned / **retention date** | **survives** |

The decisive observation is not that these files exist. It is that **`legal`'s own deterministic
signals do not fire on a single one of them.** `legal` activates on an executed-instrument structure
(a bound party pair plus an execution or notarial block) or a proceeding structure (a tribunal
caption plus a matter-identifier slot). A conflicts screen has no party recital, no execution block
and no caption. Neither has a time export, a diary, a review log or a closure record. And the
precedent bank is `legal`'s **photographic negative** — an instrument whose party and execution slots
are blank *by design*, which is exactly the evidence `legal` requires, deliberately absent.

So the answer to the charge, in one sentence: **`law_practice` holds the apparatus by which matters
are run, which is a class of artefacts the `legal` schema's recognition cannot see at all;
`law_practice` does not hold the instruments and proceeding records that apparatus produces, which
stay `legal`'s on `legal`'s own evidence and at `legal`'s safety protection.**

**And the neighbour says so itself.** `legal.practice-matter-file`, landed and unedited, records:

> "J-IND authorizes gist-level professional recognition now and defers full industry depth, so this
> row does not recreate practice areas, litigation phases, transaction types, or the dozens of
> sibling schemas from the overnight catalogue."

That row is a *marker that deferred the detail*. This schema is where the deferral lands. Their
relationship is stated as a `collides_with` entry rather than smoothed over — see NJ-LP-2.

**The two-role leg, cited and not re-derived.** `clinical_practice.patient-chart` established that
*a row supported by a relation between two labelled roles is not a row supported by never-alone
tokens*, because the never-alone failure is role ambiguity and two separately-labelled roles resolve
it. A practitioner block and a client block, separately labelled and filled by different parties, is
precisely that shape. But `business_operations.organisational-records` closed the lazy version of
that escape, and its four tests are applied here honestly rather than invoked:

- *(a) the relation must define the row, not be a property some files have.* Here it does: the
  schema's activation **requires** the two-role structure plus a matter anchor. The definition is
  positive, not a subtraction.
- *(b) two labelled parties, not two tokens.* A firm name beside the word "matter" is two struck
  tokens and is explicitly listed in `never_alone`.
- *(c) the pincer — if the roles are present, is the pair already a sibling's whole node?* This is
  where the row could still have died, and the answer is no: the pair-plus-matter-anchor structure
  belongs to no landed row. `legal.practice-matter-file` recognises it but is a *template* that
  inherits a safety schema's default and can host nothing.
- *(d) patient-chart never rested on two roles alone.* Nor does this: its independent leg is the
  **apparatus** table above, which survives the deletion test without reference to any role name.

---

## Did this row survive the node test? All three legs

`kind: schema`, so CONNECTION §2 asks whether the field set is genuinely distinct.

### Leg 1 — a distinct field set: **unsatisfiable, and not quietly satisfied**

Same as `clinical_practice`, and for the same three reasons that outrank the dispatch prompt:
`_CONTRACT` rule 15 permits a placeholder schema to carry no field rows, CONNECTION PR-6 makes the
placeholder schemas `kind: schema` rows with an empty field list, and ratified J-IND makes the new
professional schemas placeholders. **The leg cannot be run as written, and it is recorded as not
passed rather than as passed.** It is unsatisfiable identically for `hr`, `clinical_practice`,
`nonprofit` and every other J-IND schema; that is a roster-wide question, not this row's to answer.

What *can* be said, and is one notch stronger than `clinical_practice` could say: **the field set
this schema would be built on is nameable, and four of its six keys already exist.** `client` and
`our_firm` are canonical; `work_type` and `project` are canonical; `subject_of_record` and
`fiscal_period` are live proposals from three other rows. A schema that can name its 3–6 fields
without minting a single new key is not a schema that "would need a giant form" — it is a schema
blocked by PR-6 and nothing else. That is filed as a request for adjudication, **not** as a
satisfied check. See `open_question` (1) and NJ-LP-1.

### Leg 2 — detection signals of its own: **passes, and carries the row**

Three signals in `recognition.deterministic` belong to no other roster schema:

1. **The intake-and-conflicts structure** — the family's cleanest signal precisely because it is the
   file `legal` cannot see. A labelled slot set with no instrument and no caption anywhere on it.
2. **The matter-reference-keyed operational table** — the time-and-disbursement column set and the
   limitation diary's portfolio shape. The discriminating column is *matter reference*; without it
   an issuer-and-billed-to structure is finance's and a project column is business_operations'.
3. **Inverse recognition: the precedent bank.** An instrument-shaped file with deliberately empty
   party and execution slots. This is the family's structural mirror of
   `clinical_practice.protocol-guideline`, and like it, it is the one part of the family that is
   *not* protected material — no client, no matter, no third party — which is why its residual is
   Reading Inbox and not Protected Records. A signal defined by a designed **absence** of the
   neighbour's signal is not a signal any neighbour can also claim.

The privilege log is arguably a fourth, and it is the family's most distinctive single artefact, but
it is folded into the disclosure-review signal because it is a stage of one exercise.

**Verdict: passes.**

### Leg 3 — privacy rules of its own: **passes, and passes hardest**

Four rules here are not `legal`'s, argued in full in `sensitivity_why`:

- **The exposed party cannot consent.** `legal` protects the holder's own record; the holder can
  consent to what happens to it. Here the party is a client, an adverse party, a witness, a
  deponent, an accused or a child — and in the adverse-party and witness cases has *no relationship
  with the holder at all*. This is `clinical_practice`'s argument, one degree weaker in kinship and
  one degree stronger in consent: a patient at least chose their clinician.
- **Bulk.** A privilege log is not one file's exposure; it is N people's, and its sensitivity scales
  with row count. `clinical_practice`'s multi-subject list rule read across, biting harder because
  the rows are *other people's correspondence metadata*.
- **Existence is disclosive.** That a named person appears in this corpus can imply they are being
  prosecuted, divorced, investigated, deported or sued, before any content is read. Hence the
  family's hardest rule is a **naming** rule rather than a content rule.
- **Privilege is never inferred.** The literal label is preserved as an observation; the product
  decides no legal status, scope or waiver. Carried up from the landed neighbour, which states it.

**Verdict: passes.**

**Overall: kept, on legs 2 and 3, with leg 1 recorded as unsatisfiable rather than satisfied** —
the same margin `clinical_practice` reported, and the row says so in its own `open_question`.

---

## The default template — the paragraph all 36 templates must differ from

`template.dimension_order` is `[]`, **three times over**, and the three reasons are independent:
(1) by contract, no fields to branch on; (2) by the safety neighbour, since `legal` co-activates on
much of this material and no deep template unlocks from safety activation; (3) **by disclosure —
and this reason survives even if D1 lifts, so it is the one every sibling must answer.**

The recommendation held as prose:

> The **client** only where the corpus genuinely spans more than one **and the user has explicitly
> approved a client-named branch** → the **matter** → the **document function** → the **period**,
> last. Never a named third party at any level. Not time-first.

Why each clause:

- **Client seeded ineligible.** In a single-client corpus it is `00`'s own validator failure — *"use
  an author or organization merely as a collector"* and *"create meaningless one-child levels"*. In
  *any* corpus it is a disclosure: *"A visible client or matter label can itself disclose the
  existence and subject of a representation."*
- **Function after matter**, because a child is unintelligible without its parent — *"A work type
  such as Homework 3 is meaningful only after the course is known"*. An "amendment", a "schedule" or
  a "supplemental list" means nothing without the matter it belongs to.
- **Never a named third party**, however strong the grouping axis — a path writes their identity
  where every later process reads it, against *"The default posture must therefore be local-first
  and data-minimizing."*
- **Not time-first**, and no sibling may claim otherwise. Nothing here is capture-based, so
  `time_first: true` in this family is claiming the photos exception without the photos evidence.
  R1c should reject it on sight.

### Three family-wide principles the 36 must apply

**1. The document-kind principle.** *A legal document kind is a `work_type` value, not a node.*
Pleading, motion, order, brief, affidavit, exhibit, undertaking, completion statement — values. A
row justified only by "we hold motions" is the schema's default template with a narrower filename
filter. This is why `work_type` is in `proposed_fields`: it is the cheapest available way to stop 36
rows becoming 150. **Consequence, raised as NJ-LP-3 and edited nowhere:** the roster's `pleadings`,
`motions-and-briefs`, `orders-and-judgments` and `court-filing-record` differ from one another *only*
by document kind, and on this default template they are one row with four enum values.

**2. The practice-area principle.** *A practice area is a value, exactly as `clinical_practice`
ruled a specialty to be.* Family, criminal, immigration, IP, conveyancing, probate — values. But
the ruling has a real exception, and it is the most useful sentence in this memo for the six
practice-area authors: **a practice-area row survives only if it changes the privacy rule, never
because it changes the topic.** Three plausibly do — `family-law`, `criminal-defence` and
`immigration-casework`, where the *existence* of the file is disclosive about a child, an accused or
an immigration status. Those three must argue **leg 3** explicitly and must not argue leg 1 or a
document list. `ip-prosecution` and `conveyancing` look like registry-submission and transaction
situations under other names and should expect to be folded.

**3. The side rule.** Every file in this world has a side — practitioner or client, our side or the
other side, counsel or opposing counsel — **and the side is frequently unrecoverable from the
bytes.** When it is unrecoverable, abstain into Protected Records: *"Correct abstention is a
successful outcome because the product’s goal is reliable organization, not maximum file
movement."* Read across from `business_operations`' own side rule, and it is sharper here because
getting it wrong exposes *the holder's own* affairs (see the under-firing fixture).

---

## What this schema gives away

Following `nonprofit`, which conceded nine-tenths of its plausible content and kept a defensible
tenth. This row concedes, by name and in the JSON:

| Ceded to | What |
|---|---|
| `legal` | every executed instrument and proceeding record inside a matter — pleadings, orders, judgments, settlements, executed transaction sets, closing instruments, sworn statements. Safety protection runs first. |
| `legal.personal-legal-matters` | the holder's own position in their own dispute |
| `business_operations` / `hr` / `finance` | the **firm running itself** — practice accounts, its own lease, marketing, IT, procurement, PII renewal, its own HR files |
| `business_operations.contract-administration` | the contract register, including a law firm's register of its own supplier contracts |
| `finance` | the issued bill, **and the client account** — the client/office partition is an accounting partition on a real account, and a partition does not claim the account (nonprofit's restricted-fund concession, read across) |
| `government` | the court's, tribunal's, prosecutor's and regulator's own side |
| `career.credentials-licenses` | the practising certificate and the CPD log — hence the recommendation that `law_practice.admission-cle` be **refused** |
| `clinical_practice.malpractice-incident` | the clinician's own incident record, even when a solicitor is later instructed |

What is kept is the tenth: **the apparatus**.

---

## Files considered and rejected

Named because a row that only lists what it holds has not been researched.

- **A published opinion, statute, practice note or textbook.** Public reading material with the same
  vocabulary and the same caption structure. Reading Inbox. Topic cannot separate it; *"purpose
  answers what the file was for"* is the only test that works.
- **`LICENSE.txt` at a repository root.** `legal`'s own collision fixture, struck by `00`'s
  project-root marker rule. Not reached here at all — but listed because "legal-sounding text" is
  the family's cheapest false positive at corpus scale.
- **A terms-of-service or EULA PDF.** Instrument vocabulary with no bound party pair. Nobody's.
- **A consulting statement of work.** `legal.practice-matter-file` already named it; this row
  reuses that seam rather than re-deriving it.
- **An insurance policy, an HR policy, a commercial NDA.** All carry privileged/confidential
  labelling and legal vocabulary. All struck by the label rule in `never_alone`.
- **A law firm's own recruitment pack, pitch deck or website export.** `business_operations`. A firm
  name is never-alone in both families.
- **A court's own listing sheet or registry record.** `government`, by side.

## The collision fixtures, both directions

Both are in the JSON, and the second is the more important.

**Over-firing — `Order - Hartley v Nash - sealed.pdf`.** A caption, operative paragraphs, a court
seal, a counsel block naming the holder's firm, inside a matter-referenced folder. Everything says
"this family". **It is `legal`'s**, on `legal`'s own signal, and this schema co-activates without
displacing. The row concedes it in `must_not_conclude`. The folder name supplies nothing — a folder
is an unlabelled position.

**Under-firing — `Ellis and Co - Client Care Letter - my divorce.pdf`.** *Every* token that looks
like practitioner-side evidence is present: a firm letterhead, an allocated matter reference,
engagement structure, hourly rates, professional vocabulary. **The holder is the client.** The
discriminating evidence is which signature block is the holder's, and whether the practitioner-side
apparatus exists in the corpus at all. This is the fixture the family most needs, because the cost
of getting it wrong is not a misfiled document — it is the product treating the user's own divorce
as a work product. It is named on both sides of the `legal.personal-legal-matters` seam.

A third worth flagging: **`LPC Skills - sample client attendance note (marked).docx`.** The legal
profession teaches by producing exact replicas of its own artefacts, so structure alone cannot
separate a training exercise from a real matter. `also_schema: academic`, residual Review Later.

---

## `proposed_fields` — six, and **not one of them is a mint**

This is the row's most deliberate result. The family's obvious mint is `matter`, and it is declined.

| Key | Status | Ask |
|---|---|---|
| `client` | **canonical already** | declare on this schema; `destination_eligible` conditioned FALSE unless user-approved |
| `our_firm` | **canonical already** | declare; already ineligible; requested to be *read*, never written into a path |
| `project` | **canonical already** | adopt as the matter anchor **instead of minting `matter`**; eligibility conditioned |
| `work_type` | **canonical already** | declare; its enum is where document kinds live — this is principle 1 in field form |
| `subject_of_record` | reuse of `clinical_practice`'s proposal (also adopted by `nonprofit`) | adjudicate once; ineligible here |
| `fiscal_period` | reuse of an existing 10-row proposal | nothing the other ten do not ask |

**Why `matter` is declined.** A matter is a bounded engagement with an opening, a reference repeated
across content-incoherent artefacts, and a closure — structurally what canonical `project` already
is, and `00`'s licence for the group is the same sentence: *"The documents are content-incoherent
but purpose-coherent."* Minting `matter` would put a second name on one concept and encode a
profession into a key, which is the very charge this schema had to answer. Recorded in the JSON so
that all 36 authors reuse rather than mint: **`matter`, `case_ref`, `file_number`, `engagement_id`
and `docket` are all variants of this one key and none may be minted.**

**What R1c must weigh against the reuse, unsmoothed:** a matter reference is *disclosive* in a way a
project name is not — `41127-0006 Hartley v Nash` names a dispute and two parties in one token — so
if `project` is adopted here it cannot inherit `project`'s canonical destination eligibility.

---

## Reciprocal boundaries owed to R1c

All eleven `collides_with` and all seven `also_holds_with` entries were **authored one-way here**;
this row edited no neighbour. The reciprocals owed:

- `legal` and `legal.practice-matter-file` — neither could have anticipated a sibling schema.
- `legal.personal-legal-matters` — the role fork, named on both sides in prose, on one side in JSON.
- `business_operations.contract-administration` — the portfolio-table-with-a-date-column seam.
- `finance` — the bill and the client account.
- `government`, `hr`, `clinical_practice.malpractice-incident`, `career.credentials-licenses`,
  `career.consulting-client-engagement`.

---

## NEEDS-JOSEPH

Six, spelled out with alternatives in `open_question`. In brief:

- **NJ-LP-1 — the existence question.** Answered as a narrow YES and recorded so it can be reversed.
  If the practitioner role is judged a field value rather than a structure, the correct outcome is
  refusal and the coverage routes to the eight neighbours above plus Protected Records. This row
  would rather be refused than kept to save 36 ids.
- **NJ-LP-2 — the two-row question.** The roster keeps both the marker and this schema. Preference
  if one must go: **keep the schema, fold the marker** — a template cannot host a default template
  against which 36 node tests are measured. This row touched the marker not at all.
- **NJ-LP-3 — the document-kind fold.** Highest leverage: four roster rows differ only by document
  kind and are one row on this default template. Same charge owed against `discovery` vs
  `evidence-exhibits`, and `settlement` vs `orders-and-judgments`.
- **NJ-LP-4 — the practice-area rows.** Survive only on leg 3. Three plausibly do; two should expect
  to fold; `admission-cle` should be refused.
- **NJ-LP-5 — the in-house boundary.** An in-house team's client is its own employer: two roles in
  form, thin in substance. Three alternatives stated; this row prefers admitting it and cannot
  settle it.
- **NJ-LP-6 — the safety-ordering residue.** `legal` carries `is_safety_domain` and usually
  co-activates, so protective ordering usually runs — but **not on this schema's own characteristic
  files**, which are exactly the ones `legal` cannot see. `clinical_practice`'s NJ-CP-SAFETY and
  `nonprofit`'s NJ-NP-3 restated at a sharper point, with the uncovered files named.

---

## Audits run before returning

1. `python3 -m json.tool planning/domains/nodes/law_practice.json` → **parses.**
2. Key set compared programmatically against `nonprofit.json` → **identical, in order.**
3. Every `"…"` span of 15+ characters extracted from the finished JSON and re-checked against
   `00-database-agent-product-design.md` or the landed node file it was borrowed from →
   **0 unverified.**
4. `fields: []`, `launch: "placeholder"`, `kind: "schema"`, `template.dimension_order: []`,
   `time_first: false` → all as required by PR-6.
5. Every neighbour id in `collides_with`, `also_holds_with` and `role_split` checked to exist on the
   roster; no id invented.
6. No canonical key minted; six `proposed_fields`, all reuses, four of them already canonical.
7. Files written: **only** `planning/domains/nodes/law_practice.json` and this memo. No roster,
   prompt, canonical-fields, `src/`, or other-node edit. `resource_operations` and the three
   `creative.*` rows owned by CODEX were **not touched**.
8. Claims in this memo re-read against the JSON actually written — the concession table, the six
   `proposed_fields`, the three principles and all six NJ items appear in the JSON, not only here.

The verification script from audit 3:

```python
obj = json.load(open('planning/domains/nodes/law_practice.json'))
qs = {m for s in walk(obj) for m in re.findall(r'"([^"]{15,})"', s)}
bad = [q for q in qs if q not in design and not any(q in v for v in node_files.values())]
```
