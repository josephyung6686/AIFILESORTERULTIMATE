# Execute P7 — Pillar D memory atoms (dark)

**Authority:** four-pillars D + agent-design Addendum T-P4-01/03.

## Shipped

1. `memory_atoms` + `memory_atom_gate` schema (`assistant/memory_v2.py`)
2. ADD / supersede (never DELETE); hard link `source_diff_ids`
3. Dirty DiffEvent → promote refused (L0 only)
4. Steering dark until latest gate passed; `ASSISTANT_ATOMS_STEER=0` force-dark
5. Gate floors: precision ≥ 0.95, coverage ≥ 0.20, beats rules-only
6. Dirty DiffEvent promote refused; v1 retrieve surfaces atoms only when open

## Still open (not blocking dark ship)

- Frozen owner-labeled precision eval set in CI
- L2/L3 Markdown rollups under playbook/
- Online acceptance + 7-day undo rate dashboards
