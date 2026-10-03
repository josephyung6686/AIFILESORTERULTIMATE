# Conversational Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `database-agent` opens one conversation that finds, answers, quick-sorts, organises a whole folder, asks well-phrased questions, and undoes — over one database, with the sorter and the assistant as one product.

**Architecture:** A `Session` engine (`src/assistant/session.py`) owns history, permission level, pending confirmations and an event stream; it calls the existing tool loop in multi-turn form (`chat.converse`). Two renderers draw its events: the terminal (`assistant/terminal.py`) and JSON lines for the desktop app (`database-agent --events`). New tools wrap existing seams: fast indexing (`items/indexing.py`), the sorter (`cli.main(..., out=)`), the question store (`questions.store`), memory (`memory_v1`, `memory_l0`).

**Tech Stack:** Python 3.12, SQLite (SQLCipher optional), pytest, DeepSeek via `assistant.provider`.

**Spec:** `docs/superpowers/specs/2026-10-03-conversational-assistant-design.md` (v2). Read it before any task.

## Global Constraints

- One database: `~/.graph-agent/database-agent.sqlite` (constant from Lane C); explicit `--database` wins; tests always use a tmp DB or monkeypatched `HOME`.
- The model decides, code delivers: confirmations, permission checks, sensitivity checks and question rendering are code, never model text.
- Sensitive/protected files never enter a cloud request envelope; their name/folder are rendered locally only.
- Coverage is sacred: every file is indexed, set aside (counted, listed) or protected (counted, listed). Never silently omitted.
- Nothing moves without a yes unless the permission level allows it; sensitive files, branch/whole-folder applies and protection changes always confirm. Every move is undoable.
- No traceback, internal id, hash, schema id, situation code or latency reaches the person.
- Never edit `src/privacy/**`. Never `git add -A`. Build simply: existing seams, one purpose per change, no shims.
- One pytest at a time machine-wide: `until mkdir /tmp/graph-agent-pytest.lock 2>/dev/null; do sleep 5; done; PYTHONPATH=src python3 -m pytest …; rmdir /tmp/graph-agent-pytest.lock`.
- Commit messages end with a blank line and `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.

## Review Focus

1. **Person answers "y" to a confirm, then the file changed on disk before apply** → apply refuses with a plain line, nothing moves (test in Task 5).
2. **The provider fails mid-conversation (network, 402 balance)** → one plain line, nothing changed, session continues in no-model mode (test in Task 8).
3. **A question's prompt text contains a schema id or situation code** → the renderer never shows it raw; the wording guard flags it (test in Task 6).
4. **Person types an answer that matches no option** → stored as `free_text`, the question stays open-but-answered, nothing is invented (test in Task 6).
5. **History grows past the model budget in a long session** → oldest tool payloads drop first, the person's words survive, no crash (test in Task 4).

## File map

| File | Responsibility | Task |
|---|---|---|
| `src/items/indexing.py` (new) | `index_folder(conn, root, on_progress)`: selection + scan + item projection + local sensitivity, returns counts | 1, 2, 3 |
| `src/assistant/events.py` (new) | Event dataclasses + `to_json` | 4 |
| `src/assistant/session.py` (new) | `Session`: history, level, confirms, questions, memory hooks | 4, 5, 6, 7, 8 |
| `src/assistant/chat.py` | `converse(conn, messages, …)`; `ask` becomes a wrapper | 4 |
| `src/assistant/engine_tools.py` (new) | status, index_folder, organise_folder, show_skipped, show_protected, next_questions, answer_question, quick_sort, apply_branch, undo_last, mark_sensitive, release, rules, set_level | 5, 6, 7 |
| `src/assistant/registry.py`, `src/assistant/tools.py` | register/dispatch the engine tools | 5, 6, 7 |
| `src/assistant/terminal.py` (new) | render events in a terminal; read input | 9 |
| `src/database_agent/entrypoint.py` | route bare / folder / one-shot / `--events` | 9 |
| `src/assistant/conversation_store.py` (new) | `conversation_turns` table, last-5-sessions load, forget | 8 |
| `src/items/hot_index.py` | ranking: demote junk, boost filename | 10 |
| `src/items/suggest.py`, `src/items/nudge.py`, `src/assistant/gaps.py` | suggestions source without deadlines | 11 |
| `tools/run_daily_use_pilot.py` | drive a `Session` | 12 |

---

### Task 1: Fast `index_folder` with progress and counts

**Files:**
- Create: `src/items/indexing.py`
- Test: `tests/items/test_indexing.py`

**Interfaces:**
- Consumes: `scan_agent.selection.record_selection`, `scan_agent.scan.scan`, `items.project.project_context_graph`, `scan_agent.selection.selection_sources` (the sequence in `src/orchestrator.py` ~725-739); `items.identity.excluded_areas(conn)` (Lane A: reads `exclusion_verdicts`, returns list of `{folder, rule, rule_subject, paths, protected}`).
- Produces: `index_folder(conn, root: Path, *, on_progress: Callable[[str, int, int], None] | None = None) -> IndexCounts` and `counts(conn) -> IndexCounts` where `IndexCounts` is a frozen dataclass `(indexed: int, set_aside: int, set_aside_folders: int, protected: int, held: int, open_questions: int)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/items/test_indexing.py
from pathlib import Path
from database_agent.db import open_database
from items.indexing import index_folder, counts

def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "home"
    (root / "notes").mkdir(parents=True)
    (root / "notes" / "essay.txt").write_text("my essay", encoding="utf-8")
    (root / "proj").mkdir()
    (root / "proj" / "package.json").write_text("{}", encoding="utf-8")
    (root / "proj" / "index.js").write_text("x", encoding="utf-8")
    app = root / "Tool.app" / "Contents"
    app.mkdir(parents=True)
    (app / "Info.plist").write_text("<plist/>", encoding="utf-8")
    (root / "id.pem").write_text("-----BEGIN", encoding="utf-8")
    return root

def test_index_folder_reports_every_file_class(tmp_path):
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    seen = []
    c = index_folder(conn, _corpus(tmp_path), on_progress=lambda s, d, t: seen.append(s))
    assert c.indexed >= 1
    assert c.set_aside_folders >= 1          # proj/
    assert c.protected >= 2                  # Tool.app + id.pem
    assert seen and seen[-1] == "done"
    assert counts(conn) == c

def test_search_finds_the_essay_right_after_indexing(tmp_path):
    from items.hot_index import find_files
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    assert any(h.display_label == "essay.txt" for h in find_files(conn, "essay", limit=5).hits)
```

- [ ] **Step 2: Run it — expect `ModuleNotFoundError: items.indexing`.**
- [ ] **Step 3: Implement** `index_folder` as: `record_selection(conn, [root])` → `scan(conn, selection_id, source=FilesystemCorpusSource(), mime_type_for=lambda _p: None, scan_state=P1_INCLUDED_SCAN_STATE, budget_exhausted=lambda: False)` → `project_context_graph(conn, selection_sources(conn, selection_id), P1_INCLUDED_SCAN_STATE)` → `rebuild_fts(conn)` → `conn.commit()`; call `on_progress("scan", n, total)` from the walk and `on_progress("done", total, total)` at the end. Check the exact signatures of `record_selection` and `scan` with `graphify explain "record_selection"` before writing; reuse, do not re-implement. `counts(conn)` reads: `items` live files; `excluded_areas(conn)` (non-protected → set aside, protected → protected) plus items whose sensitivity check (Lane B's `item_is_sensitive`) is true; `held` from `items.typing_state='held'`; `open_questions` from `len(questions.store.open_questions(conn))` (0 when the table is absent).
- [ ] **Step 4: Run tests — PASS. Time the 800-file Desktop sample copy (`scratchpad/desktop-sample`): must finish < 30 s; record the number in the commit message.**
- [ ] **Step 5: Commit** `feat: index a folder in one fast pass with counts`.

### Task 2: Local sensitivity rules during indexing

**Files:** Modify `src/items/indexing.py`; Test `tests/items/test_indexing_sensitivity.py`.

**Interfaces:** Consumes Lane B's report naming the local, no-cloud rules that decide sensitivity from file name/content (the sorter's rules gate). Produces: after `index_folder`, those files have a protected classification row (or `typing_state='held'`) that Lane B's `item_is_sensitive(conn, item_id)` returns True for.

- [ ] **Step 1: Failing test** — corpus with `HKID_card.pdf` (a minimal PDF whose text contains an HKID-format number), `vaccination_record.pdf`, `notes.txt`; after `index_folder`, `item_is_sensitive` is True for the first two, False for `notes.txt`; `counts(conn).protected` includes them; `find_files(conn, "vaccination")` returns the hit with `protected=True` and no `open_target` in the tool payload.
- [ ] **Step 2: Run — FAIL (protected count misses them).**
- [ ] **Step 3: Implement** by reusing the sorter's local pass, which Lane B located: content sensitivity is `recognition.detector.Detector` (rules over P5 extracted evidence + identifier readings), wired through `cli.classifier(detector)` (cli.py ~11720, wrapped by `_semantic_classifier`); the detector is built at cli.py ~17768 (needs the recognition rules manifest, `HANDLING_POLICY`, `is_protected_container`, identifier observations, and the `activated_schemas` / `declared_lives` callbacks); records are written by `learning_seam.assign` (orchestrator.py ~1150) after extraction. For each newly scanned file version: run P5 extraction (local; Apple Vision OCR allowed, no model site), then the classifier, then `assign`. Extract the minimum shared helper from cli.py rather than copying it. It must make no network call — assert with a socket-blocking monkeypatch. Do not write new rules. Lane B's `items.file_identity.item_is_sensitive` then picks the store rows up with no further change.
- [ ] **Step 4: PASS; also re-run Task 1 tests and the 800-file timing (< 45 s).**
- [ ] **Step 5: Commit** `feat: decide sensitivity locally while indexing`.

### Task 3: Software projects are findable as one item

**Files:** Modify `src/items/indexing.py`; Test `tests/items/test_project_items.py`.

**Interfaces:** Produces: for each `exclusion_verdicts` project root, one `items` row with `item_type='project'`, `display_label` = folder name, `open_target` = folder path, FTS text = folder name + README first 2 KB + top-level file names. Never a row per file inside.

- [ ] **Step 1: Failing test** — corpus `Hoyahacks/frontend/package.json`, `Hoyahacks/frontend/README.md` ("Hackathon dashboard"); after `index_folder`: `find_files(conn, "hoyahacks")` and `find_files(conn, "hackathon dashboard")` each return one hit whose label is `frontend` or `Hoyahacks/frontend` with `item_type == 'project'`; no item has `open_target` inside that folder.
- [ ] **Step 2: FAIL.** **Step 3:** implement the projection from `excluded_areas(conn)` rows with `rule == RULE_PROJECT_ROOT_DESCENDANT`; README read is local only and capped at 2 KB. **Step 4: PASS.** **Step 5: Commit** `feat: index software projects as one findable item`.

### Task 4: `Session` core, events and multi-turn `converse`

**Files:** Create `src/assistant/events.py`, `src/assistant/session.py`; Modify `src/assistant/chat.py`; Test `tests/assistant/test_session_core.py`.

**Interfaces:**
- Produces `events.py`: frozen dataclasses `Message(text, citations)`, `Citation(name, folder, open_target)`, `Progress(stage, done, total, line)`, `Question(question_id, text, why, changes, options, allow_text, allow_skip, files_preview, count, index, of)`, `Option(id, label)`, `Confirm(confirm_id, summary, moves, sensitive, undo_available)`, `Move(src, dst)`, `Counts(indexed, set_aside, protected, held, open_questions)`, `Suggestions(items)`, `Done(moved, undo_token)`, `Error(text, changed)`; `to_json(event) -> str` adds `"type"`.
- Produces `chat.converse(conn, messages: list[dict], *, runtime: ToolRuntime, provider_turn=None) -> tuple[list[dict], ChatAnswer]` — the loop body of today's `ask` taking a history; `ask()` builds `[system, user]` and calls it.
- Produces `Session(conn, *, provider_turn=None, emit: Callable[[object], None])` with `open() -> None`, `say(text: str) -> None`, `answer(question_id, value) -> None`, `confirm(confirm_id, yes: bool) -> None`, `set_level(n: int) -> None`, `undo(undo_token: str) -> None`. `provider_turn` is injectable for tests (defaults to `chat_turn`).

- [ ] **Step 1: Failing tests**

```python
# tests/assistant/test_session_core.py
from assistant.session import Session
from assistant.events import Message, Counts

def scripted(*replies):
    it = iter(replies)
    def turn(messages, tools, config=None, **_):
        return next(it)
    return turn

def test_open_on_empty_db_asks_for_a_folder(conn):
    out = []
    Session(conn, provider_turn=scripted(), emit=out.append).open()
    assert isinstance(out[-1], Message)
    assert "which folder" in out[-1].text.lower()

def test_two_turns_share_history(conn, tmp_path):
    seen = []
    def turn(messages, tools, config=None, **_):
        seen.append([m["content"] for m in messages if m["role"] == "user"])
        return {"role": "assistant", "content": "noted"}
    s = Session(conn, provider_turn=turn, emit=lambda e: None)
    s.say("my name is Ada")
    s.say("what is my name?")
    assert seen[-1] == ["my name is Ada", "what is my name?"]

def test_history_over_budget_drops_tool_payloads_first(conn):
    s = Session(conn, provider_turn=scripted(*[{"role": "assistant", "content": "ok"}] * 40), emit=lambda e: None)
    for i in range(40):
        s.history.append({"role": "tool", "tool_call_id": str(i), "content": "x" * 5000})
        s.say(f"question {i}")
    users = [m for m in s.history if m["role"] == "user"]
    assert len(users) == 40
    assert sum(len(m["content"]) for m in s.history if m["role"] == "tool") < 60000

def test_provider_failure_is_one_plain_line(conn):
    def boom(*a, **k): raise RuntimeError("402 Insufficient Balance")
    out = []
    Session(conn, provider_turn=boom, emit=out.append).say("hi")
    text = out[-1].text
    assert "Traceback" not in text and "nothing changed" in text.lower()
```

- [ ] **Step 2: FAIL (no module).** **Step 3:** implement; `Session.open()` emits `Counts` + greeting or the folder question; `say()` appends the user message, runs `converse`, emits `Message` with `Citation`s built from returned item ids (name, folder relative to `~`); history trimming keeps every `user`/`assistant` message and truncates oldest `tool` contents to `"[earlier result dropped]"` until total chars < 60 000; any exception from the provider → `Error(text="The AI model didn't respond (…short reason…). Nothing changed. I can still find files and undo.", changed=False)` and the session flips to no-model mode (Task 8).
- [ ] **Step 4: PASS + run `tests/assistant` (ask still works).** **Step 5: Commit** `feat: Session engine with multi-turn conversation and events`.

### Task 5: Confirmations, permission levels, quick sort, apply, undo

**Files:** Create `src/assistant/engine_tools.py`; Modify `src/assistant/registry.py`, `src/assistant/tools.py` (register/dispatch only), `src/assistant/session.py`; Test `tests/assistant/test_session_moves.py`.

**Interfaces:**
- Engine tools return `ToolResult` payloads; a moving tool returns `{"ok": True, "needs_confirmation": {"kind": "plan"|"branch"|"undo"|"protection", "ref": <plan_id|branch|journal ref>, "summary": str, "moves": [{"from","to"}], "sensitive": bool}}` and moves nothing.
- `Session` turns that into `Confirm` unless `level_allows(level, kind, n_moves, sensitive)` → execute immediately. `level_allows`: level 1 → never; level 2 → `kind=="plan" and n<=20 and not sensitive`; level 3 → `kind=="plan" and not sensitive`. Branch, undo-of-branch and protection always confirm.
- `Session.confirm(confirm_id, yes)` → on yes calls `engine_tools.execute_confirmed(conn, kind, ref)` → `assistant.apply.apply_plan` / sorter apply via `cli.main([root, "--apply", branch, "--confirm"], out=…)` / undo; emits `Done(moved, undo_token)`.
- Level stored in table `session_settings(key TEXT PRIMARY KEY, value TEXT)`, key `permission_level`, default `"1"`.
- `quick_sort(files: list[str], destination: str | None)` → resolves names via `find_files`, destination = the sorter tree folder for those items when a tree exists (Lane E's `show_tree` reader), else `<common parent>/<type label>`; builds a plan with `content_hash`, `file_id`, `root_scope` (Lane C's fix) and returns `needs_confirmation`.
- `undo_last()` → newest of `assistant_journal` (applied, not undone) and sorter `move_journal`; returns `needs_confirmation`.

- [ ] **Step 1: Failing tests** — (a) level 1: model calls `quick_sort(["a.png","b.png"], "Screenshots")` → `Confirm` emitted, files unmoved; `confirm(id, False)` → still unmoved, `Message` "Cancelled. Nothing moved."; (b) `confirm(id, True)` → moved, `Done(moved=True)`; `undo(token)` at level 1 → `Confirm`; yes → back; (c) level 2 with 3 ordinary files → moved without `Confirm`; with a `.pem` among them → `Confirm` with `sensitive=True`; (d) level 3 with `apply_branch` → still `Confirm`; (e) Review Focus 1: after `Confirm`, overwrite `a.png` bytes, `confirm(id, True)` → `Error(text containing "changed since", changed=False)`, nothing moved.
- [ ] **Step 2: FAIL.** **Step 3: Implement.** **Step 4: PASS + `tests/assistant/test_crash_recovery.py tests/assistant/test_no_clobber_and_hash.py`.** **Step 5: Commit** `feat: confirmations, permission levels, quick sort and undo in the Session`.

### Task 6: Questions from the store — live and queued

**Files:** Modify `src/assistant/engine_tools.py`, `src/assistant/session.py`; Test `tests/assistant/test_session_questions.py`.

**Interfaces:**
- Consumes `questions.store.open_questions(conn) -> tuple[StructuralQuestion, ...]`, `questions.store.record_answer(conn, StructuralAnswer)`; check field names with `graphify explain "StructuralQuestion"` (`prompt`, `evidence_context`, `unlocks`, `will_not_do`, `options`).
- Produces `question_event(q, index, of) -> events.Question` mapping `text=q.prompt`, `why=q.evidence_context`, `changes=q.unlocks`, options → `Option(id, label)`, `allow_text=True`, `allow_skip=True`; `wording_problems(text) -> list[str]` flags `[a-z]+\.[a-z_-]+` codes (e.g. `academic.coursework`), snake_case tokens, ids ≥ 8 hex chars.
- `Session.open()`: if `open_questions` non-empty → `Message("While you were away I have N questions — want to go through them?")`; on yes, emits them one `Question` at a time; `Session.answer(qid, value)` → `record_answer` (choice / free_text / skipped) → next question or resume organise (Task 7).

- [ ] **Step 1: Failing tests** — seed two `structural_questions` rows (use the existing test helpers that tests in `tests/` already use to create P15 questions; find them with `grep -rl record_question tests`); (a) open → queued message; (b) answer option → `structural_answers` row `state='confirmed'`, next `Question` with `index=2, of=2`; (c) Review Focus 4: typed text matching no option → row `answer_type='free_text'`, `option_id IS NULL`; (d) "skip" → `state='skipped'`; (e) Review Focus 3: a prompt containing `academic.coursework` → `wording_problems` non-empty and the rendered `Question.text` does not contain it (renderer substitutes the option's human label or drops the code).
- [ ] **Step 2–5:** FAIL → implement → PASS → commit `feat: ask the sorter's questions in the conversation, live and queued`.

### Task 7: Sorter tools — organise, tree, branch apply, protection

**Files:** Modify `src/assistant/engine_tools.py`; Test `tests/assistant/test_session_organise.py`.

**Interfaces:**
- `organise_folder(path)` → `cli.main([str(path), "--database", db_path, "--stop-after", "tree"], out=_ProgressStream(emit))` where `_ProgressStream.write(line)` emits `Progress(stage="organise", line=line.strip())` for non-empty lines; returns `{"ok": True, "open_questions": n, "tree": show_tree(conn)}`.
- `show_tree` — Lane E's reader (import it; do not reimplement).
- `apply_branch(branch)` → `needs_confirmation(kind="branch")`; executed by Task 5's `execute_confirmed`.
- `mark_sensitive(file)` / `release(file)` → `needs_confirmation(kind="protection")`; executed via `cli.main([root, "--file-held", file_id], …)` / `--release`.

- [ ] **Step 1: Failing test** on a small synthetic corpus run through the real sorter path with cloud off (copy the corpus fixture used by `tests/test_cli.py` tests that reach `--stop-after tree`; find one with `grep -n "stop-after" tests/test_cli*.py | head`): model calls `organise_folder` → ≥1 `Progress` event, payload has `tree` or `open_questions`; no file moved.
- [ ] **Step 2–5:** FAIL → implement → PASS → commit `feat: organise a whole folder from the conversation`.

### Task 8: Memory, rules and the no-model router

**Files:** Create `src/assistant/conversation_store.py`; Modify `src/assistant/session.py`, `src/assistant/engine_tools.py`, the reject/edit call sites that should call `capture_reject` / `capture_edit` / `capture_accept_correction` (find with `graphify query "reject_link"` and the plan edit path); Test `tests/assistant/test_session_memory.py`.

**Interfaces:**
- `conversation_store`: table `conversation_turns(session_id, seq, role CHECK(role IN ('user','assistant')), text, ts)`; `save_turn(conn, session_id, role, text)`, `recent(conn, sessions=5, exchanges=20) -> list[dict]`, `forget(conn) -> int`. `save_turn` refuses text containing the display label of any protected item (check via Lane B's sensitivity function over items whose label occurs in the text).
- Tools `remember_rule(text)` (→ `needs_confirmation(kind="rule")`, then `memory_v1.add_rule`), `list_rules`, `forget_rule(rule_id)`, `forget_conversations`.
- No-model router `route_without_model(conn, text) -> list[event]`: regexes for `^(find|where('s| is)|search)\b` → `find_files`; `status|what have you got` → counts; `show skipped|show protected|questions|undo|help`.

- [ ] **Step 1: Failing tests** — (a) two sessions: second session's first provider call includes the first session's user text; (b) `forget_conversations` → `recent()` empty; (c) a reply mentioning a protected file's label is not stored; (d) "always put screenshots in Screenshots" → model calls `remember_rule` → `Confirm`; yes → `list_rules` contains it and the next provider call's system prompt contains it; (e) Review Focus 2: provider raises → `Error` then `say("where is essay")` answered by the router with a `Message` citing `essay.txt`.
- [ ] **Step 2–5:** FAIL → implement → PASS → commit `feat: rules, conversation memory and a no-model mode`.

### Task 9: Terminal renderer and entry routing

**Files:** Create `src/assistant/terminal.py`; Modify `src/database_agent/entrypoint.py`; Test `tests/assistant/test_terminal.py`, `tests/items/test_cli_routing.py`.

**Interfaces:**
- `run_terminal(conn, *, folder: Path | None, stdin=sys.stdin, stdout=sys.stdout, provider_turn=None) -> int` renders: `Message` → text + citations as `name   ~/folder`; `Progress` → one updating line; `Question` → text, "why" in dim, options as `1) … 2) …`, `or type your own · s) skip`; `Confirm` → summary, move list (first 10 + "and N more"), `Go ahead? 1) Yes  2) No`; `Counts` → `· Set aside N … · Protected N …`; `Error` → text. Protected citations show name + folder from the DB directly.
- `run_events(conn, stdin, stdout)` → `to_json` per event; reads JSON actions `{"action":"say","text":…}`, `answer`, `confirm`, `set_level`, `undo`.
- `entrypoint.main`: no args → `run_terminal(conn, folder=None)`; one arg that is an existing directory and stdin is a TTY → `run_terminal(conn, folder=Path(arg))`; one arg not a directory and not a subcommand → one-shot `Session.say` then exit; `--events` → `run_events`; anything else unchanged (subcommands; sorter with flags).

- [ ] **Step 1: Failing tests** — feed scripted stdin to `run_terminal` with a scripted provider: transcript contains the folder question, counts line, a numbered confirm, "Moved"; no line contains "Traceback", "item_id", 8+ hex chars. `run_events` round trip: `say` in → `message` JSON out. Routing: `entrypoint.main([str(dir)])` with `isatty` patched True calls `run_terminal`; `entrypoint.main([str(dir), "--stop-after", "tree"])` still calls `cli.main`.
- [ ] **Step 2–5:** FAIL → implement → PASS → commit `feat: open the conversation from database-agent`.

### Task 10: Search ranking a person trusts

**Files:** Modify `src/items/hot_index.py`, `src/items/commands.py` (search output only); Test `tests/items/test_ranking.py`.

- [ ] **Step 1: Failing test** — corpus: `Applications/Resume.docx` ("work experience"), `site_files/resume.chunk.js`, `graphify-out/cache/resume.json`, `_archive/old/FOLDER_TREE.html` (body mentions resume 20×); `find_files(conn, "resume")` first hit is `Resume.docx`; junk paths (`*_files/`, `cache/`, `graphify-out/`, `node_modules/`, `__pycache__/`) rank below every non-junk hit; filename match outranks body-only match; `search` CLI output has no score column.
- [ ] **Step 2–5:** FAIL → implement (multiply FTS rank by a filename-match boost and a junk-path penalty in the existing scoring function; no new index) → PASS → commit `fix: rank filename matches first and junk folders last`.

### Task 11: Suggestions without deadlines; counts everywhere

**Files:** Delete `src/items/deadline_view.py`, `tests/items/test_deadline_view.py`; Modify `src/items/nudge.py`, `src/items/suggest.py`, `src/assistant/gaps.py` (drop `enriched_deadlines`), `src/assistant/tools.py` (drop `_list_deadlines`), `src/assistant/chat.py` (system prompt line), `src/items/commands.py` (`view_main` drops `deadlines`, default `folder`; `db check`, `watch`, `view` print the counts line from `items.indexing.counts`), `tests/items/test_cli_routing.py`; Test `tests/items/test_suggestions.py`.

**Interfaces:** Produces `suggestions(conn) -> list[dict(kind, text, action)]` in `items/suggest.py` from gaps + nudge warnings (no event/deadline kinds). `Session.open()` emits `Suggestions` (Task 4 calls it if present).

- [ ] **Step 1: Failing tests** — `suggestions(conn)` on a corpus with a set-aside project and a missing file returns both kinds with plain text; no item mentions deadline/calendar; `view deadlines` exits 2 with usage; `db check` output contains "Set aside" and "Protected" lines.
- [ ] **Step 2–5:** FAIL → implement → PASS (`tests/items tests/assistant`) → commit `refactor: suggestions without calendar deadlines; counts on every surface`.

### Task 12: Pilot and judge

**Files:** Modify `tools/run_daily_use_pilot.py`; Test `tests/test_release_gates.py`.

- [ ] **Step 1:** add pilot steps driving a `Session` with a scripted provider on the copied corpus: open → index counts → find → quick sort (level 1 confirm yes) → undo → organise (cloud off) → questions present or tree present → no traceback in any event; thresholds unchanged.
- [ ] **Step 2:** run pilot both modes on `scratchpad/desktop-sample`; full `tests/`; `RELEASE_DEP_WHEELHOUSE=/private/tmp/graph-agent-release-deps bash tools/run_release_gates.sh`.
- [ ] **Step 3:** judge loop (lead): a fresh Opus agent with no repo context plays a first-time student on a fresh copy of the Desktop sample through `database-agent` with live DeepSeek, reports every confusion ranked; fix; repeat ≤ 3 rounds.
- [ ] **Step 4: Commit** `test: pilot drives the conversation`.

### Task 13: Document text after the fast index (Index agent, after Task 3)

**Files:** Modify `src/items/indexing.py`; Test `tests/items/test_indexing_text.py`.

**Interfaces:** Produces `read_document_text(conn, *, on_progress=None, limit=None) -> int` that, for live items with no extracted body, runs local extraction (pdf → pdfium/pdfminer reader, docx → python-docx reader, images → Apple Vision OCR where available; the existing `readers/` callables) and writes the body into the chunk/FTS tables the search already reads (`_body_for_item` / `item_chunks`); also runs Task 2's sensitivity pass on each file before its text becomes searchable. `counts()` gains `unread_documents: int`. Search hits for unread files carry `matched_by="name"`.

- [ ] **Step 1: Failing tests** — after `index_folder` + `read_document_text`, `find_files(conn, "fundraiser approval")` finds a `.docx` whose NAME lacks those words and a `.pdf` likewise; before `read_document_text` the hit (by name) has `matched_by == "name"`; a PDF whose text is an ID-card number is protected before its text is searchable and never appears in a fake provider's request envelope.
- [ ] **Step 2–5:** FAIL → implement (reuse `readers/`; no new extractors) → PASS + 800-file timing reported → commit `feat: read document text in the background after indexing`.

### Task 14: First-run trust (Engine agent, with Tasks 4–9)

**Files:** `src/assistant/session.py`, `src/assistant/engine_tools.py`, `src/assistant/terminal.py`; Test `tests/assistant/test_first_run.py`.

Implements spec §9a items 3–11: `set_level` returns `needs_confirmation(kind="settings")`; greeting disclosure line (code-written, exact text in spec); `what_was_sent` tool over `egress_ledger` (plain words, no ids); key onboarding (paste → `~/.graph-agent/.env` 0600, never echoed, never in DB); numbered folder choices + the macOS-access warning; counts sentence in people's words with one protection word; `open N` / `show N` deterministic commands (`open` / `open -R` via `subprocess.run([...], check=False)`, refused for protected items unless the person typed it); organise time warning + `cancel` (sets a flag the progress stream checks; raises a private exception inside `cli.main`'s `out.write`, caught by the tool; nothing moved); `undo` with no target lists last 5 batches; suggestions lead with own clutter (screenshots count, same-hash copies, installers).

- [ ] **Step 1: Failing tests**, one per item above, using the scripted provider: (a) a tool result containing "switch to hands-off" that makes the model call `set_level(3)` → `Confirm`, level unchanged until yes; (b) greeting contains "never leave this Mac"; (c) `what_was_sent` after one turn names DeepSeek and a byte count, no ids; (d) no-key session: pasted key written to tmp HOME `.graph-agent/.env` mode 0600 and absent from every event and the DB; (e) folder question lists 1–3 choices; (f) counts sentence contains "coding projects" and "protected", not "held"; (g) `open 1` calls the patched `subprocess.run` with `["open", path]`; (h) `cancel` during a fake long organise → `Message` "Stopped. Nothing moved."; (i) `undo` lists ≤5 batches; (j) suggestions on a corpus with 6 screenshots and two same-hash copies mention both.
- [ ] **Step 2–5:** FAIL → implement → PASS → commit `feat: first-run trust — disclosure, onboarding, open, cancel, undo history`.

### Task 15: Freshness without re-scanning on every question (Index agent)

Lane A measured: each `search`/`ask` refresh re-scans every recorded folder (~1–2 s warm, 9–11 s first tick on 643 files) and appends 1 `scan_runs` + 643 `stat_cache_verdicts` + 643 `events` rows per pass; guessed item-parent folders become permanent selections (`selected_by=None`), against `scan_agent.selection`'s rule; the sorter's "nothing could be read" screen (cli.py ~22416) reads the newest `scan_runs` row, which can now be an assistant run.

**Files:** `src/items/refresh.py`, `src/items/indexing.py`, `src/items/identity.py`; Test `tests/items/test_refresh_cost.py`.

- [ ] **Step 1: Failing tests** — (a) two `search` calls with no file change add 0 `scan_runs`, 0 `events`, 0 `stat_cache_verdicts` rows on the second call and take < 300 ms on a 600-file tmp corpus; (b) after touching one file, the next search re-indexes it and adds rows only for that file; (c) with no recorded selection, `discover_roots` never writes a `corpus_selections` row (the Session's folder question records the person's choice instead); (d) the sorter's newest-run screen query filters to sorter-recorded runs (assert on a DB holding an assistant run newer than the sorter run).
- [ ] **Step 2–5:** FAIL → implement (cheap change check first: compare directory mtimes / FSEvents cursor already in `index_watch_cursors` and only reconcile changed subtrees; mark assistant runs so sorter queries can exclude them) → PASS + the Lane A timing table re-measured → commit `fix: refresh only what changed`.

Also in Task 14's counts sentence: one unit (folders) for "set aside", and the search header's two "Protected" counts merged into one line in the sorter's words.

## Execution

Lanes A–E merge first. Then three agents in parallel worktrees by file ownership:
- **Engine (Opus):** Tasks 4 → 5 → 6 → 7 → 8 → 9 → 14 (session.py, events.py, engine_tools.py, terminal.py, conversation_store.py, chat.py, registry/tools registration, entrypoint.py).
- **Index (Opus):** Tasks 1 → 2 → 3 → 13 → 15 (items/indexing.py and its tests). The engine imports `index_folder`/`counts` by the names above; until merged it may stub them in its tests.
- **Surfaces (Sonnet):** Tasks 10 → 11 (hot_index.py, suggest.py, nudge.py, gaps.py, deadline_view.py, commands.py view/db/watch output; tools.py `_list_deadlines` removal only — coordinate: Engine owns the rest of tools.py).
Lead merges, runs the full suite, then Task 12.
