# Database agent

A local app that lets you **design a folder tree**, freeze it, then files only what it is
confident about — leaving everything else where it is.

**Product spec (canonical):** [`docs/superpowers/specs/2026-08-17-database-agent-design.md`](docs/superpowers/specs/2026-08-17-database-agent-design.md)

**Status:** spec locked for Phase 1. Not implemented yet.

---

## Phase 1 loop

```text
1. PICK        sources (e.g. Downloads) + destination roots (Desktop, Documents, …)
2. PROFILE     optional role card (student / business / engineer / …) — skip allowed
3. INDEX       existing folders become a graph (cross-root; skip node_modules etc.)
4. CANVAS      visual tree — set depth, drag-drop, add folders only on purpose
5. FREEZE      those nodes are the only legal destinations
6. CLASSIFY    loose files may only land on a frozen node — unmatched stay put
7. APPLY       plan → dry run → confirm → move, with undo
```

Freezing turns “what categories should exist?” into “which of these folders does this file
belong to?” The first is how organizers go wrong. The second is reviewable.

---

## What we take from the FileGraph research

The measurements in `research/` and the long FileGraph write-up stay as **evidence**, not as the
app architecture. The product spec borrows these constraints:

- Skip project/build trees as **destinations**, not only as sources
- Identity tokens are not folders; type tokens can be
- Unmatched stay put
- Log the original suggestion and the user’s final choice
- Sensitive content never leaves the machine
- Only loose files move
- Destinations must sit inside a **chosen destination root** (so Downloads → Desktop is legal)

Full contract: the spec linked above. Research write-up:
[`docs/superpowers/specs/2026-08-16-filegraph-design.md`](docs/superpowers/specs/2026-08-16-filegraph-design.md).

---

## Repository

```text
docs/superpowers/specs/2026-08-17-database-agent-design.md   product spec
docs/superpowers/specs/2026-08-16-filegraph-design.md        research spec
research/                                                    scripts behind the measurements
```
