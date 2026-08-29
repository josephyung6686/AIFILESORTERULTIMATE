# Catalogue 11 — pack registry

Authored 2026-08-22 by R5. Nothing here is committed by the authoring agent — Joseph reviews and
commits.

**The v1 pack is awaiting Joseph.** D4 (ratified 2026-08-21) fixes that v1 ships **one**
jurisdiction's value lists, injected per deployment, and that `jurisdiction` is a value, never a
field name, never a destination dimension. The ratification does not name *which* jurisdiction;
the DECISION-BRIEF records the fork ("design's examples are US, the catalogue authors wrote UK")
and defers the list to P10 planning. Until Joseph answers, no pack in this directory is
deployable, and `check.py` fails any manifest that claims `v1`.

## Registry

| pack | status | jurisdiction | contents | deployable |
|---|---|---|---|---|
| `00-example/` | `shape_example` | mixed on purpose (`null` in the manifest) | `record_type.json` — two rows, `W-2` (us) and `P60` (uk), both `proposal` from overnight prose | **never** — exists to make `_SCHEMA.md` concrete without picking a side |
| `us/` | sketched, **not authored** | `us` | first-wave members sketched in `RESEARCH.md` section 7 | no — does not exist on disk |
| `uk/` | sketched, **not authored** | `uk` | first-wave members sketched in `RESEARCH.md` section 7 | no — does not exist on disk |

No other packs exist and none may be added "to be safe" — D4 option 2 (multiple at launch) was
refused, and shipping a second jurisdiction is a new D4-sized decision, not a catalogue edit.

## Ratification protocol — what flips when Joseph answers

One answer, five edits, one commit:

1. Record the answer here (replace "awaiting Joseph" above with the chosen pack and the date).
2. Create `<chosen>/` with `_pack.json` (`status: candidate`, single `jurisdiction` tag) and the
   per-field value files, growing them from the matching sketch in `RESEARCH.md` section 7 —
   rows sourced honestly (`source_kind: official_list` with register citations once a real
   register is consulted; `proposal` until then).
3. Fill the pack's `gate_slot_projections` for all four catalogue-08 slots (empty-with-why is
   legal per slot; silence is not).
4. Flip the pack to `status: v1` **and** relax `check.py`'s no-v1 assertion in the same edit —
   the check names this file so the two cannot drift apart silently.
5. Leave `00-example/` as the shape document (recommended), or delete it in the same commit if
   Joseph prefers — it must never become loadable either way.

What does **not** change on ratification: field keys (they are jurisdiction-neutral and stay
so), catalogue 08's detector rules (the hooks already point the right way), R4's institution
lists (institutions are theirs; the same D4 fork governs which register fills them), and the
`unsupported_region_copy` slot (already present in every manifest — a chosen pack makes it
*reachable*, since only then is there a supported region to be outside of).

## The unpacked deployment

A deployment with **no** pack loaded is legal and safe: safety detection does not consume pack
values as a precondition (catalogue 08's rules fire on shapes, generic labels and structure;
its four R5 slots *extend* them), and P7's absence rule resolves unclassified files to
`unreadable_unclassified`, never `public_low`. What is lost without a pack is recognition
quality in finance/legal/government domains — files land in residual review — plus the honesty
string, which is exactly the situation `unsupported-region.md` exists for.
