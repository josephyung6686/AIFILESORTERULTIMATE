# 115 — Handoff: one product, both halves at 10/10

**Date:** 2026-10-04 · **Branch:** `build/p6-p7-first-packages` (~170 commits ahead of origin, **not pushed** — owner pushes) · **Supersedes** `docs/operations/everyday-readiness-handoff.md` for the everyday assistant.

## The goal (owner, verbatim intent)

1. **The everyday assistant must be 10/10** — intuitive and working, judged by a fresh agent playing a real first-time user.
2. **The sorter must be 10/10** — "organise my whole desktop" must produce a structure a student would accept, ask only answerable questions, lock in, apply, and undo.
3. **The assistant and the sorter must be properly integrated in the codebase** — one product, one database, one move path, one privacy decision, one vocabulary. Not two tools glued together.

"Done" = a user-judge round scores **both** halves 10/10 and the full suite, release gate and pilot pass with no new failures.

## Where it stands (4 Oct 2026)

| | Intuitive | Works | Source |
|---|---|---|---|
| Everyday chat (find, ask, small tidy, undo, memory) | 7 | 7 | user-judge round 3 |
| Organise (sorter via chat) | 3 | 2 | user-judge round 3, before fixes M1 + N1 |

Verified on the branch tip: release gate 11/11 (`docs/operations/release-gate-report.json`), daily-use pilot passes both modes on the 800-file Desktop sample, no new test failures vs the pre-3-Oct baseline (29 pre-existing in `tests/integration` + `tests/test_cli*.py`; list in the session scratchpad `int_base.txt`).

## What exists now

- **Design:** `docs/superpowers/specs/2026-10-03-conversational-assistant-design.md` (v2 + §9a user-review changes) and the plan `docs/superpowers/plans/2026-10-03-conversational-assistant.md`. Designer-facing page: https://claude.ai/artifact/3mQcenyJWrSJy5iF8c2hwd (event contract §9).
- **Engine:** `src/assistant/session.py` (Session: history, permission levels 1–3, confirmations built by code, live + queued sorter questions, memory), `events.py`, `engine_tools.py`, `terminal.py`, `conversation_store.py`; `database-agent` opens the chat, `--events` serves the desktop app.
- **Index:** `src/items/indexing.py` — fast index with counts that reconcile to files on disk, local sensitivity while indexing, background document reading that resumes, projects as one item; refresh only re-reads what changed.
- **Integration done:** one database `~/.graph-agent/database-agent.sqlite`; one move seam (sorter and assistant moves update both `files` and `items`; one undo); one exclusion record (`exclusion_verdicts`); one live sensitivity check (`items.file_identity.item_is_sensitive`); one router (`database_agent/entrypoint.py`); the assistant reads the sorter's tree, placements and questions from SQL (`show_tree`, `proposal_files`, `structural_questions`).
- **Sorter speed:** organise of 800 files 1555 s → 169 s offline (output-identical); cloud judge calls 28-wide.
- **Cut:** Gmail/Calendar, deadline/nudge views. UI is built by someone else against the event contract.

## Integration gaps still open (goal 3)

- The assistant's model calls (`assistant/provider.py`, `local_model.py`) sit **outside** the ratified single-egress door (`tests/integration/test_single_egress.py` fails for both, pre-existing) — bringing them under `src/privacy` is an owner decision.
- Two move journals still exist (`assistant_journal`, sorter `move_journal`); they agree via the shared seam but are not one table.
- Lock-in reruns the whole sorter pipeline (3–5 min); needs a freeze-from-stored-proposal entry point.
- Sorter question text is rendered by the chat (plain sentences); the sorter's own screen vocabulary still differs from the chat's.

## Sorter gaps (goal 2)

- **Placement of loose files:** offline, 32/34 loose Desktop files have no fact any destination expects → only the model can place them (constitution: model decides). Live re-measurement on a 33-file sample is running (agent N1, see below).
- Questions: plainer now, but some still offer category menus that don't fit a student ("retail hospitality material"); library coverage for students is thin (owner-ratified text).
- Owner-reviewed behaviour changes made overnight: empty proposed folders are dropped at freeze instead of refusing the plan; stale shape answers are re-asked; project markers added (`.git`, `Package.swift`, `*.xcodeproj`, gradle, pom, sln/csproj, `pyvenv.cfg`, `package-lock.json`, venv `Lib/`+`Scripts/`); chat organise runs `--accept-groups` (no freeze) so proposals show placements.

## Everyday gaps (goal 1) — from round 3, most fixed in L1, unverified live

Offline "find" after a model failure, ID leaks, pending-prompt consistency, "what goes where", Chinese-named folders, junk suggestions — fixed by L1 (`tests/assistant/test_chat_final_fixes.py`) but **not yet re-judged live**. Open: protected-count false positives (a notes file, a web script — detector rules, owner), egress size (~30 KB per find turn; schemas dominate).

## Live result on the 33-file sample (agent N1, 4 Oct, with the AI)

**0 of 32 loose files got a destination, even with the AI.** Cause (not wiring): the model's per-file answers are correct (e.g. screenshots → `photos.screenshot-captures`, resume → `career.recruiting`), but they are stored as `llm_supported` facts and grouping only seeds groups from `direct`/`validated` facts (`src/grouping/seeds.py`, deliberate); proposed folders come only from accepted groups → no groups, no folders. Also: the default folder's kind is set by one file's rule facts outvoting 16 photo readings, producing a whole-Desktop "Which of these is career?" question; answered questions don't trigger a re-organise; the sorter's offered homes for leftovers ("Temporary Screenshots", "Review Later") have no chat route. **This is the #1 sorter decision:** let model-judged kinds seed groups/folders (or give recognised branches template folders without a group), and decide what sets the default kind. Fixed: a failed lock-in is not re-offered until the plan changes (3f47f144).

## Owner decisions waiting

All listed with evidence in memory `graph-agent-3-oct-scope`: single-egress for the assistant; retry rule for deterministic extraction timeouts; duplicate-file nondeterminism; `.git` as a project marker; review of the overnight sorter changes; whether protecting a file should also block moving it; detector false positives.

## Next steps (in order)

1. Read agent **N1**'s report (live organise on the 33-file sample `scratchpad/small-sample`, ≤3 runs) — merge its fixes.
2. **Credit rule:** live runs use **small samples only** (≈30–50 files). No more 800-file live runs.
3. User-judge round 4 on the small sample, scoring **both** halves separately; fix; repeat until both are 10/10.
4. Close the integration gaps above (after owner decisions).
5. Owner pushes the branch.

## How to run

```bash
cd "/Users/jy/GRAPH AGENT"
PYTHONPATH=src python3 -m database_agent.entrypoint            # the chat
env HOME=/tmp/x PYTHONPATH=src python3 -m database_agent.entrypoint   # isolated test home
RELEASE_DEP_WHEELHOUSE=/private/tmp/graph-agent-release-deps bash tools/run_release_gates.sh
```
Tests: one pytest at a time (`/tmp/graph-agent-pytest.lock` convention); tests never touch the real `~/.graph-agent` (autouse guard in `tests/conftest.py`).

## Session of 4 Oct (afternoon) — progress

- **Everyday chat:** user-judge round 4 (live, 33-file sample) = Intuitive 7, Works 8. Five defects fixed and merged (K4, merge 247000ad): dropped yes/no names what was dropped; protected files shown only when they match as well as an ordinary hit; the list under a reply is only what the reply names; background reading never splices into a reply and newly protected files are named; "undo that" asks once. tests/assistant + tests/items 605 passed. Not re-judged yet. **Owner:** a school attendance record is *ordinary* by the design (`00`:333, `privacy/vocabulary.py:664`), so its content may be sent; protecting school records would be a new protected kind.
- **Sorter:** model-named situations now open top-level life branches (O1, merges 9c67693e + f3125f01): `cli.draft_for_review` drafts a branch's judge-named files where P9 formed no group (`104`:2081 gap); default kind voted judge > facts > readings; a one-kind branch of two situations asks its open files. Live 33-file run: 8 placed, 15 waiting on a question, 9 no destination (≈6 protected). Borrowed P9 words (`strongly-identified-file`, `compatible-document-type`) kept — an honest new word is a contract revision (owner).
- **User-judge round 5 (organise via chat):** Intuitive 3, Works 2 — chat claimed 7 moves, 1 happened; one prompt per folder; undo one step only; plan places ~8/33; answers don't change the tree; jargon/duplicate questions. Fix agents running: **K5** (chat side, src/assistant) and **O2** (sorter side). Then re-judge both halves.
- Disk: 167 merged/clean worktrees removed (branches kept); 17 with uncommitted work kept.
