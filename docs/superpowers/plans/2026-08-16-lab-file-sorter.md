# Lab file sorter Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a standalone local lab-folder sorter that dry-runs a plan, then after confirm moves auto-eligible groups into `raw/{YYYY-MM-DD}/{instrument}/…` with journalled undo, and only asks the user for keys and leftovers.

**Architecture:** Pure-Python `labsort` engine (scan → group → resolve date/instrument/experiment → rules → plan → apply). Localhost UI is last. Undo and exclusive moves exist before any live tree is touched. No LLM in routing.

**Tech Stack:** Python 3.12+, pytest, PyYAML, platformdirs. Stdlib for filesystem. No Qt, no llama.cpp, no AI File Sorter source.

## Global Constraints

- Python `>=3.12`; dependencies only `pyyaml` and `platformdirs` (+ pytest for tests)
- Package name `labsort`; rules file `rules/nutrigene.yaml`
- State via `platformdirs`, keyed by canonical sort-root path — never hardcode `~/Library/Application Support`
- `apply(plan)` is dry-run; moves require `dry_run=False`
- Auto-move only `Disposition.FULL` and `DATE_INSTRUMENT`, and only with date evidence stronger than mtime (`Decision.__post_init__` enforces this)
- Never overwrite (`os.link` / `O_EXCL`; **`os.replace` is forbidden**)
- Group key is `(directory, stem)`; `cohort_id` is canonical source directory
- Review and unclassifiable stay in place (flags); `_review/` and `_unsorted/` are user-chosen only
- Instrument is per-group; experiment may be omitted; missing experiment does not block `raw/{date}/flow/`
- No LLM, no renames, no AGPL copy from hyperfield/ai-file-sorter
- Fixture mtimes must be backdated (quiet-file rule skips files touched in 24h)
- Do not assert the Nutrigene audit’s headline counts; freeze `tests/golden/nutrigene.json`
- Commits only when the user explicitly asks; skip commit steps otherwise
- Spec: `docs/superpowers/specs/2026-08-16-lab-file-sorter-design.md`
- Reference tests and production code for M0/M1: appendix of this file (A.1–A.4). Land those files **verbatim** unless a test proves a bug.

### File map

- Create: `pyproject.toml`, `labsort/__init__.py`, `labsort/model.py`, `labsort/apply.py`, `labsort/resolve.py`, `labsort/scanner.py`, `labsort/grouper.py`, `labsort/rules.py`, `labsort/plan.py`, `labsort/decision_log.py`, `labsort/cli.py`, `labsort/ui/` (M8), `rules/nutrigene.yaml`, `tests/test_labsort.py`, `tests/test_scanner.py`, `tests/test_rules.py`, `tests/test_plan.py`, `tests/test_decision_log.py`, `tests/fixtures/`, `tests/golden/nutrigene.json`, `tests/audit_divergences.md`

---

### Task 1: Scaffold + M0 tests (fail first)

**Files:**
- Create: `pyproject.toml`
- Create: `labsort/__init__.py`
- Create: `tests/test_labsort.py` (M0 subset only: move/undo/Decision mtime — copy from Appendix A.4, omitting instrument/experiment tests until Task 3)

**Interfaces:**
- Consumes: nothing
- Produces: installable empty `labsort` package; failing tests that import `labsort.model` and `labsort.apply`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "labsort"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pyyaml", "platformdirs"]

[project.optional-dependencies]
dev = ["pytest"]

[tool.setuptools.packages.find]
include = ["labsort*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 2: Write `labsort/__init__.py`**

```python
"""Lab file sorter engine. Phase 1: Nutrigene profile."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Write failing M0 tests**

Create `tests/test_labsort.py` with these tests **exactly** from Appendix A.4:

- `test_mtime_only_cannot_be_auto_moved`
- `test_move_never_overwrites`
- `test_same_name_different_size_is_not_a_duplicate`
- `test_dry_run_is_default_and_touches_nothing`
- `test_sidecar_moves_with_its_image`
- `test_undo_restores_files_and_pruned_directories`
- `test_group_rolls_back_when_one_member_fails`
- `test_rerun_skips_already_filed_without_error`
- `test_undo_leaves_edited_file_in_place`

Include the helpers `sparse`, `make_group`, `full`, `build_plan` from A.4. Do not add resolver tests yet.

- [ ] **Step 4: Install and run tests to verify they fail**

```bash
python3.12 -m pip install -e ".[dev]"
python3.12 -m pytest tests/test_labsort.py -v
```

Expected: FAIL with `ModuleNotFoundError: labsort.model` / `labsort.apply` (or import errors). Not collection errors from syntax.

---

### Task 2: M0 safety core (`model.py` + `apply.py`)

**Files:**
- Create: `labsort/model.py` — Appendix A.1 verbatim
- Create: `labsort/apply.py` — Appendix A.3 verbatim
- Test: `tests/test_labsort.py`

**Interfaces:**
- Consumes: failing M0 tests
- Produces:
  - `Disposition`, `AUTO_MOVE`, `DateEvidence`, `FileRef`, `Group`, `Decision`, `Plan`
  - `Decision.__post_init__` raises if auto-move lacks destination or sufficient date evidence
  - `FileRef.digest() -> str` (blake2b of size ‖ first 64KiB ‖ last 64KiB)
  - `move_exclusive(src: Path, dst: Path) -> None` raises `CollisionError` on EEXIST
  - `Applier.apply(plan: Plan, *, dry_run: bool = True) -> ApplyResult`
  - `undo(journal_path: Path) -> tuple[int, list[str]]`

- [ ] **Step 1: Write `labsort/model.py`**

Paste Appendix A.1 in full.

- [ ] **Step 2: Write `labsort/apply.py`**

Paste Appendix A.3 in full.

- [ ] **Step 3: Run M0 tests**

```bash
python3.12 -m pytest tests/test_labsort.py -v
```

Expected: the 9 M0 tests PASS. If `test_group_rolls_back_when_one_member_fails` sees `collisions` vs `failed_group`, match `apply.py`: a pre-existing different sidecar is a collision (`pending is None`) so `res.collisions == ["g1"]` and sources remain. Do not “fix” the test to use `os.replace`.

- [ ] **Step 4: Confirm dry-run default**

```bash
python3.12 -c "from labsort.apply import Applier; import inspect; assert 'dry_run' in inspect.signature(Applier.apply).parameters"
```

Expected: exit 0.

---

### Task 3: M1 Resolver

**Files:**
- Create: `labsort/resolve.py` — Appendix A.2 verbatim
- Modify: `tests/test_labsort.py` — append Appendix A.4 date + instrument + experiment tests

**Interfaces:**
- Consumes: `FileRef`, `DateEvidence`, `InstrumentEvidence`, `ExperimentEvidence` from `labsort.model`
- Produces:
  - `DateResolver.resolve(ref, *, siblings=()) -> DateEvidence | None` (mtime always returned as last rung, never sufficient)
  - `infer_year(month, day, not_after) -> tuple[date | None, bool]`
  - `InstrumentResolver.resolve(ref) -> InstrumentEvidence | None`
  - `ExperimentResolver.resolve(ref, *, siblings=()) -> ExperimentEvidence | None`

- [ ] **Step 1: Add failing resolver tests**

Append to `tests/test_labsort.py` from Appendix A.4:

- `test_mmdd_year_inferred_from_mtime_ceiling`
- `test_mmdd_rolls_back_across_new_year`
- `test_filename_iso_beats_folder_and_mtime`
- `test_new_folder_dated_from_unanimous_siblings`
- `test_disagreeing_siblings_do_not_produce_a_date`
- `test_one_folder_can_mix_instruments`
- `test_flow_files_resolve_to_flow`
- `test_experiment_from_sibling_xit`
- `test_experiment_from_folder_when_no_xit`
- `test_no_experiment_is_omitted_not_blocking`

- [ ] **Step 2: Run to verify resolver tests fail**

```bash
python3.12 -m pytest tests/test_labsort.py -k "mmdd or filename_iso or New_folder or disagreeing or mix_instruments or flow_files or experiment" -v
```

Expected: FAIL import `labsort.resolve` or missing classes.

- [ ] **Step 3: Write `labsort/resolve.py`**

Paste Appendix A.2 in full.

- [ ] **Step 4: Run full `test_labsort.py`**

```bash
python3.12 -m pytest tests/test_labsort.py -v
```

Expected: 19 tests PASS (9 M0 + 10 M1; A.4 lists 19 including mtime-only which already passed in M0).

---

### Task 4: M2 Fixture generator

**Files:**
- Create: `tests/fixtures/generate_nutrigene.py`
- Create: `tests/fixtures/nutrigene-mini/` (generated, git-keep a small committed subset if the live tree is absent)
- Test: `tests/test_fixture.py`

**Interfaces:**
- Consumes: live tree at `~/Desktop/NutrigeneAI Lab Data/1. Relevant files for the BO project` when present
- Produces: sparse files (`open(p,"wb").truncate(size)`) with **real sizes**, same relative paths and sidecar pairs, **mtimes backdated ≥ 48 hours**

- [ ] **Step 1: Write failing test**

```python
from datetime import datetime, timezone, timedelta
from pathlib import Path

def test_fixture_files_are_older_than_quiet_window(nutrigene_fixture: Path):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    samples = list(nutrigene_fixture.rglob("*"))[:20]
    assert samples, "fixture empty"
    for p in samples:
        if p.is_file():
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            assert mtime < cutoff, p
```

- [ ] **Step 2: Run — expect fail** (no fixture)

```bash
python3.12 -m pytest tests/test_fixture.py -v
```

- [ ] **Step 3: Implement generator**

Walk the live relevant subtree if it exists. For each file, mkdir, `truncate(size)`, `os.utime` to original mtime if it is already old, else set mtime to 2026-06-01. Copy names and sidecar pairing. Skip `2. Irrelevant files for the BO project`. If the live tree is missing, generate a documented mini tree that still includes: Leica+metadata pair, `QS_####.jpg`, `f2.5.fcs`, `well 3.fcs`, `Exp_20260806_1` vs `_2` same names different sizes, `ExpSummaryForAPI.xml` in two dirs, a zip beside an unpacked folder, `New Folder-copy-copy` with dated Leica names.

- [ ] **Step 4: pytest `tests/test_fixture.py` PASS**

---

### Task 5: M3 Scanner + Grouper

**Files:**
- Create: `labsort/scanner.py`
- Create: `labsort/grouper.py`
- Test: `tests/test_scanner.py`

**Interfaces:**
- Consumes: `FileRef`, `Group`
- Produces:
  - `scan(root: Path, *, now=None, quiet_file_hours=24, quiet_dir_minutes=5, ignore_names=frozenset(), managed=False) -> list[FileRef]`
  - Skips: `.DS_Store`, empty `Backup/`, symlinks, git roots, ignore names, managed dirs only if `root/.labsort-root.json` exists, quiet files, exclusive-open failures (defer)
  - `group(files: list[FileRef]) -> list[Group]` with key `(parent, stem)` (jpeg + `.jpeg.metadata` share stem handling: sidecar suffix `.metadata` glued to image stem), `cohort_id=str(parent.resolve())`

- [ ] **Step 1: Write failing tests**

```python
def test_group_key_does_not_merge_two_exp_folders(tmp_path):
    # Exp_1 and Exp_2 both have well 3.fcs — two groups
    ...

def test_jpeg_and_metadata_are_one_group(tmp_path):
    ...

def test_quiet_file_is_skipped(tmp_path):
    # mtime now → absent from scan()
    ...

def test_managed_raw_skipped_only_with_marker(tmp_path):
    ...
```

- [ ] **Step 2: pytest fail**
- [ ] **Step 3: Implement scanner + grouper**
- [ ] **Step 4: pytest pass**
- [ ] **Step 5: Hand-review group count on the fixture; record the number in `tests/audit_divergences.md`**

---

### Task 6: M4 Corrected rules + golden file

**Files:**
- Create: `rules/nutrigene.yaml` (copy from `~/Personal Projects/Data Sorter/sorter-audit/patterns.yaml`, then correct)
- Create: `labsort/rules.py`
- Create: `tests/golden/nutrigene.json` (after hand review)
- Create: `tests/audit_divergences.md`
- Test: `tests/test_rules.py`

**Interfaces:**
- Consumes: `Group`, Resolver outputs, YAML
- Produces: `classify(group, date, instrument, experiment) -> Decision`
- Corrections required in YAML: `(?i)` / `re.I` on `coating_dose`, `coating_named_control`, `freeform_shorthand`; do not treat false ordering comments as logic; `experiment` comes from Resolver not capture groups

- [ ] **Step 1: Copy YAML, add failing tests for `Fib 10%`, `Fib c+`, `ecT75` matching**
- [ ] **Step 2: pytest fail**
- [ ] **Step 3: Fix regexes case-insensitive; implement `labsort/rules.py`**
- [ ] **Step 4: Run classifier over fixture, dump JSON, hand-review, freeze golden**
- [ ] **Step 5: Assert golden; document every audit divergence**

```bash
python3.12 -m pytest tests/test_rules.py -v
```

Expected: PASS. Do **not** assert 91.7% or 34%.

---

### Task 7: M5 Planner + CLI dry run

**Files:**
- Create: `labsort/plan.py`
- Create: `labsort/cli.py`
- Test: `tests/test_plan.py`

**Interfaces:**
- Consumes: groups + decisions
- Produces: `Plan(run_id, root, groups, decisions)` written as `sort-plan.json`; `summary(plan) -> str` like “I would file N groups… Nothing has moved yet.”
- CLI: `python -m labsort --root PATH` (dry run default); `--apply` sets `dry_run=False`

- [ ] **Step 1: Failing test that dry-run CLI creates no `raw/` and writes a plan file in platformdirs or `--state-dir`**
- [ ] **Step 2: pytest fail**
- [ ] **Step 3: Implement planner + CLI**
- [ ] **Step 4: Full dry run over fixture; review plan line by line**

---

### Task 8: M6 Live dry run (manual gate)

**Files:** none required if CLI works. Log: `docs/superpowers/plans/m6-live-dry-run-notes.md`

- [ ] **Step 1: `python -m labsort --root "$HOME/Desktop/NutrigeneAI Lab Data/1. Relevant files for the BO project"`**
- [ ] **Step 2: Confirm nothing moved (`raw/` absent unless it already existed as unmanaged)**
- [ ] **Step 3: Write surprises vs golden into `m6-live-dry-run-notes.md`**
- [ ] **Step 4: Do not apply until notes are empty of blockers**

---

### Task 9: M7 Live apply + undo

**Files:** none new

- [ ] **Step 1: Apply with `dry_run=False` only after M6 is clean**
- [ ] **Step 2: Undo last run; tree matches pre-apply snapshot (file list + paths)**
- [ ] **Step 3: Re-apply; second run is a no-op (skipped already filed)**
- [ ] **Step 4: Record journal path and counts**

---

### Task 10: M8 Localhost UI

**Files:**
- Create: `labsort/ui/` (stdlib `http.server` or a tiny stdlib-only app; **do not add Flask/FastAPI** unless already in Global Constraints — stay stdlib + existing deps)
- Test: `tests/test_ui.py` (optional: call handlers without a browser)

**Interfaces:**
- Actions: pick folder, run dry, confirm apply, counts, key prompt (CSV template with well numbers found), leftover worklist grouped by `cohort_id`, undo last run
- Reject any destination not under the schema (agent guard)

- [ ] **Step 1: Failing test: posting destination `Images/Science` does not move files**
- [ ] **Step 2: Implement UI + guard**
- [ ] **Step 3: pytest pass**
- [ ] **Step 4: Manual: a first-time user can complete a dry run on the fixture**

---

### Task 11: M9 Decision log

**Files:**
- Create: `labsort/decision_log.py`
- Test: `tests/test_decision_log.py`

**Interfaces:**
- `append(state_dir, event: dict) -> None` JSONL
- Fields: timestamp, run_id, group_id, cohort_id, source signature, disposition, reason, destination, actor, action
- Fingerprints **only** for groups that move
- Phase 1 never reads the log to change routing

- [ ] **Step 1: Failing tests for `planned`, `auto_move`, `resolved`, `undo` lines after a tiny apply/undo**
- [ ] **Step 2: pytest fail**
- [ ] **Step 3: Implement append-only log; wire Applier + UI**
- [ ] **Step 4: pytest pass**

---

### Task 12: Remaining tests called out in the spec

**Files:** modify test modules as needed

- [ ] **`test_crash_recovery_truncated_journal`**: write a journal with `group_commit` for g1 and a truncated `move` for g2; `apply` refuses; `undo` restores g1 only
- [ ] **`test_key_unlock_reclassifies_needs_key`**: drop `keys/well-map.csv`; `well 3.fcs` becomes auto-eligible
- [ ] Run `python3.12 -m pytest tests/ -v` — all green

---

## Spec coverage (self-review)

| Spec requirement | Task |
|---|---|
| Dry-run default, confirm to move | 2, 7 |
| mtime cannot auto-move | 2, 3 |
| Resolver date/instrument/experiment | 3 |
| Sidecar atomicity, no overwrite, journal+undo | 2 |
| Quiet-file, managed marker, group key | 5 |
| Corrected YAML, golden not audit counts | 6 |
| Experiment omitted not blocking | 3, 6 |
| Key CSV template, no docx parse | 10 |
| Review stays in place | 6, 10 |
| Decision log write-only | 11 |
| Live dry then apply | 8, 9 |
| UI agent guard | 10 |
| North star / profile / LLM / rename | out of scope (no task) |

No TBD steps. Types match Appendix A.1 (`Disposition`, `Decision`, `Plan`, `Applier.apply(..., dry_run=True)`).

---

# Appendix — M0/M1 reference (land verbatim)

## A.1 `labsort/model.py`

```python
"""Core value objects. Everything here is frozen; the pipeline is a series of
pure transformations until Applier, which is the only component that touches disk."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Literal, Mapping, Optional, Sequence

CHUNK = 64 * 1024


class Disposition(str, Enum):
    """What the rule engine decided to do with a group.

    This is a routing class, not a probability. Named `disposition` rather than
    `confidence` because `needs_key` and `review` are not points on a scale.
    """

    FULL = "full"
    DATE_INSTRUMENT = "date_instrument"
    NEEDS_KEY = "needs_key"
    REVIEW = "review"
    UNCLASSIFIABLE = "unclassifiable"
    SKIP = "skip"


AUTO_MOVE: frozenset[Disposition] = frozenset(
    {Disposition.FULL, Disposition.DATE_INSTRUMENT}
)

DateSource = Literal[
    "filename_iso",
    "sibling_filename",
    "folder_iso",
    "folder_mmdd",
    "mtime",
]

INSUFFICIENT_FOR_AUTO: frozenset[str] = frozenset({"mtime"})


@dataclass(frozen=True, slots=True)
class DateEvidence:
    value: date
    source: DateSource
    inferred_year: bool = False

    @property
    def sufficient_for_auto_move(self) -> bool:
        return self.source not in INSUFFICIENT_FOR_AUTO


@dataclass(frozen=True, slots=True)
class InstrumentEvidence:
    kind: str
    subpath: str
    source: str


@dataclass(frozen=True, slots=True)
class ExperimentEvidence:
    name: str
    source: Literal["sibling_xit", "folder_name"]


@dataclass(frozen=True, slots=True)
class FileRef:
    path: Path
    size: int
    mtime_ns: int

    @classmethod
    def stat(cls, path: Path) -> "FileRef":
        st = path.lstat()
        return cls(path=path, size=st.st_size, mtime_ns=st.st_mtime_ns)

    def digest(self) -> str:
        h = hashlib.blake2b(digest_size=16)
        h.update(self.size.to_bytes(8, "little"))
        with open(self.path, "rb") as fh:
            h.update(fh.read(CHUNK))
            if self.size > 2 * CHUNK:
                fh.seek(-CHUNK, os.SEEK_END)
                h.update(fh.read(CHUNK))
        return h.hexdigest()


@dataclass(frozen=True, slots=True)
class Group:
    group_id: str
    members: tuple[FileRef, ...]
    cohort_id: str
    primary: FileRef

    @property
    def total_size(self) -> int:
        return sum(m.size for m in self.members)


@dataclass(frozen=True, slots=True)
class Decision:
    group_id: str
    disposition: Disposition
    reason: str
    rule: Optional[str] = None
    destination: Optional[PurePosixPath] = None
    fields: Mapping[str, str] = field(default_factory=dict)
    date_evidence: Optional[DateEvidence] = None
    instrument: Optional[InstrumentEvidence] = None
    experiment: Optional[ExperimentEvidence] = None
    needs: Optional[str] = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.disposition in AUTO_MOVE:
            if self.destination is None:
                raise ValueError(f"{self.disposition} requires a destination")
            if self.date_evidence is None or not self.date_evidence.sufficient_for_auto_move:
                raise ValueError(
                    f"{self.group_id}: auto-move requires date evidence better than mtime"
                )


@dataclass(frozen=True, slots=True)
class Plan:
    run_id: str
    root: Path
    groups: Mapping[str, Group]
    decisions: Sequence[Decision]

    def auto(self) -> list[Decision]:
        return [d for d in self.decisions if d.disposition in AUTO_MOVE]

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for d in self.decisions:
            out[d.disposition.value] = out.get(d.disposition.value, 0) + 1
        return out
```

## A.2 `labsort/resolve.py`

Copy `docs/superpowers/plans/appendix/labsort_resolve.py` to `labsort/resolve.py` (change `from .model import` stays).

## A.3 `labsort/apply.py`

Copy `docs/superpowers/plans/appendix/labsort_apply.py` to `labsort/apply.py`.

## A.4 `tests/test_labsort.py`

Copy `docs/superpowers/plans/appendix/test_labsort.py` to `tests/test_labsort.py`.
