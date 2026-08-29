# P1–P9 Seam Repair Plan

**Date:** 2026-08-27

**Status:** Repair work discovered by the 15-part live-code audit of 2026-08-27. This plan repairs
defects that exist in shipped `src/` today. It authors no prompts, no domain rules, no P10 templates,
no P11 placements and no P13 consent handling. It is a plan only — **nothing here has been applied**.

**Authority:** `planning/00-database-agent-product-design.md` → the part `SPEC.md` files →
`planning/30-p8-p9-connection-contract.md` → live unchanged-meaning P1–P9 APIs.

**Baseline verified at authoring time:** `PYTHONPATH=src python3 -m pytest -q` → **3621 passed in
74.85s**. `src/` and `tests/` are byte-identical to `HEAD` (`git diff --stat HEAD -- src/ tests/` is
empty). Python 3.12.4.

---

## Why this plan exists

The suite is green and the product cannot run. Eight defects sit in seams that are currently proved
only against hand-built substitutes: every one of them is invisible to a test that constructs the
record the seam was supposed to produce.

| # | Severity | Part | One sentence |
|---|---|---|---|
| 1 | BLOCKER | P3 | `SessionWatch` walks into `.app` bundles, stats their contents, and writes interior paths into the append-only `events` log. |
| 2 | BLOCKER | P7 | The gate redacts a value and then releases the raw text on either side of it. |
| 3 | BLOCKER | P8+P9 | `pipeline.py` calls `run_call` with two arguments; the live signature requires five more. `TypeError` on the first real call. |
| 4 | HIGH | P8 | Claim-level verdict selection still returns the last verdict by position, so a rejected first claim can return `accept_direct`. |
| 5 | HIGH | P6 | `proposal_eligible` returns superseded conclusions; the §2.2 tool-metadata survivor set is computed and discarded. |
| 6 | HIGH | P9 | `meets_support_bar` has no production caller, so `Group.state` can never become `supported`. |
| 7 | MEDIUM | P5 | D10's collapse renumbers observations after `long_tail` recorded positional indices into them. |
| 8 | MEDIUM | P7 | The single-egress guard asserts against an empty set and **fails** the real transport when pointed at it. |

---

## Verification log — corrections to the audit brief

Every line number and quotation in the commissioning brief was re-checked against live code before
being written into this plan. The following citations were **stale and are corrected here**:

| Brief said | Live code says |
|---|---|
| `notify()` writes `old_path=str(path), new_path=str(path)` at "~104–119" | `src/scan_agent/watch.py:112`, inside the `append_event` call spanning `108–119`. |
| SPEC line 47 carries "the container's own path and nothing derived from inside it" | `planning/parts/P3-scan-corpus-selection/SPEC.md:46–47` — the sentence spans both lines. Line 39 is correct as given. |
| `gate.py:475-485` | `src/privacy/gate.py:475–486`. The raw `context_before` / `context_after` are at **`483–484`**. |
| SPEC:248 says `materialised_items[] post-redaction values only` | Correct, but it is **P7's** SPEC (`planning/parts/P7-privacy-consent-gate/SPEC.md:248`), not P8's. P7's SPEC contains "context" **zero** times — confirmed by `grep -c`. |
| `values_with_counts` is "twelve lines below" `proposal_eligible` | `proposal_eligible` is at `read_surface.py:143`, `values_with_counts` at `:166` — 23 lines. Its supersede filter is the SQL at `:195` (`WHERE active = 1 AND superseded_by IS NULL`). The substance is unchanged. |
| "Every P9 test injects a two-argument spy" | **Wrong, and it changes the design.** Eight of ten P9 pipeline tests pass `p8_run_call=None`. The only two callables injected are `tests/p9/test_p9_pipeline.py:272` (`lambda *a, **k`) and `:410` (`def spy(conn, request, **kwargs)`) — **both already absorb keyword arguments**. Adding the five keywords at the call site therefore breaks **no existing test**. See Task 5. |
| `run_call` takes `SiteDependencies` as `validation_dependencies` (contract line 74) | **Contract is stale.** Live `validation_dependencies` is `llm_harness.harness.CallDependencies` — a 17-field frozen record with no defaults, which *contains* `site_dependencies: SiteDependencies \| None`. This changes the answer to "how does P9 get the deps". See Task 5. |

Citations confirmed exactly as briefed: `watch.py` has zero references to protection or exclusion;
`harness.py:348` / `:472`; `vocabulary.py:45`; `graph.py:262` and the comment at `:298`;
`sink.py:49`; `discount.py:113`; `resolver.py:174`; `transport_guard.py:27–28`;
`p8_seam.py:172` and `:336`; `pipeline.py:323`; `tests/p3/test_p3_watch.py:143`;
`tests/p7/test_p7_skeleton_step.py:405`; design §8.4 at `planning/00-database-agent-product-design.md:186`.

**Two additional defects found while verifying, both in the same seams:**

- **`conflicts=()` appears at six sites, not two.** `p8_seam.py:172` and `:336`, plus
  `pipeline.py:193`, `:223`, `:301`, plus `src/grouping/fixtures.py:177`. Task 5 covers all six.
  **The sixth is a different kind of site and must not be edited the same way** — see Task 5's
  "The sixth site" below: `fixtures.py:177` is the *course* dossier, and a course group with no
  conflicting course code is the design's own conflict-free example. The conflict-bearing shape is
  published beside it at `fixtures.py:270`, verified live:

  ```
  $ PYTHONPATH=src python3 -c "from grouping.fixtures import GOLDEN_DOSSIERS; ..."
  course_dossier_fixture           conflicts=[]
  application_dossier_fixture      conflicts=[('target_institution', ('Columbia', 'Duke'))]
  ```
- **`run["observation_count"]` is computed before D10's collapse in eight extractors**
  (`archive.py:186`, `docx.py:213`, `filesystem.py:109` and `:163`, `image.py:203`,
  `long_tail.py:311`, `ocr.py:191`, `pdf.py:178`, `structured_text.py:185`), so a run row can claim
  more observations than the batch contains, and `extractors/stage_output.py:73` copies that number
  into the P2 payload. Same root cause as defect 7; folded into Task 8.

---

## Non-negotiable boundaries

- **P7 remains the sole materializer and release authority.** No part substitutes raw P4 text for a
  released/redacted value, and no repair here relaxes that.
- **A protected container is never opened, never read, never moved.** There is no override
  (P3 SPEC:39–47, `11-ops-runtime.md` §4b). The repair adds a refusal; it removes none.
- **P9 does not call a model, does not call `Gate.release`, and does not validate citations**
  (`planning/30-p8-p9-connection-contract.md:19`). Task 5 gives P9 dependencies it *receives*; it
  never lets P9 construct one.
- **No invented thresholds, gazetteers, detectors or producer strings.** Every threshold in this
  plan is one that already exists and is already injected.
- **`§1.1`'s ordinary exclusions are not §4b.** `tests/p3/test_p3_watch.py:143` deliberately asserts
  the watch still observes a path the *scan* would prune (`node_modules`). That reading is defensible
  and Task 2 must not break it.

---

## Task order, and why

| Task | Repairs | Commit | Suite after |
|---|---|---|---|
| **1** | the live-path integration test | **held, not committed** | 3621 (file lives outside `testpaths`) |
| **2** | defect 1 (P3 watch) | `fix(p3): the watch never reads inside a protected container` | green |
| **3** | defect 4 (P8 verdict severity) | `fix(p8): one verdict per call, chosen by severity at both sites` | green |
| **4** | defect 2 (P7 context release) | `fix(p7): the gate releases no text outside the requested span` | green |
| **5** | defect 3 (P8+P9 wiring, conflicts) | `fix(p9): p9 supplies run_call's real dependencies and its own conflicts` | green |
| **6** | defect 5 (P6 supersede + survivors) | `fix(p6): proposals rest on live facts and screened observations` | green |
| **7** | defect 6 (P9 support bar) | `fix(p9): the support bar decides `supported`` | green |
| **8** | defect 7 (P5 D10 renumbering) | `fix(p5): a positional signal survives D10's collapse` | green |
| **9** | defect 8 (P7 egress guard) | `fix(p7): the egress guard runs over the real transport` | green |
| **10** | lands Task 1's test | `test(seams): one live path with no doubles` | 3621 + Task 1's tests |

Task 1 is written **first** because it is the specification of done for every other task, and
committed **last** because it is RED until Tasks 2–9 land. Tasks 2–9 are independent of one another:
each touches a different module and each leaves the suite green on its own.

**Branch discipline.** Other sessions commit to `build/p6-p7-first-packages`. Task 1's test file is
therefore authored at `docs/superpowers/plans/artifacts/p1_p9_live_path.py` — outside
`testpaths = ["tests"]` (`pyproject.toml`), so a bare `pytest` does not collect it and no other
session's run goes red. Task 10 `git mv`s it into `tests/integration/` only once it passes.

---

## Task 1: One live path, with no doubles

**This is the task that matters most.** Every defect above lives in a seam currently proved against a
hand-built substitute. This is the single test that would have caught defects **1, 3, 4 and 8**
simultaneously, and it is the acceptance criterion for Tasks 2–9.

> ### This test is RED until Tasks 2–9 land. That is correct TDD, not a regression.
> It fails at authoring time with `TypeError: run_call() missing 5 required keyword-only arguments`
> (defect 3) before it can reach its other assertions. **Do not commit it in a red state** — the
> branch is shared. It is authored at a path pytest does not collect and moved into `tests/` by
> Task 10.

**Files:**

- create `docs/superpowers/plans/artifacts/p1_p9_live_path.py` (moved to
  `tests/integration/test_p1_p9_live_path.py` by Task 10)
- create `src/production.py` additions: `P8P9Authorities`, `compose_p8_p9` (see Task 5 — the test
  consumes them; Task 5 builds them)
- read-only: `src/production.py`, `src/privacy/fixtures.py`, `src/llm_harness/harness.py`,
  `src/grouping/pipeline.py`

**Interfaces:**

```
Consumes: production.bootstrap_p1_p7(conn) -> None
          production.run_production_p1_p7(conn, selection_id, *, authorities: P1P7Authorities) -> P1P7Run
          production.compose_p8_p9(conn, *, authorities: P8P9Authorities)      # Task 5 builds this
              -> Callable[[str, str], grouping.pipeline.GroupingResult]
          privacy.gate.Gate(conn, **privacy.fixtures.gate_arguments(fixture, store=...))
          llm_harness.harness.run_call(conn, request, *, gate, model_client, prompt,
                                       validation_dependencies, observed_at)
          scan_agent.exclusion.is_protected_container(path, *, extra=None) -> bool
Produces: no runtime symbol. A test module.
```

**What "no doubles" means here, precisely.** The product *requires* injected authorities: P7 ships no
detector (`_PLAN-AUTHORING-BRIEF.md` §7: "The detector does not exist"), P5 ships no format readers
(`pyproject.toml` comment: "every format reader is a caller-supplied callable"), and P6's thresholds
are injected with no default. Supplying those is honouring the contract, not faking a seam.

- **Permitted** (contract-mandated injections): `classify`, `Readers`, `usable_threshold`,
  `mime_type_for`, `detect_format`, `now`, `context_window`, `scan_budget_exhausted`, and the
  source-shipped `privacy.fixtures._identifier_classifier` / `_redaction_transform` via
  `gate_arguments`, and one `ModelClient.invoke` that returns bytes (a real network call is not a
  test).
- **Forbidden** (the seams under test): any substitute for `run_call`, `Gate`, `Gate.release`,
  `build_dossier`, `dispatch`, `apply_p8_verdict`, `FactResolver.resolve`, `group_subject`; any
  hand-constructed `Dossier`, `Materialised`, `ReleasedEvidence`, `P8Verdict`, `Membership`,
  `Group`, `Observation` or `ExtractionResult`; any import from `grouping.fixtures`,
  `llm_harness.fixtures` or `evidence_shape.fixtures`.

**Fixture corpus** — built on disk under `tmp_path`, four files, chosen so each one loads a
different seam:

```
corpus/
  Syllabus.pdf                       # anchor: text-bearing, yields the P6 subject fact
  Lecture 08.pdf                     # second anchor: same subject, independent file
  Contacts.vcf                       # long-tail, two entries sharing one address  -> defect 7
  Numbers.app/Contents/sheet.numbers # protected container interior                -> defect 1
```

**Done-means** (each falsifiable by a named assertion):

1. **D1.1** — `exclusion_verdicts` contains exactly one row for `Numbers.app` with
   `rule = "protected container"` and `label = "untouched_protected"`, and **no** row, `files` row,
   `evidence` row or `events` row anywhere in the database mentions
   `Numbers.app/Contents` (defect 1).
2. **D1.2** — `group_subject` reaches `run_call` and returns a `GroupingResult` whose
   `model_result` is a `GroupDecision`; no `TypeError` is raised (defect 3).
3. **D1.3** — a Site-B response whose **first** claim cites a span the release does not contain and
   whose **second** claim is clean produces **no accepted membership** (defect 4).
4. **D1.4** — `privacy.transport_guard.assert_single_egress(llm_harness.transport)` returns `None`,
   and the module scan in `tests/p7/test_p7_skeleton_step.py` finds exactly one declared transport
   (defect 8).
5. **D1.5** — the canonical model-visible bytes contain the released span and **no other character**
   of its text unit (defect 2).
6. **D1.6** — `p9`'s `DossierRequest.conflicts` is non-empty when
   `knowledge.conflicts_for` returns a conflict, and Site B's `target_institution` check can fire
   (defect 3, second half).

**Steps:**

- [ ] **Step 1.1: Write the corpus builder.** A module-level `_corpus(tmp_path) -> Path` that
      creates the four files above with real bytes. `Numbers.app/Contents/sheet.numbers` must contain
      a distinctive marker string (`b"BUNDLE-INTERIOR-MUST-NOT-BE-READ"`) so D1.1 can grep the whole
      database for it rather than trusting a path comparison.

- [ ] **Step 1.2: Write the P1–P7 half.** Reuse the shape of
      `tests/integration/test_production_p1_p7.py:_readers` and `:_authorities`, with **one required
      change**: `policy=SafetyPolicy(is_protected_container=is_protected_container, is_dataless=...)`.
      The existing test passes `lambda path: False` there, which is why no live test has ever
      exercised the real predicate through the real pipeline.

```python
# docs/superpowers/plans/artifacts/p1_p9_live_path.py
"""One run of the real path, from a directory on disk to a P9 membership.

Nothing here is a double for a seam. Every authority supplied is one the product
requires a deployment to supply -- P7 ships no detector, P5 ships no readers, P6's
thresholds are injected with no default -- and every seam between them is live:
the real `Gate`, the real `run_call`, the real dispatcher, the real `p8_seam`, the
real `FactResolver`, the real `group_subject`.

This exists because eight defects shipped green. Each of them lives at a seam whose
only test builds the record the seam was supposed to produce, and a test that
constructs the answer cannot fail when the producer is wrong.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from privacy.transport_guard import assert_single_egress
from production import (
    P1P7Authorities,
    P8P9Authorities,
    bootstrap_p1_p7,
    compose_p8_p9,
    run_production_p1_p7,
)
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.selection import record_selection

CLOCK = "2026-08-27T12:00:00+00:00"
BUNDLE_MARKER = "BUNDLE-INTERIOR-MUST-NOT-BE-READ"


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    (root / "Numbers.app" / "Contents").mkdir(parents=True)
    (root / "Numbers.app" / "Contents" / "sheet.numbers").write_text(BUNDLE_MARKER)
    (root / "Syllabus.pdf").write_bytes(b"%PDF PHYS1401 Syllabus Spring 2026")
    (root / "Lecture 08.pdf").write_bytes(b"%PDF PHYS1401 Lecture 08")
    (root / "Contacts.vcf").write_text(
        "BEGIN:VCARD\nFN:A\nEMAIL:same@example.com\nEND:VCARD\n"
        "BEGIN:VCARD\nFN:B\nEMAIL:same@example.com\nEND:VCARD\n")
    return root
```

- [ ] **Step 1.3: Write the defect-1 assertion.** It reads the whole database, not one table: the
      harm defect 1 causes is a row in the append-only `events` log, and a test that checks only
      `files` would miss it.

```python
def _every_text_value(conn) -> list[str]:
    """Every TEXT cell in every table. The bundle marker must appear in none of them."""
    found: list[str] = []
    tables = [row["name"] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' "
        "AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        for row in conn.execute(f'SELECT * FROM "{table}"'):
            found.extend(str(value) for value in tuple(row) if isinstance(value, str))
    return found


def test_nothing_inside_a_protected_container_reaches_the_database(live_run):
    conn, corpus = live_run
    bundle = str(corpus / "Numbers.app")
    interior = str(corpus / "Numbers.app" / "Contents")

    verdicts = conn.execute(
        "SELECT * FROM exclusion_verdicts WHERE rule = 'protected container'"
    ).fetchall()
    assert [row["path"] for row in verdicts] == [bundle]
    assert verdicts[0]["label"] == "untouched_protected"

    values = _every_text_value(conn)
    assert not [v for v in values if interior in v], "an interior path was recorded"
    assert not [v for v in values if BUNDLE_MARKER in v], "interior CONTENT was recorded"
```

- [ ] **Step 1.4: Write the defect-1 assertion for the watch.** The scan and the watch are two
      different readers of the same corpus, and only the scan has ever been tested against §4b.

```python
def test_the_session_watch_reads_nothing_inside_a_protected_container(live_run):
    from scan_agent.watch import SessionWatch

    conn, corpus = live_run
    interior = corpus / "Numbers.app" / "Contents" / "sheet.numbers"

    statted: list[str] = []
    original = SessionWatch._stat

    watch = SessionWatch(conn)
    try:
        SessionWatch._stat = staticmethod(
            lambda path: statted.append(str(path)) or original(path))
        watch.open([corpus])
        interior.write_text(BUNDLE_MARKER + " changed")
        watch.poll()
        watch.notify(interior)
    finally:
        SessionWatch._stat = staticmethod(original)
        watch.close()

    assert not [p for p in statted if "Numbers.app" in p], statted
    rows = conn.execute(
        "SELECT * FROM events WHERE event_type = 'external modification detection'"
    ).fetchall()
    assert not [r for r in rows
                if "Numbers.app" in ((r["old_path"] or "") + (r["new_path"] or ""))]
```

- [ ] **Step 1.5: Write the defect-3 assertion.** The whole point: reach `run_call` for real.

```python
def test_the_group_pipeline_reaches_run_call_without_a_type_error(live_run_p9):
    result = live_run_p9.group("Syllabus")
    assert result.not_implemented_reason is None, result.not_implemented_reason
    assert result.dossier is not None
    assert result.model_result is not None
    assert result.model_result.membership_ids
```

- [ ] **Step 1.6: Write the defect-4 assertion.** Two claims, first rejected, second clean.

```python
def test_a_rejected_first_claim_is_not_overruled_by_a_clean_second(live_run_p9):
    """`vocabulary.py:45`: one verdict per call, "one per shard, one per claim".
    Only the shard half shipped, so the LAST claim's outcome was returned."""
    live_run_p9.respond_with_two_claims(
        first_cites="text the release does not contain",
        second_cites=live_run_p9.released_span())
    result = live_run_p9.group("Syllabus")
    assert result.model_result.membership_ids == ()
```

- [ ] **Step 1.7: Write the defect-8 assertion.** One line, and it is the one nobody could write
      while `IS_MODEL_TRANSPORT` was `False` everywhere.

```python
def test_the_real_transport_satisfies_the_single_egress_guard():
    import llm_harness.transport as transport
    assert transport.IS_MODEL_TRANSPORT is True
    assert assert_single_egress(transport) is None
```

- [ ] **Step 1.8: Write the defect-2 assertion.** Against the canonical model-visible bytes, which
      is the only artefact that answers "what did the model see".

```python
def test_the_model_saw_the_released_span_and_no_other_character_of_its_unit(live_run_p9):
    seen = live_run_p9.model_visible_bytes()
    span, unit = live_run_p9.released_span(), live_run_p9.text_unit()
    assert span.encode() in seen
    for fragment in (unit[:unit.index(span)], unit[unit.index(span) + len(span):]):
        if fragment.strip():
            assert fragment.encode() not in seen, f"released context: {fragment!r}"
```

- [ ] **Step 1.9: Write the defect-3-second-half assertion.**

```python
def test_the_builders_conflicts_reach_site_b(live_run_p9):
    """`planning/30-p8-p9-connection-contract.md:60-61`: the field exists BECAUSE
    P8 hardcoded `()` and Site B's `target_institution` check could never fire."""
    live_run_p9.with_conflict(kind="target_institution", values=("Columbia", "Duke"))
    request = live_run_p9.captured_dossier_request()
    assert [c.kind for c in request.conflicts] == ["target_institution"]
```

- [ ] **Step 1.10: Run it and state the expected failure.**
      `PYTHONPATH=src python3 -m pytest docs/superpowers/plans/artifacts/p1_p9_live_path.py -q`
      **Expected: collection error** — `ImportError: cannot import name 'P8P9Authorities' from
      'production'`, because Task 5 has not built it. After Task 5, expected: **9 failed** on the
      remaining assertions, resolving one at a time as Tasks 2, 3, 4, 8 and 9 land.

- [ ] **Step 1.11: Do not commit.** Leave the file untracked. Confirm with
      `git status --short docs/superpowers/plans/artifacts/` and confirm a bare
      `PYTHONPATH=src python3 -m pytest -q` still reports **3621 passed** — the file is outside
      `testpaths`.

**The guard, and how to sabotage it.** Task 1's file *is* the guard for every other task. To prove it
is not silent: after Task 10, revert any single one of Tasks 2–9 (`git revert --no-commit <sha>`) and
re-run; exactly the assertion named in that task's Done-means must fail, and the rest must still
pass. A revert that leaves the file green means that task's assertion is decoration and must be
rewritten before the branch merges.

---

## Task 2: The session watch never reads inside a protected container

**Files:**

- modify `src/scan_agent/watch.py`
- modify `tests/p3/test_p3_watch.py` (append; change nothing existing)

**Interfaces:**

```
Consumes: scan_agent.exclusion.is_protected_container(path, *, extra=None) -> bool
Produces: SessionWatch.__init__(conn: sqlite3.Connection, *,
                                is_protected: Callable[[PurePath], bool] | None = None)
          (open / poll / notify / close signatures unchanged)
```

**Why `is_protected` gets a `None` default when this project forbids defaults.** It is not a
threshold. `is_protected_container(path, *, extra=None)` already publishes `None` as its own default
and documents that `extra` "can only ADD: a caller cannot un-protect a `.app`"
(`exclusion.py:79–81`). `.app` is enforced unconditionally either way. Adding a required parameter
would instead break the eight existing `SessionWatch(scanned)` constructions for no gain in safety.

**Done-means:**

- **D2.1** — `open` records no stat for any path inside a `.app` bundle, and skips a watched root
  that is itself inside one.
- **D2.2** — `poll` produces no detection for a change inside a bundle.
- **D2.3** — `notify`, called directly with an interior path (the entry point an FSEvents adapter
  uses), appends **zero** `events` rows.
- **D2.4** — `tests/p3/test_p3_watch.py:143` still passes unchanged: a `node_modules` path still
  authors a detection.

**Steps:**

- [ ] **Step 2.1: Write the failing tests.** Append to `tests/p3/test_p3_watch.py`.

```python
def test_the_watch_does_not_stat_inside_a_protected_container(scanned, corpus: Path,
                                                              monkeypatch):
    # P3 SPEC:39 -- P3 "does not descend into one, does not stat its contents". The
    # `_stat` recorder is the instrument because `_stat` is the ONLY place this
    # module stats, so "did not stat" is exactly "did not call this".
    interior = corpus / "Numbers.app" / "Contents" / "sheet.numbers"
    interior.parent.mkdir(parents=True)
    interior.write_bytes(b"private")

    seen: list[str] = []
    original = SessionWatch._stat
    monkeypatch.setattr(
        SessionWatch, "_stat",
        staticmethod(lambda path: seen.append(str(path)) or original(path)))

    watch = SessionWatch(scanned)
    watch.open([corpus])
    assert not [p for p in seen if "Numbers.app" in p], seen
    watch.close()


def test_a_change_inside_a_protected_container_authors_no_detection(scanned,
                                                                    corpus: Path):
    interior = corpus / "Numbers.app" / "Contents" / "sheet.numbers"
    interior.parent.mkdir(parents=True)
    interior.write_bytes(b"private")

    watch = SessionWatch(scanned)
    watch.open([corpus])
    interior.write_bytes(b"private, and longer")
    watch.poll()
    assert _detections(scanned) == []
    watch.close()


def test_notify_refuses_an_interior_path_a_platform_adapter_hands_it(scanned,
                                                                     corpus: Path):
    # SPEC:46-47 -- the verdict carries "the container's own path and nothing
    # derived from inside it". `events` is append-only, so a row written here is
    # unrecoverable. `notify` needs its own guard because a real FSEvents adapter
    # calls it directly and never goes through `open` or `poll`.
    interior = corpus / "Numbers.app" / "Contents" / "sheet.numbers"
    interior.parent.mkdir(parents=True)
    interior.write_bytes(b"private")

    watch = SessionWatch(scanned)
    watch.open([corpus])
    watch.notify(interior)
    assert _detections(scanned) == []
    watch.close()


def test_a_watched_root_inside_a_protected_container_is_skipped_whole(scanned,
                                                                      corpus: Path):
    inner = corpus / "Numbers.app" / "Contents"
    inner.mkdir(parents=True)
    (inner / "sheet.numbers").write_bytes(b"private")

    watch = SessionWatch(scanned)
    watch.open([inner])          # the user selected a path inside a bundle
    (inner / "sheet.numbers").write_bytes(b"private, and longer")
    watch.poll()
    assert _detections(scanned) == []
    watch.close()


def test_the_caller_can_add_protected_members_but_cannot_remove_one(scanned,
                                                                    corpus: Path):
    # `exclusion.is_protected_container` documents `extra` as ADD-only. The watch
    # must not become the override §4b says does not exist.
    (corpus / "Vault").mkdir()
    (corpus / "Vault" / "secret.txt").write_bytes(b"x")
    (corpus / "Numbers.app").mkdir()
    (corpus / "Numbers.app" / "inside.txt").write_bytes(b"y")

    watch = SessionWatch(scanned, is_protected=lambda path: path.name == "Vault")
    watch.open([corpus])
    (corpus / "Vault" / "secret.txt").write_bytes(b"xx")
    (corpus / "Numbers.app" / "inside.txt").write_bytes(b"yy")
    watch.poll()
    assert _detections(scanned) == []
    watch.close()

    unprotecting = SessionWatch(scanned, is_protected=lambda path: False)
    unprotecting.open([corpus])
    (corpus / "Numbers.app" / "inside.txt").write_bytes(b"yyy")
    unprotecting.poll()
    assert _detections(scanned) == []      # `.app` is not switchable off
    unprotecting.close()
```

- [ ] **Step 2.2: Run them and state the failure.**
      `PYTHONPATH=src python3 -m pytest tests/p3/test_p3_watch.py -q`
      **Expected: 5 failed** — the first with a non-empty `seen`, the next three with one detection
      row each, the last with `TypeError: SessionWatch.__init__() got an unexpected keyword
      argument 'is_protected'`.

- [ ] **Step 2.3: Add the import and the constructor keyword.**

```python
from scan_agent.exclusion import is_protected_container
```

```python
    def __init__(self, conn: sqlite3.Connection, *, is_protected=None):
        self._conn = conn
        # `11-ops-runtime.md` §4b / P3 SPEC:39. `extra` can only ADD members: a
        # predicate that returned False for a `.app` would be the override §4b says
        # does not exist, and `is_protected_container` checks the suffix first.
        self._is_protected = is_protected
        self._roots: tuple[Path, ...] = ()
        self._observed: dict[str, tuple[int, float] | None] = {}
        self._open = False

    def _protected(self, path) -> bool:
        return is_protected_container(path, extra=self._is_protected)
```

- [ ] **Step 2.4: Prune the walk in `open` and `poll`.** `os.walk`'s `dirnames` is mutable
      in-place and that is the only way to stop a descent before it happens; filtering after the
      walk has already paid the stat the rule forbids.

```python
    def open(self, roots) -> None:
        """Begin watching the selected roots and record their current stat."""
        self._roots = tuple(Path(root) for root in roots)
        self._observed = {}
        for root in self._roots:
            if self._protected(root):
                continue
            for current, dirnames, names in self._walk(root):
                for name in names:
                    path = Path(current) / name
                    self._observed[str(path)] = self._stat(path)
        self._open = True
```

```python
    def poll(self) -> None:
        """Re-stat the watched paths and notify each difference.

        The stdlib driver. A platform adapter (FSEvents / DispatchSource) calls
        `notify` directly instead, and is not built here.
        """
        if not self._open:
            return
        known = set(self._observed)
        live: set[str] = set()
        for root in self._roots:
            if self._protected(root):
                continue
            for current, _dirnames, names in self._walk(root):
                for name in names:
                    live.add(str(Path(current) / name))
        for path in sorted(known | live):
            self.notify(Path(path))

    def _walk(self, root: Path):
        """`os.walk`, pruned at every protected container before it is entered.

        The prune is an in-place assignment to `dirnames` because that is the only
        thing `os.walk` reads back. Filtering the result instead would have already
        descended, and descending IS the read §4b forbids -- P3 "does not descend
        into one, does not stat its contents" (P3 SPEC:39).
        """
        for current, dirnames, names in os.walk(root):
            dirnames[:] = [name for name in dirnames
                           if not self._protected(Path(current) / name)]
            yield current, dirnames, names
```

- [ ] **Step 2.5: Guard `notify`.** Placed **first**, before the roots check and before `_stat`,
      mirroring `exclusion_for`'s "FIRST, and before every other rule" (`exclusion.py:127`) and
      `extractors.safety.admit`'s ordering.

```python
    def notify(self, path) -> None:
        """One watched path may have changed. Authors the detection when it did.

        A detection is NOT a rescan (11 §4): this re-stats the one path, writes no
        `files` row, and starts no scan run.
        """
        if not self._open:
            return
        path = Path(path)
        # FIRST, and before the roots test and before the stat below. A platform
        # adapter calls `notify` directly, so `open`'s prune does not protect this
        # entry point. The stat IS the read §4b forbids, and `append_event` would
        # then write an interior path into the append-only `events` log, where it
        # cannot be removed. SPEC:46-47: the record carries "the container's own
        # path and nothing derived from inside it".
        if self._protected(path):
            return
        if not any(path == root or root in path.parents for root in self._roots):
            return
        ...  # unchanged from here
```

- [ ] **Step 2.6: Run the whole P3 suite.**
      `PYTHONPATH=src python3 -m pytest tests/p3 -q` → **expected: all pass**, including
      `test_the_watch_observes_a_path_the_scan_would_have_excluded` (D2.4).

- [ ] **Step 2.7: Run the full suite.** `PYTHONPATH=src python3 -m pytest -q` → expected
      **3626 passed** (3621 + 5 new).

- [ ] **Step 2.8: Commit.**
      `git commit -m "fix(p3): the watch never reads inside a protected container"`

**The guard: `test_the_watch_does_not_stat_inside_a_protected_container`.**
**Sabotage recipe:** delete the `if self._protected(root): continue` line in `open` — the test must
fail with a non-empty `seen`. Then restore it and delete only the `dirnames[:]` assignment in
`_walk` — the test must still fail. Then restore that and delete only the `notify` guard — the
third test must fail. Three independent lines, three independent failures: if any deletion leaves
the suite green, that line is unguarded.

---

## Task 3: One verdict per call, chosen by severity at both sites

**Files:**

- modify `src/llm_harness/harness.py`
- modify `tests/p8/test_p8_validation.py` (append)

**Interfaces:**

```
Consumes: llm_harness.vocabulary.OUTCOME_SEVERITY: tuple[str, ...]   (already imported, harness.py:54)
Produces: llm_harness.harness.worst_outcome(verdicts: Sequence[P8Verdict]) -> P8Verdict
```

**The defect, verified.** `harness.py:472` reduces many shard verdicts with
`min(produced, key=lambda v: OUTCOME_SEVERITY.index(v.outcome))` and the comment *"chosen by
severity and not by position"*. `harness.py:348` reduces many **claim** verdicts with
`return verdicts[-1]`. `vocabulary.py:44–49` states the rule once, for both:

> `run_call` returns ONE verdict for a call that may have produced several — **one per shard, one
> per claim** — and `emit_stage_output` maps that one result onto one P2 envelope. Returning the LAST
> one reported by position: a call whose first shard was rejected and whose second was accepted read
> `accept_direct`, and the P2 row read `produced`.

Only the shard half shipped. Downstream, `grouping/p8_seam.py:285` reads
`accepting = result.outcome in (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED)` and writes a `Membership`
— so a two-claim Site A response whose first claim quotes unreleased text becomes an accepted
membership.

**Done-means:**

- **D3.1** — the rule exists in exactly one place and both reducers call it.
- **D3.2** — a two-claim response `(reject, accept_direct)` returns `reject`.
- **D3.3** — a two-shard response `(reject, accept_direct)` still returns `reject` (no regression).
- **D3.4** — order-independence: `(accept_direct, reject)` and `(reject, accept_direct)` return the
  same outcome.

**Steps:**

- [ ] **Step 3.1: Write the failing tests.**

```python
def test_the_worst_outcome_is_returned_whatever_its_position():
    # `vocabulary.py:45`: "one per shard, one per claim". Only the shard half
    # shipped -- `harness.py:348` returned `verdicts[-1]`, so a two-claim Site A
    # response whose FIRST claim quoted unreleased text read `accept_direct`, and
    # `grouping.p8_seam.apply_p8_verdict` turned that into an accepted membership.
    from llm_harness.harness import worst_outcome
    from llm_harness.vocabulary import ACCEPT_DIRECT, REJECT, WEAK

    def verdict(outcome):
        return _p8_verdict(outcome=outcome)      # the module's existing helper

    for order in ((REJECT, ACCEPT_DIRECT), (ACCEPT_DIRECT, REJECT)):
        assert worst_outcome([verdict(o) for o in order]).outcome == REJECT
    assert worst_outcome(
        [verdict(ACCEPT_DIRECT), verdict(WEAK)]).outcome == WEAK


def test_a_rejected_first_claim_is_the_calls_verdict(validation_conn, two_claim_dossier):
    """The claim-level path, end to end through `dispatch` and `_validate_and_record`."""
    result = _run_two_claims(validation_conn, two_claim_dossier,
                             first="cites text no release contains",
                             second=two_claim_dossier.released_evidence[0].value)
    assert result.outcome == "reject"


def test_both_reducers_use_the_one_rule():
    """A rule written twice is a rule that can ship half-applied -- it did. This
    asserts the source has one reducer, so a third caller cannot re-introduce the
    positional form without failing here."""
    import inspect
    import llm_harness.harness as harness

    source = inspect.getsource(harness)
    assert source.count("OUTCOME_SEVERITY.index") == 1
    assert "verdicts[-1]" not in source
    assert "produced[-1]" not in source
```

- [ ] **Step 3.2: Run and state the failure.**
      `PYTHONPATH=src python3 -m pytest tests/p8/test_p8_validation.py -q`
      **Expected: 3 failed** — `ImportError: cannot import name 'worst_outcome'`; the claim test
      asserting `'accept_direct' == 'reject'`; the source test failing on `verdicts[-1]`.

- [ ] **Step 3.3: Add the one rule.** Place it directly above `_validate_and_record`.

```python
def worst_outcome(verdicts: Sequence[P8Verdict]) -> P8Verdict:
    """The single verdict a call returns when it produced several.

    `vocabulary.OUTCOME_SEVERITY` states the rule as "one per shard, one per claim"
    and both halves are reduced here, by ONE function. They were two expressions --
    the shard reducer used severity and the claim reducer used `verdicts[-1]` -- and
    the fix that landed the first never reached the second. A caller told
    `accept_direct` must be able to take it as true of the whole call.
    """
    return min(verdicts, key=lambda verdict: OUTCOME_SEVERITY.index(verdict.outcome))
```

- [ ] **Step 3.4: Call it at both sites.** `harness.py:348`:

```python
    if not verdicts:
        return ValidationUnavailable(missing=("claims",))
    return worst_outcome(verdicts)
```

`harness.py:472`:

```python
    if not produced:
        return ValidationUnavailable(missing=("fitting_shard",))
    # One call, one returned verdict, chosen by severity and not by position.
    return worst_outcome(produced)
```

- [ ] **Step 3.5: Re-run.** `PYTHONPATH=src python3 -m pytest tests/p8 tests/integration -q` →
      expected all pass.

- [ ] **Step 3.6: Full suite.** `PYTHONPATH=src python3 -m pytest -q` → expected **3629 passed**.

- [ ] **Step 3.7: Commit.**
      `git commit -m "fix(p8): one verdict per call, chosen by severity at both sites"`

**The guard: `test_both_reducers_use_the_one_rule` plus the two behavioural tests.**
**Sabotage recipe:** change `worst_outcome`'s `min` to `max` — both behavioural tests must fail
(`accept_direct != reject`). Then restore and change one call site back to `verdicts[-1]` — the
source test must fail *and* the claim test must fail. A source test alone would be silent against
`max`; a behavioural test alone would be silent against a third reducer added later. Both are needed
and both must be shown to fire.

---

## Task 4: The gate releases no text outside the requested span

> ### OPEN — owner decides. Two options are presented; one is recommended. Do not implement until ruled.

**Files:**

- modify `src/privacy/gate.py`
- modify `src/privacy/resolve.py` **or** `src/privacy/release.py` (depends on the ruling)
- modify `src/llm_harness/dossier.py`, `src/llm_harness/records.py` (option b only)
- modify `tests/p7/test_p7_gate.py`, `tests/p8/test_p8_dossier.py` (append)

**The defect, verified.** `src/privacy/gate.py:475–486`:

```python
            value, entry = apply_redaction(
                found.value, observation_key=found.observation_key,
                span=found.span, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                classifier=self._classifier, transform=self._transform)
            resolved.append(Materialised(
                observation_key=found.observation_key, span=found.span, value=value,
                zone=found.zone, context_before=found.context_before,   # <-- RAW
                context_after=found.context_after,                      # <-- RAW
                context_truncated=found.context_truncated,
                unit_length=found.unit_length))
```

`value` is redacted. `context_before` and `context_after` come straight off `found`, which is
`resolve.materialise`'s pre-redaction record. `llm_harness/dossier.py:52–53` copies them into
`ReleasedEvidence`, and `:74–75` writes them into `_released_body` — the canonical model-visible
bytes.

**How much this releases, computed against the live `extractors.shape.context_for`:**

```
$ PYTHONPATH=src python3 -c "..."
unit len 57
span      : 'Hartwell' 8
before    : 'Invoice 88 for Dr. Amelia ' 26
after     : ', acct 4111111111111111' 23
TOTAL released chars if context ships raw = 57 of 57
```

An 8-character requested span released the whole 57-character unit, redaction notwithstanding — the
name was masked and the account number beside it was not. `context_for`'s `window` is configuration
(§8.6), so the leak scales with whatever the deployment sets.

**Authority:**
- `planning/parts/P7-privacy-consent-gate/SPEC.md:248` — `materialised_items[] post-redaction values only`.
- P7's SPEC contains the word "context" **zero** times (`grep -c "context" ...SPEC.md` → `0`).
- `planning/00-database-agent-product-design.md:186` (§8.4) puts **"complete extracted text"** in the
  always-local set, and says the engine "should send only a compact dossier … selected excerpts,
  redacted identifiers".

### Does anything read context? — the evidence

**No validator reads it.** `src/llm_harness/validation.py:_check_citation` (`:130–178`) is the only
consumer of a `ReleasedEvidence` and uses exactly two of its fields:

```python
    if citation.cited_span:
        matched = citation.cited_span in released.value
    elif citation.cited_span is None:
        matched = citation.metadata_field_name == released.address
```

`released.context_before` and `released.context_after` are read **nowhere** in P8. The only reader in
the entire tree is `dossier.py:_released_body`, which puts them in front of the model.

**Keeping context locally is correct and already happens.** `src/privacy/redaction.py`'s module
docstring, third bullet: *"The value is replaced and its context is not. M5 split `context_before`,
`context_after` and `context_truncated` out of the observation 'precisely so §8.4 can redact a value
without dropping its context'."* That statement is about `RedactionEntry`, whose own docstring says
it *"travels inside the audit event's `explanation`"* — the **local** audit manifest. The
`redaction_manifest` keeps the context and must keep it. The **released** item is the one that must
not.

### The two options

**(a) Redact both context fields with the same transform.**
Cost: the transform's contract is `transform(value, *, identifier_class) -> str`, and
`identifier_class` was produced by classifying the **value**, not the context. Applying it to the
context asserts the context has the value's identifier class — a judgement P7 is forbidden to make
(`redaction.py`: "P7 ships no implementation of this protocol"). It also runs
`RedactionIneffective` whenever the transform happens to be an identity over the context.
And when the classifier returns `None` — a value that is not an identifier — `apply_redaction`
returns early and nothing is transformed, so the raw context ships anyway. **Option (a) does not
close the hole for the un-classified case, which is the common case.**

**(b) The released item carries no context at all.** *Recommended.* Nothing reads it; the SPEC never
names it; §8.4 forbids it. Two shapes:

- **(b1)** *Recommended shape.* Split the type. `Materialised` stays the resolution record
  (pre-redaction, with context, feeding the classifier). Add `privacy.release.ReleasedItem`
  — `(observation_key, span, value, zone, unit_length)` — as what `Released.materialised_items`
  carries. `dossier._released_evidence` and `records.ReleasedEvidence` drop the three context fields.
  The released record then has **no place** to put raw text, which is the property, rather than a
  discipline about what to put there.
- **(b2)** *Smaller diff, weaker.* Keep one type; `Gate._materialise` passes
  `context_before=None, context_after=None`. The fields survive as always-`None` decoration. This
  project has already named that pattern a defect: `exclusion.py:107–113` explains at length why a
  field whose only value is its own constant "reached no verdict, no row and no summary".

**Recommendation: (b1).** It is the only option under which a future edit cannot silently re-release
context, and it costs one new record type plus three call sites.

**Interfaces (under b1):**

```
Consumes: privacy.resolve.Materialised   (unchanged -- still carries context; feeds the classifier)
Produces: privacy.release.ReleasedItem(observation_key: str, span: str, value: str,
                                       zone: str, unit_length: int | None)
          privacy.release.Released.materialised_items: tuple[ReleasedItem, ...]
          llm_harness.records.ReleasedEvidence(observation_key, address, value, zone)
```

**Done-means:**

- **D4.1** — for a released span, the canonical model-visible bytes contain the released value and
  **no other character** of the text unit it came from.
- **D4.2** — the `redaction_manifest` entry for that item still carries `context_before`,
  `context_after` and `context_truncated` unchanged (M5's property survives locally).
- **D4.3** — under (b1) only: `ReleasedItem` has no attribute named `context_before` or
  `context_after`, asserted by `dataclasses.fields`.
- **D4.4** — every existing citation test still passes; `validation._check_citation` never needed
  context and must not start needing it.

**Steps:**

- [ ] **Step 4.1: Get the ruling.** Do not proceed until the owner picks (a), (b1) or (b2). The
      test in Step 4.2 is written to be **decision-independent** — it passes under all three — so it
      can and should be written first.

- [ ] **Step 4.2: Write the failing test.** Decision-independent: it asserts the property, not the
      mechanism.

```python
def test_the_release_carries_no_text_outside_the_requested_span(gate_conn):
    """§8.4 puts "complete extracted text" in the always-local set
    (`planning/00-database-agent-product-design.md:186`), and P7 SPEC:248 says
    `materialised_items[] post-redaction values only`. An 8-character requested
    span released all 57 characters of its unit, because the two context fields
    shipped raw beside the redacted value."""
    unit = "Invoice 88 for Dr. Amelia Hartwell, acct 4111111111111111"
    start = unit.index("Hartwell")
    released = _release_span(gate_conn, unit=unit, start=start, end=start + 8)

    item = released.materialised_items[0]
    assert item.value != "Hartwell"                       # it was redacted
    body = json.dumps(_as_released_body(item))
    for forbidden in ("Invoice 88 for Dr. Amelia", "acct 4111111111111111"):
        assert forbidden not in body, f"released: {forbidden!r}"


def test_the_manifest_still_carries_the_context_it_always_did(gate_conn):
    """M5 split the context out "precisely so §8.4 can redact a value without
    dropping its context" (`privacy/redaction.py`). That property is about the
    LOCAL audit entry, which travels inside the audit event's explanation -- it is
    kept, and this asserts it was not thrown away with the released copy."""
    unit = "Invoice 88 for Dr. Amelia Hartwell, acct 4111111111111111"
    start = unit.index("Hartwell")
    released = _release_span(gate_conn, unit=unit, start=start, end=start + 8)

    entry = released.redaction_manifest.entries[0]
    assert entry.context_before == "Invoice 88 for Dr. Amelia "
    assert entry.context_after == ", acct 4111111111111111"
    assert entry.context_truncated is False
```

- [ ] **Step 4.3: Run and state the failure.**
      `PYTHONPATH=src python3 -m pytest tests/p7/test_p7_gate.py -q`
      **Expected: 1 failed** — `AssertionError: released: 'acct 4111111111111111'`. The manifest
      test passes already; it is a regression lock, not a new requirement.

- [ ] **Step 4.4 (option b1): Add `ReleasedItem` to `src/privacy/release.py`.**

```python
@dataclass(frozen=True, slots=True)
class ReleasedItem:
    """One item as the model sees it. SPEC §6: "post-redaction values only".

    There is deliberately no `context_before` and no `context_after`. The context is
    the raw text on either side of the requested span, and §8.4 puts "complete
    extracted text" in the always-local set. `Materialised` keeps them, because the
    classifier is given them before a redaction decision is made and the audit
    manifest records them; a RELEASED item has no place to put them, which is the
    property rather than a discipline about it. An 8-character span released all 57
    characters of its unit for as long as this type was `Materialised`.
    """

    observation_key: str
    span: str
    value: str
    zone: str
    unit_length: int | None
```

- [ ] **Step 4.5 (option b1): Build it in `Gate._materialise`.**

```python
            resolved.append(ReleasedItem(
                observation_key=found.observation_key, span=found.span, value=value,
                zone=found.zone, unit_length=found.unit_length))
```

with `_materialise`'s return annotation becoming
`tuple[tuple[ReleasedItem, ...], RedactionManifest]`. `_postcheck_items` reads only
`item.observation_key` and `item.unit_length` (`gate.py:435`), both of which survive.

- [ ] **Step 4.6 (option b1): Narrow `ReleasedEvidence`.** In `src/llm_harness/records.py` drop the
      three context fields and their `__post_init__` check; in `src/llm_harness/dossier.py` drop
      them from `_released_evidence` (`:51–53`) and `_released_body` (`:73–75`).

- [ ] **Step 4.7: Run the P7 and P8 suites.**
      `PYTHONPATH=src python3 -m pytest tests/p7 tests/p8 tests/integration -q`. Expect churn in
      tests that construct a `ReleasedEvidence` with context keyword arguments
      (`src/llm_harness/fixtures.py:139–140`, `src/privacy/fixtures.py:711`/`:717`/`:935`/`:940`) —
      update the constructions, change no assertion.

- [ ] **Step 4.8: Full suite, then commit.**
      `git commit -m "fix(p7): the gate releases no text outside the requested span"`

**The guard: `test_the_release_carries_no_text_outside_the_requested_span`.**
**Sabotage recipe:** re-add `context_before=found.context_before` to the released item (under b1,
add the field back to `ReleasedItem` and pass it) — the test must fail naming the exact leaked
fragment. Under option (a) instead, make the transform an identity on context — the test must still
fail. A guard that passes under either sabotage is asserting the mechanism rather than the property
and must be rewritten.

---

## Task 5: P9 supplies `run_call`'s real dependencies, and its own conflicts

**Files:**

- modify `src/grouping/pipeline.py`
- modify `src/grouping/p8_seam.py`
- modify `src/production.py` (adds `P8P9Authorities`, `compose_p8_p9`)
- modify `planning/30-p8-p9-connection-contract.md` (correct the stale lines 73–76)
- modify `tests/p9/test_p9_pipeline.py`, `tests/integration/test_p9_p8_group_seam.py` (append)

**The defect, verified.**

```
$ PYTHONPATH=src python3 -c "import inspect; from llm_harness.harness import run_call; print(inspect.signature(run_call))"
run_call (conn, request: 'DossierRequest', *, gate: 'Gate', model_client: 'ModelClient',
          prompt: 'PromptDefinition | None', validation_dependencies,
          observed_at: 'Callable[[], str]') -> ...
```

`src/grouping/pipeline.py:323` is `outcome_from_model = p8_run_call(conn, request)`. Five required
keyword-only arguments are absent: **`TypeError` on the first real call**. Every green test either
passes `p8_run_call=None` (eight of ten) or a callable that swallows keywords (two of ten), so the
defect is invisible.

### How P9 obtains the five dependencies

The contract's answer is stale. `planning/30-p8-p9-connection-contract.md:73–76` says *"P9 passes
`llm_harness.sites.SiteDependencies`; Site B needs no bundle, so `SiteDependencies(fact=None, …)` is
what a group call supplies."* Live code disagrees: `validation_dependencies` is
`llm_harness.harness.CallDependencies`, a **17-field frozen record with no defaults**, of which
`site_dependencies: SiteDependencies | None` is one field. The others are `proposal_class`,
`basis_key`, `learning_scope`, `learning_subject_id`, `evidence_resolver`, `contradicts`,
`unreduced_fits`, `summarized_fits`, `anchors_fit`, `split_shard_fits`, `split_shards`,
`scan_budget`, `estimated_cost`, `actual_cost`, `allowed_vocabulary`, `policy_version`.

Three live facts settle the design:

1. **P9 cannot construct `CallDependencies`.** It is defined in `llm_harness.harness`, and
   `tests/integration/test_p9_p8_group_seam.py:56–74` fails the build if any file in `src/grouping/`
   imports `llm_harness.harness`, `llm_harness.sites`, `llm_harness.transport`,
   `llm_harness.validation`, `llm_harness.group_validation` or `privacy.gate`.
2. **P9 cannot construct a `Gate`.** `Gate.__init__` takes eleven required keyword authorities
   (policy store, classifier, transform, scope resolvers, clock, user id), and the contract at line
   19 says P9 "must not … call `privacy.gate.Gate.release`".
3. **`llm_harness.__all__` is frozen at eight names** and `SiteDependencies` is not among them;
   `test_p9_consumes_exactly_the_eight_frozen_p8_names` asserts the list exactly.

**Therefore: P9 receives all five as one opaque bundle it neither constructs nor inspects.** The
bundle is declared in `src/grouping/pipeline.py` with `object` annotations, so P9 imports nothing
from a forbidden module, and the composition root (`src/production.py`) fills it. The field names are
`run_call`'s keyword names exactly, and a signature-conformance test binds one to the other so the
`TypeError` cannot come back.

**Interfaces:**

```
Consumes: llm_harness.harness.run_call  -- by injection, never by import from src/grouping/
Produces: grouping.pipeline.ModelCallAuthorities(gate, model_client, prompt,
                                                 validation_dependencies, observed_at)
          grouping.pipeline.group_subject(..., p8_run_call, p8_authorities, ...)
          production.P8P9Authorities / production.compose_p8_p9(conn, *, authorities)
```

**Done-means:**

- **D5.1** — `ModelCallAuthorities`' field names equal `run_call`'s keyword-only parameter names,
  asserted by `inspect.signature(run_call).bind(...)`.
- **D5.2** — `group_subject` with a real `run_call` and a filled bundle raises no `TypeError` and
  returns a `GroupDecision`.
- **D5.3** — `p8_run_call` supplied with `p8_authorities=None` fails closed
  (`not_implemented_reason` set, no call, no membership) rather than raising.
- **D5.4** — `DossierRequest.conflicts` carries what `knowledge.conflicts_for` returned; Site B's
  `target_institution` check (`llm_harness/group_validation.py:113`) fires on it.
- **D5.5** — `Membership.conflicts` carries the conflicts that apply to that file, not `()`.
- **D5.6** — no file in `src/grouping/` imports any of the six forbidden modules (the existing
  boundary test still passes).
- **D5.7** — every `conflicts=()` remaining anywhere in `src/grouping/` is on a named allowlist
  carrying a stated reason; a seventh cannot appear without failing the build.
- **D5.8** — the published `GOLDEN_DOSSIERS` collectively carry at least one conflict of every kind
  Site B checks, and that conflict survives `build_dossier_request` into the `DossierRequest`.

**Steps:**

- [ ] **Step 5.1: Write the failing tests.** In `tests/integration/test_p9_p8_group_seam.py`:

```python
def test_the_authorities_bundle_matches_run_calls_real_signature():
    """`pipeline.py:323` called `p8_run_call(conn, request)`. Live `run_call` has
    five required keyword-only arguments, so the first real call was a `TypeError`
    -- invisible because every P9 test injects `None` or a `**kwargs` spy."""
    import dataclasses
    import inspect

    import llm_harness
    from grouping.pipeline import ModelCallAuthorities

    keyword_only = {
        name for name, p in inspect.signature(llm_harness.run_call).parameters.items()
        if p.kind is inspect.Parameter.KEYWORD_ONLY
    }
    fields = {f.name for f in dataclasses.fields(ModelCallAuthorities)}
    assert fields == keyword_only, (fields ^ keyword_only)

    sentinel = object()
    inspect.signature(llm_harness.run_call).bind(
        sentinel, sentinel, **{name: sentinel for name in fields})


def test_the_pipeline_reaches_the_real_run_call(seam_conn, live_authorities, subject):
    from grouping.p8_seam import GroupDecision
    from grouping.pipeline import group_subject

    import llm_harness

    result = group_subject(
        seam_conn, file_id=subject[0], content_hash=subject[1],
        plan_version_id="plan-1", limits=_limits(), knowledge=_knowledge(),
        user_seed_for=lambda f, h: None,
        p8_run_call=llm_harness.run_call,
        p8_authorities=live_authorities,
        embeddings=_embeddings_off(), created_at=T0)

    assert isinstance(result.model_result, GroupDecision)


def test_a_run_call_without_authorities_fails_closed(seam_conn, subject):
    """`planning/30-p8-p9-connection-contract.md:86`: "missing P8/config -> fail
    closed". A missing bundle is missing config, not an exception."""
    import llm_harness
    from grouping.pipeline import NO_MODEL_CONFIGURED, group_subject

    result = group_subject(
        seam_conn, file_id=subject[0], content_hash=subject[1],
        plan_version_id="plan-1", limits=_limits(), knowledge=_knowledge(),
        user_seed_for=lambda f, h: None,
        p8_run_call=llm_harness.run_call, p8_authorities=None,
        embeddings=_embeddings_off(), created_at=T0)

    assert result.not_implemented_reason == NO_MODEL_CONFIGURED
    assert result.model_result is None


def test_the_builders_conflicts_reach_the_dossier_request(seam_conn, subject):
    """`planning/30-p8-p9-connection-contract.md:60-61` added this field BECAUSE
    P8 hardcoded `()`. P9 then hardcoded `()` from the other side, at five sites,
    and `group_validation.py:113`'s `target_institution` check went dead again."""
    from grouping.records import Conflict
    from grouping.pipeline import group_subject

    seen = []
    conflict = Conflict(kind="target_institution",
                        competing_values=("Columbia", "Duke"),
                        file_ids=(subject[0],))
    group_subject(
        seam_conn, file_id=subject[0], content_hash=subject[1],
        plan_version_id="plan-1", limits=_limits(),
        knowledge=_knowledge(conflicts_for=lambda files: (conflict,)),
        user_seed_for=lambda f, h: None,
        p8_run_call=lambda conn, request, **kw: seen.append(request) or None,
        p8_authorities=_empty_authorities(),
        embeddings=_embeddings_off(), created_at=T0)

    assert seen and [c.kind for c in seen[0].conflicts] == ["target_institution"]
```

- [ ] **Step 5.2: Run and state the failure.**
      `PYTHONPATH=src python3 -m pytest tests/integration/test_p9_p8_group_seam.py -q`
      **Expected: 4 failed** — `ImportError: cannot import name 'ModelCallAuthorities'` on the first
      three, and `AssertionError: [] and ...` on the fourth once the import lands.

- [ ] **Step 5.3: Declare the bundle in `src/grouping/pipeline.py`.**

```python
@dataclass(frozen=True)
class ModelCallAuthorities:
    """`run_call`'s five keyword arguments, as P9 receives them.

    Every annotation is `object` on purpose. `CallDependencies` lives in
    `llm_harness.harness` and `Gate` in `privacy.gate`, and
    `test_p9_never_imports_run_calls_neighbours` fails the build if any file under
    `src/grouping/` imports either -- because an import is a second route to a
    model. P9 does not construct one of these, does not read a field of one, and
    does not know their types; it forwards them.

    The FIELD NAMES are `run_call`'s keyword names exactly, and a conformance test
    binds this bundle to the live signature. `pipeline.py` called
    `p8_run_call(conn, request)` for as long as this bundle did not exist, which is
    a `TypeError` on the first real call and a green suite behind a `**kwargs` spy.
    """

    gate: object
    model_client: object
    prompt: object
    validation_dependencies: object
    observed_at: object
```

- [ ] **Step 5.4: Wire the call site.** `pipeline.py:239` gains the parameter and `:323` the
      keywords.

```python
    p8_run_call: Callable[..., object] | None,
    p8_authorities: ModelCallAuthorities | None,
```

```python
    if p8_run_call is None or p8_authorities is None:
        # "missing P8/config -> fail closed" (connection contract, seam ledger).
        # A bundle-less run is a deterministic run, not an exception: P9 calling a
        # model it was given no authority for is the failure this returns instead.
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph, group=group,
            memberships=(membership,), dossier=dossier,
            not_implemented_reason=NO_MODEL_CONFIGURED)

    outcome_from_model = p8_run_call(
        conn, request,
        gate=p8_authorities.gate,
        model_client=p8_authorities.model_client,
        prompt=p8_authorities.prompt,
        validation_dependencies=p8_authorities.validation_dependencies,
        observed_at=p8_authorities.observed_at,
    )
```

The existing `if p8_run_call is None:` block at `:309` is replaced by the combined test above; the
early `NO_MODEL_CONFIGURED` return at `:309–312` moves down to sit after the dossier, which is
where the authorities are first needed.

- [ ] **Step 5.5: Stop hardcoding `conflicts=()` at all six sites.**

`pipeline.py:301` — the dossier assembly already has them: `evaluate_stop_rules` is called with
`conflicts_for=knowledge.conflicts_for` at `:283`. Hoist that call's result:

```python
    conflicts = tuple(knowledge.conflicts_for(tuple(graph.file_ids)))
    outcome = evaluate_stop_rules(
        conn, graph, limits=limits, conflicts_for=lambda _files: conflicts, ...)
    ...
    dossier = assemble_group_dossier(
        conn, group=group, graph=graph, limits=limits, ...,
        conflicts=conflicts, created_at=created_at)
```

`pipeline.py:193` and `:223` (`_group_for` and `_self_membership`) take the same tuple.
`p8_seam.py:172` (`build_dossier_request`) reads them off the dossier it is handed:

```python
        conflicts=tuple(
            Conflict(conflict_id=f"{dossier.group_id}:{item.kind}", kind=item.kind)
            for item in dossier.conflicts),
```

`p8_seam.py:336` (`Membership`) carries the conflicts naming that file:

```python
                conflicts=tuple(item for item in dossier.conflicts
                                if item.file_ids and item.file_ids.count(item.file_id)),
```

**The sixth site — `src/grouping/fixtures.py:177` — is verified and annotated, not changed.**

It is shipped surface, not a test file: its own module docstring says *"These are contract witnesses
that **P10 and P11 build against** before P9's pipeline runs"*, and the P9 plan
(`docs/superpowers/plans/2026-08-25-p9-bounded-evidence-grouping.md:1016`) records that P10/P11's
current P9 connections are *"deliberately fixture publication paths from
`src/grouping/fixtures.py`"*. So a hardcode here would reach P10 and P11.

**But it is not a hardcode.** Verified live:

```
course_dossier_fixture           conflicts=[]
application_dossier_fixture      conflicts=[('target_institution', ('Columbia', 'Duke'))]
```

`fixtures.py:270` already carries the `target_institution` conflict, `engine_flagged_outliers` names
the Duke essay, and `GOLDEN_DOSSIERS` publishes both shapes. The concern that P10/P11 develop
against a fixture that cannot exercise Site B's check is answered by the application dossier, which
exists for exactly that reason — the comment above it says so: *"The conflicting Duke essay is IN the
dossier and flagged, not omitted."*

The course dossier is the design's own conflict-free example (§4.4's course case has no conflicting
course code; §4.4's application case is where the Duke essay appears). Rewriting `:177` to carry a
conflict would put a conflict in the shape the design uses to show a coherent group, which makes the
fixture *less* faithful, not more.

**So the sixth site gets a comment naming why it is empty, and the guard is built to allow it by
name rather than to force a wrong edit.** A guard that fails a correct line is a guard someone
silences, and this project has shipped fifteen silenced guards already.

- [ ] **Step 5.5a: Annotate the sixth site.**

```python
        # Empty because a course group with no conflicting course code is the
        # design's own coherent example (§4.4) -- NOT because the builder had
        # nowhere to get conflicts from, which is what `()` meant at the five
        # production sites above. The conflict-bearing shape is
        # `application_dossier_fixture`, whose `target_institution` conflict is
        # what lets P10 and P11 exercise Site B's check against a published
        # fixture. `CONFLICT_FREE_BY_DESIGN` below names this line for the guard.
        conflicts=(),
```

- [ ] **Step 5.5b: Add the allowlist guard.** In `tests/p9/test_p9_fixtures.py`:

```python
#: Every `conflicts=()` allowed to remain in `src/grouping/`, with the reason.
#: A seventh cannot appear without failing the test below. Adding an entry here is
#: a reviewable decision; adding a bare `conflicts=()` to a module is not.
CONFLICT_FREE_BY_DESIGN = {
    ("fixtures.py", "course_dossier_fixture"):
        "§4.4's coherent course example has no conflicting course code; the "
        "conflict-bearing shape is application_dossier_fixture",
}


def test_no_unexplained_empty_conflicts_survives_in_src_grouping():
    """`planning/30-p8-p9-connection-contract.md:60-61` added `conflicts` BECAUSE
    P8 hardcoded `()` and Site B's `target_institution` check could never fire. P9
    then hardcoded it from the other side at five sites. This is the third chance
    for the same defect, and an allowlist is what makes a fourth reviewable."""
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    found = []
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text())
        scopes = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(node):
                    scopes[id(inner)] = node.name
        for node in ast.walk(tree):
            if not isinstance(node, ast.keyword) or node.arg != "conflicts":
                continue
            if isinstance(node.value, ast.Tuple) and not node.value.elts:
                found.append((path.name, scopes.get(id(node.value), "<module>")))

    unexplained = [site for site in found if site not in CONFLICT_FREE_BY_DESIGN]
    assert unexplained == [], (
        f"bare conflicts=() at {unexplained}; either wire the builder's conflicts "
        f"or add the site to CONFLICT_FREE_BY_DESIGN with a reason")
    stale = [site for site in CONFLICT_FREE_BY_DESIGN if site not in found]
    assert stale == [], f"allowlist entry no longer matches any line: {stale}"


def test_a_published_fixture_can_exercise_every_site_b_conflict_check():
    """P10 and P11 build against `GOLDEN_DOSSIERS`. If no published dossier carries
    a conflict of a kind Site B checks, they are developed against a fixture that
    cannot reach the check -- the frozen contract's defect, one layer further out."""
    from grouping.fixtures import GOLDEN_DOSSIERS

    published = {conflict.kind
                 for build in GOLDEN_DOSSIERS for conflict in build().conflicts}
    assert "target_institution" in published, published


def test_the_published_conflict_survives_into_the_dossier_request():
    """Carrying it on the fixture is not enough -- `build_dossier_request` is where
    P9 hardcoded `()`, so the conflict has to be shown crossing that seam."""
    from grouping.fixtures import application_dossier_fixture
    from grouping.p8_seam import build_dossier_request

    request = build_dossier_request(
        application_dossier_fixture(), model_target=LOCAL,
        prompt_template_id="template.grouping",
        prompt_fingerprint="fixture-application-fingerprint",
        max_dossier_tokens=4000)
    assert [conflict.kind for conflict in request.conflicts] == ["target_institution"]
```

- [ ] **Step 5.6: Add the composition root.** In `src/production.py`, beside `P1P7Authorities`:

```python
@dataclass(frozen=True)
class P8P9Authorities:
    """What a deployment must supply to run the model path.

    P8 is no longer "deliberately absent": `llm_harness.run_call` exists and P9's
    pipeline calls it. Every value here is policy-bearing and injected -- the gate's
    classifier and transform, the model client's destination and invoke callable,
    the authored prompt, and P8's own `CallDependencies`. This module chooses
    plumbing and lifecycle only, exactly as it does for P1--P7.
    """

    gate: object
    model_client: object
    prompt: object
    validation_dependencies: object
    observed_at: Callable[[], str]
    limits: object
    knowledge: object
    plan_version_id: str


def compose_p8_p9(conn: sqlite3.Connection, *, authorities: P8P9Authorities):
    """Bind P9's pipeline to the real `run_call`. Returns `(file_id, hash) -> result`."""
    from grouping.pipeline import ModelCallAuthorities, group_subject
    from llm_harness import run_call

    bundle = ModelCallAuthorities(
        gate=authorities.gate, model_client=authorities.model_client,
        prompt=authorities.prompt,
        validation_dependencies=authorities.validation_dependencies,
        observed_at=authorities.observed_at)

    def group(file_id: str, content_hash: str):
        return group_subject(
            conn, file_id=file_id, content_hash=content_hash,
            plan_version_id=authorities.plan_version_id,
            limits=authorities.limits, knowledge=authorities.knowledge,
            user_seed_for=lambda _f, _h: None,
            p8_run_call=run_call, p8_authorities=bundle,
            embeddings=authorities.knowledge.embeddings,
            created_at=authorities.observed_at())

    return group
```

- [ ] **Step 5.7: Correct the contract.** Replace
      `planning/30-p8-p9-connection-contract.md:73–76` with a paragraph naming
      `llm_harness.harness.CallDependencies` as `validation_dependencies`, noting that
      `SiteDependencies` is one of its seventeen fields and that Site B's is
      `SiteDependencies(fact=None, placement=None, residual=None, template=None)`, and recording
      that P9 receives the whole bundle from its caller because it may construct neither a `Gate`
      nor a `CallDependencies`. This is a factual correction, not a ruling.

- [ ] **Step 5.8: Run.** `PYTHONPATH=src python3 -m pytest tests/p9 tests/integration -q` →
      expected all pass, including the two existing `**kwargs` spies at
      `tests/p9/test_p9_pipeline.py:272` and `:410`, which absorb the new keywords unchanged.

- [ ] **Step 5.9: Full suite, then commit.**
      `git commit -m "fix(p9): p9 supplies run_call's real dependencies and its own conflicts"`

**Guard 1: `test_the_authorities_bundle_matches_run_calls_real_signature`.**
**Sabotage recipe:** add a sixth keyword-only parameter to `run_call` — the test must fail on the
set difference. Rename `ModelCallAuthorities.prompt` to `prompt_definition` — it must fail again.
Then delete one keyword from the `p8_run_call(...)` call — the *signature* test still passes (it does
not read the call site), so `test_the_pipeline_reaches_the_real_run_call` must fail with the
`TypeError`. Both tests are needed; confirm both fire before trusting either.

**Guard 2: `test_no_unexplained_empty_conflicts_survives_in_src_grouping`, and it must be run red
before it is trusted.** Three sabotages, three different failures — run all three:

1. **A seventh site appears.** Add `conflicts=()` to any function in `src/grouping/`. The test must
   fail naming `(file.py, function_name)`. *If it passes, the AST walk is not finding keyword
   arguments and the guard is decoration.*
2. **A real fix is reverted.** Put `conflicts=()` back at `p8_seam.py:172`. The test must fail —
   `build_dossier_request` is not on the allowlist — **and**
   `test_the_published_conflict_survives_into_the_dossier_request` must fail with `[] != ['target_institution']`.
   *Two independent failures for one regression is the point: the allowlist catches the shape, the
   behavioural test catches the consequence.*
3. **The allowlist goes stale.** Delete the `conflicts=()` line at `fixtures.py:177` entirely (leave
   the field to its default). The `stale` assertion must fail. *Without this half, the allowlist
   would silently license a line that no longer exists and would re-license it if it came back for
   a different reason.*

A blanket "no `conflicts=()` anywhere" guard was rejected: it would fail `fixtures.py:177`, which is
correct, and a guard that fails a correct line is the one that gets commented out.

> **OPEN — owner decides: does `src/production.py` grow to P8+P9?**
> Its docstring says *"P8 is deliberately absent; whether an LLM stage exists is a decision already
> frozen inside each supplied P6 resolver."* Task 1 needs a composition root that wires P8 and P9, and
> there is none. Options: **(i)** extend `production.py` as written above — recommended, it is
> already the one place that binds plumbing to injected authorities; **(ii)** add a separate
> `src/production_model.py` so the P1–P7 root keeps its "no model" property literally; **(iii)** keep
> the wiring in the integration test only, which leaves the product with no way to run the model path
> and defers the defect. **(iii) is not recommended** — it is how defect 3 survived.

---

## Task 6: Proposals rest on live facts and screened observations

**Files:**

- modify `src/facts/read_surface.py`
- modify `src/facts/resolver.py`
- modify `tests/p6/test_p6_read_surface.py`, `tests/p6/test_p6_resolver.py` (append)

### Part A — `proposal_eligible` returns superseded conclusions

`src/facts/read_surface.py:143`:

```python
def proposal_eligible(conn, *, file_id, content_hash) -> list[sqlite3.Row]:
    return facts_for(conn, file_id=file_id, content_hash=content_hash,
                     states=PROPOSAL_ELIGIBLE_STATES)
```

`facts_for` (`:108`) filters state and field scope only, and delegates to `facts_for_file`
(`file_facts.py:290`) whose docstring says: *"Unfiltered: selecting by `active`, by `preferred` or by
reliability state is the proposal-eligible read."* Twenty-three lines below, `values_with_counts`
does filter both — its SQL at `:195` is `WHERE active = 1 AND superseded_by IS NULL` — and its
docstring explains exactly why:

> ONLY PROPOSAL-ELIGIBLE FACTS COUNT. … the two reads in this one module disagreed about the same file.

They still disagree, in the other direction: the counter excludes superseded rows and the read that
feeds P10/P11's folder proposals does not. A replaced conclusion reaches a folder proposal.

### Part B — the §2.2 survivor set is computed and thrown away

`src/facts/resolver.py:174–177`:

```python
        # §2.2 fires before ranking. The return value is the survivor set;
        # stages that re-query observations still use field_permitted.
        # This call is what writes the unresolved row Done-means 22 requires.
        self._screen_metadata(conn, file_id, content_hash)
```

The return value is discarded. `screen_metadata` (`discount.py:131`) does two things: it writes the
`unresolved` row, and it *returns the survivors*. Only the first happens. The comment's promise —
"stages that re-query observations still use `field_permitted`" — is false:
`facts.discount.field_permitted` (`discount.py:113`) has **no production caller anywhere**; the only
references outside its own definition are this comment and `tests/p6/test_p6_discount.py`.

`FactResolver.__init__`'s own docstring (`resolver.py:110–113`) states the consequence: *"§2.2's
tool-metadata suppression must fire **before** any producer; without this call `python-docx` can
become a `direct` fact and Done-means 22 is unreachable."* The call fires and constrains nothing.

**Interfaces:**

```
Consumes: facts.discount.field_permitted(observation, field_key, *,
              tool_producer_strings, metadata_property_names) -> bool
          facts.discount.screen_metadata(...) -> tuple[Observation, ...]
Produces: facts.read_surface.proposal_eligible  (same signature; narrower result)
          facts.resolver.Stage protocol gains the survivor set
```

**Done-means:**

- **D6.1** — a fact whose row has `superseded_by IS NOT NULL` does not appear in
  `proposal_eligible`, and does appear in `facts_for` and in `history`.
- **D6.2** — a fact whose row has `active = 0` does not appear in `proposal_eligible`.
- **D6.3** — `proposal_eligible` and `values_with_counts` agree: for one field, the set of values
  reachable from `proposal_eligible` equals the set `values_with_counts` counts.
- **D6.4** — a `python-docx` producer string in a metadata property yields **no fact in any field**,
  including `authored_by`, plus one `unresolved` row with reason `discounted_tool_metadata`.
- **D6.5** — a HUMAN name in the same property yields an `authored_by` fact and **no** fact in any
  other field (the demotion tier, `_PLAN-AUTHORING-BRIEF.md` §4).
- **D6.6** — `field_permitted` has at least one production caller, asserted by import graph, not by
  a text search.

**Steps:**

- [ ] **Step 6.1: Write the failing tests.**

```python
def test_a_superseded_conclusion_is_not_proposal_eligible(facts_conn, version):
    """§3.13 makes `rejected` an exclusion from proposals; §8.2 keeps a superseded
    row readable. A readable old row is not a folder the product still proposes --
    which `values_with_counts` says in its own docstring, 23 lines below, and
    enforces in SQL. `proposal_eligible` did not."""
    first = _write_fact(facts_conn, version, field="subject", value="BUSIB 4300")
    second = _write_fact(facts_conn, version, field="subject", value="BUSIB 4301",
                         supersedes=first)

    eligible = {row["fact_id"] for row in proposal_eligible(
        facts_conn, file_id=version.file_id, content_hash=version.content_hash)}
    assert eligible == {second}
    assert first in {row["fact_id"] for row in facts_for(
        facts_conn, file_id=version.file_id, content_hash=version.content_hash)}


def test_an_inactive_fact_is_not_proposal_eligible(facts_conn, version):
    inactive = _write_fact(facts_conn, version, field="subject",
                           value="BUSIB 4300", active=False)
    assert inactive not in {row["fact_id"] for row in proposal_eligible(
        facts_conn, file_id=version.file_id, content_hash=version.content_hash)}


def test_the_two_reads_in_this_module_agree(facts_conn, version):
    """The defect `values_with_counts` was written to fix, from the other side."""
    _write_fact(facts_conn, version, field="subject", value="LIVE")
    superseded = _write_fact(facts_conn, version, field="subject", value="OLD")
    _supersede(facts_conn, superseded)

    proposable = {row["canonical_value"] for row in proposal_eligible(
        facts_conn, file_id=version.file_id, content_hash=version.content_hash)
        if row["field_key"] == "subject"}
    counted = {value for value, _count in values_with_counts(
        facts_conn, field_key="subject")}
    assert proposable == counted


def test_a_tool_producer_string_becomes_no_fact_in_any_field(resolver_conn, version):
    """Done-means 22, both halves. `resolver.py:174` computes the survivor set and
    discards it, and `field_permitted` has no production caller -- so an auditor
    produced `subject = "python-docx"` as a `validated` fact."""
    _observation(resolver_conn, version, zone="metadata", slot="creator",
                 raw_value="python-docx")
    _resolver(resolver_conn).resolve(
        resolver_conn, file_id=version.file_id, content_hash=version.content_hash)

    facts = facts_for(resolver_conn, file_id=version.file_id,
                      content_hash=version.content_hash)
    assert [row["canonical_value"] for row in facts] == []
    unresolved = unresolved_for(resolver_conn, file_id=version.file_id,
                                content_hash=version.content_hash)
    assert [row["reason"] for row in unresolved] == ["discounted_tool_metadata"]


def test_a_human_name_is_demoted_and_not_suppressed(resolver_conn, version):
    _observation(resolver_conn, version, zone="metadata", slot="creator",
                 raw_value="Amelia Hartwell")
    _resolver(resolver_conn).resolve(
        resolver_conn, file_id=version.file_id, content_hash=version.content_hash)

    facts = facts_for(resolver_conn, file_id=version.file_id,
                      content_hash=version.content_hash)
    assert {row["field_key"] for row in facts} == {"authored_by"}


def test_field_permitted_has_a_production_caller():
    """Asserted on the import graph, not on source text. Scanning text for a token
    has produced a false result nine times on this project."""
    import ast
    import pathlib

    import facts

    root = pathlib.Path(facts.__file__).resolve().parent
    callers = []
    for path in sorted(root.glob("*.py")):
        if path.name == "discount.py":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "field_permitted":
                callers.append(f"{path.name}:{node.lineno}")
    assert callers, "field_permitted is published and called by nothing"
```

- [ ] **Step 6.2: Run and state the failure.**
      `PYTHONPATH=src python3 -m pytest tests/p6 -q` → **expected: 6 failed**, the first three on the
      superseded/inactive row appearing, the next two on a `python-docx` fact existing and on the
      human name reaching a second field, the last on an empty `callers` list.

- [ ] **Step 6.3: Narrow `proposal_eligible`.**

```python
def proposal_eligible(conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str) -> list[sqlite3.Row]:
    """The facts a folder proposal may rest on.

    §3.6: a weak model output "may remain a possible clue for review; it must not
    quietly become a folder proposal or an asserted file property". `unresolved` rows
    are in a different table and are therefore absent by construction rather than by
    a filter.

    Three filters, not one. `active = 0` and a non-null `superseded_by` are both
    "this conclusion was replaced", and §8.2 keeps the replaced row READABLE --
    readable is not proposable. `values_with_counts`, 23 lines below, has always
    filtered all three, and its docstring records what happened when the two reads
    in this one module disagreed about the same file. They disagreed in the other
    direction too: a replaced conclusion reached P10/P11's folder-proposal read.
    """
    return [row for row in facts_for(conn, file_id=file_id,
                                     content_hash=content_hash,
                                     states=PROPOSAL_ELIGIBLE_STATES)
            if row["active"] and row["superseded_by"] is None]
```

- [ ] **Step 6.4: Make the survivor set constrain the stages.** `resolver.py:174–177`:

```python
        # §2.2 fires before ranking, and its RETURN VALUE is the survivor set. It was
        # discarded for as long as the `Stage` protocol took only the version, and
        # `field_permitted` -- published for exactly this -- had no production caller:
        # `python-docx` reached `subject` as a `validated` fact with the unresolved
        # row sitting beside it saying it had not.
        survivors = self._screen_metadata(conn, file_id, content_hash)
```

and each stage call becomes `stage(conn, file_id, content_hash, survivors)`. The `Stage` protocol
in `facts/resolver.py` gains the fourth positional parameter, and the four fixtures/tests that bind
a stage gain an ignored fourth argument.

- [ ] **Step 6.5: Call `field_permitted` where a stage picks a field.** The stage receives survivors
      (suppression already applied), and applies `field_permitted` for the demotion tier — a HUMAN
      name may support `authored_by` and "no other field":

```python
        if not field_permitted(observation, field_key,
                               tool_producer_strings=tool_producer_strings,
                               metadata_property_names=metadata_property_names):
            continue
```

- [ ] **Step 6.6: Run the P6 suite, then the full suite, then commit.**
      `git commit -m "fix(p6): proposals rest on live facts and screened observations"`

**The guard: `test_the_two_reads_in_this_module_agree` and
`test_field_permitted_has_a_production_caller`.**
**Sabotage recipe:** drop the `row["superseded_by"] is None` clause — the agreement test must fail
with two values on one side and one on the other. Then restore it and delete the `field_permitted`
call from the stage — the import-graph test must fail with an empty list *and*
`test_a_human_name_is_demoted_and_not_suppressed` must fail. The import-graph test alone is not
enough (a call inside dead code would satisfy it), which is why the behavioural test is paired
with it.

> **NOTE — this task changes the `Stage` protocol.** `_PLAN-AUTHORING-BRIEF.md` D5 cut P6 Task 26
> (the orchestrator restructure) and says "P6 touches **no file outside `src/facts/` and
> `tests/p6/`**". This change stays inside that boundary: `Stage` is declared in `facts/resolver.py`
> and its only production binder is `src/production.py:123`'s `resolve()` adapter, which forwards
> whatever `FactResolver.resolve` passes. No orchestrator wiring changes.

---

## Task 7: The support bar decides `supported`

**Files:**

- modify `src/grouping/pipeline.py`
- modify `tests/p9/test_p9_pipeline.py` (append)

**The defect, verified.** `src/grouping/graph.py:262` defines `meets_support_bar`. Its only other
mention anywhere is the comment at `:298`. `SUPPORTED` (`vocabulary.py:23`) appears in exactly two
places: its own definition and the `GROUP_STATES` tuple. `pipeline.py:195` writes
`state=CANDIDATE` unconditionally. **No group can ever become `supported`.**

`graph.py:265–271` states why this is load-bearing:

> Not a stop rule, and deliberately separate from SR1. SR1 is "no valid anchor" — zero of them — and
> it stops the group forming at all. This is §4.9's minimum independent anchor count, which decides
> whether a formed group may become `supported` rather than staying a candidate. **Conflating the
> two made a one-anchor group vanish instead of waiting for confirmation.**

Both rules exist; only one is wired. `minimum_independent_anchors` is injected with no default
(`config.py:44`, `:75`) — P9 SPEC:654 lists it among the thresholds that "must be measured through
P2 (§8.5) before any value is written down". Nothing is invented here.

**Interfaces:**

```
Consumes: grouping.graph.meets_support_bar(graph, *, limits: GroupingLimits,
                                           seed_anchors: bool) -> bool
Produces: unchanged signatures; `Group.state` may now be SUPPORTED
```

**Done-means:**

- **D7.1** — a graph whose independent anchor count reaches `limits.minimum_independent_anchors`
  produces `Group.state == "supported"`.
- **D7.2** — one anchor below the bar produces `state == "candidate"`, and **no** stop rule fires
  (the group exists and waits).
- **D7.3** — zero anchors still fires SR1 and produces no group at all — SR1 and the bar remain two
  rules.
- **D7.4** — the recorded row round-trips: `current_group(conn, id).state` equals the computed state.

**Steps:**

- [ ] **Step 7.1: Write the failing tests.**

```python
def test_enough_independent_anchors_makes_a_group_supported(pipeline_conn, subject,
                                                            tmp_path):
    """`graph.py:262` computes the bar; nothing called it, so `SUPPORTED` was a
    vocabulary member no writer could reach."""
    _second_anchor(pipeline_conn, tmp_path)
    result = _run(pipeline_conn, subject, p8_run_call=None,
                  limits=_limits(minimum_independent_anchors=2))
    assert result.group.state == SUPPORTED
    assert current_group(pipeline_conn, result.group.group_id).state == SUPPORTED


def test_one_anchor_below_the_bar_waits_as_a_candidate(pipeline_conn, subject):
    """"Conflating the two made a one-anchor group vanish instead of waiting for
    confirmation" (`graph.py:270`). It must not vanish and must not be supported."""
    result = _run(pipeline_conn, subject, p8_run_call=None,
                  limits=_limits(minimum_independent_anchors=2))
    assert result.group is not None
    assert result.group.state == CANDIDATE
    assert result.stop_rule_outcome is None


def test_zero_anchors_still_fires_sr1(pipeline_conn, anchorless_subject):
    """SR1 and the support bar stay two rules. SR1 stops the group forming."""
    result = _run(pipeline_conn, anchorless_subject, p8_run_call=None,
                  limits=_limits(minimum_independent_anchors=2))
    assert result.group is None or result.stop_rule_outcome is not None
    assert SR1 in result.stop_rule_outcome.fired
```

- [ ] **Step 7.2: Run and state the failure.**
      `PYTHONPATH=src python3 -m pytest tests/p9/test_p9_pipeline.py -q` → **expected: 1 failed**,
      `AssertionError: 'candidate' == 'supported'`. The other two pass already and are regression
      locks on the SR1/bar separation.

- [ ] **Step 7.3: Wire it.** In `group_subject`, after `build_graph` and after `evaluate_stop_rules`
      returned `None` (a group that cannot form is not a group whose state is worth computing):

```python
from grouping.graph import (
    LocalEvidenceGraph, build_graph, evaluate_stop_rules, meets_support_bar,
)
from grouping.vocabulary import SUPPORTED
```

```python
    # SR1 already returned above for zero anchors. This is §4.9's minimum
    # INDEPENDENT anchor count, and it decides `supported` rather than existence --
    # `graph.py:265`: "Not a stop rule, and deliberately separate from SR1."
    # `minimum_independent_anchors` is injected with no default (`config.py:44`);
    # P9 SPEC:654 lists it among the thresholds P2 must measure before any value is
    # written down, so nothing here invents one.
    group = _group_for(
        seed, group_id=f"group:{file_id}:{seed.seed_kind}", created_at=created_at,
        state=SUPPORTED if meets_support_bar(
            graph, limits=limits,
            seed_anchors=bool(seed.observation_key and seed.reliability_state),
        ) else CANDIDATE)
```

`_group_for` (`pipeline.py:~185`) gains a keyword-only `state: str` with no default, and `:195`'s
literal `state=CANDIDATE` becomes `state=state`. The `build_graph` call must move above `_group_for`,
which is a reordering of two adjacent statements with no dependency between them.

- [ ] **Step 7.4: Run, full suite, commit.**
      ``git commit -m "fix(p9): the support bar decides `supported`"``

**The guard: `test_enough_independent_anchors_makes_a_group_supported`.**
**Sabotage recipe:** replace the conditional with `state=CANDIDATE` — the test must fail. Then
replace it with `state=SUPPORTED` unconditionally — `test_one_anchor_below_the_bar_waits_as_a_candidate`
must fail. Two tests pinning opposite directions: a single-sided guard would pass an
always-`supported` regression, which is the more dangerous of the two.

---

## Task 8: A positional signal survives D10's collapse

**Files:**

- modify `src/extractors/sink.py`
- modify `src/extractors/long_tail.py`
- modify `tests/p5/test_p5_long_tail.py`, `tests/p4/test_p4_emit_order.py` (append)

**The defect, verified.** `src/extractors/sink.py:49` runs D10's collapse inside
`ExtractionResult.__post_init__`:

```python
        object.__setattr__(self, "observations", _collapse(self.observations))
```

`_collapse` (`:52`) keys on `(location.zone, raw_value)` and keeps the first, so the tuple **shrinks
and renumbers**.

`src/extractors/long_tail.py:246` records a signal against the pre-collapse position:

```python
            signals.append(SensitivitySignal(observation_index=len(observations) - 1, ...))
```

and `SensitivitySignal`'s docstring (`:132`) defines it as *"the observation's position in the
batch"*. At `:302–314` the pre-collapse list is handed to `ExtractionResult`, which collapses it, and
the signals are handed through untouched. `record_sensitivity_signals` (`:344–351`) then resolves
`observation_keys[signal.observation_index]` against **P4's keys for the written (collapsed) batch**.

Two concrete outcomes, both live:

- An email whose `From` and `Reply-To` carry the same address emits both at `zone="metadata"` with
  the same `raw_value`, so `_collapse` merges them. Every signal recorded after the merge point
  shifts down one, and §2.9's *"treating addresses and message content as potentially sensitive"* is
  filed against whichever observation now occupies that index — the `Subject`, if `Subject` follows
  the addresses in `document.values`.
- Three copies of one address collapse three observations into one. The last signal's index is then
  `>= len(observation_keys)` and `record_sensitivity_signals` raises `IndexError` — which nothing
  catches, so the scan ends.

The `Dispatched.__post_init__` invariant at `dispatch.py:92–112` was written for exactly this class
of bug ("the Wave-2 caller resolved E3's signals against the FILESYSTEM run's keys for a day"). It
guards *which batch*; it cannot guard *which position within one*.

**Sub-defect, same root cause, and it is the larger of the two.** `run["observation_count"]` is
computed from the pre-collapse list in nine places (`archive.py:186`, `docx.py:213`,
`filesystem.py:109` and `:163`, `image.py:203`, `long_tail.py:311`, `ocr.py:191`, `pdf.py:178`,
`structured_text.py:185`), so a run row can claim more observations than its batch contains.

**Why this matters beyond tidiness.** `src/extractors/stage_output.py:73` copies that number
straight into the P2 stage payload:

```python
            "observation_count": run["observation_count"],
```

§8.5 is the design's measurement surface — the thing that decides whether a threshold is right, and
the thing every unset number in this project is waiting on ("All must be measured through P2 (§8.5)
before any value is written down", P9 SPEC:654). **Every extractor run whose batch contains one
repeated value reports a stage count its own batch cannot support**, in every format, not only
`.eml`. This is not "an `.eml` edge case with a bad index": it is P2's `observation_count` being
systematically high for any file that mentions the same string twice in one zone — a heading
repeated in a PDF, an identifier repeated in a spreadsheet, a tag repeated in an archive manifest.
Every threshold measured off that column has been measured off an overcount.

**Interfaces:**

```
Produces: ExtractionResult.collapsed_index: tuple[int, ...]
              -- for every observation as SUBMITTED, its position after D10 collapsed
```

**Done-means:**

- **D8.1** — two `long_tail` observations sharing `(zone, raw_value)` collapse to one, and the
  sensitivity signal resolves to that one's `observation_key`, not to a neighbour's.
- **D8.2** — three copies raise **no** `IndexError`, and produce exactly one signal row.
- **D8.3** — `len(result.collapsed_index) == len(submitted)` and
  `max(collapsed_index) < len(result.observations)` for every extractor.
- **D8.4** — `run["observation_count"] == len(result.observations)` for every extractor, asserted
  parametrically.
- **D8.5** — a batch with no duplicates has `collapsed_index == tuple(range(n))` (identity), so
  nothing changes for the ordinary case.

**Steps:**

- [ ] **Step 8.1: Write the failing tests.**

```python
def test_a_signal_survives_the_collapse_of_a_duplicate_address(long_tail_conn, tmp_path):
    """D10 collapses on `(zone, raw_value)` and renumbers. `long_tail` recorded the
    signal against the PRE-collapse position, so an email whose From and Reply-To
    share an address filed §2.9's sensitivity signal against the next observation."""
    document = LongTailFile(values=(
        _value("From", "same@example.com"),
        _value("Reply-To", "same@example.com"),
        _value("Subject", "Quarterly review"),
    ), entries=(_entry(),))
    result = extract_long_tail(**_arguments(document))

    assert len(result.extraction.observations) == 2      # the two addresses merged
    flagged = {result.extraction.observations[s.observation_index]["raw_value"]
               for s in result.sensitivity}
    assert flagged == {"same@example.com"}


def test_three_copies_do_not_end_the_scan(long_tail_conn, tmp_path):
    """`record_sensitivity_signals` raises IndexError for a position past the
    collapsed batch, and nothing catches it."""
    document = LongTailFile(values=tuple(
        _value(name, "same@example.com") for name in ("From", "Reply-To", "Cc")
    ), entries=(_entry(),))
    result = extract_long_tail(**_arguments(document))

    run_id = _write(long_tail_conn, result.extraction)
    stored = record_sensitivity_signals(
        long_tail_conn, run_id=run_id, signals=result.sensitivity,
        observation_keys=observation_keys_for_run(long_tail_conn, run_id), now=NOW)
    assert stored == 1


def test_the_collapse_publishes_where_every_submitted_observation_went():
    submitted = (_obs("metadata", "a"), _obs("metadata", "a"), _obs("body", "b"))
    result = ExtractionResult(run=_run(), observations=submitted)
    assert result.collapsed_index == (0, 0, 1)
    assert len(result.observations) == 2


def test_the_identity_case_is_the_identity():
    submitted = (_obs("metadata", "a"), _obs("body", "b"))
    assert ExtractionResult(run=_run(), observations=submitted).collapsed_index == (0, 1)


@pytest.mark.parametrize("build", ALL_EXTRACTOR_BUILDERS)
def test_the_run_counts_what_the_batch_holds(build):
    """`stage_output.py:73` copies `run["observation_count"]` into the P2 payload,
    and every extractor computed it before D10 collapsed."""
    result = build()
    assert result.run["observation_count"] == len(result.observations)
```

- [ ] **Step 8.2: Run and state the failure.**
      `PYTHONPATH=src python3 -m pytest tests/p4 tests/p5 -q` → **expected: 5 failed** — the first on
      `flagged == {"Quarterly review"}`, the second with `IndexError`, the third and fourth with
      `AttributeError: 'ExtractionResult' object has no attribute 'collapsed_index'`, the last on
      the count mismatch for the duplicate-bearing builders.

- [ ] **Step 8.3: Publish the index map from `_collapse`.**

```python
def _collapse(observations):
    """D10, plus where every submitted observation went.

    The map is returned because the collapse RENUMBERS, and a caller that recorded
    a position into the submitted list has no other way to follow it.
    `long_tail.SensitivitySignal.observation_index` is the only such caller and it
    filed §2.9's sensitivity signal against a neighbour for as long as this returned
    only the survivors.
    """
    first: dict[tuple, int] = {}
    kept: list[dict] = []
    index: list[int] = []
    for candidate in observations:
        zone = (candidate.get("location") or {}).get("zone")
        key = (zone, candidate.get("raw_value"))
        if key not in first:
            first[key] = len(kept)
            row = dict(candidate)
            row.setdefault("occurrence_count", 1)
            kept.append(row)
        else:
            kept[first[key]]["occurrence_count"] = (
                kept[first[key]]["occurrence_count"]
                + (candidate.get("occurrence_count") or 1))
        index.append(first[key])
    return tuple(kept), tuple(index)
```

- [ ] **Step 8.4: Publish it on the result, and correct the count.**

```python
@dataclass(frozen=True)
class ExtractionResult:
    """One run and everything it produced. The unit P5 hands to P4."""
    run: Mapping[str, Any]
    observations: tuple[Mapping[str, Any], ...] = ()
    text_units: tuple[Mapping[str, Any], ...] = ()
    #: For every observation as SUBMITTED, its position in `observations` after D10
    #: collapsed. A constructor argument only so the dataclass can hold it; it is
    #: always recomputed below, and passing one is not a way to state a different map.
    collapsed_index: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        """P4 D10 is applied HERE, once, for every extractor.
        ... (existing docstring unchanged) ...

        The collapse RENUMBERS, so it also publishes `collapsed_index` and corrects
        `observation_count`. Nine extractors counted the SUBMITTED list, and
        `stage_output.py:73` copies that number into the P2 payload, so a batch with
        one duplicate reported a count its own batch could not support.
        """
        collapsed, index = _collapse(self.observations)
        object.__setattr__(self, "observations", collapsed)
        object.__setattr__(self, "collapsed_index", index)
        if self.run.get("observation_count") != len(collapsed):
            object.__setattr__(self, "run",
                               {**self.run, "observation_count": len(collapsed)})
```

- [ ] **Step 8.5: Remap the signals in `long_tail`.** Replace `:302–314`'s single expression with:

```python
    entries = len(document.entries) or 1
    extraction = ExtractionResult(
        run=run(file_id=file_row["file_id"],
                content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=source_type, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected", "transcribe": transcribe},
                completeness="complete",
                coverage=coverage("entries", entries, entries),
                observation_count=len(observations), started_at=now,
                finished_at=now),
        observations=tuple(observations),
        text_units=tuple(units))

    # D10 collapsed and renumbered. A signal's `observation_index` is a position in
    # the SUBMITTED list, so it is mapped through before it leaves this function --
    # after this point nothing remembers what the submitted list looked like.
    # Two signals can land on one survivor (a From and a Reply-To sharing an
    # address ARE one located value once collapsed); the triple is deduplicated so
    # one value does not get two rows, and two DIFFERENT bases still get two,
    # because those are two reasons and §2.9 records the reason.
    remapped: list[SensitivitySignal] = []
    for signal in signals:
        moved = SensitivitySignal(
            observation_index=extraction.collapsed_index[signal.observation_index],
            signal=signal.signal, basis=signal.basis)
        if moved not in remapped:
            remapped.append(moved)

    return LongTailResult(extraction=extraction, sensitivity=tuple(remapped))
```

- [ ] **Step 8.6: Run P4 and P5, then the full suite, then commit.**
      `git commit -m "fix(p5): a positional signal survives D10's collapse"`

**The guard: `test_a_signal_survives_the_collapse_of_a_duplicate_address` and the parametrised
count test.**
**Sabotage recipe:** return `tuple(signals)` unmapped from `extract_long_tail` — the first test must
fail with `flagged == {"Quarterly review"}` and the second with `IndexError`. Then restore it and
delete the `observation_count` correction in `__post_init__` — the parametrised test must fail for
every builder that emits a duplicate. If the parametrised test passes with the correction removed,
no builder in `ALL_EXTRACTOR_BUILDERS` emits a duplicate and the parameter list is the thing that is
wrong.

---

## Task 9: The egress guard runs over the real transport

> ### OPEN — owner decides. This is a design question, not a bug with one answer.

**Files:**

- modify `src/llm_harness/transport.py`
- modify `src/privacy/transport_guard.py` (depends on the ruling)
- modify `tests/p7/test_p7_skeleton_step.py`, `tests/p7/test_p7_transport.py`

**The defect, verified.** `src/privacy/transport_guard.py:27–28` says:

> Running this over the real transport is P8's obligation and cannot happen here — **there is no
> transport module in this repository.**

That is now false: `src/llm_harness/transport.py` exists and is the sole egress. It does not set
`IS_MODEL_TRANSPORT = True` (the only assignment anywhere is `transport_guard.py:56`, which sets
`False`), so `tests/p7/test_p7_skeleton_step.py:403–409` scans every module in `src/`, finds none,
asserts the empty list, and its `for module in transports: assert_single_egress(module)` loop —
commented *"reachable the day P8 lands"* — has never executed a single iteration.

**Pointed at the real transport, the guard fails it.** Run read-only against live code:

```
$ PYTHONPATH=src python3 -c "from privacy.transport_guard import assert_single_egress; import llm_harness.transport as m; assert_single_egress(m)"
UnreleasedContentParameter : ModelClient.__init__(invoke) accepts <class 'bytes'>,
which is content the gate never minted a release for
```

The full set of violations, enumerated with the guard's own internals:

```
ModelClient.__init__(invoke)             -> bytes
ModelResponse.__init__(response_bytes)   -> bytes
ModelResponse.__init__(model_id)         -> str
ModelResponse.__init__(prompt_fingerprint) -> str
ModelResponse.__init__(response_id)      -> str
ModelResponse.__init__(release_id)       -> str
_explanation(model_id)                   -> str
_explanation(prompt_fingerprint)         -> str
_failed(explanation)                     -> str
_record_issued(fingerprint)              -> str
_record_issued(observed_at)              -> str
```

The public entry point itself is clean:

```
issue (conn: sqlite3.Connection, released: Released, payload: CallPayload, *,
       model_client: ModelClient) -> ModelResponse | CallFailed
```

Exactly one public function; it takes a `Released`; it takes no forbidden type. That is Done-means
1 satisfied literally: *"Exactly one function in the codebase constructs a model request, and its
only parameter type is P7's `Released`."*

**So the guard is not merely finding one hole — it forbids every `str` parameter in the module,
including an ISO timestamp (`_record_issued(observed_at)`) and a model id.** It was proven against
seventeen non-conforming fixtures and zero real transports, and its content-type list was calibrated
for a hypothetical one.

### The options

**(a) Conform the transport.** Wrap all eleven `str`/`bytes` parameters in nominal types.
Cost: ~6 new record types for ids, fingerprints and timestamps that are not content by any reading.
Benefit: the guard passes unmodified.
Against: it makes the module less readable to satisfy a proxy, and a future `str` parameter is a
build break rather than a review conversation.

**(b) Narrow the guard to the egress surface.** Keep rules 1 and 2 (resolved annotations, walked
containers); change rule 3 from *"every function in the module is checked"* to *"the public entry
point and every parameter type reachable from it"*. That still catches
`ModelClient.__init__(invoke: Callable[[bytes], bytes])`, because `ModelClient` is `issue`'s
parameter type — which is the one real hole. It stops flagging a timestamp.
Against: rule 3's stated reason is that *"the un-released path does not exist" is a claim about the
module, not its exports*, and a private `_format(text: str)` helper is exactly what it was written
to catch.

**(c) Both.** Narrow the guard per (b), **and** give `invoke` a nominal type so no bare `bytes`
crosses the boundary even under the narrowed rule:

```python
@dataclass(frozen=True, slots=True)
class ModelVisibleBytes:
    """The canonical dossier bytes, and the only thing a client is ever handed.

    A nominal type rather than `bytes` because the egress guard cannot tell a
    released dossier from a `TextUnit.text`, and §8.4 puts the second in the
    always-local set. Constructing one is the assertion that the gate released it;
    `issue` is the only place that does.
    """

    value: bytes
```

**Recommendation: (c).** It keeps the guard's own standard ("shown to be" is the only standard an
inspection can hold) while removing the eleven findings that are about identifiers rather than
content, and it puts a name on the one boundary where content genuinely does cross.

**Done-means:**

- **D9.1** — `llm_harness.transport.IS_MODEL_TRANSPORT is True`.
- **D9.2** — `assert_single_egress(llm_harness.transport)` returns `None`.
- **D9.3** — the module scan in `tests/p7/test_p7_skeleton_step.py` finds **exactly one** declared
  transport, and runs `assert_single_egress` over it — the loop executes at least one iteration.
- **D9.4** — `transport_guard.py`'s docstring no longer claims there is no transport in this
  repository.
- **D9.5** — all seventeen non-conforming fixtures in `tests/p7/transport_fixtures.py` still fail
  the guard under whatever narrowing is chosen. **This is the check that keeps (b) and (c) honest:**
  a narrowing that also lets a fixture through has removed the guard rather than focused it.

**Steps:**

- [ ] **Step 9.1: Get the ruling.** (a), (b) or (c). Steps 9.2 and 9.3 are independent of it.

- [ ] **Step 9.2: Write the failing tests.**

```python
def test_the_repository_now_has_exactly_one_declared_transport():
    """`test_p7_skeleton_step.py:405` asserted `transports == []` and its
    `assert_single_egress` loop -- "reachable the day P8 lands" -- never ran one
    iteration. P8 landed."""
    declared = [dotted for dotted, path, _m in src_modules() if _declares_transport(path)]
    assert declared == ["llm_harness.transport"]


def test_the_real_transport_satisfies_the_guard():
    import llm_harness.transport as transport
    assert assert_single_egress(transport) is None


@pytest.mark.parametrize("name", NON_CONFORMING_FIXTURE_NAMES)
def test_every_non_conforming_fixture_still_fails(name):
    """The narrowing must focus the guard, not remove it."""
    with pytest.raises(EgressGuardFailure):
        assert_single_egress(_fixture_module(name))
```

- [ ] **Step 9.3: Run and state the failure.**
      `PYTHONPATH=src python3 -m pytest tests/p7 -q` → **expected: 3 failed** — `declared == []`;
      `UnreleasedContentParameter: ModelClient.__init__(invoke) accepts <class 'bytes'>`; plus
      `test_the_gate_is_installed_on_the_only_egress_path` (`:393`) now failing its
      `assert declared == []`, which is the pre-P8 assertion this task replaces.

- [ ] **Step 9.4: Declare the transport.** In `src/llm_harness/transport.py`, at module level:

```python
#: P7 Task 22's scan reads this as syntax. `privacy/transport_guard.py:52` names this
#: module as "the one writer of `True`", and the scan was empty for as long as this
#: line was missing -- which made P7's single-egress property an assertion over an
#: empty set, and left `assert_single_egress` never once run over a real transport.
IS_MODEL_TRANSPORT: bool = True
```

- [ ] **Step 9.5 (option c): Add `ModelVisibleBytes`** as above; change `ModelClient.invoke` to
      `Callable[[ModelVisibleBytes], bytes]` and wrap at the one call site inside `issue`.

- [ ] **Step 9.6 (option b/c): Narrow rule 3.** In `assert_single_egress`, replace the
      `_functions(module, public_only=False)` content walk with a walk over the entry point's
      parameters and their transitively-referenced dataclass constructors. Update
      `transport_guard.py`'s module docstring rule 3 and lines 27–29 to state the new scope and to
      record that the repository now contains a transport.

- [ ] **Step 9.7: Rewrite `test_the_gate_is_installed_on_the_only_egress_path`.** Its body becomes
      the assertion that exactly one transport is declared and that the guard passes over it — the
      test's own comment already says that is what it becomes "the day P8 lands".

- [ ] **Step 9.8: Run P7 and P8, full suite, commit.**
      `git commit -m "fix(p7): the egress guard runs over the real transport"`

**The guard: `test_the_real_transport_satisfies_the_guard` plus the parametrised fixture test.**
**Sabotage recipe:** add `def _debug(text: str) -> None: ...` to `llm_harness/transport.py`. Under
option (a) the guard must reject it; under (b) or (c) it will not, **and that is the cost of the
narrowing** — so instead sabotage by adding a second public function `def send(payload: bytes)`,
which every option must reject (`MultipleEgressPoints` and `UnreleasedContentParameter`). Then
delete one non-conforming fixture's expected failure — the parametrised test must fail. A narrowing
that leaves any of the seventeen fixtures passing has removed the guard.

---

## Task 10: Land the live-path test

**Files:**

- `git mv docs/superpowers/plans/artifacts/p1_p9_live_path.py tests/integration/test_p1_p9_live_path.py`

**Done-means:**

- **D10.1** — `PYTHONPATH=src python3 -m pytest tests/integration/test_p1_p9_live_path.py -q`
  reports all tests passing.
- **D10.2** — `PYTHONPATH=src python3 -m pytest -q` reports the full expected count with zero
  failures.
- **D10.3** — for each of Tasks 2–9, reverting that commit alone makes exactly the assertions named
  in its Done-means fail, and no others.

**Steps:**

- [ ] **Step 10.1:** Run the held file in place and confirm green.
- [ ] **Step 10.2:** `git mv` it into `tests/integration/`.
- [ ] **Step 10.3:** Full suite.
- [ ] **Step 10.4:** Run the D10.3 revert loop, one task at a time, with
      `git revert --no-commit <sha> && PYTHONPATH=src python3 -m pytest tests/integration/test_p1_p9_live_path.py -q && git revert --abort`.
      Record which assertion fired for each. **A task whose revert leaves the file green has no
      guard and must go back to its own step before this branch merges.**
- [ ] **Step 10.5:** `git commit -m "test(seams): one live path with no doubles"`

---

## Open items, collected

| # | Item | Recommendation |
|---|---|---|
| **O1** | **Task 4** — does the released item redact its context (a) or carry none (b)? | **(b1)**: split the type so a released record has no place to put raw text. Nothing reads context; P7's SPEC never names it; §8.4 forbids it. Option (a) additionally fails to close the un-classified case. |
| **O2** | **Task 5** — does `src/production.py` grow to compose P8+P9, or does a second root appear? | Extend `production.py`. It is already the one place that binds plumbing to injected authorities, and leaving the wiring in a test is how defect 3 survived. |
| **O3** | **Task 9** — is the egress guard wrong or the transport wrong? | **(c)**: narrow rule 3 to the egress surface *and* give `invoke` a nominal `ModelVisibleBytes`. Keeping rule 3 as-is forbids an ISO timestamp parameter; removing the `bytes` check entirely removes the only real finding. |
| **O4** | Contract lines 73–76 name `SiteDependencies` where live `run_call` takes `CallDependencies`. | Correct the contract (Task 5, Step 5.7). This is a factual staleness, not a ruling — recorded here so the owner sees the contract changed under them. |
| **O5** | `field_permitted`'s demotion tier needs the two catalogue predicates at the stage. Where do `TOOL_PRODUCER_STRINGS` and `METADATA_PROPERTY_NAMES` come from in production? | `resolver.py:118–129` documents a caller-bound adapter; `src/production.py` binds no such catalogue today. Task 6 assumes the stage receives them the same way `screen_metadata` does. If the owner wants them injected on `FactResolver` instead, Task 6 Step 6.5 changes shape. |
| **O6** | Task 8 corrects `run["observation_count"]` inside `ExtractionResult.__post_init__`, which rewrites a mapping the caller supplied. | Acceptable — the same method already rewrites `observations`, and one point of repair is D10's own argument. If the owner prefers, the alternative is nine edits at the extractors and a conformance test; say so and Step 8.4 drops its last three lines. |

---

## What this plan does not repair

- **The detector still does not exist.** On a real corpus every file resolves to
  `Denied(unclassified)` (`_PLAN-AUTHORING-BRIEF.md` §7). Task 1 supplies a `classify` producer
  because the contract requires one; that is not the same as shipping a rule set.
- **No prompt is authored.** `PromptDefinition` is injected everywhere and this plan authors none.
- **`NEEDS-JOSEPH C22` (region origin) stays open.** Redaction still refuses a bounding box by name.
- **P13's consent hand-off is untouched.** `NeedsConsent` is returned unchanged, as the contract
  requires, and nobody catches it yet.
- **`llm_harness/fixtures.py` keeps its `conflicts=()`.** It is P8's own recorded Site-B fixture and
  P8 owns it (contract seam ledger, P9→P8 row). `src/grouping/fixtures.py:177` is **no longer** on
  this list — Task 5 covers it, verifies it is conflict-free by design rather than by omission, and
  puts it on a named allowlist so a seventh bare `conflicts=()` cannot appear silently.
