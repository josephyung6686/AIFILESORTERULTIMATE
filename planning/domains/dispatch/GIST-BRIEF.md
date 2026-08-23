# Industry gist swarm — standing brief

Every gist-swarm agent reads this file. Your dispatch message names only your row list and any
row-specific warnings; everything else is here.

## What you are doing

You own a chunk of sibling roster rows on one schema. You research them together — read the
authority stack ONCE, then write rows that agree with each other. This is the J-IND industry pass:
placeholder rows carrying honest gist-level coverage of the old 574 industries.

## Step 1 — read the authority stack (once)

- `planning/prompts/ALIGNMENT.md`
- `planning/00-database-agent-product-design.md` — the source of truth. Quote VERBATIM only; never
  paraphrase-as-quote.
- `planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `_CONTRACT.md` — binding contract
- `planning/domains/canonical_fields.json`
- `planning/overnight/council/DECISION-BRIEF.md` — D1–D6 and J-IND are RATIFIED. Do not re-debate them.
- `planning/domains/ROSTER.md` §4 + Appendix A — find which legacy ids each of your rows absorbed
  (also named in each row's `one_line_hint`). You own that absorbed coverage.

**Reference standard.** The landed `planning/domains/nodes/clinical_practice*` and
`business_operations*` files are the house standard for gist depth, JSON key set, and idiom. Match
them exactly. Read `business_operations.organisational-records.json` to see what a good refusal
looks like.

## Step 2 — per-row stamped assignment

For each id: `python3 planning/domains/dispatch/make_prompt.py <id>` and follow it.

## Depth: GIST

An honest, useful map of each row: what this filing world is FOR, what real files it actually holds,
what signals recognise it, what folder dimensions make sense. This is NOT the deep per-industry
research the 83 launch rows received — that comes much later. Label each memo `Depth: GIST`.
A shorter honest memo beats a padded speculative one. Never imitate depth you did not do.

## Hard constraints

- Write ONLY `planning/domains/nodes/<id>.json` and `<id>.research.md` for the ids you were
  assigned. Nothing else — no roster edits, no other agent's rows, no `src/`, no `check.py`.
  Other agents are working in parallel on adjacent chunks.
- These are `launch: "placeholder"` rows: `fields: []`. Write NO field rows unless the design docs
  already license the field. Do NOT mint canonical field keys — candidates go in `proposed_fields`
  with an argument, for R1c to adjudicate. Reuse an existing proposal rather than minting a variant.
- **`refuse_node: true` with an honest argued reason is a SUCCESS, not a failure.** Apply the node
  test from CONNECTION.md §2: a template row exists only when its detection signals, recommended
  dimensions, or privacy rules differ from its schema's default. A row whose only evidence is
  never-alone (an organisation name, a person's name, a document-type word) can never activate.
  When you refuse, route the coverage through `falls_through_to` residual templates with quotes.
  Inventing a node to save a legacy id is the 574's original mistake — do not repeat it.
- Quotations verbatim. Invent no thresholds, statistics, or file counts.
- Unresolved cross-domain boundaries become explicit NEEDS-JOSEPH / NJ-* items in the memo, stated
  reciprocally per CONNECTION.md — never a silent guess.

## Step 3 — self-verify before returning

Every JSON parses (`python3 -m json.tool`), key sets match the landed siblings, every memo is
substantive, every quote greps back out of its source verbatim, and you wrote nothing outside your
assigned files.

## Return

One or two sentences per row; what you changed in any salvaged draft; the full `proposed_fields`
list; all NEEDS-JOSEPH items; every refusal with its reason; and your self-verification results.
