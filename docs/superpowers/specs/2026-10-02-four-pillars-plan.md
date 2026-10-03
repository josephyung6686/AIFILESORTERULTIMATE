# Four Pillars — Complete Build Plan

**Date:** 2026-10-02  
**Authority:** Supplements [`2026-10-02-local-file-assistant-architecture-report.md`](./2026-10-02-local-file-assistant-architecture-report.md)  
**Agent + deep-dives:** [`2026-10-02-agent-design-and-deep-dives.md`](./2026-10-02-agent-design-and-deep-dives.md)  
**Rule:** Embeddings never alone approve a life link or a move. File text is untrusted. No OpenClaw.  

This document plans **all four pillars** end-to-end: contracts, schemas, tools, privacy, eval, phases, and what is already done.

---

## Cross-cutting invariants (every pillar)

| # | Invariant |
|---|---|
| I1 | Filesystem is system of record; DB is working memory |
| I2 | No silent `approved` / no silent move |
| I3 | Held / safety / `ALWAYS_LOCAL` never enter cloud prompts |
| I4 | Citations = `item_id` + `source_ids[]` (hard links) |
| I5 | Exact suppress always on; learned memory never shadows holds |
| I6 | Write args come from **plan objects** + find `item_id`s, not free-form file text |
| I7 | BYOK agent loop only — no OpenClaw / TencentDB npm |
| I8 | Index excerpts are a honeypot → encrypt at rest (Keychain); held opens need local auth |
| I9 | Every cloud turn appends an egress ledger row the user can view |
| I10 | Labels/subjects/basenames in tool cards are untrusted (never write-arg sources) |
| I11 | Approvals bind `plan_hash`; edit invalidates; full op list viewable before Approve |
| I12 | T0 rename = template-rendered names only — never model free text |

---

# Pillar A — Embeddings meaning-search = default product surface

## A.1 Goal

Search is the **default entry** (CLI/UI), not “run sorter.”  
Every live item is findable in &lt;SLO latency via **hybrid** lexical + vector retrieval.  
Detail loads on demand.

## A.2 What is indexed

| Item type | Indexed when | Text for FTS | Vector text |
|---|---|---|---|
| `file` | after identity project | label, path basename, **safe excerpt** (chunked) | same, per chunk |
| `email` | after fixture/live ingest | subject, from/to addresses, attachment names | subject + attachment names (**no body**) |
| `event` | after ingest | title, calendar id | title |
| `project` / `course` | after mint | display_label | display_label |
| `person` | after mint (P5) | display_label + address aliases | same |

**Never indexed for cloud egress:** held bodies, `ALWAYS_LOCAL`, raw attachment bytes, OAuth tokens.

## A.3 Storage (new / extend)

```
item_fts          FTS5 — dual tokenizer path (Latin unicode61+porter; CJK bigram/trigram)
item_fts_meta     item_id, field weights (label > path > excerpt)
item_chunks       chunk_id, item_id, ordinal, text, char_start, char_end
item_vec          chunk_id or item_id → versioned embedding (reuse vector_versions pattern)
item_heat         item_id, heat INTEGER  -- bump on read_item / cited use
```

Change feed: **FSEvents** preferred; fallback reconcile. Spotlight/`mdfind` optional candidate helper only.

## A.4 Query path

```
query
  → script-aware route (Latin / CJK / mixed)
  → parallel: FTS top-K + vector top-K (chunk level)
  → aggregate chunks → item
  → RRF (then convex combo once ≥40 labeled queries)
  → + small additives: recency, heat, path-prior
  → INDEX cards ≤20: {item_id, one_line, type, score, channel, heat, protected?}
  → full body/path only via read_item (bump heat)
```

Protected/held: counted **present-but-unopened**; `open_target` / excerpt omitted from cloud-bound payloads.

## A.5 Product surface

| Surface | Behavior |
|---|---|
| CLI default | `search "…"` / assistant find tool — **not** full sort |
| UI (later) | Search box first viewport |
| Degrade | No embedding weights → FTS-only; never block |

## A.6 Progress

| Piece | Status |
|---|---|
| Shallow `meaning_search` (substring + edge boost) | **Done** |
| MiniLM resolve-when-present | **Done** |
| True FTS5 + vec + RRF + chunking + CJK | **Done** (`hot_index`; ZH bake-off winner) |
| FSEvents feed | **Done** (`fsevents_live` + polling fallback) |
| SLO @ 50k/250k | **Partial** — 2k measured in CI; 50k offline; 250k not yet |

## A.7 Build tasks

1. Schema: `item_chunks`, dual FTS, heat, vec linkage  
2. Indexer: run after `project_context_graph` / mailbox ingest  
3. `find_files` tool + upgrade CLI `search`  
4. Embedding bake-off (EN/ZH golden)  
5. Measure p50/p95 at 2k / 50k / 250k (after chunking)  
6. Injection: search results never auto-fill write tool args  

## A.8 Exit criteria

- Recall@10 / nDCG@10 / MRR beat FTS-only on bilingual golden set  
- p95 documented at 2k / 50k / 250k cold+warm  
- Protected never appears as openable path in cloud request fixtures  
- CLI/docs present Search as default entry  

## A.9 Kill criteria

- Chinese 2-char query returns empty when files exist with those chars  
- One malicious PDF excerpt becomes a write-tool argument without a plan  

---

# Pillar B — Assistant (tool-calling; ship read-only first)

## B.1 Goal

A **full local file assistant** that chats and **tool-calls** like production LLM agents (OpenAI/Anthropic patterns): find, explain, relate, organize (optional heavy tools), never silent write.  
**Not** “architecture only forever” — **ship read-only loop in P2**; writes in P4 after undo journal.

## B.2 Inputs the model may use

| Input | How |
|---|---|
| Search hits | INDEX cards from Pillar A |
| Approved + witnessed relationships | `list_related` |
| Deadlines | `list_deadlines` |
| Item detail | `read_item` (on demand) |
| Pipeline pieces | Deferred tools only when user asks to organize |

All tool outputs tagged **`untrusted_data=true`** when derived from file/email text.

## B.3 Output contract

```json
{
  "answer": "…",
  "citations": [{"item_id": "…", "source_ids": ["…"]}],
  "plan_id": null,
  "egress": {"item_ids": [], "bytes": 0, "provider": "…", "model": "…"}
}
```

No silent approve/move. If a write is proposed → **plan object** for human approval.

## B.4 Agent loop

```
user → model(tools≤10) → tool_calls
    → validate schema → policy (privacy + risk tier)
    → execute → tag untrusted → return
    → … until final answer
    → citations required when items used
    → append egress ledger
```

| Phase | Model |
|---|---|
| Tool follow-ups / find | Cheap BYOK |
| Multi-step organize / recovery | Frontier BYOK |
| Local explain/find option | Optional on-device (Apple FM etc.) |

**No lane router gate** — optional cheap *hint* to preload deferred tools / tier only.

## B.5 Tool catalog

**Always on:** `find_files` · `read_item` · `list_related` · `list_deadlines` · `explain_file` · `ask_user` · `request_tools`  

**Deferred:** `scan_refresh` · `extract_one` · `propose_groups` · `propose_tree` · `place_preview` · `freeze` · `apply_moves` · `undo_moves` · `propose_links` · `accept_link` · `reject_link` · `sync_mail` · `sync_calendar`  

**Bulk summarize/group:** Map-Reduce — one isolated constrained schema call per file.

## B.6 Approvals (writes)

- Plan-level, risk-tiered (not per-file spam)  
- UI from plan `(src, dst, count, reversible)` — never model prose  
- Auto-allow only pre-authorized reversible in-scope ops  
- Track &lt;2s approval as fatigue signal  

## B.7 Progress

| Piece | Status |
|---|---|
| Architecture | **Done (this + parent report)** |
| Tool runtime / `chat` / `ask` CLI | **Done** (read-only default) |
| Egress ledger | **Done** |
| Injection golden trajectories | **Done** (pass^3 gates) |
| Write tools + plan approval | **Done** (env-gated apply/undo + deferred P6) |

## B.8 Build tasks

1. P0: eval harness + injection fixtures + threat tags  
2. P2: runner + read-only tools + egress ledger  
3. P3: undo journal `(plan_id, item_id, file_id, content_hash, src, dst, state)` + dry-run  
4. P4: apply/undo/link tools behind plan approval  
5. P6: wire heavy pipeline tools behind `request_tools`  
6. Post-P2: index encryption + Touch ID for held detail opens  

## B.9 Exit criteria

- Golden find/explain trajectories **pass^3** ≥ target  
- **0** injection-induced write tool calls  
- Apply without approval **fails** in tests  
- Egress ledger lists every cloud turn  

## B.10 Kill criteria

- File text alone selects `apply_moves` arguments  
- Held body appears in any request fixture  

---

# Pillar C — People / projects as first-class citizens

## C.1 Goal

`project`, `course`, and later `person` are real **items** (not view stubs).  
Board/Graph hubs are those rows. Relationships are evidenced and reviewable.

## C.2 Identity rules

| Type | Mint from | Durable key |
|---|---|---|
| `course` | `named_courses` answers | `course:<casefold name>` |
| `project` | `named_projects` answers | `project:<casefold name>` |
| `person` | addresses / user confirmation (later) | local id; address = alias |
| `file` / `email` / `event` | existing identity / mailbox | as today |

**Never:** folder-named third parties as auto destinations without rules (privacy).  
Empty profile → no forced hubs; recognition unchanged.

## C.3 Relationships

| rel_type | Confidence path | Auto-draw on default graph? |
|---|---|---|
| `duplicate-of` / `version-of` | witnessed (hash / grouping) | witnessed OK (proposed until approve) |
| `attached-to` | witnessed (hash match) | yes when witnessed |
| `member-of` | witnessed (name in filename) or inferred (connector) | only after approve; inferred hidden |
| `about` | inferred (connector) | hidden until approve |
| `from-person` | later | review-only |

Semantic `group_edges` **never** projected into life relationships.

## C.4 Progress

| Piece | Status |
|---|---|
| Course/project mint (`profile_items`) | **Done** |
| Connector `member-of` / `about` proposed | **Done** |
| Typing + declared lives | **Done** |
| Board/graph query use hubs | **Done** (CLI) |
| Person items + aliases | **Done** (`people`) |
| Entity merge precision suite | **Done** (`test_people_merge_precision`) |
| Graph/Board GUI | **Out of scope now** (CLI views remain) |

## C.5 Build tasks

1. Keep mint on `project_context_graph`  
2. Person mint from email addresses (opt-in, aliased)  
3. Merge/dedup protocol: blocking keys → human confirm  
4. Eval: entity merge precision on labeled set  
5. Ensure board Unplaced + hubs always real `item_id`s  

## C.6 Exit criteria

- Declared course name → one course item; file with name in label → proposed `member-of`  
- Inferred edges never default-drawn  
- Person merge precision meets labeled-set bar  
- No third-party name becomes a folder destination without rule  

## C.7 Kill criteria

- Semantic edge appears as `relationships` row  
- Connector writes `state=approved`  

---

# Pillar D — Correction memory that generalizes (Tencent corrective)

## D.1 Goal

Learn from user corrections **with audit drill-down**, without unsafe auto-filing.  
Exact suppress remains the safety floor. Generalization is **additive, flagged, dark until gate**.

## D.2 Layers

```
L0 DiffEvent   {diff_id, ai_proposal, expert_fix, item_ids[], basis, session_flags}
L1 Atom        {atom_id, rule_text, kind, confidence, heat, source_diff_ids[], superseded_by}
L2 Cluster     Markdown under playbook/clusters/  (human-readable)
L3 Profile     Markdown under playbook/profiles/  (human-readable)
```

**MAINTAIN:** top-K similar atoms (vector→FTS→skip) → **ADD or supersede** (prefer ADD + `superseded_by` over fragile LLM merge).  
**RETRIEVE:** hybrid index cards; inject INDEX; bump heat on full load.

## D.3 Two versions

| Version | Behavior | When |
|---|---|---|
| **v1** | Explicit user rules + few-shot retrieval of 3–5 similar DiffEvents at proposal time | Ship first |
| **v2** | L1 atoms with hard links; ADD/supersede; no delete | After v1 beats baseline |

Sessions that read untrusted files: write **L0 only** until human promotes.

## D.4 Gate (replaces F1 ≥ 0.65)

On frozen owner-labeled set:

- **Precision ≥ 0.95** on proposals the system is willing to make  
- Report **abstention rate** + **coverage floor** (cannot pass by abstaining on everything — T-P4-01)  
- Online: acceptance rate + **7-day undo rate**  
- Must **beat rules-only (v1)** on both before atoms steer anything  
- v1 steering waits until `propose_*` tools exist (T-P4-03); L0 capture may start earlier 

Never steers recognition/filing while dark. Never shadows safety holds.

## D.5 Interaction with exact suppress

| Layer | Role |
|---|---|
| `is_suppressed` / `basis_is_rejected` | Always on; exact |
| Memory atoms | Optional prior for *proposals* only after gate |
| Safety domains | Untouchable by memory |

## D.6 Progress

| Piece | Status |
|---|---|
| Exact suppress (facts/links) | **Done** |
| DiffEvent table (L0) | **Done** (`memory_l0`) |
| Atom table (L1) + ADD/supersede | **Done** (`memory_v2`) — dark by default |
| v1 rules + few-shot | **Done** (`memory_v1` injects into system prompt) |
| v2 atoms steering | **Done dark** — needs `ASSISTANT_ATOMS_STEER=1` + passing gate |
| L2/L3 Markdown rollups | **Done** (`playbook_rollups` → `playbook/clusters|profiles`) |
| Precision gate harness | **Done** — frozen golden + `tools/run_memory_gate_eval.py` in CI |

## D.7 Build tasks

1. Schema: `diff_events`, `memory_atoms`, heat, cursor  
2. Capture DiffEvent on reject/edit/accept-correction  
3. v1: rule store + few-shot retrieve into propose_* tools  
4. v2: EXTRACT batch + ADD/supersede writer  
5. Gate harness; dark flag default on  
6. Injection: untrusted session → L0 only  

## D.8 Exit criteria

- Drill-down atom → DiffEvent → item_ids works  
- Same-batch conflict cannot leave two live contradicting atoms without supersede  
- Gate metrics computed in CI  
- Dark default: 0 recognition changes from atoms  

## D.9 Kill criteria

- Atom steers filing while dark  
- Hold lowered by a memory rule  
- LLM merge deletes history without `superseded_by`  

---

## Pillar dependency graph

```
P0 eval/injection ──┬──► P1 Pillar A (hybrid find)
                    └──► P2 Pillar B read-only (uses A)
                              │
                    P3 undo journal
                              │
                    P4 Pillar B writes
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   P5 Pillar C polish   P6 heavy organize    P7 Pillar D memory
```

| Pillar | Can start | Blocked on |
|---|---|---|
| A | After P0 golden set | — |
| B read-only | After A `find_files` MVP | P0 injection fixtures |
| B writes | After P3 undo journal | A+B read-only |
| C polish | Parallel after mint (mostly done) | Person = after P2 |
| D | After P0; v1 parallel with B | Gate before any steer |

---

## One-page status

| Pillar | Planned? | Built? | Next phase |
|---|---|---|---|
| **A Meaning-search** | Yes | Hybrid+CJK+chunks+RRF; ZH bake-off; live FSEvents | 250k SLO; live Downloads scale |
| **B Assistant** | Yes | Read-only + P4 apply/undo (env-gated) + P6 deferred tools | more write dogfood |
| **C People/projects** | Yes | Mint+connector+views + person/aliases/merge + precision suite | live mailbox person mint |
| **D Correction memory** | Yes | L0 + v1 + L1 atoms dark + gate in CI | L2/L3 after production gate pass |

---

## Owner checklist

- [ ] Pillar A contracts + exit/kill accepted  
- [ ] Pillar B ship-read-only-first + injection/egress accepted  
- [ ] Pillar C person later + inferred review-only accepted  
- [ ] Pillar D v1→v2 + precision≥0.95 gate (not F1 0.65) accepted  

When all four are checked, implementation follows the phase table in the parent architecture report.
