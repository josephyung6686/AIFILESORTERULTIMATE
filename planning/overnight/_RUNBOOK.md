# Overnight run — 2026-08-21

Joseph asleep. Nothing blocks on him. Everything needing his decision lands in
`NEEDS-JOSEPH.md` for morning review.

## Phases
- [x] A  Collect part-audits, fix findings, retest — **1237 passing**
- [x] B  P6–P7 task skeletons (P6: 26 tasks · P7: 22 tasks)
- [~] C  5 review rounds, fresh context each — round 1 running
- [x] D  P1–P5 connection verified; P1–P7 contract authored (`22-...`)
- [~] E  Decisions accumulating in `NEEDS-JOSEPH.md`
- [~] F  Domain map — 8 of 13 catalogues, 324 entries, gate clean

## Fixed this run
- Three values the caller computed and dropped: sensitivity signals, routing
  decisions, and `handling_class` fed from P1's `sensitivity_state`.
- A published emit order that was uuid4 order, with a live consumer indexing
  into it — §2.9's sensitivity signal landed on the wrong value.
- An unrouted run whose observations carried the indexer's extractor name.
- P6's absent verdict, faked as `False`, now named.
- An unused import; the test fixture that created four parts' tables out of five.

## Known open
- 155 dangling `collides_with` ids across catalogues — reconciliation pass owed
  once all thirteen land.
- `no_usable_facts` ordering: the caller must split into four passes when P6
  lands. Shape is specified; the code is not written.
- `files.sensitivity_state` still has no writer, by design, pending C8.

## Rule
No claim without executed evidence. "Tests pass" is evidence about shape, not
about intent — three of tonight's worst defects passed every unit test.
