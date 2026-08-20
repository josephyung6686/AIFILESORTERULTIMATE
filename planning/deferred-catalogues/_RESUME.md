# Resume state — deferred evidence catalogues

**STATUS: COMPLETE.** All seven catalogues, the README, the renderer and the check suite are on
disk and passing. Nothing is committed — Joseph reviews and commits. Delete this file after that.

Last updated 2026-08-20 22:0x by the `catalogues` agent.

## Done — 7 of 7, plus README

| File | rows | verified by |
|---|---|---|
| `01-tool-producer-strings` | 115 entries · 6 refused · 6 uncertain | `checks/check01.py` |
| `02-screen-resolutions` | 70 entries · 4 uncertain | `checks/check23.py` |
| `03-sensor-aspect-ratios` | 5 ratios · 12 anchors · 3 refused · 5 uncertain | `checks/check23.py` |
| `04-camera-filename-patterns` | 37 entries · 5 refused · 8 uncertain | `checks/check04.py` |
| `05-repository-markers` | 4 + 118 entries · 4 refused · 6 uncertain | `checks/check05.py` |
| `06-citation-identifier-patterns` | 22 entries · 7 refused · 7 uncertain | `checks/check06.py` |
| `07-archive-recognizable-markers` | 80 entries · 4 refused · 6 uncertain | `checks/check07.py` |

`./checks/run_all.sh` runs all six checkers plus `render.py --check` (the JSON→markdown no-drift
guard). It exits non-zero on any failure. Everything passes as of this writing.

## Concurrency incident — resolved, do not re-litigate

Two agents wrote this directory simultaneously around 21:48 after the lead read a sleep-failure
notification as a death. Resolution, already applied:

- **Catalogue 04.** The other agent's 13-entry `cfp-*` version overwrote the 35-entry `fnp-*`
  version and was committed in `69db62b`. The `fnp-*` version was re-authored, the `cfp-*` version
  is preserved at `checks/04-alternate-version.json`, and the live file is **v1.1 (37 entries)** —
  the superset plus `MOV_####`, Canon `1NN_####`, the bare-sequence refusal and two uncertain items
  taken from the other version, all credited in its `provenance_note`. Nothing was discarded.
- **`render.py`.** Both agents added columns; the other agent removed their two duplicates. Verified
  clean: 31 columns, no duplicate keys or headings.
- **The two versions converged independently** on refusing the generic DCF basename and on flagging
  the `filename_pattern` return-value contract. That agreement is recorded as evidence, not noise.
- **Nothing else was touched.** 01/02/03/05 were never overwritten.

## Settled decisions — carry forward, do not redesign

1. **`prefix` is not "starts-with".** Whole-value equality, or prefix + boundary character + a
   remainder containing a digit. Two rows opt out with `tail_required: "any"` and their own
   false-positive analysis.
2. **Arbitration between 02 and 03.** `dimension_signal` returns at most one name: catalogue 02
   (exact) first, then 03 (ratio, 0.5 % tolerance), else `None`. Reasoning is in both files.
3. **`4032x3024` is a catalogue-03 anchor, never a catalogue-02 row.** A check asserts it.
4. **`p3_exclusion_roots` is exactly §1.1's four**, every row `settled`, zero `proposed`. A check
   fails if a fifth appears. Every candidate is written up in `uncertain`/`refused` for Joseph.
5. **Pattern labels name naming conventions, never media types** — P5 may not conclude photo or
   screenshot, so catalogue 04 says "Apple/DCF camera-roll sequence", not "camera".
6. **Sourcing honesty.** Every citation carries `verification`. Only 8 of 44 pages were actually
   opened; the rest say `consulted`, not `retrieved`. Do not upgrade a tag without opening the page.

## Constraints still in force

- Create files **only** under `planning/deferred-catalogues/`. Read anything.
- Do not edit `src/`, `tests/`, or any existing planning doc. No pointer was added to
  `P5-extractors/PLAN.md` or `P6-facts-facets/SPEC.md`; none proved necessary.
- Edit the JSON, never the markdown. Catalogues 02, 05 and 07 come from builders in `checks/`.
- Nothing committed by any agent.
