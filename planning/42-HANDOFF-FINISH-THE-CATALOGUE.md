# Handoff — finish the domain catalogue

> # ✅ CLOSED 2026-08-27 22:11 — THIS HANDOFF IS DISCHARGED. DO NOT EXECUTE §7.
>
> **The catalogue is finished: 358/358 rows, 0 owed, 0 partial, 44 argued refusals.** The last 9
> rows (`creative.commissioned-shoot`, 4 × `logistics.*`, 4 × `manufacturing.*`) were written by
> CODEX and landed at 22:11. Every count in §2 below is stale (it says 329 complete / 27 owed /
> 40 refusals) and the "remaining work" in §4 is done as far as new rows go.
>
> **Running §7 now would re-research rows that already exist and overwrite finished work.**
>
> What is still owed is NOT in this document: it is the **R1c merge-and-gate**
> (`planning/prompts/01c-merge-and-gate.md`) over a closed corpus, plus the audit findings recorded
> in `planning/27-dispatch-run-log.md`. Start there instead.
>
> Kept unedited below for the history — the failure modes in §6 are still true and still worth
> reading before touching this corpus.

Date: 2026-08-27 · Written for the next agent, who should need nothing but this file and the repo.
Repo: `/Users/jy/GRAPH AGENT` (**the path contains a space — quote it in every shell command**).
Branch: `build/p6-p7-first-packages`, pushed clean at `103548d`.

**Paste the block in §7 into a fresh agent.** Everything above it is the context that block assumes.

---

## 1. What this is

A local-first file-organisation product. `planning/00-database-agent-product-design.md` ("`00`") is
the product design and the **only** authority; every other document defers to it. The catalogue you
are finishing is the library of **domain schemas** (which fact fields are legal when a domain is
plausible) and **domain templates** (which of those fields may become folder levels, in what
recommended order). One row per organisational situation, in `planning/domains/nodes/<id>.json`
plus `<id>.research.md`.

Precedence on any conflict, highest first:

```text
00-database-agent-product-design.md
planning/prompts/ALIGNMENT.md
planning/domains/CONNECTION.md          (+ CONNECTION-EXAMPLES.md, binding fixtures)
planning/domains/_CONTRACT.md           (entry shape)
planning/domains/dispatch/RESEARCH-BRIEF.md
any dispatch prompt
```

Ratified decisions live in `planning/overnight/council/DECISION-BRIEF.md` (D1–D6, plus **J-IND**).
**Follow the recorded state; never re-open a ratified decision and never close an open one.**
Notably D6 is ratified: snake_case keys, the academic field key is `subject`.

## 2. State right now — verified, not remembered

| | Count |
|---|---:|
| Roster rows | 358 |
| **Complete** (JSON + memo) | **329** |
| JSON-only partials | 2 |
| Owed (no files) | 27 |
| Of the complete, argued refusals | 40 |

18 of 25 families are 100% done, including every launch domain `00` names (academic, applications,
research, career, photos, code) and all four safety domains (finance, identity, medical, legal).
All 23 schema anchors exist, so every remaining template has the default template it is measured
against.

**Never work from a written list of what is owed** — that error once silently skipped five rows.
Recompute, every time:

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -c "
import json,os,collections
r=json.load(open('planning/domains/roster.json')); n=r['nodes'] if isinstance(r,dict) else r
N='planning/domains/nodes/'
todo=[x['domain_id'] for x in n
      if not os.path.exists(N+x['domain_id']+'.json')
      or not os.path.exists(N+x['domain_id']+'.research.md')]
print(len(todo),'owed'); print(collections.Counter(x.split('.')[0] for x in todo))
print('\n'.join('  '+t for t in sorted(todo)))"
```

The **memo clause is not optional**: a killed agent writes its `.json` first and its `.research.md`
second, so a row can have JSON and no memo. Selecting on `.json` alone marks those rows finished and
they are then skipped forever, carrying unverified, unargued JSON into the merge gate. Two such
partials exist right now (`nonprofit.advocacy-campaign`, `law_practice.estates-administration`).

## 3. Two teams write into this directory

`planning/29-DOMAIN-OWNERSHIP.md` is the claim register. **Claim before writing; release when done.**
A second team (CODEX) writes rows into the same folder. Rules that have already been violated once
and cost real work:

1. Edit only `nodes/<id>.json` and `<id>.research.md` for ids your team has claimed.
2. Never edit — or delete — a file inside another team's claim. Report it instead.
3. Never edit shared files (roster, canonical fields, prompts, `check.py`, `src/`, SPECs).
   Cross-row changes are **recommendations to R1c**, never edits.
4. **Commit by explicit file path. Never a wildcard** — a wildcard once swept unverified files in.
5. Do not stash, rebase, pull or reset while either team has uncommitted work. If a push is
   rejected, hold the commits locally and say so.

A third workstream (P6/P7) owns `src/` and `tests/` on this same branch and usually has dozens of
uncommitted files. **Ignore its churn entirely** — never revert, fix, commit, or flag it.

## 4. The remaining work, in order

### Step 1 — the last 29 rows

Recompute with §2's query. As of writing: `creative` 1, `law_practice` 7, `logistics` 4,
`manufacturing` 5, `nonprofit` 3, `resource_operations` 4, `retail_hospitality` 5.

Dispatch **one agent per row** using the prompt template in
`~/.claude-max/.../workflows/scripts/jdepth-wave2.js` (function `rowPrompt`) — or rebuild it from
§7's rules. Concurrency: the runtime caps agents at `min(16, cores−2)` **per workflow**, which is 6
on this 8-core machine. To run more in parallel, launch several workflows with **disjoint** row
sets — two agents on one id is a lost node.

`resource_operations.*` and `creative.commissioned-shoot` were CODEX's; check the register before
claiming them.

### Step 2 — R1c, the merge gate

`planning/prompts/01c-merge-and-gate.md`. This is the biggest remaining job.
`python3 planning/domains/check_edges.py` currently reports **~1,600 findings**, all judgement work:

| Finding | Approx | What it needs |
|---|---:|---|
| `collides_with` one-way | 1,072 | add the reciprocal, or record a `one_way_reason`. Per pair. |
| `also_holds_with` one-way | ~245 | same, co-activation side |
| `also_holds_with` on a template | ~196 | §5 restricts it to **schema ↔ schema**. **Lift** to the schema pair or **convert** to `collides_with` — guessing destroys the distinction |
| cross-kind `collides_with` | ~88 | §5 joins same-kind pairs only; lift or push down |

The count **rises** as rows land (a collision into an unwritten row is owed, not one-way) and will
fall sharply once the forest is complete. **Re-run the gate; never quote these numbers.**

R1c also owes: folding `check_edges.py` into `check.py` (which still does not scan `nodes/` at all),
adjudicating the **40 refusals**, and clustering `proposed_fields` — several concepts were proposed
independently by different families and must each be settled as **one** decision, notably
`subject_of_record` (three rows: clinical_practice, law_practice ×2) and `organization`
(business_operations and construction_property).

### Step 3 — two argued overlaps the auditors found

- `creative.film-production` / `.shoot-day-media` / `.post-production` compete for the same call
  sheets and `.prproj` files **with no edge between any pair**, and all three sit on a field-less
  schema so `dimension_order` cannot discriminate. Proposed split: shoot-day-media owns capture-day
  media, post-production owns the edit/master chain, film-production narrows to the production spine
  or is refused as the schema's default template.
- `finance.household-property` positively claims files that are the flagship examples of five
  `construction_property` rows; eleven rows collide *into* it and it names none of them back.
  Proposed discriminator: the owner's retained copy vs the professional's working copy.

### Step 4 — a family-level question, not five row failures

`nonprofit` has **refused 5 of 9 rows** (advocacy-campaign, governance, political-campaign,
standards-body, volunteer-management). `standards-body` refused on leg 1 "in the strongest available
way — not *the same signals as the schema default* but *signals that cannot activate this schema at
all*", because the `nonprofit` anchor makes a **non-exchange relation between two labelled parties**
its whole precondition. Four siblings then failed identically.

Decide it **once**: either the anchor is drawn too tight (governance minutes and volunteer rosters
are real filing worlds a charity keeps), or those ids were mis-specced and belong to
`business_operations` templates plus residual fallthrough — which is where each refusal already
routed them. **Do not simply re-fire the five**: the refusals are argued, and re-firing without
settling the anchor produces either the same refusals or five rows padded to avoid repeating them.

### Step 5 — re-audit, then finish

Both auditors (cross-family **overlap**, and **design-fidelity vs `00`**) returned **FAIL** and
neither has seen a repaired corpus. Re-run them plus both gates. **A repair that is not re-audited
is a claim, not a result.** Then the final review panel and the index doc.

## 5. Open NEEDS-JOSEPH — do not close these yourself

- `CONNECTION.md` §10: NJ-1 the "500+" counting rule · NJ-2 safety ordering · NJ-3 whether `purpose`
  is universal or Applications-scoped · NJ-4 where protected-record surfacing lands · NJ-5 whether
  browse `parent_id` ships.
- `ROSTER.md`: creative schema · travel schema · `target_school` vs `target_university` ·
  `people` / `programming_language` destination-eligibility · scholarship sponsors.
- `08-sensitivity-detector/RESEARCH.md`: twelve detector questions.
- `11-jurisdiction-values/RESEARCH.md`: **which jurisdiction ships in v1** — correctly left open.

## 6. Failure modes this project has actually hit — avoid repeating them

1. **The 574.** An overnight pass produced 574 flat industry *schemas* with 2,295 private field
   names, joined only by one-way collisions. `00` forbids "prematurely hand-authoring hundreds of
   specialized schemas". Schemas stay few; the library is **templates**.
2. **A fabricated quotation** shipped in source. Any span in quote marks attributed to `00` must be
   `grep`-verified verbatim **before** it is written. This is the worst failure here.
3. **Bare-string collision edges.** Five rows wrote `collides_with: ["neighbour-id", …]`, recording
   *that* they collide but not *how to tell the rows apart* — the only part P6 activation and the P8
   validator can act on. All edges must be `{"domain", "signal"}` objects.
4. **A hand-written owed list** silently skipped five rows of one family.
5. **A wildcard `git add`** swept unverified files into a commit.
6. **Padding a row to save an id.** `refuse_node: true` with an argued reason is a **success** — 40
   rows are refused and that is the node test working.

## 7. ─────── PASTE FROM HERE INTO THE NEXT AGENT ───────

You are finishing the domain catalogue in `/Users/jy/GRAPH AGENT` (**quote the path — it contains a
space**). Read `planning/42-HANDOFF-FINISH-THE-CATALOGUE.md` first, in full; it is written for you
and everything below assumes it.

Your job, in order:

1. **Finish the ~29 remaining rows.** Recompute what is owed with the query in §2 of the handoff —
   never from a written list, and the query must select on **both** `.json` and `.research.md`,
   because a row with JSON and no memo is an unverified draft, not a finished row. Claim ids in
   `planning/29-DOMAIN-OWNERSHIP.md` before writing. Dispatch **one agent per row**; to exceed 6
   concurrent, launch several workflows with **disjoint** row sets.
2. **Run R1c** (`planning/prompts/01c-merge-and-gate.md`) against the completed forest.
3. **Re-run both gates and both auditors** on the repaired corpus.
4. **Write the index** and update `planning/26-research-dispatch-state.md`.

Every row agent must:

- Read `planning/domains/dispatch/RESEARCH-BRIEF.md`, run
  `python3 planning/domains/dispatch/make_prompt.py <id>` for its stamped assignment, read **one**
  landed launch row for depth calibration (e.g. `nodes/legal.practice-matter-file.research.md`), and
  read its schema anchor's JSON.
- **Argue the charge first**: state the strongest case that its row should NOT exist (a work-type
  value, a document type, a lifecycle stage, a medium, a format, an organisation name — which is
  never-alone evidence — a row defined only by an absence, or a duplicate of its schema's default
  template). Then defeat it with evidence, or `refuse_node`. **A refusal is a success.**
- Hit **J-DEPTH**, whose six requirements are: evidence not assertion; the node test argued across
  all three legs; files considered **and rejected**; boundaries stated in **both** directions; a
  collision fixture (a real file that looks like its evidence and is not); open questions surfaced
  as NEEDS-JOSEPH. Memo target ~13 KB with a `Depth: J-DEPTH` header — reached by having more to
  say, never by padding. Do **not** imitate the 27–86 KB `business_operations` /
  `clinical_practice` / `construction_property` memos; the brief calls those debt, not exemplars.
- Write every `collides_with` / `also_holds_with` entry as
  `{"domain": "<roster id>", "signal": "SAME FIXTURE BOTH SIDES: <the one real file both rows would
  claim> — this row owns X, the neighbour owns Y, discriminated by <evidence item>"}`. Bare strings
  are the defect repaired this week. `also_holds_with` is **schema ↔ schema only**.
- Never fabricate a quotation — `grep`-verify any span attributed to `00` before writing it. No
  threshold numbers. No handling classes. Provenance is `design | inference | proposal`.
- Write **only** its own two files, the moment each is ready. Never edit a neighbour, the roster,
  `canonical_fields.json`, `check.py`, `src/`, or a SPEC — cross-row changes are recommendations
  recorded in the memo for R1c.

Read cheaply: `grep -n` into `00` for the phrase you need rather than reading its ~33k tokens; read
the anchor's JSON, not its memo, unless the node test is genuinely undecided; one grep for
neighbours. Depth is not negotiable — the economy applies to how you **read**, never to how well you
research.

Verify before every commit: both files exist, the JSON parses, the memo carries `Depth: J-DEPTH`.
Commit **by explicit file path, never a wildcard**, and never commit a file inside another team's
claim. Append what happened to `planning/27-dispatch-run-log.md` — including kills, salvage, and
process slips; that log is what survives a session ending.
