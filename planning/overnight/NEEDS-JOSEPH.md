# NEEDS JOSEPH — decisions only you can make

Date: 2026-08-21 (overnight run)
Status: **accumulating.** Nothing here was decided for you.

Each row is a question I refused to answer because answering it would be inventing
your product rather than building it. Where I had to proceed to keep working, the
assumption I made is stated so you can overturn it cheaply.

## How to read this

| Column | Meaning |
|---|---|
| **Blocks** | what stays wrong or unbuilt until you answer |
| **My assumption** | what the code/plan does today, so nothing was silently decided |
| **Cost to change** | how expensive your answer is to apply if it differs |

---

## A. Scope and jurisdiction

*(filled by the domain agents)*

## B. Domains — the schema and template calls

### B1 · **The most important one.** A 500-domain catalogue and P6's Done-means 2 cannot both stand

§3.11 states the mechanism the whole domain catalogue implements:

> "The fields used to describe files should not be one enormous universal list. The product should
> have a small shared set of universal file facts, such as file type, creation date, language,
> duplicate family, version family, and sensitivity status. It should then **activate
> domain-specific schemas only when the evidence indicates that a domain is plausible**."

It then gives a table of **six** domains — Academic, College applications, Research, Finance,
Photos, Code — with about five fields each.

**P6's SPEC turned that table into a closed list.** Done-means 2 restricts the field catalogue to
the six universal fields, `download_session` and the six §3.11 domain sets, *"and no field outside
them"* — roughly 37 fields total.

The catalogues you asked for currently define **1,287 distinct field names across 324 domains**, and
five more catalogues are still landing.

**My reading, and I want you to check it.** The design's six rows are *examples of a mechanism*, not
the mechanism's whole output — the sentence that carries the rule is "activate domain-specific
schemas", and "should not be one enormous universal list" is an argument **for** many small schemas,
not against having many of them. 1,287 fields is only "one enormous universal list" if they are all
live at once; under §3.11's own mechanism roughly five are active for any given file. On that
reading the catalogue is aligned with the design and **P6's Done-means 2 is the thing that is
wrong** — a SPEC over-constraining a design it was meant to implement.

**Review round 1 turned my reading into a proof.** §3.8 — a section P6's own slice table says it
owns — names four role fields outright:

> "The agent should model these as distinct facets, such as `authored_by` and `target_school`, or
> `our_firm` and `client`."

**None of the four appears in any §3.11 row.** And P6's own Done-means 13 and Done-means 22 both
require `authored_by` to exist. So Done-means 2 forbids a field two other Done-means items require,
and Task 2 as written forbids the field Tasks 9 and 24 must test.

That settles the direction: the closed reading is not merely restrictive, it is **internally
impossible**. §3.11's table cannot be a closed list, because §3.8 states fields outside it as
plain design text. What remains yours is only *how far* it opens.

**What you need to decide:** does the field catalogue open fully — §3.11's six rows as a seed, the
500-domain catalogue as its growth — or open narrowly to §3.8's four plus §3.11's, with the domain
catalogue becoming a routing aid rather than a fact schema? Everything about P6's shape follows.
**Cost to change: low now, very high after P6 is built.** This is the decision I would most want
made before Task 1.

**Cost to change:** low now, very high after P6 is built. This is the decision I would most want
made before Task 1.

### B2 · The field-name conflict reaches further than P6

C15 below records that §3.1, §3.2 and §3.12 say **`subject`** while §3.11's Academic row says
**`course`**. The domain catalogues have now picked `course` (5 entries) *and* `subject` (5 entries)
— because both are defensible and nobody has ruled.

Same for capture: §3.1 and §3.2 use `capture date = 2026-07-17` as a worked example; §3.11's
universal set has **`creation date`** and its Photos row has **`capture year`**. `capture date` is in
neither. Four catalogue entries use `capture date`, none use `creation date`.

So this is not a P6 detail — it is a naming rule that 324 entries and counting are already applying
inconsistently.

### B3 · Two naming conventions in one namespace

The catalogues carry both `record type` / `artifact type` (spaced, matching §3.11's own style) and
`case_identifier` / `matter_reference` (snake_case). §3.11's table is spaced, so spaced is the
design's convention — but nobody said so, so authors split. Mechanical to fix once you confirm
spaced wins; I have not applied it, because renaming 1,287 fields on my own reading is exactly the
kind of silent decision this document exists to prevent.

**Found twice independently.** Review round 1 hit the same split inside the plans: §3.11's table
writes `work type`, `target university`, `media type`; the P6 SPEC's own `fields` example writes
`work_type`, `target_university`. So the inconsistency is in the SPEC as well as the catalogues.
**One rule closes both.**

### B5 · Four more from review round 1

| # | Question | Why it is yours |
|---|---|---|
| B5a | **What row does P6 write while OQ10 is open?** Two `validated` facts asserting conflicting course codes on one file. None of the thirteen `unresolved` reasons can name that situation, and B7 forbids writing nothing. | The answer to OQ10 can wait; the *row* cannot. |
| B5b | **Which of P4's nine `completeness` values imply `unreadable_unclassified`?** §8.4 names five handling classes and never mentions extraction completeness. The SPEC states one mapping; the other eight decide whether a real file is releasable. | P7's first constraint is that it owns no detection rule, so it cannot invent the other eight. |
| B5c | **Was W1 ratified?** `07-fidelity-audit.md` heads it *"Nearest faithful fix (not applied)"*, and P7's SPEC adopted it verbatim and now tests it as contract — including "where the design is silent on a redaction default, the more redacting option is the default." §8.4's `must` is real; that derivation is the audit's, not the design's. | It constrains what ships. |
| B5d | **`filename` as a releasable kind** — the one P7 open question its own plan left off its list. §8.4's releasable list is five and does not name it. | See C9a. |

### B4 · Jurisdiction

Three catalogues (tax, legal practice, government) independently raised the same question: this
product states no jurisdiction, and tax forms, court structures, permit regimes and certificate
names differ completely by country. Each wrote functionally where it could and flagged where it
could not. **Which jurisdictions ship at launch?**

## C. P6 / P7 plan questions

### C1–C7 · P7, the privacy and consent gate

From `planning/parts/P7-privacy-consent-gate/PLAN-SKELETON.md`. Each was refused rather than
guessed; the plan is written so your answer drops in without rework.

| # | Question | Blocks | My assumption |
|---|---|---|---|
| C1 | **Deletion vs append-only (I6).** §8.4 gives the user the right to "review and delete local derived data"; §8.2 requires an append-only log and forbids overwriting evidence. Which wins? What counts as "derived"? Are audit records themselves deletable? | P7 Task 15 outright. Also touches P1's core contract and P6's facts. | Nothing deletes. `delete_derived` refuses until you rule. |
| C2 | **Which mode is the install default** — `offline` or `local_model`? | Turns on whether a local model is assumed present at all. | Local-first, but the specific default is left unset. |
| C3 | **What is a "corpus area"?** `cloud_assisted` permits a cloud model for "selected corpus areas". A scan root? A frozen tree node? An accepted group? A domain? | Consent grants cannot be **scoped** until this is named. Affects P3, P9, P10. | Unscoped; the parameter exists and takes no default. |
| C4 | **Does `unreadable_unclassified` permit a *local* model call?** Strict reading blocks exactly the OCR-opaque screenshots §2.7 and §7.8 want interpreted. | P8 and P11. | Parameter has no default until you answer. |
| C5 | **Is `protected` exactly the top two handling classes?** §8.4 lists five classes and, separately, five kinds that "enter a protected state immediately", without stating the relation. | P9 (§4.9), P10 (§5.12's `protected` node type), P11 (§6.10). | Consume the `protected` flag; never infer it from the class. |
| C6 | **Identifier classes and the redaction transform.** The SPEC defers them; a shipped product needs them. | Real redaction. | Injected, with no default list. |
| C7 | **Retention.** How long are audit records, consent grants and superseded classifications kept? | Nothing today; it will matter. | Nothing is deleted (see C1). |

### C8 · The one that spans parts — `sensitivity` has three homes

Found independently by me and by the P7 planner, and flagged by P6's own SPEC (open question 11):

> `sensitivity status` is a universal *fact* (§3.11), a *sensitivity state* on the file record
> (§8.2), and a *handling class* in the privacy gate (§8.4). One record or three? Which part writes
> it, and does a user reclassification arrive as a `user_confirmed` fact?

**Three spellings exist right now**: `sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6),
`sensitivity_state` (P1's column — which exists and **nothing writes**). This is the defect class
that has cost this project the most, at the largest scale it has appeared. It is a decision about
which record is authoritative, not something I can infer.

**Standing rule until you decide:** a part that does not own the concept passes `None` and says the
value is unknown. It never forwards a neighbour's column because the shapes line up. I applied that
tonight — P2's `handling_class` was being fed P1's `sensitivity_state`; it is now a literal `None`.

### C9 · Where the P7 SPEC and §8.4 differ, and the design wins

| # | Difference | What I did |
|---|---|---|
| C9a | `filename` is **not** one of §8.4's releasable kinds — the design names five ("selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata, and evidence references") and puts *Paths* in the always-local set. The SPEC adds a sixth. | Recorded; the design wins. The SPEC flags it itself. **Your call.** |
| C9b | The SPEC calls its three protected consequences "verbatim from §8.4"; they are faithful in substance, lightly normalized in grammar. | The plan stores §8.4's sentence, not the SPEC's rendering. |
| C9c | Mode identifiers (`offline`, `local_model`, `hybrid`, `cloud_assisted`) are the SPEC's; §8.4's names are "Fully offline mode", "Local-model mode", "Hybrid mode", "Cloud-assisted mode". | Both pinned, identifier-to-display-name. |

### C11–C14 · P6, facts and facets

From `planning/parts/P6-facts-facets/PLAN-SKELETON.md`. The planner refused all four.

| # | Question | Blocks | Recommendation it gave |
|---|---|---|---|
| C11 | **The `no_usable_facts` cycle.** §2.2 permits targeted OCR "only when its stored evidence yields no usable facts" — but P6's pass needs P5's observations and P5's OCR decision needs P6's verdict. | Targeted OCR never fires today; a stub always says "fine". | **Four passes**: P6 resolves on native observations → P5 runs targeted OCR for the unresolved → P6 re-resolves. §3.4's cache key already makes the second pass a different key, so nothing is overwritten. |
| C12 | **Three event types P6 needs that P1 does not have** — value creation, value merge/alias, user fact correction. | P6's Provenance section promises three types that would raise at run time. | Ride them on `fact creation` / `fact rejection` for v1 (no P1 change; I4's read keys on `proposal_class` + `basis_key`, not event type) — **and say so in the SPEC**. |
| C13 | **Five naming questions, four of them the same underlying issue** (see C15). | Five Done-means items. | Settle OQ4 first, then apply the same rule to the rest. "An afternoon of naming that removes five blocked tests." |
| C14 | **Which fields are `destination_eligible`** beyond §3.8's rule that no authorship or creator-identity field ever is. | P10 cannot build a folder template against a column nobody filled. Not blocking P6. | — |

### C15 · The P6 SPEC contradicts the design on field names — **this one is important**

The planner verified these word by word. In each case the SPEC and the design disagree, and
**the design wins**:

- **`subject` vs `course`.** §3.1, §3.2 and §3.12 all say **`subject`** — "A fact is a statement such
  as `subject = BUSIB 4300`". §3.11's Academic row says `course`. The SPEC's Done-means 4 requires
  "exactly the three facts §3.2 names (**course**, term, work type)" and the field catalogue carries
  `course` with **no `subject` row at all** — while the SPEC's own OQ4 leaves the question open. So
  Done-means 4 answers OQ4 by fiat, and answers it against §3.2.
- **`capture date` vs `creation date` vs `capture year`.** Done-means 5 requires an EXIF
  `DateTimeOriginal` to produce **`capture date`**; Done-means 2 restricts the catalogue to a field
  list that contains **neither** — the universal set has `creation date`, the Photos row has
  `capture year`. §3.1 and §3.2 both use `capture date = 2026-07-17`. **Done-means 5 requires a field
  Done-means 2 forbids from existing.**
- Plus `document type` vs `application document type`, and two more.

Four of the five are one underlying issue: **the design states its field names once in prose and once
in a table, and the two do not match.** You need to rule once — table wins, or prose wins — and then
apply it. I did not pick.

### C10 · An ordering defect I introduced, and the shape of its fix

P6's SPEC: `no_usable_facts` is *"defined only after P6's deterministic pass on that content hash has
completed. Consulted earlier it would return `true` for every file and trigger OCR on the whole
corpus."* My Wave-2 caller consults it **inside** the extraction loop, where that pass cannot have
run. Harmless today only because every test injects a false constant.

Not a question for you — my defect, and I will fix it — but you should know the caller's shape
changes: one loop becomes native extraction → P6 pass → targeted OCR → a second P6 pass.

## D. The connection questions — from review round 4

### D1 · **Who writes the sensitivity classification?** Nobody, in thirteen parts.

This is the sharpest structural finding of the night and it is not a P6 or P7 defect — it is a hole
between all thirteen SPECs.

P7's Deferred section says the detector rule set is *"hand-authored"* and that *"P7 publishes the
vocabulary the detectors write into."* **No part's SPEC claims the detector.** So:

- `basis = detector` is a vocabulary member with no producer.
- `files.sensitivity_state` stays NULL after P7 ships.
- Every file is `unreadable_unclassified`, and §8.4's gate returns `Denied(unclassified)` for
  **everything**.

The privacy gate would work perfectly and deny the entire corpus, because nothing ever classifies a
file. **Who owns the detectors — a fourteenth part, P7 itself, or hand-authored configuration you
supply?**

### D2 · Four cross-part surfaces named by a consumer and produced by no task

| Surface | Named by | Produced by |
|---|---|---|
| `SensitivityFacts` protocol | P7 | **nothing** — zero mentions in 1,621 lines of P6's plan |
| `contradicts(claim, existing_fact)` | P8's Contract-in, as P6's | **nothing** — P6 Task 17 says "P6 owns none of the checking" |
| `normalize(field, raw_value)` | P8's Contract-in, as P6's | **nothing**, same reason |
| `StageAdapter` | P2, the connector between a stage and the replay machinery | **no SPEC at all** |

Both plans are careful about *columns* with no writer. Neither checks the converse — a **consumer
with no producer** — and that is where the wave breaks.

## E. P1–P5 audit questions

*(filled by the audit agents)*

## F. Carried forward from earlier sessions

| # | Question | Blocks | My assumption |
|---|---|---|---|
| E1 | The 42 `uncertain` rows in `planning/deferred-catalogues/` are still unresolved — entries I could not classify from a citable source. | The gazetteers cannot ship complete. | Left `uncertain`, not guessed. |
| E2 | `.pages`, `.key`, `.swift`, `.ts`, `.go` route as `unsupported`. §2.4 and §2.9 do not name them. | Those files get a filename and nothing else. | Spec-faithful: left unrouted rather than invented. |
| E3 | `.numbers` routes as a spreadsheet, but a real Numbers file is often a **package**. P3 Q7 (packages) is open. | A silent empty extraction on a common Mac format. | Left as the SPEC's routing says. |
| E4 | Filename normalization NFC vs NFD (P3 Q1) is open; macOS stores NFD. | `normalized_filename` is P3's raw `path.name`, so it is not actually normalized. | Passed through unchanged, and P5 labels it `direct` metadata. |

---

## B6 · Slice 11 — business operations, HR, strategy and management

Source: `planning/domains/11-business-operations.json` (45 entries, 11 open questions). Appended by the slice-11 author; nothing below was decided.

**B6.1 · `ops.business-records` — Organisational records (branch root)**

> TWO questions, both of which every entry in this slice inherits. FIRST — whose organisation is it? One person's Documents folder holds their employer's strategy deck, a client's brief, a supplier's quotation and their own household budget, and §3.8's our_firm/client discipline names the problem without deciding it. For most of this slice the discriminator is not in the document: an operating budget and a household budget are the same spreadsheet, and a performance review the user received and one they wrote are the same form. Does the product ask the user once for their own organisation and role — making it a user fact the way §4's user-approved folder is — or does it try to read the role per file and accept that it will often return unknown? SECOND — does §2.9's 'potentially sensitive' reach COMMERCIAL confidentiality, or only personal data? §8.4's corpus list is entirely personal: “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. A pre-announcement board pack, an unsigned term sheet and a customer list are not personal data but are exactly the material a user would not want in a cloud prompt. This catalogue marks sensitivity on personal-data grounds only and leaves the commercial question to Joseph, because widening §2.9's phrase would silently widen P7's scope.

**B6.2 · `ops.okr-goals` — Goals, OKRs and scorecards**

> Whether an individual's goal sheet is an operations artifact or an HR record is not a property of the document — the same template is used for both, and organisations differ on whether goal attainment feeds pay. This catalogue routes it to `hr.performance-cycle` whenever a named individual is the owner, which is a conservative default rather than a decision. Joseph decides whether that default is right, because it determines whether the file is treated as sensitive.

**B6.3 · `ops.operating-plan-budget` — Operational budgeting and forecasting**

> A sole trader's, freelancer's or founder's budget is simultaneously a household budget and a business one, and no field in the document separates them — the finance slice raises the same problem for bank accounts and reaches the same wall. Whether the product asks the user to declare a business entity once, or accepts that this material is genuinely dual-homed under §4.9's “A file may validly belong to more than one accepted group”, is Joseph's call and it decides whether an operations branch and a personal branch both surface the same file.

**B6.4 · `ops.meeting-record` — Meeting agendas, minutes and notes**

> Meeting records are the clearest case in the slice where the personal and professional shapes are identical: a residents' association AGM minute, a school governor's minute and a departmental minute differ in no readable respect. This entry assumes an employer or client organisation is required and therefore silently declines volunteer and community meetings, pushing them to the personal slice. Joseph decides whether that is right, or whether one meeting domain should span both — which would make the meeting series, not the organisation, the top folder level.

**B6.5 · `ops.project` — Project delivery artifacts**

> Should there be ONE `project` domain across the whole catalogue rather than one per slice? §3.11 already gives `project` to Research and to Code, this entry adds a business instance, and the personal slice has its own. §3.12 says “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically” — so the field is shared and only the SCHEMA around it differs. Either the product has one project domain whose neighbouring fields vary, or it has four domains that will compete for every file containing the word. This catalogue cannot resolve it alone because the answer changes four slices; it is Joseph's.

**B6.6 · `ops.business-travel` — Business travel administration**

> Travel is a design-named domain owned by the personal slice, and this entry deliberately carves the employer's side out of it. The mixed trip — flights booked by the employer, a weekend added at the traveller's own cost, photographs from both — has no defensible split, and §4.9's “A file may validly belong to more than one accepted group” suggests it should simply be two memberships. Whether the product surfaces one trip in two branches, or whether business travel should not be a separate domain at all and should instead be a purpose facet on the personal travel domain, is Joseph's call. It matters because it decides whether a personal holiday can end up in a work folder.

**B6.7 · `ops.sourcing-rfp` — Sourcing events, tenders and bid evaluation**

> This entry is written from the BUYER's side. The same corpus, for a supplier-side user, contains the mirror image — the RFPs they respond to and the bids they submit — and every field inverts: their bidder becomes our organisation, their tender reference is someone else's. §3.8's “such as authored_by and target_school, or our_firm and client” names the role discipline that makes this expressible but does not say whether one domain with a role field or two domains is right. This catalogue routes supplier-side bidding to `ops.partnerships-bd`, which is a compromise rather than a decision, and it is Joseph's call because it determines whether a consultancy's proposal library and a buyer's tender file are one branch or two.

**B6.8 · `ops.client-engagement` — Client engagements and professional-services delivery**

> Client data received during an engagement is the sharpest privacy problem in this slice: it is a THIRD PARTY's personal and financial material sitting in the user's corpus, and none of the protections are about the user at all. §8.4 requires privacy be enforced before content reaches a model, and “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. Whether client-received data should be a distinct domain with its own treatment — rather than a work type inside this one — is Joseph's call, and it is the decision most likely to be regretted if made implicitly. SECOND: this domain is authored THREE times across the catalogue — here, as `career.consulting-engagement` and as `studio.client-engagement` — with near-identical templates. §5.7 names client engagements once; three entries answer it. Which one owns non-creative, non-freelance professional services is a merge decision, not a recognition problem.

**B6.9 · `hr.job-requisition` — Job requisitions and role definitions**

> FOUR entries in this catalogue duplicate four in the career slice rather than bordering them. `hr.job-requisition` / `career.employer-job-requisition`, `hr.recruiting-pipeline` / `career.employer-candidate-packet`, `hr.interview-panel` / `career.employer-interview-scorecard` and `hr.offer-package` / `career.employer-offer-approval` describe the same artifacts, key on the same requisition id, and differ only in whether the organisation or the requisition leads the template. This is not a boundary that better recognition would sharpen — it is one domain authored twice, and §3.6 “that each fact or label belongs to an allowed domain schema” cannot arbitrate it, because a fact belonging to two allowed schemas passes validation in both. Either the career slice keeps employer-side recruiting and this catalogue drops these four, or the reverse; the split cannot stand. This slice does not resolve it unilaterally because the two were authored in parallel and neither author has standing over the other. It is Joseph's, and it should be settled at merge.

**B6.10 · `hr.dei-program` — Diversity, equity and inclusion programmes**

> This entry names `characteristic_category` as a field but deliberately does not enumerate its values. The list of protected or monitored characteristics is jurisdiction-defined and the categories are not translations of one another. More importantly, a catalogue that enumerated them would be instructing the extractor to look for them, and §3.7's conservative-facet-extraction discipline argues against building a gazetteer of characteristics at all. Whether this product should DETECT such material in order to protect it, or should decline to model it and let it fall to §7.3's Protected Records template — “Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials” — is Joseph's call, and it is the single most consequential question in this slice.

**B6.11 · `hr.employee-relations` — Employee relations cases**

> There is no `hr.personnel-file` entry in this catalogue, and there probably should be one somewhere: the employer's per-employee file is the natural home for contracts, pay letters, training records, reviews and case outcomes about one person. This slice deliberately declines to create it, because a per-person folder is exactly what §3.8's “It should avoid using authorship or creator identity as a destination dimension” warns against and because it collides head-on with the career slice, which holds the same documents from the individual's own side. Whether the product should model an employer-held personnel file at all — and if so, which slice owns it — is Joseph's call and it is left open rather than resolved by omission.

