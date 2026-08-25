# Deepening addendum — for rows that already exist at gist depth

Read this together with `RESEARCH-BRIEF.md`. It applies when your assignment says DEEPEN rather
than write: the row's two files already exist, written under the retired gist standard.

## What you are working with

The existing files are a **verified-but-shallow draft, not an untrusted one.** Their facts were
checked, their JSON key set is house-correct, and their arguments — where they made any — were
sound. What they lack is depth.

**Preserve what is right. Deepen the rest. Do not rewrite for the sake of rewriting**, and do not
discard a correct argument to replace it with your own phrasing of the same thing. If you disagree
with something the draft argued, say so explicitly and give the reason — do not silently reverse it.

## Your schema row is now a real anchor — use it

All three gist-era schema rows (`clinical_practice`, `business_operations`, `construction_property`)
have been deepened to J-DEPTH. **Read your schema row's `.research.md` first.** It now states the
family's default template explicitly, and your node test is measured against that. It may also state
a family-wide principle your row must apply — `business_operations`, for example, generalises the
never-alone principle for all 24 of its siblings.

## What the gist rows are missing, specifically

These are the sections a gist row skipped. Each is required now:

1. **The node test argued leg by leg**, with reasoning per leg, not a verdict. Name the schema's
   default template and say exactly how this row differs from it — or refuse.
2. **Files considered and rejected.** The tempting false positives, and why each is not this row's
   evidence. A row that only lists what it holds has not been researched.
3. **A collision fixture, in both directions.** A real file that would wrongly fire this row, and a
   real file that must not be lost *to* it. Name the same bytes both neighbours name where they
   compete.
4. **Reciprocal boundaries.** For every neighbour this row could steal from, state the boundary in
   both directions. Read the neighbour's own file first and do not contradict it; if you must
   diverge, say so explicitly and reciprocally.
5. **Evidence, not assertion.** Every claim traces to a verbatim design quote, a named real
   document type, or an inference you mark as inference.
6. **Open questions surfaced**, with alternatives and their costs, rather than smoothed over.
7. **A closing "what changed in this pass" section**, so the deepening is auditable.

## Depth calibration

Landed J-DEPTH rows run 19–46KB, and the deepened schema anchors run 40–46KB. Depth comes from
having more to say — more neighbours argued with, more false positives named, more of the test
actually reasoned through. **Never from padding.** A row with genuinely less to say is allowed to
be shorter; say so plainly rather than inflating it.

## Refusal is still a success

Deepening sometimes reveals that a row should never have stood. If the full node test fails, set
`refuse_node: true`, argue it, and route coverage through `falls_through_to`. Reversing a gist row's
"stands" verdict on good evidence is a **correct** outcome, not a failure — say clearly that you are
reversing it and why.
