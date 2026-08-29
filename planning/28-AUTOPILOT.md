# Autopilot — run the research dispatch unattended

**One instruction: read this file, do §2, repeat.** Everything needed is here or linked.
Companion state: [`26-research-dispatch-state.md`](26-research-dispatch-state.md) ·
append-only history: [`27-dispatch-run-log.md`](27-dispatch-run-log.md)

## 0. ⚠ STOP — TWO TEAMS ARE WRITING (added 2026-08-25)

**Before dispatching anything, read `planning/29-DOMAIN-OWNERSHIP.md` and claim your ids there.**
A second team (CODEX) writes rows into the same directory. An unattended tick that dispatches
against their id will collide — this has already happened twice and cost two stopped agents.

- Dispatch ONLY ids marked for this team (`OTHER-TEAM`), or unclaimed ids you claim first.
- **Never** write, edit, or delete a file for an id claimed by CODEX, including deleting a stray
  file left there by this team. Report it instead; deleting inside their claim is the edit the
  rules forbid.
- **Do not stash, rebase, pull, or reset while either team has uncommitted work.** If a push is
  rejected, hold the commit locally and say so. (This overrides §3 below.)
- Release each id to `complete` in the register when its row lands.

## 1. Standing orders (Joseph, 2026-08-25)

- Run **4 agents at a time**, one row each. (8 was validated and worked; 4 is the standing order.)
- Keep going until credits run out. When they do, retry every 2 hours and continue.
- **Never stop and wait for permission.** If a wave completes and credits remain, dispatch the next.
- Depth is **J-DEPTH** (ratified, overrules J-IND's gist clause) — same depth as the 83 launch rows.

## 2. The loop

1. **Compute what is owed** — never from a written list, always from the roster:

```bash
cd "/Users/jy/GRAPH AGENT" && python3 - <<'PY'
import json,os,glob
r=json.load(open('planning/domains/roster.json')); n=r['nodes'] if isinstance(r,dict) else r
fams=('clinical_practice','business_operations','construction_property')
debt=[]
for f in glob.glob('planning/domains/nodes/*.research.md'):
    b=os.path.basename(f)[:-12]
    if b.split('.')[0] in fams and 'J-DEPTH' not in ''.join(open(f).readlines()[:8]):
        debt.append((os.path.getsize(f),b))
debt.sort()
unwritten=[x['domain_id'] for x in n if not os.path.exists('planning/domains/nodes/'+x['domain_id']+'.json')]
print("DEBT (deepen first, shallowest first):",len(debt)); [print("  ",b,s) for s,b in debt[:8]]
print("UNWRITTEN (after debt is clear):",len(unwritten)); [print("  ",i) for i in unwritten[:8]]
PY
```

2. **Priority order.** Clear the DEBT rows first (Joseph's call). Then the UNWRITTEN rows —
   **schema rows before their templates**, because every template's node test is measured against
   its schema's default template.

3. **Dispatch 4 agents**, one row each, general-purpose, model opus. Each prompt contains only:
   - `Read first, in order: planning/domains/dispatch/RESEARCH-BRIEF.md`, then
     `planning/domains/dispatch/DEEPEN-ADDENDUM.md` (the addendum only when deepening).
   - The one row id, its current memo size, and its stamped-assignment command
     (`python3 planning/domains/dispatch/make_prompt.py <id>`).
   - **Required reading:** its schema anchor, its 2–4 nearest neighbours by name, and any landed
     row that already argued a boundary against it.
   - **A row-specific charge** — name the most plausible reason this row should NOT exist
     (a work_type value, a document type, a format, a never-alone signal, a duplicate of a
     neighbour). This is the highest-value part of the prompt. Rows that are merely asked to
     describe themselves produce description; rows that must survive a charge produce argument.
   - The standing constraints: write only its own two files, never edit a neighbour (recommend to
     R1c instead), `fields: []`, don't mint canonical keys, quotes verbatim, refusal is a success,
     write each file the moment it is ready, don't pad.

4. **Verify before committing** — parse the JSON, confirm every universal key is present, confirm
   the memo header says `Depth: J-DEPTH`, confirm the memo ends mid-nothing, confirm no file
   outside the row's two was touched.

5. **Commit by explicit file list** (never a wildcard — a wildcard once swept in unverified files),
   append to `27-dispatch-run-log.md`, and `git push`.

6. **Go to 1.**

## 3. If the push is rejected — SUPERSEDED BY §0

Historically: the P6/P7 workstream also commits to `build/p6-p7-first-packages` (they own `src/`,
this track owns `planning/domains/`), and rebasing onto them was safe.
**That no longer applies while two teams are writing rows.** Per §0, do not rebase, pull, stash or
reset while either team has uncommitted work — hold the commit locally and report it.

## 4. If agents are killed by the usage limit

Expected, not a failure. Agents are told to write each file as it is ready, so kills usually leave
complete rows on disk. **Check for survivors before re-dispatching**, verify them like any other
row, and log what was salvaged. A partial file with no memo is an UNTRUSTED DRAFT — verify
line-by-line, repair, complete, own it; never discard unread, never trust unverified.

## 5. Open tripwire

Five consecutive flagged-as-likely-failure rows have stood. The flagging still produces reversals
and withdrawn proposals, and it has refused six rows earlier. **But if flagged rows stop failing
entirely across two more waves, the challenge has become theatre** — redesign it rather than
repeating it. Check this rather than inheriting the assumption.

## 6. After the debt and the unwritten rows

R1c merge gate (`planning/prompts/01c-merge-and-gate.md`), then the final review panel, then the
index. See `26-research-dispatch-state.md` §0a. Do not start R1c early — it audits the whole forest
and wants every row present.
