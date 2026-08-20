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

*(filled by the domain agents)*

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

## D. P1–P5 audit questions

*(filled by the audit agents)*

## E. Carried forward from earlier sessions

| # | Question | Blocks | My assumption |
|---|---|---|---|
| E1 | The 42 `uncertain` rows in `planning/deferred-catalogues/` are still unresolved — entries I could not classify from a citable source. | The gazetteers cannot ship complete. | Left `uncertain`, not guessed. |
| E2 | `.pages`, `.key`, `.swift`, `.ts`, `.go` route as `unsupported`. §2.4 and §2.9 do not name them. | Those files get a filename and nothing else. | Spec-faithful: left unrouted rather than invented. |
| E3 | `.numbers` routes as a spreadsheet, but a real Numbers file is often a **package**. P3 Q7 (packages) is open. | A silent empty extraction on a common Mac format. | Left as the SPEC's routing says. |
| E4 | Filename normalization NFC vs NFD (P3 Q1) is open; macOS stores NFD. | `normalized_filename` is P3's raw `path.name`, so it is not actually normalized. | Passed through unchanged, and P5 labels it `direct` metadata. |
