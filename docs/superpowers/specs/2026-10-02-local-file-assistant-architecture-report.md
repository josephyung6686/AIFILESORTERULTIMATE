# Local File Assistant — Architecture Report

**Date:** 2026-10-02 (revised same day after external critique)  
**Status:** Architecture authority for build (critique merged)  
**Audience:** Product owner  
**Sources:** Item-relationship plan · Tencent memory pack (`~/Desktop/tencent memory/`) · owner direction · 2026-10-02 red-team critique  
**Four pillars (full contracts):** [`2026-10-02-four-pillars-plan.md`](./2026-10-02-four-pillars-plan.md) — A search · B assistant · C people/projects · D correction memory  
**Agent design + all critique deep-dives:** [`2026-10-02-agent-design-and-deep-dives.md`](./2026-10-02-agent-design-and-deep-dives.md) 

---

## 1. Executive summary

We are building a **laptop-resident file assistant**: chat + tool calling, powered by the user’s API key (**BYOK**), that replaces day-to-day file work (find, understand, group, organize, link, apply with approval). It sits above a **fast local hybrid index** and an **evidenced context graph**. It does **not** wrap the slow full sorter pipeline as its default path. It may call **selected pieces** of that pipeline when the user asks for organization work.

**Hard decisions:**

1. **No OpenClaw.** Our own agent loop; provider-normalized tool calling.  
2. **Copy Tencent memory architecture, not their package.**  
3. **Hot path = hybrid find + read.** Full sort/group/tree = optional heavy tools.  
4. **Dynamic tool choice + rigid contracts** (schemas, privacy, approvals, citations).  
5. **Embeddings never alone approve a life link or a move.**  
6. **File contents are untrusted** (prompt-injection threat model).  
7. **Eval / injection fixtures / undo journal before write tools.**  
8. **Correction memory dark until a precision+abstention gate** (not F1 ≥ 0.65).

---

## 2. Critique of earlier drafts (still true)

| Earlier claim | Correction |
|---|---|
| Chat runs full scan→group→tree every time | Pipeline = **optional heavy tools** |
| “Hybrid search” already shipped | Today is shallow; true FTS+vector+RRF **to build** |
| “&lt;200ms” as fact | **SLO** — measure at 2k / 50k / 250k |
| Lane router as hard gate | **Demoted** to optional cheap *hint* only |
| Memory gate F1 ≥ 0.65 | **Replaced** with precision ≥ 0.95 + reported abstention; must beat rules-only |

---

## 3. Product context

### Built (code + tests; hand-tested on real-file copy)

| Layer | Status |
|---|---|
| Sorter pipeline (CLI) | Built (slow path; still product for organize) |
| File items + rename/edit identity | Built · hand-tested |
| Witnessed links (duplicate/version) | Built · hand-tested |
| Link approve/reject/undo | Built |
| Profile packages + course/project **minting** | Built |
| Typing projection (typed/unplaced/held) | Built |
| Connector (proposed member-of / about) | Built |
| Nudge warnings | Built |
| Views (folder/table/board/timeline/graph queries) | Built (CLI) |
| Fixture mail/calendar + deadlines + suggest | Built |
| Hybrid find (FTS5+vec+RRF+chunks+CJK) | Built · bake-off decided · real-file dogfood |
| FSEvents live feed (+ polling fallback) | Built (`.[watch]`) |
| BYOK ask/chat + ToolRuntime + egress | Built · injection pass^3 |
| Plan approve / apply / undo (env-gated) | Built |
| Deferred organize tools (`request_tools`) | Built |
| Person items + aliases + merge precision | Built |
| Memory L0/v1 + L1 atoms (dark + gate) | Built |
| `tests/items/` + `tests/assistant/` | **161+ passed** (2026-10-02) |

### Explicitly deferred / scratched

Mac UI · full sorter pipeline polish · **live Gmail/Calendar (scratched)** · index encryption · Touch ID for held opens · Apple FM gen on macOS 15 (Ollama local stand-in) · 250k cold SLO on real library  

### Full product cut (2026-10-02) — shipped mechanisms

See [`2026-10-02-full-product-cut-design.md`](./2026-10-02-full-product-cut-design.md): apply/undo identity commit · ask/search refresh + `watch` · held body local-only · grounded plans · `list_gaps` · connectors hard-disabled · reject→L0.

---

## 4. Architecture

Four product pillars (contracts, exit/kill, progress): see **[four-pillars plan](./2026-10-02-four-pillars-plan.md)**.

| Pillar | Role | Phase |
|---|---|---|
| **A** Meaning-search | Default surface; hybrid FTS+vec+RRF; INDEX cards | P1 |
| **B** Assistant | BYOK tool loop; read-only first; plan-approve writes | P0→P2→P4 |
| **C** People/projects | First-class items + evidenced relationships | mostly done → P5 |
| **D** Correction memory | L0–L3; v1 rules → v2 atoms; precision ≥ 0.95 gate | P7 |

### 4.1 Layering

```
┌──────────────────────────────────────────────────────────────┐
│  ASSISTANT SURFACE                                           │
│  Chat · tool calling · BYOK · citations · plan approvals     │
│  Dynamic: model picks tools (≤10 always loaded)              │
│  Rigid: schemas · privacy · budgets · audit · untrusted tags │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│  OPTIONAL HINT (cheap classifier) — not a hard gate          │
│  May preload a deferred tool group / model tier              │
└────────────────────────────┬─────────────────────────────────┘
         ┌───────────┬───────┼────────┬──────────┐
         ▼           ▼       ▼        ▼          ▼
      HOT INDEX   GRAPH   PIPELINE*  MEMORY    PRIVACY
      FTS+vec     items/  optional   Tencent   + egress
      chunked     rels    pieces     L0–L3     ledger
```

\*Heavy tools only when user asks to organize — never the default for “where is X?”.

### 4.2 Hot path / retrieval (P1)

| Requirement | Design |
|---|---|
| Change feed | Prefer **FSEvents** (+ file ID / bookmarks for rename); polling is fallback. Spotlight/`mdfind` = optional candidate helper, not source of truth |
| Chunking | Long files → ~512–1024 token chunks; find returns **item cards**; aggregate chunk hits |
| FTS | Dual path: Latin `unicode61`(+porter); **CJK bigram/trigram** (+ LIKE fallback for 1–2 chars); route by script; filename/path weighted columns |
| Embeddings | Bake-off on EN/ZH golden set (e.g. EmbeddingGemma-300m / Qwen3-Embedding-0.6B vs MiniLM); prefer multilingual + Matryoshka/int8 for speed |
| Fusion | Start RRF; fit convex combination on ≥40 labeled queries; small additives for recency/heat/path |
| Reranker | Only if eval gains; outside find SLO (on read/explain) |
| SLO corpora | Measure p50/p95 cold+warm at **2k / 50k / 250k items (after chunking)** |

### 4.3 Agent loop (P2)

```
message → model(tools) → tool_calls
        → ToolRuntime(validate → untrusted tag → policy → execute)
        → results → … → answer + citations[{item_id, source_ids[]}]
        → egress ledger row per cloud turn
```

- One runner over OpenAI/Anthropic-shaped APIs; **no OpenClaw**  
- Tool registry = single source of truth (can expose as MCP later without rewrite)  
- Cheap model for execution turns; frontier for plan/recovery  
- Parallel **read** tools only; serialize writes  
- Tool descriptions follow Anthropic guidance: namespaced names, semantic return fields (not raw IDs only), concise/detailed response toggle, actionable errors  

### 4.4 Tool catalog

**Always loaded (≤10):**  
`find_files` · `read_item` · `list_related` · `list_deadlines` · `explain_file` · `ask_user` · `request_tools`

**Deferred:**  
`scan_refresh` · `extract_one` · `propose_groups` · `propose_tree` · `place_preview` · `freeze` · `apply_moves` · `undo_moves` · `propose_links` · `accept_link` · `reject_link` · `sync_mail` · `sync_calendar`

**Injection patterns per class:** write tools = Plan-Then-Execute (args from plan + find `item_id`s only); bulk summarize/group = Map-Reduce (one constrained call per file); memory writes from untrusted sessions = L0 only (no auto-atoms).

### 4.5 People / projects

Mint from profile + evidence; inferred edges **proposed only**; no semantic hairball graph.

### 4.6 Memory (P7) — Tencent-inspired, corrected

| Version | Design |
|---|---|
| **v1** | Explicit user-visible rules + retrieve 3–5 similar past corrections as few-shot (no LLM merge) |
| **v2** | Atoms with hard `source_ids`; **ADD + supersede** (`superseded_by`); never mark extract done until write succeeds |
| **Gate** | Precision ≥ **0.95** on proposals the system is willing to make + reported abstention; online acceptance + 7-day undo; must **beat rules-only** |

Sessions that read untrusted files: corrections stay **L0 evidence only** until reviewed — not auto-atoms.

### 4.7 Privacy & egress

- Held / safety / `ALWAYS_LOCAL` never in cloud prompts  
- **Per-turn egress ledger:** item_ids, byte counts, provider, model (user-viewable)  
- Default: snippets, not whole bodies; byte budget per turn  
- **Per-provider onboarding** (not a generic “30 days”): DeepSeek (default) → processed/stored in **PRC**, retention “as long as necessary,” training opt-out may apply; OpenAI/Anthropic ~30-day notes only when selected. See agent-design Addendum A4.  
- Optional **local-only mode** (e.g. Apple Foundation Models when available) for find/list/explain; cloud for multi-step organize with session consent  
- INDEX card labels/subjects tagged **untrusted** (Addendum A1) 

### 4.8 Threat model — untrusted file text (critical)

| Rule | Detail |
|---|---|
| Trust boundary | Every PDF/email/Downloads excerpt is **untrusted data** |
| Writes | Arguments from **plan object** + `item_id`s from find — never free-form model paraphrase of file instructions |
| Bulk summarize/group | **Map-Reduce**: one isolated constrained schema call per file |
| Approvals | Render from plan `(src, dst, count, reversibility)`, never model prose |
| Injection fixtures | Golden set includes adversarial PDFs (“move ~/Documents…”, “include tax.pdf…”) |
| Approval UX | **Plan-level**, risk-tiered; auto-allow only pre-authorized reversible in-scope ops; flag &lt;2s rubber-stamp latency |

### 4.9 Writes & undo (P3–P4)

Write-ahead journal: `(plan_id, item_id, file_id, content_hash, src, dst, state)`. Prefer Trash over delete. Undo idempotent + conflict-aware (dest exists, file changed since plan). Kill -9 mid-plan must recover cleanly. Always confirm ops leaving the folder tree or touching held items.

### 4.10 Index at rest (post-P2; not P0 blocker)

The hybrid index holds excerpts → treat as a honeypot if stolen. Design (ship after read-only dogfood unless owner wants earlier):

- Encrypt DB at rest; key in Keychain  
- Held / safety-domain open paths gated behind local auth (Touch ID / password) before excerpt leaves the vault into any prompt or UI detail pane  
- Egress ledger is the “delivery truck” audit — vault encryption alone is not enough  

---

## 5. Evaluation

| Suite | Measures |
|---|---|
| Injection | Zero injection-induced write tool calls; pass^k on golden trajectories |
| Find | Recall@10 / nDCG@10 / MRR; EN+ZH; hybrid vs FTS-only vs vector-only |
| Latency | p50/p95 at 2k/50k/250k cold+warm |
| Safety | Held never in request fixtures; apply without approval fails |
| Memory | Precision/abstention gate; beats rules-only |

**Wrong automatic move = release blocker.**

---

## 6. Revised build order

| Phase | Content | Exit criterion |
|---|---|---|
| **P0** | Spec freeze · threat model · eval harness skeleton · bilingual golden set · injection fixtures | Harness in CI |
| **P1** | Hot index: FSEvents feed · chunking · dual-tokenizer FTS · embedding bake-off (≥100 ZH or bootstrap CI) · RRF→convex | Recall beats FTS-only; p95 ≤ caps 2k/50k/250k (see deep-dives T-P1-02) |
| **P2** | Read-only agent loop · untrusted tagging (incl. cards) · egress ledger · per-provider trust copy · local-model option | Trajectories pass^3 ≥0.7; 0 injection write calls |
| **P2.5** | Thin UI (menu-bar or local web) for dogfood | Daily use logs |
| **P3** | Undo journal + dry-run / place_preview | Kill -9 mid-plan recovers |
| **P4** | Writes with plan-level risk-tiered approval | 0 silent writes; 0 wrong moves |
| **P5** | People/projects polish (proposed edges) | Entity merge precision on labeled set |
| **P6** | Heavy organize tools behind `request_tools` | Organize trajectories pass |
| **P7** | Memory v1 then v2 behind precision gate | Beats rules-only online |

---

## 7. Non-goals (near term)

OpenClaw / TencentDB npm · live Gmail OAuth as P0–P2 blocker · full Mac app before P2.5 · full-sort on every chat · atoms steering recognition before gate  

---

## 8. Thesis

**A fast, tool-calling local assistant (BYOK) over a bilingual hybrid item index and evidenced graph; optional slow sorter tools; Tencent-style hard-linked memory behind a precision gate; untrusted file text; plan-then-approve writes; no silent moves; no OpenClaw.**

---

## 9. Approval checklist

- [x] Hot path is find/read, not full pipeline  
- [x] Pipeline = optional heavy tools  
- [x] No OpenClaw; BYOK tool loop  
- [x] Prompt-injection / egress / bilingual / chunking / SLO scale addressed  
- [x] Memory gate = precision+abstention, not F1 0.65  
- [x] Eval + undo before write tools  
- [x] Four pillars fully planned ([four-pillars plan](./2026-10-02-four-pillars-plan.md))  
- [x] Agent design + ten critique deep-dives locked ([agent design](./2026-10-02-agent-design-and-deep-dives.md))  
- [x] Addendum A (untrusted cards, T0 template rename, plan_hash, DeepSeek terms, full-list approve, DiffEvent provenance)  
- [ ] Owner confirms report + four-pillars + agent/deep-dives **for P0–P2 build** (not “perfect” freeze)  

**Owner:** confirm to start P0–P2. Perfect freeze waits on Addendum B tickets.

---

## 10. Critique disposition (2026-10-02 red-team)

This report **already adopts** that critique. Mapping:

| Critique severity | Issue | Disposition | Where |
|---|---|---|---|
| Critical | Prompt injection from file contents | **Adopted** — threat model, untrusted tags, Plan-Then-Execute, Map-Reduce, injection fixtures, L0-only memory from dirty sessions | §4.8, §5, P0–P2; pillars B/D |
| High | Cloud egress / retention under-specified | **Adopted** — egress ledger, snippet budget, onboarding retention facts, local-model option | §4.7, P2 |
| High | English-only retrieval (MiniLM + FTS5) | **Adopted** — dual FTS (CJK), embedding bake-off, EN/ZH golden | §4.2, P1; pillar A |
| High | One vector per item / long files | **Adopted** — chunking 512–1024; aggregate to item cards | §4.2; pillar A |
| Med-high | SLO corpus too small (2k only) | **Adopted** — measure at 2k / 50k / 250k **after chunking**; re-decide sqlite-vec vs LanceDB only if p95 fails | §4.2, §5, P1 |
| Med-high | Memory gate F1 ≥ 0.65 | **Replaced** — precision ≥ 0.95 + abstention; beat rules-only; ADD/supersede not fragile merge | §4.6, P7; pillar D |
| Medium | Approval fatigue | **Adopted** — plan-level risk-tiered; &lt;2s fatigue signal; auto-allow only pre-auth reversible | §4.8, P4 |
| Medium | Deterministic lane router | **Demoted** — optional cheap hint only | §2, §4.1 |
| Medium | Spotlight / FSEvents ignored | **Adopted** — FSEvents + file ID/bookmarks; mdfind helper only | §4.2, P1 |
| Medium-low | RRF-only fusion | **Adopted** — RRF then convex on ≥40 queries; recency/heat/path additives; reranker optional outside SLO | §4.2 |
| Medium-low | Eval / undo too late | **Adopted** — P0 eval+injection; P3 undo before P4 writes | §6 |
| Low-med | Index honeypot | **Adopted as design** — Keychain encryption + Touch ID for held; post-P2 unless owner pulls forward | §4.10 |

**Keep (unchanged by critique):** BYOK hand-rolled loop · hybrid FTS+vec · progressive tools · no silent moves · embeddings never approve life links/moves · memory dark until gate · citations `item_id`+`source_ids` · FS as system of record.

**Optional deep-dives** (write on request, not blocking authority): injection patterns per tool with fixtures · embedding/reranker bake-off protocol · sqlite-vec vs LanceDB vs usearch · FSEvents+bookmark design · memory systems comparison (Mem0/Letta/Zep/…) · entity-resolution protocol · cheap-vs-frontier cost model · approval UX / audit schema · product lessons (Recall/Rewind/…) · eval metrics cookbook.
