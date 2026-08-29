# P1–P7 Live Assembly Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Assemble the shipped P1–P7 libraries into one fail-closed ingestion path without inventing unfinished domain, detector, threshold, prompt, or policy content.

**Architecture:** Keep `run_wave2` as the backward-compatible P1–P5 entry point. Add a strict assembled entry point that uses P5 public native/targeted-OCR operations, injected P6 resolution/verdict callables, and an injected P7 classification producer. It bundles only after the final classification state exists; P2 stage outputs remain replay-time records because P2 publishes no live run kind.

**Tech Stack:** Python 3.12, SQLite, pytest, Graphify.

---

### Task 1: Split P5 native extraction from targeted OCR

**Files:**
- Modify: `src/extractors/ocr_policy.py`
- Modify: `src/extractors/dispatch.py`
- Test: `tests/p5/test_p5_ocr.py`
- Test: `tests/p5/test_p5_reextraction.py`

- [ ] **Step 1: Write failing tests for the two public passes**

Add tests proving:

```python
native = extract_native(...)
assert native.results[0].run["analysis_tier"] == "native"
assert all(r.run["analysis_tier"] != "ocr" for r in native.results)  # text-bearing PDF

ocr = extract_targeted_ocr(...)
assert tuple(r.run["analysis_tier"] for r in ocr.results) == ("ocr",)
```

Also prove a scanned PDF with no text still receives direct OCR during the native
pass, an image keeps its existing P5-owned OCR decision, non-PDF targeted OCR returns
no result, and neither API evaluates a P6 verdict at the wrong time.

- [ ] **Step 2: Run the tests and confirm the missing public APIs fail**

Run: `python3.12 -m pytest -q tests/p5/test_p5_ocr.py tests/p5/test_p5_reextraction.py`

Expected: FAIL because `extract_native` and `extract_targeted_ocr` do not exist.

- [ ] **Step 3: Implement the minimal split**

Publish:

```python
def extract_native(*, file_row, decision, path, policy, readers, now,
                   context_window, transcription_authorized) -> Dispatched: ...

def extract_targeted_ocr(*, file_row, decision, path, policy, readers, now,
                         context_window) -> Dispatched: ...
```

Keep existing `extract(...)` as a compatibility composition of the same private
family dispatch. Do not duplicate router vocabulary in the orchestrator. Native PDF
logic performs direct OCR only when the text layer is absent; targeted OCR is a
separate PDF-only pass after P6.

- [ ] **Step 4: Verify focused and complete P5 tests**

Run: `python3.12 -m pytest -q tests/p5 tests/readers`

Expected: PASS (native reader tests require unsandboxed macOS access).

### Task 2: Publish P6's completed-pass targeted-OCR decision

**Files:**
- Modify: `src/facts/usable.py`
- Test: `tests/p6/test_p6_usable.py`

- [ ] **Step 1: Write a failing termination test**

The callable must return true only when the deterministic pass completed, facts are
not usable, and no recorded pass already contains the OCR tier:

```python
needed = targeted_ocr_needed_for(conn, usable_threshold=threshold)
assert needed(file_id, content_hash) is True
record_pass(conn, file_id=file_id, content_hash=content_hash,
            analysis_tiers=frozenset({"native", "ocr"}))
assert needed(file_id, content_hash) is False
```

An unrecorded pass must still raise `FactPassNotRun`.

- [ ] **Step 2: Run the test and confirm the API is missing**

Run: `python3.12 -m pytest -q tests/p6/test_p6_usable.py`

Expected: FAIL on the missing symbol.

- [ ] **Step 3: Implement by composing P6's existing authorities**

Implement `targeted_ocr_needed_for` using `no_usable_facts_for` and `passes_for`.
It must inspect no raw text and define no quality heuristic or threshold.

- [ ] **Step 4: Verify P6 usable/determinism tests**

Run: `python3.12 -m pytest -q tests/p6/test_p6_usable.py tests/p6/test_p6_deterministic.py`

Expected: PASS.

### Task 3: Add the strict assembled caller

**Files:**
- Modify: `src/orchestrator.py`
- Create: `tests/integration/test_p1_p7_live_assembly.py`

- [ ] **Step 1: Write the failing caller-level skeleton**

Define injected callables in the test:

```python
ResolveFacts = Callable[[sqlite3.Connection, str, str], ResolveResult]
TargetedOcrNeeded = Callable[[str, str], bool]
ClassifyFile = Callable[[sqlite3.Connection, str, str], ClassificationRecord | None]
```

Run one text-bearing PDF through the assembled entry point and assert the trace is:

```python
assert trace == ["native", "p6-native", "ocr", "p6-with-ocr", "p7"]
```

The fixture-supplied resolver/detector may be minimal but must use real P4/P6/P7
records. Do not import or edit domain/catalogue files.

- [ ] **Step 2: Add negative tests before implementation**

Prove:

- a missing P6 resolver or classifier cannot call the strict entry point;
- unclassified remains `None` and is never coerced to a safe class;
- a P6 `ContractViolation` propagates and creates no false file failure;
- targeted OCR runs at most once per file version;
- REUSE, dataless, and protected-container behavior stays unchanged;
- P6 and P7 still do not import one another.

- [ ] **Step 3: Run and observe the missing entry-point failure**

Run: `python3.12 -m pytest -q tests/integration/test_p1_p7_live_assembly.py`

Expected: FAIL because `run_p1_p7` does not exist.

- [ ] **Step 4: Implement `run_p1_p7` without policy ownership**

Add a required-keyword entry point that sequences:

```text
P3 scan
P5 filesystem + native extraction/direct OCR
P6 resolve every current file version
P5 targeted PDF OCR where P6 requests it
P6 re-resolve only versions that gained OCR evidence
P7 injected classification producer
P2 bundle after classification
```

Refactor shared roster, refusal, persistence, status-merge, and bundle code into
private helpers used by both callers. Do not add defaults for the P6 resolver,
targeted-OCR predicate, or P7 classifier. Preserve `run_wave2` behavior and signature.

- [ ] **Step 5: Verify the integration and old caller**

Run: `python3.12 -m pytest -q tests/integration/test_p1_p7_live_assembly.py tests/wave2`

Expected: PASS.

### Task 4: Carry P7 authority into the replay bundle

**Files:**
- Modify: `src/orchestrator.py`
- Modify: `tests/integration/test_p1_p7_live_assembly.py`
- Modify: `tests/test_p1_p7_seams.py`

- [ ] **Step 1: Write failing bundle assertions**

For a classified file, assert `bundle_file_entry.handling_class` equals the current
P7 classification and P1's mirrored `sensitivity_state` carries the same class. For
an unclassified file assert the bundle remains NULL.

- [ ] **Step 2: Run and observe the literal-None failure**

Run: `python3.12 -m pytest -q tests/integration/test_p1_p7_live_assembly.py tests/test_p1_p7_seams.py`

Expected: FAIL because the current bundle writer always passes `handling_class=None`.

- [ ] **Step 3: Pass an explicit per-file handling map to the shared bundler**

The assembled path supplies the P7-derived value; the compatibility path supplies
`None`. Never parse P1's projection to recreate P7 authority.

- [ ] **Step 4: Verify bundle replay remains filesystem-free**

Run: `python3.12 -m pytest -q tests/eval tests/integration/test_p1_p7_live_assembly.py`

Expected: PASS.

### Task 5: Mission and no-invention guards

**Files:**
- Modify: `tests/integration/test_p1_p7_live_assembly.py`
- Modify: `planning/28-p1-p7-design-conformance-audit.md`

- [ ] **Step 1: Add AST/behavior guards**

Assert the assembled caller contains no domain names, regexes, thresholds, handling-
class derivation, model call, prompt, gazetteer, or detector rule. Assert P7 remains
the sole owner of classification writes and `Gate.release` remains the sole egress
door for later P8.

- [ ] **Step 2: Add replay adapter acceptance**

Build a P2 replay run from the assembled bundle and prove P5/P6 adapters—not the live
ingestion caller—produce the extraction and factual-validation stage envelopes.

- [ ] **Step 3: Update the audit verdict with evidence**

Mark only B1, B2, and B4 closed when their tests pass. B3 is “mechanism connected,
knowledge injection still required” until the concurrently authored detector/domain
catalogues are complete.

- [ ] **Step 4: Run final verification**

Run:

```bash
python3.12 -m compileall -q src tests
python3.12 -m pytest -q
graphify update .
graphify diagnose multigraph --json --max-examples 10
git diff --check
```

Expected: compilation exit 0, full suite zero failures, fresh graph produced, and no
whitespace errors. Native macOS reader tests must run outside the sandbox.
