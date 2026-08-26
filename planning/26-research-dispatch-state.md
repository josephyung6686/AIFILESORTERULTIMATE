# Research dispatch — resumable state

Date: 2026-08-24 (supersedes the 2026-08-22 revision)
Status: **R1b complete. J-IND roster expansion complete. Industry gist swarm in progress — 147 of 358 rows landed, 211 owed.**
Live progress log, newest entry at the bottom: [`27-dispatch-run-log.md`](27-dispatch-run-log.md) — **read it first.** It records every wave, kill, salvage, and process slip.
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md) · contract: [`domains/CONNECTION.md`](domains/CONNECTION.md) · roster: [`domains/roster.json`](domains/roster.json)
Standing brief every swarm agent reads: [`domains/dispatch/RESEARCH-BRIEF.md`](domains/dispatch/RESEARCH-BRIEF.md)
(the old `GIST-BRIEF.md` pointer was stale — that file does not exist; the brief was renamed when
J-DEPTH overruled the gist clause. `DEEPEN-ADDENDUM.md` sits beside it, for deepening passes only.)
Ratifications: [`overnight/council/DECISION-BRIEF.md`](overnight/council/DECISION-BRIEF.md) — D1–D6 (2026-08-21) plus J-IND (2026-08-22).

---

## 0. Resume in one command

The owed rows are always *whatever the roster lists that has no node file*. Never work from a
hand-written list — that error already cost five rows of a family once:

```bash
python3 -c "
import json,os,collections
r=json.load(open('planning/domains/roster.json')); n=r['nodes'] if isinstance(r,dict) else r
N='planning/domains/nodes/'
todo=[x['domain_id'] for x in n
      if not os.path.exists(N+x['domain_id']+'.json')
      or not os.path.exists(N+x['domain_id']+'.research.md')]
print(len(todo),'owed'); print(collections.Counter(x.split('.')[0] for x in todo))"
```

**The memo clause is not optional (added 2026-08-26).** A killed agent writes its `.json` first and
its `.research.md` second, so a row can have JSON and no memo. The earlier query keyed on `.json`
alone, which made those rows look finished — they would be skipped forever, carrying unverified,
unargued JSON into R1c. Six such partials exist right now (listed in the run log). Selecting on
**both** files is what makes the resume honest.

Then dispatch 3–4 agents, each owning ~9–11 sibling rows of ONE schema, each pointed at
`domains/dispatch/GIST-BRIEF.md` plus row-specific warnings (name the rows you expect to fail the
node test — that is what makes agents argue instead of agree). Verify, then commit **by explicit
file list**.

## 0a. Where it stands (2026-08-24)

| Stage | State |
|---|---|
| R0, R1a, R2–R6 | complete (§1) |
| R1b — the 83 launch rows | **complete, 83/83** |
| J-IND roster expansion | **complete** — 358 rows, 23 schemas, all 574 legacy ids reconciled |
| Industry gist swarm | **147/358 landed, 211 owed** |
| R1c merge gate | not started |
| Final review panel + index | not started |

Families finished end to end: `clinical_practice` (11), `business_operations` (25),
`construction_property` (28).

**Owed, by family:** creative 42 · law_practice 37 · government 32 · engineering 25 ·
manufacturing 20 · retail_hospitality 15 · hr 12 · nonprofit 11 · resource_operations 9 ·
logistics 8.

`creative` was dispatched twice (4 agents, 42 rows) and both times the agents were killed by the
usage limit before writing anything — **nothing to salvage, redispatch it whole.** It is the
riskiest family: its central hazard is the professional-vs-hobby seam (a working photographer's
client jobs are a filing world; a personal sketch folder is residual-library material), and it
carries the open **NJ-R1a-1**, which agents must record a dependency on rather than resolve.

Rows already flagged as likely node-test failures, for whoever redispatches `creative`:
`creative-brief`, `deliverable-handoff`, `revision-round`, `post-production` (probably *stages* in
one lifecycle); `illustration`, `motion-graphics`, `short-form-writing` (probably a *medium* or a
*length*, i.e. a `work_type` value); `self-initiated-work` (defined by the *absence* of a client —
a row with only negative evidence can never activate); `raw-photo-catalogue`, `shoot-day-media`
(collide with the landed `photos.*` family — and must not contradict the argument already made in
`construction_property.progress-photos`).

## 0b. Refusals so far — R1c adjudicates, do not blindly re-fire

Three from the gist swarm, each routing coverage through `falls_through_to` rather than dropping it:
`business_operations.organisational-records` (its only signal is an organisation name, which is
never-alone evidence, so the row could never activate), `construction_property.compliance-certificate`
(a document type; dimensions and privacy identical to the schema default),
`construction_property.timesheet` (three documents sharing a table shape, each already housed).
Plus the three from R1b: `research.project-workspace`, `code.software-project`,
`code.scratch-prototypes`.

## 0c. Proposed fields awaiting R1c (extends §4)

`organization` — proposed **independently by both** `business_operations` and
`construction_property`; must be settled as ONE decision, not two. Also `fiscal_period`
(business_operations); `property`, `instruction`, `revision` (construction_property);
`subject_of_record` (clinical_practice).

## 0d. Operating rules learned the hard way

1. **Row lists come from the roster programmatically.** A truncated terminal listing once caused
   5 rows of `clinical_practice` to be silently skipped.
2. **Commit by explicit file list, never a wildcard.** A wildcard once swept an agent's files into
   a commit before they had been verified.
3. **Tell agents to write each row's two files as they finish it**, not hold them to the end.
   Wave 1 died having written 4 salvageable files; wave 2 died having written none.
4. **Log before re-dispatching, not after.** The log is what survives a kill.
5. **A partial file with no memo is an UNTRUSTED DRAFT** — verify line-by-line, repair, complete,
   own it. Do not discard unread (it cost real tokens); do not trust unverified.
6. Waves of 3–4 agents, one family per wave where possible, so a completed wave is a clean commit
   boundary. Each usage-limit window buys roughly one wave.

---

## 1. Done and verified (do not redo)

Every item passed a mechanical quote audit (verbatim vs `00`) plus an adversarial done-when audit; repairs were applied and re-checked where audits failed.

| Stage | Deliverable | Where |
|---|---|---|
| R0 | Connection contract + 8 worked-join fixtures + gate delta (closed edge keys, kind rules) | `domains/CONNECTION.md`, `domains/CONNECTION-EXAMPLES.md`, `domains/_CONTRACT.md` (rules 11–15), `domains/check.py` |
| R1a | 83-row roster (10 schemas + 73 templates), 37-key canonical field list, triage of the 574 (~160 folded / ~40 values / ~370 refused pending J-IND) | `domains/roster.json`, `domains/canonical_fields.json`, `domains/ROSTER.md` |
| R1b | **61 of 83 rows fully landed** (includes 3 honest `refuse_node`: `research.project-workspace`, `code.software-project`, `code.scratch-prototypes` — R1c adjudicates, do not blindly re-fire) | `domains/nodes/<id>.json` + `.research.md` |
| R2 | Sensitivity detector rules + identifier classes + redaction transforms | `deferred-catalogues/08-sensitivity-detector/` |
| R3 | Nine residual templates, eight slots each + user-defined shape + falls-through boundaries | `deferred-catalogues/09-residual-library/` |
| R4 | Gazetteers (schools, orgs/roles, venues, course-code formats) + validation procedure | `deferred-catalogues/10-gazetteers/` |
| R5 | Jurisdiction value pack **shape + seed** (which-jurisdiction correctly left to Joseph) | `deferred-catalogues/11-jurisdiction-values/` |
| R6 | Academic context terms, course-code formats, term patterns, narrow dates, capture composition | `deferred-catalogues/12-academic-capture-patterns/` |

Gate: `python3 planning/domains/check.py` → legacy 574 baseline **566 in-file / 0 cross-file** (pre-existing audited debt, superseded by the roster; not new findings). `nodes/` is **not yet scanned** by the gate — extending it there is R1c's job.

## 2. SUPERSEDED — the R1b swarm tail (historical)

> **This section is history. R1b is complete at 83/83.** All 22 rows below were landed and
> committed (the last three in `1347e27`). Kept only as a record of what the interrupted session
> owed. Do not act on it — §0 is the live resume point.

One Opus agent per roster row; 60/83 agents completed before the session credit limit. Rows still owed:

**Missing entirely (19):** `finance.small-business-bookkeeping`, `finance.cap-table-equity`, `finance.student-financial-aid`, `travel.bookings-confirmations`, `finance.subscriptions-utilities`, `finance.vehicle-records`, `finance.household-property`, `finance.hoa-residents-association`, `finance.payroll-received`, `identity.core-documents`, `identity.immigration-visa`, `identity.credentials-passwords`, `medical.personal-health-records`, `medical.dependant-child-health`, `medical.wearable-health-exports`, `legal.personal-legal-matters`, `legal.estate-planning`, `legal.leases-agreements`, `legal.practice-matter-file`

**Partial — one of two files exists; treat as UNTRUSTED DRAFT, verify-complete-own (3):** `finance.insurance-corporate`, `finance.insurance-healthcare`, `finance.crypto-assets`

## 3. SUPERSEDED — the original workflow-resume recipe (historical)

> The `Workflow`/`resumeFromRunId` route below belongs to the original Claude swarm run and is no
> longer the resume path. **Use §0.** Kept for provenance.

**Preferred — resume the recorded workflow run** (cached rows replay free, only the 22 re-run):

```
Workflow({
  scriptPath: "planning/domains/dispatch/r1b-swarm.workflow.js",   // repo copy; original under the session dir
  resumeFromRunId: "wf_1dd2b90c-aa6",
  args: { rows: <the 83 {id, kind} rows — regenerate from roster.json: [{id: n.domain_id, kind: n.kind} for n in nodes]> }
})
```

Original script path (if the session store survives): `~/.claude-max/projects/-Users-jy-GRAPH-AGENT/606cb32b-c623-4625-a9ec-426dde6eb395/workflows/scripts/r1b-swarm-wf_1dd2b90c-aa6.js`; journal with per-agent results in the sibling `subagents/workflows/wf_1dd2b90c-aa6/journal.jsonl`.

**Fallback — fresh dispatch of only the 22 rows** using the same script with `args.rows` set to §2's list (ids + kinds from `roster.json`). The per-row prompt is embedded in the script (`rowPrompt`): each agent runs `python3 planning/domains/dispatch/make_prompt.py <id>` for its stamped assignment; wrapper rules = CONNECTION binding, D6/D2 ratified, verbatim-quote discipline, write only its own two node files, `refuse_node` is success, Opus / effort high. For the 3 partials add the salvage rule: existing files are untrusted draft — verify, fix, complete, own.

**Then, in order:**

1. **Roster expansion pass (J-IND)** — one agent: grow schemas to ~20 (`kind: schema`, PR-6 placeholder shape — no field rows unless design) covering the professional worlds (creative, engineering, business-ops/HR, government/civic, trades/property/logistics, clinician-practice, law-practice, …); triage **all 574 legacy ids** into `launch: placeholder` template rows on those schemas (or documented value/duplicate drops) in `roster.json` + `ROSTER.md`; prove with `make_prompt.py --all` and an unchanged legacy gate baseline.
2. **Industry gist swarm** — one **Opus** agent per new row (a couple hundred), same R1b mechanics, gist/purpose depth per J-IND ("good gist of each; depth much later").
3. **R1c merge gate** — `prompts/01c-merge-and-gate.md`, one agent: extend `check.py` to scan `nodes/`, reciprocity ≥90%, cluster `proposed_fields` (backlog in §4), adjudicate the 3 refusals, `FOREST-REPORT.md`, re-fire list.
4. **Final review panel** — 2–3 agents: mechanical+quote audit across all nodes (sampled deep), design-fidelity audit vs `00`/CONNECTION worked examples.
5. **Index** — update this file to point at everything; gate green on the live node set.

## 4. Proposed-fields backlog (R1c clusters these; do not mint before then)

From the 60 landed agents: `account_holder` (finance), `student` (k12/homeschool/k12-admission), `host_school` (study-abroad), `target_program` (grad-professional), `manuscript_id`, `dataset_name`, `institution`-reuse-on-research (grants — reuse, not mint), `protocol_id`, `chapter`, `employer` + `role` (employment-records — argued destination-eligible from `00`'s Career order), `credential_expiry` (recorded-not-written, D1 respected), `capture_date`, `duration`, `export_source`.

## 5. Open NEEDS-JOSEPH (unchanged; one sentence each unlocks)

- NJ-1 counting rule (narrowed by J-IND), NJ-2 safety ordering, NJ-3 `purpose` scope, NJ-4 protected-record surfacing, NJ-5 browse `parent_id` shipping — `domains/CONNECTION.md` §10.
- NJ-R1a-1 creative schema, -2 travel schema, -3 `target_school` vs `target_university` fold, -4 `people`/`programming_language` destination-eligibility, -6 scholarship sponsors — `domains/ROSTER.md`. (NJ-R1a-5 professional worlds: **answered by J-IND**.)
- R2's twelve detector questions — `deferred-catalogues/08-sensitivity-detector/RESEARCH.md`; R5's which-jurisdiction — `11-jurisdiction-values/RESEARCH.md`.
