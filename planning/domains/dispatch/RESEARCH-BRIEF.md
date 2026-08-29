# Industry research swarm — standing brief

Every industry-research agent reads this file. Your dispatch message names only your row list and any
row-specific warnings; everything else is here.

## What you are doing

You own one roster row, or a small set of tightly-related sibling rows. Research each to full depth. This is the J-IND industry pass:
placeholder rows carrying full-depth research coverage of the old 574 industries (J-DEPTH).

## Step 1 — read the authority stack (once)

- `planning/prompts/ALIGNMENT.md`
- `planning/00-database-agent-product-design.md` — the source of truth. Quote VERBATIM only; never
  paraphrase-as-quote.
- `planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `_CONTRACT.md` — binding contract
- `planning/domains/canonical_fields.json`
- `planning/overnight/council/DECISION-BRIEF.md` — D1–D6 and J-IND are RATIFIED. Do not re-debate them.
- `planning/domains/ROSTER.md` §4 + Appendix A — find which legacy ids each of your rows absorbed
  (also named in each row's `one_line_hint`). You own that absorbed coverage.

**Reference standard.** Match the landed *launch* rows for depth (see the Depth section). Use the
`clinical_practice*` / `business_operations*` files for JSON key set and idiom only — their depth is
below standard. Read `business_operations.organisational-records.json` for what a good refusal looks
like; refusal quality there is exemplary even though its depth is not.

## Step 2 — per-row stamped assignment

For each id: `python3 planning/domains/dispatch/make_prompt.py <id>` and follow it.

## Depth: FULL R1b DEPTH (ratified J-DEPTH, 2026-08-24)

**J-IND's gist clause is overruled. Do not write gist-level rows.** Every row you write must be
researched to the same depth as the 83 landed launch rows, and must be indistinguishable from one
when finished. The `Depth: GIST` label is retired — do not use it.

Calibrate against the real standard, not against the shallower rows:

- **Read a landed launch row before you write anything** — e.g.
  `planning/domains/nodes/finance.crypto-assets.research.md`,
  `medical.personal-health-records.research.md`, or `legal.practice-matter-file.research.md`.
  Those memos run ~13KB and that is the target, reached by having more to say, never by padding.
- The rows under `clinical_practice`, `business_operations`, and `construction_property` were
  written at the old gist depth. They are **debt, not exemplars.** Use them for JSON key set and
  house idiom only; do not imitate their depth.

What full depth actually requires, beyond a gist:

1. **Evidence, not assertion.** Every claim about what this world files traces to something — a
   quotation from the design docs, a named real document type, or an argued inference you mark as
   inference. No unsourced confidence.
2. **The node test argued in full**, all three legs, each with its own reasoning — not a verdict.
   Say what the schema's default template is and exactly how this row differs from it, or refuse.
3. **Files considered and rejected.** Name the tempting false positives and say why each is not
   this row's evidence. A row that only lists what it holds has not been researched.
4. **Reciprocal boundaries.** For every neighbour this row could steal from, state the boundary in
   both directions and name the same fixture bytes on both sides where they compete.
5. **The collision fixture.** Name at least one real file that looks like this row's evidence and
   is not, and say what discriminates it.
6. **Open questions surfaced, not smoothed.** Anything you cannot settle from the design docs is a
   NEEDS-JOSEPH item with the alternatives spelled out.

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
