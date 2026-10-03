# Conversational Assistant — Design (v2)

**Date:** 2026-10-03 · **Owner decisions:** talk-first; cloud brain (DeepSeek) by default; sensitive files never sent; Gmail/Calendar cut; UI built by someone else against the contract in §9.

## Goal

A person types `database-agent`, talks to it, and everything — find, ask, sort a few files, organise a whole folder, answer its questions, undo — works, makes sense, and asks them only when a real decision is needed. Done when a judge agent playing a first-time user on real files finds nothing confusing or broken, and the full suite, release gate and pilot pass.

## Shape

```
 terminal chat ─┐                         ┌─ assistant tools (find, read, quick sort, plans, undo …)
                ├─ Session (engine) ──────┤
 desktop app ───┘   events out,           └─ sorter (index, organise, questions, tree, apply)
                    actions in                       │
                                   one database ─────┘  ~/.graph-agent/database-agent.sqlite
```

- **`assistant/session.py` — `Session`** is the engine. It owns the conversation history, the permission level, pending confirmations and the event stream. It has no printing in it.
- **Renderers** draw `Session` events: `assistant/terminal.py` (numbered choices, progress lines) and, for the desktop app, `database-agent --events` (JSON lines on stdout, actions on stdin, §9).
- **Tools** are the only way the model acts; each wraps an existing seam (§4). The model decides; code delivers (constitution): confirmations, permission checks, sensitivity checks and question rendering are code, never model text.

## 1. Entry points

| Typed | Behaviour |
|---|---|
| `database-agent` | Opens the chat. |
| `database-agent ~/Desktop` (no other flags, in a terminal) | Opens the chat looking after that folder. |
| `database-agent "where is my CV"` | One answer, exits. |
| `database-agent <FOLDER> --flags…` | The sorter, unchanged, for scripts and existing runs. |
| `database-agent search\|ask\|plan\|db\|memory\|view\|watch …` | Existing subcommands for scripts. |
| `database-agent --events` | Engine over JSON lines, for the desktop app. |

Routing lives in `database_agent/entrypoint.py` only; `cli.main` is untouched.

## 2. A session

1. **Open.** Load the last 5 conversations (§7), the permission level, the counts. If nothing is indexed: "Which folder should I look after?"
2. **Index fast** (`index_folder`): scan + exclusions + local sensitivity rules + item projection, streamed as `progress`, finishing with a `counts` event. Seconds, not minutes; no cloud call.
3. **Greet** with counts and suggestions (§6), then wait.
4. **Each turn:** the person's words → the tool loop (`chat.converse(conn, messages, …)`, the multi-turn form of today's `ask`) → `message` with citations. Tool payloads stay in the session; oldest payloads drop first when history exceeds the model budget.
5. **Open questions** queued while the person was away are offered as a series on return (§5).

## 3. Owner rulings that shape behaviour

- **Software projects** are findable, never sorted: each is ONE item (name, README, top-level file names); code inside is never read; nothing inside is moved.
- **Sensitive files**: "where is my passport?" → the renderer shows name and folder from the database; the model is told only "1 protected file matched — shown to the person locally". Content is never opened or sent.
- **Suggestions** (gaps: set-aside areas, missing files, unsorted files, open questions, plus `items.suggest` / `items.nudge` warnings with the calendar-deadline parts removed) appear in the greeting, on "anything I should look at?", and as the app's `suggestions` event. `items/deadline_view.py` is deleted; `suggest`/`nudge` stay as the engine's source.
- **Cloud brain**: DeepSeek by default; any configured key works; without one, §8.

## 4. Tools

| Tool | Seam | Effect |
|---|---|---|
| `status` | DB counts + level + open questions + last move | read |
| `index_folder(path)` | `scan_agent` selection + scan + `items.project.project_context_graph` + local sensitivity rules | writes index only |
| `find`, `read_item`, `list_related`, `list_gaps` | existing assistant tools (Lane B's sensitivity gate) | read |
| `show_skipped`, `show_protected` | `exclusion_verdicts`; protected names rendered locally | read |
| `organise_folder(path)` | `cli.main([path, "--stop-after", "tree", …], out=progress)` | writes tree proposal, no moves |
| `show_tree` | sorter's tree/placements via SQL (Lane E) | read |
| `next_questions` | `questions.store.open_questions` | read |
| `answer_question(id, option_id\|text\|skip)` | `questions.store.record_answer` (what `--answer` writes), then resume organise | writes answer |
| `quick_sort(files, destination?)` | plan + preview; destination from the sorter's tree when one exists (Lane E), else type groups | proposes |
| `apply_plan(plan)`, `apply_branch(branch)` | assistant apply / sorter apply, one move seam (Lane A) | **moves — §5 gate** |
| `undo_last` | most recent move in either journal | **moves — §5 gate** |
| `mark_sensitive(file)`, `release(file)` | sorter `--file-held` / `--release` store | **changes protection — always confirms** |
| `remember_rule(text)`, `forget_rule(id)`, `list_rules` | `memory_v1` | rules — confirms |
| `set_level(n)` | session setting in DB | settings |

## 5. Decisions the person makes

**Permission levels** (stored in the DB; changed by saying so):

| Level | Moves the person asked for | Always confirms |
|---|---|---|
| 1 Ask every time (default) | confirm | — |
| 2 Small sorts automatic | ≤20 ordinary files at once, with undo | sensitive files, branch/whole-folder applies, protection changes |
| 3 Hands-off | at once, with undo | sensitive files, branch/whole-folder applies, protection changes |

**Confirmations** are `confirm` events built by code from the plan rows (moves listed, sensitive flag, undo available). Only an explicit yes from the person executes; the model can never confirm.

**Questions** come from `structural_questions`, never from parsing the sorter's screen. One question object = `prompt` (text), `evidence_context` (why), `unlocks` / `will_not_do` (what it changes), `options` (buttons), plus free text and skip — exactly what `structural_answers` can record (`choice`, `free_text`, `skipped`, `revoked`). Rendered by code, not paraphrased by the model. Live: asked one at a time as organising reaches them. Queued: unanswered rows wait; on return, "While you were away I have 6 questions — want to go through them?". Wording rule: plain sentences a student or job-seeker understands; no schema ids, situation codes or branch ids; the judge loop rewrites any prompt text that fails this (ratified prompt rows are versioned, never edited in place).

## 6. Counts, never silent

`counts` (indexed, set aside, protected, held, open questions) is emitted on open, after indexing, and whenever it changes. "Show skipped" / "show protected" list them. The same totals appear in `db check`, `watch`, `view` and the sorter's header.

## 7. Memory

- Decisions (answers, holds, rejected links, frozen plans): in the DB as today.
- Rules: `remember_rule` → `memory_rules`, injected into every prompt (`memory_v1.retrieve_for_proposal`).
- Corrections: every reject/edit/correction in chat → `diff_events` (wire `capture_reject`, `capture_edit`, `capture_accept_correction`). Atoms stay dark until their release gate passes.
- Recent conversations: the person's words and the assistant's replies (never tool payloads, never protected-file names) of the last 5 sessions in a local `conversation_turns` table; a new session starts with the last ~20 exchanges. "Forget our conversations" deletes them.

## 8. Without a model

If no key is configured or the provider fails: one line ("No AI model is set up, so I can find files, show what I've got and undo — set DEEPSEEK_API_KEY to chat"), then a deterministic router handles find / where is / status / show skipped / show protected / questions / undo / help.

## 9. Contract for the desktop app

`database-agent --events`: one JSON object per line.

| Event | Fields |
|---|---|
| `message` | `text`, `citations[]` (`name`, `folder`, `open_target`) |
| `progress` | `stage`, `done`, `total`, `line` |
| `question` | `question_id`, `text`, `why`, `changes`, `options[]` (`id`, `label`), `allow_text`, `allow_skip`, `files_preview[]`, `count`, `index`, `of` |
| `confirm` | `confirm_id`, `summary`, `moves[]` (`from`, `to`), `sensitive`, `undo_available` |
| `counts` | `indexed`, `set_aside`, `protected`, `held`, `open_questions` |
| `suggestions` | `items[]` (`kind`, `text`, `action`) |
| `done` | `moved`, `undo_token` |
| `error` | `text`, `changed` |

Actions in: `say(text)`, `answer(question_id, option_id | text | skip)`, `confirm(confirm_id, yes|no)`, `set_level(1|2|3)`, `undo(undo_token)`.

## 10. Errors

No traceback reaches the person. Missing index → the folder question. Model or network failure → one line saying what failed and that nothing changed, then §8.

## 11. Testing

- `Session` tests with a scripted fake provider: open on empty DB, index, counts, find, sensitive file shown locally and absent from every request envelope, quick sort at each level, confirm yes/no, organise → open questions → answer → tree, apply branch, undo, rules, conversation memory and forget, no-model router, `--events` round trip.
- Pilot drives a `Session` on a copied real corpus.
- Judge loop: a first-time-user agent on the real Desktop sample, live DeepSeek; each round's issues fixed, at most 3 rounds, then reported plainly.

## Dependencies

Lanes A–E (one move seam, one exclusion record, live sensitivity, one default DB and empty state, one router, tree from the DB) merge before the Session is built on them.
