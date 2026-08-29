---
last_mapped_commit: a5219c2d247f9cb754ea3eb38a6cf025a52fb26c
---
# Testing Patterns

**Analysis Date:** 2026-08-29

## Test Framework

**Runner:**
- pytest ≥ 8 (`dev` optional dependency in `pyproject.toml`)
- Config: `[tool.pytest.ini_options]` in `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**Assertion Library:**
- pytest built-in `assert` (no unittest-style assertions as the default style)
- `pytest.raises(...)` for expected refusals; often capture `excinfo` when the message is part of the contract

**Order independence (required tooling):**
- `pytest-randomly>=3.15` is part of `dev` and is **not** optional for claiming suite correctness. A guard that only holds in one collection order is treated as accidental.
- Canonical full-suite invocation:

```bash
python3 -m pytest tests/ -p randomly --randomly-dont-reset-seed
```

- Why `--randomly-dont-reset-seed`: pytest-randomly reseeds every RNG advertised via the `pytest_randomly.random_seeder` entry point; a `thinc`/spaCy install in the same interpreter can hand `numpy.random.seed` an out-of-range value and fail every test in setup/teardown. Order randomisation is wanted; seed resetting is not. See comments in `pyproject.toml`.

**Run Commands:**
```bash
python3 -m pytest tests/                                          # full suite (default order)
python3 -m pytest tests/ -p randomly --randomly-dont-reset-seed   # order-independence check
python3 -m pytest tests/p6/ -q                                    # one part
python3 -m pytest tests/integration/test_p8_p6_fact_seam.py -q    # one seam file
SCALE_STRESS=1 python -m pytest tests/integration/test_scale_stress.py -v -s
python3 -m pytest tests/readers/                                  # needs `readers` extra where applicable
```

**Optional extras for reader tests:**
```bash
pip install -e '.[dev,readers]'   # pdfminer.six; pyobjc Vision/Quartz on macOS
```

## Test File Organization

**Location:** Separate `tests/` tree mirroring product parts (not co-located under `src/`).

**Layout (~285 `test_*.py` files):**

```text
tests/
├── conftest.py                 # P1 root: conn, sample_file
├── test_*.py                   # P1 unit/contract tests at suite root
├── p1_contract.py              # shared P1 contract helpers
├── p3/ … p11/                  # part suites (p3–p11)
├── eval/                       # P2 eval harness
├── integration/                # cross-part live seams, walking skeletons, scale
├── readers/                    # deployment adapters (real libraries)
├── recognition/                # recognition detector / rules / compile
└── wave2/                      # P3→P5→P4→P1→P2 join orchestrator
```

**Approximate file counts (test modules only):**
| Directory | Role | ~Files |
|-----------|------|--------|
| `tests/` (root) | P1 + cross-cutting | 17 |
| `tests/p3` | Scan agent | 19 |
| `tests/p4` | Evidence shape | 23 |
| `tests/p5` | Extractors | 28 |
| `tests/p6` | Facts | 30 |
| `tests/p7` | Privacy | 22 |
| `tests/p8` | LLM harness | 24 |
| `tests/p9` | Grouping | 19 |
| `tests/p10` | Tree design | 31 |
| `tests/p11` | Placement | 21 |
| `tests/eval` | Eval harness (P2) | 18 |
| `tests/integration` | Seams / live / stress | 23 |
| `tests/readers` | pdfminer / Vision adapters | 3 |
| `tests/recognition` | Recognition package | 5 |
| `tests/wave2` | Wave-2 orchestrator join | 2 |

**Naming:**
- Files: `test_<part>_<topic>.py` or `test_<topic>.py` at root
- Tests: sentence-style `def test_<behaviour>():` — prefer readable claims over `test_1` / `test_foo_bar_baz` abbreviations:

```python
def test_an_unrouted_run_is_the_native_tier_not_a_second_filesystem_extract(): ...
def test_a_rejection_without_evidence_is_refused(p6_conn): ...
def test_the_table_this_module_addresses_carries_both_columns_it_needs(p6_conn): ...
```

**`__init__.py` under tests:**
- Present in `tests/p4`, `p6`, `p7`, `p8`, `p9`, `p10`, `p11`, `eval` so that package `conftest.py` imports as `pN.conftest` rather than colliding on top-level `conftest`.
- Absent at `tests/` root and intentionally absent for `tests/wave2/` (fixtures stay in-module — see `tests/wave2/test_wave2_orchestrator.py` comments).

## Test Structure

**Suite Organization:**
```python
# tests/p6/test_p6_supersede.py
from __future__ import annotations

import pytest

from facts.supersede import PreferredNeverReverses, supersede_fact, ...

CLOCK = "2026-08-19T12:00:00+00:00"


def _record(conn, tmp_path, *, name, body):
    ...


@pytest.fixture()
def scanned(p6_conn, tmp_path):
    ...


def test_the_table_this_module_addresses_carries_both_columns_it_needs(p6_conn):
    assert FACT_TABLE == "file_facts"
    ...
```

**Patterns:**
- Setup: pytest fixtures + small private builders (`_record`, `_observe`, `_fact`, `make_dossier`)
- Teardown: connection fixtures `yield` then `c.close()`; prefer `tmp_path` over manual temp dirs
- Assertion: direct `assert` on vocabulary strings, row counts, raised types; prefer exact SPEC spellings
- Fixed clocks: every timestamp-bearing record uses an injectable / fixture clock (`FIXED_CLOCK`, `observed_at`) so §8.5 determinism / equality assertions are real

**Conftest ownership:**
| Fixture file | Owns | Notes |
|--------------|------|-------|
| `tests/conftest.py` | `conn`, `sample_file` | P1; other packages must not rewrite this file |
| `tests/eval/conftest.py` | `eval_conn` | Deliberately separate from P1 |
| `tests/p5/conftest.py` | `RecordingSink`, `sink` | In-memory P4 writer double |
| `tests/p6/conftest.py` | `p6_conn`, `observed_at` | Layers evidence + fields on P1 `conn` |
| `tests/p7/conftest.py` | P7 schema fixtures | Privacy tables |
| `tests/p8/conftest.py` | `p8_conn`, record builders | Task-3 LLM tables |
| `tests/p10/conftest.py` | layered `conn` | fields + scan + privacy + eval schemas; **not** P10's own tree schema |
| `tests/p11/conftest.py` | P11 fixtures | Placement |

**Part-local schema rule:** Create only the upstream tables the suite needs. Own-part DDL is often left to the test that asserts before/after schema creation (`tests/p10/conftest.py` documents this explicitly).

## Mocking

**Framework:** Prefer pytest `monkeypatch` over `unittest.mock`. **Zero** `unittest.mock` / `MagicMock` usages detected in `tests/`.

**Patterns:**
```python
def test_a_third_value_read_back_is_a_load_error_not_a_fallback(p7_conn, monkeypatch):
    monkeypatch.setattr(display_module, "current_policy", ...)
    with pytest.raises(UnknownDisplaySetting):
        ...
```

**What to Mock / replace:**
- Injectable authorities and module callables via `monkeypatch.setattr` when proving a refusal path
- In-memory doubles that preserve real contracts (`RecordingSink` in `tests/p5/conftest.py` mirrors P4 write semantics including `MalformedRun` on caller-supplied `run_id`)
- Synthetic `ModuleType` transports for signature guards (`tests/p7/transport_fixtures.py`) — real function objects, not string eval of production code

**What NOT to Mock:**
- SQLite / `open_database` — use real temp DB files via `tmp_path`
- Upstream part APIs in seam/integration tests — bind live signatures and drive real callees (`tests/integration/test_p8_p6_fact_seam.py`, `tests/recognition/test_recognition_seam.py`)
- Optional reader libraries — `pytest.importorskip` and run against real bytes (`tests/readers/test_pdf_pdfminer.py`)

**Stubs:**
- `tests/p5/p4_stub.py` adapts P5 dict batches to live `evidence_shape` validators; it must not reimplement P4 vocabularies or conformance. Prefer importing P4 and wrapping only the adaptation.

## Fixtures and Factories

**Test Data:**
```python
# Builder with overrides (P8)
def make_dossier(**overrides) -> Dossier:
    values = dict(dossier_id="dossier-1", call_site=A_FACT, ...)
    values.update(overrides)
    return Dossier(**values)

# Corpus helpers (P10/P11)
# tests/p10/p6_fixtures.py, p9_fixtures.py, p13_fixtures.py
# tests/p11/p10_fixtures.py, multi_life_corpus.py, seam_corpus.py
```

**Location:**
- Shared clocks / sinks: package `conftest.py`
- Cross-part corpora and record builders: `*_fixtures.py` beside the suite
- Eval JSON fixtures: `tests/eval/fixtures/` (including `adversarial/`)
- PDF bytes for readers: `tests/readers/pdf_bytes.py`

**Determinism constants:**
- Prefer a single module-level ISO-8601 timestamp string reused across builders so replay and equality tests do not depend on wall clock.

## Coverage

**Requirements:** None enforced (no pytest-cov / coverage config detected).

**View Coverage:** Not applicable as a project gate. Correctness is enforced by behavioural guards, seam tests, and order-randomised full runs rather than a percentage threshold.

## Test Types

**Unit Tests:**
- Per-part packages under `tests/p3`–`tests/p11`, `tests/eval`, root `tests/test_*.py`
- Assert schema columns, vocabulary membership, pure functions, and single-module refusals

**Guard / no-invention Tests:**
- `tests/pN/test_pN_no_invention.py` (p3–p11) plus `tests/test_no_interpretation.py`
- Introspect module namespaces and `co_consts` / AST so catalogues, thresholds, and producer strings cannot be silently authored
- Include negative controls (`test_the_guards_themselves_can_fail`) so empty walkers cannot vacuously pass

**Integration / seam Tests:**
- `tests/integration/` — live multi-part paths (`test_p8_p6_fact_seam.py`, `test_p10_p6_materialise.py`, `test_p11_pipeline_live.py`, `test_p*_p2_replay.py`, walking skeletons)
- `tests/wave2/` — join coverage the unit suite historically missed
- Rule of thumb from recognition/production seams: a seam is verified when caller arguments bind against the live callee signature **or** a test drives the real callee end-to-end — never merely when an import chain exists

**Reader / deployment Tests:**
- `tests/readers/` — real pdfminer / Vision adapters; skip if extra missing

**Recognition Tests:**
- `tests/recognition/` — boundaries, compile, detector, rules, production classification seam

**Scale / stress:**
- `tests/integration/test_scale_stress.py` — skipped unless `SCALE_STRESS=1`; asserts complexity curves and design promises, not absolute wall-clock thresholds

**E2E Tests:**
- No separate browser/UI E2E framework. Closest equivalents are integration walking skeletons, `tests/wave2/`, and production corpus runners under `tests/integration/`.

## Common Patterns

**Async Testing:**
- Not detected (suite is synchronous / SQLite-local).

**Error Testing:**
```python
with pytest.raises(PreferredNeverReverses):
    preferred_fact(...)

with pytest.raises(MalformedRun):
    sink.write(batch_with_run_id)

with pytest.raises(ShadowWroteLiveState) as caught:
    ...
assert "..." in str(caught.value)
```

**Parametrize:**
- Used where a closed vocabulary or matrix of cases must stay exhaustive (`@pytest.mark.parametrize` in P7/P8/P11 suites). Prefer parametrize over copy-paste when the assertion body is identical.

**Skip / xfail:**
- `pytest.importorskip` for optional readers
- `pytest.mark.skipif` for privilege-sensitive FS tests (`tests/p3/`), absent research surfaces (`tests/p10/test_library_*.py`), and scale stress
- `pytest.xfail` reserved for documented open gaps (version-boundary / known unfinished surfaces) — keep a passing positive counterpart nearby so the xfail cannot mask a broader breakage

**AST / source guards:**
```python
tree = ast.parse(inspect.getsource(module))
names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
# assert forbidden tokens absent from CODE, not prose
```

**Fixture import safety:**
- Do not `from conftest import X` across packages unless the exporting package has `__init__.py` isolating its conftest, or the import targets the intended package path. Prefer fixtures via pytest's normal fixture injection.

## Adding Tests (prescription)

1. Place the file under the owning part directory (`tests/p6/…`) or `tests/integration/` if it requires two live parts.
2. Reuse the part's `*_conn` fixture; layer only the schemas you need.
3. Freeze time with the package clock constant.
4. Name the test as the behaviour claim under test.
5. Prefer real DB + real upstream modules; use `monkeypatch` only for injected authorities.
6. If encoding a SPEC negative (no invention / no second home), add or extend a guard test, not only a happy-path example.
7. Run the file, then run with pytest-randomly before treating the change as green:

```bash
python3 -m pytest tests/<path> -q
python3 -m pytest tests/ -p randomly --randomly-dont-reset-seed
```

---

*Testing analysis: 2026-08-29*
