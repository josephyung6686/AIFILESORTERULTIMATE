# Conversational Assistant — Design

**Date:** 2026-10-03 · **Owner decisions:** talk-first (one conversation), cloud brain by default, sensitive files never sent, Gmail/Calendar cut, UI owned elsewhere.

## Goal

A person types `database-agent`, talks to it, and everything — find, ask, sort a few files, organise a whole folder, undo — works, makes sense, and asks them only when a real decision is needed. Done when a judge agent playing a first-time user on real files finds nothing confusing or broken, and the full suite, release gate and pilot pass.

## Approach

One conversation on top of the existing engine. The assistant's tool loop (`assistant/chat.py:ask`) becomes multi-turn; the sorter's pipeline is reached through tools that call `cli.main(argv, out=stream)` — the injection point the sorter already has — so nothing in the sorter is duplicated. Existing subcommands stay as thin wrappers for scripts and the UI.

## 1. Entry points

| Typed | Behaviour |
|---|---|
| `database-agent` (terminal) | Opens the conversation. |
| `database-agent "where is my CV"` | One question, one answer, exits. |
| `database-agent <FOLDER> [flags]` | The sorter, unchanged, for scripts. |
| `database-agent search\|ask\|plan\|db\|…` | Existing subcommands, unchanged. |

One database for everything: `~/.graph-agent/database-agent.sqlite` (an explicit `--database` wins).

First run with nothing indexed: the assistant asks which folder to look after, indexes it, and reports counts (indexed / set aside / protected) before anything else.

## 2. The conversation

- `assistant/session.py` (new, one purpose): the read–reply loop. Holds the message history for the session; each turn calls the tool loop with that history. Oldest tool payloads are dropped first when the history exceeds the model budget; the person's words and the assistant's replies are kept.
- `chat.ask` is split so the loop takes a message list (`converse(conn, messages, …)`); `ask(question)` stays as the one-shot wrapper.
- Long-running tools print progress lines to the terminal as they run (the sorter's own screen, streamed) and return a short summary to the model.
- Output style: plain sentences, paths shown relative to `~`, filenames as citations, no IDs or hashes, no latency or egress footers. The counts line (set aside / protected) appears on first contact and whenever it changes, not on every reply.

## 3. Tools (each wraps an existing seam)

| Tool | Seam | Changes files? |
|---|---|---|
| `status` | DB counts: indexed, set aside, protected, held, tree state, open questions, last moves | no |
| `index_folder(path)` | fast index: scan + exclusions + local sensitivity rules, records the selection | no |
| `find`, `read_item`, `list_related` … | existing assistant tools | no |
| `show_skipped`, `show_protected` | `exclusion_verdicts`; protected names only when asked (the sorter's `--show-protected` rule) | no |
| `organise_folder(path)` | `cli.main([path, --stop-after tree …])` | no |
| `show_tree` | sorter's tree from the DB (Lane E) | no |
| `answer_question(answer)` | `cli.main([path, --answer …])` | no |
| `quick_sort(files, destination?)` | plan → preview; files into the sorter's tree folder when one exists, else type groups | proposes |
| `apply_branch(branch)`, `apply_plan(plan)` | sorter apply / assistant apply (one move seam, Lane A) | **yes — confirm** |
| `undo_last` | the most recent move from either journal | **yes — confirm** |
| `mark_sensitive(file)`, `release(file)` | sorter `--file-held` / `--release` | **yes — confirm** |

## 4. Confirmation (code delivers, the model never approves)

A tool that moves files or changes a hold returns `needs_confirmation` with a one-line plain summary ("Move 5 files → ~/Desktop/Screenshots/. Nothing sensitive."). The session — code, not the model — prints it and asks `Go ahead? [y/N]`. Only a typed `y` executes, and the result goes back to the model. Big changes (whole-folder organise, apply a branch) happen only when the person asks for them.

## 5. Without an API key

The session says once: "No AI model is set up, so I can find files, show what I've got, and undo — not chat. To chat, set DEEPSEEK_API_KEY." A small deterministic router then handles: find/where is X → `find`; status; show skipped; undo; help.

## 6. Safety

Unchanged rules, enforced in one place: sensitivity is read live from the database plus both protection lists (Lane B); sensitive files never enter a cloud request; every provider request is a ledger row; nothing moves without a typed yes; every move is undoable.

## 7. Errors

No tracebacks reach the person. Missing index → "Nothing indexed yet — which folder should I look after?" Model/network failure → one line saying what failed and that nothing changed.

## 8. Testing

- Conversation tests with a scripted fake provider (tool calls in, transcript out): first run, find, quick sort with confirm and with refusal, organise → question → answer → show tree, apply branch with confirm, undo, no-key fallback, sensitive file never in a request envelope.
- The pilot drives the conversation on a copied real corpus.
- A judge agent plays a first-time user on the real Desktop sample; every confusion it reports is fixed and re-judged until it reports none.

## Dependencies

Lanes A–E (one move seam, one exclusion record, live sensitivity, one default DB, empty state, one router, tree from the DB) merge first. Round 2 (fast index with local sensitivity rules, counts everywhere, search ranking) lands with or before the conversation.
