---
last_mapped_commit: a5219c2d247f9cb754ea3eb38a6cf025a52fb26c
---
# Coding Conventions

**Analysis Date:** 2026-08-29

## Naming Patterns

**Files:**
- Source modules: `snake_case.py` under a part package (`src/facts/supersede.py`, `src/privacy/gate.py`, `src/extractors/runs.py`).
- One concern per module. Prefer a SPEC section or task name in the module docstring over a vague utility name.
- Test files: `test_<part>_<topic>.py` inside the matching package dir (`tests/p6/test_p6_supersede.py`, `tests/p8/test_p8_dossier.py`). Cross-part suites use descriptive names (`tests/integration/test_p8_p6_fact_seam.py`, `tests/wave2/test_wave2_orchestrator.py`).
- Fixture helpers co-located with the suite: `p4_stub.py`, `p6_fixtures.py`, `p8_fixtures.py`, `p9_fixtures.py`, `p10_fixtures.py`, `p13_fixtures.py`, `transport_fixtures.py`, `pdf_bytes.py`.

**Functions:**
- Public API: `snake_case` verbs that name the contract (`ensure_value`, `supersede_fact`, `facts_for`, `open_database`, `apply_rules`).
- Private helpers: leading underscore (`_row`, `_tail`, `_slot`, `_checked_field_key`, `_deny_events_history_loss`).
- Prefer keyword-only arguments after `*` for multi-field domain operations so call sites cannot swap ids:

```python
def supersede_fact(conn: sqlite3.Connection, *, old_fact_id: str, ...): ...
def facts_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str, ...): ...
def record_pass(conn: sqlite3.Connection, *, file_id: str, content_hash: str, ...): ...
```

**Variables:**
- Local names are short and domain-shaped (`conn`, `file_id`, `content_hash`, `field_key`, `value_id`, `observation`).
- Fixture clocks and fixed timestamps are module constants (`FIXED_CLOCK`, `FIXED_OBSERVED_AT`, `CLOCK`).

**Types / classes:**
- Records: PascalCase frozen dataclasses (`Rule`, `ValueRow`, `Candidate`, `ResolveResult`, `Dossier`).
- Domain errors: PascalCase phrases that state the refusal (`PreferredNeverReverses`, `MalformedRule`, `DatabaseInsideCorpus`, `ConfigurationRequired`, `OutOfVocabulary`). Prefer a dedicated subclass of `ValueError`, `KeyError`, `LookupError`, `RuntimeError`, or `Exception` over a bare generic raise.
- Closed vocabularies and authored string tables: `SCREAMING_SNAKE` module constants (`ACADEMIC_CONTEXT_TERMS`, `FACT_TABLE`, `STATES`, `VALUE_ORIGINS`, `TEXT_BEARING`). Import the constant; do not index into a tuple by magic position at call sites.

**Packages (parts):**
- Implementation lives under `src/<package>/` mapped to product parts: `database_agent` (P1), `eval_harness` (P2), `scan_agent` (P3), `evidence_shape` (P4), `extractors` (P5), `facts` (P6), `privacy` (P7), `llm_harness` (P8), `grouping` (P9), `tree_design` (P10), `placement` (P11), plus `readers`, `recognition`, and top-level `cli.py` / `orchestrator.py` / `production.py`.

## Code Style

**Formatting:**
- Not detected as an automated formatter (no Ruff, Black, isort, or Prettier config in the repo).
- Follow surrounding module style: ~88–100 character soft wrap, hanging indent on continued calls, blank line between top-level defs.
- Use `from __future__ import annotations` in essentially every module (~216 of ~229 `src/**/*.py` files).

**Linting / typing:**
- Not detected as a project-enforced linter or mypy/pyright config.
- Type annotations are mandatory on public surfaces: parameters, returns, dataclass fields, and exception classes.
- Prefer `collections.abc` (`Callable`, `Iterable`, `Mapping`, `Sequence`) over `typing` equivalents when both work.
- Prefer `|` unions (`str | None`) over `Optional[str]`.
- Use `@dataclass(frozen=True)` / `frozen=True, slots=True` for immutable records.

**Python version:**
- `requires-python = "==3.12.*"` in `pyproject.toml`. Write 3.12-only code; do not add compatibility shims for older Pythons.

## Import Organization

**Order (observed and preferred):**
1. `from __future__ import annotations`
2. Stdlib (`sqlite3`, `json`, `pathlib`, `re`, `dataclasses`, …)
3. Blank line, then other packages in this repo — typically P1 / shared first (`database_agent…`), then upstream part packages (`evidence_shape…`, `extractors…`), then the current package (`facts…`, `privacy…`)
4. Relative imports are rare; prefer absolute package imports (`from facts.states import VALIDATED`)

**Path / install:**
- Packages are under `src/` via setuptools (`[tool.setuptools.packages.find] where = ["src"]`).
- Pytest sets `pythonpath = ["src"]` so tests import packages without an editable install being strictly required for collection.
- No path aliases (no `src.` prefix in imports). Import `facts.rules`, not `src.facts.rules`.

**Package `__init__.py`:**
- Package markers document the part and often re-export nothing until the surface is stable (`src/facts/__init__.py`, `src/privacy/__init__.py`). Do not import unfinished modules from `__init__.py` — that makes earlier tasks uncollectable under pytest.
- When a module publishes a closed API surface, prefer an explicit `__all__` (see `src/facts/values.py`).

## Error Handling

**Patterns:**
- Raise a named domain exception that encodes the SPEC refusal. Document the SPEC citation in the class docstring.
- Prefer refuse-over-repair: if storage cannot represent an operation, raise (`SupersedeMerge`) rather than silently overwrite.
- Use `KeyError` / `LookupError` for unknown ids (`unknown fact {fact_id!r}`); use `ValueError` subclasses for malformed caller input; use `RuntimeError` subclasses when a required upstream authority is missing (`ConfigurationRequired`, `FrozenTreeRequired`).
- `ContractViolation` (`src/extractors/failure.py`) is the cross-part signal that the orchestrator must not treat as a per-file failure — subclass it when the contract itself is broken (`FactPassNotRun` in `src/facts/usable.py`).
- Catch narrowly. Extractors convert reader exceptions into `completeness="failed"` runs via `failed_result` rather than inventing corruption thresholds (`src/extractors/failure.py`, guarded in `tests/p5/test_p5_join.py`).
- Message strings cite the SPEC section or decision id when that citation is load-bearing for a test or review.

**Do not:**
- Invent numeric thresholds, gazetteers, or producer-string catalogues as module-level defaults. Inject them; absent means refuse (`ConfigurationRequired` / no-invention guards).
- Swallow exceptions to keep a scan green. Failed runs are first-class vocabulary.

## Logging

**Framework:** Not detected as a structured logging stack.

**Patterns:**
- Library/domain packages do not use `logging` as a control path; behaviour is expressed via raised exceptions, returned records, and SQLite rows.
- User-facing output lives in `src/cli.py` via `print(..., file=out)`.
- Auditability is storage: append-only `events`, privacy audit records, supersession columns — not log lines.

## Comments

**When to Comment:**
- Module docstrings are long and load-bearing: quote the SPEC, name the decisions (D/M/F/OQ ids), and state what this module deliberately does **not** own.
- Use `#:` attribute doc comments for module-level constants that tests or neighbouring parts must treat as vocabulary.
- Inline comments explain a non-obvious refusal, a SQLite quirk verified by execution, or why an import is a module rather than a name (see `src/privacy/gate.py`).

**JSDoc/TSDoc:** Not applicable (Python). Prefer module + class + function docstrings over stub one-liners.

**Guard-token trap:**
- When asserting absence of a concept, scope the check to AST names/literals (`ast.Name`, `ast.Attribute`, `ast.Constant`), not whole source text — otherwise the docstring explaining the absence fails the guard. See `tests/p5/test_p5_join.py` and `tests/p6/test_p6_no_invention.py`.

## Function Design

**Size:** Prefer one SPEC behaviour per public function. Split helpers with `_` prefixes rather than large multi-purpose APIs.

**Parameters:**
- First argument for DB work is almost always `conn: sqlite3.Connection`.
- Remaining domain fields are keyword-only.
- Injected authorities (screens, classifiers, ceilings, clocks, normalizers) take **no default** when the SPEC leaves them open — a missing authority must raise, not guess (`MetadataScreen` on `apply_rules`, gate constructor parameters in `src/privacy/gate.py`).

**Return Values:**
- Prefer explicit records / tuples over ad-hoc dict bags at package boundaries (frozen dataclasses for LLM/privacy/evidence shapes).
- Dict rows appear at SQLite boundaries (`sqlite3.Row`) and older extractor batch shapes; convert at the seam rather than inventing a second schema.

## Module Design

**Exports:**
- Public names are importable from the owning module. Package `__init__` stays thin.
- One home for each spelling: a vocabulary constant lives in one module; other modules import it. Tests (`test_*_no_invention.py`, vocabulary adoption tests) enforce this.

**Barrel Files:**
- Avoid. Do not create `catalogues.py`-style grab bags of invented constants; no-invention suites treat new collection modules as failures unless declared.

**Schema creators:**
- Each part owns an idempotent `create_*_schema(conn)` (or catalogue loader like `create_fields`). Callers compose schemas explicitly; do not hide another part's DDL inside an unrelated open path except where P1's `open_database` already creates the P1 core.

**Transactions / SQLite:**
- Use `database_agent.db.transaction` and the P1 connection conventions (`row_factory=sqlite3.Row`, `foreign_keys=ON`, `recursive_triggers=ON`, WAL). Do not use `INSERT OR REPLACE` on append-only history tables.

## Anti-Patterns to Avoid

**Second home for a decision:**
- Do not re-spell a field key, producer string, denial order, or table name in a second module. Import the constant; add a guard test if the spelling is load-bearing.

**Silent defaults for open questions:**
- Do not paper over Deferred / OQ items with a guessed threshold or catalogue. Refuse or inject.

**Cross-package conftest name collisions:**
- `tests/` root has no `__init__.py`. Pytest prepend import mode can make every `conftest.py` compete for `sys.modules["conftest"]`. Put `__init__.py` in part test packages that need an isolated conftest (`tests/p6/__init__.py`, `tests/p8/__init__.py`, …), and do **not** add a `tests/wave2/conftest.py` that would displace another package's fixtures.

**Mocking real adapters:**
- Deployment readers (`src/readers/`) are tested against real library behaviour (`tests/readers/`). Do not mock pdfminer/Vision to “prove” an adapter shape.

---

*Convention analysis: 2026-08-29*
