# 09 · Residual template library (R3)

Slot values for the nine `00` residual templates, the shape a user-defined residual area must
fill, and the residual ↔ domain boundary joins. This is R3 research output: nothing here is
auto-enabled, nothing here is a roster node, and the nine names are `00`'s, fixed — this
catalogue fills slots, it does not rename or extend.

Authority on conflict: `planning/00-database-agent-product-design.md` (`00`) wins, then
`planning/prompts/ALIGNMENT.md`, then `planning/domains/CONNECTION.md`, then the R3 dispatch
prompt (`planning/prompts/03-residual-library.md`).

Quote convention across every file in this directory: curly double quotes are reserved for
verbatim `00` quotations and are mechanically verified by `check.py` on every run. Statements
about CONNECTION.md, the P10/P11/P7 SPECs, `planning/11-ops-runtime.md`, or sibling catalogues
are paraphrased and named, never curly-quoted.

Gate: `python3 planning/deferred-catalogues/09-residual-library/check.py` — exits non-zero on
any problem (nine names exactly, eight slots each, quote authenticity, no numeric JSON values,
Protected Records' constraint by construction, review-set projectability, terminal edges,
user-defined shape shipping zero templates).

## Who consumes what

- **P10 injects the definitions.** `01-nine-templates.json` fills the eight §7.2 slots for the
  nine §7.3 names. P10 owns the residual library (resolution M10) and surfaces it at tree
  design as an optional set of controlled branches; enablement, the three dispositions
  (physical-destination | review-only | leave-in-place), rename / relocate / merge /
  replace-with-existing, and the freeze consequence are all P10's, per its SPEC's Contract out
  §6. Nothing in this catalogue preselects a disposition, enables a branch, or names a
  filesystem path — `default_parent_location` is a display-label chain in the tree (P10
  resolution B3, paraphrased).
- **P11 reads the frozen result.** The residual workflow — surfacing screen, set-level
  decisions before any per-file model call, the eight-action controlled review — consumes
  enabled residual *nodes*, never these definitions. `residual_candidates` orders the broad
  homes worth offering from activation flags plus the `falls_through_to` edges recorded in
  `03-falls-through.json` (CONNECTION.md §8, paraphrased). A template the user did not enable
  has no node, so no model can name it — that is the whole enforcement mechanism.
- **User-defined areas use the same schema.** `02-user-defined-shape.json` is the form P13
  collects a custom residual area against — the same eight slot keys, so P10's enablement
  model, P11's workflow, and P12's path composition need no second code path. Zero
  user-defined templates ship: `00`'s example names (Things to Read, Ideas, Shopping Research,
  Memes, Travel, Receipts to Process, Clips, Stuff to Sort) are illustrations of user freedom,
  and `check.py` asserts none appears as a shipped template.

## Files

| File | Content |
|---|---|
| `01-nine-templates.json` | the nine templates × eight slots — value, injected slot, or explicit empty-with-why; plus the projection of `00`'s eight §7.5 review-set bullets onto the slots |
| `02-user-defined-shape.json` | the eight slots a user-defined residual area must supply, who supplies each, naming and shadow rules |
| `03-falls-through.json` | the complement rule, the two reach mechanisms, the authored `falls_through_to` edges, eleven boundaries, and `00`'s worked cases |
| `RESEARCH.md` | grounding: the real-Mac leftover-pile inventory, depth and default-parent recommendations (`proposal`), the treatment forks, sourcing honesty |
| `check.py` | the gate |

## The join — adopted, not redefined

`falls_through_to` is CONNECTION.md's edge (§5), adopted here without a competing definition:
schema or template → one of the nine `00` residual names, spelled `00`'s way; residuals are
never roster nodes, never carry a schema, never activate, and never appear as an edge source —
terminal by construction (invariant 5). Residual is the complement of reliable domain
association (CONNECTION.md §7), reached by `falls_through_to` or by the empty activation set.

The complement rule, stated once: **when a domain association is reliable, residual must not
claim the file** — “If the LLM finds a credible connection to an accepted project, course,
application, photo event, or career group, the file should be returned to the standard
node-aware placement engine rather than being trapped in a generic residual folder.” And when
nothing is reliable, the honest terminal outcomes stay legal: “the correct result is leave in
place, Review Later, or abstain”.

Protected Records is the one home whose slots are load-bearing for privacy: its evidence
patterns are deterministic-only (membership never requires a model prompt, so no residual
dossier exists to leak), its subfolders are empty (no content-derived names in any path P12
composes), its surfacing is count-only, and its `sensitivity_restrictions` carry `00`'s
constraint verbatim — “must not cause filenames or content to be exposed in model prompts”.
`check.py` asserts each of these mechanically.

## NEEDS-JOSEPH

Open questions this catalogue surfaces. None is closed here; where a value was needed to make
the library usable, it is recorded with `provenance: proposal` so P10 is not blocked, and the
question stays open.

- **NJ-R3-1 · The five blank default parents.** `00` states default parent locations for four
  templates only (Photos/ for the two image homes, Personal/ for Reference Clips and
  Independent Records). Proposed, all `proposal`: `Personal/<display name>` for Receipts and
  Confirmations, Reading Inbox, Review Later, Unsupported or Encrypted, and Protected
  Records, following `00`'s own images-under-Photos / documents-under-Personal pattern. `00`'s
  alternatives (`Desktop/Inbox` for unclear downloads, `Travel/Confirmations` for tickets,
  mapping Review Later onto an existing `To Sort` folder) are user freedom the enablement
  model already provides, not defaults. Joseph picks or renames.
- **NJ-R3-2 · Reference Clips' optional kind subfolders.** Six optional shallow subfolders are
  proposed (Recipes, Products, Quotes, Inspiration, Articles, Code Snippets) — the names are
  `00`'s own enumeration of what the template holds, offered as one flat clip-kind level.
  Ship or drop; dropping costs nothing structural. The other eight homes ship none, each with
  a recorded `why_empty`.
- **NJ-R3-3 · Receipts and Confirmations `treatment`.** Recorded as `reviewed` (`inference`):
  much of the class expires — `00`'s lifecycle example is “surface travel confirmations after
  their date has passed”. The `retained` reading (purchase receipts and invoices are durable
  records) is also real. Fork open.
- **NJ-R3-4 · Unsupported or Encrypted `treatment`.** Recorded as `retained` (`proposal`):
  nothing is readable, so neither content review nor content search is possible — what `00`
  requires is keeping the record and never forcing anything open. The `reviewed` reading
  (`00`'s set-level question offers “review them manually?”) is a user action on the set, not
  necessarily a treatment of the home. Fork open.
- **NJ-R3-5 · Who authors `falls_through_to` for a shadowing user-defined home.**
  CONNECTION.md invariant 5 requires the edge when a residual home shadows a domain template
  (a residual `Travel` beside a travel template). Whether P13's collection flow writes it at
  creation time, or R1c/P10 reconciles it later, is open — `02-user-defined-shape.json`
  records the rule and leaves the author open.
- **Adopted open, not closed here:** CONNECTION.md **NJ-4** (where protected-record surfacing
  lands — P9 group, P7 surface, or P11 residual routing). PR-4's provisional rule is what
  `01` and `03` build on: the safety-activated file with no accepted deeper group is offered
  its `falls_through_to` home. Nothing in this catalogue depends on how NJ-4 closes.
