# P1–P7 design-conformance audit

Date: 2026-08-25
Status: **REOPENED. The callback seam is assembled; production P1–P7 composition is
not yet proven. P8/P9 remain plans only.**

Sources of authority, in order:

1. `planning/00-database-agent-product-design.md`
2. Ratified decisions in the part specifications and `planning/02-segmentation-map.md`
3. Live source and executable tests

This audit does not edit the concurrent catalogue/domain lane named in
`planning/26-handoff.md` §4.

## 2026-08-25 adversarial re-audit correction

The earlier post-assembly conclusion was too broad. `run_p1_p7` had no source caller;
only integration tests invoked it, and those tests supplied fake P6/P7 callbacks.
Graphify's outbound call edges proved the orchestrator's internal order, not a
production composition root. The audit is therefore reopened until a real schema
bootstrap and composition exercise actual P6 records, P7 authority/P1 mirroring, and
P2 bundle output without inventing the unfinished domain and detector inputs.

The re-audit also found that P7's derived-data deletion surface deliberately refuses
all deletion pending the ratified P13-driven tombstone migration. That is an explicit
future product dependency, not completed P7 behavior, and prevents an unqualified
claim that all of §8.4 is implemented today.

## Verification evidence

- Full suite with native macOS framework access after assembly: **2697 passed**.
- Focused P5/P6/P7/Wave-2/live-assembly suite: **1762 passed**.
- Native reader integration: **24 passed**.
- `python3.12 -m compileall -q src tests`: exit 0.
- Fresh post-assembly `graphify update .`: 14,977 nodes, 27,043 edges, 889
  communities.
- `graphify diagnose multigraph`: zero missing endpoints, dangling endpoints,
  self-loops, duplicate edges, or collapsed same-endpoint edges.
- A separate forced `--code-only --no-cluster` extraction produced 5,930 nodes and
  17,195 raw edges. Its raw directed diagnostic reports 917 unresolved endpoints and
  161 same-endpoint relation variants that a simple directed graph would collapse.
  These are Graphify extraction/model limitations to account for when interpreting
  the curated post-build graph; they are not silently reported as application seams.

One test defect was found and corrected: P7's repo-wide materialiser guard required
three optional reader modules to be unimportable. That made installing the documented
`readers` extra fail the suite. The guard now permits those three modules to be either
importable or absent while still rejecting every unexpected import failure.

## What conforms now

- P1 keeps identity separate from path, preserves append-only provenance, and owns the
  `files.sensitivity_state` projection writer.
- P2 can create, seal, replay, compare, and assert a filesystem-free bundle.
- P3 owns corpus selection, exclusions, stat/cache verdicts, and dataless detection.
- P4's immutable observation/run/text-unit shapes and citation handles are the shared
  evidence boundary.
- P5 routes and extracts into P4's shape, preserves raw text separately, and handles
  unsupported, dataless, protected-container, OCR, and failure outcomes distinctly.
- P6 consumes P4 observations without format branching, preserves evidence links,
  records abstention explicitly, keeps history, and refuses invented fields/rules.
- P7 owns classification authority, mirrors only file facts into P1, uses one egress
  gate, defaults unknown files to denial, preserves audit/history, and prevents a
  detector rerun from superseding a stronger user-confirmed classification.
- P6 and P7 do not import each other. Their shared reliability vocabulary comes from
  P4, avoiding a second authority.

## Closed release blockers: the live caller is now connected

### B1 — closed: live P1→P6 call path

The legacy `run_wave2` remains unchanged, but the additive
`src/orchestrator.py::run_p1_p7` invokes caller-supplied P6 passes after persisted
extraction. This keeps domain-specific resolver policy outside the orchestrator while
making the original design's `FACTS` step a live product path.

### B2 — closed: P6's targeted-OCR seam is sequenced after the first pass

P5 now publishes separate initial and targeted extraction calls. `run_p1_p7` persists
initial evidence, runs P6, and only then asks the persisted targeted-OCR predicate.
A second P6 pass occurs only when post-P6 targeted OCR adds observations. Direct OCR
is already part of the first pass, and a failed OCR run does not falsely trigger a
second pass. REUSE never guesses a historical native `ExtractionResult`.

### B3 — closed as an orchestration seam; detector content remains an injected input

`run_p1_p7` now calls an injected classification producer, routes its candidate through
P7 `assign`, and re-reads `ClassificationStore.current` so a weaker detector rerun
cannot displace stronger user authority. Candidate file/version identity is checked
before any write. The unfinished detector/domain catalogues remain outside this
change: absence returns no candidate and fails closed as `unreadable_unclassified`.

### B4 — closed: the P2 bundle carries P7's authoritative handling class

The legacy caller still writes `None` by contract. The new caller resolves the current
P7 record at bundle assembly and writes that class. Absence is represented by P7's
gate outcome `unreadable_unclassified`; it is not stored or mirrored as a file fact.

### Resolved audit correction — stage-output envelopes do not belong to the live caller

P5 publishes `extraction_stage_output`; P6 publishes `fact_stage_output`; P2 publishes
`record_stage_output`. Tests compose them through P2 replay adapters, while `run_wave2`
calls none of them.

That is correct. `record_stage_output` requires a P2 `run_manifest`, whose closed
`run_kind` vocabulary is `replay | shadow | adversarial`; a live scan is none of
those, and the orchestrator may not invent a fourth kind. P2's bundle captures the
replay inputs; its adapters emit stage outputs when that bundle is run. The assembly
must keep those adapters working and bundle the final P1–P7 inputs, not write replay
records during ingestion. Both P6 passes remain visible through P6/P4's append-only
records.

### B6 — resolved with call-level evidence, while retaining the diagnostic caveat

The post-assembly graph gives `run_p1_p7()` 36 direct connections, including extracted
call edges to `scan`, `extract_initial`, `extract_targeted_ocr`, P7 `assign`,
`resolve_class`, and `_assemble_bundle`, plus references to `ClassificationStore`.
P6 passes remain injected callables, so their authority is proven by integration tests
rather than a statically named edge.

The raw code-only graph also exposes 917 dangling endpoints and 161 relation-variant
endpoint pairs, while the curated undirected post-build graph reports zero. Graphify
therefore remains useful for locating candidate seams, but its post-build integrity
summary cannot be treated as proof of a runtime connection or proof that the raw
producer preserved every distinct relation.

## Intentional deferrals, not bugs to paper over

- Detection rules, thresholds, gazetteers, identifier transforms, and many numeric
  ceilings are manually authored inputs. Do not add defaults to make a skeleton green.
- P7 must precede P8, but the deterministic offline walking skeleton makes no model or
  external call, so zero gate releases on that path is correct.
- `unreadable_unclassified` is a release outcome, never a mirrored file fact.
- P6 and P7 staying independent is deliberate; orchestration belongs above them.

## Assembly result and remaining boundary

The caller-owned integration now:

1. run native extraction without consulting a not-yet-run P6 verdict;
2. run P6 deterministic resolution and retain its replayable inputs/history;
3. run targeted OCR only for completed P6 verdicts that need it;
4. re-run P6 against the new observation set and preserve both passes in P6 history;
5. run the injected P7 detector/classification producer and mirror the authoritative
   record through P1;
6. write the resulting handling class into the P2 bundle;
7. leaves `Gate.release` as the sole future egress door; P8 is not implemented;
8. preserve REUSE, dataless, protected-container, status-map merge, and append-only
   behavior already fixed in `run_wave2`.

Caller-level tests start at P3 input and prove initial P6, targeted OCR, second P6,
authoritative P7 assignment, and P2 handling-class bundling. They also cover direct
OCR, failed OCR, classifier identity refusal, targeted OCR at-most-once, conservative
REUSE, protected refusal, and the fail-closed unclassified outcome. P2 stage outputs
remain correctly owned by replay/shadow/adversarial runs rather than live ingestion.

The accurate release statement is: **P1–P7 is connected and verified for the injected
authorities that exist. Unfinished domains, catalogues, prompts, and P8/P9 runtime work
remain explicit prerequisites, not defaults hidden inside the caller.**
