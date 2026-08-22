# Research dispatch — resumable state

Date: 2026-08-22
Status: **paused on credits, mid-R1b.** Everything below is on disk and verified except the 22 R1b rows listed in §2. Resume from §3 at any time.
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md) · contract: [`domains/CONNECTION.md`](domains/CONNECTION.md) · roster: [`domains/roster.json`](domains/roster.json)
Ratifications: [`overnight/council/DECISION-BRIEF.md`](overnight/council/DECISION-BRIEF.md) — D1–D6 (2026-08-21) **plus J-IND (2026-08-22)**: professional worlds get placeholder schemas (~20 total) + gist-level per-industry research covering all of the old 574; depth much later.

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

## 2. Interrupted: the R1b swarm tail (22 rows)

One Opus agent per roster row; 60/83 agents completed before the session credit limit. Rows still owed:

**Missing entirely (19):** `finance.small-business-bookkeeping`, `finance.cap-table-equity`, `finance.student-financial-aid`, `travel.bookings-confirmations`, `finance.subscriptions-utilities`, `finance.vehicle-records`, `finance.household-property`, `finance.hoa-residents-association`, `finance.payroll-received`, `identity.core-documents`, `identity.immigration-visa`, `identity.credentials-passwords`, `medical.personal-health-records`, `medical.dependant-child-health`, `medical.wearable-health-exports`, `legal.personal-legal-matters`, `legal.estate-planning`, `legal.leases-agreements`, `legal.practice-matter-file`

**Partial — one of two files exists; treat as UNTRUSTED DRAFT, verify-complete-own (3):** `finance.insurance-corporate`, `finance.insurance-healthcare`, `finance.crypto-assets`

## 3. How to resume (any session)

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
