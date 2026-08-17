# Database agent — product spec

Date: 2026-08-17  
Status: **canonical** — this is the contract for the GitHub repo  
Remote: [josephyung6686/AIFILESORTERULTIMATE](https://github.com/josephyung6686/AIFILESORTERULTIMATE)

This file supersedes conversation drafts. Joseph’s FileGraph write-up
(`docs/superpowers/specs/2026-08-16-filegraph-design.md` + `research/`) is **reference and
evidence**, not the product contract. Constraints we take from it are listed under
[Borrowed from FileGraph](#borrowed-from-filegraph).

---

## Product

A **general database agent**: a local app a busy person runs without Cursor. It helps them see
and shape how their files should live, then files into that shape.

It is not a lab-only regex sorter, and it is not an LLM inventing `Images/Science`.

**Sequence (locked):**

1. **Sort** — design the folder tree, then put files into it.  
2. **Catalog / ask** — index that world so you can ask “what do I have / where is this / what’s related.”  
3. **Later profiles** — lab (Nutrigene-style), then a personal OS (projects, people, “what I need next”).

Phase 1 is (1) only.

---

## Goal (Phase 1)

You pick messy **sources** (e.g. Downloads) and **destination roots** (Desktop, Documents,
Personal Projects). You see a visual folder graph, set how deep it should go, drag-and-drop to
mix and match, freeze the designated tree, then the agent files into **those** folders.

Nothing random is created inside Downloads when the real place already exists on Desktop.

Success: the tree you froze is the only legal landing zone; unmatched files stay put; every move
is previewed and undoable.

Phase 1 answers: **where does this file go, how sure are we, do we need you?**  
Later answers: what activity it belongs to, and what is useful now.

---

## Users

People too busy or lazy to sort. Not developers. Local browser window. A few bulk decisions, not
a terminal JSON workflow.

---

## Locked decisions

| Decision | Choice |
|---|---|
| Product | General database agent, not lab-first |
| Phase 1 | Structure canvas, then sort |
| Phase 2 | Catalog + ask |
| Destinations | Frozen tree. Never invent `Downloads/Work/Misc` |
| Destination roots | A file may land in any **chosen destination root** (Desktop, Documents, Projects, …), not only inside the source folder |
| Existing folders | The schema. Cross-root links so Desktop/Work/Plasmole is visible while sorting Downloads |
| New folders | Only if you add them on purpose on the canvas and freeze |
| Profile | Short optional role card **before** the canvas. Skip allowed |
| Profile may | Rank/suggest nodes that already exist or that you add |
| Profile may not | Invent a path, move files, or skip freeze/confirm |
| Age | Not asked |
| Classifier (Phase 1) | Names, paths, extensions, siblings → frozen nodes only. Unmatched stay put |
| Apply | Dry-run default; confirm to move; journal; undo |
| Overwrite | Never. Same name, different bytes → ask; file stays. No silent `file (1).ext` |
| Rename | Not in Phase 1 |
| LLM inventing folders | Never. If a model is added later, it may only choose among frozen nodes |
| Decision log | Written from day one. Not read for routing yet. Stores **original suggestion and final choice** |
| What may move | **Loose files only.** Do not reach into a folder the user already organized |
| Directories | Never moved as units. Files move; empty dirs may be pruned only if journalled |
| Delete | Never. Duplicates, when handled later, go to quarantine with a manifest |
| Sensitive content | Never leaves the machine |
| Lab rules | Later **profile**, not Phase 1 |
| Interface | Standalone local UI (localhost) |

---

## Architecture

```text
Pick sources + destination roots
  → Profile card (optional, ~15s)
  → Index existing folders into a graph
       node = a folder that already exists
       edge = parent/child, plus same-name / likely-same-project across roots
       skip project/build trees as destinations (see Borrowed)
  → Structure canvas (quick step)
       visual tree; set depth; drag-drop merge/nest/ignore/add
       existing one colour, your edits another
       FREEZE = the only allowed destinations
  → Classify each loose source file onto a frozen node only
  → Plan (dry run) → you confirm → apply with undo
  → Decision log (append-only)
```

The graph is a **folder map**, not a people/events knowledge graph. That comes with catalog/ask.

---

## Components

| Piece | Job |
|---|---|
| **Root picker** | Sources and destination roots |
| **Profile card** | Role + optional tags. Skip = graph-only personalization |
| **Indexer** | Walk roots. Build folder graph. List loose files. Do not move. Skip protected trees as destinations |
| **Structure canvas** | Visual tree. Depth, drag-drop, deliberate add. Freeze designated tree |
| **Classifier** | Loose file → frozen node. Never a path the canvas did not freeze. Abstain when unsure |
| **Planner** | `sort-plan.json`: destination, reason, disposition (`match` / `ask` / `skip`), original suggestion |
| **Applier** | Dry-run default. Journal then move. Never overwrite. Undo. Destination must resolve inside a chosen destination root |
| **Agent UI** | Profile, canvas, “I would file N. M need you. Nothing has moved yet.” Confirm, leftovers, undo |
| **Decision log** | Append-only. Suggestion + final choice + actor |

---

## Data flow

1. Pick sources and destination roots.  
2. Optional profile card.  
3. Indexer builds the folder graph (project-skip on destinations).  
4. Canvas shows it, shaped by profile if present. You remix and **freeze**.  
5. Classifier assigns **loose** source files only onto frozen nodes.  
6. Dry-run plan. Nothing has moved.  
7. Confirm → journal → move matches. Leftovers stay.  
8. You resolve leftovers onto a designated node, or skip.  
9. Undo last run restores that run.  
10. Plan / move / ask / undo append to the decision log (suggestion + choice).

---

## Profile (Phase 1)

**Ask:** role = student / business / engineer / researcher / mixed. Optional tags (CS, lab, freelance, …).

**Effect:** bias which existing folders are promoted on the canvas (student → Courses if it
exists; business → Clients). You still freeze.

**Not:** tagging individual files; age; a long interview; creating folders without you.

This is template *selection*, not a tag filesystem. The graph of folders is still inferred from
disk. The card only ranks what to show first.

---

## Borrowed from FileGraph

Taken as **constraints**. Not taken: his OCR/embedding/Leiden engine, Phase 0-before-UI build
order, auto `file (1).ext`, or “never ask the user anything.”

1. **Project-skip destinations, not just sources.** A folder is never a destination if any
   ancestor is `node_modules`, `.git`, `venv`, `build`, `dist`, `target`, `vendor`, `Pods`,
   `site-packages`, `Library`, `__pycache__`; if any ancestor contains `package.json`,
   `requirements.txt`, `Cargo.toml`, `go.mod`; or if it is a build artefact. Check ancestors to
   the volume root. Measured: 1,266 raw destination candidates → 30 after this filter.
2. **Identity is not a category.** Tokens that name *who you are* (`joseph`, student IDs,
   `columbia.edu`) must not become folders. Tokens that name *what a file is* (`screenshot`,
   `resume`) may, even when common. Frequency cannot tell these apart.
3. **Unmatched stay put is the quality bar.** A smaller correct set beats filing everything.
   ~32% high-precision placement is a good first run if nothing is misfiled.
4. **Log original suggestion and final choice.** An unedited approval and a correction are
   different facts. Do not learn only from the destination that landed.
5. **Sensitive content never leaves the machine.** Government ID, medical, financial, legal,
   credentials — forced local even if a cloud model exists later.
6. **Only loose files move.** Do not reach into a folder the user already organized.
7. **Destination must resolve inside a chosen destination root** (after symlink resolution), not
   necessarily inside the source. Cross-root sort (Downloads → Desktop) is required. Plans are
   user-editable, therefore untrusted input.

Evidence for (1)–(5) lives in `research/` and
`docs/superpowers/specs/2026-08-16-filegraph-design.md`.

---

## Error handling

- Dry-run default. First contact never moves until confirm.  
- Never overwrite. Same content at destination → skip as already filed. Same name, different
  bytes → `ask`; file stays.  
- Never invent folders in the source.  
- Frozen node deleted before apply → that file becomes `ask`, not silent create.  
- Classifier cannot name a path that is not frozen — including if the profile “wants” it.  
- Permission / in use / disk full → stop apply, keep journal, undo what moved.  
- Undo: restore committed moves; if edited after the run, leave it and report; never delete the
  destination to fake success.  
- Crash: journal before each move; restart offers undo of that run.  
- Offline. Local only.  
- Skipping the profile card still works.

---

## Testing (Phase 1)

Fixture: fake `Downloads` with loose files + fake `Desktop` that already has `Work/Plasmole`.

- A Plasmole-ish file is planned to Desktop, **not** to a new `Downloads/Plasmole`.  
- Destination not on the frozen tree is rejected (even with a matching profile).  
- `Desktop/Hoyahacks/node_modules/...` is not offered as a destination.  
- Skip profile → canvas still runs.  
- Dry run touches nothing.  
- Apply + undo restores the tree.  
- Same name, different bytes → no overwrite and no silent `(1)` rename.  
- Nested files under an already-organized folder are not in the move set.  
- No Nutrigene regex in this suite.

---

## Phase 1 out of scope

- Catalog / ask.  
- Lab profile (instrument sidecars, well maps, `raw/{date}/{instrument}`).  
- FileGraph pipeline as the app: OCR, GLiNER, embeddings, Leiden, fitness scorer before UI.  
- Local LLM on every file.  
- Knowledge graph of people/events, “what you need next,” rename suggestions.  
- Copying [hyperfield/ai-file-sorter](https://github.com/hyperfield/ai-file-sorter) source (AGPL).

---

## Later (after Phase 1 sorts)

When classify needs to get smarter, **adapt** from FileGraph — still freeze-gated:

- EXIF / first-page PDF text for opaque names.  
- Duplicate and version detection → quarantine, never delete.  
- Classify into frozen folders first; propose new canvas nodes only for leftovers.  
- Abstain when the top two destinations are too close.  
- Hand-written templates as **canvas suggestions**, never as silent folder creation.

**Do not take:** fitness scorer blocking the UI; GPL stacks (`leidenalg`, PyMuPDF); feeding a
model’s own output back as ground truth without a negative signal.

---

## North star

Long-term: a personal file intelligence system — what a file is, what work it belongs to, how
*this* user handles similar material, what is useful now. The lasting advantage is a personalized
model that improves with every interaction, not a generic categorizer.

Phase 1 only takes: freeze destinations, confidence-aware filing, ask when stuck, write a
decision log, a short role card.

---

## Deferred, in order

1. Implementation plan for Phase 1 (canvas + profile + classify + apply/undo).  
2. Catalog / ask.  
3. Smarter classify (FileGraph adaptations above).  
4. Lab profile.  
5. Act on the decision log; projects/people graph; predictor / OS features.

---

## Repository layout (this contract)

```text
docs/superpowers/specs/2026-08-17-database-agent-design.md   THIS FILE — product spec
docs/superpowers/specs/2026-08-16-filegraph-design.md        research spec (not the contract)
research/                                                    measurement scripts
README.md                                                    points here
```
